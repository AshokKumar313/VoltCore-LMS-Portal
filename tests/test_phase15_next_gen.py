"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 15 Next-Gen Innovations & AI Academic Agent
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase15_next_gen.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import tempfile
import unittest
import sqlite3
from backend.next_gen_agent_engine import (
    NextGenAgentEngine,
    CURRICULUM_KNOWLEDGE_GRAPH,
    FAULT_DIAGNOSTIC_CATALOG,
    CAREER_TRACKS
)


class TestPhase15NextGenAgent(unittest.TestCase):
    """
    Validation suite for Phase 15:
      - Smart syllabus progression recommendations with AU R2023 prerequisite trees
      - Automated lab firmware troubleshooting & root cause diagnostics
      - Predictive career pathway fit scoring for core hardware & semiconductor domains
      - MIT Campus Virtual Lab 304 digital twin telemetry
      - Astro page, React island component & strict data privacy invariants
    """

    def setUp(self):
        # Create an isolated temporary SQLite database for each test
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.engine = NextGenAgentEngine(db_path=self.temp_db_path)
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except Exception:
                pass

    def test_syllabus_progression_recommendation_and_prerequisites(self):
        """Validates Anna University R2023 prerequisite chains and smart module recommendation."""
        # Scenario 1: Student has completed foundational modules
        completed = ["1-iot-foundations", "6-embedded-rtos", "7-analog-signal-integrity"]
        rec = self.engine.recommend_syllabus_progression(
            user_id="2023MITEC042",
            completed_modules=completed
        )

        self.assertEqual(rec["status"], "SUCCESS")
        self.assertEqual(rec["user_id"], "2023MITEC042")
        self.assertEqual(rec["completed_modules_count"], 3)
        self.assertGreaterEqual(rec["curriculum_mastery_pct"], 30.0)
        self.assertLessEqual(rec["curriculum_mastery_pct"], 100.0)

        # Next best module should be unlocked (e.g. 8-advanced-rtos-dma or 2-automotive-edge)
        best = rec["next_best_module"]
        self.assertTrue(best["prerequisites_met"])
        self.assertIn(best["id"], ("8-advanced-rtos-dma", "2-automotive-edge", "5-riscv-fpga", "10-gate-ece-instrumentation"))
        self.assertIn("Prerequisites satisfied", best["rationale"])

        # Scenario 2: Student has only completed 1-iot-foundations; 8-advanced-rtos-dma must NOT be unlocked
        unlocked_ids = [m["module_id"] for m in self.engine.recommend_syllabus_progression(
            user_id="STU_NEW",
            completed_modules=["1-iot-foundations"]
        )["unlocked_modules"]]
        self.assertNotIn("8-advanced-rtos-dma", unlocked_ids)
        self.assertNotIn("9-tiny-ml-edge", unlocked_ids)

    def test_lab_issue_automated_diagnostic(self):
        """Validates automated firmware fault detection, confidence scoring, and actionable fixes."""
        # 1. Watchdog Starvation Diagnostic
        diag_wdt = self.engine.diagnose_lab_issue(
            symptom_query="FreeRTOS task watchdog timeout triggered in tight telemetry loop",
            hardware_target="ESP32-S3"
        )
        self.assertEqual(diag_wdt["status"], "SUCCESS")
        d1 = diag_wdt["diagnosis"]
        self.assertEqual(d1["fault_code"], "TASK_WATCHDOG_TIMEOUT")
        self.assertGreaterEqual(d1["confidence"], 85.0)
        self.assertIn("TIMG_WDTCONFIG0_REG", d1["registers_to_inspect"])
        self.assertIn("vTaskDelay", d1["actionable_fix"])

        # 2. DMA FIFO Error Diagnostic
        diag_dma = self.engine.diagnose_lab_issue(
            symptom_query="DMA stream FIFO underrun during SPI audio stream transfer",
            hardware_target="STM32F407"
        )
        self.assertEqual(diag_dma["status"], "SUCCESS")
        d2 = diag_dma["diagnosis"]
        self.assertEqual(d2["fault_code"], "DMA_FIFO_ERROR")
        self.assertGreaterEqual(d2["confidence"], 85.0)
        self.assertIn("DMA_SxFCR", d2["registers_to_inspect"])
        self.assertIn("aligned(4)", d2["actionable_fix"])

        # 3. I2C Bus NACK Diagnostic
        diag_i2c = self.engine.diagnose_lab_issue(
            symptom_query="I2C slave peripheral address NACK detected on MFRC522 scan",
            hardware_target="ESP32-S3"
        )
        self.assertEqual(diag_i2c["status"], "SUCCESS")
        d3 = diag_i2c["diagnosis"]
        self.assertEqual(d3["fault_code"], "I2C_NACK_ADDR")
        self.assertGreaterEqual(d3["confidence"], 85.0)
        self.assertIn("4.7k", d3["hardware_check"])

        # 4. Unknown symptom fallback
        diag_unknown = self.engine.diagnose_lab_issue(
            symptom_query="Random uncharacterized noise on breadboard",
            hardware_target="ESP32-S3"
        )
        self.assertEqual(diag_unknown["status"], "SUCCESS")
        self.assertEqual(diag_unknown["diagnosis"]["fault_code"], "GENERAL_BUS_FAULT")

    def test_predictive_career_path_analytics(self):
        """Validates career trajectory fit scoring across the 4 core ECE industry tracks."""
        pred = self.engine.predict_career_path(
            user_id="2023MITEC042",
            student_ratings={"FreeRTOS": 9.8, "DMA": 9.6, "CAN_Bus": 8.5, "Verilog_RTL": 7.5, "TinyML": 8.0}
        )

        self.assertEqual(pred["status"], "SUCCESS")
        self.assertEqual(pred["user_id"], "2023MITEC042")
        self.assertEqual(len(pred["all_pathways"]), 4)

        # Primary track should be Embedded Firmware Architect
        primary = pred["primary_track"]
        self.assertEqual(primary["track_id"], "EMBEDDED_FIRMWARE_ARCHITECT")
        self.assertGreaterEqual(primary["fit_score"], 90.0)
        self.assertLessEqual(primary["fit_score"], 99.5)
        self.assertIn("Qualcomm", primary["target_companies"])
        self.assertIn("FreeRTOS", primary["core_domains"])
        self.assertIn("LPA", primary["median_salary_range"])

    def test_mit_campus_digital_twin_telemetry(self):
        """Validates Lab 304 virtual twin sensor telemetry and connected hardware testbeds."""
        twin = self.engine.get_digital_twin_telemetry()

        self.assertIn("Madras Institute of Technology", twin["institution"])
        self.assertEqual(twin["lab_designation"], "Lab 304 - Embedded Systems & IoT Apex Facility")
        self.assertEqual(twin["digital_twin_status"], "ONLINE_SYNCHRONIZED")

        # Environmental sanity bounds
        env = twin["environmental_telemetry"]
        self.assertGreaterEqual(env["ambient_temperature_c"], 20.0)
        self.assertLessEqual(env["ambient_temperature_c"], 30.0)
        self.assertGreaterEqual(env["relative_humidity_pct"], 30.0)
        self.assertLessEqual(env["relative_humidity_pct"], 75.0)

        # Nodes check
        nodes = twin["connected_hardware_nodes"]
        self.assertGreaterEqual(len(nodes), 3)
        targets = [n["target"] for n in nodes]
        self.assertTrue(any("ESP32" in t for t in targets))
        self.assertTrue(any("STM32" in t for t in targets))
        self.assertTrue(any("Wokwi" in t for t in targets))

    def test_next_gen_overview_metrics(self):
        """Validates dashboard overview aggregation."""
        ov = self.engine.get_next_gen_overview(user_id="2023MITEC042")
        self.assertIn("Madras Institute of Technology", ov["institution"])
        self.assertIn("Ashok Kumar A", ov["platform_lead"])
        self.assertEqual(ov["regulation"], "Anna University Regulation 2023")
        self.assertEqual(ov["agent_status"], "ACTIVE_AUTONOMOUS_ONLINE")
        self.assertIn("next_best_module", ov)
        self.assertIn("digital_twin", ov)

    def test_next_gen_page_and_component_exist(self):
        """Validates existence of the Next-Gen Astro page and React island component."""
        page_path = os.path.join(self.base_dir, "src", "pages", "next-gen.astro")
        comp_path = os.path.join(self.base_dir, "src", "components", "NextGenInnovationHub.jsx")

        self.assertTrue(os.path.exists(page_path), "next-gen.astro page must exist")
        self.assertTrue(os.path.exists(comp_path), "NextGenInnovationHub.jsx must exist")

        with open(page_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("NextGenInnovationHub", content)
            self.assertIn("Ashok Kumar A", content)
            self.assertIn("Regulation 2023", content)

        with open(comp_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Autonomous AI Academic Agent", content)
            self.assertIn("Lab Troubleshooting Engine", content)
            self.assertIn("Predictive Career Pathways", content)

    def test_data_privacy_invariants_no_leakage(self):
        """
        Validates that private admin contact details are strictly isolated
        and never leaked in client bundles or public notes.
        """
        restricted_patterns = [
            "ashokkumar2008313@gmail.com",
            "9597382878"
        ]

        target_files = [
            os.path.join(self.base_dir, "src", "pages", "next-gen.astro"),
            os.path.join(self.base_dir, "src", "components", "NextGenInnovationHub.jsx"),
            os.path.join(self.base_dir, "src", "components", "Topbar.astro"),
            os.path.join(self.base_dir, "backend", "next_gen_agent_engine.py"),
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

