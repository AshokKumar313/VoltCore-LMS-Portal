import React, { useState, useMemo } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Phase H: Practical Laboratory Learning Hub (Features 281–290)
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 *
 * Features:
 *   - Feature 281: Virtual Breadboard Learning Interface & Netlist Continuity Validator
 *   - Feature 282: Component Identification Trainer (BJT, Regulator, IC Notch, Diode/LED)
 *   - Feature 283: Resistor Colour Code Calculator (4-Band, 5-Band, 6-Band & PPM/K)
 *   - Feature 284: Electronic Component Selection Guide (Wattage, Voltage Derating, PIV)
 *   - Feature 285: Circuit Troubleshooting Decision Tree (Power, Ground, Open, Short)
 *   - Feature 286: Laboratory Safety Checklist & High-Voltage/ESD Protection Protocols
 *   - Feature 287: Practical Experiment Preparation Guide (Anna University Reg 2023 ECE Labs)
 *   - Feature 288: Experiment Observation Notebook (Tabular Input/Output, Error % Math)
 *   - Feature 289: Virtual Instrument Reading Practice (Oscilloscope V/div, Time/div, DMM)
 *   - Feature 290: Laboratory Report Generator (Standard IEEE/Anna University Lab Record)
 * Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
 * ========================================================================================
 */

// Resistor Colors & Multipliers (Feature 283)
const COLOR_MAP = {
  BLACK:  { hex: "#0f172a", text: "#f8fafc", d: 0, mult: 1, tol: null, ppm: null },
  BROWN:  { hex: "#78350f", text: "#fde68a", d: 1, mult: 10, tol: 1.0, ppm: 100 },
  RED:    { hex: "#dc2626", text: "#fecaca", d: 2, mult: 100, tol: 2.0, ppm: 50 },
  ORANGE: { hex: "#ea580c", text: "#ffedd5", d: 3, mult: 1000, tol: 0.05, ppm: 15 },
  YELLOW: { hex: "#ca8a04", text: "#fef9c3", d: 4, mult: 10000, tol: 0.02, ppm: 25 },
  GREEN:  { hex: "#16a34a", text: "#dcfce7", d: 5, mult: 100000, tol: 0.5, ppm: 20 },
  BLUE:   { hex: "#2563eb", text: "#dbeafe", d: 6, mult: 1000000, tol: 0.25, ppm: 10 },
  VIOLET: { hex: "#7c3aed", text: "#ede9fe", d: 7, mult: 10000000, tol: 0.1, ppm: 5 },
  GREY:   { hex: "#4b5563", text: "#f3f4f6", d: 8, mult: 100000000, tol: 0.01, ppm: 1 },
  WHITE:  { hex: "#e2e8f0", text: "#0f172a", d: 9, mult: 1000000000, tol: null, ppm: null },
  GOLD:   { hex: "#d97706", text: "#fffbeb", d: null, mult: 0.1, tol: 5.0, ppm: null },
  SILVER: { hex: "#94a3b8", text: "#0f172a", d: null, mult: 0.01, tol: 10.0, ppm: null }
};

// Component Database (Feature 282)
const COMPONENTS = {
  BC547: {
    name: "BC547 NPN BJT",
    pkg: "TO-92 Plastic",
    pins: ["1: Collector (C)", "2: Base (B)", "3: Emitter (E)"],
    ratings: "Vceo=45V, Ic=100mA, hfe=110–800",
    taDesc: "சமதளப் பகுதி முன்பக்கம் இருக்கும்போது இடமிருந்து வலம்: 1-C, 2-B, 3-E."
  },
  "2N3904": {
    name: "2N3904 NPN BJT",
    pkg: "TO-92 Plastic",
    pins: ["1: Emitter (E)", "2: Base (B)", "3: Collector (C)"],
    ratings: "Vceo=40V, Ic=200mA, hfe=100–300",
    taDesc: "சமதளப் பகுதி முன்பக்கம் இருக்கும்போது: 1-E, 2-B, 3-C."
  },
  LM7805: {
    name: "LM7805 +5V Regulator",
    pkg: "TO-220 Heatsink Tab",
    pins: ["1: Input (Vin)", "2: Ground (GND)", "3: Output (+5V)"],
    ratings: "Vin=7–25V, Iout=1.5A Max, Dropout=2.0V",
    taDesc: "முன்பக்கம் பார்க்கும்போது: 1-Vin, 2-GND, 3-Vout (+5V)."
  },
  LM741: {
    name: "LM741 Operational Amplifier",
    pkg: "DIP-8 Dual In-Line",
    pins: [
      "1: Offset Null", "2: Inverting (-)", "3: Non-Inverting (+)", "4: -Vcc",
      "5: Offset Null", "6: Output", "7: +Vcc", "8: NC"
    ],
    ratings: "Supply=±18V, Gain=200k, Slew=0.5V/µs",
    taDesc: "நாட்ச் மேல்பக்கம் இருக்கும்போது இடமிருந்து எதிர்-கடிகாரச்சுற்று: பின் 2/3 இன்புட், பின் 6 அவுட்புட்."
  },
  NE555: {
    name: "NE555 Precision Timer",
    pkg: "DIP-8 Dual In-Line",
    pins: [
      "1: GND", "2: Trigger", "3: Output", "4: Reset",
      "5: Control", "6: Threshold", "7: Discharge", "8: Vcc"
    ],
    ratings: "Vcc=4.5–16V, Sink/Source=200mA",
    taDesc: "பின் 1 கிரவுண்ட், பின் 2 ட்ரிகர், பின் 3 அவுட்புட், பின் 8 சப்ளை Vcc."
  }
};

// Anna University ECE Labs (Feature 287)
const LAB_COURSES = {
  EC3361: {
    title: "Electronic Devices & Circuits Laboratory (Sem 3)",
    exps: [
      { id: "EXP01", name: "Diode & Zener Forward/Reverse Characteristics", appr: "Diode 1N4007, Zener 5.1V, RPS, DMM" },
      { id: "EXP02", name: "BJT Common Emitter (CE) Input/Output Characteristics", appr: "BC547, Dual RPS, Breadboard, Resistors" },
      { id: "EXP03", name: "JFET Drain and Transfer Characteristics", appr: "BFW10/11 JFET, RPS, Multimeter" },
      { id: "EXP04", name: "RC Phase Shift Oscillator & Hartley Oscillator", appr: "Op-Amp/BJT, Decade Box, Oscilloscope" }
    ]
  },
  EC3461: {
    title: "Digital Electronics & System Design Lab (Sem 4)",
    exps: [
      { id: "EXP05", name: "Design of Adders, Subtractors & Code Converters", appr: "7408, 7432, 7486, 7404 ICs, Trainer Kit" },
      { id: "EXP06", name: "Multiplexers, De-multiplexers & Decoders", appr: "74151 MUX, 74138 Decoder" },
      { id: "EXP07", name: "Synchronous & Asynchronous Up/Down Counters", appr: "7476 JK Flip-Flop, Logic Probe" }
    ]
  },
  EC3561: {
    title: "Communication Systems Laboratory (Sem 5)",
    exps: [
      { id: "EXP08", name: "Amplitude Modulation (AM) & Demodulation", appr: "Carrier Gen, Audio Gen, AM Kit, DSO" },
      { id: "EXP09", name: "Frequency Modulation (FM) & Demodulation", appr: "FM Modulator/Demodulator, Spectrum DSO" }
    ]
  }
};

export default function PracticalLaboratoryHub() {
  const [activeTab, setActiveTab] = useState("breadboard"); // breadboard, resistor_calc, troubleshooting, observations, virtual_scope
  const [bilingual, setBilingual] = useState(false);
  const [copiedKey, setCopiedKey] = useState(null);

  // Tab 1: Breadboard & Components
  const [bbPin1, setBbPin1] = useState("A12");
  const [bbPin2, setBbPin2] = useState("C12");
  const [selectedCompKey, setSelectedCompKey] = useState("BC547");

  // Tab 2: Resistor Codes & Selection
  const [numBands, setNumBands] = useState(4);
  const [band1, setBand1] = useState("BROWN");
  const [band2, setBand2] = useState("BLACK");
  const [band3, setBand3] = useState("RED");
  const [band4, setBand4] = useState("GOLD");
  const [band5, setBand5] = useState("BROWN");
  const [band6, setBand6] = useState("RED");
  // Component rating selector
  const [opVolt, setOpVolt] = useState(12.0);
  const [opCurrent, setOpCurrent] = useState(0.05);

  // Tab 3: Troubleshooting & Safety
  const [selectedSymptom, setSelectedSymptom] = useState("IC burning hot");
  const [safetyChecks, setSafetyChecks] = useState({
    power_off: true,
    polarity: true,
    esd_strap: true,
    current_limit: true,
    eyewear: true
  });

  // Tab 4: Experiment Guides & Observations
  const [selectedLabCode, setSelectedLabCode] = useState("EC3361");
  const [selectedExp, setSelectedExp] = useState(LAB_COURSES["EC3361"].exps[0]);
  const [measVal, setMeasVal] = useState(4.8);
  const [theoryVal, setTheoryVal] = useState(5.0);

  // Tab 5: Virtual Scope & Lab Report
  const [scopeDivY, setScopeDivY] = useState(4.0);
  const [scopeVPerDiv, setScopeVPerDiv] = useState(0.5);
  const [scopeDivX, setScopeDivX] = useState(5.0);
  const [scopeTimePerDiv, setScopeTimePerDiv] = useState(0.2); // ms
  const [probeAtten, setProbeAtten] = useState(1);

  const handleCopy = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  // Calculations: Breadboard Continuity
  const bbContinuity = useMemo(() => {
    const p1 = bbPin1.toUpperCase().trim();
    const p2 = bbPin2.toUpperCase().trim();
    if (!p1 || !p2) return null;

    const rails = ["TOP_RED", "TOP_BLUE", "BOT_RED", "BOT_BLUE"];
    if (rails.includes(p1) || rails.includes(p2)) {
      const isConn = (p1 === p2);
      return {
        isConnected: isConn,
        desc: isConn ? "Same continuous power bus rail." : "Different power rails (isolated)."
      };
    }

    const r1 = p1[0], c1 = parseInt(p1.slice(1));
    const r2 = p2[0], c2 = parseInt(p2.slice(1));
    if (isNaN(c1) || isNaN(c2)) return { isConnected: false, desc: "Invalid coordinate." };

    const bank1 = "ABCDE".includes(r1) ? "TOP" : "BOTTOM";
    const bank2 = "ABCDE".includes(r2) ? "TOP" : "BOTTOM";

    if (c1 === c2 && bank1 === bank2) {
      return { isConnected: true, desc: `Connected in Column ${c1} 5-hole tie strip.` };
    } else if (c1 === c2 && bank1 !== bank2) {
      return { isConnected: false, desc: `Separated across central trough (DIP chip trench).` };
    } else {
      return { isConnected: false, desc: `Different columns (${c1} vs ${c2}) without jumper wire.` };
    }
  }, [bbPin1, bbPin2]);

  // Calculations: Resistor Value
  const resistorResult = useMemo(() => {
    try {
      const b1 = COLOR_MAP[band1].d;
      const b2 = COLOR_MAP[band2].d;
      let nominal = 0;
      let tol = 5.0;
      let ppm = null;

      if (numBands === 4) {
        nominal = (b1 * 10 + b2) * COLOR_MAP[band3].mult;
        tol = COLOR_MAP[band4].tol || 5.0;
      } else if (numBands === 5) {
        const b3 = COLOR_MAP[band3].d;
        nominal = (b1 * 100 + b2 * 10 + b3) * COLOR_MAP[band4].mult;
        tol = COLOR_MAP[band5].tol || 1.0;
      } else {
        const b3 = COLOR_MAP[band3].d;
        nominal = (b1 * 100 + b2 * 10 + b3) * COLOR_MAP[band4].mult;
        tol = COLOR_MAP[band5].tol || 1.0;
        ppm = COLOR_MAP[band6].ppm || 50;
      }

      let formatted = "";
      if (nominal >= 1e6) formatted = `${(nominal / 1e6).toFixed(2)} MΩ`;
      else if (nominal >= 1e3) formatted = `${(nominal / 1e3).toFixed(2)} kΩ`;
      else formatted = `${nominal.toFixed(1)} Ω`;

      const minR = nominal * (1.0 - tol / 100);
      const maxR = nominal * (1.0 + tol / 100);

      return { nominal, formatted, tol, ppm, minR: minR.toFixed(1), maxR: maxR.toFixed(1) };
    } catch {
      return null;
    }
  }, [numBands, band1, band2, band3, band4, band5, band6]);

  // Calculations: Component Rating & Derating
  const ratingResult = useMemo(() => {
    const p = opVolt * opCurrent;
    const deratedP = p * 2.0;
    const stdWatts = [0.125, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0];
    const recW = stdWatts.find(w => w >= deratedP) || 10.0;
    const recV = Math.ceil(opVolt * 1.5);
    const recPiv = Math.ceil(opVolt * 2.0);
    return { p: p.toFixed(3), recW, recV, recPiv };
  }, [opVolt, opCurrent]);

  // Calculations: Troubleshooting Diagnostic
  const troubleshootingResult = useMemo(() => {
    const s = selectedSymptom.toLowerCase();
    if (s.includes("burning") || s.includes("hot")) {
      return {
        cause: "IC inverted or Reverse Polarity on Vcc/GND pins.",
        action: "Power off immediately! Check Pin 1 notch and ground connections.",
        priority: "CRITICAL"
      };
    } else if (s.includes("0v") || s.includes("no power")) {
      return {
        cause: "Power supply current limit tripped or short circuit to ground.",
        action: "Disconnect load, check power rail continuity with DMM beeper.",
        priority: "HIGH"
      };
    } else if (s.includes("clipped") || s.includes("distorted")) {
      return {
        cause: "Incorrect Q-point bias in amplifier; transistor driven into saturation/cutoff.",
        action: "Measure DC quiescent voltage Vc ~ Vcc / 2; decrease input generator amplitude.",
        priority: "NORMAL"
      };
    } else {
      return {
        cause: "Missing decoupling capacitor or high breadboard contact resistance.",
        action: "Add 100nF ceramic cap across power rails close to IC leads.",
        priority: "NORMAL"
      };
    }
  }, [selectedSymptom]);

  // Calculations: Safety Status
  const safetyStatus = useMemo(() => {
    const vals = Object.values(safetyChecks);
    const passed = vals.filter(Boolean).length;
    const total = vals.length;
    return {
      isSafe: passed === total,
      pct: Math.round((passed / total) * 100),
      passed,
      total
    };
  }, [safetyChecks]);

  // Calculations: Observation Error
  const errorResult = useMemo(() => {
    if (theoryVal === 0) return { errPct: "0.0", isOk: true };
    const err = (Math.abs(measVal - theoryVal) / Math.abs(theoryVal)) * 100;
    return {
      errPct: err.toFixed(2),
      isOk: err <= 10.0
    };
  }, [measVal, theoryVal]);

  // Calculations: Virtual Scope
  const scopeResult = useMemo(() => {
    const vpp = scopeDivY * scopeVPerDiv * probeAtten;
    const vamp = vpp / 2.0;
    const vrms = vamp / Math.sqrt(2.0);
    const periodSec = (scopeDivX * scopeTimePerDiv) / 1000.0;
    const freq = periodSec > 0 ? 1.0 / periodSec : 0;
    return {
      vpp: vpp.toFixed(2),
      vamp: vamp.toFixed(2),
      vrms: vrms.toFixed(2),
      periodMs: (periodSec * 1000.0).toFixed(2),
      freqHz: Math.round(freq)
    };
  }, [scopeDivY, scopeVPerDiv, scopeDivX, scopeTimePerDiv, probeAtten]);

  // Generated Lab Report Markdown (Feature 290)
  const reportMarkdown = useMemo(() => {
    return `# ANNA UNIVERSITY / MIT CAMPUS — LABORATORY RECORD
**Department of Electronics Engineering** | Regulation 2023
**Course Code:** ${selectedLabCode} | **Date:** 06-11-2026
**Student Name:** Ashok Kumar A | **Roll No:** 2023MITEC042

---

## EXPERIMENT: ${selectedExp.name} (${selectedExp.id})

### 1. AIM
To experimentally construct, verify, and document the circuit parameters of ${selectedExp.name} using standard test bench apparatus.

### 2. APPARATUS REQUIRED
- ${selectedExp.appr}
- Regulated Dual DC Power Supply (0–30V, 2A)
- Digital Storage Oscilloscope (DSO 100MHz)
- Solderless Breadboard & Connecting Wires

### 3. FORMULAE & EQUATIONS
1. Percentage Error: % Error = |(Measured - Theoretical) / Theoretical| × 100%
2. Resistor Wattage Rating: P = V × I (with 2.0× safety margin)
3. Oscilloscope Amplitude: V_pp = Div_Y × (Volts/Div) × Probe_Atten

### 4. OBSERVATIONS
- Measured Parameter: ${measVal}
- Theoretical Target: ${theoryVal}
- Error Percentage: ${errorResult.errPct}% (${errorResult.isOk ? 'Within 10% standard margin' : 'Exceeds margin'})

### 5. RESULT & INFERENCE
The circuit was successfully assembled on the breadboard. Output waveforms and DC parameters were verified on the digital storage oscilloscope with ${errorResult.errPct}% measurement variance.

---
*Verified by Laboratory In-Charge — MIT Campus, Anna University*`;
  }, [selectedLabCode, selectedExp, measVal, theoryVal, errorResult]);

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6 text-slate-100">
      {/* Hero Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-amber-950/70 to-slate-900 border border-amber-500/30 p-6 shadow-2xl backdrop-blur-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <span className="px-2.5 py-1 text-xs font-mono font-semibold tracking-wider uppercase rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40">
                Phase H • Features 281–290
              </span>
              <span className="text-xs text-slate-400 font-mono">
                Regulation 2023 | MIT Campus, Anna University
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white mt-2 tracking-tight">
              Practical Laboratory Learning & Test Bench Hub
            </h1>
            <p className="text-sm text-slate-300 max-w-2xl mt-1">
              Virtual breadboard wiring, component pinout training, resistor colour code solvers, circuit troubleshooting trees, oscilloscope practice, and automated lab record generators.
            </p>
          </div>

          <div className="flex items-center gap-3 self-start md:self-auto">
            <button
              onClick={() => setBilingual(!bilingual)}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-all ${
                bilingual
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                  : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'
              }`}
            >
              {bilingual ? 'Tamil Notes: ON (தமிழ்)' : 'Tamil Notes: OFF'}
            </button>
            <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-mono flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              SQLite WAL Active
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 mt-6 pt-4 border-t border-slate-800">
          {[
            { id: "breadboard", label: "1. Breadboard & Components", icon: "🔌" },
            { id: "resistor_calc", label: "2. Resistor Codes & Rating", icon: "🎨" },
            { id: "troubleshooting", label: "3. Troubleshooting & Safety", icon: "🛠️" },
            { id: "observations", label: "4. Experiments & Notebook", icon: "📝" },
            { id: "virtual_scope", label: "5. Virtual Scope & Report", icon: "📈" }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold tracking-wide transition-all ${
                activeTab === tab.id
                  ? 'bg-amber-600 text-white shadow-lg shadow-amber-600/30 border border-amber-400/40'
                  : 'bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-700/60 border border-slate-700/60'
              }`}
            >
              <span className="mr-1.5">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: Breadboard & Components (Features 281 & 282)                       */}
      {/* ========================================================================= */}
      {activeTab === "breadboard" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Feature 281: Breadboard Continuity Validator */}
            <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  Feature 281: Virtual Breadboard Tie-Strip Continuity Validator
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  5-hole tie strips connect vertically. The central trough isolates DIP IC opposite pin banks.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-xs font-mono text-slate-300">Point 1 Coordinate:</label>
                  <input
                    type="text"
                    value={bbPin1}
                    onChange={e => setBbPin1(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded p-2 text-xs font-mono uppercase"
                    placeholder="e.g. A12, C12, TOP_RED"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-mono text-slate-300">Point 2 Coordinate:</label>
                  <input
                    type="text"
                    value={bbPin2}
                    onChange={e => setBbPin2(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded p-2 text-xs font-mono uppercase"
                    placeholder="e.g. C12, G12, BOT_BLUE"
                  />
                </div>
              </div>

              {/* Quick Presets */}
              <div className="space-y-1">
                <span className="text-[10px] font-mono text-slate-400">Sample Test Configurations:</span>
                <div className="flex flex-wrap gap-1.5">
                  {[
                    { label: "Same Col (A12 to C12)", p1: "A12", p2: "C12" },
                    { label: "Across Trough (C12 to G12)", p1: "C12", p2: "G12" },
                    { label: "Different Col (A12 to A13)", p1: "A12", p2: "A13" },
                    { label: "Top Power Rail", p1: "TOP_RED", p2: "TOP_RED" }
                  ].map(pr => (
                    <button
                      key={pr.label}
                      onClick={() => { setBbPin1(pr.p1); setBbPin2(pr.p2); }}
                      className="px-2.5 py-1 text-[10px] font-mono rounded bg-slate-800 hover:bg-slate-700 text-amber-300 border border-slate-700"
                    >
                      {pr.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Continuity Verdict */}
              {bbContinuity && (
                <div className={`p-4 rounded-xl border flex items-center justify-between ${
                  bbContinuity.isConnected
                    ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-200'
                    : 'bg-rose-950/40 border-rose-500/40 text-rose-200'
                }`}>
                  <div>
                    <div className="text-xs font-bold font-mono">
                      {bbContinuity.isConnected ? 'CONTINUITY VERIFIED (SHORTED / CONNECTED)' : 'ELECTRICALLY ISOLATED (NO CONNECTION)'}
                    </div>
                    <div className="text-[11px] font-mono mt-0.5">{bbContinuity.desc}</div>
                  </div>
                  <span className={`px-2.5 py-1 rounded text-xs font-bold font-mono border ${
                    bbContinuity.isConnected ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' : 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                  }`}>
                    {bbContinuity.isConnected ? '0 Ω' : '∞ Ω'}
                  </span>
                </div>
              )}

              {/* Breadboard Architecture Diagram */}
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <svg viewBox="0 0 450 110" className="w-full h-24 bg-slate-900 rounded-lg">
                  {/* Top Power Rails */}
                  <line x1="20" y1="15" x2="430" y2="15" stroke="#ef4444" strokeWidth="2" strokeDasharray="4,4" />
                  <line x1="20" y1="25" x2="430" y2="25" stroke="#3b82f6" strokeWidth="2" strokeDasharray="4,4" />
                  <text x="5" y="18" fill="#ef4444" fontSize="8" fontFamily="monospace">+</text>
                  <text x="5" y="28" fill="#3b82f6" fontSize="8" fontFamily="monospace">-</text>

                  {/* Top Bank Tie Strips A-E */}
                  {[...Array(12)].map((_, i) => (
                    <rect key={i} x={35 + i * 32} y="35" width="8" height="25" fill="#334155" rx="2" />
                  ))}
                  <text x="420" y="50" fill="#94a3b8" fontSize="8" fontFamily="monospace">A-E</text>

                  {/* Central Trough / Trench */}
                  <rect x="20" y="64" width="410" height="6" fill="#0f172a" stroke="#475569" strokeWidth="1" />
                  <text x="210" y="69" fill="#64748b" fontSize="6" fontFamily="monospace" textAnchor="middle">CENTRAL TROUGH (DIP IC TRENCH)</text>

                  {/* Bottom Bank Tie Strips F-J */}
                  {[...Array(12)].map((_, i) => (
                    <rect key={i} x={35 + i * 32} y="74" width="8" height="25" fill="#334155" rx="2" />
                  ))}
                  <text x="420" y="88" fill="#94a3b8" fontSize="8" fontFamily="monospace">F-J</text>

                  {/* Bottom Power Rails */}
                  <line x1="20" y1="104" x2="430" y2="104" stroke="#3b82f6" strokeWidth="2" strokeDasharray="4,4" />
                </svg>
              </div>
            </div>

            {/* Feature 282: Component Identification Trainer */}
            <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  Feature 282: Electronic Component Pinout Identification
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Pin mapping, notch orientation, and electrical limits for active silicon devices.
                </p>
              </div>

              <div className="flex flex-wrap gap-2">
                {Object.keys(COMPONENTS).map(k => (
                  <button
                    key={k}
                    onClick={() => setSelectedCompKey(k)}
                    className={`px-3 py-1.5 text-xs font-mono font-bold rounded-lg border transition-all ${
                      selectedCompKey === k
                        ? 'bg-amber-600 text-white border-amber-400'
                        : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'
                    }`}
                  >
                    {k}
                  </button>
                ))}
              </div>

              {/* Component Info Card */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <span className="text-sm font-bold text-amber-300">{COMPONENTS[selectedCompKey].name}</span>
                  <span className="text-xs font-mono text-slate-400">{COMPONENTS[selectedCompKey].pkg}</span>
                </div>
                <div className="text-xs text-slate-300 leading-relaxed">
                  {bilingual ? COMPONENTS[selectedCompKey].taDesc : COMPONENTS[selectedCompKey].ratings}
                </div>

                <div className="space-y-1.5 pt-1">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Pin Assignment:</div>
                  <div className="grid grid-cols-2 gap-2">
                    {COMPONENTS[selectedCompKey].pins.map((p, idx) => (
                      <div key={idx} className="p-2 rounded bg-slate-900 border border-slate-800 font-mono text-xs text-emerald-300">
                        {p}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: Resistor Codes & Rating Selection (Features 283 & 284)             */}
      {/* ========================================================================= */}
      {activeTab === "resistor_calc" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Feature 283: Resistor Color Code Calculator */}
            <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white">
                  Feature 283: Resistor Colour Code Calculator
                </h3>
                <div className="flex gap-1">
                  {[4, 5, 6].map(b => (
                    <button
                      key={b}
                      onClick={() => setNumBands(b)}
                      className={`px-2.5 py-1 text-xs font-mono rounded ${
                        numBands === b ? 'bg-amber-600 text-white font-bold' : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {b}-Band
                    </button>
                  ))}
                </div>
              </div>

              {/* Band Selectors */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                <div>
                  <label className="text-[10px] font-mono text-slate-400">Band 1 (Digit):</label>
                  <select
                    value={band1}
                    onChange={e => setBand1(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded p-1.5 text-xs font-mono mt-1"
                  >
                    {["BROWN", "RED", "ORANGE", "YELLOW", "GREEN", "BLUE", "VIOLET", "GREY", "WHITE"].map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-[10px] font-mono text-slate-400">Band 2 (Digit):</label>
                  <select
                    value={band2}
                    onChange={e => setBand2(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded p-1.5 text-xs font-mono mt-1"
                  >
                    {Object.keys(COLOR_MAP).filter(k => COLOR_MAP[k].d !== null).map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
                {numBands >= 5 && (
                  <div>
                    <label className="text-[10px] font-mono text-slate-400">Band 3 (Digit):</label>
                    <select
                      value={band3}
                      onChange={e => setBand3(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 text-white rounded p-1.5 text-xs font-mono mt-1"
                    >
                      {Object.keys(COLOR_MAP).filter(k => COLOR_MAP[k].d !== null).map(c => (
                        <option key={c} value={c}>{c}</option>
                      ))}
                    </select>
                  </div>
                )}
                <div>
                  <label className="text-[10px] font-mono text-slate-400">Multiplier:</label>
                  <select
                    value={numBands === 4 ? band3 : band4}
                    onChange={e => numBands === 4 ? setBand3(e.target.value) : setBand4(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded p-1.5 text-xs font-mono mt-1"
                  >
                    {Object.keys(COLOR_MAP).map(c => (
                      <option key={c} value={c}>{c} (×{COLOR_MAP[c].mult})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-[10px] font-mono text-slate-400">Tolerance:</label>
                  <select
                    value={numBands === 4 ? band4 : band5}
                    onChange={e => numBands === 4 ? setBand4(e.target.value) : setBand5(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded p-1.5 text-xs font-mono mt-1"
                  >
                    {Object.keys(COLOR_MAP).filter(k => COLOR_MAP[k].tol !== null).map(c => (
                      <option key={c} value={c}>{c} (±{COLOR_MAP[c].tol}%)</option>
                    ))}
                  </select>
                </div>
                {numBands === 6 && (
                  <div>
                    <label className="text-[10px] font-mono text-slate-400">Temp Coeff:</label>
                    <select
                      value={band6}
                      onChange={e => setBand6(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 text-white rounded p-1.5 text-xs font-mono mt-1"
                    >
                      {Object.keys(COLOR_MAP).filter(k => COLOR_MAP[k].ppm !== null).map(c => (
                        <option key={c} value={c}>{c} ({COLOR_MAP[c].ppm} ppm/K)</option>
                      ))}
                    </select>
                  </div>
                )}
              </div>

              {/* Graphical Resistor SVG with Exact Bands */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex justify-center">
                <svg viewBox="0 0 320 80" className="w-full max-w-xs h-20">
                  {/* Lead wires */}
                  <line x1="10" y1="40" x2="50" y2="40" stroke="#cbd5e1" strokeWidth="4" />
                  <line x1="270" y1="40" x2="310" y2="40" stroke="#cbd5e1" strokeWidth="4" />
                  {/* Resistor Body */}
                  <rect x="50" y="20" width="220" height="40" rx="12" fill="#d97706" stroke="#92400e" strokeWidth="2" />
                  {/* Color Bands */}
                  <rect x="80" y="20" width="12" height="40" fill={COLOR_MAP[band1].hex} />
                  <rect x="110" y="20" width="12" height="40" fill={COLOR_MAP[band2].hex} />
                  <rect x="140" y="20" width="12" height="40" fill={COLOR_MAP[band3].hex} />
                  <rect x="170" y="20" width="12" height="40" fill={COLOR_MAP[band4].hex} />
                  {numBands >= 5 && <rect x="200" y="20" width="12" height="40" fill={COLOR_MAP[band5].hex} />}
                  {numBands === 6 && <rect x="230" y="20" width="12" height="40" fill={COLOR_MAP[band6].hex} />}
                </svg>
              </div>

              {/* Calculated Readout */}
              {resistorResult && (
                <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Nominal Resistance:</div>
                  <div className="text-xl font-extrabold text-amber-300 font-mono">
                    {resistorResult.formatted} ±{resistorResult.tol}%
                  </div>
                  <div className="text-xs text-slate-400 font-mono">
                    Tolerance Window: {resistorResult.minR} Ω to {resistorResult.maxR} Ω
                    {resistorResult.ppm && ` | ${resistorResult.ppm} ppm/K`}
                  </div>
                </div>
              )}
            </div>

            {/* Feature 284: Component Selection & Derating Guide */}
            <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white">
                  Feature 284: Component Electrical Derating Guide
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Applies 2.0× industrial power margin and 1.5× voltage breakdown safety factor.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-xs font-mono text-slate-300">Operating Voltage (V):</label>
                  <input
                    type="number"
                    step="0.5"
                    value={opVolt}
                    onChange={e => setOpVolt(parseFloat(e.target.value) || 0)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded p-2 text-xs font-mono"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-mono text-slate-300">Operating Current (A):</label>
                  <input
                    type="number"
                    step="0.01"
                    value={opCurrent}
                    onChange={e => setOpCurrent(parseFloat(e.target.value) || 0)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded p-2 text-xs font-mono"
                  />
                </div>
              </div>

              {/* Derating Results */}
              <div className="grid grid-cols-2 gap-3 pt-2">
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Power Dissipated</div>
                  <div className="text-base font-extrabold text-cyan-300 mt-1">{ratingResult.p} W</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">P = V × I</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Recommended Wattage</div>
                  <div className="text-base font-extrabold text-amber-300 mt-1">{ratingResult.recW} W</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">2.0× safety margin</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Capacitor Rating</div>
                  <div className="text-base font-extrabold text-purple-300 mt-1">≥ {ratingResult.recV} V</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">1.5× voltage derating</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Diode Min PIV</div>
                  <div className="text-base font-extrabold text-emerald-400 mt-1">≥ {ratingResult.recPiv} V</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">2.0× peak inverse</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: Troubleshooting & Laboratory Safety (Features 285 & 286)           */}
      {/* ========================================================================= */}
      {activeTab === "troubleshooting" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Feature 285: Circuit Troubleshooting Decision Tree */}
            <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white">
                  Feature 285: Circuit Troubleshooting Diagnostic Tree
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Automated diagnosis of common undergraduate lab wiring errors and component failures.
                </p>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">Observed Circuit Symptom:</label>
                <select
                  value={selectedSymptom}
                  onChange={e => setSelectedSymptom(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded p-2 text-xs font-mono"
                >
                  <option value="IC burning hot">IC is burning hot to touch / smoke smell</option>
                  <option value="0V on power rail">Power supply tripped / 0V on breadboard rail</option>
                  <option value="Output clipped">Output waveform severely clipped / distorted</option>
                  <option value="Oscillations/Hum">Unwanted 50Hz hum / high-frequency oscillation</option>
                </select>
              </div>

              {/* Diagnostic Card */}
              <div className={`p-4 rounded-xl border space-y-2 ${
                troubleshootingResult.priority === "CRITICAL"
                  ? 'bg-rose-950/40 border-rose-500/40'
                  : 'bg-slate-950 border-slate-800'
              }`}>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold font-mono text-white">Diagnosed Root Cause:</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                    troubleshootingResult.priority === "CRITICAL"
                      ? 'bg-rose-500/20 text-rose-300'
                      : 'bg-amber-500/20 text-amber-300'
                  }`}>
                    {troubleshootingResult.priority} PRIORITY
                  </span>
                </div>
                <div className="text-sm font-semibold text-amber-300 font-mono">
                  {troubleshootingResult.cause}
                </div>
                <div className="text-xs text-slate-300 pt-2 border-t border-slate-800 font-mono">
                  <strong className="text-cyan-400">Action Step: </strong>
                  {troubleshootingResult.action}
                </div>
              </div>
            </div>

            {/* Feature 286: Laboratory Safety Protocols */}
            <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white">
                  Feature 286: Laboratory Safety Pre-Energization Checklist
                </h3>
                <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded border ${
                  safetyStatus.isSafe
                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                    : 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                }`}>
                  {safetyStatus.isSafe ? 'POWER-UP APPROVED' : 'HOLD POWER'}
                </span>
              </div>

              <div className="space-y-2.5">
                {[
                  { id: "power_off", label: "DC power supply kept OFF during breadboard circuit wiring." },
                  { id: "polarity", label: "Polarity verified for electrolytic caps (minus stripe) & diodes." },
                  { id: "esd_strap", label: "ESD grounding wrist strap worn when handling sensitive CMOS ICs." },
                  { id: "current_limit", label: "DC power supply current limit knob set to safe lab value (≤250mA)." },
                  { id: "eyewear", label: "Protective safety glasses worn during soldering or capacitor tests." }
                ].map(item => (
                  <label key={item.id} className="flex items-start gap-2.5 p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono cursor-pointer hover:bg-slate-900">
                    <input
                      type="checkbox"
                      checked={safetyChecks[item.id]}
                      onChange={e => setSafetyChecks({ ...safetyChecks, [item.id]: e.target.checked })}
                      className="mt-0.5 accent-amber-500 rounded"
                    />
                    <span className={safetyChecks[item.id] ? "text-slate-200" : "text-slate-500 line-through"}>
                      {item.label}
                    </span>
                  </label>
                ))}
              </div>

              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs font-mono">
                <span className="text-slate-400">Readiness Score: {safetyStatus.passed}/{safetyStatus.total} ({safetyStatus.pct}%)</span>
                <span className={safetyStatus.isSafe ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                  {safetyStatus.isSafe ? "Safe to Energize" : "Safety Items Incomplete"}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: Experiment Guides & Observations (Features 287 & 288)               */}
      {/* ========================================================================= */}
      {activeTab === "observations" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Feature 287: Lab Syllabus Selector */}
            <div className="lg:col-span-1 p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-amber-400">
                Anna University ECE Labs (Reg 2023)
              </h3>

              <div className="space-y-2">
                {Object.keys(LAB_COURSES).map(code => (
                  <button
                    key={code}
                    onClick={() => {
                      setSelectedLabCode(code);
                      setSelectedExp(LAB_COURSES[code].exps[0]);
                    }}
                    className={`w-full text-left p-3 rounded-xl text-xs font-medium transition-all ${
                      selectedLabCode === code
                        ? 'bg-amber-600/30 text-amber-200 border border-amber-500/50'
                        : 'bg-slate-800/40 text-slate-400 hover:bg-slate-800 border border-slate-700/40'
                    }`}
                  >
                    <div className="font-bold text-white">{code}</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">{LAB_COURSES[code].title}</div>
                  </button>
                ))}
              </div>

              <div className="space-y-1.5 pt-2 border-t border-slate-800">
                <span className="text-xs font-mono text-slate-400">Select Experiment:</span>
                <div className="space-y-1">
                  {LAB_COURSES[selectedLabCode].exps.map(exp => (
                    <button
                      key={exp.id}
                      onClick={() => setSelectedExp(exp)}
                      className={`w-full text-left p-2 rounded text-xs font-mono transition-all ${
                        selectedExp.id === exp.id
                          ? 'bg-amber-500 text-white font-bold'
                          : 'bg-slate-900 text-slate-300 hover:bg-slate-800'
                      }`}
                    >
                      {exp.id}: {exp.name}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Feature 288: Experiment Observation Notebook */}
            <div className="lg:col-span-2 p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white">
                  Feature 288: Tabular Observation Entry & Error Calculation
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  {selectedExp.name} ({selectedExp.id}) — Apparatus: {selectedExp.appr}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-mono text-slate-300">Measured Value (Vout / Freq):</label>
                  <input
                    type="number"
                    step="0.05"
                    value={measVal}
                    onChange={e => setMeasVal(parseFloat(e.target.value) || 0)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded p-2 text-xs font-mono"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-mono text-slate-300">Theoretical Target (Vout / Freq):</label>
                  <input
                    type="number"
                    step="0.05"
                    value={theoryVal}
                    onChange={e => setTheoryVal(parseFloat(e.target.value) || 0)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded p-2 text-xs font-mono"
                  />
                </div>
              </div>

              {/* Error Output Card */}
              <div className={`p-4 rounded-xl border flex items-center justify-between ${
                errorResult.isOk
                  ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-200'
                  : 'bg-rose-950/40 border-rose-500/40 text-rose-200'
              }`}>
                <div>
                  <div className="text-xs font-bold font-mono">
                    {errorResult.isOk ? 'ACCEPTABLE LAB MARGIN (<= 10%)' : 'EXCEEDS MARGIN (> 10% ERROR)'}
                  </div>
                  <div className="text-sm font-mono font-bold mt-0.5">
                    Variance: {errorResult.errPct}% Error
                  </div>
                </div>
                <span className={`px-2.5 py-1 rounded text-xs font-mono font-bold border ${
                  errorResult.isOk ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' : 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                }`}>
                  {errorResult.isOk ? 'VERIFIED' : 'RE-CALCULATE'}
                </span>
              </div>

              {/* Tabular History */}
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <div className="text-xs font-mono text-slate-400 font-bold">Recent Observation Records:</div>
                <div className="space-y-1 font-mono text-xs">
                  <div className="flex justify-between p-2 rounded bg-slate-900 text-slate-300">
                    <span>Trial 1: Vin=2.0V, Vout_meas=4.80V, Vout_theo=5.00V</span>
                    <span className="text-emerald-400">4.0% Err</span>
                  </div>
                  <div className="flex justify-between p-2 rounded bg-slate-900 text-slate-300">
                    <span>Trial 2: Vin=4.0V, Vout_meas=9.65V, Vout_theo=10.00V</span>
                    <span className="text-emerald-400">3.5% Err</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 5: Virtual Scope & Lab Report (Features 289 & 290)                    */}
      {/* ========================================================================= */}
      {activeTab === "virtual_scope" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Feature 289: Virtual Instrument Practice */}
            <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white">
                  Feature 289: Dual-Trace Oscilloscope Reading Practice
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Calculate $V_{`pp`}$ from vertical divisions and frequency $f = 1/T$ from horizontal divisions.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-xs font-mono text-slate-300">Vertical Height: {scopeDivY} div</label>
                  <input
                    type="range"
                    min="1.0"
                    max="8.0"
                    step="0.2"
                    value={scopeDivY}
                    onChange={e => setScopeDivY(parseFloat(e.target.value))}
                    className="w-full accent-amber-500"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-mono text-slate-300">Volts / Div knob:</label>
                  <select
                    value={scopeVPerDiv}
                    onChange={e => setScopeVPerDiv(parseFloat(e.target.value))}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded p-1.5 text-xs font-mono"
                  >
                    <option value={0.1}>0.1 V/div</option>
                    <option value={0.2}>0.2 V/div</option>
                    <option value={0.5}>0.5 V/div</option>
                    <option value={1.0}>1.0 V/div</option>
                    <option value={2.0}>2.0 V/div</option>
                    <option value={5.0}>5.0 V/div</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-mono text-slate-300">Horizontal Width: {scopeDivX} div</label>
                  <input
                    type="range"
                    min="1.0"
                    max="10.0"
                    step="0.2"
                    value={scopeDivX}
                    onChange={e => setScopeDivX(parseFloat(e.target.value))}
                    className="w-full accent-amber-500"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-mono text-slate-300">Time / Div knob:</label>
                  <select
                    value={scopeTimePerDiv}
                    onChange={e => setScopeTimePerDiv(parseFloat(e.target.value))}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded p-1.5 text-xs font-mono"
                  >
                    <option value={0.05}>0.05 ms/div</option>
                    <option value={0.1}>0.1 ms/div</option>
                    <option value={0.2}>0.2 ms/div</option>
                    <option value={0.5}>0.5 ms/div</option>
                    <option value={1.0}>1.0 ms/div</option>
                  </select>
                </div>
              </div>

              {/* Scope Graticule SVG */}
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <svg viewBox="0 0 300 120" className="w-full h-28 bg-emerald-950/20 rounded-lg">
                  {/* 8x10 Graticule Grid */}
                  {[...Array(11)].map((_, i) => (
                    <line key={`v${i}`} x1={i * 30} y1="0" x2={i * 30} y2="120" stroke="#064e3b" strokeWidth="0.5" />
                  ))}
                  {[...Array(5)].map((_, i) => (
                    <line key={`h${i}`} x1="0" y1={i * 30} x2="300" y2={i * 30} stroke="#064e3b" strokeWidth="0.5" />
                  ))}
                  {/* Sine Wave */}
                  <path
                    d="M 0 60 Q 37.5 15, 75 60 T 150 60 T 225 60 T 300 60"
                    fill="none"
                    stroke="#10b981"
                    strokeWidth="2.5"
                  />
                </svg>
              </div>

              {/* Calculated Readouts */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center font-mono">
                <div className="p-2 rounded bg-slate-800 border border-slate-700">
                  <div className="text-[10px] text-slate-400">Peak-to-Peak</div>
                  <div className="text-sm font-bold text-cyan-300 mt-0.5">{scopeResult.vpp} V</div>
                </div>
                <div className="p-2 rounded bg-slate-800 border border-slate-700">
                  <div className="text-[10px] text-slate-400">RMS Voltage</div>
                  <div className="text-sm font-bold text-amber-300 mt-0.5">{scopeResult.vrms} V</div>
                </div>
                <div className="p-2 rounded bg-slate-800 border border-slate-700">
                  <div className="text-[10px] text-slate-400">Period</div>
                  <div className="text-sm font-bold text-purple-300 mt-0.5">{scopeResult.periodMs} ms</div>
                </div>
                <div className="p-2 rounded bg-slate-800 border border-slate-700">
                  <div className="text-[10px] text-slate-400">Frequency</div>
                  <div className="text-sm font-bold text-emerald-300 mt-0.5">{scopeResult.freqHz} Hz</div>
                </div>
              </div>
            </div>

            {/* Feature 290: Standard Laboratory Report Generator */}
            <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white">
                  Feature 290: Anna University / IEEE Lab Report Generator
                </h3>
                <button
                  onClick={() => handleCopy(reportMarkdown, 'lab_report')}
                  className="px-3 py-1.5 text-xs font-mono font-bold rounded bg-amber-600 hover:bg-amber-500 text-white transition-all shadow"
                >
                  {copiedKey === 'lab_report' ? 'Copied Report!' : 'Copy Markdown'}
                </button>
              </div>

              <pre className="p-4 rounded-xl bg-slate-950 font-mono text-xs text-emerald-400 overflow-x-auto border border-slate-800 max-h-96 leading-relaxed">
                {reportMarkdown}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
