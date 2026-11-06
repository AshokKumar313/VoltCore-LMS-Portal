"""
========================================================================================
VoltCore Apex Academia - Phase B: Advanced Course Content & ECE Textbooks
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Features:
  - Feature 211: Interactive ECE Textbook & Curriculum Chapter Reader
  - Feature 212: Bookmark Manager with Section Offsets
  - Feature 213: PDF & Markdown Annotation Workspace
  - Feature 214: Component Specification Comparison Table (MCU / Silicon)
  - Feature 215: Technical Block & Circuit Diagram Library Viewer
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU usage.
========================================================================================
"""

import os
import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")

# Curated Anna University R2023 ECE Textbooks & Chapter Catalog
TEXTBOOK_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "cortex_m_guide",
        "title": "The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors",
        "author": "Joseph Yiu",
        "course_code": "EC8702",
        "course_name": "Embedded Systems & Real-Time Operating Systems",
        "edition": "3rd Edition",
        "chapters": [
            {
                "id": "ch1_arch",
                "number": 1,
                "title": "Cortex-M4 Architecture, Register Set & Harvard Bus Matrix",
                "summary": "Covers R0-R12 general-purpose registers, SP (MSP & PSP), LR, PC, PRIMASK, FAULTMASK, and 3-stage pipeline architecture.",
                "read_time_mins": 25,
                "key_equations": [
                    "Interrupt Latency = T_detect + T_stack_push (12 cycles) + T_vector_fetch (6 cycles)",
                    "Tail-chaining latency = 6 cycles (skips register pop/push)"
                ],
                "content_markdown": "### 1. Cortex-M4 Core Architecture\n\nThe ARM Cortex-M4 is a high-performance 32-bit RISC processor core featuring Harvard architecture with separate ICode, DCode, and System buses. It integrates hardware single-cycle MAC instructions and IEEE 754 single-precision FPU.\n\n#### 1.1 Stack Pointers: MSP vs PSP\n- **MSP (Main Stack Pointer):** Default stack used during reset and Exception/Interrupt handlers.\n- **PSP (Process Stack Pointer):** Used exclusively by RTOS tasks during Thread Mode execution to isolate task stack overruns from kernel memory."
            },
            {
                "id": "ch2_nvic",
                "number": 2,
                "title": "Nested Vectored Interrupt Controller (NVIC) & Tail-Chaining",
                "summary": "Detailed analysis of priority grouping (PRIGROUP), preemption priority vs sub-priority, late-arrival servicing, and zero-jitter tail-chaining.",
                "read_time_mins": 30,
                "key_equations": [
                    "PRIGROUP[10:8]: Split into Preemption Bits [7:x] and Subpriority Bits [x-1:0]",
                    "Tail-chaining latency saving = 12 cycles"
                ],
                "content_markdown": "### 2. Nested Vectored Interrupt Controller (NVIC)\n\nThe NVIC supports up to 240 external physical interrupts with 8 to 256 programmable priority levels. The hardware automatically pushes R0-R3, R12, LR, PC, and xPSR onto the active stack when an exception occurs."
            },
            {
                "id": "ch3_dma",
                "number": 3,
                "title": "Direct Memory Access (DMA) & Zero-Copy Circular Streams",
                "summary": "Peripheral-to-Memory, Memory-to-Peripheral, and Memory-to-Memory DMA architecture with double-buffering and FIFO threshold interrupts.",
                "read_time_mins": 28,
                "key_equations": [
                    "DMA Throughput = (Bus Clock Frequency * Bus Width in Bytes) * (1 - Arbitration Contention Loss)"
                ],
                "content_markdown": "### 3. Direct Memory Access (DMA) Architecture\n\nDMA relieves the main CPU core from bulk data transfers between high-speed peripherals (ADC, SPI, UART) and SRAM. Circular mode automatically wraps buffer pointers upon reaching buffer boundaries."
            }
        ]
    },
    {
        "id": "sedra_smith_circuits",
        "title": "Microelectronic Circuits: Theory & Design",
        "author": "Adel S. Sedra & Kenneth C. Smith",
        "course_code": "EC3452",
        "course_name": "Analog Integrated Circuits & Signals",
        "edition": "8th Edition",
        "chapters": [
            {
                "id": "ch1_opamp",
                "number": 1,
                "title": "Operational Amplifier Miller Frequency Compensation & Pole-Splitting",
                "summary": "Small-signal AC frequency analysis of two-stage CMOS op-amps, Miller effect capacitor Cc, dominant pole shifting, and phase margin stability.",
                "read_time_mins": 35,
                "key_equations": [
                    "Dominant Pole: p1' = 1 / (gm2 * R1 * R2 * Cc)",
                    "Non-Dominant Pole: p2' = gm2 / C2",
                    "Unity-Gain Bandwidth: ft = gm1 / (2 * pi * Cc)"
                ],
                "content_markdown": "### 1. Two-Stage CMOS Op-Amp Frequency Response\n\nConnecting compensation capacitor Cc across the high-gain inverting second stage introduces pole-splitting. This pushes the dominant pole to a very low frequency while shoving the second pole far beyond the unity-gain frequency ft, securing phase margin > 60 degrees."
            },
            {
                "id": "ch2_cmrr",
                "number": 2,
                "title": "Differential Amplifiers, Tail Resistance & CMRR Degradation",
                "summary": "Large and small-signal analysis of differential pairs with non-ideal tail current sources (finite Rss), common-mode gain Acm, and mismatch errors.",
                "read_time_mins": 25,
                "key_equations": [
                    "CMRR = |Adm / Acm| = 2 * gm * Rss / (delta-gm / gm)",
                    "Common-Mode Gain: Acm = - (delta-Rd / (2 * Rss))"
                ],
                "content_markdown": "### 2. Differential Pair CMRR\n\nIn ideal symmetric differential pairs, common-mode variations do not alter differential output. Finite tail resistance Rss and transistor parameter mismatches convert common-mode inputs into differential output voltages, degrading CMRR."
            }
        ]
    },
    {
        "id": "tinyml_warden",
        "title": "TinyML: Machine Learning with TensorFlow Lite on Arduino and Ultra-Low-Power Microcontrollers",
        "author": "Pete Warden & Daniel Situnayake",
        "course_code": "EC3712",
        "course_name": "TinyML & Edge AI Intelligence",
        "edition": "1st Edition",
        "chapters": [
            {
                "id": "ch1_quant",
                "number": 1,
                "title": "INT8 Quantization, Zero-Point Offsets & Scale Factors",
                "summary": "Mathematical conversion between 32-bit floating point weights/activations and 8-bit quantized signed integers for microcontroller execution.",
                "read_time_mins": 30,
                "key_equations": [
                    "Real Value = Scale * (Quantized_Int8 - ZeroPoint)",
                    "Scale S = (max_real - min_real) / 255.0"
                ],
                "content_markdown": "### 1. Quantization for Microcontrollers\n\nQuantization transforms 32-bit floating-point tensors into 8-bit integers, shrinking flash footprint by 75% and accelerating matrix multiplications using native MCU SIMD/DSP instructions."
            },
            {
                "id": "ch2_arena",
                "number": 2,
                "title": "Tensor Arena SRAM Allocation & Memory Budgeting",
                "summary": "Static SRAM memory management in TensorFlow Lite Micro, tensor arenas, buffer reuse across sequential convolution layers.",
                "read_time_mins": 20,
                "key_equations": [
                    "Arena Size = max(layer_i_input + layer_i_weights + layer_i_output) + alignment_overhead"
                ],
                "content_markdown": "### 2. Tensor Arena Budgeting\n\nMicrocontrollers lack virtual memory or dynamic heap allocators. TFLite Micro preallocates a contiguous byte buffer called Tensor Arena where tensor buffers are reused between layers."
            }
        ]
    }
];

# Silicon & Microcontroller Datasheet Comparison Database (Feature 214)
DATASHEET_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "esp32_wroom_32",
        "name": "Espressif ESP32-WROOM-32",
        "architecture": "Xtensa Dual-Core 32-bit LX6",
        "clock_mhz": 240,
        "flash_kb": 4096,
        "sram_kb": 520,
        "operating_voltage": "2.7V - 3.6V (3.3V Typ)",
        "dma_channels": 8,
        "adc_channels": "18 channels (12-bit SAR)",
        "hardware_timers": "4x 64-bit general purpose",
        "connectivity": "Wi-Fi 802.11 b/g/n + BLE 4.2",
        "active_power_ma": 68.0,
        "deep_sleep_ua": 5.0,
        "target_application": "IoT Edge Nodes, Wi-Fi Gateways, HIL Telemetry",
        "typical_price_inr": 290
    },
    {
        "id": "stm32f401re",
        "name": "STMicroelectronics STM32F401RE",
        "architecture": "ARM Cortex-M4 32-bit with FPU",
        "clock_mhz": 84,
        "flash_kb": 512,
        "sram_kb": 96,
        "operating_voltage": "1.7V - 3.6V (3.3V Typ)",
        "dma_channels": 16,
        "adc_channels": "16 channels (12-bit, 2.4 MSPS)",
        "hardware_timers": "8x (16-bit & 32-bit)",
        "connectivity": "USB 2.0 OTG, 3x SPI, 3x I2C, 3x USART",
        "active_power_ma": 19.5,
        "deep_sleep_ua": 2.2,
        "target_application": "Real-Time Embedded Control, DSP Filtering, Industrial Automation",
        "typical_price_inr": 480
    },
    {
        "id": "rp2040_pico",
        "name": "Raspberry Pi RP2040",
        "architecture": "Dual ARM Cortex-M0+ 32-bit",
        "clock_mhz": 133,
        "flash_kb": 2048,
        "sram_kb": 264,
        "operating_voltage": "1.8V - 3.3V (3.3V Typ)",
        "dma_channels": 12,
        "adc_channels": "4 channels (12-bit, 500 kSPS)",
        "hardware_timers": "1x 64-bit timer + 8x PWM blocks",
        "connectivity": "2x SPI, 2x I2C, 2x UART, 8x PIO State Machines",
        "active_power_ma": 22.0,
        "deep_sleep_ua": 180.0,
        "target_application": "Programmable I/O (PIO), Protocol Emulation, Education",
        "typical_price_inr": 350
    },
    {
        "id": "nrf52840_ble",
        "name": "Nordic Semiconductor nRF52840",
        "architecture": "ARM Cortex-M4 32-bit with FPU",
        "clock_mhz": 64,
        "flash_kb": 1024,
        "sram_kb": 256,
        "operating_voltage": "1.7V - 5.5V",
        "dma_channels": 8,
        "adc_channels": "8 channels (12-bit EasyDMA SAADC)",
        "hardware_timers": "5x 32-bit timers + RTC",
        "connectivity": "Bluetooth 5.3 Low Energy, Zigbee, Thread, NFC",
        "active_power_ma": 4.8,
        "deep_sleep_ua": 0.4,
        "target_application": "Ultra-Low-Power Wearables, Medical Sensors, TinyML Edge",
        "typical_price_inr": 720
    }
];

# Technical Block & Circuit Diagram Library (Feature 215)
DIAGRAM_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "diag_cortex_m4_bus",
        "title": "ARM Cortex-M4 Harvard Bus Matrix & NVIC Pipeline",
        "category": "Microcontroller Architecture",
        "description": "Visualizes separate ICode, DCode, and System 32-bit AHB-Lite interconnect buses and private peripheral bus (PPB).",
        "layers": ["Core Registers", "AHB Bus Matrix", "Flash / SRAM Interface", "NVIC Controller", "DMA Channels"],
        "svg_thumbnail": "cortex_m4_bus_matrix.svg"
    },
    {
        "id": "diag_esp32_dual_core",
        "title": "ESP32 Xtensa Dual-Core LX6 & ULP Coprocessor",
        "category": "Microcontroller Architecture",
        "description": "Dual core PRO_CPU and APP_CPU memory bus sharing with Ultra-Low-Power (ULP) RTC coprocessor.",
        "layers": ["PRO_CPU (Core 0)", "APP_CPU (Core 1)", "RTC ULP Coprocessor", "Peripheral Crossbar", "Radio Subsystem"],
        "svg_thumbnail": "esp32_dual_core.svg"
    },
    {
        "id": "diag_opamp_miller",
        "title": "Two-Stage CMOS Op-Amp with Miller Frequency Compensation",
        "category": "Analog Circuit Schematics",
        "description": "Differential input stage (M1-M4) coupled to common-source gain stage (M5) with Cc compensation capacitor.",
        "layers": ["Differential Pair", "Current Mirror Active Load", "Miller Capacitor Cc", "Output Buffer Stage"],
        "svg_thumbnail": "opamp_miller_compensation.svg"
    },
    {
        "id": "diag_tinyml_arena",
        "title": "TinyML Tensor Arena SRAM Memory Budgeting Map",
        "category": "TinyML & DSP Systems",
        "description": "Memory mapping of input activations, persistent model state, and scratch buffer reuse.",
        "layers": ["Input Tensor", "Weight Flash Mapping", "Layer Scratch Buffers", "Output Classification"],
        "svg_thumbnail": "tinyml_tensor_arena.svg"
    }
];


class TextbookDatasheetEngine:
    """
    Backend service engine for Phase B:
    - Features 211-213: Textbook reader, bookmarks, annotations
    - Features 214-215: Datasheet comparisons and technical diagram viewer
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_db(self) -> None:
        with self._lock:
            conn = self._get_connection()
            try:
                # Feature 212: Textbook Bookmarks
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS textbook_bookmarks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        book_id TEXT NOT NULL,
                        chapter_id TEXT NOT NULL,
                        section_title TEXT NOT NULL,
                        page_offset INTEGER DEFAULT 1,
                        created_at TEXT NOT NULL
                    );
                """)

                # Feature 213: PDF & Markdown Annotations
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS textbook_annotations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        book_id TEXT NOT NULL,
                        chapter_id TEXT NOT NULL,
                        selected_quote TEXT NOT NULL,
                        student_note TEXT NOT NULL,
                        color_tag TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)

                # Seed sample bookmark & annotation for student if not present
                cur = conn.execute("SELECT id FROM textbook_bookmarks WHERE student_id = ?", ("2023MITEC042",))
                if not cur.fetchone():
                    now = datetime.now(timezone.utc).isoformat()
                    conn.execute("""
                        INSERT INTO textbook_bookmarks (student_id, book_id, chapter_id, section_title, page_offset, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, ("2023MITEC042", "cortex_m_guide", "ch2_nvic", "Tail-Chaining Latency Derivation", 48, now))

                    conn.execute("""
                        INSERT INTO textbook_annotations (student_id, book_id, chapter_id, selected_quote, student_note, color_tag, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, ("2023MITEC042", "sedra_smith_circuits", "ch1_opamp", "Dominant Pole p1' = 1 / (gm2 * R1 * R2 * Cc)", "Crucial formula for CAT-1 Q3 calculation!", "Yellow", now))

                conn.commit()
            finally:
                conn.close()

    def get_textbooks(self) -> List[Dict[str, Any]]:
        """Return all curated textbooks in the catalog."""
        return TEXTBOOK_CATALOG

    def get_textbook_by_id(self, book_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve textbook and its chapters by book_id."""
        return next((b for b in TEXTBOOK_CATALOG if b["id"] == book_id), None)

    def save_bookmark(
        self,
        student_id: str,
        book_id: str,
        chapter_id: str,
        section_title: str,
        page_offset: int = 1
    ) -> Dict[str, Any]:
        """Save a new chapter/section bookmark (Feature 212)."""
        with self._lock:
            conn = self._get_connection()
            try:
                now = datetime.now(timezone.utc).isoformat()
                cur = conn.execute("""
                    INSERT INTO textbook_bookmarks (student_id, book_id, chapter_id, section_title, page_offset, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (student_id, book_id, chapter_id, section_title, page_offset, now))
                conn.commit()
                return {
                    "status": "success",
                    "bookmark_id": cur.lastrowid,
                    "student_id": student_id,
                    "book_id": book_id,
                    "chapter_id": chapter_id,
                    "section_title": section_title,
                    "created_at": now
                }
            finally:
                conn.close()

    def get_bookmarks(self, student_id: str = "2023MITEC042") -> List[Dict[str, Any]]:
        """Retrieve all active bookmarks for a student."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.execute("""
                    SELECT id, student_id, book_id, chapter_id, section_title, page_offset, created_at
                    FROM textbook_bookmarks
                    WHERE student_id = ?
                    ORDER BY id DESC
                """, (student_id,))
                return [dict(row) for row in cur.fetchall()]
            finally:
                conn.close()

    def save_annotation(
        self,
        student_id: str,
        book_id: str,
        chapter_id: str,
        selected_quote: str,
        student_note: str,
        color_tag: str = "Yellow"
    ) -> Dict[str, Any]:
        """Record an inline text annotation/note (Feature 213)."""
        if not selected_quote or not student_note:
            raise ValueError("Quote and note cannot be empty.")

        with self._lock:
            conn = self._get_connection()
            try:
                now = datetime.now(timezone.utc).isoformat()
                cur = conn.execute("""
                    INSERT INTO textbook_annotations (student_id, book_id, chapter_id, selected_quote, student_note, color_tag, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (student_id, book_id, chapter_id, selected_quote, student_note, color_tag, now))
                conn.commit()
                return {
                    "status": "success",
                    "annotation_id": cur.lastrowid,
                    "student_id": student_id,
                    "book_id": book_id,
                    "chapter_id": chapter_id,
                    "color_tag": color_tag,
                    "created_at": now
                }
            finally:
                conn.close()

    def get_annotations(self, student_id: str = "2023MITEC042", book_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve student annotations, optionally filtered by book."""
        with self._lock:
            conn = self._get_connection()
            try:
                if book_id:
                    cur = conn.execute("""
                        SELECT id, student_id, book_id, chapter_id, selected_quote, student_note, color_tag, created_at
                        FROM textbook_annotations
                        WHERE student_id = ? AND book_id = ?
                        ORDER BY id DESC
                    """, (student_id, book_id))
                else:
                    cur = conn.execute("""
                        SELECT id, student_id, book_id, chapter_id, selected_quote, student_note, color_tag, created_at
                        FROM textbook_annotations
                        WHERE student_id = ?
                        ORDER BY id DESC
                    """, (student_id,))
                return [dict(row) for row in cur.fetchall()]
            finally:
                conn.close()

    def compare_datasheets(self, component_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Compare silicon component specifications side-by-side (Feature 214).
        If component_ids is empty, returns all components.
        """
        if not component_ids:
            return DATASHEET_CATALOG

        matched = [c for c in DATASHEET_CATALOG if c["id"] in component_ids]
        return matched if matched else DATASHEET_CATALOG

    def get_diagram_library(self) -> List[Dict[str, Any]]:
        """Return the technical block & circuit diagram catalog (Feature 215)."""
        return DIAGRAM_CATALOG
