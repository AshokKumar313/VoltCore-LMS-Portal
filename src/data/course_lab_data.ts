/**
 * ========================================================================================
 * VoltCore Apex Academia - Laboratory Simulators & Interactive Benchmarks Schema
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead & Systems Architect: Ashok Kumar A
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 *
 * Provides structured experimental configurations for Anna University Regulation 2023:
 *   - EC23S01: Python DSP Filter & FFT Frequency Response Grapher
 *   - EC23C03: Semiconductor Diode & MOSFET IV Characteristic Curve Tracer
 *   - EC23E04: Optical Laser Resonator Stability & Cavity Mode Simulator
 *   - EC8702:  FreeRTOS Task Scheduler & Interrupt Latency Timing Visualizer
 * ========================================================================================
 */

export interface LabParameter {
  id: string;
  name: string;
  min: number;
  max: number;
  step: number;
  defaultValue: number;
  unit: string;
  description: string;
}

export interface LabPreset {
  name: string;
  description: string;
  paramValues: Record<string, number>;
}

export interface ObservationColumn {
  id: string;
  label: string;
  unit: string;
}

export interface VivaQuestion {
  question: string;
  answer: string;
}

export interface LabExercise {
  id: string;
  courseCode: string;
  title: string;
  unitRoman: "I" | "II" | "III" | "IV" | "V";
  apparatus: string[];
  objectives: string[];
  parameters: LabParameter[];
  presets: LabPreset[];
  formulas: string[];
  observationColumns: ObservationColumn[];
  vivaQuestions: VivaQuestion[];
  safetyProtocol: string;
}

export const COURSE_LAB_CATALOG: Record<string, LabExercise[]> = {
  // ===========================================================================
  // COURSE 1: EC23S01 - Numerical and Signal Processing Practice Through Python
  // ===========================================================================
  "EC23S01": [
    {
      id: "EC23S01_LAB1",
      courseCode: "EC23S01",
      title: "Interactive Python DSP Filter & Frequency Response Grapher",
      unitRoman: "II",
      apparatus: [
        "Python 3.11+ with NumPy, SciPy & Matplotlib",
        "VoltCore Digital Oscilloscope & FFT Signal Generator",
        "PC Workstation (HP Victus / Intel Core i5/i7)"
      ],
      objectives: [
        "Design Butterworth lowpass filters using bilinear frequency pre-warping.",
        "Synthesize magnitude and phase Bode plots from digital transfer function H(z).",
        "Observe transition band attenuation roll-off at -20*N dB/decade.",
        "Examine 3dB cutoff frequency accuracy and group delay characteristics."
      ],
      parameters: [
        {
          id: "fc",
          name: "Cutoff Frequency (fc)",
          min: 200,
          max: 4000,
          step: 50,
          defaultValue: 1000,
          unit: "Hz",
          description: "Corner frequency where filter magnitude drops by 3 dB"
        },
        {
          id: "fs",
          name: "Sampling Frequency (fs)",
          min: 4000,
          max: 48000,
          step: 1000,
          defaultValue: 16000,
          unit: "Hz",
          description: "Digital discrete sampling rate satisfying Nyquist criteria (fs > 2*fc)"
        },
        {
          id: "order",
          name: "Butterworth Order (N)",
          min: 1,
          max: 8,
          step: 1,
          defaultValue: 3,
          unit: "poles",
          description: "Number of poles in s-plane determining steepness of roll-off"
        },
        {
          id: "passbandGain",
          name: "Passband Gain (A0)",
          min: 0.5,
          max: 2.0,
          step: 0.1,
          defaultValue: 1.0,
          unit: "V/V",
          description: "DC voltage amplification factor in the linear passband"
        }
      ],
      presets: [
        {
          name: "Standard Audio Low-Pass",
          description: "Speech frequency cutoff at 3.4 kHz with 16 kHz sampling",
          paramValues: { fc: 3400, fs: 16000, order: 4, passbandGain: 1.0 }
        },
        {
          name: "Biomedical ECG Anti-Aliasing",
          description: "Sub-100 Hz cutoff for cardiac telemetry with steep 6th-order roll-off",
          paramValues: { fc: 150, fs: 8000, order: 6, passbandGain: 1.2 }
        },
        {
          name: "High-Steepness Telecom Filter",
          description: "Sharp 8th-order Butterworth brickwall profile",
          paramValues: { fc: 2000, fs: 24000, order: 8, passbandGain: 1.0 }
        }
      ],
      formulas: [
        "|H(j\\Omega)|^2 = \\frac{1}{1 + \\left( \\frac{\\Omega}{\\Omega_c} \\right)^{2N}}",
        "\\text{Attenuation (dB)} = 10 \\log_{10} \\left( \\frac{1}{1 + (f/f_c)^{2N}} \\right)",
        "\\text{Roll-off Rate} = -20 \\times N \\text{ dB/decade}",
        "f_{\\text{Nyquist}} = \\frac{f_s}{2}"
      ],
      observationColumns: [
        { id: "testFreq", label: "Test Freq", unit: "Hz" },
        { id: "ratio", label: "f / fc", unit: "norm" },
        { id: "magGain", label: "|H(f)| Gain", unit: "V/V" },
        { id: "magDb", label: "Gain (dB)", unit: "dB" },
        { id: "regime", label: "Filter Regime", unit: "status" }
      ],
      vivaQuestions: [
        {
          question: "Why is the Butterworth filter known as a 'maximally flat' filter?",
          answer: "Because all derivatives of the magnitude squared response |H(jOmega)|^2 from 1st to (2N-1)th are zero at Omega = 0, ensuring zero ripple across the passband."
        },
        {
          question: "How does the attenuation change if we increase the order N by 1?",
          answer: "Each added pole increases the stopband attenuation roll-off rate by an additional -20 dB/decade (-6 dB/octave)."
        }
      ],
      safetyProtocol: "Ensure digital sampling frequency fs satisfies Nyquist bound (fs >= 2*fc) to prevent spectral aliasing."
    },
    {
      id: "EC23S01_LAB2",
      courseCode: "EC23S01",
      title: "Discrete FFT Spectrum & Windowing Artifacts",
      unitRoman: "I",
      apparatus: [
        "SciPy Signal Processing Module (scipy.signal.windows)",
        "Synthetic Dual-Tone Frequency Generator",
        "Digital Spectrum Analyzer Visualizer"
      ],
      objectives: [
        "Compute discrete fast Fourier transform (FFT) of synthesized dual-tone signals.",
        "Observe spectral leakage and Rayleigh resolution limit under Rectangular and Hamming windows.",
        "Evaluate SNR degradation under additive Gaussian noise."
      ],
      parameters: [
        {
          id: "tone1",
          name: "Primary Tone Frequency",
          min: 100,
          max: 2000,
          step: 50,
          defaultValue: 440,
          unit: "Hz",
          description: "Frequency of first harmonic component"
        },
        {
          id: "tone2",
          name: "Secondary Tone Frequency",
          min: 150,
          max: 2500,
          step: 50,
          defaultValue: 880,
          unit: "Hz",
          description: "Frequency of second harmonic component"
        },
        {
          id: "snrDb",
          name: "Signal-to-Noise Ratio (SNR)",
          min: 5,
          max: 50,
          step: 5,
          defaultValue: 30,
          unit: "dB",
          description: "Additive white Gaussian noise variance control"
        },
        {
          id: "nFft",
          name: "FFT Size (N_points)",
          min: 64,
          max: 1024,
          step: 64,
          defaultValue: 256,
          unit: "bins",
          description: "Number of discrete Fourier transform frequency bins"
        }
      ],
      presets: [
        {
          name: "A4 Tuning Note (440 + 880 Hz)",
          description: "Fundamental tone and octave overtone with high SNR",
          paramValues: { tone1: 440, tone2: 880, snrDb: 40, nFft: 256 }
        },
        {
          name: "Dense Spectral Spacing (1000 + 1100 Hz)",
          description: "Close carrier frequencies testing Rayleigh resolution limit",
          paramValues: { tone1: 1000, tone2: 1100, snrDb: 25, nFft: 512 }
        }
      ],
      formulas: [
        "\\Delta f = \\frac{f_s}{N_{\\text{FFT}}}",
        "X[k] = \\sum_{n=0}^{N-1} x[n] e^{-j 2\\pi k n / N}",
        "\\text{SNR (dB)} = 10 \\log_{10}\\left( \\frac{P_{\\text{signal}}}{P_{\\text{noise}}} \\right)"
      ],
      observationColumns: [
        { id: "binIndex", label: "Bin Index (k)", unit: "bin" },
        { id: "binFreq", label: "Center Freq", unit: "Hz" },
        { id: "magDb", label: "Spectral Power", unit: "dBFS" },
        { id: "harmonicFlag", label: "Harmonic Identification", unit: "tag" }
      ],
      vivaQuestions: [
        {
          question: "What causes spectral leakage in the discrete Fourier transform?",
          answer: "Time-domain truncation of a non-integer number of signal periods by a finite window, causing energy to disperse into neighboring sidelobes."
        }
      ],
      safetyProtocol: "Check that FFT point size is a power of 2 for optimal O(N log N) radix-2 Cooley-Tukey efficiency."
    }
  ],

  // ===========================================================================
  // COURSE 2: EC23C03 - Electronic Devices
  // ===========================================================================
  "EC23C03": [
    {
      id: "EC23C03_LAB1",
      courseCode: "EC23C03",
      title: "Semiconductor Diode & MOSFET IV Characteristic Curve Tracer",
      unitRoman: "II",
      apparatus: [
        "Variable DC Power Supply (0 to 15V)",
        "Digital Multimeter (Keithley 2000 precision series)",
        "N-channel Enhancement MOSFET (2N7000 / IRF540N)",
        "Silicon PN Junction Diode (1N4148 / 1N4007)",
        "Breadboard and 100 Ohm Current-Sense Resistor"
      ],
      objectives: [
        "Trace Shockley exponential forward-bias diode current ID vs VD.",
        "Compute dynamic small-signal resistance rd = eta*VT / ID.",
        "Plot family of MOSFET ID vs VDS curves across varying gate voltages VGS.",
        "Identify Triode (Ohmic) and Saturation regions and determine pinch-off locus."
      ],
      parameters: [
        {
          id: "vf",
          name: "Forward Bias (VD)",
          min: 0.1,
          max: 0.85,
          step: 0.01,
          defaultValue: 0.65,
          unit: "V",
          description: "Forward voltage drop applied across PN junction"
        },
        {
          id: "tempK",
          name: "Junction Temperature (T)",
          min: 250,
          max: 400,
          step: 5,
          defaultValue: 300,
          unit: "K",
          description: "Absolute junction temperature governing thermal voltage VT = kB*T/q"
        },
        {
          id: "eta",
          name: "Ideality Factor (eta)",
          min: 1.0,
          max: 2.0,
          step: 0.05,
          defaultValue: 1.05,
          unit: "factor",
          description: "Recombination-to-diffusion current ratio (1.0 for Si diffusion, 2.0 for recombination)"
        },
        {
          id: "vgs",
          name: "MOSFET Gate Bias (VGS)",
          min: 1.5,
          max: 5.0,
          step: 0.1,
          defaultValue: 3.3,
          unit: "V",
          description: "Gate-to-source bias for MOSFET inversion channel control"
        }
      ],
      presets: [
        {
          name: "Silicon Diode at Room Temp (300K)",
          description: "Nominal silicon junction forward knee at ~0.65V",
          paramValues: { vf: 0.65, tempK: 300, eta: 1.05, vgs: 3.3 }
        },
        {
          name: "High Temperature Diode Stress (375K)",
          description: "Thermal generation increases IS and drops forward knee voltage by ~2 mV/K",
          paramValues: { vf: 0.55, tempK: 375, eta: 1.10, vgs: 3.3 }
        },
        {
          name: "MOSFET Deep Saturation Drive",
          description: "High gate bias (VGS = 4.5V) creating high drain saturation current",
          paramValues: { vf: 0.70, tempK: 300, eta: 1.0, vgs: 4.5 }
        }
      ],
      formulas: [
        "V_T = \\frac{k_B T}{q} \\approx 25.86 \\text{ mV at } 300\\text{ K}",
        "I_D = I_S \\left( e^{\\frac{V_D}{\\eta V_T}} - 1 \\right)",
        "r_d = \\frac{\\eta V_T}{I_D}",
        "I_{D,\\text{sat}} = \\frac{1}{2} k_n' \\frac{W}{L} (V_{GS} - V_{th})^2 (1 + \\lambda V_{DS})"
      ],
      observationColumns: [
        { id: "appliedVd", label: "Voltage VD", unit: "V" },
        { id: "diodeIdMa", label: "Diode ID", unit: "mA" },
        { id: "dynamicRd", label: "Dynamic rd", unit: "Ω" },
        { id: "mosfetIdMa", label: "MOSFET ID (sat)", unit: "mA" },
        { id: "state", label: "Conduction State", unit: "status" }
      ],
      vivaQuestions: [
        {
          question: "Why does the forward voltage of a silicon diode decrease with increasing temperature?",
          answer: "Because intrinsic carrier concentration ni increases exponentially with temperature (ni^2 proportional to T^3 * exp(-Eg/kT)), which increases reverse saturation current IS by ~7%/°C, lowering the forward voltage drop for a fixed current by roughly -2 mV/°C."
        },
        {
          question: "What is the condition for a MOSFET to enter the saturation regime?",
          answer: "The drain-to-source voltage must satisfy VDS >= VGS - Vth, causing the inversion channel to pinch off near the drain terminal."
        }
      ],
      safetyProtocol: "Limit forward diode current below maximum continuous rating (1N4148: 200 mA) to prevent thermal runaway."
    }
  ],

  // ===========================================================================
  // COURSE 3: EC23E04 - Optics and Lasers
  // ===========================================================================
  "EC23E04": [
    {
      id: "EC23E04_LAB1",
      courseCode: "EC23E04",
      title: "Optical Laser Resonator Stability & Cavity Mode Simulator",
      unitRoman: "I",
      apparatus: [
        "Helium-Neon Laser Cavity Assembly (632.8 nm)",
        "Precision Optical Rail & Gimbal Mirror Mounts (Thorlabs)",
        "Dual Spherical Dielectric Mirrors (R1 = 1.0m, R2 = 0.75m)",
        "Spatial Beam Profiler & Fabry-Perot Interferometer"
      ],
      objectives: [
        "Calculate cavity g-parameters: g1 = 1 - L/R1 and g2 = 1 - L/R2.",
        "Plot cavity operating point on the universal g1-g2 stability diagram.",
        "Verify stability condition 0 <= g1*g2 <= 1 for low-diffraction optical containment.",
        "Calculate Fabry-Perot longitudinal mode spacing Delta_nu = c / (2*L)."
      ],
      parameters: [
        {
          id: "cavityLength",
          name: "Cavity Length (L)",
          min: 0.1,
          max: 1.8,
          step: 0.05,
          defaultValue: 0.5,
          unit: "m",
          description: "Physical distance between resonator mirrors along optical axis"
        },
        {
          id: "r1",
          name: "Mirror 1 Radius of Curvature (R1)",
          min: 0.2,
          max: 2.0,
          step: 0.05,
          defaultValue: 1.0,
          unit: "m",
          description: "Radius of curvature of high-reflector mirror (concave > 0)"
        },
        {
          id: "r2",
          name: "Mirror 2 Radius of Curvature (R2)",
          min: 0.2,
          max: 2.0,
          step: 0.05,
          defaultValue: 0.75,
          unit: "m",
          description: "Radius of curvature of output coupler mirror"
        },
        {
          id: "wavelengthNm",
          name: "Laser Wavelength (lambda)",
          min: 400,
          max: 1064,
          step: 1,
          defaultValue: 632.8,
          unit: "nm",
          description: "Emission optical wavelength (He-Ne red: 632.8 nm)"
        }
      ],
      presets: [
        {
          name: "Standard Symmetric Confocal (L = R1 = R2 = 0.5m)",
          description: "Minimum diffraction loss configuration with g1 = g2 = 0 (g1*g2 = 0)",
          paramValues: { cavityLength: 0.5, r1: 0.5, r2: 0.5, wavelengthNm: 632.8 }
        },
        {
          name: "Hemispherical Resonator (L = 0.5m, R1 = inf, R2 = 1.0m)",
          description: "Planar high-reflector with concave output coupler: g1 = 1, g2 = 0.5",
          paramValues: { cavityLength: 0.5, r1: 2.0, r2: 1.0, wavelengthNm: 632.8 }
        },
        {
          name: "Unstable Resonator Frontier (L = 1.2m, R1 = 0.8m, R2 = 0.6m)",
          description: "Beyond stability hyperbola: g1*g2 > 1 producing high geometric output coupling",
          paramValues: { cavityLength: 1.2, r1: 0.8, r2: 0.6, wavelengthNm: 632.8 }
        }
      ],
      formulas: [
        "g_1 = 1 - \\frac{L}{R_1}, \\quad g_2 = 1 - \\frac{L}{R_2}",
        "0 \\le g_1 g_2 \\le 1 \\quad (\\text{Resonator Stability Condition})",
        "\\Delta \\nu = \\frac{c}{2 L}",
        "w_0^2 = \\frac{L \\lambda}{\\pi} \\sqrt{\\frac{g_1 g_2 (1 - g_1 g_2)}{(g_1 + g_2 - 2 g_1 g_2)^2}}"
      ],
      observationColumns: [
        { id: "lengthL", label: "Length L", unit: "m" },
        { id: "g1Val", label: "g1 Param", unit: "dim" },
        { id: "g2Val", label: "g2 Param", unit: "dim" },
        { id: "gProd", label: "g1 * g2", unit: "dim" },
        { id: "modeSpacing", label: "Mode Spacing", unit: "MHz" },
        { id: "stability", label: "Resonator Status", unit: "tag" }
      ],
      vivaQuestions: [
        {
          question: "Why is the confocal resonator (L = R) widely used in gas lasers?",
          answer: "Because it exhibits minimal diffraction losses for transverse TEM00 mode and boasts highest tolerance to slight mirror misalignment."
        },
        {
          question: "What happens when g1 * g2 < 0 or g1 * g2 > 1?",
          answer: "The optical ray walks off the mirror edges after finite round-trips; the resonator becomes geometrically unstable with high output coupling."
        }
      ],
      safetyProtocol: "Always wear Class 3B/4 laser safety goggles matching 632.8 nm optical density (OD 5+) when handling active beam cavities."
    }
  ],

  // ===========================================================================
  // COURSE 4: EC8702 - Embedded Systems
  // ===========================================================================
  "EC8702": [
    {
      id: "EC8702_LAB1",
      courseCode: "EC8702",
      title: "FreeRTOS Task Scheduler & Interrupt Latency Timing Visualizer",
      unitRoman: "IV",
      apparatus: [
        "STM32F401RE Nucleo-64 Board (ARM Cortex-M4 84 MHz)",
        "Saleae 8-Channel USB Logic Analyzer & PulseView",
        "FreeRTOS Kernel v10.4 with preemptive priority scheduler",
        "CMSIS-OS2 Core API wrapper"
      ],
      objectives: [
        "Analyze Rate Monotonic Scheduling (RMS) utilization bounds.",
        "Calculate Liu & Layland schedulability bound U <= n*(2^(1/n) - 1).",
        "Visualize task preemptions and ARM NVIC interrupt tail-chaining (6 cycles).",
        "Audit context-switch overhead and verify deadline compliance."
      ],
      parameters: [
        {
          id: "c1",
          name: "Task 1 Exec Time (C1)",
          min: 2,
          max: 25,
          step: 1,
          defaultValue: 8,
          unit: "ms",
          description: "High priority telemetry sampling computational duration"
        },
        {
          id: "t1",
          name: "Task 1 Period (T1)",
          min: 10,
          max: 60,
          step: 5,
          defaultValue: 30,
          unit: "ms",
          description: "Repetition period and deadline for Task 1"
        },
        {
          id: "c2",
          name: "Task 2 Exec Time (C2)",
          min: 5,
          max: 35,
          step: 1,
          defaultValue: 12,
          unit: "ms",
          description: "Medium priority communication stream computation"
        },
        {
          id: "t2",
          name: "Task 2 Period (T2)",
          min: 20,
          max: 100,
          step: 5,
          defaultValue: 50,
          unit: "ms",
          description: "Repetition period and deadline for Task 2"
        },
        {
          id: "c3",
          name: "Task 3 Exec Time (C3)",
          min: 5,
          max: 40,
          step: 1,
          defaultValue: 15,
          unit: "ms",
          description: "Low priority background display logging"
        },
        {
          id: "t3",
          name: "Task 3 Period (T3)",
          min: 40,
          max: 150,
          step: 5,
          defaultValue: 100,
          unit: "ms",
          description: "Repetition period and deadline for Task 3"
        }
      ],
      presets: [
        {
          name: "Guaranteed RMS Schedulable (U = 65.7%)",
          description: "Conservative utilization well below 3-task Liu-Layland bound (77.98%)",
          paramValues: { c1: 5, t1: 30, c2: 12, t2: 60, c3: 15, t3: 120 }
        },
        {
          name: "Near Bound Operating Point (U = 76.5%)",
          description: "Optimized utilization hovering immediately under the 77.98% threshold",
          paramValues: { c1: 8, t1: 30, c2: 14, t2: 50, c3: 20, t3: 100 }
        },
        {
          name: "CPU Overload & Deadline Miss (U = 95.0%)",
          description: "Excessive task load producing deadline miss on lowest-priority Task 3",
          paramValues: { c1: 15, t1: 30, c2: 20, t2: 50, c3: 35, t3: 100 }
        }
      ],
      formulas: [
        "U = \\sum_{i=1}^{n} \\frac{C_i}{T_i} = \\frac{C_1}{T_1} + \\frac{C_2}{T_2} + \\frac{C_3}{T_3}",
        "U_{\\text{bound}}(n) = n \\left( 2^{1/n} - 1 \\right)",
        "U_{\\text{bound}}(3) = 3(2^{1/3} - 1) \\approx 0.7798 \\quad (77.98\\%)",
        "T_{\\text{tail-chain}} = 6 \\text{ clock cycles (NVIC hardware optimization)}"
      ],
      observationColumns: [
        { id: "u1Pct", label: "Task 1 U%", unit: "%" },
        { id: "u2Pct", label: "Task 2 U%", unit: "%" },
        { id: "u3Pct", label: "Task 3 U%", unit: "%" },
        { id: "totalUPct", label: "Total CPU U%", unit: "%" },
        { id: "boundPct", label: "Bound (n=3)", unit: "%" },
        { id: "schedStatus", label: "Schedulability Verdict", unit: "tag" }
      ],
      vivaQuestions: [
        {
          question: "What is the key difference between Rate Monotonic (RMS) and Earliest Deadline First (EDF) scheduling?",
          answer: "RMS is a static-priority algorithm (shorter period = higher fixed priority) with upper utilization bound ~69.3% as n -> inf, whereas EDF is dynamic-priority (nearest deadline = highest priority) achieving up to 100% theoretical CPU utilization."
        },
        {
          question: "How does ARM Cortex-M NVIC hardware tail-chaining reduce interrupt latency?",
          answer: "By keeping the 8 saved registers on the stack between consecutive interrupts, the NVIC transitions to a pending ISR in only 6 cycles instead of 24+ cycles for unstacking and re-stacking."
        }
      ],
      safetyProtocol: "Verify priority levels such that critical sensor sampling interrupts cannot be preempted by lower-priority communication tasks."
    }
  ]
};

/**
 * Helper to retrieve all lab exercises for a given course code.
 */
export function getLabsByCourse(courseCode: string): LabExercise[] {
  return COURSE_LAB_CATALOG[courseCode] || [];
}

/**
 * Helper to retrieve a specific lab exercise by ID.
 */
export function getLabById(id: string): LabExercise | undefined {
  for (const list of Object.values(COURSE_LAB_CATALOG)) {
    const found = list.find(l => l.id === id);
    if (found) return found;
  }
  return undefined;
}
