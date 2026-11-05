"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 16 Cloud Staging & Deployment Optimizer
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase16_cloud_deploy.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import unittest
from deploy.cloud_deployment_optimizer import (
    CloudDeploymentOptimizer,
    PUBLIC_ADMIN_EMAIL,
    PUBLIC_GITHUB,
    RESTRICTED_METADATA_PATTERNS
)


class TestPhase16CloudDeploy(unittest.TestCase):
    """
    Validation suite for Phase 16:
      - Environment variable schema validation & secret parameterization
      - Strict secret isolation (RBAC) across client files
      - SQLite WAL cloud connection parameters (busy_timeout, synchronous, integrity)
      - Multi-container resource quotas (API <= 256MB, Redis <= 64MB, Nginx <= 128MB)
      - Production manifest generation with 25 verified static routes
      - Astro page, React island component & zero-leak data privacy invariants
    """

    def setUp(self):
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.optimizer = CloudDeploymentOptimizer(base_dir=self.base_dir)

    def test_environment_schema_validation(self):
        """Validates environment variable schema audit and public attribution metadata."""
        test_env = {
            "PYTHONUNBUFFERED": "1",
            "LMS_DB_PATH": "/data/voltcore_lms.db",
            "VOLTCORE_JWT_SECRET": "M1T_CHROMEPET_ECE_SECURE_TOKEN_2026",
            "PUBLIC_ADMIN_EMAIL": PUBLIC_ADMIN_EMAIL
        }
        res = self.optimizer.validate_environment_schema(env_dict=test_env)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(len(res["missing_vars"]), 0)
        self.assertEqual(res["public_contact"], "ashokkumar3132008@gmail.com")
        self.assertTrue(res["secret_admin_email_isolated"])

    def test_strict_secret_isolation_in_client_bundles(self):
        """Ensures restricted admin contact details are not present in src/."""
        audit_res = self.optimizer.audit_secret_isolation()
        self.assertEqual(audit_res["status"], "PASS")
        self.assertTrue(audit_res["rbac_isolated"])
        self.assertEqual(audit_res["leaks_found"], 0)
        self.assertGreater(audit_res["scanned_files_count"], 50)

    def test_sqlite_wal_cloud_config_parameters(self):
        """Validates that SQLite WAL mode is active with optimal cloud concurrency settings."""
        wal_res = self.optimizer.audit_sqlite_wal_cloud_config()
        self.assertEqual(wal_res["status"], "PASS")
        self.assertTrue(wal_res["valid"])
        self.assertTrue(wal_res["is_wal"])
        self.assertEqual(wal_res["journal_mode"], "wal")
        self.assertEqual(wal_res["integrity"], "ok")

    def test_multi_container_docker_spec_caps(self):
        """Inspects docker-compose.yml to ensure memory limits and CPU constraints are enforced."""
        compose_res = self.optimizer.audit_container_spec()
        self.assertEqual(compose_res["status"], "PASS")
        self.assertTrue(compose_res["valid"])

        services = compose_res["services_detected"]
        self.assertTrue(services["api_gateway"])
        self.assertTrue(services["redis_cache"])
        self.assertTrue(services["nginx_web"])

        self.assertTrue(compose_res["resource_caps_enforced"])
        self.assertTrue(compose_res["secret_parameterized"])

    def test_production_manifest_generation(self):
        """Validates generation of the immutable production deployment manifest."""
        manifest_res = self.optimizer.generate_production_manifest()
        manifest = manifest_res["deployment_manifest"]

        self.assertEqual(manifest["platform"], "VoltCore Apex Academia")
        self.assertIn("Madras Institute of Technology", manifest["institution"])
        self.assertIn("Ashok Kumar A", manifest["lead_architect"])
        self.assertEqual(manifest["cloud_region"], "singapore (Low-latency to Chennai / Anna University)")
        self.assertEqual(manifest["total_verified_static_routes"], 25)
        self.assertEqual(manifest["runtime_port"], 5000)
        self.assertLessEqual(manifest["resource_limits"]["target_memory_mb"], 300.0)

    def test_full_cloud_readiness_audit(self):
        """Validates that the comprehensive cloud audit returns ready = True."""
        full_audit = self.optimizer.run_full_cloud_audit()
        self.assertEqual(full_audit["status"], "PASS")
        self.assertTrue(full_audit["cloud_staging_ready"])

    def test_cloud_deploy_page_and_component_exist(self):
        """Validates existence of cloud-deploy.astro and CloudDeploymentHub.jsx."""
        page_path = os.path.join(self.base_dir, "src", "pages", "cloud-deploy.astro")
        comp_path = os.path.join(self.base_dir, "src", "components", "CloudDeploymentHub.jsx")

        self.assertTrue(os.path.exists(page_path), "cloud-deploy.astro must exist")
        self.assertTrue(os.path.exists(comp_path), "CloudDeploymentHub.jsx must exist")

        with open(page_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("CloudDeploymentHub", content)
            self.assertIn("Ashok Kumar A", content)
            self.assertIn("Docker", content)

        with open(comp_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Cloud Production Staging & Live Deployment Hub", content)
            self.assertIn("Multi-Container Topology", content)
            self.assertIn("One-Click Export", content)

    def test_privacy_invariants_no_leakage(self):
        """
        Validates that private admin contact details are strictly isolated
        and never present in cloud deploy components or scripts.
        """
        target_files = [
            os.path.join(self.base_dir, "src", "pages", "cloud-deploy.astro"),
            os.path.join(self.base_dir, "src", "components", "CloudDeploymentHub.jsx"),
            os.path.join(self.base_dir, "deploy", "cloud_deployment_optimizer.py"),
            os.path.join(self.base_dir, "src", "components", "Topbar.astro"),
            os.path.join(self.base_dir, "public", "service-worker.js")
        ]

        for file_path in target_files:
            if not os.path.exists(file_path):
                continue
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                for pattern in RESTRICTED_METADATA_PATTERNS:
                    self.assertNotIn(
                        pattern,
                        content,
                        f"CRITICAL PRIVACY VIOLATION: '{pattern}' leaked in {os.path.basename(file_path)}!"
                    )


if __name__ == "__main__":
    unittest.main()
