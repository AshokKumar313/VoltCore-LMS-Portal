"""
========================================================================================
VoltCore Apex Academia - RF Smith Chart & Impedance Matching Engine
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Lead RF Circuit Designer & Systems Architect: Ashok Kumar A
========================================================================================
Capabilities:
  1. Complex Reflection Coefficient (Gamma) Analysis:
       Gamma = (ZL - Z0) / (ZL + Z0) = (zL - 1) / (zL + 1)
       Magnitude |Gamma|, Phase angle, Voltage Standing Wave Ratio (VSWR):
       VSWR = (1 + |Gamma|) / (1 - |Gamma|)
       Return Loss (RL_dB = -20*log10(|Gamma|)), Mismatch Loss (ML_dB)
  2. Normalized Impedance (z = r + jx) <-> Normalized Admittance (y = g + jb) Transformation:
       y = 1 / z = (r - jx) / (r^2 + x^2)
       Inversion on Smith Chart corresponds to 180-degree rotation (Gamma -> -Gamma).
  3. Single-Stub Transmission Line Impedance Matching:
       Calculates distance d/lambda from load to stub location and stub length l/lambda
       for both Short-Circuit (-cot(beta*l)) and Open-Circuit (tan(beta*l)) stubs.
       Provides both analytical solution branches (Branch 1 & Branch 2).
  4. Quarter-Wave Transformer Matching:
       ZT = sqrt(Z0 * RL) for purely real resistive loads.
  5. Parametric Constant Resistance Circles & Reactance Arcs for UI Canvas Rendering:
       (u - r/(1+r))^2 + v^2 = (1/(1+r))^2
       (u - 1)^2 + (v - 1/x)^2 = (1/x)^2
  6. Passive CPU profile (<5% utilization) and SQLite WAL mode persistence.
========================================================================================
"""

import os
import math
import cmath
import json
import sqlite3
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Union

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")

# Speed of light in vacuum (m/s)
C_LIGHT = 2.99792458e8


def complex_from_input(val: Union[Dict[str, float], complex, List[float], float, int]) -> complex:
    """Helper to convert varied JSON representations into Python complex."""
    if isinstance(val, complex):
        return val
    if isinstance(val, (int, float)):
        return complex(float(val), 0.0)
    if isinstance(val, (list, tuple)) and len(val) >= 2:
        return complex(float(val[0]), float(val[1]))
    if isinstance(val, dict):
        re_val = float(val.get("r", val.get("re", val.get("real", 0.0))))
        im_val = float(val.get("x", val.get("im", val.get("imag", 0.0))))
        return complex(re_val, im_val)
    return complex(50.0, 0.0)


class RFSmithChartEngine:
    """
    Unified RF microwave engine for Smith Chart calculations, complex reflection coefficients,
    normalized immittance mapping, and transmission line stub impedance matching.
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
                CREATE TABLE IF NOT EXISTS rf_matching_history (
                    design_id TEXT PRIMARY KEY,
                    design_type TEXT NOT NULL,
                    z0 REAL NOT NULL,
                    z_load_real REAL NOT NULL,
                    z_load_imag REAL NOT NULL,
                    gamma_mag REAL NOT NULL,
                    vswr REAL NOT NULL,
                    frequency_hz REAL,
                    solutions_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)
            conn.commit()
        finally:
            conn.close()

    def calculate_reflection_coefficient(
        self,
        z_load: Union[complex, Dict[str, float], float],
        z0: float = 50.0
    ) -> Dict[str, Any]:
        """
        Computes complex reflection coefficient Gamma = (ZL - Z0) / (ZL + Z0),
        along with magnitude |Gamma|, phase angle (degrees), VSWR, Return Loss (dB),
        and Mismatch Loss (dB).
        """
        zl_c = complex_from_input(z_load)
        z0_val = max(1e-3, float(z0))

        # Normalized load impedance zL = r + jx
        zl_norm = zl_c / z0_val
        r = zl_norm.real
        x = zl_norm.imag

        # Gamma = (zL - 1) / (zL + 1)
        denom = zl_norm + 1.0
        if abs(denom) < 1e-12:
            gamma = complex(1.0, 0.0)
        else:
            gamma = (zl_norm - 1.0) / denom

        gamma_mag = abs(gamma)
        gamma_phase_rad = cmath.phase(gamma)
        gamma_phase_deg = math.degrees(gamma_phase_rad)

        # Voltage Standing Wave Ratio: VSWR = (1 + |Gamma|) / (1 - |Gamma|)
        if gamma_mag >= 0.99999:
            vswr = 999.0
        else:
            vswr = (1.0 + gamma_mag) / (1.0 - gamma_mag)

        # Return Loss: RL = -20 * log10(|Gamma|) dB
        if gamma_mag > 1e-6:
            return_loss_db = -20.0 * math.log10(gamma_mag)
        else:
            return_loss_db = 120.0  # Perfect match

        # Mismatch Loss: ML = -10 * log10(1 - |Gamma|^2) dB
        gamma_sq = min(0.99999, gamma_mag ** 2)
        mismatch_loss_db = -10.0 * math.log10(max(1e-12, 1.0 - gamma_sq))

        # Transmission coefficient T = 1 + Gamma
        trans_coeff = 1.0 + gamma

        return {
            "status": "SUCCESS",
            "z_load_ohms": {"real": round(zl_c.real, 4), "imag": round(zl_c.imag, 4)},
            "z0_ohms": z0_val,
            "normalized_impedance": {"r": round(r, 4), "x": round(x, 4)},
            "gamma": {"real": round(gamma.real, 5), "imag": round(gamma.imag, 5)},
            "reflection_coefficient": {"real": round(gamma.real, 5), "imag": round(gamma.imag, 5)},
            "gamma_magnitude": round(gamma_mag, 5),
            "gamma_phase_deg": round(gamma_phase_deg, 2),
            "vswr": round(vswr, 3),
            "return_loss_db": round(return_loss_db, 2),
            "mismatch_loss_db": round(mismatch_loss_db, 2),
            "transmission_coefficient": {"real": round(trans_coeff.real, 5), "imag": round(trans_coeff.imag, 5)},
            "is_matched": gamma_mag < 0.05
        }

    def convert_impedance_to_admittance(
        self,
        z_load: Union[complex, Dict[str, float], float],
        z0: float = 50.0
    ) -> Dict[str, Any]:
        """
        Transforms normalized impedance z = r + jx into normalized admittance y = g + jb = 1/z.
        Actual admittance Y = y / Z0 in Siemens (S).
        """
        zl_c = complex_from_input(z_load)
        z0_val = max(1e-3, float(z0))
        z_norm = zl_c / z0_val

        # y = 1 / z = (r - jx) / (r^2 + x^2)
        denom = (z_norm.real ** 2) + (z_norm.imag ** 2)
        if denom < 1e-12:
            y_norm = complex(1e6, 0.0)
        else:
            y_norm = complex(z_norm.real / denom, -z_norm.imag / denom)

        # Actual admittance Y in Siemens
        y_siemens = y_norm / z0_val

        return {
            "status": "SUCCESS",
            "z_load_ohms": {"real": round(zl_c.real, 4), "imag": round(zl_c.imag, 4)},
            "z_norm": {"r": round(z_norm.real, 4), "x": round(z_norm.imag, 4)},
            "normalized_impedance": {"r": round(z_norm.real, 4), "x": round(z_norm.imag, 4)},
            "y_norm": {"g": round(y_norm.real, 4), "b": round(y_norm.imag, 4)},
            "normalized_admittance": {"g": round(y_norm.real, 4), "b": round(y_norm.imag, 4)},
            "y_siemens": {
                "g_ms": round(y_siemens.real * 1000.0, 4),
                "b_ms": round(y_siemens.imag * 1000.0, 4)
            },
            "admittance_siemens": {
                "conductance_mS": round(y_siemens.real * 1000.0, 4),
                "susceptance_mS": round(y_siemens.imag * 1000.0, 4)
            }
        }

    def convert_reflection_to_impedance(
        self,
        gamma: Union[complex, Dict[str, float]],
        z0: float = 50.0
    ) -> Dict[str, Any]:
        """
        Converts complex reflection coefficient Gamma back to normalized impedance z = (1+Gamma)/(1-Gamma).
        """
        gamma_c = complex_from_input(gamma)
        z0_val = max(1e-3, float(z0))

        denom = 1.0 - gamma_c
        if abs(denom) < 1e-12:
            z_norm = complex(1e6, 0.0)
        else:
            z_norm = (1.0 + gamma_c) / denom

        zl = z_norm * z0_val
        return {
            "status": "SUCCESS",
            "gamma": {"real": round(gamma_c.real, 5), "imag": round(gamma_c.imag, 5)},
            "z_norm": {"r": round(z_norm.real, 4), "x": round(z_norm.imag, 4)},
            "normalized_impedance": {"r": round(z_norm.real, 4), "x": round(z_norm.imag, 4)},
            "z_load_ohms": {"real": round(zl.real, 4), "imag": round(zl.imag, 4)},
            "impedance_ohms": {"r": round(zl.real, 4), "x": round(zl.imag, 4)}
        }

    def design_single_stub_match(
        self,
        z_load: Union[complex, Dict[str, float], float],
        z0: float = 50.0,
        stub_type: str = "SHORT",
        frequency_hz: float = 1e9
    ) -> Dict[str, Any]:
        """
        Designs a single-stub shunt impedance matching network:
          - Finds distance d/lambda from load to stub where Re(y(d)) = 1.0
          - Finds stub length l/lambda required to cancel imaginary susceptance b(d)
          - Evaluates both Solution Branch 1 and Solution Branch 2
          - Computes physical dimensions (mm) for the specified operating frequency
          - Verifies matched input reflection coefficient Gamma_in = 0.0
        """
        zl_c = complex_from_input(z_load)
        z0_val = max(1e-3, float(z0))
        freq = max(1e6, float(frequency_hz))
        stype = stub_type.strip().upper()
        is_short = stype.startswith("SHORT")

        # Wavelength lambda in meters: lambda = c / f
        lambda_m = C_LIGHT / freq
        lambda_mm = lambda_m * 1000.0

        # Load reflection coefficient Gamma_L
        z_norm = zl_c / z0_val
        denom = z_norm + 1.0
        gamma_l = (z_norm - 1.0) / denom if abs(denom) > 1e-12 else complex(1.0, 0.0)
        gamma_mag = abs(gamma_l)
        theta_l = cmath.phase(gamma_l)

        # If already matched (|Gamma| < 1e-4)
        if gamma_mag < 1e-4:
            solution_identity = {
                "branch": 1,
                "d_over_lambda": 0.0,
                "l_over_lambda": 0.0,
                "d_mm": 0.0,
                "l_mm": 0.0,
                "line_susceptance_b": 0.0,
                "stub_susceptance_b": 0.0,
                "matched_gamma_mag": 0.0,
                "matched_vswr": 1.0
            }
            return {
                "status": "ALREADY_MATCHED",
                "message": "Load is already matched to characteristic impedance Z0.",
                "z_load_ohms": {"real": zl_c.real, "imag": zl_c.imag},
                "z0_ohms": z0_val,
                "frequency_hz": freq,
                "wavelength_mm": round(lambda_mm, 2),
                "solutions": [solution_identity, solution_identity]
            }

        # Solve for distance d where Re(y(d)) = 1.0:
        # |Gamma(d)| = |Gamma_L|, phase(Gamma(d)) = theta_L - 2*beta*d
        # Re(y(d)) = 1.0 <=> cos(theta_L - 2*beta*d) = -|Gamma_L|
        mag_clamped = min(0.99999, gamma_mag)
        phi = math.acos(-mag_clamped)

        # Branch 1: 2*beta*d1 = theta_L - phi (mod 2*pi)
        angle1 = (theta_l - phi) % (2.0 * math.pi)
        d1_lambda = angle1 / (4.0 * math.pi)

        # Branch 2: 2*beta*d2 = theta_L + phi (mod 2*pi)
        angle2 = (theta_l + phi) % (2.0 * math.pi)
        d2_lambda = angle2 / (4.0 * math.pi)

        # Exact line admittance y(d) = (1 - Gamma(d)) / (1 + Gamma(d))
        def eval_line_admittance(d_lam: float) -> Tuple[complex, float]:
            beta_d = 2.0 * math.pi * d_lam
            gamma_d = gamma_l * cmath.exp(complex(0.0, -2.0 * beta_d))
            denom_y = 1.0 + gamma_d
            y_d = (1.0 - gamma_d) / denom_y if abs(denom_y) > 1e-12 else complex(1.0, 0.0)
            return y_d, y_d.imag

        y1_line, b1_line = eval_line_admittance(d1_lambda)
        y2_line, b2_line = eval_line_admittance(d2_lambda)

        # Required stub susceptance to cancel line susceptance: b_stub = -b_line
        b1_stub = -b1_line
        b2_stub = -b2_line

        # Stub length l/lambda:
        # For Short-circuit: y_stub = -j * cot(beta*l) => b_stub = -cot(beta*l) => tan(beta*l) = -1/b_stub = 1/(-b_stub)
        # For Open-circuit:  y_stub = +j * tan(beta*l) => b_stub = tan(beta*l)  => tan(beta*l) = b_stub
        def compute_stub_length(b_s: float) -> float:
            if is_short:
                ang = math.atan2(1.0, -b_s) % math.pi
            else:
                ang = math.atan2(b_s, 1.0) % math.pi
            l_lam = ang / (2.0 * math.pi)
            return (l_lam % 0.5)

        l1_lambda = compute_stub_length(b1_stub)
        l2_lambda = compute_stub_length(b2_stub)

        # Verification of matched input reflection coefficient
        def verify_match(d_lam: float, l_lam: float) -> Tuple[float, float]:
            beta_d = 2.0 * math.pi * d_lam
            gamma_d = gamma_l * cmath.exp(complex(0.0, -2.0 * beta_d))
            denom_y = 1.0 + gamma_d
            y_d = (1.0 - gamma_d) / denom_y if abs(denom_y) > 1e-12 else complex(1.0, 0.0)

            # Stub admittance
            beta_l = 2.0 * math.pi * l_lam
            if is_short:
                tan_bl = math.tan(beta_l)
                y_stub = complex(0.0, -1.0 / tan_bl) if abs(tan_bl) > 1e-6 else complex(0.0, -1e6)
            else:
                y_stub = complex(0.0, math.tan(beta_l))

            y_total = y_d + y_stub
            denom_g = y_total + 1.0
            gamma_in = (1.0 - y_total) / denom_g if abs(denom_g) > 1e-12 else complex(0.0, 0.0)
            g_mag = abs(gamma_in)
            vswr_v = (1.0 + g_mag) / (1.0 - g_mag) if g_mag < 0.999 else 999.0
            return g_mag, vswr_v

        g1_mag, vswr1 = verify_match(d1_lambda, l1_lambda)
        g2_mag, vswr2 = verify_match(d2_lambda, l2_lambda)

        branch1 = {
            "branch": 1,
            "d_over_lambda": round(d1_lambda, 4),
            "distance_d_wavelengths": round(d1_lambda, 4),
            "l_over_lambda": round(l1_lambda, 4),
            "stub_length_l_wavelengths": round(l1_lambda, 4),
            "d_mm": round(d1_lambda * lambda_mm, 2),
            "distance_d_mm": round(d1_lambda * lambda_mm, 2),
            "l_mm": round(l1_lambda * lambda_mm, 2),
            "stub_length_l_mm": round(l1_lambda * lambda_mm, 2),
            "line_susceptance_b": round(b1_line, 4),
            "stub_susceptance_b": round(b1_stub, 4),
            "matched_gamma_mag": round(g1_mag, 6),
            "matched_gamma_magnitude": round(g1_mag, 6),
            "matched_vswr": round(vswr1, 3)
        }

        branch2 = {
            "branch": 2,
            "d_over_lambda": round(d2_lambda, 4),
            "distance_d_wavelengths": round(d2_lambda, 4),
            "l_over_lambda": round(l2_lambda, 4),
            "stub_length_l_wavelengths": round(l2_lambda, 4),
            "d_mm": round(d2_lambda * lambda_mm, 2),
            "distance_d_mm": round(d2_lambda * lambda_mm, 2),
            "l_mm": round(l2_lambda * lambda_mm, 2),
            "stub_length_l_mm": round(l2_lambda * lambda_mm, 2),
            "line_susceptance_b": round(b2_line, 4),
            "stub_susceptance_b": round(b2_stub, 4),
            "matched_gamma_mag": round(g2_mag, 6),
            "matched_gamma_magnitude": round(g2_mag, 6),
            "matched_vswr": round(vswr2, 3)
        }

        # Persist design to SQLite WAL
        design_id = f"RF_STUB_{int(time.time() * 1000)}_{os.urandom(2).hex()}"
        now_str = datetime.now(timezone.utc).isoformat()
        conn = self._get_connection()
        try:
            conn.execute("""
                INSERT INTO rf_matching_history (
                    design_id, design_type, z0, z_load_real, z_load_imag,
                    gamma_mag, vswr, frequency_hz, solutions_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                design_id, f"SINGLE_STUB_{stype}", z0_val, zl_c.real, zl_c.imag,
                gamma_mag, (1.0 + gamma_mag) / max(1e-4, 1.0 - gamma_mag),
                freq, json.dumps([branch1, branch2]), now_str
            ))
            conn.commit()
        finally:
            conn.close()

        return {
            "status": "SUCCESS",
            "design_id": design_id,
            "stub_type": "SHORT_CIRCUIT" if is_short else "OPEN_CIRCUIT",
            "z_load_ohms": {"real": zl_c.real, "imag": zl_c.imag},
            "z0_ohms": z0_val,
            "frequency_hz": freq,
            "wavelength_mm": round(lambda_mm, 2),
            "unmatched_gamma_mag": round(gamma_mag, 5),
            "solutions": [branch1, branch2]
        }

    def design_quarter_wave_transformer(
        self,
        r_load: float,
        z0: float = 50.0,
        frequency_hz: float = 1e9
    ) -> Dict[str, Any]:
        """
        Designs a Quarter-Wave Transformer for purely real resistive load:
          ZT = sqrt(Z0 * RL), length l = lambda / 4.
        """
        if float(r_load) <= 0.0:
            return {
                "status": "ERROR",
                "error": "Load resistance must be strictly positive (R_L > 0)."
            }

        rl = float(r_load)
        z0_val = max(1e-3, float(z0))
        freq = max(1e6, float(frequency_hz))

        zt = math.sqrt(z0_val * rl)
        lambda_m = C_LIGHT / freq
        l_quarter_mm = (lambda_m / 4.0) * 1000.0

        # Unmatched reflection coefficient
        gamma_unmatched = abs((rl - z0_val) / (rl + z0_val))
        vswr_unmatched = (1.0 + gamma_unmatched) / max(1e-4, 1.0 - gamma_unmatched)

        return {
            "status": "SUCCESS",
            "transformer_type": "QUARTER_WAVE",
            "r_load_ohms": rl,
            "z0_ohms": z0_val,
            "zt_characteristic_impedance_ohms": round(zt, 3),
            "transformer_characteristic_impedance_z_t": round(zt, 3),
            "frequency_hz": freq,
            "wavelength_mm": round(lambda_m * 1000.0, 2),
            "transformer_length_mm": round(l_quarter_mm, 2),
            "physical_length_mm": round(l_quarter_mm, 2),
            "length_over_lambda": 0.25,
            "electrical_length_wavelengths": 0.25,
            "unmatched_vswr": round(vswr_unmatched, 3),
            "matched_vswr": 1.0,
            "matched_gamma_mag": 0.0
        }

    def generate_smith_chart_grid(self) -> Dict[str, Any]:
        """
        Generates standard parametric Smith Chart coordinate circles and arcs
        for client-side SVG rendering:
          - Constant Resistance Circles: r in [0, 0.2, 0.5, 1.0, 2.0, 5.0]
            Center = (r / (1 + r), 0), Radius = 1 / (1 + r)
          - Constant Reactance Arcs: x in [+-0.2, +-0.5, +-1.0, +-2.0, +-5.0]
            Center = (1.0, 1 / x), Radius = 1 / |x|
        """
        r_values = [0.0, 0.2, 0.5, 1.0, 2.0, 5.0]
        x_values = [0.2, 0.5, 1.0, 2.0, 5.0]

        resistance_circles = []
        for r in r_values:
            center_u = r / (1.0 + r)
            radius = 1.0 / (1.0 + r)
            resistance_circles.append({
                "r": r,
                "r_value": r,
                "center_x": round(center_u, 4),
                "center_y": 0.0,
                "center_u": round(center_u, 4),
                "center_v": 0.0,
                "radius": round(radius, 4)
            })

        reactance_arcs = []
        for x in x_values:
            # Parametric points along arc for SVG paths
            pts_ind = [
                {"u": round(1.0 - (1.0 / x) * math.sin(i * math.pi / 20.0), 4),
                 "v": round((1.0 / x) * (1.0 - math.cos(i * math.pi / 20.0)), 4)}
                for i in range(11)
            ]
            pts_cap = [
                {"u": round(1.0 - (1.0 / x) * math.sin(i * math.pi / 20.0), 4),
                 "v": round(-(1.0 / x) * (1.0 - math.cos(i * math.pi / 20.0)), 4)}
                for i in range(11)
            ]
            # Positive inductive arc (upper hemisphere)
            reactance_arcs.append({
                "x": x,
                "x_value": x,
                "type": "INDUCTIVE",
                "center_x": 1.0,
                "center_y": round(1.0 / x, 4),
                "center_u": 1.0,
                "center_v": round(1.0 / x, 4),
                "radius": round(1.0 / x, 4),
                "points": pts_ind
            })
            # Negative capacitive arc (lower hemisphere)
            reactance_arcs.append({
                "x": -x,
                "x_value": -x,
                "type": "CAPACITIVE",
                "center_x": 1.0,
                "center_y": round(-1.0 / x, 4),
                "center_u": 1.0,
                "center_v": round(-1.0 / x, 4),
                "radius": round(1.0 / x, 4),
                "points": pts_cap
            })

        return {
            "status": "SUCCESS",
            "outer_boundary_radius": 1.0,
            "resistance_circles": resistance_circles,
            "reactance_arcs": reactance_arcs
        }


# Global singleton instance for platform-wide use
rf_smith_chart_engine = RFSmithChartEngine()
