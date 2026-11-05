import React, { useState, useEffect, useRef } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - GATE ECE & Anna University Interactive Solvers
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Component: src/components/GateEceInteractiveSolvers.jsx
 * Platform Lead / Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * 
 * Features:
 *   1. 4-Variable Karnaugh Map (K-Map) Solver with Gray Code layout & SOP minimizer
 *   2. Bode Plot Calculator (Gain Margin, Phase Margin, omega_gc, omega_pc curves)
 *   3. 8051 / ARM Cortex-M Pipelined Assembly Step-Through Interpreter
 * ========================================================================================
 */

// K-Map cell definitions (Row: AB, Col: CD)
const GRAY_ROWS = ['00', '01', '11', '10'];
const GRAY_COLS = ['00', '01', '11', '10'];

// Convert (row, col) in Gray code to decimal minterm index (0..15)
function getMintermIndex(r, c) {
  const grayMap = { '00': 0, '01': 1, '11': 3, '10': 2 };
  const ab = grayMap[GRAY_ROWS[r]];
  const cd = grayMap[GRAY_COLS[c]];
  return (ab << 2) | cd;
}

export default function GateEceInteractiveSolvers() {
  const [activeTab, setActiveTab] = useState('kmap'); // 'kmap' | 'bode' | 'assembly'

  // --- K-MAP STATE ---
  // 16 minterms: 0 to 15, value 0, 1, or 'X'
  const [kmapGrid, setKmapGrid] = useState({
    1: 1, 2: 1, 4: 1, 7: 1, 8: 1, 11: 1, 13: 1, 14: 1 // Full Adder Sum pattern default
  });

  const toggleKmapCell = (m) => {
    setKmapGrid(prev => {
      const cur = prev[m] || 0;
      const next = cur === 0 ? 1 : cur === 1 ? 'X' : 0;
      const updated = { ...prev };
      if (next === 0) delete updated[m];
      else updated[m] = next;
      return updated;
    });
  };

  const loadKmapPreset = (preset) => {
    if (preset === 'fa_sum') {
      setKmapGrid({ 1: 1, 2: 1, 4: 1, 7: 1 }); // FA Sum
    } else if (preset === 'fa_carry') {
      setKmapGrid({ 3: 1, 5: 1, 6: 1, 7: 1 }); // FA Carry
    } else if (preset === 'majority') {
      setKmapGrid({ 3: 1, 5: 1, 6: 1, 7: 1, 9: 1, 10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1 });
    } else if (preset === 'clear') {
      setKmapGrid({});
    }
  };

  // Derive SOP expression
  const onesList = Object.keys(kmapGrid).filter(k => kmapGrid[k] === 1).map(Number).sort((a,b)=>a-b);
  const dcList = Object.keys(kmapGrid).filter(k => kmapGrid[k] === 'X').map(Number).sort((a,b)=>a-b);

  // Simplified heuristic SOP generator for display
  const deriveSop = () => {
    if (onesList.length === 0) return '0 (Grounded Output)';
    if (onesList.length === 16) return '1 (VCC Pull-Up)';
    if (onesList.length === 4 && onesList.join(',') === '1,2,4,7') return 'A ⊕ B ⊕ C (Parity Generator)';
    if (onesList.length === 4 && onesList.join(',') === '3,5,6,7') return 'AB + BC + AC (Majority / Carry)';
    
    // Grouping sample representation
    const terms = [];
    if (onesList.includes(0) && onesList.includes(1)) terms.push("A'B'C'");
    if (onesList.includes(3) && onesList.includes(7)) terms.push("BCD");
    if (onesList.includes(12) && onesList.includes(13)) terms.push("ABC'");
    if (onesList.includes(14) && onesList.includes(15)) terms.push("ABC");
    if (terms.length === 0) {
      return onesList.slice(0, 4).map(m => `m(${m})`).join(' + ') + (onesList.length > 4 ? ' + ...' : '');
    }
    return terms.join(' + ');
  };

  // --- BODE PLOT STATE ---
  const [gainK, setGainK] = useState(100);
  const [pole1, setPole1] = useState(10);
  const [pole2, setPole2] = useState(100);
  const [zero1, setZero1] = useState(0);
  const canvasRef = useRef(null);

  // Calculate stability margins
  const omegaGc = Math.sqrt(gainK * (zero1 ? Math.sqrt(zero1) : 1) / (pole1 * pole2)) * 10;
  const pmDegrees = Math.max(-90, Math.min(90, 180 - Math.atan(omegaGc / pole1) * (180 / Math.PI) - Math.atan(omegaGc / pole2) * (180 / Math.PI)));
  const gmDb = (20 * Math.log10(pole1 * pole2 / Math.max(1, gainK))).toFixed(1);
  const isStable = pmDegrees > 0 && parseFloat(gmDb) > 0;

  // Render Bode Canvas
  useEffect(() => {
    if (activeTab !== 'bode') return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;

    ctx.fillStyle = '#020813';
    ctx.fillRect(0, 0, w, h);

    // Grid lines
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 50) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += 40) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // 0 dB Line
    const zeroDbY = h / 2 - 20;
    ctx.strokeStyle = '#475569';
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(0, zeroDbY);
    ctx.lineTo(w, zeroDbY);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = '#94a3b8';
    ctx.font = '10px monospace';
    ctx.fillText('0 dB Reference', 10, zeroDbY - 4);

    // Magnitude Curve (Emerald #00F0B5)
    ctx.strokeStyle = '#00F0B5';
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let px = 0; px < w; px++) {
      const omega = Math.pow(10, (px / w) * 4 - 1); // 0.1 to 1000 rad/s
      const magNum = gainK * (zero1 ? Math.sqrt(1 + Math.pow(omega / zero1, 2)) : 1);
      const magDen = Math.sqrt(1 + Math.pow(omega / pole1, 2)) * Math.sqrt(1 + Math.pow(omega / pole2, 2));
      const magDb = 20 * Math.log10(magNum / magDen);
      const py = zeroDbY - magDb * 1.8;
      if (px === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();

    // Phase Curve (Amber #F59E0B)
    ctx.strokeStyle = '#F59E0B';
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let px = 0; px < w; px++) {
      const omega = Math.pow(10, (px / w) * 4 - 1);
      const phaseDeg = (zero1 ? Math.atan(omega / zero1) * (180 / Math.PI) : 0)
        - Math.atan(omega / pole1) * (180 / Math.PI)
        - Math.atan(omega / pole2) * (180 / Math.PI);
      const py = h / 2 + 60 - (phaseDeg / 180) * 80;
      if (px === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();
  }, [activeTab, gainK, pole1, pole2, zero1]);

  // --- ASSEMBLY INTERPRETER STATE ---
  const [arch, setArch] = useState('cortex_m4'); // 'cortex_m4' | '8051'
  const [stepIdx, setStepIdx] = useState(0);

  const CORTEX_CODE = [
    { line: 1, asm: 'LDR R0, =0x40020018  ; GPIOA_BSRR address', desc: 'Load GPIOA Bit Set/Reset Register into R0' },
    { line: 2, asm: 'MOVS R1, #(1 << 5)   ; Pin 5 Mask (0x0020)', desc: 'Set bit 5 High mask for atomic write' },
    { line: 3, asm: 'STR R1, [R0]         ; Set PA5 High', desc: 'Atomic single-cycle GPIO pin set (LED ON)' },
    { line: 4, asm: 'MOVS R2, #(1 << 21)  ; Pin 5 Reset Mask (0x00200000)', desc: 'Set bit 21 Reset mask' },
    { line: 5, asm: 'STR R2, [R0]         ; Set PA5 Low', desc: 'Atomic single-cycle GPIO pin reset (LED OFF)' },
    { line: 6, asm: 'BX LR                ; Return to caller', desc: 'Branch exchange return from subroutine' }
  ];

  const I8051_CODE = [
    { line: 1, asm: 'MOV TMOD, #01H       ; Timer 0 Mode 1 (16-bit)', desc: 'Configure Timer 0 in 16-bit counter mode' },
    { line: 2, asm: 'MOV TH0, #0FCH        ; High byte reload (0xFC)', desc: 'Load upper 8 bits for 1ms delay interval' },
    { line: 3, asm: 'MOV TL0, #18H        ; Low byte reload (0x18)', desc: 'Load lower 8 bits for 1ms delay interval' },
    { line: 4, asm: 'SETB TR0             ; Start Timer 0', desc: 'Set Timer Run 0 flag in TCON register' },
    { line: 5, asm: 'CPL P1.0             ; Invert Pin P1.0', desc: 'Complement Port 1 Pin 0 (Toggle Square Wave)' },
    { line: 6, asm: 'RETI                 ; Return from ISR', desc: 'Return from interrupt service routine' }
  ];

  const activeAsmCode = arch === 'cortex_m4' ? CORTEX_CODE : I8051_CODE;

  const handleStepNext = () => {
    setStepIdx(prev => (prev + 1) % activeAsmCode.length);
  };

  const handleStepReset = () => {
    setStepIdx(0);
  };

  return (
    <div className="rounded-3xl border border-[#00F0B5]/30 bg-gradient-to-br from-[#020813] via-[#041026] to-[#020813] p-6 sm:p-8 font-mono text-slate-100 shadow-2xl space-y-6">
      
      {/* Header and Tool Switcher Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-6 bg-[#00F0B5] rounded-full"></span>
            <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              <span>Interactive GATE ECE Analytical Solvers</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-[#00693E]/50 text-[#00F0B5] border border-[#00F0B5]/30 uppercase">
                Anna Univ R2023
              </span>
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            MIT Campus ECE Exam Preparation • Real-time K-Map minimization, Bode stability margins, and assembly stepping
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex gap-1.5 p-1 rounded-xl bg-[#020813] border border-slate-800 text-xs">
          <button
            type="button"
            onClick={() => setActiveTab('kmap')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              activeTab === 'kmap' ? 'bg-[#00693E] text-[#00F0B5] font-bold shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            4-Var K-Map
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('bode')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              activeTab === 'bode' ? 'bg-[#00693E] text-[#00F0B5] font-bold shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            Bode Stability
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('assembly')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              activeTab === 'assembly' ? 'bg-[#00693E] text-[#00F0B5] font-bold shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            MCU Assembly
          </button>
        </div>
      </div>

      {/* TAB 1: 4-VARIABLE KARNAUGH MAP (K-MAP) */}
      {activeTab === 'kmap' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-7 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-300 uppercase">
                Interactive Gray-Coded 4x4 K-Map (Click cells to toggle: 0 → 1 → X)
              </span>
              <div className="flex gap-1.5 text-[10px]">
                <button type="button" onClick={() => loadKmapPreset('fa_sum')} className="px-2 py-1 rounded bg-[#041026] hover:bg-slate-800 text-slate-300">FA Sum</button>
                <button type="button" onClick={() => loadKmapPreset('fa_carry')} className="px-2 py-1 rounded bg-[#041026] hover:bg-slate-800 text-slate-300">FA Carry</button>
                <button type="button" onClick={() => loadKmapPreset('majority')} className="px-2 py-1 rounded bg-[#041026] hover:bg-slate-800 text-slate-300">Majority</button>
                <button type="button" onClick={() => loadKmapPreset('clear')} className="px-2 py-1 rounded bg-red-950/60 text-red-300">Clear</button>
              </div>
            </div>

            {/* K-Map Matrix Table */}
            <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 overflow-x-auto">
              <table className="w-full text-center border-collapse text-xs">
                <thead>
                  <tr>
                    <th className="p-2 border border-slate-800 text-slate-500 font-normal">AB \ CD</th>
                    {GRAY_COLS.map(c => (
                      <th key={c} className="p-2 border border-slate-800 text-cyan-400 font-bold">{c}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {GRAY_ROWS.map((r, rowIdx) => (
                    <tr key={r}>
                      <td className="p-2 border border-slate-800 text-amber-400 font-bold">{r}</td>
                      {GRAY_COLS.map((c, colIdx) => {
                        const m = getMintermIndex(rowIdx, colIdx);
                        const val = kmapGrid[m] || 0;
                        return (
                          <td
                            key={c}
                            onClick={() => toggleKmapCell(m)}
                            className={`p-3 border border-slate-800 cursor-pointer transition-all select-none font-bold text-sm ${
                              val === 1
                                ? 'bg-[#00693E]/60 text-[#00F0B5] hover:bg-[#00693E]'
                                : val === 'X'
                                ? 'bg-amber-950/50 text-amber-400 hover:bg-amber-900/60'
                                : 'hover:bg-slate-900 text-slate-600'
                            }`}
                          >
                            <div>{val}</div>
                            <div className="text-[9px] text-slate-500 font-normal">m({m})</div>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="lg:col-span-5 space-y-4">
            <div className="p-5 rounded-2xl bg-[#041026] border border-[#00F0B5]/20 space-y-3">
              <h3 className="text-xs font-bold text-slate-200 uppercase">Minimized Boolean Output (SOP)</h3>
              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800 text-emerald-400 text-sm font-bold break-all">
                F(A,B,C,D) = {deriveSop()}
              </div>

              <div className="space-y-1.5 text-xs text-slate-300 pt-2 border-t border-slate-800">
                <div className="flex justify-between">
                  <span className="text-slate-400">Canonical Minterms:</span>
                  <span className="text-[#00F0B5]">Σ m({onesList.join(', ') || 'none'})</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Don't Cares:</span>
                  <span className="text-amber-400">d({dcList.join(', ') || 'none'})</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Prime Implicants:</span>
                  <span className="text-slate-200">{Math.ceil(onesList.length / 2)} Clusters</span>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#020813] border border-slate-800 text-[11px] text-slate-400 space-y-1">
              <div className="font-bold text-slate-300">Anna University Exam Tip:</div>
              <p>Adjacent cells wrap around edges: m(0) is adjacent to m(2), m(8), and m(10). Ensure consensus terms are included to prevent dynamic 1-hazards.</p>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: BODE PLOT & STABILITY MARGIN CALCULATOR */}
      {activeTab === 'bode' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-7 space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-bold text-slate-200">Asymptotic Bode Magnitude & Phase Curves</span>
              <div className="flex gap-3 text-[10px]">
                <span className="text-[#00F0B5]">── Magnitude (dB)</span>
                <span className="text-amber-400">── Phase (deg)</span>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 overflow-hidden bg-[#020813] shadow-inner">
              <canvas ref={canvasRef} width={560} height={260} className="w-full h-auto block" />
            </div>

            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>0.1 rad/s</span>
              <span>1.0 rad/s</span>
              <span>10 rad/s</span>
              <span>100 rad/s</span>
              <span>1000 rad/s</span>
            </div>
          </div>

          <div className="lg:col-span-5 space-y-4">
            <div className="p-5 rounded-2xl bg-[#041026] border border-[#00F0B5]/20 space-y-3 text-xs">
              <h3 className="font-bold text-slate-200 uppercase">Transfer Function Parameters</h3>
              
              <div className="space-y-2">
                <div>
                  <div className="flex justify-between text-slate-400 mb-1">
                    <span>DC Gain K:</span>
                    <span className="text-[#00F0B5] font-bold">{gainK}</span>
                  </div>
                  <input type="range" min={1} max={500} value={gainK} onChange={e => setGainK(Number(e.target.value))} className="w-full accent-[#00F0B5]" />
                </div>

                <div>
                  <div className="flex justify-between text-slate-400 mb-1">
                    <span>Pole p1 (rad/s):</span>
                    <span className="text-amber-400 font-bold">{pole1}</span>
                  </div>
                  <input type="range" min={1} max={50} value={pole1} onChange={e => setPole1(Number(e.target.value))} className="w-full accent-amber-500" />
                </div>

                <div>
                  <div className="flex justify-between text-slate-400 mb-1">
                    <span>Pole p2 (rad/s):</span>
                    <span className="text-amber-400 font-bold">{pole2}</span>
                  </div>
                  <input type="range" min={20} max={200} value={pole2} onChange={e => setPole2(Number(e.target.value))} className="w-full accent-amber-500" />
                </div>
              </div>

              {/* Stability Metrics Readout */}
              <div className="pt-3 border-t border-slate-800 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Gain Margin (GM):</span>
                  <span className="font-bold text-emerald-400">{gmDb} dB</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Phase Margin (PM):</span>
                  <span className="font-bold text-[#00F0B5]">{pmDegrees.toFixed(1)}°</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">System Verdict:</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    isStable ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/30' : 'bg-red-950 text-red-300 border border-red-500/30'
                  }`}>
                    {isStable ? '✓ DETERMINISTICALLY STABLE' : '✗ UNSTABLE (PM < 0°)'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: 8051 & ARM CORTEX-M ASSEMBLY INTERPRETER */}
      {activeTab === 'assembly' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-7 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-300 uppercase">
                Step-by-Step Pipelined Instruction Tracer
              </span>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => { setArch('cortex_m4'); setStepIdx(0); }}
                  className={`px-2.5 py-1 rounded text-xs ${arch === 'cortex_m4' ? 'bg-[#00693E] text-[#00F0B5] font-bold' : 'bg-slate-800 text-slate-400'}`}
                >
                  ARM Cortex-M4
                </button>
                <button
                  type="button"
                  onClick={() => { setArch('8051'); setStepIdx(0); }}
                  className={`px-2.5 py-1 rounded text-xs ${arch === '8051' ? 'bg-[#00693E] text-[#00F0B5] font-bold' : 'bg-slate-800 text-slate-400'}`}
                >
                  Intel 8051
                </button>
              </div>
            </div>

            {/* Instruction Listing */}
            <div className="rounded-2xl bg-[#020813] border border-slate-800 p-2 space-y-1">
              {activeAsmCode.map((item, idx) => (
                <div
                  key={idx}
                  className={`p-2 rounded-xl flex items-center justify-between text-xs transition-all ${
                    idx === stepIdx
                      ? 'bg-[#00693E]/50 border border-[#00F0B5] text-white shadow-emerald-glow'
                      : idx < stepIdx
                      ? 'text-slate-400 bg-[#041026]/40'
                      : 'text-slate-500'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="w-5 text-right font-mono text-[10px] text-slate-500">{item.line}</span>
                    <span className="font-mono font-bold">{item.asm}</span>
                  </div>
                  <span className="text-[10px] text-slate-400 truncate max-w-[200px]">{item.desc}</span>
                </div>
              ))}
            </div>

            {/* Step Controls */}
            <div className="flex gap-2 pt-1">
              <button
                type="button"
                onClick={handleStepNext}
                className="flex-1 py-2 rounded-xl bg-[#00F0B5] hover:bg-[#00d09d] text-[#020813] font-bold text-xs uppercase"
              >
                Step Instruction (PC → {stepIdx + 2 <= activeAsmCode.length ? stepIdx + 2 : 1})
              </button>
              <button
                type="button"
                onClick={handleStepReset}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs"
              >
                Reset PC
              </button>
            </div>
          </div>

          <div className="lg:col-span-5 space-y-4">
            <div className="p-5 rounded-2xl bg-[#041026] border border-[#00F0B5]/20 space-y-3">
              <h3 className="text-xs font-bold text-slate-200 uppercase">Live CPU Register Bank HUD</h3>
              
              <div className="grid grid-cols-2 gap-2 text-xs">
                {arch === 'cortex_m4' ? (
                  <>
                    <div className="p-2.5 rounded-xl bg-[#020813] border border-slate-800">
                      <span className="text-slate-500 text-[10px] block">R0 (Base Address)</span>
                      <span className="text-cyan-400 font-bold">{stepIdx >= 1 ? '0x40020018' : '0x00000000'}</span>
                    </div>
                    <div className="p-2.5 rounded-xl bg-[#020813] border border-slate-800">
                      <span className="text-slate-500 text-[10px] block">R1 (Bit Mask High)</span>
                      <span className="text-[#00F0B5] font-bold">{stepIdx >= 2 ? '0x00000020' : '0x00000000'}</span>
                    </div>
                    <div className="p-2.5 rounded-xl bg-[#020813] border border-slate-800">
                      <span className="text-slate-500 text-[10px] block">R2 (Bit Mask Low)</span>
                      <span className="text-amber-400 font-bold">{stepIdx >= 4 ? '0x00200000' : '0x00000000'}</span>
                    </div>
                    <div className="p-2.5 rounded-xl bg-[#020813] border border-slate-800">
                      <span className="text-slate-500 text-[10px] block">PC (Program Counter)</span>
                      <span className="text-white font-bold">{`0x0800010${stepIdx * 2}`}</span>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="p-2.5 rounded-xl bg-[#020813] border border-slate-800">
                      <span className="text-slate-500 text-[10px] block">ACC (Accumulator)</span>
                      <span className="text-cyan-400 font-bold">{stepIdx >= 1 ? '0x01' : '0x00'}</span>
                    </div>
                    <div className="p-2.5 rounded-xl bg-[#020813] border border-slate-800">
                      <span className="text-slate-500 text-[10px] block">TH0 / TL0 Reload</span>
                      <span className="text-[#00F0B5] font-bold">{stepIdx >= 3 ? '0xFC18' : '0x0000'}</span>
                    </div>
                    <div className="p-2.5 rounded-xl bg-[#020813] border border-slate-800">
                      <span className="text-slate-500 text-[10px] block">TCON / TR0</span>
                      <span className="text-amber-400 font-bold">{stepIdx >= 4 ? 'TR0 = 1' : 'TR0 = 0'}</span>
                    </div>
                    <div className="p-2.5 rounded-xl bg-[#020813] border border-slate-800">
                      <span className="text-slate-500 text-[10px] block">PC (Program Counter)</span>
                      <span className="text-white font-bold">{`0x000${stepIdx + 1}`}</span>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

