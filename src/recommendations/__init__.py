"""Recommendations subpackage for TREKVERSE Academic Monitoring System."""
from src.recommender import (
    SEVERITY_ORDER,
    diagnose,
    generate_recommendations,
)
from src.what_if_simulator import simulate_academic_scenario
from src.study_planner import generate_personalized_study_plan

__all__ = [
    "SEVERITY_ORDER",
    "diagnose",
    "generate_recommendations",
    "simulate_academic_scenario",
    "generate_personalized_study_plan",
]
