"""
========================================================================================
VoltCore Apex Academia - RTOS Task Scheduler & Context Switch Engine (Phase 33)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
Target Facility: Lab 304 (Real-Time Systems & Hardware-in-the-Loop Emulation)
Regulation: Anna University ECE Regulation 2023
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import csv
import io
import json
import uuid
import math
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")
DEFAULT_STUDENT_ID = "2023MITEC042"

# Microcontroller Hardware Architecture Presets for Context Switch Benchmarking
MCU_PRESETS: Dict[str, Dict[str, Any]] = {
    "ESP32_WROOM_32": {
        "name": "ESP32-WROOM-32 (Tensilica Xtensa Dual-Core)",
        "clock_mhz": 240.0,
        "context_switch_cycles": 84,
        "interrupt_latency_cycles": 16,
        "critical_section_cycles": 12,
        "fpu_enabled": True,
        "rtos_kernel": "FreeRTOS SMP Core 1"
    },
    "STM32F401RE": {
        "name": "STM32F401RE Nucleo (ARM Cortex-M4 with FPU)",
        "clock_mhz": 84.0,
        "context_switch_cycles": 64,
        "interrupt_latency_cycles": 12,
        "critical_section_cycles": 8,
        "fpu_enabled": True,
        "rtos_kernel": "FreeRTOS Classic"
    },
    "ARM_CORTEX_M0_PLUS": {
        "name": "RP2040 / SAMD21 (ARM Cortex-M0+)",
        "clock_mhz": 48.0,
        "context_switch_cycles": 96,
        "interrupt_latency_cycles": 15,
        "critical_section_cycles": 10,
        "fpu_enabled": False,
        "rtos_kernel": "FreeRTOS Thumb-1"
    },
    "ATMEGA328P": {
        "name": "ATmega328P (8-bit AVR RISC Architecture)",
        "clock_mhz": 16.0,
        "context_switch_cycles": 142,
        "interrupt_latency_cycles": 4,
        "critical_section_cycles": 4,
        "fpu_enabled": False,
        "rtos_kernel": "FreeRTOS 8-bit Port"
    }
}

# Standard ECE Lab 304 Curated Embedded Tasks
DEFAULT_ECE_TASKS: List[Dict[str, Any]] = [
    {
        "id": "TASK_1",
        "name": "Sensor_Acquisition_ISR",
        "tamil_name": "உணரி சமிக்ஞை கையகப்படுத்தல்",
        "priority": 3,
        "burst_ms": 4,
        "period_ms": 20,
        "deadline_ms": 20,
        "state": "READY"
    },
    {
        "id": "TASK_2",
        "name": "TinyML_Vibration_Filter",
        "tamil_name": "நுண் இயந்திர கற்றல் வடிப்பான்",
        "priority": 2,
        "burst_ms": 8,
        "period_ms": 40,
        "deadline_ms": 40,
        "state": "READY"
    },
    {
        "id": "TASK_3",
        "name": "MQTT_Telemetry_Publisher",
        "tamil_name": "MQTT தொலைத்தொடர்பு வெளியீடு",
        "priority": 1,
        "burst_ms": 12,
        "period_ms": 100,
        "deadline_ms": 100,
        "state": "READY"
    },
    {
        "id": "TASK_IDLE",
        "name": "FreeRTOS_Idle_Daemon",
        "tamil_name": "செயலற்ற பின்னணி பணி",
        "priority": 0,
        "burst_ms": 50,
        "period_ms": 100,
        "deadline_ms": 100,
        "state": "READY"
    }
]


class RtosSchedulerEngine:
    """
    Lightweight, thread-safe RTOS Task Scheduling Simulator & Benchmarking Engine.
    Executes deterministic preemptive priority and cooperative multi-tasking simulations
    persisted into SQLite WAL tables with zero continuous background loops.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Establishes an optimized SQLite connection in WAL mode."""
        conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_db(self):
        """Initializes tables for RTOS task simulations and MCU latency benchmarks."""
        with self._lock:
            conn = self._get_connection()
            try:
                # 1. RTOS Scheduling Simulations
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS rtos_task_simulations (
                        simulation_id TEXT PRIMARY KEY,
                        mode TEXT NOT NULL,
                        mcu_target TEXT NOT NULL,
                        total_duration_ms INTEGER NOT NULL,
                        cpu_utilization_pct REAL NOT NULL,
                        context_switch_count INTEGER NOT NULL,
                        context_switch_overhead_pct REAL NOT NULL,
                        is_schedulable INTEGER NOT NULL,
                        timeline_json TEXT NOT NULL,
                        metrics_json TEXT NOT NULL,
                        student_id TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_rtos_sim_mode ON rtos_task_simulations(mode);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_rtos_sim_mcu ON rtos_task_simulations(mcu_target);")

                # 2. RTOS Benchmark Logs
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS rtos_benchmark_logs (
                        log_id TEXT PRIMARY KEY,
                        mcu_target TEXT NOT NULL,
                        clock_mhz REAL NOT NULL,
                        context_switch_cycles INTEGER NOT NULL,
                        context_switch_us REAL NOT NULL,
                        interrupt_latency_ns REAL NOT NULL,
                        max_task_rate_khz REAL NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)
                conn.commit()
            finally:
                conn.close()

    @staticmethod
    def calculate_liu_layland_bound(num_tasks: int) -> float:
        """
        Computes the theoretical Liu-Layland CPU utilization bound:
        U_bound = n * (2^(1/n) - 1)
        For Rate-Monotonic Schedulability Guarantee.
        """
        if num_tasks <= 0:
            return 1.0
        return round(num_tasks * (math.pow(2.0, 1.0 / num_tasks) - 1.0), 4)

    def benchmark_mcu_hardware(
        self,
        mcu_key: str = "ESP32_WROOM_32"
    ) -> Dict[str, Any]:
        """
        Calculates exact hardware interrupt latency, context switch overhead, and
        maximum task dispatch frequency for target microcontroller architectures.
        """
        preset = MCU_PRESETS.get(mcu_key, MCU_PRESETS["ESP32_WROOM_32"])
        clock_mhz = preset["clock_mhz"]
        cs_cycles = preset["context_switch_cycles"]
        irq_cycles = preset["interrupt_latency_cycles"]

        # Cycle time in nanoseconds: T_cyc = 1000 / clock_mhz
        cycle_ns = 1000.0 / clock_mhz

        # Context switch time in microseconds
        context_switch_us = round((cs_cycles * cycle_ns) / 1000.0, 4)

        # Interrupt latency in nanoseconds (hardware stacking + NVIC tail-chain)
        interrupt_latency_ns = round(irq_cycles * cycle_ns, 2)

        # Maximum schedulable task switching rate (kHz) assuming 5us minimum execution
        min_task_exec_us = 5.0
        max_task_rate_khz = round(1000.0 / (context_switch_us + min_task_exec_us), 2)

        log_id = f"BM_{uuid.uuid4().hex[:8].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()

        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT INTO rtos_benchmark_logs
                    (log_id, mcu_target, clock_mhz, context_switch_cycles,
                     context_switch_us, interrupt_latency_ns, max_task_rate_khz, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    log_id, mcu_key, clock_mhz, cs_cycles,
                    context_switch_us, interrupt_latency_ns, max_task_rate_khz, now_iso
                ))
                conn.commit()
            finally:
                conn.close()

        return {
            "status": "SUCCESS",
            "log_id": log_id,
            "mcu_target": mcu_key,
            "architecture_name": preset["name"],
            "clock_mhz": clock_mhz,
            "context_switch_cycles": cs_cycles,
            "context_switch_us": context_switch_us,
            "interrupt_latency_ns": interrupt_latency_ns,
            "max_task_rate_khz": max_task_rate_khz,
            "fpu_enabled": preset["fpu_enabled"],
            "rtos_kernel": preset["rtos_kernel"],
            "timestamp": now_iso
        }

    def simulate_scheduler(
        self,
        tasks: Optional[List[Dict[str, Any]]] = None,
        mode: str = "PREEMPTIVE_PRIORITY",
        mcu_target: str = "ESP32_WROOM_32",
        total_duration_ms: int = 50,
        student_id: str = DEFAULT_STUDENT_ID
    ) -> Dict[str, Any]:
        """
        Executes a deterministic RTOS task scheduling simulation.
        Modes: 'PREEMPTIVE_PRIORITY' or 'COOPERATIVE_ROUND_ROBIN'.
        Produces a Gantt timeline, CPU utilization, context switch counts, and
        schedulability metrics.
        """
        task_list = tasks if tasks is not None else DEFAULT_ECE_TASKS
        preset = MCU_PRESETS.get(mcu_target, MCU_PRESETS["ESP32_WROOM_32"])
        cs_time_us = (preset["context_switch_cycles"] * (1000.0 / preset["clock_mhz"])) / 1000.0

        # Calculate theoretical utilization (excluding Idle task)
        active_tasks = [t for t in task_list if t["priority"] > 0]
        utilization = sum(t["burst_ms"] / t["period_ms"] for t in active_tasks if t.get("period_ms", 0) > 0)
        utilization_pct = round(utilization * 100.0, 2)
        bound = self.calculate_liu_layland_bound(len(active_tasks))
        bound_pct = round(bound * 100.0, 2)
        is_schedulable = utilization <= 1.0

        # Discrete simulation timeline generation (1ms slices)
        timeline: List[Dict[str, Any]] = []
        task_remaining = {t["id"]: 0 for t in task_list}
        task_next_release = {t["id"]: 0 for t in task_list}
        context_switch_count = 0
        current_running_id: Optional[str] = None

        duration = max(10, min(total_duration_ms, 200))

        for t in range(duration):
            # 1. Release periodic tasks
            for task in task_list:
                if t >= task_next_release[task["id"]]:
                    task_remaining[task["id"]] = task["burst_ms"]
                    task_next_release[task["id"]] = t + task["period_ms"]

            # 2. Determine highest priority READY task
            eligible = []
            for task in task_list:
                if task.get("state") in ("SUSPENDED", "BLOCKED"):
                    continue
                if task_remaining[task["id"]] > 0:
                    eligible.append(task)

            if eligible:
                if mode == "PREEMPTIVE_PRIORITY":
                    # Strictly highest priority first
                    eligible.sort(key=lambda x: x["priority"], reverse=True)
                    chosen = eligible[0]
                else:
                    # Cooperative: keep running current task until burst exhausted
                    if current_running_id and task_remaining.get(current_running_id, 0) > 0:
                        chosen = next((x for x in eligible if x["id"] == current_running_id), eligible[0])
                    else:
                        eligible.sort(key=lambda x: x["priority"], reverse=True)
                        chosen = eligible[0]

                # Check if context switch occurred
                if current_running_id != chosen["id"]:
                    context_switch_count += 1
                    current_running_id = chosen["id"]

                task_remaining[chosen["id"]] -= 1
                timeline.append({
                    "time_ms": t,
                    "task_id": chosen["id"],
                    "task_name": chosen["name"],
                    "priority": chosen["priority"],
                    "state": "RUNNING"
                })
            else:
                # CPU Idle
                if current_running_id != "IDLE":
                    context_switch_count += 1
                    current_running_id = "IDLE"
                timeline.append({
                    "time_ms": t,
                    "task_id": "IDLE",
                    "task_name": "FreeRTOS_Idle_Daemon",
                    "priority": 0,
                    "state": "IDLE"
                })

        # Calculate overhead: total time spent in context switching
        total_cs_time_ms = (context_switch_count * cs_time_us) / 1000.0
        cs_overhead_pct = round((total_cs_time_ms / duration) * 100.0, 4)

        simulation_id = f"SIM_{uuid.uuid4().hex[:8].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()

        metrics = {
            "mode": mode,
            "mcu_target": mcu_target,
            "total_tasks": len(task_list),
            "cpu_utilization_pct": utilization_pct,
            "liu_layland_bound_pct": bound_pct,
            "is_schedulable": is_schedulable,
            "context_switch_count": context_switch_count,
            "context_switch_overhead_pct": cs_overhead_pct,
            "context_switch_latency_us": round(cs_time_us, 4),
            "duration_ms": duration
        }

        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT INTO rtos_task_simulations
                    (simulation_id, mode, mcu_target, total_duration_ms, cpu_utilization_pct,
                     context_switch_count, context_switch_overhead_pct, is_schedulable,
                     timeline_json, metrics_json, student_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    simulation_id, mode, mcu_target, duration, utilization_pct,
                    context_switch_count, cs_overhead_pct, 1 if is_schedulable else 0,
                    json.dumps(timeline), json.dumps(metrics), student_id, now_iso
                ))
                conn.commit()
            finally:
                conn.close()

        return {
            "status": "SUCCESS",
            "simulation_id": simulation_id,
            "metrics": metrics,
            "timeline": timeline,
            "timestamp": now_iso
        }

    def get_simulation_history(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Retrieves recent task scheduling simulation runs from the WAL database."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.execute(
                    "SELECT simulation_id, mode, mcu_target, total_duration_ms, cpu_utilization_pct, "
                    "context_switch_count, context_switch_overhead_pct, is_schedulable, metrics_json, created_at "
                    "FROM rtos_task_simulations ORDER BY created_at DESC LIMIT ?;",
                    (limit,)
                )
                rows = cur.fetchall()
                history = []
                for r in rows:
                    history.append({
                        "simulation_id": r["simulation_id"],
                        "mode": r["mode"],
                        "mcu_target": r["mcu_target"],
                        "duration_ms": r["total_duration_ms"],
                        "cpu_utilization_pct": r["cpu_utilization_pct"],
                        "context_switch_count": r["context_switch_count"],
                        "context_switch_overhead_pct": r["context_switch_overhead_pct"],
                        "is_schedulable": bool(r["is_schedulable"]),
                        "metrics": json.loads(r["metrics_json"]),
                        "created_at": r["created_at"]
                    })
                return history
            finally:
                conn.close()

    def export_benchmark_csv(self, simulation_id: Optional[str] = None) -> str:
        """
        Exports RTOS scheduling benchmarks and hardware metrics as an RFC-4180 compliant CSV string.
        """
        output = io.StringIO()
        fieldnames = [
            "mcu_target",
            "architecture_name",
            "clock_mhz",
            "context_switch_cycles",
            "context_switch_us",
            "interrupt_latency_ns",
            "max_task_rate_khz",
            "fpu_enabled",
            "rtos_kernel"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for mcu_key in MCU_PRESETS:
            bm = self.benchmark_mcu_hardware(mcu_key)
            writer.writerow({
                "mcu_target": bm["mcu_target"],
                "architecture_name": bm["architecture_name"],
                "clock_mhz": bm["clock_mhz"],
                "context_switch_cycles": bm["context_switch_cycles"],
                "context_switch_us": bm["context_switch_us"],
                "interrupt_latency_ns": bm["interrupt_latency_ns"],
                "max_task_rate_khz": bm["max_task_rate_khz"],
                "fpu_enabled": bm["fpu_enabled"],
                "rtos_kernel": bm["rtos_kernel"]
            })

        return output.getvalue()


# Singleton Instance
rtos_scheduler_engine = RtosSchedulerEngine()
