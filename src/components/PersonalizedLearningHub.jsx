import React, { useState } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Phase A: Personalized Learning Hub (Features 201–202)
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 * 
 * Features:
 *   - Feature 201: Personalized Learning Dashboard (Domain mastery, cognitive gaps, study velocity)
 *   - Feature 202: Adaptive Learning Path Generator (Prerequisite DAG, career goals, diagnostic quiz)
 * ========================================================================================
 */

// Initial student profile
const INITIAL_STUDENT = {
  name: "Ashok Kumar A",
  rollNo: "2023MITEC042",
  department: "Department of Electronics Engineering",
  campus: "Madras Institute of Technology (MIT) Campus, Anna University",
  streak: 14,
  xp: 4950,
  level: "Silicon Grandmaster (Level 18)",
  weeklyGoalHours: 12.5,
  completedHours: 9.2,
  targetCareer: "embedded_firmware_architect"
};

// 5 Core ECE Domains
const INITIAL_DOMAINS = [
  {
    id: "embedded_rtos",
    name: "Embedded Systems & FreeRTOS",
    code: "EC8702",
    mastery: 88.0,
    status: "Advanced",
    color: "#00F0B5",
    topics: ["ARM Cortex-M4 NVIC", "FreeRTOS Priority Inversion", "DMA Zero-Copy"]
  },
  {
    id: "digital_vlsi",
    name: "Digital VLSI & FPGA Synthesis",
    code: "EC3451",
    mastery: 76.5,
    status: "Proficient",
    color: "#38BDF8",
    topics: ["Quine-McCluskey K-Map", "Verilog HDL FSMs", "FPGA LUT-6 Timing"]
  },
  {
    id: "analog_rf",
    name: "Analog Integrated Circuits & Signals",
    code: "EC3452",
    mastery: 71.0,
    status: "Needs Review",
    color: "#F97316",
    topics: ["Op-Amp 741 Miller Pole-Splitting", "Differential Pair CMRR", "Sallen-Key Bode"]
  },
  {
    id: "tinyml_edge",
    name: "TinyML & Edge AI Intelligence",
    code: "EC3712",
    mastery: 82.5,
    status: "Proficient",
    color: "#D946EF",
    topics: ["INT8 Quantization", "Depthwise Convolutions", "Tensor Arena SRAM"]
  },
  {
    id: "iot_bus",
    name: "IoT Telemetry & Peripheral Protocols",
    code: "EC3552",
    mastery: 91.0,
    status: "Advanced",
    color: "#10B981",
    topics: ["SPI Mode 0-3 Waveforms", "I2C 7-Bit Address ACK", "WebSerial HIL Bridge"]
  }
];

// Career Tracks Definition
const CAREER_TRACKS = {
  embedded_firmware_architect: {
    title: "Tier-1 Embedded Firmware Architect",
    companies: "Qualcomm, Texas Instruments, Intel, Apple",
    milestones: [
      { id: "m1", title: "ARM Cortex-M4 Fundamentals & Memory Map", domain: "Embedded RTOS", diff: "Intermediate", req: 75, status: "Completed" },
      { id: "m2", title: "FreeRTOS Priority Inversion & Mutex Protocol", domain: "Embedded RTOS", diff: "Advanced", req: 80, status: "Completed" },
      { id: "m3", title: "Scatter-Gather DMA & Zero-Copy Circular Buffers", domain: "Embedded RTOS", diff: "Hardcore", req: 85, status: "Recommended Next" },
      { id: "m4", title: "SPI/I2C/UART Peripheral Bus Driver Synthesis", domain: "IoT & Buses", diff: "Advanced", req: 80, status: "Locked (Prerequisite Required)" }
    ]
  },
  gate_ece_top_ranker: {
    title: "GATE ECE Top 100 Ranker",
    companies: "IISc Bangalore, IIT Madras, BARC, ISRO",
    milestones: [
      { id: "g1", title: "Network Theorems & RLC Transients", domain: "Analog & RF", diff: "Intermediate", req: 70, status: "Completed" },
      { id: "g2", title: "Small-Signal BJT & Op-Amp Frequency Response", domain: "Analog & RF", diff: "Advanced", req: 80, status: "Recommended Next" },
      { id: "g3", title: "Sequential Logic FSM & Setup/Hold Times", domain: "Digital VLSI", diff: "Advanced", req: 80, status: "Locked (Prerequisite Required)" },
      { id: "g4", title: "Nyquist Stability & Control System State Space", domain: "Analog & RF", diff: "Hardcore", req: 85, status: "Locked (Prerequisite Required)" }
    ]
  },
  edge_ai_silicon_engineer: {
    title: "Edge AI & Silicon Systems Engineer",
    companies: "NVIDIA, Edge Impulse, Bosch, STMicroelectronics",
    milestones: [
      { id: "a1", title: "INT8 Quantization & MAC Operations", domain: "TinyML Edge", diff: "Intermediate", req: 75, status: "Completed" },
      { id: "a2", title: "Microcontroller Tensor Arena SRAM Budgeting", domain: "TinyML Edge", diff: "Advanced", req: 80, status: "Completed" },
      { id: "a3", title: "ESP32-S3 Keyword Spotting Firmware", domain: "TinyML Edge", diff: "Hardcore", req: 85, status: "Recommended Next" },
      { id: "a4", title: "WebSerial HIL Telemetry & Anomaly Sentinel", domain: "IoT & Buses", diff: "Advanced", req: 80, status: "Locked (Prerequisite Required)" }
    ]
  }
};

// Diagnostic Quiz Questions
const QUIZ_QUESTIONS = [
  {
    id: 1,
    domain: "analog_rf",
    question: "In a two-stage CMOS op-amp, connecting a Miller compensation capacitor Cc across the second stage causes:",
    options: [
      "Both poles to shift to higher frequencies simultaneously",
      "Pole-splitting: dominant pole shifts lower, non-dominant pole shifts higher",
      "Phase margin to degrade below 30 degrees",
      "Common-mode rejection ratio to drop to zero"
    ],
    correctIndex: 1,
    explanation: "Miller compensation splits poles: dominant pole p1' = 1 / (gm2 * R1 * R2 * Cc) drops lower, while non-dominant pole p2' = gm2 / C2 shifts higher, ensuring stability (>60° phase margin)."
  },
  {
    id: 2,
    domain: "embedded_rtos",
    question: "Which mechanism resolves unbounded priority inversion when a high-priority task contends for a shared mutex held by a low-priority task?",
    options: [
      "Round-Robin time slicing without preemption",
      "Priority Inheritance Protocol (elevating low-priority task)",
      "Disabling all interrupts globally indefinitely",
      "Software polling in an infinite while loop"
    ],
    correctIndex: 1,
    explanation: "Priority Inheritance Protocol temporarily elevates the mutex-holding low-priority task to the priority of the highest blocked task, preventing medium-priority tasks from preempting."
  },
  {
    id: 3,
    domain: "tinyml_edge",
    question: "When quantizing a floating-point tensor to INT8 symmetric format (range [-128, 127]), the scale factor S is given by:",
    options: [
      "S = (max(val) - min(val)) / 255.0",
      "S = max(|min|, |max|) / 127.0 with zero_point = 0",
      "S = 1.0 / sqrt(MAC_count)",
      "S = total_sram_bytes / 1024"
    ],
    correctIndex: 1,
    explanation: "In symmetric INT8 quantization, zero_point is strictly 0 and scale S = max(|val_min|, |val_max|) / 127.0, simplifying MCU hardware matrix multiplication."
  }
];

export default function PersonalizedLearningHub() {
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard' | 'adaptive_path' | 'quiz'
  const [student, setStudent] = useState(INITIAL_STUDENT);
  const [domains, setDomains] = useState(INITIAL_DOMAINS);
  const [selectedCareer, setSelectedCareer] = useState('embedded_firmware_architect');
  
  // Quiz Simulator State
  const [currentQuizIndex, setCurrentQuizIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [quizScore, setQuizScore] = useState(0);

  const activeCareerInfo = CAREER_TRACKS[selectedCareer];

  // Handle Career Change
  const handleCareerChange = (careerKey) => {
    setSelectedCareer(careerKey);
    setStudent(prev => ({ ...prev, targetCareer: careerKey }));
  };

  // Handle Quiz Submission
  const handleAnswerSelect = (qId, optionIdx) => {
    if (quizSubmitted) return;
    setSelectedAnswers(prev => ({ ...prev, [qId]: optionIdx }));
  };

  const submitQuiz = () => {
    let score = 0;
    QUIZ_QUESTIONS.forEach(q => {
      if (selectedAnswers[q.id] === q.correctIndex) {
        score += 1;
      }
    });

    setQuizScore(score);
    setQuizSubmitted(true);

    // Adaptively update domain mastery
    if (score >= 2) {
      setDomains(prev => prev.map(d => {
        if (d.id === "analog_rf") return { ...d, mastery: Math.min(100, d.mastery + 8.5), status: "Proficient" };
        if (d.id === "embedded_rtos") return { ...d, mastery: Math.min(100, d.mastery + 3.0), status: "Advanced" };
        return d;
      }));
      setStudent(prev => ({ ...prev, xp: prev.xp + 150 }));
    }
  };

  const resetQuiz = () => {
    setSelectedAnswers({});
    setQuizSubmitted(false);
    setQuizScore(0);
    setCurrentQuizIndex(0);
  };

  // Export Learning Profile to CSV
  const handleExportCSV = () => {
    let csv = "Domain Code,Domain Name,Mastery Percentage,Competency Status\n";
    domains.forEach(d => {
      csv += `${d.code},"${d.name}",${d.mastery}%,${d.status}\n`;
    });
    csv += `\nStudent,${student.name} (${student.rollNo})\n`;
    csv += `Target Career,"${activeCareerInfo.title}"\n`;
    csv += `Study Streak,${student.streak} Days\n`;
    csv += `Total XP,${student.xp}\n`;

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `VoltCore_Learning_Profile_${student.rollNo}.csv`;
    a.click();
  };

  return (
    <div className="w-full flex flex-col gap-6 font-mono text-xs">
      
      {/* Top Banner Navigation & Summary HUD */}
      <div 
        className="glass-card rounded-2xl p-4 sm:p-5 border flex flex-wrap items-center justify-between gap-4 shadow-xl"
        style={{ borderColor: 'var(--theme-border)' }}
      >
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 p-0.5 flex items-center justify-center text-xl shadow-lg">
            🎓
          </div>
          <div>
            <div className="font-bold text-white text-sm sm:text-base flex items-center gap-2">
              <span>{student.name}</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                {student.rollNo}
              </span>
            </div>
            <div className="text-[11px] text-slate-400">
              {student.department} • {student.level}
            </div>
          </div>
        </div>

        {/* Global Quick Stats */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="px-3 py-1.5 rounded-xl bg-slate-900/80 border border-amber-500/30 text-amber-300 flex items-center gap-1.5">
            <span>🔥</span>
            <span className="font-bold">{student.streak} Days</span>
            <span className="text-[10px] text-slate-400">Streak</span>
          </div>

          <div className="px-3 py-1.5 rounded-xl bg-slate-900/80 border border-cyan-500/30 text-cyan-300 flex items-center gap-1.5">
            <span>⚡</span>
            <span className="font-bold">{student.xp} XP</span>
          </div>

          <div className="px-3 py-1.5 rounded-xl bg-slate-900/80 border border-emerald-500/30 text-emerald-300 flex items-center gap-1.5">
            <span>⏱️</span>
            <span className="font-bold">{student.completedHours}h / {student.weeklyGoalHours}h</span>
          </div>

          <button
            type="button"
            onClick={handleExportCSV}
            className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 font-bold transition-all flex items-center gap-1.5"
            title="Export Learning Progress to CSV"
          >
            <span>📥</span>
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Main Tab Controller */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          type="button"
          onClick={() => setActiveTab('dashboard')}
          className={`px-4 py-2 rounded-xl transition-all font-bold flex items-center gap-2 ${
            activeTab === 'dashboard'
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <span>📊</span>
          <span>Feature 201: Learning Dashboard</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('adaptive_path')}
          className={`px-4 py-2 rounded-xl transition-all font-bold flex items-center gap-2 ${
            activeTab === 'adaptive_path'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <span>🧭</span>
          <span>Feature 202: Adaptive Learning Path</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('quiz')}
          className={`px-4 py-2 rounded-xl transition-all font-bold flex items-center gap-2 ${
            activeTab === 'quiz'
              ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <span>⚡</span>
          <span>Adaptive Diagnostic Quiz</span>
        </button>
      </div>

      {/* TAB 1: FEATURE 201 — PERSONALIZED LEARNING DASHBOARD */}
      {activeTab === 'dashboard' && (
        <div className="space-y-6 animate-in fade-in duration-200">
          
          {/* Urgent Revision Alert & Cognitive Gaps */}
          <div className="glass-card-accent rounded-2xl p-5 border border-amber-500/30 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <span className="text-2xl mt-0.5">⚠️</span>
              <div>
                <div className="font-bold text-white text-sm flex items-center gap-2">
                  <span>Urgent Revision Alert: Analog Integrated Circuits (EC3452)</span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-500/20 text-red-300 border border-red-500/40 font-bold">
                    High Urgency
                  </span>
                </div>
                <p className="text-slate-300 text-xs mt-1 leading-relaxed">
                  Cognitive gap detected in <strong>Op-Amp 741 Miller Frequency Compensation & Pole-Splitting</strong>. Current domain mastery is <strong>71.0%</strong> (below the 80% competency threshold for CAT-1).
                </p>
                <div className="text-[11px] text-amber-300/90 mt-1">
                  💡 Recommendation: Review dominant pole shift formula \(p_1' = \frac&#123;1&#125;&#123;g_&#123;m2&#125; R_1 R_2 C_c&#125;\) before the upcoming assessment.
                </div>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setActiveTab('quiz')}
              className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold transition-all shadow-md flex-shrink-0"
            >
              Take Diagnostic Drill →
            </button>
          </div>

          {/* 5 ECE Domain Mastery Cards */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-white text-sm flex items-center gap-2">
                <span>Anna University R2023 Domain Mastery Radar</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                  5 Core Areas
                </span>
              </h3>
              <span className="text-[11px] text-emerald-400">
                Overall Average: {(domains.reduce((a, b) => a + b.mastery, 0) / domains.length).toFixed(1)}%
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {domains.map((domain) => (
                <div 
                  key={domain.id}
                  className="glass-card rounded-2xl p-4 border flex flex-col justify-between hover:border-slate-600 transition-all shadow-md"
                  style={{ borderColor: 'var(--theme-border)' }}
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-bold">
                        {domain.code}
                      </span>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                        domain.status === 'Advanced'
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          : domain.status === 'Proficient'
                          ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                          : 'bg-red-500/20 text-red-300 border border-red-500/30'
                      }`}>
                        {domain.status}
                      </span>
                    </div>

                    <h4 className="font-bold text-white text-xs mb-1">
                      {domain.name}
                    </h4>

                    {/* Mastery Bar */}
                    <div className="my-3 space-y-1">
                      <div className="flex justify-between text-[11px]">
                        <span className="text-slate-400">Mastery Level:</span>
                        <span className="font-bold text-white">{domain.mastery.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div 
                          className="h-full rounded-full transition-all duration-500"
                          style={{ 
                            width: `${domain.mastery}%`,
                            backgroundColor: domain.color 
                          }}
                        />
                      </div>
                    </div>

                    {/* Key Topics List */}
                    <div className="space-y-1 text-[10px] text-slate-300/80 pt-2 border-t border-slate-800/80">
                      <div className="text-slate-400 font-semibold mb-0.5">Syllabus Highlights:</div>
                      {domain.topics.map((t, idx) => (
                        <div key={idx} className="truncate flex items-center gap-1.5">
                          <span className="w-1 h-1 rounded-full bg-slate-500"></span>
                          <span className="truncate">{t}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <a 
                    href="/workspace"
                    className="mt-4 w-full py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-200 hover:text-white text-center font-bold transition-all block"
                  >
                    Open in Studio →
                  </a>
                </div>
              ))}
            </div>
          </div>

          {/* Weekly Learning Velocity & Hours Tracker */}
          <div className="glass-card rounded-2xl p-5 border" style={{ borderColor: 'var(--theme-border)' }}>
            <div className="flex flex-wrap items-center justify-between gap-4 mb-3">
              <div>
                <h4 className="font-bold text-white text-sm">Weekly Study Velocity & Time Investment</h4>
                <p className="text-slate-400 text-xs mt-0.5">
                  Target: {student.weeklyGoalHours} hrs/week • Completed: {student.completedHours} hrs ({((student.completedHours / student.weeklyGoalHours) * 100).toFixed(0)}%)
                </p>
              </div>
              <div className="text-right">
                <span className="text-emerald-400 font-bold text-base">2.8 hrs/day</span>
                <div className="text-[10px] text-slate-400">Average Velocity</div>
              </div>
            </div>

            <div className="w-full bg-slate-800 h-3 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-full"
                style={{ width: `${(student.completedHours / student.weeklyGoalHours) * 100}%` }}
              />
            </div>
          </div>

        </div>
      )}

      {/* TAB 2: FEATURE 202 — ADAPTIVE LEARNING PATH GENERATOR */}
      {activeTab === 'adaptive_path' && (
        <div className="space-y-6 animate-in fade-in duration-200">
          
          {/* Career Track Objective Selector */}
          <div className="glass-card rounded-2xl p-5 border" style={{ borderColor: 'var(--theme-border)' }}>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
              <div>
                <h3 className="font-bold text-white text-sm flex items-center gap-2">
                  <span>Target Career Track & Academic Objective</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-bold">
                    Adaptive DAG
                  </span>
                </h3>
                <p className="text-slate-400 text-xs mt-0.5">
                  Select your primary destination to adapt prerequisites, milestone roadmap, and diagnostic quizzes.
                </p>
              </div>

              {/* Career Dropdown Selector */}
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Active Track:</span>
                <select
                  value={selectedCareer}
                  onChange={(e) => handleCareerChange(e.target.value)}
                  className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-white font-bold text-xs focus:outline-none focus:border-cyan-400 cursor-pointer"
                >
                  <option value="embedded_firmware_architect">Tier-1 Embedded Firmware Architect</option>
                  <option value="gate_ece_top_ranker">GATE ECE Top 100 Ranker</option>
                  <option value="edge_ai_silicon_engineer">Edge AI & Silicon Systems Engineer</option>
                </select>
              </div>
            </div>

            {/* Career Details Pill */}
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs space-y-1">
              <div className="text-slate-300">
                Target Objective: <strong className="text-cyan-300">{activeCareerInfo.title}</strong>
              </div>
              <div className="text-slate-400 text-[11px]">
                Target Benchmark Recruiters / Institutions: <span className="text-slate-200">{activeCareerInfo.companies}</span>
              </div>
            </div>
          </div>

          {/* Sequential Milestone Roadmap */}
          <div className="space-y-3">
            <h4 className="font-bold text-white text-sm flex items-center gap-2">
              <span>Adaptive Milestone Path & Prerequisite Dependencies</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                {activeCareerInfo.milestones.length} Steps
              </span>
            </h4>

            <div className="space-y-3">
              {activeCareerInfo.milestones.map((milestone, idx) => {
                const isRecommended = milestone.status === 'Recommended Next';
                const isCompleted = milestone.status === 'Completed';
                return (
                  <div 
                    key={milestone.id}
                    className={`p-4 rounded-2xl border transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 ${
                      isRecommended
                        ? 'bg-gradient-to-r from-cyan-950/40 via-emerald-950/30 to-slate-900/60 border-cyan-400 ring-2 ring-cyan-400/20 shadow-lg'
                        : isCompleted
                        ? 'bg-slate-900/40 border-emerald-500/30'
                        : 'bg-slate-900/20 border-slate-800 text-slate-500'
                    }`}
                  >
                    <div className="flex items-start gap-3.5">
                      <div className={`w-8 h-8 rounded-xl flex items-center justify-center font-bold text-xs ${
                        isCompleted
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                          : isRecommended
                          ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400 animate-pulse'
                          : 'bg-slate-800 text-slate-500'
                      }`}>
                        {idx + 1}
                      </div>

                      <div>
                        <div className="flex items-center gap-2">
                          <h5 className={`font-bold text-xs ${isRecommended ? 'text-white' : isCompleted ? 'text-slate-200' : 'text-slate-400'}`}>
                            {milestone.title}
                          </h5>
                          <span className={`text-[9px] px-1.5 py-0.2 rounded font-bold ${
                            milestone.diff === 'Hardcore'
                              ? 'bg-red-500/20 text-red-300'
                              : milestone.diff === 'Advanced'
                              ? 'bg-amber-500/20 text-amber-300'
                              : 'bg-blue-500/20 text-blue-300'
                          }`}>
                            {milestone.diff}
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5">
                          Domain: <span className="text-slate-300">{milestone.domain}</span> • Required Mastery: <span className="text-cyan-400 font-bold">{milestone.req}%</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className={`text-[10px] px-2.5 py-1 rounded-full font-bold flex items-center gap-1 ${
                        isCompleted
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          : isRecommended
                          ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400'
                          : 'bg-slate-800 text-slate-400 border border-slate-700'
                      }`}>
                        {isCompleted && "✓ "}
                        {isRecommended && "⚡ "}
                        {milestone.status}
                      </span>

                      {isRecommended && (
                        <a
                          href="/workspace"
                          className="px-3 py-1 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold transition-all shadow-md"
                        >
                          Start Module →
                        </a>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

        </div>
      )}

      {/* TAB 3: ADAPTIVE DIAGNOSTIC QUIZ SIMULATOR */}
      {activeTab === 'quiz' && (
        <div className="glass-card rounded-2xl p-6 border space-y-6 animate-in fade-in duration-200" style={{ borderColor: 'var(--theme-border)' }}>
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <h3 className="font-bold text-white text-base flex items-center gap-2">
                <span>Adaptive Diagnostic Technical Quiz</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 font-bold border border-purple-500/30">
                  Anna University Standard
                </span>
              </h3>
              <p className="text-slate-400 text-xs mt-0.5">
                Answer technical diagnostic questions to update your domain mastery and recalculate recommended milestones.
              </p>
            </div>

            {quizSubmitted && (
              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-300">
                  Result: <strong className={quizScore >= 2 ? "text-emerald-400" : "text-amber-400"}>{quizScore} / {QUIZ_QUESTIONS.length} Correct</strong>
                </span>
                <button
                  type="button"
                  onClick={resetQuiz}
                  className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition-all"
                >
                  Retake Quiz
                </button>
              </div>
            )}
          </div>

          {/* Quiz Question Cards */}
          <div className="space-y-6">
            {QUIZ_QUESTIONS.map((q, idx) => {
              const selectedOpt = selectedAnswers[q.id];
              const isCorrect = selectedOpt === q.correctIndex;
              return (
                <div key={q.id} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span className="font-bold text-white">Question {idx + 1} of {QUIZ_QUESTIONS.length}</span>
                    <span className="uppercase text-[10px] px-2 py-0.5 rounded bg-slate-800 text-cyan-300">{q.domain}</span>
                  </div>

                  <p className="text-white text-xs leading-relaxed font-semibold">
                    {q.question}
                  </p>

                  {/* Options */}
                  <div className="space-y-2">
                    {q.options.map((opt, optIdx) => {
                      const isOptionSelected = selectedOpt === optIdx;
                      let btnStyle = "border-slate-800 bg-slate-900/80 text-slate-300 hover:bg-slate-800";
                      
                      if (quizSubmitted) {
                        if (optIdx === q.correctIndex) {
                          btnStyle = "border-emerald-400 bg-emerald-500/20 text-emerald-300 font-bold";
                        } else if (isOptionSelected) {
                          btnStyle = "border-red-400 bg-red-500/20 text-red-300";
                        }
                      } else if (isOptionSelected) {
                        btnStyle = "border-cyan-400 bg-cyan-500/20 text-cyan-300 font-bold";
                      }

                      return (
                        <button
                          key={optIdx}
                          type="button"
                          onClick={() => handleAnswerSelect(q.id, optIdx)}
                          className={`w-full text-left p-2.5 rounded-xl border text-xs transition-all flex items-center justify-between ${btnStyle}`}
                        >
                          <span>{String.fromCharCode(65 + optIdx)}. {opt}</span>
                          {quizSubmitted && optIdx === q.correctIndex && (
                            <span className="text-emerald-400 font-bold">✓ Correct</span>
                          )}
                        </button>
                      );
                    })}
                  </div>

                  {/* Technical Explanation after submission */}
                  {quizSubmitted && (
                    <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-[11px] text-slate-300 mt-2">
                      <strong className="text-cyan-400">Technical Derivation & Rubric:</strong>
                      <p className="mt-1 text-slate-300/90 leading-relaxed">{q.explanation}</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Submit Action */}
          {!quizSubmitted && (
            <div className="pt-2 flex justify-end">
              <button
                type="button"
                onClick={submitQuiz}
                disabled={Object.keys(selectedAnswers).length === 0}
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-slate-950 font-bold text-xs transition-all shadow-lg disabled:opacity-50"
              >
                Submit Diagnostic Quiz & Recalculate Mastery →
              </button>
            </div>
          )}

        </div>
      )}

    </div>
  );
}
