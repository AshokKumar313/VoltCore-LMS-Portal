"""
========================================================================================
VoltCore Apex Academia - Phase 3 Enterprise Analytics & Fleet Test Suite
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase3_enterprise.py
Platform Lead / Architect: Ashok Kumar A
Public Email: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
Curriculum / Regulation: Department of Electronics Engineering, Regulation 2023

Validates:
  1. Data Privacy Isolation & RBAC Credential Protection
  2. Public Headers Sanitization (Private Admin Email & Phone Never Leaked)
  3. LittleFS Bulk Sync & Tamper-Evident SHA-256 Merkle Hash Chaining
  4. Class Weak-Topic Matrix Derivation from Wokwi Failure Telemetry
  5. Statistical Attendance Z-Score Anomaly Early Warning System
  6. NBA Course Outcome (CO1-CO5) & Program Outcome (PO) Attainment Engine
========================================================================================
"""

import os
import sys
import time
import json
import hashlib
import unittest
from typing import Dict, Any, List

# Ensure UTF-8 console output on Windows platforms
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.security_auth import (
    PUBLIC_CONTACT_METADATA,
    SECURE_ADMIN_EMAIL,
    SECURE_ADMIN_PHONE,
    get_admin_audit_metadata,
    OWNER_METADATA
)
from backend.security_middleware import SECURITY_HEADERS
from attendance_server import (
    process_bulk_attendance_sync,
    get_class_weak_topics,
    compute_nba_attainment_and_zscores
)


# ========================================================================================
# 1. DATA PRIVACY & RBAC ISOLATION TEST SUITE
# ========================================================================================
def test_public_contact_metadata_specification():
    """Verify that public contact metadata contains the specified public email and GitHub repository."""
    assert PUBLIC_CONTACT_METADATA["platform_lead"] == "Ashok Kumar A"
    assert PUBLIC_CONTACT_METADATA["public_email"] == "ashokkumar3132008@gmail.com"
    assert "AshokKumar313" in PUBLIC_CONTACT_METADATA["github"]
    assert "https://github.com/AshokKumar313" in PUBLIC_CONTACT_METADATA["github_url"]


def test_private_admin_credentials_not_leaked_in_public_headers():
    """Verify that private admin email and phone number are NEVER present in public response headers."""
    headers_str = json.dumps(SECURITY_HEADERS)

    # 1. Private admin email must NOT be present in public client headers
    assert "ashokkumar2008313@gmail.com" not in headers_str, "CRITICAL PRIVACY LEAK: Private admin email found in public SECURITY_HEADERS!"
    assert "+91 9597382878" not in headers_str, "CRITICAL PRIVACY LEAK: Private admin phone found in public SECURITY_HEADERS!"

    # 2. Public contact email must be present
    assert SECURITY_HEADERS["X-Architect-Contact"] == "ashokkumar3132008@gmail.com"
    assert SECURITY_HEADERS["X-Architect-GitHub"] == "AshokKumar313"


def test_rbac_admin_audit_metadata_protection():
    """Verify that unprivileged roles receive redacted placeholders while Owner/Admin receives private telemetry."""
    # A. Unprivileged Student / Guest Role
    student_meta = get_admin_audit_metadata(role="Student")
    assert student_meta["rbac_access_level"] == "PUBLIC_UNPRIVILEGED"
    assert student_meta["public_email"] == "ashokkumar3132008@gmail.com"
    assert "REDACTED" in student_meta["admin_email"]
    assert "REDACTED" in student_meta["admin_phone"]

    # B. Privileged Owner / Platform-Lead / Admin Role
    owner_meta = get_admin_audit_metadata(role="Owner")
    assert owner_meta["rbac_access_level"] == "PRIVILEGED_ADMIN_ACCESS"
    assert owner_meta["admin_email"] == SECURE_ADMIN_EMAIL
    assert owner_meta["admin_phone"] == SECURE_ADMIN_PHONE


# ========================================================================================
# 2. LITTLEFS BULK SYNC & SHA-256 MERKLE CHAIN TEST SUITE
# ========================================================================================
def test_littlefs_bulk_sync_valid_hash_chain():
    """Verify that process_bulk_attendance_sync validates consecutive SHA-256 hash chains."""
    node_id = "ESP32_MIT_TEST_LAB_01"
    records = []
    prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"

    # Construct 4 valid chained records
    for seq in range(1, 5):
        ts = 1729864000 + seq * 60
        sid = "2023MITEC042"
        uid = "E2 80 6F 3B"
        # Preimage: prev_hash:seq:ts:sid:uid:node
        preimage = f"{prev_hash}:{seq}:{ts}:{sid}:{uid}:{node_id}".encode("utf-8")
        h = hashlib.sha256(preimage).hexdigest()

        records.append({
            "seq_id": seq,
            "timestamp": ts,
            "student_id": sid,
            "rfid_uid": uid,
            "prev_hash": prev_hash,
            "hash": h
        })
        prev_hash = h

    payload = {
        "node_id": node_id,
        "batch_size": len(records),
        "records": records
    }

    res, code = process_bulk_attendance_sync(payload)
    assert code == 200
    assert res["status"] == "success"
    assert res["verified_committed"] == 4
    assert res["tampered_rejected"] == 0
    assert res["head_hash"] == prev_hash


def test_littlefs_bulk_sync_tampered_record_detection():
    """Verify that altered records or broken Merkle hash chains are detected and rejected."""
    node_id = "ESP32_MIT_TEST_LAB_01"
    records = []
    prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"

    for seq in range(1, 4):
        ts = 1729865000 + seq * 60
        sid = "2023MITEC042"
        uid = "E2 80 6F 3B"
        preimage = f"{prev_hash}:{seq}:{ts}:{sid}:{uid}:{node_id}".encode("utf-8")
        h = hashlib.sha256(preimage).hexdigest()

        # Maliciously tamper with 2nd record
        if seq == 2:
            sid = "2023MITEC999_TAMPERED"

        records.append({
            "seq_id": seq,
            "timestamp": ts,
            "student_id": sid,
            "rfid_uid": uid,
            "prev_hash": prev_hash,
            "hash": h
        })
        prev_hash = h

    payload = {
        "node_id": node_id,
        "records": records
    }

    res, code = process_bulk_attendance_sync(payload)
    assert code == 207  # Multi-Status / Partial Success
    assert res["tampered_rejected"] >= 1
    assert 1 in res["tampered_indices"]  # Index 1 was tampered


# ========================================================================================
# 3. TEACHER ANALYTICS & STATISTICAL Z-SCORE TEST SUITE
# ========================================================================================
def test_class_weak_topics_matrix():
    """Verify that weak-topic matrices accurately identify high-failure embedded systems concepts."""
    data = get_class_weak_topics()
    assert "weak_topic_matrix" in data
    matrix = data["weak_topic_matrix"]
    assert len(matrix) >= 5

    # ARM Cortex-M DMA Memory Barriers should have highest failure rate (~42%)
    dma_item = next(m for m in matrix if "DMA" in m["topic"])
    assert dma_item["failure_rate_percent"] > 40.0
    assert dma_item["severity"] == "CRITICAL"


def test_attendance_zscore_anomaly_and_nba_attainment():
    """Verify statistical attendance Z-score calculations and NBA Course Outcome attainment mapping."""
    data = compute_nba_attainment_and_zscores()

    assert "mean_attendance" in data
    assert "std_attendance" in data
    assert "at_risk_roster" in data
    assert "course_outcomes" in data

    mean_att = data["mean_attendance"]
    std_att = data["std_attendance"]

    # Verify Z-score equation: Z = (X - mean) / std for every student in roster
    for student in data["at_risk_roster"]:
        expected_z = round((student["attendance_pct"] - mean_att) / std_att, 2)
        assert abs(student["z_score"] - expected_z) <= 0.05, f"Z-Score calculation error for {student['student_id']}"

        # If attendance < 75%, must be flagged as non-compliant
        if student["attendance_pct"] < 75.0:
            assert student["mandatory_75_compliant"] is False
            assert student["risk_tier"] in ("CRITICAL_DEFICIT", "MODERATE_WARNING")

    # Verify NBA CO1-CO5 attainment
    cos = data["course_outcomes"]
    assert len(cos) == 5
    for co in cos:
        assert "target_pct" in co
        assert "attainment_level" in co
        assert len(co["mapped_pos"]) > 0


# ========================================================================================
# UNITTEST TESTCASE WRAPPER
# ========================================================================================
class TestPhase3Enterprise(unittest.TestCase):
    def test_01_public_metadata(self):
        test_public_contact_metadata_specification()

    def test_02_privacy_headers(self):
        test_private_admin_credentials_not_leaked_in_public_headers()

    def test_03_rbac_isolation(self):
        test_rbac_admin_audit_metadata_protection()

    def test_04_littlefs_bulk_sync(self):
        test_littlefs_bulk_sync_valid_hash_chain()

    def test_05_tamper_detection(self):
        test_littlefs_bulk_sync_tampered_record_detection()

    def test_06_weak_topics(self):
        test_class_weak_topics_matrix()

    def test_07_zscore_and_nba(self):
        test_attendance_zscore_anomaly_and_nba_attainment()


# ========================================================================================
# STANDALONE TERMINAL RUNNER WITH PRECISION ANSI DIAGNOSTICS
# ========================================================================================
if __name__ == "__main__":
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    EMERALD = '\033[38;2;0;240;181m'

    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║{RESET} {EMERALD}[VOLTCORE APEX ACADEMIA] PHASE 3 ENTERPRISE & FLEET TEST SUITE{RESET}           {BOLD}{CYAN}║{RESET}")
    print(f"{BOLD}{CYAN}║{RESET} Lead Architect : {BOLD}Ashok Kumar A{RESET} ({PUBLIC_CONTACT_METADATA['public_email']})            {BOLD}{CYAN}║{RESET}")
    print(f"{BOLD}{CYAN}║{RESET} GitHub Profile : {BOLD}https://github.com/AshokKumar313{RESET}                               {BOLD}{CYAN}║{RESET}")
    print(f"{BOLD}{CYAN}║{RESET} Privacy Policy : {BOLD}Private Admin Credentials Strictly Isolated via RBAC{RESET}          {BOLD}{CYAN}║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════════════════════════════╝{RESET}\n")

    tests = [
        ("Public Contact Metadata Specification Compliance", test_public_contact_metadata_specification),
        ("Public Security Headers Credential Isolation (Zero Leakage)", test_private_admin_credentials_not_leaked_in_public_headers),
        ("Role-Based Access Control (RBAC) Admin Audit Protection", test_rbac_admin_audit_metadata_protection),
        ("LittleFS Bulk Sync & SHA-256 Merkle Chain Validation", test_littlefs_bulk_sync_valid_hash_chain),
        ("Tamper-Evident SHA-256 Offline Rejection & Tamper Flagging", test_littlefs_bulk_sync_tampered_record_detection),
        ("Wokwi Failure-Derived Class Weak-Topic Matrix", test_class_weak_topics_matrix),
        ("Statistical Attendance Z-Score & NBA CO-PO Attainment", test_attendance_zscore_anomaly_and_nba_attainment),
    ]

    passed = 0
    failed = 0
    for name, func in tests:
        t0 = time.time()
        try:
            func()
            elapsed_ms = (time.time() - t0) * 1000
            print(f"  {GREEN}✓ [PASS]{RESET} {BOLD}{name:<58}{RESET} {YELLOW}({elapsed_ms:.1f}ms){RESET}")
            passed += 1
        except Exception as e:
            elapsed_ms = (time.time() - t0) * 1000
            print(f"  {RED}✗ [FAIL]{RESET} {BOLD}{name:<58}{RESET} {RED}Error: {e}{RESET}")
            failed += 1

    print(f"\n{BOLD}{CYAN}──────────────────────────────────────────────────────────────────────────────────{RESET}")
    if failed == 0:
        print(f"  {BOLD}{GREEN}ALL {passed} PHASE 3 TEST SPECIFICATIONS PASSED (100% SUCCESS RATE){RESET}\n")
    else:
        print(f"  {BOLD}{RED}{failed} TESTS FAILED{RESET}\n")
        sys.exit(1)
