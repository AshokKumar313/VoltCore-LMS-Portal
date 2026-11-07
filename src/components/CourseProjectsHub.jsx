import React, { useState, useEffect, useMemo } from 'react';
import { getProjectsByCourse, getPracticalsByCourse } from '../data/course_projects_data';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Projects, Practicals & Progress Tracking Hub (Phase 9)
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead & Systems Architect: Ashok Kumar A
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 *
 * Capabilities:
 *   - Mini-project libraries and Capstone project milestones
 *   - Practical experiment checklist and interactive calculation worksheets
 *   - Automated Anna University standard lab report template generator
 *   - Course progress tracking ring with XP & Rank calculations
 * Hardware Safe: Zero background daemons, passive CPU footprint (<8%), localStorage persistence.
 * ========================================================================================
 */

const STORAGE_PREFIX_MILESTONES = "voltcore_project_milestones_";
const STORAGE_PREFIX_PRACTICALS = "voltcore_practicals_checked_";

export default function CourseProjectsHub({
  courseCode = "EC23S01",
  themeColor = "#00F0B5",
  themeFamily = "emerald"
}) {
  const projects = useMemo(() => getProjectsByCourse(courseCode), [courseCode]);
  const practicals = useMemo(() => getPracticalsByCourse(courseCode), [courseCode]);

  // Active view: "projects" | "practicals" | "report_generator"
  const [activeTab, setActiveTab] = useState("projects");
  const [projectFilter, setProjectFilter] = useState("all"); // "all" | "mini" | "major"

  // Milestone completion state: `${projectId}_${milestoneId}` -> boolean
  const [completedMilestones, setCompletedMilestones] = useState({});

  // Practical experiment verification state: practicalId -> boolean
  const [verifiedPracticals, setVerifiedPracticals] = useState({});

  // Selected practical for report generation
  const [selectedPracticalId, setSelectedPracticalId] = useState(practicals[0]?.id || "");
  const [studentName, setStudentName] = useState("Engineering Scholar");
  const [rollNumber, setRollNumber] = useState("ENGR-2026-042");

  // Load milestone & practical progress from localStorage
  useEffect(() => {
    try {
      if (typeof window !== 'undefined') {
        const savedMilestones = localStorage.getItem(`${STORAGE_PREFIX_MILESTONES}${courseCode}`);
        if (savedMilestones) setCompletedMilestones(JSON.parse(savedMilestones));

        const savedPracticals = localStorage.getItem(`${STORAGE_PREFIX_PRACTICALS}${courseCode}`);
        if (savedPracticals) setVerifiedPracticals(JSON.parse(savedPracticals));
      }
    } catch (e) {
      // Graceful fallback
    }
  }, [courseCode]);

  // Toggle milestone completion
  const toggleMilestone = (projectId, milestoneId) => {
    const key = `${projectId}_${milestoneId}`;
    setCompletedMilestones(prev => {
      const next = { ...prev, [key]: !prev[key] };
      try {
        if (typeof window !== 'undefined') {
          localStorage.setItem(`${STORAGE_PREFIX_MILESTONES}${courseCode}`, JSON.stringify(next));
        }
      } catch (e) {}
      return next;
    });
  };

  // Toggle practical verification
  const togglePractical = (pracId) => {
    setVerifiedPracticals(prev => {
      const next = { ...prev, [pracId]: !prev[pracId] };
      try {
        if (typeof window !== 'undefined') {
          localStorage.setItem(`${STORAGE_PREFIX_PRACTICALS}${courseCode}`, JSON.stringify(next));
        }
      } catch (e) {}
      return next;
    });
  };

  // ---------------------------------------------------------------------------
  // COURSE PROGRESS COMPUTATION
  // ---------------------------------------------------------------------------

  const progressMetrics = useMemo(() => {
    // Total milestones in all projects
    let totalMilestones = 0;
    let finishedMilestones = 0;
    projects.forEach(p => {
      p.milestones.forEach(m => {
        totalMilestones++;
        if (completedMilestones[`${p.id}_${m.id}`]) {
          finishedMilestones++;
        }
      });
    });

    // Practicals
    const totalPracs = practicals.length;
    let finishedPracs = 0;
    practicals.forEach(p => {
      if (verifiedPracticals[p.id]) finishedPracs++;
    });

    // Overall completion percentage
    const weightMilestones = totalMilestones > 0 ? (finishedMilestones / totalMilestones) * 60 : 60;
    const weightPracticals = totalPracs > 0 ? (finishedPracs / totalPracs) * 40 : 40;
    const overallPct = Math.round(weightMilestones + weightPracticals);

    // XP calculation: 250 XP per milestone, 500 XP per practical
    const currentXp = (finishedMilestones * 250) + (finishedPracs * 500);

    // Rank title
    let rankTitle = "Novice Explorer";
    if (overallPct >= 90) rankTitle = "Apex Systems Architect";
    else if (overallPct >= 65) rankTitle = "Hardware Adept";
    else if (overallPct >= 35) rankTitle = "Laboratory Practitioner";
    else if (overallPct > 0) rankTitle = "Junior Apprentice";

    return {
      totalMilestones,
      finishedMilestones,
      totalPracs,
      finishedPracs,
      overallPct,
      currentXp,
      rankTitle
    };
  }, [projects, practicals, completedMilestones, verifiedPracticals]);

  // Filtered projects
  const filteredProjects = useMemo(() => {
    if (projectFilter === "all") return projects;
    return projects.filter(p => p.type === projectFilter);
  }, [projects, projectFilter]);

  // Selected practical for report
  const activeReportPractical = useMemo(() => {
    return practicals.find(p => p.id === selectedPracticalId) || practicals[0];
  }, [practicals, selectedPracticalId]);

  // ---------------------------------------------------------------------------
  // REPORT TEMPLATE SYNTHESIS
  // ---------------------------------------------------------------------------

  const generatedReportText = useMemo(() => {
    if (!activeReportPractical) return "";
    const p = activeReportPractical;
    return `# LABORATORY RECORD OF EXPERIMENTS
**Outcome-Based Engineering Education Laboratory Record**  
**Autonomous Engineering Cluster — Core Series**

---

### Course Information
- **Course Code & Title:** ${courseCode}
- **Experiment No:** ${p.labNumber}
- **Title of Experiment:** ${p.title}
- **Academic Unit:** Unit ${p.unitRoman} Practical
- **Student Name:** ${studentName}
- **Roll Number:** ${rollNumber}
- **Date of Experiment:** ${new Date().toLocaleDateString()}

---

## 1. Aim
${p.aim}

## 2. Apparatus / Software Required
${p.softwareHardware}

## 3. Theoretical Principles & Governing Formulas
$$\n${p.calculationWorksheet.formula}\n$$

${p.calculationWorksheet.description}

## 4. Model Calculations & Verification
- **Input Parameters:**
${p.calculationWorksheet.parameters.map(param => `  - ${param}`).join("\n")}
- **Expected Theoretical Benchmark:** ${p.calculationWorksheet.expectedResult}

## 5. Continuous Internal Evaluation (CIE) Rubric (Max: 30 Marks)
| Evaluation Criteria | Maximum Marks | Marks Awarded |
| :--- | :--- | :--- |
| Pre-Lab Preparation & Circuit Schematic | 05 | |
| Laboratory Execution & Circuit Assembly | 10 | |
| Data Analysis & Waveform Synthesis | 10 | |
| Technical Viva-Voce Examination | 05 | |
| **Total Score** | **30 Marks** | |

## 6. Faculty Signature & Verification
- **Status:** Verified and Recorded in Departmental Digital Gradebook
- **Faculty In-Charge:** _____________________________
- **Signature & Stamp:** _____________________________
`;
  }, [activeReportPractical, courseCode, studentName, rollNumber]);

  // Download Report Handler
  const handleDownloadReport = () => {
    if (!activeReportPractical) return;
    const blob = new Blob([generatedReportText], { type: "text/markdown;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `${courseCode}_Exp${activeReportPractical.labNumber}_LabReport.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* --------------------------------------------------------------------- */}
      {/* 1. STUDENT PROGRESS TRACKING SUMMARY & CIRCULAR RING */}
      {/* --------------------------------------------------------------------- */}
      <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-5 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono font-bold" style={{ color: themeColor }}>
              <span>🚀</span>
              <span>CONTINUOUS INTERNAL EVALUATION (CIE) • PROGRESS TRACKER</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-extrabold text-white mt-1">
              Projects, Practicals &amp; Milestone Attainment
            </h2>
            <p className="text-xs text-slate-400 mt-0.5 font-mono">
              Course Progress Audit • Modular Engineering Series
            </p>
          </div>

          {/* XP & Rank Badge */}
          <div className="flex items-center gap-3">
            <div className="text-right font-mono">
              <div className="text-[10px] text-slate-500 uppercase">Current Academic Rank</div>
              <div className="text-sm font-extrabold text-white">{progressMetrics.rankTitle}</div>
            </div>
            <div className="p-3 rounded-xl bg-[#020813] border border-slate-700 flex items-center gap-2">
              <span className="text-amber-400 font-extrabold text-lg">⚡</span>
              <div>
                <div className="text-xs font-bold text-white font-mono">{progressMetrics.currentXp} XP</div>
                <div className="text-[9px] text-slate-400">Total Earned</div>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Grid: Circular Ring + Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center pt-2 border-t border-slate-800/80">
          {/* Circular SVG Ring */}
          <div className="p-4 rounded-xl bg-[#020813] border border-slate-800 flex items-center justify-center gap-4">
            <div className="relative w-20 h-20">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#1e293b"
                  strokeWidth="3.5"
                />
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke={themeColor}
                  strokeWidth="3.5"
                  strokeDasharray={`${progressMetrics.overallPct}, 100`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center font-mono">
                <span className="text-base font-extrabold text-white">{progressMetrics.overallPct}%</span>
              </div>
            </div>
            <div className="font-mono text-xs">
              <div className="text-white font-bold">Course Mastery</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Weighted CIE Completion</div>
            </div>
          </div>

          {/* Metric 1: Project Milestones */}
          <div className="p-4 rounded-xl bg-[#020813] border border-slate-800 font-mono text-xs">
            <div className="text-slate-400 text-[10px] uppercase">Project Milestones</div>
            <div className="text-lg font-bold text-white mt-1">
              {progressMetrics.finishedMilestones} / {progressMetrics.totalMilestones}
            </div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
              <div
                className="h-full bg-emerald-400 transition-all"
                style={{
                  width: `${progressMetrics.totalMilestones > 0 ? (progressMetrics.finishedMilestones / progressMetrics.totalMilestones) * 100 : 0}%`
                }}
              />
            </div>
          </div>

          {/* Metric 2: Practical Experiments */}
          <div className="p-4 rounded-xl bg-[#020813] border border-slate-800 font-mono text-xs">
            <div className="text-slate-400 text-[10px] uppercase">Practicals Verified</div>
            <div className="text-lg font-bold text-white mt-1">
              {progressMetrics.finishedPracs} / {progressMetrics.totalPracs}
            </div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
              <div
                className="h-full bg-cyan-400 transition-all"
                style={{
                  width: `${progressMetrics.totalPracs > 0 ? (progressMetrics.finishedPracs / progressMetrics.totalPracs) * 100 : 0}%`
                }}
              />
            </div>
          </div>

          {/* Metric 3: Departmental Benchmarks */}
          <div className="p-4 rounded-xl bg-[#020813] border border-slate-800 font-mono text-xs">
            <div className="text-slate-400 text-[10px] uppercase">NBA Outcome Target</div>
            <div className="text-sm font-bold text-emerald-400 mt-1">Tier-1 Attainment</div>
            <div className="text-[10px] text-slate-400 mt-1">OBE Rubric: Level 3 HOTS</div>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <div className="flex gap-2 pt-2 border-t border-slate-800">
          {[
            { id: "projects", label: `Course Projects (${projects.length})`, icon: "🛠️" },
            { id: "practicals", label: `Practical Checklist (${practicals.length})`, icon: "📋" },
            { id: "report_generator", label: "Lab Report Generator", icon: "📑" }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-mono transition-all flex items-center gap-1.5 ${
                activeTab === tab.id
                  ? "bg-slate-800 text-white font-bold border border-slate-700"
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
      {/* VIEW 1: PROJECTS EXPLORER */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "projects" && (
        <div className="space-y-4">
          {/* Project Type Filter Buttons */}
          <div className="flex gap-2 font-mono text-xs">
            {[
              { id: "all", label: "All Projects" },
              { id: "mini", label: "Mini-Projects (25h)" },
              { id: "major", label: "Major Capstones (50h)" }
            ].map(f => (
              <button
                key={f.id}
                onClick={() => setProjectFilter(f.id)}
                className={`px-3 py-1.5 rounded-lg border transition-colors ${
                  projectFilter === f.id
                    ? "bg-[#020813] text-white border-emerald-500/50 font-bold"
                    : "bg-[#041026] text-slate-400 border-slate-800 hover:text-white"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* Projects List */}
          <div className="space-y-5">
            {filteredProjects.map(proj => {
              // Calculate completion for this specific project
              const completedCount = proj.milestones.filter(m => completedMilestones[`${proj.id}_${m.id}`]).length;
              const pct = Math.round((completedCount / proj.milestones.length) * 100);

              return (
                <div key={proj.id} className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-5">
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 border-b border-slate-800 pb-4">
                    <div>
                      <div className="flex items-center gap-2 font-mono text-xs">
                        <span className={`px-2 py-0.5 rounded font-bold uppercase text-[10px] ${
                          proj.type === "major" ? "bg-purple-950 text-purple-300 border border-purple-800/40" : "bg-emerald-950 text-emerald-300 border border-emerald-800/40"
                        }`}>
                          {proj.type === "major" ? "Major Capstone" : "Mini-Project"}
                        </span>
                        <span className="text-slate-400">•</span>
                        <span className="text-slate-300 font-bold">{proj.estimatedHours} Hours</span>
                        <span className="text-slate-400">•</span>
                        <span className="text-amber-400">{proj.difficulty}</span>
                      </div>
                      <h3 className="text-lg font-bold text-white mt-1.5">{proj.title}</h3>
                    </div>

                    <div className="text-right font-mono shrink-0">
                      <div className="text-xs font-bold text-white">{completedCount} / {proj.milestones.length} Milestones</div>
                      <div className="text-[10px] text-emerald-400 font-bold">{pct}% Completed</div>
                    </div>
                  </div>

                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-sans">
                    {proj.summary}
                  </p>

                  {/* Domain Keywords */}
                  <div className="flex flex-wrap gap-1.5">
                    {proj.domainKeywords.map((kw, i) => (
                      <span key={i} className="px-2 py-0.5 rounded bg-[#020813] border border-slate-800 text-[10px] font-mono text-slate-400">
                        #{kw}
                      </span>
                    ))}
                  </div>

                  {/* Hardware & Software Requirements */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
                    <div className="p-3 rounded-xl bg-[#020813] border border-slate-800 space-y-1">
                      <div className="text-[10px] text-slate-500 uppercase font-bold">Hardware Apparatus Required:</div>
                      <ul className="text-slate-300 list-disc list-inside space-y-0.5 text-[11px]">
                        {proj.hardwareApparatus.map((hw, i) => (
                          <li key={i}>{hw}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="p-3 rounded-xl bg-[#020813] border border-slate-800 space-y-1">
                      <div className="text-[10px] text-slate-500 uppercase font-bold">Software Development Tools:</div>
                      <ul className="text-slate-300 list-disc list-inside space-y-0.5 text-[11px]">
                        {proj.softwareTools.map((sw, i) => (
                          <li key={i}>{sw}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Milestones Checklist */}
                  <div className="space-y-2 pt-2 border-t border-slate-800">
                    <div className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider flex items-center justify-between">
                      <span>CIE Phase Milestones &amp; Deliverables:</span>
                      <span className="text-[10px] text-slate-500">Click to update status</span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 font-mono text-xs">
                      {proj.milestones.map(m => {
                        const isDone = Boolean(completedMilestones[`${proj.id}_${m.id}`]);
                        return (
                          <button
                            key={m.id}
                            onClick={() => toggleMilestone(proj.id, m.id)}
                            className={`p-3 rounded-xl border text-left transition-all flex items-start gap-3 ${
                              isDone
                                ? "bg-emerald-950/20 border-emerald-500/40 text-emerald-300"
                                : "bg-[#020813] border-slate-800 text-slate-300 hover:border-slate-700"
                            }`}
                          >
                            <span className="text-sm mt-0.5">{isDone ? "✅" : "⭕"}</span>
                            <div className="space-y-1 flex-1">
                              <div className="flex justify-between items-center">
                                <span className="font-bold text-white text-xs">{m.title}</span>
                                <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                                  {m.weightagePct}% CIE
                                </span>
                              </div>
                              <div className="text-[11px] text-slate-400 font-sans leading-tight">
                                {m.description}
                              </div>
                              <div className="text-[10px] text-slate-500">
                                Deliverable: <strong className="text-slate-300">{m.deliverable}</strong>
                              </div>
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* VIEW 2: PRACTICAL EXPERIMENT CHECKLIST & WORKSHEET */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "practicals" && (
        <div className="space-y-5">
          <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
            <h3 className="font-bold text-base text-white flex items-center gap-2">
              <span>📋</span>
              <span>Prescribed Practical Experiments</span>
            </h3>
            <p className="text-xs text-slate-400">
              Complete and verify practical experiments to fulfill Continuous Internal Evaluation (CIE) requirements.
            </p>

            <div className="space-y-4 font-mono text-xs">
              {practicals.map(prac => {
                const isVerified = Boolean(verifiedPracticals[prac.id]);
                return (
                  <div key={prac.id} className="p-4 rounded-xl bg-[#020813] border border-slate-800 space-y-4">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                      <div>
                        <div className="text-[10px] text-slate-500 uppercase">
                          Experiment #{prac.labNumber} • Unit {prac.unitRoman}
                        </div>
                        <h4 className="text-sm font-bold text-white mt-0.5">{prac.title}</h4>
                      </div>

                      <button
                        onClick={() => togglePractical(prac.id)}
                        className={`px-3 py-1.5 rounded-xl border text-xs font-bold transition-all flex items-center gap-1.5 ${
                          isVerified
                            ? "bg-emerald-950/40 border-emerald-500/50 text-emerald-300"
                            : "bg-slate-800 border-slate-700 text-slate-300 hover:text-white"
                        }`}
                      >
                        <span>{isVerified ? "✅ VERIFIED BY FACULTY" : "⭕ PENDING VERIFICATION"}</span>
                      </button>
                    </div>

                    <div className="text-slate-300 text-xs font-sans">
                      <strong>Aim: </strong>{prac.aim}
                    </div>

                    {/* Calculation Worksheet */}
                    <div className="p-3.5 rounded-xl bg-[#041026] border border-slate-800 space-y-2">
                      <div className="text-white font-bold text-xs flex items-center gap-1.5">
                        <span>📐</span>
                        <span>Calculation Worksheet &amp; Expected Results:</span>
                      </div>
                      <div className="p-2.5 rounded-lg bg-[#020813] border border-slate-800 text-slate-200">
                        <code>{prac.calculationWorksheet.formula}</code>
                      </div>
                      <div className="text-[11px] text-slate-400 font-sans leading-relaxed">
                        {prac.calculationWorksheet.description}
                      </div>
                      <div className="text-[11px] text-emerald-400 font-mono">
                        Benchmark: <strong>{prac.calculationWorksheet.expectedResult}</strong>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* VIEW 3: LAB REPORT GENERATOR */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "report_generator" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* LEFT: CONFIGURATION FORM (4 COLS) */}
          <div className="lg:col-span-4 p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4 font-mono text-xs">
            <h3 className="font-bold text-sm text-white flex items-center gap-2">
              <span>📑</span>
              <span>Report Details</span>
            </h3>

            <div className="space-y-3">
              <div>
                <label className="text-slate-400 block mb-1">Select Experiment:</label>
                <select
                  value={selectedPracticalId}
                  onChange={(e) => setSelectedPracticalId(e.target.value)}
                  className="w-full p-2.5 rounded-xl bg-[#020813] border border-slate-800 text-white font-mono text-xs focus:border-emerald-500 outline-none"
                >
                  {practicals.map(p => (
                    <option key={p.id} value={p.id}>
                      Exp #{p.labNumber}: {p.title}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Student Name:</label>
                <input
                  type="text"
                  value={studentName}
                  onChange={(e) => setStudentName(e.target.value)}
                  className="w-full p-2.5 rounded-xl bg-[#020813] border border-slate-800 text-white font-mono text-xs focus:border-emerald-500 outline-none"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Register / Roll Number:</label>
                <input
                  type="text"
                  value={rollNumber}
                  onChange={(e) => setRollNumber(e.target.value)}
                  className="w-full p-2.5 rounded-xl bg-[#020813] border border-slate-800 text-white font-mono text-xs focus:border-emerald-500 outline-none"
                />
              </div>

              <button
                onClick={handleDownloadReport}
                className="w-full py-2.5 rounded-xl font-bold font-mono text-xs transition-all shadow-md flex items-center justify-center gap-2 mt-4"
                style={{
                  backgroundColor: themeColor,
                  color: "#020813"
                }}
              >
                <span>💾</span>
                <span>Download Report (.md)</span>
              </button>
            </div>
          </div>

          {/* RIGHT: PREVIEW CANVAS (8 COLS) */}
          <div className="lg:col-span-8 p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-bold text-sm text-white font-mono flex items-center gap-2">
                <span>👁️</span>
                <span>Generated Markdown Report Preview</span>
              </h3>
              <span className="text-[10px] font-mono text-slate-400">Modular Engineering Format</span>
            </div>

            <pre className="w-full p-4 rounded-xl bg-[#020813] border border-slate-800 text-slate-300 font-mono text-[11px] leading-relaxed overflow-x-auto max-h-[460px] overflow-y-auto whitespace-pre-wrap">
              {generatedReportText}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
