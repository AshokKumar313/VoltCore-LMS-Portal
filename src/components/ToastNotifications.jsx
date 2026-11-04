import React, { useState, useEffect, useCallback, useRef } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Enterprise Glassmorphic Toast Notifications
 * Tailored for Anna University / MIT Campus Standards (Department of Electronics Eng.)
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A (ashokkumar2008313@gmail.com | +91 9597382878)
 * GitHub Profile: https://github.com/AshokKumar313 (Username: AshokKumar313)
 * Aesthetic: Italian Glassmorphism (Deep Royal Navy #020813 to Emerald #00693E)
 * Features:
 *   - Instant visual feedback for XP Gains, ESP32 Attendance Scans, Login, and Rate Limits
 *   - Auto-dismiss countdown timer with real-time visual progress bar
 *   - Pause timer on hover, manual dismissal (✕)
 *   - Global window event listener ('voltcore:toast') & direct triggerToast() export
 * ========================================================================================
 */

// Global trigger function exported for external React components & vanilla scripts
export const triggerToast = (options) => {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(
      new CustomEvent('voltcore:toast', {
        detail: {
          id: options.id || `toast-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
          type: options.type || 'info', // 'xp' | 'attendance' | 'login' | 'security' | 'success' | 'error' | 'info'
          title: options.title || 'VoltCore Notification',
          message: options.message || '',
          xp: options.xp || null,
          multiplier: options.multiplier || null,
          nodeId: options.nodeId || null,
          studentId: options.studentId || null,
          duration: options.duration !== undefined ? options.duration : 3800,
          timestamp: new Date().toLocaleTimeString(),
        }
      })
    );
  }
};

export default function ToastNotifications({ position = 'bottom-right' }) {
  const [toasts, setToasts] = useState([]);
  const [isDemoOpen, setIsDemoOpen] = useState(false);
  const timersRef = useRef({});

  // Add toast to stack
  const addToast = useCallback((toastData) => {
    const toastId = toastData.id || `toast-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`;
    const duration = toastData.duration !== undefined ? toastData.duration : 3800;

    const newToast = {
      ...toastData,
      id: toastId,
      duration,
      remaining: duration,
      createdAt: Date.now(),
      isPaused: false,
    };

    setToasts((prev) => {
      // Keep maximum 5 concurrent toasts
      const updated = [newToast, ...prev.filter((t) => t.id !== toastId)];
      return updated.slice(0, 5);
    });

    if (duration > 0) {
      timersRef.current[toastId] = setTimeout(() => {
        removeToast(toastId);
      }, duration);
    }
  }, []);

  // Remove toast from stack
  const removeToast = useCallback((id) => {
    if (timersRef.current[id]) {
      clearTimeout(timersRef.current[id]);
      delete timersRef.current[id];
    }
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  // Pause timer on hover
  const handleMouseEnter = (id) => {
    if (timersRef.current[id]) {
      clearTimeout(timersRef.current[id]);
      delete timersRef.current[id];
    }
    setToasts((prev) =>
      prev.map((t) => (t.id === id ? { ...t, isPaused: true } : t))
    );
  };

  // Resume timer on mouse leave
  const handleMouseLeave = (id) => {
    setToasts((prev) => {
      const toast = prev.find((t) => t.id === id);
      if (toast && toast.duration > 0) {
        timersRef.current[id] = setTimeout(() => {
          removeToast(id);
        }, 1500); // Give user a grace period of 1.5s after un-hovering
      }
      return prev.map((t) => (t.id === id ? { ...t, isPaused: false } : t));
    });
  };

  // Setup Global Event Listeners & Window API
  useEffect(() => {
    const handleCustomToast = (event) => {
      if (event.detail) {
        addToast(event.detail);
      }
    };

    window.addEventListener('voltcore:toast', handleCustomToast);
    window.VoltCoreToast = {
      emit: triggerToast,
      clear: () => setToasts([]),
    };

    return () => {
      window.removeEventListener('voltcore:toast', handleCustomToast);
      Object.values(timersRef.current).forEach(clearTimeout);
    };
  }, [addToast]);

  // Visual Theme mapping based on toast type
  const getTypeConfig = (type) => {
    switch (type) {
      case 'xp':
        return {
          icon: '⚡',
          badgeText: 'XP REWARD',
          borderColor: 'border-[#FFB703]/40',
          glowColor: 'shadow-[0_0_25px_rgba(255,183,3,0.22)]',
          badgeBg: 'bg-[#FFB703]/20 text-[#FFB703] border-[#FFB703]/40',
          progressBarColor: 'bg-gradient-to-r from-[#FFB703] to-[#00F0B5]',
          accentGlow: 'from-[#FFB703]/10 to-transparent',
        };
      case 'attendance':
        return {
          icon: '📡',
          badgeText: 'ESP32 TELEMETRY',
          borderColor: 'border-[#00F0B5]/40',
          glowColor: 'shadow-[0_0_30px_rgba(0,240,181,0.22)]',
          badgeBg: 'bg-[#00693E]/35 text-[#00F0B5] border-[#00F0B5]/35',
          progressBarColor: 'bg-gradient-to-r from-[#00693E] to-[#00F0B5]',
          accentGlow: 'from-[#00F0B5]/15 to-transparent',
        };
      case 'login':
        return {
          icon: '🛡️',
          badgeText: 'IAM AUTHENTICATED',
          borderColor: 'border-[#00D8F6]/40',
          glowColor: 'shadow-[0_0_25px_rgba(0,216,246,0.22)]',
          badgeBg: 'bg-[#00D8F6]/15 text-[#00D8F6] border-[#00D8F6]/30',
          progressBarColor: 'bg-gradient-to-r from-[#00D8F6] to-[#00693E]',
          accentGlow: 'from-[#00D8F6]/10 to-transparent',
        };
      case 'security':
        return {
          icon: '⚠️',
          badgeText: 'SECURITY GATEWAY',
          borderColor: 'border-rose-500/40',
          glowColor: 'shadow-[0_0_30px_rgba(244,63,94,0.25)]',
          badgeBg: 'bg-rose-500/20 text-rose-300 border-rose-500/35',
          progressBarColor: 'bg-gradient-to-r from-rose-500 to-amber-500',
          accentGlow: 'from-rose-500/15 to-transparent',
        };
      case 'error':
        return {
          icon: '✕',
          badgeText: 'ERROR',
          borderColor: 'border-rose-500/40',
          glowColor: 'shadow-[0_0_25px_rgba(244,63,94,0.22)]',
          badgeBg: 'bg-rose-500/20 text-rose-300 border-rose-500/35',
          progressBarColor: 'bg-rose-500',
          accentGlow: 'from-rose-500/15 to-transparent',
        };
      case 'success':
      default:
        return {
          icon: '✓',
          badgeText: 'VERIFIED',
          borderColor: 'border-[#00F0B5]/40',
          glowColor: 'shadow-[0_0_25px_rgba(0,240,181,0.2)]',
          badgeBg: 'bg-[#00693E]/30 text-[#00F0B5] border-[#00F0B5]/30',
          progressBarColor: 'bg-[#00F0B5]',
          accentGlow: 'from-[#00F0B5]/10 to-transparent',
        };
    }
  };

  // Preset demo triggers
  const triggerDemo = (demoType) => {
    switch (demoType) {
      case 'xp':
        triggerToast({
          type: 'xp',
          title: 'Silicon Mastery XP Boosted!',
          message: 'Completed EC8702 FreeRTOS Semaphore Mutex Challenge.',
          xp: 125,
          multiplier: '2.5x',
          duration: 4000,
        });
        break;
      case 'attendance':
        triggerToast({
          type: 'attendance',
          title: 'ESP32 RFID Lab Entry Confirmed',
          message: 'Student Ashok Kumar A (2023MITEC042) logged at MIT IoT Lab 01.',
          nodeId: 'ESP32_MIT_NODE_01',
          duration: 4500,
        });
        break;
      case 'login':
        triggerToast({
          type: 'login',
          title: 'Session Authenticated (PBKDF2 600K)',
          message: 'Access granted as Platform Architect (MIT Campus ECE R2023).',
          studentId: 'Ashok Kumar A',
          duration: 3800,
        });
        break;
      case 'security':
        triggerToast({
          type: 'security',
          title: 'Rate Limit Warning (HTTP 429)',
          message: 'Burst limit threshold reached (120 req/min). Cooldown engaged.',
          duration: 4200,
        });
        break;
      default:
        break;
    }
  };

  return (
    <>
      {/* Interactive Quick-Test HUD Button for Evaluators */}
      <div className="fixed bottom-4 left-4 z-40 hidden sm:flex items-center gap-2">
        <button
          onClick={() => setIsDemoOpen(!isDemoOpen)}
          className="text-[11px] font-mono px-3 py-1.5 rounded-lg bg-[#041026]/85 border border-[#00F0B5]/30 text-[#00F0B5] hover:bg-[#00693E]/40 hover:border-[#00F0B5] transition-all flex items-center gap-1.5 shadow-glass backdrop-blur-md"
          title="Toggle Phase 1 Security & Event Toast HUD"
        >
          <span className="w-2 h-2 rounded-full bg-[#00F0B5] animate-pulse"></span>
          <span>Security HUD {isDemoOpen ? '▲' : '▼'}</span>
        </button>

        {isDemoOpen && (
          <div className="flex items-center gap-1.5 bg-[#020813]/90 border border-[#00F0B5]/25 p-1 rounded-lg backdrop-blur-xl animate-in fade-in slide-in-from-left duration-200 shadow-glass">
            <button
              onClick={() => triggerDemo('xp')}
              className="text-[10px] font-mono px-2 py-1 rounded bg-[#FFB703]/20 text-[#FFB703] border border-[#FFB703]/30 hover:bg-[#FFB703]/30 transition-all"
            >
              +XP Gain
            </button>
            <button
              onClick={() => triggerDemo('attendance')}
              className="text-[10px] font-mono px-2 py-1 rounded bg-[#00693E]/40 text-[#00F0B5] border border-[#00F0B5]/40 hover:bg-[#00F0B5]/20 transition-all"
            >
              ESP32 Scan
            </button>
            <button
              onClick={() => triggerDemo('login')}
              className="text-[10px] font-mono px-2 py-1 rounded bg-[#00D8F6]/20 text-[#00D8F6] border border-[#00D8F6]/30 hover:bg-[#00D8F6]/30 transition-all"
            >
              Login Auth
            </button>
            <button
              onClick={() => triggerDemo('security')}
              className="text-[10px] font-mono px-2 py-1 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 hover:bg-rose-500/30 transition-all"
            >
              Rate Limit
            </button>
          </div>
        )}
      </div>

      {/* Primary Toast Notification Stack */}
      <aside
        aria-live="polite"
        aria-label="System notifications"
        className="fixed bottom-6 right-6 z-50 flex flex-col gap-3 w-full max-w-sm sm:max-w-md pointer-events-none px-4 sm:px-0"
      >
        {toasts.map((toast) => {
          const config = getTypeConfig(toast.type);

          return (
            <div
              key={toast.id}
              onMouseEnter={() => handleMouseEnter(toast.id)}
              onMouseLeave={() => handleMouseLeave(toast.id)}
              className={`pointer-events-auto relative overflow-hidden rounded-xl bg-[#041026]/92 backdrop-blur-2xl border ${config.borderColor} ${config.glowColor} transition-all duration-300 transform translate-y-0 opacity-100 flex flex-col shadow-glass`}
            >
              {/* Radial gradient background accent */}
              <div
                className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl ${config.accentGlow} blur-2xl pointer-events-none`}
              />

              {/* Main Content Area */}
              <div className="p-4 flex items-start gap-3.5 relative z-10">
                {/* Visual Icon Badge */}
                <div className="w-9 h-9 rounded-lg bg-[#020813] border border-white/10 flex items-center justify-center text-lg flex-shrink-0 shadow-inner">
                  {config.icon}
                </div>

                {/* Text & Metadata Container */}
                <div className="flex-1 min-w-0 pr-2">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span
                      className={`text-[9px] font-mono font-bold tracking-wider px-2 py-0.5 rounded border uppercase ${config.badgeBg}`}
                    >
                      {config.badgeText}
                    </span>
                    <span className="text-[10px] font-mono text-slate-500">
                      {toast.timestamp}
                    </span>
                  </div>

                  <h4 className="text-xs sm:text-sm font-semibold text-slate-100 tracking-tight leading-snug">
                    {toast.title}
                  </h4>

                  {toast.message && (
                    <p className="text-xs text-slate-300 mt-1 leading-relaxed line-clamp-2">
                      {toast.message}
                    </p>
                  )}

                  {/* Extra Metadata Pill Bars (XP or Node) */}
                  {(toast.xp || toast.multiplier || toast.nodeId) && (
                    <div className="flex flex-wrap items-center gap-2 mt-2 pt-2 border-t border-white/5">
                      {toast.xp && (
                        <span className="text-[10px] font-mono font-bold text-[#FFB703] bg-[#FFB703]/10 px-2 py-0.5 rounded border border-[#FFB703]/25">
                          +{toast.xp} XP
                        </span>
                      )}
                      {toast.multiplier && (
                        <span className="text-[10px] font-mono text-[#00F0B5] bg-[#00693E]/30 px-2 py-0.5 rounded border border-[#00F0B5]/30">
                          {toast.multiplier} Streak Multiplier
                        </span>
                      )}
                      {toast.nodeId && (
                        <span className="text-[10px] font-mono text-slate-400 bg-slate-800/60 px-2 py-0.5 rounded border border-slate-700/60">
                          Node: {toast.nodeId}
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Dismiss Button */}
                <button
                  onClick={() => removeToast(toast.id)}
                  className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-white/10 transition-colors flex-shrink-0"
                  aria-label="Close notification"
                >
                  <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>

              {/* Progress Countdown Bar */}
              {toast.duration > 0 && (
                <div className="w-full h-1 bg-white/5 overflow-hidden">
                  <div
                    className={`h-full ${config.progressBarColor} transition-all`}
                    style={{
                      animation: `voltcore-toast-shrink ${toast.duration}ms linear forwards`,
                      animationPlayState: toast.isPaused ? 'paused' : 'running',
                    }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </aside>

      <style>{`
        @keyframes voltcore-toast-shrink {
          from {
            width: 100%;
          }
          to {
            width: 0%;
          }
        }
      `}</style>
    </>
  );
}

