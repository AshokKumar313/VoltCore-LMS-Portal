"""
========================================================================================
VoltCore Apex Academia - Advanced ECE Knowledge Center Test Suite (Phase 20)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: tests/test_phase20_ece_knowledge.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Rapid, low-overhead pytest suite validating:
    1. EceKnowledgeEngine initialization and SQLite WAL schema integrity.
    2. Formula query filtering across Anna University ECE core subjects.
    3. Component datasheet retrieval and key electrical specifications.
    4. Technical abbreviation glossary lookups and category mapping.
    5. Strict RBAC permission enforcement on custom formula additions.
    6. REST API endpoints in attendance_server for knowledge operations.
    7. Strict zero-leakage privacy invariants.
========================================================================================
"""

import os
import json
import pytest
from typing import Dict, Any

from backend.ece_knowledge_engine import EceKnowledgeEngine, ece_knowledge_engine


def test_ece_knowledge_engine_initialization(tmp_path):
    """Verify engine initializes schema and seeds default formulas, components, and abbreviations in WAL mode."""
    test_db = str(tmp_path / "test_knowledge.db")
    engine = EceKnowledgeEngine(db_path=test_db)

    overview = engine.get_knowledge_overview()
    assert overview["status"] == "OPERATIONAL"
    assert "MIT" in overview["campus"]
    assert overview["total_formulas"] >= 15
    assert overview["total_components"] >= 8
    assert overview["total_abbreviations"] >= 14
    assert overview["total_subjects_covered"] == 4


def test_formula_search_and_subject_filtering():
    """Verify searching formulas by keyword, Anna University subject code, and unit number."""
    engine = ece_knowledge_engine

    # 1. Subject code filter: EC3452 (Electromagnetic Fields)
    emf_formulas = engine.search_formulas(subject_code="EC3452")
    assert len(emf_formulas) >= 4
    for f in emf_formulas:
        assert f["subject_code"] == "EC3452"
        assert "EC3452" in f["au_regulation"]
        assert len(f["latex_repr"]) > 0
        assert isinstance(f["variables"], dict)

    # 2. Keyword query: "Nyquist"
    nyquist_res = engine.search_formulas(query="Nyquist")
    assert len(nyquist_res) >= 1
    assert any("Nyquist" in f["formula_name"] for f in nyquist_res)

    # 3. Keyword query: "CMRR"
    cmrr_res = engine.search_formulas(query="CMRR")
    assert len(cmrr_res) >= 1
    assert any("CMRR" in f["formula_name"] for f in cmrr_res)

    # 4. Unit filter: Unit 1 of EC3352
    u1_res = engine.search_formulas(subject_code="EC3352", unit_number=1)
    assert len(u1_res) >= 2
    for f in u1_res:
        assert f["unit_number"] == 1


def test_component_datasheet_retrieval():
    """Verify component datasheet search by category, part number, and manufacturer."""
    engine = ece_knowledge_engine

    # 1. Filter by MICROCONTROLLER category
    mcus = engine.search_components(category="MICROCONTROLLER")
    assert len(mcus) >= 2
    parts = [m["part_number"] for m in mcus]
    assert "ESP32-S3-WROOM-1" in parts
    assert "STM32F407VGT6" in parts

    # 2. Query specific part: LM741
    opamps = engine.search_components(query="741")
    assert len(opamps) >= 1
    lm741 = opamps[0]
    assert "LM741" in lm741["part_number"]
    assert lm741["category"] == "OPAMP"
    assert "Unity Gain Bandwidth" in lm741["key_specs"]
    assert lm741["pin_count"] == 8

    # 3. Query instrument: Oscilloscope
    scopes = engine.search_components(query="Oscilloscope")
    assert len(scopes) >= 1
    assert "Keysight" in scopes[0]["manufacturer"]


def test_abbreviation_dictionary_lookups():
    """Verify technical abbreviation dictionary lookups and category mappings."""
    engine = ece_knowledge_engine

    # Search by term: CMRR
    cmrr_abbr = engine.search_abbreviations(query="CMRR")
    assert len(cmrr_abbr) >= 1
    assert cmrr_abbr[0]["term"] == "CMRR"
    assert cmrr_abbr[0]["full_form"] == "Common-Mode Rejection Ratio"
    assert cmrr_abbr[0]["related_subject"] == "EC3451"

    # Search by category: COMMUNICATION
    comm_abbrs = engine.search_abbreviations(category="COMMUNICATION")
    terms = [a["term"] for a in comm_abbrs]
    assert "PLL" in terms or "AWGN" in terms or "BER" in terms


def test_custom_formula_addition_rbac():
    """Verify strict RBAC barriers when adding custom formulas to the encyclopedia."""
    engine = ece_knowledge_engine

    # Faculty permitted
    fac_res = engine.add_custom_formula(
        topic="RF Filters",
        formula_name="Butterworth Low-Pass Pole Locations",
        subject_code="EC3451",
        unit_number=2,
        latex_repr="s_k = \\omega_c \\exp\\left(j \\frac{2k + n - 1}{2n}\\pi\\right)",
        plain_text="s_k = omega_c * exp(j * (2k + n - 1) * pi / (2n))",
        derivation_summary="Maximally flat magnitude filter pole distribution along Butterworth semicircle.",
        variables={"s_k": "Complex frequency pole location", "omega_c": "Cutoff frequency", "n": "Filter order"},
        unit_result="rad / s",
        actor_role="Faculty"
    )
    assert fac_res["status"] == "SUCCESS"
    assert "FORM_" in fac_res["formula_id"]

    # Student forbidden
    stu_res = engine.add_custom_formula(
        topic="Unauthorized Formula",
        formula_name="Bogus Equation",
        subject_code="EC3352",
        unit_number=1,
        latex_repr="X = Y",
        plain_text="X = Y",
        derivation_summary="Unauthorized entry.",
        variables={"X": "Test"},
        unit_result="Unitless",
        actor_role="Student"
    )
    assert stu_res["status"] == "FORBIDDEN"
    assert "lacks permission" in stu_res["message"]


def test_attendance_server_ece_knowledge_endpoints():
    """Verify REST API endpoints in attendance_server for ECE knowledge center."""
    import attendance_server

    if hasattr(attendance_server, "app") and attendance_server.app:
        client = attendance_server.app.test_client()

        # 1. GET /api/ece_knowledge/formulas
        f_resp = client.get("/api/ece_knowledge/formulas?subject_code=EC3452")
        assert f_resp.status_code == 200
        f_data = json.loads(f_resp.data)
        assert isinstance(f_data, list)
        assert len(f_data) >= 4

        # 2. GET /api/ece_knowledge/components
        c_resp = client.get("/api/ece_knowledge/components?category=MICROCONTROLLER")
        assert c_resp.status_code == 200
        c_data = json.loads(c_resp.data)
        assert isinstance(c_data, list)
        assert len(c_data) >= 2

        # 3. GET /api/ece_knowledge/abbreviations
        a_resp = client.get("/api/ece_knowledge/abbreviations?query=CMRR")
        assert a_resp.status_code == 200
        a_data = json.loads(a_resp.data)
        assert len(a_data) >= 1
        assert a_data[0]["term"] == "CMRR"

        # 4. GET /api/ece_knowledge/overview
        ov_resp = client.get("/api/ece_knowledge/overview")
        assert ov_resp.status_code == 200
        ov_data = json.loads(ov_resp.data)
        assert ov_data["status"] == "OPERATIONAL"


def test_privacy_invariants_no_leakage():
    """Verify restricted private administrator credentials are never exposed."""
    p_email = "".join(["ashok", "kumar", "2008313", "@", "gmail.com"])
    p_phone = "".join(["95973", "82878"])
    restricted_patterns = [p_email, p_phone]

    files_to_check = [
        os.path.join(os.path.dirname(__file__), "..", "backend", "ece_knowledge_engine.py"),
        os.path.join(os.path.dirname(__file__), "..", "src", "components", "EceKnowledgeHub.jsx"),
        os.path.join(os.path.dirname(__file__), "..", "src", "pages", "ece-knowledge.astro")
    ]

    for fpath in files_to_check:
        assert os.path.exists(fpath), f"File {fpath} must exist"
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            for pattern in restricted_patterns:
                assert pattern not in content, f"Restricted metadata leaked in {fpath}!"
