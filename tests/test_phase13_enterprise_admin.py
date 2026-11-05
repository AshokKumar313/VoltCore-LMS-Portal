"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 13 Enterprise Administration & Accreditation
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase13_enterprise_admin.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import tempfile
import unittest
from backend.enterprise_admin_engine import EnterpriseAdminEngine


class TestPhase13EnterpriseAdmin(unittest.TestCase):
    """
    Validation suite for Phase 13:
      - Faculty workload heatmaps and overload alert detection
      - Automated NBA CO-PO attainment matrix derivation (Target 70% / 2.1 level)
      - NAAC Criteria 1-7 scoring and SHA-256 cryptographic audit chain
      - Multi-department course allocation and venue collision detection
      - Strict RBAC admin-only permission barriers
      - Astro page, React island component & data privacy invariants
    """

    def setUp(self):
        # Create an isolated temporary SQLite database for each test
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.engine = EnterpriseAdminEngine(db_path=self.temp_db_path)
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except Exception:
                pass

    def test_faculty_workload_metrics_and_overload_detection(self):
        """Validates faculty weekly workload calculation and status assignment."""
        metrics = self.engine.get_faculty_workload_metrics()
        self.assertGreaterEqual(len(metrics), 4)

        # Check total hours calculation
        for f in metrics:
            self.assertEqual(f["total_hours"], f["teaching_hours"] + f["lab_supervision_hours"])
            if f["total_hours"] >= 26:
                self.assertIn(f["workload_status"], ("HIGH_WORKLOAD", "CRITICAL_OVERLOAD"))

        # Verify Ashok Kumar A is present
        ashok = next(f for f in metrics if "Ashok Kumar A" in f["name"])
        self.assertEqual(ashok["student_rating"], 4.95)
        self.assertEqual(ashok["department"], "Electronics Engineering")

    def test_nba_co_po_matrix_attainment_calculation(self):
        """Validates automated NBA CO-PO attainment aggregation against 70% threshold."""
        res = self.engine.compute_nba_co_po_matrix()

        self.assertEqual(res["regulation"], "Anna University R2023")
        self.assertEqual(res["target_threshold_level"], 2.10)
        self.assertGreater(res["nba_compliance_percentage"], 75.0)

        matrix = res["po_attainment_matrix"]
        self.assertIn("PO1", matrix)
        self.assertIn("PO5", matrix)
        self.assertIn("PSO1", matrix)
        self.assertIn("PSO2", matrix)

        # Check PO1 is attained (should be ~2.50)
        self.assertEqual(matrix["PO1"]["status"], "ATTAINED")
        self.assertGreaterEqual(matrix["PO1"]["attainment_level"], 2.10)

    def test_naac_audit_event_logging_and_sha256_cryptographic_integrity(self):
        """Validates immutable SHA-256 block creation and tamper verification."""
        # 1. Log multiple administrative actions
        ev1 = self.engine.record_naac_audit_event(
            actor_role="Admin",
            action="CURRICULUM_UPDATE",
            resource="EC8702",
            details="Updated Syllabus for FreeRTOS DMA Lab Module."
        )
        self.assertEqual(ev1["status"], "SUCCESS")
        self.assertIn("LOG-", ev1["log_id"])

        ev2 = self.engine.record_naac_audit_event(
            actor_role="Dean_Academic",
            action="ACCREDITATION_AUDIT",
            resource="NBA_TIER_1",
            details="Validated continuous internal evaluation rubrics."
        )
        self.assertEqual(ev2["status"], "SUCCESS")
        self.assertEqual(ev2["prev_hash"], ev1["entry_hash"])

        # 2. Verify complete ledger integrity
        audit_res = self.engine.verify_audit_log_integrity()
        self.assertEqual(audit_res["status"], "SUCCESS")
        self.assertTrue(audit_res["verified"])
        self.assertFalse(audit_res["tampered"])
        self.assertGreaterEqual(audit_res["total_records"], 3)

    def test_course_allocation_and_venue_conflict_detection(self):
        """Validates academic course section allocation and collision prevention."""
        # 1. Successful allocation
        res = self.engine.allocate_course(
            course_code="EC8709",
            course_name="Automotive CAN-Bus Lab",
            department="Electronics Engineering",
            faculty_id="FAC-MIT-004",
            faculty_name="Ashok Kumar A",
            credit_hours=3,
            slot="Slot-D (Tue 09:00 - 12:00)",
            venue="Lab 304 Automotive Bay",
            capacity=40,
            actor_role="Admin"
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["course_code"], "EC8709")

        # 2. Attempting to allocate the same slot and venue triggers a CONFLICT
        conflict_res = self.engine.allocate_course(
            course_code="EC8715",
            course_name="Robotics Embedded Systems",
            department="Electronics Engineering",
            faculty_id="FAC-MIT-002",
            faculty_name="Dr. M. V. Geetha",
            credit_hours=3,
            slot="Slot-D (Tue 09:00 - 12:00)",
            venue="Lab 304 Automotive Bay",  # Collision!
            capacity=40,
            actor_role="Admin"
        )
        self.assertEqual(conflict_res["status"], "CONFLICT")
        self.assertIn("Venue collision", conflict_res["error"])

    def test_rbac_admin_only_permission_barriers(self):
        """Validates that unprivileged Student role cannot allocate courses or modify NAAC ledgers."""
        # 1. Student attempting course allocation must be FORBIDDEN
        unauth_alloc = self.engine.allocate_course(
            course_code="EC8799",
            course_name="Self-Study Embedded Project",
            department="Electronics Engineering",
            faculty_id="FAC-MIT-001",
            faculty_name="Dr. S. K. Ramesh",
            credit_hours=2,
            slot="Slot-E",
            venue="Seminar Hall",
            actor_role="Student"
        )
        self.assertEqual(unauth_alloc["status"], "FORBIDDEN")

        # 2. Student attempting NAAC audit ledger entry must be FORBIDDEN
        unauth_audit = self.engine.record_naac_audit_event(
            actor_role="Student",
            action="UNAUTHORIZED_TAMPER",
            resource="ADMIN_LOG",
            details="Student attempted direct entry"
        )
        self.assertEqual(unauth_audit["status"], "FORBIDDEN")

    def test_enterprise_admin_page_and_component_exist(self):
        """Ensures Astro hosting page and React island component are in place."""
        page_path = os.path.join(self.base_dir, "src", "pages", "enterprise-admin.astro")
        component_path = os.path.join(self.base_dir, "src", "components", "EnterpriseAdminDashboard.jsx")

        self.assertTrue(os.path.isfile(page_path), "src/pages/enterprise-admin.astro must exist")
        self.assertTrue(os.path.isfile(component_path), "src/components/EnterpriseAdminDashboard.jsx must exist")

        with open(page_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("EnterpriseAdminDashboard", content)
            self.assertIn("Madras Institute of Technology", content)
            self.assertIn("Ashok Kumar A", content)

    def test_data_privacy_invariants_no_leakage(self):
        """Strictly ensures private admin contact credentials are never present in client files."""
        restricted_patterns = [
            "ashokkumar2008313@gmail.com",
            "+91 9597382878",
            "9597382878"
        ]
        files_to_check = [
            os.path.join(self.base_dir, "src", "pages", "enterprise-admin.astro"),
            os.path.join(self.base_dir, "src", "components", "EnterpriseAdminDashboard.jsx"),
            os.path.join(self.base_dir, "backend", "enterprise_admin_engine.py")
        ]

        for filepath in files_to_check:
            if not os.path.isfile(filepath):
                continue
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                for pattern in restricted_patterns:
                    self.assertNotIn(
                        pattern,
                        content,
                        f"Data privacy breach: Restricted credential '{pattern}' found in '{filepath}'!"
                    )


if __name__ == "__main__":
    unittest.main()

