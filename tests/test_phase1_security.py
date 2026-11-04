"""
========================================================================================
VoltCore Apex Academia - Phase 1 Security Test Suite
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase1_security.py
Platform Lead / Architect: Ashok Kumar A
Primary Contact Email: ashokkumar2008313@gmail.com
GitHub Profile: https://github.com/AshokKumar313 (Username: AshokKumar313)
Contact / Telemetry Line: +91 9597382878
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
Curriculum / Regulation: Department of Electronics Engineering, Regulation 2023

Validates:
  1. Cryptographic PBKDF2-HMAC-SHA256 upgraded to 600,000 iterations
  2. Cryptographic Salt Uniqueness (16-byte random salts per hash)
  3. Constant-Time Verification & Failure Handling (tampering, malformed hashes)
  4. TokenBucketRateLimiter Capacity Depletion, Burst Blocking, and Client Isolation
  5. Response Security Headers (CSP, nosniff, DENY, XSS-Protection)
  6. Request JSON Payload Schema Validation (@validate_json_payload)
  7. Project Ownership & Metadata Integrity
========================================================================================
"""

import os
import sys
import time
import unittest
from typing import Dict, Any

# Ensure UTF-8 console output on Windows platforms
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.security_auth import (
    hash_password,
    verify_password,
    generate_jwt_token,
    verify_jwt_token,
    TokenBucketRateLimiter,
    PBKDF2_ITERATIONS,
    SALT_BYTE_LENGTH,
    OWNER_METADATA,
    PUBLIC_CONTACT_METADATA
)
from backend.security_middleware import (
    SECURITY_HEADERS,
    add_security_headers,
    validate_json_payload,
    rate_limited
)


# Helper Mock Request class for isolated unit testing
class MockRequest:
    def __init__(self, content_type: str = "application/json", json_data: Any = None, remote_addr: str = "127.0.0.1"):
        self.content_type = content_type
        self.headers = {"Content-Type": content_type}
        self.remote_addr = remote_addr
        self._json_data = json_data

    def get_json(self, silent=True):
        return self._json_data


# Helper Mock Response class
class MockResponse:
    def __init__(self):
        self.headers: Dict[str, str] = {}


# ========================================================================================
# 1. PBKDF2 HASHING & ITERATIONS TEST SUITE
# ========================================================================================
def test_pbkdf2_600000_iterations_and_format():
    """Verify that password hashing enforces OWASP-compliant 600,000 iterations and valid format."""
    password = "MIT_Chromepet_ECE_2026!Secure"
    hashed = hash_password(password)

    # Must start with algo name and iteration count
    assert hashed.startswith("pbkdf2_sha256$600000$"), f"Expected 600,000 iterations prefix, got: {hashed[:30]}"
    
    parts = hashed.split("$")
    assert len(parts) == 4, f"Hash string must have 4 dollar-separated parts, found {len(parts)}"
    
    algo, iterations_str, salt_hex, hash_hex = parts
    assert algo == "pbkdf2_sha256"
    assert int(iterations_str) == 600_000
    assert PBKDF2_ITERATIONS == 600_000

    # Salt must be 16 bytes (32 hex characters)
    salt_bytes = bytes.fromhex(salt_hex)
    assert len(salt_bytes) == SALT_BYTE_LENGTH, f"Expected 16-byte salt, got {len(salt_bytes)}"

    # Derived key must be 32 bytes (64 hex characters)
    hash_bytes = bytes.fromhex(hash_hex)
    assert len(hash_bytes) == 32, f"Expected 32-byte derived key, got {len(hash_bytes)}"


def test_salt_uniqueness_across_identical_passwords():
    """Verify that hashing identical passwords generates unique 16-byte cryptographically secure salts."""
    password = "IdenticalAnnaUniversityPassword#2026"
    salts = set()
    hashes = set()

    for _ in range(8):
        h = hash_password(password)
        salt_hex = h.split("$")[2]
        salts.add(salt_hex)
        hashes.add(h)

    # Every invocation must produce a distinct salt and hash
    assert len(salts) == 8, f"Salts must be strictly unique! Expected 8 distinct salts, found {len(salts)}"
    assert len(hashes) == 8, f"Hashes must be strictly unique! Expected 8 distinct hashes, found {len(hashes)}"


def test_password_verification_success():
    """Verify that correct passwords match their PBKDF2-HMAC-SHA256 hash."""
    pwd = "AshokKumar@MITCampus#2023ECE"
    h = hash_password(pwd)

    assert verify_password(pwd, h) is True, "Valid password verification failed."


def test_password_verification_failure_handling():
    """Verify constant-time failure handling for wrong passwords, tampered hashes, and bad inputs."""
    pwd = "CorrectPassword123"
    h = hash_password(pwd)

    # 1. Incorrect password
    assert verify_password("WrongPassword999", h) is False

    # 2. Tampered hash output (flip last hex char)
    tampered_hash = h[:-1] + ('a' if h[-1] != 'a' else 'b')
    assert verify_password(pwd, tampered_hash) is False

    # 3. Tampered salt (flip first char of salt)
    parts = h.split("$")
    salt_tampered = ('0' if parts[2][0] != '0' else '1') + parts[2][1:]
    tampered_salt_hash = f"{parts[0]}${parts[1]}${salt_tampered}${parts[3]}"
    assert verify_password(pwd, tampered_salt_hash) is False

    # 4. Malformed inputs and edge cases
    assert verify_password(pwd, "invalid_format_string") is False
    assert verify_password(pwd, "pbkdf2_sha256$notanumber$aabb$ccdd") is False
    assert verify_password(pwd, "") is False
    assert verify_password("", h) is False
    assert verify_password(None, h) is False
    assert verify_password(pwd, None) is False


def test_empty_password_rejection():
    """Verify that empty or invalid passwords raise ValueError during hash creation."""
    try:
        hash_password("")
        assert False, "Should have raised ValueError on empty string password"
    except ValueError:
        pass

    try:
        hash_password(None)
        assert False, "Should have raised ValueError on None password"
    except ValueError:
        pass


# ========================================================================================
# 2. TOKEN BUCKET RATE LIMITER TEST SUITE
# ========================================================================================
def test_rate_limiter_capacity_depletion():
    """Verify that TokenBucketRateLimiter depletes tokens and blocks requests upon capacity exhaustion."""
    limiter = TokenBucketRateLimiter(capacity=5, fill_rate=1.0)
    client_id = "ip:192.168.1.100"

    # Consume all 5 available tokens
    for i in range(5):
        allowed, meta = limiter.check_rate_limit(client_id, cost=1.0)
        assert allowed is True, f"Request {i+1} should be allowed"
        assert meta["allowed"] is True

    # 6th request should be throttled
    allowed, meta = limiter.check_rate_limit(client_id, cost=1.0)
    assert allowed is False, "6th request exceeded capacity and must be rejected"
    assert meta["allowed"] is False
    assert meta["retry_after_seconds"] > 0, "Retry-After seconds must be positive"
    assert meta["tokens_remaining"] < 1.0


def test_rate_limiter_client_isolation():
    """Verify that rate limits for one client do not impact another client."""
    limiter = TokenBucketRateLimiter(capacity=3, fill_rate=0.5)
    student_a = "user:2023MITEC042"
    student_b = "user:2023MITEC099"

    # Deplete Student A
    for _ in range(3):
        assert limiter.is_allowed(student_a) is True
    assert limiter.is_allowed(student_a) is False

    # Student B should still have full capacity
    assert limiter.is_allowed(student_b) is True
    allowed, meta = limiter.check_rate_limit(student_b)
    assert allowed is True
    assert meta["tokens_remaining"] >= 1.0


def test_rate_limiter_token_regeneration():
    """Verify that rate limiter regenerates tokens based on fill_rate over time."""
    # 2 tokens capacity, regenerates 20 tokens per second (1 token per 50ms)
    limiter = TokenBucketRateLimiter(capacity=2, fill_rate=20.0)
    client_id = "test_replenish_client"

    # Deplete all 2 tokens
    assert limiter.is_allowed(client_id) is True
    assert limiter.is_allowed(client_id) is True
    assert limiter.is_allowed(client_id) is False

    # Sleep 60ms to regenerate at least 1 token
    time.sleep(0.06)

    # Next request should now succeed
    assert limiter.is_allowed(client_id) is True


# ========================================================================================
# 3. SECURITY MIDDLEWARE & HEADERS TEST SUITE
# ========================================================================================
def test_security_headers_compliance():
    """Verify that security headers meet OWASP guidelines and contain project ownership metadata."""
    headers = SECURITY_HEADERS

    # Essential OWASP Hardening Headers
    assert "Content-Security-Policy" in headers
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    assert "object-src 'none'" in headers["Content-Security-Policy"]
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["X-XSS-Protection"] == "1; mode=block"

    # Project Ownership Telemetry Headers (Public Contact Isolation)
    assert headers["X-Lead-Architect"] == OWNER_METADATA["platform_lead"]
    assert headers["X-Architect-Contact"] in (PUBLIC_CONTACT_METADATA["public_email"], OWNER_METADATA["email"])
    assert headers["X-Architect-GitHub"] == OWNER_METADATA["github"]
    assert "MIT Campus" in headers["X-Academic-Institution"]


def test_add_security_headers_injection():
    """Verify that add_security_headers attaches all headers to response objects."""
    resp = MockResponse()
    hardened = add_security_headers(resp)

    for h_name, h_val in SECURITY_HEADERS.items():
        assert hardened.headers[h_name] == h_val


def test_validate_json_payload_decorator_success_and_failure():
    """Verify that @validate_json_payload decorator strictly filters media types and payload schemas."""
    
    @validate_json_payload("student_id", "rfid_uid")
    def handle_scan(payload=None):
        return {"status": "success", "user": payload["student_id"]}, 200

    # Case A: Valid JSON Payload with all required fields
    valid_req = MockRequest(
        content_type="application/json; charset=utf-8",
        json_data={"student_id": "2023MITEC042", "rfid_uid": "E2 80 6F 3B"}
    )
    res, code = handle_scan(_mock_request=valid_req)
    assert code == 200
    assert res["status"] == "success"

    # Case B: Rejects non-JSON Content-Type (HTTP 415)
    text_req = MockRequest(
        content_type="text/plain",
        json_data={"student_id": "2023MITEC042", "rfid_uid": "E2 80 6F 3B"}
    )
    res, code = handle_scan(_mock_request=text_req)
    assert code == 415
    assert res["body"]["code"] == "INVALID_CONTENT_TYPE"

    # Case C: Rejects missing required field (HTTP 422)
    missing_req = MockRequest(
        content_type="application/json",
        json_data={"student_id": "2023MITEC042"}  # missing rfid_uid
    )
    res, code = handle_scan(_mock_request=missing_req)
    assert code == 422
    assert "rfid_uid" in res["body"]["missing_fields"]

    # Case D: Rejects empty string required field (HTTP 422)
    empty_req = MockRequest(
        content_type="application/json",
        json_data={"student_id": "2023MITEC042", "rfid_uid": "   "}
    )
    res, code = handle_scan(_mock_request=empty_req)
    assert code == 422
    assert "rfid_uid" in res["body"]["missing_fields"]


# ========================================================================================
# 4. PROJECT OWNERSHIP & METADATA TEST SUITE
# ========================================================================================
def test_official_project_ownership_metadata():
    """Verify that all project ownership metadata matches official credentials."""
    assert OWNER_METADATA["platform_lead"] == "Ashok Kumar A"
    assert OWNER_METADATA["email"] == "ashokkumar2008313@gmail.com"
    assert OWNER_METADATA["github"] == "AshokKumar313"
    assert OWNER_METADATA["telemetry_contact"] == "+91 9597382878"
    assert "Anna University" in OWNER_METADATA["institution"]
    assert "MIT Campus" in OWNER_METADATA["institution"]
    assert "Regulation 2023" in OWNER_METADATA["regulation"]


# ========================================================================================
# UNITTEST TESTCASE WRAPPER (FOR PYTEST & PYTHON -M UNITTEST)
# ========================================================================================
class TestPhase1Security(unittest.TestCase):
    def test_01_pbkdf2_iterations(self):
        test_pbkdf2_600000_iterations_and_format()

    def test_02_salt_uniqueness(self):
        test_salt_uniqueness_across_identical_passwords()

    def test_03_verification_success(self):
        test_password_verification_success()

    def test_04_verification_failure(self):
        test_password_verification_failure_handling()

    def test_05_empty_password(self):
        test_empty_password_rejection()

    def test_06_rate_limiter_depletion(self):
        test_rate_limiter_capacity_depletion()

    def test_07_rate_limiter_isolation(self):
        test_rate_limiter_client_isolation()

    def test_08_rate_limiter_replenishment(self):
        test_rate_limiter_token_regeneration()

    def test_09_security_headers(self):
        test_security_headers_compliance()

    def test_10_add_security_headers(self):
        test_add_security_headers_injection()

    def test_11_validate_json_payload(self):
        test_validate_json_payload_decorator_success_and_failure()

    def test_12_owner_metadata(self):
        test_official_project_ownership_metadata()


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
    print(f"{BOLD}{CYAN}║{RESET} {EMERALD}[VOLTCORE APEX ACADEMIA] PHASE 1 ENTERPRISE SECURITY TEST SUITE{RESET}           {BOLD}{CYAN}║{RESET}")
    print(f"{BOLD}{CYAN}║{RESET} Lead Architect : {BOLD}Ashok Kumar A{RESET} ({OWNER_METADATA['email']})                    {BOLD}{CYAN}║{RESET}")
    print(f"{BOLD}{CYAN}║{RESET} Institution    : {OWNER_METADATA['institution']} ({OWNER_METADATA['regulation']})           {BOLD}{CYAN}║{RESET}")
    print(f"{BOLD}{CYAN}║{RESET} GitHub Profile : {BOLD}https://github.com/AshokKumar313{RESET}                               {BOLD}{CYAN}║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════════════════════════════╝{RESET}\n")

    test_functions = [
        ("PBKDF2-HMAC-SHA256 600,000 Iterations & Key Length", test_pbkdf2_600000_iterations_and_format),
        ("Cryptographic Salt Uniqueness (16-byte cryptographically secure)", test_salt_uniqueness_across_identical_passwords),
        ("Constant-Time Password Verification Success", test_password_verification_success),
        ("Constant-Time Failure & Tampering Rejection", test_password_verification_failure_handling),
        ("Empty / Invalid Password Exception Guard", test_empty_password_rejection),
        ("Token Bucket Rate Limiter Capacity Depletion", test_rate_limiter_capacity_depletion),
        ("Token Bucket Client Bucket Isolation (Per-IP / Per-User)", test_rate_limiter_client_isolation),
        ("Token Bucket Token Regeneration & Refill Rate", test_rate_limiter_token_regeneration),
        ("OWASP Strict Security Headers & CSP Configuration", test_security_headers_compliance),
        ("Security Header Response Injection Hook", test_add_security_headers_injection),
        ("JSON Schema & Content-Type Validator Decorator", test_validate_json_payload_decorator_success_and_failure),
        ("Official Project Ownership Metadata Integrity", test_official_project_ownership_metadata),
    ]

    passed_count = 0
    failed_count = 0

    for name, func in test_functions:
        t0 = time.time()
        try:
            func()
            elapsed_ms = (time.time() - t0) * 1000
            print(f"  {GREEN}✓ [PASS]{RESET} {BOLD}{name:<58}{RESET} {YELLOW}({elapsed_ms:.1f}ms){RESET}")
            passed_count += 1
        except Exception as e:
            elapsed_ms = (time.time() - t0) * 1000
            print(f"  {RED}✗ [FAIL]{RESET} {BOLD}{name:<58}{RESET} {RED}Error: {e}{RESET}")
            failed_count += 1

    print(f"\n{BOLD}{CYAN}──────────────────────────────────────────────────────────────────────────────────{RESET}")
    if failed_count == 0:
        print(f"  {BOLD}{GREEN}ALL {passed_count} TEST SPECIFICATIONS PASSED (100% SUCCESS RATE){RESET}")
        print(f"  {EMERALD}Phase 1 Security Subsystem Armed & Certified for Anna University / MIT Campus.{RESET}\n")
    else:
        print(f"  {BOLD}{RED}{failed_count} TESTS FAILED out of {passed_count + failed_count}{RESET}\n")
        sys.exit(1)
