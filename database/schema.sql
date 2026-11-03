-- ====================================================================
-- TREKVERSE Intelligent Academic Performance Monitoring & Recommendation System
-- SQLite Relational Database Schema
-- ====================================================================

-- 1. Users Table (Authentication & Role-Based Access Control)
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK(role IN ('admin', 'faculty', 'student')),
    full_name VARCHAR(120) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
);

-- 2. Departments Table
CREATE TABLE IF NOT EXISTS departments (
    dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dept_code VARCHAR(10) UNIQUE NOT NULL,
    dept_name VARCHAR(100) NOT NULL,
    head_of_dept VARCHAR(100)
);

-- 3. Faculty Table
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    employee_code VARCHAR(20) UNIQUE NOT NULL,
    dept_id INTEGER,
    designation VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);

-- 4. Students Table
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    roll_number VARCHAR(30) UNIQUE NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    dept_id INTEGER,
    admission_year INTEGER NOT NULL,
    current_semester INTEGER NOT NULL,
    cgpa REAL DEFAULT 0.0,
    attendance_avg REAL DEFAULT 0.0,
    academic_standing VARCHAR(30) DEFAULT 'Good Standing',
    risk_level VARCHAR(20) DEFAULT 'Low Risk',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);

-- 5. Subjects Table
CREATE TABLE IF NOT EXISTS subjects (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_code VARCHAR(20) UNIQUE NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    dept_id INTEGER,
    credits INTEGER DEFAULT 3,
    semester INTEGER NOT NULL,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);

-- 6. Attendance Table
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    total_classes INTEGER NOT NULL DEFAULT 60,
    attended_classes INTEGER NOT NULL DEFAULT 48,
    attendance_pct REAL DEFAULT 80.0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

-- 7. Assignments Table
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    title VARCHAR(150) NOT NULL,
    max_score REAL DEFAULT 100.0,
    due_date DATE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

-- 8. Marks Table
CREATE TABLE IF NOT EXISTS marks (
    mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    exam_type VARCHAR(30) NOT NULL, -- 'Internal-1', 'Internal-2', 'Quiz', 'Final-Exam'
    score REAL NOT NULL,
    max_score REAL DEFAULT 20.0,
    score_pct REAL DEFAULT 75.0,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

-- 9. Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_name VARCHAR(80),
    predicted_score_pct REAL NOT NULL,
    predicted_grade_20 REAL NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    prediction_range_low REAL,
    prediction_range_high REAL,
    model_version VARCHAR(50) DEFAULT 'v1.0.0-GradientBoosting',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- 10. Recommendations Table
CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK(severity IN ('Critical', 'High', 'Medium', 'Low', 'Info')),
    title VARCHAR(150) NOT NULL,
    finding TEXT NOT NULL,
    action_detail TEXT NOT NULL,
    resource_link VARCHAR(255),
    is_acknowledged INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- 11. Study Plans Table
CREATE TABLE IF NOT EXISTS study_plans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    target_subject VARCHAR(100),
    weekly_hours REAL DEFAULT 14.0,
    plan_schedule_json TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- 12. Faculty Interventions Table
CREATE TABLE IF NOT EXISTS interventions (
    intervention_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    faculty_id INTEGER,
    faculty_code VARCHAR(30),
    intervention_type VARCHAR(50) NOT NULL, -- 'Faculty Mentoring', 'Remedial Session', 'Attendance Warning', 'Counseling'
    notes TEXT,
    follow_up_date DATE,
    outcome_status VARCHAR(30) DEFAULT 'Pending Review',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- 13. Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80),
    role VARCHAR(20),
    action VARCHAR(100) NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_student_roll ON students(roll_number);
CREATE INDEX IF NOT EXISTS idx_pred_student ON predictions(student_id);
CREATE INDEX IF NOT EXISTS idx_mark_student ON marks(student_id);
CREATE INDEX IF NOT EXISTS idx_inv_student ON interventions(student_id);

