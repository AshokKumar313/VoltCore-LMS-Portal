/**
 * ========================================================================================
 * VoltCore Apex Academia - ECE Professional Subject Emblem & Discipline Registry
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Module: src/data/subjectRegistry.ts
 * Platform Lead & Educational Systems Director: Ashok Kumar A (2023MITEC042)
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 *
 * Capabilities:
 *   1. Complete 14 Core ECE Disciplines with Clean, Professional Engineering Nomenclature
 *   2. Industry-Aligned Professional Titles, Disciplines, and Subfield Categorization
 *   3. Bespoke Precision Vector SVG Geometries (Bandgap, Op-Amp, Smith Chart, FFT, CMOS, etc.)
 *   4. Harmonious Theme-Adaptive Color Palettes (Dynamic 18-Theme System)
 *   5. Robust Fallback Emblem for Unregistered / Specialized Elective Modules
 *   6. Complete Backward Compatibility with Alphanumeric Course Codes in Metadata
 * ========================================================================================
 */

export interface SubjectMetadata {
  /** Course code retained in secondary technical metadata for backward compatibility & indexing */
  code: string;
  /** Clean, professional engineering discipline name (no raw course codes in primary headings) */
  disciplineName: string;
  /** Comprehensive professional engineering title */
  professionalTitle: string;
  /** Primary industry sector application */
  industryDomain: string;
  /** Specific engineering subfield specialization */
  subfield: string;
  /** Academic syllabus name */
  name: string;
  /** Concise professional title */
  shortTitle: string;
  category: 'FOUNDATION' | 'CORE_ANALOG' | 'CORE_DIGITAL' | 'SYSTEMS_SIGNALS' | 'EMBEDDED_VLSI';
  tier: string;
  semester: number;
  credits: number;
  symbolName: string;
  primaryColor: string;
  accentColor: string;
  gradient: [string, string];
  darkBackground: string;
  accessibleLabel: string;
  technicalKeywords: string[];
  svgPath: string; // Inner SVG vector paths for 48x48 viewBox
}

export const ECE_SUBJECT_REGISTRY: Record<string, SubjectMetadata> = {
  // 1. Circuit Analysis & Network Synthesis
  'EC23C01': {
    code: 'EC23C01',
    disciplineName: 'Circuit Analysis & Network Synthesis',
    professionalTitle: 'Linear Circuit Theory & Network Synthesis',
    industryDomain: 'Analog EDA & Circuit Infrastructure',
    subfield: 'Circuits & Systems',
    name: 'Circuit Analysis & Network Synthesis',
    shortTitle: 'Circuits & Networks',
    category: 'FOUNDATION',
    tier: 'Tier 1: Foundation',
    semester: 2,
    credits: 4,
    symbolName: 'MNA Nodal Bridge',
    primaryColor: '#00F0B5',
    accentColor: '#10B981',
    gradient: ['#00F0B5', '#047857'],
    darkBackground: 'rgba(0, 240, 181, 0.08)',
    accessibleLabel: 'Resistor-Inductor-Capacitor Lattice Network Emblem',
    technicalKeywords: ['KCL', 'KVL', 'Thevenin', 'Norton', 'MNA Solver', 'Laplace Transients'],
    svgPath: `
      <!-- Inductor Loop & Capacitive Node Bridge -->
      <path d="M6 24h6c0-4 3-7 6-7s6 3 6 7c0-4 3-7 6-7s6 3 6 7h6" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="24" y1="24" x2="24" y2="34" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="16" y1="34" x2="32" y2="34" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="18" y1="38" x2="30" y2="38" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="24" y1="38" x2="24" y2="44" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <circle cx="6" cy="24" r="2.5" fill="currentColor"/>
      <circle cx="42" cy="24" r="2.5" fill="currentColor"/>
      <circle cx="24" cy="17" r="1.5" fill="currentColor" opacity="0.8"/>
    `
  },

  // 2. Semiconductor Device Physics
  'EC23C02': {
    code: 'EC23C02',
    disciplineName: 'Semiconductor Device Physics',
    professionalTitle: 'Solid-State Physics & Semiconductor Devices',
    industryDomain: 'Semiconductor Foundry & Microelectronics',
    subfield: 'Solid-State Physics',
    name: 'Semiconductor Physics & Devices',
    shortTitle: 'Semiconductor Physics',
    category: 'FOUNDATION',
    tier: 'Tier 1: Foundation',
    semester: 3,
    credits: 3,
    symbolName: 'Fermi Bandgap Lattice',
    primaryColor: '#38BDF8',
    accentColor: '#0284C7',
    gradient: ['#38BDF8', '#0369A1'],
    darkBackground: 'rgba(56, 189, 248, 0.08)',
    accessibleLabel: 'Energy Bandgap with Conduction and Valence Bands Emblem',
    technicalKeywords: ['Bandgap Eg', 'Fermi-Dirac', 'Intrinsic Carriers ni', 'Carrier Drift-Diffusion'],
    svgPath: `
      <!-- Conduction Band (Top Curve) -->
      <path d="M8 14c8-6 24-6 32 0" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <!-- Valence Band (Bottom Curve) -->
      <path d="M8 34c8 6 24 6 32 0" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <!-- Fermi Level Dashed Line -->
      <line x1="10" y1="24" x2="38" y2="24" stroke="currentColor" stroke-width="2" stroke-dasharray="3 3"/>
      <!-- Quantum Electron & Hole Particles -->
      <circle cx="24" cy="11" r="2.5" fill="currentColor"/>
      <circle cx="16" cy="13" r="2" fill="currentColor" opacity="0.75"/>
      <circle cx="32" cy="13" r="2" fill="currentColor" opacity="0.75"/>
      <circle cx="24" cy="37" r="2.5" fill="none" stroke="currentColor" stroke-width="2"/>
      <circle cx="16" cy="35" r="2" fill="none" stroke="currentColor" stroke-width="1.5"/>
      <circle cx="32" cy="35" r="2" fill="none" stroke="currentColor" stroke-width="1.5"/>
    `
  },

  // 3. Electronic Devices & Circuit Modeling
  'EC23C03': {
    code: 'EC23C03',
    disciplineName: 'Electronic Devices & Circuit Modeling',
    professionalTitle: 'Discrete Semiconductor Devices & Active Circuits',
    industryDomain: 'Hardware Electronics & Power Systems',
    subfield: 'Electronic Devices',
    name: 'Electronic Devices & Solid-State Circuits',
    shortTitle: 'Electronic Devices',
    category: 'CORE_ANALOG',
    tier: 'Tier 2: Core Analog',
    semester: 3,
    credits: 4,
    symbolName: 'Shockley PN Junction',
    primaryColor: '#F59E0B',
    accentColor: '#D97706',
    gradient: ['#F59E0B', '#B45309'],
    darkBackground: 'rgba(245, 158, 11, 0.08)',
    accessibleLabel: 'Semiconductor Diode and MOSFET Channel Junction Emblem',
    technicalKeywords: ['Shockley Diode', 'BJT Hybrid-Pi', 'MOSFET Subthreshold', 'Depletion Width'],
    svgPath: `
      <!-- Diode Triangle & Cathode Bar -->
      <path d="M12 16 L28 24 L12 32 Z" fill="currentColor" fill-opacity="0.85" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
      <line x1="28" y1="14" x2="28" y2="34" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
      <!-- Input and Output Leads -->
      <line x1="4" y1="24" x2="12" y2="24" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="28" y1="24" x2="44" y2="24" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <!-- Depletion Region Space-Charge Ions -->
      <circle cx="36" cy="18" r="1.5" fill="currentColor"/>
      <circle cx="36" cy="30" r="1.5" fill="currentColor"/>
    `
  },

  // 4. Analog Integrated Circuit Design
  'EC23C05': {
    code: 'EC23C05',
    disciplineName: 'Analog Integrated Circuit Design',
    professionalTitle: 'Precision Analog ICs & Operational Amplifiers',
    industryDomain: 'Mixed-Signal ICs & Sensor Frontends',
    subfield: 'Analog ICs',
    name: 'Analog Integrated Electronics',
    shortTitle: 'Analog Electronics',
    category: 'CORE_ANALOG',
    tier: 'Tier 2: Core Analog',
    semester: 4,
    credits: 4,
    symbolName: 'Differential Op-Amp Core',
    primaryColor: '#EC4899',
    accentColor: '#BE185D',
    gradient: ['#EC4899', '#9D174D'],
    darkBackground: 'rgba(236, 72, 153, 0.08)',
    accessibleLabel: 'High-Precision Operational Amplifier Symbol Emblem',
    technicalKeywords: ['Op-Amp', 'CMRR', 'Gain-Bandwidth', 'Active Filters', 'Slew Rate'],
    svgPath: `
      <!-- Operational Amplifier Triangle -->
      <path d="M10 8 L38 24 L10 40 Z" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>
      <!-- Non-Inverting (+) and Inverting (-) Inputs -->
      <line x1="4" y1="16" x2="10" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="4" y1="32" x2="10" y2="32" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <!-- Polarity Glyphs -->
      <text x="13" y="19" fill="currentColor" font-size="9" font-family="sans-serif" font-weight="bold">+</text>
      <text x="14" y="34" fill="currentColor" font-size="9" font-family="sans-serif" font-weight="bold">-</text>
      <!-- Output Lead -->
      <line x1="38" y1="24" x2="44" y2="24" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
    `
  },

  // 5. Digital Logic Design & Finite Automata
  'EC23C06': {
    code: 'EC23C06',
    disciplineName: 'Digital Logic Design & Finite Automata',
    professionalTitle: 'Combinational & Sequential Logic Architecture',
    industryDomain: 'Digital Systems & ASIC Microarchitecture',
    subfield: 'Digital Logic',
    name: 'Digital Electronics & Logic Design',
    shortTitle: 'Digital Electronics',
    category: 'CORE_DIGITAL',
    tier: 'Tier 2: Core Digital',
    semester: 4,
    credits: 4,
    symbolName: 'K-Map Logic Gate Matrix',
    primaryColor: '#8B5CF6',
    accentColor: '#6D28D9',
    gradient: ['#8B5CF6', '#5B21B6'],
    darkBackground: 'rgba(139, 92, 246, 0.08)',
    accessibleLabel: 'NAND Logic Gate with Binary Grid Emblem',
    technicalKeywords: ['K-Map', 'Quine-McCluskey', 'Synchronous FSM', 'Setup/Hold Slack'],
    svgPath: `
      <!-- Logic Gate Body (AND/NAND Curve) -->
      <path d="M10 12 h12 c8 0 14 5 14 12 s-6 12-14 12 h-12 Z" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>
      <!-- Inputs -->
      <line x1="4" y1="18" x2="10" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="4" y1="30" x2="10" y2="30" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <!-- Inversion Bubble & Output Lead -->
      <circle cx="38.5" cy="24" r="2.5" fill="none" stroke="currentColor" stroke-width="2"/>
      <line x1="41" y1="24" x2="44" y2="24" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    `
  },

  // 6. Signals & Linear Systems Theory
  'EC23C04': {
    code: 'EC23C04',
    disciplineName: 'Signals & Linear Systems Theory',
    professionalTitle: 'Continuous & Discrete-Time Linear Systems',
    industryDomain: 'Signal Processing & Communication Infrastructure',
    subfield: 'Systems & Signals',
    name: 'Signals and Linear Systems',
    shortTitle: 'Signals & Systems',
    category: 'SYSTEMS_SIGNALS',
    tier: 'Tier 2: Systems & Signals',
    semester: 3,
    credits: 4,
    symbolName: 'Continuous Fourier S-Plane',
    primaryColor: '#06B6D4',
    accentColor: '#0891B2',
    gradient: ['#06B6D4', '#0E7490'],
    darkBackground: 'rgba(6, 182, 212, 0.08)',
    accessibleLabel: 'Sine Wave Harmonic Frequency Domain S-Plane Emblem',
    technicalKeywords: ['LTI Convolution', 'Fourier Series', 'Laplace ROC', 'Z-Transform'],
    svgPath: `
      <!-- Time-Domain Harmonic Sine Waveform -->
      <path d="M6 24 c5-14 9-14 13 0 s8 14 13 0 s7-14 10-4" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <!-- S-Plane Orthogonal Axes -->
      <line x1="24" y1="6" x2="24" y2="42" stroke="currentColor" stroke-width="1.5" stroke-opacity="0.4" stroke-dasharray="2 2"/>
      <line x1="4" y1="24" x2="44" y2="24" stroke="currentColor" stroke-width="1.5" stroke-opacity="0.4"/>
      <!-- Complex Conjugate Poles (x) -->
      <path d="M14 12 l4 4 m0 -4 l-4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <path d="M14 32 l4 4 m0 -4 l-4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    `
  },

  // 7. Control Systems Engineering
  'EC23C07': {
    code: 'EC23C07',
    disciplineName: 'Control Systems Engineering',
    professionalTitle: 'Feedback Dynamics, Stability & Modern Control',
    industryDomain: 'Robotics, Aerospace & Industrial Automation',
    subfield: 'Control Systems',
    name: 'Control Systems Engineering',
    shortTitle: 'Control Systems',
    category: 'SYSTEMS_SIGNALS',
    tier: 'Tier 3: Systems & Signals',
    semester: 4,
    credits: 4,
    symbolName: 'Closed-Loop Root Locus Plant',
    primaryColor: '#10B981',
    accentColor: '#059669',
    gradient: ['#10B981', '#047857'],
    darkBackground: 'rgba(16, 185, 129, 0.08)',
    accessibleLabel: 'Closed-Loop Feedback Block Diagram with Summing Junction Emblem',
    technicalKeywords: ['Root Locus', 'Bode Plot', 'Nyquist Stability', 'State-Space'],
    svgPath: `
      <!-- Summing Junction Circle with Cross -->
      <circle cx="14" cy="20" r="5" fill="none" stroke="currentColor" stroke-width="2"/>
      <line x1="11" y1="20" x2="17" y2="20" stroke="currentColor" stroke-width="1.5"/>
      <line x1="14" y1="17" x2="14" y2="23" stroke="currentColor" stroke-width="1.5"/>
      <!-- Plant G(s) Block -->
      <rect x="25" y="14" width="14" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>
      <text x="28" y="23" fill="currentColor" font-size="7" font-family="sans-serif" font-weight="bold">G(s)</text>
      <!-- Feedforward Line -->
      <line x1="4" y1="20" x2="9" y2="20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="19" y1="20" x2="25" y2="20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="39" y1="20" x2="45" y2="20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <!-- Feedback Return Loop H(s) -->
      <path d="M42 20 v14 h-28 v-9" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
    `
  },

  // 8. Digital Signal Processing & Algorithms
  'EC23S01': {
    code: 'EC23S01',
    disciplineName: 'Digital Signal Processing & Algorithms',
    professionalTitle: 'Discrete-Time Transforms & Multirate Filterbanks',
    industryDomain: 'Audio/Image DSP, Radar & Biomedical Signals',
    subfield: 'Digital Signal Processing',
    name: 'Digital Signal Processing Practice',
    shortTitle: 'Python DSP',
    category: 'SYSTEMS_SIGNALS',
    tier: 'Tier 3: Systems & Signals',
    semester: 5,
    credits: 4,
    symbolName: 'Radix-2 FFT Butterfly Ring',
    primaryColor: '#14B8A6',
    accentColor: '#0D9488',
    gradient: ['#14B8A6', '#0F766E'],
    darkBackground: 'rgba(20, 184, 166, 0.08)',
    accessibleLabel: 'Radix-2 Butterfly FFT Discrete Window Lattice Emblem',
    technicalKeywords: ['Cooley-Tukey FFT', 'FIR Parks-McClellan', 'IIR Butterworth', 'Polyphase Decimation'],
    svgPath: `
      <!-- FFT Butterfly Interconnects -->
      <line x1="8" y1="12" x2="40" y2="36" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="8" y1="36" x2="40" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="8" y1="12" x2="40" y2="12" stroke="currentColor" stroke-width="2" stroke-dasharray="2 2"/>
      <line x1="8" y1="36" x2="40" y2="36" stroke="currentColor" stroke-width="2" stroke-dasharray="2 2"/>
      <!-- Twiddle Factor W_N Complex Phase Node -->
      <circle cx="24" cy="24" r="5" fill="currentColor" fill-opacity="0.2" stroke="currentColor" stroke-width="1.8"/>
      <text x="21.5" y="27" fill="currentColor" font-size="6" font-family="serif" font-weight="bold">W</text>
      <!-- Discrete Sample Input/Output Nodes -->
      <circle cx="8" cy="12" r="2.5" fill="currentColor"/>
      <circle cx="8" cy="36" r="2.5" fill="currentColor"/>
      <circle cx="40" cy="12" r="2.5" fill="currentColor"/>
      <circle cx="40" cy="36" r="2.5" fill="currentColor"/>
    `
  },

  // 9. Telecommunications & RF Engineering
  'EC23C08': {
    code: 'EC23C08',
    disciplineName: 'Telecommunications & RF Engineering',
    professionalTitle: 'Analog & Digital Modulation, Information Theory',
    industryDomain: 'Wireless Telecom, 5G/6G & RF Infrastructure',
    subfield: 'RF & Communications',
    name: 'Analog & Digital Communication Systems',
    shortTitle: 'Communication Systems',
    category: 'SYSTEMS_SIGNALS',
    tier: 'Tier 3: Systems & Signals',
    semester: 5,
    credits: 4,
    symbolName: 'Smith Chart Reflection Circle',
    primaryColor: '#F97316',
    accentColor: '#EA580C',
    gradient: ['#F97316', '#C2410C'],
    darkBackground: 'rgba(249, 115, 22, 0.08)',
    accessibleLabel: 'RF Smith Chart and QAM Constellation Emblem',
    technicalKeywords: ['Smith Chart Gamma', 'QAM-16', 'Shannon Capacity', 'Friis Free-Space'],
    svgPath: `
      <!-- Smith Chart Unit Outer Circle |Gamma| = 1 -->
      <circle cx="24" cy="24" r="18" fill="none" stroke="currentColor" stroke-width="2"/>
      <!-- Constant Resistance Circles (r = 1 through center) -->
      <circle cx="30" cy="24" r="12" fill="none" stroke="currentColor" stroke-width="1.5" stroke-opacity="0.8"/>
      <circle cx="36" cy="24" r="6" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.6"/>
      <!-- Constant Reactance Arcs -->
      <path d="M6 24 C14 16, 28 14, 42 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="2 2"/>
      <path d="M6 24 C14 32, 28 34, 42 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="2 2"/>
      <!-- Prime Center Match Point (1 + j0) -->
      <circle cx="24" cy="24" r="2.5" fill="currentColor"/>
    `
  },

  // 10. Embedded Real-Time Systems
  'EC8702': {
    code: 'EC8702',
    disciplineName: 'Embedded Real-Time Systems',
    professionalTitle: 'Deterministic Firmware, RTOS & Microcontrollers',
    industryDomain: 'Automotive, Avionics & Critical Embedded',
    subfield: 'Embedded Systems',
    name: 'Embedded Systems & RTOS Architecture',
    shortTitle: 'Embedded Systems',
    category: 'EMBEDDED_VLSI',
    tier: 'Tier 4: Embedded Systems & Architecture',
    semester: 6,
    credits: 3,
    symbolName: 'NVIC Priority DMA Pipeline',
    primaryColor: '#6366F1',
    accentColor: '#4338CA',
    gradient: ['#6366F1', '#3730A3'],
    darkBackground: 'rgba(99, 102, 241, 0.08)',
    accessibleLabel: 'ARM Nested Vectored Interrupt Controller Microchip Emblem',
    technicalKeywords: ['NVIC Tail-Chaining', 'FreeRTOS Mutex', 'DMA Ping-Pong', 'HardFault Handler'],
    svgPath: `
      <!-- Microcontroller Dual-In-Line / QFP Die -->
      <rect x="12" y="12" width="24" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="2"/>
      <!-- Silicon Core Matrix -->
      <rect x="18" y="18" width="12" height="12" rx="1" fill="currentColor" fill-opacity="0.3" stroke="currentColor" stroke-width="1.2"/>
      <!-- Silicon Pins (North, South, East, West) -->
      <line x1="16" y1="6" x2="16" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="24" y1="6" x2="24" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="32" y1="6" x2="32" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="16" y1="36" x2="16" y2="42" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="24" y1="36" x2="24" y2="42" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="32" y1="36" x2="32" y2="42" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="6" y1="16" x2="12" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="6" y1="24" x2="12" y2="24" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="6" y1="32" x2="12" y2="32" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="36" y1="16" x2="42" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="36" y1="24" x2="42" y2="24" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="36" y1="32" x2="42" y2="32" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    `
  },

  // 11. ARM Cortex-M Microcontroller Engineering
  'STM32-ACADEMY': {
    code: 'STM32-ACADEMY',
    disciplineName: 'ARM Cortex-M Microcontroller Engineering',
    professionalTitle: 'Bare-Metal Silicon Drivers & Hardware Peripherals',
    industryDomain: 'Industrial Edge IoT & Precision Control',
    subfield: 'Microcontroller Engineering',
    name: 'ARM Cortex-M Firmware Mastery',
    shortTitle: 'STM32 Academy',
    category: 'EMBEDDED_VLSI',
    tier: 'Specialized Track: STM32 Academy',
    semester: 5,
    credits: 3,
    symbolName: 'Cortex-M Harvard Silicon Matrix',
    primaryColor: '#00D8F6',
    accentColor: '#0284C7',
    gradient: ['#00D8F6', '#0369A1'],
    darkBackground: 'rgba(0, 216, 246, 0.08)',
    accessibleLabel: 'STM32 ARM Cortex-M4 Microcontroller Die Emblem',
    technicalKeywords: ['Cortex-M4', 'CMSIS-Core', 'Bare-Metal HAL', 'DMA Circular Buffer'],
    svgPath: `
      <!-- Hexagonal MCU Shield -->
      <polygon points="24,6 40,15 40,33 24,42 8,33 8,15" fill="none" stroke="currentColor" stroke-width="2"/>
      <!-- Central ARM 32-bit Cortex Core -->
      <rect x="16" y="16" width="16" height="16" rx="2" fill="currentColor" fill-opacity="0.25" stroke="currentColor" stroke-width="1.5"/>
      <text x="18" y="27" fill="currentColor" font-size="8" font-family="monospace" font-weight="bold">M4</text>
      <!-- Silicon Trace Interconnects -->
      <line x1="24" y1="6" x2="24" y2="16" stroke="currentColor" stroke-width="1.5"/>
      <line x1="24" y1="32" x2="24" y2="42" stroke="currentColor" stroke-width="1.5"/>
      <line x1="8" y1="24" x2="16" y2="24" stroke="currentColor" stroke-width="1.5"/>
      <line x1="32" y1="24" x2="40" y2="24" stroke="currentColor" stroke-width="1.5"/>
    `
  },

  // 12. Internet of Things & Connected Systems
  'IOT8701': {
    code: 'IOT8701',
    disciplineName: 'Internet of Things & Connected Systems',
    professionalTitle: 'Wireless Embedded Networks & Cloud Edge Gateways',
    industryDomain: 'Smart Infrastructure & Industrial IoT',
    subfield: 'IoT & Wireless',
    name: 'ESP32 IoT Systems & FreeRTOS',
    shortTitle: 'ESP32 IoT Systems',
    category: 'EMBEDDED_VLSI',
    tier: 'Specialized Track: IoT Engineering',
    semester: 6,
    credits: 3,
    symbolName: 'Xtensa RF Antenna Transceiver',
    primaryColor: '#E11D48',
    accentColor: '#9F1239',
    gradient: ['#E11D48', '#881337'],
    darkBackground: 'rgba(225, 29, 72, 0.08)',
    accessibleLabel: 'ESP32 Wi-Fi Bluetooth Meander Antenna Emblem',
    technicalKeywords: ['Xtensa Dual-Core', 'MQTT / TLS', 'Deep-Sleep ULP', 'BLE GATT Mesh'],
    svgPath: `
      <!-- PCB Inverted-F Meander Antenna -->
      <path d="M10 24 h6 v-14 h4 v14 h4 v-14 h4 v14 h6" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      <!-- Radiating RF Wireless Wavefront Arcs -->
      <path d="M36 14 A 14 14 0 0 1 36 34" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <path d="M40 10 A 20 20 0 0 1 40 38" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-opacity="0.6"/>
      <!-- Ground Return Connection -->
      <line x1="10" y1="24" x2="10" y2="38" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="6" y1="38" x2="14" y2="38" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
    `
  },

  // 13. FPGA Digital Design & Verilog HDL
  'HDL6001': {
    code: 'HDL6001',
    disciplineName: 'FPGA Digital Design & Verilog HDL',
    professionalTitle: 'Synchronous RTL Synthesis & Digital Verification',
    industryDomain: 'FPGA Acceleration & ASIC Prototyping',
    subfield: 'FPGA & Hardware Synthesis',
    name: 'Verilog HDL & FPGA Hardware Synthesis',
    shortTitle: 'Verilog HDL & FPGA',
    category: 'EMBEDDED_VLSI',
    tier: 'Tier 4: Embedded Systems & Architecture',
    semester: 6,
    credits: 4,
    symbolName: 'FPGA Synchronous LUT Matrix',
    primaryColor: '#A855F7',
    accentColor: '#7E22CE',
    gradient: ['#A855F7', '#581C87'],
    darkBackground: 'rgba(168, 85, 247, 0.08)',
    accessibleLabel: 'FPGA Look-Up Table (LUT) Switch Box Routing Fabric Emblem',
    technicalKeywords: ['Verilog RTL', 'Non-blocking <=', '4-LUT Synthesis', 'Hold Timing Closure'],
    svgPath: `
      <!-- Synchronous 4-LUT Logic Cells (2x2 Matrix) -->
      <rect x="8" y="8" width="12" height="12" rx="2" fill="currentColor" fill-opacity="0.3" stroke="currentColor" stroke-width="1.8"/>
      <rect x="28" y="8" width="12" height="12" rx="2" fill="currentColor" fill-opacity="0.3" stroke="currentColor" stroke-width="1.8"/>
      <rect x="8" y="28" width="12" height="12" rx="2" fill="currentColor" fill-opacity="0.3" stroke="currentColor" stroke-width="1.8"/>
      <rect x="28" y="28" width="12" height="12" rx="2" fill="currentColor" fill-opacity="0.3" stroke="currentColor" stroke-width="1.8"/>
      <!-- Interconnect Switch Box Matrix Bus Lines -->
      <line x1="20" y1="14" x2="28" y2="14" stroke="currentColor" stroke-width="2"/>
      <line x1="20" y1="34" x2="28" y2="34" stroke="currentColor" stroke-width="2"/>
      <line x1="14" y1="20" x2="14" y2="28" stroke="currentColor" stroke-width="2"/>
      <line x1="34" y1="20" x2="34" y2="28" stroke="currentColor" stroke-width="2"/>
      <!-- Programmable Cross-Point Antifuse Via -->
      <circle cx="24" cy="24" r="2.5" fill="currentColor"/>
    `
  },

  // 14. Digital VLSI Design & Silicon Layout
  'VLSI7001': {
    code: 'VLSI7001',
    disciplineName: 'Digital VLSI Design & Silicon Layout',
    professionalTitle: 'Sub-Micron CMOS Physical Design & Timing Closure',
    industryDomain: 'Semiconductor Foundry & Silicon Tape-Out',
    subfield: 'VLSI & Physical Design',
    name: 'CMOS VLSI Design & Physical Architecture',
    shortTitle: 'CMOS VLSI Design',
    category: 'EMBEDDED_VLSI',
    tier: 'Tier 5: Advanced VLSI & Microelectronics',
    semester: 7,
    credits: 4,
    symbolName: 'CMOS Sub-Micron Transistor Layout',
    primaryColor: '#EAB308',
    accentColor: '#CA8A04',
    gradient: ['#EAB308', '#854D0E'],
    darkBackground: 'rgba(234, 179, 8, 0.08)',
    accessibleLabel: 'CMOS Inverter Gate Physical Silicon Layout Emblem',
    technicalKeywords: ['Elmore Delay', 'Logical Effort', 'RC Wire Delay', 'Clock Tree Skew'],
    svgPath: `
      <!-- Diffusion Wells (N-Well Top, P-Substrate Bottom) -->
      <rect x="6" y="8" width="36" height="12" rx="2" fill="currentColor" fill-opacity="0.2" stroke="currentColor" stroke-width="2"/>
      <rect x="6" y="28" width="36" height="12" rx="2" fill="currentColor" fill-opacity="0.2" stroke="currentColor" stroke-width="2"/>
      <!-- Polysilicon Gate Running Vertically Across Both Wells -->
      <rect x="21" y="4" width="6" height="40" rx="1.5" fill="currentColor" fill-opacity="0.75" stroke="currentColor" stroke-width="2"/>
      <!-- Metal 1 Contact Plugs (Vias) -->
      <circle cx="12" cy="14" r="2" fill="currentColor"/>
      <circle cx="36" cy="14" r="2" fill="currentColor"/>
      <circle cx="12" cy="34" r="2" fill="currentColor"/>
      <circle cx="36" cy="34" r="2" fill="currentColor"/>
    `
  }
};

/**
 * Default fallback emblem modeled after the VoltCore Silicon Microchip Chevron.
 */
export const DEFAULT_FALLBACK_EMBLEM: SubjectMetadata = {
  code: 'CORE-GENERIC',
  disciplineName: 'Advanced Engineering Discipline',
  professionalTitle: 'VoltCore Apex Applied Engineering System',
  industryDomain: 'Electronics & Computer Engineering',
  subfield: 'Core Engineering',
  name: 'VoltCore Apex Engineering Course',
  shortTitle: 'Engineering Discipline',
  category: 'FOUNDATION',
  tier: 'Core Engineering',
  semester: 1,
  credits: 3,
  symbolName: 'Silicon Chevron Beacon',
  primaryColor: '#00F0B5',
  accentColor: '#10B981',
  gradient: ['#00F0B5', '#00693E'],
  darkBackground: 'rgba(0, 240, 181, 0.08)',
  accessibleLabel: 'VoltCore Apex Academia Silicon Chevron Logo',
  technicalKeywords: ['Hardware-in-the-Loop', 'Simulation', 'Autonomous Cluster'],
  svgPath: `
    <!-- VoltCore Chevron Base & Micro-Die Beacon -->
    <path d="M14 14 L24 32 L34 14" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    <line x1="24" y1="24" x2="24" y2="38" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
    <circle cx="24" cy="14" r="3" fill="currentColor"/>
    <rect x="6" y="6" width="36" height="36" rx="8" fill="none" stroke="currentColor" stroke-width="1.8" stroke-opacity="0.4"/>
  `
};

/**
 * Retrieves subject metadata by course code with guaranteed fallback.
 */
export function getSubjectMetadata(courseCode?: string): SubjectMetadata {
  if (!courseCode) return DEFAULT_FALLBACK_EMBLEM;
  const normalized = courseCode.trim().toUpperCase();
  return ECE_SUBJECT_REGISTRY[normalized] || DEFAULT_FALLBACK_EMBLEM;
}

/**
 * Retrieves clean, professional engineering discipline name (no raw course codes).
 */
export function getDisciplineName(courseCode?: string): string {
  const meta = getSubjectMetadata(courseCode);
  return meta.disciplineName || meta.name;
}

/**
 * Retrieves full professional title for a discipline.
 */
export function getProfessionalTitle(courseCode?: string): string {
  const meta = getSubjectMetadata(courseCode);
  return meta.professionalTitle || meta.name;
}

/**
 * Returns list of all 14 official ECE curriculum subjects.
 */
export function listAllSubjects(): SubjectMetadata[] {
  return Object.values(ECE_SUBJECT_REGISTRY);
}

/**
 * Returns formatted SVG string for a subject emblem.
 */
export function getSubjectEmblemSvg(
  courseCode?: string,
  options?: { size?: number; className?: string; overrideColor?: string }
): string {
  const meta = getSubjectMetadata(courseCode);
  const size = options?.size || 48;
  const color = options?.overrideColor || meta.primaryColor;
  const cls = options?.className || '';

  return `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="${size}" height="${size}" class="${cls}" style="color: ${color};" aria-label="${meta.accessibleLabel}">
      ${meta.svgPath}
    </svg>
  `.trim();
}
