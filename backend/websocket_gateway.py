"""
========================================================================================
VoltCore Apex Academia - Real-Time Server-Sent Events (SSE) Telemetry Gateway
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/websocket_gateway.py
Platform Lead / Architect: Ashok Kumar A
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
Architecture:
  - Thread-Safe In-Memory Server-Sent Events (SSE) & WebSocket Telemetry Broker
  - Real-Time Dispatches: Attendance Scans, XP Multipliers, Fleet Heartbeats, TinyML Alerts
  - Zero-Latency Sub-Millisecond Queue Fan-Out for Connected React Clients
========================================================================================
"""

import os
import sys
import time
import json
import queue
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
            "campus": "MIT Campus, Anna University"
        })

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
                "platform": "VoltCore Apex Academia (MIT Campus Anna University)"
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

    telemetry_broker.unsubscribe(test_q)
    print("\n" + "=" * 80)
    print(" ALL SSE TELEMETRY BROKER TESTS PASSED.")
    print("=" * 80)
