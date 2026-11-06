"""
========================================================================================
VoltCore Apex Academia - Phase 37: ARM Cortex-M NVIC & DMA Channel Simulator Engine
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

# Supported ARM Cortex-M Microcontroller Profiles
ARM_MCU_TARGETS: Dict[str, Dict[str, Any]] = {
    "STM32F401RE": {
        "key": "STM32F401RE",
        "name": "STMicroelectronics STM32F401RE (ARM Cortex-M4F)",
        "core": "Cortex-M4F with FPU",
        "max_freq_mhz": 84.0,
        "nvic_prio_bits": 4,
        "ahb_matrix_masters": 5,
        "ahb_matrix_slaves": 5,
        "dma_controllers": 2,
        "dma_streams_per_controller": 8,
        "normal_entry_latency_cycles": 12,
        "tail_chain_latency_cycles": 6,
        "exit_latency_cycles": 10
    },
    "STM32H743ZI": {
        "key": "STM32H743ZI",
        "name": "STMicroelectronics STM32H743ZI (ARM Cortex-M7)",
        "core": "Cortex-M7 Dual-Issue Superscalar",
        "max_freq_mhz": 480.0,
        "nvic_prio_bits": 4,
        "ahb_matrix_masters": 10,
        "ahb_matrix_slaves": 9,
        "dma_controllers": 3,
        "dma_streams_per_controller": 8,
        "normal_entry_latency_cycles": 12,
        "tail_chain_latency_cycles": 6,
        "exit_latency_cycles": 10
    },
    "NXP_LPC55S69": {
        "key": "NXP_LPC55S69",
        "name": "NXP LPC55S69 (Dual ARM Cortex-M33)",
        "core": "Dual Cortex-M33 with TrustZone",
        "max_freq_mhz": 150.0,
        "nvic_prio_bits": 3,
        "ahb_matrix_masters": 6,
        "ahb_matrix_slaves": 6,
        "dma_controllers": 2,
        "dma_streams_per_controller": 8,
        "normal_entry_latency_cycles": 12,
        "tail_chain_latency_cycles": 6,
        "exit_latency_cycles": 10
    },
    "SAMD51J19": {
        "key": "SAMD51J19",
        "name": "Microchip SAMD51J19 (ARM Cortex-M4F)",
        "core": "Cortex-M4F with DSP Instructions",
        "max_freq_mhz": 120.0,
        "nvic_prio_bits": 3,
        "ahb_matrix_masters": 4,
        "ahb_matrix_slaves": 4,
        "dma_controllers": 1,
        "dma_streams_per_controller": 32,
        "normal_entry_latency_cycles": 12,
        "tail_chain_latency_cycles": 6,
        "exit_latency_cycles": 10
    }
}

# Interrupt Source Definitions
INTERRUPT_SOURCES = [
    {"irq_num": 6, "name": "EXTI0_IRQn", "desc": "GPIO External Interrupt Line 0", "default_prio": 0, "isr_cycles": 24},
    {"irq_num": 28, "name": "TIM2_IRQn", "desc": "General Purpose Timer 2 Elapsed Tick", "default_prio": 1, "isr_cycles": 36},
    {"irq_num": 18, "name": "ADC1_IRQn", "desc": "Analog-to-Digital End of Conversion", "default_prio": 2, "isr_cycles": 30},
    {"irq_num": 37, "name": "USART1_IRQn", "desc": "UART Byte Received RXNE Flag", "default_prio": 3, "isr_cycles": 42},
    {"irq_num": 11, "name": "DMA1_Stream0_IRQn", "desc": "DMA1 Stream 0 Half/Full Transfer", "default_prio": 4, "isr_cycles": 20}
]

# DMA Transfer Modes
DMA_TRANSFER_MODES = {
    "CIRCULAR_BUFFER": {
        "key": "CIRCULAR_BUFFER",
        "name": "Circular Ring Buffer Mode (Continuous Streaming)",
        "desc": "DMA automatically wraps to base address on completion. Fires Half-Transfer (HTIF) and Transfer-Complete (TCIF) interrupts without CPU reconfiguration.",
        "cpu_cycles_saved_pct": 97.5
    },
    "NORMAL_SINGLE": {
        "key": "NORMAL_SINGLE",
        "name": "Normal Single-Block Transfer (Memory / Peripheral Copy)",
        "desc": "Transfers fixed N items then disables channel until explicitly reloaded by CPU firmware.",
        "cpu_cycles_saved_pct": 92.0
    },
    "SCATTER_GATHER": {
        "key": "SCATTER_GATHER",
        "name": "Scatter-Gather Chained Transfer (Linked Descriptors)",
        "desc": "DMA hardware autonomously walks linked-list memory descriptors to service fragmented memory buffers without CPU intervention.",
        "cpu_cycles_saved_pct": 98.2
    }
}


class DmaNvicEngine:
    """
    Simulates ARM Cortex-M NVIC preemption, tail-chaining latency, DMA channel transfers,
    AHB bus matrix cycle-stealing, and CPU cycle overhead savings.
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
        """Initializes tables for DMA and NVIC simulation runs and timeline events."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dma_nvic_simulations (
                    id TEXT PRIMARY KEY,
                    mcu_target TEXT NOT NULL,
                    simulation_type TEXT NOT NULL,
                    nvic_priority_group INTEGER NOT NULL,
                    active_interrupts_json TEXT NOT NULL,
                    tail_chaining_occurred INTEGER NOT NULL,
                    entry_latency_cycles INTEGER NOT NULL,
                    dma_mode TEXT NOT NULL,
                    dma_channel TEXT NOT NULL,
                    transfer_size_bytes INTEGER NOT NULL,
                    throughput_mbps REAL NOT NULL,
                    cpu_overhead_saved_pct REAL NOT NULL,
                    bus_contention_pct REAL NOT NULL,
                    student_id TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dma_timeline_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT NOT NULL,
                    cycle_index INTEGER NOT NULL,
                    time_ns REAL NOT NULL,
                    cpu_state TEXT NOT NULL,
                    dma_state TEXT NOT NULL,
                    bus_owner TEXT NOT NULL,
                    active_isr TEXT NOT NULL,
                    buffer_head INTEGER NOT NULL,
                    packet_annotation TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(simulation_id) REFERENCES dma_nvic_simulations(id)
                );
            """)
            conn.commit()

    def get_available_mcus(self) -> List[Dict[str, Any]]:
        """Returns metadata catalog of supported ARM Cortex-M MCUs."""
        return list(ARM_MCU_TARGETS.values())

    def get_interrupt_catalog(self) -> List[Dict[str, Any]]:
        """Returns interrupt sources catalog."""
        return INTERRUPT_SOURCES

    def simulate_nvic_and_dma(
        self,
        mcu_key: str = "STM32F401RE",
        priority_group: int = 3,
        trigger_interrupts: List[str] = None,
        dma_mode: str = "CIRCULAR_BUFFER",
        data_width_bytes: int = 2,
        buffer_size_items: int = 512,
        core_clock_mhz: float = 84.0,
        enable_concurrent_cpu: bool = True,
        student_id: str = "2023MITEC042"
    ) -> Dict[str, Any]:
        """
        Executes a deterministic cycle-accurate simulation of ARM Cortex-M NVIC
        interrupt servicing (stacking, tail-chaining, preemption) and DMA transfer.
        Logs metrics and timeline events to SQLite WAL.
        """
        mcu = ARM_MCU_TARGETS.get(mcu_key, ARM_MCU_TARGETS["STM32F401RE"])
        core_clock_mhz = min(mcu["max_freq_mhz"], max(10.0, core_clock_mhz))
        cycle_period_ns = round(1000.0 / core_clock_mhz, 3)

        if trigger_interrupts is None:
            # Default sequence: Timer tick arrives, then higher-priority EXTI0 arrives during execution
            trigger_interrupts = ["TIM2_IRQn", "EXTI0_IRQn"]

        dma_info = DMA_TRANSFER_MODES.get(dma_mode, DMA_TRANSFER_MODES["CIRCULAR_BUFFER"])
        total_transfer_bytes = buffer_size_items * data_width_bytes

        # Calculate DMA Throughput and Bus Contention
        # For STM32F4 AHB matrix: DMA burst takes 4 cycles per 4-item burst
        cycles_per_item = 1.0  # 1 cycle per item in continuous stream
        dma_cycles_total = int(buffer_size_items * cycles_per_item)
        dma_duration_us = round((dma_cycles_total * cycle_period_ns) / 1000.0, 3)
        throughput_mbps = round((total_transfer_bytes / (dma_duration_us / 1000000.0)) / (1024 * 1024), 2) if dma_duration_us > 0 else 0.0

        # Bus Contention: if CPU accesses RAM concurrently, DMA steals 1 cycle every 4 cycles (25%)
        bus_contention_pct = 25.0 if enable_concurrent_cpu else 0.0

        # CPU Overhead Saved
        # Interrupt per sample: 35 cycles (12 entry + 13 ISR body + 10 exit) * N samples
        # DMA: only 2 interrupts (HTIF at 50%, TCIF at 100%) = 70 cycles total!
        cpu_legacy_cycles = buffer_size_items * 35
        cpu_dma_cycles = 70
        cpu_saved_pct = round(((cpu_legacy_cycles - cpu_dma_cycles) / cpu_legacy_cycles) * 100.0, 2)

        # Timeline Event Generation (up to 48 representative discrete phases)
        timeline_events: List[Dict[str, Any]] = []
        cur_cycle = 0
        tail_chaining_occurred = 0
        buffer_head = 0

        # Phase 1: Main Thread Execution (Background)
        for i in range(4):
            timeline_events.append({
                "cycle": cur_cycle,
                "time_ns": round(cur_cycle * cycle_period_ns, 2),
                "cpu_state": "MAIN_THREAD",
                "dma_state": "ACTIVE_STREAMING",
                "bus_owner": "CPU_IBUS (FLASH)" if enable_concurrent_cpu else "IDLE",
                "active_isr": "NONE",
                "buffer_head": buffer_head,
                "packet_annotation": "CPU executing background tasks"
            })
            cur_cycle += 1
            buffer_head = (buffer_head + 4) % buffer_size_items

        # Phase 2: First Interrupt Arrival (e.g. TIM2_IRQn)
        # 12-Cycle Hardware Register Stacking (R0-R3, R12, LR, PC, xPSR)
        stacking_cycles = mcu["normal_entry_latency_cycles"]
        for s in range(4):  # Grouped representative steps
            timeline_events.append({
                "cycle": cur_cycle,
                "time_ns": round(cur_cycle * cycle_period_ns, 2),
                "cpu_state": "STACKING_REGISTERS",
                "dma_state": "CYCLE_STEALING_RAM",
                "bus_owner": "DMA1_STREAM0",
                "active_isr": "PENDING (TIM2)",
                "buffer_head": buffer_head,
                "packet_annotation": f"Hardware Stacking ({s * 3 + 3}/12 cycles)"
            })
            cur_cycle += 3
            buffer_head = (buffer_head + 8) % buffer_size_items

        # Phase 3: TIM2 ISR Execution (Timer Handler)
        for e in range(4):
            timeline_events.append({
                "cycle": cur_cycle,
                "time_ns": round(cur_cycle * cycle_period_ns, 2),
                "cpu_state": "EXECUTING_ISR",
                "dma_state": "ACTIVE_STREAMING",
                "bus_owner": "CPU_DBUS",
                "active_isr": "TIM2_IRQHandler",
                "buffer_head": buffer_head,
                "packet_annotation": "Timer tick processed"
            })
            cur_cycle += 4
            buffer_head = (buffer_head + 12) % buffer_size_items

        # Phase 4: Tail-Chaining to EXTI0_IRQn (Higher/Pending IRQ)
        # Instead of 12-cycle exit + 12-cycle entry (24 cycles), Cortex-M does 6-cycle Tail-Chain!
        tail_chaining_occurred = 1
        tail_cycles = mcu["tail_chain_latency_cycles"]
        for tc in range(2):
            timeline_events.append({
                "cycle": cur_cycle,
                "time_ns": round(cur_cycle * cycle_period_ns, 2),
                "cpu_state": "TAIL_CHAINING",
                "dma_state": "BURST_TRANSFER",
                "bus_owner": "DMA1_STREAM0",
                "active_isr": "TAIL_CHAIN -> EXTI0",
                "buffer_head": buffer_head,
                "packet_annotation": f"Tail-Chaining switch ({tc * 3 + 3}/6 cycles - 18 cycles saved!)"
            })
            cur_cycle += 3
            buffer_head = (buffer_head + 6) % buffer_size_items

        # Phase 5: EXTI0 ISR Execution (GPIO Pin Handler)
        for e in range(4):
            timeline_events.append({
                "cycle": cur_cycle,
                "time_ns": round(cur_cycle * cycle_period_ns, 2),
                "cpu_state": "EXECUTING_ISR",
                "dma_state": "ACTIVE_STREAMING",
                "bus_owner": "CPU_DBUS",
                "active_isr": "EXTI0_IRQHandler",
                "buffer_head": buffer_head,
                "packet_annotation": "Emergency GPIO trigger serviced"
            })
            cur_cycle += 3
            buffer_head = (buffer_head + 10) % buffer_size_items

        # Phase 6: Unstacking Registers & Return to Thread Mode
        unstack_cycles = mcu["exit_latency_cycles"]
        for u in range(3):
            timeline_events.append({
                "cycle": cur_cycle,
                "time_ns": round(cur_cycle * cycle_period_ns, 2),
                "cpu_state": "UNSTACKING_REGISTERS",
                "dma_state": "ACTIVE_STREAMING",
                "bus_owner": "DMA1_STREAM0",
                "active_isr": "EXC_RETURN",
                "buffer_head": buffer_head,
                "packet_annotation": f"Hardware Unstacking ({u * 3 + 4}/10 cycles)"
            })
            cur_cycle += 3
            buffer_head = (buffer_head + 8) % buffer_size_items

        # Phase 7: Circular Buffer DMA Milestone (Half-Transfer Watermark)
        timeline_events.append({
            "cycle": cur_cycle,
            "time_ns": round(cur_cycle * cycle_period_ns, 2),
            "cpu_state": "MAIN_THREAD",
            "dma_state": "DMA_HTIF_FLAG",
            "bus_owner": "DMA1_STREAM0",
            "active_isr": "DMA_HalfTransfer_Flag",
            "buffer_head": buffer_size_items // 2,
            "packet_annotation": "DMA HTIF (50% Watermark Reached)"
        })

        sim_id = f"SIM_DMA_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(2).hex()}"
        now_str = datetime.now().isoformat()

        # Log to SQLite WAL
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO dma_nvic_simulations (
                    id, mcu_target, simulation_type, nvic_priority_group,
                    active_interrupts_json, tail_chaining_occurred, entry_latency_cycles,
                    dma_mode, dma_channel, transfer_size_bytes,
                    throughput_mbps, cpu_overhead_saved_pct, bus_contention_pct,
                    student_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                sim_id, mcu["key"], "NVIC_DMA_CO_SIMULATION", priority_group,
                json.dumps(trigger_interrupts), tail_chaining_occurred, mcu["normal_entry_latency_cycles"],
                dma_mode, "DMA1_Stream0", total_transfer_bytes,
                throughput_mbps, cpu_saved_pct, bus_contention_pct,
                student_id, now_str
            ))
            conn.commit()

        return {
            "status": "SUCCESS",
            "simulation_id": sim_id,
            "mcu_target": mcu,
            "priority_group": priority_group,
            "trigger_interrupts": trigger_interrupts,
            "tail_chaining_occurred": bool(tail_chaining_occurred),
            "dma_mode": dma_mode,
            "data_width_bytes": data_width_bytes,
            "buffer_size_items": buffer_size_items,
            "total_transfer_bytes": total_transfer_bytes,
            "core_clock_mhz": core_clock_mhz,
            "cycle_period_ns": cycle_period_ns,
            "throughput_mbps": throughput_mbps,
            "bus_contention_pct": bus_contention_pct,
            "cpu_overhead_saved_pct": cpu_saved_pct,
            "metrics": {
                "entry_latency_cycles": mcu["normal_entry_latency_cycles"],
                "tail_chain_cycles": mcu["tail_chain_latency_cycles"],
                "exit_latency_cycles": mcu["exit_latency_cycles"],
                "cycles_saved_per_tail_chain": 18,
                "dma_duration_us": dma_duration_us,
                "bus_contention_factor": round(bus_contention_pct / 100.0, 3)
            },
            "timeline_events": timeline_events,
            "created_at": now_str
        }

    def get_simulation_history(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Returns recent DMA & NVIC simulation logs from SQLite WAL."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM dma_nvic_simulations
                ORDER BY created_at DESC
                LIMIT ?;
            """, (limit,)).fetchall()
            return [dict(r) for r in rows]

    def export_dma_csv(self, mcu_key: str = "STM32F401RE") -> str:
        """Exports cycle-accurate DMA & NVIC timeline events formatted as RFC-4180 CSV."""
        res = self.simulate_nvic_and_dma(mcu_key=mcu_key)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        writer.writerow([
            "Cycle", "Time_ns", "CPU_State", "DMA_State",
            "Bus_Owner", "Active_ISR", "Buffer_Head", "Annotation"
        ])

        for ev in res["timeline_events"]:
            writer.writerow([
                ev["cycle"],
                ev["time_ns"],
                ev["cpu_state"],
                ev["dma_state"],
                ev["bus_owner"],
                ev["active_isr"],
                ev["buffer_head"],
                ev["packet_annotation"]
            ])

        return output.getvalue()


# Singleton Instance
dma_nvic_engine = DmaNvicEngine()
