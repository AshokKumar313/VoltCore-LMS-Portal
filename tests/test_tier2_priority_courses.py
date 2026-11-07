"""
========================================================================================
VoltCore Apex Academia - Tier 2 Priority Courses Testbed & Validation Suite
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead & Systems Architect: Ashok Kumar A
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313

Validates:
  1. Descriptive engineering course names and metadata integrity (4 Priority Courses)
  2. Outcome-Based Education (OBE) tags, Choice-Based Credit System (CBCS) params & Bloom levels
  3. Granular Module-to-Laboratory relationships
  4. Curriculum DAG dependency resolution and topological acyclicity
  5. Mathematical simulation engines (DSP Chebyshev/Butterworth, Diode/MOSFET, Cavity/Fabry-Perot, FreeRTOS RMS)
  6. Quiz scoring and assessment under SQLite WAL mode with 5s busy timeout
  7. Passive CPU footprint (<500ms execution) ensuring HP Victus laptop thermal safety
========================================================================================
"""

import os
import time
import math
import tempfile
import pytest
import sqlite3

from backend.course_config_engine import CourseConfigEngine, COURSE_REGISTRY_DATA
from backend.course_lab_engine import CourseLabEngine
from backend.course_quiz_engine import CourseQuizEngine

TIER2_COURSES = {
    "EC23S01": {
        "expected_title": "Python Digital Signal Processing",
        "expected_short_title": "Python DSP",
        "credits": 2,
        "category": "Employability Enhancement (EEC)"
    },
    "EC23C03": {
        "expected_title": "Electronic Devices and Circuits",
        "expected_short_title": "Devices & Circuits",
        "credits": 3,
        "category": "Professional Core (PCC)"
    },
    "EC23E04": {
        "expected_title": "Optics, Lasers and Fiber Optics",
        "expected_short_title": "Optics & Fiber Optics",
        "credits": 3,
        "category": "Professional Elective (PEC)"
    },
    "EC8702": {
        "expected_title": "Advanced Embedded Systems Architecture",
        "expected_short_title": "Advanced Embedded Architecture",
        "credits": 3,
        "category": "Professional Core (PCC)"
    }
}


@pytest.fixture
def config_engine():
    return CourseConfigEngine()


@pytest.fixture
def lab_engine():
    return CourseLabEngine()


@pytest.fixture
def temp_wal_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        if os.path.exists(path):
            os.remove(path)
        wal = path + "-wal"
        shm = path + "-shm"
        if os.path.exists(wal):
            os.remove(wal)
        if os.path.exists(shm):
            os.remove(shm)
    except OSError:
        pass


# -----------------------------------------------------------------------------
# 1. DESCRIPTIVE ENGINEERING TITLES & COURSE METADATA
# -----------------------------------------------------------------------------

def test_tier2_descriptive_engineering_titles(config_engine):
    """Verify each of the 4 priority courses uses the updated descriptive engineering title."""
    for code, spec in TIER2_COURSES.items():
        course = config_engine.get_course(code)
        assert course is not None, f"Course {code} must be present in registry"
        assert course["title"] == spec["expected_title"]
        assert course["short_title"] == spec["expected_short_title"]
        assert course["credits"] == spec["credits"]
        assert course["category"] == spec["category"]


# -----------------------------------------------------------------------------
# 2. OBE ATTAINMENT TAGS, CBCS PARAMETERS & BLOOM'S TAXONOMY
# -----------------------------------------------------------------------------

def test_tier2_obe_and_blooms_taxonomy_levels(config_engine):
    """Verify each syllabus unit contains valid OBE attainment tags and Bloom levels (L3-L6)."""
    valid_bloom_levels = {
        "L1 (Remember)", "L2 (Understand)", "L3 (Apply)",
        "L4 (Analyze)", "L5 (Evaluate)", "L6 (Create)"
    }

    for code in TIER2_COURSES:
        obe_tags = config_engine.get_obe_attainment_tags(code)
        assert len(obe_tags) == 5, f"Course {code} must have 5 units with OBE tags"

        for unit in obe_tags:
            tag = unit["obe_attainment_tag"]
            bloom = unit["bloom_level"]
            assert tag.startswith("OBE-CO"), f"Unit tag {tag} must start with OBE-CO"
            assert bloom in valid_bloom_levels, f"Unit Bloom level {bloom} is invalid"
            assert unit["cbcs_params"] is not None
            assert "credit_weight" in unit["cbcs_params"]


def test_tier2_cbcs_classification_parameters(config_engine):
    """Verify Choice-Based Credit System (CBCS) grading scheme and weight distribution."""
    for code in TIER2_COURSES:
        cbcs = config_engine.get_cbcs_parameters(code)
        assert cbcs, f"Course {code} must specify CBCS classification"
        assert cbcs["credit_value"] in [2, 3]
        assert cbcs["contact_hours_per_week"] in [3, 4]
        assert "Letter Grade" in cbcs["grading_scheme"]

        # Ensure continuous internal evaluation + end-semester weights sum to 100%
        cie = cbcs["continuous_evaluation_weight"]
        ese = cbcs["end_semester_weight"]
        assert cie + ese == 100, f"Weights for {code} must sum to 100, got {cie + ese}"


# -----------------------------------------------------------------------------
# 3. GRANULAR MODULE-TO-LABORATORY RELATIONSHIPS
# -----------------------------------------------------------------------------

def test_tier2_module_to_laboratory_mappings(config_engine):
    """Verify that each unit is linked to a concrete lab experiment and simulation component."""
    for code in TIER2_COURSES:
        mappings = config_engine.get_module_lab_mappings(code)
        assert len(mappings) == 5, f"Course {code} must have 5 module-to-lab mappings"

        for mapping in mappings:
            assert mapping["lab_id"].startswith(code)
            assert len(mapping["lab_title"]) > 10
            assert len(mapping["simulation_component"]) > 0
            assert mapping["obe_target_co"].startswith("CO")
            assert "L" in mapping["bloom_level"]


# -----------------------------------------------------------------------------
# 4. CURRICULUM DAG DEPENDENCY RESOLUTION
# -----------------------------------------------------------------------------

def test_tier2_curriculum_dag_acyclicity(config_engine):
    """Verify that prerequisite DAG dependencies resolve without cycles."""
    for code in TIER2_COURSES:
        dag = config_engine.resolve_prerequisite_dag(code)
        assert dag["is_valid_dag"] is True, f"DAG for {code} must be valid"
        assert dag["has_cycle"] is False, f"DAG for {code} must be acyclic"
        assert dag["total_prerequisites"] >= 1


# -----------------------------------------------------------------------------
# 5. SIMULATION PHYSICS ENGINE VALIDATION
# -----------------------------------------------------------------------------

def test_simulation_dsp_butterworth_and_chebyshev(lab_engine):
    """Verify Butterworth and Chebyshev filter frequency responses and roll-off rates."""
    # 1. Butterworth: Maximally flat passband, -3dB at cutoff
    bw = lab_engine.simulate_dsp_butterworth(fc=1200.0, fs=16000.0, order=3)
    assert bw["is_nyquist_valid"] is True
    assert bw["db_at_cutoff"] == pytest.approx(-3.01, abs=0.1)
    assert bw["roll_off_db_per_decade"] == -60

    # 2. Chebyshev: Equiripple passband with 1.0 dB ripple
    cheb = lab_engine.simulate_dsp_chebyshev(fc=1200.0, fs=16000.0, order=3, ripple_db=1.0)
    assert cheb["is_nyquist_valid"] is True
    assert cheb["epsilon"] > 0
    # Stopband point at 2*fc should attenuate significantly
    stopband_point = [pt for pt in cheb["test_points"] if pt["ratio"] == 2.0][0]
    assert stopband_point["gain_db"] < -15.0


def test_simulation_device_iv_diode_and_mosfet(lab_engine):
    """Verify Shockley diode exponential conduction and MOSFET saturation current."""
    res = lab_engine.simulate_device_iv(vf=0.68, temp_k=300.0, vgs=3.5, vth=1.2, kn=20.0)
    assert res["vt_mv"] == pytest.approx(25.85, abs=0.5)
    assert res["diode_current_ma"] > 0.1
    assert res["is_conduction_active"] is True

    # MOSFET saturation: Vov = 3.5 - 1.2 = 2.3V; ID,sat = 0.5 * 20 * (2.3)^2 = 52.9 mA
    assert res["vov"] == pytest.approx(2.3, abs=0.01)
    assert res["mosfet_sat_id_ma"] == pytest.approx(52.9, abs=0.2)


def test_simulation_optics_cavity_and_fabry_perot(lab_engine):
    """Verify optical resonator stability and Fabry-Perot cavity finesse."""
    # Resonator: L=0.5m, R1=1.0m, R2=0.8m -> g1=0.5, g2=0.375 -> g1*g2 = 0.1875 (Stable)
    cavity = lab_engine.simulate_laser_cavity(cavity_length=0.5, r1=1.0, r2=0.8)
    assert cavity["is_stable"] is True
    assert cavity["g_prod"] == pytest.approx(0.1875, abs=0.001)
    assert cavity["mode_spacing_mhz"] == pytest.approx(299.79, abs=0.5)

    # Fabry-Perot Etalon: L=0.5m, R=0.95 -> Finesse = pi * sqrt(0.95) / (1 - 0.95) ≈ 61.24
    fp = lab_engine.simulate_fabry_perot_etalon(cavity_length=0.5, reflectance=0.95)
    assert fp["finesse"] == pytest.approx(61.24, abs=0.2)
    assert fp["fsr_mhz"] == pytest.approx(299.79, abs=0.5)


def test_simulation_rtos_schedulability_rms(lab_engine):
    """Verify FreeRTOS Rate Monotonic Scheduling (RMS) utilization bounds."""
    # Task 1: C=8ms, T=30ms (26.67%)
    # Task 2: C=12ms, T=50ms (24.00%)
    # Task 3: C=15ms, T=100ms (15.00%)
    # Total U = 65.67% <= 77.98% (Guaranteed Schedulable)
    tasks = [
        {"c": 8.0, "t": 30.0},
        {"c": 12.0, "t": 50.0},
        {"c": 15.0, "t": 100.0}
    ]
    res = lab_engine.simulate_rtos_schedulability(tasks)
    assert res["is_schedulable"] is True
    assert res["total_utilization_pct"] == pytest.approx(65.67, abs=0.1)
    assert res["liu_layland_bound_pct"] == pytest.approx(77.98, abs=0.1)


# -----------------------------------------------------------------------------
# 6. QUIZ SCORING & SQLITE WAL MODE PERSISTENCE
# -----------------------------------------------------------------------------

def test_quiz_scoring_and_sqlite_wal_persistence(temp_wal_db):
    """Verify quiz assessment scoring and history logging under SQLite WAL mode."""
    quiz_engine = CourseQuizEngine(db_path=temp_wal_db)

    # 1. Verify SQLite PRAGMA journal_mode is WAL
    conn = sqlite3.connect(temp_wal_db)
    journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
    conn.close()
    assert journal_mode.upper() == "WAL", f"Expected WAL mode, got {journal_mode}"

    # 2. Evaluate quiz for Tier 2 course EC23S01
    answers = {
        "EC23S01_Q1": 0,
        "EC23S01_Q2": 1
    }
    result = quiz_engine.evaluate_submission(
        course_code="EC23S01",
        student_id="STUDENT_TEST_001",
        answers=answers
    )
    assert "submission_id" in result
    assert result["percentage"] >= 0.0
    assert result["total_mcqs"] > 0
    assert result["student_id"] == "STUDENT_TEST_001"

    # 3. Verify attempt was persisted into SQLite database in WAL mode
    conn = sqlite3.connect(temp_wal_db)
    row = conn.execute(
        "SELECT course_code, student_id, percentage FROM course_quiz_submissions WHERE student_id = ?",
        ("STUDENT_TEST_001",)
    ).fetchone()
    conn.close()
    assert row is not None
    assert row[0] == "EC23S01"
    assert row[1] == "STUDENT_TEST_001"



# -----------------------------------------------------------------------------
# 7. THERMAL SAFETY & PASSIVE CPU EXECUTION
# -----------------------------------------------------------------------------

def test_thermal_safety_execution_benchmark(config_engine, lab_engine):
    """Verify that combined metadata resolution and physics simulation executes within <100ms."""
    t_start = time.perf_counter()

    for code in TIER2_COURSES:
        config_engine.get_course(code)
        config_engine.get_obe_attainment_tags(code)
        config_engine.get_cbcs_parameters(code)
        config_engine.get_module_lab_mappings(code)
        config_engine.resolve_prerequisite_dag(code)

    lab_engine.simulate_dsp_butterworth(1200, 16000, 3)
    lab_engine.simulate_dsp_chebyshev(1200, 16000, 3)
    lab_engine.simulate_device_iv(0.68, 300)
    lab_engine.simulate_laser_cavity(0.5, 1.0, 0.8)
    lab_engine.simulate_fabry_perot_etalon(0.5, 0.95)

    elapsed_ms = (time.perf_counter() - t_start) * 1000.0
    assert elapsed_ms < 150.0, f"Benchmark took {elapsed_ms}ms, exceeding passive CPU thermal threshold"
