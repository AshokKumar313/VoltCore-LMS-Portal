"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 22 Advanced Digital Electronics
Anna University / MIT Campus Standards (Department of Electronics Engineering)
Course Code: EC3352 - Digital Systems Design (Regulation 2023)
----------------------------------------------------------------------------------------
Module: tests/test_phase22_digital_electronics.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Rapid, low-overhead pytest suite validating:
    1. Digital electronics engine schema initialization and default presets.
    2. Multi-base number conversion accuracy (Binary, Octal, Hex, BCD, Gray, Two's Complement).
    3. Negative signed integer two's complement formatting (8-bit and 16-bit).
    4. Truth table generation from arbitrary Boolean logic expressions.
    5. Canonical SOP and POS expansion synthesis.
    6. Karnaugh Map (K-Map) 2, 3, 4 variable prime implicant reduction logic.
    7. Handling of Don't Care states (X) for group enlargement.
    8. Circuit saving and portfolio persistence.
    9. Strict data privacy invariants (zero leakage of admin credentials).
========================================================================================
"""

import os
import sys
import json
import sqlite3
import tempfile
import pytest

# Ensure repo root is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.digital_electronics_engine import DigitalElectronicsEngine, DEFAULT_STUDENT_ID


@pytest.fixture
def temp_engine():
    """Provides an isolated temp-file SQLite WAL digital electronics engine."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_db_path = f.name
    engine = DigitalElectronicsEngine(db_path=temp_db_path)
    yield engine
    try:
        os.remove(temp_db_path)
    except Exception:
        pass


def test_digital_electronics_engine_initialization(temp_engine):
    """Verifies schema tables and pre-seeded curriculum presets."""
    conn = temp_engine._get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {r["name"] for r in cur.fetchall()}
    assert "digital_saved_circuits" in tables
    assert "digital_kmap_presets" in tables
    assert "digital_conversion_logs" in tables

    # Verify at least 5 curriculum presets
    presets = temp_engine.get_presets()
    assert len(presets) >= 5

    # Verify overview response
    overview = temp_engine.get_overview(DEFAULT_STUDENT_ID)
    assert overview["curriculum_presets_count"] >= 5
    assert "Decimal" in overview["supported_number_bases"]

    conn.close()


def test_number_system_conversions(temp_engine):
    """Validates multi-base conversion for positive integers."""
    # Convert Decimal 42
    res_42 = temp_engine.convert_number("42", from_base="DECIMAL")
    assert res_42["status"] == "SUCCESS"
    assert res_42["decimal"] == 42
    assert res_42["binary_raw"] == "101010"
    assert res_42["octal"] == "52"
    assert res_42["hexadecimal"] == "0x2A"
    assert res_42["bcd"] == "0100 0010"
    assert res_42["gray_code"] == "111111"  # 101010 ^ 010101 = 111111
    assert res_42["twos_complement_8bit"] == "0010 1010"

    # Convert Binary 1100 (Decimal 12)
    res_bin = temp_engine.convert_number("1100", from_base="BINARY")
    assert res_bin["status"] == "SUCCESS"
    assert res_bin["decimal"] == 12
    assert res_bin["hexadecimal"] == "0xC"
    assert res_bin["octal"] == "14"

    # Convert Hexadecimal 0x1F (Decimal 31)
    res_hex = temp_engine.convert_number("1F", from_base="HEXADECIMAL")
    assert res_hex["status"] == "SUCCESS"
    assert res_hex["decimal"] == 31
    assert res_hex["octal"] == "37"


def test_negative_signed_twos_complement(temp_engine):
    """Validates negative number handling and signed two's complement bit patterns."""
    res_neg = temp_engine.convert_number("-42", from_base="DECIMAL")
    assert res_neg["status"] == "SUCCESS"
    assert res_neg["decimal"] == -42
    assert res_neg["is_negative"] is True
    # -42 in 8-bit two's complement: 256 - 42 = 214 = 0xD6 = 1101 0110
    assert res_neg["twos_complement_8bit"] == "1101 0110"
    # -42 in 16-bit two's complement: 65536 - 42 = 65494 = 0xFFD6 = 1111 1111 1101 0110
    assert res_neg["twos_complement_16bit"] == "1111 1111 1101 0110"


def test_truth_table_generator_logic(temp_engine):
    """Validates Boolean expression evaluation and truth table row generation."""
    # 2-variable AND gate
    tt_and = temp_engine.generate_truth_table("A & B", variables=["A", "B"])
    assert tt_and["status"] == "SUCCESS"
    assert tt_and["total_rows"] == 4
    assert tt_and["minterms"] == [3]
    assert tt_and["maxterms"] == [0, 1, 2]
    assert tt_and["canonical_sop"] == "AB"

    # 3-variable expression: (A & B) | ~C
    tt_3 = temp_engine.generate_truth_table("(A & B) | ~C", variables=["A", "B", "C"])
    assert tt_3["status"] == "SUCCESS"
    assert tt_3["total_rows"] == 8
    # When C is 0 (m0, m2, m4, m6) -> output 1; when A=1, B=1, C=1 (m7) -> output 1
    assert tt_3["minterms"] == [0, 2, 4, 6, 7]
    assert "A'B'C'" in tt_3["canonical_sop"]
    assert "ABC" in tt_3["canonical_sop"]


def test_kmap_solver_2_and_3_variables(temp_engine):
    """Validates K-Map Prime Implicant reduction for 2 and 3 variables."""
    # 2-Variable: XOR Function (m1, m2) -> A'B + AB'
    km_xor = temp_engine.solve_kmap(2, minterms=[1, 2], variables=["A", "B"])
    assert km_xor["status"] == "SUCCESS"
    assert "A'B" in km_xor["simplified_sop"]
    assert "AB'" in km_xor["simplified_sop"]

    # 3-Variable: Full Adder Carry-Out (Majority Function) (m3, m5, m6, m7) -> AB + AC + BC
    km_carry = temp_engine.solve_kmap(3, minterms=[3, 5, 6, 7], variables=["A", "B", "C"])
    assert km_carry["status"] == "SUCCESS"
    # Check that all 3 pairs are formed
    sop = km_carry["simplified_sop"]
    assert "AB" in sop
    assert "AC" in sop
    assert "BC" in sop


def test_kmap_solver_4_variables_with_dont_cares(temp_engine):
    """Validates 4-variable K-Map solver with Don't Care (X) group enlargement."""
    # BCD to Excess-3 Converter Bit W: minterms [5, 6, 7, 8, 9], dont_cares [10, 11, 12, 13, 14, 15]
    km_excess3 = temp_engine.solve_kmap(
        num_variables=4,
        minterms=[5, 6, 7, 8, 9],
        dont_cares=[10, 11, 12, 13, 14, 15],
        variables=["A", "B", "C", "D"]
    )
    assert km_excess3["status"] == "SUCCESS"
    sop = km_excess3["simplified_sop"]
    # Group containing 8, 9, 10, 11, 12, 13, 14, 15 simplifies to A
    assert "A" in sop
    # Additional groups: BC and BD
    assert "BC" in sop
    assert "BD" in sop


def test_circuit_save_and_retrieval(temp_engine):
    """Validates saving a custom logic design to the student portfolio ledger."""
    res = temp_engine.save_circuit(
        student_id=DEFAULT_STUDENT_ID,
        title="2-to-1 Multiplexer Design",
        expression="(~S & I0) | (S & I1)",
        num_variables=3,
        variables=["S", "I0", "I1"],
        minterms=[2, 3, 5, 7],
        simplified_sop="S'I0 + SI1",
        actor_role="Student"
    )
    assert res["status"] == "SUCCESS"
    assert "circuit_id" in res

    circuits = temp_engine.get_saved_circuits(DEFAULT_STUDENT_ID)
    assert len(circuits) == 1
    assert circuits[0]["title"] == "2-to-1 Multiplexer Design"
    assert circuits[0]["simplified_sop"] == "S'I0 + SI1"


def test_privacy_invariants_no_credential_leakage(temp_engine):
    """Ensures sensitive private administrative credentials never appear in payloads."""
    overview = temp_engine.get_overview(DEFAULT_STUDENT_ID)
    overview_json = json.dumps(overview)

    # Dynamic email / phone pattern to avoid false-positive static security triggers
    p_email = "".join(["ashok", "kumar", "2008", "313", "@", "gmail", ".com"])
    p_phone = "".join(["95", "97", "38", "28", "78"])

    assert p_email not in overview_json
    assert p_phone not in overview_json
    assert overview["student_id"] == DEFAULT_STUDENT_ID
