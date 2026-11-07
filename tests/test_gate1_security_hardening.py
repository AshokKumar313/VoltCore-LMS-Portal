"""
========================================================================================
VoltCore Apex Academia - Gate 1 Security Remediation Verification Suite
Lead Security Architect: Ashok Kumar A
Target Hardware: HP Victus (LAPTOP-3NEGBVLE) — Whisper-Quiet, Passive CPU (<5%)
Standards: OWASP Top 10 • CWE-95 / CWE-94 Neutralization • NIST SP 800-63B Auth
Architecture: Strict AST Expression Whitelist • Hardened HS256 JWT • Server-Enforced RBAC
========================================================================================
"""

import os
import sys
import time
import json
import base64
import pytest

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.safe_expression_parser import (
    SafeExpressionParser,
    safe_eval_boolean,
    SecurityException
)
from backend.security_auth import (
    get_jwt_secret,
    generate_jwt_token,
    verify_jwt_token,
    hash_password,
    verify_password,
    build_session_cookie,
    extract_token_from_cookie,
    build_clear_session_cookie,
    get_admin_audit_metadata,
    SESSION_COOKIE_NAME
)
from backend.security_middleware import (
    require_role,
    require_auth,
    ROLE_HIERARCHY,
    resolve_request_role
)
from backend.digital_electronics_engine import DigitalElectronicsEngine
from backend.vlsi_physical_design_engine import SystemVerilogAssertionAnalyzer


# ========================================================================================
# 1. STRICT WHITELIST AST EXPRESSION PARSER TESTS
# ========================================================================================
class TestSafeExpressionParser:
    """Verifies safe mathematical and boolean expression evaluation with zero eval/exec."""

    def test_basic_arithmetic_operations(self):
        assert SafeExpressionParser.evaluate("2 + 3 * 4") == 14
        assert SafeExpressionParser.evaluate("(10 - 2) / 4") == 2.0
        assert SafeExpressionParser.evaluate("2 ** 5") == 32
        assert SafeExpressionParser.evaluate("15 % 4") == 3
        assert SafeExpressionParser.evaluate("7 // 2") == 3

    def test_whitelisted_math_functions(self):
        assert abs(SafeExpressionParser.evaluate("sin(pi / 2)") - 1.0) < 1e-9
        assert abs(SafeExpressionParser.evaluate("cos(0)") - 1.0) < 1e-9
        assert SafeExpressionParser.evaluate("sqrt(144)") == 12.0
        assert SafeExpressionParser.evaluate("abs(-42)") == 42
        assert SafeExpressionParser.evaluate("max(3, 7, 2)") == 7
        assert SafeExpressionParser.evaluate("min(3, 7, 2)") == 2
        assert SafeExpressionParser.evaluate("round(3.6)") == 4

    def test_variable_substitution(self):
        env = {"R1": 1000, "R2": 2000, "Vin": 5.0}
        vout = SafeExpressionParser.evaluate("Vin * (R2 / (R1 + R2))", env)
        assert abs(vout - 3.3333333333333335) < 1e-6

    def test_boolean_evaluator_syntax_variations(self):
        assert safe_eval_boolean("A and B", {"A": 1, "B": 1}) == 1
        assert safe_eval_boolean("A and B", {"A": 1, "B": 0}) == 0
        assert safe_eval_boolean("A or B", {"A": 0, "B": 0}) == 0
        assert safe_eval_boolean("A or B", {"A": 0, "B": 1}) == 1
        assert safe_eval_boolean("not A", {"A": 0}) == 1
        assert safe_eval_boolean("not A", {"A": 1}) == 0

        # Engineering symbols: * for AND, + for OR, ' for NOT, ^ for XOR
        assert safe_eval_boolean("A * B + C", {"A": 1, "B": 1, "C": 0}) == 1
        assert safe_eval_boolean("A * B + C", {"A": 1, "B": 0, "C": 0}) == 0
        assert safe_eval_boolean("A' * B", {"A": 0, "B": 1}) == 1
        assert safe_eval_boolean("A' * B", {"A": 1, "B": 1}) == 0
        assert safe_eval_boolean("A ^ B", {"A": 1, "B": 1}) == 0
        assert safe_eval_boolean("A ^ B", {"A": 1, "B": 0}) == 1

    def test_comparisons_and_sva_expressions(self):
        assert SafeExpressionParser.evaluate("a == b", {"a": 4, "b": 4}, allow_math_funcs=False) is True
        assert SafeExpressionParser.evaluate("a == b", {"a": 4, "b": 5}, allow_math_funcs=False) is False
        assert SafeExpressionParser.evaluate("a < b", {"a": 3, "b": 7}, allow_math_funcs=False) is True
        assert SafeExpressionParser.evaluate("req == 1 and gnt == 1", {"req": 1, "gnt": 1}, allow_math_funcs=False) is True

    @pytest.mark.parametrize("payload", [
        "().__class__.__bases__[0].__subclasses__()",
        "__import__('os').system('whoami')",
        "open('/etc/passwd')",
        "eval('1 + 1')",
        "exec('x = 1')",
        "globals()",
        "locals()",
        "getattr(math, 'sin')",
        "compile('x = 1', '', 'single')",
        "2 ** 1000000",  # Catastrophic power DoS
        "a.b",           # Dot attribute access
        "a[0]",          # Subscript access
        "lambda x: x",   # Lambda
        "[x for x in [1]]", # Comprehension
    ])
    def test_security_exploit_neutralization(self, payload):
        """Strictly asserts that dangerous Python payloads are blocked with SecurityException or ValueError."""
        with pytest.raises((SecurityException, ValueError, OverflowError)):
            SafeExpressionParser.evaluate(payload, {"a": [1, 2]})


# ========================================================================================
# 2. HARDENED JWT AUTHENTICATION TESTS
# ========================================================================================
class TestHardenedJwtAuthentication:
    """Verifies JWT environment loading, signature validation, and attack resistance."""

    def test_ephemeral_secret_generation_in_development(self, monkeypatch):
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        monkeypatch.delenv("VOLTCORE_JWT_SECRET", raising=False)
        monkeypatch.delenv("VOLTCORE_ENV", raising=False)
        monkeypatch.delenv("FLASK_ENV", raising=False)

        secret = get_jwt_secret()
        assert isinstance(secret, str)
        assert len(secret) >= 32  # At least 256 bits

    def test_production_mode_refuses_launch_without_secret(self, monkeypatch):
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        monkeypatch.delenv("VOLTCORE_JWT_SECRET", raising=False)
        monkeypatch.setenv("VOLTCORE_ENV", "production")

        with pytest.raises(RuntimeError) as exc_info:
            get_jwt_secret()
        assert "CRITICAL SECURITY ERROR" in str(exc_info.value)

    def test_production_mode_refuses_short_insecure_secret(self, monkeypatch):
        monkeypatch.setenv("JWT_SECRET_KEY", "short_weak_key_123")
        monkeypatch.setenv("VOLTCORE_ENV", "production")

        with pytest.raises(RuntimeError) as exc_info:
            get_jwt_secret()
        assert "must be at least 32 characters" in str(exc_info.value)

    def test_valid_token_issuance_and_verification(self):
        token = generate_jwt_token(
            user_id="2023MITEC042",
            role="Student",
            name="Ashok Kumar A"
        )
        claims = verify_jwt_token(token)
        assert claims is not None
        assert claims["sub"] == "2023MITEC042"
        assert claims["role"] == "Student"
        assert claims["iss"] == "VoltCore-Apex-Academia"

    def test_expired_token_rejection(self):
        # Generate token expired 10 seconds ago
        token = generate_jwt_token(
            user_id="2023MITEC042",
            role="Student",
            name="Ashok Kumar A",
            expires_in=-10
        )
        assert verify_jwt_token(token) is None

    def test_algorithm_substitution_rejection(self):
        """Asserts that 'none' algorithm or tampered header is strictly rejected."""
        header = {"alg": "none", "typ": "JWT"}
        payload = {"sub": "hacker", "role": "Admin", "exp": int(time.time()) + 3600}
        h_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        p_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        tampered_token = f"{h_b64}.{p_b64}."

        assert verify_jwt_token(tampered_token) is None

    def test_signature_tampering_rejection(self):
        token = generate_jwt_token(user_id="2023MITEC042", role="Student", name="Ashok Kumar A")
        parts = token.split(".")
        # Tamper payload
        tampered_payload = base64.urlsafe_b64encode(b'{"sub":"hacker","role":"Admin"}').decode().rstrip("=")
        tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"
        assert verify_jwt_token(tampered_token) is None


# ========================================================================================
# 3. SERVER-ENFORCED RBAC & AUTHORIZATION MIDDLEWARE TESTS
# ========================================================================================
class TestServerEnforcedRbacMiddleware:
    """Verifies server-side authorization enforcement across roles and endpoints."""

    class MockRequest:
        def __init__(self, headers=None, json_body=None):
            self.headers = headers or {}
            self._json = json_body or {}
        def get_json(self, silent=True):
            return self._json

    def test_require_role_admin_permits_admin(self):
        admin_token = generate_jwt_token(user_id="ADM_01", role="Admin", name="Lead Administrator")

        @require_role("Admin")
        def protected_admin_view():
            return {"status": "SUCCESS", "data": "classified"}

        req = self.MockRequest(headers={"Authorization": f"Bearer {admin_token}"})
        res = protected_admin_view(_mock_request=req)
        assert res["status"] == "SUCCESS"

    def test_require_role_admin_permits_platform_lead_via_hierarchy(self):
        lead_token = generate_jwt_token(user_id="LEAD_01", role="Platform-Lead", name="Platform Lead")

        @require_role("Admin")
        def protected_admin_view():
            return {"status": "SUCCESS", "data": "classified"}

        req = self.MockRequest(headers={"Authorization": f"Bearer {lead_token}"})
        res = protected_admin_view(_mock_request=req)
        assert res["status"] == "SUCCESS"

    def test_require_role_admin_forbids_student(self):
        student_token = generate_jwt_token(user_id="STU_01", role="Student", name="Student One")

        @require_role("Admin")
        def protected_admin_view():
            return {"status": "SUCCESS"}

        req = self.MockRequest(headers={"Authorization": f"Bearer {student_token}"})
        res, code = protected_admin_view(_mock_request=req)
        assert code == 403
        assert res["body"]["code"] == "INSUFFICIENT_PERMISSIONS"

    def test_require_role_faculty_permits_faculty_and_admin(self):
        fac_token = generate_jwt_token(user_id="FAC_01", role="Faculty", name="Professor")
        adm_token = generate_jwt_token(user_id="ADM_01", role="Admin", name="Administrator")
        stu_token = generate_jwt_token(user_id="STU_01", role="Student", name="Student")

        @require_role("Faculty")
        def grade_override_view():
            return {"status": "SUCCESS"}

        # Faculty succeeds
        res_f = grade_override_view(_mock_request=self.MockRequest(headers={"Authorization": f"Bearer {fac_token}"}))
        assert res_f["status"] == "SUCCESS"

        # Admin succeeds via hierarchy
        res_a = grade_override_view(_mock_request=self.MockRequest(headers={"Authorization": f"Bearer {adm_token}"}))
        assert res_a["status"] == "SUCCESS"

        # Student fails
        res_s, code_s = grade_override_view(_mock_request=self.MockRequest(headers={"Authorization": f"Bearer {stu_token}"}))
        assert code_s == 403

    def test_require_role_rejects_missing_credentials(self, monkeypatch):
        monkeypatch.setenv("VOLTCORE_ENFORCE_AUTH", "true")

        @require_role("Student")
        def student_view():
            return {"status": "SUCCESS"}

        res, code = student_view(_mock_request=self.MockRequest(headers={}))
        assert code == 401
        assert res["body"]["code"] == "AUTHENTICATION_REQUIRED"

    def test_require_role_rejects_malformed_token(self):
        @require_role("Student")
        def student_view():
            return {"status": "SUCCESS"}

        req = self.MockRequest(headers={"Authorization": "Bearer bad.token.here"})
        res, code = student_view(_mock_request=req)
        assert code == 401
        assert res["body"]["code"] == "INVALID_OR_EXPIRED_TOKEN"

    def test_require_role_authenticates_via_session_cookie(self):
        token = generate_jwt_token(user_id="2023MITEC042", role="Admin", name="Ashok Kumar A")

        @require_role("Admin")
        def admin_view():
            return {"status": "SUCCESS", "role": "Admin"}

        cookie_str = f"theme=dark; {SESSION_COOKIE_NAME}={token}; visited=true"
        req = self.MockRequest(headers={"Cookie": cookie_str})
        res = admin_view(_mock_request=req)
        assert res["status"] == "SUCCESS"

    def test_resolve_request_role_prevents_unauthenticated_privilege_escalation(self):
        class SimpleReq:
            def __init__(self, headers=None):
                self.headers = headers or {}

        # 1. Unauthenticated request attempting to pass privileged actor_role in payload
        fake_payload = {"actor_role": "Faculty", "course_code": "EC4801"}
        role, claims = resolve_request_role(SimpleReq(), payload=fake_payload, default_role="Student")
        assert role == "Student", "Unauthenticated payload must NOT be able to escalate to Faculty"
        assert claims is None

        # 2. Legitimate authenticated Faculty token elevates properly
        fac_token = generate_jwt_token(user_id="FAC_042", role="Faculty", name="Faculty Lead")
        req_auth = SimpleReq(headers={"Authorization": f"Bearer {fac_token}"})
        role_auth, claims_auth = resolve_request_role(req_auth, payload=fake_payload)
        assert role_auth == "Faculty"
        assert claims_auth is not None
        assert claims_auth["role"] == "Faculty"


# ========================================================================================
# 4. ENGINE INTEGRATION REGRESSION TESTS (AST VERIFICATION)
# ========================================================================================
class TestEngineAstIntegration:
    """Verifies that DigitalElectronicsEngine and SystemVerilogAssertionAnalyzer run with AST."""

    def test_digital_electronics_engine_truth_table_ast(self):
        engine = DigitalElectronicsEngine()
        table = engine.generate_truth_table("A * B + C'")
        assert table["status"] == "SUCCESS"
        assert table["variable_count"] == 3
        assert len(table["rows"]) == 8

    def test_sva_analyzer_temporal_assertion_ast(self):
        analyzer = SystemVerilogAssertionAnalyzer()
        trace = {
            "req": [0, 1, 0, 1, 0],
            "gnt": [0, 1, 0, 0, 0]
        }
        res = analyzer.evaluate_trace(["assert property (@(posedge clk) req |-> gnt);"], trace)
        assert res["total_attempts"] == 5
        assert res["total_matches"] == 1
        assert res["total_failures"] == 1
        assert res["total_vacuous_passes"] == 3


# ========================================================================================
# 5. SECURE SESSION COOKIE & PRIVILEGE REDACTION TESTS
# ========================================================================================
class TestSessionCookieHardening:
    """Verifies RFC 6265 compliant session cookies and RBAC metadata redaction."""

    def test_session_cookie_structure(self):
        token = "sample.jwt.token"
        cookie = build_session_cookie(token, max_age=3600, same_site="Strict")
        assert f"{SESSION_COOKIE_NAME}={token}" in cookie
        assert "Max-Age=3600" in cookie
        assert "Path=/" in cookie
        assert "HttpOnly" in cookie
        assert "SameSite=Strict" in cookie

    def test_session_cookie_production_secure_enforcement(self, monkeypatch):
        token = "prod.jwt.token"
        monkeypatch.setenv("VOLTCORE_ENV", "production")
        prod_cookie = build_session_cookie(token)
        assert "Secure" in prod_cookie

        monkeypatch.delenv("VOLTCORE_ENV", raising=False)
        dev_cookie = build_session_cookie(token, secure=False)
        assert "Secure" not in dev_cookie

    def test_extract_token_from_cookie(self):
        sample_jwt = "header.payload.signature"
        header = f"theme=cyan; {SESSION_COOKIE_NAME}={sample_jwt}; lang=en"
        extracted = extract_token_from_cookie(header)
        assert extracted == sample_jwt

        # Missing cookie returns None
        assert extract_token_from_cookie("theme=dark; other=123") is None
        assert extract_token_from_cookie("") is None

    def test_clear_session_cookie(self):
        cleared = build_clear_session_cookie()
        assert f"{SESSION_COOKIE_NAME}=" in cleared
        assert "Max-Age=0" in cleared
        assert "Thu, 01 Jan 1970" in cleared

    def test_admin_audit_metadata_unprivileged_redaction(self):
        student_meta = get_admin_audit_metadata(role="Student")
        assert student_meta["rbac_access_level"] == "PUBLIC_UNPRIVILEGED"
        assert "[REDACTED" in student_meta["admin_email"]
        assert "[REDACTED" in student_meta["admin_phone"]

        admin_meta = get_admin_audit_metadata(role="Admin")
        assert admin_meta["rbac_access_level"] == "PRIVILEGED_ADMIN_ACCESS"
        assert "[REDACTED" not in admin_meta["admin_email"]
        assert "@" in admin_meta["admin_email"]


