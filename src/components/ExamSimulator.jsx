import React, { useState, useEffect, useRef, useMemo } from 'react';
import { triggerToast } from './ToastNotifications.jsx';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Advanced Academic Examination Center & GATE ECE Simulator
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Component: src/components/ExamSimulator.jsx
 * Platform Lead / Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 * 
 * Features:
 *   - Timed multi-section examination simulator with auto-submit countdown timer
 *   - Configurable GATE ECE negative marking mode (+1/-0.33, +2/-0.66) vs University zero penalty
 *   - Question palette HUD (Answered, Unanswered, Marked for Review, Answered & Marked)
 *   - Instantaneous evaluation against Anna University Regulation 2023 Course Outcomes (CO1-CO5)
 *   - Automated question shuffling and detailed mistake derivation analysis (+180 XP)
 * ========================================================================================
 */

const SECTIONS = [
  { id: 'sec_analog', title: 'Section 1: Analog & Signal Integrity (CO1)' },
  { id: 'sec_digital', title: 'Section 2: Digital Systems & Microprocessors (CO2, CO3)' },
  { id: 'sec_embedded', title: 'Section 3: FreeRTOS, DMA & Edge IoT (CO4, CO5)' }
];

const INITIAL_EXAM_QUESTIONS = [
  // SECTION 1: ANALOG & SIGNAL INTEGRITY (CO1)
  {
    id: 'analog_01',
    section: 'sec_analog',
    course_outcome: 'CO1',
    marks: 2,
    type: 'NAT',
    title: 'BJT Miller Input Capacitance',
    question: 'A BJT Common-Emitter amplifier has small-signal voltage gain Av = -180. The transistor has base-collector junction capacitance C_mu = 3.5 pF and base-emitter capacitance C_pi = 25 pF. Calculate the total effective input capacitance (in pF) due to Miller feedback.',
    correctAnswer: 658.5,
    tolerance: 2.0,
    unit: 'pF',
    derivation: 'C_M = C_mu * (1 - Av) = 3.5 * (1 + 180) = 633.5 pF. Total C_in = C_pi + C_M = 25 + 633.5 = 658.5 pF.',
    distractor: 'Forgetting sign reversal gives 3.5 * 179 = 626.5 pF. Neglecting C_pi yields 633.5 pF.'
  },
  {
    id: 'analog_02',
    section: 'sec_analog',
    course_outcome: 'CO1',
    marks: 2,
    type: 'MCQ',
    title: 'Op-Amp Slew Rate & Bandwidth',
    question: 'An ideal operational amplifier with Slew Rate SR = 8.0 V/µs outputs an undistorted sinusoid of peak amplitude V_p = 4.0 V. What is the maximum Full-Power Bandwidth (f_max) in kHz?',
    options: [
      { key: 'A', text: '159.2 kHz' },
      { key: 'B', text: '318.3 kHz' },
      { key: 'C', text: '636.6 kHz' },
      { key: 'D', text: '79.6 kHz' }
    ],
    correctAnswer: 'B',
    derivation: 'f_max = SR / (2 * pi * V_p) = (8.0 * 10^6) / (2 * pi * 4.0) = 318,310 Hz ≈ 318.3 kHz.',
    distractor: 'Option A uses peak-to-peak voltage 8V. Option C neglects factor of 2 in 2*pi.'
  },

  // SECTION 2: DIGITAL & MICROPROCESSORS (CO2, CO3)
  {
    id: 'digital_01',
    section: 'sec_digital',
    course_outcome: 'CO2',
    marks: 1,
    type: 'MCQ',
    title: 'Gray Code K-Map Adjacency',
    question: 'In a 4-variable Karnaugh Map (variables A, B, C, D in Gray code order), minterm m11 (binary 1011) and minterm m10 (binary 1010) differ by:',
    options: [
      { key: 'A', text: 'Exactly 1 bit (Logical Adjacency)' },
      { key: 'B', text: '2 bits (Diagonal Adjacency)' },
      { key: 'C', text: 'No bits (Duplicate cells)' },
      { key: 'D', text: '3 bits (Non-adjacent cells)' }
    ],
    correctAnswer: 'A',
    derivation: 'Binary 1011 XOR 1010 = 0001 (Hamming distance = 1), fulfilling unit-distance Gray code adjacency.',
    distractor: 'Assuming standard binary ordering instead of reflected Gray code ordering leads to confusion.'
  },
  {
    id: 'digital_02',
    section: 'sec_digital',
    course_outcome: 'CO3',
    marks: 2,
    type: 'MCQ',
    title: 'ARM Cortex-M BSRR Atomic Write',
    question: 'On an ARM Cortex-M4 microcontroller, which register mechanism guarantees single-cycle atomic GPIO pin toggling without read-modify-write race conditions?',
    options: [
      { key: 'A', text: 'Direct write to ODR (Output Data Register)' },
      { key: 'B', text: 'BSRR (Bit Set/Reset Register) lower and upper half-words' },
      { key: 'C', text: 'Software disable interrupts around ODR bitwise OR' },
      { key: 'D', text: 'Memory barrier __DSB() before ODR write' }
    ],
    correctAnswer: 'B',
    derivation: 'Writing 1 to BSRR bits 0-15 sets pins; writing 1 to bits 16-31 resets pins atomically in 1 clock cycle.',
    distractor: 'Direct write to ODR requires multi-cycle read-modify-write, vulnerable to interrupt preemption.'
  },

  // SECTION 3: FREERTOS, DMA & IOT (CO4, CO5)
  {
    id: 'embedded_01',
    section: 'sec_embedded',
    course_outcome: 'CO4',
    marks: 2,
    type: 'MCQ',
    title: 'DMA Memory Barrier Coherency',
    question: 'When arming an ARM Cortex-M circular DMA stream after updating memory buffer descriptors, which ISO C instruction barrier must be executed before writing CR_EN to guarantee SRAM coherency?',
    options: [
      { key: 'A', text: '__NOP() pipeline pad' },
      { key: 'B', text: '__WFI() wait for interrupt' },
      { key: 'C', text: '__DMB() (Data Memory Barrier)' },
      { key: 'D', text: '__SEV() send event' }
    ],
    correctAnswer: 'C',
    derivation: '__DMB() forces all explicit data memory writes to complete on the AHB matrix before enabling the peripheral stream.',
    distractor: '__NOP() only pads the pipeline; it does not serialize bus matrix writes.'
  },
  {
    id: 'embedded_02',
    section: 'sec_embedded',
    course_outcome: 'CO5',
    marks: 1,
    type: 'MCQ',
    title: 'ESP32 Input-Only Pin Restriction',
    question: 'Which set of ESP32 GPIO pins are strictly GPI (General Purpose Input only) and lack internal output pull-up/pull-down transistors?',
    options: [
      { key: 'A', text: 'GPIO 18, 19, 21, 22' },
      { key: 'B', text: 'GPIO 34, 35, 36, 39' },
      { key: 'C', text: 'GPIO 0, 2, 4, 15' },
      { key: 'D', text: 'GPIO 12, 13, 14, 27' }
    ],
    correctAnswer: 'B',
    derivation: 'ESP32 Technical Reference specifies GPI 34-39 have no output drivers and cannot be set to OUTPUT.',
    distractor: 'Option C contains strapping pins; Option A are standard output pins for SPI/I2C.'
  }
];

export default function ExamSimulator() {
  const [examStarted, setExamStarted] = useState(false);
  const [examSubmitted, setExamSubmitted] = useState(false);
  const [activeSection, setActiveSection] = useState('sec_analog');
  const [currentQIdx, setCurrentQIdx] = useState(0);

  // Configuration options
  const [negativeMarking, setNegativeMarking] = useState(true);
  const [shuffleQuestions, setShuffleQuestions] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(1200); // 20 minutes in seconds
  const [isTimerPaused, setIsTimerPaused] = useState(false);

  // Student Responses: { [qId]: answer }
  const [answers, setAnswers] = useState({});
  // Review flags: { [qId]: boolean }
  const [reviewFlags, setReviewFlags] = useState({});
  // Evaluation Result
  const [evaluationResult, setEvaluationResult] = useState(null);
  const [ledgerCommitted, setLedgerCommitted] = useState(false);

  const timerRef = useRef(null);

  // Prepared Question List (shuffled or sequential)
  const questionPool = useMemo(() => {
    const list = [...INITIAL_EXAM_QUESTIONS];
    if (shuffleQuestions && !examStarted) {
      return list.sort(() => Math.random() - 0.5);
    }
    return list;
  }, [shuffleQuestions, examStarted]);

  // Section filtered questions
  const sectionQuestions = useMemo(() => {
    return questionPool.filter(q => q.section === activeSection);
  }, [questionPool, activeSection]);

  const activeQuestion = sectionQuestions[currentQIdx] || sectionQuestions[0];

  // Global Countdown Timer
  useEffect(() => {
    if (!examStarted || examSubmitted || isTimerPaused) return;

    timerRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          clearInterval(timerRef.current);
          handleAutoSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timerRef.current);
  }, [examStarted, examSubmitted, isTimerPaused]);

  const handleStartExam = () => {
    setExamStarted(true);
    setExamSubmitted(false);
    setTimeRemaining(1200);
    setAnswers({});
    setReviewFlags({});
    setEvaluationResult(null);
    setLedgerCommitted(false);
    setCurrentQIdx(0);
    triggerToast({
      title: 'Examination Commenced',
      message: 'Timer started: 20 minutes. Negative marking mode: ' + (negativeMarking ? 'ENABLED (1/3 deduction)' : 'DISABLED'),
      type: 'info',
      category: 'academic'
    });
  };

  const handleAnswerSelect = (qId, val) => {
    setAnswers(prev => ({ ...prev, [qId]: val }));
  };

  const handleClearAnswer = (qId) => {
    setAnswers(prev => {
      const copy = { ...prev };
      delete copy[qId];
      return copy;
    });
  };

  const handleToggleReview = (qId) => {
    setReviewFlags(prev => ({ ...prev, [qId]: !prev[qId] }));
  };

  const handleAutoSubmit = () => {
    triggerToast({
      title: 'Time Elapsed',
      message: 'Examination timer reached 00:00. Automatically evaluating submission...',
      type: 'warning',
      category: 'academic'
    });
    executeEvaluation();
  };

  const executeEvaluation = () => {
    clearInterval(timerRef.current);

    let maxScore = 0;
    let posScore = 0;
    let negScore = 0;
    let correct = 0;
    let incorrect = 0;
    let unanswered = 0;

    const coAttainment = {
      CO1: { earned: 0, total: 0, name: 'Analog & Signal Integrity' },
      CO2: { earned: 0, total: 0, name: 'Digital Sequential Systems' },
      CO3: { earned: 0, total: 0, name: 'Microprocessor & ARM Firmware' },
      CO4: { earned: 0, total: 0, name: 'FreeRTOS Multi-Tasking' },
      CO5: { earned: 0, total: 0, name: 'IoT Sensors & Hardware' }
    };

    const mistakes = [];

    questionPool.forEach(q => {
      const m = q.marks;
      maxScore += m;
      const co = q.course_outcome;
      if (coAttainment[co]) coAttainment[co].total += m;

      const studentAns = answers[q.id];

      if (studentAns === undefined || String(studentAns).trim() === '') {
        unanswered++;
        return;
      }

      let isCorrect = false;
      if (q.type === 'NAT') {
        const sNum = parseFloat(studentAns);
        const cNum = parseFloat(q.correctAnswer);
        if (!isNaN(sNum) && Math.abs(sNum - cNum) <= q.tolerance) {
          isCorrect = true;
        }
      } else {
        isCorrect = String(studentAns).toUpperCase() === String(q.correctAnswer).toUpperCase();
      }

      if (isCorrect) {
        correct++;
        posScore += m;
        if (coAttainment[co]) coAttainment[co].earned += m;
      } else {
        incorrect++;
        let penalty = 0;
        if (negativeMarking && q.type !== 'NAT') {
          penalty = Number((m / 3.0).toFixed(2));
          negScore += penalty;
        }
        mistakes.push({
          id: q.id,
          title: q.title,
          studentAns,
          correctAns: q.correctAnswer,
          penalty,
          derivation: q.derivation,
          distractor: q.distractor
        });
      }
    });

    const netScore = Math.max(0, Number((posScore - negScore).toFixed(2)));
    const percentage = Number(((netScore / Math.max(1, maxScore)) * 100).toFixed(1));

    // Simulated percentile
    const percentile = percentage >= 85 ? 99.2 : percentage >= 70 ? 94.5 : percentage >= 50 ? 82.0 : 64.0;
    const rankBand = percentage >= 85 ? 'AIR 1 - 25 (MIT Campus Gold Medal)' : percentage >= 70 ? 'AIR 26 - 150 (Top Decile)' : 'GATE Qualified';

    const result = {
      maxScore,
      posScore,
      negScore,
      netScore,
      percentage,
      correct,
      incorrect,
      unanswered,
      percentile,
      rankBand,
      coAttainment,
      mistakes,
      grade: percentage >= 85 ? 'O' : percentage >= 70 ? 'A+' : percentage >= 55 ? 'A' : 'RA'
    };

    setEvaluationResult(result);
    setExamSubmitted(true);

    triggerToast({
      title: 'Exam Evaluated',
      message: `Score: ${netScore}/${maxScore} (${percentage}%). ${result.grade === 'O' ? 'Outstanding Performance!' : 'Evaluation complete.'}`,
      type: 'success',
      category: 'academic'
    });
  };

  const handleCommitLedger = () => {
    setLedgerCommitted(true);
    triggerToast({
      title: 'Ledger Synchronized',
      message: 'Exam score committed to student transcript ledger. +180 XP Credited!',
      type: 'success',
      category: 'telemetry'
    });
  };

  // Format time mm:ss
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  return (
    <div className="rounded-3xl border border-[#00F0B5]/30 bg-gradient-to-br from-[#020813] via-[#041026] to-[#020813] p-6 sm:p-8 font-mono text-slate-100 shadow-2xl space-y-6">
      
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-[#00F0B5] border border-[#00F0B5]/30 font-bold uppercase tracking-wider">
              Anna University / GATE ECE Center
            </span>
            <span className="text-xs text-slate-400">Regulation 2023 Mock Hall</span>
          </div>
          <h2 className="text-lg sm:text-xl font-bold text-white mt-1">
            Advanced Electronics Examination Simulator
          </h2>
        </div>

        {/* Action / Mode Badges */}
        <div className="flex flex-wrap items-center gap-3">
          {examStarted && !examSubmitted && (
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border ${
              timeRemaining < 180
                ? 'bg-rose-950/80 border-rose-500 text-rose-300 animate-pulse'
                : 'bg-[#020813] border-slate-700 text-slate-200'
            }`}>
              <svg className="w-4 h-4 text-[#00F0B5]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              <span className="font-bold text-sm">{formatTime(timeRemaining)}</span>
            </div>
          )}

          {!examStarted && (
            <button
              type="button"
              onClick={handleStartExam}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00F0B5] hover:brightness-110 text-[#020813] font-bold text-xs uppercase tracking-wider transition-all shadow-emerald-glow"
            >
              Start 20-Min Exam
            </button>
          )}

          {examStarted && !examSubmitted && (
            <button
              type="button"
              onClick={executeEvaluation}
              className="px-4 py-1.5 rounded-xl bg-rose-600/30 hover:bg-rose-600 text-rose-300 hover:text-white border border-rose-500/40 text-xs font-bold transition-all"
            >
              Finish & Submit
            </button>
          )}
        </div>
      </div>

      {/* Configuration Switches (Before Exam Starts) */}
      {!examStarted && (
        <div className="p-5 rounded-2xl bg-[#020813] border border-slate-800 space-y-4">
          <div className="text-xs font-bold text-[#00F0B5] uppercase tracking-wider">
            Test Hall Configuration & Grading Policy
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            
            <div
              onClick={() => setNegativeMarking(!negativeMarking)}
              className={`p-3.5 rounded-xl border cursor-pointer transition-all flex items-center justify-between ${
                negativeMarking ? 'bg-emerald-950/40 border-emerald-500/50 text-white' : 'bg-slate-900 border-slate-800 text-slate-400'
              }`}
            >
              <div>
                <div className="font-bold">Negative Marking (GATE)</div>
                <div className="text-[10px] text-slate-400 mt-0.5">1/3 penalty per wrong MCQ</div>
              </div>
              <span className={`text-xs font-bold ${negativeMarking ? 'text-[#00F0B5]' : 'text-slate-500'}`}>
                {negativeMarking ? 'ON' : 'OFF'}
              </span>
            </div>

            <div
              onClick={() => setShuffleQuestions(!shuffleQuestions)}
              className={`p-3.5 rounded-xl border cursor-pointer transition-all flex items-center justify-between ${
                shuffleQuestions ? 'bg-emerald-950/40 border-emerald-500/50 text-white' : 'bg-slate-900 border-slate-800 text-slate-400'
              }`}
            >
              <div>
                <div className="font-bold">Question Shuffling</div>
                <div className="text-[10px] text-slate-400 mt-0.5">Randomize sequence order</div>
              </div>
              <span className={`text-xs font-bold ${shuffleQuestions ? 'text-[#00F0B5]' : 'text-slate-500'}`}>
                {shuffleQuestions ? 'ON' : 'OFF'}
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300">
              <div className="font-bold text-white">Target Candidate</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Ashok Kumar A (2023MITEC042)</div>
              <div className="text-[10px] text-emerald-400 mt-0.5">CO1-CO5 Outcome Tracking Active</div>
            </div>

          </div>
        </div>
      )}

      {/* ACTIVE EXAMINATION RUNNER */}
      {examStarted && !examSubmitted && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Main Question Workspace (8 cols) */}
          <div className="lg:col-span-8 space-y-4">
            
            {/* Section Tabs */}
            <div className="flex gap-2 border-b border-slate-800 pb-2 overflow-x-auto">
              {SECTIONS.map((sec, idx) => (
                <button
                  key={sec.id}
                  onClick={() => {
                    setActiveSection(sec.id);
                    setCurrentQIdx(0);
                  }}
                  className={`text-xs px-3 py-1.5 rounded-xl whitespace-nowrap transition-all ${
                    activeSection === sec.id
                      ? 'bg-gradient-to-r from-[#00693E] to-[#00b884] text-[#020813] font-bold shadow-emerald-glow'
                      : 'bg-[#020813] text-slate-400 hover:text-slate-200 border border-slate-800'
                  }`}
                >
                  {sec.title}
                </button>
              ))}
            </div>

            {/* Current Question Card */}
            {activeQuestion ? (
              <div className="p-6 rounded-2xl bg-[#020813] border border-[#00F0B5]/30 space-y-5">
                
                <div className="flex items-center justify-between pb-3 border-b border-slate-800 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white">Question #{currentQIdx + 1}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-500/20">
                      {activeQuestion.course_outcome}
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-500/20">
                      {activeQuestion.marks} Mark{activeQuestion.marks > 1 ? 's' : ''}
                    </span>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleToggleReview(activeQuestion.id)}
                    className={`text-[10px] px-2.5 py-1 rounded-lg border transition-all ${
                      reviewFlags[activeQuestion.id]
                        ? 'bg-amber-500 text-[#020813] font-bold border-amber-400'
                        : 'bg-slate-900 text-slate-400 border-slate-700 hover:text-white'
                    }`}
                  >
                    {reviewFlags[activeQuestion.id] ? '★ Marked for Review' : '☆ Mark for Review'}
                  </button>
                </div>

                {/* Statement */}
                <div className="text-sm font-sans text-slate-100 leading-relaxed">
                  {activeQuestion.question}
                </div>

                {/* Answer Options */}
                {activeQuestion.type === 'MCQ' ? (
                  <div className="space-y-2 pt-2">
                    {activeQuestion.options.map(opt => {
                      const isSelected = answers[activeQuestion.id] === opt.key;
                      return (
                        <div
                          key={opt.key}
                          onClick={() => handleAnswerSelect(activeQuestion.id, opt.key)}
                          className={`p-3.5 rounded-xl border cursor-pointer transition-all flex items-center gap-3 text-xs ${
                            isSelected
                              ? 'bg-emerald-950/60 border-emerald-400 text-white shadow-emerald-glow'
                              : 'bg-[#041026] border-slate-800 text-slate-300 hover:border-slate-700'
                          }`}
                        >
                          <span className={`w-6 h-6 rounded-lg flex items-center justify-center font-bold text-xs ${
                            isSelected ? 'bg-[#00F0B5] text-[#020813]' : 'bg-slate-800 text-slate-400'
                          }`}>
                            {opt.key}
                          </span>
                          <span className="font-sans">{opt.text}</span>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="pt-2 space-y-2">
                    <label className="text-xs text-slate-400 block">Enter Numerical Answer ({activeQuestion.unit}):</label>
                    <input
                      type="number"
                      step="any"
                      value={answers[activeQuestion.id] || ''}
                      onChange={(e) => handleAnswerSelect(activeQuestion.id, e.target.value)}
                      placeholder="e.g. 658.5"
                      className="w-full sm:w-64 px-4 py-2.5 rounded-xl bg-[#041026] border border-slate-700 focus:border-[#00F0B5] text-sm text-white font-mono focus:outline-none"
                    />
                    <span className="text-[10px] text-slate-500 block">Accepted tolerance: ±{activeQuestion.tolerance} {activeQuestion.unit}</span>
                  </div>
                )}

                {/* Bottom Navigation */}
                <div className="flex items-center justify-between pt-4 border-t border-slate-800 text-xs">
                  <button
                    type="button"
                    onClick={() => handleClearAnswer(activeQuestion.id)}
                    className="text-slate-400 hover:text-rose-400 text-[11px]"
                  >
                    Clear Response
                  </button>

                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      disabled={currentQIdx === 0}
                      onClick={() => setCurrentQIdx(prev => Math.max(0, prev - 1))}
                      className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 hover:bg-slate-800 disabled:opacity-40"
                    >
                      &larr; Prev
                    </button>
                    <button
                      type="button"
                      disabled={currentQIdx >= sectionQuestions.length - 1}
                      onClick={() => setCurrentQIdx(prev => Math.min(sectionQuestions.length - 1, prev + 1))}
                      className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 hover:bg-slate-800 disabled:opacity-40"
                    >
                      Next &rarr;
                    </button>
                  </div>
                </div>

              </div>
            ) : null}

          </div>

          {/* Question Palette HUD (4 cols) */}
          <div className="lg:col-span-4 space-y-4">
            <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-3">
              <div className="text-xs font-bold text-white flex items-center justify-between">
                <span>Question Palette</span>
                <span className="text-[10px] text-slate-400">{activeSection}</span>
              </div>

              {/* Status Legend */}
              <div className="grid grid-cols-2 gap-2 text-[10px] text-slate-400 pb-2 border-b border-slate-800">
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded bg-emerald-400"></span> Answered
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded bg-amber-400"></span> Review
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded bg-purple-400"></span> Ans & Rev
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded bg-slate-800"></span> Not Visited
                </div>
              </div>

              {/* Number Grid */}
              <div className="grid grid-cols-4 gap-2 pt-1">
                {sectionQuestions.map((q, idx) => {
                  const hasAnswer = answers[q.id] !== undefined && answers[q.id] !== '';
                  const isMarked = reviewFlags[q.id];
                  const isCurrent = idx === currentQIdx;

                  let bgClass = 'bg-slate-900 text-slate-400 border-slate-800';
                  if (hasAnswer && isMarked) bgClass = 'bg-purple-950 text-purple-300 border-purple-500 font-bold';
                  else if (hasAnswer) bgClass = 'bg-emerald-950 text-emerald-400 border-emerald-500 font-bold';
                  else if (isMarked) bgClass = 'bg-amber-950 text-amber-300 border-amber-500 font-bold';

                  return (
                    <button
                      key={q.id}
                      onClick={() => setCurrentQIdx(idx)}
                      className={`h-9 rounded-xl border text-xs flex items-center justify-center transition-all ${bgClass} ${
                        isCurrent ? 'ring-2 ring-[#00F0B5]' : ''
                      }`}
                    >
                      {idx + 1}
                    </button>
                  );
                })}
              </div>

            </div>
          </div>

        </div>
      )}

      {/* EVALUATION RESULTS & SCORE LEDGER */}
      {examSubmitted && evaluationResult && (
        <div className="space-y-6">
          
          {/* Main Score Card */}
          <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-emerald-950/50 via-[#041026] to-emerald-950/50 border border-emerald-500/50 shadow-emerald-glow flex flex-col sm:flex-row items-center justify-between gap-6">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-[#00F0B5] font-bold border border-[#00F0B5]/30">
                  Grade {evaluationResult.grade} (Passed)
                </span>
                <span className="text-xs text-slate-400">Scorecard: 2023MITEC042</span>
              </div>
              <div className="text-3xl sm:text-4xl font-extrabold text-white mt-1">
                {evaluationResult.netScore} <span className="text-lg text-slate-400">/ {evaluationResult.maxScore} Points</span>
                <span className="text-emerald-400 text-xl ml-3">({evaluationResult.percentage}%)</span>
              </div>
              <div className="text-xs text-slate-300 mt-1">
                {evaluationResult.rankBand} • Simulated Percentile: <span className="text-[#00F0B5] font-bold">{evaluationResult.percentile}%</span>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row items-center gap-3">
              <button
                type="button"
                onClick={handleCommitLedger}
                disabled={ledgerCommitted}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] font-bold text-xs uppercase tracking-wider hover:brightness-110 transition-all shadow-emerald-glow disabled:opacity-50"
              >
                {ledgerCommitted ? '✓ Ledger Committed' : 'Commit Grade (+180 XP)'}
              </button>
              <button
                type="button"
                onClick={handleStartExam}
                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:text-white text-xs border border-slate-700"
              >
                Retake Exam
              </button>
            </div>
          </div>

          {/* Course Outcome (CO1 - CO5) Radar / Bars */}
          <div className="p-6 rounded-2xl bg-[#020813] border border-slate-800 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-xs">
              <span className="font-bold text-white">Anna University Regulation 2023 Course Outcome Attainment</span>
              <span className="text-slate-400">NBA Tier-1 Criteria</span>
            </div>

            <div className="space-y-3">
              {Object.entries(evaluationResult.coAttainment).map(([coId, data]) => {
                const pct = data.total > 0 ? Math.round((data.earned / data.total) * 100) : 0;
                return (
                  <div key={coId} className="space-y-1 text-xs">
                    <div className="flex justify-between items-center text-[11px]">
                      <span className="text-slate-300">
                        <strong className="text-[#00F0B5]">{coId}:</strong> {data.name}
                      </span>
                      <span className="font-bold text-white">
                        {data.earned} / {data.total} pts ({pct}%)
                      </span>
                    </div>
                    <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-[#00693E] to-[#00F0B5] rounded-full transition-all duration-500"
                        style={{ width: `${pct}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Mistake Derivation Analysis */}
          {evaluationResult.mistakes.length > 0 && (
            <div className="p-6 rounded-2xl bg-[#020813] border border-rose-500/30 space-y-4">
              <div className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-2">
                <span>⚠ Mistake Derivations & Engineering Distractor Analysis</span>
                <span className="text-slate-400 font-normal">({evaluationResult.mistakes.length} errors)</span>
              </div>

              <div className="space-y-3">
                {evaluationResult.mistakes.map((m, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-[#041026] border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center text-slate-200">
                      <span className="font-bold">{m.title}</span>
                      <span className="text-rose-400 font-mono">Penalty: -{m.penalty} pts</span>
                    </div>
                    <div className="text-[11px] text-slate-400">
                      Your answer: <span className="text-rose-300 font-mono">{String(m.studentAns)}</span> | Correct: <span className="text-emerald-400 font-mono">{String(m.correctAns)}</span>
                    </div>
                    <div className="p-2.5 rounded bg-[#020813] text-[11px] text-slate-300 border border-slate-800/80">
                      <strong className="text-[#00F0B5]">Derivation:</strong> {m.derivation}
                    </div>
                    <div className="text-[10px] text-amber-300/90 italic">
                      Trap: {m.distractor}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>
      )}

    </div>
  );
}
