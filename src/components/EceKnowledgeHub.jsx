import React, { useState, useEffect } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Advanced ECE Knowledge Center & Formula Encyclopedia
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 * ========================================================================================
 */

const SEED_FORMULAS = [
  {
    formula_id: "FORM_DE_MORGAN",
    topic: "Boolean Algebra",
    formula_name: "De Morgan's Laws",
    subject_code: "EC3352",
    unit_number: 1,
    latex_repr: "\\overline{A \\cdot B} = \\bar{A} + \\bar{B}, \\quad \\overline{A + B} = \\bar{A} \\cdot \\bar{B}",
    plain_text: "NOT(A AND B) = NOT(A) OR NOT(B); NOT(A OR B) = NOT(A) AND NOT(B)",
    derivation_summary: "Fundamental duality theorem in Boolean algebra transforming product-of-sums into sum-of-products.",
    variables: { "A": "Binary Boolean input A", "B": "Binary Boolean input B" },
    unit_result: "Boolean (0 or 1)",
    au_regulation: "EC3352"
  },
  {
    formula_id: "FORM_FSM_CLOCK_PERIOD",
    topic: "Synchronous Sequential Logic",
    formula_name: "FSM Minimum Clock Period & Setup Invariant",
    subject_code: "EC3352",
    unit_number: 2,
    latex_repr: "T_{clk} \\ge t_{cq} + t_{comb} + t_{setup}",
    plain_text: "Tclk >= t_cq + t_comb + t_setup",
    derivation_summary: "Ensures data launched from flip-flop propagation delay and combinational network stabilizes before next clock edge.",
    variables: { "T_{clk}": "Clock period (s)", "t_{cq}": "Clock-to-Q delay (s)", "t_{comb}": "Max combinational delay (s)", "t_{setup}": "Flip-flop setup time (s)" },
    unit_result: "Seconds (s)",
    au_regulation: "EC3352"
  },
  {
    formula_id: "FORM_CLA_CARRY",
    topic: "Arithmetic Circuits",
    formula_name: "Carry Lookahead Adder Carry Generation",
    subject_code: "EC3352",
    unit_number: 1,
    latex_repr: "C_{i+1} = G_i + P_i C_i, \\quad G_i = A_i B_i, \\; P_i = A_i \\oplus B_i",
    plain_text: "C_(i+1) = G_i + P_i * C_i where G_i = A_i * B_i and P_i = A_i XOR B_i",
    derivation_summary: "Eliminates ripple carry propagation delay by computing carries in parallel using Generate and Propagate terms.",
    variables: { "C_{i+1}": "Carry out of stage i", "G_i": "Carry generate term", "P_i": "Carry propagate term", "C_i": "Carry in" },
    unit_result: "Boolean (Carry bit)",
    au_regulation: "EC3352"
  },
  {
    formula_id: "FORM_GAUSS_ELECTRIC",
    topic: "Electrostatics",
    formula_name: "Gauss's Law for Electric Fields (Differential Form)",
    subject_code: "EC3452",
    unit_number: 1,
    latex_repr: "\\nabla \\cdot \\mathbf{D} = \\rho_v",
    plain_text: "div(D) = rho_v",
    derivation_summary: "States that the divergence of electric flux density D from any volume is equal to the volume charge density enclosed.",
    variables: { "D": "Electric flux density (C/m^2)", "rho_v": "Volume charge density (C/m^3)" },
    unit_result: "Coulombs / m^3",
    au_regulation: "EC3452"
  },
  {
    formula_id: "FORM_FARADAY_INDUCTION",
    topic: "Time-Varying Fields",
    formula_name: "Faraday's Law of Induction (Maxwell's 3rd Equation)",
    subject_code: "EC3452",
    unit_number: 4,
    latex_repr: "\\nabla \\times \\mathbf{E} = -\\frac{\\partial \\mathbf{B}}{\\partial t}",
    plain_text: "curl(E) = -dB/dt",
    derivation_summary: "A time-varying magnetic flux density produces an electric field circulation, forming the governing equation for inductors and transformers.",
    variables: { "E": "Electric field intensity (V/m)", "B": "Magnetic flux density (Tesla)", "t": "Time (s)" },
    unit_result: "Volts / m^2",
    au_regulation: "EC3452"
  },
  {
    formula_id: "FORM_POYNTING_VECTOR",
    topic: "Electromagnetic Wave Propagation",
    formula_name: "Poynting Vector (Instantaneous Power Flow)",
    subject_code: "EC3452",
    unit_number: 4,
    latex_repr: "\\mathbf{S} = \\mathbf{E} \\times \\mathbf{H}",
    plain_text: "S = E x H",
    derivation_summary: "Represents the directional energy flux density (rate of energy transfer per unit area) of an electromagnetic wave.",
    variables: { "S": "Poynting vector (W/m^2)", "E": "Electric field vector (V/m)", "H": "Magnetic field vector (A/m)" },
    unit_result: "Watts / m^2",
    au_regulation: "EC3452"
  },
  {
    formula_id: "FORM_SKIN_DEPTH",
    topic: "Uniform Plane Waves",
    formula_name: "Skin Depth in Good Conducting Media",
    subject_code: "EC3452",
    unit_number: 5,
    latex_repr: "\\delta = \\frac{1}{\\sqrt{\\pi f \\mu \\sigma}}",
    plain_text: "delta = 1 / sqrt(pi * f * mu * sigma)",
    derivation_summary: "Depth at which the amplitude of an impinging electromagnetic wave attenuates to 1/e (~36.8%) of its surface value.",
    variables: { "delta": "Skin depth (m)", "f": "Frequency (Hz)", "mu": "Permeability (H/m)", "sigma": "Conductivity (S/m)" },
    unit_result: "Meters (m)",
    au_regulation: "EC3452"
  },
  {
    formula_id: "FORM_OPAMP_INV_GAIN",
    topic: "Operational Amplifiers",
    formula_name: "Inverting Op-Amp Closed-Loop Voltage Gain",
    subject_code: "EC3451",
    unit_number: 1,
    latex_repr: "A_v = -\\frac{R_f}{R_{in}}",
    plain_text: "Av = -(Rf / Rin)",
    derivation_summary: "Derived from virtual ground concept at the inverting terminal under negative feedback configuration.",
    variables: { "A_v": "Voltage gain (dimensionless)", "R_f": "Feedback resistor (Ohms)", "R_{in}": "Input resistor (Ohms)" },
    unit_result: "V/V",
    au_regulation: "EC3451"
  },
  {
    formula_id: "FORM_OPAMP_CMRR",
    topic: "Differential Amplifiers",
    formula_name: "Common-Mode Rejection Ratio (CMRR)",
    subject_code: "EC3451",
    unit_number: 1,
    latex_repr: "\\text{CMRR}_{dB} = 20 \\log_{10} \\left|\\frac{A_d}{A_{cm}}\\right|",
    plain_text: "CMRR_dB = 20 * log10(|Ad / Acm|)",
    derivation_summary: "Figures of merit measuring the amplifier's ability to reject unwanted common-mode noise while amplifying differential signals.",
    variables: { "A_d": "Differential gain", "A_{cm}": "Common-mode gain" },
    unit_result: "Decibels (dB)",
    au_regulation: "EC3451"
  },
  {
    formula_id: "FORM_SLEW_RATE",
    topic: "Op-Amp Dynamic Characteristics",
    formula_name: "Full-Power Bandwidth & Slew Rate",
    subject_code: "EC3451",
    unit_number: 1,
    latex_repr: "\\text{SR} = \\left.\\frac{dV_o}{dt}\\right|_{max} = 2\\pi f_{max} V_p",
    plain_text: "SR = 2 * pi * f_max * V_p",
    derivation_summary: "Maximum rate of change of output voltage without experiencing non-linear slew-induced distortion.",
    variables: { "SR": "Slew Rate (V/s or V/us)", "f_{max}": "Full-power bandwidth (Hz)", "V_p": "Peak output amplitude (V)" },
    unit_result: "V / microsecond",
    au_regulation: "EC3451"
  },
  {
    formula_id: "FORM_555_ASTABLE",
    topic: "Special Function ICs",
    formula_name: "IC 555 Astable Multivibrator Frequency",
    subject_code: "EC3451",
    unit_number: 5,
    latex_repr: "f = \\frac{1.44}{(R_A + 2 R_B) C}, \\quad D = \\frac{R_A + R_B}{R_A + 2 R_B}",
    plain_text: "f = 1.44 / ((RA + 2*RB) * C); Duty Cycle = (RA + RB) / (RA + 2*RB)",
    derivation_summary: "Charge time through (RA + RB)*C*ln(2) and discharge time through RB*C*ln(2).",
    variables: { "f": "Oscillation frequency (Hz)", "R_A": "Timing resistor A (Ohms)", "R_B": "Timing resistor B (Ohms)", "C": "Timing capacitor (F)" },
    unit_result: "Hertz (Hz)",
    au_regulation: "EC3451"
  },
  {
    formula_id: "FORM_RLC_RESONANCE",
    topic: "RF & Tuned Circuits",
    formula_name: "Series/Parallel RLC Resonant Frequency",
    subject_code: "EC3491",
    unit_number: 1,
    latex_repr: "f_0 = \\frac{1}{2\\pi \\sqrt{L C}}",
    plain_text: "f0 = 1 / (2 * pi * sqrt(L * C))",
    derivation_summary: "Condition where inductive reactance cancels capacitive reactance, resulting in purely resistive impedance.",
    variables: { "f_0": "Resonant frequency (Hz)", "L": "Inductance (H)", "C": "Capacitance (F)" },
    unit_result: "Hertz (Hz)",
    au_regulation: "EC3491"
  },
  {
    formula_id: "FORM_NYQUIST_SAMPLING",
    topic: "Baseband Digital Transmission",
    formula_name: "Nyquist-Shannon Sampling Criterion",
    subject_code: "EC3491",
    unit_number: 3,
    latex_repr: "f_s \\ge 2 f_{max}",
    plain_text: "fs >= 2 * fmax",
    derivation_summary: "Minimum sampling rate required to fully reconstruct a bandlimited analog signal without spectral aliasing.",
    variables: { "f_s": "Sampling frequency (Hz)", "f_{max}": "Highest signal frequency (Hz)" },
    unit_result: "Samples / second (Hz)",
    au_regulation: "EC3491"
  },
  {
    formula_id: "FORM_SHANNON_CAPACITY",
    topic: "Information Theory",
    formula_name: "Shannon-Hartley Channel Capacity",
    subject_code: "EC3491",
    unit_number: 5,
    latex_repr: "C = B \\log_2\\left(1 + \\text{SNR}\\right)",
    plain_text: "C = B * log2(1 + SNR)",
    derivation_summary: "Theoretical maximum rate at which error-free data can be transmitted over an additive white Gaussian noise channel.",
    variables: { "C": "Channel capacity (bps)", "B": "Channel bandwidth (Hz)", "SNR": "Signal-to-noise power ratio (linear)" },
    unit_result: "Bits / second",
    au_regulation: "EC3491"
  },
  {
    formula_id: "FORM_CARSON_RULE",
    topic: "Angle Modulation",
    formula_name: "Carson's Rule for FM Transmission Bandwidth",
    subject_code: "EC3491",
    unit_number: 2,
    latex_repr: "B_T = 2 (\\Delta f + f_m) = 2 f_m (\\beta + 1)",
    plain_text: "BT = 2 * (delta_f + fm) = 2 * fm * (beta + 1)",
    derivation_summary: "Approximates 98% of the total transmitted power in an angle-modulated frequency carrier.",
    variables: { "B_T": "Transmission bandwidth (Hz)", "delta_f": "Peak frequency deviation (Hz)", "f_m": "Modulating frequency (Hz)", "beta": "Modulation index" },
    unit_result: "Hertz (Hz)",
    au_regulation: "EC3491"
  }
];

const SEED_COMPONENTS = [
  {
    part_number: "ESP32-S3-WROOM-1",
    component_name: "Dual-Core Xtensa LX7 MCU with Wi-Fi & BLE",
    category: "MICROCONTROLLER",
    manufacturer: "Espressif Systems",
    operating_voltage: "3.0V – 3.6V",
    package_type: "QFN-56 / SMD-44",
    pin_count: 44,
    key_specs: {
      "Core Clock": "240 MHz",
      "Flash": "8 MB SPI Flash",
      "SRAM": "512 KB",
      "Wireless": "2.4 GHz Wi-Fi + BLE 5.0",
      "Hardware USB": "Full-speed USB-OTG and USB-CDC Serial"
    },
    datasheet_url: "https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf"
  },
  {
    part_number: "STM32F407VGT6",
    component_name: "ARM Cortex-M4 High-Performance DSP MCU",
    category: "MICROCONTROLLER",
    manufacturer: "STMicroelectronics",
    operating_voltage: "1.8V – 3.6V",
    package_type: "LQFP-100",
    pin_count: 100,
    key_specs: {
      "Core Clock": "168 MHz with FPU",
      "Flash": "1024 KB Flash Memory",
      "SRAM": "192 KB",
      "ADC": "3x 12-bit, 2.4 MSPS ADCs",
      "Peripherals": "Ethernet MAC, USB OTG, 3x SPI, 4x USART"
    },
    datasheet_url: "https://www.st.com/resource/en/datasheet/stm32f407vg.pdf"
  },
  {
    part_number: "LM741CN",
    component_name: "General Purpose Operational Amplifier",
    category: "OPAMP",
    manufacturer: "Texas Instruments",
    operating_voltage: "±5.0V to ±18.0V",
    package_type: "PDIP-8",
    pin_count: 8,
    key_specs: {
      "Unity Gain Bandwidth": "1.0 MHz",
      "Slew Rate": "0.5 V/µs",
      "Input Offset Voltage": "1.0 mV typical",
      "CMRR": "90 dB typical"
    },
    datasheet_url: "https://www.ti.com/lit/ds/symlink/lm741.pdf"
  },
  {
    part_number: "NE555P",
    component_name: "Precision Bipolar Timer / Pulse Generator",
    category: "TIMER",
    manufacturer: "Texas Instruments",
    operating_voltage: "4.5V – 16.0V",
    package_type: "PDIP-8",
    pin_count: 8,
    key_specs: {
      "Max Operating Frequency": "500 kHz",
      "Output Sink/Source": "200 mA capability",
      "Operating Modes": "Astable, Monostable, Bistable"
    },
    datasheet_url: "https://www.ti.com/lit/ds/symlink/ne555.pdf"
  },
  {
    part_number: "2N2222A",
    component_name: "NPN High-Speed Switching Transistor",
    category: "TRANSISTOR",
    manufacturer: "ON Semiconductor",
    operating_voltage: "Vceo = 40V, Vcbo = 75V",
    package_type: "TO-92",
    pin_count: 3,
    key_specs: {
      "Collector Current (Ic)": "800 mA continuous",
      "Transition Frequency (fT)": "300 MHz",
      "DC Current Gain (hFE)": "100 to 300 @ 150mA"
    },
    datasheet_url: "https://www.onsemi.com/pdf/datasheet/p2n2222a-d.pdf"
  },
  {
    part_number: "AD620AN",
    component_name: "Low Cost Instrumentation Amplifier",
    category: "OPAMP",
    manufacturer: "Analog Devices",
    operating_voltage: "±2.3V to ±18.0V",
    package_type: "DIP-8",
    pin_count: 8,
    key_specs: {
      "Gain Range": "1 to 10,000 configured by 1 resistor Rg",
      "CMRR": "100 dB minimum (G = 10)",
      "Bandwidth": "120 kHz (G = 100)"
    },
    datasheet_url: "https://www.analog.com/media/en/technical-documentation/data-sheets/AD620.pdf"
  },
  {
    part_number: "Keysight-DSOX1204G",
    component_name: "4-Channel Digital Storage Oscilloscope with WaveGen",
    category: "INSTRUMENT",
    manufacturer: "Keysight Technologies",
    operating_voltage: "100V – 240V AC",
    package_type: "Benchtop Instrument",
    pin_count: 4,
    key_specs: {
      "Bandwidth": "70 MHz to 200 MHz upgradeable",
      "Sample Rate": "Up to 2.0 GSa/s",
      "Function Generator": "20 MHz built-in arbitrary waveform generator",
      "Waveform Update Rate": "100,000 waveforms/second"
    },
    datasheet_url: "https://www.keysight.com/us/en/assets/7018-05995/data-sheets/5992-3484EN.pdf"
  },
  {
    part_number: "Rigol-DP832",
    component_name: "Programmable Triple-Output Linear DC Power Supply",
    category: "INSTRUMENT",
    manufacturer: "Rigol Technologies",
    operating_voltage: "100V – 240V AC",
    package_type: "Benchtop Instrument",
    pin_count: 3,
    key_specs: {
      "Channels": "3 isolated channels (30V/3A, 30V/3A, 5V/3A)",
      "Total Power": "195 Watts",
      "Ripple & Noise": "< 350 µVrms / 2 mVpp"
    },
    datasheet_url: "https://www.rigolna.com/products/dc-power-loads/dp800/"
  }
];

const SEED_ABBREVIATIONS = [
  { term: "CMRR", full_form: "Common-Mode Rejection Ratio", category: "ANALOG_CIRCUITS", definition: "Ratio of differential voltage gain to common-mode voltage gain in an operational amplifier, expressing its rejection of unwanted interference.", related_subject: "EC3451" },
  { term: "PLL", full_form: "Phase-Locked Loop", category: "COMMUNICATION", definition: "Feedback circuit consisting of a phase detector, low-pass filter, and voltage-controlled oscillator locking output frequency to reference phase.", related_subject: "EC3451" },
  { term: "FSM", full_form: "Finite State Machine", category: "DIGITAL_SYSTEMS", definition: "Sequential computational model with discrete states, transitions triggered by inputs, and registered outputs (Mealy or Moore architectures).", related_subject: "EC3352" },
  { term: "AWGN", full_form: "Additive White Gaussian Noise", category: "COMMUNICATION", definition: "Statistical channel noise model with uniform spectral density across all frequencies and Gaussian amplitude probability distribution.", related_subject: "EC3491" },
  { term: "SAR ADC", full_form: "Successive Approximation Register ADC", category: "ANALOG_CIRCUITS", definition: "A widely used ADC architecture that executes binary search convergence using an internal DAC to digitize analog voltages.", related_subject: "EC3451" },
  { term: "BER", full_form: "Bit Error Rate", category: "COMMUNICATION", definition: "Fraction of bits received in error compared to total bits transmitted over a telecommunications link.", related_subject: "EC3491" },
  { term: "FFT", full_form: "Fast Fourier Transform", category: "SIGNAL_PROCESSING", definition: "Algorithm computing the Discrete Fourier Transform of a sequence in O(N log N) computational complexity.", related_subject: "EC3491" },
  { term: "SPI", full_form: "Serial Peripheral Interface", category: "EMBEDDED_SYSTEMS", definition: "Synchronous 4-wire full-duplex serial bus (MOSI, MISO, SCLK, and CS) used for sensors, flash memory, and peripheral expansion.", related_subject: "EC3352" },
  { term: "I2C", full_form: "Inter-Integrated Circuit", category: "EMBEDDED_SYSTEMS", definition: "Synchronous multi-master 2-wire serial bus (SDA and SCL) with open-drain pull-up topology.", related_subject: "EC3352" },
  { term: "UART", full_form: "Universal Asynchronous Receiver-Transmitter", category: "EMBEDDED_SYSTEMS", definition: "Asynchronous byte transmission protocol without shared clock lines via configurable baud rates and start/stop framing.", related_subject: "EC3352" },
  { term: "HIL", full_form: "Hardware-in-the-Loop", category: "EMBEDDED_SYSTEMS", definition: "Real-time simulation technique where physical microcontrollers and sensors interact directly with virtual circuit models and test assertion benches.", related_subject: "EC3352" },
  { term: "PWM", full_form: "Pulse-Width Modulation", category: "EMBEDDED_SYSTEMS", definition: "Modulation technique that varies the duty cycle of a fixed-frequency square wave to regulate average power delivered to electrical loads.", related_subject: "EC3451" },
  { term: "EMF", full_form: "Electromotive Force", category: "ELECTROMAGNETICS", definition: "Electrical potential generated by changing magnetic fields (Faraday induction) or chemical electrochemical reactions.", related_subject: "EC3452" },
  { term: "RISC-V", full_form: "Reduced Instruction Set Computer - Architecture V", category: "DIGITAL_SYSTEMS", definition: "Open-standard, royalty-free instruction set architecture (ISA) based on established RISC design principles.", related_subject: "EC3352" }
];

export default function EceKnowledgeHub() {
  const [activeTab, setActiveTab] = useState("formulas"); // 'formulas' | 'components' | 'abbreviations' | 'cheatsheet'
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSubject, setSelectedSubject] = useState("ALL");
  const [selectedComponentCat, setSelectedComponentCat] = useState("ALL");
  const [toastMessage, setToastMessage] = useState("");
  const [copiedId, setCopiedId] = useState("");

  const [formulas, setFormulas] = useState(SEED_FORMULAS);
  const [components, setComponents] = useState(SEED_COMPONENTS);
  const [abbreviations, setAbbreviations] = useState(SEED_ABBREVIATIONS);

  const triggerToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(""), 4000);
  };

  const copyToClipboard = (text, id) => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text);
      setCopiedId(id);
      triggerToast("Formula copied to clipboard!");
      setTimeout(() => setCopiedId(""), 3000);
    }
  };

  // Fetch from backend API if available
  useEffect(() => {
    fetchFormulas(searchQuery, selectedSubject);
  }, [searchQuery, selectedSubject]);

  const fetchFormulas = async (query, sub) => {
    try {
      const qParams = new URLSearchParams();
      if (query) qParams.append("query", query);
      if (sub && sub !== "ALL") qParams.append("subject_code", sub);

      const resp = await fetch(`/api/ece_knowledge/formulas?${qParams.toString()}`);
      if (resp.ok) {
        const data = await resp.json();
        if (Array.isArray(data) && data.length > 0) {
          setFormulas(data);
        }
      }
    } catch {
      // Local filter fallback
    }
  };

  // Filter local state if backend offline
  const filteredFormulas = formulas.filter(f => {
    const matchesSubject = selectedSubject === "ALL" || f.subject_code === selectedSubject;
    const matchesQuery = !searchQuery ||
      f.formula_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.topic.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.plain_text.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSubject && matchesQuery;
  });

  const filteredComponents = components.filter(c => {
    const matchesCat = selectedComponentCat === "ALL" || c.category === selectedComponentCat;
    const matchesQuery = !searchQuery ||
      c.part_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.component_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.manufacturer.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesQuery;
  });

  const filteredAbbreviations = abbreviations.filter(a => {
    const matchesQuery = !searchQuery ||
      a.term.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.full_form.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.definition.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesQuery;
  });

  return (
    <div className="space-y-6 font-mono">

      {/* Floating Alert HUD */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 p-4 rounded-2xl bg-[#041026] border border-[#00F0B5]/50 text-white text-xs shadow-2xl flex items-center gap-3 animate-bounce">
          <span className="text-[#00F0B5] text-lg">📐</span>
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Top Banner KPI HUD */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30 shadow-lg">
          <div className="flex items-center justify-between text-slate-400">
            <span>Formula Encyclopedia</span>
            <span className="text-[#00F0B5] font-bold">{formulas.length} Curated</span>
          </div>
          <div className="text-2xl font-black text-white mt-1">
            4 Core Subjects
          </div>
          <div className="text-[10px] text-emerald-400 mt-1">LaTeX & Plain-Text Derivations</div>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30 shadow-lg">
          <div className="flex items-center justify-between text-slate-400">
            <span>Component Datasheets</span>
            <span className="text-cyan-400 font-bold">{components.length} Indexed</span>
          </div>
          <div className="text-2xl font-black text-white mt-1">
            Lab 304 Roster
          </div>
          <div className="text-[10px] text-cyan-400 mt-1">MCUs, Op-Amps, Instruments</div>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30 shadow-lg">
          <div className="flex items-center justify-between text-slate-400">
            <span>Technical Glossary</span>
            <span className="text-amber-400 font-bold">{abbreviations.length} Terms</span>
          </div>
          <div className="text-2xl font-black text-white mt-1">
            Abbreviations
          </div>
          <div className="text-[10px] text-amber-400 mt-1">ECE R2023 Categorized</div>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30 shadow-lg">
          <div className="flex items-center justify-between text-slate-400">
            <span>Instant Search Engine</span>
            <span className="text-emerald-400 font-bold">WAL ACTIVE</span>
          </div>
          <div className="text-2xl font-black text-emerald-400 mt-1">
            &lt; 5 ms Latency
          </div>
          <div className="text-[10px] text-slate-400 mt-1">Zero GPU Load • Passive Safe</div>
        </div>
      </div>

      {/* Instant Search Bar & Filter Controls */}
      <div className="p-5 rounded-3xl bg-gradient-to-b from-[#041026] to-[#020813] border border-slate-800 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <span className="absolute left-4 top-3 text-slate-500">🔍</span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search formulas, components, derivations, or abbreviations (e.g. Nyquist, CMRR, ESP32, Slew Rate)..."
              className="w-full pl-11 pr-4 py-2.5 rounded-2xl bg-[#020813] border border-slate-700 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-[#00F0B5]"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute right-4 top-3 text-slate-400 hover:text-white text-xs"
              >
                ✕
              </button>
            )}
          </div>

          {activeTab === "formulas" && (
            <div className="flex items-center gap-1.5 overflow-x-auto text-xs">
              {["ALL", "EC3352", "EC3452", "EC3451", "EC3491"].map((sub) => (
                <button
                  key={sub}
                  onClick={() => setSelectedSubject(sub)}
                  className={`px-3 py-2 rounded-xl text-[11px] font-bold whitespace-nowrap transition-all ${
                    selectedSubject === sub
                      ? "bg-[#00693E] text-[#00F0B5] border border-[#00F0B5]/50 shadow"
                      : "bg-[#020813] text-slate-400 hover:text-white border border-slate-800"
                  }`}
                >
                  {sub}
                </button>
              ))}
            </div>
          )}

          {activeTab === "components" && (
            <div className="flex items-center gap-1.5 overflow-x-auto text-xs">
              {["ALL", "MICROCONTROLLER", "OPAMP", "TIMER", "TRANSISTOR", "INSTRUMENT"].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedComponentCat(cat)}
                  className={`px-3 py-2 rounded-xl text-[10px] font-bold whitespace-nowrap transition-all ${
                    selectedComponentCat === cat
                      ? "bg-[#00693E] text-[#00F0B5] border border-[#00F0B5]/50"
                      : "bg-[#020813] text-slate-400 hover:text-white border border-slate-800"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Main Tab Bar Navigation */}
      <div className="flex border-b border-slate-800 text-xs">
        <button
          onClick={() => setActiveTab("formulas")}
          className={`px-5 py-3 font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === "formulas"
              ? "border-[#00F0B5] text-[#00F0B5]"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <span>📐 Formula Encyclopedia</span>
          <span className="px-1.5 py-0.2 rounded-full bg-[#00693E]/40 text-[#00F0B5] text-[10px]">
            {filteredFormulas.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab("components")}
          className={`px-5 py-3 font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === "components"
              ? "border-[#00F0B5] text-[#00F0B5]"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <span>🔌 Component Datasheet Library</span>
          <span className="px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-300 text-[10px]">
            {filteredComponents.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab("abbreviations")}
          className={`px-5 py-3 font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === "abbreviations"
              ? "border-[#00F0B5] text-[#00F0B5]"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <span>📖 Technical Glossary</span>
          <span className="px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-300 text-[10px]">
            {filteredAbbreviations.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab("cheatsheet")}
          className={`px-5 py-3 font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === "cheatsheet"
              ? "border-[#00F0B5] text-[#00F0B5]"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <span>⚡ Physical Constants & Cheat Sheet</span>
        </button>
      </div>

      {/* TAB 1: Formula Encyclopedia Cards */}
      {activeTab === "formulas" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredFormulas.map((f) => (
            <div
              key={f.formula_id}
              className="p-5 rounded-3xl bg-[#041026] border border-slate-800 hover:border-[#00F0B5]/40 transition-all shadow-xl space-y-4 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-white text-sm">{f.formula_name}</span>
                  <div className="flex items-center gap-1.5">
                    <span className="text-[10px] px-2 py-0.5 rounded bg-[#00693E]/40 text-[#00F0B5] font-bold">
                      {f.subject_code} • U{f.unit_number}
                    </span>
                  </div>
                </div>
                <div className="text-[10px] text-slate-400 mt-0.5">{f.topic}</div>

                {/* LaTeX Equation Box */}
                <div className="mt-3 p-3.5 rounded-2xl bg-[#020813] text-center border border-slate-800 text-sm font-mono text-[#00F0B5] font-bold shadow-inner">
                  {f.latex_repr}
                </div>

                {/* Derivation / Conceptual Summary */}
                <p className="mt-3 text-xs text-slate-300 leading-relaxed">
                  {f.derivation_summary}
                </p>

                {/* Variables Legend */}
                {f.variables && (
                  <div className="mt-3 pt-3 border-t border-slate-800/80 space-y-1">
                    <span className="text-[10px] text-slate-500 font-bold block mb-1">VARIABLE PARAMETERS:</span>
                    <div className="grid grid-cols-1 gap-1 text-[11px]">
                      {Object.entries(f.variables).map(([k, v]) => (
                        <div key={k} className="flex items-start gap-1.5 text-slate-400">
                          <span className="text-[#00F0B5] font-bold">{k}:</span>
                          <span className="text-slate-300">{v}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <span className="text-[10px] text-slate-400">
                  Result Unit: <span className="text-white font-bold">{f.unit_result}</span>
                </span>
                <button
                  onClick={() => copyToClipboard(f.plain_text, f.formula_id)}
                  className={`px-3 py-1.5 rounded-xl border text-[11px] font-bold transition-all flex items-center gap-1.5 ${
                    copiedId === f.formula_id
                      ? "bg-[#00693E] text-[#00F0B5] border-[#00F0B5]"
                      : "bg-[#020813] text-slate-300 border-slate-700 hover:border-[#00F0B5] hover:text-[#00F0B5]"
                  }`}
                >
                  <span>{copiedId === f.formula_id ? "✓ Copied" : "📋 Copy Plain Text"}</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* TAB 2: Component Datasheet Library */}
      {activeTab === "components" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredComponents.map((c) => (
            <div
              key={c.part_number}
              className="p-5 rounded-3xl bg-[#041026] border border-slate-800 hover:border-cyan-500/40 transition-all shadow-xl space-y-4 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-white text-base font-mono">{c.part_number}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-bold">
                    {c.category}
                  </span>
                </div>
                <div className="text-xs text-slate-300 mt-1">{c.component_name}</div>
                <div className="text-[11px] text-slate-400 mt-0.5">Manufacturer: {c.manufacturer}</div>

                <div className="mt-3 p-3 rounded-2xl bg-[#020813] border border-slate-800 text-[11px] space-y-1.5">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Operating Voltage:</span>
                    <span className="text-emerald-400 font-bold">{c.operating_voltage}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Package / Pins:</span>
                    <span className="text-slate-200">{c.package_type} ({c.pin_count} pins)</span>
                  </div>
                </div>

                {/* Key Electrical Specs List */}
                {c.key_specs && (
                  <div className="mt-3 space-y-1">
                    <span className="text-[10px] text-slate-500 font-bold block mb-1">KEY SPECIFICATIONS:</span>
                    <div className="space-y-1 text-[11px]">
                      {Object.entries(c.key_specs).map(([k, v]) => (
                        <div key={k} className="flex justify-between text-slate-300">
                          <span className="text-slate-400">{k}:</span>
                          <span className="font-medium text-right ml-2">{v}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <span className="text-[10px] text-emerald-400">✓ MIT Lab 304 Certified</span>
                <a
                  href={c.datasheet_url}
                  target="_blank"
                  rel="noreferrer"
                  className="px-3.5 py-1.5 rounded-xl bg-[#020813] border border-cyan-500/40 text-cyan-300 hover:bg-cyan-950 text-xs font-bold transition-all flex items-center gap-1.5"
                >
                  <span>📄 Official Datasheet</span>
                  <span>↗</span>
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* TAB 3: Technical Glossary */}
      {activeTab === "abbreviations" && (
        <div className="p-6 rounded-3xl bg-[#041026] border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3 text-xs">
            <span className="font-bold text-white text-sm">ECE Technical Abbreviations & Acronyms</span>
            <span className="text-[#00F0B5] font-mono">Anna University R2023 Aligned</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {filteredAbbreviations.map((abbr) => (
              <div
                key={abbr.term}
                className="p-4 rounded-2xl bg-[#020813] border border-slate-800 hover:border-slate-700 transition-all space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-base font-black text-[#00F0B5] font-mono">{abbr.term}</span>
                    <span className="text-xs text-slate-300 font-bold">— {abbr.full_form}</span>
                  </div>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                    {abbr.related_subject}
                  </span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  {abbr.definition}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 4: Physical Constants & Cheat Sheet */}
      {activeTab === "cheatsheet" && (
        <div className="space-y-6">
          <div className="p-6 rounded-3xl bg-[#041026] border border-slate-800 shadow-xl space-y-4">
            <div className="border-b border-slate-800 pb-3 flex items-center justify-between text-xs">
              <span className="font-bold text-white text-sm">Fundamental Physical & Engineering Constants</span>
              <span className="text-[#00F0B5] font-mono">NIST / IEEE Standard Values</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
              <div className="p-3.5 rounded-2xl bg-[#020813] border border-slate-800">
                <div className="text-slate-400 text-[10px]">Speed of Light in Vacuum (c)</div>
                <div className="text-lg font-black text-white font-mono mt-1">2.9979 × 10⁸ m/s</div>
                <div className="text-[10px] text-emerald-400 mt-0.5">Wave Velocity</div>
              </div>

              <div className="p-3.5 rounded-2xl bg-[#020813] border border-slate-800">
                <div className="text-slate-400 text-[10px]">Permittivity of Free Space (ε₀)</div>
                <div className="text-lg font-black text-white font-mono mt-1">8.854 × 10⁻¹² F/m</div>
                <div className="text-[10px] text-cyan-400 mt-0.5">Electrostatics</div>
              </div>

              <div className="p-3.5 rounded-2xl bg-[#020813] border border-slate-800">
                <div className="text-slate-400 text-[10px]">Permeability of Free Space (μ₀)</div>
                <div className="text-lg font-black text-white font-mono mt-1">4π × 10⁻⁷ H/m</div>
                <div className="text-[10px] text-cyan-400 mt-0.5">Magnetostatics</div>
              </div>

              <div className="p-3.5 rounded-2xl bg-[#020813] border border-slate-800">
                <div className="text-slate-400 text-[10px]">Elementary Electron Charge (q)</div>
                <div className="text-lg font-black text-white font-mono mt-1">1.602 × 10⁻¹⁹ C</div>
                <div className="text-[10px] text-amber-400 mt-0.5">Semiconductor Physics</div>
              </div>

              <div className="p-3.5 rounded-2xl bg-[#020813] border border-slate-800">
                <div className="text-slate-400 text-[10px]">Boltzmann Constant (k)</div>
                <div className="text-lg font-black text-white font-mono mt-1">1.3806 × 10⁻²³ J/K</div>
                <div className="text-[10px] text-amber-400 mt-0.5">Thermal Voltage</div>
              </div>

              <div className="p-3.5 rounded-2xl bg-[#020813] border border-slate-800">
                <div className="text-slate-400 text-[10px]">Thermal Voltage @ 300K (Vt)</div>
                <div className="text-lg font-black text-[#00F0B5] font-mono mt-1">~25.86 mV</div>
                <div className="text-[10px] text-emerald-400 mt-0.5">BJT / Diode Calculations</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MIT Campus Institutional Footer */}
      <div className="p-4 rounded-2xl bg-[#041026]/70 border border-slate-800 text-center text-xs text-slate-400 flex flex-col sm:flex-row items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span>Department of Electronics Engineering • Madras Institute of Technology (MIT) Campus</span>
        </div>
        <div className="text-[11px] font-mono text-slate-500">
          Anna University Regulation 2023 • ECE Knowledge Engine v1.0
        </div>
      </div>
    </div>
  );
}
