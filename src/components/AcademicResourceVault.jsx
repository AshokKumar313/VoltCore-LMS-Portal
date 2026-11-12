import React, { useState, useMemo } from 'react';

/**
 * ============================================================================
 * VOLTCORE APEX ACADEMIA — ACADEMIC RESOURCE & DRIVE VAULT PANEL
 * ============================================================================
 * Department of Electronics Engineering • MIT Campus • Anna University
 * Regulation 2023 Choice Based Credit System (CBCS)
 * 
 * Curated repository of open-access textbooks, semiconductor manufacturer
 * datasheets, interactive cloud simulations, and student Google Drive folders.
 * Zero private API tokens or credentials exposed.
 * ============================================================================
 */

const RESOURCE_CATEGORIES = [
  { id: 'all', label: 'All Resources' },
  { id: 'textbooks', label: 'Open Textbooks & OCW' },
  { id: 'datasheets', label: 'Semiconductor Datasheets' },
  { id: 'simulators', label: 'Interactive Cloud Labs' },
  { id: 'vault', label: 'Google Drive Vaults' }
];

const VAULT_ITEMS = [
  // 1. Open Textbooks & MIT OCW
  {
    id: 'res-1',
    category: 'textbooks',
    domain: 'Analog & Devices',
    title: 'MIT OpenCourseWare 6.002: Circuits and Electronics',
    author: 'Prof. Anant Agarwal (MIT)',
    description: 'Foundational lumped circuit abstraction, KCL/KVL, MOSFET switches, operational amplifiers, and energy storage elements.',
    url: 'https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/',
    badge: 'MIT OCW',
    badgeColor: '#EF4444'
  },
  {
    id: 'res-2',
    category: 'textbooks',
    domain: 'Signals & Systems',
    title: 'MIT OpenCourseWare 6.011: Signals, Systems and Inference',
    author: 'Prof. Alan V. Oppenheim & Prof. George C. Verghese (MIT)',
    description: 'Linear state-space models, random processes, continuous and discrete Fourier transforms, and optimal Wiener filtering.',
    url: 'https://ocw.mit.edu/courses/6-011-signals-systems-and-inference-spring-2018/',
    badge: 'MIT OCW',
    badgeColor: '#EF4444'
  },
  {
    id: 'res-3',
    category: 'textbooks',
    domain: 'Analog & Devices',
    title: 'All About Circuits: Electric Circuits Volume III (Semiconductors)',
    author: 'Tony R. Kuphaldt',
    description: 'Open-access engineering textbook covering diodes, bipolar junction transistors, JFETs, MOSFETs, and thyristors.',
    url: 'https://www.allaboutcircuits.com/textbook/semiconductors/',
    badge: 'Open Textbook',
    badgeColor: '#10B981'
  },
  {
    id: 'res-4',
    category: 'textbooks',
    domain: 'Digital & VLSI',
    title: 'LibreTexts: Digital Circuit Projects & Logic Systems',
    author: 'Engineering LibreTexts Consortium',
    description: 'Comprehensive digital logic synthesis, Karnaugh maps, binary arithmetic, and HDL finite state machine architecture.',
    url: 'https://eng.libretexts.org/Bookshelves/Electrical_Engineering',
    badge: 'LibreTexts',
    badgeColor: '#38BDF8'
  },

  // 2. Semiconductor Manufacturer Datasheets
  {
    id: 'ds-1',
    category: 'datasheets',
    domain: 'Embedded Systems',
    title: 'STM32F401RE Reference Manual (RM0368)',
    author: 'STMicroelectronics',
    description: 'Complete ARM 32-bit Cortex-M4 with FPU advanced register reference, RCC clock trees, NVIC, DMA, and timers.',
    url: 'https://www.st.com/resource/en/reference_manual/rm0368-stm32f401xbd-and-stm32f401xce-advanced-armbased-32bit-mcus-stmicroelectronics.pdf',
    badge: 'STMicro RM0368',
    badgeColor: '#00F0B5'
  },
  {
    id: 'ds-2',
    category: 'datasheets',
    domain: 'Embedded Systems',
    title: 'ESP32 Technical Reference Manual',
    author: 'Espressif Systems',
    description: 'Xtensa Dual-Core 32-bit LX6 microprocessor hardware architecture, DPORT registers, FreeRTOS dual-core IPC, and Wi-Fi/BT baseband.',
    url: 'https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf',
    badge: 'Espressif Manual',
    badgeColor: '#F59E0B'
  },
  {
    id: 'ds-3',
    category: 'datasheets',
    domain: 'Analog Circuits',
    title: 'TL07x Low-Noise JFET-Input General-Purpose Op-Amp',
    author: 'Texas Instruments',
    description: 'High input impedance, low harmonic distortion (0.003%), high slew rate (13 V/µs), and wide supply range ±18 V.',
    url: 'https://www.ti.com/lit/ds/symlink/tl074.pdf',
    badge: 'TI Datasheet',
    badgeColor: '#EF4444'
  },
  {
    id: 'ds-4',
    category: 'datasheets',
    domain: 'Analog Devices',
    title: '2N2222A NPN Bipolar Silicon Transistor Datasheet',
    author: 'Microchip / Central Semiconductor',
    description: 'High-speed saturation switching and medium power amplifier characteristics with V_CEO = 40V, I_C = 800mA, and f_T = 300MHz.',
    url: 'https://www.onsemi.com/pdf/datasheet/p2n2222a-d.pdf',
    badge: 'Semiconductor Spec',
    badgeColor: '#8B5CF6'
  },

  // 3. Interactive Cloud Labs
  {
    id: 'sim-1',
    category: 'simulators',
    domain: 'Embedded Systems',
    title: 'Wokwi Embedded Systems Simulator: STM32F4 & FreeRTOS',
    author: 'Wokwi Simulator Cloud',
    description: 'Browser-based real-time simulation of ARM Cortex-M and ESP32 with OLED, I2C, SPI sensors, and logic analyzer captures.',
    url: 'https://wokwi.com',
    badge: 'Cloud Simulator',
    badgeColor: '#00F0B5'
  },
  {
    id: 'sim-2',
    category: 'simulators',
    domain: 'Analog Circuits',
    title: 'Falstad Real-Time Electronic Circuit Simulator',
    author: 'Paul Falstad',
    description: 'Interactive animated schematic simulator showing dynamic current flow, op-amp filters, 555 timers, and RLC resonance.',
    url: 'https://www.falstad.com/circuit/',
    badge: 'SPICE Interactive',
    badgeColor: '#10B981'
  },
  {
    id: 'sim-3',
    category: 'simulators',
    domain: 'Digital Logic',
    title: 'CircuitVerse Online Digital Logic Simulator',
    author: 'CircuitVerse Org',
    description: 'Collaborative web-based digital design platform supporting 7400-series ICs, multiplexers, sequential flip-flops, and ROM/RAM.',
    url: 'https://circuitverse.org/simulator',
    badge: 'Logic Workbench',
    badgeColor: '#38BDF8'
  },

  // 4. Google Drive & Institutional Archive Vault
  {
    id: 'drv-1',
    category: 'vault',
    domain: 'Institutional Archive',
    title: 'Anna University ECE Regulation 2023 Official Syllabus Vault',
    author: 'Centre for Academic Courses, Anna University',
    description: 'Curated repository for semester course structures, credit matrices, and laboratory evaluation rubrics.',
    url: 'https://cac.annauniv.edu',
    badge: 'Curriculum Vault',
    badgeColor: '#E5A93C'
  },
  {
    id: 'drv-2',
    category: 'vault',
    domain: 'Lecture Archive',
    title: 'NPTEL & Swayam Open Video Courseware Directory',
    author: 'Ministry of Education & IIT Madras',
    description: 'Centralized indexing for 100+ accredited Indian technical course offerings in Electronics, Communication, and Embedded Systems.',
    url: 'https://nptel.ac.in/courses',
    badge: 'National Portal',
    badgeColor: '#38BDF8'
  },
  {
    id: 'drv-3',
    category: 'vault',
    domain: 'Open Lab Manuals',
    title: 'VoltCore Peer Lab Manuals & Hardware In-The-Loop Archive',
    author: 'MIT Campus Peer Study Circle',
    description: 'Collaborative student lab record templates, LTspice simulation netlists, and STM32 register cheat-sheets.',
    url: '/textbook-library',
    badge: 'Student Vault',
    badgeColor: '#00F0B5'
  }
];

export default function AcademicResourceVault({ embedded = false }) {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredItems = useMemo(() => {
    return VAULT_ITEMS.filter(item => {
      const matchCat = selectedCategory === 'all' || item.category === selectedCategory;
      const q = searchQuery.toLowerCase().trim();
      const matchSearch = !q ||
        item.title.toLowerCase().includes(q) ||
        item.author.toLowerCase().includes(q) ||
        item.description.toLowerCase().includes(q) ||
        item.domain.toLowerCase().includes(q);
      return matchCat && matchSearch;
    });
  }, [selectedCategory, searchQuery]);

  return (
    <div
      className={`rounded-3xl border overflow-hidden font-sans space-y-5 ${
        embedded ? 'p-5' : 'p-6 sm:p-8 shadow-2xl'
      }`}
      style={{
        background: 'var(--theme-surface, rgba(4,16,38,0.92))',
        borderColor: 'var(--theme-border, rgba(0,240,181,0.25))'
      }}
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xl">🗄️</span>
            <h2 className="font-heading font-extrabold text-lg sm:text-xl text-white tracking-tight">
              Academic Resource, Open Textbook &amp; Drive Vault
            </h2>
          </div>
          <p className="text-xs text-slate-400 font-sans mt-0.5">
            Verified open-access textbooks, manufacturer reference manuals, cloud simulators, and institutional archives.
          </p>
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-[11px] font-mono text-emerald-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Zero Private Credentials Exposed</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search textbooks, datasheets (STM32, ESP32, TI), or simulators..."
            className="w-full px-4 py-2 pl-10 rounded-xl bg-[#020813] border border-slate-800 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-400 font-mono"
          />
          <span className="absolute left-3.5 top-2.5 text-slate-500 text-xs">🔍</span>
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-2.5 text-xs text-slate-400 hover:text-white"
            >
              ✕
            </button>
          )}
        </div>

        {/* Category Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto text-xs font-mono pb-1 sm:pb-0">
          {RESOURCE_CATEGORIES.map(cat => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-3 py-1.5 rounded-lg transition-all flex-shrink-0 ${
                selectedCategory === cat.id
                  ? 'bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/40'
                  : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Grid of Vault Items */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredItems.length === 0 ? (
          <div className="col-span-3 p-8 text-center text-slate-500 font-mono text-xs">
            No resources match "{searchQuery}".
          </div>
        ) : (
          filteredItems.map(item => (
            <div
              key={item.id}
              className="p-4 rounded-2xl bg-[#020813]/90 border border-slate-800 hover:border-emerald-400/40 transition-all flex flex-col justify-between space-y-3 group"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <span
                    className="text-[10px] font-mono px-2 py-0.5 rounded font-bold border"
                    style={{
                      backgroundColor: `${item.badgeColor}15`,
                      color: item.badgeColor,
                      borderColor: `${item.badgeColor}40`
                    }}
                  >
                    {item.badge}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">{item.domain}</span>
                </div>

                <h3 className="font-heading font-bold text-sm text-white group-hover:text-emerald-300 transition-colors">
                  {item.title}
                </h3>
                <div className="text-[11px] text-slate-400 font-mono">{item.author}</div>

                <p className="text-xs text-slate-300 font-sans leading-relaxed line-clamp-3">
                  {item.description}
                </p>
              </div>

              <div className="pt-2 border-t border-slate-800/80">
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full py-2 px-3 rounded-xl bg-slate-900 hover:bg-emerald-500/20 text-slate-300 hover:text-emerald-300 border border-slate-700 hover:border-emerald-500/40 font-mono text-xs font-bold transition-all flex items-center justify-center gap-1.5"
                >
                  <span>Access Resource</span>
                  <span className="text-[10px]">&rarr;</span>
                </a>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
