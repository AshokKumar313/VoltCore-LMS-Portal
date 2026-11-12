import React, { useState } from 'react';
import nptelData from '../data/nptel_mapper.json';

/**
 * ========================================================================================
 * VoltCore Apex Academia - NPTEL Video & Anna University Regulation 2023 Curriculum Mapper
 * Department of Electronics Engineering, MIT Campus, Anna University
 * ----------------------------------------------------------------------------------------
 * Component: src/components/NptelCurriculumMapper.jsx
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * ========================================================================================
 */

export default function NptelCurriculumMapper() {
  const [selectedModule, setSelectedModule] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const modules = nptelData.modules || [];

  const filteredModules = modules.filter((mod) => {
    if (selectedModule !== 'ALL' && mod.module_code !== selectedModule) {
      return false;
    }
    if (!searchQuery.trim()) return true;

    const query = searchQuery.toLowerCase();
    const titleMatch = mod.module_title.toLowerCase().includes(query);
    const codeMatch = mod.module_code.toLowerCase().includes(query);
    const instructorMatch = mod.nptel_course.instructor.toLowerCase().includes(query);
    const conceptMatch = mod.nptel_course.lectures.some((lec) =>
      lec.key_concepts.some((c) => c.toLowerCase().includes(query)) ||
      lec.lecture_title.toLowerCase().includes(query)
    );

    return titleMatch || codeMatch || instructorMatch || conceptMatch;
  });

  const formatTimestamp = (sec) => {
    const mins = Math.floor(sec / 60);
    const remainingSec = sec % 60;
    return `${mins}:${remainingSec < 10 ? '0' : ''}${remainingSec}`;
  };

  return (
    <div className="rounded-3xl border border-[#00F0B5]/30 bg-gradient-to-b from-[#020813] via-[#041026] to-[#020813] p-5 sm:p-7 shadow-2xl font-mono text-slate-100 space-y-6">
      
      {/* Header & Academic Credentials */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-5 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-6 bg-gradient-to-b from-[#00693E] to-[#00F0B5] rounded-full"></span>
            <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <span>NPTEL IIT Lecture & Anna University R2023 Mapper</span>
              <span className="text-[10px] uppercase px-2 py-0.5 rounded bg-[#00693E]/50 text-[#00F0B5] border border-[#00F0B5]/30">
                Official MOOC
              </span>
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Madras Institute of Technology (MIT Campus) • Verified IIT Kharagpur, IIT Madras & IISc Video Timestamps
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative min-w-[220px] sm:w-72">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search concepts, professors, COs..."
            className="w-full px-3.5 py-2 rounded-xl bg-[#020813] border border-slate-800 focus:border-[#00F0B5]/60 text-xs text-slate-200 placeholder-slate-500 focus:outline-none"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 text-xs"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Module Filter Pills */}
      <div className="flex flex-wrap gap-1.5 p-1 rounded-2xl bg-[#020813] border border-slate-800 text-xs">
        <button
          onClick={() => setSelectedModule('ALL')}
          className={`px-3 py-1.5 rounded-xl transition-all ${
            selectedModule === 'ALL'
              ? 'bg-[#00693E] text-[#00F0B5] font-bold shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
          }`}
        >
          All Modules ({modules.length})
        </button>
        {modules.map((m) => (
          <button
            key={m.module_code}
            onClick={() => setSelectedModule(m.module_code)}
            className={`px-3 py-1.5 rounded-xl transition-all flex items-center gap-1.5 ${
              selectedModule === m.module_code
                ? 'bg-[#00693E] text-[#00F0B5] font-bold shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <span>{m.module_title ? (m.module_title.length > 22 ? m.module_title.substring(0, 20) + '...' : m.module_title) : `Unit ${m.curriculum_unit}`}</span>
            <span className="text-[10px] text-slate-400">Unit {m.curriculum_unit}</span>
          </button>
        ))}
      </div>

      {/* Module Cards Grid */}
      <div className="space-y-6">
        {filteredModules.length === 0 ? (
          <div className="p-8 text-center text-slate-500 border border-slate-800 rounded-2xl bg-[#020813]">
            No NPTEL lectures match the search criteria.
          </div>
        ) : (
          filteredModules.map((mod) => (
            <div
              key={mod.module_code}
              className="rounded-2xl border border-slate-800 hover:border-[#00F0B5]/40 bg-[#020813]/80 p-5 transition-all space-y-4"
            >
              {/* Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800/80">
                <div className="flex flex-wrap items-center gap-2.5">
                  <span className="px-2.5 py-1 rounded-lg bg-[#00693E]/40 text-[#00F0B5] border border-[#00F0B5]/30 text-xs font-bold">
                    Unit {mod.curriculum_unit}
                  </span>
                  <h3 className="font-bold text-slate-100 text-sm sm:text-base">
                    {mod.module_title}
                  </h3>
                  <span className="text-[11px] text-slate-400">
                    (Unit {mod.curriculum_unit} • {mod.credits} Credits)
                  </span>
                </div>

                {/* CO & PO Badges */}
                <div className="flex flex-wrap items-center gap-1.5">
                  {mod.mapped_cos.map((co) => (
                    <span key={co} className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold">
                      {co}
                    </span>
                  ))}
                  {mod.mapped_pos.map((po) => (
                    <span key={po} className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/30 text-[10px]">
                      {po}
                    </span>
                  ))}
                </div>
              </div>

              {/* Course Meta Info */}
              <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400 bg-[#041026]/70 p-3 rounded-xl border border-slate-800/60">
                <div className="flex items-center gap-2">
                  <span className="text-[#00F0B5] font-bold">NPTEL Course:</span>
                  <span className="text-slate-200">{mod.nptel_course.course_name}</span>
                  <span className="text-[11px] text-slate-500">({mod.nptel_course.course_id})</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-amber-400 font-semibold">{mod.nptel_course.instructor}</span>
                  <span>•</span>
                  <span>{mod.nptel_course.institution}</span>
                </div>
              </div>

              {/* Prerequisites */}
              {mod.prerequisites && mod.prerequisites.length > 0 && (
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <span className="text-slate-500 text-[11px]">Prerequisites:</span>
                  {mod.prerequisites.map((p, idx) => (
                    <span key={idx} className="text-[11px] text-slate-300 bg-[#041026] px-2 py-0.5 rounded border border-slate-800">
                      {p}
                    </span>
                  ))}
                </div>
              )}

              {/* Lectures List */}
              <div className="space-y-3 pt-1">
                <div className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Mapped Official Video Lectures & Timestamps:
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {mod.nptel_course.lectures.map((lec, idx) => {
                    const isFallback = lec.verification_status === 'PORTAL_FALLBACK' || !lec.youtube_url;
                    const targetUrl = isFallback 
                      ? (lec.portal_url || mod.nptel_course.portal_url || 'https://nptel.ac.in')
                      : `${lec.youtube_url}&t=${lec.timestamp_start_sec}s`;

                    return (
                      <div
                        key={idx}
                        className="rounded-xl border border-slate-800/80 bg-[#041026]/50 p-3.5 space-y-2.5 hover:border-slate-700 transition-all flex flex-col justify-between"
                      >
                        <div>
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-[11px] font-bold text-emerald-400">
                              Lecture {lec.lecture_number}
                            </span>
                            <div className="flex items-center gap-1.5">
                              {isFallback ? (
                                <span className="text-[9px] px-2 py-0.5 rounded bg-amber-950/40 text-amber-300 border border-amber-500/30 uppercase font-mono">
                                  Official Portal
                                </span>
                              ) : (
                                <span className="text-[9px] px-2 py-0.5 rounded bg-emerald-950/40 text-emerald-300 border border-emerald-500/30 uppercase font-mono">
                                  Stream Active
                                </span>
                              )}
                              <span className="text-[10px] px-2 py-0.5 rounded bg-[#020813] text-[#00F0B5] border border-[#00F0B5]/30">
                                {formatTimestamp(lec.timestamp_start_sec)} - {formatTimestamp(lec.timestamp_end_sec)}
                              </span>
                            </div>
                          </div>
                          <div className="font-semibold text-slate-100 text-xs mt-1 leading-snug">
                            {lec.lecture_title}
                          </div>
                          <ul className="mt-2 space-y-1">
                            {lec.key_concepts.map((c, cIdx) => (
                              <li key={cIdx} className="text-[11px] text-slate-400 flex items-start gap-1.5 leading-relaxed">
                                <span className="text-[#00F0B5] mt-0.5">•</span>
                                <span>{c}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between">
                          <span className="text-[10px] text-slate-500 font-mono">
                            {isFallback ? 'Verification: Official Portal' : `Video ID: ${lec.youtube_video_id}`}
                          </span>
                          <a
                            href={targetUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#00693E]/30 text-[#00F0B5] border border-[#00F0B5]/30 hover:bg-[#00F0B5] hover:text-[#020813] text-xs font-bold transition-all"
                          >
                            <span>{isFallback ? 'Open NPTEL Portal' : 'Open at Timestamp'}</span>
                            <span>↗</span>
                          </a>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

    </div>
  );
}

