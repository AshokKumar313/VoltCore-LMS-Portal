"""
========================================================================================
VoltCore Apex Academia - Phase 2 Learning & RAG Engine Test Suite
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase2_learning.py
Platform Lead / Architect: Ashok Kumar A (ashokkumar2008313@gmail.com | +91 9597382878)
GitHub Profile: https://github.com/AshokKumar313 (Username: AshokKumar313)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
Curriculum / Regulation: Department of Electronics Engineering, Regulation 2023
========================================================================================
"""

import os
import sys
import time
import unittest

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.rag_tutor_engine import (
    rag_engine,
    query_rag_knowledge_base,
    MODULES_DIR,
    BM25CurriculumEngine
)
from backend.security_auth import OWNER_METADATA


def test_rag_engine_indexing_capacity():
    """Verify that BM25CurriculumEngine indexes at least 60 semantic chunks from curriculum modules."""
    assert os.path.exists(MODULES_DIR), f"Curriculum modules directory not found: {MODULES_DIR}"
    count = len(rag_engine.chunks)
    assert count >= 60, f"Expected at least 60 indexed chunks, found {count}"


def test_rag_retrieval_and_source_citations():
    """Verify that BM25 search returns relevant results and verified citations for DMA queries."""
    query = "ARM Cortex-M DMA Ping-Pong buffer memory barrier"
    res = query_rag_knowledge_base(query)

    assert res["status"] == "success"
    assert "citations" in res
    assert len(res["citations"]) > 0

    top_cite = res["citations"][0]
    assert "8-advanced-rtos-dma.mdx" in top_cite["source_file"]
    assert top_cite["module_code"] == "EC8708"
    assert top_cite["relevance_score"] > 5.0
    assert "EC8708" in res["response"]


def test_rag_viva_challenge_generation():
    """Verify that Viva Voce mode returns structured oral examination questions with rubrics."""
    res = query_rag_knowledge_base("FreeRTOS Mutex Priority Inversion", mode="viva")

    assert res["status"] == "success"
    assert res["mode"] == "viva"
    assert "viva_challenge" in res

    chal = res["viva_challenge"]
    assert len(chal["questions"]) >= 3
    for q in chal["questions"]:
        assert "question" in q
        assert "rubric" in q
        assert len(q["expected_keywords"]) > 0


def test_module_8_content_and_engineering_trap():
    """Verify that EC8708 Module 8 file exists and contains the Uninitialized DMA Pointer Overwrite trap."""
    mod8_path = os.path.join(MODULES_DIR, "8-advanced-rtos-dma.mdx")
    assert os.path.exists(mod8_path), f"Module 8 missing at {mod8_path}"

    with open(mod8_path, "r", encoding="utf-8") as f:
        text = f.read()

    assert "EC8708" in text
    assert "Uninitialized DMA Ring Buffer Pointer Overwrite" in text
    assert "__DMB()" in text
    assert "__DSB()" in text
    assert "xTaskNotifyIndexedFromISR" in text


def test_sm2_spaced_repetition_algorithm():
    """Verify mathematical correctness of the SuperMemo-2 (SM-2) interval and ease factor formulas."""
    def compute_sm2(repetitions, interval, easeFactor, quality):
        if quality >= 3:
            if repetitions == 0:
                interval = 1
            elif repetitions == 1:
                interval = 6
            else:
                interval = round(interval * easeFactor)
            repetitions += 1
        else:
            repetitions = 0
            interval = 1

        qDiff = 5 - quality
        easeFactor = easeFactor + (0.1 - qDiff * (0.08 + qDiff * 0.02))
        if easeFactor < 1.3:
            easeFactor = 1.3
        return repetitions, interval, round(easeFactor, 2)

    # 1. First perfect recall (quality 5)
    r1, i1, ef1 = compute_sm2(0, 1, 2.5, 5)
    assert r1 == 1
    assert i1 == 1
    assert ef1 == 2.6  # 2.5 + 0.1

    # 2. Second recall (quality 4)
    r2, i2, ef2 = compute_sm2(r1, i1, ef1, 4)
    assert r2 == 2
    assert i2 == 6

    # 3. Third recall (quality 5) -> interval = 6 * 2.6 = 16
    r3, i3, ef3 = compute_sm2(r2, i2, ef2, 5)
    assert r3 == 3
    assert i3 == 16

    # 4. Failed recall (quality 1) resets repetitions to 0 and interval to 1
    r4, i4, ef4 = compute_sm2(r3, i3, ef3, 1)
    assert r4 == 0
    assert i4 == 1
    assert ef4 < ef3


class TestPhase2Learning(unittest.TestCase):
    def test_01_indexing(self):
        test_rag_engine_indexing_capacity()

    def test_02_citations(self):
        test_rag_retrieval_and_source_citations()

    def test_03_viva(self):
        test_rag_viva_challenge_generation()

    def test_04_module_8(self):
        test_module_8_content_and_engineering_trap()

    def test_05_sm2(self):
        test_sm2_spaced_repetition_algorithm()


if __name__ == "__main__":
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    EMERALD = '\033[38;2;0;240;181m'

    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║{RESET} {EMERALD}[VOLTCORE APEX ACADEMIA] PHASE 2 LEARNING & RAG ENGINE TEST SUITE{RESET}        {BOLD}{CYAN}║{RESET}")
    print(f"{BOLD}{CYAN}║{RESET} Lead Architect : {BOLD}Ashok Kumar A{RESET} ({OWNER_METADATA['email']})                    {BOLD}{CYAN}║{RESET}")
    print(f"{BOLD}{CYAN}║{RESET} Institution    : {OWNER_METADATA['institution']} ({OWNER_METADATA['regulation']})           {BOLD}{CYAN}║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════════════════════════════╝{RESET}\n")

    tests = [
        ("Curriculum BM25 Indexing Capacity (>= 60 Chunks)", test_rag_engine_indexing_capacity),
        ("RAG Semantic Retrieval & Verifiable IEEE Citations", test_rag_retrieval_and_source_citations),
        ("Anna University Viva Voce Challenge Generator", test_rag_viva_challenge_generation),
        ("EC8708 Module 8 DMA Architecture & Trap Verification", test_module_8_content_and_engineering_trap),
        ("SuperMemo-2 (SM-2) Interval & Ease Factor Algorithm", test_sm2_spaced_repetition_algorithm),
    ]

    passed = 0
    failed = 0
    for name, func in tests:
        t0 = time.time()
        try:
            func()
            elapsed_ms = (time.time() - t0) * 1000
            print(f"  {GREEN}✓ [PASS]{RESET} {BOLD}{name:<58}{RESET} {YELLOW}({elapsed_ms:.1f}ms){RESET}")
            passed += 1
        except Exception as e:
            elapsed_ms = (time.time() - t0) * 1000
            print(f"  {RED}✗ [FAIL]{RESET} {BOLD}{name:<58}{RESET} {RED}Error: {e}{RESET}")
            failed += 1

    print(f"\n{BOLD}{CYAN}──────────────────────────────────────────────────────────────────────────────────{RESET}")
    if failed == 0:
        print(f"  {BOLD}{GREEN}ALL {passed} PHASE 2 TEST SPECIFICATIONS PASSED (100% SUCCESS RATE){RESET}\n")
    else:
        print(f"  {BOLD}{RED}{failed} TESTS FAILED{RESET}\n")
        sys.exit(1)

