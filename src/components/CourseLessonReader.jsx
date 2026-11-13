import React, { useState, useEffect, useMemo } from 'react';
import { getLessonsByCourse, getLessonsByUnit } from '../data/course_lessons_data';
import KatexFormulaCard from './KatexFormulaCard';
import { DepartmentalBadgeIcon } from './CourseShellHub';
import CourseSimulationIsland from './CourseSimulationIsland';
import IeeeEngineeringVisualizer from './IeeeEngineeringVisualizer';
import { ECE_SUBJECT_REGISTRY } from '../data/subjectRegistry';
import AcademicResourceVault from './AcademicResourceVault';
import { getCoverSvgForCourse } from './CourseCoverArtwork';
import EceInteractiveLabApplets from './EceInteractiveLabApplets';
import SubjectEmblem from './SubjectEmblem';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Unit-Wise Lesson Library & Student Bookmarking Hub
 * Core Engineering Series • Autonomous Engineering Cluster Standards
 * Platform Lead & Systems Architect: Ashok Kumar A
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 *
 * Capabilities:
 *   - Unit-wise curated lesson library across all 5 syllabus units
 *   - Markdown lecture notes reader with theoretical derivations
 *   - KaTeX mathematical formula inspector integration
 *   - Virtual hardware serial stimulus bridge (voltcore:lesson-transmit)
 *   - Student study notes and persistent bookmarking (localStorage with zero background polling)
 *   - Completion tracking and progress metric visualizer
 * ========================================================================================
 */

const STORAGE_KEY_BOOKMARKS = "voltcore_lesson_bookmarks";
const STORAGE_KEY_COMPLETED = "voltcore_lesson_completed";
const STORAGE_KEY_NOTES = "voltcore_student_study_notes";

export function getCourseVisualizerMode(code) {
  if (['EC23S01', 'EC23C07'].includes(code)) return 'dsp';
  if (['EC23C04', 'EC23C06', 'HDL6001', 'VLSI7001'].includes(code)) return 'digital';
  if (['EC23C08', 'EC23E04'].includes(code)) return 'comm';
  if (['EC23C03', 'EC23C05', 'EC23C01', 'EC23C02'].includes(code)) return 'bjt';
  return 'bjt';
}

export default function CourseLessonReader({
  courseCode = "EC23S01",
  themeColor = "#00F0B5",
  themeFamily = "emerald",
  onLaunchSimulator
}) {
  // Active Filter States
  const [selectedUnitFilter, setSelectedUnitFilter] = useState("all"); // "all" | "1" | "2" | "3" | "4" | "5"
  const [statusFilter, setStatusFilter] = useState("all"); // "all" | "bookmarked" | "completed" | "gate"
  const [searchQuery, setSearchQuery] = useState("");

  // Active Lesson Reader Modal/Drawer State
  const [activeLesson, setActiveLesson] = useState(null);

  // Student Bookmarks, Completed Lessons & Study Notes
  const [bookmarks, setBookmarks] = useState({});
  const [completedLessons, setCompletedLessons] = useState({});
  const [studyNotes, setStudyNotes] = useState({});
  const [currentNoteText, setCurrentNoteText] = useState("");
  const [noteSavedFeedback, setNoteSavedFeedback] = useState(false);
  const [stimulusTransmitted, setStimulusTransmitted] = useState(false);
  const [showInteractiveApplets, setShowInteractiveApplets] = useState(false);

  // Transmit hardware serial command to active Wokwi hardware bridge
  const handleTransmitStimulus = (lesson) => {
    if (typeof window === 'undefined' || !lesson) return;
    const stimulusText = `CMD:${lesson.courseCode}_L${lesson.lessonNumber}:${lesson.simulationBridge?.tool || 'HIL'}`;
    window.dispatchEvent(new CustomEvent('voltcore:lesson-transmit', {
      detail: {
        text: stimulusText,
        lessonId: lesson.id,
        courseCode: lesson.courseCode,
        timestamp: new Date().toISOString()
      }
    }));
    setStimulusTransmitted(true);
    setTimeout(() => setStimulusTransmitted(false), 2000);
  };

  // Hydrate persistent state from localStorage on client-side mount
  useEffect(() => {
    try {
      if (typeof window !== 'undefined') {
        const savedBookmarks = localStorage.getItem(STORAGE_KEY_BOOKMARKS);
        if (savedBookmarks) setBookmarks(JSON.parse(savedBookmarks));

        const savedCompleted = localStorage.getItem(STORAGE_KEY_COMPLETED);
        if (savedCompleted) setCompletedLessons(JSON.parse(savedCompleted));

        const savedNotes = localStorage.getItem(STORAGE_KEY_NOTES);
        if (savedNotes) setStudyNotes(JSON.parse(savedNotes));
      }
    } catch (e) {
      console.warn("Storage access restricted or unavailable:", e);
    }
  }, []);

  // Fetch lessons for the course
  const lessons = useMemo(() => {
    return getLessonsByCourse(courseCode);
  }, [courseCode]);

  // Filter lessons
  const filteredLessons = useMemo(() => {
    return lessons.filter((lesson) => {
      // Unit filter
      if (selectedUnitFilter !== "all" && lesson.unitNumber !== Number(selectedUnitFilter)) {
        return false;
      }
      // Status filter
      if (statusFilter === "bookmarked" && !bookmarks[lesson.id]) {
        return false;
      }
      if (statusFilter === "completed" && !completedLessons[lesson.id]) {
        return false;
      }
      if (statusFilter === "gate" && lesson.difficulty !== "GATE ECE Level") {
        return false;
      }
      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesTitle = lesson.title.toLowerCase().includes(q);
        const matchesSummary = lesson.summary.toLowerCase().includes(q);
        const matchesTopic = lesson.learningObjectives.some(lo => lo.toLowerCase().includes(q));
        if (!matchesTitle && !matchesSummary && !matchesTopic) return false;
      }
      return true;
    });
  }, [lessons, selectedUnitFilter, statusFilter, searchQuery, bookmarks, completedLessons]);

  // Completion metrics
  const completionStats = useMemo(() => {
    const total = lessons.length;
    const completedCount = lessons.filter(l => completedLessons[l.id]).length;
    const bookmarkedCount = lessons.filter(l => bookmarks[l.id]).length;
    const percentage = total > 0 ? Math.round((completedCount / total) * 100) : 0;
    return { total, completedCount, bookmarkedCount, percentage };
  }, [lessons, completedLessons, bookmarks]);

  // Toggle Bookmark
  const toggleBookmark = (lessonId, e) => {
    if (e) e.stopPropagation();
    setBookmarks((prev) => {
      const updated = { ...prev, [lessonId]: !prev[lessonId] };
      try {
        localStorage.setItem(STORAGE_KEY_BOOKMARKS, JSON.stringify(updated));
      } catch (err) {}
      return updated;
    });
  };

  // Toggle Complete & Sync Last Opened Lesson
  const toggleComplete = (lessonId, e) => {
    if (e) e.stopPropagation();
    setCompletedLessons((prev) => {
      const updated = { ...prev, [lessonId]: !prev[lessonId] };
      try {
        localStorage.setItem(STORAGE_KEY_COMPLETED, JSON.stringify(updated));
        const target = lessons.find(l => l.id === lessonId);
        if (target) {
          const payload = {
            id: target.id,
            courseCode: target.courseCode,
            courseName: target.courseCode === 'EC23S01' ? 'Signal Processing Practice (Python)' : target.courseCode,
            title: target.title,
            unit: `Unit ${target.unitRoman}: ${target.shortTitle || target.title}`,
            duration: `~${target.estimatedMinutes} mins`,
            path: `/course-hub?course=${target.courseCode}&lesson=${target.id}`,
            progress: updated[lessonId] ? 100 : 50,
            type: 'Lesson'
          };
          localStorage.setItem('voltcore_last_opened_lesson', JSON.stringify(payload));
        }
      } catch (err) {}
      return updated;
    });
  };

  // Copy code snippet helper
  const [copiedSnippet, setCopiedSnippet] = useState(false);
  const handleCopySnippet = (code) => {
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(code);
      setCopiedSnippet(true);
      setTimeout(() => setCopiedSnippet(false), 2000);
    }
  };

  // Export Markdown Study Note Helper
  const handleExportMarkdown = (lesson) => {
    if (!lesson) return;
    let md = `# Unit ${lesson.unitRoman}: ${lesson.title}\n\n`;
    md += `**Academic Level:** ${lesson.difficulty} | **Est. Study Time:** ~${lesson.estimatedMinutes} mins\n\n`;
    if (lesson.learningObjectives?.length) {
      md += `## 1. Learning Deliverables\n`;
      lesson.learningObjectives.forEach(obj => { md += `- ${obj}\n`; });
      md += `\n`;
    }
    if (lesson.prerequisites?.length) {
      md += `## 2. Prerequisites & Key Definitions\n`;
      lesson.prerequisites.forEach(p => { md += `- ${p}\n`; });
      md += `\n`;
    }
    md += `## 3. Academic Lecture Notes\n\n${lesson.markdownNotes}\n\n`;
    if (lesson.formulas?.length) {
      md += `## 4. Key Mathematical Formulations\n\n`;
      lesson.formulas.forEach(f => {
        md += `### ${f.name}\n$$${f.latex}$$\n${f.description}\n\n`;
      });
    }
    if (lesson.workedExample) {
      md += `## 5. Worked Numerical Example\n\n`;
      md += `**Problem Statement:** ${lesson.workedExample.problemStatement}\n\n`;
      lesson.workedExample.steps.forEach(s => {
        md += `#### ${s.stepTitle}\n${s.explanation}\n\n\`\`\`\n${s.calculation}\n\`\`\`\n\n`;
      });
      md += `**Final Answer:** ${lesson.workedExample.finalAnswer}\n\n`;
    }
    if (lesson.comparisonTable) {
      md += `## 6. Comparative Analysis\n\n| ${lesson.comparisonTable.headers.join(' | ')} |\n`;
      md += `| ${lesson.comparisonTable.headers.map(() => '---').join(' | ')} |\n`;
      lesson.comparisonTable.rows.forEach(r => {
        md += `| ${r.join(' | ')} |\n`;
      });
      md += `\n`;
    }
    if (studyNotes[lesson.id]) {
      md += `## Personal Student Study Notes\n\n${studyNotes[lesson.id]}\n\n`;
    }
    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${lesson.id}_lecture_notes.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    if (typeof window !== 'undefined') {
      window.print();
    }
  };

  // Save Student Study Note
  const handleSaveNote = () => {
    if (!activeLesson) return;
    setStudyNotes((prev) => {
      const updated = { ...prev, [activeLesson.id]: currentNoteText };
      try {
        localStorage.setItem(STORAGE_KEY_NOTES, JSON.stringify(updated));
      } catch (err) {}
      return updated;
    });
    setNoteSavedFeedback(true);
    setTimeout(() => setNoteSavedFeedback(false), 2000);
  };

  // Open Lesson Reader
  const handleOpenLesson = (lesson) => {
    setActiveLesson(lesson);
    setCurrentNoteText(studyNotes[lesson.id] || "");
  };

  return (
    <div className="space-y-6">
      
      {/* ------------------------------------------------------------------- */}
      {/* 1. STUDY PROGRESS & BOOKMARK SUMMARY HUD */}
      {/* ------------------------------------------------------------------- */}
      <div className="p-5 rounded-2xl bg-[#041026] border border-slate-800 shadow-xl space-y-4 font-mono">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
              {ECE_SUBJECT_REGISTRY[courseCode]?.disciplineName || 'Curriculum'} Study Progress &amp; Syllabus Coverage
            </div>
            <div className="text-lg font-extrabold text-white font-sans mt-0.5 flex items-center gap-2">
              <span>{completionStats.completedCount} of {completionStats.total} Lessons Completed</span>
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-full bg-[#020813] border border-slate-800" style={{ color: themeColor }}>
                {completionStats.percentage}%
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="px-3 py-1.5 rounded-xl bg-[#020813] border border-slate-800 text-amber-300 font-bold flex items-center gap-1.5">
              <span>⭐</span>
              <span>{completionStats.bookmarkedCount} Bookmarked</span>
            </span>
            <span className="px-3 py-1.5 rounded-xl bg-[#020813] border border-slate-800 text-emerald-400 font-bold flex items-center gap-1.5">
              <span>✓</span>
              <span>{completionStats.completedCount} Finished</span>
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full h-2.5 bg-[#020813] rounded-full overflow-hidden border border-slate-800 p-0.5">
          <div
            className="h-full rounded-full transition-all duration-500 shadow-md"
            style={{
              width: `${completionStats.percentage}%`,
              backgroundColor: themeColor
            }}
          ></div>
        </div>
      </div>

      {/* ------------------------------------------------------------------- */}
      {/* 2. FILTER & SEARCH STRIP */}
      {/* ------------------------------------------------------------------- */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 p-4 rounded-2xl bg-[#041026] border border-slate-800 font-mono text-xs shadow-md">
        
        {/* Unit Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-slate-500 font-semibold mr-1">Unit:</span>
          {["all", "1", "2", "3", "4", "5"].map((u) => {
            const isSelected = selectedUnitFilter === u;
            const label = u === "all" ? "All Units" : `Unit ${["I", "II", "III", "IV", "V"][Number(u) - 1]}`;
            return (
              <button
                key={u}
                onClick={() => setSelectedUnitFilter(u)}
                className={`px-2.5 py-1 rounded-lg transition-all ${
                  isSelected
                    ? "bg-[#020813] text-white font-bold border"
                    : "text-slate-400 hover:text-white bg-[#020813]/40 border border-slate-800"
                }`}
                style={{
                  borderColor: isSelected ? themeColor : undefined,
                  color: isSelected ? themeColor : undefined
                }}
              >
                {label}
              </button>
            );
          })}
        </div>

        {/* Status Filter Pills & Search Input */}
        <div className="flex flex-wrap items-center gap-2">
          {[
            { id: "all", label: "All Lessons" },
            { id: "bookmarked", label: "⭐ Bookmarks" },
            { id: "completed", label: "✓ Completed" },
            { id: "gate", label: "🎯 GATE ECE" }
          ].map((st) => (
            <button
              key={st.id}
              onClick={() => setStatusFilter(st.id)}
              className={`px-2.5 py-1 rounded-lg text-xs transition-all ${
                statusFilter === st.id
                  ? "bg-[#020813] text-white font-bold border border-slate-700"
                  : "text-slate-400 hover:text-slate-200"
              }`}
              style={{
                color: statusFilter === st.id ? themeColor : undefined
              }}
            >
              {st.label}
            </button>
          ))}

          <input
            type="text"
            placeholder="Search lessons or formulas..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-[#020813] border border-slate-800 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-emerald-500 transition-colors w-full sm:w-48"
          />
        </div>
      </div>

      {/* ------------------------------------------------------------------- */}
      {/* 3. LESSON LIBRARY CARDS GRID */}
      {/* ------------------------------------------------------------------- */}
      {filteredLessons.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredLessons.map((lesson) => {
            const isBookmarked = !!bookmarks[lesson.id];
            const isCompleted = !!completedLessons[lesson.id];
            const hasStudyNote = !!studyNotes[lesson.id];

            return (
              <div
                key={lesson.id}
                onClick={() => handleOpenLesson(lesson)}
                className="p-5 rounded-2xl bg-[#041026] border border-slate-800 hover:border-slate-700 transition-all cursor-pointer shadow-lg space-y-4 flex flex-col justify-between group relative overflow-hidden"
              >
                {/* Compact Unit-Level Cover Strip Background */}
                <div
                  className="absolute inset-0 pointer-events-none opacity-5 group-hover:opacity-15 transition-opacity"
                  style={{
                    backgroundImage: `url(${getCoverSvgForCourse(lesson.courseCode)})`,
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                  }}
                />

                <div className="relative z-10 space-y-3">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded-full bg-[#020813] border border-slate-800 font-bold" style={{ color: themeColor }}>
                        Unit {lesson.unitRoman} • Lesson {lesson.lessonNumber}
                      </span>
                      <span className="text-slate-500 text-[10px]">
                        ~{lesson.estimatedMinutes} mins
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={(e) => toggleBookmark(lesson.id, e)}
                        className={`p-1.5 rounded-lg border transition-all text-xs ${
                          isBookmarked
                            ? "bg-amber-950/60 text-amber-300 border-amber-500/40"
                            : "bg-[#020813] text-slate-500 border-slate-800 hover:text-amber-400"
                        }`}
                        title={isBookmarked ? "Remove Bookmark" : "Add Bookmark"}
                      >
                        {isBookmarked ? "⭐" : "☆"}
                      </button>

                      <button
                        onClick={(e) => toggleComplete(lesson.id, e)}
                        className={`p-1.5 rounded-lg border transition-all text-xs ${
                          isCompleted
                            ? "bg-emerald-950/60 text-emerald-300 border-emerald-500/40 font-bold"
                            : "bg-[#020813] text-slate-500 border-slate-800 hover:text-emerald-400"
                        }`}
                        title={isCompleted ? "Mark Incomplete" : "Mark as Completed"}
                      >
                        {isCompleted ? "✓" : "○"}
                      </button>
                    </div>
                  </div>

                  <h3 className="text-base font-bold text-white font-sans mt-2.5 group-hover:text-emerald-300 transition-colors">
                    {lesson.title}
                  </h3>

                  <p className="text-xs text-slate-400 leading-relaxed mt-1.5 line-clamp-2">
                    {lesson.summary}
                  </p>

                  <div className="mt-3 flex flex-wrap items-center gap-1.5 text-[10px] font-mono">
                    <span className={`px-2 py-0.5 rounded-md border ${
                      lesson.difficulty === "Foundational"
                        ? "bg-slate-900 text-slate-300 border-slate-800"
                        : lesson.difficulty === "Intermediate"
                        ? "bg-cyan-950/40 text-cyan-300 border-cyan-800/40"
                        : lesson.difficulty === "Advanced"
                        ? "bg-amber-950/40 text-amber-300 border-amber-800/40"
                        : "bg-purple-950/40 text-purple-300 border-purple-800/40"
                    }`}>
                      {lesson.difficulty}
                    </span>

                    {lesson.formulas.length > 0 && (
                      <span className="px-2 py-0.5 rounded-md bg-[#020813] border border-slate-800 text-slate-400">
                        📐 {lesson.formulas.length} KaTeX Formula{lesson.formulas.length > 1 ? "s" : ""}
                      </span>
                    )}

                    {hasStudyNote && (
                      <span className="px-2 py-0.5 rounded-md bg-emerald-950/30 text-emerald-300 border border-emerald-500/30">
                        📝 Notes Added
                      </span>
                    )}
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-400 text-[11px] group-hover:text-white transition-colors">
                    Read Lecture Notes →
                  </span>
                  {isCompleted && (
                    <span className="text-emerald-400 font-bold text-[10px]">
                      COMPLETED
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="p-8 rounded-2xl bg-[#041026] border border-slate-800 text-center font-mono text-xs text-slate-400 space-y-2">
          <div>No lessons matching active filters.</div>
          <button
            onClick={() => { setSelectedUnitFilter("all"); setStatusFilter("all"); setSearchQuery(""); }}
            className="text-emerald-400 underline"
          >
            Reset Filters
          </button>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* 3B. INTERACTIVE IEEE-STANDARD ENGINEERING VISUALIZER STUDIO        */}
      {/* ------------------------------------------------------------------- */}
      <section className="space-y-4 pt-4 border-t border-slate-800/80">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="text-xl">⚡</span>
            <h3 className="font-heading font-bold text-lg text-white">
              IEEE-Standard Interactive Engineering Visualizer Studio
            </h3>
          </div>
          <span className="text-[10px] font-mono px-2.5 py-1 rounded-full bg-[#00693E]/20 text-[#00F0B5] border border-[#00F0B5]/30 uppercase self-start sm:self-auto">
            Live Parameter Simulation Deck
          </span>
        </div>
        <IeeeEngineeringVisualizer
          courseCode={courseCode}
          initialMode={getCourseVisualizerMode(courseCode)}
          themeColor={themeColor}
        />
      </section>

      {/* ------------------------------------------------------------------- */}
      {/* 4. ACTIVE LECTURE NOTES & ACADEMIC STUDIO READER (15-SECTION MODAL)  */}
      {/* ------------------------------------------------------------------- */}
      {activeLesson && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 md:p-6 bg-black/85 backdrop-blur-md overflow-y-auto">
          <div
            className="w-full max-w-5xl bg-[#041026] border border-slate-700/80 rounded-3xl shadow-2xl p-5 sm:p-8 space-y-8 max-h-[94vh] overflow-y-auto font-sans text-slate-200"
            style={{
              borderColor: 'var(--theme-border, rgba(0, 240, 181, 0.3))'
            }}
          >
            
            {/* ===============================================================
                SECTION 1: COURSE IDENTITY, TITLE & ACTION TOOLBAR
                =============================================================== */}
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800 pb-5">
              <div className="flex items-start gap-4">
                <SubjectEmblem courseCode={courseCode} size="lg" className="shrink-0 mt-1" />
                <div className="space-y-1.5">
                  <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
                    <span
                      className="px-2.5 py-0.5 rounded-full font-bold border"
                      style={{
                        backgroundColor: `${themeColor}15`,
                        color: themeColor,
                        borderColor: `${themeColor}40`
                      }}
                    >
                      UNIT {activeLesson.unitRoman} • {activeLesson.unitTitle || 'Curriculum Studio'}
                    </span>
                    <span className="text-slate-400">Lesson {activeLesson.lessonNumber}</span>
                    <span className="text-slate-600">•</span>
                    <span className="text-slate-400">~{activeLesson.estimatedMinutes} mins study</span>
                    <span className="text-slate-600">•</span>
                    <span className="px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800 text-[10px]">
                      {activeLesson.difficulty}
                    </span>
                  </div>
                  <h2 className="text-xl sm:text-2xl md:text-3xl font-heading font-extrabold text-white tracking-tight">
                    {activeLesson.title}
                  </h2>
                  <div className="text-xs text-slate-400 font-mono">
                    Anna University Regulation 2023 • MIT Campus • Department of Electronics Engineering
                  </div>
                </div>
              </div>

              {/* Action Toolbar */}
              <div className="flex flex-wrap items-center gap-2 flex-shrink-0 font-mono text-xs">
                <button
                  type="button"
                  onClick={() => toggleBookmark(activeLesson.id)}
                  className={`px-3 py-1.5 rounded-xl border transition-all flex items-center gap-1.5 cursor-pointer ${
                    bookmarks[activeLesson.id]
                      ? "bg-amber-950/80 text-amber-300 border-amber-500/60 font-bold"
                      : "bg-[#020813] text-slate-300 border-slate-800 hover:text-white"
                  }`}
                  title="Bookmark this lesson for rapid resume"
                >
                  <span>{bookmarks[activeLesson.id] ? "⭐ Bookmarked" : "☆ Bookmark"}</span>
                </button>

                <button
                  type="button"
                  onClick={() => toggleComplete(activeLesson.id)}
                  className={`px-3 py-1.5 rounded-xl border transition-all flex items-center gap-1.5 cursor-pointer ${
                    completedLessons[activeLesson.id]
                      ? "bg-emerald-950/80 text-emerald-300 border-emerald-500/60 font-bold"
                      : "bg-[#020813] text-slate-300 border-slate-800 hover:text-white"
                  }`}
                  title="Mark lesson as complete in student record"
                >
                  <span>{completedLessons[activeLesson.id] ? "✓ Finished" : "○ Mark Complete"}</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleExportMarkdown(activeLesson)}
                  className="px-3 py-1.5 rounded-xl bg-[#020813] hover:bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition-all flex items-center gap-1 cursor-pointer"
                  title="Download clean Markdown revision sheet"
                >
                  <span>📥</span>
                  <span>Export .MD</span>
                </button>

                <button
                  type="button"
                  onClick={handlePrint}
                  className="px-2.5 py-1.5 rounded-xl bg-[#020813] hover:bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-all cursor-pointer"
                  title="Print this lesson"
                >
                  <span>🖨️</span>
                </button>

                <a
                  href="/math-studio"
                  className="px-3 py-1.5 rounded-xl bg-cyan-950/40 hover:bg-cyan-900/40 text-cyan-300 border border-cyan-500/30 transition-all flex items-center gap-1"
                  title="Open KaTeX formula studio and scratchpad"
                >
                  <span>📐</span>
                  <span>Math Studio</span>
                </a>

                <button
                  type="button"
                  onClick={() => setActiveLesson(null)}
                  className="p-2 rounded-xl bg-[#020813] border border-slate-800 text-slate-400 hover:text-white transition-all cursor-pointer"
                  title="Close Reader [ESC]"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* ===============================================================
                SECTION 2: MODULAR LEARNING OBJECTIVES & PREREQUISITES
                =============================================================== */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-2 font-mono text-xs">
                <div className="font-bold text-slate-300 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                  <span className="text-emerald-400">🎯</span>
                  <span>Modular Curriculum Learning Objectives:</span>
                </div>
                <ul className="space-y-1.5 text-slate-300">
                  {activeLesson.learningObjectives.map((obj, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-emerald-400 font-bold">✓</span>
                      <span>{obj}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {activeLesson.prerequisites && activeLesson.prerequisites.length > 0 && (
                <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-2 font-mono text-xs">
                  <div className="font-bold text-slate-300 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                    <span className="text-cyan-400">🔗</span>
                    <span>Prerequisites &amp; Prior Knowledge:</span>
                  </div>
                  <ul className="space-y-1.5 text-slate-400">
                    {activeLesson.prerequisites.map((p, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-cyan-400 font-bold">&bull;</span>
                        <span>{p}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* ===============================================================
                SECTION 3: IN-DEPTH ACADEMIC LECTURE EXPOSITION (72ch MEASURE)
                =============================================================== */}
            <section className="space-y-3">
              <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <span>📖</span>
                <span>In-Depth Academic Engineering Exposition:</span>
              </div>
              <div className="academic-lesson-prose p-6 rounded-2xl bg-[#020813]/70 border border-slate-800/80 text-slate-200">
                <div className="whitespace-pre-line leading-relaxed">
                  {activeLesson.markdownNotes}
                </div>
              </div>
            </section>

            {/* ===============================================================
                SECTION 4: EXAM-FOCUSED KATEX FORMULATIONS
                =============================================================== */}
            {activeLesson.formulas.length > 0 && (
              <section className="space-y-3">
                <div className="text-xs font-mono font-bold uppercase tracking-wider flex items-center gap-2" style={{ color: themeColor }}>
                  <span>📐</span>
                  <span>Exam-Focused KaTeX Formulations ({activeLesson.formulas.length}):</span>
                </div>
                <div className="space-y-3">
                  {activeLesson.formulas.map((formula) => (
                    <KatexFormulaCard
                      key={formula.id}
                      formula={formula}
                      themeColor={themeColor}
                      themeFamily={themeFamily}
                    />
                  ))}
                </div>
              </section>
            )}


            {/* ===============================================================
                SECTION 4B: INTERACTIVE IEEE-STANDARD ENGINEERING VISUALIZER
                =============================================================== */}
            <section className="space-y-3">
              <div className="text-xs font-mono font-bold uppercase tracking-wider flex items-center justify-between" style={{ color: themeColor }}>
                <div className="flex items-center gap-2">
                  <span>⚡</span>
                  <span>Interactive IEEE Engineering Visualizer &amp; Dynamic Q-Point:</span>
                </div>
                <span className="text-[10px] text-slate-400 font-normal">
                  Live Mathematical Computation Deck
                </span>
              </div>
              <IeeeEngineeringVisualizer
                courseCode={activeLesson.courseCode}
                initialMode={getCourseVisualizerMode(activeLesson.courseCode)}
                themeColor={themeColor}
              />
            </section>

            {/* ===============================================================
                SECTION 5: STEP-BY-STEP WORKED NUMERICAL EXAMPLE
                =============================================================== */}
            {activeLesson.workedExample && (
              <section className="p-5 sm:p-6 rounded-2xl bg-[#020813] border border-slate-800 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                  <div className="flex items-center gap-2 font-mono">
                    <span className="text-lg">🧮</span>
                    <h4 className="font-heading font-bold text-base text-white">
                      Step-by-Step Worked Numerical Example
                    </h4>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                    Anna University Style Numerical
                  </span>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 text-xs sm:text-sm text-slate-200 font-sans leading-relaxed">
                  <strong>Problem:</strong> {activeLesson.workedExample.problemStatement}
                </div>

                {/* Given Data Chips */}
                <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
                  <span className="text-slate-500 font-bold">Given Parameters:</span>
                  {Object.entries(activeLesson.workedExample.givenData).map(([k, v]) => (
                    <span key={k} className="px-2.5 py-1 rounded-lg bg-slate-900 text-slate-300 border border-slate-800">
                      <strong>{k}:</strong> {v}
                    </span>
                  ))}
                </div>

                {/* Calculation Steps */}
                <div className="space-y-3 font-mono text-xs">
                  {activeLesson.workedExample.steps.map((st, i) => (
                    <div key={i} className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1.5">
                      <div className="font-bold text-emerald-400">{st.stepTitle}</div>
                      <p className="text-slate-400 font-sans">{st.explanation}</p>
                      <pre className="p-2.5 rounded-lg bg-[#020813] border border-slate-800 text-slate-200 font-mono text-[11px] overflow-x-auto whitespace-pre-wrap">
                        {st.calculation}
                      </pre>
                    </div>
                  ))}
                </div>

                {/* Final Answer */}
                <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-500/40 font-mono text-xs text-emerald-300 flex items-center justify-between">
                  <div>
                    <span className="font-bold text-white uppercase text-[10px] block">Final Calculated Value:</span>
                    <span className="text-emerald-200 font-bold">{activeLesson.workedExample.finalAnswer}</span>
                  </div>
                  <span className="text-lg">✓</span>
                </div>

                {/* Python Verification Snippet */}
                {activeLesson.workedExample.pythonVerificationCode && (
                  <div className="space-y-2 pt-2">
                    <div className="flex items-center justify-between font-mono text-xs">
                      <span className="text-slate-400 font-bold flex items-center gap-1.5">
                        <span>🐍</span>
                        <span>Python / SciPy Verification Snippet:</span>
                      </span>
                      <button
                        type="button"
                        onClick={() => handleCopySnippet(activeLesson.workedExample.pythonVerificationCode)}
                        className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-[10px] transition-colors"
                      >
                        {copiedSnippet ? "✓ Copied" : "Copy Code"}
                      </button>
                    </div>
                    <pre className="p-3.5 rounded-xl bg-[#020813] border border-slate-800 font-mono text-xs text-cyan-300 overflow-x-auto">
                      <code>{activeLesson.workedExample.pythonVerificationCode}</code>
                    </pre>
                  </div>
                )}
              </section>
            )}

            {/* ===============================================================
                SECTION 6: COMPARATIVE ANALYSIS & TRADE-OFF MATRIX
                =============================================================== */}
            {activeLesson.comparisonTable && (
              <section className="space-y-3 font-sans">
                <div className="flex items-center gap-2 font-mono text-xs font-bold uppercase tracking-wider text-slate-400">
                  <span>📊</span>
                  <span>{activeLesson.comparisonTable.title}</span>
                </div>
                <div className="overflow-x-auto rounded-2xl border border-slate-800">
                  <table className="w-full text-left font-mono text-xs">
                    <thead className="bg-[#020813] border-b border-slate-800 text-slate-300">
                      <tr>
                        {activeLesson.comparisonTable.headers.map((h, i) => (
                          <th key={i} className="p-3 font-bold">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/80 bg-[#041026]">
                      {activeLesson.comparisonTable.rows.map((row, rIdx) => (
                        <tr key={rIdx} className="hover:bg-slate-900/50 transition-colors">
                          {row.map((cell, cIdx) => (
                            <td key={cIdx} className={`p-3 ${cIdx === 0 ? "font-bold text-white" : "text-slate-300"}`}>
                              {cell}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}

            {/* ===============================================================
                SECTION 7: ENGINEERING APPLICATIONS, ADVANTAGES & LIMITATIONS
                =============================================================== */}
            {activeLesson.applicationsAndTradeoffs && (
              <section className="grid grid-cols-1 md:grid-cols-3 gap-3 font-mono text-xs">
                {/* Applications */}
                <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-2">
                  <div className="font-bold text-emerald-400 flex items-center gap-1.5">
                    <span>🚀</span>
                    <span>Industry Applications</span>
                  </div>
                  <ul className="space-y-1 text-slate-300 text-[11px] list-disc list-inside">
                    {activeLesson.applicationsAndTradeoffs.applications.map((app, i) => (
                      <li key={i}>{app}</li>
                    ))}
                  </ul>
                </div>

                {/* Advantages */}
                <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-2">
                  <div className="font-bold text-cyan-400 flex items-center gap-1.5">
                    <span>✅</span>
                    <span>Engineering Advantages</span>
                  </div>
                  <ul className="space-y-1 text-slate-300 text-[11px] list-disc list-inside">
                    {activeLesson.applicationsAndTradeoffs.advantages.map((adv, i) => (
                      <li key={i}>{adv}</li>
                    ))}
                  </ul>
                </div>

                {/* Limitations */}
                <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-2">
                  <div className="font-bold text-amber-400 flex items-center gap-1.5">
                    <span>⚠️</span>
                    <span>Hardware Trade-offs</span>
                  </div>
                  <ul className="space-y-1 text-slate-300 text-[11px] list-disc list-inside">
                    {activeLesson.applicationsAndTradeoffs.limitations.map((lim, i) => (
                      <li key={i}>{lim}</li>
                    ))}
                  </ul>
                </div>
              </section>
            )}

            {/* ===============================================================
                SECTION 8: ANNA UNIVERSITY EXAMINATION QUESTIONS
                =============================================================== */}
            {activeLesson.examQuestions && (
              <section className="p-5 sm:p-6 rounded-2xl bg-[#020813] border border-slate-800 space-y-4 font-mono text-xs">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">🏛️</span>
                    <h4 className="font-heading font-bold text-base text-white">
                      Anna University Examination Question Bank
                    </h4>
                  </div>
                  <span className="text-[10px] text-amber-400 font-bold bg-amber-950/60 px-2 py-0.5 rounded border border-amber-500/30">
                    AU Reg 2023 Blueprint
                  </span>
                </div>

                {/* Part A (2-Mark Questions) */}
                <div className="space-y-2.5">
                  <div className="font-bold text-cyan-300 uppercase text-[11px]">
                    Part A: Short Conceptual Questions (2 Marks)
                  </div>
                  {activeLesson.examQuestions.partA.map((q, i) => (
                    <div key={i} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                      <div className="font-bold text-white">
                        Q{i + 1}. {q.question} <span className="text-slate-500 font-normal">[{q.marks} Marks]</span>
                      </div>
                      <div className="text-slate-300 text-[11px] pl-3 border-l-2 border-cyan-500/50">
                        <strong className="text-cyan-400">Answer Key:</strong> {q.answerKey}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Part B (16-Mark University Exam Derivations) */}
                <div className="space-y-2.5 pt-2">
                  <div className="font-bold text-purple-300 uppercase text-[11px]">
                    Part B / C: Analytical &amp; Derivation Questions (13/15/16 Marks)
                  </div>
                  {activeLesson.examQuestions.partB.map((q, i) => (
                    <div key={i} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                      <div className="font-bold text-white">
                        Q{i + 1}. {q.question} <span className="text-slate-500 font-normal">[{q.marks} Marks]</span>
                      </div>
                      <div className="text-slate-300 text-[11px] space-y-1 pl-3 border-l-2 border-purple-500/50">
                        <div className="font-bold text-purple-400">Key Evaluation Steps:</div>
                        <ul className="list-disc list-inside space-y-0.5 text-slate-400">
                          {q.keySteps.map((ks, kIdx) => (
                            <li key={kIdx}>{ks}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}


            {/* ===============================================================
                SECTION 9: FURTHER LEARNING & VERIFIED OPEN ACADEMIC RESOURCES
                =============================================================== */}
            {activeLesson.furtherLearning && activeLesson.furtherLearning.length > 0 && (
              <section className="space-y-3 font-sans">
                <div className="flex items-center justify-between font-mono text-xs">
                  <div className="flex items-center gap-2 font-bold uppercase tracking-wider text-slate-400">
                    <span>🌐</span>
                    <span>Further Learning: Verified Open Academic Resources</span>
                  </div>
                  <span className="text-[10px] text-emerald-400 font-mono">
                    Legally Free Open Access
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {activeLesson.furtherLearning.map((res, i) => (
                    <a
                      key={i}
                      href={res.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-4 rounded-2xl bg-[#020813] border border-slate-800 hover:border-emerald-500/40 transition-all group flex flex-col justify-between space-y-3 shadow-md"
                    >
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between text-[10px] font-mono">
                          <span className="px-2 py-0.5 rounded bg-slate-900 text-emerald-400 font-bold border border-emerald-500/30">
                            {res.provider}
                          </span>
                          <span className="text-slate-500">{res.license}</span>
                        </div>
                        <div className="font-heading font-bold text-xs sm:text-sm text-white group-hover:text-emerald-300 transition-colors">
                          {res.name}
                        </div>
                        <div className="text-[11px] text-slate-400 font-sans line-clamp-2">
                          {res.recommendedTopics}
                        </div>
                      </div>

                      <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 group-hover:text-emerald-400 transition-colors pt-2 border-t border-slate-800/80">
                        <span>{res.type}</span>
                        <span>Open Resource &rarr;</span>
                      </div>
                    </a>
                  ))}
                </div>
              </section>
            )}

            {/* Academic Open Resource & Google Drive Vault */}
            <section className="pt-2">
              <AcademicResourceVault embedded={true} />
            </section>

            {/* Standalone Interactive ECE Mini-Applets Suite (Phase 13) */}
            <section className="pt-2">
              <div className="rounded-2xl border border-slate-800 bg-[#041026] overflow-hidden">
                <button
                  type="button"
                  onClick={() => setShowInteractiveApplets(!showInteractiveApplets)}
                  className="w-full p-4 flex items-center justify-between text-left hover:bg-slate-900/60 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="p-2 rounded-xl bg-sky-500/10 text-sky-400 border border-sky-500/20 text-lg">
                      🎛️
                    </span>
                    <div>
                      <h4 className="text-sm font-bold text-white flex items-center gap-2">
                        Interactive Engineering Mini-Applets
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/40">
                          Convolution • Op-Amps • Logic • Serial
                        </span>
                      </h4>
                      <p className="text-[11px] text-slate-400">
                        Zero-polling visual sandbox for testing waveforms, logic gates, and packet frames.
                      </p>
                    </div>
                  </div>
                  <span className="text-xs font-mono text-sky-400 font-bold px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700">
                    {showInteractiveApplets ? 'Hide Applets ▲' : 'Open Applets ▼'}
                  </span>
                </button>

                {showInteractiveApplets && (
                  <div className="p-4 border-t border-slate-800 bg-slate-950/80">
                    <EceInteractiveLabApplets />
                  </div>
                )}
              </div>
            </section>

            {/* ===============================================================
                SECTION 10: SIMULATION BRIDGE BANNER (IF AVAILABLE)
                =============================================================== */}
            {activeLesson.simulationBridge && (
              <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-950/40 via-teal-950/30 to-cyan-950/40 border border-emerald-500/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3 font-mono text-xs">
                <div className="space-y-0.5">
                  <div className="font-bold text-emerald-400 flex items-center gap-1.5">
                    <span>⚡</span>
                    <span>Associated Laboratory Simulator: {activeLesson.simulationBridge.experimentName}</span>
                  </div>
                  <div className="text-slate-300 text-[11px]">
                    Tool: <strong className="text-white">{activeLesson.simulationBridge.tool}</strong> • {activeLesson.simulationBridge.actionDescription}
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  <button
                    type="button"
                    onClick={() => handleTransmitStimulus(activeLesson)}
                    className="px-3 py-2 rounded-xl bg-cyan-950/60 hover:bg-cyan-900/60 text-cyan-300 border border-cyan-500/40 text-[11px] font-bold transition-all flex items-center gap-1.5 cursor-pointer"
                    title="Transmit hardware serial command to active Wokwi hardware bridge"
                  >
                    <span>{stimulusTransmitted ? '✓ Transmitted' : '📡 Send Serial Stimulus'}</span>
                  </button>
                  {onLaunchSimulator && (
                    <button
                      type="button"
                      onClick={() => {
                        setActiveLesson(null);
                        onLaunchSimulator();
                      }}
                      className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold transition-all shadow-md flex items-center gap-1.5 flex-shrink-0 cursor-pointer"
                    >
                      <span>Launch Simulator</span>
                      <span>&rarr;</span>
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* ===============================================================
                SECTION 11: DEDICATED INTERACTIVE COURSE SIMULATION ISLAND
                =============================================================== */}
            <div className="space-y-2">
              <div className="text-xs font-mono font-bold uppercase tracking-wider flex items-center gap-2" style={{ color: themeColor }}>
                <span>⚡</span>
                <span>Interactive Laboratory Simulation Workbench:</span>
              </div>
              <CourseSimulationIsland
                courseCode={courseCode}
                themeColor={themeColor}
                themeFamily={themeFamily}
                compact={true}
              />
            </div>

            {/* ===============================================================
                SECTION 12: STUDENT PERSONAL STUDY NOTES STUDIO
                =============================================================== */}
            <div className="p-5 rounded-2xl bg-[#020813] border border-slate-800 space-y-3 font-mono text-xs">
              <div className="flex items-center justify-between">
                <div className="font-bold text-white flex items-center gap-1.5">
                  <span>📝</span>
                  <span>Personal Study &amp; Revision Notes Studio:</span>
                </div>
                {noteSavedFeedback && (
                  <span className="text-emerald-400 font-bold animate-pulse text-[11px]">
                    ✓ Notes Saved to Local Profile
                  </span>
                )}
              </div>

              <textarea
                rows={3}
                placeholder="Write your personal derivation notes, key formula mnemonics, or lab experiment observations here..."
                value={currentNoteText}
                onChange={(e) => setCurrentNoteText(e.target.value)}
                className="w-full p-3 rounded-xl bg-[#041026] border border-slate-800 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-emerald-500 transition-colors"
              />

              <div className="flex justify-between items-center pt-1">
                <span className="text-[10px] text-slate-500">
                  Persisted automatically across 18 themes in browser localStorage.
                </span>
                <button
                  type="button"
                  onClick={handleSaveNote}
                  className="px-4 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-emerald-300 font-bold transition-all text-xs cursor-pointer"
                >
                  Save Study Notes
                </button>
              </div>
            </div>

            {/* ===============================================================
                SECTION 13: MODAL FOOTER & KEYBOARD SHORTCUTS
                =============================================================== */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-slate-800 text-xs font-mono text-slate-500">
              <span>VoltCore Apex Academia • Flagship Course Studio</span>
              <button
                type="button"
                onClick={() => setActiveLesson(null)}
                className="hover:text-white transition-colors cursor-pointer self-start sm:self-auto"
              >
                Close Reader [ESC]
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}