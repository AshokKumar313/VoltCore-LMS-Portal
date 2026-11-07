/**
 * ========================================================================================
 * VoltCore Apex Academia - ECE Canva-Inspired Subject Emblem & Vector Logo Registry
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Module: src/data/subjectRegistry.ts
 * Platform Lead & Educational Systems Director: Ashok Kumar A (2023MITEC042)
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 *
 * Capabilities:
 *   1. Complete 14 Core ECE Disciplines Registry
 *   2. Bespoke Precision Vector SVG Geometries (Bandgap, Op-Amp, Smith Chart, FFT, CMOS, etc.)
 *   3. Harmonious Color Palettes & Gradient Pairs (Dynamic 18-Theme Adaptive)
 *   4. Technical Discipline Keywords & Pedagogical Taxonomies
 *   5. Robust Fallback Emblem for Unregistered / Elective Courses
 * ========================================================================================
 */

export interface SubjectMetadata {
  code: string;
  name: string;
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

  // 2. Semiconductor Physics & Devices
  'EC23C02': {
    code: 'EC23C02',
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

  // 3. Electronic Devices & Solid-State Circuits
  'EC23C03': {
    code: 'EC23C03',
    name: 'Electronic Devices & Solid-State Circuits',
    shortTitle: 'Electronic Devices',
    category: 'CORE_ANALOG',
    tier: 'Tier 2: Core Engineering',
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
      <polygon points="14,14 14,34 32,24" fill="currentColor" fill-opacity="0.25" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>
      <line x1="32" y1="12" x2="32" y2="36" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
      <line x1="6" y1="24" x2="14" y2="24" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="32" y1="24" x2="42" y2="24" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <!-- Breakdown Glow Rings -->
      <circle cx="23" cy="24" r="14" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.3" stroke-dasharray="2 4"/>
    `
  },

  // 4. Analog Integrated Electronics
  'EC23C05': {
    code: 'EC23C05',
    name: 'Analog Integrated Electronics',
    shortTitle: 'Analog Electronics',
    category: 'CORE_ANALOG',
    tier: 'Tier 2: Core Engineering',
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
      <!-- Op-Amp Triangle -->
      <polygon points="12,8 12,40 38,24" fill="currentColor" fill-opacity="0.18" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>
      <!-- Inverting and Non-Inverting Inputs -->
      <line x1="4" y1="16" x2="12" y2="16" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="4" y1="32" x2="12" y2="32" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="38" y1="24" x2="44" y2="24" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <!-- Plus and Minus Glyphs -->
      <line x1="16" y1="16" x2="20" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="16" y1="32" x2="20" y2="32" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="18" y1="30" x2="18" y2="34" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    `
  },

  // 5. Digital Electronics & Logic Design
  'EC23C06': {
    code: 'EC23C06',
    name: 'Digital Electronics & Logic Design',
    shortTitle: 'Digital Electronics',
    category: 'CORE_DIGITAL',
    tier: 'Tier 2: Core Engineering',
    semester: 3,
    credits: 4,
    symbolName: 'K-Map Logic Gate Matrix',
    primaryColor: '#8B5CF6',
    accentColor: '#6D28D9',
    gradient: ['#8B5CF6', '#5B21B6'],
    darkBackground: 'rgba(139, 92, 246, 0.08)',
    accessibleLabel: 'NAND Logic Gate with Binary Grid Emblem',
    technicalKeywords: ['K-Map', 'Quine-McCluskey', 'Synchronous FSM', 'Setup/Hold Slack'],
    svgPath: `
      <!-- NAND Gate Profile -->
      <path d="M10 12h12a12 12 0 0 1 0 24H10z" fill="currentColor" fill-opacity="0.2" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>
      <!-- Inputs -->
      <line x1="4" y1="18" x2="10" y2="18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="4" y1="30" x2="10" y2="30" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <!-- Negation Bubble -->
      <circle cx="36" cy="24" r="3" fill="none" stroke="currentColor" stroke-width="2"/>
      <line x1="39" y1="24" x2="44" y2="24" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <!-- Internal Binary Clock Pulse -->
      <polyline points="16,21 19,21 19,27 22,27" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
    `
  },

  // 6. Signals and Linear Systems
  'EC23C04': {
    code: 'EC23C04',
    name: 'Signals and Linear Systems',
    shortTitle: 'Signals & Systems',
    category: 'SYSTEMS_SIGNALS',
    tier: 'Tier 2: Core Engineering',
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
      <!-- Orthogonal S-Plane Axes -->
      <line x1="6" y1="24" x2="42" y2="24" stroke="currentColor" stroke-width="1.5" stroke-opacity="0.6"/>
      <line x1="24" y1="6" x2="24" y2="42" stroke="currentColor" stroke-width="1.5" stroke-opacity="0.6"/>
      <!-- Continuous Harmonic Sinusoid -->
      <path d="M6 24c4-12 8-12 12 0s8 12 12 0 8-12 12 0" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <!-- S-Plane Poles and Zeros -->
      <line x1="16" y1="16" x2="20" y2="20" stroke="currentColor" stroke-width="2"/>
      <line x1="20" y1="16" x2="16" y2="20" stroke="currentColor" stroke-width="2"/>
      <circle cx="32" cy="18" r="2.5" fill="none" stroke="currentColor" stroke-width="2"/>
    `
  },

  // 7. Control Systems Engineering
  'EC23C07': {
    code: 'EC23C07',
    name: 'Control Systems Engineering',
    shortTitle: 'Control Systems',
    category: 'SYSTEMS_SIGNALS',
    tier: 'Tier 3: Systems Specialization',
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
      <!-- Summing Junction Circle -->
      <circle cx="14" cy="24" r="5" fill="none" stroke="currentColor" stroke-width="2.5"/>
      <line x1="11" y1="24" x2="17" y2="24" stroke="currentColor" stroke-width="1.5"/>
      <line x1="14" y1="21" x2="14" y2="27" stroke="currentColor" stroke-width="1.5"/>
      <!-- Feedforward to Plant G(s) -->
      <line x1="4" y1="24" x2="9" y2="24" stroke="currentColor" stroke-width="2"/>
      <line x1="19" y1="24" x2="26" y2="24" stroke="currentColor" stroke-width="2"/>
      <!-- Plant G(s) Box -->
      <rect x="26" y="16" width="14" height="16" rx="3" fill="currentColor" fill-opacity="0.2" stroke="currentColor" stroke-width="2.5"/>
      <path d="M30 22h6M30 26h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <!-- Feedback Loop with Return Path -->
      <path d="M40 24h4v14H14v-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <polygon points="14,33 11,37 17,37" fill="currentColor"/>
    `
  },

  // 8. Digital Signal Processing
  'EC23S01': {
    code: 'EC23S01',
    name: 'Digital Signal Processing Practice',
    shortTitle: 'Python DSP',
    category: 'SYSTEMS_SIGNALS',
    tier: 'Tier 3: Systems Specialization',
    semester: 4,
    credits: 2,
    symbolName: 'Radix-2 FFT Butterfly Ring',
    primaryColor: '#14B8A6',
    accentColor: '#0D9488',
    gradient: ['#14B8A6', '#0F766E'],
    darkBackground: 'rgba(20, 184, 166, 0.08)',
    accessibleLabel: 'Radix-2 Butterfly FFT Discrete Window Lattice Emblem',
    technicalKeywords: ['Cooley-Tukey FFT', 'FIR Parks-McClellan', 'IIR Butterworth', 'Polyphase Decimation'],
    svgPath: `
      <!-- FFT Butterfly Cross Lattice -->
      <line x1="8" y1="14" x2="26" y2="34" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="8" y1="34" x2="26" y2="14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <!-- Discrete Signal Inputs & Outputs -->
      <line x1="26" y1="14" x2="40" y2="14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="26" y1="34" x2="40" y2="34" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <circle cx="8" cy="14" r="3" fill="currentColor"/>
      <circle cx="8" cy="34" r="3" fill="currentColor"/>
      <circle cx="40" cy="14" r="3" fill="currentColor"/>
      <circle cx="40" cy="34" r="3" fill="currentColor"/>
      <!-- Twiddle Factor W_N Vector Circle -->
      <circle cx="24" cy="24" r="15" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="3 3"/>
      <text x="24" y="27" font-size="7" font-family="monospace" text-anchor="middle" fill="currentColor" font-weight="bold">W_N</text>
    `
  },

  // 9. Communication Systems
  'EC23C08': {
    code: 'EC23C08',
    name: 'Analog & Digital Communication Systems',
    shortTitle: 'Communication Systems',
    category: 'SYSTEMS_SIGNALS',
    tier: 'Tier 3: Systems Specialization',
    semester: 4,
    credits: 4,
    symbolName: 'Smith Chart Reflection Circle',
    primaryColor: '#F97316',
    accentColor: '#EA580C',
    gradient: ['#F97316', '#C2410C'],
    darkBackground: 'rgba(249, 115, 22, 0.08)',
    accessibleLabel: 'RF Smith Chart and QAM Constellation Emblem',
    technicalKeywords: ['Smith Chart Gamma', 'QAM-16', 'Shannon Capacity', 'Friis Free-Space'],
    svgPath: `
      <!-- Smith Chart Normalized Outer Circle -->
      <circle cx="24" cy="24" r="18" fill="none" stroke="currentColor" stroke-width="2.5"/>
      <!-- Real Axis -->
      <line x1="6" y1="24" x2="42" y2="24" stroke="currentColor" stroke-width="2"/>
      <!-- Internal Constant Resistance Circles -->
      <circle cx="30" cy="24" r="12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-opacity="0.8"/>
      <circle cx="34" cy="24" r="8" fill="none" stroke="currentColor" stroke-width="1.5" stroke-opacity="0.6"/>
      <!-- Constant Reactance Arcs -->
      <path d="M42 24c0-8-8-12-16-12" fill="none" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2 2"/>
      <path d="M42 24c0 8-8 12-16 12" fill="none" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2 2"/>
      <!-- Reflection Coefficient Gamma Beacon -->
      <circle cx="28" cy="20" r="2.5" fill="currentColor"/>
    `
  },

  // 10. Embedded Systems & RTOS Architecture
  'EC8702': {
    code: 'EC8702',
    name: 'Embedded Systems & RTOS Architecture',
    shortTitle: 'Embedded Systems',
    category: 'EMBEDDED_VLSI',
    tier: 'Tier 3: Systems Specialization',
    semester: 4,
    credits: 4,
    symbolName: 'NVIC Priority DMA Pipeline',
    primaryColor: '#6366F1',
    accentColor: '#4338CA',
    gradient: ['#6366F1', '#3730A3'],
    darkBackground: 'rgba(99, 102, 241, 0.08)',
    accessibleLabel: 'ARM Nested Vectored Interrupt Controller Microchip Emblem',
    technicalKeywords: ['NVIC Tail-Chaining', 'FreeRTOS Mutex', 'DMA Ping-Pong', 'HardFault Handler'],
    svgPath: `
      <!-- Microcontroller Quad Flat Package Silicon Base -->
      <rect x="12" y="12" width="24" height="24" rx="4" fill="currentColor" fill-opacity="0.22" stroke="currentColor" stroke-width="2.5"/>
      <!-- External Peripheral Bus Pins -->
      <line x1="16" y1="6" x2="16" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="24" y1="6" x2="24" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="32" y1="6" x2="32" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="16" y1="36" x2="16" y2="42" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="24" y1="36" x2="24" y2="42" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="32" y1="36" x2="32" y2="42" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="6" y1="20" x2="12" y2="20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="6" y1="28" x2="12" y2="28" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="36" y1="20" x2="42" y2="20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="36" y1="28" x2="42" y2="28" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <!-- Inner Core Ring -->
      <circle cx="24" cy="24" r="5" fill="none" stroke="currentColor" stroke-width="1.8"/>
      <circle cx="24" cy="24" r="2" fill="currentColor"/>
    `
  },

  // 11. ARM Cortex-M Firmware Mastery
  'STM32-ACADEMY': {
    code: 'STM32-ACADEMY',
    name: 'ARM Cortex-M Firmware Mastery',
    shortTitle: 'STM32 Academy',
    category: 'EMBEDDED_VLSI',
    tier: 'Tier 3: Capstone Specialization',
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
      <!-- High-Tech Silicon Die with Dual Harvard Bus -->
      <rect x="8" y="8" width="32" height="32" rx="6" fill="currentColor" fill-opacity="0.18" stroke="currentColor" stroke-width="2.5"/>
      <!-- Internal Bus Matrix Cross -->
      <line x1="8" y1="24" x2="40" y2="24" stroke="currentColor" stroke-width="1.8" stroke-dasharray="2 3"/>
      <line x1="24" y1="8" x2="24" y2="40" stroke="currentColor" stroke-width="1.8" stroke-dasharray="2 3"/>
      <!-- Central ARM RISC Core -->
      <rect x="18" y="18" width="12" height="12" rx="2" fill="currentColor" fill-opacity="0.4" stroke="currentColor" stroke-width="2"/>
      <circle cx="24" cy="24" r="2" fill="currentColor"/>
      <!-- Corner Pin Alignment Reticles -->
      <circle cx="12" cy="12" r="1.5" fill="currentColor"/>
      <circle cx="36" cy="12" r="1.5" fill="currentColor"/>
      <circle cx="12" cy="36" r="1.5" fill="currentColor"/>
      <circle cx="36" cy="36" r="1.5" fill="currentColor"/>
    `
  },

  // 12. ESP32 IoT Systems
  'IOT8701': {
    code: 'IOT8701',
    name: 'ESP32 IoT Systems & FreeRTOS',
    shortTitle: 'ESP32 IoT Systems',
    category: 'EMBEDDED_VLSI',
    tier: 'Tier 3: Capstone Specialization',
    semester: 5,
    credits: 3,
    symbolName: 'Xtensa RF Antenna Transceiver',
    primaryColor: '#E11D48',
    accentColor: '#9F1239',
    gradient: ['#E11D48', '#881337'],
    darkBackground: 'rgba(225, 29, 72, 0.08)',
    accessibleLabel: 'ESP32 Wi-Fi Bluetooth Meander Antenna Emblem',
    technicalKeywords: ['Xtensa Dual-Core', 'MQTT / TLS', 'Deep-Sleep ULP', 'BLE GATT Mesh'],
    svgPath: `
      <!-- PCB Trace Meander Antenna -->
      <polyline points="10,24 10,12 16,12 16,20 22,20 22,12 28,12 28,20 34,20 34,12 38,12 38,24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      <!-- RF Transmission Waves -->
      <path d="M16 28c4 4 12 4 16 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <path d="M12 34c8 8 16 8 24 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <path d="M8 40c12 12 20 12 32 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <circle cx="24" cy="24" r="2.5" fill="currentColor"/>
    `
  },

  // 13. Verilog HDL & FPGA Hardware Synthesis
  'HDL6001': {
    code: 'HDL6001',
    name: 'Verilog HDL & FPGA Hardware Synthesis',
    shortTitle: 'Verilog HDL & FPGA',
    category: 'EMBEDDED_VLSI',
    tier: 'Tier 3: Systems Specialization',
    semester: 5,
    credits: 4,
    symbolName: 'FPGA Synchronous LUT Matrix',
    primaryColor: '#A855F7',
    accentColor: '#7E22CE',
    gradient: ['#A855F7', '#581C87'],
    darkBackground: 'rgba(168, 85, 247, 0.08)',
    accessibleLabel: 'FPGA Look-Up Table (LUT) Switch Box Routing Fabric Emblem',
    technicalKeywords: ['Verilog RTL', 'Non-blocking <=', '4-LUT Synthesis', 'Hold Timing Closure'],
    svgPath: `
      <!-- FPGA 4-LUT Hex Matrix Grid -->
      <rect x="8" y="8" width="14" height="14" rx="2" fill="currentColor" fill-opacity="0.25" stroke="currentColor" stroke-width="2"/>
      <rect x="26" y="8" width="14" height="14" rx="2" fill="currentColor" fill-opacity="0.25" stroke="currentColor" stroke-width="2"/>
      <rect x="8" y="26" width="14" height="14" rx="2" fill="currentColor" fill-opacity="0.25" stroke="currentColor" stroke-width="2"/>
      <rect x="26" y="26" width="14" height="14" rx="2" fill="currentColor" fill-opacity="0.25" stroke="currentColor" stroke-width="2"/>
      <!-- Interconnect Switchbox Lines -->
      <line x1="15" y1="22" x2="15" y2="26" stroke="currentColor" stroke-width="2.5"/>
      <line x1="33" y1="22" x2="33" y2="26" stroke="currentColor" stroke-width="2.5"/>
      <line x1="22" y1="15" x2="26" y2="15" stroke="currentColor" stroke-width="2.5"/>
      <line x1="22" y1="33" x2="26" y2="33" stroke="currentColor" stroke-width="2.5"/>
      <!-- Programmable Crosspoint Center -->
      <circle cx="24" cy="24" r="3" fill="currentColor"/>
    `
  },

  // 14. CMOS VLSI Design & Physical Architecture
  'VLSI7001': {
    code: 'VLSI7001',
    name: 'CMOS VLSI Design & Physical Architecture',
    shortTitle: 'CMOS VLSI Design',
    category: 'EMBEDDED_VLSI',
    tier: 'Tier 3: Capstone Specialization',
    semester: 6,
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
