"""Personalized study plan generator based on performance gaps and available study time."""
from typing import Any, Dict, List
import pandas as pd


def generate_personalized_study_plan(
    weak_subjects: List[str],
    daily_study_hours: float = 2.0,
    upcoming_exam: str = "Midterm Assessment"
) -> Dict[str, Any]:
    """Create a day-by-day customized weekly study plan tailored to diagnosed gaps.

    Parameters
    ----------
    weak_subjects : list of str
        List of identified weak subject areas.
    daily_study_hours : float
        Hours student can dedicate daily.
    upcoming_exam : str
        Target upcoming exam.

    Returns
    -------
    dict
        Plan containing daily activities, durations, and focus areas.
    """
    primary_focus = weak_subjects[0] if weak_subjects else "Database Management (DBMS)"
    secondary_focus = weak_subjects[1] if len(weak_subjects) > 1 else "Mathematics"

    dur1 = f"{min(daily_study_hours, 1.5):.1f} hours"
    dur2 = f"{max(0.5, daily_study_hours - 1.0):.1f} hour(s)"

    schedule = [
        {"Day": "Monday", "Primary Subject": primary_focus, "Activity": f"Core concept breakdown & foundational revision for {upcoming_exam}", "Duration": dur1},
        {"Day": "Tuesday", "Primary Subject": primary_focus, "Activity": "Guided practice exercises and problem sets", "Duration": dur2},
        {"Day": "Wednesday", "Primary Subject": secondary_focus, "Activity": "Analytical problem-solving and derivations", "Duration": dur1},
        {"Day": "Thursday", "Primary Subject": primary_focus, "Activity": "Previous year question papers & doubt clearance", "Duration": dur1},
        {"Day": "Friday", "Primary Subject": secondary_focus, "Activity": "Timed practice quiz and error logging", "Duration": "45 mins"},
        {"Day": "Saturday", "Primary Subject": "Cross-Subject Review", "Activity": "Revision of difficult concepts and flashcards", "Duration": dur2},
        {"Day": "Sunday", "Primary Subject": "Weekly Assessment", "Activity": "Self-assessment test, progress tracking, and faculty review prep", "Duration": "1.0 hour"}
    ]

    total_weekly_hours = daily_study_hours * 6.0

    return {
        "schedule_table": pd.DataFrame(schedule),
        "primary_focus": primary_focus,
        "secondary_focus": secondary_focus,
        "total_weekly_hours": total_weekly_hours,
        "recommendation_tips": [
            f"Prioritize {primary_focus} during early morning or high-energy study blocks.",
            "Use active recall and Feynman technique rather than passive re-reading.",
            "Schedule a 10-minute break for every 50 minutes of focused study (Pomodoro technique).",
            "Bring your Sunday self-assessment error log to faculty mentoring sessions."
        ]
    }
