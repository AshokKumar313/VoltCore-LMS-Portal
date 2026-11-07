"""
========================================================================================
VoltCore Apex Academia - Semiconductor Physics Explorer Engine
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Lead Semiconductor Device Physicist & Systems Architect: Ashok Kumar A
========================================================================================
Provides:
  1. Temperature-dependent energy bandgap calculation via Varshni's empirical equation:
       Eg(T) = Eg(0) - (alpha * T^2) / (T + beta)
     for Silicon (Si), Germanium (Ge), Gallium Arsenide (GaAs), Silicon Carbide (4H-SiC),
     and Gallium Nitride (GaN).
  2. Effective density of states Nc(T), Nv(T) and intrinsic carrier concentration ni(T):
       ni(T) = sqrt(Nc * Nv) * exp(-Eg / (2 * kB * T))
  3. Fermi-Dirac distribution probability calculators:
       f(E) = 1 / (1 + exp((E - EF) / (kB * T)))
     along with non-degenerate vs degenerate occupancy regime audits.
  4. Einstein relation and drift-diffusion charge carrier transport:
       D = mu * (kB * T / q) = mu * Vt
       Jn = q * n * mu_n * E + q * Dn * (dn/dx)
       Jp = q * p * mu_p * E - q * Dp * (dp/dx)
  5. PN Junction space-charge electrostatics:
       Vbi = Vt * ln((Na * Nd) / ni^2)
       W_dep(Va) = sqrt((2 * eps_s * (Vbi - Va) / q) * (1/Na + 1/Nd))
       Cj(Va) = (eps_s * Area) / W_dep(Va)
  6. Passive CPU profile (<5% utilization) and single-process execution safety.
========================================================================================
"""

import math
import os
import json
import sqlite3
import datetime
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")

# ========================================================================================
# 1. Fundamental Physical Constants (CODATA Recommended Values)
# ========================================================================================

Q_ELEM = 1.602176634e-19       # Elementary charge (Coulombs, C)
K_BOLTZ_J = 1.380649e-23       # Boltzmann constant (Joules per Kelvin, J/K)
K_BOLTZ_EV = 8.617333262e-5    # Boltzmann constant in electron-volts (eV/K)
EPSILON_0 = 8.8541878128e-14   # Permittivity of vacuum (Farads per cm, F/cm)
H_PLANCK_J = 6.62607015e-34    # Planck's constant (Joule-seconds, J*s)
M_ELECTRON_KG = 9.1093837e-31  # Rest mass of electron (kg)


# ========================================================================================
# 2. Semiconductor Material Parameter Database
# ========================================================================================

SEMICONDUCTOR_MATERIALS: Dict[str, Dict[str, Any]] = {
    "SI": {
        "name": "Silicon",
        "formula": "Si",
        "crystal_structure": "Diamond Cubic",
        "bandgap_type": "INDIRECT",
        "eg_0_ev": 1.166,             # Bandgap at 0K (eV)
        "alpha_varshni": 4.73e-4,      # Varshni alpha (eV/K)
        "beta_varshni": 636.0,         # Varshni beta (K)
        "eps_r": 11.7,                 # Relative dielectric permittivity
        "nc_300": 2.8e19,              # Conduction band DOS at 300K (cm^-3)
        "nv_300": 1.04e19,             # Valence band DOS at 300K (cm^-3)
        "mu_n_300": 1350.0,            # Electron mobility at 300K (cm^2/V-s)
        "mu_p_300": 450.0,             # Hole mobility at 300K (cm^2/V-s)
        "ni_300_empirical": 1.0e10,    # Baseline standard intrinsic carrier density (cm^-3)
        "mn_eff": 1.08,                # Density of states effective mass ratio (m_e*/m_0)
        "mp_eff": 0.81,                # Density of states effective mass ratio (m_h*/m_0)
        "breakdown_field_v_cm": 3.0e5  # Critical electric field (V/cm)
    },
    "GE": {
        "name": "Germanium",
        "formula": "Ge",
        "crystal_structure": "Diamond Cubic",
        "bandgap_type": "INDIRECT",
        "eg_0_ev": 0.7437,
        "alpha_varshni": 4.77e-4,
        "beta_varshni": 235.0,
        "eps_r": 16.0,
        "nc_300": 1.04e19,
        "nv_300": 6.0e18,
        "mu_n_300": 3900.0,
        "mu_p_300": 1900.0,
        "ni_300_empirical": 2.4e13,
        "mn_eff": 0.55,
        "mp_eff": 0.37,
        "breakdown_field_v_cm": 1.0e5
    },
    "GAAS": {
        "name": "Gallium Arsenide",
        "formula": "GaAs",
        "crystal_structure": "Zincblende",
        "bandgap_type": "DIRECT",
        "eg_0_ev": 1.519,
        "alpha_varshni": 5.405e-4,
        "beta_varshni": 204.0,
        "eps_r": 12.9,
        "nc_300": 4.7e17,
        "nv_300": 7.0e18,
        "mu_n_300": 8500.0,
        "mu_p_300": 400.0,
        "ni_300_empirical": 2.1e6,
        "mn_eff": 0.067,
        "mp_eff": 0.45,
        "breakdown_field_v_cm": 4.0e5
    },
    "SIC": {
        "name": "Silicon Carbide (4H-SiC)",
        "formula": "4H-SiC",
        "crystal_structure": "Hexagonal",
        "bandgap_type": "INDIRECT",
        "eg_0_ev": 3.26,
        "alpha_varshni": 6.5e-4,
        "beta_varshni": 1200.0,
        "eps_r": 9.7,
        "nc_300": 1.6e19,
        "nv_300": 2.5e19,
        "mu_n_300": 900.0,
        "mu_p_300": 120.0,
        "ni_300_empirical": 8.2e-9,
        "mn_eff": 0.42,
        "mp_eff": 1.0,
        "breakdown_field_v_cm": 3.0e6
    },
    "GAN": {
        "name": "Gallium Nitride",
        "formula": "GaN",
        "crystal_structure": "Wurtzite",
        "bandgap_type": "DIRECT",
        "eg_0_ev": 3.47,
        "alpha_varshni": 9.09e-4,
        "beta_varshni": 830.0,
        "eps_r": 8.9,
        "nc_300": 2.3e18,
        "nv_300": 4.6e19,
        "mu_n_300": 1000.0,
        "mu_p_300": 30.0,
        "ni_300_empirical": 1.9e-10,
        "mn_eff": 0.20,
        "mp_eff": 0.80,
        "breakdown_field_v_cm": 3.3e6
    }
}


# ========================================================================================
# 3. Semiconductor Physics Computational Engine
# ========================================================================================

class SemiconductorPhysicsEngine:
    """
    Unified device physics engine for solid-state electronic devices:
      - Bandgap temperature scaling (Varshni)
      - Effective density of states Nc(T), Nv(T)
      - Intrinsic carrier density ni(T)
      - Fermi-Dirac probability and degeneracy audits
      - Drift-diffusion current density & Einstein relation
      - PN junction space-charge electrostatics & barrier potential
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    def _init_db(self):
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS semiconductor_analysis_history (
                    analysis_id TEXT PRIMARY KEY,
                    analysis_type TEXT NOT NULL,
                    material TEXT NOT NULL,
                    temperature_k REAL NOT NULL,
                    result_summary_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)
            conn.commit()
        finally:
            conn.close()

    def get_supported_materials(self) -> List[Dict[str, Any]]:
        """Returns catalog of all supported semiconductor materials and constants."""
        materials = []
        for key, prop in SEMICONDUCTOR_MATERIALS.items():
            materials.append({
                "code": key,
                "name": prop["name"],
                "formula": prop["formula"],
                "bandgap_type": prop["bandgap_type"],
                "eg_300k": round(self.calculate_bandgap(key, 300.0), 4),
                "eps_r": prop["eps_r"],
                "mu_n": prop["mu_n_300"],
                "mu_p": prop["mu_p_300"]
            })
        return materials

    def calculate_bandgap(self, material: str, temperature_k: float) -> float:
        """
        Computes energy bandgap Eg(T) in electron-volts (eV) using Varshni's equation:
          Eg(T) = Eg(0) - (alpha * T^2) / (T + beta)
        Clamped to physical range (T >= 0K).
        """
        mat = material.strip().upper()
        props = SEMICONDUCTOR_MATERIALS.get(mat, SEMICONDUCTOR_MATERIALS["SI"])
        T = max(0.1, float(temperature_k))
        eg_0 = props["eg_0_ev"]
        alpha = props["alpha_varshni"]
        beta = props["beta_varshni"]

        delta_eg = (alpha * (T ** 2)) / (T + beta)
        eg_t = max(0.05, eg_0 - delta_eg)
        return round(eg_t, 5)

    def calculate_thermal_voltage(self, temperature_k: float) -> float:
        """
        Computes thermal voltage Vt = kB * T / q in Volts (V).
        At 300K, Vt ~ 0.025852 V = 25.85 mV.
        """
        T = max(0.1, float(temperature_k))
        return (K_BOLTZ_J * T) / Q_ELEM

    def calculate_effective_density_of_states(
        self,
        material: str,
        temperature_k: float
    ) -> Tuple[float, float]:
        """
        Computes conduction Nc(T) and valence Nv(T) band effective density of states (cm^-3):
          Nc(T) = Nc(300) * (T / 300)^1.5
          Nv(T) = Nv(300) * (T / 300)^1.5
        """
        mat = material.strip().upper()
        props = SEMICONDUCTOR_MATERIALS.get(mat, SEMICONDUCTOR_MATERIALS["SI"])
        T = max(0.1, float(temperature_k))
        t_ratio = (T / 300.0) ** 1.5

        nc = props["nc_300"] * t_ratio
        nv = props["nv_300"] * t_ratio
        return nc, nv

    def calculate_intrinsic_carrier_concentration(
        self,
        material: str,
        temperature_k: float
    ) -> float:
        """
        Calculates intrinsic carrier concentration ni(T) in cm^-3:
          ni(T) = sqrt(Nc(T) * Nv(T)) * exp(-Eg(T) / (2 * kB * T))
        """
        mat = material.strip().upper()
        T = max(0.1, float(temperature_k))
        eg = self.calculate_bandgap(mat, T)
        nc, nv = self.calculate_effective_density_of_states(mat, T)

        # Thermal energy in eV
        kb_t_ev = K_BOLTZ_EV * T
        exp_arg = -eg / (2.0 * kb_t_ev)

        # Prevent numerical underflow
        if exp_arg < -250.0:
            return 0.0

        ni = math.sqrt(nc * nv) * math.exp(exp_arg)
        return ni

    def calculate_fermi_dirac_probability(
        self,
        energy_ev: float,
        fermi_level_ev: float,
        temperature_k: float = 300.0
    ) -> Dict[str, Any]:
        """
        Computes Fermi-Dirac occupancy probability:
          f(E) = 1 / (1 + exp((E - EF) / (kB * T)))
        and hole occupancy:
          1 - f(E) = 1 / (1 + exp((EF - E) / (kB * T)))
        Also checks Maxwell-Boltzmann approximation validity and degeneracy criteria.
        """
        T = max(0.1, float(temperature_k))
        kb_t_ev = K_BOLTZ_EV * T
        delta_e = float(energy_ev) - float(fermi_level_ev)
        ratio = delta_e / kb_t_ev

        # Numerical bounds protection
        if ratio > 600.0:
            f_e = 0.0
            hole_prob = 1.0
        elif ratio < -600.0:
            f_e = 1.0
            hole_prob = 0.0
        else:
            exp_val = math.exp(ratio)
            f_e = 1.0 / (1.0 + exp_val)
            hole_prob = exp_val / (1.0 + exp_val)

        # Maxwell-Boltzmann approximation: f_mb = exp(- (E - EF) / (kB * T)) for E > EF
        f_mb = math.exp(-ratio) if 0.0 <= ratio < 500.0 else (1.0 if ratio < 0.0 else 0.0)
        mb_error_pct = abs(f_e - f_mb) / max(1e-15, f_e) * 100.0 if f_e > 1e-12 else 0.0

        # Degeneracy regime
        if abs(delta_e) >= 3.0 * kb_t_ev:
            regime = "NON_DEGENERATE_BOLTZMANN"
            regime_desc = "Non-degenerate semiconductor: |E - EF| >= 3*kB*T. Classical Maxwell-Boltzmann statistics are accurate."
        elif abs(delta_e) > 0.0:
            regime = "QUASI_DEGENERATE_TRANSITION"
            regime_desc = "Quasi-degenerate transition: |E - EF| < 3*kB*T. Fermi-Dirac Fermi integral is strictly required."
        else:
            regime = "DEGENERATE_FERMI_EDGE"
            regime_desc = "Energy level exactly coincides with Fermi level (E = EF); occupancy probability is exactly 0.50 (50%)."

        return {
            "energy_ev": float(energy_ev),
            "fermi_level_ev": float(fermi_level_ev),
            "temperature_k": T,
            "thermal_energy_ev": round(kb_t_ev, 5),
            "delta_e_ev": round(delta_e, 5),
            "fermi_dirac_prob_electron": round(f_e, 6),
            "fermi_dirac_prob_hole": round(hole_prob, 6),
            "boltzmann_approx_prob": round(f_mb, 6),
            "boltzmann_error_pct": round(mb_error_pct, 2),
            "regime": regime,
            "regime_description": regime_desc
        }

    def calculate_einstein_diffusion_coefficient(
        self,
        mobility_cm2_v_s: float,
        temperature_k: float = 300.0
    ) -> float:
        """
        Computes diffusion coefficient D = mu * (kB * T / q) = mu * Vt in cm^2/s.
        Governed by the Einstein relation for carrier transport.
        """
        T = max(0.1, float(temperature_k))
        mu = max(0.1, float(mobility_cm2_v_s))
        vt = self.calculate_thermal_voltage(T)
        return mu * vt

    def calculate_drift_diffusion_current_density(
        self,
        carrier_density_cm3: float,
        carrier_gradient_cm4: float,
        electric_field_v_cm: float,
        mobility_cm2_v_s: float,
        temperature_k: float = 300.0,
        carrier_type: str = "ELECTRON"
    ) -> Dict[str, Any]:
        """
        Computes drift and diffusion current densities in A/cm^2:
          Electron: Jn = q * n * mu_n * E + q * Dn * (dn/dx)
          Hole:     Jp = q * p * mu_p * E - q * Dp * (dp/dx)
        """
        T = max(0.1, float(temperature_k))
        ctype = carrier_type.strip().upper()
        conc = max(0.0, float(carrier_density_cm3))
        grad = float(carrier_gradient_cm4)
        field = float(electric_field_v_cm)
        mu = max(0.1, float(mobility_cm2_v_s))
        d_coeff = self.calculate_einstein_diffusion_coefficient(mu, T)

        # Drift component: J_drift = q * conc * mu * E
        j_drift = Q_ELEM * conc * mu * field

        # Diffusion component:
        # For electrons: J_diff = + q * Dn * (dn/dx)
        # For holes:     J_diff = - q * Dp * (dp/dx)
        if ctype.startswith("E") or ctype == "N":
            ctype_norm = "ELECTRON"
            j_diff = Q_ELEM * d_coeff * grad
        else:
            ctype_norm = "HOLE"
            j_diff = -Q_ELEM * d_coeff * grad

        j_total = j_drift + j_diff

        return {
            "carrier_type": ctype_norm,
            "carrier_density_cm3": conc,
            "carrier_gradient_cm4": grad,
            "electric_field_v_cm": field,
            "mobility_cm2_v_s": mu,
            "diffusion_coeff_cm2_s": round(d_coeff, 4),
            "thermal_voltage_v": round(self.calculate_thermal_voltage(T), 5),
            "j_drift_a_cm2": round(j_drift, 6),
            "j_diffusion_a_cm2": round(j_diff, 6),
            "j_total_a_cm2": round(j_total, 6),
            "drift_fraction": round(abs(j_drift) / max(1e-12, abs(j_drift) + abs(j_diff)), 4)
        }

    def calculate_pn_junction_electrostatics(
        self,
        material: str = "SI",
        na_cm3: float = 1e16,
        nd_cm3: float = 1e17,
        v_applied: float = 0.0,
        area_cm2: float = 1e-4,
        temperature_k: float = 300.0
    ) -> Dict[str, Any]:
        """
        Computes abrupt step PN junction electrostatics:
          - Built-in barrier potential Vbi
          - Total depletion width W(Va) and regional components xp, xn
          - Peak junction electric field E_max
          - Junction capacitance Cj(Va)
          - Depletion layer charge Qj
        """
        mat = material.strip().upper()
        props = SEMICONDUCTOR_MATERIALS.get(mat, SEMICONDUCTOR_MATERIALS["SI"])
        T = max(0.1, float(temperature_k))
        na = max(1e12, float(na_cm3))
        nd = max(1e12, float(nd_cm3))
        va = float(v_applied)
        area = max(1e-10, float(area_cm2))

        vt = self.calculate_thermal_voltage(T)
        ni = self.calculate_intrinsic_carrier_concentration(mat, T)
        eps_s = props["eps_r"] * EPSILON_0

        # Built-in potential: Vbi = Vt * ln((Na * Nd) / ni^2)
        if ni > 0.0:
            arg = (na * nd) / (ni ** 2)
            v_bi = vt * math.log(max(1.0, arg))
        else:
            v_bi = 1.0

        # Forward bias clamping: Va cannot exceed Vbi (inversion/high injection limit)
        effective_va = min(va, v_bi - 0.05)
        barrier_v = max(0.01, v_bi - effective_va)

        # Total depletion width: W = sqrt((2 * eps_s * barrier_v / q) * (1/Na + 1/Nd))
        w_sq = (2.0 * eps_s * barrier_v / Q_ELEM) * ((1.0 / na) + (1.0 / nd))
        w_dep_cm = math.sqrt(max(1e-24, w_sq))
        w_dep_um = w_dep_cm * 1e4

        # Depletion components in p-side and n-side:
        # x_p * Na = x_n * Nd => x_p = W * Nd / (Na + Nd), x_n = W * Na / (Na + Nd)
        x_p_cm = w_dep_cm * (nd / (na + nd))
        x_n_cm = w_dep_cm * (na / (na + nd))

        # Peak electric field at metallurgical junction (x = 0):
        # E_max = 2 * barrier_v / W
        e_max_v_cm = (2.0 * barrier_v) / w_dep_cm

        # Junction capacitance: Cj = (eps_s * Area) / W
        c_j_f = (eps_s * area) / w_dep_cm
        c_j_pf = c_j_f * 1e12

        # Zero-bias capacitance Cj0
        w0_sq = (2.0 * eps_s * v_bi / Q_ELEM) * ((1.0 / na) + (1.0 / nd))
        w0_cm = math.sqrt(max(1e-24, w0_sq))
        c_j0_pf = ((eps_s * area) / w0_cm) * 1e12

        # Space charge Q_j = q * Na * x_p * Area = q * Nd * x_n * Area
        q_j_c = Q_ELEM * na * x_p_cm * area

        # Check critical breakdown field
        is_breakdown = e_max_v_cm > props["breakdown_field_v_cm"]

        return {
            "material": mat,
            "material_name": props["name"],
            "temperature_k": T,
            "na_cm3": na,
            "nd_cm3": nd,
            "v_applied_v": va,
            "effective_barrier_v": round(barrier_v, 4),
            "built_in_potential_v": round(v_bi, 4),
            "depletion_width_um": round(w_dep_um, 4),
            "depletion_width_cm": w_dep_cm,
            "x_p_um": round(x_p_cm * 1e4, 4),
            "x_n_um": round(x_n_cm * 1e4, 4),
            "peak_electric_field_v_cm": round(e_max_v_cm, 1),
            "junction_capacitance_pf": round(c_j_pf, 4),
            "zero_bias_capacitance_pf": round(c_j0_pf, 4),
            "depletion_charge_pc": round(q_j_c * 1e12, 4),
            "is_avalanche_breakdown_risk": is_breakdown,
            "breakdown_field_v_cm": props["breakdown_field_v_cm"]
        }


# Global singleton instance for platform-wide use
semiconductor_physics_engine = SemiconductorPhysicsEngine()
