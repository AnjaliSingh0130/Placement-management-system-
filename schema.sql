CREATE TABLE IF NOT EXISTS students(
 id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL,
 email VARCHAR(120) NOT NULL UNIQUE, password_hash VARCHAR(255) NOT NULL,
 branch VARCHAR(20) NOT NULL DEFAULT 'BCA', cgpa DECIMAL(3,1) NOT NULL DEFAULT 0,
 backlogs INT NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS drives(
 id INT AUTO_INCREMENT PRIMARY KEY, company VARCHAR(80) NOT NULL, role VARCHAR(100) NOT NULL,
 package VARCHAR(30) NOT NULL, min_cgpa DECIMAL(3,1) NOT NULL, max_backlogs INT NOT NULL,
 branches VARCHAR(60) NOT NULL, drive_date DATE NOT NULL);
CREATE TABLE IF NOT EXISTS applications(
 id INT AUTO_INCREMENT PRIMARY KEY, student_id INT NOT NULL, drive_id INT NOT NULL,
 applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE(student_id,drive_id),
 FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
 FOREIGN KEY(drive_id) REFERENCES drives(id) ON DELETE CASCADE);
INSERT INTO drives(company,role,package,min_cgpa,max_backlogs,branches,drive_date) VALUES
('Infosys','Systems Engineer','3.6 LPA',6,0,'BCA,MCA,BTech','2026-11-12'),
('TCS','Assistant System Engineer','3.4 LPA',6,1,'BCA,MCA,BTech','2026-11-18'),
('Wipro','Project Engineer','3.8 LPA',6.5,0,'BCA,MCA','2026-11-25'),
('Zoho','Software Developer','7 LPA',8,0,'BCA,MCA,BTech','2026-12-02'),
('Capgemini','Analyst','4 LPA',6.5,0,'MCA,BTech','2026-12-09');
