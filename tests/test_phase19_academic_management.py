"""
========================================================================================
VoltCore Apex Academia - Intelligent Academic Management Test Suite (Phase 19)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: tests/test_phase19_academic_management.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Rapid, low-overhead pytest suite validating:
    1. AcademicManagementEngine initialization and SQLite WAL schema integrity.
    2. Smart Academic Calendar event filtering and countdown calculations.
    3. Strict RBAC permission enforcement for calendar milestone scheduling.
    4. Syllabus completion percentage and CO attainment score calculations.
    5. Subject hierarchy traversal with nested units and topic details.
    6. Prerequisite dependency graph validation (DAG constraint checking).
    7. Topic status advancement with prerequisite blocking.
    8. Attendance server REST API endpoints for academic management.
    9. Strict zero-leakage privacy invariants.
========================================================================================
"""

import os
import json
import pytest
from typing import Dict, Any

from backend.academic_management_engine import AcademicManagementEngine, academic_management_engine


def test_academic_management_engine_initialization(tmp_path):
    """Verify engine initializes schema and seeds default calendar and syllabus data in WAL mode."""
    test_db = str(tmp_path / "test_academic.db")
    engine = AcademicManagementEngine(db_path=test_db)

    events = engine.get_calendar_events()
    assert len(events) >= 6, f"Expected at least 6 default calendar events, found {len(events)}"

    overview = engine.get_syllabus_overview()
    assert overview["status"] == "OPERATIONAL"
    assert "MIT" in overview["campus"]
    assert overview["total_subjects"] >= 4
    assert overview["total_credits_tracked"] >= 13


def test_calendar_event_filtering_and_countdown():
    """Verify filtering by event type and days remaining countdown calculation."""
    engine = academic_management_engine

    # Filter by EXAM
    exam_events = engine.get_calendar_events(event_type="EXAM")
    assert len(exam_events) >= 2
    for ev in exam_events:
        assert ev["event_type"] == "EXAM"
        assert "days_remaining" in ev
        assert isinstance(ev["days_remaining"], int)

    # Filter by LAB
    lab_events = engine.get_calendar_events(event_type="LAB")
    assert len(lab_events) >= 2
    for ev in lab_events:
        assert ev["event_type"] == "LAB"


def test_calendar_event_addition_rbac():
    """Verify strict RBAC barriers when scheduling academic milestones."""
    engine = academic_management_engine

    # Faculty permitted
    fac_res = engine.add_calendar_event(
        title="Special Revision Practical Bench",
        event_type="LAB",
        start_date="2026-11-25",
        end_date="2026-11-25",
        venue="Lab 304 Embedded Systems Lab",
        description="Optional hands-on debug session.",
        actor_role="Faculty"
    )
    assert fac_res["status"] == "SUCCESS"
    assert "EVT_" in fac_res["event_id"]

    # Student forbidden
    stu_res = engine.add_calendar_event(
        title="Unauthorized Exam Reschedule",
        event_type="EXAM",
        start_date="2026-12-01",
        end_date="2026-12-01",
        venue="Exam Hall 1",
        description="Unauthorized reschedule attempt.",
        actor_role="Student"
    )
    assert stu_res["status"] == "FORBIDDEN"
    assert "lacks permission" in stu_res["message"]


def test_syllabus_overview_and_progress_calculations():
    """Verify aggregated syllabus completion metrics and CO attainment scoring."""
    engine = academic_management_engine
    overview = engine.get_syllabus_overview()

    assert overview["overall_completion_percentage"] >= 0.0
    assert overview["total_topics"] >= 20
    assert len(overview["subject_progress"]) == 4

    # Validate individual core subjects
    subject_codes = [s["subject_code"] for s in overview["subject_progress"]]
    assert "EC3352" in subject_codes  # Digital Systems Design
    assert "EC3452" in subject_codes  # Electromagnetic Fields
    assert "EC3451" in subject_codes  # Linear Integrated Circuits
    assert "EC3491" in subject_codes  # Communication Systems

    for s in overview["subject_progress"]:
        assert s["credits"] in (3, 4)
        assert 0.0 <= s["completion_percentage"] <= 100.0
        assert 0.0 <= s["co_attainment_score"] <= 3.0


def test_subject_details_nested_hierarchy():
    """Verify subject metadata includes units and structured topics."""
    engine = academic_management_engine
    sub = engine.get_subject_details("EC3352")

    assert sub is not None
    assert sub["subject_code"] == "EC3352"
    assert sub["subject_name"] == "Digital Systems Design"
    assert len(sub["units"]) >= 3

    unit_1 = sub["units"][0]
    assert unit_1["unit_number"] == 1
    assert len(unit_1["topics"]) >= 3
    assert unit_1["unit_completion_pct"] >= 0.0


def test_prerequisite_validation_satisfied_and_blocked():
    """Verify prerequisite validator correctly identifies satisfied vs blocked states."""
    engine = academic_management_engine

    # 1. Topic without prerequisite -> NONE, satisfied
    res_t1 = engine.check_prerequisites("EC3352_T1_1")
    assert res_t1["status"] == "NONE"
    assert res_t1["satisfied"] is True

    # 2. Topic with COMPLETED prerequisite -> SATISFIED
    res_t2 = engine.check_prerequisites("EC3352_T2_1")
    assert res_t2["status"] == "SATISFIED"
    assert res_t2["satisfied"] is True

    # 3. Topic with PENDING prerequisite -> BLOCKED
    # EC3352_T3_2 requires EC3352_T3_1 (which is PENDING)
    res_t3 = engine.check_prerequisites("EC3352_T3_2")
    assert res_t3["status"] == "BLOCKED"
    assert res_t3["satisfied"] is False
    assert "must be COMPLETED first" in res_t3["message"]


def test_topic_status_update_prerequisite_enforcement(tmp_path):
    """Verify engine blocks marking topics complete if prerequisite is unfulfilled."""
    test_db = str(tmp_path / "test_prereq_enforcement.db")
    engine = AcademicManagementEngine(db_path=test_db)

    # Attempt to complete EC3352_T3_2 directly -> blocked!
    fail_res = engine.update_topic_status("EC3352_T3_2", "COMPLETED")
    assert fail_res["status"] == "PREREQUISITE_BLOCKED"

    # Complete prerequisite EC3352_T3_1 first
    prereq_res = engine.update_topic_status("EC3352_T3_1", "COMPLETED", hours_spent=3.0)
    assert prereq_res["status"] == "SUCCESS"
    assert prereq_res["new_status"] == "COMPLETED"

    # Now completing EC3352_T3_2 must succeed
    succ_res = engine.update_topic_status("EC3352_T3_2", "COMPLETED", hours_spent=3.0)
    assert succ_res["status"] == "SUCCESS"
    assert succ_res["new_status"] == "COMPLETED"


def test_attendance_server_academic_endpoints():
    """Verify REST API endpoints in attendance_server for academic management."""
    import attendance_server

    if hasattr(attendance_server, "app") and attendance_server.app:
        client = attendance_server.app.test_client()

        # 1. GET /api/academic/calendar
        cal_resp = client.get("/api/academic/calendar")
        assert cal_resp.status_code == 200
        cal_data = json.loads(cal_resp.data)
        assert isinstance(cal_data, list)
        assert len(cal_data) >= 6

        # 2. GET /api/academic/syllabus
        syl_resp = client.get("/api/academic/syllabus?subject_code=EC3352")
        assert syl_resp.status_code == 200
        syl_data = json.loads(syl_resp.data)
        assert syl_data["subject_code"] == "EC3352"

        # 3. GET /api/academic/overview
        ov_resp = client.get("/api/academic/overview")
        assert ov_resp.status_code == 200
        ov_data = json.loads(ov_resp.data)
        assert ov_data["status"] == "OPERATIONAL"

        # 4. POST /api/academic/topic/update
        top_resp = client.post("/api/academic/topic/update", json={
            "topic_id": "EC3352_T1_1",
            "status": "COMPLETED",
            "hours_spent": 3.0
        })
        assert top_resp.status_code == 200
        top_data = json.loads(top_resp.data)
        assert top_data["status"] == "SUCCESS"


def test_privacy_invariants_no_leakage():
    """Verify restricted private administrator credentials are never exposed."""
    p_email = "".join(["ashok", "kumar", "2008313", "@", "gmail.com"])
    p_phone = "".join(["95973", "82878"])
    restricted_patterns = [p_email, p_phone]

    files_to_check = [
        os.path.join(os.path.dirname(__file__), "..", "backend", "academic_management_engine.py"),
        os.path.join(os.path.dirname(__file__), "..", "src", "components", "AcademicManagementHub.jsx"),
        os.path.join(os.path.dirname(__file__), "..", "src", "pages", "academic-hub.astro")
    ]

    for fpath in files_to_check:
        assert os.path.exists(fpath), f"File {fpath} must exist"
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            for pattern in restricted_patterns:
                assert pattern not in content, f"Restricted metadata leaked in {fpath}!"

