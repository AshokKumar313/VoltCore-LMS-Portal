import React from 'react';

/**
 * ========================================================================================
 * VOLTCORE APEX ACADEMIA — INSTITUTIONAL LOADING & SYNCHRONIZATION STATE
 * ========================================================================================
 * Madras Institute of Technology (MIT) Campus • Anna University
 * Department of Electronics Engineering • Regulation 2023 (CBCS)
 * 
 * Capabilities:
 *   - Sovereign silicon die with dynamic pulsing reticle and oscilloscope trace animation
 *   - Crisp, lightweight inline SVG silicon-trace pulse lines (< 2 KB)
 *   - Clean academic typography (Manrope headings + Inter body)
 *   - Zero course codes in UI text
 *   - Full 18-theme CSS variable compatibility (--theme-primary, --theme-border, etc.)
 * ========================================================================================
 */

export default function InstitutionalLoadingState({
  statusMessage = 'Initializing Hardware Simulation Subsystem...',
  subtext = 'Synchronizing SQLite WAL Journals & FPGA Fabric',
  fullScreen = false,
  progress = null,
  size = 'md' // 'sm' | 'md' | 'lg'
}) {
  const containerClass = fullScreen
    ? 'fixed inset-0 z-50 flex flex-col items-center justify-center bg-[var(--theme-bg)]/90 backdrop-blur-2xl p-6 font-sans'
    : 'w-full py-10 flex flex-col items-center justify-center p-6 rounded-3xl border border-[var(--theme-border)] bg-[var(--theme-surface)]/70 backdrop-blur-xl font-sans';

  return (
    <div className={containerClass} role="status" aria-live="polite">
      {/* Central Silicon Die with Rotating Reticle */}
      <div className="relative mb-5">
        {/* Glowing Ambient Aura */}
        <div
          className="absolute inset-0 rounded-3xl blur-2xl opacity-35 animate-pulse pointer-events-none"
          style={{ backgroundColor: 'var(--theme-primary, #00F0B5)' }}
        />

        {/* Rotating Outer Circuit Track */}
        <div
          className="w-20 h-20 sm:w-24 sm:h-24 rounded-3xl border-2 border-dashed flex items-center justify-center transition-all animate-spin-slow"
          style={{ borderColor: 'var(--theme-primary, rgba(0,240,181,0.35))' }}
        >
          <div
            className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl border flex items-center justify-center p-2.5 shadow-xl"
            style={{
              background: 'linear-gradient(135deg, var(--theme-card, #041026) 0%, var(--theme-bg, #020813) 100%)',
              borderColor: 'var(--theme-border, rgba(0,240,181,0.25))'
            }}
          >
            <img
              src="/favicon.svg"
              alt="VoltCore Silicon Sovereign Emblem"
              className="w-full h-full drop-shadow-md animate-pulse"
            />
          </div>
        </div>

        {/* Corner Micro-Die Alignment Indicators */}
        <span className="absolute -top-1 -right-1 flex h-3 w-3">
          <span
            className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
            style={{ backgroundColor: 'var(--theme-primary, #00F0B5)' }}
          />
          <span
            className="relative inline-flex rounded-full h-3 w-3"
            style={{ backgroundColor: 'var(--theme-primary, #00F0B5)' }}
          />
        </span>
      </div>

      {/* Animated Oscilloscope Silicon-Trace SVG Wave */}
      <div className="w-48 sm:w-64 h-8 mb-3 overflow-hidden flex items-center justify-center">
        <svg viewBox="0 0 240 32" className="w-full h-full">
          <defs>
            <linearGradient id="traceGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="var(--theme-primary, #00F0B5)" stopOpacity="0.1" />
              <stop offset="50%" stopColor="var(--theme-primary, #00F0B5)" stopOpacity="0.9" />
              <stop offset="100%" stopColor="var(--theme-primary, #00F0B5)" stopOpacity="0.1" />
            </linearGradient>
          </defs>
          {/* Background Bus Grid */}
          <line x1="0" y1="16" x2="240" y2="16" stroke="var(--theme-border, rgba(0,240,181,0.15))" strokeDasharray="3 3" />
          {/* Dynamic Oscilloscope Pulse Waveform */}
          <path
            d="M 0 16 L 70 16 L 80 4 L 90 28 L 100 10 L 110 22 L 120 16 L 240 16"
            fill="none"
            stroke="url(#traceGrad)"
            strokeWidth="2"
            strokeLinecap="round"
          />
          {/* Signal Pulse Dot */}
          <circle cx="100" cy="10" r="3" fill="var(--theme-primary, #00F0B5)" className="animate-ping" opacity="0.8" />
        </svg>
      </div>

      {/* Institutional Academic Branding & Status Typography */}
      <div className="text-center space-y-1.5 max-w-md px-4">
        <div className="flex items-center justify-center gap-2">
          <span className="font-heading font-extrabold text-base sm:text-lg text-[var(--theme-text,#FFFFFF)] tracking-tight">
            VOLT<span style={{ color: 'var(--theme-primary, #00F0B5)' }}>CORE</span>
          </span>
          <span
            className="text-[10px] font-mono font-bold tracking-wider uppercase px-2 py-0.5 rounded border"
            style={{
              backgroundColor: 'rgba(0, 240, 181, 0.12)',
              color: 'var(--theme-primary, #00F0B5)',
              borderColor: 'var(--theme-border, rgba(0, 240, 181, 0.3))'
            }}
          >
            APEX ACADEMIA
          </span>
        </div>

        <p className="text-xs sm:text-sm font-heading font-semibold text-[var(--theme-text,#FFFFFF)] tracking-tight">
          {statusMessage}
        </p>

        <p className="text-[11px] font-mono text-[var(--theme-text-muted,#94A3B8)]">
          {subtext}
        </p>

        {/* Determinate Progress Indicator (if provided) */}
        {progress !== null && (
          <div
            className="w-56 mx-auto mt-3 h-1.5 rounded-full overflow-hidden border"
            style={{
              backgroundColor: 'var(--theme-bg, #020813)',
              borderColor: 'var(--theme-border, rgba(0, 240, 181, 0.2))'
            }}
          >
            <div
              className="h-full rounded-full transition-all duration-300"
              style={{
                width: `${Math.min(Math.max(progress, 0), 100)}%`,
                backgroundColor: 'var(--theme-primary, #00F0B5)',
                boxShadow: '0 0 10px var(--theme-primary, #00F0B5)',
              }}
            />
          </div>
        )}

        {/* Institutional Motto */}
        <p
          className="text-[10px] font-mono pt-3 tracking-wide"
          style={{ color: 'var(--theme-primary, #00F0B5)', opacity: 0.85 }}
        >
          Madras Institute of Technology • Department of Electronics Engineering
        </p>
      </div>
    </div>
  );
}
