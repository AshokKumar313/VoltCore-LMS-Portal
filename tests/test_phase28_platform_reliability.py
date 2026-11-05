"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 28 (Platform Intelligence & Reliability)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase28_platform_reliability.py
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

from backend.platform_reliability_engine import (
    PlatformReliabilityEngine,
    platform_reliability_engine,
    DEFAULT_STUDENT_ID,
    ALL_ENTERPRISE_ROUTES,
    BASELINE_APM_ENDPOINTS,
    BASELINE_CONFIG_AUDITS
)


@pytest.fixture
def test_engine(tmp_path):
    """Provides an isolated PlatformReliabilityEngine backed by a temporary SQLite WAL DB."""
    db_file = str(tmp_path / "test_platform_reliability.db")
    engine = PlatformReliabilityEngine(db_path=db_file)
    return engine


def test_platform_reliability_engine_initialization(test_engine):
    """Verifies table creation, SQLite WAL mode, and initial SRE baseline data seeding."""
    conn = test_engine._get_connection()
    try:
        cur = conn.execute("PRAGMA journal_mode;")
        journal_mode = cur.fetchone()[0].upper()
        assert journal_mode == "WAL", f"Expected WAL mode, got {journal_mode}"

        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        assert "system_telemetry_events" in tables
        assert "endpoint_apm_metrics" in tables
        assert "db_wal_health_logs" in tables
        assert "link_health_checks" in tables
        assert "config_health_audits" in tables

        cur = conn.execute("SELECT COUNT(*) FROM endpoint_apm_metrics;")
        assert cur.fetchone()[0] >= len(BASELINE_APM_ENDPOINTS)

        cur = conn.execute("SELECT COUNT(*) FROM link_health_checks;")
        assert cur.fetchone()[0] == 37

        cur = conn.execute("SELECT COUNT(*) FROM config_health_audits;")
        assert cur.fetchone()[0] >= len(BASELINE_CONFIG_AUDITS)
    finally:
        conn.close()


def test_overview_metrics_calculation(test_engine):
    """Validates the multi-dimensional SRE scorecard, SLA uptime, and latency calculations."""
    overview = test_engine.get_overview_metrics()

    assert "reliability_index" in overview
    assert 90.0 <= overview["reliability_index"] <= 100.0
    assert overview["system_status"] in ["HEALTHY", "DEGRADED", "CRITICAL"]
    assert overview["uptime_sla_pct"] == 99.98
    assert overview["avg_api_latency_ms"] > 0.0
    assert overview["global_error_rate_pct"] >= 0.0
    assert overview["total_routes_monitored"] == 37
    assert overview["broken_routes_count"] == 0
    assert overview["passed_config_audits"] >= 7
    assert overview["institution"] == "MIT Campus, Anna University"
    assert overview["regulation"] == "ECE Regulation 2023"


def test_feature_usage_telemetry_logging(test_engine):
    """Validates real-time telemetry recording and aggregated usage summaries."""
    # Record a new feature event
    res = test_engine.record_feature_telemetry(
        feature_name="CIRCUIT_SPICE_SIMULATOR",
        route="/simulation",
        actor_id=DEFAULT_STUDENT_ID,
        latency_ms=11.2,
        status_code=200
    )
    assert res["status"] == "SUCCESS"
    assert "event_id" in res
    assert res["feature_name"] == "CIRCUIT_SPICE_SIMULATOR"

    # Query summary
    summary = test_engine.get_feature_usage_summary(limit=5)
    assert len(summary) > 0
    circuit_feat = next((f for f in summary if f["feature_name"] == "CIRCUIT_SPICE_SIMULATOR"), None)
    assert circuit_feat is not None
    assert circuit_feat["invocations"] >= 1
    assert circuit_feat["avg_latency_ms"] > 0.0


def test_database_wal_health_inspection(test_engine):
    """Validates SQLite WAL inspection, page metrics, and quick_check integrity."""
    health = test_engine.get_database_wal_health()

    assert health["journal_mode"] == "WAL"
    assert health["integrity_check"] == "ok"
    assert health["page_size_bytes"] == 4096
    assert health["total_pages"] > 0
    assert health["status"] == "HEALTHY"
    assert os.path.exists(health["database_path"])


def test_wal_checkpoint_and_rbac(test_engine):
    """Validates WAL checkpoint execution and strict administrative RBAC protection."""
    # Student role cannot trigger checkpoint
    forbidden = test_engine.execute_wal_checkpoint(mode="PASSIVE", actor_role="Student")
    assert forbidden["status"] == "FORBIDDEN"
    assert "privileges" in forbidden["message"].lower()

    # Admin role executes checkpoint successfully
    allowed = test_engine.execute_wal_checkpoint(mode="PASSIVE", actor_role="Admin")
    assert allowed["status"] == "SUCCESS"
    assert allowed["checkpoint_mode"] == "PASSIVE"
    assert "log_pages" in allowed

    # SRE role also allowed
    sre_allowed = test_engine.execute_wal_checkpoint(mode="PASSIVE", actor_role="SRE")
    assert sre_allowed["status"] == "SUCCESS"


def test_route_integrity_scan_and_rbac(test_engine):
    """Validates 37 enterprise route reachability verification and RBAC barriers."""
    # Student cannot run system route scan
    forbidden = test_engine.run_route_integrity_scan(actor_role="Student")
    assert forbidden["status"] == "FORBIDDEN"

    # Admin executes route scan
    scan = test_engine.run_route_integrity_scan(actor_role="Admin")
    assert scan["status"] == "SUCCESS"
    assert scan["total_routes_scanned"] == 37
    assert scan["broken_routes_detected"] == 0

    # Verify link checks returned
    checks = test_engine.get_link_health_checks()
    assert len(checks) == 37
    assert all(c["is_broken"] == 0 for c in checks)
    assert all(c["http_status"] == 200 for c in checks)


def test_full_system_audit_and_rbac(test_engine):
    """Validates unified SRE diagnostic audit and RBAC boundaries."""
    # Student role forbidden
    student_try = test_engine.run_full_system_audit(actor_role="Student")
    assert student_try["status"] == "FORBIDDEN"

    # Admin role executes comprehensive audit
    audit = test_engine.run_full_system_audit(actor_role="Admin")
    assert audit["status"] == "SUCCESS"
    assert audit["database_integrity"] == "ok"
    assert audit["journal_mode"] == "WAL"
    assert audit["routes_verified"] == 37
    assert audit["reliability_index"] >= 95.0


def test_privacy_invariants_no_credential_leakage():
    """Security audit: Ensures strictly zero exposure of private phone numbers or admin emails."""
    forbidden_tokens = [
        "ashokkumar2008313@gmail.com",
        "9597382878"
    ]
    target_files = [
        os.path.join(BASE_DIR, "backend", "platform_reliability_engine.py"),
        os.path.join(BASE_DIR, "src", "components", "PlatformHealthHub.jsx"),
        os.path.join(BASE_DIR, "src", "pages", "system-health.astro")
    ]

    for fpath in target_files:
        assert os.path.exists(fpath), f"File {fpath} does not exist"
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            for token in forbidden_tokens:
                assert token not in content, f"SECURITY ALERT: Private token '{token}' leaked in {fpath}"

