"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 3 Academic Quality & Zero-Stub Verification
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase3_academic_quality_zero_stub.py
Platform Lead & System Architect: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Verifies:
  1. Zero-Stub Content Integrity across all 15 ECE disciplines
  2. Mathematical Derivations & LaTeX Formulations with Parameter Tables
  3. Step-by-Step Worked Engineering Examples with Verified Output
  4. Simulation Activity Bindings & Interactive Telemetry Benchmarks
  5. Bloom's Taxonomy Cognitive Rubrics & Assessment Questions (CO1-CO5)
  6. Prerequisite DAG Topological Sort & Remedial Pathway Micro-Lesson Generation
  7. Outcome-Based Education (OBE) CO-PO Attainment Calculation & NBA Threshold Gating
  8. Academic Rigor & Syllabus Contact Hour Compliance
========================================================================================
"""

import os
import sys
import json
import pytest
from typing import Dict, Any, List

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.course_config_engine import CourseConfigEngine, COURSE_REGISTRY_DATA
from backend.ece_comprehensive_curriculum import COMPREHENSIVE_ECE_CURRICULUM
from backend.learning_pathway_engine import LearningPathwayEngine, ACADEMIC_PATHWAYS
from backend.viva_voce_simulator_engine import ObeAttainmentEngine, VivaVoceSimulatorEngine


# ========================================================================================
# 1. ZERO-STUB CONTENT INTEGRITY & ACADEMIC RIGOR VERIFICATION
# ========================================================================================
class TestPhase3CurriculumZeroStubIntegrity:
    """Verifies that every ECE course meets complete zero-stub academic rigor standards."""

    ALL_15_DISCIPLINES = [
        "EC23C01",  # Circuit Analysis & Network Theory
        "EC23C02",  # Semiconductor Physics & Solid-State Devices
        "EC23C03",  # Electronic Devices & Circuit Modeling
        "EC23C04",  # Signals & Linear Systems
        "EC23C05",  # Analog Electronics & Linear ICs
        "EC23C06",  # Digital Electronics & Switching Theory
        "EC23C07",  # Control Systems Engineering
        "EC23C08",  # Analog & Digital Communication Systems
        "EC23S01",  # Digital Signal Processing & Algorithms
        "EC23E04",  # Optics, Lasers & Optical Communication
        "EC8702",   # Embedded Systems & ARM Architecture
        "STM32-ACADEMY",  # STM32 Bare-Metal & FreeRTOS
        "IOT8701",  # ESP32 IoT Edge Node
        "HDL6001",  # Verilog HDL & FPGA Digital Design
        "VLSI7001", # VLSI Physical Design & ASIC Architecture
    ]

    @pytest.fixture
    def engine(self):
        return CourseConfigEngine()

    def test_all_15_disciplines_present_in_both_registries(self, engine):
        """All 15 disciplines must exist in both COMPREHENSIVE_ECE_CURRICULUM and CourseConfigEngine."""
        registered_codes = set(c["code"] for c in engine.list_all_courses())
        comprehensive_codes = set(COMPREHENSIVE_ECE_CURRICULUM.keys())

        for code in self.ALL_15_DISCIPLINES:
            assert code in registered_codes, f"Discipline {code} missing from CourseConfigEngine!"
            assert code in comprehensive_codes, f"Discipline {code} missing from COMPREHENSIVE_ECE_CURRICULUM!"

    def test_zero_placeholder_stubs_in_all_courses(self, engine):
        """Zero placeholder stubs ('TODO', 'TBD', 'Coming Soon', etc.) across all 15 courses."""
        forbidden_stubs = ["TODO", "TBD", "Coming Soon", "Under Construction", "Lorem ipsum", "Placeholder"]
        for code in self.ALL_15_DISCIPLINES:
            course = engine.get_course(code)
            assert course is not None, f"Course {code} not found"
            serialized = json.dumps(course)
            for stub in forbidden_stubs:
                assert stub not in serialized, f"Course {code} contains forbidden stub '{stub}'!"

    def test_course_outcomes_co1_to_co5_rigor(self, engine):
        """Every course must specify at least 5 Course Outcomes with Bloom levels L1-L6, POs, and PSOs."""
        for code in self.ALL_15_DISCIPLINES:
            course = engine.get_course(code)
            cos = course.get("course_outcomes", [])
            assert len(cos) >= 5, f"{code} must have at least 5 Course Outcomes"

            co_ids = [co["id"] for co in cos]
            for i in range(1, 6):
                assert f"CO{i}" in co_ids, f"{code} missing CO{i}"

            for co in cos:
                assert "id" in co
                assert "description" in co and len(co["description"]) > 25
                assert "bloom_level" in co
                assert any(lvl in co["bloom_level"] for lvl in ["L1", "L2", "L3", "L4", "L5", "L6"])
                assert "mapped_pos" in co and len(co["mapped_pos"]) >= 1
                assert "mapped_psos" in co and len(co["mapped_psos"]) >= 1

    def test_mathematical_derivations_complete_for_all_courses(self, engine):
        """Every course must have rigorous mathematical derivations with valid LaTeX formulas."""
        for code in self.ALL_15_DISCIPLINES:
            course = engine.get_course(code)
            derivations = course.get("mathematical_derivations", [])
            assert len(derivations) >= 1, f"{code} missing mathematical derivations"

            for d in derivations:
                assert "topic" in d and len(d["topic"]) > 10
                assert "formula_latex" in d and len(d["formula_latex"]) > 5
                assert "derivation_steps" in d and len(d["derivation_steps"]) >= 3
                assert "parameters" in d and len(d["parameters"]) >= 2
                for p in d["parameters"]:
                    assert "symbol" in p
                    assert "unit" in p
                    assert "definition" in p

    def test_worked_examples_complete_for_all_courses(self, engine):
        """Every course must contain verified engineering worked examples with step-by-step math."""
        for code in self.ALL_15_DISCIPLINES:
            course = engine.get_course(code)
            examples = course.get("worked_examples", [])
            assert len(examples) >= 1, f"{code} missing worked examples"

            for ex in examples:
                assert "title" in ex and len(ex["title"]) > 10
                assert "problem_statement" in ex and len(ex["problem_statement"]) > 25
                assert "step_by_step_solution" in ex and len(ex["step_by_step_solution"]) >= 3
                assert "verified_output" in ex and len(ex["verified_output"]) > 5

    def test_simulation_activities_complete_for_all_courses(self, engine):
        """Every course must bind to an interactive React workbench with expected telemetry."""
        valid_components = {
            "MnaAnalogWorkbench", "VirtualOscilloscope", "SemiconductorPhysicsWorkbench",
            "DigitalElectronicsHub", "MathStudioHub", "RfSmithChartHub", "Stm32AcademySimulator",
            "IoTSensorSimulatorHub", "FpgaSynthesisHub", "VlsiPhysicalDesignHub",
            "DiodeMosfetIvCurveTracer", "DmaNvicHub", "PythonSciPy"
        }
        for code in self.ALL_15_DISCIPLINES:
            course = engine.get_course(code)
            sims = course.get("simulation_activities", [])
            assert len(sims) >= 1, f"{code} missing simulation activities"

            for sim in sims:
                assert "lab_id" in sim and len(sim["lab_id"]) > 3
                assert "title" in sim and len(sim["title"]) > 10
                assert "component" in sim and sim["component"] in valid_components
                assert "instructions" in sim and len(sim["instructions"]) > 25
                assert "expected_telemetry" in sim and len(sim["expected_telemetry"]) >= 1

    def test_assessment_questions_complete_for_all_courses(self, engine):
        """Every course must have structured assessment questions with 4 options and Bloom level."""
        for code in self.ALL_15_DISCIPLINES:
            course = engine.get_course(code)
            questions = course.get("assessment_questions", [])
            assert len(questions) >= 1, f"{code} missing assessment questions"

            for q in questions:
                assert "id" in q
                assert "bloom_level" in q
                assert "question" in q and len(q["question"]) > 15
                assert "options" in q and len(q["options"]) == 4
                assert 0 <= q["correct_index"] <= 3
                assert "explanation" in q and len(q["explanation"]) > 25

    def test_academic_rigor_and_contact_hours_compliance_all_15_courses(self, engine):
        """All 15 courses must satisfy contact hours and Bloom's Taxonomy L3-L6 rigor."""
        for code in self.ALL_15_DISCIPLINES:
            rigor = engine.audit_academic_rigor(code)
            assert rigor["is_hour_compliant"] is True, f"{code} failed contact hour compliance: {rigor}"
            assert rigor["nba_tier1_aligned"] is True, f"{code} not NBA Tier 1 aligned"
            assert "L3-L6" in rigor["obe_blooms_rigor"], f"{code} missing higher-order Bloom's rigor"


# ========================================================================================
# 2. PREREQUISITE DAG & REMEDIAL PATHWAY VERIFICATION
# ========================================================================================
class TestPhase3PrerequisiteDagAndPathways:
    """Verifies topological sorting and remedial dispatching across learning pathways."""

    @pytest.fixture
    def pathway_engine(self):
        return LearningPathwayEngine()

    @pytest.fixture
    def course_engine(self):
        return CourseConfigEngine()

    def test_all_five_pathways_registered_and_structured(self, pathway_engine):
        """All 5 official academic pathways must be registered with correct credit weights."""
        expected_pathways = [
            "pathway_semiconductor",
            "pathway_embedded",
            "pathway_dsp_telecom",
            "pathway_vlsi",
            "pathway_ai_hardware"
        ]
        all_pathways = pathway_engine.list_all_pathways()
        registered_ids = [p["id"] for p in all_pathways]

        for pid in expected_pathways:
            assert pid in registered_ids
            pathway = pathway_engine.get_pathway(pid)
            assert pathway is not None
            assert len(pathway["nodes"]) >= 3
            assert pathway["total_credits"] >= 12

    def test_topological_sort_all_five_pathways(self, pathway_engine):
        """Topological sorting must succeed without cycles on all 5 academic pathways."""
        for pid in pathway_engine.pathways.keys():
            sorted_nodes = pathway_engine.topological_sort_pathway(pid)
            assert len(sorted_nodes) == len(pathway_engine.pathways[pid]["nodes"])
            # Verify order respects prerequisites
            visited = set()
            for node_code in sorted_nodes:
                node_data = next(n for n in pathway_engine.pathways[pid]["nodes"] if n["code"] == node_code)
                for prereq in node_data.get("prerequisites", []):
                    assert prereq in visited, f"In pathway {pid}, {prereq} must precede {node_code}!"
                visited.add(node_code)

    def test_course_engine_prerequisite_dag_acyclicity(self, course_engine):
        """CourseConfigEngine prerequisite DAG resolution must verify acyclicity for all courses."""
        for course in course_engine.list_all_courses():
            code = course["code"]
            dag_res = course_engine.resolve_prerequisite_dag(code)
            assert dag_res["is_valid_dag"] is True, f"Prerequisite cycle detected for {code}!"
            assert dag_res["has_cycle"] is False

    def test_remedial_micro_lesson_generation_on_low_score(self, pathway_engine):
        """Telemetry score < 70% must dispatch targeted remedial micro-lesson with root prerequisite."""
        remedial = pathway_engine.generate_remedial_micro_lesson(
            target_concept="Elmore_Delay",
            telemetry_score=54.0,
            student_id="2023MITEC042"
        )
        assert remedial["requires_remediation"] is True
        assert remedial["status"] == "REMEDIAL_DISPATCHED"
        assert remedial["root_prerequisite"] == "RC_Time_Constants"
        assert remedial["discipline_origin"] == "EC23C01"
        assert "mathematical_formula" in remedial and len(remedial["mathematical_formula"]) > 5
        assert "diagnostic_task" in remedial
        assert remedial["mastery_threshold_to_unlock"] == 75.0

    def test_remedial_micro_lesson_bypass_on_high_score(self, pathway_engine):
        """Telemetry score >= 70% must confirm mastery without requiring remediation."""
        remedial = pathway_engine.generate_remedial_micro_lesson(
            target_concept="Elmore_Delay",
            telemetry_score=88.5,
            student_id="2023MITEC042"
        )
        assert remedial["requires_remediation"] is False
        assert remedial["status"] == "MASTERY_SATISFIED"


# ========================================================================================
# 3. OUTCOME-BASED EDUCATION (OBE) & CO-PO ATTAINMENT VERIFICATION
# ========================================================================================
class TestPhase3ObeAttainmentVerification:
    """Verifies direct CO/PO attainment calculations against NBA Tier 1 standards."""

    def test_co_attainment_calculation_against_nba_levels(self):
        """CO attainment must calculate percentage and map to NBA 0-3 levels."""
        assessment_records = [
            {"target_co": "CO1", "score_earned": 9.0, "max_marks": 10.0},
            {"target_co": "CO1", "score_earned": 8.0, "max_marks": 10.0},
            {"target_co": "CO2", "score_earned": 6.5, "max_marks": 10.0},
            {"target_co": "CO3", "score_earned": 5.5, "max_marks": 10.0},
            {"target_co": "CO4", "score_earned": 4.0, "max_marks": 10.0},
            {"target_co": "CO5", "score_earned": 8.5, "max_marks": 10.0},
        ]
        attainment = ObeAttainmentEngine.calculate_co_attainment(assessment_records)

        # CO1: 17/20 = 85.0% -> Level 3 (ATTAINED)
        assert attainment["CO1"]["attainment_pct"] == 85.0
        assert attainment["CO1"]["obe_level"] == 3
        assert attainment["CO1"]["status"] == "ATTAINED"
        assert attainment["CO1"]["threshold_met"] is True

        # CO2: 6.5/10 = 65.0% -> Level 2 (PARTIAL_ATTAINED)
        assert attainment["CO2"]["attainment_pct"] == 65.0
        assert attainment["CO2"]["obe_level"] == 2
        assert attainment["CO2"]["status"] == "PARTIAL_ATTAINED"

        # CO3: 5.5/10 = 55.0% -> Level 1 (MARGINAL_ATTAINED)
        assert attainment["CO3"]["attainment_pct"] == 55.0
        assert attainment["CO3"]["obe_level"] == 1
        assert attainment["CO3"]["status"] == "MARGINAL_ATTAINED"

        # CO4: 4.0/10 = 40.0% -> Level 0 (ACTION_REQUIRED)
        assert attainment["CO4"]["attainment_pct"] == 40.0
        assert attainment["CO4"]["obe_level"] == 0
        assert attainment["CO4"]["status"] == "ACTION_REQUIRED"

    def test_po_weighted_mapping_matrices(self):
        """PO weighted mapping averages must properly reflect mapped CO values."""
        co_attainment = {
            "CO1": {"attainment_pct": 80.0},
            "CO2": {"attainment_pct": 75.0},
            "CO3": {"attainment_pct": 70.0},
            "CO4": {"attainment_pct": 65.0},
            "CO5": {"attainment_pct": 85.0},
        }
        po_results = ObeAttainmentEngine.calculate_po_attainment(co_attainment)

        assert "PO1" in po_results
        assert "PO2" in po_results
        assert "PSO1" in po_results
        assert po_results["PO1"]["attainment_pct"] > 70.0
        assert po_results["PO1"]["obe_level"] > 2.0
        assert po_results["PSO1"]["threshold_met"] is True
        assert po_results["PSO1"]["status"] == "ATTAINED"
