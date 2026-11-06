"""
========================================================================================
VoltCore Apex Academia - Phase E: Signals & Communication Systems (Features 251–260)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Features:
  - Feature 251: Waveform Generator (Sine, Cos, Square, Triangle, Sawtooth, Sinc, Step)
  - Feature 252: Signal Operations (Addition, Subtraction, Multiplication, Beat Frequencies)
  - Feature 253: Time Shifting, Scaling & Reversal Visualizer (y(t) = x(at - t0))
  - Feature 254: Continuous vs Discrete Signals & Discrete Periodicity Checker
  - Feature 255: Fourier Transform Pairs & Continuous Magnitude/Phase Spectrum
  - Feature 256: Fourier Series Harmonic Synthesizer & Gibbs Phenomenon
  - Feature 257: Linear & Circular Discrete Convolution Calculator
  - Feature 258: Sampling Theorem & Aliasing Demonstrator (Nyquist Rate & Aliased Frequency)
  - Feature 259: Analog Modulation (AM Modulation Index, Efficiency, FM Carson's Rule)
  - Feature 260: Digital Modulation Comparison (BPSK, QPSK, 16-QAM, Constellations & BER)
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

# Digital Modulation Specifications (Feature 260)
DIGITAL_MODULATION_SCHEMES: Dict[str, Dict[str, Any]] = {
    "BPSK": {
        "name": "Binary Phase Shift Keying",
        "bits_per_symbol": 1,
        "spectral_efficiency_bps_hz": 1.0,
        "constellation": [{"i": -1.0, "q": 0.0, "bits": "0"}, {"i": 1.0, "q": 0.0, "bits": "1"}],
        "complexity": "Low",
        "application": "Deep space communication, GPS L1/L2, Satellite telemetry"
    },
    "QPSK": {
        "name": "Quadrature Phase Shift Keying",
        "bits_per_symbol": 2,
        "spectral_efficiency_bps_hz": 2.0,
        "constellation": [
            {"i": 0.707, "q": 0.707, "bits": "00"},
            {"i": -0.707, "q": 0.707, "bits": "01"},
            {"i": -0.707, "q": -0.707, "bits": "11"},
            {"i": 0.707, "q": -0.707, "bits": "10"}
        ],
        "complexity": "Moderate",
        "application": "DVB-S satellite TV, 4G LTE control channels, ZigBee"
    },
    "16-QAM": {
        "name": "16-Quadrature Amplitude Modulation",
        "bits_per_symbol": 4,
        "spectral_efficiency_bps_hz": 4.0,
        "constellation": [
            {"i": (2 * x - 3) / 3.162, "q": (2 * y - 3) / 3.162, "bits": f"{x:02b}{y:02b}"}
            for x in range(4) for y in range(4)
        ],
        "complexity": "High",
        "application": "Wi-Fi (802.11n/ac), DOCSIS cable modems, 5G NR data"
    },
    "BFSK": {
        "name": "Binary Frequency Shift Keying",
        "bits_per_symbol": 1,
        "spectral_efficiency_bps_hz": 0.5,
        "constellation": [{"i": 1.0, "q": 0.0, "bits": "f1"}, {"i": 0.0, "q": 1.0, "bits": "f2"}],
        "complexity": "Low",
        "application": "Caller ID, Bluetooth Low Energy (BLE), Low-cost telemetry"
    }
}


def _q_function(x: float) -> float:
    """Standard Gaussian Q-function: Q(x) = 0.5 * erfc(x / sqrt(2))."""
    if x < 0:
        return 1.0 - _q_function(-x)
    return 0.5 * math.erfc(x / math.sqrt(2.0))


class SignalsCommunicationEngine:
    """
    Backend service engine for Phase E (Features 251–260):
    - Common waveform generation & power/energy
    - Signal operations (beat frequencies & envelope)
    - Time transformations (shift, scale, invert)
    - Continuous vs discrete periodicity
    - Fourier Transform pairs & magnitude/phase
    - Fourier Series synthesis & Gibbs phenomenon
    - Linear & circular discrete convolution
    - Sampling theorem, Nyquist rate & aliasing
    - Analog AM/FM modulation indices & Carson's rule
    - Digital modulation constellations & BER curves
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
                # Signals simulations ledger
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS signals_simulations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        operation_type TEXT NOT NULL,
                        input_params TEXT NOT NULL,
                        output_metrics TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)

                # Modulation experiments ledger
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS modulation_experiments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        mod_type TEXT NOT NULL,
                        carrier_freq_hz REAL NOT NULL,
                        message_freq_hz REAL NOT NULL,
                        bandwidth_hz REAL NOT NULL,
                        modulation_index REAL NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)

                # Seed initial demo record if empty
                cur = conn.execute("SELECT id FROM modulation_experiments WHERE student_id = ?", ("2023MITEC042",))
                if not cur.fetchone():
                    now = datetime.now(timezone.utc).isoformat()
                    conn.execute("""
                        INSERT INTO modulation_experiments (student_id, mod_type, carrier_freq_hz, message_freq_hz, bandwidth_hz, modulation_index, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, ("2023MITEC042", "AM_STANDARD", 10000.0, 1000.0, 2000.0, 0.8, now))

                    conn.execute("""
                        INSERT INTO signals_simulations (student_id, operation_type, input_params, output_metrics, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        "2023MITEC042",
                        "LINEAR_CONVOLUTION",
                        json.dumps({"x": [1, 2, 3], "h": [1, 1]}),
                        json.dumps({"y": [1, 3, 5, 3], "length": 4}),
                        now
                    ))

                conn.commit()
            finally:
                conn.close()

    # ------------------------------------------------------------------------------------
    # Feature 251: Waveform Generator
    # ------------------------------------------------------------------------------------
    def generate_waveform(
        self,
        waveform_type: str = "sine",
        amplitude: float = 1.0,
        frequency_hz: float = 5.0,
        phase_deg: float = 0.0,
        duration_sec: float = 1.0,
        sampling_rate_hz: float = 200.0
    ) -> Dict[str, Any]:
        """
        Generate time samples and evaluate energy, power, and RMS for standard waveforms.
        Supported: sine, cosine, square, triangle, sawtooth, sinc, unit_step.
        """
        if frequency_hz <= 0 or duration_sec <= 0 or sampling_rate_hz <= 0:
            raise ValueError("Frequency, duration, and sampling rate must be positive.")

        phase_rad = math.radians(phase_deg)
        total_samples = int(duration_sec * sampling_rate_hz)
        points = []
        energy_sum = 0.0

        for i in range(total_samples):
            t = i / sampling_rate_hz
            arg = 2.0 * math.pi * frequency_hz * t + phase_rad

            if waveform_type == "sine":
                val = amplitude * math.sin(arg)
            elif waveform_type == "cosine":
                val = amplitude * math.cos(arg)
            elif waveform_type == "square":
                val = amplitude if math.sin(arg) >= 0 else -amplitude
            elif waveform_type == "triangle":
                val = (2.0 * amplitude / math.pi) * math.asin(math.sin(arg))
            elif waveform_type == "sawtooth":
                cycle = (frequency_hz * t) % 1.0
                val = amplitude * (2.0 * cycle - 1.0)
            elif waveform_type == "sinc":
                sinc_arg = math.pi * frequency_hz * (t - duration_sec / 2.0)
                val = amplitude if abs(sinc_arg) < 1e-9 else amplitude * (math.sin(sinc_arg) / sinc_arg)
            elif waveform_type == "unit_step":
                val = amplitude if t >= (duration_sec / 4.0) else 0.0
            else:
                raise ValueError(f"Unknown waveform '{waveform_type}'.")

            points.append({"t": round(t, 4), "y": round(val, 4)})
            energy_sum += (val ** 2) / sampling_rate_hz

        average_power = energy_sum / duration_sec
        rms_val = math.sqrt(average_power)

        return {
            "waveform_type": waveform_type,
            "amplitude": amplitude,
            "frequency_hz": frequency_hz,
            "duration_sec": duration_sec,
            "total_samples": total_samples,
            "signal_energy_joules": round(energy_sum, 4),
            "average_power_watts": round(average_power, 4),
            "rms_value": round(rms_val, 4),
            "points": points[:200]  # First 200 points for preview
        }

    # ------------------------------------------------------------------------------------
    # Feature 252: Signal Operations (Addition, Beat Frequency, Multiplication)
    # ------------------------------------------------------------------------------------
    def combine_signals(
        self,
        op: str = "add",
        f1_hz: float = 10.0,
        f2_hz: float = 12.0,
        a1: float = 1.0,
        a2: float = 1.0,
        duration_sec: float = 1.0,
        fs: float = 200.0
    ) -> Dict[str, Any]:
        """Combine two sinusoidal signals and analyze beat frequencies or envelope modulation."""
        total_samples = int(duration_sec * fs)
        beat_freq = abs(f1_hz - f2_hz)
        points = []

        for i in range(total_samples):
            t = i / fs
            s1 = a1 * math.cos(2.0 * math.pi * f1_hz * t)
            s2 = a2 * math.cos(2.0 * math.pi * f2_hz * t)

            if op == "add":
                y = s1 + s2
            elif op == "subtract":
                y = s1 - s2
            elif op == "multiply":
                y = s1 * s2
            else:
                raise ValueError(f"Unknown operation '{op}'. Supported: add, subtract, multiply.")

            points.append({"t": round(t, 4), "s1": round(s1, 3), "s2": round(s2, 3), "y": round(y, 3)})

        return {
            "operation": op,
            "f1_hz": f1_hz,
            "f2_hz": f2_hz,
            "beat_frequency_hz": round(beat_freq, 2),
            "envelope_period_sec": round(1.0 / beat_freq, 3) if beat_freq > 0 else "Infinity",
            "points": points[:200]
        }

    # ------------------------------------------------------------------------------------
    # Feature 253: Time Shifting, Scaling & Reversal
    # ------------------------------------------------------------------------------------
    def transform_signal(
        self,
        a_scale: float = 1.0,
        t0_shift: float = 0.2,
        reverse: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate time transformations: y(t) = x(a * t - t0) or x(-(a * t - t0)).
        Classifies operation: expansion/compression, delay/advance, reflection.
        """
        if abs(a_scale) < 1e-6:
            raise ValueError("Time scaling factor 'a' cannot be zero.")

        # Classifications
        if abs(a_scale) > 1.0:
            scale_desc = f"Time Compression (Compressed by {abs(a_scale)}x)"
        elif abs(a_scale) < 1.0:
            scale_desc = f"Time Expansion (Expanded by {round(1.0/abs(a_scale), 2)}x)"
        else:
            scale_desc = "No Scaling"

        if t0_shift > 0:
            shift_desc = f"Time Delay (Shifted Right by {t0_shift}s)"
        elif t0_shift < 0:
            shift_desc = f"Time Advance (Shifted Left by {abs(t0_shift)}s)"
        else:
            shift_desc = "No Shift"

        reflection = reverse or (a_scale < 0)

        return {
            "scale_factor_a": a_scale,
            "shift_t0": t0_shift,
            "time_reversed": reflection,
            "transformation_formula": f"y(t) = x({' - ' if reflection else ''}{abs(a_scale)}t {' - ' if t0_shift >= 0 else ' + '}{abs(t0_shift)})",
            "scale_effect": scale_desc,
            "shift_effect": shift_desc,
            "reflection_effect": "Time Reflected across t = 0" if reflection else "No Reflection"
        }

    # ------------------------------------------------------------------------------------
    # Feature 254: Continuous vs Discrete Signals & Periodicity Checker
    # ------------------------------------------------------------------------------------
    def check_discrete_periodicity(
        self,
        analog_freq_hz: float = 50.0,
        sampling_rate_fs: float = 200.0
    ) -> Dict[str, Any]:
        """
        Analyze continuous to discrete sampling and check if discrete sequence x[n] is periodic.
        Condition: f / fs must be a rational number (k / N).
        """
        if sampling_rate_fs <= 0:
            raise ValueError("Sampling rate must be positive.")

        omega_rad_per_sample = 2.0 * math.pi * (analog_freq_hz / sampling_rate_fs)
        ratio = analog_freq_hz / sampling_rate_fs

        # Rational approximation
        mult = 1000
        num = int(round(ratio * mult))
        den = mult
        common = math.gcd(num, den)
        k = num // common
        fundamental_period_n = den // common

        is_periodic = (fundamental_period_n <= 500)

        return {
            "analog_freq_hz": analog_freq_hz,
            "sampling_rate_fs": sampling_rate_fs,
            "digital_omega_rad": round(omega_rad_per_sample, 4),
            "ratio_f_over_fs": round(ratio, 4),
            "is_discrete_periodic": is_periodic,
            "fundamental_period_n": fundamental_period_n if is_periodic else "Aperiodic (Irrational)",
            "explanation": (
                f"x[n] repeats every {fundamental_period_n} samples because (f/fs) = {k}/{fundamental_period_n} is rational."
                if is_periodic else "x[n] is aperiodic because f/fs cannot be reduced to a small integer fraction."
            )
        }

    # ------------------------------------------------------------------------------------
    # Feature 255: Fourier Transform Pairs & Spectrum
    # ------------------------------------------------------------------------------------
    def get_fourier_transform_pair(self, signal_name: str = "rect", param: float = 1.0) -> Dict[str, Any]:
        """
        Compute continuous-time Fourier transform (CTFT) analytical pair:
        - rect(t/T) <-> T * sinc(w*T / 2pi)
        - exp(-at)*u(t) <-> 1 / (a + jw)
        - delta(t) <-> 1
        - gaussian <-> gaussian
        """
        if signal_name == "rect":
            formula_time = f"rect(t / {param})"
            formula_freq = f"{param} · sinc(ω · {param} / 2π)"
            zero_crossings = [round((2.0 * math.pi * k) / param, 2) for k in [1, 2, 3]]
        elif signal_name == "exponential":
            formula_time = f"e^(-{param}t) · u(t)"
            formula_freq = f"1 / ({param} + jω) = {param}/({param}² + ω²) - j·ω/({param}² + ω²)"
            zero_crossings = []
        elif signal_name == "delta":
            formula_time = "δ(t) (Dirac Delta)"
            formula_freq = "1.0 (Uniform infinite flat spectrum)"
            zero_crossings = []
        elif signal_name == "gaussian":
            formula_time = f"e^(-{param}t²)"
            formula_freq = f"√(π / {param}) · e^(-ω² / 4{param})"
            zero_crossings = []
        else:
            raise ValueError(f"Unknown signal '{signal_name}'. Supported: rect, exponential, delta, gaussian.")

        return {
            "signal_name": signal_name,
            "parameter": param,
            "time_domain_expression": formula_time,
            "fourier_transform_expression": formula_freq,
            "first_zero_crossings_rad_s": zero_crossings
        }

    # ------------------------------------------------------------------------------------
    # Feature 256: Fourier Series Harmonic Synthesizer (Gibbs Phenomenon)
    # ------------------------------------------------------------------------------------
    def synthesize_fourier_series(
        self,
        waveform: str = "square",
        harmonics: int = 5,
        fundamental_freq_hz: float = 2.0
    ) -> Dict[str, Any]:
        """
        Synthesize periodic signals via Fourier Series summation:
        Square: x(t) = (4A/pi) * sum_{n odd}^N (1/n) * sin(n*w0*t)
        Sawtooth: x(t) = (2A/pi) * sum_{n=1}^N ((-1)^(n+1)/n) * sin(n*w0*t)
        """
        if harmonics <= 0 or harmonics > 50:
            raise ValueError("Harmonics must be between 1 and 50.")

        w0 = 2.0 * math.pi * fundamental_freq_hz
        duration = 1.0 / fundamental_freq_hz
        points = []

        harmonic_coeffs = []
        for n in range(1, harmonics + 1):
            if waveform == "square":
                coeff = (4.0 / (math.pi * n)) if (n % 2 == 1) else 0.0
            elif waveform == "sawtooth":
                coeff = (2.0 / (math.pi * n)) * ((-1) ** (n + 1))
            else:
                # Triangle
                coeff = (8.0 / (math.pi ** 2 * (n ** 2))) * ((-1) ** ((n - 1) // 2)) if (n % 2 == 1) else 0.0
            harmonic_coeffs.append({"harmonic": n, "amplitude": round(coeff, 4)})

        # Generate synthesized wave
        for step in range(101):
            t = (step / 100.0) * duration
            val = 0.0
            for h in harmonic_coeffs:
                if abs(h["amplitude"]) > 1e-6:
                    val += h["amplitude"] * math.sin(h["harmonic"] * w0 * t)
            points.append({"t": round(t, 4), "y": round(val, 4)})

        # Gibbs overshoot is ~8.95% for square wave discontinuous jumps
        gibbs_overshoot_pct = 8.95 if waveform == "square" else 0.0

        return {
            "waveform": waveform,
            "harmonics_count": harmonics,
            "fundamental_freq_hz": fundamental_freq_hz,
            "gibbs_overshoot_pct": gibbs_overshoot_pct,
            "harmonic_coefficients": harmonic_coeffs[:10],
            "points": points
        }

    # ------------------------------------------------------------------------------------
    # Feature 257: Linear & Circular Discrete Convolution
    # ------------------------------------------------------------------------------------
    def calculate_convolution(
        self,
        x_seq: List[float],
        h_seq: List[float],
        circular: bool = False,
        n_points: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate linear discrete convolution: y[n] = x[n] * h[n]
        or circular discrete convolution: y[n] = x[n] (N) h[n].
        """
        lx = len(x_seq)
        lh = len(h_seq)
        if lx == 0 or lh == 0:
            raise ValueError("Sequences x and h cannot be empty.")

        if not circular:
            # Linear convolution: output length = lx + lh - 1
            ly = lx + lh - 1
            y = [0.0] * ly
            for i in range(lx):
                for j in range(lh):
                    y[i + j] += x_seq[i] * h_seq[j]
            return {
                "convolution_type": "Linear Convolution",
                "x_len": lx,
                "h_len": lh,
                "output_length": ly,
                "output_sequence": [round(val, 4) for val in y]
            }
        else:
            # Circular convolution of length N
            n = n_points if n_points else max(lx, lh)
            if n < max(lx, lh):
                raise ValueError(f"Circular convolution length N ({n}) must be >= max(len(x), len(h)).")

            y_circ = [0.0] * n
            for i in range(n):
                for k in range(n):
                    x_val = x_seq[k] if k < lx else 0.0
                    h_idx = (i - k) % n
                    h_val = h_seq[h_idx] if h_idx < lh else 0.0
                    y_circ[i] += x_val * h_val

            return {
                "convolution_type": "Circular Convolution",
                "n_point_dft": n,
                "x_len": lx,
                "h_len": lh,
                "output_length": n,
                "output_sequence": [round(val, 4) for val in y_circ],
                "aliasing_present": n < (lx + lh - 1)
            }

    # ------------------------------------------------------------------------------------
    # Feature 258: Sampling Theorem & Aliasing Demonstrator
    # ------------------------------------------------------------------------------------
    def analyze_sampling(
        self,
        signal_freq_hz: float = 100.0,
        sampling_rate_fs: float = 250.0
    ) -> Dict[str, Any]:
        """
        Verify Nyquist-Shannon Sampling Theorem:
        - Nyquist rate: fs >= 2 * f_max
        - Computes aliased frequency: f_alias = |f - k * fs| closest to [0, fs/2]
        """
        if signal_freq_hz <= 0 or sampling_rate_fs <= 0:
            raise ValueError("Signal frequency and sampling rate must be positive.")

        nyquist_rate_hz = 2.0 * signal_freq_hz
        fn = sampling_rate_fs / 2.0  # Nyquist frequency

        # Determine alias frequency
        k = round(signal_freq_hz / sampling_rate_fs)
        alias_hz = abs(signal_freq_hz - k * sampling_rate_fs)

        if sampling_rate_fs > nyquist_rate_hz:
            sampling_state = "Oversampling (Perfect reconstruction possible)"
            has_aliasing = False
        elif abs(sampling_rate_fs - nyquist_rate_hz) < 1e-6:
            sampling_state = "Critical Nyquist Sampling"
            has_aliasing = False
        else:
            sampling_state = "Undersampling (Severe Spectral Aliasing!)"
            has_aliasing = True

        return {
            "signal_freq_hz": signal_freq_hz,
            "sampling_rate_fs": sampling_rate_fs,
            "nyquist_rate_hz": nyquist_rate_hz,
            "nyquist_folding_frequency_hz": fn,
            "has_aliasing": has_aliasing,
            "apparent_alias_frequency_hz": round(alias_hz, 2),
            "sampling_status": sampling_state
        }

    # ------------------------------------------------------------------------------------
    # Feature 259: Analog Modulation (AM & FM)
    # ------------------------------------------------------------------------------------
    def calculate_analog_modulation(
        self,
        mod_type: str = "AM",
        fc_hz: float = 10000.0,
        fm_hz: float = 1000.0,
        ac_v: float = 10.0,
        am_v: float = 8.0,
        kf_hz_v: float = 500.0
    ) -> Dict[str, Any]:
        """
        Calculate AM/FM modulation parameters:
        AM: modulation index m = Am / Ac, efficiency eta = m^2 / (2 + m^2), BW = 2*fm
        FM: freq deviation Delta_f = kf * Am, beta = Delta_f / fm, Carson's BW = 2*(Delta_f + fm)
        """
        if fc_hz <= 0 or fm_hz <= 0 or ac_v <= 0:
            raise ValueError("Frequencies and carrier amplitude must be positive.")

        if mod_type.upper() == "AM":
            m_index = am_v / ac_v
            bw_hz = 2.0 * fm_hz
            efficiency_pct = (m_index ** 2 / (2.0 + m_index ** 2)) * 100.0

            if m_index < 1.0:
                condition = "Under-modulation (Clean envelope detection)"
            elif abs(m_index - 1.0) < 1e-4:
                condition = "Critical Modulation (100% modulation)"
            else:
                condition = "Over-modulation (Envelope distortion / phase reversal)"

            return {
                "modulation_type": "Standard AM (DSB-FC)",
                "carrier_freq_hz": fc_hz,
                "message_freq_hz": fm_hz,
                "modulation_index_m": round(m_index, 3),
                "bandwidth_hz": round(bw_hz, 1),
                "power_efficiency_pct": round(efficiency_pct, 2),
                "operating_condition": condition
            }

        elif mod_type.upper() == "FM":
            delta_f_hz = kf_hz_v * am_v
            beta = delta_f_hz / fm_hz
            # Carson's rule: BW = 2 * (Delta_f + fm)
            bw_carsons_hz = 2.0 * (delta_f_hz + fm_hz)

            classification = "Narrowband FM (NBFM)" if beta <= 0.5 else "Wideband FM (WBFM)"

            return {
                "modulation_type": "Frequency Modulation (FM)",
                "carrier_freq_hz": fc_hz,
                "message_freq_hz": fm_hz,
                "frequency_deviation_hz": round(delta_f_hz, 2),
                "modulation_index_beta": round(beta, 3),
                "carsons_bandwidth_hz": round(bw_carsons_hz, 1),
                "classification": classification
            }
        else:
            raise ValueError(f"Unknown mod_type '{mod_type}'. Supported: AM, FM.")

    # ------------------------------------------------------------------------------------
    # Feature 260: Digital Modulation Comparison & BER Curves
    # ------------------------------------------------------------------------------------
    def compare_digital_modulations(self, snr_db: float = 10.0) -> Dict[str, Any]:
        """
        Evaluate Bit Error Rate (BER) and spectral efficiency across BPSK, QPSK, 16-QAM, and BFSK.
        """
        snr_linear = 10.0 ** (snr_db / 10.0)  # Eb / N0
        results = []

        for key, scheme in DIGITAL_MODULATION_SCHEMES.items():
            if key in ["BPSK", "QPSK"]:
                # Pb = Q(sqrt(2 * Eb/N0))
                ber = _q_function(math.sqrt(2.0 * snr_linear))
            elif key == "BFSK":
                # Pb = Q(sqrt(Eb/N0))
                ber = _q_function(math.sqrt(snr_linear))
            elif key == "16-QAM":
                # Pb ~ 3/8 * Q(sqrt(4/5 * Eb/N0))
                ber = (3.0 / 8.0) * _q_function(math.sqrt(0.8 * snr_linear))
            else:
                ber = 1e-6

            results.append({
                "scheme": key,
                "name": scheme["name"],
                "bits_per_symbol": scheme["bits_per_symbol"],
                "spectral_efficiency": scheme["spectral_efficiency_bps_hz"],
                "bit_error_rate": max(1e-12, min(0.5, ber)),
                "complexity": scheme["complexity"],
                "application": scheme["application"],
                "constellation_points": scheme["constellation"]
            })

        return {
            "snr_db": snr_db,
            "snr_linear": round(snr_linear, 2),
            "schemes": results
        }

    # ------------------------------------------------------------------------------------
    # Persistence Methods (SQLite WAL Mode)
    # ------------------------------------------------------------------------------------
    def save_simulation(
        self,
        student_id: str,
        operation_type: str,
        input_params: Dict[str, Any],
        output_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Record a signals simulation to SQLite WAL ledger."""
        with self._lock:
            conn = self._get_connection()
            try:
                now = datetime.now(timezone.utc).isoformat()
                cur = conn.execute("""
                    INSERT INTO signals_simulations (student_id, operation_type, input_params, output_metrics, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    student_id,
                    operation_type,
                    json.dumps(input_params),
                    json.dumps(output_metrics),
                    now
                ))
                conn.commit()
                return {
                    "status": "success",
                    "simulation_id": cur.lastrowid,
                    "student_id": student_id,
                    "operation_type": operation_type,
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
                    SELECT id, student_id, operation_type, input_params, output_metrics, created_at
                    FROM signals_simulations
                    WHERE student_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                """, (student_id, limit))
                results = []
                for row in cur.fetchall():
                    item = dict(row)
                    try:
                        item["input_params"] = json.loads(item["input_params"])
                        item["output_metrics"] = json.loads(item["output_metrics"])
                    except Exception:
                        pass
                    results.append(item)
                return results
            finally:
                conn.close()
