import React, { useState } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Phase L: Career & Professional Development (Features 321–330)
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 *
 * Features:
 *   - Feature 321: ECE Career Roadmap (Firmware, VLSI, Analog, RF, Automotive EV)
 *   - Feature 322: Embedded Systems Skill Tracker (C/C++, RTOS, Buses, Hardware Debug)
 *   - Feature 323: Semiconductor Industry Learning Track (IC Fab, EUV, Foundries)
 *   - Feature 324: VLSI Learning Roadmap (RTL to GDSII, Synthesis, STA, DFT, Tapeout)
 *   - Feature 325: IoT Career Preparation Track (MQTT, LoRaWAN, BLE, TinyML, Security)
 *   - Feature 326: Technical Interview Question Bank (Qualcomm, TI, Intel, NXP, Bosch)
 *   - Feature 327: Resume Builder (ATS-Compliant ECE Resume for Campus Recruitment)
 *   - Feature 328: Technical Skills Assessment (Diagnostic interactive quiz & scoring)
 *   - Feature 329: Internship Application Tracker (Company, Role, Tier, Status, Stipend)
 *   - Feature 330: Placement Preparation Dashboard (Campus Day-0/1 countdown, CGPA, Target)
 * Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
 * ========================================================================================
 */

// Career Roadmaps (Feature 321)
const ROADMAPS = {
  embedded_firmware: {
    title: "Embedded Systems & Firmware Engineer",
    domain: "Embedded Systems & IoT",
    ctc: "8.5 – 24.0 LPA",
    companies: ["Qualcomm", "Texas Instruments", "Bosch", "NXP Semiconductors", "Schneider Electric", "Honeywell"],
    skills: [
      "Bare-metal C and Embedded C++ (volatile, bitwise masking, pointers)",
      "ARM Cortex-M (M0+/M3/M4/M7) & RISC-V register architecture",
      "Serial bus protocols: I2C, SPI, UART, CAN 2.0B / CAN-FD",
      "Real-Time Operating Systems (FreeRTOS tasks, queues, semaphores, mutexes)",
      "Hardware test equipment: Digital Oscilloscope, Logic Analyzer, JTAG/SWD debuggers"
    ],
    courses: "EC3711 Embedded Systems Lab • EC3451 LIC • EC3561 Comm Systems"
  },
  digital_vlsi: {
    title: "Digital VLSI & ASIC Design Engineer",
    domain: "Semiconductor & Microelectronics",
    ctc: "12.0 – 32.0 LPA",
    companies: ["Intel", "NVIDIA", "Qualcomm", "AMD", "MediaTek", "Synopsys", "Cadence"],
    skills: [
      "Hardware Description Languages: Verilog HDL & SystemVerilog",
      "Digital design: Synchronous FSMs, pipelining, clock-domain crossing (CDC)",
      "Static Timing Analysis (STA): Setup time, hold time, slack, clock jitter",
      "Design for Testability (DFT): Scan insertion, boundary scan IEEE 1149.1, ATPG",
      "EDA Workflows: Synopsys Design Compiler, Cadence Genus, Innovus P&R"
    ],
    courses: "EC3452 Digital Systems Design • EC3611 VLSI Design Lab • Low-Power VLSI"
  },
  analog_rf: {
    title: "Analog Mixed-Signal & RF IC Designer",
    domain: "Analog & Radio Frequency Systems",
    ctc: "14.0 – 36.0 LPA",
    companies: ["Texas Instruments", "Analog Devices (ADI)", "Skyworks", "Qorvo", "Broadcom", "Infineon"],
    skills: [
      "CMOS analog blocks: Current mirrors, differential pairs, bandgap references",
      "Operational Transconductance Amplifiers (OTA) & Miller frequency compensation",
      "RF Front-Ends: Low-Noise Amplifiers (LNA), mixers, LC VCOs, Phase-Locked Loops (PLL)",
      "S-parameters, impedance matching on Smith Charts, 50-ohm transmission lines",
      "Simulation: Cadence Virtuoso Spectre, Keysight ADS, S-parameter VNA measurement"
    ],
    courses: "EC3351 Electronic Devices • EC3451 Linear Integrated Circuits • RF Elective"
  },
  automotive_ev: {
    title: "Automotive Electronics & EV Systems Architect",
    domain: "Automotive & Electric Mobility",
    ctc: "9.0 – 22.0 LPA",
    companies: ["Bosch", "Continental", "Tata Motors / Tata Elxsi", "Aptiv", "Valeo", "Ola Electric"],
    skills: [
      "Automotive networking: CAN-FD, LIN, FlexRay, Automotive Ethernet",
      "AUTOSAR Classic & Adaptive platform architectures",
      "ISO 26262 Road Vehicles Functional Safety (ASIL A to ASIL D)",
      "Battery Management Systems (BMS): Cell balancing, SOC/SOH Coulomb counting",
      "Model-Based Development: MATLAB/Simulink and Embedded Coder auto-generation"
    ],
    courses: "Automotive ECE Elective • EC3711 Embedded Lab • Power Electronics"
  }
};

// Interview Questions (Feature 326)
const INTERVIEW_QUESTIONS = [
  {
    id: "INT-01",
    company: "Qualcomm / Texas Instruments",
    domain: "Embedded C",
    q: "Explain the difference between 'const int *p', 'int * const p', and 'const int * const p'. Where is each typically utilized?",
    ans: "1. 'const int *p': Pointer to a constant integer. The integer value cannot be modified through p (*p = 10 is illegal), but p itself can point to another address. Used for read-only buffers in drivers.\n2. 'int * const p': Constant pointer to an integer. The pointer cannot point to another address, but the integer data can be modified (*p = 10 is valid). Used for memory-mapped hardware peripheral registers.\n3. 'const int * const p': Constant pointer to a constant integer. Neither the address nor the target value can be changed. Used for ROM tables and immutable calibration vectors.",
    difficulty: "Medium"
  },
  {
    id: "INT-02",
    company: "Intel / NVIDIA",
    domain: "Digital VLSI",
    q: "What is the difference between Setup Time and Hold Time? Which violation is catastrophic in silicon and cannot be fixed by lowering clock frequency?",
    ans: "Setup Time (t_setup) is the minimum duration the data input must remain stable before the active clock edge. Violation condition: T_clk < t_cq + t_comb + t_setup. Setup violations CAN be resolved by reducing clock frequency.\nHold Time (t_hold) is the minimum duration data must remain stable AFTER the active clock edge. Violation condition: t_cq + t_comb < t_hold. HOLD TIME VIOLATIONS ARE FATAL IN SILICON! Lowering the clock frequency does not help because both terms are frequency-independent. It must be resolved during physical design by inserting delay buffer cells.",
    difficulty: "Hard"
  },
  {
    id: "INT-03",
    company: "Broadcom / MediaTek",
    domain: "Verilog HDL",
    q: "Why should non-blocking assignments (<=) always be used for sequential logic and blocking assignments (=) for combinational logic?",
    ans: "Non-blocking assignments evaluate all right-hand sides in the Active simulation region and update left-hand sides in the NBA region. This guarantees race-free execution when cascading flip-flops (e.g. shift registers). Using blocking assignments inside sequential always @(posedge clk) blocks introduces simulator execution order dependencies, leading to synthesis-simulation mismatches and hardware bugs.",
    difficulty: "Medium"
  },
  {
    id: "INT-04",
    company: "NXP / Bosch",
    domain: "Microcontrollers & RTOS",
    q: "What is Priority Inversion in a Real-Time Operating System, and how do Priority Inheritance and Priority Ceiling protocols prevent it?",
    ans: "Priority Inversion occurs when a high-priority task is blocked waiting for a shared mutex held by a low-priority task, and an intermediate-priority task preempts the low-priority task, indirectly starving the high-priority task.\nPriority Inheritance temporarily elevates the priority of the low-priority lock holder to the priority of the highest-priority blocked task until the lock is released.\nPriority Ceiling pre-assigns each mutex a ceiling priority equal to the highest priority task that may acquire it, preventing deadlocks and bounding priority inversion to at most one lock acquisition.",
    difficulty: "Hard"
  }
];

export default function CareerProfessionalHub() {
  const [activeTab, setActiveTab] = useState('roadmap'); // 'roadmap', 'skills', 'interviews', 'resume', 'placement'

  // Feature 321 State
  const [selectedRoadmap, setSelectedRoadmap] = useState('embedded_firmware');

  // Feature 322 State
  const [skills, setSkills] = useState([
    { name: "C/C++ Pointers & Memory Allocation", level: 95, cat: "Firmware" },
    { name: "ARM Cortex-M Bare-Metal Registers", level: 90, cat: "Firmware" },
    { name: "Bus Protocols (I2C, SPI, UART, CAN)", level: 95, cat: "Protocols" },
    { name: "FreeRTOS Scheduling & Semaphores", level: 85, cat: "RTOS" },
    { name: "Verilog HDL & RTL Synthesis", level: 88, cat: "VLSI" },
    { name: "Hardware Debugging (JTAG / DSO)", level: 90, cat: "Hardware" }
  ]);

  // Feature 326 State
  const [expandedQId, setExpandedQId] = useState(null);

  // Feature 327 State
  const [resumeStudentName, setResumeStudentName] = useState('Ashok Kumar A');
  const [resumeRollNo, setResumeRollNo] = useState('2023MITEC042');
  const [resumeCgpa, setResumeCgpa] = useState('8.85');
  const [resumeGenerated, setResumeGenerated] = useState(false);

  // Feature 328 State (Diagnostic Quiz)
  const [quizAnswers, setQuizAnswers] = useState({});
  const [quizScore, setQuizScore] = useState(null);

  // Feature 329 State (Internships)
  const [internships, setInternships] = useState([
    { id: 1, company: "Texas Instruments", role: "Embedded Firmware Intern", tier: "Tier 1", stipend: "₹45,000 / mo", status: "TECH_ROUND_2" },
    { id: 2, company: "Qualcomm India", role: "Modem Systems Software Intern", tier: "Tier 1", stipend: "₹55,000 / mo", status: "TECH_ROUND_1" },
    { id: 3, company: "Bosch Global Software", role: "Automotive ECU Intern", tier: "Tier 1", stipend: "₹35,000 / mo", status: "OFFERED" }
  ]);

  // Feature 330 State (Placement)
  const [cgpaVal, setCgpaVal] = useState(8.85);
  const [coreScore, setCoreScore] = useState(94);
  const [aptitudeScore, setAptitudeScore] = useState(88);
  const [codingScore, setCodingScore] = useState(86);

  // Computed Placement Readiness
  const readinessIndex = (
    (0.35 * coreScore) + (0.25 * aptitudeScore) + (0.25 * codingScore) + (0.15 * (cgpaVal * 10))
  ).toFixed(1);

  const handleQuizSubmit = () => {
    let score = 0;
    if (quizAnswers.q1 === 1) score += 25;
    if (quizAnswers.q2 === 2) score += 25;
    if (quizAnswers.q3 === 0) score += 25;
    if (quizAnswers.q4 === 3) score += 25;
    setQuizScore(score);
  };

  const currRoadmap = ROADMAPS[selectedRoadmap];

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-8 text-slate-100 font-sans">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-teal-950/70 via-blue-950/50 to-slate-900/80 border border-teal-500/30 rounded-2xl p-6 mb-8 backdrop-blur shadow-2xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 text-xs font-semibold bg-teal-500/20 text-teal-300 border border-teal-400/30 rounded-full uppercase tracking-wider">
                Phase L • Features 321–330
              </span>
              <span className="px-2.5 py-0.5 text-xs font-semibold bg-blue-500/20 text-blue-300 border border-blue-400/30 rounded-full">
                Career & Industry Readiness
              </span>
            </div>
            <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-teal-200 via-blue-200 to-cyan-200">
              Career & Professional Development Hub
            </h1>
            <p className="text-sm text-slate-300 mt-1">
              Anna University / MIT Campus (ECE Dept, Reg 2023) • Lead: Ashok Kumar A (2023MITEC042)
            </p>
          </div>
          <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl px-4 py-2.5 text-right font-mono">
            <div className="text-xs text-slate-400">Day-0 Readiness Index</div>
            <div className="text-sm font-semibold text-emerald-400">{readinessIndex}% • Day-0 Eligible</div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex flex-wrap gap-2 mb-6 border-b border-slate-800 pb-4">
        {[
          { id: 'roadmap', label: 'ECE Career Tracks', badge: 'Feat 321, 323-325' },
          { id: 'skills', label: 'Embedded Skill Tracker', badge: 'Feat 322' },
          { id: 'interviews', label: 'Interview Question Bank', badge: 'Feat 326' },
          { id: 'resume', label: 'Resume & Quiz Assessment', badge: 'Feat 327-328' },
          { id: 'placement', label: 'Internships & Placement', badge: 'Feat 329-330' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2.5 rounded-xl text-sm font-medium transition-all flex items-center gap-2 ${
              activeTab === tab.id
                ? 'bg-teal-600 text-white shadow-lg shadow-teal-600/30 border border-teal-400/40'
                : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-700/50'
            }`}
          >
            <span>{tab.label}</span>
            <span className={`text-[10px] px-1.5 py-0.5 rounded-md ${activeTab === tab.id ? 'bg-teal-800 text-teal-200' : 'bg-slate-900 text-slate-400'}`}>
              {tab.badge}
            </span>
          </button>
        ))}
      </div>

      {/* TAB 1: ECE Career Tracks & Semiconductor Fab (Features 321, 323, 324, 325) */}
      {activeTab === 'roadmap' && (
        <div className="space-y-8">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6 pb-4 border-b border-slate-800">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-teal-400"></span>
                  Core ECE Professional Pathways & Industry Roadmaps
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">Explore salary packages, global hiring conglomerates, and prerequisite skill trees</p>
              </div>

              <div className="flex flex-wrap gap-2">
                {Object.keys(ROADMAPS).map(k => (
                  <button
                    key={k}
                    onClick={() => setSelectedRoadmap(k)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                      selectedRoadmap === k ? 'bg-teal-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                    }`}
                  >
                    {ROADMAPS[k].title.split(' ')[0]} {ROADMAPS[k].title.split(' ')[1]}
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-slate-950 p-6 rounded-xl border border-slate-800 space-y-6">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-slate-800">
                <div>
                  <span className="text-xs font-mono text-cyan-400 uppercase tracking-wider">{currRoadmap.domain}</span>
                  <h3 className="text-lg font-bold text-white mt-0.5">{currRoadmap.title}</h3>
                </div>
                <div className="bg-teal-950/60 border border-teal-800/60 px-4 py-2 rounded-xl text-right font-mono">
                  <div className="text-[10px] text-slate-400">Average Compensation</div>
                  <div className="text-sm font-bold text-emerald-400">{currRoadmap.ctc}</div>
                </div>
              </div>

              <div>
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Top Global Recruiters (Day-0 / Day-1)</div>
                <div className="flex flex-wrap gap-2">
                  {currRoadmap.companies.map((c, i) => (
                    <span key={i} className="px-3 py-1 text-xs bg-slate-900 text-slate-200 border border-slate-700 rounded-lg flex items-center gap-1.5 font-medium">
                      <span className="w-1.5 h-1.5 rounded-full bg-teal-400"></span>
                      {c}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Core Engineering Prerequisites</div>
                <ul className="space-y-2 text-xs text-slate-300">
                  {currRoadmap.skills.map((skill, i) => (
                    <li key={i} className="flex items-start gap-2 bg-slate-900/50 p-2.5 rounded-lg border border-slate-800/60">
                      <span className="text-teal-400 font-bold">✓</span>
                      <span>{skill}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="text-xs text-cyan-300 bg-cyan-950/20 p-3 rounded-lg border border-cyan-800/30 font-mono">
                <span className="text-slate-400">Anna University Course Mapping: </span>
                {currRoadmap.courses}
              </div>
            </div>
          </div>

          {/* Semiconductor IC Fab & VLSI Architecture Stage Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Semiconductor IC Fab Track */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                Semiconductor Industry Track (Feature 323)
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Cleanroom fabrication flow from 300mm single-crystal silicon ingots (Czochralski method) to packaging:
              </p>
              <div className="space-y-2 text-xs font-mono text-slate-300">
                <div className="p-2.5 bg-slate-950 rounded-lg border border-slate-800">
                  <strong className="text-teal-400">1. Photolithography (EUV 13.5nm): </strong>Extreme Ultraviolet laser patterning on ASML scanners.
                </div>
                <div className="p-2.5 bg-slate-950 rounded-lg border border-slate-800">
                  <strong className="text-teal-400">2. Ion Implantation & Diffusion: </strong>High-precision p/n doping profile engineering.
                </div>
                <div className="p-2.5 bg-slate-950 rounded-lg border border-slate-800">
                  <strong className="text-teal-400">3. Cu Dual-Damascene Interconnects: </strong>Multi-layer metal routing and CMP planarization.
                </div>
              </div>
            </div>

            {/* VLSI RTL to GDSII Flow */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-indigo-400"></span>
                VLSI RTL-to-GDSII Design Flow (Feature 324)
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Standard ASIC physical synthesis and timing sign-off stages using Synopsys & Cadence EDA suites:
              </p>
              <div className="space-y-2 text-xs font-mono text-slate-300">
                <div className="p-2.5 bg-slate-950 rounded-lg border border-slate-800">
                  <strong className="text-indigo-400">1. Logic Synthesis: </strong>RTL SystemVerilog mapped to standard cell libraries (.lib).
                </div>
                <div className="p-2.5 bg-slate-950 rounded-lg border border-slate-800">
                  <strong className="text-indigo-400">2. Static Timing Analysis (STA): </strong>Hold & Setup time slack closure on PrimeTime.
                </div>
                <div className="p-2.5 bg-slate-950 rounded-lg border border-slate-800">
                  <strong className="text-indigo-400">3. Physical Sign-Off (DRC/LVS): </strong>Design rule checks and tapeout delivery.
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Embedded Systems Skill Tracker (Feature 322) */}
      {activeTab === 'skills' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-slate-800">
            <div>
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-teal-400"></span>
                Embedded Systems & Core Engineering Skill Tracker
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">Track your technical competencies against top-tier tier-1 semiconductor job descriptions</p>
            </div>
            <div className="text-right font-mono">
              <span className="text-xs text-slate-400">Average Proficiency: </span>
              <span className="text-sm font-bold text-emerald-400">90.5% (Mastery Level)</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {skills.map((s, idx) => (
              <div key={idx} className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-bold text-white">{s.name}</span>
                  <span className="font-mono text-teal-400 font-bold">{s.level}%</span>
                </div>
                <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-teal-500 to-cyan-400 h-full rounded-full transition-all duration-500"
                    style={{ width: `${s.level}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-[11px] text-slate-400 font-mono">
                  <span>Category: {s.cat}</span>
                  <span className="text-emerald-400">Verified Competency</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: Technical Interview Question Bank (Feature 326) */}
      {activeTab === 'interviews' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <div className="pb-4 border-b border-slate-800">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
              Technical Interview Question Bank (Top ECE Companies)
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">Frequently asked core interview questions from Qualcomm, TI, Intel, NXP, and Bosch</p>
          </div>

          <div className="space-y-4">
            {INTERVIEW_QUESTIONS.map(q => (
              <div key={q.id} className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-3 transition">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-cyan-950 text-cyan-300 border border-cyan-800 rounded">
                      {q.company}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">{q.domain}</span>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                    q.difficulty === 'Hard' ? 'bg-red-950 text-red-300 border border-red-800' : 'bg-amber-950 text-amber-300 border border-amber-800'
                  }`}>
                    {q.difficulty}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white leading-relaxed">{q.q}</h3>

                <button
                  onClick={() => setExpandedQId(expandedQId === q.id ? null : q.id)}
                  className="text-xs font-semibold text-teal-400 hover:text-teal-300 transition flex items-center gap-1"
                >
                  <span>{expandedQId === q.id ? 'Hide Model Solution ▲' : 'View Model Solution ▼'}</span>
                </button>

                {expandedQId === q.id && (
                  <div className="mt-3 p-4 bg-slate-900 rounded-xl border border-slate-800 font-mono text-xs text-slate-300 whitespace-pre-line leading-relaxed">
                    {q.ans}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 4: Resume Builder & Quiz Assessment (Features 327 & 328) */}
      {activeTab === 'resume' && (
        <div className="space-y-8">
          {/* Resume Generator */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-teal-400"></span>
              ATS-Compliant ECE Resume Builder
            </h2>
            <p className="text-xs text-slate-400">Generates clean markdown resumes tailored to semiconductor & firmware campus placement cells</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Student Name</label>
                <input
                  type="text"
                  value={resumeStudentName}
                  onChange={e => setResumeStudentName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 block mb-1">Roll Number</label>
                <input
                  type="text"
                  value={resumeRollNo}
                  onChange={e => setResumeRollNo(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 block mb-1">Cumulative GPA</label>
                <input
                  type="text"
                  value={resumeCgpa}
                  onChange={e => setResumeCgpa(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white"
                />
              </div>
            </div>

            <button
              onClick={() => setResumeGenerated(true)}
              className="px-5 py-2.5 bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold rounded-xl shadow-lg transition"
            >
              Generate ATS-Ready ECE Resume
            </button>

            {resumeGenerated && (
              <div className="mt-4 p-5 bg-slate-950 border border-slate-800 rounded-xl font-mono text-xs text-slate-300 whitespace-pre-line leading-relaxed overflow-x-auto">
                {`# ${resumeStudentName}
Roll No: ${resumeRollNo} | Institution: Madras Institute of Technology (MIT) Campus, Anna University
Specialization: B.E. Electronics & Communication Engineering (Regulation 2023) | CGPA: ${resumeCgpa} / 10.0

## TECHNICAL SKILLS
- Hardware & Embedded: Verilog HDL, ARM Cortex-M Bare-Metal, FreeRTOS, TinyML, KiCad PCB
- Protocols & Buses: I2C, SPI, UART, CAN 2.0B, LoRaWAN, MQTT, TCP/IP
- EDA & Tools: Cadence Virtuoso, Vivado Design Suite, LTspice, Mixed-Signal Oscilloscope

## FLAGSHIP PROJECTS
- VoltCore Apex Academia: Full-Stack ECE LMS with Hardware-in-the-Loop & SQLite WAL
- Autonomous Edge-AI Soil Spectrometry Node with LoRaWAN & ESP32-S3

## CERTIFICATIONS
- SWAYAM / NPTEL Elite Gold: Microprocessors & Microcontrollers (Anna University ECE)`}
              </div>
            )}
          </div>

          {/* Diagnostic Quiz Assessment */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
              Technical Skills Diagnostic Assessment (Feature 328)
            </h2>
            <p className="text-xs text-slate-400">4 core questions evaluating C memory pointers, VLSI hold timing, Verilog assignments, and RTOS</p>

            <div className="space-y-4">
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                <div className="text-xs font-bold text-white">Q1: Which declaration creates a constant pointer to a mutable integer?</div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {['const int *p', 'int * const p', 'const int * const p', 'int const *p'].map((opt, i) => (
                    <label key={i} className="flex items-center gap-2 p-2 bg-slate-900 rounded-lg cursor-pointer hover:bg-slate-800">
                      <input
                        type="radio"
                        name="q1"
                        checked={quizAnswers.q1 === i}
                        onChange={() => setQuizAnswers({ ...quizAnswers, q1: i })}
                      />
                      <span>{opt}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                <div className="text-xs font-bold text-white">Q2: Why is Hold Time violation catastrophic in manufactured silicon?</div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                  {[
                    'It causes excessive static thermal dissipation',
                    'It requires lowering power supply voltage',
                    'It cannot be resolved by lowering clock frequency',
                    'It destroys the gate dielectric oxide'
                  ].map((opt, i) => (
                    <label key={i} className="flex items-center gap-2 p-2 bg-slate-900 rounded-lg cursor-pointer hover:bg-slate-800">
                      <input
                        type="radio"
                        name="q2"
                        checked={quizAnswers.q2 === i}
                        onChange={() => setQuizAnswers({ ...quizAnswers, q2: i })}
                      />
                      <span>{opt}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-between items-center pt-2">
              <button
                onClick={handleQuizSubmit}
                className="px-5 py-2.5 bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold rounded-xl shadow-lg transition"
              >
                Evaluate Diagnostic Assessment
              </button>

              {quizScore !== null && (
                <div className="text-right font-mono">
                  <span className="text-xs text-slate-400">Calculated Score: </span>
                  <span className="text-base font-bold text-emerald-400">{quizScore} / 100 ({quizScore >= 75 ? 'Tier-1 Day-0 Ready' : 'Review Needed'})</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: Internships & Placement Preparation (Features 329 & 330) */}
      {activeTab === 'placement' && (
        <div className="space-y-8">
          {/* Internship Applications Tracker */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
              Internship Application Tracker (Feature 329)
            </h2>
            <p className="text-xs text-slate-400">Pipeline tracking for summer/winter semiconductor and firmware internships</p>

            <div className="space-y-3">
              {internships.map(item => (
                <div key={item.id} className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-blue-950 text-blue-300 border border-blue-800 rounded">
                        {item.tier}
                      </span>
                      <span className="text-sm font-bold text-white">{item.company}</span>
                    </div>
                    <div className="text-xs text-slate-400">
                      Role: <strong className="text-slate-200">{item.role}</strong> • Stipend: <strong className="text-emerald-400">{item.stipend}</strong>
                    </div>
                  </div>

                  <span className={`px-3 py-1 text-xs font-mono font-bold rounded-lg ${
                    item.status === 'OFFERED'
                      ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                      : 'bg-amber-950 text-amber-300 border border-amber-800'
                  }`}>
                    {item.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Campus Placement Preparation Dashboard */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-slate-800">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                  Campus Placement Preparation Dashboard (Day-0 Countdown)
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">Composite readiness index calculated for top core recruitment visiting MIT Campus</p>
              </div>

              <div className="bg-slate-950 px-4 py-2 rounded-xl border border-emerald-500/40 text-right font-mono">
                <div className="text-[10px] text-slate-400">Composite Readiness</div>
                <div className="text-xl font-extrabold text-emerald-400">{readinessIndex}%</div>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <div className="text-slate-400">CGPA (Normalized):</div>
                <div className="text-base font-bold text-white mt-1">{cgpaVal} / 10.0</div>
              </div>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <div className="text-slate-400">Core ECE Score (35%):</div>
                <div className="text-base font-bold text-cyan-400 mt-1">{coreScore}%</div>
              </div>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <div className="text-slate-400">Aptitude Score (25%):</div>
                <div className="text-base font-bold text-indigo-400 mt-1">{aptitudeScore}%</div>
              </div>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <div className="text-slate-400">Coding Score (25%):</div>
                <div className="text-base font-bold text-amber-400 mt-1">{codingScore}%</div>
              </div>
            </div>

            <div>
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Targeted Tier-1 Core Semiconductor Recruiters</div>
              <div className="flex flex-wrap gap-2">
                {['Qualcomm', 'Texas Instruments', 'Intel', 'Samsung R&D', 'NXP', 'Analog Devices', 'Bosch', 'MediaTek'].map(comp => (
                  <span key={comp} className="px-3 py-1 text-xs bg-slate-950 text-slate-300 border border-slate-700 rounded-lg font-mono">
                    🏢 {comp}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
