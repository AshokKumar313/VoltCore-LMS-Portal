"""
========================================================================================
VoltCore Apex Academia - Test Suite for Phase 16
Concept Dependency Intelligence & Dynamic Engineering Assumptions Checker
Lead Systems Architect & Quality Assurance Director: Ashok Kumar A
========================================================================================
Validates:
  1. Fine-grained Concept DAG topology (24 interconnected ECE concepts, acyclicity, prerequisite hierarchy).
  2. Semantic confidence scoring via Exponential Moving Average (EMA) and dynamic misconception tracking.
  3. Backward DAG traversal, weak ancestor pruning (C < 0.70), and topological remedial micro-lesson synthesis.
  4. Transistor & Analog Circuit Operating Region Assumptions:
     - BJT Saturation vs Cutoff vs Active mode vs Breakdown (Vceo > 50V).
     - MOSFET Triode (Ohmic) vs Saturation vs Subthreshold Cutoff.
     - Diode reverse breakdown and extreme node voltage singularities (|V| > 1000V).
  5. Mathematical Rational Transfer Assumptions:
     - Hurwitz LHP stability (flags steady-state Final Value Theorem on unstable systems).
     - Pole-zero cancellation singularities (|p - z| < 1e-4).
     - Pure imaginary axis division-by-zero infinite resonance (s = +- j*w0).
     - Non-minimum phase excess phase lag (Re(z) > 0).
     - Discrete Z-domain Schur-Cohn unit circle stability (|z| >= 1.0).
     - Frequency sweep bounds validation (w_min > 0, w_max > w_min).
  6. High-Precision Performance Budget: Execution time < 350ms (HP Victus passive profile).
  7. In-Memory REST API Endpoints:
     - /api/intelligence/concept_map
     - /api/intelligence/student_confidence
     - /api/intelligence/remedial_path
     - /api/intelligence/check_assumptions
========================================================================================
"""

import os
import io
import json
import time
import pytest
import sqlite3

from backend.course_config_engine import (
    ConceptDependencyIntelligenceEngine,
    concept_intelligence_engine
)
from backend.analog_mna_engine import (
    Circuit,
    Resistor,
    BJT,
    MOSFET,
    Diode,
    VoltageSource,
    CircuitAssumptionsChecker,
    analog_mna_engine
)
from backend.math_studio_engine import (
    MathematicalAssumptionsChecker,
    math_studio_engine
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
# 1. Concept DAG Topology & Misconception Tracking Tests
# ========================================================================================

class TestConceptDAGAndRemediation:
    def test_concept_graph_dag_integrity(self):
        """Verify DAG acyclicity, valid prerequisite references, and node count."""
        graph = ConceptDependencyIntelligenceEngine.ECE_CONCEPT_GRAPH
        assert len(graph) >= 20, f"Expected >= 20 concepts, got {len(graph)}"

        # Verify all prerequisite IDs exist
        for cid, data in graph.items():
            assert "prerequisites" in data
            assert "key_principles" in data
            assert "interactive_tool" in data
            for p in data["prerequisites"]:
                assert p in graph, f"Concept '{cid}' references non-existent prerequisite '{p}'"

        # Topological sorting cycle detection using Kahn's algorithm
        in_degree = {cid: 0 for cid in graph}
        for cid, data in graph.items():
            for p in data["prerequisites"]:
                in_degree[cid] += 1

        queue = [cid for cid, deg in in_degree.items() if deg == 0]
        visited_count = 0

        while queue:
            curr = queue.pop(0)
            visited_count += 1
            for cid, data in graph.items():
                if curr in data["prerequisites"]:
                    in_degree[cid] -= 1
                    if in_degree[cid] == 0:
                        queue.append(cid)

        assert visited_count == len(graph), "Cycle detected in ECE_CONCEPT_GRAPH! DAG property violated."

    def test_concept_evaluation_and_confidence_scoring(self, tmp_path):
        """Verify EMA confidence score calculation and SQLite WAL persistence."""
        test_db = str(tmp_path / "test_intel.db")
        engine = ConceptDependencyIntelligenceEngine(db_path=test_db)

        # First evaluation: score 60/100 -> confidence 0.60
        res1 = engine.record_concept_evaluation(
            student_id="STU_INTEL_01",
            concept_id="OHMS_LAW",
            score=60.0,
            max_score=100.0
        )
        assert res1["confidence_score"] == 0.60
        assert res1["evaluations_count"] == 1
        assert res1["is_competent"] is False

        # Second evaluation: score 100/100 -> new_conf = 0.65*0.60 + 0.35*1.0 = 0.39 + 0.35 = 0.74
        res2 = engine.record_concept_evaluation(
            student_id="STU_INTEL_01",
            concept_id="OHMS_LAW",
            score=100.0,
            max_score=100.0
        )
        assert pytest.approx(res2["confidence_score"], 0.01) == 0.74
        assert res2["evaluations_count"] == 2
        assert res2["is_competent"] is True

        # Check retrieval
        conf_map = engine.get_student_concept_confidence("STU_INTEL_01")
        assert "OHMS_LAW" in conf_map
        assert conf_map["OHMS_LAW"]["status"] == "COMPETENT"

    def test_misconception_logging(self, tmp_path):
        """Verify dynamic misconception detection logs into SQLite WAL table."""
        test_db = str(tmp_path / "test_misc.db")
        engine = ConceptDependencyIntelligenceEngine(db_path=test_db)

        res = engine.record_concept_evaluation(
            student_id="STU_MISC_99",
            concept_id="BJT_ACTIVE_AMPLIFIER",
            score=30.0,
            detected_misconceptions=["MISCONCEPTION_BJT_SATURATION_CONFUSION", "MISCONCEPTION_ACTIVE_MODE_BIASING"],
            context="LAB_EXPERIMENT_04"
        )
        assert res["confidence_score"] == 0.30

        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        cur.execute("SELECT misconception_id, assessment_context FROM student_misconceptions WHERE student_id = 'STU_MISC_99';")
        rows = cur.fetchall()
        conn.close()

        assert len(rows) == 2
        misc_ids = [r[0] for r in rows]
        assert "MISCONCEPTION_BJT_SATURATION_CONFUSION" in misc_ids
        assert "MISCONCEPTION_ACTIVE_MODE_BIASING" in misc_ids

    def test_remedial_path_weak_ancestor_pruning(self, tmp_path):
        """Verify that strong ancestors (C >= 0.70) are pruned, leaving only weak prerequisites in topological order."""
        test_db = str(tmp_path / "test_remedial.db")
        engine = ConceptDependencyIntelligenceEngine(db_path=test_db)

        # Seed student competencies:
        # OHMS_LAW = Strong (0.95)
        # KIRCHHOFF_LAWS = Strong (0.90)
        # PN_JUNCTION = Weak (0.45)
        # BJT_BIASING = Weak (0.50)
        # RC_RL_TRANSIENT = Strong (0.85)
        # BJT_ACTIVE_AMPLIFIER = Failed (0.35)
        student_id = "STU_REMEDIAL_07"
        engine.record_concept_evaluation(student_id, "OHMS_LAW", 95.0)
        engine.record_concept_evaluation(student_id, "KIRCHHOFF_LAWS", 90.0)
        engine.record_concept_evaluation(student_id, "PN_JUNCTION", 45.0)
        engine.record_concept_evaluation(student_id, "BJT_BIASING", 50.0)
        engine.record_concept_evaluation(student_id, "RC_RL_TRANSIENT", 85.0)
        engine.record_concept_evaluation(student_id, "BJT_ACTIVE_AMPLIFIER", 35.0)

        # Generate remedial path
        path = engine.generate_remedial_path(student_id, "BJT_ACTIVE_AMPLIFIER")
        assert path["status"] == "SUCCESS"
        assert path["student_id"] == student_id
        assert path["failed_concept_id"] == "BJT_ACTIVE_AMPLIFIER"

        weak_prereqs = path["weak_prerequisites"]
        # Strong ancestors (OHMS_LAW, KIRCHHOFF_LAWS, RC_RL_TRANSIENT) should be pruned out
        assert "OHMS_LAW" not in weak_prereqs
        assert "KIRCHHOFF_LAWS" not in weak_prereqs
        assert "RC_RL_TRANSIENT" not in weak_prereqs

        # Weak ancestors should be present
        assert "PN_JUNCTION" in weak_prereqs
        assert "BJT_BIASING" in weak_prereqs
        assert "BJT_ACTIVE_AMPLIFIER" in weak_prereqs

        # Verify topological ordering: PN_JUNCTION before BJT_BIASING before BJT_ACTIVE_AMPLIFIER
        idx_pn = weak_prereqs.index("PN_JUNCTION")
        idx_bias = weak_prereqs.index("BJT_BIASING")
        idx_amp = weak_prereqs.index("BJT_ACTIVE_AMPLIFIER")
        assert idx_pn < idx_bias < idx_amp, "Remedial micro-lessons must be strictly ordered from foundational to downstream"

        # Verify micro-lessons contents
        lessons = path["remedial_micro_lessons"]
        assert len(lessons) == len(weak_prereqs)
        assert all(l["interactive_sandbox"] == "MNA_LAB" for l in lessons)
        assert all("diagnostic_checkpoint" in l for l in lessons)

        # Verify persistence in SQLite WAL
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        cur.execute("SELECT path_id, failed_concept_id FROM remedial_learning_paths WHERE student_id = ?;", (student_id,))
        row = cur.fetchone()
        conn.close()
        assert row is not None
        assert row[1] == "BJT_ACTIVE_AMPLIFIER"


# ========================================================================================
# 2. Transistor & Analog Circuit Assumptions Checker Tests
# ========================================================================================

class TestCircuitAssumptionsChecker:
    def test_bjt_active_mode_valid(self):
        """Verify normal linear active mode passes with 0 critical violations."""
        circuit = Circuit(title="BJT Active Amplifier")
        circuit.add_bjt("Q1", "c", "b", "e", bjt_type="NPN")
        sim_res = {
            "node_voltages": {"c": 5.0, "b": 0.70, "e": 0.0},
            "trajectories": {}
        }
        res = CircuitAssumptionsChecker.check_assumptions(circuit, sim_res, assumed_operating_mode="LINEAR_AMPLIFICATION")
        assert res["assumptions_valid"] is True
        assert len(res["violations"]) == 0
        assert res["device_operating_points"]["Q1"]["region"] == "ACTIVE"

    def test_bjt_saturation_violation(self):
        """Verify BJT saturation (Vce < 0.2V) flags BJT_SATURATION_REGION_VIOLATION."""
        circuit = Circuit(title="BJT Saturated Circuit")
        circuit.add_bjt("Q1", "c", "b", "0", bjt_type="NPN")
        sim_res = {
            "node_voltages": {"c": 0.12, "b": 0.75, "0": 0.0},
            "trajectories": {}
        }
        res = CircuitAssumptionsChecker.check_assumptions(circuit, sim_res, assumed_operating_mode="LINEAR_AMPLIFICATION")
        assert res["assumptions_valid"] is False
        assert any(v["type"] == "BJT_SATURATION_REGION_VIOLATION" for v in res["violations"])
        assert res["device_operating_points"]["Q1"]["region"] == "SATURATION"

    def test_bjt_cutoff_violation(self):
        """Verify BJT cutoff (Vbe < 0.5V) flags BJT_CUTOFF_REGION_VIOLATION."""
        circuit = Circuit(title="BJT Cutoff Circuit")
        circuit.add_bjt("Q1", "c", "b", "0", bjt_type="NPN")
        sim_res = {
            "node_voltages": {"c": 10.0, "b": 0.35, "0": 0.0},
            "trajectories": {}
        }
        res = CircuitAssumptionsChecker.check_assumptions(circuit, sim_res, assumed_operating_mode="LINEAR_AMPLIFICATION")
        assert res["assumptions_valid"] is False
        assert any(v["type"] == "BJT_CUTOFF_REGION_VIOLATION" for v in res["violations"])
        assert res["device_operating_points"]["Q1"]["region"] == "CUTOFF"

    def test_bjt_breakdown_voltage_exceeded(self):
        """Verify excessive Vce > 50V flags BJT_BREAKDOWN_VOLTAGE_EXCEEDED."""
        circuit = Circuit(title="BJT Overvoltage")
        circuit.add_bjt("Q1", "c", "b", "0", bjt_type="NPN")
        sim_res = {
            "node_voltages": {"c": 65.0, "b": 0.70, "0": 0.0},
            "trajectories": {}
        }
        res = CircuitAssumptionsChecker.check_assumptions(circuit, sim_res)
        assert any(v["type"] == "BJT_BREAKDOWN_VOLTAGE_EXCEEDED" for v in res["violations"])

    def test_mosfet_triode_violation(self):
        """Verify MOSFET in Triode region (Vds < Vgs - Vth) flags MOSFET_TRIODE_REGION_VIOLATION."""
        circuit = Circuit(title="MOSFET Triode")
        # Vgs = 3.0V, Vth = 1.0V -> Vov = 2.0V. If Vds = 0.5V < 2.0V -> Triode
        circuit.add_mosfet("M1", "d", "g", "0", mos_type="NMOS", vth=1.0)
        sim_res = {
            "node_voltages": {"d": 0.5, "g": 3.0, "0": 0.0},
            "trajectories": {}
        }
        res = CircuitAssumptionsChecker.check_assumptions(circuit, sim_res, assumed_operating_mode="LINEAR_AMPLIFICATION")
        assert res["assumptions_valid"] is False
        assert any(v["type"] == "MOSFET_TRIODE_REGION_VIOLATION" for v in res["violations"])
        assert res["device_operating_points"]["M1"]["region"] == "TRIODE"

    def test_mosfet_subthreshold_cutoff_violation(self):
        """Verify MOSFET in Cutoff (Vgs <= Vth) flags MOSFET_SUBTHRESHOLD_CUTOFF_VIOLATION."""
        circuit = Circuit(title="MOSFET Cutoff")
        circuit.add_mosfet("M1", "d", "g", "0", mos_type="NMOS", vth=1.2)
        sim_res = {
            "node_voltages": {"d": 5.0, "g": 0.8, "0": 0.0},
            "trajectories": {}
        }
        res = CircuitAssumptionsChecker.check_assumptions(circuit, sim_res, assumed_operating_mode="LINEAR_AMPLIFICATION")
        assert res["assumptions_valid"] is False
        assert any(v["type"] == "MOSFET_SUBTHRESHOLD_CUTOFF_VIOLATION" for v in res["violations"])
        assert res["device_operating_points"]["M1"]["region"] == "CUTOFF"

    def test_diode_reverse_breakdown_exceeded(self):
        """Verify Diode reverse voltage > 50V flags DIODE_REVERSE_BREAKDOWN_EXCEEDED."""
        circuit = Circuit(title="Diode Breakdown")
        circuit.add_diode("D1", "0", "k")
        sim_res = {
            "node_voltages": {"0": 0.0, "k": 75.0},
            "trajectories": {}
        }
        res = CircuitAssumptionsChecker.check_assumptions(circuit, sim_res)
        assert any(v["type"] == "DIODE_REVERSE_BREAKDOWN_EXCEEDED" for v in res["violations"])
        assert res["device_operating_points"]["D1"]["state"] == "BREAKDOWN"

    def test_extreme_node_voltage_divergence(self):
        """Verify unphysical node voltage (> 1000V) flags EXTREME_VOLTAGE_NUMERICAL_DIVERGENCE."""
        circuit = Circuit(title="Floating Node Arc")
        circuit.add_resistor("R1", "1", "0", 1000.0)
        sim_res = {
            "node_voltages": {"1": 1500.0, "0": 0.0},
            "trajectories": {}
        }
        res = CircuitAssumptionsChecker.check_assumptions(circuit, sim_res)
        assert any(v["type"] == "EXTREME_VOLTAGE_NUMERICAL_DIVERGENCE" for v in res["violations"])


# ========================================================================================
# 3. Mathematical Transfer Assumptions Checker Tests
# ========================================================================================

class TestMathematicalAssumptionsChecker:
    def test_stable_system_valid(self):
        """Verify strictly Hurwitz stable system passes with 0 violations."""
        poles = [complex(-2.0, 0), complex(-5.0, 3.0), complex(-5.0, -3.0)]
        zeros = [complex(-1.0, 0)]
        res = MathematicalAssumptionsChecker.check_assumptions("LAPLACE", poles, zeros)
        assert res["assumptions_valid"] is True
        assert res["violations_count"] == 0

    def test_unstable_pole_steady_state_violation(self):
        """Verify RHP pole (Re(p) > 0) flags UNSTABLE_POLE_STEADY_STATE_VIOLATION."""
        poles = [complex(1.5, 0), complex(-4.0, 0)]
        zeros = [complex(-2.0, 0)]
        res = MathematicalAssumptionsChecker.check_assumptions("LAPLACE", poles, zeros)
        assert res["assumptions_valid"] is False
        assert any(v["type"] == "UNSTABLE_POLE_STEADY_STATE_VIOLATION" for v in res["violations"])

    def test_pole_zero_cancellation_singularity(self):
        """Verify coincident pole and zero (|p - z| < 1e-4) flags POLE_ZERO_CANCELLATION_SINGULARITY."""
        poles = [complex(-3.0, 0), complex(-10.0, 0)]
        zeros = [complex(-3.00002, 0)]
        res = MathematicalAssumptionsChecker.check_assumptions("LAPLACE", poles, zeros)
        assert any(v["type"] == "POLE_ZERO_CANCELLATION_SINGULARITY" for v in res["violations"])

    def test_imaginary_axis_infinite_resonance(self):
        """Verify pure imaginary undamped pole flags IMAGINARY_AXIS_INFINITE_RESONANCE_VIOLATION."""
        poles = [complex(0.0, 15.0), complex(0.0, -15.0), complex(-5.0, 0)]
        zeros = []
        res = MathematicalAssumptionsChecker.check_assumptions("LAPLACE", poles, zeros, w_min=0.1, w_max=50.0)
        assert any(v["type"] == "IMAGINARY_AXIS_INFINITE_RESONANCE_VIOLATION" for v in res["violations"])

    def test_non_minimum_phase_zero_warning(self):
        """Verify RHP zero (Re(z) > 0) flags NON_MINIMUM_PHASE_DELAY_VIOLATION warning."""
        poles = [complex(-2.0, 0), complex(-5.0, 0)]
        zeros = [complex(3.0, 0)]  # Non-minimum phase zero
        res = MathematicalAssumptionsChecker.check_assumptions("LAPLACE", poles, zeros)
        assert res["assumptions_valid"] is True  # Warning does not invalidate mathematical existence
        assert any(w["type"] == "NON_MINIMUM_PHASE_DELAY_VIOLATION" for w in res["warnings"])

    def test_discrete_z_domain_instability(self):
        """Verify z-plane pole outside unit circle (|z| >= 1.0) flags DISCRETE_UNIT_CIRCLE_INSTABILITY."""
        poles = [complex(1.15, 0), complex(0.5, 0.3)]
        zeros = [complex(0.2, 0)]
        res = MathematicalAssumptionsChecker.check_assumptions("Z_TRANSFORM", poles, zeros)
        assert res["assumptions_valid"] is False
        assert any(v["type"] == "DISCRETE_UNIT_CIRCLE_INSTABILITY" for v in res["violations"])

    def test_invalid_logarithmic_frequency_range(self):
        """Verify non-positive frequency bounds flag INVALID_LOGARITHMIC_FREQUENCY_RANGE."""
        poles = [complex(-2.0, 0)]
        zeros = []
        res = MathematicalAssumptionsChecker.check_assumptions("LAPLACE", poles, zeros, w_min=-1.0, w_max=10.0)
        assert any(v["type"] == "INVALID_LOGARITHMIC_FREQUENCY_RANGE" for v in res["violations"])


# ========================================================================================
# 4. In-Memory REST API Endpoints Verification
# ========================================================================================

class TestIntelligenceRESTEndpoints:
    def test_rest_concept_map_get(self):
        """Verify GET /api/intelligence/concept_map returns the complete concept graph."""
        status, body = execute_mock_http_request("GET", "/api/intelligence/concept_map")
        assert status == 200
        assert body["status"] == "SUCCESS"
        cmap = body["concept_map"]
        assert cmap["total_concepts"] >= 20
        assert cmap["total_dependencies"] > 0
        assert len(cmap["nodes"]) == cmap["total_concepts"]

    def test_rest_student_confidence_get(self):
        """Verify GET /api/intelligence/student_confidence returns student profile."""
        concept_intelligence_engine.record_concept_evaluation("STU_API_TEST", "OHMS_LAW", 85.0)
        status, body = execute_mock_http_request("GET", "/api/intelligence/student_confidence?student_id=STU_API_TEST")
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert body["student_id"] == "STU_API_TEST"
        assert "OHMS_LAW" in body["confidence"]

    def test_rest_remedial_path_post(self):
        """Verify POST /api/intelligence/remedial_path generates dynamic micro-lessons."""
        payload = {
            "student_id": "STU_API_REMEDIAL",
            "failed_concept_id": "BJT_ACTIVE_AMPLIFIER"
        }
        status, body = execute_mock_http_request("POST", "/api/intelligence/remedial_path", payload)
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert body["failed_concept_id"] == "BJT_ACTIVE_AMPLIFIER"
        assert len(body["remedial_micro_lessons"]) > 0
        assert "estimated_remedial_time_minutes" in body

    def test_rest_check_assumptions_math_post(self):
        """Verify POST /api/intelligence/check_assumptions with MATH_TRANSFER payload."""
        payload = {
            "check_type": "MATH_TRANSFER",
            "domain": "LAPLACE",
            "poles": [{"real": 2.5, "imag": 0.0}, {"real": -5.0, "imag": 0.0}],
            "zeros": []
        }
        status, body = execute_mock_http_request("POST", "/api/intelligence/check_assumptions", payload)
        assert status == 200
        assert body["status"] == "SUCCESS"
        assumptions = body["assumptions"]
        assert assumptions["assumptions_valid"] is False
        assert any(v["type"] == "UNSTABLE_POLE_STEADY_STATE_VIOLATION" for v in assumptions["violations"])

    def test_rest_check_assumptions_analog_post(self):
        """Verify POST /api/intelligence/check_assumptions with ANALOG_CIRCUIT netlist."""
        netlist = """
        * Simple Saturated BJT test
        Vcc c 0 DC 5
        Vbb b 0 DC 2
        Rb b base_node 10k
        Rc c col_node 4.7k
        Q1 col_node base_node 0 2N2222
        .op
        .end
        """
        payload = {
            "check_type": "ANALOG_CIRCUIT",
            "netlist": netlist
        }
        status, body = execute_mock_http_request("POST", "/api/intelligence/check_assumptions", payload)
        assert status == 200
        assert body["status"] == "SUCCESS"
        assert "assumptions" in body


# ========================================================================================
# 5. Thermal & Execution Performance Budget Test (< 350ms on HP Victus)
# ========================================================================================

class TestThermalPerformanceBudget:
    def test_intelligence_pipeline_budget(self):
        """Verify end-to-end intelligence evaluations and audits execute well within 350ms."""
        start_time = time.perf_counter()

        # 1. Evaluate concept
        concept_intelligence_engine.record_concept_evaluation("STU_BUDGET", "BJT_ACTIVE_AMPLIFIER", 40.0)

        # 2. Generate remedial path with backward DAG traversal
        path = concept_intelligence_engine.generate_remedial_path("STU_BUDGET", "BJT_ACTIVE_AMPLIFIER")
        assert path["status"] == "SUCCESS"

        # 3. Check mathematical assumptions
        math_res = MathematicalAssumptionsChecker.check_assumptions(
            "LAPLACE",
            [complex(-2, 0), complex(1, 0)],
            [complex(3, 0)]
        )
        assert math_res["assumptions_valid"] is False

        # 4. Check circuit assumptions
        circ = Circuit(title="Budget Test Circuit")
        circ.add_bjt("Q1", "c", "b", "0", bjt_type="NPN")
        circ_res = CircuitAssumptionsChecker.check_assumptions(circ, {"node_voltages": {"c": 0.1, "b": 0.7, "0": 0.0}})
        assert circ_res["assumptions_valid"] is False

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        assert elapsed_ms < 350.0, f"Performance budget exceeded: {elapsed_ms:.2f}ms >= 350.0ms"
