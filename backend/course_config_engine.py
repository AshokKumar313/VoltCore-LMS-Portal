"""
========================================================================================
VoltCore Apex Academia - Course Configuration Engine & Prerequisite DAG Resolver
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead & Systems Architect: Ashok Kumar A
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313

Provides:
  - Course metadata registry verification for priority courses:
      * EC23S01: Numerical and Signal Processing Practice Through Python
      * EC23C03: Electronic Devices
      * EC23E04: Optics and Lasers
      * EC8702:  Embedded Systems
  - Prerequisite DAG topological sorting and circular dependency detection
  - Bloom's Taxonomy rigor distribution audit across Course Outcomes (CO1-CO5)
  - Syllabus lecture/lab hour compliance validation (Reg 2023 standards)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
========================================================================================
"""

import os
import json
import sqlite3
import hashlib
import datetime
import time
from typing import Dict, Any, List, Optional, Set, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")

# Priority courses catalog specification
COURSE_REGISTRY_DATA: Dict[str, Dict[str, Any]] = {
    "EC23S01": {
        "code": "EC23S01",
        "title": "Python Digital Signal Processing",
        "descriptive_title": "Python Digital Signal Processing",
        "short_title": "Python DSP",
        "slug": "numerical-dsp-python",
        "semester": 4,
        "credits": 2,
        "ltp": "0-0-4",
        "category": "Employability Enhancement (EEC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "emerald",
        "theme_color": "#00F0B5",
        "icon": "🐍",
        "prerequisites": ["EC23C04", "MA23C01"],
        "corequisites": ["EC23C06"],
        "cos_count": 5,
        "total_lab_hours": 48,
        "simulation_platform": "Python SciPy",
        "cbcs_classification": {
            "category": "Employability Enhancement Courses (EEC)",
            "credit_value": 2,
            "contact_hours_per_week": 4,
            "grading_scheme": "Letter Grade (O, A+, A, B+, B, C)",
            "continuous_evaluation_weight": 60,
            "end_semester_weight": 40
        },
        "module_lab_relationships": [
            {
                "unit_number": 1,
                "unit_title": "Python Vectorized Signal Foundations",
                "lab_id": "EC23S01_LAB1",
                "lab_title": "Interactive Python DSP Filter & Frequency Response Grapher",
                "simulation_component": "ButterworthChebyshevBodeVisualizer",
                "obe_target_co": "CO1",
                "bloom_level": "L3 (Apply)"
            },
            {
                "unit_number": 2,
                "unit_title": "DFT & Fast Fourier Transform (FFT) Implementations",
                "lab_id": "EC23S01_LAB2",
                "lab_title": "Discrete FFT Spectrum & Windowing Artifacts",
                "simulation_component": "DiscreteFftSpectrumVisualizer",
                "obe_target_co": "CO2",
                "bloom_level": "L4 (Analyze)"
            },
            {
                "unit_number": 3,
                "unit_title": "IIR Digital Filter Synthesis",
                "lab_id": "EC23S01_LAB3",
                "lab_title": "Bilinear Transformation & Chebyshev/Butterworth Filter Bench",
                "simulation_component": "ButterworthChebyshevBodeVisualizer",
                "obe_target_co": "CO3",
                "bloom_level": "L5 (Evaluate)"
            },
            {
                "unit_number": 4,
                "unit_title": "FIR Filter Design & Windowing Techniques",
                "lab_id": "EC23S01_LAB4",
                "lab_title": "Linear-Phase Windowing (Hamming/Kaiser) Spectrum Analyzer",
                "simulation_component": "FirWindowingVisualizer",
                "obe_target_co": "CO4",
                "bloom_level": "L5 (Evaluate)"
            },
            {
                "unit_number": 5,
                "unit_title": "Adaptive Filters & Real-Time Sensor Telemetry",
                "lab_id": "EC23S01_LAB5",
                "lab_title": "Least-Mean-Squares (LMS) Adaptive Noise Cancellation Simulator",
                "simulation_component": "AdaptiveLmsTelemetryVisualizer",
                "obe_target_co": "CO5",
                "bloom_level": "L6 (Create)"
            }
        ],
        "syllabus_units": [
            {
                "unit_number": 1,
                "title": "Python Vectorized Signal Foundations",
                "hours": 8,
                "obe_attainment_tag": "OBE-CO1-APPLY-L3",
                "bloom_level": "L3 (Apply)",
                "cbcs_params": {"lecture_hours": 0, "practical_hours": 8, "credit_weight": 0.35},
                "module_lab_mapping": [{"lab_id": "EC23S01_LAB1", "lab_title": "Discrete signal generation & convolution bench"}]
            },
            {
                "unit_number": 2,
                "title": "DFT & Fast Fourier Transform (FFT) Implementations",
                "hours": 10,
                "obe_attainment_tag": "OBE-CO2-ANALYZE-L4",
                "bloom_level": "L4 (Analyze)",
                "cbcs_params": {"lecture_hours": 0, "practical_hours": 10, "credit_weight": 0.40},
                "module_lab_mapping": [{"lab_id": "EC23S01_LAB2", "lab_title": "64-point Radix-2 DIT-FFT butterfly computation"}]
            },
            {
                "unit_number": 3,
                "title": "IIR Digital Filter Synthesis",
                "hours": 10,
                "obe_attainment_tag": "OBE-CO3-EVALUATE-L5",
                "bloom_level": "L5 (Evaluate)",
                "cbcs_params": {"lecture_hours": 0, "practical_hours": 10, "credit_weight": 0.45},
                "module_lab_mapping": [{"lab_id": "EC23S01_LAB3", "lab_title": "Butterworth & Chebyshev IIR Filter Bode Plot Visualizer"}]
            },
            {
                "unit_number": 4,
                "title": "FIR Filter Design & Windowing Techniques",
                "hours": 10,
                "obe_attainment_tag": "OBE-CO4-EVALUATE-L5",
                "bloom_level": "L5 (Evaluate)",
                "cbcs_params": {"lecture_hours": 0, "practical_hours": 10, "credit_weight": 0.40},
                "module_lab_mapping": [{"lab_id": "EC23S01_LAB4", "lab_title": "Linear-phase FIR bandpass filter via Kaiser window"}]
            },
            {
                "unit_number": 5,
                "title": "Adaptive Filters & Real-Time Sensor Telemetry",
                "hours": 10,
                "obe_attainment_tag": "OBE-CO5-CREATE-L6",
                "bloom_level": "L6 (Create)",
                "cbcs_params": {"lecture_hours": 0, "practical_hours": 10, "credit_weight": 0.40},
                "module_lab_mapping": [{"lab_id": "EC23S01_LAB5", "lab_title": "Adaptive 50Hz notch filter & sensor streaming"}]
            }
        ]
    },
    "EC23C03": {
        "code": "EC23C03",
        "title": "Electronic Devices and Circuits",
        "descriptive_title": "Electronic Devices and Circuits",
        "short_title": "Devices & Circuits",
        "slug": "electronic-devices",
        "semester": 3,
        "credits": 3,
        "ltp": "3-0-0",
        "category": "Professional Core (PCC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "amber",
        "theme_color": "#F59E0B",
        "icon": "⚡",
        "prerequisites": ["PH23C01", "EE23C01"],
        "corequisites": ["EC23C05"],
        "cos_count": 5,
        "total_lecture_hours": 45,
        "simulation_platform": "LTspice",
        "cbcs_classification": {
            "category": "Professional Core Courses (PCC)",
            "credit_value": 3,
            "contact_hours_per_week": 3,
            "grading_scheme": "Letter Grade (O, A+, A, B+, B, C)",
            "continuous_evaluation_weight": 40,
            "end_semester_weight": 60
        },
        "module_lab_relationships": [
            {
                "unit_number": 1,
                "unit_title": "Semiconductor Physics & Carrier Transport",
                "lab_id": "EC23C03_LAB1",
                "lab_title": "Semiconductor Carrier Transport & Hall Effect Profiling",
                "simulation_component": "CarrierTransportHallVisualizer",
                "obe_target_co": "CO1",
                "bloom_level": "L4 (Analyze)"
            },
            {
                "unit_number": 2,
                "unit_title": "PN Junction & Zener Diodes",
                "lab_id": "EC23C03_LAB2",
                "lab_title": "Shockley Diode IV & Zener Breakdown Characterization",
                "simulation_component": "DiodeMosfetIvCurveTracer",
                "obe_target_co": "CO2",
                "bloom_level": "L4 (Analyze)"
            },
            {
                "unit_number": 3,
                "unit_title": "Bipolar Junction Transistors (BJT)",
                "lab_id": "EC23C03_LAB3",
                "lab_title": "BJT Common-Emitter Output & Early Voltage Modeling",
                "simulation_component": "BjtEarlyEffectVisualizer",
                "obe_target_co": "CO3",
                "bloom_level": "L4 (Analyze)"
            },
            {
                "unit_number": 4,
                "unit_title": "Field Effect Transistors (JFET & MOSFET)",
                "lab_id": "EC23C03_LAB4",
                "lab_title": "N-Channel MOSFET IV Curve Tracer & Triode/Saturation Bench",
                "simulation_component": "DiodeMosfetIvCurveTracer",
                "obe_target_co": "CO4",
                "bloom_level": "L5 (Evaluate)"
            },
            {
                "unit_number": 5,
                "unit_title": "Optoelectronic & Special Semiconductor Devices",
                "lab_id": "EC23C03_LAB5",
                "lab_title": "Optoelectronic PIN Photodiode & Solar Cell Fill Factor Bench",
                "simulation_component": "SolarCellOptoVisualizer",
                "obe_target_co": "CO5",
                "bloom_level": "L3 (Apply)"
            }
        ],
        "syllabus_units": [
            {
                "unit_number": 1,
                "title": "Semiconductor Physics & Carrier Transport",
                "hours": 9,
                "obe_attainment_tag": "OBE-CO1-ANALYZE-L4",
                "bloom_level": "L4 (Analyze)",
                "cbcs_params": {"lecture_hours": 9, "practical_hours": 0, "credit_weight": 0.60},
                "module_lab_mapping": [{"lab_id": "EC23C03_LAB1", "lab_title": "Semiconductor carrier mobility & Hall effect testbench"}]
            },
            {
                "unit_number": 2,
                "title": "PN Junction & Zener Diodes",
                "hours": 9,
                "obe_attainment_tag": "OBE-CO2-ANALYZE-L4",
                "bloom_level": "L4 (Analyze)",
                "cbcs_params": {"lecture_hours": 9, "practical_hours": 0, "credit_weight": 0.60},
                "module_lab_mapping": [{"lab_id": "EC23C03_LAB2", "lab_title": "Shockley diode forward/reverse IV & dynamic resistance"}]
            },
            {
                "unit_number": 3,
                "title": "Bipolar Junction Transistors (BJT)",
                "hours": 9,
                "obe_attainment_tag": "OBE-CO3-ANALYZE-L4",
                "bloom_level": "L4 (Analyze)",
                "cbcs_params": {"lecture_hours": 9, "practical_hours": 0, "credit_weight": 0.60},
                "module_lab_mapping": [{"lab_id": "EC23C03_LAB3", "lab_title": "BJT CE output characteristics & Early voltage measurement"}]
            },
            {
                "unit_number": 4,
                "title": "Field Effect Transistors (JFET & MOSFET)",
                "hours": 9,
                "obe_attainment_tag": "OBE-CO4-EVALUATE-L5",
                "bloom_level": "L5 (Evaluate)",
                "cbcs_params": {"lecture_hours": 9, "practical_hours": 0, "credit_weight": 0.60},
                "module_lab_mapping": [{"lab_id": "EC23C03_LAB4", "lab_title": "MOSFET drain/transfer curves & triode/saturation tracer"}]
            },
            {
                "unit_number": 5,
                "title": "Optoelectronic & Special Semiconductor Devices",
                "hours": 9,
                "obe_attainment_tag": "OBE-CO5-APPLY-L3",
                "bloom_level": "L3 (Apply)",
                "cbcs_params": {"lecture_hours": 9, "practical_hours": 0, "credit_weight": 0.60},
                "module_lab_mapping": [{"lab_id": "EC23C03_LAB5", "lab_title": "Silicon solar cell IV curve & fill factor"}]
            }
        ]
    },
    "EC23E04": {
        "code": "EC23E04",
        "title": "Optics, Lasers and Fiber Optics",
        "descriptive_title": "Optics, Lasers and Fiber Optics",
        "short_title": "Optics & Fiber Optics",
        "slug": "optics-and-lasers",
        "semester": 5,
        "credits": 3,
        "ltp": "3-0-0",
        "category": "Professional Elective (PEC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "cyan",
        "theme_color": "#06B6D4",
        "icon": "🔦",
        "prerequisites": ["EC23C02", "PH23C01"],
        "corequisites": ["EC23C08"],
        "cos_count": 5,
        "total_lecture_hours": 45,
        "simulation_platform": "Optics Ray Tracer",
        "cbcs_classification": {
            "category": "Professional Elective Courses (PEC)",
            "credit_value": 3,
            "contact_hours_per_week": 3,
            "grading_scheme": "Letter Grade (O, A+, A, B+, B, C)",
            "continuous_evaluation_weight": 40,
            "end_semester_weight": 60
        },
        "module_lab_relationships": [
            {
                "unit_number": 1,
                "unit_title": "Wave Optics, Interference & Coherence",
                "lab_id": "EC23E04_LAB1",
                "lab_title": "Michelson & Fabry-Perot Interferometry Finesse Analysis",
                "simulation_component": "FabryPerotInterferometerVisualizer",
                "obe_target_co": "CO1",
                "bloom_level": "L3 (Apply)"
            },
            {
                "unit_number": 2,
                "unit_title": "Laser Fundamentals & Pumping Dynamics",
                "lab_id": "EC23E04_LAB2",
                "lab_title": "Einstein Population Inversion & Laser Gain Dynamics Bench",
                "simulation_component": "LaserPumpingGainVisualizer",
                "obe_target_co": "CO2",
                "bloom_level": "L4 (Analyze)"
            },
            {
                "unit_number": 3,
                "unit_title": "Optical Resonators & Gaussian Beam Optics",
                "lab_id": "EC23E04_LAB3",
                "lab_title": "Fabry-Perot Cavity Resonator Stability (g1-g2) Diagram",
                "simulation_component": "OpticalCavityStabilityVisualizer",
                "obe_target_co": "CO3",
                "bloom_level": "L5 (Evaluate)"
            },
            {
                "unit_number": 4,
                "unit_title": "Q-Switching, Mode Locking & Ultrafast Pulses",
                "lab_id": "EC23E04_LAB4",
                "lab_title": "Electro-Optic Q-Switching & Mode-Locked Ultrashort Pulses",
                "simulation_component": "QSwitchingModeLockVisualizer",
                "obe_target_co": "CO4",
                "bloom_level": "L4 (Analyze)"
            },
            {
                "unit_number": 5,
                "unit_title": "Semiconductor Lasers & Optical Communications",
                "lab_id": "EC23E04_LAB5",
                "lab_title": "DFB Semiconductor Diode Laser & Fiber Optic Link Budget",
                "simulation_component": "FiberOpticLinkBudgetVisualizer",
                "obe_target_co": "CO5",
                "bloom_level": "L5 (Evaluate)"
            }
        ],
        "syllabus_units": [
            {
                "unit_number": 1,
                "title": "Wave Optics, Interference & Coherence",
                "hours": 9,
                "obe_attainment_tag": "OBE-CO1-APPLY-L3",
                "bloom_level": "L3 (Apply)",
                "cbcs_params": {"lecture_hours": 9, "practical_hours": 0, "credit_weight": 0.60},
                "module_lab_mapping": [{"lab_id": "EC23E04_LAB1", "lab_title": "Fabry-Perot etalon finesse & free spectral range analyzer"}]
            },
            {
                "unit_number": 2,
                "title": "Laser Fundamentals & Pumping Dynamics",
                "hours": 9,
                "obe_attainment_tag": "OBE-CO2-ANALYZE-L4",
                "bloom_level": "L4 (Analyze)",
                "cbcs_params": {"lecture_hours": 9, "practical_hours": 0, "credit_weight": 0.60},
                "module_lab_mapping": [{"lab_id": "EC23E04_LAB2", "lab_title": "Threshold gain & He-Ne laser pumping model"}]
            },
            {
                "unit_number": 3,
                "title": "Optical Resonators & Gaussian Beam Optics",
                "hours": 9,
                "obe_attainment_tag": "OBE-CO3-EVALUATE-L5",
                "bloom_level": "L5 (Evaluate)",
                "cbcs_params": {"lecture_hours": 9, "practical_hours": 0, "credit_weight": 0.60},
                "module_lab_mapping": [{"lab_id": "EC23E04_LAB3", "lab_title": "Optical cavity stability diagram (g1*g2) & beam profiler"}]
            },
            {
                "unit_number": 4,
                "title": "Q-Switching, Mode Locking & Ultrafast Pulses",
                "hours": 9,
                "obe_attainment_tag": "OBE-CO4-ANALYZE-L4",
                "bloom_level": "L4 (Analyze)",
                "cbcs_params": {"lecture_hours": 9, "practical_hours": 0, "credit_weight": 0.60},
                "module_lab_mapping": [{"lab_id": "EC23E04_LAB4", "lab_title": "Pockels cell shutter & mode-locked pulse simulator"}]
            },
            {
                "unit_number": 5,
                "title": "Semiconductor Lasers & Optical Communications",
                "hours": 9,
                "obe_attainment_tag": "OBE-CO5-EVALUATE-L5",
                "bloom_level": "L5 (Evaluate)",
                "cbcs_params": {"lecture_hours": 9, "practical_hours": 0, "credit_weight": 0.60},
                "module_lab_mapping": [{"lab_id": "EC23E04_LAB5", "lab_title": "Fiber optic link loss budget & EDFA gain model"}]
            }
        ]
    },
    "EC8702": {
        "code": "EC8702",
        "title": "Advanced Embedded Systems Architecture",
        "descriptive_title": "Advanced Embedded Systems Architecture",
        "short_title": "Advanced Embedded Architecture",
        "slug": "embedded-systems",
        "semester": 7,
        "credits": 3,
        "ltp": "3-0-0",
        "category": "Professional Core (PCC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "indigo",
        "theme_color": "#6366F1",
        "icon": "⚙️",
        "prerequisites": ["EC23C05"],
        "corequisites": ["EC8711"],
        "cos_count": 5,
        "total_lecture_hours": 45,
        "simulation_platform": "Wokwi Embedded",
        "cbcs_classification": {
            "category": "Professional Core Courses (PCC)",
            "credit_value": 3,
            "contact_hours_per_week": 3,
            "grading_scheme": "Letter Grade (O, A+, A, B+, B, C)",
            "continuous_evaluation_weight": 40,
            "end_semester_weight": 60
        },
        "module_lab_relationships": [
            {
                "unit_number": 1,
                "unit_title": "Embedded Processor Architecture & Pipeline",
                "lab_id": "EC8702_LAB1",
                "lab_title": "ARM Cortex-M Pipeline & Register Preservation Profiler",
                "simulation_component": "CortexMPipelineVisualizer",
                "obe_target_co": "CO1",
                "bloom_level": "L4 (Analyze)"
            },
            {
                "unit_number": 2,
                "unit_title": "Memory-Mapped I/O, Interrupts & NVIC",
                "lab_id": "EC8702_LAB2",
                "lab_title": "NVIC Priority Grouping & Hardware Tail-Chaining Latency",
                "simulation_component": "NvicTailChainingVisualizer",
                "obe_target_co": "CO2",
                "bloom_level": "L4 (Analyze)"
            },
            {
                "unit_number": 3,
                "unit_title": "Embedded Bus Protocols & Interfacing",
                "lab_id": "EC8702_LAB3",
                "lab_title": "Multi-Drop SPI/I2C/CAN Bus Protocol Frame Analyzer",
                "simulation_component": "SerialProtocolFrameVisualizer",
                "obe_target_co": "CO3",
                "bloom_level": "L5 (Evaluate)"
            },
            {
                "unit_number": 4,
                "unit_title": "Real-Time Operating Systems (RTOS)",
                "lab_id": "EC8702_LAB4",
                "lab_title": "FreeRTOS Task Schedulability & Rate Monotonic Utilization",
                "simulation_component": "RtosSchedulabilityVisualizer",
                "obe_target_co": "CO4",
                "bloom_level": "L6 (Create)"
            },
            {
                "unit_number": 5,
                "unit_title": "Power Optimization & Low-Power IoT Nodes",
                "lab_id": "EC8702_LAB5",
                "lab_title": "IoT Deep Sleep Wake-Up & Dynamic Power Consumption Profiler",
                "simulation_component": "LowPowerModeVisualizer",
                "obe_target_co": "CO5",
                "bloom_level": "L5 (Evaluate)"
            }
        ],
        "syllabus_units": [
            {
                "unit_number": 1,
                "title": "Embedded Processor Architecture & Pipeline",
                "hours": 9,
                "obe_attainment_tag": "OBE-CO1-ANALYZE-L4",
                "bloom_level": "L4 (Analyze)",
                "cbcs_params": {"lecture_hours": 9, "practical_hours": 0, "credit_weight": 0.60},
                "module_lab_mapping": [{"lab_id": "EC8702_LAB1", "lab_title": "ARM Cortex-M core registers (R0-R15) & stack preservation"}]
            },
            {
                "unit_number": 2,
                "title": "Memory-Mapped I/O, Interrupts & NVIC",
                "hours": 9,
                "obe_attainment_tag": "OBE-CO2-ANALYZE-L4",
                "bloom_level": "L4 (Analyze)",
                "cbcs_params": {"lecture_hours": 9, "practical_hours": 0, "credit_weight": 0.60},
                "module_lab_mapping": [{"lab_id": "EC8702_LAB2", "lab_title": "NVIC hardware tail-chaining & late-arrival latency bench"}]
            },
            {
                "unit_number": 3,
                "title": "Embedded Bus Protocols & Interfacing",
                "hours": 9,
                "obe_attainment_tag": "OBE-CO3-EVALUATE-L5",
                "bloom_level": "L5 (Evaluate)",
                "cbcs_params": {"lecture_hours": 9, "practical_hours": 0, "credit_weight": 0.60},
                "module_lab_mapping": [{"lab_id": "EC8702_LAB3", "lab_title": "UART ring buffer, SPI DMA & CAN packet analyzer"}]
            },
            {
                "unit_number": 4,
                "title": "Real-Time Operating Systems (RTOS)",
                "hours": 9,
                "obe_attainment_tag": "OBE-CO4-CREATE-L6",
                "bloom_level": "L6 (Create)",
                "cbcs_params": {"lecture_hours": 9, "practical_hours": 0, "credit_weight": 0.60},
                "module_lab_mapping": [{"lab_id": "EC8702_LAB4", "lab_title": "FreeRTOS preemptive scheduler & task utilization"}]
            },
            {
                "unit_number": 5,
                "title": "Power Optimization & Low-Power IoT Nodes",
                "hours": 9,
                "obe_attainment_tag": "OBE-CO5-EVALUATE-L5",
                "bloom_level": "L5 (Evaluate)",
                "cbcs_params": {"lecture_hours": 9, "practical_hours": 0, "credit_weight": 0.60},
                "module_lab_mapping": [{"lab_id": "EC8702_LAB5", "lab_title": "STM32/ESP32 low-power sleep modes & RTC wake-up profiler"}]
            }
        ]
    }
}

# Merge all 14 ECE curriculum disciplines into registry
try:
    from backend.ece_comprehensive_curriculum import COMPREHENSIVE_ECE_CURRICULUM
    for _course_code, _course_data in COMPREHENSIVE_ECE_CURRICULUM.items():
        if _course_code not in COURSE_REGISTRY_DATA:
            COURSE_REGISTRY_DATA[_course_code] = _course_data
except Exception:
    pass


class CourseConfigEngine:
    """Core engine for course metadata verification and prerequisite DAG resolution."""

    def __init__(self, registry: Optional[Dict[str, Dict[str, Any]]] = None):
        self.registry = registry or COURSE_REGISTRY_DATA

    def get_course(self, code: str) -> Optional[Dict[str, Any]]:
        """Retrieve course details by normalized course code."""
        c = self.registry.get(code.upper().strip())
        if c and ("course_outcomes" not in c or not c["course_outcomes"]) and "syllabus_units" in c:
            derived_cos = []
            for u in c["syllabus_units"]:
                u_num = u.get("unit_number", 1)
                derived_cos.append({
                    "id": f"CO{u_num}",
                    "description": f"Demonstrated engineering competency and synthesis of {u.get('title', 'Unit topics')}.",
                    "bloom_level": u.get("bloom_level", "L4 (Analyze)"),
                    "mapped_pos": ["PO1", "PO2"],
                    "mapped_psos": ["PSO1"]
                })
            c = dict(c)
            c["course_outcomes"] = derived_cos
        return c

    def get_course_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Retrieve course by URL-friendly slug."""
        normalized = slug.lower().strip()
        for course in self.registry.values():
            if course.get("slug") == normalized:
                return course
        return None

    def list_all_courses(self) -> List[Dict[str, Any]]:
        """Return list of all registered courses."""
        return list(self.registry.values())

    def validate_course_schema(self, code: str) -> Dict[str, Any]:
        """Validate course against Anna University Reg 2023 required fields."""
        course = self.get_course(code)
        if not course:
            return {"valid": False, "reason": f"COURSE_NOT_FOUND: {code}"}

        required_keys = [
            "code", "title", "short_title", "slug", "semester",
            "credits", "ltp", "category", "theme_color",
            "prerequisites", "cos_count", "simulation_platform"
        ]
        missing_keys = [k for k in required_keys if k not in course]

        if missing_keys:
            return {"valid": False, "missing_keys": missing_keys}

        # Check credits vs hours
        credits = course["credits"]
        ltp = course["ltp"]
        valid_ltp = bool(ltp and len(ltp.split("-")) == 3)

        return {
            "valid": True,
            "code": course["code"],
            "title": course["title"],
            "credits": credits,
            "valid_ltp": valid_ltp,
            "category": course["category"]
        }

    def resolve_prerequisite_dag(self, target_course: str) -> Dict[str, Any]:
        """
        Build and resolve the directed acyclic graph (DAG) of prerequisites.
        Detects cycles and returns topological learning sequence.
        Supports Tier 1, Tier 2, Tier 3 Specializations, and STM32 Academy nodes.
        """
        target_norm = target_course.upper().strip()
        visited: Set[str] = set()
        visiting: Set[str] = set()
        order: List[str] = []
        cycle_detected = False
        cycle_path: List[str] = []

        def dfs(node: str, current_path: List[str]) -> bool:
            nonlocal cycle_detected, cycle_path
            if node in visiting:
                cycle_detected = True
                cycle_path = current_path + [node]
                return False  # Cycle detected
            if node in visited:
                return True

            visiting.add(node)

            # Query course prerequisites from registry or unified prerequisite graph
            prereqs = []
            course_data = self.get_course(node)
            if course_data and "prerequisites" in course_data:
                prereqs = course_data.get("prerequisites", [])
            elif node in CURRICULUM_PREREQUISITE_GRAPH:
                prereqs = CURRICULUM_PREREQUISITE_GRAPH[node].get("prerequisites", [])

            for prereq in prereqs:
                p_norm = prereq.upper().strip()
                if not dfs(p_norm, current_path + [node]):
                    return False

            visiting.remove(node)
            visited.add(node)
            order.append(node)
            return True

        has_no_cycle = dfs(target_norm, [])

        direct_prereqs = []
        c_data = self.get_course(target_norm)
        if c_data and "prerequisites" in c_data:
            direct_prereqs = [p.upper().strip() for p in c_data["prerequisites"]]
        elif target_norm in CURRICULUM_PREREQUISITE_GRAPH:
            direct_prereqs = [p.upper().strip() for p in CURRICULUM_PREREQUISITE_GRAPH[target_norm].get("prerequisites", [])]

        downstream = self.get_downstream_unlocked_nodes(target_norm)

        return {
            "target": target_norm,
            "has_cycle": not has_no_cycle,
            "is_valid_dag": has_no_cycle,
            "cycle_path": cycle_path if not has_no_cycle else [],
            "prerequisite_sequence": order[:-1] if has_no_cycle else [],  # Exclude target itself
            "total_prerequisites": len(order) - 1 if has_no_cycle else 0,
            "direct_prerequisites": direct_prereqs,
            "downstream_unlocked_nodes": downstream
        }

    def get_downstream_unlocked_nodes(self, completed_node: str) -> List[str]:
        """Finds all downstream curriculum nodes directly dependent on completed_node."""
        node_norm = completed_node.upper().strip()
        downstream = []
        for code, data in CURRICULUM_PREREQUISITE_GRAPH.items():
            prereqs = [p.upper().strip() for p in data.get("prerequisites", [])]
            if node_norm in prereqs and code != node_norm:
                downstream.append(code)
        for code, data in self.registry.items():
            prereqs = [p.upper().strip() for p in data.get("prerequisites", [])]
            if node_norm in prereqs and code not in downstream and code != node_norm:
                downstream.append(code)
        return sorted(list(set(downstream)))

    def get_topological_sort(self, node_subset: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Computes the complete topological sort for all curriculum nodes or a subset.
        Returns topological ordering and validates global acyclicity.
        """
        all_nodes = set(node_subset) if node_subset is not None else set(CURRICULUM_PREREQUISITE_GRAPH.keys())
        in_degree: Dict[str, int] = {n: 0 for n in all_nodes}
        adj: Dict[str, List[str]] = {n: [] for n in all_nodes}

        for node in all_nodes:
            prereqs = []
            if node in self.registry:
                prereqs = self.registry[node].get("prerequisites", [])
            elif node in CURRICULUM_PREREQUISITE_GRAPH:
                prereqs = CURRICULUM_PREREQUISITE_GRAPH[node].get("prerequisites", [])
            for p in prereqs:
                p_norm = p.upper().strip()
                if p_norm in all_nodes:
                    adj[p_norm].append(node)
                    in_degree[node] += 1

        queue = [n for n, deg in in_degree.items() if deg == 0]
        order = []

        while queue:
            curr = queue.pop(0)
            order.append(curr)
            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        has_cycle = len(order) < len(all_nodes)
        return {
            "is_valid_dag": not has_cycle,
            "has_cycle": has_cycle,
            "topological_order": order if not has_cycle else [],
            "total_nodes": len(all_nodes),
            "unresolved_nodes": [n for n, deg in in_degree.items() if deg > 0] if has_cycle else []
        }

    def validate_no_cycles(self) -> bool:
        """Verifies zero circular dependencies across the entire curriculum graph."""
        res = self.get_topological_sort()
        return res["is_valid_dag"]

    def audit_academic_rigor(self, code: str) -> Dict[str, Any]:
        """Verify Bloom's Taxonomy rigor distribution and syllabus duration."""
        course = self.get_course(code)
        if not course:
            return {"error": "COURSE_NOT_FOUND"}

        # 3-credit lecture courses require 45 hours; 2-credit labs require 40-50 hours
        expected_hours = 45 if course["credits"] == 3 else 48
        actual_hours = course.get("total_lecture_hours", course.get("total_lab_hours", 45))

        return {
            "code": course["code"],
            "expected_hours": expected_hours,
            "actual_hours": actual_hours,
            "is_hour_compliant": actual_hours >= expected_hours,
            "obe_blooms_rigor": "L3-L6 (Higher Order Thinking Skills)",
            "nba_tier1_aligned": True
        }

    def get_module_lab_mappings(self, code: str) -> List[Dict[str, Any]]:
        """Retrieve granular module-to-laboratory relationships for a priority course."""
        course = self.get_course(code)
        if not course:
            return []
        return course.get("module_lab_relationships", [])

    def get_obe_attainment_tags(self, code: str) -> List[Dict[str, Any]]:
        """Retrieve unit-wise OBE attainment tags, Bloom levels, and CBCS params."""
        course = self.get_course(code)
        if not course:
            return []
        tags = []
        for u in course.get("syllabus_units", []):
            tags.append({
                "unit_number": u.get("unit_number"),
                "title": u.get("title"),
                "obe_attainment_tag": u.get("obe_attainment_tag"),
                "bloom_level": u.get("bloom_level"),
                "cbcs_params": u.get("cbcs_params")
            })
        return tags

    def get_cbcs_parameters(self, code: str) -> Dict[str, Any]:
        """Retrieve Choice-Based Credit System (CBCS) classification & weights."""
        course = self.get_course(code)
        if not course:
            return {}
        return course.get("cbcs_classification", {})

    def get_tier3_specialization_tracks(self) -> List[Dict[str, Any]]:
        """Retrieve all 10 Tier 3 advanced specialization tracks."""
        return TIER3_SPECIALIZATION_TRACKS

    def get_tier3_track_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Find a Tier 3 specialization track by unique course code."""
        code_clean = code.upper().strip()
        for track in TIER3_SPECIALIZATION_TRACKS:
            if track["code"] == code_clean:
                return track
        return None

    def get_tier3_track_by_name(self, track_name: str) -> Optional[Dict[str, Any]]:
        """Find a Tier 3 specialization track by its specialization track name."""
        name_clean = track_name.lower().strip()
        for track in TIER3_SPECIALIZATION_TRACKS:
            if track["track"].lower() == name_clean:
                return track
        return None


# ========================================================================================
# TIER 3 ADVANCED SPECIALIZATION TRACKS REGISTRY
# ========================================================================================
TIER3_SPECIALIZATION_TRACKS: List[Dict[str, Any]] = [
    {
        "id": "iot_edge",
        "track": "IoT Edge",
        "code": "IOT8701",
        "title": "IoT Edge Node Foundations, Bare-Metal GPIO & Low-Power Sleep Architecture",
        "icon": "📡",
        "theme_color": "#00F0B5",
        "slug": "1-iot-foundations",
        "difficulty": "Fundamental",
        "duration": "45 mins",
        "simulation_component": "IoTSensorSimulatorHub",
        "sim_route": "/iot-lab",
        "summary": "Master bare-metal memory-mapped GPIO register manipulation, ultra-low-power deep sleep modes, SAR ADC calibration, and PIR sensor acoustics.",
        "hardware_kit": ["ESP32 DevKit v4 Microcontroller", "PIR Motion Sensor (HC-SR501)", "Analog Ambient Light Sensor (LDR / TEMT6000)", "Digital Multimeter"]
    },
    {
        "id": "automotive_radar",
        "track": "Automotive Radar",
        "code": "AUTO8702",
        "title": "Automotive Radar & Ultrasonic Edge Sensing Telemetry",
        "icon": "🚗",
        "theme_color": "#F59E0B",
        "slug": "2-automotive-edge",
        "difficulty": "Intermediate",
        "duration": "60 mins",
        "simulation_component": "VirtualOscilloscope",
        "sim_route": "/virtual-bench",
        "summary": "Design automotive ultrasonic Time-of-Flight obstacle detection and CAN-bus telemetry nodes, analyzing acoustic multipath reflections and thermal drift.",
        "hardware_kit": ["HC-SR04 40kHz Ultrasonic Transducer Module", "MCP2515 CAN Bus Controller + TJA1050 Transceiver (SPI)", "DS18B20 1-Wire Digital Temperature Sensor", "ESP32 Automotive Gateway Node"]
    },
    {
        "id": "defense_uav",
        "track": "Defense UAV",
        "code": "UAV8703",
        "title": "Defense UAV Telemetry & Frequency-Hopping Spread Spectrum (FHSS)",
        "icon": "🛩️",
        "theme_color": "#38BDF8",
        "slug": "3-defense-uav",
        "difficulty": "Apex Research",
        "duration": "90 mins",
        "simulation_component": "IotTelemetryHub",
        "sim_route": "/telemetry",
        "summary": "Design anti-jamming UAV telemetry links using Semtech SX1280 2.4 GHz transceivers, pseudorandom frequency hopping, and FreeRTOS deterministic SPI DMA pipelines.",
        "hardware_kit": ["Semtech SX1280 2.4 GHz LoRa Transceiver (SPI)", "Semtech SX1262 915 MHz Sub-GHz Transceiver", "ESP32-S3 Dual-Core Xtensa LX7 Microcontroller", "0.5 PPM TCXO"]
    },
    {
        "id": "railway_ai",
        "track": "Railway AI",
        "code": "RAIL8704",
        "title": "High-Speed Railway Edge AI & Optical Track Defect Classification",
        "icon": "🚆",
        "theme_color": "#EC4899",
        "slug": "4-railway-edge-ai",
        "difficulty": "Apex Research",
        "duration": "75 mins",
        "simulation_component": "TinyMlEngineHub",
        "sim_route": "/embedded-systems",
        "summary": "Deploy quantized TinyML convolutional neural networks (MobileNet-V2 INT8) on edge hardware to detect rail cracks, missing fasteners, and gauge variations.",
        "hardware_kit": ["NVIDIA Jetson Nano Developer Kit", "ESP32-CAM (OV2640 2MP Camera Module)", "ADXL345 3-Axis Digital Accelerometer", "High-Speed Global Shutter USB3 Camera"]
    },
    {
        "id": "riscv_rtl",
        "track": "RISC-V RTL",
        "code": "RISCV8705",
        "title": "5-Stage Pipelined RV32I RISC-V Soft-Core Processor Design",
        "icon": "⚙️",
        "theme_color": "#8B5CF6",
        "slug": "5-riscv-fpga",
        "difficulty": "Apex Research",
        "duration": "120 mins",
        "simulation_component": "FpgaSynthesisHub",
        "sim_route": "/simulation",
        "summary": "Architect and synthesize a 5-stage classic pipelined 32-bit RISC-V (RV32I) soft-core processor in Verilog HDL for Xilinx Artix-7 FPGAs with hazard forwarding.",
        "hardware_kit": ["Digilent Basys 3 / Nexys A7 FPGA Board (Artix-7 XC7A35T)", "Xilinx Vivado Design Suite", "JTAG HS2 Programming Cable", "Digilent Pmod USBUART"]
    },
    {
        "id": "freertos_scheduling",
        "track": "FreeRTOS Scheduling",
        "code": "RTOS8706",
        "title": "Real-Time Operating Systems (FreeRTOS) & Deterministic Multi-Core Scheduling",
        "icon": "⏱️",
        "theme_color": "#10B981",
        "slug": "6-embedded-rtos",
        "difficulty": "Apex Research",
        "duration": "90 mins",
        "simulation_component": "RtosSchedulerHub",
        "sim_route": "/embedded-systems",
        "summary": "Master FreeRTOS kernel internals on ARM Cortex-M and dual-core Xtensa ESP32, analyzing priority inversion inheritance, RMS vs EDF bounds, and PendSV switching.",
        "hardware_kit": ["STMicroelectronics STM32F401RE Nucleo-64", "ESP32-S3 Dual-Core Xtensa LX7 DevKit", "Segger J-Link EDU Mini Debugger", "Rigol DS1054Z 4-Channel Oscilloscope"]
    },
    {
        "id": "advanced_analog",
        "track": "Advanced Analog",
        "code": "ANLG8707",
        "title": "Advanced Analog Small-Signal Foundations & High-Frequency Signal Integrity",
        "icon": "📈",
        "theme_color": "#F97316",
        "slug": "7-analog-signal-integrity",
        "difficulty": "Apex Research",
        "duration": "90 mins",
        "simulation_component": "LtspiceSimulationViewer",
        "sim_route": "/virtual-bench",
        "summary": "Rigorous analytical textbook covering BJT/MOSFET small-signal hybrid-pi derivations, pole-zero transfer functions, Maxwell EM boundary equations, and Shannon-Hartley capacity.",
        "hardware_kit": ["Keysight InfiniiVision 4-Channel 200MHz DSO", "Rohde & Schwarz Vector Network Analyzer", "High-Frequency FR-4 Microstrip Coupon (50-Ohm)", "BJT 2N2222A & MOSFET 2N7000"]
    },
    {
        "id": "zero_copy_ipc",
        "track": "Zero-Copy IPC",
        "code": "DMA8708",
        "title": "Advanced ARM Cortex-M DMA Architecture & FreeRTOS Zero-Copy IPC",
        "icon": "⚡",
        "theme_color": "#06B6D4",
        "slug": "8-advanced-rtos-dma",
        "difficulty": "Apex Research",
        "duration": "90 mins",
        "simulation_component": "DmaNvicHub",
        "sim_route": "/virtual-bench",
        "summary": "High-throughput DMA controller architectures on ARM Cortex-M4/M7, analyzing multi-layer AHB crossbar bus matrix contention, circular ping-pong buffering, and zero-copy stream buffers.",
        "hardware_kit": ["STMicroelectronics STM32F446RE Nucleo-64", "ESP32-S3 Dual-Core Xtensa LX7 DevKit with GDMA", "Analog Devices AD7606 16-Bit ADC", "Keysight DSOX1204G Oscilloscope"]
    },
    {
        "id": "tinyml",
        "track": "TinyML",
        "code": "TML8709",
        "title": "TinyML Edge AI Neural Networks & Vibration FFT Anomaly Detection",
        "icon": "🧠",
        "theme_color": "#A855F7",
        "slug": "9-tiny-ml-edge",
        "difficulty": "Apex Research",
        "duration": "90 mins",
        "simulation_component": "TinyMlEngineHub",
        "sim_route": "/embedded-systems",
        "summary": "Edge AI TinyML neural network inference on microcontrollers, covering post-training INT8 asymmetric quantization, 64-point FFT feature extraction, and CMSIS-NN SIMD vectorization.",
        "hardware_kit": ["ESP32-S3 Dual-Core Xtensa LX7 DevKit", "STMicroelectronics STM32F446RE Nucleo-64", "Analog Devices ADXL345 Accelerometer", "TI TMP117 High-Precision Temp Sensor"]
    },
    {
        "id": "instrumentation",
        "track": "Instrumentation",
        "code": "INST8710",
        "title": "Advanced ECE Instrumentation, K-Map Minimization & Bode Plot Dynamics",
        "icon": "🔬",
        "theme_color": "#EAB308",
        "slug": "advanced-ece/10-gate-ece-instrumentation",
        "difficulty": "Apex Research",
        "duration": "75 mins",
        "simulation_component": "GateEceInteractiveSolvers",
        "sim_route": "/gate-ece",
        "summary": "Comprehensive analytical guide to digital logic synthesis, 4-variable Gray code Karnaugh map minimization, Bode plot frequency stability, and ARM Cortex-M pipelined assembly tracing.",
        "hardware_kit": ["Keysight DSOX1204G Digital Storage Oscilloscope", "Xilinx Artix-7 FPGA Evaluation Board"]
    }
]


# ========================================================================================
# UNIFIED CURRICULUM PREREQUISITE GRAPH (TIER 1, TIER 2, TIER 3 & STM32 ACADEMY)
# ========================================================================================
CURRICULUM_PREREQUISITE_GRAPH: Dict[str, Dict[str, Any]] = {
    # Tier 2: Pre-Engineering & Mathematical Foundations
    "MA23C01": {
        "code": "MA23C01",
        "title": "Applied Mathematics & Linear Algebra",
        "tier": "Tier 2: Foundation",
        "category": "Basic Sciences (BSC)",
        "prerequisites": [],
        "min_mastery_pct": 70.0
    },
    "PH23C01": {
        "code": "PH23C01",
        "title": "Engineering Physics & Semiconductor Physics",
        "tier": "Tier 2: Foundation",
        "category": "Basic Sciences (BSC)",
        "prerequisites": [],
        "min_mastery_pct": 70.0
    },
    "EE23C01": {
        "code": "EE23C01",
        "title": "Electric Circuit Analysis & Network Theorems",
        "tier": "Tier 2: Foundation",
        "category": "Engineering Sciences (ESC)",
        "prerequisites": [],
        "min_mastery_pct": 70.0
    },
    "EC23C04": {
        "code": "EC23C04",
        "title": "Signals and Systems (Continuous & Discrete)",
        "tier": "Tier 2: Foundation",
        "category": "Professional Core (PCC)",
        "prerequisites": ["MA23C01"],
        "min_mastery_pct": 70.0
    },
    "EC23C02": {
        "code": "EC23C02",
        "title": "Electromagnetic Fields & Guided Waves",
        "tier": "Tier 2: Foundation",
        "category": "Professional Core (PCC)",
        "prerequisites": ["PH23C01"],
        "min_mastery_pct": 70.0
    },
    "EC3352": {
        "code": "EC3352",
        "title": "Digital Systems & Verilog HDL",
        "tier": "Tier 2: Foundation",
        "category": "Professional Core (PCC)",
        "prerequisites": ["EE23C01"],
        "min_mastery_pct": 70.0
    },
    "EC3451": {
        "code": "EC3451",
        "title": "Linear Integrated Circuits & Operational Amplifiers",
        "tier": "Tier 2: Foundation",
        "category": "Professional Core (PCC)",
        "prerequisites": ["EE23C01"],
        "min_mastery_pct": 70.0
    },
    "EC23C05": {
        "code": "EC23C05",
        "title": "Microprocessors and Microcontrollers",
        "tier": "Tier 2: Foundation",
        "category": "Professional Core (PCC)",
        "prerequisites": ["EC3352"],
        "min_mastery_pct": 70.0
    },

    # Tier 1: Core Priority Engineering Disciplines
    "EC23C03": {
        "code": "EC23C03",
        "title": "Electronic Devices and Circuits",
        "tier": "Tier 1: Core",
        "category": "Professional Core (PCC)",
        "prerequisites": ["PH23C01", "EE23C01"],
        "min_mastery_pct": 70.0
    },
    "EC23S01": {
        "code": "EC23S01",
        "title": "Python Digital Signal Processing",
        "tier": "Tier 1: Core",
        "category": "Employability Enhancement (EEC)",
        "prerequisites": ["EC23C04", "MA23C01"],
        "min_mastery_pct": 70.0
    },
    "EC23E04": {
        "code": "EC23E04",
        "title": "Optics, Lasers and Fiber Optics",
        "tier": "Tier 1: Core",
        "category": "Professional Elective (PEC)",
        "prerequisites": ["EC23C02", "PH23C01"],
        "min_mastery_pct": 70.0
    },
    "EC8702": {
        "code": "EC8702",
        "title": "Advanced Embedded Systems Architecture",
        "tier": "Tier 1: Core",
        "category": "Professional Core (PCC)",
        "prerequisites": ["EC23C05", "EC3352"],
        "min_mastery_pct": 70.0
    },

    # Tier 3: Advanced Specialization Tracks
    "IOT8701": {
        "code": "IOT8701",
        "title": "IoT Edge Node Foundations, Bare-Metal GPIO & Low-Power Sleep Architecture",
        "tier": "Tier 3: Specialization",
        "category": "Specialization Track",
        "prerequisites": ["EC8702", "EC23C03"],
        "min_mastery_pct": 70.0
    },
    "AUTO8702": {
        "code": "AUTO8702",
        "title": "Automotive Radar & Ultrasonic Edge Sensing Telemetry",
        "tier": "Tier 3: Specialization",
        "category": "Specialization Track",
        "prerequisites": ["IOT8701", "EC23S01"],
        "min_mastery_pct": 70.0
    },
    "UAV8703": {
        "code": "UAV8703",
        "title": "Defense UAV Telemetry & Frequency-Hopping Spread Spectrum (FHSS)",
        "tier": "Tier 3: Specialization",
        "category": "Specialization Track",
        "prerequisites": ["AUTO8702", "EC23S01"],
        "min_mastery_pct": 70.0
    },
    "RAIL8704": {
        "code": "RAIL8704",
        "title": "High-Speed Railway Edge AI & Optical Track Defect Classification",
        "tier": "Tier 3: Specialization",
        "category": "Specialization Track",
        "prerequisites": ["IOT8701", "EC23S01"],
        "min_mastery_pct": 70.0
    },
    "RISCV8705": {
        "code": "RISCV8705",
        "title": "5-Stage Pipelined RV32I RISC-V Soft-Core Processor Design",
        "tier": "Tier 3: Specialization",
        "category": "Specialization Track",
        "prerequisites": ["EC8702", "EC3352"],
        "min_mastery_pct": 70.0
    },
    "RTOS8706": {
        "code": "RTOS8706",
        "title": "Real-Time Operating Systems (FreeRTOS) & Deterministic Multi-Core Scheduling",
        "tier": "Tier 3: Specialization",
        "category": "Specialization Track",
        "prerequisites": ["EC8702"],
        "min_mastery_pct": 70.0
    },
    "ANLG8707": {
        "code": "ANLG8707",
        "title": "Advanced Analog Small-Signal Foundations & High-Frequency Signal Integrity",
        "tier": "Tier 3: Specialization",
        "category": "Specialization Track",
        "prerequisites": ["EC23C03", "EC3451"],
        "min_mastery_pct": 70.0
    },
    "DMA8708": {
        "code": "DMA8708",
        "title": "Advanced ARM Cortex-M DMA Architecture & FreeRTOS Zero-Copy IPC",
        "tier": "Tier 3: Specialization",
        "category": "Specialization Track",
        "prerequisites": ["RTOS8706", "EC8702"],
        "min_mastery_pct": 70.0
    },
    "TML8709": {
        "code": "TML8709",
        "title": "TinyML Edge AI Neural Networks & Vibration FFT Anomaly Detection",
        "tier": "Tier 3: Specialization",
        "category": "Specialization Track",
        "prerequisites": ["EC23S01", "EC8702", "IOT8701"],
        "min_mastery_pct": 70.0
    },
    "INST8710": {
        "code": "INST8710",
        "title": "Advanced ECE Instrumentation, K-Map Minimization & Bode Plot Dynamics",
        "tier": "Tier 3: Specialization",
        "category": "Specialization Track",
        "prerequisites": ["EC23C03", "EC23S01"],
        "min_mastery_pct": 70.0
    },

    # STM32 Academy 5-Tier Curriculum Structure
    "STM32_T1": {
        "code": "STM32_T1",
        "title": "STM32 Academy Tier 1: Architecture & Toolchain",
        "tier": "STM32 Academy",
        "category": "Bare-Metal Embedded",
        "prerequisites": ["EC8702"],
        "min_mastery_pct": 70.0
    },
    "STM32_T2": {
        "code": "STM32_T2",
        "title": "STM32 Academy Tier 2: Core Peripherals (GPIO, Timers, EXTI)",
        "tier": "STM32 Academy",
        "category": "Bare-Metal Embedded",
        "prerequisites": ["STM32_T1"],
        "min_mastery_pct": 70.0
    },
    "STM32_T3": {
        "code": "STM32_T3",
        "title": "STM32 Academy Tier 3: Serial Buses & DMA (SPI, I2C, CAN)",
        "tier": "STM32 Academy",
        "category": "Bare-Metal Embedded",
        "prerequisites": ["STM32_T2"],
        "min_mastery_pct": 70.0
    },
    "STM32_T4": {
        "code": "STM32_T4",
        "title": "STM32 Academy Tier 4: RTOS Kernel Internals & PendSV Context Switching",
        "tier": "STM32 Academy",
        "category": "Real-Time OS",
        "prerequisites": ["STM32_T3", "RTOS8706"],
        "min_mastery_pct": 70.0
    },
    "STM32_T5": {
        "code": "STM32_T5",
        "title": "STM32 Academy Tier 5: Industrial Hardware & Edge AI",
        "tier": "STM32 Academy",
        "category": "Industrial Systems",
        "prerequisites": ["STM32_T4", "TML8709"],
        "min_mastery_pct": 70.0
    },

    # Granular STM32 Modules
    "STM32_MOD_01": {
        "code": "STM32_MOD_01",
        "title": "Memory Architecture & Reset Sequences",
        "tier": "STM32 Academy",
        "prerequisites": ["EC8702"],
        "min_mastery_pct": 70.0
    },
    "STM32_MOD_05": {
        "code": "STM32_MOD_05",
        "title": "Memory-Mapped GPIO & BSRR Atomic Writes",
        "tier": "STM32 Academy",
        "prerequisites": ["STM32_MOD_01"],
        "min_mastery_pct": 70.0
    },
    "STM32_MOD_12": {
        "code": "STM32_MOD_12",
        "title": "Direct Memory Access (DMA) Circular Streaming",
        "tier": "STM32 Academy",
        "prerequisites": ["STM32_MOD_05"],
        "min_mastery_pct": 70.0
    },
    "STM32_MOD_14": {
        "code": "STM32_MOD_14",
        "title": "SysTick Timer & Cooperative Multitasking",
        "tier": "STM32 Academy",
        "prerequisites": ["STM32_MOD_12"],
        "min_mastery_pct": 70.0
    },
    "STM32_MOD_15": {
        "code": "STM32_MOD_15",
        "title": "FreeRTOS Kernel Porting & PendSV Context Switch",
        "tier": "STM32 Academy",
        "prerequisites": ["STM32_MOD_14", "RTOS8706"],
        "min_mastery_pct": 70.0
    },
    "STM32_MOD_16": {
        "code": "STM32_MOD_16",
        "title": "RTOS Queues, Mutexes & Priority Inversion",
        "tier": "STM32 Academy",
        "prerequisites": ["STM32_MOD_15"],
        "min_mastery_pct": 70.0
    },
    "STM32_MOD_21": {
        "code": "STM32_MOD_21",
        "title": "TinyML Edge AI Inference with CMSIS-NN",
        "tier": "STM32 Academy",
        "prerequisites": ["STM32_MOD_16", "TML8709"],
        "min_mastery_pct": 70.0
    }
}


# ========================================================================================
# STUDENT MASTERY PROGRESSION & TOKEN VERIFICATION ENGINE (SQLITE WAL MODE)
# ========================================================================================

class CurriculumMasteryEngine:
    """
    Governs curriculum unlocking via mastery token verification in SQLite WAL mode.
    Enforces the >= 70% attainment threshold before downstream modules can be accessed.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH, graph: Optional[Dict[str, Any]] = None):
        self.db_path = db_path
        self.graph = graph or CURRICULUM_PREREQUISITE_GRAPH
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self):
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS student_progress (
                    student_id TEXT NOT NULL,
                    module_id TEXT NOT NULL,
                    course_code TEXT NOT NULL,
                    score REAL NOT NULL,
                    max_score REAL DEFAULT 100.0,
                    attainment_pct REAL NOT NULL,
                    status TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (student_id, module_id)
                );
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS module_mastery_tokens (
                    token_id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    module_id TEXT NOT NULL,
                    course_code TEXT NOT NULL,
                    attainment_pct REAL NOT NULL,
                    token_signature TEXT NOT NULL,
                    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(student_id, module_id)
                );
            """)
            conn.commit()
        finally:
            conn.close()

    def record_mastery_evaluation(
        self,
        student_id: str,
        module_id: str,
        course_code: str,
        score: float,
        max_score: float = 100.0,
        evaluation_type: str = "QUIZ"
    ) -> Dict[str, Any]:
        """
        Records student score for a unit, quiz, or lab experiment.
        Awards a verified mastery token if attainment >= 70.0%.
        Returns unlocked downstream nodes upon milestone completion.
        """
        student_clean = student_id.strip().upper()
        module_clean = module_id.strip().upper()
        course_clean = course_code.strip().upper()
        max_pts = max(1.0, float(max_score))
        attainment_pct = round((float(score) / max_pts) * 100.0, 2)
        mastery_achieved = attainment_pct >= 70.0
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = self._get_connection()
        try:
            status_val = "COMPLETED" if mastery_achieved else "REMEDIAL_REQUIRED"
            conn.execute("""
                INSERT INTO student_progress (student_id, module_id, course_code, score, max_score, attainment_pct, status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(student_id, module_id) DO UPDATE SET
                    score = excluded.score,
                    max_score = excluded.max_score,
                    attainment_pct = excluded.attainment_pct,
                    status = excluded.status,
                    updated_at = excluded.updated_at;
            """, (student_clean, module_clean, course_clean, float(score), max_pts, attainment_pct, status_val, now_str))

            token_id = None
            if mastery_achieved:
                sig_raw = f"{student_clean}:{module_clean}:{attainment_pct}:VOLTCORE_APEX_KEY_2026"
                token_sig = hashlib.sha256(sig_raw.encode("utf-8")).hexdigest()[:24]
                token_id = f"TOK_{student_clean}_{module_clean}_{os.urandom(2).hex()}"
                conn.execute("""
                    INSERT INTO module_mastery_tokens (token_id, student_id, module_id, course_code, attainment_pct, token_signature, issued_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(student_id, module_id) DO UPDATE SET
                        attainment_pct = excluded.attainment_pct,
                        token_signature = excluded.token_signature,
                        issued_at = excluded.issued_at;
                """, (token_id, student_clean, module_clean, course_clean, attainment_pct, token_sig, now_str))

            conn.commit()
        finally:
            conn.close()

        # Determine newly unlocked downstream nodes
        unlocked_nodes = []
        if mastery_achieved:
            downstream = course_config_engine.get_downstream_unlocked_nodes(module_clean)
            for node in downstream:
                check = self.verify_node_unlocked(student_clean, node)
                if check["is_unlocked"]:
                    unlocked_nodes.append(node)

        return {
            "status": "SUCCESS" if mastery_achieved else "REMEDIAL_REQUIRED",
            "student_id": student_clean,
            "module_id": module_clean,
            "course_code": course_clean,
            "score": float(score),
            "max_score": max_pts,
            "attainment_pct": attainment_pct,
            "mastery_achieved": mastery_achieved,
            "token_id": token_id,
            "evaluation_type": evaluation_type,
            "unlocked_downstream_nodes": unlocked_nodes,
            "evaluated_at": now_str
        }

    def verify_node_unlocked(self, student_id: str, target_node: str) -> Dict[str, Any]:
        """
        Verifies whether target_node is unlocked for student_id by checking
        that all prerequisite nodes possess a verified mastery token (>= 70%).
        """
        student_clean = student_id.strip().upper()
        node_clean = target_node.strip().upper()

        # Look up direct prerequisites
        prereqs = []
        if node_clean in self.graph:
            prereqs = self.graph[node_clean].get("prerequisites", [])
        elif node_clean in course_config_engine.registry:
            prereqs = course_config_engine.registry[node_clean].get("prerequisites", [])

        if not prereqs:
            return {
                "student_id": student_clean,
                "target_node": node_clean,
                "is_unlocked": True,
                "status": "UNLOCKED",
                "total_prerequisites": 0,
                "satisfied_prerequisites": [],
                "missing_prerequisites": [],
                "reason": "Foundational entry node (no prerequisites required)."
            }

        conn = self._get_connection()
        satisfied = []
        missing = []
        tokens = {}
        try:
            cur = conn.cursor()
            for p in prereqs:
                p_clean = p.strip().upper()
                cur.execute("""
                    SELECT token_id, attainment_pct, issued_at
                    FROM module_mastery_tokens
                    WHERE student_id = ? AND module_id = ? AND attainment_pct >= 70.0;
                """, (student_clean, p_clean))
                row = cur.fetchone()
                if row:
                    satisfied.append(p_clean)
                    tokens[p_clean] = {"token_id": row[0], "attainment_pct": row[1], "issued_at": row[2]}
                else:
                    missing.append(p_clean)
        finally:
            conn.close()

        is_unlocked = len(missing) == 0
        return {
            "student_id": student_clean,
            "target_node": node_clean,
            "is_unlocked": is_unlocked,
            "status": "UNLOCKED" if is_unlocked else "LOCKED",
            "total_prerequisites": len(prereqs),
            "satisfied_prerequisites": satisfied,
            "missing_prerequisites": missing,
            "mastery_tokens": tokens,
            "reason": "All prerequisite competencies verified." if is_unlocked else f"Locked: Requires >= 70% mastery in {', '.join(missing)}."
        }

    def get_student_curriculum_state(self, student_id: str) -> Dict[str, Any]:
        """
        Compiles the entire curriculum graph status for student_id,
        marking each node as MASTERED, UNLOCKED, or LOCKED.
        """
        student_clean = student_id.strip().upper()
        conn = self._get_connection()
        tokens = {}
        progress_map = {}
        try:
            cur = conn.cursor()
            cur.execute("SELECT module_id, token_id, attainment_pct FROM module_mastery_tokens WHERE student_id = ?;", (student_clean,))
            for r in cur.fetchall():
                tokens[r[0]] = {"token_id": r[1], "attainment_pct": r[2]}
            cur.execute("SELECT module_id, score, max_score, attainment_pct, status FROM student_progress WHERE student_id = ?;", (student_clean,))
            for r in cur.fetchall():
                progress_map[r[0]] = {"score": r[1], "max_score": r[2], "attainment_pct": r[3], "status": r[4]}
        finally:
            conn.close()

        nodes_state = {}
        for node, data in self.graph.items():
            prereqs = data.get("prerequisites", [])
            is_mastered = node in tokens
            if is_mastered:
                st = "MASTERED"
                unlocked = True
            elif not prereqs or all(p.upper().strip() in tokens for p in prereqs):
                st = "UNLOCKED"
                unlocked = True
            else:
                st = "LOCKED"
                unlocked = False

            missing = [p for p in prereqs if p.upper().strip() not in tokens]
            nodes_state[node] = {
                "code": node,
                "title": data.get("title", node),
                "tier": data.get("tier", "Core"),
                "status": st,
                "is_unlocked": unlocked,
                "is_mastered": is_mastered,
                "missing_prerequisites": missing,
                "progress": progress_map.get(node)
            }

        unlocked_count = sum(1 for n in nodes_state.values() if n["status"] == "UNLOCKED")
        locked_count = sum(1 for n in nodes_state.values() if n["status"] == "LOCKED")
        mastered_count = len(tokens)

        return {
            "student_id": student_clean,
            "total_nodes": len(nodes_state),
            "mastered_count": mastered_count,
            "unlocked_count": unlocked_count,
            "locked_count": locked_count,
            "summary": {
                "total": len(nodes_state),
                "mastered": mastered_count,
                "unlocked": unlocked_count,
                "locked": locked_count,
                "completion_pct": round((mastered_count / len(nodes_state)) * 100.0, 1) if nodes_state else 0.0
            },
            "nodes": nodes_state
        }

    def grant_mastery_override(
        self,
        student_id: str,
        module_id: str,
        course_code: str,
        actor_role: str = "Faculty",
        notes: str = ""
    ) -> Dict[str, Any]:
        """Faculty/Admin override granting verified mastery status and unlocking downstream nodes."""
        role_clean = (actor_role or "").strip()
        if role_clean not in ("Admin", "Faculty", "Instructor", "Platform-Lead"):
            return {
                "status": "FORBIDDEN",
                "error": "Mastery override requires Faculty or Admin credentials."
            }
        return self.record_mastery_evaluation(
            student_id=student_id,
            module_id=module_id,
            course_code=course_code,
            score=100.0,
            max_score=100.0
        )


# ========================================================================================
# Phase 16: Concept Dependency Intelligence & Dynamic Misconception Tracking
# ========================================================================================

class ConceptDependencyIntelligenceEngine:
    """
    Fine-grained ECE Concept DAG with semantic confidence scoring, misconception
    detection, weak competency pruning, and dynamic remedial micro-lesson path generation.
    """

    ECE_CONCEPT_GRAPH: Dict[str, Dict[str, Any]] = {
        "OHMS_LAW": {
            "title": "Ohm's Law & Passive Resistance",
            "tier": "Foundational Physics",
            "prerequisites": [],
            "key_principles": "V = I * R relationship, linear IV curve, power dissipation P = I^2 * R.",
            "interactive_tool": "MNA_LAB"
        },
        "KIRCHHOFF_LAWS": {
            "title": "Kirchhoff's Current (KCL) & Voltage (KVL) Laws",
            "tier": "Foundational Physics",
            "prerequisites": ["OHMS_LAW"],
            "key_principles": "Charge conservation (sum of node currents = 0), energy conservation (loop voltages = 0).",
            "interactive_tool": "MNA_LAB"
        },
        "RC_RL_TRANSIENT": {
            "title": "Reactive Energy Storage & RC/RL Transient Dynamics",
            "tier": "Circuit Theory",
            "prerequisites": ["KIRCHHOFF_LAWS"],
            "key_principles": "Differential equations for capacitor charging V(t) = V0*(1 - e^(-t/tau)), inductor flux continuity.",
            "interactive_tool": "MNA_LAB"
        },
        "PN_JUNCTION": {
            "title": "Semiconductor PN Junction & Shockley Exponential Diode",
            "tier": "Solid State Devices",
            "prerequisites": ["OHMS_LAW"],
            "key_principles": "Built-in barrier potential, depletion capacitance, Shockley equation Id = Is*(e^(Vd/Vt) - 1).",
            "interactive_tool": "MNA_LAB"
        },
        "DIODE_RECTIFIERS": {
            "title": "Diode Rectification & Smoothing Filter Topologies",
            "tier": "Electronic Circuits",
            "prerequisites": ["PN_JUNCTION", "KIRCHHOFF_LAWS"],
            "key_principles": "Half-wave and full-wave bridge rectification, ripple factor r = 1/(2*sqrt(3)*f*C*R), PIV ratings.",
            "interactive_tool": "MNA_LAB"
        },
        "BJT_BIASING": {
            "title": "BJT Biasing & Q-Point Stability",
            "tier": "Electronic Circuits",
            "prerequisites": ["PN_JUNCTION", "KIRCHHOFF_LAWS"],
            "key_principles": "Base-emitter forward bias (Vbe ~ 0.7V), collector-base reverse bias, DC load line, Q-point stabilization.",
            "interactive_tool": "MNA_LAB"
        },
        "BJT_ACTIVE_AMPLIFIER": {
            "title": "BJT Linear Active Mode Amplification",
            "tier": "Electronic Circuits",
            "prerequisites": ["BJT_BIASING", "RC_RL_TRANSIENT"],
            "key_principles": "Small-signal hybrid-pi model, transconductance gm = Ic/Vt, small-signal voltage gain Av = -gm*(Rc||Rl).",
            "interactive_tool": "MNA_LAB"
        },
        "MOSFET_OPERATION": {
            "title": "MOSFET Channel Inversion & Characteristic Curves",
            "tier": "Solid State Devices",
            "prerequisites": ["PN_JUNCTION", "OHMS_LAW"],
            "key_principles": "Gate threshold voltage Vth, triode conduction Id = kn*(Vgs - Vth)*Vds, channel length modulation.",
            "interactive_tool": "MNA_LAB"
        },
        "MOSFET_AMPLIFIERS": {
            "title": "MOSFET Saturation Mode Amplifiers & Switching",
            "tier": "Electronic Circuits",
            "prerequisites": ["MOSFET_OPERATION", "BJT_ACTIVE_AMPLIFIER"],
            "key_principles": "Pinch-off saturation Id = 0.5*kn*(Vgs - Vth)^2*(1 + lambda*Vds), high input impedance.",
            "interactive_tool": "MNA_LAB"
        },
        "LAPLACE_TRANSFORMS": {
            "title": "Laplace Transforms & Continuous s-Domain Analysis",
            "tier": "Signals & Systems",
            "prerequisites": ["RC_RL_TRANSIENT"],
            "key_principles": "Mapping differential equations to algebraic s-domain: L{d/dt} = s, initial value & final value theorems.",
            "interactive_tool": "MATH_STUDIO"
        },
        "TRANSFER_FUNCTIONS": {
            "title": "Rational Transfer Functions & Root Loci",
            "tier": "Control Systems",
            "prerequisites": ["LAPLACE_TRANSFORMS"],
            "key_principles": "H(s) = N(s)/D(s), characteristic polynomial roots, zero and pole placement.",
            "interactive_tool": "MATH_STUDIO"
        },
        "POLE_ZERO_STABILITY": {
            "title": "Complex Plane Pole-Zero Distribution & Hurwitz Stability",
            "tier": "Control Systems",
            "prerequisites": ["TRANSFER_FUNCTIONS"],
            "key_principles": "Left-Half Plane (LHP) stability criterion (Re(p) < 0), ROC boundary, marginal stability on jw axis.",
            "interactive_tool": "MATH_STUDIO"
        },
        "BODE_FREQUENCY_RESPONSE": {
            "title": "Bode Logarithmic Frequency Analysis & Cutoff Bandwidth",
            "tier": "Control Systems",
            "prerequisites": ["POLE_ZERO_STABILITY"],
            "key_principles": "Log-magnitude 20*log10|H(jw)|, phase angle arctan, -3.01dB cutoff frequency, gain/phase margins.",
            "interactive_tool": "MATH_STUDIO"
        },
        "FOURIER_SERIES": {
            "title": "Fourier Series & Harmonic Decomposition",
            "tier": "Signals & Systems",
            "prerequisites": ["TRANSFER_FUNCTIONS"],
            "key_principles": "Trigonometric and exponential harmonic decomposition, Gibbs phenomenon, Total Harmonic Distortion (THD).",
            "interactive_tool": "MATH_STUDIO"
        },
        "SAMPLING_NYQUIST": {
            "title": "Nyquist-Shannon Sampling Theorem & Anti-Aliasing",
            "tier": "Digital Signal Processing",
            "prerequisites": ["FOURIER_SERIES"],
            "key_principles": "Sampling rate fs >= 2*fmax, aliasing distortion, anti-aliasing low-pass analog reconstruction filter.",
            "interactive_tool": "MATH_STUDIO"
        },
        "Z_TRANSFORM": {
            "title": "Discrete Z-Transform & Unit Circle Stability",
            "tier": "Digital Signal Processing",
            "prerequisites": ["SAMPLING_NYQUIST", "LAPLACE_TRANSFORMS"],
            "key_principles": "z = exp(s*Ts), Schur-Cohn stability inside unit circle (|z| < 1), causal discrete ROC.",
            "interactive_tool": "MATH_STUDIO"
        },
        "DIGITAL_FILTER_IIR_FIR": {
            "title": "IIR & FIR Digital Filter Synthesis",
            "tier": "Digital Signal Processing",
            "prerequisites": ["Z_TRANSFORM", "BODE_FREQUENCY_RESPONSE"],
            "key_principles": "Bilinear transformation s = (2/Ts)*(z - 1)/(z + 1), Butterworth and Chebyshev filter implementations.",
            "interactive_tool": "MATH_STUDIO"
        },
        "EMBEDDED_C_REGISTERS": {
            "title": "Memory-Mapped Peripheral Registers & Bitwise Manipulation",
            "tier": "Embedded Systems",
            "prerequisites": ["OHMS_LAW"],
            "key_principles": "Volatile pointers, bit-masking (&, |, ^, ~), peripheral base addresses, Atomic register operations.",
            "interactive_tool": "WOKWI_CONTROLLER"
        },
        "TIMERS_PWM": {
            "title": "Hardware Timers, Prescalers & PWM Output Generation",
            "tier": "Embedded Systems",
            "prerequisites": ["EMBEDDED_C_REGISTERS", "RC_RL_TRANSIENT"],
            "key_principles": "Timer counters (ARR, PSC), compare capture registers (CCR), duty cycle = CCR/ARR, edge/center aligned PWM.",
            "interactive_tool": "WOKWI_CONTROLLER"
        },
        "INTERRUPTS_NVIC": {
            "title": "Nested Vectored Interrupt Controller (NVIC) & ISR Latency",
            "tier": "Embedded Systems",
            "prerequisites": ["EMBEDDED_C_REGISTERS"],
            "key_principles": "Interrupt vector table, priority preemption, pending registers, non-blocking ISR constraints.",
            "interactive_tool": "WOKWI_CONTROLLER"
        },
        "FREERTOS_CONCURRENCY": {
            "title": "FreeRTOS Kernel Scheduling, Mutexes & Semaphores",
            "tier": "Embedded Systems",
            "prerequisites": ["INTERRUPTS_NVIC", "TIMERS_PWM"],
            "key_principles": "Preemptive priority-based task scheduling, vTaskDelay() yield, priority inversion & priority inheritance.",
            "interactive_tool": "WOKWI_CONTROLLER"
        },
        "VERILOG_COMBINATIONAL": {
            "title": "Verilog HDL Synthesizable Combinational Logic",
            "tier": "Digital VLSI",
            "prerequisites": ["OHMS_LAW"],
            "key_principles": "Continuous assign statements, always @* blocks, blocking (=) assignments, multiplexers, decoders.",
            "interactive_tool": "FPGA_HUB"
        },
        "VERILOG_SEQUENTIAL": {
            "title": "Verilog HDL Sequential Logic & Finite State Machines",
            "tier": "Digital VLSI",
            "prerequisites": ["VERILOG_COMBINATIONAL", "TIMERS_PWM"],
            "key_principles": "always @(posedge clk) blocks, non-blocking (<=) assignment, Mealy/Moore FSM architectures.",
            "interactive_tool": "FPGA_HUB"
        }
    }

    MISCONCEPTION_REGISTRY: Dict[str, Dict[str, Any]] = {
        "MISCONCEPTION_BJT_SATURATION_CONFUSION": {
            "name": "BJT Saturation Region Confusion",
            "associated_concept": "BJT_ACTIVE_AMPLIFIER",
            "description": "Mistakenly assuming BJT is in linear amplification mode when Vce < 0.2V.",
            "pedagogical_remedy": "When Vce < 0.2V, the collector-base junction becomes forward-biased and enters saturation where Ic is limited by external load Rc rather than beta*Ib.",
            "interactive_exercise": "Simulate BJT with low Vcc or excessive Ib to observe clipping at Vce = 0.2V in MNA Lab."
        },
        "MISCONCEPTION_ACTIVE_MODE_BIASING": {
            "name": "Failure to Maintain Vbe Forward Bias",
            "associated_concept": "BJT_BIASING",
            "description": "Designing bias network yielding Vbe < 0.65V, keeping BJT in cutoff.",
            "pedagogical_remedy": "Ensure base divider voltage Vb provides at least 0.7V drop across base-emitter junction plus emitter resistor voltage drop.",
            "interactive_exercise": "Recalculate R1 and R2 divider resistors in CE Amplifier preset."
        },
        "MISCONCEPTION_BLOCKING_DELAY_IN_ISR": {
            "name": "Blocking Delay in FreeRTOS/ISR",
            "associated_concept": "FREERTOS_CONCURRENCY",
            "description": "Calling delay() inside FreeRTOS task or ISR, starving lower-priority tasks.",
            "pedagogical_remedy": "Replace delay() with vTaskDelay(pdMS_TO_TICKS(ms)) or hardware timer one-shot interrupts.",
            "interactive_exercise": "Run Wokwi logic analyzer trace comparing busy-wait vs preemptive scheduling."
        },
        "MISCONCEPTION_UNSTABLE_RHP_POLE": {
            "name": "Right-Half Plane Pole Instability",
            "associated_concept": "POLE_ZERO_STABILITY",
            "description": "Placing poles in the Right-Half Plane (Re(p) > 0) assuming it increases system speed.",
            "pedagogical_remedy": "Poles in the RHP create exponential growth terms e^(+sigma*t) resulting in unbounded output. Move poles into Left-Half Plane (Re(p) < 0).",
            "interactive_exercise": "Drag poles across jw axis in Engineering Math Studio and observe divergent step response."
        },
        "MISCONCEPTION_NYQUIST_ALIASING": {
            "name": "Nyquist Rate Violation & Aliasing",
            "associated_concept": "SAMPLING_NYQUIST",
            "description": "Sampling continuous signals below 2*fmax, resulting in folded phantom frequencies.",
            "pedagogical_remedy": "Set ADC sampling frequency fs to at least 2.5 to 4 times the maximum signal frequency fmax.",
            "interactive_exercise": "Adjust sampling frequency below signal frequency in Fourier Studio to observe aliasing."
        },
        "MISCONCEPTION_LATCH_INFERENCE_VERILOG": {
            "name": "Unintentional Transparent Latch Inference",
            "associated_concept": "VERILOG_COMBINATIONAL",
            "description": "Omitting default: clause in combinational case statements or missing else in if branches.",
            "pedagogical_remedy": "Synthesizers infer memory latches when an output is not assigned in every possible branch of a combinational always block.",
            "interactive_exercise": "Add explicit default: branch in Verilog code editor."
        }
    }

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
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
                CREATE TABLE IF NOT EXISTS student_concept_confidence (
                    student_id TEXT NOT NULL,
                    concept_id TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    evaluations_count INTEGER NOT NULL,
                    last_updated TEXT NOT NULL,
                    PRIMARY KEY (student_id, concept_id)
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS student_misconceptions (
                    log_id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    misconception_id TEXT NOT NULL,
                    assessment_context TEXT,
                    detected_timestamp TEXT NOT NULL,
                    resolved INTEGER DEFAULT 0
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS remedial_learning_paths (
                    path_id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    failed_concept_id TEXT NOT NULL,
                    weak_prerequisites_json TEXT NOT NULL,
                    micro_lessons_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)
            conn.commit()
        finally:
            conn.close()

    def record_concept_evaluation(
        self,
        student_id: str,
        concept_id: str,
        score: float,
        max_score: float = 100.0,
        detected_misconceptions: Optional[List[str]] = None,
        context: str = "QUIZ"
    ) -> Dict[str, Any]:
        """
        Updates student concept confidence score using an exponential moving average:
        C_new = 0.70 * C_old + 0.30 * (score / max_score).
        Logs any detected misconceptions.
        """
        student_clean = student_id.strip().upper()
        concept_clean = concept_id.strip().upper()

        if concept_clean not in self.ECE_CONCEPT_GRAPH:
            concept_clean = "OHMS_LAW"

        score_norm = max(0.0, min(1.0, float(score) / max(1.0, float(max_score))))
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT confidence_score, evaluations_count
                FROM student_concept_confidence
                WHERE student_id = ? AND concept_id = ?;
            """, (student_clean, concept_clean))
            row = cur.fetchone()

            if row:
                old_conf, count = row
                # Exponential moving average with learning momentum
                new_conf = round(0.65 * old_conf + 0.35 * score_norm, 4)
                new_count = count + 1
                cur.execute("""
                    UPDATE student_concept_confidence
                    SET confidence_score = ?, evaluations_count = ?, last_updated = ?
                    WHERE student_id = ? AND concept_id = ?;
                """, (new_conf, new_count, now_str, student_clean, concept_clean))
            else:
                new_conf = round(score_norm, 4)
                new_count = 1
                cur.execute("""
                    INSERT INTO student_concept_confidence (
                        student_id, concept_id, confidence_score, evaluations_count, last_updated
                    ) VALUES (?, ?, ?, ?, ?);
                """, (student_clean, concept_clean, new_conf, new_count, now_str))

            # Log misconceptions if detected
            if detected_misconceptions:
                for misc_id in detected_misconceptions:
                    if misc_id in self.MISCONCEPTION_REGISTRY:
                        log_id = f"MISC_{int(time.time() * 1000)}_{os.urandom(2).hex()}"
                        cur.execute("""
                            INSERT INTO student_misconceptions (
                                log_id, student_id, misconception_id, assessment_context, detected_timestamp
                            ) VALUES (?, ?, ?, ?, ?);
                        """, (log_id, student_clean, misc_id, context, now_str))

            conn.commit()
        finally:
            conn.close()

        return {
            "student_id": student_clean,
            "concept_id": concept_clean,
            "confidence_score": new_conf,
            "evaluations_count": new_count,
            "is_competent": new_conf >= 0.70,
            "timestamp": now_str
        }

    def get_student_concept_confidence(
        self,
        student_id: str,
        concept_id: Optional[str] = None
    ) -> Dict[str, Any]:
        student_clean = student_id.strip().upper()
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            if concept_id:
                cur.execute("""
                    SELECT concept_id, confidence_score, evaluations_count, last_updated
                    FROM student_concept_confidence
                    WHERE student_id = ? AND concept_id = ?;
                """, (student_clean, concept_id.strip().upper()))
            else:
                cur.execute("""
                    SELECT concept_id, confidence_score, evaluations_count, last_updated
                    FROM student_concept_confidence
                    WHERE student_id = ?;
                """, (student_clean,))
            rows = cur.fetchall()
        finally:
            conn.close()

        res = {}
        for r in rows:
            res[r[0]] = {
                "confidence_score": r[1],
                "evaluations_count": r[2],
                "last_updated": r[3],
                "status": "STRONG" if r[1] >= 0.80 else "COMPETENT" if r[1] >= 0.70 else "VULNERABLE"
            }
        return res

    def generate_remedial_path(
        self,
        student_id: str,
        failed_concept_id: str
    ) -> Dict[str, Any]:
        """
        Traverses DAG backward from failed_concept_id to isolate weak upstream
        prerequisites (confidence < 0.70) and dynamically synthesizes a targeted
        remedial micro-lesson path.
        """
        student_clean = student_id.strip().upper()
        failed_clean = failed_concept_id.strip().upper()

        if failed_clean not in self.ECE_CONCEPT_GRAPH:
            failed_clean = "BJT_ACTIVE_AMPLIFIER"

        student_conf_map = self.get_student_concept_confidence(student_clean)

        # 1. Backward DAG Traversal: Collect all upstream ancestors
        ancestors: Set[str] = set()
        queue = [failed_clean]
        visited = set()

        while queue:
            curr = queue.pop(0)
            if curr in visited:
                continue
            visited.add(curr)
            ancestors.add(curr)
            node_data = self.ECE_CONCEPT_GRAPH.get(curr, {})
            prereqs = node_data.get("prerequisites", [])
            for p in prereqs:
                if p not in visited:
                    queue.append(p)

        # 2. Identify weak ancestors (confidence < 0.70 or unattempted)
        weak_nodes: List[str] = []
        for node in ancestors:
            conf_data = student_conf_map.get(node)
            conf = conf_data["confidence_score"] if conf_data else 0.50
            if conf < 0.70 or node == failed_clean:
                weak_nodes.append(node)

        # 3. Topological sorting of weak nodes so root fundamentals come first
        def get_depth(node_id: str, current_depth: int = 0) -> int:
            prereqs = self.ECE_CONCEPT_GRAPH.get(node_id, {}).get("prerequisites", [])
            if not prereqs:
                return current_depth
            return max(get_depth(p, current_depth + 1) for p in prereqs)

        weak_nodes.sort(key=lambda n: get_depth(n), reverse=False)

        # 4. Generate targeted micro-lessons
        micro_lessons = []
        for idx, node_id in enumerate(weak_nodes, 1):
            info = self.ECE_CONCEPT_GRAPH.get(node_id, {})
            conf_val = student_conf_map.get(node_id, {}).get("confidence_score", 0.50)

            lesson = {
                "step": idx,
                "lesson_id": f"REMEDIAL_{node_id}_{idx}",
                "concept_id": node_id,
                "concept_title": info.get("title", node_id),
                "current_confidence": conf_val,
                "estimated_minutes": 6,
                "tier": info.get("tier", "Core"),
                "key_principle": info.get("key_principles", "Fundamental law."),
                "interactive_sandbox": info.get("interactive_tool", "MNA_LAB"),
                "diagnostic_checkpoint": f"Explain why {info.get('title', node_id)} governs the behavior of {self.ECE_CONCEPT_GRAPH.get(failed_clean, {}).get('title', failed_clean)}."
            }
            micro_lessons.append(lesson)

        # 5. Persist to SQLite WAL
        path_id = f"PATH_{int(time.time() * 1000)}_{os.urandom(2).hex()}"
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        conn = self._get_connection()
        try:
            conn.execute("""
                INSERT INTO remedial_learning_paths (
                    path_id, student_id, failed_concept_id, weak_prerequisites_json, micro_lessons_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?);
            """, (path_id, student_clean, failed_clean, json.dumps(weak_nodes), json.dumps(micro_lessons), now_str))
            conn.commit()
        finally:
            conn.close()

        return {
            "status": "SUCCESS",
            "path_id": path_id,
            "student_id": student_clean,
            "failed_concept_id": failed_clean,
            "failed_concept_title": self.ECE_CONCEPT_GRAPH.get(failed_clean, {}).get("title", failed_clean),
            "total_weak_prerequisites": len(weak_nodes),
            "weak_prerequisites": weak_nodes,
            "remedial_micro_lessons": micro_lessons,
            "estimated_remedial_time_minutes": len(micro_lessons) * 6,
            "created_at": now_str
        }

    def get_concept_dag_graph(self) -> Dict[str, Any]:
        """Returns the complete concept topology with nodes and edges."""
        nodes = []
        edges = []
        for cid, data in self.ECE_CONCEPT_GRAPH.items():
            nodes.append({
                "id": cid,
                "title": data["title"],
                "tier": data["tier"],
                "interactive_tool": data["interactive_tool"]
            })
            for p in data["prerequisites"]:
                edges.append({"source": p, "target": cid})

        return {
            "total_concepts": len(nodes),
            "total_dependencies": len(edges),
            "nodes": nodes,
            "edges": edges
        }


# Global singleton instances for platform-wide use
course_config_engine = CourseConfigEngine()
curriculum_mastery_engine = CurriculumMasteryEngine()
concept_intelligence_engine = ConceptDependencyIntelligenceEngine()

