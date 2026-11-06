"""
========================================================================================
VoltCore Apex Academia - Unit Tests for Phase N: Accessibility & Multilingual Learning
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
========================================================================================
"""

import os
import pytest
import tempfile
from backend.accessibility_multilingual_engine import (
    AccessibilityMultilingualEngine,
    ECE_DICTIONARY,
    CONCEPT_EXPLANATIONS,
    ACCESSIBLE_FORMULAS
)

@pytest.fixture
def temp_engine():
    """Create an isolated temporary SQLite database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = AccessibilityMultilingualEngine(db_path=path)
    yield engine
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def test_dictionary_lookup_english_and_tamil(temp_engine):
    """Feature 341: English-Tamil Technical Dictionary lookups."""
    # Lookup in English
    semi = temp_engine.lookup_term("semiconductor")
    assert semi is not None
    assert semi["term_ta"] == "குறைகடத்தி"
    assert semi["transliteration"] == "Kuraikadathi"
    assert "doping" in semi["definition_en"].lower()

    # Lookup in Tamil script
    diode = temp_engine.lookup_term("இருமுனையம்")
    assert diode is not None
    assert diode["term_en"] == "Diode"
    assert "one-way" in diode["simplified_en"].lower()

    # Lookup via transliteration
    cap = temp_engine.lookup_term("Minthekki")
    assert cap is not None
    assert cap["term_en"] == "Capacitor"


def test_custom_dictionary_addition(temp_engine):
    """Feature 341: Custom student-contributed technical terms."""
    res = temp_engine.add_custom_term(
        term_en="Phase Locked Loop",
        term_ta="கட்டப் பூட்டு வளையம்",
        transliteration="Kattap Poottu Valaiyam",
        phonetic="/kʌ-tʌp-puːt-tʊ/",
        subject_code="EC3451",
        definition_en="A control system that generates an output signal whose phase is related to the phase of an input signal.",
        definition_ta="உள்ளீட்டு சமிக்ஞையின் கட்டத்திற்கு ஏற்ப வெளியீட்டு சமிக்ஞையின் கட்டத்தை ஒத்திசைக்கும் ஒரு கட்டுப்பாட்டு அமைப்பு.",
        simplified_en="A synchronization lock that keeps two signals dancing at the exact same beat.",
        simplified_ta="இரு அலைகளை ஒரே தாளத்தில் துல்லியமாக ஆட வைக்கும் மின்னணு பூட்டு.",
        contributor_roll="2023MITEC042"
    )
    assert res["status"] == "success"

    # Query custom term in English and Tamil
    found = temp_engine.lookup_term("Phase Locked Loop")
    assert found is not None
    assert found["term_ta"] == "கட்டப் பூட்டு வளையம்"

    found_ta = temp_engine.lookup_term("கட்டப் பூட்டு வளையம்")
    assert found_ta is not None
    assert found_ta["term_en"] == "Phase Locked Loop"


def test_concept_explanation_bilingual(temp_engine):
    """Feature 342 & 349: Tamil Concept Explanation Library and ELI5 analogies."""
    concept = temp_engine.get_concept_explanation("pn_junction")
    assert concept is not None
    assert "பி-என் சந்தி" in concept["title_ta"]
    assert "0.7V" in concept["english_summary"]
    assert len(concept["spoken_script_ta"]) > 20
    assert "கதவு" in concept["eli5_ta"] # check ELI5 door analogy

    all_concepts = temp_engine.list_all_concepts()
    assert len(all_concepts) >= 3


def test_accessible_math_formulas(temp_engine):
    """Feature 348: Accessible Mathematical Formulas (LaTeX, MathML & Speech strings)."""
    formulas = temp_engine.get_accessible_formulas()
    assert len(formulas) >= 4

    ohm = next(f for f in formulas if f["id"] == "ohm_law")
    assert ohm["latex"] == "V = I \\times R"
    assert "<math>" in ohm["mathml"]
    assert "Voltage V equals electric current" in ohm["spoken_en"]
    assert "மின்னழுத்தம் V சமம்" in ohm["spoken_ta"]

    nyquist = next(f for f in formulas if f["id"] == "nyquist_formula")
    assert "two times" in nyquist["spoken_en"]
    assert "இரண்டு மடங்கு" in nyquist["spoken_ta"]


def test_multilingual_search_cross_lingual(temp_engine):
    """Feature 350: Multilingual search cross-matching English & Tamil."""
    # Search in Tamil script for sampling
    res_ta = temp_engine.search_multilingual("மாதிரி")
    assert len(res_ta) > 0
    match_terms = [r["data"].get("term_en", "") or r["data"].get("title_en", "") for r in res_ta]
    assert any("Sampling" in t for t in match_terms)

    # Search in English for modulation
    res_en = temp_engine.search_multilingual("modulation")
    assert len(res_en) > 0
    assert any(r["data"].get("term_ta") == "பண்பேற்றம்" for r in res_en if r["type"] == "dictionary")


def test_vtt_subtitle_parser_and_storage(temp_engine):
    """Feature 344: WebVTT Subtitle parser and persistent cue storage."""
    vtt_data = """WEBVTT

00:00:01.000 --> 00:00:04.500
Welcome to VoltCore Apex Academia Lecture 4.

00:00:05.000 --> 00:00:09.200
Today we examine the inverting operational amplifier circuit.
"""
    cues = temp_engine.parse_vtt_subtitles(vtt_data)
    assert len(cues) == 2
    assert cues[0]["start"] == "00:00:01.000"
    assert "VoltCore" in cues[0]["text"]
    assert cues[1]["end"] == "00:00:09.200"

    # Save and retrieve from DB
    temp_engine.save_subtitles("lesson_opamp_01", "en", cues)
    retrieved = temp_engine.get_subtitles("lesson_opamp_01", "en")
    assert retrieved is not None
    assert len(retrieved) == 2
    assert retrieved[1]["text"] == "Today we examine the inverting operational amplifier circuit."


def test_accessibility_preferences_persistence(temp_engine):
    """Features 345, 346, 347: User Accessibility Preferences & Clamping."""
    # Test custom preferences with value clamping
    save_res = temp_engine.save_accessibility_preferences(
        student_roll="2023MITEC042",
        font_size=40, # should clamp to 28
        line_spacing=0.5, # should clamp to 1.0
        letter_spacing=1.2,
        font_family="opendyslexic",
        high_contrast_theme="navy_yellow",
        tts_speech_rate=1.2,
        tts_pitch=0.9,
        preferred_language="ta-IN",
        screen_reader_verbosity="detailed"
    )
    assert save_res["status"] == "success"
    assert save_res["preferences"]["font_size"] == 28
    assert save_res["preferences"]["line_spacing"] == 1.0
    assert save_res["preferences"]["font_family"] == "opendyslexic"

    prefs = temp_engine.get_accessibility_preferences("2023MITEC042")
    assert prefs["high_contrast_theme"] == "navy_yellow"
    assert prefs["preferred_language"] == "ta-IN"

    # Test defaults for unregistered student
    default_prefs = temp_engine.get_accessibility_preferences("2023MITEC999")
    assert default_prefs["font_size"] == 16
    assert default_prefs["high_contrast_theme"] == "dark_cyber"


def test_formula_speech_retrieval(temp_engine):
    """Feature 348: Formula speech string retrieval."""
    speech_en = temp_engine.get_formula_speech("inverting_gain", lang="en")
    assert "Output voltage V out" in speech_en

    speech_ta = temp_engine.get_formula_speech("inverting_gain", lang="ta")
    assert "வெளியீட்டு மின்னழுத்தம்" in speech_ta

    # Unknown formula returns None
    assert temp_engine.get_formula_speech("unknown_formula") is None
