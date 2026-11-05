"""
========================================================================================
VoltCore Apex Academia - Academic Examination & GATE ECE Evaluator Engine
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/exam_evaluator_engine.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  High-performance, lightweight evaluation engine for Anna University semester exams
  and national GATE ECE test simulations. Computes negative marking, section breakdowns,
  Course Outcome (CO1-CO5) attainment metrics, simulated percentiles, and mistake analysis.
========================================================================================
"""

import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone

# Standard Course Outcome Mappings for Anna University Regulation 2023 ECE
COURSE_OUTCOMES = {
    "CO1": "Analyze semiconductor devices, hybrid-pi models, and analog amplifier bandwidth",
    "CO2": "Design synchronous/asynchronous sequential digital systems, FSMs, and K-Map logic",
    "CO3": "Develop pipelined assembly firmware and hardware drivers for ARM Cortex / 8051",
    "CO4": "Engineer deterministic real-time multi-tasking and zero-copy IPC using FreeRTOS",
    "CO5": "Integrate edge IoT sensor topologies, LittleFS flash wear-leveling, and power modes"
}


class ExamEvaluatorEngine:
    """
    Automated evaluation engine for competitive and curriculum ECE examinations.
    Enforces Anna University & GATE ECE evaluation standards with sub-millisecond latency.
    """

    def __init__(self):
        self.course_outcomes = COURSE_OUTCOMES

    def evaluate_exam_submission(
        self,
        questions: List[Dict[str, Any]],
        student_answers: Dict[str, Any],
        enable_negative_marking: bool = True,
        exam_id: str = "GATE-ECE-2026-MOCK-01",
        student_id: str = "2023MITEC042"
    ) -> Dict[str, Any]:
        """
        Scores an exam submission against question rubrics.
        Calculates positive score, negative deductions, net score, CO attainment, and percentile.
        """
        t0 = time.perf_counter()

        total_questions = len(questions)
        answered_count = 0
        correct_count = 0
        incorrect_count = 0
        unanswered_count = 0

        max_possible_score = 0.0
        positive_score = 0.0
        negative_deduction = 0.0

        # Section-wise breakdown: { section_name: { 'earned': float, 'total': float, 'correct': int, 'incorrect': int } }
        section_stats: Dict[str, Dict[str, Any]] = {}

        # Course Outcome breakdown: { 'CO1': { 'earned': float, 'total': float, 'questions': int } }
        co_stats: Dict[str, Dict[str, Any]] = {
            co_id: {
                "description": desc,
                "earned_marks": 0.0,
                "total_marks": 0.0,
                "question_count": 0,
                "correct_count": 0
            }
            for co_id, desc in self.course_outcomes.items()
        }

        mistake_analysis: List[Dict[str, Any]] = []

        for q in questions:
            q_id = str(q.get("id"))
            marks = float(q.get("marks", 1))
            sec = str(q.get("section", "General ECE"))
            co = str(q.get("course_outcome", "CO1"))
            q_type = str(q.get("type", "MCQ")).upper()
            correct_ans = q.get("correctAnswer")
            tolerance = float(q.get("tolerance", 0.0))
            bloom = str(q.get("bloom_taxonomy", "Apply"))

            max_possible_score += marks

            # Initialize section stats if new
            if sec not in section_stats:
                section_stats[sec] = {
                    "earned_marks": 0.0,
                    "total_marks": 0.0,
                    "correct": 0,
                    "incorrect": 0,
                    "unanswered": 0
                }
            section_stats[sec]["total_marks"] += marks

            # Ensure CO exists in tracking
            if co not in co_stats:
                co_stats[co] = {
                    "description": "General ECE Engineering Outcome",
                    "earned_marks": 0.0,
                    "total_marks": 0.0,
                    "question_count": 0,
                    "correct_count": 0
                }
            co_stats[co]["total_marks"] += marks
            co_stats[co]["question_count"] += 1

            # Check student answer
            student_val = student_answers.get(q_id)

            if student_val is None or str(student_val).strip() == "":
                unanswered_count += 1
                section_stats[sec]["unanswered"] += 1
                continue

            answered_count += 1
            is_correct = False

            if q_type == "NAT":
                # Numerical Answer Type (within tolerance)
                try:
                    s_num = float(student_val)
                    c_num = float(correct_ans)
                    if abs(s_num - c_num) <= tolerance:
                        is_correct = True
                except (ValueError, TypeError):
                    is_correct = False
            else:
                # Standard Multiple Choice (case-insensitive string match)
                is_correct = (str(student_val).strip().upper() == str(correct_ans).strip().upper())

            if is_correct:
                correct_count += 1
                positive_score += marks
                section_stats[sec]["earned_marks"] += marks
                section_stats[sec]["correct"] += 1
                co_stats[co]["earned_marks"] += marks
                co_stats[co]["correct_count"] += 1
            else:
                incorrect_count += 1
                section_stats[sec]["incorrect"] += 1

                # Calculate negative penalty (GATE style: 1/3 mark for 1-mark question, 2/3 for 2-mark question)
                # NAT questions in GATE have zero negative marking
                penalty = 0.0
                if enable_negative_marking and q_type != "NAT":
                    penalty = round(marks / 3.0, 2)
                    negative_deduction += penalty
                    section_stats[sec]["earned_marks"] -= penalty

                mistake_analysis.append({
                    "question_id": q_id,
                    "section": sec,
                    "course_outcome": co,
                    "bloom_taxonomy": bloom,
                    "question_text": q.get("question", "")[:120] + "...",
                    "student_answer": student_val,
                    "correct_answer": correct_ans,
                    "penalty_incurred": penalty,
                    "distractor_trap": q.get("distractorAnalysis", "Review standard textbook derivation."),
                    "remedy": q.get("solution", "Refer to Anna University Regulation 2023 syllabus.")[:200] + "..."
                })

        net_score = round(max(0.0, positive_score - negative_deduction), 2)
        percentage = round((net_score / max(1.0, max_possible_score)) * 100.0, 2)

        # Compute simulated percentile (Gaussian approximation against historical Anna University / GATE cohort)
        # Score of 80%+ corresponds to 99th percentile; 60% corresponds to 90th percentile
        if percentage >= 90.0:
            simulated_percentile = round(99.0 + (percentage - 90.0) * 0.09, 2)
            rank_band = "All India Rank (AIR) 1 - 25"
        elif percentage >= 75.0:
            simulated_percentile = round(95.0 + (percentage - 75.0) * 0.26, 2)
            rank_band = "AIR 26 - 150 (MIT Campus Top Decile)"
        elif percentage >= 60.0:
            simulated_percentile = round(85.0 + (percentage - 60.0) * 0.66, 2)
            rank_band = "AIR 151 - 600 (GATE Qualified)"
        elif percentage >= 45.0:
            simulated_percentile = round(70.0 + (percentage - 45.0) * 1.0, 2)
            rank_band = "State Merit Band"
        else:
            simulated_percentile = round(max(10.0, percentage * 1.5), 2)
            rank_band = "Foundation Building Required"

        # Calculate CO attainment percentages & NBA accreditation status
        co_attainment_summary: Dict[str, Any] = {}
        for co_id, cdata in co_stats.items():
            tot = cdata["total_marks"]
            earned = cdata["earned_marks"]
            pct = round((earned / max(1.0, tot)) * 100.0, 2) if tot > 0 else 0.0

            if pct >= 80.0:
                attainment_level = "Exemplary (Level 3)"
            elif pct >= 60.0:
                attainment_level = "Attained (Level 2)"
            elif pct >= 40.0:
                attainment_level = "Developing (Level 1)"
            else:
                attainment_level = "Action Required (Level 0)"

            co_attainment_summary[co_id] = {
                "description": cdata["description"],
                "earned_marks": earned,
                "total_marks": tot,
                "attainment_percent": pct,
                "level": attainment_level,
                "passed": pct >= 60.0
            }

        eval_duration_ms = round((time.perf_counter() - t0) * 1000.0, 3)

        return {
            "status": "SUCCESS",
            "exam_id": exam_id,
            "student_id": student_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evaluation_duration_ms": eval_duration_ms,
            "score_summary": {
                "max_possible_score": max_possible_score,
                "positive_score": round(positive_score, 2),
                "negative_deductions": round(negative_deduction, 2),
                "net_score": net_score,
                "percentage": percentage,
                "grade": "O" if percentage >= 90 else "A+" if percentage >= 80 else "A" if percentage >= 70 else "B+" if percentage >= 60 else "RA",
                "simulated_percentile": simulated_percentile,
                "rank_band": rank_band,
                "passed": percentage >= 60.0,
                "xp_reward": 180 if percentage >= 60.0 else 75
            },
            "question_stats": {
                "total": total_questions,
                "answered": answered_count,
                "unanswered": unanswered_count,
                "correct": correct_count,
                "incorrect": incorrect_count,
                "accuracy_percent": round((correct_count / max(1, answered_count)) * 100.0, 2)
            },
            "section_breakdown": section_stats,
            "course_outcome_attainment": co_attainment_summary,
            "mistake_analysis": mistake_analysis,
            "academic_institution": "Madras Institute of Technology (MIT) Campus, Anna University",
            "evaluator": "VoltCore Apex Academic Evaluation Engine v9.0"
        }


# Global evaluator singleton
exam_evaluator = ExamEvaluatorEngine()
