"""
========================================================================================
VoltCore Apex Academia - Phase 6 Contextual RAG AI Tutor, Code Reviewer & OBE Testbed
Core Engineering Series • Autonomous Engineering Cluster
Platform Lead & Systems Architect: Ashok Kumar A
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313

Validates:
  1. Sublinear TF-IDF VectorRAGIndexer chunking and semantic search across 350+ curriculum sections
  2. Register-focus boosting and hardware citation synthesis (GPIOx_BSRR, DMA_SxCR, etc.)
  3. Embedded C/C++ firmware reviewer:
     - EMB-C-01: Blocking delay inside ISR (HAL_Delay, delay_ms, sleep)
     - EMB-C-02: Shared global variable modified in ISR lacking volatile
     - EMB-C-03: Memory-mapped hardware register pointer cast lacking volatile
     - EMB-C-04: Large local stack buffer hazard (>=256 elements)
  4. Verilog HDL RTL reviewer:
     - HDL-V-01: Blocking assignment '=' in clocked sequential always block
     - HDL-V-02: Non-blocking assignment '<=' in combinational always block
  5. OBE Assessment Grader:
     - Bloom's Taxonomy cognitive distribution (L1-L6)
     - ABET / NBA Program Outcome attainments (PO1-PO5)
     - Viva voce keyword coverage and descriptive solution scoring
  6. SQLite WAL mode persistence (code_review_history, obe_attainment_history, rag_vector_chunks)
  7. HTTP REST endpoints via FallbackHTTPHandler:
     - GET /api/tutor/status
     - POST /api/tutor/rag_query
     - POST /api/tutor/code_review
     - POST /api/tutor/obe_evaluate
  8. Complete decoupling of institutional markers
  9. Laptop thermal safety: execution runtime < 500ms on HP Victus development laptop
========================================================================================
"""

import os
import io
import re
import json
import time
import sqlite3
import tempfile
import pytest

from backend.ai_tutor_engine import (
    VectorRAGChunk,
    VectorRAGIndexer,
    EmbeddedCodeReviewer,
    OBEAssessmentGrader,
    ai_rag_indexer,
    embedded_code_reviewer,
    obe_assessment_grader
)
import attendance_server


FORBIDDEN_INSTITUTIONAL_MARKERS = [
    r"Anna\s+University",
    r"MIT\s+Campus",
    r"Regulation\s+2023",
    r"2023MITEC042"
]


class MockHTTPConnection:
    """Mock socket connection for in-memory HTTP dispatch without network binding."""
    def __init__(self, raw_request_bytes: bytes):
        self.rfile = io.BytesIO(raw_request_bytes)
        self.wfile = io.BytesIO()

    def makefile(self, *args, **kwargs):
        if "r" in args[0]:
            return self.rfile
        return self.wfile

    def sendall(self, b: bytes):
        self.wfile.write(b)


class DummyServer:
    def __init__(self):
        self.server_name = "127.0.0.1"
        self.server_port = 5000


def execute_mock_http_request(method: str, path: str, payload: dict = None):
    """Executes HTTP request through attendance_server.FallbackHTTPHandler without socket port binding."""
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


# ----------------------------------------------------------------------------------------
# 1. RAG INDEXING & SEMANTIC RETRIEVAL TESTS
# ----------------------------------------------------------------------------------------

def test_rag_indexer_curriculum_chunking_and_metadata():
    """Verify that curriculum markdown files are indexed into discrete semantic chunks."""
    assert ai_rag_indexer.is_indexed
    assert ai_rag_indexer.num_docs >= 300, f"Expected >= 300 chunks, found {ai_rag_indexer.num_docs}"
    assert ai_rag_indexer.avg_doc_len > 10.0

    # Verify chunk structure on sample
    sample_chunk = ai_rag_indexer.chunks[0]
    assert isinstance(sample_chunk, VectorRAGChunk)
    assert sample_chunk.category in ("STM32_Academy", "Specialization_Track")
    assert len(sample_chunk.tokens) > 0


def test_rag_search_stm32_bsrr_atomic():
    """Verify sublinear TF-IDF search returns STM32 Module 05 for BSRR atomic queries."""
    results = ai_rag_indexer.search("GPIOx_BSRR atomic bit set reset register", top_k=3)
    assert len(results) > 0

    top_hit = results[0]
    assert "05" in top_hit["module_code"] or "02" in top_hit["module_code"] or "BSRR" in top_hit["section"] or "GPIO" in top_hit["section"] or "BSRR" in top_hit["content"]
    assert top_hit["similarity_score"] > 0.0

    # Test structured synthesis
    synth = ai_rag_indexer.synthesize_response("GPIOx_BSRR atomic bit set reset register")
    assert "Curriculum Retrieval" in synth["answer"]
    assert len(synth["citations"]) > 0
    assert synth["confidence"] > 0.0


def test_rag_search_dma_circular_buffer():
    """Verify search returns DMA module for circular buffer audio/ADC streaming queries."""
    results = ai_rag_indexer.search("DMA circular mode half transfer complete interrupt buffer", top_k=3)
    assert len(results) > 0

    top_hit = results[0]
    assert "12" in top_hit["module_code"] or "DMA" in top_hit["title"] or "DMA" in top_hit["section"]
    assert any("DMA" in r for r in top_hit.get("registers", [])) or "dma" in top_hit["content"].lower()


# ----------------------------------------------------------------------------------------
# 2. EMBEDDED C/C++ CODE REVIEWER RULES
# ----------------------------------------------------------------------------------------

def test_c_reviewer_detects_blocking_delay_in_isr():
    """Rule EMB-C-01: Detect HAL_Delay / delay inside ISR."""
    hazard_code = """
    void TIM2_IRQHandler(void) {
        if (TIM2->SR & TIM_SR_UIF) {
            HAL_Delay(25); // Critical hazard: blocking in ISR
            TIM2->SR = ~TIM_SR_UIF;
        }
    }
    """
    review = embedded_code_reviewer.review(hazard_code, language="c")
    assert not review["is_safe"]
    assert review["critical_count"] >= 1
    assert review["verdict"] == "REJECTED_CRITICAL_HAZARDS"

    rule_ids = [issue["rule_id"] for issue in review["issues"]]
    assert "EMB-C-01" in rule_ids

    issue_01 = [i for i in review["issues"] if i["rule_id"] == "EMB-C-01"][0]
    assert issue_01["severity"] == "CRITICAL"
    assert "HAL_Delay" in issue_01["title"]
    assert "Watchdog" in issue_01["description"]


def test_c_reviewer_detects_unvolatile_shared_isr_variable():
    """Rule EMB-C-02: Detect shared global variable modified in ISR without volatile."""
    hazard_code = """
    uint32_t telemetry_counter = 0; // Lacks volatile

    void EXTI0_IRQHandler(void) {
        telemetry_counter++; // Modified asynchronously in ISR
        EXTI->PR = EXTI_PR_PR0;
    }
    """
    review = embedded_code_reviewer.review(hazard_code, language="c")
    assert not review["is_safe"]
    rule_ids = [issue["rule_id"] for issue in review["issues"]]
    assert "EMB-C-02" in rule_ids

    issue_02 = [i for i in review["issues"] if i["rule_id"] == "EMB-C-02"][0]
    assert "telemetry_counter" in issue_02["title"]
    assert "volatile" in issue_02["fix"]


def test_c_reviewer_detects_register_cast_and_stack_allocation():
    """Rules EMB-C-03 & EMB-C-04: Non-volatile register cast & large stack allocation."""
    code = """
    void setup_gpio(void) {
        uint32_t *pReg = (uint32_t *)0x40020000; // EMB-C-03: lacks volatile
        *pReg |= 0x01;

        char huge_buffer[1024]; // EMB-C-04: large local stack frame
        huge_buffer[0] = 'A';
    }
    """
    review = embedded_code_reviewer.review(code, language="c")
    assert review["warning_count"] >= 2
    rule_ids = [issue["rule_id"] for issue in review["issues"]]
    assert "EMB-C-03" in rule_ids
    assert "EMB-C-04" in rule_ids


def test_c_reviewer_approves_safe_firmware():
    """Verify that correct embedded firmware with volatile and DMA receives APPROVED verdict."""
    clean_code = """
    volatile uint32_t isr_flag = 0;

    void EXTI0_IRQHandler(void) {
        isr_flag = 1;
        EXTI->PR = EXTI_PR_PR0;
    }

    void init_hardware(void) {
        volatile uint32_t *pGPIOB_MODER = (volatile uint32_t *)0x40020400;
        *pGPIOB_MODER |= (1 << 0);
    }
    """
    review = embedded_code_reviewer.review(clean_code, language="c")
    assert review["is_safe"]
    assert review["critical_count"] == 0
    assert review["score"] >= 80.0
    assert review["verdict"] == "APPROVED"


# ----------------------------------------------------------------------------------------
# 3. VERILOG HDL RTL REVIEWER RULES
# ----------------------------------------------------------------------------------------

def test_verilog_reviewer_detects_blocking_in_sequential_logic():
    """Rule HDL-V-01: Detect '=' assignment in always @(posedge clk)."""
    hdl_code = """
    module counter (
        input wire clk,
        input wire rst_n,
        output reg [7:0] count
    );
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            count = 8'h00; // Critical: blocking assignment in sequential
        else
            count = count + 1; // Critical
    end
    endmodule
    """
    review = embedded_code_reviewer.review(hdl_code, language="verilog")
    assert not review["is_safe"]
    assert review["critical_count"] >= 1
    assert review["verdict"] == "REJECTED_CRITICAL_HAZARDS"

    rule_ids = [issue["rule_id"] for issue in review["issues"]]
    assert "HDL-V-01" in rule_ids


def test_verilog_reviewer_detects_nonblocking_in_combinational_logic():
    """Rule HDL-V-02: Detect '<=' assignment in always @(*)."""
    hdl_code = """
    module alu_mux (
        input wire [7:0] a,
        input wire [7:0] b,
        output reg [7:0] out
    );
    always @(*) begin
        out <= a ^ b; // Warning: non-blocking in combinational
    end
    endmodule
    """
    review = embedded_code_reviewer.review(hdl_code, language="verilog")
    assert review["warning_count"] >= 1
    rule_ids = [issue["rule_id"] for issue in review["issues"]]
    assert "HDL-V-02" in rule_ids


# ----------------------------------------------------------------------------------------
# 4. OBE ASSESSMENT GRADER & BLOOM / PO MAPPING
# ----------------------------------------------------------------------------------------

def test_obe_assessment_grader_bloom_and_program_outcomes():
    """Verify quiz score translation into Bloom L1-L6 and ABET PO1-PO5 attainments."""
    quiz_eval = {
        "student_id": "ENG-2024-042",
        "course_code": "STM32_ARM",
        "percentage": 85.0,
        "bloom_performance": {
            "L1 (Remember)": {"total": 4, "correct": 4},
            "L2 (Understand)": {"total": 4, "correct": 4},
            "L3 (Apply)": {"total": 4, "correct": 3},
            "L4 (Analyze)": {"total": 4, "correct": 3},
            "L5 (Evaluate)": {"total": 2, "correct": 1},
            "L6 (Create)": {"total": 2, "correct": 2}
        }
    }
    obe_res = obe_assessment_grader.compute_obe_attainment(quiz_eval, target_threshold_pct=70.0)
    assert obe_res["target_met"] is True
    assert "bloom_taxonomy_attainment" in obe_res
    assert "program_outcomes_attainment" in obe_res

    # PO1 through PO5 mapped
    pos = obe_res["program_outcomes_attainment"]
    assert "PO1" in pos
    assert "PO2" in pos
    assert "PO3" in pos
    assert pos["PO1"]["attainment_pct"] >= 70.0
    assert pos["PO1"]["attained"] is True


def test_obe_viva_descriptive_scoring():
    """Verify technical descriptive solution evaluation with keyword coverage."""
    key_concepts = ["atomic", "bsrr", "single-cycle", "read-modify-write"]
    good_answer = "GPIOx_BSRR performs an atomic single-cycle APB write that eliminates read-modify-write hazards."

    res = obe_assessment_grader.evaluate_descriptive_viva(
        student_answer=good_answer,
        model_answer="BSRR provides atomic single cycle writes.",
        key_concepts=key_concepts,
        max_marks=5
    )
    assert res["score"] >= 4.0
    assert res["percentage"] >= 80.0
    assert "atomic" in res["matched_concepts"]
    assert "bsrr" in res["matched_concepts"]


# ----------------------------------------------------------------------------------------
# 5. SQLITE WAL MODE PERSISTENCE
# ----------------------------------------------------------------------------------------

def test_sqlite_wal_persistence_of_reviews_and_obe():
    """Verify that code reviews and OBE evaluations commit cleanly in WAL mode."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        temp_db_path = tf.name

    try:
        reviewer = EmbeddedCodeReviewer(db_path=temp_db_path)
        sample_review = reviewer.review("void TIM2_IRQHandler(void) { HAL_Delay(10); }", language="c")
        review_id = reviewer.persist_review_to_db("ENG-2024-042", sample_review)
        assert review_id > 0

        grader = OBEAssessmentGrader(db_path=temp_db_path)
        sample_obe = grader.compute_obe_attainment({
            "student_id": "ENG-2024-042",
            "course_code": "STM32_TEST",
            "percentage": 90.0,
            "bloom_performance": {"L1 (Remember)": {"total": 2, "correct": 2}}
        })
        obe_id = grader.persist_obe_to_db(sample_obe)
        assert obe_id > 0

        # Verify SQLite WAL mode PRAGMA
        conn = sqlite3.connect(temp_db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode;")
        mode = cur.fetchone()[0]
        assert mode.lower() == "wal"

        cur.execute("SELECT id, student_id, score FROM code_review_history WHERE id = ?", (review_id,))
        row = cur.fetchone()
        assert row is not None
        assert row[1] == "ENG-2024-042"

        conn.close()
    finally:
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)


# ----------------------------------------------------------------------------------------
# 6. HTTP REST ENDPOINTS DISPATCH
# ----------------------------------------------------------------------------------------

def test_http_tutor_status_endpoint():
    """Verify GET /api/tutor/status returns online status and indexed chunks count."""
    code, data = execute_mock_http_request("GET", "/api/tutor/status")
    assert code == 200
    assert data["status"] == "online"
    assert data["indexed_chunks"] >= 300


def test_http_tutor_rag_query_endpoint():
    """Verify POST /api/tutor/rag_query synthesizes answer with citations."""
    payload = {"query": "STM32 BSRR atomic register", "top_k": 2}
    code, data = execute_mock_http_request("POST", "/api/tutor/rag_query", payload)
    assert code == 200
    assert data["status"] == "success"
    assert "data" in data
    assert "answer" in data["data"]
    assert len(data["data"]["citations"]) > 0


def test_http_tutor_code_review_endpoint():
    """Verify POST /api/tutor/code_review detects ISR hazards via HTTP."""
    payload = {
        "source_code": "void EXTI0_IRQHandler(void) { HAL_Delay(50); }",
        "language": "c",
        "student_id": "ENG-2024-042",
        "persist": True
    }
    code, data = execute_mock_http_request("POST", "/api/tutor/code_review", payload)
    assert code == 200
    assert data["status"] == "success"
    assert data["data"]["critical_count"] >= 1
    assert data["data"]["verdict"] == "REJECTED_CRITICAL_HAZARDS"


def test_http_tutor_obe_evaluate_endpoint():
    """Verify POST /api/tutor/obe_evaluate evaluates both viva and quiz payloads."""
    # 1. Viva Evaluation
    viva_payload = {
        "type": "viva",
        "student_answer": "Writing to BSRR eliminates read-modify-write hazards atomically.",
        "model_answer": "Atomic BSRR writes avoid race conditions.",
        "key_concepts": ["atomic", "bsrr", "read-modify-write"],
        "max_marks": 5
    }
    code_viva, res_viva = execute_mock_http_request("POST", "/api/tutor/obe_evaluate", viva_payload)
    assert code_viva == 200
    assert res_viva["status"] == "success"
    assert res_viva["data"]["score"] >= 3.0

    # 2. Quiz OBE Attainment
    quiz_payload = {
        "type": "quiz",
        "student_id": "ENG-2024-042",
        "course_code": "STM32-EXP",
        "percentage": 82.0,
        "bloom_performance": {
            "L3 (Apply)": {"total": 5, "correct": 4},
            "L4 (Analyze)": {"total": 5, "correct": 4}
        }
    }
    code_quiz, res_quiz = execute_mock_http_request("POST", "/api/tutor/obe_evaluate", quiz_payload)
    assert code_quiz == 200
    assert res_quiz["status"] == "success"
    assert res_quiz["data"]["target_met"] is True


# ----------------------------------------------------------------------------------------
# 7. DECOUPLING & THERMAL SAFETY
# ----------------------------------------------------------------------------------------

def test_institutional_decoupling_and_laptop_thermal_safety():
    """Verify components contain zero forbidden institutional markers and execute under 500ms."""
    start_time = time.perf_counter()

    files_to_check = [
        "src/components/GeminiTutorChat.jsx",
        "src/components/GeminiTutorDrawer.astro",
        "backend/ai_tutor_engine.py"
    ]

    for filepath in files_to_check:
        assert os.path.exists(filepath), f"File {filepath} not found"
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for marker in FORBIDDEN_INSTITUTIONAL_MARKERS:
            matches = re.findall(marker, content, re.IGNORECASE)
            assert not matches, f"Forbidden marker '{marker}' found in {filepath}: {matches}"

    duration_ms = (time.perf_counter() - start_time) * 1000.0
    assert duration_ms < 500.0, f"Check took {duration_ms:.1f}ms, exceeding 500ms limit"
