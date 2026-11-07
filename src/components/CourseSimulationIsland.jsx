import React, { useState, useMemo } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Dedicated Interactive Course Simulation Island (Tier 2)
 * Connects directly to CourseLessonReader and CourseLabSimulator:
 *   - EC23S01: Python DSP Butterworth & Chebyshev Bode Plot Visualizer
 *   - EC23C03: Shockley Diode & MOSFET IV Characteristic Curve Tracer
 *   - EC23E04: Fabry-Perot Optical Cavity Stability (g1-g2) Diagram Viewer
 *   - EC8702:  FreeRTOS Task Schedulability & Rate Monotonic Utilization Calculator
 *
 * Hardware Safe: 100% client-side computation, passive CPU (<5%), zero polling daemons.
 * ========================================================================================
 */

export default function CourseSimulationIsland({
  courseCode = "EC23S01",
  themeColor = "#00F0B5",
  themeFamily = "emerald",
  compact = false
}) {
  const normalizedCode = courseCode.toUpperCase().trim();

  return (
    <div className={`rounded-2xl border bg-[#020813] p-4 sm:p-5 font-mono text-xs text-slate-200 shadow-xl space-y-4`}
         style={{ borderColor: `${themeColor}40` }}>
      
      {/* Simulation Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <span className="p-1.5 rounded-lg bg-[#041026] border border-slate-700 text-sm">⚡</span>
          <div>
            <span className="font-bold text-white text-xs sm:text-sm font-sans block">
              {normalizedCode === "EC23S01" && "Python DSP: Butterworth & Chebyshev Bode Visualizer"}
              {normalizedCode === "EC23C03" && "Electronic Devices: Shockley Diode & MOSFET IV Tracer"}
              {normalizedCode === "EC23E04" && "Optics & Lasers: Fabry-Perot Cavity Stability (g1-g2) Viewer"}
              {normalizedCode === "EC8702" && "Embedded Systems: FreeRTOS Task Schedulability Calculator"}
            </span>
            <span className="text-[10px] text-slate-400">
              Interactive Hardware & Physics Mathematical Sandbox • Local Edge Engine
            </span>
          </div>
        </div>
        <span className="text-[10px] px-2.5 py-0.5 rounded-full font-bold uppercase self-start sm:self-auto"
              style={{ backgroundColor: `${themeColor}20`, color: themeColor, border: `1px solid ${themeColor}40` }}>
          Active Island
        </span>
      </div>

      {/* Render Specific Simulation by Course */}
      {normalizedCode === "EC23S01" && <DspFilterSimulation themeColor={themeColor} compact={compact} />}
      {normalizedCode === "EC23C03" && <DeviceIvSimulation themeColor={themeColor} compact={compact} />}
      {normalizedCode === "EC23E04" && <OpticsCavitySimulation themeColor={themeColor} compact={compact} />}
      {normalizedCode === "EC8702" && <RtosSchedulabilitySimulation themeColor={themeColor} compact={compact} />}
    </div>
  );
}

// ---------------------------------------------------------------------------
// 1. EC23S01: PYTHON DSP BUTTERWORTH & CHEBYSHEV BODE PLOT VISUALIZER
// ---------------------------------------------------------------------------
function DspFilterSimulation({ themeColor, compact }) {
  const [filterType, setFilterType] = useState('butterworth'); // 'butterworth' | 'chebyshev'
  const [fc, setFc] = useState(1200); // Cutoff frequency Hz
  const [fs, setFs] = useState(16000); // Sampling frequency Hz
  const [order, setOrder] = useState(3); // Filter order N
  const [rippleDb, setRippleDb] = useState(1.0); // Chebyshev passband ripple

  const simData = useMemo(() => {
    const fNyquist = fs / 2;
    const points = [];
    const numPoints = 60;
    const minF = 20;
    const maxF = fNyquist;

    // Chebyshev epsilon parameter
    const epsilon = Math.sqrt(Math.pow(10, rippleDb / 10) - 1);

    for (let i = 0; i < numPoints; i++) {
      const logF = Math.log10(minF) + (i / (numPoints - 1)) * (Math.log10(maxF) - Math.log10(minF));
      const f = Math.pow(10, logF);
      const wRatio = f / fc;

      let magGain = 1.0;
      if (filterType === 'butterworth') {
        magGain = 1.0 / Math.sqrt(1 + Math.pow(wRatio, 2 * order));
      } else {
        // Chebyshev polynomial approximation CN(x)
        let cn = 0;
        if (wRatio <= 1.0) {
          cn = Math.cos(order * Math.acos(wRatio));
        } else {
          cn = Math.cosh(order * Math.acosh(wRatio));
        }
        magGain = 1.0 / Math.sqrt(1 + Math.pow(epsilon * cn, 2));
      }

      const magDb = 20 * Math.log10(Math.max(magGain, 1e-4));
      points.push({ f: Math.round(f), magDb: Number(magDb.toFixed(2)) });
    }

    const rollOff = -20 * order;
    return { fNyquist, points, rollOff };
  }, [filterType, fc, fs, order, rippleDb]);

  // SVG Coordinates mapping: width=500, height=200, dB range: 0 to -60 dB
  const svgWidth = 500;
  const svgHeight = 180;
  const minDb = -60;
  const maxDb = 5;

  const pathData = useMemo(() => {
    return simData.points.map((pt, idx) => {
      const x = (idx / (simData.points.length - 1)) * (svgWidth - 40) + 30;
      const clampedDb = Math.max(minDb, Math.min(maxDb, pt.magDb));
      const y = svgHeight - 20 - ((clampedDb - minDb) / (maxDb - minDb)) * (svgHeight - 40);
      return `${idx === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
    }).join(' ');
  }, [simData.points]);

  return (
    <div className="space-y-4">
      {/* Controls Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div>
          <label className="text-slate-400 text-[10px] uppercase font-bold block mb-1">Filter Family</label>
          <div className="flex rounded-lg overflow-hidden border border-slate-700">
            <button
              onClick={() => setFilterType('butterworth')}
              className={`flex-1 py-1 text-[11px] font-bold ${filterType === 'butterworth' ? 'bg-emerald-500 text-slate-950' : 'bg-[#041026] text-slate-400'}`}
            >
              Butterworth
            </button>
            <button
              onClick={() => setFilterType('chebyshev')}
              className={`flex-1 py-1 text-[11px] font-bold ${filterType === 'chebyshev' ? 'bg-emerald-500 text-slate-950' : 'bg-[#041026] text-slate-400'}`}
            >
              Chebyshev
            </button>
          </div>
        </div>

        <div>
          <label className="text-slate-400 text-[10px] uppercase font-bold block mb-1">Cutoff fc: {fc} Hz</label>
          <input
            type="range"
            min="200"
            max="4000"
            step="50"
            value={fc}
            onChange={(e) => setFc(Number(e.target.value))}
            className="w-full accent-[#00F0B5]"
          />
        </div>

        <div>
          <label className="text-slate-400 text-[10px] uppercase font-bold block mb-1">Order N: {order}</label>
          <input
            type="range"
            min="1"
            max="6"
            step="1"
            value={order}
            onChange={(e) => setOrder(Number(e.target.value))}
            className="w-full accent-[#00F0B5]"
          />
        </div>

        {filterType === 'chebyshev' ? (
          <div>
            <label className="text-slate-400 text-[10px] uppercase font-bold block mb-1">Passband Ripple: {rippleDb} dB</label>
            <input
              type="range"
              min="0.2"
              max="3.0"
              step="0.2"
              value={rippleDb}
              onChange={(e) => setRippleDb(Number(e.target.value))}
              className="w-full accent-[#00F0B5]"
            />
          </div>
        ) : (
          <div>
            <label className="text-slate-400 text-[10px] uppercase font-bold block mb-1">Sampling fs: {fs} Hz</label>
            <select
              value={fs}
              onChange={(e) => setFs(Number(e.target.value))}
              className="w-full p-1 rounded bg-[#041026] border border-slate-700 text-slate-200 text-xs"
            >
              <option value="8000">8 kHz (Telephony)</option>
              <option value="16000">16 kHz (Wideband)</option>
              <option value="44100">44.1 kHz (Audio CD)</option>
            </select>
          </div>
        )}
      </div>

      {/* SVG Bode Graph Canvas */}
      <div className="p-3 rounded-xl bg-[#041026] border border-slate-800 relative">
        <div className="flex justify-between items-center text-[10px] text-slate-400 mb-2">
          <span>Magnitude Frequency Response |H(f)|</span>
          <span className="font-bold text-emerald-400">Roll-Off: {simData.rollOff} dB/dec • Nyquist: {simData.fNyquist} Hz</span>
        </div>
        <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="w-full h-40 bg-[#020813] rounded-lg border border-slate-800">
          {/* Horizontal Grid lines (0 dB, -20 dB, -40 dB, -60 dB) */}
          {[0, -20, -40, -60].map((db) => {
            const y = svgHeight - 20 - ((db - minDb) / (maxDb - minDb)) * (svgHeight - 40);
            return (
              <g key={db}>
                <line x1="30" y1={y} x2={svgWidth - 10} y2={y} stroke="#1E293B" strokeDasharray="3 3" />
                <text x="24" y={y + 3} fill="#64748B" fontSize="8" textAnchor="end">{db}dB</text>
              </g>
            );
          })}
          {/* -3dB Cutoff dashed guideline */}
          <line
            x1="30"
            y1={svgHeight - 20 - ((-3 - minDb) / (maxDb - minDb)) * (svgHeight - 40)}
            x2={svgWidth - 10}
            y2={svgHeight - 20 - ((-3 - minDb) / (maxDb - minDb)) * (svgHeight - 40)}
            stroke="#F59E0B"
            strokeDasharray="2 2"
            strokeWidth="1"
          />
          {/* Frequency Response Curve */}
          <path d={pathData} fill="none" stroke="#00F0B5" strokeWidth="2.5" />
        </svg>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// 2. EC23C03: SHOCKLEY DIODE & MOSFET IV CHARACTERISTIC CURVE TRACER
// ---------------------------------------------------------------------------
function DeviceIvSimulation({ themeColor, compact }) {
  const [deviceMode, setDeviceMode] = useState('diode'); // 'diode' | 'mosfet'
  const [vf, setVf] = useState(0.68); // Forward bias voltage
  const [tempK, setTempK] = useState(300); // Kelvin
  const [vgs, setVgs] = useState(3.5); // MOSFET VGS
  const [vds, setVds] = useState(2.5); // MOSFET VDS

  // Mathematical Physics Engine
  const data = useMemo(() => {
    const kB = 1.380649e-23;
    const q = 1.60217663e-19;
    const vt = (kB * tempK) / q;
    const vtMv = vt * 1000;
    const eta = 1.05;

    // Diode IS at temperature T
    const is300 = 1e-12;
    const isCurrent = is300 * Math.pow(tempK / 300, 3) * Math.exp(1.12 / (kB * 300 / q) - 1.12 / vt);
    const diodeCurrentA = isCurrent * (Math.exp(Math.min(vf / (eta * vt), 25)) - 1);
    const diodeCurrentMa = diodeCurrentA * 1000;
    const dynamicRd = (eta * vt) / Math.max(diodeCurrentA, 1e-9);

    // Diode Curve (0 to 0.85V)
    const diodePoints = [];
    for (let v = 0; v <= 0.85; v += 0.02) {
      const iA = isCurrent * (Math.exp(Math.min(v / (eta * vt), 25)) - 1);
      diodePoints.push({ v: Number(v.toFixed(2)), iMa: Math.min(iA * 1000, 80) });
    }

    // MOSFET parameters
    const vth = 1.2;
    const kn = 20.0; // mA/V^2
    const vov = Math.max(0, vgs - vth);
    const mosfetSatIdMa = 0.5 * kn * Math.pow(vov, 2);
    let currentIdMa = 0;
    let operatingRegion = 'Cutoff';

    if (vgs < vth) {
      currentIdMa = 0;
      operatingRegion = 'Cutoff (VGS < Vth)';
    } else if (vds < vov) {
      currentIdMa = kn * (vov * vds - 0.5 * vds * vds);
      operatingRegion = 'Triode / Linear (VDS < Vov)';
    } else {
      currentIdMa = 0.5 * kn * Math.pow(vov, 2) * (1 + 0.02 * vds);
      operatingRegion = 'Saturation / Active (VDS >= Vov)';
    }

    return { vtMv, diodeCurrentMa, dynamicRd, diodePoints, vov, mosfetSatIdMa, currentIdMa, operatingRegion };
  }, [vf, tempK, vgs, vds]);

  const svgWidth = 500;
  const svgHeight = 180;

  return (
    <div className="space-y-4">
      {/* Controls Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div>
          <label className="text-slate-400 text-[10px] uppercase font-bold block mb-1">Device Mode</label>
          <div className="flex rounded-lg overflow-hidden border border-slate-700">
            <button
              onClick={() => setDeviceMode('diode')}
              className={`flex-1 py-1 text-[11px] font-bold ${deviceMode === 'diode' ? 'bg-amber-500 text-slate-950' : 'bg-[#041026] text-slate-400'}`}
            >
              PN Diode
            </button>
            <button
              onClick={() => setDeviceMode('mosfet')}
              className={`flex-1 py-1 text-[11px] font-bold ${deviceMode === 'mosfet' ? 'bg-amber-500 text-slate-950' : 'bg-[#041026] text-slate-400'}`}
            >
              N-MOSFET
            </button>
          </div>
        </div>

        {deviceMode === 'diode' ? (
          <>
            <div>
              <label className="text-slate-400 text-[10px] uppercase font-bold block mb-1">Bias VF: {vf.toFixed(2)} V</label>
              <input
                type="range"
                min="0.1"
                max="0.85"
                step="0.01"
                value={vf}
                onChange={(e) => setVf(Number(e.target.value))}
                className="w-full accent-[#F59E0B]"
              />
            </div>
            <div>
              <label className="text-slate-400 text-[10px] uppercase font-bold block mb-1">Temp: {tempK} K</label>
              <input
                type="range"
                min="250"
                max="400"
                step="5"
                value={tempK}
                onChange={(e) => setTempK(Number(e.target.value))}
                className="w-full accent-[#F59E0B]"
              />
            </div>
            <div className="p-2 rounded bg-[#041026] border border-slate-800 text-[11px]">
              <span className="text-slate-400 block text-[9px] uppercase">ID Current / Dynamic rd:</span>
              <span className="text-amber-400 font-bold">{data.diodeCurrentMa.toFixed(2)} mA</span> • <span className="text-slate-300">{data.dynamicRd.toFixed(1)} Ω</span>
            </div>
          </>
        ) : (
          <>
            <div>
              <label className="text-slate-400 text-[10px] uppercase font-bold block mb-1">VGS: {vgs.toFixed(1)} V</label>
              <input
                type="range"
                min="0.5"
                max="5.0"
                step="0.1"
                value={vgs}
                onChange={(e) => setVgs(Number(e.target.value))}
                className="w-full accent-[#F59E0B]"
              />
            </div>
            <div>
              <label className="text-slate-400 text-[10px] uppercase font-bold block mb-1">VDS: {vds.toFixed(1)} V</label>
              <input
                type="range"
                min="0.0"
                max="6.0"
                step="0.1"
                value={vds}
                onChange={(e) => setVds(Number(e.target.value))}
                className="w-full accent-[#F59E0B]"
              />
            </div>
            <div className="p-2 rounded bg-[#041026] border border-slate-800 text-[11px]">
              <span className="text-slate-400 block text-[9px] uppercase">Region / Drain ID:</span>
              <span className="text-amber-400 font-bold">{data.currentIdMa.toFixed(2)} mA</span>
              <span className="text-[9px] text-slate-400 block truncate">{data.operatingRegion}</span>
            </div>
          </>
        )}
      </div>

      {/* SVG IV Curve Canvas */}
      <div className="p-3 rounded-xl bg-[#041026] border border-slate-800 relative">
        <div className="flex justify-between items-center text-[10px] text-slate-400 mb-2">
          <span>{deviceMode === 'diode' ? "Shockley Diode Exponential IV Curve" : "N-MOSFET Drain Family Characteristics"}</span>
          <span className="text-amber-400 font-bold">Thermal VT: {data.vtMv.toFixed(1)} mV</span>
        </div>
        <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="w-full h-40 bg-[#020813] rounded-lg border border-slate-800">
          {/* Axis Grid */}
          <line x1="40" y1="10" x2="40" y2={svgHeight - 20} stroke="#334155" strokeWidth="1.5" />
          <line x1="40" y1={svgHeight - 20} x2={svgWidth - 10} y2={svgHeight - 20} stroke="#334155" strokeWidth="1.5" />

          {deviceMode === 'diode' ? (
            <>
              {/* Diode Curve */}
              <path
                d={data.diodePoints.map((pt, i) => {
                  const x = 40 + (pt.v / 0.85) * (svgWidth - 60);
                  const y = svgHeight - 20 - (pt.iMa / 80) * (svgHeight - 35);
                  return `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
                }).join(' ')}
                fill="none"
                stroke="#F59E0B"
                strokeWidth="2.5"
              />
              {/* Operating Point */}
              <circle
                cx={(40 + (vf / 0.85) * (svgWidth - 60)).toFixed(1)}
                cy={(svgHeight - 20 - (Math.min(data.diodeCurrentMa, 80) / 80) * (svgHeight - 35)).toFixed(1)}
                r="4.5"
                fill="#EF4444"
              />
            </>
          ) : (
            <>
              {/* 4 MOSFET Curves for VGS = 2, 3, 4, 5V */}
              {[2.0, 3.0, 4.0, 5.0].map((vg, curveIdx) => {
                const ov = Math.max(0, vg - 1.2);
                const pts = [];
                for (let v = 0; v <= 6.0; v += 0.2) {
                  let iD = v < ov ? 20 * (ov * v - 0.5 * v * v) : 0.5 * 20 * Math.pow(ov, 2) * (1 + 0.02 * v);
                  pts.push({ v, iD: Math.min(iD, 160) });
                }
                const dPath = pts.map((pt, i) => {
                  const x = 40 + (pt.v / 6.0) * (svgWidth - 60);
                  const y = svgHeight - 20 - (pt.iD / 160) * (svgHeight - 35);
                  return `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
                }).join(' ');
                return (
                  <path key={curveIdx} d={dPath} fill="none" stroke={vg === 5 ? "#F59E0B" : "#FBBF24"} strokeWidth={vg === Math.round(vgs) ? "3" : "1.5"} opacity={vg === Math.round(vgs) ? 1 : 0.45} />
                );
              })}
            </>
          )}
        </svg>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// 3. EC23E04: FABRY-PEROT OPTICAL CAVITY STABILITY (g1-g2) DIAGRAM VIEWER
// ---------------------------------------------------------------------------
function OpticsCavitySimulation({ themeColor, compact }) {
  const [cavityLength, setCavityLength] = useState(0.5); // meters
  const [r1, setR1] = useState(1.0); // radius mirror 1
  const [r2, setR2] = useState(0.8); // radius mirror 2
  const [reflectance, setReflectance] = useState(0.95);

  const opticsData = useMemo(() => {
    const g1 = 1 - (cavityLength / r1);
    const g2 = 1 - (cavityLength / r2);
    const gProd = g1 * g2;
    const isStable = gProd >= 0 && gProd <= 1.0;

    // Speed of light mode spacing
    const c = 2.99792458e8;
    const modeSpacingMhz = (c / (2 * cavityLength)) / 1e6;

    // Fabry-Perot Finesse F = pi * sqrt(R) / (1 - R)
    const finesse = (Math.PI * Math.sqrt(reflectance)) / (1 - reflectance);

    return { g1, g2, gProd, isStable, modeSpacingMhz, finesse };
  }, [cavityLength, r1, r2, reflectance]);

  return (
    <div className="space-y-4">
      {/* Controls Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div>
          <label className="text-slate-400 text-[10px] uppercase font-bold block mb-1">Cavity Length L: {cavityLength} m</label>
          <input
            type="range"
            min="0.1"
            max="1.5"
            step="0.05"
            value={cavityLength}
            onChange={(e) => setCavityLength(Number(e.target.value))}
            className="w-full accent-[#06B6D4]"
          />
        </div>
        <div>
          <label className="text-slate-400 text-[10px] uppercase font-bold block mb-1">Mirror R1: {r1} m</label>
          <input
            type="range"
            min="0.2"
            max="2.0"
            step="0.1"
            value={r1}
            onChange={(e) => setR1(Number(e.target.value))}
            className="w-full accent-[#06B6D4]"
          />
        </div>
        <div>
          <label className="text-slate-400 text-[10px] uppercase font-bold block mb-1">Mirror R2: {r2} m</label>
          <input
            type="range"
            min="0.2"
            max="2.0"
            step="0.1"
            value={r2}
            onChange={(e) => setR2(Number(e.target.value))}
            className="w-full accent-[#06B6D4]"
          />
        </div>
        <div>
          <label className="text-slate-400 text-[10px] uppercase font-bold block mb-1">Reflectance R: {reflectance}</label>
          <input
            type="range"
            min="0.80"
            max="0.99"
            step="0.01"
            value={reflectance}
            onChange={(e) => setReflectance(Number(e.target.value))}
            className="w-full accent-[#06B6D4]"
          />
        </div>
      </div>

      {/* Stability Metrics & Diagram */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-center">
        <div className="sm:col-span-2 p-3 rounded-xl bg-[#041026] border border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-[10px]">
            <span className="text-slate-400">Resonator Stability Product:</span>
            <span className={`px-2 py-0.5 rounded font-bold ${opticsData.isStable ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/50' : 'bg-rose-950 text-rose-300 border border-rose-500/50'}`}>
              {opticsData.isStable ? "STABLE (0 <= g1*g2 <= 1)" : "UNSTABLE (g1*g2 > 1 or < 0)"}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="p-2 rounded bg-[#020813] border border-slate-800">
              <span className="text-slate-400 text-[10px] block">g1 = 1 - L/R1:</span>
              <span className="font-bold text-cyan-400">{opticsData.g1.toFixed(3)}</span>
            </div>
            <div className="p-2 rounded bg-[#020813] border border-slate-800">
              <span className="text-slate-400 text-[10px] block">g2 = 1 - L/R2:</span>
              <span className="font-bold text-cyan-400">{opticsData.g2.toFixed(3)}</span>
            </div>
          </div>
          <div className="flex justify-between text-[11px] pt-1">
            <span className="text-slate-400">Mode Spacing Δν: <strong className="text-white">{opticsData.modeSpacingMhz.toFixed(1)} MHz</strong></span>
            <span className="text-slate-400">Etalon Finesse: <strong className="text-cyan-300">{opticsData.finesse.toFixed(1)}</strong></span>
          </div>
        </div>

        {/* 2D g1-g2 Diagram */}
        <div className="flex justify-center p-2 rounded-xl bg-[#041026] border border-slate-800">
          <svg viewBox="0 0 160 160" className="w-36 h-36 bg-[#020813] rounded border border-slate-800">
            {/* Axes */}
            <line x1="80" y1="10" x2="80" y2="150" stroke="#334155" strokeWidth="1" />
            <line x1="10" y1="80" x2="150" y2="80" stroke="#334155" strokeWidth="1" />
            {/* Stability shaded boundaries: g1*g2 = 1 branches */}
            <rect x="80" y="20" width="60" height="60" fill="rgba(6, 182, 212, 0.15)" />
            <rect x="20" y="80" width="60" height="60" fill="rgba(6, 182, 212, 0.15)" />
            {/* Operating Point */}
            {(() => {
              const cx = Math.max(10, Math.min(150, 80 + opticsData.g1 * 50));
              const cy = Math.max(10, Math.min(150, 80 - opticsData.g2 * 50));
              return (
                <circle cx={cx} cy={cy} r="4" fill={opticsData.isStable ? "#00F0B5" : "#EF4444"} className="animate-pulse" />
              );
            })()}
          </svg>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// 4. EC8702: FREERTOS TASK SCHEDULABILITY & UTILIZATION CALCULATOR
// ---------------------------------------------------------------------------
function RtosSchedulabilitySimulation({ themeColor, compact }) {
  const [tasks, setTasks] = useState([
    { id: 1, name: 'Sensor Poll', c: 8, t: 30 },
    { id: 2, name: 'Control Loop', c: 12, t: 50 },
    { id: 3, name: 'Telemetry Log', c: 15, t: 100 }
  ]);

  const handleUpdateTask = (idx, field, val) => {
    setTasks(prev => {
      const copy = [...prev];
      copy[idx] = { ...copy[idx], [field]: Number(val) };
      return copy;
    });
  };

  const schedData = useMemo(() => {
    const utilizations = tasks.map(t => (t.c / t.t) * 100);
    const totalU = utilizations.reduce((a, b) => a + b, 0);

    // Liu & Layland bound for n = 3: 3 * (2^(1/3) - 1) = 77.98%
    const bound = 3 * (Math.pow(2, 1 / 3) - 1) * 100;
    const isGuaranteed = totalU <= bound;

    return { utilizations, totalU, bound, isGuaranteed };
  }, [tasks]);

  return (
    <div className="space-y-4">
      {/* 3-Task Inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {tasks.map((task, i) => (
          <div key={task.id} className="p-3 rounded-xl bg-[#041026] border border-slate-800 space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-white">Task {task.id}: {task.name}</span>
              <span className="text-[10px] text-indigo-400 font-bold">{schedData.utilizations[i].toFixed(1)}% CPU</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[10px]">
              <div>
                <label className="text-slate-400 block mb-0.5">Exec C{task.id} (ms)</label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={task.c}
                  onChange={(e) => handleUpdateTask(i, 'c', e.target.value)}
                  className="w-full p-1 rounded bg-[#020813] border border-slate-700 text-white text-xs"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-0.5">Period T{task.id} (ms)</label>
                <input
                  type="number"
                  min="5"
                  max="200"
                  value={task.t}
                  onChange={(e) => handleUpdateTask(i, 't', e.target.value)}
                  className="w-full p-1 rounded bg-[#020813] border border-slate-700 text-white text-xs"
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Schedulability Metric Verdict HUD */}
      <div className="p-4 rounded-xl bg-[#041026] border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <span className="text-slate-400 text-[10px] uppercase block font-bold">Total Processor Utilization:</span>
          <div className="flex items-baseline gap-2 mt-0.5">
            <span className={`text-xl font-extrabold font-sans ${schedData.isGuaranteed ? 'text-emerald-400' : 'text-rose-400'}`}>
              {schedData.totalU.toFixed(1)}%
            </span>
            <span className="text-slate-400 text-xs">/ Liu-Layland Bound: <strong>{schedData.bound.toFixed(2)}%</strong></span>
          </div>
        </div>

        <div className={`px-3 py-1.5 rounded-xl border text-xs font-bold ${schedData.isGuaranteed ? 'bg-emerald-950 text-emerald-300 border-emerald-500/50' : 'bg-rose-950 text-rose-300 border-rose-500/50'}`}>
          {schedData.isGuaranteed ? "✓ SCHEDULABLE UNDER RMS" : "⚠️ EXCEEDS BOUND (Analyze EDF / Hyperbolic)"}
        </div>
      </div>
    </div>
  );
}
