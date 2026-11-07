"""
========================================================================================
VoltCore Apex Academia - Test Suite for Phase 14
Engineering Mathematics Studio, Complex Plane Pole-Zero Solver & Fourier Synthesizer
Lead Systems Architect & Applied Mathematics Professor: Ashok Kumar A
========================================================================================
Validates:
  1. Pole-Zero analytical H(s) and H(z) evaluation.
  2. 2nd-Order Butterworth filter exact -3.01dB cutoff and -90 deg phase at w = wc.
  3. Continuous-time Hurwitz stability (LHP vs RHP vs imaginary axis).
  4. Discrete-time Schur-Cohn stability (inside vs outside vs on unit circle).
  5. Region of Convergence (ROC) boundary determination.
  6. 4th-Order Runge-Kutta (RK4) state-space step response overshoot and rise time.
  7. Fourier Series harmonic synthesis (Square, Triangle, Sawtooth, Half-Wave) and THD.
  8. SQLite WAL mode persistence into 'math_studio_history' table.
  9. Host thermal and performance budget (<350ms).
 10. End-to-end Flask & Fallback REST API endpoints (/api/math/presets, analyze, fourier, history).
========================================================================================
"""

import os
import io
import json
import math
import cmath
import time
import pytest
import sqlite3

from backend.math_studio_engine import (
    PoleZeroSystem,
    FourierSeriesEngine,
    MathStudioEngine,
    math_studio_engine,
    complex_from_dict,
    complex_to_dict
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
    """Helper to dispatch HTTP requests in-memory through attendance_server handlers."""
    if getattr(attendance_server, "HAS_FLASK", False):
        client = attendance_server.app.test_client()
        if method == "POST":
            resp = client.post(path, data=json.dumps(payload or {}), content_type="application/json")
        else:
            resp = client.get(path)
        return resp.status_code, json.loads(resp.data.decode("utf-8"))

    # In-memory execution using FallbackHTTPHandler
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


class TestMathStudioPoleZeroSolver:
    """Tests the analytical frequency and stability solvers."""

    def test_butterworth_lp2_cutoff_and_phase(self):
        """2nd-order Butterworth low-pass filter with wc = 10 rad/s."""
        wc = 10.0
        # Poles: (wc / sqrt(2)) * (-1 +- j)
        re_val = -wc / math.sqrt(2.0)
        im_val = wc / math.sqrt(2.0)
        p1 = complex(re_val, im_val)
        p2 = complex(re_val, -im_val)
        gain = wc * wc  # H(0) = gain / (p1*p2) = 100 / 100 = 1.0 (0 dB)

        sys = PoleZeroSystem(domain="LAPLACE", poles=[p1, p2], zeros=[], gain=gain)

        # DC response (w = 0)
        h_dc = sys.evaluate_h(complex(0.0, 0.0))
        assert abs(abs(h_dc) - 1.0) < 1e-4

        # Cutoff frequency response (w = wc)
        h_cutoff = sys.evaluate_h(complex(0.0, wc))
        mag_cutoff = abs(h_cutoff)
        db_cutoff = 20.0 * math.log10(mag_cutoff)
        phase_cutoff_deg = math.degrees(cmath.phase(h_cutoff))

        # Expected: -3.01 dB and -90 degrees
        assert abs(db_cutoff - (-3.0103)) < 0.02
        assert abs(phase_cutoff_deg - (-90.0)) < 0.1

    def test_stability_laplace_domain_lhp_rhp_imaginary(self):
        """Validates Hurwitz stability classification in the Laplace s-plane."""
        # 1. Stable LHP system
        sys_stable = PoleZeroSystem(
            domain="LAPLACE",
            poles=[complex(-2.0, 3.0), complex(-2.0, -3.0)],
            zeros=[complex(-1.0, 0.0)],
            gain=1.0
        )
        res_stable = sys_stable.stability_analysis()
        assert res_stable["is_stable"] is True
        assert res_stable["classification"] == "STABLE"
        assert res_stable["is_minimum_phase"] is True
        assert res_stable["roc_boundary"] == -2.0

        # 2. Unstable RHP system
        sys_unstable = PoleZeroSystem(
            domain="LAPLACE",
            poles=[complex(1.5, 2.0), complex(1.5, -2.0)],
            zeros=[],
            gain=1.0
        )
        res_unstable = sys_unstable.stability_analysis()
        assert res_unstable["is_stable"] is False
        assert res_unstable["classification"] == "UNSTABLE"
        assert res_unstable["roc_boundary"] == 1.5

        # 3. Marginally stable system (pure imaginary poles)
        sys_marginal = PoleZeroSystem(
            domain="LAPLACE",
            poles=[complex(0.0, 5.0), complex(0.0, -5.0)],
            zeros=[],
            gain=1.0
        )
        res_marginal = sys_marginal.stability_analysis()
        assert res_marginal["classification"] == "MARGINALLY_STABLE"
        assert res_marginal["is_stable"] is False

        # 4. Non-minimum phase (zero in RHP)
        sys_nmp = PoleZeroSystem(
            domain="LAPLACE",
            poles=[complex(-1.0, 0.0)],
            zeros=[complex(2.0, 0.0)],
            gain=1.0
        )
        res_nmp = sys_nmp.stability_analysis()
        assert res_nmp["is_stable"] is True
        assert res_nmp["is_minimum_phase"] is False

    def test_stability_z_transform_unit_circle(self):
        """Validates Schur-Cohn stability classification in discrete z-plane."""
        # 1. Stable inside unit circle (|z| < 1)
        sys_z_stable = PoleZeroSystem(
            domain="Z_TRANSFORM",
            poles=[complex(0.5, 0.5), complex(0.5, -0.5)],  # |p| = sqrt(0.5) ~= 0.707 < 1
            zeros=[complex(1.0, 0.0)],
            gain=1.0
        )
        res_z = sys_z_stable.stability_analysis()
        assert res_z["is_stable"] is True
        assert res_z["classification"] == "STABLE"
        assert abs(res_z["roc_boundary"] - math.sqrt(0.5)) < 1e-4

        # 2. Unstable outside unit circle (|z| > 1)
        sys_z_unstable = PoleZeroSystem(
            domain="Z_TRANSFORM",
            poles=[complex(0.9, 0.6)],  # |p| = sqrt(0.81 + 0.36) = sqrt(1.17) > 1
            zeros=[],
            gain=1.0
        )
        res_z_un = sys_z_unstable.stability_analysis()
        assert res_z_un["is_stable"] is False
        assert res_z_un["classification"] == "UNSTABLE"

        # 3. Marginally stable on unit circle (|z| = 1)
        sys_z_marg = PoleZeroSystem(
            domain="Z_TRANSFORM",
            poles=[complex(0.0, 1.0), complex(0.0, -1.0)],
            zeros=[],
            gain=1.0
        )
        res_z_marg = sys_z_marg.stability_analysis()
        assert res_z_marg["classification"] == "MARGINALLY_STABLE"

    def test_bode_plot_computation_and_bandwidth(self):
        """Validates logarithmic frequency sweep and 3dB bandwidth detection."""
        sys = PoleZeroSystem(
            domain="LAPLACE",
            poles=[complex(-10.0, 0.0)],
            zeros=[],
            gain=10.0  # H(s) = 10 / (s + 10), H(0) = 1 (0 dB), wc = 10 rad/s
        )
        bode = sys.compute_bode_response(w_min=0.1, w_max=100.0, num_points=100)

        assert len(bode["frequencies"]) == 100
        assert len(bode["magnitude_db"]) == 100
        assert len(bode["phase_deg"]) == 100

        # DC magnitude is ~0 dB
        assert abs(bode["magnitude_db"][0] - 0.0) < 0.2
        # Cutoff frequency should be detected near 10 rad/s
        assert bode["cutoff_3db_w"] is not None
        assert abs(bode["cutoff_3db_w"] - 10.0) < 1.0


class TestMathStudioTransientRK4:
    """Tests the 4th-Order Runge-Kutta state-space transient simulator."""

    def test_rk4_underdamped_second_order_step_response(self):
        """
        Validates step response of standard 2nd-order underdamped system:
        wn = 10 rad/s, zeta = 0.25.
        Analytical Overshoot: %OS = 100 * exp(-pi*zeta / sqrt(1 - zeta^2)) = 44.43%.
        """
        zeta = 0.25
        wn = 10.0
        re_part = -zeta * wn
        im_part = wn * math.sqrt(1.0 - zeta * zeta)

        p1 = complex(re_part, im_part)
        p2 = complex(re_part, -im_part)
        gain = wn * wn

        sys = PoleZeroSystem(domain="LAPLACE", poles=[p1, p2], zeros=[], gain=gain)
        resp = sys.compute_time_response(t_stop=2.0, dt=0.001, response_type="STEP")

        assert resp["response_type"] == "STEP"
        assert len(resp["time"]) > 500
        assert len(resp["y"]) == len(resp["time"])

        # Steady-state final value should be 1.0
        assert abs(resp["metrics"]["final_value"] - 1.0) < 0.02

        # Theoretical peak is ~1.4443. Check that numerical RK4 gives peak within 1.5%
        peak_val = resp["metrics"]["peak_value"]
        assert abs(peak_val - 1.4443) < 0.02
        overshoot_pct = resp["metrics"]["overshoot_pct"]
        assert abs(overshoot_pct - 44.43) < 2.0

        # Rise time (10-90%) should be positive and realistic (~0.12s)
        assert 0.05 < resp["metrics"]["rise_time_sec"] < 0.25

    def test_rk4_impulse_response(self):
        """Validates impulse response simulation decay."""
        sys = PoleZeroSystem(
            domain="LAPLACE",
            poles=[complex(-5.0, 0.0)],
            zeros=[],
            gain=5.0  # H(s) = 5/(s+5), h(t) = 5*exp(-5t)
        )
        resp = sys.compute_time_response(t_stop=1.0, dt=0.002, response_type="IMPULSE")
        assert resp["response_type"] == "IMPULSE"
        # As t -> 1.0, y(t) should decay close to 0
        assert abs(resp["y"][-1]) < 0.05


class TestFourierSeriesEngine:
    """Tests the Fourier series harmonic coefficient calculator and synthesizer."""

    def test_square_wave_fourier_coefficients(self):
        """Square wave: b_n = 4*A / (n * pi) for odd n; even harmonics = 0."""
        amp = 2.0
        coeffs = FourierSeriesEngine.get_fourier_coefficients("SQUARE", amplitude=amp, num_harmonics=7)
        assert coeffs["waveform"] == "SQUARE"
        assert abs(coeffs["dc_a0"]) < 1e-6

        harmonics = coeffs["harmonics"]
        # n = 1: b1 = 4*2 / pi = 8/pi ~= 2.5465
        h1 = harmonics[0]
        assert h1["n"] == 1
        assert abs(h1["an"]) < 1e-6
        assert abs(h1["bn"] - (8.0 / math.pi)) < 1e-4

        # n = 2: even harmonic must be 0
        h2 = harmonics[1]
        assert h2["n"] == 2
        assert abs(h2["cn_mag"]) < 1e-6

        # n = 3: b3 = 8 / (3*pi) ~= 0.8488
        h3 = harmonics[2]
        assert h3["n"] == 3
        assert abs(h3["bn"] - (8.0 / (3.0 * math.pi))) < 1e-4

    def test_triangle_wave_fourier_coefficients(self):
        """Triangle wave: odd harmonics fall off as 1/n^2."""
        amp = 1.0
        coeffs = FourierSeriesEngine.get_fourier_coefficients("TRIANGLE", amplitude=amp, num_harmonics=5)
        harmonics = coeffs["harmonics"]
        # n = 1: b1 = 8 / pi^2 ~= 0.81057
        assert abs(harmonics[0]["bn"] - (8.0 / (math.pi ** 2))) < 1e-4
        # n = 2: 0
        assert abs(harmonics[1]["cn_mag"]) < 1e-6
        # n = 3: b3 = -8 / (9 * pi^2) ~= -0.09006
        assert abs(harmonics[2]["bn"] - (-8.0 / (9.0 * (math.pi ** 2)))) < 1e-4

    def test_half_wave_rectified_fourier_coefficients(self):
        """Half-wave rectified: DC = A/pi, fundamental b1 = A/2, even a_n = -2A / [pi*(n^2 - 1)]."""
        amp = 3.0
        coeffs = FourierSeriesEngine.get_fourier_coefficients("HALF_WAVE_RECTIFIED", amplitude=amp, num_harmonics=4)
        assert abs(coeffs["dc_a0"] - (3.0 / math.pi)) < 1e-4
        harmonics = coeffs["harmonics"]
        # n = 1: b1 = 1.5
        assert abs(harmonics[0]["bn"] - 1.5) < 1e-4
        # n = 2: a2 = -6 / (3*pi) = -2/pi ~= -0.6366
        assert abs(harmonics[1]["an"] - (-2.0 / math.pi)) < 1e-4

    def test_fourier_curve_reconstruction(self):
        """Tests time-domain synthesis demonstrating convergence."""
        res = FourierSeriesEngine.synthesize_reconstructed_curve(
            waveform="SQUARE",
            amplitude=1.0,
            freq_hz=50.0,
            num_harmonics=15,
            num_points=100
        )
        assert "time_ms" in res
        assert "ideal_curve" in res
        assert "reconstructed_curve" in res
        assert len(res["time_ms"]) == 100
        assert len(res["reconstructed_curve"]) == 100
        # Reconstructed curve should oscillate around +-1.0
        max_recon = max(res["reconstructed_curve"])
        # Gibbs phenomenon: overshoot is ~1.178
        assert 1.05 < max_recon < 1.30


class TestMathStudioEngineFacadeAndDatabase:
    """Tests the high-level MathStudioEngine facade and SQLite WAL persistence."""

    def test_preset_retrieval(self):
        presets = math_studio_engine.get_presets()
        assert "butterworth_lp2" in presets
        assert "chebyshev_lp2" in presets
        assert "underdamped_resonator" in presets
        assert "notch_filter" in presets
        assert "digital_resonator_z" in presets

    def test_analyze_pole_zero_system_and_history_logging(self):
        """Runs end-to-end analysis and verifies record in SQLite WAL table."""
        poles = [{"re": -1.0, "im": 2.0}, {"re": -1.0, "im": -2.0}]
        zeros = [{"re": 0.0, "im": 0.0}]
        gain = 5.0

        res = math_studio_engine.analyze_pole_zero_system(
            poles=poles,
            zeros=zeros,
            gain=gain,
            domain="LAPLACE",
            w_min=0.1,
            w_max=50.0,
            t_stop=1.5,
            preset_id="custom_bandpass_test"
        )

        assert res["status"] == "SUCCESS"
        assert res["simulation_id"].startswith("MATH_")
        assert res["stability"]["is_stable"] is True
        assert "bode" in res
        assert "step_response" in res
        assert "impulse_response" in res

        # Verify entry in SQLite database
        history = math_studio_engine.get_studio_history(limit=5)
        assert len(history) > 0
        latest = history[0]
        assert latest["simulation_id"] == res["simulation_id"]
        assert latest["domain"] == "LAPLACE"
        assert latest["is_stable"] is True

    def test_thermal_and_performance_budget(self):
        """Ensures complete analysis takes < 350ms to protect HP Victus thermal profile."""
        t0 = time.perf_counter()
        math_studio_engine.analyze_pole_zero_system(
            poles=[{"re": -3.0, "im": 4.0}, {"re": -3.0, "im": -4.0}],
            zeros=[],
            gain=25.0,
            domain="LAPLACE",
            w_min=0.1,
            w_max=100.0,
            t_stop=2.0
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        assert elapsed_ms < 350.0, f"Math Studio took {elapsed_ms:.2f}ms (> 350ms budget)"


class TestMathStudioRestEndpoints:
    """Validates the REST API endpoints across Flask and FallbackHTTPHandler."""

    def test_api_math_presets(self):
        status, data = execute_mock_http_request("GET", "/api/math/presets")
        assert status == 200
        assert data["status"] == "SUCCESS"
        assert "butterworth_lp2" in data["presets"]

    def test_api_math_analyze_get_preset(self):
        status, data = execute_mock_http_request("GET", "/api/math/analyze?preset_id=butterworth_lp2")
        assert status == 200
        assert data["status"] == "SUCCESS"
        assert data["stability"]["is_stable"] is True
        assert len(data["bode"]["frequencies"]) > 0

    def test_api_math_analyze_post_custom(self):
        payload = {
            "domain": "LAPLACE",
            "poles": [{"re": -2.0, "im": 5.0}, {"re": -2.0, "im": -5.0}],
            "zeros": [],
            "gain": 29.0,
            "w_min": 0.1,
            "w_max": 50.0,
            "t_stop": 1.0
        }
        status, data = execute_mock_http_request("POST", "/api/math/analyze", payload)
        assert status == 200
        assert data["status"] == "SUCCESS"
        assert data["stability"]["is_stable"] is True
        assert "step_response" in data

    def test_api_math_fourier_endpoint(self):
        status, data = execute_mock_http_request("GET", "/api/math/fourier?waveform=SQUARE&amplitude=2.0&frequency_hz=1000&num_harmonics=9")
        assert status == 200
        assert data["status"] == "SUCCESS"
        assert data["data"]["waveform"] == "SQUARE"
        assert len(data["data"]["time_ms"]) > 0

    def test_api_math_history_endpoint(self):
        status, data = execute_mock_http_request("GET", "/api/math/history?limit=10")
        assert status == 200
        assert data["status"] == "SUCCESS"
        assert isinstance(data["history"], list)
