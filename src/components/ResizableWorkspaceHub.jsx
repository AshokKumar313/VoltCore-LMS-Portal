import React, { useState, useEffect, useRef } from 'react';
import ThemeSelector from './ThemeSelector.jsx';
import CourseNavigationSidebar, { COURSE_CATALOG } from './CourseNavigationSidebar.jsx';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Flexible Resizable Multi-Frame Workspace Hub
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 * 
 * Features:
 *   - 4 Toggleable Workspace Frames: Video Lecture, Circuit Simulator, Code Editor, Notes
 *   - Dynamic layout modes (2x2 Grid, Horizontal Stack, Vertical Split, Code+Sim Focus)
 *   - One-Click Reset for Equal Grid Split
 *   - Frame show/hide toggles & individual Maximize / Restore controls
 *   - Reactive coupling with Granular Course Sidebar (3 tracks, 7 sections)
 * ========================================================================================
 */

export default function ResizableWorkspaceHub() {
  // Course Track & Section Selection State
  const [activeTrack, setActiveTrack] = useState(COURSE_CATALOG[0]);
  const [activeSection, setActiveSection] = useState(COURSE_CATALOG[0].sections[0]);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // 4 Toggleable Workspace Frames Visibility
  const [visibleFrames, setVisibleFrames] = useState({
    video: true,
    circuit: true,
    code: true,
    notes: true
  });

  // Layout mode: 'grid' (2x2), 'horizontal', 'vertical', 'code-sim', 'maximized'
  const [layoutMode, setLayoutMode] = useState('grid');
  const [maximizedFrame, setMaximizedFrame] = useState(null);

  // Split Ratio (percentage for 2-column or 2-row layouts)
  const [splitRatio, setSplitRatio] = useState(50); // 50% = equal split

  // Frame 1: Video State
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);
  const [videoProgress, setVideoProgress] = useState(32); // percentage

  // Frame 2: Circuit Simulator State
  const [simRunning, setSimRunning] = useState(true);
  const [inputA, setInputA] = useState(true);
  const [inputB, setInputB] = useState(false);
  const [clockTick, setClockTick] = useState(1);
  const [simMode, setSimMode] = useState('digital'); // 'digital' | 'analog'
  const [voltage, setVoltage] = useState(3.3);

  // Frame 3: Code Editor State
  const [codeContent, setCodeContent] = useState(activeSection.codeSnippet);
  const [compiling, setCompiling] = useState(false);
  const [consoleLogs, setConsoleLogs] = useState([
    "[SYSTEM] VoltCore GCC Compiler v12.2.0 (ARM Cortex-M4 / Xtensa ESP32)",
    "[READY] Ready to compile. Select section or edit firmware."
  ]);

  // Frame 4: Notes & Documentation State
  const [notesText, setNotesText] = useState(
    "### Lab Notes - " + activeTrack.title + "\n- Module: " + activeSection.title + "\n- Concept: " + activeSection.summary + "\n\n1. Key Derivations:\n2. Observation Checkpoints:\n"
  );
  const [notesTab, setNotesTab] = useState('notes'); // 'notes' | 'syllabus'

  // Update starter code & notes when active section changes
  useEffect(() => {
    setCodeContent(activeSection.codeSnippet);
    setNotesText(
      "### Lab Notes - " + activeTrack.title + "\n- Module: " + activeSection.title + "\n- Concept: " + activeSection.summary + "\n\n1. Key Derivations:\n2. Observation Checkpoints:\n"
    );
    setConsoleLogs(prev => [
      ...prev.slice(-4),
      `[NAVIGATE] Loaded section: ${activeSection.title} (${activeTrack.badge})`
    ]);
  }, [activeTrack, activeSection]);

  // Handle section selection from sidebar
  const handleSelectSection = (track, section) => {
    setActiveTrack(track);
    setActiveSection(section);
  };

  // Toggle visibility of individual frame
  const toggleFrame = (frameKey) => {
    setVisibleFrames(prev => {
      const updated = { ...prev, [frameKey]: !prev[frameKey] };
      // Prevent all frames from being hidden
      if (!Object.values(updated).some(Boolean)) {
        return prev;
      }
      return updated;
    });
  };

  // One-Click Equal Grid Split Reset
  const handleResetEqualGrid = () => {
    setVisibleFrames({
      video: true,
      circuit: true,
      code: true,
      notes: true
    });
    setLayoutMode('grid');
    setMaximizedFrame(null);
    setSplitRatio(50);
    setConsoleLogs(prev => [...prev.slice(-3), "[WORKSPACE] Layout reset to Equal 2x2 Grid (50/50 split)"]);
  };

  // Toggle maximize single frame
  const handleToggleMaximize = (frameKey) => {
    if (maximizedFrame === frameKey) {
      setMaximizedFrame(null);
      setLayoutMode('grid');
    } else {
      setMaximizedFrame(frameKey);
      setLayoutMode('maximized');
    }
  };

  // Simulate Code Compilation
  const handleCompileCode = () => {
    setCompiling(true);
    setConsoleLogs(prev => [
      ...prev,
      `[COMPILING] Building ${activeTrack.title} firmware target...`,
      `[AST] Verifying syntax tree and memory allocation...`
    ]);

    setTimeout(() => {
      setCompiling(false);
      setConsoleLogs(prev => [
        ...prev,
        `[SUCCESS] 0 errors, 0 warnings. Binary size: 148,924 bytes (Flash: 11.2%, SRAM: 8.4%).`,
        `[HIL] Ready for direct WebUSB flash or Wokwi emulation.`
      ]);
    }, 650);
  };

  // Calculate circuit output
  const outputY = inputA !== inputB; // XOR logic demo
  const clockFreq = 40.0; // MHz

  // Count active frames
  const activeCount = Object.values(visibleFrames).filter(Boolean).length;

  return (
    <div className="w-full flex flex-col gap-4 font-mono text-xs">
      
      {/* Top Workspace Control Bar */}
      <div 
        className="glass-card rounded-2xl p-4 border flex flex-wrap items-center justify-between gap-4 shadow-xl"
        style={{ borderColor: 'var(--theme-border)' }}
      >
        <div className="flex flex-wrap items-center gap-3">
          {/* Active Track & Section Badge */}
          <div className="flex items-center gap-2">
            <span className="text-base">{activeTrack.icon}</span>
            <div>
              <div className="font-bold text-white text-xs flex items-center gap-2">
                <span>{activeTrack.title}</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                  {activeSection.title}
                </span>
              </div>
              <div className="text-[10px] text-slate-400">
                {activeTrack.regulation} • Anna University MIT Campus
              </div>
            </div>
          </div>
        </div>

        {/* Frame Toggle Controls & Presets */}
        <div className="flex flex-wrap items-center gap-2">
          
          {/* 4 Frame Toggle Pills */}
          <div className="flex items-center gap-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
            <button
              type="button"
              onClick={() => toggleFrame('video')}
              className={`px-2.5 py-1 rounded-lg text-[11px] transition-all flex items-center gap-1.5 ${
                visibleFrames.video 
                  ? 'bg-blue-600/30 text-blue-300 border border-blue-500/40 font-bold' 
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <span>🎥</span>
              <span>Video</span>
            </button>

            <button
              type="button"
              onClick={() => toggleFrame('circuit')}
              className={`px-2.5 py-1 rounded-lg text-[11px] transition-all flex items-center gap-1.5 ${
                visibleFrames.circuit 
                  ? 'bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 font-bold' 
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <span>🔌</span>
              <span>Circuit</span>
            </button>

            <button
              type="button"
              onClick={() => toggleFrame('code')}
              className={`px-2.5 py-1 rounded-lg text-[11px] transition-all flex items-center gap-1.5 ${
                visibleFrames.code 
                  ? 'bg-purple-600/30 text-purple-300 border border-purple-500/40 font-bold' 
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <span>💻</span>
              <span>Editor</span>
            </button>

            <button
              type="button"
              onClick={() => toggleFrame('notes')}
              className={`px-2.5 py-1 rounded-lg text-[11px] transition-all flex items-center gap-1.5 ${
                visibleFrames.notes 
                  ? 'bg-amber-600/30 text-amber-300 border border-amber-500/40 font-bold' 
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <span>📝</span>
              <span>Notes</span>
            </button>
          </div>

          {/* One-Click Equal Grid Split Reset */}
          <button
            type="button"
            onClick={handleResetEqualGrid}
            className="px-3 py-1.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 font-bold transition-all flex items-center gap-1.5"
            title="Reset all 4 frames to equal 2x2 grid split"
          >
            <span>⊞</span>
            <span>Equal 2x2 Split</span>
          </button>

          {/* Split Slider for Dynamic Resizing */}
          <div className="hidden lg:flex items-center gap-2 px-2.5 py-1 rounded-xl bg-slate-900/80 border border-slate-800 text-[10px] text-slate-400">
            <span>Split:</span>
            <input
              type="range"
              min="25"
              max="75"
              value={splitRatio}
              onChange={(e) => setSplitRatio(Number(e.target.value))}
              className="w-16 accent-emerald-400 cursor-pointer"
              title={`Adjust frame split ratio: ${splitRatio}% / ${100 - splitRatio}%`}
            />
            <span className="w-8 text-white font-semibold">{splitRatio}%</span>
          </div>

          {/* 18 Vibrant Themes Selector Island */}
          <ThemeSelector />

        </div>
      </div>

      {/* Main Studio Body: Sidebar + Multi-Frame Workspace */}
      <div className="flex flex-col lg:flex-row gap-4 min-h-[720px]">
        
        {/* Granular Course Sidebar */}
        <CourseNavigationSidebar
          activeTrackId={activeTrack.id}
          activeSectionId={activeSection.id}
          onSelectSection={handleSelectSection}
          isCollapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        {/* Resizable 4-Frame Workspace Container */}
        <div className="flex-1 flex flex-col gap-4">
          
          {/* Active Frame Grid Layout */}
          <div 
            className={`w-full flex-1 grid gap-4 transition-all duration-300 ${
              maximizedFrame
                ? 'grid-cols-1 grid-rows-1'
                : activeCount === 1
                ? 'grid-cols-1 grid-rows-1'
                : activeCount === 2
                ? 'grid-cols-1 lg:grid-cols-2'
                : activeCount === 3
                ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
                : 'grid-cols-1 lg:grid-cols-2'
            }`}
          >

            {/* FRAME 1: Video Lecture */}
            {visibleFrames.video && (!maximizedFrame || maximizedFrame === 'video') && (
              <div 
                className="glass-card rounded-2xl border flex flex-col overflow-hidden shadow-lg transition-all"
                style={{ borderColor: 'var(--theme-border)' }}
              >
                {/* Frame Header */}
                <div className="p-3 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-blue-400 font-bold">🎥</span>
                    <span className="font-bold text-white text-xs">Video Lecture: {activeSection.title}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300">
                      {activeSection.duration}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <button
                      type="button"
                      onClick={() => handleToggleMaximize('video')}
                      className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px]"
                      title={maximizedFrame === 'video' ? "Restore Frame" : "Maximize Frame"}
                    >
                      {maximizedFrame === 'video' ? "❐" : "⛶"}
                    </button>
                    <button
                      type="button"
                      onClick={() => toggleFrame('video')}
                      className="p-1 rounded bg-slate-800 hover:bg-red-500/20 hover:text-red-400 text-slate-400 text-[10px]"
                      title="Hide Video Frame"
                    >
                      ✕
                    </button>
                  </div>
                </div>

                {/* Video Player Canvas / Embed */}
                <div className="relative flex-1 bg-black flex flex-col justify-center items-center p-4 min-h-[260px] overflow-hidden group">
                  {/* Atmospheric Glow */}
                  <div className="absolute inset-0 bg-gradient-to-tr from-blue-900/20 via-transparent to-emerald-900/20 pointer-events-none"></div>

                  <div className="text-center space-y-3 z-10">
                    <div className="w-16 h-16 rounded-full bg-blue-500/20 border border-blue-400/40 flex items-center justify-center mx-auto shadow-xl group-hover:scale-105 transition-transform cursor-pointer"
                      onClick={() => setIsVideoPlaying(!isVideoPlaying)}
                    >
                      <span className="text-2xl text-blue-300 ml-1">
                        {isVideoPlaying ? "⏸" : "▶"}
                      </span>
                    </div>
                    <div>
                      <div className="text-white font-bold text-sm">{activeSection.title}</div>
                      <div className="text-slate-400 text-[11px] mt-0.5">{activeTrack.title} • Module Overview</div>
                    </div>
                  </div>

                  {/* Video Progress Bar */}
                  <div className="absolute bottom-0 inset-x-0 bg-slate-900/90 backdrop-blur-md p-2.5 border-t border-slate-800 flex items-center justify-between gap-3 text-[10px]">
                    <div className="flex items-center gap-2 text-slate-300">
                      <button 
                        type="button"
                        onClick={() => setIsVideoPlaying(!isVideoPlaying)}
                        className="text-blue-400 font-bold"
                      >
                        {isVideoPlaying ? "PAUSE" : "PLAY"}
                      </button>
                      <span>14:20 / {activeSection.duration}</span>
                    </div>

                    <div className="flex-1 max-w-xs mx-2 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-blue-500 rounded-full"
                        style={{ width: `${videoProgress}%` }}
                      ></div>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-slate-400">Speed:</span>
                      {[1.0, 1.25, 1.5, 2.0].map(s => (
                        <button
                          key={s}
                          type="button"
                          onClick={() => setPlaybackSpeed(s)}
                          className={`px-1 rounded ${playbackSpeed === s ? 'bg-blue-600 text-white font-bold' : 'text-slate-400 hover:text-white'}`}
                        >
                          {s}x
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* FRAME 2: Interactive Circuit Simulator */}
            {visibleFrames.circuit && (!maximizedFrame || maximizedFrame === 'circuit') && (
              <div 
                className="glass-card rounded-2xl border flex flex-col overflow-hidden shadow-lg transition-all"
                style={{ borderColor: 'var(--theme-border)' }}
              >
                {/* Frame Header */}
                <div className="p-3 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-emerald-400 font-bold">🔌</span>
                    <span className="font-bold text-white text-xs">Circuit Simulator: {activeSection.circuitSim}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                      LIVE HIL
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <button
                      type="button"
                      onClick={() => handleToggleMaximize('circuit')}
                      className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px]"
                      title={maximizedFrame === 'circuit' ? "Restore Frame" : "Maximize Frame"}
                    >
                      {maximizedFrame === 'circuit' ? "❐" : "⛶"}
                    </button>
                    <button
                      type="button"
                      onClick={() => toggleFrame('circuit')}
                      className="p-1 rounded bg-slate-800 hover:bg-red-500/20 hover:text-red-400 text-slate-400 text-[10px]"
                      title="Hide Circuit Frame"
                    >
                      ✕
                    </button>
                  </div>
                </div>

                {/* Circuit Simulator Canvas */}
                <div className="flex-1 bg-slate-950/90 p-4 flex flex-col justify-between gap-4 min-h-[260px]">
                  
                  {/* Top Readout HUD */}
                  <div className="flex flex-wrap items-center justify-between gap-2 p-2 rounded-xl bg-slate-900/90 border border-slate-800 text-[11px]">
                    <div className="flex items-center gap-3">
                      <div>
                        <span className="text-slate-400">VCC:</span>
                        <span className="text-emerald-400 font-bold ml-1">{voltage.toFixed(2)} V</span>
                      </div>
                      <div>
                        <span className="text-slate-400">Freq:</span>
                        <span className="text-cyan-400 font-bold ml-1">{clockFreq} MHz</span>
                      </div>
                      <div>
                        <span className="text-slate-400">I_draw:</span>
                        <span className="text-amber-400 font-bold ml-1">24.5 mA</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-1.5">
                      <button
                        type="button"
                        onClick={() => setSimMode(simMode === 'digital' ? 'analog' : 'digital')}
                        className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-[10px]"
                      >
                        Mode: {simMode.toUpperCase()}
                      </button>
                      <button
                        type="button"
                        onClick={() => setSimRunning(!simRunning)}
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          simRunning ? 'bg-emerald-500/20 text-emerald-300' : 'bg-red-500/20 text-red-300'
                        }`}
                      >
                        {simRunning ? "RUNNING" : "STOPPED"}
                      </button>
                    </div>
                  </div>

                  {/* Interactive Breadboard / Logic Gate Model */}
                  <div className="flex-1 rounded-xl bg-slate-900/50 border border-slate-800 p-4 flex flex-col justify-center items-center gap-4">
                    <div className="flex items-center gap-6">
                      
                      {/* Logic Inputs */}
                      <div className="space-y-3">
                        <button
                          type="button"
                          onClick={() => setInputA(!inputA)}
                          className={`w-20 px-3 py-1.5 rounded-lg border flex items-center justify-between font-bold ${
                            inputA 
                              ? 'bg-emerald-500/20 border-emerald-400 text-emerald-300 shadow-sm' 
                              : 'bg-slate-800/80 border-slate-700 text-slate-400'
                          }`}
                        >
                          <span>IN_A</span>
                          <span>{inputA ? "1 (3.3V)" : "0 (0V)"}</span>
                        </button>

                        <button
                          type="button"
                          onClick={() => setInputB(!inputB)}
                          className={`w-20 px-3 py-1.5 rounded-lg border flex items-center justify-between font-bold ${
                            inputB 
                              ? 'bg-emerald-500/20 border-emerald-400 text-emerald-300 shadow-sm' 
                              : 'bg-slate-800/80 border-slate-700 text-slate-400'
                          }`}
                        >
                          <span>IN_B</span>
                          <span>{inputB ? "1 (3.3V)" : "0 (0V)"}</span>
                        </button>
                      </div>

                      {/* Logic Function Node */}
                      <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 border border-emerald-500/40 flex flex-col items-center justify-center p-2 shadow-lg">
                        <span className="text-slate-400 text-[10px]">LOGIC</span>
                        <span className="text-white font-extrabold text-sm">XOR</span>
                        <span className="text-[9px] text-emerald-400">74LVC1G86</span>
                      </div>

                      {/* Logic Outputs & LEDs */}
                      <div className="space-y-3">
                        <div className={`w-24 px-3 py-1.5 rounded-lg border flex items-center justify-between font-bold ${
                          outputY 
                            ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300 shadow-md' 
                            : 'bg-slate-800/80 border-slate-700 text-slate-400'
                        }`}>
                          <div className="flex items-center gap-1.5">
                            <span className={`w-2.5 h-2.5 rounded-full ${outputY ? 'bg-cyan-400 animate-ping' : 'bg-slate-700'}`}></span>
                            <span>OUT_Y</span>
                          </div>
                          <span>{outputY ? "HIGH" : "LOW"}</span>
                        </div>

                        <div className="w-24 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 flex items-center justify-between text-slate-400 text-[10px]">
                          <span>CLK</span>
                          <span className="text-emerald-400 font-bold">{clockTick}</span>
                        </div>
                      </div>

                    </div>
                  </div>

                  {/* Bottom Trigger Controls */}
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <button
                      type="button"
                      onClick={() => setClockTick(c => c + 1)}
                      className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-bold transition-all"
                    >
                      ⚡ Pulse Clock Edge
                    </button>
                    <span className="text-[10px]">Model: 74LVC / ESP32 GPIO Matrix</span>
                  </div>

                </div>
              </div>
            )}

            {/* FRAME 3: Interactive Code Editor */}
            {visibleFrames.code && (!maximizedFrame || maximizedFrame === 'code') && (
              <div 
                className="glass-card rounded-2xl border flex flex-col overflow-hidden shadow-lg transition-all"
                style={{ borderColor: 'var(--theme-border)' }}
              >
                {/* Frame Header */}
                <div className="p-3 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-purple-400 font-bold">💻</span>
                    <span className="font-bold text-white text-xs">Firmware Editor</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300">
                      C++ / FreeRTOS
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <button
                      type="button"
                      onClick={() => handleToggleMaximize('code')}
                      className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px]"
                      title={maximizedFrame === 'code' ? "Restore Frame" : "Maximize Frame"}
                    >
                      {maximizedFrame === 'code' ? "❐" : "⛶"}
                    </button>
                    <button
                      type="button"
                      onClick={() => toggleFrame('code')}
                      className="p-1 rounded bg-slate-800 hover:bg-red-500/20 hover:text-red-400 text-slate-400 text-[10px]"
                      title="Hide Code Frame"
                    >
                      ✕
                    </button>
                  </div>
                </div>

                {/* Editor Body */}
                <div className="flex-1 bg-slate-950 p-2 flex flex-col min-h-[260px]">
                  
                  {/* Top Editor Toolbar */}
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800/80 mb-2 px-1 text-[11px]">
                    <div className="flex items-center gap-2">
                      <span className="text-slate-400">Target:</span>
                      <span className="text-white font-semibold">ESP32-WROOM-32</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={handleCompileCode}
                        disabled={compiling}
                        className="px-3 py-1 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold transition-all shadow-sm flex items-center gap-1.5"
                      >
                        <span>{compiling ? "⏳" : "⚡"}</span>
                        <span>{compiling ? "Compiling..." : "Compile & Run"}</span>
                      </button>
                    </div>
                  </div>

                  {/* Textarea Code Buffer */}
                  <textarea
                    value={codeContent}
                    onChange={(e) => setCodeContent(e.target.value)}
                    className="flex-1 w-full bg-slate-900/60 text-slate-200 p-3 rounded-xl border border-slate-800 font-mono text-xs focus:outline-none focus:border-purple-400 resize-none min-h-[140px]"
                    spellCheck="false"
                  />

                  {/* Serial Monitor & Compilation Console */}
                  <div className="mt-2 p-2 rounded-xl bg-black/80 border border-slate-800/80 font-mono text-[10px] text-slate-300 max-h-24 overflow-y-auto space-y-0.5">
                    {consoleLogs.map((log, idx) => (
                      <div key={idx} className={log.includes('[SUCCESS]') ? 'text-emerald-400 font-bold' : log.includes('[COMPILING]') ? 'text-cyan-400' : 'text-slate-400'}>
                        {log}
                      </div>
                    ))}
                  </div>

                </div>
              </div>
            )}

            {/* FRAME 4: Notes / Documentation */}
            {visibleFrames.notes && (!maximizedFrame || maximizedFrame === 'notes') && (
              <div 
                className="glass-card rounded-2xl border flex flex-col overflow-hidden shadow-lg transition-all"
                style={{ borderColor: 'var(--theme-border)' }}
              >
                {/* Frame Header */}
                <div className="p-3 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-amber-400 font-bold">📝</span>
                    <span className="font-bold text-white text-xs">Notes & Syllabus Reference</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <button
                      type="button"
                      onClick={() => handleToggleMaximize('notes')}
                      className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px]"
                      title={maximizedFrame === 'notes' ? "Restore Frame" : "Maximize Frame"}
                    >
                      {maximizedFrame === 'notes' ? "❐" : "⛶"}
                    </button>
                    <button
                      type="button"
                      onClick={() => toggleFrame('notes')}
                      className="p-1 rounded bg-slate-800 hover:bg-red-500/20 hover:text-red-400 text-slate-400 text-[10px]"
                      title="Hide Notes Frame"
                    >
                      ✕
                    </button>
                  </div>
                </div>

                {/* Tabs & Content */}
                <div className="flex-1 bg-slate-950 p-3 flex flex-col min-h-[260px]">
                  
                  {/* Tab Selector */}
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-2 text-[11px]">
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => setNotesTab('notes')}
                        className={`px-2.5 py-1 rounded-lg transition-all ${
                          notesTab === 'notes'
                            ? 'bg-amber-500/20 text-amber-300 font-bold border border-amber-500/30'
                            : 'text-slate-400 hover:text-white'
                        }`}
                      >
                        Personal Notes (.md)
                      </button>
                      <button
                        type="button"
                        onClick={() => setNotesTab('syllabus')}
                        className={`px-2.5 py-1 rounded-lg transition-all ${
                          notesTab === 'syllabus'
                            ? 'bg-amber-500/20 text-amber-300 font-bold border border-amber-500/30'
                            : 'text-slate-400 hover:text-white'
                        }`}
                      >
                        Anna University Rubrics
                      </button>
                    </div>

                    <span className="text-[10px] text-slate-500">
                      Auto-saved • LocalStorage
                    </span>
                  </div>

                  {notesTab === 'notes' ? (
                    <div className="flex-1 flex flex-col gap-2">
                      <textarea
                        value={notesText}
                        onChange={(e) => setNotesText(e.target.value)}
                        className="flex-1 w-full bg-slate-900/60 text-slate-200 p-3 rounded-xl border border-slate-800 font-mono text-xs focus:outline-none focus:border-amber-400 resize-none min-h-[160px]"
                        placeholder="Write your markdown lab observations and derivations..."
                      />
                      <div className="flex items-center justify-between text-[10px] text-slate-400">
                        <span>Characters: {notesText.length}</span>
                        <button
                          type="button"
                          onClick={() => {
                            const blob = new Blob([notesText], { type: 'text/markdown' });
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `VoltCore_Notes_${activeSection.id}.md`;
                            a.click();
                          }}
                          className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-amber-300 font-bold transition-all"
                        >
                          Export .md
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex-1 overflow-y-auto space-y-3 p-2 bg-slate-900/40 rounded-xl border border-slate-800 text-slate-300 text-xs">
                      <div className="p-2 rounded-lg bg-slate-900/80 border border-slate-800">
                        <div className="font-bold text-white text-xs mb-1">
                          Syllabus Reference: {activeTrack.regulation}
                        </div>
                        <p className="text-[11px] text-slate-300 leading-relaxed">
                          {activeSection.summary}
                        </p>
                      </div>

                      <div className="space-y-1.5 text-[11px]">
                        <div className="font-bold text-amber-400">Key Competencies Tested:</div>
                        <ul className="list-disc pl-4 space-y-1 text-slate-300">
                          <li>Derivation of hardware timing equations and critical path constraints.</li>
                          <li>Register configuration and peripheral memory-mapped IO operations.</li>
                          <li>Real-time multi-threaded task synchronization under FreeRTOS / CMSIS.</li>
                        </ul>
                      </div>
                    </div>
                  )}

                </div>
              </div>
            )}

          </div>

        </div>

      </div>

    </div>
  );
}
