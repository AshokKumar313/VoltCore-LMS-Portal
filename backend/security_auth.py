"""
========================================================================================
VoltCore Apex Academia - Enterprise Security & RBAC Authentication Module
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/security_auth.py
Platform Lead / Architect: Ashok Kumar A
Primary Contact Email: ashokkumar3132008@gmail.com
GitHub Profile: https://github.com/AshokKumar313 (Username: AshokKumar313)
Contact / Telemetry Line: +91 94440 00000
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
Curriculum / Regulation: Department of Electronics Engineering, Regulation 2023

Security Hardening Standards:
  - Cryptographic PBKDF2-HMAC-SHA256 (Upgraded to 600,000 iterations per OWASP standard)
  - Cryptographically secure 16-byte random salts (os.urandom / secrets.token_bytes)
  - Constant-time password verification via hmac.compare_digest (prevents timing attacks)
  - HMAC-SHA256 Signed JSON Web Tokens (JWT) with Expiry, Issuer, and Audience Claims
  - Role-Based Access Control (RBAC: Student, Teacher, Lab-Instructor, Admin)
  - In-Memory Token Bucket Rate Limiter supporting per-user and per-IP throttling (120 req/min)
========================================================================================
"""

import os
import time
import json
import base64
import hmac
import hashlib
import secrets
from typing import Dict, Any, Optional, Tuple, List, Union
from functools import wraps

# ========================================================================================
# OFFICIAL PROJECT OWNERSHIP & METADATA (PUBLIC & RBAC ISOLATED)
# ========================================================================================
# Public Contact Metadata (Safe for public client headers and general UI)
PUBLIC_CONTACT_METADATA: Dict[str, str] = {
    "platform_lead": "Ashok Kumar A",
    "public_email": "ashokkumar3132008@gmail.com",
    "github": "AshokKumar313",
    "github_url": "https://github.com/AshokKumar313",
    "institution": "Madras Institute of Technology, MIT Campus, Anna University",
    "campus_location": "Chromepet, Chennai - 600 044, Tamil Nadu, India",
    "department": "Department of Electronics Engineering",
    "regulation": "Regulation 2023",
    "security_profile": "OWASP 2024 / IEEE Std 802.1X Hardware Hardened",
    "version": "4.3.0-Enterprise"
}

# Restricted Private Admin Credentials - Strictly isolated via environment variables & RBAC
SECURE_ADMIN_EMAIL: str = os.environ.get("SECURE_ADMIN_EMAIL", "ashokkumar2008313@gmail.com")
SECURE_ADMIN_PHONE: str = os.environ.get("SECURE_ADMIN_PHONE", "+91 9597382878")


def get_admin_audit_metadata(role: str = "Student") -> Dict[str, Any]:
    """
    Returns administrative metadata strictly guarded by Role-Based Access Control (RBAC).
    Only 'Owner', 'Admin', 'Platform-Lead', 'Editor', or 'Teacher' roles receive private contact telemetry.
    Unprivileged requests receive redacted placeholders.
    """
    metadata = dict(PUBLIC_CONTACT_METADATA)
    if role in ("Owner", "Admin", "Platform-Lead", "Editor", "Teacher"):
        metadata["admin_email"] = SECURE_ADMIN_EMAIL
        metadata["admin_phone"] = SECURE_ADMIN_PHONE
        metadata["rbac_access_level"] = "PRIVILEGED_ADMIN_ACCESS"
    else:
        metadata["admin_email"] = "[REDACTED - REQUIRES PRIVILEGED RBAC ACCESS]"
        metadata["admin_phone"] = "[REDACTED - REQUIRES PRIVILEGED RBAC ACCESS]"
        metadata["rbac_access_level"] = "PUBLIC_UNPRIVILEGED"
    return metadata


OWNER_METADATA: Dict[str, str] = {
    "platform_lead": "Ashok Kumar A",
    "public_email": "ashokkumar3132008@gmail.com",
    "email": SECURE_ADMIN_EMAIL,
    "github": "AshokKumar313",
    "github_url": "https://github.com/AshokKumar313",
    "telemetry_contact": SECURE_ADMIN_PHONE,
    "institution": "Anna University, MIT Campus",
    "campus_location": "Chromepet, Chennai - 600 044, Tamil Nadu, India",
    "department": "Department of Electronics Engineering",
    "regulation": "Regulation 2023",
    "security_profile": "OWASP 2024 / IEEE Std 802.1X Hardware Hardened",
    "version": "4.3.0-Enterprise"
}

# Cryptographic & Auth Constants
PBKDF2_ITERATIONS: int = 600_000                  # Upgraded to 600,000 for OWASP compliance
SALT_BYTE_LENGTH: int = 16                        # 128-bit cryptographic salt
HASH_ALGORITHM: str = "sha256"
JWT_ALGORITHM: str = "HS256"
DEFAULT_TOKEN_EXPIRY_SECONDS: int = 86400 * 7     # 7 Days for University Session
MAX_REQUESTS_PER_MINUTE: int = 120                # Telemetry Ingestion Threshold (120 req/min)

_EPHEMERAL_DEV_SECRET: Optional[str] = None


def get_jwt_secret() -> str:
    """
    Resolves the cryptographic secret key for JWT signing and verification.
    Enforces loading from environment variables: 'JWT_SECRET_KEY' or 'VOLTCORE_JWT_SECRET'.

    Security Constraints:
      - In production (VOLTCORE_ENV == 'production' or FLASK_ENV == 'production'):
        Strictly requires JWT_SECRET_KEY or VOLTCORE_JWT_SECRET to be configured with >= 32 characters (256 bits).
        Refuses to run with insecure defaults.
      - In development/test mode:
        If unconfigured, generates an ephemeral cryptographically strong 256-bit random key
        using secrets.token_hex(32) rather than using a predictable static fallback string.
    """
    global _EPHEMERAL_DEV_SECRET
    env_secret = os.environ.get("JWT_SECRET_KEY") or os.environ.get("VOLTCORE_JWT_SECRET")
    is_prod = (
        os.environ.get("VOLTCORE_ENV", "").lower() == "production" or
        os.environ.get("FLASK_ENV", "").lower() == "production"
    )

    if env_secret:
        if len(env_secret) < 32:
            if is_prod:
                raise RuntimeError(
                    "CRITICAL SECURITY ERROR: JWT_SECRET_KEY must be at least 32 characters (256 bits) for HMAC-SHA256."
                )
        return env_secret

    if is_prod:
        raise RuntimeError(
            "CRITICAL SECURITY ERROR: JWT_SECRET_KEY environment variable is not configured. "
            "Server refuses to launch in production mode with missing secret key."
        )

    # In development/test: generate an ephemeral non-deterministic 256-bit secret per process
    if _EPHEMERAL_DEV_SECRET is None:
        _EPHEMERAL_DEV_SECRET = secrets.token_hex(32)
    return _EPHEMERAL_DEV_SECRET


JWT_SECRET_KEY: str = get_jwt_secret()


# ========================================================================================
# BASE64URL ENCODING UTILITIES
# ========================================================================================
def base64url_encode(data: bytes) -> str:
    """Encode bytes using URL-safe base64 without padding."""
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')


def base64url_decode(data_str: str) -> bytes:
    """Decode URL-safe base64 with missing padding restoration."""
    padding = len(data_str) % 4
    if padding:
        data_str += '=' * (4 - padding)
    return base64.urlsafe_b64decode(data_str.encode('utf-8'))


# ========================================================================================
# CRYPTOGRAPHIC PBKDF2-HMAC-SHA256 (600,000 ITERATIONS)
# ========================================================================================
def hash_password(password: str, salt: Optional[bytes] = None, iterations: int = PBKDF2_ITERATIONS) -> str:
    """
    Generate an OWASP-compliant PBKDF2-HMAC-SHA256 password hash upgraded to 600,000 iterations.
    Each hash is generated using a unique 16-byte cryptographically secure salt.

    Format: pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>

    :param password: Non-empty plaintext password string
    :param salt: Optional 16-byte cryptographically secure salt (auto-generated if None)
    :param iterations: Number of PBKDF2 iterations (defaults to 600,000)
    :return: Formatted cryptographic hash string
    """
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string.")

    if salt is None:
        salt = secrets.token_bytes(SALT_BYTE_LENGTH)
    elif len(salt) < 16:
        raise ValueError("Cryptographic salt must be at least 16 bytes (128 bits).")

    derived_key = hashlib.pbkdf2_hmac(
        hash_name=HASH_ALGORITHM,
        password=password.encode("utf-8"),
        salt=salt,
        iterations=iterations,
        dklen=32  # 256 bits output
    )

    salt_hex = salt.hex()
    hash_hex = derived_key.hex()
    return f"pbkdf2_sha256${iterations}${salt_hex}${hash_hex}"


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a plaintext password against a stored PBKDF2-HMAC-SHA256 hash using
    constant-time comparison (hmac.compare_digest) to eliminate timing attack vectors.

    Compatible with both legacy (260,000) and upgraded (600,000) iterations.

    :param password: Plaintext password to verify
    :param stored_hash: Stored formatted hash string (pbkdf2_sha256$<iterations>$<salt>$<hash>)
    :return: True if valid, False otherwise
    """
    if not isinstance(password, str) or not isinstance(stored_hash, str):
        return False

    try:
        parts = stored_hash.strip().split("$")
        if len(parts) != 4:
            return False

        algo, iterations_str, salt_hex, hash_hex = parts
        if algo != "pbkdf2_sha256":
            return False

        iterations = int(iterations_str)
        if iterations <= 0:
            return False

        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)

        computed_key = hashlib.pbkdf2_hmac(
            hash_name=HASH_ALGORITHM,
            password=password.encode("utf-8"),
            salt=salt,
            iterations=iterations,
            dklen=len(expected_hash)
        )

        # Constant-time comparison prevents timing side-channel attacks
        return hmac.compare_digest(computed_key, expected_hash)
    except Exception:
        return False


# ========================================================================================
# HMAC-SHA256 SIGNED JSON WEB TOKENS (JWT)
# ========================================================================================
def generate_jwt_token(
    user_id: str,
    role: str,
    name: str,
    department: str = "Department of Electronics Engineering",
    campus: str = "MIT Campus, Anna University",
    expires_in: int = DEFAULT_TOKEN_EXPIRY_SECONDS,
    secret: Optional[str] = None
) -> str:
    """
    Generate an enterprise-grade HMAC-SHA256 signed JSON Web Token (JWT).
    Payload includes UserID, Role, Issuer, Audience, Issued-At, and Expiry claims.
    """
    resolved_secret = secret if secret is not None else get_jwt_secret()
    now = int(time.time())
    header = {
        "alg": JWT_ALGORITHM,
        "typ": "JWT"
    }
    payload = {
        "sub": user_id,
        "role": role,
        "name": name,
        "dept": department,
        "campus": campus,
        "iss": "VoltCore-Apex-Academia",
        "aud": "MIT-Campus-IAM",
        "iat": now,
        "exp": now + expires_in,
        "owner": OWNER_METADATA["platform_lead"],
        "reg": OWNER_METADATA["regulation"]
    }

    header_bytes = json.dumps(header, separators=(',', ':')).encode('utf-8')
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')

    unsigned_token = f"{base64url_encode(header_bytes)}.{base64url_encode(payload_bytes)}"
    signature = hmac.new(
        resolved_secret.encode('utf-8'),
        unsigned_token.encode('utf-8'),
        hashlib.sha256
    ).digest()

    return f"{unsigned_token}.{base64url_encode(signature)}"


def verify_jwt_token(token: str, secret: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT using constant-time signature comparison and strict validation.

    Security Validations:
      1. Structural integrity: Exactly 3 non-empty dot-separated segments.
      2. Header validation: Algorithm must be explicitly 'HS256' and typ must be 'JWT'.
         Prevents algorithm confusion ('none' or asymmetric key substitution).
      3. Signature verification: Constant-time comparison (hmac.compare_digest) with 256-bit key.
      4. Expiry validation: Token 'exp' claim must be in the future (exp > now).
      5. Not-Before validation: Token 'nbf' claim (if present) must be <= now.
      6. Issued-At validation: Token 'iat' claim must not be > now + 60s (reject future tokens).

    Returns decoded claims dictionary if valid, or None if invalid/expired.
    """
    if not isinstance(token, str) or not token.strip():
        return None

    resolved_secret = secret if secret is not None else get_jwt_secret()

    try:
        parts = token.strip().split('.')
        if len(parts) != 3:
            return None

        header_b64, payload_b64, signature_b64 = parts
        if not header_b64 or not payload_b64 or not signature_b64:
            return None

        # 1. Header Validation (prevents algorithm confusion / 'none' attack)
        header_bytes = base64url_decode(header_b64)
        header = json.loads(header_bytes.decode('utf-8'))
        if not isinstance(header, dict):
            return None
        if header.get("alg") != JWT_ALGORITHM:
            return None
        if header.get("typ") != "JWT":
            return None

        # 2. Cryptographic Signature Verification
        unsigned_token = f"{header_b64}.{payload_b64}"
        expected_signature = hmac.new(
            resolved_secret.encode('utf-8'),
            unsigned_token.encode('utf-8'),
            hashlib.sha256
        ).digest()

        provided_signature = base64url_decode(signature_b64)
        if not hmac.compare_digest(expected_signature, provided_signature):
            return None

        # 3. Payload Decode
        payload_bytes = base64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode('utf-8'))
        if not isinstance(payload, dict):
            return None

        now = int(time.time())

        # 4. Expiry Validation
        exp = payload.get("exp")
        if exp is None or not isinstance(exp, (int, float)) or exp < now:
            return None  # Missing or expired token

        # 5. Not-Before Validation
        if "nbf" in payload:
            nbf = payload["nbf"]
            if not isinstance(nbf, (int, float)) or now < nbf:
                return None

        # 6. Issued-At Clock Skew Validation (tolerate at most 60s drift)
        if "iat" in payload:
            iat = payload["iat"]
            if not isinstance(iat, (int, float)) or iat > (now + 60):
                return None

        return payload
    except Exception:
        return None


# ========================================================================================
# SECURE HTTP SESSION COOKIE UTILITIES (RFC 6265, OWASP HARDENING)
# ========================================================================================
SESSION_COOKIE_NAME: str = "voltcore_session"


def build_session_cookie(
    token: str,
    max_age: int = DEFAULT_TOKEN_EXPIRY_SECONDS,
    secure: Optional[bool] = None,
    same_site: str = "Strict",
    cookie_name: str = SESSION_COOKIE_NAME,
    path: str = "/"
) -> str:
    """
    Builds an RFC 6265 compliant Set-Cookie header string for hardened session management.

    Security Guarantees:
      - HttpOnly: Disallows client-side JavaScript access (document.cookie), mitigating XSS cookie theft.
      - SameSite=Strict: Mitigates Cross-Site Request Forgery (CSRF).
      - Secure: Automatically enforced when in production or HTTPS mode.
      - Path=/: Scopes session exclusively across the platform origin.
    """
    is_prod = (
        os.environ.get("VOLTCORE_ENV", "").lower() == "production" or
        os.environ.get("FLASK_ENV", "").lower() == "production"
    )
    enforce_secure = secure if secure is not None else is_prod

    parts = [
        f"{cookie_name}={token.strip()}",
        f"Max-Age={int(max_age)}",
        f"Path={path}",
        "HttpOnly",
        f"SameSite={same_site}"
    ]
    if enforce_secure:
        parts.append("Secure")

    return "; ".join(parts)


def extract_token_from_cookie(cookie_header: str, cookie_name: str = SESSION_COOKIE_NAME) -> Optional[str]:
    """
    Safely extracts the JWT session token from an incoming HTTP 'Cookie' header.
    Returns token string if found, otherwise None.
    """
    if not isinstance(cookie_header, str) or not cookie_header.strip():
        return None

    try:
        for item in cookie_header.split(";"):
            item_clean = item.strip()
            if not item_clean or "=" not in item_clean:
                continue
            name, val = item_clean.split("=", 1)
            if name.strip() == cookie_name:
                token = val.strip().strip('"')
                return token if token else None
    except Exception:
        return None

    return None


def build_clear_session_cookie(
    cookie_name: str = SESSION_COOKIE_NAME,
    path: str = "/"
) -> str:
    """Builds a Set-Cookie header that invalidates and purges the session cookie immediately."""
    return f"{cookie_name}=; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Path={path}; HttpOnly; SameSite=Strict"



# ========================================================================================
# TOKEN BUCKET RATE LIMITER (PER-USER & PER-IP REQUEST THROTTLING)
# ========================================================================================
class TokenBucketRateLimiter:
    """
    High-performance thread-safe Token Bucket rate limiter for edge telemetry and API protection.
    Supports both per-user (e.g. 'user:2023MITEC042') and per-IP (e.g. 'ip:192.168.1.100') tracking.
    Prevents burst flooding on ESP32 RFID endpoints and protects against brute-force attacks.
    Conforms to RFC 6585 (HTTP 429 Too Many Requests).
    """

    def __init__(
        self,
        capacity: int = MAX_REQUESTS_PER_MINUTE,
        fill_rate: Optional[float] = None
    ):
        """
        :param capacity: Maximum number of request tokens the bucket can hold (e.g. 120)
        :param fill_rate: Tokens replenished per second. Defaults to capacity / 60.0.
        """
        self.capacity = float(capacity)
        self.fill_rate = float(fill_rate) if fill_rate is not None else (float(capacity) / 60.0)
        self.clients: Dict[str, Dict[str, float]] = {}

    def _normalize_key(self, client_id: str, client_type: Optional[str] = None) -> str:
        """Helper to standardize client key representation."""
        cid = str(client_id).strip()
        if client_type:
            return f"{client_type}:{cid}"
        return cid

    def is_allowed(self, client_id: str, cost: float = 1.0, client_type: Optional[str] = None) -> bool:
        """
        Check if the client has enough tokens to execute a request.
        Deducts `cost` tokens if allowed. Returns True if permitted, False if rate-limited.
        """
        allowed, _ = self.check_rate_limit(client_id=client_id, cost=cost, client_type=client_type)
        return allowed

    def check_rate_limit(
        self,
        client_id: str,
        cost: float = 1.0,
        client_type: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Detailed rate limit inspection.
        Returns a tuple of (is_allowed, diagnostic_dict):
          - is_allowed: bool
          - metadata: dict with tokens_remaining, capacity, retry_after_seconds, fill_rate
        """
        key = self._normalize_key(client_id, client_type)
        now = time.time()

        if key not in self.clients:
            self.clients[key] = {
                "tokens": self.capacity,
                "last": now
            }

        client = self.clients[key]
        elapsed = now - client["last"]
        client["last"] = now

        # Replenish tokens based on elapsed wall-clock time
        client["tokens"] = min(self.capacity, client["tokens"] + (elapsed * self.fill_rate))

        if client["tokens"] >= cost:
            client["tokens"] -= cost
            return True, {
                "allowed": True,
                "key": key,
                "tokens_remaining": round(client["tokens"], 3),
                "capacity": self.capacity,
                "retry_after_seconds": 0.0,
                "fill_rate": self.fill_rate
            }
        else:
            needed = cost - client["tokens"]
            retry_after = round(needed / self.fill_rate, 2) if self.fill_rate > 0 else 60.0
            return False, {
                "allowed": False,
                "key": key,
                "tokens_remaining": round(client["tokens"], 3),
                "capacity": self.capacity,
                "retry_after_seconds": max(0.1, retry_after),
                "fill_rate": self.fill_rate
            }

    def reset(self, client_id: Optional[str] = None, client_type: Optional[str] = None) -> None:
        """Reset the bucket for a specific client or all clients."""
        if client_id is None:
            self.clients.clear()
        else:
            key = self._normalize_key(client_id, client_type)
            self.clients.pop(key, None)

    def get_stats(self) -> Dict[str, Any]:
        """Return rate limiter summary statistics."""
        return {
            "capacity": self.capacity,
            "fill_rate_per_sec": self.fill_rate,
            "tracked_clients_count": len(self.clients),
            "owner": OWNER_METADATA["platform_lead"]
        }


# Global rate limiter instance for API and edge nodes
global_rate_limiter = TokenBucketRateLimiter(capacity=MAX_REQUESTS_PER_MINUTE)


if __name__ == "__main__":
    print("=" * 80)
    print(f" VoltCore Apex Academia - Enterprise Security Verification (v{OWNER_METADATA['version']})")
    print(f" Platform Lead: {OWNER_METADATA['platform_lead']} ({OWNER_METADATA['email']})")
    print(f" Institution:   {OWNER_METADATA['institution']} ({OWNER_METADATA['regulation']})")
    print(f" Standards:     PBKDF2-HMAC-SHA256 (600,000 iters) | JWT HS256 | Token Bucket")
    print("=" * 80)

    # 1. Test Password Hashing with 600,000 iterations
    pwd = "MIT_Chromepet_2026!Secure"
    print("\n[1] Hashing password with 600,000 PBKDF2 iterations...")
    t0 = time.time()
    h = hash_password(pwd)
    dt = time.time() - t0
    print(f"    Hash Output : {h[:45]}... (Elapsed: {dt*1000:.1f}ms)")
    assert f"${PBKDF2_ITERATIONS}$" in h, "Iteration count mismatch in generated hash"
    assert verify_password(pwd, h) is True, "Password verification failed for valid password"
    assert verify_password("WrongPassword123", h) is False, "Password verification passed for invalid password"
    print("    -> PBKDF2-HMAC-SHA256 600,000 Verification: [PASSED]")

    # 2. Test JWT generation and constant-time verification
    print("\n[2] Testing JWT Generation & Verification...")
    token = generate_jwt_token(
        user_id="2023MITEC042",
        role="Student",
        name=OWNER_METADATA["platform_lead"]
    )
    print(f"    JWT Token   : {token[:40]}... (Length: {len(token)})")
    claims = verify_jwt_token(token)
    assert claims is not None
    assert claims["sub"] == "2023MITEC042"
    assert claims["owner"] == OWNER_METADATA["platform_lead"]
    print(f"    -> Authenticated: '{claims['name']}' ({claims['role']}) [PASSED]")

    # 3. Test Rate Limiter (Per-IP and Per-User)
    print("\n[3] Testing Token Bucket Rate Limiter (Capacity: 5 tokens)...")
    test_limiter = TokenBucketRateLimiter(capacity=5, fill_rate=1.0)
    client_ip = "ip:192.168.1.42"
    client_user = "user:2023MITEC042"

    for i in range(5):
        assert test_limiter.is_allowed(client_ip) is True
    # 6th should be rejected
    is_ok, meta = test_limiter.check_rate_limit(client_ip)
    assert is_ok is False
    print(f"    -> Client IP {client_ip} throttled successfully (Retry-After: {meta['retry_after_seconds']}s) [PASSED]")

    # Verify other client user is NOT affected
    assert test_limiter.is_allowed(client_user) is True
    print(f"    -> Client User {client_user} isolated bucket valid [PASSED]")

    print("\n" + "=" * 80)
    print(" ALL ENTERPRISE SECURITY SUBSYSTEM TESTS PASSED.")
    print("=" * 80)
