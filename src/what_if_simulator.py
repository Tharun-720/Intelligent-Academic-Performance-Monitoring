"""AI What-If Simulator: interactive scenario analysis for student academic performance.

Allows students and faculty to simulate changes in study habits, attendance,
and interim grades to observe simulated model outcomes without making causal claims.
"""
from typing import Any, Dict, Tuple
import pandas as pd


def simulate_academic_scenario(
    predictor: Any,
    base_record: Dict[str, Any],
    simulated_mods: Dict[str, Any]
) -> Dict[str, Any]:
    """Compare baseline student prediction with a simulated scenario.

    Parameters
    ----------
    predictor : StudentPredictor
        Initialized predictor instance.
    base_record : dict
        Current student input record.
    simulated_mods : dict
        Dictionary of changed parameters (e.g. {'studytime': 4, 'absences': 2}).

    Returns
    -------
    dict
        Comparison dictionary containing baseline, simulated, delta, and summary.
    """
    sim_record = dict(base_record)
    sim_record.update(simulated_mods)

    base_pred = predictor.predict_single(base_record)
    sim_pred = predictor.predict_single(sim_record)

    score_delta = round(sim_pred["predicted_score_pct"] - base_pred["predicted_score_pct"], 1)
    grade_delta = round(sim_pred["predicted_grade_20"] - base_pred["predicted_grade_20"], 1)

    # Risk level mapping
    tier_map = {
        "High Support": "High Risk 🔴",
        "Medium Support": "Moderate Risk 🟡",
        "Low Support": "Low Risk 🟢"
    }

    base_risk = tier_map.get(base_pred["support_level"], base_pred["support_level"])
    sim_risk = tier_map.get(sim_pred["support_level"], sim_pred["support_level"])

    # Comparative DataFrame for dashboard display
    comparison_rows = [
        {
            "Parameter": "Weekly Study Time",
            "Current": f"{base_record.get('studytime', 2)} ({_fmt_study(base_record.get('studytime', 2))})",
            "Simulated": f"{sim_record.get('studytime', 2)} ({_fmt_study(sim_record.get('studytime', 2))})",
            "Change": f"{'+' if sim_record.get('studytime', 2) > base_record.get('studytime', 2) else ''}{sim_record.get('studytime', 2) - base_record.get('studytime', 2)}"
        },
        {
            "Parameter": "Absences (Count)",
            "Current": str(base_record.get("absences", 0)),
            "Simulated": str(sim_record.get("absences", 0)),
            "Change": f"{sim_record.get('absences', 0) - base_record.get('absences', 0):+d}"
        },
        {
            "Parameter": "G1 Grade (0-20)",
            "Current": f"{base_record.get('G1', 10)}/20",
            "Simulated": f"{sim_record.get('G1', 10)}/20",
            "Change": f"{sim_record.get('G1', 10) - base_record.get('G1', 10):+d}"
        },
        {
            "Parameter": "G2 Grade (0-20)",
            "Current": f"{base_record.get('G2', 10)}/20",
            "Simulated": f"{sim_record.get('G2', 10)}/20",
            "Change": f"{sim_record.get('G2', 10) - base_record.get('G2', 10):+d}"
        },
        {
            "Parameter": "Predicted Final Grade",
            "Current": f"{base_pred['predicted_grade_20']}/20 ({base_pred['predicted_score_pct']}%)",
            "Simulated": f"{sim_pred['predicted_grade_20']}/20 ({sim_pred['predicted_score_pct']}%)",
            "Change": f"{grade_delta:+.1f} pts ({score_delta:+.1f}%)"
        },
        {
            "Parameter": "Academic Risk Category",
            "Current": base_risk,
            "Simulated": sim_risk,
            "Change": "Improved 🟢" if sim_pred["predicted_score_pct"] > base_pred["predicted_score_pct"] else ("Unchanged ⚪" if sim_pred["predicted_score_pct"] == base_pred["predicted_score_pct"] else "Declined 🔴")
        }
    ]

    return {
        "base_prediction": base_pred,
        "simulated_prediction": sim_pred,
        "score_delta": score_delta,
        "grade_delta": grade_delta,
        "base_risk": base_risk,
        "simulated_risk": sim_risk,
        "comparison_table": pd.DataFrame(comparison_rows),
        "disclaimer": "Model simulations illustrate statistical associations within the trained model, not guaranteed causal outcomes."
    }


def _fmt_study(val: int) -> str:
    mapping = {1: "<2 hrs", 2: "2-5 hrs", 3: "5-10 hrs", 4: ">10 hrs"}
    return mapping.get(int(val), f"{val} hrs")
