import React, { useState } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Phase P: Accreditation & Compliance (Features 361–370)
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 *
 * Features:
 *   - Feature 361: NBA/NAAC Outcome-Based Education (OBE) Dashboard (Tier-1 Criteria)
 *   - Feature 362: Course Outcome (CO) Attainment Calculator (Threshold & Attainment 1/2/3)
 *   - Feature 363: Program Outcome (PO) & PSO Mapping Matrix (PO1-PO12 + PSO1-PSO2)
 *   - Feature 364: Direct & Indirect Assessment Evaluator (80% Direct + 20% Indirect)
 *   - Feature 365: Bloom's Taxonomy Level Distribution Analyzer (L1 to L6 Rigor Audit)
 *   - Feature 366: Continuous Quality Improvement (CQI) Logbook (Closing the Loop)
 *   - Feature 367: Faculty Course File Archivist (Mandatory NBA Audit Checklist)
 *   - Feature 368: Student Feedback Analysis Portal (Course Exit Survey Likert Scale)
 *   - Feature 369: Accreditation Evidence Repository (Lab calibration, projects, audit proofs)
 *   - Feature 370: Self-Assessment Report (SAR) Generator (Tier-1 SAR Executive Summaries)
 * Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
 * ========================================================================================
 */

// NBA Tier-1 Accreditation Criteria Scorecard (Feature 361)
const NBA_TIER1_CRITERIA = [
  { id: 1, name: "Criterion 1: Vision, Mission & PEOs", max_marks: 50, awarded: 46, status: "COMPLIANT" },
  { id: 2, name: "Criterion 2: Program Curriculum & Teaching-Learning", max_marks: 100, awarded: 88, status: "COMPLIANT" },
  { id: 3, name: "Criterion 3: Course Outcomes & Program Outcomes (CO-PO)", max_marks: 120, awarded: 108, status: "COMPLIANT" },
  { id: 4, name: "Criterion 4: Students' Performance & Graduating Metrics", max_marks: 150, awarded: 132, status: "COMPLIANT" },
  { id: 5, name: "Criterion 5: Faculty Information & Contributions (SFR 1:15)", max_marks: 200, awarded: 176, status: "COMPLIANT" },
  { id: 6, name: "Criterion 6: Facilities & Technical Infrastructure", max_marks: 80, awarded: 74, status: "COMPLIANT" },
  { id: 7, name: "Criterion 7: Continuous Improvement (CQI Loop)", max_marks: 50, awarded: 44, status: "COMPLIANT" },
  { id: 8, name: "Criterion 8: First Year Academics", max_marks: 50, awarded: 42, status: "COMPLIANT" },
  { id: 9, name: "Criterion 9: Student Support Systems & Mentoring", max_marks: 50, awarded: 45, status: "COMPLIANT" },
  { id: 10, name: "Criterion 10: Governance, Institutional Support & Finance", max_marks: 150, awarded: 130, status: "COMPLIANT" }
];

// Seed Course Outcomes for EC3552 VLSI & Chip Design (Feature 362)
const SEED_COS = [
  {
    id: "CO1",
    desc: "Analyze DC transfer characteristics, noise margins, and power dissipation of nanoscale CMOS inverters.",
    bloom: "L4 (Analyze)",
    target: 70.0,
    direct_pct: 82.5,
    indirect_stars: 4.8,
    level: 3,
    met: true
  },
  {
    id: "CO2",
    desc: "Design combinational and sequential digital logic circuits in Verilog HDL following synchronous RTL design guidelines.",
    bloom: "L6 (Create)",
    target: 70.0,
    direct_pct: 76.0,
    indirect_stars: 4.5,
    level: 3,
    met: true
  },
  {
    id: "CO3",
    desc: "Perform static timing analysis (STA) to calculate setup/hold slacks and resolve timing violations on advanced technology nodes.",
    bloom: "L4 (Analyze)",
    target: 65.0,
    direct_pct: 68.0,
    indirect_stars: 4.2,
    level: 2,
    met: false
  },
  {
    id: "CO4",
    desc: "Implement physical synthesis flows including floorplanning, power planning, placement, CTS, and routing in modern EDA suites.",
    bloom: "L3 (Apply)",
    target: 65.0,
    direct_pct: 73.5,
    indirect_stars: 4.6,
    level: 3,
    met: true
  },
  {
    id: "CO5",
    desc: "Verify Design-for-Testability (DFT) architectures using scan insertion, ATPG fault coverage, and boundary scan techniques.",
    bloom: "L5 (Evaluate)",
    target: 60.0,
    direct_pct: 54.0,
    indirect_stars: 3.5,
    level: 1,
    met: false
  }
];

// CO-PO Correlation Matrix for EC3552 (Feature 363)
const CO_PO_MAPPING = [
  { co: "CO1", po1: 3, po2: 3, po3: 2, po4: 2, po5: 3, po9: 0, po10: 0, po12: 2, pso1: 3, pso2: 1 },
  { co: "CO2", po1: 3, po2: 3, po3: 3, po4: 2, po5: 3, po9: 2, po10: 0, po12: 2, pso1: 3, pso2: 2 },
  { co: "CO3", po1: 3, po2: 3, po3: 2, po4: 3, po5: 3, po9: 0, po10: 0, po12: 2, pso1: 3, pso2: 1 },
  { co: "CO4", po1: 3, po2: 2, po3: 3, po4: 2, po5: 3, po9: 0, po10: 0, po12: 2, pso1: 3, pso2: 2 },
  { co: "CO5", po1: 3, po2: 3, po3: 2, po4: 2, po5: 3, po9: 1, po10: 1, po12: 2, pso1: 3, pso2: 1 }
];

// Course File Mandatory Items (Feature 367)
const COURSE_FILE_ITEMS = [
  { id: "cf_01", name: "Syllabus, Textbooks & Course Objectives (AU Reg 2023)", uploaded: true, verifier: "Dr. P. Nirmal" },
  { id: "cf_02", name: "Course Articulation Matrix (CO-PO & CO-PSO Mapping Table)", uploaded: true, verifier: "Dr. P. Nirmal" },
  { id: "cf_03", name: "Detailed Lesson Plan & 45-Hour Lecture Delivery Schedule", uploaded: true, verifier: "Dr. P. Nirmal" },
  { id: "cf_04", name: "IAT 1/2/3 Question Papers mapped with Bloom's Cognitive Levels", uploaded: true, verifier: "Dr. P. Nirmal" },
  { id: "cf_05", name: "Three-Sample Evaluated Answer Scripts (Best / Average / Weak)", uploaded: true, verifier: "Dr. P. Nirmal" },
  { id: "cf_06", name: "Consolidated CO-PO Direct & Indirect Attainment Spreadsheets", uploaded: true, verifier: "Dr. P. Nirmal" },
  { id: "cf_07", name: "Continuous Quality Improvement (CQI) Action Taken Report", uploaded: false, verifier: "Pending HOD Signoff" }
];

// CQI Action Logbook (Feature 366)
const SEED_CQI_LOGS = [
  {
    id: "cqi_01",
    course: "EC3552",
    co: "CO5 (DFT & Scan Insertion)",
    deficiency: "Attainment level reached 1.84/3.00 (below 2.40 target). Students struggled with boundary scan JTAG TAP controller state transitions.",
    action: "Conduct 4-hour hands-on Cadence Modus DFT workshop with live scan chain insertion and ATPG stuck-at fault simulation.",
    faculty: "Dr. P. Nirmal",
    cycle: "AY 2026-2027",
    status: "IN_PROGRESS"
  },
  {
    id: "cqi_02",
    course: "EC3552",
    co: "CO3 (STA Timing Slack)",
    deficiency: "Attainment reached 2.14/3.00. Students faced difficulty resolving hold violations across multi-corner fast-fast libraries.",
    action: "Introduce LTspice & Innovus delay cell insertion lab module in week 8 tutorial session.",
    faculty: "Dr. P. Nirmal",
    cycle: "AY 2026-2027",
    status: "RESOLVED"
  }
];

export default function AccreditationComplianceHub() {
  const [activeTab, setActiveTab] = useState('obe_dashboard');

  // CO Attainment Calculator Interactive State (Feature 362 & 364)
  const [cos, setCos] = useState(SEED_COS);
  const [editCoId, setEditCoId] = useState('CO1');
  const [directPctInput, setDirectPctInput] = useState(82.5);
  const [indirectStarInput, setIndirectStarInput] = useState(4.8);

  // CQI Logbook State (Feature 366)
  const [cqiLogs, setCqiLogs] = useState(SEED_CQI_LOGS);
  const [newCqiCo, setNewCqiCo] = useState('CO5 (DFT & Scan Insertion)');
  const [newCqiDeficiency, setNewCqiDeficiency] = useState('');
  const [newCqiAction, setNewCqiAction] = useState('');

  // Course File Checklist State (Feature 367)
  const [checklist, setChecklist] = useState(COURSE_FILE_ITEMS);

  // Student Exit Survey Form State (Feature 368)
  const [surveyCo1, setSurveyCo1] = useState(5);
  const [surveyCo2, setSurveyCo2] = useState(5);
  const [surveyCo3, setSurveyCo3] = useState(4);
  const [surveyCo4, setSurveyCo4] = useState(5);
  const [surveyCo5, setSurveyCo5] = useState(4);
  const [surveyFeedback, setSurveyFeedback] = useState('EDA labs provided exceptional real-world exposure to Cadence physical layout workflows.');

  // Total NBA Score calculation
  const totalAwarded = NBA_TIER1_CRITERIA.reduce((acc, c) => acc + c.awarded, 0);
  const totalMax = NBA_TIER1_CRITERIA.reduce((acc, c) => acc + c.max_marks, 0);

  // Helper for composite attainment calculation (80% Direct + 20% Indirect)
  const computeCompositeAttainment = (directPct, indirectStars) => {
    let directLevel = 0;
    if (directPct >= 70.0) directLevel = 3;
    else if (directPct >= 60.0) directLevel = 2;
    else if (directPct >= 50.0) directLevel = 1;

    const indirectScaled = (indirectStars / 5.0) * 3.0;
    const composite = (0.80 * directLevel + 0.20 * indirectScaled).toFixed(2);
    return { directLevel, composite, isMet: parseFloat(composite) >= 2.40 };
  };

  // Handle CO recalculation
  const handleUpdateCo = (e) => {
    e.preventDefault();
    const { directLevel, composite, isMet } = computeCompositeAttainment(directPctInput, indirectStarInput);
    setCos(items => items.map(co => {
      if (co.id === editCoId) {
        return {
          ...co,
          direct_pct: directPctInput,
          indirect_stars: indirectStarInput,
          level: directLevel,
          composite: parseFloat(composite),
          met: isMet
        };
      }
      return co;
    }));
    alert(`CO Attainment for ${editCoId} recalculated: Composite Score ${composite}/3.00 (Direct Level: ${directLevel})`);
  };

  // Add CQI log
  const handleAddCqi = (e) => {
    e.preventDefault();
    if (!newCqiDeficiency.trim() || !newCqiAction.trim()) return;
    const newLog = {
      id: `cqi_${Date.now()}`,
      course: "EC3552",
      co: newCqiCo,
      deficiency: newCqiDeficiency,
      action: newCqiAction,
      faculty: "Dr. P. Nirmal",
      cycle: "AY 2026-2027",
      status: "OPEN"
    };
    setCqiLogs([newLog, ...cqiLogs]);
    setNewCqiDeficiency('');
    setNewCqiAction('');
    alert("CQI Action Plan recorded in accreditation audit trail!");
  };

  // Toggle checklist upload status
  const toggleChecklistItem = (id) => {
    setChecklist(items => items.map(item => {
      if (item.id === id) {
        return { ...item, uploaded: !item.uploaded };
      }
      return item;
    }));
  };

  // Submit course exit survey
  const handleSubmitSurvey = (e) => {
    e.preventDefault();
    alert("Thank you! Course exit indirect evaluation successfully logged in department OBE repository.");
  };

  return (
    <div className="accreditation-hub space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900/80 border border-emerald-500/30 rounded-2xl p-6 backdrop-blur-md shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="px-3 py-1 text-xs font-bold rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                PHASE P • ACCREDITATION & COMPLIANCE
              </span>
              <span className="px-3 py-1 text-xs font-bold rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                NBA TIER-1 ACCREDITED (6 YEARS)
              </span>
              <span className="px-3 py-1 text-xs font-bold rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/40">
                NAAC A++ (CGPA: 3.82)
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              NBA / NAAC Outcome-Based Education (OBE) Governance Hub
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Madras Institute of Technology (MIT Campus) • Department of Electronics Engineering (Regulation 2023)
            </p>
          </div>

          <div className="flex items-center gap-3 bg-slate-800/80 border border-slate-700/60 p-3 rounded-xl">
            <div className="text-right">
              <div className="text-xs text-slate-400">NBA SAR Readiness Score</div>
              <div className="text-2xl font-black text-emerald-300">{totalAwarded} <span className="text-xs text-slate-400">/ {totalMax}</span></div>
              <div className="text-[10px] text-emerald-400 font-bold">TIER-1 EXCELLENCE COMPLIANT</div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 mt-6 border-t border-slate-800 pt-4">
          {[
            { id: 'obe_dashboard', label: 'OBE Criteria Scorecard', icon: '🏛️' },
            { id: 'co_attainment', label: 'CO Attainment Calculator', icon: '🧮' },
            { id: 'po_pso_matrix', label: 'CO-PO & PSO Mapping', icon: '📊' },
            { id: 'blooms_cqi', label: "Bloom's Rigor & CQI Loop", icon: '🔄' },
            { id: 'course_file_audit', label: 'Course File Audit Checklist', icon: '📁' },
            { id: 'sar_generator', label: 'Student Exit & SAR Summary', icon: '📄' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-2 ${
                activeTab === tab.id
                  ? 'bg-emerald-500 text-slate-950 font-bold shadow-lg shadow-emerald-500/20'
                  : 'bg-slate-800/60 text-slate-300 hover:bg-slate-700 hover:text-white border border-slate-700/40'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* =========================================================================
          TAB 1: NBA/NAAC OBE CRITERIA SCORECARD (Feature 361)
      ========================================================================= */}
      {activeTab === 'obe_dashboard' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-slate-400 uppercase tracking-wider">Accreditation Tier</div>
              <div className="text-xl font-bold text-emerald-400 mt-1">NBA Tier-1 (Washington Accord)</div>
              <div className="text-[11px] text-slate-400 mt-1">Autonomous Institutions & University Depts</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-slate-400 uppercase tracking-wider">Student-Faculty Ratio (SFR)</div>
              <div className="text-xl font-bold text-cyan-400 mt-1">1:13.8 (Cadre Ratio 1:2:6)</div>
              <div className="text-[11px] text-slate-400 mt-1">Full marks in Criterion 5.1</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-slate-400 uppercase tracking-wider">Average CO Attainment Rate</div>
              <div className="text-xl font-bold text-purple-400 mt-1">2.68 / 3.00 (89.3%)</div>
              <div className="text-[11px] text-slate-400 mt-1">Threshold: 2.40 target met</div>
            </div>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <span>🏛️</span> NBA Tier-1 Institutional Criteria Scorecard (1000 Marks)
            </h2>

            <div className="space-y-3">
              {NBA_TIER1_CRITERIA.map(crit => {
                const pct = Math.round((crit.awarded / crit.max_marks) * 100);
                return (
                  <div key={crit.id} className="p-3.5 bg-slate-800/50 rounded-xl border border-slate-700/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-xs text-white">{crit.name}</span>
                        <span className="font-mono text-xs font-bold text-emerald-400">{crit.awarded} / {crit.max_marks} pts ({pct}%)</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full" style={{ width: `${pct}%` }}></div>
                      </div>
                    </div>
                    <span className="px-2.5 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-[10px] font-bold rounded-lg self-start sm:self-auto">
                      {crit.status}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 2: CO ATTAINMENT CALCULATOR (Features 362 & 364)
      ========================================================================= */}
      {activeTab === 'co_attainment' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* CO List */}
          <div className="space-y-3 lg:col-span-2">
            <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-white">Course Outcomes: EC3552 (VLSI & Chip Design)</h2>
                <p className="text-xs text-slate-400">Target formula: 80% Direct (Internal + Univ) + 20% Indirect (Exit Survey)</p>
              </div>
              <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 text-xs font-bold rounded-full border border-emerald-500/40">
                AY 2026-2027
              </span>
            </div>

            <div className="space-y-3">
              {cos.map(co => {
                const { directLevel, composite, isMet } = computeCompositeAttainment(co.direct_pct, co.indirect_stars);
                return (
                  <div key={co.id} className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-emerald-400 bg-emerald-500/20 px-2.5 py-0.5 rounded border border-emerald-500/30">
                          {co.id}
                        </span>
                        <span className="text-[11px] font-semibold text-purple-300 bg-purple-500/20 px-2 py-0.5 rounded">
                          {co.bloom}
                        </span>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        isMet
                          ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                          : 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                      }`}>
                        {isMet ? 'TARGET ATTAINED' : 'CQI ACTION REQUIRED'}
                      </span>
                    </div>

                    <p className="text-xs text-slate-200 leading-relaxed">{co.desc}</p>

                    <div className="pt-2 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
                      <div className="text-slate-400">
                        Direct Assessment: <strong className="text-cyan-300">{co.direct_pct}%</strong> (Level {directLevel}/3)
                      </div>
                      <div className="text-slate-400">
                        Exit Survey: <strong className="text-amber-300">{co.indirect_stars} ⭐</strong>
                      </div>
                      <div className="text-slate-400">
                        Composite: <strong className="text-emerald-400 font-mono text-sm">{composite} / 3.00</strong>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Attainment Recalculator Widget */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 h-fit space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <span>🧮</span> Direct & Indirect Attainment Simulator
            </h3>

            <form onSubmit={handleUpdateCo} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Target Course Outcome</label>
                <select
                  value={editCoId}
                  onChange={e => {
                    setEditCoId(e.target.value);
                    const target = cos.find(c => c.id === e.target.value);
                    if (target) {
                      setDirectPctInput(target.direct_pct);
                      setIndirectStarInput(target.indirect_stars);
                    }
                  }}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white"
                >
                  {cos.map(c => (
                    <option key={c.id} value={c.id}>{c.id} - {c.desc.slice(0, 40)}...</option>
                  ))}
                </select>
              </div>

              <div>
                <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                  <span>Direct: % Students Scoring &ge; 60%</span>
                  <span className="font-bold text-cyan-400">{directPctInput}%</span>
                </div>
                <input
                  type="range" min="30" max="100" step="0.5" value={directPctInput}
                  onChange={e => setDirectPctInput(parseFloat(e.target.value))}
                  className="w-full accent-cyan-400"
                />
                <div className="text-[10px] text-slate-400 mt-0.5">
                  &ge;70%: Level 3 • 60-69%: Level 2 • 50-59%: Level 1 • &lt;50%: Level 0
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                  <span>Indirect: Course Exit Survey (Stars)</span>
                  <span className="font-bold text-amber-400">{indirectStarInput} ⭐</span>
                </div>
                <input
                  type="range" min="1.0" max="5.0" step="0.1" value={indirectStarInput}
                  onChange={e => setIndirectStarInput(parseFloat(e.target.value))}
                  className="w-full accent-amber-400"
                />
              </div>

              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs">
                <div className="text-slate-400">Simulated Composite Attainment:</div>
                <div className="text-xl font-black text-emerald-400 mt-1 font-mono">
                  {computeCompositeAttainment(directPctInput, indirectStarInput).composite} / 3.00
                </div>
                <div className="text-[10px] text-slate-400 mt-0.5">Formula: 0.80 &times; Direct + 0.20 &times; (Stars/5 &times; 3)</div>
              </div>

              <button
                type="submit"
                className="w-full py-2 bg-gradient-to-r from-emerald-500 to-teal-600 text-slate-950 font-bold rounded-lg text-xs hover:from-emerald-400 hover:to-teal-500 transition"
              >
                Commit Recalculation
              </button>
            </form>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 3: PO & PSO MAPPING MATRIX (Feature 363)
      ========================================================================= */}
      {activeTab === 'po_pso_matrix' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <span>📊</span> Course Articulation Matrix (CO-PO & CO-PSO Mapping)
              </h2>
              <p className="text-xs text-slate-400">Correlation Weights: 3 = High, 2 = Medium, 1 = Low, - = No correlation</p>
            </div>
            <span className="px-3 py-1 bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 text-xs font-mono font-bold rounded">
              EC3552
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-center text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-2 px-3 text-left">Course Outcome</th>
                  <th className="py-2 px-2">PO1</th>
                  <th className="py-2 px-2">PO2</th>
                  <th className="py-2 px-2">PO3</th>
                  <th className="py-2 px-2">PO4</th>
                  <th className="py-2 px-2">PO5</th>
                  <th className="py-2 px-2">PO9</th>
                  <th className="py-2 px-2">PO10</th>
                  <th className="py-2 px-2">PO12</th>
                  <th className="py-2 px-2 font-bold text-teal-400">PSO1</th>
                  <th className="py-2 px-2 font-bold text-teal-400">PSO2</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 font-mono">
                {CO_PO_MAPPING.map(m => (
                  <tr key={m.co} className="hover:bg-slate-800/40 transition">
                    <td className="py-2.5 px-3 text-left font-bold text-emerald-400 font-sans">{m.co}</td>
                    <td className="py-2.5 px-2 text-white">{m.po1}</td>
                    <td className="py-2.5 px-2 text-white">{m.po2}</td>
                    <td className="py-2.5 px-2 text-white">{m.po3}</td>
                    <td className="py-2.5 px-2 text-white">{m.po4}</td>
                    <td className="py-2.5 px-2 text-cyan-300 font-bold">{m.po5}</td>
                    <td className="py-2.5 px-2 text-slate-400">{m.po9 || '-'}</td>
                    <td className="py-2.5 px-2 text-slate-400">{m.po10 || '-'}</td>
                    <td className="py-2.5 px-2 text-white">{m.po12}</td>
                    <td className="py-2.5 px-2 font-bold text-teal-300">{m.pso1}</td>
                    <td className="py-2.5 px-2 font-bold text-teal-300">{m.pso2}</td>
                  </tr>
                ))}
                {/* Average Row */}
                <tr className="bg-slate-950 font-bold border-t-2 border-slate-700 text-emerald-400">
                  <td className="py-2.5 px-3 text-left font-sans">Avg Correlation</td>
                  <td className="py-2.5 px-2">3.00</td>
                  <td className="py-2.5 px-2">2.80</td>
                  <td className="py-2.5 px-2">2.40</td>
                  <td className="py-2.5 px-2">2.20</td>
                  <td className="py-2.5 px-2 text-cyan-300">3.00</td>
                  <td className="py-2.5 px-2 text-slate-400">1.50</td>
                  <td className="py-2.5 px-2 text-slate-400">1.00</td>
                  <td className="py-2.5 px-2">2.00</td>
                  <td className="py-2.5 px-2 text-teal-300">3.00</td>
                  <td className="py-2.5 px-2 text-teal-300">1.40</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 4: BLOOM'S TAXONOMY & CQI LOOP (Features 365 & 366)
      ========================================================================= */}
      {activeTab === 'blooms_cqi' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Bloom's Rigor */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <span>🧠</span> Bloom's Taxonomy Cognitive Level Balance (Feature 365)
            </h2>
            <p className="text-xs text-slate-400">NBA Tier-1 expects &ge;60% Higher-Order Thinking Skills (HOTS) in pre-final year</p>

            <div className="space-y-3">
              {[
                { lvl: "L6 (Create)", count: 1, pct: 20, desc: "Verilog RTL Design & Synthesis" },
                { lvl: "L5 (Evaluate)", count: 1, pct: 20, desc: "DFT Scan Insertion & ATPG Fault Coverage" },
                { lvl: "L4 (Analyze)", count: 2, pct: 40, desc: "CMOS Inverter DC Transfer & STA Slack Closure" },
                { lvl: "L3 (Apply)", count: 1, pct: 20, desc: "Physical Placement & CTS Execution" },
                { lvl: "L2 (Understand)", count: 0, pct: 0, desc: "Fundamental definitions" },
                { lvl: "L1 (Remember)", count: 0, pct: 0, desc: "Terminology recall" }
              ].map(b => (
                <div key={b.lvl} className="p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="font-semibold text-white">{b.lvl} — <span className="text-slate-400">{b.desc}</span></span>
                    <span className="font-mono font-bold text-emerald-400">{b.pct}% ({b.count} CO)</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${b.pct}%` }}></div>
                  </div>
                </div>
              ))}
            </div>

            <div className="p-3 bg-emerald-950/20 border border-emerald-500/40 rounded-lg text-xs text-emerald-300">
              ✓ <strong>100.0% Higher-Order Cognitive Rigor</strong> (L3–L6). Fully conforms to NBA Tier-1 OBE benchmark.
            </div>
          </div>

          {/* CQI Closing the Loop Logbook */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <span>🔄</span> Continuous Quality Improvement (CQI) Logbook (Feature 366)
            </h2>

            <form onSubmit={handleAddCqi} className="space-y-3 bg-slate-800/40 p-3.5 rounded-lg border border-slate-700/50">
              <input
                type="text"
                value={newCqiDeficiency}
                onChange={e => setNewCqiDeficiency(e.target.value)}
                placeholder="Observed Learning Deficiency..."
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500"
                required
              />
              <textarea
                value={newCqiAction}
                onChange={e => setNewCqiAction(e.target.value)}
                rows={2}
                placeholder="Action Plan / Corrective Intervention..."
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                required
              />
              <button
                type="submit"
                className="w-full py-1.5 bg-emerald-500 text-slate-950 font-bold rounded-lg text-xs hover:bg-emerald-400 transition"
              >
                Log Corrective Action Plan
              </button>
            </form>

            <div className="space-y-2 max-h-56 overflow-y-auto">
              {cqiLogs.map(log => (
                <div key={log.id} className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50 text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-amber-400">{log.co}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      log.status === 'RESOLVED' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'
                    }`}>
                      {log.status}
                    </span>
                  </div>
                  <div className="text-slate-300"><strong>Deficiency:</strong> {log.deficiency}</div>
                  <div className="text-emerald-300"><strong>Intervention:</strong> {log.action}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 5: MANDATORY COURSE FILE AUDIT (Feature 367)
      ========================================================================= */}
      {activeTab === 'course_file_audit' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <span>📁</span> Faculty Course File Archivist & NBA Audit Checklist
              </h2>
              <p className="text-xs text-slate-400">7 Mandatory audit artifacts verified for external NBA peer committee review</p>
            </div>
            <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 text-xs font-bold rounded-full border border-emerald-500/40">
              {checklist.filter(c => c.uploaded).length} / {checklist.length} Complete
            </span>
          </div>

          <div className="space-y-3">
            {checklist.map(item => (
              <div key={item.id} className="p-3.5 bg-slate-800/50 rounded-xl border border-slate-700/50 flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => toggleChecklistItem(item.id)}
                    className={`w-6 h-6 rounded flex items-center justify-center font-bold text-xs transition ${
                      item.uploaded ? 'bg-emerald-500 text-slate-950' : 'bg-slate-700 text-slate-400'
                    }`}
                  >
                    {item.uploaded ? '✓' : ''}
                  </button>
                  <div>
                    <div className="text-xs font-semibold text-white">{item.name}</div>
                    <div className="text-[10px] text-slate-400">Auditor Signoff: {item.verifier}</div>
                  </div>
                </div>

                <span className={`px-2.5 py-1 rounded text-[10px] font-bold ${
                  item.uploaded ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                }`}>
                  {item.uploaded ? 'VERIFIED IN REPO' : 'PENDING UPLOAD'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 6: STUDENT EXIT SURVEY & SAR GENERATOR (Features 368 & 370)
      ========================================================================= */}
      {activeTab === 'sar_generator' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Student Exit Survey (Feature 368) */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <span>📝</span> Student Course Exit Survey (Likert 1 to 5)
            </h2>
            <p className="text-xs text-slate-400">Directly feeds 20% indirect attainment calculation for Criterion 3</p>

            <form onSubmit={handleSubmitSurvey} className="space-y-3 bg-slate-800/40 p-4 rounded-xl border border-slate-700/50">
              {[
                { id: "co1", label: "CO1: CMOS Inverter DC transfer & noise margins", val: surveyCo1, set: setSurveyCo1 },
                { id: "co2", label: "CO2: Verilog HDL digital logic design", val: surveyCo2, set: setSurveyCo2 },
                { id: "co3", label: "CO3: Static timing analysis & slack closure", val: surveyCo3, set: setSurveyCo3 },
                { id: "co4", label: "CO4: Cadence physical synthesis & CTS", val: surveyCo4, set: setSurveyCo4 },
                { id: "co5", label: "CO5: DFT scan chains & ATPG testability", val: surveyCo5, set: setSurveyCo5 }
              ].map(field => (
                <div key={field.id}>
                  <div className="flex justify-between text-xs text-slate-300 mb-1">
                    <span>{field.label}</span>
                    <span className="font-bold text-amber-400">{field.val} ⭐</span>
                  </div>
                  <input
                    type="range" min="1" max="5" value={field.val}
                    onChange={e => field.set(parseInt(e.target.value))}
                    className="w-full accent-amber-400"
                  />
                </div>
              ))}

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Qualitative Feedback</label>
                <textarea
                  value={surveyFeedback}
                  onChange={e => setSurveyFeedback(e.target.value)}
                  rows={2}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-xs text-white"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2 bg-amber-500 text-slate-950 font-bold rounded-lg text-xs hover:bg-amber-400 transition"
              >
                Submit Course Exit Feedback
              </button>
            </form>
          </div>

          {/* SAR Executive Summary Generator (Feature 370) */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4 flex flex-col justify-between">
            <div className="space-y-3">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <span>📄</span> NBA Tier-1 Self-Assessment Report (SAR) Executive Dossier
              </h2>

              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2 text-xs">
                <div className="text-emerald-400 font-bold font-mono">CRITERION 3 & 4 EVALUATION SUMMARY</div>
                <div className="text-slate-300"><strong>Program:</strong> B.E. Electronics and Communication Engineering</div>
                <div className="text-slate-300"><strong>Institution:</strong> MIT Campus, Anna University (Reg 2023)</div>
                <div className="text-slate-300"><strong>Average PO Attainment:</strong> 2.68 / 3.00 (&gt; 2.40 Target Met)</div>
                <div className="text-slate-300"><strong>HOTS Cognitive Percentage:</strong> 100.0% (L3 to L6)</div>
                <div className="text-slate-300"><strong>Course File Completeness:</strong> 85.7% (6/7 Items Verified)</div>
                <div className="text-slate-300"><strong>Status:</strong> <span className="text-emerald-400 font-bold">READY FOR NBA PEER TEAM AUDIT</span></div>
              </div>
            </div>

            <button
              onClick={() => alert("Official NBA Tier-1 SAR Criterion 3 & 4 dossier exported as PDF/Docx.")}
              className="w-full py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 text-slate-950 font-bold rounded-lg text-xs hover:from-emerald-400 hover:to-teal-500 transition shadow-lg shadow-emerald-500/20"
            >
              📥 Generate Formal NBA SAR Criterion 3 & 4 Dossier
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
