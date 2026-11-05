"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 8 Concurrency & Cloud Staging Hardening
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase8_concurrency_staging.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import time
import json
import sqlite3
import unittest
from backend.sqlite_wal_optimizer import (
    SQLiteConnectionPool,
    sqlite_pool,
    execute_wal_checkpoint,
    get_wal_statistics
)
from backend.concurrency_limiter import (
    ConcurrencyLimiter,
    concurrency_limiter,
    transaction_retry,
    bounded_write_operation,
    simulate_concurrent_load
)
from scripts.validate_staging_env import validate_staging_composition


class TestPhase8ConcurrencyStaging(unittest.TestCase):
    """
    Validation suite for Phase 8:
      - Thread-safe SQLite connection pooling
      - Multi-user concurrency without lock contention
      - Rate limiting headers and transaction retries
      - Cloud staging multi-container RAM budget (<= 450MB)
      - Settings page and CloudSyncStatus offline spool
    """

    def setUp(self):
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.limiter = ConcurrencyLimiter(max_concurrent_writes=4, default_rate_limit=120)

    def test_sqlite_connection_pool_acquisition_and_release(self):
        """Connection pool must acquire pre-tuned connections and release them cleanly."""
        pool = SQLiteConnectionPool(max_connections=5)
        with pool.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA journal_mode;")
            journal_mode = str(cur.fetchone()[0]).lower()
            self.assertEqual(journal_mode, "wal")

            cur.execute("PRAGMA busy_timeout;")
            busy_timeout = cur.fetchone()[0]
            self.assertEqual(busy_timeout, 5000)

            cur.execute("SELECT 1;")
            self.assertEqual(cur.fetchone()[0], 1)

        # Confirm pool has active connections ready
        self.assertGreaterEqual(pool._created_count, 1)
        pool.close_all()

    def test_wal_checkpoint_routines(self):
        """WAL checkpoint operations (PASSIVE and FULL) must execute successfully."""
        res_passive = execute_wal_checkpoint(mode="PASSIVE")
        self.assertEqual(res_passive["status"], "SUCCESS")
        self.assertEqual(res_passive["mode"], "PASSIVE")
        self.assertEqual(res_passive["busy"], 0)

        res_full = execute_wal_checkpoint(mode="FULL")
        self.assertEqual(res_full["status"], "SUCCESS")
        self.assertEqual(res_full["mode"], "FULL")

        stats = get_wal_statistics()
        self.assertGreater(stats["db_size_kb"], 0)
        self.assertIn("wal_exists", stats)

    def test_multi_user_concurrent_read_write_safety(self):
        """Simultaneous multi-threaded reads/writes must achieve zero lock contention."""
        result = simulate_concurrent_load(
            sqlite_pool,
            num_threads=10,
            ops_per_thread=5,
            write_ratio=0.2
        )
        self.assertTrue(result["zero_contention_passed"], f"Errors: {result.get('errors')}")
        self.assertEqual(result["failed_operations"], 0)
        self.assertEqual(result["successful_operations"], 50)
        self.assertEqual(result["success_rate_percent"], 100.0)
        self.assertLess(result["avg_latency_ms"], 50.0)

    def test_rate_limiting_headers_generation(self):
        """Rate limiter must generate standard RFC-compliant rate limit HTTP headers."""
        headers = self.limiter.get_rate_limit_headers(client_key="test_student_ip", limit=100)
        self.assertEqual(headers["X-RateLimit-Limit"], "100")
        self.assertEqual(headers["X-RateLimit-Remaining"], "99")
        self.assertIn("w=60", headers["X-RateLimit-Policy"])
        self.assertGreaterEqual(int(headers["X-RateLimit-Reset"]), 1)

        # Sequential calls should decrement remaining tokens
        headers_2 = self.limiter.get_rate_limit_headers(client_key="test_student_ip", limit=100)
        self.assertEqual(headers_2["X-RateLimit-Remaining"], "98")

    def test_transaction_retry_decorator_resilience(self):
        """Retry decorator must succeed if transient lock clears within max retries."""
        attempts = 0

        @transaction_retry(max_retries=3, initial_delay=0.001, backoff_factor=1.5)
        def transient_locked_operation():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise sqlite3.OperationalError("database is locked")
            return "SUCCESS_COMMITTED"

        result = transient_locked_operation()
        self.assertEqual(result, "SUCCESS_COMMITTED")
        self.assertEqual(attempts, 3)

    def test_bounded_write_operation_semaphore(self):
        """Bounded write operation decorator must execute and properly release semaphore."""
        executed = False

        @bounded_write_operation
        def write_action():
            nonlocal executed
            executed = True
            return "WRITE_OK"

        res = write_action()
        self.assertEqual(res, "WRITE_OK")
        self.assertTrue(executed)

    def test_staging_environment_memory_budget(self):
        """Staging container specifications must not exceed 450MB total RAM limit."""
        report = validate_staging_composition()
        self.assertTrue(report["passed"])
        self.assertTrue(report["ram_budget_compliant"])
        self.assertLessEqual(report["core_services_ram_mb"], 450.0)
        self.assertEqual(report["core_services_ram_mb"], 448.0)
        self.assertTrue(report["security_isolation_compliant"])
        self.assertTrue(report["networking_compliant"])

    def test_cloud_sync_status_component_exists(self):
        """CloudSyncStatus.jsx must implement offline spool and retry handlers."""
        path = os.path.join(self.base_dir, "src", "components", "CloudSyncStatus.jsx")
        self.assertTrue(os.path.isfile(path))
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()

        required_keywords = [
            "voltcore_telemetry_spool",
            "flushSpoolQueue",
            "Force Cloud Sync",
            "window.addEventListener('online'",
            "window.addEventListener('offline'",
            "triggerToast"
        ]
        for kw in required_keywords:
            self.assertIn(kw, code, f"Keyword '{kw}' missing from CloudSyncStatus.jsx")

    def test_settings_page_and_static_route_exist(self):
        """settings.astro and generated dist/settings/index.html must exist."""
        src_path = os.path.join(self.base_dir, "src", "pages", "settings.astro")
        dist_path = os.path.join(self.base_dir, "dist", "settings", "index.html")

        self.assertTrue(os.path.isfile(src_path), "src/pages/settings.astro missing")
        self.assertTrue(os.path.isfile(dist_path), "dist/settings/index.html missing from static build")

        with open(src_path, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn("CloudSyncStatus", code)
        self.assertIn("HP Victus", code)
        self.assertIn("Ashok Kumar A", code)

    def test_docker_compose_healthcheck_script_exists(self):
        """deploy/docker_compose_healthcheck.sh must exist and be valid shell script."""
        script_path = os.path.join(self.base_dir, "deploy", "docker_compose_healthcheck.sh")
        self.assertTrue(os.path.isfile(script_path))
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("VOLTCORE APEX ACADEMIA", content)
        self.assertIn("448MB", content)
        self.assertIn("exit 0", content)

    def test_data_privacy_invariants_in_phase8_files(self):
        """Private admin email and phone must never be hardcoded into client code."""
        restricted_patterns = ["ashokkumar2008313@gmail.com", "9597382878"]
        phase8_files = [
            os.path.join(self.base_dir, "src", "components", "CloudSyncStatus.jsx"),
            os.path.join(self.base_dir, "src", "pages", "settings.astro")
        ]

        for p8_path in phase8_files:
            with open(p8_path, "r", encoding="utf-8") as f:
                content = f.read()
                for pat in restricted_patterns:
                    self.assertNotIn(
                        pat,
                        content,
                        f"Restricted admin metadata leaked in {p8_path}"
                    )


if __name__ == "__main__":
    unittest.main()
