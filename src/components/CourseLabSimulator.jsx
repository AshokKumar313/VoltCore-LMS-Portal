import React, { useState, useMemo, useEffect } from 'react';
import { getLabsByCourse, getLabById } from '../data/course_lab_data';
import VirtualOscilloscope from './VirtualOscilloscope.jsx';
import WokwiSimulationController from './WokwiSimulationController.jsx';
import WebUsbFlashingPanel from './WebUsbFlashingPanel.jsx';
import GeminiTutorChat from './GeminiTutorChat.jsx';
import MnaAnalogWorkbench from './MnaAnalogWorkbench.jsx';
import MathStudioHub from './MathStudioHub.jsx';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Laboratory Simulators & Interactive Benchmarks (Phase 8)
 * Core Engineering Series • Autonomous Test Bench Standards
 * Platform Lead & Systems Architect: Ashok Kumar A
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Series: Core Engineering Series • Autonomous Engineering Cluster
 *
 * Capabilities:
 *   - Client-side physics simulators with real-time SVG waveform / characteristic rendering
 *   - DSP Filter Bode grapher, Diode/MOSFET IV curve tracer, Laser g-stability diagram, RTOS Gantt
 *   - Universal Virtual Benches: DSO, Wokwi Bridge, WebUSB Flasher, Gemini AI Tutor
 *   - Cross-tool telemetry logging (voltcore:lab-telemetry event bus)
 *   - Local observation data logger (CSV export, zero background polling daemons)
 *   - Engineering syllabus viva-voce rubrics and safety protocols
 * ========================================================================================
 */

const STORAGE_KEY_PREFIX = "voltcore_lab_trials_";

export default function CourseLabSimulator({
  courseCode = "EC23S01",
  themeColor = "#00F0B5",
  themeFamily = "emerald"
}) {
  const labs = useMemo(() => getLabsByCourse(courseCode), [courseCode]);
  const [selectedLabId, setSelectedLabId] = useState(labs[0]?.id || "");

  // Update selected lab when course changes
  useEffect(() => {
    if (labs.length > 0 && (!selectedLabId || !labs.some(l => l.id === selectedLabId))) {
      setSelectedLabId(labs[0].id);
    }
  }, [courseCode, labs, selectedLabId]);

  const currentLab = useMemo(() => {
    return labs.find(l => l.id === selectedLabId) || labs[0];
  }, [labs, selectedLabId]);

  // Parameter state dictionary: paramId -> numerical value
  const [paramValues, setParamValues] = useState({});

  // Initialize or reset parameters when current lab changes
  useEffect(() => {
    if (currentLab && currentLab.parameters) {
      const initial = {};
      currentLab.parameters.forEach(p => {
        initial[p.id] = p.defaultValue;
      });
      setParamValues(initial);
    }
  }, [currentLab?.id]);

  // Observation records: array of logged row objects
  const [recordedTrials, setRecordedTrials] = useState([]);
  const [activeTab, setActiveTab] = useState("simulator"); // "simulator" | "instruments" | "observations" | "viva"
  const [activeBench, setActiveBench] = useState("dso"); // "dso" | "wokwi" | "flasher" | "tutor"

  // Load trials from localStorage
  useEffect(() => {
    if (!currentLab?.id) return;
    try {
      if (typeof window !== 'undefined') {
        const stored = localStorage.getItem(`${STORAGE_KEY_PREFIX}${currentLab.id}`);
        if (stored) {
          setRecordedTrials(JSON.parse(stored));
        } else {
          setRecordedTrials([]);
        }
      }
    } catch (e) {
      // Graceful fallback
    }
  }, [currentLab?.id]);

  // Cross-component telemetry listener for Virtual Benches (DSO, Wokwi, Flasher, Gemini Viva)
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleIncomingTelemetry = (event) => {
      if (!event.detail) return;
      const telemetry = event.detail;
      const newEntry = {
        id: `tel-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
        timestamp: new Date().toLocaleTimeString(),
        source: telemetry.tool || "Virtual Bench",
        ...(telemetry.board ? { board: telemetry.board } : {}),
        ...(telemetry.status ? { status: telemetry.status } : {}),
        ...(telemetry.topic ? { topic: telemetry.topic } : {}),
        ...(telemetry.parameters || {})
      };

      setRecordedTrials((prev) => {
        const updated = [newEntry, ...prev].slice(0, 50);
        try {
          if (currentLab?.id) {
            localStorage.setItem(`${STORAGE_KEY_PREFIX}${currentLab.id}`, JSON.stringify(updated));
          }
        } catch (e) {
          // Graceful fallback
        }
        return updated;
      });
    };

    window.addEventListener('voltcore:lab-telemetry', handleIncomingTelemetry);
    return () => {
      window.removeEventListener('voltcore:lab-telemetry', handleIncomingTelemetry);
    };
  }, [currentLab?.id]);

  // Update a single parameter
  const handleParamChange = (paramId, val) => {
    setParamValues(prev => ({
      ...prev,
      [paramId]: Number(val)
    }));
  };

  // Apply a preset
  const handleApplyPreset = (preset) => {
    setParamValues(prev => ({
      ...prev,
      ...preset.paramValues
    }));
  };

  // ---------------------------------------------------------------------------
  // MATHEMATICAL SIMULATION CALCULATION ENGINES (100% CLIENT-SIDE)
  // ---------------------------------------------------------------------------

  // 1. EC23S01: DSP Butterworth Frequency Response
  const dspSimData = useMemo(() => {
    if (courseCode !== "EC23S01") return null;
    const fc = paramValues.fc || 1000;
    const fs = paramValues.fs || 16000;
    const order = paramValues.order || 3;
    const gain = paramValues.passbandGain || 1.0;

    // Generate 60 log-spaced frequency points from 20 Hz to fs/2
    const fNyquist = fs / 2;
    const points = [];
    const numPoints = 60;
    const minF = 20;
    const maxF = fNyquist;

    for (let i = 0; i < numPoints; i++) {
      const logF = Math.log10(minF) + (i / (numPoints - 1)) * (Math.log10(maxF) - Math.log10(minF));
      const f = Math.pow(10, logF);
      const ratio = f / fc;
      
      let magGain = gain;
      if (paramValues.filterType === 1 || paramValues.isChebyshev) {
        // Chebyshev Type I polynomial CN(x)
        const eps = Math.sqrt(Math.pow(10, (paramValues.rippleDb || 1.0) / 10) - 1);
        const cn = ratio <= 1.0 ? Math.cos(order * Math.acos(ratio)) : Math.cosh(order * Math.acosh(ratio));
        magGain = gain / Math.sqrt(1 + Math.pow(eps * cn, 2));
      } else {
        // Butterworth |H(f)|^2 = A0^2 / (1 + (f/fc)^(2N))
        magGain = gain / Math.sqrt(1 + Math.pow(ratio, 2 * order));
      }
      const magDb = 20 * Math.log10(Math.max(magGain, 1e-4));
      points.push({ f: Math.round(f), ratio: Number(ratio.toFixed(2)), magGain: Number(magGain.toFixed(4)), magDb: Number(magDb.toFixed(2)) });
    }

    const rollOff = -20 * order;
    return { fc, fs, order, gain, fNyquist, points, rollOff };
  }, [courseCode, paramValues]);

  // 2. EC23C03: Semiconductor Diode & MOSFET IV Curve Tracer
  const deviceSimData = useMemo(() => {
    if (courseCode !== "EC23C03") return null;
    const vf = paramValues.vf !== undefined ? paramValues.vf : 0.65;
    const tempK = paramValues.tempK || 300;
    const eta = paramValues.eta || 1.05;
    const vgs = paramValues.vgs || 3.3;

    const kB = 1.380649e-23;
    const q = 1.60217663e-19;
    const vt = (kB * tempK) / q; // Volts
    const vtMv = vt * 1000;

    // Reverse saturation IS: scale exponentially with temperature
    // IS(T) = IS_300 * (T/300)^3 * exp(-Eg/(kT) * (1 - T/300))
    const is300 = 1e-12; // 1 pA at 300K
    const isCurrent = is300 * Math.pow(tempK / 300, 3) * Math.exp(1.12 / (kB * 300 / q) - 1.12 / vt);

    // Diode current ID = IS * (exp(VD / (eta*VT)) - 1)
    const diodeCurrentA = isCurrent * (Math.exp(Math.min(vf / (eta * vt), 25)) - 1);
    const diodeCurrentMa = diodeCurrentA * 1000;
    const dynamicRd = (eta * vt) / Math.max(diodeCurrentA, 1e-9);

    // Diode SVG curve points (0V to 0.85V)
    const diodeCurve = [];
    for (let v = 0; v <= 0.85; v += 0.02) {
      const iA = isCurrent * (Math.exp(Math.min(v / (eta * vt), 25)) - 1);
      diodeCurve.push({ v: Number(v.toFixed(2)), iMa: Math.min(iA * 1000, 100) });
    }

    // MOSFET: kn = 20 mA/V^2, Vth = 1.2V
    const vth = 1.2;
    const kn = 20.0;
    const vov = Math.max(0, vgs - vth);
    const mosfetSatIdMa = 0.5 * kn * Math.pow(vov, 2);

    // MOSFET curves for 4 VGS levels: 2.0, 3.0, 4.0, 5.0 V
    const mosfetFamily = [2.0, 3.0, 4.0, 5.0].map(vg => {
      const ov = Math.max(0, vg - vth);
      const points = [];
      for (let vds = 0; vds <= 6.0; vds += 0.2) {
        let iD = 0;
        if (vds < ov) {
          // Triode
          iD = kn * (ov * vds - 0.5 * vds * vds);
        } else {
          // Saturation with slight Early lambda = 0.02
          iD = 0.5 * kn * Math.pow(ov, 2) * (1 + 0.02 * vds);
        }
        points.push({ vds: Number(vds.toFixed(1)), iD: Number(iD.toFixed(2)) });
      }
      return { vg, ov, points };
    });

    return { vf, tempK, vtMv: Number(vtMv.toFixed(2)), diodeCurrentMa: Number(diodeCurrentMa.toFixed(3)), dynamicRd: Number(dynamicRd.toFixed(2)), diodeCurve, vgs, vth, mosfetSatIdMa: Number(mosfetSatIdMa.toFixed(2)), mosfetFamily };
  }, [courseCode, paramValues]);

  // 3. EC23E04: Optics Laser Cavity Stability
  const opticsSimData = useMemo(() => {
    if (courseCode !== "EC23E04") return null;
    const L = paramValues.cavityLength || 0.5;
    const R1 = paramValues.r1 || 1.0;
    const R2 = paramValues.r2 || 0.75;
    const lambdaNm = paramValues.wavelengthNm || 632.8;

    const g1 = 1 - L / R1;
    const g2 = 1 - L / R2;
    const gProd = g1 * g2;
    const isStable = gProd >= 0 && gProd <= 1.0;

    // Longitudinal mode spacing Delta_nu = c / (2*L)
    const c = 2.99792458e8; // m/s
    const modeSpacingHz = c / (2 * L);
    const modeSpacingMhz = modeSpacingHz / 1e6;

    // Coherence length for typical He-Ne gain bandwidth 1.5 GHz
    const deltaNuLaser = 1.5e9;
    const coherenceLengthM = c / deltaNuLaser;

    return {
      L, R1, R2, lambdaNm,
      g1: Number(g1.toFixed(3)),
      g2: Number(g2.toFixed(3)),
      gProd: Number(gProd.toFixed(3)),
      isStable,
      modeSpacingMhz: Number(modeSpacingMhz.toFixed(2)),
      coherenceLengthM: Number(coherenceLengthM.toFixed(3))
    };
  }, [courseCode, paramValues]);

  // 4. EC8702: Embedded Systems FreeRTOS Schedulability & Timing
  const rtosSimData = useMemo(() => {
    if (courseCode !== "EC8702") return null;
    const c1 = paramValues.c1 || 8;
    const t1 = paramValues.t1 || 30;
    const c2 = paramValues.c2 || 12;
    const t2 = paramValues.t2 || 50;
    const c3 = paramValues.c3 || 15;
    const t3 = paramValues.t3 || 100;

    const u1 = (c1 / t1) * 100;
    const u2 = (c2 / t2) * 100;
    const u3 = (c3 / t3) * 100;
    const totalU = u1 + u2 + u3;

    // Liu & Layland bound for n = 3: 3 * (2^(1/3) - 1) = 77.98%
    const bound = 3 * (Math.pow(2, 1 / 3) - 1) * 100;
    const isSchedulable = totalU <= bound;

    // Hardware ARM NVIC Tail-Chaining latency
    const coreClockMhz = 84;
    const cycleTimeNs = 1000 / coreClockMhz;
    const tailChainCycles = 6;
    const standardUnstackStackCycles = 24;
    const tailChainTimeNs = tailChainCycles * cycleTimeNs;
    const standardTimeNs = standardUnstackStackCycles * cycleTimeNs;
    const latencySavingsPct = ((standardTimeNs - tailChainTimeNs) / standardTimeNs) * 100;

    return {
      c1, t1, c2, t2, c3, t3,
      u1: Number(u1.toFixed(1)),
      u2: Number(u2.toFixed(1)),
      u3: Number(u3.toFixed(1)),
      totalU: Number(totalU.toFixed(1)),
      bound: Number(bound.toFixed(2)),
      isSchedulable,
      tailChainTimeNs: Number(tailChainTimeNs.toFixed(1)),
      standardTimeNs: Number(standardTimeNs.toFixed(1)),
      latencySavingsPct: Number(latencySavingsPct.toFixed(1))
    };
  }, [courseCode, paramValues]);

  // ---------------------------------------------------------------------------
  // OBSERVATION LOGGER HANDLERS
  // ---------------------------------------------------------------------------

  const handleRecordObservation = () => {
    if (!currentLab) return;
    let newEntry = {
      timestamp: new Date().toLocaleTimeString(),
      id: Date.now()
    };

    if (courseCode === "EC23S01" && dspSimData) {
      newEntry = {
        ...newEntry,
        testFreq: `${dspSimData.fc} Hz`,
        ratio: "1.00",
        magGain: "0.7071",
        magDb: "-3.01 dB",
        regime: "Cutoff (-3dB)"
      };
    } else if (courseCode === "EC23C03" && deviceSimData) {
      newEntry = {
        ...newEntry,
        appliedVd: `${deviceSimData.vf} V`,
        diodeIdMa: `${deviceSimData.diodeCurrentMa} mA`,
        dynamicRd: `${deviceSimData.dynamicRd} Ω`,
        mosfetIdMa: `${deviceSimData.mosfetSatIdMa} mA`,
        state: deviceSimData.diodeCurrentMa > 0.5 ? "Forward Conduction" : "Sub-threshold"
      };
    } else if (courseCode === "EC23E04" && opticsSimData) {
      newEntry = {
        ...newEntry,
        lengthL: `${opticsSimData.L} m`,
        g1Val: opticsSimData.g1,
        g2Val: opticsSimData.g2,
        gProd: opticsSimData.gProd,
        modeSpacing: `${opticsSimData.modeSpacingMhz} MHz`,
        stability: opticsSimData.isStable ? "STABLE" : "UNSTABLE"
      };
    } else if (courseCode === "EC8702" && rtosSimData) {
      newEntry = {
        ...newEntry,
        u1Pct: `${rtosSimData.u1}%`,
        u2Pct: `${rtosSimData.u2}%`,
        u3Pct: `${rtosSimData.u3}%`,
        totalUPct: `${rtosSimData.totalU}%`,
        boundPct: `${rtosSimData.bound}%`,
        schedStatus: rtosSimData.isSchedulable ? "SCHEDULABLE" : "OVERLOAD"
      };
    }

    const updated = [newEntry, ...recordedTrials.slice(0, 19)];
    setRecordedTrials(updated);
    try {
      if (typeof window !== 'undefined') {
        localStorage.setItem(`${STORAGE_KEY_PREFIX}${currentLab.id}`, JSON.stringify(updated));
      }
    } catch (e) {
      // Ignore
    }
  };

  const handleClearObservations = () => {
    setRecordedTrials([]);
    try {
      if (typeof window !== 'undefined') {
        localStorage.removeItem(`${STORAGE_KEY_PREFIX}${currentLab?.id}`);
      }
    } catch (e) {
      // Ignore
    }
  };

  const handleExportCsv = () => {
    if (recordedTrials.length === 0 || !currentLab) return;
    const cols = currentLab.observationColumns;
    let csv = "Timestamp," + cols.map(c => `"${c.label} (${c.unit})"`).join(",") + "\n";
    recordedTrials.forEach(t => {
      const row = [t.timestamp, ...cols.map(c => `"${t[c.id] || ''}"`)];
      csv += row.join(",") + "\n";
    });

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `VoltCore_Lab_${currentLab.id}_Observations.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!currentLab) {
    return (
      <div className="p-8 rounded-2xl bg-[#041026] border border-slate-800 text-center text-slate-400 font-mono text-sm">
        No laboratory exercises configured for course {courseCode}.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* --------------------------------------------------------------------- */}
      {/* HEADER & LAB EXERCISE SELECTOR STRIP */}
      {/* --------------------------------------------------------------------- */}
      <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono font-bold" style={{ color: themeColor }}>
              <span>🧪</span>
              <span>MODULAR ENGINEERING SERIES • VIRTUAL LAB WORKBENCH</span>
              <span className="text-slate-500">•</span>
              <span className="text-slate-400">Unit {currentLab.unitRoman} Practical</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-extrabold text-white mt-1">
              {currentLab.title}
            </h2>
          </div>

          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-[#020813] border border-slate-700 text-slate-300">
              ⚡ 100% Client-Side Physics
            </span>
            <button
              onClick={handleRecordObservation}
              className="px-3.5 py-1.5 rounded-xl font-mono text-xs font-bold transition-all shadow-md flex items-center gap-1.5"
              style={{
                backgroundColor: themeColor,
                color: "#020813"
              }}
            >
              <span>💾</span>
              <span>Record Trial</span>
            </button>
          </div>
        </div>

        {/* Multi-Exercise Switcher (if course has >1 lab) */}
        {labs.length > 1 && (
          <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-800">
            {labs.map(l => (
              <button
                key={l.id}
                onClick={() => setSelectedLabId(l.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold transition-all ${
                  selectedLabId === l.id
                    ? "bg-[#020813] text-white border-2 shadow-md"
                    : "bg-[#020813]/60 text-slate-400 hover:text-white border border-slate-800"
                }`}
                style={{
                  borderColor: selectedLabId === l.id ? themeColor : undefined
                }}
              >
                Unit {l.unitRoman}: {l.title}
              </button>
            ))}
          </div>
        )}

        {/* View Mode Navigation: Simulator vs Universal Instruments vs Observations vs Viva Voce */}
        <div className="flex flex-wrap gap-2 pt-2">
          {[
            { id: "simulator", label: "Simulation & Waveforms", icon: "📊" },
            { id: "instruments", label: "Universal Virtual Benches", icon: "🔬" },
            { id: "observations", label: `Observation Data Log (${recordedTrials.length})`, icon: "📋" },
            { id: "viva", label: "Viva-Voce & Lab Rubric", icon: "🎓" }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1 rounded-lg text-xs font-mono transition-colors flex items-center gap-1.5 ${
                activeTab === tab.id
                  ? "bg-slate-800 text-white font-bold"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/40"
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* --------------------------------------------------------------------- */}
      {/* VIEW 1: ACTIVE SIMULATION & WAVEFORMS */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "simulator" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* LEFT COLUMN: PARAMETER CONTROL CONSOLE (4 COLS) */}
          <div className="lg:col-span-4 space-y-4">
            <div className="p-5 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="font-bold text-sm text-white font-mono flex items-center gap-2">
                  <span>🎛️</span>
                  <span>Parameter Controls</span>
                </h3>
                <span className="text-[10px] font-mono text-slate-400 uppercase">Live Reactive</span>
              </div>

              {/* Parameter Sliders */}
              <div className="space-y-4 font-mono text-xs">
                {currentLab.parameters.map(param => {
                  const val = paramValues[param.id] !== undefined ? paramValues[param.id] : param.defaultValue;
                  return (
                    <div key={param.id} className="space-y-1.5 p-3 rounded-xl bg-[#020813] border border-slate-800">
                      <div className="flex justify-between items-center">
                        <label className="text-slate-300 font-medium truncate">{param.name}:</label>
                        <span className="font-bold px-2 py-0.5 rounded bg-slate-800" style={{ color: themeColor }}>
                          {val} {param.unit}
                        </span>
                      </div>
                      <input
                        type="range"
                        min={param.min}
                        max={param.max}
                        step={param.step}
                        value={val}
                        onChange={(e) => handleParamChange(param.id, e.target.value)}
                        className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                        style={{ accentColor: themeColor }}
                      />
                      <div className="flex justify-between text-[10px] text-slate-500">
                        <span>{param.min} {param.unit}</span>
                        <span>{param.max} {param.unit}</span>
                      </div>
                      <div className="text-[10px] text-slate-400 leading-tight pt-1">
                        {param.description}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Scenario Presets */}
              {currentLab.presets && currentLab.presets.length > 0 && (
                <div className="space-y-2 pt-2 border-t border-slate-800">
                  <div className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider">
                    Benchmark Presets:
                  </div>
                  <div className="space-y-1.5">
                    {currentLab.presets.map((p, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleApplyPreset(p)}
                        className="w-full p-2 rounded-xl bg-[#020813] hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-left transition-colors"
                      >
                        <div className="text-xs font-bold text-white font-mono flex items-center justify-between">
                          <span>{p.name}</span>
                          <span className="text-[10px] text-emerald-400 font-sans">Apply ⚡</span>
                        </div>
                        <div className="text-[10px] text-slate-400 font-sans mt-0.5">
                          {p.description}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Hardware Apparatus & Safety Notice */}
            <div className="p-4 rounded-xl bg-[#020813] border border-slate-800 font-mono text-xs space-y-2">
              <div className="text-[11px] font-bold text-slate-300 flex items-center gap-1.5">
                <span>🛡️</span>
                <span>Laboratory Safety Compliance:</span>
              </div>
              <p className="text-[10px] text-slate-400 leading-relaxed font-sans">
                {currentLab.safetyProtocol}
              </p>
            </div>
          </div>

          {/* RIGHT COLUMN: GRAPHICAL WORKBENCH & CANVASES (8 COLS) */}
          <div className="lg:col-span-8 space-y-4">
            {/* 1. EC23S01: DSP BODE PLOT VISUALIZER */}
            {courseCode === "EC23S01" && dspSimData && (
              <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                  <div>
                    <h4 className="font-bold text-sm text-white font-mono flex items-center gap-2">
                      <span>📈</span>
                      <span>Butterworth Filter Magnitude Response |H(f)| (Bode Plot)</span>
                    </h4>
                    <div className="text-xs text-slate-400 font-mono">
                      Roll-off rate: <strong className="text-emerald-400">{dspSimData.rollOff} dB/decade</strong> • Order N = {dspSimData.order}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-mono">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">Cutoff: {dspSimData.fc} Hz</span>
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">Nyquist: {dspSimData.fNyquist} Hz</span>
                  </div>
                </div>

                {/* SVG Bode Plot Graph */}
                <div className="relative w-full h-64 bg-[#020813] rounded-xl border border-slate-800 p-3 overflow-hidden">
                  <svg className="w-full h-full" viewBox="0 0 500 220" preserveAspectRatio="none">
                    {/* Grid lines */}
                    <line x1="40" y1="20" x2="480" y2="20" stroke="#1e293b" strokeWidth="1" strokeDasharray="3 3" />
                    <line x1="40" y1="70" x2="480" y2="70" stroke="#1e293b" strokeWidth="1" strokeDasharray="3 3" />
                    <line x1="40" y1="120" x2="480" y2="120" stroke="#1e293b" strokeWidth="1" strokeDasharray="3 3" />
                    <line x1="40" y1="170" x2="480" y2="170" stroke="#1e293b" strokeWidth="1" strokeDasharray="3 3" />

                    {/* -3dB Cutoff Reference Line */}
                    <line x1="40" y1="50" x2="480" y2="50" stroke="#f59e0b" strokeWidth="1.5" strokeDasharray="4 4" />
                    <text x="42" y="46" fill="#f59e0b" fontSize="9" fontFamily="monospace">-3 dB Cutoff Threshold</text>

                    {/* dB Axis Labels */}
                    <text x="5" y="24" fill="#64748b" fontSize="9" fontFamily="monospace">0 dB</text>
                    <text x="5" y="74" fill="#64748b" fontSize="9" fontFamily="monospace">-20</text>
                    <text x="5" y="124" fill="#64748b" fontSize="9" fontFamily="monospace">-40</text>
                    <text x="5" y="174" fill="#64748b" fontSize="9" fontFamily="monospace">-60</text>

                    {/* Frequency Axis */}
                    <line x1="40" y1="190" x2="480" y2="190" stroke="#475569" strokeWidth="1.5" />
                    <text x="40" y="206" fill="#64748b" fontSize="9" fontFamily="monospace">20 Hz</text>
                    <text x="250" y="206" fill="#64748b" fontSize="9" fontFamily="monospace">1 kHz</text>
                    <text x="440" y="206" fill="#64748b" fontSize="9" fontFamily="monospace">{dspSimData.fNyquist} Hz</text>

                    {/* Bode Curve Mapping: Map magDb [-60, 0] to Y [190, 20] */}
                    {(() => {
                      const pts = dspSimData.points.map((pt, i) => {
                        const x = 40 + (i / (dspSimData.points.length - 1)) * 440;
                        const clampedDb = Math.max(-65, Math.min(5, pt.magDb));
                        const y = 20 + ((0 - clampedDb) / 60) * 170;
                        return `${x},${y}`;
                      }).join(" ");

                      return (
                        <>
                          {/* Filled semi-transparent area under passband */}
                          <polygon
                            points={`40,190 ${pts} 480,190`}
                            fill={themeColor}
                            fillOpacity="0.12"
                          />
                          {/* Main Characteristic Line */}
                          <polyline
                            points={pts}
                            fill="none"
                            stroke={themeColor}
                            strokeWidth="2.5"
                            strokeLinecap="round"
                          />
                        </>
                      );
                    })()}
                  </svg>
                </div>

                {/* Analytical Metrics Cards */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">3dB Cutoff (fc)</div>
                    <div className="text-white font-bold text-sm mt-0.5">{dspSimData.fc} Hz</div>
                  </div>
                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Roll-off Slope</div>
                    <div className="text-emerald-400 font-bold text-sm mt-0.5">{dspSimData.rollOff} dB/dec</div>
                  </div>
                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Nyquist Limit</div>
                    <div className="text-cyan-400 font-bold text-sm mt-0.5">{dspSimData.fNyquist} Hz</div>
                  </div>
                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Transition Ratio</div>
                    <div className="text-amber-300 font-bold text-sm mt-0.5">{(dspSimData.fc / dspSimData.fNyquist).toFixed(2)}</div>
                  </div>
                </div>
              </div>
            )}

            {/* 2. EC23C03: SEMICONDUCTOR DIODE & MOSFET IV CURVE TRACER */}
            {courseCode === "EC23C03" && deviceSimData && (
              <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-5">
                {currentLab?.mnaConfig && (
                  <div className="p-3.5 rounded-xl bg-gradient-to-r from-emerald-950/40 via-cyan-950/30 to-[#020813] border border-emerald-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono">
                    <div className="flex items-center gap-2.5">
                      <span className="text-xl">🎛️</span>
                      <div>
                        <div className="text-emerald-300 font-bold">
                          Interactive Modified Nodal Analysis (MNA) &amp; SPICE Deck Available
                        </div>
                        <div className="text-slate-400 text-[11px]">
                          Preset: <span className="text-white">{currentLab.mnaConfig.presetId}</span> • Numerical Matrix Solver &amp; Transient Waveform Synchronization
                        </div>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        setActiveTab("instruments");
                        setActiveBench("mna");
                      }}
                      className="px-3.5 py-1.5 rounded-xl bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 border border-emerald-500/40 font-bold transition-all flex items-center gap-1.5 whitespace-nowrap self-start sm:self-auto cursor-pointer"
                    >
                      <span>⚡</span>
                      <span>Launch MNA Workbench &amp; SPICE</span>
                    </button>
                  </div>
                )}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                  <div>
                    <h4 className="font-bold text-sm text-white font-mono flex items-center gap-2">
                      <span>⚡</span>
                      <span>Diode Shockley &amp; MOSFET Output Characteristic Family</span>
                    </h4>
                    <div className="text-xs text-slate-400 font-mono">
                      Thermal Voltage VT = <strong className="text-amber-400">{deviceSimData.vtMv} mV</strong> at {deviceSimData.tempK} K
                    </div>
                  </div>
                  <span className="px-2.5 py-1 rounded bg-[#020813] border border-slate-700 text-xs font-mono text-emerald-400">
                    {deviceSimData.diodeCurrentMa > 0.5 ? "Knee Passed (Active Conduction)" : "Sub-threshold Leakage"}
                  </span>
                </div>

                {/* SVG Curve Canvas: Side-by-Side or Combined */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Left: Diode IV Curve */}
                  <div className="bg-[#020813] rounded-xl border border-slate-800 p-3">
                    <div className="text-xs font-mono font-bold text-slate-300 mb-2 flex justify-between">
                      <span>Diode ID vs VD (Shockley)</span>
                      <span className="text-amber-400">{deviceSimData.diodeCurrentMa} mA</span>
                    </div>
                    <div className="h-44 w-full">
                      <svg className="w-full h-full" viewBox="0 0 240 160">
                        {/* Axes */}
                        <line x1="30" y1="135" x2="230" y2="135" stroke="#475569" strokeWidth="1.5" />
                        <line x1="30" y1="135" x2="30" y2="15" stroke="#475569" strokeWidth="1.5" />
                        <text x="210" y="148" fill="#64748b" fontSize="8" fontFamily="monospace">VD (V)</text>
                        <text x="5" y="25" fill="#64748b" fontSize="8" fontFamily="monospace">ID (mA)</text>

                        {/* Grid */}
                        <line x1="30" y1="75" x2="230" y2="75" stroke="#1e293b" strokeDasharray="2 2" />
                        <line x1="130" y1="135" x2="130" y2="15" stroke="#1e293b" strokeDasharray="2 2" />

                        {/* Diode Exponential Curve */}
                        {(() => {
                          const pts = deviceSimData.diodeCurve.map(pt => {
                            const x = 30 + (pt.v / 0.85) * 190;
                            const y = 135 - (Math.min(pt.iMa, 100) / 100) * 115;
                            return `${x},${y}`;
                          }).join(" ");
                          return (
                            <polyline
                              points={pts}
                              fill="none"
                              stroke="#F59E0B"
                              strokeWidth="2.5"
                            />
                          );
                        })()}

                        {/* Operating Point Marker */}
                        {(() => {
                          const curX = 30 + (deviceSimData.vf / 0.85) * 190;
                          const curY = 135 - (Math.min(deviceSimData.diodeCurrentMa, 100) / 100) * 115;
                          return (
                            <circle cx={curX} cy={curY} r="4" fill="#00F0B5" stroke="#ffffff" strokeWidth="1.5" />
                          );
                        })()}
                      </svg>
                    </div>
                  </div>

                  {/* Right: MOSFET ID vs VDS Family */}
                  <div className="bg-[#020813] rounded-xl border border-slate-800 p-3">
                    <div className="text-xs font-mono font-bold text-slate-300 mb-2 flex justify-between">
                      <span>MOSFET Family (VGS = 2, 3, 4, 5V)</span>
                      <span className="text-cyan-400">Sat ID: {deviceSimData.mosfetSatIdMa} mA</span>
                    </div>
                    <div className="h-44 w-full">
                      <svg className="w-full h-full" viewBox="0 0 240 160">
                        {/* Axes */}
                        <line x1="30" y1="135" x2="230" y2="135" stroke="#475569" strokeWidth="1.5" />
                        <line x1="30" y1="135" x2="30" y2="15" stroke="#475569" strokeWidth="1.5" />
                        <text x="205" y="148" fill="#64748b" fontSize="8" fontFamily="monospace">VDS (V)</text>
                        <text x="5" y="25" fill="#64748b" fontSize="8" fontFamily="monospace">ID (mA)</text>

                        {/* 4 Curves */}
                        {deviceSimData.mosfetFamily.map((fam, idx) => {
                          const pts = fam.points.map(pt => {
                            const x = 30 + (pt.vds / 6.0) * 190;
                            const y = 135 - (Math.min(pt.iD, 160) / 160) * 115;
                            return `${x},${y}`;
                          }).join(" ");
                          const colors = ["#475569", "#06B6D4", "#3B82F6", "#00F0B5"];
                          return (
                            <g key={fam.vg}>
                              <polyline points={pts} fill="none" stroke={colors[idx]} strokeWidth="1.8" />
                              <text x="210" y={135 - (fam.points[fam.points.length - 1].iD / 160) * 115} fill={colors[idx]} fontSize="7" fontFamily="monospace">
                                {fam.vg}V
                              </text>
                            </g>
                          );
                        })}
                      </svg>
                    </div>
                  </div>
                </div>

                {/* Analytical Metrics */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Diode Current (ID)</div>
                    <div className="text-amber-400 font-bold text-sm mt-0.5">{deviceSimData.diodeCurrentMa} mA</div>
                  </div>
                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Dynamic rd</div>
                    <div className="text-emerald-400 font-bold text-sm mt-0.5">{deviceSimData.dynamicRd} Ω</div>
                  </div>
                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">MOSFET Sat ID</div>
                    <div className="text-cyan-400 font-bold text-sm mt-0.5">{deviceSimData.mosfetSatIdMa} mA</div>
                  </div>
                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Junction Temp (T)</div>
                    <div className="text-white font-bold text-sm mt-0.5">{deviceSimData.tempK} K ({deviceSimData.tempK - 273}°C)</div>
                  </div>
                </div>
              </div>
            )}

            {/* 3. EC23E04: OPTICS LASER CAVITY STABILITY G-DIAGRAM */}
            {courseCode === "EC23E04" && opticsSimData && (
              <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                  <div>
                    <h4 className="font-bold text-sm text-white font-mono flex items-center gap-2">
                      <span>🔦</span>
                      <span>Universal (g1 - g2) Resonator Stability Diagram</span>
                    </h4>
                    <div className="text-xs text-slate-400 font-mono">
                      Stability Product: <strong className={opticsSimData.isStable ? "text-emerald-400" : "text-rose-400"}>{opticsSimData.gProd}</strong> (Condition: 0 ≤ g1*g2 ≤ 1)
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-mono font-bold ${
                    opticsSimData.isStable ? "bg-emerald-950/60 text-emerald-300 border border-emerald-500/40" : "bg-rose-950/60 text-rose-300 border border-rose-500/40"
                  }`}>
                    {opticsSimData.isStable ? "STABLE RESONATOR" : "UNSTABLE RESONATOR"}
                  </span>
                </div>

                {/* SVG g1-g2 Plane */}
                <div className="w-full h-64 bg-[#020813] rounded-xl border border-slate-800 p-3 relative flex items-center justify-center">
                  <svg className="w-full h-full" viewBox="0 0 300 240">
                    {/* Centered Coordinate axes g1, g2 ranging [-1.5, +1.5] */}
                    <line x1="20" y1="120" x2="280" y2="120" stroke="#475569" strokeWidth="1.5" />
                    <line x1="150" y1="10" x2="150" y2="230" stroke="#475569" strokeWidth="1.5" />
                    <text x="270" y="135" fill="#64748b" fontSize="9" fontFamily="monospace">g1</text>
                    <text x="155" y="20" fill="#64748b" fontSize="9" fontFamily="monospace">g2</text>

                    {/* Stable Region Quadrants: Shaded between axes and hyperbola g1*g2 = 1 */}
                    <rect x="150" y="33" width="86" height="87" fill="#00F0B5" fillOpacity="0.08" />
                    <rect x="64" y="120" width="86" height="87" fill="#00F0B5" fillOpacity="0.08" />

                    {/* Stability Hyperbola g1 * g2 = 1 curves */}
                    <path
                      d="M 165 220 Q 185 145 270 130"
                      fill="none"
                      stroke="#06B6D4"
                      strokeWidth="1.5"
                      strokeDasharray="3 3"
                    />
                    <path
                      d="M 135 20 Q 115 95 30 110"
                      fill="none"
                      stroke="#06B6D4"
                      strokeWidth="1.5"
                      strokeDasharray="3 3"
                    />

                    {/* Axis Scale Markers */}
                    <text x="236" y="132" fill="#64748b" fontSize="8" fontFamily="monospace">+1</text>
                    <text x="64" y="132" fill="#64748b" fontSize="8" fontFamily="monospace">-1</text>
                    <text x="153" y="36" fill="#64748b" fontSize="8" fontFamily="monospace">+1</text>
                    <text x="153" y="207" fill="#64748b" fontSize="8" fontFamily="monospace">-1</text>

                    {/* Operating Point Marker (g1, g2) mapped to [0, 300] and [0, 240] */}
                    {(() => {
                      // Center is (150, 120), unit length is 86.6 pixels
                      const cx = 150 + opticsSimData.g1 * 86.6;
                      const cy = 120 - opticsSimData.g2 * 86.6;
                      const clampedX = Math.max(10, Math.min(290, cx));
                      const clampedY = Math.max(10, Math.min(230, cy));
                      return (
                        <g>
                          <circle cx={clampedX} cy={clampedY} r="6" fill={opticsSimData.isStable ? "#00F0B5" : "#F43F5E"} stroke="#ffffff" strokeWidth="2" />
                          <text x={clampedX + 8} y={clampedY - 6} fill="#ffffff" fontSize="9" fontFamily="monospace" fontWeight="bold">
                            P({opticsSimData.g1}, {opticsSimData.g2})
                          </text>
                        </g>
                      );
                    })()}
                  </svg>
                </div>

                {/* Analytical Metrics */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Parameter g1</div>
                    <div className="text-white font-bold text-sm mt-0.5">{opticsSimData.g1}</div>
                  </div>
                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Parameter g2</div>
                    <div className="text-white font-bold text-sm mt-0.5">{opticsSimData.g2}</div>
                  </div>
                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Mode Spacing (Δν)</div>
                    <div className="text-cyan-400 font-bold text-sm mt-0.5">{opticsSimData.modeSpacingMhz} MHz</div>
                  </div>
                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Coherence Length (Lc)</div>
                    <div className="text-emerald-400 font-bold text-sm mt-0.5">{opticsSimData.coherenceLengthM} m</div>
                  </div>
                </div>
              </div>
            )}

            {/* 4. EC8702: FREERTOS TASK SCHEDULING TIMELINE & GANTT */}
            {courseCode === "EC8702" && rtosSimData && (
              <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                  <div>
                    <h4 className="font-bold text-sm text-white font-mono flex items-center gap-2">
                      <span>⚙️</span>
                      <span>FreeRTOS Rate Monotonic Scheduling (RMS) &amp; CPU Utilization</span>
                    </h4>
                    <div className="text-xs text-slate-400 font-mono">
                      Total CPU Load: <strong className={rtosSimData.isSchedulable ? "text-emerald-400" : "text-rose-400"}>{rtosSimData.totalU}%</strong> (Bound: ≤ {rtosSimData.bound}%)
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-mono font-bold ${
                    rtosSimData.isSchedulable ? "bg-emerald-950/60 text-emerald-300 border border-emerald-500/40" : "bg-rose-950/60 text-rose-300 border border-rose-500/40"
                  }`}>
                    {rtosSimData.isSchedulable ? "100% SCHEDULABLE" : "DEADLINE MISS RISK"}
                  </span>
                </div>

                {/* Scheduling Gantt Bar Chart */}
                <div className="p-4 rounded-xl bg-[#020813] border border-slate-800 space-y-3 font-mono text-xs">
                  <div className="text-slate-400 text-xs flex justify-between">
                    <span>Task Utilization Breakdown:</span>
                    <span>Total U = {rtosSimData.totalU}%</span>
                  </div>

                  {/* Stacked utilization bar vs bound */}
                  <div className="relative w-full h-7 bg-slate-900 rounded-lg overflow-hidden flex border border-slate-800">
                    <div style={{ width: `${Math.min(rtosSimData.u1, 100)}%` }} className="bg-indigo-500 h-full flex items-center justify-center text-[10px] text-white font-bold">
                      T1: {rtosSimData.u1}%
                    </div>
                    <div style={{ width: `${Math.min(rtosSimData.u2, 100 - rtosSimData.u1)}%` }} className="bg-cyan-500 h-full flex items-center justify-center text-[10px] text-slate-900 font-bold">
                      T2: {rtosSimData.u2}%
                    </div>
                    <div style={{ width: `${Math.min(rtosSimData.u3, Math.max(0, 100 - rtosSimData.u1 - rtosSimData.u2))}%` }} className="bg-amber-400 h-full flex items-center justify-center text-[10px] text-slate-900 font-bold">
                      T3: {rtosSimData.u3}%
                    </div>
                  </div>

                  {/* Bound line indicator */}
                  <div className="relative w-full h-4">
                    <div className="absolute top-0 bottom-0 w-0.5 bg-emerald-400 z-10" style={{ left: `${rtosSimData.bound}%` }}>
                      <span className="absolute -top-3.5 -left-8 text-[9px] text-emerald-400 whitespace-nowrap font-bold">
                        Bound: {rtosSimData.bound}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* ARM NVIC Interrupt Tail-Chaining Benchmark */}
                <div className="p-4 rounded-xl bg-[#020813] border border-slate-800 space-y-2 font-mono text-xs">
                  <div className="text-white font-bold flex items-center justify-between">
                    <span>⚡ ARM Cortex-M4 NVIC Tail-Chaining Optimization:</span>
                    <span className="text-emerald-400">{rtosSimData.latencySavingsPct}% Latency Saved</span>
                  </div>
                  <div className="grid grid-cols-2 gap-3 text-[11px] pt-1">
                    <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                      <div className="text-slate-400">Standard Context Unstack + Stack:</div>
                      <div className="text-slate-200 font-bold mt-0.5">24 Cycles ({rtosSimData.standardTimeNs} ns)</div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-500/30">
                      <div className="text-emerald-300">Hardware Tail-Chaining:</div>
                      <div className="text-emerald-400 font-bold mt-0.5">6 Cycles ({rtosSimData.tailChainTimeNs} ns)</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* VIEW: UNIVERSAL VIRTUAL INSTRUMENTATION BENCHES */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "instruments" && (
        <div className="space-y-6">
          <div className="p-5 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>🔬</span>
                <span>Universal Hardware Simulation Benches &amp; Test Instrumentation</span>
              </h3>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                Cross-instrument telemetry automatically logs into the current laboratory observation ledger
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
              {[
                { id: 'dso', label: 'Virtual DSO (Rigol DS1054Z)', icon: '📈' },
                { id: 'mna', label: 'MNA Analog Lab', icon: '🎛️' },
                { id: 'math', label: 'Math Studio (Poles/Zeros)', icon: '📐' },
                { id: 'wokwi', label: 'Wokwi Silicon Controller', icon: '⚡' },
                { id: 'flasher', label: 'WebUSB/Serial Flasher', icon: '🔌' },
                { id: 'tutor', label: 'Gemini AI Lab Tutor', icon: '🤖' }
              ].map(bench => (
                <button
                  key={bench.id}
                  type="button"
                  onClick={() => setActiveBench(bench.id)}
                  className={`px-3 py-1.5 rounded-xl border transition-all cursor-pointer ${
                    activeBench === bench.id
                      ? 'border-[#00F0B5] bg-[#020813] text-[#00F0B5] font-bold shadow-emerald-glow'
                      : 'border-slate-800 bg-[#020813]/60 text-slate-400 hover:text-white hover:border-slate-700'
                  }`}
                >
                  <span className="mr-1.5">{bench.icon}</span>
                  <span>{bench.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="transition-all duration-200">
            {activeBench === 'dso' && <VirtualOscilloscope />}
            {activeBench === 'mna' && <MnaAnalogWorkbench themeColor={themeColor} />}
            {activeBench === 'math' && <MathStudioHub themeColor={themeColor} />}
            {activeBench === 'wokwi' && <WokwiSimulationController />}
            {activeBench === 'flasher' && <WebUsbFlashingPanel />}
            {activeBench === 'tutor' && <GeminiTutorChat />}
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* VIEW 2: OBSERVATION DATA LOG TABLE */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "observations" && (
        <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
            <div>
              <h3 className="font-bold text-base text-white flex items-center gap-2">
                <span>📋</span>
                <span>Recorded Laboratory Observations &amp; Verification Matrix</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5 font-mono">
                Modular Engineering Laboratory Trial Audit • Zero-Overhead Local Storage
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleExportCsv}
                disabled={recordedTrials.length === 0}
                className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-xs font-mono font-bold text-emerald-300 transition-colors flex items-center gap-1.5"
              >
                <span>📥</span>
                <span>Export CSV</span>
              </button>
              <button
                onClick={handleClearObservations}
                disabled={recordedTrials.length === 0}
                className="px-3 py-1.5 rounded-xl bg-rose-950/40 hover:bg-rose-900/40 disabled:opacity-40 text-xs font-mono font-bold text-rose-300 border border-rose-800/40 transition-colors flex items-center gap-1.5"
              >
                <span>🗑️</span>
                <span>Clear All</span>
              </button>
            </div>
          </div>

          {recordedTrials.length === 0 ? (
            <div className="p-8 text-center text-slate-500 font-mono text-xs">
              No trial observations recorded yet. Adjust parameters and click "Record Trial" to log data points.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 bg-[#020813]/60">
                    <th className="py-2.5 px-3">Time</th>
                    <th className="py-2.5 px-3">Origin / Tool</th>
                    {currentLab.observationColumns.map(col => (
                      <th key={col.id} className="py-2.5 px-3">
                        {col.label} ({col.unit})
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {recordedTrials.map((t, idx) => (
                    <tr key={t.id || idx} className="hover:bg-slate-800/20">
                      <td className="py-2.5 px-3 text-slate-400">{t.timestamp}</td>
                      <td className="py-2.5 px-3">
                        <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-emerald-400 border border-slate-700">
                          {t.source || "Manual Trial"}
                        </span>
                      </td>
                      {currentLab.observationColumns.map(col => (
                        <td key={col.id} className="py-2.5 px-3 font-bold text-white">
                          {t[col.id] !== undefined ? t[col.id] : (t.status || t.board || "—")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* VIEW 3: VIVA-VOCE & RUBRIC */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "viva" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
            <h3 className="font-bold text-base text-white flex items-center gap-2">
              <span>🎓</span>
              <span>Viva-Voce Examination Questions</span>
            </h3>
            <div className="space-y-3 font-mono text-xs">
              {currentLab.vivaQuestions.map((vq, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-[#020813] border border-slate-800 space-y-2">
                  <div className="text-white font-bold flex items-start gap-2">
                    <span style={{ color: themeColor }}>Q{idx + 1}:</span>
                    <span>{vq.question}</span>
                  </div>
                  <div className="text-slate-300 text-[11px] leading-relaxed pl-6 border-l-2 border-slate-800">
                    {vq.answer}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
            <h3 className="font-bold text-base text-white flex items-center gap-2">
              <span>📐</span>
              <span>Theoretical Formulations (KaTeX / LaTeX)</span>
            </h3>
            <div className="space-y-2.5 font-mono text-xs">
              {currentLab.formulas.map((form, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-[#020813] border border-slate-800 text-slate-200">
                  <code>{form}</code>
                </div>
              ))}
            </div>

            <h4 className="font-bold text-xs text-slate-400 font-mono uppercase tracking-wider pt-2">
              Hardware Apparatus Requisition:
            </h4>
            <ul className="space-y-1 text-xs font-mono text-slate-400 list-disc list-inside">
              {currentLab.apparatus.map((app, i) => (
                <li key={i}>{app}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
