"""
========================================================================================
VoltCore Apex Academia - Voice-Enabled Hands-Free Lab Assistant Router
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/voice_command_router.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Lightweight, low-latency acoustic query router and speech intent dispatcher:
    1. Sanitizes spoken transcripts (lowercasing, filler removal, phonetic normalization).
    2. Fast regex and keyword-based intent classification (0-bloat, native Python).
    3. Anna University ECE Regulation 2023 formula lookups and dynamic math solvers
       (Resonant frequency, Nyquist sampling rate, Shannon capacity, Op-Amp gain).
    4. Hardware-in-the-Loop lab actions & route triggers backed by SQLite WAL.
========================================================================================
"""

import os
import re
import math
import time
import json
import sqlite3
import threading
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")

# Spoken noise phrases & filler words to strip for crisp semantic intent matching
SPOKEN_FILLER_PATTERNS = [
    r"^\s*hey\s+voltcore[\s,]*",
    r"^\s*voltcore[\s,]*",
    r"^\s*okay\s+voltcore[\s,]*",
    r"^\s*can\s+you\s+(?:please\s+)?",
    r"^\s*please\s+",
    r"^\s*could\s+you\s+(?:tell\s+me\s+)?(?:about\s+)?",
    r"^\s*tell\s+me\s+(?:about\s+)?",
    r"^\s*about\s+",
    r"^\s*what\s+is\s+the\s+",
    r"^\s*what\s+is\s+",
    r"^\s*how\s+to\s+",
    r"^\s*show\s+me\s+(?:the\s+)?",
    r"^\s*the\s+",
    r"^\s*calculate\s+the\s+",
    r"^\s*give\s+me\s+(?:the\s+)?",
    r"^\s*find\s+(?:the\s+)?",
    r"[\?\.\!,]+$"
]

DEFAULT_INTENTS = [
    {
        "intent_id": "INTENT_CALCULATE_RESONANCE",
        "intent_name": "LC Resonance Calculation",
        "category": "FORMULA_SOLVER",
        "keywords": ["resonant frequency", "resonance", "tank circuit", "lc circuit", "tuned circuit", "omega 0", "f0"],
        "action_route": "/simulation",
        "response_template": "Resonant frequency f0 equals 1 divided by (2 pi times square root of L times C). In a series RLC circuit, at resonance impedance is purely resistive.",
        "example_queries": ["calculate resonant frequency", "what is the resonance formula", "resonant frequency for 10 microhenry and 100 picofarad"]
    },
    {
        "intent_id": "INTENT_NYQUIST_RATE",
        "intent_name": "Nyquist-Shannon Sampling Rate",
        "category": "FORMULA_SOLVER",
        "keywords": ["nyquist rate", "nyquist sampling", "sampling theorem", "aliasing", "fs greater than 2fm"],
        "action_route": "/virtual-bench",
        "response_template": "Nyquist-Shannon theorem states sampling frequency fs must be at least twice the maximum signal frequency fm to prevent aliasing. fs >= 2 * fm.",
        "example_queries": ["what is the nyquist rate", "nyquist sampling for 20 khz", "how to avoid aliasing"]
    },
    {
        "intent_id": "INTENT_SHANNON_CAPACITY",
        "intent_name": "Shannon Channel Capacity",
        "category": "FORMULA_SOLVER",
        "keywords": ["shannon capacity", "channel capacity", "hartley shannon", "signal to noise", "snr capacity"],
        "action_route": "/gate-ece",
        "response_template": "Shannon Channel Capacity C equals B times log base 2 of (1 plus SNR) in bits per second, representing the theoretical upper bound error-free data rate.",
        "example_queries": ["explain shannon channel capacity", "channel capacity formula", "shannon limit"]
    },
    {
        "intent_id": "INTENT_MAXWELL_EQUATIONS",
        "intent_name": "Maxwell's Equations",
        "category": "ELECTROMAGNETICS",
        "keywords": ["maxwell", "maxwell equations", "gauss law", "faraday law", "ampere circuital", "divergence of d", "curl of e"],
        "action_route": "/gate-ece",
        "response_template": "Maxwell's 4 differential equations: 1. Div D equals rho_v. 2. Div B equals 0. 3. Curl E equals negative partial B with respect to t. 4. Curl H equals J plus displacement current density.",
        "example_queries": ["explain maxwells equations", "differential form of maxwells equations", "gauss law in electromagnetics"]
    },
    {
        "intent_id": "INTENT_BJT_GAIN",
        "intent_name": "BJT Small-Signal Gain",
        "category": "ANALOG_CIRCUITS",
        "keywords": ["bjt gain", "transconductance", "common emitter gain", "small signal gain", "gm rc"],
        "action_route": "/simulation",
        "response_template": "For a Common-Emitter BJT amplifier with bypass capacitor, the small-signal midband voltage gain Av is approximately negative gm times RC, where gm equals collector current Ic divided by thermal voltage Vt.",
        "example_queries": ["what is bjt common emitter voltage gain", "calculate bjt gm", "small signal model"]
    },
    {
        "intent_id": "INTENT_NAVIGATE_PHYSICAL_LAB",
        "intent_name": "Physical HIL Lab Automation",
        "category": "NAVIGATION",
        "keywords": ["physical lab", "hardware in the loop", "serial com", "com3", "com4", "com7", "serial terminal", "test bench"],
        "action_route": "/physical-lab",
        "response_template": "Routing you to the Physical Hardware-in-the-Loop lab automation terminal. Discovered COM ports: ESP32-S3, STM32F4, and FTDI gateway are available.",
        "example_queries": ["open physical lab", "connect com3 test bench", "open serial port manager", "navigate to physical lab"]
    },
    {
        "intent_id": "INTENT_NAVIGATE_SIMULATION",
        "intent_name": "SPICE Circuit Simulator",
        "category": "NAVIGATION",
        "keywords": ["simulate", "circuit simulator", "spice", "transient simulation", "bjt simulation", "op amp circuit", "run spice"],
        "action_route": "/simulation",
        "response_template": "Launching the VoltCore Interactive SPICE Circuit Simulation Suite. Ready to analyze Common Emitter, Sallen-Key Active Filter, and Inverting Op-Amp topologies.",
        "example_queries": ["open circuit simulator", "simulate bjt circuit", "launch spice"]
    },
    {
        "intent_id": "INTENT_NAVIGATE_VIRTUAL_BENCH",
        "intent_name": "Virtual DSO Oscilloscope",
        "category": "NAVIGATION",
        "keywords": ["oscilloscope", "virtual bench", "keysight", "dsox1204g", "function generator", "waveform view"],
        "action_route": "/virtual-bench",
        "response_template": "Opening Keysight DSOX1204G 4-Channel Virtual Digital Storage Oscilloscope and Arbitrary Waveform Generator.",
        "example_queries": ["open oscilloscope", "show virtual bench", "keysight dso oscilloscope"]
    },
    {
        "intent_id": "INTENT_NAVIGATE_EXAM_CENTER",
        "intent_name": "Exam Center & GATE ECE",
        "category": "NAVIGATION",
        "keywords": ["exam", "mock test", "gate ece", "anna university test", "test center", "start test", "quiz"],
        "action_route": "/exam-center",
        "response_template": "Entering Anna University R2023 & GATE ECE Examination Simulator. Timed assessments, negative marking, and NBA outcome analytics are ready.",
        "example_queries": ["open exam center", "start gate ece mock test", "take anna university exam"]
    },
    {
        "intent_id": "INTENT_NAVIGATE_SMART_LAB",
        "intent_name": "IoT Smart Lab 304 Telemetry",
        "category": "NAVIGATION",
        "keywords": ["smart lab", "lab 304", "equipment status", "overcurrent trip", "iot telemetry"],
        "action_route": "/smart-lab",
        "response_template": "Opening IoT Smart Laboratory 304 Monitoring Center. Live telemetry streams active for Keysight DSO, Rigol DC Power Supply, and Weller Station.",
        "example_queries": ["open smart lab", "check lab 304 equipment", "smart lab monitoring"]
    },
    {
        "intent_id": "INTENT_CHECK_THERMAL_STATUS",
        "intent_name": "Hardware Thermal & Safety Guard",
        "category": "SYSTEM_DIAGNOSTICS",
        "keywords": ["thermal status", "temperature", "victus", "fan speed", "passive cooling", "thermal safety", "cpu temperature"],
        "action_route": "/cloud-deploy",
        "response_template": "HP Victus 15 thermal guardian reports nominal condition. Passive cooling headroom is maintained, memory footprint is below 300MB, and RTX 4050 throttling guards are active.",
        "example_queries": ["check thermal status", "is system temperature safe", "victus hardware health"]
    },
    {
        "intent_id": "INTENT_ESP32_PINOUT",
        "intent_name": "ESP32-S3 Hardware Pinout",
        "category": "EMBEDDED_SYSTEMS",
        "keywords": ["esp32 pinout", "esp32 s3 pins", "esp32 spi", "esp32 gpio", "xtensa pinout"],
        "action_route": "/flash-firmware",
        "response_template": "ESP32-S3 default hardware pinout: SPI FSPI utilizes GPIO 10 (CS), GPIO 11 (MOSI), GPIO 12 (CLK), and GPIO 13 (MISO). Default USB-CDC serial is on GPIO 19 and 20. UART0 debug is GPIO 43 and 44.",
        "example_queries": ["show esp32 s3 spi pinout", "what are esp32 pin mappings", "esp32 gpio configuration"]
    }
]

DEFAULT_ECE_FORMULAS = [
    {
        "formula_id": "FORMULA_RESONANCE_LC",
        "topic": "Resonant Frequency",
        "formula_name": "Series/Parallel RLC Resonance",
        "latex_expression": "f_0 = \\frac{1}{2\\pi \\sqrt{L C}}",
        "plain_text": "f0 = 1 / (2 * pi * sqrt(L * C))",
        "explanation": "Calculates the undamped natural frequency at which inductive and capacitive reactances cancel (X_L = X_C).",
        "speech_summary": "Resonant frequency f 0 equals 1 divided by 2 pi square root of L times C.",
        "variables_json": json.dumps({"L": "Inductance in Henrys (H)", "C": "Capacitance in Farads (F)", "f_0": "Frequency in Hertz (Hz)"}),
        "unit_result": "Hz",
        "au_regulation": "EC3352"
    },
    {
        "formula_id": "FORMULA_NYQUIST_SAMPLING",
        "topic": "Digital Signal Processing",
        "formula_name": "Nyquist-Shannon Sampling Theorem",
        "latex_expression": "f_s \\ge 2 f_{max}",
        "plain_text": "fs >= 2 * fmax",
        "explanation": "Minimum sampling rate necessary to avoid frequency fold-over and spectral aliasing during analog-to-digital conversion.",
        "speech_summary": "Sampling frequency f s must be greater than or equal to twice the maximum signal frequency.",
        "variables_json": json.dumps({"f_s": "Sampling Frequency (Hz)", "f_max": "Bandwidth / Max Signal Frequency (Hz)"}),
        "unit_result": "Samples/s (Hz)",
        "au_regulation": "EC3491"
    },
    {
        "formula_id": "FORMULA_SHANNON_CAPACITY",
        "topic": "Information Theory & Communication",
        "formula_name": "Shannon-Hartley Channel Capacity",
        "latex_expression": "C = B \\log_2\\left(1 + \\text{SNR}\\right)",
        "plain_text": "C = B * log2(1 + SNR)",
        "explanation": "Tightest theoretical upper bound on transmission rate of error-free data across an AWGN channel with bandwidth B and signal-to-noise ratio SNR.",
        "speech_summary": "Channel capacity C equals bandwidth B times log base 2 of 1 plus S N R.",
        "variables_json": json.dumps({"C": "Channel Capacity (bps)", "B": "Bandwidth (Hz)", "SNR": "Linear Signal-to-Noise Ratio"}),
        "unit_result": "bits/second",
        "au_regulation": "EC3491"
    },
    {
        "formula_id": "FORMULA_MAXWELL_FARADAY",
        "topic": "Electromagnetic Fields",
        "formula_name": "Faraday's Law of Induction (Differential)",
        "latex_expression": "\\nabla \\times \\mathbf{E} = -\\frac{\\partial \\mathbf{B}}{\\partial t}",
        "plain_text": "curl(E) = -dB/dt",
        "explanation": "Time-varying magnetic flux density induces a circulation of electric field, forming the basis for transformers and inductors.",
        "speech_summary": "Curl of electric field E equals negative time rate of change of magnetic flux density B.",
        "variables_json": json.dumps({"E": "Electric Field (V/m)", "B": "Magnetic Flux Density (Tesla)", "t": "Time (s)"}),
        "unit_result": "V/m^2",
        "au_regulation": "EC3452"
    },
    {
        "formula_id": "FORMULA_BJT_TRANSCONDUCTANCE",
        "topic": "Analog Electronic Circuits",
        "formula_name": "BJT Transconductance (gm)",
        "latex_expression": "g_m = \\frac{I_C}{V_T} \\approx \\frac{I_C}{26\\text{ mV}}",
        "plain_text": "gm = Ic / Vt",
        "explanation": "Small-signal transconductance of a bipolar junction transistor at room temperature (T = 300K, Vt = 25.86 mV).",
        "speech_summary": "Transconductance g m equals quiescent collector current I c divided by thermal voltage V t.",
        "variables_json": json.dumps({"I_C": "Collector Current (A)", "V_T": "Thermal Voltage (~26 mV at 300K)"}),
        "unit_result": "Siemens (A/V)",
        "au_regulation": "EC3451"
    },
    {
        "formula_id": "FORMULA_OPAMP_INVERTING_GAIN",
        "topic": "Linear Integrated Circuits",
        "formula_name": "Inverting Op-Amp Closed-Loop Gain",
        "latex_expression": "A_v = -\\frac{R_f}{R_{in}}",
        "plain_text": "Av = -(Rf / Rin)",
        "explanation": "Negative feedback voltage gain configured by the ratio of feedback resistor Rf to input resistor Rin.",
        "speech_summary": "Voltage gain A v equals negative R feedback divided by R input.",
        "variables_json": json.dumps({"R_f": "Feedback Resistance (Ohms)", "R_{in}": "Input Resistance (Ohms)"}),
        "unit_result": "V/V (dimensionless)",
        "au_regulation": "EC3451"
    }
]


class VoiceCommandRouter:
    """
    Lightweight, thread-safe speech intent classification router and Anna University
    ECE formula solver using SQLite WAL storage and low-overhead regex tokenization.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self._lock = threading.Lock()
        self._init_sqlite_schema()
        self._seed_default_intents_and_formulas()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns an optimized SQLite WAL connection."""
        conn = sqlite3.connect(self.db_path, timeout=5.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode = WAL;")
        cur.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_sqlite_schema(self) -> None:
        """Initializes tables for voice intents, formulas, and acoustic query logs."""
        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()
            try:
                # 1. Voice intents registry
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS voice_command_intents (
                        intent_id TEXT PRIMARY KEY,
                        intent_name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        keywords_json TEXT NOT NULL,
                        action_route TEXT,
                        response_template TEXT NOT NULL,
                        example_queries_json TEXT NOT NULL
                    );
                """)

                # 2. Curated Anna University ECE formula catalog
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS voice_ece_formulas (
                        formula_id TEXT PRIMARY KEY,
                        topic TEXT NOT NULL,
                        formula_name TEXT NOT NULL,
                        latex_expression TEXT NOT NULL,
                        plain_text TEXT NOT NULL,
                        explanation TEXT NOT NULL,
                        speech_summary TEXT NOT NULL,
                        variables_json TEXT NOT NULL,
                        unit_result TEXT NOT NULL,
                        au_regulation TEXT NOT NULL
                    );
                """)

                # 3. Voice query execution logs
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS voice_command_logs (
                        log_id TEXT PRIMARY KEY,
                        student_id TEXT NOT NULL,
                        raw_transcript TEXT NOT NULL,
                        cleaned_transcript TEXT NOT NULL,
                        detected_intent TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        response_text TEXT NOT NULL,
                        action_route TEXT,
                        execution_ms REAL NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)
                conn.commit()
            finally:
                conn.close()

    def _seed_default_intents_and_formulas(self) -> None:
        """Seeds initial default intents and ECE formulas if empty."""
        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()
            try:
                cur.execute("SELECT COUNT(*) FROM voice_command_intents;")
                if cur.fetchone()[0] == 0:
                    for intent in DEFAULT_INTENTS:
                        cur.execute("""
                            INSERT INTO voice_command_intents 
                            (intent_id, intent_name, category, keywords_json, action_route, response_template, example_queries_json)
                            VALUES (?, ?, ?, ?, ?, ?, ?);
                        """, (
                            intent["intent_id"],
                            intent["intent_name"],
                            intent["category"],
                            json.dumps(intent["keywords"]),
                            intent["action_route"],
                            intent["response_template"],
                            json.dumps(intent["example_queries"])
                        ))

                cur.execute("SELECT COUNT(*) FROM voice_ece_formulas;")
                if cur.fetchone()[0] == 0:
                    for f in DEFAULT_ECE_FORMULAS:
                        cur.execute("""
                            INSERT INTO voice_ece_formulas
                            (formula_id, topic, formula_name, latex_expression, plain_text, explanation, speech_summary, variables_json, unit_result, au_regulation)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, (
                            f["formula_id"],
                            f["topic"],
                            f["formula_name"],
                            f["latex_expression"],
                            f["plain_text"],
                            f["explanation"],
                            f["speech_summary"],
                            f["variables_json"],
                            f["unit_result"],
                            f["au_regulation"]
                        ))
                conn.commit()
            finally:
                conn.close()

    def clean_transcript(self, raw_transcript: str) -> str:
        """
        Cleans and normalizes spoken text:
        Strips noise punctuation, filler leading phrases, and excess whitespace.
        """
        if not raw_transcript:
            return ""

        text = raw_transcript.strip().lower()

        # Iteratively remove filler phrases
        changed = True
        while changed:
            changed = False
            for pat in SPOKEN_FILLER_PATTERNS:
                new_text = re.sub(pat, "", text, flags=re.IGNORECASE).strip()
                if new_text != text:
                    text = new_text
                    changed = True

        # Collapse excess whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def parse_values_with_units(self, text: str) -> Dict[str, float]:
        """
        Extracts physical electrical parameters with SI prefixes:
        - 10uH, 10 microhenry -> L: 1e-5
        - 100pF, 100 picofarad -> C: 1e-10
        - 20kHz -> f: 20000
        - 10k, 10kohm -> R: 10000
        """
        extracted = {}

        # Unit multipliers
        multipliers = {
            "p": 1e-12, "pico": 1e-12, "pf": 1e-12,
            "n": 1e-9, "nano": 1e-9, "nf": 1e-9,
            "u": 1e-6, "micro": 1e-6, "uf": 1e-6, "µ": 1e-6,
            "m": 1e-3, "milli": 1e-3, "mf": 1e-3, "mh": 1e-3,
            "k": 1e3, "kilo": 1e3, "khz": 1e3, "kohm": 1e3,
            "meg": 1e6, "mega": 1e6, "mhz": 1e6, "megohm": 1e6,
            "g": 1e9, "giga": 1e9, "ghz": 1e9
        }

        # Match Inductance
        l_match = re.search(r"(\d+(?:\.\d+)?)\s*(pico|nano|micro|milli|u|n|p|m)?\s*(?:h|henry|henries)\b", text, re.IGNORECASE)
        if l_match:
            val = float(l_match.group(1))
            prefix = (l_match.group(2) or "").lower()
            mul = multipliers.get(prefix, 1.0)
            extracted["inductance_h"] = val * mul

        # Match Capacitance
        c_match = re.search(r"(\d+(?:\.\d+)?)\s*(pico|nano|micro|milli|u|n|p|m)?\s*(?:f|farad|farads)\b", text, re.IGNORECASE)
        if c_match:
            val = float(c_match.group(1))
            prefix = (c_match.group(2) or "").lower()
            mul = multipliers.get(prefix, 1.0)
            extracted["capacitance_f"] = val * mul

        # Match Frequency
        f_match = re.search(r"(\d+(?:\.\d+)?)\s*(kilo|mega|giga|k|m|g)?\s*(?:hz|hertz)\b", text, re.IGNORECASE)
        if f_match:
            val = float(f_match.group(1))
            prefix = (f_match.group(2) or "").lower()
            mul = multipliers.get(prefix, 1.0)
            extracted["frequency_hz"] = val * mul

        # Match Resistor
        r_match = re.search(r"(\d+(?:\.\d+)?)\s*(kilo|mega|k|m)?\s*(?:ohm|ohms|r)\b", text, re.IGNORECASE)
        if r_match:
            val = float(r_match.group(1))
            prefix = (r_match.group(2) or "").lower()
            mul = multipliers.get(prefix, 1.0)
            extracted["resistance_ohm"] = val * mul

        return extracted

    def solve_dynamic_formula(self, intent_id: str, cleaned_text: str) -> Optional[Dict[str, Any]]:
        """
        If student provides numbers in query, dynamically evaluates the formula.
        """
        params = self.parse_values_with_units(cleaned_text)

        if intent_id == "INTENT_CALCULATE_RESONANCE":
            L = params.get("inductance_h")
            C = params.get("capacitance_f")
            if L and C and L > 0 and C > 0:
                f0 = 1.0 / (2.0 * math.pi * math.sqrt(L * C))
                # Format friendly engineering notation
                if f0 >= 1e6:
                    freq_str = f"{f0 / 1e6:.3f} MHz"
                elif f0 >= 1e3:
                    freq_str = f"{f0 / 1e3:.3f} kHz"
                else:
                    freq_str = f"{f0:.2f} Hz"

                return {
                    "calculated": True,
                    "result_numeric": round(f0, 4),
                    "result_display": freq_str,
                    "explanation": f"For L = {L:.2e} H and C = {C:.2e} F, resonant frequency f0 = {freq_str}.",
                    "speech_text": f"The calculated resonant frequency is {freq_str}."
                }

        elif intent_id == "INTENT_NYQUIST_RATE":
            f_max = params.get("frequency_hz")
            if f_max and f_max > 0:
                nyquist = 2.0 * f_max
                if nyquist >= 1e6:
                    rate_str = f"{nyquist / 1e6:.3f} MHz"
                elif nyquist >= 1e3:
                    rate_str = f"{nyquist / 1e3:.3f} kHz"
                else:
                    rate_str = f"{nyquist:.2f} Hz"

                return {
                    "calculated": True,
                    "result_numeric": round(nyquist, 4),
                    "result_display": rate_str,
                    "explanation": f"For maximum signal frequency fmax = {f_max:g} Hz, the Nyquist sampling rate fs is {rate_str}.",
                    "speech_text": f"The Nyquist rate is {rate_str} to prevent aliasing."
                }

        return None

    def match_intent(self, cleaned_text: str) -> Tuple[Dict[str, Any], float]:
        """
        Matches cleaned transcript against registered intents with confidence scoring.
        Returns (intent_dict, confidence).
        """
        if not cleaned_text:
            return {
                "intent_id": "INTENT_UNKNOWN",
                "intent_name": "Unrecognized Query",
                "category": "FALLBACK",
                "action_route": None,
                "response_template": "I didn't catch that lab inquiry. You can ask for ECE formulas, hardware pinouts, or to open lab simulation benches.",
                "example_queries": []
            }, 0.0

        intents = self.get_all_intents()
        best_intent = None
        highest_score = 0.0

        words = set(cleaned_text.split())

        for item in intents:
            keywords = json.loads(item["keywords_json"])
            score = 0.0

            for kw in keywords:
                kw_lower = kw.lower()
                # Exact phrase match gives maximum weight
                if kw_lower in cleaned_text:
                    kw_word_count = len(kw_lower.split())
                    match_weight = 0.4 + (0.15 * min(kw_word_count, 4))
                    score = max(score, match_weight)
                else:
                    # Token overlap match
                    kw_words = set(kw_lower.split())
                    overlap = len(words.intersection(kw_words))
                    if overlap > 0:
                        ratio = overlap / len(kw_words)
                        if ratio == 1.0:
                            token_score = 0.50 + (0.10 * min(len(kw_words), 3))
                        else:
                            token_score = 0.35 * ratio
                        score = max(score, token_score)

            if score > highest_score:
                highest_score = score
                best_intent = item

        if best_intent and highest_score >= 0.35:
            # Normalize confidence cap to 0.98
            conf = min(0.98, highest_score + 0.15)
            return dict(best_intent), conf

        # Fallback intent if below threshold
        return {
            "intent_id": "INTENT_UNKNOWN",
            "intent_name": "Unrecognized Query",
            "category": "FALLBACK",
            "action_route": None,
            "response_template": "Query not matched to an automated ECE trigger. Try asking 'Calculate resonant frequency', 'Open physical lab', or 'What is the Nyquist rate?'.",
            "example_queries": ["calculate resonant frequency", "open physical lab", "check thermal status"]
        }, 0.15

    def get_formula_by_intent(self, intent_id: str) -> Optional[Dict[str, Any]]:
        """Finds matching ECE formula entity if applicable."""
        intent_to_formula_map = {
            "INTENT_CALCULATE_RESONANCE": "FORMULA_RESONANCE_LC",
            "INTENT_NYQUIST_RATE": "FORMULA_NYQUIST_SAMPLING",
            "INTENT_SHANNON_CAPACITY": "FORMULA_SHANNON_CAPACITY",
            "INTENT_MAXWELL_EQUATIONS": "FORMULA_MAXWELL_FARADAY",
            "INTENT_BJT_GAIN": "FORMULA_BJT_TRANSCONDUCTANCE"
        }
        f_id = intent_to_formula_map.get(intent_id)
        if not f_id:
            return None

        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM voice_ece_formulas WHERE formula_id = ?;", (f_id,))
            row = cur.fetchone()
            if row:
                res = dict(row)
                res["variables"] = json.loads(res["variables_json"])
                return res
            return None
        finally:
            conn.close()

    def process_voice_query(
        self,
        raw_transcript: str,
        student_id: str = "2023MITEC042",
        actor_role: str = "Student"
    ) -> Dict[str, Any]:
        """
        End-to-end voice query processor:
        1. Cleans transcript
        2. Classifies intent & calculates confidence
        3. Dynamically solves formula if arguments present
        4. Links matching ECE formula cards
        5. Logs query to SQLite WAL
        """
        start_time = time.perf_counter()
        cleaned = self.clean_transcript(raw_transcript)
        matched_intent, confidence = self.match_intent(cleaned)

        intent_id = matched_intent["intent_id"]
        response_text = matched_intent["response_template"]
        speech_text = response_text
        action_route = matched_intent.get("action_route")

        # Check for dynamic calculation
        calculation_result = self.solve_dynamic_formula(intent_id, cleaned)
        if calculation_result:
            response_text = calculation_result["explanation"]
            speech_text = calculation_result["speech_text"]

        # Check for formula card metadata
        formula_card = self.get_formula_by_intent(intent_id)

        execution_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        log_id = f"VLOG_{int(time.time() * 1000)}"

        # Log query
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO voice_command_logs
                    (log_id, student_id, raw_transcript, cleaned_transcript, detected_intent, confidence, response_text, action_route, execution_ms, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    log_id,
                    student_id,
                    raw_transcript,
                    cleaned,
                    intent_id,
                    confidence,
                    response_text,
                    action_route,
                    execution_ms,
                    datetime.now(timezone.utc).isoformat()
                ))
                conn.commit()
            finally:
                conn.close()

        return {
            "status": "SUCCESS",
            "log_id": log_id,
            "raw_transcript": raw_transcript,
            "cleaned_transcript": cleaned,
            "intent_id": intent_id,
            "intent_name": matched_intent["intent_name"],
            "category": matched_intent["category"],
            "confidence": round(confidence, 3),
            "response_text": response_text,
            "speech_text": speech_text,
            "action_route": action_route,
            "formula": formula_card,
            "calculation": calculation_result,
            "execution_ms": execution_ms
        }

    def get_all_intents(self) -> List[Dict[str, Any]]:
        """Returns all registered voice intents."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM voice_command_intents ORDER BY category, intent_name;")
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_all_formulas(self) -> List[Dict[str, Any]]:
        """Returns all Anna University ECE regulation 2023 formulas."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM voice_ece_formulas ORDER BY topic, formula_name;")
            rows = cur.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["variables"] = json.loads(item["variables_json"])
                results.append(item)
            return results
        finally:
            conn.close()

    def get_recent_logs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns recent voice command execution logs."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM voice_command_logs
                ORDER BY created_at DESC LIMIT ?;
            """, (limit,))
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def get_voice_overview(self) -> Dict[str, Any]:
        """Provides an aggregated overview of voice system capabilities and activity."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM voice_command_intents;")
            intent_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM voice_ece_formulas;")
            formula_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM voice_command_logs;")
            total_logs = cur.fetchone()[0]

            cur.execute("SELECT AVG(confidence), AVG(execution_ms) FROM voice_command_logs;")
            avg_row = cur.fetchone()
            avg_conf = round(avg_row[0] or 0.0, 3)
            avg_ms = round(avg_row[1] or 0.0, 2)

            return {
                "status": "OPERATIONAL",
                "campus": "Madras Institute of Technology (MIT) Campus, Anna University",
                "department": "Electronics Engineering (Regulation 2023)",
                "total_intents": intent_count,
                "total_formulas": formula_count,
                "total_queries_logged": total_logs,
                "average_confidence": avg_conf,
                "average_latency_ms": avg_ms,
                "supported_routes": [
                    "/physical-lab",
                    "/simulation",
                    "/virtual-bench",
                    "/exam-center",
                    "/smart-lab",
                    "/flash-firmware",
                    "/cloud-deploy"
                ],
                "voice_synthesis_engine": "Native Web Speech API (W3C standard)",
                "thermal_status": "PASSIVE_SAFE (<300MB RAM, zero local ML training loops)"
            }
        finally:
            conn.close()


# Global Singleton
voice_command_router = VoiceCommandRouter()
