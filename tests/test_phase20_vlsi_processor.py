"""
========================================================================================
VoltCore Apex Academia - Test Suite for Phase 20
SystemVerilog Verification Studio, ASIC Physical Design Explorer & RISC-V 5-Stage Core
Lead VLSI Architect & Digital Verification Specialist: Ashok Kumar A
========================================================================================
Validates:
  1. SystemVerilog Assertion (SVA) Verification Engine:
     - Immediate assertions: 'assert (expr)' procedural checking.
     - Concurrent properties: 'assert property (@(posedge clk) disable iff (rst) expr)'.
     - Sequences & temporal sampled functions: $rose(sig), $fell(sig), $past(sig, k),
       $stable(sig), $onehot(sig), temporal delays ##n and ##[min:max].
     - Implication operators: Overlapping (|->) and Non-overlapping (|=>).
     - Formal coverage metrics: attempts, matches, failures, vacuous passes, and coverage %.
  2. ASIC Physical Design Explorer:
     - Floorplan dimensioning: cell area, target utilization, core width/height, aspect ratio,
       die margins, perimeter I/O ring pad budget, and wafer yield.
     - Placement Congestion & Routing Density Heatmap: 2D mesh grid discretization,
       spatial clustering, hotspot detection (>= 0.85), routability status.
     - Interconnect Elmore Distributed RC Delay: wire resistance and capacitance scaling across
       nodes (7nm, 14nm, 28nm, 65nm, 180nm), optimal repeater pitch L_opt, buffered delay reduction.
     - Clock Tree Synthesis (CTS) Modeling: symmetric H-tree depth, clock insertion latency,
       PVT clock skew, jitter RSS, setup/hold slack margin timing closure at 1 GHz.
     - SQLite WAL mode persistence in 'vlsi_physical_design_history'.
  3. RISC-V 5-Stage Pipelined Processor Core:
     - Full 5-stage pipeline: IF -> ID -> EX -> MEM -> WB.
     - RV32I integer instructions: ADD, SUB, AND, OR, XOR, SLT, ADDI, LW, SW, BEQ, BNE, JAL, NOP.
     - Data Forwarding Unit: EX->EX and MEM->EX bypassing for rs1 and rs2 without stalls.
     - Load-Use Hazard Detection: 1-cycle stall bubble injection, PC & IF/ID freeze.
     - Control Hazards: branch and jump evaluation with pipeline flush.
     - Invariant: register x0 hardwired to 0.
     - Cycle trace, CPI, IPC, stall count, forwarding count, register state snapshots.
     - SQLite WAL mode persistence in 'riscv_processor_history'.
  4. In-Memory REST API Endpoints:
     - POST /api/vlsi/sva_analyze
     - POST /api/vlsi/floorplan
     - POST /api/vlsi/density_heatmap
     - POST /api/vlsi/elmore_delay
     - POST /api/vlsi/cts_model
     - POST /api/riscv/simulate
     - POST /api/riscv/step
     - GET  /api/vlsi/history
     - GET  /api/riscv/history
  5. High-Precision Performance Budget: Execution time < 350ms (HP Victus passive profile).
========================================================================================
"""

import io
import json
import math
import time
import pytest
import sqlite3

from backend.vlsi_physical_design_engine import (
    SystemVerilogAssertionAnalyzer,
    sva_assertion_analyzer,
    ASICPhysicalDesignEngine,
    vlsi_physical_design_engine,
    TECH_NODE_LIBRARY
)
from backend.riscv_processor_engine import (
    RiscVInstruction,
    RiscVAssembler,
    RiscV5StagePipeline,
    RiscVProcessorEngine,
    riscv_processor_engine,
    to_signed_32,
    to_uint_32
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
    """Dispatches HTTP requests in-memory through attendance_server handlers."""
    if getattr(attendance_server, "HAS_FLASK", False):
        client = attendance_server.app.test_client()
        if method == "POST":
            resp = client.post(path, data=json.dumps(payload or {}), content_type="application/json")
        else:
            resp = client.get(path)
        return resp.status_code, json.loads(resp.data.decode("utf-8"))

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
# 1. SystemVerilog Assertion (SVA) Verification Engine Tests
# ========================================================================================
class TestSystemVerilogAssertionAnalyzer:
    """Verifies SVA property parsing, evaluation, and coverage calculation."""

    def test_immediate_assertion_pass_and_fail(self):
        analyzer = SystemVerilogAssertionAnalyzer()
        trace = {
            "a": [1, 2, 3, 4],
            "b": [1, 2, 0, 4]
        }
        res = analyzer.evaluate_trace(["assert (a == b);"], trace)
        assert res["total_attempts"] == 4
        assert res["total_matches"] == 3
        assert res["total_failures"] == 1
        assert res["all_passed"] is False
        assert res["overall_assertion_coverage_pct"] == 75.0

    def test_concurrent_assertion_overlapping_implication(self):
        analyzer = SystemVerilogAssertionAnalyzer()
        # Overlapping |-> : if req at cycle t, gnt must be 1 at cycle t
        trace = {
            "req": [0, 1, 0, 1, 0],
            "gnt": [0, 1, 0, 0, 0]
        }
        res = analyzer.evaluate_trace(["assert property (@(posedge clk) req |-> gnt);"], trace)
        assert res["total_attempts"] == 5
        assert res["total_matches"] == 1  # Cycle 1 matched
        assert res["total_failures"] == 1  # Cycle 3 failed
        assert res["total_vacuous_passes"] == 3  # Cycles 0, 2, 4 (req == 0)

    def test_concurrent_assertion_non_overlapping_implication(self):
        analyzer = SystemVerilogAssertionAnalyzer()
        # Non-overlapping |=> : if req at cycle t, gnt must be 1 at cycle t+1
        trace = {
            "req": [0, 1, 0, 0, 1, 0],
            "gnt": [0, 0, 1, 0, 0, 1]
        }
        res = analyzer.evaluate_trace(["assert property (@(posedge clk) req |=> gnt);"], trace)
        assert res["total_attempts"] == 6
        assert res["total_matches"] == 2
        assert res["total_failures"] == 0
        assert res["total_vacuous_passes"] == 4
        assert res["all_passed"] is True

    def test_sequence_delay_range_operator(self):
        analyzer = SystemVerilogAssertionAnalyzer()
        # Range delay: req |-> ##[1:3] ack
        trace = {
            "req": [1, 0, 0, 0, 0],
            "ack": [0, 0, 1, 0, 0]  # ack arrives at cycle 2 (t+2), within [1:3]
        }
        res = analyzer.evaluate_trace(["assert property (@(posedge clk) req |-> ##[1:3] ack);"], trace)
        assert res["total_matches"] == 1
        assert res["total_failures"] == 0

    def test_sampled_value_functions_rose_fell_past(self):
        analyzer = SystemVerilogAssertionAnalyzer()
        trace = {
            "req": [0, 1, 1, 0, 0],
            "gnt": [0, 0, 1, 0, 0],
            "state": [1, 2, 3, 4, 5]
        }
        # $rose(req) occurs only at cycle 1
        res_rose = analyzer.evaluate_trace(["assert property (@(posedge clk) $rose(req) |=> gnt);"], trace)
        assert res_rose["total_matches"] == 1

        # $fell(req) occurs only at cycle 3
        res_fell = analyzer.evaluate_trace(["assert property (@(posedge clk) $fell(req) |-> !req);"], trace)
        assert res_fell["total_matches"] == 1

    def test_sampled_function_onehot(self):
        analyzer = SystemVerilogAssertionAnalyzer()
        trace = {
            "bus": [1, 2, 4, 3, 8]  # 3 has two bits set (not one-hot)
        }
        res = analyzer.evaluate_trace(["assert property (@(posedge clk) $onehot(bus));"], trace)
        assert res["total_matches"] == 4
        assert res["total_failures"] == 1

    def test_assertion_disable_iff_reset(self):
        analyzer = SystemVerilogAssertionAnalyzer()
        trace = {
            "rst": [1, 1, 0, 0],
            "req": [1, 1, 1, 0],
            "gnt": [0, 0, 1, 0]
        }
        res = analyzer.evaluate_trace(["assert property (@(posedge clk) disable iff (rst) req |-> gnt);"], trace)
        report = res["assertion_reports"][0]
        assert report["attempts"] == 2  # Cycles 2 and 3 (cycles 0 and 1 disabled)
        assert report["matches"] == 1
        assert report["failures"] == 0


# ========================================================================================
# 2. ASIC Physical Design Explorer Tests
# ========================================================================================
class TestASICPhysicalDesignEngine:
    """Verifies floorplanning, congestion heatmaps, Elmore delay, and CTS modeling."""

    def test_floorplan_dimensions_and_utilization(self):
        engine = ASICPhysicalDesignEngine()
        fp = engine.calculate_floorplan_dimensions(
            gate_count=100000,
            tech_node="28nm",
            target_utilization=0.70,
            aspect_ratio=1.0,
            core_margin_um=25.0
        )
        assert fp["gate_count"] == 100000
        assert fp["total_cell_area_um2"] == pytest.approx(46000.0, abs=1.0)
        assert fp["core_area_um2"] == pytest.approx(65714.28, abs=1.0)
        assert fp["aspect_ratio"] == 1.0
        assert fp["core_width_um"] == fp["core_height_um"]
        assert fp["die_width_um"] == fp["core_width_um"] + 50.0
        assert fp["die_utilization"] < fp["target_utilization"]
        assert fp["max_io_pad_count"] > 0
        assert fp["estimated_wafer_yield_pct"] > 90.0

    def test_floorplan_technology_node_scaling(self):
        engine = ASICPhysicalDesignEngine()
        fp_7nm = engine.calculate_floorplan_dimensions(50000, tech_node="7nm")
        fp_180nm = engine.calculate_floorplan_dimensions(50000, tech_node="180nm")
        # 7nm FinFET should occupy a fraction of the silicon area of 180nm planar CMOS
        assert fp_7nm["core_area_um2"] < (fp_180nm["core_area_um2"] / 100.0)

    def test_placement_density_heatmap_generation(self):
        engine = ASICPhysicalDesignEngine()
        res = engine.generate_placement_density_heatmap(
            gate_count=50000,
            core_width_um=200.0,
            core_height_um=200.0,
            grid_cols=16,
            grid_rows=16,
            rent_exponent=0.65
        )
        assert res["grid_dimensions"]["rows"] == 16
        assert res["grid_dimensions"]["cols"] == 16
        assert len(res["density_heatmap"]) == 16
        assert len(res["density_heatmap"][0]) == 16
        assert 0.0 < res["average_density"] < 1.0
        assert res["peak_density"] <= 1.0
        assert isinstance(res["hotspots"], list)
        assert res["routability_status"] in ("ROUTABLE", "CONGESTION_RISK")

    def test_interconnect_elmore_rc_delay(self):
        engine = ASICPhysicalDesignEngine()
        res = engine.estimate_interconnect_elmore_delay(
            wirelength_um=1000.0,
            metal_layer="intermediate",
            tech_node="28nm"
        )
        assert res["unbuffered_elmore_delay_ps"] > 0.0
        assert res["optimal_repeater_spacing_um"] > 0.0
        # For long wire (1000um), buffer insertion should reduce total interconnect latency
        if res["recommended_buffer_count"] > 0:
            assert res["buffered_total_delay_ps"] < res["unbuffered_elmore_delay_ps"]
            assert res["buffer_speedup_savings_pct"] > 0.0

    def test_clock_tree_synthesis_model_and_timing_closure(self):
        engine = ASICPhysicalDesignEngine()
        cts = engine.model_clock_tree_synthesis(
            num_sinks=1024,
            die_width_um=400.0,
            die_height_um=400.0,
            target_freq_mhz=1000.0,
            tech_node="28nm",
            process_variation_sigma_pct=5.0
        )
        assert cts["htree_depth"] == 10  # log2(1024) = 10
        assert cts["clock_period_ps"] == 1000.0
        assert cts["clock_insertion_latency_ps"] > 0.0
        assert cts["clock_skew_ps"] > 0.0
        assert cts["clock_jitter_ps"] > 0.0
        assert "setup_slack_ps" in cts
        assert "hold_slack_ps" in cts
        assert cts["maximum_achievable_frequency_mhz"] > 0.0
        assert cts["timing_closure_passed"] is True


# ========================================================================================
# 3. RISC-V 5-Stage Pipelined Processor Core Tests
# ========================================================================================
class TestRiscV5StagePipeline:
    """Verifies RV32I pipeline stages, forwarding unit, stalls, branches, and register commit."""

    def test_rv32i_assembler_parsing(self):
        code = """
        # Fibonacci test
        ADDI x1, x0, 10
        ADDI x2, x0, 20
        ADD  x3, x1, x2
        SW   x3, 0(x0)
        LW   x4, 0(x0)
        NOP
        """
        instructions = RiscVAssembler.assemble(code)
        assert len(instructions) == 6
        assert instructions[0].opcode == "ADDI"
        assert instructions[0].rd == 1
        assert instructions[0].imm == 10
        assert instructions[2].opcode == "ADD"
        assert instructions[2].rd == 3
        assert instructions[3].opcode == "SW"
        assert instructions[4].opcode == "LW"

    def test_register_x0_hardwired_zero_invariant(self):
        pipeline = RiscV5StagePipeline()
        code = """
        ADDI x0, x0, 100
        ADD  x0, x0, x0
        """
        pipeline.load_program(code)
        res = pipeline.run_simulation()
        assert res["final_registers"]["x0"] == 0

    def test_data_hazard_ex_to_ex_forwarding(self):
        # Consecutive dependent instructions without NOPs
        code = """
        ADDI x1, x0, 15
        ADD  x2, x1, x1
        ADD  x3, x2, x1
        """
        pipeline = RiscV5StagePipeline()
        pipeline.load_program(code)
        res = pipeline.run_simulation()
        assert res["final_registers"]["x1"] == 15
        assert res["final_registers"]["x2"] == 30
        assert res["final_registers"]["x3"] == 45
        assert res["stalls_count"] == 0  # Fully resolved by forwarding!
        assert res["forwarding_events"] >= 3

    def test_load_use_hazard_1_cycle_stall_injection(self):
        # LW immediately followed by dependent ADD strictly requires 1 stall bubble
        code = """
        ADDI x1, x0, 50
        SW   x1, 0(x0)
        LW   x2, 0(x0)
        ADD  x3, x2, x1
        """
        pipeline = RiscV5StagePipeline()
        pipeline.load_program(code)
        res = pipeline.run_simulation()
        assert res["final_registers"]["x3"] == 100
        assert res["stalls_count"] == 1  # Exactly 1 load-use stall bubble!

    def test_branch_taken_control_hazard_flush(self):
        code = """
        ADDI x1, x0, 5
        ADDI x2, x0, 5
        BEQ  x1, x2, target
        ADDI x3, x0, 999   # Should be flushed!
        target:
        ADDI x4, x0, 42
        """
        pipeline = RiscV5StagePipeline()
        pipeline.load_program(code)
        res = pipeline.run_simulation()
        assert res["final_registers"]["x4"] == 42
        assert res["final_registers"]["x3"] == 0  # Never committed due to pipeline flush!
        assert res["branch_flushes"] == 1

    def test_jal_procedure_call_and_return_address(self):
        code = """
        ADDI x5, x0, 7
        JAL  ra, subroutine
        ADDI x2, x0, 99
        subroutine:
        ADDI x3, x5, 10
        """
        pipeline = RiscV5StagePipeline()
        pipeline.load_program(code)
        res = pipeline.run_simulation()
        assert res["final_registers"]["ra"] == 8  # PC+4 where JAL was at PC=4
        assert res["final_registers"]["x3"] == 17

    def test_rv32i_arithmetic_logical_suite(self):
        code = """
        ADDI x1, x0, 12
        ADDI x2, x0, 5
        SUB  x3, x1, x2   # 12 - 5 = 7
        AND  x4, x1, x2   # 12 & 5 = 4
        OR   x5, x1, x2   # 12 | 5 = 13
        XOR  x6, x1, x2   # 12 ^ 5 = 9
        SLT  x7, x2, x1   # 5 < 12 = 1
        SLT  x8, x1, x2   # 12 < 5 = 0
        """
        pipeline = RiscV5StagePipeline()
        pipeline.load_program(code)
        res = pipeline.run_simulation()
        regs = res["final_registers"]
        assert regs["x3"] == 7
        assert regs["x4"] == 4
        assert regs["x5"] == 13
        assert regs["x6"] == 9
        assert regs["x7"] == 1
        assert regs["x8"] == 0


# ========================================================================================
# 4. In-Memory REST API Endpoints Verification
# ========================================================================================
class TestPhase20RESTEndpoints:
    """Verifies all Phase 20 HTTP API routes with in-memory execution."""

    def test_api_vlsi_sva_analyze_endpoint(self):
        status, body = execute_mock_http_request("POST", "/api/vlsi/sva_analyze", {
            "assertions": ["assert property (@(posedge clk) req |=> gnt);"],
            "trace": {
                "req": [0, 1, 0, 0, 1, 0],
                "gnt": [0, 0, 1, 0, 0, 1]
            }
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert body["data"]["total_matches"] == 2
        assert body["data"]["all_passed"] is True

    def test_api_vlsi_floorplan_endpoint(self):
        status, body = execute_mock_http_request("POST", "/api/vlsi/floorplan", {
            "gate_count": 50000,
            "tech_node": "28nm",
            "target_utilization": 0.70,
            "aspect_ratio": 1.0
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert body["data"]["core_area_um2"] > 0
        assert "die_width_um" in body["data"]

    def test_api_vlsi_density_heatmap_endpoint(self):
        status, body = execute_mock_http_request("POST", "/api/vlsi/density_heatmap", {
            "gate_count": 50000,
            "core_width_um": 200.0,
            "core_height_um": 200.0,
            "grid_cols": 16,
            "grid_rows": 16
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert len(body["data"]["density_heatmap"]) == 16

    def test_api_vlsi_elmore_delay_endpoint(self):
        status, body = execute_mock_http_request("POST", "/api/vlsi/elmore_delay", {
            "wirelength_um": 500.0,
            "metal_layer": "intermediate",
            "tech_node": "28nm"
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert body["data"]["unbuffered_elmore_delay_ps"] > 0.0

    def test_api_vlsi_cts_model_endpoint(self):
        status, body = execute_mock_http_request("POST", "/api/vlsi/cts_model", {
            "num_sinks": 1024,
            "die_width_um": 300.0,
            "die_height_um": 300.0,
            "target_freq_mhz": 1000.0,
            "tech_node": "28nm"
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert body["data"]["timing_closure_passed"] is True

    def test_api_vlsi_history_endpoint(self):
        status, body = execute_mock_http_request("GET", "/api/vlsi/history?limit=10")
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert isinstance(body["data"], list)

    def test_api_riscv_simulate_endpoint(self):
        prog = """
        ADDI x1, x0, 10
        ADDI x2, x0, 25
        ADD  x3, x1, x2
        """
        status, body = execute_mock_http_request("POST", "/api/riscv/simulate", {
            "assembly_code": prog,
            "program_name": "api_test_add",
            "max_cycles": 100
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert body["data"]["final_registers"]["x3"] == 35

    def test_api_riscv_step_endpoint(self):
        prog = "ADDI x1, x0, 5\n"
        status, body = execute_mock_http_request("POST", "/api/riscv/step", {
            "assembly_code": prog,
            "cycles": 3
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert len(body["steps"]) == 3
        assert body["current_cycle"] == 3

    def test_api_riscv_history_endpoint(self):
        status, body = execute_mock_http_request("GET", "/api/riscv/history?limit=10")
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert isinstance(body["data"], list)


# ========================================================================================
# 5. Thermal & Execution Performance Budget Test (< 350ms on HP Victus)
# ========================================================================================
class TestThermalPerformanceBudget:
    """Verifies that all Phase 20 algorithms execute well within the 350ms passive thermal budget."""

    def test_full_phase20_execution_budget(self):
        t0 = time.perf_counter()

        # 1. SVA trace evaluation
        sva = SystemVerilogAssertionAnalyzer()
        trace = {"clk": [0, 1] * 20, "req": [0, 1, 0, 0] * 10, "gnt": [0, 0, 1, 0] * 10}
        sva.evaluate_trace(["assert property (@(posedge clk) req |=> gnt);"], trace)

        # 2. ASIC Floorplan, Heatmap, and CTS
        asic = ASICPhysicalDesignEngine()
        fp = asic.calculate_floorplan_dimensions(50000, "28nm")
        asic.generate_placement_density_heatmap(50000, fp["core_width_um"], fp["core_height_um"])
        asic.estimate_interconnect_elmore_delay(500.0, "intermediate", "28nm")
        asic.model_clock_tree_synthesis(512, fp["die_width_um"], fp["die_height_um"], 1000.0, "28nm")

        # 3. RISC-V 5-stage pipeline simulation
        prog = """
        ADDI x1, x0, 10
        ADDI x2, x0, 20
        ADD  x3, x1, x2
        SW   x3, 0(x0)
        LW   x4, 0(x0)
        ADD  x5, x4, x1
        """
        riscv = RiscVProcessorEngine()
        riscv.simulate_assembly(prog, "budget_run", max_cycles=100)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        assert elapsed_ms < 350.0, f"Phase 20 execution time {elapsed_ms:.2f}ms exceeded 350ms passive profile budget"
