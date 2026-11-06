"""
========================================================================================
VoltCore Apex Academia - Phase D: Analog Electronics & Semiconductor Tools (Features 241–250)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Features:
  - Feature 241: PN Junction Learning Explorer (Vbi, W, peak E-field, junction cap)
  - Feature 242: Diode Characteristics Plotter (Shockley equation, dynamic resistance)
  - Feature 243: Zener Voltage Regulator Calculator (Rs, Iz, line/load regulation)
  - Feature 244: BJT Configuration Comparison Matrix (CB, CE, CC parameters)
  - Feature 245: MOSFET Characteristics Plotter (Cutoff, Triode, Saturation, gm, ro)
  - Feature 246: Small-Signal Amplifier Gain Calculator (CE Av, Rin, Rout, 3dB cutoff)
  - Feature 247: Op-Amp Configuration Explorer (Inverting, Non-inv, Diff, Slew Rate)
  - Feature 248: RC/RL Transient Response Calculator (Time constant tau, step curves)
  - Feature 249: RLC Resonance Calculator (Series/Parallel f0, Q, BW, damping zeta)
  - Feature 250: Semiconductor Material Comparison Tool (Si, Ge, GaAs, GaN, SiC)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU usage.
========================================================================================
"""

import os
import math
import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")

# Physical Constants
Q_ELEC = 1.602176634e-19       # Electron charge (Coulombs)
K_BOLTZ = 1.380649e-23         # Boltzmann constant (J/K)
EPSILON_0 = 8.854187817e-14    # Vacuum permittivity (F/cm)
T_ROOM = 300.0                 # Room temperature in Kelvin
VT_ROOM = (K_BOLTZ * T_ROOM) / Q_ELEC  # ~0.02585 V (25.85 mV)

# Curated Semiconductor Materials Database (Feature 250)
SEMICONDUCTOR_MATERIALS: Dict[str, Dict[str, Any]] = {
    "Silicon": {
        "symbol": "Si",
        "bandgap_ev": 1.12,
        "bandgap_type": "Indirect",
        "relative_permittivity": 11.7,
        "electron_mobility": 1400.0,   # cm^2 / V*s
        "hole_mobility": 450.0,        # cm^2 / V*s
        "breakdown_field_mv_cm": 0.3,  # MV/cm
        "thermal_conductivity": 1.5,   # W/cm*K
        "intrinsic_ni_cm3": 1.5e10,    # cm^-3
        "typical_knee_voltage": 0.7,   # V
        "applications": "VLSI logic, Microprocessors, General CMOS"
    },
    "Germanium": {
        "symbol": "Ge",
        "bandgap_ev": 0.66,
        "bandgap_type": "Indirect",
        "relative_permittivity": 16.0,
        "electron_mobility": 3900.0,
        "hole_mobility": 1900.0,
        "breakdown_field_mv_cm": 0.1,
        "thermal_conductivity": 0.6,
        "intrinsic_ni_cm3": 2.4e13,
        "typical_knee_voltage": 0.3,
        "applications": "High-speed detectors, Infrared optics, Cryogenic electronics"
    },
    "Gallium Arsenide": {
        "symbol": "GaAs",
        "bandgap_ev": 1.42,
        "bandgap_type": "Direct",
        "relative_permittivity": 12.9,
        "electron_mobility": 8500.0,
        "hole_mobility": 400.0,
        "breakdown_field_mv_cm": 0.4,
        "thermal_conductivity": 0.5,
        "intrinsic_ni_cm3": 2.1e6,
        "typical_knee_voltage": 1.2,
        "applications": "RF MMICs, Radar, Photovoltaics, Laser Diodes"
    },
    "Gallium Nitride": {
        "symbol": "GaN",
        "bandgap_ev": 3.4,
        "bandgap_type": "Direct",
        "relative_permittivity": 8.9,
        "electron_mobility": 1500.0,
        "hole_mobility": 30.0,
        "breakdown_field_mv_cm": 3.3,
        "thermal_conductivity": 1.3,
        "intrinsic_ni_cm3": 1.9e-10,
        "typical_knee_voltage": 2.8,
        "applications": "Power converters, 5G Base Stations, High-power RF"
    },
    "Silicon Carbide (4H)": {
        "symbol": "4H-SiC",
        "bandgap_ev": 3.26,
        "bandgap_type": "Indirect",
        "relative_permittivity": 9.7,
        "electron_mobility": 900.0,
        "hole_mobility": 120.0,
        "breakdown_field_mv_cm": 3.0,
        "thermal_conductivity": 4.9,
        "intrinsic_ni_cm3": 8.2e-9,
        "typical_knee_voltage": 2.6,
        "applications": "EV Traction inverters, High-voltage grid switches (>1.2kV)"
    }
}

# Standard BJT Configuration Comparison Matrix (Feature 244)
BJT_CONFIGURATIONS: Dict[str, Dict[str, Any]] = {
    "CE": {
        "name": "Common Emitter",
        "input_terminal": "Base",
        "output_terminal": "Collector",
        "common_terminal": "Emitter",
        "input_impedance": "Medium (~1 kΩ to 5 kΩ)",
        "output_impedance": "High (~40 kΩ to 50 kΩ)",
        "voltage_gain": "High (-Av, typical 100 to 500)",
        "current_gain": "High (Beta, typical 50 to 300)",
        "power_gain": "Very High (Highest among all configs)",
        "phase_shift_deg": 180,
        "primary_applications": "Audio and voltage pre-amplification, General switching"
    },
    "CB": {
        "name": "Common Base",
        "input_terminal": "Emitter",
        "output_terminal": "Collector",
        "common_terminal": "Base",
        "input_impedance": "Very Low (~10 Ω to 50 Ω)",
        "output_impedance": "Very High (~1 MΩ)",
        "voltage_gain": "High (+Av, typical 100 to 500)",
        "current_gain": "Low (Alpha < 1, typical 0.98 to 0.998)",
        "power_gain": "Moderate",
        "phase_shift_deg": 0,
        "primary_applications": "High-frequency RF amplifiers, Current buffers, Cascode stages"
    },
    "CC": {
        "name": "Common Collector (Emitter Follower)",
        "input_terminal": "Base",
        "output_terminal": "Emitter",
        "common_terminal": "Collector",
        "input_impedance": "Very High (~100 kΩ to 500 kΩ)",
        "output_impedance": "Very Low (~10 Ω to 50 Ω)",
        "voltage_gain": "Unity (~0.99, <= 1)",
        "current_gain": "High (Gamma = Beta + 1)",
        "power_gain": "Moderate",
        "phase_shift_deg": 0,
        "primary_applications": "Impedance matching, Headphone audio output driver, Buffer stage"
    }
}


class AnalogElectronicsEngine:
    """
    Backend service engine for Phase D (Features 241–250):
    - PN junction physics & depletion width
    - Diode Shockley I-V characteristics & dynamic resistance
    - Zener voltage regulator design & line/load regulation
    - BJT configuration matrix & conversions
    - MOSFET I-V curves (Cutoff, Triode, Saturation)
    - Small-signal BJT CE amplifier gain & 3dB frequency
    - Op-amp configurations (Inverting, Non-inverting, Diff, Slew Rate)
    - RC/RL transient step response
    - RLC series/parallel resonance & Q-factor
    - Semiconductor material physics comparison & Baliga FOM
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_db(self) -> None:
        with self._lock:
            conn = self._get_connection()
            try:
                # Analog simulations ledger
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS analog_circuit_simulations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        circuit_type TEXT NOT NULL,
                        input_params TEXT NOT NULL,
                        computed_metrics TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)

                # Semiconductor material research ledger
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS semiconductor_studies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        material_name TEXT NOT NULL,
                        doping_na REAL NOT NULL,
                        doping_nd REAL NOT NULL,
                        v_bi REAL NOT NULL,
                        depletion_width_um REAL NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)

                # Seed initial demo study if empty
                cur = conn.execute("SELECT id FROM semiconductor_studies WHERE student_id = ?", ("2023MITEC042",))
                if not cur.fetchone():
                    now = datetime.now(timezone.utc).isoformat()
                    conn.execute("""
                        INSERT INTO semiconductor_studies (student_id, material_name, doping_na, doping_nd, v_bi, depletion_width_um, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, ("2023MITEC042", "Silicon", 1e16, 1e16, 0.695, 0.428, now))

                    conn.execute("""
                        INSERT INTO analog_circuit_simulations (student_id, circuit_type, input_params, computed_metrics, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        "2023MITEC042",
                        "RLC_SERIES_RESONANCE",
                        json.dumps({"R": 10.0, "L_uH": 100.0, "C_nF": 10.0}),
                        json.dumps({"f0_khz": 159.15, "Q": 10.0, "bw_khz": 15.92}),
                        now
                    ))

                conn.commit()
            finally:
                conn.close()

    # ------------------------------------------------------------------------------------
    # Feature 241: PN Junction Learning Explorer
    # ------------------------------------------------------------------------------------
    def calculate_pn_junction(
        self,
        material: str = "Silicon",
        na_cm3: float = 1e16,
        nd_cm3: float = 1e16,
        applied_voltage_v: float = 0.0,
        temp_k: float = 300.0,
        area_cm2: float = 1e-4
    ) -> Dict[str, Any]:
        """
        Calculate built-in potential (Vbi), depletion width (W), peak electric field (Emax),
        and junction capacitance (Cj) for a step PN junction.
        """
        if material not in SEMICONDUCTOR_MATERIALS:
            raise ValueError(f"Unknown material '{material}'. Supported: {list(SEMICONDUCTOR_MATERIALS.keys())}")

        mat = SEMICONDUCTOR_MATERIALS[material]
        eps_s = mat["relative_permittivity"] * EPSILON_0
        ni = mat["intrinsic_ni_cm3"]

        if na_cm3 <= 0 or nd_cm3 <= 0:
            raise ValueError("Doping concentrations Na and Nd must be positive (> 0).")

        vt = (K_BOLTZ * temp_k) / Q_ELEC

        # Built-in potential: Vbi = Vt * ln(Na * Nd / ni^2)
        ratio = (na_cm3 * nd_cm3) / (ni ** 2)
        if ratio <= 0:
            raise ValueError("Invalid doping product.")
        v_bi = vt * math.log(ratio)

        # Effective barrier voltage (Vbi - V)
        v_eff = v_bi - applied_voltage_v
        if v_eff <= 0.05:
            # Under high forward bias approaching Vbi
            v_eff = 0.05

        # Depletion width: W = sqrt((2 * eps_s * v_eff / q) * (1/Na + 1/Nd))
        w_cm = math.sqrt((2.0 * eps_s * v_eff / Q_ELEC) * (1.0 / na_cm3 + 1.0 / nd_cm3))
        w_um = w_cm * 1e4

        # Depletion widths in p and n regions
        x_p_um = w_um * (nd_cm3 / (na_cm3 + nd_cm3))
        x_n_um = w_um * (na_cm3 / (na_cm3 + nd_cm3))

        # Peak electric field: E_max = 2 * v_eff / W
        e_max_v_cm = (2.0 * v_eff) / w_cm
        e_max_kv_cm = e_max_v_cm / 1e3

        # Junction capacitance: Cj = eps_s * A / W
        c_j_f = (eps_s * area_cm2) / w_cm
        c_j_pf = c_j_f * 1e12

        return {
            "material": material,
            "temp_k": temp_k,
            "thermal_voltage_mv": round(vt * 1e3, 3),
            "built_in_potential_v": round(v_bi, 4),
            "applied_voltage_v": applied_voltage_v,
            "effective_barrier_v": round(v_eff, 4),
            "depletion_width_um": round(w_um, 4),
            "p_region_width_um": round(x_p_um, 4),
            "n_region_width_um": round(x_n_um, 4),
            "peak_electric_field_kv_cm": round(e_max_kv_cm, 2),
            "junction_capacitance_pf": round(c_j_pf, 3)
        }

    # ------------------------------------------------------------------------------------
    # Feature 242: Diode Characteristics Plotter
    # ------------------------------------------------------------------------------------
    def calculate_diode_iv(
        self,
        is_sat_a: float = 1e-12,
        ideality_factor_n: float = 1.0,
        voltage_v: float = 0.65,
        temp_k: float = 300.0,
        series_r_ohm: float = 0.1
    ) -> Dict[str, Any]:
        """
        Calculate diode current and dynamic resistance using Shockley's equation.
        I = Is * (exp(V / (n * Vt)) - 1)
        rd = (n * Vt) / (I + Is)
        """
        vt = (K_BOLTZ * temp_k) / Q_ELEC
        nvt = ideality_factor_n * vt

        # Cap voltage exponent to prevent numerical overflow
        exp_arg = voltage_v / nvt
        if exp_arg > 60:
            exp_arg = 60

        current_a = is_sat_a * (math.exp(exp_arg) - 1.0)
        dynamic_rd_ohm = nvt / (current_a + is_sat_a) if current_a > -is_sat_a else 1e9

        # Generate sample points for I-V curve visualization
        curve_points = []
        for v_step in [v * 0.05 for v in range(-10, 18)]:  # -0.5V to +0.85V
            arg = v_step / nvt
            if arg < 60:
                i_step = is_sat_a * (math.exp(arg) - 1.0)
                curve_points.append({"v": round(v_step, 2), "i_ma": round(i_step * 1e3, 4)})

        return {
            "applied_voltage_v": voltage_v,
            "current_ma": round(current_a * 1e3, 4),
            "current_a": current_a,
            "dynamic_resistance_ohm": round(dynamic_rd_ohm, 3),
            "thermal_voltage_mv": round(vt * 1e3, 2),
            "knee_threshold_v": 0.7 if is_sat_a <= 1e-10 else 0.3,
            "curve_points": curve_points
        }

    # ------------------------------------------------------------------------------------
    # Feature 243: Zener Voltage Regulator Calculator
    # ------------------------------------------------------------------------------------
    def design_zener_regulator(
        self,
        vin_min_v: float = 15.0,
        vin_max_v: float = 18.0,
        vz_v: float = 10.0,
        il_min_ma: float = 5.0,
        il_max_ma: float = 50.0,
        iz_min_ma: float = 5.0,
        pz_max_w: float = 1.5,
        rz_ohm: float = 8.0
    ) -> Dict[str, Any]:
        """
        Design a shunt Zener diode voltage regulator:
        - Series resistance bounds: Rs_max and Rs_min
        - Max Zener power dissipation Pz_max
        - Line and load regulation
        """
        if vin_min_v <= vz_v:
            raise ValueError(f"Input voltage min ({vin_min_v}V) must be strictly greater than Zener voltage ({vz_v}V).")

        il_max_a = il_max_ma / 1e3
        il_min_a = il_min_ma / 1e3
        iz_min_a = iz_min_ma / 1e3

        # Max allowed Zener current based on power rating
        iz_max_a = pz_max_w / vz_v
        iz_max_ma = iz_max_a * 1e3

        # Rs_max to guarantee Iz_min at Vin_min and IL_max
        rs_max = (vin_min_v - vz_v) / (il_max_a + iz_min_a)

        # Rs_min to avoid exceeding Pz_max at Vin_max and IL_min
        rs_min = (vin_max_v - vz_v) / (il_min_a + iz_max_a)

        if rs_min > rs_max:
            recommended_rs = rs_max
            valid_design = False
            msg = "Zener power rating insufficient for specified input/load range."
        else:
            recommended_rs = round((rs_min + rs_max) / 2.0, 1)
            valid_design = True
            msg = "Design valid. Recommended standard resistor within safe boundaries."

        # Compute max power in recommended Rs
        max_is_a = (vin_max_v - vz_v) / recommended_rs
        prs_max_w = (max_is_a ** 2) * recommended_rs

        # Max Zener power in this design
        actual_pz_max_w = (max_is_a - il_min_a) * vz_v

        # Line regulation: dVo / dVin = rz / (Rs + rz)
        line_reg = rz_ohm / (recommended_rs + rz_ohm)

        # Load regulation: dVo / dIL = -rz
        load_reg_mv_per_ma = -rz_ohm

        return {
            "valid_design": valid_design,
            "status_message": msg,
            "rs_min_ohm": round(rs_min, 1),
            "rs_max_ohm": round(rs_max, 1),
            "recommended_rs_ohm": recommended_rs,
            "max_zener_current_ma": round(iz_max_ma, 2),
            "actual_pz_max_w": round(actual_pz_max_w, 3),
            "resistor_power_w": round(prs_max_w, 3),
            "line_regulation": round(line_reg, 5),
            "load_regulation_mv_per_ma": round(load_reg_mv_per_ma, 2)
        }

    # ------------------------------------------------------------------------------------
    # Feature 244: BJT Configuration Comparison Matrix
    # ------------------------------------------------------------------------------------
    def compare_bjt_configurations(self, beta: float = 100.0) -> Dict[str, Any]:
        """Compare CE, CB, and CC topologies and compute alpha, beta, and gamma current gains."""
        if beta <= 0:
            raise ValueError("Beta must be positive (> 0).")

        alpha = beta / (beta + 1.0)
        gamma = beta + 1.0

        return {
            "beta": beta,
            "alpha": round(alpha, 5),
            "gamma": round(gamma, 1),
            "configurations": BJT_CONFIGURATIONS
        }

    # ------------------------------------------------------------------------------------
    # Feature 245: MOSFET Characteristics Plotter
    # ------------------------------------------------------------------------------------
    def calculate_mosfet_iv(
        self,
        vgs_v: float = 3.0,
        vds_v: float = 4.0,
        vth_v: float = 1.0,
        kn_prime_ua_v2: float = 200.0,  # mu_n * Cox in uA/V^2
        w_over_l: float = 10.0,
        lambda_v_inv: float = 0.02
    ) -> Dict[str, Any]:
        """
        Calculate MOSFET operating region and drain current (ID):
        - Cutoff: Vgs <= Vth -> ID = 0
        - Triode: Vds < Vgs - Vth
        - Saturation: Vds >= Vgs - Vth
        """
        v_ov = vgs_v - vth_v  # Overdrive voltage
        kn = (kn_prime_ua_v2 * 1e-6) * w_over_l  # A/V^2

        if v_ov <= 0:
            region = "Cutoff"
            id_a = 0.0
            gm_ms = 0.0
            ro_kohm = 1e6
        elif vds_v < v_ov:
            region = "Triode (Linear)"
            id_a = kn * ((v_ov * vds_v) - 0.5 * (vds_v ** 2)) * (1.0 + lambda_v_inv * vds_v)
            gm_ms = kn * vds_v * 1e3
            ro_kohm = (1.0 / (lambda_v_inv * id_a)) / 1e3 if id_a > 0 and lambda_v_inv > 0 else 1e6
        else:
            region = "Saturation (Active)"
            id_a = 0.5 * kn * (v_ov ** 2) * (1.0 + lambda_v_inv * vds_v)
            gm_ms = math.sqrt(2.0 * kn * id_a) * 1e3
            ro_kohm = (1.0 / (lambda_v_inv * id_a)) / 1e3 if id_a > 0 and lambda_v_inv > 0 else 1e6

        # Generate sample points for Vds sweep at current Vgs
        vds_sweep = []
        for step in range(0, 51):
            v_ds = step * 0.1  # 0 to 5.0 V
            if v_ov <= 0:
                curr = 0.0
            elif v_ds < v_ov:
                curr = kn * ((v_ov * v_ds) - 0.5 * (v_ds ** 2)) * (1.0 + lambda_v_inv * v_ds)
            else:
                curr = 0.5 * kn * (v_ov ** 2) * (1.0 + lambda_v_inv * v_ds)
            vds_sweep.append({"vds": round(v_ds, 2), "id_ma": round(curr * 1e3, 4)})

        return {
            "vgs_v": vgs_v,
            "vds_v": vds_v,
            "vth_v": vth_v,
            "overdrive_v": round(v_ov, 3),
            "operating_region": region,
            "drain_current_ma": round(id_a * 1e3, 4),
            "transconductance_gm_ms": round(gm_ms, 3),
            "output_resistance_ro_kohm": round(ro_kohm, 2),
            "vds_sweep": vds_sweep
        }

    # ------------------------------------------------------------------------------------
    # Feature 246: Small-Signal CE Amplifier Gain Calculator
    # ------------------------------------------------------------------------------------
    def calculate_ce_amplifier(
        self,
        ic_ma: float = 2.0,
        beta: float = 100.0,
        rc_kohm: float = 4.7,
        rl_kohm: float = 10.0,
        r1_kohm: float = 47.0,
        r2_kohm: float = 10.0,
        re_ohm: float = 470.0,
        bypassed_emitter: bool = True,
        va_v: float = 100.0,
        cin_uf: float = 10.0
    ) -> Dict[str, Any]:
        """
        Calculate small-signal AC parameters for a BJT Common Emitter amplifier:
        - gm, r_pi, ro
        - Voltage gain Av, Input impedance Rin, Output impedance Rout
        - Lower 3dB cutoff frequency f_L
        """
        ic_a = ic_ma / 1e3
        vt = VT_ROOM

        # Small signal hybrid-pi parameters
        gm = ic_a / vt  # A/V
        r_pi = beta / gm  # Ohms
        ro = (va_v / ic_a) if va_v > 0 else 1e9  # Ohms

        rc = rc_kohm * 1e3
        rl = rl_kohm * 1e3
        r1 = r1_kohm * 1e3
        r2 = r2_kohm * 1e3
        rb = (r1 * r2) / (r1 + r2)  # Base bias parallel combination

        # Effective AC collector load: Rc || Rl || ro
        rac = 1.0 / (1.0 / rc + 1.0 / rl + 1.0 / ro)

        if bypassed_emitter:
            rin_base = r_pi
            av = -gm * rac
        else:
            # Unbypassed emitter degeneration
            rin_base = r_pi + (beta + 1.0) * re_ohm
            av = (-beta * rac) / (r_pi + (beta + 1.0) * re_ohm)

        rin_total = 1.0 / (1.0 / rb + 1.0 / rin_base)
        rout_total = 1.0 / (1.0 / rc + 1.0 / ro)

        # Lower 3dB cutoff frequency due to Cin: fL = 1 / (2 * pi * (Rsig + Rin) * Cin)
        cin_f = cin_uf * 1e-6
        fl_hz = 1.0 / (2.0 * math.pi * rin_total * cin_f)

        return {
            "ic_ma": ic_ma,
            "transconductance_gm_ms": round(gm * 1e3, 3),
            "r_pi_kohm": round(r_pi / 1e3, 3),
            "ro_kohm": round(ro / 1e3, 1),
            "voltage_gain_av": round(av, 2),
            "voltage_gain_db": round(20.0 * math.log10(abs(av)), 2) if abs(av) > 0 else 0.0,
            "input_impedance_rin_kohm": round(rin_total / 1e3, 3),
            "output_impedance_rout_kohm": round(rout_total / 1e3, 3),
            "lower_cutoff_fl_hz": round(fl_hz, 2),
            "bypassed_emitter": bypassed_emitter
        }

    # ------------------------------------------------------------------------------------
    # Feature 247: Op-Amp Configuration Explorer
    # ------------------------------------------------------------------------------------
    def calculate_opamp_circuit(
        self,
        topology: str = "inverting",
        rf_kohm: float = 100.0,
        rin_kohm: float = 10.0,
        vin_v: float = 1.0,
        vin2_v: float = 0.0,
        v_supply_v: float = 15.0,
        slew_rate_v_us: float = 0.5
    ) -> Dict[str, Any]:
        """
        Evaluate ideal & practical operational amplifier topologies:
        - Inverting: Av = -Rf / Rin
        - Non-inverting: Av = 1 + Rf / Rin
        - Voltage Follower: Av = 1
        - Differential: Vout = (Rf / Rin) * (Vin2 - Vin1)
        - Full-power bandwidth (FPBW) from Slew Rate
        """
        rf = rf_kohm * 1e3
        rin = rin_kohm * 1e3

        if topology == "inverting":
            gain = -rf / rin
            vout_ideal = gain * vin_v
            rin_eff_kohm = rin_kohm
        elif topology == "non_inverting":
            gain = 1.0 + (rf / rin)
            vout_ideal = gain * vin_v
            rin_eff_kohm = 1e6  # ~Infinite
        elif topology == "voltage_follower":
            gain = 1.0
            vout_ideal = vin_v
            rin_eff_kohm = 1e6
        elif topology == "differential":
            gain = rf / rin
            vout_ideal = gain * (vin2_v - vin_v)
            rin_eff_kohm = rin_kohm * 2.0
        else:
            raise ValueError(f"Unknown topology '{topology}'. Supported: inverting, non_inverting, voltage_follower, differential.")

        # Supply rail saturation clipping (typically ~1.5V below supply rails for general op-amps)
        v_sat = v_supply_v - 1.5
        is_saturated = abs(vout_ideal) > v_sat
        vout_clipped = max(-v_sat, min(v_sat, vout_ideal))

        # Full power bandwidth from slew rate: f_max = SR / (2 * pi * Vp)
        vp = max(0.1, abs(vout_clipped))
        sr_v_s = slew_rate_v_us * 1e6
        fpbw_khz = (sr_v_s / (2.0 * math.pi * vp)) / 1e3

        return {
            "topology": topology,
            "ideal_gain": round(gain, 3),
            "vout_ideal_v": round(vout_ideal, 3),
            "vout_actual_v": round(vout_clipped, 3),
            "is_saturated": is_saturated,
            "effective_rin_kohm": rin_eff_kohm,
            "full_power_bandwidth_khz": round(fpbw_khz, 2),
            "slew_rate_v_us": slew_rate_v_us
        }

    # ------------------------------------------------------------------------------------
    # Feature 248: RC & RL Transient Response Calculator
    # ------------------------------------------------------------------------------------
    def calculate_transient_response(
        self,
        circuit_type: str = "RC",
        r_kohm: float = 10.0,
        c_uf: float = 1.0,
        l_mh: float = 100.0,
        v_step_v: float = 5.0
    ) -> Dict[str, Any]:
        """
        Calculate step charging and discharging curves for RC or RL circuits:
        - RC: tau = R * C
        - RL: tau = L / R
        """
        r_ohm = r_kohm * 1e3

        if circuit_type.upper() == "RC":
            c_f = c_uf * 1e-6
            tau_sec = r_ohm * c_f
            tau_ms = tau_sec * 1e3
        elif circuit_type.upper() == "RL":
            l_h = l_mh * 1e-3
            tau_sec = l_h / r_ohm
            tau_ms = tau_sec * 1e3
        else:
            raise ValueError("circuit_type must be either 'RC' or 'RL'.")

        # 5-time constants response curve
        curve = []
        for i in range(21):
            t_tau = i * 0.25  # 0 to 5.0 tau
            t_ms = t_tau * tau_ms
            charge_factor = 1.0 - math.exp(-t_tau)
            discharge_factor = math.exp(-t_tau)
            curve.append({
                "t_tau": round(t_tau, 2),
                "t_ms": round(t_ms, 3),
                "v_charge_v": round(v_step_v * charge_factor, 3),
                "v_discharge_v": round(v_step_v * discharge_factor, 3)
            })

        return {
            "circuit_type": circuit_type.upper(),
            "time_constant_tau_ms": round(tau_ms, 4),
            "settling_time_5tau_ms": round(5.0 * tau_ms, 4),
            "v_step_v": v_step_v,
            "curve_points": curve
        }

    # ------------------------------------------------------------------------------------
    # Feature 249: RLC Resonance Calculator
    # ------------------------------------------------------------------------------------
    def calculate_rlc_resonance(
        self,
        r_ohm: float = 10.0,
        l_uh: float = 100.0,
        c_nf: float = 10.0,
        topology: str = "series"
    ) -> Dict[str, Any]:
        """
        Calculate series or parallel RLC resonant frequency, Q-factor, bandwidth,
        half-power cutoff frequencies, and damping factor zeta.
        """
        if r_ohm <= 0 or l_uh <= 0 or c_nf <= 0:
            raise ValueError("R, L, and C values must be positive non-zero.")

        l_h = l_uh * 1e-6
        c_f = c_nf * 1e-9

        # Resonant angular frequency: omega_0 = 1 / sqrt(L * C)
        omega_0 = 1.0 / math.sqrt(l_h * c_f)
        f_0 = omega_0 / (2.0 * math.pi)
        f0_khz = f_0 / 1e3

        if topology.lower() == "series":
            # Series RLC: Q = (omega_0 * L) / R
            q_factor = (omega_0 * l_h) / r_ohm
            zeta = r_ohm / (2.0 * math.sqrt(l_h / c_f))
        elif topology.lower() == "parallel":
            # Parallel RLC: Q = R / (omega_0 * L)
            q_factor = r_ohm / (omega_0 * l_h)
            zeta = 1.0 / (2.0 * q_factor)
        else:
            raise ValueError("topology must be 'series' or 'parallel'.")

        bw_hz = f_0 / q_factor if q_factor > 0 else 0
        bw_khz = bw_hz / 1e3

        f1_khz = max(0.0, f0_khz - (bw_khz / 2.0))
        f2_khz = f0_khz + (bw_khz / 2.0)

        # Damping classification
        if zeta < 0.999:
            damping_regime = "Underdamped (Oscillatory ringing)"
        elif abs(zeta - 1.0) <= 0.002:
            damping_regime = "Critically Damped (Fastest settling without ringing)"
        else:
            damping_regime = "Overdamped (Sluggish non-oscillatory return)"

        return {
            "topology": topology.capitalize(),
            "resonant_freq_f0_khz": round(f0_khz, 3),
            "quality_factor_q": round(q_factor, 2),
            "bandwidth_bw_khz": round(bw_khz, 3),
            "lower_cutoff_f1_khz": round(f1_khz, 3),
            "upper_cutoff_f2_khz": round(f2_khz, 3),
            "damping_factor_zeta": round(zeta, 4),
            "damping_regime": damping_regime
        }

    # ------------------------------------------------------------------------------------
    # Feature 250: Semiconductor Material Comparison Tool
    # ------------------------------------------------------------------------------------
    def compare_semiconductor_materials(self) -> Dict[str, Any]:
        """
        Compare semiconductors (Si, Ge, GaAs, GaN, SiC) across bandgap,
        breakdown field, mobility, and compute Baliga Figure of Merit (BFOM = eps_r * mu_n * Ec^3).
        """
        results = []
        si_bfom = 11.7 * 1400.0 * (0.3 ** 3)  # Silicon normalized baseline

        for name, data in SEMICONDUCTOR_MATERIALS.items():
            eps_r = data["relative_permittivity"]
            mu_n = data["electron_mobility"]
            ec = data["breakdown_field_mv_cm"]
            raw_bfom = eps_r * mu_n * (ec ** 3)
            normalized_bfom = raw_bfom / si_bfom

            results.append({
                "material": name,
                "symbol": data["symbol"],
                "bandgap_ev": data["bandgap_ev"],
                "bandgap_type": data["bandgap_type"],
                "electron_mobility": data["electron_mobility"],
                "hole_mobility": data["hole_mobility"],
                "breakdown_field_mv_cm": data["breakdown_field_mv_cm"],
                "thermal_conductivity": data["thermal_conductivity"],
                "intrinsic_ni_cm3": data["intrinsic_ni_cm3"],
                "typical_knee_voltage": data["typical_knee_voltage"],
                "baliga_fom_normalized": round(normalized_bfom, 1),
                "applications": data["applications"]
            })

        return {
            "materials_count": len(results),
            "baseline_material": "Silicon (1.0x)",
            "comparison": results
        }

    # ------------------------------------------------------------------------------------
    # Persistence Methods (SQLite WAL Mode)
    # ------------------------------------------------------------------------------------
    def save_simulation(
        self,
        student_id: str,
        circuit_type: str,
        input_params: Dict[str, Any],
        computed_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Record an analog circuit simulation run to SQLite WAL ledger."""
        with self._lock:
            conn = self._get_connection()
            try:
                now = datetime.now(timezone.utc).isoformat()
                cur = conn.execute("""
                    INSERT INTO analog_circuit_simulations (student_id, circuit_type, input_params, computed_metrics, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    student_id,
                    circuit_type,
                    json.dumps(input_params),
                    json.dumps(computed_metrics),
                    now
                ))
                conn.commit()
                return {
                    "status": "success",
                    "simulation_id": cur.lastrowid,
                    "student_id": student_id,
                    "circuit_type": circuit_type,
                    "created_at": now
                }
            finally:
                conn.close()

    def get_simulations(self, student_id: str = "2023MITEC042", limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent simulation runs for a student."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.execute("""
                    SELECT id, student_id, circuit_type, input_params, computed_metrics, created_at
                    FROM analog_circuit_simulations
                    WHERE student_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                """, (student_id, limit))
                results = []
                for row in cur.fetchall():
                    item = dict(row)
                    try:
                        item["input_params"] = json.loads(item["input_params"])
                        item["computed_metrics"] = json.loads(item["computed_metrics"])
                    except Exception:
                        pass
                    results.append(item)
                return results
            finally:
                conn.close()
