"""
========================================================================================
VoltCore Apex Academia - Phase 41: Dynamic Multi-Theme & Resizable Workspace Engine
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
========================================================================================
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Database path in workspace root
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "voltcore_telemetry.db")

# ========================================================================================
# 18 VIBRANT & COLORFUL THEMES SPECIFICATION (Non-Black Focus)
# ========================================================================================
THEMES_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "cyber-emerald",
        "name": "Cyber Emerald & Mint",
        "category": "Vibrant Neon",
        "badge": "Neon Mint",
        "icon": "⚡",
        "description": "Deep crystalline teal base with radiant emerald-cyan accents and electric mint glows.",
        "colors": {
            "primary": "#00F0B5",
            "accent": "#10B981",
            "background": "#03261f",
            "backgroundGradient": "linear-gradient(135deg, #03261f 0%, #063d32 50%, #021a15 100%)",
            "surface": "rgba(4, 46, 38, 0.78)",
            "card": "rgba(6, 61, 50, 0.65)",
            "border": "rgba(0, 240, 181, 0.35)",
            "text": "#E6FFFA",
            "textMuted": "#80DFCB",
            "glow": "0 0 25px rgba(0, 240, 181, 0.35)"
        }
    },
    {
        "id": "electric-violet",
        "name": "Electric Violet & Magenta",
        "category": "Vibrant Neon",
        "badge": "Ultraviolet",
        "icon": "🔮",
        "description": "Royal indigo and cosmic violet with laser magenta highlights and neon purple aura.",
        "colors": {
            "primary": "#A855F7",
            "accent": "#EC4899",
            "background": "#160d33",
            "backgroundGradient": "linear-gradient(135deg, #160d33 0%, #291557 50%, #100826 100%)",
            "surface": "rgba(33, 19, 74, 0.82)",
            "card": "rgba(45, 24, 99, 0.65)",
            "border": "rgba(168, 85, 247, 0.38)",
            "text": "#FAF5FF",
            "textMuted": "#D8B4FE",
            "glow": "0 0 28px rgba(168, 85, 247, 0.4)"
        }
    },
    {
        "id": "sunset-crimson",
        "name": "Sunset Crimson & Amber",
        "category": "Sunset Gradient",
        "badge": "Solar Sunset",
        "icon": "🌅",
        "description": "Warm blood-orange and vivid crimson with glowing golden hour horizon gradients.",
        "colors": {
            "primary": "#F97316",
            "accent": "#F43F5E",
            "background": "#260a14",
            "backgroundGradient": "linear-gradient(135deg, #260a14 0%, #4c1122 50%, #1c050c 100%)",
            "surface": "rgba(56, 17, 30, 0.82)",
            "card": "rgba(74, 20, 38, 0.65)",
            "border": "rgba(249, 115, 22, 0.38)",
            "text": "#FFF5F5",
            "textMuted": "#FCA5A5",
            "glow": "0 0 28px rgba(249, 115, 22, 0.4)"
        }
    },
    {
        "id": "oceanic-azure",
        "name": "Oceanic Sapphire & Cyan",
        "category": "Rich Chromatic",
        "badge": "Deep Ocean",
        "icon": "🌊",
        "description": "Deep ocean trench navy-blue with vivid sky cyan and sapphire luminescence.",
        "colors": {
            "primary": "#00D8F6",
            "accent": "#3B82F6",
            "background": "#061b33",
            "backgroundGradient": "linear-gradient(135deg, #061b33 0%, #0c2d52 50%, #031122 100%)",
            "surface": "rgba(10, 39, 71, 0.82)",
            "card": "rgba(13, 51, 94, 0.65)",
            "border": "rgba(0, 216, 246, 0.35)",
            "text": "#F0F9FF",
            "textMuted": "#93C5FD",
            "glow": "0 0 26px rgba(0, 216, 246, 0.38)"
        }
    },
    {
        "id": "golden-mustard",
        "name": "Imperial Gold & Warm Mustard",
        "category": "Rich Chromatic",
        "badge": "Royal Gold",
        "icon": "👑",
        "description": "Regal warm umber and antique bronze enriched with vivid honey mustard and imperial amber.",
        "colors": {
            "primary": "#FFC83B",
            "accent": "#F59E0B",
            "background": "#241503",
            "backgroundGradient": "linear-gradient(135deg, #241503 0%, #3d2306 50%, #170d01 100%)",
            "surface": "rgba(54, 32, 7, 0.85)",
            "card": "rgba(74, 43, 8, 0.65)",
            "border": "rgba(255, 200, 59, 0.4)",
            "text": "#FFFBEB",
            "textMuted": "#FDE68A",
            "glow": "0 0 28px rgba(255, 200, 59, 0.38)"
        }
    },
    {
        "id": "tokyo-neon",
        "name": "Tokyo Cyberpunk Neon",
        "category": "Vibrant Neon",
        "badge": "Cyberpunk",
        "icon": "🗼",
        "description": "Electrifying high-voltage neon pink, cyber cyan, and laser lime on deep amethyst.",
        "colors": {
            "primary": "#FF007F",
            "accent": "#00F5FF",
            "background": "#140524",
            "backgroundGradient": "linear-gradient(135deg, #140524 0%, #2b0b47 50%, #0c0217 100%)",
            "surface": "rgba(35, 11, 59, 0.85)",
            "card": "rgba(50, 15, 84, 0.65)",
            "border": "rgba(255, 0, 127, 0.45)",
            "text": "#FFF0F8",
            "textMuted": "#F472B6",
            "glow": "0 0 30px rgba(255, 0, 127, 0.45)"
        }
    },
    {
        "id": "nordic-frost",
        "name": "Nordic Glacial Frost",
        "category": "Rich Chromatic",
        "badge": "Glacial Blue",
        "icon": "❄️",
        "description": "Crystalline Scandinavian fjord blue with arctic ice highlights and frost cyan edges.",
        "colors": {
            "primary": "#38BDF8",
            "accent": "#7DD3FC",
            "background": "#071c2c",
            "backgroundGradient": "linear-gradient(135deg, #071c2c 0%, #0f3450 50%, #04121d 100%)",
            "surface": "rgba(12, 45, 71, 0.82)",
            "card": "rgba(18, 62, 97, 0.65)",
            "border": "rgba(56, 189, 248, 0.38)",
            "text": "#F0F9FF",
            "textMuted": "#BAE6FD",
            "glow": "0 0 25px rgba(56, 189, 248, 0.35)"
        }
    },
    {
        "id": "forest-sage",
        "name": "Lush Forest & Olive Sage",
        "category": "Rich Chromatic",
        "badge": "Pine Forest",
        "icon": "🌲",
        "description": "Lush evergreen pine canopy paired with olive sage and vibrant lime moss radiance.",
        "colors": {
            "primary": "#84A950",
            "accent": "#10B981",
            "background": "#092112",
            "backgroundGradient": "linear-gradient(135deg, #092112 0%, #133b20 50%, #05140a 100%)",
            "surface": "rgba(17, 51, 28, 0.82)",
            "card": "rgba(24, 71, 39, 0.65)",
            "border": "rgba(132, 169, 80, 0.4)",
            "text": "#F0FDF4",
            "textMuted": "#86EFAC",
            "glow": "0 0 26px rgba(132, 169, 80, 0.35)"
        }
    },
    {
        "id": "solar-flare",
        "name": "Solar Flare & Plasma",
        "category": "Sunset Gradient",
        "badge": "Solar Plasma",
        "icon": "☀️",
        "description": "Blazing coronal eruption of radiant cadmium yellow and molten fiery orange.",
        "colors": {
            "primary": "#FACC15",
            "accent": "#FB923C",
            "background": "#2b1003",
            "backgroundGradient": "linear-gradient(135deg, #2b1003 0%, #4a1d06 50%, #1a0801 100%)",
            "surface": "rgba(61, 25, 7, 0.85)",
            "card": "rgba(82, 34, 9, 0.65)",
            "border": "rgba(250, 204, 21, 0.42)",
            "text": "#FEFCE8",
            "textMuted": "#FED7AA",
            "glow": "0 0 30px rgba(250, 204, 21, 0.45)"
        }
    },
    {
        "id": "cherry-blossom",
        "name": "Kyoto Sakura Blossom",
        "category": "Pastel Academy",
        "badge": "Sakura Pink",
        "icon": "🌸",
        "description": "Soft floral blossom pink with radiant ruby highlights and delicate rose petal tones.",
        "colors": {
            "primary": "#F472B6",
            "accent": "#FB7185",
            "background": "#260614",
            "backgroundGradient": "linear-gradient(135deg, #260614 0%, #470d27 50%, #18030c 100%)",
            "surface": "rgba(56, 13, 33, 0.82)",
            "card": "rgba(77, 18, 46, 0.65)",
            "border": "rgba(244, 114, 182, 0.4)",
            "text": "#FDF2F8",
            "textMuted": "#FBCFE8",
            "glow": "0 0 28px rgba(244, 114, 182, 0.38)"
        }
    },
    {
        "id": "pastel-academic",
        "name": "Cambridge Academic Pastel",
        "category": "Pastel Academy",
        "badge": "Ivory / Pastel",
        "icon": "🎓",
        "description": "Elegant ivory-cream parchment with academic periwinkle, lavender, and mint laurel.",
        "colors": {
            "primary": "#6366F1",
            "accent": "#10B981",
            "background": "#F5F3EC",
            "backgroundGradient": "linear-gradient(135deg, #F5F3EC 0%, #E9E6DC 50%, #FAF8F2 100%)",
            "surface": "rgba(255, 255, 255, 0.92)",
            "card": "rgba(245, 243, 235, 0.88)",
            "border": "rgba(99, 102, 241, 0.35)",
            "text": "#1E293B",
            "textMuted": "#64748B",
            "glow": "0 0 25px rgba(99, 102, 241, 0.22)"
        }
    },
    {
        "id": "oxford-navy",
        "name": "Oxford Collegiate Navy & Gold",
        "category": "Rich Chromatic",
        "badge": "Collegiate Blue",
        "icon": "🏛️",
        "description": "Stately university royal navy blue with heraldic gold emblem accents and crisp silver.",
        "colors": {
            "primary": "#EAB308",
            "accent": "#3B82F6",
            "background": "#09152b",
            "backgroundGradient": "linear-gradient(135deg, #09152b 0%, #122447 50%, #050d1c 100%)",
            "surface": "rgba(16, 34, 69, 0.85)",
            "card": "rgba(23, 49, 99, 0.65)",
            "border": "rgba(234, 179, 8, 0.4)",
            "text": "#F8FAFC",
            "textMuted": "#94A3B8",
            "glow": "0 0 28px rgba(234, 179, 8, 0.35)"
        }
    },
    {
        "id": "synthwave-80s",
        "name": "80s Retro Synthwave",
        "category": "Vibrant Neon",
        "badge": "Synthwave",
        "icon": "📼",
        "description": "Radical dark fuchsia and electric cyan with nostalgic neon grid reflections.",
        "colors": {
            "primary": "#FF1493",
            "accent": "#00E5FF",
            "background": "#190524",
            "backgroundGradient": "linear-gradient(135deg, #190524 0%, #330b4a 50%, #0e0214 100%)",
            "surface": "rgba(43, 11, 64, 0.85)",
            "card": "rgba(61, 16, 89, 0.65)",
            "border": "rgba(255, 20, 147, 0.42)",
            "text": "#FFF0F9",
            "textMuted": "#F472B6",
            "glow": "0 0 30px rgba(255, 20, 147, 0.45)"
        }
    },
    {
        "id": "matrix-terminal",
        "name": "Matrix Phosphor CRT",
        "category": "Vibrant Neon",
        "badge": "CRT Lime",
        "icon": "📟",
        "description": "Deep cathode dark green with high-intensity phosphor lime terminal glow.",
        "colors": {
            "primary": "#22C55E",
            "accent": "#4ADE80",
            "background": "#04190c",
            "backgroundGradient": "linear-gradient(135deg, #04190c 0%, #082e16 50%, #020d06 100%)",
            "surface": "rgba(8, 38, 19, 0.85)",
            "card": "rgba(12, 54, 27, 0.65)",
            "border": "rgba(34, 197, 94, 0.4)",
            "text": "#F0FDF4",
            "textMuted": "#86EFAC",
            "glow": "0 0 30px rgba(34, 197, 94, 0.45)"
        }
    },
    {
        "id": "lavender-dream",
        "name": "Lavender Amethyst Glow",
        "category": "Pastel Academy",
        "badge": "Soft Lavender",
        "icon": "🪻",
        "description": "Twilight amethyst background illuminated with serene lavender and periwinkle dreams.",
        "colors": {
            "primary": "#C084FC",
            "accent": "#818CF8",
            "background": "#170f2b",
            "backgroundGradient": "linear-gradient(135deg, #170f2b 0%, #291b4a 50%, #0e091c 100%)",
            "surface": "rgba(36, 24, 66, 0.82)",
            "card": "rgba(51, 34, 94, 0.65)",
            "border": "rgba(192, 132, 252, 0.4)",
            "text": "#FAF5FF",
            "textMuted": "#D8B4FE",
            "glow": "0 0 26px rgba(192, 132, 252, 0.38)"
        }
    },
    {
        "id": "autumn-copper",
        "name": "Autumn Harvest Copper",
        "category": "Sunset Gradient",
        "badge": "Copper Bronze",
        "icon": "🍂",
        "description": "Warm roasted espresso wood tone highlighted with burnished copper and amber honey.",
        "colors": {
            "primary": "#EA580C",
            "accent": "#F59E0B",
            "background": "#261005",
            "backgroundGradient": "linear-gradient(135deg, #261005 0%, #451d09 50%, #170902 100%)",
            "surface": "rgba(59, 26, 9, 0.85)",
            "card": "rgba(79, 35, 12, 0.65)",
            "border": "rgba(234, 88, 12, 0.4)",
            "text": "#FFF7ED",
            "textMuted": "#FDBA74",
            "glow": "0 0 28px rgba(234, 88, 12, 0.38)"
        }
    },
    {
        "id": "clean-canvas",
        "name": "Modern Pristine Canvas",
        "category": "Light Dynamic",
        "badge": "Light Studio",
        "icon": "✨",
        "description": "Clinical, ultra-crisp modern light workspace with cobalt electric blue and emerald accents.",
        "colors": {
            "primary": "#2563EB",
            "accent": "#059669",
            "background": "#F8FAFC",
            "backgroundGradient": "linear-gradient(135deg, #F8FAFC 0%, #EEF2F6 50%, #FFFFFF 100%)",
            "surface": "rgba(255, 255, 255, 0.95)",
            "card": "rgba(241, 245, 249, 0.9)",
            "border": "rgba(37, 99, 235, 0.3)",
            "text": "#0F172A",
            "textMuted": "#475569",
            "glow": "0 0 25px rgba(37, 99, 235, 0.2)"
        }
    },
    {
        "id": "cosmic-nebula",
        "name": "Cosmic Chromatic Nebula",
        "category": "Multi-Chromatic",
        "badge": "Multi-Chromatic",
        "icon": "🌌",
        "description": "Stunning multidimensional chromatic aurora with magenta, starlight teal, and celestial violet.",
        "colors": {
            "primary": "#D946EF",
            "accent": "#06B6D4",
            "background": "#110826",
            "backgroundGradient": "linear-gradient(135deg, #110826 0%, #240f47 50%, #0a0417 100%)",
            "surface": "rgba(31, 14, 59, 0.85)",
            "card": "rgba(45, 21, 84, 0.65)",
            "border": "rgba(217, 70, 239, 0.42)",
            "text": "#FDF4FF",
            "textMuted": "#E879F9",
            "glow": "0 0 32px rgba(217, 70, 239, 0.42)"
        }
    }
]

# ========================================================================================
# GRANULAR COURSE SIDEBAR & CURRICULUM SECTIONS SPECIFICATION
# ========================================================================================
COURSE_TRACKS: List[Dict[str, Any]] = [
    {
        "track_id": "embedded_systems",
        "title": "Embedded Systems & Real-Time IoT",
        "regulation": "Anna University R2023 / EC8702",
        "badge": "Core ECE",
        "icon": "⚡",
        "color": "#00F0B5",
        "description": "Cortex-M4 / Xtensa dual-core firmware, FreeRTOS preemption, DMA zero-copy, and bus protocol architectures.",
        "sections": [
            {
                "section_id": "intro",
                "title": "Introduction & Architecture",
                "icon": "📌",
                "summary": "ARM Cortex-M vs ESP32 Xtensa Dual-Core, memory maps, Harvard bus matrix, and Harvard architecture pipeline.",
                "lecture_id": "embed_01_intro",
                "starter_code": "// FreeRTOS Task Scheduling Starter\n#include <Arduino.h>\n\nvoid TaskSensor(void *pvParameters) {\n  for(;;) {\n    Serial.println(\"[Sensor] ADC sample: 3.28V\");\n    vTaskDelay(pdMS_TO_TICKS(1000));\n  }\n}\n\nvoid setup() {\n  Serial.begin(115200);\n  xTaskCreate(TaskSensor, \"SensorTask\", 2048, NULL, 2, NULL);\n}\nvoid loop() {}",
                "circuit_sim": "ESP32 + Dual I2C BME280 Sensor Hub"
            },
            {
                "section_id": "course_material",
                "title": "Course Material & Datasheets",
                "icon": "📖",
                "summary": "Unit I-V syllabus modules, NVIC priority grouping, scatter-gather DMA, and SPI/I2C/UART timing diagrams.",
                "lecture_id": "embed_02_dma",
                "starter_code": "// DMA Circular Buffer Stream\n#define BUFFER_SIZE 512\nuint8_t rx_buffer[BUFFER_SIZE] __attribute__((aligned(4)));\nvoid init_dma_stream() {\n  // Configure DMA peripheral-to-memory\n}",
                "circuit_sim": "Cortex-M4 Bus Matrix & Circular DMA Buffer"
            },
            {
                "section_id": "daily_quiz",
                "title": "Daily Quiz (Timed MCQs)",
                "icon": "⚡",
                "summary": "5 daily timed technical questions testing FreeRTOS priorities, context switch latency, and ISR tail-chaining.",
                "lecture_id": "embed_03_quiz",
                "starter_code": "// Quiz Verification Harness\nbool verify_priority_inheritance(int low_prio, int high_prio) {\n  return (high_prio > low_prio);\n}",
                "circuit_sim": "Interactive Logic State Analyzer"
            },
            {
                "section_id": "assessments",
                "title": "Continuous Assessments (CAT 1 & 2)",
                "icon": "📝",
                "summary": "Internal Continuous Assessment Test question papers with rubrics, derivations, and timing trace diagrams.",
                "lecture_id": "embed_04_cat",
                "starter_code": "// CAT Derivation Benchmark\nfloat calculate_interrupt_latency(float t_detect, float t_push, float t_vector) {\n  return t_detect + t_push + t_vector;\n}",
                "circuit_sim": "Keysight Virtual DSO Timing Deck"
            },
            {
                "section_id": "assignments",
                "title": "Laboratory Assignments",
                "icon": "💻",
                "summary": "Wokwi firmware exercises: FreeRTOS priority queues, Mutex priority ceiling, and ESP32 deep-sleep modes.",
                "lecture_id": "embed_05_assign",
                "starter_code": "// Lab 04: FreeRTOS Mutex Lock\nSemaphoreHandle_t xMutex;\nvoid setup() {\n  xMutex = xSemaphoreCreateMutex();\n}",
                "circuit_sim": "Wokwi FreeRTOS Queue Simulator"
            },
            {
                "section_id": "mini_projects",
                "title": "Mini-Projects",
                "icon": "🛠️",
                "summary": "ESP32 RFID Smart Lab Attendance Node, battery LiPo discharge profiler, and BLE environmental node.",
                "lecture_id": "embed_06_miniproj",
                "starter_code": "// RFID RC522 SPI Gateway\n#include <SPI.h>\n#include <MFRC522.h>\n#define SS_PIN 5\n#define RST_PIN 22\nMFRC522 rfid(SS_PIN, RST_PIN);",
                "circuit_sim": "ESP32 + RC522 RFID Attendance Node"
            },
            {
                "section_id": "major_projects",
                "title": "Major Projects",
                "icon": "🚀",
                "summary": "Autonomous Hardware-in-the-Loop (HIL) Test Bench, Automotive CAN bus diagnostic gateway, and drone flight telemetry.",
                "lecture_id": "embed_07_majorproj",
                "starter_code": "// Automotive CAN Bus Sentinel\n#include <CAN.h>\nvoid setup() {\n  CAN.begin(500E3);\n}",
                "circuit_sim": "Automotive CAN Transceiver Simulation"
            }
        ]
    },
    {
        "track_id": "generative_ai",
        "title": "Generative AI & Edge Intelligence",
        "regulation": "ECE R2023 Advanced Elective",
        "badge": "TinyML & AI",
        "icon": "🧠",
        "color": "#D946EF",
        "description": "Transformers on edge microcontrollers, INT8 quantization, CMSIS-NN, tensor arenas, and acoustic anomaly detection.",
        "sections": [
            {
                "section_id": "intro",
                "title": "Introduction & Transformers for ECE",
                "icon": "📌",
                "summary": "Attention mechanisms on silicon, edge compute constraints, tensor dimensions, and quantized matrix multiplication.",
                "lecture_id": "ai_01_intro",
                "starter_code": "# Edge Attention Vector Matrix Multiply\nimport numpy as np\ndef edge_dot_product(q, k):\n    return np.dot(q, k.T) / np.sqrt(q.shape[-1])",
                "circuit_sim": "Systolic Array MAC Accelerator"
            },
            {
                "section_id": "course_material",
                "title": "Course Material & Quantization",
                "icon": "📖",
                "summary": "Full integer quantization (INT8), per-channel vs per-tensor scaling, depthwise separable convolutions, and CMSIS-NN.",
                "lecture_id": "ai_02_quant",
                "starter_code": "# INT8 Symmetric Quantization\ndef quantize_float_to_int8(val, scale, zero_point=0):\n    q = np.round(val / scale) + zero_point\n    return np.clip(q, -128, 127).astype(np.int8)",
                "circuit_sim": "Tensor Arena SRAM Allocator"
            },
            {
                "section_id": "daily_quiz",
                "title": "Daily Quiz (Timed MCQs)",
                "icon": "⚡",
                "summary": "5 daily timed MCQs on ReLU vs GELU in MCU firmware, MAC throughput, and SRAM arena budgeting.",
                "lecture_id": "ai_03_quiz",
                "starter_code": "# Quiz Logic Verification\ndef compute_macs(kernel_h, kernel_w, in_ch, out_ch):\n    return kernel_h * kernel_w * in_ch * out_ch",
                "circuit_sim": "Hardware Multiplier-Accumulator Deck"
            },
            {
                "section_id": "assessments",
                "title": "Continuous Assessments (CAT 1 & 2)",
                "icon": "📝",
                "summary": "Neural network latency calculation, flash memory mapping, and INT8 zero-point offset error modeling.",
                "lecture_id": "ai_04_cat",
                "starter_code": "# Arena Memory Footprint Estimator\ndef estimate_arena_bytes(layers):\n    return sum(l['inputs'] + l['weights'] + l['outputs'] for l in layers)",
                "circuit_sim": "Microcontroller Flash/RAM Visualizer"
            },
            {
                "section_id": "assignments",
                "title": "Laboratory Assignments",
                "icon": "💻",
                "summary": "Deploy keyword spotting (KWS) model on ESP32-S3 using TFLite Micro and evaluate accuracy vs power draw.",
                "lecture_id": "ai_05_assign",
                "starter_code": "// TFLite Micro Invoke Loop\n#include \"tensorflow/lite/micro/all_ops_resolver.h\"\nvoid invoke_inference() {\n  TfLiteStatus invoke_status = interpreter->Invoke();\n}",
                "circuit_sim": "ESP32-S3 I2S Microphone Audio Pipeline"
            },
            {
                "section_id": "mini_projects",
                "title": "Mini-Projects",
                "icon": "🛠️",
                "summary": "Gemini RAG local viva-voce tutor, hand gesture IMU classifier, and smart vibration monitor.",
                "lecture_id": "ai_06_miniproj",
                "starter_code": "# Anomaly Detection Autoencoder Threshold\ndef is_anomaly(loss, threshold=0.045):\n    return loss > threshold",
                "circuit_sim": "MPU-6050 6-Axis Motion Classifier"
            },
            {
                "section_id": "major_projects",
                "title": "Major Projects",
                "icon": "🚀",
                "summary": "Edge AI UAV structural vibration sentinel, real-time multi-sensor fusion, and autonomous TinyML vision camera.",
                "lecture_id": "ai_07_majorproj",
                "starter_code": "# Vision TinyML Detection Pipeline\nclass TinyMLSentinel:\n    def __init__(self, weights_path):\n        self.ready = True",
                "circuit_sim": "Edge AI Camera & Optical Flow Unit"
            }
        ]
    },
    {
        "track_id": "foundational_fundamentals",
        "title": "Foundational Fundamentals",
        "regulation": "Core Circuits, Digital & Math",
        "badge": "Foundations",
        "icon": "📐",
        "color": "#38BDF8",
        "description": "K-Maps, Quine-McCluskey, Op-Amps, small-signal Hybrid-Pi models, Bode plots, and GATE ECE mathematical rigor.",
        "sections": [
            {
                "section_id": "intro",
                "title": "Introduction to Circuits & Logic",
                "icon": "📌",
                "summary": "Kirchhoff laws, Thevenin/Norton equivalents, boolean algebra axioms, De Morgan laws, and semiconductor junctions.",
                "lecture_id": "found_01_intro",
                "starter_code": "// Digital Logic Gate Primitive Verification\nmodule logic_test(input a, input b, output y);\n  assign y = a ^ b; // XOR\nendmodule",
                "circuit_sim": "Interactive Dual Logic Gate Breadboard"
            },
            {
                "section_id": "course_material",
                "title": "Course Material & Formulas",
                "icon": "📖",
                "summary": "Op-Amp 741 golden rules, Miller compensation, BJT hybrid-pi r_pi and gm derivations, and Nyquist stability criteria.",
                "lecture_id": "found_02_analog",
                "starter_code": "# Small-Signal BJT Transconductance\ndef bjt_gm(ic_ma, vt_mv=26.0):\n    return ic_ma / vt_mv",
                "circuit_sim": "Op-Amp 741 Non-Inverting Amplifier"
            },
            {
                "section_id": "daily_quiz",
                "title": "Daily Quiz (Timed MCQs)",
                "icon": "⚡",
                "summary": "5 daily timed MCQs selected from Anna University semester exams and GATE ECE 2020-2026 archives.",
                "lecture_id": "found_03_quiz",
                "starter_code": "# GATE ECE Formula Check\ndef resonance_frequency(l_henry, c_farad):\n    import math\n    return 1.0 / (2 * math.pi * math.sqrt(l_henry * c_farad))",
                "circuit_sim": "RLC Series Resonant Circuit"
            },
            {
                "section_id": "assessments",
                "title": "Continuous Assessments (CAT 1 & 2)",
                "icon": "📝",
                "summary": "Active Butterworth filter order calculation, pole placement, and state-transition equation synthesis.",
                "lecture_id": "found_04_cat",
                "starter_code": "# Butterworth Filter Order\nimport math\ndef butterworth_order(ap_db, as_db, wp, ws):\n    num = math.log10((10**(as_db/10) - 1) / (10**(ap_db/10) - 1))\n    den = 2 * math.log10(ws / wp)\n    return math.ceil(num / den)",
                "circuit_sim": "2nd-Order Sallen-Key Low-Pass Filter"
            },
            {
                "section_id": "assignments",
                "title": "Laboratory Assignments",
                "icon": "💻",
                "summary": "LTspice frequency response Bode plot simulation, gain-bandwidth product measurement, and 4-variable K-Map minimization.",
                "lecture_id": "found_05_assign",
                "starter_code": "* LTspice SPICE Netlist Benchmark\nV1 in 0 AC 1\nR1 in out 1k\nC1 out 0 100n\n.ac dec 20 10 100k\n.backanno\n.end",
                "circuit_sim": "LTspice Virtual Bode Waveform Analyzer"
            },
            {
                "section_id": "mini_projects",
                "title": "Mini-Projects",
                "icon": "🛠️",
                "summary": "8-bit R-2R ladder digital-to-analog converter (DAC) and precision 555-timer astable multivibrator clock.",
                "lecture_id": "found_06_miniproj",
                "starter_code": "// 8-Bit R-2R DAC Output Formula\nfloat compute_dac_vout(uint8_t code, float vref=3.3) {\n  return (code / 256.0) * vref;\n}",
                "circuit_sim": "R-2R Ladder DAC & Precision Op-Amp Buffer"
            },
            {
                "section_id": "major_projects",
                "title": "Major Projects",
                "icon": "🚀",
                "summary": "FPGA 8-channel logic analyzer with cursor measurement tools, dual-slope integrating digital voltmeter instrument.",
                "lecture_id": "found_07_majorproj",
                "starter_code": "// Verilog Clock Divider (50MHz to 1kHz)\nmodule clk_div(input clk_in, output reg clk_out);\n  reg [15:0] count = 0;\n  always @(posedge clk_in) begin\n    if (count == 24999) begin\n      count <= 0;\n      clk_out <= ~clk_out;\n    end else count <= count + 1;\n  end\nendmodule",
                "circuit_sim": "FPGA 8-Channel Timing Diagram Analyzer"
            }
        ]
    }
]

# ========================================================================================
# DATABASE INITIALIZATION (SQLite WAL Mode)
# ========================================================================================
def init_workspace_themes_db(db_path: str = DB_PATH) -> None:
    """Initialize SQLite tables in WAL mode for theme preferences and workspace state."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        
        # User Theme Preferences
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workspace_theme_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                theme_id TEXT NOT NULL,
                theme_name TEXT NOT NULL,
                applied_at TEXT NOT NULL
            );
        """)
        
        # Resizable Workspace State Snapshots
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workspace_state_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                layout_mode TEXT NOT NULL,
                frames_visible TEXT NOT NULL,
                split_ratio TEXT NOT NULL,
                active_track TEXT NOT NULL,
                active_section TEXT NOT NULL,
                saved_at TEXT NOT NULL
            );
        """)
        
        conn.commit()
    finally:
        conn.close()


def save_theme_preference(theme_id: str, student_id: str = "2023MITEC042", db_path: str = DB_PATH) -> Dict[str, Any]:
    """Save or update student's selected theme preference."""
    init_workspace_themes_db(db_path)
    
    # Lookup theme
    theme = next((t for t in THEMES_CATALOG if t["id"] == theme_id), None)
    if not theme:
        raise ValueError(f"Theme '{theme_id}' not found in catalog.")
        
    now = datetime.now().isoformat()
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""
            INSERT INTO workspace_theme_preferences (student_id, theme_id, theme_name, applied_at)
            VALUES (?, ?, ?, ?)
        """, (student_id, theme["id"], theme["name"], now))
        conn.commit()
        return {
            "status": "success",
            "student_id": student_id,
            "theme_id": theme["id"],
            "theme_name": theme["name"],
            "applied_at": now
        }
    finally:
        conn.close()


def get_latest_theme_preference(student_id: str = "2023MITEC042", db_path: str = DB_PATH) -> Dict[str, Any]:
    """Retrieve student's latest theme preference (defaults to 'cyber-emerald')."""
    init_workspace_themes_db(db_path)
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute("""
            SELECT theme_id, theme_name, applied_at FROM workspace_theme_preferences
            WHERE student_id = ? ORDER BY id DESC LIMIT 1
        """, (student_id,))
        row = cur.fetchone()
        if row:
            return {"theme_id": row[0], "theme_name": row[1], "applied_at": row[2]}
        return {"theme_id": "cyber-emerald", "theme_name": "Cyber Emerald & Mint", "applied_at": None}
    finally:
        conn.close()


def calculate_equal_frame_split(visible_frames: Dict[str, bool]) -> Dict[str, Any]:
    """
    Calculate responsive dimensions and percentages for equal split based on active frames.
    Handles 1, 2, 3, or 4 active frames deterministically.
    """
    active_keys = [k for k, v in visible_frames.items() if v]
    count = len(active_keys)
    
    if count == 0:
        return {
            "active_count": 0,
            "layout_class": "hidden",
            "grid_template": "none",
            "frame_percentage": 0.0,
            "per_frame": {}
        }
    elif count == 1:
        return {
            "active_count": 1,
            "layout_class": "grid grid-cols-1 grid-rows-1 h-full",
            "grid_template": "1fr",
            "frame_percentage": 100.0,
            "per_frame": {active_keys[0]: 100.0}
        }
    elif count == 2:
        return {
            "active_count": 2,
            "layout_class": "grid grid-cols-1 md:grid-cols-2 h-full gap-4",
            "grid_template": "1fr 1fr",
            "frame_percentage": 50.0,
            "per_frame": {k: 50.0 for k in active_keys}
        }
    elif count == 3:
        return {
            "active_count": 3,
            "layout_class": "grid grid-cols-1 md:grid-cols-3 h-full gap-4",
            "grid_template": "1fr 1fr 1fr",
            "frame_percentage": 33.33,
            "per_frame": {k: 33.33 for k in active_keys}
        }
    else: # 4 frames: 2x2 equal grid
        return {
            "active_count": 4,
            "layout_class": "grid grid-cols-1 md:grid-cols-2 grid-rows-2 h-full gap-4",
            "grid_template": "repeat(2, 1fr) / repeat(2, 1fr)",
            "frame_percentage": 25.0,
            "per_frame": {k: 25.0 for k in active_keys}
        }


def save_workspace_snapshot(
    layout_mode: str,
    frames_visible: Dict[str, bool],
    split_ratio: Dict[str, float],
    active_track: str,
    active_section: str,
    student_id: str = "2023MITEC042",
    db_path: str = DB_PATH
) -> Dict[str, Any]:
    """Save an immutable snapshot of the user's workspace layout."""
    init_workspace_themes_db(db_path)
    now = datetime.now().isoformat()
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""
            INSERT INTO workspace_state_snapshots (
                student_id, layout_mode, frames_visible, split_ratio, active_track, active_section, saved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            layout_mode,
            json.dumps(frames_visible),
            json.dumps(split_ratio),
            active_track,
            active_section,
            now
        ))
        conn.commit()
        return {
            "status": "success",
            "student_id": student_id,
            "layout_mode": layout_mode,
            "saved_at": now
        }
    finally:
        conn.close()


def get_latest_workspace_snapshot(student_id: str = "2023MITEC042", db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieve the latest saved workspace configuration."""
    init_workspace_themes_db(db_path)
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute("""
            SELECT layout_mode, frames_visible, split_ratio, active_track, active_section, saved_at
            FROM workspace_state_snapshots
            WHERE student_id = ? ORDER BY id DESC LIMIT 1
        """, (student_id,))
        row = cur.fetchone()
        if row:
            return {
                "layout_mode": row[0],
                "frames_visible": json.loads(row[1]),
                "split_ratio": json.loads(row[2]),
                "active_track": row[3],
                "active_section": row[4],
                "saved_at": row[5]
            }
        return None
    finally:
        conn.close()
