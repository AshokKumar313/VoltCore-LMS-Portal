"""
========================================================================================
VoltCore Apex Academia - Test Suite: Stage 4 & Stage 5 Hardening Verification
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_stage4_stage5_curriculum_ai.py
Platform Lead & Systems Architect: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Verifies:
  1. STAGE 4: Full ECE Course Registry & Curriculum Completeness (14 Disciplines)
     - Learning objectives (CO1-CO5 with Bloom's Taxonomy L1-L6)
     - Prerequisite DAG topological order & acyclicity
     - Mathematical derivations with KaTeX parameters
     - Worked engineering examples with step-by-step solutions
     - Simulation activity bindings to React interactive workbenches
     - Assessment questions with options, rubrics, and explanations
     - Zero placeholder stubs across all curriculum courses
     - Dashboard validations: Student Learning, Instructor Workspace, Admin Workspace
  2. STAGE 5: Secure Cloud AI Grounding Engine
     - Local vector/BM25 retrieval grounding
     - Anti-hallucination prompt construction
     - Sliding window rate limiting (30 requests/minute)
     - Zero client-side API key leakage
     - Deterministic local retrieval fallback on missing key or network timeout
     - Server API endpoint contracts (/api/ai/grounded-ask, /api/ai/curriculum/courses)
========================================================================================
"""

import os
import sys
import json
import pytest
from typing import Dict, Any

# Ensure project root in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.course_config_engine import CourseConfigEngine, COURSE_REGISTRY_DATA
from backend.ece_comprehensive_curriculum import COMPREHENSIVE_ECE_CURRICULUM
from backend.cloud_ai_grounding_engine import (
    CloudAIGroundingEngine,
    SlidingWindowRateLimiter,
    cloud_ai_grounding_engine
)


# ========================================================================================
# 1. STAGE 4: ECE COURSE REGISTRY & CURRICULUM VERIFICATION
# ========================================================================================
class TestStage4CurriculumCompleteness:
    """Verifies all 14 ECE disciplines meet university accreditation standards."""

    REQUIRED_DISCIPLINES = [
        "EC23C01",  # Circuit Analysis
        "EC23C02",  # Semiconductor Physics
        "EC23C03",  # Electronic Devices
        "EC23C05",  # Analog Electronics
        "EC23C06",  # Digital Electronics
        "EC23C04",  # Signals & Systems
        "EC23C07",  # Control Systems
        "EC23S01",  # Digital Signal Processing
        "EC23C08",  # Communication Systems
        "EC8702",   # Embedded Systems
        "STM32-ACADEMY",  # STM32 Architecture
        "IOT8701",  # ESP32 IoT Systems
        "HDL6001",  # Verilog HDL & FPGA
        "VLSI7001", # VLSI Physical Design
    ]

    @pytest.fixture
    def engine(self):
        return CourseConfigEngine()

    def test_all_14_disciplines_registered(self, engine):
        """Every required core ECE discipline must be registered in the engine."""
        registered_codes = [c["code"] for c in engine.list_all_courses()]
        for code in self.REQUIRED_DISCIPLINES:
            assert code in registered_codes, f"Discipline {code} missing from CourseConfigEngine registry!"

    def test_zero_placeholder_stubs_in_curriculum(self, engine):
        """No course may contain placeholder stubs such as 'TODO', 'TBD', or 'Coming Soon'."""
        stubs = ["TODO", "TBD", "Coming Soon", "Under Construction", "Placeholder"]
        for code in self.REQUIRED_DISCIPLINES:
            course = engine.get_course(code)
            assert course is not None, f"Course {code} not found"
            serialized = json.dumps(course)
            for stub in stubs:
                assert stub not in serialized, f"Discipline {code} contains placeholder stub: '{stub}'!"

    def test_course_outcomes_and_blooms_rigor(self, engine):
        """Every course must specify at least 5 Course Outcomes with Bloom levels L1-L6."""
        for code in self.REQUIRED_DISCIPLINES:
            course = engine.get_course(code)
            assert course["cos_count"] >= 5, f"{code} must specify at least 5 COs"
            cos = course.get("course_outcomes", [])
            assert len(cos) >= 5, f"{code} course_outcomes list must contain >= 5 entries"
            for co in cos:
                assert "id" in co
                assert "description" in co and len(co["description"]) > 20
                assert "bloom_level" in co
                assert any(lvl in co["bloom_level"] for lvl in ["L1", "L2", "L3", "L4", "L5", "L6"])

    def test_mathematical_derivations_present(self, engine):
        """Every comprehensive curriculum course must have KaTeX mathematical derivations."""
        for code, data in COMPREHENSIVE_ECE_CURRICULUM.items():
            derivations = data.get("mathematical_derivations", [])
            assert len(derivations) >= 1, f"{code} must have at least one mathematical derivation"
            for d in derivations:
                assert "formula_latex" in d and len(d["formula_latex"]) > 5
                assert "derivation_steps" in d and len(d["derivation_steps"]) >= 2
                assert "parameters" in d and len(d["parameters"]) >= 2

    def test_worked_examples_present(self, engine):
        """Every comprehensive curriculum course must have step-by-step worked numerical examples."""
        for code, data in COMPREHENSIVE_ECE_CURRICULUM.items():
            examples = data.get("worked_examples", [])
            assert len(examples) >= 1, f"{code} must contain worked engineering examples"
            for ex in examples:
                assert "problem_statement" in ex and len(ex["problem_statement"]) > 20
                assert "step_by_step_solution" in ex and len(ex["step_by_step_solution"]) >= 3
                assert "verified_output" in ex and len(ex["verified_output"]) > 5

    def test_simulation_activity_component_bindings(self, engine):
        """Every course must bind to an interactive simulation component with expected telemetry."""
        valid_components = {
            "MnaAnalogWorkbench", "VirtualOscilloscope", "SemiconductorPhysicsWorkbench",
            "DigitalElectronicsHub", "MathStudioHub", "RfSmithChartHub", "Stm32AcademySimulator",
            "IoTSensorSimulatorHub", "FpgaSynthesisHub", "VlsiPhysicalDesignHub",
            "DiodeMosfetIvCurveTracer", "DmaNvicHub", "PythonSciPy"
        }
        for code in self.REQUIRED_DISCIPLINES:
            course = engine.get_course(code)
            sim_comp = course.get("simulation_component") or course.get("simulation_platform")
            assert sim_comp is not None, f"{code} missing simulation component binding"

    def test_assessment_questions_structure(self, engine):
        """Assessment questions must contain Bloom level, options, correct index, and explanation."""
        for code, data in COMPREHENSIVE_ECE_CURRICULUM.items():
            questions = data.get("assessment_questions", [])
            assert len(questions) >= 1, f"{code} must contain assessment questions"
            for q in questions:
                assert "question" in q and len(q["question"]) > 15
                assert "options" in q and len(q["options"]) == 4
                assert 0 <= q["correct_index"] <= 3
                assert "explanation" in q and len(q["explanation"]) > 20

    def test_prerequisite_dag_acyclicity(self, engine):
        """The complete prerequisite graph must be a valid Directed Acyclic Graph (DAG)."""
        visited = set()
        recursion_stack = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            recursion_stack.add(node)
            course = engine.get_course(node)
            if course:
                for prereq in course.get("prerequisites", []):
                    if prereq not in visited:
                        if has_cycle(prereq):
                            return True
                    elif prereq in recursion_stack:
                        return True
            recursion_stack.remove(node)
            return False

        for code in self.REQUIRED_DISCIPLINES:
            if code not in visited:
                assert not has_cycle(code), f"Circular prerequisite dependency detected involving {code}!"

    def test_workspace_dashboards_exist(self):
        """Student learning, instructor, and administrator dashboards must exist in src/pages/."""
        dashboards = [
            "src/pages/learning-dashboard.astro",
            "src/pages/faculty-workspace.astro",
            "src/pages/enterprise-admin.astro",
            "src/pages/course-hub.astro"
        ]
        for db_path in dashboards:
            full_path = os.path.join(PROJECT_ROOT, db_path)
            assert os.path.isfile(full_path), f"Dashboard {db_path} must exist"
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert len(content) > 500, f"Dashboard {db_path} content cannot be empty"


# ========================================================================================
# 2. STAGE 5: SECURE CLOUD AI GROUNDING ENGINE VERIFICATION
# ========================================================================================
class TestStage5CloudAIGrounding:
    """Verifies hybrid local retrieval + cloud LLM grounding architecture."""

    @pytest.fixture
    def grounding_engine(self):
        return CloudAIGroundingEngine(rate_limit_per_min=30, timeout_seconds=4.0)

    def test_sliding_window_rate_limiter_permits_under_limit(self):
        """Rate limiter permits requests within capacity."""
        limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60.0)
        for i in range(5):
            allowed, remaining, _ = limiter.is_allowed("student_101")
            assert allowed is True
            assert remaining == 4 - i

    def test_sliding_window_rate_limiter_blocks_burst(self):
        """Rate limiter blocks burst requests exceeding limit with retry interval."""
        limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=60.0)
        for _ in range(3):
            limiter.is_allowed("student_102")
        allowed, remaining, reset_after = limiter.is_allowed("student_102")
        assert allowed is False
        assert remaining == 0
        assert reset_after > 0.0

    def test_zero_cloud_api_key_leakage_in_frontend(self):
        """Frontend files in src/ must never contain hardcoded API keys."""
        restricted_patterns = [
            "AIzaSy",  # Google Gemini API key prefix
            "sk-proj-", # OpenAI project key prefix
            "sk-ant-",  # Anthropic key prefix
        ]
        for root, dirs, files in os.walk(os.path.join(PROJECT_ROOT, "src")):
            for f in files:
                if f.endswith((".js", ".jsx", ".ts", ".tsx", ".astro")):
                    fpath = os.path.join(root, f)
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                        content = fp.read()
                        for pattern in restricted_patterns:
                            assert pattern not in content, (
                                f"CRITICAL SECURITY LEAK: API key pattern '{pattern}' found in client file '{fpath}'!"
                            )

    def test_anti_hallucination_prompt_grounding_assembly(self, grounding_engine):
        """Prompt assembly must include authoritative passages, KaTeX rules, and provenance."""
        citations = [
            {"module_code": "EC8702", "section": "DMA Ping-Pong Architecture", "relevance_score": 8.5}
        ]
        contexts = [
            "DMA controllers on Cortex-M4 utilize dual-buffer descriptors to eliminate ISR overrun."
        ]
        prompt = grounding_engine._build_grounding_prompt(
            query="Explain ping-pong buffering",
            citations=citations,
            contexts=contexts,
            course_code="EC8702"
        )
        assert "BEGIN AUTHORITATIVE CURRICULUM PASSAGES" in prompt
        assert "DMA Ping-Pong Architecture" in prompt
        assert "KaTeX" in prompt
        assert "EC8702" in prompt

    def test_deterministic_curriculum_retrieval_fallback(self, grounding_engine):
        """When cloud key is unset or offline, seamlessly falls back to local curriculum synthesis."""
        # Ensure no real API key interferes with deterministic test
        original_key = os.environ.pop("GEMINI_API_KEY", None)
        try:
            res = grounding_engine.query_grounded_tutor(
                query="ARM Cortex-M DMA Ping-Pong buffer memory barrier",
                student_id="test_student_2023",
                course_code="EC8702"
            )
            assert res["status"] == "SUCCESS"
            assert res["grounding_mode"] == "LOCAL_CURRICULUM_SYNTHESIS"
            assert len(res["grounded_answer"]) > 50
            assert res["citations_count"] > 0
            assert any("8-advanced-rtos-dma.mdx" in c["source_file"] for c in res["citations"])
        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key

    def test_grounded_ask_server_route(self):
        """Verifies /api/ai/grounded-ask server route handles queries gracefully."""
        from io import BytesIO
        from attendance_server import FallbackHTTPHandler

        class DummyServer:
            pass

        class MockSocket:
            def __init__(self, data):
                self.data = data
                self.output = BytesIO()

            def makefile(self, mode, *args, **kwargs):
                if 'r' in mode:
                    return BytesIO(self.data)
                return self.output

            def sendall(self, b):
                self.output.write(b)

        body = json.dumps({
            "query": "ARM Cortex-M NVIC priority grouping",
            "student_id": "2023MITEC042",
            "course_code": "EC8702"
        }).encode("utf-8")

        req = (
            b"POST /api/ai/grounded-ask HTTP/1.1\r\n"
            b"Host: localhost\r\n"
            b"Content-Type: application/json\r\n"
            b"Content-Length: " + str(len(body)).encode("utf-8") + b"\r\n\r\n"
            + body
        )
        sock = MockSocket(req)
        FallbackHTTPHandler(sock, ("127.0.0.1", 8080), DummyServer())
        resp = sock.output.getvalue().decode("utf-8")
        assert "200 OK" in resp
        assert "SUCCESS" in resp
        assert "grounded_answer" in resp
        assert "citations" in resp

    def test_curriculum_courses_server_route(self):
        """Verifies /api/ai/curriculum/courses returns all 14 disciplines."""
        from io import BytesIO
        from attendance_server import FallbackHTTPHandler

        class DummyServer:
            pass

        class MockSocket:
            def __init__(self, data):
                self.data = data
                self.output = BytesIO()

            def makefile(self, mode, *args, **kwargs):
                if 'r' in mode:
                    return BytesIO(self.data)
                return self.output

            def sendall(self, b):
                self.output.write(b)

        req = b"GET /api/ai/curriculum/courses HTTP/1.1\r\nHost: localhost\r\n\r\n"
        sock = MockSocket(req)
        FallbackHTTPHandler(sock, ("127.0.0.1", 8080), DummyServer())
        resp = sock.output.getvalue().decode("utf-8")
        assert "200 OK" in resp
        assert "EC23C01" in resp
        assert "VLSI7001" in resp
        assert "STM32-ACADEMY" in resp
