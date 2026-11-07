"""
========================================================================================
VoltCore Apex Academia - ECE Professional Subject Emblem & Institutional Registry (Backend)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/subject_emblem_registry.py
Platform Lead & Educational Systems Director: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Provides:
  1. Complete 14 Core ECE Disciplines with Clean, Professional Engineering Nomenclature
  2. Industry-Aligned Professional Titles, Disciplines, and Subfield Categorization
  3. Verified SVG Circuit Geometries (Nodal Bridge, Bandgap, Op-Amp, Smith Chart, etc.)
  4. Official VoltCore Sovereign Brand Identity & Institutional Motto
  5. Theme-Adaptive Color Tokens and Accessible Descriptions
  6. Robust Fallback and Discipline Name Lookup Services
========================================================================================
"""

from typing import Dict, Any, List, Optional


INSTITUTIONAL_BRANDING: Dict[str, Any] = {
    "platform_name": "VoltCore Apex Academia",
    "lead_architect": "Ashok Kumar A (2023MITEC042)",
    "institution": "Madras Institute of Technology (MIT) Campus, Anna University",
    "department": "Department of Electronics Engineering",
    "regulation": "Regulation 2023",
    "favicon_svg_path": "public/favicon.svg",
    "motto": "Engineering Intelligence. Practical Innovation. Academic Excellence.",
    "brand_colors": {
        "emerald_primary": "#00F0B5",
        "emerald_dark": "#00693E",
        "cyan_accent": "#00D8F6",
        "silicon_dark": "#020813",
        "surface_dark": "rgba(4, 16, 38, 0.78)"
    },
    "supported_themes_count": 18
}


ECE_SUBJECT_EMBLEMS: Dict[str, Dict[str, Any]] = {
    "EC23C01": {
        "code": "EC23C01",
        "discipline_name": "Circuit Analysis & Network Synthesis",
        "professional_title": "Linear Circuit Theory & Network Synthesis",
        "industry_domain": "Analog EDA & Circuit Infrastructure",
        "subfield": "Circuits & Systems",
        "name": "Circuit Analysis & Network Synthesis",
        "short_title": "Circuits & Networks",
        "symbol_name": "MNA Nodal Bridge",
        "primary_color": "#00F0B5",
        "accent_color": "#10B981",
        "gradient": ["#00F0B5", "#047857"],
        "category": "FOUNDATION",
        "accessible_label": "Resistor-Inductor-Capacitor Lattice Network Emblem",
        "technical_keywords": ["KCL", "KVL", "Thevenin", "Norton", "MNA Solver", "Laplace Transients"],
        "svg_viewbox": "0 0 48 48",
        "svg_elements_count": 8
    },
    "EC23C02": {
        "code": "EC23C02",
        "discipline_name": "Semiconductor Device Physics",
        "professional_title": "Solid-State Physics & Semiconductor Devices",
        "industry_domain": "Semiconductor Foundry & Microelectronics",
        "subfield": "Solid-State Physics",
        "name": "Semiconductor Physics & Devices",
        "short_title": "Semiconductor Physics",
        "symbol_name": "Fermi Bandgap Lattice",
        "primary_color": "#38BDF8",
        "accent_color": "#0284C7",
        "gradient": ["#38BDF8", "#0369A1"],
        "category": "FOUNDATION",
        "accessible_label": "Energy Bandgap with Conduction and Valence Bands Emblem",
        "technical_keywords": ["Bandgap Eg", "Fermi-Dirac", "Intrinsic Carriers ni", "Carrier Drift-Diffusion"],
        "svg_viewbox": "0 0 48 48",
        "svg_elements_count": 9
    },
    "EC23C03": {
        "code": "EC23C03",
        "discipline_name": "Electronic Devices & Circuit Modeling",
        "professional_title": "Discrete Semiconductor Devices & Active Circuits",
        "industry_domain": "Hardware Electronics & Power Systems",
        "subfield": "Electronic Devices",
        "name": "Electronic Devices & Solid-State Circuits",
        "short_title": "Electronic Devices",
        "symbol_name": "Shockley PN Junction",
        "primary_color": "#F59E0B",
        "accent_color": "#D97706",
        "gradient": ["#F59E0B", "#B45309"],
        "category": "CORE_ANALOG",
        "accessible_label": "Semiconductor Diode and MOSFET Channel Junction Emblem",
        "technical_keywords": ["Shockley Diode", "BJT Hybrid-Pi", "MOSFET Subthreshold", "Depletion Width"],
        "svg_viewbox": "0 0 48 48",
        "svg_elements_count": 5
    },
    "EC23C05": {
        "code": "EC23C05",
        "discipline_name": "Analog Integrated Circuit Design",
        "professional_title": "Precision Analog ICs & Operational Amplifiers",
        "industry_domain": "Mixed-Signal ICs & Sensor Frontends",
        "subfield": "Analog ICs",
        "name": "Analog Integrated Electronics",
        "short_title": "Analog Electronics",
        "symbol_name": "Differential Op-Amp Core",
        "primary_color": "#EC4899",
        "accent_color": "#BE185D",
        "gradient": ["#EC4899", "#9D174D"],
        "category": "CORE_ANALOG",
        "accessible_label": "High-Precision Operational Amplifier Symbol Emblem",
        "technical_keywords": ["Op-Amp", "CMRR", "Gain-Bandwidth", "Active Filters", "Slew Rate"],
        "svg_viewbox": "0 0 48 48",
        "svg_elements_count": 7
    },
    "EC23C06": {
        "code": "EC23C06",
        "discipline_name": "Digital Logic Design & Finite Automata",
        "professional_title": "Combinational & Sequential Logic Architecture",
        "industry_domain": "Digital Systems & ASIC Microarchitecture",
        "subfield": "Digital Logic",
        "name": "Digital Electronics & Logic Design",
        "short_title": "Digital Electronics",
        "symbol_name": "K-Map Logic Gate Matrix",
        "primary_color": "#8B5CF6",
        "accent_color": "#6D28D9",
        "gradient": ["#8B5CF6", "#5B21B6"],
        "category": "CORE_DIGITAL",
        "accessible_label": "NAND Logic Gate with Binary Grid Emblem",
        "technical_keywords": ["K-Map", "Quine-McCluskey", "Synchronous FSM", "Setup/Hold Slack"],
        "svg_viewbox": "0 0 48 48",
        "svg_elements_count": 6
    },
    "EC23C04": {
        "code": "EC23C04",
        "discipline_name": "Signals & Linear Systems Theory",
        "professional_title": "Continuous & Discrete-Time Linear Systems",
        "industry_domain": "Signal Processing & Communication Infrastructure",
        "subfield": "Systems & Signals",
        "name": "Signals and Linear Systems",
        "short_title": "Signals & Systems",
        "symbol_name": "Continuous Fourier S-Plane",
        "primary_color": "#06B6D4",
        "accent_color": "#0891B2",
        "gradient": ["#06B6D4", "#0E7490"],
        "category": "SYSTEMS_SIGNALS",
        "accessible_label": "Sine Wave Harmonic Frequency Domain S-Plane Emblem",
        "technical_keywords": ["LTI Convolution", "Fourier Series", "Laplace ROC", "Z-Transform"],
        "svg_viewbox": "0 0 48 48",
        "svg_elements_count": 6
    },
    "EC23C07": {
        "code": "EC23C07",
        "discipline_name": "Control Systems Engineering",
        "professional_title": "Feedback Dynamics, Stability & Modern Control",
        "industry_domain": "Robotics, Aerospace & Industrial Automation",
        "subfield": "Control Systems",
        "name": "Control Systems Engineering",
        "short_title": "Control Systems",
        "symbol_name": "Closed-Loop Root Locus Plant",
        "primary_color": "#10B981",
        "accent_color": "#059669",
        "gradient": ["#10B981", "#047857"],
        "category": "SYSTEMS_SIGNALS",
        "accessible_label": "Closed-Loop Feedback Block Diagram with Summing Junction Emblem",
        "technical_keywords": ["Root Locus", "Bode Plot", "Nyquist Stability", "State-Space"],
        "svg_viewbox": "0 0 48 48",
        "svg_elements_count": 8
    },
    "EC23S01": {
        "code": "EC23S01",
        "discipline_name": "Digital Signal Processing & Algorithms",
        "professional_title": "Discrete-Time Transforms & Multirate Filterbanks",
        "industry_domain": "Audio/Image DSP, Radar & Biomedical Signals",
        "subfield": "Digital Signal Processing",
        "name": "Digital Signal Processing Practice",
        "short_title": "Python DSP",
        "symbol_name": "Radix-2 FFT Butterfly Ring",
        "primary_color": "#14B8A6",
        "accent_color": "#0D9488",
        "gradient": ["#14B8A6", "#0F766E"],
        "category": "SYSTEMS_SIGNALS",
        "accessible_label": "Radix-2 Butterfly FFT Discrete Window Lattice Emblem",
        "technical_keywords": ["Cooley-Tukey FFT", "FIR Parks-McClellan", "IIR Butterworth", "Polyphase Decimation"],
        "svg_viewbox": "0 0 48 48",
        "svg_elements_count": 9
    },
    "EC23C08": {
        "code": "EC23C08",
        "discipline_name": "Telecommunications & RF Engineering",
        "professional_title": "Analog & Digital Modulation, Information Theory",
        "industry_domain": "Wireless Telecom, 5G/6G & RF Infrastructure",
        "subfield": "RF & Communications",
        "name": "Analog & Digital Communication Systems",
        "short_title": "Communication Systems",
        "symbol_name": "Smith Chart Reflection Circle",
        "primary_color": "#F97316",
        "accent_color": "#EA580C",
        "gradient": ["#F97316", "#C2410C"],
        "category": "SYSTEMS_SIGNALS",
        "accessible_label": "RF Smith Chart and QAM Constellation Emblem",
        "technical_keywords": ["Smith Chart Gamma", "QAM-16", "Shannon Capacity", "Friis Free-Space"],
        "svg_viewbox": "0 0 48 48",
        "svg_elements_count": 7
    },
    "EC8702": {
        "code": "EC8702",
        "discipline_name": "Embedded Real-Time Systems",
        "professional_title": "Deterministic Firmware, RTOS & Microcontrollers",
        "industry_domain": "Automotive, Avionics & Critical Embedded",
        "subfield": "Embedded Systems",
        "name": "Embedded Systems & RTOS Architecture",
        "short_title": "Embedded Systems",
        "symbol_name": "NVIC Priority DMA Pipeline",
        "primary_color": "#6366F1",
        "accent_color": "#4338CA",
        "gradient": ["#6366F1", "#3730A3"],
        "category": "EMBEDDED_VLSI",
        "accessible_label": "ARM Nested Vectored Interrupt Controller Microchip Emblem",
        "technical_keywords": ["NVIC Tail-Chaining", "FreeRTOS Mutex", "DMA Ping-Pong", "HardFault Handler"],
        "svg_viewbox": "0 0 48 48",
        "svg_elements_count": 13
    },
    "STM32-ACADEMY": {
        "code": "STM32-ACADEMY",
        "discipline_name": "ARM Cortex-M Microcontroller Engineering",
        "professional_title": "Bare-Metal Silicon Drivers & Hardware Peripherals",
        "industry_domain": "Industrial Edge IoT & Precision Control",
        "subfield": "Microcontroller Engineering",
        "name": "ARM Cortex-M Firmware Mastery",
        "short_title": "STM32 Academy",
        "symbol_name": "Cortex-M Harvard Silicon Matrix",
        "primary_color": "#00D8F6",
        "accent_color": "#0284C7",
        "gradient": ["#00D8F6", "#0369A1"],
        "category": "EMBEDDED_VLSI",
        "accessible_label": "STM32 ARM Cortex-M4 Microcontroller Die Emblem",
        "technical_keywords": ["Cortex-M4", "CMSIS-Core", "Bare-Metal HAL", "DMA Circular Buffer"],
        "svg_viewbox": "0 0 48 48",
        "svg_elements_count": 9
    },
    "IOT8701": {
        "code": "IOT8701",
        "discipline_name": "Internet of Things & Connected Systems",
        "professional_title": "Wireless Embedded Networks & Cloud Edge Gateways",
        "industry_domain": "Smart Infrastructure & Industrial IoT",
        "subfield": "IoT & Wireless",
        "name": "ESP32 IoT Systems & FreeRTOS",
        "short_title": "ESP32 IoT Systems",
        "symbol_name": "Xtensa RF Antenna Transceiver",
        "primary_color": "#E11D48",
        "accent_color": "#9F1239",
        "gradient": ["#E11D48", "#881337"],
        "category": "EMBEDDED_VLSI",
        "accessible_label": "ESP32 Wi-Fi Bluetooth Meander Antenna Emblem",
        "technical_keywords": ["Xtensa Dual-Core", "MQTT / TLS", "Deep-Sleep ULP", "BLE GATT Mesh"],
        "svg_viewbox": "0 0 48 48",
        "svg_elements_count": 5
    },
    "HDL6001": {
        "code": "HDL6001",
        "discipline_name": "FPGA Digital Design & Verilog HDL",
        "professional_title": "Synchronous RTL Synthesis & Digital Verification",
        "industry_domain": "FPGA Acceleration & ASIC Prototyping",
        "subfield": "FPGA & Hardware Synthesis",
        "name": "Verilog HDL & FPGA Hardware Synthesis",
        "short_title": "Verilog HDL & FPGA",
        "symbol_name": "FPGA Synchronous LUT Matrix",
        "primary_color": "#A855F7",
        "accent_color": "#7E22CE",
        "gradient": ["#A855F7", "#581C87"],
        "category": "EMBEDDED_VLSI",
        "accessible_label": "FPGA Look-Up Table (LUT) Switch Box Routing Fabric Emblem",
        "technical_keywords": ["Verilog RTL", "Non-blocking <=", "4-LUT Synthesis", "Hold Timing Closure"],
        "svg_viewbox": "0 0 48 48",
        "svg_elements_count": 9
    },
    "VLSI7001": {
        "code": "VLSI7001",
        "discipline_name": "Digital VLSI Design & Silicon Layout",
        "professional_title": "Sub-Micron CMOS Physical Design & Timing Closure",
        "industry_domain": "Semiconductor Foundry & Silicon Tape-Out",
        "subfield": "VLSI & Physical Design",
        "name": "CMOS VLSI Design & Physical Architecture",
        "short_title": "CMOS VLSI Design",
        "symbol_name": "CMOS Sub-Micron Transistor Layout",
        "primary_color": "#EAB308",
        "accent_color": "#CA8A04",
        "gradient": ["#EAB308", "#854D0E"],
        "category": "EMBEDDED_VLSI",
        "accessible_label": "CMOS Inverter Gate Physical Silicon Layout Emblem",
        "technical_keywords": ["Elmore Delay", "Logical Effort", "RC Wire Delay", "Clock Tree Skew"],
        "svg_viewbox": "0 0 48 48",
        "svg_elements_count": 7
    }
}

DEFAULT_FALLBACK: Dict[str, Any] = {
    "code": "CORE-GENERIC",
    "discipline_name": "Advanced Engineering Discipline",
    "professional_title": "VoltCore Apex Applied Engineering System",
    "industry_domain": "Electronics & Computer Engineering",
    "subfield": "Core Engineering",
    "name": "VoltCore Apex Engineering Course",
    "short_title": "Engineering Discipline",
    "symbol_name": "Silicon Chevron Beacon",
    "primary_color": "#00F0B5",
    "accent_color": "#10B981",
    "gradient": ["#00F0B5", "#00693E"],
    "category": "FOUNDATION",
    "accessible_label": "VoltCore Apex Academia Silicon Chevron Logo",
    "technical_keywords": ["Hardware-in-the-Loop", "Simulation", "Autonomous Cluster"],
    "svg_viewbox": "0 0 48 48",
    "svg_elements_count": 4
}


def get_subject_emblem(course_code: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves subject emblem metadata by course code with guaranteed fallback."""
    if not course_code:
        return DEFAULT_FALLBACK
    code_norm = course_code.strip().upper()
    return ECE_SUBJECT_EMBLEMS.get(code_norm, DEFAULT_FALLBACK)


def get_discipline_name(course_code: Optional[str] = None) -> str:
    """Retrieves clean, professional engineering discipline name (no raw course codes)."""
    meta = get_subject_emblem(course_code)
    return meta.get("discipline_name", meta.get("name", "Advanced Engineering Discipline"))


def get_professional_title(course_code: Optional[str] = None) -> str:
    """Retrieves full professional title for an engineering discipline."""
    meta = get_subject_emblem(course_code)
    return meta.get("professional_title", meta.get("name", "VoltCore Apex Applied Engineering System"))


def list_all_subject_emblems() -> List[Dict[str, Any]]:
    """Returns list of all 14 official ECE curriculum subject emblems."""
    return list(ECE_SUBJECT_EMBLEMS.values())


def list_discipline_catalog() -> List[Dict[str, Any]]:
    """Returns list of all 14 disciplines with clean professional names, domains, and subfields."""
    catalog = []
    for meta in ECE_SUBJECT_EMBLEMS.values():
        catalog.append({
            "discipline_name": meta["discipline_name"],
            "professional_title": meta["professional_title"],
            "industry_domain": meta["industry_domain"],
            "subfield": meta["subfield"],
            "code": meta["code"],
            "primary_color": meta["primary_color"]
        })
    return catalog


def get_institutional_branding() -> Dict[str, Any]:
    """Returns official VoltCore institutional branding dictionary."""
    return INSTITUTIONAL_BRANDING
