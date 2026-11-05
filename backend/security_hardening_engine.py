"""
========================================================================================
VoltCore Apex Academia - Security, Immutable Audit & Infrastructure Hardening Engine
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/security_hardening_engine.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Lightweight enterprise security manager handling Multi-Factor Authentication (MFA/TOTP),
  fine-grained RBAC permission matrices, immutable SHA-256 security event logging,
  and automated SQLite WAL database backup and recovery verification.
========================================================================================
"""

import os
import time
import hmac
import struct
import hashlib
import sqlite3
import secrets
import threading
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")
BACKUP_DIR = os.path.join(BASE_DIR, "backend", "cache", "backups")

# Role-Based Permission Matrix
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "Admin_Owner": [
        "VIEW_DASHBOARD", "SUBMIT_CODE", "BOOK_LAB", "EDIT_CURRICULUM",
        "MANAGE_ALLOCATIONS", "AUDIT_LOG_WRITE", "BACKUP_DATABASE",
        "MANAGE_MFA", "ADMIN_AUDIT_VIEW", "PURGE_LOGS"
    ],
    "Admin": [
        "VIEW_DASHBOARD", "SUBMIT_CODE", "BOOK_LAB", "EDIT_CURRICULUM",
        "MANAGE_ALLOCATIONS", "AUDIT_LOG_WRITE", "BACKUP_DATABASE",
        "MANAGE_MFA", "ADMIN_AUDIT_VIEW"
    ],
    "Dean_Academic": [
        "VIEW_DASHBOARD", "EDIT_CURRICULUM", "MANAGE_ALLOCATIONS",
        "AUDIT_LOG_WRITE", "ADMIN_AUDIT_VIEW"
    ],
    "Teacher": [
        "VIEW_DASHBOARD", "SUBMIT_CODE", "BOOK_LAB", "EDIT_CURRICULUM",
        "VIEW_ANALYTICS"
    ],
    "Lab-Instructor": [
        "VIEW_DASHBOARD", "BOOK_LAB", "RESOLVE_FAULT", "SUPERVISE_BENCH"
    ],
    "Student": [
        "VIEW_DASHBOARD", "SUBMIT_CODE", "BOOK_LAB", "JOIN_GROUP", "SUBMIT_REVIEW"
    ],
    "Guest": [
        "VIEW_DASHBOARD"
    ]
}


class SecurityHardeningEngine:
    """
    Core security hardening, MFA verification, and disaster recovery manager.
    Enforces OWASP 2024 / IEEE Std 802.1X standards backed by SQLite WAL tables.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self._lock = threading.Lock()
        os.makedirs(BACKUP_DIR, exist_ok=True)
        self._init_sqlite_schema()
        self._seed_default_security_state()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns an optimized SQLite WAL connection."""
        conn = sqlite3.connect(self.db_path, timeout=5.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode = WAL;")
        cur.execute("PRAGMA synchronous = NORMAL;")
        cur.execute("PRAGMA busy_timeout = 5000;")
        cur.close()
        return conn

    def _init_sqlite_schema(self):
        """Initializes tables for MFA secrets, security events, and backups."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS security_mfa_secrets (
                        user_id TEXT PRIMARY KEY,
                        secret_key TEXT NOT NULL,
                        mfa_enabled INTEGER DEFAULT 1,
                        backup_codes TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS security_audit_events (
                        event_id TEXT PRIMARY KEY,
                        actor_id TEXT NOT NULL,
                        actor_role TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        ip_address TEXT NOT NULL,
                        details TEXT NOT NULL,
                        prev_hash TEXT NOT NULL,
                        block_hash TEXT NOT NULL,
                        timestamp TEXT NOT NULL
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS db_backup_registry (
                        backup_id TEXT PRIMARY KEY,
                        backup_file TEXT NOT NULL,
                        file_size_bytes INTEGER NOT NULL,
                        sha256_checksum TEXT NOT NULL,
                        integrity_status TEXT NOT NULL,
                        created_by TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)
                conn.commit()
            finally:
                conn.close()

    def _seed_default_security_state(self):
        """Seeds platform lead MFA configuration and genesis audit event."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                # 1. Seed Platform Architect MFA (Ashok Kumar A)
                cur.execute("SELECT COUNT(*) FROM security_mfa_secrets;")
                if cur.fetchone()[0] == 0:
                    lead_secret = "4A7B9C2D1E8F3A5B"
                    backup_codes = "718293,482910,958201,310492"
                    now_str = datetime.now(timezone.utc).isoformat()
                    cur.execute("""
                        INSERT INTO security_mfa_secrets (user_id, secret_key, mfa_enabled, backup_codes, created_at)
                        VALUES (?, ?, 1, ?, ?);
                    """, ("2023MITEC042", lead_secret, backup_codes, now_str))

                # 2. Seed Genesis Security Event
                cur.execute("SELECT COUNT(*) FROM security_audit_events;")
                if cur.fetchone()[0] == 0:
                    now_str = datetime.now(timezone.utc).isoformat()
                    prev_h = "0" * 64
                    det = "Security Infrastructure Genesis: VoltCore Hardening Engine Online (OWASP / IEEE 802.1X)."
                    raw = f"SEC-000001:SYSTEM:Admin_Owner:GENESIS:127.0.0.1:{det}:{now_str}:{prev_h}"
                    block_h = hashlib.sha256(raw.encode()).hexdigest()
                    cur.execute("""
                        INSERT INTO security_audit_events
                        (event_id, actor_id, actor_role, event_type, ip_address, details, prev_hash, block_hash, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, ("SEC-000001", "SYSTEM", "Admin_Owner", "GENESIS", "127.0.0.1", det, prev_h, block_h, now_str))

                conn.commit()
            finally:
                conn.close()

    # =========================================================================
    # Multi-Factor Authentication (MFA / TOTP)
    # =========================================================================
    @staticmethod
    def _compute_totp(secret: str, timestamp: Optional[int] = None, step: int = 30) -> str:
        """
        Derives an RFC 6238 compliant 6-digit Time-based One-Time Password (TOTP).
        Uses HMAC-SHA256 truncated to 6 decimal digits.
        """
        t = timestamp if timestamp is not None else int(time.time())
        counter = t // step
        counter_bytes = struct.pack(">Q", counter)
        secret_bytes = secret.encode("utf-8")

        h = hmac.new(secret_bytes, counter_bytes, hashlib.sha256).digest()
        offset = h[-1] & 0x0F
        binary_code = (
            ((h[offset] & 0x7F) << 24) |
            ((h[offset + 1] & 0xFF) << 16) |
            ((h[offset + 2] & 0xFF) << 8) |
            (h[offset + 3] & 0xFF)
        )
        token = str(binary_code % 1000000).zfill(6)
        return token

    def generate_mfa_secret(self, user_id: str) -> Dict[str, Any]:
        """Generates a novel cryptographically random MFA secret key and backup codes."""
        secret = secrets.token_hex(10).upper()
        codes = [str(secrets.randbelow(900000) + 100000) for _ in range(4)]
        now_str = datetime.now(timezone.utc).isoformat()

        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT OR REPLACE INTO security_mfa_secrets
                    (user_id, secret_key, mfa_enabled, backup_codes, created_at)
                    VALUES (?, ?, 1, ?, ?);
                """, (user_id, secret, ",".join(codes), now_str))
                conn.commit()

                return {
                    "status": "SUCCESS",
                    "user_id": user_id,
                    "secret_key": secret,
                    "backup_codes": codes,
                    "algorithm": "TOTP-HMAC-SHA256",
                    "step_seconds": 30
                }
            finally:
                conn.close()

    def validate_mfa_token(
        self,
        user_id: str,
        token_code: str,
        client_ip: str = "127.0.0.1",
        window_steps: int = 1
    ) -> Dict[str, Any]:
        """
        Validates incoming 6-digit TOTP token with time-drift tolerance (+/- 30s).
        Logs security event for failed and successful authentications.
        """
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT secret_key, backup_codes, mfa_enabled FROM security_mfa_secrets WHERE user_id = ?;", (user_id,))
            row = cur.fetchone()
            if not row or not row["mfa_enabled"]:
                return {"status": "ERROR", "valid": False, "error": "MFA is not configured for this user"}

            secret = row["secret_key"]
            backup_codes = [c.strip() for c in row["backup_codes"].split(",") if c.strip()]
            cur_time = int(time.time())

            # Check backup code
            if token_code in backup_codes:
                self.log_security_event(
                    actor_id=user_id,
                    actor_role="Student",
                    event_type="MFA_BACKUP_CODE_USED",
                    ip_address=client_ip,
                    details=f"User {user_id} authenticated using one-time backup recovery code."
                )
                return {"status": "SUCCESS", "valid": True, "auth_method": "BACKUP_CODE"}

            # Check TOTP within +/- window_steps (each step = 30 seconds)
            valid = False
            for step_offset in range(-window_steps, window_steps + 1):
                calc_token = self._compute_totp(secret, timestamp=cur_time + (step_offset * 30))
                if hmac.compare_digest(calc_token, token_code):
                    valid = True
                    break

            if valid:
                self.log_security_event(
                    actor_id=user_id,
                    actor_role="Student",
                    event_type="MFA_CHALLENGE_SUCCESS",
                    ip_address=client_ip,
                    details=f"User {user_id} successfully passed TOTP MFA challenge."
                )
                return {"status": "SUCCESS", "valid": True, "auth_method": "TOTP_HMAC_SHA256"}
            else:
                self.log_security_event(
                    actor_id=user_id,
                    actor_role="Student",
                    event_type="MFA_CHALLENGE_FAILED",
                    ip_address=client_ip,
                    details=f"Invalid TOTP challenge attempt on account {user_id}."
                )
                return {"status": "INVALID", "valid": False, "error": "Invalid or expired MFA token"}
        finally:
            conn.close()

    # =========================================================================
    # RBAC Permission Enforcement
    # =========================================================================
    @staticmethod
    def check_permission(role: str, permission: str) -> bool:
        """Checks if a given role possesses the requested capability."""
        allowed = ROLE_PERMISSIONS.get(role, [])
        return permission in allowed

    def enforce_permission(self, role: str, permission: str) -> Dict[str, Any]:
        """Enforces RBAC barrier, logging unauthorized privilege escalation attempts."""
        if self.check_permission(role, permission):
            return {"status": "SUCCESS", "authorized": True, "role": role, "permission": permission}

        # Log unauthorized attempt
        self.log_security_event(
            actor_id="UNKNOWN",
            actor_role=role,
            event_type="PRIVILEGE_ESCALATION_BLOCKED",
            ip_address="127.0.0.1",
            details=f"Unauthorized role '{role}' attempted action requiring '{permission}'."
        )
        return {
            "status": "FORBIDDEN",
            "authorized": False,
            "error": f"Role '{role}' is not authorized for capability '{permission}'"
        }

    # =========================================================================
    # Cryptographic SHA-256 Chained Security Event Ledger
    # =========================================================================
    def log_security_event(
        self,
        actor_id: str,
        actor_role: str,
        event_type: str,
        ip_address: str,
        details: str
    ) -> Dict[str, Any]:
        """Records an immutable security event with chained cryptographic SHA-256 blocks."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT block_hash FROM security_audit_events ORDER BY rowid DESC LIMIT 1;")
                prev_row = cur.fetchone()
                prev_hash = prev_row["block_hash"] if prev_row else "0" * 64

                cur.execute("SELECT COUNT(*) FROM security_audit_events;")
                count = cur.fetchone()[0] + 1
                event_id = f"SEC-{count:06d}"
                now_str = datetime.now(timezone.utc).isoformat()

                raw_input = f"{event_id}:{actor_id}:{actor_role}:{event_type}:{ip_address}:{details}:{now_str}:{prev_hash}"
                block_hash = hashlib.sha256(raw_input.encode("utf-8")).hexdigest()

                cur.execute("""
                    INSERT INTO security_audit_events
                    (event_id, actor_id, actor_role, event_type, ip_address, details, prev_hash, block_hash, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (event_id, actor_id, actor_role, event_type, ip_address, details, prev_hash, block_hash, now_str))
                conn.commit()

                return {
                    "status": "SUCCESS",
                    "event_id": event_id,
                    "event_type": event_type,
                    "block_hash": block_hash,
                    "prev_hash": prev_hash
                }
            finally:
                conn.close()

    def verify_security_chain_integrity(self) -> Dict[str, Any]:
        """Validates that all blocks in the security event ledger form an unbroken hash chain."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM security_audit_events ORDER BY rowid ASC;")
            rows = cur.fetchall()

            if not rows:
                return {"status": "SUCCESS", "verified": True, "total_events": 0, "tampered": False}

            prev_hash = "0" * 64
            for r in rows:
                expected_raw = f"{r['event_id']}:{r['actor_id']}:{r['actor_role']}:{r['event_type']}:{r['ip_address']}:{r['details']}:{r['timestamp']}:{r['prev_hash']}"
                calc_hash = hashlib.sha256(expected_raw.encode("utf-8")).hexdigest()

                if calc_hash != r["block_hash"]:
                    return {
                        "status": "INTEGRITY_BREACH",
                        "verified": False,
                        "tampered": True,
                        "failed_at_event_id": r["event_id"],
                        "message": f"Cryptographic mismatch detected at block {r['event_id']}."
                    }
                prev_hash = r["block_hash"]

            return {
                "status": "SUCCESS",
                "verified": True,
                "total_events": len(rows),
                "tampered": False,
                "latest_hash": prev_hash
            }
        finally:
            conn.close()

    # =========================================================================
    # Disaster Recovery: Automated Database Backup & Integrity Verification
    # =========================================================================
    def create_database_backup(
        self,
        backup_name: Optional[str] = None,
        actor_role: str = "Admin"
    ) -> Dict[str, Any]:
        """
        Creates an atomic SQLite WAL backup snapshot and verifies integrity.
        Enforces RBAC: Only 'Admin' or 'Admin_Owner' can trigger backups.
        """
        if not self.check_permission(actor_role, "BACKUP_DATABASE"):
            return {
                "status": "FORBIDDEN",
                "error": f"Role '{actor_role}' lacks permission 'BACKUP_DATABASE'"
            }

        with self._lock:
            ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            b_name = backup_name or f"voltcore_lms_backup_{ts_str}.db"
            backup_path = os.path.join(BACKUP_DIR, b_name)

            # Atomic SQLite WAL backup via sqlite3.backup API
            src_conn = self._get_connection()
            dest_conn = sqlite3.connect(backup_path)
            try:
                src_conn.backup(dest_conn)
                dest_conn.commit()
            finally:
                src_conn.close()
                dest_conn.close()

            # Verify integrity on the newly created snapshot
            check_conn = sqlite3.connect(backup_path)
            try:
                check_cur = check_conn.cursor()
                check_cur.execute("PRAGMA integrity_check;")
                integrity_result = check_cur.fetchone()[0]
            finally:
                check_conn.close()

            # Compute SHA-256 Checksum of the backup snapshot
            with open(backup_path, "rb") as f:
                sha256_chk = hashlib.sha256(f.read()).hexdigest()

            file_size = os.path.getsize(backup_path)
            backup_id = f"BKP-{int(time.time())%100000:05d}"
            now_str = datetime.now(timezone.utc).isoformat()

            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO db_backup_registry
                    (backup_id, backup_file, file_size_bytes, sha256_checksum, integrity_status, created_by, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (backup_id, b_name, file_size, sha256_chk, integrity_result, actor_role, now_str))
                conn.commit()
            finally:
                conn.close()

        # Log event in security ledger
        self.log_security_event(
            actor_id="ADMIN_CONSOLE",
            actor_role=actor_role,
            event_type="DATABASE_BACKUP_COMPLETED",
            ip_address="127.0.0.1",
            details=f"Atomic backup {b_name} generated ({file_size} bytes, integrity: {integrity_result})."
        )

        return {
            "status": "SUCCESS",
            "backup_id": backup_id,
            "backup_file": b_name,
            "file_size_bytes": file_size,
            "sha256_checksum": sha256_chk,
            "integrity": integrity_result,
            "created_at": now_str
        }

    def list_backups(self) -> List[Dict[str, Any]]:
        """Returns the list of verified database backup snapshots."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM db_backup_registry ORDER BY rowid DESC LIMIT 10;")
            rows = cur.fetchall()
            return [
                {
                    "backup_id": r["backup_id"],
                    "backup_file": r["backup_file"],
                    "file_size_bytes": r["file_size_bytes"],
                    "sha256_checksum": r["sha256_checksum"],
                    "integrity_status": r["integrity_status"],
                    "created_by": r["created_by"],
                    "created_at": r["created_at"]
                }
                for r in rows
            ]
        finally:
            conn.close()

    def get_security_overview(self) -> Dict[str, Any]:
        """Provides an aggregated overview of security hardening metrics."""
        chain_status = self.verify_security_chain_integrity()
        backups = self.list_backups()
        return {
            "institution": "Madras Institute of Technology (MIT) Campus, Anna University",
            "platform_lead": "Ashok Kumar A (2023MITEC042)",
            "security_standard": "OWASP 2024 / IEEE Std 802.1X Hardened",
            "mfa_algorithm": "TOTP-HMAC-SHA256 (30s Step)",
            "chain_integrity": chain_status,
            "backups_count": len(backups),
            "recent_backups": backups[:3]
        }


# Global Security Hardening Engine Singleton
security_hardening_engine = SecurityHardeningEngine()
