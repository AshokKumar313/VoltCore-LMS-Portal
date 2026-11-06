import React, { useState, useMemo } from 'react';
import { PRIORITY_COURSES, getCourseByCode, getAllCourses } from '../data/course_config_schema';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Modular Course Shell Component Architecture (Phase 4)
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead & Systems Architect: Ashok Kumar A
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 *
 * Reusable Course Container supporting all priority courses:
 *   - EC23S01: Numerical and Signal Processing Practice Through Python
 *   - EC23C03: Electronic Devices
 *   - EC23E04: Optics and Lasers
 *   - EC8702:  Embedded Systems
 *
 * Dynamic Features:
 *   - Per-course theme hydration (primaryColor, accentGlow, borderAccent, icon)
 *   - Unit-wise syllabus breakdown (Units 1–5) with KaTeX formula callout boxes
 *   - Course Outcomes (CO1-CO5) and Bloom's Rigor PO/PSO attainment matrix
 *   - Prerequisite DAG visualizer and student diagnostic self-assessment
 *   - Dedicated interactive client-side simulators with live formula computation
 *   - Peer-neutral attribution invariant (ECE Undergraduate • MIT Campus)
 * Hardware Safe: Zero background polling daemons, lightweight client calculations.
 * ========================================================================================
 */

export default function CourseShellHub({ initialCourseId = "EC23S01", allowCourseSwitch = true }) {
  // Course Selection
  const [selectedCourseId, setSelectedCourseId] = useState(initialCourseId);

  // Active Navigation Tab
  const [activeTab, setActiveTab] = useState("overview");

  // Syllabus Unit Selector (Units 1 to 5)
  const [selectedUnitIndex, setSelectedUnitIndex] = useState(0);

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

  // 1. EC23S01: DSP Butterworth Frequency Response Points
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
    const rayleighRangeCm = ((Math.PI * Math.pow(0.5e-3, 2)) / 632.8e-9) * 100; // Sample for w0=0.5mm, 632.8nm
    return {
      g1: g1.toFixed(3),
      g2: g2.toFixed(3),
      gProd: gProd.toFixed(3),
      isStable,
      rayleighRangeCm: rayleighRangeCm.toFixed(1)
    };
  }, [laserL, laserR1, laserR2]);

  // 4. EC8702: FreeRTOS Utilization & Liu & Layland Schedulability
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
    <div className="w-full max-w-7xl mx-auto px-4 py-8 space-y-8 font-sans text-slate-200">
      
      {/* --------------------------------------------------------------------- */}
      {/* COURSE SWITCHER BAR (OPTIONAL TOP HUD) */}
      {/* --------------------------------------------------------------------- */}
      {allowCourseSwitch && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-2xl bg-[#041026] border border-slate-800 font-mono text-xs shadow-lg">
          <div className="flex items-center gap-2 text-slate-400">
            <span className="text-base">📚</span>
            <span className="font-bold text-slate-300 uppercase tracking-wider">Course Catalog:</span>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {allCourses.map((c) => (
              <button
                key={c.code}
                onClick={() => {
                  setSelectedCourseId(c.code);
                  setSelectedUnitIndex(0);
                }}
                className={`px-3 py-1.5 rounded-xl transition-all flex items-center gap-1.5 font-bold ${
                  selectedCourseId === c.code
                    ? "bg-[#020813] text-white border scale-102 shadow-md"
                    : "bg-[#020813]/40 text-slate-400 hover:text-white border border-slate-800"
                }`}
                style={{
                  borderColor: selectedCourseId === c.code ? c.visualTheme.primaryColor : "transparent",
                  color: selectedCourseId === c.code ? c.visualTheme.primaryColor : undefined
                }}
              >
                <span>{c.visualTheme.icon}</span>
                <span>{c.code}</span>
                <span className="hidden md:inline font-normal text-slate-400 text-[10px]">
                  ({c.shortTitle})
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* DYNAMIC PER-COURSE HERO HEADER */}
      {/* --------------------------------------------------------------------- */}
      <div
        className="relative overflow-hidden rounded-3xl p-8 border shadow-2xl backdrop-blur-xl transition-all duration-300"
        style={{
          backgroundColor: "#041026",
          borderColor: theme.borderAccent,
          boxShadow: `0 20px 40px -15px ${theme.accentGlow}`
        }}
      >
        <div
          className="absolute top-0 right-0 w-96 h-96 rounded-full blur-3xl pointer-events-none opacity-20"
          style={{ backgroundColor: theme.primaryColor }}
        ></div>

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            {/* Breadcrumb Trail */}
            <div className="text-[11px] font-mono text-slate-400 flex items-center gap-1.5 flex-wrap">
              <span className="text-slate-300">VoltCore Apex</span>
              <span>/</span>
              <span>MIT Campus (ECE)</span>
              <span>/</span>
              <span>Regulation 2023</span>
              <span>/</span>
              <span className="font-bold" style={{ color: theme.primaryColor }}>{currentCourse.code}</span>
            </div>

            {/* Course Code & Title */}
            <div className="flex items-center gap-3">
              <span className="text-3xl">{theme.icon}</span>
              <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-white font-sans">
                {currentCourse.code}: {currentCourse.title}
              </h1>
            </div>

            <p className="text-slate-300 text-sm md:text-base max-w-3xl leading-relaxed">
              {currentCourse.description}
            </p>

            <div className="pt-2 flex flex-wrap items-center gap-2 text-xs font-mono">
              <span className="px-2.5 py-1 rounded-lg bg-[#020813] border border-slate-800 text-slate-300">
                Semester: <strong className="text-white">{currentCourse.semester}</strong>
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[#020813] border border-slate-800 text-slate-300">
                Credits: <strong className="text-white">{currentCourse.credits} ({currentCourse.lectureTutorialLabHours})</strong>
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[#020813] border border-slate-800" style={{ color: theme.primaryColor }}>
                {currentCourse.category}
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[#020813] border border-slate-800 text-emerald-400">
                Simulation: {currentCourse.labSimulation.simulationPlatform}
              </span>
            </div>
          </div>

          {/* Quick HUD Card */}
          <div className="flex flex-col gap-2 font-mono text-xs min-w-[220px]">
            <div className="p-3.5 rounded-2xl bg-[#020813]/90 border border-slate-800 space-y-1">
              <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Active Syllabus Scope</div>
              <div className="text-white font-bold text-sm">5 Units • 45-48 Total Hours</div>
              <div className="text-[10px]" style={{ color: theme.primaryColor }}>5 Verified Course Outcomes (COs)</div>
            </div>
            <div className="p-3 rounded-2xl bg-[#020813]/90 border border-slate-800 flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-slate-300 text-[11px] truncate">{currentCourse.labSimulation.labRoom}</span>
            </div>
          </div>
        </div>

        {/* NAVIGATION TABS */}
        <div className="mt-8 flex flex-wrap gap-2 border-t border-slate-800/80 pt-6">
          {[
            { id: "overview", label: "Course Overview", icon: "📋" },
            { id: "syllabus", label: "Syllabus & KaTeX Units", icon: "📖" },
            { id: "outcomes", label: "Course Outcomes (CO-PO)", icon: "🎯" },
            { id: "prerequisites", label: "Prerequisites & DAG", icon: "🔗" },
            { id: "simulator", label: "Lab Simulator", icon: "⚡" },
            { id: "textbooks", label: "Textbooks & NPTEL", icon: "📚" }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2.5 rounded-xl text-xs md:text-sm font-semibold transition-all flex items-center gap-2 ${
                activeTab === tab.id
                  ? "bg-[#020813] text-white font-bold shadow-lg border scale-102"
                  : "bg-[#020813]/60 text-slate-400 hover:text-white hover:bg-slate-800/60 border border-slate-800"
              }`}
              style={{
                borderColor: activeTab === tab.id ? theme.primaryColor : undefined,
                color: activeTab === tab.id ? theme.primaryColor : undefined
              }}
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
            {/* Detailed Course Specs */}
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

              {/* Corequisite Pill */}
              {currentCourse.corequisites.length > 0 && (
                <div className="p-3 rounded-xl bg-[#020813] border border-slate-800 text-xs font-mono flex items-center justify-between">
                  <span className="text-slate-400">Concurrent Corequisites:</span>
                  <span className="text-amber-300 font-bold">{currentCourse.corequisites.join(", ")}</span>
                </div>
              )}
            </div>

            {/* Laboratory & Simulation Summary */}
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
      {/* TAB 2: SYLLABUS UNITS & KATEX CALLOUTS */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "syllabus" && (
        <div className="space-y-6">
          {/* Unit Selector Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 font-mono text-xs">
            {currentCourse.syllabusUnits.map((unit, idx) => (
              <button
                key={unit.unitNumber}
                onClick={() => setSelectedUnitIndex(idx)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  selectedUnitIndex === idx
                    ? "bg-[#020813] shadow-lg border"
                    : "bg-[#041026] border-slate-800 hover:border-slate-700 text-slate-400"
                }`}
                style={{
                  borderColor: selectedUnitIndex === idx ? theme.primaryColor : undefined
                }}
              >
                <div className="flex justify-between items-center">
                  <span className="font-bold text-white">Unit {unit.unitNumber}</span>
                  <span className="text-[10px] text-slate-500">{unit.hours}h</span>
                </div>
                <div className="text-[11px] truncate mt-1" style={{ color: selectedUnitIndex === idx ? theme.primaryColor : undefined }}>
                  {unit.title}
                </div>
              </button>
            ))}
          </div>

          {/* Active Unit Detailed Content */}
          <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
              <div>
                <div className="text-xs font-mono font-bold" style={{ color: theme.primaryColor }}>
                  UNIT {currentUnit.unitNumber} • {currentUnit.hours} LECTURE/PRACTICAL HOURS
                </div>
                <h3 className="text-xl font-extrabold text-white font-sans mt-0.5">
                  {currentUnit.title}
                </h3>
              </div>
              <span className="px-3 py-1 rounded-full bg-[#020813] border border-slate-800 font-mono text-xs text-slate-300">
                {currentCourse.code} Module
              </span>
            </div>

            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              {currentUnit.description}
            </p>

            {/* Topics List */}
            <div className="space-y-2">
              <div className="text-xs font-bold text-slate-300 font-mono uppercase tracking-wider">
                Key Topics & Syllabus Deliverables:
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {currentUnit.topics.map((topic, i) => (
                  <div key={i} className="p-2.5 rounded-lg bg-[#020813] border border-slate-800 text-xs font-mono text-slate-300 flex items-start gap-2">
                    <span style={{ color: theme.primaryColor }}>•</span>
                    <span>{topic}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* LaTeX / KaTeX Key Mathematical Formulas Callout Box */}
            {currentUnit.keyFormulas && currentUnit.keyFormulas.length > 0 && (
              <div className="p-4 rounded-xl bg-[#020813] border space-y-2" style={{ borderColor: theme.borderAccent }}>
                <div className="flex items-center gap-2 text-xs font-mono font-bold" style={{ color: theme.primaryColor }}>
                  <span>📐</span>
                  <span>Key Mathematical & Physical Formulations (KaTeX):</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {currentUnit.keyFormulas.map((formula, i) => (
                    <div key={i} className="p-3 rounded-lg bg-[#041026] border border-slate-800 text-center font-mono text-xs sm:text-sm text-[#00F0B5]">
                      <code className="text-slate-100">{formula}</code>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Associated Lab Experiments */}
            {currentUnit.labComponents && currentUnit.labComponents.length > 0 && (
              <div className="p-4 rounded-xl bg-[#020813] border border-emerald-500/30 space-y-2">
                <div className="flex items-center gap-2 text-xs font-mono font-bold text-emerald-400">
                  <span>🧪</span>
                  <span>Associated Hands-On Laboratory Exercises:</span>
                </div>
                <ul className="text-xs font-mono text-slate-300 space-y-1 list-disc list-inside">
                  {currentUnit.labComponents.map((lab, i) => (
                    <li key={i}>{lab}</li>
                  ))}
                </ul>
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
            <span className="text-xs font-mono px-2 py-1 rounded bg-[#020813] border border-slate-800 text-emerald-400">
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
              <div>
                <div className="text-xs font-mono text-emerald-400 font-bold">
                  INTERACTIVE SIMULATOR • {currentCourse.labSimulation.simulationPlatform.toUpperCase()}
                </div>
                <h3 className="text-xl font-extrabold text-white font-sans mt-0.5">
                  {currentCourse.code} Live Laboratory Workbench
                </h3>
              </div>
              <span className="px-3 py-1 rounded-full bg-[#020813] border border-slate-800 font-mono text-xs text-slate-300">
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

                {/* Filter Response Table */}
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
                    <label className="text-slate-400">Cavity Length (L): <strong className="text-purple-400">{laserL.toFixed(2)} m</strong></label>
                    <input
                      type="range" min="0.1" max="1.5" step="0.05"
                      value={laserL} onChange={(e) => setLaserL(Number(e.target.value))}
                      className="w-full mt-2 accent-purple-500"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400">Mirror 1 RoC (R1): <strong className="text-white">{laserR1.toFixed(2)} m</strong></label>
                    <input
                      type="range" min="0.2" max="2.0" step="0.1"
                      value={laserR1} onChange={(e) => setLaserR1(Number(e.target.value))}
                      className="w-full mt-2 accent-purple-500"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400">Mirror 2 RoC (R2): <strong className="text-white">{laserR2.toFixed(2)} m</strong></label>
                    <input
                      type="range" min="0.2" max="2.0" step="0.1"
                      value={laserR2} onChange={(e) => setLaserR2(Number(e.target.value))}
                      className="w-full mt-2 accent-purple-500"
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
                    <div className="text-purple-300 font-bold text-sm mt-0.5">{laserSimulationResult.gProd}</div>
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
                      className="w-full accent-emerald-500"
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
                      className="w-full accent-emerald-500"
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
                  <span className="text-emerald-400 font-bold">[{i + 1}] </span>
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
              <div className="text-[#00F0B5] font-bold text-sm">{currentCourse.nptelCourseId || "noc23-ee44"}</div>
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
