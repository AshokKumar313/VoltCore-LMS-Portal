"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 31 (ECE Coursework Assessment & Telemetry)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase31_ece_assessment.py
Target Facility: Lab 304 (Hardware Prototyping & Real-Time Embedded Systems Lab)
Regulation: Anna University ECE Regulation 2023
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import pytest
from backend.ece_assignment_engine import EceAssignmentEngine


@pytest.fixture
def test_engine(tmp_path):
    """Provides an isolated EceAssignmentEngine backed by a temporary SQLite WAL DB."""
    db_file = str(tmp_path / "test_ece_assessments.db")
    engine = EceAssignmentEngine(db_path=db_file)
    return engine


def test_engine_initialization_and_wal(test_engine):
    """Verifies that SQLite tables are created with WAL mode and indices."""
    conn = test_engine._get_connection()
    try:
        cur = conn.execute("PRAGMA journal_mode;")
        journal_mode = cur.fetchone()[0].upper()
        assert journal_mode == "WAL", f"Expected WAL mode, got {journal_mode}"

        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        assert "ece_student_assessments" in tables
        assert "ece_telemetry_logs" in tables
    finally:
        conn.close()


def test_verify_combinational_logic_full_adder(test_engine):
    """Validates 8-vector truth table verification for Full Adder combinational logic."""
    code = """
    Sum = A ^ B ^ Cin;
    Cout = (A & B) | (B & Cin) | (A & Cin);
    """
    res = test_engine.verify_combinational_logic(
        circuit_type="FULL_ADDER",
        student_code_or_expression=code,
        student_id="2023MITEC042"
    )
    assert res["status"] == "SUCCESS"
    assert res["circuit_type"] == "FULL_ADDER"
    assert res["test_vectors_count"] == 8
    assert res["passed_vectors"] == 8
    assert res["score"] == 25.0
    assert res["verification_status"] == "VERIFIED"


def test_verify_combinational_logic_mux4to1(test_engine):
    """Validates 4:1 multiplexer select line routing across all channels."""
    code = "Y = D[S1*2 + S0];"
    res = test_engine.verify_combinational_logic(
        circuit_type="MUX_4TO1",
        student_code_or_expression=code,
        student_id="2023MITEC042"
    )
    assert res["status"] == "SUCCESS"
    assert res["circuit_type"] == "MUX_4TO1"
    assert res["test_vectors_count"] == 4
    assert res["passed_vectors"] == 4
    assert res["score"] == 25.0
    assert res["verification_status"] == "VERIFIED"


def test_verify_combinational_logic_unsupported(test_engine):
    """Verifies graceful handling of unsupported circuit types."""
    res = test_engine.verify_combinational_logic(
        circuit_type="UNKNOWN_CIRCUIT",
        student_code_or_expression="",
        student_id="2023MITEC042"
    )
    assert res["status"] == "ERROR"
    assert "Unsupported circuit" in res["message"]


def test_verify_button_debouncing_clean(test_engine):
    """Validates non-blocking software push-button debouncing with 100% chatter rejection."""
    clean_code = """
    unsigned long lastDebounceTime = 0;
    const unsigned long debounceDelay = 30;
    int buttonState = HIGH;
    int lastButtonState = HIGH;

    void checkButton() {
        int reading = digitalRead(BUTTON_PIN);
        if (reading != lastButtonState) {
            lastDebounceTime = millis();
        }
        if ((millis() - lastDebounceTime) > debounceDelay) {
            if (reading != buttonState) {
                buttonState = reading;
            }
        }
        lastButtonState = reading;
    }
    """
    res = test_engine.verify_button_debouncing(clean_code, student_id="2023MITEC042")
    assert res["status"] == "SUCCESS"
    assert res["score"] == 25.0
    assert res["chatter_rejection_efficiency_pct"] == 100.0
    assert res["verification_status"] == "VERIFIED"
    assert len(res["deductions"]) == 0
    assert len(res["positive_credits"]) >= 2


def test_verify_button_debouncing_with_blocking_delay(test_engine):
    """Ensures busy-wait delay() calls are penalized and flagged for revision."""
    flawed_code = """
    void checkButton() {
        if (digitalRead(BUTTON_PIN) == LOW) {
            delay(50); // Blocking delay halts CPU
            if (digitalRead(BUTTON_PIN) == LOW) {
                processPress();
            }
        }
    }
    """
    res = test_engine.verify_button_debouncing(flawed_code, student_id="2023MITEC042")
    assert res["status"] == "SUCCESS"
    assert res["score"] < 20.0
    assert res["verification_status"] == "REVISION_REQUIRED"
    assert any("delay()" in d["issue"] for d in res["deductions"])


def test_verify_non_blocking_timing_rollover_safe(test_engine):
    """Verifies that rollover-safe subtraction arithmetic passes with maximum score."""
    clean_timing_code = """
    unsigned long prevSensorMillis = 0;
    unsigned long prevTelemetryMillis = 0;
    const unsigned long sensorInterval = 200;
    const unsigned long telemetryInterval = 1000;

    void loop() {
        unsigned long currentMillis = millis();
        if ((currentMillis - prevSensorMillis >= sensorInterval)) {
            prevSensorMillis = currentMillis;
            readSensors();
        }
        if ((currentMillis - prevTelemetryMillis >= telemetryInterval)) {
            prevTelemetryMillis = currentMillis;
            sendTelemetry();
        }
    }
    """
    res = test_engine.verify_non_blocking_timing(clean_timing_code, student_id="2023MITEC042")
    assert res["status"] == "SUCCESS"
    assert res["score"] == 25.0
    assert res["rollover_safe"] is True
    assert res["cooperative_task_slots"] == 2
    assert res["verification_status"] == "VERIFIED"
    assert len(res["deductions"]) == 0


def test_verify_non_blocking_timing_flawed_addition_overflow(test_engine):
    """Ensures unsafe rollover addition (now >= last + interval) is penalized."""
    flawed_code = """
    void loop() {
        unsigned long current = millis();
        if (current >= lastTime + interval) { // Fails when millis() overflows at 49.7 days
            lastTime = current;
            doTask();
        }
    }
    """
    res = test_engine.verify_non_blocking_timing(flawed_code, student_id="2023MITEC042")
    assert res["status"] == "SUCCESS"
    assert res["rollover_safe"] is False
    assert any("rollover" in d["issue"].lower() for d in res["deductions"])


def test_verify_ir_proximity_interrupt_clean(test_engine):
    """Validates edge-triggered IR proximity ISR with volatile memory and zero blocking."""
    clean_isr = """
    const uint8_t IR_PIN = 19;
    volatile bool objectDetected = false;
    volatile unsigned long lastTriggerMicros = 0;

    void IRAM_ATTR irSensorISR() {
        objectDetected = true;
        lastTriggerMicros = micros();
    }

    void setup() {
        pinMode(IR_PIN, INPUT_PULLUP);
        attachInterrupt(digitalPinToInterrupt(IR_PIN), irSensorISR, FALLING);
    }
    """
    res = test_engine.verify_ir_proximity_interrupt(clean_isr, student_id="2023MITEC042")
    assert res["status"] == "SUCCESS"
    assert res["score"] == 25.0
    assert res["volatile_memory_guarantee"] is True
    assert res["verification_status"] == "VERIFIED"
    assert res["simulated_isr_latency_us"] <= 5.0
    assert len(res["deductions"]) == 0


def test_verify_ir_proximity_interrupt_forbidden_serial(test_engine):
    """Flags forbidden blocking operations (Serial.print, delay) inside ISR context."""
    flawed_isr = """
    bool objectDetected = false; // Missing volatile!

    void IRAM_ATTR irSensorISR() {
        Serial.println("Object Detected!"); // Forbidden in ISR!
        delay(10);                          // Forbidden in ISR!
        objectDetected = true;
    }

    void setup() {
        attachInterrupt(digitalPinToInterrupt(19), irSensorISR, FALLING);
    }
    """
    res = test_engine.verify_ir_proximity_interrupt(flawed_isr, student_id="2023MITEC042")
    assert res["status"] == "SUCCESS"
    assert res["score"] <= 10.0
    assert res["volatile_memory_guarantee"] is False
    assert res["verification_status"] == "REVISION_REQUIRED"
    assert any("volatile" in d["issue"].lower() for d in res["deductions"])
    assert any("forbidden operations" in d["issue"].lower() for d in res["deductions"])


def test_telemetry_logging_and_retrieval(test_engine):
    """Validates real-time hardware telemetry logging and retrieval via SQLite WAL."""
    t1 = test_engine.log_telemetry(
        experiment_type="COMBINATIONAL_ADDER",
        input_signals={"A": 1, "B": 1, "Cin": 1},
        output_signals={"Sum": 1, "Cout": 1},
        latency_us=8.5,
        student_id="2023MITEC042"
    )
    assert t1["status"] == "SUCCESS"
    assert "log_id" in t1

    t2 = test_engine.log_telemetry(
        experiment_type="IR_PROXIMITY",
        input_signals={"pin_19_state": 0},
        output_signals={"interrupt_triggered": 1},
        latency_us=4.2,
        student_id="2023MITEC042"
    )
    assert t2["status"] == "SUCCESS"

    logs = test_engine.get_telemetry_logs(limit=10)
    assert len(logs) == 2
    assert logs[0]["experiment_type"] == "IR_PROXIMITY"
    assert logs[1]["experiment_type"] == "COMBINATIONAL_ADDER"

    # Filtered query
    ir_logs = test_engine.get_telemetry_logs(experiment_type="IR_PROXIMITY")
    assert len(ir_logs) == 1
    assert ir_logs[0]["input_signals"]["pin_19_state"] == 0


def test_assessment_history_persistence(test_engine):
    """Verifies that past student submissions are persisted and queryable."""
    test_engine.verify_combinational_logic("FULL_ADDER", "Sum = A ^ B ^ Cin;", student_id="2023MITEC042")
    test_engine.verify_button_debouncing("void checkButton() { if ((millis() - t) > 30) {} }", student_id="2023MITEC042")

    history = test_engine.get_student_assessment_history(student_id="2023MITEC042", limit=10)
    assert len(history) == 2
    types = [h["assignment_type"] for h in history]
    assert "BUTTON_DEBOUNCE_VERIFICATION" in types
    assert "COMBINATIONAL_LOGIC_VERIFICATION" in types


def test_privacy_invariants_and_author_metadata():
    """Enforces absolute isolation of private contact credentials and author attribution."""
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    engine_file = os.path.join(workspace_root, "backend", "ece_assignment_engine.py")
    ui_component = os.path.join(workspace_root, "src", "components", "EceCourseworkGrid.jsx")

    with open(engine_file, "r", encoding="utf-8") as f:
        engine_content = f.read()

    with open(ui_component, "r", encoding="utf-8") as f:
        ui_content = f.read()

    # STRICT INVARIANTS:
    # 1. Private email ashokkumar2008313@gmail.com and phone 9597382878 MUST NEVER appear
    assert "ashokkumar2008313@gmail.com" not in engine_content
    assert "ashokkumar2008313@gmail.com" not in ui_content
    assert "9597382878" not in engine_content
    assert "9597382878" not in ui_content

    # 2. Public author attribution must be Ashok Kumar A (2023MITEC042)
    assert "2023MITEC042" in engine_content
    assert "2023MITEC042" in ui_content

