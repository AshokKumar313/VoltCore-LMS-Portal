"""
========================================================================================
VoltCore Apex Academia - Low-Power Sleep & Battery Profiler Engine (Phase 34)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
Target Facility: Lab 304 (Low-Power Embedded IoT & Energy Harvesting Laboratory)
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

# Microcontroller Sleep State Profiles (Current draw in mA)
MCU_SLEEP_PROFILES: Dict[str, Dict[str, Any]] = {
    "ESP32_WROOM_32": {
        "name": "ESP32-WROOM-32 (Tensilica Xtensa Dual-Core)",
        "voltage_nominal": 3.3,
        "modes": {
            "ACTIVE_WIFI_TX": {"name": "Active Wi-Fi Tx (20 dBm)", "current_ma": 240.0, "clock": "240 MHz"},
            "ACTIVE_CPU": {"name": "Active CPU Only (No RF)", "current_ma": 45.0, "clock": "240 MHz"},
            "MODEM_SLEEP": {"name": "Modem-Sleep (DTIM3 Beacon)", "current_ma": 15.0, "clock": "240 MHz"},
            "LIGHT_SLEEP": {"name": "Light-Sleep (RAM Retained)", "current_ma": 0.800, "clock": "Clock Gated"},
            "DEEP_SLEEP": {"name": "Deep-Sleep (ULP + RTC Mem)", "current_ma": 0.010, "clock": "RTC 150 kHz"},
            "HIBERNATION": {"name": "Hibernation (RTC Timer Only)", "current_ma": 0.005, "clock": "RTC 32 kHz"}
        },
        "wake_sources": ["RTC_TIMER", "EXT0_GPIO", "EXT1_BITMAP", "TOUCH_PAD", "ULP_COPROCESSOR"]
    },
    "STM32F401RE": {
        "name": "STM32F401RE Nucleo (ARM Cortex-M4 with FPU)",
        "voltage_nominal": 3.3,
        "modes": {
            "ACTIVE_RUN": {"name": "Active Run Mode", "current_ma": 18.0, "clock": "84 MHz"},
            "SLEEP_WFI": {"name": "Sleep Mode (WFI / Clock Gated)", "current_ma": 4.5, "clock": "Peripherals Active"},
            "STOP_MODE": {"name": "Stop Mode (All Clocks Off, RAM On)", "current_ma": 0.042, "clock": "LSI / LSE"},
            "STANDBY_MODE": {"name": "Standby Mode (1.2V Off, Backup Reg)", "current_ma": 0.0025, "clock": "RTC Only"}
        },
        "wake_sources": ["RTC_ALARM", "WKUP_PIN", "EXTI_GPIO", "TAMPER_EVENT"]
    },
    "NRF52840_BLE": {
        "name": "Nordic nRF52840 (ARM Cortex-M4F BLE 5.3)",
        "voltage_nominal": 3.0,
        "modes": {
            "RADIO_TX": {"name": "Radio Tx (+4 dBm)", "current_ma": 4.8, "clock": "64 MHz"},
            "CPU_ACTIVE": {"name": "CPU Active Only", "current_ma": 3.3, "clock": "64 MHz"},
            "SYSTEM_ON_IDLE": {"name": "System ON (Idle, RAM Retained)", "current_ma": 0.0015, "clock": "32 kHz RTC"},
            "SYSTEM_OFF": {"name": "System OFF (Deepest Sleep)", "current_ma": 0.0004, "clock": "Pin Reset Only"}
        },
        "wake_sources": ["RTC_COMPARE", "NFC_FIELD", "LPCOMP_ANALOG", "GPIO_DETECT"]
    },
    "ATMEGA328P": {
        "name": "ATmega328P (8-bit AVR RISC Architecture)",
        "voltage_nominal": 5.0,
        "modes": {
            "ACTIVE": {"name": "Active Run (16 MHz)", "current_ma": 12.0, "clock": "16 MHz XTAL"},
            "IDLE": {"name": "Idle Mode", "current_ma": 3.5, "clock": "Timer Active"},
            "POWER_DOWN_WDT": {"name": "Power-Down (WDT On)", "current_ma": 0.006, "clock": "WDT 128 kHz"},
            "POWER_DOWN_OFF": {"name": "Power-Down (WDT Off, Ext Interrupt)", "current_ma": 0.0001, "clock": "Static"}
        },
        "wake_sources": ["WDT_TIMEOUT", "INT0_INT1", "PIN_CHANGE", "TWI_ADDRESS"]
    }
}

# Standard Chemical Battery Profiles
BATTERY_PRESETS: Dict[str, Dict[str, Any]] = {
    "LIPO_500MAH": {
        "name": "LiPo 1S 3.7V (500 mAh) Wearable",
        "nominal_mah": 500.0,
        "voltage_nominal": 3.7,
        "voltage_full": 4.20,
        "voltage_cutoff": 3.00,
        "chemistry": "Lithium-Polymer"
    },
    "LIPO_1200MAH": {
        "name": "LiPo 1S 3.7V (1200 mAh) IoT Sensor Node",
        "nominal_mah": 1200.0,
        "voltage_nominal": 3.7,
        "voltage_full": 4.20,
        "voltage_cutoff": 3.00,
        "chemistry": "Lithium-Polymer"
    },
    "LIPO_18650_2500MAH": {
        "name": "18650 Li-Ion Cell (2500 mAh) Industrial Grade",
        "nominal_mah": 2500.0,
        "voltage_nominal": 3.7,
        "voltage_full": 4.20,
        "voltage_cutoff": 3.00,
        "chemistry": "Lithium-Ion"
    },
    "LI_SOCL2_3000MAH": {
        "name": "Tadiran Li-SOCl2 (3000 mAh) Ultra-Long Life",
        "nominal_mah": 3000.0,
        "voltage_nominal": 3.6,
        "voltage_full": 3.65,
        "voltage_cutoff": 2.80,
        "chemistry": "Lithium-Thionyl Chloride"
    }
}

# Empirical Non-linear LiPo Discharge Mapping (State of Charge % -> Cell Voltage V)
LIPO_SOC_VOLTAGE_CURVE: List[Tuple[float, float]] = [
    (100.0, 4.20),
    (90.0, 4.05),
    (80.0, 3.96),
    (70.0, 3.88),
    (60.0, 3.82),
    (50.0, 3.77),
    (40.0, 3.73),
    (30.0, 3.69),
    (20.0, 3.62),
    (10.0, 3.50),
    (0.0, 3.00)
]


class LowPowerEnergyEngine:
    """
    Lightweight, thread-safe Low-Power Sleep & Battery Discharge Profiling Engine.
    Computes duty cycles, average current draw, operating lifetimes, and piecewise
    discharge curves persisted into SQLite WAL mode with zero continuous background loops.
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
        """Initializes tables for low power energy simulations and battery discharge curves."""
        with self._lock:
            conn = self._get_connection()
            try:
                # 1. Low Power Simulations Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS low_power_simulations (
                        simulation_id TEXT PRIMARY KEY,
                        mcu_target TEXT NOT NULL,
                        active_mode TEXT NOT NULL,
                        sleep_mode TEXT NOT NULL,
                        wake_source TEXT NOT NULL,
                        active_duration_ms REAL NOT NULL,
                        sleep_duration_s REAL NOT NULL,
                        duty_cycle_pct REAL NOT NULL,
                        avg_current_ma REAL NOT NULL,
                        avg_power_mw REAL NOT NULL,
                        battery_key TEXT NOT NULL,
                        runtime_hours REAL NOT NULL,
                        runtime_days REAL NOT NULL,
                        metrics_json TEXT NOT NULL,
                        student_id TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_lp_mcu ON low_power_simulations(mcu_target);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_lp_battery ON low_power_simulations(battery_key);")

                # 2. Battery Discharge Curves Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS battery_discharge_profiles (
                        profile_id TEXT PRIMARY KEY,
                        battery_key TEXT NOT NULL,
                        avg_current_ma REAL NOT NULL,
                        total_runtime_hours REAL NOT NULL,
                        discharge_points_json TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)
                conn.commit()
            finally:
                conn.close()

    def calculate_energy_profile(
        self,
        mcu_target: str = "ESP32_WROOM_32",
        active_mode: str = "ACTIVE_WIFI_TX",
        sleep_mode: str = "DEEP_SLEEP",
        wake_source: str = "RTC_TIMER",
        active_duration_ms: float = 200.0,
        sleep_duration_s: float = 59.8,
        battery_key: str = "LIPO_18650_2500MAH",
        battery_efficiency: float = 0.85,
        student_id: str = DEFAULT_STUDENT_ID
    ) -> Dict[str, Any]:
        """
        Calculates operational runtime, duty cycle, average current draw, and power
        dissipation based on active vs sleep duration.
        """
        mcu_data = MCU_SLEEP_PROFILES.get(mcu_target, MCU_SLEEP_PROFILES["ESP32_WROOM_32"])
        battery_data = BATTERY_PRESETS.get(battery_key, BATTERY_PRESETS["LIPO_18650_2500MAH"])

        # Currents in mA
        i_active = mcu_data["modes"].get(active_mode, {"current_ma": 240.0})["current_ma"]
        i_sleep = mcu_data["modes"].get(sleep_mode, {"current_ma": 0.010})["current_ma"]

        # Time conversions to seconds
        t_active_s = max(0.001, active_duration_ms / 1000.0)
        t_sleep_s = max(0.001, sleep_duration_s)
        t_total_s = t_active_s + t_sleep_s

        # Duty cycle percentage
        duty_cycle_pct = round((t_active_s / t_total_s) * 100.0, 4)

        # Average current in mA
        avg_current_ma = ((i_active * t_active_s) + (i_sleep * t_sleep_s)) / t_total_s
        avg_current_ma = round(avg_current_ma, 5)
        avg_current_ua = round(avg_current_ma * 1000.0, 2)

        # Average power in mW
        v_nom = battery_data["voltage_nominal"]
        avg_power_mw = round(avg_current_ma * v_nom, 4)

        # Usable battery capacity accounting for LDO/quiescent losses
        usable_mah = battery_data["nominal_mah"] * max(0.5, min(1.0, battery_efficiency))

        # Runtime projections
        runtime_hours = round(usable_mah / avg_current_ma, 2)
        runtime_days = round(runtime_hours / 24.0, 2)
        runtime_months = round(runtime_days / 30.417, 2)
        runtime_years = round(runtime_days / 365.25, 3)

        # Energy metrics
        total_energy_mwh = round(battery_data["nominal_mah"] * v_nom, 1)
        daily_energy_mwh = round(avg_power_mw * 24.0, 2)

        simulation_id = f"LP_{uuid.uuid4().hex[:8].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()

        metrics = {
            "mcu_target": mcu_target,
            "mcu_name": mcu_data["name"],
            "active_mode": active_mode,
            "active_current_ma": i_active,
            "sleep_mode": sleep_mode,
            "sleep_current_ma": i_sleep,
            "wake_source": wake_source,
            "active_duration_ms": active_duration_ms,
            "sleep_duration_s": sleep_duration_s,
            "duty_cycle_pct": duty_cycle_pct,
            "avg_current_ma": avg_current_ma,
            "avg_current_ua": avg_current_ua,
            "avg_power_mw": avg_power_mw,
            "battery_key": battery_key,
            "battery_name": battery_data["name"],
            "battery_nominal_mah": battery_data["nominal_mah"],
            "battery_voltage": v_nom,
            "battery_efficiency": battery_efficiency,
            "runtime_hours": runtime_hours,
            "runtime_days": runtime_days,
            "runtime_months": runtime_months,
            "runtime_years": runtime_years,
            "total_energy_mwh": total_energy_mwh,
            "daily_energy_mwh": daily_energy_mwh
        }

        # Persist simulation in SQLite WAL
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT INTO low_power_simulations
                    (simulation_id, mcu_target, active_mode, sleep_mode, wake_source,
                     active_duration_ms, sleep_duration_s, duty_cycle_pct, avg_current_ma,
                     avg_power_mw, battery_key, runtime_hours, runtime_days, metrics_json, student_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    simulation_id, mcu_target, active_mode, sleep_mode, wake_source,
                    active_duration_ms, sleep_duration_s, duty_cycle_pct, avg_current_ma,
                    avg_power_mw, battery_key, runtime_hours, runtime_days, json.dumps(metrics), student_id, now_iso
                ))
                conn.commit()
            finally:
                conn.close()

        return {
            "status": "SUCCESS",
            "simulation_id": simulation_id,
            "metrics": metrics,
            "timestamp": now_iso
        }

    def generate_discharge_curve(
        self,
        battery_key: str = "LIPO_18650_2500MAH",
        avg_current_ma: float = 0.54,
        battery_efficiency: float = 0.85
    ) -> Dict[str, Any]:
        """
        Synthesizes a 10-point non-linear discharge voltage curve vs operating hours.
        Accounts for flat chemical plateau and exponential knee cutoff.
        """
        battery = BATTERY_PRESETS.get(battery_key, BATTERY_PRESETS["LIPO_18650_2500MAH"])
        usable_mah = battery["nominal_mah"] * battery_efficiency
        total_hours = usable_mah / max(0.0001, avg_current_ma)

        points = []
        for soc_pct, base_voltage in LIPO_SOC_VOLTAGE_CURVE:
            # Scale voltage by nominal cell voltage ratio
            scaled_v = round(base_voltage * (battery["voltage_nominal"] / 3.7), 2)
            # Hours elapsed = (1 - SoC / 100) * total_hours
            elapsed_hours = round(total_hours * (1.0 - (soc_pct / 100.0)), 1)
            points.append({
                "soc_pct": soc_pct,
                "cell_voltage_v": scaled_v,
                "elapsed_hours": elapsed_hours,
                "elapsed_days": round(elapsed_hours / 24.0, 1)
            })

        profile_id = f"DIS_{uuid.uuid4().hex[:8].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()

        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT INTO battery_discharge_profiles
                    (profile_id, battery_key, avg_current_ma, total_runtime_hours, discharge_points_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (
                    profile_id, battery_key, avg_current_ma, round(total_hours, 1), json.dumps(points), now_iso
                ))
                conn.commit()
            finally:
                conn.close()

        return {
            "status": "SUCCESS",
            "profile_id": profile_id,
            "battery_key": battery_key,
            "battery_name": battery["name"],
            "total_runtime_hours": round(total_hours, 1),
            "total_runtime_days": round(total_hours / 24.0, 1),
            "discharge_points": points,
            "timestamp": now_iso
        }

    def get_simulation_history(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Retrieves recent low-power energy simulations from the SQLite WAL database."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.execute(
                    "SELECT simulation_id, mcu_target, active_mode, sleep_mode, wake_source, "
                    "duty_cycle_pct, avg_current_ma, avg_power_mw, battery_key, runtime_days, created_at "
                    "FROM low_power_simulations ORDER BY created_at DESC LIMIT ?;",
                    (limit,)
                )
                rows = cur.fetchall()
                history = []
                for r in rows:
                    history.append({
                        "simulation_id": r["simulation_id"],
                        "mcu_target": r["mcu_target"],
                        "active_mode": r["active_mode"],
                        "sleep_mode": r["sleep_mode"],
                        "wake_source": r["wake_source"],
                        "duty_cycle_pct": r["duty_cycle_pct"],
                        "avg_current_ma": r["avg_current_ma"],
                        "avg_power_mw": r["avg_power_mw"],
                        "battery_key": r["battery_key"],
                        "runtime_days": r["runtime_days"],
                        "created_at": r["created_at"]
                    })
                return history
            finally:
                conn.close()

    def export_energy_csv(self) -> str:
        """
        Exports low-power microcontroller sleep mode specifications and battery runtime
        estimates into an RFC-4180 compliant CSV string.
        """
        output = io.StringIO()
        fieldnames = [
            "mcu_target",
            "mcu_name",
            "active_mode",
            "active_current_ma",
            "sleep_mode",
            "sleep_current_ma",
            "battery_name",
            "battery_capacity_mah",
            "runtime_days_10pct_duty",
            "runtime_days_1pct_duty",
            "runtime_days_0_1pct_duty"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        # Generate comparative benchmarks across typical duty cycles
        for mcu_key, mcu_data in MCU_SLEEP_PROFILES.items():
            active_mode_key = list(mcu_data["modes"].keys())[0]
            sleep_mode_key = list(mcu_data["modes"].keys())[-1]
            i_act = mcu_data["modes"][active_mode_key]["current_ma"]
            i_slp = mcu_data["modes"][sleep_mode_key]["current_ma"]

            for bat_key, bat_data in BATTERY_PRESETS.items():
                usable_mah = bat_data["nominal_mah"] * 0.85

                # 10% duty cycle
                i_avg_10 = (i_act * 0.10) + (i_slp * 0.90)
                days_10 = round((usable_mah / i_avg_10) / 24.0, 1)

                # 1% duty cycle
                i_avg_1 = (i_act * 0.01) + (i_slp * 0.99)
                days_1 = round((usable_mah / i_avg_1) / 24.0, 1)

                # 0.1% duty cycle (e.g. 1s wake every 1000s)
                i_avg_01 = (i_act * 0.001) + (i_slp * 0.999)
                days_01 = round((usable_mah / i_avg_01) / 24.0, 1)

                writer.writerow({
                    "mcu_target": mcu_key,
                    "mcu_name": mcu_data["name"],
                    "active_mode": active_mode_key,
                    "active_current_ma": i_act,
                    "sleep_mode": sleep_mode_key,
                    "sleep_current_ma": i_slp,
                    "battery_name": bat_data["name"],
                    "battery_capacity_mah": bat_data["nominal_mah"],
                    "runtime_days_10pct_duty": days_10,
                    "runtime_days_1pct_duty": days_1,
                    "runtime_days_0_1pct_duty": days_01
                })

        return output.getvalue()


# Singleton Instance
low_power_energy_engine = LowPowerEnergyEngine()

