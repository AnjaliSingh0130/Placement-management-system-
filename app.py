import os
from functools import wraps
import mysql.connector
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

app = Flask(__name__)
CORS(app)
ser = URLSafeTimedSerializer(os.environ.get("SECRET_KEY", "change-this-secret"))

def conn():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"), user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASS", ""), database=os.environ.get("DB_NAME", "placement"))

def q(sql, args=(), one=False, commit=False):
    c = conn(); cur = c.cursor(dictionary=True)
    try:
        cur.execute(sql, args)
        if commit:
            c.commit(); return cur.lastrowid
        rows = cur.fetchall()
        return (rows[0] if rows else None) if one else rows
    finally:
        cur.close(); c.close()

def login_required(f):
    @wraps(f)
    def w(*a, **k):
        t = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            g.uid = ser.loads(t, max_age=7 * 86400)
        except (BadSignature, SignatureExpired):
            return jsonify(error="Please log in again"), 401
        return f(*a, **k)
    return w

def profile_of(uid):
    s = q("SELECT name,branch,cgpa,backlogs FROM students WHERE id=%s", (uid,), one=True)
    return {"name": s["name"], "branch": s["branch"], "cgpa": float(s["cgpa"]), "back": s["backlogs"]}

@app.post("/api/register")
def register():
    d = request.get_json(force=True)
    name, email, pw = d.get("name", "").strip(), d.get("email", "").strip().lower(), d.get("password", "")
    if not name or "@" not in email or len(pw) < 6:
        return jsonify(error="Enter name, valid email and a password of 6+ characters"), 400
    if q("SELECT id FROM students WHERE email=%s", (email,), one=True):
        return jsonify(error="This email is already registered"), 409
    uid = q("INSERT INTO students(name,email,password_hash,branch,cgpa,backlogs) VALUES(%s,%s,%s,%s,%s,%s)",
            (name, email, generate_password_hash(pw), d.get("branch", "BCA"),
             float(d.get("cgpa") or 0), int(d.get("back") or 0)), commit=True)
    return jsonify(token=ser.dumps(uid))

@app.post("/api/login")
def login():
    d = request.get_json(force=True)
    s = q("SELECT id,password_hash FROM students WHERE email=%s", (d.get("email", "").strip().lower(),), one=True)
    if not s or not check_password_hash(s["password_hash"], d.get("password", "")):
        return jsonify(error="Wrong email or password"), 401
    return jsonify(token=ser.dumps(s["id"]))

@app.get("/api/profile")
@login_required
def get_profile():
    return jsonify(profile_of(g.uid))

@app.put("/api/profile")
@login_required
def put_profile():
    d = request.get_json(force=True)
    q("UPDATE students SET name=%s,branch=%s,cgpa=%s,backlogs=%s WHERE id=%s",
      (d["name"], d["branch"], float(d["cgpa"]), int(d["back"]), g.uid), commit=True)
    return jsonify(profile_of(g.uid))

@app.get("/api/drives")
@login_required
def drives():
    return jsonify([{"id": r["id"], "co": r["company"], "role": r["role"], "pkg": r["package"],
                     "cgpa": float(r["min_cgpa"]), "back": r["max_backlogs"], "br": r["branches"].split(","),
                     "date": r["drive_date"].strftime("%d %b %Y")}
                    for r in q("SELECT * FROM drives ORDER BY drive_date")])

@app.get("/api/applied")
@login_required
def applied():
    return jsonify([r["drive_id"] for r in q("SELECT drive_id FROM applications WHERE student_id=%s", (g.uid,))])

@app.post("/api/apply")
@login_required
def apply():
    did = request.get_json(force=True).get("drive_id")
    d = q("SELECT * FROM drives WHERE id=%s", (did,), one=True)
    if not d:
        return jsonify(error="Drive not found"), 404
    p = profile_of(g.uid)
    if p["branch"] not in d["branches"].split(",") or p["cgpa"] < float(d["min_cgpa"]) or p["back"] > d["max_backlogs"]:
        return jsonify(error="You are not eligible for this drive"), 403
    q("INSERT IGNORE INTO applications(student_id,drive_id) VALUES(%s,%s)", (g.uid, did), commit=True)
    return jsonify(ok=True)

@app.delete("/api/apply/<int:did>")
@login_required
def withdraw(did):
    q("DELETE FROM applications WHERE student_id=%s AND drive_id=%s", (g.uid, did), commit=True)
    return jsonify(ok=True)

if __name__ == "__main__":
    app.run(debug=True)
