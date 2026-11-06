"""
========================================================================================
VoltCore Apex Academia - Phase N: Accessibility & Multilingual Learning (Features 341–350)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Features:
  - Feature 341: English-Tamil Technical Dictionary (ECE Terms, Transliteration, Definitions)
  - Feature 342: Tamil Concept Explanation Library (Bilingual ECE Explanations & Audio scripts)
  - Feature 343: Text-to-Speech Lesson Reader (Speech synthesis configurations, rate, pitch)
  - Feature 344: Video Subtitle Manager (SRT/VTT parser, timestamp sync, bilingual tracks)
  - Feature 345: Adjustable Reading Interface (Font size, line height, dyslexic font toggles)
  - Feature 346: Keyboard-Only Navigation & Shortcut Engine (WCAG 2.1 AAA accessibility mapping)
  - Feature 347: High-Contrast Theme Options (Contrast ratios > 7:1 & > 14:1)
  - Feature 348: Accessible Mathematical Formula Display (MathML/LaTeX to spoken description)
  - Feature 349: Simplified Technical Definitions (ELI5 English & Tamil analogies)
  - Feature 350: Multilingual Search Support (Cross-lingual search English <-> Tamil script)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
========================================================================================
"""

import os
import re
import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")

# ---------------------------------------------------------------------------
# ECE ENGLISH-TAMIL TECHNICAL DICTIONARY CATALOG (Feature 341 & 349)
# ---------------------------------------------------------------------------

ECE_DICTIONARY: Dict[str, Dict[str, Any]] = {
    "semiconductor": {
        "term_en": "Semiconductor",
        "term_ta": "குறைகடத்தி",
        "transliteration": "Kuraikadathi",
        "phonetic": "/kʊ-raɪ-kə-dʌ-θi/",
        "subject_code": "EC3451",
        "definition_en": "A material whose electrical conductivity lies between that of a conductor (e.g., copper) and an insulator (e.g., glass), with resistivity modifiable by doping.",
        "definition_ta": "கடத்திக்கும் (எ.கா. செம்பு) மின்கடத்தாப் பொருளுக்கும் (எ.கா. கண்ணாடி) இடைப்பட்ட மின்கடத்துத்திறன் கொண்ட பொருள்; மாசு சேர்த்தல் மூலம் இதன் கடத்துத்திறன் மாற்றியமைக்கப்படும்.",
        "simplified_en": "A smart material (like silicon) that can act like a switch: letting electricity flow when you want, and blocking it when you don't.",
        "simplified_ta": "தேவைப்படும்போது மின்சாரத்தை கடத்தவும், தேவையில்லாதபோது தடுக்கவும் கூடிய சிலிக்கான் போன்ற அதிநவீன சுவிட்ச் பொருள்."
    },
    "diode": {
        "term_en": "Diode",
        "term_ta": "இருமுனையம்",
        "transliteration": "Irumunaiyam",
        "phonetic": "/ɪ-rʊ-mʊ-naɪ-jʌm/",
        "subject_code": "EC3451",
        "definition_en": "A two-terminal semiconductor device that permits current to flow readily in forward bias and blocks current in reverse bias.",
        "definition_ta": "நேர்திசை மின்னழுத்தத்தில் மின்னோட்டத்தை எளிதாக கடத்தவும், எதிர்திசையில் தடுக்கவும் செய்யும் இரு முனைகளைக் கொண்ட குறைகடத்திக் கருவி.",
        "simplified_en": "A one-way turnstile gate for electric current.",
        "simplified_ta": "மின்சாரத்தை ஒரே திசையில் மட்டும் செல்ல அனுமதிக்கும் ஒருவழிப் பாதை கேட்."
    },
    "transistor": {
        "term_en": "Transistor",
        "term_ta": "திரிதடையம்",
        "transliteration": "Thirithadaiyam",
        "phonetic": "/θɪ-rɪ-θʌ-daɪ-jʌm/",
        "subject_code": "EC3451",
        "definition_en": "A three-terminal semiconductor device used to amplify or switch electrical signals and power.",
        "definition_ta": "மின் சமிக்ஞைகளைப் பெருக்கவும் மற்றும் விரைவாக சுவிட்ச் செய்யவும் பயன்படும் மூன்று முனையக் குறைகடத்திக் கருவி.",
        "simplified_en": "A tiny electronic faucet where a small control signal turns a large stream of electric current on and off.",
        "simplified_ta": "ஒரு சிறிய சிக்னல் மூலம் பெரிய மின்னோட்டத்தைக் கட்டுப்படுத்தும் மின்னணு குழாய் (சுவிட்ச்)."
    },
    "capacitor": {
        "term_en": "Capacitor",
        "term_ta": "மின்தேக்கி",
        "transliteration": "Minthekki",
        "phonetic": "/mɪn-ðeːk-kɪ/",
        "subject_code": "EC3351",
        "definition_en": "A passive two-terminal component that stores electrical energy in an electrostatic field between two conducting plates separated by a dielectric.",
        "definition_ta": "இரு கடத்துத் தகடுகளுக்கு இடையே மின்காப்புப் பொருளைக் கொண்டு மின்புலத்தில் ஆற்றலைச் சேமிக்கும் செயலற்ற மின்னணுக் கூறு.",
        "simplified_en": "A mini temporary battery that charges and discharges in milliseconds to smooth out voltage bumps.",
        "simplified_ta": "மின்னழுத்த ஏற்றத்தாழ்வுகளைச் சீராக்க மில்லி வினாடிகளில் மின்னேற்றம் செய்து உடனே வெளியிடும் தற்காலிக மின்கலம்."
    },
    "inductor": {
        "term_en": "Inductor",
        "term_ta": "மின்தூண்டி",
        "transliteration": "Minthundi",
        "phonetic": "/mɪn-ðuːɳ-ɖɪ/",
        "subject_code": "EC3452",
        "definition_en": "A passive component that stores energy in a magnetic field when electric current flows through it, opposing rapid changes in current.",
        "definition_ta": "மின்னோட்டம் பாயும் போது காந்தப்புலத்தில் ஆற்றலைச் சேமித்து, மின்னோட்ட மாற்றத்தை எதிர்க்கும் செயலற்ற மின்னணுக் கூறு.",
        "simplified_en": "A coil of wire that resists sudden changes in electrical current, acting like a shock absorber for electricity.",
        "simplified_ta": "மின்சாரத்தில் திடீரென ஏற்படும் மாற்றங்களை எதிர்க்கும் ஒரு சுருள் கம்பி."
    },
    "frequency": {
        "term_en": "Frequency",
        "term_ta": "அதிர்வெண்",
        "transliteration": "Athirven",
        "phonetic": "/ʌ-ðɪr-ʋeɳ/",
        "subject_code": "EC3501",
        "definition_en": "The number of complete cycles or oscillations of a periodic waveform occurring per unit time, measured in Hertz (Hz).",
        "definition_ta": "ஒரு வினாடியில் நிகழும் முழுமையான அலைவுக் காலவட்டங்களின் எண்ணிக்கை; இதன் அலகு ஹெர்ட்ஸ் (Hz).",
        "simplified_en": "How many times a wave wiggles back and forth every second.",
        "simplified_ta": "ஒரு வினாடியில் அலை எத்தனை முறை மேலும் கீழுமாக துடிக்கிறது என்ற எண்ணிக்கை."
    },
    "modulation": {
        "term_en": "Modulation",
        "term_ta": "பண்பேற்றம்",
        "transliteration": "Panpetram",
        "phonetic": "/pʌɳ-beː-trʌm/",
        "subject_code": "EC3501",
        "definition_en": "The process of varying one or more properties of a high-frequency carrier wave (amplitude, frequency, or phase) in proportion to an information-bearing message signal.",
        "definition_ta": "தகவல் சமிக்ஞைக்கு ஏற்ப உயர் அதிர்வெண் கொண்ட ஊர்தி அலையின் வீச்சு, அதிர்வெண் அல்லது கட்டத்தை மாற்றியமைக்கும் முறை.",
        "simplified_en": "Mounting your low-pitch voice onto a high-speed supersonic airplane wave so it can travel across cities.",
        "simplified_ta": "நமது குரலை வெகுதூரம் அனுப்ப, அதை ஒரு அதிவேக ராக்கெட் அலையின் மேல் ஏற்றி அனுப்பும் உத்தி."
    },
    "sampling": {
        "term_en": "Sampling",
        "term_ta": "மாதிரியெடுத்தல்",
        "transliteration": "Maathiriyeduthal",
        "phonetic": "/maː-θɪ-rɪ-je-ɖʊ-θʌl/",
        "subject_code": "EC3501",
        "definition_en": "The conversion of a continuous-time analog signal into a discrete-time sequence of values taken at periodic intervals.",
        "definition_ta": "தொடர்ச்சியான நேர அனலாக் சமிக்ஞையை சீரான கால இடைவெளிகளில் தனித்தனி அளவுகளாக மாற்றும் முறை.",
        "simplified_en": "Taking snapshots of a moving video 60 times a second so a computer can store and replay it.",
        "simplified_ta": "தொடர்ச்சியாக ஓடும் காட்சியை வினாடிக்கு பல முறை புகைப்படம் எடுத்து சேமிப்பது போன்றது."
    },
    "impedance": {
        "term_en": "Impedance",
        "term_ta": "மின்மறிப்பு",
        "transliteration": "Minmarippu",
        "phonetic": "/mɪn-mʌ-rɪp-pʊ/",
        "subject_code": "EC3551",
        "definition_en": "The total effective opposition that a circuit presents to alternating current (AC), consisting of resistance and reactance (Z = R + jX).",
        "definition_ta": "மாறுதிசை மின்னோட்டத்திற்கு (AC) ஒரு மின்சுற்று ஏற்படுத்தும் ஒட்டுமொத்த எதிர்ப்பு; இது மின்தடை மற்றும் மின்எதிர்ப்பு ஆகியவற்றின் கூட்டமைப்பாகும் (Z = R + jX).",
        "simplified_en": "The total roadblock an alternating current faces, combining both regular friction and reactive springiness.",
        "simplified_ta": "ஏசி மின்சாரம் பாய்வதற்கு மின்சுற்று ஏற்படுத்தும் மொத்த தடை அரண்."
    },
    "amplification": {
        "term_en": "Amplification",
        "term_ta": "பெருக்கம்",
        "transliteration": "Perukkam",
        "phonetic": "/pe-rʊk-kʌm/",
        "subject_code": "EC3451",
        "definition_en": "The technique of increasing the magnitude (voltage, current, or power) of a time-varying signal without altering its fundamental waveform shape.",
        "definition_ta": "ஒரு சமிக்ஞையின் அலைவடிவத்தை மாற்றாமல், அதன் மின்னழுத்தம், மின்னோட்டம் அல்லது திறனின் வீச்சை அதிகரிக்கும் செயல்முறை.",
        "simplified_en": "Using a megaphone to make a whisper loud enough for a stadium to hear without changing what words were said.",
        "simplified_ta": "ஒரு மெல்லிய குரலை அதன் அசல் தன்மை மாறாமல் ஒலிபெருக்கி மூலம் பல மடங்கு பெரிதாக்குவது."
    }
}

# ---------------------------------------------------------------------------
# TAMIL CONCEPT EXPLANATION LIBRARY (Feature 342)
# ---------------------------------------------------------------------------

CONCEPT_EXPLANATIONS: Dict[str, Dict[str, Any]] = {
    "pn_junction": {
        "id": "pn_junction",
        "title_en": "PN Junction Diode Operation",
        "title_ta": "பி-என் சந்தி இருமுனையத்தின் இயக்கம்",
        "subject": "EC3451",
        "tamil_summary": "P-வகை மற்றும் N-வகை குறைகடத்திகள் இணையும் போது, சந்தியில் எலக்ட்ரான்கள் மற்றும் துளைகளின் பரவலால் ஒரு வறுமை மண்டலம் (Depletion Region) உருவாகிறது. நேர்மின்னழுத்தம் தரும்போது இவ்வெல்லை சுருங்கி மின்னோட்டம் பாய்கிறது.",
        "english_summary": "When P-type and N-type semiconductors merge, carrier diffusion forms a depletion region with a built-in barrier potential (0.7V for Silicon). Forward bias overcomes this barrier, enabling exponential conduction.",
        "spoken_script_ta": "பி என் சந்தி இருமுனையம் என்பது சிலிக்கான் படிகத்தில் பி வகை மற்றும் என் வகை பகுதிகள் இணையும் சந்தி ஆகும். சிலிக்கான் சந்திக்கு பூஜ்ஜியம் புள்ளி ஏழு வோல்ட் நேர்திசை மின்னழுத்தம் வழங்கும்போது, வறுமை மண்டலம் உடைந்து மின்னோட்டம் பாய்கிறது.",
        "eli5_ta": "ஒரு கதவு போன்றது: உள்ளிருந்து தள்ளினால் (நேர் மின்சாரம்) கதவு எளிதாகத் திறக்கும், வெளியிருந்து தள்ளினால் தானாக பூட்டிக்கொள்ளும்."
    },
    "op_amp_inverting": {
        "id": "op_amp_inverting",
        "title_en": "Inverting Operational Amplifier",
        "title_ta": "எதிர்த்திசை செயல்பாட்டுப் பெருக்கி (Inverting Op-Amp)",
        "subject": "EC3451",
        "tamil_summary": "மெய்நிகர் தரை (Virtual Ground) கருத்தின்படி, ஆப்-ஆம்ப் இன் நேர்மறை முனை தரையிறக்கப்பட்டால், எதிர்மறை முனையும் சுழி வோல்ட்டாகக் கருதப்படும். இதன் மூலம் வெளியீட்டு மின்னழுத்தம் Vout = -(Rf/Rin) * Vin என பெறப்படுகிறது.",
        "english_summary": "By virtue of infinite open-loop gain and virtual ground at the inverting terminal, feedback resistor Rf and input resistor Rin determine closed-loop gain: Vout = -(Rf/Rin) * Vin.",
        "spoken_script_ta": "செயல்பாட்டுப் பெருக்கியின் எதிர்த்திசை உள்ளீட்டில் சிக்னல் கொடுக்கப்பட்டு நேர்மறை முனை தரையிறக்கப்படும்போது, மெய்நிகர் தரை உருவாகிறது. இதனால் வெளியீட்டு மின்னழுத்தம் உள்ளீட்டின் தலைகீழான பெருக்கமாக வெளிப்படுகிறது.",
        "eli5_ta": "ஒரு சீ-சா ஊஞ்சல் பலகை போல: ஒரு பக்கத்தை கீழே அழுத்தினால் (உள்ளீடு), மறுபக்கம் பல மடங்கு உயரே எழும்பும் (வெளியீடு)."
    },
    "nyquist_sampling": {
        "id": "nyquist_sampling",
        "title_en": "Nyquist-Shannon Sampling Theorem",
        "title_ta": "நைகுவிஸ்ட்-ஷானன் மாதிரி கோட்பாடு",
        "subject": "EC3501",
        "tamil_summary": "அனலாக் சிக்னலை சிதைவின்றி டிஜிட்டலாக மாற்ற, மாதிரியெடுப்பு அதிர்வெண் (fs) சிக்னலின் உச்ச அதிர்வெண்ணை (fmax) விட குறைந்தது இருமடங்காக இருக்க வேண்டும் (fs >= 2 * fmax). தவறினால் மாற்றுப்பெயரிடுதல் (Aliasing) சிதைவு ஏற்படும்.",
        "english_summary": "To reconstruct a bandlimited analog signal without aliasing distortion, the sampling frequency fs must be at least twice the maximum signal frequency component: fs >= 2 * fmax.",
        "spoken_script_ta": "நைகுவிஸ்ட் மாதிரி கோட்பாட்டின்படி, ஒரு தொடர் சிக்னலை டிஜிட்டலாக மாற்றும்போது அதன் அதிகபட்ச அதிர்வெண்ணைப் போல இரு மடங்கு வேகத்தில் மாதிரிகள் எடுக்க வேண்டும். இல்லையெனில் சிக்னலில் அலியாசிங் என்ற பெரும் பிழை உருவாகும்.",
        "eli5_ta": "ஒரு கார் சக்கரம் முன்னோக்கி சுழல்வதை சரியாகப் பதிவு செய்ய, கேமரா சக்கரத்தின் சுழற்சியை விட இருமடங்கு வேகத்தில் படம் பிடிக்க வேண்டும், இல்லாவிட்டால் சக்கரம் பின்னோக்கி சுழல்வது போல மாயத்தோற்றம் தோன்றும்."
    }
}

# ---------------------------------------------------------------------------
# ACCESSIBLE MATH FORMULAS (Feature 348)
# ---------------------------------------------------------------------------

ACCESSIBLE_FORMULAS: List[Dict[str, Any]] = [
    {
        "id": "ohm_law",
        "name": "Ohm's Law",
        "latex": "V = I \\times R",
        "mathml": "<math><mi>V</mi><mo>=</mo><mi>I</mi><mo>&times;</mo><mi>R</mi></math>",
        "spoken_en": "Voltage V equals electric current I multiplied by resistance R.",
        "spoken_ta": "மின்னழுத்தம் V சமம் மின்னோட்டம் I பெருக்கல் மின்தடை R.",
        "description": "Fundamental relationship between voltage, current, and resistance in a linear conductor."
    },
    {
        "id": "nyquist_formula",
        "name": "Nyquist Minimum Sampling Rate",
        "latex": "f_s \\ge 2 f_{\\max}",
        "mathml": "<math><msub><mi>f</mi><mi>s</mi></msub><mo>&ge;</mo><mn>2</mn><msub><mi>f</mi><mo>max</mo></msub></math>",
        "spoken_en": "Sampling frequency f sub s must be greater than or equal to two times the maximum signal frequency f sub max.",
        "spoken_ta": "மாதிரியெடுப்பு அதிர்வெண் f sub s, சிக்னலின் அதிகபட்ச அதிர்வெண் f max-ஐ விட இரண்டு மடங்கு அல்லது அதற்கு அதிகமாக இருக்க வேண்டும்.",
        "description": "Criterion to prevent spectral aliasing in pulse code modulation."
    },
    {
        "id": "inverting_gain",
        "name": "Inverting Op-Amp Closed-Loop Gain",
        "latex": "V_{\\text{out}} = -\\left(\\frac{R_f}{R_{\\text{in}}}\\right) V_{\\text{in}}",
        "mathml": "<math><msub><mi>V</mi><mo>out</mo></msub><mo>=</mo><mo>-</mo><mrow><mo>(</mo><mfrac><msub><mi>R</mi><mi>f</mi></msub><msub><mi>R</mi><mo>in</mo></msub></mfrac><mo>)</mo></mrow><msub><mi>V</mi><mo>in</mo></msub></math>",
        "spoken_en": "Output voltage V out equals negative open parenthesis R f divided by R in close parenthesis multiplied by input voltage V in.",
        "spoken_ta": "வெளியீட்டு மின்னழுத்தம் V out சமம் மைனஸ் ஆர் எஃப் வகுத்தல் ஆர் இன் பெருக்கல் உள்ளீட்டு மின்னழுத்தம் V in.",
        "description": "Gain equation of inverting operational amplifier configuration with 180 degree phase shift."
    },
    {
        "id": "maxwell_faraday",
        "name": "Faraday-Maxwell Induction Law",
        "latex": "\\nabla \\times \\mathbf{E} = -\\frac{\\partial \\mathbf{B}}{\\partial t}",
        "mathml": "<math><mo>&nabla;</mo><mo>&times;</mo><mi mathvariant='bold'>E</mi><mo>=</mo><mo>-</mo><mfrac><mrow><mo>&part;</mo><mi mathvariant='bold'>B</mi></mrow><mrow><mo>&part;</mo><mi>t</mi></mrow></mfrac></math>",
        "spoken_en": "Curl of electric field vector E equals negative partial derivative of magnetic flux density B with respect to time t.",
        "spoken_ta": "மின்புலம் E வெக்டரின் சுருள் சமம் காலத்தைப் பொருத்து காந்தப்பாய்வு அடர்த்தி B-ன் மைனஸ் பகுதி வகைக்கெழு.",
        "description": "A time-varying magnetic field induces a spatially circulating non-conservative electric field."
    }
]


class AccessibilityMultilingualEngine:
    """
    Core backend engine for VoltCore Apex Academia Phase N (Features 341–350).
    Manages English-Tamil technical dictionary queries, bilingual audio scripts,
    subtitle tracks, accessible math formulations, and user accessibility profiles.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_sqlite()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _init_sqlite(self) -> None:
        with self._lock:
            conn = self._get_connection()
            try:
                # Student Accessibility Preferences (Features 345, 346, 347)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_accessibility_prefs (
                        student_roll TEXT PRIMARY KEY,
                        font_size INTEGER DEFAULT 16,
                        line_spacing REAL DEFAULT 1.6,
                        letter_spacing REAL DEFAULT 0.5,
                        font_family TEXT DEFAULT 'system',
                        high_contrast_theme TEXT DEFAULT 'dark_cyber',
                        tts_speech_rate REAL DEFAULT 1.0,
                        tts_pitch REAL DEFAULT 1.0,
                        preferred_language TEXT DEFAULT 'en-IN',
                        screen_reader_verbosity TEXT DEFAULT 'normal',
                        updated_at TEXT NOT NULL
                    )
                """)

                # Video Subtitle Storage (Feature 344)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS video_subtitles (
                        id TEXT PRIMARY KEY,
                        lesson_id TEXT NOT NULL,
                        language TEXT NOT NULL,
                        cues_json TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                """)

                # Technical Dictionary Custom Additions (Feature 341)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS custom_dictionary_terms (
                        term_key TEXT PRIMARY KEY,
                        term_en TEXT NOT NULL,
                        term_ta TEXT NOT NULL,
                        transliteration TEXT NOT NULL,
                        phonetic TEXT NOT NULL,
                        subject_code TEXT NOT NULL,
                        definition_en TEXT NOT NULL,
                        definition_ta TEXT NOT NULL,
                        simplified_en TEXT NOT NULL,
                        simplified_ta TEXT NOT NULL,
                        contributed_by TEXT NOT NULL
                    )
                """)

                conn.commit()
            finally:
                conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 341 & 350: ENGLISH-TAMIL DICTIONARY & MULTILINGUAL SEARCH
    # ---------------------------------------------------------------------------

    def lookup_term(self, query: str) -> Optional[Dict[str, Any]]:
        """Lookup a term in English or Tamil."""
        clean_q = query.strip().lower()

        # Check standard dictionary
        for key, data in ECE_DICTIONARY.items():
            if (
                clean_q == key.lower()
                or clean_q == data["term_en"].lower()
                or clean_q in data["term_ta"]
                or clean_q == data["transliteration"].lower()
            ):
                return data

        # Check custom user contributions in SQLite
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM custom_dictionary_terms
                WHERE LOWER(term_key) = ? OR LOWER(term_en) = ? OR term_ta LIKE ? OR LOWER(transliteration) = ?
            """, (clean_q, clean_q, f"%{clean_q}%", clean_q))
            row = cursor.fetchone()
            if row:
                return dict(row)
        finally:
            conn.close()

        return None

    def search_multilingual(self, query: str) -> List[Dict[str, Any]]:
        """Cross-lingual search across English and Tamil terms, definitions, and concepts."""
        clean_q = query.strip().lower()
        results = []

        # Search dictionary
        for key, item in ECE_DICTIONARY.items():
            score = 0
            if clean_q in item["term_en"].lower():
                score += 10
            if clean_q in item["term_ta"]:
                score += 10
            if clean_q in item["transliteration"].lower():
                score += 8
            if clean_q in item["definition_en"].lower() or clean_q in item["definition_ta"]:
                score += 5

            if score > 0:
                results.append({"type": "dictionary", "score": score, "data": item})

        # Search concepts
        for c_id, concept in CONCEPT_EXPLANATIONS.items():
            score = 0
            if clean_q in concept["title_en"].lower() or clean_q in concept["title_ta"]:
                score += 10
            if clean_q in concept["english_summary"].lower() or clean_q in concept["tamil_summary"]:
                score += 5

            if score > 0:
                results.append({"type": "concept", "score": score, "data": concept})

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def add_custom_term(
        self,
        term_en: str,
        term_ta: str,
        transliteration: str,
        phonetic: str,
        subject_code: str,
        definition_en: str,
        definition_ta: str,
        simplified_en: str,
        simplified_ta: str,
        contributor_roll: str
    ) -> Dict[str, Any]:
        """Add a student-contributed term to the technical dictionary."""
        term_key = term_en.strip().lower().replace(" ", "_")
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO custom_dictionary_terms
                    (term_key, term_en, term_ta, transliteration, phonetic, subject_code, definition_en, definition_ta, simplified_en, simplified_ta, contributed_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (term_key, term_en, term_ta, transliteration, phonetic, subject_code.upper(), definition_en, definition_ta, simplified_en, simplified_ta, contributor_roll))
                conn.commit()
            finally:
                conn.close()

        return {"status": "success", "term_key": term_key, "term_en": term_en, "term_ta": term_ta}

    # ---------------------------------------------------------------------------
    # FEATURE 342: TAMIL CONCEPT EXPLANATION LIBRARY
    # ---------------------------------------------------------------------------

    def get_concept_explanation(self, concept_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve bilingual ECE concept explanation with audio text."""
        return CONCEPT_EXPLANATIONS.get(concept_id.lower())

    def list_all_concepts(self) -> List[Dict[str, Any]]:
        """List all bilingual concepts in catalog."""
        return list(CONCEPT_EXPLANATIONS.values())

    # ---------------------------------------------------------------------------
    # FEATURE 344: VIDEO SUBTITLE MANAGER
    # ---------------------------------------------------------------------------

    def parse_vtt_subtitles(self, vtt_content: str) -> List[Dict[str, Any]]:
        """
        Parse WebVTT content into structured timestamped cues:
        [{start: '00:01.000', end: '00:04.500', text: '...'}]
        """
        cues = []
        # Pattern for standard WebVTT / SRT timestamps: 00:00:01.000 --> 00:00:04.500 or 00:01.000 --> 00:04.500
        time_pattern = re.compile(r"((?:\d{2}:)?\d{2}:\d{2}[\.,]\d{3})\s*-->\s*((?:\d{2}:)?\d{2}:\d{2}[\.,]\d{3})")

        lines = vtt_content.strip().splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            match = time_pattern.search(line)
            if match:
                start_time = match.group(1).replace(",", ".")
                end_time = match.group(2).replace(",", ".")
                text_lines = []
                i += 1
                while i < len(lines) and lines[i].strip() and not time_pattern.search(lines[i]):
                    text_lines.append(lines[i].strip())
                    i += 1
                cues.append({
                    "start": start_time,
                    "end": end_time,
                    "text": " ".join(text_lines)
                })
            else:
                i += 1
        return cues

    def save_subtitles(self, lesson_id: str, language: str, cues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Save parsed subtitles for a lesson."""
        sub_id = f"sub_{lesson_id}_{language.lower()}"
        now_iso = datetime.now(timezone.utc).isoformat()
        cues_json = json.dumps(cues)
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO video_subtitles
                    (id, lesson_id, language, cues_json, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (sub_id, lesson_id, language.upper(), cues_json, now_iso))
                conn.commit()
            finally:
                conn.close()
        return {"status": "success", "subtitle_id": sub_id, "cue_count": len(cues)}

    def get_subtitles(self, lesson_id: str, language: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve subtitle cues for a lesson in specified language."""
        sub_id = f"sub_{lesson_id}_{language.lower()}"
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT cues_json FROM video_subtitles WHERE id = ?", (sub_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row["cues_json"])
            return None
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 345, 346, 347: ACCESSIBILITY PREFERENCES
    # ---------------------------------------------------------------------------

    def save_accessibility_preferences(
        self,
        student_roll: str,
        font_size: int = 16,
        line_spacing: float = 1.6,
        letter_spacing: float = 0.5,
        font_family: str = "system",
        high_contrast_theme: str = "dark_cyber",
        tts_speech_rate: float = 1.0,
        tts_pitch: float = 1.0,
        preferred_language: str = "en-IN",
        screen_reader_verbosity: str = "normal"
    ) -> Dict[str, Any]:
        """Save user accessibility preferences."""
        # Sanitize parameters
        f_size = max(12, min(28, int(font_size)))
        l_spacing = max(1.0, min(2.5, float(line_spacing)))
        lt_spacing = max(0.0, min(3.0, float(letter_spacing)))
        speech_rate = max(0.5, min(2.0, float(tts_speech_rate)))
        speech_pitch = max(0.5, min(2.0, float(tts_pitch)))
        now_iso = datetime.now(timezone.utc).isoformat()

        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO user_accessibility_prefs
                    (student_roll, font_size, line_spacing, letter_spacing, font_family, high_contrast_theme, tts_speech_rate, tts_pitch, preferred_language, screen_reader_verbosity, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (student_roll, f_size, l_spacing, lt_spacing, font_family, high_contrast_theme, speech_rate, speech_pitch, preferred_language, screen_reader_verbosity, now_iso))
                conn.commit()
            finally:
                conn.close()

        return {
            "status": "success",
            "student_roll": student_roll,
            "preferences": {
                "font_size": f_size,
                "line_spacing": l_spacing,
                "letter_spacing": lt_spacing,
                "font_family": font_family,
                "high_contrast_theme": high_contrast_theme,
                "tts_speech_rate": speech_rate,
                "tts_pitch": speech_pitch,
                "preferred_language": preferred_language,
                "screen_reader_verbosity": screen_reader_verbosity
            }
        }

    def get_accessibility_preferences(self, student_roll: str) -> Dict[str, Any]:
        """Retrieve user accessibility preferences, falling back to defaults."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_accessibility_prefs WHERE student_roll = ?", (student_roll,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return {
                "student_roll": student_roll,
                "font_size": 16,
                "line_spacing": 1.6,
                "letter_spacing": 0.5,
                "font_family": "system",
                "high_contrast_theme": "dark_cyber",
                "tts_speech_rate": 1.0,
                "tts_pitch": 1.0,
                "preferred_language": "en-IN",
                "screen_reader_verbosity": "normal"
            }
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 348: ACCESSIBLE MATHEMATICAL FORMULAS
    # ---------------------------------------------------------------------------

    def get_accessible_formulas(self) -> List[Dict[str, Any]]:
        """Retrieve accessible mathematical formulas with screen-reader descriptions."""
        return ACCESSIBLE_FORMULAS

    def get_formula_speech(self, formula_id: str, lang: str = "en") -> Optional[str]:
        """Get accessible speech description for a specific mathematical formula."""
        for f in ACCESSIBLE_FORMULAS:
            if f["id"] == formula_id:
                return f["spoken_ta"] if lang.lower() == "ta" else f["spoken_en"]
        return None
