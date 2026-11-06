/**
 * ========================================================================================
 * VoltCore Apex Academia - Unit-Wise Lesson Libraries & Markdown Lecture Notes
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead & Systems Architect: Ashok Kumar A
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 *
 * Provides curated academic lessons, rich markdown lecture notes, KaTeX formula models,
 * and laboratory simulator hooks for all 4 priority courses:
 *   1. EC23S01: Numerical and Signal Processing Practice Through Python
 *   2. EC23C03: Electronic Devices
 *   3. EC23E04: Optics and Lasers
 *   4. EC8702:  Embedded Systems
 * ========================================================================================
 */

export interface KatexFormula {
  id: string;
  name: string;
  latex: string;
  renderedHtmlPreview?: string;
  description: string;
  variables: Record<string, string>;
  examSignificance: "High (Part B 16-Mark Derivation)" | "Medium (Part B 8-Mark Problem)" | "Essential (Part A 2-Mark Question)";
}

export interface Lesson {
  id: string; // e.g. "EC23S01_U1_L1"
  courseCode: string; // "EC23S01", "EC23C03", "EC23E04", "EC8702"
  unitNumber: number; // 1 to 5
  unitRoman: "I" | "II" | "III" | "IV" | "V";
  lessonNumber: number;
  title: string;
  shortTitle: string;
  estimatedMinutes: number;
  difficulty: "Foundational" | "Intermediate" | "Advanced" | "GATE ECE Level";
  summary: string;
  learningObjectives: string[];
  markdownNotes: string;
  formulas: KatexFormula[];
  simulationBridge?: {
    experimentName: string;
    tool: string;
    actionDescription: string;
  };
}

export const COURSE_LESSONS_REGISTRY: Record<string, Lesson[]> = {
  // ===========================================================================
  // COURSE 1: EC23S01 - Numerical and Signal Processing Practice Through Python
  // ===========================================================================
  "EC23S01": [
    // Unit I: Lesson 1
    {
      id: "EC23S01_U1_L1",
      courseCode: "EC23S01",
      unitNumber: 1,
      unitRoman: "I",
      lessonNumber: 1,
      title: "Vectorized Discrete-Time Convolution & Zero-Padding Equivalence",
      shortTitle: "Discrete Convolution in Python",
      estimatedMinutes: 45,
      difficulty: "Foundational",
      summary: "Mathematical formulation of discrete linear convolution, Cauchy product interpretation, boundary effect mitigation, and the circular convolution zero-padding theorem.",
      learningObjectives: [
        "Formulate linear convolution sum for finite-duration causal sequences",
        "Derive the minimum zero-padding length L >= N1 + N2 - 1 for circular equivalence",
        "Implement vectorized numpy.convolve with valid, same, and full boundary modes"
      ],
      markdownNotes: `### 1. Mathematical Foundations of Discrete Convolution
Discrete linear convolution is the cornerstone operator for Linear Time-Invariant (LTI) systems. For an input sequence $x[n]$ of length $N_1$ and impulse response $h[n]$ of length $N_2$, the output $y[n]$ is defined by the convolution sum:

$$y[n] = x[n] * h[n] = \\sum_{k=-\\infty}^{\\infty} x[k] h[n-k]$$

#### Computational Steps in Discrete Time:
1. **Time Reversal (Folding):** Replace $k$ with $-k$ to form $h[-k]$.
2. **Time Shifting:** Shift the folded sequence by $n$ steps to obtain $h[n-k]$.
3. **Pointwise Multiplication:** Compute the product sequence $v_n[k] = x[k] \\cdot h[n-k]$.
4. **Summation:** Accumulate all non-zero terms across index $k$.

### 2. Output Duration & Boundary Invariant
For causal sequences where $x[n] \\neq 0$ for $0 \\le n \\le N_1 - 1$ and $h[n] \\neq 0$ for $0 \\le n \\le N_2 - 1$, the convolution result $y[n]$ has a finite support length $L$:

$$L = N_1 + N_2 - 1$$

In Python NumPy, \`np.convolve(x, h, mode='full')\` computes all $L$ samples, while \`mode='same'\` returns the central $N_1$ samples.

### 3. Circular vs Linear Convolution Equivalence
Direct frequency-domain multiplication using DFT yields circular convolution:
$$y_{circ}[n] = x[n] \\circledast h[n] = \\text{IDFT}\\{ X[k] \\cdot H[k] \\}$$

To prevent time-domain aliasing (circular wrap-around), both sequences must be zero-padded to length:
$$N_{FFT} \\ge N_1 + N_2 - 1$$
`,
      formulas: [
        {
          id: "FORM_CONV_DISCRETE",
          name: "Linear Convolution Sum",
          latex: "y[n] = \\sum_{k=-\\infty}^{\\infty} x[k] h[n - k]",
          description: "Discrete-time convolution sum characterizing an LTI system's response to an arbitrary input signal.",
          variables: {
            "y[n]": "Output discrete-time response signal",
            "x[k]": "Input excitation sequence at sample index k",
            "h[n-k]": "Time-reversed and shifted unit impulse response"
          },
          examSignificance: "High (Part B 16-Mark Derivation)"
        },
        {
          id: "FORM_ZERO_PAD_BOUND",
          name: "Zero-Padding Circular Equivalence Bound",
          latex: "N_{FFT} \\ge N_1 + N_2 - 1",
          description: "Minimum DFT size required to guarantee that circular convolution matches linear convolution exactly.",
          variables: {
            "N_FFT": "Fast Fourier Transform length",
            "N_1": "Length of input sequence x[n]",
            "N_2": "Length of impulse response h[n]"
          },
          examSignificance: "Essential (Part A 2-Mark Question)"
        }
      ],
      simulationBridge: {
        experimentName: "Discrete Convolution Workbench",
        tool: "Python SciPy",
        actionDescription: "Compute full, same, and circular convolution with real-time waveform visualizer."
      }
    },

    // Unit II: Lesson 2
    {
      id: "EC23S01_U2_L1",
      courseCode: "EC23S01",
      unitNumber: 2,
      unitRoman: "II",
      lessonNumber: 1,
      title: "Radix-2 Decimation-in-Time Cooley-Tukey FFT & Twiddle Factors",
      shortTitle: "DIT-FFT Butterfly Networks",
      estimatedMinutes: 50,
      difficulty: "Intermediate",
      summary: "Decomposition of N-point DFT into even and odd decimated sub-sequences, bit-reversal sorting index computation, and twiddle factor symmetry properties.",
      learningObjectives: [
        "Decompose N-point DFT into two N/2-point DFTs",
        "Exploit periodicity and symmetry of twiddle factor W_N^k",
        "Trace the butterfly computation network and calculate complexity reduction from O(N^2) to O(N log2 N)"
      ],
      markdownNotes: `### 1. The Radix-2 DIT-FFT Formulation
The $N$-point Discrete Fourier Transform (DFT) is given by:

$$X[k] = \\sum_{n=0}^{N-1} x[n] W_N^{kn}, \\quad W_N = e^{-j \\frac{2\\pi}{N}}$$

For $N = 2^m$, decimate $x[n]$ into even-indexed and odd-indexed samples:
$$X[k] = \\sum_{r=0}^{N/2-1} x[2r] W_N^{2rk} + W_N^k \\sum_{r=0}^{N/2-1} x[2r+1] W_N^{2rk}$$

Since $W_N^{2} = W_{N/2}$, we obtain:
$$X[k] = G[k] + W_N^k H[k]$$
$$X\\left[k + \\frac{N}{2}\\right] = G[k] - W_N^k H[k]$$

### 2. Twiddle Factor Invariant Properties
- **Symmetry Property:** $W_N^{k + N/2} = -W_N^k$
- **Periodicity Property:** $W_N^{k + N} = W_N^k$

### 3. Computational Advantage
- Direct DFT: $N^2$ complex multiplications and $N(N-1)$ complex additions.
- Cooley-Tukey FFT: $\\frac{N}{2} \\log_2 N$ complex multiplications.
- For $N = 1024$: Direct requires $1,048,576$ ops vs FFT requiring $5,120$ ops (~$200\\times$ speedup).
`,
      formulas: [
        {
          id: "FORM_FFT_BUTTERFLY",
          name: "Radix-2 Butterfly Computation",
          latex: "X[k] = G[k] + W_N^k H[k], \\quad X\\left[k + \\frac{N}{2}\\right] = G[k] - W_N^k H[k]",
          description: "Basic butterfly equation of Decimation-in-Time (DIT) Fast Fourier Transform algorithm.",
          variables: {
            "G[k]": "N/2-point DFT of even-indexed samples",
            "H[k]": "N/2-point DFT of odd-indexed samples",
            "W_N^k": "Twiddle factor phase rotator e^(-j 2pi k / N)"
          },
          examSignificance: "High (Part B 16-Mark Derivation)"
        }
      ],
      simulationBridge: {
        experimentName: "64-Point FFT Butterfly Analyzer",
        tool: "Python SciPy",
        actionDescription: "Inspect butterfly stage-by-stage bit-reversal array operations."
      }
    },

    // Unit III: Lesson 3
    {
      id: "EC23S01_U3_L1",
      courseCode: "EC23S01",
      unitNumber: 3,
      unitRoman: "III",
      lessonNumber: 1,
      title: "Bilinear Transformation & Frequency Pre-Warping for IIR Filters",
      shortTitle: "IIR Filter Bilinear Mapping",
      estimatedMinutes: 50,
      difficulty: "Advanced",
      summary: "Conformal mapping of analog Laplace s-plane to digital z-plane, trapezoidal integration substitution, and non-linear tangent frequency pre-warping.",
      learningObjectives: [
        "Map the imaginary j-Omega axis into the unit circle |z| = 1",
        "Derive the frequency pre-warping relationship Omega = (2/T) * tan(omega/2)",
        "Synthesize a stable Butterworth IIR digital filter with monotonic passband"
      ],
      markdownNotes: `### 1. Bilinear Transformation Mechanism
The Bilinear Transformation maps the analog $s$-plane into the digital $z$-plane using the trapezoidal integration approximation:

$$s = \\frac{2}{T} \\left( \\frac{1 - z^{-1}}{1 + z^{-1}} \\right) = \\frac{2}{T} \\left( \\frac{z - 1}{z + 1} \\right)$$

### 2. Frequency Warping Distortion
Substituting $s = j\\Omega$ and $z = e^{j\\omega}$:
$$j\\Omega = \\frac{2}{T} \\frac{e^{j\\omega} - 1}{e^{j\\omega} + 1} = \\frac{2}{T} \\frac{j \\sin(\\omega/2)}{\\cos(\\omega/2)} = j \\frac{2}{T} \\tan\\left(\\frac{\\omega}{2}\\right)$$

Thus, the analog frequency $\\Omega$ and digital frequency $\\omega$ are related non-linearly by:
$$\\Omega = \\frac{2}{T} \\tan\\left(\\frac{\\omega}{2}\\right) \\iff \\omega = 2 \\arctan\\left(\\frac{\\Omega T}{2}\\right)$$

### 3. Butterworth Filter Order Equation
To meet passband ripple $\\alpha_p$ at $\\Omega_p$ and stopband attenuation $\\alpha_s$ at $\\Omega_s$:
$$N \\ge \\frac{\\log_{10} \\left( \\frac{10^{0.1 \\alpha_s} - 1}{10^{0.1 \\alpha_p} - 1} \\right)}{2 \\log_{10} (\\Omega_s / \\Omega_p)}$$
`,
      formulas: [
        {
          id: "FORM_BILINEAR_WARPING",
          name: "Frequency Pre-Warping Relation",
          latex: "\\Omega = \\frac{2}{T} \\tan\\left( \\frac{\\omega}{2} \\right)",
          description: "Relates analog frequency Omega to discrete digital frequency omega to counter non-linear compression.",
          variables: {
            "\\Omega": "Analog continuous frequency (rad/sec)",
            "\\omega": "Digital normalized frequency (rad/sample)",
            "T": "Sampling period in seconds (1/fs)"
          },
          examSignificance: "High (Part B 16-Mark Derivation)"
        },
        {
          id: "FORM_BUTTERWORTH_MAG",
          name: "Butterworth Magnitude Response",
          latex: "|H(j\\Omega)| = \\frac{1}{\\sqrt{1 + \\left( \\frac{\\Omega}{\\Omega_c} \\right)^{2N}}}",
          description: "Maximally flat magnitude transfer characteristic in the passband.",
          variables: {
            "N": "Filter order",
            "\\Omega_c": "3-dB cutoff frequency"
          },
          examSignificance: "Medium (Part B 8-Mark Problem)"
        }
      ],
      simulationBridge: {
        experimentName: "Butterworth IIR Frequency Response Engine",
        tool: "Python SciPy",
        actionDescription: "Dynamically alter cutoff frequency and filter order to observe attenuation."
      }
    },

    // Unit IV: Lesson 4
    {
      id: "EC23S01_U4_L1",
      courseCode: "EC23S01",
      unitNumber: 4,
      unitRoman: "IV",
      lessonNumber: 1,
      title: "Linear-Phase FIR Filter Design via Windowing (Hamming & Kaiser)",
      shortTitle: "FIR Filter Windowing",
      estimatedMinutes: 45,
      difficulty: "Intermediate",
      summary: "Conditions for generalized linear phase, symmetric and antisymmetric impulse responses, Gibbs phenomenon, and spectral sidelobe roll-off comparison.",
      learningObjectives: [
        "Classify 4 types of linear phase FIR filters based on length and symmetry",
        "Explain truncation of ideal sinc impulse response and Gibbs phenomenon",
        "Select appropriate window function (Rectangular, Hamming, Blackman, Kaiser) for stopband specifications"
      ],
      markdownNotes: `### 1. Linear Phase Conditions
An FIR filter guarantees strictly linear phase if its impulse response $h[n]$ of length $M$ satisfies symmetry:
- **Symmetric:** $h[n] = h[M - 1 - n] \\implies$ Constant group delay $\\tau_g = (M - 1)/2$
- **Antisymmetric:** $h[n] = -h[M - 1 - n] \\implies 90^\\circ$ phase shift (Hilbert Transformers)

### 2. Windowing Formulation
The ideal lowpass filter impulse response is infinite in duration (non-causal):
$$h_d[n] = \\frac{\\sin(\\omega_c (n - \\alpha))}{\\pi (n - \\alpha)}, \\quad \\alpha = \\frac{M - 1}{2}$$

Multiplying with a finite window $w[n]$ yields the causal FIR filter:
$$h[n] = h_d[n] \\cdot w[n]$$

### 3. Hamming Window Formulation
$$w[n] = 0.54 - 0.46 \\cos\\left(\\frac{2\\pi n}{M - 1}\\right), \\quad 0 \\le n \\le M - 1$$
- Peak sidelobe attenuation: $-43\\text{ dB}$
- Mainlobe width: $8\\pi / M$
`,
      formulas: [
        {
          id: "FORM_HAMMING_WINDOW",
          name: "Hamming Window Function",
          latex: "w[n] = 0.54 - 0.46 \\cos\\left( \\frac{2\\pi n}{M - 1} \\right), \\quad 0 \\le n \\le M - 1",
          description: "Raised cosine window suppressing the first spectral sidelobe down to -43 dB.",
          variables: {
            "M": "Total filter length (number of taps)",
            "n": "Discrete sample index 0 <= n <= M-1"
          },
          examSignificance: "Essential (Part A 2-Mark Question)"
        }
      ]
    },

    // Unit V: Lesson 5
    {
      id: "EC23S01_U5_L1",
      courseCode: "EC23S01",
      unitNumber: 5,
      unitRoman: "V",
      lessonNumber: 1,
      title: "Least-Mean-Squares (LMS) Adaptive Noise Cancellation",
      shortTitle: "LMS Adaptive Filtering",
      estimatedMinutes: 55,
      difficulty: "GATE ECE Level",
      summary: "Stochastic gradient descent optimization, Wiener-Hopf equation, weight adaptation recursion, and convergence step-size bounds.",
      learningObjectives: [
        "Derive the instantaneous gradient estimation in LMS algorithms",
        "Formulate weight vector update equation w(n+1) = w(n) + 2 mu e(n) x(n)",
        "Determine the upper bound on step-size mu < 1 / lambda_max for stability"
      ],
      markdownNotes: `### 1. Adaptive Filtering Configuration
In adaptive noise cancellation, an input signal $x[n]$ contaminated with noise is processed by an FIR filter with time-varying weights $\\mathbf{w}[n]$ to approximate a desired signal $d[n]$.

The filter output is:
$$y[n] = \\mathbf{w}^T[n] \\mathbf{x}[n] = \\sum_{k=0}^{M-1} w_k[n] x[n-k]$$

The instantaneous error signal is:
$$e[n] = d[n] - y[n]$$

### 2. Widrow-Hoff LMS Weight Update
Instead of inverting the autocorrelation matrix $\\mathbf{R}$ as in Wiener filters, LMS approximates the mean square error gradient $\\nabla J[n]$ with $-2 e[n] \\mathbf{x}[n]$:

$$\\mathbf{w}[n+1] = \\mathbf{w}[n] + 2 \\mu e[n] \\mathbf{x}[n]$$

### 3. Stability & Convergence Condition
For the weight vector mean to converge to the optimal Wiener solution $\\mathbf{w}_o$:
$$0 < \\mu < \\frac{1}{\\lambda_{\\max}} < \\frac{1}{\\text{tr}(\\mathbf{R})} = \\frac{1}{M \\cdot P_x}$$
where $P_x = E[x^2[n]]$ is the input signal power.
`,
      formulas: [
        {
          id: "FORM_LMS_UPDATE",
          name: "LMS Weight Adaptation Equation",
          latex: "\\mathbf{w}[n + 1] = \\mathbf{w}[n] + 2\\mu e[n] \\mathbf{x}[n]",
          description: "Widrow-Hoff stochastic gradient descent weight update equation for adaptive transversal filters.",
          variables: {
            "\\mathbf{w}[n]": "Weight tap vector at iteration n",
            "\\mu": "Convergence step-size adaptation factor",
            "e[n]": "Instantaneous estimation error d[n] - y[n]",
            "\\mathbf{x}[n]": "Input sample buffer vector"
          },
          examSignificance: "High (Part B 16-Mark Derivation)"
        }
      ]
    }
  ],

  // ===========================================================================
  // COURSE 2: EC23C03 - Electronic Devices
  // ===========================================================================
  "EC23C03": [
    // Unit I: Lesson 1
    {
      id: "EC23C03_U1_L1",
      courseCode: "EC23C03",
      unitNumber: 1,
      unitRoman: "I",
      lessonNumber: 1,
      title: "Carrier Concentration, Fermi-Dirac Statistics & Einstein Relations",
      shortTitle: "Carrier Transport & Fermi Level",
      estimatedMinutes: 50,
      difficulty: "Foundational",
      summary: "Intrinsic vs extrinsic silicon, mass action law, Fermi-Dirac distribution, drift-diffusion currents, and the Einstein thermal voltage relation.",
      learningObjectives: [
        "Calculate intrinsic carrier concentration ni as a function of temperature",
        "Locate Fermi level position EF in n-type and p-type semiconductors",
        "Derive Einstein's relationship between diffusion coefficient D and mobility mu"
      ],
      markdownNotes: `### 1. Carrier Statistics in Silicon
In thermal equilibrium, the concentration of electrons in the conduction band $n_0$ and holes in the valence band $p_0$ are governed by:

$$n_0 = N_c e^{-\\frac{E_c - E_F}{kT}}, \\quad p_0 = N_v e^{-\\frac{E_F - E_v}{kT}}$$

The Mass Action Law holds universally:
$$n_0 p_0 = n_i^2(T) = N_c N_v e^{-\\frac{E_g}{kT}}$$
At $T = 300\\text{ K}$, for Silicon: $n_i \\approx 1.5 \\times 10^{10}\\text{ cm}^{-3}$, $E_g \\approx 1.12\\text{ eV}$.

### 2. Total Current Density (Drift + Diffusion)
Current flow comprises drift due to electric field $\\mathcal{E}$ and diffusion due to concentration gradients:
$$J_n = q n \\mu_n \\mathcal{E} + q D_n \\frac{dn}{dx}$$
$$J_p = q p \\mu_p \\mathcal{E} - q D_p \\frac{dp}{dx}$$

### 3. Einstein's Relation
At thermal equilibrium ($J = 0$), the ratio of diffusion coefficient to mobility equals the thermal voltage $V_T$:
$$\\frac{D_n}{\\mu_n} = \\frac{D_p}{\\mu_p} = \\frac{kT}{q} = V_T \\approx 25.86\\text{ mV at } 300\\text{ K}$$
`,
      formulas: [
        {
          id: "FORM_MASS_ACTION",
          name: "Mass Action Law",
          latex: "n_0 p_0 = n_i^2 = N_c N_v e^{-\\frac{E_g}{kT}}",
          description: "Equilibrium product of electron and hole concentrations in an extrinsic semiconductor.",
          variables: {
            "n_0, p_0": "Equilibrium electron and hole densities (cm^-3)",
            "n_i": "Intrinsic carrier concentration (1.5 x 10^10 cm^-3 for Si at 300K)",
            "E_g": "Semiconductor bandgap energy (1.12 eV for Si)",
            "k": "Boltzmann's constant (1.38 x 10^-23 J/K)",
            "T": "Absolute temperature in Kelvin"
          },
          examSignificance: "Essential (Part A 2-Mark Question)"
        },
        {
          id: "FORM_EINSTEIN_RELATION",
          name: "Einstein Diffusion-Mobility Relation",
          latex: "\\frac{D}{\\mu} = \\frac{kT}{q} = V_T",
          description: "Connects carrier diffusion coefficient to drift mobility via thermal voltage.",
          variables: {
            "D": "Diffusion coefficient (cm^2/s)",
            "\\mu": "Carrier mobility (cm^2 / V*s)",
            "V_T": "Thermal voltage (~25.9 mV at room temperature)"
          },
          examSignificance: "Medium (Part B 8-Mark Problem)"
        }
      ]
    },

    // Unit II: Lesson 2
    {
      id: "EC23C03_U2_L1",
      courseCode: "EC23C03",
      unitNumber: 2,
      unitRoman: "II",
      lessonNumber: 1,
      title: "PN Junction Diode Electrostatics & The Shockley Ideal Equation",
      shortTitle: "Shockley Diode IV Physics",
      estimatedMinutes: 50,
      difficulty: "Intermediate",
      summary: "Built-in potential barrier, depletion width, Poisson's equation space charge profile, and Shockley diode forward/reverse characteristics.",
      learningObjectives: [
        "Calculate the built-in potential V_bi from doping densities Na and Nd",
        "Derive depletion layer width W as a function of reverse bias",
        "Analyze Shockley equation parameters: reverse saturation current Is and ideality factor eta"
      ],
      markdownNotes: `### 1. Built-in Potential Barrier
When a p-type and n-type semiconductor join, carrier diffusion sets up an unneutralized space charge region:

$$V_{bi} = V_T \\ln\\left( \\frac{N_a N_d}{n_i^2} \\right)$$

### 2. Depletion Width under Bias
Under an applied voltage $V_a$ (positive for forward bias, negative for reverse bias):
$$W = \\sqrt{\\frac{2 \\varepsilon_s}{q} \\left( \\frac{1}{N_a} + \\frac{1}{N_d} \\right) (V_{bi} - V_a)}$$

### 3. Shockley Ideal Diode Equation
$$I_D = I_S \\left( e^{\\frac{q V_D}{\\eta k T}} - 1 \\right) = I_S \\left( e^{\\frac{V_D}{\\eta V_T}} - 1 \\right)$$
- **Forward Bias ($V_D > 3 V_T$):** Current increases exponentially: $I_D \\approx I_S e^{V_D / \\eta V_T}$.
- **Reverse Bias ($V_D < -3 V_T$):** Current saturates to $-I_S$.
- **Dynamic Small-Signal Resistance:**
  $$r_d = \\frac{d V_D}{d I_D} \\approx \\frac{\\eta V_T}{I_D}$$
`,
      formulas: [
        {
          id: "FORM_SHOCKLEY_DIODE",
          name: "Shockley Ideal Diode Current Equation",
          latex: "I_D = I_S \\left( e^{\\frac{q V_D}{\\eta k T}} - 1 \\right)",
          description: "Universal forward-reverse IV characteristic equation for semiconductor pn junctions.",
          variables: {
            "I_D": "Diode terminal current (A)",
            "I_S": "Reverse saturation current (typically 10^-12 A for Si)",
            "V_D": "Applied terminal bias voltage (V)",
            "\\eta": "Ideality factor (1 for diffusion, 2 for recombination)"
          },
          examSignificance: "High (Part B 16-Mark Derivation)"
        }
      ],
      simulationBridge: {
        experimentName: "Diode IV Curve & Dynamic Resistance Workbench",
        tool: "LTspice",
        actionDescription: "Tune forward voltage and temperature to calculate real-time dynamic resistance rd."
      }
    },

    // Unit III: Lesson 3
    {
      id: "EC23C03_U3_L1",
      courseCode: "EC23C03",
      unitNumber: 3,
      unitRoman: "III",
      lessonNumber: 1,
      title: "Bipolar Junction Transistor Transport & The Early Effect",
      shortTitle: "BJT Ebers-Moll & Early Effect",
      estimatedMinutes: 50,
      difficulty: "Advanced",
      summary: "Minority carrier base profile, base transport factor, emitter injection efficiency, base-width modulation (Early effect), and Early voltage VA.",
      learningObjectives: [
        "Relate terminal currents IE, IB, IC through alpha and beta parameters",
        "Formulate base-width modulation as a function of collector-base reverse voltage VCB",
        "Calculate output dynamic resistance ro from Early voltage VA"
      ],
      markdownNotes: `### 1. Carrier Transport in Active Mode
In forward-active mode (EBJ forward biased, CBJ reverse biased), electrons injected from the emitter traverse the narrow base region by diffusion:

$$I_C = I_S e^{V_{BE} / V_T} \\left( 1 + \\frac{V_{CE}}{V_A} \\right)$$
$$I_B = \\frac{I_C}{\\beta}, \\quad I_E = I_B + I_C = \\frac{1 + \\beta}{\\beta} I_C$$

### 2. Base-Width Modulation (Early Effect)
As the reverse bias across the collector-base junction $V_{CB}$ increases, the depletion layer widens into the lightly doped base, narrowing the neutral base width $W_B$.
This causes:
1. Less base recombination $\\implies$ Common-emitter current gain $\\beta$ increases.
2. A non-zero slope in the output characteristics $I_C$ vs $V_{CE}$.

### 3. Small-Signal Output Resistance
$$r_o = \\left( \\frac{\\partial I_C}{\\partial V_{CE}} \\right)^{-1} = \\frac{V_A + V_{CE}}{I_C} \\approx \\frac{V_A}{I_C}$$
where $V_A$ is the Early Voltage (typically $50\\text{ V} - 150\\text{ V}$).
`,
      formulas: [
        {
          id: "FORM_EARLY_RESISTANCE",
          name: "BJT Output Resistance via Early Voltage",
          latex: "r_o = \\frac{V_A + V_{CE}}{I_C} \\approx \\frac{V_A}{I_C}",
          description: "Small-signal output resistance modeling base-width modulation in forward-active BJTs.",
          variables: {
            "r_o": "Small-signal collector-emitter dynamic resistance",
            "V_A": "Early voltage intercept on the negative Vce axis",
            "I_C": "DC collector operating point current"
          },
          examSignificance: "Medium (Part B 8-Mark Problem)"
        }
      ]
    },

    // Unit IV: Lesson 4
    {
      id: "EC23C03_U4_L1",
      courseCode: "EC23C03",
      unitNumber: 4,
      unitRoman: "IV",
      lessonNumber: 1,
      title: "Nanoscale MOSFET Physics, Inversion & Channel Length Modulation",
      shortTitle: "MOSFET Strong Inversion",
      estimatedMinutes: 50,
      difficulty: "Advanced",
      summary: "Metal-Oxide-Semiconductor energy band bending, flatband voltage, threshold voltage VT derivation, quadratic saturation model, and lambda channel modulation.",
      learningObjectives: [
        "Explain surface accumulation, depletion, and strong inversion thresholds",
        "Derive drain current equations in linear and pinch-off saturation regimes",
        "Calculate transconductance gm and small-signal output resistance ro"
      ],
      markdownNotes: `### 1. MOS Band Bending & Threshold Invariant
Strong inversion begins when the surface potential $\\phi_s$ reaches twice the bulk Fermi potential $2\\phi_F$:

$$V_{TH} = V_{FB} + 2\\phi_F + \\frac{\\sqrt{2 q \\varepsilon_s N_a (2\\phi_F)}}{C_{ox}}$$
where $C_{ox} = \\varepsilon_{ox} / t_{ox}$ is the gate oxide capacitance per unit area.

### 2. Current-Voltage Regimes (NMOS)
- **Triode / Linear ($V_{GS} > V_{TH}$ and $V_{DS} < V_{GS} - V_{TH}$):**
  $$I_D = \\mu_n C_{ox} \\frac{W}{L} \\left[ (V_{GS} - V_{TH}) V_{DS} - \\frac{V_{DS}^2}{2} \\right]$$
- **Saturation / Pinch-off ($V_{GS} > V_{TH}$ and $V_{DS} \\ge V_{GS} - V_{TH}$):**
  $$I_D = \\frac{1}{2} \\mu_n C_{ox} \\frac{W}{L} (V_{GS} - V_{TH})^2 (1 + \\lambda V_{DS})$$

### 3. Transconductance ($g_m$)
$$g_m = \\frac{\\partial I_D}{\\partial V_{GS}} = \\mu_n C_{ox} \\frac{W}{L} (V_{GS} - V_{TH}) = \\sqrt{2 \\mu_n C_{ox} \\frac{W}{L} I_D}$$
`,
      formulas: [
        {
          id: "FORM_MOSFET_SAT",
          name: "MOSFET Saturation Current",
          latex: "I_D = \\frac{1}{2} \\mu_n C_{ox} \\frac{W}{L} (V_{GS} - V_{TH})^2 (1 + \\lambda V_{DS})",
          description: "Drain current in saturation with channel length modulation factor lambda.",
          variables: {
            "\\mu_n C_{ox}": "Process transconductance parameter (A/V^2)",
            "W/L": "Aspect ratio (channel width / channel length)",
            "V_{GS} - V_{TH}": "Gate overdrive voltage (V_ov)",
            "\\lambda": "Channel length modulation parameter (V^-1)"
          },
          examSignificance: "High (Part B 16-Mark Derivation)"
        }
      ]
    },

    // Unit V: Lesson 5
    {
      id: "EC23C03_U5_L1",
      courseCode: "EC23C03",
      unitNumber: 5,
      unitRoman: "V",
      lessonNumber: 1,
      title: "Breakdown Mechanisms: Zener vs Avalanche & Varactor Capacitance",
      shortTitle: "Diode Breakdowns & Varactors",
      estimatedMinutes: 45,
      difficulty: "Intermediate",
      summary: "Quantum mechanical tunneling vs impact ionization, temperature coefficients of breakdown voltages, and voltage-variable junction capacitance tuning.",
      learningObjectives: [
        "Contrast Zener tunneling (<5V) and Avalanche multiplication (>6V)",
        "Explain negative temperature coefficient of Zener vs positive of Avalanche",
        "Formulate voltage-dependent junction capacitance Cj = Cj0 / (1 - Vr/Vbi)^m"
      ],
      markdownNotes: `### 1. Breakdown Mechanisms Comparison
- **Zener Breakdown ($V_Z < 5\\text{ V}$):**
  Occurs in heavily doped junctions ($N_a, N_d > 10^{18}\\text{ cm}^{-3}$). The depletion region is extremely narrow ($< 10\\text{ nm}$), producing a massive electric field ($> 10^6\\text{ V/cm}$) that pulls electrons directly from valence to conduction band by quantum tunneling.
  - Temperature Coefficient: **Negative** (as $T$ increases, bandgap $E_g$ narrows, easing tunneling).
- **Avalanche Breakdown ($V_Z > 6\\text{ V}$):**
  Occurs in lightly doped junctions. Thermally generated carriers gain sufficient kinetic energy from the electric field to knock lattice valence electrons into conduction (impact ionization).
  - Temperature Coefficient: **Positive** (increased lattice scattering reduces mean free path).

### 2. Varactor Diode Capacitance
A reverse-biased diode acts as a voltage-controlled capacitor:
$$C_j(V_R) = \\frac{C_{j0}}{\\left( 1 + \\frac{V_R}{V_{bi}} \\right)^m}$$
where $m = 1/2$ for abrupt junctions and $m = 1/3$ for linearly graded junctions.
`,
      formulas: [
        {
          id: "FORM_VARACTOR_CAP",
          name: "Junction Transition Capacitance",
          latex: "C_j = \\frac{C_{j0}}{\\left( 1 + \\frac{V_R}{V_{bi}} \\right)^m}",
          description: "Models voltage-dependent capacitance in varactor diodes and RF tuning tanks.",
          variables: {
            "C_{j0}": "Zero-bias junction capacitance",
            "V_R": "Applied reverse voltage (V)",
            "V_{bi}": "Built-in potential barrier",
            "m": "Grading coefficient (0.5 for abrupt, 0.33 for linearly graded)"
          },
          examSignificance: "Essential (Part A 2-Mark Question)"
        }
      ]
    }
  ],

  // ===========================================================================
  // COURSE 3: EC23E04 - Optics and Lasers
  // ===========================================================================
  "EC23E04": [
    // Unit I: Lesson 1
    {
      id: "EC23E04_U1_L1",
      courseCode: "EC23E04",
      unitNumber: 1,
      unitRoman: "I",
      lessonNumber: 1,
      title: "Electromagnetic Wave Optics, Coherence & Michelson Interferometry",
      shortTitle: "Wave Optics & Coherence",
      estimatedMinutes: 50,
      difficulty: "Foundational",
      summary: "Maxwell plane wave propagation in dielectric media, spatial and temporal coherence, coherence length Lc = c / delta-nu, and interference visibility.",
      learningObjectives: [
        "Relate refractive index n to wave velocity and propagation constant beta",
        "Derive temporal coherence length Lc from spectral linewidth delta-lambda",
        "Calculate fringe visibility in Michelson and Mach-Zehnder interferometers"
      ],
      markdownNotes: `### 1. Optical Wave Propagation
An optical plane wave traveling along the $z$-direction in an isotropic dielectric medium is governed by the Helmholtz wave equation:

$$E(z, t) = E_0 e^{-\\alpha z} \\cos(\\omega t - k z), \\quad k = \\frac{2\\pi n}{\\lambda_0}$$
where $n = \\sqrt{\\varepsilon_r}$ is the refractive index and $\\alpha$ is the attenuation coefficient.

### 2. Temporal Coherence & Coherence Length
Temporal coherence characterizes the phase correlation between optical oscillations at the same spatial point at two different times $\\tau$.
The coherence time $\\tau_c$ and coherence length $L_c$ are given by:

$$\\tau_c \\approx \\frac{1}{\\Delta \\nu}, \\quad L_c = c \\tau_c = \\frac{c}{\\Delta \\nu} = \\frac{\\lambda_0^2}{\\Delta \\lambda}$$

#### Comparison across Light Sources:
- White Sunlight: $\\Delta \\lambda \\approx 300\\text{ nm} \\implies L_c \\approx 1\\text{ }\\mu\\text{m}$ (low coherence).
- He-Ne Gas Laser: $\\Delta \\nu \\approx 1\\text{ MHz} \\implies L_c \\approx 300\\text{ m}$ (ultra-high coherence).

### 3. Michelson Fringe Visibility
$$V = \\frac{I_{\\max} - I_{\\min}}{I_{\\max} + I_{\\min}} = |\\gamma_{11}(\\tau)|$$
`,
      formulas: [
        {
          id: "FORM_COHERENCE_LENGTH",
          name: "Optical Coherence Length",
          latex: "L_c = c \\tau_c = \\frac{c}{\\Delta \\nu} = \\frac{\\lambda_0^2}{\\Delta \\lambda}",
          description: "Maximum optical path difference over which laser interference fringes can form.",
          variables: {
            "L_c": "Coherence length in meters",
            "c": "Speed of light in vacuum (3 x 10^8 m/s)",
            "\\Delta \\nu": "Spectral linewidth frequency spread (Hz)",
            "\\lambda_0": "Central emission wavelength (m)",
            "\\Delta \\lambda": "Linewidth in wavelength units (m)"
          },
          examSignificance: "Essential (Part A 2-Mark Question)"
        }
      ]
    },

    // Unit II: Lesson 2
    {
      id: "EC23E04_U2_L1",
      courseCode: "EC23E04",
      unitNumber: 2,
      unitRoman: "II",
      lessonNumber: 1,
      title: "Einstein A & B Coefficients, Stimulated Emission & Population Inversion",
      shortTitle: "Einstein A & B Coefficients",
      estimatedMinutes: 50,
      difficulty: "Intermediate",
      summary: "Spontaneous emission, stimulated emission, stimulated absorption, blackbody thermal equilibrium, and population inversion threshold.",
      learningObjectives: [
        "Formulate radiative transition rates between energy states E1 and E2",
        "Derive Einstein's coefficient ratio B12 = B21 and A21 / B21 = (8 pi h nu^3) / c^3",
        "Explain why a two-level optical system cannot achieve steady-state population inversion"
      ],
      markdownNotes: `### 1. Three Radiative Processes
For two atomic energy levels $E_1$ and $E_2$ with populations $N_1$ and $N_2$ in radiation field spectral energy density $\\rho(\\nu)$:
1. **Stimulated Absorption:** Rate $= B_{12} N_1 \\rho(\\nu)$
2. **Spontaneous Emission:** Rate $= A_{21} N_2$
3. **Stimulated Emission:** Rate $= B_{21} N_2 \\rho(\\nu)$

### 2. Einstein Relations
At thermodynamic equilibrium, matching with Planck's radiation law yields:
$$B_{12} = \\frac{g_2}{g_1} B_{21}$$
$$\\frac{A_{21}}{B_{21}} = \\frac{8 \\pi h \\nu^3}{c^3}$$

### 3. Population Inversion Threshold
For net optical amplification, stimulated emission must dominate over absorption:
$$B_{21} N_2 \\rho(\\nu) > B_{12} N_1 \\rho(\\nu) \\implies N_2 > \\frac{g_2}{g_1} N_1$$
This non-equilibrium condition ($N_2 > N_1$) requires external pumping in a 3-level (e.g. Ruby) or 4-level (e.g. Nd:YAG) medium.
`,
      formulas: [
        {
          id: "FORM_EINSTEIN_RATIO",
          name: "Einstein Coefficient Ratio",
          latex: "\\frac{A_{21}}{B_{21}} = \\frac{8\\pi h \\nu^3}{c^3}",
          description: "Ratio of spontaneous to stimulated emission rates demonstrating rapid increase of spontaneous noise at high optical frequencies.",
          variables: {
            "A_{21}": "Spontaneous emission transition probability rate (s^-1)",
            "B_{21}": "Stimulated emission rate coefficient",
            "h": "Planck's constant (6.626 x 10^-34 J*s)",
            "\\nu": "Optical photon frequency (Hz)"
          },
          examSignificance: "High (Part B 16-Mark Derivation)"
        }
      ]
    },

    // Unit III: Lesson 3
    {
      id: "EC23E04_U3_L1",
      courseCode: "EC23E04",
      unitNumber: 3,
      unitRoman: "III",
      lessonNumber: 1,
      title: "Optical Resonator Cavity Stability & g-Parameter Boundaries",
      shortTitle: "Laser Resonator Stability",
      estimatedMinutes: 50,
      difficulty: "Advanced",
      summary: "Ray transfer matrix ABCD formulation for curved mirrors, resonator g-parameters, round-trip stability criterion, and longitudinal mode spacing.",
      learningObjectives: [
        "Calculate g-parameters g1 = 1 - L/R1 and g2 = 1 - L/R2",
        "Apply the Sylvester stability criterion 0 <= g1 * g2 <= 1 to optical resonators",
        "Determine longitudinal cavity mode frequency spacing delta-nu = c / (2 n L)"
      ],
      markdownNotes: `### 1. Ray Transfer Matrix for Optical Cavities
A two-mirror Fabry-Perot cavity of length $L$ with mirror radii of curvature $R_1$ and $R_2$ can be analyzed as a periodic sequence of lenses.

The resonator $g$-parameters are defined as:
$$g_1 = 1 - \\frac{L}{R_1}, \\quad g_2 = 1 - \\frac{L}{R_2}$$

### 2. Resonator Stability Condition
A paraxial optical ray remains confined within the cavity after an arbitrary number of round-trips if and only if:
$$0 \\le g_1 g_2 \\le 1$$

#### Classic Resonator Configurations:
- **Planar (Flat-Flat):** $R_1 = R_2 = \\infty \\implies g_1 = g_2 = 1 \\implies g_1 g_2 = 1$ (Marginally Stable).
- **Symmetric Confocal:** $R_1 = R_2 = L \\implies g_1 = g_2 = 0 \\implies g_1 g_2 = 0$ (Stable, low diffraction loss).
- **Concentric (Spherical):** $R_1 = R_2 = L/2 \\implies g_1 = g_2 = -1 \\implies g_1 g_2 = 1$ (Critical Boundary).

### 3. Longitudinal Mode Frequency Spacing
$$\\Delta \\nu_{long} = \\frac{c}{2 n L}$$
`,
      formulas: [
        {
          id: "FORM_RESONATOR_STABILITY",
          name: "Resonator Stability Criterion",
          latex: "0 \\le g_1 g_2 \\le 1, \\quad g_1 = 1 - \\frac{L}{R_1}, \\quad g_2 = 1 - \\frac{L}{R_2}",
          description: "Defines the geometric stability boundary preventing diffractive beam escape from laser cavities.",
          variables: {
            "L": "Cavity length between mirrors (m)",
            "R_1, R_2": "Radii of curvature of mirrors 1 and 2 (m)",
            "g_1, g_2": "Resonator dimensionless geometric parameters"
          },
          examSignificance: "High (Part B 16-Mark Derivation)"
        },
        {
          id: "FORM_LONGITUDINAL_MODES",
          name: "Longitudinal Mode Frequency Spacing",
          latex: "\\Delta \\nu = \\frac{c}{2 n L}",
          description: "Frequency interval between adjacent resonant axial TEM00 modes in a laser cavity.",
          variables: {
            "\\Delta \\nu": "Mode separation (Hz)",
            "c": "Speed of light (3 x 10^8 m/s)",
            "n": "Refractive index of intracavity medium",
            "L": "Cavity physical length (m)"
          },
          examSignificance: "Medium (Part B 8-Mark Problem)"
        }
      ],
      simulationBridge: {
        experimentName: "Laser Resonator Cavity Stability Workbench",
        tool: "Optics Ray Tracer",
        actionDescription: "Adjust L, R1, and R2 sliders to verify stability condition 0 <= g1*g2 <= 1."
      }
    },

    // Unit IV: Lesson 4
    {
      id: "EC23E04_U4_L1",
      courseCode: "EC23E04",
      unitNumber: 4,
      unitRoman: "IV",
      lessonNumber: 1,
      title: "Ultrafast Laser Pulse Generation: Q-Switching vs Mode-Locking",
      shortTitle: "Q-Switching & Mode-Locking",
      estimatedMinutes: 45,
      difficulty: "Advanced",
      summary: "Intracavity loss modulation, giant pulse generation, saturable absorber dyes, and Kerr lens femtosecond mode locking.",
      learningObjectives: [
        "Contrast giant nanosecond pulse generation (Q-switching) with picosecond/femtosecond pulses (mode-locking)",
        "Formulate pulse repetition rate and peak power relations P_peak = E_pulse / tau_p",
        "Describe active electro-optic Pockels cells vs passive semiconductor saturable absorber mirrors (SESAM)"
      ],
      markdownNotes: `### 1. Q-Switching (Giant Nanosecond Pulses)
By artificially spoiling cavity quality factor $Q$ (introducing high loss), population inversion builds up to extremely high values far above the normal threshold.
Suddenly restoring high $Q$ releases the stored inverted energy as a single giant optical pulse:
- Pulse duration: $\\tau_p \\sim 1 - 50\\text{ ns}$
- Peak power: Megawatts ($10^6 - 10^9\\text{ W}$)

### 2. Mode-Locking (Femtosecond Pulses)
When $N$ independent longitudinal cavity modes have their relative phases locked ($e^{j\\phi_m} = \\text{const}$), they interfere constructively to form a train of ultra-short periodic pulses:
- Pulse repetition rate: $T_{rep} = \\frac{2 L}{c}$
- Pulse width: $\\tau_p \\approx \\frac{1}{\\Delta \\nu_{gain}} \\sim 10 - 100\\text{ fs}$
- Peak Power Amplification: $P_{peak} = N \\cdot P_{avg}$
`,
      formulas: [
        {
          id: "FORM_MODE_LOCKING_WIDTH",
          name: "Mode-Locked Pulse Duration",
          latex: "\\tau_p \\approx \\frac{1}{N \\Delta \\nu} = \\frac{1}{\\Delta \\nu_{gain}}",
          description: "Fourier transform limited pulse width inversely proportional to the laser gain bandwidth.",
          variables: {
            "\\tau_p": "Full-width at half-maximum (FWHM) pulse duration",
            "\\Delta \\nu_{gain}": "Lasing medium gain bandwidth (Hz)",
            "N": "Number of locked phase-coherent modes"
          },
          examSignificance: "Essential (Part A 2-Mark Question)"
        }
      ]
    },

    // Unit V: Lesson 5
    {
      id: "EC23E04_U5_L1",
      courseCode: "EC23E04",
      unitNumber: 5,
      unitRoman: "V",
      lessonNumber: 1,
      title: "Semiconductor Double Heterostructure (DH) & Quantum Well Lasers",
      shortTitle: "Semiconductor Diode Lasers",
      estimatedMinutes: 50,
      difficulty: "Intermediate",
      summary: "Bandgap engineering, optical and electrical confinement, threshold current density Jth reduction, and single-mode DFB gratings.",
      learningObjectives: [
        "Explain how GaAs/AlGaAs double heterostructures confine both carriers and optical photons",
        "Calculate threshold current density Jth from internal quantum efficiency and cavity loss",
        "Describe Distributed Feedback (DFB) Bragg grating wavelength selection lambda_B = 2 n_eff Lambda"
      ],
      markdownNotes: `### 1. Double Heterostructure (DH) Architecture
Homojunction GaAs lasers require impractically high current densities ($J_{th} > 50,000\\text{ A/cm}^2$ at room temp).
The Double Heterostructure sandwiches a thin narrow-bandgap GaAs active layer between two wide-bandgap AlGaAs cladding layers:
1. **Carrier Confinement:** Energy band offsets $\\Delta E_c$ and $\\Delta E_v$ form a potential well preventing electrons and holes from escaping.
2. **Optical Waveguiding Confinement:** GaAs has a higher refractive index ($n = 3.6$) than AlGaAs ($n = 3.4$), forming a dielectric optical waveguide that guides generated photons.
- Result: $J_{th}$ drops to $< 1000\\text{ A/cm}^2$ (enabling continuous room-temperature operation).

### 2. Distributed Feedback (DFB) Bragg Condition
$$\\lambda_B = 2 n_{eff} \\Lambda$$
where $\\Lambda$ is the etched corrugation pitch and $n_{eff}$ is the effective modal index.
`,
      formulas: [
        {
          id: "FORM_BRAGG_DFB",
          name: "Bragg Wavelength Selection",
          latex: "\\lambda_B = \\frac{2 n_{eff} \\Lambda}{m}",
          description: "Governs single-frequency dynamic longitudinal mode selection in telecommunication DFB lasers.",
          variables: {
            "\\lambda_B": "Bragg lasing wavelength",
            "n_{eff}": "Effective waveguide refractive index",
            "\\Lambda": "Periodic grating spatial period (pitch)",
            "m": "Diffraction order (typically 1)"
          },
          examSignificance: "Essential (Part A 2-Mark Question)"
        }
      ]
    }
  ],

  // ===========================================================================
  // COURSE 4: EC8702 - Embedded Systems
  // ===========================================================================
  "EC8702": [
    // Unit I: Lesson 1
    {
      id: "EC8702_U1_L1",
      courseCode: "EC8702",
      unitNumber: 1,
      unitRoman: "I",
      lessonNumber: 1,
      title: "ARM Cortex-M Architecture, Pipeline & Nested Vectored Interrupt Controller (NVIC)",
      shortTitle: "ARM Cortex-M & NVIC Pipeline",
      estimatedMinutes: 50,
      difficulty: "Foundational",
      summary: "Harvard 3-stage pipeline, Thumb-2 instruction set, deterministic zero-latency interrupt handling, tail-chaining, and late-arrival preemption.",
      learningObjectives: [
        "Distinguish between ARM Cortex-M0+, M3, and M4 core microarchitectures",
        "Explain NVIC low-latency features: tail-chaining (6 cycles) and late-arriving interrupts",
        "Configure preemption priority and subpriority register groupings"
      ],
      markdownNotes: `### 1. ARM Cortex-M Pipeline & Register Architecture
The ARM Cortex-M4 features a 3-stage pipeline (Fetch, Decode, Execute) implementing the 32-bit ARMv7-M architecture with Thumb-2 instructions.

#### Key Register Set:
- **General Purpose:** $R_0 - R_{12}$
- **Stack Pointers:** $R_{13}$ banked into Main Stack Pointer (MSP) and Process Stack Pointer (PSP)
- **Link Register:** $R_{14}$ (stores return address or \`EXC_RETURN\` during exception entry)
- **Program Counter:** $R_{15}$

### 2. NVIC Hardware Exception Handling
The Nested Vectored Interrupt Controller (NVIC) is tightly coupled with the core for deterministic, low-latency interrupt servicing:
- **Automatic Hardware Stacking:** Upon interrupt, the hardware automatically pushes 8 words to the stack ($R_0 - R_3, R_{12}, LR, PC, xPSR$) in 12 clock cycles.
- **Tail-Chaining:** If a second interrupt is pending when the first completes, NVIC skips the unstacking/restacking sequence and directly vectors to the next ISR in just **6 clock cycles**.
- **Late-Arriving Preemption:** If a higher-priority interrupt arrives while stacking for a lower-priority interrupt, NVIC redirects to the higher-priority ISR without restarting stacking.
`,
      formulas: [
        {
          id: "FORM_NVIC_LATENCY",
          name: "NVIC Tail-Chaining Latency",
          latex: "T_{tail\\text{-}chain} = 6 \\text{ clock cycles}",
          description: "Hardware optimization eliminating redundant stack pop and push between consecutive interrupt service routines.",
          variables: {
            "T_{tail-chain}": "Cycle latency between consecutive pending ISRs"
          },
          examSignificance: "Essential (Part A 2-Mark Question)"
        }
      ]
    },

    // Unit II: Lesson 2
    {
      id: "EC8702_U2_L1",
      courseCode: "EC8702",
      unitNumber: 2,
      unitRoman: "II",
      lessonNumber: 1,
      title: "Memory Mapped I/O, Bit-Banding & SysTick Timer Architecture",
      shortTitle: "Bit-Banding & SysTick",
      estimatedMinutes: 45,
      difficulty: "Intermediate",
      summary: "Atomic bit manipulation via bit-band alias regions, peripheral memory mapping, and the 24-bit SysTick down-counter calibration.",
      learningObjectives: [
        "Calculate the 32-bit bit-band alias address for any SRAM or Peripheral bit",
        "Prevent race conditions in read-modify-write GPIO pin toggling without disabling interrupts",
        "Configure SysTick reload register for 1ms RTOS kernel scheduling ticks"
      ],
      markdownNotes: `### 1. Bit-Banding Atomic Access
ARM Cortex-M provides bit-banding, which maps individual bits in a 1 MB bit-band region to distinct 32-bit words in a 32 MB bit-band alias region.
Writing 1 to the alias word sets the corresponding bit; writing 0 clears it—achieving **atomic single-cycle operations** without read-modify-write race conditions.

#### Alias Address Formula:
$$\\text{AliasAddress} = \\text{AliasBase} + (\\text{ByteOffset} \\times 32) + (\\text{BitNumber} \\times 4)$$
- **SRAM Bit-Band Base:** \`0x20000000\` mapped to \`0x22000000\`
- **Peripheral Bit-Band Base:** \`0x40000000\` mapped to \`0x42000000\`

### 2. SysTick Real-Time Timer
A 24-bit down-counter dedicated to generating periodic system tick interrupts for RTOS schedulers:
$$\\text{ReloadValue} = (f_{CPU} \\times T_{tick}) - 1$$
For $f_{CPU} = 168\\text{ MHz}$ and $T_{tick} = 1\\text{ ms}$:
$$\\text{ReloadValue} = (168 \\times 10^6 \\times 0.001) - 1 = 167,999$$
`,
      formulas: [
        {
          id: "FORM_BITBAND_MAP",
          name: "Bit-Band Alias Address Formula",
          latex: "\\text{Addr}_{alias} = \\text{Base}_{alias} + (\\text{ByteOffset} \\times 32) + (\\text{Bit} \\times 4)",
          description: "Maps a single bit in the 1MB bit-band region to a unique 32-bit word in the alias space for atomic access.",
          variables: {
            "\\text{Base}_{alias}": "0x22000000 (SRAM) or 0x42000000 (Peripherals)",
            "\\text{ByteOffset}": "Byte offset from memory base (0x0 to 0xFFFFF)",
            "\\text{Bit}": "Target bit position (0 to 7)"
          },
          examSignificance: "Medium (Part B 8-Mark Problem)"
        }
      ]
    },

    // Unit III: Lesson 3
    {
      id: "EC8702_U3_L1",
      courseCode: "EC8702",
      unitNumber: 3,
      unitRoman: "III",
      lessonNumber: 1,
      title: "Synchronous Bus Protocol Engineering: SPI vs I2C Clock Stretching",
      shortTitle: "SPI & I2C Bus Protocols",
      estimatedMinutes: 50,
      difficulty: "Intermediate",
      summary: "Full-duplex SPI phase/polarity (CPOL/CPHA) configurations, open-drain I2C pull-ups, multi-master arbitration, and slave clock stretching.",
      learningObjectives: [
        "Configure the 4 SPI modes based on CPOL and CPHA timing diagrams",
        "Calculate optimal I2C pull-up resistor Rp based on bus capacitance Cb and rise time tr",
        "Trace I2C ACK/NACK signaling and arbitration lost detection"
      ],
      markdownNotes: `### 1. Serial Peripheral Interface (SPI)
Synchronous 4-wire full-duplex protocol:
- **Signals:** SCK (Serial Clock), MOSI (Master Out Slave In), MISO (Master In Slave Out), SS/CS (Slave Select active low).
- **SPI Modes:**
  - Mode 0: CPOL=0 (idle low), CPHA=0 (sample on leading rising edge)
  - Mode 1: CPOL=0 (idle low), CPHA=1 (sample on trailing falling edge)
  - Mode 2: CPOL=1 (idle high), CPHA=0 (sample on leading falling edge)
  - Mode 3: CPOL=1 (idle high), CPHA=1 (sample on trailing rising edge)

### 2. Inter-Integrated Circuit (I2C)
Synchronous 2-wire half-duplex open-drain bus (SDA, SCL):
- **Pull-up Resistor Sizing:**
  $$R_{p,\\min} = \\frac{V_{DD} - V_{OL,\\max}}{I_{OL}}, \\quad R_{p,\\max} = \\frac{t_r}{0.8473 \\cdot C_b}$$
  For standard mode ($100\\text{ kHz}$, $t_r \\le 1000\\text{ ns}$, $C_b = 100\\text{ pF}$): $R_p \\approx 4.7\\text{ k}\\Omega$.
- **Clock Stretching:** A slow slave holds SCL low to delay data transmission until it finishes processing.
`,
      formulas: [
        {
          id: "FORM_I2C_PULLUP",
          name: "I2C Maximum Pull-Up Resistor",
          latex: "R_{p,\\max} = \\frac{t_r}{0.8473 \\cdot C_b}",
          description: "Calculates maximum allowable pull-up resistance to meet I2C rise-time constraints given total bus capacitance.",
          variables: {
            "t_r": "Maximum allowed rise time (1000 ns for Standard Mode)",
            "C_b": "Total capacitive load on the bus wire (pF)"
          },
          examSignificance: "Essential (Part A 2-Mark Question)"
        }
      ]
    },

    // Unit IV: Lesson 4
    {
      id: "EC8702_U4_L1",
      courseCode: "EC8702",
      unitNumber: 4,
      unitRoman: "IV",
      lessonNumber: 1,
      title: "FreeRTOS Preemptive Priority Scheduling & Rate Monotonic Bound",
      shortTitle: "FreeRTOS Scheduling & Bounds",
      estimatedMinutes: 55,
      difficulty: "GATE ECE Level",
      summary: "Task Control Blocks (TCB), context switching via PendSV, priority inversion, priority inheritance, and the Liu & Layland schedulability test.",
      learningObjectives: [
        "Explain PendSV exception mechanism for interrupt-safe RTOS context switching",
        "Calculate Rate Monotonic Scheduling (RMS) utilization bound U <= n(2^(1/n) - 1)",
        "Mitigate priority inversion using FreeRTOS mutex priority inheritance"
      ],
      markdownNotes: `### 1. FreeRTOS Task Lifecycle & PendSV
In FreeRTOS, tasks exist in one of four states: **Running, Ready, Blocked, Suspended**.
Context switches are deferred to the **PendSV** exception (set to the lowest NVIC priority) so that active high-priority peripheral ISRs are never delayed by scheduler overhead.

### 2. Liu & Layland Rate Monotonic Schedulability Bound
For a set of $n$ independent periodic tasks scheduled under Rate Monotonic (shorter period = higher priority), a sufficient condition for all tasks to meet their deadlines is:

$$U = \\sum_{i=1}^n \\frac{C_i}{T_i} \\le n \\left( 2^{1/n} - 1 \\right)$$
- For $n = 1$: $U \\le 100\\%$
- For $n = 2$: $U \\le 2(2^{1/2} - 1) \\approx 82.84\\%$
- For $n = 3$: $U \\le 3(2^{1/3} - 1) \\approx 77.98\\%$
- As $n \\to \\infty$: $U \\to \\ln 2 \\approx 69.3\\%$

### 3. Priority Inversion & Inheritance
When a low-priority task holds a mutex needed by a high-priority task, and is preempted by a medium-priority task, unbounded priority inversion occurs.
- **Fix:** Priority Inheritance temporarily elevates the low-priority task's priority to match that of the blocked high-priority task until the mutex is released.
`,
      formulas: [
        {
          id: "FORM_RMS_BOUND",
          name: "Liu & Layland Schedulability Bound",
          latex: "U = \\sum_{i=1}^n \\frac{C_i}{T_i} \\le n \\left( 2^{1/n} - 1 \\right)",
          description: "Sufficient mathematical bound guaranteeing 100% deadline satisfaction under Rate Monotonic Scheduling.",
          variables: {
            "C_i": "Worst-case execution time of task i",
            "T_i": "Repetition period of task i",
            "n": "Number of periodic tasks in the task set",
            "U": "Total processor utilization factor"
          },
          examSignificance: "High (Part B 16-Mark Derivation)"
        }
      ],
      simulationBridge: {
        experimentName: "FreeRTOS Dual-Task Schedulability Simulator",
        tool: "Wokwi Embedded",
        actionDescription: "Adjust execution times C1, C2 and periods T1, T2 to test against the 82.84% bound."
      }
    },

    // Unit V: Lesson 5
    {
      id: "EC8702_U5_L1",
      courseCode: "EC8702",
      unitNumber: 5,
      unitRoman: "V",
      lessonNumber: 1,
      title: "Ultra Low-Power Embedded Design: Sleep Modes & Hardware Watchdogs",
      shortTitle: "Low-Power & Watchdogs",
      estimatedMinutes: 45,
      difficulty: "Intermediate",
      summary: "Cortex-M WFI/WFE instructions, sleep/deep-sleep modes, clock gating, Independent Watchdog (IWDG) timeout calculations, and battery endurance modeling.",
      learningObjectives: [
        "Contrast Wait For Interrupt (WFI) vs Wait For Event (WFE) instructions",
        "Formulate average current consumption I_avg = (T_on * I_on + T_sleep * I_sleep) / T_total",
        "Calculate Independent Watchdog (IWDG) timeout window to prevent firmware lockups"
      ],
      markdownNotes: `### 1. Power Saving Modes in Cortex-M
1. **Sleep Mode (WFI / WFE):** CPU clock is stopped; peripherals and SysTick continue running. Wakeup is near-instantaneous ($< 5$ clock cycles).
2. **Deep Sleep / Stop Mode:** CPU and high-speed oscillators are disabled; SRAM contents are retained. Wakeup via external EXTI interrupt ($~5 - 10\\text{ }\\mu\\text{s}$).
3. **Standby Mode:** Power to SRAM and CPU core is switched off; only Backup Domain and RTC run on $V_{BAT}$ ($I_{standby} < 1\\text{ }\\mu\\text{A}$).

### 2. Average Current Consumption & Battery Lifetime
For a device active for $T_{on}$ with current $I_{on}$ and sleeping for $T_{sleep}$ with current $I_{sleep}$:

$$I_{avg} = \\frac{T_{on} I_{on} + T_{sleep} I_{sleep}}{T_{on} + T_{sleep}}$$
$$\\text{Battery Life (Hours)} = \\frac{\\text{Capacity (mAh)}}{I_{avg} (\\text{mA})}$$

### 3. Independent Watchdog (IWDG)
Driven by an internal dedicated low-speed oscillator (LSI $\\approx 32\\text{ kHz}$):
$$T_{timeout} = \\frac{4 \\times 2^{PR} \\times \\text{Reload}}{f_{LSI}}$$
`,
      formulas: [
        {
          id: "FORM_AVG_CURRENT",
          name: "Average Embedded Current Consumption",
          latex: "I_{avg} = \\frac{T_{on} I_{on} + T_{sleep} I_{sleep}}{T_{on} + T_{sleep}}",
          description: "Calculates duty-cycled average current draw for estimating battery operating life in remote IoT sensors.",
          variables: {
            "T_{on}": "Active processing duration per cycle",
            "I_{on}": "Active current draw (e.g., 20 mA)",
            "T_{sleep}": "Sleep duration per cycle",
            "I_{sleep}": "Quiescent sleep current (e.g., 5 uA)"
          },
          examSignificance: "Medium (Part B 8-Mark Problem)"
        }
      ]
    }
  ]
};

/**
 * Helper to fetch all lessons for a specific course
 */
export function getLessonsByCourse(courseCode: string): Lesson[] {
  const normalized = courseCode.toUpperCase().trim();
  return COURSE_LESSONS_REGISTRY[normalized] || [];
}

/**
 * Helper to fetch a single lesson by its ID
 */
export function getLessonById(lessonId: string): Lesson | undefined {
  for (const lessons of Object.values(COURSE_LESSONS_REGISTRY)) {
    const match = lessons.find(l => l.id === lessonId);
    if (match) return match;
  }
  return undefined;
}

/**
 * Helper to fetch lessons by unit
 */
export function getLessonsByUnit(courseCode: string, unitNumber: number): Lesson[] {
  const courseLessons = getLessonsByCourse(courseCode);
  return courseLessons.filter(l => l.unitNumber === unitNumber);
}
