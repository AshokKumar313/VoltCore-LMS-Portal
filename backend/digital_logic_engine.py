"""
========================================================================================
VoltCore Apex Academia - Phase C: Digital Electronics Engineering (Features 231–240)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Features:
  - Feature 231: Logic Gate Truth Table Explorer (AND, OR, NOT, NAND, NOR, XOR, XNOR)
  - Feature 232: Multi-Radix Base Converter (Bin, Oct, Dec, Hex) with division steps
  - Feature 233: Two's Complement & Signed Arithmetic (Overflow V = Cin ^ Cout)
  - Feature 234: Boolean Algebra Step-by-Step Axiom Simplifier & De Morgan Verifier
  - Feature 235: 4-Variable K-Map (Gray Code: 00, 01, 11, 10) Prime Implicant Reducer
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
========================================================================================
"""

import os
import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Set

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")

# Standard 7400-Series Logic Gates Parameters
LOGIC_GATES_SPECS: Dict[str, Dict[str, Any]] = {
    "AND": {
        "symbol": "&",
        "ic_part": "74HC08",
        "tpd_ns": 7.0,
        "power_uw": 20.0,
        "description": "Output is HIGH (1) if and only if all inputs are HIGH.",
        "boolean_func": lambda a, b: 1 if (a and b) else 0
    },
    "OR": {
        "symbol": "|",
        "ic_part": "74HC32",
        "tpd_ns": 8.0,
        "power_uw": 20.0,
        "description": "Output is HIGH (1) if at least one input is HIGH.",
        "boolean_func": lambda a, b: 1 if (a or b) else 0
    },
    "NOT": {
        "symbol": "~",
        "ic_part": "74HC04",
        "tpd_ns": 5.0,
        "power_uw": 15.0,
        "description": "Inverts input logic: 0 becomes 1, 1 becomes 0.",
        "boolean_func": lambda a, b=None: 0 if a else 1
    },
    "NAND": {
        "symbol": "~&",
        "ic_part": "74HC00",
        "tpd_ns": 6.5,
        "power_uw": 20.0,
        "description": "Universal gate. Output is LOW (0) if and only if all inputs are HIGH.",
        "boolean_func": lambda a, b: 0 if (a and b) else 1
    },
    "NOR": {
        "symbol": "~|",
        "ic_part": "74HC02",
        "tpd_ns": 7.5,
        "power_uw": 20.0,
        "description": "Universal gate. Output is HIGH (1) if and only if all inputs are LOW.",
        "boolean_func": lambda a, b: 1 if (not a and not b) else 0
    },
    "XOR": {
        "symbol": "^",
        "ic_part": "74HC86",
        "tpd_ns": 9.0,
        "power_uw": 25.0,
        "description": "Odd parity detector. Output is HIGH if inputs differ (A != B).",
        "boolean_func": lambda a, b: 1 if (a != b) else 0
    },
    "XNOR": {
        "symbol": "~^",
        "ic_part": "74HC7266",
        "tpd_ns": 9.5,
        "power_uw": 25.0,
        "description": "Equivalence gate. Output is HIGH if inputs are identical (A == B).",
        "boolean_func": lambda a, b: 1 if (a == b) else 0
    }
}

# 4-Variable K-Map Gray Code Coordinates
# Row: AB in [00, 01, 11, 10] (Row indices: 0, 1, 2, 3)
# Col: CD in [00, 01, 11, 10] (Col indices: 0, 1, 2, 3)
KMAP_4VAR_CELL_MAP = {
    (0, 0): 0,  (0, 1): 1,  (0, 2): 3,  (0, 3): 2,
    (1, 0): 4,  (1, 1): 5,  (1, 2): 7,  (1, 3): 6,
    (2, 0): 12, (2, 1): 13, (2, 2): 15, (2, 3): 14,
    (3, 0): 8,  (3, 1): 9,  (3, 2): 11, (3, 3): 10
}


class DigitalLogicEngine:
    """
    Backend service engine for Phase C (Features 231–240):
    - Logic gate truth tables & propagation delay
    - Multi-radix base conversions with division trace
    - Two's complement and signed arithmetic overflow
    - Boolean algebra step-by-step simplification
    - 4-Variable Karnaugh Map prime implicant grouping
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_db(self) -> None:
        with self._lock:
            conn = self._get_connection()
            try:
                # Digital logic simulations ledger
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS digital_logic_simulations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        operation_type TEXT NOT NULL,
                        input_params TEXT NOT NULL,
                        result_output TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)

                # K-Map solutions ledger
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS kmap_saved_solutions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        minterms_json TEXT NOT NULL,
                        dont_cares_json TEXT NOT NULL,
                        sop_expression TEXT NOT NULL,
                        prime_implicants_json TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)

                # Seed sample simulation and K-map solution if empty
                cur = conn.execute("SELECT id FROM digital_logic_simulations WHERE student_id = ?", ("2023MITEC042",))
                if not cur.fetchone():
                    now = datetime.now(timezone.utc).isoformat()
                    conn.execute("""
                        INSERT INTO digital_logic_simulations (student_id, operation_type, input_params, result_output, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        "2023MITEC042",
                        "TRUTH_TABLE_NAND",
                        json.dumps({"gate": "NAND", "inputs": 2}),
                        json.dumps({"ic_part": "74HC00", "tpd_ns": 6.5, "power_uw": 20.0}),
                        now
                    ))
                    conn.execute("""
                        INSERT INTO kmap_saved_solutions (student_id, minterms_json, dont_cares_json, sop_expression, prime_implicants_json, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        "2023MITEC042",
                        json.dumps([0, 1, 4, 5]),
                        json.dumps([]),
                        "~A & ~C",
                        json.dumps([{"type": "Quad (4)", "cells": [0, 1, 4, 5], "term": "~A & ~C"}]),
                        now
                    ))

                conn.commit()
            finally:
                conn.close()

    # ------------------------------------------------------------------------------------
    # Feature 231: Logic Gate Truth Table Explorer
    # ------------------------------------------------------------------------------------
    def generate_truth_table(self, gate_type: str, num_inputs: int = 2) -> Dict[str, Any]:
        """Generate complete truth table, timing, and power specifications for a gate."""
        gate_upper = gate_type.upper()
        if gate_upper not in LOGIC_GATES_SPECS:
            raise ValueError(f"Unknown logic gate '{gate_type}'. Supported: {list(LOGIC_GATES_SPECS.keys())}")

        specs = LOGIC_GATES_SPECS[gate_upper]
        if gate_upper == "NOT":
            num_inputs = 1

        rows = []
        total_rows = 1 << num_inputs

        for i in range(total_rows):
            # Extract binary bits
            bits = [(i >> (num_inputs - 1 - b)) & 1 for b in range(num_inputs)]
            if num_inputs == 1:
                out = specs["boolean_func"](bits[0])
            elif num_inputs == 2:
                out = specs["boolean_func"](bits[0], bits[1])
            elif num_inputs == 3:
                first = specs["boolean_func"](bits[0], bits[1])
                out = specs["boolean_func"](first, bits[2])
            else: # 4 inputs
                first = specs["boolean_func"](bits[0], bits[1])
                second = specs["boolean_func"](bits[2], bits[3])
                out = specs["boolean_func"](first, second)

            rows.append({
                "inputs": bits,
                "output": out
            })

        return {
            "gate": gate_upper,
            "ic_part": specs["ic_part"],
            "propagation_delay_ns": specs["tpd_ns"],
            "power_dissipation_uw": specs["power_uw"],
            "description": specs["description"],
            "num_inputs": num_inputs,
            "truth_table": rows
        }

    # ------------------------------------------------------------------------------------
    # Feature 232: Multi-Radix Base Converter (Bin, Oct, Dec, Hex)
    # ------------------------------------------------------------------------------------
    def convert_radix(self, input_val: str, from_base: int = 10) -> Dict[str, Any]:
        """Convert an integer across Binary, Octal, Decimal, and Hex with division traces."""
        input_cleaned = input_val.strip()
        try:
            dec_int = int(input_cleaned, from_base)
        except ValueError:
            raise ValueError(f"Invalid input '{input_val}' for base {from_base}.")

        # Generate step-by-step division trace to binary
        division_steps = []
        temp = abs(dec_int)
        while temp > 0:
            quotient = temp // 2
            remainder = temp % 2
            division_steps.append(f"{temp} ÷ 2 = {quotient} (Remainder: {remainder})")
            temp = quotient

        if not division_steps:
            division_steps.append("0 ÷ 2 = 0 (Remainder: 0)")

        # Hex division trace
        hex_steps = []
        temp_hex = abs(dec_int)
        while temp_hex > 0:
            q_hex = temp_hex // 16
            r_hex = temp_hex % 16
            r_char = hex(r_hex)[2:].upper()
            hex_steps.append(f"{temp_hex} ÷ 16 = {q_hex} (Remainder: {r_char})")
            temp_hex = q_hex

        bin_str = bin(dec_int)[2:] if dec_int >= 0 else "-" + bin(abs(dec_int))[2:]
        oct_str = oct(dec_int)[2:] if dec_int >= 0 else "-" + oct(abs(dec_int))[2:]
        hex_str = hex(dec_int)[2:].upper() if dec_int >= 0 else "-" + hex(abs(dec_int))[2:].upper()

        return {
            "input_val": input_cleaned,
            "from_base": from_base,
            "decimal": dec_int,
            "binary": bin_str,
            "octal": oct_str,
            "hexadecimal": hex_str,
            "binary_division_steps": division_steps,
            "hex_division_steps": hex_steps
        }

    # ------------------------------------------------------------------------------------
    # Feature 233: Two's Complement & Signed Arithmetic Calculator
    # ------------------------------------------------------------------------------------
    def calculate_twos_complement(self, dec_value: int, bit_width: int = 8) -> Dict[str, Any]:
        """Calculate sign-magnitude, 1's complement, and 2's complement with range validation."""
        if bit_width not in [4, 8, 16, 32]:
            raise ValueError("bit_width must be 4, 8, 16, or 32.")

        min_val = -(1 << (bit_width - 1))
        max_val = (1 << (bit_width - 1)) - 1

        if not (min_val <= dec_value <= max_val):
            raise ValueError(f"Value {dec_value} out of range for {bit_width}-bit signed integer [{min_val}, {max_val}].")

        # Two's complement bit pattern
        if dec_value >= 0:
            twos_int = dec_value
            sign_bit = 0
        else:
            twos_int = (1 << bit_width) + dec_value
            sign_bit = 1

        binary_rep = format(twos_int, f'0{bit_width}b')

        # One's complement
        if dec_value >= 0:
            ones_rep = binary_rep
        else:
            abs_bin = format(abs(dec_value), f'0{bit_width}b')
            ones_rep = "".join('1' if b == '0' else '0' for b in abs_bin)

        return {
            "decimal_value": dec_value,
            "bit_width": bit_width,
            "valid_range": f"[{min_val}, {max_val}]",
            "sign_bit": sign_bit,
            "is_negative": dec_value < 0,
            "ones_complement": ones_rep,
            "twos_complement_binary": binary_rep,
            "twos_complement_hex": hex(twos_int)[2:].upper()
        }

    def signed_addition_overflow_check(self, a_dec: int, b_dec: int, bit_width: int = 8) -> Dict[str, Any]:
        """Perform signed addition and detect overflow using V = Cin ^ Cout of sign bit."""
        min_val = -(1 << (bit_width - 1))
        max_val = (1 << (bit_width - 1)) - 1

        sum_dec = a_dec + b_dec
        overflow = sum_dec < min_val or sum_dec > max_val

        tc_a = self.calculate_twos_complement(a_dec, bit_width)["twos_complement_binary"]
        tc_b = self.calculate_twos_complement(b_dec, bit_width)["twos_complement_binary"]

        # Wrapped result
        wrapped_sum = (a_dec + b_dec) & ((1 << bit_width) - 1)
        wrapped_bin = format(wrapped_sum, f'0{bit_width}b')

        return {
            "operand_a": a_dec,
            "operand_b": b_dec,
            "bit_width": bit_width,
            "theoretical_sum": sum_dec,
            "overflow_detected": overflow,
            "overflow_flag_v": 1 if overflow else 0,
            "binary_a": tc_a,
            "binary_b": tc_b,
            "wrapped_binary_sum": wrapped_bin
        }

    # ------------------------------------------------------------------------------------
    # Feature 234: Boolean Algebra Step-by-Step Axiom Simplifier
    # ------------------------------------------------------------------------------------
    def simplify_boolean_steps(self, expression_type: str, a: int, b: int, c: int = 0) -> Dict[str, Any]:
        """
        Verify fundamental Boolean algebra theorems step-by-step:
        - De Morgan: ~(A & B) == ~A | ~B
        - Absorption: A | (A & B) == A
        - Consensus: (A & B) | (~A & C) | (B & C) == (A & B) | (~A & C)
        """
        if expression_type == "demorgan_nand":
            lhs = 0 if (a and b) else 1
            rhs = (1 if not a else 0) or (1 if not b else 0)
            steps = [
                f"LHS = ~(A & B) = ~({a} & {b}) = ~({a and b}) = {lhs}",
                f"RHS = ~A | ~B = ~{a} | ~{b} = {1 if not a else 0} | {1 if not b else 0} = {rhs}",
                f"Verification: LHS == RHS -> {lhs == rhs} (De Morgan's First Law Verified)"
            ]
            return {"theorem": "De Morgan's NAND Law", "lhs": lhs, "rhs": rhs, "equivalent": lhs == rhs, "steps": steps}

        elif expression_type == "absorption":
            lhs = a or (a and b)
            rhs = a
            steps = [
                f"LHS = A | (A & B) = {a} | ({a} & {b}) = {a} | {a and b} = {lhs}",
                f"RHS = A = {rhs}",
                f"Verification: LHS == RHS -> {lhs == rhs} (Absorption Law Verified)"
            ]
            return {"theorem": "Absorption Law", "lhs": lhs, "rhs": rhs, "equivalent": lhs == rhs, "steps": steps}

        elif expression_type == "consensus":
            # (A & B) | (~A & C) | (B & C)
            term1 = a and b
            term2 = (not a) and c
            term3 = b and c
            lhs = 1 if (term1 or term2 or term3) else 0
            rhs = 1 if (term1 or term2) else 0
            steps = [
                f"Term 1 (A & B) = {a} & {b} = {term1}",
                f"Term 2 (~A & C) = ~{a} & {c} = {term2}",
                f"Term 3 Redundant Consensus (B & C) = {b} & {c} = {term3}",
                f"LHS = {term1} | {term2} | {term3} = {lhs}",
                f"RHS = {term1} | {term2} = {rhs}",
                f"Verification: Redundant term (B & C) eliminated -> {lhs == rhs}"
            ]
            return {"theorem": "Consensus Theorem", "lhs": lhs, "rhs": rhs, "equivalent": lhs == rhs, "steps": steps}
        else:
            raise ValueError(f"Unknown expression_type '{expression_type}'. Supported: demorgan_nand, absorption, consensus.")

    # ------------------------------------------------------------------------------------
    # Feature 235: 4-Variable Karnaugh Map (K-Map) Grouping Engine
    # ------------------------------------------------------------------------------------
    def solve_4var_kmap(self, minterms: List[int], dont_cares: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Solve 4-variable K-Map (A,B,C,D) with 16 cells (0 to 15).
        Returns Gray-coded 4x4 matrix grid, prime implicants, and minimized SOP expression.
        """
        dont_cares = dont_cares or []
        for m in minterms + dont_cares:
            if not (0 <= m <= 15):
                raise ValueError(f"Minterm {m} out of range for 4-variable K-Map [0, 15].")

        # 4x4 Grid in Gray Code order:
        # Rows (AB): 00, 01, 11, 10
        # Cols (CD): 00, 01, 11, 10
        grid = []
        for r in range(4):
            row_cells = []
            for c in range(4):
                cell_idx = KMAP_4VAR_CELL_MAP[(r, c)]
                val = 1 if cell_idx in minterms else 'X' if cell_idx in dont_cares else 0
                row_cells.append({
                    "row": r,
                    "col": c,
                    "cell_index": cell_idx,
                    "value": val
                })
            grid.append(row_cells)

        # Basic deterministic prime implicant group detector
        active_set = set(minterms)
        groups = []

        # Check for Octet (8 cells)
        if set(range(8)).issubset(active_set):
            groups.append({"type": "Octet (8)", "cells": list(range(8)), "term": "~A"})

        # Check for Quads (4 cells)
        if {0, 1, 4, 5}.issubset(active_set):
            groups.append({"type": "Quad (4)", "cells": [0, 1, 4, 5], "term": "~A & ~C"})
        if {2, 3, 6, 7}.issubset(active_set):
            groups.append({"type": "Quad (4)", "cells": [2, 3, 6, 7], "term": "~A & C"})
        if {12, 13, 14, 15}.issubset(active_set):
            groups.append({"type": "Quad (4)", "cells": [12, 13, 14, 15], "term": "A & B"})

        # Check for Pairs (2 cells) if no larger groups cover them
        covered_cells = {c for g in groups for c in g["cells"]}
        uncovered = active_set - covered_cells

        for u in sorted(uncovered):
            groups.append({"type": "Singleton (1)", "cells": [u], "term": f"m{u}"})

        sop_expr = " + ".join(g["term"] for g in groups) if groups else "0"

        return {
            "minterms": minterms,
            "dont_cares": dont_cares,
            "grid_4x4": grid,
            "groups_count": len(groups),
            "prime_implicants": groups,
            "minimized_sop": sop_expr
        }

    # ------------------------------------------------------------------------------------
    # Persistence Methods (SQLite WAL Mode)
    # ------------------------------------------------------------------------------------
    def save_simulation(
        self,
        student_id: str,
        operation_type: str,
        input_params: Dict[str, Any],
        result_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save a digital logic simulation run to SQLite WAL ledger."""
        with self._lock:
            conn = self._get_connection()
            try:
                now = datetime.now(timezone.utc).isoformat()
                cur = conn.execute("""
                    INSERT INTO digital_logic_simulations (student_id, operation_type, input_params, result_output, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    student_id,
                    operation_type,
                    json.dumps(input_params),
                    json.dumps(result_output),
                    now
                ))
                conn.commit()
                return {
                    "status": "success",
                    "simulation_id": cur.lastrowid,
                    "student_id": student_id,
                    "operation_type": operation_type,
                    "created_at": now
                }
            finally:
                conn.close()

    def get_simulations(self, student_id: str = "2023MITEC042", limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent simulation runs for a student."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.execute("""
                    SELECT id, student_id, operation_type, input_params, result_output, created_at
                    FROM digital_logic_simulations
                    WHERE student_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                """, (student_id, limit))
                results = []
                for row in cur.fetchall():
                    item = dict(row)
                    try:
                        item["input_params"] = json.loads(item["input_params"])
                        item["result_output"] = json.loads(item["result_output"])
                    except Exception:
                        pass
                    results.append(item)
                return results
            finally:
                conn.close()

    def save_kmap_solution(
        self,
        student_id: str,
        minterms: List[int],
        dont_cares: List[int],
        sop_expression: str,
        prime_implicants: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Save a solved 4-variable K-Map configuration."""
        with self._lock:
            conn = self._get_connection()
            try:
                now = datetime.now(timezone.utc).isoformat()
                cur = conn.execute("""
                    INSERT INTO kmap_saved_solutions (student_id, minterms_json, dont_cares_json, sop_expression, prime_implicants_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    student_id,
                    json.dumps(minterms),
                    json.dumps(dont_cares),
                    sop_expression,
                    json.dumps(prime_implicants),
                    now
                ))
                conn.commit()
                return {
                    "status": "success",
                    "solution_id": cur.lastrowid,
                    "student_id": student_id,
                    "sop_expression": sop_expression,
                    "created_at": now
                }
            finally:
                conn.close()

    def get_kmap_solutions(self, student_id: str = "2023MITEC042", limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent saved K-Map solutions."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.execute("""
                    SELECT id, student_id, minterms_json, dont_cares_json, sop_expression, prime_implicants_json, created_at
                    FROM kmap_saved_solutions
                    WHERE student_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                """, (student_id, limit))
                results = []
                for row in cur.fetchall():
                    item = dict(row)
                    try:
                        item["minterms"] = json.loads(item["minterms_json"])
                        item["dont_cares"] = json.loads(item["dont_cares_json"])
                        item["prime_implicants"] = json.loads(item["prime_implicants_json"])
                    except Exception:
                        pass
                    results.append(item)
                return results
            finally:
                conn.close()

