"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 33 (RTOS Task Scheduler & Latency Benchmarks)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase33_rtos_scheduler.py
Target Facility: Lab 304 (Real-Time Systems & Hardware-in-the-Loop Emulation)
Regulation: Anna University ECE Regulation 2023
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import csv
import io
import pytest
from backend.rtos_scheduler_engine import RtosSchedulerEngine, MCU_PRESETS


@pytest.fixture
def test_engine(tmp_path):
    """Provides an isolated RtosSchedulerEngine backed by a temporary SQLite WAL DB."""
    db_file = str(tmp_path / "test_rtos_scheduler.db")
    engine = RtosSchedulerEngine(db_path=db_file)
    return engine


def test_engine_initialization_and_wal(test_engine):
    """Verifies SQLite tables and WAL journal mode for deterministic RTOS telemetry."""
    conn = test_engine._get_connection()
    try:
        cur = conn.execute("PRAGMA journal_mode;")
        journal_mode = cur.fetchone()[0].upper()
        assert journal_mode == "WAL", f"Expected WAL mode, got {journal_mode}"

        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        assert "rtos_task_simulations" in tables
        assert "rtos_benchmark_logs" in tables
    finally:
        conn.close()


def test_liu_layland_bound_calculation():
    """Validates theoretical Rate-Monotonic utilization bounds U = n * (2^(1/n) - 1)."""
    assert RtosSchedulerEngine.calculate_liu_layland_bound(1) == 1.0
    # For n=2: 2 * (sqrt(2) - 1) ~= 0.8284
    assert 0.828 <= RtosSchedulerEngine.calculate_liu_layland_bound(2) <= 0.829
    # For n=3: 3 * (2^(1/3) - 1) ~= 0.7798
    assert 0.779 <= RtosSchedulerEngine.calculate_liu_layland_bound(3) <= 0.781
    # For n=100: approaches ln(2) ~= 0.6931
    assert 0.69 <= RtosSchedulerEngine.calculate_liu_layland_bound(100) <= 0.70


def test_benchmark_mcu_hardware_esp32(test_engine):
    """Validates hardware timing benchmarks for ESP32-WROOM-32 at 240 MHz."""
    res = test_engine.benchmark_mcu_hardware("ESP32_WROOM_32")
    assert res["status"] == "SUCCESS"
    assert res["clock_mhz"] == 240.0
    # 84 cycles / 240 MHz = 0.35 us
    assert res["context_switch_us"] == 0.35
    # 16 cycles / 240 MHz = 66.67 ns
    assert 66.0 <= res["interrupt_latency_ns"] <= 67.0
    assert res["fpu_enabled"] is True


def test_benchmark_mcu_hardware_stm32(test_engine):
    """Validates hardware timing benchmarks for STM32F401RE at 84 MHz."""
    res = test_engine.benchmark_mcu_hardware("STM32F401RE")
    assert res["status"] == "SUCCESS"
    assert res["clock_mhz"] == 84.0
    # 64 cycles / 84 MHz = 0.7619 us
    assert 0.76 <= res["context_switch_us"] <= 0.77
    # 12 cycles / 84 MHz = 142.86 ns
    assert 142.0 <= res["interrupt_latency_ns"] <= 143.0


def test_benchmark_mcu_hardware_atmega(test_engine):
    """Validates AVR ATmega328P context switch cycle benchmarks at 16 MHz."""
    res = test_engine.benchmark_mcu_hardware("ATMEGA328P")
    assert res["status"] == "SUCCESS"
    assert res["clock_mhz"] == 16.0
    # 142 cycles / 16 MHz = 8.875 us
    assert res["context_switch_us"] == 8.875
    assert res["fpu_enabled"] is False


def test_simulate_scheduler_preemptive(test_engine):
    """Validates deterministic preemptive priority dispatch and context switch count."""
    custom_tasks = [
        {"id": "T1", "name": "HighPri", "priority": 3, "burst_ms": 3, "period_ms": 15, "state": "READY"},
        {"id": "T2", "name": "MedPri", "priority": 2, "burst_ms": 5, "period_ms": 25, "state": "READY"},
        {"id": "T3", "name": "Idle", "priority": 0, "burst_ms": 50, "period_ms": 100, "state": "READY"}
    ]
    sim = test_engine.simulate_scheduler(
        tasks=custom_tasks,
        mode="PREEMPTIVE_PRIORITY",
        mcu_target="ESP32_WROOM_32",
        total_duration_ms=40,
        student_id="2023MITEC042"
    )
    assert sim["status"] == "SUCCESS"
    assert len(sim["timeline"]) == 40
    assert sim["metrics"]["mode"] == "PREEMPTIVE_PRIORITY"
    assert sim["metrics"]["context_switch_count"] >= 2
    assert sim["metrics"]["is_schedulable"] is True
    assert "simulation_id" in sim


def test_simulate_scheduler_cooperative(test_engine):
    """Validates cooperative round-robin execution where tasks run full burst uninterrupted."""
    custom_tasks = [
        {"id": "T1", "name": "TaskA", "priority": 2, "burst_ms": 4, "period_ms": 20, "state": "READY"},
        {"id": "T2", "name": "TaskB", "priority": 3, "burst_ms": 4, "period_ms": 20, "state": "READY"}
    ]
    sim = test_engine.simulate_scheduler(
        tasks=custom_tasks,
        mode="COOPERATIVE_ROUND_ROBIN",
        total_duration_ms=30
    )
    assert sim["status"] == "SUCCESS"
    assert sim["metrics"]["mode"] == "COOPERATIVE_ROUND_ROBIN"
    assert len(sim["timeline"]) == 30


def test_simulate_scheduler_overload(test_engine):
    """Ensures CPU overload condition (U > 100%) is flagged accurately."""
    overloaded_tasks = [
        {"id": "T1", "name": "HeavyA", "priority": 2, "burst_ms": 15, "period_ms": 20, "state": "READY"},
        {"id": "T2", "name": "HeavyB", "priority": 3, "burst_ms": 15, "period_ms": 20, "state": "READY"}
    ]
    # Total U = 15/20 + 15/20 = 1.50 = 150%
    sim = test_engine.simulate_scheduler(
        tasks=overloaded_tasks,
        total_duration_ms=20
    )
    assert sim["metrics"]["cpu_utilization_pct"] == 150.0
    assert sim["metrics"]["is_schedulable"] is False


def test_simulation_history_persistence(test_engine):
    """Verifies that simulation runs are persisted and queryable from SQLite WAL."""
    test_engine.simulate_scheduler(total_duration_ms=20)
    test_engine.simulate_scheduler(total_duration_ms=25)

    history = test_engine.get_simulation_history(limit=5)
    assert len(history) == 2
    assert history[0]["duration_ms"] in (20, 25)
    assert "cpu_utilization_pct" in history[0]


def test_export_benchmark_csv(test_engine):
    """Validates RFC-4180 CSV export generation with expected column headers."""
    csv_data = test_engine.export_benchmark_csv()
    reader = csv.reader(io.StringIO(csv_data))
    rows = list(reader)

    assert len(rows) == len(MCU_PRESETS) + 1  # 1 header + 4 MCU architectures
    headers = rows[0]
    assert "mcu_target" in headers
    assert "context_switch_cycles" in headers
    assert "interrupt_latency_ns" in headers
    assert "max_task_rate_khz" in headers


def test_privacy_invariants_and_author_attribution():
    """Enforces absolute protection of private contact info and verifies public author identity."""
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    engine_path = os.path.join(workspace_root, "backend", "rtos_scheduler_engine.py")
    comp_path = os.path.join(workspace_root, "src", "components", "RtosSchedulerHub.jsx")

    with open(engine_path, "r", encoding="utf-8") as f:
        engine_str = f.read()

    with open(comp_path, "r", encoding="utf-8") as f:
        comp_str = f.read()

    # STRICT INVARIANTS:
    # 1. Private credentials must NEVER leak into source code
    assert "ashokkumar2008313@gmail.com" not in engine_str
    assert "ashokkumar2008313@gmail.com" not in comp_str
    assert "9597382878" not in engine_str
    assert "9597382878" not in comp_str

    # 2. Public author attribution
    assert "Ashok Kumar A" in engine_str
    assert "2023MITEC042" in engine_str
    assert "2023MITEC042" in comp_str

