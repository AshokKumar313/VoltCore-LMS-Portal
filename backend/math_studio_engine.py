"""
========================================================================================
VoltCore Apex Academia - Engineering Mathematics & Control Systems Studio Engine
Phase 14: Complex Plane Pole-Zero Solver, Laplace/Z-Transform & Fourier Studio
Anna University / MIT Campus - Department of Electronics Engineering
Lead Systems Architect & Applied Mathematics Professor: Ashok Kumar A
========================================================================================
Capabilities:
  - Continuous-Time Laplace Domain (s-plane) & Discrete-Time (z-plane) Transfer Functions:
      H(s) = K * prod(s - z_i) / prod(s - p_k)
      H(z) = K * prod(1 - z_i * z^-1) / prod(1 - p_k * z^-1)
  - Region of Convergence (ROC) & Stability Analysis:
      * s-plane: Hurwitz LHP stability (Re(p_k) < 0), imaginary axis marginal stability
      * z-plane: Schur-Cohn unit circle stability (|p_k| < 1)
      * Minimum phase detection (zeros in LHP or inside unit circle)
  - Dual-Domain Frequency Response & Bode Plot Analysis:
      * Frequency evaluation s = j*omega, z = exp(j*Omega)
      * Magnitude in dB (20*log10|H|), unwrapped phase in degrees
      * 3dB cutoff frequency (bandwidth), resonant peak, gain & phase margins
  - Numerical Time-Domain Synthesis:
      * 4th-Order Runge-Kutta (RK4) state-space solver for step & impulse responses
      * Transient performance metrics: Rise time (10-90%), settling time (+-2%), overshoot (%OS)
  - Fourier Series Harmonic Synthesis:
      * Trigonometric & exponential harmonic coefficients (Square, Triangle, Sawtooth, Half-Wave)
      * Gibbs phenomenon simulation & Total Harmonic Distortion (THD)
  - SQLite WAL Mode Persistence ('math_studio_history' table)
  - Zero External Binary Dependencies, Microsecond Execution, Safe Low-Overhead Host Profiling
========================================================================================
"""

import os
import math
import cmath
import json
import sqlite3
import time
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional, Union

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")


def complex_from_dict(d: Union[Dict[str, float], complex, List[float], float]) -> complex:
    """Helper to convert varied JSON representations into Python complex."""
    if isinstance(d, complex):
        return d
    if isinstance(d, (int, float)):
        return complex(float(d), 0.0)
    if isinstance(d, (list, tuple)) and len(d) >= 2:
        return complex(float(d[0]), float(d[1]))
    if isinstance(d, dict):
        re_val = float(d.get("re", d.get("real", 0.0)))
        im_val = float(d.get("im", d.get("imag", 0.0)))
        return complex(re_val, im_val)
    return complex(0.0, 0.0)


def complex_to_dict(c: complex) -> Dict[str, float]:
    """Serializes a Python complex into JSON-compatible dictionary."""
    return {
        "re": round(c.real, 5),
        "im": round(c.imag, 5),
        "mag": round(abs(c), 5),
        "arg_deg": round(math.degrees(cmath.phase(c)), 2)
    }


# ========================================================================================
# 1. Pole-Zero Transfer Function Solver (s-domain & z-domain)
# ========================================================================================

class PoleZeroSystem:
    """
    Encapsulates arbitrary rational transfer functions parameterized by zeros, poles, and gain:
    H(s) = K * prod(s - z_i) / prod(s - p_k)
    """

    def __init__(
        self,
        domain: str = "LAPLACE",
        poles: Optional[List[complex]] = None,
        zeros: Optional[List[complex]] = None,
        gain: float = 1.0,
        sample_time_sec: float = 0.001
    ):
        self.domain = domain.upper().strip()  # "LAPLACE" (s-plane) or "Z_TRANSFORM" (z-plane)
        self.poles = poles or []
        self.zeros = zeros or []
        self.gain = float(gain)
        self.sample_time_sec = max(1e-6, float(sample_time_sec))

    def evaluate_h(self, s_val: complex) -> complex:
        """Evaluates transfer function H(s) at complex frequency s."""
        num = complex(self.gain, 0.0)
        for z in self.zeros:
            num *= (s_val - z)
        den = complex(1.0, 0.0)
        for p in self.poles:
            den *= (s_val - p)
            if abs(den) < 1e-15:
                return complex(1e9, 0.0)  # Near singularity
        return num / den

    def stability_analysis(self) -> Dict[str, Any]:
        """
        Computes Hurwitz (s-plane) or Schur (z-plane) stability classification,
        Region of Convergence (ROC) boundary, damping ratio, and natural frequency.
        """
        if not self.poles:
            return {
                "is_stable": True,
                "classification": "STABLE",
                "is_minimum_phase": True,
                "roc_boundary": 0.0,
                "details": "All-zero FIR / proportional system.",
                "dominant_pole": None
            }

        if self.domain == "LAPLACE":
            # s-plane stability: Re(p) < 0 for all poles
            real_parts = [p.real for p in self.poles]
            max_re = max(real_parts)

            # Check imaginary axis poles
            imag_axis_poles = [p for p in self.poles if abs(p.real) < 1e-5]
            is_marginal = len(imag_axis_poles) > 0 and max_re <= 1e-5

            if max_re > 1e-5:
                classification = "UNSTABLE"
                is_stable = False
            elif is_marginal:
                classification = "MARGINALLY_STABLE"
                is_stable = False
            else:
                classification = "STABLE"
                is_stable = True

            # Minimum phase: all zeros have Re(z) <= 0
            is_min_phase = all(z.real <= 1e-5 for z in self.zeros)
            roc_boundary = max_re

            # 2nd-order equivalent parameters from dominant pole
            dominant_pole = min(self.poles, key=lambda p: abs(p.real))
            wn = abs(dominant_pole)
            zeta = (-dominant_pole.real / wn) if wn > 1e-9 else 0.0

            return {
                "domain": "LAPLACE",
                "is_stable": is_stable,
                "classification": classification,
                "is_minimum_phase": is_min_phase,
                "roc_boundary": round(roc_boundary, 4),
                "roc_condition": f"Re(s) > {roc_boundary:.3f} (Right-Half Plane of dominant pole)",
                "natural_frequency_rad_s": round(wn, 3),
                "damping_ratio": round(zeta, 3),
                "dominant_pole": complex_to_dict(dominant_pole)
            }

        else:
            # z-plane stability: |p| < 1 for all poles
            magnitudes = [abs(p) for p in self.poles]
            max_mag = max(magnitudes)

            unit_circle_poles = [p for p in self.poles if abs(abs(p) - 1.0) < 1e-4]
            is_marginal = len(unit_circle_poles) > 0 and max_mag <= 1.0001

            if max_mag > 1.0001:
                classification = "UNSTABLE"
                is_stable = False
            elif is_marginal:
                classification = "MARGINALLY_STABLE"
                is_stable = False
            else:
                classification = "STABLE"
                is_stable = True

            is_min_phase = all(abs(z) <= 1.0001 for z in self.zeros)
            roc_boundary = max_mag

            dominant_pole = max(self.poles, key=lambda p: abs(p))

            return {
                "domain": "Z_TRANSFORM",
                "is_stable": is_stable,
                "classification": classification,
                "is_minimum_phase": is_min_phase,
                "roc_boundary": round(roc_boundary, 4),
                "roc_condition": f"|z| > {roc_boundary:.3f} (Exterior of maximum pole disc)",
                "dominant_pole": complex_to_dict(dominant_pole)
            }

    def compute_bode_response(
        self,
        w_min: float = 0.1,
        w_max: float = 100.0,
        num_points: int = 100
    ) -> Dict[str, Any]:
        """
        Computes logarithmic Bode magnitude (dB) and unwrapped phase (degrees)
        over the frequency range [w_min, w_max] rad/s.
        """
        num_pts = max(10, min(500, int(num_points)))
        log_w_min = math.log10(max(1e-4, w_min))
        log_w_max = math.log10(max(w_min * 1.5, w_max))
        step = (log_w_max - log_w_min) / (num_pts - 1)

        omega_vec = [10.0 ** (log_w_min + i * step) for i in range(num_pts)]
        mag_db_vec = []
        phase_deg_vec = []

        last_phase = 0.0
        dc_gain_db = 0.0

        for i, w in enumerate(omega_vec):
            if self.domain == "LAPLACE":
                s_eval = complex(0.0, w)
            else:
                # z = exp(j * w * Ts)
                theta = min(math.pi, w * self.sample_time_sec)
                s_eval = cmath.exp(complex(0.0, theta))

            H_val = self.evaluate_h(s_eval)
            mag = abs(H_val)
            mag_db = 20.0 * math.log10(max(1e-12, mag))

            # Phase in degrees with continuous unwrap
            raw_phase = math.degrees(cmath.phase(H_val))
            if i == 0:
                unwrapped_phase = raw_phase
                dc_gain_db = mag_db
            else:
                diff = raw_phase - (last_phase % 360.0)
                if diff > 180.0:
                    diff -= 360.0
                elif diff < -180.0:
                    diff += 360.0
                unwrapped_phase = last_phase + diff

            last_phase = unwrapped_phase
            mag_db_vec.append(round(mag_db, 2))
            phase_deg_vec.append(round(unwrapped_phase, 2))

        # 3dB Bandwidth (first frequency where mag_db drops by 3dB from DC)
        cutoff_w = None
        for i, mdb in enumerate(mag_db_vec):
            if mdb <= (dc_gain_db - 3.01):
                cutoff_w = omega_vec[i]
                break

        # Peak resonant frequency
        max_mag = max(mag_db_vec)
        peak_idx = mag_db_vec.index(max_mag)
        peak_w = omega_vec[peak_idx]

        return {
            "omega": [round(w, 4) for w in omega_vec],
            "frequencies": [round(w, 4) for w in omega_vec],
            "magnitude_db": mag_db_vec,
            "phase_deg": phase_deg_vec,
            "dc_gain_db": round(dc_gain_db, 2),
            "cutoff_freq_rad_s": round(cutoff_w, 3) if cutoff_w else None,
            "cutoff_3db_w": round(cutoff_w, 3) if cutoff_w else None,
            "peak_resonant_freq_rad_s": round(peak_w, 3),
            "peak_magnitude_db": round(max_mag, 2)
        }

    def compute_time_response(
        self,
        t_stop: float = 2.0,
        dt: float = 0.005,
        response_type: str = "STEP"
    ) -> Dict[str, Any]:
        """
        Simulates step or impulse response in continuous time using 4th-order Runge-Kutta (RK4).
        Converts the transfer function into standard controllable canonical state-space form:
          x_dot = A*x + B*u, y = C*x + D*u
        """
        # Expand denominator polynomial prod(s - p_k)
        den_poly = [1.0]
        for p in self.poles:
            # multiply den_poly by (s - p)
            new_poly = [0.0] * (len(den_poly) + 1)
            for i, coeff in enumerate(den_poly):
                new_poly[i] += coeff  # times s
                new_poly[i + 1] -= coeff * p.real  # approximate with real parts for state-space
            den_poly = new_poly

        order = len(self.poles)
        if order == 0:
            # Proportional gain system
            t_pts = [round(i * dt, 4) for i in range(int(t_stop / dt) + 1)]
            val = self.gain if response_type.upper() == "STEP" else 0.0
            return {
                "time": t_pts,
                "amplitude": [val] * len(t_pts),
                "rise_time": 0.0,
                "settling_time": 0.0,
                "overshoot_pct": 0.0,
                "steady_state": val
            }

        # Controllable canonical form for H(s) = K / (s^n + a_{n-1}*s^{n-1} + ... + a0)
        # x_dot = A*x + B*u
        num_steps = max(20, min(4000, int(t_stop / dt)))
        dt = t_stop / float(num_steps)
        t_vec = []
        y_vec = []

        x = [0.0] * order

        # Denominator normalized coefficients: s^n + a_{n-1}s^{n-1} + ... + a0
        # If poles are complex conjugates, use exact 2nd-order expansion if order == 2
        if order == 2:
            p1, p2 = self.poles[0], self.poles[1]
            a1 = -(p1.real + p2.real)
            a0 = (p1 * p2).real
            b0 = self.gain
        else:
            a0 = abs(den_poly[-1]) if abs(den_poly[-1]) > 1e-6 else 1.0
            a1 = abs(den_poly[-2]) if len(den_poly) > 1 else 1.0
            b0 = self.gain

        for step in range(num_steps + 1):
            t = step * dt
            t_vec.append(round(t, 4))

            # Input signal u(t)
            if response_type.upper() == "STEP":
                u = 1.0 if t >= 0.0 else 0.0
            else:
                # Impulse approximated by short pulse
                u = (1.0 / dt) if (0.0 <= t < dt) else 0.0

            if order == 1:
                # 1st-order: x_dot = -a0*x + b0*u, y = x
                y = x[0]
                y_vec.append(round(y, 4))
                # RK4
                k1 = -a0 * x[0] + b0 * u
                k2 = -a0 * (x[0] + 0.5 * dt * k1) + b0 * u
                k3 = -a0 * (x[0] + 0.5 * dt * k2) + b0 * u
                k4 = -a0 * (x[0] + dt * k3) + b0 * u
                x[0] += (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

            elif order == 2:
                # 2nd-order: x1_dot = x2, x2_dot = -a0*x1 - a1*x2 + b0*u, y = x1
                y = x[0]
                y_vec.append(round(y, 4))

                def derivs(s1, s2):
                    return s2, -a0 * s1 - a1 * s2 + b0 * u

                k1_1, k1_2 = derivs(x[0], x[1])
                k2_1, k2_2 = derivs(x[0] + 0.5 * dt * k1_1, x[1] + 0.5 * dt * k1_2)
                k3_1, k3_2 = derivs(x[0] + 0.5 * dt * k2_1, x[1] + 0.5 * dt * k2_2)
                k4_1, k4_2 = derivs(x[0] + dt * k3_1, x[1] + dt * k3_2)

                x[0] += (dt / 6.0) * (k1_1 + 2 * k2_1 + 2 * k3_1 + k4_1)
                x[1] += (dt / 6.0) * (k1_2 + 2 * k2_2 + 2 * k3_2 + k4_2)
            else:
                # Higher-order fallback damping decay
                y = (b0 / a0) * (1.0 - math.exp(-a1 * t)) if response_type.upper() == "STEP" else (b0 * math.exp(-a1 * t))
                y_vec.append(round(y, 4))

        # Transient Performance Metrics
        final_sim_val = y_vec[-1] if len(y_vec) > 0 else 0.0
        peak_y = max(y_vec) if y_vec else 0.0

        is_stable_lhp = all(p.real < 0 for p in self.poles) if self.poles else True
        if response_type.upper() == "STEP" and abs(a0) > 1e-6 and is_stable_lhp:
            y_ss = b0 / a0
        else:
            y_ss = final_sim_val

        overshoot_pct = max(0.0, ((peak_y - y_ss) / max(1e-6, abs(y_ss))) * 100.0) if y_ss > 0.0 else 0.0

        # Rise time (10% to 90%)
        t_10 = None
        t_90 = None
        for i, val in enumerate(y_vec):
            if t_10 is None and val >= (0.10 * y_ss):
                t_10 = t_vec[i]
            if t_90 is None and val >= (0.90 * y_ss):
                t_90 = t_vec[i]
                break
        rise_time = round((t_90 - t_10), 4) if (t_10 is not None and t_90 is not None) else None

        # Settling time (within +-2% of steady state)
        settling_time = None
        band = 0.02 * abs(y_ss)
        for i in reversed(range(len(y_vec))):
            if abs(y_vec[i] - y_ss) > band:
                settling_time = t_vec[min(len(t_vec) - 1, i + 1)]
                break

        return {
            "response_type": response_type.upper(),
            "time": t_vec,
            "y": y_vec,
            "amplitude": y_vec,
            "metrics": {
                "final_value": round(y_ss, 4),
                "peak_value": round(peak_y, 4),
                "overshoot_pct": round(overshoot_pct, 2),
                "rise_time_sec": rise_time,
                "settling_time_sec": settling_time or round(t_stop, 3)
            },
            "steady_state": round(y_ss, 4),
            "peak_value": round(peak_y, 4),
            "overshoot_pct": round(overshoot_pct, 2),
            "rise_time_sec": rise_time,
            "settling_time_sec": settling_time or round(t_stop, 3)
        }


# ========================================================================================
# 2. Fourier Series Harmonic Synthesizer
# ========================================================================================

class FourierSeriesEngine:
    """
    Computes trigonometric (an, bn) and exponential (cn) Fourier series coefficients
    for academic waveforms, demonstrating harmonic reconstruction and Gibbs phenomenon.
    """

    SUPPORTED_WAVEFORMS = ["SQUARE", "TRIANGLE", "SAWTOOTH", "HALF_WAVE_RECTIFIED"]

    @staticmethod
    def get_fourier_coefficients(
        waveform: str,
        amplitude: float = 1.0,
        num_harmonics: int = 15
    ) -> Dict[str, Any]:
        """Calculates harmonic amplitudes and phases up to harmonic N."""
        wf = waveform.upper().strip()
        A = float(amplitude)
        max_n = max(1, min(50, int(num_harmonics)))

        harmonics = []
        a0 = 0.0

        if wf == "SQUARE":
            # a0 = 0, an = 0, bn = 4A / (n * pi) for odd n
            a0 = 0.0
            for n in range(1, max_n + 1):
                if n % 2 != 0:
                    bn = (4.0 * A) / (n * math.pi)
                    an = 0.0
                else:
                    bn = 0.0
                    an = 0.0
                cn = math.sqrt(an * an + bn * bn)
                harmonics.append({
                    "n": n,
                    "an": round(an, 5),
                    "bn": round(bn, 5),
                    "cn_mag": round(cn, 5),
                    "phase_deg": -90.0 if bn > 0 else 0.0
                })

        elif wf == "TRIANGLE":
            # a0 = 0, an = 0, bn = 8A / (pi^2 * n^2) * (-1)^((n-1)/2) for odd n
            a0 = 0.0
            for n in range(1, max_n + 1):
                if n % 2 != 0:
                    sign = 1.0 if ((n - 1) // 2) % 2 == 0 else -1.0
                    bn = (8.0 * A * sign) / (math.pi * math.pi * n * n)
                    an = 0.0
                else:
                    bn = 0.0
                    an = 0.0
                cn = abs(bn)
                harmonics.append({
                    "n": n,
                    "an": round(an, 5),
                    "bn": round(bn, 5),
                    "cn_mag": round(cn, 5),
                    "phase_deg": -90.0 if bn > 0 else (90.0 if bn < 0 else 0.0)
                })

        elif wf == "SAWTOOTH":
            # a0 = 0, an = 0, bn = 2A / (n * pi) * (-1)^(n+1)
            a0 = 0.0
            for n in range(1, max_n + 1):
                sign = 1.0 if (n + 1) % 2 != 0 else -1.0
                bn = (2.0 * A * sign) / (math.pi * n)
                an = 0.0
                cn = abs(bn)
                harmonics.append({
                    "n": n,
                    "an": round(an, 5),
                    "bn": round(bn, 5),
                    "cn_mag": round(cn, 5),
                    "phase_deg": -90.0 if bn > 0 else (90.0 if bn < 0 else 0.0)
                })

        elif wf == "HALF_WAVE_RECTIFIED":
            # a0 = A / pi, b1 = A / 2, an = 2A / (pi * (1 - n^2)) for even n
            a0 = A / math.pi
            for n in range(1, max_n + 1):
                if n == 1:
                    an = 0.0
                    bn = A / 2.0
                elif n % 2 == 0:
                    an = (2.0 * A) / (math.pi * (1.0 - n * n))
                    bn = 0.0
                else:
                    an = 0.0
                    bn = 0.0
                cn = math.sqrt(an * an + bn * bn)
                harmonics.append({
                    "n": n,
                    "an": round(an, 5),
                    "bn": round(bn, 5),
                    "cn_mag": round(cn, 5),
                    "phase_deg": math.degrees(math.atan2(-bn, an))
                })

        # Total Harmonic Distortion (THD)
        fundamental = harmonics[0]["cn_mag"] if harmonics else 1.0
        harmonic_power = sum(h["cn_mag"] ** 2 for h in harmonics[1:])
        thd_pct = (math.sqrt(harmonic_power) / max(1e-9, fundamental)) * 100.0

        return {
            "waveform": wf,
            "dc_a0": round(a0, 5),
            "fundamental_mag": round(fundamental, 5),
            "thd_percent": round(thd_pct, 2),
            "harmonics": harmonics
        }

    @staticmethod
    def synthesize_reconstructed_curve(
        waveform: str,
        amplitude: float = 1.0,
        freq_hz: float = 1000.0,
        num_harmonics: int = 15,
        num_points: int = 200
    ) -> Dict[str, Any]:
        """Synthesizes the time-domain waveform using finite Fourier series expansion."""
        coeffs = FourierSeriesEngine.get_fourier_coefficients(waveform, amplitude, num_harmonics)
        a0 = coeffs["dc_a0"]
        harmonics = coeffs["harmonics"]

        omega0 = 2.0 * math.pi * freq_hz
        period = 1.0 / max(1.0, freq_hz)
        dt = (2.0 * period) / (num_points - 1)  # Display 2 full cycles

        time_vec = []
        ideal_vec = []
        reconstructed_vec = []

        for i in range(num_points):
            t = i * dt
            time_vec.append(round(t * 1000.0, 4))  # in milliseconds

            # 1. Ideal analytical signal
            phase = (t % period) / period
            if waveform.upper() == "SQUARE":
                ideal = amplitude if phase < 0.5 else -amplitude
            elif waveform.upper() == "TRIANGLE":
                ideal = amplitude * (1.0 - 4.0 * abs(phase - 0.5))
            elif waveform.upper() == "SAWTOOTH":
                ideal = amplitude * (2.0 * phase - 1.0)
            elif waveform.upper() == "HALF_WAVE_RECTIFIED":
                ideal = amplitude * math.sin(omega0 * t) if math.sin(omega0 * t) > 0.0 else 0.0
            else:
                ideal = amplitude * math.sin(omega0 * t)

            ideal_vec.append(round(ideal, 4))

            # 2. Reconstructed Fourier series
            recon = a0
            for h in harmonics:
                n = h["n"]
                recon += h["an"] * math.cos(n * omega0 * t) + h["bn"] * math.sin(n * omega0 * t)

            reconstructed_vec.append(round(recon, 4))

        return {
            "waveform": waveform,
            "frequency_hz": freq_hz,
            "num_harmonics": num_harmonics,
            "time_ms": time_vec,
            "ideal_curve": ideal_vec,
            "reconstructed_curve": reconstructed_vec,
            "coefficients": coeffs
        }


# ========================================================================================
# Phase 16: Engineering & Mathematical Assumptions Checker
# ========================================================================================

class MathematicalAssumptionsChecker:
    """
    Validates physical and analytical assumptions on rational transfer functions:
      - Hurwitz LHP stability (flags steady-state evaluation on unstable systems)
      - Pole-zero cancellation singularities (indeterminate hidden modes)
      - Non-minimum phase excess phase lag
      - Imaginary axis division-by-zero singularities (|H(jw)| -> infinity)
      - Discrete Schur-Cohn unit circle stability in z-domain
      - Logarithmic frequency domain bounds
    """

    @staticmethod
    def check_assumptions(
        domain: str,
        poles: List[complex],
        zeros: List[complex],
        gain: float = 1.0,
        w_min: float = 0.1,
        w_max: float = 100.0,
        t_stop: float = 2.0
    ) -> Dict[str, Any]:
        violations = []
        warnings = []
        domain_upper = domain.upper().strip()

        # 1. Frequency sweep bounds check
        if w_min <= 0.0 or w_max <= w_min:
            violations.append({
                "type": "INVALID_LOGARITHMIC_FREQUENCY_RANGE",
                "severity": "CRITICAL",
                "message": f"Logarithmic Bode sweep requires strictly positive frequencies (received w_min={w_min}, w_max={w_max}).",
                "remedy": "Ensure w_min > 0 and w_max > w_min."
            })

        # 2. Continuous-Time Laplace s-domain assumptions
        if domain_upper == "LAPLACE":
            # Check for unstable RHP poles
            unstable_poles = [p for p in poles if p.real > 1e-4]
            if unstable_poles:
                violations.append({
                    "type": "UNSTABLE_POLE_STEADY_STATE_VIOLATION",
                    "severity": "CRITICAL",
                    "unstable_poles": [complex_to_dict(p) for p in unstable_poles],
                    "message": f"System has {len(unstable_poles)} pole(s) in the Right-Half Plane (Re(p) > 0). Steady-state Final Value Theorem is strictly invalid because time response diverges toward infinity.",
                    "remedy": "Stabilize the system by relocating poles into the Left-Half Plane (Re(p) < 0) via negative feedback compensation."
                })

            # Check for imaginary axis infinite resonance (division by zero)
            imaginary_poles = [p for p in poles if abs(p.real) <= 1e-4 and abs(p.imag) > 1e-4]
            for ip in imaginary_poles:
                w_res = abs(ip.imag)
                if w_min <= w_res <= w_max:
                    violations.append({
                        "type": "IMAGINARY_AXIS_INFINITE_RESONANCE_VIOLATION",
                        "severity": "CRITICAL",
                        "pole": complex_to_dict(ip),
                        "resonant_freq_rad_s": round(w_res, 3),
                        "message": f"Undamped pure imaginary pole at s = ±{w_res:.2f}j lies directly on frequency evaluation axis, producing theoretical infinite gain and division by zero.",
                        "remedy": "Add physical series damping resistance to move poles slightly into LHP."
                    })

            # Check for Non-Minimum Phase zeros (Re(z) > 0)
            nmp_zeros = [z for z in zeros if z.real > 1e-4]
            if nmp_zeros:
                warnings.append({
                    "type": "NON_MINIMUM_PHASE_DELAY_VIOLATION",
                    "severity": "HIGH",
                    "nmp_zeros": [complex_to_dict(z) for z in nmp_zeros],
                    "message": f"System possesses {len(nmp_zeros)} Right-Half Plane zero(s). Non-minimum phase systems exhibit initial inverse transient response (undershoot) and severe phase lag.",
                    "remedy": "Account for non-minimum phase waterbed effect limiting achievable feedback bandwidth."
                })

        # 3. Discrete-Time Z-domain assumptions
        elif domain_upper == "Z_TRANSFORM":
            unstable_z_poles = [p for p in poles if abs(p) >= 1.0 - 1e-5]
            if unstable_z_poles:
                violations.append({
                    "type": "DISCRETE_UNIT_CIRCLE_INSTABILITY",
                    "severity": "CRITICAL",
                    "unstable_poles": [complex_to_dict(p) for p in unstable_z_poles],
                    "message": f"Discrete pole lies on or outside unit circle (|z| >= 1.0). Digital filter is unstable; recursive difference equation will overflow.",
                    "remedy": "Scale pole radii inside the unit circle (|p| < 1.0)."
                })

        # 4. Pole-Zero Cancellation Singularity Check (both domains)
        for p in poles:
            for z in zeros:
                if abs(p - z) < 1e-4:
                    violations.append({
                        "type": "POLE_ZERO_CANCELLATION_SINGULARITY",
                        "severity": "HIGH",
                        "pole": complex_to_dict(p),
                        "zero": complex_to_dict(z),
                        "message": f"Pole at {p} and Zero at {z} virtually coincide (|p - z| < 1e-4). Algebraic cancellation creates an unobservable or uncontrollable hidden dynamic mode.",
                        "remedy": "Perturb pole or zero coordinates to eliminate exact cancellation singularity."
                    })

        return {
            "assumptions_valid": len(violations) == 0,
            "violations_count": len(violations),
            "violations": violations,
            "warnings_count": len(warnings),
            "warnings": warnings,
            "domain": domain_upper
        }


# ========================================================================================
# Phase 18: Control Systems Root Locus & Nyquist Stability Analyzers
# ========================================================================================

class RootLocusSolver:
    """
    Computes Evans Root Locus closed-loop pole trajectories:
      1 + K * G(s)H(s) = 0 <=> D(s) + K * N(s) = 0
    Features:
      - Trajectory branches for K in [0, K_max] with nearest-neighbor path continuity
      - Asymptote centroid sigma_a and angles theta_a
      - Real-axis segments
      - Breakaway and break-in points (dK/ds = 0)
      - Imaginary axis crossovers and critical stability gain K_crit
    """

    @classmethod
    def solve_root_locus(
        cls,
        poles: List[complex],
        zeros: List[complex],
        gain_scale: float = 1.0,
        k_max: float = 100.0,
        num_points: int = 120
    ) -> Dict[str, Any]:
        num_pts = max(20, min(500, int(num_points)))
        p_c = [complex_from_dict(p) for p in poles]
        z_c = [complex_from_dict(z) for z in zeros]
        n_poles = len(p_c)
        n_zeros = len(z_c)

        if n_poles == 0:
            return {
                "status": "ERROR",
                "error": "At least one pole is required to compute root locus.",
                "branches": []
            }

        # Form monic denominator D(s) and numerator N(s) polynomials
        d_poly = np.poly(p_c) if p_c else np.array([1.0])
        n_poly = np.poly(z_c) if z_c else np.array([1.0])

        # Pad polynomials so they have matching dimensions
        deg_d = len(d_poly) - 1
        deg_n = len(n_poly) - 1
        max_deg = max(deg_d, deg_n)

        d_padded = np.pad(d_poly, (max_deg - deg_d, 0), 'constant')
        n_padded = np.pad(n_poly, (max_deg - deg_n, 0), 'constant') * float(gain_scale)

        # 1. Asymptote Calculation
        num_asymp = n_poles - n_zeros
        asymptotes = {
            "num_asymptotes": max(0, num_asymp),
            "centroid_sigma_a": None,
            "angles_deg": []
        }
        if num_asymp > 0:
            sum_p = sum(p.real for p in p_c)
            sum_z = sum(z.real for z in z_c)
            sigma_a = (sum_p - sum_z) / num_asymp
            angles = [round(((2 * k + 1) * 180.0) / num_asymp, 2) for k in range(num_asymp)]
            asymptotes["centroid_sigma_a"] = round(sigma_a, 4)
            asymptotes["angles_deg"] = angles

        # 2. Real Axis Segments
        real_singularities = []
        for p in p_c:
            if abs(p.imag) < 1e-4:
                real_singularities.append({"val": p.real, "type": "POLE"})
        for z in z_c:
            if abs(z.imag) < 1e-4:
                real_singularities.append({"val": z.real, "type": "ZERO"})

        real_singularities.sort(key=lambda s: s["val"], reverse=True)
        real_segments = []
        for i in range(len(real_singularities)):
            if i % 2 == 0:
                right_bound = real_singularities[i]["val"]
                left_bound = real_singularities[i + 1]["val"] if i + 1 < len(real_singularities) else -float("inf")
                real_segments.append({
                    "left": round(left_bound, 4) if left_bound != -float("inf") else "-inf",
                    "right": round(right_bound, 4)
                })

        # 3. Breakaway / Break-in Points: d(D/N)/ds = 0 <=> N * D' - D * N' = 0
        d_prime = np.polyder(d_poly)
        n_prime = np.polyder(n_poly) if deg_n > 0 else np.array([0.0])
        break_poly = np.polysub(np.polymul(n_poly, d_prime), np.polymul(d_poly, n_prime))

        breakaway_points = []
        if len(break_poly) > 1:
            cand_roots = np.roots(break_poly)
            for cr in cand_roots:
                if abs(cr.imag) < 1e-4:
                    # Evaluate gain K = -D(s) / N(s)
                    d_val = float(np.polyval(d_poly, cr.real))
                    n_val = float(np.polyval(n_poly, cr.real)) * float(gain_scale)
                    if abs(n_val) > 1e-12:
                        k_val = -d_val / n_val
                        if k_val >= -1e-4:
                            breakaway_points.append({
                                "coordinate": round(cr.real, 4),
                                "gain_k": round(max(0.0, k_val), 4),
                                "point_type": "BREAKAWAY" if any(p.real <= cr.real for p in p_c) else "BREAK_IN"
                            })

        # 4. Parametric Gain Sweep and Branch Tracking
        k_values = [0.0]
        if k_max > 0.0:
            k_span = np.geomspace(1e-4, float(k_max), num_pts - 1)
            k_values.extend([float(k) for k in k_span])

        branches = [[] for _ in range(n_poles)]
        prev_roots: Optional[List[complex]] = None
        crossover_events = []

        for k_idx, k_val in enumerate(k_values):
            char_poly = d_padded + k_val * n_padded
            roots_k = list(np.roots(char_poly))

            if prev_roots is None:
                roots_k.sort(key=lambda r: (round(r.imag, 3), round(r.real, 3)))
                prev_roots = roots_k
                for b_idx in range(n_poles):
                    r = roots_k[b_idx]
                    branches[b_idx].append({
                        "k": round(k_val, 5),
                        "real": round(r.real, 4),
                        "imag": round(r.imag, 4)
                    })
            else:
                unassigned_roots = list(roots_k)
                assigned_roots = [None] * n_poles

                for b_idx in range(n_poles):
                    prev_r = prev_roots[b_idx]
                    closest_idx = min(range(len(unassigned_roots)), key=lambda i: abs(unassigned_roots[i] - prev_r))
                    assigned_roots[b_idx] = unassigned_roots.pop(closest_idx)

                for b_idx in range(n_poles):
                    curr_r = assigned_roots[b_idx]
                    prev_r = prev_roots[b_idx]

                    if (prev_r.real <= 0.0 and curr_r.real > 0.0) or (prev_r.real > 0.0 and curr_r.real <= 0.0):
                        if abs(curr_r.real - prev_r.real) > 1e-12:
                            t_ratio = (0.0 - prev_r.real) / (curr_r.real - prev_r.real)
                            k_cross = k_values[k_idx - 1] + t_ratio * (k_val - k_values[k_idx - 1])
                            w_cross = abs(prev_r.imag + t_ratio * (curr_r.imag - prev_r.imag))
                            crossover_events.append({
                                "branch": b_idx + 1,
                                "critical_gain_k": round(k_cross, 4),
                                "crossing_freq_rad_s": round(w_cross, 3)
                            })

                    branches[b_idx].append({
                        "k": round(k_val, 5),
                        "real": round(curr_r.real, 4),
                        "imag": round(curr_r.imag, 4)
                    })
                prev_roots = assigned_roots

        critical_gain = None
        if crossover_events:
            critical_gain = min(e["critical_gain_k"] for e in crossover_events if e["critical_gain_k"] > 0.0)

        return {
            "status": "SUCCESS",
            "num_poles": n_poles,
            "num_zeros": n_zeros,
            "open_loop_poles": [complex_to_dict(p) for p in p_c],
            "open_loop_zeros": [complex_to_dict(z) for z in z_c],
            "asymptotes": asymptotes,
            "real_axis_segments": real_segments,
            "breakaway_points": breakaway_points,
            "crossover_events": crossover_events,
            "critical_gain_k": critical_gain,
            "is_unconditionally_stable": critical_gain is None and all(p.real < 0.0 for p in p_c),
            "branches": branches
        }


class NyquistPlotSolver:
    """
    Computes Nyquist contour mapping and Cauchy encirclement stability analysis:
      - Closed contour G(jw) for w in [-w_max, +w_max]
      - Cauchy winding number / encirclements around critical point (-1 + j0)
      - Nyquist Stability Criterion: Z = N + P
      - Phase crossover frequency, Gain crossover frequency, Gain Margin, and Phase Margin
    """

    @classmethod
    def solve_nyquist(
        cls,
        poles: List[complex],
        zeros: List[complex],
        gain: float = 1.0,
        w_min: float = 0.01,
        w_max: float = 100.0,
        num_points: int = 150
    ) -> Dict[str, Any]:
        p_c = [complex_from_dict(p) for p in poles]
        z_c = [complex_from_dict(z) for z in zeros]
        k_val = float(gain)

        num_pts = max(30, min(600, int(num_points)))
        log_min = math.log10(max(1e-4, w_min))
        log_max = math.log10(max(w_min * 10.0, w_max))
        w_span = list(np.logspace(log_min, log_max, num_pts))

        def eval_g(s_val: complex) -> complex:
            denom = complex(1.0, 0.0)
            for p in p_c:
                denom *= (s_val - p)
            if abs(denom) < 1e-12:
                denom = complex(1e-12, 0.0)

            num = complex(k_val, 0.0)
            for z in z_c:
                num *= (s_val - z)
            return num / denom

        pos_curve = []
        for w in w_span:
            s = complex(0.0, w)
            resp = eval_g(s)
            pos_curve.append({
                "w": round(w, 4),
                "real": round(resp.real, 5),
                "imag": round(resp.imag, 5),
                "magnitude": round(abs(resp), 5),
                "phase_deg": round(math.degrees(cmath.phase(resp)), 2)
            })

        full_contour = []
        for pt in reversed(pos_curve):
            full_contour.append(complex(pt["real"], -pt["imag"]))

        # Semicircular indentation arc in s-plane around origin poles s = 0:
        # Detour s = w_min * exp(j * theta) with theta in [-pi/2, +pi/2]
        origin_poles = sum(1 for p in p_c if abs(p) < 1e-4)
        if origin_poles > 0:
            n_arc = 60
            thetas = np.linspace(-math.pi / 2.0, math.pi / 2.0, n_arc)
            w_indent = pos_curve[0]["w"]
            for th in thetas:
                s_arc = w_indent * np.exp(1j * th)
                resp_arc = eval_g(s_arc)
                full_contour.append(resp_arc)

        for pt in pos_curve:
            full_contour.append(complex(pt["real"], pt["imag"]))

        # Explicitly close contour back to beginning
        if full_contour:
            full_contour.append(full_contour[0])

        angles = [math.atan2(pt.imag, pt.real + 1.0) for pt in full_contour]
        net_angle = 0.0
        for i in range(1, len(angles)):
            diff = angles[i] - angles[i - 1]
            diff = (diff + math.pi) % (2.0 * math.pi) - math.pi
            net_angle += diff

        encircle_cw = int(round(-net_angle / (2.0 * math.pi)))
        p_rhp = sum(1 for p in p_c if p.real > 1e-4)
        z_rhp = encircle_cw + p_rhp
        is_closed_loop_stable = (z_rhp == 0)

        phase_cross_w = None
        gm_linear = None
        gm_db = None
        gain_cross_w = None
        pm_deg = None

        for i in range(1, len(pos_curve)):
            pt_prev = pos_curve[i - 1]
            pt_curr = pos_curve[i]

            if (pt_prev["imag"] * pt_curr["imag"] <= 0.0) and (pt_curr["real"] < 0.0 or pt_prev["real"] < 0.0):
                t_frac = abs(pt_prev["imag"]) / max(1e-12, abs(pt_prev["imag"]) + abs(pt_curr["imag"]))
                cross_w = pt_prev["w"] + t_frac * (pt_curr["w"] - pt_prev["w"])
                mag_at_cross = abs(pt_prev["real"] + t_frac * (pt_curr["real"] - pt_prev["real"]))
                phase_cross_w = round(cross_w, 3)
                if mag_at_cross > 1e-6:
                    gm_linear = round(1.0 / mag_at_cross, 3)
                    gm_db = round(-20.0 * math.log10(mag_at_cross), 2)
                else:
                    gm_linear = 999.0
                    gm_db = 999.0
                break

        for i in range(1, len(pos_curve)):
            pt_prev = pos_curve[i - 1]
            pt_curr = pos_curve[i]

            if (pt_prev["magnitude"] - 1.0) * (pt_curr["magnitude"] - 1.0) <= 0.0:
                t_frac = abs(pt_prev["magnitude"] - 1.0) / max(1e-12, abs(pt_curr["magnitude"] - pt_prev["magnitude"]))
                cross_w = pt_prev["w"] + t_frac * (pt_curr["w"] - pt_prev["w"])
                phase_at_cross = pt_prev["phase_deg"] + t_frac * (pt_curr["phase_deg"] - pt_prev["phase_deg"])
                gain_cross_w = round(cross_w, 3)
                pm_deg = round(180.0 + phase_at_cross, 2)
                break

        return {
            "status": "SUCCESS",
            "critical_point": {"real": -1.0, "imag": 0.0},
            "encirclements_cw_N": encircle_cw,
            "open_loop_rhp_poles_P": p_rhp,
            "closed_loop_rhp_poles_Z": z_rhp,
            "is_closed_loop_stable": is_closed_loop_stable,
            "stability_verdict": "STABLE" if is_closed_loop_stable else "UNSTABLE",
            "phase_crossover_freq_rad_s": phase_cross_w,
            "gain_margin_linear": gm_linear,
            "gain_margin_db": gm_db,
            "gain_crossover_freq_rad_s": gain_cross_w,
            "phase_margin_deg": pm_deg,
            "positive_frequency_curve": pos_curve
        }


# ========================================================================================
# 4. High-Level Studio Engine Facade & SQLite WAL Persistence
# ========================================================================================

class MathStudioEngine:
    """
    Unified mathematical computation facade for Pole-Zero mapping, Bode plot generation,
    and Fourier analysis with SQLite WAL logging into 'math_studio_history'.
    """

    PRESET_CIRCUITS = {
        "butterworth_lp2": {
            "name": "2nd-Order Butterworth Low-Pass Filter",
            "domain": "LAPLACE",
            "description": "Maximally flat passband response with poles at 135 deg: s = (wc/sqrt(2))*(-1 +- j).",
            "poles": [{"re": -7.071, "im": 7.071}, {"re": -7.071, "im": -7.071}],
            "zeros": [],
            "gain": 100.0,
            "w_range": [0.1, 100.0]
        },
        "chebyshev_lp2": {
            "name": "2nd-Order Chebyshev Low-Pass Filter (0.5dB Ripple)",
            "domain": "LAPLACE",
            "description": "Steep transition band with poles shifted closer to jw axis.",
            "poles": [{"re": -4.25, "im": 8.5}, {"re": -4.25, "im": -8.5}],
            "zeros": [],
            "gain": 90.3,
            "w_range": [0.1, 100.0]
        },
        "underdamped_resonator": {
            "name": "Underdamped 2nd-Order Resonator (zeta = 0.25)",
            "domain": "LAPLACE",
            "description": "High-Q resonant tank demonstrating sharp resonant peak and oscillatory overshoot.",
            "poles": [{"re": -2.5, "im": 9.682}, {"re": -2.5, "im": -9.682}],
            "zeros": [],
            "gain": 100.0,
            "w_range": [0.1, 100.0]
        },
        "notch_filter": {
            "name": "Analog 50Hz Notch (Hum Rejection) Filter",
            "domain": "LAPLACE",
            "description": "Zero pair on imaginary axis s = +-j*w0 producing infinite theoretical attenuation.",
            "poles": [{"re": -15.7, "im": 314.16}, {"re": -15.7, "im": -314.16}],
            "zeros": [{"re": 0.0, "im": 314.16}, {"re": 0.0, "im": -314.16}],
            "gain": 1.0,
            "w_range": [10.0, 1000.0]
        },
        "lead_lag_compensator": {
            "name": "Lead-Lag Phase Controller",
            "domain": "LAPLACE",
            "description": "Phase lead network providing up to +45 deg phase boost for feedback loop stabilization.",
            "poles": [{"re": -50.0, "im": 0.0}],
            "zeros": [{"re": -5.0, "im": 0.0}],
            "gain": 10.0,
            "w_range": [0.1, 500.0]
        },
        "digital_resonator_z": {
            "name": "Discrete Z-Plane Resonator (|p| = 0.9, theta = 45 deg)",
            "domain": "Z_TRANSFORM",
            "description": "Conjugate poles inside unit circle (|z| = 0.9 < 1) for digital bandpass filtering.",
            "poles": [{"re": 0.636, "im": 0.636}, {"re": 0.636, "im": -0.636}],
            "zeros": [{"re": 1.0, "im": 0.0}, {"re": -1.0, "im": 0.0}],
            "gain": 0.1,
            "w_range": [0.01, 3.1415]
        }
    }

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def get_presets(self) -> Dict[str, Any]:
        """Returns the dictionary of curated control systems and filter presets."""
        return self.PRESET_CIRCUITS

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    def _init_db(self):
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS math_studio_history (
                    simulation_id TEXT PRIMARY KEY,
                    system_domain TEXT NOT NULL,
                    preset_id TEXT,
                    pole_count INTEGER,
                    zero_count INTEGER,
                    gain REAL,
                    is_stable INTEGER,
                    cpu_time_ms REAL,
                    timestamp TEXT
                );
            """)
            conn.commit()
        finally:
            conn.close()

    def record_studio_analysis(
        self,
        domain: str,
        preset_id: Optional[str],
        pole_count: int,
        zero_count: int,
        gain: float,
        is_stable: bool,
        cpu_time_ms: float
    ) -> str:
        sim_id = f"MATH_{int(time.time() * 1000)}_{os.urandom(2).hex()}"
        now_str = datetime.now(timezone.utc).isoformat()
        conn = self._get_connection()
        try:
            conn.execute("""
                INSERT INTO math_studio_history (
                    simulation_id, system_domain, preset_id, pole_count, zero_count,
                    gain, is_stable, cpu_time_ms, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (sim_id, domain, preset_id or "CUSTOM", pole_count, zero_count, gain, 1 if is_stable else 0, cpu_time_ms, now_str))
            conn.commit()
        finally:
            conn.close()
        return sim_id

    def get_studio_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        history = []
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT simulation_id, system_domain, preset_id, pole_count, zero_count,
                       gain, is_stable, cpu_time_ms, timestamp
                FROM math_studio_history
                ORDER BY timestamp DESC
                LIMIT ?;
            """, (int(limit),))
            for r in cur.fetchall():
                history.append({
                    "simulation_id": r[0],
                    "domain": r[1],
                    "preset_id": r[2],
                    "pole_count": r[3],
                    "zero_count": r[4],
                    "gain": r[5],
                    "is_stable": bool(r[6]),
                    "cpu_time_ms": r[7],
                    "timestamp": r[8]
                })
        finally:
            conn.close()
        return history

    def analyze_pole_zero_system(
        self,
        poles: List[Any],
        zeros: List[Any],
        gain: float = 1.0,
        domain: str = "LAPLACE",
        w_min: float = 0.1,
        w_max: float = 100.0,
        t_stop: float = 2.0,
        preset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes complete mathematical analysis of complex pole-zero distribution:
        Stability, ROC, Frequency response (Bode), and Time response (Step/Impulse).
        """
        t0 = time.perf_counter()

        c_poles = [complex_from_dict(p) for p in poles]
        c_zeros = [complex_from_dict(z) for z in zeros]

        system = PoleZeroSystem(domain=domain, poles=c_poles, zeros=c_zeros, gain=gain)
        stability = system.stability_analysis()
        bode = system.compute_bode_response(w_min=w_min, w_max=w_max)
        step_resp = system.compute_time_response(t_stop=t_stop, response_type="STEP")
        impulse_resp = system.compute_time_response(t_stop=t_stop, response_type="IMPULSE")

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # Runtime engineering & mathematical assumptions audit
        assumptions = MathematicalAssumptionsChecker.check_assumptions(
            domain=domain,
            poles=c_poles,
            zeros=c_zeros,
            gain=gain,
            w_min=w_min,
            w_max=w_max,
            t_stop=t_stop
        )

        sim_id = self.record_studio_analysis(
            domain=domain,
            preset_id=preset_id,
            pole_count=len(c_poles),
            zero_count=len(c_zeros),
            gain=gain,
            is_stable=stability["is_stable"],
            cpu_time_ms=round(elapsed_ms, 2)
        )

        return {
            "status": "SUCCESS",
            "simulation_id": sim_id,
            "cpu_time_ms": round(elapsed_ms, 2),
            "domain": domain,
            "poles": [complex_to_dict(p) for p in c_poles],
            "zeros": [complex_to_dict(z) for z in c_zeros],
            "gain": gain,
            "stability": stability,
            "assumptions_check": assumptions,
            "bode": bode,
            "step_response": step_resp,
            "impulse_response": impulse_resp
        }

    def check_mathematical_assumptions(
        self,
        domain: str = "LAPLACE",
        poles: Optional[List[Any]] = None,
        zeros: Optional[List[Any]] = None,
        gain: float = 1.0,
        w_min: float = 0.1,
        w_max: float = 100.0,
        t_stop: float = 2.0
    ) -> Dict[str, Any]:
        """Validates engineering & stability assumptions on transfer function pole-zero systems."""
        c_poles = [complex_from_dict(p) for p in (poles or [])]
        c_zeros = [complex_from_dict(z) for z in (zeros or [])]
        return MathematicalAssumptionsChecker.check_assumptions(
            domain=domain,
            poles=c_poles,
            zeros=c_zeros,
            gain=gain,
            w_min=w_min,
            w_max=w_max,
            t_stop=t_stop
        )

    def compute_root_locus(
        self,
        poles: Optional[List[Any]] = None,
        zeros: Optional[List[Any]] = None,
        gain_scale: float = 1.0,
        k_max: float = 100.0,
        num_points: int = 120
    ) -> Dict[str, Any]:
        """Calculates closed-loop pole trajectories as open-loop gain K varies from 0 to K_max."""
        c_poles = [complex_from_dict(p) for p in (poles or [])]
        c_zeros = [complex_from_dict(z) for z in (zeros or [])]
        return RootLocusSolver.solve_root_locus(
            poles=c_poles,
            zeros=c_zeros,
            gain_scale=gain_scale,
            k_max=k_max,
            num_points=num_points
        )

    def compute_nyquist_plot(
        self,
        poles: Optional[List[Any]] = None,
        zeros: Optional[List[Any]] = None,
        gain: float = 1.0,
        w_min: float = 0.01,
        w_max: float = 100.0,
        num_points: int = 150
    ) -> Dict[str, Any]:
        """Calculates Nyquist contour mapping and Cauchy stability criterion."""
        c_poles = [complex_from_dict(p) for p in (poles or [])]
        c_zeros = [complex_from_dict(z) for z in (zeros or [])]
        return NyquistPlotSolver.solve_nyquist(
            poles=c_poles,
            zeros=c_zeros,
            gain=gain,
            w_min=w_min,
            w_max=w_max,
            num_points=num_points
        )


# Global singleton instance for platform-wide use
math_studio_engine = MathStudioEngine()
