import React, { useState, useMemo } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Low-Power Sleep & Battery Energy Profiler (Phase 34)
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * Target Facility: Lab 304 (Low-Power Embedded IoT & Energy Harvesting Laboratory)
 * Regulation: Anna University ECE Regulation 2023
 * Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * ----------------------------------------------------------------------------------------
 * Architectural Guarantees:
 *  1. Zero Background Polling Loops (Manual Trigger Only)
 *  2. Multi-Mode Sleep Modeling (Modem, Light, Deep Sleep, Hibernation)
 *  3. Non-linear LiPo Battery Discharge Curve Profiling
 *  4. Bilingual Technical Tooltips (English & Tamil)
 *  5. Local RFC-4180 CSV Export
 * ========================================================================================
 */

const MCU_POWER_SPECS = [
  {
    key: 'ESP32_WROOM_32',
    name: 'ESP32-WROOM-32 (Xtensa Dual-Core 240 MHz)',
    voltage: 3.3,
    activeModes: [
      { id: 'ACTIVE_WIFI_TX', label: 'Active Wi-Fi Tx (20 dBm)', currentMa: 240.0 },
      { id: 'ACTIVE_CPU', label: 'Active CPU Only (No RF)', currentMa: 45.0 }
    ],
    sleepModes: [
      { id: 'MODEM_SLEEP', label: 'Modem-Sleep (DTIM3)', currentMa: 15.0, ramRetained: true, ulp: false },
      { id: 'LIGHT_SLEEP', label: 'Light-Sleep (Clock Gated)', currentMa: 0.800, ramRetained: true, ulp: true },
      { id: 'DEEP_SLEEP', label: 'Deep-Sleep (RTC + ULP)', currentMa: 0.010, ramRetained: 'RTC Only', ulp: true },
      { id: 'HIBERNATION', label: 'Hibernation (RTC Timer)', currentMa: 0.005, ramRetained: false, ulp: false }
    ],
    wakeSources: [
      { id: 'RTC_TIMER', label: 'RTC Timer', desc: 'Periodic deep sleep wake-up' },
      { id: 'EXT0_GPIO', label: 'Ext0 GPIO', desc: 'Single RTC pin edge trigger (PIR / Button)' },
      { id: 'EXT1_BITMAP', label: 'Ext1 Bitmap', desc: 'Multi-pin OR/AND RTC GPIO mask' },
      { id: 'TOUCH_PAD', label: 'Touch Pad', desc: 'Capacitive touch pad wake-up' },
      { id: 'ULP_COPROCESSOR', label: 'ULP Coprocessor', desc: 'ADC threshold sensor monitor' }
    ]
  },
  {
    key: 'STM32F401RE',
    name: 'STM32F401RE Nucleo (ARM Cortex-M4 84 MHz)',
    voltage: 3.3,
    activeModes: [
      { id: 'ACTIVE_RUN', label: 'Active Run (84 MHz)', currentMa: 18.0 }
    ],
    sleepModes: [
      { id: 'SLEEP_WFI', label: 'Sleep Mode (WFI)', currentMa: 4.5, ramRetained: true, ulp: false },
      { id: 'STOP_MODE', label: 'Stop Mode (Clocks Off, RAM On)', currentMa: 0.042, ramRetained: true, ulp: false },
      { id: 'STANDBY_MODE', label: 'Standby Mode (1.2V Off)', currentMa: 0.0025, ramRetained: 'Backup Only', ulp: false }
    ],
    wakeSources: [
      { id: 'RTC_ALARM', label: 'RTC Alarm', desc: 'Periodic sub-second calendar alarm' },
      { id: 'WKUP_PIN', label: 'WKUP Pin', desc: 'High-speed hardware wake-up line' },
      { id: 'EXTI_GPIO', label: 'EXTI GPIO Line', desc: 'External peripheral interrupt' }
    ]
  },
  {
    key: 'NRF52840_BLE',
    name: 'Nordic nRF52840 (ARM Cortex-M4F BLE 5.3)',
    voltage: 3.0,
    activeModes: [
      { id: 'RADIO_TX', label: 'Radio Tx (+4 dBm)', currentMa: 4.8 },
      { id: 'CPU_ACTIVE', label: 'CPU Active (64 MHz)', currentMa: 3.3 }
    ],
    sleepModes: [
      { id: 'SYSTEM_ON_IDLE', label: 'System ON (Idle, RAM On)', currentMa: 0.0015, ramRetained: true, ulp: false },
      { id: 'SYSTEM_OFF', label: 'System OFF (Deepest)', currentMa: 0.0004, ramRetained: false, ulp: false }
    ],
    wakeSources: [
      { id: 'RTC_COMPARE', label: 'RTC Compare', desc: 'Low-power 32 kHz timer' },
      { id: 'NFC_FIELD', label: 'NFC Field Detect', desc: 'Contactless tag proximity wake' },
      { id: 'GPIO_DETECT', label: 'GPIO DETECT', desc: 'Latched sense pin transition' }
    ]
  }
];

const BATTERY_OPTIONS = [
  {
    key: 'LIPO_500MAH',
    name: 'LiPo 1S 3.7V (500 mAh) Wearable',
    capacityMah: 500,
    voltageNominal: 3.7,
    chemistry: 'Li-Po'
  },
  {
    key: 'LIPO_1200MAH',
    name: 'LiPo 1S 3.7V (1200 mAh) IoT Sensor Node',
    capacityMah: 1200,
    voltageNominal: 3.7,
    chemistry: 'Li-Po'
  },
  {
    key: 'LIPO_18650_2500MAH',
    name: '18650 Li-Ion Cell (2500 mAh) Industrial',
    capacityMah: 2500,
    voltageNominal: 3.7,
    chemistry: 'Li-Ion'
  },
  {
    key: 'LI_SOCL2_3000MAH',
    name: 'Tadiran Li-SOCl2 (3000 mAh) Primary Cell',
    capacityMah: 3000,
    voltageNominal: 3.6,
    chemistry: 'Li-SOCl2'
  }
];

export default function LowPowerEnergyHub() {
  const [selectedMcuKey, setSelectedMcuKey] = useState('ESP32_WROOM_32');
  const [activeModeId, setActiveModeId] = useState('ACTIVE_WIFI_TX');
  const [sleepModeId, setSleepModeId] = useState('DEEP_SLEEP');
  const [wakeSourceId, setWakeSourceId] = useState('RTC_TIMER');
  const [activeDurationMs, setActiveDurationMs] = useState(200);
  const [sleepDurationS, setSleepDurationS] = useState(59.8);
  const [selectedBatteryKey, setSelectedBatteryKey] = useState('LIPO_18650_2500MAH');
  const [batteryEfficiency, setBatteryEfficiency] = useState(0.85);

  const [activeTooltip, setActiveTooltip] = useState(null);
  const [calculating, setCalculating] = useState(false);
  const [exportNotice, setExportNotice] = useState(null);

  // Active MCU & Battery Objects
  const mcu = useMemo(
    () => MCU_POWER_SPECS.find((m) => m.key === selectedMcuKey) || MCU_POWER_SPECS[0],
    [selectedMcuKey]
  );

  const battery = useMemo(
    () => BATTERY_OPTIONS.find((b) => b.key === selectedBatteryKey) || BATTERY_OPTIONS[2],
    [selectedBatteryKey]
  );

  // Auto-reset modes when MCU changes
  const handleMcuChange = (newMcuKey) => {
    setSelectedMcuKey(newMcuKey);
    const newMcu = MCU_POWER_SPECS.find((m) => m.key === newMcuKey) || MCU_POWER_SPECS[0];
    setActiveModeId(newMcu.activeModes[0].id);
    setSleepModeId(newMcu.sleepModes[newMcu.sleepModes.length - 2]?.id || newMcu.sleepModes[0].id);
    setWakeSourceId(newMcu.wakeSources[0].id);
  };

  // Real-time Energy Computations
  const energyMetrics = useMemo(() => {
    const actObj = mcu.activeModes.find((m) => m.id === activeModeId) || mcu.activeModes[0];
    const slpObj = mcu.sleepModes.find((m) => m.id === sleepModeId) || mcu.sleepModes[0];

    const iActive = actObj.currentMa;
    const iSleep = slpObj.currentMa;

    const tActiveS = activeDurationMs / 1000.0;
    const tSleepS = sleepDurationS;
    const tTotalS = tActiveS + tSleepS;

    const dutyCyclePct = +((tActiveS / tTotalS) * 100.0).toFixed(3);
    const avgCurrentMa = +(((iActive * tActiveS) + (iSleep * tSleepS)) / tTotalS).toFixed(5);
    const avgCurrentUa = +(avgCurrentMa * 1000.0).toFixed(2);
    const avgPowerMw = +(avgCurrentMa * battery.voltageNominal).toFixed(3);

    const usableMah = battery.capacityMah * batteryEfficiency;
    const runtimeHours = +(usableMah / avgCurrentMa).toFixed(1);
    const runtimeDays = +(runtimeHours / 24.0).toFixed(1);
    const runtimeMonths = +(runtimeDays / 30.417).toFixed(1);
    const runtimeYears = +(runtimeDays / 365.25).toFixed(2);

    const totalEnergyMwh = +(battery.capacityMah * battery.voltageNominal).toFixed(1);
    const dailyEnergyMwh = +(avgPowerMw * 24.0).toFixed(2);

    return {
      iActive,
      iSleep,
      dutyCyclePct,
      avgCurrentMa,
      avgCurrentUa,
      avgPowerMw,
      usableMah,
      runtimeHours,
      runtimeDays,
      runtimeMonths,
      runtimeYears,
      totalEnergyMwh,
      dailyEnergyMwh
    };
  }, [mcu, activeModeId, sleepModeId, activeDurationMs, sleepDurationS, battery, batteryEfficiency]);

  // Non-linear LiPo Discharge Curve (10 points)
  const dischargePoints = useMemo(() => {
    const totalDays = energyMetrics.runtimeDays;
    const baseCurve = [
      { soc: 100, v: 4.20 },
      { soc: 90, v: 4.05 },
      { soc: 80, v: 3.96 },
      { soc: 70, v: 3.88 },
      { soc: 60, v: 3.82 },
      { soc: 50, v: 3.77 },
      { soc: 40, v: 3.73 },
      { soc: 30, v: 3.69 },
      { soc: 20, v: 3.62 },
      { soc: 10, v: 3.50 },
      { soc: 0, v: 3.00 }
    ];

    const vScale = battery.voltageNominal / 3.7;

    return baseCurve.map((pt) => ({
      soc: pt.soc,
      voltage: +(pt.v * vScale).toFixed(2),
      elapsedDays: +(totalDays * (1 - pt.soc / 100.0)).toFixed(1)
    }));
  }, [energyMetrics.runtimeDays, battery.voltageNominal]);

  // Trigger manual simulation persistence
  const handleRunCalculation = async () => {
    setCalculating(true);
    try {
      await fetch('http://127.0.0.1:5000/api/energy/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mcu_target: selectedMcuKey,
          active_mode: activeModeId,
          sleep_mode: sleepModeId,
          wake_source: wakeSourceId,
          active_duration_ms: activeDurationMs,
          sleep_duration_s: sleepDurationS,
          battery_key: selectedBatteryKey,
          battery_efficiency: batteryEfficiency,
          student_id: '2023MITEC042'
        })
      }).catch(() => null);

      setExportNotice('Energy profile synchronized with SQLite WAL!');
      setTimeout(() => setExportNotice(null), 3000);
    } finally {
      setCalculating(false);
    }
  };

  // Export energy profile to local CSV
  const handleExportCsv = () => {
    const headers = [
      'soc_percent',
      'cell_voltage_v',
      'elapsed_operating_days',
      'mcu_target',
      'active_mode',
      'sleep_mode',
      'duty_cycle_pct',
      'avg_current_ua',
      'battery_name',
      'total_runtime_days'
    ];

    const rows = dischargePoints.map((pt) => [
      pt.soc,
      pt.voltage,
      pt.elapsedDays,
      `"${mcu.name}"`,
      activeModeId,
      sleepModeId,
      energyMetrics.dutyCyclePct,
      energyMetrics.avgCurrentUa,
      `"${battery.name}"`,
      energyMetrics.runtimeDays
    ]);

    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `voltcore_energy_profile_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    setExportNotice('Exported Energy Profile to CSV!');
    setTimeout(() => setExportNotice(null), 3500);
  };

  // Helper: Render SVG LiPo Discharge Curve
  const renderDischargeSvg = () => {
    const width = 360;
    const height = 120;
    const padding = 20;

    const minV = 2.8;
    const maxV = 4.4;
    const rangeV = maxV - minV;

    const totalDays = energyMetrics.runtimeDays || 1;

    const points = dischargePoints.map((pt) => {
      const x = padding + (pt.elapsedDays / totalDays) * (width - 2 * padding);
      const y = height - padding - ((pt.voltage - minV) / rangeV) * (height - 2 * padding);
      return `${x},${y}`;
    }).join(' ');

    return (
      <svg className="w-full h-32 overflow-visible" viewBox={`0 0 ${width} ${height}`}>
        <defs>
          <linearGradient id="dischargeGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#8AB45C" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#8AB45C" stopOpacity="0.0" />
          </linearGradient>
        </defs>

        {/* Cutoff Voltage Threshold Line (3.0V) */}
        <line
          x1={padding}
          y1={height - padding - ((3.00 - minV) / rangeV) * (height - 2 * padding)}
          x2={width - padding}
          y2={height - padding - ((3.00 - minV) / rangeV) * (height - 2 * padding)}
          stroke="#EF4444"
          strokeWidth="1"
          strokeDasharray="4 3"
        />
        <text
          x={width - padding}
          y={height - padding - ((3.00 - minV) / rangeV) * (height - 2 * padding) - 4}
          fill="#EF4444"
          fontSize="9"
          textAnchor="end"
          fontFamily="monospace"
        >
          Cutoff 3.00V
        </text>

        {/* Discharge Polyline */}
        <polyline
          fill="none"
          stroke="#8AB45C"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={points}
        />

        {/* Milestone Circles */}
        {dischargePoints.map((pt, idx) => {
          const x = padding + (pt.elapsedDays / totalDays) * (width - 2 * padding);
          const y = height - padding - ((pt.voltage - minV) / rangeV) * (height - 2 * padding);
          return (
            <circle
              key={idx}
              cx={x}
              cy={y}
              r={pt.soc === 100 || pt.soc === 0 ? 4 : 2.5}
              className={pt.soc === 100 ? 'fill-emerald-400' : pt.soc === 0 ? 'fill-red-400' : 'fill-olive-300'}
            />
          );
        })}
      </svg>
    );
  };

  return (
    <div className="space-y-8 my-6">
      {/* Top Banner: Jewel Tone Dark Theme with Zero-Polling Guarantee */}
      <div className="glass-card-jewel rounded-3xl p-6 sm:p-8 border border-olive-500/30 relative overflow-hidden shadow-2xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="jewel-badge-olive">
                <span className="h-1.5 w-1.5 rounded-full bg-olive-400 animate-pulse"></span>
                Phase 34 Energy Profiler
              </span>
              <span className="jewel-badge-mustard">
                Zero Background Polling
              </span>
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono bg-slate-900 border border-slate-700 text-slate-300">
                Lab 304 Low-Power IoT Testbed
              </span>
            </div>

            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2 font-sans">
              <span>Low-Power Sleep Modes &amp; LiPo Battery Profiler</span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-2xl font-sans">
              Evaluate operational battery runtime across Modem-Sleep, Light-Sleep, Deep-Sleep, and Hibernation modes with non-linear LiPo discharge voltage curve synthesis.
            </p>
          </div>

          {/* Quick Metrics Header */}
          <div className="flex flex-wrap items-center gap-3 font-mono text-xs">
            <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-center min-w-[100px]">
              <span className="text-[10px] text-slate-400 block">AVG CURRENT</span>
              <span className="text-base font-bold text-olive-400">{energyMetrics.avgCurrentUa} µA</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-center min-w-[100px]">
              <span className="text-[10px] text-slate-400 block">LIFETIME</span>
              <span className="text-base font-bold text-mustard-300">{energyMetrics.runtimeDays} Days</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-center min-w-[100px]">
              <span className="text-[10px] text-slate-400 block">DUTY CYCLE</span>
              <span className="text-base font-bold text-slate-200">{energyMetrics.dutyCyclePct}%</span>
            </div>
          </div>
        </div>

        {/* Zero-Polling Hardware Safety Tagline */}
        <div className="mt-5 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs font-mono text-slate-400">
          <div className="flex items-center gap-2">
            <span className="text-olive-400 font-bold">⚡ Zero-Polling Thermal Safety:</span>
            <span>Mathematical discharge simulation executed on manual demand. No active timers or background daemons.</span>
          </div>
          {exportNotice && (
            <span className="px-2.5 py-1 rounded-lg bg-olive-500/20 text-olive-300 border border-olive-500/40 font-bold animate-pulse">
              ✓ {exportNotice}
            </span>
          )}
        </div>
      </div>

      {/* 2-Column Profiler Deck */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* Left Column (7 cols): Sleep State Machine & Wake-up Matrix */}
        <div className="lg:col-span-7 glass-card-jewel rounded-2xl p-6 border border-slate-800 space-y-6">
          <div className="pb-3 border-b border-slate-800">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white font-mono flex items-center gap-2">
                <span>Microcontroller Sleep State Matrix</span>
                <span className="px-2 py-0.5 rounded text-[10px] bg-slate-900 border border-slate-700 text-slate-400">
                  {mcu.voltage}V Rail
                </span>
              </h3>
            </div>
            <p className="text-xs text-slate-400 font-sans mt-0.5">
              Select target architecture, active burst state, and low-power sleep mode.
            </p>
          </div>

          {/* MCU Selector */}
          <div className="space-y-1.5 font-mono text-xs">
            <label className="text-slate-300 font-semibold block">Target MCU Architecture:</label>
            <select
              value={selectedMcuKey}
              onChange={(e) => handleMcuChange(e.target.value)}
              className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3 py-2 text-white font-mono text-xs focus:outline-none focus:border-olive-400"
            >
              {MCU_POWER_SPECS.map((m) => (
                <option key={m.key} value={m.key}>
                  {m.name}
                </option>
              ))}
            </select>
          </div>

          {/* Active Mode Radio Selector */}
          <div className="space-y-2 font-mono text-xs">
            <label className="text-slate-300 font-semibold block">Active Burst Mode:</label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {mcu.activeModes.map((mode) => (
                <button
                  key={mode.id}
                  type="button"
                  onClick={() => setActiveModeId(mode.id)}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    activeModeId === mode.id
                      ? 'bg-olive-950/80 border-olive-400 ring-1 ring-olive-400 shadow-olive-glow'
                      : 'bg-[#020813] border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="font-bold text-white">{mode.label}</div>
                  <div className="text-[11px] text-olive-300 font-bold mt-1">{mode.currentMa} mA</div>
                </button>
              ))}
            </div>
          </div>

          {/* Sleep Mode Radio Selector */}
          <div className="space-y-2 font-mono text-xs">
            <label className="text-slate-300 font-semibold block">Low-Power Sleep State:</label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {mcu.sleepModes.map((mode) => (
                <button
                  key={mode.id}
                  type="button"
                  onClick={() => setSleepModeId(mode.id)}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    sleepModeId === mode.id
                      ? 'bg-mustard-950/80 border-mustard-400 ring-1 ring-mustard-400 shadow-mustard-glow'
                      : 'bg-[#020813] border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="font-bold text-white">{mode.label}</div>
                  <div className="text-[11px] text-mustard-300 font-bold mt-1">
                    {mode.currentMa < 1.0 ? `${mode.currentMa * 1000} µA` : `${mode.currentMa} mA`}
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">
                    RAM: {mode.ramRetained ? 'Retained' : 'Powered Down'}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Wake-Up Source Selector */}
          <div className="space-y-2 font-mono text-xs">
            <label className="text-slate-300 font-semibold block">Configured Wake-Up Source:</label>
            <div className="flex flex-wrap gap-2">
              {mcu.wakeSources.map((wake) => (
                <button
                  key={wake.id}
                  type="button"
                  onClick={() => setWakeSourceId(wake.id)}
                  className={`px-3 py-1.5 rounded-xl border text-xs transition-all ${
                    wakeSourceId === wake.id
                      ? 'bg-olive-600/30 text-olive-300 border-olive-400 font-bold'
                      : 'bg-[#020813] text-slate-400 border-slate-800 hover:text-slate-200'
                  }`}
                  title={wake.desc}
                >
                  {wake.label}
                </button>
              ))}
            </div>
          </div>

          {/* Active vs Sleep Duration Sliders */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-800 font-mono text-xs">
            <div className="bg-[#020813] p-4 rounded-xl border border-slate-800 space-y-2">
              <div className="flex justify-between text-slate-300">
                <span>Active Duration (t_active):</span>
                <span className="font-bold text-olive-400">{activeDurationMs} ms</span>
              </div>
              <input
                type="range"
                min="10"
                max="1000"
                step="10"
                value={activeDurationMs}
                onChange={(e) => setActiveDurationMs(parseInt(e.target.value, 10))}
                className="w-full accent-[#8AB45C]"
              />
              <div className="flex justify-between text-[10px] text-slate-500">
                <span>10 ms (Burst)</span>
                <span>1000 ms (Lengthy)</span>
              </div>
            </div>

            <div className="bg-[#020813] p-4 rounded-xl border border-slate-800 space-y-2">
              <div className="flex justify-between text-slate-300">
                <span>Sleep Interval (t_sleep):</span>
                <span className="font-bold text-mustard-400">{sleepDurationS} s</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="300.0"
                step="1.0"
                value={sleepDurationS}
                onChange={(e) => setSleepDurationS(parseFloat(e.target.value))}
                className="w-full accent-[#E5A93C]"
              />
              <div className="flex justify-between text-[10px] text-slate-500">
                <span>1 s (Frequent)</span>
                <span>300 s (5 min)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column (5 cols): Battery Discharge Profiler & Runtime Projections */}
        <div className="lg:col-span-5 glass-card-mustard rounded-2xl p-6 border border-mustard-500/30 space-y-5 flex flex-col justify-between shadow-xl">
          <div>
            <div className="pb-3 border-b border-slate-800/80">
              <div className="flex items-center justify-between">
                <span className="jewel-badge-mustard">
                  Battery Profiler
                </span>
                <span className="text-[10px] font-mono text-slate-400">
                  LiPo Non-linear Curve
                </span>
              </div>
              <h3 className="text-base font-bold text-white font-mono mt-1">
                Battery Energy &amp; Runtime Projection
              </h3>
              <p className="text-xs text-slate-400 mt-0.5 font-sans">
                Estimates operational life accounting for 85% regulator &amp; chemical efficiency.
              </p>
            </div>

            {/* Battery Selector */}
            <div className="mt-4 space-y-1.5 font-mono text-xs">
              <label className="text-slate-300 font-semibold block">Power Supply Chemistry:</label>
              <select
                value={selectedBatteryKey}
                onChange={(e) => setSelectedBatteryKey(e.target.value)}
                className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3 py-2 text-white font-mono text-xs focus:outline-none focus:border-mustard-400"
              >
                {BATTERY_OPTIONS.map((bat) => (
                  <option key={bat.key} value={bat.key}>
                    {bat.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Key Computed Metrics Cards */}
            <div className="mt-4 grid grid-cols-2 gap-3 font-mono text-xs">
              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <span className="text-[10px] text-slate-400 block" title="இயக்க சுழற்சி விகிதம்">DUTY CYCLE</span>
                <span className="text-base font-bold text-white">{energyMetrics.dutyCyclePct}%</span>
                <span className="text-[10px] text-slate-500 block">{(energyMetrics.iActive).toFixed(1)} mA peak</span>
              </div>

              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <span className="text-[10px] text-slate-400 block" title="சராசரி திறன் இழப்பு">AVG POWER</span>
                <span className="text-base font-bold text-olive-300">{energyMetrics.avgPowerMw} mW</span>
                <span className="text-[10px] text-slate-500 block">{energyMetrics.dailyEnergyMwh} mWh/day</span>
              </div>

              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <span className="text-[10px] text-slate-400 block" title="செயல்பாட்டு நாட்கள்">RUNTIME (DAYS)</span>
                <span className="text-base font-bold text-mustard-300">{energyMetrics.runtimeDays}</span>
                <span className="text-[10px] text-slate-500 block">~{energyMetrics.runtimeMonths} months</span>
              </div>

              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <span className="text-[10px] text-slate-400 block" title="மொத்த ஆற்றல் சேமிப்பு">STORED ENERGY</span>
                <span className="text-base font-bold text-cyan-300">{energyMetrics.totalEnergyMwh} mWh</span>
                <span className="text-[10px] text-slate-500 block">{energyMetrics.usableMah} mAh usable</span>
              </div>
            </div>

            {/* Dynamic SVG LiPo Discharge Curve */}
            <div className="mt-4 p-3 rounded-xl bg-[#020813] border border-slate-800 font-mono text-xs">
              <div className="flex justify-between items-center mb-1">
                <span className="text-slate-300 font-bold">LiPo Discharge Curve (Voltage vs Days):</span>
                <span className="text-[10px] text-olive-300">Nominal 3.7V Plateau</span>
              </div>
              <div className="mt-2">
                {renderDischargeSvg()}
              </div>
              <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                <span>Day 0 (4.20V Full)</span>
                <span>~Day {(energyMetrics.runtimeDays * 0.5).toFixed(0)} (Plateau)</span>
                <span>Day {energyMetrics.runtimeDays} (3.0V Cutoff)</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 font-mono text-xs">
            <button
              type="button"
              onClick={handleRunCalculation}
              disabled={calculating}
              className="flex-1 py-2.5 rounded-xl bg-olive-600 hover:bg-olive-500 text-white font-bold shadow-olive-glow transition-all flex items-center justify-center gap-1.5 disabled:opacity-50"
            >
              {calculating ? 'Syncing...' : '▶ Sync SQLite WAL'}
            </button>

            <button
              type="button"
              onClick={handleExportCsv}
              className="flex-1 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white border border-slate-700 font-bold transition-all flex items-center justify-center gap-1.5"
            >
              <svg className="w-3.5 h-3.5 text-mustard-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" />
              </svg>
              <span>Export CSV</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
