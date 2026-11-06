import React, { useState } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Phase B: ECE Textbook Reader & Datasheet Library
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 * 
 * Features:
 *   - Feature 211: Interactive ECE Textbook & Curriculum Chapter Reader
 *   - Feature 212: Bookmark Manager with Section Offsets
 *   - Feature 213: PDF & Markdown Annotation Workspace
 *   - Feature 214: Component Specification Comparison Table (MCU / Silicon)
 *   - Feature 215: Technical Block & Circuit Diagram Library Viewer
 * ========================================================================================
 */

const TEXTBOOKS = [
  {
    id: "cortex_m_guide",
    title: "Definitive Guide to ARM Cortex-M3/M4",
    author: "Joseph Yiu",
    course: "EC8702 Embedded Systems",
    color: "#00F0B5",
    chapters: [
      {
        id: "ch1_arch",
        num: 1,
        title: "Cortex-M4 Architecture & Harvard Bus Matrix",
        readTime: "25m",
        equations: [
            "Interrupt Latency = T_detect + T_stack_push (12 cycles) + T_vector_fetch (6 cycles)",
            "Tail-chaining latency = 6 cycles (skips register pop/push)"
        ],
        body: `### 1. Cortex-M4 Core Architecture

The ARM Cortex-M4 is a high-performance 32-bit RISC core featuring Harvard architecture with separate ICode, DCode, and System buses. It integrates hardware single-cycle MAC instructions and IEEE 754 single-precision FPU.

#### 1.1 Dual Stack Pointers: MSP vs PSP
- **MSP (Main Stack Pointer):** Default stack used during reset and Exception/Interrupt handlers.
- **PSP (Process Stack Pointer):** Used exclusively by RTOS tasks during Thread Mode execution to isolate task stack overruns from kernel memory.

\`\`\`c
// Assembly check for active stack pointer
__asm volatile (
    "mrs r0, CONTROL   \\n"
    "tst r0, #2        \\n"
    "ite eq            \\n"
    "mrseq r0, msp     \\n"
    "mrsne r0, psp     \\n"
);
\`\`\``
      },
      {
        id: "ch2_nvic",
        num: 2,
        title: "NVIC Priority Grouping & Tail-Chaining",
        readTime: "30m",
        equations: [
            "PRIGROUP[10:8]: Split into Preemption Bits [7:x] and Subpriority Bits [x-1:0]",
            "Tail-chaining latency saving = 12 cycles"
        ],
        body: `### 2. Nested Vectored Interrupt Controller (NVIC)

The NVIC supports up to 240 external physical interrupts with 8 to 256 programmable priority levels. The hardware automatically pushes R0-R3, R12, LR, PC, and xPSR onto the active stack when an exception occurs.

#### 2.1 Late-Arrival & Tail-Chaining
When a higher-priority interrupt arrives during stack-push of a lower-priority interrupt, the NVIC executes late-arrival preemption without resetting stack state. In tail-chaining, consecutive ISRs execute with only 6 cycles overhead.`
      },
      {
        id: "ch3_dma",
        num: 3,
        title: "Direct Memory Access (DMA) & Zero-Copy Streams",
        readTime: "28m",
        equations: [
            "Throughput = Bus Clock * Bus Width * (1 - Contention Loss)"
        ],
        body: `### 3. Direct Memory Access (DMA)

DMA relieves the CPU core from bulk data transfers between high-speed peripherals (ADC, SPI, UART) and SRAM. Circular mode automatically wraps buffer pointers upon reaching buffer boundaries.`
      }
    ]
  },
  {
    id: "sedra_smith_circuits",
    title: "Microelectronic Circuits (Sedra & Smith)",
    author: "Adel S. Sedra & Kenneth C. Smith",
    course: "EC3452 Analog ICs",
    color: "#F97316",
    chapters: [
      {
        id: "ch1_opamp",
        num: 1,
        title: "Op-Amp Miller Frequency Compensation & Pole-Splitting",
        readTime: "35m",
        equations: [
            "Dominant Pole: p1' = 1 / (gm2 * R1 * R2 * Cc)",
            "Non-Dominant Pole: p2' = gm2 / C2",
            "Unity-Gain Bandwidth: ft = gm1 / (2 * pi * Cc)"
        ],
        body: `### 1. Two-Stage CMOS Op-Amp Frequency Response

Connecting compensation capacitor Cc across the high-gain inverting second stage introduces pole-splitting. This pushes the dominant pole to a very low frequency while shoving the second pole far beyond the unity-gain frequency ft, securing phase margin > 60 degrees.

#### 1.2 Derivation of Phase Margin
Phase margin must exceed 60 degrees to prevent step-response ringing and unstable closed-loop oscillation in negative feedback configurations.`
      },
      {
        id: "ch2_cmrr",
        num: 2,
        title: "Differential Pairs, Tail Resistance & CMRR",
        readTime: "25m",
        equations: [
            "CMRR = |Adm / Acm| = 2 * gm * Rss / (delta-gm / gm)",
            "Common-Mode Gain: Acm = - (delta-Rd / (2 * Rss))"
        ],
        body: `### 2. Differential Pair CMRR

In ideal symmetric differential pairs, common-mode variations do not alter differential output. Finite tail resistance Rss and transistor parameter mismatches convert common-mode inputs into differential output voltages, degrading CMRR.`
      }
    ]
  },
  {
    id: "tinyml_warden",
    title: "TinyML: Machine Learning on Microcontrollers",
    author: "Pete Warden & Daniel Situnayake",
    course: "EC3712 TinyML & Edge AI",
    color: "#D946EF",
    chapters: [
      {
        id: "ch1_quant",
        num: 1,
        title: "INT8 Symmetric Quantization & Zero-Point Offsets",
        readTime: "30m",
        equations: [
            "Real Value = Scale * (Quantized_Int8 - ZeroPoint)",
            "Scale S = (max_real - min_real) / 255.0"
        ],
        body: `### 1. Quantization for Microcontrollers

Quantization transforms 32-bit floating-point tensors into 8-bit integers, shrinking flash footprint by 75% and accelerating matrix multiplications using native MCU SIMD/DSP instructions.`
      },
      {
        id: "ch2_arena",
        num: 2,
        title: "Tensor Arena SRAM Allocation & Memory Budgeting",
        readTime: "20m",
        equations: [
            "Arena Size = max(layer_i_input + layer_i_weights + layer_i_output) + alignment"
        ],
        body: `### 2. Tensor Arena Budgeting

Microcontrollers lack virtual memory or dynamic heap allocators. TFLite Micro preallocates a contiguous byte buffer called Tensor Arena where tensor buffers are reused between layers.`
      }
    ]
  }
];

const DATASHEETS = [
  {
    id: "esp32",
    name: "ESP32-WROOM-32",
    arch: "Xtensa Dual-Core LX6",
    mhz: 240,
    flash: "4 MB",
    sram: "520 KB",
    vcc: "2.7 - 3.6 V",
    dma: 8,
    adc: "18ch (12-bit)",
    active_ma: 68.0,
    sleep_ua: 5.0,
    price: "₹290"
  },
  {
    id: "stm32f4",
    name: "STM32F401RE",
    arch: "ARM Cortex-M4 FPU",
    mhz: 84,
    flash: "512 KB",
    sram: "96 KB",
    vcc: "1.7 - 3.6 V",
    dma: 16,
    adc: "16ch (12-bit)",
    active_ma: 19.5,
    sleep_ua: 2.2,
    price: "₹480"
  },
  {
    id: "rp2040",
    name: "RP2040 Pico",
    arch: "Dual Cortex-M0+",
    mhz: 133,
    flash: "2 MB",
    sram: "264 KB",
    vcc: "1.8 - 3.3 V",
    dma: 12,
    adc: "4ch (12-bit)",
    active_ma: 22.0,
    sleep_ua: 180.0,
    price: "₹350"
  },
  {
    id: "nrf52840",
    name: "nRF52840 BLE",
    arch: "ARM Cortex-M4 FPU",
    mhz: 64,
    flash: "1 MB",
    sram: "256 KB",
    vcc: "1.7 - 5.5 V",
    dma: 8,
    adc: "8ch (12-bit)",
    active_ma: 4.8,
    sleep_ua: 0.4,
    price: "₹720"
  }
];

const DIAGRAMS = [
  {
    id: "diag_cortex",
    title: "ARM Cortex-M4 Harvard Bus Matrix & NVIC Pipeline",
    cat: "Core Architecture",
    layers: ["ICode Bus (Flash)", "DCode Bus (Constants)", "System Bus (SRAM/Peripherals)", "NVIC Priority Interconnect"]
  },
  {
    id: "diag_esp32",
    title: "ESP32 Xtensa Dual-Core & ULP Coprocessor Bus Interconnect",
    cat: "Microcontroller Architecture",
    layers: ["PRO_CPU (Core 0)", "APP_CPU (Core 1)", "RTC Ultra-Low-Power (ULP)", "Wi-Fi/BLE Radio Crossbar"]
  },
  {
    id: "diag_opamp",
    title: "Two-Stage CMOS Op-Amp with Miller Compensation (Cc)",
    cat: "Analog Circuit Schematics",
    layers: ["Differential Input Pair", "Current Mirror Active Load", "Cc Compensation Network", "Output Buffer Stage"]
  },
  {
    id: "diag_tinyml",
    title: "TinyML Tensor Arena SRAM Scratch Memory Map",
    cat: "Edge AI & Memory",
    layers: ["Input Tensor Buffer", "Persistent Weights Flash", "Reused Layer Scratch Area", "Output Classification Buffer"]
  }
];

export default function TextbookReaderHub() {
  const [activeTab, setActiveTab] = useState('reader'); // 'reader' | 'bookmarks' | 'datasheets' | 'diagrams'
  
  // Textbook Reader State (Features 211-213)
  const [selectedBook, setSelectedBook] = useState(TEXTBOOKS[0]);
  const [selectedChapter, setSelectedChapter] = useState(TEXTBOOKS[0].chapters[0]);
  
  // Bookmarks (Feature 212)
  const [bookmarks, setBookmarks] = useState([
    { id: 1, book: "Definitive Guide to ARM Cortex-M3/M4", chapter: "NVIC Priority Grouping & Tail-Chaining", date: "2026-11-06" }
  ]);

  // Annotations (Feature 213)
  const [annotations, setAnnotations] = useState([
    { id: 1, quote: "Dominant Pole: p1' = 1 / (gm2 * R1 * R2 * Cc)", note: "Vital equation for CAT-1 Op-Amp derivation!", color: "Yellow" }
  ]);
  const [newNote, setNewNote] = useState('');
  const [selectedColor, setSelectedColor] = useState('Yellow');

  // Datasheet Comparison State (Feature 214)
  const [selectedMcus, setSelectedMcus] = useState(['esp32', 'stm32f4', 'rp2040', 'nrf52840']);

  // Diagram Viewer State (Feature 215)
  const [selectedDiagram, setSelectedDiagram] = useState(DIAGRAMS[0]);
  const [activeLayers, setActiveLayers] = useState(DIAGRAMS[0].layers);

  const handleBookmark = () => {
    setBookmarks(prev => [
      { id: Date.now(), book: selectedBook.title, chapter: selectedChapter.title, date: new Date().toISOString().split('T')[0] },
      ...prev
    ]);
  };

  const handleAddAnnotation = () => {
    if (!newNote.trim()) return;
    setAnnotations(prev => [
      { id: Date.now(), quote: selectedChapter.title, note: newNote, color: selectedColor },
      ...prev
    ]);
    setNewNote('');
  };

  const toggleMcu = (id) => {
    setSelectedMcus(prev => prev.includes(id) ? prev.filter(m => m !== id) : [...prev, id]);
  };

  const toggleLayer = (layer) => {
    setActiveLayers(prev => prev.includes(layer) ? prev.filter(l => l !== layer) : [...prev, layer]);
  };

  return (
    <div className="w-full flex flex-col gap-6 font-mono text-xs">
      
      {/* Top Navigation HUD */}
      <div 
        className="glass-card rounded-2xl p-4 sm:p-5 border flex flex-wrap items-center justify-between gap-4 shadow-xl"
        style={{ borderColor: 'var(--theme-border)' }}
      >
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-amber-500 to-emerald-500 p-0.5 flex items-center justify-center text-xl shadow-lg">
            📖
          </div>
          <div>
            <div className="font-bold text-white text-sm sm:text-base flex items-center gap-2">
              <span>ECE Textbook & Datasheet Workspace</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40">
                PHASE B (FEATURES 211–215)
              </span>
            </div>
            <div className="text-[11px] text-slate-400">
              Anna University ECE R2023 • Curated Textbooks, MCU Datasheets & Circuit Schematics
            </div>
          </div>
        </div>

        {/* Global Action Badges */}
        <div className="flex flex-wrap items-center gap-2 text-slate-300">
          <span className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700">
            📚 {TEXTBOOKS.length} Core Textbooks
          </span>
          <span className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700">
            📑 {bookmarks.length} Bookmarks
          </span>
          <span className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700">
            🔬 {DATASHEETS.length} Silicon Datasheets
          </span>
        </div>
      </div>

      {/* Main Tab Controller */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2 overflow-x-auto">
        <button
          type="button"
          onClick={() => setActiveTab('reader')}
          className={`px-4 py-2 rounded-xl transition-all font-bold flex items-center gap-2 flex-shrink-0 ${
            activeTab === 'reader'
              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <span>📖</span>
          <span>Feature 211: Textbook Reader</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('bookmarks')}
          className={`px-4 py-2 rounded-xl transition-all font-bold flex items-center gap-2 flex-shrink-0 ${
            activeTab === 'bookmarks'
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <span>📑</span>
          <span>Features 212–213: Annotations & Bookmarks</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('datasheets')}
          className={`px-4 py-2 rounded-xl transition-all font-bold flex items-center gap-2 flex-shrink-0 ${
            activeTab === 'datasheets'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <span>🔬</span>
          <span>Feature 214: Datasheet Matrix</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('diagrams')}
          className={`px-4 py-2 rounded-xl transition-all font-bold flex items-center gap-2 flex-shrink-0 ${
            activeTab === 'diagrams'
              ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <span>📐</span>
          <span>Feature 215: Technical Diagrams</span>
        </button>
      </div>

      {/* TAB 1: FEATURE 211 — INTERACTIVE ECE TEXTBOOK READER */}
      {activeTab === 'reader' && (
        <div className="flex flex-col lg:flex-row gap-6 animate-in fade-in duration-200">
          
          {/* Textbook & Chapter Sidebar */}
          <div className="w-full lg:w-80 space-y-4 flex-shrink-0">
            {/* Book Selector */}
            <div className="glass-card rounded-2xl p-4 border space-y-2" style={{ borderColor: 'var(--theme-border)' }}>
              <div className="text-slate-400 font-bold uppercase text-[10px]">Select Textbook:</div>
              <div className="space-y-1.5">
                {TEXTBOOKS.map(book => (
                  <button
                    key={book.id}
                    type="button"
                    onClick={() => {
                      setSelectedBook(book);
                      setSelectedChapter(book.chapters[0]);
                    }}
                    className={`w-full text-left p-2.5 rounded-xl border transition-all ${
                      selectedBook.id === book.id
                        ? 'bg-slate-800 border-amber-400 text-white font-bold shadow-md'
                        : 'border-slate-800 text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                    }`}
                  >
                    <div className="truncate font-semibold text-xs">{book.title}</div>
                    <div className="text-[10px] text-slate-500 truncate">{book.author} • {book.course}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Chapters Accordion */}
            <div className="glass-card rounded-2xl p-4 border space-y-2" style={{ borderColor: 'var(--theme-border)' }}>
              <div className="text-slate-400 font-bold uppercase text-[10px]">Chapters:</div>
              <div className="space-y-1.5">
                {selectedBook.chapters.map(ch => (
                  <button
                    key={ch.id}
                    type="button"
                    onClick={() => setSelectedChapter(ch)}
                    className={`w-full text-left p-2 rounded-xl transition-all flex items-center justify-between ${
                      selectedChapter.id === ch.id
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold'
                        : 'text-slate-400 hover:bg-slate-900 hover:text-white'
                    }`}
                  >
                    <div className="truncate flex items-center gap-1.5">
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800">Ch {ch.num}</span>
                      <span className="truncate text-[11px]">{ch.title}</span>
                    </div>
                    <span className="text-[10px] text-slate-500 ml-1">{ch.readTime}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Chapter Reading View & Annotation Controls */}
          <div className="flex-1 glass-card rounded-2xl p-6 border space-y-6 shadow-xl" style={{ borderColor: 'var(--theme-border)' }}>
            
            {/* Chapter Header */}
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
              <div>
                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-amber-400 font-bold">
                  {selectedBook.course}
                </span>
                <h2 className="text-lg sm:text-xl font-bold text-white mt-1">
                  Chapter {selectedChapter.num}: {selectedChapter.title}
                </h2>
                <p className="text-slate-400 text-xs mt-0.5">
                  {selectedBook.title} by {selectedBook.author} • Est. Read: {selectedChapter.readTime}
                </p>
              </div>

              <button
                type="button"
                onClick={handleBookmark}
                className="px-3.5 py-2 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 font-bold transition-all flex items-center gap-1.5"
                title="Bookmark Current Chapter Offset"
              >
                <span>🔖</span>
                <span>Bookmark Chapter</span>
              </button>
            </div>

            {/* Key Derivations / Equations Callout Banner */}
            <div className="p-4 rounded-xl bg-slate-900/80 border border-amber-500/30 space-y-2">
              <div className="text-amber-400 font-bold text-xs flex items-center gap-1.5">
                <span>⚡</span>
                <span>Key Examination Derivations & Silicon Equations:</span>
              </div>
              <div className="space-y-1">
                {selectedChapter.equations.map((eq, idx) => (
                  <div key={idx} className="p-2 rounded-lg bg-black/50 text-emerald-300 font-mono text-[11px] border border-slate-800">
                    {eq}
                  </div>
                ))}
              </div>
            </div>

            {/* Main Textbook Prose Content */}
            <div className="prose prose-invert max-w-none text-slate-200 text-xs leading-relaxed space-y-3 whitespace-pre-line bg-slate-950/60 p-5 rounded-2xl border border-slate-800/80">
              {selectedChapter.body}
            </div>

            {/* Quick Inline Annotation Input */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white text-xs">Add Inline Annotation / Margin Note:</span>
                <div className="flex items-center gap-1.5">
                  {['Yellow', 'Cyan', 'Emerald'].map(color => (
                    <button
                      key={color}
                      type="button"
                      onClick={() => setSelectedColor(color)}
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        selectedColor === color ? 'ring-2 ring-white text-slate-950' : 'opacity-70'
                      }`}
                      style={{
                        backgroundColor: color === 'Yellow' ? '#FACC15' : color === 'Cyan' ? '#38BDF8' : '#10B981'
                      }}
                    >
                      {color}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Type margin note on this chapter..."
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  className="flex-1 px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-amber-400"
                />
                <button
                  type="button"
                  onClick={handleAddAnnotation}
                  className="px-4 py-1.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold transition-all"
                >
                  Save Note
                </button>
              </div>
            </div>

          </div>

        </div>
      )}

      {/* TAB 2: FEATURES 212–213 — ANNOTATIONS & BOOKMARKS */}
      {activeTab === 'bookmarks' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in duration-200">
          
          {/* Bookmarks Column (Feature 212) */}
          <div className="glass-card rounded-2xl p-5 border space-y-4" style={{ borderColor: 'var(--theme-border)' }}>
            <h3 className="font-bold text-white text-sm flex items-center gap-2">
              <span>📑 Saved Chapter Bookmarks</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold">
                {bookmarks.length} Active
              </span>
            </h3>

            <div className="space-y-2.5">
              {bookmarks.map((b) => (
                <div key={b.id} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                  <div>
                    <div className="font-bold text-white text-xs">{b.chapter}</div>
                    <div className="text-[11px] text-slate-400">{b.book}</div>
                    <div className="text-[10px] text-slate-500 mt-0.5">Saved: {b.date}</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => setActiveTab('reader')}
                    className="px-3 py-1 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 font-bold text-[11px] transition-all"
                  >
                    Jump →
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Annotations Column (Feature 213) */}
          <div className="glass-card rounded-2xl p-5 border space-y-4" style={{ borderColor: 'var(--theme-border)' }}>
            <h3 className="font-bold text-white text-sm flex items-center gap-2">
              <span>📝 PDF & Markdown Annotations</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold">
                {annotations.length} Notes
              </span>
            </h3>

            <div className="space-y-2.5">
              {annotations.map((ann) => (
                <div key={ann.id} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] px-1.5 py-0.2 rounded font-bold" style={{
                      backgroundColor: ann.color === 'Yellow' ? 'rgba(250,204,21,0.2)' : ann.color === 'Cyan' ? 'rgba(56,189,248,0.2)' : 'rgba(16,185,129,0.2)',
                      color: ann.color === 'Yellow' ? '#FACC15' : ann.color === 'Cyan' ? '#38BDF8' : '#10B981'
                    }}>
                      {ann.color} Tag
                    </span>
                    <span className="text-[10px] text-slate-500">Margin Note</span>
                  </div>
                  <div className="text-[11px] text-slate-300 font-semibold italic">"{ann.quote}"</div>
                  <div className="text-white text-xs">{ann.note}</div>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}

      {/* TAB 3: FEATURE 214 — DATASHEET SPECIFICATION COMPARISON MATRIX */}
      {activeTab === 'datasheets' && (
        <div className="glass-card rounded-2xl p-6 border space-y-6 animate-in fade-in duration-200" style={{ borderColor: 'var(--theme-border)' }}>
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <h3 className="font-bold text-white text-base flex items-center gap-2">
                <span>Silicon & Microcontroller Specification Matrix</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 font-bold">
                  Side-by-Side ECE Benchmark
                </span>
              </h3>
              <p className="text-slate-400 text-xs mt-0.5">
                Compare architectural specs, DMA channels, power consumption, and price points.
              </p>
            </div>

            {/* Toggle MCU Chips */}
            <div className="flex items-center gap-2">
              {DATASHEETS.map(d => (
                <button
                  key={d.id}
                  type="button"
                  onClick={() => toggleMcu(d.id)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${
                    selectedMcus.includes(d.id)
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400'
                      : 'bg-slate-900 text-slate-500 border border-slate-800'
                  }`}
                >
                  {d.name.split(' ')[0]}
                </button>
              ))}
            </div>
          </div>

          {/* Comparison Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                  <th className="py-2.5 px-3">PARAMETER</th>
                  {DATASHEETS.filter(d => selectedMcus.includes(d.id)).map(d => (
                    <th key={d.id} className="py-2.5 px-3 font-bold text-white">
                      {d.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                <tr>
                  <td className="py-2.5 px-3 text-slate-400 font-semibold">Core Architecture</td>
                  {DATASHEETS.filter(d => selectedMcus.includes(d.id)).map(d => (
                    <td key={d.id} className="py-2.5 px-3 font-bold text-cyan-300">{d.arch}</td>
                  ))}
                </tr>
                <tr>
                  <td className="py-2.5 px-3 text-slate-400 font-semibold">Clock Frequency</td>
                  {DATASHEETS.filter(d => selectedMcus.includes(d.id)).map(d => (
                    <td key={d.id} className="py-2.5 px-3">{d.mhz} MHz</td>
                  ))}
                </tr>
                <tr>
                  <td className="py-2.5 px-3 text-slate-400 font-semibold">Flash Memory</td>
                  {DATASHEETS.filter(d => selectedMcus.includes(d.id)).map(d => (
                    <td key={d.id} className="py-2.5 px-3 text-emerald-400">{d.flash}</td>
                  ))}
                </tr>
                <tr>
                  <td className="py-2.5 px-3 text-slate-400 font-semibold">Internal SRAM</td>
                  {DATASHEETS.filter(d => selectedMcus.includes(d.id)).map(d => (
                    <td key={d.id} className="py-2.5 px-3 text-amber-400">{d.sram}</td>
                  ))}
                </tr>
                <tr>
                  <td className="py-2.5 px-3 text-slate-400 font-semibold">Operating Voltage</td>
                  {DATASHEETS.filter(d => selectedMcus.includes(d.id)).map(d => (
                    <td key={d.id} className="py-2.5 px-3">{d.vcc}</td>
                  ))}
                </tr>
                <tr>
                  <td className="py-2.5 px-3 text-slate-400 font-semibold">DMA Channels</td>
                  {DATASHEETS.filter(d => selectedMcus.includes(d.id)).map(d => (
                    <td key={d.id} className="py-2.5 px-3">{d.dma} channels</td>
                  ))}
                </tr>
                <tr>
                  <td className="py-2.5 px-3 text-slate-400 font-semibold">Active Current Draw</td>
                  {DATASHEETS.filter(d => selectedMcus.includes(d.id)).map(d => (
                    <td key={d.id} className="py-2.5 px-3">{d.active_ma} mA</td>
                  ))}
                </tr>
                <tr>
                  <td className="py-2.5 px-3 text-slate-400 font-semibold">Deep Sleep Current</td>
                  {DATASHEETS.filter(d => selectedMcus.includes(d.id)).map(d => (
                    <td key={d.id} className="py-2.5 px-3 text-emerald-300 font-bold">{d.sleep_ua} µA</td>
                  ))}
                </tr>
                <tr>
                  <td className="py-2.5 px-3 text-slate-400 font-semibold">Indicative Cost (INR)</td>
                  {DATASHEETS.filter(d => selectedMcus.includes(d.id)).map(d => (
                    <td key={d.id} className="py-2.5 px-3 font-bold text-white">{d.price}</td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 4: FEATURE 215 — TECHNICAL DIAGRAM LIBRARY VIEWER */}
      {activeTab === 'diagrams' && (
        <div className="flex flex-col lg:flex-row gap-6 animate-in fade-in duration-200">
          
          {/* Diagrams Catalog Sidebar */}
          <div className="w-full lg:w-80 space-y-3 flex-shrink-0">
            <div className="glass-card rounded-2xl p-4 border space-y-2" style={{ borderColor: 'var(--theme-border)' }}>
              <div className="text-slate-400 font-bold uppercase text-[10px]">Select Diagram:</div>
              <div className="space-y-1.5">
                {DIAGRAMS.map(diag => (
                  <button
                    key={diag.id}
                    type="button"
                    onClick={() => {
                      setSelectedDiagram(diag);
                      setActiveLayers(diag.layers);
                    }}
                    className={`w-full text-left p-2.5 rounded-xl border transition-all ${
                      selectedDiagram.id === diag.id
                        ? 'bg-purple-500/20 text-purple-300 border-purple-400 font-bold shadow-md'
                        : 'border-slate-800 text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                    }`}
                  >
                    <div className="truncate font-semibold text-xs">{diag.title}</div>
                    <div className="text-[10px] text-slate-500">{diag.cat}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Layer Toggles */}
            <div className="glass-card rounded-2xl p-4 border space-y-2" style={{ borderColor: 'var(--theme-border)' }}>
              <div className="text-slate-400 font-bold uppercase text-[10px]">Active Layers:</div>
              <div className="space-y-1.5">
                {selectedDiagram.layers.map(layer => {
                  const isActive = activeLayers.includes(layer);
                  return (
                    <button
                      key={layer}
                      type="button"
                      onClick={() => toggleLayer(layer)}
                      className={`w-full text-left p-2 rounded-lg border text-[11px] flex items-center justify-between ${
                        isActive
                          ? 'bg-slate-800 border-purple-500 text-white font-semibold'
                          : 'bg-slate-950/60 border-slate-800 text-slate-500'
                      }`}
                    >
                      <span>{layer}</span>
                      <span>{isActive ? "👁️" : "✕"}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Interactive Schematic / Block Canvas */}
          <div className="flex-1 glass-card rounded-2xl p-6 border flex flex-col justify-between shadow-xl min-h-[420px]" style={{ borderColor: 'var(--theme-border)' }}>
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                <div>
                  <h3 className="font-bold text-white text-base">{selectedDiagram.title}</h3>
                  <p className="text-slate-400 text-xs mt-0.5">{selectedDiagram.cat} • Layer Inspection Engine</p>
                </div>
                <span className="text-[10px] px-2.5 py-0.5 rounded bg-purple-500/20 text-purple-300 font-bold border border-purple-500/40">
                  Interactive View
                </span>
              </div>

              {/* Graphical Schematic Canvas Model */}
              <div className="rounded-2xl bg-slate-950 p-6 border border-slate-800 flex flex-col items-center justify-center min-h-[280px] relative overflow-hidden">
                <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(168,85,247,0.04)_1px,transparent_1px),linear-gradient(to_bottom,rgba(168,85,247,0.04)_1px,transparent_1px)] bg-[size:24px_24px]"></div>

                {/* Animated Blocks */}
                <div className="z-10 grid grid-cols-2 gap-4 w-full max-w-md">
                  {selectedDiagram.layers.map((layer, idx) => {
                    const isVisible = activeLayers.includes(layer);
                    return (
                      <div
                        key={idx}
                        className={`p-4 rounded-xl border transition-all text-center flex flex-col items-center justify-center ${
                          isVisible
                            ? 'bg-gradient-to-br from-purple-950/40 to-slate-900 border-purple-400 text-purple-300 shadow-lg scale-100'
                            : 'opacity-25 border-dashed border-slate-800 text-slate-600 scale-95'
                        }`}
                      >
                        <span className="text-lg mb-1">{idx === 0 ? "⚡" : idx === 1 ? "💾" : idx === 2 ? "🔄" : "📡"}</span>
                        <span className="font-bold text-xs">{layer}</span>
                        <span className="text-[9px] text-slate-400 mt-0.5">Subsystem Node</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
              <span>Layers Active: {activeLayers.length} / {selectedDiagram.layers.length}</span>
              <span className="text-purple-300 font-bold">VoltCore Hardware Schematic Engine</span>
            </div>

          </div>

        </div>
      )}

    </div>
  );
}
