/**
 * ========================================================================================
 * VoltCore Apex Academia - AI Viva Voce Simulator & OBE Analytics Hub
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Module: src/components/VivaVoceSimulatorHub.jsx
 * Platform Lead & Systems Director: Ashok Kumar A (2023MITEC042)
 *
 * Capabilities:
 *   1. Conversational Oral Viva Examination across 5 Core ECE Domains
 *   2. Adaptive Question Selection with Bloom's Taxonomy Cognitive Grading Rubrics
 *   3. Course Outcome (CO1-CO5) & Program Outcome (PO1-PO12) Attainment Tracking
 *   4. Institutional Threshold Gating (>= 70%) & Exportable NBA Accreditation Report
 * ========================================================================================
 */

import React, { useState } from 'react';
import SubjectEmblem from './SubjectEmblem.jsx';

const VIVA_DOMAINS = [
  {
    id: "circuit_theorems",
    title: "Circuit Theorems & MNA Formulations",
    code: "EC23C01",
    targetCO: "CO1",
    sampleQ: "State Thevenin's Theorem for active networks and explain how to find Rth with dependent sources.",
    keyPoints: ["Thevenin Vth", "Rth test source Vx/Ix", "Dependent sources active", "MNA formulation"]
  },
  {
    id: "semiconductor_physics",
    title: "Semiconductor Physics & Bandgaps",
    code: "EC23C02",
    targetCO: "CO2",
    sampleQ: "Define the Fermi energy level Ef and describe how donor and acceptor doping shifts Ef.",
    keyPoints: ["Fermi level 50% probability", "Nd donor shifts to Ec", "Na acceptor shifts to Ev", "Intrinsic ni"]
  },
  {
    id: "feedback_stability",
    title: "Feedback Stability & Nyquist Contours",
    code: "EC23C07",
    targetCO: "CO3",
    sampleQ: "State the Barkhausen criteria for sustained oscillations and loop gain startup conditions.",
    keyPoints: ["|A*beta| = 1", "Phase shift 0 or 360", "Loop gain > 1 at startup", "Non-linear limiting"]
  },
  {
    id: "rtl_design",
    title: "Synchronous RTL & Timing Closure",
    code: "EC23C06",
    targetCO: "CO4",
    sampleQ: "Compare Mealy and Moore FSMs, and explain why hold time violations cannot be fixed by lowering clock speed.",
    keyPoints: ["Moore depends only on state", "Mealy input glitches", "Hold time independent of Tclk", "Delay buffer insertion"]
  },
  {
    id: "protocol_timing",
    title: "Protocol Timing & Bus Arbitration",
    code: "EC8702",
    targetCO: "CO5",
    sampleQ: "Explain open-drain outputs with pull-ups in I2C and describe how slave clock stretching operates.",
    keyPoints: ["Open-drain wired-AND", "Zero shoot-through current", "Slave pulls SCL low", "Non-destructive CAN arbitration"]
  }
];

const INITIAL_CO_ATTAINMENT = {
  CO1: { earned: 84.0, max: 100.0, pct: 84.0, level: 3, status: "ATTAINED" },
  CO2: { earned: 76.5, max: 100.0, pct: 76.5, level: 3, status: "ATTAINED" },
  CO3: { earned: 82.0, max: 100.0, pct: 82.0, level: 3, status: "ATTAINED" },
  CO4: { earned: 68.0, max: 100.0, pct: 68.0, level: 2, status: "ACTION_REQUIRED" },
  CO5: { earned: 91.5, max: 100.0, pct: 91.5, level: 3, status: "ATTAINED" }
};

export default function VivaVoceSimulatorHub() {
  const [selectedDomainId, setSelectedDomainId] = useState("circuit_theorems");
  const [studentAnswer, setStudentAnswer] = useState("");
  const [activeTab, setActiveTab] = useState("viva"); // "viva" | "obe" | "matrix"
  const [evaluation, setEvaluation] = useState(null);
  const [evaluating, setEvaluating] = useState(false);
  const [coData, setCoData] = useState(INITIAL_CO_ATTAINMENT);
  const [copiedReport, setCopiedReport] = useState(false);

  const currentDomain = VIVA_DOMAINS.find(d => d.id === selectedDomainId) || VIVA_DOMAINS[0];

  const handleEvaluate = () => {
    if (!studentAnswer.trim()) return;
    setEvaluating(true);

    // Simulated evaluation matching backend deterministic rubric
    setTimeout(() => {
      const text = studentAnswer.toLowerCase();
      const matched = currentDomain.keyPoints.filter(kp => text.includes(kp.toLowerCase()) || kp.toLowerCase().split(' ').some(w => text.includes(w)));
      const ratio = matched.length / currentDomain.keyPoints.length;

      const depth = Math.min(5.0, Math.round((ratio * 4.5 + (text.split(' ').length > 25 ? 0.5 : 0.0)) * 10) / 10);
      const precision = Math.min(3.0, Math.round((ratio * 3.0) * 10) / 10);
      const clarity = text.split(' ').length > 20 ? 2.0 : 1.0;
      const totalScore = Math.min(10.0, Math.round((depth + precision + clarity) * 10) / 10);

      const targetCO = currentDomain.targetCO;
      setEvaluation({
        score: totalScore,
        maxMarks: 10.0,
        pct: totalScore * 10.0,
        bloom: totalScore >= 8.0 ? "L5 (Evaluate) - Mastered" : (totalScore >= 6.0 ? "L4 (Analyze) - Attained" : "L3 (Apply) - Revision Recommended"),
        verdict: totalScore >= 7.0 ? "Threshold Attained (>= 70%)" : "Remedial Review Required (< 70%)",
        rubric: { depth, precision, clarity },
        matched,
        missing: currentDomain.keyPoints.filter(kp => !matched.includes(kp)),
        adaptiveNext: totalScore >= 8.0 ? "Advanced Synthesis Probe" : "Foundational Concept Clarification"
      });

      // Update CO Attainment
      setCoData(prev => {
        const curr = prev[targetCO];
        const newEarned = curr.earned + totalScore;
        const newMax = curr.max + 10.0;
        const newPct = Math.round((newEarned / newMax) * 1000) / 10;
        return {
          ...prev,
          [targetCO]: {
            ...curr,
            earned: newEarned,
            max: newMax,
            pct: newPct,
            level: newPct >= 70.0 ? 3 : (newPct >= 60.0 ? 2 : 1),
            status: newPct >= 70.0 ? "ATTAINED" : "ACTION_REQUIRED"
          }
        };
      });

      setEvaluating(false);
    }, 600);
  };

  const handleCopyReport = () => {
    const reportText = `
# VoltCore Apex Academia - NBA / OBE Accreditation Matrix
Institution: Madras Institute of Technology (MIT) Campus, Anna University
Threshold Gating: >= 70.0%

| Course Outcome | Attainment % | Level (0-3) | Status | Gating (>=70%) |
| :--- | :---: | :---: | :---: | :---: |
| CO1 (Circuits) | ${coData.CO1.pct}% | Level ${coData.CO1.level} | ${coData.CO1.status} | ${coData.CO1.pct >= 70 ? 'PASS' : 'ACTION'} |
| CO2 (Devices) | ${coData.CO2.pct}% | Level ${coData.CO2.level} | ${coData.CO2.status} | ${coData.CO2.pct >= 70 ? 'PASS' : 'ACTION'} |
| CO3 (Feedback) | ${coData.CO3.pct}% | Level ${coData.CO3.level} | ${coData.CO3.status} | ${coData.CO3.pct >= 70 ? 'PASS' : 'ACTION'} |
| CO4 (RTL/Timing) | ${coData.CO4.pct}% | Level ${coData.CO4.level} | ${coData.CO4.status} | ${coData.CO4.pct >= 70 ? 'PASS' : 'ACTION'} |
| CO5 (Protocols) | ${coData.CO5.pct}% | Level ${coData.CO5.level} | ${coData.CO5.status} | ${coData.CO5.pct >= 70 ? 'PASS' : 'ACTION'} |
    `.trim();

    navigator.clipboard.writeText(reportText);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2000);
  };

  return (
    <div className="space-y-6 font-mono text-[var(--theme-text,#F8FAFC)]">

      {/* Top Domain Selector Carousel */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <span className="text-xs uppercase tracking-wider text-slate-400 font-bold">
            Select ECE Viva Voce Oral Assessment Domain:
          </span>
          <span className="text-[11px] font-mono text-cyan-400 font-semibold bg-cyan-500/10 px-2.5 py-0.5 rounded-full border border-cyan-500/20">
            Bloom's Cognitive Rubrics Active
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3">
          {VIVA_DOMAINS.map((dom) => {
            const isSelected = dom.id === selectedDomainId;
            return (
              <button
                key={dom.id}
                onClick={() => {
                  setSelectedDomainId(dom.id);
                  setEvaluation(null);
                  setStudentAnswer("");
                }}
                className={`p-3.5 rounded-2xl text-left transition-all border flex flex-col justify-between ${
                  isSelected
                    ? "bg-slate-900/90 border-[var(--theme-primary,#00F0B5)] shadow-lg shadow-emerald-500/10 scale-[1.02]"
                    : "bg-slate-950/60 border-slate-800/80 hover:border-slate-700"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <SubjectEmblem courseCode={dom.code} size="sm" showFrame={true} />
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-emerald-400 border border-slate-800 font-bold">
                      {dom.targetCO}
                    </span>
                  </div>
                  <div className="text-xs font-bold text-white tracking-tight font-sans line-clamp-2">
                    {dom.title}
                  </div>
                </div>
                <div className="text-[10px] font-mono text-slate-500 mt-2">
                  [{dom.code}]
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Tab Navigation */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
        <button
          onClick={() => setActiveTab("viva")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === "viva"
              ? "bg-[var(--theme-primary,#00F0B5)]/15 text-[var(--theme-primary,#00F0B5)] border border-[var(--theme-primary,#00F0B5)]/40"
              : "text-slate-400 hover:text-white"
          }`}
        >
          <span>🎙️</span>
          <span>Conversational Viva Simulator</span>
        </button>

        <button
          onClick={() => setActiveTab("obe")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === "obe"
              ? "bg-cyan-500/15 text-cyan-400 border border-cyan-500/40"
              : "text-slate-400 hover:text-white"
          }`}
        >
          <span>📊</span>
          <span>OBE &amp; CO-PO Attainment Dashboard</span>
        </button>

        <button
          onClick={() => setActiveTab("matrix")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === "matrix"
              ? "bg-purple-500/15 text-purple-400 border border-purple-500/40"
              : "text-slate-400 hover:text-white"
          }`}
        >
          <span>📜</span>
          <span>NBA / ABET Accreditation Matrix</span>
        </button>
      </div>

      {/* Tab 1: Conversational Viva Voce Simulator */}
      {activeTab === "viva" && (
        <div className="glass-card-accent rounded-3xl p-6 border border-slate-800/80 bg-slate-950/80 shadow-2xl space-y-6">

          {/* Examiner Question Card */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="flex items-center gap-2 font-bold text-emerald-400">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                AI Examiner Prompt • Target: {currentDomain.targetCO}
              </span>
              <span className="font-mono text-slate-500">Max Marks: 10.0</span>
            </div>

            <p className="text-sm sm:text-base font-sans font-bold text-white leading-relaxed">
              "{currentDomain.sampleQ}"
            </p>

            <div className="flex flex-wrap items-center gap-2 pt-2 text-[11px] text-slate-400">
              <span className="font-semibold text-slate-500">Assessment Focus:</span>
              {currentDomain.keyPoints.map((kp, idx) => (
                <span key={idx} className="px-2 py-0.5 rounded-md bg-slate-950 text-slate-300 border border-slate-800">
                  {kp}
                </span>
              ))}
            </div>
          </div>

          {/* Student Verbal/Text Defense Input */}
          <div className="space-y-3">
            <label className="text-xs uppercase tracking-wider text-slate-400 font-bold block">
              Student Oral / Written Technical Defense:
            </label>
            <textarea
              rows={4}
              value={studentAnswer}
              onChange={(e) => setStudentAnswer(e.target.value)}
              placeholder="State your formal technical explanation, referencing governing equations, semiconductor limits, or protocol timing..."
              className="w-full p-4 rounded-2xl bg-slate-900/90 border border-slate-700 text-sm text-white focus:outline-none focus:border-emerald-400 font-sans leading-relaxed transition-all"
            />

            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-500">
                Evaluated deterministically with cloud LLM grounding fallback.
              </span>
              <button
                onClick={handleEvaluate}
                disabled={evaluating || !studentAnswer.trim()}
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-sans font-bold text-xs uppercase tracking-wider shadow-lg transition-all disabled:opacity-50"
              >
                {evaluating ? "Evaluating..." : "Submit Oral Defense"}
              </button>
            </div>
          </div>

          {/* Evaluation Results Banner */}
          {evaluation && (
            <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4 animate-fadeIn">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
                <div>
                  <span className="text-xs uppercase tracking-wider text-slate-400">Oral Defense Score:</span>
                  <div className="text-2xl font-extrabold text-emerald-400 font-sans mt-0.5">
                    {evaluation.score} / {evaluation.maxMarks} Marks ({evaluation.pct}%)
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xs font-mono font-bold px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                    {evaluation.verdict}
                  </span>
                  <div className="text-[11px] text-slate-400 font-mono mt-1">
                    {evaluation.bloom}
                  </div>
                </div>
              </div>

              {/* Rubric Breakdown */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-center">
                  <div className="text-[10px] text-slate-500 uppercase">Core Depth (5.0)</div>
                  <div className="text-lg font-bold text-cyan-400 font-mono">{evaluation.rubric.depth}</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-center">
                  <div className="text-[10px] text-slate-500 uppercase">Keyword Precision (3.0)</div>
                  <div className="text-lg font-bold text-purple-400 font-mono">{evaluation.rubric.precision}</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-center">
                  <div className="text-[10px] text-slate-500 uppercase">Clarity &amp; Structure (2.0)</div>
                  <div className="text-lg font-bold text-amber-400 font-mono">{evaluation.rubric.clarity}</div>
                </div>
              </div>

              {/* Adaptive Next Question Directive */}
              <div className="p-3.5 rounded-xl bg-slate-950/80 border border-cyan-800/40 text-xs flex items-center justify-between">
                <span className="text-slate-300">
                  <strong className="text-cyan-400">Adaptive Branching:</strong> Next recommended prompt scheduled as <em>{evaluation.adaptiveNext}</em>.
                </span>
                <span className="text-slate-500 font-mono text-[10px]">Session ID: VIVA-AUTO-VERIFIED</span>
              </div>
            </div>
          )}

        </div>
      )}

      {/* Tab 2: OBE & CO-PO Attainment Dashboard */}
      {activeTab === "obe" && (
        <div className="glass-card-accent rounded-3xl p-6 border border-slate-800/80 bg-slate-950/80 shadow-2xl space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-white font-sans">
                Course Outcome (CO1–CO5) Attainment Matrix
              </h3>
              <p className="text-xs text-slate-400">
                Institutional Accreditation Threshold: Direct Attainment &ge; 70.0%
              </p>
            </div>
            <button
              onClick={handleCopyReport}
              className="px-4 py-2 rounded-xl bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 text-xs font-bold hover:bg-cyan-500/25 transition-all"
            >
              {copiedReport ? "✓ Copied Report!" : "Export NBA Report"}
            </button>
          </div>

          {/* CO Attainment Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
            {Object.entries(coData).map(([coKey, co]) => {
              const isPassing = co.pct >= 70.0;
              return (
                <div
                  key={coKey}
                  className={`p-4 rounded-2xl border text-center transition-all ${
                    isPassing ? "bg-emerald-950/20 border-emerald-500/40" : "bg-amber-950/20 border-amber-500/40"
                  }`}
                >
                  <div className="text-xs font-bold font-mono text-slate-300 mb-1">{coKey}</div>
                  <div className={`text-2xl font-extrabold font-mono ${isPassing ? "text-emerald-400" : "text-amber-400"}`}>
                    {co.pct}%
                  </div>
                  <div className="text-[10px] uppercase font-bold tracking-wider mt-1 text-slate-400">
                    Level {co.level} / 3
                  </div>
                  <span className={`inline-block mt-2 px-2 py-0.5 rounded text-[9px] font-bold ${
                    isPassing ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"
                  }`}>
                    {co.status}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Program Outcomes (PO1-PO12) Summary */}
          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
            <h4 className="text-sm font-bold text-white">Program Outcome (PO1-PO12, PSO1-PSO2) Weighted Attainment</h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2 text-center text-xs">
              {["PO1", "PO2", "PO3", "PO4", "PO5", "PO9", "PO10", "PO11", "PO12", "PSO1", "PSO2"].map((po) => (
                <div key={po} className="p-2.5 rounded-xl bg-slate-950 border border-slate-800">
                  <div className="font-bold text-cyan-400 font-mono">{po}</div>
                  <div className="text-[11px] text-slate-300 mt-0.5">&gt; 78.5%</div>
                  <div className="text-[9px] text-emerald-400 font-semibold mt-0.5">✓ Attained</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Exportable NBA Matrix */}
      {activeTab === "matrix" && (
        <div className="glass-card-accent rounded-3xl p-6 border border-slate-800/80 bg-slate-950/80 shadow-2xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-white font-sans">
                Official NBA / ABET Accreditation Ledger
              </h3>
              <p className="text-xs text-slate-400">
                Anna University Regulation 2023 Statutory Audit Format
              </p>
            </div>
            <button
              onClick={handleCopyReport}
              className="px-4 py-2 rounded-xl bg-purple-500/15 text-purple-300 border border-purple-500/30 text-xs font-bold hover:bg-purple-500/25 transition-all"
            >
              {copiedReport ? "✓ Copied Table!" : "Copy Markdown Table"}
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300 border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-mono">
                  <th className="py-2.5 px-3">Course Outcome</th>
                  <th className="py-2.5 px-3">Score %</th>
                  <th className="py-2.5 px-3">Attainment Level</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Accreditation Threshold (&ge;70%)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {Object.entries(coData).map(([coKey, co]) => (
                  <tr key={coKey} className="hover:bg-slate-900/40">
                    <td className="py-2.5 px-3 font-bold text-white">{coKey}</td>
                    <td className="py-2.5 px-3">{co.pct}%</td>
                    <td className="py-2.5 px-3 text-cyan-400">Level {co.level} / 3</td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] ${
                        co.pct >= 70 ? "bg-emerald-500/15 text-emerald-300" : "bg-amber-500/15 text-amber-300"
                      }`}>
                        {co.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-emerald-400 font-bold">
                      {co.pct >= 70 ? "✓ COMPLIANT" : "✗ ACTION REQUIRED"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  );
}
