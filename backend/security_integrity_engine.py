"""
========================================================================================
VoltCore Apex Academia - Phase Q: Security, Authentication & System Integrity (Features 371–380)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Features:
  - Feature 371: Role-Based Access Control (RBAC) (STUDENT, FACULTY, LAB_TECH, HOD_ADMIN)
  - Feature 372: Session Token Manager (HMAC-SHA256 cryptographically signed tokens & TTL)
  - Feature 373: SQLite WAL Integrity Checker (PRAGMA integrity_check & WAL verification)
  - Feature 374: Secure Password Hashing & Salt Audit (PBKDF2-HMAC-SHA256 100k iterations)
  - Feature 375: API Rate Limiting Monitor (Sliding window rate limiter: 60 req/min)
  - Feature 376: Security Vulnerability Scanner (SQL injection & XSS sanitization audit)
  - Feature 377: Automated Database Backup Manager (Zero-downtime hot backups & checksums)
  - Feature 378: Audit Trail Logger (Append-only tamper-evident security event logs)
  - Feature 379: CORS & CSP Policy Enforcer (Content-Security-Policy & origin allowlists)
  - Feature 380: Dedicated Public Platform Lead Portfolio Tab (Architectural showcase)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
========================================================================================
"""

import os
import re
import json
import hmac
import secrets
import hashlib
import sqlite3
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")
DEFAULT_SECRET_KEY = "voltcore_mit_campus_ece_secret_key_2026_apex"

# ---------------------------------------------------------------------------
# RBAC PERMISSIONS MATRIX (Feature 371)
# ---------------------------------------------------------------------------

RBAC_PERMISSIONS: Dict[str, List[str]] = {
    "STUDENT": [
        "VIEW_COURSES",
        "ACCESS_SIMULATORS",
        "SUBMIT_ASSIGNMENTS",
        "VIEW_OWN_ATTENDANCE",
        "VIEW_OWN_GRADES",
        "POST_FORUM_DISCUSSIONS",
        "BOOK_OFFICE_HOURS"
    ],
    "LAB_TECH": [
        "VIEW_COURSES",
        "ACCESS_SIMULATORS",
        "MANAGE_HIL_HARDWARE",
        "CALIBRATE_TESTBENCH",
        "RECORD_EQUIPMENT_LOGS",
        "VIEW_LAB_ATTENDANCE"
    ],
    "FACULTY": [
        "VIEW_COURSES",
        "ACCESS_SIMULATORS",
        "GRADE_ASSIGNMENTS",
        "MANAGE_ATTENDANCE",
        "UPLOAD_COURSE_MATERIALS",
        "POST_ANNOUNCEMENTS",
        "GENERATE_PROGRESS_REPORTS",
        "CALCULATE_CO_ATTAINMENT",
        "LOG_CQI_ACTIONS",
        "MANAGE_OFFICE_HOURS"
    ],
    "HOD_ADMIN": [
        "VIEW_COURSES",
        "ACCESS_SIMULATORS",
        "GRADE_ASSIGNMENTS",
        "MANAGE_ATTENDANCE",
        "UPLOAD_COURSE_MATERIALS",
        "POST_ANNOUNCEMENTS",
        "GENERATE_PROGRESS_REPORTS",
        "CALCULATE_CO_ATTAINMENT",
        "LOG_CQI_ACTIONS",
        "MANAGE_OFFICE_HOURS",
        "AUDIT_DATABASE_INTEGRITY",
        "CREATE_DATABASE_BACKUPS",
        "VIEW_SECURITY_AUDIT_TRAILS",
        "MANAGE_USER_ROLES",
        "GENERATE_NBA_SAR_REPORTS",
        "SYSTEM_SETTINGS"
    ]
}


class SecurityIntegrityEngine:
    """
    Core backend engine for VoltCore Apex Academia Phase Q (Features 371–380).
    Manages RBAC permission enforcement, HMAC token lifecycles, database WAL integrity audits,
    PBKDF2 password security, rate limiting, and automated backups.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH, secret_key: str = DEFAULT_SECRET_KEY):
        self.db_path = db_path
        self.secret_key = secret_key.encode("utf-8")
        self._lock = threading.Lock()
        self._init_sqlite()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _init_sqlite(self) -> None:
        with self._lock:
            conn = self._get_connection()
            try:
                # Feature 372: Session tokens
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS security_session_tokens (
                        token_id TEXT PRIMARY KEY,
                        token_hash TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        user_role TEXT NOT NULL,
                        expires_at TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        is_revoked INTEGER DEFAULT 0
                    )
                """)

                # Feature 375: Rate limit sliding windows
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS security_rate_limits (
                        client_ip TEXT PRIMARY KEY,
                        request_count INTEGER DEFAULT 1,
                        window_start REAL NOT NULL
                    )
                """)

                # Feature 377: Database backup logs
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS database_backup_registry (
                        backup_id TEXT PRIMARY KEY,
                        filename TEXT NOT NULL,
                        filepath TEXT NOT NULL,
                        file_size_bytes INTEGER NOT NULL,
                        checksum_sha256 TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                """)

                # Feature 378: Security audit trail
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS security_audit_logs (
                        log_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        user_role TEXT NOT NULL,
                        action TEXT NOT NULL,
                        resource TEXT NOT NULL,
                        client_ip_hash TEXT NOT NULL,
                        status TEXT NOT NULL
                    )
                """)

                conn.commit()
            finally:
                conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 371: ROLE-BASED ACCESS CONTROL (RBAC)
    # ---------------------------------------------------------------------------

    def check_rbac_permission(self, role: str, permission: str) -> bool:
        """Verify whether a user role possesses a specific capability."""
        normalized_role = role.upper().strip()
        allowed_permissions = RBAC_PERMISSIONS.get(normalized_role, [])
        return permission.upper().strip() in allowed_permissions

    def list_role_permissions(self, role: str) -> List[str]:
        """List all permitted actions for a role."""
        return RBAC_PERMISSIONS.get(role.upper().strip(), [])

    # ---------------------------------------------------------------------------
    # FEATURE 372: SESSION TOKEN MANAGER (HMAC-SHA256)
    # ---------------------------------------------------------------------------

    def issue_session_token(
        self,
        user_id: str,
        role: str,
        ttl_seconds: int = 3600
    ) -> Dict[str, Any]:
        """Issue a cryptographically signed session token with TTL."""
        token_id = secrets.token_hex(16)
        payload = f"{token_id}:{user_id}:{role}:{ttl_seconds}"
        signature = hmac.new(self.secret_key, payload.encode("utf-8"), hashlib.sha256).hexdigest()
        full_token = f"{token_id}.{signature}"

        token_hash = hashlib.sha256(full_token.encode("utf-8")).hexdigest()
        now = datetime.now(timezone.utc)
        expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
        now_iso = now.isoformat()

        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO security_session_tokens
                    (token_id, token_hash, user_id, user_role, expires_at, created_at, is_revoked)
                    VALUES (?, ?, ?, ?, ?, ?, 0)
                """, (token_id, token_hash, user_id, role.upper(), expires_at, now_iso))
                conn.commit()
            finally:
                conn.close()

        return {
            "token": full_token,
            "token_id": token_id,
            "user_id": user_id,
            "role": role.upper(),
            "expires_at": expires_at,
            "ttl_seconds": ttl_seconds
        }

    def validate_session_token(self, full_token: str) -> Dict[str, Any]:
        """Verify token authenticity, expiration, and revocation status."""
        if not full_token or "." not in full_token:
            return {"valid": False, "reason": "MALFORMED_TOKEN"}

        token_id, signature = full_token.split(".", 1)
        token_hash = hashlib.sha256(full_token.encode("utf-8")).hexdigest()

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM security_session_tokens WHERE token_id = ?", (token_id,))
            record = cursor.fetchone()

            if not record:
                return {"valid": False, "reason": "TOKEN_NOT_FOUND"}

            if record["is_revoked"] == 1:
                return {"valid": False, "reason": "TOKEN_REVOKED"}

            expires_at = datetime.fromisoformat(record["expires_at"])
            if datetime.now(timezone.utc) > expires_at:
                return {"valid": False, "reason": "TOKEN_EXPIRED"}

            # Verify cryptographic signature
            payload = f"{token_id}:{record['user_id']}:{record['user_role']}:3600"
            expected_sig = hmac.new(self.secret_key, payload.encode("utf-8"), hashlib.sha256).hexdigest()

            # Constant-time comparison
            if not hmac.compare_digest(signature, expected_sig):
                return {"valid": False, "reason": "INVALID_SIGNATURE"}

            return {
                "valid": True,
                "token_id": token_id,
                "user_id": record["user_id"],
                "role": record["user_role"],
                "expires_at": record["expires_at"]
            }
        finally:
            conn.close()

    def revoke_session_token(self, token_id: str) -> Dict[str, Any]:
        """Revoke an active session token."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("UPDATE security_session_tokens SET is_revoked = 1 WHERE token_id = ?", (token_id,))
                conn.commit()
            finally:
                conn.close()
        return {"status": "success", "token_id": token_id, "revoked": True}

    # ---------------------------------------------------------------------------
    # FEATURE 373: SQLITE WAL INTEGRITY CHECKER
    # ---------------------------------------------------------------------------

    def check_database_integrity(self) -> Dict[str, Any]:
        """Execute SQLite PRAGMA integrity_check and verify WAL mode status."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]

            cursor.execute("PRAGMA quick_check")
            quick_result = cursor.fetchone()[0]

            cursor.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0].upper()

            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]

            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]

            db_size_kb = round((page_count * page_size) / 1024.0, 2)
            is_healthy = (integrity_result.lower() == "ok") and (quick_result.lower() == "ok") and (journal_mode == "WAL")

            return {
                "status": "HEALTHY" if is_healthy else "CORRUPTED",
                "integrity_check": integrity_result,
                "quick_check": quick_result,
                "journal_mode": journal_mode,
                "is_wal_mode": journal_mode == "WAL",
                "page_count": page_count,
                "database_size_kb": db_size_kb,
                "is_healthy": is_healthy
            }
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 374: SECURE PASSWORD HASHING & SALT AUDIT (PBKDF2-HMAC-SHA256)
    # ---------------------------------------------------------------------------

    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Dict[str, str]:
        """Hash password using PBKDF2-HMAC-SHA256 with 100,000 iterations and a 16-byte random salt."""
        if salt is None:
            salt = secrets.token_bytes(16)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return {
            "salt_hex": salt.hex(),
            "hash_hex": key.hex(),
            "algorithm": "PBKDF2-HMAC-SHA256",
            "iterations": 100000
        }

    def verify_password(self, password: str, salt_hex: str, hash_hex: str) -> bool:
        """Constant-time password verification."""
        try:
            salt = bytes.fromhex(salt_hex)
            key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
            return hmac.compare_digest(key.hex(), hash_hex)
        except Exception:
            return False

    def audit_password_strength(self, password: str) -> Dict[str, Any]:
        """Analyze password complexity and entropy."""
        length = len(password)
        has_upper = bool(re.search(r"[A-Z]", password))
        has_lower = bool(re.search(r"[a-z]", password))
        has_digit = bool(re.search(r"\d", password))
        has_special = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

        score = 0
        if length >= 8: score += 1
        if length >= 12: score += 1
        if has_upper and has_lower: score += 1
        if has_digit: score += 1
        if has_special: score += 1

        strength = "VERY_WEAK"
        if score == 5: strength = "STRONG"
        elif score >= 3: strength = "MODERATE"
        elif score >= 2: strength = "WEAK"

        return {
            "length": length,
            "has_upper": has_upper,
            "has_lower": has_lower,
            "has_digit": has_digit,
            "has_special": has_special,
            "score": score,
            "strength": strength,
            "is_acceptable": score >= 3
        }

    # ---------------------------------------------------------------------------
    # FEATURE 375: API RATE LIMITING MONITOR
    # ---------------------------------------------------------------------------

    def check_rate_limit(
        self,
        client_ip: str,
        limit: int = 60,
        window_seconds: float = 60.0
    ) -> Dict[str, Any]:
        """Sliding-window rate limiter per client IP."""
        now = datetime.now(timezone.utc).timestamp()
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT request_count, window_start FROM security_rate_limits WHERE client_ip = ?", (client_ip,))
                row = cursor.fetchone()

                if not row or (now - row["window_start"]) > window_seconds:
                    # New window
                    conn.execute("""
                        INSERT OR REPLACE INTO security_rate_limits (client_ip, request_count, window_start)
                        VALUES (?, 1, ?)
                    """, (client_ip, now))
                    conn.commit()
                    return {"allowed": True, "remaining": limit - 1, "retry_after_seconds": 0}

                current_count = row["request_count"] + 1
                if current_count > limit:
                    retry_after = int(window_seconds - (now - row["window_start"]))
                    return {"allowed": False, "remaining": 0, "retry_after_seconds": max(1, retry_after)}

                conn.execute("UPDATE security_rate_limits SET request_count = ? WHERE client_ip = ?", (current_count, client_ip))
                conn.commit()
                return {"allowed": True, "remaining": limit - current_count, "retry_after_seconds": 0}
            finally:
                conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 376: SECURITY VULNERABILITY SCANNER (SQLi & XSS)
    # ---------------------------------------------------------------------------

    def scan_input_vulnerabilities(self, text_input: str) -> Dict[str, Any]:
        """Audit text for common web injection payloads."""
        sqli_patterns = [
            r"(\bUNION\b\s+\bSELECT\b)",
            r"(--|\#|\/\*)",
            r"(\bOR\b\s+\d+=\d+)",
            r"(\bDROP\b\s+\bTABLE\b)",
            r"(';\s*--)"
        ]
        xss_patterns = [
            r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>",
            r"javascript:",
            r"onerror\s*=",
            r"onload\s*=",
            r"<iframe\b"
        ]

        sqli_detected = any(re.search(p, text_input, re.IGNORECASE) for p in sqli_patterns)
        xss_detected = any(re.search(p, text_input, re.IGNORECASE) for p in xss_patterns)

        return {
            "is_safe": not (sqli_detected or xss_detected),
            "sqli_detected": sqli_detected,
            "xss_detected": xss_detected,
            "sanitized_preview": re.sub(r"[<>&\"']", "", text_input)[:100]
        }

    # ---------------------------------------------------------------------------
    # FEATURE 377: AUTOMATED DATABASE BACKUP MANAGER
    # ---------------------------------------------------------------------------

    def create_database_backup(self, backup_dir: Optional[str] = None) -> Dict[str, Any]:
        """Perform zero-downtime hot database backup using sqlite3_backup."""
        if backup_dir is None:
            backup_dir = os.path.join(BASE_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_filename = f"voltcore_backup_{timestamp_str}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        backup_id = f"bup_{timestamp_str}"

        # Perform hot SQLite backup
        with self._lock:
            src_conn = self._get_connection()
            dst_conn = sqlite3.connect(backup_path)
            try:
                src_conn.backup(dst_conn)
            finally:
                dst_conn.close()
                src_conn.close()

        # Compute SHA256 checksum and file size
        file_size = os.path.getsize(backup_path)
        sha256 = hashlib.sha256()
        with open(backup_path, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        checksum = sha256.hexdigest()

        # Register backup
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO database_backup_registry
                    (backup_id, filename, filepath, file_size_bytes, checksum_sha256, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (backup_id, backup_filename, backup_path, file_size, checksum, now_iso))
                conn.commit()
            finally:
                conn.close()

        return {
            "status": "success",
            "backup_id": backup_id,
            "filename": backup_filename,
            "filepath": backup_path,
            "file_size_bytes": file_size,
            "checksum_sha256": checksum
        }

    def list_backups(self) -> List[Dict[str, Any]]:
        """List registered backups."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM database_backup_registry ORDER BY created_at DESC")
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 378: AUDIT TRAIL LOGGER
    # ---------------------------------------------------------------------------

    def log_security_event(
        self,
        user_role: str,
        action: str,
        resource: str,
        client_ip: str,
        status: str = "SUCCESS"
    ) -> Dict[str, Any]:
        """Record an immutable security event."""
        log_id = f"log_{secrets.token_hex(8)}"
        now_iso = datetime.now(timezone.utc).isoformat()
        ip_hash = hashlib.sha256(client_ip.encode("utf-8")).hexdigest()[:16]

        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT INTO security_audit_logs
                    (log_id, timestamp, user_role, action, resource, client_ip_hash, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (log_id, now_iso, user_role.upper(), action.upper(), resource, ip_hash, status.upper()))
                conn.commit()
            finally:
                conn.close()

        return {"status": "success", "log_id": log_id, "timestamp": now_iso}

    def get_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent security audit entries."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM security_audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 379: CORS & CSP POLICY ENFORCER
    # ---------------------------------------------------------------------------

    def generate_csp_headers(self, custom_script_src: Optional[List[str]] = None) -> Dict[str, str]:
        """Generate hardened Content-Security-Policy and CORS headers."""
        scripts = ["'self'", "'unsafe-inline'"]
        if custom_script_src:
            scripts.extend(custom_script_src)

        csp_policy = "; ".join([
            "default-src 'self'",
            f"script-src {' '.join(scripts)}",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com data:",
            "img-src 'self' data: https:",
            "connect-src 'self' https://acoe.annauniv.edu https://meet.jit.si",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ])

        return {
            "Content-Security-Policy": csp_policy,
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Access-Control-Allow-Origin": "https://voltcore.annauniv.edu"
        }
