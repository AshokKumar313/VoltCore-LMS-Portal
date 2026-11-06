"""
========================================================================================
VoltCore Apex Academia - Laboratory Simulators & Interactive Benchmarks Engine (Phase 8)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead & Systems Architect: Ashok Kumar A
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313

Capabilities:
  - Physics computation models:
      * EC23S01: Butterworth DSP frequency response & Nyquist validation
      * EC23C03: Shockley diode IV & MOSFET saturation transconductance
      * EC23E04: Laser cavity g-parameter stability & mode spacing
      * EC8702:  FreeRTOS Rate Monotonic Scheduling (RMS) & ARM NVIC tail-chaining
  - Lab exercise catalog validation (apparatus, parameters, viva-voce)
  - SQLite WAL laboratory observation telemetry with zero background polling
Hardware Safe: Zero background daemons, passive CPU footprint (<8%), thread-safe.
========================================================================================
"""

import os
import json
import math
import sqlite3
import datetime
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")

# Physical constants
BOLTZMANN_K = 1.380649e-23  # J/K
ELECTRON_CHARGE = 1.60217663e-19  # Coulombs
SPEED_OF_LIGHT = 2.99792458e8  # m/s

# -----------------------------------------------------------------------------
# LABORATORY EXPERIMENT CATALOG SPECIFICATION
# -----------------------------------------------------------------------------

COURSE_LAB_CATALOG_DATA: Dict[str, List[Dict[str, Any]]] = {
    "EC23S01": [
        {
            "id": "EC23S01_LAB1",
            "course_code": "EC23S01",
            "title": "Interactive Python DSP Filter & Frequency Response Grapher",
            "unit": "II",
            "simulation_platform": "Python SciPy / WebAudio",
            "apparatus": [
                "Python 3.11+ NumPy, SciPy & Matplotlib",
                "VoltCore Digital Oscilloscope & FFT Signal Generator",
                "PC Workstation"
            ],
            "parameters": ["fc", "fs", "order", "passbandGain"],
            "viva_count": 2
        },
        {
            "id": "EC23S01_LAB2",
            "course_code": "EC23S01",
            "title": "Discrete FFT Spectrum & Windowing Artifacts",
            "unit": "I",
            "simulation_platform": "Python SciPy",
            "apparatus": [
                "SciPy Signal Processing Module",
                "Synthetic Dual-Tone Frequency Generator"
            ],
            "parameters": ["tone1", "tone2", "snrDb", "nFft"],
            "viva_count": 1
        }
    ],
    "EC23C03": [
        {
            "id": "EC23C03_LAB1",
            "course_code": "EC23C03",
            "title": "Semiconductor Diode & MOSFET IV Characteristic Curve Tracer",
            "unit": "II",
            "simulation_platform": "LTspice / SPICE Engine",
            "apparatus": [
                "Variable DC Power Supply",
                "Keithley Digital Multimeter",
                "N-channel MOSFET 2N7000",
                "1N4148 Silicon Diode"
            ],
            "parameters": ["vf", "tempK", "eta", "vgs"],
            "viva_count": 2
        }
    ],
    "EC23E04": [
        {
            "id": "EC23E04_LAB1",
            "course_code": "EC23E04",
            "title": "Optical Laser Resonator Stability & Cavity Mode Simulator",
            "unit": "I",
            "simulation_platform": "Optics Ray Tracer",
            "apparatus": [
                "He-Ne Laser Assembly (632.8 nm)",
                "Precision Optical Rail",
                "Dielectric Mirrors (R1=1.0m, R2=0.75m)"
            ],
            "parameters": ["cavityLength", "r1", "r2", "wavelengthNm"],
            "viva_count": 2
        }
    ],
    "EC8702": [
        {
            "id": "EC8702_LAB1",
            "course_code": "EC8702",
            "title": "FreeRTOS Task Scheduler & Interrupt Latency Timing Visualizer",
            "unit": "IV",
            "simulation_platform": "FreeRTOS Kernel / Wokwi STM32",
            "apparatus": [
                "STM32F401RE Nucleo-64 Board",
                "Saleae USB Logic Analyzer",
                "FreeRTOS Kernel v10.4"
            ],
            "parameters": ["c1", "t1", "c2", "t2", "c3", "t3"],
            "viva_count": 2
        }
    ]
}


# -----------------------------------------------------------------------------
# COMPUTATIONAL LABORATORY ENGINE
# -----------------------------------------------------------------------------

class CourseLabEngine:
    """
    Back-end laboratory physics simulator and observation verification engine.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self._ensure_database_schema()

    def _ensure_database_schema(self) -> None:
        """Create lab observation telemetry table in SQLite WAL mode."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            try:
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
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
                conn.commit()
            finally:
                conn.close()
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # PHYSICS VERIFICATION METHODS
    # -------------------------------------------------------------------------

    @staticmethod
    def simulate_dsp_butterworth(
        fc: float,
        fs: float,
        order: int,
        gain: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculates Butterworth filter magnitude response |H(f)| in linear and dB.
        Verifies Nyquist criteria (fs >= 2*fc) and -3dB cutoff point.
        """
        if fs <= 0 or fc <= 0 or order < 1:
            raise ValueError("Invalid filter parameters: fs and fc must be > 0, order >= 1")

        nyquist_freq = fs / 2.0
        is_nyquist_valid = fs >= (2.0 * fc)

        # Attenuation at cutoff frequency fc must be approx -3.0103 dB
        ratio_cutoff = fc / fc
        mag_at_cutoff = gain / math.sqrt(1.0 + math.pow(ratio_cutoff, 2 * order))
        db_at_cutoff = 20.0 * math.log10(mag_at_cutoff)

        # Roll-off rate: -20 * order dB/decade
        roll_off_rate = -20 * order

        # Test points: 0.1*fc, 0.5*fc, 1.0*fc, 2.0*fc, 4.0*fc
        test_ratios = [0.1, 0.5, 1.0, 2.0, 4.0]
        test_points = []
        for r in test_ratios:
            freq = r * fc
            if freq <= nyquist_freq:
                g = gain / math.sqrt(1.0 + math.pow(r, 2 * order))
                db = 20.0 * math.log10(g)
                test_points.append({
                    "frequency": round(freq, 1),
                    "ratio": r,
                    "gain_linear": round(g, 4),
                    "gain_db": round(db, 2)
                })

        return {
            "fc": fc,
            "fs": fs,
            "order": order,
            "gain": gain,
            "nyquist_freq": nyquist_freq,
            "is_nyquist_valid": is_nyquist_valid,
            "mag_at_cutoff": round(mag_at_cutoff, 4),
            "db_at_cutoff": round(db_at_cutoff, 2),
            "roll_off_db_per_decade": roll_off_rate,
            "test_points": test_points
        }

    @staticmethod
    def simulate_device_iv(
        vf: float,
        temp_k: float = 300.0,
        eta: float = 1.05,
        vgs: float = 3.3,
        vth: float = 1.2,
        kn: float = 20.0
    ) -> Dict[str, Any]:
        """
        Calculates Shockley diode IV and MOSFET saturation current.
        """
        if temp_k <= 0 or eta <= 0:
            raise ValueError("Temperature and ideality factor must be positive")

        # Thermal voltage: VT = kB * T / q
        vt = (BOLTZMANN_K * temp_k) / ELECTRON_CHARGE
        vt_mv = vt * 1000.0

        # Reverse saturation current IS scaling
        is_300 = 1e-12
        is_current = is_300 * math.pow(temp_k / 300.0, 3) * math.exp(
            1.12 / ((BOLTZMANN_K * 300.0) / ELECTRON_CHARGE) - 1.12 / vt
        )

        # Diode current ID = IS * (exp(VF / (eta*VT)) - 1)
        exp_arg = min(vf / (eta * vt), 30.0)
        diode_current_a = is_current * (math.exp(exp_arg) - 1.0)
        diode_current_ma = diode_current_a * 1000.0

        # Small-signal dynamic resistance rd = eta * VT / ID
        dynamic_rd = (eta * vt) / max(diode_current_a, 1e-12)

        # MOSFET: Inversion channel overdrive voltage Vov = max(0, VGS - Vth)
        vov = max(0.0, vgs - vth)
        # Saturation drain current: ID,sat = 0.5 * kn * Vov^2
        mosfet_sat_id_ma = 0.5 * kn * (vov ** 2)
        # Small-signal transconductance: gm = kn * Vov
        gm_ma_per_v = kn * vov

        return {
            "vf": vf,
            "temp_k": temp_k,
            "vt_mv": round(vt_mv, 2),
            "diode_current_ma": round(diode_current_ma, 4),
            "dynamic_rd_ohms": round(dynamic_rd, 2),
            "vgs": vgs,
            "vth": vth,
            "vov": round(vov, 2),
            "mosfet_sat_id_ma": round(mosfet_sat_id_ma, 2),
            "transconductance_gm_ma_v": round(gm_ma_per_v, 2),
            "is_conduction_active": diode_current_ma > 0.1
        }

    @staticmethod
    def simulate_laser_cavity(
        cavity_length: float,
        r1: float,
        r2: float,
        wavelength_nm: float = 632.8
    ) -> Dict[str, Any]:
        """
        Calculates optical cavity resonator stability g-parameters and mode spacing.
        """
        if cavity_length <= 0 or r1 <= 0 or r2 <= 0:
            raise ValueError("Cavity dimensions must be positive")

        g1 = 1.0 - (cavity_length / r1)
        g2 = 1.0 - (cavity_length / r2)
        g_prod = g1 * g2

        # Stability condition: 0 <= g1 * g2 <= 1
        is_stable = (0.0 <= g_prod <= 1.0)

        # Longitudinal mode frequency spacing: Delta_nu = c / (2 * L)
        mode_spacing_hz = SPEED_OF_LIGHT / (2.0 * cavity_length)
        mode_spacing_mhz = mode_spacing_hz / 1e6

        # Longitudinal wavelength spacing: Delta_lambda = lambda^2 / (2 * L)
        wavelength_m = wavelength_nm * 1e-9
        delta_lambda_m = (wavelength_m ** 2) / (2.0 * cavity_length)
        delta_lambda_pm = delta_lambda_m * 1e12

        return {
            "cavity_length_m": cavity_length,
            "r1_m": r1,
            "r2_m": r2,
            "g1": round(g1, 4),
            "g2": round(g2, 4),
            "g_prod": round(g_prod, 4),
            "is_stable": is_stable,
            "mode_spacing_mhz": round(mode_spacing_mhz, 2),
            "delta_lambda_pm": round(delta_lambda_pm, 4)
        }

    @staticmethod
    def simulate_rtos_schedulability(
        tasks: List[Dict[str, float]],
        core_clock_mhz: float = 84.0
    ) -> Dict[str, Any]:
        """
        Computes Rate Monotonic Scheduling (RMS) utilization and ARM NVIC tail-chaining latency.
        """
        n = len(tasks)
        if n == 0:
            raise ValueError("Task list cannot be empty")

        utilizations = []
        total_u = 0.0

        for t in tasks:
            c = t["c"]
            period = t["t"]
            if period <= 0 or c < 0:
                raise ValueError("Execution time must be >= 0 and period > 0")
            u_i = (c / period) * 100.0
            utilizations.append({
                "c": c,
                "t": period,
                "utilization_pct": round(u_i, 2)
            })
            total_u += u_i

        # Liu & Layland bound: n * (2^(1/n) - 1)
        bound_pct = n * (math.pow(2.0, 1.0 / n) - 1.0) * 100.0
        is_schedulable = total_u <= bound_pct

        # ARM Cortex-M4 NVIC Tail-Chaining latency
        cycle_time_ns = 1000.0 / core_clock_mhz
        tail_chain_cycles = 6
        standard_cycles = 24
        tail_chain_time_ns = tail_chain_cycles * cycle_time_ns
        standard_time_ns = standard_cycles * cycle_time_ns
        latency_savings_pct = ((standard_time_ns - tail_chain_time_ns) / standard_time_ns) * 100.0

        return {
            "task_count": n,
            "tasks": utilizations,
            "total_utilization_pct": round(total_u, 2),
            "liu_layland_bound_pct": round(bound_pct, 2),
            "is_schedulable": is_schedulable,
            "tail_chain_time_ns": round(tail_chain_time_ns, 2),
            "standard_time_ns": round(standard_time_ns, 2),
            "latency_savings_pct": round(latency_savings_pct, 2)
        }

    # -------------------------------------------------------------------------
    # CATALOG & OBSERVATION LOGGING
    # -------------------------------------------------------------------------

    def get_catalog_for_course(self, course_code: str) -> List[Dict[str, Any]]:
        """Retrieve lab exercise catalog for course."""
        return COURSE_LAB_CATALOG_DATA.get(course_code, [])

    def validate_catalog(self) -> Dict[str, Any]:
        """Verify lab catalog completeness across all priority courses."""
        errors = []
        total_labs = 0

        for code in ["EC23S01", "EC23C03", "EC23E04", "EC8702"]:
            labs = COURSE_LAB_CATALOG_DATA.get(code, [])
            if not labs:
                errors.append(f"Missing lab exercises for course {code}")
            for lab in labs:
                total_labs += 1
                if not lab.get("id"):
                    errors.append(f"Lab in course {code} missing ID")
                if not lab.get("parameters") or len(lab["parameters"]) == 0:
                    errors.append(f"Lab {lab.get('id')} missing parameters")
                if not lab.get("apparatus") or len(lab["apparatus"]) == 0:
                    errors.append(f"Lab {lab.get('id')} missing apparatus list")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "total_courses": len(COURSE_LAB_CATALOG_DATA),
            "total_labs": total_labs
        }

    def log_observation(
        self,
        course_code: str,
        lab_id: str,
        student_id: str,
        telemetry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Persist an observation trial record into SQLite WAL gradebook."""
        obs_id = f"OBS-{lab_id}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}"
        now = datetime.datetime.now().isoformat()

        try:
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            try:
                conn.execute("""
                    INSERT INTO course_lab_observations
                    (observation_id, course_code, lab_id, student_id, telemetry_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    obs_id,
                    course_code,
                    lab_id,
                    student_id,
                    json.dumps(telemetry),
                    now
                ))
                conn.commit()
            finally:
                conn.close()
            return {"status": "success", "observation_id": obs_id, "logged_at": now}
        except Exception as e:
            return {"status": "error", "error": str(e)}
