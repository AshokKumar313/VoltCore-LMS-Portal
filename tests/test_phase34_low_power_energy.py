"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 34 (Low-Power Sleep & Battery Profiler)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase34_low_power_energy.py
Target Facility: Lab 304 (Low-Power Embedded IoT & Energy Harvesting Laboratory)
Regulation: Anna University ECE Regulation 2023
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import csv
import io
import pytest
from backend.low_power_energy_engine import (
    LowPowerEnergyEngine,
    MCU_SLEEP_PROFILES,
    BATTERY_PRESETS,
    LIPO_SOC_VOLTAGE_CURVE
)


@pytest.fixture
def test_engine(tmp_path):
    """Provides an isolated LowPowerEnergyEngine backed by a temporary SQLite WAL DB."""
    db_file = str(tmp_path / "test_low_power_energy.db")
    engine = LowPowerEnergyEngine(db_path=db_file)
    return engine


def test_engine_initialization_and_wal(test_engine):
    """Verifies SQLite tables and WAL journal mode for energy simulation persistence."""
    conn = test_engine._get_connection()
    try:
        cur = conn.execute("PRAGMA journal_mode;")
        journal_mode = cur.fetchone()[0].upper()
        assert journal_mode == "WAL", f"Expected WAL mode, got {journal_mode}"

        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        assert "low_power_simulations" in tables
        assert "battery_discharge_profiles" in tables
    finally:
        conn.close()


def test_calculate_energy_profile_esp32_deep_sleep(test_engine):
    """Validates duty cycle, average current draw, and runtime projections for ESP32 deep sleep."""
    res = test_engine.calculate_energy_profile(
        mcu_target="ESP32_WROOM_32",
        active_mode="ACTIVE_WIFI_TX",     # 240 mA
        sleep_mode="DEEP_SLEEP",          # 0.010 mA
        active_duration_ms=200.0,         # 0.2 s
        sleep_duration_s=59.8,            # 59.8 s -> total 60.0 s
        battery_key="LIPO_18650_2500MAH", # 2500 mAh
        battery_efficiency=0.85,          # 2125 mAh usable
        student_id="2023MITEC042"
    )
    assert res["status"] == "SUCCESS"
    m = res["metrics"]

    # Duty cycle: 0.2 / 60.0 = 0.003333 -> 0.333%
    assert 0.33 <= m["duty_cycle_pct"] <= 0.34

    # Avg Current: (240 * 0.2 + 0.01 * 59.8) / 60 = (48 + 0.598) / 60 = 0.80997 mA
    assert 0.80 <= m["avg_current_ma"] <= 0.82
    assert 800 <= m["avg_current_ua"] <= 820

    # Usable capacity: 2500 * 0.85 = 2125 mAh
    # Runtime: 2125 / 0.81 ~= 2623 hours ~= 109.3 days
    assert m["runtime_hours"] > 2500.0
    assert m["runtime_days"] > 100.0
    assert m["runtime_months"] > 3.0


def test_calculate_energy_profile_stm32_stop_mode(test_engine):
    """Validates low-power energy calculations for STM32 Cortex-M4 Stop mode."""
    res = test_engine.calculate_energy_profile(
        mcu_target="STM32F401RE",
        active_mode="ACTIVE_RUN",         # 18.0 mA
        sleep_mode="STOP_MODE",           # 0.042 mA
        active_duration_ms=100.0,         # 0.1 s
        sleep_duration_s=9.9,             # 9.9 s -> total 10.0 s
        battery_key="LIPO_1200MAH",       # 1200 mAh
        battery_efficiency=0.85
    )
    assert res["status"] == "SUCCESS"
    m = res["metrics"]

    # Duty cycle: 0.1 / 10.0 = 1.0%
    assert m["duty_cycle_pct"] == 1.0

    # Avg Current: (18 * 0.1 + 0.042 * 9.9) / 10 = (1.8 + 0.4158) / 10 = 0.22158 mA
    assert 0.22 <= m["avg_current_ma"] <= 0.23
    assert m["runtime_days"] > 150.0


def test_calculate_energy_profile_nrf52840_ble(test_engine):
    """Validates ultra-low power System OFF mode on Nordic nRF52840."""
    res = test_engine.calculate_energy_profile(
        mcu_target="NRF52840_BLE",
        active_mode="RADIO_TX",            # 4.8 mA
        sleep_mode="SYSTEM_ON_IDLE",       # 0.0015 mA (1.5 uA)
        active_duration_ms=50.0,           # 0.05 s
        sleep_duration_s=9.95,             # 9.95 s -> total 10.0 s
        battery_key="LIPO_500MAH",         # 500 mAh
        battery_efficiency=0.90
    )
    assert res["status"] == "SUCCESS"
    m = res["metrics"]
    assert m["avg_current_ua"] < 30.0
    assert m["runtime_days"] > 600.0


def test_generate_discharge_curve(test_engine):
    """Validates piecewise non-linear LiPo discharge curve synthesis."""
    res = test_engine.generate_discharge_curve(
        battery_key="LIPO_18650_2500MAH",
        avg_current_ma=0.54,
        battery_efficiency=0.85
    )
    assert res["status"] == "SUCCESS"
    assert "profile_id" in res
    points = res["discharge_points"]

    # 11 points from 100% down to 0%
    assert len(points) == 11
    assert points[0]["soc_pct"] == 100.0
    assert points[0]["cell_voltage_v"] == 4.20
    assert points[0]["elapsed_hours"] == 0.0

    assert points[-1]["soc_pct"] == 0.0
    assert points[-1]["cell_voltage_v"] == 3.00
    assert points[-1]["elapsed_hours"] > 3500.0

    # Monotonically increasing elapsed hours
    for i in range(len(points) - 1):
        assert points[i]["elapsed_hours"] <= points[i + 1]["elapsed_hours"]
        assert points[i]["cell_voltage_v"] >= points[i + 1]["cell_voltage_v"]


def test_simulation_history_persistence(test_engine):
    """Verifies that energy simulations are saved and queryable from SQLite WAL."""
    test_engine.calculate_energy_profile(mcu_target="ESP32_WROOM_32")
    test_engine.calculate_energy_profile(mcu_target="STM32F401RE")

    history = test_engine.get_simulation_history(limit=5)
    assert len(history) == 2
    mcus = [h["mcu_target"] for h in history]
    assert "ESP32_WROOM_32" in mcus
    assert "STM32F401RE" in mcus


def test_export_energy_csv(test_engine):
    """Validates RFC-4180 CSV export generation across MCU and battery presets."""
    csv_str = test_engine.export_energy_csv()
    reader = csv.reader(io.StringIO(csv_str))
    rows = list(reader)

    # 1 header + (4 MCUs * 4 Batteries = 16 rows)
    assert len(rows) == 17
    headers = rows[0]
    assert "mcu_target" in headers
    assert "active_current_ma" in headers
    assert "sleep_current_ma" in headers
    assert "runtime_days_1pct_duty" in headers


def test_privacy_invariants_and_author_attribution():
    """Enforces absolute protection of private contact info and verifies public author identity."""
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    engine_path = os.path.join(workspace_root, "backend", "low_power_energy_engine.py")
    comp_path = os.path.join(workspace_root, "src", "components", "LowPowerEnergyHub.jsx")

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
