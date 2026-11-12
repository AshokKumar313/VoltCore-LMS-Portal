import React, { useState, useEffect } from 'react';
import { triggerToast } from './ToastNotifications.jsx';

/**
 * VoltCore Apex Academia - XP Progression & Gamified Streak HUD
 * Integrates directly with SQLite backend (attendance_server.py on Port 5000)
 * Student: Ashok Kumar A (2023MITEC042) | MIT Campus, Anna University
 */

export default function XPProgressionWidget({
  initialXp = 4850,
  initialStreak = 14,
  initialLevel = 18,
  studentId = '2023MITEC042',
  studentName = 'Ashok Kumar A',
  backendUrl = 'http://127.0.0.1:5000'
}) {
  const [xp, setXp] = useState(initialXp);
  const [streak, setStreak] = useState(initialStreak);
  const [multiplier, setMultiplier] = useState(2.5);
  const [isSyncing, setIsSyncing] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);
  const [recentSwipes, setRecentSwipes] = useState([]);

  const xpForNextLevel = 5000;
  const currentLevelTitle = 'Silicon Grandmaster (Lvl 18)';
  const nextLevelTitle = 'Embedded Firmware Architect (Lvl 19)';

  const progressPercent = Math.min(100, Math.round((xp / xpForNextLevel) * 100));

  // Sync state from SQLite Backend on Mount
  useEffect(() => {
    async function syncBackendData() {
      try {
        const res = await fetch(`${backendUrl}/api/attendance?student_id=${studentId}&limit=5`);
        if (res.ok) {
          const json = await res.json();
          if (json.data && Array.isArray(json.data)) {
            setRecentSwipes(json.data);
            // Award calculated XP based on swipes
            const extraXp = json.data.length * 50;
            setXp((prev) => Math.max(prev, initialXp + (extraXp > 150 ? 150 : 0)));
          }
        }
      } catch (e) {
        console.log('Backend sync offline, operating in deterministic local mode:', e);
      }
    }
    syncBackendData();
  }, [backendUrl, studentId, initialXp]);

  const showToast = (msg, xpGain = 0) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);

    triggerToast({
      type: 'xp',
      title: 'XP Multiplier Recorded!',
      message: msg,
      xp: xpGain || Math.round(50 * multiplier),
      multiplier: `${multiplier}x`,
      studentId: studentName,
      duration: 4000
    });
  };

  // Simulate Instant Hardware RFID Tap (POST to /api/attendance)
  const handleSimulateRfidTap = async () => {
    setIsSyncing(true);
    const earnedXp = Math.round(50 * multiplier);

    try {
      const response = await fetch(`${backendUrl}/api/attendance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId,
          rfid_uid: 'E2 80 6F 3B',
          node_id: 'ESP32_MIT_IOT_LAB_01',
          rssi: -54
        })
      });

      if (response.ok) {
        setXp((prev) => prev + earnedXp);
        showToast(`⚡ RFID Swiped! +${earnedXp} XP (2.5x Boost) recorded on SQLite!`);
      } else {
        throw new Error('API offline');
      }
    } catch (e) {
      // Local optimistic update
      setXp((prev) => prev + earnedXp);
      showToast(`⚡ Simulation Tap Logged! +${earnedXp} XP added to profile!`);
    } finally {
      setIsSyncing(false);
    }
  };

  // Claim Daily Lab Streak Bonus
  const handleClaimStreak = () => {
    setStreak((prev) => prev + 1);
    setXp((prev) => prev + 100);
    showToast('🔥 Streak Claimed! 15-Day Lab Streak milestone achieved (+100 XP)!');
  };

  return (
    <div className="glass-card rounded-2xl p-6 border border-[#00F0B5]/30 shadow-2xl font-mono text-xs text-slate-100 relative overflow-hidden">
      
      {/* Toast Alert Banner */}
      {toastMessage && (
        <div className="absolute top-3 right-3 left-3 sm:left-auto px-4 py-2.5 rounded-xl bg-gradient-to-r from-[#00693E] to-[#041026] border border-[#00F0B5] text-[#00F0B5] text-xs font-bold shadow-2xl flex items-center justify-between gap-3 z-30 animate-pulse">
          <span>{toastMessage}</span>
          <button onClick={() => setToastMessage(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Header Info */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-white text-sm">{studentName}</span>
            <span className="px-2 py-0.5 rounded bg-[#00693E]/40 text-[#00F0B5] border border-[#00F0B5]/30 text-[10px]">
              {studentId}
            </span>
          </div>
          <div className="text-[11px] text-[#00F0B5] font-semibold mt-0.5">
            {currentLevelTitle} • MIT Campus, Anna University
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Streak Badge */}
          <div className="px-3 py-1.5 rounded-xl bg-[#020813] border border-amber-500/30 text-amber-400 font-bold flex items-center gap-1.5 shadow-sm">
            <span>🔥</span>
            <span>{streak} Days</span>
          </div>

          {/* XP Multiplier HUD */}
          <div className="px-3 py-1.5 rounded-xl bg-gradient-to-r from-[#00693E]/40 to-[#020813] border border-[#00F0B5]/30 text-[#00F0B5] font-bold flex items-center gap-1.5">
            <span>⚡</span>
            <span>{multiplier}x Multiplier</span>
          </div>
        </div>
      </div>

      {/* XP Level Progress Bar */}
      <div className="py-4 space-y-2">
        <div className="flex justify-between items-center text-xs">
          <span className="text-slate-400">Total Experience Points:</span>
          <span className="text-white font-bold">
            {xp} <span className="text-slate-500 font-normal">/ {xpForNextLevel} XP ({progressPercent}%)</span>
          </span>
        </div>

        {/* Progress Bar with Emerald Glow */}
        <div className="w-full h-3 bg-[#020813] rounded-full overflow-hidden p-0.5 border border-slate-800">
          <div
            className="h-full bg-gradient-to-r from-[#00693E] via-[#00b884] to-[#00F0B5] rounded-full transition-all duration-500 shadow-emerald-glow"
            style={{ width: `${progressPercent}%` }}
          ></div>
        </div>

        <div className="flex justify-between text-[10px] text-slate-400 pt-0.5">
          <span>Current: {currentLevelTitle}</span>
          <span className="text-emerald-400">Next: {nextLevelTitle} ({xpForNextLevel - xp} XP remaining)</span>
        </div>
      </div>

      {/* Unlocked Curriculum Modules Matrix */}
      <div className="py-3 border-t border-slate-800 space-y-2">
        <div className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
          Anna University Curriculum Modules Progress
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
          <div className="p-2.5 rounded-xl bg-[#020813] border border-emerald-500/30 flex items-center justify-between">
            <div>
              <div className="font-semibold text-white">Embedded Systems: FreeRTOS &amp; Dual-Core ESP32</div>
              <div className="text-[10px] text-slate-400">Sem 7 • 4 Credits</div>
            </div>
            <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold text-[10px]">
              ✓ Completed
            </span>
          </div>

          <div className="p-2.5 rounded-xl bg-[#020813] border border-cyan-500/30 flex items-center justify-between">
            <div>
              <div className="font-semibold text-white">EC8703: Defense UAV & 2.4GHz FHSS</div>
              <div className="text-[10px] text-slate-400">Sem 7 • 4 Credits</div>
            </div>
            <span className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 font-bold text-[10px]">
              Active (85%)
            </span>
          </div>

          <div className="p-2.5 rounded-xl bg-[#020813] border border-amber-500/30 flex items-center justify-between">
            <div>
              <div className="font-semibold text-white">EC8705: RV32I 5-Stage RISC-V FPGA</div>
              <div className="text-[10px] text-slate-400">Sem 7 • 4 Credits</div>
            </div>
            <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-bold text-[10px]">
              Active (70%)
            </span>
          </div>

          <div className="p-2.5 rounded-xl bg-[#020813] border border-emerald-500/30 flex items-center justify-between">
            <div>
              <div className="font-semibold text-white">EC8711: Embedded Systems HIL Lab</div>
              <div className="text-[10px] text-slate-400">Sem 7 • 2 Credits</div>
            </div>
            <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold text-[10px]">
              ✓ Verified
            </span>
          </div>
        </div>
      </div>

      {/* Gamified Actions Toolbar */}
      <div className="pt-4 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="text-[11px] text-slate-400">
          Hardware Token: <span className="text-[#00F0B5] font-bold">E2 80 6F 3B</span> (MFRC522)
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleClaimStreak}
            className="px-3 py-1.5 rounded-xl bg-[#020813] hover:bg-slate-800 border border-amber-500/40 text-amber-400 text-xs font-semibold transition-all"
          >
            Claim Daily Streak
          </button>

          <button
            type="button"
            onClick={handleSimulateRfidTap}
            disabled={isSyncing}
            className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00b884] hover:from-[#008f65] hover:to-[#00F0B5] text-white text-xs font-bold transition-all shadow-emerald-glow flex items-center gap-1.5 disabled:opacity-50"
          >
            <span>⚡ Tap ESP32 Node (+125 XP)</span>
          </button>
        </div>
      </div>

    </div>
  );
}

