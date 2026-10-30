# Placement Management System (PWA + Python + MySQL)

Root files (index.html, config.js, manifest.json, sw.js, icons) -> GitHub Pages par.
backend/ (app.py, schema.sql, requirements.txt) -> Python server par (GitHub Pages par nahi chalta).

## Backend chalane ke steps
1. MySQL me database banao: CREATE DATABASE placement;
2. backend/schema.sql us database me run karo.
3. pip install -r backend/requirements.txt
4. Environment variables: DB_HOST, DB_USER, DB_PASS, DB_NAME, SECRET_KEY
5. python backend/app.py  (local test: http://127.0.0.1:5000)
6. config.js me API_BASE me backend ka link daalo.
