"""
========================================================================================
VoltCore Apex Academia - Phase 24 Verification Suite
AI Viva Voce Examination Simulator & OBE CO-PO Attainment Analytics
----------------------------------------------------------------------------------------
Module: tests/test_phase24_viva_obe.py
Platform Lead & Systems Director: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import tempfile
import pytest
from pathlib import Path

from backend.viva_voce_simulator_engine import (
    VivaVoceSimulatorEngine,
    ObeAttainmentEngine,
    CORE_VIVA_BANK,
    CO_PO_MAPPING_MATRIX,
    PROGRAM_OUTCOMES_DESC,
    INSTITUTIONAL_ATTAINMENT_THRESHOLD_PCT,
    viva_voce_engine,
    obe_attainment_engine
)

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


class TestVivaVoceSimulatorEngine:
    """Verifies conversational viva voce session management, rubric grading, and adaptive branching."""

    @pytest.fixture
    def test_engine(self):
        """Creates an isolated viva simulator backed by a temporary SQLite database."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_viva_telemetry.db")
        return VivaVoceSimulatorEngine(db_path=db_path)

    def test_session_initialization_and_first_question(self, test_engine):
        """Starting a session must register the student and provide an opening foundational question."""
        session = test_engine.start_session(
            student_id="2023MITEC042",
            domain="circuit_theorems"
        )

        assert "session_id" in session
        assert session["student_id"] == "2023MITEC042"
        assert session["domain"] == "circuit_theorems"

        first_q = session["first_question"]
        assert first_q["question_id"] == "VIVA_CKT_01"
        assert first_q["target_co"] == "CO1"
        assert first_q["max_marks"] == 10.0
        assert "Thevenin" in first_q["question_text"]

    def test_turn_evaluation_with_strong_answer(self, test_engine):
        """A comprehensive technical defense must achieve high rubric scores and Bloom mastery."""
        session = test_engine.start_session(student_id="2023MITEC042", domain="circuit_theorems")
        sess_id = session["session_id"]

        strong_answer = (
            "Thevenin theorem states that any linear active bilateral network can be replaced by an open circuit voltage source Vth "
            "in series with a Thevenin equivalent resistance Rth. When dependent source elements exist, we must turn off all independent sources, "
            "apply an external test voltage source Vx = 1V, and solve for current Ix using nodal MNA to find Rth = Vx / Ix."
        )

        turn_result = test_engine.evaluate_turn_and_adapt(
            session_id=sess_id,
            question_id="VIVA_CKT_01",
            student_answer=strong_answer,
            student_id="2023MITEC042"
        )

        assert turn_result["session_id"] == sess_id
        assert turn_result["turn_number"] == 1
        assert turn_result["score_earned"] >= 8.0
        assert turn_result["max_marks"] == 10.0
        assert turn_result["target_co"] == "CO1"

        # Check Rubric Breakdown
        rubric = turn_result["rubric_breakdown"]
        assert rubric["core_depth"] >= 4.0
        assert rubric["keyword_precision"] >= 2.0
        assert rubric["clarity_and_structure"] == 2.0

        # Check matched concepts
        assert len(turn_result["matched_concepts"]) >= 4

    def test_adaptive_branching_escalates_on_high_score(self, test_engine):
        """Scoring >= 8.0 must adaptively branch to an advanced difficulty question."""
        session = test_engine.start_session(student_id="2023MITEC042", domain="circuit_theorems")
        sess_id = session["session_id"]

        strong_answer = (
            "Thevenin theorem replaces linear networks with Vth and Rth. For dependent source circuits, "
            "apply an external test voltage source Vx and calculate Vx / Ix via nodal analysis."
        )

        turn_result = test_engine.evaluate_turn_and_adapt(
            session_id=sess_id,
            question_id="VIVA_CKT_01",
            student_answer=strong_answer
        )

        next_q = turn_result["next_adaptive_question"]
        assert next_q is not None
        assert next_q["difficulty"] == "ADVANCED"
        assert next_q["question_id"] == "VIVA_CKT_02"
        assert "Modified Nodal Analysis" in next_q["question_text"]

    def test_adaptive_branching_remediates_on_low_score(self, test_engine):
        """Scoring < 6.0 must branch to a foundational diagnostic question."""
        session = test_engine.start_session(student_id="2023MITEC042", domain="semiconductor_physics")
        sess_id = session["session_id"]

        weak_answer = "Fermi level is somewhere in the bandgap."

        turn_result = test_engine.evaluate_turn_and_adapt(
            session_id=sess_id,
            question_id="VIVA_SEMI_02",  # Starting with advanced
            student_answer=weak_answer
        )

        assert turn_result["score_earned"] < 6.0
        next_q = turn_result["next_adaptive_question"]
        assert next_q is not None
        assert next_q["difficulty"] == "FOUNDATIONAL"
        assert next_q["question_id"] == "VIVA_SEMI_01"

    def test_secure_llm_grounding_fallback_without_api_keys(self, test_engine, monkeypatch):
        """When cloud LLM API keys are unset, system must run deterministic fallback securely."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        session = test_engine.start_session(student_id="2023MITEC042", domain="rtl_design")
        turn_result = test_engine.evaluate_turn_and_adapt(
            session_id=session["session_id"],
            question_id="VIVA_RTL_01",
            student_answer="Moore machine outputs depend only on state, whereas Mealy depends on inputs and state."
        )

        assert turn_result["evaluation_mode"] == "DETERMINISTIC_SEMANTIC_FALLBACK"
        assert turn_result["score_earned"] > 0.0
        assert turn_result["model_benchmark_answer"] is not None


class TestObeAttainmentEngine:
    """Verifies Course Outcome and Program Outcome calculations with >= 70% threshold gating."""

    @pytest.fixture
    def sample_assessment_records(self):
        """Sample student assessment records across all 5 Course Outcomes."""
        return [
            # CO1: Circuits (8.5 + 9.0 = 17.5 / 20 = 87.5% -> ATTAINED)
            {"target_co": "CO1", "score_earned": 8.5, "max_marks": 10.0},
            {"target_co": "CO1", "score_earned": 9.0, "max_marks": 10.0},
            # CO2: Devices (7.5 + 8.0 = 15.5 / 20 = 77.5% -> ATTAINED)
            {"target_co": "CO2", "score_earned": 7.5, "max_marks": 10.0},
            {"target_co": "CO2", "score_earned": 8.0, "max_marks": 10.0},
            # CO3: Feedback (8.0 + 7.0 = 15.0 / 20 = 75.0% -> ATTAINED)
            {"target_co": "CO3", "score_earned": 8.0, "max_marks": 10.0},
            {"target_co": "CO3", "score_earned": 7.0, "max_marks": 10.0},
            # CO4: RTL Timing (5.5 + 6.0 = 11.5 / 20 = 57.5% -> ACTION_REQUIRED (< 70%))
            {"target_co": "CO4", "score_earned": 5.5, "max_marks": 10.0},
            {"target_co": "CO4", "score_earned": 6.0, "max_marks": 10.0},
            # CO5: Protocols (9.5 + 9.0 = 18.5 / 20 = 92.5% -> ATTAINED)
            {"target_co": "CO5", "score_earned": 9.5, "max_marks": 10.0},
            {"target_co": "CO5", "score_earned": 9.0, "max_marks": 10.0}
        ]

    def test_co_attainment_calculation_and_gating(self, sample_assessment_records):
        """CO attainment must calculate percentage and enforce the 70% threshold gating."""
        co_att = ObeAttainmentEngine.calculate_co_attainment(sample_assessment_records)

        assert len(co_att) == 5
        assert co_att["CO1"]["attainment_pct"] == 87.5
        assert co_att["CO1"]["status"] == "ATTAINED"
        assert co_att["CO1"]["obe_level"] == 3
        assert co_att["CO1"]["threshold_met"] is True

        assert co_att["CO4"]["attainment_pct"] == 57.5
        assert co_att["CO4"]["status"] == "MARGINAL_ATTAINED"
        assert co_att["CO4"]["obe_level"] == 1
        assert co_att["CO4"]["threshold_met"] is False

        assert co_att["CO5"]["attainment_pct"] == 92.5
        assert co_att["CO5"]["status"] == "ATTAINED"
        assert co_att["CO5"]["obe_level"] == 3

    def test_po_weighted_attainment_mapping(self, sample_assessment_records):
        """PO attainment must calculate weighted averages across all 12 POs and 2 PSOs."""
        co_att = ObeAttainmentEngine.calculate_co_attainment(sample_assessment_records)
        po_att = ObeAttainmentEngine.calculate_po_attainment(co_att)

        assert "PO1" in po_att
        assert "PO2" in po_att
        assert "PO12" in po_att
        assert "PSO1" in po_att
        assert "PSO2" in po_att

        # PO1 is mapped across all COs with weight 3
        # PO1 attainment should be >= 70%
        assert po_att["PO1"]["attainment_pct"] >= 70.0
        assert po_att["PO1"]["status"] == "ATTAINED"
        assert po_att["PO1"]["threshold_met"] is True

    def test_nba_accreditation_report_synthesis(self, sample_assessment_records):
        """Accreditation report must generate institutional summary and exportable markdown matrix."""
        report = ObeAttainmentEngine.generate_nba_accreditation_report(
            sample_assessment_records,
            course_name="Electronics & Embedded Systems Core Series",
            instructor="Ashok Kumar A (2023MITEC042)"
        )

        assert report["institution"] == "Madras Institute of Technology (MIT) Campus, Anna University"
        assert report["threshold_pct"] == 70.0

        summary = report["summary"]
        assert summary["total_cos"] == 5
        assert summary["cos_attained"] == 4  # CO1, CO2, CO3, CO5
        assert summary["co_compliance_rate"] == 80.0
        assert summary["overall_accreditation_verdict"] == "ACCREDITED_TIER_1"

        # Check exportable Markdown table
        md = report["markdown_matrix"]
        assert "| Course Outcome | Direct Score % | NBA Attainment Level | Status | Threshold Gating (>=70%) |" in md
        assert "**CO1**" in md
        assert "✓ PASS" in md
        assert "✗ ACTION" in md


class TestFrontendVivaAndObeIntegration:
    """Verifies that the viva-voce page and simulator hub component are properly constructed."""

    def test_viva_page_structure(self):
        """viva-voce.astro must contain VoltCoreBrandHeader, role badge, breadcrumbs, and hub."""
        page_path = WORKSPACE_ROOT / "src" / "pages" / "viva-voce.astro"
        assert page_path.exists()
        content = page_path.read_text(encoding="utf-8")

        assert "VoltCoreBrandHeader" in content
        assert "ROLE: EXAMINER & SCHOLAR / ORAL ASSESSMENT" in content
        assert "Viva Voce" in content
        assert "VivaVoceSimulatorHub" in content
        assert "aria-label=\"Breadcrumb\"" in content

    def test_viva_hub_component_structure(self):
        """VivaVoceSimulatorHub.jsx must define all 5 ECE domains, rubric evaluation, and OBE tables."""
        hub_path = WORKSPACE_ROOT / "src" / "components" / "VivaVoceSimulatorHub.jsx"
        assert hub_path.exists()
        content = hub_path.read_text(encoding="utf-8")

        assert "circuit_theorems" in content
        assert "semiconductor_physics" in content
        assert "feedback_stability" in content
        assert "rtl_design" in content
        assert "protocol_timing" in content
        assert "SubjectEmblem" in content
        assert "Course Outcome (CO1–CO5) Attainment Matrix" in content
        assert "Export NBA Report" in content
