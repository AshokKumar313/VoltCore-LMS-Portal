"""
========================================================================================
VoltCore Apex Academia - Phase 38: TinyML & Edge AI Neural Network Inference Engine
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Hardware Safe: Zero background polling loops, SQLite WAL mode, cool thermal footprint.
========================================================================================
"""

import os
import sqlite3
import json
import csv
import io
import math
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Database path in workspace root
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "voltcore_telemetry.db")

# Edge AI Target Microcontrollers
EDGE_MCU_TARGETS: Dict[str, Dict[str, Any]] = {
    "ESP32_S3": {
        "key": "ESP32_S3",
        "name": "Espressif ESP32-S3 (Xtensa Dual-Core LX7 with Vector PIE)",
        "vendor": "Espressif Systems",
        "core": "Xtensa 32-bit LX7 with Vector Instructions",
        "clock_mhz": 240.0,
        "sram_kb": 512.0,
        "flash_kb": 8192.0,
        "simd_speedup_int8": 4.0,
        "simd_speedup_fp32": 1.2,
        "active_power_mw": 396.0,
        "supported_precisions": ["INT8", "FP16", "FP32"]
    },
    "NANO_33_BLE": {
        "key": "NANO_33_BLE",
        "name": "Arduino Nano 33 BLE Sense (Nordic nRF52840)",
        "vendor": "Arduino / Nordic Semi",
        "core": "ARM Cortex-M4F with FPU & CMSIS-NN",
        "clock_mhz": 64.0,
        "sram_kb": 256.0,
        "flash_kb": 1024.0,
        "simd_speedup_int8": 2.0,
        "simd_speedup_fp32": 1.0,
        "active_power_mw": 49.5,
        "supported_precisions": ["INT8", "FP32"]
    },
    "STM32F746": {
        "key": "STM32F746",
        "name": "STMicroelectronics STM32F746G-DISCO (ARM Cortex-M7)",
        "vendor": "STMicroelectronics",
        "core": "ARM Cortex-M7 Dual-Issue with L1 Cache",
        "clock_mhz": 216.0,
        "sram_kb": 320.0,
        "flash_kb": 1024.0,
        "simd_speedup_int8": 3.0,
        "simd_speedup_fp32": 1.5,
        "active_power_mw": 330.0,
        "supported_precisions": ["INT8", "FP16", "FP32"]
    },
    "RP2040_PICO": {
        "key": "RP2040_PICO",
        "name": "Raspberry Pi Pico (RP2040 Dual ARM Cortex-M0+)",
        "vendor": "Raspberry Pi",
        "core": "Dual ARM Cortex-M0+ (Software Emulation)",
        "clock_mhz": 133.0,
        "sram_kb": 264.0,
        "flash_kb": 2048.0,
        "simd_speedup_int8": 1.0,
        "simd_speedup_fp32": 0.4,
        "active_power_mw": 82.5,
        "supported_precisions": ["INT8", "FP32"]
    }
}

# Pre-Trained Benchmark TinyML Models
TINYML_MODELS: Dict[str, Dict[str, Any]] = {
    "KEYWORD_SPOTTING_DSCNN": {
        "key": "KEYWORD_SPOTTING_DSCNN",
        "title": "Keyword Spotting DS-CNN (MicroSpeech)",
        "category": "Audio Acoustic Keyword Classification",
        "input_shape": "1x49x40 (MFCC Spectrogram)",
        "classes": ["yes", "no", "silence", "unknown"],
        "architecture_summary": "Conv2D(64, 3x3) -> 4x DepthwiseSeparableConv2D(64, 3x3) -> AvgPool -> Dense(4)",
        "weights_count": 23600,
        "total_macs": 1840000,
        "fp32_flash_kb": 94.4,
        "int8_flash_kb": 24.1,
        "fp16_flash_kb": 47.8,
        "ram_arena_kb": 16.4,
        "depthwise_separable_layers": 4,
        "base_accuracy_int8": 94.5,
        "base_accuracy_fp32": 95.1,
        "default_confusion_matrix": [
            [238, 5, 2, 5],
            [4, 240, 1, 5],
            [1, 0, 248, 1],
            [6, 4, 2, 238]
        ]
    },
    "VIBRATION_ANOMALY_AUTOENCODER": {
        "key": "VIBRATION_ANOMALY_AUTOENCODER",
        "title": "Predictive Maintenance Vibration Anomaly Autoencoder",
        "category": "Industrial Vibration Anomaly Detection",
        "input_shape": "1x128 (FFT Vibration Spectrum)",
        "classes": ["normal", "bearing_fault", "unbalance", "misalignment"],
        "architecture_summary": "Dense(128->64) -> Dense(64->16) -> Dense(16->64) -> Dense(64->128)",
        "weights_count": 18432,
        "total_macs": 36864,
        "fp32_flash_kb": 73.7,
        "int8_flash_kb": 18.9,
        "fp16_flash_kb": 37.2,
        "ram_arena_kb": 8.2,
        "depthwise_separable_layers": 0,
        "base_accuracy_int8": 96.2,
        "base_accuracy_fp32": 96.8,
        "default_confusion_matrix": [
            [245, 2, 1, 2],
            [3, 242, 3, 2],
            [1, 2, 244, 3],
            [2, 3, 2, 243]
        ]
    },
    "VISUAL_WAKE_WORDS_MOBILENET": {
        "key": "VISUAL_WAKE_WORDS_MOBILENET",
        "title": "Visual Wake Words MobileNetV1 (0.25)",
        "category": "Computer Vision Person Detection",
        "input_shape": "96x96x1 (Grayscale Image)",
        "classes": ["person", "no_person"],
        "architecture_summary": "Conv2D(8, 3x3) -> 13x DepthwiseSeparableConv2D -> AvgPool -> Dense(2)",
        "weights_count": 210500,
        "total_macs": 11200000,
        "fp32_flash_kb": 842.0,
        "int8_flash_kb": 215.5,
        "fp16_flash_kb": 425.0,
        "ram_arena_kb": 48.6,
        "depthwise_separable_layers": 13,
        "base_accuracy_int8": 92.1,
        "base_accuracy_fp32": 92.8,
        "default_confusion_matrix": [
            [462, 38],
            [41, 459]
        ]
    },
    "IMU_GESTURE_1DCNN": {
        "key": "IMU_GESTURE_1DCNN",
        "title": "Wearable IMU 6-Axis Gesture Classifier (1D-CNN)",
        "category": "Motion Gesture Recognition",
        "input_shape": "100x6 (Temporal Accel + Gyro Window)",
        "classes": ["idle", "wave", "lift", "punch"],
        "architecture_summary": "Conv1D(16, 5) -> MaxPool -> Conv1D(32, 3) -> GlobalAvgPool -> Dense(4)",
        "weights_count": 7420,
        "total_macs": 145000,
        "fp32_flash_kb": 29.7,
        "int8_flash_kb": 7.8,
        "fp16_flash_kb": 15.1,
        "ram_arena_kb": 4.6,
        "depthwise_separable_layers": 0,
        "base_accuracy_int8": 95.8,
        "base_accuracy_fp32": 96.2,
        "default_confusion_matrix": [
            [246, 2, 1, 1],
            [3, 241, 4, 2],
            [1, 3, 244, 2],
            [2, 2, 3, 243]
        ]
    }
}


class TinyMlEngine:
    """
    Simulates TinyML INT8 quantization, Depthwise Separable Convolution efficiency,
    RAM tensor arena estimation, inference latency, energy consumption, and confusion matrix profiling.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_sqlite_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns SQLite connection configured with WAL journaling."""
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite_tables(self) -> None:
        """Initializes tables for TinyML benchmarks and confusion matrices."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tinyml_benchmarks (
                    id TEXT PRIMARY KEY,
                    target_mcu TEXT NOT NULL,
                    model_key TEXT NOT NULL,
                    precision_mode TEXT NOT NULL,
                    weights_count INTEGER NOT NULL,
                    flash_usage_kb REAL NOT NULL,
                    ram_tensor_arena_kb REAL NOT NULL,
                    total_macs INTEGER NOT NULL,
                    inference_latency_ms REAL NOT NULL,
                    fps REAL NOT NULL,
                    energy_uj REAL NOT NULL,
                    f1_score REAL NOT NULL,
                    student_id TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tinyml_confusion_matrices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    benchmark_id TEXT NOT NULL,
                    matrix_json TEXT NOT NULL,
                    class_labels_json TEXT NOT NULL,
                    precision_macro REAL NOT NULL,
                    recall_macro REAL NOT NULL,
                    accuracy_pct REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(benchmark_id) REFERENCES tinyml_benchmarks(id)
                );
            """)
            conn.commit()

    def get_available_targets(self) -> List[Dict[str, Any]]:
        """Returns catalog of supported Edge AI microcontrollers."""
        return list(EDGE_MCU_TARGETS.values())

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Returns catalog of pre-trained TinyML model benchmarks."""
        return list(TINYML_MODELS.values())

    def calculate_quantization_metrics(
        self,
        model_key: str = "KEYWORD_SPOTTING_DSCNN",
        precision_mode: str = "INT8"
    ) -> Dict[str, Any]:
        """
        Calculates quantization scale factor, zero point, Flash storage reduction,
        and Depthwise Separable Convolution efficiency factor.
        """
        model = TINYML_MODELS.get(model_key, TINYML_MODELS["KEYWORD_SPOTTING_DSCNN"])
        p_mode = precision_mode.upper()

        # Symmetric affine quantization: S = (max - min) / 255
        fp32_kb = model["fp32_flash_kb"]
        if p_mode == "INT8":
            active_kb = model["int8_flash_kb"]
            scale_factor = 0.0078125  # (1.0 - (-1.0)) / 256
            zero_point = 0
            bits_per_weight = 8
        elif p_mode == "FP16":
            active_kb = model["fp16_flash_kb"]
            scale_factor = 1.0
            zero_point = 0
            bits_per_weight = 16
        else:
            active_kb = fp32_kb
            scale_factor = 1.0
            zero_point = 0
            bits_per_weight = 32

        flash_savings_pct = round(((fp32_kb - active_kb) / fp32_kb) * 100.0, 2)

        # Depthwise Separable Convolution Cost Ratio vs Standard Convolution
        # Ratio = (K_w * K_h + C_out) / (K_w * K_h * C_out)
        k_size = 3
        c_out = 64
        dsc_ratio = round((k_size * k_size + c_out) / (k_size * k_size * c_out), 4)
        comp_reduction_factor = round(1.0 / dsc_ratio, 1)

        return {
            "model_key": model["key"],
            "precision_mode": p_mode,
            "bits_per_weight": bits_per_weight,
            "scale_factor": scale_factor,
            "symmetric_scale": scale_factor,
            "zero_point": zero_point,
            "unquantized_flash_kb": fp32_kb,
            "quantized_flash_kb": active_kb,
            "flash_footprint_kb": active_kb,
            "flash_savings_pct": flash_savings_pct,
            "ram_arena_kb": model["ram_arena_kb"],
            "depthwise_conv_ratio": dsc_ratio,
            "depthwise_separable_reduction_factor": comp_reduction_factor,
            "compute_reduction_vs_std_conv": f"{comp_reduction_factor}x"
        }

    def get_target_mcus(self) -> List[Dict[str, Any]]:
        """Alias for get_available_targets."""
        return self.get_available_targets()

    def get_models(self) -> List[Dict[str, Any]]:
        """Alias for get_available_models."""
        return self.get_available_models()

    def run_benchmark(
        self,
        target_mcu: str = "ESP32_S3",
        model_key: str = "KEYWORD_SPOTTING_DSCNN",
        precision_mode: str = "INT8",
        student_id: str = "2023MITEC042",
        custom_matrix: Optional[List[List[int]]] = None
    ) -> Dict[str, Any]:
        """Wrapper for benchmark_inference."""
        return self.benchmark_inference(
            target_mcu=target_mcu,
            model_key=model_key,
            precision_mode=precision_mode,
            student_id=student_id,
            custom_matrix=custom_matrix
        )

    def benchmark_inference(
        self,
        target_mcu: str = "ESP32_S3",
        model_key: str = "KEYWORD_SPOTTING_DSCNN",
        precision_mode: str = "INT8",
        student_id: str = "2023MITEC042",
        custom_matrix: Optional[List[List[int]]] = None
    ) -> Dict[str, Any]:
        """
        Executes cycle-accurate inference latency, throughput (FPS), energy consumption,
        and confusion matrix calculation. Persists benchmark to SQLite WAL.
        """
        mcu = EDGE_MCU_TARGETS.get(target_mcu, EDGE_MCU_TARGETS["ESP32_S3"])
        model = TINYML_MODELS.get(model_key, TINYML_MODELS["KEYWORD_SPOTTING_DSCNN"])
        p_mode = precision_mode.upper()

        quant_metrics = self.calculate_quantization_metrics(model_key, p_mode)
        total_macs = model["total_macs"]

        # Precision compute penalty multiplier
        if p_mode == "INT8":
            simd_speedup = mcu["simd_speedup_int8"]
            precision_penalty = 1.0
            accuracy = model["base_accuracy_int8"]
        elif p_mode == "FP16":
            simd_speedup = (mcu["simd_speedup_int8"] + mcu["simd_speedup_fp32"]) / 2.0
            precision_penalty = 1.6
            accuracy = round((model["base_accuracy_int8"] + model["base_accuracy_fp32"]) / 2.0, 2)
        else:  # FP32
            simd_speedup = mcu["simd_speedup_fp32"]
            precision_penalty = 3.2
            accuracy = model["base_accuracy_fp32"]

        # Effective CPU cycles calculation
        effective_cycles = (total_macs / simd_speedup) * precision_penalty
        latency_ms = round((effective_cycles / (mcu["clock_mhz"] * 1000.0)), 2)
        fps = round(1000.0 / latency_ms, 1) if latency_ms > 0 else 0.0

        # Energy per inference: E (uJ) = Power (mW) * Latency (ms)
        energy_uj = round(mcu["active_power_mw"] * latency_ms, 2)

        # Check Memory Constraints
        flash_fits = quant_metrics["quantized_flash_kb"] <= mcu["flash_kb"]
        ram_fits = model["ram_arena_kb"] <= mcu["sram_kb"]

        # Confusion Matrix and Macro Metrics
        matrix = custom_matrix if custom_matrix is not None else model["default_confusion_matrix"]
        classes = model["classes"]
        total_samples = sum(sum(row) for row in matrix)
        correct_samples = sum(matrix[i][i] for i in range(len(classes)))
        if custom_matrix is not None and total_samples > 0:
            accuracy = round((correct_samples / total_samples) * 100.0, 2)

        # Precision and Recall per class
        precisions = []
        recalls = []
        for i in range(len(classes)):
            tp = matrix[i][i]
            fp = sum(matrix[r][i] for r in range(len(classes)) if r != i)
            fn = sum(matrix[i][c] for c in range(len(classes)) if c != i)
            p = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
            r = (tp / (tp + fn)) if (tp + fn) > 0 else 0.0
            precisions.append(p)
            recalls.append(r)

        precision_macro = round((sum(precisions) / len(precisions)) * 100.0, 2)
        recall_macro = round((sum(recalls) / len(recalls)) * 100.0, 2)
        f1_score = round(2 * (precision_macro * recall_macro) / (precision_macro + recall_macro), 2) if (precision_macro + recall_macro) > 0 else 0.0

        bench_id = f"TINYML_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(2).hex()}"
        now_str = datetime.now().isoformat()

        # Persist to SQLite WAL
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO tinyml_benchmarks (
                    id, target_mcu, model_key, precision_mode,
                    weights_count, flash_usage_kb, ram_tensor_arena_kb,
                    total_macs, inference_latency_ms, fps,
                    energy_uj, f1_score, student_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                bench_id, mcu["key"], model["key"], p_mode,
                model["weights_count"], quant_metrics["quantized_flash_kb"], model["ram_arena_kb"],
                total_macs, latency_ms, fps,
                energy_uj, f1_score, student_id, now_str
            ))
            conn.execute("""
                INSERT INTO tinyml_confusion_matrices (
                    benchmark_id, matrix_json, class_labels_json,
                    precision_macro, recall_macro, accuracy_pct, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (
                bench_id, json.dumps(matrix), json.dumps(classes),
                precision_macro, recall_macro, accuracy, now_str
            ))
            conn.commit()

        return {
            "status": "SUCCESS",
            "benchmark_id": bench_id,
            "target_mcu": mcu,
            "model": {
                "key": model["key"],
                "title": model["title"],
                "category": model["category"],
                "input_shape": model["input_shape"],
                "classes": classes,
                "weights_count": model["weights_count"],
                "total_macs": total_macs
            },
            "precision_mode": p_mode,
            "quantization": quant_metrics,
            "performance": {
                "inference_latency_ms": latency_ms,
                "throughput_fps": fps,
                "energy_uj_per_infer": energy_uj,
                "effective_cpu_cycles": int(effective_cycles),
                "flash_fits": flash_fits,
                "ram_fits": ram_fits
            },
            "accuracy_metrics": {
                "accuracy_pct": accuracy,
                "precision_macro_pct": precision_macro,
                "recall_macro_pct": recall_macro,
                "f1_score_pct": f1_score
            },
            "confusion_matrix": matrix,
            "platform_lead": "Ashok Kumar A (2023MITEC042)",
            "institution": "MIT Campus, Anna University",
            "created_at": now_str
        }

    def get_benchmark_history(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Returns recent TinyML benchmark profiling records from SQLite WAL."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tinyml_benchmarks
                ORDER BY created_at DESC
                LIMIT ?;
            """, (limit,)).fetchall()
            return [dict(r) for r in rows]

    def export_benchmarks_csv(self) -> str:
        """Exports TinyML profiling benchmarks formatted as RFC-4180 CSV."""
        history = self.get_benchmark_history(limit=50)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        writer.writerow([
            "Benchmark_ID", "Target_MCU", "Model_Key", "Precision",
            "Weights_Count", "Flash_KB", "RAM_Arena_KB", "Total_MACs",
            "Latency_ms", "FPS", "Energy_uJ", "F1_Score", "Created_At"
        ])

        for h in history:
            writer.writerow([
                h["id"],
                h["target_mcu"],
                h["model_key"],
                h["precision_mode"],
                h["weights_count"],
                h["flash_usage_kb"],
                h["ram_tensor_arena_kb"],
                h["total_macs"],
                h["inference_latency_ms"],
                h["fps"],
                h["energy_uj"],
                h["f1_score"],
                h["created_at"]
            ])

        return output.getvalue()


# Singleton Instance
tinyml_engine = TinyMlEngine()
