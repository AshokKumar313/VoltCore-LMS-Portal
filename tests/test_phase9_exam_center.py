"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 9 Academic Exam Center & Evaluator Engine
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase9_exam_center.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import time
import json
import unittest
from backend.exam_evaluator_engine import ExamEvaluatorEngine, exam_evaluator


class TestPhase9ExamCenter(unittest.TestCase):
    """
    Validation suite for Phase 9:
      - Academic examination evaluator scoring and negative marking
      - Course Outcome (CO1-CO5) attainment percentage mapping
      - Simulated percentile computation
      - Mistake derivation analysis
      - ExamSimulator React island and exam-center Astro page
    """

    def setUp(self):
        self.evaluator = ExamEvaluatorEngine()
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.sample_questions = [
            {
                "id": "q1",
                "section": "Analog",
                "course_outcome": "CO1",
                "marks": 2,
                "type": "NAT",
                "question": "BJT Miller capacitance derivation",
                "correctAnswer": 658.5,
                "tolerance": 2.0,
                "solution": "C_M = 3.5 * 181 = 633.5 pF; Total = 658.5 pF.",
                "distractorAnalysis": "Neglecting C_pi yields 633.5 pF."
            },
            {
                "id": "q2",
                "section": "Digital",
                "course_outcome": "CO2",
                "marks": 1,
                "type": "MCQ",
                "question": "K-Map Gray code distance",
                "correctAnswer": "A",
                "solution": "Hamming distance = 1.",
                "distractorAnalysis": "Binary ordering assumption."
            },
            {
                "id": "q3",
                "section": "Embedded",
                "course_outcome": "CO4",
                "marks": 2,
                "type": "MCQ",
                "question": "DMA memory barrier primitive",
                "correctAnswer": "C",
                "solution": "Use __DMB() data memory barrier.",
                "distractorAnalysis": "__NOP does not serialize bus."
            }
        ]

    def test_evaluator_perfect_score(self):
        """All correct answers must achieve full score, Grade O, and > 99th percentile."""
        answers = {
            "q1": 658.5,
            "q2": "A",
            "q3": "C"
        }
        res = self.evaluator.evaluate_exam_submission(self.sample_questions, answers, enable_negative_marking=True)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["score_summary"]["max_possible_score"], 5.0)
        self.assertEqual(res["score_summary"]["net_score"], 5.0)
        self.assertEqual(res["score_summary"]["percentage"], 100.0)
        self.assertEqual(res["score_summary"]["grade"], "O")
        self.assertGreaterEqual(res["score_summary"]["simulated_percentile"], 99.0)
        self.assertEqual(res["score_summary"]["xp_reward"], 180)
        self.assertEqual(res["question_stats"]["correct"], 3)
        self.assertEqual(res["question_stats"]["incorrect"], 0)
        self.assertEqual(len(res["mistake_analysis"]), 0)

    def test_evaluator_negative_marking_gate_mode(self):
        """Incorrect MCQ in GATE mode incurs 1/3 penalty; NAT has zero penalty."""
        # q1 (NAT 2m) is wrong -> 0 penalty in GATE NAT
        # q2 (MCQ 1m) is correct (+1m)
        # q3 (MCQ 2m) is wrong -> -0.67 penalty (2/3)
        answers = {
            "q1": 999.0,  # Wrong NAT
            "q2": "A",    # Correct MCQ (+1)
            "q3": "B"     # Wrong MCQ (-0.67)
        }
        res = self.evaluator.evaluate_exam_submission(self.sample_questions, answers, enable_negative_marking=True)
        summary = res["score_summary"]
        self.assertEqual(summary["positive_score"], 1.0)
        self.assertAlmostEqual(summary["negative_deductions"], 0.67, places=2)
        self.assertAlmostEqual(summary["net_score"], 0.33, places=2)
        self.assertEqual(res["question_stats"]["correct"], 1)
        self.assertEqual(res["question_stats"]["incorrect"], 2)

    def test_evaluator_zero_penalty_university_mode(self):
        """Anna University semester exam mode carries zero negative marking deductions."""
        answers = {
            "q1": 658.5,  # Correct NAT (+2)
            "q2": "C",    # Wrong MCQ (0 penalty)
            "q3": "D"     # Wrong MCQ (0 penalty)
        }
        res = self.evaluator.evaluate_exam_submission(self.sample_questions, answers, enable_negative_marking=False)
        summary = res["score_summary"]
        self.assertEqual(summary["positive_score"], 2.0)
        self.assertEqual(summary["negative_deductions"], 0.0)
        self.assertEqual(summary["net_score"], 2.0)

    def test_evaluator_course_outcome_attainment(self):
        """Course Outcomes (CO1-CO5) must compute earned marks and level classification."""
        answers = {
            "q1": 658.5,  # CO1: 2/2 -> 100%
            "q2": "B",    # CO2: 0/1 -> 0%
            "q3": "C"     # CO4: 2/2 -> 100%
        }
        res = self.evaluator.evaluate_exam_submission(self.sample_questions, answers)
        co_map = res["course_outcome_attainment"]

        self.assertIn("CO1", co_map)
        self.assertEqual(co_map["CO1"]["attainment_percent"], 100.0)
        self.assertEqual(co_map["CO1"]["level"], "Exemplary (Level 3)")
        self.assertTrue(co_map["CO1"]["passed"])

        self.assertIn("CO2", co_map)
        self.assertEqual(co_map["CO2"]["attainment_percent"], 0.0)
        self.assertEqual(co_map["CO2"]["level"], "Action Required (Level 0)")
        self.assertFalse(co_map["CO2"]["passed"])

    def test_evaluator_mistake_analysis_remediation(self):
        """Mistake analysis must include question ID, distractor trap, and solution snippet."""
        answers = {"q3": "A"}  # Wrong answer for q3
        res = self.evaluator.evaluate_exam_submission(self.sample_questions, answers)
        mistakes = res["mistake_analysis"]
        self.assertEqual(len(mistakes), 1)

        m = mistakes[0]
        self.assertEqual(m["question_id"], "q3")
        self.assertEqual(m["student_answer"], "A")
        self.assertEqual(m["correct_answer"], "C")
        self.assertIn("NOP", m["distractor_trap"])
        self.assertIn("DMB", m["remedy"])

    def test_evaluator_execution_time_under_10ms(self):
        """Evaluation engine must execute in < 10ms to prevent thermal/CPU spikes."""
        t0 = time.perf_counter()
        for _ in range(50):
            _ = self.evaluator.evaluate_exam_submission(self.sample_questions, {"q1": 658.5, "q2": "A", "q3": "C"})
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        avg_per_eval_ms = elapsed_ms / 50.0

        self.assertLess(avg_per_eval_ms, 1.0, f"Evaluator took {avg_per_eval_ms:.3f}ms per call (> 1.0ms)")

    def test_exam_center_page_and_component_exist(self):
        """src/pages/exam-center.astro and src/components/ExamSimulator.jsx must exist."""
        page_path = os.path.join(self.base_dir, "src", "pages", "exam-center.astro")
        comp_path = os.path.join(self.base_dir, "src", "components", "ExamSimulator.jsx")
        dist_path = os.path.join(self.base_dir, "dist", "exam-center", "index.html")

        self.assertTrue(os.path.isfile(page_path), "exam-center.astro missing")
        self.assertTrue(os.path.isfile(comp_path), "ExamSimulator.jsx missing")
        self.assertTrue(os.path.isfile(dist_path), "dist/exam-center/index.html missing from static build")

    def test_exam_simulator_features_present(self):
        """ExamSimulator.jsx must implement timer, question palette, and CO1-CO5 mapping."""
        comp_path = os.path.join(self.base_dir, "src", "components", "ExamSimulator.jsx")
        with open(comp_path, "r", encoding="utf-8") as f:
            code = f.read()

        required_features = [
            "SECTIONS",
            "negativeMarking",
            "timeRemaining",
            "formatTime",
            "Question Palette",
            "coAttainment",
            "Commit Grade (+180 XP)",
            "Course Outcome Attainment"
        ]
        for feat in required_features:
            self.assertIn(feat, code, f"Feature '{feat}' missing from ExamSimulator.jsx")

    def test_privacy_invariants_no_leakage(self):
        """Private admin email and phone must never be hardcoded in Phase 9 files."""
        restricted_patterns = ["ashokkumar2008313@gmail.com", "9597382878"]
        phase9_files = [
            os.path.join(self.base_dir, "src", "components", "ExamSimulator.jsx"),
            os.path.join(self.base_dir, "src", "pages", "exam-center.astro")
        ]

        for p9_path in phase9_files:
            with open(p9_path, "r", encoding="utf-8") as f:
                content = f.read()
                for pat in restricted_patterns:
                    self.assertNotIn(
                        pat,
                        content,
                        f"Restricted admin metadata leaked in {p9_path}"
                    )


if __name__ == "__main__":
    unittest.main()
