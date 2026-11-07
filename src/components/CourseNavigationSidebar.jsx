import React, { useState } from 'react';
import { TIER3_SPECIALIZATION_TRACKS } from '../data/course_config_schema';
export { TIER3_SPECIALIZATION_TRACKS };

/**
 * ========================================================================================
 * VoltCore Apex Academia - Granular Course Sidebar & Navigation Island
 * Core Engineering Series • Autonomous Engineering Cluster
 * Platform Lead & Systems Architect: Ashok Kumar A
 * Features:
 *   - Core Tracks (Embedded Systems, Generative AI, Foundational Fundamentals)
 *   - Tier 3 Advanced Specialization Tracks (10 Tracks with Simulator Bindings)
 *   - Instant track switching and reactive synchronization with the Multi-Frame Workspace
 * ========================================================================================
 */

export const COURSE_CATALOG = [
  {
    id: "embedded_systems",
    title: "Embedded Systems & Real-Time IoT",
    regulation: "Core Engineering Series • Embedded & RTOS",
    badge: "Core ECE",
    icon: "⚡",
    themeColor: "#00F0B5",
    description: "Cortex-M4 / Xtensa dual-core firmware, FreeRTOS preemption, DMA zero-copy, and bus protocols.",
    sections: [
      {
        id: "intro",
        title: "Introduction & Architecture",
        icon: "📌",
        duration: "45 mins",
        completed: true,
        summary: "ARM Cortex-M4 vs ESP32 Xtensa Dual-Core, memory maps, Harvard bus matrix, and pipeline stages.",
        videoId: "embed_01_intro",
        codeSnippet: `// FreeRTOS Task Scheduling Demo\n#include <Arduino.h>\nvoid TaskSensor(void *pvParameters) {\n  for(;;) {\n    Serial.println("[Sensor] ADC Voltage: 3.28V");\n    vTaskDelay(pdMS_TO_TICKS(1000));\n  }\n}\nvoid setup() {\n  Serial.begin(115200);\n  xTaskCreate(TaskSensor, "SensorTask", 2048, NULL, 2, NULL);\n}\nvoid loop() {}`,
        circuitSim: "ESP32 + Dual I2C BME280 Sensor Hub"
      },
      {
        id: "course_material",
        title: "Course Material & Datasheets",
        icon: "📖",
        duration: "90 mins",
        completed: true,
        summary: "Unit I-V syllabus modules, NVIC priority grouping, scatter-gather DMA, and SPI/I2C/UART bus timing.",
        videoId: "embed_02_dma",
        codeSnippet: `// Circular Buffer DMA Streaming\n#define BUFFER_SIZE 512\nuint8_t rx_buffer[BUFFER_SIZE] __attribute__((aligned(4)));\nvoid init_dma_stream() {\n  // Configure DMA peripheral-to-memory\n}`,
        circuitSim: "Cortex-M4 Bus Matrix & Circular DMA Buffer"
      },
      {
        id: "daily_quiz",
        title: "Daily Quiz (Timed MCQs)",
        icon: "⚡",
        duration: "15 mins",
        completed: false,
        summary: "5 daily timed technical questions testing FreeRTOS priorities, context switch latency, and ISR tail-chaining.",
        videoId: "embed_03_quiz",
        codeSnippet: `// Quiz Verification: Priority Inheritance\nbool verify_priority_inheritance(int low_prio, int high_prio) {\n  return (high_prio > low_prio);\n}`,
        circuitSim: "Interactive Logic State Analyzer"
      },
      {
        id: "assessments",
        title: "Continuous Assessments (CAT 1 & 2)",
        icon: "📝",
        duration: "60 mins",
        completed: false,
        summary: "Internal Continuous Assessment Test question papers with rubrics, derivations, and timing trace diagrams.",
        videoId: "embed_04_cat",
        codeSnippet: `// Interrupt Latency Derivation Benchmark\nfloat calculate_interrupt_latency(float t_detect, float t_push, float t_vector) {\n  return t_detect + t_push + t_vector;\n}`,
        circuitSim: "Keysight Virtual DSO Timing Deck"
      },
      {
        id: "assignments",
        title: "Laboratory Assignments",
        icon: "💻",
        duration: "120 mins",
        completed: false,
        summary: "Wokwi firmware exercises: FreeRTOS priority queues, Mutex priority ceiling, and ESP32 deep-sleep modes.",
        videoId: "embed_05_assign",
        codeSnippet: `// Lab 04: FreeRTOS Mutex Lock\nSemaphoreHandle_t xMutex;\nvoid setup() {\n  xMutex = xSemaphoreCreateMutex();\n}`,
        circuitSim: "Wokwi FreeRTOS Queue Simulator"
      },
      {
        id: "mini_projects",
        title: "Mini-Projects",
        icon: "🛠️",
        duration: "180 mins",
        completed: false,
        summary: "ESP32 RFID Smart Lab Attendance Node, battery LiPo discharge profiler, and BLE environmental node.",
        videoId: "embed_06_miniproj",
        codeSnippet: `// RFID RC522 SPI Gateway\n#include <SPI.h>\n#include <MFRC522.h>\n#define SS_PIN 5\n#define RST_PIN 22\nMFRC522 rfid(SS_PIN, RST_PIN);`,
        circuitSim: "ESP32 + RC522 RFID Attendance Node"
      },
      {
        id: "major_projects",
        title: "Major Projects",
        icon: "🚀",
        duration: "300 mins",
        completed: false,
        summary: "Autonomous Hardware-in-the-Loop (HIL) Test Bench, Automotive CAN bus diagnostic gateway, and drone flight telemetry.",
        videoId: "embed_07_majorproj",
        codeSnippet: `// Automotive CAN Bus Sentinel\n#include <CAN.h>\nvoid setup() {\n  CAN.begin(500E3);\n}`,
        circuitSim: "Automotive CAN Transceiver Simulation"
      }
    ]
  },
  {
    id: "generative_ai",
    title: "Generative AI & Edge Intelligence",
    regulation: "Advanced Engineering Series • Edge Intelligence",
    badge: "TinyML & AI",
    icon: "🧠",
    themeColor: "#D946EF",
    description: "Transformers on edge microcontrollers, INT8 quantization, CMSIS-NN, tensor arenas, and acoustic anomaly detection.",
    sections: [
      {
        id: "intro",
        title: "Introduction & Transformers for ECE",
        icon: "📌",
        duration: "50 mins",
        completed: true,
        summary: "Attention mechanisms on silicon, edge compute constraints, tensor dimensions, and quantized matrix multiplication.",
        videoId: "ai_01_intro",
        codeSnippet: `# Edge Attention Vector Matrix Multiply\nimport numpy as np\ndef edge_dot_product(q, k):\n    return np.dot(q, k.T) / np.sqrt(q.shape[-1])`,
        circuitSim: "Systolic Array MAC Accelerator"
      },
      {
        id: "course_material",
        title: "Course Material & Quantization",
        icon: "📖",
        duration: "100 mins",
        completed: false,
        summary: "Full integer quantization (INT8), per-channel vs per-tensor scaling, depthwise separable convolutions, and CMSIS-NN.",
        videoId: "ai_02_quant",
        codeSnippet: `# INT8 Symmetric Quantization\ndef quantize_float_to_int8(val, scale, zero_point=0):\n    q = np.round(val / scale) + zero_point\n    return np.clip(q, -128, 127).astype(np.int8)`,
        circuitSim: "Tensor Arena SRAM Allocator"
      },
      {
        id: "daily_quiz",
        title: "Daily Quiz (Timed MCQs)",
        icon: "⚡",
        duration: "15 mins",
        completed: false,
        summary: "5 daily timed MCQs on ReLU vs GELU in MCU firmware, MAC throughput, and SRAM arena budgeting.",
        videoId: "ai_03_quiz",
        codeSnippet: `# Quiz: MAC Computation\ndef compute_macs(kernel_h, kernel_w, in_ch, out_ch):\n    return kernel_h * kernel_w * in_ch * out_ch`,
        circuitSim: "Hardware Multiplier-Accumulator Deck"
      },
      {
        id: "assessments",
        title: "Continuous Assessments (CAT 1 & 2)",
        icon: "📝",
        duration: "60 mins",
        completed: false,
        summary: "Neural network latency calculation, flash memory mapping, and INT8 zero-point offset error modeling.",
        videoId: "ai_04_cat",
        codeSnippet: `# Arena Memory Footprint Estimator\ndef estimate_arena_bytes(layers):\n    return sum(l['inputs'] + l['weights'] + l['outputs'] for l in layers)`,
        circuitSim: "Microcontroller Flash/RAM Visualizer"
      },
      {
        id: "assignments",
        title: "Laboratory Assignments",
        icon: "💻",
        duration: "120 mins",
        completed: false,
        summary: "Deploy keyword spotting (KWS) model on ESP32-S3 using TFLite Micro and evaluate accuracy vs power draw.",
        videoId: "ai_05_assign",
        codeSnippet: `// TFLite Micro Invoke Loop\n#include "tensorflow/lite/micro/all_ops_resolver.h"\nvoid invoke_inference() {\n  TfLiteStatus invoke_status = interpreter->Invoke();\n}`,
        circuitSim: "ESP32-S3 I2S Microphone Audio Pipeline"
      },
      {
        id: "mini_projects",
        title: "Mini-Projects",
        icon: "🛠️",
        duration: "180 mins",
        completed: false,
        summary: "Gemini RAG local viva-voce tutor, hand gesture IMU classifier, and smart vibration monitor.",
        videoId: "ai_06_miniproj",
        codeSnippet: `# Anomaly Detection Autoencoder Threshold\ndef is_anomaly(loss, threshold=0.045):\n    return loss > threshold`,
        circuitSim: "MPU-6050 6-Axis Motion Classifier"
      },
      {
        id: "major_projects",
        title: "Major Projects",
        icon: "🚀",
        duration: "300 mins",
        completed: false,
        summary: "Edge AI UAV structural vibration sentinel, real-time multi-sensor fusion, and autonomous TinyML vision camera.",
        videoId: "ai_07_majorproj",
        codeSnippet: `# Vision TinyML Detection Pipeline\nclass TinyMLSentinel:\n    def __init__(self, weights_path):\n        self.ready = True`,
        circuitSim: "Edge AI Camera & Optical Flow Unit"
      }
    ]
  },
  {
    id: "foundational_fundamentals",
    title: "Foundational Fundamentals",
    regulation: "Core Circuits, Digital & Math",
    badge: "Foundations",
    icon: "📐",
    themeColor: "#38BDF8",
    description: "K-Maps, Quine-McCluskey, Op-Amps, small-signal Hybrid-Pi models, Bode plots, and GATE ECE mathematical rigor.",
    sections: [
      {
        id: "intro",
        title: "Introduction to Circuits & Logic",
        icon: "📌",
        duration: "40 mins",
        completed: true,
        summary: "Kirchhoff laws, Thevenin/Norton equivalents, boolean algebra axioms, De Morgan laws, and semiconductor junctions.",
        videoId: "found_01_intro",
        codeSnippet: `// Digital Logic Gate Primitive Verification\nmodule logic_test(input a, input b, output y);\n  assign y = a ^ b; // XOR\nendmodule`,
        circuitSim: "Interactive Dual Logic Gate Breadboard"
      },
      {
        id: "course_material",
        title: "Course Material & Formulas",
        icon: "📖",
        duration: "90 mins",
        completed: true,
        summary: "Op-Amp 741 golden rules, Miller compensation, BJT hybrid-pi r_pi and gm derivations, and Nyquist stability criteria.",
        videoId: "found_02_analog",
        codeSnippet: `# Small-Signal BJT Transconductance\ndef bjt_gm(ic_ma, vt_mv=26.0):\n    return ic_ma / vt_mv`,
        circuitSim: "Op-Amp 741 Non-Inverting Amplifier"
      },
      {
        id: "daily_quiz",
        title: "Daily Quiz (Timed MCQs)",
        icon: "⚡",
        duration: "15 mins",
        completed: false,
        summary: "5 daily timed MCQs selected from university examinations and GATE ECE archives.",
        videoId: "found_03_quiz",
        codeSnippet: `# GATE ECE Resonance Frequency\ndef resonance_frequency(l_henry, c_farad):\n    import math\n    return 1.0 / (2 * math.pi * math.sqrt(l_henry * c_farad))`,
        circuitSim: "RLC Series Resonant Circuit"
      },
      {
        id: "assessments",
        title: "Continuous Assessments (CAT 1 & 2)",
        icon: "📝",
        duration: "60 mins",
        completed: false,
        summary: "Active Butterworth filter order calculation, pole placement, and state-transition equation synthesis.",
        videoId: "found_04_cat",
        codeSnippet: `# Butterworth Filter Order Calculation\nimport math\ndef butterworth_order(ap_db, as_db, wp, ws):\n    num = math.log10((10**(as_db/10) - 1) / (10**(ap_db/10) - 1))\n    den = 2 * math.log10(ws / wp)\n    return math.ceil(num / den)`,
        circuitSim: "2nd-Order Sallen-Key Low-Pass Filter"
      },
      {
        id: "assignments",
        title: "Laboratory Assignments",
        icon: "💻",
        duration: "120 mins",
        completed: false,
        summary: "LTspice frequency response Bode plot simulation, gain-bandwidth product measurement, and 4-variable K-Map minimization.",
        videoId: "found_05_assign",
        codeSnippet: `* LTspice SPICE Netlist Benchmark\nV1 in 0 AC 1\nR1 in out 1k\nC1 out 0 100n\n.ac dec 20 10 100k\n.backanno\n.end`,
        circuitSim: "LTspice Virtual Bode Waveform Analyzer"
      },
      {
        id: "mini_projects",
        title: "Mini-Projects",
        icon: "🛠️",
        duration: "180 mins",
        completed: false,
        summary: "8-bit R-2R ladder digital-to-analog converter (DAC) and precision 555-timer astable multivibrator clock.",
        videoId: "found_06_miniproj",
        codeSnippet: `// 8-Bit R-2R DAC Output Formula\nfloat compute_dac_vout(uint8_t code, float vref=3.3) {\n  return (code / 256.0) * vref;\n}`,
        circuitSim: "R-2R Ladder DAC & Precision Op-Amp Buffer"
      },
      {
        id: "major_projects",
        title: "Major Projects",
        icon: "🚀",
        duration: "300 mins",
        completed: false,
        summary: "FPGA 8-channel logic analyzer with cursor measurement tools, dual-slope integrating digital voltmeter instrument.",
        videoId: "found_07_majorproj",
        codeSnippet: `// Verilog Clock Divider (50MHz to 1kHz)\nmodule clk_div(input clk_in, output reg clk_out);\n  reg [15:0] count = 0;\n  always @(posedge clk_in) begin\n    if (count == 24999) begin\n      count <= 0;\n      clk_out <= ~clk_out;\n    end else count <= count + 1;\n  end\nendmodule`,
        circuitSim: "FPGA 8-Channel Timing Diagram Analyzer"
      }
    ]
  }
];

export default function CourseNavigationSidebar({
  activeTrackId = "embedded_systems",
  activeSectionId = "intro",
  onSelectSection = () => {},
  isCollapsed = false,
  onToggleCollapse = () => {}
}) {
  const [expandedTrackId, setExpandedTrackId] = useState(activeTrackId);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTabMode, setActiveTabMode] = useState("core"); // "core" | "tier3"
  const [lockAlert, setLockAlert] = useState(null);

  // Student Mastery Progression Tokens (defaults with foundational competencies)
  const [masteredModules, setMasteredModules] = useState(() => {
    try {
      if (typeof window !== "undefined" && window.localStorage) {
        const saved = localStorage.getItem("voltcore_mastered_modules");
        if (saved) return JSON.parse(saved);
      }
    } catch (e) {}
    return { "EE23C01": 85.0, "PH23C01": 90.0, "MA23C01": 78.0, "EC8702": 82.0, "EC23C03": 88.0 };
  });

  const checkTrackUnlocked = (spec) => {
    const prereqs = spec.prerequisites || [];
    if (prereqs.length === 0) return { unlocked: true, missing: [] };
    const missing = prereqs.filter(p => !masteredModules[p] || masteredModules[p] < 70.0);
    return { unlocked: missing.length === 0, missing };
  };

  const simulateMasteryAttainment = (code) => {
    setMasteredModules(prev => {
      const updated = { ...prev, [code]: 85.0 };
      try {
        if (typeof window !== "undefined" && window.localStorage) {
          localStorage.setItem("voltcore_mastered_modules", JSON.stringify(updated));
        }
      } catch (e) {}
      return updated;
    });
    setLockAlert(null);
  };

  const toggleTrack = (trackId) => {
    setExpandedTrackId(prev => prev === trackId ? null : trackId);
  };

  const filteredTier3Tracks = searchQuery
    ? TIER3_SPECIALIZATION_TRACKS.filter(t =>
        t.track.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.summary.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : TIER3_SPECIALIZATION_TRACKS;

  return (
    <aside 
      className={`glass-card rounded-2xl border transition-all duration-300 flex flex-col font-mono text-xs ${
        isCollapsed ? 'w-14 items-center p-2' : 'w-72 lg:w-80 p-4'
      }`}
      style={{ borderColor: 'var(--theme-border)' }}
    >
      {/* Sidebar Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 w-full mb-3">
        {!isCollapsed && (
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="font-bold text-white tracking-tight uppercase text-[11px]">
              Course Navigation
            </span>
          </div>
        )}
        <button
          type="button"
          onClick={onToggleCollapse}
          className="p-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 transition-colors"
          title={isCollapsed ? "Expand Course Sidebar" : "Collapse Course Sidebar"}
        >
          {isCollapsed ? "▶" : "◀"}
        </button>
      </div>

      {/* Mode Switcher Tabs */}
      {!isCollapsed && (
        <div className="flex rounded-lg bg-slate-900/80 p-0.5 border border-slate-800 mb-2.5 w-full">
          <button
            type="button"
            onClick={() => setActiveTabMode("core")}
            className={`flex-1 py-1 text-[10px] rounded-md transition-all font-bold ${
              activeTabMode === "core"
                ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Core Tracks
          </button>
          <button
            type="button"
            onClick={() => setActiveTabMode("tier3")}
            className={`flex-1 py-1 text-[10px] rounded-md transition-all font-bold ${
              activeTabMode === "tier3"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Specializations (10)
          </button>
        </div>
      )}

      {/* Quick Search (when expanded) */}
      {!isCollapsed && (
        <div className="mb-3 w-full">
          <input
            type="text"
            placeholder={activeTabMode === "core" ? "Search syllabus sections..." : "Search 10 specialization tracks..."}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-200 placeholder-slate-500 text-[11px] focus:outline-none focus:border-emerald-400"
          />
        </div>
      )}

      {/* Course Tracks Accordion */}
      <div className="flex-1 overflow-y-auto space-y-2.5 w-full pr-1">
        {activeTabMode === "tier3" && !isCollapsed && (
          <div className="space-y-2">
            {/* Prerequisite Lock Alert Banner */}
            {lockAlert && (
              <div className="p-2.5 rounded-xl bg-amber-950/40 border border-amber-500/40 text-[11px] space-y-1.5 transition-all">
                <div className="flex items-center justify-between text-amber-300 font-bold">
                  <span className="flex items-center gap-1.5">
                    <span>🔒</span>
                    <span>Locked: {lockAlert.track} ({lockAlert.code})</span>
                  </span>
                  <button 
                    type="button"
                    onClick={() => setLockAlert(null)} 
                    className="text-amber-400 hover:text-white text-xs"
                    aria-label="Dismiss alert"
                  >
                    ✕
                  </button>
                </div>
                <p className="text-slate-300 text-[10px] leading-tight">
                  Requires ≥ 70% mastery in: <span className="font-mono text-amber-200 font-bold">{lockAlert.missing.join(', ')}</span>.
                </p>
                <div className="flex flex-wrap items-center gap-1.5 pt-1">
                  {lockAlert.missing.map(m => (
                    <button
                      key={m}
                      type="button"
                      onClick={() => simulateMasteryAttainment(m)}
                      className="px-2 py-0.5 rounded bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 hover:bg-emerald-500/30 font-bold text-[9px] transition-all inline-flex items-center gap-1"
                      title={`Simulate completing ${m} to unlock downstream nodes`}
                    >
                      <span>⚡ Unlock:</span>
                      <span>Pass {m} (85%)</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {filteredTier3Tracks.map(spec => {
              const lockStatus = checkTrackUnlocked(spec);
              const isUnlocked = lockStatus.unlocked;
              const isMastered = !!masteredModules[spec.code] && masteredModules[spec.code] >= 70.0;

              return (
                <div
                  key={spec.id}
                  className={`p-2.5 rounded-xl border transition-all space-y-1.5 ${
                    !isUnlocked
                      ? "border-slate-800/60 bg-slate-950/50 opacity-80 hover:border-amber-500/40"
                      : isMastered
                        ? "border-emerald-500/40 bg-emerald-950/10 shadow-sm"
                        : "border-slate-800 bg-slate-900/40 hover:border-slate-700"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 truncate">
                      <span className="text-sm">{spec.icon}</span>
                      <span className="font-bold text-white text-[11px] truncate">{spec.track}</span>
                    </div>
                    <div className="flex items-center gap-1 flex-shrink-0">
                      {!isUnlocked ? (
                        <span 
                          className="text-[9px] px-1.5 py-0.5 rounded font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40"
                          title={`Locked: Requires >= 70% in ${lockStatus.missing.join(', ')}`}
                        >
                          🔒 {spec.code}
                        </span>
                      ) : isMastered ? (
                        <span 
                          className="text-[9px] px-1.5 py-0.5 rounded font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                          title="Competency Mastered (>= 70%)"
                        >
                          ⚡ {spec.code}
                        </span>
                      ) : (
                        <span
                          className="text-[9px] px-1.5 py-0.5 rounded font-mono font-bold"
                          style={{
                            color: spec.themeColor,
                            backgroundColor: `${spec.themeColor}15`,
                            border: `1px solid ${spec.themeColor}40`
                          }}
                        >
                          {spec.code}
                        </span>
                      )}
                    </div>
                  </div>
                  <p className="text-[10px] text-slate-300 line-clamp-2 leading-snug">
                    {spec.title}
                  </p>
                  
                  {/* Prerequisite Tags */}
                  {spec.prerequisites && spec.prerequisites.length > 0 && (
                    <div className="flex items-center gap-1 text-[9px] font-mono text-slate-400">
                      <span>Prereq:</span>
                      {spec.prerequisites.map(p => (
                        <span 
                          key={p} 
                          className={`px-1 rounded ${
                            masteredModules[p] && masteredModules[p] >= 70.0
                              ? "text-emerald-400 bg-emerald-950/40"
                              : "text-amber-400 bg-amber-950/40 font-bold"
                          }`}
                        >
                          {p} {masteredModules[p] && masteredModules[p] >= 70.0 ? "✓" : "🔒"}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="flex items-center justify-between pt-1 border-t border-slate-800/60">
                    <span className="text-[9px] text-slate-400 truncate">
                      {spec.duration} • {spec.difficulty}
                    </span>
                    {!isUnlocked ? (
                      <button
                        type="button"
                        onClick={() => setLockAlert({ track: spec.track, code: spec.code, missing: lockStatus.missing })}
                        className="text-[9px] px-2 py-0.5 rounded font-bold transition-all bg-amber-500/10 text-amber-300 border border-amber-500/40 hover:bg-amber-500/20 inline-flex items-center gap-1 flex-shrink-0"
                        title={`Locked: Requires >= 70% in ${lockStatus.missing.join(', ')}`}
                      >
                        <span>🔒</span>
                        <span>Requires {lockStatus.missing[0]}</span>
                      </button>
                    ) : (
                      <a
                        href={spec.simRoute}
                        className="text-[9px] px-2 py-0.5 rounded font-bold transition-all hover:scale-105 inline-flex items-center gap-1 flex-shrink-0"
                        style={{
                          color: spec.themeColor,
                          border: `1px solid ${spec.themeColor}50`,
                          backgroundColor: `${spec.themeColor}10`
                        }}
                        title={`Launch ${spec.simulationComponent}`}
                      >
                        <span>⚡</span>
                        <span className="truncate max-w-[100px]">{spec.simulationComponent}</span>
                      </a>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {activeTabMode === "core" && COURSE_CATALOG.map((track) => {
          const isExpanded = expandedTrackId === track.id || searchQuery.length > 0;
          const isCurrentTrack = activeTrackId === track.id;

          // Filter sections if search query is active
          const filteredSections = searchQuery
            ? track.sections.filter(s => 
                s.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                s.summary.toLowerCase().includes(searchQuery.toLowerCase())
              )
            : track.sections;

          if (searchQuery && filteredSections.length === 0) return null;

          return (
            <div 
              key={track.id}
              className={`rounded-xl border transition-all ${
                isCurrentTrack 
                  ? 'border-slate-700 bg-slate-900/60 shadow-md' 
                  : 'border-slate-800/70 bg-slate-900/30 hover:border-slate-700'
              }`}
            >
              {/* Track Title Accordion Trigger */}
              <button
                type="button"
                onClick={() => {
                  if (isCollapsed) onToggleCollapse();
                  toggleTrack(track.id);
                }}
                className={`w-full flex items-center justify-between p-2.5 text-left transition-colors ${
                  isCollapsed ? 'justify-center' : ''
                }`}
                title={track.title}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-base flex-shrink-0">{track.icon}</span>
                  {!isCollapsed && (
                    <div className="min-w-0">
                      <div className="font-bold text-white text-xs truncate leading-tight">
                        {track.title}
                      </div>
                      <div className="text-[10px] text-slate-400 truncate">
                        {track.regulation}
                      </div>
                    </div>
                  )}
                </div>

                {!isCollapsed && (
                  <span className={`text-[10px] text-slate-400 transition-transform ${isExpanded ? 'rotate-90' : ''}`}>
                    ▶
                  </span>
                )}
              </button>

              {/* Granular 7 Sections Submenu */}
              {isExpanded && !isCollapsed && (
                <div className="px-2 pb-2 space-y-1 border-t border-slate-800/60 pt-2">
                  {filteredSections.map((sec) => {
                    const isSelected = isCurrentTrack && activeSectionId === sec.id;
                    return (
                      <button
                        key={sec.id}
                        type="button"
                        onClick={() => onSelectSection(track, sec)}
                        className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-left transition-all ${
                          isSelected
                            ? 'bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/40 shadow-sm'
                            : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
                        }`}
                      >
                        <div className="flex items-center gap-2 truncate">
                          <span className="text-xs">{sec.icon}</span>
                          <span className="text-[11px] truncate">{sec.title}</span>
                        </div>

                        <div className="flex items-center gap-1.5 flex-shrink-0 ml-1">
                          {sec.completed && (
                            <span className="text-emerald-400 text-[10px]" title="Completed">✓</span>
                          )}
                          <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                            {sec.duration}
                          </span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}

            </div>
          );
        })}
      </div>

      {/* Sidebar Footer */}
      {!isCollapsed && (
        <div className="pt-3 border-t border-slate-800/80 text-[10px] text-slate-400 flex items-center justify-between mt-2">
          <span>Core Engineering Series</span>
          <span className="text-emerald-400 font-bold">10 Tracks • 21 Units</span>
        </div>
      )}
    </aside>
  );
}
