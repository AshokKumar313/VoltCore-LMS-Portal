import React, { useState, useMemo } from 'react';
import { PRIORITY_COURSES, getCourseByCode, getAllCourses, getCourseThemeTokens } from '../data/course_config_schema';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Modular Course Shell Component Architecture (Phase 4 Extension)
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead & Systems Architect: Ashok Kumar A
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 *
 * Enhanced Capabilities:
 *   - Course branding tokens & CSS glow effects (Emerald, Amber, Cyan, Indigo)
 *   - Departmental Badge Icon Suite (DSP, Bandgap, Laser Resonator, ARM Cortex-M)
 *   - State-preserving unit-wise navigation tabs (Units I through V) with Roman numerals
 *   - Dynamic multi-level breadcrumb trails (Home / Course Hub / EC23S01 / Unit III)
 *   - Client-side physics simulators with instant mathematical feedback
 * Hardware Safe: Passive CPU, zero background polling daemons, lightweight calculations.
 * ========================================================================================
 */

// Roman numeral lookup for 5 syllabus units
const ROMAN_NUMERALS = ["I", "II", "III", "IV", "V"];

// -----------------------------------------------------------------------------
// DEPARTMENTAL BADGE ICON SUITE (VECTOR SVGS FOR ANNA UNIVERSITY REG 2023 ECE)
// -----------------------------------------------------------------------------

export function DspWaveformSvg({ className = "w-6 h-6", primaryColor = "#00F0B5" }) {
  return (
    <svg className={className} viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="DSP Waveform & Discrete Stem Spectrum">
      <title>Discrete Signal Processing Waveform & FFT Spectrum</title>
      {/* Background Spectral FFT Frequency Bins */}
      <rect x="8" y="44" width="4" height="12" rx="1" fill={primaryColor} fillOpacity="0.25" />
      <rect x="16" y="32" width="4" height="24" rx="1" fill={primaryColor} fillOpacity="0.35" />
      <rect x="24" y="20" width="4" height="36" rx="1" fill={primaryColor} fillOpacity="0.5" />
      <rect x="32" y="12" width="4" height="44" rx="1" fill={primaryColor} fillOpacity="0.75" />
      <rect x="40" y="24" width="4" height="32" rx="1" fill={primaryColor} fillOpacity="0.5" />
      <rect x="48" y="36" width="4" height="20" rx="1" fill={primaryColor} fillOpacity="0.35" />
      <rect x="56" y="48" width="4" height="8" rx="1" fill={primaryColor} fillOpacity="0.25" />
      {/* Horizontal Discrete Time Axis */}
      <line x1="4" y1="32" x2="60" y2="32" stroke="#475569" strokeWidth="1.5" strokeDasharray="2 2" />
      {/* Continuous Analog Carrier Wave (Faint) */}
      <path d="M4 32 C 12 10, 20 10, 28 32 C 36 54, 44 54, 52 32 C 56 22, 60 26, 62 32" stroke={primaryColor} strokeWidth="1.5" strokeOpacity="0.4" fill="none" />
      {/* Discrete Pulse Sample Stems & Circle Markers */}
      <line x1="12" y1="32" x2="12" y2="18" stroke={primaryColor} strokeWidth="2" strokeLinecap="round" />
      <circle cx="12" cy="18" r="3" fill={primaryColor} />
      <line x1="20" y1="32" x2="20" y2="14" stroke={primaryColor} strokeWidth="2" strokeLinecap="round" />
      <circle cx="20" cy="14" r="3" fill={primaryColor} />
      <line x1="28" y1="32" x2="28" y2="32" stroke={primaryColor} strokeWidth="2" strokeLinecap="round" />
      <circle cx="28" cy="32" r="3" fill={primaryColor} />
      <line x1="36" y1="32" x2="36" y2="48" stroke={primaryColor} strokeWidth="2" strokeLinecap="round" />
      <circle cx="36" cy="48" r="3" fill={primaryColor} />
      <line x1="44" y1="32" x2="44" y2="46" stroke={primaryColor} strokeWidth="2" strokeLinecap="round" />
      <circle cx="44" cy="46" r="3" fill={primaryColor} />
      <line x1="52" y1="32" x2="52" y2="32" stroke={primaryColor} strokeWidth="2" strokeLinecap="round" />
      <circle cx="52" cy="32" r="3" fill={primaryColor} />
    </svg>
  );
}

export function SemiconductorBandgapSvg({ className = "w-6 h-6", primaryColor = "#F59E0B" }) {
  return (
    <svg className={className} viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Semiconductor Bandgap & Carrier Recombination">
      <title>Semiconductor Energy Bandgap & Carrier Dynamics</title>
      {/* Conduction Band (Ec) Upper Block */}
      <path d="M8 12 H56" stroke={primaryColor} strokeWidth="2.5" strokeLinecap="round" />
      <rect x="8" y="6" width="48" height="6" fill={primaryColor} fillOpacity="0.25" rx="1" />
      <text x="50" y="10" fill={primaryColor} fontSize="6" fontFamily="monospace" fontWeight="bold">Ec</text>
      {/* Free Electrons in Conduction Band */}
      <circle cx="18" cy="9" r="2" fill={primaryColor} />
      <circle cx="28" cy="9" r="2" fill={primaryColor} />
      <circle cx="38" cy="9" r="2" fill={primaryColor} />
      {/* Fermi Level (Ef) Dashed Line */}
      <line x1="8" y1="32" x2="56" y2="32" stroke="#FCD34D" strokeWidth="1.5" strokeDasharray="3 3" />
      <text x="50" y="30" fill="#FCD34D" fontSize="6" fontFamily="monospace" fontWeight="bold">Ef</text>
      {/* Forbidden Bandgap Eg Arrow & Indicator */}
      <path d="M10 16 L14 16 M10 48 L14 48 M12 16 L12 48" stroke="#E2E8F0" strokeWidth="1.2" />
      <text x="14" y="34" fill="#E2E8F0" fontSize="7" fontFamily="monospace" fontWeight="bold">Eg</text>
      {/* Valence Band (Ev) Lower Block */}
      <path d="M8 52 H56" stroke={primaryColor} strokeWidth="2.5" strokeLinecap="round" />
      <rect x="8" y="52" width="48" height="6" fill={primaryColor} fillOpacity="0.25" rx="1" />
      <text x="50" y="60" fill={primaryColor} fontSize="6" fontFamily="monospace" fontWeight="bold">Ev</text>
      {/* Holes in Valence Band */}
      <circle cx="22" cy="55" r="2" stroke={primaryColor} strokeWidth="1.2" fill="none" />
      <circle cx="32" cy="55" r="2" stroke={primaryColor} strokeWidth="1.2" fill="none" />
      <circle cx="44" cy="55" r="2" stroke={primaryColor} strokeWidth="1.2" fill="none" />
      {/* Recombination & Photon Transition */}
      <path d="M38 16 L38 46" stroke="#EF4444" strokeWidth="1.5" strokeDasharray="2 2" />
      <path d="M36 42 L38 47 L40 42" stroke="#EF4444" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M40 30 Q44 26 42 22 Q40 18 45 15" stroke="#FBBF24" strokeWidth="1.2" fill="none" />
    </svg>
  );
}

export function LaserResonatorSvg({ className = "w-6 h-6", primaryColor = "#06B6D4" }) {
  return (
    <svg className={className} viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Laser Optical Resonator Cavity">
      <title>Laser Resonator Cavity & Coherent Wavefronts</title>
      {/* Optical Cavity Axis */}
      <line x1="4" y1="32" x2="60" y2="32" stroke="#475569" strokeWidth="1" strokeDasharray="3 2" />
      {/* Left Highly Reflective Mirror (M1, Concave) */}
      <path d="M10 16 Q14 32 10 48" stroke={primaryColor} strokeWidth="3.5" strokeLinecap="round" fill="none" />
      <line x1="7" y1="18" x2="10" y2="20" stroke="#64748B" strokeWidth="1.2" />
      <line x1="7" y1="30" x2="10" y2="32" stroke="#64748B" strokeWidth="1.2" />
      <line x1="7" y1="42" x2="10" y2="44" stroke="#64748B" strokeWidth="1.2" />
      {/* Gain Medium Crystal Slab */}
      <rect x="22" y="20" width="20" height="24" rx="2" fill={primaryColor} fillOpacity="0.2" stroke={primaryColor} strokeWidth="1.5" />
      <circle cx="28" cy="28" r="1.5" fill="#22D3EE" />
      <circle cx="36" cy="26" r="1.5" fill="#22D3EE" />
      <circle cx="32" cy="36" r="1.5" fill="#22D3EE" />
      {/* Standing Wave Cavity Beam */}
      <path d="M12 32 C 18 24, 22 40, 28 32 C 34 24, 38 40, 44 32 C 48 26, 50 36, 52 32" stroke="#67E8F9" strokeWidth="1.8" fill="none" />
      {/* Right Partially Transmissive Output Mirror (M2) */}
      <path d="M52 18 Q48 32 52 46" stroke={primaryColor} strokeWidth="3" strokeLinecap="round" fill="none" />
      {/* Coherent Laser Output Beam & Wavefronts */}
      <line x1="52" y1="32" x2="62" y2="32" stroke="#22D3EE" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M58 26 Q60 32 58 38" stroke="#67E8F9" strokeWidth="1.5" fill="none" />
      <path d="M62 24 Q64 32 62 40" stroke="#67E8F9" strokeWidth="1.5" fill="none" />
    </svg>
  );
}

export function ArmCortexMicrocontrollerSvg({ className = "w-6 h-6", primaryColor = "#6366F1" }) {
  return (
    <svg className={className} viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ARM Cortex-M Microcontroller Architecture">
      <title>ARM Cortex-M Embedded Microcontroller Architecture</title>
      {/* QFP Package External Leads */}
      <line x1="20" y1="6" x2="20" y2="12" stroke="#94A3B8" strokeWidth="1.8" />
      <line x1="28" y1="6" x2="28" y2="12" stroke="#94A3B8" strokeWidth="1.8" />
      <line x1="36" y1="6" x2="36" y2="12" stroke="#94A3B8" strokeWidth="1.8" />
      <line x1="44" y1="6" x2="44" y2="12" stroke="#94A3B8" strokeWidth="1.8" />
      <line x1="20" y1="52" x2="20" y2="58" stroke="#94A3B8" strokeWidth="1.8" />
      <line x1="28" y1="52" x2="28" y2="58" stroke="#94A3B8" strokeWidth="1.8" />
      <line x1="36" y1="52" x2="36" y2="58" stroke="#94A3B8" strokeWidth="1.8" />
      <line x1="44" y1="52" x2="44" y2="58" stroke="#94A3B8" strokeWidth="1.8" />
      <line x1="6" y1="20" x2="12" y2="20" stroke="#94A3B8" strokeWidth="1.8" />
      <line x1="6" y1="28" x2="12" y2="28" stroke="#94A3B8" strokeWidth="1.8" />
      <line x1="6" y1="36" x2="12" y2="36" stroke="#94A3B8" strokeWidth="1.8" />
      <line x1="6" y1="44" x2="12" y2="44" stroke="#94A3B8" strokeWidth="1.8" />
      <line x1="52" y1="20" x2="58" y2="20" stroke="#94A3B8" strokeWidth="1.8" />
      <line x1="52" y1="28" x2="58" y2="28" stroke="#94A3B8" strokeWidth="1.8" />
      <line x1="52" y1="36" x2="58" y2="36" stroke="#94A3B8" strokeWidth="1.8" />
      <line x1="52" y1="44" x2="58" y2="44" stroke="#94A3B8" strokeWidth="1.8" />
      {/* IC Chip Epoxy Body */}
      <rect x="12" y="12" width="40" height="40" rx="4" fill="#090D16" stroke={primaryColor} strokeWidth="2" />
      {/* Pin 1 Marker */}
      <circle cx="17" cy="17" r="1.8" fill={primaryColor} />
      {/* Silicon CPU Core Die */}
      <rect x="20" y="20" width="24" height="24" rx="2" fill={primaryColor} fillOpacity="0.2" stroke={primaryColor} strokeWidth="1.2" />
      {/* Internal Bus Lines */}
      <line x1="20" y1="32" x2="44" y2="32" stroke="#818CF8" strokeWidth="1" strokeDasharray="2 2" />
      <line x1="32" y1="20" x2="32" y2="44" stroke="#818CF8" strokeWidth="1" strokeDasharray="2 2" />
      <text x="24" y="29" fill="#E0E7FF" fontSize="5" fontFamily="monospace" fontWeight="bold">ARM</text>
      <text x="24" y="38" fill={primaryColor} fontSize="5" fontFamily="monospace" fontWeight="bold">M4</text>
    </svg>
  );
}

export function DepartmentalBadgeIcon({ code, className = "w-6 h-6", primaryColor }) {
  switch (code) {
    case "EC23S01":
      return <DspWaveformSvg className={className} primaryColor={primaryColor || "#00F0B5"} />;
    case "EC23C03":
      return <SemiconductorBandgapSvg className={className} primaryColor={primaryColor || "#F59E0B"} />;
    case "EC23E04":
      return <LaserResonatorSvg className={className} primaryColor={primaryColor || "#06B6D4"} />;
    case "EC8702":
      return <ArmCortexMicrocontrollerSvg className={className} primaryColor={primaryColor || "#6366F1"} />;
    default:
      return <span className={className}>⚡</span>;
  }
}

// -----------------------------------------------------------------------------
// MAIN COMPONENT: CourseShellHub
// -----------------------------------------------------------------------------

export default function CourseShellHub({ initialCourseId = "EC23S01", allowCourseSwitch = true }) {
  // Course Selection
  const [selectedCourseId, setSelectedCourseId] = useState(initialCourseId);

  // Active Navigation Tab
  const [activeTab, setActiveTab] = useState("overview");

  // Syllabus Unit Selector (Units 0 to 4 -> Roman I to V)
  const [selectedUnitIndex, setSelectedUnitIndex] = useState(0);

  // Sub-Tab selector for unit view: "topics" | "formulas" | "lab"
  const [unitSubTab, setUnitSubTab] = useState("topics");

  // Prerequisite Checklist State
  const [prereqChecked, setPrereqChecked] = useState({});

  // ---------------------------------------------------------------------------
  // INTERACTIVE SIMULATOR STATES
  // ---------------------------------------------------------------------------

  // EC23S01: Python DSP Filter Simulator State
  const [dspFc, setDspFc] = useState(1200); // Cutoff frequency (Hz)
  const [dspFs, setDspFs] = useState(8000); // Sampling frequency (Hz)
  const [dspOrder, setDspOrder] = useState(4); // Filter order

  // EC23C03: Electronic Devices Diode IV Simulator State
  const [diodeVf, setDiodeVf] = useState(0.70); // Forward voltage (V)
  const [diodeTempK, setDiodeTempK] = useState(300); // Temperature (K)
  const [diodeIs, setDiodeIs] = useState(1e-12); // Reverse saturation current (A)

  // EC23E04: Optics Laser Cavity Stability State
  const [laserL, setLaserL] = useState(0.5); // Cavity length (m)
  const [laserR1, setLaserR1] = useState(1.0); // Mirror 1 radius (m)
  const [laserR2, setLaserR2] = useState(0.8); // Mirror 2 radius (m)

  // EC8702: Embedded Systems FreeRTOS Schedulability State
  const [rtosC1, setRtosC1] = useState(10); // Task 1 execution time (ms)
  const [rtosT1, setRtosT1] = useState(50); // Task 1 period (ms)
  const [rtosC2, setRtosC2] = useState(25); // Task 2 execution time (ms)
  const [rtosT2, setRtosT2] = useState(80); // Task 2 period (ms)

  // Resolve current active course
  const currentCourse = useMemo(() => {
    return getCourseByCode(selectedCourseId) || PRIORITY_COURSES["EC23S01"];
  }, [selectedCourseId]);

  const allCourses = useMemo(() => getAllCourses(), []);
  const currentUnit = currentCourse.syllabusUnits[selectedUnitIndex] || currentCourse.syllabusUnits[0];
  const theme = currentCourse.visualTheme;

  // Toggle prerequisite checklist
  const togglePrereq = (idx) => {
    setPrereqChecked(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  // ---------------------------------------------------------------------------
  // SIMULATION COMPUTATIONS
  // ---------------------------------------------------------------------------

  // 1. EC23S01: DSP Butterworth Frequency Response
  const dspSimulationResult = useMemo(() => {
    const nyquist = dspFs / 2;
    const normCutoff = dspFc / nyquist;
    const testFreqs = [200, 500, 1000, 1200, 1500, 2000, 3000];
    const points = testFreqs.map(f => {
      const ratio = f / dspFc;
      const magGain = 1 / Math.sqrt(1 + Math.pow(ratio, 2 * dspOrder));
      const magDb = 20 * Math.log10(magGain);
      return { freq: f, magGain: magGain.toFixed(4), magDb: magDb.toFixed(2) };
    });
    return { normCutoff: normCutoff.toFixed(3), points };
  }, [dspFc, dspFs, dspOrder]);

  // 2. EC23C03: Shockley Diode IV Calculation
  const diodeSimulationResult = useMemo(() => {
    const q = 1.602e-19;
    const k = 1.38e-23;
    const vt = (k * diodeTempK) / q; // Thermal voltage (approx 25.9mV at 300K)
    const currentA = diodeIs * (Math.exp(diodeVf / vt) - 1);
    const currentMa = currentA * 1000;
    const dynamicRes = currentA > 0 ? (vt / currentA).toFixed(2) : "Infinity";
    return {
      vtMv: (vt * 1000).toFixed(2),
      currentMa: currentMa < 1000 ? currentMa.toFixed(3) : currentMa.toExponential(3),
      dynamicRes
    };
  }, [diodeVf, diodeTempK, diodeIs]);

  // 3. EC23E04: Optics Laser Resonator Stability Calculation
  const laserSimulationResult = useMemo(() => {
    const g1 = 1 - (laserL / laserR1);
    const g2 = 1 - (laserL / laserR2);
    const gProd = g1 * g2;
    const isStable = (gProd >= 0 && gProd <= 1);
    return {
      g1: g1.toFixed(3),
      g2: g2.toFixed(3),
      gProd: gProd.toFixed(3),
      isStable
    };
  }, [laserL, laserR1, laserR2]);

  // 4. EC8702: FreeRTOS Liu & Layland Schedulability Bound
  const rtosSimulationResult = useMemo(() => {
    const u1 = rtosC1 / rtosT1;
    const u2 = rtosC2 / rtosT2;
    const totalU = (u1 + u2) * 100;
    const bound = 2 * (Math.pow(2, 1 / 2) - 1) * 100; // approx 82.84%
    const isSchedulable = totalU <= bound;
    return {
      u1Pct: (u1 * 100).toFixed(1),
      u2Pct: (u2 * 100).toFixed(1),
      totalUPct: totalU.toFixed(1),
      boundPct: bound.toFixed(2),
      isSchedulable
    };
  }, [rtosC1, rtosT1, rtosC2, rtosT2]);

  return (
    <div
      data-course={currentCourse.code}
      className="w-full max-w-7xl mx-auto px-4 py-6 space-y-6 font-sans text-slate-200"
    >
      
      {/* --------------------------------------------------------------------- */}
      {/* 1. DYNAMIC BREADCRUMB TRAIL (STATE-PRESERVING DEEP LINK ROUTING) */}
      {/* --------------------------------------------------------------------- */}
      <nav className="flex items-center gap-2 text-xs font-mono text-slate-400 flex-wrap p-2.5 rounded-xl bg-[#020813]/80 border border-slate-800" aria-label="Course Breadcrumb">
        <a href="/" className="hover:text-emerald-400 transition-colors flex items-center gap-1">
          <span>🏠</span>
          <span>Home</span>
        </a>
        <span className="text-slate-600">/</span>
        <a href="/course-hub" className="hover:text-emerald-400 transition-colors">
          Course Hub
        </a>
        <span className="text-slate-600">/</span>
        <button
          onClick={() => setActiveTab("overview")}
          className="font-bold hover:underline transition-all flex items-center gap-1.5"
          style={{ color: theme.primaryColor }}
          title={`Switch to ${currentCourse.code} Overview`}
        >
          <DepartmentalBadgeIcon code={currentCourse.code} className="w-3.5 h-3.5 inline" primaryColor={theme.primaryColor} />
          <span>{currentCourse.code}</span>
        </button>
        <span className="text-slate-600">/</span>
        <button
          onClick={() => { setActiveTab("syllabus"); setUnitSubTab("topics"); }}
          className="text-white font-semibold hover:underline transition-all"
          title={`Jump to Unit ${ROMAN_NUMERALS[selectedUnitIndex]}`}
        >
          Unit {ROMAN_NUMERALS[selectedUnitIndex]}: {currentUnit.title}
        </button>
        {activeTab !== "overview" && activeTab !== "syllabus" && (
          <>
            <span className="text-slate-600">/</span>
            <span className="text-slate-300 capitalize">{activeTab}</span>
          </>
        )}
      </nav>

      {/* --------------------------------------------------------------------- */}
      {/* 2. COURSE CATALOG SELECTOR BAR */}
      {/* --------------------------------------------------------------------- */}
      {allowCourseSwitch && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-2xl bg-[#041026] border border-slate-800 font-mono text-xs shadow-lg">
          <div className="flex items-center gap-2 text-slate-400">
            <span className="text-base">🎓</span>
            <span className="font-bold text-slate-300 uppercase tracking-wider">ECE Regulation 2023 Courses:</span>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {allCourses.map((c) => {
              const isSelected = selectedCourseId === c.code;
              return (
                <button
                  key={c.code}
                  onClick={() => {
                    setSelectedCourseId(c.code);
                    setSelectedUnitIndex(0);
                  }}
                  className={`px-3 py-1.5 rounded-xl transition-all flex items-center gap-2 font-bold ${
                    isSelected
                      ? `scale-105 shadow-lg border ${c.visualTheme.badgeClass}`
                      : "bg-[#020813]/60 text-slate-400 hover:text-white border border-slate-800"
                  }`}
                  style={{
                    borderColor: isSelected ? c.visualTheme.primaryColor : undefined
                  }}
                >
                  <DepartmentalBadgeIcon code={c.code} className="w-4 h-4" primaryColor={c.visualTheme.primaryColor} />
                  <span>{c.code}</span>
                  <span className="hidden md:inline font-normal text-slate-400 text-[10px]">
                    ({c.shortTitle})
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* 3. DYNAMIC PER-COURSE HERO HEADER (HARDWARE-ACCELERATED GLOW BORDERS) */}
      {/* --------------------------------------------------------------------- */}
      <div
        className={`relative overflow-hidden rounded-3xl p-6 sm:p-8 border shadow-2xl transition-all duration-300 ${theme.cardClass}`}
        style={{
          borderColor: theme.borderAccent
        }}
      >
        {/* Hardware-accelerated radial glow backdrop */}
        <div
          className="absolute -top-24 -right-24 w-80 h-80 rounded-full blur-3xl pointer-events-none opacity-25"
          style={{ backgroundColor: theme.primaryColor }}
        ></div>

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-start gap-4 sm:gap-5">
            {/* Departmental Icon Avatar Badge */}
            <div
              className={`relative w-16 h-16 sm:w-20 sm:h-20 rounded-2xl p-[2.5px] flex-shrink-0 transition-all ${theme.glowClass}`}
              style={{
                background: `linear-gradient(135deg, ${theme.gradientFrom}, ${theme.gradientTo})`
              }}
            >
              <div className="w-full h-full bg-[#020813] rounded-[14px] flex items-center justify-center">
                <DepartmentalBadgeIcon code={currentCourse.code} className="w-10 h-10 sm:w-12 sm:h-12" primaryColor={theme.primaryColor} />
              </div>
              <span
                className="absolute -bottom-1 -right-1 h-3.5 w-3.5 rounded-full ring-2 ring-[#020813] animate-pulse"
                style={{ backgroundColor: theme.primaryColor }}
              ></span>
            </div>

            <div className="space-y-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold uppercase tracking-wider ${theme.badgeClass}`}>
                  {currentCourse.category}
                </span>
                <span className="px-2 py-0.5 rounded-full bg-[#020813] text-slate-400 border border-slate-800 text-[10px] font-mono">
                  Semester {currentCourse.semester} • {currentCourse.credits} Credits ({currentCourse.lectureTutorialLabHours})
                </span>
              </div>

              <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight font-sans">
                {currentCourse.code}: {currentCourse.title}
              </h1>

              <p className="text-slate-300 text-xs sm:text-sm max-w-2xl leading-relaxed">
                {currentCourse.description}
              </p>
            </div>
          </div>

          {/* Quick Laboratory & Infrastructure HUD */}
          <div className="flex flex-col gap-2 font-mono text-xs min-w-[210px] flex-shrink-0">
            <div className="p-3 rounded-xl bg-[#020813]/90 border border-slate-800 space-y-1">
              <div className="text-[10px] text-slate-500 uppercase font-semibold">Active Lab Engine</div>
              <div className="text-white font-bold text-xs truncate">{currentCourse.labSimulation.simulationPlatform}</div>
              <div className="text-[10px] text-slate-400 truncate">{currentCourse.labSimulation.labRoom}</div>
            </div>
            <div className="p-2.5 rounded-xl bg-[#020813]/90 border border-slate-800 flex items-center justify-between text-[11px]">
              <span className="text-slate-400">Total Hours:</span>
              <span className="font-bold" style={{ color: theme.primaryColor }}>
                {currentCourse.credits === 3 ? "45 Lecture" : "48 Practical"}
              </span>
            </div>
          </div>
        </div>

        {/* ------------------------------------------------------------------- */}
        {/* PRIMARY NAVIGATION TABS */}
        {/* ------------------------------------------------------------------- */}
        <div className="mt-6 flex flex-wrap gap-2 border-t border-slate-800/80 pt-5">
          {[
            { id: "overview", label: "Overview", icon: "📋" },
            { id: "syllabus", label: "Syllabus (Units I-V)", icon: "📖" },
            { id: "outcomes", label: "Course Outcomes (CO-PO)", icon: "🎯" },
            { id: "prerequisites", label: "Prerequisites & DAG", icon: "🔗" },
            { id: "simulator", label: "Lab Simulator", icon: "⚡" },
            { id: "textbooks", label: "Textbooks & NPTEL", icon: "📚" }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all flex items-center gap-1.5 ${
                activeTab === tab.id
                  ? `${theme.activeTabClass} scale-102`
                  : "bg-[#020813]/60 text-slate-400 hover:text-white hover:bg-slate-800/60 border border-slate-800"
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* --------------------------------------------------------------------- */}
      {/* TAB 1: COURSE OVERVIEW */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
              <h3 className="font-bold text-base text-white flex items-center gap-2">
                <span>🏛️ Course Academic Profile</span>
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Formally sanctioned under Anna University Regulation 2023 for Bachelor of Engineering in Electronics and Communication Engineering at Madras Institute of Technology (MIT Campus). Aligned with Choice-Based Credit System (CBCS) and Outcome-Based Education (OBE) Tier-1 accreditation benchmarks.
              </p>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 font-mono text-xs">
                <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase">Course Code</div>
                  <div className="text-white font-bold text-sm mt-0.5">{currentCourse.code}</div>
                </div>
                <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase">Semester</div>
                  <div className="text-white font-bold text-sm mt-0.5">Sem {currentCourse.semester}</div>
                </div>
                <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase">Credits (L-T-P)</div>
                  <div className="text-emerald-400 font-bold text-sm mt-0.5">{currentCourse.credits} ({currentCourse.lectureTutorialLabHours})</div>
                </div>
                <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase">Regulation</div>
                  <div className="text-white font-bold text-xs mt-0.5">Reg 2023</div>
                </div>
                <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase">Syllabus Hours</div>
                  <div className="text-cyan-400 font-bold text-sm mt-0.5">{currentCourse.credits === 3 ? "45 Hours" : "48 Hours"}</div>
                </div>
                <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase">Assessment</div>
                  <div className="text-amber-400 font-bold text-xs mt-0.5">40 Internal / 60 End-Sem</div>
                </div>
              </div>

              {currentCourse.corequisites.length > 0 && (
                <div className="p-3 rounded-xl bg-[#020813] border border-slate-800 text-xs font-mono flex items-center justify-between">
                  <span className="text-slate-400">Concurrent Corequisites:</span>
                  <span className="text-amber-300 font-bold">{currentCourse.corequisites.join(", ")}</span>
                </div>
              )}
            </div>

            {/* Laboratory Infrastructure */}
            <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
              <h3 className="font-bold text-base text-white flex items-center gap-2">
                <span>🔬 Laboratory & Infrastructure</span>
              </h3>
              <div className="space-y-3 font-mono text-xs">
                <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase">Assigned Laboratory</div>
                  <div className="text-white font-bold mt-0.5">{currentCourse.labSimulation.labRoom}</div>
                </div>
                <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase">Simulation Engine</div>
                  <div className="text-emerald-400 font-bold mt-0.5">{currentCourse.labSimulation.simulationPlatform}</div>
                </div>
                <div className="p-3 rounded-xl bg-[#020813] border border-slate-800 space-y-1">
                  <div className="text-[10px] text-slate-500 uppercase">Hardware Apparatus:</div>
                  <ul className="text-slate-300 list-disc list-inside space-y-0.5 text-[11px]">
                    {currentCourse.labSimulation.apparatusList.map((app, i) => (
                      <li key={i}>{app}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 2: UNIT-WISE SYLLABUS NAVIGATION (UNITS I THROUGH V) */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "syllabus" && (
        <div className="space-y-6">
          {/* Unit Selector Strip (Units I to V with Roman Numerals) */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 font-mono text-xs">
            {currentCourse.syllabusUnits.map((unit, idx) => {
              const isSelected = selectedUnitIndex === idx;
              return (
                <button
                  key={unit.unitNumber}
                  onClick={() => setSelectedUnitIndex(idx)}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    isSelected
                      ? `bg-[#020813] shadow-lg border-2 ${theme.glowClass}`
                      : "bg-[#041026] border-slate-800 hover:border-slate-700 text-slate-400"
                  }`}
                  style={{
                    borderColor: isSelected ? theme.primaryColor : undefined
                  }}
                >
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-white">Unit {ROMAN_NUMERALS[idx]}</span>
                    <span className="text-[10px] text-slate-500">{unit.hours}h</span>
                  </div>
                  <div className="text-[11px] truncate mt-1" style={{ color: isSelected ? theme.primaryColor : undefined }}>
                    {unit.title}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Unit Sub-Tab Selector: Topics vs Formulas vs Laboratory */}
          <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
            {[
              { id: "topics", label: "Syllabus Topics", icon: "📋" },
              { id: "formulas", label: "KaTeX Formulations", icon: "📐" },
              { id: "lab", label: "Lab Exercises & Simulator", icon: "🧪" }
            ].map(st => (
              <button
                key={st.id}
                onClick={() => setUnitSubTab(st.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all flex items-center gap-1.5 ${
                  unitSubTab === st.id
                    ? "bg-[#020813] text-white border border-slate-700"
                    : "text-slate-400 hover:text-white"
                }`}
                style={{
                  color: unitSubTab === st.id ? theme.primaryColor : undefined,
                  borderColor: unitSubTab === st.id ? theme.primaryColor : undefined
                }}
              >
                <span>{st.icon}</span>
                <span>{st.label}</span>
              </button>
            ))}
          </div>

          {/* Active Unit Detailed Content */}
          <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
              <div>
                <div className="text-xs font-mono font-bold" style={{ color: theme.primaryColor }}>
                  UNIT {ROMAN_NUMERALS[selectedUnitIndex]} • {currentUnit.hours} LECTURE/PRACTICAL HOURS
                </div>
                <h3 className="text-xl font-extrabold text-white font-sans mt-0.5">
                  {currentUnit.title}
                </h3>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-mono font-bold ${theme.badgeClass}`}>
                {currentCourse.code} • Unit {ROMAN_NUMERALS[selectedUnitIndex]}
              </span>
            </div>

            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              {currentUnit.description}
            </p>

            {/* Sub-view: Topics List */}
            {unitSubTab === "topics" && (
              <div className="space-y-3">
                <div className="text-xs font-bold text-slate-300 font-mono uppercase tracking-wider">
                  Key Topics & Syllabus Deliverables:
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                  {currentUnit.topics.map((topic, i) => (
                    <div key={i} className="p-3 rounded-xl bg-[#020813] border border-slate-800 text-xs font-mono text-slate-300 flex items-start gap-2.5 hover:border-slate-700 transition-colors">
                      <span className="font-bold" style={{ color: theme.primaryColor }}>{i + 1}.</span>
                      <span>{topic}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Sub-view: KaTeX Key Mathematical Formulas Callout Box */}
            {unitSubTab === "formulas" && (
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-xs font-mono font-bold" style={{ color: theme.primaryColor }}>
                  <span>📐</span>
                  <span>Key Mathematical & Physical Formulations (KaTeX / LaTeX):</span>
                </div>
                {currentUnit.keyFormulas && currentUnit.keyFormulas.length > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {currentUnit.keyFormulas.map((formula, i) => (
                      <div key={i} className="p-4 rounded-xl bg-[#020813] border border-slate-800 text-center font-mono text-xs sm:text-sm shadow-md" style={{ borderColor: theme.borderAccent }}>
                        <code className="text-slate-100">{formula}</code>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 rounded-xl bg-[#020813] text-slate-400 text-xs font-mono">
                    Formulations mapped under general course outcomes.
                  </div>
                )}
              </div>
            )}

            {/* Sub-view: Associated Lab Experiments & Quick Simulator Jump */}
            {unitSubTab === "lab" && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-mono font-bold text-emerald-400 flex items-center gap-2">
                    <span>🧪</span>
                    <span>Associated Hands-On Laboratory Exercises:</span>
                  </div>
                  <button
                    onClick={() => setActiveTab("simulator")}
                    className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs font-mono font-bold transition-all flex items-center gap-1.5"
                  >
                    <span>⚡ Launch Simulator Workbench</span>
                    <span>→</span>
                  </button>
                </div>

                {currentUnit.labComponents && currentUnit.labComponents.length > 0 ? (
                  <ul className="text-xs font-mono text-slate-300 space-y-2 list-none">
                    {currentUnit.labComponents.map((lab, i) => (
                      <li key={i} className="p-3 rounded-xl bg-[#020813] border border-slate-800 flex items-center gap-2">
                        <span className="text-emerald-400 font-bold">[{i + 1}]</span>
                        <span>{lab}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="p-4 rounded-xl bg-[#020813] text-slate-400 text-xs font-mono">
                    Theoretical unit; computational verification conducted via the lab simulator tab.
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 3: COURSE OUTCOMES (CO-PO ATTAINMENT) */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "outcomes" && (
        <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
            <div>
              <h3 className="font-bold text-base text-white">Course Outcomes (COs) & NBA Tier-1 Mapping</h3>
              <div className="text-xs text-slate-400">Anna University Regulation 2023 OBE Attainment Matrix</div>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-[#020813] border border-slate-800 text-emerald-400">
              Bloom's Taxonomy: L3-L6 HOTS
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 bg-[#020813]/60">
                  <th className="py-2.5 px-3">CO ID</th>
                  <th className="py-2.5 px-3">Course Outcome Statement</th>
                  <th className="py-2.5 px-3">Bloom's Level</th>
                  <th className="py-2.5 px-2">Mapped POs</th>
                  <th className="py-2.5 px-2">Mapped PSOs</th>
                  <th className="py-2.5 px-2 text-right">Target Attainment</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {currentCourse.courseOutcomes.map((co) => (
                  <tr key={co.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-3 font-bold" style={{ color: theme.primaryColor }}>{co.id}</td>
                    <td className="py-3 px-3 text-slate-200 font-sans max-w-md">{co.description}</td>
                    <td className="py-3 px-3 text-amber-300 font-semibold">{co.bloomLevel}</td>
                    <td className="py-3 px-2 text-slate-300">{co.mappedPOs.join(", ")}</td>
                    <td className="py-3 px-2 text-slate-300">{co.mappedPSOs.join(", ")}</td>
                    <td className="py-3 px-2 text-right text-emerald-400 font-bold">{co.targetAttainmentPct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 4: PREREQUISITES & DAG PATHWAY */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "prerequisites" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Prerequisite DAG Pathway */}
            <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
              <h3 className="font-bold text-base text-white flex items-center gap-2">
                <span>🔗 Prerequisite DAG Dependency Graph</span>
              </h3>
              <p className="text-xs text-slate-400">
                Directed Acyclic Graph mapping foundational knowledge bridges to {currentCourse.code}.
              </p>

              <div className="space-y-3 font-mono text-xs">
                {currentCourse.prerequisiteDag.map((link, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-[#020813] border border-slate-800 space-y-1.5">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-emerald-400">{link.fromCourse} → {link.toCourse}</span>
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 font-bold uppercase">
                        {link.relationship} prerequisite
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-300">
                      Concept Bridge: <span className="text-white font-sans">{link.topicBridge}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Diagnostic Self-Assessment Checklist */}
            <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
              <h3 className="font-bold text-base text-white flex items-center gap-2">
                <span>📝 Student Prerequisite Readiness Audit</span>
              </h3>
              <p className="text-xs text-slate-400">
                Check off core competencies to confirm mathematical and theoretical readiness.
              </p>

              <div className="space-y-2 font-mono text-xs">
                {currentCourse.prerequisites.map((req, idx) => (
                  <button
                    key={idx}
                    onClick={() => togglePrereq(idx)}
                    className={`w-full p-3 rounded-xl border text-left flex items-center justify-between transition-colors ${
                      prereqChecked[idx]
                        ? "bg-emerald-950/20 border-emerald-500/40 text-emerald-300"
                        : "bg-[#020813] border-slate-800 text-slate-300 hover:border-slate-700"
                    }`}
                  >
                    <span className="truncate">{req}</span>
                    <span>{prereqChecked[idx] ? "✅ VERIFIED" : "⭕ PENDING"}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 5: LAB SIMULATOR WORKBENCH (DYNAMIC PER COURSE) */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "simulator" && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
              <div className="flex items-center gap-3">
                <DepartmentalBadgeIcon code={currentCourse.code} className="w-8 h-8" primaryColor={theme.primaryColor} />
                <div>
                  <div className="text-xs font-mono font-bold" style={{ color: theme.primaryColor }}>
                    INTERACTIVE SIMULATOR • {currentCourse.labSimulation.simulationPlatform.toUpperCase()}
                  </div>
                  <h3 className="text-xl font-extrabold text-white font-sans mt-0.5">
                    {currentCourse.code} Live Laboratory Workbench
                  </h3>
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-mono font-bold ${theme.badgeClass}`}>
                100% Client-Side Physics
              </span>
            </div>

            {/* 1. EC23S01: Python DSP Filter Response */}
            {currentCourse.code === "EC23S01" && (
              <div className="space-y-5">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
                  <div>
                    <label className="text-slate-400">Cutoff Frequency: <strong className="text-white">{dspFc} Hz</strong></label>
                    <input
                      type="range" min="300" max="3000" step="50"
                      value={dspFc} onChange={(e) => setDspFc(Number(e.target.value))}
                      className="w-full mt-2 accent-[#00F0B5]"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400">Sampling Rate: <strong className="text-white">{dspFs} Hz</strong></label>
                    <input
                      type="range" min="4000" max="16000" step="1000"
                      value={dspFs} onChange={(e) => setDspFs(Number(e.target.value))}
                      className="w-full mt-2 accent-[#00F0B5]"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400">Butterworth Order: <strong className="text-white">{dspOrder}</strong></label>
                    <input
                      type="range" min="1" max="8" step="1"
                      value={dspOrder} onChange={(e) => setDspOrder(Number(e.target.value))}
                      className="w-full mt-2 accent-[#00F0B5]"
                    />
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs font-mono">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 bg-[#020813]/60">
                        <th className="py-2 px-3">Test Frequency (Hz)</th>
                        <th className="py-2 px-3">Magnitude Gain |H(f)|</th>
                        <th className="py-2 px-3">Attenuation (dB)</th>
                        <th className="py-2 px-3">Regime</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {dspSimulationResult.points.map(pt => (
                        <tr key={pt.freq} className="hover:bg-slate-800/30">
                          <td className="py-2 px-3 font-bold text-white">{pt.freq} Hz</td>
                          <td className="py-2 px-3 text-[#00F0B5]">{pt.magGain}</td>
                          <td className="py-2 px-3 text-amber-300">{pt.magDb} dB</td>
                          <td className="py-2 px-3 text-[11px] text-slate-400">
                            {pt.freq <= dspFc ? "Passband" : "Stopband Attenuation"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* 2. EC23C03: Electronic Devices Diode IV Simulator */}
            {currentCourse.code === "EC23C03" && (
              <div className="space-y-5">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 font-mono text-xs">
                  <div>
                    <label className="text-slate-400">Forward Bias Voltage: <strong className="text-amber-400">{diodeVf.toFixed(2)} V</strong></label>
                    <input
                      type="range" min="0.10" max="0.85" step="0.01"
                      value={diodeVf} onChange={(e) => setDiodeVf(Number(e.target.value))}
                      className="w-full mt-2 accent-amber-500"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400">Junction Temp: <strong className="text-white">{diodeTempK} K ({diodeTempK - 273}°C)</strong></label>
                    <input
                      type="range" min="250" max="400" step="5"
                      value={diodeTempK} onChange={(e) => setDiodeTempK(Number(e.target.value))}
                      className="w-full mt-2 accent-amber-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3 font-mono text-xs">
                  <div className="p-3.5 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Thermal Voltage (VT)</div>
                    <div className="text-white font-bold text-base mt-0.5">{diodeSimulationResult.vtMv} mV</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Diode Current (ID)</div>
                    <div className="text-amber-400 font-bold text-base mt-0.5">{diodeSimulationResult.currentMa} mA</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Dynamic Resistance (rd)</div>
                    <div className="text-emerald-400 font-bold text-base mt-0.5">{diodeSimulationResult.dynamicRes} Ω</div>
                  </div>
                </div>
              </div>
            )}

            {/* 3. EC23E04: Optics Laser Cavity Stability Calculator */}
            {currentCourse.code === "EC23E04" && (
              <div className="space-y-5">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
                  <div>
                    <label className="text-slate-400">Cavity Length (L): <strong className="text-cyan-400">{laserL.toFixed(2)} m</strong></label>
                    <input
                      type="range" min="0.1" max="1.5" step="0.05"
                      value={laserL} onChange={(e) => setLaserL(Number(e.target.value))}
                      className="w-full mt-2 accent-cyan-500"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400">Mirror 1 RoC (R1): <strong className="text-white">{laserR1.toFixed(2)} m</strong></label>
                    <input
                      type="range" min="0.2" max="2.0" step="0.1"
                      value={laserR1} onChange={(e) => setLaserR1(Number(e.target.value))}
                      className="w-full mt-2 accent-cyan-500"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400">Mirror 2 RoC (R2): <strong className="text-white">{laserR2.toFixed(2)} m</strong></label>
                    <input
                      type="range" min="0.2" max="2.0" step="0.1"
                      value={laserR2} onChange={(e) => setLaserR2(Number(e.target.value))}
                      className="w-full mt-2 accent-cyan-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-4 gap-3 font-mono text-xs">
                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Parameter g1</div>
                    <div className="text-white font-bold text-sm mt-0.5">{laserSimulationResult.g1}</div>
                  </div>
                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Parameter g2</div>
                    <div className="text-white font-bold text-sm mt-0.5">{laserSimulationResult.g2}</div>
                  </div>
                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Product g1*g2</div>
                    <div className="text-cyan-300 font-bold text-sm mt-0.5">{laserSimulationResult.gProd}</div>
                  </div>
                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Stability (0 ≤ g1g2 ≤ 1)</div>
                    <div className={`font-bold text-sm mt-0.5 ${laserSimulationResult.isStable ? "text-emerald-400" : "text-rose-400"}`}>
                      {laserSimulationResult.isStable ? "STABLE RESONATOR" : "UNSTABLE"}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* 4. EC8702: FreeRTOS Schedulability Analyzer */}
            {currentCourse.code === "EC8702" && (
              <div className="space-y-5">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 font-mono text-xs">
                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800 space-y-2">
                    <div className="font-bold text-white">Task 1: Sensor Sampling (C1 / T1)</div>
                    <div className="flex justify-between text-slate-400">
                      <span>Exec: {rtosC1}ms</span>
                      <span>Period: {rtosT1}ms</span>
                    </div>
                    <input
                      type="range" min="5" max="30" step="1"
                      value={rtosC1} onChange={(e) => setRtosC1(Number(e.target.value))}
                      className="w-full accent-indigo-500"
                    />
                  </div>

                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800 space-y-2">
                    <div className="font-bold text-white">Task 2: Telemetry Stream (C2 / T2)</div>
                    <div className="flex justify-between text-slate-400">
                      <span>Exec: {rtosC2}ms</span>
                      <span>Period: {rtosT2}ms</span>
                    </div>
                    <input
                      type="range" min="10" max="60" step="1"
                      value={rtosC2} onChange={(e) => setRtosC2(Number(e.target.value))}
                      className="w-full accent-indigo-500"
                    />
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-[#020813] border border-slate-800 font-mono text-xs flex justify-between items-center">
                  <div>
                    <div className="text-white font-bold">Total CPU Utilization: {rtosSimulationResult.totalUPct}%</div>
                    <div className="text-slate-400 text-[11px] mt-0.5">
                      Liu &amp; Layland Bound: ≤ {rtosSimulationResult.boundPct}% for 2 periodic tasks
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full font-bold text-xs ${
                    rtosSimulationResult.isSchedulable ? "bg-emerald-950 text-emerald-300 border border-emerald-500/40" : "bg-rose-950 text-rose-300 border border-rose-500/40"
                  }`}>
                    {rtosSimulationResult.isSchedulable ? "100% SCHEDULABLE" : "OVERLOAD / MISSED DEADLINE"}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 6: TEXTBOOKS & NPTEL MAPPING */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "textbooks" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
            <h3 className="font-bold text-base text-white flex items-center gap-2">
              <span>📖 Prescribed Textbooks (Reg 2023)</span>
            </h3>
            <ul className="space-y-2 text-xs font-mono text-slate-300">
              {currentCourse.textbooks.map((tb, i) => (
                <li key={i} className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                  <span className="font-bold" style={{ color: theme.primaryColor }}>[{i + 1}] </span>
                  {tb}
                </li>
              ))}
            </ul>

            <h4 className="font-bold text-xs text-slate-400 font-mono uppercase tracking-wider pt-2">
              Reference Literature:
            </h4>
            <ul className="space-y-2 text-xs font-mono text-slate-400">
              {currentCourse.referenceBooks.map((rb, i) => (
                <li key={i} className="p-2.5 rounded-lg bg-[#020813]/60 border border-slate-800">
                  {rb}
                </li>
              ))}
            </ul>
          </div>

          <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
            <h3 className="font-bold text-base text-white flex items-center gap-2">
              <span>📺 NPTEL & Digital Lecture Mapping</span>
            </h3>
            <div className="p-4 rounded-xl bg-[#020813] border border-slate-800 space-y-2 font-mono text-xs">
              <div className="text-slate-400 uppercase text-[10px]">Associated NPTEL Course ID:</div>
              <div className="font-bold text-sm" style={{ color: theme.primaryColor }}>{currentCourse.nptelCourseId || "noc23-ee44"}</div>
              <div className="text-slate-400 text-[11px] leading-relaxed">
                Lectures mapped directly from Indian Institute of Technology (IIT) faculties to Anna University Regulation 2023 curriculum units.
              </div>
            </div>

            <a
              href="/nptel-player"
              className="block w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-center text-xs font-mono font-bold text-emerald-300 transition-colors"
            >
              Open NPTEL Smart Lecture Player →
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
