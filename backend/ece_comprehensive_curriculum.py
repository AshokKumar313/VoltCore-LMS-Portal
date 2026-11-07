"""
========================================================================================
VoltCore Apex Academia - Comprehensive ECE Curriculum Catalog (14 Disciplines)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/ece_comprehensive_curriculum.py
Platform Lead & Systems Architect: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Disciplines Cataloged:
  1. Circuit Analysis & Network Theory (EC23C01)
  2. Semiconductor Physics & Solid-State Devices (EC23C02)
  3. Electronic Devices & Circuits (EC23C03)
  4. Analog Electronics & Linear Integrated Circuits (EC23C05)
  5. Digital Electronics & Switching Theory (EC23C06)
  6. Signals & Systems (EC23C04)
  7. Control Systems Engineering (EC23C07)
  8. Digital Signal Processing (EC23S01)
  9. Analog & Digital Communication Systems (EC23C08)
 10. Advanced Embedded Systems Architecture (EC8702)
 11. STM32 Bare-Metal & RTOS Architecture (STM32-ACADEMY)
 12. ESP32 IoT Edge Node & Low-Power Telemetry (IOT8701)
 13. Verilog HDL & FPGA Digital System Design (HDL6001)
 14. VLSI Physical Design & ASIC Architecture (VLSI7001)
========================================================================================
"""

from typing import Dict, Any, List

COMPREHENSIVE_ECE_CURRICULUM: Dict[str, Dict[str, Any]] = {
    # 1. CIRCUIT ANALYSIS
    "EC23C01": {
        "code": "EC23C01",
        "title": "Circuit Analysis and Network Theory",
        "descriptive_title": "Linear Circuit Analysis and Dynamic Network Synthesis",
        "short_title": "Circuit Analysis",
        "slug": "circuit-analysis",
        "semester": 2,
        "credits": 4,
        "ltp": "3-1-0",
        "category": "Professional Core (PCC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "cyan",
        "theme_color": "#06B6D4",
        "icon": "⚡",
        "prerequisites": ["PH23C01", "MA23C01"],
        "corequisites": [],
        "cos_count": 5,
        "simulation_platform": "Non-Linear MNA Solver",
        "simulation_component": "MnaAnalogWorkbench",
        "total_lab_hours": 36,
        "course_outcomes": [
            {"id": "CO1", "description": "Apply Kirchhoff's laws and nodal/mesh Modified Nodal Analysis (MNA) to DC resistive networks.", "bloom_level": "L3 (Apply)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO2", "description": "Synthesize Thevenin, Norton, and Maximum Power Transfer equivalent circuits for multi-source topologies.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2", "PO3"], "mapped_psos": ["PSO1"]},
            {"id": "CO3", "description": "Formulate state-variable differential equations governing second-order transient RLC networks.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO4", "description": "Evaluate sinusoidal steady-state AC phasor impedances, resonance, and quality factor Q in tuned tank circuits.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2", "PO4"], "mapped_psos": ["PSO1"]},
            {"id": "CO5", "description": "Design passive Butterworth and Chebyshev two-port filter networks with specified attenuation cutoff frequencies.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO3", "PO5"], "mapped_psos": ["PSO2"]}
        ],
        "mathematical_derivations": [
            {
                "topic": "Parallel & Series RLC Resonance & Tank Quality Factor",
                "formula_latex": r"Q = \frac{\omega_0 L}{R} = \frac{1}{\omega_0 R C} = \frac{f_0}{\text{BW}}",
                "derivation_steps": [
                    "At resonance frequency omega_0 = 1 / sqrt(L*C), inductive and capacitive reactances cancel out (X_L = X_C).",
                    "The net impedance becomes purely resistive, yielding unity power factor (cos(phi) = 1).",
                    "Quality factor Q quantifies the ratio of stored reactive energy to dissipated active energy per radian.",
                    "Half-power bandwidth BW relates to damping ratio zeta: BW = f_0 / Q = 2 * zeta * f_0."
                ],
                "parameters": [
                    {"symbol": "Q", "unit": "dimensionless", "definition": "Resonance quality factor"},
                    {"symbol": "omega_0", "unit": "rad/s", "definition": "Natural undamped angular frequency"},
                    {"symbol": "BW", "unit": "Hz", "definition": "-3dB half-power bandwidth"}
                ]
            }
        ],
        "worked_examples": [
            {
                "title": "RLC Series Resonant Bandpass Filter Design",
                "problem_statement": "Design a series RLC tank circuit resonant at f_0 = 100 kHz with a -3dB bandwidth of BW = 5 kHz using an inductor L = 100 uH. Calculate required R and C.",
                "step_by_step_solution": [
                    "Step 1: Calculate quality factor Q = f_0 / BW = 100 kHz / 5 kHz = 20.0.",
                    "Step 2: Angular frequency omega_0 = 2 * pi * 100e3 = 628,318.53 rad/s.",
                    "Step 3: Resonant capacitance C = 1 / (omega_0^2 * L) = 1 / (3.9478e11 * 100e-6) = 25.33 nF.",
                    "Step 4: Damping resistance R = omega_0 * L / Q = (628318.53 * 100e-6) / 20 = 3.1416 Ohms."
                ],
                "verified_output": "R = 3.14 Ohms, C = 25.33 nF, Q = 20.0"
            }
        ],
        "simulation_activities": [
            {
                "lab_id": "CIR_LAB_01",
                "title": "Non-Linear MNA Transient Sweep & Resonance Verification",
                "component": "MnaAnalogWorkbench",
                "instructions": "Construct series RLC netlist with R=3.14, L=100u, C=25.33n. Execute AC frequency sweep from 80kHz to 120kHz and verify 100kHz peak and 5kHz bandwidth on Virtual DSO Channel A.",
                "expected_telemetry": {"f_res_khz": 100.0, "v_peak_v": 1.0, "bandwidth_khz": 5.0}
            }
        ],
        "assessment_questions": [
            {
                "id": "CIR_Q1",
                "bloom_level": "L3 (Apply)",
                "question": "In a series RLC circuit, if inductance L is doubled and capacitance C is halved, what happens to the resonant frequency omega_0 and quality factor Q?",
                "options": [
                    "omega_0 remains unchanged, Q doubles",
                    "omega_0 doubles, Q is halved",
                    "Both omega_0 and Q remain unchanged",
                    "omega_0 is halved, Q quadruples"
                ],
                "correct_index": 0,
                "explanation": "omega_0 = 1 / sqrt(2L * C/2) = 1 / sqrt(LC), unchanged. Q = (1/R) * sqrt(2L / (C/2)) = (1/R) * sqrt(4L/C) = 2 * Q_old."
            }
        ]
    },

    # 2. SEMICONDUCTOR PHYSICS
    "EC23C02": {
        "code": "EC23C02",
        "title": "Semiconductor Physics and Solid-State Devices",
        "descriptive_title": "Quantum Mechanics, Band Theory, and Carrier Transport in Crystalline Silicon",
        "short_title": "Semiconductor Physics",
        "slug": "semiconductor-physics",
        "semester": 3,
        "credits": 3,
        "ltp": "3-0-0",
        "category": "Professional Core (PCC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "amber",
        "theme_color": "#F59E0B",
        "icon": "⚛️",
        "prerequisites": ["PH23C01", "MA23C01"],
        "corequisites": [],
        "cos_count": 5,
        "simulation_platform": "Semiconductor Physics Explorer",
        "simulation_component": "SemiconductorPhysicsWorkbench",
        "total_lab_hours": 30,
        "course_outcomes": [
            {"id": "CO1", "description": "Formulate energy band diagrams and effective density of states (Nc, Nv) in direct and indirect bandgap crystals.", "bloom_level": "L3 (Apply)", "mapped_pos": ["PO1"], "mapped_psos": ["PSO1"]},
            {"id": "CO2", "description": "Calculate intrinsic carrier concentration ni(T) as a function of temperature and bandgap narrowing.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO3", "description": "Evaluate Fermi-Dirac distribution function and calculate extrinsic Fermi level placement under donor and acceptor doping.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO4", "description": "Derive carrier drift and diffusion current densities governed by Einstein's mobility-diffusivity relation.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2", "PO3"], "mapped_psos": ["PSO1"]},
            {"id": "CO5", "description": "Model space charge width, built-in potential Vbi, and junction breakdown mechanisms in PN junctions.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO2", "PO3"], "mapped_psos": ["PSO2"]}
        ],
        "mathematical_derivations": [
            {
                "topic": "Einstein Relation & Total Carrier Current Density",
                "formula_latex": r"J_{total} = q (n \mu_n + p \mu_p) E + q D_n \frac{dn}{dx} - q D_p \frac{dp}{dx}, \quad \frac{D_n}{\mu_n} = \frac{k_B T}{q} = V_T",
                "derivation_steps": [
                    "Drift current density arises from applied electrostatic field E: J_drift = q * (n*mu_n + p*mu_p) * E.",
                    "Diffusion current density arises from thermal spatial concentration gradient: J_diff = q * D_n * (dn/dx) - q * D_p * (dp/dx).",
                    "Under thermal equilibrium with zero external current, drift and diffusion balance out, yielding Einstein's relation: D / mu = k_B * T / q."
                ],
                "parameters": [
                    {"symbol": "V_T", "unit": "V", "definition": "Thermal voltage (25.86 mV at 300K)"},
                    {"symbol": "mu_n", "unit": "cm^2/(V*s)", "definition": "Electron drift mobility (approx 1350 in Si)"},
                    {"symbol": "D_n", "unit": "cm^2/s", "definition": "Electron diffusion coefficient (approx 35 in Si)"}
                ]
            }
        ],
        "worked_examples": [
            {
                "title": "Extrinsic Silicon Fermi Level Position Calculation",
                "problem_statement": "An n-type silicon sample at T = 300 K is doped with phosphorus donors at N_D = 10^16 cm^-3. Given N_c = 2.8e19 cm^-3, calculate the position of the Fermi level E_F relative to the conduction band edge E_c.",
                "step_by_step_solution": [
                    "Step 1: Thermal voltage V_T = k_B * T / q = 0.02586 eV.",
                    "Step 2: Under complete ionization, electron density n_0 = N_D = 1e16 cm^-3.",
                    "Step 3: Carrier statistics formula: n_0 = N_c * exp(-(E_c - E_F) / (k_B * T)).",
                    "Step 4: Solve for (E_c - E_F) = k_B * T * ln(N_c / N_D) = 0.02586 * ln(2.8e19 / 1e16) = 0.02586 * ln(2800) = 0.02586 * 7.937 = 0.205 eV."
                ],
                "verified_output": "E_c - E_F = 0.205 eV below conduction band edge"
            }
        ],
        "simulation_activities": [
            {
                "lab_id": "SEMI_LAB_01",
                "title": "Fermi-Dirac Distribution & Thermal Carrier Sweep",
                "component": "SemiconductorPhysicsWorkbench",
                "instructions": "Vary temperature from 200 K to 500 K and plot intrinsic carrier concentration ni(T). Verify that ni doubles approximately every 11 degrees Kelvin in silicon.",
                "expected_telemetry": {"ni_300k": 1.5e10, "bandgap_si_ev": 1.12}
            }
        ],
        "assessment_questions": [
            {
                "id": "SEMI_Q1",
                "bloom_level": "L4 (Analyze)",
                "question": "At what energy level is the Fermi-Dirac occupation probability exactly equal to 50% at all non-zero temperatures?",
                "options": [
                    "At the Fermi energy E = E_F",
                    "At the conduction band edge E = E_c",
                    "At the valence band edge E = E_v",
                    "At the midpoint of the forbidden gap E = E_i"
                ],
                "correct_index": 0,
                "explanation": "f(E_F) = 1 / (1 + exp((E_F - E_F)/(k_B*T))) = 1 / (1 + exp(0)) = 1 / 2 = 50%."
            }
        ]
    },

    # 4. ANALOG ELECTRONICS
    "EC23C05": {
        "code": "EC23C05",
        "title": "Analog Electronics and Linear Integrated Circuits",
        "descriptive_title": "Op-Amp Theory, Active Filters, Differential Amplifiers, and Precision Linear ICs",
        "short_title": "Analog Electronics",
        "slug": "analog-electronics",
        "semester": 4,
        "credits": 4,
        "ltp": "3-0-2",
        "category": "Professional Core (PCC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "indigo",
        "theme_color": "#6366F1",
        "icon": "📻",
        "prerequisites": ["EC23C03", "EC23C01"],
        "corequisites": [],
        "cos_count": 5,
        "simulation_platform": "Virtual Oscilloscope & MNA Engine",
        "simulation_component": "VirtualOscilloscope",
        "total_lab_hours": 45,
        "course_outcomes": [
            {"id": "CO1", "description": "Analyze BJT and MOSFET differential amplifier CMRR, tail current source biasing, and differential-to-single-ended conversion.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO2", "description": "Formulate high-frequency small-signal Miller effect frequency response and gain-bandwidth product (GBW).", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO3", "description": "Design four feedback topologies (series-shunt, shunt-series) and evaluate input/output impedance modifications.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO2", "PO3"], "mapped_psos": ["PSO1"]},
            {"id": "CO4", "description": "Design sinusoidal oscillators satisfying the Barkhausen criterion (Wien Bridge, Colpitts, Hartley).", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO3", "PO4"], "mapped_psos": ["PSO2"]},
            {"id": "CO5", "description": "Synthesize second-order Sallen-Key and Multiple Feedback active low-pass, high-pass, and bandpass filters.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO3", "PO5"], "mapped_psos": ["PSO2"]}
        ],
        "mathematical_derivations": [
            {
                "topic": "Sallen-Key Active Lowpass Filter Transfer Function & Quality Factor",
                "formula_latex": r"H(s) = \frac{K \omega_0^2}{s^2 + \frac{\omega_0}{Q} s + \omega_0^2}, \quad \omega_0 = \frac{1}{\sqrt{R_1 R_2 C_1 C_2}}, \quad Q = \frac{\sqrt{R_1 R_2 C_1 C_2}}{R_1 C_2 + R_2 C_2 + R_1 C_1 (1 - K)}",
                "derivation_steps": [
                    "Apply KCL at node Vx (between R1 and R2) and node Vy (non-inverting op-amp input).",
                    "Op-amp non-inverting gain K = 1 + R_f / R_1.",
                    "Equate node equations to standard second-order denominator form: s^2 + (omega_0/Q)*s + omega_0^2.",
                    "For maximally flat Butterworth response, set damping ratio zeta = 1 / sqrt(2) = 0.707, corresponding to Q = 0.707."
                ],
                "parameters": [
                    {"symbol": "K", "unit": "V/V", "definition": "Passband non-inverting voltage gain"},
                    {"symbol": "omega_0", "unit": "rad/s", "definition": "Cutoff angular corner frequency"},
                    {"symbol": "Q", "unit": "dimensionless", "definition": "Filter quality factor determining peaking"}
                ]
            }
        ],
        "worked_examples": [
            {
                "title": "Second-Order Butterworth Lowpass Sallen-Key Design",
                "problem_statement": "Design an active Butterworth lowpass filter with cutoff frequency f_c = 10 kHz and unity passband gain (K = 1). Choose C2 = 1 nF.",
                "step_by_step_solution": [
                    "Step 1: For equal-resistor design (R1 = R2 = R) and Butterworth Q = 1/sqrt(2) = 0.707:",
                    "Step 2: Capacitance ratio must satisfy C1 = 2 * C2 = 2 * 1 nF = 2 nF.",
                    "Step 3: Angular frequency omega_0 = 2 * pi * 10,000 = 62,831.85 rad/s.",
                    "Step 4: R = 1 / (omega_0 * sqrt(C1 * C2)) = 1 / (62831.85 * sqrt(2e-9 * 1e-9)) = 1 / (62831.85 * 1.4142e-9) = 11,254 Ohms = 11.25 kOhms."
                ],
                "verified_output": "R1 = R2 = 11.25 kOhms, C1 = 2 nF, C2 = 1 nF, Cutoff = 10.0 kHz"
            }
        ],
        "simulation_activities": [
            {
                "lab_id": "ANLG_LAB_01",
                "title": "BJT Differential Pair CMRR and Common-Mode Rejection Sweep",
                "component": "MnaAnalogWorkbench",
                "instructions": "Inject common-mode signal Vin_cm = 1V, 1kHz into both differential inputs. Measure common-mode gain A_cm, then inject differential signal and compute CMRR = 20*log10(A_d / A_cm). Target CMRR > 80 dB.",
                "expected_telemetry": {"cmrr_db": 84.5, "ad_db": 42.0, "acm_db": -42.5}
            }
        ],
        "assessment_questions": [
            {
                "id": "ANLG_Q1",
                "bloom_level": "L4 (Analyze)",
                "question": "What is the primary physical reason an active tail current mirror provides significantly higher CMRR in a differential pair compared to a passive tail resistor?",
                "options": [
                    "The current mirror provides extremely high dynamic AC output resistance (r_o)",
                    "The current mirror doubles the transconductance g_m of input transistors",
                    "The current mirror eliminates the need for negative feedback",
                    "The current mirror removes thermal noise completely"
                ],
                "correct_index": 0,
                "explanation": "Common-mode gain A_cm is inversely proportional to tail resistance R_tail. An active current source has dynamic AC resistance r_o = V_A / I_tail in the megaohm range, suppressing A_cm and maximizing CMRR."
            }
        ]
    },

    # 5. DIGITAL ELECTRONICS
    "EC23C06": {
        "code": "EC23C06",
        "title": "Digital Electronics and Switching Theory",
        "descriptive_title": "Boolean Algebra, Logic Synthesis, Synchronous Sequential Machines, and CMOS Gates",
        "short_title": "Digital Electronics",
        "slug": "digital-electronics",
        "semester": 3,
        "credits": 4,
        "ltp": "3-0-2",
        "category": "Professional Core (PCC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "emerald",
        "theme_color": "#10B981",
        "icon": "💻",
        "prerequisites": ["EC23C01"],
        "corequisites": [],
        "cos_count": 5,
        "simulation_platform": "Digital Logic Simulator & K-Map Engine",
        "simulation_component": "DigitalElectronicsHub",
        "total_lab_hours": 45,
        "course_outcomes": [
            {"id": "CO1", "description": "Minimize complex multi-variable Boolean expressions using Karnaugh maps and Quine-McCluskey tabular optimization.", "bloom_level": "L3 (Apply)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO2", "description": "Design modular combinational arithmetic modules (Carry-Lookahead Adders, Barrel Shifters, Encoders, Multipliers).", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO2", "PO3"], "mapped_psos": ["PSO1"]},
            {"id": "CO3", "description": "Synthesize Moore and Mealy synchronous finite state machines (FSM) with setup/hold timing margin verification.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO3", "PO4"], "mapped_psos": ["PSO2"]},
            {"id": "CO4", "description": "Formulate CMOS static transfer characteristics, noise margins (NMH, NML), and propagation delays.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO5", "description": "Implement programmable logic architectures (ROM, PLA, PAL, CPLD) for complex switching algorithms.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO3", "PO5"], "mapped_psos": ["PSO2"]}
        ],
        "mathematical_derivations": [
            {
                "topic": "Synchronous Flip-Flop Setup/Hold Timing Constraints",
                "formula_latex": r"T_{clk} \ge t_{cq,max} + t_{comb,max} + t_{setup}, \quad t_{cq,min} + t_{comb,min} \ge t_{hold}",
                "derivation_steps": [
                    "Setup time constraint: Data must arrive at the capturing flip-flop input at least t_setup before the next active clock edge.",
                    "Maximum operational frequency: f_max = 1 / (t_cq,max + t_comb,max + t_setup).",
                    "Hold time constraint: Data launched by the current clock edge must not contaminate the capturing flip-flop before t_hold has elapsed.",
                    "Hold timing depends solely on minimum propagation paths and is independent of clock cycle period T_clk."
                ],
                "parameters": [
                    {"symbol": "T_clk", "unit": "ns", "definition": "Clock period"},
                    {"symbol": "t_cq", "unit": "ns", "definition": "Clock-to-Q output propagation delay of launching flip-flop"},
                    {"symbol": "t_comb", "unit": "ns", "definition": "Combinational logic path delay between flip-flops"},
                    {"symbol": "t_setup", "unit": "ns", "definition": "Required data setup time before capturing edge"},
                    {"symbol": "t_hold", "unit": "ns", "definition": "Required data hold time after capturing edge"}
                ]
            }
        ],
        "worked_examples": [
            {
                "title": "Maximum Clock Frequency and Timing Margin Verification",
                "problem_statement": "A synchronous register-to-register path has t_cq,max = 1.2 ns, t_cq,min = 0.8 ns, combinational logic delay t_comb between 2.5 ns and 4.8 ns, t_setup = 0.6 ns, and t_hold = 0.5 ns. Calculate maximum clock frequency f_max and verify hold time slack.",
                "step_by_step_solution": [
                    "Step 1: Calculate minimum clock period: T_clk_min = t_cq,max + t_comb,max + t_setup = 1.2 + 4.8 + 0.6 = 6.6 ns.",
                    "Step 2: Calculate maximum frequency f_max = 1 / T_clk_min = 1 / 6.6e-9 = 151.52 MHz.",
                    "Step 3: Check hold constraint: minimum path = t_cq,min + t_comb,min = 0.8 + 2.5 = 3.3 ns.",
                    "Step 4: Hold slack = 3.3 ns - t_hold = 3.3 - 0.5 = +2.8 ns (Positive slack: NO hold violation)."
                ],
                "verified_output": "f_max = 151.52 MHz, Hold Slack = +2.8 ns (Safe)"
            }
        ],
        "simulation_activities": [
            {
                "lab_id": "DIGI_LAB_01",
                "title": "4-Variable Karnaugh Map Truth Table Minimization",
                "component": "DigitalElectronicsHub",
                "instructions": "Input minterms m(0, 2, 5, 7, 8, 10, 13, 15). Generate canonical SOP and POS. Verify minimal expression output using the interactive Boolean AST solver.",
                "expected_telemetry": {"minimal_sop": "B'D' + BD", "prime_implicants_count": 2}
            }
        ],
        "assessment_questions": [
            {
                "id": "DIGI_Q1",
                "bloom_level": "L4 (Analyze)",
                "question": "If a synchronous circuit suffers from a hold time violation on a critical path, how can it be repaired without lowering the system clock frequency?",
                "options": [
                    "Insert delay buffers in the data path between the launching and capturing flip-flops",
                    "Increase the clock period T_clk",
                    "Replace the capturing flip-flop with a slower device",
                    "Reduce the supply voltage V_DD"
                ],
                "correct_index": 0,
                "explanation": "Hold time violations depend exclusively on the minimum data path delay (t_cq,min + t_comb,min >= t_hold) and are independent of clock period T_clk. Adding buffer delays increases t_comb,min, satisfying the hold constraint."
            }
        ]
    },

    # 6. SIGNALS & SYSTEMS
    "EC23C04": {
        "code": "EC23C04",
        "title": "Signals and Systems",
        "descriptive_title": "Continuous & Discrete Time Linear Time-Invariant Systems, Transforms, and Sampling",
        "short_title": "Signals & Systems",
        "slug": "signals-and-systems",
        "semester": 3,
        "credits": 4,
        "ltp": "3-1-0",
        "category": "Professional Core (PCC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "teal",
        "theme_color": "#14B8A6",
        "icon": "📈",
        "prerequisites": ["MA23C01"],
        "corequisites": [],
        "cos_count": 5,
        "simulation_platform": "Engineering Mathematics Studio",
        "simulation_component": "MathStudioHub",
        "total_lab_hours": 36,
        "course_outcomes": [
            {"id": "CO1", "description": "Classify continuous and discrete signals and evaluate LTI system convolution integrals and sums.", "bloom_level": "L3 (Apply)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO2", "description": "Synthesize continuous-time Fourier series and Fourier transforms (CTFT) with spectral magnitude/phase plots.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO3", "description": "Apply Laplace transforms to evaluate system transfer functions, stability, and causality via pole-zero ROCs.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2", "PO3"], "mapped_psos": ["PSO1"]},
            {"id": "CO4", "description": "Analyze Nyquist-Shannon sampling theorem, bandlimited reconstruction, and spectral aliasing folding.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2", "PO4"], "mapped_psos": ["PSO1"]},
            {"id": "CO5", "description": "Formulate discrete-time Z-transforms and determine digital filter stability from unit-circle pole containment.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO2", "PO3"], "mapped_psos": ["PSO2"]}
        ],
        "mathematical_derivations": [
            {
                "topic": "Z-Transform Stability Boundary & Bilinear Frequency Warping",
                "formula_latex": r"X(z) = \sum_{n=-\infty}^{\infty} x[n] z^{-n}, \quad s = \frac{2}{T_s} \frac{1 - z^{-1}}{1 + z^{-1}}, \quad \omega_a = \frac{2}{T_s} \tan\left(\frac{\omega_d T_s}{2}\right)",
                "derivation_steps": [
                    "An LTI discrete system is bounded-input bounded-output (BIBO) stable if and only if the Region of Convergence (ROC) contains the unit circle |z| = 1.",
                    "Bilinear transform maps the continuous Laplace left-half s-plane Re(s) < 0 uniquely into the interior of the discrete unit circle |z| < 1.",
                    "The non-linear tangent relationship maps the infinite analog frequency axis (-inf < omega_a < inf) into the bounded digital range (-pi/T_s < omega_d < pi/T_s), requiring pre-warping of filter cutoff frequencies."
                ],
                "parameters": [
                    {"symbol": "z", "unit": "complex", "definition": "Complex discrete-time frequency variable r * e^(j*omega)"},
                    {"symbol": "T_s", "unit": "s", "definition": "Sampling period (1 / f_s)"},
                    {"symbol": "omega_a", "unit": "rad/s", "definition": "Analog pre-warped angular frequency"},
                    {"symbol": "omega_d", "unit": "rad/s", "definition": "Digital desired angular frequency"}
                ]
            }
        ],
        "worked_examples": [
            {
                "title": "Bilinear Transform Pre-Warping for Digital Butterworth Filter",
                "problem_statement": "Design a digital filter operating at sampling rate f_s = 48 kHz with a corner cutoff frequency f_d = 8 kHz. Calculate the analog pre-warped frequency f_a required for prototype analog filter design.",
                "step_by_step_solution": [
                    "Step 1: Calculate sampling period T_s = 1 / 48,000 = 20.833 us.",
                    "Step 2: Digital angular frequency omega_d = 2 * pi * 8,000 = 50,265.48 rad/s.",
                    "Step 3: Normalized half-angle = (omega_d * T_s) / 2 = (50265.48 * 20.833e-6) / 2 = 0.5236 rad = 30.0 degrees.",
                    "Step 4: Pre-warped analog angular frequency omega_a = (2 / T_s) * tan(30 deg) = (2 * 48000) * 0.57735 = 55,425.6 rad/s.",
                    "Step 5: Pre-warped analog frequency f_a = omega_a / (2 * pi) = 55425.6 / 6.28318 = 8,821.4 Hz = 8.82 kHz."
                ],
                "verified_output": "Pre-warped analog corner f_a = 8.82 kHz (compensating for 821 Hz compression)"
            }
        ],
        "simulation_activities": [
            {
                "lab_id": "SIGN_LAB_01",
                "title": "Complex Pole-Zero Interactive Plane & Frequency Response",
                "component": "MathStudioHub",
                "instructions": "Place a conjugate pole pair at p = -0.5 +/- j3.0. Observe transient damped oscillations and resonant peak on the generated Bode magnitude plot. Move poles into right-half plane and observe instability boundary.",
                "expected_telemetry": {"resonant_peak_hz": 0.477, "stability": "STABLE"}
            }
        ],
        "assessment_questions": [
            {
                "id": "SIGN_Q1",
                "bloom_level": "L4 (Analyze)",
                "question": "For a causal discrete-time LTI system with transfer function H(z) = 1 / (1 - 1.25 z^-1 + 0.375 z^-2), which statement regarding stability is correct?",
                "options": [
                    "The system is UNSTABLE because one pole lies outside the unit circle (|p1| = 0.75, |p2| = 0.5)",
                    "The system is STABLE because all poles lie strictly inside the unit circle",
                    "The system is MARGINALLY STABLE with poles on the unit circle",
                    "The system stability cannot be determined without the ROC"
                ],
                "correct_index": 1,
                "explanation": "Roots of z^2 - 1.25z + 0.375 = 0 are z = 0.75 and z = 0.5. Both poles have magnitude < 1.0 (inside the unit circle), so the causal system is unconditionally BIBO stable."
            }
        ]
    },

    # 7. CONTROL SYSTEMS
    "EC23C07": {
        "code": "EC23C07",
        "title": "Control Systems Engineering",
        "descriptive_title": "Mathematical Modeling, Root Locus, Frequency Domain Stability, and State-Space Design",
        "short_title": "Control Systems",
        "slug": "control-systems",
        "semester": 4,
        "credits": 4,
        "ltp": "3-1-0",
        "category": "Professional Core (PCC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "purple",
        "theme_color": "#A855F7",
        "icon": "🎛️",
        "prerequisites": ["EC23C04", "MA23C01"],
        "corequisites": [],
        "cos_count": 5,
        "simulation_platform": "Control Systems Explorer & Nyquist Tool",
        "simulation_component": "MathStudioHub",
        "total_lab_hours": 36,
        "course_outcomes": [
            {"id": "CO1", "description": "Formulate electrical and electromechanical transfer functions using block diagrams and Mason's gain formula.", "bloom_level": "L3 (Apply)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO2", "description": "Analyze time-domain transient step responses (damping ratio zeta, natural frequency wn, peak overshoot Mp, settling time ts).", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO3", "description": "Evaluate asymptotic stability via Routh-Hurwitz criteria and construct closed-loop root locus trajectories as parameter K varies.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO2", "PO3"], "mapped_psos": ["PSO1"]},
            {"id": "CO4", "description": "Design frequency-domain lead, lag, and lead-lag compensators using Bode magnitude/phase plots and Nyquist encirclement criteria.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO3", "PO4"], "mapped_psos": ["PSO2"]},
            {"id": "CO5", "description": "Synthesize state-space representations and verify system controllability, observability, and full-state feedback pole placement.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO2", "PO3", "PO5"], "mapped_psos": ["PSO2"]}
        ],
        "mathematical_derivations": [
            {
                "topic": "Second-Order Underdamped Step Response & Peak Overshoot Derivation",
                "formula_latex": r"T(s) = \frac{\omega_n^2}{s^2 + 2 \zeta \omega_n s + \omega_n^2}, \quad M_p = e^{-\frac{\zeta \pi}{\sqrt{1 - \zeta^2}}} \times 100\%, \quad t_s(2\%) \approx \frac{4}{\zeta \omega_n}",
                "derivation_steps": [
                    "For underdamped systems (0 < zeta < 1), closed-loop poles are complex conjugates: s = -zeta * wn +/- j * wn * sqrt(1 - zeta^2).",
                    "Inverse Laplace transform of Y(s) = T(s) / s yields the step response y(t) = 1 - (e^(-zeta*wn*t) / sqrt(1 - zeta^2)) * sin(wd*t + phi).",
                    "Differentiating y(t) and setting to zero yields the peak time t_p = pi / w_d = pi / (wn * sqrt(1 - zeta^2)).",
                    "Substituting t_p back into y(t) yields maximum peak value, yielding the exact formula for percentage overshoot M_p."
                ],
                "parameters": [
                    {"symbol": "zeta", "unit": "dimensionless", "definition": "Damping ratio"},
                    {"symbol": "omega_n", "unit": "rad/s", "definition": "Undamped natural frequency"},
                    {"symbol": "M_p", "unit": "%", "definition": "Maximum percentage peak overshoot"},
                    {"symbol": "t_s", "unit": "s", "definition": "2% settling time"}
                ]
            }
        ],
        "worked_examples": [
            {
                "title": "Feedback Control System Transient Specification Tuning",
                "problem_statement": "A closed-loop servo system requires maximum peak overshoot M_p <= 9.5% and a 2% settling time t_s <= 1.0 s. Determine the required damping ratio zeta and natural frequency omega_n.",
                "step_by_step_solution": [
                    "Step 1: From M_p = exp(-zeta * pi / sqrt(1 - zeta^2)) = 0.095:",
                    "Step 2: ln(0.095) = -2.3538 -> zeta * pi / sqrt(1 - zeta^2) = 2.3538 -> zeta / sqrt(1 - zeta^2) = 0.7492.",
                    "Step 3: Squaring both sides: zeta^2 = 0.5614 * (1 - zeta^2) -> 1.5614 * zeta^2 = 0.5614 -> zeta = sqrt(0.3595) = 0.60.",
                    "Step 4: From settling time t_s = 4 / (zeta * omega_n) <= 1.0 s:",
                    "Step 5: omega_n >= 4 / (0.60 * 1.0) = 6.67 rad/s."
                ],
                "verified_output": "zeta >= 0.60, omega_n >= 6.67 rad/s"
            }
        ],
        "simulation_activities": [
            {
                "lab_id": "CTRL_LAB_01",
                "title": "Root Locus Trajectory & Gain Margin Analysis",
                "component": "MathStudioHub",
                "instructions": "Input open-loop transfer function G(s) = K / (s*(s+2)*(s+5)). Compute breakaway points, imaginary axis crossing frequency, and critical gain K_crit for marginal stability.",
                "expected_telemetry": {"k_critical": 70.0, "omega_cross_rad": 3.16}
            }
        ],
        "assessment_questions": [
            {
                "id": "CTRL_Q1",
                "bloom_level": "L4 (Analyze)",
                "question": "According to the Nyquist stability criterion, if an open-loop system has P = 1 open-loop pole in the right-half plane, how many encirclements N of the critical point (-1, j0) are required for the closed-loop system to be stable?",
                "options": [
                    "N = -1 (1 counter-clockwise encirclement)",
                    "N = +1 (1 clockwise encirclement)",
                    "N = 0 (zero encirclements)",
                    "N = -2 (2 counter-clockwise encirclements)"
                ],
                "correct_index": 0,
                "explanation": "Nyquist formula states Z = N + P, where Z is the number of closed-loop right-half plane poles and N is clockwise encirclements. For stability Z = 0, so 0 = N + 1 -> N = -1, meaning exactly 1 counter-clockwise encirclement is required."
            }
        ]
    },

    # 9. COMMUNICATION SYSTEMS
    "EC23C08": {
        "code": "EC23C08",
        "title": "Analog and Digital Communication Systems",
        "descriptive_title": "Modulation Theory, Shannon Capacity, QAM Constellations, RF Matching, and Noise",
        "short_title": "Communication Systems",
        "slug": "communication-systems",
        "semester": 5,
        "credits": 4,
        "ltp": "3-0-2",
        "category": "Professional Core (PCC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "blue",
        "theme_color": "#3B82F6",
        "icon": "📡",
        "prerequisites": ["EC23C04", "EC23S01"],
        "corequisites": [],
        "cos_count": 5,
        "simulation_platform": "RF Smith Chart & Constellation Hub",
        "simulation_component": "RfSmithChartHub",
        "total_lab_hours": 45,
        "course_outcomes": [
            {"id": "CO1", "description": "Analyze analog AM, DSB-SC, SSB, and FM modulation spectra and power distribution efficiency.", "bloom_level": "L3 (Apply)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO2", "description": "Evaluate digital baseband pulse shaping, raised cosine Nyquist criterion, and intersymbol interference (ISI).", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO3", "description": "Synthesize M-ary digital modulation constellations (BPSK, QPSK, 16-QAM, 64-QAM) and bit error rate (BER) curves.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO2", "PO3"], "mapped_psos": ["PSO1"]},
            {"id": "CO4", "description": "Calculate channel capacity bounds governed by Shannon-Hartley theorem under Additive White Gaussian Noise (AWGN).", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2", "PO4"], "mapped_psos": ["PSO1"]},
            {"id": "CO5", "description": "Design RF transmission line impedance matching stubs using Smith chart reflection coefficient Gamma and VSWR.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO3", "PO5"], "mapped_psos": ["PSO2"]}
        ],
        "mathematical_derivations": [
            {
                "topic": "Shannon-Hartley Channel Capacity & Bit Error Rate in M-QAM",
                "formula_latex": r"C = B \log_2\left(1 + \frac{S}{N_0 B}\right), \quad \Gamma = \frac{Z_L - Z_0}{Z_L + Z_0}, \quad \text{VSWR} = \frac{1 + |\Gamma|}{1 - |\Gamma|}",
                "derivation_steps": [
                    "Shannon capacity establishes the theoretical maximum rate at which error-free information can be communicated over a bandwidth B with SNR.",
                    "Voltage reflection coefficient Gamma quantifies the fraction of incident electromagnetic wave reflected from load impedance Z_L.",
                    "Voltage Standing Wave Ratio (VSWR) measures the ratio of maximum to minimum voltage along a transmission line.",
                    "Perfect impedance match occurs when Z_L = Z_0, yielding Gamma = 0, VSWR = 1.0, and 100% forward power transfer."
                ],
                "parameters": [
                    {"symbol": "C", "unit": "bits/s", "definition": "Shannon channel capacity"},
                    {"symbol": "B", "unit": "Hz", "definition": "Channel bandwidth"},
                    {"symbol": "Gamma", "unit": "complex", "definition": "Voltage reflection coefficient"},
                    {"symbol": "VSWR", "unit": "dimensionless", "definition": "Voltage standing wave ratio (1 <= VSWR < inf)"}
                ]
            }
        ],
        "worked_examples": [
            {
                "title": "RF Transmission Line Matching & VSWR Calculation",
                "problem_statement": "A 50-Ohm characteristic impedance transmission line is terminated in a load impedance Z_L = 75 + j50 Ohms. Calculate the complex reflection coefficient Gamma, return loss in dB, and VSWR.",
                "step_by_step_solution": [
                    "Step 1: Numerator = Z_L - Z_0 = (75 + j50) - 50 = 25 + j50.",
                    "Step 2: Denominator = Z_L + Z_0 = (75 + j50) + 50 = 125 + j50.",
                    "Step 3: Gamma = (25 + j50) / (125 + j50) = (25 + j50)*(125 - j50) / (125^2 + 50^2) = (3125 - j1250 + j6250 + 2500) / (15625 + 2500) = (5625 + j5000) / 18125 = 0.3103 + j0.2759.",
                    "Step 4: Magnitude |Gamma| = sqrt(0.3103^2 + 0.2759^2) = sqrt(0.0963 + 0.0761) = sqrt(0.1724) = 0.4152.",
                    "Step 5: VSWR = (1 + 0.4152) / (1 - 0.4152) = 1.4152 / 0.5848 = 2.42.",
                    "Step 6: Return Loss RL = -20 * log10(0.4152) = +7.63 dB."
                ],
                "verified_output": "|Gamma| = 0.415, VSWR = 2.42, Return Loss = 7.63 dB"
            }
        ],
        "simulation_activities": [
            {
                "lab_id": "COMM_LAB_01",
                "title": "Interactive Smith Chart Quarter-Wave Transformer Matching",
                "component": "RfSmithChartHub",
                "instructions": "Place complex load Z_L = 75 + j50 Ohms on the interactive Smith Chart. Insert series transmission line and open shunt stub to rotate reflection coefficient into chart center (Gamma = 0).",
                "expected_telemetry": {"vswr_matched": 1.02, "gamma_magnitude": 0.01}
            }
        ],
        "assessment_questions": [
            {
                "id": "COMM_Q1",
                "bloom_level": "L4 (Analyze)",
                "question": "What is the minimum theoretical SNR required in dB for a 1 MHz bandwidth channel to transmit data at a rate of 4 Mbps according to the Shannon-Hartley theorem?",
                "options": [
                    "11.76 dB",
                    "15.05 dB",
                    "7.23 dB",
                    "24.08 dB"
                ],
                "correct_index": 0,
                "explanation": "C = B * log2(1 + SNR) -> 4e6 = 1e6 * log2(1 + SNR) -> log2(1 + SNR) = 4 -> 1 + SNR = 2^4 = 16 -> SNR = 15. In dB: SNR_dB = 10 * log10(15) = 11.76 dB."
            }
        ]
    },

    # 11. STM32 ARCHITECTURE
    "STM32-ACADEMY": {
        "code": "STM32-ACADEMY",
        "title": "STM32 Bare-Metal & FreeRTOS Architecture",
        "descriptive_title": "ARM Cortex-M Bare-Metal Registers, RCC Clock Tree, Peripherals, and FreeRTOS Kernel",
        "short_title": "STM32 Academy",
        "slug": "stm32-architecture",
        "semester": 6,
        "credits": 3,
        "ltp": "1-0-4",
        "category": "Employability Enhancement (EEC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "emerald",
        "theme_color": "#00F0B5",
        "icon": "⚡",
        "prerequisites": ["EC8702", "EC23C06"],
        "corequisites": [],
        "cos_count": 5,
        "simulation_platform": "Wokwi STM32 / Logic Analyzer Bridge",
        "simulation_component": "Stm32AcademySimulator",
        "total_lab_hours": 60,
        "course_outcomes": [
            {"id": "CO1", "description": "Configure STM32 Reset and Clock Control (RCC) PLL trees for maximum core frequency with proper flash latency wait-states.", "bloom_level": "L3 (Apply)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO2", "description": "Manipulate memory-mapped peripheral registers directly using volatile C pointers without HAL overhead.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO2", "PO3"], "mapped_psos": ["PSO1"]},
            {"id": "CO3", "description": "Configure Nested Vectored Interrupt Controller (NVIC) preemption priority grouping and EXTI edge triggers.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO2", "PO4"], "mapped_psos": ["PSO2"]},
            {"id": "CO4", "description": "Implement zero-copy circular DMA pipelines for high-throughput SPI and USART telemetry.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO3", "PO5"], "mapped_psos": ["PSO2"]},
            {"id": "CO5", "description": "Deploy FreeRTOS preemptive kernel tasks with mutex priority inheritance to eliminate priority inversion traps.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO3", "PO5"], "mapped_psos": ["PSO2"]}
        ],
        "mathematical_derivations": [
            {
                "topic": "STM32F4 RCC PLL Clock Multiplication & Flash Wait-States",
                "formula_latex": r"f_{VCO} = f_{in} \times \frac{\text{PLLN}}{\text{PLLM}}, \quad f_{sysclk} = \frac{f_{VCO}}{\text{PLLP}}, \quad \text{LATENCY} = \lceil \frac{f_{sysclk}}{\text{Flash Speed}} \rceil - 1",
                "derivation_steps": [
                    "Input clock frequency f_in (typically 8MHz or 16MHz HSE/HSI) is divided by PLLM to ensure 1MHz to 2MHz VCO input.",
                    "VCO multiplies by factor PLLN (between 50 and 432) to generate intermediate frequency f_VCO between 100MHz and 432MHz.",
                    "Main system clock divider PLLP (/2, /4, /6, /8) produces core clock f_sysclk up to maximum rated limit (e.g. 84MHz for F401, 168MHz for F405).",
                    "Flash memory access time requires wait-states (FLASH_ACR_LATENCY) when core clock exceeds raw flash silicon propagation delays."
                ],
                "parameters": [
                    {"symbol": "f_sysclk", "unit": "MHz", "definition": "Core CPU clock frequency"},
                    {"symbol": "PLLN", "unit": "integer", "definition": "Main PLL multiplication factor (50 to 432)"},
                    {"symbol": "PLLM", "unit": "integer", "definition": "PLL input prescaler (2 to 63)"},
                    {"symbol": "LATENCY", "unit": "wait-states", "definition": "Flash memory read latency cycles"}
                ]
            }
        ],
        "worked_examples": [
            {
                "title": "STM32F401RE 84 MHz PLL Configuration Calculation",
                "problem_statement": "An STM32F401RE Nucleo board uses an 8 MHz external crystal (HSE). Calculate PLLM, PLLN, and PLLP registers to achieve maximum 84 MHz core clock and determine required Flash wait-states at 3.3V.",
                "step_by_step_solution": [
                    "Step 1: Set input prescaler PLLM = 8 to achieve 1 MHz reference clock (8 MHz / 8 = 1 MHz).",
                    "Step 2: Set target f_VCO = 336 MHz. Multiplication factor PLLN = 336 (336 * 1 MHz = 336 MHz).",
                    "Step 3: Set main system divider PLLP = 4 (336 MHz / 4 = 84 MHz).",
                    "Step 4: At VDD = 3.3V, Flash operates without wait-states up to 30 MHz, 1 WS up to 60 MHz, and 2 WS up to 84 MHz.",
                    "Step 5: Set FLASH->ACR |= FLASH_ACR_LATENCY_2WS."
                ],
                "verified_output": "PLLM = 8, PLLN = 336, PLLP = 4, Flash Latency = 2 Wait-States"
            }
        ],
        "simulation_activities": [
            {
                "lab_id": "STM32_LAB_01",
                "title": "Bare-Metal SysTick Timer Tick Generation & GPIO Blinky",
                "component": "Stm32AcademySimulator",
                "instructions": "Configure SysTick reload register for exactly 1.0 ms tick at 84 MHz core clock. Toggle GPIOA Pin 5 LED on Nucleo board every 500 ms using interrupt handler.",
                "expected_telemetry": {"systick_reload_val": 83999, "toggle_period_ms": 500.0}
            }
        ],
        "assessment_questions": [
            {
                "id": "STM32_Q1",
                "bloom_level": "L4 (Analyze)",
                "question": "In an ARM Cortex-M interrupt handler, what is the consequence of failing to clear the peripheral EXTI pending register flag before exiting the ISR?",
                "options": [
                    "The processor immediately re-enters the same ISR upon exit, hanging the main execution loop",
                    "The peripheral enters sleep mode automatically",
                    "A HardFault exception is triggered immediately",
                    "The NVIC clears the hardware flag autonomously on the next clock cycle"
                ],
                "correct_index": 0,
                "explanation": "Cortex-M NVIC senses the active interrupt signal from the peripheral. If the software does not clear the peripheral's pending bit (e.g. EXTI->PR |= EXTI_PR_PR0), the interrupt line remains asserted, causing the CPU to immediately re-enter the ISR after unstacking."
            }
        ]
    },

    # 12. ESP32 IOT SYSTEMS
    "IOT8701": {
        "code": "IOT8701",
        "title": "ESP32 IoT Edge Node & Low-Power Telemetry",
        "descriptive_title": "Xtensa LX7 Architecture, Ultra-Low Power Deep Sleep, SAR ADC, and MQTT Telemetry",
        "short_title": "ESP32 IoT Systems",
        "slug": "esp32-iot-systems",
        "semester": 6,
        "credits": 3,
        "ltp": "1-0-4",
        "category": "Professional Core (PCC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "teal",
        "theme_color": "#14B8A6",
        "icon": "🌐",
        "prerequisites": ["EC8702", "EC23C03"],
        "corequisites": [],
        "cos_count": 5,
        "simulation_platform": "Wokwi ESP32 Sensor & Telemetry Simulator",
        "simulation_component": "IoTSensorSimulatorHub",
        "total_lab_hours": 60,
        "course_outcomes": [
            {"id": "CO1", "description": "Configure ESP32 power domains and Ultra-Low-Power (ULP) coprocessor for microampere deep-sleep telemetry.", "bloom_level": "L3 (Apply)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO2", "description": "Calibrate non-linear 12-bit SAR ADC readings using internal eFuse Vref multi-point polynomial compensation.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO2", "PO3"], "mapped_psos": ["PSO1"]},
            {"id": "CO3", "description": "Implement FreeRTOS dual-core task pinning (Core 0 for Wi-Fi stack, Core 1 for real-time sensor processing).", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO2", "PO4"], "mapped_psos": ["PSO2"]},
            {"id": "CO4", "description": "Design lightweight MQTT-SN telemetry payloads with QoS 1 acknowledgment and local offline flash circular spooling.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO3", "PO5"], "mapped_psos": ["PSO2"]},
            {"id": "CO5", "description": "Model LiFePO4 battery discharge lifetime under periodic wake-up duty cycles with temperature compensation.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO3", "PO5"], "mapped_psos": ["PSO2"]}
        ],
        "mathematical_derivations": [
            {
                "topic": "Periodic Deep-Sleep Battery Lifetime Model",
                "formula_latex": r"I_{avg} = \frac{I_{active} \times t_{active} + I_{sleep} \times t_{sleep}}{t_{active} + t_{sleep}}, \quad T_{life} = \frac{C_{battery} \times \eta}{I_{avg} \times 24 \times 365.25}",
                "derivation_steps": [
                    "Average current consumption is weighted by active duty cycle D = t_active / (t_active + t_sleep).",
                    "Active phase includes sensor warm-up, ADC sampling, Wi-Fi association, TLS handshake, and MQTT publish.",
                    "Deep sleep phase disables high-frequency PLLs and CPU cores, leaving only RTC memory powered (current draw ~10 uA).",
                    "Battery self-discharge and DC-DC converter quiescent efficiency eta reduce usable nominal capacity."
                ],
                "parameters": [
                    {"symbol": "I_active", "unit": "mA", "definition": "Average active current during Wi-Fi transmission (approx 120 mA)"},
                    {"symbol": "I_sleep", "unit": "uA", "definition": "Deep sleep quiescent current (approx 10 uA)"},
                    {"symbol": "C_battery", "unit": "mAh", "definition": "Nominal cell capacity"},
                    {"symbol": "T_life", "unit": "years", "definition": "Autonomous field operational lifetime"}
                ]
            }
        ],
        "worked_examples": [
            {
                "title": "ESP32 LiFePO4 Autonomous Sensor Node Lifetime Estimation",
                "problem_statement": "An ESP32 environmental sensor wakes up once every 10 minutes (600 s) for 3.0 s to sample sensors and transmit an MQTT packet (I_active = 150 mA). Deep sleep current is 15 uA. Using a 2500 mAh battery with 85% usable capacity efficiency, calculate expected battery lifetime in years.",
                "step_by_step_solution": [
                    "Step 1: Active time t_active = 3.0 s, Sleep time t_sleep = 597.0 s, Total period T = 600 s.",
                    "Step 2: Active charge per cycle = 150 mA * 3.0 s = 450 mAs = 0.125 mAh.",
                    "Step 3: Sleep charge per cycle = 0.015 mA * 597.0 s = 8.955 mAs = 0.002487 mAh.",
                    "Step 4: Total charge per cycle = 0.125 + 0.002487 = 0.127487 mAh per 10 minutes.",
                    "Step 5: Hourly consumption = 0.127487 * 6 = 0.7649 mAh/hour.",
                    "Step 6: Average current I_avg = 0.7649 mA.",
                    "Step 7: Usable battery capacity = 2500 * 0.85 = 2125 mAh.",
                    "Step 8: Lifetime = 2125 mAh / (0.7649 mA * 24 * 365.25) = 2125 / 6704.5 = 0.317 years = approx 116 days."
                ],
                "verified_output": "I_avg = 0.765 mA, Expected Lifetime = 116 days (3.8 months)"
            }
        ],
        "simulation_activities": [
            {
                "lab_id": "IOT_LAB_01",
                "title": "ESP32 SAR ADC Two-Point Calibration & Non-Linearity Compensation",
                "component": "IoTSensorSimulatorHub",
                "instructions": "Sweep input analog voltage from 0.1V to 3.1V across ADC1 Channel 0. Compare raw 12-bit code against calibrated mV reading. Verify elimination of ADC lower and upper non-linearity deadzones.",
                "expected_telemetry": {"v_calibrated_error_mv": 12.0, "sar_resolution_bits": 12}
            }
        ],
        "assessment_questions": [
            {
                "id": "IOT_Q1",
                "bloom_level": "L4 (Analyze)",
                "question": "Why is Wi-Fi transmission significantly more energy-intensive than BLE or LoRa for periodic sensor telemetry on ESP32?",
                "options": [
                    "Wi-Fi requires prolonged AP association, DHCP IP lease negotiation, and higher RF power amplifiers (20 dBm)",
                    "Wi-Fi uses larger antenna dimensions which increases copper resistance",
                    "Wi-Fi operates only at 5 GHz which attenuates faster",
                    "Wi-Fi chips cannot enter deep sleep modes"
                ],
                "correct_index": 0,
                "explanation": "Wi-Fi frames require beacon synchronization, active channel scanning, authentication, and DHCP lease exchanges, keeping the radio active for 1-3 seconds at ~150mA, whereas BLE advertising packets complete in < 10 ms."
            }
        ]
    },

    # 13. VERILOG HDL & FPGA
    "HDL6001": {
        "code": "HDL6001",
        "title": "Verilog HDL and FPGA Digital System Design",
        "descriptive_title": "RTL Synthesis, FSM Encoding, Timing Constraints, SVA Assertions, and FPGA Place-and-Route",
        "short_title": "Verilog & FPGA",
        "slug": "verilog-fpga-design",
        "semester": 6,
        "credits": 4,
        "ltp": "3-0-2",
        "category": "Professional Core (PCC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "amber",
        "theme_color": "#F59E0B",
        "icon": "🔲",
        "prerequisites": ["EC23C06"],
        "corequisites": [],
        "cos_count": 5,
        "simulation_platform": "FPGA Synthesis & Logic Analyzer Engine",
        "simulation_component": "FpgaSynthesisHub",
        "total_lab_hours": 45,
        "course_outcomes": [
            {"id": "CO1", "description": "Author synthesizable RTL models using structural, dataflow, and behavioral Verilog HDL constructs.", "bloom_level": "L3 (Apply)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO2", "description": "Synthesize pipelined arithmetic datapaths (carry-select adders, Wallace-tree multipliers) with balanced latency.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO2", "PO3"], "mapped_psos": ["PSO1"]},
            {"id": "CO3", "description": "Write SystemVerilog Assertions (SVA) with temporal property operators to verify bus protocols.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO2", "PO4"], "mapped_psos": ["PSO2"]},
            {"id": "CO4", "description": "Formulate Static Timing Analysis (STA) constraints in SDC syntax and resolve clock domain crossing (CDC) hazards.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO3", "PO4"], "mapped_psos": ["PSO2"]},
            {"id": "CO5", "description": "Map digital systems onto FPGA architectures (LUT6, DSP48 slices, Block RAM, PLL clock buffers).", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO3", "PO5"], "mapped_psos": ["PSO2"]}
        ],
        "mathematical_derivations": [
            {
                "topic": "Clock Domain Crossing (CDC) Synchronizer MTBF Derivation",
                "formula_latex": r"\text{MTBF} = \frac{e^{\frac{t_{resolve}}{\tau}}}{T_0 \times f_{clk} \times f_{data}}",
                "derivation_steps": [
                    "When an asynchronous signal transitions within the setup/hold window of a clock edge, the receiving flip-flop enters a metastable state.",
                    "The probability of the flip-flop remaining metastable after resolution time t_resolve decays exponentially with time constant tau.",
                    "Dual-flip-flop synchronizers grant a full clock cycle resolution window (t_resolve = T_clk - t_setup), boosting MTBF from seconds to thousands of years."
                ],
                "parameters": [
                    {"symbol": "MTBF", "unit": "seconds / years", "definition": "Mean Time Between Failures due to metastability"},
                    {"symbol": "tau", "unit": "s", "definition": "Flip-flop regeneration latch time constant"},
                    {"symbol": "T_0", "unit": "s", "definition": "Asymptotic metastability aperture window parameter"},
                    {"symbol": "f_clk", "unit": "Hz", "definition": "Receiving clock domain frequency"},
                    {"symbol": "f_data", "unit": "Hz", "definition": "Asynchronous input transition rate"}
                ]
            }
        ],
        "worked_examples": [
            {
                "title": "Dual Flip-Flop Synchronizer MTBF Calculation",
                "problem_statement": "A 10 MHz asynchronous data signal enters a 100 MHz clock domain. The flip-flop has parameters T_0 = 1.0e-10 s and tau = 0.12 ns. The resolution window t_resolve is 8.5 ns. Calculate the synchronizer MTBF in years.",
                "step_by_step_solution": [
                    "Step 1: Calculate exponent: t_resolve / tau = 8.5e-9 / 0.12e-9 = 70.833.",
                    "Step 2: Calculate numerator = exp(70.833) = 5.787e30.",
                    "Step 3: Calculate denominator = T_0 * f_clk * f_data = 1.0e-10 * 100e6 * 10e6 = 1.0e5 s^-1.",
                    "Step 4: MTBF = 5.787e30 / 1.0e5 = 5.787e25 seconds.",
                    "Step 5: Convert to years: 5.787e25 / (365.25 * 24 * 3600) = 1.834e18 years (Essentially infinite reliability)."
                ],
                "verified_output": "MTBF = 1.83e18 years (Metastability risk completely eliminated)"
            }
        ],
        "simulation_activities": [
            {
                "lab_id": "HDL_LAB_01",
                "title": "SystemVerilog Temporal Assertion Trace Evaluation",
                "component": "FpgaSynthesisHub",
                "instructions": "Simulate request-grant protocol assertion: assert property (@(posedge clk) req |-> ##[1:2] gnt). Inject artificial delayed grant and observe assertion failure firing.",
                "expected_telemetry": {"assertions_passed": 48, "assertions_failed": 1}
            }
        ],
        "assessment_questions": [
            {
                "id": "HDL_Q1",
                "bloom_level": "L4 (Analyze)",
                "question": "In synthesizable Verilog, what hardware artifact is accidentally generated if a variable in a combinational 'always @(*)' block is not assigned in every conditional branch?",
                "options": [
                    "An unintentional transparent level-sensitive latch",
                    "A positive-edge triggered D flip-flop",
                    "A high-impedance tri-state buffer",
                    "A clock tree buffer"
                ],
                "correct_index": 0,
                "explanation": "If a combinational variable is not assigned in all branches of an 'if' or 'case' statement, the synthesis tool must preserve its previous value, synthesizing an unintentional transparent latch which causes timing hazards."
            }
        ]
    },

    # 14. VLSI PHYSICAL DESIGN
    "VLSI7001": {
        "code": "VLSI7001",
        "title": "VLSI Physical Design & ASIC Architecture",
        "descriptive_title": "Floorplanning, Placement, Clock Tree Synthesis (CTS), Routing, and Static Timing Analysis",
        "short_title": "VLSI Physical Design",
        "slug": "vlsi-physical-design",
        "semester": 7,
        "credits": 4,
        "ltp": "3-0-2",
        "category": "Professional Core (PCC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "rose",
        "theme_color": "#F43F5E",
        "icon": "🔬",
        "prerequisites": ["EC23C03", "HDL6001"],
        "corequisites": [],
        "cos_count": 5,
        "simulation_platform": "ASIC Physical Design & Floorplanning Studio",
        "simulation_component": "VlsiPhysicalDesignHub",
        "total_lab_hours": 45,
        "course_outcomes": [
            {"id": "CO1", "description": "Formulate ASIC floorplanning budgeting, core-to-die aspect ratios, and standard cell utilization heatmaps.", "bloom_level": "L3 (Apply)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO2", "description": "Optimize global placement wirelength using Half-Perimeter Wirelength (HPWL) and analytical quadratic solvers.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO2", "PO3"], "mapped_psos": ["PSO1"]},
            {"id": "CO3", "description": "Synthesize balanced H-Tree Clock Tree Synthesis (CTS) topologies with minimum insertion delay and skew.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO2", "PO4"], "mapped_psos": ["PSO2"]},
            {"id": "CO4", "description": "Model multi-layer interconnect parasitics using Elmore delay approximations and buffer insertion rules.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO3", "PO4"], "mapped_psos": ["PSO1"]},
            {"id": "CO5", "description": "Execute Design Rule Checking (DRC) and Layout Versus Schematic (LVS) verification for sub-micron tapeouts.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO3", "PO5"], "mapped_psos": ["PSO2"]}
        ],
        "mathematical_derivations": [
            {
                "topic": "Elmore Delay in Distributed Distributed RC Interconnect Trees",
                "formula_latex": r"T_{Di} = \sum_{k} R_{ik} C_k, \quad \tau_{wire} = r_{sq} c_{sq} \frac{L^2}{2}, \quad L_{opt} = \sqrt{\frac{2 R_{buf} C_{buf}}{r_{wire} c_{wire}}}",
                "derivation_steps": [
                    "Elmore delay calculates the first moment of the interconnect impulse response through recursive RC tree summation.",
                    "Unbuffered interconnect delay grows quadratically with length L (proportional to L^2) due to distributed resistance and capacitance.",
                    "Inserting optimal repeater buffers at regular intervals L_opt transforms quadratic delay into linear scaling (proportional to L), maximizing operating frequency."
                ],
                "parameters": [
                    {"symbol": "T_Di", "unit": "ps", "definition": "Elmore delay at sink node i"},
                    {"symbol": "r_sq", "unit": "Ohm/um", "definition": "Metal wire sheet resistance per unit length"},
                    {"symbol": "c_sq", "unit": "fF/um", "definition": "Interconnect parasitic capacitance per unit length"},
                    {"symbol": "L_opt", "unit": "um", "definition": "Optimal repeater buffer insertion spacing"}
                ]
            }
        ],
        "worked_examples": [
            {
                "title": "Optimal Repeater Buffer Spacing for On-Chip Bus",
                "problem_statement": "An on-chip metal-4 interconnect bus in a 28nm ASIC has r_wire = 0.25 Ohm/um and c_wire = 0.18 fF/um. Standard inverter repeaters have output resistance R_buf = 300 Ohms and input capacitance C_buf = 4.0 fF. Calculate the optimal repeater spacing L_opt.",
                "step_by_step_solution": [
                    "Step 1: Calculate buffer product: R_buf * C_buf = 300 * 4e-15 = 1.2e-12 s.",
                    "Step 2: Calculate wire product: r_wire * c_wire = (0.25 * 1e6) * (0.18e-15 * 1e6) = 2.5e5 * 1.8e-10 = 4.5e-5 s/m^2.",
                    "Step 3: In terms of micrometers: r_wire * c_wire = 0.25 * 0.18e-15 = 4.5e-17 s/um^2.",
                    "Step 4: Optimal spacing formula: L_opt = sqrt((2 * R_buf * C_buf) / (r_wire * c_wire)).",
                    "Step 5: L_opt = sqrt((2 * 1.2e-12) / 4.5e-17) = sqrt(2.4e-12 / 4.5e-17) = sqrt(53,333.3) = 230.94 um."
                ],
                "verified_output": "Optimal repeater spacing L_opt = 231 um"
            }
        ],
        "simulation_activities": [
            {
                "lab_id": "VLSI_LAB_01",
                "title": "Floorplanning Core Utilization and Aspect Ratio Optimization",
                "component": "VlsiPhysicalDesignHub",
                "instructions": "Place 25 standard cells with target core utilization eta = 70%. Generate HPWL wirelength estimate and analyze clock skew across an 8-leaf H-tree clock distribution network.",
                "expected_telemetry": {"core_utilization_pct": 70.0, "clock_skew_ps": 14.5}
            }
        ],
        "assessment_questions": [
            {
                "id": "VLSI_Q1",
                "bloom_level": "L4 (Analyze)",
                "question": "What is the primary objective of Clock Tree Synthesis (CTS) in physical design compared to standard signal routing?",
                "options": [
                    "To balance clock arrival times across all sequential elements, minimizing clock skew",
                    "To minimize total metal area regardless of path latency",
                    "To eliminate all propagation delays completely",
                    "To route power rails with lowest electromigration"
                ],
                "correct_index": 0,
                "explanation": "CTS specifically inserts balanced buffer trees (e.g. H-trees or fishbone trees) to ensure the clock signal reaches every flip-flop at virtually the exact same instant, minimizing clock skew to prevent setup and hold violations."
            }
        ]
    },

    # 12. ELECTRONIC DEVICES AND CIRCUIT MODELING
    "EC23C03": {
        "code": "EC23C03",
        "title": "Electronic Devices and Circuit Modeling",
        "descriptive_title": "Non-Linear Active Devices, BJT/MOSFET Small-Signal Equivalent Circuits, and Power Amplifiers",
        "short_title": "Electronic Devices",
        "slug": "electronic-devices",
        "semester": 3,
        "credits": 3,
        "ltp": "3-0-0",
        "category": "Professional Core (PCC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "amber",
        "theme_color": "#F59E0B",
        "icon": "⚡",
        "prerequisites": ["EC23C01", "EC23C02"],
        "corequisites": [],
        "cos_count": 5,
        "simulation_platform": "Diode / MOSFET IV Curve Tracer",
        "simulation_component": "DiodeMosfetIvCurveTracer",
        "total_lab_hours": 45,
        "course_outcomes": [
            {"id": "CO1", "description": "Analyze Shockley diode equation, diffusion capacitance, and reverse recovery dynamics in high-speed switching circuits.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO2", "description": "Synthesize BJT Ebers-Moll and hybrid-pi small-signal models incorporating Early voltage and base-width modulation.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2", "PO3"], "mapped_psos": ["PSO1"]},
            {"id": "CO3", "description": "Formulate MOSFET square-law and subthreshold conduction models across triode and saturation regimes.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO4", "description": "Evaluate frequency response, Miller effect, and dominant pole compensation in multistage cascaded amplifiers.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO1", "PO3", "PO4"], "mapped_psos": ["PSO1"]},
            {"id": "CO5", "description": "Design power output stages (Class A, B, AB) with heat sink thermal dissipation and harmonic distortion constraints.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO3", "PO5"], "mapped_psos": ["PSO2"]}
        ],
        "mathematical_derivations": [
            {
                "topic": "BJT Small-Signal Transconductance & Hybrid-Pi Model Parameters",
                "formula_latex": r"g_m = \frac{I_C}{V_T}, \quad r_\pi = \frac{\beta}{g_m} = \frac{\beta V_T}{I_C}, \quad r_o = \frac{V_A + V_{CE}}{I_C} \approx \frac{V_A}{I_C}",
                "derivation_steps": [
                    "Differentiate collector current I_C = I_S * exp(V_BE / V_T) * (1 + V_CE / V_A) with respect to base-emitter voltage V_BE.",
                    "Small-signal transconductance evaluates as g_m = dI_C / dV_BE = I_C / V_T, where V_T = k_B * T / q approx 25.86 mV at 300K.",
                    "Input dynamic resistance looking into the base equals r_pi = dV_BE / dI_B = beta / g_m.",
                    "Finite output conductance due to base-width modulation (Early effect) yields output resistance r_o = dV_CE / dI_C approx V_A / I_C."
                ],
                "parameters": [
                    {"symbol": "g_m", "unit": "A/V (S)", "definition": "Small-signal transconductance"},
                    {"symbol": "r_pi", "unit": "Ohms", "definition": "Base-emitter dynamic input resistance"},
                    {"symbol": "r_o", "unit": "Ohms", "definition": "Collector-emitter Early output resistance"},
                    {"symbol": "V_A", "unit": "V", "definition": "Forward Early voltage parameter"}
                ]
            }
        ],
        "worked_examples": [
            {
                "title": "Common-Emitter Amplifier Small-Signal Midband Voltage Gain",
                "problem_statement": "A Common-Emitter BJT amplifier is biased at quiescent collector current I_C = 2.0 mA with collector load R_C = 3.3 kOhms. The BJT parameters are beta = 120, Early voltage V_A = 80 V, and thermal voltage V_T = 26 mV. Calculate g_m, r_pi, r_o, and loaded voltage gain A_v = -g_m * (R_C || r_o).",
                "step_by_step_solution": [
                    "Step 1: Compute transconductance g_m = I_C / V_T = 2.0 mA / 26 mV = 76.92 mS (0.07692 A/V).",
                    "Step 2: Compute base dynamic input resistance r_pi = beta / g_m = 120 / 0.07692 = 1,560 Ohms (1.56 kOhms).",
                    "Step 3: Compute Early output resistance r_o = V_A / I_C = 80 V / 2.0 mA = 40.0 kOhms.",
                    "Step 4: Compute effective ac collector resistance R_L' = R_C || r_o = (3.3k * 40k) / (3.3k + 40k) = 132 / 43.3 = 3.048 kOhms.",
                    "Step 5: Calculate small-signal voltage gain A_v = -g_m * R_L' = -0.07692 * 3048.5 = -234.5 V/V."
                ],
                "verified_output": "g_m = 76.92 mS, r_pi = 1.56 kOhm, r_o = 40.0 kOhm, A_v = -234.5 V/V"
            }
        ],
        "simulation_activities": [
            {
                "lab_id": "EDC_LAB_01",
                "title": "BJT Common-Emitter Output Characteristics & Early Voltage Extraction",
                "component": "DiodeMosfetIvCurveTracer",
                "instructions": "Sweep Vce from 0V to 15V at base currents Ib = 10uA to 50uA in 10uA increments. Extrapolate saturation slopes back to the negative voltage axis to extract Early voltage Va and evaluate output conductance go.",
                "expected_telemetry": {"early_voltage_v": 80.0, "gm_ms": 76.9, "vce_sat_v": 0.2}
            }
        ],
        "assessment_questions": [
            {
                "id": "EDC_Q1",
                "bloom_level": "L4 (Analyze)",
                "question": "In a BJT operating in the active region, what is the physical mechanism that causes collector current to increase slightly with increasing V_CE?",
                "options": [
                    "Base-width modulation (Early effect) narrowing the effective neutral base region",
                    "Avalanche multiplication of minority carriers in the emitter junction",
                    "Thermal runaway caused by negative temperature coefficient of V_BE",
                    "Oxide charge trapping at the silicon-silicon dioxide interface"
                ],
                "correct_index": 0,
                "explanation": "Increasing V_CE expands the reverse-biased collector-base depletion region, narrowing the effective quasi-neutral base width W_B. This reduces base recombination, steepens the carrier concentration gradient, and increases collector current."
            }
        ]
    },

    # 13. DIGITAL SIGNAL PROCESSING & ARCHITECTURE
    "EC23S01": {
        "code": "EC23S01",
        "title": "Digital Signal Processing and Algorithms",
        "descriptive_title": "Discrete Transforms, Multirate Processing, FIR/IIR Synthesis, and Fixed-Point DSP Architectures",
        "short_title": "Digital Signal Processing",
        "slug": "digital-signal-processing",
        "semester": 5,
        "credits": 2,
        "ltp": "0-0-4",
        "category": "Professional Core (PCC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "emerald",
        "theme_color": "#00F0B5",
        "icon": "📊",
        "prerequisites": ["EC23C04"],
        "corequisites": [],
        "cos_count": 5,
        "simulation_platform": "Python SciPy DSP Workstation",
        "simulation_component": "PythonSciPy",
        "total_lab_hours": 48,
        "course_outcomes": [
            {"id": "CO1", "description": "Apply Discrete Fourier Transform (DFT) and radix-2 Cooley-Tukey FFT decimation-in-time algorithms to spectral analysis.", "bloom_level": "L3 (Apply)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO2", "description": "Synthesize linear-phase FIR filters using windowing techniques and Remez/Parks-McClellan equiripple algorithms.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2", "PO3"], "mapped_psos": ["PSO1"]},
            {"id": "CO3", "description": "Design IIR digital filters via Bilinear Transformation with frequency warping pre-compensation.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO4", "description": "Analyze finite word-length quantization noise, limit cycles, and coefficient sensitivity in fixed-point registers.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2", "PO4"], "mapped_psos": ["PSO1"]},
            {"id": "CO5", "description": "Implement multirate decimation, interpolation, and polyphase filterbank decomposition on streaming telemetry.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO3", "PO5"], "mapped_psos": ["PSO2"]}
        ],
        "mathematical_derivations": [
            {
                "topic": "Bilinear Transformation & Discrete-Time Frequency Warping",
                "formula_latex": r"s = \frac{2}{T_s} \frac{1 - z^{-1}}{1 + z^{-1}}, \quad \Omega = \frac{2}{T_s} \tan\left(\frac{\omega}{2}\right)",
                "derivation_steps": [
                    "Approximate continuous integrator H_a(s) = 1/s using trapezoidal numerical integration in the time domain: y[n] - y[n-1] = (T_s/2) * (x[n] + x[n-1]).",
                    "Apply Z-transform yielding Y(z)*(1 - z^-1) = (T_s/2) * X(z)*(1 + z^-1).",
                    "Solve for transfer ratio yielding conformal substitution s = (2/T_s) * (1 - z^-1)/(1 + z^-1).",
                    "Map analog imaginary axis s = j*Omega onto discrete unit circle z = exp(j*omega): j*Omega = (2/T_s) * tanh(j*omega/2) = j*(2/T_s)*tan(omega/2).",
                    "Continuous frequencies Omega in (-inf, inf) map monotonically to discrete frequencies omega in (-pi, pi), requiring pre-warping Omega_c = (2/T_s)*tan(omega_c/2)."
                ],
                "parameters": [
                    {"symbol": "s", "unit": "rad/s", "definition": "Continuous-time Laplace complex frequency"},
                    {"symbol": "z", "unit": "dimensionless", "definition": "Discrete-time complex Z-plane variable"},
                    {"symbol": "Omega", "unit": "rad/s", "definition": "Continuous analog angular frequency"},
                    {"symbol": "omega", "unit": "rad/sample", "definition": "Digital discrete normalized angular frequency"},
                    {"symbol": "T_s", "unit": "s", "definition": "Sampling period interval"}
                ]
            }
        ],
        "worked_examples": [
            {
                "title": "Bilinear Transformation Butterworth Lowpass Filter Synthesis with Pre-Warping",
                "problem_statement": "Design a first-order digital Butterworth lowpass filter with -3dB cutoff frequency f_c = 1.0 kHz at sampling rate f_s = 8.0 kHz. Determine the pre-warped analog angular cutoff Omega_c and the resulting Z-domain transfer function H(z).",
                "step_by_step_solution": [
                    "Step 1: Compute normalized digital angular cutoff: omega_c = 2*pi*f_c / f_s = 2*pi*(1000) / 8000 = pi / 4 rad/sample approx 0.7854 rad.",
                    "Step 2: Pre-warp analog angular cutoff: Omega_c = (2 / T_s) * tan(omega_c / 2) = 2*f_s * tan(pi / 8) = 16000 * 0.414214 = 6627.42 rad/s.",
                    "Step 3: State analog prototype filter: H_a(s) = Omega_c / (s + Omega_c) = 6627.42 / (s + 6627.42).",
                    "Step 4: Substitute bilinear transformation s = 16000 * (1 - z^-1) / (1 + z^-1).",
                    "Step 5: Normalize denominator: H(z) = 6627.42*(1 + z^-1) / [16000*(1 - z^-1) + 6627.42*(1 + z^-1)] = (0.2929 + 0.2929*z^-1) / (1 - 0.4142*z^-1)."
                ],
                "verified_output": "H(z) = (0.2929 + 0.2929 z^-1) / (1 - 0.4142 z^-1), Omega_c = 6627.42 rad/s"
            }
        ],
        "simulation_activities": [
            {
                "lab_id": "DSP_LAB_01",
                "title": "Radix-2 DIT-FFT Spectrum Analysis and Windowed FIR Frequency Response",
                "component": "PythonSciPy",
                "instructions": "Synthesize a multi-tone signal (f1=500Hz, f2=1800Hz) with additive Gaussian noise. Compute 1024-point radix-2 FFT using Cooley-Tukey algorithm. Apply Hamming window and design a 31-tap Parks-McClellan FIR bandpass filter.",
                "expected_telemetry": {"fft_snr_db": 42.6, "passband_ripple_db": 0.05, "stopband_attenuation_db": -54.0}
            }
        ],
        "assessment_questions": [
            {
                "id": "DSP_Q1",
                "bloom_level": "L4 (Analyze)",
                "question": "What is the computational multiplication complexity of an N-point Radix-2 Cooley-Tukey Decimation-in-Time FFT compared to direct matrix DFT computation?",
                "options": [
                    "(N/2) * log2(N) complex multiplications versus N^2 for direct DFT",
                    "N * log2(N) complex multiplications versus N for direct DFT",
                    "O(N) linear complexity versus O(N^3) Gaussian elimination",
                    "N^2 complex multiplications versus N! combinatorial passes"
                ],
                "correct_index": 0,
                "explanation": "Radix-2 Cooley-Tukey decomposes an N-point DFT into log2(N) stages, each containing N/2 butterfly twiddle multiplications, yielding (N/2)*log2(N) complex multiplications instead of N^2."
            }
        ]
    },

    # 14. EMBEDDED SYSTEMS & ARM ARCHITECTURE
    "EC8702": {
        "code": "EC8702",
        "title": "Embedded Systems and ARM Architecture",
        "descriptive_title": "ARM Cortex-M Hardware Architecture, Deterministic RTOS Scheduling, and Low-Power Peripherals",
        "short_title": "Embedded Systems",
        "slug": "embedded-systems",
        "semester": 7,
        "credits": 3,
        "ltp": "3-0-0",
        "category": "Professional Core (PCC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "indigo",
        "theme_color": "#6366F1",
        "icon": "🖥️",
        "prerequisites": ["EC23C06"],
        "corequisites": [],
        "cos_count": 5,
        "simulation_platform": "ARM Cortex-M NVIC / DMA Virtual Hub",
        "simulation_component": "DmaNvicHub",
        "total_lab_hours": 45,
        "course_outcomes": [
            {"id": "CO1", "description": "Analyze ARM Cortex-M architecture, dual-bank stack pointers (MSP/PSP), and hardware exception auto-stacking.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO2", "description": "Synthesize preemptive Rate Monotonic and Earliest Deadline First scheduling policies on real-time RTOS kernels.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2", "PO3"], "mapped_psos": ["PSO1"]},
            {"id": "CO3", "description": "Formulate priority inversion remediation mechanisms using Priority Ceiling Protocol (PCP) and Priority Inheritance.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO3"], "mapped_psos": ["PSO1"]},
            {"id": "CO4", "description": "Evaluate direct memory access (DMA) double-buffering ping-pong streams for zero-CPU peripheral servicing.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2", "PO4"], "mapped_psos": ["PSO1"]},
            {"id": "CO5", "description": "Design power-gated ultra-low-power firmware modes (Sleep, Stop, Standby) with external wake-up latency budgets.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO3", "PO5"], "mapped_psos": ["PSO2"]}
        ],
        "mathematical_derivations": [
            {
                "topic": "Rate Monotonic Scheduling (RMS) Processor Utilization Bound",
                "formula_latex": r"U = \sum_{i=1}^{n} \frac{C_i}{T_i} \le n \left( 2^{1/n} - 1 \right), \quad \lim_{n \to \infty} n \left( 2^{1/n} - 1 \right) = \ln(2) \approx 0.693",
                "derivation_steps": [
                    "Liu & Layland established that assigning fixed priorities monotonically with task request rate (shorter period T_i implies higher priority) is optimal for static priority periodic task sets.",
                    "Processor utilization U is defined as the sum of worst-case execution time C_i divided by period T_i across all n independent periodic tasks: U = sum(C_i / T_i).",
                    "Worst-case phasing occurs at the critical instant when all tasks request execution simultaneously at t = 0.",
                    "By formulating task execution demands across worst-case period ratios, the least upper bound is proven to be U(n) = n*(2^(1/n) - 1).",
                    "For n=1: U=1.0 (100%), for n=2: U = 2*(sqrt(2)-1) approx 0.828 (82.8%), for n=3: U approx 0.780 (78.0%), and as n -> inf: lim n*(2^(1/n)-1) = ln(2) approx 0.693 (69.3%)."
                ],
                "parameters": [
                    {"symbol": "U", "unit": "dimensionless (ratio)", "definition": "Total processor core utilization"},
                    {"symbol": "C_i", "unit": "ms", "definition": "Worst-case execution time (WCET) of task i"},
                    {"symbol": "T_i", "unit": "ms", "definition": "Repetition period / deadline of task i"},
                    {"symbol": "n", "unit": "integer", "definition": "Total number of periodic real-time tasks"}
                ]
            }
        ],
        "worked_examples": [
            {
                "title": "Hard Real-Time Periodic Task Schedulability Analysis",
                "problem_statement": "A flight avionics RTOS executes three periodic tasks: Task 1 (Sensors: C_1 = 1.0 ms, T_1 = 4.0 ms), Task 2 (Guidance: C_2 = 2.0 ms, T_2 = 10.0 ms), and Task 3 (Telemetry: C_3 = 3.0 ms, T_3 = 20.0 ms). Verify whether this task set is guaranteed schedulable under Rate Monotonic Scheduling (RMS) using the Liu & Layland utilization bound.",
                "step_by_step_solution": [
                    "Step 1: Calculate individual task utilizations: U_1 = 1.0 / 4.0 = 0.250 (25.0%), U_2 = 2.0 / 10.0 = 0.200 (20.0%), U_3 = 3.0 / 20.0 = 0.150 (15.0%).",
                    "Step 2: Calculate total CPU utilization: U_total = 0.250 + 0.200 + 0.150 = 0.600 (60.0%).",
                    "Step 3: Evaluate Liu & Layland utilization bound for n = 3 tasks: U_bound = 3 * (2^(1/3) - 1) = 3 * (1.25992 - 1) = 3 * 0.25992 = 0.7798 (77.98%).",
                    "Step 4: Compare U_total against U_bound: Since 0.600 <= 0.7798, the task set is unconditionally guaranteed to meet all hard real-time deadlines under RMS.",
                    "Step 5: Verify priority assignment: Task 1 has shortest period (T=4 ms) -> Priority 1 (Highest), Task 2 (T=10 ms) -> Priority 2 (Medium), Task 3 (T=20 ms) -> Priority 3 (Lowest)."
                ],
                "verified_output": "U_total = 0.600 (60.0%) <= U_bound = 0.780 (78.0%), Guaranteed Schedulable under RMS"
            }
        ],
        "simulation_activities": [
            {
                "lab_id": "EMB_LAB_01",
                "title": "Nested Vectored Interrupt Controller (NVIC) Preemption & Latency Analysis",
                "component": "DmaNvicHub",
                "instructions": "Configure USART1_IRQn at Preemption Priority 1 and TIM2_IRQn at Preemption Priority 0 (Higher). Trigger nested interrupt arrival and measure hardware stack-push cycle count on ARM Cortex-M4 virtual core.",
                "expected_telemetry": {"nvic_latency_cycles": 12, "tail_chaining_cycles": 6, "context_switch_us": 1.45}
            }
        ],
        "assessment_questions": [
            {
                "id": "EMB_Q1",
                "bloom_level": "L4 (Analyze)",
                "question": "In real-time embedded systems, what phenomenon occurs when a high-priority task is blocked waiting for a shared mutex held by a low-priority task, which is in turn preempted by an unrelated medium-priority task?",
                "options": [
                    "Unbounded Priority Inversion",
                    "Deadlock caused by circular wait condition",
                    "Starvation due to round-robin quantum expiration",
                    "Stack frame overflow in the process stack pointer (PSP)"
                ],
                "correct_index": 0,
                "explanation": "This is classic unbounded priority inversion: the medium-priority task preempts the low-priority task holding the shared resource, indirectly delaying the high-priority task for an unbounded duration. Remediation requires Priority Inheritance Protocol (PIP) or Priority Ceiling Protocol (PCP)."
            }
        ]
    },

    # 15. OPTICS, LASERS AND OPTICAL COMMUNICATION
    "EC23E04": {
        "code": "EC23E04",
        "title": "Optics, Lasers and Optical Communication",
        "descriptive_title": "Electromagnetic Wave Propagation in Dielectric Waveguides, Laser Cavity Dynamics, and High-Speed Photonic Links",
        "short_title": "Optics and Photonics",
        "slug": "optics-and-lasers",
        "semester": 6,
        "credits": 3,
        "ltp": "3-0-0",
        "category": "Professional Elective (PEC)",
        "regulation": "Anna University Regulation 2023",
        "theme_family": "cyan",
        "theme_color": "#06B6D4",
        "icon": "🔬",
        "prerequisites": ["PH23C01", "EC23C01"],
        "corequisites": [],
        "cos_count": 5,
        "simulation_platform": "RF / Optical Waveguide Smith Chart Explorer",
        "simulation_component": "RfSmithChartHub",
        "total_lab_hours": 45,
        "course_outcomes": [
            {"id": "CO1", "description": "Analyze total internal reflection, numerical aperture (NA), and acceptance angle in step-index and graded-index fibers.", "bloom_level": "L3 (Apply)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO2", "description": "Synthesize electromagnetic wave solutions of Maxwell's equations in cylindrical dielectric waveguides and derive the V-number cutoff.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2", "PO3"], "mapped_psos": ["PSO1"]},
            {"id": "CO3", "description": "Formulate stimulated emission, Einstein coefficients, population inversion, and optical cavity threshold gain in semiconductor diode lasers.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2"], "mapped_psos": ["PSO1"]},
            {"id": "CO4", "description": "Evaluate chromatic dispersion, material dispersion, and polarization mode dispersion (PMD) in long-haul DWDM spans.", "bloom_level": "L4 (Analyze)", "mapped_pos": ["PO1", "PO2", "PO4"], "mapped_psos": ["PSO1"]},
            {"id": "CO5", "description": "Design high-speed optical transceivers with PIN/APD photodetectors meeting link power margin and rise-time budgets.", "bloom_level": "L5 (Evaluate)", "mapped_pos": ["PO3", "PO5"], "mapped_psos": ["PSO2"]}
        ],
        "mathematical_derivations": [
            {
                "topic": "Step-Index Fiber Numerical Aperture & Normalized Frequency (V-Number) Cutoff",
                "formula_latex": r"\text{NA} = \sqrt{n_1^2 - n_2^2} = n_0 \sin(\theta_{\text{max}}), \quad V = \frac{2\pi a}{\lambda_0} \text{NA} = \frac{2\pi a}{\lambda_0} \sqrt{n_1^2 - n_2^2}",
                "derivation_steps": [
                    "Apply Snell's law at the fiber entrance face: n_0 * sin(theta_a) = n_1 * sin(theta_r), where n_0 is refractive index of medium (air n_0 approx 1).",
                    "At the core-cladding boundary, total internal reflection requires incidence angle phi_c to satisfy sin(phi_c) = n_2 / n_1.",
                    "In the internal right triangle, theta_r = 90 deg - phi_c, implying sin(theta_r) = cos(phi_c) = sqrt(1 - (n_2/n_1)^2).",
                    "Multiplying by n_1 yields the numerical aperture: NA = n_0 * sin(theta_a) = sqrt(n_1^2 - n_2^2).",
                    "Normalized frequency parameter V governs supported guided modes; single-mode operation (supporting only fundamental HE11 mode) is strictly guaranteed when V <= 2.4048 (the first root of Bessel function J0)."
                ],
                "parameters": [
                    {"symbol": "NA", "unit": "dimensionless", "definition": "Numerical aperture (light gathering capacity)"},
                    {"symbol": "V", "unit": "dimensionless", "definition": "Normalized frequency / V-number parameter"},
                    {"symbol": "n_1", "unit": "dimensionless", "definition": "Core refractive index"},
                    {"symbol": "n_2", "unit": "dimensionless", "definition": "Cladding refractive index"},
                    {"symbol": "a", "unit": "m (um)", "definition": "Fiber core radius"},
                    {"symbol": "lambda_0", "unit": "m (nm)", "definition": "Free-space optical carrier wavelength"}
                ]
            }
        ],
        "worked_examples": [
            {
                "title": "Single-Mode Optical Fiber Cutoff Wavelength and Acceptance Angle Design",
                "problem_statement": "A silica step-index optical fiber has a core radius a = 4.1 um, core index n_1 = 1.468, and cladding index n_2 = 1.462. In air (n_0 = 1.0), determine: (a) Numerical aperture NA, (b) Acceptance angle theta_max, and (c) The cutoff wavelength lambda_c above which the fiber operates strictly in single-mode regime (V <= 2.405).",
                "step_by_step_solution": [
                    "Step 1: Compute numerical aperture: NA = sqrt(n_1^2 - n_2^2) = sqrt(1.468^2 - 1.462^2) = sqrt(2.155024 - 2.137444) = sqrt(0.01758) = 0.1326.",
                    "Step 2: Compute acceptance angle in air (n_0 = 1): theta_max = arcsin(NA) = arcsin(0.1326) = 7.62 degrees (full cone angle 2*theta = 15.24 degrees).",
                    "Step 3: Relate normalized frequency V to cutoff condition: V_c = 2.4048 = (2*pi*a / lambda_c) * NA.",
                    "Step 4: Solve for cutoff wavelength: lambda_c = (2*pi*a * NA) / 2.4048 = (2 * pi * 4.1e-6 * 0.13259) / 2.4048 = 3.4158e-6 / 2.4048 = 1.4204 um = 1420.4 nm.",
                    "Step 5: Interpretation: At standard telecom wavelength lambda = 1550 nm > 1420.4 nm, V = 2.204 < 2.405, guaranteeing single-mode propagation."
                ],
                "verified_output": "NA = 0.1326, Acceptance Angle = 7.62 degrees, Cutoff Wavelength lambda_c = 1420.4 nm (Single-mode at 1550 nm)"
            }
        ],
        "simulation_activities": [
            {
                "lab_id": "OPT_LAB_01",
                "title": "Optical Link Power Budget & Chromatic Dispersion Penalty Simulator",
                "component": "RfSmithChartHub",
                "instructions": "Configure a 40 km single-mode fiber span at 1550 nm with transmitter power Pt = +3 dBm and receiver sensitivity Pr = -28 dBm. Account for connector loss (0.5 dB * 2), splice loss (0.1 dB * 4), and fiber attenuation (0.2 dB/km) to calculate operating link margin.",
                "expected_telemetry": {"total_attenuation_db": 9.4, "operating_margin_db": 21.6, "dispersion_ps_per_nm": 680.0}
            }
        ],
        "assessment_questions": [
            {
                "id": "OPT_Q1",
                "bloom_level": "L4 (Analyze)",
                "question": "What is the critical normalized frequency (V-number) condition required for a step-index optical fiber to operate strictly as a single-mode waveguide?",
                "options": [
                    "V <= 2.405 (the first zero of the J0 Bessel function)",
                    "V >= 3.832 (ensuring higher-order mode propagation)",
                    "V = 1.000 (matching air wave impedance)",
                    "V <= 0.707 (corresponding to -3dB half-power cutoff)"
                ],
                "correct_index": 0,
                "explanation": "In a step-index cylindrical dielectric waveguide, the cutoff for the second guided mode (TE01 / TM01) occurs at V = 2.4048, which is the first root of the Bessel function J0(x). Below this value, only the fundamental HE11 mode can propagate."
            }
        ]
    }
}
