"""
========================================================================================
VoltCore Apex Academia - Phase 37 Test Suite
Module: ARM Cortex-M NVIC & DMA Channel Simulator Tests
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
========================================================================================
"""

import os
import sqlite3
import pytest
from backend.dma_nvic_engine import (
    DmaNvicEngine,
    ARM_MCU_TARGETS,
    INTERRUPT_SOURCES,
    dma_nvic_engine
)


def test_engine_initialization_and_wal(tmp_path):
    """Verifies SQLite tables and WAL mode are initialized correctly."""
    db_file = str(tmp_path / "test_dma_nvic_init.db")
    engine = DmaNvicEngine(db_path=db_file)
    conn = engine._get_connection()
    cursor = conn.cursor()

    # Verify journal mode is WAL
    journal_mode = cursor.execute("PRAGMA journal_mode;").fetchone()[0]
    assert journal_mode.upper() == "WAL"

    # Verify tables exist
    tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    assert "dma_nvic_simulations" in tables
    assert "dma_timeline_events" in tables
    conn.close()


def test_get_available_mcus_and_interrupts(tmp_path):
    """Verifies MCU profiles and interrupt source catalogs."""
    db_file = str(tmp_path / "test_dma_catalog.db")
    engine = DmaNvicEngine(db_path=db_file)
    mcus = engine.get_available_mcus()
    irqs = engine.get_interrupt_catalog()

    assert len(mcus) >= 4
    mcu_keys = [m["key"] for m in mcus]
    assert "STM32F401RE" in mcu_keys
    assert "STM32H743ZI" in mcu_keys
    assert "NXP_LPC55S69" in mcu_keys
    assert "SAMD51J19" in mcu_keys

    irq_names = [i["name"] for i in irqs]
    assert "EXTI0_IRQn" in irq_names
    assert "TIM2_IRQn" in irq_names
    assert "ADC1_IRQn" in irq_names


def test_simulate_nvic_tail_chaining(tmp_path):
    """Verifies 12-cycle hardware entry stacking vs. 6-cycle tail-chain latency."""
    db_file = str(tmp_path / "test_dma_tailchain.db")
    engine = DmaNvicEngine(db_path=db_file)
    res = engine.simulate_nvic_and_dma(
        mcu_key="STM32F401RE",
        priority_group=3,
        trigger_interrupts=["TIM2_IRQn", "EXTI0_IRQn"],
        dma_mode="CIRCULAR_BUFFER",
        student_id="2023MITEC042"
    )

    assert res["status"] == "SUCCESS"
    assert res["mcu_target"]["key"] == "STM32F401RE"
    assert res["tail_chaining_occurred"] is True
    assert res["metrics"]["entry_latency_cycles"] == 12
    assert res["metrics"]["tail_chain_cycles"] == 6
    assert res["metrics"]["cycles_saved_per_tail_chain"] == 18

    # Verify tail chaining event exists in timeline
    tail_chain_events = [ev for ev in res["timeline_events"] if ev["cpu_state"] == "TAIL_CHAINING"]
    assert len(tail_chain_events) > 0


def test_simulate_dma_circular_buffer(tmp_path):
    """Verifies circular buffer DMA stream, throughput calculation, and HTIF watermark."""
    db_file = str(tmp_path / "test_dma_circular.db")
    engine = DmaNvicEngine(db_path=db_file)
    res = engine.simulate_nvic_and_dma(
        mcu_key="STM32F401RE",
        dma_mode="CIRCULAR_BUFFER",
        data_width_bytes=2,  # 16-bit ADC samples
        buffer_size_items=512,
        core_clock_mhz=84.0,
        student_id="2023MITEC042"
    )

    assert res["status"] == "SUCCESS"
    assert res["total_transfer_bytes"] == 1024  # 512 * 2
    assert res["throughput_mbps"] > 0
    assert res["cpu_overhead_saved_pct"] > 95.0

    # Verify Half-Transfer event
    htif_events = [ev for ev in res["timeline_events"] if ev["dma_state"] == "DMA_HTIF_FLAG"]
    assert len(htif_events) == 1
    assert htif_events[0]["buffer_head"] == 256  # 512 / 2


def test_simulate_dma_scatter_gather(tmp_path):
    """Verifies scatter-gather chained DMA mode and CPU cycle savings."""
    db_file = str(tmp_path / "test_dma_scatter.db")
    engine = DmaNvicEngine(db_path=db_file)
    res = engine.simulate_nvic_and_dma(
        mcu_key="STM32H743ZI",
        dma_mode="SCATTER_GATHER",
        data_width_bytes=4,  # 32-bit words
        buffer_size_items=1024,
        core_clock_mhz=480.0,
        student_id="2023MITEC042"
    )

    assert res["status"] == "SUCCESS"
    assert res["dma_mode"] == "SCATTER_GATHER"
    assert res["total_transfer_bytes"] == 4096  # 1024 * 4
    assert res["cpu_overhead_saved_pct"] > 97.0


def test_bus_matrix_cycle_stealing(tmp_path):
    """Verifies AHB bus matrix contention when CPU executes concurrently with DMA."""
    db_file = str(tmp_path / "test_dma_bus.db")
    engine = DmaNvicEngine(db_path=db_file)
    res_concurrent = engine.simulate_nvic_and_dma(
        mcu_key="STM32F401RE",
        enable_concurrent_cpu=True,
        student_id="2023MITEC042"
    )
    res_isolated = engine.simulate_nvic_and_dma(
        mcu_key="STM32F401RE",
        enable_concurrent_cpu=False,
        student_id="2023MITEC042"
    )

    assert res_concurrent["bus_contention_pct"] > 0.0
    assert res_isolated["bus_contention_pct"] == 0.0


def test_history_and_csv_export(tmp_path):
    """Verifies persistence in SQLite WAL and RFC-4180 CSV export."""
    db_file = str(tmp_path / "test_dma_csv.db")
    engine = DmaNvicEngine(db_path=db_file)
    engine.simulate_nvic_and_dma(mcu_key="STM32F401RE")
    engine.simulate_nvic_and_dma(mcu_key="STM32H743ZI")

    history = engine.get_simulation_history(limit=10)
    assert len(history) == 2

    csv_str = engine.export_dma_csv(mcu_key="STM32F401RE")
    assert "Cycle,Time_ns,CPU_State,DMA_State" in csv_str
    lines = [line.strip() for line in csv_str.strip().split("\n") if line.strip()]
    assert len(lines) > 10


def test_privacy_invariants_and_attribution():
    """Strictly verifies zero leakage of private credentials and confirms public author attribution."""
    with open("backend/dma_nvic_engine.py", "r", encoding="utf-8") as f:
        code_str = f.read()

    # Zero leakage
    assert "9597382878" not in code_str
    assert "ashokkumar2008313@gmail.com" not in code_str

    # Public attribution
    assert "Ashok Kumar A" in code_str
    assert "2023MITEC042" in code_str
    assert "Anna University" in code_str
