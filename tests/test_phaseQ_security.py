"""
========================================================================================
VoltCore Apex Academia - Unit Tests for Phase Q: Security & System Integrity (Features 371–380)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A
========================================================================================
"""

import os
import pytest
import tempfile
from backend.security_integrity_engine import (
    SecurityIntegrityEngine,
    RBAC_PERMISSIONS
)

@pytest.fixture
def temp_engine():
    """Create an isolated temporary SQLite database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = SecurityIntegrityEngine(db_path=path)
    yield engine
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def test_rbac_permissions(temp_engine):
    """Feature 371: Role-Based Access Control (RBAC) permission matrix."""
    # Student checks
    assert temp_engine.check_rbac_permission("STUDENT", "VIEW_COURSES") is True
    assert temp_engine.check_rbac_permission("STUDENT", "SUBMIT_ASSIGNMENTS") is True
    assert temp_engine.check_rbac_permission("STUDENT", "CREATE_DATABASE_BACKUPS") is False
    assert temp_engine.check_rbac_permission("STUDENT", "GRADE_ASSIGNMENTS") is False

    # Faculty checks
    assert temp_engine.check_rbac_permission("FACULTY", "GRADE_ASSIGNMENTS") is True
    assert temp_engine.check_rbac_permission("FACULTY", "CALCULATE_CO_ATTAINMENT") is True
    assert temp_engine.check_rbac_permission("FACULTY", "SYSTEM_SETTINGS") is False

    # HOD Admin checks
    assert temp_engine.check_rbac_permission("HOD_ADMIN", "CREATE_DATABASE_BACKUPS") is True
    assert temp_engine.check_rbac_permission("HOD_ADMIN", "AUDIT_DATABASE_INTEGRITY") is True


def test_session_token_lifecycle(temp_engine):
    """Feature 372: Cryptographic HMAC-SHA256 session token management."""
    # 1. Issue token
    tok_data = temp_engine.issue_session_token("user_101", "STUDENT", ttl_seconds=3600)
    assert "token" in tok_data
    assert tok_data["role"] == "STUDENT"

    # 2. Validate token
    val = temp_engine.validate_session_token(tok_data["token"])
    assert val["valid"] is True
    assert val["user_id"] == "user_101"

    # 3. Revoke token
    temp_engine.revoke_session_token(tok_data["token_id"])
    val_revoked = temp_engine.validate_session_token(tok_data["token_data" if False else "token"])
    assert val_revoked["valid"] is False
    assert val_revoked["reason"] == "TOKEN_REVOKED"

    # 4. Reject malformed token
    val_bad = temp_engine.validate_session_token("invalid_token_string")
    assert val_bad["valid"] is False


def test_sqlite_wal_integrity_check(temp_engine):
    """Feature 373: SQLite WAL Integrity Checker."""
    integrity = temp_engine.check_database_integrity()
    assert integrity["status"] == "HEALTHY"
    assert integrity["integrity_check"] == "ok"
    assert integrity["quick_check"] == "ok"
    assert integrity["is_wal_mode"] is True
    assert integrity["is_healthy"] is True
    assert integrity["database_size_kb"] > 0


def test_password_hashing_and_verification(temp_engine):
    """Feature 374: PBKDF2-HMAC-SHA256 password hashing with 100,000 iterations."""
    pwd = "VoltCore#MIT#Apex2026!"
    hashed = temp_engine.hash_password(pwd)
    assert hashed["algorithm"] == "PBKDF2-HMAC-SHA256"
    assert hashed["iterations"] == 100000
    assert len(hashed["salt_hex"]) == 32
    assert len(hashed["hash_hex"]) == 64

    # Verify matching password
    assert temp_engine.verify_password(pwd, hashed["salt_hex"], hashed["hash_hex"]) is True
    # Verify non-matching password
    assert temp_engine.verify_password("WrongPassword123", hashed["salt_hex"], hashed["hash_hex"]) is False

    # Password strength auditor
    strength = temp_engine.audit_password_strength(pwd)
    assert strength["strength"] == "STRONG"
    assert strength["is_acceptable"] is True


def test_rate_limiter_sliding_window(temp_engine):
    """Feature 375: API Rate Limiter sliding window."""
    client_ip = "192.168.1.55"
    limit = 5

    # First 5 requests allowed
    for i in range(limit):
        res = temp_engine.check_rate_limit(client_ip, limit=limit, window_seconds=60)
        assert res["allowed"] is True

    # 6th request blocked
    blocked = temp_engine.check_rate_limit(client_ip, limit=limit, window_seconds=60)
    assert blocked["allowed"] is False
    assert blocked["retry_after_seconds"] > 0


def test_security_vulnerability_scanner(temp_engine):
    """Feature 376: Security Vulnerability Scanner (SQLi & XSS payloads)."""
    # SQLi payload
    sqli_attack = "admin' OR 1=1 --"
    res1 = temp_engine.scan_input_vulnerabilities(sqli_attack)
    assert res1["is_safe"] is False
    assert res1["sqli_detected"] is True

    # XSS payload
    xss_attack = "<script>alert('XSS')</script>"
    res2 = temp_engine.scan_input_vulnerabilities(xss_attack)
    assert res2["is_safe"] is False
    assert res2["xss_detected"] is True

    # Safe technical text
    safe_text = "CMOS Inverter propagation delay is t_pd = (t_phl + t_plh) / 2"
    res3 = temp_engine.scan_input_vulnerabilities(safe_text)
    assert res3["is_safe"] is True


def test_database_backup_hot_creation(temp_engine):
    """Feature 377: Automated Database Backup Manager with hot backup & SHA256."""
    with tempfile.TemporaryDirectory() as backup_dir:
        backup = temp_engine.create_database_backup(backup_dir=backup_dir)
        assert backup["status"] == "success"
        assert os.path.isfile(backup["filepath"])
        assert backup["file_size_bytes"] > 0
        assert len(backup["checksum_sha256"]) == 64

        backups_list = temp_engine.list_backups()
        assert len(backups_list) == 1
        assert backups_list[0]["backup_id"] == backup["backup_id"]


def test_audit_trail_logging(temp_engine):
    """Feature 378: Append-only security audit trail logger."""
    temp_engine.log_security_event(
        user_role="FACULTY",
        action="GRADE_RELEASE",
        resource="EC3552_LAB4",
        client_ip="10.0.0.42",
        status="SUCCESS"
    )

    logs = temp_engine.get_audit_logs(limit=10)
    assert len(logs) == 1
    assert logs[0]["action"] == "GRADE_RELEASE"
    assert logs[0]["user_role"] == "FACULTY"
    assert len(logs[0]["client_ip_hash"]) == 16


def test_cors_csp_headers_generation(temp_engine):
    """Feature 379: CORS & CSP Policy Enforcer."""
    headers = temp_engine.generate_csp_headers()
    assert "default-src 'self'" in headers["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["X-Content-Type-Options"] == "nosniff"
