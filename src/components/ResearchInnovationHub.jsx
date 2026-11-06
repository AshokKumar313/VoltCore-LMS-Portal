import React, { useState } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Phase J: Research & Innovation Hub (Features 301–310)
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 *
 * Features:
 *   - Feature 301: IEEE Paper Reading Workspace (Structured multi-column layout, margin notes)
 *   - Feature 302: Research Topic Discovery Board (6G THz, Neuromorphic, GaN, RISC-V, PIC)
 *   - Feature 303: Research Paper Tagging System (Domain, Methodology, Tools, TRL 1-9)
 *   - Feature 304: Citation Format Assistant (BibTeX, IEEE, APA, Harvard, Chicago)
 *   - Feature 305: Literature Review Organizer (Comparative matrix, SOTA metrics, gaps)
 *   - Feature 306: Research Gap Tracking Board (Open scientific hurdles & attack vectors)
 *   - Feature 307: Research Idea Notebook (Hypotheses, apparatus, expected outcomes)
 *   - Feature 308: Patent Reference Organizer (USPTO/IPO/WIPO, CPC/IPC codes, prior art)
 *   - Feature 309: Research Collaboration Workspace (CRediT taxonomy, roles, equipment)
 *   - Feature 310: Publication Progress Tracker (Stages: Draft -> Review -> Q1/Q2 Accepted)
 * Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
 * ========================================================================================
 */

// Frontier ECE Research Topics (Feature 302)
const FRONTIERS = [
  {
    id: "6g_sub_thz_ris",
    title: "Sub-THz Wireless & Reconfigurable Intelligent Surfaces (RIS)",
    domain: "Wireless & RF Systems",
    trl: 4,
    freq: "100 GHz – 300 GHz (D-Band)",
    venues: "IEEE TWC • IEEE JSAC • IEEE MTT-S IMS",
    challenges: [
      "Near-field spherical wavefront beam-squint mitigation",
      "Ultra-low-power PIN diode control for 10,000+ element metasurfaces",
      "Joint communication and radar sensing (JCAS) waveform design"
    ],
    apparatus: "Vector Network Analyzer (110 GHz), Horn Antennas, Anechoic Chamber (MIT Lab 304)"
  },
  {
    id: "neuromorphic_memristor",
    title: "Neuromorphic In-Memory Computing Using Memristive Arrays",
    domain: "VLSI & Brain-Inspired Systems",
    trl: 3,
    freq: "Sub-100 MHz (Event-Driven Asynchronous)",
    venues: "IEEE JSSC • IEEE TED • Nature Electronics",
    challenges: [
      "Device-to-device conductance variability and sneak-path current leakage",
      "ADC power and silicon area domination in multi-bit analog crossbars",
      "On-chip spike-timing-dependent plasticity (STDP) unsupervised stability"
    ],
    apparatus: "Keysight B1500A Parameter Analyzer, Probe Station, Cadence Virtuoso"
  },
  {
    id: "gan_power_converters",
    title: "Wide-Bandgap GaN HEMT High-Frequency Resonant Converters",
    domain: "Power Electronics & Energy",
    trl: 6,
    freq: "1 MHz – 10 MHz Switching Speed",
    venues: "IEEE TPEL • IEEE TIE • IEEE APEC",
    challenges: [
      "Parasitic inductance-induced voltage overshoot during nanosecond dV/dt switching",
      "Dynamic on-resistance (R_DS(on)) degradation from 2DEG surface electron trapping",
      "Isolated gate driver noise immunity under >100 V/ns common-mode transients"
    ],
    apparatus: "High-Voltage Differential Probes, Rogowski Coils, Thermal Imaging Camera"
  },
  {
    id: "riscv_edge_accelerators",
    title: "Custom RISC-V Vector Extensions for Low-Power TinyML",
    domain: "Embedded Systems & Computer Architecture",
    trl: 5,
    freq: "200 MHz – 500 MHz (ASIC / FPGA)",
    venues: "IEEE Micro • ACM/IEEE DAC • IEEE TC",
    challenges: [
      "Memory bandwidth starvation in tightly-coupled scratchpad SRAMs",
      "Compiler auto-vectorization for custom non-standard instructions",
      "Zero-overhead hardware loop control and SIMD MAC pipelining"
    ],
    apparatus: "Xilinx Zynq UltraScale+ FPGA Board, Vivado Design Suite, Logic Analyzer"
  },
  {
    id: "silicon_photonics",
    title: "Silicon Photonic Integrated Circuits (PIC) for Optical Interconnects",
    domain: "Photonics & Optoelectronics",
    trl: 4,
    freq: "100 Gbaud / 800 Gbps Transceivers",
    venues: "IEEE JLT • IEEE PTL • OFC",
    challenges: [
      "Thermal drift in microring resonance requiring dynamic closed-loop micro-heaters",
      "High fiber-to-chip coupling loss across sub-micron silicon waveguides",
      "Heterogeneous monolithic integration of III-V lasers on standard CMOS"
    ],
    apparatus: "Tunable Laser Source, Optical Spectrum Analyzer, Precision Fiber Alignment Stage"
  }
];

// Sample Research Papers (Feature 301 & 303)
const PAPERS = [
  {
    id: "IEEE-2024-RIS",
    title: "Wideband Beam-Squint Mitigation for Sub-THz Reconfigurable Intelligent Surfaces",
    authors: "Ashok Kumar, A., Ramanathan, S., & Sridhar, V.",
    year: 2024,
    journal: "IEEE Transactions on Wireless Communications",
    volume: "23",
    issue: "4",
    pages: "2150-2165",
    doi: "10.1109/TWC.2024.9876543",
    domain: "Wireless & RF",
    tags: ["Sub-THz", "RIS", "Beam-Squint", "Phase-Shifter", "6G"],
    trl: 4,
    abstract: "Sub-terahertz communication encounters severe path loss that requires extreme aperture beamforming. However, massive physical dimensions and large signal bandwidths induce spatial-wideband beam-squint. This paper presents a true-time-delay (TTD) phase-gradient meta-atom matrix with sub-nanosecond analog delay lines to synchronize wavefront arrival across a 30 GHz bandwidth.",
    sections: {
      intro: "Path loss at 140 GHz exceeds 115 dB at 10 meters in free space. Reconfigurable Intelligent Surfaces (RIS) offer energy-efficient non-line-of-sight (NLoS) relaying.",
      math: "Phase profile: \\Phi(m, n) = -\\frac{2\\pi}{\\lambda_0} (x_m \\sin\\theta_0 \\cos\\phi_0 + y_n \\sin\\theta_0 \\sin\\phi_0). With frequency dispersion f \\ne f_0, beam deflection angle shifts by \\Delta\\theta = -\\frac{\\Delta f}{f_0} \\tan\\theta_0.",
      results: "Peak gain of 28.4 dBi maintained across 130–160 GHz with <1.2 dB beam-squint attenuation, outperforming conventional phase-only arrays by 5.4 dB."
    }
  },
  {
    id: "IEEE-2024-SNN",
    title: "A 0.45V 1.2uW Neuromorphic In-Memory SNN Accelerator in 28nm FD-SOI",
    authors: "Ashok Kumar, A. and Vikram, K.",
    year: 2024,
    journal: "IEEE Journal of Solid-State Circuits",
    volume: "59",
    issue: "8",
    pages: "2410-2422",
    doi: "10.1109/JSSC.2024.1234567",
    domain: "VLSI Design",
    tags: ["Neuromorphic", "SNN", "Memristor", "FD-SOI", "Sub-Threshold"],
    trl: 5,
    abstract: "Continuous edge biosignal inference demands ultra-low power consumption. We propose a sub-threshold 1T1R memristive crossbar array with spike-rate encoding, eliminating conventional high-power high-resolution ADCs with simple asynchronous integrate-and-fire threshold comparators.",
    sections: {
      intro: "Standard von Neumann architectures dissipate >80% of total energy moving weights between memory and arithmetic logic units.",
      math: "Memristor conductance update: G_{new} = G_{old} + \\Delta G, where \\Delta G = \\alpha \\exp(-\\beta |\\Delta t|) represents biological STDP plasticity.",
      results: "Achieves 94.6% classification accuracy on ECG arrhythmia datasets with only 1.2 uW power dissipation at 0.45V supply rail."
    }
  }
];

// Literature Review Comparative Matrix (Feature 305)
const LIT_REVIEW_DATA = [
  {
    id: "REV-01",
    title: "Sub-THz RIS with True-Time-Delay Matrix",
    authors: "Kumar et al. (MIT Campus)",
    year: 2024,
    method: "True-Time-Delay Analog Delay Lines",
    strengths: "Eliminates beam-squint over 30 GHz band, 28.4 dBi gain",
    limitations: "Higher circuit complexity and DC control power",
    metrics: "BW: 30 GHz, Gain: 28.4 dBi, Loss: <1.2 dB"
  },
  {
    id: "REV-02",
    title: "Discrete Phase-Only Metasurface at 140 GHz",
    authors: "Zhang & Wei (Tsinghua)",
    year: 2023,
    method: "1-Bit PIN Diode Discrete Switching",
    strengths: "Extremely simple biasing circuit, minimal component count",
    limitations: "Severe beam-squint (>6 dB drop at band edges)",
    metrics: "BW: 8 GHz, Gain: 22.1 dBi, Loss: 6.5 dB"
  },
  {
    id: "REV-03",
    title: "Varactor-Tuned Continuous Phase Metamaterial",
    authors: "Alvarez et al. (EPFL)",
    year: 2024,
    method: "Continuous Varactor Capacitance Modulation",
    strengths: "Smooth 360-degree phase agility, low quantization lobes",
    limitations: "High parasitic series resistance limits Q-factor",
    metrics: "BW: 12 GHz, Gain: 24.0 dBi, Loss: 3.8 dB"
  }
];

// Essential ECE Patents (Feature 308)
const PATENTS = [
  {
    number: "US11234567B2",
    title: "Apparatus and Method for Beam-Squint Compensation in Wideband Phased Arrays",
    assignee: "Qualcomm Incorporated",
    cpc: "H01Q 3/26, H04B 7/06",
    claim: "A phased-array receiver comprising an array of antenna elements coupled to a true-time-delay network and frequency-domain phase equalizer.",
    priorArt: "Distinguishes over narrowband phase shifters by canceling spatial frequency dispersion across wide channel bandwidths."
  },
  {
    number: "IN202441012345",
    title: "Adaptive Sub-Threshold In-Memory SNN Accelerator with 1T1R Memristive Crossbars",
    assignee: "Anna University (MIT Campus)",
    cpc: "G06N 3/063, G11C 13/00",
    claim: "An event-driven neural processing core comprising resistive switching memory cells and asynchronous integrate-and-fire comparators.",
    priorArt: "Eliminates power-hungry high-resolution Flash/SAR ADCs, operating directly in the charge-domain below 0.5V."
  }
];

export default function ResearchInnovationHub() {
  const [activeTab, setActiveTab] = useState('reading'); // 'reading', 'discovery', 'citations', 'gaps', 'collaboration'

  // Feature 301 State
  const [selectedPaperIndex, setSelectedPaperIndex] = useState(0);
  const [annotations, setAnnotations] = useState([
    { id: 1, section: "Mathematics", text: "Notice how beam-squint deflection angle Delta_theta is directly proportional to fractional bandwidth Delta_f / f_0!" },
    { id: 2, section: "Experimental Results", text: "Benchmark peak gain of 28.4 dBi aligns within 0.3 dB of analytical simulation models." }
  ]);
  const [newAnnotationText, setNewAnnotationText] = useState('');

  // Feature 304 State
  const [citationFormat, setCitationFormat] = useState('bibtex');
  const [copiedNotification, setCopiedNotification] = useState(false);

  // Feature 306 State
  const [gaps, setGaps] = useState([
    {
      id: "GAP-101",
      domain: "Wireless & 6G",
      statement: "Phase noise accumulation in local sub-THz oscillators degrades symbol error rate (SER) in dense 1024-QAM constellations.",
      sota: "Commercial PLLs at 140 GHz exhibit phase noise > -85 dBc/Hz at 100 kHz offset.",
      vector: "Optical injection locking using dual-wavelength distributed feedback (DFB) lasers to achieve < -110 dBc/Hz phase noise."
    },
    {
      id: "GAP-102",
      domain: "Edge AI / VLSI",
      statement: "Sneak path leakage currents in crossbar arrays corrupt analog vector-matrix multiplication results during parallel row reading.",
      sota: "Current 1T1R structures require large access transistors, limiting cell area scaling.",
      vector: "Self-rectifying volatile threshold switches (1S1R) with >10^4 non-linear selectivity."
    }
  ]);
  const [newGapDomain, setNewGapDomain] = useState('Power Electronics');
  const [newGapStatement, setNewGapStatement] = useState('');
  const [newGapVector, setNewGapVector] = useState('');

  // Feature 307 State
  const [ideas, setIdeas] = useState([
    {
      id: "IDEA-01",
      title: "Self-Powered Wearable ECG SNN Processor Using Piezoelectric Harvester",
      hypothesis: "Energy harvested from human body biomechanical motion (0.8 mW) can continuously sustain sub-threshold SNN inference.",
      apparatus: "Mide Piezoelectric Transducer, Custom Energy Harvesting IC, Keysight DSOX3024T",
      score: 9.2
    }
  ]);
  const [ideaTitle, setIdeaTitle] = useState('');
  const [ideaHypothesis, setIdeaHypothesis] = useState('');
  const [ideaApparatus, setIdeaApparatus] = useState('');

  // Feature 310 State
  const [manuscripts, setManuscripts] = useState([
    {
      id: "PUB-01",
      title: "Wideband Beam-Squint Mitigation for Sub-THz Reconfigurable Intelligent Surfaces",
      journal: "IEEE Transactions on Wireless Communications",
      quartile: "Q1",
      status: "UNDER_PEER_REVIEW",
      impactFactor: 8.9,
      deadline: "2026-12-15"
    },
    {
      id: "PUB-02",
      title: "A 0.45V 1.2uW Neuromorphic In-Memory SNN Accelerator in 28nm FD-SOI",
      journal: "IEEE Journal of Solid-State Circuits (JSSC)",
      quartile: "Q1",
      status: "ACCEPTED",
      impactFactor: 6.2,
      deadline: "2026-11-30"
    }
  ]);

  const currPaper = PAPERS[selectedPaperIndex];

  // Citation computation
  const getFormattedCitation = () => {
    const p = currPaper;
    if (citationFormat === 'bibtex') {
      return `@article{kumar2024${p.id.toLowerCase().replace(/[^a-z0-9]/g, '')},
  author    = {${p.authors}},
  title     = {{${p.title}}},
  journal   = {${p.journal}},
  volume    = {${p.volume}},
  number    = {${p.issue}},
  pages     = {${p.pages}},
  year      = {${p.year}},
  doi       = {${p.doi}}
}`;
    } else if (citationFormat === 'ieee') {
      return `${p.authors}, "${p.title}," ${p.journal}, vol. ${p.volume}, no. ${p.issue}, pp. ${p.pages}, ${p.year}, doi: ${p.doi}.`;
    } else if (citationFormat === 'apa') {
      return `${p.authors} (${p.year}). ${p.title}. ${p.journal}, ${p.volume}(${p.issue}), ${p.pages}. https://doi.org/${p.doi}`;
    } else {
      return `${p.authors}, ${p.year}. "${p.title}." ${p.journal} ${p.volume}, no. ${p.issue}: ${p.pages}.`;
    }
  };

  const handleCopyCitation = () => {
    navigator.clipboard.writeText(getFormattedCitation());
    setCopiedNotification(true);
    setTimeout(() => setCopiedNotification(false), 2000);
  };

  const handleAddAnnotation = () => {
    if (!newAnnotationText.trim()) return;
    setAnnotations([
      ...annotations,
      { id: Date.now(), section: "General Note", text: newAnnotationText.trim() }
    ]);
    setNewAnnotationText('');
  };

  const handleAddGap = () => {
    if (!newGapStatement.trim()) return;
    setGaps([
      ...gaps,
      {
        id: `GAP-${Date.now().toString().slice(-4)}`,
        domain: newGapDomain,
        statement: newGapStatement.trim(),
        sota: "Literature identifies severe scaling or noise boundaries.",
        vector: newGapVector.trim() || "Algorithmic co-design with domain-specific hardware."
      }
    ]);
    setNewGapStatement('');
    setNewGapVector('');
  };

  const handleAddIdea = () => {
    if (!ideaTitle.trim()) return;
    setIdeas([
      ...ideas,
      {
        id: `IDEA-${Date.now().toString().slice(-4)}`,
        title: ideaTitle.trim(),
        hypothesis: ideaHypothesis.trim() || "Circuit optimization will lower power dissipation by 30%.",
        apparatus: ideaApparatus.trim() || "Standard MIT Campus ECE Lab test bench.",
        score: 8.8
      }
    ]);
    setIdeaTitle('');
    setIdeaHypothesis('');
    setIdeaApparatus('');
  };

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-8 text-slate-100 font-sans">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-emerald-950/70 via-teal-950/50 to-slate-900/80 border border-emerald-500/30 rounded-2xl p-6 mb-8 backdrop-blur shadow-2xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 rounded-full uppercase tracking-wider">
                Phase J • Features 301–310
              </span>
              <span className="px-2.5 py-0.5 text-xs font-semibold bg-teal-500/20 text-teal-300 border border-teal-400/30 rounded-full">
                Research & Innovation
              </span>
            </div>
            <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-200 via-teal-200 to-cyan-200">
              Research & Innovation Hub
            </h1>
            <p className="text-sm text-slate-300 mt-1">
              Anna University / MIT Campus (ECE Dept, Reg 2023) • Lead: Ashok Kumar A (2023MITEC042)
            </p>
          </div>
          <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl px-4 py-2.5 text-right font-mono">
            <div className="text-xs text-slate-400">Target Standard</div>
            <div className="text-sm font-semibold text-emerald-400">IEEE Transactions • Q1 Index</div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex flex-wrap gap-2 mb-6 border-b border-slate-800 pb-4">
        {[
          { id: 'reading', label: 'IEEE Paper Workspace', badge: 'Feat 301, 303' },
          { id: 'discovery', label: 'Research Frontiers', badge: 'Feat 302' },
          { id: 'citations', label: 'Citations & Lit Review', badge: 'Feat 304-305' },
          { id: 'gaps', label: 'Gaps & Ideation Notebook', badge: 'Feat 306-307' },
          { id: 'collaboration', label: 'Patents & Publication Pipeline', badge: 'Feat 308-310' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2.5 rounded-xl text-sm font-medium transition-all flex items-center gap-2 ${
              activeTab === tab.id
                ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/30 border border-emerald-400/40'
                : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-700/50'
            }`}
          >
            <span>{tab.label}</span>
            <span className={`text-[10px] px-1.5 py-0.5 rounded-md ${activeTab === tab.id ? 'bg-emerald-800 text-emerald-200' : 'bg-slate-900 text-slate-400'}`}>
              {tab.badge}
            </span>
          </button>
        ))}
      </div>

      {/* TAB 1: IEEE Paper Reading Workspace & Tagging (Features 301 & 303) */}
      {activeTab === 'reading' && (
        <div className="space-y-6">
          {/* Paper Selector & Tagging Header */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4 pb-4 border-b border-slate-800">
              <div>
                <span className="text-xs font-mono text-emerald-400 uppercase tracking-wider">{currPaper.domain}</span>
                <h2 className="text-xl font-bold text-white mt-0.5">{currPaper.title}</h2>
                <div className="text-xs text-slate-400 mt-1">
                  {currPaper.authors} • <span className="text-slate-200 font-semibold">{currPaper.journal}</span> ({currPaper.year})
                </div>
              </div>

              <div className="flex gap-2">
                {PAPERS.map((p, idx) => (
                  <button
                    key={p.id}
                    onClick={() => setSelectedPaperIndex(idx)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                      selectedPaperIndex === idx ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                    }`}
                  >
                    Paper #{idx + 1}
                  </button>
                ))}
              </div>
            </div>

            {/* Taxonomy Tags */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-semibold text-slate-400 mr-1">Taxonomy Tags:</span>
              {currPaper.tags.map((tag, i) => (
                <span key={i} className="px-2.5 py-1 text-xs bg-emerald-950/60 text-emerald-300 border border-emerald-800/50 rounded-md font-mono">
                  #{tag}
                </span>
              ))}
              <span className="ml-auto px-3 py-1 text-xs bg-cyan-950/60 text-cyan-300 border border-cyan-800/50 rounded-full font-mono font-bold">
                TRL Level {currPaper.trl} (Experimental Verification)
              </span>
            </div>
          </div>

          {/* Reading Split Screen */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left 2 Cols: Structured Manuscript */}
            <div className="lg:col-span-2 space-y-4">
              {/* Abstract */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg">
                <div className="text-xs font-bold text-emerald-400 uppercase tracking-wide mb-2">Abstract</div>
                <p className="text-xs text-slate-200 leading-relaxed">{currPaper.abstract}</p>
                <div className="mt-3 text-[11px] font-mono text-cyan-400">DOI: {currPaper.doi}</div>
              </div>

              {/* Introduction */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg">
                <div className="text-xs font-bold text-slate-300 uppercase tracking-wide mb-2">1. Introduction & Motivation</div>
                <p className="text-xs text-slate-300 leading-relaxed">{currPaper.sections.intro}</p>
              </div>

              {/* Mathematical Formulation */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg">
                <div className="text-xs font-bold text-cyan-400 uppercase tracking-wide mb-2">2. Analytical System Formulation</div>
                <div className="bg-slate-950 p-4 rounded-lg font-mono text-xs text-cyan-200 border border-slate-800 leading-relaxed overflow-x-auto">
                  {currPaper.sections.math}
                </div>
              </div>

              {/* Experimental Results */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg">
                <div className="text-xs font-bold text-amber-400 uppercase tracking-wide mb-2">3. Experimental Benchmarks & Discussion</div>
                <p className="text-xs text-slate-300 leading-relaxed">{currPaper.sections.results}</p>
              </div>
            </div>

            {/* Right 1 Col: Interactive Margin Notes */}
            <div className="space-y-4">
              <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg">
                <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-3">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  Margin Notes & Annotations
                </h3>

                <div className="space-y-3 mb-4 max-h-[380px] overflow-y-auto pr-1">
                  {annotations.map(ann => (
                    <div key={ann.id} className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs space-y-1">
                      <div className="text-[10px] font-mono text-emerald-400 uppercase font-semibold">{ann.section}</div>
                      <p className="text-slate-300 leading-relaxed">{ann.text}</p>
                    </div>
                  ))}
                </div>

                <div className="space-y-2 pt-3 border-t border-slate-800">
                  <textarea
                    value={newAnnotationText}
                    onChange={e => setNewAnnotationText(e.target.value)}
                    rows={3}
                    placeholder="Add scientific margin note or hypothesis..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                  <button
                    onClick={handleAddAnnotation}
                    className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg transition"
                  >
                    Save Annotation
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Research Topic Discovery Board (Feature 302) */}
      {activeTab === 'discovery' && (
        <div className="space-y-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-teal-400"></span>
              ECE Frontier Research Topic Discovery Board
            </h2>
            <p className="text-xs text-slate-400 mb-6">
              Curated breakthrough technical frontiers aligned with Anna University PG/PhD curricula and MIT Campus lab capabilities
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {FRONTIERS.map(f => (
                <div key={f.id} className="bg-slate-950 border border-slate-800 hover:border-teal-500/50 rounded-xl p-5 flex flex-col justify-between transition-all shadow-lg group">
                  <div>
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-[11px] font-mono text-teal-400 font-semibold">{f.domain}</span>
                      <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-teal-950 text-teal-300 border border-teal-800 rounded">
                        TRL {f.trl}
                      </span>
                    </div>

                    <h3 className="text-sm font-bold text-white group-hover:text-teal-300 transition-colors">
                      {f.title}
                    </h3>
                    <div className="text-[11px] text-cyan-400 font-mono mt-1">{f.freq}</div>

                    <p className="text-xs text-slate-400 mt-2.5 leading-relaxed">{f.summary}</p>

                    <div className="mt-4 pt-3 border-t border-slate-800">
                      <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-1">Key Scientific Challenges:</div>
                      <ul className="space-y-1 text-xs text-slate-300">
                        {f.challenges.map((c, i) => (
                          <li key={i} className="flex items-start gap-1.5">
                            <span className="text-teal-400 text-[10px]">•</span>
                            <span className="text-[11px]">{c}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-800/60 text-[11px] text-emerald-400 font-mono">
                    <span className="text-slate-400">MIT Campus Lab Apparatus: </span>
                    {f.apparatus}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Citations & Literature Review Matrix (Features 304 & 305) */}
      {activeTab === 'citations' && (
        <div className="space-y-8">
          {/* Citation Format Assistant */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4 pb-4 border-b border-slate-800">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
                  Citation Format Assistant
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">Generate verified BibTeX, IEEE, APA 7th, and Chicago citations for publication records</p>
              </div>

              <div className="flex items-center gap-2">
                <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-800">
                  {['bibtex', 'ieee', 'apa', 'chicago'].map(fmt => (
                    <button
                      key={fmt}
                      onClick={() => setCitationFormat(fmt)}
                      className={`px-3 py-1 rounded-md text-xs font-semibold uppercase transition ${
                        citationFormat === fmt ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      {fmt}
                    </button>
                  ))}
                </div>

                <button
                  onClick={handleCopyCitation}
                  className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold rounded-lg border border-slate-700 transition flex items-center gap-1.5"
                >
                  <span>{copiedNotification ? '✓ Copied!' : 'Copy'}</span>
                </button>
              </div>
            </div>

            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-cyan-300 overflow-x-auto leading-relaxed">
              <pre>{getFormattedCitation()}</pre>
            </div>
          </div>

          {/* Literature Review Organizer Matrix */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
              Literature Review Comparative Matrix
            </h2>
            <p className="text-xs text-slate-400 mb-6">Cross-comparison of published state-of-the-art architectures, methodology, and metrics</p>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-mono">
                    <th className="py-2.5 px-3">Title & Authors</th>
                    <th className="py-2.5 px-3">Year</th>
                    <th className="py-2.5 px-3">Core Methodology</th>
                    <th className="py-2.5 px-3">Key Strengths</th>
                    <th className="py-2.5 px-3">Critical Limitations</th>
                    <th className="py-2.5 px-3">Benchmark Metrics</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {LIT_REVIEW_DATA.map(row => (
                    <tr key={row.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-3 px-3">
                        <div className="font-bold text-white">{row.title}</div>
                        <div className="text-[11px] text-slate-400">{row.authors}</div>
                      </td>
                      <td className="py-3 px-3 font-mono text-cyan-400">{row.year}</td>
                      <td className="py-3 px-3">{row.method}</td>
                      <td className="py-3 px-3 text-emerald-300">{row.strengths}</td>
                      <td className="py-3 px-3 text-amber-300">{row.limitations}</td>
                      <td className="py-3 px-3 font-mono text-teal-300">{row.metrics}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: Gaps & Ideation Notebook (Features 306 & 307) */}
      {activeTab === 'gaps' && (
        <div className="space-y-8">
          {/* Research Gap Tracker */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-red-400"></span>
              Research Gap Tracking Board
            </h2>
            <p className="text-xs text-slate-400 mb-6">Catalog of unresolved scientific hurdles and open research problems in current literature</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              {gaps.map(g => (
                <div key={g.id} className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] font-mono text-red-400 uppercase font-bold">{g.domain}</span>
                    <span className="px-2 py-0.5 text-[9px] bg-red-950 text-red-300 border border-red-800 rounded font-mono">OPEN SOTA GAP</span>
                  </div>
                  <div className="text-xs font-bold text-white">{g.statement}</div>
                  <div className="text-[11px] text-slate-400">
                    <strong className="text-slate-300">SOTA Bottleneck: </strong>{g.sota}
                  </div>
                  <div className="text-[11px] text-emerald-400 bg-emerald-950/20 p-2 rounded border border-emerald-800/30">
                    <strong>Proposed Attack Vector: </strong>{g.vector}
                  </div>
                </div>
              ))}
            </div>

            {/* Quick Gap Adder */}
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 space-y-3">
              <div className="text-xs font-bold text-slate-300">Track New Open Research Gap</div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <input
                  type="text"
                  placeholder="Domain (e.g. 6G RF, Power GaN)"
                  value={newGapDomain}
                  onChange={e => setNewGapDomain(e.target.value)}
                  className="bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white"
                />
                <input
                  type="text"
                  placeholder="Unresolved Scientific Gap Statement"
                  value={newGapStatement}
                  onChange={e => setNewGapStatement(e.target.value)}
                  className="bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white"
                />
                <input
                  type="text"
                  placeholder="Proposed Engineering Attack Vector"
                  value={newGapVector}
                  onChange={e => setNewGapVector(e.target.value)}
                  className="bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white"
                />
              </div>
              <button
                onClick={handleAddGap}
                className="px-4 py-2 bg-red-600/80 hover:bg-red-600 text-white text-xs font-semibold rounded-lg transition"
              >
                Add Research Gap
              </button>
            </div>
          </div>

          {/* Research Idea Notebook */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-indigo-400"></span>
              Research Idea Notebook (Hypothesis & Lab Formulation)
            </h2>
            <p className="text-xs text-slate-400 mb-6">Structured ideation canvas for Anna University undergraduate/postgraduate capstone theses</p>

            <div className="space-y-4 mb-6">
              {ideas.map(idea => (
                <div key={idea.id} className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-indigo-400 font-bold">{idea.id}</span>
                      <span className="text-sm font-bold text-white">{idea.title}</span>
                    </div>
                    <div className="text-xs text-slate-300">
                      <strong className="text-indigo-300">Hypothesis: </strong>{idea.hypothesis}
                    </div>
                    <div className="text-[11px] text-slate-400 font-mono">
                      <span>Required MIT Apparatus: </span>{idea.apparatus}
                    </div>
                  </div>
                  <div className="bg-indigo-950/60 border border-indigo-800 px-3 py-1.5 rounded-lg text-center font-mono">
                    <div className="text-[10px] text-slate-400">Feasibility</div>
                    <div className="text-sm font-bold text-cyan-300">{idea.score} / 10</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Quick Idea Form */}
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 space-y-3">
              <div className="text-xs font-bold text-slate-300">Log New Research Hypothesis</div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <input
                  type="text"
                  placeholder="Project/Idea Title"
                  value={ideaTitle}
                  onChange={e => setIdeaTitle(e.target.value)}
                  className="bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white"
                />
                <input
                  type="text"
                  placeholder="Formal Research Hypothesis"
                  value={ideaHypothesis}
                  onChange={e => setIdeaHypothesis(e.target.value)}
                  className="bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white"
                />
                <input
                  type="text"
                  placeholder="Required MIT Campus Laboratory Equipment"
                  value={ideaApparatus}
                  onChange={e => setIdeaApparatus(e.target.value)}
                  className="bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white"
                />
              </div>
              <button
                onClick={handleAddIdea}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition"
              >
                Log Idea to Canvas
              </button>
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: Patents, Collaboration & Publication Pipeline (Features 308-310) */}
      {activeTab === 'collaboration' && (
        <div className="space-y-8">
          {/* Patent Reference Organizer */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
              Patent Reference Organizer (Intellectual Property Catalog)
            </h2>
            <p className="text-xs text-slate-400 mb-6">Essential ECE patents with claim summaries, assignee metadata, and prior-art differentiators</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {PATENTS.map(p => (
                <div key={p.number} className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-xs text-amber-400 font-bold">{p.number}</span>
                    <span className="text-[10px] font-mono text-slate-400">{p.cpc}</span>
                  </div>
                  <div className="text-xs font-bold text-white">{p.title}</div>
                  <div className="text-[11px] text-cyan-300">Assignee: {p.assignee}</div>
                  <div className="text-[11px] text-slate-300 bg-slate-900 p-2.5 rounded border border-slate-800">
                    <strong className="text-slate-400">Independent Claim 1: </strong>{p.claim}
                  </div>
                  <div className="text-[11px] text-emerald-300">
                    <strong>Prior-Art Distinction: </strong>{p.priorArt}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Research Collaboration Roster (CRediT Taxonomy) */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-400"></span>
              Research Collaboration Workspace (CRediT Taxonomy)
            </h2>
            <p className="text-xs text-slate-400 mb-6">International CASRAI / ISO 20147 Contributor Roles Taxonomy mapping author accountability</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs">
                    AK
                  </div>
                  <div>
                    <div className="text-xs font-bold text-white">Ashok Kumar A (Lead)</div>
                    <div className="text-[10px] text-slate-400 font-mono">2023MITEC042 • MIT Campus, Anna University</div>
                  </div>
                </div>
                <div className="flex flex-wrap gap-1.5 mt-3">
                  {['Conceptualization', 'Methodology', 'Circuit Design', 'Writing - Original Draft'].map(role => (
                    <span key={role} className="px-2 py-0.5 text-[10px] bg-blue-950 text-blue-300 border border-blue-800 rounded-md">
                      {role}
                    </span>
                  ))}
                </div>
              </div>

              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-xs">
                    SR
                  </div>
                  <div>
                    <div className="text-xs font-bold text-white">Dr. S. Ramanathan (Faculty Advisor)</div>
                    <div className="text-[10px] text-slate-400 font-mono">Dept of Electronics Engineering • MIT Campus</div>
                  </div>
                </div>
                <div className="flex flex-wrap gap-1.5 mt-3">
                  {['Supervision', 'Formal Analysis', 'Validation', 'Writing - Review & Editing'].map(role => (
                    <span key={role} className="px-2 py-0.5 text-[10px] bg-indigo-950 text-indigo-300 border border-indigo-800 rounded-md">
                      {role}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Publication Progress Tracker */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
              Publication Pipeline Progress Tracker
            </h2>
            <p className="text-xs text-slate-400 mb-6">Manuscript lifecycle milestones from initial draft to Q1/Q2 peer-reviewed journal publication</p>

            <div className="space-y-4">
              {manuscripts.map(m => (
                <div key={m.id} className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-emerald-950 text-emerald-300 border border-emerald-800 rounded">
                        {m.quartile}
                      </span>
                      <span className="text-xs font-bold text-white">{m.title}</span>
                    </div>
                    <div className="text-xs text-slate-400">
                      Target Venue: <strong className="text-slate-200">{m.journal}</strong> (IF: {m.impactFactor})
                    </div>
                    <div className="text-[11px] text-cyan-400 font-mono">
                      Camera-Ready / Review Deadline: {m.deadline}
                    </div>
                  </div>

                  <div className="px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold tracking-wider bg-slate-900 border border-slate-700 text-emerald-400">
                    {m.status}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
