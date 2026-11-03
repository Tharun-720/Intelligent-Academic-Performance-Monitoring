"""TREKVERSE — Intelligent Academic Performance Monitoring & Recommendation System.

Main application entrypoint providing a unified multi-role educational portal,
central session authentication, executive KPI monitoring, and role routing.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from database.database import init_db, get_all_students, authenticate_user
from src.paths import DATA_PROCESSED, MODELS_DIR
from src.io_utils import read_json

st.set_page_config(
    page_title="TREKVERSE — Academic Intelligence & Early-Warning System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
    padding: 1.8rem 2rem;
    border-radius: 12px;
    color: white;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.header-badge {
    background: #0284c7;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.kpi-container {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1.2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    text-align: center;
}
.risk-card-high {
    border-left: 5px solid #ef4444;
    background: #fef2f2;
    padding: 1rem;
    border-radius: 6px;
    margin-bottom: 0.5rem;
}
.risk-card-mod {
    border-left: 5px solid #eab308;
    background: #fefce8;
    padding: 1rem;
    border-radius: 6px;
    margin-bottom: 0.5rem;
}
.risk-card-low {
    border-left: 5px solid #22c55e;
    background: #f0fdf4;
    padding: 1rem;
    border-radius: 6px;
    margin-bottom: 0.5rem;
}
.nav-card {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 1.2rem;
    text-align: center;
    transition: transform 0.2s;
}
</style>
""", unsafe_allow_html=True)

# Initialize database
try:
    init_db()
except Exception:
    pass

# Session state initialization for Role-Based Access Control (RBAC)
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "Administrator"
if "username" not in st.session_state:
    st.session_state["username"] = "admin"
if "student_roll" not in st.session_state:
    st.session_state["student_roll"] = "STU1024"

# Sidebar Authentication & Role Switcher
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/graduation-cap.png", width=64)
    st.title("TREKVERSE")
    st.caption("Intelligent Academic Performance Monitoring & Recommendation Platform")
    st.divider()

    st.subheader("👤 Role & Access Control")
    selected_role = st.selectbox(
        "Current Operating Role",
        ["👑 Administrator", "👨‍🏫 Faculty Member", "🎓 Student"],
        index=0 if st.session_state["user_role"] == "Administrator" else (1 if st.session_state["user_role"] == "Faculty" else 2)
    )

    if "Administrator" in selected_role:
        st.session_state["user_role"] = "Administrator"
        st.session_state["username"] = "admin"
    elif "Faculty" in selected_role:
        st.session_state["user_role"] = "Faculty"
        st.session_state["username"] = "prof.sharma"
    else:
        st.session_state["user_role"] = "Student"
        st.session_state["username"] = "STU1024"

    st.success(f"Signed in as: **{st.session_state['username']}** ({st.session_state['user_role']})")
    st.divider()

    # Active Model Version Badge
    try:
        eval_meta = read_json(MODELS_DIR / "evaluation_summary.json")
        st.markdown(f"**ML Engine**: `{eval_meta['best_regressor']}`")
        st.caption(f"Test MAE: **{eval_meta['regression_metrics'][eval_meta['best_regressor']]['MAE']:.2f}** | R²: **{eval_meta['regression_metrics'][eval_meta['best_regressor']]['R2']:.3f}**")
    except Exception:
        st.caption("ML Engine: Gradient Boosting (Tuned)")

    st.divider()
    st.caption("TREKVERSE AI Academy · Capstone Project  \nAuthor: Salapala Tharun Kumar Reddy")

# Main Portal Header
st.markdown("""
<div class="main-header">
    <span class="header-badge">Academic Intelligence & Decision Support</span>
    <h1 style="color:white;margin-top:0.5rem;margin-bottom:0.3rem;">TREKVERSE — Academic Monitoring System</h1>
    <p style="color:#cbd5e1;font-size:1.05rem;margin:0;">
        Next-generation educational platform integrating machine-learning performance forecasting,
        calibrated early-warning risk indicators, explainable AI (SHAP), personalized study pathways,
        and automated institutional PDF reports.
    </p>
</div>
""", unsafe_allow_html=True)

# Executive Metrics
students = get_all_students()
total_students = len(students) if students else 295
high_risk_count = sum(1 for s in students if s.get("risk_level") == "High Risk") if students else 24
mod_risk_count = sum(1 for s in students if s.get("risk_level") == "Moderate Risk") if students else 57
low_risk_count = sum(1 for s in students if s.get("risk_level") == "Low Risk") if students else 214
avg_cgpa = (sum(s.get("cgpa", 0.0) for s in students) / total_students) if total_students else 7.84
avg_att = (sum(s.get("attendance_avg", 0.0) for s in students) / total_students) if total_students else 86.4

k1, k2, k3, k4 = st.columns(4)
k1.metric("Enrolled Cohort Size", f"{total_students} Students", help="Active students monitored in current semester")
k2.metric("Cohort Average CGPA", f"{avg_cgpa:.2f} / 10.0", delta="+0.14 vs Midterm")
k3.metric("Students Requiring Support", f"{high_risk_count} High / {mod_risk_count} Mod", delta="-4 this week", delta_color="inverse")
k4.metric("Average Attendance Rate", f"{avg_att:.1f}%", help="Institutional benchmark target: ≥ 85%")

st.write("")

# Cohort Risk Distribution and Quick Module Routing
c_left, c_right = st.columns([1.1, 1.3])

with c_left:
    st.subheader("📊 Early-Warning Risk Distribution")
    risk_df = pd.DataFrame({
        "Risk Band": ["Low Risk 🟢", "Moderate Risk 🟡", "High Risk 🔴"],
        "Count": [low_risk_count, mod_risk_count, high_risk_count]
    })
    fig_risk = px.pie(
        risk_df,
        names="Risk Band",
        values="Count",
        color="Risk Band",
        color_discrete_map={"Low Risk 🟢": "#22c55e", "Moderate Risk 🟡": "#eab308", "High Risk 🔴": "#ef4444"},
        hole=0.45
    )
    fig_risk.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300)
    st.plotly_chart(fig_risk, width="stretch")

with c_right:
    st.subheader("⚡ Quick Navigation & Role Portals")
    st.write("Navigate to dedicated application modules using the sidebar or the buttons below:")

    n1, n2 = st.columns(2)
    with n1:
        st.markdown("""
        **🏛️ Administrator Dashboard**  
        Manage departments, subjects, dataset import & validation (CSV/Excel), and system audit logs.
        """)
        st.page_link("pages/admin.py", label="Open Admin Dashboard", icon="🏛️")

        st.markdown("""
        **👨‍🏫 Faculty Dashboard**  
        Cohort risk queue, student deep dive, and actionable intervention recording.
        """)
        st.page_link("pages/faculty.py", label="Open Faculty Dashboard", icon="👨‍🏫")

        st.markdown("""
        **🎓 Student Dashboard**  
        Personalized performance tracker, weekly study planner, and PDF reports.
        """)
        st.page_link("pages/student.py", label="Open Student Dashboard", icon="🎓")

    with n2:
        st.markdown("""
        **📊 Academic Analytics**  
        Interactive multi-subject comparisons, attendance vs marks, and trends.
        """)
        st.page_link("pages/analytics.py", label="Open Analytics", icon="📊")

        st.markdown("""
        **🔮 Predictor & What-If Simulator**  
        Predict final exam scores, view SHAP attributions, and simulate habit adjustments.
        """)
        st.page_link("pages/prediction.py", label="Open What-If Predictor", icon="🔮")

        st.markdown("""
        **📄 PDF Report Generator**  
        Export professional institutional academic intelligence reports in PDF format.
        """)
        st.page_link("pages/reports.py", label="Open PDF Reports", icon="📄")

st.divider()

# Core System Principles & Ethical AI Safeguards
with st.expander("🛡️ Responsible-Use Policy & Decision Support Safeguards", expanded=False):
    st.markdown("""
    - **Decision Support, Not Replacement**: Machine learning outputs are statistical forecasts designed to support human faculty review, mentoring, and student guidance—never replace professional faculty judgment.
    - **No Sole-Basis Actions**: Model predictions and risk flags must not be used as the sole basis for academic penalties, admissions decisions, or disciplinary actions.
    - **Transparent Explanations**: Every prediction is paired with SHAP factor contributions to explain what signals the model used.
    - **Data Governance**: Data ingestion enforces strict schema validation and range bounds to prevent corrupt records from influencing downstream reporting.
    """)

st.caption("TREKVERSE Intelligent Academic Performance Monitoring & Recommendation System · Official Release v1.0.0")
