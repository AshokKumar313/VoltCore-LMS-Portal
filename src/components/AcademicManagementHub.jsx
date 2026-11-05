import React, { useState, useEffect } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Intelligent Academic Management Hub
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 * ========================================================================================
 */

const SEED_EVENTS = [
  {
    event_id: "EVT_IA1_2026",
    title: "Continuous Assessment Test 1 (IA-1)",
    event_type: "EXAM",
    start_date: "2026-11-12",
    end_date: "2026-11-16",
    venue: "MIT Campus Examination Hall 2",
    target_regulation: "ECE Regulation 2023 (Semester 4)",
    description: "Continuous Assessment covering Units 1 & 2 for all core electronics engineering subjects.",
    days_remaining: 7,
    is_past: false
  },
  {
    event_id: "EVT_LAB_HIL_304",
    title: "Hardware HIL & Microcontroller Lab Practical Bench",
    event_type: "LAB",
    start_date: "2026-11-18",
    end_date: "2026-11-18",
    venue: "Lab 304 Embedded Systems Lab",
    target_regulation: "ECE Regulation 2023 (Semester 4)",
    description: "Hands-on bench assessment for ESP32-S3 and STM32 DMA communication with DSO.",
    days_remaining: 13,
    is_past: false
  },
  {
    event_id: "EVT_NPTEL_EXAM",
    title: "NPTEL Proctored Certification Exam (TinyML & RTOS)",
    event_type: "MILESTONE",
    start_date: "2026-12-05",
    end_date: "2026-12-05",
    venue: "IIT Madras Online Testing Node",
    target_regulation: "ECE Open Elective",
    description: "Nationwide MOOC credit transfer exam for Embedded RTOS and TinyML Edge AI.",
    days_remaining: 30,
    is_past: false
  },
  {
    event_id: "EVT_IA2_2026",
    title: "Continuous Assessment Test 2 (IA-2)",
    event_type: "EXAM",
    start_date: "2026-12-10",
    end_date: "2026-12-14",
    venue: "MIT Campus Examination Hall 2",
    target_regulation: "ECE Regulation 2023 (Semester 4)",
    description: "Continuous Assessment covering Units 3 & 4 with NBA CO-PO mapping analytics.",
    days_remaining: 35,
    is_past: false
  },
  {
    event_id: "EVT_MODEL_PRAC_2026",
    title: "Model Practical Examination (Analog & Digital VLSI Lab)",
    event_type: "LAB",
    start_date: "2026-12-20",
    end_date: "2026-12-22",
    venue: "Electronics Dept Labs 301-304",
    target_regulation: "ECE Regulation 2023 (Semester 4)",
    description: "Full-day mock university practical exam with physical oscilloscope rubrics.",
    days_remaining: 45,
    is_past: false
  },
  {
    event_id: "EVT_MINI_PROJECT_REV",
    title: "Capstone Mini-Project Phase 1 Evaluation Review",
    event_type: "MILESTONE",
    start_date: "2026-12-28",
    end_date: "2026-12-28",
    venue: "Department Seminar Hall, MIT Campus",
    target_regulation: "ECE Regulation 2023 (Semester 4)",
    description: "Faculty jury evaluation of hardware prototype, Git repository, and bill of materials.",
    days_remaining: 53,
    is_past: false
  },
  {
    event_id: "EVT_AU_THEORY_SEM4",
    title: "Anna University End-Semester Theory Examinations",
    event_type: "EXAM",
    start_date: "2027-01-08",
    end_date: "2027-01-24",
    venue: "Centrally Designated Exam Centers",
    target_regulation: "ECE Regulation 2023 (Semester 4)",
    description: "Final university degree examinations under Controller of Examinations, Anna University.",
    days_remaining: 64,
    is_past: false
  }
];

const SEED_SUBJECTS = [
  {
    subject_code: "EC3352",
    subject_name: "Digital Systems Design",
    faculty: "Dr. M. Kannan",
    credits: 3,
    total_topics: 9,
    completed_topics: 5,
    in_progress_topics: 1,
    hours_logged: 17.0,
    target_hours: 45,
    completion_percentage: 55.6,
    co_attainment_score: 1.67,
    units: [
      {
        unit_id: "EC3352_U1",
        unit_number: 1,
        unit_title: "Combinational Logic Circuit Synthesis",
        topics: [
          { topic_id: "EC3352_T1_1", topic_name: "Karnaugh Maps & Quine-McCluskey Optimization", status: "COMPLETED", hours: 3.0, prereq: null },
          { topic_id: "EC3352_T1_2", topic_name: "Carry-Lookahead Adders & Fast ALU Topologies", status: "COMPLETED", hours: 3.0, prereq: "EC3352_T1_1" },
          { topic_id: "EC3352_T1_3", topic_name: "Magnitude Comparators and Decoders", status: "COMPLETED", hours: 3.0, prereq: "EC3352_T1_2" }
        ]
      },
      {
        unit_id: "EC3352_U2",
        unit_number: 2,
        unit_title: "Synchronous Sequential Logic & FSM",
        topics: [
          { topic_id: "EC3352_T2_1", topic_name: "Flip-Flop Metatables & Setup/Hold Time Invariants", status: "COMPLETED", hours: 3.0, prereq: "EC3352_T1_2" },
          { topic_id: "EC3352_T2_2", topic_name: "Mealy & Moore State Machine Reduction", status: "COMPLETED", hours: 3.0, prereq: "EC3352_T2_1" },
          { topic_id: "EC3352_T2_3", topic_name: "Asynchronous & Synchronous Counter Verification", status: "IN_PROGRESS", hours: 2.0, prereq: "EC3352_T2_2" }
        ]
      },
      {
        unit_id: "EC3352_U3",
        unit_number: 3,
        unit_title: "Asynchronous Sequential Networks & Hazards",
        topics: [
          { topic_id: "EC3352_T3_1", topic_name: "Primitive Flow Tables & State Assignment", status: "PENDING", hours: 0.0, prereq: "EC3352_T2_2" },
          { topic_id: "EC3352_T3_2", topic_name: "Critical & Non-Critical Race Elimination", status: "PENDING", hours: 0.0, prereq: "EC3352_T3_1" },
          { topic_id: "EC3352_T3_3", topic_name: "Static and Dynamic Hazards in Combinational Paths", status: "PENDING", hours: 0.0, prereq: "EC3352_T3_2" }
        ]
      }
    ]
  },
  {
    subject_code: "EC3452",
    subject_name: "Electromagnetic Fields",
    faculty: "Dr. P. Nirmal Kumar",
    credits: 4,
    total_topics: 9,
    completed_topics: 4,
    in_progress_topics: 1,
    hours_logged: 19.0,
    target_hours: 60,
    completion_percentage: 44.4,
    co_attainment_score: 1.33,
    units: [
      {
        unit_id: "EC3452_U1",
        unit_number: 1,
        unit_title: "Static Electric Fields & Gauss Law",
        topics: [
          { topic_id: "EC3452_T1_1", topic_name: "Coulomb's Law, Divergence Theorem & Electric Flux", status: "COMPLETED", hours: 4.0, prereq: null },
          { topic_id: "EC3452_T1_2", topic_name: "Poisson and Laplace Differential Equations", status: "COMPLETED", hours: 4.0, prereq: "EC3452_T1_1" },
          { topic_id: "EC3452_T1_3", topic_name: "Capacitance Calculation for Parallel Plates & Coaxial", status: "COMPLETED", hours: 4.0, prereq: "EC3452_T1_2" }
        ]
      },
      {
        unit_id: "EC3452_U2",
        unit_number: 2,
        unit_title: "Static Magnetic Fields & Vector Potential",
        topics: [
          { topic_id: "EC3452_T2_1", topic_name: "Biot-Savart Law and Ampere's Circuital Law", status: "COMPLETED", hours: 4.0, prereq: "EC3452_T1_1" },
          { topic_id: "EC3452_T2_2", topic_name: "Magnetic Vector Potential & Curl of H", status: "IN_PROGRESS", hours: 3.0, prereq: "EC3452_T2_1" },
          { topic_id: "EC3452_T2_3", topic_name: "Self and Mutual Inductance in Solenoids & Toroids", status: "PENDING", hours: 0.0, prereq: "EC3452_T2_2" }
        ]
      },
      {
        unit_id: "EC3452_U4",
        unit_number: 4,
        unit_title: "Time-Varying Fields & Maxwell's Equations",
        topics: [
          { topic_id: "EC3452_T4_1", topic_name: "Faraday's Law of Induction & Transformer EMF", status: "PENDING", hours: 0.0, prereq: "EC3452_T2_2" },
          { topic_id: "EC3452_T4_2", topic_name: "Maxwell's Equations in Differential & Integral Forms", status: "PENDING", hours: 0.0, prereq: "EC3452_T4_1" },
          { topic_id: "EC3452_T4_3", topic_name: "Poynting Vector & Electromagnetic Power Flow", status: "PENDING", hours: 0.0, prereq: "EC3452_T4_2" }
        ]
      }
    ]
  },
  {
    subject_code: "EC3451",
    subject_name: "Linear Integrated Circuits",
    faculty: "Dr. V. Sathiesh Kumar",
    credits: 3,
    total_topics: 6,
    completed_topics: 4,
    in_progress_topics: 1,
    hours_logged: 14.5,
    target_hours: 45,
    completion_percentage: 66.7,
    co_attainment_score: 2.0,
    units: [
      {
        unit_id: "EC3451_U1",
        unit_number: 1,
        unit_title: "Op-Amp Internal Architectures & DC Characteristics",
        topics: [
          { topic_id: "EC3451_T1_1", topic_name: "Differential Pair Stage, CMRR, & Active Current Mirror", status: "COMPLETED", hours: 3.0, prereq: null },
          { topic_id: "EC3451_T1_2", topic_name: "Input Offset Voltage, Slew Rate, & Frequency Compensation", status: "COMPLETED", hours: 3.0, prereq: "EC3451_T1_1" },
          { topic_id: "EC3451_T1_3", topic_name: "Inverting and Non-Inverting Closed-Loop Analysis", status: "COMPLETED", hours: 3.0, prereq: "EC3451_T1_2" }
        ]
      },
      {
        unit_id: "EC3451_U2",
        unit_number: 2,
        unit_title: "Active Filters & Non-Linear Signal Processing",
        topics: [
          { topic_id: "EC3451_T2_1", topic_name: "Sallen-Key Active Low-Pass & High-Pass Filter Design", status: "COMPLETED", hours: 3.0, prereq: "EC3451_T1_3" },
          { topic_id: "EC3451_T2_2", topic_name: "Precision Rectifiers, Peak Detectors & Schmitt Triggers", status: "IN_PROGRESS", hours: 2.5, prereq: "EC3451_T2_1" },
          { topic_id: "EC3451_T2_3", topic_name: "IC 555 Astable and Monostable Multivibrators", status: "PENDING", hours: 0.0, prereq: "EC3451_T2_2" }
        ]
      }
    ]
  },
  {
    subject_code: "EC3491",
    subject_name: "Communication Systems",
    faculty: "Dr. S. Dhanasekaran",
    credits: 3,
    total_topics: 6,
    completed_topics: 4,
    in_progress_topics: 1,
    hours_logged: 14.0,
    target_hours: 45,
    completion_percentage: 66.7,
    co_attainment_score: 2.0,
    units: [
      {
        unit_id: "EC3491_U1",
        unit_number: 1,
        unit_title: "Continuous Wave Modulation (AM & FM)",
        topics: [
          { topic_id: "EC3491_T1_1", topic_name: "DSB-FC, DSB-SC, and SSB-SC Spectral Efficiency", status: "COMPLETED", hours: 3.0, prereq: null },
          { topic_id: "EC3491_T1_2", topic_name: "Wideband Frequency Modulation & Carson's Rule", status: "COMPLETED", hours: 3.0, prereq: "EC3491_T1_1" },
          { topic_id: "EC3491_T1_3", topic_name: "Superheterodyne Receiver Intermediate Frequency Selection", status: "COMPLETED", hours: 3.0, prereq: "EC3491_T1_2" }
        ]
      },
      {
        unit_id: "EC3491_U3",
        unit_number: 3,
        unit_title: "Baseband Digital Transmission & ISI",
        topics: [
          { topic_id: "EC3491_T3_1", topic_name: "Sampling Theorem & Pulse Code Modulation (PCM)", status: "COMPLETED", hours: 3.0, prereq: "EC3491_T1_3" },
          { topic_id: "EC3491_T3_2", topic_name: "Nyquist Criterion for Zero Inter-Symbol Interference", status: "IN_PROGRESS", hours: 2.0, prereq: "EC3491_T3_1" },
          { topic_id: "EC3491_T3_3", topic_name: "Matched Filter Receiver & Probability of Error", status: "PENDING", hours: 0.0, prereq: "EC3491_T3_2" }
        ]
      }
    ]
  }
];

export default function AcademicManagementHub() {
  const [activeTab, setActiveTab] = useState("calendar"); // 'calendar' | 'syllabus' | 'prereq' | 'deadlines'
  const [calendarEvents, setCalendarEvents] = useState(SEED_EVENTS);
  const [selectedEventType, setSelectedEventType] = useState("ALL");
  const [subjects, setSubjects] = useState(SEED_SUBJECTS);
  const [selectedSubjectCode, setSelectedSubjectCode] = useState("EC3352");
  const [toastMessage, setToastMessage] = useState("");
  const [actorRole, setActorRole] = useState("Student"); // 'Student' | 'Faculty'

  // Modal for adding event
  const [showAddEventModal, setShowAddEventModal] = useState(false);
  const [newEventTitle, setNewEventTitle] = useState("");
  const [newEventType, setNewEventType] = useState("EXAM");
  const [newEventStartDate, setNewEventStartDate] = useState("");
  const [newEventVenue, setNewEventVenue] = useState("MIT Campus Examination Hall");
  const [newEventDesc, setNewEventDesc] = useState("");

  const triggerToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(""), 4500);
  };

  // Fetch live overview & calendar on mount if API available
  useEffect(() => {
    fetchCalendarEvents(selectedEventType);
    fetchSyllabusOverview();
  }, [selectedEventType]);

  const fetchCalendarEvents = async (type) => {
    try {
      const resp = await fetch(`/api/academic/calendar?event_type=${type}`);
      if (resp.ok) {
        const data = await resp.json();
        if (Array.isArray(data) && data.length > 0) {
          setCalendarEvents(data);
        }
      }
    } catch {
      // Fallback to initial seeds
    }
  };

  const fetchSyllabusOverview = async () => {
    try {
      const resp = await fetch(`/api/academic/overview`);
      if (resp.ok) {
        const data = await resp.json();
        if (data && data.subject_progress) {
          // Merge with detailed units
          setSubjects(prev =>
            prev.map(sub => {
              const live = data.subject_progress.find(p => p.subject_code === sub.subject_code);
              return live ? { ...sub, ...live } : sub;
            })
          );
        }
      }
    } catch {
      // Fallback
    }
  };

  const handleUpdateTopicStatus = async (topicId, currentStatus, prereqId) => {
    const nextStatus = currentStatus === "COMPLETED" ? "PENDING" : currentStatus === "IN_PROGRESS" ? "COMPLETED" : "IN_PROGRESS";

    // Client-side prerequisite check before making call
    if (nextStatus === "COMPLETED" && prereqId) {
      // Find prerequisite topic
      let isPrereqCompleted = false;
      let prereqName = "";

      for (const sub of subjects) {
        for (const u of sub.units || []) {
          for (const t of u.topics || []) {
            if (t.topic_id === prereqId) {
              prereqName = t.topic_name;
              isPrereqCompleted = t.status === "COMPLETED";
              break;
            }
          }
        }
      }

      if (!isPrereqCompleted) {
        triggerToast(`⚠️ Prerequisite Warning: Complete "${prereqName}" before marking this topic complete!`);
        return;
      }
    }

    try {
      const resp = await fetch("/api/academic/topic/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic_id: topicId,
          status: nextStatus,
          student_id: "2023MITEC042",
          role: actorRole
        })
      });

      if (resp.ok) {
        const resData = await resp.json();
        triggerToast(`✓ Topic updated to ${nextStatus}: ${resData.message}`);
      }
    } catch (err) {
      console.warn("Topic update fallback to local state:", err);
    }

    // Update local state smoothly
    setSubjects(prev =>
      prev.map(sub => ({
        ...sub,
        units: sub.units?.map(u => ({
          ...u,
          topics: u.topics?.map(t =>
            t.topic_id === topicId ? { ...t, status: nextStatus, hours: nextStatus === "COMPLETED" ? t.hours || 3.0 : t.hours } : t
          )
        }))
      }))
    );
  };

  const handleAddCalendarEvent = async (e) => {
    e.preventDefault();
    if (!newEventTitle || !newEventStartDate) {
      triggerToast("Please provide event title and start date.");
      return;
    }

    try {
      const resp = await fetch("/api/academic/calendar/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: newEventTitle,
          event_type: newEventType,
          start_date: newEventStartDate,
          end_date: newEventStartDate,
          venue: newEventVenue,
          description: newEventDesc,
          role: actorRole
        })
      });

      if (resp.ok) {
        const data = await resp.json();
        triggerToast(`✓ Calendar Event Added: ${data.title}`);
        setShowAddEventModal(false);
        fetchCalendarEvents(selectedEventType);
      } else {
        const err = await resp.json();
        triggerToast(`Permission Error: ${err.message || 'Action Forbidden'}`);
      }
    } catch {
      // Local fallback
      const localEvent = {
        event_id: `EVT_${Date.now()}`,
        title: newEventTitle,
        event_type: newEventType,
        start_date: newEventStartDate,
        end_date: newEventStartDate,
        venue: newEventVenue,
        description: newEventDesc,
        target_regulation: "ECE Regulation 2023",
        days_remaining: 15,
        is_past: false
      };
      setCalendarEvents(prev => [localEvent, ...prev]);
      setShowAddEventModal(false);
      triggerToast(`✓ Event scheduled locally: ${newEventTitle}`);
    }
  };

  // Computations
  const totalTopicsCount = subjects.reduce((acc, s) => acc + (s.total_topics || 0), 0);
  const completedTopicsCount = subjects.reduce((acc, s) => acc + (s.completed_topics || 0), 0);
  const overallPercentage = totalTopicsCount > 0 ? Math.round((completedTopicsCount / totalTopicsCount) * 1000) / 10 : 0;
  const currentSubject = subjects.find(s => s.subject_code === selectedSubjectCode) || subjects[0];

  return (
    <div className="space-y-6 font-mono">

      {/* Floating Alert HUD */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 p-4 rounded-2xl bg-[#041026] border border-[#00F0B5]/50 text-white text-xs shadow-2xl flex items-center gap-3 animate-bounce">
          <span className="text-[#00F0B5] text-lg">📅</span>
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Top Banner KPI HUD */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30 shadow-lg">
          <div className="flex items-center justify-between text-slate-400">
            <span>ECE R2023 Progress</span>
            <span className="text-[#00F0B5] font-bold">{overallPercentage}%</span>
          </div>
          <div className="text-2xl font-black text-white mt-1">
            {completedTopicsCount} / {totalTopicsCount} <span className="text-xs text-slate-400 font-normal">Topics</span>
          </div>
          {/* Visual Progress Bar */}
          <div className="w-full bg-slate-800 rounded-full h-1.5 mt-2 overflow-hidden">
            <div
              className="bg-gradient-to-r from-[#00693E] to-[#00F0B5] h-full rounded-full transition-all duration-500"
              style={{ width: `${overallPercentage}%` }}
            ></div>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30 shadow-lg">
          <div className="flex items-center justify-between text-slate-400">
            <span>Upcoming Milestones</span>
            <span className="text-amber-400 font-bold">{calendarEvents.length} Active</span>
          </div>
          <div className="text-2xl font-black text-white mt-1">
            IA-1 In 7 Days
          </div>
          <div className="text-[10px] text-slate-400 mt-1">Continuous Assessment Exam Hall 2</div>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30 shadow-lg">
          <div className="flex items-center justify-between text-slate-400">
            <span>Curricular Credits</span>
            <span className="text-cyan-400 font-bold">13 TRACKED</span>
          </div>
          <div className="text-2xl font-black text-white mt-1">
            4 Core Subjects
          </div>
          <div className="text-[10px] text-cyan-400 mt-1">Sem 4 • MIT Campus ECE</div>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30 shadow-lg">
          <div className="flex items-center justify-between text-slate-400">
            <span>Active RBAC Role</span>
            <button
              onClick={() => setActorRole(actorRole === "Student" ? "Faculty" : "Student")}
              className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                actorRole === "Faculty" ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40" : "bg-[#00693E]/30 text-[#00F0B5] border border-[#00F0B5]/30"
              }`}
              title="Click to toggle role simulation"
            >
              {actorRole} (TOGGLE)
            </button>
          </div>
          <div className="text-2xl font-black text-emerald-400 mt-1">
            {actorRole === "Faculty" ? "Staff Mode" : "Student View"}
          </div>
          <div className="text-[10px] text-slate-400 mt-1">
            {actorRole === "Faculty" ? "Can Schedule Milestones" : "Prerequisite Enforced"}
          </div>
        </div>
      </div>

      {/* Main Tab Bar Navigation */}
      <div className="flex border-b border-slate-800 text-xs">
        <button
          onClick={() => setActiveTab("calendar")}
          className={`px-5 py-3 font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === "calendar"
              ? "border-[#00F0B5] text-[#00F0B5]"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <span>📅 Smart Academic Calendar</span>
          <span className="px-1.5 py-0.2 rounded-full bg-[#00693E]/40 text-[#00F0B5] text-[10px]">
            {calendarEvents.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab("syllabus")}
          className={`px-5 py-3 font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === "syllabus"
              ? "border-[#00F0B5] text-[#00F0B5]"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <span>📚 Syllabus Completion Tracker</span>
          <span className="px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-300 text-[10px]">
            {subjects.length} Subjects
          </span>
        </button>

        <button
          onClick={() => setActiveTab("prereq")}
          className={`px-5 py-3 font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === "prereq"
              ? "border-[#00F0B5] text-[#00F0B5]"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <span>🔗 Prerequisite Course Graph</span>
        </button>

        <button
          onClick={() => setActiveTab("deadlines")}
          className={`px-5 py-3 font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === "deadlines"
              ? "border-[#00F0B5] text-[#00F0B5]"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <span>⏳ Assessment Deadlines</span>
        </button>
      </div>

      {/* TAB 1: Smart Academic Calendar */}
      {activeTab === "calendar" && (
        <div className="space-y-6">
          {/* Filter Bar & Action Header */}
          <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-slate-400 font-bold">Filter By Type:</span>
              {["ALL", "EXAM", "LAB", "MILESTONE"].map((type) => (
                <button
                  key={type}
                  onClick={() => setSelectedEventType(type)}
                  className={`px-3 py-1 rounded-lg transition-all ${
                    selectedEventType === type
                      ? "bg-[#00693E] text-[#00F0B5] font-bold"
                      : "bg-[#020813] text-slate-400 hover:text-white border border-slate-800"
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowAddEventModal(true)}
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-slate-950 font-bold hover:opacity-90 transition-all flex items-center gap-1.5 shadow-md"
              >
                <span>+ Schedule Milestone</span>
                <span className="text-[10px] px-1 rounded bg-slate-900/20">{actorRole}</span>
              </button>
            </div>
          </div>

          {/* Timeline Event Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {calendarEvents.map((evt) => {
              const typeColor =
                evt.event_type === "EXAM"
                  ? "border-rose-500/40 bg-rose-500/10 text-rose-300"
                  : evt.event_type === "LAB"
                  ? "border-cyan-500/40 bg-cyan-500/10 text-cyan-300"
                  : "border-amber-500/40 bg-amber-500/10 text-amber-300";

              return (
                <div
                  key={evt.event_id}
                  className="p-5 rounded-3xl bg-[#041026] border border-slate-800 hover:border-[#00F0B5]/40 transition-all shadow-xl space-y-3 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 text-xs">
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${typeColor}`}>
                        {evt.event_type}
                      </span>
                      <span className="text-[#00F0B5] font-bold text-xs">
                        {evt.days_remaining > 0 ? `In ${evt.days_remaining} Days` : evt.days_remaining === 0 ? "TODAY" : "PAST"}
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-white mt-2 leading-snug">
                      {evt.title}
                    </h3>

                    <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                      {evt.description}
                    </p>
                  </div>

                  <div className="pt-3 border-t border-slate-800/80 space-y-1.5 text-[11px] text-slate-400">
                    <div className="flex items-center justify-between">
                      <span>Dates:</span>
                      <span className="text-white font-mono font-medium">
                        {evt.start_date} {evt.end_date !== evt.start_date ? `to ${evt.end_date}` : ""}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Venue:</span>
                      <span className="text-slate-300">{evt.venue}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Regulation:</span>
                      <span className="text-[#00F0B5] text-[10px] font-mono">{evt.target_regulation}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB 2: Syllabus Completion Tracker */}
      {activeTab === "syllabus" && (
        <div className="space-y-6">
          {/* Subject Switcher Chips */}
          <div className="flex flex-wrap gap-2">
            {subjects.map((sub) => (
              <button
                key={sub.subject_code}
                onClick={() => setSelectedSubjectCode(sub.subject_code)}
                className={`p-3 rounded-2xl border text-left transition-all flex-1 min-w-[200px] ${
                  selectedSubjectCode === sub.subject_code
                    ? "bg-[#041026] border-[#00F0B5] shadow-lg shadow-[#00F0B5]/10"
                    : "bg-[#020813] border-slate-800 hover:border-slate-700 text-slate-400"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[#00F0B5] font-bold text-xs font-mono">{sub.subject_code}</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-bold">
                    {sub.credits} Credits
                  </span>
                </div>
                <div className="text-sm font-bold text-white mt-1 truncate">{sub.subject_name}</div>
                <div className="flex items-center justify-between text-[10px] text-slate-400 mt-2">
                  <span>{sub.faculty}</span>
                  <span className="text-emerald-400 font-bold">{sub.completion_percentage}%</span>
                </div>
              </button>
            ))}
          </div>

          {/* Current Subject Unit & Topic Breakdown */}
          <div className="p-6 rounded-3xl bg-[#041026] border border-[#00F0B5]/30 shadow-2xl space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-black text-white font-sans">{currentSubject.subject_name}</span>
                  <span className="px-2 py-0.5 rounded bg-[#00693E]/40 text-[#00F0B5] text-xs font-bold border border-[#00F0B5]/30">
                    {currentSubject.subject_code}
                  </span>
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  Faculty in Charge: <span className="text-slate-200 font-bold">{currentSubject.faculty}</span> • Target: {currentSubject.target_hours} Hours
                </div>
              </div>

              <div className="text-right">
                <div className="text-2xl font-black text-[#00F0B5]">
                  {currentSubject.completion_percentage}%
                </div>
                <div className="text-[10px] text-slate-400">CO Attainment: {currentSubject.co_attainment_score} / 3.0</div>
              </div>
            </div>

            {/* Units & Topics List */}
            <div className="space-y-6">
              {currentSubject.units?.map((unit) => (
                <div key={unit.unit_id} className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-white">
                      Unit {unit.unit_number}: {unit.unit_title}
                    </span>
                    <span className="text-slate-400 text-[11px]">
                      {unit.topics.filter(t => t.status === "COMPLETED").length} / {unit.topics.length} Completed
                    </span>
                  </div>

                  {/* Topic Items with Interactive Status Toggles */}
                  <div className="space-y-2">
                    {unit.topics.map((t) => {
                      const isComp = t.status === "COMPLETED";
                      const isIP = t.status === "IN_PROGRESS";

                      return (
                        <div
                          key={t.topic_id}
                          className="p-3 rounded-xl bg-[#041026] border border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs hover:border-slate-700 transition-all"
                        >
                          <div className="space-y-0.5">
                            <div className="flex items-center gap-2">
                              <span className="text-slate-200 font-medium">{t.topic_name}</span>
                              {t.prereq && (
                                <span className="text-[9px] px-1 rounded bg-slate-800 text-slate-400" title={`Requires ${t.prereq}`}>
                                  Prereq: {t.prereq}
                                </span>
                              )}
                            </div>
                            <div className="text-[10px] text-slate-500 font-mono">
                              Topic ID: {t.topic_id} • Logged: {t.hours} hrs
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => handleUpdateTopicStatus(t.topic_id, t.status, t.prereq)}
                              className={`px-3 py-1.5 rounded-lg text-[10px] font-bold transition-all flex items-center gap-1.5 ${
                                isComp
                                  ? "bg-[#00693E] text-[#00F0B5] hover:bg-rose-900/40 hover:text-rose-300"
                                  : isIP
                                  ? "bg-cyan-500/20 text-cyan-300 hover:bg-[#00693E] hover:text-[#00F0B5]"
                                  : "bg-slate-800 text-slate-400 hover:bg-cyan-500/20 hover:text-cyan-300"
                              }`}
                              title="Click to advance/toggle topic status"
                            >
                              <span>{isComp ? "✓ COMPLETED" : isIP ? "⚙ IN PROGRESS" : "○ PENDING"}</span>
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Prerequisite Dependency Course Graph */}
      {activeTab === "prereq" && (
        <div className="p-6 rounded-3xl bg-[#041026] border border-slate-800 shadow-xl space-y-6">
          <div className="border-b border-slate-800 pb-3 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white">Course Prerequisite Dependency Engine</h3>
              <p className="text-xs text-slate-400">Strict sequencing prevents knowledge gaps in Anna University ECE R2023 curriculum.</p>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-[#00693E]/40 text-[#00F0B5] font-bold">
              DAG ENFORCED
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-3">
              <span className="text-xs font-bold text-[#00F0B5]">EC3352: Digital Systems Design Sequential Tree</span>
              <div className="space-y-2 text-xs">
                <div className="p-2.5 rounded-lg bg-[#041026] border border-emerald-500/40 text-emerald-300 flex items-center justify-between">
                  <span>1. K-Maps Optimization (EC3352_T1_1)</span>
                  <span className="text-[10px]">✓ FOUNDATION</span>
                </div>
                <div className="text-center text-slate-600">↓</div>
                <div className="p-2.5 rounded-lg bg-[#041026] border border-emerald-500/40 text-emerald-300 flex items-center justify-between">
                  <span>2. Carry-Lookahead Adders (EC3352_T1_2)</span>
                  <span className="text-[10px]">✓ SATISFIED</span>
                </div>
                <div className="text-center text-slate-600">↓</div>
                <div className="p-2.5 rounded-lg bg-[#041026] border border-emerald-500/40 text-emerald-300 flex items-center justify-between">
                  <span>3. Flip-Flop Metatables & Timing (EC3352_T2_1)</span>
                  <span className="text-[10px]">✓ SATISFIED</span>
                </div>
                <div className="text-center text-slate-600">↓</div>
                <div className="p-2.5 rounded-lg bg-[#041026] border border-emerald-500/40 text-emerald-300 flex items-center justify-between">
                  <span>4. Mealy/Moore State Machines (EC3352_T2_2)</span>
                  <span className="text-[10px]">✓ SATISFIED</span>
                </div>
                <div className="text-center text-slate-600">↓</div>
                <div className="p-2.5 rounded-lg bg-[#041026] border border-amber-500/40 text-amber-300 flex items-center justify-between">
                  <span>5. Primitive Flow Tables (EC3352_T3_1)</span>
                  <span className="text-[10px]">○ UNLOCKED</span>
                </div>
                <div className="text-center text-slate-600">↓</div>
                <div className="p-2.5 rounded-lg bg-[#041026] border border-slate-800 text-slate-500 flex items-center justify-between">
                  <span>6. Race Elimination & Hazards (EC3352_T3_2)</span>
                  <span className="text-[10px]">🔒 BLOCKED</span>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-3">
              <span className="text-xs font-bold text-cyan-400">EC3452: Electromagnetic Fields Wave Progression</span>
              <div className="space-y-2 text-xs">
                <div className="p-2.5 rounded-lg bg-[#041026] border border-emerald-500/40 text-emerald-300 flex items-center justify-between">
                  <span>1. Coulomb's Law & Flux Divergence (EC3452_T1_1)</span>
                  <span className="text-[10px]">✓ FOUNDATION</span>
                </div>
                <div className="text-center text-slate-600">↓</div>
                <div className="p-2.5 rounded-lg bg-[#041026] border border-emerald-500/40 text-emerald-300 flex items-center justify-between">
                  <span>2. Biot-Savart & Ampere's Law (EC3452_T2_1)</span>
                  <span className="text-[10px]">✓ SATISFIED</span>
                </div>
                <div className="text-center text-slate-600">↓</div>
                <div className="p-2.5 rounded-lg bg-[#041026] border border-cyan-500/40 text-cyan-300 flex items-center justify-between">
                  <span>3. Magnetic Vector Potential (EC3452_T2_2)</span>
                  <span className="text-[10px]">⚙ IN PROGRESS</span>
                </div>
                <div className="text-center text-slate-600">↓</div>
                <div className="p-2.5 rounded-lg bg-[#041026] border border-slate-800 text-slate-500 flex items-center justify-between">
                  <span>4. Faraday's Law & Maxwell EMF (EC3452_T4_1)</span>
                  <span className="text-[10px]">🔒 BLOCKED</span>
                </div>
                <div className="text-center text-slate-600">↓</div>
                <div className="p-2.5 rounded-lg bg-[#041026] border border-slate-800 text-slate-500 flex items-center justify-between">
                  <span>5. Poynting Vector Power Flow (EC3452_T4_3)</span>
                  <span className="text-[10px]">🔒 BLOCKED</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: Assessment Deadlines Ledger */}
      {activeTab === "deadlines" && (
        <div className="p-6 rounded-3xl bg-[#041026] border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3 text-xs">
            <span className="font-bold text-white text-sm">Critical Academic Deadlines Ledger</span>
            <span className="text-[#00F0B5] font-mono">Anna University COE Synchronized</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-mono text-[11px]">
                  <th className="pb-3">ASSESSMENT / MILESTONE</th>
                  <th className="pb-3">TYPE</th>
                  <th className="pb-3">TARGET DATES</th>
                  <th className="pb-3">VENUE</th>
                  <th className="pb-3 text-right">COUNTDOWN</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {calendarEvents.map((evt) => (
                  <tr key={evt.event_id} className="hover:bg-[#020813] transition-colors">
                    <td className="py-3 font-semibold text-white">{evt.title}</td>
                    <td className="py-3">
                      <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-[#00F0B5] font-bold">
                        {evt.event_type}
                      </span>
                    </td>
                    <td className="py-3 font-mono text-slate-300">{evt.start_date}</td>
                    <td className="py-3 text-slate-400">{evt.venue}</td>
                    <td className="py-3 text-right font-bold text-emerald-400">
                      {evt.days_remaining > 0 ? `${evt.days_remaining} Days` : "TODAY"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Schedule Milestone Modal */}
      {showAddEventModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#041026] border border-[#00F0B5]/40 rounded-3xl p-6 max-w-md w-full space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <span className="text-sm font-bold text-white">Schedule Academic Milestone</span>
              <button onClick={() => setShowAddEventModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <form onSubmit={handleAddCalendarEvent} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Milestone Title</label>
                <input
                  type="text"
                  value={newEventTitle}
                  onChange={(e) => setNewEventTitle(e.target.value)}
                  placeholder="e.g. EC3452 Special Revision Lab Assessment"
                  className="w-full px-3 py-2 rounded-xl bg-[#020813] border border-slate-700 text-white focus:outline-none focus:border-[#00F0B5]"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">Event Type</label>
                  <select
                    value={newEventType}
                    onChange={(e) => setNewEventType(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-[#020813] border border-slate-700 text-white focus:outline-none focus:border-[#00F0B5]"
                  >
                    <option value="EXAM">EXAM</option>
                    <option value="LAB">LAB</option>
                    <option value="MILESTONE">MILESTONE</option>
                  </select>
                </div>

                <div>
                  <label className="text-slate-400 block mb-1">Target Date</label>
                  <input
                    type="date"
                    value={newEventStartDate}
                    onChange={(e) => setNewEventStartDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-[#020813] border border-slate-700 text-white focus:outline-none focus:border-[#00F0B5]"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Venue</label>
                <input
                  type="text"
                  value={newEventVenue}
                  onChange={(e) => setNewEventVenue(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#020813] border border-slate-700 text-white focus:outline-none focus:border-[#00F0B5]"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Description</label>
                <textarea
                  value={newEventDesc}
                  onChange={(e) => setNewEventDesc(e.target.value)}
                  rows="2"
                  placeholder="Assessment rubric and syllabus scope..."
                  className="w-full px-3 py-2 rounded-xl bg-[#020813] border border-slate-700 text-white focus:outline-none focus:border-[#00F0B5]"
                ></textarea>
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddEventModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-slate-950 font-bold hover:opacity-90"
                >
                  Confirm Milestone
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MIT Campus Department of Electronics Engineering Institutional Footer */}
      <div className="p-4 rounded-2xl bg-[#041026]/70 border border-slate-800 text-center text-xs text-slate-400 flex flex-col sm:flex-row items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span>Department of Electronics Engineering • Madras Institute of Technology (MIT) Campus</span>
        </div>
        <div className="text-[11px] font-mono text-slate-500">
          Anna University Regulation 2023 • Academic Management Engine v1.0
        </div>
      </div>
    </div>
  );
}
