"""
========================================================================================
VoltCore Apex Academia - Phase 35 Test Suite
Module: FPGA VHDL/Verilog Synthesis & Logic Analyzer Simulator Tests
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
========================================================================================
"""

import os
import sqlite3
import pytest
from backend.fpga_synthesis_engine import (
    FpgaSynthesisEngine,
    FPGA_TARGETS,
    HDL_MODULES,
    fpga_synthesis_engine
)

TEST_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_fpga_synthesis.db")


@pytest.fixture(autouse=True)
def clean_test_db():
    """Ensure clean test database before and after each test."""
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
    yield
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass


def test_engine_initialization_and_wal():
    """Verifies SQLite tables and WAL mode are initialized correctly."""
    engine = FpgaSynthesisEngine(db_path=TEST_DB_PATH)
    conn = engine._get_connection()
    cursor = conn.cursor()

    # Verify journal mode
    journal_mode = cursor.execute("PRAGMA journal_mode;").fetchone()[0]
    assert journal_mode.upper() == "WAL"

    # Verify tables exist
    tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    assert "fpga_synthesis_runs" in tables
    assert "logic_analyzer_traces" in tables
    conn.close()


def test_get_available_targets_and_modules():
    """Verifies target FPGA catalogs and synthesizable HDL module templates."""
    engine = FpgaSynthesisEngine(db_path=TEST_DB_PATH)
    targets = engine.get_available_targets()
    modules = engine.get_available_modules()

    assert len(targets) >= 3
    target_keys = [t["key"] for t in targets]
    assert "XILINX_ARTIX7_XC7A35T" in target_keys
    assert "INTEL_CYCLONE_IV_EP4CE6" in target_keys
    assert "LATTICE_ICE40_HX1K" in target_keys

    assert len(modules) >= 4
    mod_keys = [m["key"] for m in modules]
    assert "CLOCK_DIVIDER_COUNTER" in mod_keys
    assert "UART_TX_FSM" in mod_keys
    assert "PIPELINED_ALU_8BIT" in mod_keys
    assert "FIFO_BUFFER_8X8" in mod_keys


def test_synthesize_clock_divider_artix7():
    """Verifies synthesis on Xilinx Artix-7 computes LUTs, FFs, setup slack, and Fmax."""
    engine = FpgaSynthesisEngine(db_path=TEST_DB_PATH)
    res = engine.synthesize_module(
        target_fpga="XILINX_ARTIX7_XC7A35T",
        module_key="CLOCK_DIVIDER_COUNTER",
        hdl_type="VERILOG",
        target_clock_mhz=100.0,
        student_id="2023MITEC042"
    )

    assert res["status"] == "SUCCESS"
    assert res["synthesis_id"].startswith("SYNTH_")
    assert res["target_fpga"]["family"] == "Artix-7"
    assert res["utilization"]["luts_used"] > 0
    assert res["utilization"]["ffs_used"] > 0
    assert res["utilization"]["luts_pct"] < 1.0  # Counter is very small relative to 20,800 LUTs
    assert res["timing_metrics"]["fmax_mhz"] > 200.0  # Artix-7 easily achieves > 200MHz for counter
    assert res["timing_metrics"]["timing_met"] is True
    assert res["timing_metrics"]["setup_slack_ns"] > 0.0


def test_synthesize_fsm_cyclone_iv():
    """Verifies synthesis on Intel Cyclone IV computes proper LE utilization and timing metrics."""
    engine = FpgaSynthesisEngine(db_path=TEST_DB_PATH)
    res = engine.synthesize_module(
        target_fpga="INTEL_CYCLONE_IV_EP4CE6",
        module_key="UART_TX_FSM",
        hdl_type="VHDL",
        target_clock_mhz=50.0,
        student_id="2023MITEC042"
    )

    assert res["status"] == "SUCCESS"
    assert res["target_fpga"]["vendor"] == "Intel PSG (Altera)"
    assert res["utilization"]["luts_used"] >= 30
    assert res["utilization"]["ffs_used"] >= 25
    assert res["timing_metrics"]["fmax_mhz"] > 100.0
    assert res["hdl_type"] == "VHDL"


def test_synthesize_pipelined_alu_dsp_usage():
    """Verifies DSP slice allocation and logic propagation delay for 8-bit pipelined ALU."""
    engine = FpgaSynthesisEngine(db_path=TEST_DB_PATH)
    res = engine.synthesize_module(
        target_fpga="XILINX_ARTIX7_XC7A35T",
        module_key="PIPELINED_ALU_8BIT",
        hdl_type="VERILOG",
        target_clock_mhz=150.0,
        student_id="2023MITEC042"
    )

    assert res["status"] == "SUCCESS"
    assert res["utilization"]["dsp_used"] == 1
    assert res["timing_metrics"]["t_logic_ns"] > 1.5


def test_generate_logic_analyzer_traces():
    """Verifies multi-channel digital waveform trace generation across clock cycles."""
    engine = FpgaSynthesisEngine(db_path=TEST_DB_PATH)
    res = engine.generate_logic_analyzer_traces(
        module_key="CLOCK_DIVIDER_COUNTER",
        cycles=32,
        clk_period_ns=10.0
    )

    assert res["status"] == "SUCCESS"
    assert res["cycles_count"] == 32
    assert len(res["traces"]) == 32

    # Verify first cycle (reset active)
    c0 = res["traces"][0]
    assert c0["cycle"] == 0
    assert c0["reset"] == 1
    assert c0["time_ns"] == 0.0

    # Verify post-reset cycle (reset deasserted)
    c5 = res["traces"][5]
    assert c5["cycle"] == 5
    assert c5["reset"] == 0
    assert "data_in_hex" in c5
    assert "data_out_hex" in c5
    assert "fsm_state" in c5
    assert "flags" in c5

    # Verify persistence in SQLite WAL
    conn = engine._get_connection()
    count = conn.execute("SELECT count(*) FROM logic_analyzer_traces WHERE synthesis_id = ?;", (res["synthesis_id"],)).fetchone()[0]
    assert count == 32
    conn.close()


def test_export_traces_csv():
    """Verifies RFC-4180 compliant CSV export containing logic analyzer waveforms."""
    engine = FpgaSynthesisEngine(db_path=TEST_DB_PATH)
    csv_str = engine.export_traces_csv(module_key="UART_TX_FSM", cycles=16, clk_period_ns=20.0)

    assert "Cycle,Time_ns,CLK,RESET,ENABLE,DATA_IN_HEX" in csv_str
    lines = [line.strip() for line in csv_str.strip().split("\n") if line.strip()]
    assert len(lines) == 17  # 1 header + 16 cycles
    assert "START (01)" in csv_str or "DATA_BIT" in csv_str or "IDLE (00)" in csv_str


def test_privacy_invariants_and_attribution():
    """Strictly verifies zero leakage of private credentials and confirms public attribution."""
    with open("backend/fpga_synthesis_engine.py", "r", encoding="utf-8") as f:
        code_str = f.read()

    # Zero leakage of private credentials
    assert "9597382878" not in code_str
    assert "ashokkumar2008313@gmail.com" not in code_str

    # Public attribution verified
    assert "Ashok Kumar A" in code_str
    assert "2023MITEC042" in code_str
    assert "Anna University" in code_str

