"""
========================================================================================
VoltCore Apex Academia - Unit Tests for Phase P: Accreditation & Compliance (Features 361–370)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
========================================================================================
"""

import os
import pytest
import tempfile
from backend.accreditation_compliance_engine import (
    AccreditationComplianceEngine,
    PROGRAM_OUTCOMES,
    BLOOM_LEVELS
)

@pytest.fixture
def temp_engine():
    """Create an isolated temporary SQLite database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = AccreditationComplianceEngine(db_path=path)
    yield engine
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def test_co_attainment_calculation_levels(temp_engine):
    """Feature 362: Course Outcome (CO) Attainment Calculator levels & composite formula."""
    # Level 3: >= 70% students score >= 60%
    c3 = temp_engine.calculate_co_attainment(students_above_threshold_pct=78.5, indirect_survey_avg=4.5)
    assert c3["direct_attainment_level"] == 3
    # 0.80 * 3 + 0.20 * (4.5/5.0 * 3.0) = 2.40 + 0.54 = 2.94
    assert c3["composite_attainment"] == 2.94
    assert c3["is_target_met"] is True

    # Level 2: 60% to 69.9%
    c2 = temp_engine.calculate_co_attainment(students_above_threshold_pct=64.0, indirect_survey_avg=4.0)
    assert c2["direct_attainment_level"] == 2
    # 0.80 * 2 + 0.20 * (4.0/5.0 * 3.0) = 1.60 + 0.48 = 2.08
    assert c2["composite_attainment"] == 2.08
    assert c2["is_target_met"] is False

    # Level 1: 50% to 59.9%
    c1 = temp_engine.calculate_co_attainment(students_above_threshold_pct=54.0, indirect_survey_avg=3.5)
    assert c1["direct_attainment_level"] == 1

    # Level 0: < 50%
    c0 = temp_engine.calculate_co_attainment(students_above_threshold_pct=42.0, indirect_survey_avg=3.0)
    assert c0["direct_attainment_level"] == 0


def test_record_co_attainment_persistence(temp_engine):
    """Feature 362 & 364: Direct/Indirect Attainment persistence in SQLite WAL."""
    rec = temp_engine.record_co_attainment(
        course_code="EC3552",
        co_id="CO1",
        pct_students_above_60=82.0,
        indirect_survey_rating=4.8
    )
    assert rec["status"] == "success"
    assert rec["attainment"]["direct_attainment_level"] == 3
    assert rec["cqi_required"] is False

    # Deficient CO triggering CQI requirement
    rec_cqi = temp_engine.record_co_attainment(
        course_code="EC3552",
        co_id="CO5",
        pct_students_above_60=45.0,
        indirect_survey_rating=3.2
    )
    assert rec_cqi["cqi_required"] is True


def test_po_pso_attainment_matrix_calculation(temp_engine):
    """Feature 363: PO & PSO Mapping Matrix and Weighted Attainment."""
    # Seed CO attainments for EC3552
    temp_engine.record_co_attainment("EC3552", "CO1", 85.0, 4.8) # Level 3
    temp_engine.record_co_attainment("EC3552", "CO2", 78.0, 4.5) # Level 3
    temp_engine.record_co_attainment("EC3552", "CO3", 65.0, 4.0) # Level 2
    temp_engine.record_co_attainment("EC3552", "CO4", 72.0, 4.4) # Level 3
    temp_engine.record_co_attainment("EC3552", "CO5", 58.0, 3.8) # Level 1

    po_data = temp_engine.calculate_po_attainments("EC3552")
    assert po_data["course_code"] == "EC3552"
    assert "PO1" in po_data["po_attainments"]
    assert "PSO1" in po_data["po_attainments"]
    assert po_data["po_attainments"]["PO1"] >= 2.0
    assert po_data["po_attainments"]["PSO1"] >= 2.0


def test_blooms_taxonomy_distribution(temp_engine):
    """Feature 365: Bloom's Taxonomy Level Distribution Analyzer."""
    blooms = temp_engine.analyze_blooms_distribution("EC3552")
    assert blooms["total_cos"] == 5
    assert blooms["counts"]["L4"] >= 2 # CO1 and CO3 are L4 Analyze
    assert blooms["counts"]["L6"] >= 1 # CO2 is L6 Create
    assert blooms["higher_order_thinking_pct"] >= 60.0
    assert blooms["is_nba_compliant"] is True


def test_cqi_logbook_workflow(temp_engine):
    """Feature 366: Continuous Quality Improvement (CQI) Logbook."""
    res = temp_engine.log_cqi_action(
        log_id="cqi_ec3552_01",
        course_code="EC3552",
        co_id="CO5",
        deficiency_reason="Students struggled with ATPG scan chain fault coverage and boundary scan testing.",
        corrective_action="Organize an extra 3-hour hands-on workshop using Synopsys TetraMAX / Cadence Modus ATPG tools.",
        responsible_faculty="Dr. P. Nirmal",
        review_cycle="AY 2026-2027"
    )
    assert res["status"] == "success"

    cqi_list = temp_engine.get_cqi_logbook("EC3552")
    assert len(cqi_list) == 1
    assert "TetraMAX" in cqi_list[0]["corrective_action"]
    assert cqi_list[0]["status"] == "OPEN"


def test_course_file_checklist_audit(temp_engine):
    """Feature 367: Faculty Course File Archivist checklist."""
    check = temp_engine.check_course_file_completeness("EC3552")
    assert check["total_items"] == 7
    assert check["is_audit_ready"] is False # initially 0% uploaded
    item_keys = [i["item_key"] for i in check["checklist"]]
    assert "item_syllabus" in item_keys
    assert "item_attainment" in item_keys
    assert "item_cqi" in item_keys


def test_student_exit_survey_indirect_attainment(temp_engine):
    """Feature 368: Student Feedback Analysis Portal on Likert scale."""
    temp_engine.submit_course_exit_survey(
        survey_id="surv_01",
        course_code="EC3552",
        student_roll="2023MITEC042",
        co1_rating=5, co2_rating=5, co3_rating=4, co4_rating=5, co5_rating=4,
        comments="Great exposure to Cadence EDA tools and STA slack closure."
    )
    temp_engine.submit_course_exit_survey(
        survey_id="surv_02",
        course_code="EC3552",
        student_roll="2023MITEC055",
        co1_rating=4, co2_rating=4, co3_rating=4, co4_rating=4, co5_rating=3,
        comments="Need more examples on ATPG scan compression."
    )

    ind_scores = temp_engine.get_survey_indirect_attainment("EC3552")
    assert ind_scores["CO1"] == 4.5
    assert ind_scores["CO2"] == 4.5
    assert ind_scores["CO5"] == 3.5


def test_nba_sar_summary_generation(temp_engine):
    """Feature 370: Self-Assessment Report (SAR) Criterion 3 Generator."""
    sar = temp_engine.generate_nba_sar_summary("EC3552")
    assert sar["department"] == "Department of Electronics Engineering"
    assert sar["accreditation_body"] == "National Board of Accreditation (NBA) Tier-1"
    assert "Criterion 3" in sar["criterion_evaluated"]
    assert sar["average_po_attainment"] > 0.0
    assert sar["higher_order_cognitive_percentage"] >= 60.0
