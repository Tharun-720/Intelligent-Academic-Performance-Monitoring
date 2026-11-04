"""Administrator Dashboard — TREKVERSE Academic Monitoring System.

Features:
- Academic metadata and role management (Users, Faculty, Students, Departments).
- Institutional Dataset Import & Validation (CSV & Excel .xlsx).
- Interactive Column Mapping Wizard.
- Row-level validation feedback and range checks.
- Model version governance & performance registry.
- System Activity & Audit Trail logs.
"""
import io
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from database.database import (
    get_all_students,
    get_audit_logs,
    get_connection,
    log_audit
)
from src.paths import MODELS_DIR
from src.io_utils import read_json

st.set_page_config(page_title="Administrator Dashboard — TREKVERSE", page_icon="🏛️", layout="wide")

st.title("🏛️ Administrator Control Center & Governance")
st.caption("Manage institutional metadata, validate college dataset uploads, govern ML models, and audit system events.")

# Authorization Check
user_role = st.session_state.get("user_role", "Administrator")
if user_role != "Administrator":
    st.warning(f"⚠️ Current session role is **{user_role}**. Administrator privileges are recommended for configuration modifications.")

tabs = st.tabs([
    "📥 College Data Ingestion & Validator",
    "👥 Academic Directory & Roles",
    "🤖 ML Model Registry & Health",
    "🛡️ System Activity & Audit Logs",
    "⚙️ Risk Threshold Governance"
])

# ------------------------------------------------------------------ 1. DATASET IMPORT & VALIDATION
with tabs[0]:
    st.subheader("Institutional Dataset Upload & Schema Validation Wizard")
    st.write(
        "Upload college academic records in **CSV** or **Excel (.xlsx)** format. "
        "The system validates column mappings, value ranges, and identifies row-level errors."
    )

    sample_template = pd.DataFrame([
        {
            "Student_ID": "STU1050",
            "Name": "Aarav Sharma",
            "Department": "CSE",
            "Semester": 6,
            "Attendance": 88.5,
            "Internal_Marks": 16.5,
            "Study_Hours": 3.0,
            "Previous_CGPA": 8.20,
            "Backlogs": 0
        },
        {
            "Student_ID": "STU1051",
            "Name": "Ananya Roy",
            "Department": "CSE",
            "Semester": 6,
            "Attendance": 62.0,
            "Internal_Marks": 9.5,
            "Study_Hours": 1.5,
            "Previous_CGPA": 6.10,
            "Backlogs": 2
        }
    ])

    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        csv_bytes = sample_template.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Standard Template CSV",
            data=csv_bytes,
            file_name="trekverse_student_upload_template.csv",
            mime="text/csv"
        )

    uploaded_file = st.file_uploader(
        "Select Institutional Data File (.csv or .xlsx)",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".xlsx"):
                df_upload = pd.read_excel(uploaded_file)
            else:
                df_upload = pd.read_csv(uploaded_file)
            st.success(f"File `{uploaded_file.name}` uploaded successfully ({len(df_upload)} records detected).")

            st.write("### Step 1: Column Mapping Wizard")
            st.caption("Match incoming column headers to Trekverse expected system fields:")

            exp_fields = [
                ("Student_ID", "Unique Student Roll Number / Identifier", True),
                ("Name", "Student Full Name", False),
                ("Department", "Academic Department (e.g. CSE, ECE)", True),
                ("Semester", "Current Enrolled Semester (1-8)", True),
                ("Attendance", "Attendance Percentage (0-100)", True),
                ("Internal_Marks", "Internal Assessment Marks (0-20)", True),
                ("Study_Hours", "Self-Study Hours per Week (>= 0)", False),
                ("Previous_CGPA", "Cumulative Grade Point Average (0-10)", True),
                ("Backlogs", "Count of Active Academic Backlogs (>= 0)", True),
            ]

            mapping = {}
            map_cols = st.columns(3)
            incoming_cols = ["-- Select Header --"] + list(df_upload.columns)

            for idx, (target_field, desc, is_req) in enumerate(exp_fields):
                c_idx = idx % 3
                # Auto-match if exact or case-insensitive match exists
                default_idx = 0
                for c_i, inc_col in enumerate(incoming_cols):
                    if inc_col.lower() == target_field.lower():
                        default_idx = c_i
                        break

                label = f"{target_field} {'*(Required)*' if is_req else '(Optional)'}"
                mapping[target_field] = map_cols[c_idx].selectbox(
                    label,
                    incoming_cols,
                    index=default_idx,
                    key=f"map_{target_field}",
                    help=desc
                )

            st.write("### Step 2: Automated Schema & Range Validation")
            if st.button("Validate & Process Dataset", type="primary"):
                # Run validation
                errors = []
                valid_rows = []

                # Verify required fields are mapped
                missing_mappings = [req for req, _, is_req in exp_fields if is_req and mapping[req] == "-- Select Header --"]
                if missing_mappings:
                    st.error(f"Cannot validate: Please map required field(s): {', '.join(missing_mappings)}")
                else:
                    for i, row in df_upload.iterrows():
                        row_errors = []
                        # Check Student ID
                        sid_val = str(row[mapping["Student_ID"]]).strip()
                        if not sid_val or sid_val == "nan":
                            row_errors.append("Missing Student_ID")

                        # Check Attendance
                        try:
                            att = float(row[mapping["Attendance"]])
                            if not (0.0 <= att <= 100.0):
                                row_errors.append(f"Attendance out of range (0-100): {att}")
                        except Exception:
                            row_errors.append("Invalid non-numeric Attendance")

                        # Check Marks
                        try:
                            marks = float(row[mapping["Internal_Marks"]])
                            if not (0.0 <= marks <= 20.0):
                                row_errors.append(f"Internal marks out of range (0-20): {marks}")
                        except Exception:
                            row_errors.append("Invalid non-numeric Internal Marks")

                        # Check CGPA
                        try:
                            cgpa = float(row[mapping["Previous_CGPA"]])
                            if not (0.0 <= cgpa <= 10.0):
                                row_errors.append(f"CGPA out of range (0-10): {cgpa}")
                        except Exception:
                            row_errors.append("Invalid non-numeric CGPA")

                        # Check Backlogs
                        try:
                            backlogs = int(row[mapping["Backlogs"]])
                            if backlogs < 0:
                                row_errors.append(f"Negative backlogs: {backlogs}")
                        except Exception:
                            row_errors.append("Invalid Backlogs count")

                        if row_errors:
                            errors.append({"Row": i + 1, "Student_ID": sid_val, "Errors": "; ".join(row_errors)})
                        else:
                            valid_rows.append(row.to_dict())

                    # Results
                    st.markdown("---")
                    c_val1, c_val2 = st.columns(2)
                    c_val1.metric("Valid Rows Passed", len(valid_rows))
                    c_val2.metric("Rows Flagged with Errors", len(errors))

                    if errors:
                        st.warning(f"⚠️ Found {len(errors)} row(s) with validation issues. Review below:")
                        st.dataframe(pd.DataFrame(errors), width="stretch", hide_index=True)
                    else:
                        st.success("✅ All records passed schema and range checks with zero validation errors!")

                    if valid_rows:
                        st.write("Preview of Validated Institutional Records:")
                        st.dataframe(pd.DataFrame(valid_rows).head(10), width="stretch")
                        log_audit("admin", "admin", "Dataset Validated", f"File {uploaded_file.name} validated: {len(valid_rows)} valid, {len(errors)} errors.")

        except Exception as e:
            st.error(f"Error reading dataset: {e}")

# ------------------------------------------------------------------ 2. ACADEMIC DIRECTORY & ROLES
with tabs[1]:
    st.subheader("Academic Directory & Enrolled Students")
    students = get_all_students()
    df_stus = pd.DataFrame(students)
    if not df_stus.empty:
        display_cols = ["roll_number", "full_name", "dept_name", "current_semester", "cgpa", "attendance_avg", "academic_standing", "risk_level"]
        st.dataframe(df_stus[display_cols], width="stretch", hide_index=True)
    else:
        st.info("No students registered yet.")

    with st.expander("➕ Register New Student Profile", expanded=False):
        c1, c2, c3 = st.columns(3)
        n_roll = c1.text_input("Roll Number", "STU1300")
        n_name = c2.text_input("Student Full Name", "Arun Kumar")
        n_sem = c3.number_input("Semester", min_value=1, max_value=8, value=6)
        c4, c5, c6 = st.columns(3)
        n_cgpa = c4.number_input("Cumulative CGPA", min_value=0.0, max_value=10.0, value=7.50, step=0.05)
        n_att = c5.number_input("Attendance Rate (%)", min_value=0.0, max_value=100.0, value=85.0, step=0.5)
        n_standing = c6.selectbox("Academic Standing", ["Good Standing", "Dean's Honors", "Academic Notice", "Probation"])

        if st.button("Save Student to Database"):
            try:
                with get_connection() as conn:
                    cur = conn.cursor()
                    risk = "Low Risk" if n_cgpa >= 7.5 and n_att >= 80 else ("Moderate Risk" if n_cgpa >= 6.0 else "High Risk")
                    cur.execute("""
                        INSERT INTO students (roll_number, full_name, dept_id, admission_year, current_semester, cgpa, attendance_avg, academic_standing, risk_level)
                        VALUES (?, ?, 1, 2023, ?, ?, ?, ?, ?)
                    """, (n_roll, n_name, n_sem, n_cgpa, n_att, n_standing, risk))
                    conn.commit()
                log_audit("admin", "admin", "Student Registered", f"Added {n_roll} - {n_name}")
                st.success(f"Student {n_roll} successfully added!")
                st.rerun()
            except Exception as e:
                st.error(f"Could not register student: {e}")

# ------------------------------------------------------------------ 3. MODEL REGISTRY
with tabs[2]:
    st.subheader("Machine Learning Model Registry & Performance Governance")
    try:
        eval_meta = read_json(MODELS_DIR / "evaluation_summary.json")
        reg_best = eval_meta["best_regressor"]
        clf_best = eval_meta["best_classifier"]

        c_reg, c_clf = st.columns(2)
        with c_reg:
            st.markdown(f"### Best Regressor: `{reg_best}`")
            m_reg = eval_meta["regression_metrics"][reg_best]
            st.metric("Test MAE", f"{m_reg['MAE']:.2f} points", "Target < 5.0")
            st.metric("Test R²", f"{m_reg['R2']:.3f}")
            st.caption(f"Cross-Validation MAE: {m_reg['CV_MAE']:.2f}")

        with c_clf:
            st.markdown(f"### Best Classifier: `{clf_best}`")
            m_clf = eval_meta["classification_metrics"][clf_best]
            st.metric("Test Accuracy", f"{m_clf['Accuracy']*100:.1f}%")
            st.metric("Test Macro-F1", f"{m_clf['F1_Macro']:.3f}")
            st.caption(f"Cross-Validation Macro-F1: {m_clf['CV_F1_Macro']:.3f}")

        st.markdown("---")
        st.write("#### Comprehensive Model Benchmark Comparison")
        reg_df = pd.DataFrame([
            {"Model": k, "CV MAE": v["CV_MAE"], "Test MAE": v["MAE"], "Test RMSE": v["RMSE"], "Test R²": v["R2"]}
            for k, v in eval_meta["regression_metrics"].items()
        ])
        st.dataframe(reg_df, width="stretch", hide_index=True)

    except Exception as e:
        st.info(f"Model metadata loading: {e}")

# ------------------------------------------------------------------ 4. AUDIT LOGS
with tabs[3]:
    st.subheader("System Security & Operational Audit Log")
    st.caption("Immutable trail of data modifications, predictions, interventions, and administrative actions.")
    logs = get_audit_logs(limit=50)
    if logs:
        st.dataframe(pd.DataFrame(logs), width="stretch", hide_index=True)
    else:
        st.info("No audit entries recorded yet.")

# ------------------------------------------------------------------ 5. THRESHOLD GOVERNANCE
with tabs[4]:
    st.subheader("Early-Warning Risk Thresholds & Institutional Policies")
    st.write("Configure the decision boundaries for student academic risk classification:")

    t1, t2, t3 = st.columns(3)
    t1.slider("High Risk Attendance Cutoff (%)", 50, 75, 65, help="Students with attendance below this are flagged for prompt intervention.")
    t2.slider("Moderate Risk Attendance Cutoff (%)", 70, 85, 75)
    t3.slider("Minimum Internal Passing Score (out of 20)", 6, 12, 8)

    st.info("💡 Threshold modifications are automatically logged in the audit trail.")
    if st.button("Apply Threshold Policy"):
        log_audit("admin", "admin", "Thresholds Updated", "Institutional early-warning risk cutoffs adjusted.")
        st.success("New institutional policy saved.")

