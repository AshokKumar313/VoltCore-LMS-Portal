import React, { useState, useEffect } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - IoT Smart Laboratory & Equipment Telemetry Hub (Phase 29)
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * Target Facility: Lab 304 (Smart Electronics & IoT Testbed)
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 * ========================================================================================
 */

// Fallback Overview Metrics
const FALLBACK_OVERVIEW = {
  health_score: 87.5,
  lab_status: 'ATTENTION_REQUIRED',
  total_benches: 8,
  online_benches: 6,
  alert_benches: 1,
  standby_benches: 1,
  total_power_watts: 152.07,
  avg_temp_celsius: 36.7,
  active_alerts_count: 2,
  telemetry_samples_logged: 148,
  laboratory: 'MIT Campus - ECE Smart Lab 304',
  regulation: 'ECE Regulation 2023'
};

// Fallback Bench Nodes (8 Workstations in Lab 304)
const FALLBACK_BENCH_NODES = [
  { node_id: 'NODE_ESP32_BENCH_01', bench_id: 'BENCH_304_01', bench_name: 'Bench 01 (RF & Microwave Design)', node_status: 'ONLINE', voltage_v: 12.0, current_a: 1.45, power_w: 17.4, ambient_temp_c: 34.2, relay_state: 'CLOSED', firmware_version: 'v2.4.1-mit-freertos', rssi_dbm: -58 },
  { node_id: 'NODE_ESP32_BENCH_02', bench_id: 'BENCH_304_02', bench_name: 'Bench 02 (Embedded DSP & FPGA)', node_status: 'ONLINE', voltage_v: 5.0, current_a: 2.10, power_w: 10.5, ambient_temp_c: 38.5, relay_state: 'CLOSED', firmware_version: 'v2.4.1-mit-freertos', rssi_dbm: -62 },
  { node_id: 'NODE_ESP32_BENCH_03', bench_id: 'BENCH_304_03', bench_name: 'Bench 03 (Linear ICs & Analog Design)', node_status: 'ONLINE', voltage_v: 15.0, current_a: 0.85, power_w: 12.75, ambient_temp_c: 31.0, relay_state: 'CLOSED', firmware_version: 'v2.4.1-mit-freertos', rssi_dbm: -55 },
  { node_id: 'NODE_ESP32_BENCH_04', bench_id: 'BENCH_304_04', bench_name: 'Bench 04 (Power Electronics & Inverter)', node_status: 'ALERT', voltage_v: 24.2, current_a: 3.42, power_w: 82.76, ambient_temp_c: 68.4, relay_state: 'OPEN', firmware_version: 'v2.4.1-mit-freertos', rssi_dbm: -65 },
  { node_id: 'NODE_ESP32_BENCH_05', bench_id: 'BENCH_304_05', bench_name: 'Bench 05 (IoT Wireless Sensor Testbed)', node_status: 'ONLINE', voltage_v: 3.3, current_a: 0.32, power_w: 1.06, ambient_temp_c: 28.5, relay_state: 'CLOSED', firmware_version: 'v2.4.1-mit-freertos', rssi_dbm: -51 },
  { node_id: 'NODE_ESP32_BENCH_06', bench_id: 'BENCH_304_06', bench_name: 'Bench 06 (VLSI Characterization)', node_status: 'ONLINE', voltage_v: 1.8, current_a: 1.20, power_w: 2.16, ambient_temp_c: 29.8, relay_state: 'CLOSED', firmware_version: 'v2.4.1-mit-freertos', rssi_dbm: -59 },
  { node_id: 'NODE_ESP32_BENCH_07', bench_id: 'BENCH_304_07', bench_name: 'Bench 07 (Automotive CAN/LIN Bus)', node_status: 'ONLINE', voltage_v: 13.8, current_a: 1.80, power_w: 24.84, ambient_temp_c: 36.1, relay_state: 'CLOSED', firmware_version: 'v2.4.1-mit-freertos', rssi_dbm: -60 },
  { node_id: 'NODE_ESP32_BENCH_08', bench_id: 'BENCH_304_08', bench_name: 'Bench 08 (Robotics & Actuators)', node_status: 'STANDBY', voltage_v: 12.0, current_a: 0.05, power_w: 0.60, ambient_temp_c: 27.2, relay_state: 'CLOSED', firmware_version: 'v2.4.1-mit-freertos', rssi_dbm: -64 }
];

// Fallback Threshold Alerts
const FALLBACK_ALERTS = [
  { alert_id: 'ALT_OVERTEMP_304_04', node_id: 'NODE_ESP32_BENCH_04', bench_id: 'BENCH_304_04', alert_type: 'OVER_TEMPERATURE', severity: 'CRITICAL', threshold_val: 65.0, actual_val: 68.4, message: 'Bench 04 heatsink temperature reached 68.4°C (> 65.0°C safety ceiling). Automated relay cutoff tripped.', status: 'ACTIVE', triggered_at: '2026-11-05T12:00:00Z', resolved_at: null },
  { alert_id: 'ALT_OVERCURR_304_04', node_id: 'NODE_ESP32_BENCH_04', bench_id: 'BENCH_304_04', alert_type: 'OVER_CURRENT', severity: 'CRITICAL', threshold_val: 3.0, actual_val: 3.42, message: 'Bench 04 load current 3.42A exceeded 3.00A circuit breaker limit during inverter test.', status: 'ACTIVE', triggered_at: '2026-11-05T12:00:02Z', resolved_at: null }
];

export default function IotTelemetryHub() {
  const [activeTab, setActiveTab] = useState('benches'); // 'benches' | 'history' | 'alerts' | 'injector'
  const [actorRole, setActorRole] = useState('Admin'); // 'Admin' | 'Faculty' | 'Staff' | 'Student'
  
  // Data State
  const [metrics, setMetrics] = useState(FALLBACK_OVERVIEW);
  const [benches, setBenches] = useState(FALLBACK_BENCH_NODES);
  const [alerts, setAlerts] = useState(FALLBACK_ALERTS);
  const [statusMessage, setStatusMessage] = useState('');

  // Packet Injector State
  const [selectedNode, setSelectedNode] = useState('NODE_ESP32_BENCH_01');
  const [injVoltage, setInjVoltage] = useState(12.5);
  const [injCurrent, setInjCurrent] = useState(1.6);
  const [injTemp, setInjTemp] = useState(35.5);
  const [ackNotes, setAckNotes] = useState('');
  const [selectedAlertId, setSelectedAlertId] = useState(null);

  // Load live data
  useEffect(() => {
    fetchMetrics();
    fetchBenches();
    fetchAlerts();
  }, []);

  const fetchMetrics = async () => {
    try {
      const res = await fetch('/api/iot/overview');
      if (res.ok) {
        const data = await res.json();
        setMetrics(data);
      }
    } catch {
      // Offline fallback
    }
  };

  const fetchBenches = async () => {
    try {
      const res = await fetch('/api/iot/nodes');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) setBenches(data);
      }
    } catch {
      // Offline fallback
    }
  };

  const fetchAlerts = async () => {
    try {
      const res = await fetch('/api/iot/alerts');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) setAlerts(data);
      }
    } catch {
      // Offline fallback
    }
  };

  // Toggle Bench Relay (Power ON / CUTOFF)
  const handleToggleRelay = async (benchId, currentState) => {
    const targetState = currentState === 'CLOSED' ? 'OPEN' : 'CLOSED';
    setStatusMessage(`Sending relay command: ${targetState === 'CLOSED' ? 'POWER ON' : 'CUTOFF'} to ${benchId}...`);
    try {
      const res = await fetch('/api/iot/bench/relay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bench_id: benchId,
          target_state: targetState,
          role: actorRole,
          actor_id: '2023MITEC042'
        })
      });
      const data = await res.json();
      if (data.status === 'SUCCESS') {
        setStatusMessage(`✓ Relay updated: ${benchId} is now ${targetState === 'CLOSED' ? 'ENERGIZED (CLOSED)' : 'ISOLATED (OPEN)'}.`);
        setBenches(benches.map(b => b.bench_id === benchId ? { ...b, relay_state: targetState, node_status: targetState === 'CLOSED' ? 'ONLINE' : 'ALERT' } : b));
        fetchMetrics();
      } else {
        setStatusMessage(`⚠️ Action Denied: ${data.message}`);
      }
    } catch (e) {
      setBenches(benches.map(b => b.bench_id === benchId ? { ...b, relay_state: targetState, node_status: targetState === 'CLOSED' ? 'ONLINE' : 'ALERT' } : b));
      setStatusMessage(`✓ Offline Mode: ${benchId} relay toggled to ${targetState}.`);
    }
    setTimeout(() => setStatusMessage(''), 5000);
  };

  // Acknowledge Alert
  const handleAcknowledgeAlert = async (alertId) => {
    try {
      const res = await fetch('/api/iot/alerts/ack', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          alert_id: alertId,
          notes: ackNotes || 'Verified bench load and thermal heatsink by Lab Technician.',
          role: actorRole
        })
      });
      const data = await res.json();
      if (data.status === 'SUCCESS') {
        setAlerts(alerts.map(a => a.alert_id === alertId ? { ...a, status: 'RESOLVED' } : a));
        setSelectedAlertId(null);
        setAckNotes('');
        setStatusMessage(`✓ Alert ${alertId} resolved and logged in audit ledger.`);
        fetchMetrics();
      } else {
        alert(data.message || 'Action denied');
      }
    } catch (e) {
      setAlerts(alerts.map(a => a.alert_id === alertId ? { ...a, status: 'RESOLVED' } : a));
      setSelectedAlertId(null);
      setAckNotes('');
      setStatusMessage(`✓ Offline Mode: Alert ${alertId} marked as RESOLVED.`);
    }
  };

  // Ingest Simulated Telemetry Packet
  const handleInjectPacket = async () => {
    setStatusMessage(`Injecting live telemetry packet from ${selectedNode}...`);
    try {
      const res = await fetch('/api/iot/telemetry/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          node_id: selectedNode,
          voltage_v: parseFloat(injVoltage),
          current_a: parseFloat(injCurrent),
          ambient_temp_c: parseFloat(injTemp)
        })
      });
      const data = await res.json();
      if (data.status === 'SUCCESS') {
        const powerW = Math.round(parseFloat(injVoltage) * parseFloat(injCurrent) * 100) / 100;
        setStatusMessage(`✓ Ingested: P = ${powerW}W (${injVoltage}V * ${injCurrent}A). Alerts Triggered: ${data.alerts_triggered_count}`);
        fetchBenches();
        fetchAlerts();
        fetchMetrics();
      } else {
        setStatusMessage(`⚠️ Ingestion Error: ${data.message}`);
      }
    } catch (e) {
      const powerW = Math.round(parseFloat(injVoltage) * parseFloat(injCurrent) * 100) / 100;
      setBenches(benches.map(b => b.node_id === selectedNode ? {
        ...b,
        voltage_v: parseFloat(injVoltage),
        current_a: parseFloat(injCurrent),
        power_w: powerW,
        ambient_temp_c: parseFloat(injTemp),
        node_status: parseFloat(injTemp) > 65 || parseFloat(injCurrent) > 3.0 ? 'ALERT' : 'ONLINE',
        relay_state: parseFloat(injTemp) > 65 || parseFloat(injCurrent) > 3.0 ? 'OPEN' : 'CLOSED'
      } : b));
      setStatusMessage(`✓ Local Telemetry Simulation: ${selectedNode} updated (${powerW}W).`);
    }
    setTimeout(() => setStatusMessage(''), 5000);
  };

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-8 space-y-8 font-sans">
      {/* Header Banner */}
      <div className="bg-slate-900/90 border border-emerald-500/30 rounded-2xl p-6 shadow-xl backdrop-blur-md relative overflow-hidden">
        <div className="absolute top-0 right-0 -mt-4 -mr-4 w-40 h-40 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 tracking-wide">
                PHASE 29 ENTERPRISE
              </span>
              <span className="text-xs text-slate-400">Lab 304 Smart Electronics &amp; IoT Testbed (MIT Campus)</span>
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
              IoT Smart Laboratory &amp; Telemetry Hub
            </h1>
            <p className="text-sm text-slate-300 mt-1 max-w-2xl">
              Real-time ESP32 workstation node telemetry, voltage/current monitoring, automated thermal overload tripping, remote bench AC/DC relay control, and safety alert ledgers.
            </p>
          </div>

          {/* Role Switcher */}
          <div className="flex items-center gap-3 bg-slate-800/80 p-2.5 rounded-xl border border-slate-700/60 self-start md:self-auto">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Role:</span>
            <div className="flex gap-1.5">
              {['Admin', 'Faculty', 'Staff', 'Student'].map(role => (
                <button
                  key={role}
                  onClick={() => setActorRole(role)}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                    actorRole === role
                      ? 'bg-emerald-500 text-slate-950 shadow-sm font-bold'
                      : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
                  }`}
                >
                  {role}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Global Action Banner */}
        {statusMessage && (
          <div className="mt-4 p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 text-xs font-mono animate-fadeIn flex items-center justify-between">
            <span>{statusMessage}</span>
            <button onClick={() => setStatusMessage('')} className="text-emerald-400 hover:text-white">✕</button>
          </div>
        )}
      </div>

      {/* Metric Scorecards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Lab Status */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 relative overflow-hidden group hover:border-emerald-500/40 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Lab 304 Status</span>
            <span className={`px-2 py-0.5 rounded text-xs font-bold ${
              metrics.lab_status === 'NORMAL' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'
            }`}>
              {metrics.lab_status}
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white tracking-tight">{metrics.health_score}%</span>
            <span className="text-xs text-slate-400">Health Index</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
            <div
              className="bg-emerald-500 h-full rounded-full transition-all duration-700"
              style={{ width: `${metrics.health_score}%` }}
            ></div>
          </div>
        </div>

        {/* Power Consumption */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 relative overflow-hidden group hover:border-cyan-500/40 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Bench Load</span>
            <span className="text-xs font-mono text-cyan-400">8 Workstations</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white tracking-tight">{metrics.total_power_watts} W</span>
            <span className="text-xs text-slate-400">Real-time Draw</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
            <div
              className="bg-cyan-500 h-full rounded-full transition-all duration-700"
              style={{ width: `${Math.min(100, (metrics.total_power_watts / 500) * 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Temperature */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 relative overflow-hidden group hover:border-indigo-500/40 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Ambient Heatsink</span>
            <span className="text-xs font-mono text-indigo-400">Threshold: 65°C</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white tracking-tight">{metrics.avg_temp_celsius} °C</span>
            <span className="text-xs text-slate-400">Safe Operating Range</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
            <div
              className="bg-indigo-500 h-full rounded-full transition-all duration-700"
              style={{ width: `${Math.min(100, (metrics.avg_temp_celsius / 70) * 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Active Threshold Alerts */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 relative overflow-hidden group hover:border-red-500/40 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Safety Trips</span>
            <span className="text-xs font-mono text-red-400">{metrics.active_alerts_count} Active</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white tracking-tight">{metrics.alert_benches}</span>
            <span className="text-xs text-slate-400">Benches Tripped</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
            <div
              className="bg-red-500 h-full rounded-full transition-all duration-700"
              style={{ width: `${Math.min(100, metrics.alert_benches * 25)}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex flex-wrap gap-2 w-full sm:w-auto">
          {[
            { id: 'benches', label: 'Lab 304 Bench Matrix', icon: '⚡' },
            { id: 'alerts', label: 'Safety Threshold Alerts', icon: '🚨' },
            { id: 'injector', label: 'ESP32 Telemetry Simulator', icon: '📡' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
                activeTab === tab.id
                  ? 'bg-emerald-500 text-slate-950 shadow-md font-bold'
                  : 'bg-slate-900/80 text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2 text-2xs text-slate-400 font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>8 ESP32 Nodes Synchronized</span>
        </div>
      </div>

      {/* ==================================================================================== */}
      {/* TAB 1: Lab 304 Bench Matrix */}
      {/* ==================================================================================== */}
      {activeTab === 'benches' && (
        <div className="space-y-6 animate-fadeIn">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {benches.map(b => (
              <div
                key={b.bench_id}
                className={`bg-slate-900/90 border rounded-2xl p-5 flex flex-col justify-between transition-all ${
                  b.node_status === 'ALERT'
                    ? 'border-red-500/40 hover:border-red-500/70'
                    : b.node_status === 'STANDBY'
                    ? 'border-slate-800 hover:border-slate-700'
                    : 'border-slate-800 hover:border-emerald-500/40'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-2xs font-mono font-bold text-slate-400">{b.bench_id}</span>
                    <span className={`px-2 py-0.5 rounded text-2xs font-bold ${
                      b.node_status === 'ONLINE' ? 'bg-emerald-500/20 text-emerald-400' :
                      b.node_status === 'ALERT' ? 'bg-red-500/20 text-red-400 animate-pulse' :
                      'bg-slate-800 text-slate-400'
                    }`}>
                      {b.node_status}
                    </span>
                  </div>

                  <h3 className="text-xs font-bold text-white mb-3 leading-snug">{b.bench_name}</h3>

                  <div className="grid grid-cols-2 gap-2 text-xs font-mono mb-4">
                    <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/80">
                      <span className="text-2xs text-slate-500 block">Voltage:</span>
                      <span className="text-cyan-400 font-bold">{b.voltage_v} V</span>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/80">
                      <span className="text-2xs text-slate-500 block">Current:</span>
                      <span className="text-emerald-400 font-bold">{b.current_a} A</span>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/80">
                      <span className="text-2xs text-slate-500 block">Power:</span>
                      <span className="text-white font-bold">{b.power_w} W</span>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/80">
                      <span className="text-2xs text-slate-500 block">Heatsink:</span>
                      <span className={`font-bold ${b.ambient_temp_c >= 65 ? 'text-red-400' : 'text-slate-300'}`}>
                        {b.ambient_temp_c} °C
                      </span>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className={`w-2 h-2 rounded-full ${b.relay_state === 'CLOSED' ? 'bg-emerald-400' : 'bg-red-500'}`}></span>
                    <span className="text-2xs font-mono text-slate-400">
                      Relay: <strong className={b.relay_state === 'CLOSED' ? 'text-emerald-400' : 'text-red-400'}>{b.relay_state}</strong>
                    </span>
                  </div>

                  <button
                    onClick={() => handleToggleRelay(b.bench_id, b.relay_state)}
                    className={`px-2.5 py-1 rounded text-2xs font-bold transition-all ${
                      b.relay_state === 'CLOSED'
                        ? 'bg-red-600/80 hover:bg-red-500 text-white'
                        : 'bg-emerald-600 hover:bg-emerald-500 text-slate-950'
                    }`}
                  >
                    {b.relay_state === 'CLOSED' ? 'Trip / Cutoff' : 'Reset Relay'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ==================================================================================== */}
      {/* TAB 2: Safety Threshold Alerts Ledger */}
      {/* ==================================================================================== */}
      {activeTab === 'alerts' && (
        <div className="space-y-6 animate-fadeIn">
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6">
            <h3 className="text-base font-bold text-white mb-1">Lab 304 Threshold Safety Alerts</h3>
            <p className="text-xs text-slate-400 mb-4">
              Automated safety trips triggered when workstation voltage exceeds 25V, current exceeds 3A, or heatsink temperature surpasses 65°C.
            </p>

            <div className="space-y-3">
              {alerts.map(alt => (
                <div
                  key={alt.alert_id}
                  className={`p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                    alt.status === 'ACTIVE'
                      ? 'bg-red-950/20 border-red-500/40'
                      : 'bg-slate-950/60 border-slate-800'
                  }`}
                >
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`px-2 py-0.5 rounded text-2xs font-bold ${
                        alt.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-amber-500/20 text-amber-400'
                      }`}>
                        {alt.severity}
                      </span>
                      <span className="font-mono text-2xs text-cyan-400 font-bold">{alt.bench_id}</span>
                      <span className="text-2xs text-slate-500 font-mono">• {alt.alert_type}</span>
                    </div>
                    <div className="text-xs font-semibold text-white">{alt.message}</div>
                    <div className="text-2xs text-slate-400 mt-0.5">
                      Threshold: <strong className="text-slate-300">{alt.threshold_val}</strong> • Measured: <strong className="text-red-400">{alt.actual_val}</strong> • Triggered: {alt.triggered_at}
                    </div>
                  </div>

                  <div className="self-start sm:self-auto flex items-center gap-2">
                    {alt.status === 'ACTIVE' ? (
                      <div>
                        {selectedAlertId === alt.alert_id ? (
                          <div className="flex items-center gap-2">
                            <input
                              type="text"
                              value={ackNotes}
                              onChange={(e) => setAckNotes(e.target.value)}
                              placeholder="Technician resolution note..."
                              className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-2xs text-white"
                            />
                            <button
                              onClick={() => handleAcknowledgeAlert(alt.alert_id)}
                              className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-2xs rounded"
                            >
                              Confirm
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => { setSelectedAlertId(alt.alert_id); setAckNotes(''); }}
                            className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-2xs font-semibold transition-all"
                          >
                            Acknowledge &amp; Clear
                          </button>
                        )}
                      </div>
                    ) : (
                      <span className="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400 text-2xs font-bold">
                        ✓ RESOLVED
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ==================================================================================== */}
      {/* TAB 3: ESP32 Telemetry Simulator & Packet Injector */}
      {/* ==================================================================================== */}
      {activeTab === 'injector' && (
        <div className="space-y-6 animate-fadeIn">
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6">
            <h3 className="text-base font-bold text-white mb-1">Live ESP32 Telemetry Packet Injector</h3>
            <p className="text-xs text-slate-400 mb-4">
              Simulate real-time sensor packets from Lab 304 ESP32 smart bench nodes. Test over-current or over-temperature tripping mechanisms safely.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-4">
              <div>
                <label className="text-2xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Target Node:</label>
                <select
                  value={selectedNode}
                  onChange={(e) => setSelectedNode(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                >
                  {benches.map(b => (
                    <option key={b.node_id} value={b.node_id}>
                      {b.bench_id} ({b.bench_name.split('(')[1]?.replace(')', '') || b.bench_id})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-2xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Voltage (V):</label>
                <input
                  type="number"
                  step="0.1"
                  value={injVoltage}
                  onChange={(e) => setInjVoltage(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="text-2xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Current (A):</label>
                <input
                  type="number"
                  step="0.05"
                  value={injCurrent}
                  onChange={(e) => setInjCurrent(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="text-2xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Temperature (°C):</label>
                <input
                  type="number"
                  step="0.5"
                  value={injTemp}
                  onChange={(e) => setInjTemp(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
            </div>

            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between">
              <div className="text-xs font-mono text-slate-300">
                Calculated Power: <strong className="text-emerald-400">{Math.round(injVoltage * injCurrent * 100) / 100} W</strong> • Trip Check: {injCurrent > 3.0 || injTemp > 65.0 ? <span className="text-red-400 font-bold">⚠️ OVERLOAD WILL TRIP RELAY</span> : <span className="text-emerald-400">NORMAL</span>}
              </div>

              <button
                onClick={handleInjectPacket}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs rounded-xl shadow transition-all"
              >
                Transmit Packet 📡
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

