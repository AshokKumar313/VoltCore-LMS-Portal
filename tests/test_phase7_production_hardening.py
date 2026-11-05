"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 7 Production Hardening & Latency Profiling
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase7_production_hardening.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import time
import json
import unittest
from backend.performance_profiler import SystemPerformanceProfiler, performance_profiler
from deploy.production_readiness_audit import ProductionReadinessAuditor, EXPECTED_STATIC_ROUTES


class TestPhase7ProductionHardening(unittest.TestCase):
    """
    Rapid, low-overhead test suite verifying:
      1. Hardware safety & cool thermal bounds on HP Victus environment
      2. Process memory footprint compliance (< 300MB target, < 500MB hard limit)
      3. Sub-50ms database and API latency benchmarks
      4. Complete 16 static routes production readiness
      5. Strict zero-leakage data privacy invariants
    """

    def setUp(self):
        self.profiler = SystemPerformanceProfiler()
        self.auditor = ProductionReadinessAuditor()
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def test_thermal_and_cpu_readiness(self):
        """CPU execution benchmark must run under 25ms, confirming unthrottled cool status."""
        report = self.profiler.audit_thermal_and_cpu()
        self.assertTrue(report["ready"])
        self.assertIn(report["status"], ["OPTIMAL_COOL", "SAFE_NORMAL"])
        self.assertLess(report["benchmark_eval_ms"], 25.0)
        self.assertGreaterEqual(report["core_count"], 2)
        self.assertIn("HP Victus", report["hardware_target"])

    def test_ram_footprint_within_mandate(self):
        """Process memory footprint must stay strictly below 500MB (target < 300MB)."""
        report = self.profiler.audit_ram_footprint()
        self.assertTrue(report["compliant"])
        self.assertIn(report["status"], ["PASS_LIGHTWEIGHT", "PASS_MODERATE"])
        self.assertLessEqual(report["process_ram_mb"], 500.0)
        self.assertGreater(report["memory_headroom_mb"], 0.0)

    def test_sqlite_wal_integrity(self):
        """Database must be in Write-Ahead Logging (WAL) mode with intact pages."""
        report = self.profiler.audit_sqlite_wal_integrity()
        self.assertTrue(report["valid"])
        self.assertEqual(report["journal_mode"], "wal")
        self.assertTrue(report["is_wal"])
        self.assertEqual(report["integrity_check"], "ok")
        self.assertEqual(report["quick_check"], "ok")
        self.assertIn("users", report["tables"])
        self.assertIn("attendance", report["tables"])

    def test_query_latencies_under_50ms(self):
        """All indexed SQLite queries and RAG searches must execute in < 50ms."""
        report = self.profiler.benchmark_query_latencies(iterations=10)
        self.assertTrue(report["all_latencies_under_50ms"])

        user_bench = report["benchmarks"].get("sqlite_user_lookup", {})
        self.assertTrue(user_bench.get("passed", False))
        self.assertLess(user_bench.get("avg_ms", 999.0), 50.0)

        att_bench = report["benchmarks"].get("sqlite_attendance_agg", {})
        self.assertTrue(att_bench.get("passed", False))
        self.assertLess(att_bench.get("avg_ms", 999.0), 50.0)

        rag_bench = report["benchmarks"].get("bm25_rag_query", {})
        self.assertTrue(rag_bench.get("passed", False))
        self.assertLess(rag_bench.get("avg_ms", 999.0), 50.0)

    def test_full_system_profile_health(self):
        """Full system diagnostic must return healthy state and execute in < 600ms."""
        profile = self.profiler.collect_full_profile()
        self.assertEqual(profile["status"], "SUCCESS")
        self.assertTrue(profile["healthy"])
        self.assertIn(profile["overall_health"], ["GRADE_A_OPTIMAL", "GRADE_B_HEALTHY"])
        self.assertLess(profile["profiling_duration_ms"], 600.0)
        self.assertEqual(profile["platform_metadata"]["lead"], "Ashok Kumar A (2023MITEC042)")

    def test_production_readiness_static_routes(self):
        """All enterprise production static routes must exist in dist/."""
        report = self.auditor.audit_static_routes()
        self.assertTrue(report["passed"], f"Missing routes: {report.get('missing_routes')}")
        self.assertEqual(report["verified_count"], len(EXPECTED_STATIC_ROUTES))
        self.assertEqual(len(report["missing_routes"]), 0)

    def test_production_readiness_privacy_invariants(self):
        """Private admin email and phone must never appear in client bundles."""
        report = self.auditor.audit_privacy_and_rbac_invariants()
        self.assertTrue(report["passed"], f"Leaks found: {report.get('leaks')}")
        self.assertEqual(report["leaks_found"], 0)
        self.assertGreater(report["scanned_files_count"], 50)

    def test_production_readiness_public_metadata(self):
        """Public email and GitHub repository must be present."""
        report = self.auditor.audit_public_metadata_presence()
        self.assertTrue(report["passed"])
        self.assertTrue(report["found_github"])
        self.assertTrue(report["found_lead"])

    def test_production_readiness_pwa_service_worker(self):
        """PWA Service Worker and manifest must be valid."""
        report = self.auditor.audit_pwa_service_worker()
        self.assertTrue(report["passed"])
        self.assertTrue(report["service_worker_present"])
        self.assertTrue(report["manifest_json_present"])
        self.assertTrue(report["critical_routes_precached"])

    def test_production_readiness_full_audit(self):
        """Comprehensive audit must return production_ready = True."""
        report = self.auditor.run_full_audit()
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["production_ready"])

    def test_api_endpoints_sub_50ms_latency(self):
        """Direct API service handlers must compute responses with < 50ms latency."""
        import lms_database
        from backend.security_auth import get_admin_audit_metadata

        # 1. Admin Audit Metadata
        t0 = time.perf_counter()
        meta = get_admin_audit_metadata(role="Student")
        lat_meta = (time.perf_counter() - t0) * 1000.0
        self.assertLess(lat_meta, 50.0)
        self.assertIn("platform_lead", meta)

        # 2. Database Student Lookup
        t0 = time.perf_counter()
        student = lms_database.get_user_by_id("2023MITEC042")
        lat_student = (time.perf_counter() - t0) * 1000.0
        self.assertLess(lat_student, 50.0)
        self.assertIsNotNone(student)

        # 3. Attendance Analytics
        t0 = time.perf_counter()
        att = lms_database.get_attendance_history(limit=10)
        lat_att = (time.perf_counter() - t0) * 1000.0
        self.assertLess(lat_att, 50.0)

        # 4. System Metrics Profile
        t0 = time.perf_counter()
        prof = performance_profiler.collect_full_profile()
        lat_prof = (time.perf_counter() - t0) * 1000.0
        self.assertLess(lat_prof, 600.0)
        self.assertTrue(prof["healthy"])

    def test_api_admin_audit_metadata_rbac_safety(self):
        """Ensure unprivileged roles receive redacted contact info, while Owner receives full info."""
        from backend.security_auth import get_admin_audit_metadata

        # 1. Unprivileged Student query
        student_data = get_admin_audit_metadata(role="Student")
        self.assertIn("REDACTED", student_data.get("admin_email", ""))
        self.assertIn("REDACTED", student_data.get("admin_phone", ""))
        self.assertEqual(student_data.get("rbac_access_level"), "PUBLIC_UNPRIVILEGED")

        # 2. Privileged Owner / Admin query
        owner_data = get_admin_audit_metadata(role="Admin")
        self.assertEqual(owner_data.get("rbac_access_level"), "PRIVILEGED_ADMIN_ACCESS")
        self.assertNotIn("REDACTED", owner_data.get("admin_email", ""))
        self.assertNotIn("REDACTED", owner_data.get("admin_phone", ""))

    def test_system_status_widget_exists(self):
        """SystemStatusWidget.jsx must exist and have zero-polling design."""
        widget_path = os.path.join(self.base_dir, "src", "components", "SystemStatusWidget.jsx")
        self.assertTrue(os.path.isfile(widget_path))
        with open(widget_path, "r", encoding="utf-8") as f:
            code = f.read()

        self.assertIn("Zero-polling design", code)
        self.assertIn("caches.keys()", code)
        self.assertIn("runDiagnostics", code)
        self.assertIn("HP Victus", code)

    def test_profile_astro_optimized(self):
        """profile.astro must import and render SystemStatusWidget."""
        profile_path = os.path.join(self.base_dir, "src", "pages", "profile.astro")
        with open(profile_path, "r", encoding="utf-8") as f:
            code = f.read()

        self.assertIn("SystemStatusWidget", code)
        self.assertIn("client:idle", code)


if __name__ == "__main__":
    unittest.main()
