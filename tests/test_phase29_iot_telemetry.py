"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 29 (IoT Smart Laboratory & Telemetry Hub)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase29_iot_telemetry.py
Target Facility: Lab 304 (Smart Electronics & IoT Testbed, MIT Campus, Chromepet)
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

from backend.iot_telemetry_engine import (
    IotTelemetryEngine,
    iot_telemetry_engine,
    DEFAULT_STUDENT_ID,
    DEFAULT_TECH_ID,
    DEFAULT_BENCH_NODES,
    BASELINE_ALERTS,
    THRESHOLD_OVER_VOLTAGE_V,
    THRESHOLD_OVER_CURRENT_A,
    THRESHOLD_OVER_TEMP_C
)


@pytest.fixture
def test_engine(tmp_path):
    """Provides an isolated IotTelemetryEngine backed by a temporary SQLite WAL DB."""
    db_file = str(tmp_path / "test_iot_telemetry.db")
    engine = IotTelemetryEngine(db_path=db_file)
    return engine


def test_iot_telemetry_engine_initialization(test_engine):
    """Verifies table creation, SQLite WAL mode, and baseline Lab 304 bench seeding."""
    conn = test_engine._get_connection()
    try:
        cur = conn.execute("PRAGMA journal_mode;")
        journal_mode = cur.fetchone()[0].upper()
        assert journal_mode == "WAL", f"Expected WAL mode, got {journal_mode}"

        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        assert "iot_bench_nodes" in tables
        assert "iot_telemetry_logs" in tables
        assert "iot_threshold_alerts" in tables
        assert "iot_bench_controls" in tables

        cur = conn.execute("SELECT COUNT(*) FROM iot_bench_nodes;")
        assert cur.fetchone()[0] == 8

        cur = conn.execute("SELECT COUNT(*) FROM iot_threshold_alerts;")
        assert cur.fetchone()[0] >= len(BASELINE_ALERTS)
    finally:
        conn.close()


def test_overview_metrics_calculation(test_engine):
    """Validates Lab 304 aggregate indicators, power consumption, and health indices."""
    overview = test_engine.get_overview_metrics()

    assert "health_score" in overview
    assert 0.0 <= overview["health_score"] <= 100.0
    assert overview["total_benches"] == 8
    assert overview["online_benches"] >= 1
    assert overview["total_power_watts"] > 0.0
    assert overview["avg_temp_celsius"] > 0.0
    assert overview["laboratory"] == "MIT Campus - ECE Smart Lab 304"
    assert overview["regulation"] == "ECE Regulation 2023"


def test_telemetry_ingestion_and_power_calculation(test_engine):
    """Validates real-time P = V * I calculation, log recording, and normal status."""
    res = test_engine.ingest_telemetry_packet(
        node_id="NODE_ESP32_BENCH_01",
        voltage_v=12.0,
        current_a=1.5,
        ambient_temp_c=32.0,
        relay_state="CLOSED"
    )
    assert res["status"] == "SUCCESS"
    assert res["power_watts"] == 18.0  # 12.0 * 1.5 = 18.0
    assert res["relay_state"] == "CLOSED"
    assert res["node_status"] == "ONLINE"
    assert res["alerts_triggered_count"] == 0

    # Verify history has recorded the sample
    history = test_engine.get_telemetry_history(bench_id="BENCH_304_01", limit=5)
    assert len(history) > 0
    latest = history[-1]
    assert latest["voltage_v"] == 12.0
    assert latest["power_w"] == 18.0


def test_over_voltage_safety_cutoff_alert(test_engine):
    """Validates over-voltage threshold detection and automatic relay tripping."""
    # Voltage 26.5V exceeds 25.0V ceiling
    res = test_engine.ingest_telemetry_packet(
        node_id="NODE_ESP32_BENCH_02",
        voltage_v=26.5,
        current_a=1.2,
        ambient_temp_c=33.0
    )
    assert res["status"] == "SUCCESS"
    assert res["alerts_triggered_count"] >= 1
    assert res["relay_state"] == "OPEN"  # Auto-tripped
    assert res["node_status"] == "ALERT"

    # Verify alert logged in table
    alerts = test_engine.get_threshold_alerts(status="ACTIVE")
    ov_alerts = [a for a in alerts if a["alert_type"] == "OVER_VOLTAGE"]
    assert len(ov_alerts) >= 1
    assert ov_alerts[0]["severity"] == "CRITICAL"


def test_over_current_safety_cutoff_alert(test_engine):
    """Validates over-current threshold detection and automated circuit breaker trip."""
    # Current 3.8A exceeds 3.0A limit
    res = test_engine.ingest_telemetry_packet(
        node_id="NODE_ESP32_BENCH_03",
        voltage_v=15.0,
        current_a=3.8,
        ambient_temp_c=34.0
    )
    assert res["status"] == "SUCCESS"
    assert res["alerts_triggered_count"] >= 1
    assert res["relay_state"] == "OPEN"  # Auto-tripped
    assert res["node_status"] == "ALERT"


def test_over_temperature_safety_cutoff_alert(test_engine):
    """Validates heatsink over-temperature safety shutdown (> 65.0°C)."""
    # Temp 72.5°C exceeds 65.0°C threshold
    res = test_engine.ingest_telemetry_packet(
        node_id="NODE_ESP32_BENCH_05",
        voltage_v=3.3,
        current_a=0.5,
        ambient_temp_c=72.5
    )
    assert res["status"] == "SUCCESS"
    assert res["alerts_triggered_count"] >= 1
    assert res["relay_state"] == "OPEN"  # Auto-tripped
    assert res["node_status"] == "ALERT"


def test_bench_relay_control_and_rbac(test_engine):
    """Validates high-voltage relay command execution and strict RBAC barriers."""
    # Student role cannot toggle relays
    forbidden = test_engine.toggle_bench_relay(
        bench_id="BENCH_304_01",
        target_state="OPEN",
        actor_id=DEFAULT_STUDENT_ID,
        actor_role="Student"
    )
    assert forbidden["status"] == "FORBIDDEN"
    assert "unauthorized" in forbidden["message"].lower()

    # Admin role can toggle relay
    allowed = test_engine.toggle_bench_relay(
        bench_id="BENCH_304_01",
        target_state="OPEN",
        actor_id=DEFAULT_TECH_ID,
        actor_role="Admin"
    )
    assert allowed["status"] == "SUCCESS"
    assert allowed["relay_state"] == "OPEN"

    # Reset relay back to CLOSED
    reset = test_engine.toggle_bench_relay(
        bench_id="BENCH_304_01",
        target_state="CLOSED",
        actor_id=DEFAULT_TECH_ID,
        actor_role="Staff"
    )
    assert reset["status"] == "SUCCESS"
    assert reset["relay_state"] == "CLOSED"


def test_alert_acknowledgement_and_rbac(test_engine):
    """Validates threshold alert resolution and technician RBAC boundaries."""
    alerts = test_engine.get_threshold_alerts(status="ACTIVE")
    assert len(alerts) > 0
    target_alert = alerts[0]["alert_id"]

    # Student cannot resolve safety alerts
    forbidden = test_engine.acknowledge_alert(
        alert_id=target_alert,
        notes="Student trying to clear",
        actor_role="Student"
    )
    assert forbidden["status"] == "FORBIDDEN"

    # Technician resolves alert
    resolved = test_engine.acknowledge_alert(
        alert_id=target_alert,
        notes="Load calibrated and heatsink fan verified.",
        actor_role="Lab_Technician"
    )
    assert resolved["status"] == "SUCCESS"
    assert resolved["alert_id"] == target_alert


def test_privacy_invariants_no_credential_leakage():
    """Security audit: Ensures strictly zero exposure of private phone numbers or admin emails."""
    forbidden_tokens = [
        "ashokkumar2008313@gmail.com",
        "9597382878"
    ]
    target_files = [
        os.path.join(BASE_DIR, "backend", "iot_telemetry_engine.py"),
        os.path.join(BASE_DIR, "src", "components", "IotTelemetryHub.jsx"),
        os.path.join(BASE_DIR, "src", "pages", "iot-lab.astro")
    ]

    for fpath in target_files:
        assert os.path.exists(fpath), f"File {fpath} does not exist"
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            for token in forbidden_tokens:
                assert token not in content, f"SECURITY ALERT: Private token '{token}' leaked in {fpath}"

