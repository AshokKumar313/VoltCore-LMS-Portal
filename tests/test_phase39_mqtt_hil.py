"""
========================================================================================
VoltCore Apex Academia - Phase 39 Test Suite
Module: Cloud IoT MQTT Broker & WebSerial / WebUSB HIL Engine Tests
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
========================================================================================
"""

import os
import sqlite3
import pytest
from backend.mqtt_hil_engine import (
    MqttHilEngine,
    HIL_DEVICE_TARGETS,
    calculate_crc16_ccitt,
    mqtt_hil_engine
)


def test_wal_initialization_and_schema(tmp_path):
    """Verifies SQLite tables and WAL mode are initialized correctly."""
    db_file = str(tmp_path / "test_mqtt_hil_init.db")
    engine = MqttHilEngine(db_path=db_file)
    conn = engine._get_connection()
    cursor = conn.cursor()

    # Verify journal mode is WAL
    journal_mode = cursor.execute("PRAGMA journal_mode;").fetchone()[0]
    assert journal_mode.upper() == "WAL"

    # Verify tables exist
    tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    assert "mqtt_hil_sessions" in tables
    assert "mqtt_hil_packets" in tables
    conn.close()


def test_available_devices_catalog(tmp_path):
    """Verifies microcontroller target catalog and hardware specifications."""
    db_file = str(tmp_path / "test_mqtt_hil_devices.db")
    engine = MqttHilEngine(db_path=db_file)
    devices = engine.get_available_devices()

    assert len(devices) == 4
    keys = [d["key"] for d in devices]
    assert "ESP32_WROOM_32" in keys
    assert "UNO_R4_WIFI" in keys
    assert "RP2040_PICO_W" in keys
    assert "NUCLEO_F401RE" in keys

    esp32 = next(d for d in devices if d["key"] == "ESP32_WROOM_32")
    assert "WebSerial" in esp32["interfaces"][0]
    assert esp32["base_latency_ms"] > 0
    assert esp32["default_baud"] == 115200


def test_simulate_hil_stream_execution(tmp_path):
    """Verifies deterministic telemetry streaming, packet frame sequence, and CRC16 validation."""
    db_file = str(tmp_path / "test_mqtt_hil_stream.db")
    engine = MqttHilEngine(db_path=db_file)

    res = engine.simulate_hil_stream(
        device_id="ESP32_WROOM_32",
        transport_mode="WEBSERIAL",
        baud_rate=115200,
        qos_level=1,
        num_packets=15,
        student_id="2023MITEC042"
    )

    assert res["status"] == "SUCCESS"
    assert res["summary"]["packets_transmitted"] == 15
    assert len(res["packets"]) == 15
    assert res["packets"][0]["seq_num"] == 1
    assert res["packets"][-1]["seq_num"] == 15

    # Check payload and CRC validity
    for pkt in res["packets"]:
        assert pkt["crc_valid"] == 1
        assert "0x" in pkt["crc16_hex"]
        assert "voltcore/mit/ece/lab304" in pkt["topic"]


def test_rfc3550_jitter_calculation(tmp_path):
    """Verifies RFC 3550 inter-arrival jitter smoothing formula."""
    db_file = str(tmp_path / "test_mqtt_hil_jitter.db")
    engine = MqttHilEngine(db_path=db_file)

    res = engine.simulate_hil_stream(
        device_id="NUCLEO_F401RE",
        transport_mode="WEBUSB",
        num_packets=25
    )

    jitters = [p["jitter_ms"] for p in res["packets"]]
    assert all(j > 0 for j in jitters)
    assert res["summary"]["avg_jitter_ms"] > 0
    # Jitter for STM32 Nucleo over WebUSB should be sub-5ms
    assert res["summary"]["avg_jitter_ms"] < 6.0


def test_packet_loss_and_qos_delivery(tmp_path):
    """Verifies packet delivery guarantees across QoS 0 vs QoS 1/2."""
    db_file = str(tmp_path / "test_mqtt_hil_qos.db")
    engine = MqttHilEngine(db_path=db_file)

    # QoS 0 (Fire-and-forget: sequence 13 dropped)
    res_qos0 = engine.simulate_hil_stream(
        device_id="ESP32_WROOM_32",
        qos_level=0,
        num_packets=20
    )
    assert res_qos0["summary"]["packet_loss_pct"] > 0.0
    dropped_pkt = next(p for p in res_qos0["packets"] if p["seq_num"] == 13)
    assert dropped_pkt["status"] == "DROPPED"

    # QoS 1 (Guaranteed delivery: sequence 13 retried & acknowledged)
    res_qos1 = engine.simulate_hil_stream(
        device_id="ESP32_WROOM_32",
        qos_level=1,
        num_packets=20
    )
    assert res_qos1["summary"]["packet_loss_pct"] == 0.0
    retried_pkt = next(p for p in res_qos1["packets"] if p["seq_num"] == 13)
    assert retried_pkt["status"] == "RETRIED_ACK"


def test_publish_mqtt_message(tmp_path):
    """Verifies discrete MQTT Pub/Sub command handling and database logging."""
    db_file = str(tmp_path / "test_mqtt_hil_pub.db")
    engine = MqttHilEngine(db_path=db_file)

    cmd_payload = {"cmd": "GPIO_WRITE", "pin": 2, "state": 1}
    res = engine.publish_mqtt_message(
        device_id="RP2040_PICO_W",
        topic="voltcore/mit/ece/lab304/pico_01/command",
        payload=cmd_payload,
        qos_level=2,
        student_id="2023MITEC042"
    )

    assert res["status"] == "DELIVERED"
    assert res["topic"] == "voltcore/mit/ece/lab304/pico_01/command"
    assert res["qos_level"] == 2
    assert "0x" in res["crc16_hex"]

    logs = engine.get_packet_logs(session_id=res["session_id"])
    assert len(logs) == 1
    assert logs[0]["topic"] == "voltcore/mit/ece/lab304/pico_01/command"


def test_session_history_and_csv_export(tmp_path):
    """Verifies SQLite persistence and RFC-4180 CSV export."""
    db_file = str(tmp_path / "test_mqtt_hil_csv.db")
    engine = MqttHilEngine(db_path=db_file)

    s1 = engine.simulate_hil_stream(device_id="ESP32_WROOM_32", num_packets=10)
    s2 = engine.simulate_hil_stream(device_id="UNO_R4_WIFI", num_packets=10)

    history = engine.get_session_history(limit=5)
    assert len(history) == 2

    csv_data = engine.export_session_csv(session_id=s1["session_id"])
    assert "Packet_ID,Session_ID,Seq_Num,Topic" in csv_data
    lines = [line.strip() for line in csv_data.strip().split("\n") if line.strip()]
    assert len(lines) == 11  # Header + 10 packet rows


def test_privacy_invariants_and_attribution():
    """Strictly verifies zero leakage of private credentials and confirms public author attribution."""
    with open("backend/mqtt_hil_engine.py", "r", encoding="utf-8") as f:
        code_str = f.read()

    # Zero leakage
    assert "9597382878" not in code_str
    assert "ashokkumar2008313@gmail.com" not in code_str

    # Public attribution
    assert "Ashok Kumar A" in code_str
    assert "2023MITEC042" in code_str
    assert "Anna University" in code_str
