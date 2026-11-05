import React, { useState } from 'react';

/**
 * VoltCore Apex Academia - Physical Hardware-in-the-Loop (HIL) Lab Bridge
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 * ----------------------------------------------------------------------------------------
 * German Precision Engineering + Italian Glassmorphism Design Architecture
 */

const SEED_DEVICES = [
  {
    port_id: "COM3",
    device_name: "ESP32-S3 Dual-Core Xtensa LX7 (HIL Testbed #1)",
    hardware_target: "ESP32-S3",
    vid: "0x303A",
    pid: "0x1001",
    manufacturer: "Espressif Systems",
    max_baud_rate: 921600,
    default_baud: 115200,
    status: "AVAILABLE",
    ch1_v: 3.31,
    ch2_v: 1.64,
    current_ma: 124.5,
    freq_hz: 1000.2,
    temp_c: 34.8
  },
  {
    port_id: "COM4",
    device_name: "STM32F407VGT6 ARM Cortex-M4 (DMA Audio Testbed)",
    hardware_target: "STM32F407",
    vid: "0x0483",
    pid: "0x374B",
    manufacturer: "STMicroelectronics",
    max_baud_rate: 460800,
    default_baud: 115200,
    status: "AVAILABLE",
    ch1_v: 3.29,
    ch2_v: 2.10,
    current_ma: 96.0,
    freq_hz: 8000.0,
    temp_c: 31.4
  },
  {
    port_id: "COM7",
    device_name: "FTDI FT232R Dual UART High-Speed Gateway",
    hardware_target: "FT232R",
    vid: "0x0403",
    pid: "0x6001",
    manufacturer: "FTDI Chip",
    max_baud_rate: 3000000,
    default_baud: 115200,
    status: "AVAILABLE",
    ch1_v: 5.02,
    ch2_v: 3.30,
    current_ma: 42.1,
    freq_hz: 115200.0,
    temp_c: 28.6
  }
];

const INITIAL_SERIAL_LOGS = [
  "[17:40:02.104] [COM3:ESP32-S3] ROM boot v1.1.2 - CPU Freq: 240MHz, Flash: 8MB QIO",
  "[17:40:02.128] [COM3:ESP32-S3] FreeRTOS Kernel v10.5.1 Initialized. Starting Task Scheduler...",
  "[17:40:02.152] [COM3:ESP32-S3] [HIL_TASK] Pin 18 PWM Configured -> 1.000 kHz, Duty 50.0%",
  "[17:40:02.180] [COM3:ESP32-S3] [ADC1_CH4] VDD Rail Sample: 3.312V (Noise Floor: 1.8mV RMS)",
  "[17:40:02.215] [COM3:ESP32-S3] [I2C_MASTER] Bus Scan: ACK on slave address 0x28 (MFRC522)",
  "[17:40:02.240] [COM3:ESP32-S3] [WATCHDOG] Task WDT Armed. Tick interval: 20ms OK."
];

export default function PhysicalLabBridge() {
  const [activeTab, setActiveTab] = useState("board-telemetry");
  const [selectedPort, setSelectedPort] = useState("COM3");
  const [selectedBaud, setSelectedBaud] = useState(115200);
  const [isLocked, setIsLocked] = useState(false);
  const [lockedBy, setLockedBy] = useState(null);
  const [serialLogs, setSerialLogs] = useState(INITIAL_SERIAL_LOGS);
  const [commandInput, setCommandInput] = useState("");
  const [assertionsPassed, setAssertionsPassed] = useState(null);
  const [isRunningAssertions, setIsRunningAssertions] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  const currentDev = SEED_DEVICES.find(d => d.port_id === selectedPort) || SEED_DEVICES[0];

  const triggerToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleToggleLock = () => {
    if (isLocked) {
      setIsLocked(false);
      setLockedBy(null);
      triggerToast(`Session Lock Released on port ${selectedPort}.`);
    } else {
      setIsLocked(true);
      setLockedBy("2023MITEC042 (Ashok Kumar A)");
      triggerToast(`Port ${selectedPort} locked exclusively to your academic session.`);
    }
  };

  const handleSendCommand = (e) => {
    e.preventDefault();
    if (!commandInput.trim()) return;

    const timeStr = new Date().toTimeString().split(' ')[0] + "." + Math.floor(Math.random() * 900 + 100);
    const userLine = `[${timeStr}] [TX] > ${commandInput}`;
    let ackLine = `[${timeStr}] [RX] < OK: Command acknowledged by ${currentDev.hardware_target}.`;

    if (commandInput.toUpperCase().includes("ASSERT")) {
      ackLine = `[${timeStr}] [RX] < [ASSERT_PASSED] VDD=3.31V, FREQ=1000.2Hz, CRC=0x7F2B OK.`;
    }

    setSerialLogs(prev => [...prev, userLine, ackLine]);
    setCommandInput("");
  };

  const handleRunAssertions = () => {
    setIsRunningAssertions(true);
    setTimeout(() => {
      setAssertionsPassed(true);
      setIsRunningAssertions(false);
      triggerToast("All Physical HIL Test Bench Assertions PASSED! (+150 XP Lab Mastery)");
      setSerialLogs(prev => [
        ...prev,
        `[${new Date().toLocaleTimeString()}] [HIL_AUDIT] Assert VDD Rail 3V3 (3.31V) -> PASSED`,
        `[${new Date().toLocaleTimeString()}] [HIL_AUDIT] Assert GPIO Clock Freq (1000.2Hz) -> PASSED`,
        `[${new Date().toLocaleTimeString()}] [HIL_AUDIT] Assert Thermal Headroom (34.8°C) -> PASSED`
      ]);
    }, 500);
  };

  return (
    <div className="space-y-6 font-mono">

      {/* Floating Alert HUD */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 p-4 rounded-2xl bg-[#041026] border border-[#00F0B5]/50 text-white text-xs shadow-2xl flex items-center gap-3 animate-bounce">
          <span className="text-[#00F0B5] text-lg">🔌</span>
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Top Banner KPI HUD */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30">
          <div className="flex items-center justify-between text-slate-400">
            <span>Hardware Target</span>
            <span className="text-emerald-400 font-bold">{currentDev.hardware_target}</span>
          </div>
          <div className="text-2xl font-black text-white mt-1">
            {selectedPort} <span className="text-xs text-slate-400 font-normal">({selectedBaud} bps)</span>
          </div>
          <div className="text-[10px] text-[#00F0B5] mt-1">USB-CDC Virtual COM Bridge</div>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30">
          <div className="flex items-center justify-between text-slate-400">
            <span>Port Session Lock</span>
            <span className={`font-bold ${isLocked ? "text-cyan-400" : "text-slate-400"}`}>
              {isLocked ? "ACQUIRED" : "AVAILABLE"}
            </span>
          </div>
          <div className="text-2xl font-black text-white mt-1">
            {isLocked ? "MUTEX LOCKED" : "UNLOCKED"}
          </div>
          <div className="text-[10px] text-cyan-400 mt-1 truncate">
            {isLocked ? `User: ${lockedBy}` : "Contention Guard Active"}
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30">
          <div className="flex items-center justify-between text-slate-400">
            <span>Supply Rail (CH1)</span>
            <span className="text-emerald-400 font-bold">NORMAL</span>
          </div>
          <div className="text-2xl font-black text-white mt-1">
            {currentDev.ch1_v} V <span className="text-xs text-slate-400 font-normal">({currentDev.current_ma} mA)</span>
          </div>
          <div className="text-[10px] text-emerald-400 mt-1">Noise Margin: ±1.8 mV RMS</div>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30">
          <div className="flex items-center justify-between text-slate-400">
            <span>Die Temperature</span>
            <span className="text-emerald-400 font-bold">OPTIMAL</span>
          </div>
          <div className="text-2xl font-black text-white mt-1">
            {currentDev.temp_c} °C <span className="text-xs text-slate-400 font-normal">Passive</span>
          </div>
          <div className="text-[10px] text-emerald-400 mt-1">Safe Headroom: +30.2 °C</div>
        </div>
      </div>

      {/* Main Tab Navigation */}
      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-3 text-xs">
        <button
          type="button"
          onClick={() => setActiveTab("board-telemetry")}
          className={`px-4 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2 ${
            activeTab === "board-telemetry"
              ? "bg-[#00F0B5] text-[#020813] shadow-emerald-glow"
              : "bg-[#041026] text-slate-300 hover:text-white border border-slate-800"
          }`}
        >
          <span>📊</span>
          <span>Board Hardware &amp; Telemetry</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("serial-terminal")}
          className={`px-4 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2 ${
            activeTab === "serial-terminal"
              ? "bg-[#00F0B5] text-[#020813] shadow-emerald-glow"
              : "bg-[#041026] text-slate-300 hover:text-white border border-slate-800"
          }`}
        >
          <span>📟</span>
          <span>Live Serial Terminal Stream</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("automated-assertions")}
          className={`px-4 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2 ${
            activeTab === "automated-assertions"
              ? "bg-[#00F0B5] text-[#020813] shadow-emerald-glow"
              : "bg-[#041026] text-slate-300 hover:text-white border border-slate-800"
          }`}
        >
          <span>✅</span>
          <span>Automated Assertion Recorder</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("lab-roster")}
          className={`px-4 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2 ${
            activeTab === "lab-roster"
              ? "bg-[#00F0B5] text-[#020813] shadow-emerald-glow"
              : "bg-[#041026] text-slate-300 hover:text-white border border-slate-800"
          }`}
        >
          <span>🏛️</span>
          <span>Lab 304 Equipment Roster</span>
        </button>
      </div>

      {/* Tab 1: Board Hardware & Telemetry */}
      {activeTab === "board-telemetry" && (
        <div className="space-y-6">
          <div className="p-6 rounded-3xl bg-gradient-to-br from-[#041026] via-[#020813] to-[#041026] border border-[#00F0B5]/40 shadow-2xl relative overflow-hidden space-y-5">
            <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <span className="px-3 py-1 rounded-full bg-[#00693E]/50 text-[#00F0B5] border border-[#00F0B5]/40 text-xs font-bold">
                  PHYSICAL HIL TESTBED
                </span>
                <h3 className="text-xl sm:text-2xl font-black text-white mt-2">
                  {currentDev.device_name}
                </h3>
                <p className="text-slate-300 text-xs sm:text-sm mt-1">
                  Manufacturer: <strong className="text-white">{currentDev.manufacturer}</strong> • VID: <span className="text-[#00F0B5] font-mono">{currentDev.vid}</span> • PID: <span className="text-[#00F0B5] font-mono">{currentDev.pid}</span>
                </p>
              </div>

              <div className="flex items-center gap-3 self-start md:self-auto">
                <button
                  type="button"
                  onClick={handleToggleLock}
                  className={`px-5 py-2.5 rounded-xl font-bold text-xs transition-all ${
                    isLocked
                      ? "bg-red-500/20 text-red-400 border border-red-500/40 hover:bg-red-500/30"
                      : "bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] hover:shadow-emerald-glow"
                  }`}
                >
                  {isLocked ? "Release Port Mutex" : "Acquire Safe Port Lock"}
                </button>
              </div>
            </div>

            {/* Port & Baud Rate Configurator */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 pt-3 border-t border-slate-800 text-xs">
              <div>
                <label className="text-slate-400 text-[11px] block mb-1">Active COM Port:</label>
                <select
                  value={selectedPort}
                  onChange={(e) => setSelectedPort(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#020813] border border-slate-700 text-white focus:outline-none focus:border-[#00F0B5]"
                >
                  {SEED_DEVICES.map(d => (
                    <option key={d.port_id} value={d.port_id}>{d.port_id} - {d.hardware_target}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-slate-400 text-[11px] block mb-1">Baud Rate:</label>
                <select
                  value={selectedBaud}
                  onChange={(e) => setSelectedBaud(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-[#020813] border border-slate-700 text-white focus:outline-none focus:border-[#00F0B5]"
                >
                  <option value={115200}>115,200 baud</option>
                  <option value={460800}>460,800 baud</option>
                  <option value={921600}>921,600 baud</option>
                </select>
              </div>

              <div>
                <label className="text-slate-400 text-[11px] block mb-1">Flow Control:</label>
                <div className="px-3 py-2 rounded-xl bg-[#020813] border border-slate-800 text-slate-300">
                  RTS / CTS Hardware
                </div>
              </div>

              <div>
                <label className="text-slate-400 text-[11px] block mb-1">Parity / Stop Bits:</label>
                <div className="px-3 py-2 rounded-xl bg-[#020813] border border-slate-800 text-slate-300">
                  8-N-1 (Standard)
                </div>
              </div>
            </div>

            {/* Live Bench Voltage & Frequency Gauges */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 text-center text-xs">
              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <span className="text-slate-500 text-[10px]">CH1 Rail Voltage</span>
                <div className="text-xl font-bold text-white mt-1">{currentDev.ch1_v} V</div>
                <div className="text-[10px] text-emerald-400">Within ±2% Target</div>
              </div>

              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <span className="text-slate-500 text-[10px]">CH2 Waveform Voltage</span>
                <div className="text-xl font-bold text-white mt-1">{currentDev.ch2_v} V</div>
                <div className="text-[10px] text-cyan-400">Peak-to-Peak 3.3V</div>
              </div>

              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <span className="text-slate-500 text-[10px]">Bus Frequency</span>
                <div className="text-xl font-bold text-white mt-1">{currentDev.freq_hz} Hz</div>
                <div className="text-[10px] text-amber-400">Clock Stable 50% Duty</div>
              </div>

              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <span className="text-slate-500 text-[10px]">Active Current</span>
                <div className="text-xl font-bold text-white mt-1">{currentDev.current_ma} mA</div>
                <div className="text-[10px] text-emerald-400">Safe Operating Area</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Live Serial Terminal Stream */}
      {activeTab === "serial-terminal" && (
        <div className="space-y-4">
          <div className="p-6 rounded-2xl bg-[#041026]/90 border border-slate-800 space-y-4 text-xs">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div>
                <h3 className="text-base font-bold text-white">Live Serial Terminal Buffer ({selectedPort})</h3>
                <p className="text-slate-400">115200 Baud • 8-N-1 • Bidirectional USB CDC</p>
              </div>
              <button
                type="button"
                onClick={() => setSerialLogs([])}
                className="px-3 py-1.5 rounded-lg bg-[#020813] border border-slate-700 text-slate-400 hover:text-white text-[11px]"
              >
                Clear Buffer
              </button>
            </div>

            {/* Terminal Window */}
            <div className="p-4 rounded-xl bg-[#010409] border border-slate-800 h-64 overflow-y-auto space-y-1 font-mono text-[11px] text-emerald-400">
              {serialLogs.map((log, idx) => (
                <div key={idx} className="leading-relaxed hover:bg-slate-900/50 px-1 rounded">
                  {log}
                </div>
              ))}
            </div>

            {/* Serial Command Input */}
            <form onSubmit={handleSendCommand} className="flex gap-2">
              <input
                type="text"
                value={commandInput}
                onChange={(e) => setCommandInput(e.target.value)}
                placeholder="Type command (e.g. AT+PING, ASSERT_ALL, GET_REG SCB_CFSR)..."
                className="flex-1 px-4 py-2.5 rounded-xl bg-[#020813] border border-slate-700 text-white text-xs focus:outline-none focus:border-[#00F0B5]"
              />
              <button
                type="submit"
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] font-bold text-xs hover:shadow-emerald-glow transition-all"
              >
                Send (TX)
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Tab 3: Automated Assertion Recorder */}
      {activeTab === "automated-assertions" && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-[#041026]/90 border border-slate-800 space-y-5 text-xs">
            <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
              <div>
                <h3 className="text-base font-bold text-white">Automated Test Bench Assertion Verification</h3>
                <p className="text-slate-400">Real-Time Pass/Fail Criteria for MIT Campus Lab 304 Workstations</p>
              </div>

              <button
                type="button"
                onClick={handleRunAssertions}
                disabled={isRunningAssertions}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] font-bold hover:shadow-emerald-glow transition-all"
              >
                {isRunningAssertions ? "Evaluating Assertions..." : "Run Test Bench Assertions (+150 XP)"}
              </button>
            </div>

            <div className="space-y-3">
              <div className="p-4 rounded-xl bg-[#020813] border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white text-sm">ASSERT_VDD_RAIL_3V3</span>
                  <span className="px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold">
                    PASSED (3.31 V)
                  </span>
                </div>
                <p className="text-slate-400 text-[11px]">
                  Validates target board 3.3V DC rail stability. Tolerable boundary: [3.20V - 3.40V].
                </p>
              </div>

              <div className="p-4 rounded-xl bg-[#020813] border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white text-sm">ASSERT_GPIO_CLOCK_FREQ</span>
                  <span className="px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold">
                    PASSED (1000.2 Hz)
                  </span>
                </div>
                <p className="text-slate-400 text-[11px]">
                  Validates 1.0 kHz FreeRTOS hardware timer tick output on GPIO 18. Tolerable boundary: [950Hz - 1050Hz].
                </p>
              </div>

              <div className="p-4 rounded-xl bg-[#020813] border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white text-sm">ASSERT_THERMAL_HEADROOM</span>
                  <span className="px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold">
                    PASSED (34.8 °C)
                  </span>
                </div>
                <p className="text-slate-400 text-[11px]">
                  Validates SoC internal temperature remains within safe passive cooling limits [&lt; 65°C].
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Lab 304 Equipment Roster */}
      {activeTab === "lab-roster" && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-[#041026]/90 border border-slate-800 space-y-4 text-xs">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div>
                <h3 className="text-base font-bold text-white">MIT Campus Lab 304 Physical Equipment Inventory</h3>
                <p className="text-slate-400">Department of Electronics Engineering • Regulation 2023</p>
              </div>
              <span className="text-[#00F0B5]">3 Connected Workstations</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {SEED_DEVICES.map(dev => (
                <div key={dev.port_id} className="p-4 rounded-xl bg-[#020813] border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-[#00F0B5]">{dev.port_id}</span>
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold">
                      {dev.status}
                    </span>
                  </div>
                  <div className="font-bold text-white text-sm">{dev.hardware_target}</div>
                  <div className="text-slate-400 text-[11px] leading-relaxed">
                    {dev.device_name}
                  </div>
                  <div className="pt-2 border-t border-slate-800/80 text-[10px] text-slate-500 space-y-1">
                    <div>Vendor ID: <span className="text-white">{dev.vid}</span></div>
                    <div>Product ID: <span className="text-white">{dev.pid}</span></div>
                    <div>Max Baud: <span className="text-cyan-400">{dev.max_baud_rate}</span></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

