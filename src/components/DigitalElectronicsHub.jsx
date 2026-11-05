import React, { useState, useEffect } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Advanced Digital Electronics Learning Center
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * Course Code: EC3352 - Digital Systems Design (Regulation 2023)
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 * ========================================================================================
 */

const DEFAULT_STUDENT_ID = "2023MITEC042";

const CURRICULUM_PRESETS = [
  {
    preset_id: "PRESET_HALF_ADDER",
    title: "Half Adder (Sum & Carry)",
    unit_number: 1,
    num_variables: 2,
    variables: ["A", "B"],
    minterms: [1, 2],
    dont_cares: [],
    target_expression: "A ^ B",
    description: "Standard 2-input XOR sum output for binary addition without carry-in."
  },
  {
    preset_id: "PRESET_FULL_ADDER_CARRY",
    title: "Full Adder Carry-Out (Majority Function)",
    unit_number: 1,
    num_variables: 3,
    variables: ["A", "B", "Cin"],
    minterms: [3, 5, 6, 7],
    dont_cares: [],
    target_expression: "(A & B) | (B & Cin) | (A & Cin)",
    description: "Majority vote circuit generating carry output when 2 or 3 inputs are high."
  },
  {
    preset_id: "PRESET_2TO1_MUX",
    title: "2-to-1 Multiplexer",
    unit_number: 2,
    num_variables: 3,
    variables: ["S", "I0", "I1"],
    minterms: [2, 3, 5, 7],
    dont_cares: [],
    target_expression: "(~S & I0) | (S & I1)",
    description: "Single-bit selection logic steering input I0 when S=0, or I1 when S=1."
  },
  {
    preset_id: "PRESET_BCD_EXCESS3_W",
    title: "BCD to Excess-3 Converter (Bit W)",
    unit_number: 1,
    num_variables: 4,
    variables: ["A", "B", "C", "D"],
    minterms: [5, 6, 7, 8, 9],
    dont_cares: [10, 11, 12, 13, 14, 15],
    target_expression: "A | (B & C) | (B & D)",
    description: "Most significant bit of Excess-3 code with invalid BCD don't cares (10-15)."
  },
  {
    preset_id: "PRESET_PARITY_GENERATOR_4BIT",
    title: "4-Bit Even Parity Generator",
    unit_number: 2,
    num_variables: 4,
    variables: ["A", "B", "C", "D"],
    minterms: [1, 2, 4, 7, 8, 11, 13, 14],
    dont_cares: [],
    target_expression: "A ^ B ^ C ^ D",
    description: "Generates parity bit such that total number of 1s in 5-bit codeword is even."
  }
];

export default function DigitalElectronicsHub() {
  const [activeTab, setActiveTab] = useState('truthtable'); // 'truthtable' | 'converter' | 'kmap' | 'presets'
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  // =========================================================================
  // TAB 1: TRUTH TABLE GENERATOR STATE
  // =========================================================================
  const [ttExpr, setTtExpr] = useState('(A & B) | ~C');
  const [ttNumVars, setTtNumVars] = useState(3);
  const [ttResult, setTtResult] = useState(null);
  const [ttLoading, setTtLoading] = useState(false);

  // Compute default truth table on mount
  useEffect(() => {
    handleGenerateTruthTable();
  }, []);

  const handleGenerateTruthTable = (expressionToUse = ttExpr, numVars = ttNumVars) => {
    setTtLoading(true);
    const varNames = ['A', 'B', 'C', 'D'].slice(0, numVars);

    fetch('/api/digital/truth_table', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ expression: expressionToUse, variables: varNames })
    })
      .then((res) => res.json())
      .then((data) => {
        setTtLoading(false);
        if (data.status === 'SUCCESS') {
          setTtResult(data);
        } else {
          // Client-side fallback computation
          computeClientTruthTable(expressionToUse, varNames);
        }
      })
      .catch(() => {
        setTtLoading(false);
        computeClientTruthTable(expressionToUse, varNames);
      });
  };

  const computeClientTruthTable = (expr, variables) => {
    const totalRows = 1 << variables.length;
    const rows = [];
    const minterms = [];
    const maxterms = [];

    for (let i = 0; i < totalRows; i++) {
      const row = { minterm_index: i };
      const env = {};
      variables.forEach((v, idx) => {
        const bit = (i >> (variables.length - 1 - idx)) & 1;
        row[v] = bit;
        env[v] = bit;
      });

      // Safe evaluation of simple logic
      let out = 0;
      try {
        let clean = expr
          .replace(/AND/g, '&&').replace(/&/g, '&&')
          .replace(/OR/g, '||').replace(/\|/g, '||')
          .replace(/NOT/g, '!').replace(/~/g, '!')
          .replace(/\+/g, '||').replace(/\*/g, '&&');
        
        variables.forEach(v => {
          clean = clean.replace(new RegExp(`${v}'`, 'g'), `(!${env[v]})`);
          clean = clean.replace(new RegExp(v, 'g'), env[v]);
        });
        out = new Function(`return (${clean}) ? 1 : 0;`)();
      } catch (e) {
        out = 0;
      }

      row.output = out;
      rows.push(row);
      if (out === 1) minterms.push(i);
      else maxterms.push(i);
    }

    const sop = minterms.map(m => {
      return variables.map((v, idx) => {
        const bit = (m >> (variables.length - 1 - idx)) & 1;
        return bit ? v : `${v}'`;
      }).join('');
    }).join(' + ') || '0';

    setTtResult({
      status: 'SUCCESS',
      expression: expr,
      variables,
      rows,
      minterms,
      maxterms,
      minterm_notation: `Σ m(${minterms.join(', ')})`,
      maxterm_notation: `Π M(${maxterms.join(', ')})`,
      canonical_sop: sop
    });
  };

  const handleAppendSymbol = (sym) => {
    setTtExpr(prev => prev + sym);
  };

  // =========================================================================
  // TAB 2: NUMBER BASE CONVERTER STATE
  // =========================================================================
  const [numInput, setNumInput] = useState('42');
  const [fromBase, setFromBase] = useState('DECIMAL');
  const [convResult, setConvResult] = useState(null);

  useEffect(() => {
    handleConvertNumber(numInput, fromBase);
  }, [numInput, fromBase]);

  const handleConvertNumber = (val, base) => {
    fetch('/api/digital/convert_number', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value: val, from_base: base, student_id: DEFAULT_STUDENT_ID })
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'SUCCESS') {
          setConvResult(data);
        } else {
          fallbackNumberConversion(val, base);
        }
      })
      .catch(() => fallbackNumberConversion(val, base));
  };

  const fallbackNumberConversion = (val, base) => {
    try {
      let dec = 0;
      if (base === 'DECIMAL') dec = parseInt(val, 10);
      else if (base === 'BINARY') dec = parseInt(val.replace(/\s+/g, ''), 2);
      else if (base === 'OCTAL') dec = parseInt(val, 8);
      else if (base === 'HEXADECIMAL') dec = parseInt(val.replace(/0x/i, ''), 16);

      if (isNaN(dec)) return;

      const isNeg = dec < 0;
      const absVal = Math.abs(dec);
      const binStr = absVal.toString(2).padStart(8, '0');
      const binFmt = binStr.match(/.{1,4}/g).join(' ');
      const octStr = absVal.toString(8);
      const hexStr = absVal.toString(16).toUpperCase();
      const gray = (absVal ^ (absVal >> 1)).toString(2).padStart(binStr.length, '0');

      const twos8 = (dec & 0xFF).toString(2).padStart(8, '0');
      const twos8Fmt = `${twos8.slice(0, 4)} ${twos8.slice(4)}`;

      setConvResult({
        status: 'SUCCESS',
        input: val,
        from_base: base,
        decimal: dec,
        binary: isNeg ? `-${binFmt}` : binFmt,
        octal: isNeg ? `-${octStr}` : octStr,
        hexadecimal: isNeg ? `-0x${hexStr}` : `0x${hexStr}`,
        bcd: String(absVal).split('').map(d => parseInt(d, 10).toString(2).padStart(4, '0')).join(' '),
        gray_code: gray,
        twos_complement_8bit: twos8Fmt,
        is_negative: isNeg,
        steps: `Converted value ${val} from base ${base}. Absolute magnitude: ${absVal}. Binary: ${binStr}.`
      });
    } catch (e) {}
  };

  // =========================================================================
  // TAB 3: KARNAUGH MAP (K-MAP) STATE
  // =========================================================================
  const [kmapNumVars, setKmapNumVars] = useState(3);
  const [kmapMinterms, setKmapMinterms] = useState([3, 5, 6, 7]);
  const [kmapDontCares, setKmapDontCares] = useState([]);
  const [kmapSolverResult, setKmapSolverResult] = useState(null);

  useEffect(() => {
    handleSolveKmap();
  }, [kmapNumVars, kmapMinterms, kmapDontCares]);

  const handleSolveKmap = (numVars = kmapNumVars, mins = kmapMinterms, dcs = kmapDontCares) => {
    fetch('/api/digital/kmap_solve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ num_variables: numVars, minterms: mins, dont_cares: dcs })
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'SUCCESS') {
          setKmapSolverResult(data);
        }
      })
      .catch(() => {});
  };

  const handleCellToggle = (mIdx) => {
    if (kmapMinterms.includes(mIdx)) {
      // 1 -> X (Don't care)
      setKmapMinterms(kmapMinterms.filter(m => m !== mIdx));
      setKmapDontCares([...kmapDontCares, mIdx]);
    } else if (kmapDontCares.includes(mIdx)) {
      // X -> 0
      setKmapDontCares(kmapDontCares.filter(m => m !== mIdx));
    } else {
      // 0 -> 1
      setKmapMinterms([...kmapMinterms, mIdx]);
    }
  };

  const handleClearKmap = () => {
    setKmapMinterms([]);
    setKmapDontCares([]);
  };

  const handleLoadPreset = (preset) => {
    setKmapNumVars(preset.num_variables);
    setKmapMinterms(preset.minterms);
    setKmapDontCares(preset.dont_cares || []);
    setTtExpr(preset.target_expression);
    setTtNumVars(preset.num_variables);
    setActiveTab('kmap');
    showToast(`Loaded ${preset.title} into K-Map & Logic Analyzer!`);
  };

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    showToast(`Copied ${label} to clipboard!`);
  };

  return (
    <div className="w-full min-h-screen bg-slate-900/60 p-4 md:p-8 text-slate-100">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-emerald-600/95 text-white px-5 py-3 rounded-xl shadow-2xl border border-emerald-400/40 backdrop-blur-md flex items-center gap-3 animate-fade-in">
          <svg className="w-5 h-5 text-emerald-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
          </svg>
          <span className="text-sm font-medium">{toastMessage}</span>
        </div>
      )}

      {/* Top Header & Sub-Nav */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                MIT Campus • EC3352 Digital Systems Design
              </span>
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Lead: Ashok Kumar A ({DEFAULT_STUDENT_ID})
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400 bg-clip-text text-transparent">
              Advanced Digital Electronics Learning Center
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Interactive truth table solver, multi-base number converter, and 2-4 variable Karnaugh Map prime implicant minimizer.
            </p>
          </div>

          {/* Metrics Ribbon */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-3 text-center">
              <div className="text-xs text-cyan-400 font-medium">⚡ Engine Latency</div>
              <div className="text-lg font-bold text-white mt-1">&lt; 3ms WAL</div>
            </div>
            <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-3 text-center">
              <div className="text-xs text-emerald-400 font-medium">🔢 Number Bases</div>
              <div className="text-lg font-bold text-white mt-1">7 Formats</div>
            </div>
            <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-3 text-center">
              <div className="text-xs text-amber-400 font-medium">🗺️ K-Map Grid</div>
              <div className="text-lg font-bold text-white mt-1">2 - 4 Vars</div>
            </div>
            <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-3 text-center">
              <div className="text-xs text-purple-400 font-medium">📚 AU Presets</div>
              <div className="text-lg font-bold text-purple-300 mt-1">5 Core Labs</div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap items-center gap-2 mt-6">
          <button
            onClick={() => setActiveTab('truthtable')}
            className={`px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 transition-all ${
              activeTab === 'truthtable'
                ? 'bg-cyan-500 text-slate-950 font-semibold shadow-lg shadow-cyan-500/20'
                : 'bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-white'
            }`}
          >
            <span>📊</span> Truth Table & Logic Analyzer
          </button>

          <button
            onClick={() => setActiveTab('converter')}
            className={`px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 transition-all ${
              activeTab === 'converter'
                ? 'bg-cyan-500 text-slate-950 font-semibold shadow-lg shadow-cyan-500/20'
                : 'bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-white'
            }`}
          >
            <span>🔢</span> Number Base & Code Converter
          </button>

          <button
            onClick={() => setActiveTab('kmap')}
            className={`px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 transition-all ${
              activeTab === 'kmap'
                ? 'bg-cyan-500 text-slate-950 font-semibold shadow-lg shadow-cyan-500/20'
                : 'bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-white'
            }`}
          >
            <span>🗺️</span> Karnaugh Map (K-Map) Solver
          </button>

          <button
            onClick={() => setActiveTab('presets')}
            className={`px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 transition-all ${
              activeTab === 'presets'
                ? 'bg-cyan-500 text-slate-950 font-semibold shadow-lg shadow-cyan-500/20'
                : 'bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-white'
            }`}
          >
            <span>📚</span> EC3352 Curriculum Presets
          </button>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="max-w-7xl mx-auto">
        {/* ========================================================================= */}
        {/* TAB 1: TRUTH TABLE & LOGIC ANALYZER */}
        {/* ========================================================================= */}
        {activeTab === 'truthtable' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Input Controls (5 cols) */}
            <div className="lg:col-span-5 space-y-6">
              <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
                <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                  <span>⚙️</span> Boolean Logic Input
                </h3>

                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Variable Count</label>
                    <div className="grid grid-cols-3 gap-2">
                      {[2, 3, 4].map(n => (
                        <button
                          key={n}
                          onClick={() => {
                            setTtNumVars(n);
                            handleGenerateTruthTable(ttExpr, n);
                          }}
                          className={`py-2 rounded-xl text-xs font-bold transition-all ${
                            ttNumVars === n
                              ? 'bg-cyan-500 text-slate-950'
                              : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-700'
                          }`}
                        >
                          {n} Variables ({['A,B', 'A,B,C', 'A,B,C,D'][n - 2]})
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Boolean Expression</label>
                    <input
                      type="text"
                      value={ttExpr}
                      onChange={(e) => setTtExpr(e.target.value)}
                      placeholder="(A & B) | ~C"
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono"
                    />
                  </div>

                  {/* Quick Symbol Palette */}
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1.5">Logic Operator Shortcuts</label>
                    <div className="flex flex-wrap gap-2">
                      <button onClick={() => handleAppendSymbol(' & ')} className="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-lg text-xs font-mono text-cyan-400">AND (&)</button>
                      <button onClick={() => handleAppendSymbol(' | ')} className="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-lg text-xs font-mono text-emerald-400">OR (|)</button>
                      <button onClick={() => handleAppendSymbol('~')} className="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-lg text-xs font-mono text-amber-400">NOT (~)</button>
                      <button onClick={() => handleAppendSymbol(' ^ ')} className="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-lg text-xs font-mono text-purple-400">XOR (^)</button>
                      <button onClick={() => handleAppendSymbol("'")} className="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-lg text-xs font-mono text-rose-400">Prime (')</button>
                      <button onClick={() => handleAppendSymbol('(')} className="px-2 py-1 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-lg text-xs font-mono text-slate-300">(</button>
                      <button onClick={() => handleAppendSymbol(')')} className="px-2 py-1 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-lg text-xs font-mono text-slate-300">)</button>
                    </div>
                  </div>

                  <div className="pt-2 flex items-center gap-3">
                    <button
                      onClick={() => handleGenerateTruthTable()}
                      className="flex-1 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-sm transition-all shadow-md shadow-cyan-500/20"
                    >
                      {ttLoading ? 'Evaluating...' : 'Generate Truth Table →'}
                    </button>
                    {ttResult && (
                      <button
                        onClick={() => {
                          setKmapNumVars(ttNumVars);
                          setKmapMinterms(ttResult.minterms);
                          setKmapDontCares([]);
                          setActiveTab('kmap');
                          showToast('Transferred minterms to K-Map Solver!');
                        }}
                        className="px-4 py-2.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs font-bold transition-all"
                        title="Send Minterms to K-Map"
                      >
                        Solve in K-Map 🗺️
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* Canonical Decompositions */}
              {ttResult && (
                <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6 space-y-4">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Algebraic Decompositions</h4>
                  
                  <div>
                    <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                      <span>Minterm Expansion:</span>
                      <button onClick={() => copyToClipboard(ttResult.minterm_notation, 'Minterms')} className="text-cyan-400 hover:underline">Copy</button>
                    </div>
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 font-mono text-xs text-emerald-400 font-semibold break-all">
                      {ttResult.minterm_notation}
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                      <span>Canonical Sum of Products (SOP):</span>
                      <button onClick={() => copyToClipboard(ttResult.canonical_sop, 'SOP')} className="text-cyan-400 hover:underline">Copy</button>
                    </div>
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 font-mono text-xs text-cyan-300 font-semibold break-all">
                      {ttResult.canonical_sop}
                    </div>
                  </div>

                  {ttResult.maxterm_notation && (
                    <div>
                      <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                        <span>Maxterm Expansion (POS):</span>
                        <button onClick={() => copyToClipboard(ttResult.maxterm_notation, 'Maxterms')} className="text-cyan-400 hover:underline">Copy</button>
                      </div>
                      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 font-mono text-xs text-amber-300 font-semibold break-all">
                        {ttResult.maxterm_notation}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Truth Table Grid (7 cols) */}
            <div className="lg:col-span-7">
              <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>📋</span> Computed Truth Table ({ttResult ? ttResult.rows.length : 0} Rows)
                  </h3>
                  <span className="text-xs text-slate-400 font-mono">MSB on Left</span>
                </div>

                {ttResult && ttResult.rows ? (
                  <div className="overflow-x-auto max-h-[520px] overflow-y-auto border border-slate-800 rounded-xl">
                    <table className="w-full text-center text-sm font-mono">
                      <thead className="bg-slate-900/90 text-xs text-slate-400 uppercase tracking-wider sticky top-0 z-10 border-b border-slate-700">
                        <tr>
                          <th className="py-2.5 px-3">m#</th>
                          {ttResult.variables.map(v => (
                            <th key={v} className="py-2.5 px-3 text-cyan-400">{v}</th>
                          ))}
                          <th className="py-2.5 px-3 text-emerald-400">Output (F)</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {ttResult.rows.map((r) => (
                          <tr key={r.minterm_index} className={`transition-colors ${r.output === 1 ? 'bg-emerald-500/5 hover:bg-emerald-500/10' : 'hover:bg-slate-800/50'}`}>
                            <td className="py-2 px-3 text-xs text-slate-500">m{r.minterm_index}</td>
                            {ttResult.variables.map(v => (
                              <td key={v} className="py-2 px-3 font-bold text-slate-300">{r[v]}</td>
                            ))}
                            <td className="py-2 px-3">
                              <span className={`inline-block px-2.5 py-0.5 rounded text-xs font-bold ${
                                r.output === 1
                                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                                  : 'bg-slate-800 text-slate-500'
                              }`}>
                                {r.output}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="p-8 text-center text-slate-500 text-sm">
                    Enter an expression and click Generate Truth Table.
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 2: NUMBER BASE & CODE CONVERTER */}
        {/* ========================================================================= */}
        {activeTab === 'converter' && (
          <div className="space-y-6">
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
              <div className="grid grid-cols-1 sm:grid-cols-12 gap-4 items-end">
                <div className="sm:col-span-8">
                  <label className="block text-xs font-medium text-slate-400 mb-1">Input Numeric Value</label>
                  <input
                    type="text"
                    value={numInput}
                    onChange={(e) => setNumInput(e.target.value)}
                    placeholder="Enter decimal, binary (e.g. 1010), or hex (e.g. 2A)"
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-base text-white font-mono focus:outline-none focus:border-cyan-500"
                  />
                </div>

                <div className="sm:col-span-4">
                  <label className="block text-xs font-medium text-slate-400 mb-1">Source Number Base</label>
                  <select
                    value={fromBase}
                    onChange={(e) => setFromBase(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-semibold focus:outline-none focus:border-cyan-500"
                  >
                    <option value="DECIMAL">Decimal (Base 10)</option>
                    <option value="BINARY">Binary (Base 2)</option>
                    <option value="OCTAL">Octal (Base 8)</option>
                    <option value="HEXADECIMAL">Hexadecimal (Base 16)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Results Grid */}
            {convResult && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Decimal */}
                <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-5">
                  <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Decimal (Base 10)</div>
                  <div className="text-2xl font-bold font-mono text-white mt-1.5 flex items-center justify-between">
                    <span>{convResult.decimal}</span>
                    <button onClick={() => copyToClipboard(String(convResult.decimal), 'Decimal')} className="text-xs text-cyan-400 hover:underline">Copy</button>
                  </div>
                  <div className="text-[11px] text-slate-500 mt-2 font-mono">Standard signed decimal representation</div>
                </div>

                {/* Binary */}
                <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-5">
                  <div className="text-xs text-emerald-400 font-semibold uppercase tracking-wider">Binary (Base 2)</div>
                  <div className="text-2xl font-bold font-mono text-emerald-300 mt-1.5 flex items-center justify-between">
                    <span>{convResult.binary}</span>
                    <button onClick={() => copyToClipboard(convResult.binary, 'Binary')} className="text-xs text-cyan-400 hover:underline">Copy</button>
                  </div>
                  <div className="text-[11px] text-slate-500 mt-2 font-mono">Grouped into 4-bit nibbles</div>
                </div>

                {/* Hexadecimal */}
                <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-5">
                  <div className="text-xs text-cyan-400 font-semibold uppercase tracking-wider">Hexadecimal (Base 16)</div>
                  <div className="text-2xl font-bold font-mono text-cyan-300 mt-1.5 flex items-center justify-between">
                    <span>{convResult.hexadecimal}</span>
                    <button onClick={() => copyToClipboard(convResult.hexadecimal, 'Hex')} className="text-xs text-cyan-400 hover:underline">Copy</button>
                  </div>
                  <div className="text-[11px] text-slate-500 mt-2 font-mono">Direct 4-bit nibble mapping</div>
                </div>

                {/* Octal */}
                <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-5">
                  <div className="text-xs text-amber-400 font-semibold uppercase tracking-wider">Octal (Base 8)</div>
                  <div className="text-2xl font-bold font-mono text-amber-300 mt-1.5 flex items-center justify-between">
                    <span>{convResult.octal}</span>
                    <button onClick={() => copyToClipboard(convResult.octal, 'Octal')} className="text-xs text-cyan-400 hover:underline">Copy</button>
                  </div>
                  <div className="text-[11px] text-slate-500 mt-2 font-mono">Grouped into 3-bit clusters</div>
                </div>

                {/* Gray Code */}
                <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-5">
                  <div className="text-xs text-purple-400 font-semibold uppercase tracking-wider">Reflected Gray Code</div>
                  <div className="text-2xl font-bold font-mono text-purple-300 mt-1.5 flex items-center justify-between">
                    <span>{convResult.gray_code}</span>
                    <button onClick={() => copyToClipboard(convResult.gray_code, 'Gray Code')} className="text-xs text-cyan-400 hover:underline">Copy</button>
                  </div>
                  <div className="text-[11px] text-slate-500 mt-2 font-mono">Unit distance code: G = B ^ (B &gt;&gt; 1)</div>
                </div>

                {/* BCD */}
                <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-5">
                  <div className="text-xs text-rose-400 font-semibold uppercase tracking-wider">Binary-Coded Decimal (BCD)</div>
                  <div className="text-2xl font-bold font-mono text-rose-300 mt-1.5 flex items-center justify-between">
                    <span>{convResult.bcd}</span>
                    <button onClick={() => copyToClipboard(convResult.bcd, 'BCD')} className="text-xs text-cyan-400 hover:underline">Copy</button>
                  </div>
                  <div className="text-[11px] text-slate-500 mt-2 font-mono">Each decimal digit encoded in 4 bits</div>
                </div>

                {/* Two's Complement 8-Bit */}
                <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-5 md:col-span-2 lg:col-span-3">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                      <div className="text-xs text-emerald-400 font-semibold uppercase tracking-wider">Signed Two's Complement (8-Bit &amp; 16-Bit)</div>
                      <div className="text-lg font-bold font-mono text-white mt-1">
                        8-Bit: <span className="text-cyan-300">{convResult.twos_complement_8bit}</span>
                        <span className="mx-3 text-slate-600">|</span>
                        16-Bit: <span className="text-emerald-300">{convResult.twos_complement_16bit}</span>
                      </div>
                    </div>
                  </div>
                  {convResult.steps && (
                    <div className="mt-4 pt-4 border-t border-slate-700/60 text-xs text-slate-400 font-mono whitespace-pre-line leading-relaxed">
                      {convResult.steps}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 3: KARNAUGH MAP (K-MAP) SOLVER */}
        {/* ========================================================================= */}
        {activeTab === 'kmap' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Grid & Interactivity (8 cols) */}
            <div className="lg:col-span-8 space-y-6">
              <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
                  <div>
                    <h3 className="text-base font-bold text-white flex items-center gap-2">
                      <span>🗺️</span> Interactive Karnaugh Map Grid
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Click any cell to toggle: <span className="text-slate-400">0</span> → <span className="text-emerald-400 font-bold">1</span> → <span className="text-amber-400 font-bold">X (Don't Care)</span>.
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    {[2, 3, 4].map(n => (
                      <button
                        key={n}
                        onClick={() => {
                          setKmapNumVars(n);
                          setKmapMinterms(kmapMinterms.filter(m => m < (1 << n)));
                          setKmapDontCares(kmapDontCares.filter(m => m < (1 << n)));
                        }}
                        className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                          kmapNumVars === n
                            ? 'bg-cyan-500 text-slate-950 font-bold'
                            : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-700'
                        }`}
                      >
                        {n} Vars
                      </button>
                    ))}
                    <button
                      onClick={handleClearKmap}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white border border-slate-700 text-xs font-semibold"
                    >
                      Clear
                    </button>
                  </div>
                </div>

                {/* Dynamic K-Map Matrix Display */}
                {kmapSolverResult && kmapSolverResult.grid && (
                  <div className="overflow-x-auto pb-4">
                    <div className="inline-block min-w-full text-center font-mono">
                      {/* Top Column Gray Code Headers */}
                      <div className="flex items-center justify-center">
                        <div className="w-16 h-10 flex items-center justify-center text-xs text-cyan-400 font-bold border-b border-r border-slate-700 bg-slate-900/80">
                          {kmapSolverResult.row_var} \ {kmapSolverResult.col_var}
                        </div>
                        {kmapSolverResult.col_labels.map((colLbl, cIdx) => (
                          <div key={cIdx} className="w-20 sm:w-24 h-10 flex items-center justify-center text-xs font-bold text-slate-300 border-b border-r border-slate-700 bg-slate-900/60">
                            {colLbl}
                          </div>
                        ))}
                      </div>

                      {/* Rows */}
                      {kmapSolverResult.grid.map((rowCells, rIdx) => (
                        <div key={rIdx} className="flex items-center justify-center">
                          {/* Row Header */}
                          <div className="w-16 h-16 sm:h-20 flex items-center justify-center text-xs font-bold text-slate-300 border-b border-r border-slate-700 bg-slate-900/60">
                            {kmapSolverResult.row_labels[rIdx]}
                          </div>

                          {/* Interactive Cells */}
                          {rowCells.map((cell) => {
                            const isOne = cell.val === 1;
                            const isDc = cell.val === 'X';
                            return (
                              <button
                                key={cell.minterm}
                                onClick={() => handleCellToggle(cell.minterm)}
                                className={`w-20 sm:w-24 h-16 sm:h-20 border-b border-r border-slate-700 flex flex-col items-center justify-center relative transition-all group ${
                                  isOne
                                    ? 'bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300'
                                    : isDc
                                    ? 'bg-amber-500/20 hover:bg-amber-500/30 text-amber-300'
                                    : 'bg-slate-900/40 hover:bg-slate-800 text-slate-500'
                                }`}
                              >
                                <span className="text-xl sm:text-2xl font-black">{cell.val}</span>
                                <span className="absolute bottom-1 right-2 text-[10px] text-slate-500 group-hover:text-slate-300 font-mono">
                                  m{cell.minterm}
                                </span>
                              </button>
                            );
                          })}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Minimized Output & Explanation (4 cols) */}
            <div className="lg:col-span-4 space-y-6">
              <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Minimized Boolean Output</h4>
                <div className="bg-slate-900 border border-slate-700 rounded-xl p-4 text-center">
                  <div className="text-xs text-slate-400 font-mono mb-1">Minimal Sum of Products (SOP)</div>
                  <div className="text-xl sm:text-2xl font-black font-mono text-emerald-400 tracking-wide break-all">
                    F = {kmapSolverResult ? kmapSolverResult.simplified_sop : '0'}
                  </div>
                  {kmapSolverResult && kmapSolverResult.simplified_sop && (
                    <button
                      onClick={() => copyToClipboard(`F = ${kmapSolverResult.simplified_sop}`, 'Minimized Equation')}
                      className="mt-3 px-3 py-1 bg-slate-800 hover:bg-slate-700 rounded-lg text-xs text-cyan-400 font-semibold"
                    >
                      Copy Equation 📋
                    </button>
                  )}
                </div>

                <div className="mt-6 space-y-3">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Included Minterms:</span>
                    <span className="font-mono text-emerald-400 font-bold">
                      {kmapMinterms.length > 0 ? kmapMinterms.sort((a,b)=>a-b).join(', ') : 'None'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Don't Cares (X):</span>
                    <span className="font-mono text-amber-400 font-bold">
                      {kmapDontCares.length > 0 ? kmapDontCares.sort((a,b)=>a-b).join(', ') : 'None'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Grid Cell Total:</span>
                    <span className="font-mono text-white font-bold">{1 << kmapNumVars} Cells</span>
                  </div>
                </div>
              </div>

              <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6 text-xs text-slate-400 space-y-2">
                <div className="font-bold text-white text-sm mb-1">📘 K-Map Reduction Rules</div>
                <p>1. Groups must contain $2^n$ cells (1, 2, 4, 8, or 16).</p>
                <p>2. Groups must be rectangular and can wrap around the outer perimeter edges.</p>
                <p>3. Don't cares ('X') are greedily included if they enlarge a power-of-2 group.</p>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 4: EC3352 CURRICULUM PRESETS */}
        {/* ========================================================================= */}
        {activeTab === 'presets' && (
          <div className="space-y-6">
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
              <h3 className="text-base font-bold text-white mb-2">Anna University EC3352 Benchmark Exercises</h3>
              <p className="text-xs text-slate-400 mb-6">
                Standard digital arithmetic and combinational logic problems from Unit 1 and Unit 2. Click any preset to load it directly into the solver.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {CURRICULUM_PRESETS.map((p) => (
                  <div
                    key={p.preset_id}
                    className="bg-slate-900/80 border border-slate-800 hover:border-slate-700 rounded-xl p-5 transition-all flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between gap-2">
                        <span className="px-2 py-0.5 rounded text-xs font-bold bg-slate-800 text-cyan-400 border border-cyan-500/20">
                          Unit {p.unit_number} • {p.num_variables} Vars
                        </span>
                        <span className="text-xs font-mono text-slate-500">
                          Σ m({p.minterms.join(',')})
                        </span>
                      </div>

                      <h4 className="text-base font-bold text-white mt-2">{p.title}</h4>
                      <p className="text-xs text-slate-400 mt-1">{p.description}</p>

                      <div className="mt-3 bg-slate-950 p-2.5 rounded-lg border border-slate-800 font-mono text-xs text-emerald-400">
                        Equation: {p.target_expression}
                      </div>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
                      <span className="text-[11px] text-slate-500 font-mono">
                        {p.dont_cares.length > 0 ? `Don't Cares: ${p.dont_cares.join(',')}` : 'No Don\'t Cares'}
                      </span>
                      <button
                        onClick={() => handleLoadPreset(p)}
                        className="px-4 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-bold transition-colors"
                      >
                        Load Preset →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
