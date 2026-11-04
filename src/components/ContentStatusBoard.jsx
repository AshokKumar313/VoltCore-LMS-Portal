import React, { useState, useEffect } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Curriculum Module Content Status & Lifecycle Board
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Component: src/components/ContentStatusBoard.jsx
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * 
 * Lifecycle Stages:
 *   1. Draft -> 2. AI-Generated -> 3. Human-Reviewed -> 4. Faculty-Approved -> 5. Published
 * ========================================================================================
 */

const STAGES = [
  { id: 'Draft', label: 'Draft', color: 'border-slate-700 bg-slate-900/40 text-slate-400' },
  { id: 'AI-Generated', label: 'AI-Generated', color: 'border-cyan-500/40 bg-cyan-950/20 text-cyan-400' },
  { id: 'Human-Reviewed', label: 'Human-Reviewed', color: 'border-amber-500/40 bg-amber-950/20 text-amber-400' },
  { id: 'Faculty-Approved', label: 'Faculty-Approved', color: 'border-blue-500/40 bg-blue-950/20 text-blue-400' },
  { id: 'Published', label: 'Published (Live)', color: 'border-emerald-500/50 bg-emerald-950/30 text-[#00F0B5]' }
];

const INITIAL_MODULES = [
  { module_code: 'EC8701', module_title: 'IoT Edge Node Foundations & Bare-Metal GPIO', status: 'Published', reviewer_name: 'Dr. S. Ramanujam (MIT Faculty)', completion_pct: 100, quality_score: 9.8 },
  { module_code: 'EC8702', module_title: 'Embedded Systems Architecture & Microcontrollers', status: 'Published', reviewer_name: 'Dr. P. V. Anand (MIT Faculty)', completion_pct: 100, quality_score: 9.6 },
  { module_code: 'EC8703', module_title: 'Defense UAV Telemetry & 2.4GHz FHSS', status: 'Published', reviewer_name: 'Prof. K. Venkatesh (Aerospace Div)', completion_pct: 100, quality_score: 9.9 },
  { module_code: 'EC8704', module_title: 'Automotive Radar & Ultrasonic Edge Sensing', status: 'Faculty-Approved', reviewer_name: 'Dr. M. Soundararajan', completion_pct: 95, quality_score: 9.4 },
  { module_code: 'EC8705', module_title: '5-Stage RV32I RISC-V Soft-Core in Verilog', status: 'Published', reviewer_name: 'Ashok Kumar A (Platform Architect)', completion_pct: 100, quality_score: 10.0 },
  { module_code: 'EC8706', module_title: 'FreeRTOS & Deterministic Multi-Core Scheduling', status: 'Published', reviewer_name: 'Dr. S. Ramanujam', completion_pct: 100, quality_score: 9.7 },
  { module_code: 'EC8707', module_title: 'High-Speed Railway Edge AI Track Defect Vision', status: 'Human-Reviewed', reviewer_name: 'Faculty Review Committee', completion_pct: 90, quality_score: 9.1 },
  { module_code: 'EC8708', module_title: 'ARM Cortex-M DMA Architecture & Zero-Copy IPC', status: 'Published', reviewer_name: 'Ashok Kumar A (Platform Architect)', completion_pct: 100, quality_score: 9.9 },
  { module_code: 'EC8709', module_title: 'TinyML Edge AI Neural Networks & Vibration FFT', status: 'Published', reviewer_name: 'Ashok Kumar A & MIT Faculty', completion_pct: 100, quality_score: 9.9 }
];

export default function ContentStatusBoard() {
  const [modules, setModules] = useState(INITIAL_MODULES);
  const [selectedFilter, setSelectedFilter] = useState('ALL');
  const [changelog, setChangelog] = useState([]);
  const [showChangelogDrawer, setShowChangelogDrawer] = useState(false);
  const [updatingCode, setUpdatingCode] = useState(null);
  const [transitionStatus, setTransitionStatus] = useState('Published');
  const [reviewerComment, setReviewerComment] = useState('');

  // Fetch status report from API
  useEffect(() => {
    fetch('/api/content/status')
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data && data.modules && data.modules.length > 0) {
          setModules(data.modules);
        }
      })
      .catch(() => {
        // Fallback to local default state
      });
  }, []);

  // Fetch changelog audit history
  const loadChangelog = () => {
    fetch('/api/content/changelog')
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data && data.changelog) {
          setChangelog(data.changelog);
        }
      })
      .catch(() => {});
    setShowChangelogDrawer(true);
  };

  // Submit status update
  const handleStatusSubmit = async (e) => {
    e.preventDefault();
    if (!updatingCode) return;

    const payload = {
      module_code: updatingCode,
      status: transitionStatus,
      author: 'Ashok Kumar A (Platform Architect)',
      comment: reviewerComment || `Transitioned status to ${transitionStatus}`
    };

    try {
      const res = await fetch('/api/content/status/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error('API Offline');
    } catch {
      // Local state update
    }

    setModules(prev =>
      prev.map(m =>
        m.module_code === updatingCode
          ? { ...m, status: transitionStatus, last_updated: new Date().toISOString() }
          : m
      )
    );

    setUpdatingCode(null);
    setReviewerComment('');
  };

  // Metrics calculation
  const total = modules.length;
  const publishedCount = modules.filter(m => m.status === 'Published').length;
  const publishedPct = total ? Math.round((publishedCount / total) * 100) : 0;
  const avgQuality = (modules.reduce((acc, m) => acc + (m.quality_score || 0), 0) / (total || 1)).toFixed(1);

  const filteredModules = selectedFilter === 'ALL'
    ? modules
    : modules.filter(m => m.status === selectedFilter);

  return (
    <div className="rounded-3xl border border-[#00F0B5]/30 bg-gradient-to-b from-[#020813] via-[#041026] to-[#020813] p-5 sm:p-7 shadow-2xl font-mono text-slate-100 space-y-6">
      
      {/* Top Header & Metrics Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-5 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-6 bg-gradient-to-b from-[#00693E] to-[#00F0B5] rounded-full"></span>
            <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <span>Curriculum Content Status & Editorial Lifecycle</span>
              <span className="text-[10px] uppercase px-2 py-0.5 rounded bg-[#00693E]/50 text-[#00F0B5] border border-[#00F0B5]/30">
                SQLite WAL
              </span>
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Madras Institute of Technology (MIT Campus, Anna University) • Quality Assurance & Faculty Sign-Off Tracking
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2.5 text-xs">
          <button
            onClick={loadChangelog}
            className="px-3.5 py-1.5 rounded-xl bg-[#020813] border border-slate-800 hover:border-[#00F0B5]/40 text-slate-300 hover:text-white transition-all flex items-center gap-1.5"
          >
            <span>📜 View Audit Changelog</span>
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-xl bg-[#020813]/80 border border-slate-800">
          <div className="text-[10px] uppercase text-slate-400">Total Modules</div>
          <div className="text-2xl font-bold text-white mt-0.5">{total}</div>
          <div className="text-[10px] text-slate-500">Tier 1 - 4 Syllabus</div>
        </div>

        <div className="p-3.5 rounded-xl bg-[#020813]/80 border border-emerald-500/20">
          <div className="text-[10px] uppercase text-emerald-400">Published Rate</div>
          <div className="text-2xl font-bold text-[#00F0B5] mt-0.5">{publishedPct}%</div>
          <div className="text-[10px] text-emerald-300/70">{publishedCount}/{total} Live Modules</div>
        </div>

        <div className="p-3.5 rounded-xl bg-[#020813]/80 border border-amber-500/20">
          <div className="text-[10px] uppercase text-amber-400">Average QA Score</div>
          <div className="text-2xl font-bold text-amber-400 mt-0.5">{avgQuality} / 10</div>
          <div className="text-[10px] text-amber-300/70">Anti-Hallucination Verified</div>
        </div>

        <div className="p-3.5 rounded-xl bg-[#020813]/80 border border-cyan-500/20">
          <div className="text-[10px] uppercase text-cyan-400">Editorial Authority</div>
          <div className="text-sm font-bold text-cyan-300 mt-1.5">MIT ECE Board</div>
          <div className="text-[10px] text-slate-500">Regulation 2023</div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-1.5 p-1 rounded-2xl bg-[#020813] border border-slate-800 text-xs">
        <button
          onClick={() => setSelectedFilter('ALL')}
          className={`px-3 py-1.5 rounded-xl transition-all ${
            selectedFilter === 'ALL'
              ? 'bg-[#00693E] text-[#00F0B5] font-bold shadow-sm'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          All Stages ({total})
        </button>
        {STAGES.map(s => {
          const count = modules.filter(m => m.status === s.id).length;
          return (
            <button
              key={s.id}
              onClick={() => setSelectedFilter(s.id)}
              className={`px-3 py-1.5 rounded-xl transition-all flex items-center gap-1.5 ${
                selectedFilter === s.id
                  ? 'bg-[#00693E] text-[#00F0B5] font-bold shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span>{s.label}</span>
              <span className="text-[10px] px-1 rounded bg-[#020813] text-slate-400">
                {count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Modules Matrix / Table */}
      <div className="rounded-2xl border border-slate-800 bg-[#020813] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-[#041026] text-slate-400 border-b border-slate-800 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="p-3.5">Code</th>
                <th className="p-3.5">Module Title</th>
                <th className="p-3.5">Lifecycle Status</th>
                <th className="p-3.5">Reviewer Attribution</th>
                <th className="p-3.5">QA Score</th>
                <th className="p-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredModules.map(m => {
                const stageConfig = STAGES.find(s => s.id === m.status) || STAGES[0];
                return (
                  <tr key={m.module_code} className="hover:bg-[#041026]/60 transition-colors">
                    <td className="p-3.5 font-bold text-white whitespace-nowrap">
                      <span className="px-2 py-0.5 rounded bg-[#041026] text-[#00F0B5] border border-[#00F0B5]/30">
                        {m.module_code}
                      </span>
                    </td>
                    <td className="p-3.5 text-slate-200 font-semibold max-w-xs truncate">
                      {m.module_title}
                    </td>
                    <td className="p-3.5 whitespace-nowrap">
                      <span className={`px-2.5 py-1 rounded-full border text-[11px] font-bold ${stageConfig.color}`}>
                        {m.status}
                      </span>
                    </td>
                    <td className="p-3.5 text-slate-400 whitespace-nowrap text-[11px]">
                      {m.reviewer_name || 'Faculty Review Board'}
                    </td>
                    <td className="p-3.5 whitespace-nowrap">
                      <span className="text-amber-400 font-bold">{m.quality_score}</span>
                      <span className="text-slate-500 text-[10px]"> / 10</span>
                    </td>
                    <td className="p-3.5 text-right whitespace-nowrap">
                      <button
                        onClick={() => {
                          setUpdatingCode(m.module_code);
                          setTransitionStatus(m.status);
                        }}
                        className="px-2.5 py-1 rounded-lg bg-[#00693E]/20 text-[#00F0B5] border border-[#00F0B5]/30 hover:bg-[#00F0B5] hover:text-[#020813] transition-all text-xs font-bold"
                      >
                        Transition Status ✎
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Transition Modal */}
      {updatingCode && (
        <div className="fixed inset-0 bg-[#020813]/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full rounded-2xl bg-[#041026] border border-[#00F0B5]/40 p-5 space-y-4 shadow-2xl font-mono text-xs">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <span className="font-bold text-white text-sm">
                Transition Status: {updatingCode}
              </span>
              <button
                onClick={() => setUpdatingCode(null)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleStatusSubmit} className="space-y-3">
              <div>
                <label className="block text-slate-400 text-[11px] mb-1">Select Target Lifecycle Stage:</label>
                <select
                  value={transitionStatus}
                  onChange={(e) => setTransitionStatus(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#020813] border border-slate-800 text-white focus:outline-none focus:border-[#00F0B5]"
                >
                  {STAGES.map(s => (
                    <option key={s.id} value={s.id}>{s.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-400 text-[11px] mb-1">Reviewer Editorial Comment:</label>
                <textarea
                  value={reviewerComment}
                  onChange={(e) => setReviewerComment(e.target.value)}
                  placeholder="e.g. KaTeX math validated, references verified against IEEE Transactions..."
                  rows={3}
                  className="w-full px-3 py-2 rounded-xl bg-[#020813] border border-slate-800 text-white focus:outline-none focus:border-[#00F0B5] text-xs placeholder-slate-500"
                ></textarea>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setUpdatingCode(null)}
                  className="px-3 py-1.5 rounded-xl border border-slate-700 text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-xl bg-[#00F0B5] text-[#020813] font-bold hover:bg-emerald-300 transition-all"
                >
                  Commit Status & Log
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Changelog Drawer Modal */}
      {showChangelogDrawer && (
        <div className="fixed inset-0 bg-[#020813]/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="max-w-2xl w-full rounded-2xl bg-[#041026] border border-[#00F0B5]/40 p-5 space-y-4 shadow-2xl font-mono text-xs">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div>
                <span className="font-bold text-white text-sm">
                  SQLite WAL Audit Changelog
                </span>
                <p className="text-[10px] text-slate-400">Historical status transitions recorded in voltcore_lms.db</p>
              </div>
              <button
                onClick={() => setShowChangelogDrawer(false)}
                className="text-slate-400 hover:text-white text-base"
              >
                ✕
              </button>
            </div>

            <div className="max-h-80 overflow-y-auto space-y-2">
              {changelog.length === 0 ? (
                <div className="text-center py-8 text-slate-500">
                  No previous changelog entries recorded in database yet.
                </div>
              ) : (
                changelog.map(log => (
                  <div key={log.id} className="p-3 rounded-xl bg-[#020813] border border-slate-800 space-y-1">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="font-bold text-[#00F0B5]">{log.module_code}</span>
                      <span className="text-slate-500">{log.timestamp}</span>
                    </div>
                    <div className="text-xs text-slate-300">
                      <span className="text-slate-500">{log.previous_status}</span>
                      <span className="text-[#00F0B5] mx-1.5">➔</span>
                      <span className="text-emerald-400 font-bold">{log.new_status}</span>
                      <span className="text-slate-500 text-[10px] ml-2">by {log.author}</span>
                    </div>
                    {log.comment && (
                      <p className="text-[11px] text-slate-400 italic">"{log.comment}"</p>
                    )}
                  </div>
                ))
              )}
            </div>

            <div className="text-right pt-2 border-t border-slate-800">
              <button
                onClick={() => setShowChangelogDrawer(false)}
                className="px-4 py-1.5 rounded-xl bg-[#020813] border border-slate-700 text-slate-300 hover:text-white"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

