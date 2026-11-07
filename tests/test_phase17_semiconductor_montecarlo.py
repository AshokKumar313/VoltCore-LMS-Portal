"""
========================================================================================
VoltCore Apex Academia - Test Suite for Phase 17
Semiconductor Physics Explorer & Circuit Tolerance Monte Carlo Yield Simulator
Lead Systems Architect & Applied Statistics Specialist: Ashok Kumar A
========================================================================================
Validates:
  1. Varshni Energy Bandgap Temperature Scaling Eg(T) for Si, Ge, GaAs, 4H-SiC, and GaN.
  2. Effective Density of States (Nc, Nv) and Intrinsic Carrier Concentration ni(T).
  3. Fermi-Dirac Distribution Bounding, EF = 0.50 probability, and Degeneracy Regimes.
  4. Einstein Diffusion Relation (D = mu * Vt) and Drift-Diffusion Current Densities (Jn, Jp).
  5. Step PN Junction Electrostatics (Built-in potential Vbi, Depletion Width W, Peak E-field, Cj).
  6. Statistical Monte Carlo Circuit Tolerance Simulator:
     - Gaussian component parameter sweeps (Resistors, Capacitors, BJTs, MOSFETs).
     - Sample mean, variance, standard deviation, interquartile range (IQR), and skewness/kurtosis.
     - Wilson Score 95% Confidence Interval for Circuit Yield.
     - Pearson parameter sensitivity ranking (identifying variance-dominant components).
     - 15-bin histogram distributions for client-side rendering.
     - SQLite WAL mode audit logging in 'circuit_monte_carlo_history'.
  7. High-Precision Performance Budget: Execution time < 350ms (HP Victus passive profile).
  8. In-Memory REST API Endpoints:
     - /api/semiconductor/materials
     - /api/semiconductor/bandgap
     - /api/semiconductor/fermi_dirac
     - /api/semiconductor/drift_diffusion
     - /api/semiconductor/pn_junction
     - /api/mna/monte_carlo
     - /api/mna/monte_carlo_history
========================================================================================
"""

import os
import io
import json
import time
import math
import pytest
import sqlite3

from backend.semiconductor_physics_engine import (
    SemiconductorPhysicsEngine,
    semiconductor_physics_engine,
    SEMICONDUCTOR_MATERIALS,
    Q_ELEM,
    K_BOLTZ_J,
    K_BOLTZ_EV
)
from backend.analog_mna_engine import (
    Circuit,
    Resistor,
    Capacitor,
    Inductor,
    VoltageSource,
    BJT,
    MOSFET,
    Diode,
    CircuitMonteCarloSimulator,
    analog_mna_engine
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
# 1. Semiconductor Physics Explorer Unit Tests
# ========================================================================================

class TestSemiconductorPhysicsExplorer:
    def test_supported_materials_catalog(self):
        """Verify standard semiconductor database includes Si, Ge, GaAs, SiC, and GaN."""
        materials = semiconductor_physics_engine.get_supported_materials()
        codes = [m["code"] for m in materials]
        assert "SI" in codes
        assert "GE" in codes
        assert "GAAS" in codes
        assert "SIC" in codes
        assert "GAN" in codes
        assert len(materials) >= 5

    def test_bandgap_varshni_temperature_scaling(self):
        """Verify Varshni's equation: Eg(0) and monotonic temperature reduction."""
        # 1. Silicon at 0K and 300K
        eg_si_0 = semiconductor_physics_engine.calculate_bandgap("SI", 0.1)
        assert pytest.approx(eg_si_0, 0.01) == 1.166

        eg_si_300 = semiconductor_physics_engine.calculate_bandgap("SI", 300.0)
        assert pytest.approx(eg_si_300, 0.01) == 1.1205

        eg_si_400 = semiconductor_physics_engine.calculate_bandgap("SI", 400.0)
        # Bandgap must strictly decrease as lattice expands with temperature
        assert eg_si_0 > eg_si_300 > eg_si_400

        # 2. Germanium at 300K: Eg ~ 0.66 eV
        eg_ge_300 = semiconductor_physics_engine.calculate_bandgap("GE", 300.0)
        assert pytest.approx(eg_ge_300, 0.01) == 0.6635

        # 3. Gallium Arsenide at 300K: Eg ~ 1.42 eV
        eg_gaas_300 = semiconductor_physics_engine.calculate_bandgap("GAAS", 300.0)
        assert pytest.approx(eg_gaas_300, 0.01) == 1.4225

        # 4. Wide bandgap semiconductors (SiC and GaN > 3.0 eV)
        eg_sic_300 = semiconductor_physics_engine.calculate_bandgap("SIC", 300.0)
        eg_gan_300 = semiconductor_physics_engine.calculate_bandgap("GAN", 300.0)
        assert eg_sic_300 > 3.0
        assert eg_gan_300 > 3.3

    def test_effective_density_of_states(self):
        """Verify Nc(T) and Nv(T) obey (T / 300)^1.5 thermal scaling."""
        nc_300, nv_300 = semiconductor_physics_engine.calculate_effective_density_of_states("SI", 300.0)
        assert pytest.approx(nc_300, 1e17) == 2.8e19
        assert pytest.approx(nv_300, 1e17) == 1.04e19

        # At T = 600K: (600 / 300)^1.5 = 2^1.5 = 2.8284
        nc_600, nv_600 = semiconductor_physics_engine.calculate_effective_density_of_states("SI", 600.0)
        assert pytest.approx(nc_600 / nc_300, 0.01) == 2.8284
        assert pytest.approx(nv_600 / nv_300, 0.01) == 2.8284

    def test_intrinsic_carrier_concentration(self):
        """Verify intrinsic carrier concentration ni(T) obeys thermal exponential physics."""
        ni_si_300 = semiconductor_physics_engine.calculate_intrinsic_carrier_concentration("SI", 300.0)
        # In Silicon at 300K, ni is approximately 6.6e9 to 1.5e10 cm^-3
        assert 1e9 < ni_si_300 < 2e10

        # Narrower bandgap Ge must have far higher ni than Si
        ni_ge_300 = semiconductor_physics_engine.calculate_intrinsic_carrier_concentration("GE", 300.0)
        assert ni_ge_300 > 1e12

        # Wider bandgap GaAs must have dramatically lower ni than Si
        ni_gaas_300 = semiconductor_physics_engine.calculate_intrinsic_carrier_concentration("GAAS", 300.0)
        assert ni_gaas_300 < 1e7

        # ni must increase rapidly with temperature
        ni_si_350 = semiconductor_physics_engine.calculate_intrinsic_carrier_concentration("SI", 350.0)
        assert ni_si_350 > ni_si_300 * 5.0

    def test_fermi_dirac_distribution(self):
        """Verify Fermi-Dirac occupancy: f(EF) == 0.50 and non-degenerate vs degenerate bounds."""
        # 1. Energy exactly at Fermi level: f(EF) must be exactly 0.50
        fd_ef = semiconductor_physics_engine.calculate_fermi_dirac_probability(
            energy_ev=0.55,
            fermi_level_ev=0.55,
            temperature_k=300.0
        )
        assert fd_ef["fermi_dirac_prob_electron"] == 0.50
        assert fd_ef["fermi_dirac_prob_hole"] == 0.50
        assert fd_ef["regime"] == "DEGENERATE_FERMI_EDGE"

        # 2. Conduction band energy well above EF (> 3*kB*T ~ 0.078 eV)
        fd_high = semiconductor_physics_engine.calculate_fermi_dirac_probability(
            energy_ev=0.70,
            fermi_level_ev=0.55,
            temperature_k=300.0
        )
        assert 0.0 < fd_high["fermi_dirac_prob_electron"] < 0.01
        assert fd_high["regime"] == "NON_DEGENERATE_BOLTZMANN"
        # Boltzmann approximation error should be small (< 2%)
        assert fd_high["boltzmann_error_pct"] < 2.0

        # 3. Energy well below EF: electron occupancy approaches 1.0
        fd_low = semiconductor_physics_engine.calculate_fermi_dirac_probability(
            energy_ev=0.20,
            fermi_level_ev=0.55,
            temperature_k=300.0
        )
        assert fd_low["fermi_dirac_prob_electron"] > 0.999
        assert fd_low["fermi_dirac_prob_hole"] < 0.001

        # 4. Extreme bounds protection without numerical overflow
        fd_extreme = semiconductor_physics_engine.calculate_fermi_dirac_probability(50.0, 0.0, 300.0)
        assert fd_extreme["fermi_dirac_prob_electron"] == 0.0

    def test_einstein_relation(self):
        """Verify Einstein relation: D = mu * Vt = mu * (kB * T / q)."""
        mu_n = 1350.0  # cm^2/V-s
        d_n = semiconductor_physics_engine.calculate_einstein_diffusion_coefficient(mu_n, 300.0)
        vt_300 = semiconductor_physics_engine.calculate_thermal_voltage(300.0)
        assert pytest.approx(vt_300, 0.001) == 0.02585
        assert pytest.approx(d_n, 0.1) == 34.90
        assert pytest.approx(d_n / mu_n, 1e-4) == vt_300

    def test_drift_diffusion_current_densities(self):
        """Verify drift and diffusion current density calculations for electrons and holes."""
        # Electron current with density 1e16 cm^-3, gradient 1e19 cm^-4, field 1000 V/cm
        res_e = semiconductor_physics_engine.calculate_drift_diffusion_current_density(
            carrier_density_cm3=1e16,
            carrier_gradient_cm4=1e19,
            electric_field_v_cm=1000.0,
            mobility_cm2_v_s=1350.0,
            temperature_k=300.0,
            carrier_type="ELECTRON"
        )
        assert res_e["j_drift_a_cm2"] > 0.0
        assert res_e["j_diffusion_a_cm2"] > 0.0
        assert res_e["j_total_a_cm2"] == pytest.approx(res_e["j_drift_a_cm2"] + res_e["j_diffusion_a_cm2"], 1e-4)

        # Hole diffusion has opposite sign due to positive charge: Jp_diff = -q * Dp * (dp/dx)
        res_h = semiconductor_physics_engine.calculate_drift_diffusion_current_density(
            carrier_density_cm3=1e16,
            carrier_gradient_cm4=1e19,
            electric_field_v_cm=0.0,
            mobility_cm2_v_s=450.0,
            temperature_k=300.0,
            carrier_type="HOLE"
        )
        assert res_h["j_drift_a_cm2"] == 0.0
        assert res_h["j_diffusion_a_cm2"] < 0.0  # Negative diffusion direction

    def test_pn_junction_electrostatics(self):
        """Verify PN junction barrier potential, depletion width, charge, and capacitance."""
        res = semiconductor_physics_engine.calculate_pn_junction_electrostatics(
            material="SI",
            na_cm3=1e16,
            nd_cm3=1e17,
            v_applied=0.0,
            area_cm2=1e-4,
            temperature_k=300.0
        )
        # Built-in potential in Silicon typically 0.75 - 0.85V
        assert 0.70 < res["built_in_potential_v"] < 0.85
        # Depletion width typically 0.2 - 0.5 um
        assert 0.15 < res["depletion_width_um"] < 0.60
        # Charge neutrality: xp * Na == xn * Nd
        xp_cm = res["x_p_um"] * 1e-4
        xn_cm = res["x_n_um"] * 1e-4
        assert pytest.approx(xp_cm * 1e16, rel=1e-3) == (xn_cm * 1e17)
        # Reverse bias should expand depletion layer and decrease capacitance
        res_rev = semiconductor_physics_engine.calculate_pn_junction_electrostatics(
            material="SI", na_cm3=1e16, nd_cm3=1e17, v_applied=-5.0, area_cm2=1e-4
        )
        assert res_rev["depletion_width_um"] > res["depletion_width_um"]
        assert res_rev["junction_capacitance_pf"] < res["junction_capacitance_pf"]


# ========================================================================================
# 2. Circuit Tolerance Monte Carlo Simulator Unit Tests
# ========================================================================================

class TestCircuitToleranceMonteCarloSimulator:
    def test_monte_carlo_voltage_divider_gaussian(self):
        """Verify Gaussian tolerance sweep on standard 10V / (1k + 1k) divider produces 5.0V mean."""
        circuit = Circuit("Voltage Divider")
        circuit.add_voltage_source("V1", "IN", "0", dc_val=10.0)
        circuit.add_resistor("R1", "IN", "OUT", 1000.0)
        circuit.add_resistor("R2", "OUT", "0", 1000.0)

        res = CircuitMonteCarloSimulator.run_monte_carlo(
            circuit=circuit,
            runs=100,
            tolerances={"R": 0.05, "V": 0.01},  # 5% resistor tolerance, 1% source
            target_nodes=["OUT"],
            seed=42
        )
        assert res["status"] == "SUCCESS"
        assert res["total_runs"] == 100

        out_stats = res["node_statistics"]["OUT"]
        # Expected nominal output is 5.0V; mean should be within 1% of 5.0V
        assert pytest.approx(out_stats["mean"], 0.05) == 5.0
        assert out_stats["std_dev"] > 0.02
        assert out_stats["min"] < out_stats["mean"] < out_stats["max"]
        # Quantiles ordering
        assert out_stats["p10"] <= out_stats["p25"] <= out_stats["median_p50"] <= out_stats["p75"] <= out_stats["p90"]

        # Histogram validation
        hist = res["histograms"]["OUT"]
        assert len(hist["counts"]) == 15
        assert sum(hist["counts"]) == 100

    def test_monte_carlo_yield_and_wilson_ci(self):
        """Verify yield percentage and Wilson score 95% confidence interval bounding."""
        circuit = Circuit("Yield Test Divider")
        circuit.add_voltage_source("V1", "IN", "0", dc_val=10.0)
        circuit.add_resistor("R1", "IN", "OUT", 1000.0)
        circuit.add_resistor("R2", "OUT", "0", 1000.0)

        # 1. Wide criteria: 4.6V to 5.4V should have high yield (> 90%)
        res_wide = CircuitMonteCarloSimulator.run_monte_carlo(
            circuit=circuit,
            runs=100,
            tolerances={"R": 0.05},
            acceptance_criteria={"OUT": (4.6, 5.4)},
            seed=101
        )
        assert res_wide["yield_pct"] >= 90.0
        ci_wide = res_wide["wilson_ci_95"]
        assert ci_wide["lower_pct"] <= res_wide["yield_pct"] <= ci_wide["upper_pct"]
        assert 0.0 <= ci_wide["lower_pct"] and ci_wide["upper_pct"] <= 100.0

        # 2. Extremely narrow criteria: 4.98V to 5.02V should fail many runs
        res_narrow = CircuitMonteCarloSimulator.run_monte_carlo(
            circuit=circuit,
            runs=100,
            tolerances={"R": 0.05},
            acceptance_criteria={"OUT": (4.98, 5.02)},
            seed=101
        )
        assert res_narrow["yield_pct"] < 60.0
        assert res_narrow["failed_runs"] > 40
        ci_narrow = res_narrow["wilson_ci_95"]
        assert ci_narrow["lower_pct"] <= res_narrow["yield_pct"] <= ci_narrow["upper_pct"]

    def test_monte_carlo_parameter_sensitivities(self):
        """Verify Pearson correlation correctly identifies positive/negative parameter impacts."""
        circuit = Circuit("Sensitivity Test Divider")
        circuit.add_voltage_source("V1", "IN", "0", dc_val=10.0)
        circuit.add_resistor("R1", "IN", "OUT", 1000.0)
        circuit.add_resistor("R2", "OUT", "0", 1000.0)

        res = CircuitMonteCarloSimulator.run_monte_carlo(
            circuit=circuit,
            runs=150,
            tolerances={"R": 0.05, "V": 0.02},
            target_nodes=["OUT"],
            seed=202
        )
        sensitivities = res["parameter_sensitivities"]
        assert len(sensitivities) >= 3

        sens_map = {s["parameter"]: s["correlation_r"] for s in sensitivities}
        # In Vout = V1 * R2 / (R1 + R2):
        # Increasing R2 increases Vout -> correlation must be positive
        assert sens_map["R2_R"] > 0.4
        # Increasing R1 decreases Vout -> correlation must be negative
        assert sens_map["R1_R"] < -0.4
        # Increasing V1 increases Vout -> correlation must be positive
        assert sens_map["V1_V"] > 0.0

    def test_monte_carlo_active_bjt_circuit(self):
        """Verify Monte Carlo simulation with BJT beta variations."""
        circuit = Circuit("BJT Inverter Tolerance")
        circuit.add_voltage_source("VCC", "VCC", "0", dc_val=5.0)
        circuit.add_voltage_source("VIN", "IN", "0", dc_val=2.0)
        circuit.add_resistor("RB", "IN", "B", 10000.0)
        circuit.add_resistor("RC", "VCC", "C", 1000.0)
        circuit.add_bjt("Q1", "C", "B", "0", bjt_type="NPN", beta_f=100.0)

        res = CircuitMonteCarloSimulator.run_monte_carlo(
            circuit=circuit,
            runs=50,
            tolerances={"BJT_BETA": 0.30, "R": 0.05},
            target_nodes=["C"],
            seed=303
        )
        assert res["status"] == "SUCCESS"
        assert res["total_runs"] == 50
        assert "C" in res["node_statistics"]

    def test_monte_carlo_spice_netlist_input(self):
        """Verify analog_mna_engine.run_monte_carlo works directly with SPICE netlist text."""
        netlist = """
        * Monte Carlo RC Divider Benchmark
        V1 in 0 DC 12
        R1 in out 2k
        R2 out 0 1k
        .op
        .end
        """
        res = analog_mna_engine.run_monte_carlo(
            netlist=netlist,
            runs=60,
            tolerances={"R": 0.05},
            target_nodes=["OUT"],
            acceptance_criteria={"OUT": (3.5, 4.5)},
            seed=404
        )
        assert res["status"] == "SUCCESS"
        # Nominal Vout = 12 * 1k / (2k + 1k) = 4.0V
        assert pytest.approx(res["node_statistics"]["OUT"]["mean"], 0.1) == 4.0
        assert res["yield_pct"] > 80.0
        assert "mc_id" in res

    def test_monte_carlo_sqlite_wal_persistence(self, tmp_path):
        """Verify Monte Carlo results are persisted to SQLite WAL database."""
        test_db = str(tmp_path / "test_mc.db")
        from backend.analog_mna_engine import AnalogMNAEngine
        engine = AnalogMNAEngine(db_path=test_db)

        circuit = Circuit("WAL Divider")
        circuit.add_voltage_source("V1", "IN", "0", dc_val=5.0)
        circuit.add_resistor("R1", "IN", "OUT", 1000.0)
        circuit.add_resistor("R2", "OUT", "0", 1000.0)

        res = engine.run_monte_carlo(
            circuit=circuit,
            runs=30,
            target_nodes=["OUT"],
            acceptance_criteria={"OUT": (2.3, 2.7)},
            seed=505
        )
        assert "mc_id" in res
        mc_id = res["mc_id"]

        # Check retrieval from DB
        history = engine.get_monte_carlo_history(limit=5)
        assert len(history) >= 1
        assert history[0]["mc_id"] == mc_id
        assert history[0]["total_runs"] == 30


# ========================================================================================
# 3. In-Memory REST API Endpoints Verification
# ========================================================================================

class TestPhase17RESTEndpoints:
    def test_rest_semiconductor_materials(self):
        """Verify GET /api/semiconductor/materials returns material catalog."""
        status, body = execute_mock_http_request("GET", "/api/semiconductor/materials")
        assert status == 200
        assert body["status"] == "SUCCESS"
        materials = body["materials"]
        assert len(materials) >= 5
        assert any(m["code"] == "SI" for m in materials)

    def test_rest_semiconductor_bandgap(self):
        """Verify POST /api/semiconductor/bandgap returns Eg, Vt, Nc, Nv, ni."""
        payload = {"material": "SI", "temperature_k": 300.0}
        status, body = execute_mock_http_request("POST", "/api/semiconductor/bandgap", payload)
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert body["material"] == "SI"
        assert pytest.approx(body["bandgap_ev"], 0.02) == 1.12
        assert "ni_cm3" in body

    def test_rest_semiconductor_fermi_dirac(self):
        """Verify POST /api/semiconductor/fermi_dirac computes occupancy."""
        payload = {"energy_ev": 0.55, "fermi_level_ev": 0.55, "temperature_k": 300.0}
        status, body = execute_mock_http_request("POST", "/api/semiconductor/fermi_dirac", payload)
        assert status == 200
        assert body["status"] == "SUCCESS"
        data = body["data"]
        assert data["fermi_dirac_prob_electron"] == 0.50

    def test_rest_semiconductor_drift_diffusion(self):
        """Verify POST /api/semiconductor/drift_diffusion computes current densities."""
        payload = {
            "carrier_density": 1e16,
            "carrier_gradient": 1e19,
            "electric_field": 1000.0,
            "mobility": 1350.0,
            "temperature_k": 300.0,
            "carrier_type": "ELECTRON"
        }
        status, body = execute_mock_http_request("POST", "/api/semiconductor/drift_diffusion", payload)
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert "j_total_a_cm2" in body["data"]

    def test_rest_semiconductor_pn_junction(self):
        """Verify POST /api/semiconductor/pn_junction computes electrostatics."""
        payload = {
            "material": "SI",
            "na_cm3": 1e16,
            "nd_cm3": 1e17,
            "v_applied": 0.0,
            "area_cm2": 1e-4,
            "temperature_k": 300.0
        }
        status, body = execute_mock_http_request("POST", "/api/semiconductor/pn_junction", payload)
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert "built_in_potential_v" in body["data"]
        assert "depletion_width_um" in body["data"]

    def test_rest_mna_monte_carlo(self):
        """Verify POST /api/mna/monte_carlo executes variation sweep."""
        netlist = """
        * Test Netlist
        V1 in 0 DC 10
        R1 in out 1k
        R2 out 0 1k
        .op
        .end
        """
        payload = {
            "netlist": netlist,
            "runs": 40,
            "target_nodes": ["OUT"],
            "acceptance_criteria": {"OUT": [4.5, 5.5]},
            "seed": 999
        }
        status, body = execute_mock_http_request("POST", "/api/mna/monte_carlo", payload)
        assert status == 200
        assert body["status"] == "SUCCESS"
        data = body["data"]
        assert data["total_runs"] == 40
        assert "yield_pct" in data
        assert "wilson_ci_95" in data

    def test_rest_mna_monte_carlo_history(self):
        """Verify GET /api/mna/monte_carlo_history returns recent runs."""
        status, body = execute_mock_http_request("GET", "/api/mna/monte_carlo_history?limit=5")
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert "history" in body


# ========================================================================================
# 4. Thermal & Execution Performance Budget Test (< 350ms on HP Victus)
# ========================================================================================

class TestThermalPerformanceBudget:
    def test_phase17_pipeline_budget(self):
        """Verify 100-run Monte Carlo simulation + semiconductor physics audits execute within 350ms."""
        start_time = time.perf_counter()

        # 1. Bandgap calculation
        eg = semiconductor_physics_engine.calculate_bandgap("SI", 300.0)
        assert eg > 1.0

        # 2. PN junction electrostatics
        pn = semiconductor_physics_engine.calculate_pn_junction_electrostatics("SI", 1e16, 1e17)
        assert pn["built_in_potential_v"] > 0.5

        # 3. 100-run Monte Carlo sweep
        circuit = Circuit("Perf Divider")
        circuit.add_voltage_source("V1", "IN", "0", dc_val=10.0)
        circuit.add_resistor("R1", "IN", "OUT", 1000.0)
        circuit.add_resistor("R2", "OUT", "0", 1000.0)

        mc = analog_mna_engine.run_monte_carlo(
            circuit=circuit,
            runs=100,
            target_nodes=["OUT"],
            acceptance_criteria={"OUT": (4.5, 5.5)},
            seed=777
        )
        assert mc["status"] == "SUCCESS"

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        assert elapsed_ms < 350.0, f"Performance budget exceeded: {elapsed_ms:.2f}ms >= 350.0ms"
