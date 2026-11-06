"""
========================================================================================
VoltCore Apex Academia - Unit Tests for Course Configuration & DAG Resolver
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead & Systems Architect: Ashok Kumar A
========================================================================================
"""

import pytest
from backend.course_config_engine import CourseConfigEngine, COURSE_REGISTRY_DATA


@pytest.fixture
def engine():
    return CourseConfigEngine()


def test_priority_courses_exist(engine):
    """Verify that all four required priority courses are registered."""
    expected_codes = ["EC23S01", "EC23C03", "EC23E04", "EC8702"]
    for code in expected_codes:
        course = engine.get_course(code)
        assert course is not None, f"Course {code} must be present in registry"
        assert course["code"] == code
        assert len(course["title"]) > 0
        assert course["credits"] in [2, 3, 4]


def test_course_schema_validation(engine):
    """Verify schema integrity against Anna University Regulation 2023 fields."""
    for code in ["EC23S01", "EC23C03", "EC23E04", "EC8702"]:
        validation = engine.validate_course_schema(code)
        assert validation["valid"] is True
        assert validation["valid_ltp"] is True
        assert "category" in validation


def test_course_lookup_by_slug(engine):
    """Verify lookup by URL-friendly slug."""
    dsp = engine.get_course_by_slug("numerical-dsp-python")
    assert dsp is not None
    assert dsp["code"] == "EC23S01"

    devices = engine.get_course_by_slug("electronic-devices")
    assert devices is not None
    assert devices["code"] == "EC23C03"

    optics = engine.get_course_by_slug("optics-and-lasers")
    assert optics is not None
    assert optics["code"] == "EC23E04"

    embedded = engine.get_course_by_slug("embedded-systems")
    assert embedded is not None
    assert embedded["code"] == "EC8702"


def test_prerequisite_dag_resolution(engine):
    """Verify prerequisite DAG resolution without circular dependencies."""
    dag_dsp = engine.resolve_prerequisite_dag("EC23S01")
    assert dag_dsp["is_valid_dag"] is True
    assert dag_dsp["has_cycle"] is False
    assert len(dag_dsp["prerequisite_sequence"]) >= 2
    assert "EC23C04" in dag_dsp["prerequisite_sequence"] or "MA23C01" in dag_dsp["prerequisite_sequence"]

    dag_devices = engine.resolve_prerequisite_dag("EC23C03")
    assert dag_devices["is_valid_dag"] is True
    assert dag_devices["has_cycle"] is False


def test_circular_dependency_detection():
    """Verify that the DAG resolver detects circular dependencies properly."""
    cyclic_data = {
        "COURSE_A": {"code": "COURSE_A", "prerequisites": ["COURSE_B"]},
        "COURSE_B": {"code": "COURSE_B", "prerequisites": ["COURSE_C"]},
        "COURSE_C": {"code": "COURSE_C", "prerequisites": ["COURSE_A"]}
    }
    cyclic_engine = CourseConfigEngine(registry=cyclic_data)
    result = cyclic_engine.resolve_prerequisite_dag("COURSE_A")
    assert result["has_cycle"] is True
    assert result["is_valid_dag"] is False


def test_academic_rigor_and_hours_compliance(engine):
    """Verify that syllabus hours and Bloom's rigor comply with Anna University Reg 2023."""
    for code in ["EC23S01", "EC23C03", "EC23E04", "EC8702"]:
        rigor = engine.audit_academic_rigor(code)
        assert rigor["is_hour_compliant"] is True
        assert rigor["nba_tier1_aligned"] is True
        assert "L3-L6" in rigor["obe_blooms_rigor"]
