import React, { useState, useMemo } from 'react';

/**
 * ============================================================================
 * VOLTCORE APEX ACADEMIA — ECE GLOSSARY & MASTER FORMULA QUICK-REFERENCE DRAWER
 * ============================================================================
 * Department of Electronics Engineering • MIT Campus • Anna University
 * Regulation 2023 Choice Based Credit System (CBCS)
 * 
 * Features:
 *   - Searchable across all 14 Regulation 2023 ECE subjects (Zero Course Codes)
 *   - Dual View: Master Formula Quick-Reference & Academic Engineering Glossary
 *   - Categorization by Engineering Discipline (Analog, Digital, Signals, etc.)
 *   - Formula breakdown with physical units and typical silicon values
 *   - High-contrast 18-theme compatible glass aesthetic
 * ============================================================================
 */

const DOMAINS = [
  { id: 'all', label: 'All Disciplines' },
  { id: 'analog', label: 'Analog & Devices' },
  { id: 'digital', label: 'Digital & VLSI' },
  { id: 'signals', label: 'Signals & DSP' },
  { id: 'comm', label: 'Communications & RF' },
  { id: 'embedded', label: 'Embedded & IoT' },
  { id: 'control', label: 'Control & Electromagnetics' }
];

const MASTER_FORMULAS = [
  {
    id: 'f1',
    name: 'Shockley Diode Characteristic',
    domain: 'analog',
    subject: 'Electronic Devices and Circuit Theory',
    formula: 'I_D = I_S · [exp(V_D / (η · V_T)) - 1]',
    variables: [
      { sym: 'I_S', desc: 'Reverse saturation current (typically 10^-14 to 10^-12 A)' },
      { sym: 'V_T', desc: 'Thermal voltage = k_B · T / q ≈ 25.86 mV at 300 K' },
      { sym: 'η', desc: 'Ideality factor (1.0 for Ge, 1.0–2.0 for Si)' }
    ],
    application: 'Diode I-V modeling, rectifiers, and PN junction temperature sensors.'
  },
  {
    id: 'f2',
    name: 'BJT Transconductance & Small-Signal Input Resistance',
    domain: 'analog',
    subject: 'Electronic Devices and Circuit Theory',
    formula: 'g_m = I_C / V_T ≈ 38.5 · I_C (mA) | r_π = β / g_m',
    variables: [
      { sym: 'I_C', desc: 'Quiescent collector current in active region' },
      { sym: 'β', desc: 'Common-emitter forward current gain (h_FE)' },
      { sym: 'r_π', desc: 'Small-signal base-emitter dynamic resistance' }
    ],
    application: 'Hybrid-pi amplifier gain calculation (A_v ≈ -g_m · R_C).'
  },
  {
    id: 'f3',
    name: 'Sallen-Key Active Filter Corner Frequency',
    domain: 'analog',
    subject: 'Linear Integrated Circuits and Applications',
    formula: 'f_c = 1 / [2π · √(R_1 · R_2 · C_1 · C_2)]',
    variables: [
      { sym: 'R_1, R_2', desc: 'Filter network input resistor values' },
      { sym: 'C_1, C_2', desc: 'Feedback and shunt capacitor values' },
      { sym: 'Q', desc: 'Quality factor = √(R_1 R_2 C_1 C_2) / [C_2(R_1 + R_2)]' }
    ],
    application: '2nd-order Butterworth / Chebyshev active lowpass and highpass synthesis.'
  },
  {
    id: 'f4',
    name: 'Static Timing Analysis Setup Constraint',
    domain: 'digital',
    subject: 'Digital System Design and Microprocessors',
    formula: 'T_clk ≥ t_cq + t_comb_max + t_setup - t_skew',
    variables: [
      { sym: 'T_clk', desc: 'Clock period (1 / f_clk)' },
      { sym: 't_cq', desc: 'Clock-to-Q register propagation delay' },
      { sym: 't_comb_max', desc: 'Worst-case combinational logic path delay' },
      { sym: 't_setup', desc: 'Capture flip-flop required setup time' }
    ],
    application: 'Determining maximum operating frequency f_max for ASIC & FPGA pipelines.'
  },
  {
    id: 'f5',
    name: 'Static Timing Analysis Hold Constraint',
    domain: 'digital',
    subject: 'Digital System Design and Microprocessors',
    formula: 't_cq + t_comb_min ≥ t_hold + t_skew',
    variables: [
      { sym: 't_comb_min', desc: 'Fastest contaminant path delay through logic' },
      { sym: 't_hold', desc: 'Required data hold time after active clock edge' }
    ],
    application: 'Preventing race conditions that cannot be solved by reducing clock rate.'
  },
  {
    id: 'f6',
    name: 'CMOS Inverter Dynamic Power Dissipation',
    domain: 'digital',
    subject: 'CMOS VLSI Design & Nanometer Technology',
    formula: 'P_dyn = α · C_L · V_DD^2 · f_clk',
    variables: [
      { sym: 'α', desc: 'Node switching activity factor (typically 0.1 to 0.2)' },
      { sym: 'C_L', desc: 'Total load capacitance (interconnect + gate fanout)' },
      { sym: 'V_DD', desc: 'Supply rail voltage (quadratic dependence)' }
    ],
    application: 'Nanometer SoC low-power design and dynamic voltage-frequency scaling (DVFS).'
  },
  {
    id: 'f7',
    name: 'Discrete Fourier Transform (DFT)',
    domain: 'signals',
    subject: 'Digital Signal Processing & Algorithms',
    formula: 'X[k] = Σ_{n=0}^{N-1} x[n] · exp(-j 2π k n / N)',
    variables: [
      { sym: 'N', desc: 'Transform block length (typically powers of 2 for FFT)' },
      { sym: 'W_N', desc: 'Twiddle factor = exp(-j 2π / N)' }
    ],
    application: 'FFT spectral analysis, filter banks, and circular convolution.'
  },
  {
    id: 'f8',
    name: 'Shannon-Hartley Channel Capacity',
    domain: 'comm',
    subject: 'Digital Communication Systems',
    formula: 'C = B · log_2(1 + SNR) [Bits per second]',
    variables: [
      { sym: 'B', desc: 'Channel bandwidth in Hertz' },
      { sym: 'SNR', desc: 'Signal-to-noise ratio in linear scale (P_S / P_N)' }
    ],
    application: 'Fundamental theoretical maximum data rate over additive white Gaussian noise (AWGN).'
  },
  {
    id: 'f9',
    name: 'Rate-Monotonic Scheduling (RMS) Feasibility Bound',
    domain: 'embedded',
    subject: 'Microcontroller Architecture and Interfacing',
    formula: 'U = Σ_{i=1}^n (C_i / T_i) ≤ n · (2^(1/n) - 1)',
    variables: [
      { sym: 'C_i', desc: 'Worst-case execution time of task i' },
      { sym: 'T_i', desc: 'Period / deadline of task i' },
      { sym: 'U', desc: 'CPU utilization bound (approaches ln(2) ≈ 69.3% as n → ∞)' }
    ],
    application: 'Hard real-time FreeRTOS priority assignment and schedulability verification.'
  },
  {
    id: 'f10',
    name: 'Closed-Loop Transfer Function & Sensitivity',
    domain: 'control',
    subject: 'Control Systems Engineering',
    formula: 'T(s) = [G_c(s) · G(s)] / [1 + G_c(s) · G(s) · H(s)]',
    variables: [
      { sym: 'G_c(s)', desc: 'Controller transfer function (PID / Lead-Lag)' },
      { sym: 'G(s)', desc: 'Open-loop plant model' },
      { sym: 'H(s)', desc: 'Feedback sensor dynamics' }
    ],
    application: 'Feedback stability, root-locus design, and steady-state error elimination.'
  }
];

const GLOSSARY_TERMS = [
  {
    term: 'Barkhausen Criterion',
    domain: 'analog',
    subject: 'Electronic Devices and Circuit Theory',
    definition: 'Conditions required for sustained sinusoidal oscillation in a feedback amplifier: loop gain magnitude |Aβ| ≥ 1 and total loop phase shift ∠(Aβ) = 0° (or 360°).'
  },
  {
    term: 'Early Effect (Base-Width Modulation)',
    domain: 'analog',
    subject: 'Electronic Devices and Circuit Theory',
    definition: 'The reduction in effective neutral base width in a BJT as reverse bias across the collector-base junction increases, causing collector current to rise with V_CE. Quantified by Early Voltage (V_A).'
  },
  {
    term: 'Common-Mode Rejection Ratio (CMRR)',
    domain: 'analog',
    subject: 'Linear Integrated Circuits and Applications',
    definition: 'The measure of a differential amplifier’s ability to amplify the differential signal while rejecting common-mode noise: CMRR = 20 · log10(|A_d / A_cm|).'
  },
  {
    term: 'Miller Theorem & Capacitive Multiplication',
    domain: 'analog',
    subject: 'Electronic Devices and Circuit Theory',
    definition: 'The phenomenon where bridging capacitance between input and inverting output nodes appears transformed to ground as an equivalent input capacitance C_in = C_f · (1 - A_v), drastically reducing amplifier bandwidth.'
  },
  {
    term: 'Metastability',
    domain: 'digital',
    subject: 'Digital System Design and Microprocessors',
    definition: 'An undefined intermediate state in a bistable flip-flop caused by setup or hold time violations during asynchronous signal capture, causing unbounded propagation delay.'
  },
  {
    term: 'Clock Skew & Jitter',
    domain: 'digital',
    subject: 'Digital System Design and Microprocessors',
    definition: 'Clock skew is the spatial difference in arrival times of a clock edge at different registers due to routing. Jitter is the temporal deviation of clock edge transition from its ideal position.'
  },
  {
    term: 'Subthreshold Conduction',
    domain: 'digital',
    subject: 'CMOS VLSI Design & Nanometer Technology',
    definition: 'Weak inversion carrier diffusion current flowing between drain and source in a MOSFET when gate-source voltage V_GS is below threshold voltage V_th. Key contributor to static leakage.'
  },
  {
    term: 'Gray Code Adjacency',
    domain: 'digital',
    subject: 'Digital System Design and Microprocessors',
    definition: 'An unweighted binary numeral system where successive values differ by only one single bit. Critical in Karnaugh maps, asynchronous FIFO pointers, and rotary encoders to prevent multi-bit glitching.'
  },
  {
    term: 'Nyquist-Shannon Sampling Theorem',
    domain: 'signals',
    subject: 'Signals and Systems Analysis',
    definition: 'A bandlimited continuous-time signal containing no frequencies higher than f_max can be perfectly reconstructed from discrete samples if the sampling rate satisfies f_s ≥ 2 · f_max.'
  },
  {
    term: 'Twiddle Factor (W_N)',
    domain: 'signals',
    subject: 'Digital Signal Processing & Algorithms',
    definition: 'The complex exponential root-of-unity phase vector W_N = exp(-j 2π / N) used in Cooley-Tukey decimation-in-time and decimation-in-frequency FFT butterfly algorithms.'
  },
  {
    term: 'Constellation Diagram',
    domain: 'comm',
    subject: 'Digital Communication Systems',
    definition: 'A 2D scatter representation in complex Cartesian signal space where in-phase (I) and quadrature (Q) amplitudes represent distinct digital symbols (e.g. BPSK, QPSK, 16-QAM).'
  },
  {
    term: 'Priority Inversion',
    domain: 'embedded',
    subject: 'Microcontroller Architecture and Interfacing',
    definition: 'A hazardous real-time OS state where a high-priority task is preempted or blocked by a low-priority task holding a shared resource, resolved via Priority Ceiling or Priority Inheritance protocols.'
  },
  {
    term: 'Atomic Register Access (W1TC / W1TS)',
    domain: 'embedded',
    subject: 'Microcontroller Architecture and Interfacing',
    definition: 'Hardware microcontroller registers where writing a logic 1 either clears (Write-1-to-Clear) or sets (Write-1-to-Set) specific peripheral interrupt bits in a single machine cycle without read-modify-write hazard.'
  },
  {
    term: 'Poynting Vector',
    domain: 'control',
    subject: 'Control Systems Engineering',
    definition: 'The directional power flux density vector S = E × H (Watts/m²) of an electromagnetic wavefront representing the rate of energy transfer per unit area.'
  }
];

export default function EceGlossaryFormulaDrawer({
  isOpen = true,
  onClose = null,
  embedded = false
}) {
  const [activeTab, setActiveTab] = useState('formulas'); // 'formulas' | 'glossary'
  const [selectedDomain, setSelectedDomain] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedId, setCopiedId] = useState(null);

  // Filter formulas
  const filteredFormulas = useMemo(() => {
    return MASTER_FORMULAS.filter(item => {
      const matchDomain = selectedDomain === 'all' || item.domain === selectedDomain;
      const q = searchQuery.toLowerCase().trim();
      const matchSearch = !q ||
        item.name.toLowerCase().includes(q) ||
        item.formula.toLowerCase().includes(q) ||
        item.application.toLowerCase().includes(q) ||
        item.subject.toLowerCase().includes(q);
      return matchDomain && matchSearch;
    });
  }, [selectedDomain, searchQuery]);

  // Filter glossary
  const filteredGlossary = useMemo(() => {
    return GLOSSARY_TERMS.filter(item => {
      const matchDomain = selectedDomain === 'all' || item.domain === selectedDomain;
      const q = searchQuery.toLowerCase().trim();
      const matchSearch = !q ||
        item.term.toLowerCase().includes(q) ||
        item.definition.toLowerCase().includes(q) ||
        item.subject.toLowerCase().includes(q);
      return matchDomain && matchSearch;
    });
  }, [selectedDomain, searchQuery]);

  const handleCopyFormula = (id, formula) => {
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(formula);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    }
  };

  return (
    <div
      className={`rounded-3xl border overflow-hidden font-sans space-y-4 ${
        embedded ? 'p-5' : 'p-6 sm:p-8 shadow-2xl'
      }`}
      style={{
        background: 'var(--theme-surface, rgba(4,16,38,0.92))',
        borderColor: 'var(--theme-border, rgba(0,240,181,0.25))'
      }}
    >
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xl">📐</span>
            <h2 className="font-heading font-extrabold text-lg sm:text-xl text-white tracking-tight">
              ECE Master Formula Library &amp; Academic Glossary
            </h2>
          </div>
          <p className="text-xs text-slate-400 font-sans mt-0.5">
            Verified mathematical models, IEEE definitions, and derivations across 14 Regulation 2023 disciplines.
          </p>
        </div>

        {/* View Switcher Pills */}
        <div className="flex items-center p-1 rounded-xl bg-[#020813] border border-slate-800 text-xs font-mono">
          <button
            type="button"
            onClick={() => setActiveTab('formulas')}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
              activeTab === 'formulas'
                ? 'bg-[#00693E] text-[#00F0B5] shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Formulas ({filteredFormulas.length})
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('glossary')}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
              activeTab === 'glossary'
                ? 'bg-[#00693E] text-[#00F0B5] shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Glossary ({filteredGlossary.length})
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search subjects, formulas, theorems, variables, or definitions..."
            className="w-full px-4 py-2 pl-10 rounded-xl bg-[#020813] border border-slate-800 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-400 font-mono"
          />
          <span className="absolute left-3.5 top-2.5 text-slate-500 text-xs">🔍</span>
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-2.5 text-xs text-slate-400 hover:text-white"
            >
              ✕
            </button>
          )}
        </div>

        {/* Domain Filter Buttons */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto text-xs font-mono pb-1 sm:pb-0">
          {DOMAINS.map(d => (
            <button
              key={d.id}
              onClick={() => setSelectedDomain(d.id)}
              className={`px-2.5 py-1.5 rounded-lg transition-all flex-shrink-0 ${
                selectedDomain === d.id
                  ? 'bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/40'
                  : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {d.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      {activeTab === 'formulas' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[560px] overflow-y-auto pr-1">
          {filteredFormulas.length === 0 ? (
            <div className="col-span-2 p-8 text-center text-slate-500 font-mono text-xs">
              No engineering formulas match "{searchQuery}".
            </div>
          ) : (
            filteredFormulas.map(item => (
              <div
                key={item.id}
                className="p-4 rounded-2xl bg-[#020813]/90 border border-slate-800 hover:border-emerald-400/40 transition-all space-y-3"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="font-heading font-bold text-sm text-white">{item.name}</h3>
                    <div className="text-[11px] text-emerald-400 font-mono mt-0.5">{item.subject}</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleCopyFormula(item.id, item.formula)}
                    className="px-2 py-1 rounded bg-slate-900 hover:bg-slate-800 border border-slate-700 text-[10px] font-mono text-slate-300 hover:text-white flex-shrink-0 transition-colors"
                  >
                    {copiedId === item.id ? '✓ Copied' : 'Copy'}
                  </button>
                </div>

                {/* Mathematical Equation Display */}
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs sm:text-sm text-emerald-300 overflow-x-auto">
                  {item.formula}
                </div>

                {/* Variable Breakdown */}
                <div className="space-y-1 font-mono text-[11px] text-slate-400 border-t border-slate-800/60 pt-2">
                  {item.variables.map((v, i) => (
                    <div key={i} className="flex items-start gap-1.5">
                      <strong className="text-cyan-300">{v.sym}:</strong>
                      <span>{v.desc}</span>
                    </div>
                  ))}
                </div>

                {/* Practical Application */}
                <div className="text-[11px] text-slate-400 font-sans leading-snug">
                  <strong className="text-slate-300">Engineering Application:</strong> {item.application}
                </div>
              </div>
            ))
          )}
        </div>
      ) : (
        /* Academic Glossary List */
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[560px] overflow-y-auto pr-1">
          {filteredGlossary.length === 0 ? (
            <div className="col-span-2 p-8 text-center text-slate-500 font-mono text-xs">
              No glossary terms match "{searchQuery}".
            </div>
          ) : (
            filteredGlossary.map((item, idx) => (
              <div
                key={idx}
                className="p-4 rounded-2xl bg-[#020813]/90 border border-slate-800 hover:border-emerald-400/40 transition-all space-y-2"
              >
                <div className="flex items-center justify-between gap-2">
                  <h3 className="font-heading font-bold text-sm text-white tracking-tight">{item.term}</h3>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-500/30">
                    {item.subject}
                  </span>
                </div>
                <p className="text-xs text-slate-300 font-sans leading-relaxed">
                  {item.definition}
                </p>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
