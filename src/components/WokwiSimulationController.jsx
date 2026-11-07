import React, { useState, useEffect, useRef } from 'react';

/**
 * VoltCore Apex Academia - Advanced Wokwi Hardware Simulation Controller
 * Core Engineering Series • Autonomous Engineering Cluster
 * Features:
 *   - Virtual Potentiometer 12-bit ADC (GPIO 34 / 35) with live millivolt scaling
 *   - Interactive Tactile Pushbuttons (GPIO 0 Boot / GPIO 4 Manual Scan)
 *   - 4-Bit Hardware DIP Switch Register Simulator
 *   - DHT22 & HC-SR04 Ultrasonic Multi-Sensor Injection Engine
 *   - Real-Time Streaming UART Serial Terminal (115200 Baud) with Filter & Hex Export
 *   - Cross-component telemetry dispatching (voltcore:lab-telemetry)
 */

const PRESET_RFID_CARDS = [
  { name: 'Ashok Kumar A', roll: 'VOLT-ENG-042', uid: 'E2 80 6F 3B', dept: 'Embedded Cluster' },
  { name: 'Kavitha Raman', roll: 'VOLT-ENG-015', uid: 'C3 4D 8A 11', dept: 'Embedded Cluster' },
  { name: 'Dr. K. S. Parthasarathy', roll: 'FAC-ENG-019', uid: 'A4 12 99 F0', dept: 'Lead Faculty' },
  { name: 'Rogue Card (Unauthorized)', roll: 'UNKNOWN-99', uid: 'FF FF FF FF', dept: 'Guest' }
];

export default function WokwiSimulationController({
  serverUrl = 'http://127.0.0.1:5000',
  defaultBaud = 115200
}) {
  // Potentiometer & ADC state
  const [potentiometerVal, setPotentiometerVal] = useState(2048);
  const [adcAttenuation, setAdcAttenuation] = useState('11dB'); // 0dB, 2.5dB, 6dB, 11dB
  
  // Button press states
  const [btn0Pressed, setBtn0Pressed] = useState(false);
  const [btn4Pressed, setBtn4Pressed] = useState(false);

  // DIP Switches: [FreeRTOS Preempt, Verbose UART, SPI DMA, Wi-Fi Station]
  const [dipSwitches, setDipSwitches] = useState({
    sw1_preempt: true,
    sw2_verbose: true,
    sw3_dma: true,
    sw4_wifi_sta: true
  });

  // Sensor injection states
  const [temperature, setTemperature] = useState(28.5);
  const [humidity, setHumidity] = useState(62.0);
  const [ultrasonicDistance, setUltrasonicDistance] = useState(45); // cm
  const [selectedCardIdx, setSelectedCardIdx] = useState(0);

  // Serial Monitor State
  const [baudRate, setBaudRate] = useState(defaultBaud);
  const [autoScroll, setAutoScroll] = useState(true);
  const [serialFilter, setSerialFilter] = useState('');
  const [serialInputText, setSerialInputText] = useState('');
  const [streamActive, setStreamActive] = useState(false);
  const [serialLogs, setSerialLogs] = useState([
    { id: 1, ts: '15:22:40.012', text: '[BOOT] ESP32-WROOM-32 (Xtensa LX6 @ 240MHz) FreeRTOS Kernel v10.4.3 initialized.', type: 'sys' },
    { id: 2, ts: '15:22:40.115', text: '[GPIO] Pin Mappings: SPI_CS=5, SCK=18, MOSI=23, MISO=19, I2C_SDA=21, I2C_SCL=22', type: 'info' },
    { id: 3, ts: '15:22:40.420', text: '[ADC] ADC1 Channel 6 (GPIO 34) calibrated: Attenuation 11dB (Full Scale 0.0V - 3.3V)', type: 'info' },
    { id: 4, ts: '15:22:41.002', text: '[WIFI] Connected to SSID: Wokwi-GUEST | IP: 10.0.2.15 | RSSI: -58 dBm', type: 'success' },
    { id: 5, ts: '15:22:42.500', text: '[SYSTEM] Hardware in-the-loop simulation active. Waiting for sensor stimuli...', type: 'sys' }
  ]);

  const serialEndRef = useRef(null);

  // Auto-scroll handler
  useEffect(() => {
    if (autoScroll) {
      serialEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [serialLogs, autoScroll]);

  const appendSerialLog = (text, type = 'info') => {
    const now = new Date();
    const ts = `${now.toTimeString().split(' ')[0]}.${String(now.getMilliseconds()).padStart(3, '0')}`;
    setSerialLogs((prev) => [...prev, { id: Date.now() + Math.random(), ts, text, type }]);
  };

  // Live SSE Telemetry & Lesson Reader Bridge (Push-driven, ZERO polling loops)
  useEffect(() => {
    if (typeof window === 'undefined') return;

    let es = null;
    if ('EventSource' in window) {
      try {
        es = new EventSource(`${serverUrl}/api/telemetry/stream`);

        es.addEventListener('connect', () => {
          setStreamActive(true);
          appendSerialLog('[STREAM] Live SSE Telemetry Pipeline connected to Wokwi Bridge.', 'sys');
        });

        es.addEventListener('hardware_telemetry', (e) => {
          try {
            const data = JSON.parse(e.data);
            const payload = data.data || data;
            if (payload.gpio_states?.GPIO34 !== undefined) {
              setPotentiometerVal(payload.gpio_states.GPIO34);
            }
            if (payload.adc_readings?.ADC1_CH6_V !== undefined) {
              appendSerialLog(`[REMOTE_ADC] GPIO 34 = ${payload.adc_readings.ADC1_CH6_V} V`, 'info');
            }
          } catch (_) {}
        });

        es.addEventListener('virtual_serial', (e) => {
          try {
            const data = JSON.parse(e.data);
            const payload = data.data || data;
            appendSerialLog(`[UART_RX] ${payload.payload_text || payload.text}`, 'info');
          } catch (_) {}
        });

        es.onerror = () => {
          setStreamActive(false);
          if (es) {
            try { es.close(); } catch (_) {}
          }
        };
      } catch (_) {}
    }

    // Local cross-component transmission from Lesson Reader or Virtual Instruments
    const handleLessonTransmit = (e) => {
      const text = e.detail?.text || e.detail?.payload || '';
      if (text) {
        appendSerialLog(`[LESSON_BRIDGE] Transmitted from curriculum lesson: "${text}"`, 'success');
      }
    };
    window.addEventListener('voltcore:lesson-transmit', handleLessonTransmit);

    return () => {
      if (es) {
        try { es.close(); } catch (_) {}
      }
      window.removeEventListener('voltcore:lesson-transmit', handleLessonTransmit);
    };
  }, [serverUrl]);

  // Transmit Virtual Serial Command
  const handleSendSerialCommand = async (e) => {
    e.preventDefault();
    const cmd = serialInputText.trim();
    if (!cmd) return;

    appendSerialLog(`> ${cmd}`, 'sys');
    setSerialInputText('');

    // Dispatch locally for zero-latency client response
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('voltcore:serial-tx', {
        detail: { text: cmd, board: 'ESP32_VOLTCORE_IOT_01', timestamp: new Date().toISOString() }
      }));
    }

    // Forward to backend stream if connected
    try {
      await fetch(`${serverUrl}/api/telemetry/serial/transmit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          board_id: 'ESP32_VOLTCORE_IOT_01',
          text: cmd,
          baud_rate: baudRate,
          direction: 'TX'
        })
      });
    } catch (_) {
      // Offline fallback: respond to standard AT / diagnostic commands
      if (cmd.toUpperCase() === 'AT') {
        setTimeout(() => appendSerialLog('OK', 'success'), 50);
      } else if (cmd.toUpperCase() === 'AT+GMR' || cmd.toUpperCase() === 'VERSION') {
        setTimeout(() => appendSerialLog('[ESP-IDF] v5.1.2-dirty / FreeRTOS v10.4.3', 'info'), 50);
      } else if (cmd.toUpperCase() === 'ADC?') {
        setTimeout(() => appendSerialLog(`[ADC1_CH6] Raw: ${potentiometerVal} | ${calculatedVoltage} V`, 'info'), 50);
      }
    }
  };

  // Calculated Voltage based on 12-bit ADC (0 - 4095)
  const calculatedVoltage = ((potentiometerVal / 4095.0) * 3.3).toFixed(3);
  const ultrasonicEchoUs = Math.round(ultrasonicDistance * 58.0); // 58 us per cm

  // Handle Potentiometer Change
  const handlePotChange = (e) => {
    const val = parseInt(e.target.value, 10);
    setPotentiometerVal(val);
    const v = ((val / 4095.0) * 3.3).toFixed(3);
    if (val % 256 === 0 || val === 0 || val === 4095) {
      appendSerialLog(`[ADC1_CH6] GPIO 34 Raw: ${val} | Voltage: ${v} V | Status: Sampled`, 'info');
    }
  };

  const [telemetrySaved, setTelemetrySaved] = useState(false);

  // Dispatch Telemetry to Laboratory Gradebook & Local Storage
  const handleRecordWokwiTelemetry = () => {
    const payload = {
      source: 'WokwiSimulationController (ESP32-WROOM-32)',
      timestamp: new Date().toLocaleTimeString(),
      potentiometerRaw: potentiometerVal,
      calculatedVoltageV: parseFloat(calculatedVoltage),
      temperatureC: temperature,
      humidityPct: humidity,
      ultrasonicDistanceCm: ultrasonicDistance,
      ultrasonicEchoUs,
      dipSwitches,
      activeRfidCard: PRESET_RFID_CARDS[selectedCardIdx]
    };

    try {
      if (typeof window !== 'undefined') {
        localStorage.setItem('voltcore_wokwi_telemetry', JSON.stringify(payload));
        window.dispatchEvent(new CustomEvent('voltcore:lab-telemetry', { detail: payload }));
      }
    } catch (_) {}

    appendSerialLog(`[TELEMETRY] Synced to Student Lab Record: ${calculatedVoltage}V | ${ultrasonicDistance}cm | ${temperature}°C`, 'success');
    setTelemetrySaved(true);
    setTimeout(() => setTelemetrySaved(false), 2000);
  };

  // Handle Virtual Pushbutton 0 (Boot Button / Manual Scan)
  const handleTriggerButton0 = async () => {
    setBtn0Pressed(true);
    setTimeout(() => setBtn0Pressed(false), 200);

    const card = PRESET_RFID_CARDS[selectedCardIdx];
    appendSerialLog(`[INTERRUPT] GPIO 0 FALLING_EDGE: Manual Card Scan Triggered!`, 'warn');
    appendSerialLog(`[MFRC522] 13.56 MHz RFID Frame: UID ${card.uid} (${card.name})`, 'info');

    try {
      const res = await fetch(`${serverUrl}/api/attendance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: card.roll,
          rfid_uid: card.uid,
          node_id: 'ESP32_VOLTCORE_IOT_01',
          rssi: -58
        })
      });

      if (res.ok) {
        const json = await res.json();
        appendSerialLog(`[HTTP 200] Access Granted: ${json.message || card.name} (+50 XP)`, 'success');
      } else {
        appendSerialLog(`[HTTP 404] Access Denied: Card UID ${card.uid} unregistered in laboratory access roster!`, 'error');
      }
    } catch (e) {
      appendSerialLog(`[SIMULATION] Card Tap Acknowledged: ${card.name} (${card.uid})`, 'success');
    }
  };

  // Handle DIP Switch Toggle
  const toggleDipSwitch = (swKey, label) => {
    setDipSwitches((prev) => {
      const nextVal = !prev[swKey];
      appendSerialLog(`[DIP_SWITCH] ${label} toggled to: ${nextVal ? 'ENABLED (HIGH)' : 'DISABLED (LOW)'}`, 'sys');
      return { ...prev, [swKey]: nextVal };
    });
  };

  // Clear Terminal
  const handleClearSerial = () => {
    setSerialLogs([{ id: Date.now(), ts: '00:00:00.000', text: '[TERMINAL BUFFER CLEARED]', type: 'sys' }]);
  };

  // Export Serial Logs to Text File
  const handleExportLogs = () => {
    const content = serialLogs.map((l) => `[${l.ts}] ${l.text}`).join('\n');
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `voltcore_serial_telemetry_${Date.now()}.log`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredLogs = serialLogs.filter((l) =>
    l.text.toLowerCase().includes(serialFilter.toLowerCase())
  );

  return (
    <div className="glass-card rounded-2xl border border-[#00F0B5]/30 shadow-2xl p-4 sm:p-6 font-mono text-xs text-slate-100 space-y-6">
      
      {/* HUD Header Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-[#00693E]/40 border border-[#00F0B5]/40 flex items-center justify-center text-[#00F0B5]">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-white text-sm">Wokwi Hardware Stimulus & Telemetry Deck</span>
              <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-[#00F0B5] border border-[#00F0B5]/30 text-[10px] font-bold">
                Active HIL
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Direct register injection: ESP32-WROOM-32 • SPI DMA • I2C Bus • 12-Bit ADC
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleRecordWokwiTelemetry}
            className={`px-3 py-1 rounded-xl border text-[11px] font-bold transition-all flex items-center gap-1.5 ${
              telemetrySaved
                ? 'bg-emerald-500/30 text-emerald-300 border-emerald-400'
                : 'bg-[#00693E]/30 text-[#00F0B5] border-[#00F0B5]/40 hover:bg-[#00693E]/50'
            }`}
            title="Dispatch telemetry to Student Laboratory Record & Gradebook"
          >
            <span>{telemetrySaved ? '✓ Recorded' : '📊 Record Telemetry'}</span>
          </button>
          <span className="text-[11px] text-slate-400">Target Core:</span>
          <span className="px-2 py-1 rounded bg-[#020813] border border-slate-700 text-[#00F0B5] font-bold">
            Xtensa LX6 (240 MHz)
          </span>
        </div>
      </div>

      {/* Grid of Interactive Hardware Stimuli */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Panel 1: Analog Potentiometer & Pushbuttons */}
        <div className="p-4 rounded-xl bg-[#020813] border border-[#00F0B5]/20 space-y-4">
          <div className="flex items-center justify-between">
            <span className="font-bold text-[#00F0B5] uppercase tracking-wider text-[11px]">
              1. Analog Potentiometer (ADC1)
            </span>
            <span className="text-amber-400 font-bold">{calculatedVoltage} V</span>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-[11px] text-slate-400">
              <span>GPIO 34 ADC Code:</span>
              <span className="text-white font-bold">{potentiometerVal} / 4095</span>
            </div>
            <input
              type="range"
              min="0"
              max="4095"
              value={potentiometerVal}
              onChange={handlePotChange}
              className="w-full h-2 bg-[#041026] rounded-lg appearance-none cursor-pointer accent-[#00F0B5]"
            />
            <div className="flex justify-between text-[9px] text-slate-500">
              <span>0.0V (GND)</span>
              <span>1.65V (MID)</span>
              <span>3.30V (VCC)</span>
            </div>
          </div>

          {/* Virtual Tactile Pushbuttons */}
          <div className="pt-3 border-t border-slate-800 space-y-2">
            <div className="text-[11px] text-slate-400 font-bold">Virtual Tactile Pushbuttons</div>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={handleTriggerButton0}
                className={`py-2.5 px-3 rounded-xl border text-center font-bold text-xs transition-all shadow-sm ${
                  btn0Pressed
                    ? 'bg-[#00F0B5] text-slate-950 scale-95 border-white'
                    : 'bg-[#041026] text-[#00F0B5] border-[#00F0B5]/30 hover:border-[#00F0B5]'
                }`}
              >
                🔘 GPIO 0 (Boot Tap)
              </button>

              <button
                type="button"
                onClick={() => {
                  setBtn4Pressed(true);
                  setTimeout(() => setBtn4Pressed(false), 200);
                  appendSerialLog('[INTERRUPT] GPIO 4 Sensor Tamper Switch Asserted!', 'warn');
                }}
                className={`py-2.5 px-3 rounded-xl border text-center font-bold text-xs transition-all shadow-sm ${
                  btn4Pressed
                    ? 'bg-amber-400 text-slate-950 scale-95 border-white'
                    : 'bg-[#041026] text-amber-400 border-amber-500/30 hover:border-amber-400'
                }`}
              >
                🔘 GPIO 4 (Tamper)
              </button>
            </div>
          </div>
        </div>

        {/* Panel 2: Sensor Telemetry Injection (DHT22 & HC-SR04) */}
        <div className="p-4 rounded-xl bg-[#020813] border border-[#00F0B5]/20 space-y-4">
          <div className="font-bold text-[#00F0B5] uppercase tracking-wider text-[11px]">
            2. Multi-Sensor Data Injection
          </div>

          {/* DHT22 Temperature & Humidity */}
          <div className="space-y-2">
            <div className="flex justify-between text-[11px]">
              <span className="text-slate-400">DHT22 Temp:</span>
              <span className="text-white font-bold">{temperature} °C</span>
            </div>
            <input
              type="range"
              min="-20"
              max="70"
              step="0.5"
              value={temperature}
              onChange={(e) => {
                const t = parseFloat(e.target.value);
                setTemperature(t);
                appendSerialLog(`[DHT22] Emulated Temp update: ${t} °C (Humidity: ${humidity}%)`, 'info');
              }}
              className="w-full h-1.5 bg-[#041026] rounded-lg appearance-none cursor-pointer accent-emerald-400"
            />
          </div>

          {/* HC-SR04 Ultrasonic Distance */}
          <div className="space-y-2">
            <div className="flex justify-between text-[11px]">
              <span className="text-slate-400">HC-SR04 Ultrasonic Distance:</span>
              <span className="text-cyan-300 font-bold">{ultrasonicDistance} cm ({ultrasonicEchoUs} µs)</span>
            </div>
            <input
              type="range"
              min="2"
              max="350"
              value={ultrasonicDistance}
              onChange={(e) => {
                const d = parseInt(e.target.value, 10);
                setUltrasonicDistance(d);
                if (d % 25 === 0) {
                  appendSerialLog(`[HC-SR04] Echo pulse width: ${Math.round(d * 58)} us => ${d} cm`, 'info');
                }
              }}
              className="w-full h-1.5 bg-[#041026] rounded-lg appearance-none cursor-pointer accent-cyan-400"
            />
          </div>

          {/* RFID Card Selector */}
          <div className="pt-2 border-t border-slate-800 space-y-1.5">
            <label className="text-[10px] text-slate-400 font-semibold block">Select Active RFID Card:</label>
            <select
              value={selectedCardIdx}
              onChange={(e) => setSelectedCardIdx(parseInt(e.target.value, 10))}
              className="w-full p-2 rounded-lg bg-[#041026] border border-slate-700 text-slate-200 text-xs focus:outline-none focus:border-[#00F0B5]"
            >
              {PRESET_RFID_CARDS.map((c, i) => (
                <option key={i} value={i}>
                  {c.name} ({c.uid})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Panel 3: 4-Bit DIP Switches & Bus State */}
        <div className="p-4 rounded-xl bg-[#020813] border border-[#00F0B5]/20 space-y-3">
          <div className="font-bold text-[#00F0B5] uppercase tracking-wider text-[11px]">
            3. Hardware DIP Switch Register
          </div>

          <div className="space-y-2">
            <div
              onClick={() => toggleDipSwitch('sw1_preempt', 'SW1 FreeRTOS Preemption')}
              className="p-2 rounded-lg bg-[#041026] border border-slate-800 flex items-center justify-between cursor-pointer hover:border-slate-700"
            >
              <span>SW1: FreeRTOS Preemptive</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${dipSwitches.sw1_preempt ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-800 text-slate-500'}`}>
                {dipSwitches.sw1_preempt ? 'ON' : 'OFF'}
              </span>
            </div>

            <div
              onClick={() => toggleDipSwitch('sw2_verbose', 'SW2 Verbose UART')}
              className="p-2 rounded-lg bg-[#041026] border border-slate-800 flex items-center justify-between cursor-pointer hover:border-slate-700"
            >
              <span>SW2: Verbose UART 115200</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${dipSwitches.sw2_verbose ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-800 text-slate-500'}`}>
                {dipSwitches.sw2_verbose ? 'ON' : 'OFF'}
              </span>
            </div>

            <div
              onClick={() => toggleDipSwitch('sw3_dma', 'SW3 SPI DMA Mode')}
              className="p-2 rounded-lg bg-[#041026] border border-slate-800 flex items-center justify-between cursor-pointer hover:border-slate-700"
            >
              <span>SW3: High-Speed SPI DMA</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${dipSwitches.sw3_dma ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-800 text-slate-500'}`}>
                {dipSwitches.sw3_dma ? 'ON' : 'OFF'}
              </span>
            </div>

            <div
              onClick={() => toggleDipSwitch('sw4_wifi_sta', 'SW4 Wi-Fi STA Engine')}
              className="p-2 rounded-lg bg-[#041026] border border-slate-800 flex items-center justify-between cursor-pointer hover:border-slate-700"
            >
              <span>SW4: 802.11 b/g/n Telemetry</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${dipSwitches.sw4_wifi_sta ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-800 text-slate-500'}`}>
                {dipSwitches.sw4_wifi_sta ? 'ON' : 'OFF'}
              </span>
            </div>
          </div>
        </div>

      </div>

      {/* Streaming UART Serial Terminal Console */}
      <div className="rounded-xl bg-[#020813] border border-[#00F0B5]/25 overflow-hidden">
        
        {/* Terminal Header Bar */}
        <div className="p-3 bg-[#041026] border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-3">
            <span className="flex h-2.5 w-2.5 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-400"></span>
            </span>
            <span className="font-bold text-white">ESP32 UART0 SERIAL MONITOR</span>
            <span className="text-slate-500">|</span>
            <select
              value={baudRate}
              onChange={(e) => setBaudRate(parseInt(e.target.value, 10))}
              className="bg-[#020813] border border-slate-700 rounded px-2 py-0.5 text-[#00F0B5] text-[11px] focus:outline-none"
            >
              <option value={9600}>9600 Baud</option>
              <option value={115200}>115200 Baud</option>
              <option value={921600}>921600 Baud</option>
            </select>
          </div>

          {/* Search Filter & Action Buttons */}
          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Filter logs (e.g. HTTP, RFID, ADC)..."
              value={serialFilter}
              onChange={(e) => setSerialFilter(e.target.value)}
              className="px-2.5 py-1 rounded bg-[#020813] border border-slate-700 text-slate-200 placeholder-slate-600 text-[11px] focus:outline-none focus:border-[#00F0B5]"
            />

            <button
              type="button"
              onClick={() => setAutoScroll(!autoScroll)}
              className={`px-2 py-1 rounded border text-[11px] ${
                autoScroll ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-[#020813] text-slate-400 border-slate-700'
              }`}
            >
              Auto-Scroll: {autoScroll ? 'ON' : 'OFF'}
            </button>

            <button
              type="button"
              onClick={handleClearSerial}
              className="px-2 py-1 rounded bg-[#020813] hover:bg-slate-800 border border-slate-700 text-slate-300 text-[11px]"
            >
              Clear
            </button>

            <button
              type="button"
              onClick={handleExportLogs}
              className="px-2.5 py-1 rounded bg-[#00693E]/40 hover:bg-[#00693E] border border-[#00F0B5]/30 text-[#00F0B5] hover:text-white text-[11px] transition-all"
            >
              Export .log
            </button>
          </div>
        </div>

        {/* Terminal Log Output Window */}
        <div className="h-64 overflow-y-auto p-4 space-y-1 font-mono text-[11px] select-text bg-[#020813]/90">
          {filteredLogs.map((log) => {
            let textColor = 'text-slate-300';
            if (log.type === 'warn') textColor = 'text-amber-400 font-bold';
            if (log.type === 'error') textColor = 'text-red-400 font-bold';
            if (log.type === 'success') textColor = 'text-[#00F0B5] font-bold';
            if (log.type === 'sys') textColor = 'text-cyan-400';

            return (
              <div key={log.id} className="flex gap-2 leading-relaxed hover:bg-[#041026] px-1 rounded">
                <span className="text-slate-500 select-none">[{log.ts}]</span>
                <span className={textColor}>{log.text}</span>
              </div>
            );
          })}
          <div ref={serialEndRef} />
        </div>

        {/* Interactive Virtual Serial Input Bar */}
        <form onSubmit={handleSendSerialCommand} className="p-2.5 bg-[#041026] border-t border-slate-800 flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-[#020813] border border-slate-700 text-[10px] text-slate-400">
            <span className={`h-2 w-2 rounded-full ${streamActive ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'}`}></span>
            <span>{streamActive ? 'SSE LIVE' : 'LOCAL'}</span>
          </div>
          <input
            type="text"
            value={serialInputText}
            onChange={(e) => setSerialInputText(e.target.value)}
            placeholder="Send UART serial string to virtual silicon (e.g. AT, ADC?, STATUS)..."
            className="flex-1 px-3 py-1.5 rounded-xl bg-[#020813] border border-slate-700 text-xs text-slate-200 focus:border-[#00F0B5] outline-none font-mono"
          />
          <button
            type="submit"
            className="px-4 py-1.5 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00F0B5] hover:brightness-110 text-[#020813] text-xs font-bold transition-all shadow-emerald-glow cursor-pointer"
          >
            TX Send
          </button>
        </form>

      </div>

    </div>
  );
}

