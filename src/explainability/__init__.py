"""Explainability package using SHAP (TreeExplainer) and permutation importance."""
from src.explainability.shap_explainer import (
    ADDITIVITY_TOLERANCE,
    make_tree_explainer,
    explain_rows,
    top_contributions,
    additivity_gap,
    main
)

__all__ = [
    "ADDITIVITY_TOLERANCE",
    "make_tree_explainer",
    "explain_rows",
    "top_contributions",
    "additivity_gap",
    "main"
]
