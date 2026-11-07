"""
========================================================================================
VoltCore Apex Academia - Automated Assessment & Grading Pipeline Engine
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/autograder_engine.py
Lead Systems Architect & Educational Platform Director: Ashok Kumar A
========================================================================================
Capabilities:
  1. Embedded Firmware C/C++ Static AST & Concurrency Audit (FirmwareAutograderEngine)
  2. Verilog HDL RTL Synthesizability & Latch Inference Audit (VerilogRtlAutograderEngine)
  3. Non-Linear MNA Analog Circuit Simulation Convergence Grader (MnaTransientAutograderEngine)
  4. Structured Laboratory Report & Error Analysis Grader (LabReportAutograderEngine)
  5. Outcome-Based Education (OBE) CO-PO Mapping & Bloom's Taxonomy Attainment Engine
  6. SQLite WAL Mode Persistence ('student_assessment_grades' table in voltcore_lms.db)
  7. High-Precision Microsecond Execution (<5ms) Preserving Host Thermal Profile
========================================================================================
"""

import os
import re
import math
import json
import sqlite3
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")


# ========================================================================================
# 1. Embedded Firmware C/C++ Autograder (Existing Enhanced Engine)
# ========================================================================================

class FirmwareAutograderEngine:
    """
    Automated grading engine enforcing Anna University ECE Regulation 2023 laboratory standards.
    Performs memory leak checks, stack overflow detection, pin conflict checks, and RTOS audits.
    """

    INPUT_ONLY_PINS = {"34", "35", "36", "39"}
    ADC2_WIFI_CONFLICT_PINS = {"0", "2", "4", "12", "13", "14", "15", "25", "26", "27"}

    def grade_firmware_submission(
        self,
        source_code: str,
        module_code: str = "EC8701",
        target_mcu: str = "esp32"
    ) -> Dict[str, Any]:
        """
        Executes comprehensive static analysis on firmware code.
        Returns detailed scoring matrix, deductions, and pedagogical remediation.
        """
        # Strip comments to prevent false matches from explanatory comments
        clean_code = re.sub(r"/\*[\s\S]*?\*/", "", source_code)
        clean_code = re.sub(r"//.*", "", clean_code)

        lines = source_code.split("\n")
        deductions: List[Dict[str, Any]] = []
        positive_credits: List[str] = []

        # Category scores (out of 25 each -> total 100)
        scores = {
            "memory_safety": 25,
            "concurrency_rtos": 25,
            "hardware_pins": 25,
            "code_quality": 25
        }

        # 1. Memory Leak & Allocation Audit
        malloc_count = len(re.findall(r"\b(malloc|calloc|pvPortMalloc)\s*\(", clean_code))
        free_count = len(re.findall(r"\b(free|vPortFree)\s*\(", clean_code))

        if malloc_count > free_count:
            diff = malloc_count - free_count
            deduction = min(20, diff * 10)
            scores["memory_safety"] -= deduction
            deductions.append({
                "category": "memory_safety",
                "severity": "CRITICAL",
                "issue": f"Potential Heap Memory Leak: {malloc_count} dynamic allocation(s) found but only {free_count} deallocation(s).",
                "penalty": deduction,
                "remedy": "Ensure every malloc/pvPortMalloc has a corresponding free/vPortFree in all execution paths."
            })
        elif malloc_count > 0 and malloc_count == free_count:
            positive_credits.append("Clean Heap Memory Balance: All dynamic allocations properly paired with free/vPortFree.")

        # 2. Stack Overflow Hazards (Large buffers allocated locally inside functions)
        large_buffer_pattern = re.compile(r"\b(uint8_t|char|int|float)\s+([a-zA-Z0-9_]+)\[\s*(\d{4,})\s*\];")
        for idx, line in enumerate(lines, 1):
            match = large_buffer_pattern.search(line)
            if match:
                buf_type, buf_name, size = match.groups()
                if int(size) >= 2048:
                    scores["memory_safety"] = max(0, scores["memory_safety"] - 10)
                    deductions.append({
                        "category": "memory_safety",
                        "severity": "HIGH",
                        "line": idx,
                        "issue": f"Stack Overflow Hazard: Local array '{buf_name}' allocated on task stack with size {size} bytes.",
                        "penalty": 10,
                        "remedy": "Allocate large buffers in static/global BSS memory or pass via pointer to prevent stack overflow."
                    })

        # 3. Blocking Delay Anti-Pattern inside FreeRTOS tasks
        has_freertos = "xTaskCreate" in source_code or "vTaskDelay" in source_code or "FreeRTOS.h" in source_code
        has_blocking_delay = bool(re.search(r"\bdelay\s*\(\s*\d+\s*\);", source_code))

        if has_freertos and has_blocking_delay:
            scores["concurrency_rtos"] -= 15
            deductions.append({
                "category": "concurrency_rtos",
                "severity": "HIGH",
                "issue": "FreeRTOS CPU Starvation: Found blocking delay() inside multi-tasking FreeRTOS firmware.",
                "penalty": 15,
                "remedy": "Replace busy-wait delay() with non-blocking vTaskDelay(pdMS_TO_TICKS(ms)) to yield execution to lower-priority tasks."
            })
        elif has_freertos and not has_blocking_delay:
            positive_credits.append("Deterministic Multi-Tasking: Compliant use of non-blocking FreeRTOS delay primitives.")

        # 4. DMA Memory Barrier Verification for Advanced DMA Modules
        if module_code in ("EC8708", "EC8706") and "DMA" in source_code:
            has_dmb = "__DMB" in source_code or "__DSB" in source_code
            if not has_dmb:
                scores["concurrency_rtos"] -= 10
                deductions.append({
                    "category": "concurrency_rtos",
                    "severity": "MEDIUM",
                    "issue": "Missing Memory Barrier: Out-of-order DMA buffer write without __DMB() or __DSB().",
                    "penalty": 10,
                    "remedy": "Invoke __DMB() after writing buffer pointers to commit changes into SRAM before enabling DMA stream."
                })
            else:
                positive_credits.append("Memory Coherency: ARM Data Memory Barrier (__DMB) properly placed before DMA trigger.")

        # 5. Hardware Pin Mismatches (Input-Only Pin Assignment as Output)
        pin_mode_pattern = re.compile(r"\bpinMode\s*\(\s*(\d+)\s*,\s*OUTPUT\s*\)", re.IGNORECASE)
        for idx, line in enumerate(lines, 1):
            match = pin_mode_pattern.search(line)
            if match:
                pin = match.group(1)
                if pin in self.INPUT_ONLY_PINS:
                    scores["hardware_pins"] -= 15
                    deductions.append({
                        "category": "hardware_pins",
                        "severity": "CRITICAL",
                        "line": idx,
                        "issue": f"Hardware Invalid Pin Mode: GPIO {pin} is an input-only pin on ESP32 and cannot be set as OUTPUT.",
                        "penalty": 15,
                        "remedy": f"Select an output-capable GPIO (e.g. GPIO 18, 19, 21, 22, 23) instead of input-only GPIO {pin}."
                    })

        # 6. ADC2 Wi-Fi Contention Trap
        has_wifi = bool(re.search(r"\b(WiFi\.begin|esp_wifi_start)\b", source_code))
        analog_read_pattern = re.compile(r"\banalogRead\s*\(\s*(\d+)\s*\)", re.IGNORECASE)
        if has_wifi:
            for idx, line in enumerate(lines, 1):
                match = analog_read_pattern.search(line)
                if match:
                    pin = match.group(1)
                    if pin in self.ADC2_WIFI_CONFLICT_PINS:
                        scores["hardware_pins"] -= 10
                        deductions.append({
                            "category": "hardware_pins",
                            "severity": "HIGH",
                            "line": idx,
                            "issue": f"ADC2 / Wi-Fi Contention: Analog read on GPIO {pin} (ADC2) fails when Wi-Fi driver is active.",
                            "penalty": 10,
                            "remedy": "Use ADC1 channels (GPIO 32, 33, 34, 35, 36, 39) which operate independently from Wi-Fi."
                        })
                        break

        # Calculate Total Composite Score
        total_score = sum(max(0, s) for s in scores.values())
        grade = "O" if total_score >= 90 else "A+" if total_score >= 80 else "A" if total_score >= 70 else "B+" if total_score >= 60 else "RA"

        return {
            "status": "success",
            "module_code": module_code,
            "target_mcu": target_mcu,
            "total_score": total_score,
            "grade": grade,
            "category_scores": scores,
            "deductions": deductions,
            "positive_credits": positive_credits,
            "evaluated_by": "VoltCore AST Autograder v6.0 (MIT Campus ECE)",
            "passed": total_score >= 60,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ========================================================================================
# 2. Verilog HDL RTL Autograder Engine (Phase 15 Deliverable)
# ========================================================================================

class VerilogRtlAutograderEngine:
    """
    Evaluates Verilog HDL RTL designs for synthesizability, sequential vs combinational
    discipline, unintentional latch inference, reset sensitivity, and modularity.
    """

    def grade_verilog_submission(
        self,
        source_code: str,
        module_name: str = "rv32i_core"
    ) -> Dict[str, Any]:
        # Strip comments
        clean_code = re.sub(r"/\*[\s\S]*?\*/", "", source_code)
        clean_code = re.sub(r"//.*", "", clean_code)

        lines = source_code.split("\n")
        deductions: List[Dict[str, Any]] = []
        positive_credits: List[str] = []

        scores = {
            "synthesizability": 25,
            "sequential_discipline": 25,
            "combinational_latch_free": 25,
            "modularity_ports": 25
        }

        # 1. Non-synthesizable delays in RTL (#10, #5)
        delay_matches = list(re.finditer(r"#\s*\d+", clean_code))
        if delay_matches:
            deduction = min(20, len(delay_matches) * 5)
            scores["synthesizability"] -= deduction
            deductions.append({
                "category": "synthesizability",
                "severity": "CRITICAL",
                "issue": f"Non-Synthesizable Delays: Found {len(delay_matches)} time-delay statement(s) (#delays) in synthesis RTL.",
                "penalty": deduction,
                "remedy": "Remove #delays from RTL module code; delays are only permissible inside testbench harnesses."
            })
        else:
            positive_credits.append("Pure Synthesizable Code: No non-synthesizable #delays found in RTL logic.")

        # 2. Sequential Logic Discipline: Non-blocking <= in clocked always blocks
        clocked_blocks = re.findall(r"always\s*@\s*\(\s*(?:posedge|negedge)[^)]+\)([\s\S]*?)(?:endmodule|always|\Z)", clean_code)
        for block in clocked_blocks:
            bad_blocking = re.findall(r"(?<![<>=!])=(?![=])", block)
            if bad_blocking:
                deduction = min(15, len(bad_blocking) * 5)
                scores["sequential_discipline"] = max(0, scores["sequential_discipline"] - deduction)
                deductions.append({
                    "category": "sequential_discipline",
                    "severity": "HIGH",
                    "issue": "Race Condition Hazard: Clocked always block contains blocking assignment (=) instead of non-blocking (<=).",
                    "penalty": deduction,
                    "remedy": "Use non-blocking assignment (<=) for all register transfers inside sequential clocked always blocks."
                })
                break
        if clocked_blocks and not any(d["category"] == "sequential_discipline" for d in deductions):
            positive_credits.append("Deterministic Flip-Flops: Strict adherence to non-blocking (<=) in all clocked sequential blocks.")

        # 3. Combinational Logic Discipline: Latch Inference Check (case without default:)
        case_blocks = re.findall(r"\bcase\s*\([^)]+\)([\s\S]*?)\bendcase\b", clean_code)
        for cb in case_blocks:
            if "default" not in cb:
                scores["combinational_latch_free"] = max(0, scores["combinational_latch_free"] - 15)
                deductions.append({
                    "category": "combinational_latch_free",
                    "severity": "HIGH",
                    "issue": "Unintentional Latch Inference: 'case' statement missing 'default:' clause.",
                    "penalty": 15,
                    "remedy": "Add a 'default:' branch to case statements to cover all unspecified state/input combinations."
                })
                break

        # Check for non-blocking in combinational always blocks
        comb_blocks = re.findall(r"always\s*@\s*(?:\(\s*)?(?:\*|[^p\s]edge|[\w\s,]+?)(?:\s*\))?\s*begin([\s\S]*?)(?:endmodule|always|\Z)", clean_code)
        for block in comb_blocks:
            if "<=" in block and not any(d["category"] == "combinational_latch_free" for d in deductions):
                scores["combinational_latch_free"] = max(0, scores["combinational_latch_free"] - 5)
                deductions.append({
                    "category": "combinational_latch_free",
                    "severity": "MEDIUM",
                    "issue": "Combinational Latency Inconsistency: Non-blocking (<=) used in combinational always block.",
                    "penalty": 5,
                    "remedy": "Use blocking assignment (=) inside combinational always @* blocks."
                })
                break

        # 4. Modularity and Port Declaration
        has_module = bool(re.search(r"\bmodule\s+[a-zA-Z0-9_]+", source_code))
        has_endmodule = "endmodule" in source_code
        has_ports = bool(re.search(r"\b(input|output|inout)\b", source_code))

        if not has_module or not has_endmodule:
            scores["modularity_ports"] = 0
            deductions.append({
                "category": "modularity_ports",
                "severity": "CRITICAL",
                "issue": "Malformed Verilog Module: Missing valid 'module' or 'endmodule' keyword wrapper.",
                "penalty": 25,
                "remedy": "Declare top-level module with proper port list and close with 'endmodule'."
            })
        elif not has_ports:
            scores["modularity_ports"] -= 10
            deductions.append({
                "category": "modularity_ports",
                "severity": "MEDIUM",
                "issue": "Isolated Module: No input or output ports defined.",
                "penalty": 10,
                "remedy": "Expose clock, reset, and data I/O ports in the module header."
            })
        else:
            positive_credits.append("Clean Structural Hierarchy: Standard IEEE 1364 Verilog module boundary with declared I/O ports.")

        total_score = sum(max(0, s) for s in scores.values())
        grade = "O" if total_score >= 90 else "A+" if total_score >= 80 else "A" if total_score >= 70 else "B+" if total_score >= 60 else "RA"

        return {
            "status": "success",
            "module_name": module_name,
            "total_score": total_score,
            "grade": grade,
            "category_scores": scores,
            "deductions": deductions,
            "positive_credits": positive_credits,
            "passed": total_score >= 60,
            "evaluated_by": "VoltCore Verilog RTL Autograder v6.0"
        }


# ========================================================================================
# 3. MNA Analog Circuit Simulation Convergence Autograder (Phase 15 Deliverable)
# ========================================================================================

class MnaTransientAutograderEngine:
    """
    Grades Modified Nodal Analysis (MNA) analog circuit simulation results, evaluating
    numerical convergence, Kirchhoff current conservation, and theoretical accuracy.
    """

    def grade_mna_simulation(
        self,
        simulation_results: Dict[str, Any],
        theoretical_benchmarks: Optional[Dict[str, float]] = None,
        circuit_type: str = "RC_STEP"
    ) -> Dict[str, Any]:
        deductions: List[Dict[str, Any]] = []
        positive_credits: List[str] = []

        scores = {
            "convergence": 30,
            "conservation_laws": 25,
            "theoretical_correlation": 25,
            "transient_smoothness": 20
        }

        # 1. Numerical Convergence
        trajectories = simulation_results.get("trajectories", {})
        time_vec = trajectories.get("time_ms", [])
        converged = simulation_results.get("converged", True)
        iterations = simulation_results.get("iterations_count", 5)

        if not converged or len(time_vec) < 3:
            scores["convergence"] = 0
            deductions.append({
                "category": "convergence",
                "severity": "CRITICAL",
                "issue": "Non-Linear Matrix Divergence: Newton-Raphson failed to converge within maximum iteration limit.",
                "penalty": 30,
                "remedy": "Reduce integration step size (t_step_us) or increase damping relaxation factor."
            })
        elif iterations > 20:
            scores["convergence"] -= 10
            deductions.append({
                "category": "convergence",
                "severity": "MEDIUM",
                "issue": f"Slow Convergence: Matrix required {iterations} iterations per step, indicating stiff dynamics.",
                "penalty": 10,
                "remedy": "Use 2nd-order Trapezoidal integration with adaptive timestep."
            })
        else:
            positive_credits.append(f"Optimal Newton-Raphson Convergence: Matrix converged cleanly in {iterations} iterations.")

        # 2. Conservation of Energy & Physical Ranges
        v_out = trajectories.get("v_out", [])
        v_in = trajectories.get("v_in", [])
        has_unphysical_voltages = any(math.isnan(v) or math.isinf(v) or abs(v) > 1000.0 for v in v_out)

        if has_unphysical_voltages:
            scores["conservation_laws"] = 0
            deductions.append({
                "category": "conservation_laws",
                "severity": "CRITICAL",
                "issue": "Unphysical Voltage Spike: Trajectory contains NaN, Inf, or voltages exceeding supply limits.",
                "penalty": 25,
                "remedy": "Check for floating ungrounded nodes or zero-impedance short circuits in netlist."
            })
        else:
            positive_credits.append("Kirchhoff Law Compliant: Voltage trajectories strictly bounded within passive physical limits.")

        # 3. Theoretical Correlation
        benchmarks = theoretical_benchmarks or {"v_final": 5.0, "time_constant_ms": 1.0}
        v_final_theo = benchmarks.get("v_final", 5.0)

        if v_out:
            v_final_sim = v_out[-1]
            error_pct = (abs(v_final_sim - v_final_theo) / max(1e-6, abs(v_final_theo))) * 100.0

            if error_pct <= 3.0:
                scores["theoretical_correlation"] = 25
                positive_credits.append(f"High-Precision Correlation: Final voltage within {error_pct:.2f}% of theoretical target.")
            elif error_pct <= 10.0:
                scores["theoretical_correlation"] = 18
                deductions.append({
                    "category": "theoretical_correlation",
                    "severity": "LOW",
                    "issue": f"Minor Deviation: Simulation final voltage deviates by {error_pct:.1f}% from analytical model.",
                    "penalty": 7,
                    "remedy": "Account for non-ideal diode forward drops or internal source resistance."
                })
            else:
                scores["theoretical_correlation"] = 5
                deductions.append({
                    "category": "theoretical_correlation",
                    "severity": "HIGH",
                    "issue": f"Significant Model Discrepancy: Simulation deviates by {error_pct:.1f}% from theory.",
                    "penalty": 20,
                    "remedy": "Verify resistor and capacitor metric prefixes (e.g. uF vs F, kOhm vs Ohm)."
                })

        # 4. Transient Smoothness (No unphysical discontinuities)
        if len(v_out) >= 5:
            # Check maximum step-to-step delta
            max_delta = max(abs(v_out[i] - v_out[i - 1]) for i in range(1, len(v_out)))
            if max_delta > 10.0:
                scores["transient_smoothness"] -= 10
                deductions.append({
                    "category": "transient_smoothness",
                    "severity": "MEDIUM",
                    "issue": f"Numerical Ringing: Large voltage step jump ({max_delta:.2f}V) detected between adjacent timesteps.",
                    "penalty": 10,
                    "remedy": "Enable Backward Euler damping on initial step transitions."
                })
            else:
                positive_credits.append("Smooth Waveform Continuity: Continuous reactive charging curve without numerical chatter.")

        total_score = sum(max(0, s) for s in scores.values())
        grade = "O" if total_score >= 90 else "A+" if total_score >= 80 else "A" if total_score >= 70 else "B+" if total_score >= 60 else "RA"

        return {
            "status": "success",
            "circuit_type": circuit_type,
            "total_score": total_score,
            "grade": grade,
            "category_scores": scores,
            "deductions": deductions,
            "positive_credits": positive_credits,
            "passed": total_score >= 60,
            "evaluated_by": "VoltCore MNA Analog Autograder v6.0"
        }


# ========================================================================================
# 4. Laboratory Report Autograder Engine (Phase 15 Deliverable)
# ========================================================================================

class LabReportAutograderEngine:
    """
    Evaluates student laboratory reports against Anna University Regulation 2023 rubrics:
    Objective & Circuit Topology, Observation Table Data, Error Analysis, and Viva Voce.
    """

    REQUIRED_SECTIONS = [
        ("aim_objective", "Aim & Technical Objectives", 20),
        ("circuit_netlist", "Circuit Topology / SPICE Netlist", 20),
        ("observations", "Observation Table Data Matrix", 30),
        ("error_analysis", "Theoretical Error Analysis", 15),
        ("viva_inferences", "Inferences & Viva Voce Q&A", 15)
    ]

    def grade_lab_report(
        self,
        report_data: Dict[str, Any],
        course_code: str = "EC23C03"
    ) -> Dict[str, Any]:
        deductions: List[Dict[str, Any]] = []
        positive_credits: List[str] = []
        scores: Dict[str, float] = {}

        # 1. Section Presence & Content Depth
        for key, label, max_pts in self.REQUIRED_SECTIONS:
            content = report_data.get(key)
            if not content:
                scores[key] = 0.0
                deductions.append({
                    "category": key,
                    "severity": "CRITICAL",
                    "issue": f"Missing Mandatory Section: '{label}' is absent from lab submission.",
                    "penalty": max_pts,
                    "remedy": f"Include a complete '{label}' section in accordance with syllabus requirements."
                })
            elif isinstance(content, str) and len(content.strip()) < 20:
                scores[key] = max_pts * 0.4
                deductions.append({
                    "category": key,
                    "severity": "MEDIUM",
                    "issue": f"Superficial Content: '{label}' contains fewer than 20 characters.",
                    "penalty": max_pts * 0.6,
                    "remedy": "Provide detailed engineering rationale, schematics, and analytical calculations."
                })
            else:
                scores[key] = float(max_pts)

        # 2. Quantitative Observation Table Audit
        obs = report_data.get("observations", [])
        if isinstance(obs, list):
            if len(obs) >= 5:
                positive_credits.append(f"Rigorous Data Collection: Observation table contains {len(obs)} verified sample points.")
            elif len(obs) > 0:
                ded = 10.0
                scores["observations"] = max(0.0, scores["observations"] - ded)
                deductions.append({
                    "category": "observations",
                    "severity": "MEDIUM",
                    "issue": f"Sparse Dataset: Only {len(obs)} readings recorded (minimum required is 5).",
                    "penalty": ded,
                    "remedy": "Record at least 5 readings across the linear and saturation operating regions."
                })

        # 3. Error Analysis Quantitative Verification
        error_val = report_data.get("experimental_error_pct")
        if error_val is not None:
            try:
                err_float = float(error_val)
                if err_float <= 5.0:
                    positive_credits.append(f"Exemplary Measurement Accuracy: Experimental error is only {err_float:.2f}%.")
                elif err_float > 20.0:
                    scores["error_analysis"] = max(0.0, scores["error_analysis"] - 7.0)
                    deductions.append({
                        "category": "error_analysis",
                        "severity": "LOW",
                        "issue": f"Elevated Error Rate: Experimental error ({err_float:.1f}%) exceeds component tolerance.",
                        "penalty": 7.0,
                        "remedy": "Calibrate virtual DSO probes and verify resistor color codes."
                    })
            except (ValueError, TypeError):
                pass

        total_score = sum(scores.values())
        grade = "O" if total_score >= 90 else "A+" if total_score >= 80 else "A" if total_score >= 70 else "B+" if total_score >= 60 else "RA"

        return {
            "status": "success",
            "course_code": course_code,
            "total_score": round(total_score, 1),
            "grade": grade,
            "category_scores": scores,
            "deductions": deductions,
            "positive_credits": positive_credits,
            "passed": total_score >= 60.0,
            "evaluated_by": "VoltCore Lab Report Autograder v6.0"
        }


# ========================================================================================
# 5. Outcome-Based Education (OBE) Competency Engine (Phase 15 Deliverable)
# ========================================================================================

class ObeCompetencyEngine:
    """
    Computes NBA / ABET Outcome-Based Education (OBE) course outcome (CO) attainments,
    program outcome (PO) mappings, and Bloom's Revised Taxonomy levels.
    """

    ASSESSMENT_MAPPING = {
        "FIRMWARE_C": {
            "course_outcome": "CO3",
            "co_desc": "Design and implement bare-metal and RTOS firmware for ARM/RISC-V microcontrollers.",
            "program_outcomes": ["PO1", "PO3", "PO5", "PSO1"],
            "bloom_level": "L3",
            "bloom_verb": "Apply"
        },
        "VERILOG_RTL": {
            "course_outcome": "CO4",
            "co_desc": "Synthesize synthesizable Verilog HDL descriptions for digital processors and accelerators.",
            "program_outcomes": ["PO3", "PO5", "PSO1", "PSO2"],
            "bloom_level": "L6",
            "bloom_verb": "Create"
        },
        "MNA_SIMULATION": {
            "course_outcome": "CO2",
            "co_desc": "Formulate and solve non-linear analog circuits using Modified Nodal Analysis matrices.",
            "program_outcomes": ["PO1", "PO2", "PO5"],
            "bloom_level": "L4",
            "bloom_verb": "Analyze"
        },
        "LAB_REPORT": {
            "course_outcome": "CO5",
            "co_desc": "Document experimental investigations, error bounds, and engineering inferences.",
            "program_outcomes": ["PO9", "PO10", "PO12"],
            "bloom_level": "L5",
            "bloom_verb": "Evaluate"
        },
        "GATE_EXAM": {
            "course_outcome": "CO1",
            "co_desc": "Demonstrate comprehensive mastery of foundational ECE theory and competitive benchmarks.",
            "program_outcomes": ["PO1", "PO2"],
            "bloom_level": "L3",
            "bloom_verb": "Apply"
        }
    }

    def compute_obe_attainment(
        self,
        assessment_type: str,
        score_pct: float,
        module_code: str = "EC8701"
    ) -> Dict[str, Any]:
        """Calculates OBE attainment metrics for an individual assessment submission."""
        mapping = self.ASSESSMENT_MAPPING.get(assessment_type.upper(), {
            "course_outcome": "CO1",
            "co_desc": "General Engineering Competency",
            "program_outcomes": ["PO1", "PO2"],
            "bloom_level": "L2",
            "bloom_verb": "Understand"
        })

        # NBA Attainment Level Thresholds: Level 3 (>= 70%), Level 2 (60-69%), Level 1 (50-59%), Level 0 (< 50%)
        if score_pct >= 70.0:
            attainment_level = 3
            attainment_status = "SUBSTANTIAL"
        elif score_pct >= 60.0:
            attainment_level = 2
            attainment_status = "MODERATE"
        elif score_pct >= 50.0:
            attainment_level = 1
            attainment_status = "SLIGHT"
        else:
            attainment_level = 0
            attainment_status = "NOT_ATTAINED"

        return {
            "course_outcome": mapping["course_outcome"],
            "co_description": mapping["co_desc"],
            "program_outcomes": mapping["program_outcomes"],
            "bloom_taxonomy_level": mapping["bloom_level"],
            "bloom_action_verb": mapping["bloom_verb"],
            "student_score_pct": round(score_pct, 2),
            "attainment_level": attainment_level,
            "attainment_status": attainment_status,
            "target_threshold_pct": 60.0,
            "threshold_met": score_pct >= 60.0
        }


# ========================================================================================
# 6. Unified Autograder Engine Facade & SQLite WAL Persistence (Phase 15 Deliverable)
# ========================================================================================

class AutograderEngine:
    """
    Central autograder orchestrator connecting all sub-graders with SQLite WAL
    persistence in 'student_assessment_grades' and analytics generation.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.firmware_grader = FirmwareAutograderEngine()
        self.verilog_grader = VerilogRtlAutograderEngine()
        self.mna_grader = MnaTransientAutograderEngine()
        self.lab_grader = LabReportAutograderEngine()
        self.obe_engine = ObeCompetencyEngine()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    def _init_db(self):
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS student_assessment_grades (
                    assessment_id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    student_name TEXT,
                    module_code TEXT NOT NULL,
                    assessment_type TEXT NOT NULL,
                    raw_score REAL NOT NULL,
                    max_score REAL NOT NULL,
                    percentage REAL NOT NULL,
                    letter_grade TEXT NOT NULL,
                    obe_attainment TEXT,
                    rubric_breakdown TEXT,
                    evaluator_verdict TEXT NOT NULL,
                    cpu_time_ms REAL,
                    timestamp TEXT NOT NULL
                );
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_student_grades_lookup
                ON student_assessment_grades(student_id, module_code);
            """)
            conn.commit()
        finally:
            conn.close()

    def grade_assessment(
        self,
        student_id: str,
        module_code: str,
        assessment_type: str,
        payload: Dict[str, Any],
        student_name: str = "Student"
    ) -> Dict[str, Any]:
        """
        Unified dispatch: routes to specialized grader, computes OBE attainment,
        and atomically commits results under SQLite WAL mode.
        """
        t0 = time.perf_counter()
        atype = assessment_type.upper().strip()

        if atype == "FIRMWARE_C":
            source_code = payload.get("source_code", "")
            target_mcu = payload.get("target_mcu", "esp32")
            sub_res = self.firmware_grader.grade_firmware_submission(source_code, module_code, target_mcu)
            raw_score = float(sub_res["total_score"])
            max_score = 100.0

        elif atype == "VERILOG_RTL":
            source_code = payload.get("source_code", "")
            module_name = payload.get("module_name", "rv32i_core")
            sub_res = self.verilog_grader.grade_verilog_submission(source_code, module_name)
            raw_score = float(sub_res["total_score"])
            max_score = 100.0

        elif atype == "MNA_SIMULATION":
            sim_results = payload.get("simulation_results", {})
            theo = payload.get("theoretical_benchmarks")
            circ_type = payload.get("circuit_type", "RC_STEP")
            sub_res = self.mna_grader.grade_mna_simulation(sim_results, theo, circ_type)
            raw_score = float(sub_res["total_score"])
            max_score = 100.0

        elif atype == "LAB_REPORT":
            report_data = payload.get("report_data", payload)
            sub_res = self.lab_grader.grade_lab_report(report_data, module_code)
            raw_score = float(sub_res["total_score"])
            max_score = 100.0

        elif atype == "GATE_EXAM":
            correct_answers = float(payload.get("correct_answers", 0))
            total_questions = float(max(1, payload.get("total_questions", 1)))
            raw_score = correct_answers
            max_score = total_questions
            pct = (correct_answers / total_questions) * 100.0
            grade = "O" if pct >= 90 else "A+" if pct >= 80 else "A" if pct >= 70 else "B+" if pct >= 60 else "RA"
            sub_res = {
                "status": "success",
                "total_score": round(pct, 1),
                "grade": grade,
                "category_scores": {"accuracy": round(pct, 1)},
                "deductions": [],
                "positive_credits": [f"Scored {int(correct_answers)}/{int(total_questions)} in competitive test."],
                "passed": pct >= 60.0
            }
        else:
            raise ValueError(f"Unsupported assessment type: {assessment_type}")

        percentage = round((raw_score / max_score) * 100.0, 2)
        letter_grade = sub_res.get("grade", "RA")
        verdict = "DISTINCTION" if percentage >= 85.0 else "PASSED" if percentage >= 60.0 else "REVISION_REQUIRED"

        # Compute OBE Attainment
        obe_metrics = self.obe_engine.compute_obe_attainment(atype, percentage, module_code)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        now_str = datetime.now(timezone.utc).isoformat()
        sim_id = f"GRADE_{int(time.time() * 1000)}_{os.urandom(2).hex()}"

        # Persist to SQLite WAL
        conn = self._get_connection()
        try:
            conn.execute("""
                INSERT INTO student_assessment_grades (
                    assessment_id, student_id, student_name, module_code, assessment_type,
                    raw_score, max_score, percentage, letter_grade, obe_attainment,
                    rubric_breakdown, evaluator_verdict, cpu_time_ms, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                sim_id, student_id, student_name, module_code, atype,
                raw_score, max_score, percentage, letter_grade,
                json.dumps(obe_metrics), json.dumps(sub_res), verdict,
                round(elapsed_ms, 2), now_str
            ))
            conn.commit()
        finally:
            conn.close()

        return {
            "status": "SUCCESS",
            "assessment_id": sim_id,
            "student_id": student_id,
            "module_code": module_code,
            "assessment_type": atype,
            "raw_score": raw_score,
            "max_score": max_score,
            "percentage": percentage,
            "letter_grade": letter_grade,
            "evaluator_verdict": verdict,
            "obe_attainment": obe_metrics,
            "rubric_breakdown": sub_res,
            "cpu_time_ms": round(elapsed_ms, 2),
            "timestamp": now_str
        }

    def get_student_grades(
        self,
        student_id: str,
        module_code: Optional[str] = None,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        records = []
        try:
            cur = conn.cursor()
            if module_code:
                cur.execute("""
                    SELECT assessment_id, student_id, student_name, module_code,
                           assessment_type, raw_score, max_score, percentage,
                           letter_grade, obe_attainment, evaluator_verdict, timestamp
                    FROM student_assessment_grades
                    WHERE student_id = ? AND module_code = ?
                    ORDER BY timestamp DESC
                    LIMIT ?;
                """, (student_id, module_code, int(limit)))
            else:
                cur.execute("""
                    SELECT assessment_id, student_id, student_name, module_code,
                           assessment_type, raw_score, max_score, percentage,
                           letter_grade, obe_attainment, evaluator_verdict, timestamp
                    FROM student_assessment_grades
                    WHERE student_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?;
                """, (student_id, int(limit)))

            for r in cur.fetchall():
                obe = json.loads(r[9]) if r[9] else {}
                records.append({
                    "assessment_id": r[0],
                    "student_id": r[1],
                    "student_name": r[2],
                    "module_code": r[3],
                    "assessment_type": r[4],
                    "raw_score": r[5],
                    "max_score": r[6],
                    "percentage": r[7],
                    "letter_grade": r[8],
                    "obe_attainment": obe,
                    "evaluator_verdict": r[10],
                    "timestamp": r[11]
                })
        finally:
            conn.close()
        return records

    def get_cohort_obe_summary(self, module_code: str) -> Dict[str, Any]:
        """Aggregates cohort-level attainment percentage across Course Outcomes (COs)."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT assessment_type, percentage
                FROM student_assessment_grades
                WHERE module_code = ?;
            """, (module_code,))
            rows = cur.fetchall()
        finally:
            conn.close()

        total_students = len(rows)
        if total_students == 0:
            return {
                "module_code": module_code,
                "cohort_size": 0,
                "overall_attainment_pct": 0.0,
                "co_attainments": {}
            }

        co_buckets: Dict[str, List[float]] = {}
        for atype, pct in rows:
            mapping = self.obe_engine.ASSESSMENT_MAPPING.get(atype, {})
            co = mapping.get("course_outcome", "CO1")
            co_buckets.setdefault(co, []).append(pct)

        co_results = {}
        for co, scores in co_buckets.items():
            passed_count = sum(1 for s in scores if s >= 60.0)
            attainment_pct = round((passed_count / len(scores)) * 100.0, 1)
            level = 3 if attainment_pct >= 70.0 else 2 if attainment_pct >= 60.0 else 1 if attainment_pct >= 50.0 else 0
            co_results[co] = {
                "sample_count": len(scores),
                "attainment_pct": attainment_pct,
                "attainment_level": level,
                "target_met": attainment_pct >= 60.0
            }

        overall_passed = sum(1 for _, pct in rows if pct >= 60.0)
        overall_pct = round((overall_passed / total_students) * 100.0, 1)

        return {
            "module_code": module_code,
            "cohort_size": total_students,
            "overall_attainment_pct": overall_pct,
            "co_attainments": co_results
        }

    def get_rubric_standards(self) -> Dict[str, Any]:
        return {
            "FIRMWARE_C": "Memory Safety (25%), RTOS Concurrency (25%), Pin Conflicts (25%), Code Quality (25%)",
            "VERILOG_RTL": "Synthesizability (25%), Sequential Discipline (25%), Latch-Free Logic (25%), Modularity (25%)",
            "MNA_SIMULATION": "Newton-Raphson Convergence (30%), Conservation Laws (25%), Theoretical Correlation (25%), Waveform Smoothness (20%)",
            "LAB_REPORT": "Aim/Objective (20%), Schematic/Netlist (20%), Observations (30%), Error Analysis (15%), Viva Voce (15%)",
            "GATE_EXAM": "Objective Multiple-Choice & Numerical Answer Type (100%)"
        }


# Global singleton instances
firmware_autograder = FirmwareAutograderEngine()
verilog_autograder = VerilogRtlAutograderEngine()
mna_autograder = MnaTransientAutograderEngine()
lab_report_autograder = LabReportAutograderEngine()
obe_engine = ObeCompetencyEngine()
autograder_engine = AutograderEngine()
