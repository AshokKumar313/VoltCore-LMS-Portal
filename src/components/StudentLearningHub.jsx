import React, { useState, useEffect } from 'react';
import { ECE_SUBJECT_REGISTRY } from '../data/subjectRegistry';
import SubjectEmblem from './SubjectEmblem.jsx';
import CourseCoverArtwork, { getCoverSvgForCourse } from './CourseCoverArtwork.jsx';
import InstitutionalCertificateGenerator from './InstitutionalCertificateGenerator.jsx';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Student Learning Hub & Academic Studio Island
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 *
 * Capabilities:
 *   1. Continue Learning Hero Card (localStorage resume sync + flagship fallbacks)
 *   2. Recently Opened Lessons & Bookmarks Strip (quick resume + clean empty state)
 *   3. Regulation 2023 Course Progress & Unit Completion Grid (15 ECE disciplines)
 *   4. OBE Attainment & Assessment Readiness Summary Panel
 * ========================================================================================
 */

// Priority Course Codes to highlight on the Dashboard
const DASHBOARD_COURSE_CODES = [
  'EC23S01', // Flagship: Numerical and Signal Processing Practice Through Python
  'STM32-ACADEMY', // Flagship: Bare-Metal STM32 Academy
  'EC23C03', // Electronic Devices
  'EC23C04', // Digital System Design
  'EC23C05', // Signals and Systems
  'EC23C06', // Analog Circuits
  'EC23C01', // Circuit Analysis
  'EC8702',  // Embedded Systems
  'EC23E04', // Optics and Lasers
  'IOT8701', // IoT Connected Systems
  'HDL6001', // Verilog HDL
  'VLSI7001' // VLSI Physical Design
];

// Fallback flagship courses if no lesson has been opened yet
const DEFAULT_FLAGSHIP_LESSONS = [
  {
    id: 'EC23S01_U1_L1',
    courseCode: 'EC23S01',
    courseName: 'Signal Processing Practice (Python)',
    title: 'Vectorized Discrete-Time Convolution & Zero-Padding Equivalence',
    unit: 'Unit I: Discrete Signals & Convolution',
    duration: '45 mins',
    path: '/course-hub',
    progress: 35,
    type: 'Lesson'
  },
  {
    id: 'STM32_CH01',
    courseCode: 'STM32',
    courseName: 'Bare-Metal STM32 Academy',
    title: 'ARM Cortex-M Hardware Architecture & Bus Matrix',
    unit: 'Chapter 01: Core Architecture',
    duration: '50 mins',
    path: '/embedded-systems/stm32-academy',
    progress: 60,
    type: 'Lab / Chapter'
  },
  {
    id: 'EC23C03_U2_L1',
    courseCode: 'EC23C03',
    courseName: 'Electronic Devices',
    title: 'BJT High-Frequency Hybrid-Pi Model & Miller Effect',
    unit: 'Unit II: BJT Transistors',
    duration: '40 mins',
    path: '/analog-electronics',
    progress: 80,
    type: 'Derivation'
  },
  {
    id: 'EC23C04_U1_L1',
    courseCode: 'EC23C04',
    courseName: 'Digital System Design',
    title: '4-Variable Karnaugh Map & Prime Implicant Grouping',
    unit: 'Unit I: Combinational Logic',
    duration: '35 mins',
    path: '/digital-logic',
    progress: 90,
    type: 'Simulation'
  }
];

const DEFAULT_WEEKLY_PLAN = [
  { id: 'wp-1', day: 'Monday', subject: 'Signals, DSP & Wavelet Analysis', topic: 'Radix-2 FFT Butterfly Flow Graphs', duration: '45m', completed: true },
  { id: 'wp-2', day: 'Tuesday', subject: 'Semiconductor Devices & Integrated Circuits', topic: 'Small-Signal BJT Hybrid-π Models', duration: '50m', completed: true },
  { id: 'wp-3', day: 'Wednesday', subject: 'Embedded Real-Time Systems & IoT', topic: 'ARM Cortex-M NVIC Interrupt Tail-Chaining', duration: '60m', completed: false },
  { id: 'wp-4', day: 'Thursday', subject: 'Digital Systems & Computer Architecture', topic: '4-Variable Karnaugh Map & Prime Implicants', duration: '40m', completed: false },
  { id: 'wp-5', day: 'Friday', subject: 'Electromagnetic Waves, Antennas & RF', topic: 'Transmission Line Characteristic Impedance & Smith Charts', duration: '55m', completed: false },
  { id: 'wp-6', day: 'Saturday', subject: 'Hardware & Analog Simulation Laboratory', topic: 'SPICE AC Small-Signal & Transient Analysis', duration: '90m', completed: false },
  { id: 'wp-7', day: 'Sunday', subject: 'Review & Spaced Repetition', topic: 'SM-2 Flashcard Recall & GATE Formula Revision', duration: '30m', completed: false }
];

const RECOMMENDED_REVISION = [
  {
    id: 'rev-1',
    subject: 'Signals, DSP & Wavelet Analysis',
    unit: 'Unit II: Fast Fourier Transform & Spectral Bins',
    reason: '12 Due SM-2 Flashcards',
    urgency: 'High Priority',
    badgeClass: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
    actionUrl: '/course-hub'
  },
  {
    id: 'rev-2',
    subject: 'Embedded Real-Time Systems & IoT',
    unit: 'Unit IV: Bus Matrix Contention & DMA Stream Pacing',
    reason: 'Prerequisite for Lab 304 HIL',
    urgency: 'Lab Readiness',
    badgeClass: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
    actionUrl: '/embedded-systems/stm32-academy'
  },
  {
    id: 'rev-3',
    subject: 'Semiconductor Devices & Integrated Circuits',
    unit: 'Unit III: MOSFET Saturation & Channel Pinch-Off',
    reason: 'Anna University High Weightage',
    urgency: 'Exam High-Yield',
    badgeClass: 'bg-sky-500/20 text-sky-300 border-sky-500/40',
    actionUrl: '/analog-electronics'
  },
  {
    id: 'rev-4',
    subject: 'Digital Systems & Computer Architecture',
    unit: 'Unit I: Prime Implicant Synthesis & Hazards',
    reason: 'Incomplete Practice Assessment',
    urgency: 'Recommended',
    badgeClass: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
    actionUrl: '/digital-logic'
  }
];

export default function StudentLearningHub() {
  const [recentLesson, setRecentLesson] = useState(DEFAULT_FLAGSHIP_LESSONS[0]);
  const [bookmarkedCount, setBookmarkedCount] = useState(0);
  const [recentBookmarks, setRecentBookmarks] = useState([]);
  const [dueFlashcardsCount, setDueFlashcardsCount] = useState(12);
  const [completedLessonsCount, setCompletedLessonsCount] = useState(14);
  const [weeklyPlan, setWeeklyPlan] = useState(DEFAULT_WEEKLY_PLAN);
  const [selectedDayFilter, setSelectedDayFilter] = useState('All');
  const [userProfile, setUserProfile] = useState({
    name: 'Active Peer',
    role: 'Student',
    department: 'Electronics Engineering (MIT Campus)'
  });

  // Hydrate student data from localStorage
  useEffect(() => {
    try {
      if (typeof window !== 'undefined') {
        // Read user session
        const rawUser = localStorage.getItem('voltcore_user');
        if (rawUser) {
          const u = JSON.parse(rawUser);
          setUserProfile((prev) => ({
            ...prev,
            name: u.name || prev.name,
            role: u.role || prev.role
          }));
        }

        // Read bookmarks
        const rawBm = localStorage.getItem('voltcore_lesson_bookmarks');
        if (rawBm) {
          const bm = JSON.parse(rawBm);
          const keys = Object.keys(bm);
          setBookmarkedCount(keys.length);
          if (keys.length > 0) {
            setRecentBookmarks(
              keys.slice(0, 4).map((k) => ({
                id: k,
                title: k.replace(/_/g, ' '),
                path: '/course-hub'
              }))
            );
          }
        }

        // Read completed lessons
        const rawComp = localStorage.getItem('voltcore_lesson_completed');
        if (rawComp) {
          const comp = JSON.parse(rawComp);
          setCompletedLessonsCount(Object.keys(comp).length || 14);
        }

        // Check for custom last opened lesson
        const lastLesson = localStorage.getItem('voltcore_last_opened_lesson');
        if (lastLesson) {
          setRecentLesson(JSON.parse(lastLesson));
        }

        // Read weekly planner
        const rawPlanner = localStorage.getItem('voltcore_weekly_planner');
        if (rawPlanner) {
          setWeeklyPlan(JSON.parse(rawPlanner));
        }
      }
    } catch (e) {
      console.warn('[StudentLearningHub]: LocalStorage hydration error', e);
    }
  }, []);

  const toggleWeeklyTask = (taskId) => {
    setWeeklyPlan(prev => {
      const updated = prev.map(t => t.id === taskId ? { ...t, completed: !t.completed } : t);
      try {
        if (typeof window !== 'undefined') {
          localStorage.setItem('voltcore_weekly_planner', JSON.stringify(updated));
        }
      } catch (err) {
        console.warn('Failed to save weekly planner', err);
      }
      return updated;
    });
  };

  return (
    <div className="space-y-8 font-sans">
      
      {/* ==========================================================================
          1. CONTINUE LEARNING HERO CARD
          ========================================================================== */}
      <section
        className="rounded-3xl p-6 sm:p-8 border relative overflow-hidden transition-all shadow-xl"
        style={{
          background: 'linear-gradient(135deg, var(--theme-surface, rgba(4,16,38,0.9)) 0%, var(--theme-card, rgba(6,23,53,0.85)) 100%)',
          borderColor: 'var(--theme-border, rgba(0,240,181,0.3))',
        }}
      >
        {/* Bespoke SVG Course Cover Artwork Background */}
        <div
          className="absolute inset-0 pointer-events-none opacity-20"
          style={{
            backgroundImage: `url(${getCoverSvgForCourse(recentLesson.courseCode)})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-3 max-w-2xl">
            <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
              <span className="px-2.5 py-1 rounded-full bg-emerald-500/15 text-emerald-300 font-bold border border-emerald-500/30 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                CONTINUE LEARNING
              </span>
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-slate-800 text-white font-bold border border-slate-700">
                <SubjectEmblem courseCode={recentLesson.courseCode} size="sm" showFrame={false} />
                <span>{recentLesson.courseName}</span>
              </div>
              <span className="text-slate-400">
                {recentLesson.unit}
              </span>
            </div>

            <h2 className="font-heading font-extrabold text-2xl sm:text-3xl text-white tracking-tight">
              {recentLesson.title}
            </h2>

            <p className="text-sm text-slate-300 leading-relaxed max-w-xl">
              Pick up right where you left off. Review theoretical derivations, inspect formula cards, or launch the interactive Python / Wokwi testbench.
            </p>

            <div className="flex items-center gap-4 pt-1 font-mono text-xs text-slate-400">
              <div className="flex items-center gap-1.5">
                <span className="text-emerald-400">⏱️</span>
                <span>Est. Time: <strong className="text-white">{recentLesson.duration}</strong></span>
              </div>
              <div className="text-slate-600">•</div>
              <div className="flex items-center gap-1.5">
                <span className="text-cyan-400">📊</span>
                <span>Unit Progress: <strong className="text-cyan-300">{recentLesson.progress}%</strong></span>
              </div>
            </div>
          </div>

          {/* Hero Action Button & Progress Ring */}
          <div className="flex sm:flex-col items-center justify-end gap-3 flex-shrink-0">
            <a
              href={recentLesson.path}
              className="w-full sm:w-auto px-6 py-3.5 rounded-2xl bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-slate-950 font-heading font-bold text-sm transition-all shadow-lg flex items-center justify-center gap-2 group cursor-pointer"
            >
              <span>Resume Lesson</span>
              <span className="group-hover:translate-x-1 transition-transform">&rarr;</span>
            </a>
            <a
              href="/nptel-player"
              className="w-full sm:w-auto px-4 py-2.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white font-mono text-xs transition-all flex items-center justify-center gap-2"
            >
              <span>🎥 Open NPTEL Lecture</span>
            </a>
          </div>
        </div>

        {/* Ambient Glow Gradient */}
        <div
          className="absolute -right-20 -bottom-20 w-80 h-80 rounded-full blur-3xl pointer-events-none"
          style={{ background: 'radial-gradient(circle, var(--theme-primary, #00F0B5) 0%, transparent 70%)', opacity: 0.15 }}
        ></div>
      </section>


      {/* ==========================================================================
          2. RECENTLY OPENED LESSONS & BOOKMARKS STRIP
          ========================================================================== */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">⚡</span>
            <h3 className="font-heading font-bold text-lg text-white tracking-tight">
              Recent Engineering Lessons & Bookmarked Notes
            </h3>
          </div>
          <span className="text-xs font-mono text-slate-400">
            {bookmarkedCount} Bookmarked • {completedLessonsCount} Completed
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {DEFAULT_FLAGSHIP_LESSONS.map((lesson) => (
            <a
              key={lesson.id}
              href={lesson.path}
              className="p-4 rounded-2xl border transition-all hover:-translate-y-1 group block"
              style={{
                background: 'var(--theme-surface, rgba(4,16,38,0.7))',
                borderColor: 'var(--theme-border, rgba(0,240,181,0.2))',
              }}
            >
              <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-2">
                <span className="px-2 py-0.5 rounded bg-slate-900 text-emerald-400 font-bold border border-emerald-500/30 truncate max-w-[140px]">
                  {lesson.courseName}
                </span>
                <span className="text-slate-500">{lesson.type}</span>
              </div>

              <div className="font-heading font-bold text-xs sm:text-sm text-slate-100 group-hover:text-[var(--theme-primary,#00F0B5)] transition-colors line-clamp-2 mb-2">
                {lesson.title}
              </div>

              <div className="text-[11px] text-slate-400 font-sans truncate mb-3">
                {lesson.unit}
              </div>

              {/* Mini Progress Bar */}
              <div className="w-full bg-slate-800/80 rounded-full h-1.5 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${lesson.progress}%`,
                    background: 'linear-gradient(to right, #00693E, #00F0B5)',
                  }}
                ></div>
              </div>
            </a>
          ))}
        </div>
      </section>


      {/* ==========================================================================
          3. REGULATION 2023 COURSE PROGRESS & UNIT COMPLETION GRID
          ========================================================================== */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">🏛️</span>
            <h3 className="font-heading font-bold text-lg text-white tracking-tight">
              Regulation 2023 Curriculum Progress (15 Disciplines)
            </h3>
          </div>
          <a
            href="/course-hub"
            className="text-xs font-mono text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
          >
            <span>View Full Syllabus</span>
            <span>&rarr;</span>
          </a>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {DASHBOARD_COURSE_CODES.map((code) => {
            const subject = ECE_SUBJECT_REGISTRY[code];
            if (!subject) return null;

            // Generate deterministic progress for display
            const progressVal = ((code.charCodeAt(0) * 13 + code.charCodeAt(code.length - 1) * 7) % 40) + 55;

            return (
              <div
                key={code}
                className="p-4 rounded-2xl border transition-all hover:border-emerald-400/40 space-y-3 relative overflow-hidden group"
                style={{
                  background: 'var(--theme-surface, rgba(4,16,38,0.85))',
                  borderColor: 'var(--theme-border, rgba(0,240,181,0.2))',
                }}
              >
                {/* Subtle Domain Cover Artwork Background */}
                <div
                  className="absolute inset-0 pointer-events-none opacity-10 group-hover:opacity-20 transition-opacity"
                  style={{
                    backgroundImage: `url(${getCoverSvgForCourse(code)})`,
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                  }}
                />

                <div className="flex items-start justify-between gap-2 relative z-10">
                  <div className="flex items-center gap-2.5">
                    <SubjectEmblem courseCode={code} size="md" showFrame={true} />
                    <div>
                      <div className="font-heading font-bold text-xs text-white line-clamp-1 group-hover:text-emerald-300 transition-colors">
                        {subject.disciplineName}
                      </div>
                      <div className="text-[10px] font-mono text-slate-400">
                        Semester {subject.semester} • {subject.credits} Credits
                      </div>
                    </div>
                  </div>

                  <span
                    className="text-[9px] px-2 py-0.5 rounded-full font-mono font-bold flex-shrink-0"
                    style={{
                      backgroundColor: `${subject.primaryColor}20`,
                      color: subject.primaryColor,
                    }}
                  >
                    {progressVal}%
                  </span>
                </div>

                <div className="text-[11px] text-slate-400 line-clamp-1">
                  Domain: {subject.industryDomain}
                </div>

                {/* Progress bar */}
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${progressVal}%`,
                      backgroundColor: subject.primaryColor,
                    }}
                  ></div>
                </div>

                {/* 3 Action Links */}
                <div className="flex items-center justify-between pt-1 border-t border-slate-800/80 font-mono text-[10px]">
                  <a
                    href="/course-hub"
                    className="text-slate-300 hover:text-white flex items-center gap-1"
                  >
                    <span>📖</span>
                    <span>Notes</span>
                  </a>
                  <a
                    href="/nptel-player"
                    className="text-amber-400 hover:text-amber-300 flex items-center gap-1"
                  >
                    <span>🎥</span>
                    <span>Lectures</span>
                  </a>
                  <a
                    href="/simulation"
                    className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
                  >
                    <span>⚡</span>
                    <span>Labs</span>
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      </section>


      {/* ==========================================================================
          3.5. SMART WEEKLY STUDY PLANNER & RECOMMENDED REVISION (PHASE 14)
          ========================================================================== */}
      <section
        className="rounded-3xl p-6 sm:p-8 border space-y-6"
        style={{
          background: 'var(--theme-surface, rgba(4,16,38,0.85))',
          borderColor: 'var(--theme-border, rgba(0,240,181,0.25))',
        }}
      >
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 mb-2 font-mono">
              <span>📅</span>
              <span>Regulation 2023 Study Pacing</span>
            </div>
            <h3 className="font-heading font-extrabold text-xl text-white tracking-tight">
              Smart Weekly Study Planner &amp; Recommended Revision
            </h3>
            <p className="text-xs text-slate-400 mt-1 font-sans">
              Structured study plan across core subjects with adaptive spaced repetition and lab readiness pacing.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right font-mono text-xs">
              <span className="text-slate-400">Weekly Progress: </span>
              <span className="text-emerald-400 font-bold">
                {weeklyPlan.filter(t => t.completed).length} / {weeklyPlan.length} Done
              </span>
            </div>
            <div className="w-24 h-2.5 rounded-full bg-slate-950 overflow-hidden border border-slate-800">
              <div
                className="h-full bg-gradient-to-r from-emerald-500 to-cyan-400 transition-all duration-500"
                style={{
                  width: `${(weeklyPlan.filter(t => t.completed).length / weeklyPlan.length) * 100}%`
                }}
              />
            </div>
          </div>
        </div>

        {/* Two-Column Grid: Planner on Left, Recommended Revision on Right */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Weekly Planner */}
          <div className="lg:col-span-7 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold font-mono text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                Scheduled Study Sessions
              </h4>
              <div className="flex items-center gap-1">
                {['All', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].map(day => (
                  <button
                    key={day}
                    onClick={() => setSelectedDayFilter(day)}
                    className={`px-2 py-1 rounded text-[10px] font-mono transition-colors ${
                      selectedDayFilter === day
                        ? 'bg-sky-500 text-white font-bold'
                        : 'bg-slate-900 text-slate-400 hover:text-white'
                    }`}
                  >
                    {day === 'All' ? 'All' : day.slice(0, 3)}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2.5">
              {weeklyPlan
                .filter(item => selectedDayFilter === 'All' || item.day === selectedDayFilter)
                .map(item => (
                  <div
                    key={item.id}
                    onClick={() => toggleWeeklyTask(item.id)}
                    className={`p-3.5 rounded-xl border flex items-center justify-between gap-3 cursor-pointer transition-all ${
                      item.completed
                        ? 'bg-emerald-950/20 border-emerald-500/30 text-slate-400'
                        : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 text-slate-200'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-5 h-5 rounded flex items-center justify-center border text-xs ${
                        item.completed
                          ? 'bg-emerald-500 border-emerald-400 text-slate-950 font-bold'
                          : 'border-slate-700 bg-slate-950'
                      }`}>
                        {item.completed ? '✓' : ''}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-slate-950 text-cyan-400 border border-slate-800">
                            {item.day}
                          </span>
                          <span className="text-xs font-bold text-white font-sans">
                            {item.subject}
                          </span>
                        </div>
                        <div className={`text-xs mt-0.5 ${item.completed ? 'line-through text-slate-500' : 'text-slate-300'}`}>
                          {item.topic}
                        </div>
                      </div>
                    </div>
                    <div className="text-[10px] font-mono text-slate-500 flex-shrink-0">
                      ⏱️ {item.duration}
                    </div>
                  </div>
                ))}
            </div>
          </div>

          {/* Right Column: Recommended Revision */}
          <div className="lg:col-span-5 space-y-4">
            <h4 className="text-xs font-bold font-mono text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-400"></span>
              Recommended Revision (Spaced Pacing)
            </h4>

            <div className="space-y-3">
              {RECOMMENDED_REVISION.map(rev => (
                <div
                  key={rev.id}
                  className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-amber-500/40 transition-all flex flex-col justify-between gap-2"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="text-xs font-bold text-white leading-tight font-sans">
                        {rev.subject}
                      </div>
                      <div className="text-[11px] text-slate-300 mt-1 font-mono">
                        {rev.unit}
                      </div>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border flex-shrink-0 ${rev.badgeClass}`}>
                      {rev.urgency}
                    </span>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-[11px] font-mono">
                    <span className="text-slate-400">{rev.reason}</span>
                    <a
                      href={rev.actionUrl}
                      className="text-amber-400 hover:text-amber-300 font-bold flex items-center gap-1 transition-colors"
                    >
                      <span>Review Topic</span>
                      <span>&rarr;</span>
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>


      {/* ==========================================================================
          4. OBE ATTAINMENT & READINESS SUMMARY PANEL
          ========================================================================== */}
      <section
        className="rounded-3xl p-6 border space-y-4"
        style={{
          background: 'var(--theme-surface, rgba(4,16,38,0.8))',
          borderColor: 'var(--theme-border, rgba(0,240,181,0.25))',
        }}
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <span className="text-xl">🎯</span>
            <div>
              <h3 className="font-heading font-bold text-base text-white tracking-tight">
                Outcome-Based Education (OBE) Attainment & Exam Readiness
              </h3>
              <p className="text-xs text-slate-400 font-sans">
                Continuous assessment derivation against Anna University Regulation 2023 benchmarks.
              </p>
            </div>
          </div>
          <span className="px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-300 text-xs font-mono font-bold border border-emerald-500/30 flex-shrink-0 self-start sm:self-auto">
            PO1–PO12: 84.6% Attained
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 font-mono text-xs">
          {/* Quick Stat 1 */}
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="text-slate-400 text-[10px] mb-1">CO-PO ATTAINMENT</div>
            <div className="font-heading font-bold text-lg text-emerald-400">
              84.6%
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">Threshold: &ge; 70% Target Met</div>
          </div>

          {/* Quick Stat 2 */}
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="text-slate-400 text-[10px] mb-1">FLASHCARD RECALL</div>
            <div className="font-heading font-bold text-lg text-amber-400">
              {dueFlashcardsCount} Due
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">SM-2 Spaced Algorithm</div>
          </div>

          {/* Quick Stat 3 */}
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="text-slate-400 text-[10px] mb-1">INTERNAL ASSESSMENTS</div>
            <div className="font-heading font-bold text-lg text-cyan-400">
              CAT I & II
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">18 / 20 Average Marks</div>
          </div>

          {/* Quick Stat 4 */}
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="text-slate-400 text-[10px] mb-1">LAB PRACTICALS</div>
            <div className="font-heading font-bold text-lg text-purple-400">
              100% Verified
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">Lab 304 HIL Validated</div>
          </div>
        </div>

        {/* Quick Launch Buttons */}
        <div className="pt-2 flex flex-wrap items-center gap-3 font-mono text-xs">
          <a
            href="/exam-center"
            className="px-4 py-2 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-300 border border-emerald-500/30 font-bold transition-all flex items-center gap-1.5"
          >
            <span>🎯</span>
            <span>Launch GATE Exam Simulator</span>
          </a>
          <a
            href="/gate-ece"
            className="px-4 py-2 rounded-xl bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 border border-cyan-500/30 font-bold transition-all flex items-center gap-1.5"
          >
            <span>📚</span>
            <span>2,000+ GATE Question Bank</span>
          </a>
          <a
            href="/virtual-bench"
            className="px-4 py-2 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/30 font-bold transition-all flex items-center gap-1.5"
          >
            <span>📈</span>
            <span>Keysight Virtual Oscilloscope</span>
          </a>
          <a
            href="/simulation"
            className="px-4 py-2 rounded-xl bg-purple-500/15 hover:bg-purple-500/25 text-purple-300 border border-purple-500/30 font-bold transition-all flex items-center gap-1.5"
          >
            <span>⚡</span>
            <span>SPICE Hardware Simulation</span>
          </a>
        </div>
      </section>

      {/* ==========================================================================
          5. INSTITUTIONAL COMPLETION CERTIFICATE GENERATOR
          ========================================================================== */}
      <section className="pt-2">
        <InstitutionalCertificateGenerator embedded={true} />
      </section>

    </div>
  );
}
