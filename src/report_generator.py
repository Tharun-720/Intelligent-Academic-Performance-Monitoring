"""Report Generator: Automated academic intelligence report generation."""
from typing import Any, Dict, Optional
import datetime


def generate_student_academic_report(
    prediction_result: Dict[str, Any],
    student_name: str = "Tharun Reddy",
    student_id: str = "STU1024",
    department: str = "Artificial Intelligence & Data Science",
    semester: int = 6
) -> str:
    """Generate a comprehensive academic intelligence report following Trekverse AI standards."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    score = prediction_result.get("predicted_score_pct", 0.0)
    grade = prediction_result.get("predicted_grade_20", 0.0)
    pr = prediction_result.get("prediction_range", {"low": 0.0, "high": 100.0})
    tier = prediction_result.get("support_level", "Medium Support")
    ex = prediction_result.get("explanation", {})
    summary = prediction_result.get("student_summary", {})
    recs = prediction_result.get("recommendations", {})

    increasing = [f"{d['feature']} ({d['shap']:+.2f} pts)" for d in ex.get("increasing", [])]
    decreasing = [f"{d['feature']} ({d['shap']:+.2f} pts)" for d in ex.get("decreasing", [])]

    # Map tier to risk
    risk_label = "High Risk 🔴" if tier == "High Support" else ("Moderate Risk 🟡" if tier == "Medium Support" else "Low Risk 🟢")

    report = f"""================================================================================
                         TREKVERSE AI ACADEMY
                 Student Academic Intelligence Report
================================================================================
Generated: {now_str}  |  System: AI Academic Early-Warning Platform

SECTION 1: STUDENT INFORMATION
--------------------------------------------------------------------------------
• Student Name:       {student_name}
• Student ID / Roll:  {student_id}
• Department:         {department}
• Current Semester:   Semester {semester}
• Enrollment Status:  Active

SECTION 2: ACADEMIC PERFORMANCE SUMMARY
--------------------------------------------------------------------------------
• Estimated Attendance:  {summary.get('estimated_attendance_pct', 85.0)}% ({summary.get('absences', 0)} absences recorded)
• Internal Assessments:  G1 = {summary.get('G1', 11)}/20 | G2 = {summary.get('G2', 11)}/20
• Grade Trajectory:      {summary.get('trajectory', 'Stable')}
• Engagement Cluster:    {prediction_result.get('cluster_name', 'Consistent')}

SECTION 3: AI / MACHINE LEARNING PREDICTIVE ANALYSIS
--------------------------------------------------------------------------------
• Predicted Final Score:  {score:.1f}% (Equivalent: {grade:.1f}/20)
• Academic Risk Category: {risk_label}
• Approximate 95% Range:  {pr.get('low', 0):.1f}% – {pr.get('high', 100):.1f}% (from cross-validated residuals)
• Base Expected Average:  {ex.get('base_value', 50.0):.1f}%

SHAP Explainability - Key Contributing Drivers:
  [+] Factors raising predicted score:
      {', '.join(increasing) if increasing else 'None identified'}
  [-] Factors lowering predicted score:
      {', '.join(decreasing) if decreasing else 'None identified'}

SECTION 4: PERSONALIZED RECOMMENDATIONS & INTERVENTIONS
--------------------------------------------------------------------------------
Diagnosed Knowledge Gaps: {recs.get('total_gaps_identified', 0)} priority areas identified

Priority Action Items:
"""
    for idx, act in enumerate(recs.get("priority_actions", []), 1):
        report += f"  {idx}. [{act.get('severity', 'Medium')}] {act.get('title')}\n"
        report += f"     Finding: {act.get('finding')}\n"
        report += f"     Action:  {act.get('detail')}\n\n"

    report += f"""Recommended Faculty Intervention:
  • Strategy:   {'Bi-weekly mentoring, attendance target plan & remediation sessions' if tier == 'High Support' else ('Subject practice & attendance monitoring' if tier == 'Medium Support' else 'Enrichment problem sets & honors tracking')}
  • Status:     Active Review

SECTION 5: PROGRESS TRACKING & DISCLAIMER
--------------------------------------------------------------------------------
• Prediction Mode: Statistical inference via validated ensemble ML models
• Important Notice: Predictions are statistical estimates derived from historical
  academic records to assist instructors. They support, and never replace, professional
  faculty judgment and personalized academic counseling.
================================================================================
"""
    return report
