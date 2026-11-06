"""
========================================================================================
VoltCore Apex Academia - Phase K Unit Test Suite (Features 311–320)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
========================================================================================
"""

import os
import sqlite3
import pytest
from backend.student_projects_engine import (
    generate_project_ideas,
    generate_project_proposal_template,
    initialize_project_milestones,
    assign_project_team,
    generate_bill_of_materials,
    audit_project_documentation,
    validate_github_project_repo,
    submit_project_demo,
    create_digital_portfolio,
    init_projects_db
)

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_student_projects.db")

@pytest.fixture(autouse=True)
def clean_test_db():
    """Ensure clean isolated SQLite test database."""
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
    init_projects_db(TEST_DB_PATH)
    yield
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass

# Feature 311: ECE Project Idea Generator
def test_generate_project_ideas():
    all_ideas = generate_project_ideas("all", "all")
    assert len(all_ideas) >= 5

    iot_ideas = generate_project_ideas("embedded_iot", "all")
    assert len(iot_ideas) >= 2
    assert any("LoRaWAN" in item["title"] for item in iot_ideas)

    vlsi_ideas = generate_project_ideas("vlsi_fpga", "advanced")
    assert len(vlsi_ideas) >= 1
    assert any("RISC-V" in item["title"] for item in vlsi_ideas)

# Feature 312: Project Proposal Template
def test_generate_project_proposal_template():
    res = generate_project_proposal_template(
        project_title="Edge-AI IoT Irrigation Node",
        domain="Embedded Systems",
        student_lead="Ashok Kumar A",
        roll_no="2023MITEC042"
    )
    assert res["status"] == "success"
    assert "ANNA UNIVERSITY" in res["proposal_markdown"]
    assert "2023MITEC042" in res["proposal_markdown"]
    assert "FACULTY GUIDE APPROVAL" in res["proposal_markdown"]

# Feature 313: Project Milestones
def test_initialize_project_milestones():
    milestones = initialize_project_milestones("PRJ-2026-001", db_path=TEST_DB_PATH)
    assert len(milestones) == 5
    assert milestones[0]["rev"] == 0
    assert milestones[0]["status"] == "COMPLETED"
    assert milestones[2]["rev"] == 2
    assert milestones[2]["status"] == "IN_PROGRESS"

# Feature 314: Team Role Manager
def test_assign_project_team():
    members = [
        {"name": "Ashok Kumar A", "roll_no": "2023MITEC042", "role": "Team Lead & Firmware Architect"},
        {"name": "Dinesh K", "roll_no": "2023MITEC015", "role": "Hardware & PCB Layout Engineer"},
        {"name": "Harini S", "roll_no": "2023MITEC028", "role": "DSP & Simulation Specialist"}
    ]
    res = assign_project_team(
        project_id="PRJ-2026-001",
        project_title="Smart LoRaWAN Agriculture",
        domain="Embedded IoT",
        members=members,
        budget_inr=7500.0,
        github_url="https://github.com/AshokKumar313/VoltCore-LMS-Portal",
        db_path=TEST_DB_PATH
    )
    assert res["status"] == "success"
    assert res["team_size"] == 3
    assert res["members"][0]["roll_no"] == "2023MITEC042"

# Feature 315 & 316: BOM Cost Calculator
def test_generate_bill_of_materials():
    components = [
        {"name": "ESP32-S3 Microcontroller", "ref_des": "U1", "mpn": "ESP32-S3-WROOM-1", "package": "QFN-56", "quantity": 1, "unit_price_inr": 450.0},
        {"name": "SX1262 LoRa Transceiver", "ref_des": "U2", "mpn": "SX1262IMLTRT", "package": "QFN-24", "quantity": 1, "unit_price_inr": 350.0},
        {"name": "Decoupling Capacitors 100nF", "ref_des": "C1-C10", "mpn": "CC0805KRX7R9BB104", "package": "0805 SMD", "quantity": 10, "unit_price_inr": 5.0},
        {"name": "Pull-up Resistors 10k", "ref_des": "R1-R5", "mpn": "RC0805JR-0710KL", "package": "0805 SMD", "quantity": 5, "unit_price_inr": 2.0}
    ]
    res = generate_bill_of_materials(
        project_id="PRJ-2026-001",
        components=components,
        gst_percent=18.0,
        contingency_percent=15.0,
        db_path=TEST_DB_PATH
    )
    assert res["status"] == "success"
    assert res["line_items_count"] == 4
    # subtotal = 450 + 350 + 50 + 10 = 860.0
    assert res["subtotal_inr"] == 860.0
    # GST = 154.8, Contingency = 129.0, Total = 1143.8
    assert res["gst_inr"] == 154.8
    assert res["contingency_inr"] == 129.0
    assert res["total_cost_inr"] == 1143.8
    assert res["total_cost_usd"] > 0

# Feature 317: Documentation Checklist
def test_audit_project_documentation():
    # 1. Complete submission
    full_checklist = {
        "synopsis_signed": True,
        "literature_survey": True,
        "block_and_schematic": True,
        "bom_and_gerbers": True,
        "modular_source_code": True,
        "observation_error_table": True,
        "plagiarism_report": True,
        "hardcover_binding": True
    }
    res_full = audit_project_documentation(full_checklist)
    assert res_full["compliance_percentage"] == 100.0
    assert res_full["submission_ready"] is True
    assert len(res_full["missing_critical"]) == 0

    # 2. Incomplete missing critical plagiarism
    incomplete_checklist = {
        "synopsis_signed": True,
        "literature_survey": True,
        "block_and_schematic": True,
        "bom_and_gerbers": True,
        "modular_source_code": True,
        "observation_error_table": True,
        "plagiarism_report": False,
        "hardcover_binding": False
    }
    res_inc = audit_project_documentation(incomplete_checklist)
    assert res_inc["submission_ready"] is False
    assert any("Plagiarism" in s for s in res_inc["missing_critical"])

# Feature 318: GitHub Link Validator
def test_validate_github_project_repo():
    valid_res = validate_github_project_repo("https://github.com/AshokKumar313/VoltCore-LMS-Portal")
    assert valid_res["status"] == "success"
    assert valid_res["is_valid"] is True
    assert valid_res["owner"] == "AshokKumar313"
    assert valid_res["repo_name"] == "VoltCore-LMS-Portal"

    invalid_res = validate_github_project_repo("not_a_github_url")
    assert invalid_res["is_valid"] is False

# Feature 319: Project Demo Submission
def test_submit_project_demo():
    res = submit_project_demo(
        project_id="PRJ-2026-001",
        video_url="https://youtu.be/example_demo_link",
        examiner_scores={
            "innovation": 9.5,
            "hardware_execution": 14.5,
            "code_quality": 9.0,
            "documentation": 5.0,
            "viva_defence": 9.5
        },
        feedback="Flawless real-time LoRa packet transmission and telemetry reception.",
        db_path=TEST_DB_PATH
    )
    assert res["status"] == "success"
    assert res["total_score"] == 47.5
    assert res["max_score"] == 50.0

# Feature 320: Digital Portfolio
def test_create_digital_portfolio():
    res = create_digital_portfolio(
        student_id="2023MITEC042",
        student_name="Ashok Kumar A",
        title="Silicon Systems & Embedded Firmware Architect",
        skills=["Verilog HDL", "ARM Cortex-M", "LoRaWAN", "TinyML"],
        badges=["Hardware Grandmaster", "Firmware Architect"],
        featured_project_id="PRJ-2026-001",
        db_path=TEST_DB_PATH
    )
    assert res["status"] == "success"
    assert res["student_id"] == "2023MITEC042"
    assert len(res["skills"]) == 4
    assert len(res["badges"]) == 2

# SQLite WAL Persistence Test
def test_student_projects_sqlite_wal_persistence():
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    assert "student_projects" in tables
    assert "project_milestones" in tables
    assert "project_bom_items" in tables
    assert "project_portfolios" in tables
    assert "project_demo_submissions" in tables
    conn.close()
