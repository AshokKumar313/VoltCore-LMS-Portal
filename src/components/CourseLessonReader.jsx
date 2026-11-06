import React, { useState, useEffect, useMemo } from 'react';
import { getLessonsByCourse, getLessonsByUnit } from '../data/course_lessons_data';
import KatexFormulaCard from './KatexFormulaCard';
import { DepartmentalBadgeIcon } from './CourseShellHub';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Unit-Wise Lesson Library & Student Bookmarking Hub
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead & Systems Architect: Ashok Kumar A
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 *
 * Capabilities:
 *   - Unit-wise curated lesson library across all 5 syllabus units
 *   - Markdown lecture notes reader with theoretical derivations
 *   - KaTeX mathematical formula inspector integration
 *   - Student study notes and persistent bookmarking (localStorage with zero background polling)
 *   - Completion tracking and progress metric visualizer
 * ========================================================================================
 */

const STORAGE_KEY_BOOKMARKS = "voltcore_lesson_bookmarks";
const STORAGE_KEY_COMPLETED = "voltcore_lesson_completed";
const STORAGE_KEY_NOTES = "voltcore_student_study_notes";

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

  // Toggle Complete
  const toggleComplete = (lessonId, e) => {
    if (e) e.stopPropagation();
    setCompletedLessons((prev) => {
      const updated = { ...prev, [lessonId]: !prev[lessonId] };
      try {
        localStorage.setItem(STORAGE_KEY_COMPLETED, JSON.stringify(updated));
      } catch (err) {}
      return updated;
    });
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
              {courseCode} Study Progress &amp; Syllabus Coverage
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
                <div>
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
      {/* 4. ACTIVE LECTURE NOTES & KATEX READER (MODAL / OVERLAY) */}
      {/* ------------------------------------------------------------------- */}
      {activeLesson && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-md overflow-y-auto">
          <div className="w-full max-w-4xl bg-[#041026] border border-slate-700 rounded-3xl shadow-2xl p-6 sm:p-8 space-y-6 max-h-[92vh] overflow-y-auto font-sans">
            
            {/* Header Strip */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-xs font-mono">
                  <span className="px-2.5 py-0.5 rounded-full font-bold" style={{ backgroundColor: `${themeColor}20`, color: themeColor }}>
                    {activeLesson.courseCode} • UNIT {activeLesson.unitRoman}
                  </span>
                  <span className="text-slate-400">Lesson {activeLesson.lessonNumber}</span>
                  <span className="text-slate-600">•</span>
                  <span className="text-slate-400">~{activeLesson.estimatedMinutes} mins study</span>
                </div>
                <h2 className="text-xl sm:text-2xl font-extrabold text-white">
                  {activeLesson.title}
                </h2>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => toggleBookmark(activeLesson.id)}
                  className={`px-3 py-1.5 rounded-xl border font-mono text-xs transition-all flex items-center gap-1.5 ${
                    bookmarks[activeLesson.id]
                      ? "bg-amber-950 text-amber-300 border-amber-500/60 font-bold"
                      : "bg-[#020813] text-slate-300 border-slate-800 hover:text-white"
                  }`}
                >
                  <span>{bookmarks[activeLesson.id] ? "⭐ Bookmarked" : "☆ Bookmark"}</span>
                </button>

                <button
                  onClick={() => toggleComplete(activeLesson.id)}
                  className={`px-3 py-1.5 rounded-xl border font-mono text-xs transition-all flex items-center gap-1.5 ${
                    completedLessons[activeLesson.id]
                      ? "bg-emerald-950 text-emerald-300 border-emerald-500/60 font-bold"
                      : "bg-[#020813] text-slate-300 border-slate-800 hover:text-white"
                  }`}
                >
                  <span>{completedLessons[activeLesson.id] ? "✓ Completed" : "○ Mark Complete"}</span>
                </button>

                <button
                  onClick={() => setActiveLesson(null)}
                  className="p-2 rounded-xl bg-[#020813] border border-slate-800 text-slate-400 hover:text-white text-sm"
                  title="Close Reader"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Learning Objectives */}
            <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-2 font-mono text-xs">
              <div className="font-bold text-slate-400 uppercase tracking-wider text-[10px]">
                Anna University Regulation 2023 Learning Deliverables:
              </div>
              <ul className="space-y-1 text-slate-300 list-disc list-inside">
                {activeLesson.learningObjectives.map((obj, i) => (
                  <li key={i}>{obj}</li>
                ))}
              </ul>
            </div>

            {/* Markdown Lecture Content */}
            <div className="prose prose-invert max-w-none text-slate-300 text-sm leading-relaxed space-y-4">
              <div className="whitespace-pre-line p-5 rounded-2xl bg-[#020813]/60 border border-slate-800/80 font-sans">
                {activeLesson.markdownNotes}
              </div>
            </div>

            {/* KaTeX Mathematical Formulations */}
            {activeLesson.formulas.length > 0 && (
              <div className="space-y-3">
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
              </div>
            )}

            {/* Simulation Bridge Banner (If available) */}
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

                {onLaunchSimulator && (
                  <button
                    onClick={() => {
                      setActiveLesson(null);
                      onLaunchSimulator();
                    }}
                    className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold transition-all shadow-md flex items-center gap-1.5 flex-shrink-0"
                  >
                    <span>Launch Simulator</span>
                    <span>→</span>
                  </button>
                )}
              </div>
            )}

            {/* Student Personal Study Notes */}
            <div className="p-5 rounded-2xl bg-[#020813] border border-slate-800 space-y-3 font-mono text-xs">
              <div className="flex items-center justify-between">
                <div className="font-bold text-white flex items-center gap-1.5">
                  <span>📝</span>
                  <span>Personal Study & Revision Notes:</span>
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

              <div className="flex justify-end">
                <button
                  onClick={handleSaveNote}
                  className="px-4 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-emerald-300 font-bold transition-all text-xs"
                >
                  Save Study Notes
                </button>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex justify-between items-center pt-2 border-t border-slate-800 text-xs font-mono text-slate-500">
              <span>Anna University ECE R2023 Study Module</span>
              <button
                onClick={() => setActiveLesson(null)}
                className="hover:text-white transition-colors"
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
