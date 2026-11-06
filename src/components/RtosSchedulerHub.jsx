import React, { useState, useMemo } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - FreeRTOS Task Scheduler & Context Switch Simulator (Phase 33)
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * Target Facility: Lab 304 (Real-Time Systems & Hardware-in-the-Loop Emulation)
 * Regulation: Anna University ECE Regulation 2023
 * Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * ----------------------------------------------------------------------------------------
 * Architectural Guarantees:
 *  1. Zero Background Polling Loops (Manual Trigger Only)
 *  2. Preemptive & Cooperative FreeRTOS Multitasking Models
 *  3. Bilingual Tooltips (English & Tamil)
 *  4. Hardware Context Switch & Interrupt Latency Benchmarker
 * ========================================================================================
 */

const MCU_OPTIONS = [
  {
    key: 'ESP32_WROOM_32',
    name: 'ESP32-WROOM-32 (240 MHz Xtensa LX6)',
    clockMhz: 240.0,
    csCycles: 84,
    irqCycles: 16,
    fpu: true,
    accent: 'olive',
    colorHex: '#8AB45C'
  },
  {
    key: 'STM32F401RE',
    name: 'STM32F401RE Nucleo (84 MHz Cortex-M4)',
    clockMhz: 84.0,
    csCycles: 64,
    irqCycles: 12,
    fpu: true,
    accent: 'mustard',
    colorHex: '#E5A93C'
  },
  {
    key: 'ARM_CORTEX_M0_PLUS',
    name: 'RP2040 / SAMD21 (48 MHz Cortex-M0+)',
    clockMhz: 48.0,
    csCycles: 96,
    irqCycles: 15,
    fpu: false,
    accent: 'cyan',
    colorHex: '#00D8F6'
  },
  {
    key: 'ATMEGA328P',
    name: 'ATmega328P (16 MHz AVR RISC)',
    clockMhz: 16.0,
    csCycles: 142,
    irqCycles: 4,
    fpu: false,
    accent: 'purple',
    colorHex: '#9D4EDD'
  }
];

const INITIAL_TASKS = [
  {
    id: 'TASK_1',
    name: 'Sensor_Acquisition_ISR',
    tamilName: 'உணரி சமிக்ஞை கையகப்படுத்தல்',
    priority: 3,
    burstMs: 4,
    periodMs: 20,
    state: 'READY',
    color: '#8AB45C', // olive
    badgeClass: 'jewel-badge-olive'
  },
  {
    id: 'TASK_2',
    name: 'TinyML_DSP_Filter',
    tamilName: 'நுண் இயந்திர கற்றல் வடிப்பான்',
    priority: 2,
    burstMs: 8,
    periodMs: 40,
    state: 'READY',
    color: '#E5A93C', // mustard
    badgeClass: 'jewel-badge-mustard'
  },
  {
    id: 'TASK_3',
    name: 'MQTT_Telemetry_Tx',
    tamilName: 'MQTT தொலைத்தொடர்பு வெளியீடு',
    priority: 1,
    burstMs: 12,
    periodMs: 100,
    state: 'READY',
    color: '#00D8F6', // cyan
    badgeClass: 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 px-2 py-0.5 rounded-full text-xs font-semibold'
  },
  {
    id: 'TASK_IDLE',
    name: 'FreeRTOS_Idle_Daemon',
    tamilName: 'செயலற்ற பின்னணி பணி',
    priority: 0,
    burstMs: 50,
    periodMs: 100,
    state: 'READY',
    color: '#475569', // slate
    badgeClass: 'bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded-full text-xs font-semibold'
  }
];

export default function RtosSchedulerHub() {
  const [tasks, setTasks] = useState(INITIAL_TASKS);
  const [schedulerMode, setSchedulerMode] = useState('PREEMPTIVE_PRIORITY'); // 'PREEMPTIVE_PRIORITY' | 'COOPERATIVE'
  const [selectedMcuKey, setSelectedMcuKey] = useState('ESP32_WROOM_32');
  const [simDuration, setSimDuration] = useState(50); // ms
  const [activeTooltip, setActiveTooltip] = useState(null);
  const [simulationResult, setSimulationResult] = useState(null);
  const [benchmarking, setBenchmarking] = useState(false);
  const [exportNotice, setExportNotice] = useState(null);

  const selectedMcu = useMemo(
    () => MCU_OPTIONS.find((m) => m.key === selectedMcuKey) || MCU_OPTIONS[0],
    [selectedMcuKey]
  );

  // Compute Hardware Benchmark Metrics
  const benchmarkMetrics = useMemo(() => {
    const cycleNs = 1000.0 / selectedMcu.clockMhz;
    const csUs = +( (selectedMcu.csCycles * cycleNs) / 1000.0 ).toFixed(4);
    const irqNs = +( selectedMcu.irqCycles * cycleNs ).toFixed(2);
    const maxRateKhz = +( 1000.0 / (csUs + 5.0) ).toFixed(2);

    return {
      clockMhz: selectedMcu.clockMhz,
      csCycles: selectedMcu.csCycles,
      csUs,
      irqNs,
      maxRateKhz
    };
  }, [selectedMcu]);

  // Compute Liu-Layland Schedulability Bound: U <= n*(2^(1/n) - 1)
  const schedulability = useMemo(() => {
    const active = tasks.filter((t) => t.priority > 0 && t.state !== 'SUSPENDED');
    const n = active.length;
    if (n === 0) return { u: 0, bound: 100, schedulable: true };

    const u = active.reduce((acc, t) => acc + (t.burstMs / t.periodMs), 0) * 100.0;
    const bound = n * (Math.pow(2.0, 1.0 / n) - 1.0) * 100.0;

    return {
      u: +u.toFixed(2),
      bound: +bound.toFixed(2),
      schedulable: u <= bound,
      overload: u > 100.0
    };
  }, [tasks]);

  // Toggle task state: READY -> BLOCKED -> SUSPENDED -> READY
  const handleCycleState = (taskId) => {
    setTasks((prev) =>
      prev.map((t) => {
        if (t.id !== taskId || t.id === 'TASK_IDLE') return t;
        const nextState =
          t.state === 'READY' ? 'BLOCKED' : t.state === 'BLOCKED' ? 'SUSPENDED' : 'READY';
        return { ...t, state: nextState };
      })
    );
  };

  // Adjust task priority (0 to 4)
  const handlePriorityChange = (taskId, newPri) => {
    setTasks((prev) =>
      prev.map((t) => {
        if (t.id !== taskId || t.id === 'TASK_IDLE') return t;
        return { ...t, priority: Math.max(1, Math.min(4, newPri)) };
      })
    );
  };

  // Deterministic Client-side simulation matching Python engine logic
  const runClientSimulation = () => {
    const csTimeUs = benchmarkMetrics.csUs;
    const timeline = [];
    const taskRemaining = {};
    const taskNextRelease = {};
    tasks.forEach((t) => {
      taskRemaining[t.id] = 0;
      taskNextRelease[t.id] = 0;
    });

    let contextSwitchCount = 0;
    let currentRunningId = null;

    for (let t = 0; t < simDuration; t++) {
      // Release periodic tasks
      tasks.forEach((task) => {
        if (t >= taskNextRelease[task.id]) {
          taskRemaining[task.id] = task.burstMs;
          taskNextRelease[task.id] = t + task.periodMs;
        }
      });

      // Find eligible READY tasks
      const eligible = tasks.filter(
        (task) => task.state !== 'SUSPENDED' && task.state !== 'BLOCKED' && taskRemaining[task.id] > 0
      );

      let chosen = null;
      if (eligible.length > 0) {
        if (schedulerMode === 'PREEMPTIVE_PRIORITY') {
          eligible.sort((a, b) => b.priority - a.priority);
          chosen = eligible[0];
        } else {
          // Cooperative
          if (currentRunningId && taskRemaining[currentRunningId] > 0) {
            chosen = eligible.find((x) => x.id === currentRunningId) || eligible[0];
          } else {
            eligible.sort((a, b) => b.priority - a.priority);
            chosen = eligible[0];
          }
        }

        if (currentRunningId !== chosen.id) {
          contextSwitchCount += 1;
          currentRunningId = chosen.id;
        }

        taskRemaining[chosen.id] -= 1;
        timeline.push({
          timeMs: t,
          taskId: chosen.id,
          taskName: chosen.name,
          priority: chosen.priority,
          color: chosen.color,
          state: 'RUNNING'
        });
      } else {
        // Idle
        if (currentRunningId !== 'TASK_IDLE') {
          contextSwitchCount += 1;
          currentRunningId = 'TASK_IDLE';
        }
        timeline.push({
          timeMs: t,
          taskId: 'TASK_IDLE',
          taskName: 'FreeRTOS_Idle_Daemon',
          priority: 0,
          color: '#334155',
          state: 'IDLE'
        });
      }
    }

    const totalCsTimeMs = (contextSwitchCount * csTimeUs) / 1000.0;
    const csOverheadPct = +((totalCsTimeMs / simDuration) * 100.0).toFixed(4);

    return {
      status: 'SUCCESS',
      simulationId: `SIM_${Math.random().toString(36).substring(2, 10).toUpperCase()}`,
      metrics: {
        mode: schedulerMode,
        mcuTarget: selectedMcu.name,
        contextSwitchCount,
        contextSwitchOverheadPct: csOverheadPct,
        cpuUtilizationPct: schedulability.u,
        isSchedulable: schedulability.schedulable,
        durationMs: simDuration
      },
      timeline
    };
  };

  // Run Simulation on manual trigger
  const handleRunSimulation = async () => {
    setBenchmarking(true);
    try {
      const res = await fetch('http://127.0.0.1:5000/api/rtos/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tasks: tasks.map((t) => ({
            id: t.id,
            name: t.name,
            priority: t.priority,
            burst_ms: t.burstMs,
            period_ms: t.periodMs,
            state: t.state
          })),
          mode: schedulerMode,
          mcu_target: selectedMcuKey,
          total_duration_ms: simDuration,
          student_id: '2023MITEC042'
        })
      }).catch(() => null);

      if (res && res.ok) {
        const data = await res.json();
        // Harmonize field naming for timeline
        const mappedTimeline = data.timeline.map((item) => {
          const taskObj = tasks.find((x) => x.id === item.task_id);
          return {
            timeMs: item.time_ms,
            taskId: item.task_id,
            taskName: item.task_name,
            priority: item.priority,
            color: taskObj ? taskObj.color : '#334155',
            state: item.state
          };
        });
        setSimulationResult({
          status: 'SUCCESS',
          simulationId: data.simulation_id,
          metrics: {
            mode: data.metrics.mode,
            mcuTarget: selectedMcu.name,
            contextSwitchCount: data.metrics.context_switch_count,
            contextSwitchOverheadPct: data.metrics.context_switch_overhead_pct,
            cpuUtilizationPct: data.metrics.cpu_utilization_pct,
            isSchedulable: data.metrics.is_schedulable,
            durationMs: data.metrics.duration_ms
          },
          timeline: mappedTimeline
        });
      } else {
        // High-fidelity client fallback
        const clientSim = runClientSimulation();
        setSimulationResult(clientSim);
      }
    } finally {
      setBenchmarking(false);
    }
  };

  // Export benchmark CSV
  const handleExportCsv = () => {
    const headers = [
      'mcu_target',
      'architecture_name',
      'clock_mhz',
      'context_switch_cycles',
      'context_switch_us',
      'interrupt_latency_ns',
      'max_task_rate_khz',
      'fpu_enabled',
      'rtos_kernel'
    ];

    const rows = MCU_OPTIONS.map((m) => {
      const cycleNs = 1000.0 / m.clockMhz;
      const csUs = +( (m.csCycles * cycleNs) / 1000.0 ).toFixed(4);
      const irqNs = +( m.irqCycles * cycleNs ).toFixed(2);
      const maxRate = +( 1000.0 / (csUs + 5.0) ).toFixed(2);
      return [
        m.key,
        `"${m.name}"`,
        m.clockMhz,
        m.csCycles,
        csUs,
        irqNs,
        maxRate,
        m.fpu,
        'FreeRTOS'
      ];
    });

    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `voltcore_rtos_benchmarks_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    setExportNotice('Exported MCU Benchmarks to CSV!');
    setTimeout(() => setExportNotice(null), 3500);
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
                Phase 33 FreeRTOS Kernel
              </span>
              <span className="jewel-badge-mustard">
                Zero Background Polling
              </span>
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono bg-slate-900 border border-slate-700 text-slate-300">
                Anna University ECE R2023 • Lab 304
              </span>
            </div>

            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2 font-sans">
              <span>FreeRTOS Task Scheduler & Context Switch Simulator</span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-2xl font-sans">
              Interactive deterministic multi-tasking scheduler modeling preemptive priority queues, cooperative round-robin slicing, and exact hardware interrupt response benchmarks.
            </p>
          </div>

          {/* Quick Metrics Header */}
          <div className="flex flex-wrap items-center gap-3 font-mono text-xs">
            <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-center min-w-[100px]">
              <span className="text-[10px] text-slate-400 block">CPU UTIL (U)</span>
              <span className={`text-base font-bold ${schedulability.schedulable ? 'text-olive-400' : 'text-amber-400'}`}>
                {schedulability.u}%
              </span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-center min-w-[100px]">
              <span className="text-[10px] text-slate-400 block">L-L BOUND</span>
              <span className="text-base font-bold text-slate-200">{schedulability.bound}%</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-center min-w-[100px]">
              <span className="text-[10px] text-slate-400 block">CS LATENCY</span>
              <span className="text-base font-bold text-mustard-300">{benchmarkMetrics.csUs} µs</span>
            </div>
          </div>
        </div>

        {/* Action Controls & Zero-Polling Notice */}
        <div className="mt-5 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs font-mono text-slate-400">
          <div className="flex items-center gap-2">
            <span className="text-olive-400 font-bold">⚡ Zero-Polling Real-Time Guarantee:</span>
            <span>Scheduler simulation runs purely on-demand upon manual trigger. Zero CPU fan spin-up.</span>
          </div>
          {exportNotice && (
            <span className="px-2.5 py-1 rounded-lg bg-olive-500/20 text-olive-300 border border-olive-500/40 font-bold animate-pulse">
              ✓ {exportNotice}
            </span>
          )}
        </div>
      </div>

      {/* 2-Column Deck: Left = Task Configuration; Right = Hardware Benchmarking */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column (7 cols): Task Queue & State Machine */}
        <div className="lg:col-span-7 glass-card-jewel rounded-2xl p-6 border border-slate-800 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
            <div>
              <h3 className="text-base font-bold text-white font-mono flex items-center gap-2">
                <span>FreeRTOS Task Management Deck</span>
                <span className="px-2 py-0.5 rounded text-[10px] bg-slate-900 border border-slate-700 text-slate-400">
                  Priority 0 to 3
                </span>
              </h3>
              <p className="text-xs text-slate-400 font-sans mt-0.5">
                Click task state pill to cycle (READY ➔ BLOCKED ➔ SUSPENDED).
              </p>
            </div>

            {/* Mode Switcher */}
            <div className="flex items-center bg-[#020813] p-1 rounded-xl border border-slate-800 text-xs font-mono">
              <button
                type="button"
                onClick={() => setSchedulerMode('PREEMPTIVE_PRIORITY')}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  schedulerMode === 'PREEMPTIVE_PRIORITY'
                    ? 'bg-olive-600/30 text-olive-300 font-bold border border-olive-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="முந்துரிமை முன்கணிப்பு (Preemptive Multitasking)"
              >
                Preemptive
              </button>
              <button
                type="button"
                onClick={() => setSchedulerMode('COOPERATIVE')}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  schedulerMode === 'COOPERATIVE'
                    ? 'bg-mustard-600/30 text-mustard-300 font-bold border border-mustard-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="கூட்டுறவு திட்டமிடல் (Cooperative Task Slicing)"
              >
                Cooperative
              </button>
            </div>
          </div>

          {/* Tasks List */}
          <div className="space-y-3">
            {tasks.map((task) => (
              <div
                key={task.id}
                onMouseEnter={() => setActiveTooltip(task.id)}
                onMouseLeave={() => setActiveTooltip(null)}
                className="bg-[#020813] border border-slate-800 hover:border-slate-700 rounded-xl p-4 transition-all"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span
                      className="w-3.5 h-3.5 rounded-full flex-shrink-0"
                      style={{ backgroundColor: task.color }}
                    ></span>
                    <div>
                      <div className="text-sm font-bold text-white font-mono flex items-center gap-2">
                        <span>{task.name}</span>
                        <span className="text-[11px] text-slate-400 font-sans font-normal">
                          ({task.tamilName})
                        </span>
                      </div>
                      <div className="text-[11px] font-mono text-slate-400 mt-0.5">
                        Burst: <span className="text-white font-bold">{task.burstMs} ms</span> • Period: <span className="text-white font-bold">{task.periodMs} ms</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 self-end sm:self-auto font-mono text-xs">
                    {/* Priority Selector */}
                    {task.id !== 'TASK_IDLE' && (
                      <div className="flex items-center gap-1 bg-slate-900 px-2 py-1 rounded border border-slate-800">
                        <span className="text-[10px] text-slate-400">Pri:</span>
                        <button
                          type="button"
                          onClick={() => handlePriorityChange(task.id, task.priority - 1)}
                          className="px-1.5 hover:text-olive-300 text-slate-400 font-bold"
                        >
                          -
                        </button>
                        <span className="font-bold text-white">{task.priority}</span>
                        <button
                          type="button"
                          onClick={() => handlePriorityChange(task.id, task.priority + 1)}
                          className="px-1.5 hover:text-olive-300 text-slate-400 font-bold"
                        >
                          +
                        </button>
                      </div>
                    )}

                    {/* State Pill Toggle */}
                    <button
                      type="button"
                      onClick={() => handleCycleState(task.id)}
                      className={`px-3 py-1 rounded-full text-xs font-bold border transition-all ${
                        task.state === 'READY'
                          ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40 hover:bg-emerald-500/30'
                          : task.state === 'BLOCKED'
                          ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 hover:bg-amber-500/30'
                          : 'bg-red-500/20 text-red-300 border-red-500/40 hover:bg-red-500/30'
                      }`}
                      title="நிலைமாற்ற கிளிக் செய்யவும் (Click to toggle state)"
                    >
                      {task.state}
                    </button>
                  </div>
                </div>

                {/* Tooltip Description */}
                {activeTooltip === task.id && (
                  <div className="mt-3 pt-2 border-t border-slate-800/80 text-[11px] font-mono text-slate-300">
                    <span className="text-olive-400 font-bold">FreeRTOS Context: </span>
                    {task.state === 'READY' && 'பணி செயல்படுத்த தயாராக உள்ளது (Ready queue).'}
                    {task.state === 'BLOCKED' && 'செமாஃபோர் அல்லது வரிசைக்காக காத்திருக்கிறது (Blocked on Queue/Semaphore).'}
                    {task.state === 'SUSPENDED' && 'இடைநிறுத்தப்பட்ட நிலை (Suspended via vTaskSuspend).'}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Trigger & Export Bar */}
          <div className="pt-2 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-slate-400">Duration:</span>
              <select
                value={simDuration}
                onChange={(e) => setSimDuration(parseInt(e.target.value, 10))}
                className="bg-[#020813] border border-slate-700 text-slate-200 text-xs font-mono rounded px-2 py-1"
              >
                <option value={30}>30 ms</option>
                <option value={50}>50 ms</option>
                <option value={100}>100 ms</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setTasks(INITIAL_TASKS)}
                className="px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800 text-xs font-mono transition-all"
              >
                ↺ Reset
              </button>

              <button
                type="button"
                onClick={handleRunSimulation}
                disabled={benchmarking}
                className="px-5 py-2 rounded-xl bg-olive-600 hover:bg-olive-500 text-white font-mono text-xs font-bold shadow-olive-glow transition-all flex items-center gap-2 disabled:opacity-50"
              >
                {benchmarking ? (
                  <>
                    <span className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
                    <span>Scheduling...</span>
                  </>
                ) : (
                  <>
                    <span>▶ Run Scheduler Simulation</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right Column (5 cols): Interrupt Latency & Context Switching Benchmarker */}
        <div className="lg:col-span-5 glass-card-mustard rounded-2xl p-6 border border-mustard-500/30 space-y-5 flex flex-col justify-between shadow-xl">
          <div>
            <div className="pb-3 border-b border-slate-800/80">
              <div className="flex items-center justify-between">
                <span className="jewel-badge-mustard">
                  Hardware Benchmarker
                </span>
                <span className="text-[10px] font-mono text-slate-400">
                  Register Stacking & NVIC
                </span>
              </div>
              <h3 className="text-base font-bold text-white font-mono mt-1">
                Context Switch &amp; ISR Latency Widget
              </h3>
              <p className="text-xs text-slate-400 mt-0.5 font-sans">
                Real-world register stacking overhead (T_cs) and tail-chaining latency.
              </p>
            </div>

            {/* Target Microcontroller Selector */}
            <div className="mt-4 space-y-1.5 font-mono text-xs">
              <label className="text-slate-300 font-semibold block">Target MCU Architecture:</label>
              <select
                value={selectedMcuKey}
                onChange={(e) => setSelectedMcuKey(e.target.value)}
                className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3 py-2 text-white font-mono text-xs focus:outline-none focus:border-mustard-400"
              >
                {MCU_OPTIONS.map((mcu) => (
                  <option key={mcu.key} value={mcu.key}>
                    {mcu.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Benchmark Computed Metrics Grid */}
            <div className="mt-4 grid grid-cols-2 gap-3 font-mono text-xs">
              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <span className="text-[10px] text-slate-400 block" title="சூழல் நிலைமாற்ற நேரம்">CS TIME (T_cs)</span>
                <span className="text-base font-bold text-mustard-300">{benchmarkMetrics.csUs} µs</span>
                <span className="text-[10px] text-slate-500 block">{benchmarkMetrics.csCycles} cycles</span>
              </div>

              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <span className="text-[10px] text-slate-400 block" title="குறுக்கீடு பதிலளிப்பு நேரம்">ISR LATENCY</span>
                <span className="text-base font-bold text-cyan-300">{benchmarkMetrics.irqNs} ns</span>
                <span className="text-[10px] text-slate-500 block">{selectedMcu.irqCycles} cycles</span>
              </div>

              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <span className="text-[10px] text-slate-400 block" title="அதிகபட்ச திட்டமிடல் வீதம்">MAX TASK RATE</span>
                <span className="text-base font-bold text-olive-300">{benchmarkMetrics.maxRateKhz} kHz</span>
                <span className="text-[10px] text-slate-500 block">Dispatch limit</span>
              </div>

              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <span className="text-[10px] text-slate-400 block" title="ஹார்டுவேர் மிதவை புள்ளி">FPU HARDWARE</span>
                <span className={`text-base font-bold ${selectedMcu.fpu ? 'text-emerald-400' : 'text-slate-400'}`}>
                  {selectedMcu.fpu ? 'YES (s0-s31)' : 'NO (SoftFP)'}
                </span>
                <span className="text-[10px] text-slate-500 block">Lazy stacking</span>
              </div>
            </div>

            {/* Schedulability Guarantee Badge */}
            <div className="mt-4 p-3 rounded-xl bg-[#020813] border border-slate-800 font-mono text-xs">
              <div className="flex justify-between items-center mb-1">
                <span className="text-slate-400">Liu-Layland Guarantee:</span>
                <span
                  className={`font-bold px-2 py-0.5 rounded text-[10px] ${
                    schedulability.schedulable
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  }`}
                >
                  {schedulability.schedulable ? '✓ SCHEDULABLE' : '⚠ POTENTIAL JITTER'}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-sans">
                {schedulability.schedulable
                  ? `Active CPU load (${schedulability.u}%) is within theoretical bound (${schedulability.bound}%). Zero deadline misses guaranteed.`
                  : `CPU utilization (${schedulability.u}%) exceeds Liu-Layland bound (${schedulability.bound}%). Higher-priority tasks may introduce latency jitter.`}
              </p>
            </div>
          </div>

          {/* Export Action */}
          <button
            type="button"
            onClick={handleExportCsv}
            className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white border border-slate-700 font-mono text-xs font-bold transition-all flex items-center justify-center gap-2"
          >
            <svg className="w-3.5 h-3.5 text-mustard-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" />
            </svg>
            <span>Export MCU Benchmarks CSV</span>
          </button>
        </div>
      </div>

      {/* Gantt Chart Scheduling Timeline (Appears after simulation trigger) */}
      <div className="glass-card-jewel rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div>
            <h3 className="text-base font-bold text-white font-mono flex items-center gap-2">
              <span>FreeRTOS Discrete Timeline (Gantt Chart Slices)</span>
              {simulationResult && (
                <span className="text-xs font-mono text-slate-400">
                  [{simulationResult.metrics.mode}] • {simulationResult.metrics.contextSwitchCount} Context Switches
                </span>
              )}
            </h3>
            <p className="text-xs text-slate-400 font-sans mt-0.5">
              1 millisecond execution slots demonstrating real-time task preemption and idle daemon scheduling.
            </p>
          </div>

          {/* Color Legend */}
          <div className="flex flex-wrap items-center gap-3 font-mono text-[11px]">
            {tasks.map((t) => (
              <div key={t.id} className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded" style={{ backgroundColor: t.color }}></span>
                <span className="text-slate-300">{t.name.split('_')[0]}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Timeline Visualization Grid */}
        {simulationResult ? (
          <div className="space-y-4">
            {/* Visual Gantt Bar */}
            <div className="relative overflow-x-auto pb-2">
              <div className="min-w-[650px] flex h-10 rounded-lg overflow-hidden border border-slate-800 bg-[#020813]">
                {simulationResult.timeline.map((slot, idx) => (
                  <div
                    key={idx}
                    className="flex-1 transition-all hover:opacity-80 relative group cursor-pointer"
                    style={{ backgroundColor: slot.color }}
                  >
                    {/* Tooltip on Hover */}
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none absolute bottom-12 left-1/2 -translate-x-1/2 bg-slate-900 border border-slate-700 p-2 rounded shadow-xl text-[10px] font-mono text-slate-200 z-30 whitespace-nowrap">
                      <div className="font-bold text-white">{slot.taskName}</div>
                      <div>Time: {slot.timeMs} ms • Priority: {slot.priority}</div>
                      <div>State: {slot.state}</div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Time Axis Ticks */}
              <div className="min-w-[650px] flex justify-between text-[10px] font-mono text-slate-500 mt-1 px-1">
                <span>0 ms</span>
                <span>{Math.floor(simDuration * 0.25)} ms</span>
                <span>{Math.floor(simDuration * 0.5)} ms</span>
                <span>{Math.floor(simDuration * 0.75)} ms</span>
                <span>{simDuration} ms</span>
              </div>
            </div>

            {/* Diagnostic Metrics Summary */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs pt-2">
              <div className="bg-[#020813] p-3 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-400 block">Context Switches:</span>
                <span className="text-base font-bold text-white">{simulationResult.metrics.contextSwitchCount}</span>
              </div>
              <div className="bg-[#020813] p-3 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-400 block">Switch Overhead:</span>
                <span className="text-base font-bold text-mustard-300">{simulationResult.metrics.contextSwitchOverheadPct}%</span>
              </div>
              <div className="bg-[#020813] p-3 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-400 block">Simulation ID:</span>
                <span className="text-slate-300 font-mono text-[11px] truncate block">{simulationResult.simulationId}</span>
              </div>
              <div className="bg-[#020813] p-3 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-400 block">Target Kernel:</span>
                <span className="text-olive-300 font-bold">FreeRTOS SMP</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="py-10 text-center space-y-3 font-mono text-xs text-slate-400">
            <div className="w-10 h-10 mx-auto rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-olive-400 text-lg">
              ⏱️
            </div>
            <div>Click <strong>"Run Scheduler Simulation"</strong> to execute multi-tasking timeline dispatch.</div>
          </div>
        )}
      </div>
    </div>
  );
}
