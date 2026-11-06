/**
 * ========================================================================================
 * VoltCore Apex Academia - Projects, Practicals & Progress Tracking Data Schema
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead & Systems Architect: Ashok Kumar A
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 *
 * Provides:
 *   - Mini-projects and Capstone project libraries for 4 priority courses
 *   - Practical experiment checklists and calculation worksheets
 *   - Structured milestones aligned with Anna University Continuous Internal Evaluation (CIE)
 *   - Rubrics for lab report generation and viva-voce examination
 * ========================================================================================
 */

export interface ProjectMilestone {
  id: string;
  title: string;
  description: string;
  deliverable: string;
  weightagePct: number;
}

export interface CourseProject {
  id: string;
  courseCode: string;
  title: string;
  type: "mini" | "major";
  difficulty: "Beginner" | "Intermediate" | "Advanced";
  estimatedHours: number;
  summary: string;
  hardwareApparatus: string[];
  softwareTools: string[];
  domainKeywords: string[];
  milestones: ProjectMilestone[];
  expectedOutcomes: string[];
}

export interface CalculationWorksheet {
  formula: string;
  description: string;
  parameters: string[];
  sampleValues: Record<string, number>;
  expectedResult: string;
}

export interface PracticalExperiment {
  id: string;
  courseCode: string;
  labNumber: number;
  title: string;
  unitRoman: "I" | "II" | "III" | "IV" | "V";
  aim: string;
  softwareHardware: string;
  rubricMarks: {
    preparation: number;
    execution: number;
    analysis: number;
    viva: number;
  };
  calculationWorksheet: CalculationWorksheet;
}

export const COURSE_PROJECTS_CATALOG: Record<string, CourseProject[]> = {
  // ===========================================================================
  // COURSE 1: EC23S01 - Numerical and Signal Processing Practice Through Python
  // ===========================================================================
  "EC23S01": [
    {
      id: "EC23S01_PRJ1",
      courseCode: "EC23S01",
      title: "Real-Time Acoustic Heart Sound (PCG) Noise Cancellation Using LMS Adaptive Filter",
      type: "mini",
      difficulty: "Intermediate",
      estimatedHours: 25,
      summary: "Develop a discrete-time Least Mean Squares (LMS) adaptive filter in Python to denoise phonocardiogram (PCG) acoustic recordings corrupted by ambient respiratory and environmental noise.",
      hardwareApparatus: ["Electret Microphone / Electronic Stethoscope", "Audio Capture Interface", "PC Workstation"],
      softwareTools: ["Python 3.11", "NumPy", "SciPy Signal", "Matplotlib", "PyAudio"],
      domainKeywords: ["Adaptive Filtering", "LMS Algorithm", "Biomedical DSP", "Noise Cancellation"],
      milestones: [
        { id: "M1", title: "Dataset Acquisition & Spectral Profiling", description: "Collect and synthesize noisy PCG wavefiles; compute Welch power spectral density.", deliverable: "Input Signal Spectrum (.png / .csv)", weightagePct: 25 },
        { id: "M2", title: "LMS Filter Weight Convergence", description: "Formulate weight update vector w[n+1] = w[n] + 2*mu*e[n]*x[n] and optimize step size mu.", deliverable: "Filter Convergence Plot", weightagePct: 25 },
        { id: "M3", title: "SNR Evaluation & Denoising Benchmark", description: "Quantify SNR improvement in dB and compute Mean Squared Error (MSE).", deliverable: "SNR Benchmark Table", weightagePct: 25 },
        { id: "M4", title: "Interactive Audio Player & Technical Report", description: "Package filter pipeline with before/after audio playback and IEEE format report.", deliverable: "Final Report & Audio Demos", weightagePct: 25 }
      ],
      expectedOutcomes: [
        "Mastery of discrete Wiener filter formulation and gradient descent convergence.",
        "Demonstrated >14 dB SNR improvement on physiological audio signals.",
        "Implementation of real-time streaming buffer processing in Python."
      ]
    },
    {
      id: "EC23S01_PRJ2",
      courseCode: "EC23S01",
      title: "Edge-AI Audio Keyword Spotting & Spectrogram Feature Extractor",
      type: "major",
      difficulty: "Advanced",
      estimatedHours: 50,
      summary: "Build an end-to-end edge keyword recognition system using Short-Time Fourier Transform (STFT), Mel-Frequency Cepstral Coefficients (MFCC), and lightweight 1D-CNN on embedded hardware.",
      hardwareApparatus: ["Raspberry Pi 4 / STM32F4 Discovery", "I2S Digital MEMS Microphone (INMP441)"],
      softwareTools: ["Python TensorFlow Lite", "SciPy FFT", "Edge Impulse", "CMSIS-DSP"],
      domainKeywords: ["STFT", "MFCC", "Edge AI", "Embedded TinyML", "Speech Recognition"],
      milestones: [
        { id: "M1", title: "Audio Preprocessing & STFT Spectrograms", description: "Implement sliding Hamming window STFT and 40-band Mel filterbank in pure Python.", deliverable: "Mel Spectrogram Matrix", weightagePct: 20 },
        { id: "M2", title: "TinyML Classifier Training", description: "Train compact Convolutional Neural Network with quantized int8 weights.", deliverable: "Quantized .tflite model (<50 KB)", weightagePct: 30 },
        { id: "M3", title: "Hardware Deployment & DMA Audio Buffer", description: "Stream 16 kHz I2S audio via DMA circular double buffering to inference engine.", deliverable: "Oscilloscope / UART Timing Trace", weightagePct: 25 },
        { id: "M4", title: "Latency & Energy Profiling", description: "Measure inference latency (<35 ms) and dynamic power consumption.", deliverable: "IEEE Conference Paper & Poster", weightagePct: 25 }
      ],
      expectedOutcomes: [
        "End-to-end signal processing from analog acoustics to discrete edge inference.",
        "92%+ keyword recognition accuracy under realistic classroom acoustic conditions.",
        "Publication-ready documentation conforming to MIT Campus undergraduate standards."
      ]
    }
  ],

  // ===========================================================================
  // COURSE 2: EC23C03 - Electronic Devices
  // ===========================================================================
  "EC23C03": [
    {
      id: "EC23C03_PRJ1",
      courseCode: "EC23C03",
      title: "Temperature-Compensated CMOS Bandgap Voltage Reference (BGR)",
      type: "mini",
      difficulty: "Intermediate",
      estimatedHours: 25,
      summary: "Design and simulate a sub-1V CMOS bandgap voltage reference circuit combining Proportional to Absolute Temperature (PTAT) and Complementary to Absolute Temperature (CTAT) currents to achieve <20 ppm/°C temperature coefficient.",
      hardwareApparatus: ["PC Workstation with SPICE Simulator", "Cadence Virtuoso / LTspice XVII"],
      softwareTools: ["LTspice", "Python NumPy (SPICE raw parser)", "Matplotlib"],
      domainKeywords: ["Bandgap Reference", "PTAT / CTAT", "CMOS Analog", "Temperature Coefficient"],
      milestones: [
        { id: "M1", title: "Bipolar Core & Thermal Voltage Formulation", description: "Derive Delta_VBE = VT * ln(N) using diode-connected substrate PNPs.", deliverable: "Analytical Derivation Document", weightagePct: 25 },
        { id: "M2", title: "Resistor Ratio & Zero-TC Bias Tuning", description: "Tune resistor ratios R1/R2 to balance positive PTAT slope against negative CTAT VBE slope.", deliverable: "LTspice Netlist (.cir) & Schematics", weightagePct: 25 },
        { id: "M3", title: "Temperature Sweep Simulation (-40°C to +125°C)", description: "Simulate reference output voltage Vref across military thermal envelope.", deliverable: "Vref vs Temp Curve & TC Metric", weightagePct: 25 },
        { id: "M4", title: "Power Supply Rejection Ratio (PSRR) Analysis", description: "Measure AC PSRR from 10 Hz to 1 MHz and compile project dossier.", deliverable: "PSRR Bode Plot & Final Report", weightagePct: 25 }
      ],
      expectedOutcomes: [
        "Mastery of second-order semiconductor thermal dependencies.",
        "Verification of zero-temperature-coefficient inflection point near 300K.",
        "Understanding of substrate PNP parasitics in standard CMOS technology."
      ]
    },
    {
      id: "EC23C03_PRJ2",
      courseCode: "EC23C03",
      title: "Sub-Threshold Low-Power Biosensor Front-End with Integrated Photodiode",
      type: "major",
      difficulty: "Advanced",
      estimatedHours: 50,
      summary: "Synthesize an ultra-low-power transimpedance biosensing front-end operating MOSFETs in the weak inversion (sub-threshold) exponential regime for wearable pulse oximetry (PPG).",
      hardwareApparatus: ["Silicon PIN Photodiode (BPW34)", "Custom Discrete Breadboard / PCB", "Keithley Picoammeter"],
      softwareTools: ["LTspice", "KiCad 8.0", "Python Data Logging"],
      domainKeywords: ["Sub-Threshold Conduction", "Transimpedance Amplifier", "Biosensor", "PPG Optical"],
      milestones: [
        { id: "M1", title: "Sub-Threshold ID-VGS Modeling", description: "Model weak-inversion exponential current ID = I0 * exp((VGS - Vth)/(n*VT)).", deliverable: "Sub-threshold Slope (SS) Extraction", weightagePct: 20 },
        { id: "M2", title: "Photodiode Interface & TIA Synthesis", description: "Design multi-megohm active feedback TIA with <500 nW total quiescent power.", deliverable: "Circuit Schematic & AC Simulation", weightagePct: 30 },
        { id: "M3", title: "Breadboard Prototype & Pulse Waveform Capture", description: "Assemble physical optoelectronic sensor and acquire real-time arterial plethysmogram.", deliverable: "Digital Oscilloscope Trace & PCB Layout", weightagePct: 25 },
        { id: "M4", title: "Noise Floor & Linearity Verification", description: "Quantify input-referred noise current (pA/sqrt(Hz)) and submit capstone dossier.", deliverable: "Complete Capstone Report", weightagePct: 25 }
      ],
      expectedOutcomes: [
        "In-depth comprehension of sub-threshold conduction physics ($SS \\approx 70\\text{ mV/decade}$).",
        "Sub-microamp battery operation suitable for biomedical wearables.",
        "Comprehensive hardware-software co-verification dossier."
      ]
    }
  ],

  // ===========================================================================
  // COURSE 3: EC23E04 - Optics and Lasers
  // ===========================================================================
  "EC23E04": [
    {
      id: "EC23E04_PRJ1",
      courseCode: "EC23E04",
      title: "Optical Fiber Fabry-Perot Interferometer for Micro-Strain & Thermal Sensing",
      type: "mini",
      difficulty: "Intermediate",
      estimatedHours: 25,
      summary: "Construct an extrinsic Fabry-Perot interferometer (EFPI) sensor using cleaved single-mode optical fiber and a reflective micro-cavity for sub-micrometer displacement and temperature measurement.",
      hardwareApparatus: ["Single-Mode Fiber (SMF-28)", "Precision Fiber Cleaver", "1550 nm DFB Laser Diode", "InGaAs Optical Power Meter"],
      softwareTools: ["Python Optics Simulator", "Matplotlib", "VISA PyVISA Instrument Interface"],
      domainKeywords: ["Fabry-Perot", "Interferometry", "Fiber Optic Sensing", "Phase Sensitivity"],
      milestones: [
        { id: "M1", title: "Air Cavity Multiple-Beam Interference Theory", description: "Derive Airy distribution formula: I_trans = I0 / (1 + F * sin^2(delta/2)).", deliverable: "Interference Model Simulation", weightagePct: 25 },
        { id: "M2", title: "Micro-Cavity Alignment & Fringe Visibility", description: "Align cleaved fiber ends on precision 3-axis micro-positioner; measure fringe contrast.", deliverable: "Optical Fringe Pattern Plot", weightagePct: 25 },
        { id: "M3", title: "Thermal Sensitivity Calibration", description: "Subject EFPI sensor to controlled temperature ramp (25°C to 80°C); extract wavelength shift.", deliverable: "Sensitivity Coefficient (pm/°C)", weightagePct: 25 },
        { id: "M4", title: "Phase Unwrapping Algorithm & Technical Report", description: "Implement digital quadrature phase unwrapping in Python to track dynamic micro-strain.", deliverable: "Final Datalogger Code & Report", weightagePct: 25 }
      ],
      expectedOutcomes: [
        "Practical mastery of optical cavity finesse, phase delay, and coherence bounds.",
        "Achieved displacement resolution < 10 nanometers.",
        "Proficiency with optical lab safety and micro-positioning hardware."
      ]
    },
    {
      id: "EC23E04_PRJ2",
      courseCode: "EC23E04",
      title: "Free-Space Optical (FSO) Laser Transceiver with Adaptive Beam Collimation",
      type: "major",
      difficulty: "Advanced",
      estimatedHours: 50,
      summary: "Design and construct a high-speed line-of-sight laser communication link (100 Mbps) with motorized beam collimation and optical receiver concentrating lenses.",
      hardwareApparatus: ["650 nm 50mW Laser Diode with Modulation Driver", "Avalanche Photodiode (APD) Module", "Collimating Aspheric Lenses", "Stepper Motor Gimbal"],
      softwareTools: ["KiCad", "Python SciPy", "OpenCV (Beam Center Tracking)"],
      domainKeywords: ["Free-Space Optics", "Laser Transceiver", "Beam Divergence", "Atmospheric Attenuation"],
      milestones: [
        { id: "M1", title: "Gaussian Beam Waist & Divergence Modeling", description: "Calculate beam expansion theta = lambda / (pi * w0) and design multi-element collimator.", deliverable: "Zemax / Python Ray Trace Diagram", weightagePct: 20 },
        { id: "M2", title: "Laser Modulation & Driver Circuitry", description: "Build high-speed ECL/LVDS current driver capable of 50 MHz square-wave modulation.", deliverable: "Driver PCB Schematic & Eye Diagram", weightagePct: 30 },
        { id: "M3", title: "Free-Space Link Test (100-Meter Range)", description: "Transmit pseudorandom bit sequence (PRBS-7) across test corridor and evaluate Bit Error Rate (BER).", deliverable: "Bit Error Rate Measurement Graph", weightagePct: 25 },
        { id: "M4", title: "Vision-Guided Active Alignment & Final Dossier", description: "Implement webcam spot tracking to continuously steer beam center onto APD active area.", deliverable: "Active Tracking Video & Capstone Report", weightagePct: 25 }
      ],
      expectedOutcomes: [
        "Comprehensive understanding of laser safety, coherence propagation, and link budgets.",
        "Demonstrated 100 Mbps data transmission over 100 meters with BER < 1e-6.",
        "Full integration of optical physics, high-speed electronics, and embedded vision."
      ]
    }
  ],

  // ===========================================================================
  // COURSE 4: EC8702 - Embedded Systems
  // ===========================================================================
  "EC8702": [
    {
      id: "EC8702_PRJ1",
      courseCode: "EC8702",
      title: "Hard Real-Time Motor Position Controller with FreeRTOS & Quadrature Encoder",
      type: "mini",
      difficulty: "Intermediate",
      estimatedHours: 25,
      summary: "Implement a deterministic PID motor velocity and position controller on an ARM Cortex-M4 microcontroller under FreeRTOS, guaranteeing sub-10 microsecond interrupt jitter.",
      hardwareApparatus: ["STM32F401RE Nucleo-64 Board", "DC Motor with Optical Quadrature Encoder", "L298N / TB6612FNG H-Bridge Driver"],
      softwareTools: ["STM32CubeIDE", "FreeRTOS Kernel", "CMSIS-DSP (arm_pid_f32)", "Saleae Logic"],
      domainKeywords: ["FreeRTOS", "Hard Real-Time", "PID Control", "Quadrature Decoding", "ARM Cortex-M4"],
      milestones: [
        { id: "M1", title: "Hardware Timer Encoder Mode & DMA Capture", description: "Configure TIM2 in 4x Quadrature Decoder mode with zero CPU overhead.", deliverable: "Timer Register Configuration Code", weightagePct: 25 },
        { id: "M2", title: "Preemptive FreeRTOS Task Hierarchy", description: "Implement 1 kHz Control Task (High Priority), Telemetry Task (Med), and UART Shell (Low).", deliverable: "Task Architecture Diagram & Trace", weightagePct: 25 },
        { id: "M3", title: "CMSIS-DSP Floating-Point PID Tuning", description: "Tune proportional, integral, and derivative coefficients using Ziegler-Nichols method.", deliverable: "Step Response Transient Curve", weightagePct: 25 },
        { id: "M4", title: "Interrupt Jitter & Deadline Audit", description: "Use GPIO toggle and logic analyzer to verify <10 us ISR jitter and compile report.", deliverable: "Jitter Histogram & Technical Report", weightagePct: 25 }
      ],
      expectedOutcomes: [
        "In-depth mastery of preemptive task scheduling and hardware timer peripherals.",
        "Deterministic control loop execution with zero missed deadlines.",
        "Proficiency with CMSIS-DSP math library for real-time digital filtering."
      ]
    },
    {
      id: "EC8702_PRJ2",
      courseCode: "EC8702",
      title: "Autonomous TinyML Drone Flight Controller with Fault-Tolerant RTOS",
      type: "major",
      difficulty: "Advanced",
      estimatedHours: 50,
      summary: "Develop a fault-tolerant quadcopter attitude estimation and stabilization controller fusing IMU telemetry via Extended Kalman Filter (EKF) and TinyML anomaly detection.",
      hardwareApparatus: ["STM32F405 / ESP32-S3 Board", "MPU-6050 6-DOF IMU", "QMC5883L Magnetometer", "4x Electronic Speed Controllers (ESCs)"],
      softwareTools: ["STM32CubeIDE", "FreeRTOS v10.4", "Python NumPy / SciPy", "Edge Impulse"],
      domainKeywords: ["Sensor Fusion", "Extended Kalman Filter", "TinyML Anomaly Detection", "Fault-Tolerant RTOS"],
      milestones: [
        { id: "M1", title: "I2C DMA Sensor Read & EKF Quaternion Fusion", description: "Implement 500 Hz sensor polling with DMA and Madgwick/EKF attitude fusion.", deliverable: "Quaternion Attitude Trajectory Plot", weightagePct: 20 },
        { id: "M2", title: "Watchdog & Priority Ceiling Protocol (PCP)", description: "Implement Window Watchdog (WWDG) and PCP mutexes to eliminate priority inversion and deadlocks.", deliverable: "Fault-Recovery State Machine Diagram", weightagePct: 30 },
        { id: "M3", title: "TinyML Motor Vibration Anomaly Detector", description: "Deploy 8-bit quantized autoencoder on Cortex-M4 to detect mechanical propeller imbalance.", deliverable: "Anomaly Score Classifier Output", weightagePct: 25 },
        { id: "M4", title: "Hardware-in-the-Loop (HIL) Flight Test & Dossier", description: "Execute 6-DOF flight simulation bench test and assemble final departmental thesis dossier.", deliverable: "HIL Telemetry Logs & Thesis Report", weightagePct: 25 }
      ],
      expectedOutcomes: [
        "Complete systems architecture integrating sensor fusion, RTOS concurrency, and edge ML.",
        "Robust fail-safe behavior with sub-millisecond fault recovery.",
        "Exemplary undergraduate capstone presentation conforming to MIT Campus accreditation criteria."
      ]
    }
  ]
};

// =============================================================================
// PRACTICAL EXPERIMENT CHECKLISTS (ANNA UNIVERSITY REGULATION 2023)
// =============================================================================

export const COURSE_PRACTICALS_CHECKLIST: Record<string, PracticalExperiment[]> = {
  "EC23S01": [
    {
      id: "EC23S01_EXP1",
      courseCode: "EC23S01",
      labNumber: 1,
      title: "Discrete Linear & Circular Convolution via NumPy and SciPy",
      unitRoman: "I",
      aim: "To compute the linear and circular convolution of two discrete sequences x[n] and h[n] using Python and verify the zero-padding condition.",
      softwareHardware: "Python 3.11+, NumPy, SciPy",
      rubricMarks: { preparation: 5, execution: 10, analysis: 10, viva: 5 },
      calculationWorksheet: {
        formula: "L = N_1 + N_2 - 1, \\quad y[n] = \\sum_{k=-\\infty}^{\\infty} x[k] h[n-k]",
        description: "Calculate linear convolution length and minimum zero-padding DFT size.",
        parameters: ["Length of sequence x (N1)", "Length of filter h (N2)"],
        sampleValues: { N1: 8, N2: 6 },
        expectedResult: "Length L = 13 samples; Radix-2 FFT size = 16 points"
      }
    },
    {
      id: "EC23S01_EXP2",
      courseCode: "EC23S01",
      labNumber: 2,
      title: "Design of Butterworth IIR Low-Pass Filter Using Bilinear Transformation",
      unitRoman: "II",
      aim: "To design a digital Butterworth low-pass filter satisfying specified passband and stopband attenuation using bilinear frequency pre-warping.",
      softwareHardware: "Python SciPy Signal (scipy.signal.butter, bilinear)",
      rubricMarks: { preparation: 5, execution: 10, analysis: 10, viva: 5 },
      calculationWorksheet: {
        formula: "\\Omega_p = \\frac{2}{T} \\tan\\left(\\frac{\\omega_p}{2}\\right), \\quad N = \\left\\lceil \\frac{\\log_{10}(D)}{\\log_{10}(\\Omega_s / \\Omega_p)} \\right\\rceil",
        description: "Pre-warp analog corner frequencies and compute minimum filter order N.",
        parameters: ["Passband cutoff (wp / pi)", "Stopband cutoff (ws / pi)", "Sampling interval T (s)"],
        sampleValues: { wp_norm: 0.2, ws_norm: 0.3, T: 0.0001 },
        expectedResult: "Pre-warped Order N = 4 poles; Roll-off = -80 dB/decade"
      }
    }
  ],
  "EC23C03": [
    {
      id: "EC23C03_EXP1",
      courseCode: "EC23C03",
      labNumber: 1,
      title: "PN Junction Diode Forward and Reverse Characteristics & Dynamic Resistance",
      unitRoman: "I",
      aim: "To plot the forward and reverse bias V-I characteristics of a silicon diode (1N4148) and evaluate static and dynamic resistance.",
      softwareHardware: "Variable DC Power Supply, Keithley DMM, Resistors, 1N4148",
      rubricMarks: { preparation: 5, execution: 10, analysis: 10, viva: 5 },
      calculationWorksheet: {
        formula: "r_d = \\frac{\\eta V_T}{I_D}, \\quad V_T = \\frac{k_B T}{q} \\approx 25.86 \\text{ mV}",
        description: "Calculate theoretical dynamic small-signal resistance for a specified operating point.",
        parameters: ["Operating current ID (mA)", "Ideality factor eta", "Temperature T (K)"],
        sampleValues: { ID_mA: 2.5, eta: 1.0, tempK: 300 },
        expectedResult: "Dynamic resistance rd = 10.34 Ohms at ID = 2.5 mA"
      }
    },
    {
      id: "EC23C03_EXP2",
      courseCode: "EC23C03",
      labNumber: 2,
      title: "Enhancement MOSFET Drain & Transfer Characteristics (2N7000)",
      unitRoman: "III",
      aim: "To determine the threshold voltage Vth, process transconductance kn, and channel length modulation parameter lambda.",
      softwareHardware: "Dual DC Power Supply, Dual DMMs, 2N7000 NMOS, 100 Ohm Sense Resistor",
      rubricMarks: { preparation: 5, execution: 10, analysis: 10, viva: 5 },
      calculationWorksheet: {
        formula: "I_{D,\\text{sat}} = \\frac{1}{2} k_n (V_{GS} - V_{th})^2, \\quad g_m = k_n (V_{GS} - V_{th})",
        description: "Compute saturation current and transconductance for given gate overdrive.",
        parameters: ["Gate-Source VGS (V)", "Threshold Vth (V)", "Parameter kn (mA/V^2)"],
        sampleValues: { VGS: 3.5, Vth: 1.5, kn: 20 },
        expectedResult: "Saturation Current ID = 40.0 mA; Transconductance gm = 40.0 mA/V"
      }
    }
  ],
  "EC23E04": [
    {
      id: "EC23E04_EXP1",
      courseCode: "EC23E04",
      labNumber: 1,
      title: "Laser Resonator Stability Verification & Cavity g-Parameter Mapping",
      unitRoman: "I",
      aim: "To experimentally determine optical resonator mirror positions that satisfy the stability criteria for continuous-wave oscillation.",
      softwareHardware: "He-Ne Optical Rail (632.8 nm), Spherical Mirrors, Power Meter",
      rubricMarks: { preparation: 5, execution: 10, analysis: 10, viva: 5 },
      calculationWorksheet: {
        formula: "g_1 = 1 - \\frac{L}{R_1}, \\quad g_2 = 1 - \\frac{L}{R_2}, \\quad 0 \\le g_1 g_2 \\le 1",
        description: "Evaluate cavity stability condition and product g1*g2.",
        parameters: ["Cavity Length L (m)", "Mirror 1 Radius R1 (m)", "Mirror 2 Radius R2 (m)"],
        sampleValues: { L: 0.6, R1: 1.0, R2: 0.8 },
        expectedResult: "g1 = 0.40, g2 = 0.25, g1*g2 = 0.10 -> STABLE RESONATOR"
      }
    }
  ],
  "EC8702": [
    {
      id: "EC8702_EXP1",
      courseCode: "EC8702",
      labNumber: 1,
      title: "FreeRTOS Preemptive Priority Scheduling & Schedulability Bound Verification",
      unitRoman: "III",
      aim: "To implement multiple periodic tasks under FreeRTOS on ARM Cortex-M4 and verify the Liu & Layland schedulability bound.",
      softwareHardware: "STM32F401RE Nucleo, STM32CubeIDE, Logic Analyzer",
      rubricMarks: { preparation: 5, execution: 10, analysis: 10, viva: 5 },
      calculationWorksheet: {
        formula: "U = \\sum_{i=1}^n \\frac{C_i}{T_i} \\le n(2^{1/n} - 1)",
        description: "Calculate total CPU load and compare against the theoretical bound.",
        parameters: ["Task 1 C1/T1 (ms)", "Task 2 C2/T2 (ms)", "Task 3 C3/T3 (ms)"],
        sampleValues: { C1: 5, T1: 25, C2: 10, T2: 50, C3: 15, T3: 100 },
        expectedResult: "Total U = 55.0% <= Bound 77.98% -> GUARANTEED SCHEDULABLE"
      }
    }
  ]
};

/**
 * Retrieve projects for a specific course.
 */
export function getProjectsByCourse(courseCode: string): CourseProject[] {
  return COURSE_PROJECTS_CATALOG[courseCode] || [];
}

/**
 * Retrieve practical checklist for a specific course.
 */
export function getPracticalsByCourse(courseCode: string): PracticalExperiment[] {
  return COURSE_PRACTICALS_CHECKLIST[courseCode] || [];
}
