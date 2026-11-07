import React, { useState, useEffect, useRef, useMemo } from 'react';
import { triggerToast } from './ToastNotifications.jsx';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Advanced Academic Examination Center & Viva Voce Simulator
 * Autonomous Engineering Cluster • Outcome-Based Education (OBE) • Bloom's Taxonomy
 * ----------------------------------------------------------------------------------------
 * Component: src/components/ExamSimulator.jsx
 * Platform Lead / Architect: Ashok Kumar A
 * 
 * Features:
 *   - Dual Mode: GATE ECE Examination Simulator & Technical Viva Voce Oral Simulator
 *   - Timed multi-section examination simulator with auto-submit countdown timer (20/45/90m)
 *   - Configurable GATE ECE negative marking mode (+1/-0.33, +2/-0.66) vs University zero penalty
 *   - Question palette HUD with filtering (All, Answered, Marked for Review, Unanswered)
 *   - Instantaneous evaluation against Anna University Regulation 2023 Course Outcomes (CO1-CO5)
 *   - Technical Viva Voce Voice & Oral assessment with Text-to-Speech & Bloom's Taxonomy rubrics
 *   - Automated mistake derivation analysis (+180 XP) and simulated percentile computation
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

// Phase 8: Core ECE / Embedded Technical Viva Voce Question Catalog
const VIVA_QUESTIONS = [
  {
    id: 'VIVA_01_NVIC_LATENCY',
    topic: 'ARM Cortex-M Interrupt Architecture & NVIC',
    question: 'Explain the architectural mechanisms contributing to ARM Cortex-M interrupt entry latency and how NVIC priority grouping differentiates preemption priority from subpriority.',
    bloom_level: 'Level 4: Analyze',
    max_marks: 10.0,
    key_concepts: [
      'stacking', '12 cycles', 'tail-chaining', 'late-arrival',
      'preemption priority', 'subpriority', 'aircr prigroup', 'nested'
    ],
    rubric: {
      core_depth: 5.0,
      keyword_precision: 3.0,
      clarity_and_insight: 2.0
    },
    model_answer: 'ARM Cortex-M4 features a deterministic 12-cycle interrupt latency achieved through automatic hardware stack framing of 8 registers (R0-R3, R12, LR, PC, xPSR) onto the current stack. Features like tail-chaining reduce latency to just 6 cycles between consecutive interrupts without redundant unstacking. The AIRCR PRIGROUP register divides the 8-bit priority field into preemption priority (which allows an incoming interrupt to immediately preempt an active ISR) and subpriority (which resolves simultaneous pending requests without preemption).'
  },
  {
    id: 'VIVA_02_I2C_STRETCHING',
    topic: 'I2C Physical Layer & Bus Recovery',
    question: 'Why does the I2C physical layer require open-drain output drivers with pull-up resistors, and what causes an I2C slave to perform clock stretching?',
    bloom_level: 'Level 3: Apply',
    max_marks: 10.0,
    key_concepts: [
      'open-drain', 'pull-up', 'wired-and', 'bus contention',
      'clock stretching', 'scl low', 'slow peripheral'
    ],
    rubric: {
      core_depth: 5.0,
      keyword_precision: 3.0,
      clarity_and_insight: 2.0
    },
    model_answer: 'I2C uses open-drain NMOS transistors paired with external pull-up resistors to create a wired-AND physical bus. This ensures electrical safety: if two masters drive simultaneously, zero short-circuit currents occur during multi-master arbitration. Clock stretching occurs when a slower slave device holds the SCL line LOW after an ACK bit to pause transmission while completing an internal operation, such as an ADC conversion or Flash write buffer flush. The master pauses until SCL is released.'
  },
  {
    id: 'VIVA_03_STA_METASTABILITY',
    topic: 'Static Timing Analysis (STA) & FPGA Timing Closure',
    question: 'Define Setup Time and Hold Time in synchronous flip-flops. Why cannot a hold-time violation be resolved by simply reducing the system clock frequency, and how must silicon designers fix it?',
    bloom_level: 'Level 4: Analyze',
    max_marks: 10.0,
    key_concepts: [
      'setup time', 'hold time', 'metastability', 'clock skew',
      'insert delay buffers', 'independent of clock period', 't_co + t_logic >= t_hold'
    ],
    rubric: {
      core_depth: 5.0,
      keyword_precision: 3.0,
      clarity_and_insight: 2.0
    },
    model_answer: 'Setup time (T_su) is the minimum time data must remain stable before the active clock edge; hold time (T_h) is the minimum duration data must remain stable after the clock edge to prevent internal flip-flop metastability. Setup slack depends on clock period (T_clk - T_crit), so reducing clock frequency fixes setup violations. However, hold time is evaluated on the exact same clock edge (T_co + T_logic >= T_h + T_skew) and is completely independent of clock frequency. A hold violation means data changed too quickly and can only be resolved by inserting delay buffers or routing delay into the short data path.'
  },
  {
    id: 'VIVA_04_FREERTOS_PENDSV',
    topic: 'SysTick & PendSV Real-Time Context Switching',
    question: 'In FreeRTOS on Cortex-M, why does the kernel defer task context switching to the PendSV exception rather than performing it directly inside the SysTick interrupt service routine?',
    bloom_level: 'Level 5: Evaluate',
    max_marks: 10.0,
    key_concepts: [
      'pendsv lowest priority', 'systick', 'context switch', 'interrupt preemption',
      'prevent nesting', 'msp to psp', 'tail-chaining'
    ],
    rubric: {
      core_depth: 5.0,
      keyword_precision: 3.0,
      clarity_and_insight: 2.0
    },
    model_answer: 'If a context switch were performed directly inside the SysTick ISR while a higher-priority hardware ISR (such as a motor control PWM or UART DMA handler) was preempted, the task context switch would corrupt or delay time-critical ISR execution. FreeRTOS solves this by setting PendSV to the absolute lowest priority (0xFF). SysTick sets the PendSV bit; ARM hardware waits until all higher-priority ISRs finish executing, and only then executes PendSV to safely swap Process Stack Pointers (PSP) and Task Control Blocks (TCB) without delaying hardware interrupts.'
  },
  {
    id: 'VIVA_05_ADC_DMA_STREAMING',
    topic: 'SAR ADC Calibration, Sampling Time & DMA Overrun',
    question: 'How does source signal impedance affect the required SAR ADC sampling time, and how does circular double-buffering with Half-Transfer interrupts prevent telemetry buffer overrun?',
    bloom_level: 'Level 4: Analyze',
    max_marks: 10.0,
    key_concepts: [
      'sampling capacitor', 'input impedance', 'rc charging time',
      'circular buffer', 'half-transfer interrupt', 'transfer-complete', 'overrun'
    ],
    rubric: {
      core_depth: 5.0,
      keyword_precision: 3.0,
      clarity_and_insight: 2.0
    },
    model_answer: 'The SAR ADC sampling capacitor (typically 5-10 pF) requires a sufficient sampling period (T_sample = k * (R_src + R_switch) * C_sample) to charge within 1/2 LSB accuracy. High source impedance increases RC charging time, leading to gain and linearity errors if sampling cycles are too short. In circular DMA mode, the DMA controller continuously writes conversions to a RAM buffer. Triggering a Half-Transfer (HT) interrupt allows CPU DSP processing on the first half while DMA fills the second half, and Transfer-Complete (TC) processes the second half while DMA re-fills the first, completely preventing buffer overrun without lock contention.'
  }
];

export default function ExamSimulator() {
  // Top-level simulator mode: 'gate_exam' or 'viva_voce'
  const [simulatorMode, setSimulatorMode] = useState('gate_exam');

  // ==========================================
  // GATE ECE EXAM STATE
  // ==========================================
  const [examStarted, setExamStarted] = useState(false);
  const [examSubmitted, setExamSubmitted] = useState(false);
  const [activeSection, setActiveSection] = useState('sec_analog');
  const [currentQIdx, setCurrentQIdx] = useState(0);

  // Configuration options
  const [negativeMarking, setNegativeMarking] = useState(true);
  const [shuffleQuestions, setShuffleQuestions] = useState(false);
  const [selectedDuration, setSelectedDuration] = useState(20); // 20, 45, or 90 minutes
  const [timeRemaining, setTimeRemaining] = useState(1200); // in seconds
  const [isTimerPaused, setIsTimerPaused] = useState(false);
  const [paletteFilter, setPaletteFilter] = useState('ALL'); // 'ALL' | 'ANSWERED' | 'REVIEW' | 'UNANSWERED'

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

  // Global Countdown Timer for GATE Exam
  useEffect(() => {
    if (simulatorMode !== 'gate_exam' || !examStarted || examSubmitted || isTimerPaused) return;

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
  }, [simulatorMode, examStarted, examSubmitted, isTimerPaused]);

  const handleStartExam = () => {
    setExamStarted(true);
    setExamSubmitted(false);
    setTimeRemaining(selectedDuration * 60);
    setAnswers({});
    setReviewFlags({});
    setEvaluationResult(null);
    setLedgerCommitted(false);
    setCurrentQIdx(0);
    triggerToast({
      title: 'Examination Commenced',
      message: `Timer started: ${selectedDuration} minutes. Negative marking mode: ${negativeMarking ? 'ENABLED (1/3 deduction)' : 'DISABLED'}`,
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
    const rankBand = percentage >= 85 ? 'AIR 1 - 25 (Autonomous Cluster Honors)' : percentage >= 70 ? 'AIR 26 - 150 (Top Decile)' : 'GATE Qualified';

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

    // Sync non-blocking with backend evaluator if running
    try {
      fetch('/api/exam/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          questions: questionPool,
          answers: answers,
          enable_negative_marking: negativeMarking,
          student_id: 'STUDENT_LEAD_042'
        })
      }).catch(() => {});
    } catch (_) {}

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

  // ==========================================
  // VIVA VOCE SIMULATOR STATE
  // ==========================================
  const [selectedVivaId, setSelectedVivaId] = useState('VIVA_01_NVIC_LATENCY');
  const [vivaResponseText, setVivaResponseText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isEvaluatingViva, setIsEvaluatingViva] = useState(false);
  const [vivaResult, setVivaResult] = useState(null);
  const [vivaHistory, setVivaHistory] = useState([]);
  const [showModelAnswer, setShowModelAnswer] = useState(false);
  const recognitionRef = useRef(null);

  const activeVivaQuestion = useMemo(() => {
    return VIVA_QUESTIONS.find(q => q.id === selectedVivaId) || VIVA_QUESTIONS[0];
  }, [selectedVivaId]);

  // Read question aloud via Web Speech API
  const handleSpeakQuestion = (text) => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.95;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
      triggerToast({
        title: 'Voice Synthesizer Active',
        message: 'Reading viva question aloud through speech synthesis...',
        type: 'info',
        category: 'academic'
      });
    } else {
      triggerToast({
        title: 'Speech Synthesis Unavailable',
        message: 'Browser speech synthesis API not supported or permitted in this environment.',
        type: 'warning',
        category: 'academic'
      });
    }
  };

  // Toggle voice dictation (SpeechRecognition or simulated fallback)
  const handleToggleVoiceInput = () => {
    if (typeof window === 'undefined') return;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      triggerToast({
        title: 'Voice Input Mode',
        message: 'SpeechRecognition API not detected in browser; please type your response in the editor.',
        type: 'info',
        category: 'academic'
      });
      return;
    }

    if (isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
      triggerToast({
        title: 'Dictation Paused',
        message: 'Microphone stream stopped.',
        type: 'info',
        category: 'telemetry'
      });
    } else {
      try {
        const recog = new SpeechRecognition();
        recog.continuous = true;
        recog.interimResults = true;
        recog.lang = 'en-US';
        recog.onresult = (evt) => {
          let transcript = '';
          for (let i = evt.resultIndex; i < evt.results.length; i++) {
            transcript += evt.results[i][0].transcript;
          }
          setVivaResponseText(prev => prev ? `${prev} ${transcript}` : transcript);
        };
        recog.onerror = () => setIsListening(false);
        recog.onend = () => setIsListening(false);
        recog.start();
        recognitionRef.current = recog;
        setIsListening(true);
        triggerToast({
          title: 'Microphone Live',
          message: 'Speak clearly into your microphone to dictate your oral response...',
          type: 'success',
          category: 'telemetry'
        });
      } catch (err) {
        setIsListening(false);
      }
    }
  };

  // Local fallback evaluation for Viva Voce
  const evaluateVivaLocally = (question, studentText) => {
    const norm = (studentText || '').toLowerCase();
    const words = norm.trim().split(/\s+/).filter(Boolean);
    const matched = [];
    const missing = [];
    for (const kc of question.key_concepts) {
      if (norm.includes(kc.toLowerCase())) {
        matched.push(kc);
      } else {
        missing.push(kc);
      }
    }
    const ratio = question.key_concepts.length > 0 ? (matched.length / question.key_concepts.length) : 0;
    const keywordPrecision = Number((ratio * question.rubric.keyword_precision).toFixed(1));
    let depth = 1.0;
    if (words.length >= 60 && ratio >= 0.6) depth = question.rubric.core_depth;
    else if (words.length >= 35 && ratio >= 0.4) depth = 3.5;
    else if (words.length >= 20) depth = 2.5;

    let clarity = 1.0;
    if (words.length >= 25 && matched.length >= 2) clarity = question.rubric.clarity_and_insight;

    const totalScore = Number(Math.min(question.max_marks, depth + keywordPrecision + clarity).toFixed(1));
    const pct = Math.round((totalScore / question.max_marks) * 100);

    let bloomStatus = 'NEEDS_REVISION';
    if (pct >= 85) bloomStatus = `MASTERED (${question.bloom_level})`;
    else if (pct >= 65) bloomStatus = `PROFICIENT (${question.bloom_level})`;
    else if (pct >= 50) bloomStatus = `DEVELOPING (${question.bloom_level})`;

    return {
      status: 'SUCCESS',
      question_id: question.id,
      topic: question.topic,
      bloom_level: question.bloom_level,
      bloom_status: bloomStatus,
      score: totalScore,
      max_marks: question.max_marks,
      percentage: pct,
      breakdown: {
        core_depth: depth,
        keyword_precision: keywordPrecision,
        clarity_and_insight: clarity
      },
      matched_concepts: matched,
      missing_concepts: missing,
      feedback: ratio >= 0.7
        ? `Exceptional technical articulation! Rigorous coverage of ${matched.slice(0, 4).join(', ')}.`
        : `Good attempt. Strengthen oral explanations by explicitly addressing: ${missing.slice(0, 3).join(', ')}.`,
      model_answer: question.model_answer
    };
  };

  // Submit Viva Oral Answer
  const handleEvaluateViva = async () => {
    if (!vivaResponseText.trim()) {
      triggerToast({
        title: 'Empty Response',
        message: 'Please provide or dictate your oral answer before evaluation.',
        type: 'warning',
        category: 'academic'
      });
      return;
    }

    setIsEvaluatingViva(true);
    let evalOutput = null;

    try {
      const resp = await fetch('/api/viva/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_id: activeVivaQuestion.id,
          student_answer: vivaResponseText,
          student_id: 'STUDENT_LEAD_042'
        })
      });

      if (resp.ok) {
        const data = await resp.json();
        if (data.status === 'SUCCESS' && data.evaluation) {
          evalOutput = data.evaluation;
        }
      }
    } catch (_) {
      // Backend offline: use deterministic local evaluation
    }

    if (!evalOutput) {
      evalOutput = evaluateVivaLocally(activeVivaQuestion, vivaResponseText);
    }

    setIsEvaluatingViva(false);
    setVivaResult(evalOutput);
    setShowModelAnswer(false);
    setVivaHistory(prev => [evalOutput, ...prev.slice(0, 9)]);

    triggerToast({
      title: 'Viva Voce Evaluated',
      message: `Score: ${evalOutput.score}/${evalOutput.max_marks} (${evalOutput.percentage}%). Status: ${evalOutput.bloom_status}`,
      type: evalOutput.percentage >= 65 ? 'success' : 'info',
      category: 'academic'
    });
  };

  return (
    <div className="rounded-3xl border border-[#00F0B5]/30 bg-gradient-to-br from-[#020813] via-[#041026] to-[#020813] p-6 sm:p-8 font-mono text-slate-100 shadow-2xl space-y-6">
      
      {/* Top Banner & Mode Switcher */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-[#00F0B5] border border-[#00F0B5]/30 font-bold uppercase tracking-wider">
              Autonomous Engineering Cluster
            </span>
            <span className="text-xs text-slate-400">Regulation 2023 Mock Hall & Viva Voce</span>
          </div>
          <h2 className="text-lg sm:text-xl font-bold text-white mt-1">
            {simulatorMode === 'gate_exam' ? 'Advanced Electronics Examination Simulator' : 'Technical Viva Voce & Oral Assessment Simulator'}
          </h2>
        </div>

        {/* Simulator Mode Tabs */}
        <div className="flex items-center gap-2 bg-[#020813] p-1 rounded-2xl border border-slate-800">
          <button
            type="button"
            onClick={() => setSimulatorMode('gate_exam')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
              simulatorMode === 'gate_exam'
                ? 'bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] shadow-emerald-glow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            📝 GATE ECE Simulator
          </button>
          <button
            type="button"
            onClick={() => setSimulatorMode('viva_voce')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
              simulatorMode === 'viva_voce'
                ? 'bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] shadow-emerald-glow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            🎙️ Technical Viva Voce
          </button>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* MODE 1: GATE ECE EXAMINATION SIMULATOR */}
      {/* ========================================================================= */}
      {simulatorMode === 'gate_exam' && (
        <div className="space-y-6">
          
          {/* Action / Mode Badges */}
          <div className="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-slate-800/60">
            <div className="flex items-center gap-3">
              {examStarted && !examSubmitted && (
                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border ${
                  timeRemaining < 180
                    ? 'bg-rose-950/80 border-rose-500 text-rose-300 animate-pulse'
                    : 'bg-[#020813] border-slate-700 text-slate-200'
                }`}>
                  <svg className="w-4 h-4 text-[#00F0B5]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
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
                  Start {selectedDuration}-Min Exam
                </button>
              )}
            </div>

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

          {/* Configuration Switches (Before Exam Starts) */}
          {!examStarted && (
            <div className="p-5 rounded-2xl bg-[#020813] border border-slate-800 space-y-4">
              <div className="text-xs font-bold text-[#00F0B5] uppercase tracking-wider">
                Test Hall Configuration & Grading Policy
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs">
                
                {/* Duration Selector */}
                <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 space-y-1.5">
                  <div className="font-bold text-white">Exam Duration</div>
                  <div className="flex gap-1.5 pt-1">
                    {[20, 45, 90].map(dur => (
                      <button
                        key={dur}
                        type="button"
                        onClick={() => setSelectedDuration(dur)}
                        className={`px-2 py-1 rounded text-[11px] font-bold transition-all ${
                          selectedDuration === dur
                            ? 'bg-[#00F0B5] text-[#020813]'
                            : 'bg-slate-800 text-slate-400 hover:text-white'
                        }`}
                      >
                        {dur}m
                      </button>
                    ))}
                  </div>
                </div>

                {/* Negative Marking */}
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

                {/* Shuffling */}
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

                {/* Candidate Info */}
                <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300">
                  <div className="font-bold text-white">Target Candidate</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Ashok Kumar A (Candidate 042)</div>
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
                  {SECTIONS.map((sec) => (
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

                  {/* Filter Pills */}
                  <div className="flex gap-1 overflow-x-auto pb-1 text-[10px]">
                    {[
                      { id: 'ALL', label: 'All' },
                      { id: 'ANSWERED', label: 'Answered' },
                      { id: 'REVIEW', label: 'Review' },
                      { id: 'UNANSWERED', label: 'Unanswered' }
                    ].map(f => (
                      <button
                        key={f.id}
                        type="button"
                        onClick={() => setPaletteFilter(f.id)}
                        className={`px-2 py-0.5 rounded-md font-bold transition-all ${
                          paletteFilter === f.id
                            ? 'bg-[#00F0B5]/20 text-[#00F0B5] border border-[#00F0B5]/40'
                            : 'bg-slate-900 text-slate-400 hover:text-white'
                        }`}
                      >
                        {f.label}
                      </button>
                    ))}
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

                      // Check filter
                      if (paletteFilter === 'ANSWERED' && !hasAnswer) return null;
                      if (paletteFilter === 'REVIEW' && !isMarked) return null;
                      if (paletteFilter === 'UNANSWERED' && hasAnswer) return null;

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
                    <span className="text-xs text-slate-400">Scorecard: Candidate 042</span>
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

              {/* Course Outcome (CO1 - CO5) Attainment Bars */}
              <div className="p-6 rounded-2xl bg-[#020813] border border-slate-800 space-y-4">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-xs">
                  <span className="font-bold text-white">Course Outcome Attainment</span>
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
      )}

      {/* ========================================================================= */}
      {/* MODE 2: TECHNICAL VIVA VOCE & ORAL ASSESSMENT SIMULATOR */}
      {/* ========================================================================= */}
      {simulatorMode === 'viva_voce' && (
        <div className="space-y-6">
          
          {/* Question Selector Carousel / Tabs */}
          <div className="space-y-2">
            <label className="text-xs text-slate-400 uppercase tracking-wider font-bold">Select Viva Voce Inquiry Topic:</label>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-2">
              {VIVA_QUESTIONS.map(vq => (
                <button
                  key={vq.id}
                  type="button"
                  onClick={() => {
                    setSelectedVivaId(vq.id);
                    setVivaResult(null);
                    setVivaResponseText('');
                    setShowModelAnswer(false);
                  }}
                  className={`p-3 rounded-2xl border text-left transition-all ${
                    selectedVivaId === vq.id
                      ? 'bg-emerald-950/60 border-[#00F0B5] text-white shadow-emerald-glow'
                      : 'bg-[#020813] border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <div className="text-[10px] text-[#00F0B5] font-bold truncate">{vq.bloom_level}</div>
                  <div className="text-xs font-bold text-white mt-1 line-clamp-1">{vq.topic}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Active Question Display Card */}
          <div className="p-6 rounded-3xl bg-[#020813] border border-[#00F0B5]/30 space-y-4 shadow-xl">
            <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800 text-xs">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-500/30 text-[10px] font-bold">
                  {activeVivaQuestion.bloom_level}
                </span>
                <span className="font-bold text-white text-sm">
                  {activeVivaQuestion.topic}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] text-amber-400 font-bold">Max: {activeVivaQuestion.max_marks} pts</span>
                <button
                  type="button"
                  onClick={() => handleSpeakQuestion(activeVivaQuestion.question)}
                  className="px-3 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-[#00F0B5] text-xs font-bold flex items-center gap-1.5 transition-all"
                >
                  <span>🔊</span> Read Aloud
                </button>
              </div>
            </div>

            <p className="text-sm font-sans text-slate-100 leading-relaxed">
              {activeVivaQuestion.question}
            </p>

            <div className="flex flex-wrap gap-1.5 pt-1">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mr-1">Rubric Criteria:</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                Core Depth: {activeVivaQuestion.rubric.core_depth}m
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                Keyword Precision: {activeVivaQuestion.rubric.keyword_precision}m
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                Clarity: {activeVivaQuestion.rubric.clarity_and_insight}m
              </span>
            </div>
          </div>

          {/* Student Oral / Written Response Area */}
          <div className="p-6 rounded-3xl bg-[#020813] border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <span>Your Verbal / Technical Response</span>
                {isListening && (
                  <span className="flex items-center gap-1.5 text-rose-400 text-[10px] animate-pulse">
                    <span className="w-2 h-2 rounded-full bg-rose-500"></span> Recording Voice...
                  </span>
                )}
              </div>
              <button
                type="button"
                onClick={handleToggleVoiceInput}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${
                  isListening
                    ? 'bg-rose-600 text-white animate-pulse shadow-rose-glow'
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                }`}
              >
                <span>🎙️</span> {isListening ? 'Stop Recording' : 'Voice Dictate'}
              </button>
            </div>

            <textarea
              rows={5}
              value={vivaResponseText}
              onChange={(e) => setVivaResponseText(e.target.value)}
              placeholder="Dictate or type your technical engineering response here. Address physical layer dynamics, registers, timing budgets, or architectural mechanisms..."
              className="w-full p-4 rounded-2xl bg-[#041026] border border-slate-700 focus:border-[#00F0B5] text-sm text-slate-100 font-mono focus:outline-none leading-relaxed resize-y"
            />

            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-2">
              <div className="text-[11px] text-slate-400">
                Word Count: <span className="text-white font-bold">{vivaResponseText.trim().split(/\s+/).filter(Boolean).length}</span> words
                <span className="ml-2 text-slate-500">(Aim for 35+ words with specific hardware registers & mechanisms)</span>
              </div>

              <button
                type="button"
                disabled={isEvaluatingViva || !vivaResponseText.trim()}
                onClick={handleEvaluateViva}
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] font-bold text-xs uppercase tracking-wider hover:brightness-110 transition-all shadow-emerald-glow disabled:opacity-40"
              >
                {isEvaluatingViva ? 'Evaluating...' : '⚡ Evaluate Oral Response'}
              </button>
            </div>
          </div>

          {/* VIVA EVALUATION REPORT */}
          {vivaResult && (
            <div className="space-y-6">
              
              {/* Scorecard Header */}
              <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-emerald-950/40 via-[#041026] to-emerald-950/40 border border-emerald-500/40 shadow-emerald-glow flex flex-col sm:flex-row items-center justify-between gap-6">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-[#00F0B5] font-bold border border-[#00F0B5]/30">
                      {vivaResult.bloom_status}
                    </span>
                    <span className="text-xs text-slate-400">Oral Assessment Evaluation</span>
                  </div>
                  <div className="text-3xl sm:text-4xl font-extrabold text-white mt-1">
                    {vivaResult.score} <span className="text-lg text-slate-400">/ {vivaResult.max_marks} Points</span>
                    <span className="text-emerald-400 text-xl ml-3">({vivaResult.percentage}%)</span>
                  </div>
                  <p className="text-xs text-slate-300 mt-2 font-sans">
                    {vivaResult.feedback}
                  </p>
                </div>

                <div className="flex flex-col gap-2 w-full sm:w-auto">
                  <button
                    type="button"
                    onClick={() => setShowModelAnswer(!showModelAnswer)}
                    className="px-4 py-2 rounded-xl bg-slate-800 text-slate-200 hover:text-white text-xs border border-slate-700 transition-all"
                  >
                    {showModelAnswer ? 'Hide Model Answer' : 'View Model Answer'}
                  </button>
                </div>
              </div>

              {/* Rubric Breakdown Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-1">
                  <div className="text-xs text-slate-400">Core Technical Depth</div>
                  <div className="text-xl font-bold text-white">
                    {vivaResult.breakdown?.core_depth ?? 0} <span className="text-xs text-slate-500">/ {activeVivaQuestion.rubric.core_depth}</span>
                  </div>
                  <div className="text-[10px] text-emerald-400">Physical mechanisms & silicon architecture</div>
                </div>

                <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-1">
                  <div className="text-xs text-slate-400">Keyword Precision</div>
                  <div className="text-xl font-bold text-white">
                    {vivaResult.breakdown?.keyword_precision ?? 0} <span className="text-xs text-slate-500">/ {activeVivaQuestion.rubric.keyword_precision}</span>
                  </div>
                  <div className="text-[10px] text-emerald-400">Exact technical terminology & registers</div>
                </div>

                <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-1">
                  <div className="text-xs text-slate-400">Articulation & Clarity</div>
                  <div className="text-xl font-bold text-white">
                    {vivaResult.breakdown?.clarity_and_insight ?? 0} <span className="text-xs text-slate-500">/ {activeVivaQuestion.rubric.clarity_and_insight}</span>
                  </div>
                  <div className="text-[10px] text-emerald-400">Cohesive cause-and-effect reasoning</div>
                </div>
              </div>

              {/* Keyword Coverage Details */}
              <div className="p-5 rounded-2xl bg-[#020813] border border-slate-800 space-y-3">
                <div className="text-xs font-bold text-white">Concept Verification Breakdown:</div>
                <div className="flex flex-wrap gap-2">
                  {vivaResult.matched_concepts && vivaResult.matched_concepts.map((kc, i) => (
                    <span key={i} className="text-xs px-2.5 py-1 rounded-lg bg-emerald-950 text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
                      <span>✓</span> {kc}
                    </span>
                  ))}
                  {vivaResult.missing_concepts && vivaResult.missing_concepts.map((kc, i) => (
                    <span key={i} className="text-xs px-2.5 py-1 rounded-lg bg-rose-950/60 text-rose-300 border border-rose-500/40 flex items-center gap-1">
                      <span>✗</span> {kc}
                    </span>
                  ))}
                </div>
              </div>

              {/* Model Engineering Answer (Collapsible) */}
              {showModelAnswer && (
                <div className="p-6 rounded-2xl bg-[#041026] border border-[#00F0B5]/40 space-y-3">
                  <div className="text-xs font-bold text-[#00F0B5] uppercase tracking-wider flex items-center gap-2">
                    <span>💡 Model Engineering Answer & Architectural Derivation</span>
                  </div>
                  <p className="text-xs font-sans text-slate-200 leading-relaxed bg-[#020813] p-4 rounded-xl border border-slate-800">
                    {vivaResult.model_answer || activeVivaQuestion.model_answer}
                  </p>
                </div>
              )}

            </div>
          )}

          {/* Past Viva History Log */}
          {vivaHistory.length > 0 && (
            <div className="p-5 rounded-2xl bg-[#020813] border border-slate-800 space-y-3">
              <div className="text-xs font-bold text-slate-300 uppercase tracking-wider">Recent Viva Attempts Log:</div>
              <div className="space-y-2">
                {vivaHistory.map((item, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                    <div>
                      <span className="font-bold text-white">{item.topic}</span>
                      <span className="text-[10px] text-slate-400 ml-2">({item.bloom_level})</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-emerald-400 font-bold">{item.score} / {item.max_marks} pts</span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300">{item.percentage}%</span>
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
