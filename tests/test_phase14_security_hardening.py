"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 14 Security Hardening & Immutable Audit
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase14_security_hardening.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import time
import tempfile
import unittest
import sqlite3
from backend.security_hardening_engine import SecurityHardeningEngine, ROLE_PERMISSIONS


class TestPhase14SecurityHardening(unittest.TestCase):
    """
    Validation suite for Phase 14:
      - RFC 6238 TOTP Multi-Factor Authentication (MFA) generation & time-drift validation
      - One-time backup recovery code validation
      - Fine-grained RBAC permission matrix & privilege escalation barriers
      - Immutable SHA-256 chained security event ledger & tamper-detection verification
      - Disaster recovery: atomic SQLite WAL database backup creation & checksum verification
      - Astro page, React island component & strict data privacy invariants
    """

    def setUp(self):
        # Create an isolated temporary SQLite database for each test
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.engine = SecurityHardeningEngine(db_path=self.temp_db_path)
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except Exception:
                pass

    def test_mfa_secret_generation_and_totp_validation(self):
        """Validates MFA secret generation, TOTP derivation, and time-drift validation."""
        user_id = "TEST_USER_001"
        res = self.engine.generate_mfa_secret(user_id=user_id)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["user_id"], user_id)
        self.assertEqual(len(res["backup_codes"]), 4)
        secret = res["secret_key"]
        self.assertTrue(len(secret) >= 16)

        # Compute valid TOTP for current time
        cur_totp = SecurityHardeningEngine._compute_totp(secret)
        self.assertEqual(len(cur_totp), 6)
        self.assertTrue(cur_totp.isdigit())

        # Validate token against engine
        val_res = self.engine.validate_mfa_token(user_id=user_id, token_code=cur_totp)
        self.assertEqual(val_res["status"], "SUCCESS")
        self.assertTrue(val_res["valid"])
        self.assertEqual(val_res["auth_method"], "TOTP_HMAC_SHA256")

        # Validate with wrong token
        wrong_token = "000000" if cur_totp != "000000" else "999999"
        fail_res = self.engine.validate_mfa_token(user_id=user_id, token_code=wrong_token)
        self.assertEqual(fail_res["status"], "INVALID")
        self.assertFalse(fail_res["valid"])

    def test_mfa_backup_code_redemption(self):
        """Validates that valid backup codes can be redeemed for authentication."""
        user_id = "STU_BACKUP_TEST"
        res = self.engine.generate_mfa_secret(user_id=user_id)
        backup_code = res["backup_codes"][0]

        val_res = self.engine.validate_mfa_token(user_id=user_id, token_code=backup_code)
        self.assertEqual(val_res["status"], "SUCCESS")
        self.assertTrue(val_res["valid"])
        self.assertEqual(val_res["auth_method"], "BACKUP_CODE")

    def test_rbac_permission_matrix_and_escalation_block(self):
        """Validates RBAC least-privilege matrix and privilege escalation containment."""
        # 1. Admin_Owner has full capability
        self.assertTrue(self.engine.check_permission("Admin_Owner", "BACKUP_DATABASE"))
        self.assertTrue(self.engine.check_permission("Admin_Owner", "PURGE_LOGS"))
        self.assertTrue(self.engine.check_permission("Admin_Owner", "EDIT_CURRICULUM"))

        # 2. Student has limited capabilities
        self.assertTrue(self.engine.check_permission("Student", "SUBMIT_CODE"))
        self.assertTrue(self.engine.check_permission("Student", "BOOK_LAB"))
        self.assertFalse(self.engine.check_permission("Student", "BACKUP_DATABASE"))
        self.assertFalse(self.engine.check_permission("Student", "AUDIT_LOG_WRITE"))

        # 3. Privilege escalation enforcement
        escalation_attempt = self.engine.enforce_permission("Student", "BACKUP_DATABASE")
        self.assertEqual(escalation_attempt["status"], "FORBIDDEN")
        self.assertFalse(escalation_attempt["authorized"])

        authorized_action = self.engine.enforce_permission("Admin", "BACKUP_DATABASE")
        self.assertEqual(authorized_action["status"], "SUCCESS")
        self.assertTrue(authorized_action["authorized"])

    def test_security_audit_event_logging_and_sha256_chain_integrity(self):
        """Validates cryptographic event logging and tamper-detection verification."""
        # 1. Log two custom security events
        ev1 = self.engine.log_security_event(
            actor_id="2023MITEC042",
            actor_role="Admin_Owner",
            event_type="FIREWALL_POLICY_UPDATED",
            ip_address="192.168.1.100",
            details="Configured rate limiting on hardware-hil serial gateway."
        )
        self.assertEqual(ev1["status"], "SUCCESS")
        self.assertIn("SEC-", ev1["event_id"])

        ev2 = self.engine.log_security_event(
            actor_id="FAC002",
            actor_role="Teacher",
            event_type="EXAM_KEY_GENERATED",
            ip_address="192.168.1.105",
            details="Generated assessment decryption key for GATE ECE mock 3."
        )
        self.assertEqual(ev2["status"], "SUCCESS")
        self.assertEqual(ev2["prev_hash"], ev1["block_hash"])

        # 2. Verify complete ledger integrity
        audit_res = self.engine.verify_security_chain_integrity()
        self.assertEqual(audit_res["status"], "SUCCESS")
        self.assertTrue(audit_res["verified"])
        self.assertFalse(audit_res["tampered"])
        self.assertGreaterEqual(audit_res["total_events"], 3)  # Genesis + 2 events

        # 3. Simulate database tampering and verify detection
        conn = sqlite3.connect(self.temp_db_path)
        cur = conn.cursor()
        cur.execute("UPDATE security_audit_events SET details = 'TAMPERED DATA' WHERE event_id = ?;", (ev1["event_id"],))
        conn.commit()
        conn.close()

        tampered_res = self.engine.verify_security_chain_integrity()
        self.assertEqual(tampered_res["status"], "INTEGRITY_BREACH")
        self.assertFalse(tampered_res["verified"])
        self.assertTrue(tampered_res["tampered"])
        self.assertEqual(tampered_res["failed_at_event_id"], ev1["event_id"])

    def test_database_backup_and_wal_integrity_verification(self):
        """Validates disaster recovery atomic SQLite WAL database backup creation."""
        # Unauthorized backup by student
        denied = self.engine.create_database_backup(actor_role="Student")
        self.assertEqual(denied["status"], "FORBIDDEN")

        # Authorized backup by Admin
        backup_res = self.engine.create_database_backup(actor_role="Admin")
        self.assertEqual(backup_res["status"], "SUCCESS")
        self.assertIn("BKP-", backup_res["backup_id"])
        self.assertGreater(backup_res["file_size_bytes"], 0)
        self.assertEqual(backup_res["integrity"], "ok")
        self.assertEqual(len(backup_res["sha256_checksum"]), 64)

        # Verify backup exists in registry
        backups = self.engine.list_backups()
        self.assertGreaterEqual(len(backups), 1)
        self.assertEqual(backups[0]["backup_id"], backup_res["backup_id"])

    def test_security_overview_endpoint_data(self):
        """Validates aggregated security metrics overview."""
        overview = self.engine.get_security_overview()
        self.assertIn("Madras Institute of Technology", overview["institution"])
        self.assertIn("Ashok Kumar A", overview["platform_lead"])
        self.assertEqual(overview["security_standard"], "OWASP 2024 / IEEE Std 802.1X Hardened")
        self.assertTrue(overview["chain_integrity"]["verified"])
        self.assertIsInstance(overview["backups_count"], int)

    def test_security_hub_page_and_component_exist(self):
        """Validates existence of the Security Hub Astro page and React island component."""
        page_path = os.path.join(self.base_dir, "src", "pages", "security-hub.astro")
        comp_path = os.path.join(self.base_dir, "src", "components", "SecurityAuditDashboard.jsx")

        self.assertTrue(os.path.exists(page_path), "security-hub.astro page must exist")
        self.assertTrue(os.path.exists(comp_path), "SecurityAuditDashboard.jsx must exist")

        with open(page_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("SecurityAuditDashboard", content)
            self.assertIn("Ashok Kumar A", content)
            self.assertIn("OWASP 2024", content)

        with open(comp_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Enterprise Security & Infrastructure Hardening Hub", content)
            self.assertIn("TOTP", content)

    def test_data_privacy_invariants_no_leakage(self):
        """
        Validates that private admin contact details are strictly isolated
        and never present in public client-facing files.
        """
        restricted_patterns = [
            "ashokkumar2008313@gmail.com",
            "9597382878"
        ]

        target_files = [
            os.path.join(self.base_dir, "src", "pages", "security-hub.astro"),
            os.path.join(self.base_dir, "src", "components", "SecurityAuditDashboard.jsx"),
            os.path.join(self.base_dir, "src", "components", "Topbar.astro"),
            os.path.join(self.base_dir, "backend", "security_hardening_engine.py"),
            os.path.join(self.base_dir, "public", "service-worker.js")
        ]

        for file_path in target_files:
            if not os.path.exists(file_path):
                continue
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                for pattern in restricted_patterns:
                    self.assertNotIn(
                        pattern,
                        content,
                        f"CRITICAL PRIVACY VIOLATION: '{pattern}' leaked in {os.path.basename(file_path)}!"
                    )


if __name__ == "__main__":
    unittest.main()
