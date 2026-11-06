"""
========================================================================================
VoltCore Apex Academia - Phase L Unit Test Suite (Features 321–330)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
========================================================================================
"""

import os
import sqlite3
import pytest
from backend.career_professional_engine import (
    CAREER_ROADMAPS,
    INTERVIEW_QUESTION_BANK,
    get_career_roadmap,
    update_skill_progress,
    query_interview_questions,
    generate_ece_resume,
    evaluate_technical_skills_assessment,
    track_internship_application,
    calculate_placement_readiness,
    init_career_db
)

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_career_professional.db")

@pytest.fixture(autouse=True)
def clean_test_db():
    """Ensure clean isolated SQLite test database."""
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
    init_career_db(TEST_DB_PATH)
    yield
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass

# Feature 321: ECE Career Roadmap
def test_get_career_roadmap():
    res_emb = get_career_roadmap("embedded_firmware")
    assert res_emb["status"] == "success"
    assert "Qualcomm" in res_emb["top_recruiters"]
    assert "8.5" in res_emb["avg_ctc_lpa"]

    res_vlsi = get_career_roadmap("digital_vlsi")
    assert "Intel" in res_vlsi["top_recruiters"]
    assert any("Verilog" in req for req in res_vlsi["core_prerequisites"])

# Feature 322: Embedded Systems Skill Tracker
def test_update_skill_progress():
    res = update_skill_progress(
        student_id="2023MITEC042",
        skill_name="ARM Cortex-M Bare-Metal Registers",
        category="Microcontrollers",
        proficiency_percentage=92.5,
        db_path=TEST_DB_PATH
    )
    assert res["status"] == "success"
    assert res["proficiency_percentage"] == 92.5
    assert res["category"] == "Microcontrollers"

# Feature 326: Technical Interview Question Bank
def test_query_interview_questions():
    all_qs = query_interview_questions("all", "all")
    assert len(all_qs) >= 4

    qualcomm_qs = query_interview_questions(domain="all", company="Qualcomm")
    assert len(qualcomm_qs) >= 1
    assert "const int *p" in qualcomm_qs[0]["question"]
    assert "read-only" in qualcomm_qs[0]["model_solution"]

    vlsi_qs = query_interview_questions(domain="Digital VLSI", company="all")
    assert len(vlsi_qs) >= 1
    assert "Setup Time" in vlsi_qs[0]["question"]

# Feature 327: Resume Builder
def test_generate_ece_resume():
    res = generate_ece_resume(
        student_name="Ashok Kumar A",
        roll_no="2023MITEC042",
        email="ashokkumar3132008@gmail.com",
        cgpa=8.85,
        flagship_project="VoltCore Apex Academia",
        db_path=TEST_DB_PATH
    )
    assert res["status"] == "success"
    assert "2023MITEC042" in res["resume_markdown"]
    assert "Madras Institute of Technology" in res["resume_markdown"]
    assert "8.85" in res["resume_markdown"]
    assert "Verilog HDL" in res["resume_markdown"]

# Feature 328: Technical Skills Assessment
def test_evaluate_technical_skills_assessment():
    # 4/4 correct answers
    full_correct = {"Q1": 1, "Q2": 2, "Q3": 0, "Q4": 3}
    res_full = evaluate_technical_skills_assessment(full_correct)
    assert res_full["total_score"] == 100.0
    assert res_full["readiness_level"] == "Tier-1 Day-0 Ready"

    # Partial answers
    partial = {"Q1": 1, "Q2": 0, "Q3": 0, "Q4": 0}
    res_part = evaluate_technical_skills_assessment(partial)
    assert res_part["total_score"] == 50.0
    assert res_part["readiness_level"] == "Intermediate Review Needed"

# Feature 329: Internship Application Tracker
def test_track_internship_application():
    res = track_internship_application(
        company="Texas Instruments",
        role="Analog IC Design Intern",
        tier="Tier 1",
        stipend_inr=50000.0,
        status="TECH_ROUND_1",
        deadline_date="2026-12-01",
        student_id="2023MITEC042",
        db_path=TEST_DB_PATH
    )
    assert res["status"] == "success"
    assert res["company"] == "Texas Instruments"
    assert res["app_status"] == "TECH_ROUND_1"
    assert res["stipend_inr"] == 50000.0

# Feature 330: Placement Preparation Dashboard
def test_calculate_placement_readiness():
    res = calculate_placement_readiness(
        student_id="2023MITEC042",
        cgpa=8.85,
        aptitude_score=90.0,
        core_ece_score=95.0,
        coding_score=88.0,
        target_companies=["Qualcomm", "TI", "Intel"],
        db_path=TEST_DB_PATH
    )
    assert res["status"] == "success"
    # composite: 0.35*95 + 0.25*90 + 0.25*88 + 0.15*88.5 = 33.25 + 22.5 + 22.0 + 13.275 = 91.0
    assert res["readiness_percentage"] >= 88.0
    assert res["is_day_zero_eligible"] is True
    assert len(res["target_companies"]) == 3

# SQLite WAL Persistence Test
def test_career_sqlite_wal_persistence():
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    assert "career_skill_progress" in tables
    assert "internship_applications" in tables
    assert "placement_readiness" in tables
    assert "student_resumes" in tables
    conn.close()
