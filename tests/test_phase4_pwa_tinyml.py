"""
========================================================================================
VoltCore Apex Academia - Phase 4 Automated Test Suite
PWA Offline Architecture, SSE Telemetry Broadcaster & TinyML Quantization Verification
----------------------------------------------------------------------------------------
Module: tests/test_phase4_pwa_tinyml.py
Platform Lead / System Architect: Ashok Kumar A
Academic Institution: Madras Institute of Technology (MIT) Campus, Anna University
========================================================================================
"""

import os
import sys
import json
import math
import unittest
from datetime import datetime

# Setup project root in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import lms_database
from backend.websocket_gateway import TelemetryBroadcaster, telemetry_broker
import attendance_server


class TestPWAOfflineArchitecture(unittest.TestCase):
    """Verifies PWA manifest and service worker configuration."""

    def test_pwa_manifest_json_structure(self):
        manifest_path = os.path.join(PROJECT_ROOT, "public", "manifest.json")
        self.assertTrue(os.path.exists(manifest_path), "public/manifest.json must exist")

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        self.assertIn("name", manifest)
        self.assertIn("VoltCore Apex Academia", manifest["name"])
        self.assertIn("MIT Campus", manifest["description"])
        self.assertEqual(manifest["theme_color"], "#00693E")
        self.assertEqual(manifest["background_color"], "#020813")
        self.assertEqual(manifest["display"], "standalone")
        self.assertEqual(manifest["start_url"], "/")
        self.assertGreaterEqual(len(manifest.get("icons", [])), 2)
        self.assertGreaterEqual(len(manifest.get("shortcuts", [])), 2)

    def test_service_worker_caching_strategies(self):
        sw_path = os.path.join(PROJECT_ROOT, "public", "service-worker.js")
        self.assertTrue(os.path.exists(sw_path), "public/service-worker.js must exist")

        with open(sw_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Cache strategies checks
        self.assertIn("CACHE_NAME", content)
        self.assertIn("voltcore-apex", content)
        self.assertIn("CacheFirst", content)
        self.assertIn("NetworkFirst", content)
        self.assertIn("offline_spooled", content)
        self.assertIn("/api/", content)
        self.assertIn("skipWaiting", content)
        self.assertIn("PRECACHE_ASSETS", content)


class TestSSETelemetryBroadcaster(unittest.TestCase):
    """Verifies thread-safe real-time telemetry fan-out and queue operations."""

    def setUp(self):
        self.broadcaster = TelemetryBroadcaster(max_client_queue_size=16)

    def test_client_subscription_and_broadcast(self):
        client_q = self.broadcaster.subscribe()
        self.assertEqual(len(self.broadcaster._subscribers), 1)

        active = self.broadcaster.broadcast("test_ping", {"status": "ACTIVE_NODE", "node": "ESP32_01"})
        self.assertEqual(active, 1)

        msg = client_q.get_nowait()
        self.assertEqual(msg["event_type"], "test_ping")
        self.assertEqual(msg["data"]["node"], "ESP32_01")
        self.assertEqual(msg["source"], "VoltCore_Telemetry_Gateway")

        self.broadcaster.unsubscribe(client_q)
        self.assertEqual(len(self.broadcaster._subscribers), 0)

    def test_emit_convenience_methods(self):
        q = self.broadcaster.subscribe()

        # Attendance Scan
        self.broadcaster.emit_attendance_scan(
            node_id="ESP32_MIT_01",
            student_id="2023MITEC042",
            student_name="Ashok Kumar A",
            rfid_uid="E2 80 6F 3B"
        )
        msg1 = q.get_nowait()
        self.assertEqual(msg1["event_type"], "attendance_scan")
        self.assertEqual(msg1["data"]["student_id"], "2023MITEC042")

        # XP Gain
        self.broadcaster.emit_xp_gain(
            student_id="2023MITEC042",
            student_name="Ashok Kumar A",
            xp_amount=50,
            reason="RFID Scan Check-in",
            multiplier="2.5x"
        )
        msg2 = q.get_nowait()
        self.assertEqual(msg2["event_type"], "xp_gain")
        self.assertEqual(msg2["data"]["xp_amount"], 50)

        # Fleet Heartbeat
        self.broadcaster.emit_fleet_heartbeat(
            node_id="ESP32_NODE_02",
            status="ACTIVE_ONLINE",
            rssi=-58,
            spool_depth=2
        )
        msg3 = q.get_nowait()
        self.assertEqual(msg3["event_type"], "fleet_heartbeat")
        self.assertEqual(msg3["data"]["rssi"], -58)

        # TinyML Anomaly
        self.broadcaster.emit_tinyml_anomaly(
            node_id="ESP32_NODE_09",
            anomaly_type="BEARING_FATIGUE",
            confidence=0.94,
            vibration_rms=4.82,
            temperature_c=68.5
        )
        msg4 = q.get_nowait()
        self.assertEqual(msg4["event_type"], "tinyml_anomaly")
        self.assertEqual(msg4["data"]["severity"], "CRITICAL")
        self.assertEqual(msg4["data"]["confidence_pct"], 94.0)

        self.broadcaster.unsubscribe(q)

    def test_dead_client_cleanup_on_buffer_full(self):
        small_broker = TelemetryBroadcaster(max_client_queue_size=2)
        q1 = small_broker.subscribe()

        # Fill buffer past capacity (2 items)
        small_broker.broadcast("ping_1", {"v": 1})
        small_broker.broadcast("ping_2", {"v": 2})
        # 3rd broadcast should drop dead queue
        small_broker.broadcast("ping_3", {"v": 3})

        self.assertNotIn(q1, small_broker._subscribers)

    def test_rolling_history_retention(self):
        for i in range(120):
            self.broadcaster.broadcast("item", {"index": i})

        history = self.broadcaster.get_recent_history(limit=25)
        self.assertEqual(len(history), 25)
        self.assertEqual(history[-1]["data"]["index"], 119)


class TestTinyMLQuantizationAndMath(unittest.TestCase):
    """Verifies affine INT8 quantization formulas, FFT resolution, and saturation arithmetic."""

    def test_asymmetric_affine_quantization_formula(self):
        # Real range [alpha, beta] = [-1.0, 3.0]
        alpha = -1.0
        beta = 3.0
        q_min = -128
        q_max = 127

        # Scale S = (beta - alpha) / 255
        S = (beta - alpha) / 255.0
        # Zero-point Z = round(-alpha / S) + q_min
        Z = round(-alpha / S) + q_min

        # Quantization function: q = clamp(round(r / S) + Z, -128, 127)
        def quantize(r):
            q_val = round(r / S) + Z
            return max(q_min, min(q_max, q_val))

        def dequantize(q):
            return S * (q - Z)

        # Real zero must map exactly to Z with zero quantization shift
        q_zero = quantize(0.0)
        self.assertEqual(q_zero, Z)
        r_rec_zero = dequantize(q_zero)
        self.assertAlmostEqual(r_rec_zero, 0.0, places=4)

        # Max real value beta must map to q_max (127)
        q_beta = quantize(beta)
        self.assertEqual(q_beta, q_max)

        # Min real value alpha must map to q_min (-128)
        q_alpha = quantize(alpha)
        self.assertEqual(q_alpha, q_min)

        # Arbitrary real test: 1.5
        q_mid = quantize(1.5)
        r_mid = dequantize(q_mid)
        self.assertLess(abs(r_mid - 1.5), S)

    def test_fft_frequency_bin_resolution(self):
        # ADXL345 sampled at Fs = 1000 Hz with N = 64
        Fs = 1000.0
        N = 64
        delta_f = Fs / N
        self.assertEqual(delta_f, 15.625)

        # Check bin for 240 Hz bearing resonance
        target_f = 240.0
        bin_idx = target_f / delta_f
        self.assertAlmostEqual(bin_idx, 15.36, places=2)

    def test_32bit_accumulator_prevents_16bit_overflow(self):
        # Simulating worst-case K = 64 inputs where each (q_x - Z_x) * (q_w - Z_w) = 255 * 255 = 65025
        K = 64
        worst_case_elem = 255 * 255
        total_sum = K * worst_case_elem # 4,161,600

        # Verify int16_t (max 32767) would overflow
        self.assertGreater(total_sum, 32767)

        # Verify int32_t (max 2,147,483,647) handles it with ample headroom
        self.assertLess(total_sum, 2147483647)


class TestAttendanceServerTelemetryIntegration(unittest.TestCase):
    """Verifies attendance server telemetry endpoints and fan-out integration."""

    @classmethod
    def setUpClass(cls):
        lms_database.init_db()
        lms_database.seed_mit_campus_data()

    def test_process_attendance_scan_dispatches_sse(self):
        test_q = telemetry_broker.subscribe()

        scan_payload = {
            "node_id": "ESP32_MIT_TEST_LAB",
            "student_id": "2023MITEC042",
            "rfid_uid": "E2 80 6F 3B",
            "rssi": -55
        }
        resp, code = attendance_server.process_attendance_scan(scan_payload)
        self.assertEqual(code, 200)
        self.assertEqual(resp["status"], "success")

        # Telemetry broker should receive attendance_scan and xp_gain
        events_received = []
        while not test_q.empty():
            events_received.append(test_q.get_nowait())

        event_types = [e["event_type"] for e in events_received]
        self.assertIn("attendance_scan", event_types)
        self.assertIn("xp_gain", event_types)

        telemetry_broker.unsubscribe(test_q)

    def test_telemetry_history_contains_recent_events(self):
        history = telemetry_broker.get_recent_history(limit=10)
        self.assertIsInstance(history, list)
        self.assertGreaterEqual(len(history), 1)


if __name__ == "__main__":
    unittest.main()
