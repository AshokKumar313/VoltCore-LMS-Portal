import React, { useState, useEffect, useRef } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Real-Time Server-Sent Events (SSE) Live Telemetry Stream
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Component: src/components/LiveTelemetryStream.jsx
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 * Aesthetic: German Precision Engineering + Italian Glassmorphism (#020813 to #00693E)
 * ========================================================================================
 */

const SAMPLE_EVENTS = [
  {
    id: 'evt-init-1',
    event_type: 'attendance_scan',
    timestamp: new Date(Date.now() - 12000).toISOString(),
    data: {
      node_id: 'ESP32_MIT_IOT_LAB_01',
      student_id: '2023MITEC042',
      student_name: 'Ashok Kumar A',
      rfid_uid: 'E2 80 6F 3B',
      status: 'Lab-Verified',
      rssi: -56,
      campus: 'MIT Campus, Anna University'
    }
  },
  {
    id: 'evt-init-2',
    event_type: 'xp_gain',
    timestamp: new Date(Date.now() - 9500).toISOString(),
    data: {
      student_id: '2023MITEC042',
      student_name: 'Ashok Kumar A',
      xp_amount: 50,
      reason: 'Hardware RFID Laboratory Entry Verified',
      multiplier: '2.5x'
    }
  },
  {
    id: 'evt-init-3',
    event_type: 'fleet_heartbeat',
    timestamp: new Date(Date.now() - 6000).toISOString(),
    data: {
      node_id: 'ESP32_MIT_EMBEDDED_LAB_02',
      status: 'ACTIVE_ONLINE',
      rssi: -58,
      spool_depth: 0,
      ip_address: '10.0.4.19'
    }
  },
  {
    id: 'evt-init-4',
    event_type: 'tinyml_anomaly',
    timestamp: new Date(Date.now() - 2500).toISOString(),
    data: {
      node_id: 'ESP32_MIT_EDGE_NODE_09',
      anomaly_type: 'BEARING_INNER_RACE_FATIGUE',
      confidence_pct: 94.2,
      vibration_rms_g: 4.88,
      temperature_celsius: 69.4,
      severity: 'CRITICAL'
    }
  }
];

export default function LiveTelemetryStream() {
  const [events, setEvents] = useState(SAMPLE_EVENTS);
  const [filterType, setFilterType] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [simulationActive, setSimulationActive] = useState(false);
  const [lastPingTime, setLastPingTime] = useState(Date.now());
  const [eventCountTotal, setEventCountTotal] = useState(SAMPLE_EVENTS.length);
  const [activeTab, setActiveTab] = useState('stream'); // 'stream' | 'stats' | 'test'

  const eventSourceRef = useRef(null);
  const isPausedRef = useRef(isPaused);
  isPausedRef.current = isPaused;

  // Initialize SSE connection with graceful simulation fallback
  useEffect(() => {
    let sse = null;
    let fallbackTimer = null;

    try {
      sse = new EventSource('/api/telemetry/stream');
      eventSourceRef.current = sse;

      sse.onopen = () => {
        setIsConnected(true);
        setSimulationActive(false);
      };

      const handleIncoming = (evType, rawPayload) => {
        if (isPausedRef.current) return;
        try {
          const parsed = typeof rawPayload === 'string' ? JSON.parse(rawPayload) : rawPayload;
          const newEvent = {
            id: `evt-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
            event_type: evType,
            timestamp: parsed.timestamp || new Date().toISOString(),
            data: parsed.data || parsed
          };
          setEvents(prev => [newEvent, ...prev.slice(0, 199)]);
          setEventCountTotal(c => c + 1);
          setLastPingTime(Date.now());
        } catch {
          // Ignore parsing anomalies
        }
      };

      sse.addEventListener('attendance_scan', (e) => handleIncoming('attendance_scan', e.data));
      sse.addEventListener('xp_gain', (e) => handleIncoming('xp_gain', e.data));
      sse.addEventListener('fleet_heartbeat', (e) => handleIncoming('fleet_heartbeat', e.data));
      sse.addEventListener('tinyml_anomaly', (e) => handleIncoming('tinyml_anomaly', e.data));
      sse.addEventListener('connect', (e) => handleIncoming('connect', e.data));
      sse.addEventListener('ping', () => setLastPingTime(Date.now()));

      sse.onerror = () => {
        setIsConnected(false);
        // Start synthetic generator if server is offline (e.g. preview mode)
        setSimulationActive(true);
      };
    } catch {
      setIsConnected(false);
      setSimulationActive(true);
    }

    // Edge Node Synthetic Generator Fallback
    const simulateNodes = [
      'ESP32_MIT_IOT_LAB_01',
      'ESP32_MIT_EMBEDDED_LAB_02',
      'ESP32_MIT_DSP_VLSI_03',
      'ESP32_MIT_EDGE_NODE_09'
    ];

    const simulateStudents = [
      { id: '2023MITEC042', name: 'Ashok Kumar A', rfid: 'E2 80 6F 3B' },
      { id: '2023MITEC001', name: 'Aarav S', rfid: 'A1 B2 C3 D4' },
      { id: '2023MITEC014', name: 'Deepa K', rfid: '9F 8E 7D 6C' },
      { id: '2023MITEC035', name: 'Kavitha M', rfid: '4B 5C 6D 7E' }
    ];

    const simulateAnomalies = [
      { type: 'BEARING_BALL_DEFECT', rms: 3.94, temp: 64.2, sev: 'WARNING' },
      { type: 'ROTOR_UNBALANCE_HARMONIC', rms: 5.12, temp: 72.8, sev: 'CRITICAL' },
      { type: 'MOTOR_PHASE_ASYMMETRY', rms: 4.31, temp: 67.5, sev: 'WARNING' },
      { type: 'THERMAL_RUNAWAY_SPIKE', rms: 6.05, temp: 81.3, sev: 'CRITICAL' }
    ];

    fallbackTimer = setInterval(() => {
      if (isPausedRef.current) return;

      const dice = Math.random();
      let mockEvent = null;

      if (dice < 0.40) {
        // Attendance scan
        const student = simulateStudents[Math.floor(Math.random() * simulateStudents.length)];
        const node = simulateNodes[Math.floor(Math.random() * simulateNodes.length)];
        mockEvent = {
          id: `sim-${Date.now()}`,
          event_type: 'attendance_scan',
          timestamp: new Date().toISOString(),
          data: {
            node_id: node,
            student_id: student.id,
            student_name: student.name,
            rfid_uid: student.rfid,
            status: 'Lab-Verified',
            rssi: -50 - Math.floor(Math.random() * 25),
            campus: 'MIT Campus, Anna University'
          }
        };
      } else if (dice < 0.65) {
        // XP gain
        const student = simulateStudents[Math.floor(Math.random() * simulateStudents.length)];
        mockEvent = {
          id: `sim-${Date.now()}`,
          event_type: 'xp_gain',
          timestamp: new Date().toISOString(),
          data: {
            student_id: student.id,
            student_name: student.name,
            xp_amount: 50,
            reason: 'ESP32 LittleFS Queue Sync Attained',
            multiplier: '2.5x'
          }
        };
      } else if (dice < 0.85) {
        // Fleet heartbeat
        const node = simulateNodes[Math.floor(Math.random() * simulateNodes.length)];
        mockEvent = {
          id: `sim-${Date.now()}`,
          event_type: 'fleet_heartbeat',
          timestamp: new Date().toISOString(),
          data: {
            node_id: node,
            status: 'ACTIVE_ONLINE',
            rssi: -54 - Math.floor(Math.random() * 20),
            spool_depth: Math.floor(Math.random() * 3),
            ip_address: `10.0.4.${20 + Math.floor(Math.random() * 15)}`
          }
        };
      } else {
        // TinyML edge AI anomaly
        const anomaly = simulateAnomalies[Math.floor(Math.random() * simulateAnomalies.length)];
        mockEvent = {
          id: `sim-${Date.now()}`,
          event_type: 'tinyml_anomaly',
          timestamp: new Date().toISOString(),
          data: {
            node_id: 'ESP32_MIT_EDGE_NODE_09',
            anomaly_type: anomaly.type,
            confidence_pct: +(85 + Math.random() * 14).toFixed(1),
            vibration_rms_g: +(anomaly.rms + (Math.random() * 0.4 - 0.2)).toFixed(3),
            temperature_celsius: +(anomaly.temp + (Math.random() * 1.5 - 0.75)).toFixed(1),
            severity: anomaly.sev
          }
        };
      }

      if (mockEvent) {
        setEvents(prev => [mockEvent, ...prev.slice(0, 199)]);
        setEventCountTotal(c => c + 1);
        setLastPingTime(Date.now());
      }
    }, 4500);

    return () => {
      if (sse) sse.close();
      if (fallbackTimer) clearInterval(fallbackTimer);
    };
  }, []);

  // Filter events
  const filteredEvents = events.filter(evt => {
    if (filterType !== 'ALL' && evt.event_type !== filterType) {
      return false;
    }
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    const str = JSON.stringify(evt).toLowerCase();
    return str.includes(q);
  });

  // Calculate Metrics
  const attendanceCount = events.filter(e => e.event_type === 'attendance_scan').length;
  const xpCount = events.filter(e => e.event_type === 'xp_gain').length;
  const fleetCount = events.filter(e => e.event_type === 'fleet_heartbeat').length;
  const anomalyCount = events.filter(e => e.event_type === 'tinyml_anomaly').length;

  const triggerTestBroadcast = async (type) => {
    const testData = {
      event_type: type,
      data: type === 'tinyml_anomaly' ? {
        node_id: 'ESP32_MIT_EDGE_NODE_09',
        anomaly_type: 'INJECTED_ROTOR_UNBALANCE',
        confidence_pct: 97.4,
        vibration_rms_g: 5.62,
        temperature_celsius: 74.8,
        severity: 'CRITICAL'
      } : {
        node_id: 'ESP32_MIT_IOT_LAB_01',
        student_id: '2023MITEC042',
        student_name: 'Ashok Kumar A',
        rfid_uid: 'E2 80 6F 3B',
        status: 'Lab-Verified',
        rssi: -52
      }
    };

    try {
      const res = await fetch('/api/telemetry/broadcast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testData)
      });
      if (!res.ok) throw new Error('API offline');
    } catch {
      // Local fallback dispatch
      const injected = {
        id: `inj-${Date.now()}`,
        event_type: type,
        timestamp: new Date().toISOString(),
        data: testData.data
      };
      setEvents(prev => [injected, ...prev]);
      setEventCountTotal(c => c + 1);
    }
  };

  return (
    <div className="rounded-2xl border border-[#00F0B5]/30 bg-gradient-to-b from-[#020813] via-[#041026] to-[#020813] p-5 sm:p-7 shadow-2xl font-mono text-slate-100 space-y-6">
      
      {/* Top Header & Status Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-5 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <span className="relative flex h-3 w-3">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${isConnected ? 'bg-[#00F0B5]' : 'bg-amber-400'} opacity-75`}></span>
              <span className={`relative inline-flex rounded-full h-3 w-3 ${isConnected ? 'bg-[#00F0B5]' : 'bg-amber-400'}`}></span>
            </span>
            <h2 className="text-lg sm:text-xl font-bold tracking-tight text-white flex items-center gap-2">
              <span>Real-Time Hardware Telemetry Stream</span>
              <span className="text-[10px] uppercase px-2 py-0.5 rounded bg-[#00693E]/40 text-[#00F0B5] border border-[#00F0B5]/30">
                SSE Broker
              </span>
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Madras Institute of Technology (MIT Campus, Anna University) • Xtensa Dual-Core & Edge AI Node Telemetry
          </p>
        </div>

        {/* Status Indicators & Controls */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-3 text-xs">
          <div className="px-3 py-1.5 rounded-xl bg-[#020813] border border-slate-800 flex items-center gap-2">
            <span className="text-slate-400">Connection:</span>
            {isConnected ? (
              <span className="text-[#00F0B5] font-bold flex items-center gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-[#00F0B5]"></span>
                LIVE SSE (/api/telemetry/stream)
              </span>
            ) : simulationActive ? (
              <span className="text-amber-400 font-bold flex items-center gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-amber-400"></span>
                ACTIVE (Synthetic Edge Ticks)
              </span>
            ) : (
              <span className="text-slate-500">CONNECTING...</span>
            )}
          </div>

          <button
            onClick={() => setIsPaused(p => !p)}
            className={`px-3 py-1.5 rounded-xl border font-bold transition-all flex items-center gap-1.5 ${
              isPaused
                ? 'bg-amber-500/20 border-amber-500/50 text-amber-300 hover:bg-amber-500/30'
                : 'bg-[#041026] border-[#00F0B5]/30 text-slate-300 hover:border-[#00F0B5] hover:text-[#00F0B5]'
            }`}
          >
            {isPaused ? (
              <>
                <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                <span>Resume Feed</span>
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="6" y="4" width="4" height="16"></rect>
                  <rect x="14" y="4" width="4" height="16"></rect>
                </svg>
                <span>Pause</span>
              </>
            )}
          </button>

          <button
            onClick={() => setEvents([])}
            className="px-3 py-1.5 rounded-xl bg-[#020813] border border-slate-800 hover:border-rose-500/40 text-slate-400 hover:text-rose-400 transition-all"
            title="Clear Event Log"
          >
            Clear Log
          </button>
        </div>
      </div>

      {/* Metrics Banner */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-xl bg-[#020813]/80 border border-slate-800/80">
          <div className="text-[10px] uppercase text-slate-400 tracking-wider">Attendance Scans</div>
          <div className="text-2xl font-bold text-[#00F0B5] mt-1">{attendanceCount}</div>
          <div className="text-[10px] text-slate-500 mt-0.5">ESP32 RFID Verified</div>
        </div>

        <div className="p-3.5 rounded-xl bg-[#020813]/80 border border-slate-800/80">
          <div className="text-[10px] uppercase text-slate-400 tracking-wider">XP Dispatches</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">{xpCount}</div>
          <div className="text-[10px] text-slate-500 mt-0.5">2.5x Multiplier Active</div>
        </div>

        <div className="p-3.5 rounded-xl bg-[#020813]/80 border border-slate-800/80">
          <div className="text-[10px] uppercase text-slate-400 tracking-wider">Fleet Heartbeats</div>
          <div className="text-2xl font-bold text-cyan-400 mt-1">{fleetCount}</div>
          <div className="text-[10px] text-slate-500 mt-0.5">LittleFS Zero-Lag</div>
        </div>

        <div className="p-3.5 rounded-xl bg-[#020813]/80 border border-rose-500/20 bg-rose-500/5">
          <div className="text-[10px] uppercase text-rose-400 tracking-wider">TinyML Anomalies</div>
          <div className="text-2xl font-bold text-rose-400 mt-1">{anomalyCount}</div>
          <div className="text-[10px] text-rose-300/70 mt-0.5">Edge AI Classified</div>
        </div>
      </div>

      {/* Filter Tabs & Search Controls */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-2">
        {/* Category Pills */}
        <div className="flex flex-wrap gap-1.5 p-1 rounded-xl bg-[#020813] border border-slate-800 text-xs">
          {[
            { id: 'ALL', label: 'All Feeds', count: events.length },
            { id: 'attendance_scan', label: 'Attendance', count: attendanceCount },
            { id: 'xp_gain', label: 'XP Gains', count: xpCount },
            { id: 'fleet_heartbeat', label: 'IoT Fleet', count: fleetCount },
            { id: 'tinyml_anomaly', label: 'TinyML Anomaly', count: anomalyCount }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setFilterType(tab.id)}
              className={`px-3 py-1 rounded-lg transition-all flex items-center gap-1.5 ${
                filterType === tab.id
                  ? 'bg-[#00693E] text-[#00F0B5] font-bold shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <span>{tab.label}</span>
              <span className="text-[10px] px-1 rounded bg-[#020813]/80 text-slate-300 font-mono">
                {tab.count}
              </span>
            </button>
          ))}
        </div>

        {/* Search Bar */}
        <div className="relative min-w-[200px] sm:w-64">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search student, node, UID..."
            className="w-full px-3 py-1.5 rounded-xl bg-[#020813] border border-slate-800 focus:border-[#00F0B5]/60 text-xs text-slate-200 placeholder-slate-500 focus:outline-none"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 text-xs"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Telemetry Event Stream Log */}
      <div className="rounded-xl border border-slate-800 bg-[#020813] overflow-hidden">
        <div className="px-4 py-2.5 bg-slate-900/60 border-b border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
          <div className="flex items-center gap-2">
            <span>LIVE EVENT LOG</span>
            <span className="text-[#00F0B5]">({filteredEvents.length} displaying)</span>
          </div>
          <div className="flex items-center gap-2">
            <span>Auto-scrolling top-latest</span>
            <span className="h-1.5 w-1.5 rounded-full bg-[#00F0B5] animate-ping"></span>
          </div>
        </div>

        <div className="divide-y divide-slate-800/60 max-h-[460px] overflow-y-auto font-mono text-xs">
          {filteredEvents.length === 0 ? (
            <div className="p-8 text-center text-slate-500">
              No telemetry events match current filter or search criteria.
            </div>
          ) : (
            filteredEvents.map((evt) => {
              const dateStr = new Date(evt.timestamp).toLocaleTimeString();
              const isAnomaly = evt.event_type === 'tinyml_anomaly';
              const isAttendance = evt.event_type === 'attendance_scan';
              const isXp = evt.event_type === 'xp_gain';
              const isFleet = evt.event_type === 'fleet_heartbeat';

              return (
                <div
                  key={evt.id}
                  className={`p-3.5 hover:bg-[#041026]/80 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-3 ${
                    isAnomaly ? 'bg-rose-950/20 border-l-2 border-rose-500' : ''
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {/* Event Badge Icon */}
                    <div className="mt-0.5">
                      {isAttendance && (
                        <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold">
                          SCAN
                        </span>
                      )}
                      {isXp && (
                        <span className="px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-500/30 text-[10px] font-bold">
                          XP
                        </span>
                      )}
                      {isFleet && (
                        <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/30 text-[10px] font-bold">
                          FLEET
                        </span>
                      )}
                      {isAnomaly && (
                        <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-500/40 text-[10px] font-bold animate-pulse">
                          ANOMALY
                        </span>
                      )}
                    </div>

                    {/* Event Body Details */}
                    <div className="space-y-1">
                      {isAttendance && (
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-slate-100 font-bold">{evt.data.student_name}</span>
                          <span className="text-yellow-400 text-[11px]">({evt.data.student_id})</span>
                          <span className="text-slate-500 text-[11px]">RFID:</span>
                          <span className="text-[#00F0B5] bg-[#041026] px-1.5 py-0.2 rounded border border-[#00F0B5]/30 text-[11px]">
                            {evt.data.rfid_uid}
                          </span>
                          <span className="text-emerald-400 text-[10px] font-bold">✓ {evt.data.status}</span>
                        </div>
                      )}

                      {isXp && (
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-amber-400 font-bold">+{evt.data.xp_amount} XP Awarded</span>
                          <span className="text-slate-300 text-[11px]">to {evt.data.student_name}</span>
                          <span className="text-[#00F0B5] text-[10px] px-1.5 py-0.2 rounded bg-[#00693E]/40 border border-[#00F0B5]/30">
                            {evt.data.multiplier} Multiplier
                          </span>
                          <span className="text-slate-400 text-[11px]">— {evt.data.reason}</span>
                        </div>
                      )}

                      {isFleet && (
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-cyan-300 font-bold">{evt.data.node_id}</span>
                          <span className="text-slate-400 text-[11px]">IP: {evt.data.ip_address}</span>
                          <span className="text-slate-400 text-[11px]">RSSI: {evt.data.rssi} dBm</span>
                          <span className="text-slate-500 text-[11px]">Spool Depth: {evt.data.spool_depth}</span>
                        </div>
                      )}

                      {isAnomaly && (
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-rose-400 font-bold">{evt.data.anomaly_type}</span>
                          <span className="text-rose-300 text-[11px] font-mono">
                            Confidence: {evt.data.confidence_pct}%
                          </span>
                          <span className="text-slate-300 text-[11px]">
                            RMS: {evt.data.vibration_rms_g}g
                          </span>
                          <span className="text-amber-300 text-[11px]">
                            Temp: {evt.data.temperature_celsius}°C
                          </span>
                          <span className="text-[10px] px-1.5 rounded bg-rose-900/60 text-rose-300 border border-rose-500/40">
                            {evt.data.severity}
                          </span>
                        </div>
                      )}

                      <div className="text-[10px] text-slate-500 flex items-center gap-2">
                        <span>Node: {evt.data.node_id || 'SERVER_GATEWAY'}</span>
                        <span>•</span>
                        <span>Campus: MIT Chromepet ECE</span>
                      </div>
                    </div>
                  </div>

                  {/* Timestamp & Latency */}
                  <div className="text-right text-[11px] text-slate-400 flex md:flex-col items-center md:items-end justify-between">
                    <span className="font-mono text-slate-300">{dateStr}</span>
                    <span className="text-[9px] text-[#00F0B5]">Zero-Copy Fan-Out</span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Manual Diagnostic Injection Hub */}
      <div className="p-4 rounded-xl bg-[#041026]/60 border border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2 text-slate-400">
          <span className="text-[#00F0B5] font-bold">⚡ Hardware Simulation Trigger:</span>
          <span>Inject simulated telemetry packets into live stream</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => triggerTestBroadcast('attendance_scan')}
            className="px-2.5 py-1.5 rounded-lg bg-[#020813] border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10 transition-colors"
          >
            + RFID Scan (Ashok Kumar A)
          </button>
          <button
            onClick={() => triggerTestBroadcast('tinyml_anomaly')}
            className="px-2.5 py-1.5 rounded-lg bg-[#020813] border border-rose-500/30 text-rose-400 hover:bg-rose-500/10 transition-colors"
          >
            + TinyML Anomaly (Bearing Fatigue)
          </button>
        </div>
      </div>

    </div>
  );
}

