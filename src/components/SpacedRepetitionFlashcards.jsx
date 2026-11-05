import React, { useState, useEffect } from 'react';
import { triggerToast } from './ToastNotifications.jsx';

/**
 * ========================================================================================
 * VoltCore Apex Academia - SM-2 Spaced Repetition ECE Flashcards
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A (ashokkumar3132008@gmail.com)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Algorithm: SuperMemo-2 (SM-2) Interval Spacing
 * Features:
 *   - 3D perspective flip card animations
 *   - Register maps, hybrid-pi formulas, RISC-V hazard rules, and IEEE definitions
 *   - Daily retention analytics, ease-factor tracking, and XP progression
 * ========================================================================================
 */

const INITIAL_DECK = [
  // Category 1: ARM Cortex-M Registers
  {
    id: 'arm-01',
    category: 'ARM Cortex-M & STM32',
    difficulty: 'Apex Research',
    question: 'How do you trigger a PendSV context switch exception via direct register access in ARM Cortex-M4?',
    hint: 'Look at the System Control Block (SCB) Interrupt Control State Register (ICSR).',
    answer: 'Set bit 28 (PENDSVSET) of the SCB->ICSR register:\n\n```c\nSCB->ICSR |= SCB_ICSR_PENDSVSET_Msk; // (1UL << 28)\n```\nPendSV runs at the lowest interrupt priority (0xFF) to ensure all active ISRs complete before executing context switching.',
    formula: 'Priority(PendSV) = 0xFF \\quad (Lowest \\text{ priority for tail-chaining})',
    moduleRef: 'EC8706 (6-embedded-rtos.mdx)',
    repetitions: 0,
    interval: 1,
    easeFactor: 2.5,
    dueDate: new Date().toISOString(),
  },
  {
    id: 'arm-02',
    category: 'ARM Cortex-M & STM32',
    difficulty: 'Advanced',
    question: 'What is the required DMA register bit to enable circular ping-pong streaming on STM32F4?',
    hint: 'Inspect the Stream Control Register (DMA_SxCR).',
    answer: 'Assert bit 8 (CIRC) in `DMA_SxCR`:\n\n```c\nDMA2_Stream0->CR |= DMA_SxCR_CIRC;\n```\nCombined with Half-Transfer (`HTIE`) and Transfer-Complete (`TCIE`) interrupts, the controller circularly alternates buffers without CPU intervention.',
    formula: 'T_{\\text{half}} = \\frac{N/2}{f_s} \\quad [\\text{Buffer processing window}]',
    moduleRef: 'EC8708 (8-advanced-rtos-dma.mdx)',
    repetitions: 0,
    interval: 1,
    easeFactor: 2.5,
    dueDate: new Date().toISOString(),
  },

  // Category 2: Analog Electronics & Small-Signal Models
  {
    id: 'ana-01',
    category: 'Analog Hybrid-Pi Models',
    difficulty: 'Fundamental',
    question: 'State the closed-form equation for BJT small-signal transconductance (gm) at temperature T.',
    hint: 'Relate collector bias current IC to thermal voltage VT.',
    answer: '$$g_m = \\frac{I_C}{V_T} = \\frac{q I_C}{k T}$$\n\nAt room temperature ($T = 300\\text{ K}$), $V_T \\approx 25.86\\text{ mV}$. For $I_C = 1\\text{ mA}$, $g_m \\approx 38.66\\text{ mA/V}$ ($0.0387\\text{ \\Omega}^{-1}$).',
    formula: 'g_m = \\frac{I_C}{V_T} \\approx \\frac{I_C}{25.86\\text{ mV}}',
    moduleRef: 'EC8707 (7-analog-signal-integrity.mdx)',
    repetitions: 0,
    interval: 1,
    easeFactor: 2.5,
    dueDate: new Date().toISOString(),
  },
  {
    id: 'ana-02',
    category: 'Analog Hybrid-Pi Models',
    difficulty: 'Intermediate',
    question: 'Formulate the small-signal base-emitter input resistance (r_pi) in terms of beta and gm.',
    hint: 'Use small-signal base current ib = ic / beta.',
    answer: '$$r_\\pi = \\frac{\\beta}{g_m} = \\frac{\\beta V_T}{I_C}$$\n\nFor $\\beta = 100$ and $I_C = 1\\text{ mA}$, $r_\\pi = \\frac{100}{0.0387} \\approx 2.58\\text{ k\\Omega}$.',
    formula: 'r_\\pi = \\frac{\\beta}{g_m} = \\frac{\\beta V_T}{I_C}',
    moduleRef: 'EC8707 (7-analog-signal-integrity.mdx)',
    repetitions: 0,
    interval: 1,
    easeFactor: 2.5,
    dueDate: new Date().toISOString(),
  },

  // Category 3: RISC-V RV32I Processor Architecture
  {
    id: 'riscv-01',
    category: 'RISC-V RV32I Architecture',
    difficulty: 'Apex Research',
    question: 'What is the boolean forwarding condition for an EX-to-EX hazard on operand rs1 in a 5-stage pipeline?',
    hint: 'Check if EX/MEM destination matches ID/EX rs1 and register write is enabled.',
    answer: 'ForwardA = 2\'b10 when:\n\n```verilog\nif (ex_mem_reg_write && (ex_mem_rd != 5\'d0) && (ex_mem_rd == id_ex_rs1))\n    ForwardA = 2\'b10; // Forward from EX/MEM ALU output register\n```\nNote: `ex_mem_rd != 0` is required because register `x0` is hardwired to zero.',
    formula: '\\text{Hazard: } (\\text{ex\\_mem\\_rd} == \\text{id\\_ex\\_rs1}) \\land (\\text{ex\\_mem\\_rd} \\neq 0)',
    moduleRef: 'EC8705 (5-riscv-fpga.mdx)',
    repetitions: 0,
    interval: 1,
    easeFactor: 2.5,
    dueDate: new Date().toISOString(),
  },
  {
    id: 'riscv-02',
    category: 'RISC-V RV32I Architecture',
    difficulty: 'Advanced',
    question: 'Why cannot hardware forwarding eliminate the Load-Use RAW hazard stall?',
    hint: 'Consider the time axis of memory read vs ALU execute stages.',
    answer: 'A `lw` instruction only produces data at the end of the **MEM** stage. An immediately subsequent instruction requires data at the beginning of its **EX** stage.\n\nForwarding cannot travel backward in time! Therefore, the hazard detection unit must freeze PC and IF/ID and insert a **1-cycle pipeline bubble (NOP)**.',
    formula: '\\text{CPI Penalty: } +1 \\text{ cycle per load-use dependency}',
    moduleRef: 'EC8705 (5-riscv-fpga.mdx)',
    repetitions: 0,
    interval: 1,
    easeFactor: 2.5,
    dueDate: new Date().toISOString(),
  },

  // Category 4: FreeRTOS & Multi-Core
  {
    id: 'rtos-01',
    category: 'FreeRTOS & Multi-Core',
    difficulty: 'Intermediate',
    question: 'Distinguish between vTaskDelay() and vTaskDelayUntil() regarding cumulative drift.',
    hint: 'One delays relative to execution time; the other enforces an absolute periodic frequency.',
    answer: '• `vTaskDelay(n)` delays for $n$ ticks starting from when it is called. Execution time of task code causes **cumulative timing drift**.\n\n• `vTaskDelayUntil(&xLastWakeTime, period)` calculates delay relative to the exact scheduled wake-up epoch, guaranteeing **zero phase drift** over millions of cycles.',
    formula: 'T_{\\text{period}} = \\text{Exact Tick Interval} \\quad [\\text{Deterministic}]',
    moduleRef: 'EC8702 & EC8706 (6-embedded-rtos.mdx)',
    repetitions: 0,
    interval: 1,
    easeFactor: 2.5,
    dueDate: new Date().toISOString(),
  },

  // Category 5: IEEE Standards & RF Telemetry
  {
    id: 'rf-01',
    category: 'IEEE Standards & RF',
    difficulty: 'Advanced',
    question: 'State the Shannon-Hartley channel capacity theorem and explain its embedded IoT bandwidth limit.',
    hint: 'Relate bandwidth B and signal-to-noise ratio SNR.',
    answer: '$$C = B \\log_2(1 + \\text{SNR}) \\quad [\\text{bits per second}]$$\n\nUnder low-power LoRa links ($B = 125\\text{ kHz}$, $\\text{SNR} = -15\\text{ dB} = 0.0316$), the maximum theoretical capacity drops to:\n$$C = 125 \\times 10^3 \\times \\log_2(1.0316) \\approx 5.62\\text{ kbps}$$\nRequiring high Spreading Factors (SF10-SF12) to recover packets.',
    formula: 'C = B \\log_2\\left(1 + \\frac{S}{N}\\right)',
    moduleRef: 'EC8703 (3-defense-uav.mdx)',
    repetitions: 0,
    interval: 1,
    easeFactor: 2.5,
    dueDate: new Date().toISOString(),
  }
];

export default function SpacedRepetitionFlashcards() {
  const [deck, setDeck] = useState(INITIAL_DECK);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [reviewedTodayCount, setReviewedTodayCount] = useState(0);

  // Load saved SM-2 progress from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem('voltcore_sm2_deck');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setDeck(parsed);
        }
      }
    } catch (e) {
      console.log('Using default in-memory SM-2 deck');
    }
  }, []);

  // Filter deck by category
  const filteredDeck = selectedCategory === 'ALL'
    ? deck
    : deck.filter((c) => c.category === selectedCategory);

  const currentCard = filteredDeck[currentIndex] || filteredDeck[0];

  const categories = ['ALL', ...new Set(deck.map((c) => c.category))];

  // SuperMemo-2 (SM-2) Update Logic
  const handleGradeCard = (quality) => {
    if (!currentCard) return;

    let { repetitions, interval, easeFactor } = currentCard;

    // SM-2 Algorithm Implementation
    if (quality >= 3) {
      if (repetitions === 0) {
        interval = 1;
      } else if (repetitions === 1) {
        interval = 6;
      } else {
        interval = Math.round(interval * easeFactor);
      }
      repetitions += 1;
    } else {
      repetitions = 0;
      interval = 1;
    }

    // Ease Factor Adjustment: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    const qDiff = 5 - quality;
    easeFactor = easeFactor + (0.1 - qDiff * (0.08 + qDiff * 0.02));
    if (easeFactor < 1.3) easeFactor = 1.3;

    const nextDueDate = new Date();
    nextDueDate.setDate(nextDueDate.getDate() + interval);

    const updatedCard = {
      ...currentCard,
      repetitions,
      interval,
      easeFactor: Math.round(easeFactor * 100) / 100,
      dueDate: nextDueDate.toISOString(),
      lastReviewed: new Date().toISOString(),
    };

    const updatedDeck = deck.map((c) => (c.id === currentCard.id ? updatedCard : c));
    setDeck(updatedDeck);
    try {
      localStorage.setItem('voltcore_sm2_deck', JSON.stringify(updatedDeck));
    } catch (e) {}

    // Rewards & Feedback
    setReviewedTodayCount((prev) => prev + 1);
    setIsFlipped(false);
    setShowHint(false);

    // Advance to next card
    if (currentIndex + 1 < filteredDeck.length) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      setCurrentIndex(0);
    }

    triggerToast({
      type: 'xp',
      title: `SM-2 Spaced Recall Logged (Grade: ${quality}/5)`,
      message: `Next review interval: ${interval} day${interval > 1 ? 's' : ''} (EF: ${updatedCard.easeFactor}). +15 XP awarded!`,
      xp: 15,
      multiplier: '2.5x',
      duration: 3200,
    });
  };

  const handleNextCard = () => {
    setIsFlipped(false);
    setShowHint(false);
    setCurrentIndex((prev) => (prev + 1) % filteredDeck.length);
  };

  const handlePrevCard = () => {
    setIsFlipped(false);
    setShowHint(false);
    setCurrentIndex((prev) => (prev - 1 + filteredDeck.length) % filteredDeck.length);
  };

  return (
    <div className="w-full flex flex-col gap-6 font-sans">
      {/* Top Telemetry & Retention Analytics Deck */}
      <div className="p-5 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/25 backdrop-blur-xl shadow-glass flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-[#00F0B5] animate-ping"></span>
            <span className="text-[10px] font-mono font-bold tracking-widest text-[#00F0B5] uppercase bg-[#00693E]/30 px-2 py-0.5 rounded border border-[#00F0B5]/30">
              SM-2 Spaced Repetition Engine
            </span>
            <span className="text-xs font-mono text-slate-400">
              ECE Memory Retention Mastery
            </span>
          </div>
          <h2 className="text-lg md:text-xl font-bold text-slate-100">
            Hardware Register Maps & Analytical Formula Deck
          </h2>
        </div>

        {/* Retention HUD Counters */}
        <div className="flex items-center gap-4 font-mono text-xs">
          <div className="px-3 py-1.5 rounded-xl bg-[#020813] border border-slate-800 text-center">
            <div className="text-slate-500 text-[10px] uppercase">Mastered</div>
            <div className="text-[#00F0B5] font-bold text-sm">
              {deck.filter((c) => c.repetitions >= 2).length} / {deck.length}
            </div>
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-[#020813] border border-slate-800 text-center">
            <div className="text-slate-500 text-[10px] uppercase">Today's Drills</div>
            <div className="text-amber-400 font-bold text-sm">{reviewedTodayCount}</div>
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-[#020813] border border-slate-800 text-center">
            <div className="text-slate-500 text-[10px] uppercase">Avg Ease Factor</div>
            <div className="text-cyan-400 font-bold text-sm">
              {(deck.reduce((acc, c) => acc + c.easeFactor, 0) / deck.length).toFixed(2)}
            </div>
          </div>
        </div>
      </div>

      {/* Category Filter Pills */}
      <div className="flex flex-wrap items-center gap-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => {
              setSelectedCategory(cat);
              setCurrentIndex(0);
              setIsFlipped(false);
              setShowHint(false);
            }}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono transition-all ${
              selectedCategory === cat
                ? 'bg-[#00F0B5] text-[#020813] font-bold shadow-[0_0_15px_rgba(0,240,181,0.35)]'
                : 'bg-[#041026]/80 text-slate-400 border border-slate-800 hover:border-[#00F0B5]/40 hover:text-white'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Flashcard 3D Stage */}
      {currentCard && (
        <div className="w-full max-w-2xl mx-auto flex flex-col gap-4">
          <div className="w-full h-[420px] relative [perspective:1200px]">
            <div
              className={`w-full h-full relative [transform-style:preserve-3d] transition-transform duration-500 cursor-pointer ${
                isFlipped ? '[transform:rotateY(180deg)]' : ''
              }`}
              onClick={() => setIsFlipped(!isFlipped)}
            >
              {/* FRONT OF CARD */}
              <div className="absolute inset-0 w-full h-full rounded-2xl bg-[#041026] border border-[#00F0B5]/30 p-6 flex flex-col justify-between [backface-visibility:hidden] shadow-2xl overflow-hidden">
                {/* Glow accent */}
                <div className="absolute -top-20 -right-20 w-48 h-48 bg-[#00693E]/20 blur-3xl pointer-events-none" />

                <div>
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00693E]/30 text-[#00F0B5] border border-[#00F0B5]/25">
                      {currentCard.category}
                    </span>
                    <span className="text-xs font-mono text-slate-500">
                      Card {currentIndex + 1} of {filteredDeck.length}
                    </span>
                  </div>

                  <h3 className="text-base md:text-lg font-bold text-slate-100 leading-snug mt-2">
                    {currentCard.question}
                  </h3>

                  {showHint && (
                    <div className="mt-4 p-3 rounded-xl bg-[#020813] border border-amber-500/30 text-amber-300 text-xs font-mono leading-relaxed animate-in fade-in">
                      💡 <strong>Hint:</strong> {currentCard.hint}
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-slate-800 text-xs font-mono text-slate-400">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowHint(!showHint);
                    }}
                    className="text-amber-400 hover:text-amber-300 transition-colors"
                  >
                    {showHint ? 'Hide Hint' : '💡 Show Hint'}
                  </button>

                  <div className="text-slate-500 flex items-center gap-1">
                    <span>Click anywhere to flip</span>
                    <span className="text-[#00F0B5]">↻</span>
                  </div>
                </div>
              </div>

              {/* BACK OF CARD */}
              <div className="absolute inset-0 w-full h-full rounded-2xl bg-[#020813] border border-emerald-400/40 p-6 flex flex-col justify-between [transform:rotateY(180deg)] [backface-visibility:hidden] shadow-2xl overflow-y-auto">
                <div>
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      Analytical Solution & Bitfield Map
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      Ref: {currentCard.moduleRef}
                    </span>
                  </div>

                  {currentCard.formula && (
                    <div className="p-3 mb-3 rounded-xl bg-[#041026] border border-[#00F0B5]/30 text-center font-mono text-sm text-[#00F0B5]">
                      {currentCard.formula}
                    </div>
                  )}

                  <div className="text-xs text-slate-200 leading-relaxed font-sans whitespace-pre-wrap">
                    {currentCard.answer}
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800/80 text-[11px] font-mono text-slate-400 flex items-center justify-between">
                  <span>Interval: {currentCard.interval}d (EF: {currentCard.easeFactor})</span>
                  <span className="text-[#00F0B5]">Click to flip back ↻</span>
                </div>
              </div>
            </div>
          </div>

          {/* SM-2 Recall Quality Rating Controls */}
          {isFlipped ? (
            <div className="p-4 rounded-xl bg-[#041026]/90 border border-slate-800 flex flex-col gap-2 backdrop-blur-xl animate-in fade-in duration-200">
              <div className="text-xs font-mono text-slate-400 text-center">
                Rate your recall quality (SM-2 Interval Scheduling):
              </div>
              <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
                <button
                  onClick={() => handleGradeCard(0)}
                  className="px-2 py-2 rounded-lg bg-rose-950/40 border border-rose-500/30 hover:bg-rose-900/50 text-rose-300 text-xs font-mono transition-all text-center"
                >
                  <div className="font-bold text-sm">0</div>
                  <div className="text-[9px] text-slate-400">Blackout</div>
                </button>
                <button
                  onClick={() => handleGradeCard(1)}
                  className="px-2 py-2 rounded-lg bg-rose-950/20 border border-rose-500/20 hover:bg-rose-900/30 text-rose-300 text-xs font-mono transition-all text-center"
                >
                  <div className="font-bold text-sm">1</div>
                  <div className="text-[9px] text-slate-400">Fail</div>
                </button>
                <button
                  onClick={() => handleGradeCard(2)}
                  className="px-2 py-2 rounded-lg bg-amber-950/30 border border-amber-500/30 hover:bg-amber-900/40 text-amber-300 text-xs font-mono transition-all text-center"
                >
                  <div className="font-bold text-sm">2</div>
                  <div className="text-[9px] text-slate-400">Hard</div>
                </button>
                <button
                  onClick={() => handleGradeCard(3)}
                  className="px-2 py-2 rounded-lg bg-[#00693E]/30 border border-[#00F0B5]/30 hover:bg-[#00693E]/50 text-[#00F0B5] text-xs font-mono transition-all text-center"
                >
                  <div className="font-bold text-sm">3</div>
                  <div className="text-[9px] text-slate-400">Good</div>
                </button>
                <button
                  onClick={() => handleGradeCard(4)}
                  className="px-2 py-2 rounded-lg bg-emerald-950/40 border border-emerald-400/40 hover:bg-emerald-900/50 text-emerald-300 text-xs font-mono transition-all text-center"
                >
                  <div className="font-bold text-sm">4</div>
                  <div className="text-[9px] text-slate-400">Easy</div>
                </button>
                <button
                  onClick={() => handleGradeCard(5)}
                  className="px-2 py-2 rounded-lg bg-[#00F0B5]/20 border border-[#00F0B5] hover:bg-[#00F0B5]/30 text-[#00F0B5] text-xs font-mono transition-all text-center shadow-[0_0_10px_rgba(0,240,181,0.2)]"
                >
                  <div className="font-bold text-sm">5</div>
                  <div className="text-[9px] text-slate-300">Perfect</div>
                </button>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-between px-2 text-xs font-mono text-slate-400">
              <button
                onClick={handlePrevCard}
                className="px-4 py-2 rounded-xl bg-[#041026] border border-slate-800 hover:border-[#00F0B5]/40 text-slate-300 hover:text-white transition-all"
              >
                ← Previous Card
              </button>
              <button
                onClick={() => setIsFlipped(true)}
                className="px-5 py-2 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] font-bold shadow-emerald-glow transition-all"
              >
                Reveal Answer ↻
              </button>
              <button
                onClick={handleNextCard}
                className="px-4 py-2 rounded-xl bg-[#041026] border border-slate-800 hover:border-[#00F0B5]/40 text-slate-300 hover:text-white transition-all"
              >
                Next Card →
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

