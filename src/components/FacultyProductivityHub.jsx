import React, { useState, useEffect } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Faculty & Department Productivity Workspace (Phase 25)
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * Course Scope: EC3451 (LIC), EC3491 (CS), EC3352 (DSD), EC3601 (Embedded), EC3711 (Mini-Proj)
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A (2023MITEC042)
 * Department Head: Dr. P. Nirmal Kumar (Professor & Head, Dept of Electronics)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 * ========================================================================================
 */

// Fallback Lesson Plans
const FALLBACK_PLANS = [
  {
    plan_id: "LP_EC3451_01",
    course_code: "EC3451",
    course_title: "Linear Integrated Circuits",
    unit_number: 1,
    unit_title: "Unit I: Operational Amplifier Fundamentals",
    topic_title: "Differential Amplifier configurations, CMRR, and current mirror bias circuits",
    planned_hours: 2.0,
    actual_hours: 2.0,
    pedagogy_mode: "Chalk & Talk",
    course_outcome: "CO1",
    bloom_level: "K2-Understand",
    status: "COMPLETED",
    completed_date: "2026-10-10",
    notes: "Derivations completed on board; students solved 2 practice numericals."
  },
  {
    plan_id: "LP_EC3451_02",
    course_code: "EC3451",
    course_title: "Linear Integrated Circuits",
    unit_number: 1,
    unit_title: "Unit I: Operational Amplifier Fundamentals",
    topic_title: "Op-Amp non-ideal DC/AC characteristics: input offset voltage, slew rate, frequency response",
    planned_hours: 2.0,
    actual_hours: 2.0,
    pedagogy_mode: "Interactive PPT",
    course_outcome: "CO1",
    bloom_level: "K3-Apply",
    status: "COMPLETED",
    completed_date: "2026-10-14",
    notes: "DSO demonstration of slew-rate triangular distortion conducted."
  },
  {
    plan_id: "LP_EC3451_03",
    course_code: "EC3451",
    course_title: "Linear Integrated Circuits",
    unit_number: 2,
    unit_title: "Unit II: Active Filters & Signal Conditioning",
    topic_title: "First and second-order low-pass Butterworth filters using Sallen-Key topology",
    planned_hours: 2.0,
    actual_hours: 2.0,
    pedagogy_mode: "Wokwi Simulation",
    course_outcome: "CO2",
    bloom_level: "K3-Apply",
    status: "COMPLETED",
    completed_date: "2026-10-22",
    notes: "Simulated cutoff response in LTspice and compared with KaTeX formulas."
  },
  {
    plan_id: "LP_EC3451_04",
    course_code: "EC3451",
    course_title: "Linear Integrated Circuits",
    unit_number: 2,
    unit_title: "Unit II: Active Filters & Signal Conditioning",
    topic_title: "Higher-order filter synthesis, Chebyshev passband ripple, and bandpass state-variable filters",
    planned_hours: 2.0,
    actual_hours: 1.5,
    pedagogy_mode: "Interactive PPT",
    course_outcome: "CO2",
    bloom_level: "K4-Analyze",
    status: "IN_PROGRESS",
    completed_date: null,
    notes: "Students preparing group presentations on bandpass architectures."
  },
  {
    plan_id: "LP_EC3451_05",
    course_code: "EC3451",
    course_title: "Linear Integrated Circuits",
    unit_number: 3,
    unit_title: "Unit III: Waveform Generators & 555 Timers",
    topic_title: "Schmitt Trigger, Astable and Monostable multivibrators using IC 555",
    planned_hours: 2.0,
    actual_hours: 0.0,
    pedagogy_mode: "Hardware Lab Bench",
    course_outcome: "CO3",
    bloom_level: "K3-Apply",
    status: "PLANNED",
    completed_date: null,
    notes: "Scheduled for next lab cycle in Lab 304."
  },
  {
    plan_id: "LP_EC3491_01",
    course_code: "EC3491",
    course_title: "Communication Systems",
    unit_number: 1,
    unit_title: "Unit I: Amplitude Modulation Systems",
    topic_title: "Double Sideband Full Carrier (DSB-FC) and Suppressed Carrier (DSB-SC) modulation equations",
    planned_hours: 2.0,
    actual_hours: 2.0,
    pedagogy_mode: "Chalk & Talk",
    course_outcome: "CO1",
    bloom_level: "K2-Understand",
    status: "COMPLETED",
    completed_date: "2026-10-12",
    notes: "Power efficiency calculations derived for modulation index mu=1.0."
  },
  {
    plan_id: "LP_EC3491_02",
    course_code: "EC3491",
    course_title: "Communication Systems",
    unit_number: 2,
    unit_title: "Unit II: Angle Modulation & Carson Rule",
    topic_title: "FM frequency deviation, modulation index, and Carson's rule transmission bandwidth",
    planned_hours: 2.0,
    actual_hours: 2.0,
    pedagogy_mode: "Wokwi Simulation",
    course_outcome: "CO2",
    bloom_level: "K3-Apply",
    status: "COMPLETED",
    completed_date: "2026-10-28",
    notes: "Audio spectrum demonstration shown using software spectrogram tool."
  },
  {
    plan_id: "LP_EC3491_03",
    course_code: "EC3491",
    course_title: "Communication Systems",
    unit_number: 3,
    unit_title: "Unit III: Pulse Modulation & Sampling",
    topic_title: "Nyquist sampling theorem, aliasing mitigation, and Pulse Code Modulation (PCM) quantization",
    planned_hours: 2.0,
    actual_hours: 0.0,
    pedagogy_mode: "Flipped Classroom",
    course_outcome: "CO3",
    bloom_level: "K4-Analyze",
    status: "PLANNED",
    completed_date: null,
    notes: "Pre-lecture quiz uploaded to portal."
  }
];

// Fallback Templates
const FALLBACK_TEMPLATES = [
  {
    template_id: "TPL_THEORY_ACTIVE_FILTERS",
    course_code: "EC3451",
    title: "Active Filter Synthesis & Sallen-Key Topologies",
    category: "THEORY_UNIT",
    description: "Comprehensive 3-lecture sequence on second-order active low-pass and high-pass Butterworth filters with frequency scaling and damping factor tuning.",
    suggested_duration_hours: 3.0,
    co_mappings: ["CO2", "CO3"],
    pedagogical_aids: ["Interactive PPT", "LTspice Live Waveform Projection", "Chalk & Talk Derivations"],
    sample_topics: [
      "Butterworth filter polynomial approximations and transfer functions",
      "Sallen-Key low-pass filter synthesis with unity gain and equal component design",
      "Quality factor (Q) tuning, cutoff frequency determination, and component tolerance sensitivity"
    ]
  },
  {
    template_id: "TPL_LAB_OPAMP_CHARACTERIZATION",
    course_code: "EC3451",
    title: "Op-Amp Non-Ideal Dynamics & Slew Rate Measurement",
    category: "LAB_PRACTICAL",
    description: "Laboratory practical on characterizing LM741 / TL082 input offset voltage, slew rate distortion limits, and gain-bandwidth product trade-offs.",
    suggested_duration_hours: 2.0,
    co_mappings: ["CO1", "CO4"],
    pedagogical_aids: ["Digital Storage Oscilloscope (DSO)", "Function Generator", "Hardware Breadboard Kit"],
    sample_topics: [
      "Input offset voltage measurement and nulling potentiometer circuit",
      "Large-signal square wave response and slew rate calculation (V/us)",
      "Frequency response measurement and closed-loop -3dB bandwidth determination"
    ]
  },
  {
    template_id: "TPL_FLIPPED_MODULATION_CARSON",
    course_code: "EC3491",
    title: "FM Carson's Rule & Spectral Power Distribution",
    category: "FLIPPED_CLASSROOM",
    description: "Pre-lecture simulation activity followed by group problem solving on Carson's bandwidth rule and Bessel function power distribution in FM broadcasting.",
    suggested_duration_hours: 2.0,
    co_mappings: ["CO2", "CO4"],
    pedagogical_aids: ["Pre-Recorded Video", "VoltCore Spectrum Visualizer", "Group Problem Worksheet"],
    sample_topics: [
      "Narrowband FM vs Wideband FM spectral comparison",
      "Carson's Rule derivation and transmission bandwidth calculations",
      "Power efficiency comparison between standard AM and angle modulation systems"
    ]
  },
  {
    template_id: "TPL_EMBEDDED_RTOS_TASKS",
    course_code: "EC3601",
    title: "Deterministic Preemptive Task Scheduling in FreeRTOS",
    category: "THEORY_UNIT",
    description: "Lecture framework covering Rate Monotonic Scheduling (RMS), priority inversion, mutex priority inheritance, and context switching overhead.",
    suggested_duration_hours: 3.0,
    co_mappings: ["CO3", "CO5"],
    pedagogical_aids: ["Wokwi ESP32 Live Emulation", "Logic Analyzer Trace Viewer", "Interactive PPT"],
    sample_topics: [
      "FreeRTOS task control blocks (TCB) and state transitions",
      "Rate Monotonic priority assignment and CPU utilization bounds",
      "Priority inversion mitigation using binary semaphores vs priority-inheriting mutexes"
    ]
  }
];

// Fallback Assignments
const FALLBACK_ASSIGNMENTS = [
  {
    assignment_id: "ASGN_EC3451_01",
    course_code: "EC3451",
    title: "Assignment 1: Sallen-Key Active Filter Synthesis & LTspice Verification",
    unit_number: 2,
    due_date: "2026-11-20",
    total_marks: 100.0,
    instructions: "Design a 2nd-order Butterworth low-pass filter with cutoff fc = 1.0 kHz and unity gain. Calculate exact R1, R2, C1, and C2 values. Run AC sweep in LTspice and verify -3dB cutoff.",
    questions: [
      "Derive the transfer function H(s) of a Sallen-Key low-pass filter topology.",
      "Select standard component values assuming C1 = 14.14 nF and C2 = 7.07 nF. Determine required R1 and R2.",
      "Plot the Bode magnitude and phase response from 10 Hz to 100 kHz in LTspice or Python.",
      "Explain the impact of op-amp gain-bandwidth product (GBWP) on filter cutoff degradation at high frequencies."
    ],
    rubric: {
      mathematical_derivation: 25,
      component_selection: 25,
      simulation_accuracy: 30,
      interpretation_and_report: 20
    },
    submissions_count: 1,
    average_score: 96.0,
    status: "PUBLISHED"
  },
  {
    assignment_id: "ASGN_EC3491_01",
    course_code: "EC3491",
    title: "Assignment 1: Angle Modulation & Carson's Bandwidth Analysis",
    unit_number: 2,
    due_date: "2026-11-25",
    total_marks: 100.0,
    instructions: "Analyze a commercial FM broadcast transmission with carrier fc = 100 MHz, message frequency fm = 15 kHz, and peak frequency deviation delta_f = 75 kHz.",
    questions: [
      "Calculate the FM modulation index beta.",
      "Apply Carson's Rule to determine total 98% power bandwidth in kHz.",
      "Compare with the 1% Bessel function sideband bandwidth.",
      "Compute the total transmitted power if carrier amplitude Ac = 10V into 50 Ohm antenna."
    ],
    rubric: {
      modulation_index_calc: 30,
      carsons_rule_bandwidth: 35,
      power_calculations: 20,
      technical_presentation: 15
    },
    submissions_count: 0,
    average_score: 0.0,
    status: "PUBLISHED"
  }
];

// Fallback Feedback
const FALLBACK_FEEDBACKS = [
  {
    feedback_id: "FB_ASGN_EC3451_01_2023MITEC042",
    assignment_id: "ASGN_EC3451_01",
    student_id: "2023MITEC042",
    student_name: "Ashok Kumar A",
    submission_url: "https://github.com/AshokKumar313/VoltCore-LMS-Portal/raw/main/reports/ec3451_assignment1_filter_synthesis.pdf",
    marks_obtained: 96.0,
    total_marks: 100.0,
    rubric_scores: {
      mathematical_derivation: 25.0,
      component_selection: 24.0,
      simulation_accuracy: 29.0,
      interpretation_and_report: 18.0
    },
    qualitative_feedback: "Exemplary submission. Mathematical derivation for Sallen-Key second-order transfer function was rigorous. LTspice AC analysis matches theoretical cutoff within 0.4% error. Excellent analysis of high-frequency op-amp GBWP limitations.",
    evaluated_by: "Dr. P. Nirmal Kumar (Professor & Head, Dept of Electronics)",
    status: "GRADED"
  }
];

// Fallback Meeting Minutes
const FALLBACK_MEETINGS = [
  {
    meeting_id: "MOM_MIT_ECE_2026_10_25",
    meeting_title: "Department Faculty Review: Internal Assessment 1 & Lab Attainment",
    meeting_date: "2026-10-25",
    chairperson: "Dr. P. Nirmal Kumar (HOD / Chair)",
    attendees: [
      "Dr. P. Nirmal Kumar (HOD / Chair)",
      "Dr. M. Kannan (Professor, ECE)",
      "Dr. S. Piramasubramanian (Assoc. Prof, ECE)",
      "Dr. G. Balamurugan (Asst. Prof, ECE)",
      "Ashok Kumar A (Student Platform Lead, Invitee)"
    ],
    agenda_items: [
      "Analysis of Internal Assessment 1 (IA-1) pass percentages and CO attainment across EC3451 & EC3491.",
      "Review of Lab 304 hardware equipment calibration (DSOs, Signal Generators, FPGA trainers).",
      "Implementation of continuous digital rubric grading in VoltCore Apex Academia portal.",
      "Mini-project (EC3711) milestone tracking and faculty supervisor assignments."
    ],
    key_decisions: [
      "Remedial problem-solving tutorials approved for students scoring below 60% in IA-1.",
      "VoltCore automated rubric grading officially recognized for 20% continuous evaluation marks.",
      "Laboratory hours extended to 6:30 PM on Thursdays for hardware project prototyping."
    ],
    action_items: [
      { task: "Publish remedial tutorial schedule for EC3451 Unit II", assignee: "Dr. G. Balamurugan", deadline: "2026-11-05", status: "COMPLETED" },
      { task: "Verify calibration certificates for DSO benches in Lab 304", assignee: "Lab Superintendent", deadline: "2026-11-12", status: "IN_PROGRESS" },
      { task: "Collect mid-term mini-project proposal submissions via portal", assignee: "Dr. M. Kannan", deadline: "2026-11-18", status: "PENDING" }
    ]
  }
];

export default function FacultyProductivityHub() {
  const [activeTab, setActiveTab] = useState('lesson_plans'); // 'lesson_plans', 'templates', 'assignments', 'feedback', 'meetings'
  const [facultyId] = useState('FAC_MIT_ECE_001');
  const [overview, setOverview] = useState(null);
  const [notification, setNotification] = useState(null);

  // Filter State
  const [selectedCourse, setSelectedCourse] = useState('ALL');
  const [selectedUnit, setSelectedUnit] = useState('ALL');

  // Lesson Plans State
  const [lessonPlans, setLessonPlans] = useState(FALLBACK_PLANS);
  const [newPlanForm, setNewPlanForm] = useState({
    course_code: 'EC3451',
    course_title: 'Linear Integrated Circuits',
    unit_number: 1,
    unit_title: 'Unit I: Operational Amplifier Fundamentals',
    topic_title: '',
    planned_hours: 2.0,
    pedagogy_mode: 'Chalk & Talk',
    course_outcome: 'CO1',
    bloom_level: 'K2-Understand',
    notes: ''
  });

  // Templates State
  const [templates, setTemplates] = useState(FALLBACK_TEMPLATES);

  // Assignments State
  const [assignments, setAssignments] = useState(FALLBACK_ASSIGNMENTS);
  const [newAsgnForm, setNewAsgnForm] = useState({
    course_code: 'EC3451',
    title: '',
    unit_number: 1,
    due_date: '2026-12-05',
    total_marks: 100,
    instructions: '',
    questions: ['1. Formulate the circuit transfer function.', '2. Run transient simulation and compute rise time.']
  });

  // Feedback State
  const [feedbacks, setFeedbacks] = useState(FALLBACK_FEEDBACKS);
  const [newFbForm, setNewFbForm] = useState({
    assignment_id: 'ASGN_EC3451_01',
    student_id: '2023MITEC042',
    student_name: 'Ashok Kumar A',
    marks_obtained: 95,
    total_marks: 100,
    qualitative_feedback: 'Well-structured simulation report with accurate Bode frequency measurements.'
  });

  // Meetings State
  const [meetings, setMeetings] = useState(FALLBACK_MEETINGS);

  const showToast = (msg, type = 'info') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  };

  useEffect(() => {
    fetchOverview();
    fetchLessonPlans();
    fetchTemplates();
    fetchAssignments();
    fetchFeedbacks();
    fetchMeetings();
  }, []);

  const fetchOverview = async () => {
    try {
      const res = await fetch(`/api/faculty/overview?faculty_id=${facultyId}`);
      if (res.ok) {
        const data = await res.json();
        setOverview(data);
      }
    } catch {
      // offline fallback
      setOverview({
        metrics: {
          total_lesson_plans: lessonPlans.length,
          completed_lesson_plans: lessonPlans.filter(p => p.status === 'COMPLETED').length,
          in_progress_lesson_plans: lessonPlans.filter(p => p.status === 'IN_PROGRESS').length,
          syllabus_coverage_percent: 62.5,
          total_planned_hours: 16.0,
          total_actual_hours: 11.5,
          total_assignments: assignments.length,
          total_graded_feedbacks: feedbacks.length,
          average_assignment_score: 96.0,
          total_meeting_minutes: meetings.length,
          total_templates_available: templates.length
        }
      });
    }
  };

  const fetchLessonPlans = async () => {
    try {
      const res = await fetch('/api/faculty/lesson_plans');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          setLessonPlans(data);
        }
      }
    } catch {
      setLessonPlans(FALLBACK_PLANS);
    }
  };

  const fetchTemplates = async () => {
    try {
      const res = await fetch('/api/faculty/templates');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) setTemplates(data);
      }
    } catch {
      setTemplates(FALLBACK_TEMPLATES);
    }
  };

  const fetchAssignments = async () => {
    try {
      const res = await fetch('/api/faculty/assignments');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) setAssignments(data);
      }
    } catch {
      setAssignments(FALLBACK_ASSIGNMENTS);
    }
  };

  const fetchFeedbacks = async () => {
    try {
      const res = await fetch('/api/faculty/feedback');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) setFeedbacks(data);
      }
    } catch {
      setFeedbacks(FALLBACK_FEEDBACKS);
    }
  };

  const fetchMeetings = async () => {
    try {
      const res = await fetch('/api/faculty/meeting_minutes');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) setMeetings(data);
      }
    } catch {
      setMeetings(FALLBACK_MEETINGS);
    }
  };

  // Toggle Lesson Plan Status
  const togglePlanStatus = async (planId, currentStatus) => {
    const nextStatus = currentStatus === 'PLANNED' ? 'IN_PROGRESS' : (currentStatus === 'IN_PROGRESS' ? 'COMPLETED' : 'PLANNED');
    try {
      await fetch('/api/faculty/lesson_plan/status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan_id: planId, status: nextStatus, role: 'Faculty' })
      });
    } catch {
      // offline
    }

    setLessonPlans(lessonPlans.map(p => p.plan_id === planId ? {
      ...p,
      status: nextStatus,
      completed_date: nextStatus === 'COMPLETED' ? new Date().toISOString().split('T')[0] : null
    } : p));
    showToast(`Lesson plan status updated to ${nextStatus}.`, 'info');
    fetchOverview();
  };

  // Create Lesson Plan
  const handleCreatePlan = async (e) => {
    e.preventDefault();
    if (!newPlanForm.topic_title.trim()) {
      showToast('Please enter topic title.', 'error');
      return;
    }

    try {
      const res = await fetch('/api/faculty/lesson_plans', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...newPlanForm, role: 'Faculty' })
      });
      if (res.ok) {
        showToast('Lesson plan registered successfully!', 'success');
        fetchLessonPlans();
        fetchOverview();
        setNewPlanForm({ ...newPlanForm, topic_title: '', notes: '' });
        return;
      }
    } catch {
      // offline
    }

    const created = {
      plan_id: `LP_${newPlanForm.course_code}_${Date.now()}`,
      ...newPlanForm,
      actual_hours: 0.0,
      status: 'PLANNED',
      completed_date: null
    };
    setLessonPlans([...lessonPlans, created]);
    setNewPlanForm({ ...newPlanForm, topic_title: '', notes: '' });
    showToast('Lesson plan registered locally.', 'success');
  };

  // Clone Template into Lesson Plan
  const cloneTemplateToPlan = (tpl) => {
    setNewPlanForm({
      course_code: tpl.course_code,
      course_title: tpl.course_code === 'EC3451' ? 'Linear Integrated Circuits' : (tpl.course_code === 'EC3491' ? 'Communication Systems' : 'Embedded Systems'),
      unit_number: 2,
      unit_title: 'Unit II: Applied System Synthesis',
      topic_title: tpl.sample_topics[0] || tpl.title,
      planned_hours: tpl.suggested_duration_hours || 2.0,
      pedagogy_mode: tpl.pedagogical_aids[0] || 'Interactive PPT',
      course_outcome: tpl.co_mappings[0] || 'CO2',
      bloom_level: 'K3-Apply',
      notes: `Cloned from standard MIT faculty template: ${tpl.title}`
    });
    setActiveTab('lesson_plans');
    showToast(`Template '${tpl.title}' loaded into Lesson Plan Builder!`, 'success');
  };

  // Create Assignment
  const handleCreateAssignment = async (e) => {
    e.preventDefault();
    if (!newAsgnForm.title.trim()) return;

    try {
      const res = await fetch('/api/faculty/assignments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...newAsgnForm, role: 'Faculty' })
      });
      if (res.ok) {
        showToast(`Assignment '${newAsgnForm.title}' published successfully!`, 'success');
        fetchAssignments();
        fetchOverview();
        return;
      }
    } catch {
      // offline
    }

    const createdAsgn = {
      assignment_id: `ASGN_${newAsgnForm.course_code}_${Date.now()}`,
      ...newAsgnForm,
      submissions_count: 0,
      average_score: 0.0,
      status: 'PUBLISHED'
    };
    setAssignments([createdAsgn, ...assignments]);
    showToast('Assignment published to students.', 'success');
  };

  // Record Feedback / Grade
  const handleRecordFeedback = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/faculty/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...newFbForm, role: 'Faculty' })
      });
      if (res.ok) {
        showToast(`Grade and evaluation for ${newFbForm.student_id} saved!`, 'success');
        fetchFeedbacks();
        fetchOverview();
        return;
      }
    } catch {
      // offline
    }

    const createdFb = {
      feedback_id: `FB_${Date.now()}`,
      ...newFbForm,
      evaluated_by: "Dr. P. Nirmal Kumar (HOD, Dept of Electronics)",
      status: 'GRADED'
    };
    setFeedbacks([createdFb, ...feedbacks]);
    showToast('Evaluation report registered locally.', 'success');
  };

  // Filtered Lesson Plans
  const filteredPlans = lessonPlans.filter(p => {
    const courseMatch = selectedCourse === 'ALL' || p.course_code === selectedCourse;
    const unitMatch = selectedUnit === 'ALL' || p.unit_number.toString() === selectedUnit;
    return courseMatch && unitMatch;
  });

  // Calculate coverage for display
  const completedCount = lessonPlans.filter(p => p.status === 'COMPLETED').length;
  const coveragePercent = lessonPlans.length > 0 ? Math.round((completedCount / lessonPlans.length) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Toast Alert */}
      {notification && (
        <div className={`p-3.5 rounded-xl border text-sm flex items-center justify-between transition-all ${
          notification.type === 'error'
            ? 'bg-rose-950/80 border-rose-500/50 text-rose-200'
            : notification.type === 'warning'
            ? 'bg-amber-950/80 border-amber-500/50 text-amber-200'
            : 'bg-[#041026]/90 border-[#00F0B5]/40 text-[#00F0B5]'
        }`}>
          <span>{notification.msg}</span>
          <button onClick={() => setNotification(null)} className="text-xs opacity-70 hover:opacity-100 ml-4">✕</button>
        </div>
      )}

      {/* Top Banner / Metrics Strip */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Syllabus Coverage</span>
          <div className="text-2xl font-bold text-[#00F0B5] mt-1">{coveragePercent}%</div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
            <div className="bg-gradient-to-r from-emerald-500 to-[#00F0B5] h-full rounded-full transition-all duration-500" style={{ width: `${coveragePercent}%` }} />
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Planned / Actual</span>
          <div className="text-xl font-bold text-slate-100 mt-1 font-mono">
            {overview?.metrics?.total_actual_hours || 11.5} / {overview?.metrics?.total_planned_hours || 16.0} <span className="text-xs font-normal text-slate-400">hrs</span>
          </div>
          <span className="text-[10px] text-emerald-400 mt-1">Regulation 2023 Pace</span>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Continuous Assmts</span>
          <div className="text-2xl font-bold text-cyan-300 mt-1">
            {assignments.length} Active
          </div>
          <span className="text-[10px] text-slate-400 mt-1">Rubric Formatted</span>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Avg Student Mark</span>
          <div className="text-2xl font-bold text-amber-300 mt-1 font-mono">
            {overview?.metrics?.average_assignment_score || 96.0}%
          </div>
          <span className="text-[10px] text-slate-400 mt-1">Evaluated by HOD</span>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between col-span-2 md:col-span-1">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Department MoM</span>
          <div className="text-2xl font-bold text-purple-300 mt-1">
            {meetings.length} Recorded
          </div>
          <span className="text-[10px] text-slate-400 mt-1">Action Items Active</span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-slate-800 overflow-x-auto gap-2 pb-2">
        {[
          { id: 'lesson_plans', label: '1. Lesson Plan Studio', desc: 'Syllabus Units I - V' },
          { id: 'templates', label: '2. Lesson Templates', desc: 'MIT Curriculum Library' },
          { id: 'assignments', label: '3. Digital Assignments', desc: 'Distribution & Rubrics' },
          { id: 'feedback', label: '4. Evaluation & Feedback', desc: 'Marks & Qualitative Review' },
          { id: 'meetings', label: '5. Department Minutes', desc: 'MoM & Action Items' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2.5 rounded-xl text-left whitespace-nowrap transition-all ${
              activeTab === tab.id
                ? 'bg-[#00F0B5]/15 border border-[#00F0B5]/40 text-[#00F0B5]'
                : 'text-slate-400 hover:text-slate-200 hover:bg-[#020813] border border-transparent'
            }`}
          >
            <div className="text-xs font-semibold">{tab.label}</div>
            <div className="text-[10px] opacity-70">{tab.desc}</div>
          </button>
        ))}
      </div>

      {/* TAB 1: Lesson Plan Studio */}
      {activeTab === 'lesson_plans' && (
        <div className="space-y-6">
          {/* Controls & Filter Bar */}
          <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-slate-400 font-mono">Course:</span>
              {['ALL', 'EC3451', 'EC3491', 'EC3352', 'EC3601'].map(c => (
                <button
                  key={c}
                  onClick={() => setSelectedCourse(c)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all ${
                    selectedCourse === c
                      ? 'bg-[#00F0B5] text-slate-950 font-bold'
                      : 'bg-[#020813] text-slate-400 hover:text-slate-200 border border-slate-800'
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-slate-400 font-mono">Unit:</span>
              {['ALL', '1', '2', '3', '4', '5'].map(u => (
                <button
                  key={u}
                  onClick={() => setSelectedUnit(u)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all ${
                    selectedUnit === u
                      ? 'bg-emerald-500 text-slate-950 font-bold'
                      : 'bg-[#020813] text-slate-400 hover:text-slate-200 border border-slate-800'
                  }`}
                >
                  {u === 'ALL' ? 'All Units' : `Unit ${u}`}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Planned Lectures Table */}
            <div className="lg:col-span-2 space-y-3">
              <div className="p-5 rounded-2xl bg-[#041026] border border-slate-800 space-y-3">
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                  <div>
                    <h3 className="text-md font-semibold text-slate-100">Unit-Wise Syllabus Execution Ledger</h3>
                    <p className="text-xs text-slate-400">Tracking planned vs actual lecture hours and pedagogical tools</p>
                  </div>
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-[#00693E]/40 text-[#00F0B5] border border-[#00F0B5]/30">
                    {filteredPlans.length} Lectures Listed
                  </span>
                </div>

                <div className="space-y-2.5">
                  {filteredPlans.map((plan) => (
                    <div key={plan.plan_id} className="p-3.5 rounded-xl bg-[#020813] border border-slate-800 space-y-2">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-[#00F0B5]">
                              {plan.course_code}
                            </span>
                            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                              Unit {plan.unit_number}
                            </span>
                            <span className="text-[10px] font-mono text-cyan-400">
                              {plan.course_outcome} • {plan.bloom_level}
                            </span>
                          </div>
                          <h4 className="text-xs font-bold text-slate-100 mt-1">{plan.topic_title}</h4>
                        </div>

                        <button
                          onClick={() => togglePlanStatus(plan.plan_id, plan.status)}
                          className={`text-[10px] px-2.5 py-1 rounded-md font-mono font-bold whitespace-nowrap transition-all ${
                            plan.status === 'COMPLETED'
                              ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/40 hover:bg-emerald-900/60'
                              : plan.status === 'IN_PROGRESS'
                              ? 'bg-cyan-950 text-cyan-400 border border-cyan-500/40 hover:bg-cyan-900/60'
                              : 'bg-slate-800 text-slate-400 border border-slate-700 hover:bg-slate-700'
                          }`}
                        >
                          {plan.status} ↻
                        </button>
                      </div>

                      <div className="flex flex-wrap items-center justify-between text-[10px] text-slate-400 font-mono pt-1 border-t border-slate-800/60">
                        <span>Tool: <b className="text-slate-300">{plan.pedagogy_mode}</b></span>
                        <span>Planned: <b className="text-slate-300">{plan.planned_hours}h</b></span>
                        <span>Actual: <b className="text-emerald-400">{plan.actual_hours}h</b></span>
                        {plan.completed_date && <span>Completed: {plan.completed_date}</span>}
                      </div>

                      {plan.notes && (
                        <div className="text-[11px] text-slate-400 italic bg-[#041026] p-2 rounded-lg">
                          📝 {plan.notes}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Create Lesson Plan Form */}
            <div className="p-5 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
              <h3 className="text-md font-semibold text-slate-100">Schedule Lecture Topic</h3>
              <p className="text-xs text-slate-400">Register a planned lecture according to Regulation 2023 syllabus.</p>

              <form onSubmit={handleCreatePlan} className="space-y-3">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-[11px] text-slate-400 mb-1">Course Code</label>
                    <select
                      value={newPlanForm.course_code}
                      onChange={(e) => setNewPlanForm({ ...newPlanForm, course_code: e.target.value })}
                      className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 font-mono"
                    >
                      <option value="EC3451">EC3451 (LIC)</option>
                      <option value="EC3491">EC3491 (CS)</option>
                      <option value="EC3352">EC3352 (DSD)</option>
                      <option value="EC3601">EC3601 (Embedded)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] text-slate-400 mb-1">Syllabus Unit</label>
                    <select
                      value={newPlanForm.unit_number}
                      onChange={(e) => setNewPlanForm({ ...newPlanForm, unit_number: parseInt(e.target.value) || 1 })}
                      className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 font-mono"
                    >
                      <option value="1">Unit I</option>
                      <option value="2">Unit II</option>
                      <option value="3">Unit III</option>
                      <option value="4">Unit IV</option>
                      <option value="5">Unit V</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-[11px] text-slate-400 mb-1">Topic Title</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Sallen-Key Low Pass Filter Synthesis"
                    value={newPlanForm.topic_title}
                    onChange={(e) => setNewPlanForm({ ...newPlanForm, topic_title: e.target.value })}
                    className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                  />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-[11px] text-slate-400 mb-1">Planned Hours</label>
                    <input
                      type="number"
                      step="0.5"
                      min="0.5"
                      max="10"
                      value={newPlanForm.planned_hours}
                      onChange={(e) => setNewPlanForm({ ...newPlanForm, planned_hours: parseFloat(e.target.value) || 1.0 })}
                      className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] text-slate-400 mb-1">Pedagogy Tool</label>
                    <select
                      value={newPlanForm.pedagogy_mode}
                      onChange={(e) => setNewPlanForm({ ...newPlanForm, pedagogy_mode: e.target.value })}
                      className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                    >
                      <option value="Chalk & Talk">Chalk & Talk</option>
                      <option value="Interactive PPT">Interactive PPT</option>
                      <option value="Wokwi Simulation">Wokwi Simulation</option>
                      <option value="Hardware Lab Bench">Hardware Lab Bench</option>
                      <option value="Flipped Classroom">Flipped Classroom</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-[11px] text-slate-400 mb-1">Course Outcome</label>
                    <select
                      value={newPlanForm.course_outcome}
                      onChange={(e) => setNewPlanForm({ ...newPlanForm, course_outcome: e.target.value })}
                      className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 font-mono"
                    >
                      <option value="CO1">CO1</option>
                      <option value="CO2">CO2</option>
                      <option value="CO3">CO3</option>
                      <option value="CO4">CO4</option>
                      <option value="CO5">CO5</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] text-slate-400 mb-1">Bloom's Taxonomy</label>
                    <select
                      value={newPlanForm.bloom_level}
                      onChange={(e) => setNewPlanForm({ ...newPlanForm, bloom_level: e.target.value })}
                      className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 font-mono"
                    >
                      <option value="K1-Remember">K1-Remember</option>
                      <option value="K2-Understand">K2-Understand</option>
                      <option value="K3-Apply">K3-Apply</option>
                      <option value="K4-Analyze">K4-Analyze</option>
                      <option value="K5-Evaluate">K5-Evaluate</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-[11px] text-slate-400 mb-1">Lecture Notes / Laboratory Ref</label>
                  <textarea
                    rows={2}
                    placeholder="Specific derivations, numerical assignments, or DSO benchmarks..."
                    value={newPlanForm.notes}
                    onChange={(e) => setNewPlanForm({ ...newPlanForm, notes: e.target.value })}
                    className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-[#00F0B5] text-slate-950 font-semibold text-xs hover:opacity-95"
                >
                  + Add Lesson Plan
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Lesson Templates */}
      {activeTab === 'templates' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-400">Pre-configured pedagogical sequences approved by MIT ECE Department</p>
            <span className="text-xs font-mono text-purple-300">{templates.length} Templates Available</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {templates.map((tpl) => (
              <div key={tpl.template_id} className="p-5 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between space-y-3">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00693E]/40 text-[#00F0B5] border border-[#00F0B5]/30">
                      {tpl.course_code} • {tpl.category}
                    </span>
                    <span className="text-xs font-mono text-amber-300">{tpl.suggested_duration_hours} Hours</span>
                  </div>

                  <h4 className="text-sm font-bold text-slate-100">{tpl.title}</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">{tpl.description}</p>

                  <div className="space-y-1 pt-1">
                    <span className="text-[10px] text-slate-500">Sample Topics Sequence:</span>
                    <ul className="text-[11px] text-slate-300 list-disc list-inside space-y-0.5">
                      {tpl.sample_topics.map((t, idx) => (
                        <li key={idx} className="line-clamp-1">{t}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {tpl.pedagogical_aids.map((aid, idx) => (
                      <span key={idx} className="text-[9px] px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">
                        🛠️ {aid}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
                  <div className="text-[10px] font-mono text-cyan-400">
                    CO: {tpl.co_mappings.join(', ')}
                  </div>
                  <button
                    onClick={() => cloneTemplateToPlan(tpl)}
                    className="px-3 py-1.5 rounded-lg bg-[#00F0B5]/15 hover:bg-[#00F0B5]/25 text-[#00F0B5] border border-[#00F0B5]/30 text-xs font-semibold"
                  >
                    Use Template →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: Digital Assignments */}
      {activeTab === 'assignments' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Published Assignments Ledger */}
          <div className="lg:col-span-2 space-y-4">
            <div className="p-5 rounded-2xl bg-[#041026] border border-slate-800 space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div>
                  <h3 className="text-md font-semibold text-slate-100">Continuous Assessment Assignments</h3>
                  <p className="text-xs text-slate-400">Distributed problem sets with weighted evaluation rubrics</p>
                </div>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/30">
                  {assignments.length} Published
                </span>
              </div>

              <div className="space-y-3">
                {assignments.map((asgn) => (
                  <div key={asgn.assignment_id} className="p-4 rounded-xl bg-[#020813] border border-slate-800 space-y-2.5">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-[#00F0B5]">
                          {asgn.course_code}
                        </span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                          Unit {asgn.unit_number}
                        </span>
                      </div>
                      <span className="text-[10px] font-mono text-amber-300">
                        Due: {asgn.due_date} • {asgn.total_marks} Marks
                      </span>
                    </div>

                    <h4 className="text-xs font-bold text-slate-100">{asgn.title}</h4>
                    <p className="text-xs text-slate-400">{asgn.instructions}</p>

                    <div className="space-y-1 bg-[#041026] p-2.5 rounded-lg border border-slate-800/80">
                      <div className="text-[10px] text-slate-500 font-mono">Assigned Problems:</div>
                      <ol className="text-[11px] text-slate-300 list-decimal list-inside space-y-1">
                        {asgn.questions.map((q, idx) => (
                          <li key={idx}>{q}</li>
                        ))}
                      </ol>
                    </div>

                    <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                      <span>Submissions: <b className="text-slate-200">{asgn.submissions_count} received</b></span>
                      <span>Average Score: <b className="text-emerald-400">{asgn.average_score}%</b></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Create Assignment Form */}
          <div className="p-5 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
            <h3 className="text-md font-semibold text-slate-100">Publish Assignment</h3>
            <p className="text-xs text-slate-400">Release problem set for student continuous evaluation.</p>

            <form onSubmit={handleCreateAssignment} className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[11px] text-slate-400 mb-1">Course Code</label>
                  <select
                    value={newAsgnForm.course_code}
                    onChange={(e) => setNewAsgnForm({ ...newAsgnForm, course_code: e.target.value })}
                    className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 font-mono"
                  >
                    <option value="EC3451">EC3451</option>
                    <option value="EC3491">EC3491</option>
                    <option value="EC3352">EC3352</option>
                    <option value="EC3601">EC3601</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[11px] text-slate-400 mb-1">Due Date</label>
                  <input
                    type="date"
                    value={newAsgnForm.due_date}
                    onChange={(e) => setNewAsgnForm({ ...newAsgnForm, due_date: e.target.value })}
                    className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-slate-200 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Assignment Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Sallen-Key Low Pass Filter Synthesis"
                  value={newAsgnForm.title}
                  onChange={(e) => setNewAsgnForm({ ...newAsgnForm, title: e.target.value })}
                  className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                />
              </div>

              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Instructions</label>
                <textarea
                  rows={2}
                  placeholder="Submission rules, LTspice format, KaTeX derivations..."
                  value={newAsgnForm.instructions}
                  onChange={(e) => setNewAsgnForm({ ...newAsgnForm, instructions: e.target.value })}
                  className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded-xl bg-[#00F0B5]/20 hover:bg-[#00F0B5]/30 text-[#00F0B5] border border-[#00F0B5]/40 text-xs font-semibold"
              >
                + Publish to Students
              </button>
            </form>
          </div>
        </div>
      )}

      {/* TAB 4: Evaluation & Feedback */}
      {activeTab === 'feedback' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Graded Reports */}
          <div className="lg:col-span-2 space-y-4">
            <div className="p-5 rounded-2xl bg-[#041026] border border-slate-800 space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div>
                  <h3 className="text-md font-semibold text-slate-100">Graded Submissions & Rubric Feedback</h3>
                  <p className="text-xs text-slate-400">Continuous assessment reports verified by MIT faculty</p>
                </div>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-500/30">
                  {feedbacks.length} Evaluated
                </span>
              </div>

              <div className="space-y-3">
                {feedbacks.map((fb) => (
                  <div key={fb.feedback_id} className="p-4 rounded-xl bg-[#020813] border border-slate-800 space-y-2.5">
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-xs font-bold text-slate-100">{fb.student_name}</span>
                        <span className="text-[11px] font-mono text-[#00F0B5] ml-2">({fb.student_id})</span>
                      </div>
                      <div className="text-sm font-mono font-bold text-emerald-400">
                        {fb.marks_obtained} / {fb.total_marks} Marks
                      </div>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed bg-[#041026] p-3 rounded-xl border border-slate-800/80">
                      “{fb.qualitative_feedback}”
                    </p>

                    {fb.rubric_scores && (
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
                        {Object.entries(fb.rubric_scores).map(([k, v]) => (
                          <div key={k} className="p-2 rounded-lg bg-[#020813] border border-slate-800 text-[10px] font-mono">
                            <div className="text-slate-500 truncate">{k.replace(/_/g, ' ')}</div>
                            <div className="text-slate-200 font-bold">{v} pts</div>
                          </div>
                        ))}
                      </div>
                    )}

                    <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                      <span>Evaluator: <b className="text-slate-300">{fb.evaluated_by}</b></span>
                      <span className="text-emerald-400">Status: {fb.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Record Grade Form */}
          <div className="p-5 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
            <h3 className="text-md font-semibold text-slate-100">Grade Student Submission</h3>
            <p className="text-xs text-slate-400">Award marks and publish qualitative evaluation feedback.</p>

            <form onSubmit={handleRecordFeedback} className="space-y-3">
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Student Roll Number</label>
                <input
                  type="text"
                  required
                  value={newFbForm.student_id}
                  onChange={(e) => setNewFbForm({ ...newFbForm, student_id: e.target.value })}
                  className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 font-mono"
                />
              </div>

              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Marks Obtained (out of 100)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={newFbForm.marks_obtained}
                  onChange={(e) => setNewFbForm({ ...newFbForm, marks_obtained: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 font-mono"
                />
              </div>

              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Faculty Qualitative Review</label>
                <textarea
                  rows={3}
                  required
                  placeholder="Enter detailed review regarding derivations, circuit simulation, and error margins..."
                  value={newFbForm.qualitative_feedback}
                  onChange={(e) => setNewFbForm({ ...newFbForm, qualitative_feedback: e.target.value })}
                  className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-[#00F0B5] text-slate-950 font-semibold text-xs hover:opacity-95"
              >
                Save Evaluation Report
              </button>
            </form>
          </div>
        </div>
      )}

      {/* TAB 5: Department Minutes */}
      {activeTab === 'meetings' && (
        <div className="space-y-4">
          <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-md font-semibold text-slate-100">Department Meeting Minutes (MoM)</h3>
                <p className="text-xs text-slate-400">Department of Electronics Engineering • MIT Campus Faculty Council</p>
              </div>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-500/30">
                Official Department Ledger
              </span>
            </div>

            <div className="space-y-4">
              {meetings.map((m) => (
                <div key={m.meeting_id} className="p-5 rounded-xl bg-[#020813] border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-bold text-slate-100">{m.meeting_title}</h4>
                    <span className="text-xs font-mono text-[#00F0B5]">{m.meeting_date}</span>
                  </div>

                  <div className="text-xs text-slate-400">
                    Chairperson: <span className="text-slate-200 font-semibold">{m.chairperson}</span>
                  </div>

                  <div className="space-y-1">
                    <span className="text-[11px] font-mono text-slate-500">Key Agenda Items:</span>
                    <ol className="text-xs text-slate-300 list-decimal list-inside space-y-0.5">
                      {m.agenda_items.map((ag, idx) => (
                        <li key={idx}>{ag}</li>
                      ))}
                    </ol>
                  </div>

                  <div className="space-y-1 bg-[#041026] p-3 rounded-xl border border-slate-800">
                    <span className="text-[11px] font-mono text-emerald-400 font-bold">Key Decisions Resolved:</span>
                    <ul className="text-xs text-slate-300 list-disc list-inside space-y-0.5">
                      {m.key_decisions.map((dec, idx) => (
                        <li key={idx}>{dec}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="space-y-1.5 pt-1">
                    <span className="text-[11px] font-mono text-amber-300 font-bold">Assigned Action Items:</span>
                    <div className="space-y-1.5">
                      {m.action_items.map((act, idx) => (
                        <div key={idx} className="p-2.5 rounded-lg bg-[#020813] border border-slate-800 flex items-center justify-between text-xs">
                          <div>
                            <div className="text-slate-200 font-medium">{act.task}</div>
                            <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                              Assignee: <b className="text-slate-300">{act.assignee}</b> • Deadline: {act.deadline}
                            </div>
                          </div>
                          <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                            act.status === 'COMPLETED'
                              ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30'
                              : act.status === 'IN_PROGRESS'
                              ? 'bg-cyan-950 text-cyan-400 border border-cyan-500/30'
                              : 'bg-amber-950 text-amber-400 border border-amber-500/30'
                          }`}>
                            {act.status}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
