"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 10 IoT Smart Laboratory & Telemetry Hub
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase10_smart_lab.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import unittest
from backend.iot_telemetry_hub import SmartLabTelemetryHub, smart_lab_hub


class TestPhase10SmartLab(unittest.TestCase):
    """
    Validation suite for Phase 10:
      - Equipment power & sensor telemetry ingestion
      - Automated over-current and thermal safety trips
      - Maintenance lifecycle limits and alerts
      - Multi-bench equipment reservation and release (+120 XP)
      - Fault ticket logging and RBAC-governed resolution
      - Static page, component, and data privacy invariants
    """

    def setUp(self):
        # Create an isolated instance for each test to avoid cross-test pollution
        self.hub = SmartLabTelemetryHub()
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def test_telemetry_ingestion_and_power_calculation(self):
        """Validates that real-time voltage/current sensor data calculates power accurately."""
        res = self.hub.ingest_telemetry(
            equipment_id="OSC-DSOX1204G-01",
            voltage_v=230.0,
            current_a=0.150,
            temperature_c=37.5,
            hours_increment=1.5
        )
        self.assertEqual(res["status"], "SUCCESS")
        # 230.0 * 0.150 = 34.50 W
        self.assertEqual(res["current_power_watts"], 34.5)
        self.assertGreater(res["cumulative_hours"], 185.0)

    def test_over_current_trip_fault_alert(self):
        """Validates that drawing current exceeding max_current_a trips the safety relay."""
        res = self.hub.ingest_telemetry(
            equipment_id="OSC-DSOX1204G-01",  # max_current_a is 1.0 A
            voltage_v=230.0,
            current_a=1.450,  # exceeds 1.0 A limit
            temperature_c=38.0
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["equipment_status"], "FAULT_ALERT")
        self.assertTrue(any(a["type"] == "OVER_CURRENT_TRIP" for a in res["new_alerts"]))
        self.assertTrue(any(a["severity"] == "CRITICAL" for a in res["new_alerts"]))

    def test_thermal_overload_alert(self):
        """Validates that excessive temperature triggers an immediate thermal trip."""
        res = self.hub.ingest_telemetry(
            equipment_id="FUME-FA430-04",  # max_temperature_c is 55.0 C
            voltage_v=230.0,
            current_a=0.45,
            temperature_c=68.5  # exceeds 55.0 C limit
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["equipment_status"], "FAULT_ALERT")
        self.assertTrue(any(a["type"] == "TEMPERATURE_OVERLOAD" for a in res["new_alerts"]))

    def test_maintenance_hours_limit_alert(self):
        """Validates that exceeding operating hour threshold transitions equipment to MAINTENANCE_DUE."""
        # Weller WT1010 has 200h limit, initial is 204.5h (already seeded as MAINTENANCE_DUE)
        overview = self.hub.get_lab_overview()
        weller = next(e for e in overview["equipment"] if e["equipment_id"] == "SOLD-WT1010-03")
        self.assertEqual(weller["status"], "MAINTENANCE_DUE")
        self.assertGreaterEqual(weller["cumulative_hours"], weller["maintenance_interval_hours"])

    def test_equipment_booking_and_release_lifecycle(self):
        """Validates student equipment reservations, booking barriers, and session release."""
        # 1. Booking an idle instrument succeeds with XP award
        res_book = self.hub.book_equipment(
            equipment_id="OSC-DSOX1204G-01",
            student_id="2023MITEC042",
            bench_slot="BENCH_304_A"
        )
        self.assertEqual(res_book["status"], "SUCCESS")
        self.assertEqual(res_book["xp_reward"], 120)
        self.assertEqual(res_book["booking"]["student_id"], "2023MITEC042")

        # 2. Attempting to double-book the same occupied instrument is rejected
        res_conflict = self.hub.book_equipment(
            equipment_id="OSC-DSOX1204G-01",
            student_id="2023MITEC099",
            bench_slot="BENCH_304_A"
        )
        self.assertEqual(res_conflict["status"], "REJECTED")

        # 3. Attempting to book an instrument with maintenance due is rejected
        res_maint_reject = self.hub.book_equipment(
            equipment_id="SOLD-WT1010-03",
            student_id="2023MITEC042"
        )
        self.assertEqual(res_maint_reject["status"], "REJECTED")

        # 4. Releasing the active instrument restores ONLINE_IDLE state
        res_release = self.hub.release_equipment("OSC-DSOX1204G-01")
        self.assertEqual(res_release["status"], "SUCCESS")
        self.assertEqual(res_release["new_status"], "ONLINE_IDLE")

    def test_fault_ticket_logging_and_rbac_resolution(self):
        """Validates fault logging and strictly tests that only privileged roles can resolve faults."""
        # 1. Log a fault ticket
        ticket_res = self.hub.log_fault_ticket(
            equipment_id="PSU-DP832-02",
            fault_type="CALIBRATION_DRIFT",
            description="Channel 2 voltage offset drifted by +120mV relative to reference meter",
            reported_by="2023MITEC042"
        )
        self.assertEqual(ticket_res["status"], "SUCCESS")
        self.assertEqual(ticket_res["equipment_status"], "FAULT_ALERT")

        # 2. RBAC check: Student role cannot resolve faults (must be FORBIDDEN)
        unauth_res = self.hub.resolve_fault(
            equipment_id="PSU-DP832-02",
            resolution_notes="Student tried to self-reset",
            resolved_by_role="Student"
        )
        self.assertEqual(unauth_res["status"], "FORBIDDEN")

        # 3. RBAC check: Admin / Teacher / Lab-Instructor role succeeds
        auth_res = self.hub.resolve_fault(
            equipment_id="PSU-DP832-02",
            resolution_notes="Recalibrated Channel 2 ADC trim potentiometer to IEEE 488.2 standards.",
            resolved_by_role="Lab-Instructor"
        )
        self.assertEqual(auth_res["status"], "SUCCESS")
        self.assertEqual(auth_res["new_status"], "ONLINE_IDLE")

    def test_lab_overview_aggregation(self):
        """Validates total power, active equipment counts, and institution metadata."""
        overview = self.hub.get_lab_overview()
        self.assertIn("MIT Campus", overview["laboratory"])
        self.assertIn("Madras Institute of Technology", overview["institution"])
        self.assertEqual(overview["total_equipment"], 4)
        self.assertGreater(overview["total_power_watts"], 0.0)
        self.assertIsInstance(overview["equipment"], list)

    def test_smart_lab_page_and_component_exist(self):
        """Ensures Astro hosting page and React island component are in place."""
        page_path = os.path.join(self.base_dir, "src", "pages", "smart-lab.astro")
        component_path = os.path.join(self.base_dir, "src", "components", "SmartLabMonitor.jsx")

        self.assertTrue(os.path.isfile(page_path), "src/pages/smart-lab.astro must exist")
        self.assertTrue(os.path.isfile(component_path), "src/components/SmartLabMonitor.jsx must exist")

        with open(page_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("SmartLabMonitor", content)
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
            os.path.join(self.base_dir, "src", "pages", "smart-lab.astro"),
            os.path.join(self.base_dir, "src", "components", "SmartLabMonitor.jsx"),
            os.path.join(self.base_dir, "backend", "iot_telemetry_hub.py")
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

