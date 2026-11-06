"""
========================================================================================
VoltCore Apex Academia - Phase H: Practical Laboratory Learning (Features 281–290)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Features:
  - Feature 281: Virtual Breadboard Learning Interface & Netlist Continuity Validator
  - Feature 282: Component Identification Trainer (BJT, Regulator, IC Notch, Diode/LED)
  - Feature 283: Resistor Colour Code Calculator (4-Band, 5-Band, 6-Band & PPM/K)
  - Feature 284: Electronic Component Selection Guide (Wattage, Voltage Derating, PIV)
  - Feature 285: Circuit Troubleshooting Decision Tree (Power, Ground, Open, Short)
  - Feature 286: Laboratory Safety Checklist & High-Voltage/ESD Protection Protocols
  - Feature 287: Practical Experiment Preparation Guide (Anna University Reg 2023 ECE Labs)
  - Feature 288: Experiment Observation Notebook (Tabular Input/Output, Error % Math)
  - Feature 289: Virtual Instrument Reading Practice (Oscilloscope V/div, Time/div, DMM)
  - Feature 290: Laboratory Report Generator (Standard IEEE/Anna University Lab Record)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
========================================================================================
"""

import os
import math
import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")

# Resistor Color Code Definitions (Feature 283)
RESISTOR_COLORS: Dict[str, Dict[str, Any]] = {
    "BLACK":  {"digit": 0, "multiplier": 1e0,  "tolerance": None, "temp_coeff": None},
    "BROWN":  {"digit": 1, "multiplier": 1e1,  "tolerance": 1.0,  "temp_coeff": 100},
    "RED":    {"digit": 2, "multiplier": 1e2,  "tolerance": 2.0,  "temp_coeff": 50},
    "ORANGE": {"digit": 3, "multiplier": 1e3,  "tolerance": 0.05, "temp_coeff": 15},
    "YELLOW": {"digit": 4, "multiplier": 1e4,  "tolerance": 0.02, "temp_coeff": 25},
    "GREEN":  {"digit": 5, "multiplier": 1e5,  "tolerance": 0.5,  "temp_coeff": 20},
    "BLUE":   {"digit": 6, "multiplier": 1e6,  "tolerance": 0.25, "temp_coeff": 10},
    "VIOLET": {"digit": 7, "multiplier": 1e7,  "tolerance": 0.1,  "temp_coeff": 5},
    "GREY":   {"digit": 8, "multiplier": 1e8,  "tolerance": 0.01, "temp_coeff": 1},
    "WHITE":  {"digit": 9, "multiplier": 1e9,  "tolerance": None, "temp_coeff": None},
    "GOLD":   {"digit": None, "multiplier": 0.1,  "tolerance": 5.0,  "temp_coeff": None},
    "SILVER": {"digit": None, "multiplier": 0.01, "tolerance": 10.0, "temp_coeff": None}
}

# Component Pinout Catalog (Feature 282)
COMPONENT_PINOUT_CATALOG: Dict[str, Dict[str, Any]] = {
    "BC547": {
        "type": "NPN Bipolar Junction Transistor",
        "package": "TO-92",
        "view": "Flat face facing front, leads pointing down",
        "pins": {1: "Collector (C)", 2: "Base (B)", 3: "Emitter (E)"},
        "max_ratings": {"Vceo": "45V", "Ic_max": "100mA", "P_tot": "500mW"},
        "tamil_desc": "BC547 NPN டிரான்சிஸ்டர்: சமதளப் பகுதி முன்பக்கம் இருக்கும்போது இடமிருந்து வலம்: 1-C, 2-B, 3-E."
    },
    "2N3904": {
        "type": "NPN General Purpose BJT",
        "package": "TO-92",
        "view": "Flat face facing front, leads pointing down",
        "pins": {1: "Emitter (E)", 2: "Base (B)", 3: "Collector (C)"},
        "max_ratings": {"Vceo": "40V", "Ic_max": "200mA", "P_tot": "625mW"},
        "tamil_desc": "2N3904 NPN டிரான்சிஸ்டர்: சமதளப் பகுதி முன்பக்கம் இருக்கும்போது: 1-E, 2-B, 3-C."
    },
    "LM7805": {
        "type": "Positive +5V Linear Voltage Regulator",
        "package": "TO-220",
        "view": "Metal tab facing back, leads pointing down",
        "pins": {1: "Input (Vin: 7V–25V)", 2: "Ground (GND)", 3: "Output (+5V Regulated)"},
        "max_ratings": {"Iout_max": "1.5A", "Dropout_V": "2.0V"},
        "tamil_desc": "LM7805 வோல்டேஜ் ரெகுலேட்டர்: 1-Vin, 2-GND, 3-Vout (+5V)."
    },
    "LM741": {
        "type": "General Purpose Operational Amplifier",
        "package": "DIP-8",
        "view": "Top view, notch/dot pointing up-left",
        "pins": {
            1: "Offset Null", 2: "Inverting Input (Inv)", 3: "Non-Inverting Input (Non-Inv)",
            4: "Negative Supply (-Vcc)", 5: "Offset Null", 6: "Output (Vout)",
            7: "Positive Supply (+Vcc)", 8: "No Connection (NC)"
        },
        "max_ratings": {"Supply_V": "±18V", "GBP": "1.0MHz"},
        "tamil_desc": "LM741 ஆப்-ஆம்ப்: பின் 2 இன்வர்டிங், பின் 3 நான்-இன்வர்டிங், பின் 6 வெளியீடு, பின்கள் 7 மற்றும் 4 சப்ளை."
    },
    "NE555": {
        "type": "Precision Timer IC",
        "package": "DIP-8",
        "view": "Top view, notch/dot pointing up-left",
        "pins": {
            1: "GND", 2: "Trigger (Trig)", 3: "Output (Out)", 4: "Reset (Active Low)",
            5: "Control Voltage (Ctrl)", 6: "Threshold (Thresh)", 7: "Discharge (Disch)", 8: "Supply (Vcc)"
        },
        "max_ratings": {"Supply_V": "4.5V–16V", "Max_Freq": "500kHz"},
        "tamil_desc": "NE555 டைமர் IC: பின் 1 கிரவுண்ட், பின் 2 ட்ரிகர், பின் 3 அவுட்புட், பின் 8 Vcc."
    }
}

# Anna University Regulation 2023 ECE Lab Experiments Catalog (Feature 287)
ANNA_UNIV_ECE_LABS: Dict[str, Dict[str, Any]] = {
    "EC3361": {
        "title": "Electronic Devices & Circuits Laboratory (Semester 3)",
        "department": "Electronics & Communication Engineering",
        "regulation": "Regulation 2023",
        "experiments": [
            {"id": "EXP01", "name": "PN Junction Diode & Zener Diode Characteristics", "apparatus": "Diode 1N4007, Zener 5.1V, RPS, DMM"},
            {"id": "EXP02", "name": "BJT Common Emitter (CE) Input & Output Characteristics", "apparatus": "BC547 BJT, Dual RPS, Breadboard, Resistors"},
            {"id": "EXP03", "name": "JFET Drain & Transfer Characteristics", "apparatus": "BFW10/11 JFET, Dual RPS, Multimeter"},
            {"id": "EXP04", "name": "RC Phase Shift Oscillator & Hartley Oscillator", "apparatus": "BJT/Op-Amp, Decade Capacitance/Inductance Box, DSO"},
            {"id": "EXP05", "name": "Half-Wave & Full-Wave Rectifiers with Capacitor Filter", "apparatus": "Step-down Transformer 12-0-12, Diodes, 100uF Cap, DSO"}
        ]
    },
    "EC3461": {
        "title": "Digital Electronics & System Design Laboratory (Semester 4)",
        "department": "Electronics & Communication Engineering",
        "regulation": "Regulation 2023",
        "experiments": [
            {"id": "EXP06", "name": "Design of Adders, Subtractors & Code Converters", "apparatus": "7408, 7432, 7486, 7404 ICs, Digital Trainer Kit"},
            {"id": "EXP07", "name": "Design of Multiplexers, De-multiplexers & Decoders", "apparatus": "74151 MUX, 74138 Decoder, Trainer Kit"},
            {"id": "EXP08", "name": "Design of Synchronous & Asynchronous Up/Down Counters", "apparatus": "7476 JK Flip-Flop, 7474 D Flip-Flop, Logic Pulser"},
            {"id": "EXP09", "name": "Shift Registers & Ring/Johnson Counters", "apparatus": "7495 / 74194 Shift Register ICs"}
        ]
    },
    "EC3561": {
        "title": "Communication Systems Laboratory (Semester 5)",
        "department": "Electronics & Communication Engineering",
        "regulation": "Regulation 2023",
        "experiments": [
            {"id": "EXP10", "name": "Amplitude Modulation (AM) & Demodulation", "apparatus": "Carrier Gen, AF Gen, AM Kit, Digital Storage Oscilloscope"},
            {"id": "EXP11", "name": "Frequency Modulation (FM) & Demodulation", "apparatus": "FM Kit, Spectrum Analyzer, DSO"},
            {"id": "EXP12", "name": "Pulse Code Modulation (PCM) & Time-Division Multiplexing (TDM)", "apparatus": "PCM Trainer Kit, Storage Scope"}
        ]
    }
}


class PracticalLaboratoryEngine:
    """
    Backend computational & pedagogical engine for Phase H (Features 281–290):
    - Virtual breadboard terminal strip continuity checker
    - Electronic component identification & pinout verification
    - Resistor color code decoding (4, 5, and 6-band) & tolerance window
    - Component power/voltage rating selection with safety derating
    - Circuit troubleshooting diagnostic expert tree
    - Laboratory safety protocols & hazard check evaluation
    - Anna University ECE Regulation 2023 experiment preparation guides
    - Tabular observation recording and percentage error calculator
    - Virtual oscilloscope graticule & DMM reading simulator
    - IEEE / Anna University structured lab report generator
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
                # 1. Lab Observations Ledger
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS lab_observations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        experiment_code TEXT NOT NULL,
                        experiment_title TEXT NOT NULL,
                        input_parameters TEXT NOT NULL,
                        measured_values TEXT NOT NULL,
                        theoretical_values TEXT NOT NULL,
                        error_percent REAL NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)

                # 2. Lab Troubleshooting Logs
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS lab_troubleshooting_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        circuit_name TEXT NOT NULL,
                        symptoms TEXT NOT NULL,
                        diagnosed_cause TEXT NOT NULL,
                        resolved INTEGER NOT NULL DEFAULT 1,
                        created_at TEXT NOT NULL
                    );
                """)

                # 3. Lab Reports Ledger
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS lab_reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        experiment_code TEXT NOT NULL,
                        report_markdown TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)

                # Seed initial demo observation if empty
                cur = conn.execute("SELECT id FROM lab_observations LIMIT 1")
                if not cur.fetchone():
                    now = datetime.now(timezone.utc).isoformat()
                    demo_obs = (
                        "2023MITEC042",
                        "EC3361-EXP01",
                        "PN Junction Diode Forward Bias Characteristics",
                        json.dumps({"V_supply": 2.0, "R_limit": 330.0}),
                        json.dumps({"V_diode": 0.68, "I_diode_mA": 4.0}),
                        json.dumps({"V_diode_theory": 0.70, "I_diode_mA_theory": 3.94}),
                        2.86,
                        now
                    )
                    conn.execute("""
                        INSERT INTO lab_observations (
                            student_id, experiment_code, experiment_title, input_parameters,
                            measured_values, theoretical_values, error_percent, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, demo_obs)

                    conn.execute("""
                        INSERT INTO lab_troubleshooting_logs (
                            student_id, circuit_name, symptoms, diagnosed_cause, resolved, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, ("2023MITEC042", "CE BJT Amplifier", "Output clipped on negative cycle", "Operating point Q too close to saturation; adjust R1/R2 bias", 1, now))

                conn.commit()
            finally:
                conn.close()

    # =========================================================================
    # Feature 281: Virtual Breadboard Connection Analyzer
    # =========================================================================
    def validate_breadboard_connection(self, pin1: str, pin2: str) -> Dict[str, Any]:
        """
        Validates electrical continuity between two breadboard holes.
        Hole notation:
          Power rails: 'TOP_RED', 'TOP_BLUE', 'BOT_RED', 'BOT_BLUE'
          Tie strips: e.g. 'A1' through 'E63' (Top bank), 'F1' through 'J63' (Bottom bank)
        """
        p1 = pin1.upper().strip()
        p2 = pin2.upper().strip()

        # Check power rail continuity
        power_rails = ["TOP_RED", "TOP_BLUE", "BOT_RED", "BOT_BLUE"]
        if p1 in power_rails or p2 in power_rails:
            is_connected = (p1 == p2)
            desc = "Same power bus rail: full horizontal continuity" if is_connected else "Separate power rails: isolated"
            return {"pin1": p1, "pin2": p2, "is_connected": is_connected, "description": desc}

        # Terminal tie strips parsing (e.g. 'C12', 'F12')
        try:
            row1, col1 = p1[0], int(p1[1:])
            row2, col2 = p2[0], int(p2[1:])
        except Exception:
            return {"pin1": p1, "pin2": p2, "is_connected": False, "description": "Invalid breadboard coordinate format."}

        # Central trough separation: Rows A-E are connected vertically, Rows F-J are connected vertically
        bank1 = "TOP" if row1 in "ABCDE" else "BOTTOM"
        bank2 = "TOP" if row2 in "ABCDE" else "BOTTOM"

        if col1 == col2 and bank1 == bank2:
            return {
                "pin1": p1,
                "pin2": p2,
                "is_connected": True,
                "description": f"Connected vertically in 5-hole tie strip on Column {col1} (Bank {bank1})."
            }
        elif col1 == col2 and bank1 != bank2:
            return {
                "pin1": p1,
                "pin2": p2,
                "is_connected": False,
                "description": f"Separated by the central IC trough (DIP chip isolation) on Column {col1}."
            }
        else:
            return {
                "pin1": p1,
                "pin2": p2,
                "is_connected": False,
                "description": f"Different columns ({col1} vs {col2}): isolated without jumper wire."
            }

    # =========================================================================
    # Feature 282: Component Identification Trainer
    # =========================================================================
    def get_component_pinout(self, component_name: str) -> Dict[str, Any]:
        """Returns physical packaging, pin assignments, and electrical limits."""
        key = component_name.upper()
        if key not in COMPONENT_PINOUT_CATALOG:
            valid_keys = list(COMPONENT_PINOUT_CATALOG.keys())
            raise ValueError(f"Unknown component '{component_name}'. Available components: {valid_keys}")
        return COMPONENT_PINOUT_CATALOG[key]

    def verify_pin_identification(self, component_name: str, pin_number: int, user_guess: str) -> Dict[str, Any]:
        """Pedagogical quiz helper to verify student pin identification."""
        spec = self.get_component_pinout(component_name)
        pins = spec["pins"]
        actual_terminal = pins.get(pin_number, "Unknown")
        is_correct = user_guess.lower() in actual_terminal.lower()
        return {
            "component": component_name,
            "pin_number": pin_number,
            "user_guess": user_guess,
            "actual_terminal": actual_terminal,
            "is_correct": is_correct
        }

    # =========================================================================
    # Feature 283: Resistor Colour Code Calculator
    # =========================================================================
    def calculate_resistor_value(self, bands: List[str]) -> Dict[str, Any]:
        """
        Decodes 4-Band, 5-Band, or 6-Band resistor color codes.
        Bands format: list of color strings e.g. ['BROWN', 'BLACK', 'RED', 'GOLD']
        """
        num_bands = len(bands)
        if num_bands not in (4, 5, 6):
            raise ValueError("Resistor color code must have 4, 5, or 6 bands.")

        colors = [b.upper().strip() for b in bands]
        for c in colors:
            if c not in RESISTOR_COLORS:
                raise ValueError(f"Invalid color band '{c}'.")

        if num_bands == 4:
            d1 = RESISTOR_COLORS[colors[0]]["digit"]
            d2 = RESISTOR_COLORS[colors[1]]["digit"]
            mult = RESISTOR_COLORS[colors[2]]["multiplier"]
            tol = RESISTOR_COLORS[colors[3]]["tolerance"] or 20.0
            temp_coeff = None
            if d1 is None or d2 is None:
                raise ValueError("Bands 1 and 2 must be significant digits.")
            nominal = (d1 * 10 + d2) * mult

        elif num_bands == 5:
            d1 = RESISTOR_COLORS[colors[0]]["digit"]
            d2 = RESISTOR_COLORS[colors[1]]["digit"]
            d3 = RESISTOR_COLORS[colors[2]]["digit"]
            mult = RESISTOR_COLORS[colors[3]]["multiplier"]
            tol = RESISTOR_COLORS[colors[4]]["tolerance"] or 5.0
            temp_coeff = None
            if d1 is None or d2 is None or d3 is None:
                raise ValueError("Bands 1, 2, and 3 must be significant digits.")
            nominal = (d1 * 100 + d2 * 10 + d3) * mult

        else:  # 6-Band
            d1 = RESISTOR_COLORS[colors[0]]["digit"]
            d2 = RESISTOR_COLORS[colors[1]]["digit"]
            d3 = RESISTOR_COLORS[colors[2]]["digit"]
            mult = RESISTOR_COLORS[colors[3]]["multiplier"]
            tol = RESISTOR_COLORS[colors[4]]["tolerance"] or 1.0
            temp_coeff = RESISTOR_COLORS[colors[5]]["temp_coeff"] or 100
            nominal = (d1 * 100 + d2 * 10 + d3) * mult

        min_val = nominal * (1.0 - (tol / 100.0))
        max_val = nominal * (1.0 + (tol / 100.0))

        # Pretty formatting
        if nominal >= 1e6:
            formatted = f"{nominal / 1e6:.2f} MΩ".replace(".00", "")
        elif nominal >= 1e3:
            formatted = f"{nominal / 1e3:.2f} kΩ".replace(".00", "")
        else:
            formatted = f"{nominal:.2f} Ω".replace(".00", "")

        return {
            "num_bands": num_bands,
            "colors": colors,
            "nominal_resistance_ohms": round(nominal, 2),
            "formatted_resistance": formatted,
            "tolerance_percent": tol,
            "temp_coeff_ppm_k": temp_coeff,
            "min_resistance_ohms": round(min_val, 2),
            "max_resistance_ohms": round(max_val, 2)
        }

    # =========================================================================
    # Feature 284: Electronic Component Selection Guide & Derating
    # =========================================================================
    def select_component_rating(
        self,
        component_type: str,
        operating_voltage_v: float,
        operating_current_a: float,
        safety_derating_factor: float = 2.0
    ) -> Dict[str, Any]:
        """
        Calculates safe electrical ratings with industrial derating standards.
        Resistor: P = V * I. Recommended power = P * derating (e.g. 2x).
        Capacitor: Recommended V_rating = V_op * 1.5.
        Diode: Recommended PIV = V_op * 2.0.
        """
        c_type = component_type.upper()
        p_dissipated = operating_voltage_v * operating_current_a

        standard_wattages = [0.125, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 25.0]
        recommended_wattage = None
        target_p = p_dissipated * safety_derating_factor

        for w in standard_wattages:
            if w >= target_p:
                recommended_wattage = w
                break
        if not recommended_wattage:
            recommended_wattage = standard_wattages[-1]

        rec_voltage = operating_voltage_v * 1.5
        rec_piv = operating_voltage_v * 2.0

        return {
            "component_type": c_type,
            "operating_voltage_v": operating_voltage_v,
            "operating_current_a": operating_current_a,
            "power_dissipated_w": round(p_dissipated, 4),
            "recommended_resistor_wattage_w": recommended_wattage,
            "recommended_capacitor_voltage_v": math.ceil(rec_voltage),
            "recommended_diode_piv_v": math.ceil(rec_piv),
            "derating_factor_used": safety_derating_factor
        }

    # =========================================================================
    # Feature 285: Circuit Troubleshooting Decision Tree
    # =========================================================================
    def diagnose_circuit_fault(self, symptoms: List[str]) -> Dict[str, Any]:
        """
        Expert troubleshooting tree analyzing common undergraduate breadboard failure modes.
        """
        symp_lower = [s.lower() for s in symptoms]
        causes = []
        action_steps = []

        if any("overheating" in s or "hot" in s or "burning" in s for s in symp_lower):
            causes.append("IC inverted or Reverse Polarity on VCC/GND pins.")
            action_steps.append("Power off immediately! Verify Pin 1 orientation against notch and check ground wiring.")

        if any("no power" in s or "0v" in s or "dead" in s for s in symp_lower):
            causes.append("Power supply current limit tripped or blown protective diode/fuse.")
            action_steps.append("Measure supply voltage with DMM across red/blue breadboard rails; check for short to GND.")

        if any("clipping" in s or "distorted" in s for s in symp_lower):
            causes.append("Incorrect Q-point bias in amplifier or excessive input signal amplitude.")
            action_steps.append("Check DC quiescent collector voltage V_C ~ V_CC / 2; decrease input generator amplitude.")

        if any("oscillation" in s or "hum" in s or "noise" in s for s in symp_lower):
            causes.append("Missing decoupling bypass capacitor on power rails or long stray inductive leads.")
            action_steps.append("Place 100nF ceramic capacitor directly across IC Vcc and GND pins close to the package.")

        if not causes:
            causes.append("Possible cold solder joint or loose breadboard spring clip.")
            action_steps.append("Probe continuity along the signal path using DMM beeper mode.")

        is_high_priority = any("overheating" in s or "hot" in s or "burning" in s for s in symp_lower)

        return {
            "input_symptoms": symptoms,
            "diagnosed_root_causes": causes,
            "recommended_action_steps": action_steps,
            "priority": "HIGH" if is_high_priority else "NORMAL"
        }

    # =========================================================================
    # Feature 286: Laboratory Safety Protocols
    # =========================================================================
    def evaluate_safety_checklist(self, responses: Dict[str, bool]) -> Dict[str, Any]:
        """Evaluates lab safety readiness before powering up circuits."""
        checklist_items = {
            "power_off_while_wiring": "Did you keep DC power supply turned OFF during breadboard circuit assembly?",
            "polarity_verified": "Have you verified the polarity of electrolytic capacitors and diodes?",
            "esd_strap_worn": "Are you wearing an ESD grounding wrist strap when handling CMOS ICs?",
            "current_limit_set": "Is the DC power supply current limit knob set to safe lab value (<= 250mA)?",
            "eyewear_worn": "Are protective safety glasses worn during soldering or capacitor stress tests?"
        }

        passed_count = sum(1 for k in checklist_items if responses.get(k, False))
        total_count = len(checklist_items)
        is_safe = (passed_count == total_count)

        return {
            "is_safe_to_energize": is_safe,
            "score": f"{passed_count} / {total_count}",
            "passed_percentage": round((passed_count / total_count) * 100.0, 1),
            "safety_verdict": "APPROVED FOR POWER-UP" if is_safe else "ACTION REQUIRED: Unmet safety prerequisites"
        }

    # =========================================================================
    # Feature 287: Practical Experiment Preparation Guide
    # =========================================================================
    def get_experiment_guide(self, lab_code: str) -> Dict[str, Any]:
        """Retrieves Anna University syllabus, apparatus, and model experiments."""
        code = lab_code.upper().strip()
        if code not in ANNA_UNIV_ECE_LABS:
            valid_labs = list(ANNA_UNIV_ECE_LABS.keys())
            raise ValueError(f"Unknown lab code '{lab_code}'. Available ECE labs: {valid_labs}")
        return ANNA_UNIV_ECE_LABS[code]

    # =========================================================================
    # Feature 288: Experiment Observation Notebook & Error Calculator
    # =========================================================================
    def calculate_observation_error(
        self,
        measured_val: float,
        theoretical_val: float
    ) -> Dict[str, Any]:
        """Calculates percentage error between measured reading and theoretical calculation."""
        if theoretical_val == 0.0:
            err_percent = 0.0 if measured_val == 0.0 else 100.0
        else:
            err_percent = abs(measured_val - theoretical_val) / abs(theoretical_val) * 100.0

        is_acceptable = err_percent <= 10.0  # Standard undergraduate ECE 10% lab margin

        return {
            "measured_value": measured_val,
            "theoretical_value": theoretical_val,
            "absolute_error": round(abs(measured_val - theoretical_val), 4),
            "error_percent": round(err_percent, 2),
            "is_acceptable": is_acceptable
        }

    # =========================================================================
    # Feature 289: Virtual Instrument Reading Practice
    # =========================================================================
    def calculate_scope_measurements(
        self,
        div_y: float,
        volts_per_div: float,
        div_x: float,
        time_per_div_ms: float,
        probe_attenuation: int = 1
    ) -> Dict[str, Any]:
        """
        Calculates waveform amplitude, peak-to-peak voltage, RMS, period, and frequency from graticule divisions.
        V_pp = div_y * volts_per_div * probe_attenuation
        Period = div_x * time_per_div_ms
        Freq = 1 / Period
        """
        if volts_per_div <= 0 or time_per_div_ms <= 0:
            raise ValueError("Volts/div and Time/div must be positive.")

        v_pp = div_y * volts_per_div * probe_attenuation
        v_amplitude = v_pp / 2.0
        v_rms = v_amplitude / math.sqrt(2.0)  # For pure sine wave

        period_sec = (div_x * time_per_div_ms) / 1000.0
        frequency_hz = (1.0 / period_sec) if period_sec > 0 else 0.0

        return {
            "div_y": div_y,
            "volts_per_div": volts_per_div,
            "probe_attenuation": f"{probe_attenuation}X",
            "v_pp_volts": round(v_pp, 3),
            "v_amplitude_volts": round(v_amplitude, 3),
            "v_rms_volts": round(v_rms, 3),
            "period_ms": round(period_sec * 1000.0, 3),
            "frequency_hz": round(frequency_hz, 1)
        }

    # =========================================================================
    # Feature 290: Laboratory Report Generator (Anna University / IEEE Format)
    # =========================================================================
    def generate_laboratory_report(
        self,
        student_id: str,
        student_name: str,
        roll_no: str,
        exp_code: str,
        exp_title: str,
        aim: str,
        apparatus: List[str],
        formulae_md: str,
        results_summary: str
    ) -> str:
        """Generates standard markdown lab record report formatted to Anna University guidelines."""
        date_str = datetime.now(timezone.utc).strftime("%d-%m-%Y")
        apparatus_str = "\n".join([f"- {a}" for a in apparatus])

        report_md = f"""# ANNA UNIVERSITY / MIT CAMPUS — LABORATORY RECORD
**Department of Electronics Engineering** | Regulation 2023  
**Course Code / Lab:** {exp_code} | **Date:** {date_str}  
**Student Name:** {student_name} | **Roll No:** {roll_no} | **Student ID:** {student_id}  

---

## EXPERIMENT TITLE: {exp_title}

### 1. AIM
{aim}

### 2. APPARATUS REQUIRED
{apparatus_str}

### 3. FORMULAE & EQUATIONS
{formulae_md}

### 4. CIRCUIT DIAGRAM
```
           +Vcc (12V)
               │
              [RC]
               │─────── Output Vout
         [RB]  │
    Vin ──┤├───┴──┐
         (Cin)    │
                 [Q1] BC547 BJT
                  │
                 [RE]
                  │
                 GND
```

### 5. OBSERVATIONS & RESULT
{results_summary}

### 6. INFERENCE & CONCLUSION
The experiment was conducted successfully. Measured circuit parameters correlate closely with theoretical models with error within standard laboratory limits (< 10%).

---
*Verified by Laboratory In-Charge / Course Faculty — MIT Campus, Anna University*
"""
        return report_md

    # =========================================================================
    # Persistence Methods (SQLite WAL)
    # =========================================================================
    def save_observation(
        self,
        student_id: str,
        exp_code: str,
        exp_title: str,
        input_params: Dict[str, Any],
        measured: Dict[str, Any],
        theoretical: Dict[str, Any],
        error_percent: float
    ) -> int:
        """Saves an observation entry to SQLite WAL."""
        with self._lock:
            conn = self._get_connection()
            try:
                now = datetime.now(timezone.utc).isoformat()
                cur = conn.execute("""
                    INSERT INTO lab_observations (
                        student_id, experiment_code, experiment_title, input_parameters,
                        measured_values, theoretical_values, error_percent, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    student_id, exp_code, exp_title,
                    json.dumps(input_params), json.dumps(measured), json.dumps(theoretical),
                    error_percent, now
                ))
                conn.commit()
                return cur.lastrowid
            finally:
                conn.close()

    def get_observations(self, student_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves observation history for student."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.execute("""
                    SELECT id, student_id, experiment_code, experiment_title,
                           input_parameters, measured_values, theoretical_values, error_percent, created_at
                    FROM lab_observations
                    WHERE student_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                """, (student_id, limit))
                rows = cur.fetchall()
                results = []
                for r in rows:
                    results.append({
                        "id": r["id"],
                        "student_id": r["student_id"],
                        "experiment_code": r["experiment_code"],
                        "exp_code": r["experiment_code"],
                        "experiment_title": r["experiment_title"],
                        "input_parameters": json.loads(r["input_parameters"]),
                        "measured_values": json.loads(r["measured_values"]),
                        "theoretical_values": json.loads(r["theoretical_values"]),
                        "error_percent": r["error_percent"],
                        "created_at": r["created_at"]
                    })
                return results
            finally:
                conn.close()

    def save_report(
        self,
        student_id: str,
        exp_code: str,
        report_markdown: str,
        status: str = "SUBMITTED"
    ) -> int:
        """Saves generated laboratory report to SQLite WAL."""
        with self._lock:
            conn = self._get_connection()
            try:
                now = datetime.now(timezone.utc).isoformat()
                cur = conn.execute("""
                    INSERT INTO lab_reports (
                        student_id, experiment_code, report_markdown, status, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, (student_id, exp_code, report_markdown, status, now))
                conn.commit()
                return cur.lastrowid
            finally:
                conn.close()
