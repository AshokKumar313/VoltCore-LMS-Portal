import React, { useState } from 'react';

const VISUAL_ASSETS = [
  {
    id: 'formula-master',
    title: 'ECE Core Master Formula Infographic',
    category: 'Poster',
    description: 'Foundational analytical equations across Signals & DSP, Analog Devices, Electromagnetics, and Embedded Systems.',
    dimensions: '1200 × 900 px (4:3)',
    format: 'Vector SVG',
    filePath: '/assets/posters/ece_formula_master_poster.svg',
    discipline: 'All ECE Disciplines',
    tags: ['Formulas', 'AU-R2023', 'High-Res Print', 'IEEE']
  },
  {
    id: 'stm32-roadmap',
    title: 'Embedded Systems & RTOS Mastery Roadmap',
    category: 'Roadmap',
    description: 'Step-by-step 4-stage progression from bare-metal registers and clock trees to FreeRTOS, CMSIS-DSP, and Edge TinyML.',
    dimensions: '1200 × 900 px (4:3)',
    format: 'Vector SVG',
    filePath: '/assets/posters/stm32_architecture_roadmap.svg',
    discipline: 'Embedded Real-Time Systems & IoT',
    tags: ['Cortex-M', 'FreeRTOS', 'Curriculum Map', 'Firmware']
  },
  {
    id: 'dsp-lecture-deck',
    title: 'Discrete Signal Processing & Fast Algorithms',
    category: 'Slide Deck',
    description: '16:9 OBE lecture slide deck highlighting discrete convolution, Z-transforms, FFT butterfly stages, and FIR windowing.',
    dimensions: '1200 × 675 px (16:9)',
    format: 'Vector SVG',
    filePath: '/assets/presentations/ece_dsp_spectral_lecture_deck.svg',
    discipline: 'Signals, DSP & Wavelet Analysis',
    tags: ['Lecture Deck', '16:9 Presentation', 'OBE Syllabus']
  },
  {
    id: 'cover-dsp',
    title: 'Signals, DSP & Wavelet Studio Cover',
    category: 'Cover Artwork',
    description: 'Bespoke banner featuring Radix-2 FFT butterflies, Dirac delta trains, and KaTeX discrete frequency transforms.',
    dimensions: '1200 × 400 px (3:1)',
    format: 'Vector SVG',
    filePath: '/assets/covers/cover_signals_dsp.svg',
    discipline: 'Signals, DSP & Wavelet Analysis',
    tags: ['Cover Banner', 'Hero Artwork', 'KaTeX Motifs']
  },
  {
    id: 'cover-analog',
    title: 'Semiconductor Devices & Integrated Circuits',
    category: 'Cover Artwork',
    description: 'Bespoke banner featuring hybrid-π small-signal transconductance models and differential amplifier pairs.',
    dimensions: '1200 × 400 px (3:1)',
    format: 'Vector SVG',
    filePath: '/assets/covers/cover_analog_devices.svg',
    discipline: 'Semiconductor Devices & Integrated Circuits',
    tags: ['Cover Banner', 'Analog ICs', 'BJT / MOS']
  },
  {
    id: 'cover-vlsi',
    title: 'Digital Systems & Computer Architecture',
    category: 'Cover Artwork',
    description: 'Bespoke banner featuring 5-stage RISC-V pipelined data paths, timing buses, and clock distribution trees.',
    dimensions: '1200 × 400 px (3:1)',
    format: 'Vector SVG',
    filePath: '/assets/covers/cover_digital_vlsi.svg',
    discipline: 'Digital Systems & Computer Architecture',
    tags: ['Cover Banner', 'VLSI Logic', 'RISC-V']
  },
  {
    id: 'cover-comm',
    title: 'Electromagnetic Waves, Antennas & RF',
    category: 'Cover Artwork',
    description: 'Bespoke banner featuring 16-QAM constellations, Maxwell wave equations, and microwave Smith charts.',
    dimensions: '1200 × 400 px (3:1)',
    format: 'Vector SVG',
    filePath: '/assets/covers/cover_comm_rf.svg',
    discipline: 'Electromagnetic Waves, Antennas & RF',
    tags: ['Cover Banner', 'Microwave RF', 'Constellation']
  },
  {
    id: 'cover-embedded',
    title: 'Embedded Real-Time Systems & IoT Studio',
    category: 'Cover Artwork',
    description: 'Bespoke banner featuring ARM Cortex-M NVIC interrupt trees, DMA circular buffers, and AHB crossbar traces.',
    dimensions: '1200 × 400 px (3:1)',
    format: 'Vector SVG',
    filePath: '/assets/covers/cover_embedded_iot.svg',
    discipline: 'Embedded Real-Time Systems & IoT',
    tags: ['Cover Banner', 'Microcontrollers', 'DMA / RTOS']
  },
  {
    id: 'cover-control',
    title: 'Linear Control Theory & Dynamic Systems',
    category: 'Cover Artwork',
    description: 'Bespoke banner featuring s-plane root locus branches, Nyquist stability contours, and asymptotic Bode plots.',
    dimensions: '1200 × 400 px (3:1)',
    format: 'Vector SVG',
    filePath: '/assets/covers/cover_control_em.svg',
    discipline: 'Linear Control Theory & Instrumentation',
    tags: ['Cover Banner', 'Root Locus', 'Bode Plots']
  }
];

export default function CanvaVisualShowcase() {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [activeLightbox, setActiveLightbox] = useState(null);
  const [showCanvaGuide, setShowCanvaGuide] = useState(false);

  const categories = ['All', 'Poster', 'Roadmap', 'Slide Deck', 'Cover Artwork'];

  const filteredAssets = selectedCategory === 'All'
    ? VISUAL_ASSETS
    : VISUAL_ASSETS.filter(a => a.category === selectedCategory);

  const handlePrintAsset = (path) => {
    const printWindow = window.open(path, '_blank');
    if (printWindow) {
      printWindow.addEventListener('load', () => {
        printWindow.print();
      });
    }
  };

  return (
    <div className="w-full bg-[var(--surface-color,#0b1329)] border border-[var(--border-color,#1e293b)] rounded-2xl p-6 sm:p-8 shadow-xl">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-[var(--border-color,#1e293b)]">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20 mb-2">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Canva Visual Studio &amp; Presentation Gallery
          </div>
          <h2 className="text-2xl font-extrabold text-[var(--text-color,#f8fafc)] tracking-tight">
            Academic Posters, Slide Decks &amp; Vector Artwork
          </h2>
          <p className="text-sm text-[var(--text-secondary,#94a3b8)] mt-1">
            Official MIT Campus Anna University Regulation 2023 visual materials. Ready for classroom projection, laboratory wall display, and study prints.
          </p>
        </div>

        {/* Canva Drop-in Guide Button */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowCanvaGuide(!showCanvaGuide)}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-[var(--card-bg,#0f172a)] text-sky-400 border border-sky-500/30 hover:bg-sky-500/10 transition-all flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {showCanvaGuide ? 'Hide Canva Guide' : 'Canva Drop-In Guide'}
          </button>
        </div>
      </div>

      {/* Collapsible Canva Guide */}
      {showCanvaGuide && (
        <div className="mt-6 p-5 rounded-xl bg-gradient-to-r from-sky-950/40 to-slate-900 border border-sky-500/30 text-sm">
          <div className="flex items-start justify-between">
            <h3 className="font-bold text-sky-300 text-base flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-sky-400 animate-pulse"></span>
              Custom Canva Asset Drop-In Instructions
            </h3>
            <span className="text-xs text-sky-400/80 bg-sky-950 px-2.5 py-0.5 rounded border border-sky-800">
              Zero-Recompile Live Updates
            </span>
          </div>
          <p className="text-slate-300 mt-2 leading-relaxed">
            You can design custom vector covers, infographics, and lecture slide decks in <strong>Canva</strong> or Figma and drop them directly into the repository. They render automatically across all 18 institutional themes:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-4">
            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <div className="text-xs font-bold text-sky-400">Course &amp; Unit Covers</div>
              <div className="text-xs text-slate-400 mt-1">Path: <code className="text-slate-200">public/assets/covers/</code></div>
              <div className="text-[11px] text-slate-500 mt-0.5">1200 × 400 px (3:1 ratio), SVG &lt; 15 KB</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <div className="text-xs font-bold text-emerald-400">Posters &amp; Roadmaps</div>
              <div className="text-xs text-slate-400 mt-1">Path: <code className="text-slate-200">public/assets/posters/</code></div>
              <div className="text-[11px] text-slate-500 mt-0.5">1200 × 900 px (4:3 ratio), SVG &lt; 15 KB</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <div className="text-xs font-bold text-purple-400">Lecture Slide Decks</div>
              <div className="text-xs text-slate-400 mt-1">Path: <code className="text-slate-200">public/assets/presentations/</code></div>
              <div className="text-[11px] text-slate-500 mt-0.5">1200 × 675 px (16:9 ratio), SVG &lt; 15 KB</div>
            </div>
          </div>
          <div className="mt-3 text-xs text-amber-300/90 flex items-center gap-1.5">
            <svg className="w-4 h-4 text-amber-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            Mandatory Invariant: Never display alphanumeric course codes on artwork. Always use clean subject and discipline names.
          </div>
        </div>
      )}

      {/* Category Filter Pills */}
      <div className="flex flex-wrap items-center gap-2 mt-6">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              selectedCategory === cat
                ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/20'
                : 'bg-[var(--card-bg,#0f172a)] text-[var(--text-secondary,#94a3b8)] border border-[var(--border-color,#1e293b)] hover:text-white hover:border-slate-700'
            }`}
          >
            {cat}
          </button>
        ))}
        <span className="ml-auto text-xs text-slate-500 hidden sm:inline">
          Showing {filteredAssets.length} of {VISUAL_ASSETS.length} visual assets
        </span>
      </div>

      {/* Asset Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
        {filteredAssets.map((asset) => (
          <div
            key={asset.id}
            className="group relative flex flex-col rounded-xl overflow-hidden bg-[var(--card-bg,#0f172a)] border border-[var(--border-color,#1e293b)] hover:border-sky-500/50 hover:shadow-xl hover:shadow-sky-500/5 transition-all duration-300"
          >
            {/* Visual Preview Container */}
            <div
              onClick={() => setActiveLightbox(asset)}
              className="relative w-full h-48 bg-slate-950 overflow-hidden cursor-pointer flex items-center justify-center border-b border-[var(--border-color,#1e293b)] group-hover:bg-slate-900 transition-colors"
            >
              <img
                src={asset.filePath}
                alt={asset.title}
                loading="lazy"
                className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-slate-950/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                <span className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-sky-500 text-white shadow-lg flex items-center gap-1.5">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  Preview Fullscreen
                </span>
              </div>
              <span className="absolute top-2.5 left-2.5 px-2 py-0.5 rounded text-[10px] font-bold bg-slate-900/90 text-sky-400 border border-slate-700 backdrop-blur-sm">
                {asset.category}
              </span>
            </div>

            {/* Meta & Description */}
            <div className="p-4 flex-1 flex flex-col justify-between">
              <div>
                <div className="text-[11px] font-semibold text-sky-400 uppercase tracking-wider">
                  {asset.discipline}
                </div>
                <h4 className="font-bold text-[var(--text-color,#f8fafc)] text-base mt-1 line-clamp-1 group-hover:text-sky-300 transition-colors">
                  {asset.title}
                </h4>
                <p className="text-xs text-[var(--text-secondary,#94a3b8)] mt-1.5 line-clamp-2 leading-relaxed">
                  {asset.description}
                </p>
              </div>

              {/* Tags & Action Buttons */}
              <div className="mt-4 pt-3 border-t border-[var(--border-color,#1e293b)] flex items-center justify-between gap-2">
                <div className="text-[10px] text-slate-500 font-mono">
                  {asset.dimensions}
                </div>
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => handlePrintAsset(asset.filePath)}
                    title="Print or Export to PDF"
                    className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                    </svg>
                  </button>
                  <a
                    href={asset.filePath}
                    download
                    title="Download Source SVG"
                    className="p-1.5 rounded-lg text-sky-400 hover:text-white hover:bg-sky-500 transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                  </a>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Fullscreen Lightbox Modal */}
      {activeLightbox && (
        <div
          onClick={() => setActiveLightbox(null)}
          className="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-md flex items-center justify-center p-4 sm:p-6"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="relative max-w-5xl w-full max-h-[90vh] bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl flex flex-col"
          >
            {/* Lightbox Header */}
            <div className="flex items-center justify-between px-6 py-4 bg-slate-950 border-b border-slate-800">
              <div>
                <span className="text-xs font-bold text-sky-400 uppercase tracking-wider">
                  {activeLightbox.category} • {activeLightbox.discipline}
                </span>
                <h3 className="text-lg font-bold text-white mt-0.5">
                  {activeLightbox.title}
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handlePrintAsset(activeLightbox.filePath)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-200 hover:bg-slate-700 transition-colors flex items-center gap-1.5"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                  </svg>
                  Print / PDF
                </button>
                <a
                  href={activeLightbox.filePath}
                  download
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-sky-500 text-white hover:bg-sky-400 transition-colors flex items-center gap-1.5"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download SVG
                </a>
                <button
                  onClick={() => setActiveLightbox(null)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Lightbox Image Preview */}
            <div className="flex-1 overflow-auto p-4 sm:p-6 bg-slate-950/80 flex items-center justify-center min-h-[450px]">
              <img
                src={activeLightbox.filePath}
                alt={activeLightbox.title}
                className="max-w-full max-h-[70vh] object-contain rounded-lg shadow-lg border border-slate-800"
              />
            </div>

            {/* Lightbox Footer */}
            <div className="px-6 py-3 bg-slate-950 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
              <div>Dimensions: <span className="font-mono text-slate-200">{activeLightbox.dimensions}</span></div>
              <div>Madras Institute of Technology (MIT) Campus, Anna University</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
