/**
 * ========================================================================================
 * VoltCore Apex Academia - Unit-Wise Quizzes, Assessments & Problem Banks
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead & Systems Architect: Ashok Kumar A
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 *
 * Provides curated academic assessments:
 *   - Unit-wise multiple-choice questions (MCQs) with instant evaluation
 *   - Part A 2-mark conceptual questions with formal model answers
 *   - Part B 16-mark numerical/derivation problem banks with step-by-step solutions
 *   - Integrated KaTeX formulas and common pitfall warnings for deep learning
 * ========================================================================================
 */

export interface QuizQuestion {
  id: string;
  courseCode: string;
  unitNumber: number;
  unitRoman: "I" | "II" | "III" | "IV" | "V";
  type: "MCQ" | "PART_A" | "PART_B";
  bloomLevel: "L1 (Remember)" | "L2 (Understand)" | "L3 (Apply)" | "L4 (Analyze)" | "L5 (Evaluate)";
  questionText: string;
  options?: string[]; // For MCQs
  correctOptionIndex?: number; // 0 to 3
  marks: number; // 1, 2, or 16
  solutionSummary: string;
  stepByStepExplanation: string[];
  keyFormulas: string[];
  examYearReference: string;
  commonPitfall: string;
}

export const COURSE_ASSESSMENT_BANK: Record<string, QuizQuestion[]> = {
  // ===========================================================================
  // COURSE 1: EC23S01 - Numerical and Signal Processing Practice Through Python
  // ===========================================================================
  "EC23S01": [
    // Unit I: MCQ
    {
      id: "EC23S01_Q1",
      courseCode: "EC23S01",
      unitNumber: 1,
      unitRoman: "I",
      type: "MCQ",
      bloomLevel: "L3 (Apply)",
      questionText: "An input sequence x[n] has length N1 = 32 and an LTI filter impulse response h[n] has length N2 = 16. What is the minimum zero-padding DFT size N_FFT required to compute their linear convolution without time-domain aliasing?",
      options: [
        "N_FFT = 32",
        "N_FFT = 47",
        "N_FFT = 48 (or power-of-2 length 64)",
        "N_FFT = 512"
      ],
      correctOptionIndex: 2,
      marks: 1,
      solutionSummary: "The duration of linear convolution is L = N1 + N2 - 1 = 32 + 16 - 1 = 47. Therefore, the minimum DFT length is 47, which in practical power-of-2 radix-2 FFT implementations is zero-padded to 64.",
      stepByStepExplanation: [
        "1. Identify input lengths: N1 = 32, N2 = 16.",
        "2. Compute duration of discrete linear convolution: L = N1 + N2 - 1 = 32 + 16 - 1 = 47 samples.",
        "3. Circular convolution via DFT will wrap around if N_FFT < L.",
        "4. Therefore, minimum condition is N_FFT >= 47. Next standard power-of-2 for radix-2 FFT is 64."
      ],
      keyFormulas: ["L = N_1 + N_2 - 1", "N_{FFT} \\ge N_1 + N_2 - 1"],
      examYearReference: "Anna University Nov/Dec 2023 (EC3452)",
      commonPitfall: "Students often forget to subtract 1, mistakenly computing N1 + N2 = 48, or confuse linear convolution length with direct circular length max(N1, N2)."
    },

    // Unit I: Part A
    {
      id: "EC23S01_Q2",
      courseCode: "EC23S01",
      unitNumber: 1,
      unitRoman: "I",
      type: "PART_A",
      bloomLevel: "L2 (Understand)",
      questionText: "State the Nyquist-Shannon Sampling Theorem and define aliasing distortion in discrete-time signal processing.",
      marks: 2,
      solutionSummary: "To reconstruct a continuous-time bandlimited signal with maximum frequency f_max uniquely from its discrete samples, the sampling frequency f_s must satisfy f_s >= 2 * f_max. If f_s < 2 * f_max, spectral overlap (aliasing) occurs where high frequencies fold into the primary Nyquist interval [0, f_s/2].",
      stepByStepExplanation: [
        "1. Bandlimited criterion: Continuous spectrum X(f) = 0 for |f| > f_max.",
        "2. Sampling rate condition: f_s >= 2 * f_max (Nyquist rate = 2 * f_max).",
        "3. Consequence of violation: High-frequency components fold back as f_alias = |f - k * f_s|, causing irreversible waveform distortion."
      ],
      keyFormulas: ["f_s \\ge 2 f_{\\max}", "f_{alias} = |f - k f_s|"],
      examYearReference: "Anna University Regulation 2023 Standard",
      commonPitfall: "Omitting the 'bandlimited' precondition or confusing the Nyquist rate (2 * f_max) with the Nyquist frequency (f_s / 2)."
    },

    // Unit II: MCQ
    {
      id: "EC23S01_Q3",
      courseCode: "EC23S01",
      unitNumber: 2,
      unitRoman: "II",
      type: "MCQ",
      bloomLevel: "L4 (Analyze)",
      questionText: "How many complex multiplications are required to compute a 1024-point DFT directly versus using the Radix-2 Cooley-Tukey Decimation-in-Time (DIT) FFT algorithm?",
      options: [
        "Direct: 1024, FFT: 10",
        "Direct: 1,048,576, FFT: 5,120 (~204x speedup)",
        "Direct: 2,048, FFT: 512",
        "Direct: 524,288, FFT: 10,240"
      ],
      correctOptionIndex: 1,
      marks: 1,
      solutionSummary: "Direct DFT requires N^2 = 1024^2 = 1,048,576 complex multiplications. Radix-2 DIT-FFT requires (N/2) * log2(N) = (1024 / 2) * 10 = 5,120 complex multiplications.",
      stepByStepExplanation: [
        "1. Direct DFT complexity formula: N^2 complex multiplications.",
        "2. Substitute N = 1024: 1024^2 = 1,048,576 ops.",
        "3. Radix-2 FFT complexity: (N/2) * log2(N) complex multiplications across log2(N) butterfly stages.",
        "4. Substitute N = 1024: (1024/2) * 10 = 512 * 10 = 5,120 ops.",
        "5. Computational speedup: 1,048,576 / 5,120 ≈ 204.8x."
      ],
      keyFormulas: ["\\text{Direct Ops} = N^2", "\\text{FFT Ops} = \\frac{N}{2} \\log_2 N"],
      examYearReference: "GATE ECE 2022 / Anna University",
      commonPitfall: "Confusing complex multiplications with complex additions (which are N * log2 N = 10,240)."
    },

    // Unit III: Part B Numerical
    {
      id: "EC23S01_Q4",
      courseCode: "EC23S01",
      unitNumber: 3,
      unitRoman: "III",
      type: "PART_B",
      bloomLevel: "L5 (Evaluate)",
      questionText: "Design a digital Butterworth lowpass filter using Bilinear Transformation with T = 1 sec. Specifications: 3-dB cutoff frequency omega_c = 0.2 pi rad/sample, order N = 2. Find the discrete transfer function H(z).",
      marks: 16,
      solutionSummary: "By frequency pre-warping, Omega_c = (2/T)*tan(omega_c/2) = 2*tan(0.1*pi) = 0.6498 rad/s. Normalized 2nd-order analog Butterworth prototype H_a(s) = Omega_c^2 / (s^2 + sqrt(2)*Omega_c*s + Omega_c^2). Substituting s = 2*(1 - z^-1)/(1 + z^-1) yields the digital filter H(z).",
      stepByStepExplanation: [
        "Step 1 (Pre-warping): Omega_c = (2/T) * tan(omega_c / 2) = 2 * tan(0.1 * pi) = 2 * 0.3249 = 0.6498 rad/s.",
        "Step 2 (Analog Prototype): H_a(s) = Omega_c^2 / (s^2 + sqrt(2)*Omega_c*s + Omega_c^2) = 0.4222 / (s^2 + 0.9190*s + 0.4222).",
        "Step 3 (Bilinear Substitution): Substitute s = 2 * (1 - z^-1) / (1 + z^-1).",
        "Step 4 (Denominator expansion): Denominator becomes [4*(1 - z^-1)^2 + 1.838*(1 - z^-2) + 0.4222*(1 + z^-1)^2] / (1 + z^-1)^2.",
        "Step 5 (Algebraic Simplification): H(z) = 0.0674 * (1 + 2*z^-1 + z^-2) / (1 - 1.143*z^-1 + 0.4128*z^-2)."
      ],
      keyFormulas: [
        "\\Omega = \\frac{2}{T} \\tan\\left(\\frac{\\omega}{2}\\right)",
        "s = \\frac{2}{T} \\left( \\frac{1 - z^{-1}}{1 + z^{-1}} \\right)",
        "H_a(s) = \\frac{\\Omega_c^2}{s^2 + \\sqrt{2}\\Omega_c s + \\Omega_c^2}"
      ],
      examYearReference: "Anna University Apr/May 2023 (Part B 16-Marks)",
      commonPitfall: "Neglecting the frequency pre-warping step and substituting omega directly into the analog prototype, causing severe passband edge distortion."
    },

    // Unit V: MCQ
    {
      id: "EC23S01_Q5",
      courseCode: "EC23S01",
      unitNumber: 5,
      unitRoman: "V",
      type: "MCQ",
      bloomLevel: "L4 (Analyze)",
      questionText: "In the Widrow-Hoff LMS adaptive algorithm, what is the theoretical upper bound on the adaptation step size mu to guarantee convergence of the weight vector mean?",
      options: [
        "mu < 1.0",
        "0 < mu < 1 / lambda_max",
        "mu > 2 * P_x",
        "mu = infinity"
      ],
      correctOptionIndex: 1,
      marks: 1,
      solutionSummary: "The LMS algorithm converges in the mean if and only if 0 < mu < 1 / lambda_max, where lambda_max is the maximum eigenvalue of the input signal correlation matrix R.",
      stepByStepExplanation: [
        "1. Write weight error update: v[n+1] = (I - 2*mu*R) * v[n].",
        "2. For asymptotic stability, all eigenvalues |1 - 2*mu*lambda_i| < 1.",
        "3. This yields: -1 < 1 - 2*mu*lambda_max < 1 => 2*mu*lambda_max < 2 => mu < 1 / lambda_max.",
        "4. Since trace(R) = sum(lambda_i) > lambda_max, a conservative practical bound is mu < 1 / trace(R) = 1 / (M * P_x)."
      ],
      keyFormulas: ["0 < \\mu < \\frac{1}{\\lambda_{\\max}}", "\\text{tr}(\\mathbf{R}) = M \\cdot P_x"],
      examYearReference: "GATE ECE 2021",
      commonPitfall: "Selecting mu > 1 or assuming step size can be arbitrarily chosen without regard to input signal power."
    }
  ],

  // ===========================================================================
  // COURSE 2: EC23C03 - Electronic Devices
  // ===========================================================================
  "EC23C03": [
    // Unit I: Part A
    {
      id: "EC23C03_Q1",
      courseCode: "EC23C03",
      unitNumber: 1,
      unitRoman: "I",
      type: "PART_A",
      bloomLevel: "L2 (Understand)",
      questionText: "State the Mass Action Law for semiconductors in thermal equilibrium and calculate the hole concentration in silicon doped with Nd = 10^17 cm^-3 donor atoms at 300 K.",
      marks: 2,
      solutionSummary: "The Mass Action Law states that in thermal equilibrium, the product of electron and hole concentrations is constant at a given temperature: n0 * p0 = ni^2. For n-type silicon with Nd = 10^17 cm^-3, n0 ≈ Nd = 10^17 cm^-3. Thus, p0 = ni^2 / Nd = (1.5 * 10^10)^2 / 10^17 = 2.25 * 10^3 cm^-3.",
      stepByStepExplanation: [
        "1. Mass action law formula: n0 * p0 = ni^2.",
        "2. At T = 300 K for silicon: ni = 1.5 * 10^10 cm^-3.",
        "3. Complete ionization assumption: n0 ≈ Nd = 10^17 cm^-3.",
        "4. Calculate minority hole concentration: p0 = (2.25 * 10^20) / 10^17 = 2.25 * 10^3 cm^-3."
      ],
      keyFormulas: ["n_0 p_0 = n_i^2", "p_0 = \\frac{n_i^2}{N_d}"],
      examYearReference: "Anna University Nov/Dec 2022",
      commonPitfall: "Forgetting to square ni, arriving at 1.5*10^10 / 10^17 = 1.5*10^-7, which is physically impossible."
    },

    // Unit II: MCQ
    {
      id: "EC23C03_Q2",
      courseCode: "EC23C03",
      unitNumber: 2,
      unitRoman: "II",
      type: "MCQ",
      bloomLevel: "L3 (Apply)",
      questionText: "A silicon PN junction diode conducts a forward DC current of ID = 2.6 mA at room temperature (VT = 26 mV, ideality factor eta = 1). What is its small-signal dynamic resistance rd?",
      options: [
        "rd = 10.0 Ohms",
        "rd = 260 Ohms",
        "rd = 1000 Ohms",
        "rd = 0.1 Ohms"
      ],
      correctOptionIndex: 0,
      marks: 1,
      solutionSummary: "Small-signal dynamic resistance rd = eta * VT / ID = (1 * 26 mV) / (2.6 mA) = 10.0 Ohms.",
      stepByStepExplanation: [
        "1. Shockley equation derivative: dID / dVD = ID / (eta * VT).",
        "2. Invert to get dynamic resistance: rd = (eta * VT) / ID.",
        "3. Substitute values: eta = 1, VT = 0.026 V, ID = 0.0026 A.",
        "4. rd = 0.026 / 0.0026 = 10.0 Ohms."
      ],
      keyFormulas: ["r_d = \\frac{\\eta V_T}{I_D}"],
      examYearReference: "GATE ECE 2023",
      commonPitfall: "Confusing dynamic AC resistance rd = VT / ID with static DC resistance R_DC = VD / ID."
    },

    // Unit III: MCQ
    {
      id: "EC23C03_Q3",
      courseCode: "EC23C03",
      unitNumber: 3,
      unitRoman: "III",
      type: "MCQ",
      bloomLevel: "L4 (Analyze)",
      questionText: "In a forward-active BJT, the Early Effect (base-width modulation) causes which of the following output characteristics?",
      options: [
        "Collector current IC becomes completely independent of VCE",
        "Collector current IC increases with increasing VCE, giving finite output resistance ro ≈ VA / IC",
        "Base current increases rapidly to equal collector current",
        "Current gain beta drops to zero"
      ],
      correctOptionIndex: 1,
      marks: 1,
      solutionSummary: "As VCE increases, the collector-base reverse bias widens the CBJ depletion layer, narrowing the neutral base width WB. Less recombination occurs in the base, causing IC to increase slightly with VCE, represented by finite output resistance ro ≈ VA / IC.",
      stepByStepExplanation: [
        "1. Increasing VCE increases reverse voltage across CBJ (VCB = VCE - VBE).",
        "2. Wider CBJ depletion layer narrows effective neutral base width W_B.",
        "3. Shorter base width increases carrier concentration gradient and reduces recombination.",
        "4. Result: IC increases with slope 1/ro = IC / (VA + VCE)."
      ],
      keyFormulas: ["I_C = I_S e^{V_{BE}/V_T} \\left(1 + \\frac{V_{CE}}{V_A}\\right)", "r_o \\approx \\frac{V_A}{I_C}"],
      examYearReference: "Anna University Regulation 2023 Benchmark",
      commonPitfall: "Assuming ideal horizontal flat curves in active mode where ro is infinite."
    },

    // Unit IV: Part B
    {
      id: "EC23C03_Q4",
      courseCode: "EC23C03",
      unitNumber: 4,
      unitRoman: "IV",
      type: "PART_B",
      bloomLevel: "L5 (Evaluate)",
      questionText: "An n-channel MOSFET has threshold voltage VTH = 0.7 V, mu_n * Cox = 200 uA/V^2, aspect ratio W/L = 10, and channel length modulation parameter lambda = 0.02 V^-1. If VGS = 1.7 V and VDS = 2.5 V, calculate the drain current ID and small-signal output resistance ro.",
      marks: 16,
      solutionSummary: "Since VGS - VTH = 1.7 - 0.7 = 1.0 V and VDS = 2.5 V > 1.0 V, the transistor operates in pinch-off saturation. ID = 0.5 * mu_n*Cox * (W/L) * (VGS - VTH)^2 * (1 + lambda*VDS) = 0.5 * 200e-6 * 10 * (1.0)^2 * (1 + 0.02*2.5) = 1.05 mA. Small signal ro ≈ 1 / (lambda * ID0) ≈ 50 kOhms.",
      stepByStepExplanation: [
        "Step 1 (Check Operating Mode): Overdrive Vov = VGS - VTH = 1.7 - 0.7 = 1.0 V. VDS = 2.5 V > Vov => SATURATION.",
        "Step 2 (Ideal Saturation Current ID0): ID0 = 0.5 * (mu_n*Cox) * (W/L) * (Vov)^2 = 0.5 * (200e-6) * 10 * 1.0^2 = 1.0 mA.",
        "Step 3 (Channel Length Modulation Factor): 1 + lambda * VDS = 1 + 0.02 * 2.5 = 1.05.",
        "Step 4 (Actual Saturation Current): ID = 1.0 mA * 1.05 = 1.05 mA.",
        "Step 5 (Output Resistance ro): ro = 1 / (lambda * ID0) = 1 / (0.02 * 1.0e-3) = 50,000 Ohms = 50 kOhms."
      ],
      keyFormulas: [
        "I_D = \\frac{1}{2} \\mu_n C_{ox} \\frac{W}{L} (V_{GS} - V_{TH})^2 (1 + \\lambda V_{DS})",
        "r_o = \\frac{1}{\\lambda I_{D0}}"
      ],
      examYearReference: "Anna University Apr/May 2023 (Part B 16-Marks)",
      commonPitfall: "Evaluating using triode equation instead of saturation, or applying lambda factor to VDS^2."
    }
  ],

  // ===========================================================================
  // COURSE 3: EC23E04 - Optics and Lasers
  // ===========================================================================
  "EC23E04": [
    // Unit I: Part A
    {
      id: "EC23E04_Q1",
      courseCode: "EC23E04",
      unitNumber: 1,
      unitRoman: "I",
      type: "PART_A",
      bloomLevel: "L3 (Apply)",
      questionText: "Calculate the coherence length Lc of a red He-Ne laser emitting at lambda0 = 632.8 nm with a spectral linewidth delta-lambda = 10^-5 nm.",
      marks: 2,
      solutionSummary: "Coherence length Lc = lambda0^2 / delta-lambda = (632.8 * 10^-9 m)^2 / (10^-14 m) = 40.04 meters.",
      stepByStepExplanation: [
        "1. Convert wavelengths to meters: lambda0 = 632.8 * 10^-9 m, delta-lambda = 10^-5 nm = 10^-14 m.",
        "2. Coherence length equation: Lc = c * tau_c = lambda0^2 / delta-lambda.",
        "3. Compute numerator: (632.8 * 10^-9)^2 = 4.004 * 10^-13 m^2.",
        "4. Divide by linewidth: (4.004 * 10^-13) / (10^-14) = 40.04 meters."
      ],
      keyFormulas: ["L_c = \\frac{\\lambda_0^2}{\\Delta \\lambda} = \\frac{c}{\\Delta \\nu}"],
      examYearReference: "Anna University Nov/Dec 2023",
      commonPitfall: "Units conversion mistake: failing to convert delta-lambda from nm (10^-9) to meters (10^-14)."
    },

    // Unit III: MCQ
    {
      id: "EC23E04_Q2",
      courseCode: "EC23E04",
      unitNumber: 3,
      unitRoman: "III",
      type: "MCQ",
      bloomLevel: "L4 (Analyze)",
      questionText: "An optical laser resonator has cavity length L = 50 cm. Mirror 1 has radius of curvature R1 = 100 cm and Mirror 2 has R2 = 80 cm. What are the g-parameters and is this cavity geometrically stable?",
      options: [
        "g1 = 0.5, g2 = 0.375, Product = 0.1875 (STABLE)",
        "g1 = -0.5, g2 = 1.25, Product = -0.625 (UNSTABLE)",
        "g1 = 1.0, g2 = 1.0, Product = 1.0 (MARGINAL)",
        "g1 = 0, g2 = 0, Product = 0 (CONFOCAL)"
      ],
      correctOptionIndex: 0,
      marks: 1,
      solutionSummary: "g1 = 1 - L/R1 = 1 - 50/100 = 0.5. g2 = 1 - L/R2 = 1 - 50/80 = 1 - 0.625 = 0.375. The product g1 * g2 = 0.5 * 0.375 = 0.1875. Since 0 <= 0.1875 <= 1, the cavity is STABLE.",
      stepByStepExplanation: [
        "1. Resonator g-parameter definition: g1 = 1 - L/R1, g2 = 1 - L/R2.",
        "2. Substitute L = 50 cm, R1 = 100 cm: g1 = 1 - 0.5 = 0.5.",
        "3. Substitute L = 50 cm, R2 = 80 cm: g2 = 1 - 0.625 = 0.375.",
        "4. Stability product: g1 * g2 = 0.5 * 0.375 = 0.1875.",
        "5. Sylvester stability test: 0 <= g1*g2 <= 1 is satisfied => Confined stable modes."
      ],
      keyFormulas: ["g_1 = 1 - \\frac{L}{R_1}", "g_2 = 1 - \\frac{L}{R_2}", "0 \\le g_1 g_2 \\le 1"],
      examYearReference: "Anna University Apr/May 2023",
      commonPitfall: "Mixing up L/R with R/L in the g-parameter definition."
    },

    // Unit III: Part B
    {
      id: "EC23E04_Q3",
      courseCode: "EC23E04",
      unitNumber: 3,
      unitRoman: "III",
      type: "PART_B",
      bloomLevel: "L5 (Evaluate)",
      questionText: "Derive the longitudinal mode frequency spacing for a Fabry-Perot laser cavity of physical length L with intracavity medium of refractive index n. For a He-Ne laser with L = 30 cm and n = 1.0, find the mode separation in MHz.",
      marks: 16,
      solutionSummary: "Longitudinal standing wave condition is 2*n*L = q*lambda = q*(c/nu), yielding modal frequencies nu_q = q*(c / 2nL). The frequency separation between adjacent modes is delta-nu = c / (2nL). For L = 0.3 m and n = 1.0: delta-nu = (3 * 10^8) / (2 * 1.0 * 0.3) = 500 MHz.",
      stepByStepExplanation: [
        "Step 1 (Resonance Condition): An integral number q of optical half-wavelengths must fit into the cavity round-trip: 2 * n * L = q * lambda.",
        "Step 2 (Frequency Relation): Since c = nu * lambda, lambda = c / nu. Thus 2 * n * L = q * (c / nu).",
        "Step 3 (Solve for Frequency): nu_q = q * c / (2 * n * L).",
        "Step 4 (Adjacent Mode Separation): delta-nu = nu_{q+1} - nu_q = c / (2 * n * L).",
        "Step 5 (Numerical Calculation): delta-nu = (3 * 10^8 m/s) / (2 * 1.0 * 0.3 m) = 3 * 10^8 / 0.6 = 5 * 10^8 Hz = 500 MHz."
      ],
      keyFormulas: ["2 n L = q \\lambda", "\\Delta \\nu = \\frac{c}{2 n L}"],
      examYearReference: "Anna University Nov/Dec 2022 (Part B 16-Marks)",
      commonPitfall: "Omitting the factor of 2 in the denominator, getting 1000 MHz instead of 500 MHz."
    }
  ],

  // ===========================================================================
  // COURSE 4: EC8702 - Embedded Systems
  // ===========================================================================
  "EC8702": [
    // Unit I: MCQ
    {
      id: "EC8702_Q1",
      courseCode: "EC8702",
      unitNumber: 1,
      unitRoman: "I",
      type: "MCQ",
      bloomLevel: "L3 (Apply)",
      questionText: "In ARM Cortex-M microcontrollers, what is the exact hardware latency required by the NVIC to execute tail-chaining between two pending interrupt service routines?",
      options: [
        "12 clock cycles",
        "6 clock cycles",
        "32 clock cycles",
        "0 clock cycles (instantaneous)"
      ],
      correctOptionIndex: 1,
      marks: 1,
      solutionSummary: "Tail-chaining allows the NVIC to skip restoring the 8 CPU registers and immediately vectors to the next pending ISR in just 6 clock cycles, compared to 12 cycles for full context pop and 12 cycles for push.",
      stepByStepExplanation: [
        "1. Standard interrupt entry stacks 8 registers: R0-R3, R12, LR, PC, xPSR (12 cycles).",
        "2. Standard interrupt return unstacks those 8 registers (12 cycles).",
        "3. Tail-chaining optimization: If an interrupt is pending upon exit of current ISR, NVIC skips unstacking.",
        "4. The processor re-fetches the next vector and vectors into the new ISR in exactly 6 clock cycles."
      ],
      keyFormulas: ["T_{tail\\text{-}chain} = 6 \\text{ cycles}", "T_{stack} = 12 \\text{ cycles}"],
      examYearReference: "Anna University Nov/Dec 2023",
      commonPitfall: "Confusing tail-chaining latency (6 cycles) with full context entry stacking latency (12 cycles)."
    },

    // Unit II: Part A
    {
      id: "EC8702_Q2",
      courseCode: "EC8702",
      unitNumber: 2,
      unitRoman: "II",
      type: "PART_A",
      bloomLevel: "L3 (Apply)",
      questionText: "In ARM Cortex-M4, calculate the bit-band alias address for bit 3 of SRAM byte address 0x20000004 (SRAM Bit-Band Alias Base = 0x22000000).",
      marks: 2,
      solutionSummary: "AliasAddress = AliasBase + (ByteOffset * 32) + (BitNumber * 4). Here ByteOffset = 0x20000004 - 0x20000000 = 0x04 (4 in decimal). AliasAddress = 0x22000000 + (4 * 32) + (3 * 4) = 0x22000000 + 128 + 12 = 0x22000000 + 140 (0x8C) = 0x2200008C.",
      stepByStepExplanation: [
        "1. Identify SRAM bit-band alias base: 0x22000000.",
        "2. Calculate byte offset from 0x20000000: 0x20000004 - 0x20000000 = 0x04 (4 bytes).",
        "3. Multiply byte offset by 32: 4 * 32 = 128 (0x80).",
        "4. Multiply target bit position by 4: 3 * 4 = 12 (0x0C).",
        "5. Sum terms: 0x22000000 + 0x80 + 0x0C = 0x2200008C."
      ],
      keyFormulas: ["\\text{AliasAddr} = \\text{Base} + (\\text{Offset} \\times 32) + (\\text{Bit} \\times 4)"],
      examYearReference: "Anna University Apr/May 2023",
      commonPitfall: "Multiplying byte offset by 4 and bit by 32 (reversing coefficients), leading to wrong memory address."
    },

    // Unit IV: Part B
    {
      id: "EC8702_Q3",
      courseCode: "EC8702",
      unitNumber: 4,
      unitRoman: "IV",
      type: "PART_B",
      bloomLevel: "L5 (Evaluate)",
      questionText: "A dual-task FreeRTOS embedded IoT node runs Task 1 (sensor acquisition, execution time C1 = 15 ms, period T1 = 50 ms) and Task 2 (MQTT telemetry, execution time C2 = 25 ms, period T2 = 80 ms). Using Liu & Layland Rate Monotonic Scheduling analysis, determine if this task set is guaranteed to meet all deadlines.",
      marks: 16,
      solutionSummary: "Task 1 utilization U1 = 15/50 = 0.30 (30%). Task 2 utilization U2 = 25/80 = 0.3125 (31.25%). Total CPU utilization U = U1 + U2 = 61.25%. Liu & Layland bound for n = 2 tasks is U_bound = 2 * (2^(1/2) - 1) = 2 * (1.4142 - 1) = 82.84%. Since U = 61.25% <= 82.84%, the task set is 100% schedulable without deadline misses.",
      stepByStepExplanation: [
        "Step 1 (Assign RMS Priorities): T1 = 50 ms < T2 = 80 ms => Task 1 has higher priority than Task 2.",
        "Step 2 (Compute Task 1 Utilization): U1 = C1 / T1 = 15 / 50 = 0.300 (30.0%).",
        "Step 3 (Compute Task 2 Utilization): U2 = C2 / T2 = 25 / 80 = 0.3125 (31.25%).",
        "Step 4 (Total Processor Utilization): U = U1 + U2 = 0.300 + 0.3125 = 0.6125 (61.25%).",
        "Step 5 (Compute Theoretical RMS Bound for n=2): U_bound = n * (2^(1/n) - 1) = 2 * (sqrt(2) - 1) = 2 * 0.41421 = 0.82842 (82.84%).",
        "Step 6 (Schedulability Conclusion): Since U = 61.25% <= 82.84%, the sufficient condition is met; all tasks are strictly schedulable."
      ],
      keyFormulas: [
        "U = \\sum_{i=1}^n \\frac{C_i}{T_i}",
        "U_{\\text{bound}} = n \\left( 2^{1/n} - 1 \\right)"
      ],
      examYearReference: "Anna University Nov/Dec 2023 (Part B 16-Marks)",
      commonPitfall: "Assuming tasks are schedulable just because U < 100%, without checking the 82.84% Liu & Layland bound for static priorities."
    }
  ]
};

/**
 * Fetch all questions for a course
 */
export function getQuestionsByCourse(courseCode: string): QuizQuestion[] {
  const normalized = courseCode.toUpperCase().trim();
  return COURSE_ASSESSMENT_BANK[normalized] || [];
}

/**
 * Fetch questions filtered by course and unit
 */
export function getQuestionsByUnit(courseCode: string, unitNumber: number): QuizQuestion[] {
  const courseQuestions = getQuestionsByCourse(courseCode);
  return courseQuestions.filter(q => q.unitNumber === unitNumber);
}

/**
 * Fetch questions filtered by type (MCQ, PART_A, PART_B)
 */
export function getQuestionsByType(courseCode: string, type: "MCQ" | "PART_A" | "PART_B"): QuizQuestion[] {
  const courseQuestions = getQuestionsByCourse(courseCode);
  return courseQuestions.filter(q => q.type === type);
}
