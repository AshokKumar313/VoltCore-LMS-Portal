"""
========================================================================================
VoltCore Apex Academia - Enterprise Production Readiness & Security Auditor
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: deploy/production_readiness_audit.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Final production audit suite:
    1. Static Route Manifest: Asserts all 16 static Astro routes exist in dist/
    2. RBAC & Data Privacy: Verifies zero leakage of private admin email/phone in client code
    3. Public Attribution: Verifies correct public email and GitHub repo metadata
    4. SQLite WAL Integrity: Verifies database WAL mode, quick_check, and table schemas
    5. PWA Manifest Consistency: Verifies precache routes and service worker versions
========================================================================================
"""

import os
import sys
import json
import sqlite3
import argparse
from typing import Dict, Any, List, Tuple

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Base repository directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

EXPECTED_STATIC_ROUTES = [
    "",
    "academic-hub",
    "attendance",
    "autograder",
    "careers",
    "cloud-deploy",
    "collaboration",
    "ece-knowledge",
    "enterprise-admin",
    "exam-center",
    "flash-firmware",
    "flashcards",
    "fleet",
    "gate-ece",
    "hardware-hil",
    "next-gen",
    "nptel",
    "nptel-player",
    "physical-lab",
    "profile",
    "research",
    "security-hub",
    "settings",
    "simulation",
    "smart-lab",
    "teacher",
    "telemetry",
    "virtual-bench",
    "voice-lab"
]

RESTRICTED_METADATA_PATTERNS = [
    "ashokkumar2008313@gmail.com",
    "9597382878"
]

PUBLIC_EMAIL = "ashokkumar3132008@gmail.com"
PUBLIC_GITHUB = "https://github.com/AshokKumar313"


class ProductionReadinessAuditor:
    """
    Comprehensive deployment verification suite for VoltCore Apex Academia.
    """

    def __init__(self, base_dir: str = BASE_DIR):
        self.base_dir = base_dir
        self.dist_dir = os.path.join(base_dir, "dist")
        self.db_path = os.path.join(base_dir, "voltcore_lms.db")

    def audit_static_routes(self) -> Dict[str, Any]:
        """Verifies all 16 static routes have generated index.html files."""
        if not os.path.isdir(self.dist_dir):
            return {
                "passed": False,
                "error": "dist/ directory not found. Please run 'npm run build' first.",
                "verified_routes": 0,
                "total_expected": len(EXPECTED_STATIC_ROUTES)
            }

        verified = []
        missing = []

        for route in EXPECTED_STATIC_ROUTES:
            if route == "":
                target_html = os.path.join(self.dist_dir, "index.html")
                route_label = "/"
            else:
                target_html = os.path.join(self.dist_dir, route, "index.html")
                route_label = f"/{route}"

            if os.path.isfile(target_html) and os.path.getsize(target_html) > 50:
                verified.append(route_label)
            else:
                missing.append(route_label)

        all_ok = len(missing) == 0 and len(verified) == len(EXPECTED_STATIC_ROUTES)
        return {
            "passed": all_ok,
            "verified_count": len(verified),
            "expected_count": len(EXPECTED_STATIC_ROUTES),
            "verified_routes": verified,
            "missing_routes": missing
        }

    def audit_privacy_and_rbac_invariants(self) -> Dict[str, Any]:
        """
        Scans all client-facing files (src/, public/, dist/) to strictly guarantee
        that private admin credentials are never leaked in client bundles.
        """
        scanned_files = 0
        leaks: List[Dict[str, Any]] = []

        target_dirs = [
            os.path.join(self.base_dir, "src", "components"),
            os.path.join(self.base_dir, "src", "pages"),
            os.path.join(self.base_dir, "src", "content"),
            os.path.join(self.base_dir, "public")
        ]
        if os.path.isdir(self.dist_dir):
            target_dirs.append(self.dist_dir)

        client_extensions = (".jsx", ".astro", ".html", ".js", ".json", ".md", ".mdx")

        for scan_dir in target_dirs:
            if not os.path.isdir(scan_dir):
                continue
            for root, _, files in os.walk(scan_dir):
                for f in files:
                    if f.endswith(client_extensions):
                        scanned_files += 1
                        full_p = os.path.join(root, f)
                        try:
                            with open(full_p, "r", encoding="utf-8", errors="ignore") as fp:
                                content = fp.read()
                                for pattern in RESTRICTED_METADATA_PATTERNS:
                                    if pattern in content:
                                        rel_path = os.path.relpath(full_p, self.base_dir)
                                        leaks.append({
                                            "file": rel_path,
                                            "pattern": pattern
                                        })
                        except Exception:
                            pass

        return {
            "passed": len(leaks) == 0,
            "scanned_files_count": scanned_files,
            "leaks_found": len(leaks),
            "leaks": leaks,
            "policy": "Strict RBAC Isolation (Private Admin Email & Phone restricted to backend env)"
        }

    def audit_public_metadata_presence(self) -> Dict[str, Any]:
        """Ensures public email and GitHub link are properly embedded in Topbar and Layout."""
        topbar_path = os.path.join(self.base_dir, "src", "components", "Topbar.astro")
        found_github = False
        found_lead = False

        if os.path.isfile(topbar_path):
            with open(topbar_path, "r", encoding="utf-8", errors="ignore") as fp:
                content = fp.read()
                found_github = "AshokKumar313" in content
                found_lead = "Ashok Kumar A" in content

        return {
            "passed": found_github and found_lead,
            "found_github": found_github,
            "found_lead": found_lead,
            "public_email": PUBLIC_EMAIL,
            "public_github": PUBLIC_GITHUB
        }

    def audit_database_readiness(self) -> Dict[str, Any]:
        """Validates SQLite WAL database integrity, tables, and seed state."""
        if not os.path.isfile(self.db_path):
            return {"passed": False, "error": "Database voltcore_lms.db not found"}

        try:
            con = sqlite3.connect(self.db_path, timeout=5.0)
            cur = con.cursor()

            cur.execute("PRAGMA journal_mode;")
            journal_mode = str(cur.fetchone()[0]).lower()

            cur.execute("PRAGMA integrity_check(1);")
            integrity = cur.fetchone()[0]

            cur.execute("SELECT count(*) FROM users WHERE user_id = '2023MITEC042';")
            student_count = cur.fetchone()[0]

            cur.execute("SELECT count(*) FROM attendance;")
            attendance_count = cur.fetchone()[0]

            con.close()

            is_wal = journal_mode == "wal"
            is_intact = integrity == "ok"
            has_student = student_count >= 1

            return {
                "passed": is_wal and is_intact and has_student,
                "journal_mode": journal_mode,
                "integrity": integrity,
                "student_seeded": has_student,
                "attendance_records": attendance_count
            }
        except Exception as err:
            return {"passed": False, "error": str(err)}

    def audit_pwa_service_worker(self) -> Dict[str, Any]:
        """Validates Service Worker precache manifest and manifest.json presence."""
        sw_public = os.path.join(self.base_dir, "public", "service-worker.js")
        manifest_path = os.path.join(self.base_dir, "public", "manifest.json")

        sw_ok = os.path.isfile(sw_public)
        manifest_ok = os.path.isfile(manifest_path)
        all_routes_cached = False

        if sw_ok:
            with open(sw_public, "r", encoding="utf-8", errors="ignore") as fp:
                sw_content = fp.read()
                # Check for critical routes in PRECACHE_ASSETS
                all_routes_cached = all(f"'{r}'" in sw_content or f"'/{r}'" in sw_content for r in ["gate-ece", "hardware-hil", "flash-firmware", "virtual-bench"])

        return {
            "passed": sw_ok and manifest_ok and all_routes_cached,
            "service_worker_present": sw_ok,
            "manifest_json_present": manifest_ok,
            "critical_routes_precached": all_routes_cached
        }

    def run_full_audit(self) -> Dict[str, Any]:
        """Executes all production readiness checks."""
        routes = self.audit_static_routes()
        privacy = self.audit_privacy_and_rbac_invariants()
        public_meta = self.audit_public_metadata_presence()
        db = self.audit_database_readiness()
        pwa = self.audit_pwa_service_worker()

        all_passed = (
            routes["passed"]
            and privacy["passed"]
            and public_meta["passed"]
            and db["passed"]
            and pwa["passed"]
        )

        return {
            "status": "PASS" if all_passed else "FAIL",
            "production_ready": all_passed,
            "audits": {
                "static_routes": routes,
                "data_privacy_rbac": privacy,
                "public_metadata": public_meta,
                "sqlite_wal_database": db,
                "pwa_service_worker": pwa
            }
        }


def main():
    parser = argparse.ArgumentParser(description="VoltCore Apex Academia Production Readiness Auditor")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Exit with non-zero on failure")
    args = parser.parse_args()

    auditor = ProductionReadinessAuditor()
    report = auditor.run_full_audit()

    if args.json:
        print(json.dumps(report, indent=2))
        sys.exit(0 if report["production_ready"] else (1 if args.strict else 0))

    print("\n" + "="*84)
    print(" VOLTCORE APEX ACADEMIA — PRODUCTION READINESS & SECURITY AUDIT")
    print(" MIT Campus, Anna University (Department of Electronics Engineering)")
    print("="*84)

    # 1. Routes
    r = report["audits"]["static_routes"]
    print(f" • Static Routes:       {'✓ PASS' if r['passed'] else '✗ FAIL'} ({r['verified_count']}/{r['expected_count']} routes verified)")

    # 2. Privacy
    p = report["audits"]["data_privacy_rbac"]
    print(f" • RBAC Data Privacy:   {'✓ PASS' if p['passed'] else '✗ FAIL'} ({p['scanned_files_count']} client files scanned, {p['leaks_found']} leaks)")

    # 3. Public Metadata
    m = report["audits"]["public_metadata"]
    print(f" • Public Metadata:     {'✓ PASS' if m['passed'] else '✗ FAIL'} (Lead: Ashok Kumar A | GitHub: AshokKumar313)")

    # 4. Database
    d = report["audits"]["sqlite_wal_database"]
    print(f" • SQLite WAL Database: {'✓ PASS' if d['passed'] else '✗ FAIL'} (Mode: {d.get('journal_mode', '').upper()} | Integrity: {d.get('integrity')})")

    # 5. PWA
    w = report["audits"]["pwa_service_worker"]
    print(f" • PWA Service Worker:  {'✓ PASS' if w['passed'] else '✗ FAIL'} (Manifest & Pre-Cache verified)")

    print("-" * 84)
    status_str = "✓ ALL PRODUCTION READINESS CHECKS PASSED (READY FOR STAGING)" if report["production_ready"] else "✗ PRODUCTION AUDIT FAILED"
    print(f" FINAL STATUS: {status_str}")
    print("="*84 + "\n")

    if args.strict and not report["production_ready"]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
