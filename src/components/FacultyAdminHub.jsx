import React, { useState } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Phase O: Faculty & Administrative Management (Features 351–360)
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 *
 * Features:
 *   - Feature 351: Faculty Dashboard (Teaching Load, Student Strength, Quick Stats)
 *   - Feature 352: Student Performance Analytics (GPA distribution, Internals, At-Risk Alert)
 *   - Feature 353: Assignment Grading Suite (Rubric-based evaluation, Grade release)
 *   - Feature 354: Attendance Management Portal (Session attendance, 75% cutoff rule)
 *   - Feature 355: Course Material Upload Manager (Notes, Lab manuals, Question banks)
 *   - Feature 356: Announcement Broadcast System (Audience targeting, Urgent broadcasts)
 *   - Feature 357: Student Progress Report Generator (AU Reg 2023 Dossier, Grades O to U)
 *   - Feature 358: Department Notice Board (Accreditation NBA/NAAC, Faculty circulars)
 *   - Feature 359: Timetable & Schedule Manager (7-period slots, Lab rooms, Faculty in-charge)
 *   - Feature 360: Faculty Office Hours Scheduler (In-person & Virtual booking slots)
 * Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
 * ========================================================================================
 */

// Initial Seed Faculty Courses (Feature 351)
const SEED_COURSES = [
  {
    id: "c1",
    code: "EC3552",
    name: "VLSI and Chip Design",
    semester: 5,
    enrolled: 64,
    avg_internal: 44.8,
    pass_pct: 94.2,
    at_risk: 2
  },
  {
    id: "c2",
    code: "EC3451",
    name: "Linear Integrated Circuits",
    semester: 4,
    enrolled: 68,
    avg_internal: 42.1,
    pass_pct: 91.5,
    at_risk: 3
  },
  {
    id: "c3",
    code: "EC3501",
    name: "Wireless Communication",
    semester: 5,
    enrolled: 64,
    avg_internal: 43.6,
    pass_pct: 95.0,
    at_risk: 1
  },
  {
    id: "c4",
    code: "EC3711",
    name: "Embedded Systems Laboratory",
    semester: 5,
    enrolled: 64,
    avg_internal: 47.5,
    pass_pct: 98.4,
    at_risk: 0
  }
];

// Seed Students with At-Risk Indicators (Feature 352 & 354)
const SEED_STUDENTS = [
  {
    roll: "2023MITEC042",
    name: "Ashok Kumar A",
    course: "EC3552",
    i1: 49, i2: 50, i3: 50,
    assignment: 98,
    attendance: 98.0,
    cgpa: 9.42,
    status: "EXEMPLARY"
  },
  {
    roll: "2023MITEC055",
    name: "Kavitha R",
    course: "EC3552",
    i1: 46, i2: 48, i3: 47,
    assignment: 94,
    attendance: 94.5,
    cgpa: 9.15,
    status: "EXEMPLARY"
  },
  {
    roll: "2023MITEC010",
    name: "Dinesh S",
    course: "EC3552",
    i1: 40, i2: 42, i3: 41,
    assignment: 85,
    attendance: 88.0,
    cgpa: 8.20,
    status: "NORMAL"
  },
  {
    roll: "2023MITEC088",
    name: "Ramesh K",
    course: "EC3552",
    i1: 34, i2: 36, i3: 35,
    assignment: 72,
    attendance: 76.5,
    cgpa: 6.85,
    status: "CONDONATION_ALERT"
  },
  {
    roll: "2023MITEC099",
    name: "Arun V",
    course: "EC3552",
    i1: 22, i2: 24, i3: 20,
    assignment: 45,
    attendance: 68.0,
    cgpa: 5.92,
    status: "AT_RISK_DEBARRED"
  }
];

// Seed Submissions Queue (Feature 353)
const SEED_SUBMISSIONS = [
  {
    id: "sub_01",
    student_roll: "2023MITEC042",
    student_name: "Ashok Kumar A",
    title: "Lab 4: Cadence Innovus Floorplan & Static Timing Slack Closure",
    course: "EC3552",
    submitted: "2026-11-05",
    circuit: 29, sim: 30, viva: 20, report: 20,
    total: 99,
    feedback: "Exceptional timing closure on 28nm corner. Buffer delay sizing is optimal.",
    graded: true
  },
  {
    id: "sub_02",
    student_roll: "2023MITEC055",
    student_name: "Kavitha R",
    title: "Lab 4: Cadence Innovus Floorplan & Static Timing Slack Closure",
    course: "EC3552",
    submitted: "2026-11-05",
    circuit: 28, sim: 28, viva: 19, report: 19,
    total: 94,
    feedback: "Clean CTS synthesis. Clock skew within 45ps bound.",
    graded: true
  },
  {
    id: "sub_03",
    student_roll: "2023MITEC010",
    student_name: "Dinesh S",
    title: "Lab 4: Cadence Innovus Floorplan & Static Timing Slack Closure",
    course: "EC3552",
    submitted: "2026-11-06",
    circuit: 24, sim: 25, viva: 16, report: 17,
    total: 82,
    feedback: "Minor hold violation on FF_3 path. Insert delay cells near capture pin.",
    graded: false
  }
];

// Seed Course Materials (Feature 355)
const SEED_MATERIALS = [
  { id: "mat_01", title: "EC3552 VLSI Design - Lecture Notes Module 1 to 5", category: "NOTES", sem: 5, url: "#" },
  { id: "mat_02", title: "Cadence EDA Lab Manual: RTL-to-GDSII Synthesis Flow", category: "LAB_MANUAL", sem: 5, url: "#" },
  { id: "mat_03", title: "Anna University End-Semester Model Question Paper (Reg 2023)", category: "QUESTION_BANK", sem: 5, url: "#" },
  { id: "mat_04", title: "LTspice Simulation Decks: CMOS Inverter & Transmission Gates", category: "SIM_TEMPLATE", sem: 4, url: "#" }
];

// Seed Timetable (Feature 359)
const SEED_TIMETABLE = [
  { period: 1, time: "08:30 - 09:20", mon: "EC3552 (LH1)", tue: "EC3501 (LH1)", wed: "VLSI CAD Lab", thu: "EC3552 (LH1)", fri: "EC3501 (LH1)" },
  { period: 2, time: "09:20 - 10:10", mon: "EC3501 (LH1)", tue: "EC3552 (LH1)", wed: "VLSI CAD Lab", thu: "EC3451 (LH2)", fri: "EC3552 (LH1)" },
  { period: 3, time: "10:30 - 11:20", mon: "EC3451 (LH2)", tue: "EC3551 (RF Lab)", wed: "VLSI CAD Lab", thu: "EC3501 (LH1)", fri: "EC3451 (LH2)" },
  { period: 4, time: "11:20 - 12:10", mon: "EC3351 (LH2)", tue: "Library/Seminar", wed: "Tutorial", thu: "EC3551 (LH1)", fri: "HOD Mentoring" },
  { period: 5, time: "13:30 - 16:30", mon: "Embedded Lab 304", tue: "Mini Project Lab", wed: "Sports/Club", thu: "Microwave Lab", fri: "Industry Guest Lec" }
];

// Seed Office Hours (Feature 360)
const SEED_OFFICE_HOURS = [
  { id: "slot_01", day: "Tuesdays", time: "14:00 - 15:30 IST", mode: "In-Person", venue: "Room ECE-302 (Prof Office)", status: "AVAILABLE", bookedBy: null },
  { id: "slot_02", day: "Thursdays", time: "15:30 - 17:00 IST", mode: "In-Person", venue: "Room ECE-302 (Prof Office)", status: "BOOKED", bookedBy: "Ashok Kumar A (2023MITEC042)" },
  { id: "slot_03", day: "Fridays", time: "11:00 - 12:30 IST", mode: "Virtual (Jitsi)", venue: "meet.jit.si/voltcore-prof-nirmal", status: "AVAILABLE", bookedBy: null }
];

export default function FacultyAdminHub() {
  const [activeTab, setActiveTab] = useState('dashboard');

  // Course state
  const [courses] = useState(SEED_COURSES);
  const [selectedCourseCode, setSelectedCourseCode] = useState('EC3552');

  // Student analytics & At-risk state
  const [students, setStudents] = useState(SEED_STUDENTS);

  // Submissions & grading state (Feature 353)
  const [submissions, setSubmissions] = useState(SEED_SUBMISSIONS);
  const [gradingSubId, setGradingSubId] = useState('sub_03');
  const [cScore, setCScore] = useState(25);
  const [sScore, setSScore] = useState(26);
  const [vScore, setVScore] = useState(17);
  const [rScore, setRScore] = useState(18);
  const [feedbackInput, setFeedbackInput] = useState('Good testbench coverage. Ensure clock domain crossing synchronizers have ASYNC_REG attributes.');

  // Attendance state (Feature 354)
  const [attendanceRecords, setAttendanceRecords] = useState(SEED_STUDENTS.map(s => ({
    roll: s.roll,
    name: s.name,
    present: true,
    pct: s.attendance
  })));

  // Course Materials state (Feature 355)
  const [materials, setMaterials] = useState(SEED_MATERIALS);
  const [newMatTitle, setNewMatTitle] = useState('');
  const [newMatCategory, setNewMatCategory] = useState('NOTES');

  // Announcements state (Feature 356)
  const [announcements, setAnnouncements] = useState([
    {
      id: "ann_1",
      title: "Lab Assessment II Practical Viva Voce Schedule",
      audience: "B.E. ECE Semester V",
      priority: "URGENT",
      date: "2026-11-06",
      body: "External viva voce for EC3552 and EC3711 will be held on Nov 19 & 20. Hall tickets and lab records must be verified."
    }
  ]);
  const [newAnnTitle, setNewAnnTitle] = useState('');
  const [newAnnAudience, setNewAnnAudience] = useState('B.E. ECE Semester V');
  const [newAnnPriority, setNewAnnPriority] = useState('URGENT');
  const [newAnnBody, setNewAnnBody] = useState('');

  // Office Hours state (Feature 360)
  const [officeSlots, setOfficeSlots] = useState(SEED_OFFICE_HOURS);

  // Progress Dossier Generator target (Feature 357)
  const [selectedStudentRoll, setSelectedStudentRoll] = useState('2023MITEC042');

  // Instructor CMS Studio & Override States (Phase 9)
  const [cmsCourseCode, setCmsCourseCode] = useState('EC3701');
  const [cmsCourseName, setCmsCourseName] = useState('Advanced Embedded Systems Architecture');
  const [cmsSemester, setCmsSemester] = useState(5);
  const [cmsCredits, setCmsCredits] = useState(4);
  const [cmsPublishedList, setCmsPublishedList] = useState([]);

  const [overrideReportId, setOverrideReportId] = useState('REP_STM32_01');
  const [overrideVerdict, setOverrideVerdict] = useState('APPROVED');
  const [overrideScore, setOverrideScore] = useState(96);
  const [overrideNotes, setOverrideNotes] = useState('Verified oscilloscope captures show zero setup violations.');

  const [questionQid, setQuestionQid] = useState('Q_GATE_01');
  const [questionText, setQuestionText] = useState('What ARM instruction guarantees SRAM cache coherency prior to circular DMA trigger?');
  const [questionAns, setQuestionAns] = useState('C');
  const [questionMarks, setQuestionMarks] = useState(2);
  const [questionCO, setQuestionCO] = useState('CO4');
  const [questionBloom, setQuestionBloom] = useState('Level 4: Analyze');

  const handlePublishCourse = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/cms/course/publish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User-Role': 'Faculty' },
        body: JSON.stringify({
          course_code: cmsCourseCode,
          course_name: cmsCourseName,
          semester: cmsSemester,
          credits: cmsCredits,
          department: 'Department of Electronics Engineering'
        })
      });
      const data = await res.json();
      if (data.status === 'SUCCESS') {
        alert(`Course ${cmsCourseCode} published successfully!`);
        setCmsPublishedList(prev => [data, ...prev]);
      } else {
        alert(`Course publishing status: ${data.status}`);
      }
    } catch {
      alert(`Course ${cmsCourseCode} published locally.`);
      setCmsPublishedList(prev => [{ course_code: cmsCourseCode, course_name: cmsCourseName, credits: cmsCredits }, ...prev]);
    }
  };

  const handleOverrideReview = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/cms/report/review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User-Role': 'Faculty' },
        body: JSON.stringify({
          report_id: overrideReportId,
          faculty_override_verdict: overrideVerdict,
          adjusted_score: overrideScore,
          faculty_notes: overrideNotes
        })
      });
      const data = await res.json();
      if (data.status === 'SUCCESS') {
        alert(`Report ${overrideReportId} override committed! Verdict: ${overrideVerdict} (${overrideScore}/100)`);
      }
    } catch {
      alert(`Report ${overrideReportId} override committed locally.`);
    }
  };

  const handleAddQuestion = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/cms/question_bank/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User-Role': 'Faculty' },
        body: JSON.stringify({
          question_id: questionQid,
          course_code: cmsCourseCode,
          section: 'sec_embedded',
          course_outcome: questionCO,
          bloom_level: questionBloom,
          marks: questionMarks,
          question_type: 'MCQ',
          question_text: questionText,
          correct_answer: questionAns
        })
      });
      const data = await res.json();
      if (data.status === 'SUCCESS') {
        alert(`Question ${questionQid} added to examination bank!`);
      }
    } catch {
      alert(`Question ${questionQid} added locally.`);
    }
  };

  // Handle grade submission
  const handleSaveGrade = (e) => {
    e.preventDefault();
    const total = cScore + sScore + vScore + rScore;
    setSubmissions(subs => subs.map(sub => {
      if (sub.id === gradingSubId) {
        return {
          ...sub,
          circuit: cScore,
          sim: sScore,
          viva: vScore,
          report: rScore,
          total: total,
          feedback: feedbackInput,
          graded: true
        };
      }
      return sub;
    }));
    alert(`Grade saved! Total Rubric Score: ${total}/100. Released to student portal.`);
  };

  // Toggle single attendance session
  const toggleAttendance = (roll) => {
    setAttendanceRecords(records => records.map(r => {
      if (r.roll === roll) {
        const nextPresent = !r.present;
        return {
          ...r,
          present: nextPresent,
          pct: nextPresent ? Math.min(100, r.pct + 1.5) : Math.max(0, r.pct - 2.5)
        };
      }
      return r;
    }));
  };

  // Upload Material
  const handleUploadMaterial = (e) => {
    e.preventDefault();
    if (!newMatTitle.trim()) return;
    const newMat = {
      id: `mat_${Date.now()}`,
      title: newMatTitle,
      category: newMatCategory,
      sem: 5,
      url: "#"
    };
    setMaterials([newMat, ...materials]);
    setNewMatTitle('');
    alert("Course material published to student portal!");
  };

  // Broadcast announcement
  const handleBroadcast = (e) => {
    e.preventDefault();
    if (!newAnnTitle.trim() || !newAnnBody.trim()) return;
    const newAnn = {
      id: `ann_${Date.now()}`,
      title: newAnnTitle,
      audience: newAnnAudience,
      priority: newAnnPriority,
      date: new Date().toISOString().split('T')[0],
      body: newAnnBody
    };
    setAnnouncements([newAnn, ...announcements]);
    setNewAnnTitle('');
    setNewAnnBody('');
    alert("Official administrative notice broadcasted successfully!");
  };

  // Book Office slot
  const handleBookSlot = (slotId) => {
    setOfficeSlots(slots => slots.map(s => {
      if (s.id === slotId) {
        return {
          ...s,
          status: "BOOKED",
          bookedBy: "Ashok Kumar A (2023MITEC042)"
        };
      }
      return s;
    }));
  };

  // Selected Student for Dossier (Feature 357)
  const targetStudent = students.find(s => s.roll === selectedStudentRoll) || students[0];
  const internalAvg = ((targetStudent.i1 + targetStudent.i2 + targetStudent.i3) / 3.0).toFixed(1);
  const totalScoreCalc = Math.round((parseFloat(internalAvg) * 2.0) * 0.70 + targetStudent.assignment * 0.30);
  const getLetterGrade = (score) => {
    if (score >= 91) return { grade: "O", desc: "OUTSTANDING (GP: 10.0)" };
    if (score >= 81) return { grade: "A+", desc: "EXCELLENT (GP: 9.0)" };
    if (score >= 71) return { grade: "A", desc: "VERY GOOD (GP: 8.0)" };
    if (score >= 61) return { grade: "B+", desc: "GOOD (GP: 7.0)" };
    if (score >= 50) return { grade: "B", desc: "AVERAGE (GP: 6.0)" };
    return { grade: "U", desc: "RE-APPEARANCE (GP: 0.0)" };
  };
  const gradeInfo = getLetterGrade(totalScoreCalc);

  return (
    <div className="faculty-admin-hub space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900/80 border border-teal-500/30 rounded-2xl p-6 backdrop-blur-md shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="px-3 py-1 text-xs font-bold rounded-full bg-teal-500/20 text-teal-300 border border-teal-500/40">
                PHASE O • FACULTY & ADMIN MANAGEMENT
              </span>
              <span className="px-3 py-1 text-xs font-bold rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/40">
                MIT CAMPUS ECE
              </span>
              <span className="px-3 py-1 text-xs font-bold rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                ANNA UNIV REG 2023
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Faculty & Academic Administrative Management Hub
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Madras Institute of Technology Campus • Department of Electronics Engineering
            </p>
          </div>

          <div className="flex items-center gap-3 bg-slate-800/80 border border-slate-700/60 p-3 rounded-xl">
            <div className="text-right">
              <div className="text-xs text-slate-400">Faculty In-Charge</div>
              <div className="text-sm font-black text-teal-300">Dr. P. Nirmal, Ph.D.</div>
              <div className="text-[10px] text-slate-400">Professor & Head • VLSI CoE</div>
            </div>
            <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-teal-500 to-blue-600 flex items-center justify-center text-white font-bold text-sm shadow-lg">
              PN
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 mt-6 border-t border-slate-800 pt-4">
          {[
            { id: 'dashboard', label: 'Faculty Dashboard', icon: '📊' },
            { id: 'analytics_at_risk', label: 'Performance & At-Risk Radar', icon: '🎯' },
            { id: 'grading_suite', label: 'Assignment Grading Suite', icon: '📝' },
            { id: 'attendance_portal', label: 'Attendance Management', icon: '📋' },
            { id: 'progress_dossier', label: 'Student Progress Dossier', icon: '📑' },
            { id: 'admin_schedule', label: 'Timetable, Materials & Office Hours', icon: '🗓️' },
            { id: 'instructor_cms', label: 'Instructor CMS & Overrides', icon: '⚡' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-2 ${
                activeTab === tab.id
                  ? 'bg-teal-500 text-slate-950 font-bold shadow-lg shadow-teal-500/20'
                  : 'bg-slate-800/60 text-slate-300 hover:bg-slate-700 hover:text-white border border-slate-700/40'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* =========================================================================
          TAB 1: FACULTY DASHBOARD (Feature 351)
      ========================================================================= */}
      {activeTab === 'dashboard' && (
        <div className="space-y-6">
          {/* Quick Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-slate-400 uppercase tracking-wider">Assigned Courses</div>
              <div className="text-2xl font-black text-teal-300 mt-1">4 Theory / Lab</div>
              <div className="text-[11px] text-slate-400 mt-1">Semesters IV & V (Reg 2023)</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-slate-400 uppercase tracking-wider">Total Enrolled Students</div>
              <div className="text-2xl font-black text-blue-400 mt-1">260 Undergrads</div>
              <div className="text-[11px] text-slate-400 mt-1">Average Attendance: 92.4%</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-slate-400 uppercase tracking-wider">Pending Grading</div>
              <div className="text-2xl font-black text-amber-400 mt-1">
                {submissions.filter(s => !s.graded).length} Submissions
              </div>
              <div className="text-[11px] text-slate-400 mt-1">EC3552 Lab 4 Cadence EDA</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-slate-400 uppercase tracking-wider">Next Evaluation</div>
              <div className="text-2xl font-black text-emerald-400 mt-1">Nov 18, 2026</div>
              <div className="text-[11px] text-slate-400 mt-1">Practical Viva-Voce (ACOE)</div>
            </div>
          </div>

          {/* Assigned Courses Table */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-white">Course Workload & Pass Statistics</h2>
                <p className="text-xs text-slate-400">Department of Electronics Engineering, MIT Campus</p>
              </div>
              <span className="px-3 py-1 bg-teal-500/20 text-teal-300 border border-teal-500/40 text-xs font-bold rounded-full">
                AY 2026-2027 Odd Semester
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="py-2.5 px-3">Course Code</th>
                    <th className="py-2.5 px-3">Course Title</th>
                    <th className="py-2.5 px-3">Semester</th>
                    <th className="py-2.5 px-3">Strength</th>
                    <th className="py-2.5 px-3">Avg Internals (50)</th>
                    <th className="py-2.5 px-3">Pass %</th>
                    <th className="py-2.5 px-3">At-Risk</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {courses.map(c => (
                    <tr key={c.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3 px-3 font-mono font-bold text-teal-400">{c.code}</td>
                      <td className="py-3 px-3 text-white font-medium">{c.name}</td>
                      <td className="py-3 px-3 text-slate-300">Sem {c.semester}</td>
                      <td className="py-3 px-3 text-slate-300">{c.enrolled}</td>
                      <td className="py-3 px-3 font-mono text-cyan-300">{c.avg_internal} / 50</td>
                      <td className="py-3 px-3 font-mono text-emerald-400">{c.pass_pct}%</td>
                      <td className="py-3 px-3">
                        <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                          c.at_risk > 0 ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-emerald-500/20 text-emerald-300'
                        }`}>
                          {c.at_risk} Students
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 2: STUDENT PERFORMANCE ANALYTICS & AT-RISK RADAR (Feature 352)
      ========================================================================= */}
      {activeTab === 'analytics_at_risk' && (
        <div className="space-y-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <span>🎯</span> Student Performance Radar & Early Warning Detection
                </h2>
                <p className="text-xs text-slate-400">
                  Threshold: CGPA &lt; 6.50 or Attendance &lt; 75.0% automatically flagged for remedial mentoring
                </p>
              </div>

              <select
                value={selectedCourseCode}
                onChange={e => setSelectedCourseCode(e.target.value)}
                className="bg-slate-800 border border-slate-700 text-xs rounded-lg px-3 py-1.5 text-white"
              >
                {courses.map(c => (
                  <option key={c.id} value={c.code}>{c.code} - {c.name}</option>
                ))}
              </select>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="py-2.5 px-3">Roll No</th>
                    <th className="py-2.5 px-3">Student Name</th>
                    <th className="py-2.5 px-3">IAT 1</th>
                    <th className="py-2.5 px-3">IAT 2</th>
                    <th className="py-2.5 px-3">IAT 3</th>
                    <th className="py-2.5 px-3">Assignment</th>
                    <th className="py-2.5 px-3">Attendance</th>
                    <th className="py-2.5 px-3">CGPA</th>
                    <th className="py-2.5 px-3">Academic Radar</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {students.map(s => {
                    const isAtRisk = s.attendance < 75.0 || s.cgpa < 6.50;
                    return (
                      <tr key={s.roll} className={`hover:bg-slate-800/40 transition ${isAtRisk ? 'bg-rose-950/10' : ''}`}>
                        <td className="py-3 px-3 font-mono font-bold text-teal-400">{s.roll}</td>
                        <td className="py-3 px-3 text-white font-medium">{s.name}</td>
                        <td className="py-3 px-3 font-mono text-slate-300">{s.i1}</td>
                        <td className="py-3 px-3 font-mono text-slate-300">{s.i2}</td>
                        <td className="py-3 px-3 font-mono text-slate-300">{s.i3}</td>
                        <td className="py-3 px-3 font-mono text-cyan-300">{s.assignment}%</td>
                        <td className="py-3 px-3 font-mono">
                          <span className={s.attendance < 75.0 ? 'text-rose-400 font-bold' : 'text-slate-300'}>
                            {s.attendance}%
                          </span>
                        </td>
                        <td className="py-3 px-3 font-mono">
                          <span className={s.cgpa < 6.50 ? 'text-rose-400 font-bold' : 'text-slate-300'}>
                            {s.cgpa.toFixed(2)}
                          </span>
                        </td>
                        <td className="py-3 px-3">
                          {isAtRisk ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">
                              ⚠️ AT-RISK (MENTORING REQ)
                            </span>
                          ) : s.attendance < 80.0 ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                              ⚠️ CONDONATION REQUIRED
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300">
                              ✓ SATISFACTORY
                            </span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 3: ASSIGNMENT GRADING SUITE (Feature 353)
      ========================================================================= */}
      {activeTab === 'grading_suite' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Submissions List */}
          <div className="space-y-3">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Submissions Queue</h2>
            {submissions.map(sub => (
              <div
                key={sub.id}
                onClick={() => setGradingSubId(sub.id)}
                className={`p-3.5 rounded-xl border cursor-pointer transition ${
                  gradingSubId === sub.id
                    ? 'bg-teal-500/20 border-teal-500 text-white'
                    : 'bg-slate-900/80 border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono text-xs font-bold text-teal-400">{sub.student_roll}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    sub.graded ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'
                  }`}>
                    {sub.graded ? `GRADED (${sub.total}/100)` : 'PENDING'}
                  </span>
                </div>
                <div className="text-xs font-semibold text-white">{sub.student_name}</div>
                <div className="text-[11px] text-slate-400 truncate mt-0.5">{sub.title}</div>
              </div>
            ))}
          </div>

          {/* 4-Pillar ECE Rubric Evaluation Form */}
          <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="border-b border-slate-800 pb-3">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <span>📝</span> 4-Pillar ECE Laboratory Rubric Evaluation
              </h2>
              <p className="text-xs text-slate-400">
                Formula: Circuit (30) + Simulation (30) + Viva-Voce (20) + Report (20) = 100 Max
              </p>
            </div>

            <form onSubmit={handleSaveGrade} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                    <span>Circuit Architecture & Design (30)</span>
                    <span className="font-bold text-teal-400">{cScore} / 30</span>
                  </div>
                  <input
                    type="range" min="0" max="30" value={cScore}
                    onChange={e => setCScore(parseInt(e.target.value))}
                    className="w-full accent-teal-400"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                    <span>Simulation & Timing Accuracy (30)</span>
                    <span className="font-bold text-blue-400">{sScore} / 30</span>
                  </div>
                  <input
                    type="range" min="0" max="30" value={sScore}
                    onChange={e => setSScore(parseInt(e.target.value))}
                    className="w-full accent-blue-400"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                    <span>Viva-Voce & Theoretical Rigor (20)</span>
                    <span className="font-bold text-purple-400">{vScore} / 20</span>
                  </div>
                  <input
                    type="range" min="0" max="20" value={vScore}
                    onChange={e => setVScore(parseInt(e.target.value))}
                    className="w-full accent-purple-400"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                    <span>Documentation & Report (20)</span>
                    <span className="font-bold text-emerald-400">{rScore} / 20</span>
                  </div>
                  <input
                    type="range" min="0" max="20" value={rScore}
                    onChange={e => setRScore(parseInt(e.target.value))}
                    className="w-full accent-emerald-400"
                  />
                </div>
              </div>

              {/* Live Rubric Total Display */}
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="text-xs text-slate-400">Total Awarded Score</div>
                  <div className="text-2xl font-black text-teal-400">{cScore + sScore + vScore + rScore} <span className="text-xs text-slate-400">/ 100</span></div>
                </div>
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-teal-500/20 text-teal-300 border border-teal-500/40">
                  {cScore + sScore + vScore + rScore >= 90 ? 'OUTSTANDING (GRADE O)' : 'FIRST CLASS (GRADE A)'}
                </span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Faculty Technical Feedback</label>
                <textarea
                  value={feedbackInput}
                  onChange={e => setFeedbackInput(e.target.value)}
                  rows={3}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-teal-500"
                  required
                />
              </div>

              <button
                type="submit"
                className="w-full py-2.5 bg-gradient-to-r from-teal-500 to-blue-600 text-slate-950 font-bold rounded-lg text-xs hover:from-teal-400 hover:to-blue-500 transition shadow-lg shadow-teal-500/20"
              >
                Commit & Release Grade to Student Record
              </button>
            </form>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 4: ATTENDANCE MANAGEMENT PORTAL (Feature 354)
      ========================================================================= */}
      {activeTab === 'attendance_portal' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <span>📋</span> Daily Session Attendance Marker (EC3552 - Period 1)
              </h2>
              <p className="text-xs text-slate-400">
                Anna University Regulation 2023: Minimum 75% attendance mandatory for semester exam hall ticket
              </p>
            </div>

            <button
              onClick={() => alert("Today's session attendance synchronized with Controller of Examinations portal.")}
              className="px-4 py-2 bg-teal-500 text-slate-950 font-bold rounded-lg text-xs hover:bg-teal-400 transition"
            >
              Sync Session with ACOE
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-2.5 px-3">Roll Number</th>
                  <th className="py-2.5 px-3">Student Name</th>
                  <th className="py-2.5 px-3">Cumulative %</th>
                  <th className="py-2.5 px-3">AU Reg 2023 Status</th>
                  <th className="py-2.5 px-3 text-right">Today's Mark</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {attendanceRecords.map(rec => (
                  <tr key={rec.roll} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-3 font-mono font-bold text-teal-400">{rec.roll}</td>
                    <td className="py-3 px-3 text-white font-medium">{rec.name}</td>
                    <td className="py-3 px-3 font-mono font-bold text-slate-200">{rec.pct.toFixed(1)}%</td>
                    <td className="py-3 px-3">
                      {rec.pct >= 80.0 ? (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300">
                          ✓ ELIGIBLE (SATISFACTORY)
                        </span>
                      ) : rec.pct >= 75.0 ? (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300">
                          ⚠️ CONDONATION REQUIRED
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">
                          🛑 DEBARRED (SHORTAGE &lt;75%)
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => toggleAttendance(rec.roll)}
                        className={`px-3 py-1 rounded text-xs font-bold transition ${
                          rec.present ? 'bg-emerald-500 text-slate-950' : 'bg-rose-500 text-white'
                        }`}
                      >
                        {rec.present ? 'PRESENT' : 'ABSENT'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 5: STUDENT PROGRESS REPORT GENERATOR (Feature 357)
      ========================================================================= */}
      {activeTab === 'progress_dossier' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Student Selector */}
          <div className="space-y-3">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Select Student</h2>
            {students.map(s => (
              <div
                key={s.roll}
                onClick={() => setSelectedStudentRoll(s.roll)}
                className={`p-3 rounded-xl border cursor-pointer transition ${
                  selectedStudentRoll === s.roll
                    ? 'bg-teal-500/20 border-teal-500 text-white'
                    : 'bg-slate-900/80 border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                <div className="font-mono text-xs font-bold text-teal-400">{s.roll}</div>
                <div className="text-xs font-semibold text-white">{s.name}</div>
                <div className="text-[11px] text-slate-400">CGPA: {s.cgpa.toFixed(2)} • Att: {s.attendance}%</div>
              </div>
            ))}
          </div>

          {/* Progress Card Dossier */}
          <div className="lg:col-span-2 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
              <div>
                <div className="text-xs font-bold text-teal-400 uppercase tracking-widest">
                  ANNA UNIVERSITY • MIT CAMPUS (REGULATION 2023)
                </div>
                <h2 className="text-xl font-black text-white mt-0.5">{targetStudent.name}</h2>
                <div className="text-xs text-slate-400 font-mono">
                  Roll: <strong className="text-white">{targetStudent.roll}</strong> • Department of Electronics Engineering
                </div>
              </div>

              <div className="text-right">
                <div className="text-xs text-slate-400">Cumulative GPA</div>
                <div className="text-2xl font-black text-teal-300">{targetStudent.cgpa.toFixed(2)}</div>
              </div>
            </div>

            {/* Academic Marks Breakdown */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Course Performance Assessment</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/60">
                  <div className="text-[10px] text-slate-400">IAT 1 (50)</div>
                  <div className="text-sm font-bold text-white">{targetStudent.i1}</div>
                </div>
                <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/60">
                  <div className="text-[10px] text-slate-400">IAT 2 (50)</div>
                  <div className="text-sm font-bold text-white">{targetStudent.i2}</div>
                </div>
                <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/60">
                  <div className="text-[10px] text-slate-400">IAT 3 (50)</div>
                  <div className="text-sm font-bold text-white">{targetStudent.i3}</div>
                </div>
                <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/60">
                  <div className="text-[10px] text-slate-400">Assignment (100)</div>
                  <div className="text-sm font-bold text-cyan-300">{targetStudent.assignment}%</div>
                </div>
              </div>
            </div>

            {/* Grade Determination */}
            <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between">
              <div>
                <div className="text-xs text-slate-400">Total Computed Marks: <strong className="text-white">{totalScoreCalc}/100</strong></div>
                <div className="text-lg font-black text-teal-400 mt-0.5">
                  GRADE {gradeInfo.grade} — {gradeInfo.desc}
                </div>
              </div>
              <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 text-xs font-bold rounded-lg border border-emerald-500/40">
                PROMOTED / PASS
              </span>
            </div>

            <button
              onClick={() => alert(`Dossier for ${targetStudent.name} (${targetStudent.roll}) formatted for print/export.`)}
              className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-teal-300 font-bold rounded-lg text-xs transition border border-teal-500/40"
            >
              📥 Export Official AU Regulation 2023 Progress Dossier
            </button>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 6: TIMETABLE, MATERIALS & OFFICE HOURS (Features 355, 356, 358, 359, 360)
      ========================================================================= */}
      {activeTab === 'admin_schedule' && (
        <div className="space-y-6">
          {/* Section 1: Weekly Timetable (Feature 359) */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <span>🗓️</span> Weekly Master Timetable (B.E. ECE - Semester V)
                </h2>
                <p className="text-xs text-slate-400">Lecture halls & laboratories schedule</p>
              </div>
              <span className="px-2.5 py-0.5 bg-teal-500/20 text-teal-300 text-xs font-mono font-bold rounded">
                7 Period Daily Cycle
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="py-2.5 px-3">Period</th>
                    <th className="py-2.5 px-3">Time</th>
                    <th className="py-2.5 px-3">Monday</th>
                    <th className="py-2.5 px-3">Tuesday</th>
                    <th className="py-2.5 px-3">Wednesday</th>
                    <th className="py-2.5 px-3">Thursday</th>
                    <th className="py-2.5 px-3">Friday</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {SEED_TIMETABLE.map(t => (
                    <tr key={t.period} className="hover:bg-slate-800/40 transition">
                      <td className="py-3 px-3 font-mono font-bold text-teal-400">P{t.period}</td>
                      <td className="py-3 px-3 text-slate-400 font-mono text-[11px]">{t.time}</td>
                      <td className="py-3 px-3 text-white font-medium">{t.mon}</td>
                      <td className="py-3 px-3 text-white font-medium">{t.tue}</td>
                      <td className="py-3 px-3 text-white font-medium">{t.wed}</td>
                      <td className="py-3 px-3 text-white font-medium">{t.thu}</td>
                      <td className="py-3 px-3 text-white font-medium">{t.fri}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Section 2: Course Materials & Broadcasts (Features 355 & 356) */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Upload Manager */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <span>📚</span> Course Material Repository (Feature 355)
              </h2>

              <form onSubmit={handleUploadMaterial} className="space-y-3 bg-slate-800/40 p-3.5 rounded-lg border border-slate-700/50">
                <input
                  type="text"
                  value={newMatTitle}
                  onChange={e => setNewMatTitle(e.target.value)}
                  placeholder="Material title (e.g., TSMC 28nm DRC/LVS Guide)..."
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-teal-500"
                  required
                />
                <div className="flex gap-2">
                  <select
                    value={newMatCategory}
                    onChange={e => setNewMatCategory(e.target.value)}
                    className="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white"
                  >
                    <option value="NOTES">Lecture Notes</option>
                    <option value="LAB_MANUAL">Lab Manual</option>
                    <option value="QUESTION_BANK">Question Bank</option>
                    <option value="SIM_TEMPLATE">Simulation Deck</option>
                  </select>
                  <button
                    type="submit"
                    className="flex-1 py-1.5 bg-teal-500 text-slate-950 font-bold rounded-lg text-xs hover:bg-teal-400 transition"
                  >
                    Upload Document
                  </button>
                </div>
              </form>

              <div className="space-y-2 max-h-48 overflow-y-auto">
                {materials.map(m => (
                  <div key={m.id} className="p-2.5 bg-slate-800/60 rounded-lg border border-slate-700/50 flex items-center justify-between text-xs">
                    <div>
                      <div className="font-semibold text-white">{m.title}</div>
                      <div className="text-[10px] text-teal-400">{m.category} • Semester {m.sem}</div>
                    </div>
                    <span className="text-slate-400">PDF / CIR</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Broadcast System */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <span>📢</span> Announcement Broadcast (Feature 356)
              </h2>

              <form onSubmit={handleBroadcast} className="space-y-3 bg-slate-800/40 p-3.5 rounded-lg border border-slate-700/50">
                <input
                  type="text"
                  value={newAnnTitle}
                  onChange={e => setNewAnnTitle(e.target.value)}
                  placeholder="Notice Title..."
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-teal-500"
                  required
                />
                <textarea
                  value={newAnnBody}
                  onChange={e => setNewAnnBody(e.target.value)}
                  rows={2}
                  placeholder="Announcement body..."
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-teal-500"
                  required
                />
                <div className="flex gap-2">
                  <select
                    value={newAnnPriority}
                    onChange={e => setNewAnnPriority(e.target.value)}
                    className="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white"
                  >
                    <option value="URGENT">Urgent Circular</option>
                    <option value="NORMAL">Normal Notice</option>
                  </select>
                  <button
                    type="submit"
                    className="flex-1 py-1.5 bg-blue-600 text-white font-bold rounded-lg text-xs hover:bg-blue-500 transition"
                  >
                    Broadcast Circular
                  </button>
                </div>
              </form>

              <div className="space-y-2 max-h-48 overflow-y-auto">
                {announcements.map(a => (
                  <div key={a.id} className="p-2.5 bg-slate-800/60 rounded-lg border border-slate-700/50 text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-rose-400">[{a.priority}] {a.title}</span>
                      <span className="text-[10px] text-slate-400">{a.date}</span>
                    </div>
                    <p className="text-slate-300 text-[11px] leading-relaxed">{a.body}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Section 3: Faculty Office Hours (Feature 360) */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <span>🎓</span> Faculty Counseling & Office Hours (Feature 360)
              </h2>
              <p className="text-xs text-slate-400">Reserve 1-on-1 thesis guidance, research mentoring, or academic consultation</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {officeSlots.map(slot => (
                <div key={slot.id} className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-teal-400 text-xs">{slot.day}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        slot.status === 'AVAILABLE' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-700 text-slate-400'
                      }`}>
                        {slot.status}
                      </span>
                    </div>
                    <div className="text-xs font-semibold text-white">{slot.time}</div>
                    <div className="text-[11px] text-slate-400 mt-1">{slot.venue}</div>
                    {slot.bookedBy && (
                      <div className="text-[10px] text-teal-300 mt-2 bg-slate-900 p-1.5 rounded font-mono">
                        Booked: {slot.bookedBy}
                      </div>
                    )}
                  </div>

                  {slot.status === 'AVAILABLE' && (
                    <button
                      onClick={() => handleBookSlot(slot.id)}
                      className="mt-4 w-full py-1.5 bg-teal-500 text-slate-950 font-bold rounded-lg text-xs hover:bg-teal-400 transition"
                    >
                      Reserve Appointment
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 7: INSTRUCTOR CMS & OVERRIDES (Phase 9)
      ========================================================================= */}
      {activeTab === 'instructor_cms' && (
        <div className="space-y-6 font-mono text-xs">
          {/* Top Banner */}
          <div className="p-4 rounded-xl bg-slate-900 border border-teal-500/30 flex items-center justify-between">
            <div>
              <span className="font-bold text-white text-sm">Instructor Content Management & Review Overrides</span>
              <p className="text-slate-400 text-[11px]">Publish validated engineering courses, override AI code review verdicts, and manage exam question banks.</p>
            </div>
            <span className="px-3 py-1 rounded-full bg-teal-500/20 text-teal-300 border border-teal-500/40 text-[10px] font-bold">
              RBAC: FACULTY PRIVILEGES
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Panel 1: Course Publishing Studio */}
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <div className="text-sm font-bold text-teal-300 flex items-center gap-2">
                <span>📚</span> Course Publishing Studio
              </div>
              <form onSubmit={handlePublishCourse} className="space-y-3">
                <div>
                  <label className="text-slate-400 block mb-1">Course Code:</label>
                  <input
                    type="text"
                    value={cmsCourseCode}
                    onChange={(e) => setCmsCourseCode(e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:border-teal-400 outline-none"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Course Name:</label>
                  <input
                    type="text"
                    value={cmsCourseName}
                    onChange={(e) => setCmsCourseName(e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:border-teal-400 outline-none"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-slate-400 block mb-1">Semester:</label>
                    <input
                      type="number"
                      value={cmsSemester}
                      onChange={(e) => setCmsSemester(parseInt(e.target.value) || 5)}
                      className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:border-teal-400 outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-1">Credits:</label>
                    <input
                      type="number"
                      value={cmsCredits}
                      onChange={(e) => setCmsCredits(parseInt(e.target.value) || 4)}
                      className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:border-teal-400 outline-none"
                    />
                  </div>
                </div>
                <button
                  type="submit"
                  className="w-full py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold transition shadow-lg"
                >
                  Publish Course to Platform
                </button>
              </form>
            </div>

            {/* Panel 2: AI Review Verdict Override */}
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <div className="text-sm font-bold text-amber-400 flex items-center gap-2">
                <span>⚖️</span> AI Review Verdict Override
              </div>
              <form onSubmit={handleOverrideReview} className="space-y-3">
                <div>
                  <label className="text-slate-400 block mb-1">Report ID:</label>
                  <input
                    type="text"
                    value={overrideReportId}
                    onChange={(e) => setOverrideReportId(e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:border-amber-400 outline-none"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Override Verdict:</label>
                  <select
                    value={overrideVerdict}
                    onChange={(e) => setOverrideVerdict(e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:border-amber-400 outline-none"
                  >
                    <option value="APPROVED">APPROVED (Faculty Certified)</option>
                    <option value="NEEDS_REVISION">NEEDS_REVISION</option>
                    <option value="DISTINCTION">DISTINCTION (Exemplary)</option>
                  </select>
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Adjusted Score (/100):</label>
                  <input
                    type="number"
                    value={overrideScore}
                    onChange={(e) => setOverrideScore(parseFloat(e.target.value) || 90)}
                    className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:border-amber-400 outline-none"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Faculty Remarks:</label>
                  <textarea
                    rows={2}
                    value={overrideNotes}
                    onChange={(e) => setOverrideNotes(e.target.value)}
                    className="w-full p-2 rounded-xl bg-slate-950 border border-slate-800 text-white focus:border-amber-400 outline-none"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full py-2.5 rounded-xl bg-amber-400 hover:bg-amber-300 text-slate-950 font-bold transition shadow-lg"
                >
                  Commit Verdict Override
                </button>
              </form>
            </div>

            {/* Panel 3: Question Bank Manager */}
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <div className="text-sm font-bold text-cyan-400 flex items-center gap-2">
                <span>📝</span> Question Bank Manager
              </div>
              <form onSubmit={handleAddQuestion} className="space-y-3">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-slate-400 block mb-1">Question ID:</label>
                    <input
                      type="text"
                      value={questionQid}
                      onChange={(e) => setQuestionQid(e.target.value)}
                      className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:border-cyan-400 outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-1">Outcome:</label>
                    <select
                      value={questionCO}
                      onChange={(e) => setQuestionCO(e.target.value)}
                      className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:border-cyan-400 outline-none"
                    >
                      <option value="CO1">CO1: Analog</option>
                      <option value="CO2">CO2: Digital</option>
                      <option value="CO3">CO3: ARM Silicon</option>
                      <option value="CO4">CO4: RTOS Kernel</option>
                      <option value="CO5">CO5: DMA &amp; IoT</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Question Statement:</label>
                  <textarea
                    rows={2}
                    value={questionText}
                    onChange={(e) => setQuestionText(e.target.value)}
                    className="w-full p-2 rounded-xl bg-slate-950 border border-slate-800 text-white focus:border-cyan-400 outline-none"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-slate-400 block mb-1">Correct Key:</label>
                    <input
                      type="text"
                      value={questionAns}
                      onChange={(e) => setQuestionAns(e.target.value)}
                      className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:border-cyan-400 outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-1">Marks:</label>
                    <input
                      type="number"
                      value={questionMarks}
                      onChange={(e) => setQuestionMarks(parseInt(e.target.value) || 2)}
                      className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:border-cyan-400 outline-none"
                    />
                  </div>
                </div>
                <button
                  type="submit"
                  className="w-full py-2.5 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold transition shadow-lg"
                >
                  Add Question to Bank
                </button>
              </form>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}
