"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 6 Hardware-in-the-Loop & Autograder Engine
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase6_hil_autograder.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import json
import unittest
from backend.autograder_engine import FirmwareAutograderEngine, firmware_autograder
from backend.circuit_syntax_parser import CircuitSyntaxParser


class TestPhase6HilAutograder(unittest.TestCase):
    """
    Validation suite for Phase 6 HIL Test Bench, AST Firmware Autograder,
    Wokwi Circuit Syntax ERC Parser, and Academic Privacy Constraints.
    """

    def setUp(self):
        self.grader = FirmwareAutograderEngine()
        self.circuit_parser = CircuitSyntaxParser()
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def test_firmware_autograder_clean_pass(self):
        """Firmware with optimal design patterns should achieve grade O or A+."""
        clean_code = """
        #include <Arduino.h>
        #include "freertos/FreeRTOS.h"
        #include "freertos/task.h"

        void taskSensor(void *pvParameters) {
            pinMode(18, OUTPUT);
            uint8_t *sample_buf = (uint8_t *)pvPortMalloc(256);
            if (sample_buf != NULL) {
                // Process samples
                vPortFree(sample_buf);
            }
            for (;;) {
                digitalWrite(18, HIGH);
                vTaskDelay(pdMS_TO_TICKS(100));
                digitalWrite(18, LOW);
                vTaskDelay(pdMS_TO_TICKS(100));
            }
        }
        """
        report = self.grader.grade_firmware_submission(clean_code, module_code="EC8701")
        self.assertEqual(report["status"], "success")
        self.assertTrue(report["passed"])
        self.assertGreaterEqual(report["total_score"], 90)
        self.assertIn(report["grade"], ["O", "A+"])
        self.assertEqual(len(report["deductions"]), 0)
        self.assertIn("Clean Heap Memory Balance: All dynamic allocations properly paired with free/vPortFree.", report["positive_credits"])

    def test_firmware_autograder_memory_leak(self):
        """Firmware with unbalanced dynamic allocations must incur memory safety penalty."""
        leaky_code = """
        void processTelemetry() {
            char *buf1 = (char *)malloc(512);
            char *buf2 = (char *)malloc(1024);
            // Only freeing one buffer
            free(buf1);
        }
        """
        report = self.grader.grade_firmware_submission(leaky_code)
        self.assertLess(report["category_scores"]["memory_safety"], 25)
        leak_deductions = [d for d in report["deductions"] if d["category"] == "memory_safety" and "Memory Leak" in d["issue"]]
        self.assertTrue(len(leak_deductions) > 0)
        self.assertEqual(leak_deductions[0]["severity"], "CRITICAL")

    def test_firmware_autograder_stack_overflow(self):
        """Firmware allocating >= 2048 bytes on the task stack must trigger stack hazard."""
        stack_heavy_code = """
        void dangerousStackFunction() {
            uint8_t buffer[4096];
            buffer[0] = 0xAA;
        }
        """
        report = self.grader.grade_firmware_submission(stack_heavy_code)
        stack_deductions = [d for d in report["deductions"] if "Stack Overflow" in d["issue"]]
        self.assertTrue(len(stack_deductions) > 0)
        self.assertEqual(stack_deductions[0]["penalty"], 10)

    def test_firmware_autograder_freertos_delay_penalty(self):
        """FreeRTOS firmware using blocking delay() instead of vTaskDelay must be penalized."""
        bad_rtos_code = """
        #include "freertos/FreeRTOS.h"
        #include "freertos/task.h"

        void vWorkerTask(void *pvParameters) {
            while(1) {
                xTaskCreate(vWorkerTask, "worker", 2048, NULL, 1, NULL);
                delay(100); // Blocking delay anti-pattern
            }
        }
        """
        report = self.grader.grade_firmware_submission(bad_rtos_code)
        rtos_deductions = [d for d in report["deductions"] if d["category"] == "concurrency_rtos"]
        self.assertTrue(len(rtos_deductions) > 0)
        self.assertIn("FreeRTOS CPU Starvation", rtos_deductions[0]["issue"])

    def test_firmware_autograder_dma_barrier(self):
        """DMA drivers in advanced modules require __DMB or __DSB memory barriers."""
        no_barrier_dma = """
        void init_dma_transfer() {
            uint32_t *dma_desc = get_desc();
            dma_desc->buffer = tx_buffer;
            enable_DMA_stream();
        }
        """
        report = self.grader.grade_firmware_submission(no_barrier_dma, module_code="EC8708")
        dmb_deductions = [d for d in report["deductions"] if "Missing Memory Barrier" in d["issue"]]
        self.assertTrue(len(dmb_deductions) > 0)

        barrier_dma = """
        void init_dma_transfer() {
            uint32_t *dma_desc = get_desc();
            dma_desc->buffer = tx_buffer;
            __DMB();
            enable_DMA_stream();
        }
        """
        pass_report = self.grader.grade_firmware_submission(barrier_dma, module_code="EC8708")
        self.assertTrue(any("Data Memory Barrier" in c for c in pass_report["positive_credits"]))

    def test_firmware_autograder_input_only_pin_mode(self):
        """Configuring GPIO 34, 35, 36, or 39 as OUTPUT on ESP32 must fail validation."""
        bad_pin_code = """
        void setup() {
            pinMode(34, OUTPUT);
            pinMode(35, OUTPUT);
        }
        """
        report = self.grader.grade_firmware_submission(bad_pin_code)
        pin_deductions = [d for d in report["deductions"] if d["category"] == "hardware_pins"]
        self.assertTrue(len(pin_deductions) >= 1)
        self.assertIn("input-only", pin_deductions[0]["issue"])

    def test_firmware_autograder_adc2_wifi_contention(self):
        """Reading ADC2 pins while Wi-Fi is initialized triggers contention warning."""
        contention_code = """
        #include <WiFi.h>
        void readSensors() {
            WiFi.begin("SSID", "PASS");
            int val = analogRead(4); // GPIO 4 is ADC2 channel 0
        }
        """
        report = self.grader.grade_firmware_submission(contention_code)
        adc_deductions = [d for d in report["deductions"] if "ADC2 / Wi-Fi Contention" in d["issue"]]
        self.assertTrue(len(adc_deductions) > 0)

    def test_circuit_parser_valid_diagram(self):
        """A valid Wokwi diagram with correct LED and resistor wiring passes ERC."""
        diagram = {
            "version": 1,
            "parts": [
                {"type": "board-esp32-devkit-c-v4", "id": "esp"},
                {"type": "wokwi-led", "id": "led1", "attrs": {"color": "emerald"}},
                {"type": "wokwi-resistor", "id": "r1", "attrs": {"resistance": "220"}}
            ],
            "connections": [
                ["esp:18", "r1:1", "green", []],
                ["r1:2", "led1:anode", "green", []],
                ["led1:cathode", "esp:GND", "black", []]
            ]
        }
        res = self.circuit_parser.parse_wokwi_diagram(json.dumps(diagram))
        self.assertTrue(res["valid"])
        self.assertEqual(res["score"], 100)
        self.assertEqual(len(res["errors"]), 0)

    def test_circuit_parser_short_circuit_detection(self):
        """Direct connection between power and ground pins must fail with critical short."""
        diagram = {
            "version": 1,
            "parts": [{"type": "board-esp32-devkit-c-v4", "id": "esp"}],
            "connections": [
                ["esp:3V3", "esp:GND", "red", []]
            ]
        }
        res = self.circuit_parser.parse_wokwi_diagram(json.dumps(diagram))
        self.assertFalse(res["valid"])
        self.assertTrue(any("SHORT CIRCUIT" in err for err in res["errors"]))

    def test_circuit_parser_input_only_actuator_drive(self):
        """Connecting ESP32 input-only GPIO (e.g. 34) directly to an actuator must fail."""
        diagram = {
            "version": 1,
            "parts": [
                {"type": "board-esp32-devkit-c-v4", "id": "esp"},
                {"type": "wokwi-led", "id": "led1"}
            ],
            "connections": [
                ["esp:34", "led1:anode", "blue", []],
                ["led1:cathode", "esp:GND", "black", []]
            ]
        }
        res = self.circuit_parser.parse_wokwi_diagram(json.dumps(diagram))
        self.assertFalse(res["valid"])
        self.assertTrue(any("PIN MISMATCH" in err for err in res["errors"]))

    def test_circuit_parser_i2c_missing_pullup_warning(self):
        """Connecting an I2C device without pull-up resistors triggers a warning."""
        diagram = {
            "version": 1,
            "parts": [
                {"type": "board-esp32-devkit-c-v4", "id": "esp"},
                {"type": "wokwi-mpu6050", "id": "imu1"}
            ],
            "connections": [
                ["esp:21", "imu1:SDA", "green", []],
                ["esp:22", "imu1:SCL", "yellow", []]
            ]
        }
        res = self.circuit_parser.parse_wokwi_diagram(json.dumps(diagram))
        self.assertTrue(res["valid"])  # Warnings don't fail validation
        self.assertTrue(any("I2C BUS INTEGRITY" in w for w in res["warnings"]))
        self.assertLess(res["score"], 100)

    def test_circuit_parser_malformed_json(self):
        """Malformed JSON must return structured validation error."""
        res = self.circuit_parser.parse_wokwi_diagram("{ invalid json ...")
        self.assertFalse(res["valid"])
        self.assertEqual(res["score"], 0)
        self.assertIn("Malformed JSON", res["errors"][0])

    def test_phase6_files_exist(self):
        """All Phase 6 components, pages, and curriculum modules must exist."""
        required_files = [
            "src/components/HwTestBenchLive.jsx",
            "src/pages/hardware-hil.astro",
            "backend/autograder_engine.py",
            "backend/circuit_syntax_parser.py",
            "src/content/modules/advanced-ece/10-gate-ece-instrumentation.mdx",
            "src/components/GateEceInteractiveSolvers.jsx"
        ]
        for rel_path in required_files:
            full_path = os.path.join(self.base_dir, rel_path)
            self.assertTrue(os.path.isfile(full_path), f"Phase 6 file missing: {rel_path}")

    def test_hardware_test_bench_assertions_present(self):
        """Verify HwTestBenchLive.jsx contains all 5 required HIL assertion routines."""
        path = os.path.join(self.base_dir, "src/components/HwTestBenchLive.jsx")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        required_keywords = [
            "Loopback",
            "ADC1 ENOB",
            "I2C Bus Stress",
            "LittleFS Flash Page",
            "FreeRTOS ISR-to-Task",
            "WebSerial",
            "navigator.serial",
            "handleCommitToLedger"
        ]
        for kw in required_keywords:
            self.assertIn(kw, content, f"Keyword '{kw}' missing from HwTestBenchLive.jsx")

    def test_gate_solvers_logic_present(self):
        """Verify GateEceInteractiveSolvers.jsx has K-Map, Bode, and 8051/ARM interpreters."""
        path = os.path.join(self.base_dir, "src/components/GateEceInteractiveSolvers.jsx")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        required_solver_features = [
            "Gray code",
            "canvasRef",
            "Gain Margin",
            "Phase Margin",
            "LDR R0,",
            "handleStepNext",
            "handleStepReset"
        ]
        for sf in required_solver_features:
            self.assertIn(sf, content, f"Feature '{sf}' missing from GateEceInteractiveSolvers.jsx")

    def test_security_privacy_invariants(self):
        """Ensure private admin phone and email are never in public client bundles."""
        restricted_phone = "9597382878"
        restricted_email = "ashokkumar2008313@gmail.com"

        public_scan_dirs = [
            os.path.join(self.base_dir, "src", "components"),
            os.path.join(self.base_dir, "src", "pages"),
            os.path.join(self.base_dir, "src", "content")
        ]

        for scan_dir in public_scan_dirs:
            for root, _, files in os.walk(scan_dir):
                for file in files:
                    if file.endswith((".jsx", ".astro", ".md", ".mdx", ".json", ".js")):
                        full_path = os.path.join(root, file)
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            text = f.read()
                            self.assertNotIn(
                                restricted_phone,
                                text,
                                f"Restricted admin phone leaked in public file: {full_path}"
                            )
                            self.assertNotIn(
                                restricted_email,
                                text,
                                f"Restricted admin email leaked in public file: {full_path}"
                            )


if __name__ == "__main__":
    unittest.main()
