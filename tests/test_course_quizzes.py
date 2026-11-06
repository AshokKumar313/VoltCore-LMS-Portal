"""
========================================================================================
VoltCore Apex Academia - Unit Tests for Academic Quizzes & Automated Assessment
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead & Systems Architect: Ashok Kumar A
========================================================================================
"""

import pytest
import tempfile
import os
from backend.course_quiz_engine import CourseQuizEngine, COURSE_QUIZ_CATALOG


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
def quiz_engine(temp_db):
    return CourseQuizEngine(db_path=temp_db)


def test_catalog_validation(quiz_engine):
    """Verify that all questions across all priority courses pass schema validation."""
    audit = quiz_engine.validate_catalog()
    assert audit["valid"] is True, f"Validation errors: {audit.get('errors')}"
    assert len(audit["errors"]) == 0
    assert audit["total_courses"] == 4
    assert audit["total_questions"] >= 16


def test_all_courses_have_questions(quiz_engine):
    """Verify each priority course has MCQs, Part A, and Part B questions."""
    required_courses = ["EC23S01", "EC23C03", "EC23E04", "EC8702"]
    for code in required_courses:
        catalog = quiz_engine.get_catalog_for_course(code)
        assert len(catalog) >= 4, f"Course {code} must have at least 4 assessment items"
        
        types = {q["type"] for q in catalog}
        assert "MCQ" in types, f"Course {code} missing MCQ"
        assert "PART_A" in types, f"Course {code} missing Part A"
        assert "PART_B" in types, f"Course {code} missing Part B"


def test_mcq_structure(quiz_engine):
    """Verify all MCQ questions have exactly 4 choices and a valid correct option index."""
    for code, questions in COURSE_QUIZ_CATALOG.items():
        for q in questions:
            if q["type"] == "MCQ":
                assert "options" in q
                assert len(q["options"]) == 4, f"{q['id']} must have 4 options"
                assert 0 <= q["correctOptionIndex"] <= 3, f"{q['id']} has invalid correct option index"
                assert q["marks"] == 1


def test_part_a_and_part_b_marks(quiz_engine):
    """Verify Anna University Regulation 2023 mark distribution (Part A: 2 marks, Part B: 16 marks)."""
    for code, questions in COURSE_QUIZ_CATALOG.items():
        for q in questions:
            if q["type"] == "PART_A":
                assert q["marks"] == 2, f"{q['id']} Part A should be 2 marks"
            elif q["type"] == "PART_B":
                assert q["marks"] == 16, f"{q['id']} Part B should be 16 marks"


def test_explanations_and_katex(quiz_engine):
    """Verify each question has pedagogical explanations, KaTeX formulas, and pitfall alerts."""
    for code, questions in COURSE_QUIZ_CATALOG.items():
        for q in questions:
            assert len(q["stepByStepExplanation"]) >= 2, f"{q['id']} needs step-by-step breakdown"
            assert len(q["keyFormulas"]) >= 1, f"{q['id']} needs KaTeX formulas"
            assert len(q["commonPitfall"]) > 0, f"{q['id']} needs common pitfall warning"
            assert len(q["examYearReference"]) > 0, f"{q['id']} needs exam year reference"


def test_evaluation_perfect_score(quiz_engine):
    """Test evaluating student submission with 100% correct answers."""
    answers = {
        "EC23S01_Q1": 2,
        "EC23S01_Q2": 1
    }
    result = quiz_engine.evaluate_submission("EC23S01", "2023MITEC042", answers)
    assert result["course_code"] == "EC23S01"
    assert result["student_id"] == "2023MITEC042"
    assert result["correct_count"] == 2
    assert result["total_mcqs"] == 2
    assert result["percentage"] == 100.0


def test_evaluation_partial_score(quiz_engine):
    """Test evaluating student submission with mixed correct and incorrect answers."""
    answers = {
        "EC23C03_Q1": 1, # correct
        "EC23C03_Q2": 0  # incorrect (correct is 1)
    }
    result = quiz_engine.evaluate_submission("EC23C03", "2023MITEC042", answers)
    assert result["course_code"] == "EC23C03"
    assert result["correct_count"] == 1
    assert result["total_mcqs"] == 2
    assert result["percentage"] == 50.0


def test_bloom_attainment_tracking(quiz_engine):
    """Verify Bloom's Taxonomy tracking in evaluation output."""
    answers = {
        "EC8702_Q1": 1,
        "EC8702_Q2": 1
    }
    result = quiz_engine.evaluate_submission("EC8702", "2023MITEC042", answers)
    bloom_perf = result["bloom_performance"]
    assert "L3 (Apply)" in bloom_perf
    assert "L4 (Analyze)" in bloom_perf
    assert bloom_perf["L3 (Apply)"]["correct"] == 1
    assert bloom_perf["L4 (Analyze)"]["correct"] == 1
