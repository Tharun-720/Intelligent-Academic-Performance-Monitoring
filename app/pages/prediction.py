"""Predictive Modeling & What-If Academic Simulator — TREKVERSE.

Features:
- Single-student inference with validated input bounds.
- Persona quick-fills (Typical, Needs Support, Strong).
- Calibrated final score prediction (0-100% and 0-20 scale) + 95% uncertainty interval.
- Early-warning risk band classification (🟢 Low Risk / 🟡 Moderate Risk / 🔴 High Risk).
- Local SHAP factor attributions (top positive and negative contributors).
- Interactive What-If Academic Scenario Simulator with delta calculations.
- Subject-wise score forecasts across curriculum.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.paths import MODELS_DIR
from src.prediction import StudentPredictor
from src.recommendations import simulate_academic_scenario
from src.subject_analyzer import analyze_subject_performance
from src.validation import ValidationError

st.set_page_config(page_title="Prediction & What-If Simulator — TREKVERSE", page_icon="🔮", layout="wide")

st.title("🔮 Predictive Performance Forecasting & What-If Simulator")
st.caption("Estimate academic outcomes using trained machine-learning pipelines, inspect SHAP drivers, and simulate study habit changes.")

# Load Cached Predictor
@st.cache_resource(show_spinner="Loading trained machine learning models...")
def get_predictor():
    return StudentPredictor()

try:
    predictor = get_predictor()
except Exception as e:
    st.error(f"Could not load ML predictor: {e}. Please ensure models are trained.")
    st.stop()

# Persona quick presets
PERSONAS = {
    "Typical Student": {"G1": 11, "G2": 12, "studytime": 2, "failures": 0, "absences": 4, "goout": 3, "freetime": 3, "higher": "yes"},
    "Needs Support": {"G1": 7, "G2": 6, "studytime": 1, "failures": 2, "absences": 14, "goout": 4, "freetime": 4, "higher": "yes"},
    "Honors Candidate": {"G1": 16, "G2": 17, "studytime": 4, "failures": 0, "absences": 1, "goout": 2, "freetime": 2, "higher": "yes"}
}

st.write("#### Quick-Fill Academic Habit Profiles:")
p_cols = st.columns(3)
for col, (p_name, p_vals) in zip(p_cols, PERSONAS.items()):
    if col.button(p_name, use_container_width=True):
        for k, v in p_vals.items():
            st.session_state[f"pred_{k}"] = v

# Form for single prediction
st.write("#### Student Input Parameters:")
with st.form("prediction_form"):
    c1, c2, c3 = st.columns(3)
    f_subject = c1.selectbox("Curriculum Domain", ["Mathematics", "Portuguese"], key="pred_subject")
    f_g1 = c1.slider("Internal Assessment G1 (0-20)", 0, 20, value=st.session_state.get("pred_G1", 11), key="in_g1")
    f_g2 = c1.slider("Mid-Term Assessment G2 (0-20)", 0, 20, value=st.session_state.get("pred_G2", 12), key="in_g2")

    f_absences = c2.slider("Recorded Absences (Sessions)", 0, 50, value=st.session_state.get("pred_absences", 4), key="in_absences")
    f_failures = c2.selectbox("Previous Course Failures / Backlogs", [0, 1, 2, 3], index=st.session_state.get("pred_failures", 0), key="in_failures")
    f_study = c2.select_slider(
        "Weekly Dedicated Study Time",
        options=[1, 2, 3, 4],
        value=st.session_state.get("pred_studytime", 2),
        format_func=lambda x: {1: "< 2 hours", 2: "2 - 5 hours", 3: "5 - 10 hours", 4: "> 10 hours"}[x],
        key="in_study"
    )

    f_goout = c3.slider("Peer Outing Frequency (1-5)", 1, 5, value=st.session_state.get("pred_goout", 3), key="in_goout")
    f_freetime = c3.slider("Free Time After Classes (1-5)", 1, 5, value=st.session_state.get("pred_freetime", 3), key="in_free")
    f_higher = c3.selectbox("Aims for Higher Degree / Honors", ["yes", "no"], index=0, key="in_higher")

    submit_pred = st.form_submit_button("Generate AI Academic Prediction", type="primary", use_container_width=True)

if submit_pred:
    record = {
        "subject": f_subject,
        "G1": f_g1,
        "G2": f_g2,
        "absences": f_absences,
        "failures": f_failures,
        "studytime": f_study,
        "goout": f_goout,
        "freetime": f_freetime,
        "higher": f_higher
    }
    try:
        res = predictor.predict_single(record)
        st.session_state["pred_result"] = res
        st.session_state["pred_input"] = record
    except ValidationError as err:
        for e in err.errors:
            st.error(e)

pred_res = st.session_state.get("pred_result")
curr_input = st.session_state.get("pred_input")

if pred_res is not None and curr_input is not None:
    st.markdown("---")
    st.subheader("🎯 Model Prediction & Risk Diagnostics")

    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    pred_score = pred_res["predicted_score_pct"]
    pred_grade = pred_res["predicted_grade_20"]
    tier = pred_res["support_level"]
    pr = pred_res["prediction_range"]

    m1.metric("Predicted Final Score", f"{pred_score:.1f}%", f"≈ {pred_grade:.1f} / 20.0")

    # Risk Band
    risk_label = "🟢 Low Risk (Satisfactory)" if tier == "Low Support" else ("🟡 Moderate Risk (Needs Support)" if tier == "Medium Support" else "🔴 High Risk (Urgent Review)")
    m2.metric("Early-Warning Risk", risk_label)
    m3.metric("95% Uncertainty Bound", f"{pr['low']:.0f}% – {pr['high']:.0f}%")
    m4.metric("Model Confidence", f"{pred_res['support_probabilities'].get(tier, 0.85)*100:.1f}%")

    pred_tabs = st.tabs([
        "🎛️ Interactive What-If Simulator",
        "🧠 SHAP Factor Attribution",
        "📚 Subject-Wise Score Projections",
        "🎯 Recommended Interventions"
    ])

    # ------------------------------------------------------------------ 1. WHAT-IF SIMULATOR
    with pred_tabs[0]:
        st.subheader("Interactive What-If Scenario Simulator")
        st.write(
            "Simulate behavioral adjustments (e.g., increasing self-study hours or cutting absences) "
            "to observe estimated performance improvements from the trained model."
        )

        w1, w2, w3 = st.columns(3)
        sim_study = w1.select_slider(
            "Simulated Study Time",
            options=[1, 2, 3, 4],
            value=min(4, curr_input.get("studytime", 2) + 1),
            format_func=lambda x: {1: "< 2 hours", 2: "2 - 5 hours", 3: "5 - 10 hours", 4: "> 10 hours"}[x]
        )
        sim_abs = w2.slider("Simulated Absences (Cut down missed sessions)", 0, 40, value=max(0, curr_input.get("absences", 4) - 2))
        sim_g2 = w3.slider("Simulated Upcoming Midterm Score (0-20)", 0, 20, value=min(20, curr_input.get("G2", 12) + 2))

        sim_mods = {"studytime": sim_study, "absences": sim_abs, "G2": sim_g2}
        sim_res = simulate_academic_scenario(predictor, curr_input, sim_mods)

        st.write("#### Baseline vs. Simulated Scenario Comparison:")
        st.dataframe(sim_res["comparison_table"], width="stretch", hide_index=True)

        delta = sim_res["score_delta"]
        if delta > 0:
            st.success(f"🚀 **Positive Outcome**: Predicted final score improves by **+{delta:.1f}%** (≈ **+{sim_res['grade_delta']:.1f}** grade points / 20) under this scenario.")
        elif delta < 0:
            st.error(f"⚠️ **Negative Outcome**: Predicted final score decreases by **{delta:.1f}%**.")
        else:
            st.info("ℹ️ Predicted score remains stable under this scenario.")

        st.caption(f"Note: {sim_res['disclaimer']}")

    # ------------------------------------------------------------------ 2. SHAP EXPLANATION
    with pred_tabs[1]:
        st.subheader("Explainable AI (SHAP) — Local Feature Attribution")
        st.write(
            "SHAP (SHapley Additive exPlanations) values show the exact points added or subtracted "
            "from the cohort average prediction for this student."
        )

        ex = pred_res.get("explanation", {})
        if ex.get("available", False):
            st.write(f"Cohort Base Value: **{ex['base_value']:.1f}%** ➔ Student Forecast: **{pred_score:.1f}%**")

            # Collect SHAP values
            shap_items = [(d["feature"], d["shap"]) for d in ex.get("increasing", [])] + [(d["feature"], d["shap"]) for d in ex.get("decreasing", [])]
            if shap_items:
                df_shap = pd.DataFrame(shap_items, columns=["Feature", "SHAP_Points"]).sort_values("SHAP_Points")
                fig_shap = go.Figure(go.Bar(
                    x=df_shap["SHAP_Points"],
                    y=df_shap["Feature"],
                    orientation="h",
                    marker_color=["#ef4444" if v < 0 else "#22c55e" for v in df_shap["SHAP_Points"]]
                ))
                fig_shap.update_layout(
                    title="SHAP Impact on Final Score Prediction (in points)",
                    xaxis_title="Points Added (+) or Deducted (-)",
                    height=300
                )
                st.plotly_chart(fig_shap, width="stretch")

            c_shp1, c_shp2 = st.columns(2)
            with c_shp1:
                st.success("**Positive Drivers (Raising Score):**")
                for u in ex.get("increasing", []):
                    st.markdown(f"- `{u['feature']}`: **+{u['shap']:.2f}** pts")
            with c_shp2:
                st.error("**Risk Drivers (Lowering Score):**")
                for d in ex.get("decreasing", []):
                    st.markdown(f"- `{d['feature']}`: **{d['shap']:.2f}** pts")
        else:
            st.info("SHAP explanations are computed for tree-based models.")

    # ------------------------------------------------------------------ 3. SUBJECT-WISE PROJECTIONS
    with pred_tabs[2]:
        st.subheader("Curriculum Subject-Level Performance Projections")
        subj_data = analyze_subject_performance(predictor, curr_input)

        c_sb1, c_sb2 = st.columns([1, 1])
        with c_sb1:
            st.dataframe(subj_data["subjects_table"], width="stretch", hide_index=True)
            st.caption(f"Estimated Overall Semester CGPA: **{subj_data['estimated_semester_cgpa']} / 10.0**")
        with c_sb2:
            fig_sub_bars = px.bar(
                subj_data["subjects_table"],
                x="Subject",
                y="Score_Val",
                color="Status",
                title="Projected Subject Scores (out of 20)",
                color_discrete_map={"Strong 🟢": "#22c55e", "Satisfactory 🟡": "#eab308", "Needs Attention 🔴": "#ef4444"},
                range_y=[0, 20]
            )
            st.plotly_chart(fig_sub_bars, width="stretch")

    # ------------------------------------------------------------------ 4. RECOMMENDATIONS
    with pred_tabs[3]:
        st.subheader("Personalized Study Recommendations & Resources")
        recs = pred_res.get("recommendations", {})
        for a in recs.get("priority_actions", []):
            sev_icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢", "Info": "⚪"}.get(a["severity"], "🔵")
            with st.expander(f"{sev_icon} {a['severity']}: {a['title']}", expanded=a["severity"] in ("Critical", "High")):
                st.write(f"**Diagnostic Finding:** {a['finding']}")
                st.write(f"**Recommended Action:** {a['detail']}")

        st.write("#### Recommended Learning Resources:")
        for r in recs.get("resources", []):
            st.markdown(f"- **{r['name']}**: {r['use']} ([Link]({r['url']}))" if r.get("url") else f"- **{r['name']}**: {r['use']}")
else:
    st.info("Configure the parameters above and click **Generate AI Academic Prediction**.")

