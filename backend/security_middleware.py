"""
========================================================================================
VoltCore Apex Academia - Enterprise Security Middleware & Header Hardening
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/security_middleware.py
Platform Lead / Architect: Ashok Kumar A
Primary Contact Email: ashokkumar2008313@gmail.com
GitHub Profile: https://github.com/AshokKumar313 (Username: AshokKumar313)
Contact / Telemetry Line: +91 9597382878
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
Curriculum / Regulation: Department of Electronics Engineering, Regulation 2023

Security Hardening Components:
  - HTTP Response Header Hardening (Strict CSP, nosniff, DENY frame options, XSS block)
  - Strict Content-Type & JSON Payload Schema Validator (@validate_json_payload)
  - Rate Limiting Enforcement Decorator (@rate_limited)
  - Ownership & Academic Telemetry Headers
========================================================================================
"""

import os
import sys
import json
from functools import wraps
from typing import Dict, Any, Optional, Tuple, List, Callable, Union

# Ensure root and backend directories are in sys.path for direct script or package execution
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Import rate limiter and owner metadata
try:
    from backend.security_auth import (
        global_rate_limiter,
        TokenBucketRateLimiter,
        OWNER_METADATA,
        PUBLIC_CONTACT_METADATA,
        get_admin_audit_metadata
    )
except ImportError:
    from security_auth import (
        global_rate_limiter,
        TokenBucketRateLimiter,
        OWNER_METADATA,
        PUBLIC_CONTACT_METADATA,
        get_admin_audit_metadata
    )

# Optional Flask import with seamless fallback for tests and custom HTTP servers
try:
    from flask import request as flask_request, jsonify as flask_jsonify, make_response as flask_make_response
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False
    flask_request = None
    flask_jsonify = None
    flask_make_response = None


# ========================================================================================
# ENTERPRISE SECURITY HEADERS CONFIGURATION
# ========================================================================================
STRICT_CSP_POLICY = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com data:; "
    "img-src 'self' data: https: blob:; "
    "connect-src 'self' http://localhost:5000 http://127.0.0.1:5000 ws: wss:; "
    "frame-ancestors 'none'; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self';"
)

SECURITY_HEADERS: Dict[str, str] = {
    # Content Security Policy preventing XSS and unwanted script execution
    "Content-Security-Policy": STRICT_CSP_POLICY,
    # Prevent MIME-type sniffing
    "X-Content-Type-Options": "nosniff",
    # Prevent clickjacking attacks by forbidding iframe embedding
    "X-Frame-Options": "DENY",
    # Legacy XSS filtering protection
    "X-XSS-Protection": "1; mode=block",
    # Control HTTP referrer leakage
    "Referrer-Policy": "strict-origin-when-cross-origin",
    # Restrict risky browser hardware features
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    # Project Ownership & Academic Telemetry Headers (Public Contact Only)
    "X-Lead-Architect": PUBLIC_CONTACT_METADATA["platform_lead"],
    "X-Architect-Contact": PUBLIC_CONTACT_METADATA["public_email"],
    "X-Architect-GitHub": PUBLIC_CONTACT_METADATA["github"],
    "X-Academic-Institution": f"{PUBLIC_CONTACT_METADATA['institution']} ({PUBLIC_CONTACT_METADATA['regulation']})",
    "X-VoltCore-Security": "Phase-3-Hardened-RBAC-Isolated"
}


# ========================================================================================
# RESPONSE HEADER HARDENING HOOK
# ========================================================================================
def add_security_headers(response: Any) -> Any:
    """
    Hardens any HTTP response by injecting OWASP security headers.
    Supports Flask Response objects, custom response classes, or header dictionaries.
    
    :param response: Flask Response object, custom response object, or dict
    :return: Modified response with security headers attached
    """
    if hasattr(response, "headers"):
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
    elif isinstance(response, dict) and "headers" in response:
        response["headers"].update(SECURITY_HEADERS)
    return response


# ========================================================================================
# JSON PAYLOAD SCHEMA & CONTENT-TYPE VALIDATION DECORATOR
# ========================================================================================
def validate_json_payload(*required_fields: str, schema: Optional[Dict[str, Union[type, tuple]]] = None):
    """
    Decorator for API endpoints that strictly enforces:
      1. Content-Type is 'application/json'
      2. Non-empty, valid JSON request body
      3. Presence of all specified `required_fields`
      4. Optional type validation according to `schema` mapping

    Returns 415 Unsupported Media Type for non-JSON content.
    Returns 400 Bad Request for malformed JSON.
    Returns 422 Unprocessable Entity for missing required fields or type mismatches.
    """
    def decorator(f: Callable):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Resolve current request context (Flask request or passed mock object)
            req = kwargs.pop("_mock_request", None)
            if req is None:
                if HAS_FLASK and flask_request:
                    req = flask_request
                elif args and hasattr(args[0], "headers"):
                    req = args[0]

            if req is None:
                err = {
                    "status": "error",
                    "code": "REQUEST_CONTEXT_MISSING",
                    "message": "No active request context found for payload validation."
                }
                return _create_error_response(err, 500)

            # 1. Content-Type Header Verification
            content_type = getattr(req, "content_type", None) or ""
            if not content_type and hasattr(req, "headers"):
                content_type = req.headers.get("Content-Type", "")

            # Ignore parameters like charset (e.g. 'application/json; charset=utf-8')
            media_type = content_type.split(";")[0].strip().lower()
            if media_type != "application/json":
                err = {
                    "status": "error",
                    "code": "INVALID_CONTENT_TYPE",
                    "message": f"Expected Content-Type 'application/json', received '{content_type or 'None'}'.",
                    "architect": OWNER_METADATA["platform_lead"]
                }
                return _create_error_response(err, 415)

            # 2. Extract JSON Body
            payload = None
            if hasattr(req, "get_json"):
                try:
                    payload = req.get_json(silent=True)
                except Exception:
                    payload = None
            elif hasattr(req, "json"):
                payload = req.json
            elif hasattr(req, "body"):
                try:
                    raw_body = req.body
                    if isinstance(raw_body, bytes):
                        raw_body = raw_body.decode("utf-8")
                    payload = json.loads(raw_body)
                except Exception:
                    payload = None

            if payload is None or not isinstance(payload, dict):
                err = {
                    "status": "error",
                    "code": "MALFORMED_JSON",
                    "message": "Request body must contain a valid, non-empty JSON object."
                }
                return _create_error_response(err, 400)

            # 3. Required Fields Verification
            missing = []
            for field in required_fields:
                if field not in payload:
                    missing.append(field)
                else:
                    val = payload[field]
                    if val is None or (isinstance(val, str) and not val.strip()):
                        missing.append(field)

            if missing:
                err = {
                    "status": "error",
                    "code": "MISSING_REQUIRED_FIELDS",
                    "missing_fields": missing,
                    "message": f"Missing or empty required fields: {', '.join(missing)}.",
                    "institution": OWNER_METADATA["institution"]
                }
                return _create_error_response(err, 422)

            # 4. Optional Type Schema Validation
            if schema:
                for field, expected_type in schema.items():
                    if field in payload and payload[field] is not None:
                        val = payload[field]
                        if not isinstance(val, expected_type):
                            type_name = expected_type.__name__ if hasattr(expected_type, "__name__") else str(expected_type)
                            err = {
                                "status": "error",
                                "code": "SCHEMA_TYPE_MISMATCH",
                                "field": field,
                                "expected_type": type_name,
                                "received_type": type(val).__name__,
                                "message": f"Field '{field}' must be of type {type_name}."
                            }
                            return _create_error_response(err, 422)

            # If handler accepts 'payload' as kwarg or positional, pass it
            if "payload" in f.__code__.co_varnames:
                kwargs["payload"] = payload

            # Execute the wrapped handler
            result = f(*args, **kwargs)
            return result
        return decorated_function
    return decorator


# ========================================================================================
# RATE LIMITING DECORATOR
# ========================================================================================
def rate_limited(
    limiter: Optional[TokenBucketRateLimiter] = None,
    cost: float = 1.0,
    per_user: bool = True
):
    """
    Endpoint rate-limiting decorator protecting against DoS and brute-force scans.
    Identifies clients by UserID (from JWT / payload) or remote IP address.
    """
    active_limiter = limiter or global_rate_limiter

    def decorator(f: Callable):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            req = kwargs.pop("_mock_request", None)
            if req is None:
                if HAS_FLASK and flask_request:
                    req = flask_request
                elif args and hasattr(args[0], "headers"):
                    req = args[0]

            client_key = "anonymous_client"
            if req is not None:
                # Extract client IP
                headers = getattr(req, "headers", {})
                ip = headers.get("X-Forwarded-For") or getattr(req, "remote_addr", None) or "127.0.0.1"
                if "," in ip:
                    ip = ip.split(",")[0].strip()

                # Extract optional user identifier
                user_id = None
                if per_user:
                    if hasattr(req, "get_json"):
                        p = req.get_json(silent=True) or {}
                        user_id = p.get("user_id") or p.get("student_id")
                    elif hasattr(req, "json") and isinstance(req.json, dict):
                        user_id = req.json.get("user_id") or req.json.get("student_id")

                client_key = f"user:{user_id}" if user_id else f"ip:{ip}"

            allowed, meta = active_limiter.check_rate_limit(client_key, cost=cost)
            if not allowed:
                err = {
                    "status": "error",
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Throttled by VoltCore security gateway.",
                    "client": client_key,
                    "retry_after_seconds": meta["retry_after_seconds"],
                    "capacity": meta["capacity"]
                }
                resp = _create_error_response(err, 429)
                if hasattr(resp, "headers"):
                    resp.headers["Retry-After"] = str(int(meta["retry_after_seconds"]) + 1)
                    resp.headers["X-RateLimit-Limit"] = str(int(meta["capacity"]))
                    resp.headers["X-RateLimit-Remaining"] = "0"
                return resp

            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ========================================================================================
# ERROR RESPONSE GENERATOR
# ========================================================================================
def _create_error_response(data: Dict[str, Any], status_code: int) -> Any:
    """Helper that creates an error response for Flask or fallback environments."""
    if HAS_FLASK and flask_make_response and flask_jsonify:
        try:
            resp = flask_make_response(flask_jsonify(data), status_code)
            return add_security_headers(resp)
        except Exception:
            pass

    # Fallback response representation: (json_dict, status_code, headers_dict)
    response_obj = {
        "body": data,
        "status_code": status_code,
        "headers": dict(SECURITY_HEADERS)
    }
    return response_obj, status_code


# ========================================================================================
# FLASK APPLICATION INITIALIZER
# ========================================================================================
def init_security_middleware(app: Any) -> None:
    """
    Hook security middleware into a Flask application:
      1. Registers after_request hook to apply security headers to every response.
      2. Logs initialization diagnostics.
    """
    if hasattr(app, "after_request"):
        app.after_request(add_security_headers)
        print(f"[VOLTCORE SECURITY]: Security headers and CSP registered for '{getattr(app, 'name', 'LMS')}'")


if __name__ == "__main__":
    print("=" * 80)
    print(" VoltCore Apex Academia - Security Middleware Diagnostics")
    print(f" Platform Lead: {OWNER_METADATA['platform_lead']} ({OWNER_METADATA['email']})")
    print(f" Institution:   {OWNER_METADATA['institution']}")
    print("=" * 80)

    # Test Security Headers presence
    print("\n[1] Verifying Hardened Response Headers...")
    for h, v in SECURITY_HEADERS.items():
        print(f"    • {h:<26}: {v[:50]}...")
    assert "Content-Security-Policy" in SECURITY_HEADERS
    assert SECURITY_HEADERS["X-Frame-Options"] == "DENY"
    assert SECURITY_HEADERS["X-Content-Type-Options"] == "nosniff"
    print("    -> Security Headers Verification: [PASSED]")

    # Test Mock Request Validation
    print("\n[2] Testing @validate_json_payload decorator...")
    class MockReq:
        def __init__(self, content_type: str, body: dict):
            self.content_type = content_type
            self.headers = {"Content-Type": content_type}
            self._json = body
        def get_json(self, silent=True):
            return self._json

    @validate_json_payload("student_id", "rfid_uid")
    def sample_api_handler(payload=None):
        return {"status": "success", "data": payload}, 200

    # 2a. Reject non-JSON
    res, code = sample_api_handler(_mock_request=MockReq("text/plain", {}))
    assert code == 415, f"Expected 415, got {code}"
    print("    -> Non-JSON Content-Type correctly rejected with HTTP 415 [PASSED]")

    # 2b. Reject missing required fields
    res, code = sample_api_handler(_mock_request=MockReq("application/json", {"student_id": "2023MITEC042"}))
    assert code == 422, f"Expected 422, got {code}"
    print("    -> Missing 'rfid_uid' correctly rejected with HTTP 422 [PASSED]")

    # 2c. Accept complete payload
    res, code = sample_api_handler(_mock_request=MockReq("application/json", {"student_id": "2023MITEC042", "rfid_uid": "E2 80 6F 3B"}))
    assert code == 200, f"Expected 200, got {code}"
    print("    -> Valid payload correctly processed with HTTP 200 [PASSED]")

    print("\n" + "=" * 80)
    print(" ALL SECURITY MIDDLEWARE TESTS PASSED.")
    print("=" * 80)
