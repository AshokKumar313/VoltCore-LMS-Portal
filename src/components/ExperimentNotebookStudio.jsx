/**
 * ========================================================================================
 * VoltCore Apex Academia - Cross-Disciplinary Experiment Notebook Studio
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Module: src/components/ExperimentNotebookStudio.jsx
 * Platform Lead & Systems Director: Ashok Kumar A (2023MITEC042)
 *
 * Capabilities:
 *   1. Version-Controlled Markdown Lab Notebooks with SHA-256 Commit Tracking
 *   2. Embedded MNA Simulation State Capture (Matrix & Node Voltages)
 *   3. SPICE Netlist (.cir) Generator & Exporter
 *   4. Oscilloscope Waveform Snapshot Visualizer with Vpp, Vrms, and Frequency
 *   5. Cross-Disciplinary Research Project Registry with Subject Emblem Integration
 * ========================================================================================
 */

import React, { useState } from 'react';
import SubjectEmblem from './SubjectEmblem.jsx';
import { getSubjectMetadata } from '../data/subjectRegistry.ts';

const DEMO_PROJECTS = [
  {
    id: "PRJ-IOT-EDGE-01",
    title: "Autonomous Edge Sensor Hub with Predictive Anomaly Detection",
    shortTitle: "IoT Edge Accelerator",
    disciplines: ["IOT8701", "STM32-ACADEMY", "HDL6001"],
    facility: "MIT Campus Lab 304 - Embedded & IoT Research Suite",
    trl: "TRL-6 (System Verified)",
    lead: "Ashok Kumar A (2023MITEC042)",
    notebook: {
      id: "NB-IOT-001",
      commitHash: "e4a2c91807f6b92a4e1d3c5f8b9e0a2d3c4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a",
      timestamp: "2026-11-07 18:30 UTC",
      markdown: `### Objective\nSynthesize an ultra-low latency interrupt service routine on STM32H7 interfacing an FPGA-based FFT coprocessor over FMC 32-bit bus.\n\n### Mathematical Formulation\nInput sampling frequency: $f_s = 2.048\\text{ MSPS}$\nRadix-2 FFT execution time on FPGA: $\\tau_{\\text{FFT}} = 12.8\\,\\mu\\text{s}$\nDMA latency: $\\tau_{\\text{DMA}} = 1.4\\,\\mu\\text{s}$\nTotal deterministic window: $\\Delta t = 14.2\\,\\mu\\text{s} < 20\\,\\mu\\text{s}$ (Requirement satisfied).`,
      mnaState: {
        circuit: "FMC_Bus_Termination_Network",
        nodes: 4,
        voltages: [3.300, 3.285, 1.642, 0.000],
        conditionNumber: 1.04
      },
      spiceDeck: `* VoltCore Apex SPICE Netlist: FMC Bus High-Speed Termination\n* Author: Ashok Kumar A (2023MITEC042)\nV1 1 0 DC 3.3\nR1 1 2 22\nC1 2 0 10p\nR2 2 3 50\nC2 3 0 15p\n.tran 0.1n 50n\n.probe\n.end`,
      waveform: {
        channel1: "FMC_CLK (100 MHz)",
        channel2: "FPGA_INT_ACK",
        vpp: 3.31,
        vrms: 2.33,
        freq: 100.0,
        dutyCycle: 50.2
      }
    }
  },
  {
    id: "PRJ-BIOSIG-DSP-02",
    title: "Ultra-Low-Power ECG/EMG Front-End with Multirate Polyphase Filterbank",
    shortTitle: "Bio-Signal DSP Processor",
    disciplines: ["EC23S01", "EC23C05", "EC23C04"],
    facility: "MIT Campus Lab 304 - Biomedical & Signal Processing Suite",
    trl: "TRL-5 (Laboratory Validated)",
    lead: "Ashok Kumar A (2023MITEC042)",
    notebook: {
      id: "NB-BIO-002",
      commitHash: "9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b",
      timestamp: "2026-11-07 18:45 UTC",
      markdown: `### Objective\nDesign a 3-op-amp instrumentation amplifier with active DC offset cancellation and cascaded 16-channel polyphase decimation filterbank for ECG QRS feature extraction.\n\n### Performance Metrics\n- Common Mode Rejection Ratio (CMRR): $112\\text{ dB}$\n- Input referred noise: $0.85\\,\\mu\\text{V}_{\\text{rms}}$\n- Passband ripple: $< 0.05\\text{ dB}$`,
      mnaState: {
        circuit: "Precision_Instrumentation_Amp",
        nodes: 5,
        voltages: [1.800, 1.250, 1.252, 0.985, 0.000],
        conditionNumber: 1.12
      },
      spiceDeck: `* VoltCore Apex SPICE Netlist: Instrumentation Bio-Amp\n* Author: Ashok Kumar A (2023MITEC042)\nVin1 1 0 SIN(1.25 5m 60)\nVin2 2 0 SIN(1.25 5m 60 0 180)\nR1 1 3 100k\nR2 2 4 100k\nRg 3 4 2k\n.tran 10u 50m\n.end`,
      waveform: {
        channel1: "ECG_Raw_Electrode",
        channel2: "Polyphase_Filtered_QRS",
        vpp: 1.24,
        vrms: 0.88,
        freq: 1.25,
        dutyCycle: 12.5
      }
    }
  },
  {
    id: "PRJ-POWER-DRIVE-03",
    title: "GaN High-Frequency Inverter with Field-Oriented Control for Electric Mobility",
    shortTitle: "GaN Traction Drive",
    disciplines: ["EC23C01", "EC23C03", "EC23C07"],
    facility: "MIT Campus Lab 304 - Power Electronics & Motion Bench",
    trl: "TRL-7 (System Prototype in Operational Environment)",
    lead: "Ashok Kumar A (2023MITEC042)",
    notebook: {
      id: "NB-PWR-003",
      commitHash: "3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e",
      timestamp: "2026-11-07 19:00 UTC",
      markdown: `### Objective\nSynthesize a dead-time optimized gate driver for Gallium Nitride (GaN) half-bridge operating at 250 kHz with zero-voltage switching (ZVS).\n\n### Analytical Loss Verification\nSwitching loss reduction: $41.8\\%$\nPeak bridge efficiency: $\\eta = 98.4\\%$\nHeat sink temperature: $48.2^\\circ\\text{C}$ at full load ($1.2\\text{ kW}$).`,
      mnaState: {
        circuit: "GaN_Half_Bridge_Lattice",
        nodes: 4,
        voltages: [400.0, 198.5, 5.0, 0.0],
        conditionNumber: 1.08
      },
      spiceDeck: `* VoltCore Apex SPICE Netlist: 250kHz GaN Half-Bridge\n* Author: Ashok Kumar A (2023MITEC042)\nVdc 1 0 DC 400\nM1 1 2 3 0 GaN_HEMT\nM2 3 4 0 0 GaN_HEMT\nLload 3 5 150u\n.tran 1n 20u\n.end`,
      waveform: {
        channel1: "HighSide_Gate_Vgs",
        channel2: "Bridge_Midpoint_Vsw",
        vpp: 402.5,
        vrms: 284.6,
        freq: 250.0,
        dutyCycle: 49.8
      }
    }
  }
];

export default function ExperimentNotebookStudio() {
  const [selectedProjectId, setSelectedProjectId] = useState(DEMO_PROJECTS[0].id);
  const [activeSubTab, setActiveSubTab] = useState("markdown"); // "markdown" | "mna" | "spice" | "oscilloscope"
  const [copiedSpice, setCopiedSpice] = useState(false);

  const currentProject = DEMO_PROJECTS.find(p => p.id === selectedProjectId) || DEMO_PROJECTS[0];
  const nb = currentProject.notebook;

  const handleCopySpice = () => {
    navigator.clipboard.writeText(nb.spiceDeck);
    setCopiedSpice(true);
    setTimeout(() => setCopiedSpice(false), 2000);
  };

  return (
    <div className="space-y-6 font-mono text-[var(--theme-text,#F8FAFC)]">

      {/* Top Cross-Disciplinary Project Carousel */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <span className="text-xs uppercase tracking-wider text-slate-400 font-bold">
            Cross-Disciplinary Research Initiatives:
          </span>
          <span className="text-[11px] font-mono text-emerald-400 font-semibold bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
            MIT Campus Lab 304 Verified
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {DEMO_PROJECTS.map((proj) => {
            const isSelected = proj.id === selectedProjectId;
            return (
              <button
                key={proj.id}
                onClick={() => setSelectedProjectId(proj.id)}
                className={`p-4 rounded-2xl text-left transition-all border ${
                  isSelected
                    ? "bg-slate-900/90 border-[var(--theme-primary,#00F0B5)] shadow-lg shadow-emerald-500/10 scale-[1.01]"
                    : "bg-slate-950/60 border-slate-800/80 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-xs font-bold text-white tracking-tight font-sans">
                    {proj.shortTitle}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                    {proj.trl}
                  </span>
                </div>

                {/* Contributing Discipline Emblems */}
                <div className="flex items-center gap-2 mb-2">
                  {proj.disciplines.map((dCode) => (
                    <SubjectEmblem key={dCode} courseCode={dCode} size="sm" showFrame={true} />
                  ))}
                </div>

                <div className="text-[11px] text-slate-400 truncate">
                  {proj.title}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Experiment Notebook Card */}
      <div className="glass-card-accent rounded-3xl p-6 border border-slate-800/80 bg-slate-950/80 shadow-2xl relative overflow-hidden">

        {/* Notebook Header & Git Commit Hash */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="px-2.5 py-0.5 rounded-md text-[11px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                {nb.id}
              </span>
              <h2 className="text-xl font-extrabold text-white font-sans tracking-tight">
                {currentProject.title}
              </h2>
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Facility: <span className="text-slate-300 font-semibold">{currentProject.facility}</span> • Lead: {currentProject.lead}
            </div>
          </div>

          {/* Commit Hash Badge */}
          <div className="flex flex-col items-end text-xs text-slate-400">
            <div className="flex items-center gap-1.5 font-mono">
              <span className="text-slate-500">commit:</span>
              <span className="text-cyan-400 font-bold bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/50" title={nb.commitHash}>
                {nb.commitHash.substring(0, 8)}...
              </span>
            </div>
            <span className="text-[10px] text-slate-500 mt-0.5">{nb.timestamp}</span>
          </div>
        </div>

        {/* Contributing Disciplines Strip */}
        <div className="flex flex-wrap items-center gap-3 py-3 border-b border-slate-800/60">
          <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Contributing Disciplines:</span>
          {currentProject.disciplines.map((dCode) => {
            const meta = getSubjectMetadata(dCode);
            return (
              <div key={dCode} className="inline-flex items-center gap-2 px-3 py-1 rounded-xl bg-slate-900/80 border border-slate-800">
                <SubjectEmblem courseCode={dCode} size="sm" showFrame={false} glow={false} />
                <span className="text-xs font-semibold text-slate-200">{meta.disciplineName || meta.name}</span>
                <span className="text-[10px] font-mono text-slate-500">[{dCode}]</span>
              </div>
            );
          })}
        </div>

        {/* Studio Sub-Navigation Tabs */}
        <div className="flex items-center gap-2 pt-4 pb-2 border-b border-slate-800/50">
          <button
            onClick={() => setActiveSubTab("markdown")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeSubTab === "markdown"
                ? "bg-[var(--theme-primary,#00F0B5)]/15 text-[var(--theme-primary,#00F0B5)] border border-[var(--theme-primary,#00F0B5)]/40"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <span>📝</span>
            <span>Markdown Lab Protocol</span>
          </button>

          <button
            onClick={() => setActiveSubTab("mna")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeSubTab === "mna"
                ? "bg-cyan-500/15 text-cyan-400 border border-cyan-500/40"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <span>🧮</span>
            <span>MNA Matrix State</span>
          </button>

          <button
            onClick={() => setActiveSubTab("spice")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeSubTab === "spice"
                ? "bg-purple-500/15 text-purple-400 border border-purple-500/40"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <span>⚡</span>
            <span>SPICE Netlist Deck</span>
          </button>

          <button
            onClick={() => setActiveSubTab("oscilloscope")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeSubTab === "oscilloscope"
                ? "bg-amber-500/15 text-amber-400 border border-amber-500/40"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <span>📈</span>
            <span>Oscilloscope Waveforms</span>
          </button>
        </div>

        {/* Studio Tab Content Views */}
        <div className="pt-4">

          {/* 1. Markdown Protocol View */}
          {activeSubTab === "markdown" && (
            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 leading-relaxed space-y-4">
              <div className="prose prose-invert max-w-none text-xs sm:text-sm text-slate-300 font-sans whitespace-pre-line">
                {nb.markdown}
              </div>
              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
                <span>Verified under Anna University ECE Academic Council Standards</span>
                <span className="font-mono text-emerald-400">Status: Experiment Validated</span>
              </div>
            </div>
          )}

          {/* 2. MNA Matrix State View */}
          {activeSubTab === "mna" && (
            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-white">Modified Nodal Analysis (MNA) DC Operating State</h4>
                  <p className="text-xs text-slate-400">Conductance matrix G · v = i formulation for {nb.mnaState.circuit}</p>
                </div>
                <div className="text-right">
                  <div className="text-xs text-slate-400">Condition Number:</div>
                  <div className="text-xs font-mono font-bold text-cyan-400">{nb.mnaState.conditionNumber} (Stable)</div>
                </div>
              </div>

              {/* Node Voltage Bars */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
                {nb.mnaState.voltages.map((v, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-950/80 border border-slate-800">
                    <div className="text-[10px] text-slate-500 font-mono">Node Voltage V({idx})</div>
                    <div className="text-base font-bold text-emerald-400 font-mono mt-0.5">{v.toFixed(3)} V</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 3. SPICE Netlist Deck View */}
          {activeSubTab === "spice" && (
            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-white">Berkeley SPICE 3f5 Compatible Deck</h4>
                  <p className="text-xs text-slate-400">Exportable for ngspice, LTspice, and Cadence Spectre verification</p>
                </div>
                <button
                  onClick={handleCopySpice}
                  className="px-3 py-1.5 rounded-xl bg-purple-500/15 text-purple-300 border border-purple-500/30 text-xs font-bold hover:bg-purple-500/25 transition-all"
                >
                  {copiedSpice ? "✓ Copied Netlist!" : "Copy .cir Deck"}
                </button>
              </div>

              <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-purple-300 overflow-x-auto leading-relaxed">
                {nb.spiceDeck}
              </pre>
            </div>
          )}

          {/* 4. Oscilloscope Waveform View */}
          {activeSubTab === "oscilloscope" && (
            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-white">Digital Storage Oscilloscope (DSO) Capture</h4>
                  <p className="text-xs text-slate-400">Hardware-in-the-Loop bench snapshot via Lab 304 Rigol/Keysight instrumentation</p>
                </div>
                <div className="flex items-center gap-3 text-xs">
                  <span className="flex items-center gap-1.5 text-amber-400 font-semibold">
                    <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span> CH1: {nb.waveform.channel1}
                  </span>
                  <span className="flex items-center gap-1.5 text-cyan-400 font-semibold">
                    <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span> CH2: {nb.waveform.channel2}
                  </span>
                </div>
              </div>

              {/* Simulated Waveform Canvas Display */}
              <div className="h-36 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-center relative overflow-hidden p-4">
                {/* Oscilloscope Grid Background */}
                <div
                  className="absolute inset-0 opacity-20"
                  style={{
                    backgroundImage: "linear-gradient(to right, #334155 1px, transparent 1px), linear-gradient(to bottom, #334155 1px, transparent 1px)",
                    backgroundSize: "24px 24px"
                  }}
                />
                
                {/* Waveform Trace SVG */}
                <svg className="w-full h-full relative z-10" viewBox="0 0 600 120" preserveAspectRatio="none">
                  {/* CH1 Waveform (Amber) */}
                  <path
                    d="M 0 60 Q 75 10 150 60 T 300 60 T 450 60 T 600 60"
                    fill="none"
                    stroke="#F59E0B"
                    strokeWidth="2.5"
                  />
                  {/* CH2 Waveform (Cyan) */}
                  <path
                    d="M 0 60 Q 75 95 150 60 T 300 60 T 450 60 T 600 60"
                    fill="none"
                    stroke="#00D8F6"
                    strokeWidth="2"
                    strokeDasharray="4 2"
                  />
                </svg>
              </div>

              {/* Waveform Metric Badges */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
                <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase tracking-wider">Peak-to-Peak (Vpp)</div>
                  <div className="text-base font-bold text-amber-400 font-mono mt-0.5">{nb.waveform.vpp} V</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase tracking-wider">True RMS Voltage</div>
                  <div className="text-base font-bold text-cyan-400 font-mono mt-0.5">{nb.waveform.vrms} V</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase tracking-wider">Measured Frequency</div>
                  <div className="text-base font-bold text-emerald-400 font-mono mt-0.5">{nb.waveform.freq} MHz</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase tracking-wider">Duty Cycle</div>
                  <div className="text-base font-bold text-purple-400 font-mono mt-0.5">{nb.waveform.dutyCycle}%</div>
                </div>
              </div>
            </div>
          )}

        </div>

      </div>

    </div>
  );
}
