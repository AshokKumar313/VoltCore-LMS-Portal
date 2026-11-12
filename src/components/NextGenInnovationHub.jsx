import React, { useState } from 'react';

/**
 * VoltCore Apex Academia - Next-Gen Innovations & Autonomous AI Academic Agent
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 * ----------------------------------------------------------------------------------------
 * German Precision Engineering + Italian Glassmorphism Design Architecture
 */

const SEED_RECOMMENDATION = {
  curriculum_mastery_pct: 70.0,
  completed_count: 7,
  total_modules: 10,
  next_best_module: {
    id: "8-advanced-rtos-dma",
    title: "Advanced RTOS DMA & Zero-Copy Buffering",
    category: "High-Performance Firmware",
    semester: 6,
    credits: 4,
    xp_reward: 180,
    prerequisites: ["6-embedded-rtos"],
    rationale: "Prerequisites satisfied (6-embedded-rtos). Recommended next step for Semester 6 under AU R2023 regulations. Unlocks 4 academic credits and +180 XP."
  },
  unlocked_modules: [
    {
      id: "8-advanced-rtos-dma",
      title: "Advanced RTOS DMA & Zero-Copy Buffering",
      semester: 6,
      credits: 4,
      xp_reward: 180
    },
    {
      id: "2-automotive-edge",
      title: "Automotive Edge Computing & CAN-FD (ISO 26262)",
      semester: 6,
      credits: 3,
      xp_reward: 170
    },
    {
      id: "10-gate-ece-instrumentation",
      title: "GATE ECE Precision Instrumentation",
      semester: 6,
      credits: 3,
      xp_reward: 140
    }
  ]
};

const SEED_CAREER_TRACKS = [
  {
    track_id: "EMBEDDED_FIRMWARE_ARCHITECT",
    title: "Embedded Firmware Architect & Systems Engineer",
    fit_score: 97.8,
    target_companies: ["Qualcomm", "Texas Instruments", "Bosch", "Intel", "NXP Semiconductors"],
    core_domains: ["FreeRTOS", "DMA", "Bare-Metal C/C++", "Device Drivers"],
    median_salary_range: "₹12.0 LPA - ₹28.0 LPA",
    hub_locations: ["Bengaluru", "Chennai (OMR / Guindy)", "Hyderabad"],
    recommended_nptel: ["Embedded System Design with ARM Cortex-M", "Real Time Operating Systems"]
  },
  {
    track_id: "AUTOMOTIVE_AUTOSAR_SPECIALIST",
    title: "Automotive Systems & AUTOSAR ECU Engineer",
    fit_score: 91.2,
    target_companies: ["Continental", "Tata Elxsi", "Mercedes-Benz R&D", "KPIT Technologies"],
    core_domains: ["CAN-FD", "AUTOSAR Classic/Adaptive", "ISO 26262 Functional Safety"],
    median_salary_range: "₹11.5 LPA - ₹26.0 LPA",
    hub_locations: ["Chennai (Sriperumbudur / Ambattur)", "Pune", "Bengaluru"],
    recommended_nptel: ["Automotive Electrical Systems", "Industrial Automation & Control"]
  },
  {
    track_id: "EDGE_AI_ROBOTICS_SPECIALIST",
    title: "Edge AI & Mission-Critical Autonomous Systems",
    fit_score: 88.5,
    target_companies: ["Bharat Electronics (BEL)", "DRDO", "DJI Enterprise", "Ather Energy"],
    core_domains: ["TinyML", "TFLite Micro", "MAVLink", "EKF Flight Control"],
    median_salary_range: "₹13.0 LPA - ₹30.0 LPA",
    hub_locations: ["Bengaluru", "Chennai (IIT-M Research Park)", "Hyderabad"],
    recommended_nptel: ["Deep Learning for Edge AI", "Robotics & Autonomous Systems"]
  },
  {
    track_id: "VLSI_VERIFICATION_ENGINEER",
    title: "Digital RTL & VLSI Verification Engineer",
    fit_score: 84.0,
    target_companies: ["Synopsys", "Cadence Design", "NVIDIA", "AMD", "Arm India"],
    core_domains: ["SystemVerilog", "UVM", "RISC-V Architecture", "Static Timing Analysis"],
    median_salary_range: "₹14.0 LPA - ₹32.0 LPA",
    hub_locations: ["Bengaluru", "Noida", "Hyderabad", "Chennai"],
    recommended_nptel: ["VLSI Design Verification & Testing", "Computer Architecture"]
  }
];

const QUICK_DIAGNOSTIC_PRESETS = [
  { label: "FreeRTOS WDT Starvation", query: "FreeRTOS task watchdog timeout triggered in tight telemetry loop", hw: "ESP32-S3" },
  { label: "DMA FIFO Bus Contention", query: "DMA stream FIFO underrun during high speed SPI audio buffer transfer", hw: "STM32F407" },
  { label: "I2C Bus Address NACK", query: "I2C peripheral not acknowledging slave address 0x28 on bus scan", hw: "ESP32-S3" },
  { label: "WiFi TX Brownout Reset", query: "Target board reboots with brownout detector message during WiFi connect", hw: "ESP32-S3" }
];

export default function NextGenInnovationHub() {
  const [activeTab, setActiveTab] = useState("autonomous-agent");
  const [symptomInput, setSymptomInput] = useState("");
  const [selectedHardware, setSelectedHardware] = useState("ESP32-S3");
  const [diagnosticResult, setDiagnosticResult] = useState(null);
  const [isDiagnosing, setIsDiagnosing] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);
  const [copiedCode, setCopiedCode] = useState(false);

  const triggerToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleRunDiagnostic = (queryToUse, hwToUse) => {
    const q = queryToUse || symptomInput;
    const hw = hwToUse || selectedHardware;

    if (!q.trim()) {
      alert("Please enter firmware error symptoms or select a diagnostic preset.");
      return;
    }

    setIsDiagnosing(true);
    // Simulating rapid sub-50ms native diagnostic response
    setTimeout(() => {
      let result = null;
      const lower = q.toLowerCase();

      if (lower.includes("watchdog") || lower.includes("wdt") || lower.includes("starvation") || lower.includes("tight loop")) {
        result = {
          fault_code: "TASK_WATCHDOG_TIMEOUT",
          title: "FreeRTOS Task Watchdog Timer Triggered (Task Starvation)",
          confidence: 97.2,
          hardware_target: hw,
          root_cause: "A high-priority telemetry loop executed without yielding CPU control to the FreeRTOS scheduler, starving the IDLE task and tripping the Hardware Watchdog Timer (WDT).",
          hardware_check: "Connect logic analyzer to GPIO debug pin to observe task execution duty cycle. Confirm IDLE task tick frequency.",
          registers_to_inspect: ["TIMG_WDTCONFIG0_REG", "CP0_PC", "EPC1"],
          actionable_fix: `// FreeRTOS Task Starvation Fix
void vTelemetryTask(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(20); // 50 Hz

    for (;;) {
        sample_oscilloscope_dma();
        transmit_telemetry_packet();

        // FIX: Yield execution to allow IDLE task WDT reset
        vTaskDelayUntil(&xLastWakeTime, xFrequency);
    }
}`
        };
      } else if (lower.includes("dma") || lower.includes("fifo") || lower.includes("underrun") || lower.includes("audio")) {
        result = {
          fault_code: "DMA_FIFO_ERROR",
          title: "DMA Stream FIFO Contention / Unaligned Memory Allocation",
          confidence: 95.8,
          hardware_target: hw,
          root_cause: "Direct Memory Access source buffer is not 32-bit word aligned or memory resides in cached tightly coupled RAM (CCM), causing DMA bus matrix stall.",
          hardware_check: "Probe SPI clock line on 100MHz+ oscilloscope. Verify lack of clock stretching or phase jitter.",
          registers_to_inspect: ["DMA_SxFCR", "DMA_SxCR", "SCB_CFSR_BFSR"],
          actionable_fix: `// DMA Memory Alignment Fix
// Force 4-byte alignment and place in non-cached SRAM1
__attribute__((section(".sram1"), aligned(4)))
static uint32_t dma_ping_pong_buffer[2][1024];

void configure_dma_stream(void) {
    DMA2_Stream0->CR &= ~DMA_SxCR_EN;
    DMA2_Stream0->FCR |= DMA_SxFCR_DMDIS | DMA_SxFCR_FTH_1; // Full FIFO
    DMA2_Stream0->M0AR = (uint32_t)&dma_ping_pong_buffer[0];
    DMA2_Stream0->CR |= DMA_SxCR_TCIE | DMA_SxCR_EN;
}`
        };
      } else if (lower.includes("nack") || lower.includes("i2c") || lower.includes("address") || lower.includes("0x28")) {
        result = {
          fault_code: "I2C_NACK_ADDR",
          title: "I2C Peripheral Address NACK / Missing Pull-up Resistor",
          confidence: 98.4,
          hardware_target: hw,
          root_cause: "Slave peripheral did not acknowledge the 7-bit target address on the 9th clock cycle, or bus float occurred due to missing external pull-up resistors.",
          hardware_check: "Measure resting voltage on SDA (GPIO 21) and SCL (GPIO 22). It must read 3.3VDC (+/-0.1V). If reading <2.5V, install 4.7kΩ pull-ups.",
          registers_to_inspect: ["I2C_SR1", "I2C_SR2", "GPIO_IN_REG"],
          actionable_fix: `// I2C Recovery & Pin Check
#define SDA_PIN 21
#define SCL_PIN 22

void i2c_bus_recovery(void) {
    gpio_set_direction(SDA_PIN, GPIO_MODE_INPUT_PULLUP);
    gpio_set_direction(SCL_PIN, GPIO_MODE_INPUT_PULLUP);
    
    // Toggle SCL 9 times to release stuck slave state machine
    for (int i = 0; i < 9; i++) {
        gpio_set_level(SCL_PIN, 0);
        esp_rom_delay_us(5);
        gpio_set_level(SCL_PIN, 1);
        esp_rom_delay_us(5);
    }
}`
        };
      } else {
        result = {
          fault_code: "BROWN_OUT_DETECTED",
          title: "ESP32 Brownout Reset During High-Current RF Burst",
          confidence: 94.6,
          hardware_target: hw,
          root_cause: "Peak RF amplifier draw during Wi-Fi beacon bursts exceeded instantaneous supply capability, causing VDD rail to drop below the 2.7V threshold.",
          hardware_check: "Probe 3.3V rail at ESP32 pin with AC coupling on oscilloscope. Trigger on falling edge < 2.8V.",
          registers_to_inspect: ["RTC_CNTL_BROWN_OUT_REG", "RTC_CNTL_STATE0_REG"],
          actionable_fix: `// Decoupling & Brownout Configuration
// 1. Hardware: Solder a 10µF tantalum + 100nF ceramic capacitor across 3V3 and GND.
// 2. Software: Fine-tune brownout threshold if necessary:
#include "soc/rtc_cntl_reg.h"

void configure_brownout_protection(void) {
    // Enable brownout detector with 2.43V threshold (Level 0)
    REG_WRITE(RTC_CNTL_BROWN_OUT_REG, 
        RTC_CNTL_BROWN_OUT_ENA | 
        RTC_CNTL_BROWN_OUT_PD_RF_ENA | 
        (0 << RTC_CNTL_BROWN_OUT_THRES_S));
}`
        };
      }

      setDiagnosticResult(result);
      setIsDiagnosing(false);
      triggerToast("AI Lab Diagnostic Complete! +150 XP Lab Mastery Earned");
    }, 120);
  };

  const handleCopyCode = (code) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  return (
    <div className="space-y-6 font-mono">

      {/* Floating Toast HUD */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 p-4 rounded-2xl bg-[#041026] border border-[#00F0B5]/50 text-white text-xs shadow-2xl flex items-center gap-3 animate-bounce">
          <span className="text-[#00F0B5] text-lg">⚡</span>
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Top Banner KPI HUD */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30">
          <div className="flex items-center justify-between text-slate-400">
            <span>Autonomous Agent</span>
            <span className="text-emerald-400 font-bold">ONLINE</span>
          </div>
          <div className="text-2xl font-black text-white mt-1">
            AU R2023 <span className="text-xs text-slate-400 font-normal">Compliant</span>
          </div>
          <div className="text-[10px] text-[#00F0B5] mt-1">Pedagogical Prerequisite Engine</div>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30">
          <div className="flex items-center justify-between text-slate-400">
            <span>Curriculum Mastery</span>
            <span className="text-cyan-400 font-bold">{SEED_RECOMMENDATION.curriculum_mastery_pct}%</span>
          </div>
          <div className="text-2xl font-black text-white mt-1">
            {SEED_RECOMMENDATION.completed_count} / {SEED_RECOMMENDATION.total_modules} <span className="text-xs text-slate-400 font-normal">Modules</span>
          </div>
          <div className="text-[10px] text-cyan-400 mt-1">3 Modules Ready to Unlock</div>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30">
          <div className="flex items-center justify-between text-slate-400">
            <span>Top Career Pathway</span>
            <span className="text-amber-400 font-bold">97.8% FIT</span>
          </div>
          <div className="text-base font-bold text-white mt-1 truncate">
            Embedded Firmware
          </div>
          <div className="text-[10px] text-amber-400 mt-1">Tier-1 Core Hardware Trajectory</div>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/30">
          <div className="flex items-center justify-between text-slate-400">
            <span>Lab 304 Digital Twin</span>
            <span className="text-emerald-400 font-bold">SYNCHRONIZED</span>
          </div>
          <div className="text-2xl font-black text-white mt-1">
            23.8°C <span className="text-xs text-slate-400 font-normal">Passive Eco</span>
          </div>
          <div className="text-[10px] text-emerald-400 mt-1">3 Active HIL Nodes Connected</div>
        </div>
      </div>

      {/* Main Tab Navigation */}
      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-3 text-xs">
        <button
          type="button"
          onClick={() => setActiveTab("autonomous-agent")}
          className={`px-4 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2 ${
            activeTab === "autonomous-agent"
              ? "bg-[#00F0B5] text-[#020813] shadow-emerald-glow"
              : "bg-[#041026] text-slate-300 hover:text-white border border-slate-800"
          }`}
        >
          <span>🤖</span>
          <span>Autonomous AI Academic Agent</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("lab-diagnostics")}
          className={`px-4 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2 ${
            activeTab === "lab-diagnostics"
              ? "bg-[#00F0B5] text-[#020813] shadow-emerald-glow"
              : "bg-[#041026] text-slate-300 hover:text-white border border-slate-800"
          }`}
        >
          <span>🔬</span>
          <span>Lab Troubleshooting Engine</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("career-pathways")}
          className={`px-4 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2 ${
            activeTab === "career-pathways"
              ? "bg-[#00F0B5] text-[#020813] shadow-emerald-glow"
              : "bg-[#041026] text-slate-300 hover:text-white border border-slate-800"
          }`}
        >
          <span>🚀</span>
          <span>Predictive Career Pathways</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("digital-twin")}
          className={`px-4 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2 ${
            activeTab === "digital-twin"
              ? "bg-[#00F0B5] text-[#020813] shadow-emerald-glow"
              : "bg-[#041026] text-slate-300 hover:text-white border border-slate-800"
          }`}
        >
          <span>🌐</span>
          <span>MIT Campus Digital Twin</span>
        </button>
      </div>

      {/* Tab 1: Autonomous AI Academic Agent */}
      {activeTab === "autonomous-agent" && (
        <div className="space-y-6">
          {/* Spotlight Next Best Action Card */}
          <div className="p-6 rounded-3xl bg-gradient-to-br from-[#041026] via-[#020813] to-[#041026] border border-[#00F0B5]/40 shadow-2xl relative overflow-hidden">
            <div className="relative z-10 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <span className="px-3 py-1 rounded-full bg-[#00693E]/50 text-[#00F0B5] border border-[#00F0B5]/40 text-xs font-bold">
                  NEXT BEST ACADEMIC MODULE • SEMESTER 6
                </span>
                <span className="text-amber-400 font-bold text-xs">
                  Yields +{SEED_RECOMMENDATION.next_best_module.xp_reward} XP &amp; {SEED_RECOMMENDATION.next_best_module.credits} Credits
                </span>
              </div>

              <div>
                <h3 className="text-xl sm:text-2xl font-black text-white">
                  {SEED_RECOMMENDATION.next_best_module.title}
                </h3>
                <p className="text-slate-300 text-xs sm:text-sm mt-1 leading-relaxed">
                  {SEED_RECOMMENDATION.next_best_module.rationale}
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-3 pt-2">
                <a
                  href={`/course-hub?module=${SEED_RECOMMENDATION.next_best_module.id}`}
                  className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] font-bold text-xs hover:shadow-emerald-glow transition-all"
                >
                  Launch Module Workspace →
                </a>
                <button
                  type="button"
                  onClick={() => triggerToast("Prerequisite Tree Verified: FreeRTOS Core Cleared with 91.5% Grade.")}
                  className="px-4 py-2.5 rounded-xl bg-[#020813] border border-slate-700 text-slate-300 hover:text-white text-xs font-bold"
                >
                  Verify Prerequisites Tree
                </button>
              </div>
            </div>

            <div className="absolute right-0 bottom-0 w-72 h-72 bg-gradient-to-tl from-[#00F0B5]/10 to-transparent rounded-full blur-2xl pointer-events-none"></div>
          </div>

          {/* Unlocked Modules Grid */}
          <div className="p-6 rounded-2xl bg-[#041026]/90 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white">Unlocked Academic Modules (AU R2023)</h3>
              <span className="text-xs text-slate-400">Ready to Enroll</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              {SEED_RECOMMENDATION.unlocked_modules.map((m) => (
                <div key={m.id} className="p-4 rounded-xl bg-[#020813] border border-slate-800 space-y-2 hover:border-[#00F0B5]/40 transition-colors">
                  <div className="flex items-center justify-between text-slate-400">
                    <span>Semester {m.semester}</span>
                    <span className="text-emerald-400 font-bold">{m.credits} Credits</span>
                  </div>
                  <div className="text-sm font-bold text-white">{m.title}</div>
                  <div className="flex items-center justify-between pt-2 border-t border-slate-800/80">
                    <span className="text-[#00F0B5]">+{m.xp_reward} XP</span>
                    <a href={`/course-hub?module=${m.id}`} className="text-slate-400 hover:text-white text-[11px] underline">
                      Explore →
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Lab Troubleshooting Engine */}
      {activeTab === "lab-diagnostics" && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-[#041026]/90 border border-slate-800 space-y-4">
            <div>
              <h3 className="text-base font-bold text-white">Automated Firmware &amp; Hardware Fault Diagnostic</h3>
              <p className="text-xs text-slate-400 mt-1">
                Enter your serial console error logs, hardware symptoms, or select a laboratory preset below.
              </p>
            </div>

            {/* Quick Diagnostic Presets */}
            <div className="flex flex-wrap gap-2 text-xs">
              <span className="text-slate-500 py-1 font-bold">Quick Presets:</span>
              {QUICK_DIAGNOSTIC_PRESETS.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setSymptomInput(p.query);
                    setSelectedHardware(p.hw);
                    handleRunDiagnostic(p.query, p.hw);
                  }}
                  className="px-3 py-1 rounded-lg bg-[#020813] border border-slate-800 text-slate-300 hover:text-[#00F0B5] hover:border-[#00F0B5]/50 transition-all text-[11px]"
                >
                  {p.label}
                </button>
              ))}
            </div>

            {/* Diagnostic Query Input */}
            <div className="space-y-3">
              <div className="flex flex-col sm:flex-row gap-3">
                <input
                  type="text"
                  value={symptomInput}
                  onChange={(e) => setSymptomInput(e.target.value)}
                  placeholder="e.g. FreeRTOS task watchdog timeout or I2C peripheral NACK on GPIO 21"
                  className="flex-1 px-4 py-2.5 rounded-xl bg-[#020813] border border-slate-700 text-white text-xs focus:outline-none focus:border-[#00F0B5]"
                />
                <select
                  value={selectedHardware}
                  onChange={(e) => setSelectedHardware(e.target.value)}
                  className="px-3 py-2.5 rounded-xl bg-[#020813] border border-slate-700 text-white text-xs focus:outline-none focus:border-[#00F0B5]"
                >
                  <option value="ESP32-S3">ESP32-S3 (Xtensa LX7)</option>
                  <option value="STM32F407">STM32F407 (ARM Cortex-M4)</option>
                  <option value="Wokwi-Virtual">Wokwi Virtual Microcontroller</option>
                </select>
                <button
                  type="button"
                  onClick={() => handleRunDiagnostic(null, null)}
                  disabled={isDiagnosing}
                  className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] font-bold text-xs hover:shadow-emerald-glow transition-all whitespace-nowrap"
                >
                  {isDiagnosing ? "Diagnosing..." : "Run AI Diagnosis (+150 XP)"}
                </button>
              </div>
            </div>

            {/* Diagnostic Result Card */}
            {diagnosticResult && (
              <div className="p-5 rounded-2xl bg-[#020813] border border-[#00F0B5]/40 space-y-4 animate-fadeIn">
                <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
                  <div>
                    <span className="px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold">
                      CONFIDENCE: {diagnosticResult.confidence}%
                    </span>
                    <h4 className="text-base font-bold text-white mt-1">
                      {diagnosticResult.title}
                    </h4>
                  </div>
                  <div className="text-right text-[11px] text-slate-400">
                    Target: <strong className="text-emerald-400">{diagnosticResult.hardware_target}</strong>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div className="p-4 rounded-xl bg-[#041026] border border-slate-800 space-y-2">
                    <div className="text-slate-400 font-bold">Root Cause Analysis:</div>
                    <p className="text-slate-200 leading-relaxed text-[11px]">
                      {diagnosticResult.root_cause}
                    </p>
                  </div>

                  <div className="p-4 rounded-xl bg-[#041026] border border-slate-800 space-y-2">
                    <div className="text-cyan-400 font-bold">Bench Test &amp; Scope Verification:</div>
                    <p className="text-slate-200 leading-relaxed text-[11px]">
                      {diagnosticResult.hardware_check}
                    </p>
                    <div className="text-[10px] text-slate-500 pt-1">
                      Registers to Inspect: <span className="text-cyan-300 font-mono">{diagnosticResult.registers_to_inspect.join(", ")}</span>
                    </div>
                  </div>
                </div>

                {/* Code Solution */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400 font-bold">Verified Firmware Solution:</span>
                    <button
                      type="button"
                      onClick={() => handleCopyCode(diagnosticResult.actionable_fix)}
                      className="px-3 py-1 rounded bg-[#041026] text-slate-300 hover:text-white border border-slate-700 text-[10px]"
                    >
                      {copiedCode ? "Copied!" : "Copy Code"}
                    </button>
                  </div>
                  <pre className="p-4 rounded-xl bg-[#010409] border border-slate-800 text-[11px] text-emerald-400 font-mono overflow-x-auto leading-relaxed">
                    {diagnosticResult.actionable_fix}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 3: Predictive Career Pathways */}
      {activeTab === "career-pathways" && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-[#041026]/90 border border-slate-800 space-y-5">
            <div>
              <h3 className="text-base font-bold text-white">Predictive Core Hardware Industry Pathways</h3>
              <p className="text-xs text-slate-400 mt-1">
                Derived from student embedded firmware lab grades, RTOS projects, and Anna University ECE R2023 competencies.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              {SEED_CAREER_TRACKS.map((track) => (
                <div key={track.track_id} className="p-5 rounded-2xl bg-[#020813] border border-slate-800 space-y-3 hover:border-[#00F0B5]/40 transition-all">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-white">{track.title}</span>
                    <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-bold">
                      {track.fit_score}% FIT
                    </span>
                  </div>

                  <div className="space-y-1 text-slate-300 text-[11px]">
                    <div>
                      <span className="text-slate-500">Core Domains:</span> {track.core_domains.join(", ")}
                    </div>
                    <div>
                      <span className="text-slate-500">Top Recruiters:</span> {track.target_companies.join(", ")}
                    </div>
                    <div>
                      <span className="text-slate-500">Median Compensation:</span> <strong className="text-amber-400">{track.median_salary_range}</strong>
                    </div>
                    <div>
                      <span className="text-slate-500">Industry Hubs:</span> {track.hub_locations.join(" • ")}
                    </div>
                  </div>

                  <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px]">
                    <span className="text-slate-400">NPTEL Path:</span>
                    <span className="text-[#00F0B5] truncate max-w-xs">{track.recommended_nptel[0]}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: MIT Campus Digital Twin */}
      {activeTab === "digital-twin" && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-[#041026]/90 border border-slate-800 space-y-5 text-xs">
            <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
              <div>
                <h3 className="text-base font-bold text-white">MIT Campus Virtual Lab 304 Digital Twin</h3>
                <p className="text-slate-400">Department of Electronics Engineering • Telemetry &amp; Energy Telemetry</p>
              </div>
              <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-bold">
                ✓ ALL 3 TESTBEDS ONLINE
              </span>
            </div>

            {/* Environmental Sensors */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <div className="text-slate-500 text-[10px]">Ambient Temperature</div>
                <div className="text-lg font-bold text-white mt-0.5">23.8 °C</div>
                <div className="text-[9px] text-emerald-400">Optimal Thermal</div>
              </div>
              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <div className="text-slate-500 text-[10px]">Relative Humidity</div>
                <div className="text-lg font-bold text-white mt-0.5">52.4 %</div>
                <div className="text-[9px] text-cyan-400">ESD Protected</div>
              </div>
              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <div className="text-slate-500 text-[10px]">Mains Power</div>
                <div className="text-lg font-bold text-white mt-0.5">231.4 VAC</div>
                <div className="text-[9px] text-amber-400">50.02 Hz Stable</div>
              </div>
              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800">
                <div className="text-slate-500 text-[10px]">Active Bench Power</div>
                <div className="text-lg font-bold text-white mt-0.5">1.42 kW</div>
                <div className="text-[9px] text-emerald-400">Eco Mode Passive</div>
              </div>
            </div>

            {/* Connected Hardware Nodes */}
            <div className="space-y-3 pt-2">
              <div className="font-bold text-white">Active Bench Testbed Nodes:</div>
              <div className="space-y-2">
                <div className="p-3 rounded-xl bg-[#020813] border border-slate-800 flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <span className="font-bold text-[#00F0B5]">MIT-NODE-ESP32-01</span>
                    <span className="text-slate-400 ml-2">ESP32-S3 (Dual-Core Xtensa LX7 @ 240MHz)</span>
                  </div>
                  <div className="flex items-center gap-3 text-[11px]">
                    <span className="text-slate-400">Rail: <strong className="text-white">3.29 V</strong></span>
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px]">
                      WebSerial Linked
                    </span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-[#020813] border border-slate-800 flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <span className="font-bold text-[#00F0B5]">MIT-NODE-STM32-02</span>
                    <span className="text-slate-400 ml-2">STM32F407VGT6 (ARM Cortex-M4 @ 168MHz)</span>
                  </div>
                  <div className="flex items-center gap-3 text-[11px]">
                    <span className="text-slate-400">Rail: <strong className="text-white">3.31 V</strong></span>
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px]">
                      ST-LINK Ready
                    </span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-[#020813] border border-slate-800 flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <span className="font-bold text-[#00F0B5]">MIT-NODE-WOKWI-SIM</span>
                    <span className="text-slate-400 ml-2">Wokwi Virtual Microcontroller HIL Simulator</span>
                  </div>
                  <div className="flex items-center gap-3 text-[11px]">
                    <span className="text-slate-400">Clock: <strong className="text-white">240 MHz</strong></span>
                    <span className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-[10px]">
                      WebSocket Synchronized
                    </span>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}

