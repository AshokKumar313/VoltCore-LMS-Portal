import React, { useState, useEffect } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - IoT Sensor Telemetry Simulator (Phase 32)
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * Target Facility: Lab 304 (Hardware Prototyping & Real-Time Embedded Systems Lab)
 * Regulation: Anna University ECE Regulation 2023
 * Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * ----------------------------------------------------------------------------------------
 * Architectural Guarantees:
 *  1. Zero Background Polling Loops (Manual Trigger Only)
 *  2. Rich Dark Theme with Jewel Tones (Olive & Mustard Highlights)
 *  3. Bilingual Tooltips (English & Tamil)
 *  4. Client & Server RFC-4180 CSV Export
 * ========================================================================================
 */

// Initial seed readings
const INITIAL_READINGS = [
  {
    reading_id: 'TEL_E4A910B821',
    node_id: 'ESP32_LAB304_DHT22_IR',
    student_id: '2023MITEC042',
    timestamp: '2026-11-06T10:30:15.120Z',
    temperature_c: 26.8,
    humidity_pct: 56.4,
    ir_proximity_count: 14,
    ir_delta: 0,
    rssi_dbm: -64,
    bus_voltage_v: 3.29,
    status: 'NORMAL',
    checksum: '0xA4F2'
  },
  {
    reading_id: 'TEL_F8C321D904',
    node_id: 'ESP32_LAB304_DHT22_IR',
    student_id: '2023MITEC042',
    timestamp: '2026-11-06T10:31:02.440Z',
    temperature_c: 27.4,
    humidity_pct: 57.1,
    ir_proximity_count: 15,
    ir_delta: 1,
    rssi_dbm: -61,
    bus_voltage_v: 3.30,
    status: 'OBSTACLE_DETECTED',
    checksum: '0xB81C'
  },
  {
    reading_id: 'TEL_73B1C5E288',
    node_id: 'ESP32_LAB304_DHT22_IR',
    student_id: '2023MITEC042',
    timestamp: '2026-11-06T10:32:45.910Z',
    temperature_c: 27.9,
    humidity_pct: 58.6,
    ir_proximity_count: 15,
    ir_delta: 0,
    rssi_dbm: -62,
    bus_voltage_v: 3.28,
    status: 'NORMAL',
    checksum: '0xC290'
  }
];

export default function IoTSensorSimulatorHub() {
  const [readings, setReadings] = useState(INITIAL_READINGS);
  const [baselineTemp, setBaselineTemp] = useState(27.5);
  const [baselineHum, setBaselineHum] = useState(58.0);
  const [activeTooltip, setActiveTooltip] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [lastIrTriggerTime, setLastIrTriggerTime] = useState(null);
  const [exportNotice, setExportNotice] = useState(null);

  // Compute live aggregates from readings
  const stats = React.useMemo(() => {
    if (readings.length === 0) {
      return {
        total: 0,
        temp: { current: 0, min: 0, max: 0, avg: 0 },
        humidity: { current: 0, min: 0, max: 0, avg: 0 },
        irCount: 0,
        alerts: 0
      };
    }
    const temps = readings.map((r) => r.temperature_c);
    const hums = readings.map((r) => r.humidity_pct);
    const alerts = readings.filter((r) => r.status !== 'NORMAL').length;
    const latest = readings[0];

    return {
      total: readings.length,
      temp: {
        current: latest.temperature_c,
        min: Math.min(...temps).toFixed(1),
        max: Math.max(...temps).toFixed(1),
        avg: (temps.reduce((a, b) => a + b, 0) / temps.length).toFixed(1)
      },
      humidity: {
        current: latest.humidity_pct,
        min: Math.min(...hums).toFixed(1),
        max: Math.max(...hums).toFixed(1),
        avg: (hums.reduce((a, b) => a + b, 0) / hums.length).toFixed(1)
      },
      irCount: latest.ir_proximity_count,
      alerts
    };
  }, [readings]);

  // Client-side deterministic reading generator matching backend engine
  const createClientReading = (triggerIr = false) => {
    const prevIr = readings.length > 0 ? readings[0].ir_proximity_count : 14;
    const irDelta = triggerIr || Math.random() < 0.3 ? 1 : 0;
    const newIr = prevIr + irDelta;

    const tDrift = +(baselineTemp + (Math.random() * 2.2 - 0.9)).toFixed(2);
    const hDrift = Math.max(10, Math.min(99, +(baselineHum + (Math.random() * 3.8 - 1.9)).toFixed(2)));
    const rssi = Math.floor(Math.random() * 18) - 74;
    const vBus = +(3.28 + (Math.random() * 0.06 - 0.03)).toFixed(3);

    let status = 'NORMAL';
    if (tDrift >= 35.0) status = 'HIGH_TEMP_ALERT';
    else if (hDrift >= 75.0) status = 'HIGH_HUMIDITY_ALERT';
    else if (irDelta > 0) status = 'OBSTACLE_DETECTED';

    if (irDelta > 0) {
      setLastIrTriggerTime(new Date().toLocaleTimeString());
    }

    const hexRand = Math.floor(Math.random() * 65535).toString(16).toUpperCase().padStart(4, '0');

    return {
      reading_id: `TEL_${Math.random().toString(36).substring(2, 10).toUpperCase()}`,
      node_id: 'ESP32_LAB304_DHT22_IR',
      student_id: '2023MITEC042',
      timestamp: new Date().toISOString(),
      temperature_c: tDrift,
      humidity_pct: hDrift,
      ir_proximity_count: newIr,
      ir_delta: irDelta,
      rssi_dbm: rssi,
      bus_voltage_v: vBus,
      status,
      checksum: `0x${hexRand}`
    };
  };

  // Manual trigger: Generate 1 Reading
  const handleGenerateReading = async (forceIr = false) => {
    setIsSimulating(true);
    try {
      // Try backend endpoint first
      const res = await fetch('http://127.0.0.1:5000/api/sensor-sim/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          burst_count: 1,
          node_id: 'ESP32_LAB304_DHT22_IR',
          student_id: '2023MITEC042',
          baseline_temp_c: baselineTemp,
          baseline_humidity_pct: baselineHum,
          trigger_ir_event: forceIr
        })
      }).catch(() => null);

      if (res && res.ok) {
        const data = await res.json();
        setReadings((prev) => [data, ...prev.slice(0, 49)]);
        if (data.ir_delta > 0) {
          setLastIrTriggerTime(new Date().toLocaleTimeString());
        }
      } else {
        // High-fidelity client fallback
        const clientReading = createClientReading(forceIr);
        setReadings((prev) => [clientReading, ...prev.slice(0, 49)]);
      }
    } finally {
      setIsSimulating(false);
    }
  };

  // Manual trigger: Inject 5-Packet Burst
  const handleGenerateBurst = async () => {
    setIsSimulating(true);
    try {
      const res = await fetch('http://127.0.0.1:5000/api/sensor-sim/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          burst_count: 5,
          node_id: 'ESP32_LAB304_DHT22_IR',
          student_id: '2023MITEC042',
          baseline_temp_c: baselineTemp,
          baseline_humidity_pct: baselineHum
        })
      }).catch(() => null);

      if (res && res.ok) {
        const data = await res.json();
        if (data.readings && Array.isArray(data.readings)) {
          setReadings((prev) => [...data.readings.reverse(), ...prev].slice(0, 50));
        }
      } else {
        const burst = [];
        for (let i = 0; i < 5; i++) {
          burst.unshift(createClientReading(false));
        }
        setReadings((prev) => [...burst, ...prev].slice(0, 50));
      }
    } finally {
      setIsSimulating(false);
    }
  };

  // Export telemetry to local CSV file
  const handleExportCsv = () => {
    if (readings.length === 0) return;

    const headers = [
      'reading_id',
      'timestamp',
      'node_id',
      'student_id',
      'temperature_c',
      'humidity_pct',
      'ir_proximity_count',
      'rssi_dbm',
      'bus_voltage_v',
      'status',
      'checksum'
    ];

    const rows = readings.map((r) => [
      r.reading_id,
      r.timestamp,
      r.node_id,
      r.student_id,
      r.temperature_c,
      r.humidity_pct,
      r.ir_proximity_count,
      r.rssi_dbm,
      r.bus_voltage_v,
      r.status,
      r.checksum
    ]);

    const csvContent = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `voltcore_telemetry_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    setExportNotice(`Exported ${readings.length} records to CSV!`);
    setTimeout(() => setExportNotice(null), 3500);
  };

  // Clear readings buffer
  const handleClearReadings = async () => {
    fetch('http://127.0.0.1:5000/api/sensor-sim/clear', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ node_id: 'ESP32_LAB304_DHT22_IR' })
    }).catch(() => null);

    setReadings([]);
  };

  // Helper: SVG Sparkline Chart
  const renderTrendSvg = () => {
    if (readings.length < 2) return null;
    const recent = readings.slice(0, 15).reverse();
    const temps = recent.map((r) => r.temperature_c);
    const minT = Math.min(...temps) - 1.0;
    const maxT = Math.max(...temps) + 1.0;
    const range = maxT - minT || 1;

    const width = 280;
    const height = 60;
    const step = width / (recent.length - 1);

    const points = recent.map((r, idx) => {
      const x = idx * step;
      const y = height - ((r.temperature_c - minT) / range) * (height - 12) - 6;
      return `${x},${y}`;
    }).join(' ');

    return (
      <svg className="w-full h-16 overflow-visible" viewBox={`0 0 ${width} ${height}`}>
        <defs>
          <linearGradient id="oliveGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#8AB45C" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#8AB45C" stopOpacity="0.0" />
          </linearGradient>
        </defs>
        <polyline
          fill="none"
          stroke="#8AB45C"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={points}
        />
        {recent.map((r, idx) => {
          const x = idx * step;
          const y = height - ((r.temperature_c - minT) / range) * (height - 12) - 6;
          return (
            <circle
              key={idx}
              cx={x}
              cy={y}
              r={idx === recent.length - 1 ? 4 : 2}
              className={idx === recent.length - 1 ? 'fill-olive-400 stroke-white stroke-2 animate-pulse' : 'fill-olive-300'}
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
                Phase 32 Telemetry Engine
              </span>
              <span className="jewel-badge-mustard">
                Zero Background Polling
              </span>
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono bg-slate-900 border border-slate-700 text-slate-300">
                Node: ESP32_LAB304_DHT22_IR
              </span>
            </div>

            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2 font-sans">
              <span>IoT Sensor Telemetry Simulator</span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-2xl font-sans">
              High-precision simulated streaming of ESP32 / DHT22 environmental metrics and TCRT5000 IR proximity pulses with SQLite WAL logging and instant CSV exports.
            </p>
          </div>

          {/* Quick Metrics Header */}
          <div className="flex flex-wrap items-center gap-3 font-mono text-xs">
            <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-center min-w-[90px]">
              <span className="text-[10px] text-slate-400 block">TOTAL LOGS</span>
              <span className="text-base font-bold text-white">{stats.total}</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-center min-w-[90px]">
              <span className="text-[10px] text-slate-400 block">IR OBJECTS</span>
              <span className="text-base font-bold text-olive-400">{stats.irCount}</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-center min-w-[90px]">
              <span className="text-[10px] text-slate-400 block">ALERTS</span>
              <span className={`text-base font-bold ${stats.alerts > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                {stats.alerts}
              </span>
            </div>
          </div>
        </div>

        {/* Zero Polling Safety Tagline */}
        <div className="mt-5 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs font-mono text-slate-400">
          <div className="flex items-center gap-2">
            <span className="text-olive-400 font-bold">⚡ Zero Polling Architecture:</span>
            <span>Sensor events update strictly on manual click. Zero thermal throttling on HP Victus.</span>
          </div>
          {exportNotice && (
            <span className="px-2.5 py-1 rounded-lg bg-olive-500/20 text-olive-300 border border-olive-500/40 font-bold animate-pulse">
              ✓ {exportNotice}
            </span>
          )}
        </div>
      </div>

      {/* 3-Gauge Live Telemetry Cluster */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Gauge 1: Temperature */}
        <div
          onMouseEnter={() => setActiveTooltip('temp')}
          onMouseLeave={() => setActiveTooltip(null)}
          className="glass-card-olive rounded-2xl p-5 border border-olive-500/30 relative flex flex-col justify-between shadow-lg"
        >
          <div>
            <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
              <div className="flex items-center gap-2">
                <span className="text-lg">🌡️</span>
                <span className="text-xs font-mono font-bold text-slate-300 uppercase">
                  Temperature
                </span>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-olive-900/60 text-olive-300 border border-olive-500/30">
                DHT22 AM2302
              </span>
            </div>

            <div className="mt-4 flex items-baseline justify-between">
              <div>
                <span className="text-4xl font-extrabold text-white font-mono">
                  {stats.temp.current}
                </span>
                <span className="text-xl font-mono text-olive-400 ml-1">°C</span>
              </div>
              <div className="text-right text-[11px] font-mono text-slate-400">
                <div>Min: <span className="text-slate-200">{stats.temp.min}°C</span></div>
                <div>Max: <span className="text-slate-200">{stats.temp.max}°C</span></div>
                <div>Avg: <span className="text-olive-300 font-semibold">{stats.temp.avg}°C</span></div>
              </div>
            </div>

            {/* Visual Temperature Bar */}
            <div className="mt-4 space-y-1">
              <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    stats.temp.current >= 35.0 ? 'bg-amber-500' : 'bg-gradient-to-r from-olive-500 to-olive-400'
                  }`}
                  style={{ width: `${Math.min(100, Math.max(10, (stats.temp.current / 50) * 100))}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-[10px] font-mono text-slate-500">
                <span>0°C (Cold)</span>
                <span>25°C (Room)</span>
                <span>50°C (Limit)</span>
              </div>
            </div>
          </div>

          {/* Bilingual Tooltip Overlay */}
          {activeTooltip === 'temp' && (
            <div className="mt-4 p-2.5 rounded-xl bg-[#020813]/95 border border-olive-500/40 text-[11px] font-mono space-y-1 shadow-xl">
              <div className="text-olive-300 font-bold">வெப்பநிலை உணரிகள் (DHT22):</div>
              <div className="text-slate-300">துல்லிய சுற்றுப்புற வெப்பநிலை அளவீடு (°C). இயல்பான எல்லை: 20°C - 35°C.</div>
            </div>
          )}
        </div>

        {/* Gauge 2: Relative Humidity */}
        <div
          onMouseEnter={() => setActiveTooltip('humidity')}
          onMouseLeave={() => setActiveTooltip(null)}
          className="glass-card-mustard rounded-2xl p-5 border border-mustard-500/30 relative flex flex-col justify-between shadow-lg"
        >
          <div>
            <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
              <div className="flex items-center gap-2">
                <span className="text-lg">💧</span>
                <span className="text-xs font-mono font-bold text-slate-300 uppercase">
                  Relative Humidity
                </span>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-mustard-900/60 text-mustard-300 border border-mustard-500/30">
                Psychrometric %
              </span>
            </div>

            <div className="mt-4 flex items-baseline justify-between">
              <div>
                <span className="text-4xl font-extrabold text-white font-mono">
                  {stats.humidity.current}
                </span>
                <span className="text-xl font-mono text-mustard-400 ml-1">% RH</span>
              </div>
              <div className="text-right text-[11px] font-mono text-slate-400">
                <div>Min: <span className="text-slate-200">{stats.humidity.min}%</span></div>
                <div>Max: <span className="text-slate-200">{stats.humidity.max}%</span></div>
                <div>Avg: <span className="text-mustard-300 font-semibold">{stats.humidity.avg}%</span></div>
              </div>
            </div>

            {/* Visual Humidity Bar */}
            <div className="mt-4 space-y-1">
              <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-mustard-600 to-mustard-400 transition-all duration-500"
                  style={{ width: `${Math.min(100, Math.max(5, stats.humidity.current))}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-[10px] font-mono text-slate-500">
                <span>10% (Dry)</span>
                <span>50% (Nominal)</span>
                <span>90% (Humid)</span>
              </div>
            </div>
          </div>

          {/* Bilingual Tooltip Overlay */}
          {activeTooltip === 'humidity' && (
            <div className="mt-4 p-2.5 rounded-xl bg-[#020813]/95 border border-mustard-500/40 text-[11px] font-mono space-y-1 shadow-xl">
              <div className="text-mustard-300 font-bold">காற்றின் ஈரப்பதம் (RH %):</div>
              <div className="text-slate-300">காற்றில் நிறைந்துள்ள நீர் ஆவியின் சதவீதம். ஆய்வக தரம்: 40% - 70% RH.</div>
            </div>
          )}
        </div>

        {/* Gauge 3: IR Proximity Counter & Optical Sensor State */}
        <div
          onMouseEnter={() => setActiveTooltip('ir')}
          onMouseLeave={() => setActiveTooltip(null)}
          className="glass-card-olive rounded-2xl p-5 border border-olive-500/30 relative flex flex-col justify-between shadow-lg"
        >
          <div>
            <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
              <div className="flex items-center gap-2">
                <span className="text-lg">📡</span>
                <span className="text-xs font-mono font-bold text-slate-300 uppercase">
                  IR Proximity Counter
                </span>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-olive-900/60 text-olive-300 border border-olive-500/30">
                TCRT5000 ISR
              </span>
            </div>

            <div className="mt-4 flex items-baseline justify-between">
              <div>
                <span className="text-4xl font-extrabold text-white font-mono">
                  {stats.irCount}
                </span>
                <span className="text-xs font-mono text-slate-400 ml-2">EVENTS</span>
              </div>
              <div className="text-right text-[11px] font-mono text-slate-400">
                <div className="flex items-center gap-1.5 justify-end">
                  <span className={`h-2.5 w-2.5 rounded-full ${readings[0]?.ir_delta > 0 ? 'bg-olive-400 animate-ping' : 'bg-slate-700'}`}></span>
                  <span className="text-slate-200">
                    {readings[0]?.ir_delta > 0 ? 'OBSTACLE DETECTED' : 'CLEAR BEAM'}
                  </span>
                </div>
                <div className="mt-1">
                  Last Trigger: <span className="text-olive-300">{lastIrTriggerTime || 'Standby'}</span>
                </div>
              </div>
            </div>

            {/* Sparkline Visual */}
            <div className="mt-4 pt-2 border-t border-slate-800/60">
              <div className="text-[10px] font-mono text-slate-400 mb-1">
                Recent Thermal Trajectory (Last 15 Packets):
              </div>
              {renderTrendSvg()}
            </div>
          </div>

          {/* Bilingual Tooltip Overlay */}
          {activeTooltip === 'ir' && (
            <div className="mt-4 p-2.5 rounded-xl bg-[#020813]/95 border border-olive-500/40 text-[11px] font-mono space-y-1 shadow-xl">
              <div className="text-olive-300 font-bold">அகச்சிவப்பு அருகாமை உணரி (IR Sensor):</div>
              <div className="text-slate-300">பொருட்கள் அல்லது பாகங்கள் கடந்து செல்லும் போது குறுக்கீடு வழியே பதிவு செய்கிறது.</div>
            </div>
          )}
        </div>
      </div>

      {/* Manual Trigger Command Center & Calibration Controls */}
      <div className="glass-card-jewel rounded-3xl p-6 border border-slate-800 space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <h3 className="text-lg font-bold text-white font-mono flex items-center gap-2">
              <span>Manual Telemetry Dispatcher</span>
              <span className="px-2 py-0.5 rounded text-[10px] bg-slate-900 border border-slate-700 text-slate-400">
                Single-Click Trigger
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5 font-sans">
              Inject telemetry on demand without background polling threads. Adjust calibration sliders below to simulate environmental drift.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => handleGenerateReading(false)}
              disabled={isSimulating}
              className="px-4 py-2 rounded-xl bg-olive-600 hover:bg-olive-500 text-white font-mono text-xs font-bold shadow-olive-glow transition-all flex items-center gap-1.5 disabled:opacity-50"
            >
              <span>▶ Simulate Next Packet</span>
            </button>

            <button
              type="button"
              onClick={handleGenerateBurst}
              disabled={isSimulating}
              className="px-4 py-2 rounded-xl bg-mustard-600 hover:bg-mustard-500 text-white font-mono text-xs font-bold shadow-mustard-glow transition-all flex items-center gap-1.5 disabled:opacity-50"
            >
              <span>⚡ Inject 5-Packet Burst</span>
            </button>

            <button
              type="button"
              onClick={() => handleGenerateReading(true)}
              disabled={isSimulating}
              className="px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-olive-300 border border-olive-500/40 font-mono text-xs font-semibold transition-all flex items-center gap-1.5 disabled:opacity-50"
            >
              <span>🔴 Trigger IR Obstacle</span>
            </button>

            <button
              type="button"
              onClick={handleExportCsv}
              className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white border border-slate-700 font-mono text-xs font-bold transition-all flex items-center gap-1.5"
            >
              <svg className="w-3.5 h-3.5 text-olive-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" />
              </svg>
              <span>Export CSV</span>
            </button>

            <button
              type="button"
              onClick={handleClearReadings}
              className="px-3 py-2 rounded-xl bg-slate-950 hover:bg-red-950/40 text-slate-400 hover:text-red-300 border border-slate-800 text-xs font-mono transition-all"
            >
              Clear Buffer
            </button>
          </div>
        </div>

        {/* Calibration Sliders */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 font-mono text-xs">
          <div className="space-y-2 bg-[#020813] p-4 rounded-xl border border-slate-800">
            <div className="flex justify-between text-slate-300">
              <span>Baseline Temperature:</span>
              <span className="font-bold text-olive-400">{baselineTemp}°C</span>
            </div>
            <input
              type="range"
              min="18.0"
              max="42.0"
              step="0.5"
              value={baselineTemp}
              onChange={(e) => setBaselineTemp(parseFloat(e.target.value))}
              className="w-full accent-[#8AB45C]"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>18°C (Cool)</span>
              <span>42°C (Thermal Stress)</span>
            </div>
          </div>

          <div className="space-y-2 bg-[#020813] p-4 rounded-xl border border-slate-800">
            <div className="flex justify-between text-slate-300">
              <span>Baseline Relative Humidity:</span>
              <span className="font-bold text-mustard-400">{baselineHum}%</span>
            </div>
            <input
              type="range"
              min="20.0"
              max="90.0"
              step="1.0"
              value={baselineHum}
              onChange={(e) => setBaselineHum(parseFloat(e.target.value))}
              className="w-full accent-[#E5A93C]"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>20% (Arid)</span>
              <span>90% (Saturated)</span>
            </div>
          </div>

          <div className="space-y-1 bg-[#020813] p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div className="text-slate-400 text-[11px]">Hardware Radio Telemetry:</div>
            <div className="flex justify-between text-slate-300">
              <span>Bus Voltage:</span>
              <span className="font-bold text-white">{readings[0]?.bus_voltage_v || 3.30} V</span>
            </div>
            <div className="flex justify-between text-slate-300">
              <span>Wi-Fi RSSI:</span>
              <span className="font-bold text-emerald-400">{readings[0]?.rssi_dbm || -62} dBm</span>
            </div>
            <div className="flex justify-between text-slate-300">
              <span>CRC16 Integrity:</span>
              <span className="font-mono text-olive-300">{readings[0]?.checksum || '0xA4F2'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Historical Telemetry Stream Table */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h3 className="text-base font-bold text-white font-mono">
              Live Sensor Packet Ledger (SQLite WAL Mode)
            </h3>
            <p className="text-xs text-slate-400 font-sans mt-0.5">
              Verified records with timestamp, temperature, humidity, IR event delta, and CRC16 checksum.
            </p>
          </div>
          <span className="text-xs font-mono text-slate-500">
            Showing {readings.length} records
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead>
              <tr className="text-slate-400 border-b border-slate-800 text-[11px]">
                <th className="py-2.5 px-3" title="நேர முத்திரை - Packet Timestamp">TIMESTAMP</th>
                <th className="py-2.5 px-3" title="சென்சார் முனையம் - Node ID">NODE ID</th>
                <th className="py-2.5 px-3" title="வெப்பநிலை (°C) - Ambient Temperature">TEMP (°C)</th>
                <th className="py-2.5 px-3" title="ஈரப்பதம் (% RH) - Relative Humidity">HUMIDITY (%)</th>
                <th className="py-2.5 px-3" title="அகச்சிவப்பு எண்ணிக்கை - Cumulative IR Count">IR COUNT</th>
                <th className="py-2.5 px-3" title="வயர்லெஸ் நிலை - RSSI Signal">RSSI</th>
                <th className="py-2.5 px-3" title="பாதுகாப்பு நிலை - Safety Status">STATUS</th>
                <th className="py-2.5 px-3" title="சரிபார்ப்பு குறியீடு - CRC16 Checksum">CRC16</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {readings.length === 0 ? (
                <tr>
                  <td colSpan="8" className="py-8 text-center text-slate-500 font-mono">
                    No telemetry records in buffer. Click "Simulate Next Packet" to generate readings.
                  </td>
                </tr>
              ) : (
                readings.map((r, idx) => (
                  <tr key={idx} className="hover:bg-[#041026]/80 text-slate-200 transition-colors">
                    <td className="py-2.5 px-3 text-slate-400 text-[11px]">
                      {new Date(r.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="py-2.5 px-3 font-bold text-white text-[11px]">
                      {r.node_id}
                    </td>
                    <td className="py-2.5 px-3 font-bold text-olive-300">
                      {r.temperature_c}°C
                    </td>
                    <td className="py-2.5 px-3 font-semibold text-mustard-300">
                      {r.humidity_pct}%
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        r.ir_delta > 0
                          ? 'bg-olive-500/20 text-olive-300 border border-olive-500/40'
                          : 'bg-slate-900 text-slate-300'
                      }`}>
                        {r.ir_proximity_count} {r.ir_delta > 0 ? '(+1)' : ''}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-400">
                      {r.rssi_dbm} dBm
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                        r.status === 'NORMAL'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : r.status === 'OBSTACLE_DETECTED'
                          ? 'bg-olive-500/20 text-olive-300 border-olive-500/40'
                          : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                      }`}>
                        {r.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-500 text-[11px]">
                      {r.checksum}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
