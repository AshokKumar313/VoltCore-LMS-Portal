"""
========================================================================================
VoltCore Apex Academia - Analog & Communication Engineering Center
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/analog_comm_engine.py
Course Codes: EC3451 - Linear Integrated Circuits | EC3491 - Communication Systems
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  High-performance, lightweight analog electronics and communication systems solver:
    1. Analog Active/Passive Filter Calculations (RC, LC, Sallen-Key 2nd-Order).
    2. Transistor DC Operating Point / Q-Point Solver (BJT & MOSFET Bias Networks).
    3. Op-Amp Closed-Loop Gain, Bandwidth, Slew-Rate, and Input Offset Models.
    4. RF Transmission Line Impedance, Reflection Coefficient, and VSWR Calculator.
    5. Modulation Parameters (AM, FM, Shannon Channel Capacity, Nyquist Sampling).
    6. SQLite WAL-backed data engine with sub-3ms latency and passive thermal profile.
========================================================================================
"""

import os
import time
import math
import json
import sqlite3
import threading
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")

# Default demo student
DEFAULT_STUDENT_ID = "2023MITEC042"

# Curriculum Benchmark Presets for EC3451 & EC3491
ANALOG_COMM_PRESETS = [
    {
        "preset_id": "PRESET_SALLEN_KEY_1KHZ",
        "title": "2nd-Order Sallen-Key Butterworth Low-Pass Filter",
        "subject_code": "EC3451",
        "category": "FILTER",
        "description": "Unity-gain Sallen-Key low-pass filter designed for 1 kHz cutoff with Q=0.707 (maximally flat).",
        "parameters": {
            "filter_type": "SALLEN_KEY_LPF",
            "R1": 15900,
            "R2": 15900,
            "C1": 1.414e-8,
            "C2": 7.07e-9,
            "gain": 1.0
        }
    },
    {
        "preset_id": "PRESET_BJT_VOLTAGE_DIVIDER",
        "title": "BJT Voltage Divider Bias (Active Region Q-Point)",
        "subject_code": "EC3451",
        "category": "TRANSISTOR",
        "description": "Standard 12V NPN transistor amplifier stage operating in the linear active region (Lab 304 spec).",
        "parameters": {
            "transistor_type": "BJT_NPN",
            "Vcc": 12.0,
            "R1": 39000.0,
            "R2": 10000.0,
            "Rc": 2200.0,
            "Re": 1000.0,
            "beta": 150.0,
            "Vbe": 0.7
        }
    },
    {
        "preset_id": "PRESET_MOSFET_SELF_BIAS",
        "title": "MOSFET Voltage Divider Bias (Saturation Region)",
        "subject_code": "EC3451",
        "category": "TRANSISTOR",
        "description": "N-channel enhancement MOSFET biased in saturation for analog linear amplification.",
        "parameters": {
            "transistor_type": "MOSFET_NMOS",
            "Vdd": 15.0,
            "R1": 1000000.0,
            "R2": 500000.0,
            "Rd": 3300.0,
            "Rs": 1500.0,
            "Vth": 2.0,
            "kn": 1.5e-3
        }
    },
    {
        "preset_id": "PRESET_OPAMP_INVERTING_LM741",
        "title": "LM741 Inverting Amplifier (Av = -10)",
        "subject_code": "EC3451",
        "category": "OPAMP",
        "description": "Inverting operational amplifier stage with 10k input, 100k feedback, and GBW=1MHz.",
        "parameters": {
            "opamp_model": "LM741",
            "config": "INVERTING",
            "Rin": 10000.0,
            "Rf": 100000.0,
            "GBW": 1000000.0,
            "SR": 500000.0,
            "Vpeak": 5.0,
            "Vio": 0.002
        }
    },
    {
        "preset_id": "PRESET_TXLINE_COAX_50OHM",
        "title": "50-Ohm Coaxial Transmission Line with Mismatched Load",
        "subject_code": "EC3491",
        "category": "TXLINE",
        "description": "50-ohm RF feedline terminated in a 75-ohm complex antenna impedance.",
        "parameters": {
            "Z0": 50.0,
            "ZL_real": 75.0,
            "ZL_imag": 25.0
        }
    },
    {
        "preset_id": "PRESET_FM_BROADCAST_CARSON",
        "title": "Commercial FM Broadcast Carson's Bandwidth",
        "subject_code": "EC3491",
        "category": "MODULATION",
        "description": "Standard 75 kHz peak frequency deviation commercial FM broadcast signal at fm=15 kHz.",
        "parameters": {
            "modulation_type": "FM",
            "delta_f": 75000.0,
            "fm": 15000.0,
            "carrier_freq": 100.0e6,
            "Pc": 1000.0
        }
    }
]


class AnalogCommEngine:
    """
    High-performance native Python analog electronics & communication solver.
    Zero-bloat execution engineered for cool thermal profiles on HP Victus.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_db(self) -> None:
        """Initializes tables for saved analog calculations and curriculum presets."""
        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS analog_circuit_calculations (
                    calc_id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subject_code TEXT DEFAULT 'EC3451',
                    parameters_json TEXT NOT NULL,
                    results_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS analog_comm_presets (
                    preset_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    subject_code TEXT DEFAULT 'EC3451',
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    parameters_json TEXT NOT NULL
                );
            """)

            cur.execute("CREATE INDEX IF NOT EXISTS idx_ana_calc_student ON analog_circuit_calculations(student_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_ana_pres_cat ON analog_comm_presets(category);")

            conn.commit()
            self._seed_presets(conn)
            conn.close()

    def _seed_presets(self, conn: sqlite3.Connection) -> None:
        """Seeds standard EC3451/EC3491 curriculum benchmark problems."""
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM analog_comm_presets;")
        if cur.fetchone()[0] == 0:
            for p in ANALOG_COMM_PRESETS:
                cur.execute("""
                    INSERT OR REPLACE INTO analog_comm_presets
                    (preset_id, title, subject_code, category, description, parameters_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    p["preset_id"],
                    p["title"],
                    p["subject_code"],
                    p["category"],
                    p["description"],
                    json.dumps(p["parameters"])
                ))
            conn.commit()

    # ====================================================================================
    # 1. ANALOG ACTIVE & PASSIVE FILTERS
    # ====================================================================================

    def calculate_filter(
        self,
        filter_type: str = "RC_LPF",
        R: float = 10000.0,
        C: float = 1.0e-8,
        L: float = 1.0e-3,
        R2: Optional[float] = None,
        C2: Optional[float] = None,
        gain: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculates cutoff frequencies, damping ratio, Q-factor, and frequency response points.
        Supports: RC_LPF, RC_HPF, LC_RESONANT, SALLEN_KEY_LPF, SALLEN_KEY_HPF.
        """
        filter_type = filter_type.upper().strip()

        try:
            if filter_type in ("RC_LPF", "RC_HPF"):
                if R <= 0 or C <= 0:
                    return {"status": "ERROR", "message": "Resistance and Capacitance must be positive"}
                fc = 1.0 / (2.0 * math.pi * R * C)
                tau = R * C
                q_factor = 0.5  # 1st order
                order = 1
                formula = "fc = 1 / (2 * pi * R * C)"
                desc = "1st-order passive RC filter providing -20 dB/decade roll-off."

            elif filter_type == "LC_RESONANT":
                if L <= 0 or C <= 0:
                    return {"status": "ERROR", "message": "Inductance and Capacitance must be positive"}
                fc = 1.0 / (2.0 * math.pi * math.sqrt(L * C))
                tau = math.sqrt(L * C)
                z0 = math.sqrt(L / C)
                q_factor = z0 / max(R, 0.001)
                order = 2
                formula = "f0 = 1 / (2 * pi * sqrt(L * C)), Q = (sqrt(L/C)) / R"
                desc = "2nd-order LC resonant tank providing -40 dB/decade roll-off."

            elif filter_type in ("SALLEN_KEY_LPF", "SALLEN_KEY_HPF"):
                r1 = R
                r2 = R2 if (R2 and R2 > 0) else R
                c1 = C
                c2 = C2 if (C2 and C2 > 0) else C
                fc = 1.0 / (2.0 * math.pi * math.sqrt(r1 * r2 * c1 * c2))
                tau = math.sqrt(r1 * r2 * c1 * c2)
                # Sallen-Key Q-factor calculation
                denom = (c2 * (r1 + r2) + r1 * c1 * (1.0 - gain))
                q_factor = math.sqrt(r1 * r2 * c1 * c2) / max(abs(denom), 1e-12)
                order = 2
                formula = "fc = 1 / (2 * pi * sqrt(R1 * R2 * C1 * C2))"
                desc = f"2nd-order active Sallen-Key Butterworth filter with Av={gain}."

            else:
                return {"status": "ERROR", "message": f"Unsupported filter type: {filter_type}"}

            # Generate Bode Magnitude sample points (0.1fc, 0.5fc, fc, 2fc, 10fc)
            freq_points = [0.1 * fc, 0.5 * fc, 1.0 * fc, 2.0 * fc, 10.0 * fc]
            bode_points = []
            for f in freq_points:
                ratio = f / max(fc, 1e-12)
                if order == 1:
                    mag_db = -10.0 * math.log10(1.0 + ratio**2)
                else: # 2nd order
                    mag_db = -10.0 * math.log10((1.0 - ratio**2)**2 + (ratio / max(q_factor, 0.01))**2)
                bode_points.append({
                    "frequency_hz": round(f, 2),
                    "magnitude_db": round(mag_db, 2)
                })

            return {
                "status": "SUCCESS",
                "filter_type": filter_type,
                "order": order,
                "cutoff_frequency_hz": round(fc, 3),
                "time_constant_seconds": f"{tau:.6e}",
                "q_factor": round(q_factor, 3),
                "damping_ratio": round(1.0 / (2.0 * max(q_factor, 0.01)), 3),
                "formula": formula,
                "description": desc,
                "bode_response": bode_points
            }
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    # ====================================================================================
    # 2. TRANSISTOR DC OPERATING POINT (BJT & MOSFET)
    # ====================================================================================

    def calculate_transistor_bias(
        self,
        transistor_type: str = "BJT_NPN",
        Vcc: float = 12.0,
        R1: float = 39000.0,
        R2: float = 10000.0,
        Rc: float = 2200.0,
        Re: float = 1000.0,
        beta: float = 150.0,
        Vbe: float = 0.7,
        Vth: float = 2.0,
        kn: float = 1.5e-3
    ) -> Dict[str, Any]:
        """
        Solves DC Q-point operating conditions for Voltage Divider Biased BJT or MOSFET.
        Identifies Active, Saturation, and Cutoff operating boundaries.
        """
        transistor_type = transistor_type.upper().strip()

        try:
            if transistor_type in ("BJT_NPN", "BJT"):
                # Thevenin equivalent
                v_th = Vcc * (R2 / (R1 + R2))
                r_th = (R1 * R2) / (R1 + R2)

                if v_th < Vbe:
                    return {
                        "status": "SUCCESS",
                        "transistor_type": "BJT_NPN",
                        "operating_region": "CUTOFF",
                        "V_TH": round(v_th, 3),
                        "R_TH": round(r_th, 1),
                        "IB_microamps": 0.0,
                        "IC_milliamps": 0.0,
                        "IE_milliamps": 0.0,
                        "VCE_volts": round(Vcc, 3),
                        "safe_for_analog": False,
                        "analysis": "Base-emitter junction is reverse/zero biased (V_TH < Vbe). Transistor is OFF."
                    }

                # Active Region assumption
                ib = (v_th - Vbe) / (r_th + (beta + 1.0) * Re)
                ic = beta * ib
                ie = (beta + 1.0) * ib

                vc = Vcc - ic * Rc
                ve = ie * Re
                vce = vc - ve

                # Check Saturation boundary (Vce < 0.2V)
                if vce < 0.2:
                    region = "SATURATION"
                    ic_sat = (Vcc - 0.2) / (Rc + Re)
                    vce = 0.2
                    safe = False
                    analysis = "Collector-base junction forward biased (VCE < 0.2V). Saturated; nonlinear."
                else:
                    region = "ACTIVE"
                    safe = True
                    analysis = "Q-point comfortably in active linear region. Ideal for small-signal amplification."

                return {
                    "status": "SUCCESS",
                    "transistor_type": "BJT_NPN",
                    "operating_region": region,
                    "V_TH": round(v_th, 3),
                    "R_TH": round(r_th, 1),
                    "IB_microamps": round(ib * 1e6, 2),
                    "IC_milliamps": round(ic * 1e3, 3),
                    "IE_milliamps": round(ie * 1e3, 3),
                    "VC_volts": round(vc, 3),
                    "VE_volts": round(ve, 3),
                    "VCE_volts": round(vce, 3),
                    "safe_for_analog": safe,
                    "analysis": analysis
                }

            elif transistor_type in ("MOSFET_NMOS", "MOSFET"):
                # Gate Voltage
                vg = Vcc * (R2 / (R1 + R2))
                if vg < Vth:
                    return {
                        "status": "SUCCESS",
                        "transistor_type": "MOSFET_NMOS",
                        "operating_region": "CUTOFF",
                        "VG_volts": round(vg, 3),
                        "ID_milliamps": 0.0,
                        "VDS_volts": round(Vcc, 3),
                        "safe_for_analog": False,
                        "analysis": "Gate-source voltage below threshold Vth. Channel not formed."
                    }

                # Solve quadratic equation for Saturation:
                # ID = 0.5 * kn * (VG - ID*Rs - Vth)^2
                # Let Vov = VG - Vth, ID = 0.5 * kn * (Vov - ID*Rs)^2
                # ID = 0.5 * kn * (Vov^2 - 2*Vov*Rs*ID + Rs^2 * ID^2)
                # 0.5*kn*Rs^2 * ID^2 - (1 + kn*Vov*Rs) * ID + 0.5*kn*Vov^2 = 0
                v_ov = vg - Vth
                a = 0.5 * kn * (Re**2)
                b = -(1.0 + kn * v_ov * Re)
                c = 0.5 * kn * (v_ov**2)

                disc = b**2 - 4.0 * a * c
                if disc < 0:
                    id_val = 0.0
                else:
                    id_val = (-b - math.sqrt(disc)) / (2.0 * a) if a > 0 else (c / abs(b))

                vgs = vg - id_val * Re
                vds = Vcc - id_val * (Rc + Re)

                is_sat = vds >= (vgs - Vth)
                region = "SATURATION" if is_sat else "TRIODE / LINEAR"

                return {
                    "status": "SUCCESS",
                    "transistor_type": "MOSFET_NMOS",
                    "operating_region": region,
                    "VG_volts": round(vg, 3),
                    "VGS_volts": round(vgs, 3),
                    "ID_milliamps": round(id_val * 1e3, 3),
                    "VDS_volts": round(vds, 3),
                    "Vov_volts": round(vgs - Vth, 3),
                    "safe_for_analog": is_sat,
                    "analysis": "Biased in Saturation (Pinch-off); constant current for linear amplification." if is_sat else "Triode region; operates as voltage-controlled resistor."
                }
            else:
                return {"status": "ERROR", "message": f"Unsupported transistor type: {transistor_type}"}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    # ====================================================================================
    # 3. OP-AMP & LINEAR IC PARAMETERS
    # ====================================================================================

    def calculate_opamp(
        self,
        config: str = "INVERTING",
        Rin: float = 10000.0,
        Rf: float = 100000.0,
        GBW: float = 1000000.0,
        SR: float = 500000.0,
        Vpeak: float = 5.0,
        Vio: float = 0.002,
        Iio: float = 2.0e-8
    ) -> Dict[str, Any]:
        """
        Calculates closed-loop voltage gain, bandwidth, slew rate full-power frequency,
        and output offset voltage error.
        """
        config = config.upper().strip()

        try:
            if config == "INVERTING":
                av = -(Rf / max(Rin, 1e-6))
                closed_loop_gain = abs(av)
                formula = "Av = -Rf / Rin"
            elif config in ("NON_INVERTING", "NONINVERTING"):
                av = 1.0 + (Rf / max(Rin, 1e-6))
                closed_loop_gain = av
                formula = "Av = 1 + (Rf / R1)"
            else:
                return {"status": "ERROR", "message": f"Unsupported op-amp config: {config}"}

            # Bandwidth: f_3dB = GBW / closed_loop_gain
            bandwidth_hz = GBW / max(closed_loop_gain, 1.0)

            # Slew Rate full-power maximum frequency: f_max = SR / (2 * pi * Vp)
            f_max_slew = SR / (2.0 * math.pi * max(Vpeak, 0.01))

            # Total Output Offset Error
            # Vout,offset = (1 + Rf/Rin) * Vio + Rf * Iio
            noise_gain = 1.0 + (Rf / max(Rin, 1e-6))
            vout_offset = noise_gain * Vio + Rf * Iio

            return {
                "status": "SUCCESS",
                "config": config,
                "voltage_gain": round(av, 3),
                "voltage_gain_db": round(20.0 * math.log10(abs(av)), 2),
                "closed_loop_bandwidth_hz": round(bandwidth_hz, 1),
                "slew_rate_v_per_us": round(SR / 1e6, 2),
                "full_power_bandwidth_hz": round(f_max_slew, 1),
                "output_offset_mv": round(vout_offset * 1e3, 3),
                "formula": formula
            }
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    # ====================================================================================
    # 4. TRANSMISSION LINES & RF IMPEDANCE
    # ====================================================================================

    def calculate_txline(
        self,
        Z0: float = 50.0,
        ZL_real: float = 75.0,
        ZL_imag: float = 0.0
    ) -> Dict[str, Any]:
        """
        Computes reflection coefficient magnitude/phase, VSWR, return loss, and matching status.
        """
        try:
            # Complex impedance reflection: Gamma = (ZL - Z0) / (ZL + Z0)
            z_num = complex(ZL_real - Z0, ZL_imag)
            z_den = complex(ZL_real + Z0, ZL_imag)
            gamma = z_num / z_den

            mag_gamma = abs(gamma)
            phase_deg = math.degrees(math.atan2(gamma.imag, gamma.real))

            # VSWR: (1 + |Gamma|) / (1 - |Gamma|)
            if mag_gamma >= 1.0:
                vswr = 999.0  # Infinite
                return_loss_db = 0.0
            else:
                vswr = (1.0 + mag_gamma) / (1.0 - mag_gamma)
                return_loss_db = -20.0 * math.log10(max(mag_gamma, 1e-9))

            # Power Delivered %: (1 - |Gamma|^2) * 100
            power_delivered_pct = (1.0 - mag_gamma**2) * 100.0

            matched = vswr <= 1.5

            return {
                "status": "SUCCESS",
                "characteristic_impedance_z0": Z0,
                "load_impedance": f"{ZL_real} + j{ZL_imag} Ω",
                "reflection_coefficient_mag": round(mag_gamma, 4),
                "reflection_coefficient_phase_deg": round(phase_deg, 2),
                "vswr": round(vswr, 3),
                "return_loss_db": round(return_loss_db, 2),
                "power_delivered_pct": round(power_delivered_pct, 2),
                "is_well_matched": matched
            }
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    # ====================================================================================
    # 5. MODULATION SYSTEMS & INFORMATION THEORY
    # ====================================================================================

    def calculate_modulation(
        self,
        modulation_type: str = "AM",
        carrier_freq: float = 1.0e6,
        mod_freq: float = 5000.0,
        mod_index: float = 0.8,
        delta_f: float = 75000.0,
        Pc: float = 100.0,
        snr_db: float = 20.0,
        channel_bandwidth: float = 100000.0
    ) -> Dict[str, Any]:
        """
        Solves modulation parameters: AM power distribution, FM Carson's bandwidth,
        Nyquist sampling theorem limits, and Shannon channel capacity.
        """
        modulation_type = modulation_type.upper().strip()

        try:
            # Universal Nyquist Sampling Minimum Rate
            nyquist_rate_hz = 2.0 * mod_freq
            nyquist_interval_seconds = f"{1.0 / nyquist_rate_hz:.6e}"

            # Universal Shannon Channel Capacity
            snr_linear = 10.0 ** (snr_db / 10.0)
            shannon_capacity_bps = channel_bandwidth * math.log2(1.0 + snr_linear)

            if modulation_type == "AM":
                mu = max(0.0, min(2.0, mod_index))
                # Total Transmitted Power: Pt = Pc * (1 + mu^2 / 2)
                pt = Pc * (1.0 + (mu**2) / 2.0)
                psb = pt - Pc  # Sideband power
                efficiency_pct = ((mu**2) / (2.0 + mu**2)) * 100.0
                bw = 2.0 * mod_freq

                return {
                    "status": "SUCCESS",
                    "modulation_type": "AM",
                    "modulation_index": mu,
                    "carrier_power_watts": Pc,
                    "total_power_watts": round(pt, 2),
                    "sideband_power_watts": round(psb, 2),
                    "efficiency_pct": round(efficiency_pct, 2),
                    "transmission_bandwidth_hz": round(bw, 1),
                    "nyquist_rate_hz": round(nyquist_rate_hz, 1),
                    "shannon_capacity_kbps": round(shannon_capacity_bps / 1e3, 2),
                    "formula": "Pt = Pc * (1 + mu^2 / 2), BW = 2 * fm"
                }

            elif modulation_type == "FM":
                # Beta = delta_f / fm
                beta = delta_f / max(mod_freq, 1.0)
                # Carson's Rule Bandwidth: 2 * (delta_f + fm)
                carson_bw = 2.0 * (delta_f + mod_freq)

                return {
                    "status": "SUCCESS",
                    "modulation_type": "FM",
                    "frequency_deviation_hz": delta_f,
                    "modulation_index_beta": round(beta, 3),
                    "carson_bandwidth_hz": round(carson_bw, 1),
                    "carrier_frequency_mhz": round(carrier_freq / 1e6, 3),
                    "nyquist_rate_hz": round(nyquist_rate_hz, 1),
                    "shannon_capacity_kbps": round(shannon_capacity_bps / 1e3, 2),
                    "formula": "Carson's BW = 2 * (delta_f + fm) = 2 * fm * (beta + 1)"
                }
            else:
                return {"status": "ERROR", "message": f"Unsupported modulation type: {modulation_type}"}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    # ====================================================================================
    # 6. PRESETS & SAVED CALCULATION LEDGER
    # ====================================================================================

    def get_presets(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns standard curriculum problem presets for EC3451 & EC3491."""
        conn = self._get_connection()
        cur = conn.cursor()
        if category:
            cur.execute("""
                SELECT preset_id, title, subject_code, category, description, parameters_json
                FROM analog_comm_presets
                WHERE category = ?
                ORDER BY subject_code, title;
            """, (category.upper(),))
        else:
            cur.execute("""
                SELECT preset_id, title, subject_code, category, description, parameters_json
                FROM analog_comm_presets
                ORDER BY subject_code, title;
            """)
        raw = cur.fetchall()
        conn.close()

        presets = []
        for r in raw:
            p = dict(r)
            try:
                p["parameters"] = json.loads(p.pop("parameters_json") or "{}")
            except Exception:
                p["parameters"] = {}
            presets.append(p)
        return presets

    def save_calculation(
        self,
        student_id: str,
        title: str,
        category: str,
        parameters: Dict[str, Any],
        results: Dict[str, Any],
        subject_code: str = "EC3451"
    ) -> Dict[str, Any]:
        """Saves a verified circuit calculation to the student portfolio ledger."""
        calc_id = f"ANA_{int(time.time() * 1000)}"
        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO analog_circuit_calculations
                (calc_id, student_id, title, category, subject_code, parameters_json, results_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                calc_id,
                student_id or DEFAULT_STUDENT_ID,
                title.strip() or "Untitled Analog Computation",
                category.upper(),
                subject_code.upper(),
                json.dumps(parameters),
                json.dumps(results),
                datetime_now_iso()
            ))
            conn.commit()
            conn.close()

        return {"status": "SUCCESS", "calc_id": calc_id, "title": title}

    def get_saved_calculations(self, student_id: str = DEFAULT_STUDENT_ID) -> List[Dict[str, Any]]:
        """Retrieves saved analog/comm calculations for a student."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT calc_id, student_id, title, category, subject_code, parameters_json, results_json, created_at
            FROM analog_circuit_calculations
            WHERE student_id = ?
            ORDER BY created_at DESC;
        """, (student_id,))
        raw = cur.fetchall()
        conn.close()

        items = []
        for r in raw:
            it = dict(r)
            try:
                it["parameters"] = json.loads(it.pop("parameters_json") or "{}")
                it["results"] = json.loads(it.pop("results_json") or "{}")
            except Exception:
                it["parameters"] = {}
                it["results"] = {}
            items.append(it)
        return items

    def get_overview(self, student_id: str = DEFAULT_STUDENT_ID) -> Dict[str, Any]:
        """High-level metrics for dashboard cards (< 3ms response time)."""
        presets = self.get_presets()
        saved = self.get_saved_calculations(student_id)
        return {
            "student_id": student_id,
            "curriculum_presets_count": len(presets),
            "saved_calculations_count": len(saved),
            "supported_solvers": ["Active Filters", "BJT/MOSFET Bias", "Op-Amp Models", "RF Transmission Lines", "Modulation Theory"],
            "target_regulations": ["EC3451 Linear Integrated Circuits", "EC3491 Communication Systems"],
            "recent_presets": presets[:3],
            "recent_calculations": saved[:3]
        }


def datetime_now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


# Global Singleton for system-wide low-overhead dispatch
analog_comm_engine = AnalogCommEngine()
