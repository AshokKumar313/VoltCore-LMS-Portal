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

export interface ModuleLabMapping {
  labExperimentId: string;
  labTitle: string;
  apparatus: string[];
  simulationInteractive: boolean;
}

export interface CBCSUnitParams {
  lectureHours: number;
  tutorialHours: number;
  practicalHours: number;
  creditWeight: number;
}

export interface ModuleLabRelationship {
  unitNumber: number;
  unitTitle: string;
  labId: string;
  labTitle: string;
  simulationComponent: string;
  obeTargetCO: string;
  bloomLevel: string;
}

export interface CBCSClassification {
  category: string;
  creditValue: number;
  contactHoursPerWeek: number;
  gradingScheme: string;
  continuousEvaluationWeight: number;
  endSemesterWeight: number;
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
  obeAttainmentTag?: string;
  bloomLevel?: "L1 (Remember)" | "L2 (Understand)" | "L3 (Apply)" | "L4 (Analyze)" | "L5 (Evaluate)" | "L6 (Create)";
  cbcsParams?: CBCSUnitParams;
  moduleLabMapping?: ModuleLabMapping[];
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
  descriptiveEngineeringTitle?: string;
  shortTitle: string;
  slug: string;
  semester: number;
  credits: number;
  lectureTutorialLabHours: string; // e.g. "3-0-0" or "0-0-4"
  category: "Professional Core (PCC)" | "Employability Enhancement (EEC)" | "Professional Elective (PEC)" | "Foundation (ESC)" | string;
  regulation?: string;
  department?: string;
  campus?: string;
  institution?: string;
  framework?: string;
  description: string;
  visualTheme: CourseVisualTheme;
  cbcsClassification?: CBCSClassification;
  moduleLabRelationships?: ModuleLabRelationship[];
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
  // 1. EC23S01: Python Digital Signal Processing
  "EC23S01": {
    code: "EC23S01",
    title: "Python Digital Signal Processing",
    descriptiveEngineeringTitle: "Python Digital Signal Processing",
    shortTitle: "Python DSP",
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
    cbcsClassification: {
      category: "Employability Enhancement Courses (EEC)",
      creditValue: 2,
      contactHoursPerWeek: 4,
      gradingScheme: "Letter Grade (O, A+, A, B+, B, C)",
      continuousEvaluationWeight: 60,
      endSemesterWeight: 40
    },
    moduleLabRelationships: [
      {
        unitNumber: 1,
        unitTitle: "Python Vectorized Signal Foundations",
        labId: "EC23S01_LAB1",
        labTitle: "Interactive Python DSP Filter & Frequency Response Grapher",
        simulationComponent: "ButterworthChebyshevBodeVisualizer",
        obeTargetCO: "CO1",
        bloomLevel: "L3 (Apply)"
      },
      {
        unitNumber: 2,
        unitTitle: "DFT & Fast Fourier Transform (FFT) Implementations",
        labId: "EC23S01_LAB2",
        labTitle: "Discrete FFT Spectrum & Windowing Artifacts",
        simulationComponent: "DiscreteFftSpectrumVisualizer",
        obeTargetCO: "CO2",
        bloomLevel: "L4 (Analyze)"
      },
      {
        unitNumber: 3,
        unitTitle: "IIR Digital Filter Synthesis",
        labId: "EC23S01_LAB3",
        labTitle: "Bilinear Transformation & Chebyshev/Butterworth Filter Bench",
        simulationComponent: "ButterworthChebyshevBodeVisualizer",
        obeTargetCO: "CO3",
        bloomLevel: "L5 (Evaluate)"
      },
      {
        unitNumber: 4,
        unitTitle: "FIR Filter Design & Windowing Techniques",
        labId: "EC23S01_LAB4",
        labTitle: "Linear-Phase Windowing (Hamming/Kaiser) Spectrum Analyzer",
        simulationComponent: "FirWindowingVisualizer",
        obeTargetCO: "CO4",
        bloomLevel: "L5 (Evaluate)"
      },
      {
        unitNumber: 5,
        unitTitle: "Adaptive Filters & Real-Time Sensor Telemetry",
        labId: "EC23S01_LAB5",
        labTitle: "Least-Mean-Squares (LMS) Adaptive Noise Cancellation Simulator",
        simulationComponent: "AdaptiveLmsTelemetryVisualizer",
        obeTargetCO: "CO5",
        bloomLevel: "L6 (Create)"
      }
    ],
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
        obeAttainmentTag: "OBE-CO1-APPLY-L3",
        bloomLevel: "L3 (Apply)",
        cbcsParams: {
          lectureHours: 0,
          tutorialHours: 0,
          practicalHours: 8,
          creditWeight: 0.35
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC23S01_LAB1",
            labTitle: "Discrete signal generation & convolution bench",
            apparatus: ["Python NumPy", "JupyterLab Workstation"],
            simulationInteractive: true
          }
        ],
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
        obeAttainmentTag: "OBE-CO2-ANALYZE-L4",
        bloomLevel: "L4 (Analyze)",
        cbcsParams: {
          lectureHours: 0,
          tutorialHours: 0,
          practicalHours: 10,
          creditWeight: 0.40
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC23S01_LAB2",
            labTitle: "64-point Radix-2 DIT-FFT butterfly computation & spectral leakage",
            apparatus: ["Python SciPy FFT", "Digital Signal Generator"],
            simulationInteractive: true
          }
        ],
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
        obeAttainmentTag: "OBE-CO3-EVALUATE-L5",
        bloomLevel: "L5 (Evaluate)",
        cbcsParams: {
          lectureHours: 0,
          tutorialHours: 0,
          practicalHours: 10,
          creditWeight: 0.45
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC23S01_LAB3",
            labTitle: "Butterworth & Chebyshev IIR Filter Bode Plot Visualizer",
            apparatus: ["SciPy Signal Filter Design", "Interactive Bode Canvas"],
            simulationInteractive: true
          }
        ],
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
        obeAttainmentTag: "OBE-CO4-EVALUATE-L5",
        bloomLevel: "L5 (Evaluate)",
        cbcsParams: {
          lectureHours: 0,
          tutorialHours: 0,
          practicalHours: 10,
          creditWeight: 0.40
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC23S01_LAB4",
            labTitle: "Linear-phase FIR bandpass filter via Kaiser/Hamming window",
            apparatus: ["Python FIRWin Engine", "Spectrum Analyzer"],
            simulationInteractive: true
          }
        ],
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
        obeAttainmentTag: "OBE-CO5-CREATE-L6",
        bloomLevel: "L6 (Create)",
        cbcsParams: {
          lectureHours: 0,
          tutorialHours: 0,
          practicalHours: 10,
          creditWeight: 0.40
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC23S01_LAB5",
            labTitle: "Adaptive 50Hz notch filter & real-time sensor streaming",
            apparatus: ["PySerial WebSocket Bridge", "ESP32 Sensor Testbed"],
            simulationInteractive: true
          }
        ],
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

  // 2. EC23C03: Electronic Devices and Circuits
  "EC23C03": {
    code: "EC23C03",
    title: "Electronic Devices and Circuits",
    descriptiveEngineeringTitle: "Electronic Devices and Circuits",
    shortTitle: "Devices & Circuits",
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
    cbcsClassification: {
      category: "Professional Core Courses (PCC)",
      creditValue: 3,
      contactHoursPerWeek: 3,
      gradingScheme: "Letter Grade (O, A+, A, B+, B, C)",
      continuousEvaluationWeight: 40,
      endSemesterWeight: 60
    },
    moduleLabRelationships: [
      {
        unitNumber: 1,
        unitTitle: "Semiconductor Physics & Carrier Transport",
        labId: "EC23C03_LAB1",
        labTitle: "Semiconductor Carrier Transport & Hall Effect Profiling",
        simulationComponent: "CarrierTransportHallVisualizer",
        obeTargetCO: "CO1",
        bloomLevel: "L4 (Analyze)"
      },
      {
        unitNumber: 2,
        unitTitle: "PN Junction & Zener Diodes",
        labId: "EC23C03_LAB2",
        labTitle: "Shockley Diode IV & Zener Breakdown Characterization",
        simulationComponent: "DiodeMosfetIvCurveTracer",
        obeTargetCO: "CO2",
        bloomLevel: "L4 (Analyze)"
      },
      {
        unitNumber: 3,
        unitTitle: "Bipolar Junction Transistors (BJT)",
        labId: "EC23C03_LAB3",
        labTitle: "BJT Common-Emitter Output & Early Voltage Modeling",
        simulationComponent: "BjtEarlyEffectVisualizer",
        obeTargetCO: "CO3",
        bloomLevel: "L4 (Analyze)"
      },
      {
        unitNumber: 4,
        unitTitle: "Field Effect Transistors (JFET & MOSFET)",
        labId: "EC23C03_LAB4",
        labTitle: "N-Channel MOSFET IV Curve Tracer & Triode/Saturation Bench",
        simulationComponent: "DiodeMosfetIvCurveTracer",
        obeTargetCO: "CO4",
        bloomLevel: "L5 (Evaluate)"
      },
      {
        unitNumber: 5,
        unitTitle: "Optoelectronic & Special Semiconductor Devices",
        labId: "EC23C03_LAB5",
        labTitle: "Optoelectronic PIN Photodiode & Solar Cell Fill Factor Bench",
        simulationComponent: "SolarCellOptoVisualizer",
        obeTargetCO: "CO5",
        bloomLevel: "L3 (Apply)"
      }
    ],
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
        obeAttainmentTag: "OBE-CO1-ANALYZE-L4",
        bloomLevel: "L4 (Analyze)",
        cbcsParams: {
          lectureHours: 9,
          tutorialHours: 0,
          practicalHours: 0,
          creditWeight: 0.60
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC23C03_LAB1",
            labTitle: "Semiconductor carrier mobility & Hall effect testbench",
            apparatus: ["Hall Effect Measurement System", "Gaussmeter"],
            simulationInteractive: true
          }
        ],
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
        obeAttainmentTag: "OBE-CO2-ANALYZE-L4",
        bloomLevel: "L4 (Analyze)",
        cbcsParams: {
          lectureHours: 9,
          tutorialHours: 0,
          practicalHours: 0,
          creditWeight: 0.60
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC23C03_LAB2",
            labTitle: "Shockley diode forward/reverse IV and dynamic resistance",
            apparatus: ["Keithley SMU / Curve Tracer", "1N4148 Diode"],
            simulationInteractive: true
          }
        ],
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
        obeAttainmentTag: "OBE-CO3-ANALYZE-L4",
        bloomLevel: "L4 (Analyze)",
        cbcsParams: {
          lectureHours: 9,
          tutorialHours: 0,
          practicalHours: 0,
          creditWeight: 0.60
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC23C03_LAB3",
            labTitle: "BJT CE output characteristics & Early voltage measurement",
            apparatus: ["Dual DC Power Supply", "2N2222 Transistor"],
            simulationInteractive: true
          }
        ],
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
        obeAttainmentTag: "OBE-CO4-EVALUATE-L5",
        bloomLevel: "L5 (Evaluate)",
        cbcsParams: {
          lectureHours: 9,
          tutorialHours: 0,
          practicalHours: 0,
          creditWeight: 0.60
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC23C03_LAB4",
            labTitle: "MOSFET drain/transfer curves & triode/saturation tracer",
            apparatus: ["2N7000 N-MOSFET", "Digital Multimeter"],
            simulationInteractive: true
          }
        ],
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
        obeAttainmentTag: "OBE-CO5-APPLY-L3",
        bloomLevel: "L3 (Apply)",
        cbcsParams: {
          lectureHours: 9,
          tutorialHours: 0,
          practicalHours: 0,
          creditWeight: 0.60
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC23C03_LAB5",
            labTitle: "Silicon solar cell IV curve, short circuit current & fill factor",
            apparatus: ["Calibrated Light Source", "Solar Cell Test Fixture"],
            simulationInteractive: true
          }
        ],
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

  // 3. EC23E04: Optics, Lasers and Fiber Optics
  "EC23E04": {
    code: "EC23E04",
    title: "Optics, Lasers and Fiber Optics",
    descriptiveEngineeringTitle: "Optics, Lasers and Fiber Optics",
    shortTitle: "Optics & Fiber Optics",
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
    cbcsClassification: {
      category: "Professional Elective Courses (PEC)",
      creditValue: 3,
      contactHoursPerWeek: 3,
      gradingScheme: "Letter Grade (O, A+, A, B+, B, C)",
      continuousEvaluationWeight: 40,
      endSemesterWeight: 60
    },
    moduleLabRelationships: [
      {
        unitNumber: 1,
        unitTitle: "Wave Optics, Interference & Coherence",
        labId: "EC23E04_LAB1",
        labTitle: "Michelson & Fabry-Perot Interferometry Finesse Analysis",
        simulationComponent: "FabryPerotInterferometerVisualizer",
        obeTargetCO: "CO1",
        bloomLevel: "L3 (Apply)"
      },
      {
        unitNumber: 2,
        unitTitle: "Laser Fundamentals & Pumping Dynamics",
        labId: "EC23E04_LAB2",
        labTitle: "Einstein Population Inversion & Laser Gain Dynamics Bench",
        simulationComponent: "LaserPumpingGainVisualizer",
        obeTargetCO: "CO2",
        bloomLevel: "L4 (Analyze)"
      },
      {
        unitNumber: 3,
        unitTitle: "Optical Resonators & Gaussian Beam Optics",
        labId: "EC23E04_LAB3",
        labTitle: "Fabry-Perot Cavity Resonator Stability (g1-g2) Diagram",
        simulationComponent: "OpticalCavityStabilityVisualizer",
        obeTargetCO: "CO3",
        bloomLevel: "L5 (Evaluate)"
      },
      {
        unitNumber: 4,
        unitTitle: "Q-Switching, Mode Locking & Ultrafast Pulses",
        labId: "EC23E04_LAB4",
        labTitle: "Electro-Optic Q-Switching & Mode-Locked Ultrashort Pulses",
        simulationComponent: "QSwitchingModeLockVisualizer",
        obeTargetCO: "CO4",
        bloomLevel: "L4 (Analyze)"
      },
      {
        unitNumber: 5,
        unitTitle: "Semiconductor Lasers & Optical Communications",
        labId: "EC23E04_LAB5",
        labTitle: "DFB Semiconductor Diode Laser & Fiber Optic Link Budget",
        simulationComponent: "FiberOpticLinkBudgetVisualizer",
        obeTargetCO: "CO5",
        bloomLevel: "L5 (Evaluate)"
      }
    ],
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
        obeAttainmentTag: "OBE-CO1-APPLY-L3",
        bloomLevel: "L3 (Apply)",
        cbcsParams: {
          lectureHours: 9,
          tutorialHours: 0,
          practicalHours: 0,
          creditWeight: 0.60
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC23E04_LAB1",
            labTitle: "Fabry-Perot etalon finesse & free spectral range analyzer",
            apparatus: ["Fabry-Perot Interferometer", "Photodetector"],
            simulationInteractive: true
          }
        ],
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
        obeAttainmentTag: "OBE-CO2-ANALYZE-L4",
        bloomLevel: "L4 (Analyze)",
        cbcsParams: {
          lectureHours: 9,
          tutorialHours: 0,
          practicalHours: 0,
          creditWeight: 0.60
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC23E04_LAB2",
            labTitle: "Threshold gain condition & 4-level He-Ne laser pumping model",
            apparatus: ["He-Ne Tube Power Supply", "Laser Power Meter"],
            simulationInteractive: true
          }
        ],
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
        obeAttainmentTag: "OBE-CO3-EVALUATE-L5",
        bloomLevel: "L5 (Evaluate)",
        cbcsParams: {
          lectureHours: 9,
          tutorialHours: 0,
          practicalHours: 0,
          creditWeight: 0.60
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC23E04_LAB3",
            labTitle: "Optical cavity stability diagram (g1*g2) & beam waist profiler",
            apparatus: ["Curved Mirror Resonator Rail", "CCD Beam Profiler"],
            simulationInteractive: true
          }
        ],
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
        obeAttainmentTag: "OBE-CO4-ANALYZE-L4",
        bloomLevel: "L4 (Analyze)",
        cbcsParams: {
          lectureHours: 9,
          tutorialHours: 0,
          practicalHours: 0,
          creditWeight: 0.60
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC23E04_LAB4",
            labTitle: "Pockels cell electro-optic shutter & mode-locked pulse simulator",
            apparatus: ["Ultrafast Photodiode", "High-Bandwidth DSO"],
            simulationInteractive: true
          }
        ],
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
        obeAttainmentTag: "OBE-CO5-EVALUATE-L5",
        bloomLevel: "L5 (Evaluate)",
        cbcsParams: {
          lectureHours: 9,
          tutorialHours: 0,
          practicalHours: 0,
          creditWeight: 0.60
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC23E04_LAB5",
            labTitle: "Fiber optic link loss budget & EDFA amplifier gain model",
            apparatus: ["Optical Power Meter", "Single-Mode Fiber Spool (10km)"],
            simulationInteractive: true
          }
        ],
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

  // 4. EC8702: Advanced Embedded Systems Architecture
  "EC8702": {
    code: "EC8702",
    title: "Advanced Embedded Systems Architecture",
    descriptiveEngineeringTitle: "Advanced Embedded Systems Architecture",
    shortTitle: "Advanced Embedded Architecture",
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
    cbcsClassification: {
      category: "Professional Core Courses (PCC)",
      creditValue: 3,
      contactHoursPerWeek: 3,
      gradingScheme: "Letter Grade (O, A+, A, B+, B, C)",
      continuousEvaluationWeight: 40,
      endSemesterWeight: 60
    },
    moduleLabRelationships: [
      {
        unitNumber: 1,
        unitTitle: "Embedded Processor Architecture & Pipeline",
        labId: "EC8702_LAB1",
        labTitle: "ARM Cortex-M Pipeline & Register Preservation Profiler",
        simulationComponent: "CortexMPipelineVisualizer",
        obeTargetCO: "CO1",
        bloomLevel: "L4 (Analyze)"
      },
      {
        unitNumber: 2,
        unitTitle: "Memory-Mapped I/O, Interrupts & NVIC",
        labId: "EC8702_LAB2",
        labTitle: "NVIC Priority Grouping & Hardware Tail-Chaining Latency",
        simulationComponent: "NvicTailChainingVisualizer",
        obeTargetCO: "CO2",
        bloomLevel: "L4 (Analyze)"
      },
      {
        unitNumber: 3,
        unitTitle: "Embedded Bus Protocols & Interfacing",
        labId: "EC8702_LAB3",
        labTitle: "Multi-Drop SPI/I2C/CAN Bus Protocol Frame Analyzer",
        simulationComponent: "SerialProtocolFrameVisualizer",
        obeTargetCO: "CO3",
        bloomLevel: "L5 (Evaluate)"
      },
      {
        unitNumber: 4,
        unitTitle: "Real-Time Operating Systems (RTOS)",
        labId: "EC8702_LAB4",
        labTitle: "FreeRTOS Task Schedulability & Rate Monotonic Utilization",
        simulationComponent: "RtosSchedulabilityVisualizer",
        obeTargetCO: "CO4",
        bloomLevel: "L6 (Create)"
      },
      {
        unitNumber: 5,
        unitTitle: "Power Optimization & Low-Power IoT Nodes",
        labId: "EC8702_LAB5",
        labTitle: "IoT Deep Sleep Wake-Up & Dynamic Power Consumption Profiler",
        simulationComponent: "LowPowerModeVisualizer",
        obeTargetCO: "CO5",
        bloomLevel: "L5 (Evaluate)"
      }
    ],
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
        obeAttainmentTag: "OBE-CO1-ANALYZE-L4",
        bloomLevel: "L4 (Analyze)",
        cbcsParams: {
          lectureHours: 9,
          tutorialHours: 0,
          practicalHours: 0,
          creditWeight: 0.60
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC8702_LAB1",
            labTitle: "ARM Cortex-M core registers (R0-R15) & stack pointer preservation",
            apparatus: ["STM32 Nucleo-F401RE", "Keil / STM32CubeIDE"],
            simulationInteractive: true
          }
        ],
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
        obeAttainmentTag: "OBE-CO2-ANALYZE-L4",
        bloomLevel: "L4 (Analyze)",
        cbcsParams: {
          lectureHours: 9,
          tutorialHours: 0,
          practicalHours: 0,
          creditWeight: 0.60
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC8702_LAB2",
            labTitle: "NVIC hardware tail-chaining & late-arrival latency bench",
            apparatus: ["Saleae Logic Analyzer", "DSOX1204G Oscilloscope"],
            simulationInteractive: true
          }
        ],
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
        obeAttainmentTag: "OBE-CO3-EVALUATE-L5",
        bloomLevel: "L5 (Evaluate)",
        cbcsParams: {
          lectureHours: 9,
          tutorialHours: 0,
          practicalHours: 0,
          creditWeight: 0.60
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC8702_LAB3",
            labTitle: "UART ring buffer, SPI DMA & CAN differential frame packet analyzer",
            apparatus: ["CAN Bus Transceiver", "I2C Sensor Shield"],
            simulationInteractive: true
          }
        ],
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
        obeAttainmentTag: "OBE-CO4-CREATE-L6",
        bloomLevel: "L6 (Create)",
        cbcsParams: {
          lectureHours: 9,
          tutorialHours: 0,
          practicalHours: 0,
          creditWeight: 0.60
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC8702_LAB4",
            labTitle: "FreeRTOS preemptive scheduler, priority inheritance mutex & task utilization",
            apparatus: ["FreeRTOS Kernel v10.4", "Wokwi STM32 Simulator"],
            simulationInteractive: true
          }
        ],
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
        obeAttainmentTag: "OBE-CO5-EVALUATE-L5",
        bloomLevel: "L5 (Evaluate)",
        cbcsParams: {
          lectureHours: 9,
          tutorialHours: 0,
          practicalHours: 0,
          creditWeight: 0.60
        },
        moduleLabMapping: [
          {
            labExperimentId: "EC8702_LAB5",
            labTitle: "STM32/ESP32 low-power sleep modes & RTC wake-up current profiler",
            apparatus: ["Nordic Power Profiler Kit II", "Coin Cell Test Fixture"],
            simulationInteractive: true
          }
        ],
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

// ---------------------------------------------------------------------------
// UNIVERSAL EMBEDDED SYSTEMS & STM32 HARDWARE ARCHITECTURE CONTRACTS
// ---------------------------------------------------------------------------

export interface CortexMArchitectureSpec {
  core: "Cortex-M0+" | "Cortex-M3" | "Cortex-M4F" | "Cortex-M7";
  architectureVersion: string; // e.g. "ARMv7-M" or "ARMv7E-M"
  pipelineStages: number;
  isaFeatures: string[];
  coreRegisters: string[];
  nvicSpec: {
    maxInterrupts: number;
    priorityBits: number;
    subPriorityGrouping: boolean;
    tailChainingCycles: number;
    lateArrivalCycles: number;
  };
  systickTimer: {
    bits: number;
    countsDown: boolean;
  };
  hasHardwareFpu: boolean;
  fpuSpec?: {
    standard: string;
    precision: "Single-Precision (FPv4-SP)" | "Double-Precision";
    registers: string;
    lazyStackingSupported: boolean;
  };
  hasDspextension: boolean;
}

export interface Stm32RegisterMap {
  gpioConfig: {
    style: "CRL_CRH_CNF_MODE" | "MODER_OTYPER_OSPEEDR_PUPDR";
    registers: string[];
    alternateFunctionRouting: "AFIO_MAPR" | "AFR_LOW_HIGH";
    atomicBitOps: "BSRR_AND_BRR" | "BSRR_SET_RESET";
    portBaseAddresses: Record<string, string>;
  };
  rccClockConfig: {
    registers: string[];
    pllEquation: string;
    internalOscMhz: number;
    crystalMaxMhz: number;
    flashWaitStatesTable: Array<{ maxFreqMhz: number; waitStates: number }>;
  };
  dmaArchitecture: {
    organization: "Channels" | "StreamsAndChannels";
    controllerCount: number;
    fifoSupport: boolean;
    circularMode: boolean;
    registers: string[];
  };
  timerMatrix: {
    advancedControlTimers: string[];
    generalPurposeTimers: string[];
    basicTimers: string[];
    prescalerResolution: string;
    counterResolution: string;
  };
}

export interface Stm32DeviceProfile {
  deviceCode: "STM32F103" | "STM32F401";
  chipPartNumber: string;
  boardTarget: "Blue Pill (STM32F103C8T6)" | "Nucleo-F401RE";
  family: "STM32F1" | "STM32F4";
  cortexSpec: CortexMArchitectureSpec;
  maxCpuClockMhz: number;
  flashMemoryKb: number;
  sramMemoryKb: number;
  voltageSupply: string;
  busTopologies: {
    ahbMhz: number;
    apb1Mhz: number;
    apb2Mhz: number;
    busMatrixDescription: string;
  };
  registerMap: Stm32RegisterMap;
  packageType: string;
  debuggerInterface: "ST-LINK V2 / SWD" | "ST-LINK V2-1 On-Board SWD";
}

export const ARM_CORTEX_SPECS: Record<"Cortex-M3" | "Cortex-M4F", CortexMArchitectureSpec> = {
  "Cortex-M3": {
    core: "Cortex-M3",
    architectureVersion: "ARMv7-M",
    pipelineStages: 3,
    isaFeatures: ["Thumb-2 (16/32-bit)", "Hardware Divide (UDIV, SDIV)", "Single-Cycle 32-bit Multiply", "Unaligned Memory Access"],
    coreRegisters: ["R0-R12", "SP (MSP / PSP)", "LR (R14)", "PC (R15)", "xPSR", "PRIMASK", "FAULTMASK", "BASEPRI", "CONTROL"],
    nvicSpec: {
      maxInterrupts: 240,
      priorityBits: 4,
      subPriorityGrouping: true,
      tailChainingCycles: 6,
      lateArrivalCycles: 6
    },
    systickTimer: {
      bits: 24,
      countsDown: true
    },
    hasHardwareFpu: false,
    hasDspextension: false
  },
  "Cortex-M4F": {
    core: "Cortex-M4F",
    architectureVersion: "ARMv7E-M",
    pipelineStages: 3,
    isaFeatures: ["Thumb-2", "Hardware Integer Divide", "Single-Cycle MAC (32x32 -> 64-bit)", "Single-Precision FPU (FPv4-SP)", "DSP SIMD Instructions"],
    coreRegisters: ["R0-R12", "SP (MSP / PSP)", "LR (R14)", "PC (R15)", "xPSR", "PRIMASK", "FAULTMASK", "BASEPRI", "CONTROL", "S0-S31 (FPU)", "FPSCR"],
    nvicSpec: {
      maxInterrupts: 240,
      priorityBits: 4,
      subPriorityGrouping: true,
      tailChainingCycles: 6,
      lateArrivalCycles: 6
    },
    systickTimer: {
      bits: 24,
      countsDown: true
    },
    hasHardwareFpu: true,
    fpuSpec: {
      standard: "IEEE 754-2008",
      precision: "Single-Precision (FPv4-SP)",
      registers: "32 single-precision registers (S0-S31) or 16 double-word registers (D0-D15)",
      lazyStackingSupported: true
    },
    hasDspextension: true
  }
};

export const STM32_DEVICE_PROFILES: Record<"STM32F103" | "STM32F401", Stm32DeviceProfile> = {
  "STM32F103": {
    deviceCode: "STM32F103",
    chipPartNumber: "STM32F103C8T6",
    boardTarget: "Blue Pill (STM32F103C8T6)",
    family: "STM32F1",
    cortexSpec: ARM_CORTEX_SPECS["Cortex-M3"],
    maxCpuClockMhz: 72,
    flashMemoryKb: 64,
    sramMemoryKb: 20,
    voltageSupply: "2.0V to 3.6V (Typical 3.3V)",
    busTopologies: {
      ahbMhz: 72,
      apb1Mhz: 36,
      apb2Mhz: 72,
      busMatrixDescription: "Multi-layer AHB bus matrix connecting Cortex-M3 core, DMA bus, and flash memory to APB1/APB2 peripheral bridges."
    },
    registerMap: {
      gpioConfig: {
        style: "CRL_CRH_CNF_MODE",
        registers: ["GPIOx_CRL (Pins 0-7)", "GPIOx_CRH (Pins 8-15)", "GPIOx_IDR", "GPIOx_ODR", "GPIOx_BSRR", "GPIOx_BRR", "GPIOx_LCKR"],
        alternateFunctionRouting: "AFIO_MAPR",
        atomicBitOps: "BSRR_AND_BRR",
        portBaseAddresses: {
          GPIOA: "0x40010800",
          GPIOB: "0x40010C00",
          GPIOC: "0x40011000",
          GPIOD: "0x40011400"
        }
      },
      rccClockConfig: {
        registers: ["RCC_CR", "RCC_CFGR", "RCC_CIR", "RCC_APB2RSTR", "RCC_APB1RSTR", "RCC_AHBENR", "RCC_APB2ENR", "RCC_APB1ENR"],
        pllEquation: "SYSCLK = (HSE / PLLXTPRE) * PLLMUL (Max 72 MHz)",
        internalOscMhz: 8,
        crystalMaxMhz: 16,
        flashWaitStatesTable: [
          { maxFreqMhz: 24, waitStates: 0 },
          { maxFreqMhz: 48, waitStates: 1 },
          { maxFreqMhz: 72, waitStates: 2 }
        ]
      },
      dmaArchitecture: {
        organization: "Channels",
        controllerCount: 1,
        fifoSupport: false,
        circularMode: true,
        registers: ["DMA_ISR", "DMA_IFCR", "DMA_CCRx", "DMA_CNDTRx", "DMA_CPARx", "DMA_CMARx"]
      },
      timerMatrix: {
        advancedControlTimers: ["TIM1 (16-bit PWM with break/deadtime)"],
        generalPurposeTimers: ["TIM2", "TIM3", "TIM4 (16-bit up/down/center)"],
        basicTimers: [],
        prescalerResolution: "16-bit (1 to 65536)",
        counterResolution: "16-bit (0 to 65535)"
      }
    },
    packageType: "LQFP48",
    debuggerInterface: "ST-LINK V2 / SWD"
  },
  "STM32F401": {
    deviceCode: "STM32F401",
    chipPartNumber: "STM32F401RET6",
    boardTarget: "Nucleo-F401RE",
    family: "STM32F4",
    cortexSpec: ARM_CORTEX_SPECS["Cortex-M4F"],
    maxCpuClockMhz: 84,
    flashMemoryKb: 512,
    sramMemoryKb: 96,
    voltageSupply: "1.7V to 3.6V (Typical 3.3V)",
    busTopologies: {
      ahbMhz: 84,
      apb1Mhz: 42,
      apb2Mhz: 84,
      busMatrixDescription: "32-bit multi-layer AHB matrix with separate I-Code, D-Code, System, and DMA master buses for concurrent memory access."
    },
    registerMap: {
      gpioConfig: {
        style: "MODER_OTYPER_OSPEEDR_PUPDR",
        registers: ["GPIOx_MODER", "GPIOx_OTYPER", "GPIOx_OSPEEDR", "GPIOx_PUPDR", "GPIOx_IDR", "GPIOx_ODR", "GPIOx_BSRR", "GPIOx_LCKR", "GPIOx_AFR[0]", "GPIOx_AFR[1]"],
        alternateFunctionRouting: "AFR_LOW_HIGH",
        atomicBitOps: "BSRR_SET_RESET",
        portBaseAddresses: {
          GPIOA: "0x40020000",
          GPIOB: "0x40020400",
          GPIOC: "0x40020800",
          GPIOD: "0x40020C00",
          GPIOE: "0x40021000",
          GPIOH: "0x40021C00"
        }
      },
      rccClockConfig: {
        registers: ["RCC_CR", "RCC_PLLCFGR", "RCC_CFGR", "RCC_CIR", "RCC_AHB1ENR", "RCC_AHB2ENR", "RCC_APB1ENR", "RCC_APB2ENR"],
        pllEquation: "VCO_IN = PLL_IN / PLL_M; VCO_OUT = VCO_IN * PLL_N; SYSCLK = VCO_OUT / PLL_P (Max 84 MHz)",
        internalOscMhz: 16,
        crystalMaxMhz: 26,
        flashWaitStatesTable: [
          { maxFreqMhz: 30, waitStates: 0 },
          { maxFreqMhz: 60, waitStates: 1 },
          { maxFreqMhz: 84, waitStates: 2 }
        ]
      },
      dmaArchitecture: {
        organization: "StreamsAndChannels",
        controllerCount: 2,
        fifoSupport: true,
        circularMode: true,
        registers: ["DMA_LISR", "DMA_HISR", "DMA_LIFCR", "DMA_HIFCR", "DMA_SxCR", "DMA_SxNDTR", "DMA_SxPAR", "DMA_SxM0AR", "DMA_SxM1AR", "DMA_SxFCR"]
      },
      timerMatrix: {
        advancedControlTimers: ["TIM1 (16-bit 3-phase PWM with deadtime)"],
        generalPurposeTimers: ["TIM2 (32-bit)", "TIM5 (32-bit)", "TIM3 (16-bit)", "TIM4 (16-bit)", "TIM9", "TIM10", "TIM11"],
        basicTimers: [],
        prescalerResolution: "16-bit (1 to 65536)",
        counterResolution: "16-bit or 32-bit (TIM2/TIM5)"
      }
    },
    packageType: "LQFP64",
    debuggerInterface: "ST-LINK V2-1 On-Board SWD"
  }
};

export function getStm32DeviceProfile(device: "STM32F103" | "STM32F401"): Stm32DeviceProfile {
  return STM32_DEVICE_PROFILES[device] || STM32_DEVICE_PROFILES["STM32F401"];
}

export function compareStm32Registers(feature: "gpio" | "rcc" | "dma" | "nvic" | "fpu") {
  switch (feature) {
    case "gpio":
      return {
        f1: "GPIOx_CRL / CRH (4 bits per pin: 2-bit MODE + 2-bit CNF). Alternate function remapping routed through global AFIO_MAPR.",
        f4: "GPIOx_MODER (2 bits), OTYPER (1 bit), OSPEEDR (2 bits), PUPDR (2 bits). Alternate function routed pin-by-pin via AFR[0]/AFR[1] (4 bits per pin: AF0-AF15).",
        architecturalNote: "STM32F4 decouples mode, output type, speed, and pull-up/pull-down into orthogonal registers, eliminating F1 read-modify-write hazards."
      };
    case "rcc":
      return {
        f1: "RCC_CFGR sets PLLMUL (2 to 16) directly from HSE/HSI. Max 72 MHz at 2 flash wait states.",
        f4: "RCC_PLLCFGR uses M, N, P, Q dividers (VCO in = HSE/M, VCO out = VCO in * N, SYSCLK = VCO out / P). Max 84 MHz at 2 flash wait states with ART Accelerator.",
        architecturalNote: "STM32F4 PLL architecture allows dedicated USB OTG 48MHz clock generation while independently clocking CPU at 84MHz."
      };
    case "dma":
      return {
        f1: "DMA1 (7 channels), fixed hardware request mapping per channel, direct peripheral-to-memory transfers.",
        f4: "DMA1 & DMA2 (8 streams per controller, each stream selectable from 8 channels), 4-word FIFO buffering, double-buffering support.",
        architecturalNote: "STM32F4 streams allow channel multiplexing and burst transfers with FIFO threshold packing."
      };
    case "nvic":
      return {
        f1: "ARM Cortex-M3 NVIC: 16 priority levels (4 bits implemented in SCB->AIRCR), 6-cycle tail-chaining.",
        f4: "ARM Cortex-M4F NVIC: 16 priority levels, hardware FPU register auto-stacking, optional lazy stacking.",
        architecturalNote: "Cortex-M4F lazy stacking defers pushing 16 FPU registers (S0-S15, FPSCR) unless an ISR executes floating-point instructions."
      };
    case "fpu":
      return {
        f1: "Software emulation only (soft-float libgcc calls, ~20-80 cycles per float op).",
        f4: "Hardware single-precision VFPv4-SP (Single-cycle VADD.F32, VMUL.F32, 14-cycle VDIV.F32, VSQRT.F32).",
        architecturalNote: "Hardware FPU provides ~15-25x speedup for real-time DSP filters, Kalman filters, and motor vector control."
      };
  }
}

// ========================================================================================
// TIER 3 ADVANCED SPECIALIZATION TRACKS SCHEMA & REGISTRY
// ========================================================================================

export interface Tier3SpecializationTrack {
  id: string;
  track: string;
  code: string;
  title: string;
  icon: string;
  themeColor: string;
  slug: string;
  difficulty: "Fundamental" | "Intermediate" | "Advanced" | "Apex Research";
  duration: string;
  simulationComponent: string;
  simRoute: string;
  summary: string;
  hardwareKit: string[];
  prerequisites?: string[];
}

export const TIER3_SPECIALIZATION_TRACKS: Tier3SpecializationTrack[] = [
  {
    id: "iot_edge",
    track: "IoT Edge",
    code: "IOT8701",
    title: "IoT Edge Node Foundations, Bare-Metal GPIO & Low-Power Sleep Architecture",
    icon: "📡",
    themeColor: "#00F0B5",
    slug: "1-iot-foundations",
    difficulty: "Fundamental",
    duration: "45 mins",
    simulationComponent: "IoTSensorSimulatorHub",
    simRoute: "/iot-lab",
    summary: "Master bare-metal memory-mapped GPIO register manipulation, ultra-low-power deep sleep modes, SAR ADC calibration, and PIR sensor acoustics.",
    hardwareKit: ["ESP32 DevKit v4 Microcontroller", "PIR Motion Sensor (HC-SR501)", "Analog Ambient Light Sensor (LDR / TEMT6000)", "Digital Multimeter"],
    prerequisites: ["EC8702", "EC23C03"]
  },
  {
    id: "automotive_radar",
    track: "Automotive Radar",
    code: "AUTO8702",
    title: "Automotive Radar & Ultrasonic Edge Sensing Telemetry",
    icon: "🚗",
    themeColor: "#F59E0B",
    slug: "2-automotive-edge",
    difficulty: "Intermediate",
    duration: "60 mins",
    simulationComponent: "VirtualOscilloscope",
    simRoute: "/virtual-bench",
    summary: "Design automotive ultrasonic Time-of-Flight obstacle detection and CAN-bus telemetry nodes, analyzing acoustic multipath reflections and thermal drift.",
    hardwareKit: ["HC-SR04 40kHz Ultrasonic Transducer Module", "MCP2515 CAN Bus Controller + TJA1050 Transceiver (SPI)", "DS18B20 1-Wire Digital Temperature Sensor", "ESP32 Automotive Gateway Node"],
    prerequisites: ["IOT8701", "EC23C04"]
  },
  {
    id: "defense_uav",
    track: "Defense UAV",
    code: "UAV8703",
    title: "Defense UAV Telemetry & Frequency-Hopping Spread Spectrum (FHSS)",
    icon: "🛩️",
    themeColor: "#38BDF8",
    slug: "3-defense-uav",
    difficulty: "Apex Research",
    duration: "90 mins",
    simulationComponent: "IotTelemetryHub",
    simRoute: "/telemetry",
    summary: "Design anti-jamming UAV telemetry links using Semtech SX1280 2.4 GHz transceivers, pseudorandom frequency hopping, and FreeRTOS deterministic SPI DMA pipelines.",
    hardwareKit: ["Semtech SX1280 2.4 GHz LoRa Transceiver (SPI)", "Semtech SX1262 915 MHz Sub-GHz Transceiver", "ESP32-S3 Dual-Core Xtensa LX7 Microcontroller", "0.5 PPM TCXO"],
    prerequisites: ["EC23C04", "EC23C03"]
  },
  {
    id: "railway_ai",
    track: "Railway AI",
    code: "RAIL8704",
    title: "High-Speed Railway Edge AI & Optical Track Defect Classification",
    icon: "🚆",
    themeColor: "#EC4899",
    slug: "4-railway-edge-ai",
    difficulty: "Apex Research",
    duration: "75 mins",
    simulationComponent: "TinyMlEngineHub",
    simRoute: "/embedded-systems",
    summary: "Deploy quantized TinyML convolutional neural networks (MobileNet-V2 INT8) on edge hardware to detect rail cracks, missing fasteners, and gauge variations.",
    hardwareKit: ["NVIDIA Jetson Nano Developer Kit", "ESP32-CAM (OV2640 2MP Camera Module)", "ADXL345 3-Axis Digital Accelerometer", "High-Speed Global Shutter USB3 Camera"],
    prerequisites: ["IOT8701", "EC23C03"]
  },
  {
    id: "riscv_rtl",
    track: "RISC-V RTL",
    code: "RISCV8705",
    title: "5-Stage Pipelined RV32I RISC-V Soft-Core Processor Design",
    icon: "⚙️",
    themeColor: "#8B5CF6",
    slug: "5-riscv-fpga",
    difficulty: "Apex Research",
    duration: "120 mins",
    simulationComponent: "FpgaSynthesisHub",
    simRoute: "/simulation",
    summary: "Architect and synthesize a 5-stage classic pipelined 32-bit RISC-V (RV32I) soft-core processor in Verilog HDL for Xilinx Artix-7 FPGAs with hazard forwarding.",
    hardwareKit: ["Digilent Basys 3 / Nexys A7 FPGA Board (Artix-7 XC7A35T)", "Xilinx Vivado Design Suite", "JTAG HS2 Programming Cable", "Digilent Pmod USBUART"],
    prerequisites: ["EC3352", "EC23C05"]
  },
  {
    id: "freertos_scheduling",
    track: "FreeRTOS Scheduling",
    code: "RTOS8706",
    title: "Real-Time Operating Systems (FreeRTOS) & Deterministic Multi-Core Scheduling",
    icon: "⏱️",
    themeColor: "#10B981",
    slug: "6-embedded-rtos",
    difficulty: "Apex Research",
    duration: "90 mins",
    simulationComponent: "RtosSchedulerHub",
    simRoute: "/embedded-systems",
    summary: "Master FreeRTOS kernel internals on ARM Cortex-M and dual-core Xtensa ESP32, analyzing priority inversion inheritance, RMS vs EDF bounds, and PendSV switching.",
    hardwareKit: ["STMicroelectronics STM32F401RE Nucleo-64", "ESP32-S3 Dual-Core Xtensa LX7 DevKit", "Segger J-Link EDU Mini Debugger", "Rigol DS1054Z 4-Channel Oscilloscope"],
    prerequisites: ["EC8702", "EC23C03"]
  },
  {
    id: "advanced_analog",
    track: "Advanced Analog",
    code: "ANLG8707",
    title: "Advanced Analog Small-Signal Foundations & High-Frequency Signal Integrity",
    icon: "📈",
    themeColor: "#F97316",
    slug: "7-analog-signal-integrity",
    difficulty: "Apex Research",
    duration: "90 mins",
    simulationComponent: "LtspiceSimulationViewer",
    simRoute: "/virtual-bench",
    summary: "Rigorous analytical textbook covering BJT/MOSFET small-signal hybrid-pi derivations, pole-zero transfer functions, Maxwell EM boundary equations, and Shannon-Hartley capacity.",
    hardwareKit: ["Keysight InfiniiVision 4-Channel 200MHz DSO", "Rohde & Schwarz Vector Network Analyzer", "High-Frequency FR-4 Microstrip Coupon (50-Ohm)", "BJT 2N2222A & MOSFET 2N7000"],
    prerequisites: ["EC3451", "EC23S01"]
  },
  {
    id: "zero_copy_ipc",
    track: "Zero-Copy IPC",
    code: "DMA8708",
    title: "Advanced ARM Cortex-M DMA Architecture & FreeRTOS Zero-Copy IPC",
    icon: "⚡",
    themeColor: "#06B6D4",
    slug: "8-advanced-rtos-dma",
    difficulty: "Apex Research",
    duration: "90 mins",
    simulationComponent: "DmaNvicHub",
    simRoute: "/virtual-bench",
    summary: "High-throughput DMA controller architectures on ARM Cortex-M4/M7, analyzing multi-layer AHB crossbar bus matrix contention, circular ping-pong buffering, and zero-copy stream buffers.",
    hardwareKit: ["STMicroelectronics STM32F446RE Nucleo-64", "ESP32-S3 Dual-Core Xtensa LX7 DevKit with GDMA", "Analog Devices AD7606 16-Bit ADC", "Keysight DSOX1204G Oscilloscope"],
    prerequisites: ["EC8702", "EC23C05"]
  },
  {
    id: "tinyml",
    track: "TinyML",
    code: "TML8709",
    title: "TinyML Edge AI Neural Networks & Vibration FFT Anomaly Detection",
    icon: "🧠",
    themeColor: "#A855F7",
    slug: "9-tiny-ml-edge",
    difficulty: "Apex Research",
    duration: "90 mins",
    simulationComponent: "TinyMlEngineHub",
    simRoute: "/embedded-systems",
    summary: "Edge AI TinyML neural network inference on microcontrollers, covering post-training INT8 asymmetric quantization, 64-point FFT feature extraction, and CMSIS-NN SIMD vectorization.",
    hardwareKit: ["ESP32-S3 Dual-Core Xtensa LX7 DevKit", "STMicroelectronics STM32F446RE Nucleo-64", "Analog Devices ADXL345 Accelerometer", "TI TMP117 High-Precision Temp Sensor"],
    prerequisites: ["IOT8701", "EC23S01"]
  },
  {
    id: "instrumentation",
    track: "Instrumentation",
    code: "INST8710",
    title: "Advanced ECE Instrumentation, K-Map Minimization & Bode Plot Dynamics",
    icon: "🔬",
    themeColor: "#EAB308",
    slug: "advanced-ece/10-gate-ece-instrumentation",
    difficulty: "Apex Research",
    duration: "75 mins",
    simulationComponent: "GateEceInteractiveSolvers",
    simRoute: "/gate-ece",
    summary: "Comprehensive analytical guide to digital logic synthesis, 4-variable Gray code Karnaugh map minimization, Bode plot frequency stability, and ARM Cortex-M pipelined assembly tracing.",
    hardwareKit: ["Keysight DSOX1204G Digital Storage Oscilloscope", "Xilinx Artix-7 FPGA Evaluation Board"],
    prerequisites: ["EC3451", "EC23C03"]
  }
];

export function getAllTier3Tracks(): Tier3SpecializationTrack[] {
  return TIER3_SPECIALIZATION_TRACKS;
}

export function getTier3TrackByCode(code: string): Tier3SpecializationTrack | undefined {
  const codeClean = code.toUpperCase().trim();
  return TIER3_SPECIALIZATION_TRACKS.find(t => t.code === codeClean);
}

export function getTier3TrackById(id: string): Tier3SpecializationTrack | undefined {
  return TIER3_SPECIALIZATION_TRACKS.find(t => t.id === id);
}
