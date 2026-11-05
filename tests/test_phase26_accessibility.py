"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 26 (Accessibility & Inclusive Learning)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase26_accessibility.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import sys
import json
import sqlite3
import pytest

# Ensure repository root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.accessibility_engine import (
    AccessibilityEngine,
    accessibility_engine,
    DEFAULT_STUDENT_ID,
    MULTILINGUAL_DICTIONARY_CATALOG,
    CONCEPT_SIMPLIFICATIONS_CATALOG
)


@pytest.fixture
def test_engine(tmp_path):
    """Provides an isolated AccessibilityEngine backed by a temporary SQLite WAL DB."""
    db_file = str(tmp_path / "test_accessibility.db")
    engine = AccessibilityEngine(db_path=db_file)
    return engine


def test_accessibility_engine_initialization(test_engine):
    """Verifies table creation, SQLite WAL mode, and multilingual dictionary seeding."""
    conn = test_engine._get_connection()
    try:
        cur = conn.execute("PRAGMA journal_mode;")
        journal_mode = cur.fetchone()[0].upper()
        assert journal_mode == "WAL", f"Expected WAL mode, got {journal_mode}"

        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        assert "user_accessibility_preferences" in tables
        assert "multilingual_ece_dictionary" in tables
        assert "concept_simplifications" in tables
        assert "accessibility_feedback" in tables

        cur = conn.execute("SELECT COUNT(*) FROM multilingual_ece_dictionary;")
        assert cur.fetchone()[0] >= len(MULTILINGUAL_DICTIONARY_CATALOG)

        cur = conn.execute("SELECT COUNT(*) FROM concept_simplifications;")
        assert cur.fetchone()[0] >= len(CONCEPT_SIMPLIFICATIONS_CATALOG)
    finally:
        conn.close()


def test_get_overview_metrics(test_engine):
    """Tests overview statistics, language counts, and preference delivery."""
    overview = test_engine.get_overview(DEFAULT_STUDENT_ID)
    assert overview["status"] == "SUCCESS"
    assert overview["user_id"] == DEFAULT_STUDENT_ID
    assert "metrics" in overview
    assert "current_preferences" in overview

    metrics = overview["metrics"]
    assert metrics["dictionary_terms_count"] >= 12
    assert metrics["concept_simplifications_count"] >= 5
    assert metrics["curriculum_categories_count"] >= 4
    assert metrics["tts_supported"] is True

    # Check supported bilingual languages
    langs = [l["code"] for l in overview["supported_languages"]]
    assert "en" in langs
    assert "ta" in langs


def test_multilingual_dictionary_search_and_filter(test_engine):
    """Validates English and Tamil term retrieval, phonetic matching, and category filters."""
    # 1. Search English term
    results_en = test_engine.get_dictionary(query="Amplifier")
    assert len(results_en) >= 1
    opamp = next(r for r in results_en if "Op-Amp" in r["term_en"])
    assert opamp["term_ta"] == "செயற்பாட்டு பெருக்கி"
    assert "Seyarpaattu Perukki" in opamp["phonetic_ta"]

    # 2. Search Tamil term
    results_ta = test_engine.get_dictionary(query="பண்பேற்றம்")
    assert len(results_ta) >= 1
    assert any("Modulation" in r["term_en"] for r in results_ta)

    # 3. Search Phonetic transliteration
    results_phonetic = test_engine.get_dictionary(query="Panpirakkam")
    assert len(results_phonetic) >= 1
    assert any("Demodulation" in r["term_en"] for r in results_phonetic)

    # 4. Filter by course code
    results_course = test_engine.get_dictionary(course_code="EC3451")
    assert len(results_course) >= 3
    for r in results_course:
        assert r["course_code"] == "EC3451"

    # 5. Filter by category
    results_cat = test_engine.get_dictionary(category="Digital Electronics")
    assert len(results_cat) >= 2
    for r in results_cat:
        assert r["category"] == "Digital Electronics"


def test_concept_simplification_analogies(test_engine):
    """Validates plain-English concept analogies, formal definitions, and takeaways."""
    # Slew rate truck speed limit analogy
    sr = test_engine.get_simplification("slew_rate")
    assert sr is not None
    assert "Speed Limit" in sr["title"]
    assert "truck" in sr["simplified_analogy"].lower()
    assert "pi" in sr["key_takeaway"].lower()
    assert sr["diagram_ascii"] is not None

    # Bandwidth highway analogy
    bw = test_engine.get_simplification("bandwidth")
    assert bw is not None
    assert "Highway" in bw["title"]
    assert "lane" in bw["simplified_analogy"].lower()

    # Nyquist sampling cinema strobe analogy
    nyq = test_engine.get_simplification("sampling_theorem")
    assert nyq is not None
    assert "Cinema Strobe" in nyq["title"]
    assert "aliasing" in nyq["simplified_analogy"].lower()

    # Non-existent concept returns None
    missing = test_engine.get_simplification("quantum_teleportation")
    assert missing is None


def test_user_accessibility_preferences_crud(test_engine):
    """Validates user preference persistence, font scale clamping, and contrast modes."""
    new_prefs = {
        "font_scale": 1.35,
        "contrast_mode": "high-contrast",
        "dyslexia_font": True,
        "tts_speech_rate": 1.2,
        "preferred_language": "ta",
        "screen_reader_optimizations": True
    }

    save_res = test_engine.save_preferences(DEFAULT_STUDENT_ID, new_prefs)
    assert save_res["status"] == "SUCCESS"
    assert save_res["preferences"]["font_scale"] == 1.35
    assert save_res["preferences"]["contrast_mode"] == "high-contrast"
    assert save_res["preferences"]["dyslexia_font"] is True
    assert save_res["preferences"]["preferred_language"] == "ta"

    # Verify retrieval
    retrieved = test_engine.get_preferences(DEFAULT_STUDENT_ID)
    assert retrieved["font_scale"] == 1.35
    assert retrieved["contrast_mode"] == "high-contrast"
    assert retrieved["dyslexia_font"] is True
    assert retrieved["preferred_language"] == "ta"

    # Edge case: scale out of bounds clamped to [0.7, 2.0]
    out_of_bounds = {"font_scale": 5.0, "contrast_mode": "invalid_mode"}
    clamp_res = test_engine.save_preferences(DEFAULT_STUDENT_ID, out_of_bounds)
    assert clamp_res["preferences"]["font_scale"] == 2.0
    assert clamp_res["preferences"]["contrast_mode"] == "dark"


def test_accessibility_feedback_recording(test_engine):
    """Validates recording of user accessibility improvement suggestions."""
    feedback_payload = {
        "user_id": DEFAULT_STUDENT_ID,
        "category": "TRANSLATION",
        "message": "Requesting Tamil translation for 'Phase-Locked Loop (PLL)'.",
        "suggested_term": "Phase-Locked Loop"
    }

    res = test_engine.record_feedback(feedback_payload)
    assert res["status"] == "SUCCESS"
    assert "feedback_id" in res

    # Empty message should fail
    empty_res = test_engine.record_feedback({"user_id": DEFAULT_STUDENT_ID, "message": ""})
    assert empty_res["status"] == "ERROR"
    assert "cannot be empty" in empty_res["message"]


def test_privacy_invariants_no_credential_leakage():
    """Guarantees zero client-side or repository leakage of private admin credentials."""
    forbidden_tokens = ["ashokkumar2008313@gmail.com", "9597382878"]
    target_files = [
        os.path.join(BASE_DIR, "backend", "accessibility_engine.py"),
        os.path.join(BASE_DIR, "src", "components", "AccessibilityHub.jsx"),
        os.path.join(BASE_DIR, "src", "pages", "accessibility.astro")
    ]

    for fpath in target_files:
        assert os.path.exists(fpath), f"File {fpath} does not exist"
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            for token in forbidden_tokens:
                assert token not in content, f"SECURITY ALERT: Private token '{token}' leaked in {fpath}"
