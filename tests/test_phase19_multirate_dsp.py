"""
========================================================================================
VoltCore Apex Academia - Test Suite for Phase 19
Advanced Multirate DSP Filterbank & Fixed-Point Quantization Laboratory
Lead Digital Signal Processing (DSP) Architect: Ashok Kumar A
========================================================================================
Validates:
  1. DSP Windowing Functions & Spectral Metrics:
     - Rectangular, Hann, Hamming, Blackman, and Kaiser (Bessel I0).
     - Coherent gain, Equivalent Noise Bandwidth (ENBW), and Peak Sidelobe Level (PSLL dB).
  2. FFT Spectrum Analysis:
     - Real-time single-sided magnitude/phase spectrum and dominant harmonic identification.
     - Windowing attenuation of spectral leakage.
  3. Multirate Polyphase Resampling (L/M):
     - Prototype windowed-sinc lowpass FIR filter design.
     - Noble identity polyphase decomposition eliminating zero multiplications.
     - Rational resampling (e.g. L=3, M=2) preserving sinusoid frequency and amplitude.
  4. Cascaded Integrator-Comb (CIC) Filters:
     - Eugene Hogenauer architecture: DC gain G_DC = (R * M)^N and bit growth B_growth = ceil(N * log2(R * M)).
     - Decimation and interpolation step response convergence.
     - Analytical frequency response nulls and sidelobe attenuation (-13.46 * N dB).
  5. Fixed-Point Quantization Laboratory:
     - Qm.n format bounds, resolution Delta = 2^-n, two's complement binary representation.
     - Saturation clipping vs. modular wrap-around overflow handling.
     - Rounding vs. truncation error bias.
     - Empirical SQNR matching theoretical 6.02B + 1.76 dB scaling law.
     - Filter coefficient quantization and complex z-plane pole-zero sensitivity.
  6. In-Memory REST API Endpoints:
     - POST /api/dsp/polyphase_resample
     - POST /api/dsp/cic_filter
     - POST /api/dsp/cic_response
     - POST /api/dsp/spectrum
     - POST /api/dsp/quantize_signal
     - POST /api/dsp/quantize_coefficients
     - GET  /api/dsp/window_analysis
     - GET  /api/dsp/history
  7. High-Precision Performance Budget: Execution time < 350ms (HP Victus passive profile).
========================================================================================
"""

import io
import json
import math
import time
import pytest
import numpy as np

from backend.multirate_dsp_engine import (
    multirate_dsp_engine,
    MultirateDSPEngine,
    PolyphaseFilterbank,
    CICFilterEngine,
    FixedPointQuantizer,
    SpectrumAnalyzer,
    DSPWindowEngine,
    FIRFilterDesigner,
    bessel_i0
)
import attendance_server


class MockHTTPConnection:
    """In-memory mock HTTP transport allowing complete HTTP protocol testing with 0 network sockets."""
    def __init__(self, request_bytes: bytes):
        self.rfile = io.BytesIO(request_bytes)
        self.wfile = io.BytesIO()

    def makefile(self, mode, *args, **kwargs):
        if "r" in mode:
            return self.rfile
        return self.wfile

    def sendall(self, b: bytes):
        self.wfile.write(b)


class DummyServer:
    pass


def execute_mock_http_request(method: str, path: str, payload: dict = None) -> tuple[int, dict]:
    """Dispatches HTTP requests in-memory through attendance_server handlers."""
    if getattr(attendance_server, "HAS_FLASK", False):
        client = attendance_server.app.test_client()
        if method == "POST":
            resp = client.post(path, data=json.dumps(payload or {}), content_type="application/json")
        else:
            resp = client.get(path)
        return resp.status_code, json.loads(resp.data.decode("utf-8"))

    raw_payload = json.dumps(payload or {}).encode("utf-8") if payload else b""
    headers = [
        f"{method} {path} HTTP/1.1",
        "Host: localhost",
        "Content-Type: application/json",
        f"Content-Length: {len(raw_payload)}"
    ]
    raw_req = "\r\n".join(headers).encode("ascii") + b"\r\n\r\n" + raw_payload

    conn = MockHTTPConnection(raw_req)
    attendance_server.FallbackHTTPHandler(conn, ("127.0.0.1", 54321), DummyServer())

    raw_resp = conn.wfile.getvalue().decode("utf-8")
    status_line = raw_resp.split("\r\n")[0]
    status_code = int(status_line.split(" ")[1])
    body_str = raw_resp.split("\r\n\r\n")[-1]
    return status_code, json.loads(body_str)


# ========================================================================================
# 1. TestDSPWindowing
# ========================================================================================

class TestDSPWindowing:
    """Verifies standard DSP windowing function properties and spectral metrics."""

    def test_bessel_i0_series_convergence(self):
        """Validates modified Bessel function I0 against analytical reference values."""
        assert bessel_i0(0.0) == 1.0
        assert pytest.approx(bessel_i0(1.0), abs=1e-5) == 1.266066
        assert pytest.approx(bessel_i0(2.0), abs=1e-5) == 2.279585
        assert pytest.approx(bessel_i0(5.65), abs=1e-3) == 48.904

    @pytest.mark.parametrize("w_name", ["RECTANGULAR", "HANN", "HAMMING", "BLACKMAN", "KAISER"])
    def test_window_symmetry_and_bounds(self, w_name):
        """Verifies symmetric window shape and coefficient bounds in [0, 1]."""
        N = 64
        w = DSPWindowEngine.get_window(w_name, N)
        assert len(w) == N
        assert np.all(w >= 0.0)
        assert np.all(w <= 1.0001)
        # Check even symmetry w[n] == w[N - 1 - n]
        for n in range(N // 2):
            assert pytest.approx(w[n], abs=1e-5) == w[N - 1 - n]

    def test_window_spectral_metrics(self):
        """Verifies coherent gain, ENBW, and PSLL for standard windows."""
        # Rectangular: CG=1.0, ENBW=1.0, PSLL ~ -13.3 dB
        rect = DSPWindowEngine.analyze_window("RECTANGULAR", 64)
        assert rect["coherent_gain"] == 1.0
        assert rect["enbw_bins"] == 1.0
        assert pytest.approx(rect["peak_sidelobe_level_db"], abs=0.5) == -13.26

        # Hann: CG ~ 0.5, ENBW ~ 1.5, PSLL ~ -31.5 dB
        hann = DSPWindowEngine.analyze_window("HANN", 64)
        assert pytest.approx(hann["coherent_gain"], abs=0.02) == 0.5
        assert pytest.approx(hann["enbw_bins"], abs=0.05) == 1.5
        assert hann["peak_sidelobe_level_db"] <= -31.0

        # Hamming: CG ~ 0.54, ENBW ~ 1.36, PSLL ~ -42.7 dB
        hamm = DSPWindowEngine.analyze_window("HAMMING", 64)
        assert pytest.approx(hamm["coherent_gain"], abs=0.02) == 0.54
        assert hamm["peak_sidelobe_level_db"] <= -40.0

        # Blackman: CG ~ 0.42, ENBW ~ 1.73, PSLL ~ -58 dB
        black = DSPWindowEngine.analyze_window("BLACKMAN", 64)
        assert pytest.approx(black["coherent_gain"], abs=0.02) == 0.42
        assert black["peak_sidelobe_level_db"] <= -55.0

    def test_invalid_window_raises(self):
        """Verifies unsupported window names raise ValueError."""
        with pytest.raises(ValueError):
            DSPWindowEngine.get_window("UNKNOWN_WINDOW", 64)


# ========================================================================================
# 2. TestFFTSpectrumAnalyzer
# ========================================================================================

class TestFFTSpectrumAnalyzer:
    """Verifies FFT single-sided spectrum computation and peak frequency detection."""

    def test_pure_sinusoid_dominant_frequency(self):
        """Tests that a 125 Hz sine wave on 1000 Hz sample rate peaks exactly at 125 Hz."""
        fs = 1000.0
        t = np.linspace(0, 0.5, 500, endpoint=False)
        sig = 1.0 * np.sin(2.0 * np.pi * 125.0 * t)

        res = SpectrumAnalyzer.compute_fft_spectrum(sig, fs=fs, window_name="HANN")
        assert res["status"] == "SUCCESS"
        assert res["dominant_frequency_hz"] == 125.0
        # Peak magnitude for 1.0 V sinusoid ~ 1.0 V
        assert pytest.approx(res["dominant_magnitude"], abs=0.05) == 1.0
        # Total power for amplitude 1.0 sine: P = A^2 / 2 = 0.5
        assert pytest.approx(res["total_power"], abs=0.02) == 0.5


# ========================================================================================
# 3. TestPolyphaseFilterbank
# ========================================================================================

class TestPolyphaseFilterbank:
    """Verifies rational resampling (L/M) and polyphase decomposition efficiency."""

    def test_fir_lowpass_prototype_synthesis(self):
        """Verifies windowed-sinc filter cutoff and unity DC gain."""
        h = FIRFilterDesigner.design_lowpass(cutoff_ratio=0.25, num_taps=31, window_name="HAMMING", gain=1.0)
        assert len(h) == 31
        assert pytest.approx(np.sum(h), abs=1e-5) == 1.0
        # Symmetry check
        for i in range(15):
            assert pytest.approx(h[i], abs=1e-5) == h[30 - i]

    def test_polyphase_rational_resampling_ratio(self):
        """Tests resampling from 1000 Hz to 1500 Hz (L=3, M=2): 100 samples -> 150 samples."""
        t = np.linspace(0, 0.1, 100, endpoint=False)
        sig = 1.0 * np.sin(2.0 * np.pi * 50.0 * t)  # 50 Hz tone

        res = PolyphaseFilterbank.resample_rational(sig, L=3, M=2, taps_per_phase=12, window_name="KAISER")
        assert res["status"] == "SUCCESS"
        assert res["interpolation_factor_L"] == 3
        assert res["decimation_factor_M"] == 2
        assert res["rate_change_ratio"] == 1.5
        assert res["input_samples"] == 100
        assert res["output_samples"] == 150
        assert res["polyphase_branches_count"] == 3
        # Speedup factor should be strictly greater than 1.0
        assert res["computational_speedup_factor"] > 1.0

        # Output signal amplitude should preserve original 1.0 V amplitude in passband
        y = np.array(res["output_signal"])
        # Ignore transient edge boundary
        core_y = y[20:-20]
        assert pytest.approx(np.max(core_y), abs=0.05) == 1.0

    def test_polyphase_pure_decimation_and_interpolation(self):
        """Tests pure decimation (L=1, M=4) and pure interpolation (L=4, M=1)."""
        sig = np.ones(80)

        # Decimation by 4: 80 -> 20 samples
        dec = PolyphaseFilterbank.resample_rational(sig, L=1, M=4, taps_per_phase=8)
        assert dec["output_samples"] == 20

        # Interpolation by 4: 80 -> 320 samples
        interp = PolyphaseFilterbank.resample_rational(sig, L=4, M=1, taps_per_phase=8)
        assert interp["output_samples"] == 320


# ========================================================================================
# 4. TestCICFilterEngine
# ========================================================================================

class TestCICFilterEngine:
    """Verifies Eugene Hogenauer Cascaded Integrator-Comb (CIC) filter models."""

    def test_cic_properties_bit_growth_and_dc_gain(self):
        """Tests G_DC = (R * M)^N and bit growth for R=4, M=1, N=3."""
        props = CICFilterEngine.calculate_properties(R=4, M=1, N=3, input_bits=16)
        # DC Gain = (4 * 1)^3 = 64
        assert props["dc_gain_linear"] == 64
        assert pytest.approx(props["dc_gain_db"], abs=0.01) == 36.12
        # Bit growth = ceil(3 * log2(4)) = 3 * 2 = 6 bits
        assert props["bit_growth"] == 6
        assert props["max_register_bits_required"] == 22
        # First sidelobe attenuation: ~ -13.46 * 3 = -40.38 dB
        assert pytest.approx(props["first_sidelobe_attenuation_db"], abs=0.1) == -40.38

    def test_cic_decimator_dc_steady_state(self):
        """Tests that a 3-stage CIC decimator converges to unity normalized gain on DC input."""
        x_dc = np.ones(120)
        res = CICFilterEngine.decimate(x_dc, R=4, M=1, N=3)
        assert res["status"] == "SUCCESS"
        assert res["output_samples"] == 30

        # Steady-state raw output converges to G_DC = 64
        assert res["raw_output"][-1] == 64.0
        # Steady-state normalized output converges to 1.0000
        assert pytest.approx(res["normalized_output"][-1], abs=1e-5) == 1.0

    def test_cic_interpolator_dc_steady_state(self):
        """Tests that a 3-stage CIC interpolator converges to unity normalized gain on DC input."""
        x_dc = np.ones(25)
        res = CICFilterEngine.interpolate(x_dc, R=4, M=1, N=3)
        assert res["status"] == "SUCCESS"
        assert res["output_samples"] == 100
        # Normalized output steady state converges to 1.0
        assert pytest.approx(res["normalized_output"][-1], abs=0.02) == 1.0

    def test_cic_frequency_response_curve(self):
        """Validates that CIC frequency response has zero nulls at 1 / (R * M)."""
        res = CICFilterEngine.compute_frequency_response(R=4, M=1, N=3, num_points=100)
        assert res["status"] == "SUCCESS"
        curve = res["frequency_response"]
        assert len(curve) == 100
        # Null at f = 0.25 cycles/sample -> high attenuation
        null_pt = min(curve, key=lambda pt: abs(pt["norm_freq"] - 0.25))
        assert null_pt["magnitude_db"] < -60.0


# ========================================================================================
# 5. TestFixedPointQuantizer
# ========================================================================================

class TestFixedPointQuantizer:
    """Verifies Qm.n format quantization, saturation, modular wrap-around, and SQNR scaling."""

    def test_q_format_metrics_parsing(self):
        """Tests Q1.14 (1 sign, 1 integer, 14 fractional -> 16 bits)."""
        metrics = FixedPointQuantizer.get_format_metrics(m=1, n=14)
        assert metrics["format"] == "Q1.14"
        assert metrics["total_wordlength_B"] == 16
        assert metrics["scale_factor"] == 16384
        assert pytest.approx(metrics["step_size_lsb"], abs=1e-7) == 6.1035e-5
        assert metrics["min_representable_float"] == -2.0
        assert pytest.approx(metrics["max_representable_float"], abs=1e-4) == 1.999939
        # Theory SQNR for 16 bits: 6.02 * 16 + 1.76 = 98.08 dB
        assert pytest.approx(metrics["theoretical_full_scale_sqnr_db"], abs=0.1) == 98.08

    def test_single_value_quantization_exact_fractions(self):
        """Verifies exact binary representation of fractional values."""
        # 0.75 in Q1.14: 0.75 * 16384 = 12288 -> 0x3000
        q = FixedPointQuantizer.quantize_value(0.75, m=1, n=14)
        assert q["quantized_float"] == 0.75
        assert q["quantized_int"] == 12288
        assert q["hex_code"] == "0x3000"
        assert q["quantization_error"] == 0.0
        assert not q["overflow_detected"]

        # -0.5 in Q1.14: -0.5 * 16384 = -8192
        q_neg = FixedPointQuantizer.quantize_value(-0.5, m=1, n=14)
        assert q_neg["quantized_float"] == -0.5
        assert q_neg["quantized_int"] == -8192
        assert not q_neg["overflow_detected"]

    def test_overflow_saturation_vs_wrap_around(self):
        """Tests that exceeding Q1.14 dynamic range (+2.5 > 2.0 - LSB) saturates or wraps."""
        # 1. Saturation mode: clamped to max positive code 32767 (~ 1.999939)
        sat = FixedPointQuantizer.quantize_value(2.5, m=1, n=14, overflow_mode="SATURATE")
        assert sat["overflow_detected"] is True
        assert sat["quantized_int"] == 32767
        assert pytest.approx(sat["quantized_float"], abs=1e-4) == 1.999939

        # 2. Wrap-around mode: wraps into negative region (-1.5)
        wrap = FixedPointQuantizer.quantize_value(2.5, m=1, n=14, overflow_mode="WRAP")
        assert wrap["overflow_detected"] is True
        assert wrap["quantized_int"] == -24576
        assert wrap["quantized_float"] == -1.5

    def test_sqnr_scaling_law_6db_per_bit(self):
        """
        Verifies fundamental DSP theorem: SQNR = 6.02B + 1.76 dB.
        Tests 16-bit Q1.14 (~98 dB) and 8-bit Q1.6 (~50 dB).
        """
        t = np.linspace(0, 1.0, 5000, endpoint=False)
        # Full-scale sinusoid of amplitude A = 1.999 (fits in [-2.0, 1.9999])
        sig = 1.999 * np.sin(2.0 * np.pi * 5.0 * t)

        # 1. 16-bit wordlength: Q1.14
        q16 = FixedPointQuantizer.quantize_signal(sig, m=1, n=14, rounding_mode="ROUND")
        assert q16["status"] == "SUCCESS"
        assert q16["overflow_samples_count"] == 0
        # Measured SQNR should be within 1 dB of theoretical 98.08 dB
        assert pytest.approx(q16["measured_sqnr_db"], abs=1.0) == 98.08

        # 2. 8-bit wordlength: Q1.6
        # Theoretical SQNR = 6.02 * 8 + 1.76 = 49.92 dB
        q8 = FixedPointQuantizer.quantize_signal(sig, m=1, n=6, rounding_mode="ROUND")
        assert pytest.approx(q8["measured_sqnr_db"], abs=1.5) == 49.92

        # Delta between 16-bit and 8-bit SQNR must be ~ 8 * 6.02 = 48.16 dB
        sqnr_diff = q16["measured_sqnr_db"] - q8["measured_sqnr_db"]
        assert pytest.approx(sqnr_diff, abs=1.5) == 48.16

    def test_filter_coefficient_quantization_pole_zero_shift(self):
        """Verifies coefficient quantization shifts complex poles and zeros."""
        # 2nd-order IIR Butterworth filter coefficients
        b = [0.067455, 0.134911, 0.067455]
        a = [1.0, -1.14298, 0.4128]

        res = FixedPointQuantizer.quantize_filter_coefficients(b_coeffs=b, a_coeffs=a, m=1, n=14)
        assert res["status"] == "SUCCESS"
        assert len(res["original_poles"]) == 2
        assert len(res["quantized_poles"]) == 2
        # Max frequency response deviation in passband should be minor for 16-bit (< 0.2 dB)
        assert res["max_frequency_response_deviation_db"] < 0.20


# ========================================================================================
# 6. TestPhase19RESTEndpoints
# ========================================================================================

class TestPhase19RESTEndpoints:
    """Verifies all Phase 19 HTTP routes with in-memory execution."""

    def test_api_dsp_polyphase_resample(self):
        status, body = execute_mock_http_request("POST", "/api/dsp/polyphase_resample", {
            "signal": [1.0, 0.5, -0.5, -1.0, -0.5, 0.5] * 10,
            "L": 3,
            "M": 2
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert body["data"]["rate_change_ratio"] == 1.5

    def test_api_dsp_cic_filter(self):
        status, body = execute_mock_http_request("POST", "/api/dsp/cic_filter", {
            "signal": [1.0] * 40,
            "mode": "DECIMATE",
            "R": 4,
            "M": 1,
            "N": 3
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert body["data"]["output_samples"] == 10

    def test_api_dsp_cic_response(self):
        status, body = execute_mock_http_request("POST", "/api/dsp/cic_response", {
            "R": 4,
            "M": 1,
            "N": 3,
            "num_points": 50
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert len(body["data"]["frequency_response"]) == 50

    def test_api_dsp_spectrum(self):
        status, body = execute_mock_http_request("POST", "/api/dsp/spectrum", {
            "signal": [math.sin(2 * math.pi * 50 * i / 500) for i in range(200)],
            "fs": 500.0,
            "window_name": "HAMMING"
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert pytest.approx(body["data"]["dominant_frequency_hz"], abs=5.0) == 50.0

    def test_api_dsp_quantize_signal(self):
        status, body = execute_mock_http_request("POST", "/api/dsp/quantize_signal", {
            "signal": [0.1, 0.25, -0.5, 0.75, 1.2],
            "m": 1,
            "n": 14,
            "rounding_mode": "ROUND",
            "overflow_mode": "SATURATE"
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert body["data"]["format_metrics"]["format"] == "Q1.14"

    def test_api_dsp_quantize_coefficients(self):
        status, body = execute_mock_http_request("POST", "/api/dsp/quantize_coefficients", {
            "b_coeffs": [0.2, 0.4, 0.2],
            "a_coeffs": [1.0, -0.5, 0.25],
            "m": 1,
            "n": 14
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert len(body["data"]["quantized_poles"]) == 2

    def test_api_dsp_window_analysis(self):
        status, body = execute_mock_http_request("GET", "/api/dsp/window_analysis?name=HANN&length=64")
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert body["data"]["window_name"] == "HANN"

    def test_api_dsp_history(self):
        status, body = execute_mock_http_request("GET", "/api/dsp/history?limit=10")
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert "multirate_history" in body["data"]
        assert "quantization_history" in body["data"]


# ========================================================================================
# 7. TestThermalPerformanceBudget
# ========================================================================================

class TestThermalPerformanceBudget:
    """Verifies that all Phase 19 DSP solvers fulfill the strict <350ms passive laptop budget."""

    def test_full_phase19_pipeline_execution_time(self):
        t0 = time.perf_counter()

        # 1. Polyphase Resampling (100 samples L=3, M=2)
        sig = np.sin(np.linspace(0, 10, 120))
        res_poly = multirate_dsp_engine.run_polyphase_resampling(sig, L=3, M=2, taps_per_phase=12)
        assert res_poly["status"] == "SUCCESS"

        # 2. CIC Decimation (120 samples)
        res_cic = multirate_dsp_engine.run_cic_filter(sig, mode="DECIMATE", R=4, M=1, N=3)
        assert res_cic["status"] == "SUCCESS"

        # 3. FFT Spectrum Analysis (256 points)
        res_spec = SpectrumAnalyzer.compute_fft_spectrum(sig, fs=1000.0, window_name="KAISER")
        assert res_spec["status"] == "SUCCESS"

        # 4. Qm.n Quantization (500 samples)
        res_quant = multirate_dsp_engine.run_quantization_analysis(sig, m=1, n=14)
        assert res_quant["status"] == "SUCCESS"

        # 5. Window Analysis
        res_win = DSPWindowEngine.analyze_window("BLACKMAN", 64)
        assert res_win["window_name"] == "BLACKMAN"

        dt_ms = (time.perf_counter() - t0) * 1000.0
        print(f"\n[Thermal Profiler] Phase 19 DSP pipeline finished in {dt_ms:.2f} ms")
        assert dt_ms < 350.0, f"Performance budget exceeded: {dt_ms:.2f}ms >= 350ms"
