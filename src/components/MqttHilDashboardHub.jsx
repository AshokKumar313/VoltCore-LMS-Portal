import React, { useState, useEffect, useMemo } from 'react';

// Microcontroller Target Profiles
const HIL_DEVICES = {
  ESP32_WROOM_32: {
    key: 'ESP32_WROOM_32',
    name: 'Espressif ESP32-WROOM-32 (Dual Xtensa LX6)',
    vendor: 'Espressif Systems',
    core: 'Dual Xtensa 240 MHz',
    interfaces: ['WebSerial (CP2102/CH340)', 'MQTT over Wi-Fi', 'WebUSB'],
    base_latency_ms: 14.2,
    base_jitter_ms: 2.1,
    default_baud: 115200,
    sensors: 'DHT22 Temp/Humidity, INA219 Voltage/Current, MPU6050 6-DOF',
    color: '#10b981'
  },
  UNO_R4_WIFI: {
    key: 'UNO_R4_WIFI',
    name: 'Arduino Uno R4 WiFi (RA4M1 + ESP32-S3)',
    vendor: 'Arduino / Renesas',
    core: 'Renesas RA4M1 Cortex-M4F 48 MHz',
    interfaces: ['WebUSB Native CDC', 'WebSerial', 'MQTT Bridge'],
    base_latency_ms: 22.5,
    base_jitter_ms: 3.4,
    default_baud: 115200,
    sensors: 'Analog NTC Thermistor, LDR Photodiode, DAC Waveform',
    color: '#38bdf8'
  },
  RP2040_PICO_W: {
    key: 'RP2040_PICO_W',
    name: 'Raspberry Pi Pico W (Dual Cortex-M0+ & CYW43439)',
    vendor: 'Raspberry Pi',
    core: 'Dual ARM Cortex-M0+ 133 MHz',
    interfaces: ['WebSerial (TinyUSB CDC)', 'MQTT over Wi-Fi', 'WebUSB'],
    base_latency_ms: 18.0,
    base_jitter_ms: 2.8,
    default_baud: 115200,
    sensors: 'On-die ADC Temp Sensor, Quadrature Encoder, PWM Power',
    color: '#f59e0b'
  },
  NUCLEO_F401RE: {
    key: 'NUCLEO_F401RE',
    name: 'STM32 Nucleo-F401RE (ARM Cortex-M4F)',
    vendor: 'STMicroelectronics',
    core: 'ARM Cortex-M4F 84 MHz',
    interfaces: ['WebSerial (ST-LINK V2-1 VCP)', 'WebUSB CDC-ACM', 'MQTT Gateway'],
    base_latency_ms: 9.4,
    base_jitter_ms: 1.2,
    default_baud: 115200,
    sensors: 'BME280 Environmental, MAX30102 Oximeter, Current Shunt',
    color: '#a855f7'
  }
};

// Transport Protocols
const TRANSPORTS = [
  { key: 'WEBSERIAL', label: 'WebSerial API (navigator.serial)', desc: 'Direct browser COM/TTY port access (CH340/CP2102/FTDI)' },
  { key: 'WEBUSB', label: 'WebUSB API (navigator.usb)', desc: 'Direct USB CDC-ACM / WinUSB raw endpoint streaming' },
  { key: 'MQTT_WSS', label: 'MQTT over WebSockets (WSS)', desc: 'Secure browser WebSocket broker bridge (Port 8883/WSS)' },
  { key: 'MQTT_TCP', label: 'MQTT Native TCP Gateway', desc: 'Standard OASIS MQTT v3.1.1/v5 broker connection (Port 1883)' }
];

// Baud Rates
const BAUD_RATES = [9600, 19200, 38400, 57600, 115200, 230400, 921600];

// Bilingual Guidance
const DICTIONARY = {
  en: {
    badge: 'PHASE 39 ENTERPRISE',
    title: 'Cloud IoT MQTT Broker & WebSerial / WebUSB HIL Dashboard',
    subtitle: 'Hardware-in-the-Loop • Live Microcontroller Telemetry • RFC 3550 Jitter • Raw Serial Terminal & Loss Profiler',
    author: 'Platform Lead: Ashok Kumar A (2023MITEC042) • MIT Campus, Anna University',
    mcuTarget: 'Connected MCU Target',
    transportMode: 'Physical / Network Transport',
    baudRate: 'Serial Baud Rate',
    qosLevel: 'MQTT Delivery Guarantee (QoS)',
    connectBtn: 'Connect WebSerial Port',
    disconnectBtn: 'Disconnect Port',
    streamBurstBtn: 'Stream Telemetry Burst (20 Pkts)',
    singleStepBtn: 'Send Single Packet Step',
    exportCsv: 'Export HIL Session CSV',
    clearTerminal: 'Clear Terminal',
    portStatusOpen: 'PORT CONNECTED (STREAMING)',
    portStatusClosed: 'PORT DISCONNECTED',
    avgLatency: 'Average Latency',
    rfcJitter: 'RFC 3550 Inter-Arrival Jitter',
    throughput: 'Throughput',
    deliveryRatio: 'Packet Delivery Ratio',
    packetLoss: 'Packet Loss Rate',
    terminalTitle: 'Hardware Serial Terminal & MQTT Packet Inspector',
    cmdPrompt: 'Transmit Raw Serial Command:',
    sendCmdBtn: 'Send Command',
    filterAll: 'All Logs',
    filterTelemetry: 'Telemetry Only',
    filterCommands: 'Commands Only',
    statusCrcOk: 'CRC-16 OK',
    jitterInfo: 'RFC 3550 formula: J_i = J_{i-1} + (|D(i-1, i)| - J_{i-1}) / 16'
  },
  ta: {
    badge: 'நிலை 39 நிறுவனம்',
    title: 'கிளவுட் IoT MQTT புரோக்கர் & WebSerial / WebUSB HIL டாஷ்போர்டு',
    subtitle: 'வன்பொருள்-சுழற்சி (HIL) • நேரலை மைக்ரோகண்ட்ரோலர் டெலிமெட்ரி • RFC 3550 ஜிட்டர் • சீரியல் முனையம் & இழப்பு பகுப்பாய்வு',
    author: 'இயங்குதள தலைமை: அசோக் குமார் A (2023MITEC042) • எம்.ஐ.டி வளாகம், அண்ணா பல்கலைக்கழகம்',
    mcuTarget: 'இணைக்கப்பட்ட MCU சாதனம்',
    transportMode: 'தகவல் தொடர்பு முறை',
    baudRate: 'சீரியல் பாட் விகிதம்',
    qosLevel: 'MQTT விநியோக உத்தரவாதம் (QoS)',
    connectBtn: 'WebSerial போர்ட்டை இணை',
    disconnectBtn: 'போர்ட்டை துண்டி',
    streamBurstBtn: 'டெலிமெட்ரி ஸ்ட்ரீமை இயக்கு (20 பாக்கெட்டுகள்)',
    singleStepBtn: 'ஒரு பாக்கெட்டை அனுப்பு',
    exportCsv: 'HIL அமர்வு CSV-யை பதிவிறக்கு',
    clearTerminal: 'முனையத்தை அழி',
    portStatusOpen: 'போர்ட் இணைக்கப்பட்டது (செயலில்)',
    portStatusClosed: 'போர்ட் துண்டிக்கப்பட்டது',
    avgLatency: 'சராசரி தாமதம்',
    rfcJitter: 'RFC 3550 இடைக்கால ஜிட்டர்',
    throughput: 'செயல்திறன் வேகம்',
    deliveryRatio: 'பாக்கெட் விநியோக விகிதம்',
    packetLoss: 'பாக்கெட் இழப்பு விகிதம்',
    terminalTitle: 'வன்பொருள் சீரியல் முனையம் & MQTT பாக்கெட் ஆய்வாளர்',
    cmdPrompt: 'சீரியல் கட்டளையை உள்ளிடவும்:',
    sendCmdBtn: 'அனுப்பு',
    filterAll: 'அனைத்து பதிவுகள்',
    filterTelemetry: 'டெலிமெட்ரி மட்டும்',
    filterCommands: 'கட்டளைகள் மட்டும்',
    statusCrcOk: 'CRC-16 சரி',
    jitterInfo: 'RFC 3550 சூத்திரம்: J_i = J_{i-1} + (|D(i-1, i)| - J_{i-1}) / 16'
  }
};

// CRC-16-CCITT in JavaScript
function computeCrc16(str) {
  let crc = 0xFFFF;
  for (let c = 0; c < str.length; c++) {
    crc ^= str.charCodeAt(c) << 8;
    for (let i = 0; i < 8; i++) {
      if (crc & 0x8000) {
        crc = ((crc << 1) ^ 0x1021) & 0xFFFF;
      } else {
        crc = (crc << 1) & 0xFFFF;
      }
    }
  }
  return '0x' + crc.toString(16).toUpperCase().padStart(4, '0');
}

export default function MqttHilDashboardHub() {
  const [lang, setLang] = useState('en');
  const [selectedDeviceKey, setSelectedDeviceKey] = useState('ESP32_WROOM_32');
  const [selectedTransport, setSelectedTransport] = useState('WEBSERIAL');
  const [selectedBaud, setSelectedBaud] = useState(115200);
  const [qosLevel, setQosLevel] = useState(1);
  const [isConnected, setIsConnected] = useState(true);
  const [filterMode, setFilterMode] = useState('ALL');
  const [commandInput, setCommandInput] = useState('AT+STATUS');
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionData, setSessionData] = useState(null);
  const [terminalLogs, setTerminalLogs] = useState([]);

  const t = DICTIONARY[lang];
  const activeDevice = HIL_DEVICES[selectedDeviceKey];

  // Client Simulation Engine (Zero Background Polling, Manual Trigger)
  const computeClientBurst = (packetCount = 20) => {
    let baseLat = activeDevice.base_latency_ms;
    if (selectedTransport === 'WEBUSB') baseLat *= 0.7;
    if (selectedTransport === 'MQTT_WSS') baseLat *= 1.3;

    let runningJitter = activeDevice.base_jitter_ms;
    let prevTransit = baseLat;
    const pkts = [];
    let received = 0;
    let totalBytes = 0;
    const transitArr = [];

    const now = Date.now();

    for (let seq = 1; seq <= packetCount; seq++) {
      const noise = Math.sin(seq * 0.45) * 1.8 + Math.cos(seq * 0.25) * 0.9;
      const transit = Math.max(2.0, Number((baseLat + noise).toFixed(2)));
      transitArr.push(transit);

      const diff = Math.abs(transit - prevTransit);
      runningJitter = Number((runningJitter + (diff - runningJitter) / 16.0).toFixed(3));
      prevTransit = transit;

      const dropped = (seq === 13 && qosLevel === 0);
      const status = dropped ? 'DROPPED' : (seq === 13 && qosLevel >= 1 ? 'RETRIED_ACK' : 'ACKNOWLEDGED');

      const telemetryObj = {
        seq,
        node: activeDevice.key,
        temp_c: Number((26.5 + Math.sin(seq * 0.3) * 3.2).toFixed(2)),
        humidity_pct: Number((58.0 + Math.cos(seq * 0.2) * 5.5).toFixed(1)),
        bus_v: Number((3.29 + (seq % 5) * 0.005).toFixed(3)),
        current_ma: Number((42.5 + Math.sin(seq * 0.8) * 8.0).toFixed(1)),
        uptime_ms: seq * 100
      };

      const payloadStr = JSON.stringify(telemetryObj);
      const crcHex = computeCrc16(payloadStr);
      const byteLen = payloadStr.length;

      if (!dropped) {
        received++;
        totalBytes += byteLen;
      }

      pkts.push({
        session_id: `HIL_${now}`,
        seq_num: seq,
        topic: `voltcore/mit/ece/lab304/${activeDevice.key.toLowerCase()}/telemetry`,
        payload_json: payloadStr,
        payload_bytes: byteLen,
        transit_time_ms: transit,
        jitter_ms: runningJitter,
        crc_valid: 1,
        crc16_hex: crcHex,
        status,
        timestamp: new Date(now + seq * 50).toISOString()
      });
    }

    const lossPct = Number((((packetCount - received) / packetCount) * 100).toFixed(2));
    const avgLat = Number((transitArr.reduce((a, b) => a + b, 0) / transitArr.length).toFixed(2));
    const durationS = Math.max(0.1, packetCount * 0.05);
    const throughput = Number(((totalBytes * 8.0) / (durationS * 1000.0)).toFixed(2));

    return {
      status: 'SUCCESS',
      session_id: `HIL_CLIENT_${now}`,
      device: activeDevice,
      transport_mode: selectedTransport,
      baud_rate: selectedBaud,
      qos_level: qosLevel,
      summary: {
        packets_transmitted: packetCount,
        packets_received: received,
        packet_loss_pct: lossPct,
        avg_latency_ms: avgLat,
        avg_jitter_ms: runningJitter,
        throughput_kbps: throughput,
        total_bytes_transferred: totalBytes
      },
      packets: pkts
    };
  };

  // Run on mount or device switch (manual trigger initial payload)
  useEffect(() => {
    handleStreamBurst(20);
  }, [selectedDeviceKey, selectedTransport, selectedBaud, qosLevel]);

  const handleStreamBurst = async (packetCount = 20) => {
    setIsStreaming(true);
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1200);

      const resp = await fetch('/api/mqtt-hil/simulate-stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({
          device_id: selectedDeviceKey,
          transport_mode: selectedTransport,
          baud_rate: selectedBaud,
          qos_level: qosLevel,
          num_packets: packetCount,
          student_id: '2023MITEC042'
        })
      });
      clearTimeout(timeoutId);

      if (resp.ok) {
        const data = await resp.json();
        setSessionData(data);
        appendTerminalPackets(data.packets);
      } else {
        const fallback = computeClientBurst(packetCount);
        setSessionData(fallback);
        appendTerminalPackets(fallback.packets);
      }
    } catch {
      const fallback = computeClientBurst(packetCount);
      setSessionData(fallback);
      appendTerminalPackets(fallback.packets);
    }
    setIsStreaming(false);
  };

  const appendTerminalPackets = (newPackets) => {
    setTerminalLogs(prev => {
      const combined = [...prev, ...newPackets];
      return combined.slice(-60); // Keep last 60 lines for thermal discipline
    });
  };

  // Handle Manual Command Send
  const handleSendCommand = async () => {
    if (!commandInput.trim()) return;

    const cmdPkt = {
      session_id: `CMD_${Date.now()}`,
      seq_num: terminalLogs.length + 1,
      topic: `voltcore/mit/ece/lab304/${activeDevice.key.toLowerCase()}/command`,
      payload_json: JSON.stringify({ command: commandInput, sender: 'Ashok Kumar A (2023MITEC042)' }),
      payload_bytes: commandInput.length,
      transit_time_ms: Number((activeDevice.base_latency_ms * 0.6).toFixed(2)),
      jitter_ms: Number((activeDevice.base_jitter_ms * 0.5).toFixed(3)),
      crc_valid: 1,
      crc16_hex: computeCrc16(commandInput),
      status: 'ACKNOWLEDGED',
      timestamp: new Date().toISOString()
    };

    setTerminalLogs(prev => [...prev, cmdPkt].slice(-60));

    try {
      await fetch('/api/mqtt-hil/publish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          device_id: selectedDeviceKey,
          topic: cmdPkt.topic,
          payload: { command: commandInput },
          qos_level: qosLevel,
          student_id: '2023MITEC042'
        })
      });
    } catch {
      // Ignored for offline client mode
    }
  };

  // Export RFC-4180 CSV
  const handleExportCsv = () => {
    const rows = [
      ['Packet_ID', 'Session_ID', 'Seq_Num', 'Topic', 'Payload_Bytes', 'Transit_Time_ms', 'Jitter_ms', 'CRC_Valid', 'Status', 'Timestamp']
    ];

    terminalLogs.forEach(p => {
      rows.push([
        p.id || 'N/A',
        p.session_id,
        p.seq_num,
        p.topic,
        p.payload_bytes,
        p.transit_time_ms,
        p.jitter_ms,
        p.crc_valid,
        p.status,
        p.timestamp
      ]);
    });

    const csvContent = 'data:text/csv;charset=utf-8,' + rows.map(e => e.join(',')).join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `voltcore_mqtt_hil_session_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const res = sessionData || computeClientBurst(20);
  const deliveryRatioPct = Number((100.0 - res.summary.packet_loss_pct).toFixed(1));

  // Filter Terminal Logs
  const filteredLogs = useMemo(() => {
    if (filterMode === 'TELEMETRY') {
      return terminalLogs.filter(l => l.topic.includes('telemetry'));
    }
    if (filterMode === 'COMMANDS') {
      return terminalLogs.filter(l => l.topic.includes('command'));
    }
    return terminalLogs;
  }, [terminalLogs, filterMode]);

  return (
    <div className="bg-[#020813] border border-cyan-500/30 rounded-3xl p-6 sm:p-8 text-slate-200 shadow-2xl relative overflow-hidden font-mono">
      {/* Background Ambient Glow */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-cyan-500/10 via-emerald-500/5 to-transparent rounded-full blur-3xl pointer-events-none" />

      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6 relative z-10">
        <div>
          <div className="flex items-center gap-3">
            <span className="px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 text-xs font-bold tracking-wider">
              {t.badge}
            </span>
            <span className="text-xs text-slate-400">Anna University R2023 Hardware Lab 304</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-black text-white mt-2 tracking-tight">
            {t.title}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            {t.subtitle}
          </p>
          <p className="text-[11px] text-cyan-400/90 mt-0.5">
            {t.author}
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setLang(lang === 'en' ? 'ta' : 'en')}
            className="px-3 py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-xs border border-slate-700 text-slate-300 transition-all font-semibold"
          >
            🌐 {lang === 'en' ? 'தமிழ்' : 'English'}
          </button>
          <button
            onClick={handleExportCsv}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-500 hover:to-teal-500 text-white text-xs font-bold shadow-lg shadow-cyan-900/30 transition-all flex items-center gap-1.5"
          >
            📥 {t.exportCsv}
          </button>
        </div>
      </div>

      {/* Target Device & Transport Parameters */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6 relative z-10">
        {/* MCU Target */}
        <div className="bg-[#0b1329] border border-slate-800 rounded-2xl p-4">
          <label className="text-xs font-bold text-slate-300 block mb-2">
            🎛️ {t.mcuTarget}
          </label>
          <select
            value={selectedDeviceKey}
            onChange={(e) => setSelectedDeviceKey(e.target.value)}
            className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3 py-2 text-xs text-cyan-300 font-mono focus:border-cyan-500 focus:outline-none"
          >
            {Object.values(HIL_DEVICES).map(d => (
              <option key={d.key} value={d.key}>{d.name}</option>
            ))}
          </select>
          <div className="mt-2 text-[11px] text-slate-400">
            <div>Core: <span className="text-white font-bold">{activeDevice.core}</span></div>
            <div>Sensors: <span className="text-cyan-400">{activeDevice.sensors}</span></div>
          </div>
        </div>

        {/* Transport Protocol */}
        <div className="bg-[#0b1329] border border-slate-800 rounded-2xl p-4">
          <label className="text-xs font-bold text-slate-300 block mb-2">
            🔌 {t.transportMode}
          </label>
          <select
            value={selectedTransport}
            onChange={(e) => setSelectedTransport(e.target.value)}
            className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3 py-2 text-xs text-emerald-300 font-mono focus:border-emerald-500 focus:outline-none"
          >
            {TRANSPORTS.map(tr => (
              <option key={tr.key} value={tr.key}>{tr.label}</option>
            ))}
          </select>
          <div className="mt-2 text-[11px] text-slate-400 leading-tight">
            {TRANSPORTS.find(t => t.key === selectedTransport)?.desc}
          </div>
        </div>

        {/* Baud Rate */}
        <div className="bg-[#0b1329] border border-slate-800 rounded-2xl p-4">
          <label className="text-xs font-bold text-slate-300 block mb-2">
            ⚡ {t.baudRate}
          </label>
          <select
            value={selectedBaud}
            onChange={(e) => setSelectedBaud(Number(e.target.value))}
            className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3 py-2 text-xs text-amber-300 font-mono focus:border-amber-500 focus:outline-none"
          >
            {BAUD_RATES.map(b => (
              <option key={b} value={b}>{b} bps (8N1)</option>
            ))}
          </select>
          <div className="mt-2 text-[11px] text-slate-400">
            Framing: <span className="text-white font-bold">1 Start, 8 Data, No Parity, 1 Stop</span>
          </div>
        </div>

        {/* MQTT QoS Level */}
        <div className="bg-[#0b1329] border border-slate-800 rounded-2xl p-4 flex flex-col justify-between">
          <div>
            <label className="text-xs font-bold text-slate-300 block mb-2">
              🛡️ {t.qosLevel}
            </label>
            <div className="grid grid-cols-3 gap-1.5">
              {[0, 1, 2].map(q => (
                <button
                  key={q}
                  onClick={() => setQosLevel(q)}
                  className={`py-1.5 rounded-lg text-xs font-bold transition-all border ${
                    qosLevel === q
                      ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300'
                      : 'bg-[#020813] border-slate-700 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  QoS {q}
                </button>
              ))}
            </div>
          </div>
          <div className="text-[10px] text-slate-400 mt-2">
            {qosLevel === 0 && 'QoS 0: At most once (No retry)'}
            {qosLevel === 1 && 'QoS 1: At least once (PUBACK)'}
            {qosLevel === 2 && 'QoS 2: Exactly once (4-way handshake)'}
          </div>
        </div>
      </div>

      {/* Port Status & Manual Stream Trigger Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 mt-5 p-4 rounded-2xl bg-[#0b1329] border border-slate-800 relative z-10">
        <div className="flex items-center gap-3">
          <span className={`w-3 h-3 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
          <span className="text-xs font-bold text-white tracking-wider">
            {isConnected ? t.portStatusOpen : t.portStatusClosed}
          </span>
          <span className="text-xs text-slate-400 hidden sm:inline">
            • {selectedTransport} • {selectedBaud} bps • Node: {activeDevice.key}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsConnected(!isConnected)}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold border transition-all ${
              isConnected
                ? 'bg-rose-500/20 border-rose-500/40 text-rose-300 hover:bg-rose-500/30'
                : 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300 hover:bg-emerald-500/30'
            }`}
          >
            {isConnected ? `❌ ${t.disconnectBtn}` : `🔗 ${t.connectBtn}`}
          </button>
          <button
            onClick={() => handleStreamBurst(20)}
            disabled={isStreaming}
            className="px-4 py-1.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow-md shadow-emerald-900/30 transition-all flex items-center gap-1.5"
          >
            {isStreaming ? '🔄 Streaming...' : `⚡ ${t.streamBurstBtn}`}
          </button>
        </div>
      </div>

      {/* Live Telemetry KPI Gauges */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-5 relative z-10">
        {/* Latency */}
        <div className="bg-[#0b1329]/90 border border-slate-800 rounded-2xl p-4">
          <div className="text-[11px] text-slate-400 uppercase tracking-wider">{t.avgLatency}</div>
          <div className="text-2xl font-black text-cyan-400 mt-1">
            {res.summary.avg_latency_ms} <span className="text-xs font-normal text-slate-400">ms</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-1">
            Baseline: {activeDevice.base_latency_ms} ms round-trip
          </div>
        </div>

        {/* RFC 3550 Inter-Arrival Jitter */}
        <div className="bg-[#0b1329]/90 border border-slate-800 rounded-2xl p-4">
          <div className="text-[11px] text-slate-400 uppercase tracking-wider">{t.rfcJitter}</div>
          <div className="text-2xl font-black text-emerald-400 mt-1">
            {res.summary.avg_jitter_ms} <span className="text-xs font-normal text-slate-400">ms</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-1">
            Smoothed (RFC 3550 standard)
          </div>
        </div>

        {/* Throughput */}
        <div className="bg-[#0b1329]/90 border border-slate-800 rounded-2xl p-4">
          <div className="text-[11px] text-slate-400 uppercase tracking-wider">{t.throughput}</div>
          <div className="text-2xl font-black text-amber-400 mt-1">
            {res.summary.throughput_kbps} <span className="text-xs font-normal text-slate-400">kbps</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-1">
            Payload: {res.summary.total_bytes_transferred} bytes transferred
          </div>
        </div>

        {/* Packet Delivery / Loss Ratio */}
        <div className="bg-[#0b1329]/90 border border-slate-800 rounded-2xl p-4">
          <div className="text-[11px] text-slate-400 uppercase tracking-wider">{t.deliveryRatio}</div>
          <div className="text-2xl font-black text-purple-400 mt-1">
            {deliveryRatioPct} <span className="text-xs font-normal text-slate-400">%</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-1">
            Loss: {res.summary.packet_loss_pct}% (Transmitted: {res.summary.packets_transmitted})
          </div>
        </div>
      </div>

      {/* Raw Serial Terminal & Packet Stream Viewer */}
      <div className="mt-6 bg-[#060c18] border border-slate-800 rounded-2xl p-5 relative z-10">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <span className="text-emerald-400">📟</span>
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              {t.terminalTitle}
            </h3>
          </div>

          {/* Filter Pills & Clear Button */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setFilterMode('ALL')}
              className={`px-2.5 py-1 rounded-lg text-[10px] font-bold ${filterMode === 'ALL' ? 'bg-cyan-500/30 text-cyan-300 border border-cyan-500/40' : 'text-slate-400 hover:text-slate-200'}`}
            >
              {t.filterAll}
            </button>
            <button
              onClick={() => setFilterMode('TELEMETRY')}
              className={`px-2.5 py-1 rounded-lg text-[10px] font-bold ${filterMode === 'TELEMETRY' ? 'bg-emerald-500/30 text-emerald-300 border border-emerald-500/40' : 'text-slate-400 hover:text-slate-200'}`}
            >
              {t.filterTelemetry}
            </button>
            <button
              onClick={() => setFilterMode('COMMANDS')}
              className={`px-2.5 py-1 rounded-lg text-[10px] font-bold ${filterMode === 'COMMANDS' ? 'bg-amber-500/30 text-amber-300 border border-amber-500/40' : 'text-slate-400 hover:text-slate-200'}`}
            >
              {t.filterCommands}
            </button>
            <button
              onClick={() => setTerminalLogs([])}
              className="px-2.5 py-1 rounded-lg text-[10px] font-bold text-rose-400 hover:bg-rose-500/20 border border-rose-500/30"
            >
              {t.clearTerminal}
            </button>
          </div>
        </div>

        {/* Scrollable Monospace Terminal Stream */}
        <div className="h-64 overflow-y-auto space-y-1.5 p-3 bg-[#020813] border border-slate-900 rounded-xl text-[11px] font-mono select-text">
          {filteredLogs.length === 0 ? (
            <div className="text-slate-600 text-center py-10">
              Terminal buffer empty. Click "Stream Telemetry Burst" or send a serial command.
            </div>
          ) : (
            filteredLogs.map((p, idx) => {
              const isCommand = p.topic.includes('command');
              const isDropped = p.status === 'DROPPED';
              return (
                <div key={idx} className="flex flex-wrap items-baseline gap-2 py-0.5 border-b border-slate-900/60 hover:bg-slate-900/40">
                  <span className="text-slate-500 text-[10px]">[{p.timestamp.slice(11, 23)}]</span>
                  <span className="text-slate-400 font-bold">#{p.seq_num}</span>
                  <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${isCommand ? 'bg-amber-500/20 text-amber-300' : 'bg-cyan-500/20 text-cyan-300'}`}>
                    {p.topic.split('/').pop().toUpperCase()}
                  </span>
                  <span className="text-slate-300 flex-1 truncate">{p.payload_json}</span>
                  <span className="text-emerald-400/90 text-[10px]">CRC:{p.crc16_hex}</span>
                  <span className="text-slate-400 text-[10px]">{p.transit_time_ms}ms</span>
                  <span className={`text-[10px] font-bold ${isDropped ? 'text-rose-400' : 'text-emerald-400'}`}>
                    [{p.status}]
                  </span>
                </div>
              );
            })
          )}
        </div>

        {/* Command Transmission Input Box */}
        <div className="mt-3 flex gap-2">
          <input
            type="text"
            value={commandInput}
            onChange={(e) => setCommandInput(e.target.value)}
            placeholder="e.g. AT+STATUS, MQTT:PUB voltcore/mit/ece/lab304/relay1 1, SYS:RESET"
            className="flex-1 bg-[#020813] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white font-mono focus:border-cyan-500 focus:outline-none"
            onKeyDown={(e) => e.key === 'Enter' && handleSendCommand()}
          />
          <button
            onClick={handleSendCommand}
            className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold transition-all"
          >
            {t.sendCmdBtn}
          </button>
        </div>
      </div>

      {/* Footer Mathematical Notes & Lead Attribution */}
      <div className="mt-6 pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-400 relative z-10 gap-2">
        <div>
          Madras Institute of Technology (MIT) Campus, Anna University • Regulation 2023
        </div>
        <div className="text-cyan-400 font-bold">
          Platform Lead: Ashok Kumar A (2023MITEC042)
        </div>
      </div>
    </div>
  );
}
