import React, { useState, useEffect, useMemo } from 'react';
import { getQuestionsByCourse, getQuestionsByType } from '../data/course_quiz_data';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Course Quiz & Automated Assessment Engine (Phase 7)
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead & Systems Architect: Ashok Kumar A
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 *
 * Capabilities:
 *   - Interactive unit-wise MCQ quiz mode with instant scoring and evaluation
 *   - Part A (2-mark conceptual) and Part B (16-mark numerical) model answer viewers
 *   - Automated Step-by-Step Explanations with KaTeX formulas and common pitfalls
 *   - Question flagging for revision and persistent score auditing (localStorage)
 * ========================================================================================
 */

const STORAGE_KEY_QUIZ_FLAGS = "voltcore_quiz_flagged";
const STORAGE_KEY_QUIZ_ANSWERS = "voltcore_quiz_answers";

export default function CourseQuizEngine({
  courseCode = "EC23S01",
  themeColor = "#00F0B5",
  themeFamily = "emerald"
}) {
  // Mode selection: "all" | "MCQ" | "PART_A" | "PART_B"
  const [activeMode, setActiveMode] = useState("all");

  // Unit filter: "all" | "1" | "2" | "3" | "4" | "5"
  const [unitFilter, setUnitFilter] = useState("all");

  // User answers record: questionId -> selectedOptionIndex (number)
  const [selectedAnswers, setSelectedAnswers] = useState({});

  // Question reveal state for Part A / Part B: questionId -> boolean
  const [revealedSolutions, setRevealedSolutions] = useState({});

  // Flagged questions for student review: questionId -> boolean
  const [flaggedQuestions, setFlaggedQuestions] = useState({});

  // Feedback display filter: "all" | "incorrect" | "flagged"
  const [reviewFilter, setReviewFilter] = useState("all");

  // Load persistent states on mount
  useEffect(() => {
    try {
      if (typeof window !== 'undefined') {
        const savedFlags = localStorage.getItem(STORAGE_KEY_QUIZ_FLAGS);
        if (savedFlags) setFlaggedQuestions(JSON.parse(savedFlags));

        const savedAnswers = localStorage.getItem(STORAGE_KEY_QUIZ_ANSWERS);
        if (savedAnswers) setSelectedAnswers(JSON.parse(savedAnswers));
      }
    } catch (e) {
      console.warn("Storage restricted or unavailable:", e);
    }
  }, []);

  // Fetch assessment questions for active course
  const questions = useMemo(() => {
    return getQuestionsByCourse(courseCode);
  }, [courseCode]);

  // Filter questions based on activeMode and unitFilter
  const filteredQuestions = useMemo(() => {
    return questions.filter((q) => {
      if (activeMode !== "all" && q.type !== activeMode) return false;
      if (unitFilter !== "all" && q.unitNumber !== Number(unitFilter)) return false;

      // Review filter
      if (reviewFilter === "flagged" && !flaggedQuestions[q.id]) return false;
      if (reviewFilter === "incorrect") {
        if (q.type !== "MCQ") return false;
        const userAnswer = selectedAnswers[q.id];
        if (userAnswer === undefined || userAnswer === q.correctOptionIndex) return false;
      }
      return true;
    });
  }, [questions, activeMode, unitFilter, reviewFilter, flaggedQuestions, selectedAnswers]);

  // Score statistics for MCQs
  const scoreStats = useMemo(() => {
    const mcqs = questions.filter(q => q.type === "MCQ");
    const answeredCount = mcqs.filter(q => selectedAnswers[q.id] !== undefined).length;
    const correctCount = mcqs.filter(q => selectedAnswers[q.id] === q.correctOptionIndex).length;
    const percentage = answeredCount > 0 ? Math.round((correctCount / answeredCount) * 100) : 0;
    return {
      totalMcqs: mcqs.length,
      answeredCount,
      correctCount,
      percentage
    };
  }, [questions, selectedAnswers]);

  // Handle MCQ answer selection
  const handleSelectOption = (questionId, optionIndex) => {
    setSelectedAnswers((prev) => {
      const updated = { ...prev, [questionId]: optionIndex };
      try {
        localStorage.setItem(STORAGE_KEY_QUIZ_ANSWERS, JSON.stringify(updated));
      } catch (err) {}
      return updated;
    });
  };

  // Toggle Solution Reveal for Part A / Part B
  const toggleSolution = (questionId) => {
    setRevealedSolutions(prev => ({ ...prev, [questionId]: !prev[questionId] }));
  };

  // Toggle Flag Question
  const toggleFlag = (questionId) => {
    setFlaggedQuestions((prev) => {
      const updated = { ...prev, [questionId]: !prev[questionId] };
      try {
        localStorage.setItem(STORAGE_KEY_QUIZ_FLAGS, JSON.stringify(updated));
      } catch (err) {}
      return updated;
    });
  };

  // Reset quiz answers
  const handleResetQuiz = () => {
    setSelectedAnswers({});
    try {
      localStorage.removeItem(STORAGE_KEY_QUIZ_ANSWERS);
    } catch (err) {}
  };

  return (
    <div className="space-y-6">
      
      {/* ------------------------------------------------------------------- */}
      {/* 1. QUIZ SCORE & EVALUATION HUD */}
      {/* ------------------------------------------------------------------- */}
      <div className="p-5 rounded-2xl bg-[#041026] border border-slate-800 shadow-xl space-y-4 font-mono">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
              {courseCode} Assessment Benchmark &amp; Score Tally
            </div>
            <div className="text-lg font-extrabold text-white font-sans mt-0.5 flex items-center gap-2">
              <span>{scoreStats.correctCount} / {scoreStats.totalMcqs} Questions Correct</span>
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-full bg-[#020813] border border-slate-800" style={{ color: themeColor }}>
                {scoreStats.percentage}% Accuracy
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <button
              onClick={handleResetQuiz}
              className="px-3 py-1.5 rounded-xl bg-[#020813] hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
            >
              Reset Answers
            </button>
            <span className="px-3 py-1.5 rounded-xl bg-[#020813] border border-slate-800 text-emerald-400 font-bold">
              {questions.length} Total Problems
            </span>
          </div>
        </div>

        {/* Accuracy Progress Bar */}
        <div className="w-full h-2.5 bg-[#020813] rounded-full overflow-hidden border border-slate-800 p-0.5">
          <div
            className="h-full rounded-full transition-all duration-500 shadow-md"
            style={{
              width: `${scoreStats.percentage}%`,
              backgroundColor: themeColor
            }}
          ></div>
        </div>
      </div>

      {/* ------------------------------------------------------------------- */}
      {/* 2. MODE & UNIT NAVIGATION TABS */}
      {/* ------------------------------------------------------------------- */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 p-4 rounded-2xl bg-[#041026] border border-slate-800 font-mono text-xs shadow-md">
        
        {/* Mode Selector */}
        <div className="flex flex-wrap items-center gap-1.5">
          {[
            { id: "all", label: "All Items", icon: "📑" },
            { id: "MCQ", label: "Practice MCQs", icon: "⚡" },
            { id: "PART_A", label: "Part A (2-Mark)", icon: "🎯" },
            { id: "PART_B", label: "Part B (16-Mark)", icon: "🏆" }
          ].map((mode) => (
            <button
              key={mode.id}
              onClick={() => setActiveMode(mode.id)}
              className={`px-3 py-1.5 rounded-xl transition-all flex items-center gap-1.5 font-bold ${
                activeMode === mode.id
                  ? "bg-[#020813] text-white border scale-102"
                  : "text-slate-400 hover:text-white bg-[#020813]/40 border border-slate-800"
              }`}
              style={{
                borderColor: activeMode === mode.id ? themeColor : undefined,
                color: activeMode === mode.id ? themeColor : undefined
              }}
            >
              <span>{mode.icon}</span>
              <span>{mode.label}</span>
            </button>
          ))}
        </div>

        {/* Unit Selector Strip */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-slate-500 font-semibold mr-1">Unit:</span>
          {["all", "1", "2", "3", "4", "5"].map((u) => {
            const isSelected = unitFilter === u;
            const label = u === "all" ? "All Units" : `Unit ${["I", "II", "III", "IV", "V"][Number(u) - 1]}`;
            return (
              <button
                key={u}
                onClick={() => setUnitFilter(u)}
                className={`px-2.5 py-1 rounded-lg transition-all ${
                  isSelected
                    ? "bg-[#020813] text-white font-bold border"
                    : "text-slate-400 hover:text-white bg-[#020813]/40 border border-slate-800"
                }`}
                style={{
                  borderColor: isSelected ? themeColor : undefined,
                  color: isSelected ? themeColor : undefined
                }}
              >
                {label}
              </button>
            );
          })}
        </div>
      </div>

      {/* ------------------------------------------------------------------- */}
      {/* 3. QUESTION LIST & AUTOMATED EXPLANATION VIEWERS */}
      {/* ------------------------------------------------------------------- */}
      <div className="space-y-4">
        {filteredQuestions.map((q, qIndex) => {
          const isMcq = q.type === "MCQ";
          const userAnswer = selectedAnswers[q.id];
          const hasAnswered = userAnswer !== undefined;
          const isCorrect = hasAnswered && userAnswer === q.correctOptionIndex;
          const isFlagged = !!flaggedQuestions[q.id];
          const isSolutionRevealed = !!revealedSolutions[q.id];

          return (
            <div
              key={q.id}
              className={`p-6 rounded-2xl bg-[#041026] border transition-all shadow-xl space-y-4 ${
                isMcq && hasAnswered
                  ? isCorrect
                    ? "border-emerald-500/50 bg-[#041026]/90"
                    : "border-rose-500/50 bg-[#041026]/90"
                  : "border-slate-800 hover:border-slate-700"
              }`}
            >
              {/* Question Header Card */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3 font-mono text-xs">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="px-2 py-0.5 rounded-full bg-[#020813] border border-slate-800 font-bold" style={{ color: themeColor }}>
                    Unit {q.unitRoman} • {q.type.replace('_', ' ')}
                  </span>
                  <span className="text-slate-500">[{q.marks} Mark{q.marks > 1 ? "s" : ""}]</span>
                  <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300 text-[10px]">
                    {q.bloomLevel}
                  </span>
                  <span className="text-slate-400 text-[11px] truncate max-w-xs">
                    {q.examYearReference}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => toggleFlag(q.id)}
                    className={`px-2.5 py-1 rounded-lg border text-xs transition-all flex items-center gap-1 ${
                      isFlagged
                        ? "bg-amber-950 text-amber-300 border-amber-500/60 font-bold"
                        : "bg-[#020813] text-slate-400 border-slate-800 hover:text-amber-400"
                    }`}
                    title="Flag question for revision"
                  >
                    <span>{isFlagged ? "🚩 Flagged" : "⚐ Flag"}</span>
                  </button>
                </div>
              </div>

              {/* Question Text */}
              <div className="text-white text-sm sm:text-base font-sans font-medium leading-relaxed">
                <span className="font-bold text-slate-400 mr-2 font-mono">Q{qIndex + 1}.</span>
                {q.questionText}
              </div>

              {/* MCQ Options Grid */}
              {isMcq && q.options && (
                <div className="grid grid-cols-1 gap-2 pt-2">
                  {q.options.map((opt, optIdx) => {
                    const isSelected = userAnswer === optIdx;
                    const isTheCorrectOption = q.correctOptionIndex === optIdx;

                    let btnStyle = "bg-[#020813] border-slate-800 text-slate-300 hover:border-slate-700";
                    if (hasAnswered) {
                      if (isTheCorrectOption) {
                        btnStyle = "bg-emerald-950/60 border-emerald-500 text-emerald-200 font-bold shadow-md";
                      } else if (isSelected) {
                        btnStyle = "bg-rose-950/60 border-rose-500 text-rose-200 font-bold";
                      } else {
                        btnStyle = "bg-[#020813]/40 border-slate-900 text-slate-500 opacity-60";
                      }
                    }

                    return (
                      <button
                        key={optIdx}
                        onClick={() => handleSelectOption(q.id, optIdx)}
                        className={`p-3.5 rounded-xl border text-left font-mono text-xs sm:text-sm transition-all flex items-center justify-between ${btnStyle}`}
                      >
                        <div className="flex items-center gap-3">
                          <span className="w-6 h-6 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center font-bold text-xs text-slate-400">
                            {["A", "B", "C", "D"][optIdx]}
                          </span>
                          <span>{opt}</span>
                        </div>
                        {hasAnswered && (
                          <span>
                            {isTheCorrectOption ? "✓ Correct" : isSelected ? "✗ Incorrect" : ""}
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>
              )}

              {/* Part A / Part B Solution Toggle */}
              {!isMcq && (
                <div className="pt-2">
                  <button
                    onClick={() => toggleSolution(q.id)}
                    className="px-4 py-2 rounded-xl bg-[#020813] hover:bg-slate-800 border border-slate-800 text-xs font-mono font-bold transition-all flex items-center gap-2"
                    style={{ color: themeColor }}
                  >
                    <span>{isSolutionRevealed ? "Hide Model Solution ▲" : "Reveal Model Answer & Derivation Steps ▼"}</span>
                  </button>
                </div>
              )}

              {/* --------------------------------------------------------------- */}
              {/* AUTOMATED EXPLANATION & DERIVATION VIEWER */}
              {/* --------------------------------------------------------------- */}
              {((isMcq && hasAnswered) || (!isMcq && isSolutionRevealed)) && (
                <div className="mt-4 p-5 rounded-2xl bg-[#020813] border border-slate-800 space-y-4 font-mono text-xs animate-fadeIn">
                  
                  {/* Status Banner */}
                  {isMcq && (
                    <div className={`p-3 rounded-xl border flex items-center justify-between font-bold ${
                      isCorrect
                        ? "bg-emerald-950/40 text-emerald-300 border-emerald-500/40"
                        : "bg-rose-950/40 text-rose-300 border-rose-500/40"
                    }`}>
                      <div className="flex items-center gap-2">
                        <span>{isCorrect ? "🎉 CORRECT ANSWER" : "❌ INCORRECT ANSWER"}</span>
                        <span className="font-normal text-slate-300">
                          — Correct Option is {["A", "B", "C", "D"][q.correctOptionIndex]}
                        </span>
                      </div>
                      <span>Score: {isCorrect ? `+${q.marks}` : "0"}</span>
                    </div>
                  )}

                  {/* Solution Summary */}
                  <div>
                    <div className="font-bold text-white uppercase text-[11px] tracking-wider mb-1">
                      Academic Solution Summary:
                    </div>
                    <p className="text-slate-300 font-sans text-xs leading-relaxed">
                      {q.solutionSummary}
                    </p>
                  </div>

                  {/* Step-by-Step Mathematical Explanation */}
                  <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
                    <div className="font-bold text-slate-400 uppercase text-[10px] tracking-wider">
                      Step-by-Step Derivation Breakdown:
                    </div>
                    <div className="space-y-1">
                      {q.stepByStepExplanation.map((step, sIdx) => (
                        <div key={sIdx} className="p-2 rounded-lg bg-[#041026] text-slate-300 text-[11px]">
                          {step}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Key Formulations Box (KaTeX) */}
                  {q.keyFormulas && q.keyFormulas.length > 0 && (
                    <div className="space-y-2 pt-2 border-t border-slate-800/80">
                      <div className="font-bold text-[10px] uppercase tracking-wider" style={{ color: themeColor }}>
                        Governing Formulations (KaTeX / LaTeX):
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {q.keyFormulas.map((formula, fIdx) => (
                          <div key={fIdx} className="p-3 rounded-xl bg-[#041026] border border-slate-800 text-center text-xs font-mono text-white">
                            <code>{formula}</code>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Common Student Pitfall Warning */}
                  {q.commonPitfall && (
                    <div className="p-3 rounded-xl bg-amber-950/20 border border-amber-500/30 text-amber-300 text-[11px] space-y-1">
                      <div className="font-bold flex items-center gap-1 text-[10px] uppercase tracking-wider text-amber-400">
                        <span>⚠️ Exam Pitfall to Avoid:</span>
                      </div>
                      <div>{q.commonPitfall}</div>
                    </div>
                  )}

                </div>
              )}

            </div>
          );
        })}
      </div>

    </div>
  );
}
