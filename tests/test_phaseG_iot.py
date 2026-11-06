"""
========================================================================================
VoltCore Apex Academia - Unit Tests for Phase G: IoT & Connected Systems (Features 271–280)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
========================================================================================
"""

import os
import pytest
import tempfile
from backend.iot_connected_systems_engine import IoTConnectedSystemsEngine, IOT_ARCHITECTURE_TIERS


@pytest.fixture
def engine():
    """Provides a fresh isolated instance of IoTConnectedSystemsEngine with temporary SQLite DB."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_iot_telemetry.db")
    eng = IoTConnectedSystemsEngine(db_path=db_path)
    yield eng


# =========================================================================
# Feature 271: Architecture Tiers
# =========================================================================
def test_architecture_tiers(engine):
    tiers = engine.get_architecture_tiers()
    assert len(tiers) == 5
    tier_names = [t["name"] for t in tiers]
    assert "Perception Layer" in tier_names
    assert "Edge / Gateway Layer" in tier_names
    assert "Network & Transport Layer" in tier_names
    assert "Middleware & Cloud Broker Layer" in tier_names
    assert "Application & Business Layer" in tier_names


# =========================================================================
# Feature 272: MQTT Message Structure & Handshake
# =========================================================================
def test_mqtt_packet_parsing(engine):
    # QoS 1 Publish Packet
    res = engine.parse_mqtt_packet(
        packet_type="PUBLISH",
        topic="voltcore/mit/ece/lab304/temperature",
        qos=1,
        retain=0,
        payload_data={"temp": 28.5},
        packet_id=1042
    )
    assert res["packet_type"] == "PUBLISH"
    assert res["qos"] == 1
    # Byte 1 for PUBLISH QoS 1: (3 << 4) | (0 << 3) | (1 << 1) | 0 = 0x32
    assert res["fixed_header_hex"] == "0x32"
    assert res["packet_size_bytes"] > 0
    assert len(res["handshake_steps"]) == 2  # PUBLISH -> PUBACK

    # QoS 2 Handshake (4-way)
    res_qos2 = engine.parse_mqtt_packet(packet_type="PUBLISH", qos=2)
    assert len(res_qos2["handshake_steps"]) == 4


# =========================================================================
# Feature 273: Sensor Telemetry & Anomaly Detection
# =========================================================================
def test_sensor_telemetry_analysis(engine):
    # Normal temperature readings with one extreme outlier
    samples = [25.1, 25.3, 25.0, 25.2, 25.4, 25.1, 25.2, 95.0, 25.3, 25.1]
    res = engine.analyze_sensor_telemetry(samples, metric_name="Temperature", upper_limit=45.0)
    assert res["sample_count"] == 10
    assert res["anomaly_count"] >= 1
    # 95.0 should trigger an anomaly
    anomaly_indices = [a["sample_index"] for a in res["anomalies"]]
    assert 7 in anomaly_indices

    # Empty sample edge case
    empty_res = engine.analyze_sensor_telemetry([])
    assert "error" in empty_res


# =========================================================================
# Feature 274: IoT Device Registry
# =========================================================================
def test_device_registry_crud(engine):
    # Initial seeded devices
    devices = engine.list_devices()
    assert len(devices) >= 4

    # Register new node
    dev_id = engine.register_device(
        node_id="NODE-TEST-99",
        name="Test Sensor Gateway",
        platform="ESP32-S3",
        mac_address="AA:BB:CC:DD:EE:FF",
        ip_address="192.168.1.199",
        status="ONLINE",
        battery_percent=95
    )
    assert dev_id > 0

    node = engine.get_device("NODE-TEST-99")
    assert node is not None
    assert node["name"] == "Test Sensor Gateway"
    assert node["platform"] == "ESP32-S3"


# =========================================================================
# Feature 275: Virtual Sensor Calibration Tool
# =========================================================================
def test_sensor_calibration(engine):
    # 2-point calibration:
    # Raw 0.0V -> 0.0 °C, Raw 3.3V -> 100.0 °C (Slope = 100/3.3 = 30.303)
    cal = engine.calibrate_sensor_reading(
        raw_val=1.65,
        p1_raw=0.0,
        p1_ref=0.0,
        p2_raw=3.3,
        p2_ref=100.0,
        ambient_temp_c=25.0,
        temp_coeff_per_deg_c=0.0
    )
    assert cal["calibrated_linear"] == pytest.approx(50.0, abs=0.1)

    # With temperature compensation: Ambient 35°C vs Ref 25°C (+10 deg)
    cal_temp = engine.calibrate_sensor_reading(
        raw_val=1.65,
        p1_raw=0.0,
        p1_ref=0.0,
        p2_raw=3.3,
        p2_ref=100.0,
        ambient_temp_c=35.0,
        temp_coeff_per_deg_c=0.002
    )
    assert cal_temp["calibrated_final"] < 50.0  # Temperature derating factor applied

    with pytest.raises(ValueError):
        engine.calibrate_sensor_reading(raw_val=1.0, p1_raw=2.0, p1_ref=10.0, p2_raw=2.0, p2_ref=20.0)


# =========================================================================
# Feature 276: MQTT Topic Structure & Wildcard Matcher
# =========================================================================
def test_mqtt_topic_matching(engine):
    # Single-level wildcard '+'
    res1 = engine.match_mqtt_topic(
        filter_pattern="voltcore/mit/+/lab304/temperature",
        topic="voltcore/mit/ece/lab304/temperature"
    )
    assert res1["is_matched"] is True

    # Multi-level wildcard '#'
    res2 = engine.match_mqtt_topic(
        filter_pattern="voltcore/mit/#",
        topic="voltcore/mit/ece/lab304/node01/telemetry/temp"
    )
    assert res2["is_matched"] is True

    # Non-matching topic
    res3 = engine.match_mqtt_topic(
        filter_pattern="voltcore/mit/cs/#",
        topic="voltcore/mit/ece/lab304/node01"
    )
    assert res3["is_matched"] is False


# =========================================================================
# Feature 277: IoT Packet History Ledger
# =========================================================================
def test_packet_history_ledger(engine):
    pkt_id = engine.record_packet(
        node_id="NODE-MIT-LAB304-01",
        topic="voltcore/mit/telemetry",
        packet_type="PUBLISH",
        qos=1,
        payload={"lux": 420.0},
        rssi_dbm=-60.0,
        snr_db=10.5
    )
    assert pkt_id > 0

    history = engine.get_packet_history(limit=5)
    assert len(history) >= 1
    assert any(p["topic"] == "voltcore/mit/telemetry" for p in history)


# =========================================================================
# Feature 278: Device Status Timeline
# =========================================================================
def test_device_timeline(engine):
    timeline = engine.generate_device_timeline("NODE-MIT-LAB304-01")
    assert len(timeline) >= 5
    states = [e["state"] for e in timeline]
    assert "POWER_ON" in states
    assert "WIFI_CONNECTED" in states
    assert "MQTT_CONNECTED" in states


# =========================================================================
# Feature 279: Smart Automation Rule Engine
# =========================================================================
def test_automation_rule_evaluation(engine):
    # Temperature 36°C > Threshold 30°C -> Should Trigger
    rule_res = engine.evaluate_automation_rule(
        rule_name="Cooling Fan Trigger",
        metric="temperature",
        operator=">",
        threshold=30.0,
        current_val=36.5,
        action_type="RELAY_FAN_ON",
        target_device="NODE-MIT-SMART-04"
    )
    assert rule_res["is_triggered"] is True
    assert rule_res["action_payload"]["action"] == "RELAY_FAN_ON"

    # Temperature 28°C > Threshold 30°C -> Should NOT Trigger
    rule_no_trig = engine.evaluate_automation_rule(
        rule_name="Cooling Fan Trigger",
        metric="temperature",
        operator=">",
        threshold=30.0,
        current_val=28.0
    )
    assert rule_no_trig["is_triggered"] is False

    # Save rule to SQLite WAL
    saved_id = engine.save_automation_rule(
        student_id="2023MITEC042",
        rule_name="Air Quality Vent",
        metric="aqi",
        operator=">",
        threshold=150.0,
        action_type="VENT_EXHAUST",
        target_device="NODE-MIT-SMART-04"
    )
    assert saved_id > 0
    rules = engine.get_automation_rules("2023MITEC042")
    assert len(rules) >= 1


# =========================================================================
# Feature 280: RF Link Budget & Path Loss
# =========================================================================
def test_rf_link_budget(engine):
    # 2.4 GHz Wi-Fi over 50 meters
    res = engine.calculate_rf_link_budget(
        distance_meters=50.0,
        freq_mhz=2400.0,
        tx_power_dbm=14.0,
        tx_antenna_gain_dbi=2.0,
        rx_antenna_gain_dbi=2.0,
        rx_sensitivity_dbm=-95.0
    )
    assert res["fspl_db"] > 60.0
    assert res["rssi_dbm"] < 0.0
    assert res["is_link_viable"] is True
    assert res["link_margin_db"] > 10.0

    with pytest.raises(ValueError):
        engine.calculate_rf_link_budget(distance_meters=-5.0)


def test_mqtt_retain_and_multibyte_length(engine):
    # Large payload testing remaining length encoding
    large_payload = {"data": "X" * 300}
    res = engine.parse_mqtt_packet(
        packet_type="PUBLISH",
        topic="voltcore/mit/large",
        qos=0,
        retain=1,
        payload_data=large_payload
    )
    assert res["retain"] == 1
    assert res["remaining_length"] > 128  # Triggers multi-byte remaining length
    assert res["packet_size_bytes"] > 300


def test_anomaly_flatline_series(engine):
    # Flatline values (std dev == 0)
    flat_samples = [25.0, 25.0, 25.0, 25.0]
    res = engine.analyze_sensor_telemetry(flat_samples, metric_name="StableTemp")
    assert res["std_dev"] == 0.0
    assert res["anomaly_count"] == 0

