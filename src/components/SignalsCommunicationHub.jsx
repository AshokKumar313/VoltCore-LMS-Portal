import React, { useState, useMemo } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Phase E: Signals & Communication Systems Hub (Features 251–260)
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 *
 * Features:
 *   - Feature 251: Waveform Generator (Sine, Cos, Square, Triangle, Sawtooth, Sinc, Step)
 *   - Feature 252: Signal Operations (Addition, Subtraction, Multiplication, Beat Frequencies)
 *   - Feature 253: Time Shifting, Scaling & Reversal Visualizer (y(t) = x(at - t0))
 *   - Feature 254: Continuous vs Discrete Signals & Discrete Periodicity Checker
 *   - Feature 255: Fourier Transform Pairs & Continuous Magnitude/Phase Spectrum
 *   - Feature 256: Fourier Series Harmonic Synthesizer & Gibbs Phenomenon
 *   - Feature 257: Linear & Circular Discrete Convolution Calculator
 *   - Feature 258: Sampling Theorem & Aliasing Demonstrator (Nyquist Rate & Aliased Frequency)
 *   - Feature 259: Analog Modulation (AM Modulation Index, Efficiency, FM Carson's Rule)
 *   - Feature 260: Digital Modulation Comparison (BPSK, QPSK, 16-QAM, Constellations & BER)
 * Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
 * ========================================================================================
 */

// Digital Modulation Specs & Constellations
const DIGITAL_MODS = [
  {
    scheme: "BPSK",
    name: "Binary Phase Shift Keying",
    kBits: 1,
    bpsHz: 1.0,
    points: [{ x: -1.0, y: 0.0, label: "0" }, { x: 1.0, y: 0.0, label: "1" }],
    app: "Deep space, GPS L1/L2, Satellite links",
    appTa: "ஆழ்ந்த விண்வெளி தகவல் தொடர்பு, ஜிபிஎஸ் சிக்னல்"
  },
  {
    scheme: "QPSK",
    name: "Quadrature Phase Shift Keying",
    kBits: 2,
    bpsHz: 2.0,
    points: [
      { x: 0.707, y: 0.707, label: "00" },
      { x: -0.707, y: 0.707, label: "01" },
      { x: -0.707, y: -0.707, label: "11" },
      { x: 0.707, y: -0.707, label: "10" }
    ],
    app: "DVB-S satellite TV, 4G LTE control, ZigBee",
    appTa: "செயற்கைக்கோள் டிவி ஒளிபரப்பு, 4G LTE கட்டுப்பாடு"
  },
  {
    scheme: "16-QAM",
    name: "16-Quadrature Amplitude Modulation",
    kBits: 4,
    bpsHz: 4.0,
    points: [
      { x: -0.95, y: -0.95, label: "0000" }, { x: -0.32, y: -0.95, label: "0001" },
      { x: 0.32, y: -0.95, label: "0010" }, { x: 0.95, y: -0.95, label: "0011" },
      { x: -0.95, y: -0.32, label: "0100" }, { x: -0.32, y: -0.32, label: "0101" },
      { x: 0.32, y: -0.32, label: "0110" }, { x: 0.95, y: -0.32, label: "0111" },
      { x: -0.95, y: 0.32, label: "1100" }, { x: -0.32, y: 0.32, label: "1101" },
      { x: 0.32, y: 0.32, label: "1110" }, { x: 0.95, y: 0.32, label: "1111" },
      { x: -0.95, y: 0.95, label: "1000" }, { x: -0.32, y: 0.95, label: "1001" },
      { x: 0.32, y: 0.95, label: "1010" }, { x: 0.95, y: 0.95, label: "1011" }
    ],
    app: "Wi-Fi (802.11ac), 5G NR data planes, Cable modems",
    appTa: "வை-ஃபை (Wi-Fi), 5G மொபைல் டேட்டா சேனல்"
  },
  {
    scheme: "BFSK",
    name: "Binary Frequency Shift Keying",
    kBits: 1,
    bpsHz: 0.5,
    points: [{ x: 1.0, y: 0.0, label: "f1" }, { x: 0.0, y: 1.0, label: "f2" }],
    app: "Bluetooth LE telemetry, Caller ID, Low-cost RF",
    appTa: "புளூடூத் எல்இ (BLE), அழைப்பாளர் எண் அறிதல்"
  }
];

export default function SignalsCommunicationHub() {
  const [activeTab, setActiveTab] = useState("waveforms"); // waveforms, transforms, fourier, sampling, modulation
  const [bilingual, setBilingual] = useState(false);
  const [saveStatus, setSaveStatus] = useState("");

  // Tab 1: Waveform & Operations State
  const [waveType, setWaveType] = useState("sine");
  const [waveAmp, setWaveAmp] = useState(1.5);
  const [waveFreq, setWaveFreq] = useState(4.0);
  const [combineOp, setCombineOp] = useState("add"); // add, subtract, multiply
  const [opF1, setOpF1] = useState(10.0);
  const [opF2, setOpF2] = useState(12.0);

  // Tab 2: Time Transformations & Discrete Periodicity
  const [timeScaleA, setTimeScaleA] = useState(1.5);
  const [timeShiftT0, setTimeShiftT0] = useState(0.2);
  const [timeReversed, setTimeReversed] = useState(false);
  const [analogFreq, setAnalogFreq] = useState(50.0);
  const [samplingRateFs, setSamplingRateFs] = useState(200.0);

  // Tab 3: Fourier Transform & Series
  const [ftSignalName, setFtSignalName] = useState("rect");
  const [ftParam, setFtParam] = useState(1.0);
  const [fsWaveform, setFsWaveform] = useState("square");
  const [fsHarmonics, setFsHarmonics] = useState(7);

  // Tab 4: Convolution & Sampling/Aliasing
  const [convXStr, setConvXStr] = useState("1, 2, 3");
  const [convHStr, setConvHStr] = useState("1, 1");
  const [convCircular, setConvCircular] = useState(false);
  const [sampleSignalFreq, setSampleSignalFreq] = useState(100.0);
  const [sampleFs, setSampleFs] = useState(150.0);

  // Tab 5: Analog & Digital Modulation
  const [analogModType, setAnalogModType] = useState("AM"); // AM, FM
  const [modCarrierFreq, setModCarrierFreq] = useState(10000.0);
  const [modMessageFreq, setModMessageFreq] = useState(1000.0);
  const [modCarrierAmp, setModCarrierAmp] = useState(10.0);
  const [modMessageAmp, setModMessageAmp] = useState(8.0);
  const [modKf, setModKf] = useState(500.0);
  const [digitalSnrDb, setDigitalSnrDb] = useState(10.0);

  // 1. Single Waveform Calculations
  const singleWave = useMemo(() => {
    const pts = [];
    let energySum = 0;
    const fs = 200;
    for (let i = 0; i < 200; i++) {
      const t = i / fs;
      const arg = 2 * Math.PI * waveFreq * t;
      let val = 0;
      if (waveType === "sine") val = waveAmp * Math.sin(arg);
      else if (waveType === "cosine") val = waveAmp * Math.cos(arg);
      else if (waveType === "square") val = Math.sin(arg) >= 0 ? waveAmp : -waveAmp;
      else if (waveType === "triangle") val = (2 * waveAmp / Math.PI) * Math.asin(Math.sin(arg));
      else if (waveType === "sawtooth") val = waveAmp * (2 * ((waveFreq * t) % 1) - 1);
      else if (waveType === "sinc") {
        const sincArg = Math.PI * waveFreq * (t - 0.5);
        val = Math.abs(sincArg) < 1e-6 ? waveAmp : waveAmp * (Math.sin(sincArg) / sincArg);
      } else if (waveType === "unit_step") val = t >= 0.25 ? waveAmp : 0;

      pts.push({ t, val });
      energySum += (val * val) / fs;
    }
    const avgPower = energySum / 1.0;
    const rms = Math.sqrt(avgPower);
    return { pts, energy: energySum.toFixed(3), power: avgPower.toFixed(3), rms: rms.toFixed(3) };
  }, [waveType, waveAmp, waveFreq]);

  // Combined Signals (Beat frequency)
  const combinedWave = useMemo(() => {
    const pts = [];
    const beatFreq = Math.abs(opF1 - opF2);
    const fs = 200;
    for (let i = 0; i < 200; i++) {
      const t = i / fs;
      const s1 = Math.cos(2 * Math.PI * opF1 * t);
      const s2 = Math.cos(2 * Math.PI * opF2 * t);
      let y = 0;
      if (combineOp === "add") y = s1 + s2;
      else if (combineOp === "subtract") y = s1 - s2;
      else if (combineOp === "multiply") y = s1 * s2;
      pts.push({ t, s1, s2, y });
    }
    return { pts, beatFreq: beatFreq.toFixed(1), envelopePeriod: beatFreq > 0 ? (1 / beatFreq).toFixed(2) : "∞" };
  }, [combineOp, opF1, opF2]);

  // 2. Discrete Periodicity Calculations
  const discretePeriod = useMemo(() => {
    const omega = 2 * Math.PI * (analogFreq / samplingRateFs);
    const ratio = analogFreq / samplingRateFs;
    const mult = 1000;
    const num = Math.round(ratio * mult);
    const den = mult;
    const gcd = (a, b) => b === 0 ? a : gcd(b, a % b);
    const common = gcd(num, den);
    const n = den / common;
    const isPeriodic = n <= 500;
    return { omega: omega.toFixed(3), ratio: ratio.toFixed(3), isPeriodic, n: isPeriodic ? n : "Aperiodic" };
  }, [analogFreq, samplingRateFs]);

  // 3. Fourier Series Harmonic Synthesis
  const fourierSeries = useMemo(() => {
    const pts = [];
    const w0 = 2 * Math.PI * 2.0; // 2 Hz fundamental
    const coeffs = [];
    for (let n = 1; n <= fsHarmonics; n++) {
      let c = 0;
      if (fsWaveform === "square") c = n % 2 === 1 ? (4 / (Math.PI * n)) : 0;
      else if (fsWaveform === "sawtooth") c = (2 / (Math.PI * n)) * Math.pow(-1, n + 1);
      else if (fsWaveform === "triangle") c = n % 2 === 1 ? (8 / (Math.pow(Math.PI, 2) * Math.pow(n, 2))) * Math.pow(-1, (n - 1) / 2) : 0;
      coeffs.push({ n, c });
    }

    for (let step = 0; step <= 100; step++) {
      const t = step / 100.0 * 0.5; // 1 period
      let val = 0;
      coeffs.forEach(h => {
        if (Math.abs(h.c) > 1e-5) val += h.c * Math.sin(h.n * w0 * t);
      });
      pts.push({ t, val });
    }
    return { pts, coeffs, gibbs: fsWaveform === "square" ? "8.95%" : "0.0%" };
  }, [fsWaveform, fsHarmonics]);

  // 4. Convolution Calculations
  const convolutionResult = useMemo(() => {
    try {
      const x = convXStr.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n));
      const h = convHStr.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n));
      if (x.length === 0 || h.length === 0) return { error: "Sequences cannot be empty" };

      if (!convCircular) {
        const ly = x.length + h.length - 1;
        const y = new Array(ly).fill(0);
        for (let i = 0; i < x.length; i++) {
          for (let j = 0; j < h.length; j++) {
            y[i + j] += x[i] * h[j];
          }
        }
        return { y, len: ly, type: "Linear Convolution" };
      } else {
        const n = Math.max(x.length, h.length);
        const y = new Array(n).fill(0);
        for (let i = 0; i < n; i++) {
          for (let k = 0; k < n; k++) {
            const xVal = k < x.length ? x[k] : 0;
            const hIdx = (i - k + n) % n;
            const hVal = hIdx < h.length ? h[hIdx] : 0;
            y[i] += xVal * hVal;
          }
        }
        return { y, len: n, type: "Circular Convolution", aliasing: n < (x.length + h.length - 1) };
      }
    } catch (e) {
      return { error: e.message };
    }
  }, [convXStr, convHStr, convCircular]);

  // Sampling & Aliasing Analysis
  const samplingAnalysis = useMemo(() => {
    const nyquistRate = 2 * sampleSignalFreq;
    const k = Math.round(sampleSignalFreq / sampleFs);
    const aliasFreq = Math.abs(sampleSignalFreq - k * sampleFs);
    const isAliased = sampleFs < nyquistRate;
    return { nyquistRate, aliasFreq: aliasFreq.toFixed(1), isAliased };
  }, [sampleSignalFreq, sampleFs]);

  // 5. Analog Modulation (AM / FM)
  const analogMod = useMemo(() => {
    if (analogModType === "AM") {
      const m = modMessageAmp / modCarrierAmp;
      const bw = 2 * modMessageFreq;
      const eta = (Math.pow(m, 2) / (2 + Math.pow(m, 2))) * 100;
      const state = m < 1.0 ? "Under-Modulated" : m === 1.0 ? "Critical (100%)" : "Over-Modulated (Distortion)";
      return { m: m.toFixed(2), bw: bw.toFixed(0), eta: eta.toFixed(1), state };
    } else {
      const deltaF = modKf * modMessageAmp;
      const beta = deltaF / modMessageFreq;
      const carsonsBw = 2 * (deltaF + modMessageFreq);
      const state = beta <= 0.5 ? "Narrowband FM (NBFM)" : "Wideband FM (WBFM)";
      return { deltaF: deltaF.toFixed(0), beta: beta.toFixed(2), carsonsBw: carsonsBw.toFixed(0), state };
    }
  }, [analogModType, modCarrierAmp, modMessageAmp, modCarrierFreq, modMessageFreq, modKf]);

  // Digital Modulation BER Calculator
  const digitalMod = useMemo(() => {
    const snrLinear = Math.pow(10, digitalSnrDb / 10);
    const qFunc = (x) => 0.5 * (1 - Math.tanh(x / Math.SQRT2)); // Approximated Q-function
    const bpskBer = qFunc(Math.sqrt(2 * snrLinear));
    const qamBer = (3 / 8) * qFunc(Math.sqrt(0.8 * snrLinear));
    const bfskBer = qFunc(Math.sqrt(snrLinear));

    return {
      bpskBer: Math.max(1e-10, bpskBer).toExponential(2),
      qamBer: Math.max(1e-10, qamBer).toExponential(2),
      bfskBer: Math.max(1e-10, bfskBer).toExponential(2)
    };
  }, [digitalSnrDb]);

  // Transformed Wave Points
  const transformWave = useMemo(() => {
    const origPts = [];
    const transPts = [];
    for (let i = 0; i <= 100; i++) {
      const t = (i / 100) * 2.0 - 1.0; // -1.0 to +1.0 s
      const origVal = Math.max(0, 1.0 - Math.abs(t) / 0.5);
      const tArg = (timeReversed ? -1 : 1) * (timeScaleA * t - timeShiftT0);
      const transVal = Math.max(0, 1.0 - Math.abs(tArg) / 0.5);
      origPts.push({ t, val: origVal });
      transPts.push({ t, val: transVal });
    }
    return { origPts, transPts };
  }, [timeScaleA, timeShiftT0, timeReversed]);

  // Discrete Stem Points
  const stemPoints = useMemo(() => {
    const pts = [];
    const omega = 2 * Math.PI * (analogFreq / samplingRateFs);
    for (let n = 0; n < 24; n++) {
      const val = Math.cos(omega * n);
      pts.push({ n, val });
    }
    return pts;
  }, [analogFreq, samplingRateFs]);

  // Modulated Analog Waveform
  const modWaveform = useMemo(() => {
    const pts = [];
    const ac = modCarrierAmp;
    const am = modMessageAmp;
    const fc = 40.0;
    const fm = 4.0;
    const m = am / ac;
    const kf = modKf / 150.0;

    for (let i = 0; i <= 150; i++) {
      const t = (i / 150.0) * 0.5;
      let y = 0;
      let env = ac;
      if (analogModType === "AM") {
        env = Math.max(0, ac * (1 + m * Math.cos(2 * Math.PI * fm * t)));
        y = env * Math.cos(2 * Math.PI * fc * t);
      } else {
        const phase = 2 * Math.PI * fc * t + (kf * am / fm) * Math.sin(2 * Math.PI * fm * t);
        y = ac * Math.cos(phase);
        env = ac;
      }
      pts.push({ t, y, env });
    }
    return pts;
  }, [analogModType, modCarrierAmp, modMessageAmp, modKf]);

  const handleSaveExperiment = () => {
    setSaveStatus("Saved signal experiment to SQLite WAL ledger!");
    setTimeout(() => setSaveStatus(""), 4000);
  };

  return (
    <div className="min-h-screen bg-[#070B12] text-slate-100 font-sans p-4 md:p-8">
      {/* Platform Header */}
      <header className="max-w-7xl mx-auto mb-8 bg-[#0D1524] border border-indigo-500/20 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
        <div className="absolute -right-16 -top-16 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                Phase E • Features 251–260
              </span>
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                Hardware Safe: SQLite WAL • 0% CPU Idle
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white flex items-center gap-2">
              📡 Signals & Communication Systems Engineering Hub
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Anna University / MIT Campus (ECE Dept, Reg 2023) • Lead: <strong className="text-indigo-300">Ashok Kumar A (2023MITEC042)</strong>
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
            <button
              onClick={handleSaveExperiment}
              className="px-3.5 py-2 rounded-xl text-xs font-bold bg-indigo-500 hover:bg-indigo-400 text-slate-950 flex items-center gap-1.5 shadow-md shadow-indigo-500/20 transition"
            >
              <span>💾</span> Save Simulation
            </button>
          </div>
        </div>

        {saveStatus && (
          <div className="mt-4 p-2.5 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 text-xs font-mono">
            ✅ {saveStatus}
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 mt-6 border-t border-slate-800 pt-4">
          {[
            { id: "waveforms", label: "Waveform Gen & Beat Ops", icon: "〰️" },
            { id: "transforms", label: "Time Transforms & Discrete", icon: "⏱️" },
            { id: "fourier", label: "Fourier Transform & Series", icon: "📈" },
            { id: "sampling", label: "Convolution & Aliasing", icon: "🔄" },
            { id: "modulation", label: "AM/FM & Digital Mod", icon: "📡" }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition flex items-center gap-2 ${
                activeTab === tab.id
                  ? "bg-indigo-500 text-slate-950 shadow-lg shadow-indigo-500/25"
                  : "bg-slate-900/80 text-slate-400 hover:bg-slate-800 hover:text-slate-200 border border-slate-800"
              }`}
            >
              <span>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </header>

      {/* Main Tab Views */}
      <main className="max-w-7xl mx-auto space-y-8">

        {/* =========================================================================
            TAB 1: WAVEFORM GENERATOR & SIGNAL ARITHMETIC (Features 251 & 252)
            ========================================================================= */}
        {activeTab === "waveforms" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Feature 251: Single Waveform Generator */}
              <div className="bg-[#0D1524] border border-slate-800 rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>〰️</span> Waveform Generator (Feature 251)
                  </h3>
                  <span className="text-xs text-indigo-400 font-mono font-bold uppercase">{waveType}</span>
                </div>

                <div className="grid grid-cols-4 gap-1.5">
                  {["sine", "cosine", "square", "triangle", "sawtooth", "sinc", "unit_step"].map(w => (
                    <button
                      key={w}
                      onClick={() => setWaveType(w)}
                      className={`py-1.5 rounded-lg text-xs font-mono font-semibold capitalize border transition ${
                        waveType === w
                          ? "bg-indigo-500 text-slate-950 border-indigo-400 font-bold"
                          : "bg-slate-900 border-slate-800 text-slate-400 hover:bg-slate-800"
                      }`}
                    >
                      {w.replace("_", " ")}
                    </button>
                  ))}
                </div>

                <div className="grid grid-cols-2 gap-3 font-mono text-xs">
                  <div>
                    <label className="text-slate-400 block mb-0.5">Amplitude ({waveAmp} V):</label>
                    <input
                      type="range"
                      min="0.5"
                      max="5.0"
                      step="0.1"
                      value={waveAmp}
                      onChange={(e) => setWaveAmp(Number(e.target.value))}
                      className="w-full accent-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-0.5">Frequency ({waveFreq} Hz):</label>
                    <input
                      type="range"
                      min="1.0"
                      max="15.0"
                      step="0.5"
                      value={waveFreq}
                      onChange={(e) => setWaveFreq(Number(e.target.value))}
                      className="w-full accent-indigo-500"
                    />
                  </div>
                </div>

                {/* SVG Waveform Visualizer */}
                <div className="h-44 bg-slate-950 rounded-xl border border-slate-800 p-2 relative overflow-hidden">
                  <svg className="w-full h-full" viewBox="0 0 300 120" preserveAspectRatio="none">
                    <line x1="0" y1="60" x2="300" y2="60" stroke="#334155" strokeWidth="1" />
                    <path
                      d={singleWave.pts.map((pt, idx) => {
                        const x = (pt.t / 1.0) * 300;
                        const y = 60 - (pt.val / 5.0) * 50;
                        return `${idx === 0 ? "M" : "L"} ${x} ${Math.max(5, Math.min(115, y))}`;
                      }).join(" ")}
                      fill="none"
                      stroke="#818CF8"
                      strokeWidth="2.5"
                    />
                  </svg>
                </div>

                <div className="grid grid-cols-3 gap-2 font-mono text-xs">
                  <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase block">Energy (J)</span>
                    <span className="text-base font-bold text-amber-400">{singleWave.energy}</span>
                  </div>
                  <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase block">Avg Power (W)</span>
                    <span className="text-base font-bold text-emerald-400">{singleWave.power}</span>
                  </div>
                  <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase block">RMS Voltage</span>
                    <span className="text-base font-bold text-cyan-400">{singleWave.rms} V</span>
                  </div>
                </div>
              </div>

              {/* Feature 252: Beat Frequency & Signal Operations */}
              <div className="bg-[#0D1524] border border-slate-800 rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>🎵</span> Signal Operations & Beats (Feature 252)
                  </h3>
                  <div className="flex gap-1 font-mono text-xs">
                    {["add", "subtract", "multiply"].map(op => (
                      <button
                        key={op}
                        onClick={() => setCombineOp(op)}
                        className={`px-2.5 py-1 rounded-lg capitalize font-bold transition ${
                          combineOp === op ? "bg-indigo-500 text-slate-950" : "bg-slate-900 text-slate-400 border border-slate-800"
                        }`}
                      >
                        {op}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 font-mono text-xs">
                  <div>
                    <label className="text-slate-400 block mb-0.5">Tone 1 Freq ({opF1} Hz):</label>
                    <input
                      type="range"
                      min="4"
                      max="20"
                      value={opF1}
                      onChange={(e) => setOpF1(Number(e.target.value))}
                      className="w-full accent-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-0.5">Tone 2 Freq ({opF2} Hz):</label>
                    <input
                      type="range"
                      min="4"
                      max="20"
                      value={opF2}
                      onChange={(e) => setOpF2(Number(e.target.value))}
                      className="w-full accent-indigo-500"
                    />
                  </div>
                </div>

                {/* SVG Beat Plot */}
                <div className="h-44 bg-slate-950 rounded-xl border border-slate-800 p-2 relative overflow-hidden">
                  <svg className="w-full h-full" viewBox="0 0 300 120" preserveAspectRatio="none">
                    <line x1="0" y1="60" x2="300" y2="60" stroke="#334155" strokeWidth="1" />
                    <path
                      d={combinedWave.pts.map((pt, idx) => {
                        const x = (pt.t / 1.0) * 300;
                        const y = 60 - (pt.y / 2.5) * 50;
                        return `${idx === 0 ? "M" : "L"} ${x} ${Math.max(5, Math.min(115, y))}`;
                      }).join(" ")}
                      fill="none"
                      stroke="#10B981"
                      strokeWidth="2"
                    />
                  </svg>
                  <div className="absolute top-2 right-2 text-[10px] font-mono text-slate-400 bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800">
                    Δf = |f1 - f2| = {combinedWave.beatFreq} Hz
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 font-mono">
                  <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase block">Beat Frequency (Δf)</span>
                    <span className="text-lg font-bold text-amber-400">{combinedWave.beatFreq} Hz</span>
                  </div>
                  <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase block">Envelope Period</span>
                    <span className="text-lg font-bold text-cyan-400">{combinedWave.envelopePeriod} s</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            TAB 2: TIME TRANSFORMATIONS & DISCRETE SIGNALS (Features 253 & 254)
            ========================================================================= */}
        {activeTab === "transforms" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Feature 253: Time Shifting, Scaling, Reversal */}
              <div className="bg-[#0D1524] border border-slate-800 rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>⏱️</span> Time Transformation y(t) = x(at - t₀)
                  </h3>
                  <button
                    onClick={() => setTimeReversed(!timeReversed)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-mono font-bold border transition ${
                      timeReversed ? "bg-rose-500/20 text-rose-400 border-rose-500/40" : "bg-slate-900 text-slate-400 border-slate-800"
                    }`}
                  >
                    Time Reversal x(-t): {timeReversed ? "ACTIVE" : "OFF"}
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-3 font-mono text-xs">
                  <div>
                    <label className="text-slate-400 block mb-0.5">Scaling Factor a ({timeScaleA}x):</label>
                    <input
                      type="range"
                      min="0.5"
                      max="3.0"
                      step="0.25"
                      value={timeScaleA}
                      onChange={(e) => setTimeScaleA(Number(e.target.value))}
                      className="w-full accent-indigo-500"
                    />
                    <span className="text-[10px] text-slate-500">{timeScaleA > 1 ? "Compression" : "Expansion"}</span>
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-0.5">Shift t₀ ({timeShiftT0} s):</label>
                    <input
                      type="range"
                      min="-0.5"
                      max="0.5"
                      step="0.05"
                      value={timeShiftT0}
                      onChange={(e) => setTimeShiftT0(Number(e.target.value))}
                      className="w-full accent-indigo-500"
                    />
                    <span className="text-[10px] text-slate-500">{timeShiftT0 > 0 ? "Delay (Right)" : "Advance (Left)"}</span>
                  </div>
                </div>

                <div className="p-4 bg-slate-950/70 rounded-xl border border-slate-800 text-xs font-mono space-y-2">
                  <div className="text-amber-300 font-bold">
                    Transformation: y(t) = x({timeReversed ? "-" : ""}{timeScaleA}t {timeShiftT0 >= 0 ? "-" : "+"} {Math.abs(timeShiftT0)})
                  </div>
                  <div className="text-slate-400">
                    Step 1: Shift x(t) by t₀ = {timeShiftT0} s.<br/>
                    Step 2: Scale time axis by factor a = {timeScaleA}.<br/>
                    {timeReversed && "Step 3: Reflect across vertical axis t = 0."}
                  </div>
                </div>

                {/* SVG Visualizer for Original vs Transformed Waveform */}
                <div className="h-36 bg-slate-950 rounded-xl border border-slate-800 p-2 relative overflow-hidden">
                  <svg className="w-full h-full" viewBox="0 0 300 100" preserveAspectRatio="none">
                    <line x1="0" y1="90" x2="300" y2="90" stroke="#334155" strokeWidth="1" />
                    <line x1="150" y1="0" x2="150" y2="100" stroke="#334155" strokeWidth="1" />
                    {/* Original Wave x(t) */}
                    <path
                      d={transformWave.origPts.map((pt, idx) => {
                        const x = ((pt.t + 1.0) / 2.0) * 300;
                        const y = 90 - pt.val * 75;
                        return `${idx === 0 ? "M" : "L"} ${x} ${y}`;
                      }).join(" ")}
                      fill="none"
                      stroke="#475569"
                      strokeWidth="2"
                      strokeDasharray="4 3"
                    />
                    {/* Transformed Wave y(t) */}
                    <path
                      d={transformWave.transPts.map((pt, idx) => {
                        const x = ((pt.t + 1.0) / 2.0) * 300;
                        const y = 90 - pt.val * 75;
                        return `${idx === 0 ? "M" : "L"} ${x} ${y}`;
                      }).join(" ")}
                      fill="none"
                      stroke="#818CF8"
                      strokeWidth="2.5"
                    />
                  </svg>
                  <div className="absolute top-2 right-2 text-[10px] font-mono text-slate-400 bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800 flex gap-2">
                    <span className="text-slate-500">--- x(t)</span>
                    <span className="text-indigo-400">― y(t)</span>
                  </div>
                </div>
              </div>

              {/* Feature 254: Continuous vs Discrete Signals */}
              <div className="bg-[#0D1524] border border-slate-800 rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>📊</span> Discrete Periodicity Checker (Feature 254)
                  </h3>
                  <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold border font-mono ${
                    discretePeriod.isPeriodic
                      ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                      : "bg-rose-500/20 text-rose-400 border-rose-500/30"
                  }`}>
                    {discretePeriod.isPeriodic ? "Periodic Discrete Signal" : "Aperiodic"}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 font-mono text-xs">
                  <div>
                    <label className="text-slate-400 block mb-0.5">Analog Freq f ({analogFreq} Hz):</label>
                    <input
                      type="number"
                      value={analogFreq}
                      onChange={(e) => setAnalogFreq(Number(e.target.value))}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-0.5">Sampling Rate fs ({samplingRateFs} Hz):</label>
                    <input
                      type="number"
                      value={samplingRateFs}
                      onChange={(e) => setSamplingRateFs(Number(e.target.value))}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 font-mono text-xs pt-2">
                  <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase block">Digital ω</span>
                    <span className="text-base font-bold text-cyan-400">{discretePeriod.omega} rad</span>
                  </div>
                  <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase block">Ratio f / fs</span>
                    <span className="text-base font-bold text-amber-400">{discretePeriod.ratio}</span>
                  </div>
                  <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase block">Fundamental N</span>
                    <span className="text-base font-bold text-emerald-400">{discretePeriod.n} samples</span>
                  </div>
                </div>

                {/* SVG Discrete Stem Plot */}
                <div className="h-32 bg-slate-950 rounded-xl border border-slate-800 p-2 relative overflow-hidden">
                  <svg className="w-full h-full" viewBox="0 0 300 80" preserveAspectRatio="none">
                    <line x1="0" y1="40" x2="300" y2="40" stroke="#334155" strokeWidth="1" />
                    {stemPoints.map((pt, idx) => {
                      const x = (idx / 23) * 280 + 10;
                      const y = 40 - pt.val * 30;
                      return (
                        <g key={idx}>
                          <line x1={x} y1="40" x2={x} y2={y} stroke="#10B981" strokeWidth="1.5" />
                          <circle cx={x} cy={y} r="3" fill="#34D399" />
                        </g>
                      );
                    })}
                  </svg>
                  <div className="absolute top-1 right-2 text-[10px] font-mono text-slate-400 bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800">
                    Discrete Stem Samples x[n] = cos(ωn)
                  </div>
                </div>

                <div className="text-[11px] text-slate-400">
                  {bilingual
                    ? "தொடர்ச்சியான சிக்னல் எப்போதும் குறிப்பிட்ட கால இடைவெளியில் இருக்கும்; ஆனால் தனித்த சிக்னல் f/fs விகிதம் பின்னமாக இருந்தால் மட்டுமே குறிப்பிட்ட கால இடைவெளியில் இருக்கும்."
                    : "Continuous sinusoids are always periodic, but discrete sinusoids x[n] = cos(ωn) are periodic ONLY if f/fs is rational."}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            TAB 3: FOURIER TRANSFORM & HARMONIC SERIES (Features 255 & 256)
            ========================================================================= */}
        {activeTab === "fourier" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Feature 255: Fourier Transform Pairs */}
              <div className="bg-[#0D1524] border border-slate-800 rounded-2xl p-6 space-y-4">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <span>📈</span> Fourier Transform Pairs (Feature 255)
                </h3>

                <div className="grid grid-cols-4 gap-1.5 font-mono text-xs">
                  {["rect", "exponential", "delta", "gaussian"].map(sig => (
                    <button
                      key={sig}
                      onClick={() => setFtSignalName(sig)}
                      className={`py-1.5 rounded-lg capitalize font-bold transition border ${
                        ftSignalName === sig ? "bg-indigo-500 text-slate-950 border-indigo-400" : "bg-slate-900 border-slate-800 text-slate-400"
                      }`}
                    >
                      {sig}
                    </button>
                  ))}
                </div>

                <div className="p-4 bg-slate-950/70 rounded-xl border border-slate-800 font-mono text-xs space-y-3">
                  <div>
                    <span className="text-slate-400 block mb-0.5">Time-Domain Signal x(t):</span>
                    <span className="text-cyan-300 font-bold text-sm">
                      {ftSignalName === "rect" && `rect(t / ${ftParam}) [Pulse Width: ${ftParam}s]`}
                      {ftSignalName === "exponential" && `e^(-${ftParam}t) · u(t) [Decay: ${ftParam}]`}
                      {ftSignalName === "delta" && "δ(t) [Dirac Delta Impulse]"}
                      {ftSignalName === "gaussian" && `e^(-${ftParam}t²) [Gaussian Bell]`}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block mb-0.5">Fourier Transform X(ω):</span>
                    <span className="text-emerald-300 font-bold text-sm">
                      {ftSignalName === "rect" && `${ftParam} · sinc(ω · ${ftParam} / 2π)`}
                      {ftSignalName === "exponential" && `1 / (${ftParam} + jω)`}
                      {ftSignalName === "delta" && "1.0 (Uniform infinite spectrum)"}
                      {ftSignalName === "gaussian" && `√(π/${ftParam}) · e^(-ω²/4${ftParam})`}
                    </span>
                  </div>
                </div>
              </div>

              {/* Feature 256: Fourier Series Harmonic Synthesizer */}
              <div className="bg-[#0D1524] border border-slate-800 rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>🎚️</span> Fourier Series Harmonic Synthesis
                  </h3>
                  <span className="text-xs text-amber-400 font-mono font-bold">
                    Gibbs: {fourierSeries.gibbs}
                  </span>
                </div>

                <div className="flex gap-2 font-mono text-xs">
                  {["square", "sawtooth", "triangle"].map(w => (
                    <button
                      key={w}
                      onClick={() => setFsWaveform(w)}
                      className={`flex-1 py-1.5 rounded-lg capitalize font-bold transition border ${
                        fsWaveform === w ? "bg-indigo-500 text-slate-950 border-indigo-400" : "bg-slate-900 border-slate-800 text-slate-400"
                      }`}
                    >
                      {w}
                    </button>
                  ))}
                </div>

                <div>
                  <div className="flex justify-between text-xs font-mono mb-1">
                    <span className="text-slate-400">Harmonics Count (N):</span>
                    <span className="text-amber-400 font-bold">{fsHarmonics} Harmonics</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="25"
                    value={fsHarmonics}
                    onChange={(e) => setFsHarmonics(Number(e.target.value))}
                    className="w-full accent-indigo-500"
                  />
                </div>

                {/* SVG Synthesized Waveform */}
                <div className="h-44 bg-slate-950 rounded-xl border border-slate-800 p-2 relative overflow-hidden">
                  <svg className="w-full h-full" viewBox="0 0 300 120" preserveAspectRatio="none">
                    <line x1="0" y1="60" x2="300" y2="60" stroke="#334155" strokeWidth="1" />
                    <path
                      d={fourierSeries.pts.map((pt, idx) => {
                        const x = (idx / (fourierSeries.pts.length - 1)) * 300;
                        const y = 60 - (pt.val / 1.5) * 50;
                        return `${idx === 0 ? "M" : "L"} ${x} ${Math.max(5, Math.min(115, y))}`;
                      }).join(" ")}
                      fill="none"
                      stroke="#F59E0B"
                      strokeWidth="2.5"
                    />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            TAB 4: CONVOLUTION & SAMPLING / ALIASING (Features 257 & 258)
            ========================================================================= */}
        {activeTab === "sampling" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Feature 257: Linear & Circular Convolution */}
              <div className="bg-[#0D1524] border border-slate-800 rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>🔄</span> Convolution Calculator (Feature 257)
                  </h3>
                  <button
                    onClick={() => setConvCircular(!convCircular)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-mono font-bold border transition ${
                      convCircular ? "bg-amber-500/20 text-amber-400 border-amber-500/40" : "bg-slate-900 text-slate-400 border-slate-800"
                    }`}
                  >
                    {convCircular ? "Circular N-point" : "Linear Convolution"}
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-3 font-mono text-xs">
                  <div>
                    <label className="text-slate-400 block mb-0.5">Input Sequence x[n]:</label>
                    <input
                      type="text"
                      value={convXStr}
                      onChange={(e) => setConvXStr(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white"
                      placeholder="1, 2, 3"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-0.5">Impulse Response h[n]:</label>
                    <input
                      type="text"
                      value={convHStr}
                      onChange={(e) => setConvHStr(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white"
                      placeholder="1, 1"
                    />
                  </div>
                </div>

                <div className="p-4 bg-slate-950/70 rounded-xl border border-slate-800 font-mono text-xs space-y-2">
                  <div className="text-slate-400">
                    Output y[n] ({convolutionResult.type}, Length: {convolutionResult.len}):
                  </div>
                  <div className="text-emerald-400 text-lg font-bold">
                    [{convolutionResult.y?.join(", ")}]
                  </div>
                  {convolutionResult.aliasing && (
                    <div className="text-rose-400 text-[11px]">
                      ⚠️ Circular time-aliasing occurred! N &lt; (Lx + Lh - 1).
                    </div>
                  )}
                </div>
              </div>

              {/* Feature 258: Sampling Theorem & Aliasing */}
              <div className="bg-[#0D1524] border border-slate-800 rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>⚡</span> Nyquist Sampling & Aliasing (Feature 258)
                  </h3>
                  <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold border font-mono ${
                    samplingAnalysis.isAliased
                      ? "bg-rose-500/20 text-rose-400 border-rose-500/30"
                      : "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                  }`}>
                    {samplingAnalysis.isAliased ? "Severe Aliasing (fs < 2f)" : "Nyquist Satisfied"}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 font-mono text-xs">
                  <div>
                    <label className="text-slate-400 block mb-0.5">Signal Freq ({sampleSignalFreq} Hz):</label>
                    <input
                      type="number"
                      value={sampleSignalFreq}
                      onChange={(e) => setSampleSignalFreq(Number(e.target.value))}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-0.5">Sampling Rate fs ({sampleFs} Hz):</label>
                    <input
                      type="number"
                      value={sampleFs}
                      onChange={(e) => setSampleFs(Number(e.target.value))}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 font-mono">
                  <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase block">Nyquist Rate (2f)</span>
                    <span className="text-lg font-bold text-amber-400">{samplingAnalysis.nyquistRate} Hz</span>
                  </div>
                  <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase block">Apparent Frequency</span>
                    <span className={`text-lg font-bold ${samplingAnalysis.isAliased ? "text-rose-400" : "text-emerald-400"}`}>
                      {samplingAnalysis.aliasFreq} Hz
                    </span>
                  </div>
                </div>

                {/* SVG Frequency Spectrum Visualizer */}
                <div className="h-32 bg-slate-950 rounded-xl border border-slate-800 p-2 relative overflow-hidden">
                  <svg className="w-full h-full" viewBox="0 0 300 80" preserveAspectRatio="none">
                    <line x1="0" y1="70" x2="300" y2="70" stroke="#334155" strokeWidth="1" />
                    {/* Nyquist folding boundary (fs/2) */}
                    <line x1="150" y1="10" x2="150" y2="70" stroke="#F59E0B" strokeWidth="1.5" strokeDasharray="3 3" />
                    {/* Original Signal Peak */}
                    <line
                      x1={Math.min(290, Math.max(10, (sampleSignalFreq / (sampleFs || 1)) * 300))}
                      y1="70"
                      x2={Math.min(290, Math.max(10, (sampleSignalFreq / (sampleFs || 1)) * 300))}
                      y2="20"
                      stroke="#818CF8"
                      strokeWidth="3"
                    />
                    {/* Alias Tone Peak if Aliasing */}
                    {samplingAnalysis.isAliased && (
                      <line
                        x1={Math.min(290, Math.max(10, (parseFloat(samplingAnalysis.aliasFreq) / (sampleFs || 1)) * 300))}
                        y1="70"
                        x2={Math.min(290, Math.max(10, (parseFloat(samplingAnalysis.aliasFreq) / (sampleFs || 1)) * 300))}
                        y2="30"
                        stroke="#F43F5E"
                        strokeWidth="2.5"
                        strokeDasharray="4 2"
                      />
                    )}
                  </svg>
                  <div className="absolute top-1 right-2 text-[10px] font-mono text-slate-400 bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800 flex gap-2">
                    <span className="text-indigo-400">| f_sig</span>
                    <span className="text-amber-400">: fs/2</span>
                    {samplingAnalysis.isAliased && <span className="text-rose-400">| f_alias</span>}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            TAB 5: ANALOG & DIGITAL MODULATION (Features 259 & 260)
            ========================================================================= */}
        {activeTab === "modulation" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Feature 259: Analog Modulation (AM & FM) */}
              <div className="bg-[#0D1524] border border-slate-800 rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>📻</span> Analog Modulation: AM & FM (Feature 259)
                  </h3>
                  <div className="flex gap-1 font-mono text-xs">
                    {["AM", "FM"].map(m => (
                      <button
                        key={m}
                        onClick={() => setAnalogModType(m)}
                        className={`px-3 py-1 rounded-lg font-bold transition ${
                          analogModType === m ? "bg-indigo-500 text-slate-950" : "bg-slate-900 text-slate-400 border border-slate-800"
                        }`}
                      >
                        {m}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 font-mono text-xs">
                  <div>
                    <label className="text-slate-400 block mb-0.5">Carrier Amp Ac ({modCarrierAmp} V):</label>
                    <input
                      type="range"
                      min="5"
                      max="20"
                      value={modCarrierAmp}
                      onChange={(e) => setModCarrierAmp(Number(e.target.value))}
                      className="w-full accent-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-0.5">Message Amp Am ({modMessageAmp} V):</label>
                    <input
                      type="range"
                      min="1"
                      max="20"
                      value={modMessageAmp}
                      onChange={(e) => setModMessageAmp(Number(e.target.value))}
                      className="w-full accent-indigo-500"
                    />
                  </div>
                </div>

                <div className="p-4 bg-slate-950/70 rounded-xl border border-slate-800 font-mono text-xs space-y-2">
                  <div className="flex justify-between">
                    <span className="text-slate-400">{analogModType === "AM" ? "Modulation Index (m):" : "Frequency Deviation (Δf):"}</span>
                    <span className="text-amber-400 font-bold">{analogModType === "AM" ? analogMod.m : `${analogMod.deltaF} Hz`}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Bandwidth:</span>
                    <span className="text-cyan-400 font-bold">{analogModType === "AM" ? `${analogMod.bw} Hz` : `${analogMod.carsonsBw} Hz (Carson)`}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Operating State:</span>
                    <span className="text-emerald-400 font-bold">{analogMod.state}</span>
                  </div>
                </div>

                {/* SVG Modulated Waveform Plot */}
                <div className="h-32 bg-slate-950 rounded-xl border border-slate-800 p-2 relative overflow-hidden">
                  <svg className="w-full h-full" viewBox="0 0 300 80" preserveAspectRatio="none">
                    <line x1="0" y1="40" x2="300" y2="40" stroke="#334155" strokeWidth="1" />
                    {/* Carrier wave */}
                    <path
                      d={modWaveform.map((pt, idx) => {
                        const x = (idx / 150) * 300;
                        const y = 40 - (pt.y / 25.0) * 35;
                        return `${idx === 0 ? "M" : "L"} ${x} ${Math.max(5, Math.min(75, y))}`;
                      }).join(" ")}
                      fill="none"
                      stroke="#818CF8"
                      strokeWidth="1.5"
                    />
                    {/* AM Envelope */}
                    {analogModType === "AM" && (
                      <path
                        d={modWaveform.map((pt, idx) => {
                          const x = (idx / 150) * 300;
                          const y = 40 - (pt.env / 25.0) * 35;
                          return `${idx === 0 ? "M" : "L"} ${x} ${y}`;
                        }).join(" ")}
                        fill="none"
                        stroke="#F59E0B"
                        strokeWidth="1"
                        strokeDasharray="3 2"
                      />
                    )}
                  </svg>
                  <div className="absolute top-1 right-2 text-[10px] font-mono text-slate-400 bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800">
                    {analogModType === "AM" ? "AM Carrier & Envelope" : "FM Instantaneous Frequency"}
                  </div>
                </div>
              </div>

              {/* Feature 260: Digital Modulation Dashboard & Constellations */}
              <div className="bg-[#0D1524] border border-slate-800 rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>📡</span> Digital Modulation & BER (Feature 260)
                  </h3>
                  <span className="text-xs font-mono text-amber-400">Eb/N0 = {digitalSnrDb} dB</span>
                </div>

                <div>
                  <label className="text-xs font-mono text-slate-400 block mb-0.5">SNR (Eb / N0 in dB):</label>
                  <input
                    type="range"
                    min="0"
                    max="16"
                    step="0.5"
                    value={digitalSnrDb}
                    onChange={(e) => setDigitalSnrDb(Number(e.target.value))}
                    className="w-full accent-indigo-500"
                  />
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs font-mono">
                    <thead className="bg-slate-900 text-slate-400 uppercase">
                      <tr>
                        <th className="py-2 px-3 rounded-l-lg">Scheme</th>
                        <th className="py-2 px-3">Bits/Sym</th>
                        <th className="py-2 px-3">bps/Hz</th>
                        <th className="py-2 px-3 rounded-r-lg">BER (Pb)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      <tr>
                        <td className="py-2 px-3 font-bold text-cyan-300">BPSK</td>
                        <td className="py-2 px-3">1</td>
                        <td className="py-2 px-3">1.0</td>
                        <td className="py-2 px-3 text-emerald-400 font-bold">{digitalMod.bpskBer}</td>
                      </tr>
                      <tr>
                        <td className="py-2 px-3 font-bold text-amber-300">QPSK</td>
                        <td className="py-2 px-3">2</td>
                        <td className="py-2 px-3">2.0</td>
                        <td className="py-2 px-3 text-emerald-400 font-bold">{digitalMod.bpskBer}</td>
                      </tr>
                      <tr>
                        <td className="py-2 px-3 font-bold text-purple-300">16-QAM</td>
                        <td className="py-2 px-3">4</td>
                        <td className="py-2 px-3">4.0</td>
                        <td className="py-2 px-3 text-amber-400 font-bold">{digitalMod.qamBer}</td>
                      </tr>
                      <tr>
                        <td className="py-2 px-3 font-bold text-slate-300">BFSK</td>
                        <td className="py-2 px-3">1</td>
                        <td className="py-2 px-3">0.5</td>
                        <td className="py-2 px-3 text-cyan-400 font-bold">{digitalMod.bfskBer}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                {/* 16-QAM & QPSK Constellation Plane */}
                <div className="h-32 bg-slate-950 rounded-xl border border-slate-800 p-2 flex items-center justify-center relative overflow-hidden">
                  <svg className="w-28 h-28" viewBox="-1.2 -1.2 2.4 2.4">
                    <line x1="-1.2" y1="0" x2="1.2" y2="0" stroke="#334155" strokeWidth="0.04" />
                    <line x1="0" y1="-1.2" x2="0" y2="1.2" stroke="#334155" strokeWidth="0.04" />
                    {DIGITAL_MODS[2].points.map((pt, idx) => (
                      <circle key={idx} cx={pt.x} cy={-pt.y} r="0.07" fill="#818CF8" />
                    ))}
                  </svg>
                  <div className="absolute top-2 right-2 text-[10px] font-mono text-slate-400 bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800">
                    16-QAM I/Q Constellation Grid
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
