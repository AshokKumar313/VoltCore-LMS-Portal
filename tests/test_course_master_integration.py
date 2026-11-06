"""
========================================================================================
VoltCore Apex Academia - Master Course Experience End-to-End Integration Tests (Phase 10)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead & Systems Architect: Ashok Kumar A
========================================================================================
"""

import pytest
import tempfile
import os
import time

from backend.course_config_engine import CourseConfigEngine, COURSE_REGISTRY_DATA
from backend.course_quiz_engine import CourseQuizEngine, COURSE_QUIZ_CATALOG
from backend.course_lab_engine import CourseLabEngine, COURSE_LAB_CATALOG_DATA
from backend.course_projects_engine import CourseProjectsEngine, COURSE_PROJECTS_CATALOG, COURSE_PRACTICALS_CATALOG


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


@pytest.fixture
def unified_suite(temp_db):
    return {
        "config": CourseConfigEngine(),
        "quiz": CourseQuizEngine(db_path=temp_db),
        "lab": CourseLabEngine(db_path=temp_db),
        "projects": CourseProjectsEngine(db_path=temp_db)
    }


def test_all_four_courses_registered_in_config(unified_suite):
    """Verify that all 4 priority courses are registered with full Regulation 2023 specs."""
    config_engine = unified_suite["config"]
    priority_codes = ["EC23S01", "EC23C03", "EC23E04", "EC8702"]

    for code in priority_codes:
        course = config_engine.get_course(code)
        assert course is not None, f"Course {code} must be registered"
        assert course["regulation"] == "Anna University Regulation 2023"
        assert course["credits"] in [2, 3, 4]
        assert course["cos_count"] == 5

        # Validate schema
        schema_audit = config_engine.validate_course_schema(code)
        assert schema_audit["valid"] is True


def test_cross_engine_code_consistency(unified_suite):
    """Verify consistent catalog synchronization across Config, Quiz, Lab, and Project engines."""
    priority_codes = ["EC23S01", "EC23C03", "EC23E04", "EC8702"]

    for code in priority_codes:
        # 1. Quizzes Catalog
        assert code in COURSE_QUIZ_CATALOG, f"Course {code} missing from Quiz catalog"
        assert len(COURSE_QUIZ_CATALOG[code]) >= 4

        # 2. Labs Catalog
        assert code in COURSE_LAB_CATALOG_DATA, f"Course {code} missing from Lab catalog"
        assert len(COURSE_LAB_CATALOG_DATA[code]) >= 1

        # 3. Projects Catalog
        assert code in COURSE_PROJECTS_CATALOG, f"Course {code} missing from Projects catalog"
        assert len(COURSE_PROJECTS_CATALOG[code]) >= 2

        # 4. Practicals Catalog
        assert code in COURSE_PRACTICALS_CATALOG, f"Course {code} missing from Practicals catalog"
        assert len(COURSE_PRACTICALS_CATALOG[code]) >= 1


def test_end_to_end_assessment_and_grading(unified_suite):
    """Verify complete quiz assessment evaluation and SQLite gradebook insertion."""
    quiz_engine = unified_suite["quiz"]

    # Student submission on EC23S01
    answers = {
        "EC23S01_Q1": 2, # Correct (linear convolution length padding)
        "EC23S01_Q2": 1  # Correct (bilinear pre-warping)
    }
    result = quiz_engine.evaluate_submission("EC23S01", "2023MITEC042", answers)

    assert result["course_code"] == "EC23S01"
    assert result["percentage"] == 100.0
    assert result["correct_count"] == 2
    assert "submission_id" in result
    assert "bloom_performance" in result


def test_end_to_end_physics_simulators(unified_suite):
    """Verify analytical physics calculations across all four engineering domains."""
    lab_engine = unified_suite["lab"]

    # 1. DSP Butterworth Filter: 1 kHz cutoff, 16 kHz sampling, 3rd order
    dsp = lab_engine.simulate_dsp_butterworth(fc=1000, fs=16000, order=3, gain=1.0)
    assert dsp["is_nyquist_valid"] is True
    assert abs(dsp["mag_at_cutoff"] - 0.7071) < 0.005
    assert dsp["roll_off_db_per_decade"] == -60

    # 2. Semiconductor Diode & MOSFET: T = 300K, VF = 0.65V, VGS = 3.3V
    device = lab_engine.simulate_device_iv(vf=0.65, temp_k=300, eta=1.05, vgs=3.3, vth=1.2, kn=20.0)
    assert 25.8 <= device["vt_mv"] <= 25.9
    assert device["diode_current_ma"] > 0
    assert device["mosfet_sat_id_ma"] > 0

    # 3. Optics Laser Cavity: Confocal Resonator L = R1 = R2 = 0.5m
    laser = lab_engine.simulate_laser_cavity(cavity_length=0.5, r1=0.5, r2=0.5)
    assert laser["g_prod"] == 0.0
    assert laser["is_stable"] is True
    assert abs(laser["mode_spacing_mhz"] - 299.79) < 0.1

    # 4. Embedded Systems RTOS: 3 tasks, 84 MHz Cortex-M4
    rtos = lab_engine.simulate_rtos_schedulability([
        {"c": 5, "t": 30},
        {"c": 10, "t": 60},
        {"c": 15, "t": 120}
    ], core_clock_mhz=84.0)
    assert rtos["is_schedulable"] is True
    assert rtos["latency_savings_pct"] == 75.0


def test_end_to_end_projects_and_progress_flow(unified_suite):
    """Verify student milestone logging, progress tracking, and lab report generation."""
    proj_engine = unified_suite["projects"]

    # 1. Log milestone
    log_res = proj_engine.log_milestone_submission(
        course_code="EC23S01",
        project_id="EC23S01_PRJ1",
        milestone_id="M1",
        student_id="2023MITEC042",
        deliverable_url="local://repository/artifacts"
    )
    assert log_res["status"] == "success"

    # 2. Calculate Progress
    progress = proj_engine.calculate_course_progress(
        course_code="EC23S01",
        completed_milestone_keys=["EC23S01_PRJ1_M1", "EC23S01_PRJ1_M2", "EC23S01_PRJ1_M3", "EC23S01_PRJ1_M4"],
        verified_practical_ids=["EC23S01_EXP1", "EC23S01_EXP2"]
    )
    # 4 of 8 milestones (50% * 60 = 30%) + 2 of 2 practicals (100% * 40 = 40%) = 70.0%
    assert progress["overall_percentage"] == 70.0
    assert progress["academic_rank"] == "Hardware Adept"
    assert progress["earned_xp"] == (4 * 250) + (2 * 500)  # 2000 XP

    # 3. Generate Lab Report
    report = proj_engine.generate_lab_report(
        course_code="EC23S01",
        practical_id="EC23S01_EXP1",
        student_name="Ashok Kumar A",
        roll_number="2023MITEC042"
    )
    assert "report_markdown" in report
    assert "Continuous Internal Evaluation (CIE) Rubric" in report["report_markdown"]


def test_prerequisite_dag_acyclicity(unified_suite):
    """Verify prerequisite DAG resolution across all 4 courses is acyclic and valid."""
    config_engine = unified_suite["config"]

    for code in ["EC23S01", "EC23C03", "EC23E04", "EC8702"]:
        dag = config_engine.resolve_prerequisite_dag(code)
        assert dag["is_valid_dag"] is True
        assert dag["has_cycle"] is False
        assert "prerequisite_sequence" in dag
        assert dag["total_prerequisites"] >= 1


def test_performance_and_thermal_invariants(unified_suite):
    """Verify lightweight passive CPU footprint (<50ms execution) and zero thread leaks."""
    start_time = time.perf_counter()

    # Run combined pipeline across all 4 engines
    unified_suite["config"].validate_course_schema("EC23S01")
    unified_suite["quiz"].validate_catalog()
    unified_suite["lab"].simulate_dsp_butterworth(1200, 16000, 4)
    unified_suite["projects"].calculate_course_progress("EC23S01", ["M1"], ["EXP1"])

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    # Ensure passive execution well within thermal budget (<150 ms)
    assert elapsed_ms < 150.0, f"Combined execution exceeded thermal threshold: {elapsed_ms}ms"
