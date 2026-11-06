"""
========================================================================================
VoltCore Apex Academia - Phase 40 Test Suite
Module: ECE Capstone Portfolio & Viva-Voce Examination Engine Tests
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
========================================================================================
"""

import os
import sqlite3
import json
import pytest
from backend.capstone_portfolio_engine import (
    CapstonePortfolioEngine,
    VIVA_QUESTION_BANK,
    CAPSTONE_CLUSTERS,
    capstone_portfolio_engine
)


def test_wal_initialization_and_schema(tmp_path):
    """Verifies SQLite tables and WAL mode are initialized correctly."""
    db_file = str(tmp_path / "test_capstone_init.db")
    engine = CapstonePortfolioEngine(db_path=db_file)
    conn = engine._get_connection()
    cursor = conn.cursor()

    # Verify journal mode is WAL
    journal_mode = cursor.execute("PRAGMA journal_mode;").fetchone()[0]
    assert journal_mode.upper() == "WAL"

    # Verify tables exist
    tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    assert "capstone_portfolios" in tables
    assert "viva_evaluations" in tables
    conn.close()


def test_viva_question_bank_catalog(tmp_path):
    """Verifies technical question bank covers all 6 required ECE domains."""
    db_file = str(tmp_path / "test_capstone_bank.db")
    engine = CapstonePortfolioEngine(db_path=db_file)
    questions = engine.get_viva_question_bank()

    assert len(questions) >= 10
    domains = set(q["domain"] for q in questions)
    assert "ANALOG_DESIGN" in domains
    assert "DIGITAL_VLSI" in domains
    assert "EMBEDDED_RTOS" in domains
    assert "PERIPHERAL_BUS" in domains
    assert "TINYML_EDGE" in domains
    assert "IOT_MQTT_HIL" in domains

    for q in questions:
        assert len(q["key_rubrics"]) >= 2
        assert len(q["model_answer"]) > 20
        assert "AU R2023" in q["syllabus_ref"]


def test_viva_response_evaluation_logic(tmp_path):
    """Verifies student answer evaluation, rubric matching, and scoring."""
    db_file = str(tmp_path / "test_capstone_eval.db")
    engine = CapstonePortfolioEngine(db_path=db_file)

    # Test high-scoring answer containing key rubrics
    high_score_res = engine.evaluate_viva_response(
        question_id="VIVA_ANA_01",
        student_response="The compensation capacitor causes pole splitting where the dominant pole shift moves to low frequency, ensuring phase margin >60 deg and stability."
    )
    assert high_score_res["score_awarded"] >= 9.0
    assert len(high_score_res["matched_rubrics"]) >= 3
    assert "Outstanding" in high_score_res["evaluator_feedback"]

    # Test low-scoring response with no matching rubrics
    low_score_res = engine.evaluate_viva_response(
        question_id="VIVA_ANA_01",
        student_response="It connects a capacitor."
    )
    assert low_score_res["score_awarded"] <= 7.0


def test_capstone_portfolio_generation(tmp_path):
    """Verifies capstone portfolio compilation, Anna University grading, and cluster summary."""
    db_file = str(tmp_path / "test_capstone_gen.db")
    engine = CapstonePortfolioEngine(db_path=db_file)

    portfolio = engine.generate_capstone_portfolio(
        student_id="2023MITEC042",
        student_name="Ashok Kumar A",
        roll_no="2023MITEC042",
        viva_score_pct=95.5
    )

    assert portfolio["student_name"] == "Ashok Kumar A"
    assert portfolio["roll_no"] == "2023MITEC042"
    assert portfolio["cumulative_phases"] == 40
    assert portfolio["total_unit_tests"] == 417
    assert portfolio["total_static_routes"] == 39
    assert portfolio["final_grade"] == "O (Outstanding)"
    assert len(portfolio["clusters"]) == 6


def test_viva_evaluations_persistence(tmp_path):
    """Verifies that individual viva question evaluations are persisted to SQLite WAL."""
    db_file = str(tmp_path / "test_capstone_eval_persist.db")
    engine = CapstonePortfolioEngine(db_path=db_file)

    eval_items = [
        {
            "domain": "ANALOG_DESIGN",
            "question_id": "VIVA_ANA_01",
            "question_text": "Op-Amp Miller Frequency Compensation",
            "student_response": "Miller pole splitting shifts dominant pole and stabilizes phase margin.",
            "score_awarded": 9.5,
            "max_score": 10.0,
            "evaluator_feedback": "Excellent response"
        },
        {
            "domain": "TINYML_EDGE",
            "question_id": "VIVA_TML_01",
            "question_text": "Symmetric INT8 Quantization",
            "student_response": "Quantization maps FP32 to 8-bit ints with symmetric zero point Z=0.",
            "score_awarded": 9.8,
            "max_score": 10.0,
            "evaluator_feedback": "Flawless formulation"
        }
    ]

    portfolio = engine.generate_capstone_portfolio(
        student_id="2023MITEC042",
        viva_score_pct=96.5,
        evaluations=eval_items
    )

    with engine._get_connection() as conn:
        rows = conn.execute("SELECT * FROM viva_evaluations WHERE portfolio_id = ?;", (portfolio["portfolio_id"],)).fetchall()
        assert len(rows) == 2
        assert rows[0]["domain"] in ["ANALOG_DESIGN", "TINYML_EDGE"]


def test_portfolio_history_and_json_export(tmp_path):
    """Verifies portfolio history retrieval and valid JSON export."""
    db_file = str(tmp_path / "test_capstone_export.db")
    engine = CapstonePortfolioEngine(db_path=db_file)

    p1 = engine.generate_capstone_portfolio(student_id="2023MITEC042", viva_score_pct=94.0)
    history = engine.get_portfolio_history(limit=5)
    assert len(history) == 1

    json_str = engine.export_portfolio_json(portfolio_id=p1["portfolio_id"])
    parsed = json.loads(json_str)
    assert parsed["portfolio_id"] == p1["portfolio_id"]
    assert parsed["cumulative_phases"] == 40


def test_portfolio_ieee_markdown_export(tmp_path):
    """Verifies IEEE-standard technical report markdown generation."""
    db_file = str(tmp_path / "test_capstone_md.db")
    engine = CapstonePortfolioEngine(db_path=db_file)

    p = engine.generate_capstone_portfolio(student_id="2023MITEC042", viva_score_pct=97.0)
    md_str = engine.export_portfolio_ieee_markdown(portfolio_id=p["portfolio_id"])

    assert "# VoltCore Apex Academia" in md_str
    assert "Ashok Kumar A" in md_str
    assert "2023MITEC042" in md_str
    assert "Regulation 2023" in md_str
    assert "O (Outstanding)" in md_str
    assert "CLUSTER_1" in md_str
    assert "CLUSTER_6" in md_str


def test_privacy_invariants_and_attribution():
    """Strictly verifies zero leakage of private credentials and confirms public author attribution."""
    with open("backend/capstone_portfolio_engine.py", "r", encoding="utf-8") as f:
        code_str = f.read()

    # Zero leakage
    assert "9597382878" not in code_str
    assert "ashokkumar2008313@gmail.com" not in code_str

    # Public attribution
    assert "Ashok Kumar A" in code_str
    assert "2023MITEC042" in code_str
    assert "Anna University" in code_str

