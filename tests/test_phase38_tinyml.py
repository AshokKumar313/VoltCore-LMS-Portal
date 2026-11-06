"""
========================================================================================
VoltCore Apex Academia - Phase 38 Test Suite
Module: TinyML & Edge AI Neural Network Inference Engine Tests
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
========================================================================================
"""

import os
import sqlite3
import pytest
from backend.tinyml_engine import (
    TinyMlEngine,
    EDGE_MCU_TARGETS,
    TINYML_MODELS,
    tinyml_engine
)


def test_engine_initialization_and_wal(tmp_path):
    """Verifies SQLite tables and WAL mode are initialized correctly."""
    db_file = str(tmp_path / "test_tinyml_init.db")
    engine = TinyMlEngine(db_path=db_file)
    conn = engine._get_connection()
    cursor = conn.cursor()

    # Verify journal mode is WAL
    journal_mode = cursor.execute("PRAGMA journal_mode;").fetchone()[0]
    assert journal_mode.upper() == "WAL"

    # Verify tables exist
    tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    assert "tinyml_benchmarks" in tables
    assert "tinyml_confusion_matrices" in tables
    conn.close()


def test_target_mcu_profiles(tmp_path):
    """Verifies MCU target profiles and hardware specifications."""
    db_file = str(tmp_path / "test_tinyml_mcus.db")
    engine = TinyMlEngine(db_path=db_file)
    mcus = engine.get_target_mcus()

    assert len(mcus) == 4
    mcu_keys = [m["key"] for m in mcus]
    assert "ESP32_S3" in mcu_keys
    assert "NANO_33_BLE" in mcu_keys
    assert "STM32F746" in mcu_keys
    assert "RP2040_PICO" in mcu_keys

    esp32 = next(m for m in mcus if m["key"] == "ESP32_S3")
    assert esp32["clock_mhz"] == 240.0
    assert esp32["sram_kb"] == 512.0
    assert esp32["simd_speedup_int8"] == 4.0


def test_model_catalog_profiles(tmp_path):
    """Verifies pre-trained TinyML model definitions and shapes."""
    db_file = str(tmp_path / "test_tinyml_models.db")
    engine = TinyMlEngine(db_path=db_file)
    models = engine.get_models()

    assert len(models) == 4
    model_keys = [m["key"] for m in models]
    assert "KEYWORD_SPOTTING_DSCNN" in model_keys
    assert "VIBRATION_ANOMALY_AUTOENCODER" in model_keys
    assert "VISUAL_WAKE_WORDS_MOBILENET" in model_keys
    assert "IMU_GESTURE_1DCNN" in model_keys

    kws = next(m for m in models if m["key"] == "KEYWORD_SPOTTING_DSCNN")
    assert len(kws["classes"]) == 4
    assert kws["total_macs"] == 1840000
    assert kws["depthwise_separable_layers"] == 4


def test_quantization_flash_ram_metrics(tmp_path):
    """Verifies INT8 vs FP32 vs FP16 flash savings and quantization scaling."""
    db_file = str(tmp_path / "test_tinyml_quant.db")
    engine = TinyMlEngine(db_path=db_file)

    res_int8 = engine.run_benchmark(
        target_mcu="ESP32_S3",
        model_key="KEYWORD_SPOTTING_DSCNN",
        precision_mode="INT8"
    )
    res_fp32 = engine.run_benchmark(
        target_mcu="ESP32_S3",
        model_key="KEYWORD_SPOTTING_DSCNN",
        precision_mode="FP32"
    )

    assert res_int8["status"] == "SUCCESS"
    assert res_int8["quantization"]["flash_savings_pct"] > 70.0
    assert res_int8["quantization"]["symmetric_scale"] > 0.0
    assert res_int8["quantization"]["zero_point"] == 0
    assert res_int8["quantization"]["depthwise_separable_reduction_factor"] > 1.0

    # INT8 flash footprint must be significantly smaller than FP32
    assert res_int8["quantization"]["flash_footprint_kb"] < res_fp32["quantization"]["flash_footprint_kb"]


def test_inference_latency_and_fps_calc(tmp_path):
    """Verifies cycle-accurate latency, FPS throughput, and energy calculations."""
    db_file = str(tmp_path / "test_tinyml_latency.db")
    engine = TinyMlEngine(db_path=db_file)

    res_fast = engine.run_benchmark(
        target_mcu="ESP32_S3",
        model_key="KEYWORD_SPOTTING_DSCNN",
        precision_mode="INT8"
    )
    res_slow = engine.run_benchmark(
        target_mcu="RP2040_PICO",
        model_key="KEYWORD_SPOTTING_DSCNN",
        precision_mode="INT8"
    )

    assert res_fast["performance"]["inference_latency_ms"] < res_slow["performance"]["inference_latency_ms"]
    assert res_fast["performance"]["throughput_fps"] > res_slow["performance"]["throughput_fps"]
    assert res_fast["performance"]["energy_uj_per_infer"] > 0.0
    assert res_fast["performance"]["effective_cpu_cycles"] > 0
    assert res_fast["performance"]["flash_fits"] is True
    assert res_fast["performance"]["ram_fits"] is True


def test_confusion_matrix_and_macro_metrics(tmp_path):
    """Verifies confusion matrix macro accuracy, precision, recall, and F1 calculations."""
    db_file = str(tmp_path / "test_tinyml_cm.db")
    engine = TinyMlEngine(db_path=db_file)

    # Perfect diagonal 2x2 confusion matrix
    perfect_matrix = [
        [100, 0, 0, 0],
        [0, 100, 0, 0],
        [0, 0, 100, 0],
        [0, 0, 0, 100]
    ]
    res = engine.run_benchmark(
        target_mcu="STM32F746",
        model_key="KEYWORD_SPOTTING_DSCNN",
        precision_mode="INT8",
        custom_matrix=perfect_matrix
    )

    acc = res["accuracy_metrics"]
    assert acc["accuracy_pct"] == 100.0
    assert acc["precision_macro_pct"] == 100.0
    assert acc["recall_macro_pct"] == 100.0
    assert acc["f1_score_pct"] == 100.0


def test_benchmark_execution_and_persistence(tmp_path):
    """Verifies SQLite persistence and RFC-4180 CSV export."""
    db_file = str(tmp_path / "test_tinyml_persist.db")
    engine = TinyMlEngine(db_path=db_file)

    engine.run_benchmark(target_mcu="ESP32_S3", model_key="KEYWORD_SPOTTING_DSCNN", precision_mode="INT8")
    engine.run_benchmark(target_mcu="NANO_33_BLE", model_key="VIBRATION_ANOMALY_AUTOENCODER", precision_mode="FP32")

    history = engine.get_benchmark_history(limit=10)
    assert len(history) == 2
    assert history[0]["target_mcu"] in ["ESP32_S3", "NANO_33_BLE"]

    csv_data = engine.export_benchmarks_csv()
    assert "Benchmark_ID,Target_MCU,Model_Key,Precision" in csv_data
    lines = [line.strip() for line in csv_data.strip().split("\n") if line.strip()]
    assert len(lines) == 3  # Header + 2 data rows


def test_privacy_invariants_and_attribution():
    """Strictly verifies zero leakage of private credentials and confirms public author attribution."""
    with open("backend/tinyml_engine.py", "r", encoding="utf-8") as f:
        code_str = f.read()

    # Zero leakage
    assert "9597382878" not in code_str
    assert "ashokkumar2008313@gmail.com" not in code_str

    # Public attribution
    assert "Ashok Kumar A" in code_str
    assert "2023MITEC042" in code_str
    assert "Anna University" in code_str
