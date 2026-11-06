"""
========================================================================================
VoltCore Apex Academia - Unit Tests for Projects, Practicals & Progress Tracking
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead & Systems Architect: Ashok Kumar A
========================================================================================
"""

import pytest
import tempfile
import os
from backend.course_projects_engine import CourseProjectsEngine, COURSE_PROJECTS_CATALOG, COURSE_PRACTICALS_CATALOG


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


@pytest.fixture
def projects_engine(temp_db):
    return CourseProjectsEngine(db_path=temp_db)


def test_catalog_validation(projects_engine):
    """Verify that all project milestones sum to 100% and practical rubrics sum to 30 marks."""
    audit = projects_engine.validate_catalog()
    assert audit["valid"] is True, f"Validation errors: {audit.get('errors')}"
    assert audit["total_courses"] == 4
    assert audit["total_projects"] >= 8
    assert audit["total_practicals"] >= 6


def test_projects_exist_for_all_courses(projects_engine):
    """Verify each priority course has both mini and major projects."""
    for code in ["EC23S01", "EC23C03", "EC23E04", "EC8702"]:
        projs = COURSE_PROJECTS_CATALOG.get(code, [])
        assert len(projs) >= 2, f"Course {code} must have at least 2 projects"
        types = {p["type"] for p in projs}
        assert "mini" in types
        assert "major" in types


def test_calculate_course_progress_zero(projects_engine):
    """Verify progress calculation when no milestones or practicals are completed."""
    res = projects_engine.calculate_course_progress("EC23S01", [], [])
    assert res["overall_percentage"] == 0.0
    assert res["finished_milestones"] == 0
    assert res["finished_practicals"] == 0
    assert res["earned_xp"] == 0
    assert res["academic_rank"] == "Novice Explorer"


def test_calculate_course_progress_partial(projects_engine):
    """Verify progress calculation with partial completion."""
    completed_milestones = ["EC23S01_PRJ1_M1", "EC23S01_PRJ1_M2"]
    verified_practicals = ["EC23S01_EXP1"]
    res = projects_engine.calculate_course_progress(
        "EC23S01",
        completed_milestones,
        verified_practicals
    )
    # Total milestones = 8 (4 in PRJ1 + 4 in PRJ2). Finished = 2. Weight = (2/8)*60 = 15%
    # Total practicals = 2. Finished = 1. Weight = (1/2)*40 = 20%
    # Overall = 15 + 20 = 35.0%
    assert res["overall_percentage"] == 35.0
    assert res["earned_xp"] == (2 * 250) + (1 * 500)  # 1000 XP
    assert res["academic_rank"] == "Laboratory Practitioner"


def test_calculate_course_progress_complete(projects_engine):
    """Verify 100% course completion leads to Apex Systems Architect rank."""
    # Complete all milestones and practicals for EC23C03
    all_milestones = [
        "EC23C03_PRJ1_M1", "EC23C03_PRJ1_M2", "EC23C03_PRJ1_M3", "EC23C03_PRJ1_M4",
        "EC23C03_PRJ2_M1", "EC23C03_PRJ2_M2", "EC23C03_PRJ2_M3", "EC23C03_PRJ2_M4"
    ]
    all_practicals = ["EC23C03_EXP1", "EC23C03_EXP2"]
    res = projects_engine.calculate_course_progress(
        "EC23C03",
        all_milestones,
        all_practicals
    )
    assert res["overall_percentage"] == 100.0
    assert res["academic_rank"] == "Apex Systems Architect"
    assert res["earned_xp"] == (8 * 250) + (2 * 500)  # 3000 XP


def test_generate_lab_report(projects_engine):
    """Verify lab report template generation."""
    report = projects_engine.generate_lab_report(
        course_code="EC23S01",
        practical_id="EC23S01_EXP1",
        student_name="Karthik R",
        roll_number="2023MITEC099"
    )
    assert "report_markdown" in report
    text = report["report_markdown"]
    assert "Karthik R" in text
    assert "2023MITEC099" in text
    assert "Continuous Internal Evaluation (CIE) Rubric" in text
    assert "Discrete Linear & Circular Convolution" in text


def test_log_milestone_submission(projects_engine):
    """Verify SQLite WAL milestone submission logging."""
    res = projects_engine.log_milestone_submission(
        course_code="EC8702",
        project_id="EC8702_PRJ1",
        milestone_id="M1",
        student_id="2023MITEC042",
        deliverable_url="https://github.com/AshokKumar313/VoltCore-LMS-Portal/commit/eeac6db"
    )
    assert res["status"] == "success"
    assert "submission_id" in res
