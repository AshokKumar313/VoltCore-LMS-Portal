"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 32 (IoT Sensor Telemetry Simulator)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase32_iot_sensor_simulator.py
Target Facility: Lab 304 (Hardware Prototyping & Real-Time Embedded Systems Lab)
Regulation: Anna University ECE Regulation 2023
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import csv
import io
import pytest
from backend.iot_sensor_simulator_engine import IoTSensorSimulatorEngine


@pytest.fixture
def test_engine(tmp_path):
    """Provides an isolated IoTSensorSimulatorEngine backed by a temporary SQLite WAL DB."""
    db_file = str(tmp_path / "test_sensor_sim.db")
    engine = IoTSensorSimulatorEngine(db_path=db_file)
    return engine


def test_engine_initialization_and_wal(test_engine):
    """Verifies SQLite tables and WAL journal mode for lightweight, thread-safe telemetry."""
    conn = test_engine._get_connection()
    try:
        cur = conn.execute("PRAGMA journal_mode;")
        journal_mode = cur.fetchone()[0].upper()
        assert journal_mode == "WAL", f"Expected WAL mode, got {journal_mode}"

        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        assert "iot_simulated_telemetry_readings" in tables
        assert "iot_simulated_sessions" in tables
    finally:
        conn.close()


def test_generate_simulated_reading_single(test_engine):
    """Verifies single-packet on-demand simulation with deterministic bounds and CRC16."""
    reading = test_engine.generate_simulated_reading(
        node_id="ESP32_LAB304_DHT22_IR",
        student_id="2023MITEC042",
        baseline_temp_c=26.5,
        baseline_humidity_pct=55.0
    )
    assert reading["status"] == "SUCCESS"
    assert "reading_id" in reading
    assert reading["node_id"] == "ESP32_LAB304_DHT22_IR"
    assert reading["student_id"] == "2023MITEC042"
    assert 20.0 <= reading["temperature_c"] <= 35.0
    assert 40.0 <= reading["humidity_pct"] <= 70.0
    assert reading["ir_proximity_count"] >= 0
    assert reading["checksum"].startswith("0x")
    assert reading["bus_voltage_v"] >= 3.20


def test_generate_simulated_reading_threshold_alert(test_engine):
    """Verifies automated status tagging for temperature and humidity threshold breaches."""
    # 1. High temperature alert (> 35°C)
    r_temp = test_engine.generate_simulated_reading(
        baseline_temp_c=38.0,
        baseline_humidity_pct=45.0
    )
    assert r_temp["telemetry_status"] == "HIGH_TEMP_ALERT"
    assert any("Temperature threshold exceeded" in a for a in r_temp["metadata"]["alerts"])

    # 2. High humidity alert (>= 75% RH)
    r_hum = test_engine.generate_simulated_reading(
        baseline_temp_c=25.0,
        baseline_humidity_pct=82.0
    )
    assert r_hum["telemetry_status"] == "HIGH_HUMIDITY_ALERT"
    assert any("High Relative Humidity" in a for a in r_hum["metadata"]["alerts"])


def test_generate_simulated_reading_forced_ir(test_engine):
    """Verifies forced optical obstacle trigger incrementing IR count."""
    r1 = test_engine.generate_simulated_reading(current_ir_count=20, trigger_ir_event=True)
    assert r1["ir_delta"] == 1
    assert r1["ir_proximity_count"] == 21
    assert r1["telemetry_status"] == "OBSTACLE_DETECTED"


def test_generate_burst_readings(test_engine):
    """Verifies synchronous 5-packet burst generation without background threads."""
    burst = test_engine.generate_burst_readings(
        count=5,
        node_id="ESP32_LAB304_DHT22_IR",
        student_id="2023MITEC042"
    )
    assert len(burst) == 5
    # Verify non-decreasing cumulative count
    ir_counts = [b["ir_proximity_count"] for b in burst]
    for i in range(len(ir_counts) - 1):
        assert ir_counts[i] <= ir_counts[i + 1]


def test_ingest_custom_reading_valid(test_engine):
    """Verifies direct ingestion of validated custom sensor packets."""
    payload = {
        "node_id": "ARDUINO_NANO_BLE_SENSE",
        "temperature_c": 24.2,
        "humidity_pct": 52.0,
        "ir_proximity_count": 8,
        "rssi_dbm": -55,
        "bus_voltage_v": 3.31,
        "status": "NORMAL"
    }
    res = test_engine.ingest_custom_reading(payload, student_id="2023MITEC042")
    assert res["status"] == "SUCCESS"
    assert res["node_id"] == "ARDUINO_NANO_BLE_SENSE"
    assert res["temperature_c"] == 24.2


def test_ingest_custom_reading_bounds_validation(test_engine):
    """Ensures packets with out-of-physical-range metrics are rejected."""
    # Impossible temperature (> 125°C)
    res1 = test_engine.ingest_custom_reading({"temperature_c": 190.0})
    assert res1["status"] == "ERROR"
    assert "Temperature out of sensor physical bounds" in res1["message"]

    # Impossible humidity (> 100%)
    res2 = test_engine.ingest_custom_reading({"temperature_c": 25.0, "humidity_pct": 115.0})
    assert res2["status"] == "ERROR"
    assert "Humidity out of bounds" in res2["message"]


def test_get_telemetry_readings_pagination(test_engine):
    """Validates ordered retrieval and pagination of simulated readings."""
    for i in range(8):
        test_engine.generate_simulated_reading()

    all_readings = test_engine.get_telemetry_readings(limit=10)
    assert len(all_readings) == 8

    # Pagination test
    page1 = test_engine.get_telemetry_readings(limit=4, offset=0)
    page2 = test_engine.get_telemetry_readings(limit=4, offset=4)
    assert len(page1) == 4
    assert len(page2) == 4
    assert page1[0]["reading_id"] != page2[0]["reading_id"]


def test_get_telemetry_statistics(test_engine):
    """Verifies calculation of instantaneous summary statistics."""
    test_engine.generate_simulated_reading(baseline_temp_c=20.0, baseline_humidity_pct=40.0)
    test_engine.generate_simulated_reading(baseline_temp_c=30.0, baseline_humidity_pct=60.0)

    stats = test_engine.get_telemetry_statistics()
    assert stats["total_packets"] == 2
    assert stats["temperature"]["min"] <= 23.0
    assert stats["temperature"]["max"] >= 28.0
    assert 18.0 <= stats["temperature"]["avg"] <= 32.0


def test_export_telemetry_csv(test_engine):
    """Verifies compliant RFC-4180 CSV export generation with expected column headers."""
    test_engine.generate_simulated_reading()
    test_engine.generate_simulated_reading()

    csv_data = test_engine.export_telemetry_csv(limit=10)
    reader = csv.reader(io.StringIO(csv_data))
    rows = list(reader)

    assert len(rows) == 3  # 1 header row + 2 data rows
    headers = rows[0]
    assert "reading_id" in headers
    assert "temperature_c" in headers
    assert "humidity_pct" in headers
    assert "ir_proximity_count" in headers
    assert "checksum" in headers


def test_clear_simulated_readings(test_engine):
    """Ensures buffer purge method removes all records."""
    test_engine.generate_simulated_reading()
    test_engine.generate_simulated_reading()
    assert len(test_engine.get_telemetry_readings()) == 2

    res = test_engine.clear_simulated_readings()
    assert res["status"] == "SUCCESS"
    assert len(test_engine.get_telemetry_readings()) == 0


def test_privacy_invariants_and_author_attribution():
    """Enforces absolute protection of private contact info and verifies public author identity."""
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    engine_path = os.path.join(workspace_root, "backend", "iot_sensor_simulator_engine.py")
    component_path = os.path.join(workspace_root, "src", "components", "IoTSensorSimulatorHub.jsx")

    with open(engine_path, "r", encoding="utf-8") as f:
        engine_str = f.read()

    with open(component_path, "r", encoding="utf-8") as f:
        comp_str = f.read()

    # STRICT INVARIANTS:
    # 1. Private credentials must NEVER leak into source code
    assert "ashokkumar2008313@gmail.com" not in engine_str
    assert "ashokkumar2008313@gmail.com" not in comp_str
    assert "9597382878" not in engine_str
    assert "9597382878" not in comp_str

    # 2. Public author attribution
    assert "Ashok Kumar A" in engine_str
    assert "2023MITEC042" in engine_str
    assert "2023MITEC042" in comp_str
