"""Faculty Dashboard — TREKVERSE Academic Monitoring System.

Features:
- Cohort risk surveillance and early-warning distribution.
- Priority student intervention queue.
- Student academic deep dive: marks, attendance, previous failures, SHAP indicators.
- Faculty Intervention Workflow (record mentoring notes, remedial actions, counseling).
- Outcome tracking and follow-up management.
"""
from datetime import datetime, timedelta
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from database.database import (
    get_all_interventions,
    get_all_students,
    get_student_academic_details,
    get_student_by_roll,
    log_audit,
    log_faculty_intervention
)

st.set_page_config(page_title="Faculty Dashboard — TREKVERSE", page_icon="👨‍🏫", layout="wide")

st.title("👨‍🏫 Faculty Intelligence & Academic Intervention Center")
st.caption("Surveil student cohort risks, inspect academic diagnostics, and coordinate targeted mentoring interventions.")

students = get_all_students()
if not students:
    st.warning("No student records available in the database.")
    st.stop()

df_students = pd.DataFrame(students)

# Cohort Summary Metrics
c_total = len(df_students)
c_cgpa = df_students["cgpa"].mean()
c_att = df_students["attendance_avg"].mean()
high_count = (df_students["risk_level"] == "High Risk").sum()
mod_count = (df_students["risk_level"] == "Moderate Risk").sum()
low_count = (df_students["risk_level"] == "Low Risk").sum()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Class Cohort Size", f"{c_total} Students")
m2.metric("Cohort Mean CGPA", f"{c_cgpa:.2f} / 10.0")
m3.metric("Cohort Attendance", f"{c_att:.1f}%")
m4.metric("Risk Distribution", f"{high_count} High · {mod_count} Mod · {low_count} Low")

st.markdown("---")

fac_tabs = st.tabs([
    "🚨 Early-Warning Priority Roster",
    "🔍 Student Academic Deep Dive",
    "📝 Record Faculty Intervention",
    "📋 Intervention History & Outcomes"
])

# ------------------------------------------------------------------ 1. PRIORITY ROSTER
with fac_tabs[0]:
    st.subheader("Priority Academic Support & Intervention Queue")
    st.caption("Students sorted by risk severity and attendance vulnerabilities requiring faculty check-in.")

    col_filter1, col_filter2 = st.columns(2)
    selected_risk_filter = col_filter1.multiselect(
        "Filter by Risk Category",
        ["High Risk", "Moderate Risk", "Low Risk"],
        default=["High Risk", "Moderate Risk"]
    )

    filtered_df = df_students[df_students["risk_level"].isin(selected_risk_filter)]

    def risk_formatter(val):
        if val == "High Risk":
            return "🔴 High Risk"
        elif val == "Moderate Risk":
            return "🟡 Moderate Risk"
        return "🟢 Low Risk"

    display_df = filtered_df[["roll_number", "full_name", "current_semester", "cgpa", "attendance_avg", "risk_level", "academic_standing"]].copy()
    display_df["risk_level"] = display_df["risk_level"].apply(risk_formatter)
    display_df.rename(columns={
        "roll_number": "Student Roll",
        "full_name": "Name",
        "current_semester": "Semester",
        "cgpa": "CGPA",
        "attendance_avg": "Attendance %",
        "risk_level": "Early-Warning Risk",
        "academic_standing": "Standing"
    }, inplace=True)

    st.dataframe(display_df, width="stretch", hide_index=True)

# ------------------------------------------------------------------ 2. STUDENT DEEP DIVE
with fac_tabs[1]:
    st.subheader("Student Academic Diagnostic & Explanations")

    roll_options = [s["roll_number"] for s in students]
    selected_roll = st.selectbox("Select Student Roll Number", roll_options, index=0)

    student_data = get_student_by_roll(selected_roll)
    if student_data:
        s_id = student_data["student_id"]
        details = get_student_academic_details(s_id)

        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
        col_d1.metric("Student Name", student_data["full_name"])
        col_d2.metric("Department", student_data.get("dept_name", "CSE"))
        col_d3.metric("CGPA", f"{student_data['cgpa']:.2f}")
        col_d4.metric("Risk Status", student_data["risk_level"])

        st.write("#### Subject-Wise Attendance & Internal Assessments")
        subjects_list = details.get("subjects", [])
        if subjects_list:
            df_sub = pd.DataFrame(subjects_list)
            st.dataframe(
                df_sub[["subject_code", "subject_name", "credits", "attended_classes", "total_classes", "attendance_pct", "score", "score_pct"]],
                width="stretch",
                hide_index=True
            )

            # Chart of internal marks per subject
            fig_sub = px.bar(
                df_sub,
                x="subject_code",
                y="score",
                color="score",
                color_continuous_scale="RdYlGn",
                range_y=[0, 20],
                title="Internal Marks (out of 20)",
                labels={"score": "Marks (out of 20)", "subject_code": "Course Code"}
            )
            fig_sub.update_layout(height=280)
            st.plotly_chart(fig_sub, width="stretch")
        else:
            st.info("No detailed subject marks recorded yet for this student.")

# ------------------------------------------------------------------ 3. RECORD INTERVENTION
with fac_tabs[2]:
    st.subheader("Record Faculty Academic Intervention & Action Plan")
    st.caption("Document 1-on-1 mentoring, remedial class assignments, and agreed improvement commitments.")

    with st.form("faculty_intervention_form"):
        i_col1, i_col2, i_col3 = st.columns(3)
        target_roll = i_col1.selectbox("Student to Support", [s["roll_number"] for s in students])
        faculty_code = i_col2.text_input("Faculty Identifier", value="FAC-CSE-01")
        int_type = i_col3.selectbox(
            "Intervention Category",
            ["Faculty Mentoring", "Remedial Problem Solving", "Attendance Warning Notice", "Academic Counseling", "Peer Tutor Assignment"]
        )

        i_notes = st.text_area(
            "Mentoring Observations & Prescribed Action Plan",
            value="Conducted 1-on-1 review of recent internal test. Student agreed to 2 hours daily focused revision on database queries and to attend bi-weekly lab clinics.",
            height=120
        )

        default_follow_up = datetime.now() + timedelta(days=14)
        follow_up_date = st.date_input("Scheduled Follow-Up Review Date", value=default_follow_up)

        submit_inv = st.form_submit_button("Record Intervention in Official Log", type="primary")

    if submit_inv:
        st_obj = get_student_by_roll(target_roll)
        if st_obj:
            inv_id = log_faculty_intervention(
                student_id=st_obj["student_id"],
                faculty_code=faculty_code,
                intervention_type=int_type,
                notes=i_notes,
                follow_up=str(follow_up_date)
            )
            log_audit(faculty_code, "faculty", "Intervention Created", f"Recorded {int_type} for {target_roll}")
            st.success(f"✅ Intervention successfully logged with ID #{inv_id} for {target_roll} ({st_obj['full_name']})!")
            st.rerun()

# ------------------------------------------------------------------ 4. INTERVENTION HISTORY
with fac_tabs[3]:
    st.subheader("Active & Past Faculty Interventions Roster")
    all_invs = get_all_interventions()
    if all_invs:
        df_invs = pd.DataFrame(all_invs)
        cols_show = ["intervention_id", "roll_number", "full_name", "risk_level", "faculty_code", "intervention_type", "follow_up_date", "outcome_status", "notes", "created_at"]
        st.dataframe(df_invs[cols_show], width="stretch", hide_index=True)
    else:
        st.info("No faculty interventions recorded yet.")
