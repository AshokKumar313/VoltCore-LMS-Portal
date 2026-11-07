"""
========================================================================================
VoltCore Apex Academia - SystemVerilog Verification & ASIC Physical Design Studio
Phase 20: SVA Assertion Analyzer, Floorplanning, Congestion Heatmaps, Elmore Interconnect & CTS
Lead VLSI Architect & Digital Verification Specialist: Ashok Kumar A
========================================================================================
Features:
  1. SystemVerilog Assertion (SVA) Verification Engine:
     - Immediate assertions: 'assert (expr)' procedural checking.
     - Concurrent assertions: 'assert property (@(posedge clk) disable iff (rst) expr)'.
     - Temporal sequences and sampled value functions: $rose(sig), $fell(sig), $past(sig, k),
       $stable(sig), $onehot(sig), temporal delays ##n and ##[min:max].
     - Implication operators: Overlapping (|->) and Non-overlapping (|=> / ##1).
     - Full SVA coverage telemetry: attempts, matches, failures, vacuous passes, and coverage %.
  2. ASIC Physical Design Explorer:
     - Floorplanning dimensioning: Standard cell area, target utilization, core width/height,
       aspect ratio, die margins, I/O ring perimeter, and pad density.
     - Placement Congestion Heatmap: 2D mesh grid discretization with Rent's rule spatial
       clustering, hotspot detection (> 0.85), routing demand vs. capacity analysis.
     - Interconnect Elmore Distributed RC Delay: Wire resistance and capacitance per technology node
       (7nm, 14nm, 28nm, 45nm, 65nm, 180nm), optimal repeater/buffer insertion pitch L_opt.
     - Clock Tree Synthesis (CTS) Modeling: Symmetric H-tree depth, clock insertion latency,
       skew Delta t_skew, random/deterministic jitter, setup/hold slack margin timing closure.
  3. SQLite WAL Mode Persistence:
     - Logged in table 'vlsi_physical_design_history' in voltcore_telemetry.db.
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU usage (<5%).
========================================================================================
"""

import os
import re
import math
import json
import time
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Union

try:
    from backend.safe_expression_parser import SafeExpressionParser
except ImportError:
    from safe_expression_parser import SafeExpressionParser

import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")

# ========================================================================================
# Technology Node Physical Parameters Database
# ========================================================================================
TECH_NODE_LIBRARY: Dict[str, Dict[str, Any]] = {
    "7nm": {
        "name": "7nm FinFET",
        "node_nm": 7,
        "nand2_cell_area_um2": 0.082,
        "dff_cell_area_um2": 0.42,
        "inv_cell_area_um2": 0.045,
        "metal_layers": 12,
        "r_sheet_m1_ohm_per_um": 1.85,
        "r_sheet_inter_ohm_per_um": 0.95,
        "r_sheet_top_ohm_per_um": 0.12,
        "c_wire_ff_per_um": 0.22,
        "driver_r_ohm": 450.0,
        "sink_c_ff": 0.75,
        "buffer_intrinsic_delay_ps": 8.5,
        "nom_vdd_v": 0.75,
        "max_freq_ghz": 3.8,
    },
    "14nm": {
        "name": "14nm FinFET",
        "node_nm": 14,
        "nand2_cell_area_um2": 0.185,
        "dff_cell_area_um2": 0.92,
        "inv_cell_area_um2": 0.098,
        "metal_layers": 10,
        "r_sheet_m1_ohm_per_um": 0.85,
        "r_sheet_inter_ohm_per_um": 0.42,
        "r_sheet_top_ohm_per_um": 0.065,
        "c_wire_ff_per_um": 0.20,
        "driver_r_ohm": 600.0,
        "sink_c_ff": 1.2,
        "buffer_intrinsic_delay_ps": 12.0,
        "nom_vdd_v": 0.85,
        "max_freq_ghz": 3.2,
    },
    "28nm": {
        "name": "28nm HKMG CMOS",
        "node_nm": 28,
        "nand2_cell_area_um2": 0.46,
        "dff_cell_area_um2": 2.25,
        "inv_cell_area_um2": 0.24,
        "metal_layers": 8,
        "r_sheet_m1_ohm_per_um": 0.40,
        "r_sheet_inter_ohm_per_um": 0.18,
        "r_sheet_top_ohm_per_um": 0.035,
        "c_wire_ff_per_um": 0.18,
        "driver_r_ohm": 900.0,
        "sink_c_ff": 2.0,
        "buffer_intrinsic_delay_ps": 18.0,
        "nom_vdd_v": 1.0,
        "max_freq_ghz": 2.4,
    },
    "45nm": {
        "name": "45nm Bulk CMOS",
        "node_nm": 45,
        "nand2_cell_area_um2": 1.15,
        "dff_cell_area_um2": 5.60,
        "inv_cell_area_um2": 0.62,
        "metal_layers": 7,
        "r_sheet_m1_ohm_per_um": 0.22,
        "r_sheet_inter_ohm_per_um": 0.095,
        "r_sheet_top_ohm_per_um": 0.022,
        "c_wire_ff_per_um": 0.17,
        "driver_r_ohm": 1200.0,
        "sink_c_ff": 3.0,
        "buffer_intrinsic_delay_ps": 26.0,
        "nom_vdd_v": 1.1,
        "max_freq_ghz": 1.8,
    },
    "65nm": {
        "name": "65nm Bulk CMOS",
        "node_nm": 65,
        "nand2_cell_area_um2": 2.20,
        "dff_cell_area_um2": 10.8,
        "inv_cell_area_um2": 1.15,
        "metal_layers": 7,
        "r_sheet_m1_ohm_per_um": 0.15,
        "r_sheet_inter_ohm_per_um": 0.065,
        "r_sheet_top_ohm_per_um": 0.015,
        "c_wire_ff_per_um": 0.16,
        "driver_r_ohm": 1500.0,
        "sink_c_ff": 4.2,
        "buffer_intrinsic_delay_ps": 35.0,
        "nom_vdd_v": 1.2,
        "max_freq_ghz": 1.4,
    },
    "180nm": {
        "name": "180nm Planar CMOS",
        "node_nm": 180,
        "nand2_cell_area_um2": 18.5,
        "dff_cell_area_um2": 85.0,
        "inv_cell_area_um2": 9.2,
        "metal_layers": 5,
        "r_sheet_m1_ohm_per_um": 0.075,
        "r_sheet_inter_ohm_per_um": 0.035,
        "r_sheet_top_ohm_per_um": 0.008,
        "c_wire_ff_per_um": 0.15,
        "driver_r_ohm": 2500.0,
        "sink_c_ff": 8.5,
        "buffer_intrinsic_delay_ps": 95.0,
        "nom_vdd_v": 1.8,
        "max_freq_ghz": 0.5,
    },
}


# ========================================================================================
# 1. SystemVerilog Assertion (SVA) Verification Engine
# ========================================================================================
class SystemVerilogAssertionAnalyzer:
    """
    Parses and verifies SystemVerilog Assertions (immediate and concurrent)
    over cycle-accurate simulation traces. Computes formal coverage metrics:
    attempts, non-vacuous matches, failures, vacuous passes, and assertion coverage %.
    """

    def __init__(self) -> None:
        pass

    def evaluate_expression_at_cycle(
        self,
        expr_str: str,
        trace: Dict[str, List[Any]],
        cycle: int,
    ) -> bool:
        """
        Evaluates a boolean condition or sampled function at a given cycle index.
        Supports:
          - $rose(sig): sig[cycle] == 1 and (cycle == 0 or sig[cycle-1] == 0)
          - $fell(sig): sig[cycle] == 0 and (cycle > 0 and sig[cycle-1] == 1)
          - $stable(sig): cycle > 0 and sig[cycle] == sig[cycle-1]
          - $past(sig, k=1): sig[cycle - k] if cycle >= k else 0
          - $onehot(sig): exactly one bit set in integer or bit list
          - Arithmetic/Boolean logic: ==, !=, >=, <=, >, <, &&, ||, !
        """
        clean_expr = expr_str.strip()

        # Handle $rose(sig)
        rose_match = re.search(r"\$rose\s*\(\s*([a-zA-Z0-9_]+)\s*\)", clean_expr)
        if rose_match:
            sig = rose_match.group(1)
            sig_val = trace.get(sig, [])
            curr = 1 if (cycle < len(sig_val) and sig_val[cycle]) else 0
            prev = 1 if (cycle > 0 and cycle - 1 < len(sig_val) and sig_val[cycle - 1]) else 0
            res = (curr == 1 and prev == 0)
            clean_expr = clean_expr.replace(rose_match.group(0), "True" if res else "False")

        # Handle $fell(sig)
        fell_match = re.search(r"\$fell\s*\(\s*([a-zA-Z0-9_]+)\s*\)", clean_expr)
        if fell_match:
            sig = fell_match.group(1)
            sig_val = trace.get(sig, [])
            curr = 1 if (cycle < len(sig_val) and sig_val[cycle]) else 0
            prev = 1 if (cycle > 0 and cycle - 1 < len(sig_val) and sig_val[cycle - 1]) else 0
            res = (curr == 0 and prev == 1)
            clean_expr = clean_expr.replace(fell_match.group(0), "True" if res else "False")

        # Handle $stable(sig)
        stable_match = re.search(r"\$stable\s*\(\s*([a-zA-Z0-9_]+)\s*\)", clean_expr)
        if stable_match:
            sig = stable_match.group(1)
            sig_val = trace.get(sig, [])
            if cycle > 0 and cycle < len(sig_val):
                res = (sig_val[cycle] == sig_val[cycle - 1])
            else:
                res = True
            clean_expr = clean_expr.replace(stable_match.group(0), "True" if res else "False")

        # Handle $past(sig, k)
        past_match = re.search(r"\$past\s*\(\s*([a-zA-Z0-9_]+)(?:\s*,\s*(\d+))?\s*\)", clean_expr)
        if past_match:
            sig = past_match.group(1)
            k = int(past_match.group(2)) if past_match.group(2) else 1
            sig_val = trace.get(sig, [])
            past_idx = cycle - k
            val = sig_val[past_idx] if (past_idx >= 0 and past_idx < len(sig_val)) else 0
            clean_expr = clean_expr.replace(past_match.group(0), str(val))

        # Handle $onehot(sig)
        onehot_match = re.search(r"\$onehot\s*\(\s*([a-zA-Z0-9_]+)\s*\)", clean_expr)
        if onehot_match:
            sig = onehot_match.group(1)
            sig_val = trace.get(sig, [])
            val = int(sig_val[cycle]) if (cycle < len(sig_val) and sig_val[cycle] is not None) else 0
            res = (val > 0) and ((val & (val - 1)) == 0)
            clean_expr = clean_expr.replace(onehot_match.group(0), "True" if res else "False")

        # Replace SystemVerilog operators with Python operators
        clean_expr = re.sub(r"&&", " and ", clean_expr)
        clean_expr = re.sub(r"\|\|", " or ", clean_expr)
        clean_expr = re.sub(r"!(?!=)", " not ", clean_expr)

        # Substitute signal names with values at current cycle
        tokens = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", clean_expr)
        for token in set(tokens):
            if token in ("True", "False", "and", "or", "not"):
                continue
            if token in trace:
                val = trace[token][cycle] if cycle < len(trace[token]) else 0
                # If bool/int
                if isinstance(val, bool):
                    val_str = "True" if val else "False"
                else:
                    val_str = str(int(val))
                clean_expr = re.sub(rf"\b{token}\b", val_str, clean_expr)

        try:
            # Safe evaluation of boolean expressions via strict AST whitelist (zero eval/exec)
            res = SafeExpressionParser.evaluate(clean_expr, allow_math_funcs=False)
            return bool(res)
        except Exception:
            return False

    def parse_assertion(self, assertion_str: str) -> Dict[str, Any]:
        """
        Parses an SVA assertion string into structured components.
        Supports immediate 'assert (cond)' and concurrent properties:
        'assert property (@(posedge clk) disable iff (rst) req |-> ##[1:3] gnt);'
        """
        raw = assertion_str.strip().rstrip(";")
        res: Dict[str, Any] = {
            "raw_str": assertion_str,
            "type": "immediate",
            "name": "",
            "clock": "clk",
            "disable_iff": None,
            "antecedent": "",
            "implication": None,  # '|->' or '|=>'
            "min_delay": 0,
            "max_delay": 0,
            "consequent": "",
        }

        # Check for property label: name: assert property ...
        name_match = re.match(r"^([a-zA-Z0-9_]+)\s*:\s*(.*)", raw)
        if name_match:
            res["name"] = name_match.group(1)
            raw = name_match.group(2).strip()

        # Check if concurrent property
        if "assert property" in raw:
            res["type"] = "concurrent"
            body = re.sub(r"^assert\s+property\s*\(\s*", "", raw)
            body = re.sub(r"\s*\)$", "", body)

            # Clock specifier
            clk_match = re.search(r"@\(\s*posedge\s+([a-zA-Z0-9_]+)\s*\)", body)
            if clk_match:
                res["clock"] = clk_match.group(1)
                body = body.replace(clk_match.group(0), "").strip()

            # Disable iff
            disable_match = re.search(r"disable\s+iff\s*\(([^)]+)\)", body)
            if disable_match:
                res["disable_iff"] = disable_match.group(1).strip()
                body = body.replace(disable_match.group(0), "").strip()

            # Implication operator (|-> or |=>)
            if "|->" in body:
                parts = body.split("|->", 1)
                res["antecedent"] = parts[0].strip()
                res["implication"] = "|->"
                rhs = parts[1].strip()
            elif "|=>" in body:
                parts = body.split("|=>", 1)
                res["antecedent"] = parts[0].strip()
                res["implication"] = "|=>"
                # Non-overlapping implies minimum 1-cycle delay
                rhs = parts[1].strip()
                res["min_delay"] = 1
                res["max_delay"] = 1
            else:
                # Direct property without implication
                res["antecedent"] = body.strip()
                res["consequent"] = body.strip()
                res["implication"] = None
                return res

            # Parse delay in consequent: ##1, ##[1:5], etc.
            range_delay_match = re.match(r"^##\[(\d+)\s*:\s*(\d+)\]\s*(.*)", rhs)
            if range_delay_match:
                base_min = int(range_delay_match.group(1))
                base_max = int(range_delay_match.group(2))
                if res["implication"] == "|=>":
                    res["min_delay"] = base_min + 1
                    res["max_delay"] = base_max + 1
                else:
                    res["min_delay"] = base_min
                    res["max_delay"] = base_max
                res["consequent"] = range_delay_match.group(3).strip()
            else:
                fixed_delay_match = re.match(r"^##(\d+)\s*(.*)", rhs)
                if fixed_delay_match:
                    delay_val = int(fixed_delay_match.group(1))
                    if res["implication"] == "|=>":
                        res["min_delay"] = delay_val + 1
                        res["max_delay"] = delay_val + 1
                    else:
                        res["min_delay"] = delay_val
                        res["max_delay"] = delay_val
                    res["consequent"] = fixed_delay_match.group(2).strip()
                else:
                    res["consequent"] = rhs
                    if res["implication"] == "|=>":
                        res["min_delay"] = 1
                        res["max_delay"] = 1
                    else:
                        res["min_delay"] = 0
                        res["max_delay"] = 0
        else:
            # Immediate assertion: assert (expr)
            imm_match = re.search(r"assert\s*\(\s*(.+?)\s*\)", raw)
            if imm_match:
                res["consequent"] = imm_match.group(1).strip()
                res["antecedent"] = "1"
            else:
                res["consequent"] = raw
                res["antecedent"] = "1"

        return res

    def evaluate_trace(
        self,
        assertions: Union[List[str], List[Dict[str, Any]]],
        trace: Dict[str, List[Any]],
    ) -> Dict[str, Any]:
        """
        Evaluates a set of SVA assertions over a multi-cycle waveform trace.
        Computes formal metrics: attempts, matches, failures, vacuous passes, coverage %.
        """
        # Determine total cycles from longest trace signal
        trace_lengths = [len(v) for v in trace.values() if isinstance(v, list)]
        num_cycles = max(trace_lengths) if trace_lengths else 0

        results: List[Dict[str, Any]] = []
        total_attempts = 0
        total_matches = 0
        total_failures = 0
        total_vacuous = 0

        for idx, item in enumerate(assertions):
            if isinstance(item, str):
                parsed = self.parse_assertion(item)
            else:
                parsed = item

            name = parsed.get("name") or f"assertion_{idx + 1}"
            is_immediate = parsed.get("type") == "immediate"
            disable_cond = parsed.get("disable_iff")
            antecedent_expr = parsed.get("antecedent", "1")
            consequent_expr = parsed.get("consequent", "")
            implication = parsed.get("implication")
            min_delay = parsed.get("min_delay", 0)
            max_delay = parsed.get("max_delay", 0)

            attempts = 0
            matches = 0
            failures = 0
            vacuous_passes = 0
            cycle_log: List[Dict[str, Any]] = []

            for t in range(num_cycles):
                # Check disable condition (e.g. reset active)
                if disable_cond and self.evaluate_expression_at_cycle(disable_cond, trace, t):
                    cycle_log.append({
                        "cycle": t,
                        "status": "DISABLED",
                        "reason": f"Disabled by {disable_cond}",
                    })
                    continue

                if is_immediate:
                    # Immediate assertion evaluated procedurally
                    attempts += 1
                    passed = self.evaluate_expression_at_cycle(consequent_expr, trace, t)
                    if passed:
                        matches += 1
                        status = "PASS"
                    else:
                        failures += 1
                        status = "FAIL"
                    cycle_log.append({
                        "cycle": t,
                        "status": status,
                        "expr": consequent_expr,
                        "result": passed,
                    })
                else:
                    # Concurrent assertion
                    if implication is None:
                        # Direct property check on cycle t
                        attempts += 1
                        passed = self.evaluate_expression_at_cycle(consequent_expr, trace, t)
                        if passed:
                            matches += 1
                            status = "PASS"
                        else:
                            failures += 1
                            status = "FAIL"
                        cycle_log.append({
                            "cycle": t,
                            "status": status,
                            "result": passed,
                        })
                    else:
                        # Implication: antecedent |-> / |=> consequent
                        attempts += 1
                        ante_eval = self.evaluate_expression_at_cycle(antecedent_expr, trace, t)

                        if not ante_eval:
                            # Vacuous pass
                            vacuous_passes += 1
                            cycle_log.append({
                                "cycle": t,
                                "status": "VACUOUS_PASS",
                                "antecedent": False,
                                "consequent": None,
                                "reason": "Antecedent condition false",
                            })
                        else:
                            # Antecedent held! Check consequent over temporal range [t + min_delay, t + max_delay]
                            matched = False
                            for offset in range(min_delay, max_delay + 1):
                                check_cycle = t + offset
                                if check_cycle < num_cycles:
                                    if self.evaluate_expression_at_cycle(consequent_expr, trace, check_cycle):
                                        matched = True
                                        match_cycle = check_cycle
                                        break

                            if matched:
                                matches += 1
                                cycle_log.append({
                                    "cycle": t,
                                    "status": "NON_VACUOUS_MATCH",
                                    "antecedent": True,
                                    "consequent": True,
                                    "matched_at_cycle": match_cycle,
                                })
                            else:
                                failures += 1
                                cycle_log.append({
                                    "cycle": t,
                                    "status": "FAIL",
                                    "antecedent": True,
                                    "consequent": False,
                                    "eval_range": [t + min_delay, t + max_delay],
                                    "reason": f"Consequent '{consequent_expr}' not satisfied in window",
                                })

            coverage_pct = round((matches / attempts * 100.0), 2) if attempts > 0 else 100.0
            vacuous_ratio = round((vacuous_passes / attempts * 100.0), 2) if attempts > 0 else 0.0

            total_attempts += attempts
            total_matches += matches
            total_failures += failures
            total_vacuous += vacuous_passes

            results.append({
                "assertion_name": name,
                "parsed": parsed,
                "attempts": attempts,
                "matches": matches,
                "failures": failures,
                "vacuous_passes": vacuous_passes,
                "assertion_coverage_pct": coverage_pct,
                "vacuous_pass_ratio_pct": vacuous_ratio,
                "cycle_log": cycle_log,
                "passed": failures == 0,
            })

        overall_coverage = round((total_matches / total_attempts * 100.0), 2) if total_attempts > 0 else 100.0

        return {
            "total_cycles_analyzed": num_cycles,
            "total_assertions": len(assertions),
            "total_attempts": total_attempts,
            "total_matches": total_matches,
            "total_failures": total_failures,
            "total_vacuous_passes": total_vacuous,
            "overall_assertion_coverage_pct": overall_coverage,
            "all_passed": total_failures == 0,
            "assertion_reports": results,
        }


# ========================================================================================
# 2. ASIC Physical Design Explorer & Interconnect Engine
# ========================================================================================
class ASICPhysicalDesignEngine:
    """
    Simulates ASIC Physical Design operations:
      - Floorplanning & Die Area Budgeting
      - Placement Congestion & Routing Density Heatmaps
      - Distributed Interconnect Elmore RC Delay with Optimal Buffer Insertion
      - Clock Tree Synthesis (CTS) Latency, Skew, Jitter, and Timing Closure
      - SQLite WAL mode logging in 'vlsi_physical_design_history'.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        self._lock = threading.Lock()
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
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS vlsi_physical_design_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        experiment_id TEXT NOT NULL UNIQUE,
                        operation_type TEXT NOT NULL,
                        tech_node TEXT NOT NULL,
                        gate_count INTEGER,
                        core_utilization REAL,
                        elmore_delay_ps REAL,
                        clock_skew_ps REAL,
                        timing_passed INTEGER,
                        metrics_json TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)
                conn.commit()
            finally:
                conn.close()

    def calculate_floorplan_dimensions(
        self,
        gate_count: int,
        tech_node: str = "28nm",
        target_utilization: float = 0.70,
        aspect_ratio: float = 1.0,
        core_margin_um: float = 20.0,
        io_pad_pitch_um: float = 40.0,
    ) -> Dict[str, Any]:
        """
        Calculates ASIC core and die dimensions, standard cell area, aspect ratio,
        and maximum I/O pad budget.
        """
        tech_info = TECH_NODE_LIBRARY.get(tech_node, TECH_NODE_LIBRARY["28nm"])
        nand2_area = tech_info["nand2_cell_area_um2"]

        # 1 Gate Equivalent (GE) is defined as standard 2-input NAND cell area
        total_cell_area_um2 = gate_count * nand2_area

        target_util = max(0.10, min(0.95, target_utilization))
        core_area_um2 = total_cell_area_um2 / target_util

        # Aspect ratio = Height / Width => H = AR * W => Area = W * (AR * W) = AR * W^2
        ar = max(0.1, min(10.0, aspect_ratio))
        core_width_um = math.sqrt(core_area_um2 / ar)
        core_height_um = core_width_um * ar

        # Die dimensions (adding core-to-die margin on all four boundaries)
        die_width_um = core_width_um + (2.0 * core_margin_um)
        die_height_um = core_height_um + (2.0 * core_margin_um)
        die_area_um2 = die_width_um * die_height_um
        die_area_mm2 = die_area_um2 / 1.0e6

        die_utilization = total_cell_area_um2 / die_area_um2

        # I/O Pad ring calculation along perimeter
        perimeter_um = 2.0 * (die_width_um + die_height_um)
        max_io_pads = int(perimeter_um / max(10.0, io_pad_pitch_um))

        # Yield estimation via Murphy's / Seed's defect density model (D0 = 0.08 defects/cm^2)
        die_area_cm2 = die_area_mm2 / 100.0
        defect_density_d0 = 0.08  # defects per cm^2
        critical_area_ratio = 0.75
        lambda_val = defect_density_d0 * die_area_cm2 * critical_area_ratio
        # Murphy's yield model: Y = ((1 - exp(-lambda)) / lambda)^2
        estimated_yield_pct = 100.0 * (((1.0 - math.exp(-max(1e-6, lambda_val))) / max(1e-6, lambda_val)) ** 2)

        return {
            "technology_node": tech_info["name"],
            "gate_count": gate_count,
            "gate_equivalent_area_um2": nand2_area,
            "total_cell_area_um2": round(total_cell_area_um2, 2),
            "target_utilization": target_util,
            "core_utilization_actual": round(total_cell_area_um2 / (core_width_um * core_height_um), 4),
            "core_width_um": round(core_width_um, 2),
            "core_height_um": round(core_height_um, 2),
            "core_area_um2": round(core_area_um2, 2),
            "aspect_ratio": round(ar, 3),
            "core_margin_um": core_margin_um,
            "die_width_um": round(die_width_um, 2),
            "die_height_um": round(die_height_um, 2),
            "die_area_um2": round(die_area_um2, 2),
            "die_area_mm2": round(die_area_mm2, 4),
            "die_utilization": round(die_utilization, 4),
            "max_io_pad_count": max_io_pads,
            "io_pad_pitch_um": io_pad_pitch_um,
            "estimated_wafer_yield_pct": round(estimated_yield_pct, 2),
        }

    def generate_placement_density_heatmap(
        self,
        gate_count: int,
        core_width_um: float,
        core_height_um: float,
        grid_cols: int = 16,
        grid_rows: int = 16,
        rent_exponent: float = 0.65,
        target_utilization: float = 0.70,
    ) -> Dict[str, Any]:
        """
        Discretizes the core into a 2D mesh grid and generates a spatial placement
        congestion profile governed by Rent's rule and pin density clustering.
        Identifies routing hotspots (> 0.85).
        """
        grid_cols = max(4, min(64, grid_cols))
        grid_rows = max(4, min(64, grid_rows))

        # Generate spatial 2D density distribution
        np.random.seed(42)  # Deterministic seed for reproducible testing
        base_density = np.ones((grid_rows, grid_cols), dtype=float) * target_utilization

        # Introduce Rent's rule clustering: central datapaths have higher interconnect density
        y_indices, x_indices = np.indices((grid_rows, grid_cols))
        center_x = (grid_cols - 1) / 2.0
        center_y = (grid_rows - 1) / 2.0
        dist_from_center = np.sqrt(((x_indices - center_x) / (grid_cols / 2.0)) ** 2 +
                                   ((y_indices - center_y) / (grid_rows / 2.0)) ** 2)

        # Core center concentration factor
        spatial_weight = 1.0 + (rent_exponent - 0.5) * (1.0 - np.clip(dist_from_center, 0.0, 1.0))
        # Add slight pseudo-random variation to simulate routing channel bottlenecks
        noise = (np.random.rand(grid_rows, grid_cols) - 0.5) * 0.15
        density_matrix = np.clip(base_density * spatial_weight + noise, 0.05, 0.98)

        # Hotspot detection (density >= 0.85)
        hotspots = []
        for r in range(grid_rows):
            for c in range(grid_cols):
                val = float(density_matrix[r, c])
                if val >= 0.85:
                    hotspots.append({
                        "row": r,
                        "col": c,
                        "density": round(val, 3),
                        "status": "CRITICAL_HOTSPOT" if val > 0.90 else "ROUTING_CONGESTED",
                    })

        hotspot_ratio = len(hotspots) / (grid_rows * grid_cols)
        avg_density = float(np.mean(density_matrix))
        peak_density = float(np.max(density_matrix))

        return {
            "grid_dimensions": {"rows": grid_rows, "cols": grid_cols},
            "bin_width_um": round(core_width_um / grid_cols, 2),
            "bin_height_um": round(core_height_um / grid_rows, 2),
            "average_density": round(avg_density, 3),
            "peak_density": round(peak_density, 3),
            "hotspot_count": len(hotspots),
            "hotspot_percentage": round(hotspot_ratio * 100.0, 2),
            "hotspots": hotspots,
            "density_heatmap": np.round(density_matrix, 3).tolist(),
            "routability_status": "ROUTABLE" if hotspot_ratio < 0.15 else "CONGESTION_RISK",
        }

    def estimate_interconnect_elmore_delay(
        self,
        wirelength_um: float,
        metal_layer: str = "intermediate",  # 'm1', 'intermediate', 'top'
        tech_node: str = "28nm",
        driver_resistance_ohms: Optional[float] = None,
        load_capacitance_ff: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculates distributed interconnect RC delay using the Elmore delay model:
          tau = R_driver * (C_wire * L + C_load) + 0.5 * R_wire * C_wire * L^2 + R_wire * L * C_load
        Computes optimal buffer insertion spacing (L_opt) and total unbuffered vs. buffered delay.
        """
        tech_info = TECH_NODE_LIBRARY.get(tech_node, TECH_NODE_LIBRARY["28nm"])
        r_drv = driver_resistance_ohms or tech_info["driver_r_ohm"]
        c_load = (load_capacitance_ff or tech_info["sink_c_ff"]) * 1e-15  # Farads

        # Determine wire sheet resistance based on metal layer
        if metal_layer == "m1":
            r_wire_per_um = tech_info["r_sheet_m1_ohm_per_um"]
        elif metal_layer == "top":
            r_wire_per_um = tech_info["r_sheet_top_ohm_per_um"]
        else:
            r_wire_per_um = tech_info["r_sheet_inter_ohm_per_um"]

        c_wire_per_um = tech_info["c_wire_ff_per_um"] * 1e-15  # Farads per um
        l_um = max(1.0, wirelength_um)

        total_wire_r = r_wire_per_um * l_um
        total_wire_c = c_wire_per_um * l_um

        # Elmore Delay formula (seconds):
        # tau_elmore = R_drv * (C_wire * L + C_load) + 0.5 * R_wire * C_wire * L^2 + R_wire * L * C_load
        tau_elmore_sec = (
            r_drv * (total_wire_c + c_load)
            + 0.5 * total_wire_r * total_wire_c
            + total_wire_r * c_load
        )
        tau_elmore_ps = tau_elmore_sec * 1e12

        # Optimal buffer insertion (Bakoglu / Rabaey model):
        # Repeaters are sized up (h_opt = sqrt((R0 * c_w) / (r_w * C0))) to achieve minimum RC delay
        buf_r0 = tech_info["driver_r_ohm"]
        buf_c0 = tech_info["sink_c_ff"] * 1e-15
        buf_intrinsic_ps = tech_info["buffer_intrinsic_delay_ps"]

        # Sizing ratio h_opt clamped to realistic standard cell drive strengths (2x to 12x)
        raw_h_opt = math.sqrt((buf_r0 * c_wire_per_um) / max(1e-25, (r_wire_per_um * buf_c0)))
        h_opt = max(2.0, min(12.0, raw_h_opt))
        buf_r = buf_r0 / h_opt
        buf_c = buf_c0 * h_opt

        l_opt_um = math.sqrt((2.0 * buf_r * (buf_c + buf_c0)) / max(1e-25, (r_wire_per_um * c_wire_per_um)))

        num_buffers = max(0, int(math.floor(l_um / max(10.0, l_opt_um))))
        if num_buffers > 0:
            stage_len_um = l_um / (num_buffers + 1)
            stage_r = r_wire_per_um * stage_len_um
            stage_c = c_wire_per_um * stage_len_um
            stage_delay_sec = (
                buf_r * (stage_c + buf_c)
                + 0.5 * stage_r * stage_c
                + stage_r * buf_c
            )
            stage_delay_ps = (stage_delay_sec * 1e12) + (buf_intrinsic_ps * 0.75)
            total_buffered_delay_ps = (num_buffers + 1) * stage_delay_ps
            delay_savings_pct = max(0.0, (tau_elmore_ps - total_buffered_delay_ps) / tau_elmore_ps * 100.0)
        else:
            total_buffered_delay_ps = tau_elmore_ps
            delay_savings_pct = 0.0

        return {
            "technology_node": tech_info["name"],
            "metal_layer": metal_layer,
            "wirelength_um": l_um,
            "unit_wire_resistance_ohm_per_um": r_wire_per_um,
            "unit_wire_capacitance_ff_per_um": tech_info["c_wire_ff_per_um"],
            "total_wire_resistance_ohm": round(total_wire_r, 2),
            "total_wire_capacitance_ff": round(total_wire_c * 1e15, 3),
            "unbuffered_elmore_delay_ps": round(tau_elmore_ps, 2),
            "optimal_repeater_spacing_um": round(l_opt_um, 1),
            "recommended_buffer_count": num_buffers,
            "buffered_total_delay_ps": round(total_buffered_delay_ps, 2),
            "buffer_speedup_savings_pct": round(delay_savings_pct, 1),
        }

    def model_clock_tree_synthesis(
        self,
        num_sinks: int,
        die_width_um: float,
        die_height_um: float,
        target_freq_mhz: float = 1000.0,
        tech_node: str = "28nm",
        process_variation_sigma_pct: float = 5.0,
    ) -> Dict[str, Any]:
        """
        Models symmetric H-tree Clock Tree Synthesis (CTS).
        Calculates tree depth, insertion delay (latency), clock skew (Delta t_skew),
        clock jitter, and timing closure setup/hold margins.
        """
        tech_info = TECH_NODE_LIBRARY.get(tech_node, TECH_NODE_LIBRARY["28nm"])
        num_sinks = max(2, num_sinks)
        t_clk_ns = 1000.0 / max(1.0, target_freq_mhz)
        t_clk_ps = t_clk_ns * 1000.0

        # Binary H-Tree depth: D = ceil(log2(num_sinks))
        tree_depth = int(math.ceil(math.log2(num_sinks)))

        # Total clock tree wirelength: geometric summation of H-tree branches
        # Branch lengths halving every 2 levels in 2D space
        span_um = (die_width_um + die_height_um) / 2.0
        total_tree_wirelength_um = span_um * (2.0 ** (tree_depth / 2.0))

        # Clock insertion latency = depth * buffer_delay + distributed segment delays
        buf_delay_ps = tech_info["buffer_intrinsic_delay_ps"]
        insertion_latency_ps = (tree_depth * buf_delay_ps * 1.8) + (total_tree_wirelength_um * 0.015)

        # Clock skew Delta t_skew modeled from process/voltage/temperature (PVT) variation
        # across symmetric H-tree branches: skew ~ latency * (sigma_PVT / 100)
        pvt_factor = max(1.0, process_variation_sigma_pct) / 100.0
        clock_skew_ps = insertion_latency_ps * pvt_factor

        # Clock Jitter: combined PLL jitter + random buffer jitter (Gaussian root-sum-square)
        pll_jitter_ps = 8.0  # Nominally 8ps for integrated PLL
        buf_jitter_ps = 1.2 * math.sqrt(tree_depth)
        total_jitter_ps = math.sqrt(pll_jitter_ps ** 2 + buf_jitter_ps ** 2)

        # Standard flip-flop timing parameters
        t_cq_ps = 45.0      # Clock-to-Q delay
        t_setup_ps = 30.0   # Setup time requirement
        t_hold_ps = 15.0    # Hold time requirement

        # Critical combinational datapath delay budget
        # Assume typical datapath uses 65% of clock period
        t_comb_max_ps = t_clk_ps * 0.65
        t_comb_min_ps = t_clk_ps * 0.08  # Minimum contamination delay

        # Timing Closure Formulations:
        # Setup Slack: T_clk - (t_cq + t_comb_max + t_setup + skew + jitter)
        setup_slack_ps = t_clk_ps - (t_cq_ps + t_comb_max_ps + t_setup_ps + clock_skew_ps + total_jitter_ps)

        # Hold Slack: t_cq + t_comb_min - (t_hold + skew + jitter)
        hold_slack_ps = (t_cq_ps + t_comb_min_ps) - (t_hold_ps + clock_skew_ps + total_jitter_ps)

        # Maximum achievable frequency F_max
        min_period_ps = t_cq_ps + t_comb_max_ps + t_setup_ps + clock_skew_ps + total_jitter_ps
        f_max_mhz = 1.0e6 / max(1.0, min_period_ps)

        timing_passed = bool(setup_slack_ps >= 0.0 and hold_slack_ps >= 0.0)

        result = {
            "technology_node": tech_info["name"],
            "target_frequency_mhz": target_freq_mhz,
            "clock_period_ps": round(t_clk_ps, 1),
            "clock_sinks_count": num_sinks,
            "htree_depth": tree_depth,
            "estimated_clock_wirelength_um": round(total_tree_wirelength_um, 1),
            "clock_insertion_latency_ps": round(insertion_latency_ps, 2),
            "clock_skew_ps": round(clock_skew_ps, 2),
            "clock_jitter_ps": round(total_jitter_ps, 2),
            "setup_slack_ps": round(setup_slack_ps, 2),
            "hold_slack_ps": round(hold_slack_ps, 2),
            "maximum_achievable_frequency_mhz": round(f_max_mhz, 1),
            "timing_closure_passed": timing_passed,
        }

        # Log into SQLite WAL database
        with self._lock:
            conn = self._get_connection()
            try:
                exp_id = f"CTS_{int(time.time() * 1000)}"
                conn.execute(
                    """
                    INSERT INTO vlsi_physical_design_history (
                        experiment_id, operation_type, tech_node, gate_count,
                        core_utilization, elmore_delay_ps, clock_skew_ps, timing_passed,
                        metrics_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        exp_id,
                        "CTS_MODELING",
                        tech_node,
                        num_sinks,
                        0.70,
                        0.0,
                        round(clock_skew_ps, 2),
                        1 if timing_passed else 0,
                        json.dumps(result),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.commit()
            except Exception:
                pass
            finally:
                conn.close()

        return result

    def get_history(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Retrieves recent VLSI physical design experiments from SQLite WAL database."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT id, experiment_id, operation_type, tech_node, gate_count,
                           core_utilization, elmore_delay_ps, clock_skew_ps, timing_passed,
                           metrics_json, created_at
                    FROM vlsi_physical_design_history
                    ORDER BY id DESC LIMIT ?
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
                results = []
                for r in rows:
                    results.append({
                        "id": r["id"],
                        "experiment_id": r["experiment_id"],
                        "operation_type": r["operation_type"],
                        "tech_node": r["tech_node"],
                        "gate_count": r["gate_count"],
                        "core_utilization": r["core_utilization"],
                        "elmore_delay_ps": r["elmore_delay_ps"],
                        "clock_skew_ps": r["clock_skew_ps"],
                        "timing_passed": bool(r["timing_passed"]),
                        "metrics": json.loads(r["metrics_json"]) if r["metrics_json"] else {},
                        "created_at": r["created_at"],
                    })
                return results
            except Exception:
                return []
            finally:
                conn.close()


# Singleton Instances
vlsi_physical_design_engine = ASICPhysicalDesignEngine()
sva_assertion_analyzer = SystemVerilogAssertionAnalyzer()
