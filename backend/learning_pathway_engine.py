"""
========================================================================================
VoltCore Apex Academia - Unified Learning Pathway Synthesis & Remedial Engine
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/learning_pathway_engine.py
Platform Lead & System Architect: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Provides:
  1. 5 Official Academic Pathways (Semiconductor, Embedded, DSP/Telecom, VLSI, AI Hardware)
  2. Prerequisite DAG Traversal (Forward Unlocking & Backward Dependency Tracing)
  3. Student Pathway Mastery Tracking (0-100% Attainment Scoring)
  4. Dynamic Remedial Micro-Lesson Dispatching Based on Concept Dependency Telemetry
========================================================================================
"""

import os
import json
from typing import Dict, Any, List, Optional, Set, Tuple
from collections import deque

from backend.subject_emblem_registry import get_discipline_name, get_subject_emblem


# -----------------------------------------------------------------------------
# 1. 5 OFFICIAL ACADEMIC PATHWAYS SPECIFICATION
# -----------------------------------------------------------------------------
ACADEMIC_PATHWAYS: Dict[str, Dict[str, Any]] = {
    "pathway_semiconductor": {
        "id": "pathway_semiconductor",
        "title": "Electronics & Semiconductor Systems",
        "industry_alignment": "Semiconductor Foundries, Analog Mixed-Signal EDA",
        "total_credits": 15,
        "nodes": [
            {
                "code": "EC23C01",
                "discipline_name": "Circuit Analysis & Network Synthesis",
                "milestone": "Passive Lattice & MNA State Formulations",
                "credits": 4,
                "prerequisites": [],
                "core_concepts": ["KCL_KVL", "Thevenin_Norton", "Laplace_Transients", "MNA_Matrix"]
            },
            {
                "code": "EC23C02",
                "discipline_name": "Semiconductor Device Physics",
                "milestone": "Bandgap Engineering & Carrier Transport",
                "credits": 3,
                "prerequisites": ["EC23C01"],
                "core_concepts": ["Fermi_Dirac", "Intrinsic_Carriers", "Drift_Diffusion", "PN_Bandgap"]
            },
            {
                "code": "EC23C03",
                "discipline_name": "Electronic Devices & Circuit Modeling",
                "milestone": "Active BJT & MOSFET Non-Linear Models",
                "credits": 4,
                "prerequisites": ["EC23C02"],
                "core_concepts": ["Shockley_Diode", "Hybrid_Pi_BJT", "MOSFET_Subthreshold", "Small_Signal_gm"]
            },
            {
                "code": "EC23C05",
                "discipline_name": "Analog Integrated Circuit Design",
                "milestone": "Operational Amplifiers & Precision Feedback",
                "credits": 4,
                "prerequisites": ["EC23C03"],
                "core_concepts": ["Differential_CMRR", "Miller_Compensation", "Active_Filters", "Gain_Bandwidth"]
            }
        ]
    },

    "pathway_embedded": {
        "id": "pathway_embedded",
        "title": "Embedded & Computer Architecture",
        "industry_alignment": "Automotive Avionics, Deterministic Real-Time Systems",
        "total_credits": 14,
        "nodes": [
            {
                "code": "EC23C06",
                "discipline_name": "Digital Logic Design & Finite Automata",
                "milestone": "Synchronous Logic & State Machines",
                "credits": 4,
                "prerequisites": [],
                "core_concepts": ["Boolean_Algebra", "K_Map", "FSM_Mealy_Moore", "Setup_Hold_Slack"]
            },
            {
                "code": "EC8702",
                "discipline_name": "Embedded Real-Time Systems",
                "milestone": "Deterministic RTOS Kernels & Preemption",
                "credits": 3,
                "prerequisites": ["EC23C06"],
                "core_concepts": ["NVIC_Priority", "FreeRTOS_Queues", "Mutex_Priority_Inversion", "DMA_Ping_Pong"]
            },
            {
                "code": "STM32-ACADEMY",
                "discipline_name": "ARM Cortex-M Microcontroller Engineering",
                "milestone": "Bare-Metal Driver Synthesis & CMSIS Core",
                "credits": 4,
                "prerequisites": ["EC8702"],
                "core_concepts": ["Cortex_M4_Registers", "Clock_Tree_RCC", "Bare_Metal_HAL", "Circular_Buffer"]
            },
            {
                "code": "IOT8701",
                "discipline_name": "Internet of Things & Connected Systems",
                "milestone": "Cloud Edge Telemetry & Wireless Mesh",
                "credits": 3,
                "prerequisites": ["STM32-ACADEMY"],
                "core_concepts": ["MQTT_TLS", "Deep_Sleep_ULP", "BLE_GATT", "WebSerial_HIL"]
            }
        ]
    },

    "pathway_dsp_telecom": {
        "id": "pathway_dsp_telecom",
        "title": "Signal Processing & Communication Systems",
        "industry_alignment": "5G/6G Wireless Telecom, Audio/Radar Processing",
        "total_credits": 16,
        "nodes": [
            {
                "code": "EC23C01",
                "discipline_name": "Circuit Analysis & Network Synthesis",
                "milestone": "Frequency-Domain Impedance & Resonance",
                "credits": 4,
                "prerequisites": [],
                "core_concepts": ["RLC_Resonance", "Transfer_Functions", "Bode_Asymptotes"]
            },
            {
                "code": "EC23C04",
                "discipline_name": "Signals & Linear Systems Theory",
                "milestone": "LTI Convolution & Fourier Transforms",
                "credits": 4,
                "prerequisites": ["EC23C01"],
                "core_concepts": ["LTI_Convolution", "Fourier_Transform", "Laplace_ROC", "Z_Transform"]
            },
            {
                "code": "EC23C07",
                "discipline_name": "Control Systems Engineering",
                "milestone": "Feedback Stability & Nyquist Encirclements",
                "credits": 4,
                "prerequisites": ["EC23C04"],
                "core_concepts": ["Root_Locus", "Nyquist_Criterion", "Bode_Phase_Margin", "State_Space"]
            },
            {
                "code": "EC23S01",
                "discipline_name": "Digital Signal Processing & Algorithms",
                "milestone": "Multirate Filterbanks & Radix-2 FFT",
                "credits": 4,
                "prerequisites": ["EC23C04"],
                "core_concepts": ["Cooley_Tukey_FFT", "FIR_Parks_McClellan", "IIR_Butterworth", "Polyphase_Decimation"]
            },
            {
                "code": "EC23C08",
                "discipline_name": "Telecommunications & RF Engineering",
                "milestone": "RF Smith Chart & Digital Modulation",
                "credits": 4,
                "prerequisites": ["EC23S01", "EC23C07"],
                "core_concepts": ["Smith_Chart_Gamma", "QAM_Constellation", "Shannon_Capacity", "Friis_Free_Space"]
            }
        ]
    },

    "pathway_vlsi": {
        "id": "pathway_vlsi",
        "title": "VLSI & Digital Hardware Design",
        "industry_alignment": "ASIC Silicon Tape-Out, FPGA Acceleration",
        "total_credits": 12,
        "nodes": [
            {
                "code": "EC23C06",
                "discipline_name": "Digital Logic Design & Finite Automata",
                "milestone": "Combinational & Sequential RTL Basics",
                "credits": 4,
                "prerequisites": [],
                "core_concepts": ["Logic_Gates", "Mux_Decoders", "Flip_Flops", "Propagation_Delay"]
            },
            {
                "code": "HDL6001",
                "discipline_name": "FPGA Digital Design & Verilog HDL",
                "milestone": "Synthesizable RTL & Timing Closure",
                "credits": 4,
                "prerequisites": ["EC23C06"],
                "core_concepts": ["Verilog_RTL", "Non_Blocking_Assignments", "LUT_Mapping", "Static_Timing_Analysis"]
            },
            {
                "code": "VLSI7001",
                "discipline_name": "Digital VLSI Design & Silicon Layout",
                "milestone": "Sub-Micron CMOS Layout & RC Delay",
                "credits": 4,
                "prerequisites": ["HDL6001"],
                "core_concepts": ["Elmore_Delay", "Logical_Effort", "Clock_Tree_Skew", "DRC_LVS_Clean"]
            }
        ]
    },

    "pathway_ai_hardware": {
        "id": "pathway_ai_hardware",
        "title": "AI & Intelligent Hardware Systems",
        "industry_alignment": "Edge AI Inference, Neuromorphic Hardware",
        "total_credits": 14,
        "nodes": [
            {
                "code": "EC23S01",
                "discipline_name": "Digital Signal Processing & Algorithms",
                "milestone": "Discrete Mathematical Transforms & Quantization",
                "credits": 4,
                "prerequisites": [],
                "core_concepts": ["Fixed_Point_Qmn", "FFT_Spectrogram", "Windowing_Functions"]
            },
            {
                "code": "STM32-ACADEMY",
                "discipline_name": "ARM Cortex-M Microcontroller Engineering",
                "milestone": "CMSIS-DSP Acceleration on Cortex-M4",
                "credits": 3,
                "prerequisites": ["EC23S01"],
                "core_concepts": ["CMSIS_DSP", "Vector_Dot_Product", "DMA_Streams"]
            },
            {
                "code": "IOT8701",
                "discipline_name": "Internet of Things & Connected Systems",
                "milestone": "Edge Telemetry & Cloud Inference Bridge",
                "credits": 3,
                "prerequisites": ["STM32-ACADEMY"],
                "core_concepts": ["Edge_Gateway", "Telemetry_Pipelines", "MQTT_Publish"]
            },
            {
                "code": "TINYML-CORE",
                "discipline_name": "TinyML & Edge AI Accelerators",
                "milestone": "INT8 Quantized CNNs on Micro-Die",
                "credits": 4,
                "prerequisites": ["IOT8701", "STM32-ACADEMY"],
                "core_concepts": ["INT8_Symmetric_Quant", "Tensor_Arena", "Depthwise_Conv", "Latency_Energy_Budget"]
            }
        ]
    }
}


# -----------------------------------------------------------------------------
# 2. REMEDIAL CONCEPT DEPENDENCY GRAPH
# -----------------------------------------------------------------------------
# Maps advanced concepts to their underlying prerequisite concepts
CONCEPT_DEPENDENCY_GRAPH: Dict[str, Dict[str, Any]] = {
    "Elmore_Delay": {
        "prerequisite_concept": "RC_Time_Constants",
        "discipline_origin": "EC23C01",
        "diagnostic_question": "How does distributed RC interconnect delay scale with interconnect length L?",
        "diagnostic_solution": "Quadratic scaling O(L^2) due to both resistance and capacitance increasing linearly with length.",
        "remedial_title": "Interconnect RC Modeling & Time Constant Derivations",
        "remedial_formula": r"\tau = R \cdot C \quad \text{and} \quad \tau_{\text{Elmore}} = \sum_{k} R_{k} C_{k}"
    },
    "Root_Locus": {
        "prerequisite_concept": "Laplace_Pole_Zero_Mapping",
        "discipline_origin": "EC23C04",
        "diagnostic_question": "What is the angle condition for a point s to lie on the root locus of G(s)H(s)?",
        "diagnostic_solution": "The sum of angles of open-loop zeros minus poles must equal odd multiples of 180 degrees.",
        "remedial_title": "S-Domain Transfer Functions & Phase Angle Criteria",
        "remedial_formula": r"\angle G(s)H(s) = (2k + 1)\cdot 180^\circ"
    },
    "Smith_Chart_Gamma": {
        "prerequisite_concept": "Transmission_Line_Impedance",
        "discipline_origin": "EC23C01",
        "diagnostic_question": "What is the reflection coefficient Gamma when a transmission line of Z0 is terminated in a short circuit (ZL = 0)?",
        "diagnostic_solution": "Gamma = (0 - Z0) / (0 + Z0) = -1 (100% reflection with 180 degree phase shift).",
        "remedial_title": "Complex Reflection Coefficients & Normalization Principles",
        "remedial_formula": r"\Gamma = \frac{Z_L - Z_0}{Z_L + Z_0} = \frac{z - 1}{z + 1}"
    },
    "Cooley_Tukey_FFT": {
        "prerequisite_concept": "Discrete_Fourier_Transform_Sum",
        "discipline_origin": "EC23C04",
        "diagnostic_question": "How does radix-2 decimation-in-time reduce computational complexity from DFT O(N^2)?",
        "diagnostic_solution": "By decomposing into even and odd index sub-transforms, achieving O(N log2 N) operations.",
        "remedial_title": "Discrete Fourier Transform Symmetry & Twiddle Factor Geometry",
        "remedial_formula": r"W_N^k = e^{-j \frac{2\pi k}{N}}"
    },
    "INT8_Symmetric_Quant": {
        "prerequisite_concept": "Fixed_Point_Qmn",
        "discipline_origin": "EC23S01",
        "diagnostic_question": "In symmetric INT8 quantization, how is float value x mapped to quantized integer q?",
        "diagnostic_solution": "q = clip(round(x / scale), -127, 127), where scale = max(|x|) / 127.",
        "remedial_title": "Fixed-Point Q-Format & Dynamic Range Mapping",
        "remedial_formula": r"q = \text{round}\left(\frac{x}{S}\right), \quad S = \frac{\max(|x|)}{127}"
    }
}


# -----------------------------------------------------------------------------
# 3. LEARNING PATHWAY ENGINE IMPLEMENTATION
# -----------------------------------------------------------------------------
class LearningPathwayEngine:
    """Handles DAG traversal, mastery evaluation, and remedial dispatching."""

    def __init__(self, pathways_data: Optional[Dict[str, Dict[str, Any]]] = None):
        self.pathways = pathways_data or ACADEMIC_PATHWAYS

    def get_pathway(self, pathway_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves pathway specification with enriched subject emblem data."""
        p = self.pathways.get(pathway_id)
        if not p:
            return None

        enriched = dict(p)
        enriched_nodes = []
        for node in p.get("nodes", []):
            code = node["code"]
            emblem = get_subject_emblem(code)
            node_copy = dict(node)
            node_copy["primary_color"] = emblem.get("primary_color", "#00F0B5")
            node_copy["accent_color"] = emblem.get("accent_color", "#10B981")
            node_copy["symbol_name"] = emblem.get("symbol_name", "")
            node_copy["accessible_label"] = emblem.get("accessible_label", "")
            enriched_nodes.append(node_copy)

        enriched["nodes"] = enriched_nodes
        return enriched

    def list_all_pathways(self) -> List[Dict[str, Any]]:
        """Returns all 5 academic pathways with basic summary metadata."""
        summaries = []
        for pid in self.pathways.keys():
            enriched = self.get_pathway(pid)
            if enriched:
                summaries.append({
                    "id": enriched["id"],
                    "title": enriched["title"],
                    "industry_alignment": enriched["industry_alignment"],
                    "total_credits": enriched["total_credits"],
                    "nodes_count": len(enriched["nodes"])
                })
        return summaries

    def topological_sort_pathway(self, pathway_id: str) -> List[str]:
        """
        Computes valid topological sequence of disciplines within a pathway.
        Raises ValueError if circular dependency detected.
        """
        pathway = self.pathways.get(pathway_id)
        if not pathway:
            raise ValueError(f"Pathway {pathway_id} not found.")

        nodes = pathway.get("nodes", [])
        code_to_node = {n["code"]: n for n in nodes}
        in_degree = {n["code"]: 0 for n in nodes}
        adj = {n["code"]: [] for n in nodes}

        for n in nodes:
            code = n["code"]
            for prereq in n.get("prerequisites", []):
                if prereq in code_to_node:
                    adj[prereq].append(code)
                    in_degree[code] += 1

        queue = deque([code for code, deg in in_degree.items() if deg == 0])
        sorted_codes = []

        while queue:
            curr = queue.popleft()
            sorted_codes.append(curr)

            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(sorted_codes) != len(nodes):
            raise ValueError(f"Circular dependency detected in pathway {pathway_id}!")

        return sorted_codes

    def evaluate_student_progress(
        self,
        pathway_id: str,
        student_completed_nodes: Set[str],
        node_scores: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculates pathway completion percentage, attained credits, and currently unlocked nodes.
        """
        pathway = self.get_pathway(pathway_id)
        if not pathway:
            raise ValueError(f"Pathway {pathway_id} not found.")

        nodes = pathway["nodes"]
        total_nodes = len(nodes)
        total_credits = sum(n.get("credits", 0) for n in nodes)

        completed_count = 0
        attained_credits = 0
        unlocked_nodes = []
        locked_nodes = []

        scores = node_scores or {}

        for n in nodes:
            code = n["code"]
            prereqs = n.get("prerequisites", [])

            is_completed = code in student_completed_nodes
            prereqs_satisfied = all(p in student_completed_nodes for p in prereqs)

            if is_completed:
                completed_count += 1
                attained_credits += n.get("credits", 0)
                status = "COMPLETED"
            elif prereqs_satisfied:
                status = "UNLOCKED"
                unlocked_nodes.append(code)
            else:
                status = "LOCKED"
                locked_nodes.append(code)

        progress_pct = round((completed_count / total_nodes) * 100.0, 1) if total_nodes > 0 else 0.0

        return {
            "pathway_id": pathway_id,
            "title": pathway["title"],
            "progress_percentage": progress_pct,
            "completed_nodes": list(student_completed_nodes),
            "attained_credits": attained_credits,
            "total_credits": total_credits,
            "unlocked_next_nodes": unlocked_nodes,
            "locked_nodes": locked_nodes
        }

    # -------------------------------------------------------------------------
    # 4. REMEDIAL MICRO-LESSON DISPATCHING
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_remedial_micro_lesson(
        target_concept: str,
        telemetry_score: float,
        student_id: str = "2023MITEC042"
    ) -> Dict[str, Any]:
        """
        Generates a remedial learning package when concept score < 70%.
        Pinpoints underlying prerequisite concept and generates verification task.
        """
        dep = CONCEPT_DEPENDENCY_GRAPH.get(target_concept)
        if not dep:
            # Fallback for unregistered concepts
            return {
                "status": "PASS" if telemetry_score >= 70.0 else "GENERAL_REVIEW_REQUIRED",
                "student_id": student_id,
                "target_concept": target_concept,
                "telemetry_score": telemetry_score,
                "requires_remediation": telemetry_score < 70.0,
                "remedial_title": f"Review of {target_concept.replace('_', ' ')}",
                "prerequisite_concept": None
            }

        requires_remediation = telemetry_score < 70.0

        return {
            "status": "REMEDIAL_DISPATCHED" if requires_remediation else "MASTERY_SATISFIED",
            "student_id": student_id,
            "target_concept": target_concept,
            "telemetry_score": round(telemetry_score, 2),
            "requires_remediation": requires_remediation,
            "root_prerequisite": dep["prerequisite_concept"],
            "discipline_origin": dep["discipline_origin"],
            "discipline_name": get_discipline_name(dep["discipline_origin"]),
            "remedial_title": dep["remedial_title"],
            "mathematical_formula": dep["remedial_formula"],
            "diagnostic_task": {
                "question": dep["diagnostic_question"],
                "solution": dep["diagnostic_solution"]
            },
            "mastery_threshold_to_unlock": 75.0,
            "recommended_lab_bench": "VoltCore MNA / Oscilloscope Virtual Bench"
        }


# Global singleton instance
learning_pathway_engine = LearningPathwayEngine()
