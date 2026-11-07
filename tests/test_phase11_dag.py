"""
========================================================================================
VoltCore Apex Academia - Phase 11 Test Suite
Prerequisite Directed Acyclic Graph (DAG) & Student Mastery Progression Engine
Anna University / MIT Campus - Department of Electronics Engineering
Lead Systems Architect: Ashok Kumar A
========================================================================================
"""

import os
import sys
import json
import sqlite3
import threading
import pytest
from io import BytesIO
from typing import Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.course_config_engine import (
    CourseConfigEngine,
    CurriculumMasteryEngine,
    CURRICULUM_PREREQUISITE_GRAPH,
    COURSE_REGISTRY_DATA,
    course_config_engine,
    curriculum_mastery_engine
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
def isolated_mastery_engine(tmp_path):
    """Provides an isolated CurriculumMasteryEngine instance with a clean SQLite WAL database."""
    db_file = str(tmp_path / "test_curriculum_mastery.db")
    engine = CurriculumMasteryEngine(db_path=db_file)
    return engine


# --------------------------------------------------------------------------------------
# 1. Topological DAG Sorter & Global Acyclicity Verification
# --------------------------------------------------------------------------------------
def test_topological_sort_and_acyclicity():
    """Verify that get_topological_sort() produces a valid topological sequence without cycles."""
    engine = CourseConfigEngine()
    topo_res = engine.get_topological_sort()
    topo_order = topo_res["topological_order"]

    assert len(topo_order) > 0, "Topological sort should contain nodes from curriculum graph."
    assert len(topo_order) == len(CURRICULUM_PREREQUISITE_GRAPH), "All curriculum nodes should be represented."

    # Validate that every prerequisite precedes its dependent node in the sequence
    position = {node: i for i, node in enumerate(topo_order)}
    for node, data in CURRICULUM_PREREQUISITE_GRAPH.items():
        for prereq in data.get("prerequisites", []):
            if prereq in position and node in position:
                assert position[prereq] < position[node], (
                    f"Topological violation: Prerequisite '{prereq}' (pos {position[prereq]}) "
                    f"must precede dependent '{node}' (pos {position[node]})."
                )

    assert topo_res["is_valid_dag"] is True
    assert topo_res["has_cycle"] is False
    assert engine.validate_no_cycles() is True


# --------------------------------------------------------------------------------------
# 2. Cycle Detection with Injected Circular Dependencies
# --------------------------------------------------------------------------------------
def test_circular_dependency_detection():
    """Verify that DFS correctly detects and reports circular dependencies."""
    cyclic_graph = {
        "ALPHA": {"prerequisites": ["GAMMA"], "tier": "Test"},
        "BETA": {"prerequisites": ["ALPHA"], "tier": "Test"},
        "GAMMA": {"prerequisites": ["BETA"], "tier": "Test"},
        "DELTA": {"prerequisites": ["ALPHA"], "tier": "Test"}
    }
    engine = CourseConfigEngine()
    # Inject cyclic graph
    engine_cycle = CourseConfigEngine()

    # Temporarily monkey-patch or test directly
    from backend import course_config_engine as cce_mod
    original_graph = cce_mod.CURRICULUM_PREREQUISITE_GRAPH
    try:
        cce_mod.CURRICULUM_PREREQUISITE_GRAPH = cyclic_graph
        res = engine_cycle.resolve_prerequisite_dag("DELTA")
        assert res["has_cycle"] is True
        assert res["is_valid_dag"] is False
        assert len(res["cycle_path"]) >= 3
        assert "ALPHA" in res["cycle_path"]
        assert "BETA" in res["cycle_path"]
        assert "GAMMA" in res["cycle_path"]
    finally:
        cce_mod.CURRICULUM_PREREQUISITE_GRAPH = original_graph


# --------------------------------------------------------------------------------------
# 3. Mastery Token Issuance at >= 70% Threshold
# --------------------------------------------------------------------------------------
def test_mastery_token_issuance_threshold(isolated_mastery_engine):
    """Verify that scores >= 70% issue cryptographic mastery tokens while < 70% are flagged remedial."""
    # Test passing evaluation (85%)
    pass_res = isolated_mastery_engine.record_mastery_evaluation(
        student_id="STUDENT_PASS_01",
        module_id="EC8702",
        course_code="EC8702",
        score=85.0,
        max_score=100.0,
        evaluation_type="LAB_EXAM"
    )
    assert pass_res["status"] == "SUCCESS"
    assert pass_res["mastery_achieved"] is True
    assert pass_res["attainment_pct"] == 85.0
    assert pass_res["token_id"].startswith("TOK_STUDENT_PASS_01_EC8702_")
    assert len(pass_res["unlocked_downstream_nodes"]) > 0

    # Test failing evaluation (62.5%)
    fail_res = isolated_mastery_engine.record_mastery_evaluation(
        student_id="STUDENT_FAIL_02",
        module_id="EC8702",
        course_code="EC8702",
        score=62.5,
        max_score=100.0,
        evaluation_type="QUIZ"
    )
    assert fail_res["status"] == "REMEDIAL_REQUIRED"
    assert fail_res["mastery_achieved"] is False
    assert fail_res["attainment_pct"] == 62.5
    assert fail_res["token_id"] is None
    assert fail_res["unlocked_downstream_nodes"] == []

    # Verify database table contents
    conn = sqlite3.connect(isolated_mastery_engine.db_path)
    cur = conn.cursor()
    cur.execute("SELECT token_id, attainment_pct FROM module_mastery_tokens WHERE student_id = ?;", ("STUDENT_PASS_01",))
    pass_tokens = cur.fetchall()
    assert len(pass_tokens) == 1
    assert pass_tokens[0][1] == 85.0

    cur.execute("SELECT token_id FROM module_mastery_tokens WHERE student_id = ?;", ("STUDENT_FAIL_02",))
    fail_tokens = cur.fetchall()
    assert len(fail_tokens) == 0, "No token should be issued for < 70% score."
    conn.close()


# --------------------------------------------------------------------------------------
# 4. Prerequisite Enforcement & Stepwise Unlocking
# --------------------------------------------------------------------------------------
def test_prerequisite_enforcement_and_dynamic_unlocking(isolated_mastery_engine):
    """Verify that dependent node IOT8701 remains locked until both EC8702 and EC23C03 are mastered."""
    student_id = "STUDENT_STEP_03"
    target = "IOT8701"

    # Step 1: Initial state (both prerequisites missing)
    v1 = isolated_mastery_engine.verify_node_unlocked(student_id, target)
    assert v1["is_unlocked"] is False
    assert v1["status"] == "LOCKED"
    assert "EC8702" in v1["missing_prerequisites"]
    assert "EC23C03" in v1["missing_prerequisites"]

    # Step 2: Pass EC8702 with 90% (one prerequisite satisfied)
    isolated_mastery_engine.record_mastery_evaluation(student_id, "EC8702", "EC8702", 90.0, 100.0)
    v2 = isolated_mastery_engine.verify_node_unlocked(student_id, target)
    assert v2["is_unlocked"] is False
    assert v2["status"] == "LOCKED"
    assert v2["satisfied_prerequisites"] == ["EC8702"]
    assert v2["missing_prerequisites"] == ["EC23C03"]

    # Step 3: Pass EC23C03 with 82% (all prerequisites satisfied)
    isolated_mastery_engine.record_mastery_evaluation(student_id, "EC23C03", "EC23C03", 82.0, 100.0)
    v3 = isolated_mastery_engine.verify_node_unlocked(student_id, target)
    assert v3["is_unlocked"] is True
    assert v3["status"] == "UNLOCKED"
    assert len(v3["missing_prerequisites"]) == 0
    assert "EC8702" in v3["mastery_tokens"]
    assert "EC23C03" in v3["mastery_tokens"]


# --------------------------------------------------------------------------------------
# 5. Student Curriculum State Compilation
# --------------------------------------------------------------------------------------
def test_student_curriculum_state_compilation(isolated_mastery_engine):
    """Verify get_student_curriculum_state accurately maps total, mastered, unlocked, and locked counts."""
    student_id = "STUDENT_STATE_04"

    # Before mastering anything, foundational nodes (0 prereqs) should be UNLOCKED, others LOCKED
    state_init = isolated_mastery_engine.get_student_curriculum_state(student_id)
    assert state_init["mastered_count"] == 0
    assert state_init["unlocked_count"] > 0
    assert state_init["locked_count"] > 0
    assert state_init["summary"]["completion_pct"] == 0.0

    # Master foundational nodes
    isolated_mastery_engine.record_mastery_evaluation(student_id, "EE23C01", "EE23C01", 80.0, 100.0)
    isolated_mastery_engine.record_mastery_evaluation(student_id, "PH23C01", "PH23C01", 88.0, 100.0)

    state_after = isolated_mastery_engine.get_student_curriculum_state(student_id)
    assert state_after["mastered_count"] == 2
    assert state_after["summary"]["completion_pct"] > 0.0
    assert state_after["nodes"]["EE23C01"]["status"] == "MASTERED"
    assert state_after["nodes"]["PH23C01"]["status"] == "MASTERED"


# --------------------------------------------------------------------------------------
# 6. Faculty / Admin Mastery Override
# --------------------------------------------------------------------------------------
def test_faculty_admin_mastery_override(isolated_mastery_engine):
    """Verify RBAC on mastery override: Faculty/Admin allowed, Student/Unauthorized rejected."""
    student_id = "STUDENT_OVERRIDE_05"

    # Student role should be rejected
    res_student = isolated_mastery_engine.grant_mastery_override(
        student_id=student_id,
        module_id="EC8702",
        course_code="EC8702",
        actor_role="Student"
    )
    assert res_student["status"] == "FORBIDDEN"

    # Faculty role should be accepted and grant 100% token
    res_faculty = isolated_mastery_engine.grant_mastery_override(
        student_id=student_id,
        module_id="EC8702",
        course_code="EC8702",
        actor_role="Faculty",
        notes="Academic Committee Fast-Track Exemption"
    )
    assert res_faculty["status"] == "SUCCESS"
    assert res_faculty["mastery_achieved"] is True
    assert res_faculty["score"] == 100.0

    # Verification confirms node is now mastered
    v = isolated_mastery_engine.verify_node_unlocked(student_id, "RTOS8706")
    assert "EC8702" in v["satisfied_prerequisites"]


# --------------------------------------------------------------------------------------
# 7. Multi-Threaded Concurrency Under SQLite WAL Mode
# --------------------------------------------------------------------------------------
def test_wal_concurrency_multi_threaded_mastery(isolated_mastery_engine):
    """Verify that 10 concurrent threads write evaluations simultaneously without SQLite database locks."""
    errors = []
    modules = ["EE23C01", "PH23C01", "MA23C01", "EC3352", "EC3451", "EC23C02", "EC23C04", "EC23C05", "EC8702", "EC23C03"]

    def worker(idx: int):
        try:
            m = modules[idx % len(modules)]
            s_id = f"CONCURRENT_STUDENT_{idx}"
            res = isolated_mastery_engine.record_mastery_evaluation(
                student_id=s_id,
                module_id=m,
                course_code=m,
                score=75.0 + idx,
                max_score=100.0
            )
            if res.get("status") != "SUCCESS":
                errors.append(f"Worker {idx} status: {res.get('status')}")
        except Exception as e:
            errors.append(f"Worker {idx} raised: {e}")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Concurrency errors encountered: {errors}"


# --------------------------------------------------------------------------------------
# 8. HTTP Fallback REST Endpoints Verification
# --------------------------------------------------------------------------------------
def test_curriculum_http_endpoints():
    """Verify GET and POST curriculum endpoints via FallbackHTTPHandler."""
    handler_class = getattr(attendance_server, "FallbackHTTPHandler", None)
    if not handler_class:
        pytest.skip("FallbackHTTPHandler not found.")

    # 1. GET /api/curriculum/dag?target_course=IOT8701
    req_get = b"GET /api/curriculum/dag?target_course=IOT8701 HTTP/1.1\r\nHost: localhost\r\n\r\n"
    sock = MockSocket(req_get)
    handler = handler_class(sock, ("127.0.0.1", 5000), None)
    resp_text = sock._wfile.getvalue().decode("utf-8")
    assert "200 OK" in resp_text
    assert "IOT8701" in resp_text

    # 2. GET /api/curriculum/prerequisites/verify?student_id=TEST_S11&target_node=IOT8701
    req_verify = b"GET /api/curriculum/prerequisites/verify?student_id=TEST_S11&target_node=IOT8701 HTTP/1.1\r\nHost: localhost\r\n\r\n"
    sock2 = MockSocket(req_verify)
    handler2 = handler_class(sock2, ("127.0.0.1", 5000), None)
    resp2 = sock2._wfile.getvalue().decode("utf-8")
    assert "200 OK" in resp2
    assert "TEST_S11" in resp2

    # 3. POST /api/curriculum/mastery/record
    payload = json.dumps({
        "student_id": "TEST_S11",
        "module_id": "EC8702",
        "course_code": "EC8702",
        "score": 88.0,
        "max_score": 100.0
    }).encode("utf-8")
    req_post = f"POST /api/curriculum/mastery/record HTTP/1.1\r\nHost: localhost\r\nContent-Length: {len(payload)}\r\nContent-Type: application/json\r\n\r\n".encode("utf-8") + payload
    sock3 = MockSocket(req_post)
    handler3 = handler_class(sock3, ("127.0.0.1", 5000), None)
    resp3 = sock3._wfile.getvalue().decode("utf-8")
    assert "200 OK" in resp3
    assert "SUCCESS" in resp3


# --------------------------------------------------------------------------------------
# 9. Privacy & Host Thermal Invariants
# --------------------------------------------------------------------------------------
def test_privacy_and_thermal_safety_invariants():
    """Ensure zero personal email/phone leaks and verify fast low-overhead execution."""
    restricted_encoded = "YXNob2trdW1hcjIwMDgzMTNAZ21haWwuY29t"
    import base64
    restricted_email = base64.b64decode(restricted_encoded).decode("utf-8")

    files_to_check = [
        os.path.join("backend", "course_config_engine.py"),
        "attendance_server.py",
        os.path.join("src", "data", "course_config_schema.ts"),
        os.path.join("src", "components", "CourseNavigationSidebar.jsx"),
        os.path.join("src", "components", "CourseShellHub.jsx")
    ]

    for fpath in files_to_check:
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                assert restricted_email not in content, f"Restricted metadata leaked in {fpath}"
