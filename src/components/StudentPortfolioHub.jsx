import React, { useState, useEffect } from 'react';

/**
 * VoltCore Apex Academia - Student Experience, Portfolio & Collaboration Hub
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 * ----------------------------------------------------------------------------------------
 * Italian Glassmorphism + German Precision Engineering Architecture
 */

// Initial Seed Portfolios
const INITIAL_PORTFOLIOS = [
  {
    project_id: "PRJ-MIT-001",
    student_id: "2023MITEC042",
    student_name: "Ashok Kumar A",
    title: "Dual-Core FreeRTOS Drone Flight Controller",
    description: "High-rate PID stabilization on STM32H7 with hardware DMA SPI telemetry to ground station. Verified via HIL Test Bench 304.",
    domain: "Embedded Firmware",
    tech_stack: ["STM32H7", "FreeRTOS", "DMA", "SPI", "MPU6050"],
    repo_url: "https://github.com/AshokKumar313/VoltCore-LMS-Portal",
    wokwi_url: "https://wokwi.com/projects/voltcore-flight-controller",
    hardware_hil_verified: true,
    status: "FEATURED",
    likes_count: 38,
    xp_reward: 200,
    created_at: "2026-11-01"
  },
  {
    project_id: "PRJ-MIT-002",
    student_id: "2023MITEC018",
    student_name: "Priya Swaminathan",
    title: "Edge AI Railway Track Micro-Crack Detector",
    description: "Quantized INT8 CNN model running on ESP32-S3 LittleFS partition with auto-upload to MQTT cloud.",
    domain: "IoT & TinyML",
    tech_stack: ["ESP32-S3", "TensorFlow Lite", "LittleFS", "MQTT"],
    repo_url: "https://github.com/AshokKumar313/railway-edge-detector",
    wokwi_url: "https://wokwi.com/projects/railway-crack-detector",
    hardware_hil_verified: true,
    status: "VERIFIED",
    likes_count: 27,
    xp_reward: 180,
    created_at: "2026-11-02"
  },
  {
    project_id: "PRJ-MIT-003",
    student_id: "2023MITEC055",
    student_name: "Karthik Ramanathan",
    title: "RV32I 5-Stage Pipelined RISC-V Core with Hazard Unit",
    description: "Synthesizable Verilog HDL implementing Harvard architecture with ALU data forwarding and branch hazard stalls.",
    domain: "VLSI & FPGA",
    tech_stack: ["Verilog", "RISC-V", "Xilinx Vivado", "ModelSim"],
    repo_url: "https://github.com/AshokKumar313/rv32i-pipelined-core",
    wokwi_url: "",
    hardware_hil_verified: false,
    status: "VERIFIED",
    likes_count: 21,
    xp_reward: 180,
    created_at: "2026-11-03"
  }
];

// Initial Seed Study Groups
const INITIAL_STUDY_GROUPS = [
  {
    group_id: "GRP-EC8702-01",
    group_name: "EC8702 Embedded RTOS Core Fellowship",
    subject_code: "EC8702",
    topic: "Priority Inversion, Semaphore Mutexes & FreeRTOS Heap_4 Analysis",
    leader_id: "2023MITEC042",
    leader_name: "Ashok Kumar A",
    schedule_slot: "Tue & Thu 17:30 - 19:00 IST",
    meeting_link: "https://meet.mitindia.edu/voltcore-rtos-sprint",
    max_members: 6,
    member_count: 4,
    members: ["2023MITEC042", "2023MITEC018", "2023MITEC055", "2023MITEC012"]
  },
  {
    group_id: "GRP-GATE-02",
    group_name: "GATE ECE 2024 Analog & Semiconductor Cohort",
    subject_code: "GATE-ECE",
    topic: "Small-Signal Hybrid-Pi BJT/MOSFET & Nyquist Stability Derivations",
    leader_id: "2023MITEC018",
    leader_name: "Priya Swaminathan",
    schedule_slot: "Sat & Sun 10:00 - 12:00 IST",
    meeting_link: "https://meet.mitindia.edu/gate-ece-analog-deepdive",
    max_members: 8,
    member_count: 3,
    members: ["2023MITEC018", "2023MITEC012", "2023MITEC061"]
  },
  {
    group_id: "GRP-WOKWI-03",
    group_name: "Wokwi & WebSerial Automated Firmware Cohort",
    subject_code: "EC8711",
    topic: "Hardware-in-the-Loop Loopback Testing & DMA Buffer Timing",
    leader_id: "2023MITEC055",
    leader_name: "Karthik Ramanathan",
    schedule_slot: "Wed 16:30 - 18:00 IST",
    meeting_link: "https://meet.mitindia.edu/wokwi-hil-cohort",
    max_members: 5,
    member_count: 2,
    members: ["2023MITEC055", "2023MITEC042"]
  }
];

// Initial Seed Leaderboard
const INITIAL_LEADERBOARD = [
  {
    rank: 1,
    student_id: "2023MITEC042",
    name: "Ashok Kumar A",
    roll_no: "2023MITEC042",
    xp: 4850,
    streak_days: 14,
    department: "Electronics Engineering",
    institution: "MIT Campus, Anna University",
    tier: "Silicon Grandmaster",
    badges: ["HIL Test Lead", "TinyML Deployer", "RTOS Kernel Master", "Silicon Architect"]
  },
  {
    rank: 2,
    student_id: "2023MITEC018",
    name: "Priya Swaminathan",
    roll_no: "2023MITEC018",
    xp: 3920,
    streak_days: 11,
    department: "Electronics Engineering",
    institution: "MIT Campus, Anna University",
    tier: "Firmware Architect",
    badges: ["Edge AI Specialist", "DMA Optimization"]
  },
  {
    rank: 3,
    student_id: "2023MITEC055",
    name: "Karthik Ramanathan",
    roll_no: "2023MITEC055",
    xp: 3410,
    streak_days: 8,
    department: "Electronics Engineering",
    institution: "MIT Campus, Anna University",
    tier: "Embedded Specialist",
    badges: ["RISC-V Verilog", "Wokwi Speedrunner"]
  },
  {
    rank: 4,
    student_id: "2023MITEC012",
    name: "Deepa Balasubramanian",
    roll_no: "2023MITEC012",
    xp: 2890,
    streak_days: 9,
    department: "Electronics Engineering",
    institution: "MIT Campus, Anna University",
    tier: "Embedded Specialist",
    badges: ["Analog Signal Integrity", "SPICE Solver"]
  },
  {
    rank: 5,
    student_id: "2023MITEC061",
    name: "Vigneshwaran K",
    roll_no: "2023MITEC061",
    xp: 2450,
    streak_days: 5,
    department: "Electronics Engineering",
    institution: "MIT Campus, Anna University",
    tier: "Circuit Novice",
    badges: ["I2C Bus Analyzer"]
  }
];

export default function StudentPortfolioHub() {
  const [activeTab, setActiveTab] = useState("portfolio"); // "portfolio" | "peer-reviews" | "study-groups" | "leaderboard"
  const [portfolios, setPortfolios] = useState(INITIAL_PORTFOLIOS);
  const [studyGroups, setStudyGroups] = useState(INITIAL_STUDY_GROUPS);
  const [leaderboard, setLeaderboard] = useState(INITIAL_LEADERBOARD);
  const [userXp, setUserXp] = useState(4850);
  const [toastMessage, setToastMessage] = useState(null);

  // Peer review form state
  const [selectedProjectForReview, setSelectedProjectForReview] = useState(INITIAL_PORTFOLIOS[1].project_id);
  const [rubricScores, setRubricScores] = useState({
    code_quality: 8.5,
    timing_safety: 8.0,
    memory_efficiency: 9.0,
    test_coverage: 7.5
  });
  const [reviewComments, setReviewComments] = useState("Outstanding quantized LittleFS implementation with robust buffer sanity checks.");

  // New Project Submission Form State
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [newProject, setNewProject] = useState({
    title: "",
    description: "",
    domain: "Embedded Firmware",
    tech_stack: "ESP32, FreeRTOS, MQTT",
    repo_url: "",
    wokwi_url: "",
    hardware_hil_verified: false
  });

  // Calculate rubric average
  const rubricAvg = (
    (rubricScores.code_quality + rubricScores.timing_safety + rubricScores.memory_efficiency + rubricScores.test_coverage) / 4
  ).toFixed(1);

  // Show toast utility
  const triggerToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Upvote / Like project
  const handleLike = (projectId) => {
    setPortfolios(prev =>
      prev.map(p => {
        if (p.project_id === projectId) {
          const updated = { ...p, likes_count: p.likes_count + 1 };
          return updated;
        }
        return p;
      })
    );
    setUserXp(prev => prev + 15);
    triggerToast("Project upvoted! +15 XP peer contribution bonus.");

    // Fire background REST sync silently
    fetch("/api/collaboration/portfolio/like", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projectId })
    }).catch(() => {});
  };

  // Submit peer review
  const handleReviewSubmit = (e) => {
    e.preventDefault();
    const passed = parseFloat(rubricAvg) >= 7.0;
    const decision = passed ? "APPROVED" : "CHANGES_REQUESTED";

    setUserXp(prev => prev + 150);
    triggerToast(
      `Peer review submitted with decision: ${decision} (Rubric ${rubricAvg}/10). +150 XP awarded!`
    );

    // Update target project status if approved
    if (passed) {
      setPortfolios(prev =>
        prev.map(p => p.project_id === selectedProjectForReview ? { ...p, status: "VERIFIED" } : p)
      );
    }
  };

  // Join Study Group
  const handleJoinGroup = (groupId) => {
    setStudyGroups(prev =>
      prev.map(g => {
        if (g.group_id === groupId && g.member_count < g.max_members) {
          return {
            ...g,
            member_count: g.member_count + 1,
            members: [...g.members, "2023MITEC042"]
          };
        }
        return g;
      })
    );
    setUserXp(prev => prev + 50);
    triggerToast("Joined study cohort successfully! +50 XP study sprint reward.");

    fetch("/api/collaboration/group/join", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        group_id: groupId,
        student_id: "2023MITEC042",
        student_name: "Ashok Kumar A"
      })
    }).catch(() => {});
  };

  // Handle New Project Submission
  const handleProjectSubmit = (e) => {
    e.preventDefault();
    if (!newProject.title.trim() || !newProject.description.trim()) {
      alert("Please provide both a project title and description.");
      return;
    }

    const createdProj = {
      project_id: `PRJ-MIT-${Math.floor(100 + Math.random() * 900)}`,
      student_id: "2023MITEC042",
      student_name: "Ashok Kumar A",
      title: newProject.title,
      description: newProject.description,
      domain: newProject.domain,
      tech_stack: newProject.tech_stack.split(",").map(s => s.trim()),
      repo_url: newProject.repo_url || "https://github.com/AshokKumar313",
      wokwi_url: newProject.wokwi_url,
      hardware_hil_verified: newProject.hardware_hil_verified,
      status: "SUBMITTED",
      likes_count: 1,
      xp_reward: 200,
      created_at: new Date().toISOString().split("T")[0]
    };

    setPortfolios([createdProj, ...portfolios]);
    setUserXp(prev => prev + 200);
    setShowSubmitModal(false);
    setNewProject({
      title: "",
      description: "",
      domain: "Embedded Firmware",
      tech_stack: "ESP32, FreeRTOS, MQTT",
      repo_url: "",
      wokwi_url: "",
      hardware_hil_verified: false
    });
    triggerToast("Project submitted to peer review queue! +200 XP portfolio reward.");
  };

  return (
    <div className="space-y-6">
      
      {/* Toast Notification HUD */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 p-4 rounded-2xl bg-[#041026] border border-[#00F0B5]/50 text-white text-xs font-mono shadow-2xl flex items-center gap-3 animate-bounce">
          <span className="text-[#00F0B5] text-lg">⚡</span>
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Top Banner KPI Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Student Lead XP</span>
            <span className="text-[#00F0B5] font-bold">Rank #1</span>
          </div>
          <div className="text-2xl font-black text-white mt-1">
            {userXp.toLocaleString()} <span className="text-xs text-[#00F0B5] font-normal">XP</span>
          </div>
          <div className="text-[10px] text-emerald-400 mt-1">Tier: Silicon Grandmaster (Lvl 18)</div>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Active Portfolios</span>
            <span className="text-emerald-400 font-bold">{portfolios.length} Live</span>
          </div>
          <div className="text-2xl font-black text-white mt-1">
            {portfolios.filter(p => p.hardware_hil_verified).length} <span className="text-xs text-slate-400 font-normal">HIL Verified</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-1">MIT Lab 304 Certified Hardware</div>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Study Pods</span>
            <span className="text-amber-400 font-bold">{studyGroups.length} Active</span>
          </div>
          <div className="text-2xl font-black text-white mt-1">
            {studyGroups.reduce((acc, g) => acc + g.member_count, 0)} <span className="text-xs text-slate-400 font-normal">Students</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-1">Embedded Systems &amp; GATE ECE Sprints</div>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Peer Review Rate</span>
            <span className="text-cyan-400 font-bold">100% SLA</span>
          </div>
          <div className="text-2xl font-black text-white mt-1">
            &lt; 24h <span className="text-xs text-slate-400 font-normal">Turnaround</span>
          </div>
          <div className="text-[10px] text-cyan-400 mt-1">4-Criterion Rigorous Rubric</div>
        </div>
      </div>

      {/* Main Tab Navigation HUD */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-2 rounded-2xl bg-[#041026] border border-[#00F0B5]/20">
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setActiveTab("portfolio")}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all ${
              activeTab === "portfolio"
                ? "bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] shadow-emerald-glow"
                : "text-slate-300 hover:text-white hover:bg-[#020813]"
            }`}
          >
            🚀 Engineering Portfolios ({portfolios.length})
          </button>
          
          <button
            type="button"
            onClick={() => setActiveTab("peer-reviews")}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all ${
              activeTab === "peer-reviews"
                ? "bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] shadow-emerald-glow"
                : "text-slate-300 hover:text-white hover:bg-[#020813]"
            }`}
          >
            🔬 Peer Code Reviews (+150 XP)
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("study-groups")}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all ${
              activeTab === "study-groups"
                ? "bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] shadow-emerald-glow"
                : "text-slate-300 hover:text-white hover:bg-[#020813]"
            }`}
          >
            👥 Study Groups & Pods ({studyGroups.length})
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("leaderboard")}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all ${
              activeTab === "leaderboard"
                ? "bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] shadow-emerald-glow"
                : "text-slate-300 hover:text-white hover:bg-[#020813]"
            }`}
          >
            🏆 Silicon Leaderboard
          </button>
        </div>

        {activeTab === "portfolio" && (
          <button
            type="button"
            onClick={() => setShowSubmitModal(true)}
            className="px-4 py-2 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-[#00F0B5] border border-[#00F0B5]/40 text-xs font-mono font-bold transition-all flex items-center gap-2"
          >
            <span>+</span>
            <span>Submit Project (+200 XP)</span>
          </button>
        )}
      </div>

      {/* Tab 1: Engineering Portfolios */}
      {activeTab === "portfolio" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {portfolios.map((proj) => (
            <div
              key={proj.project_id}
              className="p-5 rounded-2xl bg-[#041026]/90 border border-slate-800 hover:border-[#00F0B5]/40 transition-all shadow-xl flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#020813] text-[#00F0B5] border border-[#00F0B5]/30">
                    {proj.domain}
                  </span>
                  <div className="flex items-center gap-1.5">
                    {proj.hardware_hil_verified && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/30">
                        ⚡ Lab 304 HIL
                      </span>
                    )}
                    <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                      proj.status === "FEATURED"
                        ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                        : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                    }`}>
                      {proj.status}
                    </span>
                  </div>
                </div>

                <h3 className="text-base font-bold text-white tracking-tight mb-1.5">
                  {proj.title}
                </h3>
                <div className="text-xs text-slate-400 mb-3">
                  Lead: <span className="text-slate-200 font-semibold">{proj.student_name}</span> ({proj.student_id})
                </div>

                <p className="text-xs text-slate-300 leading-relaxed mb-4">
                  {proj.description}
                </p>

                {/* Tech Stack Pills */}
                <div className="flex flex-wrap gap-1.5 mb-4">
                  {proj.tech_stack.map((t, idx) => (
                    <span
                      key={idx}
                      className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#020813] text-slate-300 border border-slate-700"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>

              {/* Bottom Actions */}
              <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => handleLike(proj.project_id)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#020813] hover:bg-slate-900 border border-slate-700 hover:border-[#00F0B5]/50 text-xs text-slate-200 transition-all"
                  >
                    <span className="text-red-400">❤️</span>
                    <span className="font-mono font-bold">{proj.likes_count}</span>
                  </button>

                  {proj.wokwi_url && (
                    <a
                      href={proj.wokwi_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-2.5 py-1.5 rounded-xl bg-[#020813] border border-cyan-500/30 text-cyan-400 text-xs font-mono hover:bg-cyan-950/40 transition-colors"
                      title="Open in Wokwi Simulator"
                    >
                      Wokwi
                    </a>
                  )}

                  {proj.repo_url && (
                    <a
                      href={proj.repo_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-2.5 py-1.5 rounded-xl bg-[#020813] border border-slate-700 text-slate-300 text-xs font-mono hover:text-[#00F0B5] transition-colors"
                    >
                      GitHub
                    </a>
                  )}
                </div>

                <span className="text-[11px] font-mono text-[#00F0B5] font-semibold">
                  +{proj.xp_reward} XP
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 2: Peer Code Reviews */}
      {activeTab === "peer-reviews" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left: Rubric Evaluation Form */}
          <div className="lg:col-span-2 p-6 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30 shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
              <div>
                <h3 className="text-lg font-bold text-white">Engineering Code Review Rubric</h3>
                <p className="text-xs text-slate-400">Strict MIT Campus ECE Evaluation Standards (Regulation 2023)</p>
              </div>
              <div className="text-right">
                <div className="text-xs text-slate-400">Calculated Score</div>
                <div className={`text-2xl font-black font-mono ${parseFloat(rubricAvg) >= 7.0 ? 'text-[#00F0B5]' : 'text-amber-400'}`}>
                  {rubricAvg} <span className="text-xs text-slate-400 font-normal">/ 10.0</span>
                </div>
              </div>
            </div>

            <form onSubmit={handleReviewSubmit} className="space-y-5">
              
              <div>
                <label className="block text-xs font-mono text-slate-300 mb-1.5">
                  Select Project for Peer Review:
                </label>
                <select
                  value={selectedProjectForReview}
                  onChange={(e) => setSelectedProjectForReview(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#020813] border border-slate-700 text-slate-200 text-xs font-mono focus:outline-none focus:border-[#00F0B5]"
                >
                  {portfolios.map(p => (
                    <option key={p.project_id} value={p.project_id}>
                      {p.title} — {p.student_name} ({p.domain})
                    </option>
                  ))}
                </select>
              </div>

              {/* Criterion 1: Code Quality & Modularity */}
              <div>
                <div className="flex justify-between text-xs font-mono text-slate-300 mb-1">
                  <span>1. Code Quality & MISRA C Compliance:</span>
                  <span className="text-[#00F0B5] font-bold">{rubricScores.code_quality} / 10</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  step="0.5"
                  value={rubricScores.code_quality}
                  onChange={(e) => setRubricScores({ ...rubricScores, code_quality: parseFloat(e.target.value) })}
                  className="w-full accent-[#00F0B5] bg-slate-800"
                />
              </div>

              {/* Criterion 2: Timing Safety & Non-blocking Design */}
              <div>
                <div className="flex justify-between text-xs font-mono text-slate-300 mb-1">
                  <span>2. Timing Safety & Non-Blocking Loops:</span>
                  <span className="text-[#00F0B5] font-bold">{rubricScores.timing_safety} / 10</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  step="0.5"
                  value={rubricScores.timing_safety}
                  onChange={(e) => setRubricScores({ ...rubricScores, timing_safety: parseFloat(e.target.value) })}
                  className="w-full accent-[#00F0B5] bg-slate-800"
                />
              </div>

              {/* Criterion 3: Memory & DMA Efficiency */}
              <div>
                <div className="flex justify-between text-xs font-mono text-slate-300 mb-1">
                  <span>3. SRAM & DMA Zero-Copy Memory Footprint:</span>
                  <span className="text-[#00F0B5] font-bold">{rubricScores.memory_efficiency} / 10</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  step="0.5"
                  value={rubricScores.memory_efficiency}
                  onChange={(e) => setRubricScores({ ...rubricScores, memory_efficiency: parseFloat(e.target.value) })}
                  className="w-full accent-[#00F0B5] bg-slate-800"
                />
              </div>

              {/* Criterion 4: Test Coverage & HIL Readiness */}
              <div>
                <div className="flex justify-between text-xs font-mono text-slate-300 mb-1">
                  <span>4. Test Bench Coverage & Hardware Assertion:</span>
                  <span className="text-[#00F0B5] font-bold">{rubricScores.test_coverage} / 10</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  step="0.5"
                  value={rubricScores.test_coverage}
                  onChange={(e) => setRubricScores({ ...rubricScores, test_coverage: parseFloat(e.target.value) })}
                  className="w-full accent-[#00F0B5] bg-slate-800"
                />
              </div>

              {/* Technical Feedback */}
              <div>
                <label className="block text-xs font-mono text-slate-300 mb-1.5">
                  Detailed Technical Critique & Suggestions:
                </label>
                <textarea
                  rows="3"
                  value={reviewComments}
                  onChange={(e) => setReviewComments(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#020813] border border-slate-700 text-slate-200 text-xs font-mono focus:outline-none focus:border-[#00F0B5]"
                  placeholder="Note register optimizations, critical sections, or edge cases..."
                ></textarea>
              </div>

              <div className="pt-2 flex items-center justify-between">
                <span className="text-xs text-slate-400 font-mono">
                  Passing threshold: &gt;= 7.0 / 10.0
                </span>
                <button
                  type="submit"
                  className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] font-mono font-bold text-xs hover:shadow-emerald-glow transition-all"
                >
                  Submit Peer Review (+150 XP)
                </button>
              </div>

            </form>
          </div>

          {/* Right: Review Guidelines & Standards Card */}
          <div className="p-6 rounded-2xl bg-[#041026]/90 border border-slate-800 space-y-4">
            <h4 className="text-sm font-bold text-white font-mono flex items-center gap-2">
              <span className="text-[#00F0B5]">📋</span>
              <span>Code Review Protocol</span>
            </h4>
            <div className="space-y-3 text-xs text-slate-300 leading-relaxed font-mono">
              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <strong className="text-emerald-400 block mb-1">Zero Infinite Busy-Waits</strong>
                Always verify that while loops polling hardware flags (e.g. SPI RXNE, I2C BTF) feature timeout counters to prevent CPU hangs.
              </div>
              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <strong className="text-cyan-400 block mb-1">Volatile Qualifier Sanity</strong>
                Global variables modified in Interrupt Service Routines (ISRs) must be marked `volatile`.
              </div>
              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <strong className="text-amber-400 block mb-1">Atomic Lock Bounds</strong>
                FreeRTOS `taskENTER_CRITICAL()` regions must be bounded to microsecond durations to avoid interrupt latency jitter.
              </div>
            </div>
          </div>

        </div>
      )}

      {/* Tab 3: Study Groups & Pods */}
      {activeTab === "study-groups" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {studyGroups.map((g) => {
            const isFull = g.member_count >= g.max_members;
            const isMember = g.members.includes("2023MITEC042");

            return (
              <div
                key={g.group_id}
                className="p-5 rounded-2xl bg-[#041026]/90 border border-slate-800 hover:border-[#00F0B5]/40 transition-all shadow-xl flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#020813] text-[#00F0B5] border border-[#00F0B5]/30">
                      {g.subject_code}
                    </span>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                      isFull
                        ? "bg-red-500/20 text-red-400 border border-red-500/30"
                        : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                    }`}>
                      {g.member_count} / {g.max_members} Members
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-white tracking-tight mb-1.5">
                    {g.group_name}
                  </h3>
                  <div className="text-xs text-slate-400 mb-3">
                    Organized by: <span className="text-slate-200 font-semibold">{g.leader_name}</span>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed mb-4">
                    {g.topic}
                  </p>

                  <div className="p-3 rounded-xl bg-[#020813] border border-slate-800 text-xs font-mono space-y-1 mb-4">
                    <div className="text-slate-400">
                      🗓️ Schedule: <span className="text-emerald-400">{g.schedule_slot}</span>
                    </div>
                  </div>
                </div>

                {/* Join / Active Member Action */}
                <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                  <a
                    href={g.meeting_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs font-mono text-cyan-400 hover:underline flex items-center gap-1"
                  >
                    <span>🔗 Study Room</span>
                  </a>

                  {isMember ? (
                    <span className="px-3 py-1.5 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-bold">
                      ✓ Enrolled
                    </span>
                  ) : (
                    <button
                      type="button"
                      disabled={isFull}
                      onClick={() => handleJoinGroup(g.group_id)}
                      className={`px-4 py-1.5 rounded-xl text-xs font-mono font-bold transition-all ${
                        isFull
                          ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                          : "bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] hover:shadow-emerald-glow"
                      }`}
                    >
                      {isFull ? "Cohort Full" : "Join Pod (+50 XP)"}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Tab 4: Silicon Leaderboard */}
      {activeTab === "leaderboard" && (
        <div className="p-6 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30 shadow-2xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800 mb-6">
            <div>
              <h3 className="text-lg font-bold text-white tracking-tight">Academic Silicon Leaderboard</h3>
              <p className="text-xs text-slate-400">
                Department of Electronics Engineering • Anna University MIT Campus
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 bg-[#020813] px-3 py-1.5 rounded-xl border border-emerald-500/30">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Updated Live via SQLite WAL</span>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider">
                  <th className="py-3 px-3">Rank</th>
                  <th className="py-3 px-4">Student Candidate</th>
                  <th className="py-3 px-3">Roll No</th>
                  <th className="py-3 px-3">Streak</th>
                  <th className="py-3 px-4">Rank Tier</th>
                  <th className="py-3 px-4">Specialization Badges</th>
                  <th className="py-3 px-3 text-right">Total XP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {leaderboard.map((item) => (
                  <tr
                    key={item.student_id}
                    className={`hover:bg-[#020813]/60 transition-colors ${
                      item.roll_no === "2023MITEC042" ? "bg-[#00693E]/15 border-l-2 border-l-[#00F0B5]" : ""
                    }`}
                  >
                    <td className="py-3.5 px-3 font-bold">
                      {item.rank === 1 && <span className="text-amber-400">🥇 1st</span>}
                      {item.rank === 2 && <span className="text-slate-300">🥈 2nd</span>}
                      {item.rank === 3 && <span className="text-amber-600">🥉 3rd</span>}
                      {item.rank > 3 && <span className="text-slate-500">#{item.rank}</span>}
                    </td>

                    <td className="py-3.5 px-4 font-bold text-white flex items-center gap-2">
                      <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-[#00693E] to-[#00F0B5] p-[1.5px] flex-shrink-0">
                        <div className="w-full h-full bg-[#020813] rounded-[6px] flex items-center justify-center font-bold text-[10px] text-[#00F0B5]">
                          {item.name.split(" ").map(n => n[0]).join("")}
                        </div>
                      </div>
                      <span>{item.name}</span>
                      {item.roll_no === "2023MITEC042" && (
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#00693E] text-[#00F0B5] font-bold">
                          YOU
                        </span>
                      )}
                    </td>

                    <td className="py-3.5 px-3 text-slate-300">{item.roll_no}</td>

                    <td className="py-3.5 px-3 text-amber-400 font-bold">
                      🔥 {item.streak_days}d
                    </td>

                    <td className="py-3.5 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        item.tier === "Silicon Grandmaster"
                          ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                          : item.tier === "Firmware Architect"
                          ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40"
                          : "bg-slate-800 text-slate-300 border-slate-700"
                      }`}>
                        {item.tier}
                      </span>
                    </td>

                    <td className="py-3.5 px-4">
                      <div className="flex flex-wrap gap-1">
                        {item.badges.slice(0, 2).map((b, idx) => (
                          <span key={idx} className="text-[9px] px-1.5 py-0.5 rounded bg-[#020813] text-slate-300 border border-slate-800">
                            {b}
                          </span>
                        ))}
                      </div>
                    </td>

                    <td className="py-3.5 px-3 text-right font-black text-[#00F0B5] text-sm">
                      {item.xp.toLocaleString()} <span className="text-[10px] text-slate-400 font-normal">XP</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Modal: Submit New Project */}
      {showSubmitModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#020813]/80 backdrop-blur-md">
          <div className="max-w-xl w-full p-6 rounded-3xl bg-[#041026] border border-[#00F0B5]/40 shadow-2xl font-mono text-xs">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <h3 className="text-base font-bold text-white">Submit Engineering Portfolio Project</h3>
              <button
                type="button"
                onClick={() => setShowSubmitModal(false)}
                className="text-slate-400 hover:text-white text-base"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleProjectSubmit} className="space-y-4">
              <div>
                <label className="block text-slate-300 mb-1">Project Title:</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. FreeRTOS CAN-Bus Telemetry Node"
                  value={newProject.title}
                  onChange={(e) => setNewProject({ ...newProject, title: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-[#020813] border border-slate-700 text-slate-200 focus:outline-none focus:border-[#00F0B5]"
                />
              </div>

              <div>
                <label className="block text-slate-300 mb-1">Domain:</label>
                <select
                  value={newProject.domain}
                  onChange={(e) => setNewProject({ ...newProject, domain: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-[#020813] border border-slate-700 text-slate-200 focus:outline-none focus:border-[#00F0B5]"
                >
                  <option value="Embedded Firmware">Embedded Firmware</option>
                  <option value="IoT & TinyML">IoT & TinyML</option>
                  <option value="VLSI & FPGA">VLSI & FPGA</option>
                  <option value="Analog Signal Integrity">Analog Signal Integrity</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-300 mb-1">Tech Stack (comma-separated):</label>
                <input
                  type="text"
                  placeholder="STM32, FreeRTOS, DMA, SPI"
                  value={newProject.tech_stack}
                  onChange={(e) => setNewProject({ ...newProject, tech_stack: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-[#020813] border border-slate-700 text-slate-200 focus:outline-none focus:border-[#00F0B5]"
                />
              </div>

              <div>
                <label className="block text-slate-300 mb-1">Technical Architecture Summary:</label>
                <textarea
                  rows="3"
                  required
                  placeholder="Explain hardware modules, register configurations, and timing requirements..."
                  value={newProject.description}
                  onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-[#020813] border border-slate-700 text-slate-200 focus:outline-none focus:border-[#00F0B5]"
                ></textarea>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 mb-1">GitHub Repo URL:</label>
                  <input
                    type="url"
                    placeholder="https://github.com/..."
                    value={newProject.repo_url}
                    onChange={(e) => setNewProject({ ...newProject, repo_url: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-[#020813] border border-slate-700 text-slate-200 focus:outline-none focus:border-[#00F0B5]"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 mb-1">Wokwi Simulator URL (Optional):</label>
                  <input
                    type="url"
                    placeholder="https://wokwi.com/..."
                    value={newProject.wokwi_url}
                    onChange={(e) => setNewProject({ ...newProject, wokwi_url: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-[#020813] border border-slate-700 text-slate-200 focus:outline-none focus:border-[#00F0B5]"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="hil_check"
                  checked={newProject.hardware_hil_verified}
                  onChange={(e) => setNewProject({ ...newProject, hardware_hil_verified: e.target.checked })}
                  className="accent-[#00F0B5]"
                />
                <label htmlFor="hil_check" className="text-slate-300 cursor-pointer">
                  Hardware-in-the-Loop (HIL) Bench Verified in Lab 304
                </label>
              </div>

              <div className="pt-3 border-t border-slate-800 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowSubmitModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] font-bold hover:shadow-emerald-glow"
                >
                  Confirm & Submit (+200 XP)
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}

