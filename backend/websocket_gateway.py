"""
========================================================================================
VoltCore Apex Academia - Real-Time Server-Sent Events (SSE) Telemetry Gateway
Core Engineering Series • Autonomous Engineering Cluster Standards
----------------------------------------------------------------------------------------
Module: backend/websocket_gateway.py
Platform Lead / Architect: Ashok Kumar A
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Series: Core Engineering Series • Autonomous Engineering Cluster
Architecture:
  - Thread-Safe In-Memory Server-Sent Events (SSE) & WebSocket Telemetry Broker
  - Real-Time Dispatches: Hardware GPIO/ADC/Timer Telemetry, Virtual Serial, Attendance, TinyML
  - Zero-Latency Sub-Millisecond Queue Fan-Out for Connected React Clients
========================================================================================
"""

import os
import sys
import time
import json
import queue
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Generator

# Ensure root and backend directories are in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Import Owner Metadata
try:
    from backend.security_auth import OWNER_METADATA, PUBLIC_CONTACT_METADATA
except ImportError:
    from security_auth import OWNER_METADATA, PUBLIC_CONTACT_METADATA


class TelemetryBroadcaster:
    """
    High-performance, lightweight in-memory Server-Sent Events (SSE) broker.
    Supports concurrent client subscriptions with automatic dead-client cleanup.
    """

    def __init__(self, max_client_queue_size: int = 64):
        self.max_client_queue_size = max_client_queue_size
        self._subscribers: List[queue.Queue] = []
        self._lock = threading.Lock()
        self._history: List[Dict[str, Any]] = []
        self._max_history = 100

    def subscribe(self) -> queue.Queue:
        """Register a new client listener queue."""
        q = queue.Queue(maxsize=self.max_client_queue_size)
        with self._lock:
            self._subscribers.append(q)
        return q

    def unsubscribe(self, q: queue.Queue) -> None:
        """Unregister a client listener queue."""
        with self._lock:
            if q in self._subscribers:
                self._subscribers.remove(q)

    def broadcast(self, event_type: str, data: Dict[str, Any]) -> int:
        """
        Broadcast a structured telemetry event to all currently connected listeners.
        Returns the number of active clients who received the message.
        """
        payload = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "VoltCore_Telemetry_Gateway"
        }

        # Store in rolling audit history
        with self._lock:
            self._history.append(payload)
            if len(self._history) > self._max_history:
                self._history.pop(0)

            active_count = 0
            dead_queues = []

            for q in self._subscribers:
                try:
                    q.put_nowait(payload)
                    active_count += 1
                except queue.Full:
                    # Client buffer backlogged, mark for removal
                    dead_queues.append(q)

            for dead_q in dead_queues:
                self._subscribers.remove(dead_q)

        return active_count

    def emit_attendance_scan(
        self,
        node_id: str,
        student_id: str,
        student_name: str,
        rfid_uid: str,
        status: str = "Lab-Verified",
        rssi: Optional[int] = -54
    ) -> int:
        """Broadcast an ESP32 RFID card swipe event."""
        return self.broadcast("attendance_scan", {
            "node_id": node_id,
            "student_id": student_id,
            "student_name": student_name,
            "rfid_uid": rfid_uid,
            "status": status,
            "rssi": rssi,
            "campus": "Autonomous Engineering Cluster"
        })

    def emit_hardware_telemetry(
        self,
        board_id: str,
        gpio_states: Dict[str, Any],
        adc_readings: Dict[str, Any],
        timer_registers: Dict[str, Any],
        status: str = "RUNNING",
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Broadcast live simulated hardware telemetry (GPIO pin levels, ADC voltages, timer registers).
        Used by virtual hardware boards (ESP32-WROOM-32, STM32F401, STM32F103) and Wokwi Bridges.
        """
        return self.broadcast("hardware_telemetry", {
            "board_id": board_id,
            "gpio_states": gpio_states,
            "adc_readings": adc_readings,
            "timer_registers": timer_registers,
            "status": status,
            "metadata": metadata or {}
        })

    def emit_virtual_serial(
        self,
        board_id: str,
        payload_text: str,
        baud_rate: int = 115200,
        direction: str = "TX"
    ) -> int:
        """
        Broadcast bidirectional virtual serial UART packets between simulator, lesson reader, and client.
        """
        return self.broadcast("virtual_serial", {
            "board_id": board_id,
            "payload_text": payload_text,
            "baud_rate": baud_rate,
            "direction": direction,
            "char_count": len(payload_text)
        })

    def persist_hardware_telemetry_to_db(
        self,
        db_path: str,
        board_id: str,
        payload: Dict[str, Any],
        student_id: str = "ENG-2024-042",
        course_code: str = "EC8702"
    ) -> Dict[str, Any]:
        """
        Thread-safe persistence of live hardware telemetry into SQLite WAL gradebook.
        Uses busy_timeout = 5000 to prevent database lock contention under multi-write bursts.
        """
        obs_id = f"OBS-HIL-{board_id}-{datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}"
        now = datetime.now().isoformat()

        conn = sqlite3.connect(db_path, timeout=5.0)
        try:
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA busy_timeout = 5000;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS course_lab_observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    observation_id TEXT UNIQUE NOT NULL,
                    course_code TEXT NOT NULL,
                    lab_id TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    telemetry_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)
            conn.execute("""
                INSERT INTO course_lab_observations
                (observation_id, course_code, lab_id, student_id, telemetry_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                obs_id,
                course_code,
                f"HIL_{board_id}",
                student_id,
                json.dumps(payload),
                now
            ))
            conn.commit()
            return {"status": "success", "observation_id": obs_id, "persisted_at": now}
        finally:
            conn.close()

    def emit_xp_gain(
        self,
        student_id: str,
        student_name: str,
        xp_amount: int,
        reason: str,
        multiplier: str = "2.5x"
    ) -> int:
        """Broadcast a student XP reward event."""
        return self.broadcast("xp_gain", {
            "student_id": student_id,
            "student_name": student_name,
            "xp_amount": xp_amount,
            "reason": reason,
            "multiplier": multiplier
        })

    def emit_fleet_heartbeat(
        self,
        node_id: str,
        status: str,
        rssi: int,
        spool_depth: int,
        ip: str = "10.0.2.14"
    ) -> int:
        """Broadcast an IoT fleet node heartbeat."""
        return self.broadcast("fleet_heartbeat", {
            "node_id": node_id,
            "status": status,
            "rssi": rssi,
            "spool_depth": spool_depth,
            "ip_address": ip
        })

    def emit_tinyml_anomaly(
        self,
        node_id: str,
        anomaly_type: str,
        confidence: float,
        vibration_rms: float,
        temperature_c: float
    ) -> int:
        """Broadcast a TinyML Edge AI classified anomaly alert."""
        return self.broadcast("tinyml_anomaly", {
            "node_id": node_id,
            "anomaly_type": anomaly_type,
            "confidence_pct": round(confidence * 100, 1),
            "vibration_rms_g": round(vibration_rms, 3),
            "temperature_celsius": round(temperature_c, 1),
            "severity": "CRITICAL" if confidence >= 0.85 else "WARNING"
        })

    def stream_generator(self, timeout_seconds: float = 25.0) -> Generator[str, None, None]:
        """
        Yields Server-Sent Events (SSE) data chunks for Flask or WSGI response streams.
        Includes periodic keep-alive comments to prevent firewall timeouts.
        """
        q = self.subscribe()
        try:
            # Yield initial connection greeting
            connect_msg = {
                "event_type": "connected",
                "message": "VoltCore Live SSE Telemetry Connected",
                "platform": "VoltCore Apex Academia (Core Engineering Series)"
            }
            yield f"event: connect\ndata: {json.dumps(connect_msg)}\n\n"

            while True:
                try:
                    event = q.get(timeout=timeout_seconds)
                    event_type = event.get("event_type", "message")
                    data_json = json.dumps(event)
                    yield f"event: {event_type}\ndata: {data_json}\n\n"
                except queue.Empty:
                    # Keep-alive heartbeat ping
                    ping = {"ping": int(time.time()), "status": "ONLINE"}
                    yield f"event: ping\ndata: {json.dumps(ping)}\n\n"
        finally:
            self.unsubscribe(q)

    def get_recent_history(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Return recent broadcast events."""
        with self._lock:
            return list(self._history[-limit:])


# Global Telemetry Broker
telemetry_broker = TelemetryBroadcaster()


if __name__ == "__main__":
    print("=" * 80)
    print(" VoltCore Apex Academia - Real-Time SSE Telemetry Broker Self-Test")
    print(f" Platform Lead: {PUBLIC_CONTACT_METADATA['platform_lead']} ({PUBLIC_CONTACT_METADATA['public_email']})")
    print("=" * 80)

    # Test Subscription & Broadcast
    test_q = telemetry_broker.subscribe()

    count = telemetry_broker.emit_attendance_scan(
        node_id="ESP32_MIT_IOT_LAB_01",
        student_id="2023MITEC042",
        student_name="Ashok Kumar A",
        rfid_uid="E2 80 6F 3B"
    )
    assert count == 1
    received = test_q.get_nowait()
    assert received["event_type"] == "attendance_scan"
    assert received["data"]["student_id"] == "2023MITEC042"
    print(f"[1] Attendance Scan SSE Event Dispatched: [PASSED] -> {received['data']['student_name']}")

    # Test TinyML Anomaly Event
    count2 = telemetry_broker.emit_tinyml_anomaly(
        node_id="ESP32_MIT_EDGE_NODE_09",
        anomaly_type="BEARING_RACETRACK_FATIGUE",
        confidence=0.92,
        vibration_rms=4.82,
        temperature_c=68.5
    )
    assert count2 == 1
    received2 = test_q.get_nowait()
    assert received2["event_type"] == "tinyml_anomaly"
    assert received2["data"]["confidence_pct"] == 92.0
    print(f"[2] TinyML Anomaly Event Dispatched: [PASSED] -> {received2['data']['anomaly_type']} (92% Confidence)")

    # Test Hardware Telemetry Event
    count3 = telemetry_broker.emit_hardware_telemetry(
        board_id="ESP32_VOLTCORE_IOT_01",
        gpio_states={"GPIO0": 1, "GPIO2": 0, "GPIO4": 1, "GPIO34": 2048},
        adc_readings={"ADC1_CH6_V": 1.65},
        timer_registers={"TIM2_CNT": 4820, "TIM2_ARR": 10000}
    )
    assert count3 == 1
    received3 = test_q.get_nowait()
    assert received3["event_type"] == "hardware_telemetry"
    assert received3["data"]["board_id"] == "ESP32_VOLTCORE_IOT_01"
    assert received3["data"]["adc_readings"]["ADC1_CH6_V"] == 1.65
    print(f"[3] Hardware Telemetry Dispatched: [PASSED] -> {received3['data']['board_id']}")

    # Test Virtual Serial Event
    count4 = telemetry_broker.emit_virtual_serial(
        board_id="ESP32_VOLTCORE_IOT_01",
        payload_text="AT+STATUS\r\n"
    )
    assert count4 == 1
    received4 = test_q.get_nowait()
    assert received4["event_type"] == "virtual_serial"
    assert received4["data"]["payload_text"] == "AT+STATUS\r\n"
    print(f"[4] Virtual Serial Dispatched: [PASSED] -> {received4['data']['payload_text'].strip()}")

    telemetry_broker.unsubscribe(test_q)
    print("\n" + "=" * 80)
    print(" ALL SSE TELEMETRY BROKER TESTS PASSED.")
    print("=" * 80)
