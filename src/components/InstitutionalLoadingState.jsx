/**
 * ========================================================================================
 * VoltCore Apex Academia - Institutional Loading & Synchronization State Component
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Module: src/components/InstitutionalLoadingState.jsx
 * Platform Lead & Systems Director: Ashok Kumar A (2023MITEC042)
 *
 * Renders the sovereign emerald/cyan silicon emblem with dynamic pulsing reticles,
 * circuit trace animations, and institutional motto across all 18 themes.
 * ========================================================================================
 */

import React from 'react';

export default function InstitutionalLoadingState({
  statusMessage = 'Initializing Hardware Simulation Subsystem...',
  subtext = 'Synchronizing SQLite WAL Journals & FPGA Fabric',
  fullScreen = false,
  progress = null,
}) {
  const containerClass = fullScreen
    ? 'fixed inset-0 z-50 flex flex-col items-center justify-center bg-[var(--theme-bg)]/90 backdrop-blur-2xl p-6'
    : 'w-full py-12 flex flex-col items-center justify-center p-6 rounded-3xl border border-[var(--theme-border)] bg-[var(--theme-surface)]/70 backdrop-blur-xl';

  return (
    <div className={containerClass} role="status" aria-live="polite">
      {/* Central Silicon Die with Rotating Reticle */}
      <div className="relative mb-6">
        <!-- Glowing Ambient Aura -->
        <div
          className="absolute inset-0 rounded-3xl blur-2xl opacity-40 animate-pulse pointer-events-none"
          style={{ backgroundColor: 'var(--theme-primary)' }}
        />

        <!-- Rotating Outer Circuit Track -->
        <div className="w-24 h-24 rounded-3xl border-2 border-dashed border-[var(--theme-primary)]/40 flex items-center justify-center animate-spin-slow">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[var(--theme-card)] to-[var(--theme-bg)] border border-[var(--theme-border)] flex items-center justify-center p-3 shadow-xl">
            <img
              src="/favicon.svg"
              alt="VoltCore Silicon Emblem"
              className="w-full h-full drop-shadow-md animate-pulse"
            />
          </div>
        </div>

        <!-- Corner Micro-Die Alignment Indicators -->
        <span className="absolute -top-1 -right-1 flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--theme-primary)] opacity-75" />
          <span className="relative inline-flex rounded-full h-3 w-3 bg-[var(--theme-primary)]" />
        </span>
      </div>

      <!-- Institutional Branding Title -->
      <div className="text-center space-y-1.5 max-w-md">
        <div className="flex items-center justify-center gap-2">
          <span className="font-mono font-extrabold text-lg text-[var(--theme-text)]">
            VOLT<span className="text-[var(--theme-primary)]">CORE</span>
          </span>
          <span className="text-[10px] font-mono font-bold tracking-wider uppercase px-1.5 py-0.5 rounded bg-[var(--theme-primary)]/15 text-[var(--theme-primary)] border border-[var(--theme-primary)]/30">
            APEX
          </span>
        </div>

        <p className="text-xs font-mono font-semibold text-[var(--theme-text)]">
          {statusMessage}
        </p>

        <p className="text-[11px] font-mono text-[var(--theme-text-muted)]">
          {subtext}
        </p>

        <!-- Progress Bar if Provided -->
        {progress !== null && (
          <div className="w-48 mx-auto mt-3 h-1.5 rounded-full bg-[var(--theme-bg)] border border-[var(--theme-border)] overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-300"
              style={{
                width: `${Math.min(Math.max(progress, 0), 100)}%`,
                backgroundColor: 'var(--theme-primary)',
                boxShadow: '0 0 10px var(--theme-primary)',
              }}
            />
          </div>
        )}

        <!-- Institutional Subtitle Motto -->
        <p className="text-[10px] font-sans text-[var(--theme-primary)] pt-3 tracking-wide">
          "Engineering Intelligence. Practical Innovation. Academic Excellence."
        </p>
      </div>
    </div>
  );
}
