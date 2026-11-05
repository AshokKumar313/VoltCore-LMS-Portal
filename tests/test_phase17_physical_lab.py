"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 17 Physical HIL Lab Automation
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase17_physical_lab.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import tempfile
import unittest
from backend.physical_hil_manager import PhysicalHILManager


class TestPhase17PhysicalLab(unittest.TestCase):
    """
    Validation suite for Phase 17:
      - Physical serial port discovery and USB-CDC enumeration metadata
      - Safe COM port mutex session locking & race contention prevention
      - Sensor telemetry serialization, CRC hashing, and SQLite WAL ingestion
      - Automated test bench assertion recording & lab rubric evaluation
      - Strict RBAC laboratory permission barriers
      - Astro page, React island component & zero-leak data privacy invariants
    """

    def setUp(self):
        # Create an isolated temporary SQLite database for each test
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.manager = PhysicalHILManager(db_path=self.temp_db_path)
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except Exception:
                pass

    def test_list_detected_ports_and_device_enumeration(self):
        """Validates enumeration of connected USB-CDC microcontrollers and lab testbeds."""
        ports = self.manager.list_detected_ports()
        self.assertGreaterEqual(len(ports), 3)

        port_ids = [p["port_id"] for p in ports]
        self.assertIn("COM3", port_ids)
        self.assertIn("COM4", port_ids)
        self.assertIn("COM7", port_ids)

        esp32 = next(p for p in ports if p["port_id"] == "COM3")
        self.assertEqual(esp32["hardware_target"], "ESP32-S3")
        self.assertEqual(esp32["vid"], "0x303A")
        self.assertEqual(esp32["pid"], "0x1001")
        self.assertFalse(esp32["is_locked"])

        stm32 = next(p for p in ports if p["port_id"] == "COM4")
        self.assertEqual(stm32["hardware_target"], "STM32F407")
        self.assertEqual(stm32["vid"], "0x0483")

    def test_safe_port_locking_and_contention_prevention(self):
        """Validates exclusive mutex port locking and contention blocking across concurrent sessions."""
        port_id = "COM3"
        user_1 = "2023MITEC042"
        user_2 = "2023MITEC099"

        # 1. User 1 acquires port lock
        lock_res = self.manager.acquire_port_lock(port_id, user_1, actor_role="Student")
        self.assertEqual(lock_res["status"], "SUCCESS")
        self.assertTrue(lock_res["locked"])
        self.assertEqual(lock_res["user_id"], user_1)

        # 2. User 2 attempts to lock the same port -> BLOCKED
        contention_res = self.manager.acquire_port_lock(port_id, user_2, actor_role="Student")
        self.assertEqual(contention_res["status"], "PORT_LOCKED_BY_ANOTHER_USER")
        self.assertFalse(contention_res["locked"])
        self.assertEqual(contention_res["locked_by"], user_1)

        # 3. User 1 releases lock
        release_res = self.manager.release_port_lock(port_id, user_1)
        self.assertEqual(release_res["status"], "SUCCESS")

        # 4. Now User 2 can acquire lock
        user2_lock = self.manager.acquire_port_lock(port_id, user_2, actor_role="Student")
        self.assertEqual(user2_lock["status"], "SUCCESS")
        self.assertTrue(user2_lock["locked"])

    def test_rbac_guest_cannot_lock_ports(self):
        """Validates that unauthenticated/guest users are barred from locking hardware."""
        res = self.manager.acquire_port_lock("COM4", "GUEST_USER", actor_role="Guest")
        self.assertEqual(res["status"], "FORBIDDEN")
        self.assertFalse(res["locked"])

    def test_sensor_telemetry_logging_and_crc_hash(self):
        """Validates ingestion of high-speed sensor telemetry packets into SQLite WAL tables."""
        frame = {
            "ch1_voltage": 3.312,
            "ch2_voltage": 1.645,
            "current_ma": 128.4,
            "bus_frequency_hz": 1000.1,
            "temperature_c": 35.6
        }

        log_res = self.manager.log_sensor_telemetry("COM3", "2023MITEC042", frame)
        self.assertEqual(log_res["status"], "SUCCESS")
        self.assertGreater(log_res["log_id"], 0)
        self.assertTrue(len(log_res["frame_crc"]) >= 8)

        # Verify persisted entry in database
        logs = self.manager.get_recent_logs(port_id="COM3", limit=10)
        self.assertGreaterEqual(len(logs), 1)
        self.assertEqual(logs[0]["port_id"], "COM3")
        self.assertAlmostEqual(logs[0]["ch1_voltage"], 3.312, places=2)

    def test_test_bench_assertions_recorder(self):
        """Validates automated evaluation of test bench criteria and XP rewards."""
        assertion_res = self.manager.run_test_bench_assertions("COM3", "2023MITEC042")
        self.assertEqual(assertion_res["status"], "SUCCESS")
        self.assertTrue(assertion_res["all_assertions_passed"])
        self.assertEqual(assertion_res["xp_earned"], 150)
        self.assertEqual(assertion_res["assertions_count"], 3)

        results = assertion_res["results"]
        ids = [r["assertion_id"] for r in results]
        self.assertIn("ASSERT_VDD_RAIL_3V3", ids)
        self.assertIn("ASSERT_GPIO_CLOCK_FREQ", ids)
        self.assertIn("ASSERT_THERMAL_HEADROOM", ids)

    def test_physical_lab_overview_metrics(self):
        """Validates laboratory dashboard overview metrics."""
        ov = self.manager.get_lab_overview()
        self.assertIn("Madras Institute of Technology", ov["institution"])
        self.assertIn("Ashok Kumar A", ov["platform_lead"])
        self.assertGreaterEqual(ov["total_detected_ports"], 3)
        self.assertIn("ports", ov)

    def test_physical_lab_page_and_component_exist(self):
        """Validates existence of physical-lab.astro and PhysicalLabBridge.jsx."""
        page_path = os.path.join(self.base_dir, "src", "pages", "physical-lab.astro")
        comp_path = os.path.join(self.base_dir, "src", "components", "PhysicalLabBridge.jsx")

        self.assertTrue(os.path.exists(page_path), "physical-lab.astro must exist")
        self.assertTrue(os.path.exists(comp_path), "PhysicalLabBridge.jsx must exist")

        with open(page_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("PhysicalLabBridge", content)
            self.assertIn("Ashok Kumar A", content)
            self.assertIn("PHASE 17 ENTERPRISE", content)

        with open(comp_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Live Serial Terminal Stream", content)
            self.assertIn("Automated Assertion Recorder", content)
            self.assertIn("Lab 304 Equipment Roster", content)

    def test_privacy_invariants_no_leakage(self):
        """
        Validates that private admin contact details are strictly isolated
        and never leaked in physical lab components or manager files.
        """
        p1 = "".join(["ashok", "kumar", "2008313", "@", "gmail.com"])
        p2 = "".join(["9597", "382878"])
        p3 = "+91 " + p2
        patterns = [p1, p2, p3]

        target_files = [
            os.path.join(self.base_dir, "src", "pages", "physical-lab.astro"),
            os.path.join(self.base_dir, "src", "components", "PhysicalLabBridge.jsx"),
            os.path.join(self.base_dir, "backend", "physical_hil_manager.py"),
            os.path.join(self.base_dir, "src", "components", "Topbar.astro"),
            os.path.join(self.base_dir, "public", "service-worker.js")
        ]

        for file_path in target_files:
            if not os.path.exists(file_path):
                continue
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                for pattern in patterns:
                    self.assertNotIn(
                        pattern,
                        content,
                        f"CRITICAL PRIVACY VIOLATION: '{pattern}' leaked in {os.path.basename(file_path)}!"
                    )


if __name__ == "__main__":
    unittest.main()
