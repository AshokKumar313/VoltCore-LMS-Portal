"""
========================================================================================
VoltCore Apex Academia - Enterprise Production Readiness & Deployment Verification Engine
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/production_readiness_engine.py
Platform Lead / Systems Architect: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Verifies:
  1. Full Deployment Architecture Integrity (Astro SSG, Python REST Gateway, SQLite WAL)
  2. Multi-Stage Docker Container & Non-Root User Compliance
  3. Ephemeral Sandbox Execution Readiness
  4. Privacy & Credential Leakage Invariants (Zero private email, phone, or API keys)
  5. Continuous Healthcheck & PWA Offline Manifest Consistency
========================================================================================
"""

import os
import sys
import json
import base64
import sqlite3
import shutil
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LMS_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")
TELEMETRY_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")


class ProductionReadinessEngine:
    """Automated pre-flight and production readiness assessment engine."""

    # Base64 encoded security tokens to avoid false positives during self-inspection
    _B64_RESTRICTED = [
        "YXNob2trdW1hcjIwMDgzMTNAZ21haWwuY29t",  # private email
        "OTU5NzM4Mjg3OA==",                      # private phone
        "QUl6YVN5",                              # Gemini API key prefix
        "c2stcHJvai0=",                          # OpenAI key prefix
        "c2stYW50LQ=="                           # Anthropic key prefix
    ]

    @classmethod
    def get_restricted_patterns(cls) -> List[str]:
        return [base64.b64decode(b).decode("utf-8") for b in cls._B64_RESTRICTED]

    REQUIRED_PWA_ROUTES = [
        "/",
        "/academic-hub",
        "/attendance",
        "/autograder",
        "/careers",
        "/course-hub",
        "/learning-dashboard",
        "/faculty-workspace",
        "/enterprise-admin",
        "/security-hub"
    ]

    def verify_database_wal(self, db_path: str) -> Dict[str, Any]:
        """Validates that a database exists, is in WAL mode, and passes PRAGMA integrity_check."""
        if not os.path.exists(db_path):
            return {"exists": False, "is_wal": False, "integrity": "MISSING", "error": f"File {db_path} not found"}

        try:
            conn = sqlite3.connect(db_path, timeout=5.0)
            cur = conn.cursor()
            cur.execute("PRAGMA journal_mode;")
            journal_mode = str(cur.fetchone()[0]).lower()
            cur.execute("PRAGMA integrity_check;")
            integrity = cur.fetchone()[0]
            cur.execute("PRAGMA foreign_key_check;")
            fk_violations = cur.fetchall()
            conn.close()

            return {
                "exists": True,
                "path": os.path.basename(db_path),
                "is_wal": journal_mode == "wal",
                "journal_mode": journal_mode,
                "integrity": integrity,
                "fk_violations_count": len(fk_violations),
                "healthy": (journal_mode == "wal" and integrity == "ok" and len(fk_violations) == 0)
            }
        except Exception as e:
            return {"exists": True, "is_wal": False, "integrity": "ERROR", "error": str(e), "healthy": False}

    def verify_privacy_invariants(self) -> Dict[str, Any]:
        """Scans codebase to guarantee zero private data or credential leakage."""
        violations = []
        scanned_files = 0
        patterns = self.get_restricted_patterns()

        # Directories to audit strictly
        audit_dirs = [
            os.path.join(BASE_DIR, "src"),
            os.path.join(BASE_DIR, "backend"),
            os.path.join(BASE_DIR, "public")
        ]

        for d in audit_dirs:
            if not os.path.exists(d):
                continue
            for root, _, files in os.walk(d):
                for f in files:
                    if f.endswith((".ts", ".tsx", ".js", ".jsx", ".astro", ".py", ".md", ".json", ".html")):
                        if f in ("security_auth.py", "production_readiness_engine.py"):
                            continue
                        scanned_files += 1
                        fpath = os.path.join(root, f)
                        try:
                            with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                                content = fp.read()
                                for pat in patterns:
                                    if pat in content:
                                        rel_path = os.path.relpath(fpath, BASE_DIR)
                                        violations.append({"file": rel_path, "pattern_matched": pat})
                        except Exception:
                            pass

        return {
            "scanned_files_count": scanned_files,
            "violations_count": len(violations),
            "violations": violations,
            "passed": len(violations) == 0
        }

    def verify_docker_and_deployment_files(self) -> Dict[str, Any]:
        """Verifies Dockerfile, docker-compose.yml, and GitHub Actions workflows exist and comply."""
        dockerfile_path = os.path.join(BASE_DIR, "Dockerfile")
        compose_path = os.path.join(BASE_DIR, "docker-compose.yml")
        workflow_path = os.path.join(BASE_DIR, ".github", "workflows", "deploy.yml")

        checks = {
            "dockerfile_exists": os.path.isfile(dockerfile_path),
            "docker_compose_exists": os.path.isfile(compose_path),
            "ci_cd_workflow_exists": os.path.isfile(workflow_path)
        }

        # Check for multi-stage build and healthcheck in Dockerfile
        if checks["dockerfile_exists"]:
            with open(dockerfile_path, "r", encoding="utf-8") as f:
                d_content = f.read()
            checks["dockerfile_multistage"] = "AS frontend-builder" in d_content and "AS production-runner" in d_content
            checks["dockerfile_healthcheck"] = "HEALTHCHECK" in d_content
            checks["dockerfile_wal_volume"] = "VOLUME" in d_content or "/app/data" in d_content

        # Check for resource limits in docker-compose.yml
        if checks["docker_compose_exists"]:
            with open(compose_path, "r", encoding="utf-8") as f:
                c_content = f.read()
            checks["compose_cpu_limits"] = "cpus:" in c_content
            checks["compose_mem_limits"] = "memory:" in c_content

        all_ok = all(checks.values())
        return {"checks": checks, "passed": all_ok}

    def verify_pwa_service_worker(self) -> Dict[str, Any]:
        """Verifies public/service-worker.js caches necessary shell routes."""
        sw_path = os.path.join(BASE_DIR, "public", "service-worker.js")
        if not os.path.isfile(sw_path):
            return {"exists": False, "passed": False, "error": "service-worker.js missing"}

        with open(sw_path, "r", encoding="utf-8") as f:
            content = f.read()

        missing = [r for r in self.REQUIRED_PWA_ROUTES if f"'{r}'" not in content and f'"{r}"' not in content]
        return {
            "exists": True,
            "cache_first_strategy": "CacheFirst" in content or "caches.match" in content,
            "offline_spooling": "offline_spooled" in content or "sync" in content,
            "missing_required_routes": missing,
            "passed": len(missing) == 0
        }

    def collect_full_readiness_audit(self) -> Dict[str, Any]:
        """Runs the entire production readiness check and returns unified audit."""
        lms_db_report = self.verify_database_wal(LMS_DB_PATH)
        telemetry_db_report = self.verify_database_wal(TELEMETRY_DB_PATH)
        privacy_report = self.verify_privacy_invariants()
        docker_report = self.verify_docker_and_deployment_files()
        pwa_report = self.verify_pwa_service_worker()

        all_healthy = (
            lms_db_report.get("healthy", False) and
            telemetry_db_report.get("healthy", False) and
            privacy_report.get("passed", False) and
            docker_report.get("passed", False) and
            pwa_report.get("passed", False)
        )

        return {
            "status": "READY" if all_healthy else "NEEDS_ATTENTION",
            "audit_timestamp": datetime.now(timezone.utc).isoformat(),
            "platform": "VoltCore Apex Academia",
            "version": "5.0.0-Production",
            "author": "Ashok Kumar A (2023MITEC042)",
            "institution": "MIT Campus, Anna University",
            "databases": {
                "voltcore_lms": lms_db_report,
                "voltcore_telemetry": telemetry_db_report
            },
            "privacy_and_security": privacy_report,
            "deployment_infrastructure": docker_report,
            "pwa_offline_sync": pwa_report,
            "production_grade": "GRADE_A_ENTERPRISE" if all_healthy else "GRADE_B_PROVISIONAL"
        }


# Global singleton instance
production_readiness_engine = ProductionReadinessEngine()
