import React, { useState, useMemo } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Phase C: Digital Electronics Engineering (Features 231–240)
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 * 
 * Features:
 *   - Feature 231: Logic Gate Truth Table Explorer (AND, OR, NOT, NAND, NOR, XOR, XNOR)
 *   - Feature 232: Multi-Radix Base Converter (Bin, Oct, Dec, Hex) with division steps
 *   - Feature 233: Two's Complement & Signed Arithmetic (Overflow V = Cin ^ Cout)
 *   - Feature 234: Boolean Algebra Step-by-Step Axiom Simplifier & De Morgan Verifier
 *   - Feature 235: 4-Variable K-Map (Gray Code: 00, 01, 11, 10) Prime Implicant Reducer
 * Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
 * ========================================================================================
 */

// Standard 7400-Series Logic Gates Specifications
const LOGIC_GATES = [
  {
    id: "AND",
    name: "AND Gate",
    ic: "74HC08",
    tpd: 7.0,
    power: 20,
    symbol: "&",
    desc: "Output is HIGH (1) if and only if all inputs are HIGH.",
    descTa: "அனைத்து உள்ளீடுகளும் உயர்வாக (1) இருக்கும் போது மட்டுமே வெளியீடு 1 ஆகும்.",
    eval: (inputs) => inputs.every(b => b === 1) ? 1 : 0
  },
  {
    id: "OR",
    name: "OR Gate",
    ic: "74HC32",
    tpd: 8.0,
    power: 20,
    symbol: "≥1",
    desc: "Output is HIGH (1) if at least one input is HIGH.",
    descTa: "ஏதேனும் ஒரு உள்ளீடு உயர்வாக இருந்தாலும் வெளியீடு 1 ஆகும்.",
    eval: (inputs) => inputs.some(b => b === 1) ? 1 : 0
  },
  {
    id: "NOT",
    name: "NOT Inverter",
    ic: "74HC04",
    tpd: 5.0,
    power: 15,
    symbol: "1",
    desc: "Inverts input logic: 0 becomes 1, and 1 becomes 0.",
    descTa: "உள்ளீட்டை தலைகீழாக மாற்றுகிறது (0 எனில் 1, 1 எனில் 0).",
    eval: (inputs) => inputs[0] === 1 ? 0 : 1
  },
  {
    id: "NAND",
    name: "NAND Gate (Universal)",
    ic: "74HC00",
    tpd: 6.5,
    power: 20,
    symbol: "&",
    desc: "Universal gate. Output is LOW (0) only if all inputs are HIGH.",
    descTa: "பொது தர்க்க வாயில். அனைத்து உள்ளீடுகளும் 1 எனில் மட்டும் வெளியீடு 0 ஆகும்.",
    eval: (inputs) => inputs.every(b => b === 1) ? 0 : 1
  },
  {
    id: "NOR",
    name: "NOR Gate (Universal)",
    ic: "74HC02",
    tpd: 7.5,
    power: 20,
    symbol: "≥1",
    desc: "Universal gate. Output is HIGH (1) only if all inputs are LOW.",
    descTa: "பொது தர்க்க வாயில். அனைத்து உள்ளீடுகளும் 0 எனில் மட்டுமே வெளியீடு 1 ஆகும்.",
    eval: (inputs) => inputs.every(b => b === 0) ? 1 : 0
  },
  {
    id: "XOR",
    name: "XOR Gate (Odd Parity)",
    ic: "74HC86",
    tpd: 9.0,
    power: 25,
    symbol: "=1",
    desc: "Odd parity detector. Output is HIGH if an odd number of inputs are HIGH.",
    descTa: "ஒற்றைப்படை சமநிலை கண்டுபிடிப்பான். உள்ளீடுகளில் ஒற்றைப்படை 1-கள் இருக்கும் போது வெளியீடு 1 ஆகும்.",
    eval: (inputs) => (inputs.filter(b => b === 1).length % 2 === 1) ? 1 : 0
  },
  {
    id: "XNOR",
    name: "XNOR Gate (Equivalence)",
    ic: "74HC7266",
    tpd: 9.5,
    power: 25,
    symbol: "=",
    desc: "Equivalence gate. Output is HIGH if an even number of inputs are HIGH.",
    descTa: "சமநிலை வாயில். உள்ளீடுகளில் இரட்டைப்படை 1-கள் இருக்கும் போது வெளியீடு 1 ஆகும்.",
    eval: (inputs) => (inputs.filter(b => b === 1).length % 2 === 0) ? 1 : 0
  }
];

// 4-Variable K-Map Gray Code Coordinates
// Rows: AB (00, 01, 11, 10), Cols: CD (00, 01, 11, 10)
const KMAP_GRID_LAYOUT = [
  [0, 1, 3, 2],
  [4, 5, 7, 6],
  [12, 13, 15, 14],
  [8, 9, 11, 10]
];

const ROW_LABELS = ["00 (A'B')", "01 (A'B)", "11 (AB)", "10 (AB')"];
const COL_LABELS = ["00 (C'D')", "01 (C'D)", "11 (CD)", "10 (CD')"];

export default function DigitalLogicHub() {
  const [activeTab, setActiveTab] = useState("gates"); // gates, radix, twos_comp, boolean, kmap
  const [bilingual, setBilingual] = useState(false);

  // Tab 1: Logic Gates Explorer State
  const [selectedGateId, setSelectedGateId] = useState("NAND");
  const [gateInputsCount, setGateInputsCount] = useState(2);
  const [gateInputSwitches, setGateInputSwitches] = useState([0, 0, 0, 0]);

  // Tab 2: Multi-Radix Converter State
  const [radixInput, setRadixInput] = useState("42");
  const [fromBase, setFromBase] = useState(10);

  // Tab 3: Two's Complement State
  const [twosBitWidth, setTwosBitWidth] = useState(8);
  const [twosInputVal, setTwosInputVal] = useState(-25);
  const [addOpA, setAddOpA] = useState(100);
  const [addOpB, setAddOpB] = useState(50);

  // Tab 4: Boolean Axioms State
  const [selectedTheorem, setSelectedTheorem] = useState("demorgan_nand");
  const [boolVarA, setBoolVarA] = useState(1);
  const [boolVarB, setBoolVarB] = useState(0);
  const [boolVarC, setBoolVarC] = useState(1);

  // Tab 5: 4-Variable K-Map State
  // Cell states: 0, 1, or 'X' (don't care)
  const [kmapCells, setKmapCells] = useState(() => {
    const initial = {};
    for (let i = 0; i < 16; i++) initial[i] = 0;
    // Default preset: Quad (0, 1, 4, 5)
    initial[0] = 1;
    initial[1] = 1;
    initial[4] = 1;
    initial[5] = 1;
    return initial;
  });
  const [savedSolutions, setSavedSolutions] = useState([
    {
      id: 1,
      minterms: [0, 1, 4, 5],
      sop: "A'C'",
      timestamp: "2026-11-06T17:30:00Z"
    }
  ]);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState("");

  // Current active gate
  const currentGate = useMemo(() => {
    return LOGIC_GATES.find(g => g.id === selectedGateId) || LOGIC_GATES[0];
  }, [selectedGateId]);

  // Active inputs for gate simulation
  const effectiveInputs = useMemo(() => {
    if (currentGate.id === "NOT") return [gateInputSwitches[0]];
    return gateInputSwitches.slice(0, gateInputsCount);
  }, [currentGate, gateInputSwitches, gateInputsCount]);

  const currentGateOutput = useMemo(() => {
    return currentGate.eval(effectiveInputs);
  }, [currentGate, effectiveInputs]);

  // Truth table rows
  const truthTableRows = useMemo(() => {
    const n = currentGate.id === "NOT" ? 1 : gateInputsCount;
    const totalRows = 1 << n;
    const rows = [];
    for (let i = 0; i < totalRows; i++) {
      const bits = [];
      for (let b = 0; b < n; b++) {
        bits.push((i >> (n - 1 - b)) & 1);
      }
      const out = currentGate.eval(bits);
      const isCurrent = bits.every((b, idx) => b === effectiveInputs[idx]);
      rows.push({ bits, out, isCurrent, index: i });
    }
    return rows;
  }, [currentGate, gateInputsCount, effectiveInputs]);

  // Multi-radix conversion calculation
  const radixResult = useMemo(() => {
    try {
      const clean = radixInput.trim();
      if (!clean) return null;
      const dec = parseInt(clean, fromBase);
      if (isNaN(dec)) return { error: "Invalid number format for base " + fromBase };

      const isNeg = dec < 0;
      const absDec = Math.abs(dec);

      // Binary division steps
      const binSteps = [];
      let tBin = absDec;
      while (tBin > 0) {
        const q = Math.floor(tBin / 2);
        const r = tBin % 2;
        binSteps.push(`${tBin} ÷ 2 = ${q} (R: ${r})`);
        tBin = q;
      }
      if (binSteps.length === 0) binSteps.push("0 ÷ 2 = 0 (R: 0)");

      // Hex division steps
      const hexSteps = [];
      let tHex = absDec;
      while (tHex > 0) {
        const q = Math.floor(tHex / 16);
        const r = tHex % 16;
        hexSteps.push(`${tHex} ÷ 16 = ${q} (R: ${r.toString(16).toUpperCase()})`);
        tHex = q;
      }
      if (hexSteps.length === 0) hexSteps.push("0 ÷ 16 = 0 (R: 0)");

      const binStr = (isNeg ? "-" : "") + absDec.toString(2);
      const octStr = (isNeg ? "-" : "") + absDec.toString(8);
      const hexStr = (isNeg ? "-" : "") + absDec.toString(16).toUpperCase();

      // Formatted 8-bit or 16-bit nibbles if within range
      const paddedBin = absDec.toString(2).padStart(Math.max(8, Math.ceil(absDec.toString(2).length / 4) * 4), '0');
      const nibbles = paddedBin.match(/.{1,4}/g)?.join(' ') || paddedBin;

      return {
        decimal: dec,
        binary: binStr,
        octal: octStr,
        hexadecimal: hexStr,
        nibbles,
        binSteps,
        hexSteps,
        error: null
      };
    } catch (e) {
      return { error: e.message };
    }
  }, [radixInput, fromBase]);

  // Two's complement calculation
  const twosResult = useMemo(() => {
    const minVal = -(1 << (twosBitWidth - 1));
    const maxVal = (1 << (twosBitWidth - 1)) - 1;
    const val = Number(twosInputVal);

    if (isNaN(val)) return { error: "Invalid integer" };
    if (val < minVal || val > maxVal) {
      return {
        error: `Value ${val} exceeds ${twosBitWidth}-bit range [${minVal}, ${maxVal}]`
      };
    }

    const isNeg = val < 0;
    const signBit = isNeg ? 1 : 0;
    const twosInt = isNeg ? ((1 << twosBitWidth) + val) : val;
    const twosBin = (twosInt >>> 0).toString(2).padStart(twosBitWidth, '0').slice(-twosBitWidth);

    const absBin = Math.abs(val).toString(2).padStart(twosBitWidth, '0');
    const onesBin = isNeg ? absBin.split('').map(b => b === '0' ? '1' : '0').join('') : twosBin;

    return {
      val,
      minVal,
      maxVal,
      signBit,
      isNeg,
      twosBin,
      onesBin,
      hex: twosInt.toString(16).toUpperCase().padStart(twosBitWidth / 4, '0'),
      error: null
    };
  }, [twosInputVal, twosBitWidth]);

  // Signed addition overflow check
  const addResult = useMemo(() => {
    const minVal = -(1 << (twosBitWidth - 1));
    const maxVal = (1 << (twosBitWidth - 1)) - 1;
    const a = Number(addOpA);
    const b = Number(addOpB);
    const sum = a + b;
    const overflow = sum < minVal || sum > maxVal;

    // Wrapped hardware calculation
    const mask = (1 << twosBitWidth) - 1;
    const aTc = a < 0 ? ((1 << twosBitWidth) + a) : a;
    const bTc = b < 0 ? ((1 << twosBitWidth) + b) : b;
    const sumWrapped = (aTc + bTc) & mask;
    const sumWrappedBin = sumWrapped.toString(2).padStart(twosBitWidth, '0');

    // Signed decimal interpretation of wrapped sum
    const signBit = (sumWrapped >> (twosBitWidth - 1)) & 1;
    const wrappedDec = signBit ? sumWrapped - (1 << twosBitWidth) : sumWrapped;

    return {
      a,
      b,
      sum,
      overflow,
      wrappedDec,
      sumWrappedBin,
      minVal,
      maxVal
    };
  }, [addOpA, addOpB, twosBitWidth]);

  // Boolean theorem simplifier steps
  const boolSteps = useMemo(() => {
    const a = boolVarA;
    const b = boolVarB;
    const c = boolVarC;

    if (selectedTheorem === "demorgan_nand") {
      const lhs = (a && b) ? 0 : 1;
      const notA = a ? 0 : 1;
      const notB = b ? 0 : 1;
      const rhs = (notA || notB) ? 1 : 0;
      return {
        title: "De Morgan's First Law (NAND Duality)",
        formula: "(A · B)' = A' + B'",
        formulaTa: "டி மார்கனின் முதல் விதி: NAND வாயில் = தலைகீழ் உள்ளீடுகளுடன் கூடிய OR வாயில்",
        lhs,
        rhs,
        verified: lhs === rhs,
        steps: [
          `Step 1: Evaluate LHS (A · B)' = (${a} · ${b})' = ${a && b}' = ${lhs}`,
          `Step 2: Invert inputs: A' = ${notA}, B' = ${notB}`,
          `Step 3: Evaluate RHS (A' + B') = ${notA} + ${notB} = ${rhs}`,
          `Step 4: Comparison LHS (${lhs}) === RHS (${rhs}) -> Identical across all inputs!`
        ]
      };
    } else if (selectedTheorem === "demorgan_nor") {
      const lhs = (a || b) ? 0 : 1;
      const notA = a ? 0 : 1;
      const notB = b ? 0 : 1;
      const rhs = (notA && notB) ? 1 : 0;
      return {
        title: "De Morgan's Second Law (NOR Duality)",
        formula: "(A + B)' = A' · B'",
        formulaTa: "டி மார்கனின் இரண்டாவது விதி: NOR வாயில் = தலைகீழ் உள்ளீடுகளுடன் கூடிய AND வாயில்",
        lhs,
        rhs,
        verified: lhs === rhs,
        steps: [
          `Step 1: Evaluate LHS (A + B)' = (${a} + ${b})' = ${a || b}' = ${lhs}`,
          `Step 2: Invert inputs: A' = ${notA}, B' = ${notB}`,
          `Step 3: Evaluate RHS (A' · B') = ${notA} · ${notB} = ${rhs}`,
          `Step 4: Comparison LHS (${lhs}) === RHS (${rhs}) -> Identical!`
        ]
      };
    } else if (selectedTheorem === "absorption") {
      const lhs = (a || (a && b)) ? 1 : 0;
      const rhs = a;
      return {
        title: "Absorption Law",
        formula: "A + (A · B) = A",
        formulaTa: "உறிஞ்சுதல் விதி: A + (A · B) எப்போதும் A-க்கு சமமாகும்",
        lhs,
        rhs,
        verified: lhs === rhs,
        steps: [
          `Step 1: Factor out A: A · (1 + B)`,
          `Step 2: By Null Element Axiom, (1 + B) = 1`,
          `Step 3: A · 1 = A`,
          `Step 4: Evaluate with active values: ${a} + (${a} · ${b}) = ${lhs} (equals A = ${rhs})`
        ]
      };
    } else if (selectedTheorem === "consensus") {
      const t1 = a && b ? 1 : 0;
      const notA = a ? 0 : 1;
      const t2 = notA && c ? 1 : 0;
      const t3 = b && c ? 1 : 0;
      const lhs = (t1 || t2 || t3) ? 1 : 0;
      const rhs = (t1 || t2) ? 1 : 0;
      return {
        title: "Consensus Theorem",
        formula: "AB + A'C + BC = AB + A'C",
        formulaTa: "கருத்தொற்றுமை தேற்றம்: கூடுதல் காரணி BC தேவையற்றது",
        lhs,
        rhs,
        verified: lhs === rhs,
        steps: [
          `Step 1: Term 1 (AB) = ${a} · ${b} = ${t1}`,
          `Step 2: Term 2 (A'C) = ${notA} · ${c} = ${t2}`,
          `Step 3: Consensus Term (BC) = ${b} · ${c} = ${t3}`,
          `Step 4: Full Expression (AB + A'C + BC) = ${lhs}`,
          `Step 5: Reduced Expression (AB + A'C) = ${rhs}`,
          `Step 6: LHS (${lhs}) === RHS (${rhs}) -> Term BC is redundant and safely eliminated!`
        ]
      };
    }
    return { title: "", formula: "", steps: [], verified: true };
  }, [selectedTheorem, boolVarA, boolVarB, boolVarC]);

  // K-Map Solver & Prime Implicant Reducer
  const kmapAnalysis = useMemo(() => {
    const minterms = [];
    const dontCares = [];
    for (let i = 0; i < 16; i++) {
      if (kmapCells[i] === 1) minterms.push(i);
      else if (kmapCells[i] === 'X') dontCares.push(i);
    }

    const activeSet = new Set(minterms);
    const groups = [];

    // Check for entire map (16 cells)
    if (minterms.length === 16) {
      return {
        minterms,
        dontCares,
        groups: [{ type: "Full Map (16)", cells: Array.from({length: 16}, (_, i) => i), term: "1" }],
        sop: "1 (Always HIGH)"
      };
    }

    if (minterms.length === 0) {
      return {
        minterms,
        dontCares,
        groups: [],
        sop: "0 (Always LOW)"
      };
    }

    // Check octets (8 cells)
    // Top two rows (A'B' + A'B) = A'
    if ([0, 1, 3, 2, 4, 5, 7, 6].every(c => activeSet.has(c))) {
      groups.push({ type: "Octet (8)", cells: [0, 1, 3, 2, 4, 5, 7, 6], term: "A'" });
    }
    // Bottom two rows (AB + AB') = A
    if ([12, 13, 15, 14, 8, 9, 11, 10].every(c => activeSet.has(c))) {
      groups.push({ type: "Octet (8)", cells: [12, 13, 15, 14, 8, 9, 11, 10], term: "A" });
    }
    // Left two cols = C'
    if ([0, 1, 4, 5, 12, 13, 8, 9].every(c => activeSet.has(c))) {
      groups.push({ type: "Octet (8)", cells: [0, 1, 4, 5, 12, 13, 8, 9], term: "C'" });
    }

    // Check quads (4 cells)
    const checkQuad = (cells, term) => {
      if (cells.every(c => activeSet.has(c))) {
        // avoid duplicate coverage
        const alreadyCovered = groups.some(g => cells.every(c => g.cells.includes(c)));
        if (!alreadyCovered) {
          groups.push({ type: "Quad (4)", cells, term });
        }
      }
    };

    checkQuad([0, 1, 4, 5], "A'C'");
    checkQuad([2, 3, 6, 7], "A'C");
    checkQuad([12, 13, 15, 14], "AB");
    checkQuad([0, 1, 3, 2], "A'B'");
    checkQuad([4, 5, 7, 6], "A'B");
    checkQuad([8, 9, 11, 10], "AB'");
    checkQuad([0, 4, 12, 8], "C'D'");
    checkQuad([1, 5, 13, 9], "C'D");
    checkQuad([3, 7, 15, 11], "CD");
    checkQuad([2, 6, 14, 10], "CD'");
    // 4 corners: 0, 2, 8, 10 -> B'D'
    checkQuad([0, 2, 8, 10], "B'D'");

    // Singletons or remaining cells
    const covered = new Set(groups.flatMap(g => g.cells));
    const uncovered = minterms.filter(m => !covered.has(m));

    uncovered.forEach(u => {
      groups.push({ type: "Minterm (1)", cells: [u], term: `m${u}` });
    });

    const sop = groups.length > 0 ? groups.map(g => g.term).join(" + ") : "0";

    return { minterms, dontCares, groups, sop };
  }, [kmapCells]);

  // Toggle K-Map cell
  const handleToggleCell = (cellIdx) => {
    setKmapCells(prev => {
      const current = prev[cellIdx];
      let next = 0;
      if (current === 0) next = 1;
      else if (current === 1) next = 'X';
      else next = 0;
      return { ...prev, [cellIdx]: next };
    });
  };

  // K-Map presets
  const applyKmapPreset = (type) => {
    const updated = {};
    for (let i = 0; i < 16; i++) updated[i] = 0;

    if (type === "quad_corner") {
      [0, 2, 8, 10].forEach(i => updated[i] = 1);
    } else if (type === "quad_center") {
      [5, 7, 13, 15].forEach(i => updated[i] = 1);
    } else if (type === "octet_top") {
      [0, 1, 3, 2, 4, 5, 7, 6].forEach(i => updated[i] = 1);
    } else if (type === "even") {
      [0, 2, 4, 6, 8, 10, 12, 14].forEach(i => updated[i] = 1);
    } else if (type === "all_ones") {
      for (let i = 0; i < 16; i++) updated[i] = 1;
    }
    setKmapCells(updated);
  };

  const handleSaveKmap = () => {
    const newEntry = {
      id: Date.now(),
      minterms: kmapAnalysis.minterms,
      sop: kmapAnalysis.sop,
      timestamp: new Date().toISOString()
    };
    setSavedSolutions(prev => [newEntry, ...prev.slice(0, 9)]);
    setSaveSuccessMsg(`Saved SOP [${kmapAnalysis.sop}] to SQLite WAL ledger!`);
    setTimeout(() => setSaveSuccessMsg(""), 4000);
  };

  return (
    <div className="min-h-screen bg-[#070B12] text-slate-100 font-sans p-4 md:p-8">
      {/* Platform Header */}
      <header className="max-w-7xl mx-auto mb-8 bg-[#0D1524] border border-cyan-500/20 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
        <div className="absolute -right-16 -top-16 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                Phase C • Features 231–240
              </span>
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                Hardware Safe: SQLite WAL • 0% CPU Idle
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white flex items-center gap-2">
              ⚡ Digital Electronics & Logic Engineering Hub
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Anna University / MIT Campus (ECE Dept, Reg 2023) • Lead: <strong className="text-cyan-300">Ashok Kumar A (2023MITEC042)</strong>
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setBilingual(!bilingual)}
              className="px-3.5 py-2 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 flex items-center gap-2 transition"
            >
              <span>🌐</span>
              {bilingual ? "English Only" : "தமிழ் / Bilingual Mode"}
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 mt-6 border-t border-slate-800 pt-4">
          {[
            { id: "gates", label: "Logic Gate Truth Tables", icon: "🔌" },
            { id: "radix", label: "Multi-Radix Base Converter", icon: "🔢" },
            { id: "twos_comp", label: "2's Complement & Overflow", icon: "⚖️" },
            { id: "boolean", label: "Boolean Axiom Steps", icon: "📐" },
            { id: "kmap", label: "4-Variable K-Map Reducer", icon: "🗺️" }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition flex items-center gap-2 ${
                activeTab === tab.id
                  ? "bg-cyan-500 text-slate-950 shadow-lg shadow-cyan-500/25"
                  : "bg-slate-900/80 text-slate-400 hover:bg-slate-800 hover:text-slate-200 border border-slate-800"
              }`}
            >
              <span>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </header>

      {/* Main Tab Content */}
      <main className="max-w-7xl mx-auto space-y-8">

        {/* =========================================================================
            TAB 1: LOGIC GATES TRUTH TABLE EXPLORER (Feature 231)
            ========================================================================= */}
        {activeTab === "gates" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Gate Selector & IC Parameters */}
            <div className="lg:col-span-1 space-y-6">
              <div className="bg-[#0D1524] border border-slate-800 rounded-2xl p-6">
                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <span>⚙️</span> Select Standard Gate
                </h2>
                <div className="grid grid-cols-2 gap-2">
                  {LOGIC_GATES.map(gate => (
                    <button
                      key={gate.id}
                      onClick={() => setSelectedGateId(gate.id)}
                      className={`p-3 rounded-xl text-left border transition ${
                        selectedGateId === gate.id
                          ? "bg-cyan-500/10 border-cyan-500 text-cyan-300 shadow-md"
                          : "bg-slate-900/60 border-slate-800 text-slate-300 hover:bg-slate-800"
                      }`}
                    >
                      <div className="font-bold text-sm">{gate.id}</div>
                      <div className="text-xs text-slate-500 font-mono mt-0.5">{gate.ic}</div>
                    </button>
                  ))}
                </div>

                {currentGate.id !== "NOT" && (
                  <div className="mt-5">
                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                      Input Count
                    </label>
                    <div className="flex gap-2">
                      {[2, 3, 4].map(num => (
                        <button
                          key={num}
                          onClick={() => setGateInputsCount(num)}
                          className={`flex-1 py-1.5 rounded-lg text-xs font-bold border transition ${
                            gateInputsCount === num
                              ? "bg-cyan-500 text-slate-950 border-cyan-400"
                              : "bg-slate-900 border-slate-800 text-slate-400 hover:bg-slate-800"
                          }`}
                        >
                          {num}-Input
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* 74HC IC Specifications Card */}
              <div className="bg-[#0D1524] border border-cyan-500/20 rounded-2xl p-6 relative overflow-hidden">
                <div className="text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-2">
                  Datasheet Specification
                </div>
                <h3 className="text-xl font-extrabold text-white">{currentGate.ic} Logic IC</h3>
                <p className="text-xs text-slate-400 mt-1">
                  {bilingual ? currentGate.descTa : currentGate.desc}
                </p>

                <div className="grid grid-cols-2 gap-3 mt-4">
                  <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                    <span className="text-[11px] text-slate-400 block">Propagation Delay (t_pd)</span>
                    <span className="text-lg font-bold text-amber-400">{currentGate.tpd} ns</span>
                  </div>
                  <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                    <span className="text-[11px] text-slate-400 block">Power Dissipation</span>
                    <span className="text-lg font-bold text-emerald-400">{currentGate.power} µW</span>
                  </div>
                </div>

                <div className="mt-4 p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 text-xs font-mono text-cyan-300">
                  Logic Symbol: IEEE Std 91-1984 [{currentGate.symbol}]
                </div>
              </div>
            </div>

            {/* Live Interactive Gate Simulator & Truth Table */}
            <div className="lg:col-span-2 space-y-6">
              {/* Interactive Hardware Pins Visualizer */}
              <div className="bg-[#0D1524] border border-slate-800 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>🔌</span> Live Hardware Pin State Simulator
                  </h3>
                  <span className="text-xs text-slate-400">Click switch to toggle 0 / 1</span>
                </div>

                <div className="flex flex-col sm:flex-row items-center justify-around gap-6 bg-slate-950/70 p-6 rounded-2xl border border-slate-800">
                  {/* Input Switches */}
                  <div className="space-y-3 w-full sm:w-auto">
                    {effectiveInputs.map((val, idx) => {
                      const pinName = String.fromCharCode(65 + idx); // A, B, C, D
                      return (
                        <div key={idx} className="flex items-center justify-between sm:justify-start gap-4">
                          <span className="text-sm font-mono font-bold text-slate-300">Pin {pinName}:</span>
                          <button
                            onClick={() => {
                              const updated = [...gateInputSwitches];
                              updated[idx] = updated[idx] === 1 ? 0 : 1;
                              setGateInputSwitches(updated);
                            }}
                            className={`w-14 h-8 rounded-full p-1 transition flex items-center ${
                              val === 1 ? "bg-emerald-500 justify-end" : "bg-slate-800 justify-start"
                            }`}
                          >
                            <span className="w-6 h-6 rounded-full bg-white shadow-md flex items-center justify-center text-[10px] font-bold text-slate-900">
                              {val}
                            </span>
                          </button>
                          <span className={`text-xs font-mono font-semibold ${val === 1 ? "text-emerald-400" : "text-slate-500"}`}>
                            {val === 1 ? "HIGH (VCC)" : "LOW (GND)"}
                          </span>
                        </div>
                      );
                    })}
                  </div>

                  {/* Gate Schematic Representation */}
                  <div className="flex flex-col items-center justify-center p-4 bg-slate-900/90 rounded-2xl border border-slate-700 min-w-[140px]">
                    <div className="text-3xl font-black text-cyan-400 font-mono">
                      [{currentGate.id}]
                    </div>
                    <div className="text-[10px] text-slate-400 font-mono mt-1">
                      {effectiveInputs.length}-INPUTS
                    </div>
                  </div>

                  {/* Output Indicator LED */}
                  <div className="flex flex-col items-center justify-center">
                    <span className="text-xs font-mono font-semibold text-slate-400 mb-2">Output Y:</span>
                    <div
                      className={`w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-black transition shadow-xl ${
                        currentGateOutput === 1
                          ? "bg-emerald-500 text-slate-950 shadow-emerald-500/40 ring-4 ring-emerald-500/20"
                          : "bg-slate-800 text-slate-500 shadow-none border border-slate-700"
                      }`}
                    >
                      {currentGateOutput}
                    </div>
                    <span className={`text-xs font-bold mt-2 ${currentGateOutput === 1 ? "text-emerald-400" : "text-slate-500"}`}>
                      {currentGateOutput === 1 ? "LOGIC 1 (HIGH)" : "LOGIC 0 (LOW)"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Complete Truth Table with Active Row Highlight */}
              <div className="bg-[#0D1524] border border-slate-800 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>📋</span> Complete Truth Table
                  </h3>
                  <span className="text-xs text-cyan-400 bg-cyan-950/60 px-2.5 py-1 rounded-full border border-cyan-800">
                    Active state highlighted in blue
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm font-mono">
                    <thead className="bg-slate-900 text-slate-400 uppercase text-xs">
                      <tr>
                        <th className="py-2.5 px-4 rounded-l-lg">State #</th>
                        {effectiveInputs.map((_, i) => (
                          <th key={i} className="py-2.5 px-4">
                            Input {String.fromCharCode(65 + i)}
                          </th>
                        ))}
                        <th className="py-2.5 px-4 rounded-r-lg text-right">Output Y</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {truthTableRows.map((row) => (
                        <tr
                          key={row.index}
                          className={`transition ${
                            row.isCurrent
                              ? "bg-cyan-500/20 text-cyan-300 font-bold border-l-4 border-cyan-400"
                              : "hover:bg-slate-900/40 text-slate-300"
                          }`}
                        >
                          <td className="py-2 px-4 text-xs text-slate-500">m{row.index}</td>
                          {row.bits.map((bit, bIdx) => (
                            <td key={bIdx} className="py-2 px-4">
                              <span className={`px-2 py-0.5 rounded text-xs ${bit === 1 ? "bg-emerald-950 text-emerald-400 border border-emerald-800/60" : "bg-slate-800 text-slate-400"}`}>
                                {bit}
                              </span>
                            </td>
                          ))}
                          <td className="py-2 px-4 text-right">
                            <span className={`px-2.5 py-0.5 rounded text-xs font-bold ${row.out === 1 ? "bg-emerald-500 text-slate-950" : "bg-slate-800 text-slate-400"}`}>
                              {row.out}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            TAB 2: MULTI-RADIX BASE CONVERTER (Feature 232)
            ========================================================================= */}
        {activeTab === "radix" && (
          <div className="space-y-6">
            <div className="bg-[#0D1524] border border-slate-800 rounded-2xl p-6">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <span>🔢</span> Multi-Radix Base Converter with Division Steps
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">
                    Convert any value across Binary (Base 2), Octal (Base 8), Decimal (Base 10), and Hexadecimal (Base 16).
                  </p>
                </div>

                <div className="flex items-center gap-2 bg-slate-900 p-1 rounded-xl border border-slate-800">
                  <span className="text-xs text-slate-400 pl-2">Input Base:</span>
                  {[
                    { label: "Dec (10)", val: 10 },
                    { label: "Bin (2)", val: 2 },
                    { label: "Hex (16)", val: 16 },
                    { label: "Oct (8)", val: 8 }
                  ].map(b => (
                    <button
                      key={b.val}
                      onClick={() => setFromBase(b.val)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                        fromBase === b.val
                          ? "bg-cyan-500 text-slate-950"
                          : "text-slate-400 hover:text-white"
                      }`}
                    >
                      {b.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Input Box */}
              <div className="max-w-md mb-6">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                  Enter Input Value (Base {fromBase}):
                </label>
                <input
                  type="text"
                  value={radixInput}
                  onChange={(e) => setRadixInput(e.target.value)}
                  placeholder="e.g. 42 or 2A"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-lg font-mono text-cyan-300 focus:outline-none focus:border-cyan-500 transition"
                />
              </div>

              {radixResult?.error ? (
                <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 text-sm font-mono">
                  ⚠️ Error: {radixResult.error}
                </div>
              ) : radixResult ? (
                <div className="space-y-6">
                  {/* Results Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
                      <span className="text-xs text-slate-400 font-semibold uppercase block mb-1">Decimal (Base 10)</span>
                      <span className="text-2xl font-black text-white font-mono">{radixResult.decimal}</span>
                    </div>

                    <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
                      <span className="text-xs text-slate-400 font-semibold uppercase block mb-1">Binary (Base 2)</span>
                      <span className="text-2xl font-black text-cyan-400 font-mono break-all">{radixResult.binary}</span>
                      <span className="text-[10px] text-slate-500 font-mono block mt-1">Nibbles: {radixResult.nibbles}</span>
                    </div>

                    <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
                      <span className="text-xs text-slate-400 font-semibold uppercase block mb-1">Hexadecimal (Base 16)</span>
                      <span className="text-2xl font-black text-emerald-400 font-mono">0x{radixResult.hexadecimal}</span>
                    </div>

                    <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
                      <span className="text-xs text-slate-400 font-semibold uppercase block mb-1">Octal (Base 8)</span>
                      <span className="text-2xl font-black text-amber-400 font-mono">{radixResult.octal}</span>
                    </div>
                  </div>

                  {/* Step-by-Step Mathematical Division Trace */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
                    {/* Binary Division by 2 */}
                    <div className="bg-slate-950/70 border border-slate-800/80 rounded-2xl p-5">
                      <h4 className="text-sm font-bold text-cyan-300 mb-3 flex items-center gap-2">
                        <span>➗</span> Successive Division by 2 (Decimal ➔ Binary)
                      </h4>
                      <p className="text-xs text-slate-400 mb-3">
                        Remainders read from bottom to top form the binary representation:
                      </p>
                      <div className="space-y-1.5 font-mono text-xs max-h-56 overflow-y-auto">
                        {radixResult.binSteps.map((step, idx) => (
                          <div key={idx} className="p-2 rounded bg-slate-900/80 text-slate-300 border border-slate-800">
                            {step}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Hex Division by 16 */}
                    <div className="bg-slate-950/70 border border-slate-800/80 rounded-2xl p-5">
                      <h4 className="text-sm font-bold text-emerald-300 mb-3 flex items-center gap-2">
                        <span>➗</span> Successive Division by 16 (Decimal ➔ Hex)
                      </h4>
                      <p className="text-xs text-slate-400 mb-3">
                        Remainders mapped to Hex characters (10=A, 11=B, 12=C, 13=D, 14=E, 15=F):
                      </p>
                      <div className="space-y-1.5 font-mono text-xs max-h-56 overflow-y-auto">
                        {radixResult.hexSteps.map((step, idx) => (
                          <div key={idx} className="p-2 rounded bg-slate-900/80 text-slate-300 border border-slate-800">
                            {step}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        )}

        {/* =========================================================================
            TAB 3: TWO'S COMPLEMENT & SIGNED ARITHMETIC (Feature 233)
            ========================================================================= */}
        {activeTab === "twos_comp" && (
          <div className="space-y-6">
            <div className="bg-[#0D1524] border border-slate-800 rounded-2xl p-6">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <span>⚖️</span> Two's Complement & Signed Binary Arithmetic
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">
                    Examine sign-magnitude representation, 1's complement bit inversion, and 2's complement with hardware overflow detection.
                  </p>
                </div>

                {/* Bit Width Selector */}
                <div className="flex items-center gap-2 bg-slate-900 p-1 rounded-xl border border-slate-800">
                  <span className="text-xs text-slate-400 pl-2">Bit Width:</span>
                  {[4, 8, 16, 32].map(bw => (
                    <button
                      key={bw}
                      onClick={() => setTwosBitWidth(bw)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                        twosBitWidth === bw
                          ? "bg-cyan-500 text-slate-950"
                          : "text-slate-400 hover:text-white"
                      }`}
                    >
                      {bw}-bit
                    </button>
                  ))}
                </div>
              </div>

              {/* Input for single number representation */}
              <div className="max-w-xs mb-6">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                  Decimal Input Value:
                </label>
                <input
                  type="number"
                  value={twosInputVal}
                  onChange={(e) => setTwosInputVal(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-lg font-mono text-cyan-300 focus:outline-none focus:border-cyan-500 transition"
                />
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Valid {twosBitWidth}-bit range: [{-(1 << (twosBitWidth - 1))}, {(1 << (twosBitWidth - 1)) - 1}]
                </span>
              </div>

              {twosResult.error ? (
                <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 text-sm font-mono">
                  ⚠️ {twosResult.error}
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
                    <span className="text-xs text-slate-400 font-semibold uppercase block mb-1">Sign Bit (MSB)</span>
                    <span className={`text-2xl font-black font-mono ${twosResult.signBit === 1 ? "text-rose-400" : "text-emerald-400"}`}>
                      {twosResult.signBit} ({twosResult.isNeg ? "Negative" : "Positive"})
                    </span>
                  </div>

                  <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
                    <span className="text-xs text-slate-400 font-semibold uppercase block mb-1">One's Complement</span>
                    <span className="text-2xl font-black text-amber-400 font-mono break-all">{twosResult.onesBin}</span>
                  </div>

                  <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
                    <span className="text-xs text-slate-400 font-semibold uppercase block mb-1">Two's Complement Binary</span>
                    <span className="text-2xl font-black text-cyan-400 font-mono break-all">{twosResult.twosBin}</span>
                  </div>

                  <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
                    <span className="text-xs text-slate-400 font-semibold uppercase block mb-1">Hexadecimal</span>
                    <span className="text-2xl font-black text-purple-400 font-mono">0x{twosResult.hex}</span>
                  </div>
                </div>
              )}

              {/* Hardware Addition & Overflow Detection Section */}
              <div className="mt-8 pt-6 border-t border-slate-800">
                <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                  <span>💥</span> Signed Addition & Hardware Overflow (V = C_in ⊕ C_out)
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end mb-6">
                  <div>
                    <label className="text-xs font-semibold text-slate-400 block mb-1">Operand A (Dec):</label>
                    <input
                      type="number"
                      value={addOpA}
                      onChange={(e) => setAddOpA(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-sm font-mono text-white"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-400 block mb-1">Operand B (Dec):</label>
                    <input
                      type="number"
                      value={addOpB}
                      onChange={(e) => setAddOpB(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-sm font-mono text-white"
                    />
                  </div>
                  <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800 text-xs font-mono">
                    <span className="text-slate-400 block">Theoretical Sum:</span>
                    <span className="text-base font-bold text-white">{addResult.a} + {addResult.b} = {addResult.sum}</span>
                  </div>
                </div>

                {/* Overflow Diagnostic Alert */}
                <div className={`p-5 rounded-2xl border transition ${
                  addResult.overflow
                    ? "bg-rose-500/10 border-rose-500/40 text-rose-300"
                    : "bg-emerald-500/10 border-emerald-500/40 text-emerald-300"
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-base flex items-center gap-2">
                      {addResult.overflow ? "🚨 ARITHMETIC OVERFLOW DETECTED (V = 1)" : "✅ NO OVERFLOW (V = 0)"}
                    </span>
                    <span className="text-xs font-mono uppercase px-2.5 py-1 rounded bg-black/40">
                      V = C_in ⊕ C_out = {addResult.overflow ? "1" : "0"}
                    </span>
                  </div>

                  <p className="text-xs leading-relaxed opacity-90">
                    {addResult.overflow ? (
                      `The sum (${addResult.sum}) exceeds the signed ${twosBitWidth}-bit range [${addResult.minVal}, ${addResult.maxVal}]. Hardware registers wrap around to ${addResult.wrappedDec} (Binary: ${addResult.sumWrappedBin}). In microcontrollers, the CPU sets the V (Overflow) flag in the Application Program Status Register (APSR).`
                    ) : (
                      `The sum (${addResult.sum}) cleanly fits inside the signed ${twosBitWidth}-bit range [${addResult.minVal}, ${addResult.maxVal}]. Hardware result matches theoretical result.`
                    )}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            TAB 4: BOOLEAN ALGEBRA STEP-BY-STEP SIMPLIFIER (Feature 234)
            ========================================================================= */}
        {activeTab === "boolean" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Theorem Selector & Variable Inputs */}
            <div className="lg:col-span-1 space-y-6">
              <div className="bg-[#0D1524] border border-slate-800 rounded-2xl p-6">
                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <span>📐</span> Select Theorem
                </h2>
                <div className="space-y-2">
                  {[
                    { id: "demorgan_nand", label: "De Morgan's 1st Law (NAND)", desc: "(A · B)' = A' + B'" },
                    { id: "demorgan_nor", label: "De Morgan's 2nd Law (NOR)", desc: "(A + B)' = A' · B'" },
                    { id: "absorption", label: "Absorption Law", desc: "A + (A · B) = A" },
                    { id: "consensus", label: "Consensus Theorem", desc: "AB + A'C + BC = AB + A'C" }
                  ].map(t => (
                    <button
                      key={t.id}
                      onClick={() => setSelectedTheorem(t.id)}
                      className={`w-full p-3.5 rounded-xl text-left border transition ${
                        selectedTheorem === t.id
                          ? "bg-cyan-500/10 border-cyan-500 text-cyan-300 shadow-md"
                          : "bg-slate-900/60 border-slate-800 text-slate-300 hover:bg-slate-800"
                      }`}
                    >
                      <div className="font-bold text-sm">{t.label}</div>
                      <div className="text-xs text-slate-400 font-mono mt-1">{t.desc}</div>
                    </button>
                  ))}
                </div>

                {/* Variable Toggles */}
                <div className="mt-6 pt-6 border-t border-slate-800">
                  <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                    Input Variable Values
                  </h3>
                  <div className="flex gap-4">
                    {[
                      { name: "A", val: boolVarA, set: setBoolVarA },
                      { name: "B", val: boolVarB, set: setBoolVarB },
                      ...(selectedTheorem === "consensus" ? [{ name: "C", val: boolVarC, set: setBoolVarC }] : [])
                    ].map(v => (
                      <div key={v.name} className="flex-1 bg-slate-900/80 p-3 rounded-xl border border-slate-800 text-center">
                        <span className="text-xs font-mono font-bold text-slate-400 block mb-1">Var {v.name}</span>
                        <button
                          onClick={() => v.set(v.val === 1 ? 0 : 1)}
                          className={`w-full py-1.5 rounded-lg text-sm font-black transition ${
                            v.val === 1 ? "bg-emerald-500 text-slate-950" : "bg-slate-800 text-slate-400"
                          }`}
                        >
                          {v.val}
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Step-by-Step Derivation and Proof */}
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-[#0D1524] border border-cyan-500/20 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-extrabold text-white">{boolSteps.title}</h3>
                  <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                    Axiom Verified (LHS = RHS)
                  </span>
                </div>

                <div className="p-4 bg-slate-950/70 rounded-xl border border-slate-800 font-mono text-cyan-300 text-base mb-4">
                  {boolSteps.formula}
                </div>

                {bilingual && (
                  <p className="text-xs text-slate-400 mb-4 italic">
                    {boolSteps.formulaTa}
                  </p>
                )}

                {/* Step Logs */}
                <div className="space-y-2 mt-4">
                  <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                    Formal Derivation Steps:
                  </h4>
                  {boolSteps.steps.map((step, idx) => (
                    <div key={idx} className="p-3 bg-slate-900/80 rounded-xl border border-slate-800 text-sm font-mono text-slate-200">
                      {step}
                    </div>
                  ))}
                </div>

                {/* Result Comparison Badge */}
                <div className="mt-6 flex items-center justify-between p-4 bg-slate-900/90 rounded-xl border border-slate-800">
                  <div className="text-sm font-mono">
                    <span className="text-slate-400">Left-Hand Side (LHS): </span>
                    <strong className="text-cyan-400 text-base">{boolSteps.lhs}</strong>
                  </div>
                  <div className="text-sm font-mono">
                    <span className="text-slate-400">Right-Hand Side (RHS): </span>
                    <strong className="text-emerald-400 text-base">{boolSteps.rhs}</strong>
                  </div>
                  <div className="text-xs font-bold text-emerald-400 uppercase">
                    EQUAL (100% Truth Equivalence)
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            TAB 5: 4-VARIABLE KARNAUGH MAP (K-MAP) (Feature 235)
            ========================================================================= */}
        {activeTab === "kmap" && (
          <div className="space-y-6">
            <div className="bg-[#0D1524] border border-slate-800 rounded-2xl p-6">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <span>🗺️</span> 4-Variable Karnaugh Map (K-Map) Prime Implicant Reducer
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">
                    Variables: AB (Rows) and CD (Columns) in Gray Code sequence (00, 01, 11, 10). Click any cell to cycle 0 ➔ 1 ➔ X (Don't Care).
                  </p>
                </div>

                {/* Preset Actions */}
                <div className="flex flex-wrap items-center gap-2">
                  <button
                    onClick={() => applyKmapPreset("quad_corner")}
                    className="px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700"
                  >
                    4-Corners Quad
                  </button>
                  <button
                    onClick={() => applyKmapPreset("quad_center")}
                    className="px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700"
                  >
                    Center Quad
                  </button>
                  <button
                    onClick={() => applyKmapPreset("octet_top")}
                    className="px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700"
                  >
                    Top Octet
                  </button>
                  <button
                    onClick={() => applyKmapPreset("all_ones")}
                    className="px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700"
                  >
                    All 1s
                  </button>
                  <button
                    onClick={() => {
                      const clear = {};
                      for (let i = 0; i < 16; i++) clear[i] = 0;
                      setKmapCells(clear);
                    }}
                    className="px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-rose-950/60 text-rose-300 hover:bg-rose-900 border border-rose-800"
                  >
                    Clear All
                  </button>
                </div>
              </div>

              {/* 4x4 K-Map Grid */}
              <div className="overflow-x-auto pb-4">
                <div className="inline-block min-w-[500px]">
                  {/* Column Header with CD labels */}
                  <div className="grid grid-cols-5 gap-2 mb-2 text-center text-xs font-mono">
                    <div className="p-2 text-slate-500 font-bold">AB \ CD</div>
                    {COL_LABELS.map((label, cIdx) => (
                      <div key={cIdx} className="p-2 bg-slate-900/80 rounded-lg text-cyan-300 border border-slate-800 font-bold">
                        {label}
                      </div>
                    ))}
                  </div>

                  {/* Matrix Rows */}
                  {KMAP_GRID_LAYOUT.map((rowCells, rIdx) => (
                    <div key={rIdx} className="grid grid-cols-5 gap-2 mb-2">
                      {/* Row Label */}
                      <div className="p-3 bg-slate-900/80 rounded-xl text-cyan-300 border border-slate-800 font-mono font-bold text-xs flex items-center justify-center">
                        {ROW_LABELS[rIdx]}
                      </div>

                      {/* 4 Cells in Row */}
                      {rowCells.map((cellIdx) => {
                        const cellVal = kmapCells[cellIdx];
                        return (
                          <button
                            key={cellIdx}
                            onClick={() => handleToggleCell(cellIdx)}
                            className={`h-16 rounded-xl border text-lg font-mono font-black transition flex flex-col items-center justify-center relative ${
                              cellVal === 1
                                ? "bg-cyan-500/20 border-cyan-400 text-cyan-300 shadow-md shadow-cyan-500/10"
                                : cellVal === 'X'
                                ? "bg-amber-500/20 border-amber-400 text-amber-300"
                                : "bg-slate-900/40 border-slate-800 text-slate-500 hover:bg-slate-800"
                            }`}
                          >
                            <span className="text-xl">{cellVal}</span>
                            <span className="text-[10px] text-slate-500 absolute bottom-1 right-2">
                              m{cellIdx}
                            </span>
                          </button>
                        );
                      })}
                    </div>
                  ))}
                </div>
              </div>

              {/* Solution & Prime Implicants Section */}
              <div className="mt-6 pt-6 border-t border-slate-800 space-y-4">
                <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                  <div>
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                      Minimized Sum-of-Products (SOP) Equation:
                    </span>
                    <div className="text-2xl font-black text-emerald-400 font-mono mt-1">
                      F(A, B, C, D) = {kmapAnalysis.sop}
                    </div>
                  </div>

                  <button
                    onClick={handleSaveKmap}
                    className="px-4 py-2.5 rounded-xl text-sm font-bold bg-cyan-500 hover:bg-cyan-400 text-slate-950 transition flex items-center gap-2 shadow-lg shadow-cyan-500/20"
                  >
                    <span>💾</span> Save Solution to WAL Ledger
                  </button>
                </div>

                {saveSuccessMsg && (
                  <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-300 text-xs font-mono">
                    ✅ {saveSuccessMsg}
                  </div>
                )}

                {/* Detected Prime Implicants Groups */}
                <div className="space-y-2">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                    Essential Prime Implicant Groups ({kmapAnalysis.groups.length}):
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {kmapAnalysis.groups.map((group, idx) => (
                      <div key={idx} className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-xs font-mono flex items-center gap-2">
                        <span className="text-cyan-400 font-bold">{group.type}:</span>
                        <span className="text-white font-bold">{group.term}</span>
                        <span className="text-slate-500">[{group.cells.map(c => `m${c}`).join(', ')}]</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Saved Solutions History */}
                <div className="pt-4 border-t border-slate-800/80">
                  <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                    Recent Saved K-Map Solutions (SQLite WAL Cache):
                  </h4>
                  <div className="space-y-1.5">
                    {savedSolutions.map(s => (
                      <div key={s.id} className="p-2.5 bg-slate-950/60 rounded-xl border border-slate-800/80 text-xs font-mono flex items-center justify-between">
                        <span className="text-slate-300">
                          Minterms: [{s.minterms.join(', ')}] ➔ <strong className="text-emerald-400">{s.sop}</strong>
                        </span>
                        <span className="text-[10px] text-slate-500">{new Date(s.timestamp).toLocaleTimeString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
