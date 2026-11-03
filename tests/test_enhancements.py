"""Unit tests for AI enhancements: What-If simulator, subject analyzer, study planner, assistant, report, and database."""
import pytest
from src.predict import StudentPredictor
from src.what_if_simulator import simulate_academic_scenario
from src.subject_analyzer import analyze_subject_performance
from src.study_planner import generate_personalized_study_plan
from src.academic_assistant import query_academic_assistant
from src.report_generator import generate_student_academic_report
from database.database import init_database, log_prediction, log_faculty_intervention, get_all_interventions


@pytest.fixture(scope="module")
def predictor():
    return StudentPredictor()


@pytest.fixture(scope="module")
def sample_record():
    return {
        "subject": "Mathematics",
        "G1": 12,
        "G2": 12,
        "absences": 4,
        "failures": 0,
        "studytime": 2,
        "goout": 3,
        "freetime": 3,
        "higher": "yes"
    }


def test_what_if_simulation(predictor, sample_record):
    mods = {"studytime": 4, "absences": 1}
    res = simulate_academic_scenario(predictor, sample_record, mods)
    assert "score_delta" in res
    assert "comparison_table" in res
    assert len(res["comparison_table"]) > 0


def test_subject_performance_analysis(predictor, sample_record):
    subj_res = analyze_subject_performance(predictor, sample_record)
    assert "subjects_table" in subj_res
    assert len(subj_res["subjects_table"]) >= 5
    assert "estimated_semester_cgpa" in subj_res


def test_study_plan_generation():
    plan = generate_personalized_study_plan(["Database Management (DBMS)", "Mathematics"], daily_study_hours=2.5)
    assert len(plan["schedule_table"]) == 7
    assert plan["total_weekly_hours"] == 15.0
    assert len(plan["recommendation_tips"]) > 0


def test_academic_assistant_responses(predictor, sample_record):
    pred = predictor.predict_single(sample_record)
    ans1 = query_academic_assistant("Why is my risk classified as moderate?", pred)
    assert "risk category" in ans1["answer"].lower()
    assert len(ans1["sources"]) > 0

    ans2 = query_academic_assistant("Which subjects require more attention?", pred)
    assert "database" in ans2["answer"].lower() or "score" in ans2["answer"].lower()

    ans3 = query_academic_assistant("Create a study plan for exams", pred)
    assert "roadmap" in ans3["answer"].lower() or "schedule" in ans3["answer"].lower()


def test_report_generation(predictor, sample_record):
    pred = predictor.predict_single(sample_record)
    report = generate_student_academic_report(pred, "Tharun Reddy", "STU1024")
    assert "TREKVERSE AI ACADEMY" in report
    assert "STU1024" in report
    assert "SECTION 1: STUDENT INFORMATION" in report
    assert "SECTION 3: AI / MACHINE LEARNING" in report


def test_database_persistence(tmp_path, predictor, sample_record):
    db_file = tmp_path / "test_db.sqlite"
    from database.database import SCHEMA_PATH
    init_database(db_file, SCHEMA_PATH)

    pred = predictor.predict_single(sample_record)
    pred_id = log_prediction("STU1024", pred, db_file)
    assert pred_id > 0

    inv_id = log_faculty_intervention("STU1024", "FAC-CSE-01", "Mentoring", "All good", db_file)
    assert inv_id > 0

    all_invs = get_all_interventions(db_file)
    assert len(all_invs) == 1
    assert all_invs[0]["roll_number"] == "STU1024"
