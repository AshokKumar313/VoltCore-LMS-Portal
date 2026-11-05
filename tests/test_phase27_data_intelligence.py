"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 27 (Data Intelligence & Academic Quality)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase27_data_intelligence.py
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

from backend.data_intelligence_engine import (
    DataIntelligenceEngine,
    data_intelligence_engine,
    DEFAULT_STUDENT_ID,
    SYLLABUS_METRICS_CATALOG,
    INITIAL_AUDITS_CATALOG,
    QUESTION_BANK_GAPS_CATALOG,
    CONTENT_FRESHNESS_CATALOG,
    DOCUMENT_DUPLICATES_CATALOG
)


@pytest.fixture
def test_engine(tmp_path):
    """Provides an isolated DataIntelligenceEngine backed by a temporary SQLite WAL DB."""
    db_file = str(tmp_path / "test_data_intelligence.db")
    engine = DataIntelligenceEngine(db_path=db_file)
    return engine


def test_data_intelligence_engine_initialization(test_engine):
    """Verifies table creation, SQLite WAL mode, and initial data seeding."""
    conn = test_engine._get_connection()
    try:
        cur = conn.execute("PRAGMA journal_mode;")
        journal_mode = cur.fetchone()[0].upper()
        assert journal_mode == "WAL", f"Expected WAL mode, got {journal_mode}"

        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        assert "academic_quality_audits" in tables
        assert "syllabus_coverage_metrics" in tables
        assert "question_bank_gaps" in tables
        assert "content_freshness_logs" in tables
        assert "document_duplicates" in tables

        cur = conn.execute("SELECT COUNT(*) FROM syllabus_coverage_metrics;")
        assert cur.fetchone()[0] >= len(SYLLABUS_METRICS_CATALOG)

        cur = conn.execute("SELECT COUNT(*) FROM academic_quality_audits;")
        assert cur.fetchone()[0] >= len(INITIAL_AUDITS_CATALOG)

        cur = conn.execute("SELECT COUNT(*) FROM question_bank_gaps;")
        assert cur.fetchone()[0] >= len(QUESTION_BANK_GAPS_CATALOG)
    finally:
        conn.close()


def test_overview_metrics_calculation(test_engine):
    """Validates the multi-dimensional academic quality scorecards and health index."""
    overview = test_engine.get_overview_metrics()

    assert "overall_health_score" in overview
    assert 0.0 <= overview["overall_health_score"] <= 100.0
    assert overview["overall_health_status"] in ["EXCELLENT", "GOOD", "ACTION_REQUIRED"]
    assert overview["syllabus_coverage_avg"] > 0.0
    assert overview["total_topics_planned"] >= overview["total_topics_covered"]
    assert overview["freshness_index"] >= 0.0
    assert overview["open_audits_count"] >= 1
    assert overview["institution"] == "MIT Campus, Anna University"
    assert overview["regulation"] == "ECE Regulation 2023"


def test_record_consistency_check_and_rbac(test_engine):
    """Validates real-time academic record consistency checks and strict RBAC barriers."""
    # Student role cannot trigger institutional quality audits
    denied = test_engine.run_record_consistency_check(actor_role="Student")
    assert denied["status"] == "FORBIDDEN"
    assert "privileges" in denied["message"].lower()

    # Admin role executes consistency audit successfully
    allowed = test_engine.run_record_consistency_check(actor_role="Admin")
    assert allowed["status"] == "SUCCESS"
    assert allowed["audited_records_count"] > 0
    assert "audit_reference_id" in allowed

    # QA Director role also allowed
    qa_allowed = test_engine.run_record_consistency_check(actor_role="QA_Director")
    assert qa_allowed["status"] == "SUCCESS"


def test_audit_issue_resolution(test_engine):
    """Validates resolution workflows, RBAC barriers, and audit trail updates."""
    # Fetch an open audit
    audits = test_engine.get_academic_audits(status="OPEN")
    assert len(audits) > 0
    target_audit = audits[0]["audit_id"]

    # Student cannot resolve audits
    forbidden = test_engine.resolve_audit_issue(
        audit_id=target_audit,
        resolution_notes="Student attempt",
        actor_role="Student"
    )
    assert forbidden["status"] == "FORBIDDEN"

    # Admin successfully resolves audit
    resolved = test_engine.resolve_audit_issue(
        audit_id=target_audit,
        resolution_notes="Medical exemption certificate verified by HOD.",
        resolved_by=DEFAULT_STUDENT_ID,
        actor_role="Admin"
    )
    assert resolved["status"] == "SUCCESS"
    assert resolved["audit_id"] == target_audit

    # Verify status changed in DB
    updated_audits = test_engine.get_academic_audits(status="RESOLVED")
    resolved_ids = [a["audit_id"] for a in updated_audits]
    assert target_audit in resolved_ids


def test_syllabus_coverage_progress_update(test_engine):
    """Validates syllabus progress tracking, unit coverage calculations, and clamping."""
    # Non-existent unit check
    missing = test_engine.update_syllabus_unit_progress(
        course_code="EC9999", unit_num=1, topics_covered=5, hours_actual=5.0, actor_role="Faculty"
    )
    assert missing["status"] == "ERROR"

    # Student modification forbidden
    student_try = test_engine.update_syllabus_unit_progress(
        course_code="EC3451", unit_num=4, topics_covered=8, hours_actual=8.0, actor_role="Student"
    )
    assert student_try["status"] == "FORBIDDEN"

    # Faculty successfully updates Unit 4 of EC3451
    res = test_engine.update_syllabus_unit_progress(
        course_code="EC3451",
        unit_num=4,
        topics_covered=9,
        hours_actual=9.0,
        actor_role="Faculty"
    )
    assert res["status"] == "SUCCESS"
    assert res["coverage_pct"] == 100.0
    assert res["unit_status"] == "COMPLETED"

    # Verify query reflects new completion
    cov = test_engine.get_syllabus_coverage("EC3451")
    unit4 = next(u for u in cov if u["unit_num"] == 4)
    assert unit4["status"] == "COMPLETED"
    assert unit4["topics_covered"] == 9


def test_question_bank_taxonomy_analyzer(test_engine):
    """Validates Bloom's taxonomy balance checks (minimum 40% higher order L3-L6)."""
    # 1. Non-compliant set (only L1 Remember questions)
    low_order_questions = [
        {"unit_num": 1, "bloom_level": "L1_REMEMBER", "text": "Define slew rate."},
        {"unit_num": 1, "bloom_level": "L1_REMEMBER", "text": "List ideal op-amp characteristics."},
        {"unit_num": 2, "bloom_level": "L2_UNDERSTAND", "text": "Explain inverting amplifier action."}
    ]
    res_low = test_engine.analyze_custom_question_bank(
        course_code="EC3451", questions=low_order_questions, actor_role="Faculty"
    )
    assert res_low["status"] == "SUCCESS"
    assert res_low["higher_order_pct"] == 0.0
    assert res_low["compliance_status"] == "NON_COMPLIANT"
    assert len(res_low["gaps_detected"]) > 0

    # 2. Compliant set (balanced with L3/L4/L5 questions across all units)
    balanced_questions = [
        {"unit_num": 1, "bloom_level": "L1_REMEMBER", "text": "Define CMRR."},
        {"unit_num": 2, "bloom_level": "L3_APPLY", "text": "Design Butterworth low-pass filter."},
        {"unit_num": 3, "bloom_level": "L4_ANALYZE", "text": "Derive lock-in range for 565 PLL."},
        {"unit_num": 4, "bloom_level": "L5_EVALUATE", "text": "Evaluate VCO linearity vs temperature."},
        {"unit_num": 5, "bloom_level": "L3_APPLY", "text": "Calculate resolution of 12-bit SAR ADC."}
    ]
    res_balanced = test_engine.analyze_custom_question_bank(
        course_code="EC3451", questions=balanced_questions, actor_role="Faculty"
    )
    assert res_balanced["status"] == "SUCCESS"
    assert res_balanced["higher_order_pct"] == 80.0
    assert res_balanced["compliance_status"] == "COMPLIANT"


def test_jaccard_text_similarity_and_duplicate_detector(test_engine):
    """Validates zero-bloat lexical duplicate detection and Jaccard indexing."""
    # 1. Identical text
    sim_identical = test_engine.calculate_text_similarity(
        "Operational amplifier in negative feedback provides stable closed loop gain",
        "Operational amplifier in negative feedback provides stable closed loop gain"
    )
    assert sim_identical == 100.0

    # 2. Completely distinct text
    sim_distinct = test_engine.calculate_text_similarity(
        "Microwave antenna wave propagation impedance matching",
        "Digital logic gate karnaugh map minimization"
    )
    assert sim_distinct == 0.0

    # 3. High-overlap duplicate submission
    dup_res = test_engine.detect_duplicate_submission(
        doc_id_a="DOC_TEST_01",
        doc_id_b="DOC_TEST_02",
        title_a="Lab 3 Active Filter Manual",
        title_b="Assignment 3 Active Filter Questions",
        text_a="Design second order Sallen-Key low-pass filter with cutoff frequency 1kHz and quality factor 0.707.",
        text_b="Design a second order Sallen-Key low-pass filter having cutoff frequency 1kHz and quality factor 0.707.",
        threshold_pct=75.0,
        actor_role="Faculty"
    )
    assert dup_res["status"] == "FLAGGED"
    assert dup_res["similarity_pct"] >= 75.0
    assert "duplicate_id" in dup_res

    # 4. Resolve duplicate pair
    resolved = test_engine.resolve_duplicate_pair(dup_res["duplicate_id"], resolution="MERGED", actor_role="Admin")
    assert resolved["status"] == "SUCCESS"
    assert resolved["resolution"] == "MERGED"


def test_privacy_invariants_no_credential_leakage():
    """Security audit: Ensures strictly zero exposure of private phone numbers or admin emails."""
    forbidden_tokens = [
        "ashokkumar2008313@gmail.com",
        "9597382878"
    ]
    files_to_scan = [
        os.path.join(BASE_DIR, "backend", "data_intelligence_engine.py"),
        os.path.join(BASE_DIR, "src", "components", "DataIntelligenceHub.jsx"),
        os.path.join(BASE_DIR, "src", "pages", "data-intelligence.astro")
    ]

    for fpath in files_to_scan:
        assert os.path.exists(fpath), f"Required file missing: {fpath}"
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            for token in forbidden_tokens:
                assert token not in content, f"SECURITY ALERT: Private token '{token}' leaked in {fpath}"
