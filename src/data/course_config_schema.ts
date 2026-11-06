/**
 * ========================================================================================
 * VoltCore Apex Academia - Course Configuration Schema & Registry Architecture
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead & Systems Architect: Ashok Kumar A
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 *
 * Provides a standardized, data-driven contract powering modular course experience hubs:
 *   - Metadata, categorization & Anna University Regulation 2023 credits
 *   - Syllabus units, lecture hours & textbook mappings
 *   - Prerequisite DAG dependencies & corequisites
 *   - Hardware lab & simulation platform bindings
 *   - Visual theme tokens (colors, gradients, icons)
 * ========================================================================================
 */

export interface CourseOutcome {
  id: string; // e.g. "CO1"
  description: string;
  bloomLevel: "L1 (Remember)" | "L2 (Understand)" | "L3 (Apply)" | "L4 (Analyze)" | "L5 (Evaluate)" | "L6 (Create)";
  mappedPOs: string[]; // e.g. ["PO1", "PO2", "PO5"]
  mappedPSOs: string[]; // e.g. ["PSO1", "PSO2"]
  targetAttainmentPct: number;
}

export interface SyllabusUnit {
  unitNumber: number;
  title: string;
  hours: number;
  description: string;
  topics: string[];
  labComponents?: string[];
  keyFormulas?: string[];
  textbookReferences?: string[];
}

export interface PrerequisiteLink {
  fromCourse: string;
  toCourse: string;
  relationship: "hard" | "soft";
  topicBridge: string;
}

export type CourseThemeFamily = "emerald" | "amber" | "cyan" | "indigo";

export interface CourseVisualTheme {
  themeFamily: CourseThemeFamily;
  primaryColor: string; // Hex or CSS var
  accentGlow: string;
  badgeBg: string;
  badgeText: string;
  borderAccent: string;
  gradientFrom: string;
  gradientTo: string;
  icon: string;
  cardClass: string;
  glowClass: string;
  badgeClass: string;
  activeTabClass: string;
  textAccentClass: string;
}

export interface LabSimulationConfig {
  hasHardwareLab: boolean;
  hasVirtualSimulation: boolean;
  simulationPlatform: "Python SciPy" | "LTspice" | "Optics Ray Tracer" | "Wokwi Embedded" | "ModelSim Verilog";
  defaultSketchOrScript?: string;
  apparatusList: string[];
  labRoom: string;
}

export interface CourseConfig {
  code: string;
  title: string;
  shortTitle: string;
  slug: string;
  semester: number;
  credits: number;
  lectureTutorialLabHours: string; // e.g. "3-0-0" or "0-0-4"
  category: "Professional Core (PCC)" | "Employability Enhancement (EEC)" | "Professional Elective (PEC)" | "Foundation (ESC)";
  regulation: "Anna University Regulation 2023";
  department: "Department of Electronics Engineering";
  campus: "Madras Institute of Technology (MIT) Campus, Anna University";
  description: string;
  visualTheme: CourseVisualTheme;
  prerequisites: string[];
  corequisites: string[];
  prerequisiteDag: PrerequisiteLink[];
  courseOutcomes: CourseOutcome[];
  syllabusUnits: SyllabusUnit[];
  labSimulation: LabSimulationConfig;
  textbooks: string[];
  referenceBooks: string[];
  nptelCourseId?: string;
}

// ---------------------------------------------------------------------------
// DATA-DRIVEN COURSE REGISTRY (PRIORITY COURSES)
// ---------------------------------------------------------------------------

export const PRIORITY_COURSES: Record<string, CourseConfig> = {
  // 1. EC23S01: Numerical and Signal Processing Practice Through Python
  "EC23S01": {
    code: "EC23S01",
    title: "Numerical and Signal Processing Practice Through Python",
    shortTitle: "DSP & Python Computing",
    slug: "numerical-dsp-python",
    semester: 4,
    credits: 2,
    lectureTutorialLabHours: "0-0-4",
    category: "Employability Enhancement (EEC)",
    regulation: "Anna University Regulation 2023",
    department: "Department of Electronics Engineering",
    campus: "Madras Institute of Technology (MIT) Campus, Anna University",
    description: "Computational signal processing laboratory utilizing Python (NumPy, SciPy, Matplotlib) for discrete-time signal transformation, FFT spectral analysis, IIR/FIR filter synthesis, and real-time audio/sensor telemetry.",
    visualTheme: {
      themeFamily: "emerald",
      primaryColor: "#00F0B5",
      accentGlow: "rgba(0, 240, 181, 0.25)",
      badgeBg: "rgba(0, 105, 62, 0.4)",
      badgeText: "#00F0B5",
      borderAccent: "rgba(0, 240, 181, 0.3)",
      gradientFrom: "#00693E",
      gradientTo: "#00F0B5",
      icon: "🐍",
      cardClass: "course-card-emerald",
      glowClass: "course-glow-emerald",
      badgeClass: "course-badge-emerald",
      activeTabClass: "bg-[#00F0B5] text-slate-950 font-bold shadow-course-emerald-glow",
      textAccentClass: "text-[#00F0B5]"
    },
    prerequisites: ["Signals and Systems (EC23C04)", "Linear Algebra & Numerical Methods (MA23C01)"],
    corequisites: ["Digital Signal Processing (EC23C06)"],
    prerequisiteDag: [
      { fromCourse: "MA23C01", toCourse: "EC23S01", relationship: "hard", topicBridge: "Matrix Algebra & Eigenvalues for Signal Decompositions" },
      { fromCourse: "EC23C04", toCourse: "EC23S01", relationship: "hard", topicBridge: "CT/DT Fourier Transforms & Convolution" }
    ],
    courseOutcomes: [
      {
        id: "CO1",
        description: "Vectorize discrete-time signals, elementary functions, and convolution operations using NumPy arrays.",
        bloomLevel: "L3 (Apply)",
        mappedPOs: ["PO1", "PO2", "PO5"],
        mappedPSOs: ["PSO1"],
        targetAttainmentPct: 75.0
      },
      {
        id: "CO2",
        description: "Compute Discrete Fourier Transform (DFT) and radix-2 Fast Fourier Transform (FFT) algorithms for spectral leakage analysis.",
        bloomLevel: "L4 (Analyze)",
        mappedPOs: ["PO1", "PO2", "PO3", "PO5"],
        mappedPSOs: ["PSO1", "PSO2"],
        targetAttainmentPct: 70.0
      },
      {
        id: "CO3",
        description: "Synthesize Butterworth and Chebyshev IIR filters using bilinear transformation with frequency pre-warping.",
        bloomLevel: "L5 (Evaluate)",
        mappedPOs: ["PO1", "PO3", "PO5"],
        mappedPSOs: ["PSO1"],
        targetAttainmentPct: 70.0
      },
      {
        id: "CO4",
        description: "Design linear-phase FIR digital filters using Hamming, Hanning, and Kaiser windowing techniques.",
        bloomLevel: "L5 (Evaluate)",
        mappedPOs: ["PO2", "PO3", "PO5"],
        mappedPSOs: ["PSO1"],
        targetAttainmentPct: 70.0
      },
      {
        id: "CO5",
        description: "Implement Least-Mean-Squares (LMS) adaptive noise cancellation for dynamic biological and acoustic signals.",
        bloomLevel: "L6 (Create)",
        mappedPOs: ["PO1", "PO3", "PO4", "PO5"],
        mappedPSOs: ["PSO2"],
        targetAttainmentPct: 68.0
      }
    ],
    syllabusUnits: [
      {
        unitNumber: 1,
        title: "Python Vectorized Signal Foundations",
        hours: 8,
        description: "NumPy ndarray memory layout, broadcasting rules, discrete unit impulse, step, ramp, complex exponential, and linear/circular convolution.",
        topics: [
          "Discrete-time signal representations in NumPy arrays",
          "Linear convolution vs Circular convolution via zero-padding",
          "Correlation: Auto-correlation, cross-correlation, and noise detection",
          "Sampling theorem validation & anti-aliasing filter simulation"
        ],
        labComponents: ["Lab 1: Discrete signal generation & convolution bench", "Lab 2: Sampling & aliasing frequency domain visualizer"],
        keyFormulas: ["y[n] = \\sum_{k=-\\infty}^{\\infty} x[k]h[n-k]", "f_s \\ge 2 f_{max}"]
      },
      {
        unitNumber: 2,
        title: "DFT & Fast Fourier Transform (FFT) Implementations",
        hours: 10,
        description: "Direct DFT computation, Radix-2 Cooley-Tukey Decimation-in-Time (DIT) FFT, spectral leakage, and windowing effects.",
        topics: [
          "DFT matrix formulation & computational complexity O(N^2) vs O(N log N)",
          "Radix-2 DIT-FFT bit-reversal indexing and butterfly operations",
          "Spectral resolution vs window length trade-offs",
          "Short-Time Fourier Transform (STFT) & spectrogram visualization"
        ],
        labComponents: ["Lab 3: 64-point Radix-2 DIT-FFT butterfly computation", "Lab 4: Audio spectrogram analysis of dual-tone multi-frequency (DTMF)"],
        keyFormulas: ["X[k] = \\sum_{n=0}^{N-1} x[n] W_N^{kn}", "W_N = e^{-j 2\\pi / N}"]
      },
      {
        unitNumber: 3,
        title: "IIR Digital Filter Synthesis",
        hours: 10,
        description: "Analog prototype approximations (Butterworth, Chebyshev Type I/II, Elliptic), Bilinear Transformation, and stability analysis.",
        topics: [
          "Analog filter poles placement & Butterworth maximally flat magnitude",
          "Chebyshev ripple factor and passband/stopband attenuation",
          "Bilinear Transformation and frequency warping correction",
          "Direct Form I/II and Cascade/Parallel biquad realization"
        ],
        labComponents: ["Lab 5: 4th-order Butterworth low-pass filter design", "Lab 6: Bilinear transformation warping curve verification"],
        keyFormulas: ["\\Omega = \\frac{2}{T} \\tan\\left(\\frac{\\omega}{2}\\right)", "|H(j\\Omega)|^2 = \\frac{1}{1 + (\\Omega/\\Omega_c)^{2N}}"]
      },
      {
        unitNumber: 4,
        title: "FIR Filter Design & Windowing Techniques",
        hours: 10,
        description: "Linear-phase conditions, Gibbs phenomenon, Fourier transform windowing (Rectangular, Hamming, Hanning, Blackman, Kaiser).",
        topics: [
          "Symmetric and anti-symmetric impulse response constraints for linear phase",
          "Window function spectral characteristics (mainlobe width vs sidelobe attenuation)",
          "Optimal equiripple FIR filter design (Parks-McClellan algorithm)",
          "Polyphase filter banks and multirate decimation/interpolation"
        ],
        labComponents: ["Lab 7: Linear-phase bandpass filter via Kaiser window", "Lab 8: Multirate sampling rate conversion by factor L/M"],
        keyFormulas: ["w[n] = 0.54 - 0.46 \\cos\\left(\\frac{2\\pi n}{M}\\right)", "\\tau_g = -\\frac{d\\theta(\\omega)}{d\\omega} = \\text{const}"]
      },
      {
        unitNumber: 5,
        title: "Adaptive Filters & Real-Time Sensor Telemetry",
        hours: 10,
        description: "Weiner filter theory, stochastic gradient descent, LMS adaptive algorithm, and active noise cancellation in biomedical/telemetry streams.",
        topics: [
          "Mean-Square-Error (MSE) performance surface and gradient vector",
          "LMS weight adaptation equation and convergence stability bounds",
          "Echo cancellation and adaptive notch filter for 50 Hz power-line interference",
          "Serial streaming of real-time sensor packets from ESP32 to Python Matplotlib"
        ],
        labComponents: ["Lab 9: Adaptive 50Hz notch filter for ECG telemetry", "Lab 10: Real-time sensor streaming via PySerial / WebSockets"],
        keyFormulas: ["w[n+1] = w[n] + 2 \\mu e[n] x[n]", "0 < \\mu < \\frac{1}{\\lambda_{max}}"]
      }
    ],
    labSimulation: {
      hasHardwareLab: true,
      hasVirtualSimulation: true,
      simulationPlatform: "Python SciPy",
      defaultSketchOrScript: `import numpy as np\nimport scipy.signal as signal\n\n# Design 4th Order Butterworth Lowpass Filter\nfs = 8000  # Sampling frequency (Hz)\nfc = 1200  # Cutoff frequency (Hz)\nb, a = signal.butter(4, fc / (fs / 2), btype='low')\nw, h = signal.freqz(b, a)\nprint(f"Filter Poles: {signal.tf2zpk(b, a)[1]}")`,
      apparatusList: ["Workstation with Python 3.14 + NumPy / SciPy", "Analog Discovery 2 / Digilent USB Oscilloscope", "Audio Interface with Stereo Line In/Out"],
      labRoom: "MIT Chromepet DSP & Signal Simulation Center - Lab 302"
    },
    textbooks: [
      "Oppenheim, A. V., & Schafer, R. W. (2010). Discrete-Time Signal Processing (3rd ed.). Pearson.",
      "Proakis, J. G., & Manolakis, D. G. (2007). Digital Signal Processing: Principles, Algorithms, and Applications (4th ed.). Pearson."
    ],
    referenceBooks: [
      "Mitra, S. K. (2011). Digital Signal Processing: A Computer-Based Approach (4th ed.). McGraw-Hill.",
      "Unpingco, J. (2014). Python for Signal Processing. Springer."
    ],
    nptelCourseId: "noc23-ee91"
  },

  // 2. EC23C03: Electronic Devices
  "EC23C03": {
    code: "EC23C03",
    title: "Electronic Devices",
    shortTitle: "Semiconductors & Devices",
    slug: "electronic-devices",
    semester: 3,
    credits: 3,
    lectureTutorialLabHours: "3-0-0",
    category: "Professional Core (PCC)",
    regulation: "Anna University Regulation 2023",
    department: "Department of Electronics Engineering",
    campus: "Madras Institute of Technology (MIT) Campus, Anna University",
    description: "Fundamental semiconductor physics and charge carrier dynamics, PN junctions, Zener diodes, Bipolar Junction Transistors (BJT), JFETs, and modern nanoscale MOSFETs.",
    visualTheme: {
      themeFamily: "amber",
      primaryColor: "#F59E0B",
      accentGlow: "rgba(245, 158, 11, 0.25)",
      badgeBg: "rgba(180, 83, 9, 0.4)",
      badgeText: "#FCD34D",
      borderAccent: "rgba(245, 158, 11, 0.3)",
      gradientFrom: "#B45309",
      gradientTo: "#F59E0B",
      icon: "⚡",
      cardClass: "course-card-amber",
      glowClass: "course-glow-amber",
      badgeClass: "course-badge-amber",
      activeTabClass: "bg-[#F59E0B] text-slate-950 font-bold shadow-course-amber-glow",
      textAccentClass: "text-[#F59E0B]"
    },
    prerequisites: ["Engineering Physics (PH23C01)", "Electric Circuit Analysis (EE23C01)"],
    corequisites: ["Electronic Circuits I (EC23C05)"],
    prerequisiteDag: [
      { fromCourse: "PH23C01", toCourse: "EC23C03", relationship: "hard", topicBridge: "Energy Band Theory, Fermi Level & Quantum Mechanics" }
    ],
    courseOutcomes: [
      {
        id: "CO1",
        description: "Analyze carrier concentration, drift-diffusion mechanisms, and Einstein relations in intrinsic and extrinsic semiconductors.",
        bloomLevel: "L4 (Analyze)",
        mappedPOs: ["PO1", "PO2"],
        mappedPSOs: ["PSO1"],
        targetAttainmentPct: 75.0
      },
      {
        id: "CO2",
        description: "Evaluate forward/reverse bias IV characteristics, junction capacitance, and breakdown phenomena of PN and Zener diodes.",
        bloomLevel: "L4 (Analyze)",
        mappedPOs: ["PO1", "PO2", "PO3"],
        mappedPSOs: ["PSO1"],
        targetAttainmentPct: 72.0
      },
      {
        id: "CO3",
        description: "Model BJT operation in CB, CE, and CC configurations using Ebers-Moll equations and hybrid-pi parameters.",
        bloomLevel: "L4 (Analyze)",
        mappedPOs: ["PO1", "PO2", "PO3"],
        mappedPSOs: ["PSO1"],
        targetAttainmentPct: 70.0
      },
      {
        id: "CO4",
        description: "Characterize JFET and MOSFET drain/transfer curves, threshold voltage, and short-channel effects.",
        bloomLevel: "L5 (Evaluate)",
        mappedPOs: ["PO1", "PO2", "PO4"],
        mappedPSOs: ["PSO1", "PSO2"],
        targetAttainmentPct: 68.0
      },
      {
        id: "CO5",
        description: "Examine operating mechanisms of optoelectronic devices including Photodiodes, Solar Cells, and LEDs.",
        bloomLevel: "L3 (Apply)",
        mappedPOs: ["PO1", "PO2", "PO7"],
        mappedPSOs: ["PSO1"],
        targetAttainmentPct: 70.0
      }
    ],
    syllabusUnits: [
      {
        unitNumber: 1,
        title: "Semiconductor Physics & Carrier Transport",
        hours: 9,
        description: "Energy bands in solids, intrinsic/extrinsic semiconductors, Fermi-Dirac distribution, carrier density equations, drift, diffusion, mobility, Hall effect.",
        topics: [
          "Direct vs indirect bandgap semiconductors (Si, Ge, GaAs)",
          "Carrier generation and recombination; continuity equation",
          "Drift velocity, saturation velocity, and low-field mobility",
          "Hall effect and determination of majority carrier type"
        ],
        keyFormulas: ["n_i^2 = n_o p_o = N_c N_v e^{-E_g / kT}", "J_n = q n \\mu_n E + q D_n \\frac{dn}{dx}"]
      },
      {
        unitNumber: 2,
        title: "PN Junction & Zener Diodes",
        hours: 9,
        description: "Built-in potential, space charge region, Shockley diode equation, depletion/diffusion capacitance, Zener and Avalanche breakdown.",
        topics: [
          "Built-in potential barrier calculation from doping profiles",
          "Space charge width under reverse bias and punch-through",
          "Diode switching transients and reverse recovery time (trr)",
          "Zener diode voltage regulator circuit design"
        ],
        keyFormulas: ["V_{bi} = \\frac{kT}{q} \\ln\\left(\\frac{N_a N_d}{n_i^2}\\right)", "I = I_s \\left(e^{qV / \\eta kT} - 1\\right)"]
      },
      {
        unitNumber: 3,
        title: "Bipolar Junction Transistors (BJT)",
        hours: 9,
        description: "Physical operation of NPN and PNP transistors, minority carrier profiles in base, current gain factors, early effect, and hybrid-pi model.",
        topics: [
          "Emitter injection efficiency and base transport factor",
          "Common Base (CB), Common Emitter (CE), and Common Collector (CC) curves",
          "Early voltage and base width modulation",
          "Small-signal low-frequency hybrid-pi model"
        ],
        keyFormulas: ["I_C = I_S e^{V_{BE} / V_T} \\left(1 + \\frac{V_{CE}}{V_A}\\right)", "\\beta = \\frac{\\alpha}{1 - \\alpha}"]
      },
      {
        unitNumber: 4,
        title: "Field Effect Transistors (JFET & MOSFET)",
        hours: 9,
        description: "JFET pinch-off, MOSFET electrostatics, accumulation/depletion/inversion, threshold voltage, subthreshold conduction, and velocity saturation.",
        topics: [
          "JFET drain and transfer characteristics, Shockley JFET formula",
          "MOS capacitor C-V characteristics and flat-band voltage",
          "Enhancement vs depletion n-MOSFET and p-MOSFET IV equations",
          "Short-channel effects: DIBL, hot carrier injection, and gate leakage"
        ],
        keyFormulas: ["I_D = \\frac{1}{2} \\mu_n C_{ox} \\frac{W}{L} (V_{GS} - V_{th})^2", "V_{DS,sat} = V_{GS} - V_{th}"]
      },
      {
        unitNumber: 5,
        title: "Optoelectronic & Special Semiconductor Devices",
        hours: 9,
        description: "Tunnel diodes, Varactor diodes, Light Emitting Diodes (LED), Photodiodes, PIN diodes, and Solar Cell open-circuit voltage.",
        topics: [
          "Tunnel diode negative differential resistance and quantum tunneling",
          "Varactor diode voltage-controlled tuning capacitance",
          "LED radiant efficiency and color emission wavelengths",
          "Solar cell IV curve, short-circuit current (Isc), and fill factor (FF)"
        ],
        keyFormulas: ["\\eta = \\frac{P_{max}}{P_{in}} = \\frac{V_{oc} I_{sc} FF}{P_{in}}", "\\lambda = \\frac{hc}{E_g}"]
      }
    ],
    labSimulation: {
      hasHardwareLab: true,
      hasVirtualSimulation: true,
      simulationPlatform: "LTspice",
      defaultSketchOrScript: `* BJT CE IV Curve Tracer\nQ1 C B 0 0 2N2222\nVCE C 0 DC 0\nIB 0 B DC 10u\n.dc VCE 0 10 0.1 IB 10u 100u 10u\n.plot dc I(VCE)`,
      apparatusList: ["Dual Regulated DC Power Supply (0-30V)", "Rigol Digital Storage Oscilloscope (DSO)", "Semiconductor Curve Tracer / Keithley SMU"],
      labRoom: "MIT Chromepet Devices & Microelectronics Lab - Room 204"
    },
    textbooks: [
      "Streetman, B. G., & Banerjee, S. K. (2016). Solid State Electronic Devices (7th ed.). Pearson.",
      "Neamen, D. A. (2012). Semiconductor Physics and Devices: Basic Principles (4th ed.). McGraw-Hill."
    ],
    referenceBooks: [
      "Sze, S. M., & Ng, K. K. (2006). Physics of Semiconductor Devices (3rd ed.). Wiley.",
      "Millman, J., Halkias, C., & Jit, S. (2015). Electronic Devices and Circuits (4th ed.). McGraw-Hill."
    ],
    nptelCourseId: "noc23-ee44"
  },

  // 3. EC23E04: Optics and Lasers
  "EC23E04": {
    code: "EC23E04",
    title: "Optics and Lasers",
    shortTitle: "Optics & Laser Tech",
    slug: "optics-and-lasers",
    semester: 5,
    credits: 3,
    lectureTutorialLabHours: "3-0-0",
    category: "Professional Elective (PEC)",
    regulation: "Anna University Regulation 2023",
    department: "Department of Electronics Engineering",
    campus: "Madras Institute of Technology (MIT) Campus, Anna University",
    description: "Electromagnetic wave optics, interference, diffraction, laser physics, Einstein coefficients, cavity resonator design, Q-switching, semiconductor diode lasers, and optical fiber telecommunications.",
    visualTheme: {
      themeFamily: "cyan",
      primaryColor: "#06B6D4",
      accentGlow: "rgba(6, 182, 212, 0.25)",
      badgeBg: "rgba(8, 145, 178, 0.4)",
      badgeText: "#67E8F9",
      borderAccent: "rgba(6, 182, 212, 0.3)",
      gradientFrom: "#0891B2",
      gradientTo: "#06B6D4",
      icon: "🔦",
      cardClass: "course-card-cyan",
      glowClass: "course-glow-cyan",
      badgeClass: "course-badge-cyan",
      activeTabClass: "bg-[#06B6D4] text-slate-950 font-bold shadow-course-cyan-glow",
      textAccentClass: "text-[#06B6D4]"
    },
    prerequisites: ["Electromagnetic Fields (EC23C02)", "Engineering Physics (PH23C01)"],
    corequisites: ["Optical Communication & Networks (EC23C08)"],
    prerequisiteDag: [
      { fromCourse: "EC23C02", toCourse: "EC23E04", relationship: "hard", topicBridge: "Maxwell's Equations & Plane Wave Propagation" }
    ],
    courseOutcomes: [
      {
        id: "CO1",
        description: "Apply electromagnetic wave optics principles to evaluate interference, diffraction, and spatial coherence length.",
        bloomLevel: "L3 (Apply)",
        mappedPOs: ["PO1", "PO2"],
        mappedPSOs: ["PSO1"],
        targetAttainmentPct: 72.0
      },
      {
        id: "CO2",
        description: "Derive Einstein A and B coefficients and population inversion threshold conditions for laser oscillation.",
        bloomLevel: "L4 (Analyze)",
        mappedPOs: ["PO1", "PO2", "PO3"],
        mappedPSOs: ["PSO1"],
        targetAttainmentPct: 70.0
      },
      {
        id: "CO3",
        description: "Design optical cavity resonators using ABCD matrix analysis for Gaussian beam stability and transverse mode selection.",
        bloomLevel: "L5 (Evaluate)",
        mappedPOs: ["PO1", "PO3", "PO5"],
        mappedPSOs: ["PSO1"],
        targetAttainmentPct: 68.0
      },
      {
        id: "CO4",
        description: "Analyze giant pulse generation via active/passive Q-switching and mode-locking for ultrashort femtosecond pulses.",
        bloomLevel: "L4 (Analyze)",
        mappedPOs: ["PO1", "PO2", "PO4"],
        mappedPSOs: ["PSO1", "PSO2"],
        targetAttainmentPct: 65.0
      },
      {
        id: "CO5",
        description: "Evaluate semiconductor quantum well diode lasers and fiber optic communication transmission budgets.",
        bloomLevel: "L5 (Evaluate)",
        mappedPOs: ["PO1", "PO3", "PO5"],
        mappedPSOs: ["PSO2"],
        targetAttainmentPct: 70.0
      }
    ],
    syllabusUnits: [
      {
        unitNumber: 1,
        title: "Wave Optics, Interference & Coherence",
        hours: 9,
        description: "Maxwell's equations for optical waves, phase velocity, superposition, Michelson and Fabry-Perot interferometers, temporal and spatial coherence.",
        topics: [
          "Fresnel reflection and transmission coefficients; Brewster angle",
          "Fabry-Perot etalon: Finesse, free spectral range, and resolving power",
          "Coherence time, coherence length, and Van Cittert-Zernike theorem",
          "Fraunhofer and Fresnel diffraction through circular apertures"
        ],
        keyFormulas: ["L_c = \\frac{c}{\\Delta \\nu} = \\frac{\\lambda^2}{\\Delta \\lambda}", "\\mathcal{F} = \\frac{\\pi \\sqrt{R}}{1 - R}"]
      },
      {
        unitNumber: 2,
        title: "Laser Fundamentals & Pumping Dynamics",
        hours: 9,
        description: "Spontaneous emission, stimulated absorption and emission, Einstein relation, line broadening mechanisms, 3-level and 4-level laser systems.",
        topics: [
          "Einstein A and B coefficients relation: B12 = B21, A21/B21 = 8pi h nu^3 / c^3",
          "Homogeneous (Lorentzian) vs Inhomogeneous (Gaussian) line broadening",
          "Threshold gain condition and saturation intensity",
          "Comparison of Ruby (3-level) vs Nd:YAG and He-Ne (4-level) laser efficiency"
        ],
        keyFormulas: ["\\gamma_{th} = \\alpha_s + \\frac{1}{2L} \\ln\\left(\\frac{1}{R_1 R_2}\\right)", "\\frac{A_{21}}{B_{21}} = \\frac{8\\pi h \\nu^3}{c^3}"]
      },
      {
        unitNumber: 3,
        title: "Optical Resonators & Gaussian Beam Optics",
        hours: 9,
        description: "Plane-parallel, confocal, and concentric resonators; ray transfer ABCD matrix formalism; g-parameters; Gaussian beam waist and divergence.",
        topics: [
          "Resonator stability criterion: 0 <= g1 g2 <= 1",
          "Gaussian beam fundamental TEM00 mode propagation parameter q(z)",
          "Beam waist radius, Rayleigh range, and far-field divergence angle",
          "Higher-order Hermite-Gaussian and Laguerre-Gaussian transverse modes"
        ],
        keyFormulas: ["z_R = \\frac{\\pi w_0^2}{\\lambda}", "w(z) = w_0 \\sqrt{1 + \\left(\\frac{z}{z_R}\\right)^2}"]
      },
      {
        unitNumber: 4,
        title: "Q-Switching, Mode Locking & Ultrafast Pulses",
        hours: 9,
        description: "Giant pulse generation, mechanical/electro-optic (Pockels cell) Q-switching, saturable absorbers, active and passive mode locking.",
        topics: [
          "Pockels effect and Kerr electro-optic shutters for cavity dumping",
          "Peak power calculation and pulse energy extraction efficiency",
          "Phase-locking of longitudinal modes and Fourier transform limit: delta t delta nu >= 0.441",
          "Titanium:Sapphire Kerr-lens mode locking for femtosecond pulse trains"
        ],
        keyFormulas: ["\\Delta t_{pulse} = \\frac{2L}{c N_{modes}} = \\frac{1}{\\Delta \\nu_{total}}", "P_{peak} = \\frac{E_{pulse}}{\\tau_{pulse}}"]
      },
      {
        unitNumber: 5,
        title: "Semiconductor Lasers & Optical Communications",
        hours: 9,
        description: "Double heterostructure laser diodes, distributed feedback (DFB) lasers, VCSELs, optical amplification (EDFA), and fiber transmission links.",
        topics: [
          "Population inversion in direct bandgap degenerate semiconductors",
          "Distributed Feedback (DFB) Bragg grating single-mode lasers",
          "Vertical Cavity Surface Emitting Lasers (VCSEL) for optical interconnects",
          "Erbium-Doped Fiber Amplifiers (EDFA) gain spectrum and noise figure"
        ],
        keyFormulas: ["\\lambda_B = 2 n_{eff} \\Lambda", "J_{th} = \\frac{q d}{\\eta_i \\tau} n_{th}"]
      }
    ],
    labSimulation: {
      hasHardwareLab: true,
      hasVirtualSimulation: true,
      simulationPlatform: "Optics Ray Tracer",
      defaultSketchOrScript: `import numpy as np\n# Cavity Stability g1*g2 calculation\nL = 0.5  # Cavity length 50 cm\nR1 = 1.0 # Mirror 1 Radius of Curvature\nR2 = 0.8 # Mirror 2 Radius of Curvature\ng1 = 1 - (L / R1)\ng2 = 1 - (L / R2)\nstable = (0 <= g1 * g2 <= 1)\nprint(f"g1={g1}, g2={g2}, g1*g2={g1*g2:.3f}, Stable: {stable}")`,
      apparatusList: ["He-Ne Gas Laser (632.8 nm)", "Fabry-Perot Optical Interferometer", "Photodetector & Beam Profiling CCD Camera"],
      labRoom: "MIT Chromepet Laser & Photonics Research Facility - Room 408"
    },
    textbooks: [
      "Svelto, O. (2010). Principles of Lasers (5th ed.). Springer.",
      "Ghatak, A., & Thyagarajan, K. (2012). Optical Electronics. Cambridge University Press."
    ],
    referenceBooks: [
      "Verdeyen, J. T. (2000). Laser Electronics (3rd ed.). Prentice Hall.",
      "Saleh, B. E., & Teich, M. C. (2019). Fundamentals of Photonics (3rd ed.). Wiley."
    ],
    nptelCourseId: "noc23-ph33"
  },

  // 4. EC8702: Embedded Systems
  "EC8702": {
    code: "EC8702",
    title: "Embedded Systems",
    shortTitle: "Embedded Hardware & RTOS",
    slug: "embedded-systems",
    semester: 7,
    credits: 3,
    lectureTutorialLabHours: "3-0-0",
    category: "Professional Core (PCC)",
    regulation: "Anna University Regulation 2023",
    department: "Department of Electronics Engineering",
    campus: "Madras Institute of Technology (MIT) Campus, Anna University",
    description: "Core embedded microcontroller architecture, ARM Cortex-M, memory mapped registers, peripherals (UART, SPI, I2C), FreeRTOS real-time scheduling, and low-power IoT hardware interfaces.",
    visualTheme: {
      themeFamily: "indigo",
      primaryColor: "#6366F1",
      accentGlow: "rgba(99, 102, 241, 0.25)",
      badgeBg: "rgba(67, 56, 202, 0.4)",
      badgeText: "#A5B4FC",
      borderAccent: "rgba(99, 102, 241, 0.3)",
      gradientFrom: "#4338CA",
      gradientTo: "#6366F1",
      icon: "⚙️",
      cardClass: "course-card-indigo",
      glowClass: "course-glow-indigo",
      badgeClass: "course-badge-indigo",
      activeTabClass: "bg-[#6366F1] text-slate-950 font-bold shadow-course-indigo-glow",
      textAccentClass: "text-[#6366F1]"
    },
    prerequisites: ["Microprocessors and Microcontrollers (EC23C05)", "C Programming & Data Structures"],
    corequisites: ["Embedded Systems Laboratory (EC8711)"],
    prerequisiteDag: [
      { fromCourse: "EC23C05", toCourse: "EC8702", relationship: "hard", topicBridge: "Assembly Language, Bus Timing & Peripheral Interfacing" }
    ],
    courseOutcomes: [
      {
        id: "CO1",
        description: "Analyze the architectural differences between Von-Neumann and Harvard RISC pipelines in modern ARM Cortex-M cores.",
        bloomLevel: "L4 (Analyze)",
        mappedPOs: ["PO1", "PO2"],
        mappedPSOs: ["PSO1"],
        targetAttainmentPct: 75.0
      },
      {
        id: "CO2",
        description: "Configure Nested Vectored Interrupt Controllers (NVIC) and Direct Memory Access (DMA) channels for zero-latency I/O.",
        bloomLevel: "L4 (Analyze)",
        mappedPOs: ["PO1", "PO3", "PO5"],
        mappedPSOs: ["PSO1"],
        targetAttainmentPct: 72.0
      },
      {
        id: "CO3",
        description: "Design robust embedded firmware utilizing SPI, I2C, UART, and CAN protocols with cyclic redundancy checks (CRC).",
        bloomLevel: "L5 (Evaluate)",
        mappedPOs: ["PO2", "PO3", "PO5"],
        mappedPSOs: ["PSO1", "PSO2"],
        targetAttainmentPct: 70.0
      },
      {
        id: "CO4",
        description: "Implement multi-tasking FreeRTOS applications with mutexes, binary semaphores, and priority inheritance to eliminate priority inversion.",
        bloomLevel: "L6 (Create)",
        mappedPOs: ["PO1", "PO3", "PO4", "PO5"],
        mappedPSOs: ["PSO2"],
        targetAttainmentPct: 70.0
      },
      {
        id: "CO5",
        description: "Evaluate low-power standby and deep sleep modes for battery-powered IoT edge nodes with wake-on-interrupt.",
        bloomLevel: "L5 (Evaluate)",
        mappedPOs: ["PO1", "PO2", "PO7"],
        mappedPSOs: ["PSO2"],
        targetAttainmentPct: 70.0
      }
    ],
    syllabusUnits: [
      {
        unitNumber: 1,
        title: "Embedded Processor Architecture & Pipeline",
        hours: 9,
        description: "RISC vs CISC, ARM Cortex-M4 architecture, 3-stage fetch-decode-execute pipeline, memory map, bit-banding, and hardware floating-point unit (FPU).",
        topics: [
          "ARM Cortex-M core registers (R0-R15), PSP vs MSP stack pointers",
          "Memory architecture: Flash, SRAM, bit-band regions, and memory protection unit (MPU)",
          "Bootloader sequence, reset vector execution, and linker script mapping",
          "Thumb-2 instruction set efficiency & register preservation conventions"
        ],
        keyFormulas: ["\\text{CPI} = \\frac{\\text{Clock Cycles}}{\\text{Instruction Count}}", "\\text{Execution Time} = I \\times \\text{CPI} \\times T_{clk}"]
      },
      {
        unitNumber: 2,
        title: "Memory-Mapped I/O, Interrupts & NVIC",
        hours: 9,
        description: "GPIO register manipulation (MODER, OTYPER, PUPDR, BSRR), Nested Vectored Interrupt Controller (NVIC), tail-chaining, and DMA streaming.",
        topics: [
          "Atomic bit set/reset operations using BSRR registers",
          "NVIC priority grouping, preemption priority, and sub-priority levels",
          "Interrupt latency optimization via hardware tail-chaining and late arrival",
          "Direct Memory Access (DMA) circular buffer modes for continuous ADC streaming"
        ],
        keyFormulas: ["\\text{Interrupt Latency} = 12 \\text{ cycles (ARM Cortex-M4)}", "\\text{DMA Bandwidth} = f_{clk} \\times \\text{Bus Width}"]
      },
      {
        unitNumber: 3,
        title: "Embedded Bus Protocols & Interfacing",
        hours: 9,
        description: "Clock synchronization, start/stop conditions, frame structure, error checking, and peripheral drivers for UART, SPI, I2C, and automotive CAN.",
        topics: [
          "UART baud rate generation, fractional baud divisors, and ring buffer RX",
          "SPI CPOL and CPHA modes, master/slave handshaking, and multi-drop chip select",
          "I2C 7-bit/10-bit addressing, open-drain bus, clock stretching, and ACK/NACK",
          "CAN 2.0B differential signaling, identifier arbitration, and message filtering"
        ],
        keyFormulas: ["\\text{Baud Rate} = \\frac{f_{PCLK}}{16 \\times \\text{USARTDIV}}", "f_{SCL} = \\frac{1}{t_{HIGH} + t_{LOW}}"]
      },
      {
        unitNumber: 4,
        title: "Real-Time Operating Systems (RTOS)",
        hours: 9,
        description: "Preemptive multitasking, Round-Robin scheduling, FreeRTOS kernel primitives, task states, semaphores, message queues, and priority inversion.",
        topics: [
          "SysTick timer configuration and context switching mechanism (PendSV)",
          "Task control blocks (TCB), stack watermarking, and heap allocation strategies (heap_4)",
          "Inter-Task Communication (ITC) via queue sets, event groups, and stream buffers",
          "Priority Inversion resolution via Priority Inheritance Mutexes"
        ],
        keyFormulas: ["U = \\sum_{i=1}^{n} \\frac{C_i}{T_i} \\le n(2^{1/n} - 1)", "\\lim_{n \\to \\infty} n(2^{1/n} - 1) \\approx 0.693"]
      },
      {
        unitNumber: 5,
        title: "Power Optimization & Low-Power IoT Nodes",
        hours: 9,
        description: "Dynamic power dissipation vs static leakage, sleep, deep-sleep, and standby modes, real-time clock (RTC) alarms, and energy auditing.",
        topics: [
          "CMOS power dissipation components: P_dynamic = C V^2 f + P_leakage",
          "Clock gating, voltage scaling, and disabling unused peripheral bus domains",
          "ESP32 and STM32 ULP (Ultra-Low Power) co-processor wake-up triggers",
          "Energy harvesting power budgets and coin cell battery lifetime estimation"
        ],
        keyFormulas: ["P_{dyn} = \\alpha C_L V_{DD}^2 f_{clk}", "T_{life} = \\frac{\\text{Battery Capacity (mAh)}}{I_{avg} (\\text{mA})}"]
      }
    ],
    labSimulation: {
      hasHardwareLab: true,
      hasVirtualSimulation: true,
      simulationPlatform: "Wokwi Embedded",
      defaultSketchOrScript: `// FreeRTOS Dual-Task LED & Telemetry\n#include <Arduino.h>\nvoid Task1(void *pvParameters) {\n  pinMode(2, OUTPUT);\n  for(;;) { digitalWrite(2, !digitalRead(2)); vTaskDelay(500 / portTICK_PERIOD_MS); }\n}\nvoid setup() {\n  xTaskCreate(Task1, "BlinkTask", 1024, NULL, 1, NULL);\n}\nvoid loop() {}`,
      apparatusList: ["ESP32-S3 DevKit-C + STM32 Nucleo-F401RE", "Saleae 8-Channel USB Logic Analyzer", "Keysight 34461A 6.5 Digit Precision Digital Multimeter"],
      labRoom: "MIT Chromepet Embedded Systems & IoT Hub - Lab 304"
    },
    textbooks: [
      "Yiu, J. (2014). The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors (3rd ed.). Newnes.",
      "Barry, R. (2016). Mastering the FreeRTOS Real Time Kernel. Real Time Engineers Ltd."
    ],
    referenceBooks: [
      "Valvano, J. W. (2014). Embedded Systems: Real-Time Interfacing to ARM Cortex-M Microcontrollers. CreateSpace.",
      "Wolf, M. (2016). Computers as Components: Principles of Embedded Computing System Design (4th ed.). Morgan Kaufmann."
    ],
    nptelCourseId: "noc23-cs82"
  }
};

/**
 * Helper to fetch course by course code or slug
 */
export function getCourseByCode(code: string): CourseConfig | undefined {
  const normalized = code.toUpperCase().trim();
  return PRIORITY_COURSES[normalized];
}

export function getCourseBySlug(slug: string): CourseConfig | undefined {
  const normalizedSlug = slug.toLowerCase().trim();
  return Object.values(PRIORITY_COURSES).find(c => c.slug === normalizedSlug);
}

export function getAllCourses(): CourseConfig[] {
  return Object.values(PRIORITY_COURSES);
}

export function getCourseThemeTokens(code: string): CourseVisualTheme {
  const course = getCourseByCode(code);
  if (course) return course.visualTheme;
  return PRIORITY_COURSES["EC23S01"].visualTheme;
}
