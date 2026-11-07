"""
========================================================================================
VoltCore Apex Academia - Test Suite for Phase 15
Automated Assessment & Grading Pipeline Engine (Firmware, Verilog RTL, MNA, Lab Reports, OBE)
Lead Systems Architect & Quality Assurance Director: Ashok Kumar A
========================================================================================
Validates:
  1. Firmware AST analysis: Memory leak, stack overflow, blocking FreeRTOS delay, pin conflicts.
  2. Verilog HDL RTL: Synthesizability (#delays), race conditions (blocking in clocked always), latch inference.
  3. MNA Analog Simulation: Newton-Raphson convergence, Kirchhoff laws, error percentage correlation.
  4. Lab Report Rubrics: Mandatory sections, observation dataset, theoretical error analysis, viva voce.
  5. Outcome-Based Education (OBE): CO1-CO6 attainment, PO1-PO12 mapping, Bloom's Taxonomy (L1-L6).
  6. SQLite WAL Mode Persistence into 'student_assessment_grades' table.
  7. High-Precision Performance Budget: Execution time < 350ms (HP Victus thermal profile).
  8. In-Memory REST API Endpoints: /api/autograder/grade, grades, rubrics, obe_matrix.
========================================================================================
"""

import os
import io
import json
import time
import pytest
import sqlite3

from backend.autograder_engine import (
    FirmwareAutograderEngine,
    VerilogRtlAutograderEngine,
    MnaTransientAutograderEngine,
    LabReportAutograderEngine,
    ObeCompetencyEngine,
    AutograderEngine,
    firmware_autograder,
    verilog_autograder,
    mna_autograder,
    lab_report_autograder,
    obe_engine,
    autograder_engine
)
import attendance_server


class MockHTTPConnection:
    """In-memory mock HTTP transport allowing complete HTTP protocol testing with 0 network sockets."""
    def __init__(self, request_bytes: bytes):
        self.rfile = io.BytesIO(request_bytes)
        self.wfile = io.BytesIO()

    def makefile(self, mode, *args, **kwargs):
        if "r" in mode:
            return self.rfile
        return self.wfile

    def sendall(self, b: bytes):
        self.wfile.write(b)


class DummyServer:
    pass


def execute_mock_http_request(method: str, path: str, payload: dict = None) -> tuple[int, dict]:
    """Helper to dispatch HTTP requests in-memory through attendance_server handlers."""
    if getattr(attendance_server, "HAS_FLASK", False):
        client = attendance_server.app.test_client()
        if method == "POST":
            resp = client.post(path, data=json.dumps(payload or {}), content_type="application/json")
        else:
            resp = client.get(path)
        return resp.status_code, json.loads(resp.data.decode("utf-8"))

    # In-memory execution using FallbackHTTPHandler
    raw_payload = json.dumps(payload or {}).encode("utf-8") if payload else b""
    headers = [
        f"{method} {path} HTTP/1.1",
        "Host: localhost",
        "Content-Type: application/json",
        f"Content-Length: {len(raw_payload)}"
    ]
    raw_req = "\r\n".join(headers).encode("ascii") + b"\r\n\r\n" + raw_payload

    conn = MockHTTPConnection(raw_req)
    attendance_server.FallbackHTTPHandler(conn, ("127.0.0.1", 54321), DummyServer())

    raw_resp = conn.wfile.getvalue().decode("utf-8")
    status_line = raw_resp.split("\r\n")[0]
    status_code = int(status_line.split(" ")[1])
    body_str = raw_resp.split("\r\n\r\n")[-1]
    return status_code, json.loads(body_str)


# ========================================================================================
# 1. Firmware Autograder Unit Tests
# ========================================================================================

class TestFirmwareAutograder:
    def test_memory_leak_detection(self):
        code_with_leak = """
        void process_sensor() {
            uint8_t* buf = (uint8_t*)malloc(128);
            // Missing free(buf)
        }
        """
        res = firmware_autograder.grade_firmware_submission(code_with_leak)
        assert res["status"] == "success"
        assert res["category_scores"]["memory_safety"] < 25
        assert any(d["category"] == "memory_safety" for d in res["deductions"])

    def test_freertos_blocking_delay_detection(self):
        rtos_code = """
        #include "FreeRTOS.h"
        void vTask1(void *pvParameters) {
            for(;;) {
                delay(100); // Bad: Busy-wait delay in RTOS
            }
        }
        """
        res = firmware_autograder.grade_firmware_submission(rtos_code)
        assert res["category_scores"]["concurrency_rtos"] < 25
        assert any(d["category"] == "concurrency_rtos" for d in res["deductions"])

    def test_hardware_input_only_pin_mode(self):
        bad_pin_code = """
        void setup() {
            pinMode(34, OUTPUT); // Pin 34 is input-only on ESP32
        }
        """
        res = firmware_autograder.grade_firmware_submission(bad_pin_code)
        assert res["category_scores"]["hardware_pins"] < 25
        assert any("input-only" in d["issue"].lower() for d in res["deductions"])


# ========================================================================================
# 2. Verilog HDL RTL Autograder Unit Tests
# ========================================================================================

class TestVerilogRtlAutograder:
    def test_synthesizable_alu_full_marks(self):
        clean_rtl = """
        module alu_core (
            input wire [3:0] a,
            input wire [3:0] b,
            input wire [1:0] op,
            output reg [3:0] result
        );
            always @* begin
                case (op)
                    2'b00: result = a + b;
                    2'b01: result = a - b;
                    2'b10: result = a & b;
                    2'b11: result = a | b;
                    default: result = 4'b0000;
                endcase
            end
        endmodule
        """
        res = verilog_autograder.grade_verilog_submission(clean_rtl, "alu_core")
        assert res["status"] == "success"
        assert res["total_score"] == 100
        assert res["grade"] == "O"
        assert res["passed"] is True
        assert len(res["deductions"]) == 0

    def test_non_synthesizable_delays(self):
        code_with_delays = """
        module bad_clock_gen (input clk, output reg out);
            always @(posedge clk) begin
                #10 out <= ~out;
            end
        endmodule
        """
        res = verilog_autograder.grade_verilog_submission(code_with_delays)
        assert res["category_scores"]["synthesizability"] < 25
        assert any(d["category"] == "synthesizability" for d in res["deductions"])

    def test_latch_inference_missing_default(self):
        latch_code = """
        module latch_decoder (input [1:0] sel, input d, output reg q);
            always @* begin
                case (sel)
                    2'b00: q = d;
                    2'b01: q = ~d;
                    // Missing default: -> unintentional transparent latch
                endcase
            end
        endmodule
        """
        res = verilog_autograder.grade_verilog_submission(latch_code)
        assert res["category_scores"]["combinational_latch_free"] < 25
        assert any("latch" in d["issue"].lower() for d in res["deductions"])


# ========================================================================================
# 3. MNA Analog Circuit Simulation Autograder Unit Tests
# ========================================================================================

class TestMnaTransientAutograder:
    def test_converged_mna_simulation(self):
        sim_results = {
            "converged": True,
            "iterations_count": 4,
            "trajectories": {
                "time_ms": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
                "v_in": [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
                "v_out": [0.0, 1.96, 3.16, 3.89, 4.33, 4.59, 4.95]
            }
        }
        res = mna_autograder.grade_mna_simulation(
            simulation_results=sim_results,
            theoretical_benchmarks={"v_final": 5.0, "time_constant_ms": 1.0},
            circuit_type="RC_STEP"
        )
        assert res["status"] == "success"
        assert res["total_score"] >= 90
        assert res["passed"] is True
        assert res["category_scores"]["convergence"] == 30

    def test_diverged_matrix_simulation(self):
        diverged_results = {
            "converged": False,
            "iterations_count": 100,
            "trajectories": {
                "time_ms": [0.0, 0.01],
                "v_out": [0.0, 1e8]  # Unphysical spike
            }
        }
        res = mna_autograder.grade_mna_simulation(diverged_results)
        assert res["category_scores"]["convergence"] == 0
        assert res["passed"] is False


# ========================================================================================
# 4. Lab Report Autograder Unit Tests
# ========================================================================================

class TestLabReportAutograder:
    def test_complete_report_grading(self):
        report = {
            "aim_objective": "To simulate and analyze the transient response of an RC low-pass filter under step input.",
            "circuit_netlist": "V1 IN 0 PULSE(0 5 0 1u 1u 1m 2m)\nR1 IN OUT 1k\nC1 OUT 0 1u",
            "observations": [
                {"time_ms": 0.0, "vin": 5.0, "vout": 0.0},
                {"time_ms": 1.0, "vin": 5.0, "vout": 3.16},
                {"time_ms": 2.0, "vin": 5.0, "vout": 4.32},
                {"time_ms": 3.0, "vin": 5.0, "vout": 4.75},
                {"time_ms": 4.0, "vin": 5.0, "vout": 4.91},
                {"time_ms": 5.0, "vin": 5.0, "vout": 4.98}
            ],
            "error_analysis": "The observed time constant tau = 1.02ms matches theoretical R*C = 1.00ms within 2.0% error.",
            "experimental_error_pct": 2.0,
            "viva_inferences": "Capacitor opposes instantaneous voltage changes due to i = C*dv/dt charge accumulation."
        }
        res = lab_report_autograder.grade_lab_report(report, "EC23C03")
        assert res["status"] == "success"
        assert res["total_score"] >= 90
        assert res["grade"] == "O"
        assert res["passed"] is True

    def test_missing_sections_penalty(self):
        incomplete_report = {
            "aim_objective": "Test circuit",
            # Missing circuit_netlist, observations, error_analysis, viva
        }
        res = lab_report_autograder.grade_lab_report(incomplete_report)
        assert res["total_score"] < 40
        assert res["grade"] == "RA"
        assert res["passed"] is False


# ========================================================================================
# 5. Outcome-Based Education (OBE) Competency Unit Tests
# ========================================================================================

class TestObeCompetencyEngine:
    def test_obe_attainment_mapping(self):
        obe = obe_engine.compute_obe_attainment("FIRMWARE_C", 85.0, "EC8701")
        assert obe["course_outcome"] == "CO3"
        assert "PO1" in obe["program_outcomes"]
        assert obe["bloom_taxonomy_level"] == "L3"
        assert obe["attainment_level"] == 3
        assert obe["attainment_status"] == "SUBSTANTIAL"
        assert obe["threshold_met"] is True

    def test_obe_attainment_unmet(self):
        obe = obe_engine.compute_obe_attainment("VERILOG_RTL", 45.0, "EC8702")
        assert obe["attainment_level"] == 0
        assert obe["attainment_status"] == "NOT_ATTAINED"
        assert obe["threshold_met"] is False


# ========================================================================================
# 6. Central Autograder Facade & SQLite WAL Persistence Unit Tests
# ========================================================================================

class TestAutograderFacadeAndPersistence:
    def test_grade_assessment_and_sqlite_wal(self):
        payload = {
            "source_code": """
            module dff (input clk, input rst, input d, output reg q);
                always @(posedge clk or posedge rst) begin
                    if (rst) q <= 1'b0;
                    else q <= d;
                end
            endmodule
            """
        }
        res = autograder_engine.grade_assessment(
            student_id="STU_TEST_001",
            module_code="EC8702",
            assessment_type="VERILOG_RTL",
            payload=payload,
            student_name="Ashok Kumar"
        )
        assert res["status"] == "SUCCESS"
        assert res["assessment_id"].startswith("GRADE_")
        assert res["percentage"] >= 90.0
        assert res["evaluator_verdict"] == "DISTINCTION"
        assert res["obe_attainment"]["course_outcome"] == "CO4"

        # Verify entry in SQLite database
        grades = autograder_engine.get_student_grades("STU_TEST_001", limit=5)
        assert len(grades) > 0
        latest = grades[0]
        assert latest["assessment_id"] == res["assessment_id"]
        assert latest["assessment_type"] == "VERILOG_RTL"

    def test_cohort_obe_summary(self):
        # Insert a few grades for a module
        autograder_engine.grade_assessment(
            student_id="STU_A", module_code="EC_COHORT_TEST", assessment_type="GATE_EXAM",
            payload={"correct_answers": 8, "total_questions": 10}
        )
        autograder_engine.grade_assessment(
            student_id="STU_B", module_code="EC_COHORT_TEST", assessment_type="GATE_EXAM",
            payload={"correct_answers": 4, "total_questions": 10}
        )
        summary = autograder_engine.get_cohort_obe_summary("EC_COHORT_TEST")
        assert summary["cohort_size"] >= 2
        assert "CO1" in summary["co_attainments"]

    def test_performance_thermal_budget(self):
        """Ensures autograder execution takes < 350ms to protect HP Victus thermal profile."""
        t0 = time.perf_counter()
        autograder_engine.grade_assessment(
            student_id="STU_PERF",
            module_code="EC8701",
            assessment_type="FIRMWARE_C",
            payload={"source_code": "void setup(){ pinMode(2, OUTPUT); } void loop(){ delay(10); }"}
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        assert elapsed_ms < 350.0, f"Autograder evaluation took {elapsed_ms:.2f}ms (> 350ms budget)"


# ========================================================================================
# 7. In-Memory REST API Endpoints Unit Tests
# ========================================================================================

class TestAutograderRestEndpoints:
    def test_api_autograder_grade_endpoint(self):
        post_payload = {
            "student_id": "STU_API_01",
            "student_name": "API Tester",
            "module_code": "EC8701",
            "assessment_type": "GATE_EXAM",
            "payload": {
                "correct_answers": 9,
                "total_questions": 10
            }
        }
        status, data = execute_mock_http_request("POST", "/api/autograder/grade", post_payload)
        assert status == 200
        assert data["status"] == "SUCCESS"
        assert data["percentage"] == 90.0
        assert data["letter_grade"] == "O"

    def test_api_autograder_grades_endpoint(self):
        status, data = execute_mock_http_request("GET", "/api/autograder/grades?student_id=STU_API_01")
        assert status == 200
        assert data["status"] == "SUCCESS"
        assert isinstance(data["grades"], list)

    def test_api_autograder_rubrics_endpoint(self):
        status, data = execute_mock_http_request("GET", "/api/autograder/rubrics")
        assert status == 200
        assert data["status"] == "SUCCESS"
        assert "VERILOG_RTL" in data["rubrics"]

    def test_api_autograder_obe_matrix_endpoint(self):
        status, data = execute_mock_http_request("GET", "/api/autograder/obe_matrix?module_code=EC8701")
        assert status == 200
        assert data["status"] == "SUCCESS"
        assert "obe_summary" in data
