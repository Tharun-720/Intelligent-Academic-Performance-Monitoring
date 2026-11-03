"""Visual Analytics & Academic Intelligence Dashboard — TREKVERSE.

Features:
- Cohort and subject-level performance comparison.
- Attendance vs assessment performance scatter & correlation.
- Longitudinal semester CGPA progression trends.
- Risk-band distribution & early-warning tracking.
- Prediction error distribution & model diagnostics.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.paths import DATA_PROCESSED, IMAGES_DIR, MODELS_DIR
from src.io_utils import read_json

st.set_page_config(page_title="Academic Analytics — TREKVERSE", page_icon="📊", layout="wide")

st.title("📊 Visual Academic Analytics & Cohort Intelligence")
st.caption("Deep-dive exploration of curriculum performance, attendance patterns, risk trends, and model residual behavior.")

try:
    df_clean = pd.read_csv(DATA_PROCESSED / "student_cleaned.csv")
    eval_meta = read_json(MODELS_DIR / "evaluation_summary.json")
except Exception as e:
    st.error(f"Required dataset or metadata files not found: {e}")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Curriculum & Subject Analytics",
    "🎯 Attendance vs Assessment Performance",
    "⚠️ Risk Distribution & Transitions",
    "🔬 Model Residual & Error Analysis"
])

# ------------------------------------------------------------------ 1. CURRICULUM ANALYTICS
with tab1:
    st.subheader("Subject-Level Performance Benchmarks")

    col_sub1, col_sub2 = st.columns([1, 1])
    with col_sub1:
        fig_sub_box = px.box(
            df_clean,
            x="subject",
            y="final_score_pct",
            color="subject",
            title="Final Score Distribution by Academic Domain",
            labels={"final_score_pct": "Final Score (%)", "subject": "Course Domain"},
            points="outliers"
        )
        st.plotly_chart(fig_sub_box, width="stretch")

    with col_sub2:
        # Grade Progression G1 -> G2 -> G3
        prog_df = df_clean.groupby("subject")[["G1", "G2", "G3"]].mean().reset_index()
        prog_melted = pd.melt(prog_df, id_vars=["subject"], value_vars=["G1", "G2", "G3"], var_name="Evaluation", value_name="Average Score")
        fig_prog = px.line(
            prog_melted,
            x="Evaluation",
            y="Average Score",
            color="subject",
            markers=True,
            title="Longitudinal Evaluation Trajectory (G1 → G2 → Final G3)",
            range_y=[8, 14]
        )
        st.plotly_chart(fig_prog, width="stretch")

    st.write("#### Curricular Summary Statistics")
    sub_summary = df_clean.groupby("subject").agg(
        Students=("final_score_pct", "count"),
        Average_Score=("final_score_pct", "mean"),
        Median_Score=("final_score_pct", "median"),
        Std_Deviation=("final_score_pct", "std"),
        Average_Absences=("absences", "mean")
    ).reset_index()
    sub_summary["Average_Score"] = sub_summary["Average_Score"].round(1)
    sub_summary["Median_Score"] = sub_summary["Median_Score"].round(1)
    sub_summary["Std_Deviation"] = sub_summary["Std_Deviation"].round(2)
    sub_summary["Average_Absences"] = sub_summary["Average_Absences"].round(1)
    st.dataframe(sub_summary, width="stretch", hide_index=True)

# ------------------------------------------------------------------ 2. ATTENDANCE VS MARKS
with tab2:
    st.subheader("Attendance Regularity vs Academic Achievement")
    st.caption("Investigating the relationship between classroom attendance rates and final examination scores.")

    fig_scatter = px.scatter(
        df_clean,
        x="estimated_attendance_pct",
        y="final_score_pct",
        color="support_level",
        size="studytime",
        hover_data=["failures", "absences"],
        title="Attendance Percentage vs Final Score (%)",
        labels={"estimated_attendance_pct": "Estimated Attendance Rate (%)", "final_score_pct": "Final Examination Score (%)", "support_level": "Support Tier"},
        color_discrete_map={"Low Support": "#22c55e", "Medium Support": "#eab308", "High Support": "#ef4444"}
    )
    st.plotly_chart(fig_scatter, width="stretch")

    st.info(
        "💡 **Key Institutional Observation**: Students with attendance above 80% and regular study habits "
        "consistently achieve grades within Low Support (good academic standing). High absences (>10 sessions) "
        "strongly correlate with academic vulnerability."
    )

# ------------------------------------------------------------------ 3. RISK DISTRIBUTION
with tab3:
    st.subheader("Cohort Academic Risk Bands & Behavior Segmentation")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        tier_counts = df_clean["support_level"].value_counts().reset_index()
        tier_counts.columns = ["Support Tier", "Count"]
        fig_pie = px.pie(
            tier_counts,
            names="Support Tier",
            values="Count",
            color="Support Tier",
            color_discrete_map={"Low Support": "#22c55e", "Medium Support": "#eab308", "High Support": "#ef4444"},
            hole=0.4,
            title="Support Tier Composition Across Cohort"
        )
        st.plotly_chart(fig_pie, width="stretch")

    with col_r2:
        fig_hist = px.histogram(
            df_clean,
            x="final_score_pct",
            color="support_level",
            nbins=25,
            title="Final Score Distribution Across Risk Tiers",
            color_discrete_map={"Low Support": "#22c55e", "Medium Support": "#eab308", "High Support": "#ef4444"}
        )
        st.plotly_chart(fig_hist, width="stretch")

# ------------------------------------------------------------------ 4. MODEL RESIDUALS
with tab4:
    st.subheader("Model Diagnostic & Residual Error Distribution")
    st.caption("Validating predictive integrity and error variance on held-out test records.")

    c_img1, c_img2 = st.columns(2)
    img_conf = IMAGES_DIR / "07_confusion_matrix.png"
    img_res = IMAGES_DIR / "09_residual_analysis.png"

    if img_conf.exists():
        c_img1.image(str(img_conf), caption="Test Set Support Tier Confusion Matrix", width="stretch")
    if img_res.exists():
        c_img2.image(str(img_res), caption="Residual Error Distribution of Selected Regressor", width="stretch")
