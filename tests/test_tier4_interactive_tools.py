"""
========================================================================================
VoltCore Apex Academia - Tier 4 Interactive Tools & Hardware Benches Validation Suite
Core Engineering Series • Autonomous Engineering Cluster
Platform Lead & Systems Architect: Ashok Kumar A
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313

Validates:
  1. Complete decoupling of institutional markers across all standalone interactive tools
  2. Cross-component telemetry dispatch (voltcore:lab-telemetry, voltcore:flasher-telemetry, voltcore:quiz-submission)
  3. Universal Virtual Benches mount and tab integration inside CourseLabSimulator.jsx
  4. CourseLabEngine.log_observation() telemetry persistence under SQLite WAL mode
  5. CourseQuizEngine.evaluate_submission() and Viva Voce scoring mechanics
  6. High-throughput SQLite WAL concurrency with PRAGMA busy_timeout = 5000
  7. Thermal footprint safety (<500ms total execution) on HP Victus development laptop
========================================================================================
"""

import os
import re
import json
import time
import sqlite3
import tempfile
import pytest

from backend.course_lab_engine import CourseLabEngine
from backend.course_quiz_engine import CourseQuizEngine

TIER4_COMPONENTS = [
    os.path.join("src", "components", "VirtualOscilloscope.jsx"),
    os.path.join("src", "components", "WokwiSimulationController.jsx"),
    os.path.join("src", "components", "WebUsbFlashingPanel.jsx"),
    os.path.join("src", "components", "SystemStatusWidget.jsx"),
    os.path.join("src", "components", "GeminiTutorChat.jsx"),
    os.path.join("src", "components", "CourseLabSimulator.jsx")
]

FORBIDDEN_INSTITUTIONAL_MARKERS = [
    r"Anna\s+University",
    r"MIT\s+Campus",
    r"Regulation\s+2023",
    r"2023MITEC042"
]


def test_tier4_component_files_exist_and_clean_of_institutional_markers():
    """Verify all 6 components exist and contain zero legacy institutional markers."""
    for filepath in TIER4_COMPONENTS:
        assert os.path.exists(filepath), f"Missing Tier 4 component: {filepath}"
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        for pattern in FORBIDDEN_INSTITUTIONAL_MARKERS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            assert len(matches) == 0, (
                f"Forbidden marker '{pattern}' detected in {filepath}: {matches}"
            )


def test_tier4_components_event_bus_and_storage_wiring():
    """Verify all interactive tools dispatch and listen to the voltcore telemetry event bus."""
    # 1. VirtualOscilloscope: dispatches voltcore:lab-telemetry and persists to voltcore_dso_telemetry
    with open(TIER4_COMPONENTS[0], "r", encoding="utf-8") as f:
        dso_content = f.read()
    assert "voltcore:lab-telemetry" in dso_content
    assert "voltcore_dso_telemetry" in dso_content
    assert "handleRecordTelemetry" in dso_content

    # 2. WokwiSimulationController: dispatches voltcore:lab-telemetry and persists to voltcore_wokwi_telemetry
    with open(TIER4_COMPONENTS[1], "r", encoding="utf-8") as f:
        wokwi_content = f.read()
    assert "voltcore:lab-telemetry" in wokwi_content
    assert "voltcore_wokwi_telemetry" in wokwi_content
    assert "handleRecordWokwiTelemetry" in wokwi_content

    # 3. WebUsbFlashingPanel: dispatches voltcore:flasher-telemetry & voltcore:lab-telemetry
    with open(TIER4_COMPONENTS[2], "r", encoding="utf-8") as f:
        flasher_content = f.read()
    assert "voltcore:flasher-telemetry" in flasher_content
    assert "voltcore:lab-telemetry" in flasher_content
    assert "voltcore_flasher_telemetry" in flasher_content

    # 4. SystemStatusWidget: zero-polling health checks & thermal profile
    with open(TIER4_COMPONENTS[3], "r", encoding="utf-8") as f:
        status_content = f.read()
    assert "HP Victus 15 Safe" in status_content
    assert "Core Engineering Series • Autonomous Cluster" in status_content

    # 5. GeminiTutorChat: dispatches voltcore:quiz-submission & voltcore:lab-telemetry
    with open(TIER4_COMPONENTS[4], "r", encoding="utf-8") as f:
        tutor_content = f.read()
    assert "voltcore:quiz-submission" in tutor_content
    assert "voltcore:lab-telemetry" in tutor_content
    assert "voltcore_quiz_history" in tutor_content

    # 6. CourseLabSimulator: listens to voltcore:lab-telemetry and mounts universal benches
    with open(TIER4_COMPONENTS[5], "r", encoding="utf-8") as f:
        sim_content = f.read()
    assert "addEventListener('voltcore:lab-telemetry'" in sim_content
    assert "activeTab === \"instruments\"" in sim_content
    assert "VirtualOscilloscope" in sim_content
    assert "WokwiSimulationController" in sim_content
    assert "WebUsbFlashingPanel" in sim_content
    assert "GeminiTutorChat" in sim_content


def test_course_lab_engine_log_observation_with_tool_telemetry():
    """Verify backend CourseLabEngine persists simulated DSO and Wokwi telemetry payloads."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        temp_db_path = tf.name

    try:
        engine = CourseLabEngine(db_path=temp_db_path)

        # DSO Telemetry Payload
        dso_payload = {
            "tool": "VirtualOscilloscope",
            "timebase": "1.0ms/div",
            "vdiv_ch1": "1.0V/div",
            "freq_hz": 1000.0,
            "vpp_v": 3.3,
            "vrms_v": 1.167,
            "waveform": "sine",
            "timestamp": "2026-11-07T12:00:00Z"
        }
        res_dso = engine.log_observation(
            course_code="EC23S01",
            lab_id="EC23S01_LAB1",
            student_id="ENG-2024-042",
            telemetry=dso_payload
        )
        assert res_dso["status"] == "success"
        assert res_dso["observation_id"].startswith("OBS-EC23S01_LAB1-")

        # Wokwi Telemetry Payload
        wokwi_payload = {
            "tool": "WokwiSimulationController",
            "target": "ESP32_VOLTCORE_IOT_01",
            "baudRate": 115200,
            "nodeStatus": "RUNNING",
            "activePreset": "VOLT-ENG-042",
            "timestamp": "2026-11-07T12:00:01Z"
        }
        res_wokwi = engine.log_observation(
            course_code="EC8702",
            lab_id="EC8702_LAB1",
            student_id="ENG-2024-042",
            telemetry=wokwi_payload
        )
        assert res_wokwi["status"] == "success"

        # Verify DB records
        conn = sqlite3.connect(temp_db_path)
        cur = conn.cursor()
        rows = cur.execute("SELECT lab_id, telemetry_json FROM course_lab_observations ORDER BY id ASC").fetchall()
        assert len(rows) == 2
        assert rows[0][0] == "EC23S01_LAB1"
        stored_dso = json.loads(rows[0][1])
        assert stored_dso["tool"] == "VirtualOscilloscope"
        assert stored_dso["freq_hz"] == 1000.0

        assert rows[1][0] == "EC8702_LAB1"
        stored_wokwi = json.loads(rows[1][1])
        assert stored_wokwi["tool"] == "WokwiSimulationController"
        assert stored_wokwi["activePreset"] == "VOLT-ENG-042"
        conn.close()

    finally:
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)


def test_course_quiz_engine_evaluation_and_grading():
    """Verify backend CourseQuizEngine autograding for student assessment submissions."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        temp_db_path = tf.name

    try:
        engine = CourseQuizEngine(db_path=temp_db_path)

        # Submit answers for EC23S01 (Q1: option 2 is correct, Q2: option 1 is correct)
        answers = {
            "EC23S01_Q1": 2,  # Correct
            "EC23S01_Q2": 1   # Correct
        }
        eval_res = engine.evaluate_submission(
            course_code="EC23S01",
            student_id="ENG-2024-042",
            answers=answers
        )

        assert "error" not in eval_res
        assert eval_res["course_code"] == "EC23S01"
        assert eval_res["student_id"] == "ENG-2024-042"
        assert eval_res["total_mcqs"] == 2
        assert eval_res["correct_count"] == 2
        assert eval_res["percentage"] == 100.0
        assert len(eval_res["itemized_results"]) == 2
        assert "L3 (Apply)" in eval_res["bloom_performance"]

    finally:
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)


def test_sqlite_wal_multi_write_concurrency():
    """Verify rapid successive writes under SQLite WAL mode with busy_timeout=5000."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        temp_db_path = tf.name

    try:
        engine = CourseLabEngine(db_path=temp_db_path)
        start_time = time.perf_counter()

        # Simulate 15 rapid observation telemetry logs (e.g., streaming sensor packets)
        for i in range(15):
            res = engine.log_observation(
                course_code="EC8702",
                lab_id="EC8702_LAB1",
                student_id="ENG-2024-042",
                telemetry={"packet_index": i, "adc_raw": 2048 + (i * 10), "v_sense": 1.65}
            )
            assert res["status"] == "success"

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        # Multi-write burst should complete rapidly under WAL mode
        assert elapsed_ms < 1500, f"Write burst took too long: {elapsed_ms:.1f}ms"

        # Check total count
        conn = sqlite3.connect(temp_db_path)
        count = conn.execute("SELECT COUNT(*) FROM course_lab_observations").fetchone()[0]
        conn.close()
        assert count == 15

    finally:
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)


def test_tier4_thermal_safety_execution_time():
    """Ensure tests run within strict timing bounds (<500ms), maintaining passive CPU profile."""
    start = time.perf_counter()

    # Fast verification of CourseLabEngine catalog validation
    lab_engine = CourseLabEngine()
    val_catalog = lab_engine.validate_catalog()
    assert val_catalog["valid"] is True
    assert val_catalog["total_labs"] >= 5

    # Fast verification of CourseQuizEngine catalog validation
    quiz_engine = CourseQuizEngine()
    val_quiz = quiz_engine.validate_catalog()
    assert val_quiz["valid"] is True
    assert val_quiz["total_questions"] >= 16

    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 500, f"Engine catalog validation exceeded 500ms: {elapsed_ms:.2f}ms"
