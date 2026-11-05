"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 25 (Faculty & Department Productivity)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase25_faculty_productivity.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import sys
import json
import sqlite3
import pytest

# Ensure repository root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.faculty_productivity_engine import (
    FacultyProductivityEngine,
    faculty_productivity_engine,
    DEFAULT_FACULTY_ID,
    DEFAULT_STUDENT_ID,
    FACULTY_TEMPLATES_CATALOG
)


@pytest.fixture
def test_engine(tmp_path):
    """Provides an isolated FacultyProductivityEngine backed by a temporary SQLite WAL DB."""
    db_file = str(tmp_path / "test_faculty_productivity.db")
    engine = FacultyProductivityEngine(db_path=db_file)
    return engine


def test_faculty_engine_initialization(test_engine):
    """Verifies table creation, SQLite WAL mode, and template seeding."""
    conn = test_engine._get_connection()
    try:
        cur = conn.execute("PRAGMA journal_mode;")
        journal_mode = cur.fetchone()[0].upper()
        assert journal_mode == "WAL", f"Expected WAL mode, got {journal_mode}"

        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        assert "faculty_lesson_plans" in tables
        assert "faculty_lesson_templates" in tables
        assert "faculty_assignments" in tables
        assert "assignment_submissions_feedback" in tables
        assert "department_meeting_minutes" in tables

        cur = conn.execute("SELECT COUNT(*) FROM faculty_lesson_templates;")
        assert cur.fetchone()[0] >= len(FACULTY_TEMPLATES_CATALOG)
    finally:
        conn.close()


def test_get_overview_metrics(test_engine):
    """Tests faculty overview statistics, syllabus coverage, and meeting counts."""
    overview = test_engine.get_overview(DEFAULT_FACULTY_ID)
    assert overview["status"] == "SUCCESS"
    assert "metrics" in overview

    metrics = overview["metrics"]
    assert metrics["total_lesson_plans"] >= 8
    assert metrics["completed_lesson_plans"] >= 5
    assert metrics["total_assignments"] >= 2
    assert metrics["total_meeting_minutes"] >= 1
    assert 0.0 <= metrics["syllabus_coverage_percent"] <= 100.0
    assert metrics["total_planned_hours"] > 0.0


def test_lesson_plan_creation_and_filtering(test_engine):
    """Validates creation of syllabus unit topics and filtering by course and unit."""
    # Filter by course
    plans_ec3451 = test_engine.get_lesson_plans(course_code="EC3451")
    assert len(plans_ec3451) >= 5

    # Filter by course and unit
    unit1_plans = test_engine.get_lesson_plans(course_code="EC3451", unit_number=1)
    assert len(unit1_plans) >= 2
    for p in unit1_plans:
        assert p["unit_number"] == 1
        assert p["course_code"] == "EC3451"

    # Create new plan as faculty
    new_plan_data = {
        "course_code": "EC3352",
        "course_title": "Digital Systems Design",
        "unit_number": 3,
        "unit_title": "Unit III: Synchronous Sequential Logic",
        "topic_title": "Design of Mealy and Moore State Machines with D Flip-Flops",
        "planned_hours": 2.0,
        "pedagogy_mode": "Wokwi Simulation",
        "course_outcome": "CO3",
        "bloom_level": "K3-Apply",
        "notes": "State diagram derivation and Verilog implementation."
    }
    create_res = test_engine.create_lesson_plan(new_plan_data, actor_role="Faculty")
    assert create_res["status"] == "SUCCESS"
    pid = create_res["plan_id"]

    # Verify retrieval
    retrieved = test_engine.get_lesson_plans(course_code="EC3352", unit_number=3)
    assert any(p["plan_id"] == pid for p in retrieved)


def test_lesson_plan_status_transitions(test_engine):
    """Validates status progression (PLANNED -> IN_PROGRESS -> COMPLETED) and completion date."""
    plans = test_engine.get_lesson_plans(course_code="EC3451", unit_number=3)
    assert len(plans) >= 1
    target = plans[0]
    pid = target["plan_id"]

    # Transition to IN_PROGRESS
    res1 = test_engine.update_lesson_plan_status(pid, "IN_PROGRESS", actual_hours=1.0, actor_role="Faculty")
    assert res1["status"] == "SUCCESS"
    assert res1["new_status"] == "IN_PROGRESS"
    assert res1["completed_date"] is None

    # Transition to COMPLETED
    res2 = test_engine.update_lesson_plan_status(pid, "COMPLETED", actual_hours=2.0, actor_role="Faculty")
    assert res2["status"] == "SUCCESS"
    assert res2["new_status"] == "COMPLETED"
    assert res2["completed_date"] is not None


def test_assignment_distribution_and_rubrics(test_engine):
    """Validates assignment publishing with weighted rubric schema."""
    asgn_data = {
        "course_code": "EC3601",
        "title": "Assignment 2: Rate Monotonic Scheduling & Priority Inversion in FreeRTOS",
        "unit_number": 3,
        "due_date": "2026-12-10",
        "total_marks": 100.0,
        "instructions": "Demonstrate priority inversion using 3 FreeRTOS tasks and solve using Mutex Priority Inheritance.",
        "questions": [
            "Compute the Liu and Layland CPU utilization bound for 3 periodic tasks.",
            "Write the FreeRTOS task function simulating unbounded priority inversion.",
            "Show trace buffer capture confirming priority inheritance."
        ],
        "rubric": {
            "theoretical_utilization_calc": 25,
            "freertos_code_quality": 35,
            "logic_analyzer_trace": 25,
            "report_presentation": 15
        }
    }

    create_res = test_engine.create_assignment(asgn_data, actor_role="Faculty")
    assert create_res["status"] == "SUCCESS"
    aid = create_res["assignment_id"]

    # Verify retrieval
    asgns = test_engine.get_assignments(course_code="EC3601")
    assert any(a["assignment_id"] == aid for a in asgns)


def test_submission_evaluation_and_feedback(test_engine):
    """Validates grading, rubric breakdown, and score boundary enforcement."""
    # Valid feedback
    fb_data = {
        "assignment_id": "ASGN_EC3451_01",
        "student_id": "2023MITEC042",
        "student_name": "Ashok Kumar A",
        "marks_obtained": 98.0,
        "total_marks": 100.0,
        "evaluation_rubric_scores": {
            "mathematical_derivation": 25.0,
            "component_selection": 25.0,
            "simulation_accuracy": 30.0,
            "interpretation_and_report": 18.0
        },
        "qualitative_feedback": "Perfect mathematical formulation. Bode cutoff aligns exactly with nominal value."
    }

    fb_res = test_engine.record_feedback(fb_data, actor_role="Faculty")
    assert fb_res["status"] == "SUCCESS"
    assert fb_res["marks_obtained"] == 98.0

    # Retrieve and verify
    feedbacks = test_engine.get_assignment_feedback(assignment_id="ASGN_EC3451_01", student_id="2023MITEC042")
    assert len(feedbacks) >= 1
    assert feedbacks[0]["marks_obtained"] == 98.0

    # Invalid score (> 100.0)
    invalid_fb = {
        "assignment_id": "ASGN_EC3451_01",
        "student_id": "2023MITEC042",
        "marks_obtained": 120.0,
        "total_marks": 100.0
    }
    inv_res = test_engine.record_feedback(invalid_fb, actor_role="Faculty")
    assert inv_res["status"] == "ERROR"
    assert "between 0.0 and 100.0" in inv_res["message"]


def test_department_meeting_minutes_and_action_tracking(test_engine):
    """Validates department council meeting minutes recording and action item retrieval."""
    mom_data = {
        "meeting_title": "Continuous Attainment Review & NBA Criteria Audit",
        "meeting_date": "2026-11-02",
        "chairperson": "Dr. P. Nirmal Kumar (HOD, Electronics)",
        "attendees": ["Dr. P. Nirmal Kumar", "Dr. M. Kannan", "Dr. S. Piramasubramanian"],
        "agenda_items": ["Review of CO-PO attainment matrices for Semester 4", "Laboratory safety protocol updates"],
        "key_decisions": ["Approved modified experiment sequence for EC3451"],
        "action_items": [
            {"task": "Upload revised lab manual to VoltCore portal", "assignee": "Dr. S. Piramasubramanian", "deadline": "2026-11-10", "status": "IN_PROGRESS"}
        ]
    }

    mom_res = test_engine.record_meeting_minutes(mom_data, actor_role="Faculty")
    assert mom_res["status"] == "SUCCESS"

    meetings = test_engine.get_meeting_minutes()
    assert len(meetings) >= 2
    assert any("NBA Criteria Audit" in m["meeting_title"] for m in meetings)


def test_faculty_rbac_permission_barriers(test_engine):
    """Strictly verifies that student roles cannot mutate faculty lesson plans or issue grades."""
    # 1. Student attempting to create lesson plan
    res1 = test_engine.create_lesson_plan({
        "course_code": "EC3451",
        "topic_title": "Unauthorized Plan"
    }, actor_role="Student")
    assert res1["status"] == "FORBIDDEN"

    # 2. Student attempting to update plan status
    res2 = test_engine.update_lesson_plan_status("LP_EC3451_01", "COMPLETED", actor_role="Student")
    assert res2["status"] == "FORBIDDEN"

    # 3. Student attempting to publish assignment
    res3 = test_engine.create_assignment({
        "course_code": "EC3451",
        "title": "Unauthorized Assignment",
        "due_date": "2026-12-01"
    }, actor_role="Student")
    assert res3["status"] == "FORBIDDEN"

    # 4. Student attempting to grade
    res4 = test_engine.record_feedback({
        "assignment_id": "ASGN_EC3451_01",
        "student_id": "2023MITEC042",
        "marks_obtained": 100.0
    }, actor_role="Student")
    assert res4["status"] == "FORBIDDEN"

    # 5. Student attempting to record meeting minutes
    res5 = test_engine.record_meeting_minutes({
        "meeting_title": "Unauthorized Meeting"
    }, actor_role="Student")
    assert res5["status"] == "FORBIDDEN"


def test_privacy_invariants_no_credential_leakage():
    """Guarantees zero client-side or repository leakage of private admin credentials."""
    forbidden_tokens = ["ashokkumar2008313@gmail.com", "9597382878"]
    target_files = [
        os.path.join(BASE_DIR, "backend", "faculty_productivity_engine.py"),
        os.path.join(BASE_DIR, "src", "components", "FacultyProductivityHub.jsx"),
        os.path.join(BASE_DIR, "src", "pages", "faculty-workspace.astro")
    ]

    for fpath in target_files:
        assert os.path.exists(fpath), f"File {fpath} does not exist"
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            for token in forbidden_tokens:
                assert token not in content, f"SECURITY ALERT: Private token '{token}' leaked in {fpath}"
