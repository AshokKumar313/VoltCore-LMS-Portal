import React, { useState, useEffect, useRef } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Smart Learning Productivity & Study Management Center
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 * ========================================================================================
 */

const DEFAULT_STUDENT_ID = "2023MITEC042";

const SUBJECT_OPTIONS = [
  { code: "EC3352", name: "Digital Systems Design", color: "from-sky-500 to-blue-600" },
  { code: "EC3452", name: "Electromagnetic Fields", color: "from-amber-500 to-orange-600" },
  { code: "EC3451", name: "Linear Integrated Circuits", color: "from-emerald-500 to-teal-600" },
  { code: "EC3491", name: "Communication Systems", color: "from-purple-500 to-indigo-600" },
  { code: "ECE_GENERAL", name: "General ECE Engineering", color: "from-cyan-500 to-blue-500" }
];

const PRESETS = [
  { label: "25m Pomodoro", minutes: 25, type: "POMODORO_25" },
  { label: "50m Deep Work", minutes: 50, type: "DEEP_WORK_50" },
  { label: "15m Revision Sprint", minutes: 15, type: "REVISION_15" },
  { label: "5m Short Break", minutes: 5, type: "BREAK_5" }
];

const INITIAL_SESSIONS = [
  {
    session_id: "SESS_SEED_01",
    student_id: DEFAULT_STUDENT_ID,
    subject_code: "EC3352",
    topic: "FSM State Minimization & Flow Tables",
    duration_minutes: 25,
    session_type: "POMODORO_25",
    focus_score: 5,
    notes: "Completed Mealy to Moore conversion exercises.",
    distraction_free_mode: 1,
    completed_at: new Date(Date.now() - 3 * 3600000).toISOString()
  },
  {
    session_id: "SESS_SEED_02",
    student_id: DEFAULT_STUDENT_ID,
    subject_code: "EC3452",
    topic: "Poynting Vector & Wave Power Density",
    duration_minutes: 50,
    session_type: "DEEP_WORK_50",
    focus_score: 4,
    notes: "Derived instantaneous and time-average Poynting vector.",
    distraction_free_mode: 1,
    completed_at: new Date(Date.now() - 8 * 3600000).toISOString()
  },
  {
    session_id: "SESS_SEED_03",
    student_id: DEFAULT_STUDENT_ID,
    subject_code: "EC3451",
    topic: "Active Butterworth Filter Sallen-Key Topologies",
    duration_minutes: 25,
    session_type: "POMODORO_25",
    focus_score: 5,
    notes: "Calculated cut-off frequencies and Q-factor damping.",
    distraction_free_mode: 0,
    completed_at: new Date(Date.now() - 26 * 3600000).toISOString()
  },
  {
    session_id: "SESS_SEED_04",
    student_id: DEFAULT_STUDENT_ID,
    subject_code: "EC3491",
    topic: "Superheterodyne Receiver IF Image Frequency Rejection",
    duration_minutes: 50,
    session_type: "DEEP_WORK_50",
    focus_score: 5,
    notes: "Plotted tracking curves and calculated IF image response.",
    distraction_free_mode: 1,
    completed_at: new Date(Date.now() - 30 * 3600000).toISOString()
  }
];

const INITIAL_BOOKMARKS = [
  {
    bookmark_id: "BOOK_SEED_01",
    student_id: DEFAULT_STUDENT_ID,
    subject_code: "EC3352",
    topic: "Synchronous Sequential Logic Synthesis",
    resource_url: "/modules",
    tags: ["digital", "fsm", "verilog"],
    notes: "Crucial for Continuous Assessment Test 1 and End-Sem Theory.",
    priority: "HIGH",
    created_at: new Date().toISOString()
  },
  {
    bookmark_id: "BOOK_SEED_02",
    student_id: DEFAULT_STUDENT_ID,
    subject_code: "EC3452",
    topic: "Maxwell's Equations Differential & Integral Forms",
    resource_url: "/ece-knowledge",
    tags: ["em-fields", "maxwell", "boundary-conditions"],
    notes: "Includes vector calculus identities and normal/tangential field transitions.",
    priority: "HIGH",
    created_at: new Date().toISOString()
  },
  {
    bookmark_id: "BOOK_SEED_03",
    student_id: DEFAULT_STUDENT_ID,
    subject_code: "EC3451",
    topic: "Op-Amp Inverting/Non-Inverting Active Filters",
    resource_url: "/simulation",
    tags: ["analog", "op-amp", "spice"],
    notes: "Interactive SPICE simulations for Bode magnitude and phase response.",
    priority: "MEDIUM",
    created_at: new Date().toISOString()
  },
  {
    bookmark_id: "BOOK_SEED_04",
    student_id: DEFAULT_STUDENT_ID,
    subject_code: "EC3491",
    topic: "FM Modulation Index & Carson's Bandwidth Rule",
    resource_url: "/ece-knowledge",
    tags: ["communication", "fm", "bessel"],
    notes: "Bessel function power distribution cheat sheet and calculation examples.",
    priority: "MEDIUM",
    created_at: new Date().toISOString()
  }
];

const INITIAL_REVISION_QUEUE = [
  {
    queue_id: "REV_SEED_01",
    student_id: DEFAULT_STUDENT_ID,
    subject_code: "EC3452",
    topic: "Boundary Conditions for Dielectric-Dielectric Interfaces",
    confidence_level: 2,
    last_reviewed_at: new Date(Date.now() - 4 * 86400000).toISOString(),
    next_review_due: new Date(Date.now() - 1 * 86400000).toISOString(),
    decay_interval_days: 3,
    urgency_score: 2.67,
    status: "DUE"
  },
  {
    queue_id: "REV_SEED_02",
    student_id: DEFAULT_STUDENT_ID,
    subject_code: "EC3352",
    topic: "Algorithmic State Machines (ASM) Charts",
    confidence_level: 4,
    last_reviewed_at: new Date(Date.now() - 2 * 86400000).toISOString(),
    next_review_due: new Date(Date.now() + 5 * 86400000).toISOString(),
    decay_interval_days: 7,
    urgency_score: 0.57,
    status: "PENDING"
  },
  {
    queue_id: "REV_SEED_03",
    student_id: DEFAULT_STUDENT_ID,
    subject_code: "EC3451",
    topic: "Instrumentation Amplifier 3-Op-Amp CMRR Derivation",
    confidence_level: 3,
    last_reviewed_at: new Date(Date.now() - 3 * 86400000).toISOString(),
    next_review_due: new Date().toISOString(),
    decay_interval_days: 3,
    urgency_score: 3.0,
    status: "DUE"
  },
  {
    queue_id: "REV_SEED_04",
    student_id: DEFAULT_STUDENT_ID,
    subject_code: "EC3491",
    topic: "Nyquist Criterion for Zero ISI and Raised Cosine Filter",
    confidence_level: 5,
    last_reviewed_at: new Date(Date.now() - 1 * 86400000).toISOString(),
    next_review_due: new Date(Date.now() + 13 * 86400000).toISOString(),
    decay_interval_days: 14,
    urgency_score: 0.07,
    status: "PENDING"
  }
];

export default function LearningProductivityHub() {
  const [activeTab, setActiveTab] = useState('pomodoro'); // 'pomodoro' | 'streaks' | 'revision' | 'bookmarks'
  
  // Productivity & Streak States
  const [streakData, setStreakData] = useState({
    current_streak_days: 7,
    longest_streak_days: 14,
    total_study_minutes: 1420,
    total_study_hours: 23.7,
    total_sessions_completed: 38,
    is_active_today: true,
    last_active_date: new Date().toISOString().substring(0, 10),
    streak_history: []
  });

  const [sessions, setSessions] = useState(INITIAL_SESSIONS);
  const [bookmarks, setBookmarks] = useState(INITIAL_BOOKMARKS);
  const [revisionQueue, setRevisionQueue] = useState(INITIAL_REVISION_QUEUE);

  // Filter States
  const [bookmarkSubjectFilter, setBookmarkSubjectFilter] = useState('ALL');
  const [bookmarkSearch, setBookmarkSearch] = useState('');

  // Pomodoro Timer States
  const [timerSeconds, setTimerSeconds] = useState(25 * 60);
  const [initialDurationMins, setInitialDurationMins] = useState(25);
  const [activePresetType, setActivePresetType] = useState('POMODORO_25');
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [selectedSubject, setSelectedSubject] = useState('EC3352');
  const [sessionTopic, setSessionTopic] = useState('Digital Logic Synthesis');
  const [sessionNotes, setSessionNotes] = useState('');
  const [focusRating, setFocusRating] = useState(5);
  const [distractionFreeMode, setDistractionFreeMode] = useState(false);

  // Add Bookmark Form State
  const [newBookmarkTopic, setNewBookmarkTopic] = useState('');
  const [newBookmarkUrl, setNewBookmarkUrl] = useState('/modules');
  const [newBookmarkSub, setNewBookmarkSub] = useState('EC3451');
  const [newBookmarkNotes, setNewBookmarkNotes] = useState('');
  const [newBookmarkPriority, setNewBookmarkPriority] = useState('MEDIUM');
  const [showAddBookmarkModal, setShowAddBookmarkModal] = useState(false);

  // Quick Notification Toast
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  // Timer Ref
  const timerRef = useRef(null);

  // Play gentle Web Audio chime on session complete
  const playCompletionChime = () => {
    try {
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(587.33, audioCtx.currentTime); // D5
      osc.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.3); // A5
      gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.8);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.8);
    } catch (e) {
      // AudioContext unavailable or blocked
    }
  };

  // Timer Effect
  useEffect(() => {
    if (isTimerRunning) {
      timerRef.current = setInterval(() => {
        setTimerSeconds((prev) => {
          if (prev <= 1) {
            clearInterval(timerRef.current);
            setIsTimerRunning(false);
            playCompletionChime();
            handleLogSessionAuto();
            showToast("🎉 Session Completed! Great focus session logged.");
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isTimerRunning, initialDurationMins, selectedSubject, sessionTopic, focusRating, distractionFreeMode]);

  // Load Overview from API on Mount (with fallback)
  useEffect(() => {
    fetch('/api/productivity/overview?student_id=' + DEFAULT_STUDENT_ID)
      .then((res) => {
        if (!res.ok) throw new Error('API offline');
        return res.json();
      })
      .then((data) => {
        if (data.streak) setStreakData(data.streak);
        if (data.recent_sessions && data.recent_sessions.length > 0) setSessions(data.recent_sessions);
        if (data.top_revision_items && data.top_revision_items.length > 0) setRevisionQueue(data.top_revision_items);
      })
      .catch(() => {
        // Fallback to local default state seamlessly
      });
  }, []);

  const handleSelectPreset = (preset) => {
    setIsTimerRunning(false);
    setInitialDurationMins(preset.minutes);
    setActivePresetType(preset.type);
    setTimerSeconds(preset.minutes * 60);
  };

  const handleResetTimer = () => {
    setIsTimerRunning(false);
    setTimerSeconds(initialDurationMins * 60);
  };

  const handleToggleTimer = () => {
    if (timerSeconds === 0) {
      setTimerSeconds(initialDurationMins * 60);
    }
    setIsTimerRunning(!isTimerRunning);
  };

  const handleLogSessionAuto = () => {
    const newSession = {
      session_id: `SESS_${Date.now()}`,
      student_id: DEFAULT_STUDENT_ID,
      subject_code: selectedSubject,
      topic: sessionTopic || "Focus Session",
      duration_minutes: initialDurationMins,
      session_type: activePresetType,
      focus_score: focusRating,
      notes: sessionNotes || "Completed timed study block.",
      distraction_free_mode: distractionFreeMode ? 1 : 0,
      completed_at: new Date().toISOString()
    };

    setSessions([newSession, ...sessions]);

    // Update streak locally
    setStreakData((prev) => {
      const newMinutes = prev.total_study_minutes + initialDurationMins;
      const isConsecutive = true;
      const newStreak = prev.is_active_today ? prev.current_streak_days : prev.current_streak_days + 1;
      return {
        ...prev,
        current_streak_days: newStreak,
        longest_streak_days: Math.max(prev.longest_streak_days, newStreak),
        total_study_minutes: newMinutes,
        total_study_hours: Math.round((newMinutes / 60) * 10) / 10,
        total_sessions_completed: prev.total_sessions_completed + 1,
        is_active_today: true
      };
    });

    // POST to backend API
    fetch('/api/productivity/session/log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newSession)
    }).catch(() => {});
  };

  const handleManualLog = (e) => {
    e.preventDefault();
    handleLogSessionAuto();
    showToast("✅ Study session recorded & streak updated!");
  };

  const handleUpdateRevisionConfidence = (queueId, confidence) => {
    setRevisionQueue((prev) =>
      prev.map((item) => {
        if (item.queue_id === queueId) {
          const newInterval = confidence >= 4 ? item.decay_interval_days * 2 : confidence === 3 ? item.decay_interval_days : 1;
          const nextDue = new Date(Date.now() + newInterval * 86400000).toISOString();
          return {
            ...item,
            confidence_level: confidence,
            decay_interval_days: newInterval,
            next_review_due: nextDue,
            status: "PENDING",
            urgency_score: Math.max(0.1, Math.round(((6 - confidence) / newInterval) * 10) / 10)
          };
        }
        return item;
      })
    );

    fetch('/api/productivity/revision_queue/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        queue_id: queueId,
        student_id: DEFAULT_STUDENT_ID,
        confidence_level: confidence
      })
    }).catch(() => {});

    showToast("🧠 Confidence updated! Next review scheduled.");
  };

  const handleAddBookmarkSubmit = (e) => {
    e.preventDefault();
    if (!newBookmarkTopic) return;

    const newBookmark = {
      bookmark_id: `BOOK_${Date.now()}`,
      student_id: DEFAULT_STUDENT_ID,
      subject_code: newBookmarkSub,
      topic: newBookmarkTopic,
      resource_url: newBookmarkUrl,
      tags: [newBookmarkSub.toLowerCase(), "study-note"],
      notes: newBookmarkNotes,
      priority: newBookmarkPriority,
      created_at: new Date().toISOString()
    };

    setBookmarks([newBookmark, ...bookmarks]);
    setShowAddBookmarkModal(false);
    setNewBookmarkTopic('');
    setNewBookmarkNotes('');

    fetch('/api/productivity/bookmarks/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newBookmark)
    }).catch(() => {});

    showToast("🔖 Smart bookmark saved successfully!");
  };

  const handleDeleteBookmark = (id) => {
    setBookmarks(bookmarks.filter((b) => b.bookmark_id !== id));
    fetch('/api/productivity/bookmarks/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bookmark_id: id, student_id: DEFAULT_STUDENT_ID })
    }).catch(() => {});
    showToast("🗑️ Bookmark removed.");
  };

  // Format time mm:ss
  const formatTime = (totalSecs) => {
    const mins = Math.floor(totalSecs / 60);
    const secs = totalSecs % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Filter Bookmarks
  const filteredBookmarks = bookmarks.filter((b) => {
    const matchesSub = bookmarkSubjectFilter === 'ALL' || b.subject_code === bookmarkSubjectFilter;
    const matchesSearch = !bookmarkSearch ||
      b.topic.toLowerCase().includes(bookmarkSearch.toLowerCase()) ||
      b.notes.toLowerCase().includes(bookmarkSearch.toLowerCase()) ||
      (b.tags && b.tags.some(t => t.toLowerCase().includes(bookmarkSearch.toLowerCase())));
    return matchesSub && matchesSearch;
  });

  // Calculate subject hours for stats
  const subjectHours = SUBJECT_OPTIONS.reduce((acc, sub) => {
    const mins = sessions
      .filter((s) => s.subject_code === sub.code)
      .reduce((sum, s) => sum + s.duration_minutes, 0);
    acc[sub.code] = Math.round((mins / 60) * 10) / 10;
    return acc;
  }, {});

  const dueRevisionCount = revisionQueue.filter((r) => r.status === 'DUE').length;

  return (
    <div className={`w-full min-h-screen text-slate-100 transition-colors duration-500 ${distractionFreeMode ? 'bg-slate-950 px-4 py-8' : 'bg-slate-900/60 p-4 md:p-8'}`}>
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-emerald-600/95 text-white px-5 py-3 rounded-xl shadow-2xl border border-emerald-400/40 backdrop-blur-md flex items-center gap-3 animate-fade-in">
          <svg className="w-5 h-5 text-emerald-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
          </svg>
          <span className="text-sm font-medium">{toastMessage}</span>
        </div>
      )}

      {/* Header Container */}
      {!distractionFreeMode && (
        <div className="max-w-7xl mx-auto mb-8">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  MIT Campus • ECE Regulation 2023
                </span>
                <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  Student: Ashok Kumar A ({DEFAULT_STUDENT_ID})
                </span>
              </div>
              <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
                Smart Learning Productivity Hub
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                High-focus study management, Pomodoro sessions, spaced revision decay, and smart learning bookmarks.
              </p>
            </div>

            {/* Quick Metrics Ribbon */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-3 text-center">
                <div className="flex items-center justify-center gap-1 text-xs text-amber-400 font-medium">
                  <span>🔥</span> Daily Streak
                </div>
                <div className="text-xl font-bold text-white mt-1">{streakData.current_streak_days} Days</div>
              </div>
              <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-3 text-center">
                <div className="flex items-center justify-center gap-1 text-xs text-emerald-400 font-medium">
                  <span>⏳</span> Total Study
                </div>
                <div className="text-xl font-bold text-white mt-1">{streakData.total_study_hours}h</div>
              </div>
              <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-3 text-center">
                <div className="flex items-center justify-center gap-1 text-xs text-cyan-400 font-medium">
                  <span>📚</span> Sessions
                </div>
                <div className="text-xl font-bold text-white mt-1">{streakData.total_sessions_completed}</div>
              </div>
              <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-3 text-center">
                <div className="flex items-center justify-center gap-1 text-xs text-rose-400 font-medium">
                  <span>⚡</span> Due Revision
                </div>
                <div className="text-xl font-bold text-rose-300 mt-1">{dueRevisionCount} Topics</div>
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex flex-wrap items-center gap-2 mt-6">
            <button
              onClick={() => setActiveTab('pomodoro')}
              className={`px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 transition-all ${
                activeTab === 'pomodoro'
                  ? 'bg-emerald-500 text-slate-950 font-semibold shadow-lg shadow-emerald-500/20'
                  : 'bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-white'
              }`}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Pomodoro & Focus Timer
            </button>

            <button
              onClick={() => setActiveTab('streaks')}
              className={`px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 transition-all ${
                activeTab === 'streaks'
                  ? 'bg-emerald-500 text-slate-950 font-semibold shadow-lg shadow-emerald-500/20'
                  : 'bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-white'
              }`}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
              </svg>
              Streaks & Habit Tracker
            </button>

            <button
              onClick={() => setActiveTab('revision')}
              className={`px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 transition-all ${
                activeTab === 'revision'
                  ? 'bg-emerald-500 text-slate-950 font-semibold shadow-lg shadow-emerald-500/20'
                  : 'bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-white'
              }`}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              Spaced Revision Queue ({dueRevisionCount})
            </button>

            <button
              onClick={() => setActiveTab('bookmarks')}
              className={`px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 transition-all ${
                activeTab === 'bookmarks'
                  ? 'bg-emerald-500 text-slate-950 font-semibold shadow-lg shadow-emerald-500/20'
                  : 'bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-white'
              }`}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
              Smart Bookmarks ({bookmarks.length})
            </button>

            <div className="ml-auto flex items-center gap-2">
              <button
                onClick={() => setDistractionFreeMode(!distractionFreeMode)}
                className={`px-3 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 border transition-all ${
                  distractionFreeMode
                    ? 'bg-purple-600/30 text-purple-300 border-purple-500/40'
                    : 'bg-slate-800 text-slate-400 hover:text-slate-200 border-slate-700/60'
                }`}
              >
                <span>🎯</span> Distraction-Free Mode
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="max-w-7xl mx-auto">
        {/* DISTRACTION-FREE TOP EXIT BAR */}
        {distractionFreeMode && (
          <div className="flex items-center justify-between pb-6 mb-6 border-b border-slate-800">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Distraction-Free Focus Mode Active • {selectedSubject}</span>
            </div>
            <button
              onClick={() => setDistractionFreeMode(false)}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 border border-slate-700 transition-colors"
            >
              Exit Distraction-Free Mode ✕
            </button>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 1: POMODORO & DEEP WORK TIMER */}
        {/* ========================================================================= */}
        {activeTab === 'pomodoro' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Timer Column (7 cols) */}
            <div className="lg:col-span-7 space-y-6">
              <div className="bg-gradient-to-b from-slate-800/80 to-slate-900/90 border border-slate-700/60 rounded-2xl p-6 md:p-8 text-center relative overflow-hidden backdrop-blur-md">
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-500"></div>

                {/* Preset Chips */}
                <div className="flex flex-wrap items-center justify-center gap-2 mb-8">
                  {PRESETS.map((p) => (
                    <button
                      key={p.type}
                      onClick={() => handleSelectPreset(p)}
                      className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                        activePresetType === p.type
                          ? 'bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20'
                          : 'bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-700/50'
                      }`}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>

                {/* Big Digital Clock Display */}
                <div className="py-6">
                  <div className="text-6xl md:text-8xl font-black font-mono tracking-tight text-white select-none drop-shadow-md">
                    {formatTime(timerSeconds)}
                  </div>
                  <div className="text-xs uppercase tracking-widest text-emerald-400 font-semibold mt-2">
                    {isTimerRunning ? '● SESSION IN PROGRESS' : '○ TIMER PAUSED'}
                  </div>
                </div>

                {/* Control Action Buttons */}
                <div className="flex items-center justify-center gap-4 mt-6">
                  <button
                    onClick={handleToggleTimer}
                    className={`px-8 py-3.5 rounded-xl font-bold text-base transition-all shadow-lg flex items-center gap-2 ${
                      isTimerRunning
                        ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-amber-500/20'
                        : 'bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-emerald-500/20'
                    }`}
                  >
                    {isTimerRunning ? (
                      <>
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Pause Session
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Start Focus
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleResetTimer}
                    className="px-5 py-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 text-sm font-semibold transition-colors"
                  >
                    Reset
                  </button>

                  <button
                    onClick={handleLogSessionAuto}
                    className="px-5 py-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-emerald-400 hover:text-emerald-300 border border-emerald-500/30 text-sm font-semibold transition-colors"
                    title="Force Log Completed Session Now"
                  >
                    ✓ Log Session
                  </button>
                </div>
              </div>

              {/* Active Session Configuration */}
              <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
                <h3 className="text-base font-semibold text-white mb-4 flex items-center gap-2">
                  <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  Active Session Profile
                </h3>

                <form onSubmit={handleManualLog} className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Target Subject Code</label>
                      <select
                        value={selectedSubject}
                        onChange={(e) => setSelectedSubject(e.target.value)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500"
                      >
                        {SUBJECT_OPTIONS.map((s) => (
                          <option key={s.code} value={s.code}>
                            {s.code} - {s.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Focus Rating (1 - 5 Stars)</label>
                      <div className="flex items-center gap-2 pt-1">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <button
                            type="button"
                            key={star}
                            onClick={() => setFocusRating(star)}
                            className={`text-xl transition-transform hover:scale-110 ${star <= focusRating ? 'text-amber-400' : 'text-slate-600'}`}
                          >
                            ★
                          </button>
                        ))}
                        <span className="text-xs text-slate-400 ml-2">({focusRating}/5)</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Specific Topic or Syllabus Module</label>
                    <input
                      type="text"
                      value={sessionTopic}
                      onChange={(e) => setSessionTopic(e.target.value)}
                      placeholder="e.g. Waveguides, Transistor Biasing, PLL Synthesizers"
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 placeholder-slate-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Session Key Takeaways / Derivations Solved</label>
                    <textarea
                      rows="2"
                      value={sessionNotes}
                      onChange={(e) => setSessionNotes(e.target.value)}
                      placeholder="e.g. Proved setup time slack inequality, derived Poynting vector integral form..."
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-emerald-500 placeholder-slate-500 resize-none"
                    ></textarea>
                  </div>
                </form>
              </div>
            </div>

            {/* Recent Sessions Ledger (5 cols) */}
            <div className="lg:col-span-5 space-y-6">
              <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-base font-semibold text-white flex items-center gap-2">
                    <svg className="w-4 h-4 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Recent Completed Sessions
                  </h3>
                  <span className="text-xs text-slate-400">{sessions.length} total</span>
                </div>

                <div className="space-y-3 max-h-[480px] overflow-y-auto pr-1">
                  {sessions.map((sess) => (
                    <div
                      key={sess.session_id}
                      className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 hover:border-slate-700 transition-colors"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="px-2 py-0.5 rounded text-xs font-bold bg-slate-800 text-emerald-400 border border-emerald-500/20">
                          {sess.subject_code}
                        </span>
                        <div className="flex items-center gap-1.5 text-xs text-amber-400">
                          <span>{'★'.repeat(sess.focus_score)}</span>
                          <span className="text-slate-500 text-[11px]">• {sess.duration_minutes}m</span>
                        </div>
                      </div>

                      <div className="text-sm font-semibold text-slate-200 mt-2">
                        {sess.topic}
                      </div>

                      {sess.notes && (
                        <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                          {sess.notes}
                        </p>
                      )}

                      <div className="text-[10px] text-slate-500 mt-2 flex items-center justify-between">
                        <span>{new Date(sess.completed_at).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
                        {sess.distraction_free_mode === 1 && (
                          <span className="text-purple-400 font-medium">🎯 Distraction-Free</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 2: STREAKS & HABIT TRACKER */}
        {/* ========================================================================= */}
        {activeTab === 'streaks' && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Daily Streak Card */}
              <div className="bg-gradient-to-br from-amber-500/10 via-slate-800 to-slate-900 border border-amber-500/30 rounded-2xl p-6 relative overflow-hidden">
                <div className="text-amber-400 text-xs font-bold uppercase tracking-wider">Active Study Streak</div>
                <div className="text-5xl font-black text-white mt-2 flex items-baseline gap-2">
                  {streakData.current_streak_days}
                  <span className="text-lg text-slate-400 font-semibold">Days Continuous</span>
                </div>
                <p className="text-xs text-slate-300 mt-3">
                  🔥 Active habit streak! Studying daily directly elevates end-semester retention and NBA attainment marks.
                </p>
                <div className="mt-4 pt-4 border-t border-slate-700/60 flex items-center justify-between text-xs text-slate-400">
                  <span>Longest Streak Record:</span>
                  <span className="font-bold text-white">{streakData.longest_streak_days} Days</span>
                </div>
              </div>

              {/* Total Hours Card */}
              <div className="bg-gradient-to-br from-emerald-500/10 via-slate-800 to-slate-900 border border-emerald-500/30 rounded-2xl p-6 relative overflow-hidden">
                <div className="text-emerald-400 text-xs font-bold uppercase tracking-wider">Total Time Logged</div>
                <div className="text-5xl font-black text-white mt-2 flex items-baseline gap-2">
                  {streakData.total_study_hours}
                  <span className="text-lg text-slate-400 font-semibold">Hours</span>
                </div>
                <p className="text-xs text-slate-300 mt-3">
                  ⏳ {streakData.total_study_minutes} minutes spent in verified focused Pomodoro and Deep Work study blocks.
                </p>
                <div className="mt-4 pt-4 border-t border-slate-700/60 flex items-center justify-between text-xs text-slate-400">
                  <span>Average Session:</span>
                  <span className="font-bold text-white">
                    {streakData.total_sessions_completed > 0
                      ? Math.round(streakData.total_study_minutes / streakData.total_sessions_completed)
                      : 0}{' '}
                    mins
                  </span>
                </div>
              </div>

              {/* Sessions Count Card */}
              <div className="bg-gradient-to-br from-cyan-500/10 via-slate-800 to-slate-900 border border-cyan-500/30 rounded-2xl p-6 relative overflow-hidden">
                <div className="text-cyan-400 text-xs font-bold uppercase tracking-wider">Study Sessions</div>
                <div className="text-5xl font-black text-white mt-2 flex items-baseline gap-2">
                  {streakData.total_sessions_completed}
                  <span className="text-lg text-slate-400 font-semibold">Blocks</span>
                </div>
                <p className="text-xs text-slate-300 mt-3">
                  🎯 Consistent micro-study pacing preserves cognitive endurance without thermal brain fatigue.
                </p>
                <div className="mt-4 pt-4 border-t border-slate-700/60 flex items-center justify-between text-xs text-slate-400">
                  <span>Today's Status:</span>
                  <span className={`font-bold ${streakData.is_active_today ? 'text-emerald-400' : 'text-amber-400'}`}>
                    {streakData.is_active_today ? '✓ Active Today' : 'Pending Study Block'}
                  </span>
                </div>
              </div>
            </div>

            {/* 7-Day Activity Matrix */}
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
              <h3 className="text-base font-semibold text-white mb-4 flex items-center gap-2">
                <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Weekly Habit Consistency (Last 7 Days)
              </h3>

              <div className="grid grid-cols-7 gap-3 text-center">
                {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, idx) => (
                  <div key={day} className="bg-slate-900 border border-slate-800 rounded-xl p-3 flex flex-col items-center gap-2">
                    <span className="text-xs text-slate-400 font-medium">{day}</span>
                    <div className="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center font-bold text-xs">
                      ✓
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono">Completed</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Subject Time Distribution */}
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
              <h3 className="text-base font-semibold text-white mb-6 flex items-center gap-2">
                <svg className="w-4 h-4 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
                </svg>
                Curriculum Study Time Allocation
              </h3>

              <div className="space-y-4">
                {SUBJECT_OPTIONS.map((sub) => {
                  const hours = subjectHours[sub.code] || 0;
                  const pct = streakData.total_study_hours > 0 ? Math.round((hours / streakData.total_study_hours) * 100) : 0;
                  return (
                    <div key={sub.code}>
                      <div className="flex items-center justify-between text-xs mb-1.5">
                        <span className="font-semibold text-slate-200">
                          {sub.code} • {sub.name}
                        </span>
                        <span className="text-slate-400 font-mono">
                          {hours}h ({pct}%)
                        </span>
                      </div>
                      <div className="w-full h-2.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                        <div
                          className={`h-full bg-gradient-to-r ${sub.color} rounded-full transition-all duration-700`}
                          style={{ width: `${Math.min(100, pct)}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 3: SPACED REVISION QUEUE */}
        {/* ========================================================================= */}
        {activeTab === 'revision' && (
          <div className="space-y-6">
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-700/60">
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <svg className="w-5 h-5 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Spaced Repetition Priority Queue
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Topics ranked dynamically by memory decay interval and inverted confidence. Review due topics to maximize long-term retention.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30">
                    {dueRevisionCount} Topics Overdue
                  </span>
                </div>
              </div>

              {/* Table of Revision Items */}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-slate-700 text-xs text-slate-400 uppercase tracking-wider">
                      <th className="pb-3 font-semibold">Subject & Topic</th>
                      <th className="pb-3 font-semibold">Decay / Due</th>
                      <th className="pb-3 font-semibold text-center">Urgency</th>
                      <th className="pb-3 font-semibold text-center">Current Confidence</th>
                      <th className="pb-3 font-semibold text-right">Quick Review Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {revisionQueue.map((item) => (
                      <tr key={item.queue_id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="py-4 pr-4">
                          <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-800 text-cyan-400 border border-cyan-500/20 mr-2">
                            {item.subject_code}
                          </span>
                          <span className="font-medium text-slate-200">{item.topic}</span>
                        </td>

                        <td className="py-4 text-xs">
                          <div className={`font-semibold ${item.status === 'DUE' ? 'text-rose-400' : 'text-slate-400'}`}>
                            {item.status === 'DUE' ? '⚠️ Due for Review' : `Due in ${item.decay_interval_days}d`}
                          </div>
                          <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                            Spacing: {item.decay_interval_days} days
                          </div>
                        </td>

                        <td className="py-4 text-center">
                          <span
                            className={`px-2.5 py-1 rounded-md text-xs font-bold font-mono ${
                              item.urgency_score >= 2.0
                                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                                : item.urgency_score >= 1.0
                                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                                : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            }`}
                          >
                            {item.urgency_score}x
                          </span>
                        </td>

                        <td className="py-4 text-center">
                          <div className="flex items-center justify-center gap-1 text-amber-400 text-sm">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <span key={star} className={star <= item.confidence_level ? 'text-amber-400' : 'text-slate-700'}>
                                ★
                              </span>
                            ))}
                          </div>
                        </td>

                        <td className="py-4 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              onClick={() => handleUpdateRevisionConfidence(item.queue_id, 2)}
                              className="px-2.5 py-1 rounded-lg text-xs font-medium bg-rose-900/40 hover:bg-rose-900/70 text-rose-300 border border-rose-700/50 transition-colors"
                              title="Hard (Review tomorrow)"
                            >
                              Hard (1d)
                            </button>
                            <button
                              onClick={() => handleUpdateRevisionConfidence(item.queue_id, 4)}
                              className="px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-900/40 hover:bg-emerald-900/70 text-emerald-300 border border-emerald-700/50 transition-colors"
                              title="Good (Review next week)"
                            >
                              Good (7d)
                            </button>
                            <button
                              onClick={() => handleUpdateRevisionConfidence(item.queue_id, 5)}
                              className="px-2.5 py-1 rounded-lg text-xs font-medium bg-cyan-900/40 hover:bg-cyan-900/70 text-cyan-300 border border-cyan-700/50 transition-colors"
                              title="Mastered (Review next month)"
                            >
                              Easy (14d)
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 4: SMART BOOKMARKS & QUICK ACCESS */}
        {/* ========================================================================= */}
        {activeTab === 'bookmarks' && (
          <div className="space-y-6">
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
              {/* Filter and Search Bar */}
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mb-6">
                <div className="flex flex-wrap items-center gap-2">
                  <button
                    onClick={() => setBookmarkSubjectFilter('ALL')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                      bookmarkSubjectFilter === 'ALL'
                        ? 'bg-emerald-500 text-slate-950 font-bold'
                        : 'bg-slate-800 text-slate-400 hover:text-white border border-slate-700'
                    }`}
                  >
                    All Subjects ({bookmarks.length})
                  </button>
                  {SUBJECT_OPTIONS.map((sub) => (
                    <button
                      key={sub.code}
                      onClick={() => setBookmarkSubjectFilter(sub.code)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                        bookmarkSubjectFilter === sub.code
                          ? 'bg-emerald-500 text-slate-950 font-bold'
                          : 'bg-slate-800 text-slate-400 hover:text-white border border-slate-700'
                      }`}
                    >
                      {sub.code}
                    </button>
                  ))}
                </div>

                <div className="flex items-center gap-3 w-full sm:w-auto">
                  <input
                    type="text"
                    value={bookmarkSearch}
                    onChange={(e) => setBookmarkSearch(e.target.value)}
                    placeholder="Search bookmarks, tags, notes..."
                    className="bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 w-full sm:w-64"
                  />
                  <button
                    onClick={() => setShowAddBookmarkModal(true)}
                    className="px-4 py-1.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold transition-all shadow-md shadow-emerald-500/20 whitespace-nowrap"
                  >
                    + Add Bookmark
                  </button>
                </div>
              </div>

              {/* Bookmarks Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredBookmarks.map((b) => (
                  <div
                    key={b.bookmark_id}
                    className="bg-slate-900/80 border border-slate-800 hover:border-slate-700 rounded-xl p-4 transition-all flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between gap-2">
                        <span className="px-2 py-0.5 rounded text-xs font-bold bg-slate-800 text-emerald-400 border border-emerald-500/20">
                          {b.subject_code}
                        </span>
                        <div className="flex items-center gap-2">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                              b.priority === 'HIGH'
                                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                                : 'bg-slate-800 text-slate-400 border border-slate-700'
                            }`}
                          >
                            {b.priority}
                          </span>
                          <button
                            onClick={() => handleDeleteBookmark(b.bookmark_id)}
                            className="text-slate-500 hover:text-rose-400 text-xs"
                            title="Delete Bookmark"
                          >
                            ✕
                          </button>
                        </div>
                      </div>

                      <h4 className="text-sm font-bold text-white mt-2.5">{b.topic}</h4>
                      {b.notes && <p className="text-xs text-slate-400 mt-1">{b.notes}</p>}

                      {b.tags && b.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-3">
                          {b.tags.map((tag, idx) => (
                            <span key={idx} className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 font-mono">
                              #{tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
                      <span className="text-[11px] text-slate-500 font-mono">{b.resource_url}</span>
                      <a
                        href={b.resource_url}
                        className="px-3 py-1 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-semibold transition-colors flex items-center gap-1"
                      >
                        Open Resource →
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Modal: Add Bookmark */}
            {showAddBookmarkModal && (
              <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl animate-fade-in">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
                    <h3 className="text-base font-bold text-white">Add Smart Learning Bookmark</h3>
                    <button
                      onClick={() => setShowAddBookmarkModal(false)}
                      className="text-slate-400 hover:text-white text-sm"
                    >
                      ✕
                    </button>
                  </div>

                  <form onSubmit={handleAddBookmarkSubmit} className="space-y-4">
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Subject Code</label>
                      <select
                        value={newBookmarkSub}
                        onChange={(e) => setNewBookmarkSub(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                      >
                        {SUBJECT_OPTIONS.map((s) => (
                          <option key={s.code} value={s.code}>
                            {s.code} - {s.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Topic / Title</label>
                      <input
                        type="text"
                        required
                        value={newBookmarkTopic}
                        onChange={(e) => setNewBookmarkTopic(e.target.value)}
                        placeholder="e.g. Sallen-Key Active Filter Derivation"
                        className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Resource Route / URL</label>
                      <input
                        type="text"
                        value={newBookmarkUrl}
                        onChange={(e) => setNewBookmarkUrl(e.target.value)}
                        placeholder="/modules, /simulation, /ece-knowledge"
                        className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500 font-mono"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Notes / Key Concepts</label>
                      <textarea
                        rows="2"
                        value={newBookmarkNotes}
                        onChange={(e) => setNewBookmarkNotes(e.target.value)}
                        placeholder="Important exam tips or formula references..."
                        className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500 resize-none"
                      ></textarea>
                    </div>

                    <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                      <button
                        type="button"
                        onClick={() => setShowAddBookmarkModal(false)}
                        className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="px-5 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold transition-all shadow-md shadow-emerald-500/20"
                      >
                        Save Bookmark
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

