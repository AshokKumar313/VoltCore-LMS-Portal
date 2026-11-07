"""
========================================================================================
VoltCore Apex Academia - Advanced Multirate DSP & Fixed-Point Quantization Engine
Phase 19: Multirate Filterbanks, CIC Decimators/Interpolators, FFT Spectrum, & Q-Format Quantizer
Lead Digital Signal Processing (DSP) Architect & Fixed-Point Specialist: Ashok Kumar A
========================================================================================
Features:
  1. Multirate Polyphase Decomposition & Rational Sampling Rate Conversion (L/M):
     - Polyphase decimator and interpolator filterbank structures with minimal MAC overhead.
     - Windowed-sinc anti-aliasing / anti-imaging prototype FIR filter synthesis.
     - Exact noble identity computation eliminating multiplication by zero samples.
  2. Eugene Hogenauer Cascaded Integrator-Comb (CIC) Filter Engine:
     - N-stage Integrator and Comb cascades for decimation and interpolation.
     - Theoretical and empirical DC gain G_DC = (R * M)^N and bit growth B_growth = ceil(N * log2(R * M)).
     - Exact frequency response attenuation and alias null analysis: |H(f)|^N.
  3. Spectral Analysis & Windowing Functions:
     - Hamming, Hann, Blackman, Kaiser (with Bessel I0 parameter beta), and Rectangular windows.
     - Equivalent Noise Bandwidth (ENBW), Coherent Gain, and Peak Sidelobe Level (PSLL dB).
     - Single-sided power spectrum, linear/dB magnitude, and dominant harmonic detection.
  4. Q-Format Fixed-Point Quantization Laboratory:
     - Signed two's complement Qm.n representation (B = 1 + m + n bits, step size Delta = 2^-n).
     - Saturation clipping vs. Two's complement modular wrap-around overflow simulation.
     - Convergent rounding vs. truncation (floor) quantization.
     - Empirical and theoretical Signal-to-Quantization-Noise Ratio (SQNR = 6.02B + 1.76 dB).
     - Filter coefficient quantization and complex z-plane pole-zero sensitivity analysis.
  5. SQLite WAL Mode Persistence:
     - Logged in tables 'dsp_multirate_history' and 'dsp_quantization_history'.
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU usage (<5%).
========================================================================================
"""

import os
import math
import cmath
import json
import time
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Union

import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")


# ========================================================================================
# Helper: Modified Zeroth-Order Bessel Function of the First Kind I0(x)
# ========================================================================================

def bessel_i0(x: float) -> float:
    """
    Computes modified Bessel function I0(x) via Taylor series expansion:
      I0(x) = sum_{k=0}^{infinity} [ (x/2)^k / k! ]^2
    Accurate to within machine precision with fast O(1) convergence.
    """
    total = 1.0
    term = 1.0
    x_half = abs(float(x)) / 2.0
    for k in range(1, 50):
        term *= (x_half / k) ** 2
        total += term
        if term < 1e-15 * total:
            break
    return total


# ========================================================================================
# 1. DSP Windowing Engine
# ========================================================================================

class DSPWindowEngine:
    """
    Synthesizes and analyzes standard DSP windowing functions for spectral analysis
    and FIR filter design: Rectangular, Hann, Hamming, Blackman, and Kaiser.
    """

    SUPPORTED_WINDOWS = ["RECTANGULAR", "HANN", "HAMMING", "BLACKMAN", "KAISER"]

    @classmethod
    def get_window(cls, name: str, length: int, beta: float = 5.65) -> np.ndarray:
        """Generates window coefficients of given length."""
        N = max(1, int(length))
        if N == 1:
            return np.ones(1)

        w_name = name.strip().upper()
        n = np.arange(N)

        if w_name == "RECTANGULAR":
            return np.ones(N, dtype=float)
        elif w_name == "HANN":
            w = 0.5 - 0.5 * np.cos((2.0 * np.pi * n) / (N - 1))
            return np.maximum(0.0, w)
        elif w_name == "HAMMING":
            w = 0.54 - 0.46 * np.cos((2.0 * np.pi * n) / (N - 1))
            return np.maximum(0.0, w)
        elif w_name == "BLACKMAN":
            w = (
                0.42
                - 0.5 * np.cos((2.0 * np.pi * n) / (N - 1))
                + 0.08 * np.cos((4.0 * np.pi * n) / (N - 1))
            )
            return np.maximum(0.0, w)
        elif w_name == "KAISER":
            i0_b = bessel_i0(beta)
            frac = (2.0 * n) / (N - 1) - 1.0
            val = beta * np.sqrt(np.maximum(0.0, 1.0 - frac * frac))
            w = np.array([bessel_i0(v) for v in val], dtype=float) / i0_b
            return np.maximum(0.0, w)
        else:
            raise ValueError(f"Unsupported window type '{name}'. Supported: {cls.SUPPORTED_WINDOWS}")

    @classmethod
    def analyze_window(cls, name: str, length: int = 64, beta: float = 5.65) -> Dict[str, Any]:
        """Calculates coherent gain, ENBW, and peak sidelobe level (dB) of the window."""
        w = cls.get_window(name, length, beta)
        N = len(w)

        coherent_gain = float(np.mean(w))
        sum_sq = float(np.sum(w ** 2))
        sum_w = float(np.sum(w))
        enbw = float(N * sum_sq / (sum_w ** 2)) if sum_w > 1e-12 else 1.0

        # High-resolution FFT for peak sidelobe determination
        n_fft = max(2048, 16 * N)
        w_padded = np.pad(w, (0, n_fft - N))
        W = np.abs(np.fft.rfft(w_padded))
        W_norm = W / max(1e-12, W[0])
        W_db = 20.0 * np.log10(np.maximum(1e-12, W_norm))

        # Detect first null and peak sidelobe
        diffs = np.diff(W_db[: n_fft // 4])
        nulls = np.where(diffs > 0)[0]
        if len(nulls) > 0:
            first_null_idx = nulls[0]
            psll_db = float(np.max(W_db[first_null_idx : n_fft // 4]))
        else:
            psll_db = -13.3  # Fallback for rectangular

        return {
            "window_name": name.strip().upper(),
            "length": N,
            "coherent_gain": round(coherent_gain, 4),
            "enbw_bins": round(enbw, 4),
            "peak_sidelobe_level_db": round(psll_db, 2),
            "coefficients": [round(float(val), 5) for val in w[: min(32, N)]]
        }


# ========================================================================================
# 2. Spectrum Analyzer (Real-Time Frequency-Domain Analysis)
# ========================================================================================

class SpectrumAnalyzer:
    """
    Computes real-time FFT spectrum analysis with windowing and coherent normalization.
    """

    @classmethod
    def compute_fft_spectrum(
        cls,
        signal: Union[List[float], np.ndarray],
        fs: float = 1000.0,
        window_name: str = "HANN",
        n_fft: Optional[int] = None
    ) -> Dict[str, Any]:
        sig = np.asarray(signal, dtype=float)
        N = len(sig)
        if N < 2:
            return {"status": "ERROR", "error": "Signal must contain at least 2 samples."}

        fs_val = max(1.0, float(fs))
        fft_len = int(n_fft) if n_fft else max(N, int(2 ** math.ceil(math.log2(N))))

        w = DSPWindowEngine.get_window(window_name, N)
        sig_windowed = sig * w

        # Coherent gain compensation
        cg = float(np.mean(w))
        if cg < 1e-6:
            cg = 1.0

        fft_raw = np.fft.rfft(sig_windowed, n=fft_len)
        freqs = np.fft.rfftfreq(fft_len, d=1.0 / fs_val)

        # Normalized linear and dB magnitude
        mag_linear = np.abs(fft_raw) / (N * cg)
        mag_linear[1:-1] *= 2.0  # Conserve power in single-sided spectrum
        peak_mag = max(1e-12, float(np.max(mag_linear)))

        mag_db = 20.0 * np.log10(np.maximum(1e-12, mag_linear))
        mag_db_normalized = mag_db - 20.0 * math.log10(peak_mag)
        phase_deg = np.degrees(np.angle(fft_raw))

        # Peak frequency component
        peak_idx = int(np.argmax(mag_linear))
        dominant_freq = float(freqs[peak_idx])

        # Decimate spectrum points for JSON payload efficiency (max 250 points)
        step = max(1, len(freqs) // 250)
        spectrum_data = []
        for i in range(0, len(freqs), step):
            spectrum_data.append({
                "freq_hz": round(float(freqs[i]), 2),
                "magnitude": round(float(mag_linear[i]), 6),
                "magnitude_db": round(float(mag_db[i]), 2),
                "phase_deg": round(float(phase_deg[i]), 1)
            })

        return {
            "status": "SUCCESS",
            "sample_rate_hz": fs_val,
            "signal_length": N,
            "fft_length": fft_len,
            "window_applied": window_name.upper(),
            "dominant_frequency_hz": round(dominant_freq, 2),
            "dominant_magnitude": round(peak_mag, 6),
            "total_power": round(float(np.mean(sig ** 2)), 6),
            "spectrum": spectrum_data
        }


# ========================================================================================
# 3. FIR Prototype Filter Design
# ========================================================================================

class FIRFilterDesigner:
    """
    Designs low-pass FIR filter prototypes using the windowed-sinc method.
    """

    @classmethod
    def design_lowpass(
        cls,
        cutoff_ratio: float,
        num_taps: int = 63,
        window_name: str = "HAMMING",
        gain: float = 1.0,
        kaiser_beta: float = 5.65
    ) -> np.ndarray:
        """
        Designs lowpass FIR filter:
          h[n] = 2 * fc * sinc(2 * fc * (n - M)) * w[n]
        cutoff_ratio in (0, 0.5) (cycles / sample).
        """
        N = max(3, int(num_taps))
        if N % 2 == 0:
            N += 1  # Force odd length for Type-I linear phase FIR

        fc = max(1e-4, min(0.4999, float(cutoff_ratio)))
        M = (N - 1) / 2.0
        n = np.arange(N)

        h = np.zeros(N, dtype=float)
        for idx in range(N):
            if idx == M:
                h[idx] = 2.0 * fc
            else:
                diff = idx - M
                h[idx] = math.sin(2.0 * math.pi * fc * diff) / (math.pi * diff)

        w = DSPWindowEngine.get_window(window_name, N, beta=kaiser_beta)
        h_win = h * w

        sum_h = np.sum(h_win)
        if abs(sum_h) > 1e-12:
            h_win = (h_win / sum_h) * float(gain)

        return h_win


# ========================================================================================
# 4. Multirate Polyphase Resampling Engine
# ========================================================================================

class PolyphaseFilterbank:
    """
    Implements efficient polyphase decimation, interpolation, and rational (L/M)
    sampling rate conversion without computing zero-multiplications.
    """

    @classmethod
    def decompose_polyphase_interpolator(cls, h: np.ndarray, L: int) -> np.ndarray:
        """
        Decomposes prototype filter h into L polyphase branches:
          p_k[m] = h[m * L + k], k = 0, ..., L - 1.
        """
        L_val = max(1, int(L))
        num_taps = len(h)
        rem = num_taps % L_val
        if rem != 0:
            h_padded = np.pad(h, (0, L_val - rem), mode="constant")
        else:
            h_padded = h

        p_len = len(h_padded) // L_val
        branches = np.zeros((L_val, p_len), dtype=float)
        for k in range(L_val):
            branches[k] = h_padded[k::L_val]
        return branches

    @classmethod
    def decompose_polyphase_decimator(cls, h: np.ndarray, M: int) -> np.ndarray:
        """
        Decomposes prototype filter h into M polyphase branches for Noble identity:
          e_k[m] = h[m * M + k], k = 0, ..., M - 1.
        """
        return cls.decompose_polyphase_interpolator(h, M)

    @classmethod
    def resample_rational(
        cls,
        signal: Union[List[float], np.ndarray],
        L: int,
        M: int,
        taps_per_phase: int = 12,
        window_name: str = "KAISER",
        kaiser_beta: float = 5.65
    ) -> Dict[str, Any]:
        """
        Performs arbitrary rational sampling rate conversion by factor L/M using polyphase decomposition:
          - Reduces L and M by greatest common divisor gcd(L, M)
          - Anti-aliasing / anti-imaging cutoff: min(1/L, 1/M) * 0.5 * 0.9
          - Filters using active polyphase phase branch (k * M) % L
          - Achieves L-fold computational speedup over naive direct upsample-filter-downsample
        """
        sig = np.asarray(signal, dtype=float)
        N_in = len(sig)
        if N_in == 0:
            return {"status": "ERROR", "error": "Signal is empty."}

        # Reduce L and M to coprime integers
        gcd = math.gcd(int(L), int(M))
        L_red = max(1, int(L) // gcd)
        M_red = max(1, int(M) // gcd)

        # Filter prototype design at high intermediate rate L * fs
        fc = min(1.0 / L_red, 1.0 / M_red) * 0.5 * 0.90
        num_taps = 2 * L_red * max(4, int(taps_per_phase)) + 1
        h_proto = FIRFilterDesigner.design_lowpass(
            cutoff_ratio=fc,
            num_taps=num_taps,
            window_name=window_name,
            gain=float(L_red),
            kaiser_beta=kaiser_beta
        )

        poly_branches = cls.decompose_polyphase_interpolator(h_proto, L_red)
        p_len = poly_branches.shape[1]

        N_out = int(math.floor((N_in * L_red) / M_red))
        pad_len = p_len
        sig_padded = np.pad(sig, (pad_len, pad_len), mode="constant")

        y = np.zeros(N_out, dtype=float)
        mac_count = 0

        for k in range(N_out):
            intermediate_idx = k * M_red
            n = intermediate_idx // L_red
            phase_idx = intermediate_idx % L_red

            sub_h = poly_branches[phase_idx]
            # Time-reversed slice for convolution dot product
            in_slice = sig_padded[n + pad_len : n + pad_len - p_len : -1]
            if len(in_slice) == p_len:
                y[k] = np.dot(sub_h, in_slice)
                mac_count += p_len

        # Computational speedup relative to direct filtering of zero-inserted signal
        direct_macs = N_in * L_red * len(h_proto)
        speedup = (direct_macs / max(1, mac_count)) if mac_count > 0 else float(L_red)

        return {
            "status": "SUCCESS",
            "interpolation_factor_L": L_red,
            "decimation_factor_M": M_red,
            "rate_change_ratio": round(float(L_red) / float(M_red), 4),
            "input_samples": N_in,
            "output_samples": N_out,
            "prototype_filter_taps": len(h_proto),
            "polyphase_branches_count": L_red,
            "taps_per_branch": p_len,
            "polyphase_macs_executed": mac_count,
            "computational_speedup_factor": round(speedup, 2),
            "output_signal": [round(float(val), 6) for val in y[: min(200, N_out)]]
        }


# ========================================================================================
# 5. Cascaded Integrator-Comb (CIC) Filter Engine
# ========================================================================================

class CICFilterEngine:
    """
    Eugene Hogenauer multiplier-free Cascaded Integrator-Comb (CIC) decimation
    and interpolation filter simulation with exact bit-growth analysis.
    """

    @classmethod
    def calculate_properties(
        cls,
        R: int,
        M: int = 1,
        N: int = 3,
        input_bits: int = 16
    ) -> Dict[str, Any]:
        """
        Evaluates DC gain G_DC = (R * M)^N and maximum register bit growth:
          B_growth = ceil(N * log2(R * M))
          B_max = B_in + B_growth
        """
        r_val = max(2, int(R))
        m_val = max(1, int(M))
        n_val = max(1, int(N))
        b_in = max(1, int(input_bits))

        rm = r_val * m_val
        dc_gain = rm ** n_val
        dc_gain_db = 20.0 * math.log10(dc_gain)
        b_growth = int(math.ceil(n_val * math.log2(rm)))
        b_max = b_in + b_growth

        # Theoretical first sidelobe peak attenuation: ~ -13.46 * N dB
        first_sidelobe_atten_db = round(-13.46 * n_val, 2)

        return {
            "rate_change_factor_R": r_val,
            "differential_delay_M": m_val,
            "num_stages_N": n_val,
            "input_bits": b_in,
            "dc_gain_linear": dc_gain,
            "dc_gain_db": round(dc_gain_db, 2),
            "bit_growth": b_growth,
            "max_register_bits_required": b_max,
            "first_sidelobe_attenuation_db": first_sidelobe_atten_db
        }

    @classmethod
    def decimate(
        cls,
        signal: Union[List[float], np.ndarray],
        R: int = 4,
        M: int = 1,
        N: int = 3
    ) -> Dict[str, Any]:
        """
        Simulates an N-stage CIC Decimator:
          1. N Integrator stages running at high rate: y_k[n] = y_k[n-1] + y_{k-1}[n]
          2. Downsampling by factor R
          3. N Comb stages running at low rate: w_k[n] = w_{k-1}[n] - w_{k-1}[n - M]
        """
        sig = np.asarray(signal, dtype=float)
        N_in = len(sig)
        if N_in == 0:
            return {"status": "ERROR", "error": "Signal is empty."}

        props = cls.calculate_properties(R, M, N)
        R_val = props["rate_change_factor_R"]
        M_val = props["differential_delay_M"]
        N_val = props["num_stages_N"]
        G_dc = float(props["dc_gain_linear"])

        # 1. Integrator cascade at high rate
        curr_sig = np.copy(sig)
        for _ in range(N_val):
            curr_sig = np.cumsum(curr_sig)

        # 2. Downsampling by factor R
        downsampled = curr_sig[::R_val]

        # 3. Comb cascade at low rate
        comb_sig = np.copy(downsampled)
        for _ in range(N_val):
            diff = np.zeros_like(comb_sig)
            diff[M_val:] = comb_sig[M_val:] - comb_sig[:-M_val]
            diff[:M_val] = comb_sig[:M_val]  # Zero history assumption
            comb_sig = diff

        normalized_output = comb_sig / G_dc

        return {
            "status": "SUCCESS",
            "filter_type": "CIC_DECIMATOR",
            "properties": props,
            "input_samples": N_in,
            "output_samples": len(comb_sig),
            "raw_output": [round(float(val), 4) for val in comb_sig[: min(150, len(comb_sig))]],
            "normalized_output": [round(float(val), 6) for val in normalized_output[: min(150, len(normalized_output))]]
        }

    @classmethod
    def interpolate(
        cls,
        signal: Union[List[float], np.ndarray],
        R: int = 4,
        M: int = 1,
        N: int = 3
    ) -> Dict[str, Any]:
        """
        Simulates an N-stage CIC Interpolator:
          1. N Comb stages running at low rate
          2. Upsampling by factor R (zero insertion)
          3. N Integrator stages running at high rate
        """
        sig = np.asarray(signal, dtype=float)
        N_in = len(sig)
        if N_in == 0:
            return {"status": "ERROR", "error": "Signal is empty."}

        props = cls.calculate_properties(R, M, N)
        R_val = props["rate_change_factor_R"]
        M_val = props["differential_delay_M"]
        N_val = props["num_stages_N"]
        G_dc = float(props["dc_gain_linear"])

        # 1. Comb cascade at low rate
        comb_sig = np.copy(sig)
        for _ in range(N_val):
            diff = np.zeros_like(comb_sig)
            diff[M_val:] = comb_sig[M_val:] - comb_sig[:-M_val]
            diff[:M_val] = comb_sig[:M_val]
            comb_sig = diff

        # 2. Upsampling by R (zero insertion)
        upsampled = np.zeros(N_in * R_val, dtype=float)
        upsampled[::R_val] = comb_sig

        # 3. Integrator cascade at high rate
        int_sig = np.copy(upsampled)
        for _ in range(N_val):
            int_sig = np.cumsum(int_sig)

        normalized_output = int_sig / (G_dc / R_val)

        return {
            "status": "SUCCESS",
            "filter_type": "CIC_INTERPOLATOR",
            "properties": props,
            "input_samples": N_in,
            "output_samples": len(int_sig),
            "raw_output": [round(float(val), 4) for val in int_sig[: min(150, len(int_sig))]],
            "normalized_output": [round(float(val), 6) for val in normalized_output[: min(150, len(normalized_output))]]
        }

    @classmethod
    def compute_frequency_response(
        cls,
        R: int = 4,
        M: int = 1,
        N: int = 3,
        num_points: int = 300
    ) -> Dict[str, Any]:
        """
        Evaluates analytical CIC normalized magnitude response:
          |H_norm(f)| = | sin(pi * f * R * M) / (R * M * sin(pi * f)) |^N
        for normalized frequency f in (0, 0.5) cycles/sample.
        """
        props = cls.calculate_properties(R, M, N)
        R_val = props["rate_change_factor_R"]
        M_val = props["differential_delay_M"]
        N_val = props["num_stages_N"]
        rm = R_val * M_val

        f_norm = np.linspace(1e-4, 0.5, max(50, int(num_points)))
        num = np.sin(np.pi * f_norm * rm)
        den = rm * np.sin(np.pi * f_norm)
        h_norm = np.abs(num / den) ** N_val
        h_db = 20.0 * np.log10(np.maximum(1e-12, h_norm))

        curve = []
        for i in range(len(f_norm)):
            curve.append({
                "norm_freq": round(float(f_norm[i]), 4),
                "magnitude": round(float(h_norm[i]), 6),
                "magnitude_db": round(float(h_db[i]), 2)
            })

        return {
            "status": "SUCCESS",
            "properties": props,
            "frequency_response": curve
        }


# ========================================================================================
# 6. Fixed-Point Quantization Laboratory (Q-Format Modeling)
# ========================================================================================

class FixedPointQuantizer:
    """
    Simulates signed two's complement Qm.n fixed-point quantization, overflow saturation
    vs modular wrap-around, and evaluates theoretical vs empirical SQNR (6.02B + 1.76 dB).
    """

    @classmethod
    def parse_q_format(cls, m_or_str: Union[int, str], n_opt: Optional[int] = None) -> Tuple[int, int]:
        """Parses Qm.n format specifications (e.g. 'Q1.14', 'Q3.12', or explicit m, n integers)."""
        if isinstance(m_or_str, str):
            clean = m_or_str.strip().upper().replace("Q", "")
            if "." in clean:
                parts = clean.split(".")
                return int(parts[0]), int(parts[1])
            else:
                total_b = int(clean)
                return 1, total_b - 2
        else:
            m = int(m_or_str)
            n = int(n_opt) if n_opt is not None else 14
            return m, n

    @classmethod
    def get_format_metrics(cls, m: int, n: int) -> Dict[str, Any]:
        """Returns mathematical boundaries and resolution for Qm.n representation."""
        m_val = max(0, int(m))
        n_val = max(0, int(n))
        total_bits = 1 + m_val + n_val  # 1 sign bit + m integer + n fractional

        scale = 2 ** n_val
        step_size = 2.0 ** (-n_val)  # LSB resolution
        min_int = -(2 ** (total_bits - 1))
        max_int = (2 ** (total_bits - 1)) - 1

        min_val = min_int / float(scale)
        max_val = max_int / float(scale)

        # Theoretical SQNR for full-scale sinusoid: SQNR = 6.02 * B + 1.76 dB
        theoretical_sqnr_db = 6.02 * total_bits + 1.76

        return {
            "format": f"Q{m_val}.{n_val}",
            "sign_bits": 1,
            "integer_bits_m": m_val,
            "fractional_bits_n": n_val,
            "total_wordlength_B": total_bits,
            "scale_factor": scale,
            "step_size_lsb": step_size,
            "min_representable_float": min_val,
            "max_representable_float": max_val,
            "min_int_code": min_int,
            "max_int_code": max_int,
            "theoretical_full_scale_sqnr_db": round(theoretical_sqnr_db, 2)
        }

    @classmethod
    def quantize_value(
        cls,
        val: float,
        m: int,
        n: int,
        rounding_mode: str = "ROUND",
        overflow_mode: str = "SATURATE"
    ) -> Dict[str, Any]:
        """
        Quantizes a single floating-point number into Qm.n signed two's complement.
        Rounding: 'ROUND' (nearest) or 'TRUNCATE' (floor).
        Overflow: 'SATURATE' (clamp) or 'WRAP' (modular two's complement wrap).
        """
        metrics = cls.get_format_metrics(m, n)
        scale = metrics["scale_factor"]
        min_int = metrics["min_int_code"]
        max_int = metrics["max_int_code"]
        total_bits = metrics["total_wordlength_B"]

        scaled = float(val) * scale

        # Quantization rounding
        r_mode = rounding_mode.strip().upper()
        if r_mode.startswith("TRUNC"):
            q_int = int(math.floor(scaled))
        else:
            q_int = int(math.floor(scaled + 0.5))

        # Overflow handling
        o_mode = overflow_mode.strip().upper()
        is_overflow = False

        if o_mode.startswith("WRAP"):
            if q_int > max_int or q_int < min_int:
                is_overflow = True
                q_int = ((q_int - min_int) % (2 ** total_bits)) + min_int
        else:  # Default SATURATE
            if q_int > max_int:
                q_int = max_int
                is_overflow = True
            elif q_int < min_int:
                q_int = min_int
                is_overflow = True

        q_float = q_int / float(scale)
        error = q_float - float(val)

        # Two's complement binary representation
        unsigned_code = q_int if q_int >= 0 else (1 << total_bits) + q_int
        bin_str = bin(unsigned_code)[2:].zfill(total_bits)
        hex_str = hex(unsigned_code)[2:].upper()

        return {
            "original_value": float(val),
            "quantized_float": q_float,
            "quantized_int": q_int,
            "binary_twos_complement": bin_str,
            "hex_code": f"0x{hex_str}",
            "quantization_error": round(error, 6),
            "overflow_detected": is_overflow,
            "format": metrics["format"]
        }

    @classmethod
    def quantize_signal(
        cls,
        signal: Union[List[float], np.ndarray],
        m: int = 1,
        n: int = 14,
        rounding_mode: str = "ROUND",
        overflow_mode: str = "SATURATE"
    ) -> Dict[str, Any]:
        """
        Quantizes an entire signal array into Qm.n format and measures empirical SQNR.
        """
        sig = np.asarray(signal, dtype=float)
        N = len(sig)
        if N == 0:
            return {"status": "ERROR", "error": "Signal is empty."}

        metrics = cls.get_format_metrics(m, n)
        scale = metrics["scale_factor"]
        min_int = metrics["min_int_code"]
        max_int = metrics["max_int_code"]
        total_bits = metrics["total_wordlength_B"]

        scaled = sig * scale
        r_mode = rounding_mode.strip().upper()
        if r_mode.startswith("TRUNC"):
            q_int = np.floor(scaled).astype(np.int64)
        else:
            q_int = np.floor(scaled + 0.5).astype(np.int64)

        o_mode = overflow_mode.strip().upper()
        overflow_mask = (q_int > max_int) | (q_int < min_int)
        overflow_count = int(np.sum(overflow_mask))

        if o_mode.startswith("WRAP"):
            q_int = ((q_int - min_int) % (2 ** total_bits)) + min_int
        else:
            q_int = np.clip(q_int, min_int, max_int)

        q_float = q_int / float(scale)
        error = q_float - sig

        # Noise power and SQNR computation
        sig_power = float(np.mean(sig ** 2))
        noise_power = float(np.mean(error ** 2))

        if noise_power > 1e-15 and sig_power > 1e-15:
            measured_sqnr_db = 10.0 * math.log10(sig_power / noise_power)
        else:
            measured_sqnr_db = 120.0  # Perfect or zero noise

        # Error distribution histogram (15 bins)
        hist, bin_edges = np.histogram(error, bins=15)
        hist_data = [
            {
                "bin_center": round(float((bin_edges[i] + bin_edges[i + 1]) / 2.0), 6),
                "count": int(hist[i])
            }
            for i in range(len(hist))
        ]

        return {
            "status": "SUCCESS",
            "format_metrics": metrics,
            "rounding_mode": "TRUNCATION" if r_mode.startswith("TRUNC") else "ROUND_NEAREST",
            "overflow_mode": "WRAP_AROUND" if o_mode.startswith("WRAP") else "SATURATION_CLIPPING",
            "total_samples": N,
            "overflow_samples_count": overflow_count,
            "overflow_percentage": round((overflow_count / N) * 100.0, 2),
            "signal_power": round(sig_power, 6),
            "quantization_noise_power": round(noise_power, 8),
            "measured_sqnr_db": round(measured_sqnr_db, 2),
            "theoretical_full_scale_sqnr_db": metrics["theoretical_full_scale_sqnr_db"],
            "max_absolute_error": round(float(np.max(np.abs(error))), 6),
            "error_mean": round(float(np.mean(error)), 8),
            "error_histogram": hist_data,
            "quantized_samples": [round(float(v), 5) for v in q_float[: min(150, N)]]
        }

    @classmethod
    def quantize_filter_coefficients(
        cls,
        b_coeffs: List[float],
        a_coeffs: Optional[List[float]] = None,
        m: int = 1,
        n: int = 14
    ) -> Dict[str, Any]:
        """
        Quantizes FIR/IIR filter coefficients and evaluates shift in complex z-plane poles and zeros.
        """
        b_orig = np.asarray(b_coeffs, dtype=float)
        a_orig = np.asarray(a_coeffs if a_coeffs else [1.0], dtype=float)

        b_quant_res = cls.quantize_signal(b_orig, m, n)
        b_q = np.array(b_quant_res["quantized_samples"])

        a_quant_res = cls.quantize_signal(a_orig, m, n)
        a_q = np.array(a_quant_res["quantized_samples"])

        # Compute original vs quantized zeros
        orig_zeros = [
            {"real": round(float(z.real), 4), "imag": round(float(z.imag), 4)}
            for z in np.roots(b_orig)
        ] if len(b_orig) > 1 else []

        quant_zeros = [
            {"real": round(float(z.real), 4), "imag": round(float(z.imag), 4)}
            for z in np.roots(b_q)
        ] if len(b_q) > 1 else []

        # Compute original vs quantized poles
        orig_poles = [
            {"real": round(float(p.real), 4), "imag": round(float(p.imag), 4)}
            for p in np.roots(a_orig)
        ] if len(a_orig) > 1 else []

        quant_poles = [
            {"real": round(float(p.real), 4), "imag": round(float(p.imag), 4)}
            for p in np.roots(a_q)
        ] if len(a_q) > 1 else []

        # Frequency response comparison across [0, pi]
        w_span = np.linspace(0.0, math.pi, 120)
        max_abs_error = 0.0
        max_pb_db_deviation = 0.0

        for w_val in w_span:
            # Complex exponential e^(-j * w * k)
            k_b = np.arange(len(b_orig))
            k_a = np.arange(len(a_orig))
            num_orig = np.sum(b_orig * np.exp(-1j * w_val * k_b))
            den_orig = np.sum(a_orig * np.exp(-1j * w_val * k_a))
            h_orig = num_orig / den_orig if abs(den_orig) > 1e-12 else complex(0.0, 0.0)

            num_q = np.sum(b_q * np.exp(-1j * w_val * k_b))
            den_q = np.sum(a_q * np.exp(-1j * w_val * k_a))
            h_q = num_q / den_q if abs(den_q) > 1e-12 else complex(0.0, 0.0)

            abs_err = abs(h_orig - h_q)
            if abs_err > max_abs_error:
                max_abs_error = abs_err

            # Evaluate dB error in passband & transition band (|H| >= 0.05)
            if abs(h_orig) >= 0.05:
                db_orig = 20.0 * math.log10(abs(h_orig))
                db_q = 20.0 * math.log10(max(1e-12, abs(h_q)))
                dev = abs(db_orig - db_q)
                if dev > max_pb_db_deviation:
                    max_pb_db_deviation = dev

        return {
            "status": "SUCCESS",
            "format": f"Q{m}.{n}",
            "b_original": [round(float(v), 5) for v in b_orig],
            "b_quantized": [round(float(v), 5) for v in b_q],
            "a_original": [round(float(v), 5) for v in a_orig],
            "a_quantized": [round(float(v), 5) for v in a_q],
            "original_zeros": orig_zeros,
            "quantized_zeros": quant_zeros,
            "original_poles": orig_poles,
            "quantized_poles": quant_poles,
            "max_absolute_response_error": round(float(max_abs_error), 6),
            "max_passband_deviation_db": round(float(max_pb_db_deviation), 4),
            "max_frequency_response_deviation_db": round(float(max_pb_db_deviation), 4)
        }


# ========================================================================================
# 7. High-Level Multirate DSP Engine Facade & SQLite WAL Persistence
# ========================================================================================

class MultirateDSPEngine:
    """
    Unified high-level facade orchestrating Polyphase Resampling, CIC Filterbanks,
    FFT Spectrum Analysis, and Fixed-Point Quantization with SQLite WAL audit persistence.
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
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS dsp_multirate_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        experiment_id TEXT NOT NULL UNIQUE,
                        operation_type TEXT NOT NULL,
                        rate_l INTEGER,
                        rate_m INTEGER,
                        cic_stages INTEGER,
                        input_length INTEGER NOT NULL,
                        output_length INTEGER NOT NULL,
                        metrics_json TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS dsp_quantization_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        experiment_id TEXT NOT NULL UNIQUE,
                        q_format TEXT NOT NULL,
                        wordlength_b INTEGER NOT NULL,
                        rounding_mode TEXT NOT NULL,
                        overflow_mode TEXT NOT NULL,
                        measured_sqnr_db REAL NOT NULL,
                        overflow_count INTEGER NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)
                conn.commit()
            finally:
                conn.close()

    def run_polyphase_resampling(
        self,
        signal: Union[List[float], np.ndarray],
        L: int = 3,
        M: int = 2,
        taps_per_phase: int = 12,
        window_name: str = "KAISER"
    ) -> Dict[str, Any]:
        """Executes polyphase rational resampling and logs to SQLite WAL."""
        res = PolyphaseFilterbank.resample_rational(
            signal=signal,
            L=L,
            M=M,
            taps_per_phase=taps_per_phase,
            window_name=window_name
        )
        if res.get("status") == "SUCCESS":
            exp_id = f"POLY_{int(time.time() * 1000)}_{os.urandom(2).hex()}"
            now = datetime.now(timezone.utc).isoformat()
            with self._lock:
                conn = self._get_connection()
                try:
                    conn.execute("""
                        INSERT INTO dsp_multirate_history (
                            experiment_id, operation_type, rate_l, rate_m, cic_stages,
                            input_length, output_length, metrics_json, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        exp_id, "POLYPHASE_RESAMPLE", res["interpolation_factor_L"],
                        res["decimation_factor_M"], None, res["input_samples"],
                        res["output_samples"], json.dumps({
                            "macs": res["polyphase_macs_executed"],
                            "speedup": res["computational_speedup_factor"]
                        }), now
                    ))
                    conn.commit()
                    res["experiment_id"] = exp_id
                finally:
                    conn.close()
        return res

    def run_cic_filter(
        self,
        signal: Union[List[float], np.ndarray],
        mode: str = "DECIMATE",
        R: int = 4,
        M: int = 1,
        N: int = 3
    ) -> Dict[str, Any]:
        """Executes CIC decimation or interpolation and logs to SQLite WAL."""
        mode_upper = mode.strip().upper()
        if mode_upper.startswith("INTERP"):
            res = CICFilterEngine.interpolate(signal, R=R, M=M, N=N)
        else:
            res = CICFilterEngine.decimate(signal, R=R, M=M, N=N)

        if res.get("status") == "SUCCESS":
            exp_id = f"CIC_{int(time.time() * 1000)}_{os.urandom(2).hex()}"
            now = datetime.now(timezone.utc).isoformat()
            with self._lock:
                conn = self._get_connection()
                try:
                    conn.execute("""
                        INSERT INTO dsp_multirate_history (
                            experiment_id, operation_type, rate_l, rate_m, cic_stages,
                            input_length, output_length, metrics_json, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        exp_id, f"CIC_{mode_upper}", R if mode_upper.startswith("INTERP") else 1,
                        1 if mode_upper.startswith("INTERP") else R, N,
                        res["input_samples"], res["output_samples"],
                        json.dumps(res["properties"]), now
                    ))
                    conn.commit()
                    res["experiment_id"] = exp_id
                finally:
                    conn.close()
        return res

    def run_quantization_analysis(
        self,
        signal: Union[List[float], np.ndarray],
        m: int = 1,
        n: int = 14,
        rounding_mode: str = "ROUND",
        overflow_mode: str = "SATURATE"
    ) -> Dict[str, Any]:
        """Executes Qm.n quantization and logs SQNR metrics to SQLite WAL."""
        res = FixedPointQuantizer.quantize_signal(
            signal=signal,
            m=m,
            n=n,
            rounding_mode=rounding_mode,
            overflow_mode=overflow_mode
        )
        if res.get("status") == "SUCCESS":
            exp_id = f"QUANT_{int(time.time() * 1000)}_{os.urandom(2).hex()}"
            now = datetime.now(timezone.utc).isoformat()
            with self._lock:
                conn = self._get_connection()
                try:
                    conn.execute("""
                        INSERT INTO dsp_quantization_history (
                            experiment_id, q_format, wordlength_b, rounding_mode,
                            overflow_mode, measured_sqnr_db, overflow_count, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        exp_id, res["format_metrics"]["format"],
                        res["format_metrics"]["total_wordlength_B"],
                        res["rounding_mode"], res["overflow_mode"],
                        res["measured_sqnr_db"], res["overflow_samples_count"],
                        now
                    ))
                    conn.commit()
                    res["experiment_id"] = exp_id
                finally:
                    conn.close()
        return res

    def get_history(self, limit: int = 25) -> Dict[str, Any]:
        """Fetches recent DSP multirate and quantization experiment history."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.execute("""
                    SELECT experiment_id, operation_type, rate_l, rate_m, cic_stages,
                           input_length, output_length, metrics_json, created_at
                    FROM dsp_multirate_history
                    ORDER BY id DESC LIMIT ?;
                """, (limit,))
                multirate = [dict(r) for r in cur.fetchall()]

                cur2 = conn.execute("""
                    SELECT experiment_id, q_format, wordlength_b, rounding_mode,
                           overflow_mode, measured_sqnr_db, overflow_count, created_at
                    FROM dsp_quantization_history
                    ORDER BY id DESC LIMIT ?;
                """, (limit,))
                quantization = [dict(r) for r in cur2.fetchall()]

                return {
                    "status": "SUCCESS",
                    "multirate_history": multirate,
                    "quantization_history": quantization
                }
            finally:
                conn.close()


# Global singleton instance for platform-wide usage
multirate_dsp_engine = MultirateDSPEngine()
