import React, { useState } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - KaTeX Formula Renderer & Inspector Component
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead & Systems Architect: Ashok Kumar A
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 *
 * Provides responsive mathematical formula presentation with:
 *   - Cybernetic LaTeX mathematical formula container with theme glow
 *   - Raw LaTeX and Plain Text copy to clipboard with toast notification
 *   - Detailed parameter variable breakdown table
 *   - Anna University Regulation 2023 exam significance indicator
 * ========================================================================================
 */

export default function KatexFormulaCard({ formula, themeColor = "#00F0B5", themeFamily = "emerald" }) {
  const [copiedType, setCopiedType] = useState(null); // 'latex' | 'plain' | null
  const [isExpanded, setIsExpanded] = useState(false);

  const handleCopy = (text, type) => {
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(text);
      setCopiedType(type);
      setTimeout(() => setCopiedType(null), 2000);
    }
  };

  // Convert simple LaTeX to clean readable plain text
  const getPlainText = (latex) => {
    return latex
      .replace(/\\sum_\{([^}]+)\}\^\{([^}]+)\}/g, 'SUM($1 to $2)')
      .replace(/\\left\(/g, '(')
      .replace(/\\right\)/g, ')')
      .replace(/\\frac\{([^}]+)\}\{([^}]+)\}/g, '($1)/($2)')
      .replace(/\\sqrt\{([^}]+)\}/g, 'sqrt($1)')
      .replace(/\\mathbf\{([^}]+)\}/g, '$1')
      .replace(/\\approx/g, '≈')
      .replace(/\\le/g, '<=')
      .replace(/\\ge/g, '>=')
      .replace(/\\cdot/g, '*')
      .replace(/\\times/g, 'x')
      .replace(/\\Delta/g, 'Δ')
      .replace(/\\nu/g, 'ν')
      .replace(/\\pi/g, 'π')
      .replace(/\\mu/g, 'μ')
      .replace(/\\eta/g, 'η')
      .replace(/\\Omega/g, 'Ω')
      .replace(/\\omega/g, 'ω')
      .replace(/\\tau/g, 'τ')
      .replace(/\\varepsilon/g, 'ε')
      .replace(/\\lambda/g, 'λ')
      .replace(/\\partial/g, '∂')
      .replace(/\\ln/g, 'ln')
      .replace(/\\cos/g, 'cos')
      .replace(/\\sin/g, 'sin')
      .replace(/\\tan/g, 'tan')
      .replace(/\\text\{([^}]+)\}/g, '$1')
      .replace(/[{}\\]/g, '');
  };

  return (
    <div className="p-5 rounded-2xl bg-[#041026] border border-slate-800 hover:border-slate-700 transition-all shadow-xl space-y-4">
      {/* Header: Formula Name & Exam Significance */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2">
          <span className="text-base">📐</span>
          <h4 className="font-bold text-white text-sm font-sans">{formula.name}</h4>
        </div>
        <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
          formula.examSignificance.includes("16-Mark")
            ? "bg-rose-950/40 text-rose-300 border-rose-500/30"
            : formula.examSignificance.includes("8-Mark")
            ? "bg-amber-950/40 text-amber-300 border-amber-500/30"
            : "bg-emerald-950/40 text-emerald-300 border-emerald-500/30"
        }`}>
          {formula.examSignificance}
        </span>
      </div>

      {/* Cybernetic Mathematical Formula Display */}
      <div
        className="p-4 rounded-xl bg-[#020813] text-center border font-mono text-sm sm:text-base font-bold shadow-inner relative group overflow-x-auto"
        style={{ borderColor: `${themeColor}40` }}
      >
        <div className="py-2 px-3 text-white tracking-wide">
          {formula.latex}
        </div>
        <div className="text-[10px] text-slate-500 font-normal mt-1">
          {formula.description}
        </div>
      </div>

      {/* Interactive Copy & Inspector Strip */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-1 font-mono text-xs">
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleCopy(formula.latex, 'latex')}
            className={`px-3 py-1 rounded-lg border transition-all flex items-center gap-1.5 ${
              copiedType === 'latex'
                ? "bg-emerald-950 text-emerald-300 border-emerald-500/60 font-bold"
                : "bg-[#020813] text-slate-400 hover:text-white border-slate-800"
            }`}
            title="Copy LaTeX source string"
          >
            <span>{copiedType === 'latex' ? "✓ Copied LaTeX" : "📋 Copy LaTeX"}</span>
          </button>

          <button
            onClick={() => handleCopy(getPlainText(formula.latex), 'plain')}
            className={`px-3 py-1 rounded-lg border transition-all flex items-center gap-1.5 ${
              copiedType === 'plain'
                ? "bg-emerald-950 text-emerald-300 border-emerald-500/60 font-bold"
                : "bg-[#020813] text-slate-400 hover:text-white border-slate-800"
            }`}
            title="Copy simplified mathematical equation"
          >
            <span>{copiedType === 'plain' ? "✓ Copied Plain" : "📝 Copy Plain"}</span>
          </button>
        </div>

        {formula.variables && Object.keys(formula.variables).length > 0 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-[11px] text-slate-400 hover:text-white transition-colors flex items-center gap-1"
          >
            <span>{isExpanded ? "Hide Parameters ▲" : "Variable Parameters ▼"}</span>
          </button>
        )}
      </div>

      {/* Variable Parameters Legend */}
      {isExpanded && formula.variables && (
        <div className="p-3.5 rounded-xl bg-[#020813] border border-slate-800/80 space-y-2 font-mono text-xs">
          <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
            Parameter Variable Definitions:
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {Object.entries(formula.variables).map(([key, desc]) => (
              <div key={key} className="flex items-start gap-2 p-1.5 rounded-lg bg-[#041026] border border-slate-800">
                <code className="font-bold text-xs" style={{ color: themeColor }}>
                  {key}
                </code>
                <span className="text-slate-300 text-[11px] leading-tight">
                  {desc}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
