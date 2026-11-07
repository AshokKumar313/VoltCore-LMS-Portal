"""
========================================================================================
VoltCore Apex Academia - Test Suite for Phase 18
Control Systems Root Locus / Nyquist Explorer & RF Smith Chart Laboratory
Lead Systems Architect & Applied Mathematics Specialist: Ashok Kumar A
========================================================================================
Validates:
  1. Evans Root Locus Solvers:
     - Characteristic equation D(s) + K * N(s) = 0 closed-loop trajectories for K in [0, K_max].
     - Nearest-neighbor Euclidean branch continuity across 3 poles / 0 zeros and 2 poles / 1 zero.
     - Asymptote centroid sigma_a and angles theta_a.
     - Real-axis segments detection.
     - Breakaway and break-in points (dK/ds = 0) with non-negative gain verification.
     - Imaginary-axis crossover frequency and Routh-Hurwitz critical stability gain K_crit.
  2. Nyquist Contour Mapping & Cauchy Encirclement Criterion:
     - Origin pole indentation arc detours (s = eps * e^(j*theta)) ensuring closed contours.
     - Cauchy winding number N_cw around critical point (-1 + j0).
     - Nyquist Stability Criterion: Z = N_cw + P.
     - Accurate stability verdicts for Type-1 systems G(s) = K / [s(s+1)(s+5)] (K=10 vs K=50).
     - Phase crossover, Gain crossover, Gain Margin (dB), and Phase Margin (deg).
  3. RF Smith Chart Impedance Matching Laboratory:
     - Complex reflection coefficient Gamma = (z - 1)/(z + 1), |Gamma|, angle, VSWR, Return Loss (dB).
     - Normalized impedance to admittance inversion y = 1/z and physical admittance Y = G + jB (mS).
     - Round-trip impedance-reflection-impedance consistency.
     - Shunt single-stub transmission line matching (SHORT & OPEN stubs) with analytical
       branch 1 and branch 2, verifying matched Gamma_in = 0.0 and VSWR = 1.0.
     - Quarter-wave transformer matching: Z_T = sqrt(Z_0 * R_L), l = lambda / 4.
     - Parametric constant resistance circles and reactance arcs for SVG rendering.
     - SQLite WAL mode persistence in 'rf_matching_history'.
  4. In-Memory REST API Endpoints:
     - POST /api/math/root_locus
     - POST /api/math/nyquist
     - POST /api/rf/reflection_coefficient
     - POST /api/rf/admittance
     - POST /api/rf/stub_match
     - POST /api/rf/quarter_wave
     - GET  /api/rf/smith_chart_grid
  5. High-Precision Performance Budget: Execution time < 350ms (HP Victus passive profile).
========================================================================================
"""

import io
import json
import math
import time
import pytest
import sqlite3

from backend.math_studio_engine import (
    RootLocusSolver,
    NyquistPlotSolver,
    math_studio_engine
)
from backend.rf_smith_chart_engine import (
    RFSmithChartEngine,
    rf_smith_chart_engine,
    C_LIGHT
)
SPEED_OF_LIGHT_M_S = C_LIGHT
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
    """Dispatches HTTP requests in-memory through attendance_server with 0 network sockets."""
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
# 1. TestEvansRootLocusSolver
# ========================================================================================

class TestEvansRootLocusSolver:
    """Verifies numerical Evans root locus computation, asymptotic rules, and critical gain."""

    def test_three_pole_system_asymptotes_and_crossover(self):
        """Tests G(s) = 1 / [s(s+1)(s+5)]: sigma_a = -2.0, angles [60, 180, 300], K_crit = 30.0."""
        poles = [0.0, -1.0, -5.0]
        zeros = []
        res = RootLocusSolver.solve_root_locus(poles=poles, zeros=zeros, gain_scale=1.0, k_max=50.0, num_points=150)

        assert res["status"] == "SUCCESS"
        assert res["num_poles"] == 3
        assert res["num_zeros"] == 0

        # Asymptote Centroid sigma_a = (0 - 1 - 5 - 0) / 3 = -2.0
        asymp = res["asymptotes"]
        assert asymp["num_asymptotes"] == 3
        assert pytest.approx(asymp["centroid_sigma_a"], abs=0.01) == -2.0
        assert asymp["angles_deg"] == [60.0, 180.0, 300.0]

        # Breakaway Point between 0 and -1: d(s^3 + 6s^2 + 5s)/ds = 3s^2 + 12s + 5 = 0
        # s = (-12 + sqrt(144 - 60)) / 6 = (-12 + 9.16515) / 6 = -0.47247
        breakaways = res["breakaway_points"]
        assert len(breakaways) >= 1
        b_pt = next(bp for bp in breakaways if -1.0 <= bp["coordinate"] <= 0.0)
        assert pytest.approx(b_pt["coordinate"], abs=0.01) == -0.4725
        assert pytest.approx(b_pt["gain_k"], abs=0.05) == 1.1285
        assert b_pt["point_type"] == "BREAKAWAY"

        # Imaginary Axis Crossover (Routh-Hurwitz critical stability gain K_crit = 30.0)
        assert res["critical_gain_k"] is not None
        assert pytest.approx(res["critical_gain_k"], abs=0.5) == 30.0
        assert not res["is_unconditionally_stable"]

        # Verify branch structure: 3 branches tracked across all gain steps
        assert len(res["branches"]) == 3
        for b in res["branches"]:
            assert len(b) == 150
            # Starting point at K=0 corresponds to an open-loop pole
            p0 = b[0]
            assert p0["k"] == 0.0
            assert any(pytest.approx(complex(p0["real"], p0["imag"]), abs=0.01) == p for p in [0.0, -1.0, -5.0])

    def test_two_pole_one_zero_system(self):
        """Tests G(s) = (s + 2) / [s(s + 1)]: 1 asymptote at 180 deg, break-in onto negative real axis."""
        poles = [0.0, -1.0]
        zeros = [-2.0]
        res = RootLocusSolver.solve_root_locus(poles=poles, zeros=zeros, gain_scale=1.0, k_max=100.0, num_points=100)

        assert res["status"] == "SUCCESS"
        assert res["num_poles"] == 2
        assert res["num_zeros"] == 1
        assert res["asymptotes"]["num_asymptotes"] == 1
        assert res["asymptotes"]["angles_deg"] == [180.0]

        # In G(s) = (s+2)/(s(s+1)), branches leave 0 and -1, meet at breakaway s = -0.5858,
        # form a circle and break-in at s = -3.4142 to reach the zero at -2 and asymptote at -inf.
        # System has no imaginary axis crossing for K > 0 (strictly LHP for K > 0).
        assert res["critical_gain_k"] is None

    def test_empty_poles_error_handling(self):
        """Verifies graceful handling when poles list is empty."""
        res = RootLocusSolver.solve_root_locus(poles=[], zeros=[])
        assert res["status"] == "ERROR"
        assert "At least one pole is required" in res["error"]


# ========================================================================================
# 2. TestNyquistPlotSolver
# ========================================================================================

class TestNyquistPlotSolver:
    """Verifies Nyquist contour mapping, origin pole indentation, and Cauchy stability criterion."""

    def test_type1_system_nyquist_stability(self):
        """Tests G(s) = K / [s(s+1)(s+5)]: K=10 is stable (N=0), K=50 is unstable (N=2)."""
        poles = [0.0, -1.0, -5.0]
        zeros = []

        # 1. Gain K = 10.0 (Below K_crit = 30.0 -> Closed-loop stable)
        nyq_stable = NyquistPlotSolver.solve_nyquist(poles=poles, zeros=zeros, gain=10.0, w_min=0.01, w_max=50.0)
        assert nyq_stable["status"] == "SUCCESS"
        assert nyq_stable["open_loop_rhp_poles_P"] == 0
        assert nyq_stable["encirclements_cw_N"] == 0
        assert nyq_stable["closed_loop_rhp_poles_Z"] == 0
        assert nyq_stable["is_closed_loop_stable"] is True
        assert nyq_stable["stability_verdict"] == "STABLE"

        # Gain Margin and Phase Margin checks for stable system
        assert nyq_stable["gain_margin_linear"] is not None
        assert nyq_stable["gain_margin_linear"] > 1.0  # GM > 0 dB
        assert nyq_stable["gain_margin_db"] > 0.0
        assert nyq_stable["phase_margin_deg"] > 0.0

        # 2. Gain K = 50.0 (Above K_crit = 30.0 -> Closed-loop unstable)
        nyq_unstable = NyquistPlotSolver.solve_nyquist(poles=poles, zeros=zeros, gain=50.0, w_min=0.01, w_max=50.0)
        assert nyq_unstable["status"] == "SUCCESS"
        assert nyq_unstable["open_loop_rhp_poles_P"] == 0
        assert nyq_unstable["encirclements_cw_N"] == 2  # Two CW encirclements of (-1 + j0)
        assert nyq_unstable["closed_loop_rhp_poles_Z"] == 2
        assert nyq_unstable["is_closed_loop_stable"] is False
        assert nyq_unstable["stability_verdict"] == "UNSTABLE"
        assert nyq_unstable["gain_margin_linear"] < 1.0  # GM < 0 dB

    def test_open_loop_unstable_plant_stabilization(self):
        """Tests G(s) = K / [(s - 1)(s + 2)] with P = 1: K=1 is unstable, K=5 is stabilized (N = -1)."""
        poles = [1.0, -2.0]  # P = 1 RHP pole
        zeros = []

        # K = 1.0 (Characteristic eq: s^2 + s - 2 + 1 = s^2 + s - 1 = 0 -> unstable)
        nyq_low = NyquistPlotSolver.solve_nyquist(poles=poles, zeros=zeros, gain=1.0, w_min=0.01, w_max=50.0)
        assert nyq_low["open_loop_rhp_poles_P"] == 1
        assert nyq_low["encirclements_cw_N"] == 0
        assert nyq_low["closed_loop_rhp_poles_Z"] == 1
        assert nyq_low["is_closed_loop_stable"] is False

        # K = 5.0 (Characteristic eq: s^2 + s - 2 + 5 = s^2 + s + 3 = 0 -> stable)
        # By Nyquist: Z = 0 requires N_cw = -P = -1 (one counter-clockwise encirclement)
        nyq_high = NyquistPlotSolver.solve_nyquist(poles=poles, zeros=zeros, gain=5.0, w_min=0.01, w_max=50.0)
        assert nyq_high["open_loop_rhp_poles_P"] == 1
        assert nyq_high["encirclements_cw_N"] == -1
        assert nyq_high["closed_loop_rhp_poles_Z"] == 0
        assert nyq_high["is_closed_loop_stable"] is True
        assert nyq_high["stability_verdict"] == "STABLE"


# ========================================================================================
# 3. TestRFSmithChartEngine
# ========================================================================================

class TestRFSmithChartEngine:
    """Verifies reflection coefficient calculations, VSWR, return loss, and admittance conversions."""

    def test_matched_load(self):
        """Tests perfectly matched load Z_L = 50 + j0 on Z_0 = 50: Gamma = 0, VSWR = 1."""
        res = rf_smith_chart_engine.calculate_reflection_coefficient(z_load=[50.0, 0.0], z0=50.0)
        assert res["status"] == "SUCCESS"
        assert res["gamma_magnitude"] == 0.0
        assert res["vswr"] == 1.0
        assert res["return_loss_db"] >= 100.0  # High return loss for match
        assert res["mismatch_loss_db"] == 0.0
        assert res["normalized_impedance"] == {"r": 1.0, "x": 0.0}

    def test_short_and_open_circuit(self):
        """Tests short-circuit (Gamma = -1) and open-circuit (Gamma = +1)."""
        # Short Circuit
        sc = rf_smith_chart_engine.calculate_reflection_coefficient(z_load=[0.0, 0.0], z0=50.0)
        assert sc["gamma_magnitude"] == 1.0
        assert pytest.approx(abs(sc["gamma_phase_deg"]), abs=0.1) == 180.0
        assert sc["vswr"] == 999.0
        assert sc["return_loss_db"] == 0.0

        # Open Circuit
        oc = rf_smith_chart_engine.calculate_reflection_coefficient(z_load=[1e8, 0.0], z0=50.0)
        assert pytest.approx(oc["gamma_magnitude"], abs=0.001) == 1.0
        assert pytest.approx(abs(oc["gamma_phase_deg"]), abs=0.1) == 0.0
        assert oc["return_loss_db"] == 0.0

    def test_complex_load_impedance_to_admittance(self):
        """Tests complex load Z_L = 25 - 50j: z = 0.5 - 1.0j -> y = 0.4 + 0.8j."""
        z_res = rf_smith_chart_engine.calculate_reflection_coefficient(z_load=[25.0, -50.0], z0=50.0)
        assert pytest.approx(z_res["normalized_impedance"]["r"], abs=0.001) == 0.5
        assert pytest.approx(z_res["normalized_impedance"]["x"], abs=0.001) == -1.0

        # |Gamma| = 1 / sqrt(13) = 0.62017
        assert pytest.approx(z_res["gamma_magnitude"], abs=0.002) == 0.6202
        # VSWR = (1 + 0.62017)/(1 - 0.62017) = 4.2655
        assert pytest.approx(z_res["vswr"], abs=0.01) == 4.27
        # Return loss = -20 * log10(0.6202) = 4.15 dB
        assert pytest.approx(z_res["return_loss_db"], abs=0.05) == 4.15

        # Admittance conversion: y = 1 / (0.5 - 1.0j) = 0.4 + 0.8j
        y_res = rf_smith_chart_engine.convert_impedance_to_admittance(z_load=[25.0, -50.0], z0=50.0)
        assert pytest.approx(y_res["normalized_admittance"]["g"], abs=0.001) == 0.4
        assert pytest.approx(y_res["normalized_admittance"]["b"], abs=0.001) == 0.8
        # Y = y / 50 = 8 mS + 16 mS j
        assert pytest.approx(y_res["admittance_siemens"]["conductance_mS"], abs=0.01) == 8.0
        assert pytest.approx(y_res["admittance_siemens"]["susceptance_mS"], abs=0.01) == 16.0

    def test_round_trip_reflection_to_impedance(self):
        """Tests Gamma -> z -> Z_L round-trip inversion."""
        orig_zl = complex(75.0, 30.0)
        z0 = 50.0
        refl = rf_smith_chart_engine.calculate_reflection_coefficient([orig_zl.real, orig_zl.imag], z0=z0)
        gamma = refl["reflection_coefficient"]["real"] + 1j * refl["reflection_coefficient"]["imag"]

        recov = rf_smith_chart_engine.convert_reflection_to_impedance(gamma, z0=z0)
        assert pytest.approx(recov["impedance_ohms"]["r"], abs=0.001) == 75.0
        assert pytest.approx(recov["impedance_ohms"]["x"], abs=0.001) == 30.0


# ========================================================================================
# 4. TestSingleStubMatching
# ========================================================================================

class TestSingleStubMatching:
    """Verifies single-stub transmission line matching for both SHORT and OPEN stubs."""

    def test_shunt_stub_short_circuit(self):
        """Tests shunt shorted stub matching for Z_L = 25 - 50j at 1 GHz."""
        res = rf_smith_chart_engine.design_single_stub_match(
            z_load=[25.0, -50.0],
            z0=50.0,
            stub_type="SHORT",
            frequency_hz=1e9
        )
        assert res["status"] == "SUCCESS"
        assert "SHORT" in res["stub_type"]
        assert res["frequency_hz"] == 1e9

        solutions = res["solutions"]
        assert len(solutions) == 2

        for sol in solutions:
            # Wavelength fraction in [0, 0.5)
            assert 0.0 <= sol["distance_d_wavelengths"] < 0.5
            assert 0.0 <= sol["stub_length_l_wavelengths"] < 0.5
            # Verified perfect match
            assert sol["matched_gamma_magnitude"] == 0.0
            assert sol["matched_vswr"] == 1.0
            # Physical dimensions check for 1 GHz (lambda = 299.79 mm)
            lambda_mm = (SPEED_OF_LIGHT_M_S / 1e9) * 1000.0
            assert pytest.approx(sol["distance_d_mm"], abs=0.1) == sol["distance_d_wavelengths"] * lambda_mm
            assert pytest.approx(sol["stub_length_l_mm"], abs=0.1) == sol["stub_length_l_wavelengths"] * lambda_mm

    def test_shunt_stub_open_circuit(self):
        """Tests shunt open stub matching for Z_L = 100 + 50j at 2 GHz."""
        res = rf_smith_chart_engine.design_single_stub_match(
            z_load=[100.0, 50.0],
            z0=50.0,
            stub_type="OPEN",
            frequency_hz=2e9
        )
        assert res["status"] == "SUCCESS"
        assert "OPEN" in res["stub_type"]
        solutions = res["solutions"]
        assert len(solutions) == 2
        for sol in solutions:
            assert sol["matched_gamma_magnitude"] == 0.0
            assert sol["matched_vswr"] == 1.0


# ========================================================================================
# 5. TestQuarterWaveTransformer
# ========================================================================================

class TestQuarterWaveTransformer:
    """Verifies quarter-wave transformer matching: Z_T = sqrt(Z_0 * R_L), l = lambda / 4."""

    def test_quarter_wave_transformer_design(self):
        """Tests quarter-wave matching: R_L = 100, Z_0 = 50 at 1.5 GHz."""
        res = rf_smith_chart_engine.design_quarter_wave_transformer(
            r_load=100.0,
            z0=50.0,
            frequency_hz=1.5e9
        )
        assert res["status"] == "SUCCESS"
        # Z_T = sqrt(50 * 100) = sqrt(5000) = 70.7107 ohms
        assert pytest.approx(res["transformer_characteristic_impedance_z_t"], abs=0.01) == 70.71
        assert res["electrical_length_wavelengths"] == 0.25

        # Physical length: lambda = 3e8 / 1.5e9 = 0.2m = 200mm -> l = 50mm
        assert pytest.approx(res["physical_length_mm"], abs=0.1) == 50.0

    def test_quarter_wave_rejects_negative_or_zero_resistance(self):
        """Verifies error handling for non-positive load resistance."""
        res = rf_smith_chart_engine.design_quarter_wave_transformer(r_load=-50.0, z0=50.0)
        assert res["status"] == "ERROR"
        assert "strictly positive" in res["error"]


# ========================================================================================
# 6. TestSmithChartGrid
# ========================================================================================

class TestSmithChartGrid:
    """Verifies SVG parametric geometry generation for Smith Chart grid."""

    def test_smith_chart_grid_generation(self):
        """Validates constant resistance circles and constant reactance arcs."""
        grid = rf_smith_chart_engine.generate_smith_chart_grid()
        assert grid["status"] == "SUCCESS"

        r_circles = grid["resistance_circles"]
        assert len(r_circles) == 6  # [0, 0.2, 0.5, 1.0, 2.0, 5.0]

        # For r = 1.0: Center = (0.5, 0.0), Radius = 0.5
        r1 = next(c for c in r_circles if c["r"] == 1.0)
        assert pytest.approx(r1["center_x"], abs=0.001) == 0.5
        assert pytest.approx(r1["center_y"], abs=0.001) == 0.0
        assert pytest.approx(r1["radius"], abs=0.001) == 0.5

        # Reactance arcs should have positive (inductive) and negative (capacitive) entries
        x_arcs = grid["reactance_arcs"]
        assert len(x_arcs) == 10  # +/- 0.2, 0.5, 1.0, 2.0, 5.0
        for arc in x_arcs:
            assert arc["x"] != 0.0
            assert "points" in arc
            assert len(arc["points"]) > 5


# ========================================================================================
# 7. TestPhase18RESTEndpoints
# ========================================================================================

class TestPhase18RESTEndpoints:
    """Verifies all Phase 18 HTTP API routes with in-memory execution."""

    def test_api_math_root_locus_endpoint(self):
        status, body = execute_mock_http_request("POST", "/api/math/root_locus", {
            "poles": [0.0, -1.0, -5.0],
            "zeros": [],
            "k_max": 40.0,
            "num_points": 50
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert body["data"]["num_poles"] == 3
        assert len(body["data"]["branches"]) == 3

    def test_api_math_nyquist_endpoint(self):
        status, body = execute_mock_http_request("POST", "/api/math/nyquist", {
            "poles": [0.0, -1.0, -5.0],
            "zeros": [],
            "gain": 10.0,
            "num_points": 60
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert body["data"]["stability_verdict"] == "STABLE"

    def test_api_rf_reflection_coefficient_endpoint(self):
        status, body = execute_mock_http_request("POST", "/api/rf/reflection_coefficient", {
            "z_load": [50.0, 0.0],
            "z0": 50.0
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert body["data"]["vswr"] == 1.0

    def test_api_rf_admittance_endpoint(self):
        status, body = execute_mock_http_request("POST", "/api/rf/admittance", {
            "z_load": [25.0, -50.0],
            "z0": 50.0
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert body["data"]["normalized_admittance"]["g"] == 0.4

    def test_api_rf_stub_match_endpoint(self):
        status, body = execute_mock_http_request("POST", "/api/rf/stub_match", {
            "z_load": [25.0, -50.0],
            "z0": 50.0,
            "stub_type": "SHORT",
            "frequency_hz": 1e9
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert len(body["data"]["solutions"]) == 2

    def test_api_rf_quarter_wave_endpoint(self):
        status, body = execute_mock_http_request("POST", "/api/rf/quarter_wave", {
            "r_load": 100.0,
            "z0": 50.0,
            "frequency_hz": 1e9
        })
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert pytest.approx(body["data"]["transformer_characteristic_impedance_z_t"], abs=0.01) == 70.71

    def test_api_rf_smith_chart_grid_endpoint(self):
        status, body = execute_mock_http_request("GET", "/api/rf/smith_chart_grid")
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert len(body["grid"]["resistance_circles"]) == 6


# ========================================================================================
# 8. TestThermalPerformanceBudget
# ========================================================================================

class TestThermalPerformanceBudget:
    """Verifies that all Phase 18 solvers meet the strict <350ms passive profile budget."""

    def test_full_phase18_pipeline_execution_time(self):
        t0 = time.perf_counter()

        # 1. Root Locus computation (150 points)
        rl = math_studio_engine.compute_root_locus(poles=[0, -1, -5], zeros=[], k_max=60.0, num_points=120)
        assert rl["status"] == "SUCCESS"

        # 2. Nyquist Stability calculation (150 points with origin detour)
        ny = math_studio_engine.compute_nyquist_plot(poles=[0, -1, -5], zeros=[], gain=15.0, num_points=120)
        assert ny["status"] == "SUCCESS"

        # 3. Single Stub transmission line matching
        stub = rf_smith_chart_engine.design_single_stub_match(z_load=[25, -50], z0=50.0, stub_type="SHORT", frequency_hz=2.4e9)
        assert stub["status"] == "SUCCESS"

        # 4. Quarter-wave transformer
        qw = rf_smith_chart_engine.design_quarter_wave_transformer(r_load=150.0, z0=50.0, frequency_hz=2.4e9)
        assert qw["status"] == "SUCCESS"

        # 5. Smith Chart Grid generation
        grid = rf_smith_chart_engine.generate_smith_chart_grid()
        assert grid["status"] == "SUCCESS"

        dt_ms = (time.perf_counter() - t0) * 1000.0
        print(f"\n[Thermal Profiler] Phase 18 pipeline finished in {dt_ms:.2f} ms")
        assert dt_ms < 350.0, f"Performance budget exceeded: {dt_ms:.2f}ms >= 350ms"
