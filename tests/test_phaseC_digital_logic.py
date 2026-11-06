"""
========================================================================================
VoltCore Apex Academia - Phase C Test Suite: Digital Electronics Engineering
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU usage.
========================================================================================
"""

import os
import pytest
import sqlite3
from backend.digital_logic_engine import (
    DigitalLogicEngine,
    LOGIC_GATES_SPECS,
    KMAP_4VAR_CELL_MAP
)


@pytest.fixture
def engine(tmp_path):
    """Instantiate DigitalLogicEngine with an isolated temporary SQLite WAL database."""
    db_file = str(tmp_path / "test_digital_logic.db")
    return DigitalLogicEngine(db_path=db_file)


def test_digital_logic_wal_mode(engine):
    """Verify that SQLite tables for simulations and K-Maps are initialized in WAL mode."""
    conn = sqlite3.connect(engine.db_path)
    try:
        cur = conn.execute("PRAGMA journal_mode;")
        mode = cur.fetchone()[0]
        assert mode.lower() == "wal", f"Expected WAL mode, got {mode}"

        cur = conn.execute("""
            SELECT name FROM sqlite_master WHERE type='table'
            AND name IN ('digital_logic_simulations', 'kmap_saved_solutions');
        """)
        tables = {row[0] for row in cur.fetchall()}
        assert "digital_logic_simulations" in tables
        assert "kmap_saved_solutions" in tables
    finally:
        conn.close()


def test_generate_truth_table_all_gates(engine):
    """Verify truth table generation for all standard 74HC logic gates (Feature 231)."""
    gates = ["AND", "OR", "NOT", "NAND", "NOR", "XOR", "XNOR"]
    for gate in gates:
        res = engine.generate_truth_table(gate)
        assert res["gate"] == gate
        assert res["ic_part"] in [specs["ic_part"] for specs in LOGIC_GATES_SPECS.values()]
        assert res["propagation_delay_ns"] > 0
        assert res["power_dissipation_uw"] > 0
        assert len(res["truth_table"]) == (2 if gate == "NOT" else 4)

    # Validate specific outputs
    and_tt = engine.generate_truth_table("AND", num_inputs=2)["truth_table"]
    assert and_tt[0]["output"] == 0 # 0, 0 -> 0
    assert and_tt[1]["output"] == 0 # 0, 1 -> 0
    assert and_tt[2]["output"] == 0 # 1, 0 -> 0
    assert and_tt[3]["output"] == 1 # 1, 1 -> 1

    xor_tt = engine.generate_truth_table("XOR", num_inputs=2)["truth_table"]
    assert xor_tt[0]["output"] == 0
    assert xor_tt[1]["output"] == 1
    assert xor_tt[2]["output"] == 1
    assert xor_tt[3]["output"] == 0

    not_tt = engine.generate_truth_table("NOT")["truth_table"]
    assert len(not_tt) == 2
    assert not_tt[0]["output"] == 1 # 0 -> 1
    assert not_tt[1]["output"] == 0 # 1 -> 0

    with pytest.raises(ValueError):
        engine.generate_truth_table("UNKNOWN_GATE")


def test_multi_input_gates(engine):
    """Verify 3-input and 4-input gate truth tables (Feature 231)."""
    and3 = engine.generate_truth_table("AND", num_inputs=3)
    assert len(and3["truth_table"]) == 8
    assert and3["truth_table"][-1]["output"] == 1
    assert sum(r["output"] for r in and3["truth_table"]) == 1

    or4 = engine.generate_truth_table("OR", num_inputs=4)
    assert len(or4["truth_table"]) == 16
    assert or4["truth_table"][0]["output"] == 0
    assert sum(r["output"] for r in or4["truth_table"]) == 15


def test_multi_radix_converter(engine):
    """Verify multi-radix conversion across Bin, Oct, Dec, and Hex with division traces (Feature 232)."""
    res = engine.convert_radix("42", from_base=10)
    assert res["decimal"] == 42
    assert res["binary"] == "101010"
    assert res["octal"] == "52"
    assert res["hexadecimal"] == "2A"
    assert len(res["binary_division_steps"]) > 0
    assert len(res["hex_division_steps"]) > 0

    # Test from hex
    res_hex = engine.convert_radix("FF", from_base=16)
    assert res_hex["decimal"] == 255
    assert res_hex["binary"] == "11111111"

    # Test invalid base or input
    with pytest.raises(ValueError):
        engine.convert_radix("INVALID_BIN", from_base=2)


def test_twos_complement_calculation(engine):
    """Verify two's complement and sign bit calculation for 8-bit integers (Feature 233)."""
    # Positive number: 25 -> 00011001
    pos = engine.calculate_twos_complement(25, bit_width=8)
    assert pos["sign_bit"] == 0
    assert pos["is_negative"] is False
    assert pos["twos_complement_binary"] == "00011001"

    # Negative number: -25 -> 11100111
    neg = engine.calculate_twos_complement(-25, bit_width=8)
    assert neg["sign_bit"] == 1
    assert neg["is_negative"] is True
    assert neg["twos_complement_binary"] == "11100111"
    assert neg["ones_complement"] == "11100110"

    # Extreme bounds for 8-bit: -128 to +127
    min_8 = engine.calculate_twos_complement(-128, bit_width=8)
    assert min_8["twos_complement_binary"] == "10000000"

    max_8 = engine.calculate_twos_complement(127, bit_width=8)
    assert max_8["twos_complement_binary"] == "01111111"

    with pytest.raises(ValueError):
        engine.calculate_twos_complement(128, bit_width=8)

    with pytest.raises(ValueError):
        engine.calculate_twos_complement(-129, bit_width=8)

    with pytest.raises(ValueError):
        engine.calculate_twos_complement(10, bit_width=12) # Unsupported bit width


def test_signed_addition_overflow(engine):
    """Verify signed addition and arithmetic overflow detection (V = Cin ^ Cout) (Feature 233)."""
    # No overflow: 50 + 40 = 90 (within [-128, 127])
    no_ovf = engine.signed_addition_overflow_check(50, 40, bit_width=8)
    assert no_ovf["overflow_detected"] is False
    assert no_ovf["overflow_flag_v"] == 0
    assert no_ovf["theoretical_sum"] == 90

    # Overflow: 100 + 50 = 150 (> 127)
    ovf = engine.signed_addition_overflow_check(100, 50, bit_width=8)
    assert ovf["overflow_detected"] is True
    assert ovf["overflow_flag_v"] == 1
    assert ovf["theoretical_sum"] == 150

    # Negative overflow: -100 + (-50) = -150 (< -128)
    neg_ovf = engine.signed_addition_overflow_check(-100, -50, bit_width=8)
    assert neg_ovf["overflow_detected"] is True
    assert neg_ovf["overflow_flag_v"] == 1


def test_boolean_algebra_axioms(engine):
    """Verify De Morgan, Absorption, and Consensus theorems step-by-step (Feature 234)."""
    demorgan = engine.simplify_boolean_steps("demorgan_nand", a=1, b=0)
    assert demorgan["equivalent"] is True
    assert len(demorgan["steps"]) == 3

    absorption = engine.simplify_boolean_steps("absorption", a=1, b=0)
    assert absorption["equivalent"] is True
    assert absorption["lhs"] == 1

    consensus = engine.simplify_boolean_steps("consensus", a=1, b=1, c=0)
    assert consensus["equivalent"] is True

    with pytest.raises(ValueError):
        engine.simplify_boolean_steps("unknown_axiom", a=1, b=1)


def test_4var_kmap_solver(engine):
    """Verify 4-variable K-Map grouping, Gray code matrix, and SOP expression (Feature 235)."""
    # Minterms for Quad {0, 1, 4, 5} -> ~A & ~C
    res = engine.solve_4var_kmap(minterms=[0, 1, 4, 5], dont_cares=[])
    assert res["minterms"] == [0, 1, 4, 5]
    assert len(res["grid_4x4"]) == 4
    assert len(res["grid_4x4"][0]) == 4

    # Verify Gray code coordinates
    assert KMAP_4VAR_CELL_MAP[(0, 0)] == 0
    assert KMAP_4VAR_CELL_MAP[(0, 1)] == 1
    assert KMAP_4VAR_CELL_MAP[(0, 2)] == 3
    assert KMAP_4VAR_CELL_MAP[(0, 3)] == 2
    assert KMAP_4VAR_CELL_MAP[(2, 2)] == 15

    # Check detected prime implicant
    assert any(g["term"] == "~A & ~C" for g in res["prime_implicants"])
    assert "~A & ~C" in res["minimized_sop"]

    # Test out of bounds minterm
    with pytest.raises(ValueError):
        engine.solve_4var_kmap(minterms=[16])


def test_persistence_methods(engine):
    """Verify SQLite WAL simulation and K-Map saving & retrieval."""
    # Test save simulation
    sim_res = engine.save_simulation(
        student_id="2023MITEC042",
        operation_type="BASE_CONVERT_HEX",
        input_params={"val": "255", "base": 10},
        result_output={"hex": "FF", "bin": "11111111"}
    )
    assert sim_res["status"] == "success"
    assert sim_res["simulation_id"] > 0

    sims = engine.get_simulations("2023MITEC042")
    assert len(sims) >= 1
    assert sims[0]["operation_type"] == "BASE_CONVERT_HEX"

    # Test save K-map solution
    kmap_res = engine.save_kmap_solution(
        student_id="2023MITEC042",
        minterms=[0, 1, 4, 5],
        dont_cares=[],
        sop_expression="~A & ~C",
        prime_implicants=[{"type": "Quad (4)", "cells": [0, 1, 4, 5], "term": "~A & ~C"}]
    )
    assert kmap_res["status"] == "success"
    assert kmap_res["solution_id"] > 0

    kmaps = engine.get_kmap_solutions("2023MITEC042")
    assert len(kmaps) >= 1
    assert kmaps[0]["sop_expression"] == "~A & ~C"
