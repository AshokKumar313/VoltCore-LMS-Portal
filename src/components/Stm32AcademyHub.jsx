import React, { useState, useEffect, useMemo } from 'react';

/**
 * VoltCore STM32 Academy - Interactive Hub & Curriculum Explorer
 * Peer-neutral engineering learning platform for ARM Cortex-M3 & Cortex-M4F bare-metal mastery.
 * Optimized for passive thermals (zero polling daemons, client-side persistence).
 */

const TIERS = [
  { id: 'ALL', label: 'All Modules', count: 21 },
  { id: 'Tier 1: Architecture & Toolchain', label: 'Tier 1: Core & Toolchain', count: 4, icon: '⚙️' },
  { id: 'Tier 2: Core Peripherals', label: 'Tier 2: Peripherals & NVIC', count: 5, icon: '🔌' },
  { id: 'Tier 3: Serial Buses & DMA Engine', label: 'Tier 3: Buses & DMA', count: 4, icon: '⚡' },
  { id: 'Tier 4: Advanced Timers, RTOS & Low-Power', label: 'Tier 4: Timers & RTOS', count: 4, icon: '⏱️' },
  { id: 'Tier 5: Edge AI, USB & Industrial Protocols', label: 'Tier 5: Edge & Protocols', count: 4, icon: '🚀' },
];

const COMPARISON_DATA = [
  {
    feature: 'Core Architecture',
    f401: 'ARM Cortex-M4F (ARMv7E-M) with Hardware FPU (FPv4-SP)',
    f103: 'ARM Cortex-M3 (ARMv7-M) - No FPU (Software Emulation)',
    architecturalImpact: 'Single-cycle DSP instructions and IEEE 754 floating point arithmetic enabled on F401'
  },
  {
    feature: 'Maximum Clock Frequency',
    f401: '84 MHz (Zero-wait state via ART Accelerator)',
    f103: '72 MHz (2-wait states on Flash access above 48 MHz)',
    architecturalImpact: '105 DMIPS (F401) vs 61.25 DMIPS (F103) raw compute throughput'
  },
  {
    feature: 'GPIO Configuration Architecture',
    f401: 'Orthogonal 32-bit registers: MODER (2b/pin), OTYPER (1b/pin), OSPEEDR (2b/pin), PUPDR (2b/pin)',
    f103: 'Paired 32-bit registers: GPIOx_CRL (Pins 0..7, 4b/pin), GPIOx_CRH (Pins 8..15, 4b/pin)',
    architecturalImpact: 'F401 separates pin mode, output type, speed, and pull-up/down into independent orthogonal bits'
  },
  {
    feature: 'Alternate Function Multiplexing',
    f401: 'Dedicated 4-bit per pin selector: GPIOx_AFR[0] (Pins 0..7) & GPIOx_AFR[1] (Pins 8..15) supporting AF0..AF15',
    f103: 'Global AFIO remap register (AFIO_MAPR) with whole-peripheral remap bitfields',
    architecturalImpact: 'F401 allows arbitrary pin re-assignment without blocking neighboring peripheral signals'
  },
  {
    feature: 'DMA Controller Architecture',
    f401: '2 DMA controllers with 8 Streams each, 8 Channels per stream with hardware FIFO and circular buffer burst',
    f103: '2 DMA controllers with 7 fixed Channels (DMA1) and 5 Channels (DMA2) with direct memory transfer',
    architecturalImpact: 'F401 supports flexible cross-trigger routing, stream arbitration, and FIFO threshold packing'
  },
  {
    feature: 'Clock Generation & PLL Formula',
    f401: 'f_VCO = (f_IN / M) * N ; f_SYSCLK = f_VCO / P (Division factor P in {2, 4, 6, 8})',
    f103: 'f_SYSCLK = f_HSE * PLLMUL (Multiplication factor PLLMUL in {2..16})',
    architecturalImpact: 'F401 multi-stage integer divider chain produces separate 48 MHz USB clock and AHB/APB domain clocks'
  },
  {
    feature: 'Bit-Band Memory Operation',
    f401: 'Supported in SRAM (0x22000000) and Peripheral (0x42000000) alias regions',
    f103: 'Supported in SRAM (0x22000000) and Peripheral (0x42000000) alias regions',
    architecturalImpact: 'Atomic single-bit atomic reads and writes without requiring critical sections'
  }
];

export default function Stm32AcademyHub({ modules = [] }) {
  const [activeTier, setActiveTier] = useState('ALL');
  const [selectedBoard, setSelectedBoard] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [showComparator, setShowComparator] = useState(false);
  const [completedModules, setCompletedModules] = useState([]);
  const [notification, setNotification] = useState(null);

  // Load completed modules from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem('voltcore_stm32_completed');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) {
          setCompletedModules(parsed);
        }
      }
    } catch (e) {
      console.warn('Failed to parse completed modules from localStorage', e);
    }
  }, []);

  // Toggle module completion status
  const toggleComplete = (moduleNumber, e) => {
    if (e) e.stopPropagation();
    try {
      let updated;
      const isCompleted = completedModules.includes(moduleNumber);
      if (isCompleted) {
        updated = completedModules.filter(n => n !== moduleNumber);
        setNotification({ text: `Module ${moduleNumber} marked incomplete`, type: 'info' });
      } else {
        updated = [...completedModules, moduleNumber];
        setNotification({ text: `⚡ Module ${moduleNumber} completed! XP awarded.`, type: 'success' });
      }
      setCompletedModules(updated);
      localStorage.setItem('voltcore_stm32_completed', JSON.stringify(updated));

      setTimeout(() => setNotification(null), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  // Filter modules
  const filteredModules = useMemo(() => {
    return modules.filter(m => {
      const data = m.data || m;
      // Tier filter
      if (activeTier !== 'ALL' && data.tier !== activeTier) {
        return false;
      }
      // Board filter
      if (selectedBoard !== 'ALL') {
        const boards = data.boardTargets || [];
        const matches = boards.some(b => b.toLowerCase().includes(selectedBoard.toLowerCase()));
        if (!matches) return false;
      }
      // Search query filter
      if (searchQuery.trim() !== '') {
        const q = searchQuery.toLowerCase();
        const inTitle = (data.title || '').toLowerCase().includes(q);
        const inShortTitle = (data.shortTitle || '').toLowerCase().includes(q);
        const inDesc = (data.description || '').toLowerCase().includes(q);
        const inRegisters = (data.registerFocus || []).some(r => r.toLowerCase().includes(q));
        if (!inTitle && !inShortTitle && !inDesc && !inRegisters) {
          return false;
        }
      }
      return true;
    });
  }, [modules, activeTier, selectedBoard, searchQuery]);

  // Metrics
  const totalXp = useMemo(() => {
    return modules.reduce((sum, m) => {
      const data = m.data || m;
      if (completedModules.includes(data.moduleNumber)) {
        return sum + (data.xpReward || 150);
      }
      return sum;
    }, 0);
  }, [modules, completedModules]);

  const maxPossibleXp = useMemo(() => {
    return modules.reduce((sum, m) => sum + ((m.data || m).xpReward || 150), 0);
  }, [modules]);

  const progressPercent = modules.length > 0
    ? Math.round((completedModules.length / modules.length) * 100)
    : 0;

  // SVG Radial Progress params
  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (progressPercent / 100) * circumference;

  return (
    <div className="space-y-8 font-sans">
      
      {/* Toast Notification */}
      {notification && (
        <div className={`fixed bottom-6 right-6 z-50 px-4 py-3 rounded-xl shadow-2xl border text-sm font-semibold flex items-center gap-2 backdrop-blur-xl animate-bounce ${
          notification.type === 'success'
            ? 'bg-emerald-950/90 border-emerald-500/50 text-emerald-300'
            : 'bg-slate-900/90 border-slate-700 text-slate-300'
        }`}>
          <span>{notification.text}</span>
        </div>
      )}

      {/* Academy Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-950/70 to-slate-950 border border-indigo-500/30 p-6 sm:p-8 shadow-2xl backdrop-blur-xl">
        {/* Hardware-accelerated background circuit pattern */}
        <div className="absolute inset-0 bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:24px_24px] opacity-10 pointer-events-none"></div>

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-3 max-w-3xl">
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold tracking-wider uppercase bg-cyan-500/15 text-cyan-400 border border-cyan-500/30">
                ARM Cortex-M Bare-Metal Curriculum
              </span>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold tracking-wider uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                Universal Modular Engineering
              </span>
              <span className="px-3 py-1 rounded-full text-xs font-mono text-slate-400 border border-slate-700/60">
                21 Comprehensive Modules
              </span>
            </div>

            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              VoltCore STM32 Academy
            </h1>
            <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
              Silicon-to-software mastery of STMicroelectronics 32-bit microcontrollers. Master ARM Cortex-M architecture, vector reset sequences, register-level memory-mapped I/O, peripheral bus timing, DMA engines, and FreeRTOS kernel internals without high-level vendor libraries.
            </p>

            {/* Target Hardware Badges */}
            <div className="flex flex-wrap items-center gap-3 pt-1">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-indigo-500/40 text-xs">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-[0_0_8px_#22d3ee]"></span>
                <span className="text-slate-300">Target 1:</span>
                <strong className="text-cyan-300 font-mono">Nucleo-F401RE</strong>
                <span className="text-slate-400 font-mono text-[11px]">(Cortex-M4F @ 84MHz)</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-indigo-500/40 text-xs">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-400 shadow-[0_0_8px_#60a5fa]"></span>
                <span className="text-slate-300">Target 2:</span>
                <strong className="text-blue-300 font-mono">Blue Pill STM32F103</strong>
                <span className="text-slate-400 font-mono text-[11px]">(Cortex-M3 @ 72MHz)</span>
              </div>
              <button
                onClick={() => setShowComparator(!showComparator)}
                className="px-3 py-1.5 rounded-xl bg-indigo-600/30 hover:bg-indigo-600/50 border border-indigo-500/50 text-indigo-300 text-xs font-semibold transition-all flex items-center gap-1.5 cursor-pointer"
              >
                <span>⚡ {showComparator ? 'Hide Silicon Comparator' : 'Compare F103 vs F401 Architectures'}</span>
              </button>
            </div>
          </div>

          {/* Progress Metric Ring Card */}
          <div className="flex items-center gap-5 p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl backdrop-blur-md self-start lg:self-auto min-w-[260px]">
            <div className="relative w-24 h-24 flex items-center justify-center flex-shrink-0">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="48"
                  cy="48"
                  r={radius}
                  stroke="currentColor"
                  strokeWidth="8"
                  className="text-slate-800"
                  fill="transparent"
                />
                <circle
                  cx="48"
                  cy="48"
                  r={radius}
                  stroke="currentColor"
                  strokeWidth="8"
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeDashoffset}
                  strokeLinecap="round"
                  className="text-cyan-400 transition-all duration-700 ease-out"
                  fill="transparent"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                <span className="text-lg font-black text-white font-mono">{progressPercent}%</span>
                <span className="text-[10px] text-slate-400 font-medium">COMPLETE</span>
              </div>
            </div>

            <div className="space-y-1.5 font-mono">
              <div className="text-xs text-slate-400 uppercase tracking-wider">Academy Progress</div>
              <div className="text-lg font-bold text-white">
                {completedModules.length} <span className="text-xs text-slate-500 font-normal">/ {modules.length} modules</span>
              </div>
              <div className="text-xs text-emerald-400 font-semibold flex items-center gap-1">
                <span>⚡</span> {totalXp.toLocaleString()} / {maxPossibleXp.toLocaleString()} XP
              </div>
            </div>
          </div>
        </div>

        {/* Silicon Architecture Comparator Drawer */}
        {showComparator && (
          <div className="mt-6 pt-6 border-t border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <span>🔬</span> Hardware Comparison: STM32F103 (Blue Pill) vs. STM32F401 (Nucleo-64)
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Universal embedded systems architectural breakdown decoupling core Cortex-M capabilities from peripheral register maps.
                </p>
              </div>
              <button
                onClick={() => setShowComparator(false)}
                className="text-xs text-slate-400 hover:text-white px-2.5 py-1 rounded-lg bg-slate-800"
              >
                Close ✕
              </button>
            </div>

            <div className="overflow-x-auto rounded-xl border border-slate-800">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-950 text-slate-300 font-mono border-b border-slate-800">
                    <th className="p-3 w-1/5 font-semibold">Architectural Feature</th>
                    <th className="p-3 w-2/5 font-semibold text-cyan-400">STM32F401RE (Nucleo-64)</th>
                    <th className="p-3 w-2/5 font-semibold text-blue-400">STM32F103C8 (Blue Pill)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/80 bg-slate-900/60 font-sans">
                  {COMPARISON_DATA.map((row, i) => (
                    <tr key={i} className="hover:bg-slate-800/50 transition-colors">
                      <td className="p-3 font-semibold text-white font-mono text-[11px] align-top">{row.feature}</td>
                      <td className="p-3 text-slate-300 align-top">
                        <div className="font-medium text-slate-200">{row.f401}</div>
                        <div className="text-[11px] text-cyan-400/90 mt-1 font-mono">{row.architecturalImpact}</div>
                      </td>
                      <td className="p-3 text-slate-300 align-top">
                        <div className="font-medium text-slate-200">{row.f103}</div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Curriculum Filtering Controls */}
      <div className="space-y-4">
        {/* Tier Tabs Strip */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          {TIERS.map(tier => {
            const isActive = activeTier === tier.id;
            return (
              <button
                key={tier.id}
                onClick={() => setActiveTier(tier.id)}
                className={`px-4 py-2.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all flex items-center gap-2 cursor-pointer ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-600 to-indigo-600 text-white shadow-lg shadow-indigo-600/30 border border-cyan-400/40'
                    : 'bg-slate-900/80 text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800'
                }`}
              >
                <span>{tier.icon || '📚'}</span>
                <span>{tier.label}</span>
                <span className={`px-1.5 py-0.5 rounded-full text-[10px] font-mono ${
                  isActive ? 'bg-white/20 text-white' : 'bg-slate-800 text-slate-400'
                }`}>
                  {tier.count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Search & Board Filter Bar */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 p-3 rounded-2xl bg-slate-900/90 border border-slate-800">
          {/* Search Input */}
          <div className="relative flex-1">
            <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs">🔍</span>
            <input
              type="text"
              placeholder="Search by topic, peripheral, or register (e.g. MODER, USART, DMA, PLL, SysTick)..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors font-mono"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-white"
              >
                ✕
              </button>
            )}
          </div>

          {/* Board Selector */}
          <div className="flex items-center gap-1.5 text-xs font-mono">
            <span className="text-slate-400 text-[11px] mr-1">Board Filter:</span>
            {[
              { id: 'ALL', label: 'All Targets' },
              { id: 'Nucleo-F401RE', label: 'Nucleo-F401RE' },
              { id: 'Blue Pill', label: 'Blue Pill F103' }
            ].map(b => (
              <button
                key={b.id}
                onClick={() => setSelectedBoard(b.id)}
                className={`px-2.5 py-1.5 rounded-lg transition-colors cursor-pointer ${
                  selectedBoard === b.id
                    ? 'bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/40'
                    : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                {b.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Module Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between text-xs text-slate-400 font-mono px-1">
          <span>Showing {filteredModules.length} of {modules.length} curriculum modules</span>
          <span>Click any module to launch the full bare-metal lecture & register guide</span>
        </div>

        {filteredModules.length === 0 ? (
          <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-slate-800 space-y-3">
            <div className="text-3xl">🔍</div>
            <div className="text-white font-semibold">No curriculum modules matched your search</div>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Try adjusting your search terms or clearing the tier filter to view all 21 STM32 Academy modules.
            </p>
            <button
              onClick={() => { setActiveTier('ALL'); setSelectedBoard('ALL'); setSearchQuery(''); }}
              className="px-4 py-2 rounded-xl bg-indigo-600 text-white text-xs font-semibold cursor-pointer"
            >
              Reset All Filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredModules.map(m => {
              const data = m.data || m;
              const slug = m.slug || `module-${data.moduleNumber}`;
              const isDone = completedModules.includes(data.moduleNumber);

              // Tier Color Coding
              let tierColor = 'border-slate-800 hover:border-cyan-500/50';
              let badgeColor = 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
              if (data.tier.includes('Tier 2')) {
                badgeColor = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
              } else if (data.tier.includes('Tier 3')) {
                badgeColor = 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30';
              } else if (data.tier.includes('Tier 4')) {
                badgeColor = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
              } else if (data.tier.includes('Tier 5')) {
                badgeColor = 'bg-purple-500/10 text-purple-400 border-purple-500/30';
              }

              return (
                <div
                  key={data.moduleNumber}
                  className={`group relative rounded-2xl bg-slate-900/80 border p-5 transition-all duration-300 hover:shadow-2xl hover:shadow-cyan-500/10 flex flex-col justify-between ${
                    isDone ? 'border-emerald-500/40 bg-emerald-950/10' : tierColor
                  }`}
                >
                  <div className="space-y-3.5">
                    {/* Top Row: Module #, Tier, and Completion Toggle */}
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 font-mono font-black text-xs text-white flex items-center justify-center group-hover:border-cyan-400 transition-colors">
                          {String(data.moduleNumber).padStart(2, '0')}
                        </span>
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${badgeColor}`}>
                          {data.tier.split(':')[0]}
                        </span>
                      </div>

                      <button
                        onClick={(e) => toggleComplete(data.moduleNumber, e)}
                        title={isDone ? 'Mark as incomplete' : 'Mark as completed'}
                        className={`px-2.5 py-1 rounded-lg text-xs font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
                          isDone
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                            : 'bg-slate-800 text-slate-400 hover:text-white border border-slate-700'
                        }`}
                      >
                        <span>{isDone ? '✓ Done' : '○ Mark Done'}</span>
                      </button>
                    </div>

                    {/* Title & Short Title */}
                    <div>
                      <a
                        href={`/embedded-systems/stm32-academy/${slug}`}
                        className="text-base font-bold text-white group-hover:text-cyan-300 transition-colors line-clamp-2 block"
                      >
                        {data.title}
                      </a>
                      <p className="text-xs text-slate-400 line-clamp-2 mt-1.5 leading-relaxed">
                        {data.description}
                      </p>
                    </div>

                    {/* Register Focus Tags */}
                    {data.registerFocus && data.registerFocus.length > 0 && (
                      <div className="space-y-1">
                        <span className="text-[10px] text-slate-500 font-mono uppercase tracking-wider block">Registers:</span>
                        <div className="flex flex-wrap gap-1">
                          {data.registerFocus.slice(0, 4).map((reg, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-0.5 rounded-md bg-slate-950 border border-slate-800 text-[10px] font-mono text-cyan-300"
                            >
                              {reg}
                            </span>
                          ))}
                          {data.registerFocus.length > 4 && (
                            <span className="text-[10px] text-slate-500 font-mono self-center">
                              +{data.registerFocus.length - 4}
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Card Footer */}
                  <div className="pt-4 mt-4 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
                    <div className="flex items-center gap-3 text-slate-400 text-[11px]">
                      <span>⏱️ {data.estimatedDuration}</span>
                      <span className="text-emerald-400 font-semibold">⚡ +{data.xpReward} XP</span>
                    </div>

                    <a
                      href={`/embedded-systems/stm32-academy/${slug}`}
                      className="px-3 py-1.5 rounded-lg bg-indigo-600/30 hover:bg-indigo-600 text-indigo-300 hover:text-white border border-indigo-500/40 transition-all font-semibold text-xs flex items-center gap-1"
                    >
                      <span>Read Chapter</span>
                      <span>→</span>
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

    </div>
  );
}
