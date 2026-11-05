"""
========================================================================================
VoltCore Apex Academia - Accessibility & Inclusive Learning Center (Phase 26)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/accessibility_engine.py
Course Scope: EC3451 (LIC), EC3491 (CS), EC3352 (DSD), EC3601 (Embedded)
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Lightweight backend accessibility engine handling:
    1. Multilingual ECE Concept Dictionary (Bilingual English & Tamil translations).
    2. Simplified Technical Explanation Engine (Intuitive physical analogies & plain English).
    3. User Accessibility Preference Persistence (Font scaling, contrast modes, Dyslexia font, TTS rate).
    4. SQLite WAL-backed data engine with sub-2ms query latency and passive thermal profile.
========================================================================================
"""

import os
import time
import json
import sqlite3
import threading
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")

# Default demo student
DEFAULT_STUDENT_ID = "2023MITEC042"

# Curated Bilingual ECE Terminology Dictionary (English & Tamil with Phonetics)
MULTILINGUAL_DICTIONARY_CATALOG = [
    {
        "term_id": "TERM_OPAMP",
        "term_en": "Operational Amplifier (Op-Amp)",
        "term_ta": "செயற்பாட்டு பெருக்கி",
        "phonetic_ta": "Seyarpaattu Perukki",
        "category": "Analog Circuits",
        "course_code": "EC3451",
        "definition_en": "A high-gain direct-coupled differential voltage amplifier with single-ended output, ideal for mathematical operations and active filtering.",
        "definition_ta": "மிக அதிக மிகைப்புத்திறன் கொண்ட நேர்-இணைப்பு வேறுபாட்டு மின்னழுத்த பெருக்கி. இது கணித செயல்பாடுகள் மற்றும் சுறுசுறுப்பான வடிகட்டிகளுக்குப் பயன்படுகிறது.",
        "example_usage": "The LM741 operational amplifier is configured as an inverting amplifier with negative feedback."
    },
    {
        "term_id": "TERM_BANDWIDTH",
        "term_en": "Bandwidth",
        "term_ta": "அலைவரிசை அகலம்",
        "phonetic_ta": "Alaivarisai Agalam",
        "category": "Communication Systems",
        "course_code": "EC3491",
        "definition_en": "The range of frequencies within a continuous band that can pass through a channel or filter without significant attenuation (-3dB limits).",
        "definition_ta": "ஒரு தடம் அல்லது வடிகட்டி வழியாக குறிப்பிடத்தக்க இழப்பின்றி (-3dB வரம்பு) செல்லக்கூடிய தொடர்ச்சியான அலைவரிசைகளின் வீச்சு.",
        "example_usage": "Carson's rule estimates the transmission bandwidth of a frequency modulated (FM) signal."
    },
    {
        "term_id": "TERM_SLEW_RATE",
        "term_en": "Slew Rate",
        "term_ta": "மின்னழுத்த மாற்ற வேகம்",
        "phonetic_ta": "Min-azhutha Maatra Vegam",
        "category": "Analog Circuits",
        "course_code": "EC3451",
        "definition_en": "The maximum rate of change of an amplifier's output voltage with respect to time, typically expressed in Volts per microsecond (V/us).",
        "definition_ta": "ஒரு பெருக்கியின் வெளியீட்டு மின்னழுத்தம் காலத்தைப் பொறுத்து மாறக்கூடிய அதிகபட்ச வேகம். இது மைக்ரோவினாடிக்கு வோல்ட் (V/us) என்ற அலகால் அளக்கப்படுகிறது.",
        "example_usage": "Exceeding the op-amp slew rate distorts a sinusoidal output waveform into a triangular wave."
    },
    {
        "term_id": "TERM_TRANSISTOR_BIAS",
        "term_en": "Transistor Biasing",
        "term_ta": "திரிதடைய சார்பளித்தல்",
        "phonetic_ta": "Thirithadai Saarpalithal",
        "category": "Analog Circuits",
        "course_code": "EC3451",
        "definition_en": "The application of fixed DC voltages across transistor terminals to establish a stable quiescent operating point (Q-point) in the active region.",
        "definition_ta": "திரிதடையத்தின் முனையங்களில் நிலையான நேர் மின்னழுத்தங்களை வழங்கி, செயல்படு பகுதியில் அமைதியான இயக்கப் புள்ளியை (Q-point) நிலைநிறுத்தும் முறை.",
        "example_usage": "Voltage divider bias provides excellent thermal stability for BJT audio amplifier stages."
    },
    {
        "term_id": "TERM_MODULATION",
        "term_en": "Modulation",
        "term_ta": "பண்பேற்றம்",
        "phonetic_ta": "Panbetram",
        "category": "Communication Systems",
        "course_code": "EC3491",
        "definition_en": "The process of varying one or more properties (amplitude, frequency, phase) of a high-frequency carrier signal in accordance with a message signal.",
        "definition_ta": "செய்தி சைகைக்கு ஏற்ப, உயர் அதிர்வெண் கொண்ட ஊர்தி சைகையின் பண்புகளை (வீச்சு, அதிர்வெண், கட்டம்) மாற்றியமைக்கும் செயல்முறை.",
        "example_usage": "Frequency modulation (FM) provides superior noise immunity compared to amplitude modulation (AM)."
    },
    {
        "term_id": "TERM_DEMODULATION",
        "term_en": "Demodulation",
        "term_ta": "பண்பிறக்கம்",
        "phonetic_ta": "Panpirakkam",
        "category": "Communication Systems",
        "course_code": "EC3491",
        "definition_en": "The extraction of the original information-bearing baseband signal from the modulated carrier wave at the receiver stage.",
        "definition_ta": "பெறுமுனையில் பண்பேற்றப்பட்ட ஊர்தி அலையிலிருந்து அசல் செய்தி சைகையை பிரித்தெடுக்கும் செயல்முறை.",
        "example_usage": "An envelope detector diode circuit performs simple demodulation of standard AM signals."
    },
    {
        "term_id": "TERM_SAMPLING",
        "term_en": "Sampling Theorem",
        "term_ta": "மாதிரி எடுப்பு தேற்றம்",
        "phonetic_ta": "Maathiri Eduppu Thetram",
        "category": "Signal Processing",
        "course_code": "EC3491",
        "definition_en": "The principle stating that a continuous band-limited signal can be completely reconstructed if sampled at a rate greater than twice its highest frequency (fs >= 2fm).",
        "definition_ta": "ஒரு தொடர் சைகையை முழுமையாக மீட்டெடுக்க, அதன் அதிகபட்ச அதிர்வெண்ணைப் போல குறைந்தது இருமடங்கு வீதத்தில் மாதிரி எடுக்க வேண்டும் (fs >= 2fm) என்னும் கோட்பாடு.",
        "example_usage": "The Nyquist sampling rate must be strictly respected to avoid frequency aliasing distortion."
    },
    {
        "term_id": "TERM_LOGIC_GATE",
        "term_en": "Logic Gate",
        "term_ta": "தருக்க வாயில்",
        "phonetic_ta": "Tharukka Vaayil",
        "category": "Digital Electronics",
        "course_code": "EC3352",
        "definition_en": "An idealized or physical electronic device implementing a Boolean logic function to perform binary operations (AND, OR, NOT, NAND, NOR).",
        "definition_ta": "பூலியன் தருக்க விதிகளின்படி இரும எண்களின் மீது செயல்பாடுகளை மேற்கொள்ளும் அடிப்படை மின்னணு சுற்று.",
        "example_usage": "NAND and NOR gates are classified as universal logic gates because any digital circuit can be constructed using them alone."
    },
    {
        "term_id": "TERM_FLIP_FLOP",
        "term_en": "Flip-Flop",
        "term_ta": "நிலைமாற்றி / துடிப்பு மாற்றி",
        "phonetic_ta": "Nilaimaatru Thudipumaatri",
        "category": "Digital Electronics",
        "course_code": "EC3352",
        "definition_en": "A bistable multivibrator circuit capable of storing one bit of binary data, triggered by clock pulse edges.",
        "definition_ta": "கடிகார துடிப்பின் மூலம் தூண்டப்பட்டு, ஒரு பிட் இரும தகவலை சேமிக்கக்கூடிய இரு-நிலை மின்னணு சுற்று.",
        "example_usage": "D flip-flops are the fundamental memory storage building blocks in digital register files and FPGA slices."
    },
    {
        "term_id": "TERM_MICROCONTROLLER",
        "term_en": "Microcontroller",
        "term_ta": "நுண்கட்டுப்படுத்தி",
        "phonetic_ta": "Nunkattuppaduthi",
        "category": "Embedded Systems",
        "course_code": "EC3601",
        "definition_en": "A compact integrated circuit containing a processor core, memory (RAM/Flash), and programmable input/output peripherals on a single silicon die.",
        "definition_ta": "செயலி, நினைவகம் மற்றும் உள்ளீட்டு/வெளியீட்டு உறுப்புகளை ஒரே சிலிக்கான் சில்லில் கொண்ட தன்னிறைவான சிறிய கணினி.",
        "example_usage": "The ESP32 microcontroller features dual Xtensa 32-bit cores with integrated Wi-Fi and Bluetooth radios."
    },
    {
        "term_id": "TERM_FEEDBACK",
        "term_en": "Negative Feedback",
        "term_ta": "எதிர் பின்னூட்டம்",
        "phonetic_ta": "Ethir Pinnoottam",
        "category": "Analog Circuits",
        "course_code": "EC3451",
        "definition_en": "Feeding a portion of the amplifier's output back to the inverting input to stabilize voltage gain, increase bandwidth, and reduce harmonic distortion.",
        "definition_ta": "வெளியீட்டு சைகையின் ஒரு பகுதியை தலைகீழ் உள்ளீட்டிற்கு மீண்டும் செலுத்தி, மிகைப்பை நிலைநிறுத்தி, சிதைவை குறைக்கும் முறை.",
        "example_usage": "Negative feedback trades open-loop voltage gain for enhanced linearity and closed-loop bandwidth."
    },
    {
        "term_id": "TERM_IMPEDANCE",
        "term_en": "Impedance",
        "term_ta": "மின்மறிப்பு",
        "phonetic_ta": "Minmarippu",
        "category": "Analog Circuits",
        "course_code": "EC3451",
        "definition_en": "The total opposition that an electrical circuit offers to alternating current (AC) at a given frequency, consisting of resistance and reactance (Z = R + jX).",
        "definition_ta": "ஒரு குறிப்பிட்ட அதிர்வெண்ணில் மாற்று மின்னோட்டத்திற்கு (AC) மின்சுற்று அளிக்கும் மொத்த எதிர்ப்பு. இது மின் தடை மற்றும் மின் எதிர்வினையின் கூட்டாகும்.",
        "example_usage": "Impedance matching between transmitter output (50 Ohm) and antenna minimizes voltage standing wave ratio (VSWR)."
    }
]

# Curated Intuitive Concept Simplifications (Plain English & Physical Analogies)
CONCEPT_SIMPLIFICATIONS_CATALOG = [
    {
        "concept_key": "slew_rate",
        "title": "Slew Rate: The Speed Limit of Voltage",
        "formal_definition": "The maximum rate at which an operational amplifier output can change in response to a step input (SR = dV/dt max).",
        "simplified_analogy": "Imagine driving a heavy truck on a highway. No matter how hard you stomp on the accelerator, the truck cannot jump from 0 to 100 km/h instantaneously—it needs time to ramp up. Similarly, an op-amp's internal charging capacitor has a physical speed limit for how fast its output voltage can climb. If an input audio signal asks it to change faster than this limit, the rounded sound wave gets squished into a sharp triangular shape, causing harsh audio distortion.",
        "diagram_ascii": "Input Sine:  ~ ~ ~ (Smooth Curvature)\nSlew-Limited: /\\/\\/\\ (Triangular Distortion)",
        "key_takeaway": "Slew Rate limits high-frequency large-amplitude signals. For a sine wave of peak Vp, the maximum undistorted frequency is fmax = SR / (2 * pi * Vp).",
        "course_code": "EC3451"
    },
    {
        "concept_key": "bandwidth",
        "title": "Bandwidth: The Width of a Highway",
        "formal_definition": "The difference between upper and lower cutoff frequencies where the circuit output power drops to half (-3dB point).",
        "simplified_analogy": "Think of electrical frequencies like cars travelling down a roadway. A single-lane dirt road can only let a slow trickle of cars pass before traffic jams occur. A multi-lane expressway (wide bandwidth) lets hundreds of cars pass side-by-side at high speed without bumper-to-bumper congestion. In circuits, wider bandwidth lets fast data pulses and rich musical overtones travel through cleanly without getting smeared.",
        "diagram_ascii": "Narrow BW: |---5kHz---| (Muffled sound, slow data)\nWide BW:   |------------------100MHz------------------| (Crystal HD video)",
        "key_takeaway": "Bandwidth determines maximum data rate (Shannon's law) and rise time speed (tr approx 0.35 / BW).",
        "course_code": "EC3491"
    },
    {
        "concept_key": "sampling_theorem",
        "title": "Nyquist Sampling: The Cinema Strobe Effect",
        "formal_definition": "A continuous time signal can be completely represented in its samples and recovered if fs >= 2 * fm.",
        "simplified_analogy": "Have you ever watched an old Western movie where a galloping wagon's wheels appear to spin backwards or freeze still? That is 'aliasing'! The film camera was capturing frames at 24 photos per second. If the wheel spokes spun faster than 12 times a second, the camera failed to take enough samples between spins, tricking your eyes into seeing a false illusion. To see the true direction, the camera must take at least twice as many photos as the fastest spin rate.",
        "diagram_ascii": "Original Wave:    ~~~~~~ (High Frequency)\nUndersampled:     - - -  (Appears as false low frequency 'Ghost' wave)\nNyquist Rate (2x): ..... (Captures every peak and valley accurately)",
        "key_takeaway": "Always sample at fs >= 2*fm, and use an analog low-pass anti-aliasing filter before the ADC to block frequencies above fs/2.",
        "course_code": "EC3491"
    },
    {
        "concept_key": "negative_feedback",
        "title": "Negative Feedback: The Home Thermostat Equilibrium",
        "formal_definition": "Feeding back an inverted fraction of the output signal to the input, reducing overall gain from A to A / (1 + A*beta).",
        "simplified_analogy": "Think about the cruise control in a car or an air conditioner thermostat. If the room gets hotter than 22°C, the thermostat measures the difference and commands the cooling compressor to turn ON. As the temperature drops back down, the cooling effort backs off. Negative feedback constantly subtracts what you have from what you want. It sacrifices raw untamed power in exchange for rock-solid stability, immunity to battery voltage drops, and crystal-clear audio.",
        "diagram_ascii": "Desired Target ----> (+) ---> [ Huge Raw Gain A ] ----> Output\n                      ^ -                                   |\n                      |------- [ Fraction beta ] <----------|",
        "key_takeaway": "Negative feedback makes amplifier gain depend almost entirely on stable passive resistors (Av = -Rf/Rin) rather than unpredictable transistor silicon manufacturing variations.",
        "course_code": "EC3451"
    },
    {
        "concept_key": "capacitive_filtering",
        "title": "Capacitor Filter: The Water Pressure Tank",
        "formal_definition": "A parallel capacitor connected across a rectifier load to reduce ripple voltage (Vr = Idc / (f * C)).",
        "simplified_analogy": "Imagine an old-fashioned manual hand pump delivering water in jerky, pulsating spurts: gush, pause, gush, pause. If you pipe that water into an elevated reservoir tank, the tank fills up during the gush and continues draining smoothly from the bottom faucet during the pause. A filter capacitor does the exact same thing for electricity: it charges up to peak AC voltage and feeds the load smoothly during the dead intervals between AC cycles.",
        "diagram_ascii": "Pulsating Rectifier: /\\/\\/\\ (Pulsating bumps)\nWith Reservoir Cap:  ~~~~~~ (Smooth steady DC level with tiny ripple)",
        "key_takeaway": "A larger capacitor (higher capacitance C) creates a bigger reservoir, resulting in lower ripple voltage Vr = I / (f*C).",
        "course_code": "EC3451"
    }
]


class AccessibilityEngine:
    """
    Lightweight, high-performance Accessibility & Inclusive Learning Center engine.
    Supports multilingual English/Tamil glossaries, plain-language concept simplifications,
    and user accessibility preference persistence with SQLite WAL storage.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def init_db(self):
        """Initializes tables for preferences, multilingual dictionary, simplifications, and feedback."""
        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    # 1. User Accessibility Preferences Table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS user_accessibility_preferences (
                            user_id TEXT PRIMARY KEY,
                            font_scale REAL DEFAULT 1.0,
                            contrast_mode TEXT DEFAULT 'dark',
                            dyslexia_font INTEGER DEFAULT 0,
                            tts_speech_rate REAL DEFAULT 1.0,
                            preferred_language TEXT DEFAULT 'en',
                            screen_reader_optimizations INTEGER DEFAULT 0,
                            keyboard_navigation_enabled INTEGER DEFAULT 1,
                            updated_at REAL
                        );
                    """)

                    # 2. Multilingual ECE Dictionary Table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS multilingual_ece_dictionary (
                            term_id TEXT PRIMARY KEY,
                            term_en TEXT NOT NULL,
                            term_ta TEXT NOT NULL,
                            phonetic_ta TEXT,
                            category TEXT NOT NULL,
                            course_code TEXT,
                            definition_en TEXT NOT NULL,
                            definition_ta TEXT NOT NULL,
                            example_usage TEXT
                        );
                    """)

                    # 3. Concept Simplifications Table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS concept_simplifications (
                            concept_key TEXT PRIMARY KEY,
                            title TEXT NOT NULL,
                            formal_definition TEXT NOT NULL,
                            simplified_analogy TEXT NOT NULL,
                            diagram_ascii TEXT,
                            key_takeaway TEXT NOT NULL,
                            course_code TEXT
                        );
                    """)

                    # 4. Accessibility Feedback Table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS accessibility_feedback (
                            feedback_id TEXT PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            category TEXT NOT NULL,
                            message TEXT NOT NULL,
                            suggested_term TEXT,
                            created_at REAL
                        );
                    """)

                    # Fast Indices
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_dict_course ON multilingual_ece_dictionary(course_code);")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_dict_cat ON multilingual_ece_dictionary(category);")

                    self._seed_default_data(conn)
            finally:
                conn.close()

    def _seed_default_data(self, conn: sqlite3.Connection):
        """Seeds bilingual dictionary and plain English concept simplifications."""
        # 1. Seed Dictionary
        for term in MULTILINGUAL_DICTIONARY_CATALOG:
            conn.execute("""
                INSERT OR IGNORE INTO multilingual_ece_dictionary (
                    term_id, term_en, term_ta, phonetic_ta,
                    category, course_code, definition_en, definition_ta, example_usage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                term["term_id"],
                term["term_en"],
                term["term_ta"],
                term["phonetic_ta"],
                term["category"],
                term["course_code"],
                term["definition_en"],
                term["definition_ta"],
                term["example_usage"]
            ))

        # 2. Seed Simplifications
        for simp in CONCEPT_SIMPLIFICATIONS_CATALOG:
            conn.execute("""
                INSERT OR IGNORE INTO concept_simplifications (
                    concept_key, title, formal_definition,
                    simplified_analogy, diagram_ascii, key_takeaway, course_code
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (
                simp["concept_key"],
                simp["title"],
                simp["formal_definition"],
                simp["simplified_analogy"],
                simp["diagram_ascii"],
                simp["key_takeaway"],
                simp["course_code"]
            ))

        # 3. Seed Default Preferences for Lead Student Ashok Kumar A
        now = time.time()
        conn.execute("""
            INSERT OR IGNORE INTO user_accessibility_preferences (
                user_id, font_scale, contrast_mode, dyslexia_font,
                tts_speech_rate, preferred_language, screen_reader_optimizations,
                keyboard_navigation_enabled, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            DEFAULT_STUDENT_ID,
            1.0,
            "dark",
            0,
            1.0,
            "en",
            1,
            1,
            now
        ))

    # ====================================================================================
    # 1. Overview & Accessibility Metrics
    # ====================================================================================

    def get_overview(self, user_id: str = DEFAULT_STUDENT_ID) -> Dict[str, Any]:
        """Provides an aggregated overview of accessibility resources and user settings."""
        conn = self._get_connection()
        try:
            cur = conn.execute("SELECT COUNT(*) AS total_terms FROM multilingual_ece_dictionary;")
            total_terms = cur.fetchone()["total_terms"]

            cur = conn.execute("SELECT COUNT(*) AS total_simps FROM concept_simplifications;")
            total_simps = cur.fetchone()["total_simps"]

            cur = conn.execute("SELECT COUNT(DISTINCT category) AS total_cats FROM multilingual_ece_dictionary;")
            total_cats = cur.fetchone()["total_cats"]

            prefs = self.get_preferences(user_id)

            return {
                "status": "SUCCESS",
                "user_id": user_id,
                "institution": "Madras Institute of Technology (MIT) Campus, Anna University",
                "supported_languages": [
                    {"code": "en", "name": "English", "native": "English"},
                    {"code": "ta", "name": "Tamil", "native": "தமிழ்"}
                ],
                "metrics": {
                    "dictionary_terms_count": total_terms,
                    "concept_simplifications_count": total_simps,
                    "curriculum_categories_count": total_cats,
                    "tts_supported": True,
                    "keyboard_shortcuts_active": True
                },
                "current_preferences": prefs
            }
        finally:
            conn.close()

    # ====================================================================================
    # 2. User Preferences Persistence
    # ====================================================================================

    def get_preferences(self, user_id: str = DEFAULT_STUDENT_ID) -> Dict[str, Any]:
        """Retrieves user visual, reading, and auditory accessibility preferences."""
        conn = self._get_connection()
        try:
            cur = conn.execute("SELECT * FROM user_accessibility_preferences WHERE user_id = ?;", (user_id,))
            row = cur.fetchone()
            if not row:
                # Return default preference profile
                return {
                    "user_id": user_id,
                    "font_scale": 1.0,
                    "contrast_mode": "dark",
                    "dyslexia_font": False,
                    "tts_speech_rate": 1.0,
                    "preferred_language": "en",
                    "screen_reader_optimizations": False,
                    "keyboard_navigation_enabled": True
                }

            return {
                "user_id": row["user_id"],
                "font_scale": float(row["font_scale"]),
                "contrast_mode": row["contrast_mode"],
                "dyslexia_font": bool(row["dyslexia_font"]),
                "tts_speech_rate": float(row["tts_speech_rate"]),
                "preferred_language": row["preferred_language"],
                "screen_reader_optimizations": bool(row["screen_reader_optimizations"]),
                "keyboard_navigation_enabled": bool(row["keyboard_navigation_enabled"]),
                "updated_at": row["updated_at"]
            }
        finally:
            conn.close()

    def save_preferences(self, user_id: str, prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Saves or updates user visual and auditory accessibility preferences."""
        font_scale = max(0.7, min(2.0, float(prefs.get("font_scale", 1.0))))
        contrast = prefs.get("contrast_mode", "dark")
        if contrast not in ["normal", "high-contrast", "dark", "sepia"]:
            contrast = "dark"

        dyslexia = 1 if prefs.get("dyslexia_font") else 0
        tts_rate = max(0.5, min(2.5, float(prefs.get("tts_speech_rate", 1.0))))
        lang = "ta" if prefs.get("preferred_language") == "ta" else "en"
        screen_reader = 1 if prefs.get("screen_reader_optimizations") else 0
        keyboard = 1 if prefs.get("keyboard_navigation_enabled", True) else 0
        now = time.time()

        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO user_accessibility_preferences (
                            user_id, font_scale, contrast_mode, dyslexia_font,
                            tts_speech_rate, preferred_language, screen_reader_optimizations,
                            keyboard_navigation_enabled, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        user_id, font_scale, contrast, dyslexia,
                        tts_rate, lang, screen_reader, keyboard, now
                    ))
                return {
                    "status": "SUCCESS",
                    "user_id": user_id,
                    "message": "Accessibility preferences saved successfully.",
                    "preferences": {
                        "font_scale": font_scale,
                        "contrast_mode": contrast,
                        "dyslexia_font": bool(dyslexia),
                        "tts_speech_rate": tts_rate,
                        "preferred_language": lang,
                        "screen_reader_optimizations": bool(screen_reader),
                        "keyboard_navigation_enabled": bool(keyboard)
                    }
                }
            finally:
                conn.close()

    # ====================================================================================
    # 3. Multilingual ECE Concept Dictionary
    # ====================================================================================

    def get_dictionary(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        course_code: Optional[str] = None,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Searches bilingual dictionary by English or Tamil terms, definitions, and course codes.
        """
        conn = self._get_connection()
        try:
            sql = "SELECT * FROM multilingual_ece_dictionary WHERE 1=1"
            params = []

            if category and category != "ALL":
                sql += " AND category = ?"
                params.append(category)

            if course_code and course_code != "ALL":
                sql += " AND course_code = ?"
                params.append(course_code)

            if query:
                clean_q = f"%{query.strip().lower()}%"
                sql += " AND (LOWER(term_en) LIKE ? OR LOWER(term_ta) LIKE ? OR LOWER(phonetic_ta) LIKE ? OR LOWER(definition_en) LIKE ?)"
                params.extend([clean_q, clean_q, clean_q, clean_q])

            sql += " ORDER BY term_en ASC;"
            cur = conn.execute(sql, tuple(params))
            results = []
            for row in cur.fetchall():
                results.append({
                    "term_id": row["term_id"],
                    "term_en": row["term_en"],
                    "term_ta": row["term_ta"],
                    "phonetic_ta": row["phonetic_ta"],
                    "category": row["category"],
                    "course_code": row["course_code"],
                    "definition_en": row["definition_en"],
                    "definition_ta": row["definition_ta"],
                    "example_usage": row["example_usage"]
                })
            return results
        finally:
            conn.close()

    # ====================================================================================
    # 4. Intuitive Concept Simplification Engine
    # ====================================================================================

    def get_simplification(self, concept_key: str) -> Optional[Dict[str, Any]]:
        """Retrieves plain English analogies and intuitive explanations for an ECE concept."""
        conn = self._get_connection()
        try:
            cur = conn.execute("SELECT * FROM concept_simplifications WHERE concept_key = ?;", (concept_key,))
            row = cur.fetchone()
            if not row:
                return None
            return {
                "concept_key": row["concept_key"],
                "title": row["title"],
                "formal_definition": row["formal_definition"],
                "simplified_analogy": row["simplified_analogy"],
                "diagram_ascii": row["diagram_ascii"],
                "key_takeaway": row["key_takeaway"],
                "course_code": row["course_code"]
            }
        finally:
            conn.close()

    def get_all_simplifications(self) -> List[Dict[str, Any]]:
        """Retrieves all pre-indexed concept simplifications."""
        conn = self._get_connection()
        try:
            cur = conn.execute("SELECT * FROM concept_simplifications ORDER BY concept_key ASC;")
            results = []
            for row in cur.fetchall():
                results.append({
                    "concept_key": row["concept_key"],
                    "title": row["title"],
                    "formal_definition": row["formal_definition"],
                    "simplified_analogy": row["simplified_analogy"],
                    "diagram_ascii": row["diagram_ascii"],
                    "key_takeaway": row["key_takeaway"],
                    "course_code": row["course_code"]
                })
            return results
        finally:
            conn.close()

    # ====================================================================================
    # 5. Accessibility User Feedback
    # ====================================================================================

    def record_feedback(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Logs user accessibility improvement suggestions and missing translation requests."""
        user_id = data.get("user_id", DEFAULT_STUDENT_ID)
        category = data.get("category", "GENERAL")
        message = (data.get("message") or "").strip()
        suggested_term = data.get("suggested_term")
        if not message:
            return {"status": "ERROR", "message": "Feedback message cannot be empty."}

        feedback_id = data.get("feedback_id") or f"ACC_FB_{int(time.time()*1000)}"
        now = time.time()

        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    conn.execute("""
                        INSERT INTO accessibility_feedback (
                            feedback_id, user_id, category, message, suggested_term, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?);
                    """, (feedback_id, user_id, category, message, suggested_term, now))
                return {
                    "status": "SUCCESS",
                    "feedback_id": feedback_id,
                    "message": "Thank you! Your accessibility feedback has been submitted to the MIT portal team."
                }
            finally:
                conn.close()


# Singleton instance for system-wide dispatch
accessibility_engine = AccessibilityEngine()
