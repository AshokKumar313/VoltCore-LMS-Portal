"""
========================================================================================
VoltCore Apex Academia - Phase A Test Suite: Personalized Learning Hub
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU usage.
========================================================================================
"""

import os
import pytest
import sqlite3
from backend.personalized_learning_engine import (
    PersonalizedLearningEngine,
    ECE_DOMAINS,
    CAREER_TRACKS
)


@pytest.fixture
def engine(tmp_path):
    """Instantiate PersonalizedLearningEngine with an isolated temporary SQLite WAL database."""
    db_file = str(tmp_path / "test_personalized_learning.db")
    return PersonalizedLearningEngine(db_path=db_file)


def test_database_wal_mode_and_tables(engine):
    """Verify that the engine initializes SQLite tables with WAL journal mode enabled."""
    conn = sqlite3.connect(engine.db_path)
    try:
        cur = conn.execute("PRAGMA journal_mode;")
        mode = cur.fetchone()[0]
        assert mode.lower() == "wal", f"Expected WAL mode, got {mode}"

        cur = conn.execute("""
            SELECT name FROM sqlite_master WHERE type='table'
            AND name IN ('student_learning_profiles', 'adaptive_quiz_attempts', 'adaptive_learning_recommendations');
        """)
        tables = {row[0] for row in cur.fetchall()}
        assert "student_learning_profiles" in tables
        assert "adaptive_quiz_attempts" in tables
        assert "adaptive_learning_recommendations" in tables
    finally:
        conn.close()


def test_get_student_profile(engine):
    """Verify default student profile attributes for Ashok Kumar A."""
    profile = engine.get_student_profile("2023MITEC042")
    assert profile["student_id"] == "2023MITEC042"
    assert profile["student_name"] == "Ashok Kumar A"
    assert "Department of Electronics Engineering" in profile["department"]
    assert profile["target_career"] in CAREER_TRACKS
    assert profile["study_streak_days"] >= 0
    assert profile["total_xp"] > 0


def test_update_target_career(engine):
    """Verify updating student career goal dynamically (Feature 202)."""
    res = engine.update_target_career("2023MITEC042", "gate_ece_top_ranker")
    assert res["status"] == "success"
    assert res["target_career"] == "gate_ece_top_ranker"
    assert "IISc Bangalore" in res["career_info"]["target_companies"]

    updated = engine.get_student_profile("2023MITEC042")
    assert updated["target_career"] == "gate_ece_top_ranker"

    # Invalid career raises ValueError
    with pytest.raises(ValueError):
        engine.update_target_career("2023MITEC042", "non_existent_career")


def test_calculate_domain_mastery_baseline(engine):
    """Verify domain mastery calculation across all 5 Anna University ECE domains."""
    mastery = engine.calculate_domain_mastery("2023MITEC042")
    assert len(mastery) == len(ECE_DOMAINS)

    domain_ids = {d["domain_id"] for d in mastery}
    assert "embedded_rtos" in domain_ids
    assert "digital_vlsi" in domain_ids
    assert "analog_rf" in domain_ids
    assert "tinyml_edge" in domain_ids
    assert "iot_bus" in domain_ids

    for d in mastery:
        assert 0.0 <= d["mastery_percentage"] <= 100.0
        assert d["status"] in ["Advanced", "Proficient", "Needs Review"]
        assert len(d["topics"]) > 0


def test_log_quiz_attempt_and_mastery_update(engine):
    """Verify that logging a diagnostic quiz updates the domain mastery score."""
    # Log a high score quiz in digital_vlsi
    attempt = engine.log_quiz_attempt(
        student_id="2023MITEC042",
        domain_id="digital_vlsi",
        quiz_title="Quine-McCluskey & Timing Quiz",
        score=9.5,
        max_score=10.0,
        weak_topics=["Clock Domain Crossing"]
    )
    assert attempt["status"] == "logged"
    assert attempt["percentage"] == 95.0

    # Domain mastery should now reflect the quiz result
    mastery = engine.calculate_domain_mastery("2023MITEC042")
    vlsi = next(d for d in mastery if d["domain_id"] == "digital_vlsi")
    assert vlsi["attempts_count"] >= 1

    # Zero or negative max score raises ValueError
    with pytest.raises(ValueError):
        engine.log_quiz_attempt("2023MITEC042", "digital_vlsi", "Bad Quiz", 5, 0, [])


def test_detect_cognitive_gaps(engine):
    """Verify that cognitive gaps and urgency levels are properly identified."""
    gaps = engine.detect_cognitive_gaps("2023MITEC042")
    assert isinstance(gaps, list)
    assert len(gaps) > 0

    for g in gaps:
        assert "domain_id" in g
        assert "urgency" in g
        assert g["urgency"] in ["High", "Medium"]
        assert "focus_topic" in g
        assert "recommendation" in g


def test_generate_adaptive_learning_path(engine):
    """Verify dynamic recommendation of next milestones based on career track."""
    path = engine.generate_adaptive_learning_path("2023MITEC042")
    assert path["student_id"] == "2023MITEC042"
    assert "career_title" in path
    assert "target_companies" in path
    assert "next_recommended_action" in path

    rec = path["next_recommended_action"]
    assert "milestone_id" in rec
    assert "title" in rec
    assert "domain" in rec
    assert "reason" in rec

    milestones = path["milestone_path"]
    assert len(milestones) > 0
    statuses = {m["status"] for m in milestones}
    assert any(s in ["Completed", "Recommended Next", "Locked (Prerequisite Required)"] for s in statuses)
