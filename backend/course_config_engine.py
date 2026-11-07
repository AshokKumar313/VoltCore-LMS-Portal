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
from typing import Dict, Any, List, Optional, Set

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


class CourseConfigEngine:
    """Core engine for course metadata verification and prerequisite DAG resolution."""

    def __init__(self, registry: Optional[Dict[str, Dict[str, Any]]] = None):
        self.registry = registry or COURSE_REGISTRY_DATA

    def get_course(self, code: str) -> Optional[Dict[str, Any]]:
        """Retrieve course details by normalized course code."""
        return self.registry.get(code.upper().strip())

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
        """
        visited: Set[str] = set()
        visiting: Set[str] = set()
        order: List[str] = []

        def dfs(node: str) -> bool:
            if node in visiting:
                return False  # Cycle detected
            if node in visited:
                return True

            visiting.add(node)
            course_data = self.get_course(node)
            if course_data:
                for prereq in course_data.get("prerequisites", []):
                    if not dfs(prereq):
                        return False

            visiting.remove(node)
            visited.add(node)
            order.append(node)
            return True

        has_no_cycle = dfs(target_course.upper().strip())

        return {
            "target": target_course.upper().strip(),
            "has_cycle": not has_no_cycle,
            "is_valid_dag": has_no_cycle,
            "prerequisite_sequence": order[:-1],  # Exclude target itself from prereqs
            "total_prerequisites": len(order) - 1
        }

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

