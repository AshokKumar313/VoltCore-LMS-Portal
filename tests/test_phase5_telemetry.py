"""
========================================================================================
VoltCore Apex Academia - Phase 5 Telemetry Streaming & Hardware Bridge Testbed
Core Engineering Series • Autonomous Engineering Cluster
Platform Lead & Systems Architect: Ashok Kumar A
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313

Validates:
  1. Real-time SSE / WebSockets TelemetryBroadcaster fan-out and subscription resilience
  2. Live simulated hardware telemetry (GPIO, ADC, Timer registers) event structuring
  3. Bidirectional virtual serial UART packet streaming between simulator and lesson reader
  4. SSE wire format compliance (event: connect, event: hardware_telemetry, event: ping)
  5. High-speed telemetry persistence into SQLite WAL mode (busy_timeout = 5000)
  6. HTTP REST endpoints (/api/telemetry/hardware, /api/telemetry/serial/transmit)
  7. Component cleanliness (zero institutional markers, zero polling daemons)
  8. Laptop thermal safety: execution runtime < 500ms on HP Victus development laptop
========================================================================================
"""

import os
import io
import re
import json
import time
import queue
import sqlite3
import tempfile
import threading
import urllib.request
from http.server import HTTPServer
import pytest

from backend.websocket_gateway import TelemetryBroadcaster, telemetry_broker
import attendance_server


def test_telemetry_broadcaster_subscription_and_fanout():
    """Verify thread-safe subscription and fan-out to multiple concurrent listeners."""
    broadcaster = TelemetryBroadcaster(max_client_queue_size=16)
    q1 = broadcaster.subscribe()
    q2 = broadcaster.subscribe()
    q3 = broadcaster.subscribe()

    count = broadcaster.broadcast("test_probe", {"key": "probe_val_99"})
    assert count == 3, f"Expected 3 active listeners, got {count}"

    for q in [q1, q2, q3]:
        msg = q.get_nowait()
        assert msg["event_type"] == "test_probe"
        assert msg["data"]["key"] == "probe_val_99"
        assert "timestamp" in msg

    broadcaster.unsubscribe(q1)
    broadcaster.unsubscribe(q2)
    broadcaster.unsubscribe(q3)
    assert len(broadcaster._subscribers) == 0


def test_hardware_telemetry_broadcast_and_payload_structure():
    """Verify live simulated GPIO, ADC, and Timer register telemetry dispatches."""
    test_q = telemetry_broker.subscribe()

    try:
        gpio_data = {"PA5": 1, "PC13": 0, "GPIO34": 2048}
        adc_data = {"ADC1_IN0_V": 2.45, "ADC1_CH6_V": 1.65}
        timer_data = {"TIM2_CNT": 1200, "TIM2_ARR": 5000}

        count = telemetry_broker.emit_hardware_telemetry(
            board_id="STM32F401RE_NUCLEO",
            gpio_states=gpio_data,
            adc_readings=adc_data,
            timer_registers=timer_data,
            status="RUNNING",
            metadata={"clock_mhz": 84.0}
        )
        assert count >= 1

        rec = test_q.get_nowait()
        assert rec["event_type"] == "hardware_telemetry"
        data = rec["data"]
        assert data["board_id"] == "STM32F401RE_NUCLEO"
        assert data["gpio_states"]["PA5"] == 1
        assert data["adc_readings"]["ADC1_IN0_V"] == 2.45
        assert data["timer_registers"]["TIM2_CNT"] == 1200
        assert data["status"] == "RUNNING"
        assert data["metadata"]["clock_mhz"] == 84.0

    finally:
        telemetry_broker.unsubscribe(test_q)


def test_virtual_serial_transmission_and_direction():
    """Verify virtual serial UART packet streaming between lesson reader and simulator."""
    test_q = telemetry_broker.subscribe()

    try:
        count = telemetry_broker.emit_virtual_serial(
            board_id="ESP32_VOLTCORE_IOT_01",
            payload_text="AT+RST\r\n",
            baud_rate=115200,
            direction="TX"
        )
        assert count >= 1

        rec = test_q.get_nowait()
        assert rec["event_type"] == "virtual_serial"
        data = rec["data"]
        assert data["board_id"] == "ESP32_VOLTCORE_IOT_01"
        assert data["payload_text"] == "AT+RST\r\n"
        assert data["baud_rate"] == 115200
        assert data["direction"] == "TX"
        assert data["char_count"] == 8

    finally:
        telemetry_broker.unsubscribe(test_q)


def test_stream_generator_sse_wire_format():
    """Verify Server-Sent Events (SSE) generator produces valid event-stream formatting."""
    broadcaster = TelemetryBroadcaster(max_client_queue_size=8)
    gen = broadcaster.stream_generator(timeout_seconds=0.05)

    # First chunk is the connect handshake
    chunk1 = next(gen)
    assert chunk1.startswith("event: connect\ndata: ")
    assert "VoltCore Live SSE Telemetry Connected" in chunk1

    # Emit an event into the stream
    broadcaster.emit_virtual_serial(
        board_id="NUCLEO_F401",
        payload_text="PING\n"
    )

    chunk2 = next(gen)
    assert chunk2.startswith("event: virtual_serial\ndata: ")
    assert "PING" in chunk2


def test_hardware_telemetry_sqlite_wal_persistence():
    """Verify rapid persistent logging of hardware telemetry into SQLite WAL mode."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        temp_db_path = tf.name

    try:
        broadcaster = TelemetryBroadcaster()

        # Simulate 10 rapid telemetry writes
        for i in range(10):
            res = broadcaster.persist_hardware_telemetry_to_db(
                db_path=temp_db_path,
                board_id="STM32F401RE_NUCLEO",
                payload={"sample": i, "adc_raw": 1000 + i, "status": "ACTIVE"}
            )
            assert res["status"] == "success"
            assert "OBS-HIL-" in res["observation_id"]

        # Verify journal mode and row count
        conn = sqlite3.connect(temp_db_path)
        cur = conn.cursor()
        mode = cur.execute("PRAGMA journal_mode;").fetchone()[0]
        assert mode.lower() == "wal"

        count = cur.execute("SELECT COUNT(*) FROM course_lab_observations;").fetchone()[0]
        assert count == 10

        first_row = cur.execute("SELECT telemetry_json FROM course_lab_observations ORDER BY id ASC LIMIT 1;").fetchone()[0]
        parsed = json.loads(first_row)
        assert parsed["sample"] == 0
        assert parsed["adc_raw"] == 1000
        conn.close()

    finally:
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)


class MockHTTPConnection:
    """In-memory mock HTTP transport allowing complete HTTP protocol testing with 0 network sockets."""
    def __init__(self, request_bytes: bytes):
        self.rfile = io.BytesIO(request_bytes)
        self.wfile = io.BytesIO()

    def makefile(self, mode, *args, **kwargs):
        if "r" in mode:
            return self.rfile
        return self.wfile

    def sendall(self, b: bytes):
        self.wfile.write(b)


class DummyServer:
    pass


def execute_mock_http_request(method: str, path: str, payload: dict = None) -> tuple[int, dict]:
    """Helper to dispatch HTTP requests in-memory through attendance_server handlers."""
    if attendance_server.HAS_FLASK:
        client = attendance_server.app.test_client()
        if method == "POST":
            resp = client.post(path, data=json.dumps(payload or {}), content_type="application/json")
        else:
            resp = client.get(path)
        return resp.status_code, json.loads(resp.data.decode("utf-8"))

    # In-memory execution using FallbackHTTPHandler
    raw_payload = json.dumps(payload or {}).encode("utf-8") if payload else b""
    headers = [
        f"{method} {path} HTTP/1.1",
        "Host: localhost",
        "Content-Type: application/json",
        f"Content-Length: {len(raw_payload)}"
    ]
    raw_req = "\r\n".join(headers).encode("ascii") + b"\r\n\r\n" + raw_payload

    conn = MockHTTPConnection(raw_req)
    attendance_server.FallbackHTTPHandler(conn, ("127.0.0.1", 54321), DummyServer())

    raw_resp = conn.wfile.getvalue().decode("utf-8")
    status_line = raw_resp.split("\r\n")[0]
    status_code = int(status_line.split(" ")[1])
    body_str = raw_resp.split("\r\n\r\n")[-1]
    return status_code, json.loads(body_str)


def test_hardware_telemetry_http_endpoints():
    """Verify server hardware telemetry and virtual serial REST endpoints across Flask or Fallback handler."""
    # 1. POST /api/telemetry/hardware
    hw_payload = {
        "board_id": "STM32F401_BOARD",
        "gpio_states": {"PB0": 1, "PB7": 0},
        "adc_readings": {"ADC1_CH0": 3.12},
        "timer_registers": {"TIM1_CNT": 990},
        "status": "RUNNING",
        "metadata": {"compiler": "arm-none-eabi-gcc"}
    }
    status_code, hw_res = execute_mock_http_request("POST", "/api/telemetry/hardware", hw_payload)
    assert status_code == 200
    assert hw_res["status"] == "hardware_telemetry_dispatched"
    assert hw_res["board_id"] == "STM32F401_BOARD"

    # 2. GET /api/telemetry/hardware
    status_code_get, get_res = execute_mock_http_request("GET", "/api/telemetry/hardware")
    assert status_code_get == 200
    assert get_res["status"] == "success"
    assert get_res["count"] >= 1

    # 3. POST /api/telemetry/serial/transmit
    serial_payload = {
        "board_id": "STM32F401_BOARD",
        "text": "AT+STATUS\r\n",
        "baud_rate": 115200,
        "direction": "TX"
    }
    status_code_ser, ser_res = execute_mock_http_request("POST", "/api/telemetry/serial/transmit", serial_payload)
    assert status_code_ser == 200
    assert ser_res["status"] == "serial_packet_streamed"
    assert ser_res["char_count"] == len("AT+STATUS\r\n")


def test_component_files_clean_and_event_wired():
    """Verify front-end components have proper stream event wiring and zero institutional markers."""
    files_to_check = [
        os.path.join("src", "components", "SystemStatusWidget.jsx"),
        os.path.join("src", "components", "WokwiSimulationController.jsx"),
        os.path.join("src", "components", "WebUsbFlashingPanel.jsx"),
        os.path.join("src", "components", "CourseLessonReader.jsx"),
        os.path.join("src", "components", "WokwiSandbox.astro")
    ]

    forbidden_patterns = [
        r"Anna\s+University",
        r"MIT\s+Campus",
        r"Regulation\s+2023",
        r"2023MITEC042"
    ]

    for fpath in files_to_check:
        assert os.path.exists(fpath), f"File missing: {fpath}"
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        for pattern in forbidden_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            assert len(matches) == 0, f"Forbidden institutional marker '{pattern}' in {fpath}: {matches}"

    # Specific functional assertions:
    # 1. SystemStatusWidget consumes SSE stream without polling
    with open(files_to_check[0], "r", encoding="utf-8") as f:
        ssw = f.read()
    assert "/api/telemetry/stream" in ssw
    assert "setInterval" not in ssw, "SystemStatusWidget must not use setInterval continuous polling"

    # 2. WokwiSimulationController supports live stream and serial transmission
    with open(files_to_check[1], "r", encoding="utf-8") as f:
        wsc = f.read()
    assert "/api/telemetry/stream" in wsc
    assert "handleSendSerialCommand" in wsc
    assert "voltcore:lesson-transmit" in wsc

    # 3. WebUsbFlashingPanel handles STM32 Nucleo and Blue Pill error handling
    with open(files_to_check[2], "r", encoding="utf-8") as f:
        flasher = f.read()
    assert "stm32_nucleo_f401" in flasher
    assert "stm32_bluepill_f103" in flasher
    assert "NotFoundError" in flasher
    assert "SecurityError" in flasher

    # 4. CourseLessonReader transmits stimulus
    with open(files_to_check[3], "r", encoding="utf-8") as f:
        clr = f.read()
    assert "handleTransmitStimulus" in clr
    assert "voltcore:lesson-transmit" in clr


def test_phase5_thermal_safety_execution_time():
    """Verify test performance maintains passive CPU profile (<500ms runtime)."""
    start = time.perf_counter()

    # Fast validation of broadcaster subscription and release
    b = TelemetryBroadcaster()
    q = b.subscribe()
    b.emit_hardware_telemetry(
        board_id="BENCHMARK_BOARD",
        gpio_states={"PIN0": 1},
        adc_readings={"ADC": 1.0},
        timer_registers={"TIM": 100}
    )
    msg = q.get_nowait()
    assert msg["data"]["board_id"] == "BENCHMARK_BOARD"
    b.unsubscribe(q)

    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 500, f"Broadcaster test exceeded 500ms: {elapsed_ms:.2f}ms"
