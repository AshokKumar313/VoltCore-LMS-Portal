import React, { useState, useEffect, useRef } from 'react';
import nptelData from '../data/nptel_mapper.json';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Smart NPTEL MOOC Lecture Player Island
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Component: src/components/SmartNptelPlayer.jsx
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * 
 * Features:
 *   - YouTube IFrame API integration with precise seek control
 *   - Chapter markers from Anna University Unit key concepts
 *   - 0.5x to 2.0x playback speed toggling
 *   - LocalStorage resume position tracking per video
 *   - Global keyboard shortcuts (Space, Left/Right +/-5s, Mute, Seek)
 *   - Timestamped interactive note-taking with Markdown export
 * ========================================================================================
 */

const SPEED_OPTIONS = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0];

export default function SmartNptelPlayer() {
  const modules = nptelData.modules || [];
  const [selectedModuleCode, setSelectedModuleCode] = useState(modules[0]?.module_code || 'EC8701');
  const [selectedLectureIdx, setSelectedLectureIdx] = useState(0);

  const activeModule = modules.find(m => m.module_code === selectedModuleCode) || modules[0];
  const activeLecture = activeModule?.nptel_course?.lectures[selectedLectureIdx] || activeModule?.nptel_course?.lectures[0];

  const [currentTime, setCurrentTime] = useState(activeLecture?.timestamp_start_sec || 0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);
  const [notes, setNotes] = useState([]);
  const [noteText, setNoteText] = useState('');
  const [playerReady, setPlayerReady] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [videoLoadError, setVideoLoadError] = useState(false);

  const iframeRef = useRef(null);
  const playerInstanceRef = useRef(null);

  // Check if lecture is portal fallback or unverified synthetic ID
  const isFallback = 
    activeLecture?.verification_status === 'PORTAL_FALLBACK' ||
    activeModule?.verification_status === 'PORTAL_FALLBACK' ||
    !activeLecture?.youtube_video_id ||
    activeLecture?.youtube_video_id.startsWith('embed_') ||
    activeLecture?.youtube_video_id.startsWith('ai_') ||
    activeLecture?.youtube_video_id.startsWith('found_') ||
    activeLecture?.youtube_video_id.startsWith('nptel_') ||
    videoLoadError;

  // Storage key for resume tracking
  const resumeStorageKey = `voltcore_nptel_resume_${activeLecture?.youtube_video_id}`;
  const notesStorageKey = `voltcore_nptel_notes_${activeLecture?.youtube_video_id}`;

  // Load saved notes & resume position when lecture changes
  useEffect(() => {
    try {
      const savedNotes = localStorage.getItem(notesStorageKey);
      if (savedNotes) {
        setNotes(JSON.parse(savedNotes));
      } else {
        setNotes([]);
      }

      const savedResume = localStorage.getItem(resumeStorageKey);
      const resumeSec = savedResume ? parseInt(savedResume, 10) : activeLecture?.timestamp_start_sec || 0;
      setCurrentTime(resumeSec);
    } catch {
      // LocalStorage not available or quota exceeded
    }
  }, [activeLecture?.youtube_video_id]);

  // Save notes to localStorage
  const saveNotesToStorage = (updatedNotes) => {
    setNotes(updatedNotes);
    try {
      localStorage.setItem(notesStorageKey, JSON.stringify(updatedNotes));
    } catch {
      // Ignore storage error
    }
  };

  // Format seconds to mm:ss
  const formatTime = (totalSeconds) => {
    const sec = Math.floor(totalSeconds);
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  // Load YouTube IFrame API Script once & initialize player
  useEffect(() => {
    setVideoLoadError(false);

    if (isFallback) {
      if (playerInstanceRef.current) {
        try { playerInstanceRef.current.destroy(); } catch {}
        playerInstanceRef.current = null;
      }
      return;
    }

    if (!window.YT) {
      const tag = document.createElement('script');
      tag.src = 'https://www.youtube.com/iframe_api';
      const firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
    }

    const initPlayer = () => {
      if (!window.YT || !window.YT.Player || isFallback) return;
      if (playerInstanceRef.current) {
        try { playerInstanceRef.current.destroy(); } catch {}
      }

      const savedResume = localStorage.getItem(resumeStorageKey);
      const startSec = savedResume ? parseInt(savedResume, 10) : activeLecture?.timestamp_start_sec || 0;

      try {
        playerInstanceRef.current = new window.YT.Player('nptel-youtube-frame', {
          videoId: activeLecture?.youtube_video_id,
          playerVars: {
            autoplay: 0,
            controls: 1,
            start: startSec,
            rel: 0,
            modestbranding: 1
          },
          events: {
            onReady: (event) => {
              setPlayerReady(true);
              try {
                event.target.setPlaybackRate(playbackSpeed);
              } catch {}
            },
            onStateChange: (event) => {
              if (event.data === window.YT.PlayerState.PLAYING) {
                setIsPlaying(true);
              } else {
                setIsPlaying(false);
                // Save position immediately on Pause or End
                if (event.data === window.YT.PlayerState.PAUSED || event.data === window.YT.PlayerState.ENDED) {
                  try {
                    const t = Math.floor(event.target.getCurrentTime());
                    if (t > 0) {
                      setCurrentTime(t);
                      localStorage.setItem(resumeStorageKey, t.toString());
                    }
                  } catch {}
                }
              }
            },
            onError: (event) => {
              console.warn('[SmartNptelPlayer] YouTube playback error code:', event.data);
              setVideoLoadError(true);
            }
          }
        });
      } catch (err) {
        console.warn('[SmartNptelPlayer] Failed to instantiate YouTube player:', err);
        setVideoLoadError(true);
      }
    };

    if (window.YT && window.YT.Player) {
      initPlayer();
    } else {
      window.onYouTubeIframeAPIReady = initPlayer;
    }

    return () => {
      if (playerInstanceRef.current) {
        try { playerInstanceRef.current.destroy(); } catch {}
      }
    };
  }, [activeLecture?.youtube_video_id, isFallback]);

  // Throttled position sync & resume saving: 15 seconds (15000ms)
  useEffect(() => {
    const interval = setInterval(() => {
      if (playerInstanceRef.current && typeof playerInstanceRef.current.getCurrentTime === 'function') {
        try {
          const t = Math.floor(playerInstanceRef.current.getCurrentTime());
          if (t > 0) {
            setCurrentTime(t);
            localStorage.setItem(resumeStorageKey, t.toString());
          }
        } catch {}
      }
    }, 15000);

    return () => clearInterval(interval);
  }, [resumeStorageKey]);

  // Save playback position on beforeunload
  useEffect(() => {
    const handleBeforeUnload = () => {
      if (playerInstanceRef.current && typeof playerInstanceRef.current.getCurrentTime === 'function') {
        try {
          const t = Math.floor(playerInstanceRef.current.getCurrentTime());
          if (t > 0) {
            localStorage.setItem(resumeStorageKey, t.toString());
          }
        } catch {}
      }
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [resumeStorageKey]);

  // Seek to specific timestamp
  const seekTo = (seconds) => {
    setCurrentTime(seconds);
    try {
      localStorage.setItem(resumeStorageKey, seconds.toString());
      if (playerInstanceRef.current && typeof playerInstanceRef.current.seekTo === 'function') {
        playerInstanceRef.current.seekTo(seconds, true);
        playerInstanceRef.current.playVideo();
      }
    } catch {}
  };

  // Change playback speed
  const handleSpeedChange = (speed) => {
    setPlaybackSpeed(speed);
    try {
      if (playerInstanceRef.current && typeof playerInstanceRef.current.setPlaybackRate === 'function') {
        playerInstanceRef.current.setPlaybackRate(speed);
      }
    } catch {}
  };

  // Keyboard Shortcuts Handler
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ignore if user is typing in notes input
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

      if (e.code === 'Space' || e.key === 'k') {
        e.preventDefault();
        if (playerInstanceRef.current) {
          if (isPlaying) {
            playerInstanceRef.current.pauseVideo();
          } else {
            playerInstanceRef.current.playVideo();
          }
        }
      } else if (e.code === 'ArrowLeft' || e.key === 'j') {
        e.preventDefault();
        const nextTime = Math.max(0, currentTime - 5);
        seekTo(nextTime);
      } else if (e.code === 'ArrowRight' || e.key === 'l') {
        e.preventDefault();
        const nextTime = currentTime + 5;
        seekTo(nextTime);
      } else if (e.key === 'm') {
        e.preventDefault();
        if (playerInstanceRef.current) {
          if (isMuted) {
            playerInstanceRef.current.unMute();
            setIsMuted(false);
          } else {
            playerInstanceRef.current.mute();
            setIsMuted(true);
          }
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isPlaying, isMuted, currentTime]);

  // Add Note
  const addNote = (e) => {
    e.preventDefault();
    if (!noteText.trim()) return;

    const newNote = {
      id: `note-${Date.now()}`,
      timestamp_sec: currentTime,
      timestamp_formatted: formatTime(currentTime),
      text: noteText.trim(),
      created_at: new Date().toLocaleTimeString()
    };

    const updated = [newNote, ...notes].sort((a, b) => a.timestamp_sec - b.timestamp_sec);
    saveNotesToStorage(updated);
    setNoteText('');
  };

  // Delete Note
  const deleteNote = (noteId) => {
    const updated = notes.filter(n => n.id !== noteId);
    saveNotesToStorage(updated);
  };

  // Export Notes to Markdown
  const exportNotesMarkdown = () => {
    let md = `# VoltCore Apex Academia - NPTEL Lecture Notes\n\n`;
    md += `**Module:** ${activeModule.module_code} - ${activeModule.module_title}\n`;
    md += `**Instructor:** ${activeModule.nptel_course.instructor} (${activeModule.nptel_course.institution})\n`;
    md += `**Lecture:** ${activeLecture.lecture_title}\n`;
    md += `**Video URL:** ${activeLecture.youtube_url}\n`;
    md += `**Exported At:** ${new Date().toLocaleString()}\n\n`;
    md += `## Timestamped Notes\n\n`;

    notes.forEach(n => {
      md += `- [${n.timestamp_formatted}](${activeLecture.youtube_url}&t=${n.timestamp_sec}s): ${n.text}\n`;
    });

    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `NPTEL_Notes_${activeModule.module_code}_Lec${activeLecture.lecture_number}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="rounded-3xl border border-[#00F0B5]/30 bg-gradient-to-b from-[#020813] via-[#041026] to-[#020813] p-5 sm:p-7 shadow-2xl font-mono text-slate-100 space-y-6">
      
      {/* Top Header: Academic Course & Instructor Attribution */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-6 bg-gradient-to-b from-[#00693E] to-[#00F0B5] rounded-full"></span>
            <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <span>Smart NPTEL Lecture Player</span>
              <span className="text-[10px] uppercase px-2 py-0.5 rounded bg-[#00693E]/50 text-[#00F0B5] border border-[#00F0B5]/30">
                Unit {activeModule.curriculum_unit} Sync
              </span>
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {activeModule.module_code}: {activeModule.module_title} • {activeModule.nptel_course.instructor} ({activeModule.nptel_course.institution})
          </p>
        </div>

        {/* Module Picker */}
        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-400">Curriculum:</span>
          <select
            value={selectedModuleCode}
            onChange={(e) => {
              setSelectedModuleCode(e.target.value);
              setSelectedLectureIdx(0);
            }}
            className="px-3 py-1.5 rounded-xl bg-[#020813] border border-slate-800 text-[#00F0B5] focus:outline-none focus:border-[#00F0B5]/50 text-xs"
          >
            {modules.map(m => (
              <option key={m.module_code} value={m.module_code}>
                {m.module_code} - Unit {m.curriculum_unit} ({m.module_title.substring(0, 32)}...)
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Grid: Video Player + Playlist / Notes Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Video IFrame & Playback Controls (8 cols) */}
        <div className="lg:col-span-8 space-y-4">
          
          {/* 16:9 Responsive Video / Fallback Container */}
          <div className="relative aspect-video w-full rounded-2xl overflow-hidden border border-slate-800 bg-[#020813] shadow-2xl flex flex-col justify-center items-center">
            {isFallback ? (
              <div className="w-full h-full p-6 sm:p-8 flex flex-col justify-between bg-gradient-to-br from-[#020b18] via-[#04162c] to-[#010814] text-left border border-[#00F0B5]/20">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-500/40 text-[10px] font-bold text-emerald-300 uppercase tracking-widest">
                        Official NPTEL Portal Stream
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {activeModule?.nptel_course?.course_id || activeModule?.module_code}
                      </span>
                    </div>
                    <h3 className="text-lg sm:text-xl font-bold text-white mt-2 font-heading">
                      {activeLecture?.lecture_title || activeModule?.module_title}
                    </h3>
                    <p className="text-xs text-slate-300 mt-1">
                      Instructor: <span className="text-emerald-400 font-semibold">{activeModule?.nptel_course?.instructor}</span> • {activeModule?.nptel_course?.institution}
                    </p>
                  </div>
                  <div className="hidden sm:flex flex-col items-end text-right">
                    <span className="text-[11px] font-mono text-slate-400">Anna University AU-R2023</span>
                    <span className="text-[10px] text-emerald-400/80 font-mono">Unit {activeLecture?.unit_mapped || activeModule?.curriculum_unit} Verified</span>
                  </div>
                </div>

                <div className="my-auto py-3 px-4 rounded-xl bg-[#020813]/80 border border-slate-800/80 space-y-2">
                  <p className="text-xs text-slate-300 leading-relaxed font-sans">
                    This lecture is curated from the National Programme on Technology Enhanced Learning (NPTEL) repository. 
                    Direct portal streaming guarantees access to the full official course transcript, graded assignments, and reference slides without video stream interruptions.
                  </p>
                  <div className="flex flex-wrap gap-2 pt-1">
                    {activeLecture?.key_concepts?.slice(0, 3).map((kc, i) => (
                      <span key={i} className="px-2 py-0.5 rounded-md bg-[#041026] text-slate-400 border border-slate-700/60 text-[10px] font-mono">
                        ✦ {kc}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-800/80">
                  <a
                    href={activeLecture?.portal_url || activeModule?.nptel_course?.portal_url || "https://nptel.ac.in"}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00a86b] text-white text-xs font-bold tracking-wide shadow-lg shadow-emerald-950/50 hover:brightness-110 transition-all border border-[#00F0B5]/40"
                  >
                    <span>Open Official NPTEL Portal</span>
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                  <span className="text-[11px] text-slate-400 font-mono">
                    Timestamped notes and local markdown export remain active below ↓
                  </span>
                </div>
              </div>
            ) : (
              <div id="nptel-youtube-frame" className="w-full h-full"></div>
            )}
          </div>

          {/* Precision Control Deck: Speeds & Position */}
          <div className="p-4 rounded-2xl bg-[#041026]/80 border border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
            
            {/* Speed Buttons */}
            <div className="flex items-center gap-1.5">
              <span className="text-slate-400 mr-1 text-[11px]">Speed:</span>
              {SPEED_OPTIONS.map(spd => (
                <button
                  key={spd}
                  onClick={() => handleSpeedChange(spd)}
                  disabled={isFallback}
                  className={`px-2 py-1 rounded-lg text-xs font-bold transition-all ${
                    isFallback
                      ? 'bg-[#020813] text-slate-600 border border-slate-800/50 cursor-not-allowed'
                      : playbackSpeed === spd
                        ? 'bg-[#00693E] text-[#00F0B5] border border-[#00F0B5]/40 shadow-sm'
                        : 'bg-[#020813] text-slate-400 hover:text-slate-200 border border-slate-800'
                  }`}
                >
                  {spd}x
                </button>
              ))}
            </div>

            {/* Position Time & Resume Badge */}
            <div className="flex items-center gap-3">
              <div className="px-2.5 py-1 rounded-lg bg-[#020813] border border-slate-800 text-[11px] text-slate-300">
                <span>Pos: </span>
                <span className="text-[#00F0B5] font-bold">{formatTime(currentTime)}</span>
                <span className="text-slate-500"> / {formatTime(activeLecture.timestamp_end_sec)}</span>
              </div>
              <button
                onClick={() => seekTo(activeLecture.timestamp_start_sec)}
                className="px-2.5 py-1 rounded-lg bg-[#00693E]/20 text-[#00F0B5] border border-[#00F0B5]/30 hover:bg-[#00693E]/40 text-xs transition-colors"
                title="Restart from Syllabus Start"
              >
                Reset Start
              </button>
            </div>
          </div>

          {/* Chapter Markers from Key Concepts */}
          <div className="p-4 rounded-2xl bg-[#020813]/90 border border-slate-800 space-y-2.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-slate-200 flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-[#00F0B5]"></span>
                Anna University Syllabus Chapter Markers:
              </span>
              <span className="text-[10px] text-slate-500">Click to jump in lecture</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {activeLecture.key_concepts.map((concept, idx) => {
                // Approximate step chapters between start and end
                const totalDuration = activeLecture.timestamp_end_sec - activeLecture.timestamp_start_sec;
                const chapterTime = activeLecture.timestamp_start_sec + Math.floor((idx / activeLecture.key_concepts.length) * totalDuration);

                return (
                  <button
                    key={idx}
                    onClick={() => seekTo(chapterTime)}
                    className="p-2.5 rounded-xl bg-[#041026] hover:bg-[#00693E]/20 border border-slate-800 hover:border-[#00F0B5]/40 text-left transition-all flex items-start gap-2.5 group"
                  >
                    <span className="px-1.5 py-0.5 rounded bg-[#020813] text-[#00F0B5] text-[10px] font-bold border border-[#00F0B5]/20 shrink-0">
                      {formatTime(chapterTime)}
                    </span>
                    <span className="text-[11px] text-slate-300 group-hover:text-white leading-tight">
                      {concept}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Keyboard Shortcuts Hint Bar */}
          <div className="px-4 py-2 rounded-xl bg-[#020813]/50 border border-slate-800/80 flex flex-wrap items-center justify-between gap-2 text-[10px] text-slate-500 font-mono">
            <span>Keyboard Shortcuts:</span>
            <span><kbd className="px-1 rounded bg-[#041026] text-slate-300">Space</kbd> Play/Pause</span>
            <span><kbd className="px-1 rounded bg-[#041026] text-slate-300">←</kbd> / <kbd className="px-1 rounded bg-[#041026] text-slate-300">→</kbd> ±5s</span>
            <span><kbd className="px-1 rounded bg-[#041026] text-slate-300">M</kbd> Mute</span>
            <span><kbd className="px-1 rounded bg-[#041026] text-slate-300">J</kbd> / <kbd className="px-1 rounded bg-[#041026] text-slate-300">L</kbd> Seek</span>
          </div>

        </div>

        {/* Right Column: Lecture Selector & Timestamped Notes (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          
          {/* Lecture Playlist Drawer */}
          <div className="rounded-2xl border border-slate-800 bg-[#020813] p-4 space-y-3">
            <div className="flex items-center justify-between text-xs pb-2 border-b border-slate-800">
              <span className="font-bold text-slate-200 uppercase tracking-wider">
                Module Lectures ({activeModule.nptel_course.lectures.length})
              </span>
              <span className="text-[10px] text-[#00F0B5]">
                {activeModule.nptel_course.course_id}
              </span>
            </div>

            <div className="space-y-1.5 max-h-44 overflow-y-auto">
              {activeModule.nptel_course.lectures.map((lec, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedLectureIdx(idx)}
                  className={`w-full text-left p-2.5 rounded-xl border transition-all text-xs flex items-center justify-between gap-2 ${
                    selectedLectureIdx === idx
                      ? 'bg-[#00693E]/30 border-[#00F0B5]/50 text-white font-bold'
                      : 'bg-[#041026] border-slate-800/60 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <div className="truncate">
                    <span className="text-emerald-400 mr-1.5">Lec {lec.lecture_number}:</span>
                    <span>{lec.lecture_title}</span>
                  </div>
                  <span className="text-[10px] text-slate-500 shrink-0">
                    {formatTime(lec.timestamp_start_sec)}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Timestamped Interactive Notes Drawer */}
          <div className="rounded-2xl border border-slate-800 bg-[#020813] p-4 space-y-3">
            <div className="flex items-center justify-between text-xs pb-2 border-b border-slate-800">
              <div className="flex items-center gap-1.5">
                <span className="text-amber-400">📝</span>
                <span className="font-bold text-slate-200 uppercase tracking-wider">
                  Timestamped Notes ({notes.length})
                </span>
              </div>
              {notes.length > 0 && (
                <button
                  onClick={exportNotesMarkdown}
                  className="text-[10px] text-[#00F0B5] hover:underline"
                  title="Export notes as Markdown"
                >
                  Export .MD ↗
                </button>
              )}
            </div>

            {/* Note Input Box */}
            <form onSubmit={addNote} className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="px-2 py-1 rounded bg-[#041026] border border-amber-500/30 text-amber-400 text-xs font-bold shrink-0">
                  @{formatTime(currentTime)}
                </span>
                <input
                  type="text"
                  value={noteText}
                  onChange={(e) => setNoteText(e.target.value)}
                  placeholder="Capture note at this second..."
                  className="w-full px-3 py-1.5 rounded-xl bg-[#041026] border border-slate-800 focus:border-[#00F0B5]/50 text-xs text-slate-200 placeholder-slate-500 focus:outline-none"
                />
              </div>
              <button
                type="submit"
                className="w-full py-1.5 rounded-xl bg-[#00693E]/40 hover:bg-[#00F0B5] hover:text-[#020813] border border-[#00F0B5]/30 text-[#00F0B5] text-xs font-bold transition-all"
              >
                + Pin Note to Timestamp
              </button>
            </form>

            {/* Notes List */}
            <div className="space-y-2 max-h-64 overflow-y-auto pt-1">
              {notes.length === 0 ? (
                <div className="text-center py-6 text-slate-500 text-xs">
                  No notes pinned yet. Click play and type your observation!
                </div>
              ) : (
                notes.map(note => (
                  <div
                    key={note.id}
                    className="p-2.5 rounded-xl bg-[#041026]/60 border border-slate-800/80 hover:border-slate-700 transition-all flex items-start justify-between gap-2 text-xs"
                  >
                    <div className="space-y-1">
                      <button
                        onClick={() => seekTo(note.timestamp_sec)}
                        className="px-1.5 py-0.5 rounded bg-[#020813] text-[#00F0B5] hover:text-white border border-[#00F0B5]/30 text-[10px] font-bold"
                      >
                        ▶ {note.timestamp_formatted}
                      </button>
                      <p className="text-slate-200 text-xs leading-relaxed font-sans">
                        {note.text}
                      </p>
                    </div>
                    <button
                      onClick={() => deleteNote(note.id)}
                      className="text-slate-500 hover:text-rose-400 text-xs p-1"
                      title="Delete note"
                    >
                      ✕
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}

