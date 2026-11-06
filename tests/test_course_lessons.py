"""
========================================================================================
VoltCore Apex Academia - Unit Tests for Unit-Wise Lessons & KaTeX Formulas (Phase 6)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead & Systems Architect: Ashok Kumar A
========================================================================================
"""

import os
import json
import re
import pytest

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LESSONS_FILE_PATH = os.path.join(PROJECT_ROOT, "src", "data", "course_lessons_data.ts")


def extract_ts_registry_text():
    """Helper to read the TypeScript lesson data file."""
    assert os.path.exists(LESSONS_FILE_PATH), f"Lessons file must exist at {LESSONS_FILE_PATH}"
    with open(LESSONS_FILE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def test_lessons_file_exists():
    """Verify that the course lesson data file exists in src/data/."""
    content = extract_ts_registry_text()
    assert len(content) > 1000
    assert "COURSE_LESSONS_REGISTRY" in content


def test_all_priority_courses_present():
    """Verify that all four required priority courses have registered lesson libraries."""
    content = extract_ts_registry_text()
    for code in ["EC23S01", "EC23C03", "EC23E04", "EC8702"]:
        assert f'"{code}": [' in content, f"Course {code} must have a lesson list registered"


def test_units_1_to_5_covered_per_course():
    """Verify that units I, II, III, IV, and V are represented for each priority course."""
    content = extract_ts_registry_text()
    for code in ["EC23S01", "EC23C03", "EC23E04", "EC8702"]:
        for unit_num in [1, 2, 3, 4, 5]:
            pattern = rf'id:\s*"{code}_U{unit_num}_L1"'
            assert re.search(pattern, content) is not None, f"Course {code} must have lesson for Unit {unit_num}"


def test_katex_formula_definitions():
    """Verify that lessons include KaTeX formulas with LaTeX code and parameter variables."""
    content = extract_ts_registry_text()
    # Check key mathematical models
    assert "FORM_CONV_DISCRETE" in content
    assert "FORM_FFT_BUTTERFLY" in content
    assert "FORM_BILINEAR_WARPING" in content
    assert "FORM_SHOCKLEY_DIODE" in content
    assert "FORM_MASS_ACTION" in content
    assert "FORM_RESONATOR_STABILITY" in content
    assert "FORM_RMS_BOUND" in content
    assert "FORM_NVIC_LATENCY" in content


def test_markdown_lecture_notes_rigor():
    """Verify that markdown lecture notes contain structured markdown headers and derivations."""
    content = extract_ts_registry_text()
    assert "markdownNotes:" in content
    assert "### 1." in content
    assert "### 2." in content
    assert "### 3." in content


def test_anna_university_exam_significance():
    """Verify that KaTeX formulas include Anna University Regulation 2023 exam significance."""
    content = extract_ts_registry_text()
    assert "High (Part B 16-Mark Derivation)" in content
    assert "Essential (Part A 2-Mark Question)" in content
    assert "Medium (Part B 8-Mark Problem)" in content
