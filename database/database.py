"""Database manager and ORM layer for TREKVERSE Intelligent Academic Performance Monitoring.

Provides SQLite persistence, schema initialization, secure password hashing,
seed data generation, role-based records, audit trails, and reporting persistence.
"""
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

DB_FILE = Path(__file__).resolve().parent / "academic_intelligence.db"
SCHEMA_FILE = Path(__file__).resolve().parent / "schema.sql"
SCHEMA_PATH = SCHEMA_FILE


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt."""
    salt = "trekverse_salt_2026"
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def get_connection(db_path: Optional[Union[str, Path]] = None) -> sqlite3.Connection:
    """Return a configured SQLite database connection with row factory."""
    path = db_path or DB_FILE
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[Union[str, Path]] = None, schema_path: Optional[Union[str, Path]] = None, force_reseed: bool = False):
    """Initialize database tables and populate seed data if empty."""
    target_path = Path(db_path) if db_path else DB_FILE
    target_schema = Path(schema_path) if schema_path else SCHEMA_FILE
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with get_connection(target_path) as conn:
        with open(target_schema, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

        # Check if users exist
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]

        # Only seed automatically if it's the default DB_FILE and empty, or force_reseed is True
        if (db_path is None and user_count == 0) or force_reseed:
            _populate_seed_data(conn)


init_database = init_db


def _populate_seed_data(conn: sqlite3.Connection):
    """Insert initial institutions, roles, students, faculty, and marks."""
    cur = conn.cursor()

    # 1. Users
    users_data = [
        ("admin", "admin@trekverse.edu", hash_password("admin123"), "admin", "System Administrator"),
        ("prof.sharma", "sharma@trekverse.edu", hash_password("faculty123"), "faculty", "Prof. R. K. Sharma"),
        ("prof.reddy", "reddy@trekverse.edu", hash_password("faculty123"), "faculty", "Dr. K. V. Reddy"),
        ("STU1024", "tharun@student.trekverse.edu", hash_password("student123"), "student", "Tharun Reddy"),
        ("STU1088", "priya@student.trekverse.edu", hash_password("student123"), "student", "Priya Patel"),
        ("STU1145", "rahul@student.trekverse.edu", hash_password("student123"), "student", "Rahul Verma"),
        ("STU1202", "sneha@student.trekverse.edu", hash_password("student123"), "student", "Sneha Rao"),
        ("STU1250", "vikram@student.trekverse.edu", hash_password("student123"), "student", "Vikram Singh"),
    ]
    cur.executemany(
        "INSERT INTO users (username, email, password_hash, role, full_name) VALUES (?, ?, ?, ?, ?)",
        users_data
    )

    # 2. Department
    cur.execute(
        "INSERT INTO departments (dept_code, dept_name, head_of_dept) VALUES (?, ?, ?)",
        ("CSE", "Computer Science & Engineering", "Dr. A. Raman")
    )
    dept_id = cur.lastrowid

    # 3. Faculty
    cur.execute("SELECT user_id FROM users WHERE username = 'prof.sharma'")
    u_sharma = cur.fetchone()[0]
    cur.execute("SELECT user_id FROM users WHERE username = 'prof.reddy'")
    u_reddy = cur.fetchone()[0]

    cur.execute(
        "INSERT INTO faculty (user_id, employee_code, dept_id, designation) VALUES (?, ?, ?, ?)",
        (u_sharma, "FAC-CSE-01", dept_id, "Professor & Academic Mentor")
    )
    cur.execute(
        "INSERT INTO faculty (user_id, employee_code, dept_id, designation) VALUES (?, ?, ?, ?)",
        (u_reddy, "FAC-CSE-02", dept_id, "Associate Professor")
    )

    # 4. Subjects
    subjects = [
        ("CS601", "Mathematics III", dept_id, 4, 6),
        ("CS602", "Database Management Systems (DBMS)", dept_id, 4, 6),
        ("CS603", "Computer Networks", dept_id, 3, 6),
        ("CS604", "Machine Learning & AI", dept_id, 4, 6),
        ("CS605", "Operating Systems", dept_id, 3, 6),
    ]
    cur.executemany(
        "INSERT INTO subjects (subject_code, subject_name, dept_id, credits, semester) VALUES (?, ?, ?, ?, ?)",
        subjects
    )

    # 5. Students
    students_info = [
        ("STU1024", "Tharun Reddy", 2023, 6, 8.45, 88.0, "Good Standing", "Low Risk"),
        ("STU1088", "Priya Patel", 2023, 6, 6.20, 64.0, "Academic Notice", "High Risk"),
        ("STU1145", "Rahul Verma", 2023, 6, 7.15, 74.0, "Good Standing", "Moderate Risk"),
        ("STU1202", "Sneha Rao", 2023, 6, 9.10, 94.0, "Dean's Honors", "Low Risk"),
        ("STU1250", "Vikram Singh", 2023, 6, 6.80, 71.0, "Needs Review", "Moderate Risk"),
    ]

    for roll, name, adm_yr, sem, cgpa, att, standing, risk in students_info:
        cur.execute("SELECT user_id FROM users WHERE username = ?", (roll,))
        uid_row = cur.fetchone()
        uid = uid_row[0] if uid_row else None
        cur.execute("""
            INSERT INTO students (user_id, roll_number, full_name, dept_id, admission_year, current_semester, cgpa, attendance_avg, academic_standing, risk_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (uid, roll, name, dept_id, adm_yr, sem, cgpa, att, standing, risk))
        sid = cur.lastrowid

        # Insert subject attendance & marks
        for s_idx in range(1, 6):
            base_score = 16.0 if risk == "Low Risk" else (12.0 if risk == "Moderate Risk" else 8.5)
            s_score = round(min(20.0, max(5.0, base_score + (s_idx * 0.5 - 1.2))), 1)
            pct = round((s_score / 20.0) * 100, 1)

            cur.execute("""
                INSERT INTO attendance (student_id, subject_id, total_classes, attended_classes, attendance_pct)
                VALUES (?, ?, 60, ?, ?)
            """, (sid, s_idx, int(60 * (att / 100)), att))

            cur.execute("""
                INSERT INTO marks (student_id, subject_id, exam_type, score, max_score, score_pct)
                VALUES (?, ?, 'Internal-1', ?, 20.0, ?)
            """, (sid, s_idx, s_score, pct))

        # Insert sample predictions
        pred_pct = 82.0 if risk == "Low Risk" else (64.0 if risk == "Moderate Risk" else 48.0)
        cur.execute("""
            INSERT INTO predictions (student_id, subject_name, predicted_score_pct, predicted_grade_20, risk_level, prediction_range_low, prediction_range_high, model_version)
            VALUES (?, 'Mathematics III', ?, ?, ?, ?, ?, 'v1.0.0-GradientBoosting')
        """, (sid, pred_pct, round(pred_pct * 0.2, 1), risk, round(pred_pct - 8.0, 1), round(pred_pct + 8.0, 1)))

    # 6. Faculty Interventions Seed
    cur.execute("""
        INSERT INTO interventions (student_id, faculty_id, faculty_code, intervention_type, notes, follow_up_date, outcome_status)
        VALUES (2, 1, 'FAC-CSE-01', 'Attendance Warning', 'Attendance dropped below 65%. Contacted student and scheduled 1-on-1 counseling.', '2026-11-15', 'Action Required')
    """)
    cur.execute("""
        INSERT INTO interventions (student_id, faculty_id, faculty_code, intervention_type, notes, follow_up_date, outcome_status)
        VALUES (3, 1, 'FAC-CSE-01', 'Remedial Session', 'Assigned additional DBMS query problem sets and peer tutor.', '2026-11-20', 'In Progress')
    """)

    # 7. Audit log seed
    cur.execute("""
        INSERT INTO audit_logs (username, role, action, details)
        VALUES ('admin', 'admin', 'System Initialized', 'Database bootstrapped with initial student and faculty cohorts.')
    """)
    conn.commit()


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Verify user credentials and return user dict if valid."""
    hashed = hash_password(password)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, username, email, role, full_name, is_active FROM users WHERE username = ? AND password_hash = ?",
            (username.strip(), hashed)
        )
        row = cur.fetchone()
        if row and row["is_active"]:
            return dict(row)
        return None


def get_all_students(db_path: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
    """Retrieve all student profiles."""
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT s.*, d.dept_name 
            FROM students s
            LEFT JOIN departments d ON s.dept_id = d.dept_id
            ORDER BY s.roll_number ASC
        """)
        return [dict(r) for r in cur.fetchall()]


def get_student_by_roll(roll: str, db_path: Optional[Union[str, Path]] = None) -> Optional[Dict[str, Any]]:
    """Retrieve specific student by roll number."""
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT s.*, d.dept_name 
            FROM students s
            LEFT JOIN departments d ON s.dept_id = d.dept_id
            WHERE s.roll_number = ?
        """, (roll.strip(),))
        row = cur.fetchone()
        return dict(row) if row else None


def get_student_academic_details(student_id: int, db_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Retrieve marks and attendance per subject for a student."""
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT sub.subject_name, sub.subject_code, sub.credits,
                   a.total_classes, a.attended_classes, a.attendance_pct,
                   m.exam_type, m.score, m.max_score, m.score_pct
            FROM subjects sub
            LEFT JOIN attendance a ON a.subject_id = sub.subject_id AND a.student_id = ?
            LEFT JOIN marks m ON m.subject_id = sub.subject_id AND m.student_id = ?
            ORDER BY sub.subject_code ASC
        """, (student_id, student_id))
        rows = [dict(r) for r in cur.fetchall()]

        # Interventions
        cur.execute("""
            SELECT * FROM interventions WHERE student_id = ? ORDER BY created_at DESC
        """, (student_id,))
        interventions = [dict(r) for r in cur.fetchall()]

        return {"subjects": rows, "interventions": interventions}


def log_faculty_intervention(
    student_ident: Union[int, str],
    faculty_code: str,
    intervention_type: str,
    notes: str,
    follow_up_or_db: Optional[Union[str, Path]] = None,
    db_path: Optional[Union[str, Path]] = None
) -> int:
    """Record a faculty intervention note into database."""
    # Handle overloaded parameters
    follow_up = "2026-11-20"
    actual_db = db_path
    if isinstance(follow_up_or_db, (Path, str)) and (str(follow_up_or_db).endswith(".sqlite") or str(follow_up_or_db).endswith(".db")):
        actual_db = follow_up_or_db
    elif isinstance(follow_up_or_db, str):
        follow_up = follow_up_or_db

    with get_connection(actual_db) as conn:
        cur = conn.cursor()
        # Resolve student_id if string roll passed
        if isinstance(student_ident, str):
            cur.execute("SELECT student_id FROM students WHERE roll_number = ?", (student_ident.strip(),))
            s_row = cur.fetchone()
            if s_row:
                sid = s_row[0]
            else:
                # Insert placeholder student if not exists
                cur.execute("""
                    INSERT INTO students (roll_number, full_name, admission_year, current_semester)
                    VALUES (?, ?, 2023, 6)
                """, (student_ident.strip(), student_ident.strip()))
                sid = cur.lastrowid
        else:
            sid = student_ident

        cur.execute("""
            INSERT INTO interventions (student_id, faculty_code, intervention_type, notes, follow_up_date, outcome_status)
            VALUES (?, ?, ?, ?, ?, 'Active Review')
        """, (sid, faculty_code, intervention_type, notes, follow_up))
        conn.commit()
        return cur.lastrowid


def log_prediction(
    student_ident: Union[int, str],
    pred_or_sub: Union[Dict[str, Any], str],
    score_pct_or_db: Optional[Union[float, Path, str]] = None,
    grade_20: Optional[float] = None,
    risk: Optional[str] = None,
    low: Optional[float] = None,
    high: Optional[float] = None,
    model_ver: str = "v1.0.0-GradientBoosting",
    db_path: Optional[Union[str, Path]] = None
) -> int:
    """Persist prediction result supporting both dict result and unpacked values."""
    actual_db = db_path

    if isinstance(pred_or_sub, dict):
        pred_dict = pred_or_sub
        if isinstance(score_pct_or_db, (Path, str)):
            actual_db = score_pct_or_db
        subject_name = pred_dict.get("subject", "General")
        pred_pct = float(pred_dict.get("predicted_score_pct", 75.0))
        g_20 = float(pred_dict.get("predicted_grade_20", round(pred_pct * 0.2, 1)))
        risk_lvl = str(pred_dict.get("support_level", "Medium Support"))
        p_range = pred_dict.get("prediction_range", {})
        r_low = float(p_range.get("low", pred_pct - 8.0))
        r_high = float(p_range.get("high", pred_pct + 8.0))
    else:
        subject_name = str(pred_or_sub)
        pred_pct = float(score_pct_or_db) if score_pct_or_db is not None else 75.0
        g_20 = float(grade_20) if grade_20 is not None else round(pred_pct * 0.2, 1)
        risk_lvl = str(risk) if risk is not None else "Moderate Risk"
        r_low = float(low) if low is not None else (pred_pct - 8.0)
        r_high = float(high) if high is not None else (pred_pct + 8.0)

    with get_connection(actual_db) as conn:
        cur = conn.cursor()
        if isinstance(student_ident, str):
            cur.execute("SELECT student_id FROM students WHERE roll_number = ?", (student_ident.strip(),))
            s_row = cur.fetchone()
            if s_row:
                sid = s_row[0]
            else:
                cur.execute("""
                    INSERT INTO students (roll_number, full_name, admission_year, current_semester)
                    VALUES (?, ?, 2023, 6)
                """, (student_ident.strip(), student_ident.strip()))
                sid = cur.lastrowid
        else:
            sid = student_ident

        cur.execute("""
            INSERT INTO predictions (student_id, subject_name, predicted_score_pct, predicted_grade_20, risk_level, prediction_range_low, prediction_range_high, model_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (sid, subject_name, pred_pct, g_20, risk_lvl, r_low, r_high, model_ver))
        conn.commit()
        return cur.lastrowid


def log_audit(username: str, role: str, action: str, details: str, db_path: Optional[Union[str, Path]] = None):
    """Record an audit trail entry."""
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO audit_logs (username, role, action, details)
            VALUES (?, ?, ?, ?)
        """, (username, role, action, details))
        conn.commit()


def get_audit_logs(limit: int = 50, db_path: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
    """Retrieve recent audit events."""
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [dict(r) for r in cur.fetchall()]


def get_all_interventions(db_path: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
    """Retrieve all faculty interventions with student roll numbers."""
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT i.*, s.roll_number, s.full_name, s.risk_level
            FROM interventions i
            JOIN students s ON i.student_id = s.student_id
            ORDER BY i.created_at DESC
        """)
        return [dict(r) for r in cur.fetchall()]
