import React, { useState, useMemo } from 'react';

// =============================================================================
// APPLET 1: DISCRETE CONVOLUTION STEP-BY-STEP ANIMATOR
// =============================================================================

function DiscreteConvolutionApplet() {
  const [signalX, setSignalX] = useState('rect');
  const [signalH, setSignalH] = useState('exp');
  const [shiftN, setShiftN] = useState(3);

  // Discrete signals defined for k in [-2 .. 8]
  const kRange = useMemo(() => Array.from({ length: 13 }, (_, i) => i - 3), []);

  const getSignalValue = (type, k) => {
    switch (type) {
      case 'rect':
        return (k >= 0 && k <= 3) ? 1.0 : 0.0;
      case 'exp':
        return (k >= 0 && k <= 4) ? Math.pow(0.7, k) : 0.0;
      case 'impulse':
        return (k === 0 || k === 2) ? 1.0 : 0.0;
      case 'ramp':
        return (k >= 0 && k <= 3) ? (k + 1) * 0.3 : 0.0;
      default:
        return 0.0;
    }
  };

  // Compute x[k], h[k], h[n-k], and product x[k]*h[n-k]
  const data = useMemo(() => {
    return kRange.map(k => {
      const xVal = getSignalValue(signalX, k);
      const hFlippedShifted = getSignalValue(signalH, shiftN - k);
      const product = xVal * hFlippedShifted;
      return { k, xVal, hFlippedShifted, product };
    });
  }, [signalX, signalH, shiftN, kRange]);

  // Compute full output y[n] for n in [-3 .. 9]
  const nRange = useMemo(() => Array.from({ length: 15 }, (_, i) => i - 4), []);
  const yValues = useMemo(() => {
    return nRange.map(n => {
      let sum = 0;
      for (let k = -10; k <= 10; k++) {
        sum += getSignalValue(signalX, k) * getSignalValue(signalH, n - k);
      }
      return { n, val: sum };
    });
  }, [signalX, signalH, nRange]);

  const currentYSum = useMemo(() => {
    return data.reduce((acc, curr) => acc + curr.product, 0);
  }, [data]);

  return (
    <div className="space-y-6">
      {/* Control bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/80 border border-slate-800">
        <div className="flex flex-wrap items-center gap-4">
          <div>
            <label className="text-[11px] font-bold text-slate-400 block mb-1">Signal x[k]:</label>
            <select
              value={signalX}
              onChange={(e) => setSignalX(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-sky-400 font-semibold focus:outline-none"
            >
              <option value="rect">Rectangular Pulse [0..3]</option>
              <option value="exp">Exponential Decay (0.7^k)</option>
              <option value="impulse">Dual Impulse (δ[k] + δ[k-2])</option>
              <option value="ramp">Linear Ramp [0..3]</option>
            </select>
          </div>

          <div>
            <label className="text-[11px] font-bold text-slate-400 block mb-1">Impulse Response h[k]:</label>
            <select
              value={signalH}
              onChange={(e) => setSignalH(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-emerald-400 font-semibold focus:outline-none"
            >
              <option value="exp">Exponential Decay (0.7^k)</option>
              <option value="rect">Rectangular Pulse [0..3]</option>
              <option value="impulse">Single Impulse δ[k]</option>
              <option value="ramp">Linear Ramp [0..3]</option>
            </select>
          </div>
        </div>

        {/* Shift Slider */}
        <div className="flex items-center gap-3">
          <label className="text-xs font-bold text-amber-400">Shift Index (n):</label>
          <input
            type="range"
            min={-3}
            max={8}
            step={1}
            value={shiftN}
            onChange={(e) => setShiftN(parseInt(e.target.value, 10))}
            className="w-32 accent-amber-500 cursor-pointer"
          />
          <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono text-xs font-bold border border-amber-500/40">
            n = {shiftN}
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => setShiftN(prev => Math.max(-3, prev - 1))}
              className="p-1 px-2 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 text-xs font-mono"
            >
              -1
            </button>
            <button
              onClick={() => setShiftN(prev => Math.min(8, prev + 1))}
              className="p-1 px-2 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 text-xs font-mono"
            >
              +1
            </button>
          </div>
        </div>
      </div>

      {/* SVG Plots Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Plot A: x[k] and Folded/Shifted h[n-k] */}
        <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-xs font-bold text-slate-300 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-sky-400"></span>
              Input x[k] &amp;
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 ml-1"></span>
              Folded Kernel h[n - k]
            </h4>
            <span className="text-[10px] font-mono text-slate-500">Overlay for n = {shiftN}</span>
          </div>
          <svg viewBox="0 0 440 180" className="w-full h-44 bg-slate-900/60 rounded-lg">
            <line x1="20" y1="130" x2="420" y2="130" stroke="#334155" strokeWidth="1" />
            <line x1="120" y1="20" x2="120" y2="160" stroke="#475569" strokeWidth="1" strokeDasharray="2 2" />
            <text x="123" y="28" fill="#64748b" fontSize="9" fontFamily="monospace">k=0</text>

            {data.map(({ k, xVal, hFlippedShifted }) => {
              const xPos = 120 + k * 26;
              const yBase = 130;
              const yValX = yBase - xVal * 70;
              const yValH = yBase - hFlippedShifted * 70;

              return (
                <g key={k}>
                  {xVal > 0 && (
                    <>
                      <line x1={xPos - 2} y1={yBase} x2={xPos - 2} y2={yValX} stroke="#38bdf8" strokeWidth="2" />
                      <circle cx={xPos - 2} cy={yValX} r="3" fill="#38bdf8" />
                    </>
                  )}
                  {hFlippedShifted > 0 && (
                    <>
                      <line x1={xPos + 2} y1={yBase} x2={xPos + 2} y2={yValH} stroke="#34d399" strokeWidth="2" strokeDasharray="3 2" />
                      <circle cx={xPos + 2} cy={yValH} r="3" fill="#34d399" />
                    </>
                  )}
                  <text x={xPos} y="148" fill="#64748b" fontSize="8" textAnchor="middle" fontFamily="monospace">
                    {k}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Plot B: Overlapping Product x[k] * h[n-k] */}
        <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-xs font-bold text-amber-400 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
              Multiplication Product: x[k] · h[n - k]
            </h4>
            <span className="text-[11px] font-mono font-bold text-amber-300">
              Sum = {currentYSum.toFixed(3)}
            </span>
          </div>
          <svg viewBox="0 0 440 180" className="w-full h-44 bg-slate-900/60 rounded-lg">
            <line x1="20" y1="130" x2="420" y2="130" stroke="#334155" strokeWidth="1" />
            <line x1="120" y1="20" x2="120" y2="160" stroke="#475569" strokeWidth="1" strokeDasharray="2 2" />
            <text x="123" y="28" fill="#64748b" fontSize="9" fontFamily="monospace">k=0</text>

            {data.map(({ k, product }) => {
              const xPos = 120 + k * 26;
              const yBase = 130;
              const yVal = yBase - product * 70;

              return (
                <g key={k}>
                  {product > 0.001 ? (
                    <>
                      <line x1={xPos} y1={yBase} x2={xPos} y2={yVal} stroke="#fbbf24" strokeWidth="3" />
                      <circle cx={xPos} cy={yVal} r="3.5" fill="#f59e0b" />
                      <text x={xPos} y={yVal - 5} fill="#fbbf24" fontSize="8" textAnchor="middle" fontFamily="monospace">
                        {product.toFixed(2)}
                      </text>
                    </>
                  ) : (
                    <circle cx={xPos} cy={yBase} r="2" fill="#475569" />
                  )}
                  <text x={xPos} y="148" fill="#64748b" fontSize="8" textAnchor="middle" fontFamily="monospace">
                    {k}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
      </div>

      {/* Plot C: Resulting Convolution Sum Output y[n] */}
      <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-xs font-bold text-purple-300 flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-400"></span>
            Accumulated Convolution Sequence: y[n] = ∑ x[k] h[n - k]
          </h4>
          <span className="text-xs font-mono text-purple-400 font-bold">
            Current y[{shiftN}] = {currentYSum.toFixed(3)}
          </span>
        </div>
        <svg viewBox="0 0 880 160" className="w-full h-40 bg-slate-900/60 rounded-lg">
          <line x1="30" y1="120" x2="850" y2="120" stroke="#334155" strokeWidth="1" />
          <line x1="260" y1="15" x2="260" y2="145" stroke="#475569" strokeWidth="1" strokeDasharray="2 2" />
          <text x="265" y="24" fill="#64748b" fontSize="10" fontFamily="monospace">n=0</text>

          {yValues.map(({ n, val }) => {
            const xPos = 260 + n * 40;
            const yBase = 120;
            const yHeight = Math.min(95, val * 35);
            const isCurrent = (n === shiftN);

            return (
              <g key={n}>
                {val > 0.001 ? (
                  <>
                    <line
                      x1={xPos}
                      y1={yBase}
                      x2={xPos}
                      y2={yBase - yHeight}
                      stroke={isCurrent ? "#c084fc" : "#818cf8"}
                      strokeWidth={isCurrent ? "4" : "2"}
                    />
                    <circle
                      cx={xPos}
                      cy={yBase - yHeight}
                      r={isCurrent ? "5" : "3.5"}
                      fill={isCurrent ? "#d8b4fe" : "#a855f7"}
                    />
                    <text
                      x={xPos}
                      y={yBase - yHeight - 6}
                      fill={isCurrent ? "#f3e8ff" : "#94a3b8"}
                      fontSize={isCurrent ? "11" : "9"}
                      fontWeight={isCurrent ? "bold" : "normal"}
                      textAnchor="middle"
                      fontFamily="monospace"
                    >
                      {val.toFixed(2)}
                    </text>
                  </>
                ) : (
                  <circle cx={xPos} cy={yBase} r="2" fill="#475569" />
                )}
                <text
                  x={xPos}
                  y="138"
                  fill={isCurrent ? "#c084fc" : "#64748b"}
                  fontWeight={isCurrent ? "bold" : "normal"}
                  fontSize="10"
                  textAnchor="middle"
                  fontFamily="monospace"
                >
                  {n}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}

// =============================================================================
// APPLET 2: OPERATIONAL AMPLIFIER CONFIGURATION & GAIN LAB
// =============================================================================

function OpAmpGainLabApplet() {
  const [topology, setTopology] = useState('inverting');
  const [rIn, setRIn] = useState(10); // kΩ
  const [rF, setRF] = useState(47); // kΩ
  const [vIn, setVIn] = useState(1.2); // V peak
  const [vSat, setVSat] = useState(12); // V rail

  // Computations
  const gain = useMemo(() => {
    switch (topology) {
      case 'inverting':
        return -(rF / rIn);
      case 'non_inverting':
        return 1 + (rF / rIn);
      case 'differential':
        return rF / rIn;
      case 'integrator':
        return -(1 / (rIn * 0.001 * 10)); // pseudo gain at 1kHz with C=10nF
      default:
        return 1.0;
    }
  }, [topology, rIn, rF]);

  const vOutIdeal = useMemo(() => vIn * Math.abs(gain), [vIn, gain]);
  const isClipped = vOutIdeal > vSat;

  // Generate sine preview path points
  const wavePoints = useMemo(() => {
    const points = [];
    for (let i = 0; i <= 60; i++) {
      const angle = (i / 60) * Math.PI * 4; // 2 cycles
      const rawIn = Math.sin(angle) * vIn;
      let rawOut = (topology === 'inverting' || topology === 'integrator')
        ? -rawIn * Math.abs(gain)
        : rawIn * Math.abs(gain);

      // Apply rail clipping
      if (rawOut > vSat) rawOut = vSat;
      if (rawOut < -vSat) rawOut = -vSat;

      points.push({ x: i * 7, yIn: rawIn, yOut: rawOut });
    }
    return points;
  }, [vIn, gain, vSat, topology]);

  const topologies = ['inverting', 'non_inverting', 'differential', 'integrator'];

  return (
    <div className="space-y-6">
      {/* Topology Selector */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {topologies.map((top) => (
          <button
            key={top}
            onClick={() => setTopology(top)}
            className={`p-3 rounded-xl text-xs font-bold transition-all border text-left ${
              topology === top
                ? 'bg-sky-500/20 text-sky-300 border-sky-500 shadow-lg'
                : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700'
            }`}
          >
            <div className="capitalize">{top.replace('_', ' ')}</div>
            <div className="text-[10px] text-slate-500 font-mono mt-0.5">
              {top === 'inverting' && 'Av = -Rf / Rin'}
              {top === 'non_inverting' && 'Av = 1 + Rf / R1'}
              {top === 'differential' && 'Vo = (Rf/R1)(V2 - V1)'}
              {top === 'integrator' && 'Vo = -1/RC ∫ Vin dt'}
            </div>
          </button>
        ))}
      </div>

      {/* Control Sliders & Telemetry Box */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 p-5 rounded-xl bg-slate-950 border border-slate-800 space-y-4">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Circuit Component Parameters</h4>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="text-slate-400">Input Resistor (Rin / R1):</span>
                <span className="text-sky-400 font-bold">{rIn} kΩ</span>
              </div>
              <input
                type="range"
                min={1}
                max={50}
                step={1}
                value={rIn}
                onChange={(e) => setRIn(parseFloat(e.target.value))}
                className="w-full accent-sky-500 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="text-slate-400">Feedback Resistor (Rf):</span>
                <span className="text-emerald-400 font-bold">{rF} kΩ</span>
              </div>
              <input
                type="range"
                min={1}
                max={200}
                step={1}
                value={rF}
                onChange={(e) => setRF(parseFloat(e.target.value))}
                className="w-full accent-emerald-500 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="text-slate-400">Input Amplitude (Vin):</span>
                <span className="text-amber-400 font-bold">{vIn.toFixed(1)} V_peak</span>
              </div>
              <input
                type="range"
                min={0.1}
                max={5.0}
                step={0.1}
                value={vIn}
                onChange={(e) => setVIn(parseFloat(e.target.value))}
                className="w-full accent-amber-500 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="text-slate-400">Power Supply Rail (±Vsat):</span>
                <span className="text-purple-400 font-bold">±{vSat} V</span>
              </div>
              <input
                type="range"
                min={5}
                max={18}
                step={1}
                value={vSat}
                onChange={(e) => setVSat(parseFloat(e.target.value))}
                className="w-full accent-purple-500 cursor-pointer"
              />
            </div>
          </div>

          {/* Circuit Math Card */}
          <div className="mt-4 p-3 rounded-lg bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-4 text-xs font-mono">
            <div>
              <span className="text-slate-500">Calculated Gain (Av): </span>
              <span className="text-sky-300 font-bold">{gain.toFixed(2)} V/V</span>
              <span className="text-slate-400 ml-1">({(20 * Math.log10(Math.abs(gain))).toFixed(1)} dB)</span>
            </div>
            <div>
              <span className="text-slate-500">Unclipped Peak (Vout): </span>
              <span className="text-amber-300 font-bold">{vOutIdeal.toFixed(2)} V</span>
            </div>
            <div>
              <span className="text-slate-500">Saturation Status: </span>
              {isClipped ? (
                <span className="text-red-400 font-bold animate-pulse">CLIPPED @ ±{vSat}V</span>
              ) : (
                <span className="text-emerald-400 font-bold">LINEAR (No Slew/Clip)</span>
              )}
            </div>
          </div>
        </div>

        {/* Telemetry & Schematic preview */}
        <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col justify-between">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Op-Amp Topology Model</h4>
          <svg viewBox="0 0 240 160" className="w-full h-36 bg-slate-900/50 rounded-lg p-2">
            <polygon points="60,30 60,130 170,80" fill="#1e293b" stroke="#38bdf8" strokeWidth="2" />
            <text x="75" y="60" fill="#f8fafc" fontSize="14" fontFamily="monospace">-</text>
            <text x="75" y="110" fill="#f8fafc" fontSize="14" fontFamily="monospace">+</text>
            <line x1="170" y1="80" x2="220" y2="80" stroke="#34d399" strokeWidth="2" />
            <circle cx="220" cy="80" r="3" fill="#34d399" />
            <text x="200" y="72" fill="#34d399" fontSize="10" fontFamily="sans-serif">Vout</text>
            <path d="M 60 55 L 40 55 L 40 15 L 180 15 L 180 80" fill="none" stroke="#fbbf24" strokeWidth="1.5" strokeDasharray="3 2" />
            <text x="100" y="12" fill="#fbbf24" fontSize="9" fontFamily="monospace">Rf={rF}k</text>
            <line x1="10" y1="55" x2="60" y2="55" stroke="#38bdf8" strokeWidth="2" />
            <text x="15" y="48" fill="#38bdf8" fontSize="9" fontFamily="monospace">Rin={rIn}k</text>
          </svg>
          <div className="text-[11px] text-slate-400 leading-relaxed mt-2 font-mono">
            Input Impedance: <span className="text-white">{topology === 'inverting' ? `${rIn} kΩ` : '∞ (FET input)'}</span>
          </div>
        </div>
      </div>

      {/* Output Waveform Preview */}
      <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-xs font-bold text-slate-300 flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-400"></span>
            Input Waveform (Vin) &amp;
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 ml-1"></span>
            Output Waveform (Vout)
          </h4>
          <span className="text-[11px] font-mono text-slate-500">
            Scale: ±{vSat}V Full Dynamic Range
          </span>
        </div>
        <svg viewBox="0 0 440 180" className="w-full h-44 bg-slate-900/60 rounded-lg">
          <line x1="20" y1="20" x2="420" y2="20" stroke="#ef4444" strokeWidth="1" strokeDasharray="3 3" />
          <text x="25" y="16" fill="#ef4444" fontSize="8" fontFamily="monospace">+Vsat ({vSat}V)</text>
          
          <line x1="20" y1="90" x2="420" y2="90" stroke="#475569" strokeWidth="1" />
          <text x="25" y="86" fill="#64748b" fontSize="8" fontFamily="monospace">0V Ground</text>

          <line x1="20" y1="160" x2="420" y2="160" stroke="#ef4444" strokeWidth="1" strokeDasharray="3 3" />
          <text x="25" y="172" fill="#ef4444" fontSize="8" fontFamily="monospace">-Vsat (-{vSat}V)</text>

          <path
            d={wavePoints.reduce((acc, p, i) => {
              const yScaled = 90 - (p.yIn / vSat) * 70;
              return `${acc} ${i === 0 ? 'M' : 'L'} ${p.x + 20} ${yScaled}`;
            }, '')}
            fill="none"
            stroke="#38bdf8"
            strokeWidth="1.8"
          />

          <path
            d={wavePoints.reduce((acc, p, i) => {
              const yScaled = 90 - (p.yOut / vSat) * 70;
              return `${acc} ${i === 0 ? 'M' : 'L'} ${p.x + 20} ${yScaled}`;
            }, '')}
            fill="none"
            stroke={isClipped ? "#f87171" : "#34d399"}
            strokeWidth="2.5"
          />
        </svg>
      </div>
    </div>
  );
}

// =============================================================================
// APPLET 3: DIGITAL LOGIC BREADBOARD & COUNTER SANDBOX
// =============================================================================

function DigitalLogicSandboxApplet() {
  const [selectedBlock, setSelectedBlock] = useState('AND');
  const [inA, setInA] = useState(false);
  const [inB, setInB] = useState(false);
  const [counterVal, setCounterVal] = useState(0);

  // Compute logic gate output
  const gateOutput = useMemo(() => {
    switch (selectedBlock) {
      case 'AND': return inA && inB;
      case 'OR': return inA || inB;
      case 'NAND': return !(inA && inB);
      case 'NOR': return !(inA || inB);
      case 'XOR': return inA !== inB;
      default: return false;
    }
  }, [selectedBlock, inA, inB]);

  const stepClock = () => {
    setCounterVal(prev => (prev + 1) % 16);
  };

  const resetClock = () => {
    setCounterVal(0);
  };

  const q3 = (counterVal >> 3) & 1;
  const q2 = (counterVal >> 2) & 1;
  const q1 = (counterVal >> 1) & 1;
  const q0 = counterVal & 1;

  const logicBlocks = ['AND', 'OR', 'NAND', 'NOR', 'XOR', '4BIT_COUNTER'];

  return (
    <div className="space-y-6">
      {/* Block Selector */}
      <div className="flex flex-wrap items-center gap-2">
        {logicBlocks.map((block) => (
          <button
            key={block}
            onClick={() => setSelectedBlock(block)}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all border ${
              selectedBlock === block
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500 shadow-lg'
                : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700'
            }`}
          >
            {block === '4BIT_COUNTER' ? '4-Bit Ripple Counter (74LS93)' : `${block} Logic Gate`}
          </button>
        ))}
      </div>

      {selectedBlock !== '4BIT_COUNTER' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 rounded-xl bg-slate-950 border border-slate-800 space-y-5">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Interactive Logic Toggle Switches
            </h4>

            <div className="flex items-center gap-6">
              <button
                onClick={() => setInA(!inA)}
                className={`flex-1 p-4 rounded-xl border flex flex-col items-center justify-center gap-2 transition-all ${
                  inA
                    ? 'bg-emerald-950/60 border-emerald-500 text-emerald-300 shadow-lg shadow-emerald-500/10'
                    : 'bg-slate-900 border-slate-700 text-slate-400'
                }`}
              >
                <div className="text-xs font-bold font-mono">INPUT A</div>
                <div className={`text-2xl font-black ${inA ? 'text-emerald-400' : 'text-slate-600'}`}>
                  {inA ? '1 (HIGH)' : '0 (LOW)'}
                </div>
                <span className="text-[10px] text-slate-500">Click to Toggle</span>
              </button>

              <button
                onClick={() => setInB(!inB)}
                className={`flex-1 p-4 rounded-xl border flex flex-col items-center justify-center gap-2 transition-all ${
                  inB
                    ? 'bg-emerald-950/60 border-emerald-500 text-emerald-300 shadow-lg shadow-emerald-500/10'
                    : 'bg-slate-900 border-slate-700 text-slate-400'
                }`}
              >
                <div className="text-xs font-bold font-mono">INPUT B</div>
                <div className={`text-2xl font-black ${inB ? 'text-emerald-400' : 'text-slate-600'}`}>
                  {inB ? '1 (HIGH)' : '0 (LOW)'}
                </div>
                <span className="text-[10px] text-slate-500">Click to Toggle</span>
              </button>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
              <div>
                <div className="text-xs font-bold text-slate-400">OUTPUT Y ({selectedBlock})</div>
                <div className="text-xs font-mono text-slate-500 mt-0.5">
                  Expression: {selectedBlock === 'AND' && 'Y = A · B'}
                  {selectedBlock === 'OR' && 'Y = A + B'}
                  {selectedBlock === 'NAND' && 'Y = (A · B)\''}
                  {selectedBlock === 'NOR' && 'Y = (A + B)\''}
                  {selectedBlock === 'XOR' && 'Y = A ⊕ B'}
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center font-bold text-sm ${
                  gateOutput
                    ? 'bg-emerald-500 border-emerald-300 text-slate-950 shadow-lg shadow-emerald-500/50'
                    : 'bg-slate-950 border-slate-800 text-slate-600'
                }`}>
                  {gateOutput ? '1' : '0'}
                </div>
                <span className={`text-xs font-bold font-mono ${gateOutput ? 'text-emerald-400' : 'text-slate-500'}`}>
                  {gateOutput ? 'LED ON' : 'LED OFF'}
                </span>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-xl bg-slate-950 border border-slate-800">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
              Standard Truth Table ({selectedBlock})
            </h4>
            <table className="w-full text-xs font-mono border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 text-left">
                  <th className="py-2 px-3">Input A</th>
                  <th className="py-2 px-3">Input B</th>
                  <th className="py-2 px-3">Output Y</th>
                  <th className="py-2 px-3">State</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {[
                  [0, 0],
                  [0, 1],
                  [1, 0],
                  [1, 1]
                ].map(([a, b], idx) => {
                  let out = 0;
                  if (selectedBlock === 'AND') out = a & b;
                  if (selectedBlock === 'OR') out = a | b;
                  if (selectedBlock === 'NAND') out = (a & b) ? 0 : 1;
                  if (selectedBlock === 'NOR') out = (a | b) ? 0 : 1;
                  if (selectedBlock === 'XOR') out = a ^ b;

                  const isCurrentState = (inA ? 1 : 0) === a && (inB ? 1 : 0) === b;

                  return (
                    <tr
                      key={idx}
                      className={isCurrentState ? 'bg-sky-500/20 text-sky-300 font-bold' : 'text-slate-300'}
                    >
                      <td className="py-2.5 px-3">{a}</td>
                      <td className="py-2.5 px-3">{b}</td>
                      <td className="py-2.5 px-3 font-bold">{out}</td>
                      <td className="py-2.5 px-3">
                        {isCurrentState && (
                          <span className="px-1.5 py-0.5 rounded bg-sky-500 text-slate-950 text-[10px] font-bold">
                            CURRENT
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="p-6 rounded-xl bg-slate-950 border border-slate-800 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                4-Bit Synchronous Ripple Up-Counter
              </h4>
              <p className="text-xs text-slate-400 mt-1 font-mono">
                Counts from 0000_2 (0) to 1111_2 (15) on rising edge of clock.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={stepClock}
                className="px-4 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold text-xs font-mono shadow-lg transition-transform active:scale-95"
              >
                CLK Pulse (Step +1) ⚡
              </button>
              <button
                onClick={resetClock}
                className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono"
              >
                Reset (MR=1)
              </button>
            </div>
          </div>

          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'Q3 (MSB)', bit: q3, weight: 8 },
              { label: 'Q2', bit: q2, weight: 4 },
              { label: 'Q1', bit: q1, weight: 2 },
              { label: 'Q0 (LSB)', bit: q0, weight: 1 }
            ].map(({ label, bit, weight }) => (
              <div
                key={label}
                className={`p-4 rounded-xl border flex flex-col items-center justify-center gap-2 transition-all ${
                  bit === 1
                    ? 'bg-emerald-950/60 border-emerald-500 text-emerald-300 shadow-lg shadow-emerald-500/10'
                    : 'bg-slate-900 border-slate-800 text-slate-500'
                }`}
              >
                <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">{label}</div>
                <div className={`w-10 h-10 rounded-full border-2 flex items-center justify-center font-bold text-lg ${
                  bit === 1
                    ? 'bg-emerald-500 border-emerald-200 text-slate-950 shadow-md shadow-emerald-500/50'
                    : 'bg-slate-950 border-slate-800 text-slate-600'
                }`}>
                  {bit}
                </div>
                <div className="text-[10px] font-mono text-slate-500">Weight: 2^{Math.log2(weight)} ({weight})</div>
              </div>
            ))}
          </div>

          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-around font-mono text-center">
            <div>
              <div className="text-slate-500 text-[10px]">DECIMAL COUNT</div>
              <div className="text-2xl font-black text-amber-400">{counterVal}</div>
            </div>
            <div className="h-8 w-px bg-slate-800"></div>
            <div>
              <div className="text-slate-500 text-[10px]">HEXADECIMAL</div>
              <div className="text-2xl font-black text-sky-400">0x{counterVal.toString(16).toUpperCase()}</div>
            </div>
            <div className="h-8 w-px bg-slate-800"></div>
            <div>
              <div className="text-slate-500 text-[10px]">BINARY NIBBLE</div>
              <div className="text-2xl font-black text-emerald-400">{q3}{q2}{q1}{q0}b</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// APPLET 4: SERIAL BUS PROTOCOL & PACKET FRAME DECODER (UART / SPI / I2C)
// =============================================================================

function SerialBusProtocolDecoderApplet() {
  const [protocol, setProtocol] = useState('UART');
  const [hexInput, setHexInput] = useState('0x55');

  // Parse byte value safely
  const byteVal = useMemo(() => {
    let clean = hexInput.trim().toLowerCase();
    if (clean.startsWith('0x')) clean = clean.substring(2);
    const parsed = parseInt(clean, 16);
    return isNaN(parsed) ? 0x55 : (parsed & 0xFF);
  }, [hexInput]);

  // Bits 0..7
  const bits = useMemo(() => {
    const arr = [];
    for (let i = 0; i < 8; i++) {
      arr.push((byteVal >> i) & 1);
    }
    return arr;
  }, [byteVal]);

  const protocols = ['UART', 'SPI', 'I2C'];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/80 border border-slate-800">
        <div className="flex items-center gap-2">
          {protocols.map((p) => (
            <button
              key={p}
              onClick={() => setProtocol(p)}
              className={`px-4 py-2 rounded-xl text-xs font-bold font-mono transition-all border ${
                protocol === p
                  ? 'bg-purple-500/20 text-purple-300 border-purple-500 shadow-lg'
                  : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
              }`}
            >
              {p === 'UART' && 'UART (8N1)'}
              {p === 'SPI' && 'SPI (Mode 0)'}
              {p === 'I2C' && 'I2C (7-Bit Addr)'}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <label className="text-xs font-mono text-slate-400">Byte Payload (Hex):</label>
          <input
            type="text"
            value={hexInput}
            maxLength={4}
            onChange={(e) => setHexInput(e.target.value)}
            className="w-20 px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs font-mono font-bold text-amber-400 focus:outline-none focus:border-amber-400 text-center uppercase"
          />
          <span className="text-xs font-mono text-slate-500">
            = {byteVal} dec ({byteVal.toString(2).padStart(8, '0')}b)
          </span>
        </div>
      </div>

      <div className="p-5 rounded-xl bg-slate-950 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-400"></span>
            Bit-Accurate Logic Analyzer Waveform: {protocol}
          </h4>
          <span className="text-[11px] font-mono text-purple-300 font-semibold">
            {protocol === 'UART' && '1 Start Bit + 8 Data Bits (LSB First) + 1 Stop Bit'}
            {protocol === 'SPI' && 'CS# Active Low | CPOL=0 CPHA=0 | MSB First'}
            {protocol === 'I2C' && 'START + 7b Addr + R/W=0 + ACK + 8b Data + STOP'}
          </span>
        </div>

        {protocol === 'UART' && (
          <svg viewBox="0 0 880 180" className="w-full h-44 bg-slate-900/60 rounded-lg p-2 font-mono">
            <line x1="40" y1="50" x2="840" y2="50" stroke="#334155" strokeWidth="1" strokeDasharray="2 2" />
            <line x1="40" y1="120" x2="840" y2="120" stroke="#334155" strokeWidth="1" strokeDasharray="2 2" />
            <text x="10" y="55" fill="#64748b" fontSize="10">HIGH</text>
            <text x="10" y="125" fill="#64748b" fontSize="10">LOW</text>

            {(() => {
              const slots = [1, 0, ...bits, 1, 1];
              let pathStr = `M 40 50 L 80 50`;
              for (let i = 1; i < slots.length; i++) {
                const xStart = 80 + (i - 1) * 70;
                const xEnd = 80 + i * 70;
                const yVal = slots[i] === 1 ? 50 : 120;
                pathStr += ` L ${xStart} ${yVal} L ${xEnd} ${yVal}`;
              }

              return (
                <path d={pathStr} fill="none" stroke="#38bdf8" strokeWidth="3" strokeLinejoin="miter" />
              );
            })()}

            <g transform="translate(80, 150)">
              <text x="35" y="0" fill="#f87171" fontSize="10" textAnchor="middle" fontWeight="bold">START (0)</text>
              {bits.map((b, idx) => (
                <text key={idx} x={105 + idx * 70} y="0" fill="#fbbf24" fontSize="10" textAnchor="middle">
                  D{idx}:{b}
                </text>
              ))}
              <text x="735" y="0" fill="#34d399" fontSize="10" textAnchor="middle" fontWeight="bold">STOP (1)</text>
            </g>
          </svg>
        )}

        {protocol === 'SPI' && (
          <svg viewBox="0 0 880 220" className="w-full h-52 bg-slate-900/60 rounded-lg p-2 font-mono">
            <text x="15" y="35" fill="#f87171" fontSize="11" fontWeight="bold">CS#</text>
            <path d="M 60 25 L 120 25 L 120 45 L 800 45 L 800 25 L 860 25" fill="none" stroke="#f87171" strokeWidth="2.5" />

            <text x="15" y="95" fill="#38bdf8" fontSize="11" fontWeight="bold">SCLK</text>
            {(() => {
              let clkPath = `M 60 110 L 140 110`;
              for (let i = 0; i < 8; i++) {
                const x0 = 140 + i * 80;
                clkPath += ` L ${x0} 110 L ${x0} 80 L ${x0 + 40} 80 L ${x0 + 40} 110 L ${x0 + 80} 110`;
              }
              return <path d={clkPath} fill="none" stroke="#38bdf8" strokeWidth="2" />;
            })()}

            <text x="15" y="165" fill="#34d399" fontSize="11" fontWeight="bold">MOSI</text>
            {(() => {
              const msbBits = [...bits].reverse();
              let mosiPath = `M 60 180 L 140 180`;
              for (let i = 0; i < 8; i++) {
                const x0 = 140 + i * 80;
                const y = msbBits[i] === 1 ? 150 : 180;
                mosiPath += ` L ${x0} ${y} L ${x0 + 80} ${y}`;
              }
              return <path d={mosiPath} fill="none" stroke="#34d399" strokeWidth="2.5" />;
            })()}

            <g transform="translate(140, 205)">
              {[...bits].reverse().map((b, idx) => (
                <text key={idx} x={40 + idx * 80} y="0" fill="#fbbf24" fontSize="10" textAnchor="middle">
                  B{7 - idx}:{b}
                </text>
              ))}
            </g>
          </svg>
        )}

        {protocol === 'I2C' && (
          <svg viewBox="0 0 880 220" className="w-full h-52 bg-slate-900/60 rounded-lg p-2 font-mono">
            <text x="15" y="55" fill="#38bdf8" fontSize="11" fontWeight="bold">SCL</text>
            {(() => {
              let sclPath = `M 60 40 L 130 40`;
              for (let i = 0; i < 9; i++) {
                const x0 = 130 + i * 40;
                sclPath += ` L ${x0} 40 L ${x0} 70 L ${x0 + 20} 70 L ${x0 + 20} 40 L ${x0 + 40} 40`;
              }
              for (let i = 0; i < 9; i++) {
                const x0 = 490 + i * 40;
                sclPath += ` L ${x0} 40 L ${x0} 70 L ${x0 + 20} 70 L ${x0 + 20} 40 L ${x0 + 40} 40`;
              }
              sclPath += ` L 860 40`;
              return <path d={sclPath} fill="none" stroke="#38bdf8" strokeWidth="2" />;
            })()}

            <text x="15" y="145" fill="#fbbf24" fontSize="11" fontWeight="bold">SDA</text>
            {(() => {
              let sdaPath = `M 60 120 L 90 120 L 110 150 L 130 150`;
              const addrBits = [1, 0, 0, 1, 0, 0, 0];
              for (let i = 0; i < 7; i++) {
                const x0 = 130 + i * 40;
                const y = addrBits[i] === 1 ? 120 : 150;
                sdaPath += ` L ${x0} ${y} L ${x0 + 40} ${y}`;
              }
              sdaPath += ` L 410 150 L 450 150`;
              sdaPath += ` L 450 150 L 490 150`;
              for (let i = 0; i < 8; i++) {
                const x0 = 490 + i * 40;
                const y = bits[7 - i] === 1 ? 120 : 150;
                sdaPath += ` L ${x0} ${y} L ${x0 + 40} ${y}`;
              }
              sdaPath += ` L 810 150 L 830 150`;
              sdaPath += ` L 840 120 L 860 120`;
              return <path d={sdaPath} fill="none" stroke="#fbbf24" strokeWidth="2.5" />;
            })()}

            <g transform="translate(60, 190)">
              <text x="40" y="0" fill="#f87171" fontSize="9" fontWeight="bold">START</text>
              <text x="210" y="0" fill="#38bdf8" fontSize="9">7-Bit Addr (0x48)</text>
              <text x="360" y="0" fill="#c084fc" fontSize="9">W(0)</text>
              <text x="400" y="0" fill="#34d399" fontSize="9" fontWeight="bold">ACK</text>
              <text x="590" y="0" fill="#fbbf24" fontSize="9">8-Bit Payload (0x{byteVal.toString(16).toUpperCase()})</text>
              <text x="760" y="0" fill="#34d399" fontSize="9" fontWeight="bold">ACK</text>
              <text x="790" y="0" fill="#f87171" fontSize="9" fontWeight="bold">STOP</text>
            </g>
          </svg>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// ROOT EXPORT: EceInteractiveLabApplets
// =============================================================================

export default function EceInteractiveLabApplets({ initialApplet = 'convolution' }) {
  const [activeApplet, setActiveApplet] = useState(initialApplet);

  const APPLETS = [
    {
      id: 'convolution',
      title: 'Discrete Convolution Animator',
      category: 'Signals & Systems',
      icon: '〰️',
      description: 'Step-by-step convolution sum animator showing folded/shifted kernels and overlapping product integrals.'
    },
    {
      id: 'opamp',
      title: 'Op-Amp Topology & Gain Lab',
      category: 'Analog Electronics',
      icon: '⚡',
      description: 'Interactive inverting, non-inverting, differentiator, and integrator circuits with live clipping saturation.'
    },
    {
      id: 'digital',
      title: 'Digital Logic & Ripple Counter',
      category: 'Digital Systems',
      icon: '🔲',
      description: 'Clickable toggle switches, gate truth tables, and 4-bit synchronous ripple counter sandbox.'
    },
    {
      id: 'serial',
      title: 'Serial Bus Protocol Analyzer',
      category: 'Embedded Protocols',
      icon: '📡',
      description: 'Bit-accurate timing waveforms and packet frame decoders for UART 8N1, SPI Mode 0, and I2C buses.'
    }
  ];

  return (
    <div className="w-full bg-[var(--surface-color,#0b1329)] border border-[var(--border-color,#1e293b)] rounded-2xl p-6 sm:p-8 shadow-2xl">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-[var(--border-color,#1e293b)]">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 mb-2">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
            </svg>
            Standalone Interactive ECE Mini-Applets Suite
          </div>
          <h2 className="text-2xl font-extrabold text-[var(--text-color,#f8fafc)] tracking-tight">
            Engineering Workbench &amp; Signal Laboratories
          </h2>
          <p className="text-sm text-[var(--text-secondary,#94a3b8)] mt-1">
            Zero-polling, client-side interactive simulators designed for Anna University MIT Campus Regulation 2023 syllabi.
          </p>
        </div>

        {/* Status Badge */}
        <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-800/60 px-3 py-1.5 rounded-xl">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          Passive Event Driven • 0% Idle CPU
        </div>
      </div>

      {/* Segmented Applet Switcher */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6">
        {APPLETS.map((applet) => (
          <button
            key={applet.id}
            onClick={() => setActiveApplet(applet.id)}
            className={`p-3.5 rounded-xl border text-left transition-all ${
              activeApplet === applet.id
                ? 'bg-sky-500/15 border-sky-500/80 shadow-lg shadow-sky-500/5'
                : 'bg-[var(--card-bg,#0f172a)] border-[var(--border-color,#1e293b)] hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-lg">{applet.icon}</span>
              <span className="text-[10px] font-mono text-sky-400 uppercase tracking-wider">{applet.category}</span>
            </div>
            <div className="font-bold text-xs text-[var(--text-color,#f8fafc)] mt-2">
              {applet.title}
            </div>
          </button>
        ))}
      </div>

      {/* Active Applet Workspace */}
      <div className="mt-6 pt-6 border-t border-[var(--border-color,#1e293b)]">
        {activeApplet === 'convolution' && <DiscreteConvolutionApplet />}
        {activeApplet === 'opamp' && <OpAmpGainLabApplet />}
        {activeApplet === 'digital' && <DigitalLogicSandboxApplet />}
        {activeApplet === 'serial' && <SerialBusProtocolDecoderApplet />}
      </div>
    </div>
  );
}
