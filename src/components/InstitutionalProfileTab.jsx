/**
 * ========================================================================================
 * VoltCore Apex Academia - Institutional Profile & Regulatory Isolation Engine
 * Isolated Architecture Tab: InstitutionalProfileTab.jsx
 * Hardware Target: HP Victus (LAPTOP-3NEGBVLE) - Strict Thermal & Zero-Polling Discipline
 * ========================================================================================
 * Encapsulates all localized university branding, student roll numbers, institutional
 * affiliations, and specific regulatory standards (Anna University, MIT Campus, Regulation 2023).
 *
 * DORMANT BY DEFAULT: Remains collapsed and non-intrusive unless explicitly expanded by the user.
 */

import React, { useState, useEffect } from "react";

// Local storage preference key for institutional overlay
const STORAGE_KEY_INST_OVERLAY = "voltcore_institutional_overlay_enabled";

export const INSTITUTIONAL_DATA = {
  institution: "Madras Institute of Technology (MIT Campus), Anna University",
  campus: "Chromepet, Chennai - 600 044, Tamil Nadu, India",
  department: "Department of Electronics Engineering",
  regulation: "Anna University Regulation 2023 (CBCS / OBE Tier-1)",
  governingBody: "Center for Academic Courses & Syndicate, Anna University",
  coe: "Office of the Controller of Examinations, Anna University",
  accreditation: "NBA Tier-1 (Washington Accord) • NAAC A++ (3.54 CGPA)",
  studentProfile: {
    name: "Ashok Kumar A",
    rollNumber: "2023MITEC042",
    rfidToken: "E2 80 6F 3B",
    degree: "Bachelor of Engineering (B.E. ECE)",
    batch: "2023 - 2027",
    admittedQuota: "Anna University Single Window Counseling"
  },
  labCenters: [
    { code: "LAB-302", name: "DSP & Computational Signal Simulation Center", head: "MIT Campus" },
    { code: "LAB-304", name: "Advanced Embedded Systems & Real-Time IoT Lab", head: "MIT Campus" },
    { code: "LAB-401", name: "Optics, Semiconductor & Laser Cavity Suite", head: "MIT Campus" }
  ],
  courseCodeMapping: [
    { code: "EC23S01", title: "Numerical and Signal Processing Practice Through Python", reg: "R2023 Sem 4", credits: 2 },
    { code: "EC23C03", title: "Electronic Devices & Semiconductor Physics", reg: "R2023 Sem 3", credits: 3 },
    { code: "EC23E04", title: "Optics and Laser Technology", reg: "R2023 Sem 5", credits: 3 },
    { code: "EC8702",  title: "Embedded Systems & Real-Time Operating Systems", reg: "R2023 Sem 7", credits: 3 }
  ]
};

export default function InstitutionalProfileTab({
  isEmbeddedInShell = false,
  onOverlayToggle = null
}) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [enableOverlayInReports, setEnableOverlayInReports] = useState(false);

  useEffect(() => {
    try {
      if (typeof window !== "undefined") {
        const saved = localStorage.getItem(STORAGE_KEY_INST_OVERLAY);
        if (saved !== null) {
          setEnableOverlayInReports(JSON.parse(saved));
        }
      }
    } catch (e) {
      // Passive fallback
    }
  }, []);

  const handleToggleOverlay = (val) => {
    setEnableOverlayInReports(val);
    try {
      localStorage.setItem(STORAGE_KEY_INST_OVERLAY, JSON.stringify(val));
    } catch (e) {}
    if (onOverlayToggle) onOverlayToggle(val);
  };

  return (
    <div className="rounded-2xl bg-[#041026] border border-slate-800 transition-all font-mono text-xs overflow-hidden shadow-xl">
      {/* ------------------------------------------------------------------- */}
      {/* 1. DORMANT ACCORDION TRIGGER HEADER                                 */}
      {/* ------------------------------------------------------------------- */}
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        className="p-4 sm:p-5 flex items-center justify-between cursor-pointer hover:bg-slate-900/60 transition-colors select-none group"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[#00693E]/30 border border-[#00F0B5]/30 flex items-center justify-center text-sm">
            🏛️
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-white text-sm group-hover:text-[#00F0B5] transition-colors">
                Institutional Profile &amp; Localized Regulatory Metadata
              </span>
              <span className="px-2 py-0.5 rounded-full bg-[#020813] border border-slate-700 text-[10px] text-slate-400">
                {isExpanded ? "Active View" : "Dormant"}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5 font-sans">
              Encapsulated university affiliation, roll numbers, and Anna University Regulation 2023 mappings.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            className="px-3 py-1.5 rounded-xl bg-slate-800 group-hover:bg-[#00693E]/40 text-[#00F0B5] font-bold text-xs transition-colors"
          >
            {isExpanded ? "Collapse ▲" : "Expand Details ▼"}
          </button>
        </div>
      </div>

      {/* ------------------------------------------------------------------- */}
      {/* 2. EXPANDED INSTITUTIONAL METADATA SUITE                           */}
      {/* ------------------------------------------------------------------- */}
      {isExpanded && (
        <div className="p-5 sm:p-6 border-t border-slate-800/80 bg-[#020813]/80 space-y-6">
          
          {/* Institutional Banner */}
          <div className="p-4 rounded-xl bg-[#041026] border border-emerald-500/20 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="text-base font-extrabold text-white">
                {INSTITUTIONAL_DATA.institution}
              </div>
              <div className="text-slate-400 text-xs">
                {INSTITUTIONAL_DATA.department} • {INSTITUTIONAL_DATA.campus}
              </div>
              <div className="text-[#00F0B5] text-[11px] pt-1">
                {INSTITUTIONAL_DATA.regulation} • {INSTITUTIONAL_DATA.accreditation}
              </div>
            </div>

            {/* Overlay Preference Toggle */}
            <div className="p-3 rounded-lg bg-[#020813] border border-slate-800 flex items-center gap-3 text-[11px] flex-shrink-0">
              <span className="text-slate-300">Include in Exported Reports:</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={enableOverlayInReports}
                  onChange={(e) => handleToggleOverlay(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-9 h-5 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#00F0B5]"></div>
              </label>
            </div>
          </div>

          {/* Student & Department Identity Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <div className="p-3.5 rounded-xl bg-[#041026] border border-slate-800">
              <div className="text-[10px] text-slate-500 uppercase">Student Name</div>
              <div className="text-white font-bold text-sm mt-0.5">{INSTITUTIONAL_DATA.studentProfile.name}</div>
              <div className="text-[10px] text-slate-400 mt-1">{INSTITUTIONAL_DATA.studentProfile.degree}</div>
            </div>

            <div className="p-3.5 rounded-xl bg-[#041026] border border-slate-800">
              <div className="text-[10px] text-slate-500 uppercase">Roll Number</div>
              <div className="text-[#00F0B5] font-bold text-sm mt-0.5">{INSTITUTIONAL_DATA.studentProfile.rollNumber}</div>
              <div className="text-[10px] text-slate-400 mt-1">Batch {INSTITUTIONAL_DATA.studentProfile.batch}</div>
            </div>

            <div className="p-3.5 rounded-xl bg-[#041026] border border-slate-800">
              <div className="text-[10px] text-slate-500 uppercase">RFID Badge UID</div>
              <div className="text-amber-300 font-bold text-sm mt-0.5">{INSTITUTIONAL_DATA.studentProfile.rfidToken}</div>
              <div className="text-[10px] text-emerald-400 mt-1">Hardware Sensor Linked</div>
            </div>

            <div className="p-3.5 rounded-xl bg-[#041026] border border-slate-800">
              <div className="text-[10px] text-slate-500 uppercase">Governing Body</div>
              <div className="text-cyan-400 font-bold text-xs mt-0.5">Anna University COE</div>
              <div className="text-[10px] text-slate-400 mt-1">Autonomous Syllabus</div>
            </div>
          </div>

          {/* Specialized Lab Centers Suite */}
          <div className="p-4 rounded-xl bg-[#041026] border border-slate-800 space-y-3">
            <div className="font-bold text-white text-xs flex items-center justify-between">
              <span>🔬 Institutional Laboratory Infrastructure:</span>
              <span className="text-[10px] text-slate-400">MIT Campus Facilities</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-[11px]">
              {INSTITUTIONAL_DATA.labCenters.map((lab) => (
                <div key={lab.code} className="p-2.5 rounded-lg bg-[#020813] border border-slate-850 flex items-center gap-2.5">
                  <span className="px-1.5 py-0.5 rounded bg-slate-800 text-[#00F0B5] font-bold text-[10px]">{lab.code}</span>
                  <div className="min-w-0">
                    <div className="text-slate-200 font-semibold truncate">{lab.name}</div>
                    <div className="text-[9px] text-slate-500">{lab.head}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Localized Course Code Mapping Table */}
          <div className="p-4 rounded-xl bg-[#041026] border border-slate-800 space-y-3">
            <div className="font-bold text-white text-xs">
              📚 Localized Anna University Regulation 2023 Course Registry:
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-[11px]">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="py-2 px-2">Discipline Category</th>
                    <th className="py-2 px-2">Course Title</th>
                    <th className="py-2 px-2">Regulation Alignment</th>
                    <th className="py-2 px-2">Credits</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-850">
                  {INSTITUTIONAL_DATA.courseCodeMapping.map((c) => (
                    <tr key={c.code} className="text-slate-300">
                      <td className="py-2 px-2 font-bold text-[#00F0B5]">Core Discipline</td>
                      <td className="py-2 px-2 text-white">{c.title}</td>
                      <td className="py-2 px-2 text-slate-400">{c.reg}</td>
                      <td className="py-2 px-2 text-emerald-400">{c.credits} Credits</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
