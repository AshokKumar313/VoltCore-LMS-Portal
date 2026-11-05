"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 24 (Engineering Project & Innovation Center)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase24_project_innovation.py
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

from backend.project_innovation_engine import (
    ProjectInnovationEngine,
    project_innovation_engine,
    DEFAULT_STUDENT_ID,
    INNOVATION_IDEAS_CATALOG,
    MCU_DATABASE
)


@pytest.fixture
def test_engine(tmp_path):
    """Provides an isolated ProjectInnovationEngine backed by a temporary SQLite WAL DB."""
    db_file = str(tmp_path / "test_project_innovation.db")
    engine = ProjectInnovationEngine(db_path=db_file)
    return engine


def test_project_innovation_engine_initialization(test_engine):
    """Verifies table creation, SQLite WAL mode, and curated ideas seeding."""
    conn = test_engine._get_connection()
    try:
        # Check SQLite WAL mode
        cur = conn.execute("PRAGMA journal_mode;")
        journal_mode = cur.fetchone()[0].upper()
        assert journal_mode == "WAL", f"Expected WAL mode, got {journal_mode}"

        # Verify tables exist
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        assert "project_proposals" in tables
        assert "project_bom_items" in tables
        assert "project_milestones" in tables
        assert "innovation_ideas" in tables

        # Verify curated ideas are seeded
        cur = conn.execute("SELECT COUNT(*) FROM innovation_ideas;")
        count = cur.fetchone()[0]
        assert count >= len(INNOVATION_IDEAS_CATALOG)
    finally:
        conn.close()


def test_get_overview_metrics(test_engine):
    """Tests project overview aggregation, milestone progress, and budget metrics."""
    overview = test_engine.get_overview(DEFAULT_STUDENT_ID)
    assert overview["status"] == "SUCCESS"
    assert overview["student_id"] == DEFAULT_STUDENT_ID
    assert "metrics" in overview

    metrics = overview["metrics"]
    assert metrics["total_proposals"] >= 1
    assert metrics["approved_proposals"] >= 1
    assert metrics["total_milestones"] >= 4
    assert metrics["total_bom_expenditure_inr"] > 0
    assert metrics["curated_ideas_count"] >= 6
    assert 0.0 <= metrics["overall_progress_percent"] <= 100.0


def test_bom_cost_estimator_calculations(test_engine):
    """Validates bill of materials calculations: subtotals, GST, contingency, and categories."""
    items = [
        {"component_name": "ESP32 DevKit", "category": "MCU", "quantity": 2, "unit_price_inr": 350.0, "vendor": "Robu.in"},
        {"component_name": "BME280 Sensor", "category": "SENSOR", "quantity": 1, "unit_price_inr": 380.0, "vendor": "Robocraze"},
        {"component_name": "SX1278 LoRa", "category": "COMMUNICATION", "quantity": 1, "unit_price_inr": 550.0, "vendor": "Robu.in"}
    ]

    # Subtotal = (2*350) + 380 + 550 = 700 + 380 + 550 = 1630.0
    # GST (18%) = 1630 * 0.18 = 293.4
    # Contingency (10%) = 1630 * 0.10 = 163.0
    # Total = 1630 + 293.4 + 163.0 = 2086.4

    bom = test_engine.calculate_bom(items, tax_buffer_percent=18.0, contingency_percent=10.0)
    assert bom["status"] == "SUCCESS"
    assert bom["items_count"] == 3
    assert bom["subtotal_inr"] == 1630.0
    assert bom["gst_tax_inr"] == 293.4
    assert bom["contingency_inr"] == 163.0
    assert bom["total_estimated_budget_inr"] == 2086.4

    # Category breakdown verification
    cats = bom["category_breakdown"]
    assert cats["MCU"] == 700.0
    assert cats["SENSOR"] == 380.0
    assert cats["COMMUNICATION"] == 550.0

    # Max cost item check
    assert bom["max_cost_item"]["component_name"] == "ESP32 DevKit"
    assert bom["max_cost_item"]["total_cost_inr"] == 700.0

    # Empty items check
    empty_bom = test_engine.calculate_bom([])
    assert empty_bom["subtotal_inr"] == 0.0
    assert empty_bom["total_estimated_budget_inr"] == 0.0


def test_hardware_compatibility_logic_voltage_checks(test_engine):
    """Validates voltage level matching and level-shifter hazard detection."""
    # Case 1: 3.3V ESP32 with 3.3V sensor -> COMPATIBLE
    comp1 = [{"name": "BME280", "logic_voltage": 3.3, "current_ma": 3.6, "interface": "I2C"}]
    res1 = test_engine.check_compatibility("ESP32-WROOM-32", comp1)
    assert res1["verdict"] == "COMPATIBLE"
    assert len(res1["critical_errors"]) == 0

    # Case 2: 3.3V ESP32 with 5.0V HC-SR04 (non-tolerant) -> INCOMPATIBLE
    comp2 = [{"name": "HC-SR04 Ultrasonic", "logic_voltage": 5.0, "current_ma": 15.0, "interface": "GPIO_PULSE"}]
    res2 = test_engine.check_compatibility("ESP32-WROOM-32", comp2)
    assert res2["verdict"] == "INCOMPATIBLE"
    assert any("VOLTAGE INCOMPATIBILITY" in err for err in res2["critical_errors"])

    # Case 3: 5.0V Arduino Uno with strict 3.3V BME280 -> INCOMPATIBLE
    res3 = test_engine.check_compatibility("Arduino Uno R3 (ATmega328P)", comp1)
    assert res3["verdict"] == "INCOMPATIBLE"
    assert any("VOLTAGE HAZARD" in err for err in res3["critical_errors"])

    # Case 4: 3.3V STM32F401 (5V-tolerant pins) with 5.0V sensor -> COMPATIBLE_WITH_CAVEATS
    res4 = test_engine.check_compatibility("STM32F401CCU6 (BlackPill)", comp2)
    assert res4["verdict"] == "COMPATIBLE_WITH_CAVEATS"
    assert any("5V-tolerant input pins" in cav for cav in res4["caveats"])


def test_hardware_compatibility_power_budget_checks(test_engine):
    """Validates total current draw against microcontroller LDO limits."""
    # Normal load: 20mA total on 300mA RP2040 -> Safe
    safe_comps = [
        {"name": "OLED Display", "logic_voltage": 3.3, "current_ma": 20.0, "interface": "I2C"}
    ]
    safe_res = test_engine.check_compatibility("Raspberry Pi Pico (RP2040)", safe_comps)
    assert safe_res["power_budget"]["power_safe"] is True
    assert safe_res["power_budget"]["headroom_ma"] == 280.0

    # Overload: SIM800L (2000mA) on 300mA RP2040 -> INCOMPATIBLE
    overload_comps = [
        {"name": "SIM800L Module", "logic_voltage": 4.0, "current_ma": 2000.0, "interface": "UART"}
    ]
    overload_res = test_engine.check_compatibility("Raspberry Pi Pico (RP2040)", overload_comps)
    assert overload_res["verdict"] == "INCOMPATIBLE"
    assert overload_res["power_budget"]["power_safe"] is False
    assert any("POWER OVERLOAD" in err for err in overload_res["critical_errors"])


def test_hardware_compatibility_i2c_bus_collisions(test_engine):
    """Detects duplicate I2C addresses on the shared bus."""
    comps = [
        {"name": "MPU6050 Primary", "logic_voltage": 3.3, "current_ma": 3.9, "interface": "I2C", "i2c_address": "0x68"},
        {"name": "MPU6050 Secondary", "logic_voltage": 3.3, "current_ma": 3.9, "interface": "I2C", "i2c_address": "0x68"}
    ]
    res = test_engine.check_compatibility("ESP32-WROOM-32", comps)
    assert res["verdict"] == "COMPATIBLE_WITH_CAVEATS"
    assert any("I2C ADDRESS COLLISION" in cav for cav in res["caveats"])


def test_proposal_lifecycle_and_rbac(test_engine):
    """Validates proposal creation, schema integrity, and faculty RBAC approval barriers."""
    proposal_data = {
        "title": "Autonomous Drone with Optical Flow Sensor",
        "domain": "Embedded RTOS & Robotics",
        "abstract": "Quadcopter flight stabilizer using optical flow and LiDAR ranging.",
        "objectives": ["Implement PID flight loop", "Read optical flow at 50Hz"],
        "hardware_stack": ["STM32F401", "PMW3901 Optical Flow"],
        "software_stack": ["FreeRTOS", "CMSIS-DSP"]
    }

    create_res = test_engine.create_proposal(proposal_data, actor_role="Student")
    assert create_res["status"] == "SUCCESS"
    pid = create_res["proposal_id"]

    # Student cannot approve proposal
    forbidden_res = test_engine.update_proposal_status(pid, "APPROVED", actor_role="Student")
    assert forbidden_res["status"] == "FORBIDDEN"

    # Faculty mentor / Teacher can approve proposal
    approved_res = test_engine.update_proposal_status(pid, "APPROVED", actor_role="Teacher")
    assert approved_res["status"] == "SUCCESS"
    assert approved_res["new_status"] == "APPROVED"

    # Retrieve proposal detail and verify schema
    detail = test_engine.get_proposal_detail(pid)
    assert detail is not None
    assert detail["title"] == proposal_data["title"]
    assert detail["status"] == "APPROVED"
    assert len(detail["objectives"]) == 2


def test_milestone_tracking_and_deliverables(test_engine):
    """Validates milestone updates, deliverables checkoff, and completion timestamps."""
    milestones = test_engine.get_milestones("PROP_2023MITEC042_01")
    assert len(milestones) >= 4

    target_ms = milestones[0]
    mid = target_ms["milestone_id"]

    # Toggle to IN_PROGRESS
    res_prog = test_engine.update_milestone_status(mid, "IN_PROGRESS")
    assert res_prog["status"] == "SUCCESS"
    assert res_prog["new_status"] == "IN_PROGRESS"
    assert res_prog["completed_at"] is None

    # Toggle to COMPLETED
    res_comp = test_engine.update_milestone_status(mid, "COMPLETED")
    assert res_comp["status"] == "SUCCESS"
    assert res_comp["new_status"] == "COMPLETED"
    assert res_comp["completed_at"] is not None


def test_privacy_invariants_no_credential_leakage():
    """Guarantees zero client-side or repository leakage of private admin credentials."""
    forbidden_tokens = ["ashokkumar2008313@gmail.com", "9597382878"]
    target_files = [
        os.path.join(BASE_DIR, "backend", "project_innovation_engine.py"),
        os.path.join(BASE_DIR, "src", "components", "ProjectInnovationHub.jsx"),
        os.path.join(BASE_DIR, "src", "pages", "project-innovation.astro")
    ]

    for fpath in target_files:
        assert os.path.exists(fpath), f"File {fpath} does not exist"
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            for token in forbidden_tokens:
                assert token not in content, f"SECURITY ALERT: Private token '{token}' leaked in {fpath}"

