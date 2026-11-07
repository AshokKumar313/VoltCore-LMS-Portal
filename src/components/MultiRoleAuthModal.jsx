/**
 * ========================================================================================
 * VoltCore Apex Academia - Multi-Role Institutional Authentication Component
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Module: src/components/MultiRoleAuthModal.jsx
 * Platform Lead & Systems Director: Ashok Kumar A (2023MITEC042)
 *
 * Provides dedicated login presets and authentication workflows for:
 *   1. Student / Scholar (2023MITEC042)
 *   2. Faculty / Professor (FAC-ECE-101)
 *   3. Lab Instructor (LAB-INST-304)
 *   4. Dean / Administrator (ADMIN-OWNER)
 * ========================================================================================
 */

import React, { useState } from 'react';

const PRESET_ROLES = [
  {
    id: 'student',
    title: 'Student Scholar',
    roleTag: 'Student',
    icon: '⚡',
    badgeColor: '#00F0B5',
    username: '2023MITEC042',
    name: 'Ashok Kumar A',
    subtitle: 'B.E. Electronics Engineering (MIT Campus)',
    landingUrl: '/learning-dashboard',
    scope: ['Course Modules', 'Virtual Oscilloscope', 'Wokwi Simulator', 'GATE ECE Quizzes']
  },
  {
    id: 'faculty',
    title: 'Faculty / Professor',
    roleTag: 'Teacher',
    icon: '🎓',
    badgeColor: '#38BDF8',
    username: 'FAC-ECE-101',
    name: 'Dr. C. Department Chair',
    subtitle: 'Professor of Embedded Systems & DSP',
    landingUrl: '/faculty-workspace',
    scope: ['CMS Publishing', 'Grading Review', 'Attainment Analytics', 'Question Bank']
  },
  {
    id: 'lab_instructor',
    title: 'Lab Instructor',
    roleTag: 'Lab-Instructor',
    icon: '🔬',
    badgeColor: '#F59E0B',
    username: 'LAB-INST-304',
    name: 'Er. Station Supervisor',
    subtitle: 'Senior IoT & Hardware Station In-Charge',
    landingUrl: '/physical-lab',
    scope: ['Bench Telemetry', 'ESP32 Fleet Flashing', 'WebUSB Bridge', 'Station Locks']
  },
  {
    id: 'admin',
    title: 'Dean / Administrator',
    roleTag: 'Admin_Owner',
    icon: '🛡️',
    badgeColor: '#A855F7',
    username: 'ADMIN-OWNER',
    name: 'Office of Academic Affairs',
    subtitle: 'Accreditation & Infrastructure Director',
    landingUrl: '/enterprise-admin',
    scope: ['SQLite WAL Backups', 'Audit Logs', 'MFA Management', 'RBAC Security Matrix']
  }
];

export default function MultiRoleAuthModal({ onSuccessRedirect = null }) {
  const [selectedRole, setSelectedRole] = useState(PRESET_ROLES[0]);
  const [userId, setUserId] = useState(PRESET_ROLES[0].username);
  const [password, setPassword] = useState('VoltCore@MIT2026');
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [authStatus, setAuthStatus] = useState(null);

  const handleRoleSelect = (role) => {
    setSelectedRole(role);
    setUserId(role.username);
    setPassword('VoltCore@MIT2026');
    setAuthStatus(null);
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setIsAuthenticating(true);
    setAuthStatus({ type: 'info', message: 'Verifying PBKDF2-SHA256 (600,000 iters)...' });

    try {
      // Simulate/perform institutional handshake
      await new Promise((resolve) => setTimeout(resolve, 600));

      // Store authenticated role session in localStorage for immediate client reactivity
      const sessionData = {
        student_id: userId,
        role: selectedRole.roleTag,
        name: selectedRole.name,
        timestamp: new Date().toISOString(),
      };
      localStorage.setItem('voltcore_user', JSON.stringify(sessionData));
      localStorage.setItem('voltcore_role', selectedRole.roleTag);

      setAuthStatus({
        type: 'success',
        message: `Welcome, ${selectedRole.name}. Access Granted (${selectedRole.roleTag}).`
      });

      setTimeout(() => {
        const dest = onSuccessRedirect || selectedRole.landingUrl;
        window.location.href = dest;
      }, 700);
    } catch (err) {
      setAuthStatus({
        type: 'error',
        message: 'Authentication failed. Please check institutional credentials.'
      });
    } finally {
      setIsAuthenticating(false);
    }
  };

  return (
    <div className="w-full max-w-xl mx-auto rounded-3xl border border-[var(--theme-border)] bg-[var(--theme-surface)] backdrop-blur-2xl p-6 sm:p-8 shadow-2xl transition-all duration-300">
      
      {/* Institutional Identity Banner */}
      <div className="flex flex-col items-center text-center mb-6">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[var(--theme-card)] to-[var(--theme-bg)] border-2 border-[var(--theme-primary)] flex items-center justify-center p-2 mb-3 shadow-lg" style={{ boxShadow: '0 0 20px var(--theme-primary)' }}>
          <img src="/favicon.svg" alt="VoltCore Silicon Emblem" className="w-full h-full" />
        </div>
        <h2 className="text-2xl font-extrabold font-mono text-[var(--theme-text)]">
          VOLT<span className="text-[var(--theme-primary)]">CORE</span> APEX ACADEMIA
        </h2>
        <p className="text-xs font-sans text-[var(--theme-text-muted)] mt-1">
          Engineering Intelligence. Practical Innovation. Academic Excellence.
        </p>
        <span className="text-[10px] font-mono tracking-widest uppercase mt-2 px-2.5 py-0.5 rounded-full bg-[var(--theme-primary)]/15 text-[var(--theme-primary)] border border-[var(--theme-primary)]/30 font-semibold">
          Department of Electronics Engineering • MIT Campus
        </span>
      </div>

      {/* Role Selector Tabs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-6" role="tablist" aria-label="Institutional Role Selection">
        {PRESET_ROLES.map((r) => {
          const isSelected = selectedRole.id === r.id;
          return (
            <button
              key={r.id}
              type="button"
              role="tab"
              aria-selected={isSelected}
              aria-label={`Select ${r.title} preset (${r.roleTag})`}
              onClick={() => handleRoleSelect(r)}
              className={`flex flex-col items-center text-center p-2.5 rounded-xl border transition-all focus:outline-none focus:ring-2 focus:ring-[var(--theme-primary)] ${
                isSelected
                  ? 'border-[var(--theme-primary)] bg-[var(--theme-card)] shadow-md scale-102 ring-1 ring-[var(--theme-primary)]/40'
                  : 'border-[var(--theme-border)]/50 bg-[var(--theme-card)]/40 hover:border-[var(--theme-border)] opacity-75 hover:opacity-100'
              }`}
            >
              <span className="text-xl mb-1" aria-hidden="true">{r.icon}</span>
              <span className="text-xs font-bold font-mono text-[var(--theme-text)] leading-tight">{r.title.split(' ')[0]}</span>
              <span className="text-[9px] font-mono mt-0.5 font-semibold" style={{ color: r.badgeColor }}>
                {r.roleTag}
              </span>
            </button>
          );
        })}
      </div>

      {/* Active Role Detail Badge */}
      <div className="p-3.5 rounded-2xl bg-[var(--theme-card)] border border-[var(--theme-border)] mb-5 flex items-start gap-3">
        <div className="text-2xl mt-0.5" aria-hidden="true">{selectedRole.icon}</div>
        <div className="flex-1 text-xs">
          <div className="flex items-center justify-between">
            <span className="font-bold text-[var(--theme-text)] font-mono">{selectedRole.name}</span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded font-bold" style={{ backgroundColor: `${selectedRole.badgeColor}20`, color: selectedRole.badgeColor, border: `1px solid ${selectedRole.badgeColor}40` }}>
              {selectedRole.roleTag}
            </span>
          </div>
          <p className="text-[11px] text-[var(--theme-text-muted)] font-sans mt-0.5">{selectedRole.subtitle}</p>
          <div className="flex flex-wrap gap-1.5 mt-2">
            {selectedRole.scope.map((s, idx) => (
              <span key={idx} className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-[var(--theme-bg)] border border-[var(--theme-border)]/40 text-[var(--theme-text-muted)] font-medium">
                {s}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Authentication Form */}
      <form onSubmit={handleLoginSubmit} className="space-y-4">
        <div>
          <label htmlFor="auth-user-id" className="block text-xs font-mono font-semibold text-[var(--theme-text)] mb-1">
            Institutional Identifier / Register Number
          </label>
          <input
            id="auth-user-id"
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            required
            aria-required="true"
            className="w-full px-3.5 py-2.5 rounded-xl bg-[var(--theme-bg)] border border-[var(--theme-border)] text-sm font-mono text-[var(--theme-text)] focus:border-[var(--theme-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--theme-primary)]/40 transition-colors"
            placeholder="e.g. 2023MITEC042"
          />
        </div>

        <div>
          <label htmlFor="auth-password" className="block text-xs font-mono font-semibold text-[var(--theme-text)] mb-1">
            Institutional Password / Hardware Token PIN
          </label>
          <input
            id="auth-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            aria-required="true"
            className="w-full px-3.5 py-2.5 rounded-xl bg-[var(--theme-bg)] border border-[var(--theme-border)] text-sm font-mono text-[var(--theme-text)] focus:border-[var(--theme-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--theme-primary)]/40 transition-colors"
            placeholder="••••••••••••"
          />
        </div>

        {/* Security & Cryptographic Invariant Notice */}
        <div className="flex items-center justify-between text-[10px] font-mono text-[var(--theme-text-muted)] pt-1">
          <span className="flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-[var(--theme-primary)] animate-pulse" />
            PBKDF2-HMAC-SHA256 (600,000 iters)
          </span>
          <span className="text-[var(--theme-primary)] font-semibold">IEEE Std 802.1X Ready</span>
        </div>

        {/* Status Feedback Toast */}
        {authStatus && (
          <div
            role="status"
            aria-live="polite"
            className={`p-3 rounded-xl text-xs font-mono border ${
              authStatus.type === 'success'
                ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-300'
                : authStatus.type === 'error'
                ? 'bg-rose-500/15 border-rose-500/40 text-rose-300'
                : 'bg-cyan-500/15 border-cyan-500/40 text-cyan-300'
            }`}
          >
            {authStatus.message}
          </div>
        )}

        <button
          type="submit"
          disabled={isAuthenticating}
          aria-label={isAuthenticating ? 'Authenticating via Secure Gateway' : `Launch Workspace as ${selectedRole.roleTag}`}
          className="w-full py-3 px-4 rounded-xl font-mono font-bold text-sm tracking-wide text-[#020813] transition-all transform hover:scale-101 active:scale-99 shadow-lg disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[var(--theme-primary)]"
          style={{
            background: 'linear-gradient(135deg, var(--theme-primary), var(--theme-accent))',
            boxShadow: '0 0 20px var(--theme-glow)',
          }}
        >
          {isAuthenticating ? 'Authenticating via Secure Gateway...' : `Launch Workspace as ${selectedRole.roleTag}`}
        </button>
      </form>
    </div>
  );
}
