"""
========================================================================================
VoltCore Apex Academia - Smart PCB, SMD & Component Inspector Lab (Phase 30)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/component_inspector_engine.py
Target Environment: Lab 304 (Hardware Prototyping & Inspection Lab, MIT Campus, Chromepet)
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Lightweight backend hardware inspection engine handling:
    1. 4/5/6-Band Axial Resistor Color Code decoding (nominal resistance, tolerance, TCR ppm/K).
    2. SMD Resistor & Capacitor Marking decoders (3-digit, 4-digit, and EIA-96 1% standards).
    3. IPC-2221 PCB Trace Width & Current Capacity calculation (thermal rise, 1oz/2oz copper, resistance).
    4. IC Package Thermal Resistance (Theta-JA) and silicon junction temperature (T_J) safety assessment.
    5. High-concurrency SQLite WAL persistence for inspection histories and saved PCB trace designs.
========================================================================================
"""

import os
import math
import json
import uuid
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")

# Default student & faculty identifiers
DEFAULT_STUDENT_ID = "2023MITEC042"
DEFAULT_FACULTY_ID = "FAC_ECE_MIT_304"

# ========================================================================================
# Axial Resistor Color Standard Specifications (IEC 60062)
# ========================================================================================

COLOR_DIGITS: Dict[str, int] = {
    "black": 0,
    "brown": 1,
    "red": 2,
    "orange": 3,
    "yellow": 4,
    "green": 5,
    "blue": 6,
    "violet": 7,
    "grey": 8,
    "gray": 8,
    "white": 9
}

COLOR_MULTIPLIERS: Dict[str, float] = {
    "black": 1.0,           # 10^0
    "brown": 10.0,          # 10^1
    "red": 100.0,           # 10^2
    "orange": 1000.0,       # 10^3
    "yellow": 10000.0,      # 10^4
    "green": 100000.0,      # 10^5
    "blue": 1000000.0,      # 10^6
    "violet": 10000000.0,   # 10^7
    "grey": 100000000.0,    # 10^8
    "gray": 100000000.0,    # 10^8
    "white": 1000000000.0,  # 10^9
    "gold": 0.1,            # 10^-1
    "silver": 0.01          # 10^-2
}

COLOR_TOLERANCES: Dict[str, float] = {
    "brown": 1.0,    # +/- 1%
    "red": 2.0,      # +/- 2%
    "green": 0.5,    # +/- 0.5%
    "blue": 0.25,    # +/- 0.25%
    "violet": 0.1,   # +/- 0.1%
    "grey": 0.05,    # +/- 0.05%
    "gray": 0.05,    # +/- 0.05%
    "gold": 5.0,     # +/- 5%
    "silver": 10.0,  # +/- 10%
    "none": 20.0     # +/- 20%
}

COLOR_TCR: Dict[str, int] = {
    "black": 250,    # 250 ppm/K
    "brown": 100,    # 100 ppm/K
    "red": 50,       # 50 ppm/K
    "orange": 15,    # 15 ppm/K
    "yellow": 25,    # 25 ppm/K
    "green": 20,     # 20 ppm/K
    "blue": 10,      # 10 ppm/K
    "violet": 5,     # 5 ppm/K
    "grey": 1,       # 1 ppm/K
    "gray": 1        # 1 ppm/K
}

# ========================================================================================
# EIA-96 1% Resistor Table (96 Multiplier Decodes)
# ========================================================================================

EIA96_CODES: Dict[str, int] = {
    "01": 100, "02": 102, "03": 105, "04": 107, "05": 110, "06": 113, "07": 115, "08": 118,
    "09": 121, "10": 124, "11": 127, "12": 130, "13": 133, "14": 137, "15": 140, "16": 143,
    "17": 147, "18": 150, "19": 154, "20": 158, "21": 162, "22": 165, "23": 169, "24": 174,
    "25": 178, "26": 182, "27": 187, "28": 191, "29": 196, "30": 200, "31": 205, "32": 210,
    "33": 215, "34": 221, "35": 226, "36": 232, "37": 237, "38": 243, "39": 249, "40": 255,
    "41": 261, "42": 267, "43": 274, "44": 280, "45": 287, "46": 294, "47": 301, "48": 309,
    "49": 316, "50": 324, "51": 332, "52": 340, "53": 348, "54": 357, "55": 365, "56": 374,
    "57": 383, "58": 392, "59": 402, "60": 412, "61": 422, "62": 432, "63": 442, "64": 453,
    "65": 464, "66": 475, "67": 487, "68": 499, "69": 511, "70": 523, "71": 536, "72": 549,
    "73": 562, "74": 576, "75": 590, "76": 604, "77": 619, "78": 634, "79": 649, "80": 665,
    "81": 681, "82": 698, "83": 715, "84": 732, "85": 750, "86": 768, "87": 787, "88": 806,
    "89": 825, "90": 845, "91": 866, "92": 887, "93": 909, "94": 931, "95": 953, "96": 976
}

EIA96_MULTIPLIERS: Dict[str, float] = {
    "Z": 0.001,
    "Y": 0.01,
    "X": 0.1,
    "S": 0.1,
    "A": 1.0,
    "B": 10.0,
    "H": 10.0,
    "C": 100.0,
    "D": 1000.0,
    "E": 10000.0,
    "F": 100000.0
}

# ========================================================================================
# Curated Baseline SMD Components Catalog
# ========================================================================================

DEFAULT_SMD_CATALOG: List[Dict[str, Any]] = [
    {
        "code": "472",
        "component_type": "RESISTOR",
        "standard": "3-DIGIT",
        "nominal_value": 4700.0,
        "unit": "Ω",
        "value_formatted": "4.7 kΩ",
        "tolerance_pct": 5.0,
        "description": "Standard 0805/0603 Thick Film Resistor"
    },
    {
        "code": "103",
        "component_type": "RESISTOR",
        "standard": "3-DIGIT",
        "nominal_value": 10000.0,
        "unit": "Ω",
        "value_formatted": "10 kΩ",
        "tolerance_pct": 5.0,
        "description": "Standard I2C Bus Pull-Up Resistor"
    },
    {
        "code": "4R7",
        "component_type": "RESISTOR",
        "standard": "3-DIGIT",
        "nominal_value": 4.7,
        "unit": "Ω",
        "value_formatted": "4.7 Ω",
        "tolerance_pct": 5.0,
        "description": "Low-Ohmic Gate Damping Resistor"
    },
    {
        "code": "0R1",
        "component_type": "RESISTOR",
        "standard": "3-DIGIT",
        "nominal_value": 0.1,
        "unit": "Ω",
        "value_formatted": "0.1 Ω",
        "tolerance_pct": 5.0,
        "description": "Current Shunt Sensing Resistor"
    },
    {
        "code": "000",
        "component_type": "RESISTOR",
        "standard": "3-DIGIT",
        "nominal_value": 0.0,
        "unit": "Ω",
        "value_formatted": "0 Ω Jumper",
        "tolerance_pct": 0.0,
        "description": "Zero-Ohm Configuration Link"
    },
    {
        "code": "1001",
        "component_type": "RESISTOR",
        "standard": "4-DIGIT",
        "nominal_value": 1000.0,
        "unit": "Ω",
        "value_formatted": "1.00 kΩ",
        "tolerance_pct": 1.0,
        "description": "Precision 1% Thin-Film Divider Resistor"
    },
    {
        "code": "4702",
        "component_type": "RESISTOR",
        "standard": "4-DIGIT",
        "nominal_value": 47000.0,
        "unit": "Ω",
        "value_formatted": "47.0 kΩ",
        "tolerance_pct": 1.0,
        "description": "High Precision Instrumentation Resistor"
    },
    {
        "code": "R100",
        "component_type": "RESISTOR",
        "standard": "4-DIGIT",
        "nominal_value": 0.100,
        "unit": "Ω",
        "value_formatted": "0.100 Ω",
        "tolerance_pct": 1.0,
        "description": "Kelvin 4-Wire Current Sense Resistor"
    },
    {
        "code": "01A",
        "component_type": "RESISTOR",
        "standard": "EIA-96",
        "nominal_value": 100.0,
        "unit": "Ω",
        "value_formatted": "100 Ω",
        "tolerance_pct": 1.0,
        "description": "EIA-96 Precision 1% 100 Ohm Resistor"
    },
    {
        "code": "01C",
        "component_type": "RESISTOR",
        "standard": "EIA-96",
        "nominal_value": 10000.0,
        "unit": "Ω",
        "value_formatted": "10.0 kΩ",
        "tolerance_pct": 1.0,
        "description": "EIA-96 Precision 1% 10 kOhm Resistor"
    },
    {
        "code": "68X",
        "component_type": "RESISTOR",
        "standard": "EIA-96",
        "nominal_value": 49.9,
        "unit": "Ω",
        "value_formatted": "49.9 Ω",
        "tolerance_pct": 1.0,
        "description": "High-Speed Ethernet/USB Termination Resistor (49.9 Ohm)"
    },
    {
        "code": "104",
        "component_type": "CAPACITOR",
        "standard": "3-DIGIT",
        "nominal_value": 100000.0,
        "unit": "pF",
        "value_formatted": "100 nF (0.1 µF)",
        "tolerance_pct": 10.0,
        "description": "Standard IC Decoupling Ceramic MLCC Capacitor"
    },
    {
        "code": "223",
        "component_type": "CAPACITOR",
        "standard": "3-DIGIT",
        "nominal_value": 22000.0,
        "unit": "pF",
        "value_formatted": "22 nF",
        "tolerance_pct": 10.0,
        "description": "Active Filter Timing MLCC Capacitor"
    },
    {
        "code": "475",
        "component_type": "CAPACITOR",
        "standard": "3-DIGIT",
        "nominal_value": 4700000.0,
        "unit": "pF",
        "value_formatted": "4.7 µF",
        "tolerance_pct": 20.0,
        "description": "LDO Low-ESR Output Decoupling Capacitor"
    }
]

# ========================================================================================
# Curated Baseline IC Package Thermal Characteristics Catalog
# ========================================================================================

DEFAULT_IC_THERMAL_CATALOG: List[Dict[str, Any]] = [
    {
        "package_code": "DIP-8",
        "package_name": "Dual In-Line Package (8-pin)",
        "package_type": "THROUGH_HOLE",
        "theta_ja_degc_w": 100.0,
        "theta_jc_degc_w": 40.0,
        "max_power_w": 1.0,
        "max_tj_c": 125.0,
        "typical_applications": "Classic Op-Amps (LM741, NE5532), 555 Timers, Breadboard Circuits"
    },
    {
        "package_code": "SOIC-8",
        "package_name": "Small Outline IC (8-pin, 150 mil)",
        "package_type": "SMD",
        "theta_ja_degc_w": 150.0,
        "theta_jc_degc_w": 50.0,
        "max_power_w": 0.65,
        "max_tj_c": 125.0,
        "typical_applications": "Surface Mount Op-Amps, EEPROMs (24C08), Gate Drivers"
    },
    {
        "package_code": "TO-220",
        "package_name": "Transistor Outline 220 (Power Tab)",
        "package_type": "THROUGH_HOLE",
        "theta_ja_degc_w": 62.5,
        "theta_jc_degc_w": 2.5,
        "max_power_w": 15.0,
        "max_tj_c": 150.0,
        "typical_applications": "Linear Regulators (LM7805), Power MOSFETs (IRF540N), Triacs"
    },
    {
        "package_code": "SOT-23",
        "package_name": "Small Outline Transistor (3-pin)",
        "package_type": "SMD",
        "theta_ja_degc_w": 250.0,
        "theta_jc_degc_w": 90.0,
        "max_power_w": 0.35,
        "max_tj_c": 125.0,
        "typical_applications": "Small-Signal BJTs (2N3904, BC847), Switching Diodes, Reset ICs"
    },
    {
        "package_code": "QFP-64",
        "package_name": "Quad Flat Package (64-pin, 0.5mm pitch)",
        "package_type": "SMD",
        "theta_ja_degc_w": 45.0,
        "theta_jc_degc_w": 12.0,
        "max_power_w": 1.5,
        "max_tj_c": 125.0,
        "typical_applications": "Microcontrollers (STM32F401, ATmega2560), Audio DSPs"
    },
    {
        "package_code": "QFN-32",
        "package_name": "Quad Flat No-Leads (32-pin with Thermal Pad)",
        "package_type": "SMD",
        "theta_ja_degc_w": 38.0,
        "theta_jc_degc_w": 8.0,
        "max_power_w": 2.0,
        "max_tj_c": 125.0,
        "typical_applications": "ESP32-WROOM SoC, nRF52840 BLE, Motor Drivers, Wireless Transceivers"
    },
    {
        "package_code": "BGA-256",
        "package_name": "Ball Grid Array (256-ball, 0.8mm pitch)",
        "package_type": "SMD",
        "theta_ja_degc_w": 30.0,
        "theta_jc_degc_w": 6.0,
        "max_power_w": 3.5,
        "max_tj_c": 125.0,
        "typical_applications": "Xilinx Artix-7 FPGAs, High-Speed Networking Processors, DDR Memory"
    }
]


def format_resistance(value_ohms: float) -> str:
    """Format numerical resistance into clean engineering notation."""
    if value_ohms == 0:
        return "0 Ω"
    abs_v = abs(value_ohms)
    if abs_v >= 1e9:
        v = value_ohms / 1e9
        return f"{v:g} GΩ" if v == int(v) else f"{v:.2f} GΩ"
    elif abs_v >= 1e6:
        v = value_ohms / 1e6
        return f"{v:g} MΩ" if v == int(v) else f"{v:.2f} MΩ"
    elif abs_v >= 1e3:
        v = value_ohms / 1e3
        return f"{v:g} kΩ" if v == int(v) else f"{v:.2f} kΩ"
    elif abs_v < 1:
        return f"{value_ohms:.3f} Ω"
    else:
        return f"{value_ohms:g} Ω" if value_ohms == int(value_ohms) else f"{value_ohms:.2f} Ω"


def format_capacitance_pf(pf: float) -> str:
    """Format capacitance given in picofarads into engineering units."""
    if pf >= 1e6:
        uf = pf / 1e6
        return f"{uf:g} µF" if uf == int(uf) else f"{uf:.2f} µF"
    elif pf >= 1e3:
        nf = pf / 1e3
        return f"{nf:g} nF" if nf == int(nf) else f"{nf:.2f} nF"
    else:
        return f"{pf:g} pF"


class ComponentInspectorEngine:
    """
    Lightweight, thread-safe hardware component inspection engine.
    Computes resistor color-code decoding, SMD code lookups, IPC-2221 PCB trace width,
    and IC package junction temperatures with zero bloat and low thermal overhead.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Create and return a configured SQLite connection with WAL enabled."""
        conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def _init_db(self):
        """Initialize database tables and seed baseline SMD and IC packages."""
        with self._lock:
            conn = self._get_connection()
            try:
                # 1. Component Inspection History
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS component_inspection_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        inspection_type TEXT NOT NULL,
                        component_class TEXT NOT NULL,
                        input_params_json TEXT NOT NULL,
                        calculated_result_json TEXT NOT NULL,
                        inspected_by TEXT NOT NULL DEFAULT '2023MITEC042',
                        created_at TEXT NOT NULL
                    );
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_comp_insp_type ON component_inspection_history(inspection_type);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_comp_insp_created ON component_inspection_history(created_at);")

                # 2. Saved PCB Trace Calculations
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS saved_pcb_trace_calculations (
                        calc_id TEXT PRIMARY KEY,
                        design_name TEXT NOT NULL,
                        current_a REAL NOT NULL,
                        temp_rise_c REAL NOT NULL,
                        copper_oz REAL NOT NULL,
                        layer_type TEXT NOT NULL,
                        trace_length_cm REAL NOT NULL,
                        width_mils REAL NOT NULL,
                        width_mm REAL NOT NULL,
                        resistance_ohms REAL NOT NULL,
                        voltage_drop_v REAL NOT NULL,
                        power_loss_w REAL NOT NULL,
                        created_by TEXT NOT NULL DEFAULT '2023MITEC042',
                        created_at TEXT NOT NULL
                    );
                """)

                # 3. SMD Marking Catalog
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS smd_marking_catalog (
                        code TEXT PRIMARY KEY,
                        component_type TEXT NOT NULL,
                        standard TEXT NOT NULL,
                        nominal_value REAL NOT NULL,
                        unit TEXT NOT NULL,
                        value_formatted TEXT NOT NULL,
                        tolerance_pct REAL NOT NULL,
                        description TEXT NOT NULL
                    );
                """)

                # 4. IC Package Thermal Catalog
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS ic_package_thermal_catalog (
                        package_code TEXT PRIMARY KEY,
                        package_name TEXT NOT NULL,
                        package_type TEXT NOT NULL,
                        theta_ja_degc_w REAL NOT NULL,
                        theta_jc_degc_w REAL NOT NULL,
                        max_power_w REAL NOT NULL,
                        max_tj_c REAL NOT NULL,
                        typical_applications TEXT NOT NULL
                    );
                """)

                # Seed SMD Catalog if empty
                count_smd = conn.execute("SELECT COUNT(*) FROM smd_marking_catalog;").fetchone()[0]
                if count_smd == 0:
                    for smd in DEFAULT_SMD_CATALOG:
                        conn.execute("""
                            INSERT OR IGNORE INTO smd_marking_catalog
                            (code, component_type, standard, nominal_value, unit, value_formatted, tolerance_pct, description)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                        """, (
                            smd["code"], smd["component_type"], smd["standard"],
                            smd["nominal_value"], smd["unit"], smd["value_formatted"],
                            smd["tolerance_pct"], smd["description"]
                        ))

                # Seed IC Thermal Catalog if empty
                count_ic = conn.execute("SELECT COUNT(*) FROM ic_package_thermal_catalog;").fetchone()[0]
                if count_ic == 0:
                    for ic in DEFAULT_IC_THERMAL_CATALOG:
                        conn.execute("""
                            INSERT OR IGNORE INTO ic_package_thermal_catalog
                            (package_code, package_name, package_type, theta_ja_degc_w, theta_jc_degc_w, max_power_w, max_tj_c, typical_applications)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                        """, (
                            ic["package_code"], ic["package_name"], ic["package_type"],
                            ic["theta_ja_degc_w"], ic["theta_jc_degc_w"], ic["max_power_w"],
                            ic["max_tj_c"], ic["typical_applications"]
                        ))

                conn.commit()
            finally:
                conn.close()

    # ====================================================================================
    # 1. Axial Resistor Color Code Decoding (4, 5, 6-band)
    # ====================================================================================

    def decode_axial_resistor(self, bands: List[str], record_history: bool = True, actor_id: str = DEFAULT_STUDENT_ID) -> Dict[str, Any]:
        """
        Decodes 4, 5, or 6-band axial resistor color codes into resistance, tolerance, and TCR.
        Returns nominal resistance, minimum/maximum values, formatted engineering string, and band metadata.
        """
        clean_bands = [b.strip().lower() for b in bands if b and b.strip()]
        num_bands = len(clean_bands)

        if num_bands not in (4, 5, 6):
            return {
                "status": "ERROR",
                "message": f"Invalid band count ({num_bands}). Supported axial standards are 4-band, 5-band, or 6-band."
            }

        # Validate bands against allowed color tables
        if num_bands == 4:
            b1, b2, b_mult, b_tol = clean_bands
            b_tcr = None
            if b1 not in COLOR_DIGITS or b2 not in COLOR_DIGITS:
                return {"status": "ERROR", "message": f"Bands 1 and 2 must be valid digits. Got: '{b1}', '{b2}'."}
            if b_mult not in COLOR_MULTIPLIERS:
                return {"status": "ERROR", "message": f"Band 3 multiplier '{b_mult}' is invalid."}
            if b_tol not in COLOR_TOLERANCES:
                return {"status": "ERROR", "message": f"Band 4 tolerance '{b_tol}' is invalid."}

            digits_val = COLOR_DIGITS[b1] * 10 + COLOR_DIGITS[b2]
            multiplier = COLOR_MULTIPLIERS[b_mult]
            tolerance_pct = COLOR_TOLERANCES[b_tol]
            tcr_ppm = None

        elif num_bands == 5:
            b1, b2, b3, b_mult, b_tol = clean_bands
            b_tcr = None
            if b1 not in COLOR_DIGITS or b2 not in COLOR_DIGITS or b3 not in COLOR_DIGITS:
                return {"status": "ERROR", "message": f"Bands 1, 2, and 3 must be valid digits. Got: '{b1}', '{b2}', '{b3}'."}
            if b_mult not in COLOR_MULTIPLIERS:
                return {"status": "ERROR", "message": f"Band 4 multiplier '{b_mult}' is invalid."}
            if b_tol not in COLOR_TOLERANCES:
                return {"status": "ERROR", "message": f"Band 5 tolerance '{b_tol}' is invalid."}

            digits_val = COLOR_DIGITS[b1] * 100 + COLOR_DIGITS[b2] * 10 + COLOR_DIGITS[b3]
            multiplier = COLOR_MULTIPLIERS[b_mult]
            tolerance_pct = COLOR_TOLERANCES[b_tol]
            tcr_ppm = None

        else:  # 6-band
            b1, b2, b3, b_mult, b_tol, b_tcr = clean_bands
            if b1 not in COLOR_DIGITS or b2 not in COLOR_DIGITS or b3 not in COLOR_DIGITS:
                return {"status": "ERROR", "message": f"Bands 1, 2, and 3 must be valid digits. Got: '{b1}', '{b2}', '{b3}'."}
            if b_mult not in COLOR_MULTIPLIERS:
                return {"status": "ERROR", "message": f"Band 4 multiplier '{b_mult}' is invalid."}
            if b_tol not in COLOR_TOLERANCES:
                return {"status": "ERROR", "message": f"Band 5 tolerance '{b_tol}' is invalid."}
            if b_tcr not in COLOR_TCR:
                return {"status": "ERROR", "message": f"Band 6 temperature coefficient '{b_tcr}' is invalid."}

            digits_val = COLOR_DIGITS[b1] * 100 + COLOR_DIGITS[b2] * 10 + COLOR_DIGITS[b3]
            multiplier = COLOR_MULTIPLIERS[b_mult]
            tolerance_pct = COLOR_TOLERANCES[b_tol]
            tcr_ppm = COLOR_TCR[b_tcr]

        resistance_ohms = round(digits_val * multiplier, 6)
        min_ohms = round(resistance_ohms * (1.0 - tolerance_pct / 100.0), 6)
        max_ohms = round(resistance_ohms * (1.0 + tolerance_pct / 100.0), 6)

        result = {
            "status": "SUCCESS",
            "band_count": num_bands,
            "bands": clean_bands,
            "digits_value": digits_val,
            "multiplier": multiplier,
            "resistance_ohms": resistance_ohms,
            "formatted": format_resistance(resistance_ohms),
            "tolerance_pct": tolerance_pct,
            "min_resistance_ohms": min_ohms,
            "max_resistance_ohms": max_ohms,
            "formatted_range": f"{format_resistance(min_ohms)} - {format_resistance(max_ohms)}",
            "tcr_ppm_k": tcr_ppm,
            "decoded_at": datetime.now(timezone.utc).isoformat()
        }

        if record_history:
            self._save_inspection_record(
                inspection_type="AXIAL_RESISTOR",
                component_class="RESISTOR",
                inputs={"bands": clean_bands, "num_bands": num_bands},
                results=result,
                actor_id=actor_id
            )

        return result

    # ====================================================================================
    # 2. SMD Resistor & Capacitor Marking Decoder
    # ====================================================================================

    def decode_smd_marking(self, code: str, component_type: str = "RESISTOR", record_history: bool = True, actor_id: str = DEFAULT_STUDENT_ID) -> Dict[str, Any]:
        """
        Decodes SMD 3-digit, 4-digit, and EIA-96 resistor markings, as well as 3-digit ceramic capacitor markings.
        """
        raw_code = code.strip().upper()
        if not raw_code:
            return {"status": "ERROR", "message": "SMD code string cannot be empty."}

        clean_type = component_type.strip().upper()
        if clean_type not in ("RESISTOR", "CAPACITOR"):
            return {"status": "ERROR", "message": "component_type must be either 'RESISTOR' or 'CAPACITOR'."}

        # Check in local database catalog first for instant cached hit
        with self._lock:
            conn = self._get_connection()
            try:
                row = conn.execute(
                    "SELECT * FROM smd_marking_catalog WHERE code = ? AND component_type = ?;",
                    (raw_code, clean_type)
                ).fetchone()
                if row:
                    cached_hit = {
                        "status": "SUCCESS",
                        "code": row["code"],
                        "component_type": row["component_type"],
                        "standard": row["standard"],
                        "nominal_value": row["nominal_value"],
                        "unit": row["unit"],
                        "value_formatted": row["value_formatted"],
                        "tolerance_pct": row["tolerance_pct"],
                        "description": row["description"],
                        "source": "CATALOG_MATCH"
                    }
                    if record_history:
                        self._save_inspection_record(
                            inspection_type="SMD_MARKING",
                            component_class=clean_type,
                            inputs={"code": raw_code, "component_type": clean_type},
                            results=cached_hit,
                            actor_id=actor_id
                        )
                    return cached_hit
            finally:
                conn.close()

        # Algorithmic fallback decoder
        if clean_type == "RESISTOR":
            # 1. Zero ohm jumper
            if raw_code in ("0", "00", "000", "0000"):
                res = {
                    "status": "SUCCESS",
                    "code": raw_code,
                    "component_type": "RESISTOR",
                    "standard": f"{len(raw_code)}-DIGIT",
                    "nominal_value": 0.0,
                    "unit": "Ω",
                    "value_formatted": "0 Ω (Jumper Link)",
                    "tolerance_pct": 0.0,
                    "description": "Zero-ohm PCB bridge jumper",
                    "source": "ALGORITHMIC_SOLVER"
                }
                return res

            # 2. Resistors with 'R' representing decimal point
            if "R" in raw_code:
                try:
                    val_str = raw_code.replace("R", ".")
                    if val_str.startswith("."):
                        val_str = "0" + val_str
                    val = float(val_str)
                    std = "4-DIGIT" if len(raw_code) == 4 else "3-DIGIT"
                    tol = 1.0 if std == "4-DIGIT" else 5.0
                    res = {
                        "status": "SUCCESS",
                        "code": raw_code,
                        "component_type": "RESISTOR",
                        "standard": std,
                        "nominal_value": val,
                        "unit": "Ω",
                        "value_formatted": format_resistance(val),
                        "tolerance_pct": tol,
                        "description": f"Low-ohmic sub-standard resistor ({raw_code})",
                        "source": "ALGORITHMIC_SOLVER"
                    }
                    return res
                except ValueError:
                    return {"status": "ERROR", "message": f"Malformed R-notated resistor code: '{raw_code}'"}

            # 3. EIA-96 Standard (2 digits + 1 letter, e.g., '01C', '68X')
            if len(raw_code) == 3 and raw_code[:2].isdigit() and raw_code[2].isalpha():
                num_code = raw_code[:2]
                mult_letter = raw_code[2]
                if num_code in EIA96_CODES and mult_letter in EIA96_MULTIPLIERS:
                    base_val = EIA96_CODES[num_code]
                    mult = EIA96_MULTIPLIERS[mult_letter]
                    res_val = round(base_val * mult, 4)
                    res = {
                        "status": "SUCCESS",
                        "code": raw_code,
                        "component_type": "RESISTOR",
                        "standard": "EIA-96",
                        "nominal_value": res_val,
                        "unit": "Ω",
                        "value_formatted": format_resistance(res_val),
                        "tolerance_pct": 1.0,
                        "description": f"EIA-96 1% precision metal film resistor ({raw_code})",
                        "source": "ALGORITHMIC_SOLVER"
                    }
                    return res

            # 4. Standard 3-digit Resistor (e.g. 472 -> 47 * 10^2 = 4700)
            if len(raw_code) == 3 and raw_code.isdigit():
                sig = int(raw_code[:2])
                exp = int(raw_code[2])
                val = float(sig * (10 ** exp))
                res = {
                    "status": "SUCCESS",
                    "code": raw_code,
                    "component_type": "RESISTOR",
                    "standard": "3-DIGIT",
                    "nominal_value": val,
                    "unit": "Ω",
                    "value_formatted": format_resistance(val),
                    "tolerance_pct": 5.0,
                    "description": f"Standard 3-digit 5% thick-film resistor ({raw_code})",
                    "source": "ALGORITHMIC_SOLVER"
                }
                return res

            # 5. Standard 4-digit Resistor (e.g. 1001 -> 100 * 10^1 = 1000)
            if len(raw_code) == 4 and raw_code.isdigit():
                sig = int(raw_code[:3])
                exp = int(raw_code[3])
                val = float(sig * (10 ** exp))
                res = {
                    "status": "SUCCESS",
                    "code": raw_code,
                    "component_type": "RESISTOR",
                    "standard": "4-DIGIT",
                    "nominal_value": val,
                    "unit": "Ω",
                    "value_formatted": format_resistance(val),
                    "tolerance_pct": 1.0,
                    "description": f"Precision 4-digit 1% thin-film resistor ({raw_code})",
                    "source": "ALGORITHMIC_SOLVER"
                }
                return res

            return {"status": "ERROR", "message": f"Unable to decode SMD resistor code '{raw_code}'. Check code format."}

        else:
            # CAPACITOR: typically 3-digit picofarad encoding (e.g. 104 -> 10 * 10^4 pF = 100 nF)
            if len(raw_code) == 3 and raw_code.isdigit():
                sig = int(raw_code[:2])
                exp = int(raw_code[2])
                pf = float(sig * (10 ** exp))
                res = {
                    "status": "SUCCESS",
                    "code": raw_code,
                    "component_type": "CAPACITOR",
                    "standard": "3-DIGIT",
                    "nominal_value": pf,
                    "unit": "pF",
                    "value_formatted": format_capacitance_pf(pf),
                    "tolerance_pct": 10.0,
                    "description": f"Standard 3-digit ceramic capacitor marking ({raw_code})",
                    "source": "ALGORITHMIC_SOLVER"
                }
                return res

            return {"status": "ERROR", "message": f"Unable to decode SMD capacitor code '{raw_code}'. Expected 3 digits."}

    # ====================================================================================
    # 3. IPC-2221 PCB Trace Width & Current Capacity Calculation
    # ====================================================================================

    def calculate_pcb_trace_width(
        self,
        current_a: float,
        temp_rise_c: float = 10.0,
        copper_oz: float = 1.0,
        trace_type: str = "external",
        trace_length_cm: float = 10.0,
        ambient_temp_c: float = 25.0,
        design_name: Optional[str] = None,
        record_history: bool = True,
        actor_id: str = DEFAULT_STUDENT_ID
    ) -> Dict[str, Any]:
        """
        Calculates required PCB trace width in mils and mm according to IPC-2221:
          I = k * (Delta_T)^b * A^c
          Area A = (I / (k * Delta_T^b))^(1/c)  [mils^2]
        Trace thickness:
          1 oz copper = 1.378 mils = 0.035 mm
          2 oz copper = 2.756 mils = 0.070 mm
          0.5 oz copper = 0.689 mils = 0.0175 mm
        Also derives trace resistance, voltage drop, and Joule power dissipation.
        """
        if current_a <= 0:
            return {"status": "ERROR", "message": "Current (Amperes) must be greater than zero."}
        if temp_rise_c <= 0:
            return {"status": "ERROR", "message": "Temperature rise (°C) must be greater than zero."}
        if copper_oz <= 0:
            return {"status": "ERROR", "message": "Copper thickness (oz) must be greater than zero."}
        if trace_length_cm <= 0:
            return {"status": "ERROR", "message": "Trace length (cm) must be greater than zero."}

        clean_type = trace_type.strip().lower()
        if clean_type not in ("external", "internal"):
            return {"status": "ERROR", "message": "trace_type must be either 'external' or 'internal'."}

        # IPC-2221 constants
        # External: k = 0.048, b = 0.44, c = 0.725
        # Internal: k = 0.024, b = 0.44, c = 0.725
        b = 0.44
        c = 0.725
        k = 0.048 if clean_type == "external" else 0.024

        # Cross-sectional area in mils^2
        area_mils2 = math.pow(current_a / (k * math.pow(temp_rise_c, b)), 1.0 / c)

        # Copper thickness in mils (1 oz ~ 1.378 mils)
        thickness_mils = copper_oz * 1.378
        thickness_mm = thickness_mils * 0.0254

        # Required trace width in mils and mm
        width_mils = area_mils2 / thickness_mils
        width_mm = width_mils * 0.0254

        # Trace resistance calculation
        # Copper resistivity at 20°C: 1.72e-6 ohm-cm
        # Temp coeff alpha = 0.00393 / °C
        # T_op = ambient_temp_c + temp_rise_c
        t_op = ambient_temp_c + temp_rise_c
        rho_20 = 1.72e-6  # ohm-cm
        alpha = 0.00393
        rho_t = rho_20 * (1.0 + alpha * (t_op - 20.0))

        # Area in cm^2 (1 mil = 0.00254 cm -> 1 mil^2 = 6.4516e-6 cm^2)
        area_cm2 = area_mils2 * 6.4516e-6
        resistance_ohms = rho_t * (trace_length_cm / area_cm2)

        # Voltage drop and Joule power loss
        voltage_drop_v = current_a * resistance_ohms
        power_loss_w = (current_a ** 2) * resistance_ohms

        calc_id = f"PCB_TRC_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}_{uuid.uuid4().hex[:6]}"
        result = {
            "status": "SUCCESS",
            "calc_id": calc_id,
            "design_name": design_name or f"{clean_type.capitalize()} {current_a}A Trace",
            "inputs": {
                "current_a": current_a,
                "temp_rise_c": temp_rise_c,
                "copper_oz": copper_oz,
                "trace_type": clean_type,
                "trace_length_cm": trace_length_cm,
                "ambient_temp_c": ambient_temp_c
            },
            "cross_sectional_area_mils2": round(area_mils2, 4),
            "thickness_mils": round(thickness_mils, 4),
            "thickness_mm": round(thickness_mm, 4),
            "trace_width_mils": round(width_mils, 2),
            "trace_width_mm": round(width_mm, 4),
            "operating_temp_c": round(t_op, 1),
            "resistance_ohms": round(resistance_ohms, 6),
            "voltage_drop_v": round(voltage_drop_v, 6),
            "power_loss_w": round(power_loss_w, 6),
            "standard": "IPC-2221",
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }

        if record_history:
            with self._lock:
                conn = self._get_connection()
                try:
                    conn.execute("""
                        INSERT INTO saved_pcb_trace_calculations
                        (calc_id, design_name, current_a, temp_rise_c, copper_oz, layer_type, trace_length_cm,
                         width_mils, width_mm, resistance_ohms, voltage_drop_v, power_loss_w, created_by, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        calc_id, result["design_name"], current_a, temp_rise_c, copper_oz, clean_type,
                        trace_length_cm, result["trace_width_mils"], result["trace_width_mm"],
                        result["resistance_ohms"], result["voltage_drop_v"], result["power_loss_w"],
                        actor_id, result["calculated_at"]
                    ))
                    conn.commit()
                finally:
                    conn.close()

            self._save_inspection_record(
                inspection_type="PCB_TRACE",
                component_class="PCB",
                inputs=result["inputs"],
                results=result,
                actor_id=actor_id
            )

        return result

    # ====================================================================================
    # 4. IC Package Thermal Resistance & Junction Temperature Assessment
    # ====================================================================================

    def evaluate_ic_thermal_dissipation(
        self,
        package_code: str,
        power_watts: float,
        ambient_temp_c: float = 25.0,
        theta_ja_custom: Optional[float] = None,
        target_max_tj_c: float = 100.0,
        record_history: bool = True,
        actor_id: str = DEFAULT_STUDENT_ID
    ) -> Dict[str, Any]:
        """
        Calculates IC silicon junction temperature:
          T_J = T_A + (P_D * Theta_JA)
        Evaluates reliability status (OPTIMAL, ELEVATED, WARNING, CRITICAL_HAZARD)
        and specifies required heatsink / active cooling thermal resistance Theta_SA if necessary.
        """
        clean_code = package_code.strip().upper()
        if power_watts < 0:
            return {"status": "ERROR", "message": "Power dissipation (Watts) cannot be negative."}

        # Look up package in catalog
        theta_ja = theta_ja_custom
        theta_jc = 15.0
        max_power = 1.0
        max_silicon_tj = 125.0
        package_name = clean_code
        pkg_type = "SMD"

        with self._lock:
            conn = self._get_connection()
            try:
                row = conn.execute("SELECT * FROM ic_package_thermal_catalog WHERE package_code = ?;", (clean_code,)).fetchone()
                if row:
                    package_name = row["package_name"]
                    pkg_type = row["package_type"]
                    theta_jc = row["theta_jc_degc_w"]
                    max_power = row["max_power_w"]
                    max_silicon_tj = row["max_tj_c"]
                    if theta_ja is None:
                        theta_ja = row["theta_ja_degc_w"]
            finally:
                conn.close()

        if theta_ja is None:
            theta_ja = 100.0  # Default fallback if unknown package

        # Junction temperature calculation
        tj = ambient_temp_c + (power_watts * theta_ja)
        delta_t = tj - ambient_temp_c

        # Thermal condition assessment
        if tj <= 85.0:
            status_level = "OPTIMAL"
            status_color = "emerald"
            recommendation = "Operating well within safe silicon thresholds. Passive convection cooling is sufficient."
            heatsink_required = False
            needed_theta_sa = None
        elif tj <= 105.0:
            status_level = "ELEVATED"
            status_color = "amber"
            recommendation = "Elevated junction temperature. Adequate PCB ground copper pour or convection airflow advised."
            heatsink_required = False
            needed_theta_sa = None
        elif tj <= max_silicon_tj:
            status_level = "WARNING"
            status_color = "orange"
            recommendation = f"High thermal stress (>105°C). Aluminum heatsink, thermal vias, or active airflow recommended to safeguard long-term MTBF."
            heatsink_required = True
            # Needed Theta_JA to keep Tj <= target_max_tj_c
            if power_watts > 0:
                needed_theta_ja = (target_max_tj_c - ambient_temp_c) / power_watts
                # Theta_SA = Theta_JA_needed - Theta_JC - Theta_CS (assume interface grease ~ 0.5 °C/W)
                needed_theta_sa = max(0.1, round(needed_theta_ja - theta_jc - 0.5, 2))
            else:
                needed_theta_sa = None
        else:
            status_level = "CRITICAL_HAZARD"
            status_color = "red"
            recommendation = f"Silicon junction temperature {tj:.1f}°C exceeds rated maximum {max_silicon_tj}°C! Risk of thermal runaway and permanent junction burnout. Immediate external heatsink or lower operating power required."
            heatsink_required = True
            needed_theta_ja = (target_max_tj_c - ambient_temp_c) / power_watts if power_watts > 0 else 10.0
            needed_theta_sa = max(0.1, round(needed_theta_ja - theta_jc - 0.5, 2))

        result = {
            "status": "SUCCESS",
            "package_code": clean_code,
            "package_name": package_name,
            "package_type": pkg_type,
            "power_watts": power_watts,
            "ambient_temp_c": ambient_temp_c,
            "theta_ja_degc_w": theta_ja,
            "theta_jc_degc_w": theta_jc,
            "junction_temp_c": round(tj, 2),
            "temp_rise_c": round(delta_t, 2),
            "max_rated_tj_c": max_silicon_tj,
            "safety_margin_c": round(max_silicon_tj - tj, 2),
            "thermal_status": status_level,
            "status_color": status_color,
            "heatsink_required": heatsink_required,
            "recommended_heatsink_theta_sa": needed_theta_sa,
            "recommendation": recommendation,
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }

        if record_history:
            self._save_inspection_record(
                inspection_type="IC_THERMAL",
                component_class="IC",
                inputs={
                    "package_code": clean_code,
                    "power_watts": power_watts,
                    "ambient_temp_c": ambient_temp_c,
                    "theta_ja": theta_ja
                },
                results=result,
                actor_id=actor_id
            )

        return result

    # ====================================================================================
    # 5. Inspection History & Catalogs Query APIs
    # ====================================================================================

    def _save_inspection_record(self, inspection_type: str, component_class: str, inputs: Dict[str, Any], results: Dict[str, Any], actor_id: str):
        """Helper to append an inspection record into SQLite WAL."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT INTO component_inspection_history
                    (inspection_type, component_class, input_params_json, calculated_result_json, inspected_by, created_at)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (
                    inspection_type, component_class, json.dumps(inputs), json.dumps(results),
                    actor_id, datetime.now(timezone.utc).isoformat()
                ))
                conn.commit()
            except Exception:
                pass
            finally:
                conn.close()

    def get_inspection_history(self, inspection_type: Optional[str] = None, limit: int = 25) -> Dict[str, Any]:
        """Fetch chronological component inspection logs."""
        with self._lock:
            conn = self._get_connection()
            try:
                query = "SELECT * FROM component_inspection_history"
                params: List[Any] = []
                if inspection_type:
                    query += " WHERE inspection_type = ?"
                    params.append(inspection_type.strip().upper())
                query += " ORDER BY id DESC LIMIT ?;"
                params.append(limit)

                rows = conn.execute(query, tuple(params)).fetchall()
                records = []
                for r in rows:
                    records.append({
                        "id": r["id"],
                        "inspection_type": r["inspection_type"],
                        "component_class": r["component_class"],
                        "input_params": json.loads(r["input_params_json"]),
                        "calculated_result": json.loads(r["calculated_result_json"]),
                        "inspected_by": r["inspected_by"],
                        "created_at": r["created_at"]
                    })
                return {"status": "SUCCESS", "count": len(records), "records": records}
            finally:
                conn.close()

    def get_saved_pcb_calculations(self, limit: int = 25) -> Dict[str, Any]:
        """Retrieve stored IPC-2221 PCB trace calculation records."""
        with self._lock:
            conn = self._get_connection()
            try:
                rows = conn.execute(
                    "SELECT * FROM saved_pcb_trace_calculations ORDER BY created_at DESC LIMIT ?;",
                    (limit,)
                ).fetchall()
                calcs = [dict(r) for r in rows]
                return {"status": "SUCCESS", "count": len(calcs), "calculations": calcs}
            finally:
                conn.close()

    def get_catalogs(self) -> Dict[str, Any]:
        """Return reference catalogs for SMD markings and IC package thermal models."""
        with self._lock:
            conn = self._get_connection()
            try:
                smd_rows = conn.execute("SELECT * FROM smd_marking_catalog ORDER BY code ASC;").fetchall()
                ic_rows = conn.execute("SELECT * FROM ic_package_thermal_catalog ORDER BY theta_ja_degc_w ASC;").fetchall()

                return {
                    "status": "SUCCESS",
                    "smd_markings": [dict(r) for r in smd_rows],
                    "ic_packages": [dict(r) for r in ic_rows],
                    "color_digits": COLOR_DIGITS,
                    "color_multipliers": COLOR_MULTIPLIERS,
                    "color_tolerances": COLOR_TOLERANCES,
                    "color_tcr": COLOR_TCR
                }
            finally:
                conn.close()


# Singleton engine instance
component_inspector_engine = ComponentInspectorEngine()
