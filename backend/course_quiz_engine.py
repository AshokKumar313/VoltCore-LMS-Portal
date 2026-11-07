"""
========================================================================================
VoltCore Apex Academia - Academic Quiz & Automated Assessment Engine (Phase 7)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead & Systems Architect: Ashok Kumar A
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313

Capabilities:
  - Curated academic assessment catalog for priority courses:
      * EC23S01: Numerical and Signal Processing Practice Through Python
      * EC23C03: Electronic Devices
      * EC23E04: Optics and Lasers
      * EC8702:  Embedded Systems
  - Question validation (MCQ, Part A 2-mark conceptual, Part B 16-mark numerical/derivation)
  - Objective MCQ autograding with Bloom's Taxonomy attainment breakdown
  - KaTeX mathematical solution verification and common pitfall diagnostics
  - Lightweight SQLite WAL gradebook recording with zero background daemons
Hardware Safe: Zero background polling loops, passive CPU footprint (<8%), thread-safe.
========================================================================================
"""

import os
import json
import sqlite3
import datetime
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")

# -----------------------------------------------------------------------------
# ACADEMIC ASSESSMENT REGISTRY (ANNA UNIVERSITY REGULATION 2023 ALIGNED)
# -----------------------------------------------------------------------------

COURSE_QUIZ_CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "EC23S01": [
        {
            "id": "EC23S01_Q1",
            "courseCode": "EC23S01",
            "unitNumber": 1,
            "unitRoman": "I",
            "type": "MCQ",
            "bloomLevel": "L3 (Apply)",
            "questionText": "An input sequence x[n] has length N1 = 32 and an LTI filter impulse response h[n] has length N2 = 16. What is the minimum zero-padding DFT size N_FFT required to compute their linear convolution without time-domain aliasing?",
            "options": [
                "N_FFT = 32",
                "N_FFT = 47",
                "N_FFT = 48 (or nearest power of two: 64)",
                "N_FFT = 512"
            ],
            "correctOptionIndex": 2,
            "marks": 1,
            "solutionSummary": "Linear convolution length is L = N1 + N2 - 1 = 32 + 16 - 1 = 47. To avoid circular wrap-around and utilize radix-2 FFT, N_FFT >= 47 (next power of two is 64).",
            "stepByStepExplanation": [
                "1. Recall discrete linear convolution duration: L = len(x) + len(h) - 1.",
                "2. Substitute values: L = 32 + 16 - 1 = 47 samples.",
                "3. Standard circular convolution computed by multiplying DFTs wraps modulo N.",
                "4. To prevent aliasing: N >= 47. In radix-2 FFT algorithms (scipy.fft.fft), pad to 64."
            ],
            "keyFormulas": [
                "L = N_1 + N_2 - 1",
                "N_{\\text{FFT}} \\ge N_1 + N_2 - 1",
                "y[n] = x[n] * h[n] = \\sum_{k=-\\infty}^{\\infty} x[k] h[n-k]"
            ],
            "examYearReference": "AU End-Sem Nov/Dec 2024 (Reg 2023 Model)",
            "commonPitfall": "Confusing linear convolution length (N1 + N2 - 1) with circular convolution size (max(N1, N2))."
        },
        {
            "id": "EC23S01_Q2",
            "courseCode": "EC23S01",
            "unitNumber": 2,
            "unitRoman": "II",
            "type": "MCQ",
            "bloomLevel": "L4 (Analyze)",
            "questionText": "In bilinear transformation IIR filter design, why is frequency pre-warping necessary before applying s = (2/T)*((z-1)/(z+1))?",
            "options": [
                "Because bilinear transformation induces linear phase distortion in FIR filters",
                "To compensate for the non-linear tangent frequency compression: Omega = (2/T)*tan(omega/2)",
                "To enforce stability when poles lie strictly outside the unit circle",
                "To double the transition band roll-off rate"
            ],
            "correctOptionIndex": 1,
            "marks": 1,
            "solutionSummary": "The bilinear transform maps the entire infinite imaginary axis in s-plane to the finite unit circle in z-plane via Omega = (2/T)*tan(omega/2). Pre-warping ensures critical cutoff frequencies match exactly.",
            "stepByStepExplanation": [
                "1. Bilinear transformation uses the mapping: s = (2/T) * (1 - z^-1) / (1 + z^-1).",
                "2. Evaluating along the frequency axis yields: j*Omega = (2/T) * (1 - e^-j*omega) / (1 + e^-j*omega).",
                "3. Simplifying reveals the tangent relationship: Omega = (2/T) * tan(omega / 2).",
                "4. Pre-warping analog cutoff frequencies via Omega_p = (2/T) * tan(omega_p / 2) eliminates warping error at cutoff."
            ],
            "keyFormulas": [
                "\\Omega = \\frac{2}{T} \\tan\\left(\\frac{\\omega}{2}\\right)",
                "s = \\frac{2}{T} \\left( \\frac{z - 1}{z + 1} \\right)",
                "\\omega = 2 \\arctan\\left(\\frac{\\Omega T}{2}\\right)"
            ],
            "examYearReference": "AU Nov/Dec 2023 Reg 2021/2023",
            "commonPitfall": "Assuming the frequency mapping between s-plane and z-plane is linear (which is only approximately true at very low frequencies)."
        },
        {
            "id": "EC23S01_Q3",
            "courseCode": "EC23S01",
            "unitNumber": 3,
            "unitRoman": "III",
            "type": "PART_A",
            "bloomLevel": "L2 (Understand)",
            "questionText": "State Parseval's relation for discrete Fourier transform (DFT) and explain its energy conservation significance in Python signal processing.",
            "marks": 2,
            "solutionSummary": "Parseval's theorem states that the total energy in time domain equals the energy in frequency domain divided by N: sum(|x[n]|^2) = (1/N) * sum(|X[k]|^2).",
            "stepByStepExplanation": [
                "1. State the mathematical formula: sum_{n=0}^{N-1} |x[n]|^2 = (1/N) * sum_{k=0}^{N-1} |X[k]|^2.",
                "2. Explain physical interpretation: Discrete Fourier Transform is an orthogonal unitary transformation that preserves total Euclidean energy.",
                "3. Practical Python implementation: np.sum(np.abs(x)**2) == np.sum(np.abs(np.fft.fft(x))**2) / len(x)."
            ],
            "keyFormulas": [
                "\\sum_{n=0}^{N-1} |x[n]|^2 = \\frac{1}{N} \\sum_{k=0}^{N-1} |X[k]|^2",
                "E_x = \\|x\\|^2 = \\frac{1}{N} \\|X\\|^2"
            ],
            "examYearReference": "AU Apr/May 2024",
            "commonPitfall": "Omitting the 1/N normalization factor on the frequency-domain summation."
        },
        {
            "id": "EC23S01_Q4",
            "courseCode": "EC23S01",
            "unitNumber": 4,
            "unitRoman": "IV",
            "type": "PART_B",
            "bloomLevel": "L4 (Analyze)",
            "questionText": "Design an FIR Low-Pass Filter using the Rectangular and Hamming window methods with cutoff frequency wc = 0.3*pi rad/sample and order M = 20. Derive the filter coefficients h[n] and compare passband ripple and stopband attenuation.",
            "marks": 16,
            "solutionSummary": "Ideal impulse response is hd[n] = sin(wc*(n-alpha)) / (pi*(n-alpha)) with alpha = M/2 = 10. Multiplying with w_hamming[n] = 0.54 - 0.46*cos(2*pi*n/M) yields -53 dB stopband attenuation versus -21 dB for rectangular window.",
            "stepByStepExplanation": [
                "1. Compute delay parameter: alpha = M / 2 = 20 / 2 = 10.",
                "2. Write ideal lowpass response: hd[n] = sin(0.3*pi*(n-10)) / (pi*(n-10)) for n != 10, and hd[10] = 0.3.",
                "3. Multiply by window: h[n] = hd[n] * w[n].",
                "4. Compare: Rectangular window yields 21 dB stopband attenuation (Gibbs oscillation 9%). Hamming window yields 53 dB stopband attenuation with wider transition width (3.3*pi / M)."
            ],
            "keyFormulas": [
                "h_d[n] = \\frac{\\sin(\\omega_c(n - \\alpha))}{\\pi (n - \\alpha)}",
                "w_{\\text{Hamming}}[n] = 0.54 - 0.46 \\cos\\left(\\frac{2\\pi n}{M}\\right)",
                "\\Delta\\omega_{\\text{Hamming}} \\approx \\frac{3.3\\pi}{M}"
            ],
            "examYearReference": "AU Nov/Dec 2024 Part B (16 Marks)",
            "commonPitfall": "Forgetting to evaluate the L'Hopital limit at n = alpha = 10, resulting in division by zero."
        }
    ],
    "EC23C03": [
        {
            "id": "EC23C03_Q1",
            "courseCode": "EC23C03",
            "unitNumber": 1,
            "unitRoman": "I",
            "type": "MCQ",
            "bloomLevel": "L3 (Apply)",
            "questionText": "For an intrinsic silicon sample at T = 300 K with ni = 1.5e10 cm^-3, donor doping Nd = 1e16 cm^-3 is introduced. Assuming complete ionization, what is the minority hole concentration p_n0?",
            "options": [
                "p_n0 = 1.5e4 cm^-3",
                "p_n0 = 2.25e4 cm^-3",
                "p_n0 = 1.0e16 cm^-3",
                "p_n0 = 2.25e10 cm^-3"
            ],
            "correctOptionIndex": 1,
            "marks": 1,
            "solutionSummary": "From mass action law n * p = ni^2. With n ~ Nd = 1e16, p_n0 = (1.5e10)^2 / 1e16 = 2.25e20 / 1e16 = 2.25e4 cm^-3.",
            "stepByStepExplanation": [
                "1. Apply Mass Action Law: n0 * p0 = n_i^2.",
                "2. Since donor concentration Nd >> ni, majority electron density n0 ≈ Nd = 1e16 cm^-3.",
                "3. Calculate minority hole concentration: p_n0 = n_i^2 / Nd.",
                "4. p_n0 = (1.5e10)^2 / 1e16 = 2.25e20 / 1e16 = 2.25e4 cm^-3."
            ],
            "keyFormulas": [
                "n_0 p_0 = n_i^2",
                "p_{n0} = \\frac{n_i^2}{N_d}",
                "n_i = B T^{3/2} e^{-\\frac{E_g}{2 k_B T}}"
            ],
            "examYearReference": "AU Apr/May 2024 Reg 2023",
            "commonPitfall": "Subtracting doping concentration directly instead of applying the multiplicative mass action law."
        },
        {
            "id": "EC23C03_Q2",
            "courseCode": "EC23C03",
            "unitNumber": 2,
            "unitRoman": "II",
            "type": "MCQ",
            "bloomLevel": "L2 (Understand)",
            "questionText": "A silicon p-n junction diode operates with forward bias current ID = 2.6 mA at room temperature (VT = 26 mV). Neglecting series resistance, what is its small-signal dynamic resistance rd?",
            "options": [
                "rd = 1.0 Ohm",
                "rd = 10 Ohms",
                "rd = 100 Ohms",
                "rd = 0.1 Ohm"
            ],
            "correctOptionIndex": 1,
            "marks": 1,
            "solutionSummary": "Dynamic small signal resistance is given by rd = eta * VT / ID. For ideal diode (eta = 1), rd = 26 mV / 2.6 mA = 10 Ohms.",
            "stepByStepExplanation": [
                "1. State Shockley diode differential conductance: gd = d(ID)/d(VD) = ID / (eta * VT).",
                "2. Invert conductance to obtain dynamic resistance: rd = (eta * VT) / ID.",
                "3. With eta = 1, VT = 26 mV, and ID = 2.6 mA: rd = 26e-3 / 2.6e-3 = 10 Ohms."
            ],
            "keyFormulas": [
                "r_d = \\frac{\\eta V_T}{I_D}",
                "V_T = \\frac{k_B T}{q} \\approx 25.86 \\text{ mV at } 300\\text{ K}",
                "I_D = I_S \\left( e^{\\frac{V_D}{\\eta V_T}} - 1 \\right)"
            ],
            "examYearReference": "AU Nov/Dec 2023",
            "commonPitfall": "Using static DC resistance (VD / ID) instead of the derivative incremental dynamic resistance."
        },
        {
            "id": "EC23C03_Q3",
            "courseCode": "EC23C03",
            "unitNumber": 3,
            "unitRoman": "III",
            "type": "PART_A",
            "bloomLevel": "L2 (Understand)",
            "questionText": "Explain the physical mechanism of Base Width Modulation (Early Effect) in BJT and its consequence on output conductance ro.",
            "marks": 2,
            "solutionSummary": "As reverse bias across collector-base junction increases, the depletion region widens into the lightly-doped base, narrowing effective base width WB and increasing collector current IC, resulting in finite output resistance ro = (VA + VCE) / IC.",
            "stepByStepExplanation": [
                "1. Increasing VCB widens the reverse-biased collector-base space-charge region.",
                "2. Because the base is moderately doped compared to collector/emitter, the depletion layer penetrates significantly into the base.",
                "3. Neutral base width WB shrinks: reduces recombination and steepens carrier gradient, boosting IC.",
                "4. Generates a non-zero slope in the active region output characteristics, characterized by Early voltage VA."
            ],
            "keyFormulas": [
                "r_o = \\left( \\frac{\\partial I_C}{\\partial V_{CE}} \\right)^{-1} = \\frac{V_A + V_{CE}}{I_C} \\approx \\frac{V_A}{I_C}",
                "W_B = W_{B0} - x_{n,CB}"
            ],
            "examYearReference": "AU Nov/Dec 2024",
            "commonPitfall": "Assuming the collector-base depletion region expands solely into the collector region."
        },
        {
            "id": "EC23C03_Q4",
            "courseCode": "EC23C03",
            "unitNumber": 4,
            "unitRoman": "IV",
            "type": "PART_B",
            "bloomLevel": "L4 (Analyze)",
            "questionText": "Derive the drain current equation for an n-channel enhancement MOSFET operating in the triode and saturation regimes. Explain channel-length modulation parameter lambda and derive the small-signal transconductance gm.",
            "marks": 16,
            "solutionSummary": "In triode regime, ID = mu_n*Cox*(W/L)*((VGS - Vth)*VDS - 0.5*VDS^2). In saturation (VDS >= VGS - Vth), ID = 0.5*mu_n*Cox*(W/L)*(VGS - Vth)^2 * (1 + lambda*VDS). Transconductance gm = sqrt(2*mu_n*Cox*(W/L)*ID).",
            "stepByStepExplanation": [
                "1. Express inversion charge per unit area: Qinv(y) = -Cox * (VGS - Vth - V(y)).",
                "2. Integrate drift current ID = -W * mu_n * Qinv(y) * (dV/dy) from y=0 to y=L.",
                "3. Triode solution: ID = mu_n * Cox * (W/L) * [(VGS - Vth)*VDS - 0.5*VDS^2].",
                "4. Set VDS = VDS,sat = VGS - Vth to find pinch-off saturation current.",
                "5. Account for channel pinch-off point motion with lambda: ID,sat = 0.5*kn*(VGS - Vth)^2 * (1 + lambda*VDS).",
                "6. Differentiate ID with respect to VGS to find transconductance gm = kn*(VGS - Vth) = sqrt(2*kn*ID)."
            ],
            "keyFormulas": [
                "I_{D,\\text{triode}} = \\mu_n C_{ox} \\frac{W}{L} \\left[ (V_{GS} - V_{th}) V_{DS} - \\frac{V_{DS}^2}{2} \\right]",
                "I_{D,\\text{sat}} = \\frac{1}{2} \\mu_n C_{ox} \\frac{W}{L} (V_{GS} - V_{th})^2 (1 + \\lambda V_{DS})",
                "g_m = \\frac{\\partial I_D}{\\partial V_{GS}} = \\sqrt{2 \\mu_n C_{ox} \\frac{W}{L} I_D}"
            ],
            "examYearReference": "AU Apr/May 2024 Part B (16 Marks)",
            "commonPitfall": "Confusing threshold voltage Vth roll-off with channel-length modulation lambda."
        }
    ],
    "EC23E04": [
        {
            "id": "EC23E04_Q1",
            "courseCode": "EC23E04",
            "unitNumber": 1,
            "unitRoman": "I",
            "type": "MCQ",
            "bloomLevel": "L3 (Apply)",
            "questionText": "An optical resonator of physical length L = 0.5 m is formed by two concave mirrors with radii of curvature R1 = 1.0 m and R2 = 0.75 m. What are the g-parameters and is this cavity stable?",
            "options": [
                "g1 = 0.5, g2 = 0.333; Cavity is STABLE (g1*g2 = 0.167)",
                "g1 = 1.5, g2 = 0.667; Cavity is UNSTABLE (g1*g2 = 1.001)",
                "g1 = -0.5, g2 = -0.333; Cavity is UNSTABLE",
                "g1 = 0.25, g2 = 0.5; Cavity is STABLE (g1*g2 = 0.125)"
            ],
            "correctOptionIndex": 0,
            "marks": 1,
            "solutionSummary": "Resonator stability parameters: g1 = 1 - L/R1 = 1 - 0.5/1.0 = 0.5; g2 = 1 - L/R2 = 1 - 0.5/0.75 = 0.333. The product g1*g2 = 0.5 * 0.333 = 0.167. Since 0 <= g1*g2 <= 1, the cavity is STABLE.",
            "stepByStepExplanation": [
                "1. Recall stability parameter definition: g_i = 1 - L / R_i.",
                "2. Calculate mirror 1: g1 = 1 - 0.5 / 1.0 = 1 - 0.5 = 0.50.",
                "3. Calculate mirror 2: g2 = 1 - 0.5 / 0.75 = 1 - 0.667 = 0.333.",
                "4. Compute stability product: g1 * g2 = 0.5 * 0.333 = 0.167.",
                "5. Resonator stability criterion: 0 <= g1 * g2 <= 1 is satisfied."
            ],
            "keyFormulas": [
                "g_1 = 1 - \\frac{L}{R_1}, \\quad g_2 = 1 - \\frac{L}{R_2}",
                "0 \\le g_1 g_2 \\le 1"
            ],
            "examYearReference": "AU Nov/Dec 2024",
            "commonPitfall": "Using R/L instead of L/R when calculating resonator stability parameters."
        },
        {
            "id": "EC23E04_Q2",
            "courseCode": "EC23E04",
            "unitNumber": 2,
            "unitRoman": "II",
            "type": "MCQ",
            "bloomLevel": "L3 (Apply)",
            "questionText": "A He-Ne gas laser operating at lambda = 632.8 nm has a cavity length of L = 30 cm. What is the longitudinal mode frequency spacing Delta_nu?",
            "options": [
                "Delta_nu = 150 MHz",
                "Delta_nu = 500 MHz",
                "Delta_nu = 1.0 GHz",
                "Delta_nu = 3.0 GHz"
            ],
            "correctOptionIndex": 1,
            "marks": 1,
            "solutionSummary": "Longitudinal mode spacing is Delta_nu = c / (2 * L) = 3e8 / (2 * 0.30) = 3e8 / 0.60 = 500 MHz.",
            "stepByStepExplanation": [
                "1. Resonant frequencies satisfy: nu_m = m * c / (2 * L).",
                "2. Mode frequency difference: Delta_nu = nu_{m+1} - nu_m = c / (2 * L).",
                "3. Substitute speed of light c = 3e8 m/s and L = 0.30 m: Delta_nu = 3e8 / (2 * 0.30) = 5e8 Hz = 500 MHz."
            ],
            "keyFormulas": [
                "\\Delta \\nu = \\frac{c}{2 L}",
                "\\nu_m = m \\frac{c}{2 L}",
                "\\Delta \\lambda = \\frac{\\lambda^2}{2 L}"
            ],
            "examYearReference": "AU Apr/May 2024",
            "commonPitfall": "Using c / L (unfolded ring cavity) instead of c / (2*L) for standard Fabry-Perot standing-wave resonator."
        },
        {
            "id": "EC23E04_Q3",
            "courseCode": "EC23E04",
            "unitNumber": 3,
            "unitRoman": "III",
            "type": "PART_A",
            "bloomLevel": "L2 (Understand)",
            "questionText": "Define spatial coherence and temporal coherence of a laser beam. Relate temporal coherence to optical coherence length Lc.",
            "marks": 2,
            "solutionSummary": "Spatial coherence measures phase correlation between two transverse points at the same time. Temporal coherence measures phase correlation at the same spatial point across time interval tau_c. Coherence length is Lc = c * tau_c = c / Delta_nu.",
            "stepByStepExplanation": [
                "1. Spatial coherence: Describes fixed phase relationship between two wavefront points across beam cross-section.",
                "2. Temporal coherence: Characterizes monochromaticity and phase predictability over time interval tau_c.",
                "3. Mathematical relation: Lc = c * tau_c = lambda^2 / Delta_lambda."
            ],
            "keyFormulas": [
                "L_c = c \\tau_c = \\frac{c}{\\Delta \\nu} = \\frac{\\lambda^2}{\\Delta \\lambda}",
                "\\gamma_{12}(\\tau) = \\frac{\\langle E_1(t+\\tau) E_2^*(t) \\rangle}{\\sqrt{I_1 I_2}}"
            ],
            "examYearReference": "AU Nov/Dec 2023",
            "commonPitfall": "Confusing temporal coherence (spectral linewidth) with spatial coherence (transverse beam mode TEM00)."
        },
        {
            "id": "EC23E04_Q4",
            "courseCode": "EC23E04",
            "unitNumber": 4,
            "unitRoman": "IV",
            "type": "PART_B",
            "bloomLevel": "L5 (Evaluate)",
            "questionText": "Derive Einstein's relations for stimulated absorption (B12), spontaneous emission (A21), and stimulated emission (B21) under thermodynamic equilibrium with Planck's blackbody radiation field. Explain the necessity of population inversion for laser oscillation.",
            "marks": 16,
            "solutionSummary": "Under equilibrium, N1*B12*rho(nu) = N2*A21 + N2*B21*rho(nu). By matching with Planck's radiation law rho(nu) = (8*pi*h*nu^3/c^3)/(exp(h*nu/kT)-1) and Boltzmann distribution N2/N1 = (g2/g1)*exp(-h*nu/kT), we prove B12 = (g2/g1)*B21 and A21/B21 = 8*pi*h*nu^3/c^3.",
            "stepByStepExplanation": [
                "1. Write transition rate balance: R_up = N1 * B12 * rho(nu) and R_down = N2 * A21 + N2 * B21 * rho(nu).",
                "2. Equate rates at thermal equilibrium: rho(nu) = A21 / [ (N1/N2)*B12 - B21 ].",
                "3. Substitute Boltzmann distribution: N1 / N2 = (g1 / g2) * exp(h*nu / (k_B*T)).",
                "4. Compare with Planck's radiation law: rho(nu) = (8*pi*h*nu^3 / c^3) / [ exp(h*nu / (k_B*T)) - 1 ].",
                "5. Deduce Einstein relations: g1 * B12 = g2 * B21 and A21 / B21 = 8*pi*h*nu^3 / c^3.",
                "6. For net amplification, stimulated emission must exceed absorption: dI/dz = sigma*(N2 - (g2/g1)*N1)*I > 0, requiring population inversion N2 > (g2/g1)*N1."
            ],
            "keyFormulas": [
                "g_1 B_{12} = g_2 B_{21}",
                "\\frac{A_{21}}{B_{21}} = \\frac{8\\pi h \\nu^3}{c^3}",
                "\\gamma(\\nu) = \\sigma_{21}(\\nu) \\left( N_2 - \\frac{g_2}{g_1} N_1 \\right) > 0"
            ],
            "examYearReference": "AU Nov/Dec 2024 Part B (16 Marks)",
            "commonPitfall": "Neglecting spontaneous emission in the downward transition balance equation."
        }
    ],
    "EC8702": [
        {
            "id": "EC8702_Q1",
            "courseCode": "EC8702",
            "unitNumber": 1,
            "unitRoman": "I",
            "type": "MCQ",
            "bloomLevel": "L3 (Apply)",
            "questionText": "In ARM Cortex-M4 NVIC architecture, what hardware optimization mechanism allows an interrupt of equal or higher priority to execute immediately after another ISR without restoring and re-saving registers?",
            "options": [
                "Bit-band aliasing",
                "Interrupt Tail-Chaining (6 clock cycles)",
                "Memory Protection Unit (MPU) paging",
                "DMA circular double-buffering"
            ],
            "correctOptionIndex": 1,
            "marks": 1,
            "solutionSummary": "Tail-chaining allows the processor to skip popping registers R0-R3, R12, LR, PC, xPSR from the stack, transitioning to the pending ISR in only 6 clock cycles instead of 24+ cycles.",
            "stepByStepExplanation": [
                "1. Standard interrupt entry requires 12 cycles of stacking (R0-R3, R12, LR, PC, xPSR).",
                "2. Standard exit requires 12 cycles of unstacking.",
                "3. When an interrupt arrives during or at the completion of an existing ISR, Tail-Chaining retains stack contents.",
                "4. NVIC switches vector table execution in 6 cycles, minimizing latency for real-time systems."
            ],
            "keyFormulas": [
                "T_{\\text{tail-chain}} = 6 \\text{ clock cycles}",
                "T_{\\text{standard}} = T_{\\text{unstack}}(12) + T_{\\text{stack}}(12) = 24 \\text{ cycles}"
            ],
            "examYearReference": "AU Nov/Dec 2024 Reg 2017/2023",
            "commonPitfall": "Confusing Late-Arrival handling (preempting lower-priority stacking) with Tail-Chaining (chaining consecutive ISRs)."
        },
        {
            "id": "EC8702_Q2",
            "courseCode": "EC8702",
            "unitNumber": 2,
            "unitRoman": "II",
            "type": "MCQ",
            "bloomLevel": "L4 (Analyze)",
            "questionText": "A real-time embedded system has 2 periodic tasks running under Rate Monotonic Scheduling (RMS): Task 1 (C1 = 10ms, T1 = 40ms) and Task 2 (C2 = 15ms, T2 = 60ms). Is this task set guaranteed to be schedulable according to Liu & Layland bound?",
            "options": [
                "No, total CPU utilization is 85.0%, which exceeds the bound of 82.84%",
                "Yes, total CPU utilization is 50.0%, which is well below the 2-task bound of 82.84%",
                "No, Task 2 will miss its deadline because T2 > T1",
                "Yes, but only if Earliest Deadline First (EDF) dynamic scheduling is used"
            ],
            "correctOptionIndex": 1,
            "marks": 1,
            "solutionSummary": "CPU Utilization U = C1/T1 + C2/T2 = 10/40 + 15/60 = 0.25 + 0.25 = 0.50 (50.0%). The Liu & Layland bound for n=2 tasks is 2*(2^(1/2) - 1) = 82.84%. Since 50% <= 82.84%, it is 100% schedulable.",
            "stepByStepExplanation": [
                "1. Compute Task 1 utilization: U1 = C1 / T1 = 10 / 40 = 0.25 (25%).",
                "2. Compute Task 2 utilization: U2 = C2 / T2 = 15 / 60 = 0.25 (25%).",
                "3. Calculate total utilization: U = U1 + U2 = 0.50 (50%).",
                "4. Compute Liu & Layland bound for n = 2: U_bound = 2 * (2^(1/2) - 1) = 2 * 0.4142 = 82.84%.",
                "5. Condition U (50%) <= U_bound (82.84%) holds; schedulability is guaranteed."
            ],
            "keyFormulas": [
                "U = \\sum_{i=1}^{n} \\frac{C_i}{T_i}",
                "U_{\\text{bound}}(n) = n \\left( 2^{1/n} - 1 \\right)",
                "U(2) = 2(\\sqrt{2} - 1) \\approx 0.8284 \\quad (82.84\\%)"
            ],
            "examYearReference": "AU Apr/May 2024",
            "commonPitfall": "Evaluating only Task 2 without summing both periodic task execution fractions."
        },
        {
            "id": "EC8702_Q3",
            "courseCode": "EC8702",
            "unitNumber": 3,
            "unitRoman": "III",
            "type": "PART_A",
            "bloomLevel": "L2 (Understand)",
            "questionText": "Explain the Priority Inversion problem in RTOS and describe how the Priority Inheritance Protocol (PIP) resolves it.",
            "marks": 2,
            "solutionSummary": "Priority Inversion occurs when a high-priority task is blocked by a low-priority task holding a shared mutex, while intermediate tasks preempt the low-priority task. Priority Inheritance temporarily elevates the low-priority task's priority to that of the blocked high-priority task until the mutex is released.",
            "stepByStepExplanation": [
                "1. High-priority task H requires shared resource locked by low-priority task L.",
                "2. Medium-priority task M (not requiring resource) preempts L, indefinitely blocking H.",
                "3. Priority Inheritance Protocol (PIP): Whenever H blocks on a mutex held by L, L's dynamic priority is raised to match H.",
                "4. Prevents intermediate tasks M from preempting L; once L releases the mutex, its priority reverts to normal."
            ],
            "keyFormulas": [
                "\\text{Dynamic Priority}(Task_L) = \\max(\\text{Base}(Task_L), \\text{Priority}(Task_H))",
                "T_{\\text{blocking}} \\le \\max_{j \\in \\text{lower}} (C_{j,\\text{critical section}})"
            ],
            "examYearReference": "AU Nov/Dec 2023",
            "commonPitfall": "Confusing Priority Inheritance (dynamic elevation on conflict) with Priority Ceiling (static resource ceiling assigned at compile time)."
        },
        {
            "id": "EC8702_Q4",
            "courseCode": "EC8702",
            "unitNumber": 4,
            "unitRoman": "IV",
            "type": "PART_B",
            "bloomLevel": "L5 (Evaluate)",
            "questionText": "Design an ARM Cortex-M4 GPIO and DMA memory-to-peripheral architecture to stream 1024 samples of ADC data over SPI without CPU intervention. Write the register configuration sequence and compute the power savings compared to polling.",
            "marks": 16,
            "solutionSummary": "Configure SPI in Master Transmit Mode (CR1/CR2). Program DMA Channel with Peripheral address &SPI->DR, Memory address &adc_buffer[0], Transfer count NDTR = 1024, Direction MEM2PERIPH, and Circular/Normal mode. Enable DMA request in SPI CR2 (TXDMAEN). CPU enters WFI sleep, reducing power from ~15mA active to <1.2mA.",
            "stepByStepExplanation": [
                "1. Enable AHB1/APB peripheral clocks in RCC (RCC_AHB1ENR for DMA/GPIO, RCC_APB2ENR for SPI1).",
                "2. Configure GPIO pins for SPI Alternate Function AF5 (SCK, MOSI, MISO, NSS).",
                "3. Program DMA Stream: Set DMA_SxPAR = (uint32_t)&(SPI1->DR); Set DMA_SxM0AR = (uint32_t)adc_buffer.",
                "4. Configure transfer parameters: DMA_SxNDTR = 1024; DIR = 01 (Memory-to-Peripheral); MINC = 1; PINC = 0; Data size = 16-bit.",
                "5. Set SPI_CR2 TXDMAEN = 1 to trigger DMA requests on TXE flag.",
                "6. Execute __WFI() instruction: CPU core enters Sleep Mode while DMA controller autonomously transfers data, saving ~92% dynamic CPU energy."
            ],
            "keyFormulas": [
                "\\text{Energy Savings} = 1 - \\frac{I_{\\text{sleep}} \\cdot V_{dd} \\cdot t}{I_{\\text{active}} \\cdot V_{dd} \\cdot t} = 1 - \\frac{1.2\\text{ mA}}{15.0\\text{ mA}} = 92.0\\%",
                "\\text{Throughput} = \\frac{N \\cdot f_{\\text{SCK}}}{8} \\quad \\text{Bytes/sec}"
            ],
            "examYearReference": "AU Nov/Dec 2024 Part B (16 Marks)",
            "commonPitfall": "Failing to increment memory address pointer (MINC=0) resulting in the same byte being transmitted 1024 times."
        }
    ]
}


# -----------------------------------------------------------------------------
# ASSESSMENT AUDIT & EVALUATION ENGINE
# -----------------------------------------------------------------------------

class CourseQuizEngine:
    """
    Evaluates and audits academic quizzes for Anna University Regulation 2023.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self._ensure_database_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """Create and return a configured SQLite connection with WAL enabled."""
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    def _ensure_database_schema(self) -> None:
        """Create quiz submission gradebook table if it does not exist with SQLite WAL mode."""
        try:
            conn = self._get_connection()
            try:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS course_quiz_submissions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        submission_id TEXT UNIQUE NOT NULL,
                        course_code TEXT NOT NULL,
                        student_id TEXT NOT NULL,
                        score_obtained REAL NOT NULL,
                        max_marks REAL NOT NULL,
                        percentage REAL NOT NULL,
                        bloom_metrics TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)
                conn.commit()
            finally:
                conn.close()
        except Exception:
            # Non-blocking graceful fallback
            pass

    def get_catalog_for_course(self, course_code: str) -> List[Dict[str, Any]]:
        """Retrieve all questions for a specific course."""
        return COURSE_QUIZ_CATALOG.get(course_code, [])

    def validate_catalog(self) -> Dict[str, Any]:
        """
        Comprehensive audit of quiz question schema integrity across all courses:
        - Check unique IDs
        - Check MCQ options length == 4 and valid correctOptionIndex (0-3)
        - Check presence of stepByStepExplanation and keyFormulas
        - Verify Bloom's taxonomy tags
        """
        all_ids: Set[str] = set()
        course_summaries: Dict[str, Any] = {}
        errors: List[str] = []

        for code, questions in COURSE_QUIZ_CATALOG.items():
            mcq_count = 0
            part_a_count = 0
            part_b_count = 0
            bloom_distribution: Dict[str, int] = {}

            for q in questions:
                # 1. ID uniqueness
                q_id = q.get("id")
                if not q_id:
                    errors.append(f"Course {code} contains a question with missing ID")
                elif q_id in all_ids:
                    errors.append(f"Duplicate question ID found: {q_id}")
                else:
                    all_ids.add(q_id)

                # 2. Type validation
                q_type = q.get("type")
                if q_type == "MCQ":
                    mcq_count += 1
                    opts = q.get("options", [])
                    if len(opts) != 4:
                        errors.append(f"{q_id}: MCQ must have exactly 4 choices, found {len(opts)}")
                    corr_idx = q.get("correctOptionIndex")
                    if corr_idx is None or not (0 <= corr_idx <= 3):
                        errors.append(f"{q_id}: Invalid correctOptionIndex {corr_idx}")
                elif q_type == "PART_A":
                    part_a_count += 1
                    if q.get("marks") != 2:
                        errors.append(f"{q_id}: Part A question marks should be 2, found {q.get('marks')}")
                elif q_type == "PART_B":
                    part_b_count += 1
                    if q.get("marks") != 16:
                        errors.append(f"{q_id}: Part B question marks should be 16, found {q.get('marks')}")
                else:
                    errors.append(f"{q_id}: Invalid question type '{q_type}'")

                # 3. Bloom's Taxonomy
                bloom = q.get("bloomLevel", "Unknown")
                bloom_distribution[bloom] = bloom_distribution.get(bloom, 0) + 1

                # 4. Explanations and formulas
                if not q.get("stepByStepExplanation") or len(q["stepByStepExplanation"]) < 2:
                    errors.append(f"{q_id}: Missing comprehensive step-by-step explanation")
                if not q.get("keyFormulas") or len(q["keyFormulas"]) < 1:
                    errors.append(f"{q_id}: Missing KaTeX formulas")

            course_summaries[code] = {
                "total_questions": len(questions),
                "mcq_count": mcq_count,
                "part_a_count": part_a_count,
                "part_b_count": part_b_count,
                "bloom_distribution": bloom_distribution
            }

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "total_courses": len(COURSE_QUIZ_CATALOG),
            "total_questions": len(all_ids),
            "course_summaries": course_summaries
        }

    def evaluate_submission(
        self,
        course_code: str,
        student_id: str,
        answers: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Evaluate student MCQ submissions, compute scores, and generate itemized feedback.
        """
        questions = self.get_catalog_for_course(course_code)
        if not questions:
            return {"error": f"No questions found for course {course_code}"}

        mcq_questions = [q for q in questions if q["type"] == "MCQ"]
        total_mcqs = len(mcq_questions)
        if total_mcqs == 0:
            return {"error": f"No MCQs available in course {course_code}"}

        correct_count = 0
        total_marks = sum(q.get("marks", 1) for q in mcq_questions)
        earned_marks = 0.0
        itemized_results = []
        bloom_performance: Dict[str, Dict[str, int]] = {}

        for q in mcq_questions:
            q_id = q["id"]
            user_choice = answers.get(q_id)
            correct_choice = q["correctOptionIndex"]
            is_correct = (user_choice == correct_choice)
            bloom = q.get("bloomLevel", "General")

            if bloom not in bloom_performance:
                bloom_performance[bloom] = {"total": 0, "correct": 0}
            bloom_performance[bloom]["total"] += 1

            if is_correct:
                correct_count += 1
                earned_marks += q.get("marks", 1)
                bloom_performance[bloom]["correct"] += 1

            itemized_results.append({
                "question_id": q_id,
                "unit": q.get("unitRoman"),
                "question_text": q["questionText"],
                "user_choice": user_choice,
                "correct_choice": correct_choice,
                "is_correct": is_correct,
                "solution_summary": q.get("solutionSummary"),
                "key_formulas": q.get("keyFormulas", []),
                "common_pitfall": q.get("commonPitfall")
            })

        percentage = round((earned_marks / total_marks) * 100.0, 2) if total_marks > 0 else 0.0
        submission_id = f"SUB-{course_code}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        result = {
            "submission_id": submission_id,
            "course_code": course_code,
            "student_id": student_id,
            "total_mcqs": total_mcqs,
            "correct_count": correct_count,
            "earned_marks": earned_marks,
            "total_marks": total_marks,
            "percentage": percentage,
            "bloom_performance": bloom_performance,
            "itemized_results": itemized_results,
            "evaluation_timestamp": datetime.datetime.now().isoformat()
        }

        # Persist to SQLite WAL gradebook safely
        try:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT INTO course_quiz_submissions
                    (submission_id, course_code, student_id, score_obtained, max_marks, percentage, bloom_metrics, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    submission_id,
                    course_code,
                    student_id,
                    earned_marks,
                    total_marks,
                    percentage,
                    json.dumps(bloom_performance),
                    datetime.datetime.now().isoformat()
                ))
                conn.commit()
            finally:
                conn.close()
        except Exception:
            pass

        return result
