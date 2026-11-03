"""Official PDF Report Generator for TREKVERSE Intelligent Academic Performance Monitoring System.

Generates professional, institutional-grade academic monitoring reports (PDF)
using ReportLab with metadata, performance analytics, AI risk scores,
subject-wise marks, personalized study plans, and faculty remarks.
"""
from datetime import datetime
import io
from pathlib import Path
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_student_pdf_report(
    student_info: Dict[str, Any],
    academic_data: Dict[str, Any],
    prediction_data: Dict[str, Any],
    faculty_remarks: Optional[str] = None,
    logo_path: Optional[str] = None
) -> bytes:
    """Generate a high-quality PDF report and return as bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    header_style = ParagraphStyle(
        "HeaderTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a")
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#0284c7")
    )
    meta_style = ParagraphStyle(
        "MetaText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748b")
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )
    bold_body = ParagraphStyle(
        "BoldBodyDark",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b")
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#475569")
    )

    story = []

    # 1. Header Banner
    header_table_data = [
        [
            Paragraph("TREKVERSE ACADEMY", subtitle_style),
            Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y')}", meta_style)
        ],
        [
            Paragraph("Intelligent Academic Performance Monitoring & Recommendation Report", header_style),
            Paragraph("Model: v1.0.0-GBM<br/>Status: Official Review", meta_style)
        ]
    ]
    t_header = Table(header_table_data, colWidths=[400, 140])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0284c7"), spaceAfter=12))

    # 2. Student Demographics & Academic Standing
    story.append(Paragraph("1. STUDENT PROFILE & ACADEMIC STANDING", section_heading))
    roll = student_info.get("roll_number", "STU1024")
    name = student_info.get("full_name", "Salapala Tharun Kumar Reddy")
    dept = student_info.get("dept_name", "Computer Science & Engineering")
    sem = student_info.get("current_semester", 6)
    cgpa = student_info.get("cgpa", 8.45)
    att_avg = student_info.get("attendance_avg", 88.0)
    standing = student_info.get("academic_standing", "Good Standing")
    risk = prediction_data.get("risk_level", student_info.get("risk_level", "Low Risk"))

    info_data = [
        [
            Paragraph("<b>Student Roll No:</b>", body_style), Paragraph(str(roll), bold_body),
            Paragraph("<b>Student Name:</b>", body_style), Paragraph(str(name), bold_body)
        ],
        [
            Paragraph("<b>Department:</b>", body_style), Paragraph(str(dept), body_style),
            Paragraph("<b>Current Semester:</b>", body_style), Paragraph(f"Semester {sem}", body_style)
        ],
        [
            Paragraph("<b>Cumulative CGPA:</b>", body_style), Paragraph(f"<b>{cgpa:.2f} / 10.0</b>", bold_body),
            Paragraph("<b>Attendance Rate:</b>", body_style), Paragraph(f"<b>{att_avg:.1f}%</b>", bold_body)
        ],
        [
            Paragraph("<b>Academic Status:</b>", body_style), Paragraph(str(standing), body_style),
            Paragraph("<b>AI Risk Standing:</b>", body_style), Paragraph(f"<b>{risk}</b>", bold_body)
        ]
    ]
    t_info = Table(info_data, colWidths=[110, 160, 110, 160])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 10))

    # 3. Subject-wise Assessment Breakdown
    story.append(Paragraph("2. SUBJECT-LEVEL ASSESSMENT & ATTENDANCE RECORD", section_heading))
    subjects = academic_data.get("subjects", [])
    if not subjects:
        # Default mock subjects if none passed
        subjects = [
            {"subject_name": "Mathematics III", "subject_code": "CS601", "credits": 4, "attendance_pct": 88.0, "score": 16.5, "max_score": 20.0, "score_pct": 82.5},
            {"subject_name": "Database Management (DBMS)", "subject_code": "CS602", "credits": 4, "attendance_pct": 82.0, "score": 14.0, "max_score": 20.0, "score_pct": 70.0},
            {"subject_name": "Computer Networks", "subject_code": "CS603", "credits": 3, "attendance_pct": 91.0, "score": 15.5, "max_score": 20.0, "score_pct": 77.5},
            {"subject_name": "Machine Learning & AI", "subject_code": "CS604", "credits": 4, "attendance_pct": 90.0, "score": 17.5, "max_score": 20.0, "score_pct": 87.5},
            {"subject_name": "Operating Systems", "subject_code": "CS605", "credits": 3, "attendance_pct": 85.0, "score": 15.0, "max_score": 20.0, "score_pct": 75.0},
        ]

    table_rows = [[
        Paragraph("<b>Code</b>", bold_body),
        Paragraph("<b>Subject Name</b>", bold_body),
        Paragraph("<b>Credits</b>", bold_body),
        Paragraph("<b>Attendance</b>", bold_body),
        Paragraph("<b>Internal (20)</b>", bold_body),
        Paragraph("<b>Evaluation</b>", bold_body)
    ]]

    for s in subjects:
        att = s.get("attendance_pct", 85.0)
        score = s.get("score", 15.0)
        status = "Strong" if score >= 16.0 else ("Satisfactory" if score >= 12.0 else "Needs Focus")
        table_rows.append([
            Paragraph(s.get("subject_code", "CS601"), body_style),
            Paragraph(s.get("subject_name", "Subject"), body_style),
            Paragraph(str(s.get("credits", 3)), body_style),
            Paragraph(f"{att:.1f}%", body_style),
            Paragraph(f"{score:.1f} / 20", body_style),
            Paragraph(status, bold_body)
        ])

    t_sub = Table(table_rows, colWidths=[60, 200, 50, 75, 75, 80])
    t_sub.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_sub)
    story.append(Spacer(1, 10))

    # 4. AI Predictive Analytics & Explainability (SHAP Insights)
    story.append(Paragraph("3. AI PERFORMANCE FORECAST & EXPLAINABILITY (SHAP)", section_heading))
    pred_pct = prediction_data.get("predicted_score_pct", 82.5)
    pred_g20 = prediction_data.get("predicted_grade_20", 16.5)
    p_low = prediction_data.get("prediction_range_low", 74.0)
    p_high = prediction_data.get("prediction_range_high", 90.0)
    risk_color = "#16a34a" if risk == "Low Risk" else ("#ca8a04" if risk == "Moderate Risk" else "#dc2626")

    ai_summary_data = [
        [
            Paragraph("<b>Predicted Final Examination Score:</b>", body_style),
            Paragraph(f"<b>{pred_pct:.1f}%</b> (≈ {pred_g20:.1f} / 20.0)", bold_body),
            Paragraph("<b>95% Credible Interval:</b>", body_style),
            Paragraph(f"{p_low:.1f}% to {p_high:.1f}%", body_style)
        ],
        [
            Paragraph("<b>Early-Warning Risk Classification:</b>", body_style),
            Paragraph(f"<font color='{risk_color}'><b>{risk}</b></font>", bold_body),
            Paragraph("<b>Primary Recommendation:</b>", body_style),
            Paragraph(prediction_data.get("primary_recommendation", "Maintain weekly study momentum & target quiz benchmarks."), body_style)
        ]
    ]
    t_ai = Table(ai_summary_data, colWidths=[150, 120, 130, 140])
    t_ai.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_ai)
    story.append(Spacer(1, 8))

    # SHAP Explanations Breakdown
    story.append(Paragraph("<b>Top Factors Influencing Model Output:</b>", bold_body))
    factors = prediction_data.get("factors", [
        ("Previous Internal Assessments (G2/G1)", "+6.2 pts", "Positive Academic Momentum"),
        ("Consistent Class Attendance (>85%)", "+2.8 pts", "High Lecture Engagement"),
        ("Weekly Self-Study Time Allocation", "+1.9 pts", "Diligent Study Habit"),
        ("Absences / Missed Practical Labs", "-1.4 pts", "Minor Practical Exposure Gap"),
    ])
    f_rows = [[Paragraph("<b>Feature / Academic Metric</b>", bold_body), Paragraph("<b>SHAP Impact</b>", bold_body), Paragraph("<b>Contextual Interpretation</b>", bold_body)]]
    for feat, imp, ctx in factors:
        color_str = "#15803d" if imp.startswith("+") else "#b91c1c"
        f_rows.append([
            Paragraph(feat, body_style),
            Paragraph(f"<font color='{color_str}'><b>{imp}</b></font>", body_style),
            Paragraph(ctx, body_style)
        ])
    t_f = Table(f_rows, colWidths=[170, 90, 280])
    t_f.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_f)
    story.append(Spacer(1, 10))

    # 5. Personalized Study Action Plan & Faculty Remarks
    story.append(Paragraph("4. PERSONALIZED STUDY PLAN & FACULTY REMARKS", section_heading))
    plan_text = prediction_data.get("study_plan_summary",
        "• Monday-Wednesday: 1.5 hrs Database Management System indexing & query optimization.<br/>"
        "• Thursday: 1.0 hr Computer Networks routing protocol problem solving.<br/>"
        "• Friday-Saturday: 2.0 hrs Machine Learning loss function derivation & past paper mock exams."
    )
    remarks_text = faculty_remarks or "Student is exhibiting consistent learning progress. Recommend participating in advanced technical seminar track."

    plan_table_data = [
        [Paragraph("<b>Weekly Study Plan Roadmap:</b>", bold_body)],
        [Paragraph(plan_text, body_style)],
        [Paragraph("<b>Faculty Mentor Remarks & Follow-up:</b>", bold_body)],
        [Paragraph(remarks_text, body_style)]
    ]
    t_plan = Table(plan_table_data, colWidths=[540])
    t_plan.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_plan)
    story.append(Spacer(1, 12))

    # 6. Governance & Disclaimer Box
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
    disclaimer_box = [
        [Paragraph(
            "<b>Institutional Responsible-Use Disclaimer:</b> Machine learning predictions and risk classifications are decision-support "
            "estimates derived from historical cohort data. They do not represent guaranteed academic outcomes or final grades. "
            "Predictions must support human faculty review, mentoring, and student guidance—never replace professional academic judgment, "
            "nor be used as the sole basis for academic penalties or admissions decisions.",
            disclaimer_style
        )]
    ]
    t_disc = Table(disclaimer_box, colWidths=[540])
    t_disc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fffbeb")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#fde68a")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_disc)

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

