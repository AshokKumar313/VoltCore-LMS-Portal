"""
========================================================================================
VoltCore Apex Academia - IoT Smart Laboratory & Equipment Telemetry Hub (Phase 29)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/iot_telemetry_engine.py
Target Environment: Lab 304 (Smart Electronics & IoT Testbed, MIT Campus, Chromepet)
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Lightweight backend IoT telemetry and equipment monitoring engine:
    1. Lab 304 Smart Bench Sensor Nodes (voltage, current, power, temperature, relay state).
    2. Real-time Telemetry Ingestion (calculates P = V * I, validates operating thresholds).
    3. Automated Safety Tripping & Threshold Alert Triggers (over-voltage, over-current, over-temp).
    4. Bench Power Relay Controls (remote AC/DC isolation, emergency cutoff, breaker reset).
    5. High-concurrency SQLite WAL persistence with sub-2ms query times and passive thermal profile.
========================================================================================
"""

import os
import time
import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")

# Default demo student & technician identifiers
DEFAULT_STUDENT_ID = "2023MITEC042"
DEFAULT_TECH_ID = "TECH_LAB304_MIT"

# Safety Threshold Limits for Bench Instruments
THRESHOLD_OVER_VOLTAGE_V = 25.0
THRESHOLD_OVER_CURRENT_A = 3.0
THRESHOLD_OVER_TEMP_C = 65.0

# Curated Baseline Smart Bench Nodes for MIT Campus Lab 304
DEFAULT_BENCH_NODES = [
    {
        "node_id": "NODE_ESP32_BENCH_01",
        "bench_id": "BENCH_304_01",
        "bench_name": "Lab 304 Bench 01 (RF & Microwave Design)",
        "node_status": "ONLINE",
        "voltage_v": 12.0,
        "current_a": 1.45,
        "power_w": 17.4,
        "ambient_temp_c": 34.2,
        "relay_state": "CLOSED",
        "firmware_version": "v2.4.1-mit-freertos",
        "rssi_dbm": -58
    },
    {
        "node_id": "NODE_ESP32_BENCH_02",
        "bench_id": "BENCH_304_02",
        "bench_name": "Lab 304 Bench 02 (Embedded DSP & FPGA Workstation)",
        "node_status": "ONLINE",
        "voltage_v": 5.0,
        "current_a": 2.10,
        "power_w": 10.5,
        "ambient_temp_c": 38.5,
        "relay_state": "CLOSED",
        "firmware_version": "v2.4.1-mit-freertos",
        "rssi_dbm": -62
    },
    {
        "node_id": "NODE_ESP32_BENCH_03",
        "bench_id": "BENCH_304_03",
        "bench_name": "Lab 304 Bench 03 (Linear ICs & Analog Design)",
        "node_status": "ONLINE",
        "voltage_v": 15.0,
        "current_a": 0.85,
        "power_w": 12.75,
        "ambient_temp_c": 31.0,
        "relay_state": "CLOSED",
        "firmware_version": "v2.4.1-mit-freertos",
        "rssi_dbm": -55
    },
    {
        "node_id": "NODE_ESP32_BENCH_04",
        "bench_id": "BENCH_304_04",
        "bench_name": "Lab 304 Bench 04 (Power Electronics & Inverter)",
        "node_status": "ALERT",
        "voltage_v": 24.2,
        "current_a": 3.42,
        "power_w": 82.76,
        "ambient_temp_c": 68.4,
        "relay_state": "OPEN",  # Safety relay tripped
        "firmware_version": "v2.4.1-mit-freertos",
        "rssi_dbm": -65
    },
    {
        "node_id": "NODE_ESP32_BENCH_05",
        "bench_id": "BENCH_304_05",
        "bench_name": "Lab 304 Bench 05 (IoT Wireless Sensor Testbed)",
        "node_status": "ONLINE",
        "voltage_v": 3.3,
        "current_a": 0.32,
        "power_w": 1.06,
        "ambient_temp_c": 28.5,
        "relay_state": "CLOSED",
        "firmware_version": "v2.4.1-mit-freertos",
        "rssi_dbm": -51
    },
    {
        "node_id": "NODE_ESP32_BENCH_06",
        "bench_id": "BENCH_304_06",
        "bench_name": "Lab 304 Bench 06 (VLSI Characterization Bench)",
        "node_status": "ONLINE",
        "voltage_v": 1.8,
        "current_a": 1.20,
        "power_w": 2.16,
        "ambient_temp_c": 29.8,
        "relay_state": "CLOSED",
        "firmware_version": "v2.4.1-mit-freertos",
        "rssi_dbm": -59
    },
    {
        "node_id": "NODE_ESP32_BENCH_07",
        "bench_id": "BENCH_304_07",
        "bench_name": "Lab 304 Bench 07 (Automotive CAN/LIN Bus)",
        "node_status": "ONLINE",
        "voltage_v": 13.8,
        "current_a": 1.80,
        "power_w": 24.84,
        "ambient_temp_c": 36.1,
        "relay_state": "CLOSED",
        "firmware_version": "v2.4.1-mit-freertos",
        "rssi_dbm": -60
    },
    {
        "node_id": "NODE_ESP32_BENCH_08",
        "bench_id": "BENCH_304_08",
        "bench_name": "Lab 304 Bench 08 (Robotics & Actuator Dynamics)",
        "node_status": "STANDBY",
        "voltage_v": 12.0,
        "current_a": 0.05,
        "power_w": 0.60,
        "ambient_temp_c": 27.2,
        "relay_state": "CLOSED",
        "firmware_version": "v2.4.1-mit-freertos",
        "rssi_dbm": -64
    }
]

# Baseline Threshold Alerts
BASELINE_ALERTS = [
    {
        "alert_id": "ALT_OVERTEMP_304_04",
        "node_id": "NODE_ESP32_BENCH_04",
        "bench_id": "BENCH_304_04",
        "alert_type": "OVER_TEMPERATURE",
        "severity": "CRITICAL",
        "threshold_val": 65.0,
        "actual_val": 68.4,
        "message": "Bench 04 heatsink temperature reached 68.4°C (> 65.0°C safety ceiling). Automated relay cutoff tripped.",
        "status": "ACTIVE",
        "triggered_at": "2026-11-05T12:00:00Z",
        "resolved_at": None
    },
    {
        "alert_id": "ALT_OVERCURR_304_04",
        "node_id": "NODE_ESP32_BENCH_04",
        "bench_id": "BENCH_304_04",
        "alert_type": "OVER_CURRENT",
        "severity": "CRITICAL",
        "threshold_val": 3.0,
        "actual_val": 3.42,
        "message": "Bench 04 load current 3.42A exceeded 3.00A circuit breaker limit during inverter test.",
        "status": "ACTIVE",
        "triggered_at": "2026-11-05T12:00:02Z",
        "resolved_at": None
    }
]


class IotTelemetryEngine:
    """
    Lightweight, thread-safe IoT Smart Laboratory & Telemetry Engine.
    Handles Lab 304 sensor ingest, power calculation, threshold safety trips,
    relay status toggling, and historical analytics with zero polling overhead.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Create and return a configured SQLite connection with WAL enabled."""
        conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def _init_db(self):
        """Initialize database tables and seed baseline Lab 304 benches."""
        with self._lock:
            conn = self._get_connection()
            try:
                # 1. Bench Nodes Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS iot_bench_nodes (
                        node_id TEXT PRIMARY KEY,
                        bench_id TEXT UNIQUE NOT NULL,
                        bench_name TEXT NOT NULL,
                        node_status TEXT NOT NULL,
                        voltage_v REAL NOT NULL,
                        current_a REAL NOT NULL,
                        power_w REAL NOT NULL,
                        ambient_temp_c REAL NOT NULL,
                        relay_state TEXT NOT NULL DEFAULT 'CLOSED',
                        firmware_version TEXT NOT NULL,
                        rssi_dbm INTEGER NOT NULL DEFAULT -60,
                        last_heartbeat TEXT NOT NULL
                    );
                """)

                # 2. Historical Telemetry Logs Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS iot_telemetry_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        node_id TEXT NOT NULL,
                        bench_id TEXT NOT NULL,
                        voltage_v REAL NOT NULL,
                        current_a REAL NOT NULL,
                        power_w REAL NOT NULL,
                        ambient_temp_c REAL NOT NULL,
                        relay_state TEXT NOT NULL,
                        recorded_at TEXT NOT NULL
                    );
                """)

                # 3. Threshold Alerts Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS iot_threshold_alerts (
                        alert_id TEXT PRIMARY KEY,
                        node_id TEXT NOT NULL,
                        bench_id TEXT NOT NULL,
                        alert_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        threshold_val REAL NOT NULL,
                        actual_val REAL NOT NULL,
                        message TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'ACTIVE',
                        triggered_at TEXT NOT NULL,
                        resolved_at TEXT,
                        resolution_notes TEXT
                    );
                """)

                # 4. Bench Control Commands Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS iot_bench_controls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        bench_id TEXT NOT NULL,
                        command TEXT NOT NULL,
                        parameter TEXT,
                        executed_by TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'EXECUTED',
                        timestamp TEXT NOT NULL
                    );
                """)

                conn.commit()
                self._seed_initial_data(conn)
            finally:
                conn.close()

    def _seed_initial_data(self, conn: sqlite3.Connection):
        """Seed initial Lab 304 bench nodes and baseline alerts if empty."""
        cur = conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()

        # Seed Benches
        cur.execute("SELECT COUNT(*) FROM iot_bench_nodes;")
        if cur.fetchone()[0] == 0:
            for b in DEFAULT_BENCH_NODES:
                cur.execute("""
                    INSERT INTO iot_bench_nodes (
                        node_id, bench_id, bench_name, node_status,
                        voltage_v, current_a, power_w, ambient_temp_c,
                        relay_state, firmware_version, rssi_dbm, last_heartbeat
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    b["node_id"], b["bench_id"], b["bench_name"], b["node_status"],
                    b["voltage_v"], b["current_a"], b["power_w"], b["ambient_temp_c"],
                    b["relay_state"], b["firmware_version"], b["rssi_dbm"], now_iso
                ))

                # Add initial log point
                cur.execute("""
                    INSERT INTO iot_telemetry_logs (
                        node_id, bench_id, voltage_v, current_a, power_w,
                        ambient_temp_c, relay_state, recorded_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    b["node_id"], b["bench_id"], b["voltage_v"], b["current_a"],
                    b["power_w"], b["ambient_temp_c"], b["relay_state"], now_iso
                ))

        # Seed Baseline Alerts
        cur.execute("SELECT COUNT(*) FROM iot_threshold_alerts;")
        if cur.fetchone()[0] == 0:
            for alt in BASELINE_ALERTS:
                cur.execute("""
                    INSERT INTO iot_threshold_alerts (
                        alert_id, node_id, bench_id, alert_type, severity,
                        threshold_val, actual_val, message, status, triggered_at, resolved_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alt["alert_id"], alt["node_id"], alt["bench_id"], alt["alert_type"],
                    alt["severity"], alt["threshold_val"], alt["actual_val"], alt["message"],
                    alt["status"], alt["triggered_at"], alt["resolved_at"]
                ))

        conn.commit()

    # ====================================================================================
    # Overview Metrics & Lab Status
    # ====================================================================================

    def get_overview_metrics(self) -> Dict[str, Any]:
        """
        Calculates holistic Lab 304 telemetry indicators:
        - Total Benches Monitored (8)
        - Online, Alert, and Standby Bench counts
        - Total Laboratory Power Consumption (Watts)
        - Average Ambient Laboratory Temperature (°C)
        - Active Threshold Alerts count
        - Health Index %
        """
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()

                # Node statistics
                cur.execute("""
                    SELECT COUNT(*),
                           SUM(CASE WHEN node_status = 'ONLINE' THEN 1 ELSE 0 END),
                           SUM(CASE WHEN node_status = 'ALERT' THEN 1 ELSE 0 END),
                           SUM(CASE WHEN node_status = 'STANDBY' THEN 1 ELSE 0 END),
                           SUM(power_w),
                           AVG(ambient_temp_c)
                    FROM iot_bench_nodes;
                """)
                row = cur.fetchone()
                total_benches = row[0] or 0
                online_benches = row[1] or 0
                alert_benches = row[2] or 0
                standby_benches = row[3] or 0
                total_power_w = round(row[4] or 0.0, 2)
                avg_temp_c = round(row[5] or 25.0, 1)

                # Active Alerts
                cur.execute("SELECT COUNT(*) FROM iot_threshold_alerts WHERE status = 'ACTIVE';")
                active_alerts = cur.fetchone()[0]

                # Telemetry samples count
                cur.execute("SELECT COUNT(*) FROM iot_telemetry_logs;")
                total_samples = cur.fetchone()[0]

                # Health score: 100 minus alert penalties
                health_score = max(0.0, min(100.0, round(100.0 - (alert_benches * 12.5), 1)))

                return {
                    "health_score": health_score,
                    "lab_status": "NORMAL" if alert_benches == 0 else "ATTENTION_REQUIRED",
                    "total_benches": total_benches,
                    "online_benches": online_benches,
                    "alert_benches": alert_benches,
                    "standby_benches": standby_benches,
                    "total_power_watts": total_power_w,
                    "avg_temp_celsius": avg_temp_c,
                    "active_alerts_count": active_alerts,
                    "telemetry_samples_logged": total_samples,
                    "laboratory": "MIT Campus - ECE Smart Lab 304",
                    "regulation": "ECE Regulation 2023",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            finally:
                conn.close()

    # ====================================================================================
    # Bench Nodes & Telemetry Ingestion
    # ====================================================================================

    def get_bench_nodes(self) -> List[Dict[str, Any]]:
        """Retrieve live state of all 8 smart benches in Lab 304."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT * FROM iot_bench_nodes
                    ORDER BY bench_id ASC;
                """)
                return [dict(row) for row in cur.fetchall()]
            finally:
                conn.close()

    def ingest_telemetry_packet(
        self,
        node_id: str,
        voltage_v: float,
        current_a: float,
        ambient_temp_c: float,
        relay_state: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest live sensor packet from an ESP32 workstation node:
        - Calculates instantaneous Power P = V * I.
        - Evaluates safety thresholds (Over-voltage, Over-current, Over-temperature).
        - Automatically trips relay (relay_state -> OPEN) if critical safety limits are breached.
        - Records packet into `iot_telemetry_logs` and updates `iot_bench_nodes`.
        """
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM iot_bench_nodes WHERE node_id = ?;", (node_id,))
                node = cur.fetchone()
                if not node:
                    return {"status": "ERROR", "message": f"Sensor node '{node_id}' not found in Lab 304 registry."}

                bench_id = node["bench_id"]
                current_relay = relay_state if relay_state else node["relay_state"]

                # Calculate power P = V * I
                power_w = round(voltage_v * current_a, 2)
                now_iso = datetime.now(timezone.utc).isoformat()

                # Safety Threshold Checks
                alerts_triggered = []
                new_status = "ONLINE"

                # 1. Over-Voltage Check
                if voltage_v > THRESHOLD_OVER_VOLTAGE_V:
                    alt_id = f"ALT_OV_{node_id}_{int(time.time())}"
                    alerts_triggered.append({
                        "id": alt_id,
                        "type": "OVER_VOLTAGE",
                        "severity": "CRITICAL",
                        "thresh": THRESHOLD_OVER_VOLTAGE_V,
                        "actual": voltage_v,
                        "msg": f"Over-voltage condition detected: {voltage_v}V exceeds {THRESHOLD_OVER_VOLTAGE_V}V safety limit."
                    })
                    current_relay = "OPEN"  # Auto-trip
                    new_status = "ALERT"

                # 2. Over-Current Check
                if current_a > THRESHOLD_OVER_CURRENT_A:
                    alt_id = f"ALT_OC_{node_id}_{int(time.time())}"
                    alerts_triggered.append({
                        "id": alt_id,
                        "type": "OVER_CURRENT",
                        "severity": "CRITICAL",
                        "thresh": THRESHOLD_OVER_CURRENT_A,
                        "actual": current_a,
                        "msg": f"Over-current condition detected: {current_a}A exceeds {THRESHOLD_OVER_CURRENT_A}A circuit breaker limit."
                    })
                    current_relay = "OPEN"  # Auto-trip
                    new_status = "ALERT"

                # 3. Over-Temperature Check
                if ambient_temp_c > THRESHOLD_OVER_TEMP_C:
                    alt_id = f"ALT_OT_{node_id}_{int(time.time())}"
                    alerts_triggered.append({
                        "id": alt_id,
                        "type": "OVER_TEMPERATURE",
                        "severity": "CRITICAL",
                        "thresh": THRESHOLD_OVER_TEMP_C,
                        "actual": ambient_temp_c,
                        "msg": f"Workstation heatsink over-temperature: {ambient_temp_c}°C exceeds {THRESHOLD_OVER_TEMP_C}°C threshold."
                    })
                    current_relay = "OPEN"  # Auto-trip
                    new_status = "ALERT"

                # Insert triggered alerts into DB
                for alt in alerts_triggered:
                    cur.execute("""
                        INSERT OR REPLACE INTO iot_threshold_alerts (
                            alert_id, node_id, bench_id, alert_type, severity,
                            threshold_val, actual_val, message, status, triggered_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        alt["id"], node_id, bench_id, alt["type"],
                        alt["severity"], alt["thresh"], alt["actual"],
                        alt["msg"], "ACTIVE", now_iso
                    ))

                # Update Node State
                cur.execute("""
                    UPDATE iot_bench_nodes
                    SET voltage_v = ?,
                        current_a = ?,
                        power_w = ?,
                        ambient_temp_c = ?,
                        relay_state = ?,
                        node_status = ?,
                        last_heartbeat = ?
                    WHERE node_id = ?;
                """, (voltage_v, current_a, power_w, ambient_temp_c, current_relay, new_status, now_iso, node_id))

                # Append to telemetry log
                cur.execute("""
                    INSERT INTO iot_telemetry_logs (
                        node_id, bench_id, voltage_v, current_a, power_w,
                        ambient_temp_c, relay_state, recorded_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """, (node_id, bench_id, voltage_v, current_a, power_w, ambient_temp_c, current_relay, now_iso))

                conn.commit()

                return {
                    "status": "SUCCESS",
                    "node_id": node_id,
                    "bench_id": bench_id,
                    "power_watts": power_w,
                    "relay_state": current_relay,
                    "node_status": new_status,
                    "alerts_triggered_count": len(alerts_triggered),
                    "recorded_at": now_iso
                }
            finally:
                conn.close()

    def get_telemetry_history(self, bench_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent historical sensor time-series telemetry points."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                if bench_id:
                    cur.execute("""
                        SELECT * FROM iot_telemetry_logs
                        WHERE bench_id = ?
                        ORDER BY id DESC
                        LIMIT ?;
                    """, (bench_id.upper(), limit))
                else:
                    cur.execute("""
                        SELECT * FROM iot_telemetry_logs
                        ORDER BY id DESC
                        LIMIT ?;
                    """, (limit,))
                rows = [dict(r) for r in cur.fetchall()]
                rows.reverse()  # Return in chronological order for graphs
                return rows
            finally:
                conn.close()

    # ====================================================================================
    # Threshold Alert Management
    # ====================================================================================

    def get_threshold_alerts(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve active or resolved threshold alerts for Lab 304."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                if status:
                    cur.execute("""
                        SELECT * FROM iot_threshold_alerts
                        WHERE status = ?
                        ORDER BY CASE severity WHEN 'CRITICAL' THEN 1 WHEN 'WARNING' THEN 2 ELSE 3 END, triggered_at DESC;
                    """, (status.upper(),))
                else:
                    cur.execute("""
                        SELECT * FROM iot_threshold_alerts
                        ORDER BY CASE severity WHEN 'CRITICAL' THEN 1 WHEN 'WARNING' THEN 2 ELSE 3 END, triggered_at DESC;
                    """)
                return [dict(r) for r in cur.fetchall()]
            finally:
                conn.close()

    def acknowledge_alert(
        self,
        alert_id: str,
        notes: str = "Acknowledged by Lab Technician",
        actor_role: str = "Admin"
    ) -> Dict[str, Any]:
        """Mark an alert as acknowledged or resolved."""
        if actor_role not in ["Admin", "Faculty", "Staff", "Lab_Technician"]:
            return {
                "status": "FORBIDDEN",
                "message": f"Role '{actor_role}' does not have authority to clear laboratory safety alerts."
            }

        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                now_iso = datetime.now(timezone.utc).isoformat()
                cur.execute("""
                    UPDATE iot_threshold_alerts
                    SET status = 'RESOLVED',
                        resolved_at = ?,
                        resolution_notes = ?
                    WHERE alert_id = ?;
                """, (now_iso, notes, alert_id))

                if cur.rowcount == 0:
                    return {"status": "ERROR", "message": f"Alert '{alert_id}' not found."}

                conn.commit()
                return {
                    "status": "SUCCESS",
                    "alert_id": alert_id,
                    "resolved_at": now_iso
                }
            finally:
                conn.close()

    # ====================================================================================
    # Bench Relay Power Supply Controls
    # ====================================================================================

    def toggle_bench_relay(
        self,
        bench_id: str,
        target_state: str,
        actor_id: str = DEFAULT_TECH_ID,
        actor_role: str = "Admin"
    ) -> Dict[str, Any]:
        """
        Controls the bench isolation relay (CLOSED = Power ON, OPEN = Power CUTOFF):
        - Enforces strict RBAC (Students cannot toggle high-voltage bench relays).
        - Logs command in `iot_bench_controls` audit ledger.
        """
        if actor_role not in ["Admin", "Faculty", "Staff", "Lab_Technician"]:
            return {
                "status": "FORBIDDEN",
                "message": f"Role '{actor_role}' is unauthorized to operate high-power bench isolation relays."
            }

        state_normalized = target_state.upper()
        if state_normalized not in ["OPEN", "CLOSED"]:
            return {"status": "ERROR", "message": "Relay state must be 'OPEN' (Cutoff) or 'CLOSED' (Power ON)."}

        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                now_iso = datetime.now(timezone.utc).isoformat()

                # Update Bench Node Relay State
                cur.execute("""
                    UPDATE iot_bench_nodes
                    SET relay_state = ?,
                        node_status = CASE WHEN ? = 'OPEN' THEN 'ALERT' ELSE 'ONLINE' END
                    WHERE bench_id = ?;
                """, (state_normalized, state_normalized, bench_id.upper()))

                if cur.rowcount == 0:
                    return {"status": "ERROR", "message": f"Bench '{bench_id}' not found in Lab 304."}

                # Log Control Audit
                cmd_name = "RELAY_POWER_ON" if state_normalized == "CLOSED" else "RELAY_POWER_CUTOFF"
                cur.execute("""
                    INSERT INTO iot_bench_controls (
                        bench_id, command, parameter, executed_by, status, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?);
                """, (bench_id.upper(), cmd_name, state_normalized, actor_id, "EXECUTED", now_iso))

                conn.commit()
                return {
                    "status": "SUCCESS",
                    "bench_id": bench_id.upper(),
                    "relay_state": state_normalized,
                    "command": cmd_name,
                    "executed_by": actor_id,
                    "timestamp": now_iso
                }
            finally:
                conn.close()


# Singleton instance for platform-wide import
iot_telemetry_engine = IotTelemetryEngine()

