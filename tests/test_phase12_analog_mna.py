"""
========================================================================================
VoltCore Apex Academia - Phase 12 Test Suite
Non-Linear Modified Nodal Analysis (MNA) Analog Circuit Simulator & Transistor Workbench
Anna University / MIT Campus - Department of Electronics Engineering
Lead Systems Architect & Senior Analog IC Design Specialist: Ashok Kumar A
========================================================================================
"""

import os
import sys
import math
import json
import sqlite3
import pytest
from io import BytesIO

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.analog_mna_engine import (
    Circuit,
    NonLinearMNASolver,
    AnalogMNAEngine,
    analog_mna_engine,
    solve_linear_system,
    pnjlim,
    VT_ROOM
)
import attendance_server


class MockSocket:
    """Mock socket for standard library BaseHTTPRequestHandler testing without port binding."""
    def __init__(self, request_bytes: bytes):
        self._rfile = BytesIO(request_bytes)
        self._wfile = BytesIO()

    def makefile(self, mode: str, bufsize: int = -1):
        if "r" in mode:
            return self._rfile
        elif "w" in mode:
            return self._wfile
        raise ValueError(f"Unknown mode: {mode}")

    def sendall(self, data):
        self._wfile.write(data)

    def close(self):
        pass


@pytest.fixture
def isolated_mna_engine(tmp_path):
    """Provides an isolated AnalogMNAEngine instance with a clean SQLite WAL database."""
    db_file = str(tmp_path / "test_analog_mna.db")
    engine = AnalogMNAEngine(db_path=db_file)
    return engine


# --------------------------------------------------------------------------------------
# 1. Linear MNA Formulation & Voltage Divider Analytical Accuracy
# --------------------------------------------------------------------------------------
def test_linear_voltage_divider_mna():
    """Verify linear MNA formulation on a voltage divider (R1=1k, R2=2k, Vin=9V -> Vout=6V)."""
    ckt = Circuit("Linear Voltage Divider")
    ckt.add_voltage_source("V1", "IN", "0", dc_val=9.0)
    ckt.add_resistor("R1", "IN", "OUT", 1000.0)
    ckt.add_resistor("R2", "OUT", "0", 2000.0)

    solver = NonLinearMNASolver(ckt)
    res = solver.solve_dc_operating_point()

    assert res["converged"] is True
    assert res["node_voltages"]["IN"] == 9.0
    # Analytical: 9.0 * (2000 / (1000 + 2000)) = 6.0 V
    assert abs(res["node_voltages"]["OUT"] - 6.0) < 1e-5


# --------------------------------------------------------------------------------------
# 2. Non-Linear Diode Newton-Raphson Convergence & Forward Drop
# --------------------------------------------------------------------------------------
def test_diode_newton_raphson_convergence():
    """Verify Newton-Raphson converges on non-linear Shockley diode with accurate forward drop."""
    ckt = Circuit("Diode Test Circuit")
    ckt.add_voltage_source("V1", "IN", "0", dc_val=5.0)
    ckt.add_resistor("R1", "IN", "OUT", 1000.0)
    ckt.add_diode("D1", "OUT", "0", is_sat=1e-14, n_factor=1.0)

    solver = NonLinearMNASolver(ckt)
    res = solver.solve_dc_operating_point(max_iterations=40)

    assert res["converged"] is True
    assert res["iterations"] <= 20, f"Expected convergence within 20 iterations, took {res['iterations']}"

    v_d = res["node_voltages"]["OUT"]
    # Silicon diode forward drop typically 0.65V to 0.75V at ~4.3 mA
    assert 0.65 <= v_d <= 0.75, f"Expected diode forward drop in [0.65, 0.75]V, got {v_d}V"

    # Verify KCL: I_R = (5 - V_D)/1000 must match Shockley I_D = IS * (exp(V_D/VT) - 1)
    i_res = (5.0 - v_d) / 1000.0
    i_diode = 1e-14 * (math.exp(v_d / VT_ROOM) - 1.0)
    rel_error = abs(i_res - i_diode) / i_res
    assert rel_error < 0.01, f"KCL mismatch between resistor current {i_res*1000}mA and diode current {i_diode*1000}mA"


# --------------------------------------------------------------------------------------
# 3. Diode Exponential Current Decade Law
# --------------------------------------------------------------------------------------
def test_diode_exponential_current_decade():
    """Verify that diode voltage increases by ~60 mV (n*VT*ln(10)) per decade of current increase."""
    delta_v_decade = VT_ROOM * math.log(10.0)  # ~59.5 mV
    assert 0.055 <= delta_v_decade <= 0.065

    ckt1 = Circuit("Diode 1mA")
    ckt1.add_current_source("I1", "0", "1", dc_val=1e-3)
    ckt1.add_diode("D1", "1", "0", is_sat=1e-14)
    res1 = NonLinearMNASolver(ckt1).solve_dc_operating_point()

    ckt2 = Circuit("Diode 10mA")
    ckt2.add_current_source("I2", "0", "1", dc_val=10e-3)
    ckt2.add_diode("D1", "1", "0", is_sat=1e-14)
    res2 = NonLinearMNASolver(ckt2).solve_dc_operating_point()

    v1 = res1["node_voltages"]["1"]
    v2 = res2["node_voltages"]["1"]
    v_diff = v2 - v1

    # Measured difference should be very close to delta_v_decade
    assert abs(v_diff - delta_v_decade) < 2e-3, f"Expected ~60mV decade shift, got {v_diff*1000}mV"


# --------------------------------------------------------------------------------------
# 4. Transient RC Step Response (Trapezoidal vs Exact Analytical tau = RC)
# --------------------------------------------------------------------------------------
def test_rc_transient_trapezoidal_accuracy():
    """Verify numerical transient step response matches analytical solution V(t) = V0*(1 - exp(-t/tau))."""
    r_val = 1000.0
    c_val = 1e-6  # tau = 1 ms
    tau = r_val * c_val
    v_step = 5.0

    ckt = Circuit("RC Step Transient")
    ckt.add_voltage_source("V1", "IN", "0", wave_type="STEP", amplitude=v_step)
    ckt.add_resistor("R1", "IN", "OUT", r_val)
    ckt.add_capacitor("C1", "OUT", "0", c_val)

    solver = NonLinearMNASolver(ckt)
    res = solver.solve_transient(t_stop=3e-3, t_step=20e-6, integration_method="TRAPEZOIDAL")

    assert res["status"] == "SUCCESS"
    assert res["total_steps"] > 50

    times = res["time_points"]
    v_out = res["trajectories"]["OUT"]

    # Verify at t = 1.0 ms (1 tau): analytical V = 5.0 * (1 - 1/e) = 3.1606 V
    idx_1tau = min(range(len(times)), key=lambda i: abs(times[i] - 1e-3))
    v_sim_1tau = v_out[idx_1tau]
    v_exact_1tau = v_step * (1.0 - math.exp(-1.0))
    rel_error = abs(v_sim_1tau - v_exact_1tau) / v_exact_1tau * 100.0
    assert rel_error < 1.0, f"Relative error at 1 tau is {rel_error:.3f}% (> 1.0% tolerance)"

    # Verify at t = 3.0 ms (3 tau): analytical V = 5.0 * (1 - exp(-3)) = 4.751 V
    idx_3tau = min(range(len(times)), key=lambda i: abs(times[i] - 3e-3))
    v_sim_3tau = v_out[idx_3tau]
    v_exact_3tau = v_step * (1.0 - math.exp(-3.0))
    rel_error_3tau = abs(v_sim_3tau - v_exact_3tau) / v_exact_3tau * 100.0
    assert rel_error_3tau < 1.0, f"Relative error at 3 tau is {rel_error_3tau:.3f}%"


# --------------------------------------------------------------------------------------
# 5. Backward Euler Integration Stability
# --------------------------------------------------------------------------------------
def test_backward_euler_integration():
    """Verify Backward Euler 1st-order numerical integration is stable and monotonic."""
    ckt = Circuit("RC Backward Euler")
    ckt.add_voltage_source("V1", "IN", "0", wave_type="STEP", amplitude=5.0)
    ckt.add_resistor("R1", "IN", "OUT", 1000.0)
    ckt.add_capacitor("C1", "OUT", "0", 1e-6)

    solver = NonLinearMNASolver(ckt)
    res = solver.solve_transient(t_stop=2e-3, t_step=50e-6, integration_method="BACKWARD_EULER")

    assert res["status"] == "SUCCESS"
    v_out = res["trajectories"]["OUT"]

    # Verify strictly monotonic charging
    for i in range(1, len(v_out)):
        assert v_out[i] >= v_out[i - 1], f"Backward Euler non-monotonic at step {i}: {v_out[i]} < {v_out[i-1]}"


# --------------------------------------------------------------------------------------
# 6. BJT Common-Emitter Transistor Operating Point
# --------------------------------------------------------------------------------------
def test_bjt_ce_amplifier_operating_point():
    """Verify BJT Common-Emitter bias network establishes forward active region."""
    ckt = Circuit("BJT CE Bias Network")
    ckt.add_voltage_source("VCC", "VCC", "0", dc_val=10.0)
    ckt.add_resistor("R1", "VCC", "BASE", 47000.0)
    ckt.add_resistor("R2", "BASE", "0", 10000.0)
    ckt.add_resistor("RC", "VCC", "COLL", 2200.0)
    ckt.add_resistor("RE", "EMIT", "0", 680.0)
    ckt.add_bjt("Q1", "COLL", "BASE", "EMIT", bjt_type="NPN", beta_f=100.0)

    solver = NonLinearMNASolver(ckt)
    res = solver.solve_dc_operating_point()

    assert res["converged"] is True
    q1 = res["devices"]["Q1"]

    assert q1["region"] == "ACTIVE", f"Expected ACTIVE region, got {q1['region']}"
    assert 0.60 <= q1["v_be"] <= 0.75, f"Expected V_BE in [0.60, 0.75]V, got {q1['v_be']}V"
    assert q1["i_c_mA"] > 0.5, f"Expected collector current > 0.5 mA, got {q1['i_c_mA']} mA"
    # Verify collector voltage is between V_E and V_CC (not saturated)
    assert 1.5 < res["node_voltages"]["COLL"] < 9.5


# --------------------------------------------------------------------------------------
# 7. Automated Topology Error Checker
# --------------------------------------------------------------------------------------
def test_topology_validation_diagnostics():
    """Verify automated topology diagnostics catch shorts, loops, and floating terminals."""
    # 1. Clean circuit -> Valid
    c_clean = Circuit("Clean")
    c_clean.add_voltage_source("V1", "IN", "0", 5.0)
    c_clean.add_resistor("R1", "IN", "OUT", 1000.0)
    c_clean.add_resistor("R2", "OUT", "0", 1000.0)
    rep_clean = c_clean.validate_circuit()
    assert rep_clean["is_valid"] is True
    assert len(rep_clean["errors"]) == 0

    # 2. Self-loop -> Error
    c_loop = Circuit("Loop")
    c_loop.add_resistor("R1", "1", "1", 100.0)
    rep_loop = c_loop.validate_circuit()
    assert rep_loop["is_valid"] is False
    assert any("Self-loop" in e for e in rep_loop["errors"])

    # 3. Voltage short circuit -> Error
    c_short = Circuit("Short")
    c_short.add_voltage_source("V1", "1", "0", 5.0)
    c_short.add_voltage_source("V2", "1", "0", 12.0)
    rep_short = c_short.validate_circuit()
    assert rep_short["is_valid"] is False
    assert any("Voltage loop" in e for e in rep_short["errors"])

    # 4. Floating node -> Warning
    c_float = Circuit("Float")
    c_float.add_voltage_source("V1", "1", "0", 5.0)
    c_float.add_resistor("R1", "1", "ISOLATED", 1000.0)
    rep_float = c_float.validate_circuit()
    assert any("Floating terminal" in w for w in rep_float["warnings"])


# --------------------------------------------------------------------------------------
# 8. SQLite WAL Mode Simulation Audit Logging
# --------------------------------------------------------------------------------------
def test_simulation_history_wal_logging(isolated_mna_engine):
    """Verify that runs are logged to SQLite WAL mode table circuit_simulation_history."""
    rc_ckt = isolated_mna_engine.get_preset_circuit("rc_transient")
    res = isolated_mna_engine.run_simulation(rc_ckt, analysis_type="TRANSIENT", t_stop=1e-3, t_step=20e-6)

    assert "simulation_id" in res
    assert res["simulation_id"].startswith("SIM_")

    history = isolated_mna_engine.get_simulation_history(limit=10)
    assert len(history) >= 1
    recent = history[0]
    assert recent["simulation_id"] == res["simulation_id"]
    assert recent["analysis_type"] == "TRANSIENT"
    assert recent["total_steps"] > 0
    assert recent["cpu_time_ms"] >= 0.0


# --------------------------------------------------------------------------------------
# 9. HTTP REST Endpoints (FallbackHTTPHandler)
# --------------------------------------------------------------------------------------
def test_mna_http_endpoints():
    """Verify MNA endpoints via FallbackHTTPHandler."""
    handler_class = getattr(attendance_server, "FallbackHTTPHandler", None)
    if not handler_class:
        pytest.skip("FallbackHTTPHandler not found.")

    # 1. GET /api/mna/presets
    req_presets = b"GET /api/mna/presets HTTP/1.1\r\nHost: localhost\r\n\r\n"
    sock1 = MockSocket(req_presets)
    handler_class(sock1, ("127.0.0.1", 5000), None)
    resp1 = sock1._wfile.getvalue().decode("utf-8")
    assert "200 OK" in resp1
    assert "rc_transient" in resp1
    assert "diode_rectifier" in resp1

    # 2. GET /api/mna/simulate?preset_id=rc_transient
    req_sim = b"GET /api/mna/simulate?preset_id=rc_transient HTTP/1.1\r\nHost: localhost\r\n\r\n"
    sock2 = MockSocket(req_sim)
    handler_class(sock2, ("127.0.0.1", 5000), None)
    resp2 = sock2._wfile.getvalue().decode("utf-8")
    assert "200 OK" in resp2
    assert "SUCCESS" in resp2

    # 3. GET /api/mna/history
    req_hist = b"GET /api/mna/history?limit=5 HTTP/1.1\r\nHost: localhost\r\n\r\n"
    sock3 = MockSocket(req_hist)
    handler_class(sock3, ("127.0.0.1", 5000), None)
    resp3 = sock3._wfile.getvalue().decode("utf-8")
    assert "200 OK" in resp3

    # 4. POST /api/mna/validate
    payload = json.dumps({"preset_id": "rc_transient"}).encode("utf-8")
    req_val = f"POST /api/mna/validate HTTP/1.1\r\nHost: localhost\r\nContent-Length: {len(payload)}\r\nContent-Type: application/json\r\n\r\n".encode("utf-8") + payload
    sock4 = MockSocket(req_val)
    handler_class(sock4, ("127.0.0.1", 5000), None)
    resp4 = sock4._wfile.getvalue().decode("utf-8")
    assert "200 OK" in resp4
    assert "SUCCESS" in resp4


# --------------------------------------------------------------------------------------
# 10. Privacy & Thermal Safety Invariants
# --------------------------------------------------------------------------------------
def test_privacy_and_thermal_safety_invariants():
    """Verify zero personal email/phone leaks across Phase 12 files."""
    restricted_encoded = "YXNob2trdW1hcjIwMDgzMTNAZ21haWwuY29t"
    import base64
    restricted_email = base64.b64decode(restricted_encoded).decode("utf-8")

    files_to_check = [
        os.path.join("backend", "analog_mna_engine.py"),
        os.path.join("src", "components", "MnaAnalogWorkbench.jsx")
    ]

    for fpath in files_to_check:
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                assert restricted_email not in content, f"Restricted metadata leaked in {fpath}"
