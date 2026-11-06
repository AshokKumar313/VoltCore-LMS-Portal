"""
========================================================================================
VoltCore Apex Academia - Phase 36: Peripheral Bus Protocols Analyzer Engine
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

# Supported Peripheral Bus Protocols
BUS_PROTOCOLS = {
    "SPI": {
        "name": "Serial Peripheral Interface (SPI)",
        "type": "Full-Duplex Synchronous Serial",
        "lines": ["CS", "SCLK", "MOSI", "MISO"],
        "modes": {
            "MODE_0": {"cpol": 0, "cpha": 0, "desc": "Clock Idle LOW, Sample on Rising Edge, Shift on Falling"},
            "MODE_1": {"cpol": 0, "cpha": 1, "desc": "Clock Idle LOW, Shift on Rising Edge, Sample on Falling"},
            "MODE_2": {"cpol": 1, "cpha": 0, "desc": "Clock Idle HIGH, Sample on Falling Edge, Shift on Rising"},
            "MODE_3": {"cpol": 1, "cpha": 1, "desc": "Clock Idle HIGH, Shift on Falling Edge, Sample on Rising"}
        },
        "devices": [
            {
                "key": "SPI_W25Q64_FLASH",
                "name": "Winbond W25Q64 (64Mb SPI NOR Flash)",
                "cmd_hex": "0x9F",
                "cmd_name": "JEDEC_ID",
                "reg_hex": "0x00",
                "response_hex": "EF 40 17",
                "default_mode": "MODE_0",
                "default_clk_khz": 1000.0
            },
            {
                "key": "SPI_MAX7219_LED",
                "name": "Maxim MAX7219 (8-Digit LED Driver)",
                "cmd_hex": "0x09",
                "cmd_name": "DECODE_MODE",
                "reg_hex": "0x09",
                "response_hex": "00",
                "default_mode": "MODE_0",
                "default_clk_khz": 500.0
            },
            {
                "key": "SPI_MCP3008_ADC",
                "name": "Microchip MCP3008 (10-bit 8-Ch SPI ADC)",
                "cmd_hex": "0x01",
                "cmd_name": "START_CH0",
                "reg_hex": "0x80",
                "response_hex": "02 8A",
                "default_mode": "MODE_0",
                "default_clk_khz": 1000.0
            }
        ]
    },
    "I2C": {
        "name": "Inter-Integrated Circuit (I2C)",
        "type": "Half-Duplex Synchronous Multi-Master",
        "lines": ["SCL", "SDA"],
        "speeds": {
            "STANDARD": {"freq_khz": 100.0, "t_clk_us": 10.0, "desc": "Standard Mode (100 kHz)"},
            "FAST": {"freq_khz": 400.0, "t_clk_us": 2.5, "desc": "Fast Mode (400 kHz)"},
            "FAST_PLUS": {"freq_khz": 1000.0, "t_clk_us": 1.0, "desc": "Fast Mode Plus (1.0 MHz)"}
        },
        "devices": [
            {
                "key": "I2C_MPU6050",
                "name": "InvenSense MPU-6050 (6-Axis IMU)",
                "address_7bit": "0x68",
                "reg_hex": "0x75",
                "reg_name": "WHO_AM_I",
                "response_hex": "0x68",
                "default_speed": "STANDARD"
            },
            {
                "key": "I2C_BMP280",
                "name": "Bosch BMP280 (Barometric Pressure Sensor)",
                "address_7bit": "0x76",
                "reg_hex": "0xD0",
                "reg_name": "CHIP_ID",
                "response_hex": "0x58",
                "default_speed": "STANDARD"
            },
            {
                "key": "I2C_SSD1306_OLED",
                "name": "Solomon SSD1306 (128x64 OLED Controller)",
                "address_7bit": "0x3C",
                "reg_hex": "0x00",
                "reg_name": "COMMAND_STREAM",
                "response_hex": "0xAF",
                "default_speed": "FAST"
            }
        ]
    },
    "UART": {
        "name": "Universal Asynchronous Receiver/Transmitter (UART)",
        "type": "Full-Duplex Asynchronous Serial",
        "lines": ["TX", "RX"],
        "baud_rates": [9600, 19200, 38400, 57600, 115200],
        "parity_options": ["NONE", "EVEN", "ODD"],
        "devices": [
            {
                "key": "UART_GPS_NMEA",
                "name": "u-blox NEO-6M (GPS NMEA Receiver)",
                "default_baud": 9600,
                "tx_payload": "$PMTK000*32\\r\\n",
                "rx_payload": "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47\\r\\n"
            },
            {
                "key": "UART_ESP32_AT",
                "name": "Espressif ESP32-WROOM (Wi-Fi AT Command Node)",
                "default_baud": 115200,
                "tx_payload": "AT+GMR\\r\\n",
                "rx_payload": "AT version:2.2.0.0\\r\\nOK\\r\\n"
            },
            {
                "key": "UART_HC05_BT",
                "name": "HC-05 Bluetooth SPP Serial Module",
                "default_baud": 38400,
                "tx_payload": "AT+VERSION\\r\\n",
                "rx_payload": "+VERSION:2.0-20100601\\r\\nOK\\r\\n"
            }
        ]
    }
}


class PeripheralBusEngine:
    """
    Simulates SPI, I2C, and UART transactions, generates bit-accurate digital waveforms,
    computes timing metrics and bus overhead, and persists transaction logs in SQLite WAL.
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
        """Initializes tables for peripheral bus transactions and waveform traces."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS peripheral_bus_transactions (
                    id TEXT PRIMARY KEY,
                    protocol TEXT NOT NULL,
                    device_name TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    address_hex TEXT NOT NULL,
                    register_hex TEXT NOT NULL,
                    payload_hex TEXT NOT NULL,
                    data_length INTEGER NOT NULL,
                    duration_us REAL NOT NULL,
                    baud_or_clock_khz REAL NOT NULL,
                    status TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS peripheral_bus_waveforms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT NOT NULL,
                    sample_index INTEGER NOT NULL,
                    time_us REAL NOT NULL,
                    line1_name TEXT NOT NULL,
                    line1_val INTEGER NOT NULL,
                    line2_name TEXT NOT NULL,
                    line2_val INTEGER NOT NULL,
                    line3_name TEXT NOT NULL,
                    line3_val INTEGER NOT NULL,
                    line4_name TEXT NOT NULL,
                    line4_val INTEGER NOT NULL,
                    packet_annotation TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(transaction_id) REFERENCES peripheral_bus_transactions(id)
                );
            """)
            conn.commit()

    def get_protocol_presets(self) -> Dict[str, Any]:
        """Returns metadata catalog of all supported protocols and device presets."""
        return BUS_PROTOCOLS

    def simulate_spi_transaction(
        self,
        mode_key: str = "MODE_0",
        clock_khz: float = 1000.0,
        tx_bytes: List[int] = None,
        rx_bytes: List[int] = None,
        device_name: str = "Winbond W25Q64 Flash",
        student_id: str = "2023MITEC042"
    ) -> Dict[str, Any]:
        """
        Simulates an SPI transaction with CPOL/CPHA clock polarity, CS assertion, MOSI, and MISO traces.
        """
        if tx_bytes is None:
            tx_bytes = [0x9F, 0x00, 0x00, 0x00]  # JEDEC ID Command + 3 dummy cycles
        if rx_bytes is None:
            rx_bytes = [0x00, 0xEF, 0x40, 0x17]  # Manufacturer + Device ID

        clock_khz = max(50.0, min(clock_khz, 20000.0))
        t_half_clk_us = round((1000.0 / clock_khz) / 2.0, 3)

        mode_info = BUS_PROTOCOLS["SPI"]["modes"].get(mode_key, BUS_PROTOCOLS["SPI"]["modes"]["MODE_0"])
        cpol = mode_info["cpol"]
        cpha = mode_info["cpha"]

        waveform_samples: List[Dict[str, Any]] = []
        cur_time_us = 0.0
        sample_idx = 0

        # Initial Idle State (CS HIGH, SCLK at CPOL)
        waveform_samples.append({
            "sample_index": sample_idx,
            "time_us": cur_time_us,
            "line1_name": "CS", "line1_val": 1,
            "line2_name": "SCLK", "line2_val": cpol,
            "line3_name": "MOSI", "line3_val": 0,
            "line4_name": "MISO", "line4_val": 0,
            "packet_annotation": "IDLE"
        })
        sample_idx += 1
        cur_time_us += t_half_clk_us

        # Assert CS LOW (Lead time)
        waveform_samples.append({
            "sample_index": sample_idx,
            "time_us": cur_time_us,
            "line1_name": "CS", "line1_val": 0,
            "line2_name": "SCLK", "line2_val": cpol,
            "line3_name": "MOSI", "line3_val": 0,
            "line4_name": "MISO", "line4_val": 0,
            "packet_annotation": "CS_ASSERT"
        })
        sample_idx += 1
        cur_time_us += t_half_clk_us

        # Clock out each byte
        packet_frames = []
        for byte_idx, (t_b, r_b) in enumerate(zip(tx_bytes, rx_bytes)):
            byte_hex = f"0x{t_b:02X}"
            rx_hex = f"0x{r_b:02X}"
            packet_frames.append({"byte_index": byte_idx, "mosi_hex": byte_hex, "miso_hex": rx_hex})

            for bit_pos in range(7, -1, -1):
                mosi_bit = (t_b >> bit_pos) & 0x01
                miso_bit = (r_b >> bit_pos) & 0x01

                # First half cycle
                clk_val_1 = 1 - cpol if cpha == 0 else cpol
                waveform_samples.append({
                    "sample_index": sample_idx,
                    "time_us": round(cur_time_us, 3),
                    "line1_name": "CS", "line1_val": 0,
                    "line2_name": "SCLK", "line2_val": clk_val_1,
                    "line3_name": "MOSI", "line3_val": mosi_bit,
                    "line4_name": "MISO", "line4_val": miso_bit,
                    "packet_annotation": f"B{byte_idx}[{bit_pos}]:M{mosi_bit}/S{miso_bit}"
                })
                sample_idx += 1
                cur_time_us += t_half_clk_us

                # Second half cycle
                clk_val_2 = cpol if cpha == 0 else 1 - cpol
                waveform_samples.append({
                    "sample_index": sample_idx,
                    "time_us": round(cur_time_us, 3),
                    "line1_name": "CS", "line1_val": 0,
                    "line2_name": "SCLK", "line2_val": clk_val_2,
                    "line3_name": "MOSI", "line3_val": mosi_bit,
                    "line4_name": "MISO", "line4_val": miso_bit,
                    "packet_annotation": f"B{byte_idx}[{bit_pos}]:M{mosi_bit}/S{miso_bit}"
                })
                sample_idx += 1
                cur_time_us += t_half_clk_us

        # Deassert CS HIGH (Trail time)
        waveform_samples.append({
            "sample_index": sample_idx,
            "time_us": round(cur_time_us, 3),
            "line1_name": "CS", "line1_val": 1,
            "line2_name": "SCLK", "line2_val": cpol,
            "line3_name": "MOSI", "line3_val": 0,
            "line4_name": "MISO", "line4_val": 0,
            "packet_annotation": "CS_DEASSERT"
        })

        total_duration_us = round(cur_time_us, 3)
        tx_id = f"BUS_SPI_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(2).hex()}"
        now_str = datetime.now().isoformat()

        # Log to SQLite WAL
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO peripheral_bus_transactions (
                    id, protocol, device_name, operation_type,
                    address_hex, register_hex, payload_hex,
                    data_length, duration_us, baud_or_clock_khz,
                    status, student_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                tx_id, "SPI", device_name, f"FULL_DUPLEX_{mode_key}",
                "N/A", f"0x{tx_bytes[0]:02X}", " ".join(f"{b:02X}" for b in tx_bytes),
                len(tx_bytes), total_duration_us, clock_khz,
                "SUCCESS", student_id, now_str
            ))
            conn.commit()

        return {
            "status": "SUCCESS",
            "transaction_id": tx_id,
            "protocol": "SPI",
            "mode": mode_key,
            "device_name": device_name,
            "clock_khz": clock_khz,
            "cpol": cpol,
            "cpha": cpha,
            "tx_hex": [f"0x{b:02X}" for b in tx_bytes],
            "rx_hex": [f"0x{b:02X}" for b in rx_bytes],
            "packet_frames": packet_frames,
            "total_duration_us": total_duration_us,
            "samples_count": len(waveform_samples),
            "waveform_samples": waveform_samples[:64],  # Return up to 64 points for immediate client preview
            "created_at": now_str
        }

    def simulate_i2c_transaction(
        self,
        slave_addr_7bit: str = "0x68",
        reg_addr_hex: str = "0x75",
        is_read: bool = True,
        data_byte_hex: str = "0x68",
        speed_mode: str = "STANDARD",
        device_name: str = "InvenSense MPU-6050",
        student_id: str = "2023MITEC042"
    ) -> Dict[str, Any]:
        """
        Simulates an I2C transaction with START, 7-bit Address + R/W, ACK, Register Address,
        Repeated START (if read), Read Data, NACK, and STOP condition.
        """
        speed_info = BUS_PROTOCOLS["I2C"]["speeds"].get(speed_mode, BUS_PROTOCOLS["I2C"]["speeds"]["STANDARD"])
        clock_khz = speed_info["freq_khz"]
        t_clk_us = speed_info["t_clk_us"]
        t_qtr_clk_us = round(t_clk_us / 4.0, 3)

        addr_int = int(slave_addr_7bit, 16) & 0x7F
        reg_int = int(reg_addr_hex, 16) & 0xFF
        data_int = int(data_byte_hex, 16) & 0xFF

        waveform_samples: List[Dict[str, Any]] = []
        cur_time_us = 0.0
        sample_idx = 0

        # Helper to push sample
        def push_sample(scl: int, sda: int, annot: str):
            nonlocal cur_time_us, sample_idx
            waveform_samples.append({
                "sample_index": sample_idx,
                "time_us": round(cur_time_us, 3),
                "line1_name": "SCL", "line1_val": scl,
                "line2_name": "SDA", "line2_val": sda,
                "line3_name": "UNUSED", "line3_val": 0,
                "line4_name": "UNUSED", "line4_val": 0,
                "packet_annotation": annot
            })
            sample_idx += 1
            cur_time_us += t_qtr_clk_us

        # 1. Idle Bus (SCL HIGH, SDA HIGH)
        push_sample(1, 1, "IDLE")
        push_sample(1, 1, "IDLE")

        # 2. START Condition: SDA drops while SCL is HIGH
        push_sample(1, 0, "START_COND")
        push_sample(0, 0, "START_HOLD")

        # 3. Transmit Slave Address (Write: R/W = 0)
        addr_byte = (addr_int << 1) | 0  # Write
        packet_steps = [{"stage": "START", "desc": "Start condition initiated"}]
        packet_steps.append({"stage": "SLAVE_ADDR_W", "hex": f"0x{addr_byte:02X}", "desc": f"Slave Addr {slave_addr_7bit} + W(0)"})

        for bit in range(7, -1, -1):
            val = (addr_byte >> bit) & 1
            push_sample(0, val, f"ADDR[{bit}]={val}")
            push_sample(1, val, f"ADDR[{bit}]={val}")
            push_sample(1, val, f"ADDR[{bit}]={val}")
            push_sample(0, val, f"ADDR[{bit}]={val}")

        # Slave ACK (SDA pulled LOW by slave on 9th clock pulse)
        push_sample(0, 0, "ACK_PULL_LOW")
        push_sample(1, 0, "ACK_SAMPLED")
        push_sample(1, 0, "ACK_SAMPLED")
        push_sample(0, 0, "ACK_RELEASE")
        packet_steps.append({"stage": "ACK_1", "desc": "Slave ACK asserted (0)"})

        # 4. Transmit Register Pointer
        packet_steps.append({"stage": "REG_PTR", "hex": f"0x{reg_int:02X}", "desc": f"Register Pointer 0x{reg_int:02X}"})
        for bit in range(7, -1, -1):
            val = (reg_int >> bit) & 1
            push_sample(0, val, f"REG[{bit}]={val}")
            push_sample(1, val, f"REG[{bit}]={val}")
            push_sample(1, val, f"REG[{bit}]={val}")
            push_sample(0, val, f"REG[{bit}]={val}")

        # Slave ACK for Register
        push_sample(0, 0, "ACK_REG_LOW")
        push_sample(1, 0, "ACK_REG_SAMPLED")
        push_sample(1, 0, "ACK_REG_SAMPLED")
        push_sample(0, 0, "ACK_REG_RELEASE")
        packet_steps.append({"stage": "ACK_2", "desc": "Slave ACK asserted (0)"})

        # If read transaction, perform Repeated START + Read Byte
        if is_read:
            # Repeated Start
            push_sample(0, 1, "PREP_RESTART")
            push_sample(1, 1, "SCL_HIGH_RESTART")
            push_sample(1, 0, "RESTART_COND")
            push_sample(0, 0, "RESTART_HOLD")
            packet_steps.append({"stage": "RESTART", "desc": "Repeated Start condition"})

            # Address with R/W = 1
            addr_read_byte = (addr_int << 1) | 1
            packet_steps.append({"stage": "SLAVE_ADDR_R", "hex": f"0x{addr_read_byte:02X}", "desc": f"Slave Addr {slave_addr_7bit} + R(1)"})
            for bit in range(7, -1, -1):
                val = (addr_read_byte >> bit) & 1
                push_sample(0, val, f"RADDR[{bit}]={val}")
                push_sample(1, val, f"RADDR[{bit}]={val}")
                push_sample(1, val, f"RADDR[{bit}]={val}")
                push_sample(0, val, f"RADDR[{bit}]={val}")

            # Slave ACK
            push_sample(0, 0, "ACK_R_LOW")
            push_sample(1, 0, "ACK_R_SAMPLED")
            push_sample(1, 0, "ACK_R_SAMPLED")
            push_sample(0, 0, "ACK_R_RELEASE")
            packet_steps.append({"stage": "ACK_3", "desc": "Slave ACK asserted (0)"})

            # Read Data from slave
            packet_steps.append({"stage": "DATA_READ", "hex": f"0x{data_int:02X}", "desc": f"Data Byte 0x{data_int:02X}"})
            for bit in range(7, -1, -1):
                val = (data_int >> bit) & 1
                push_sample(0, val, f"DATA[{bit}]={val}")
                push_sample(1, val, f"DATA[{bit}]={val}")
                push_sample(1, val, f"DATA[{bit}]={val}")
                push_sample(0, val, f"DATA[{bit}]={val}")

            # Master NACK (SDA left HIGH to indicate end of read)
            push_sample(0, 1, "MASTER_NACK")
            push_sample(1, 1, "NACK_SAMPLED")
            push_sample(1, 1, "NACK_SAMPLED")
            push_sample(0, 1, "NACK_RELEASE")
            packet_steps.append({"stage": "NACK", "desc": "Master NACK asserted (1)"})

        # STOP Condition: SDA rises while SCL is HIGH
        push_sample(0, 0, "PREP_STOP")
        push_sample(1, 0, "SCL_HIGH_STOP")
        push_sample(1, 1, "STOP_COND")
        push_sample(1, 1, "IDLE_POST_STOP")
        packet_steps.append({"stage": "STOP", "desc": "Stop condition terminated"})

        total_duration_us = round(cur_time_us, 3)
        tx_id = f"BUS_I2C_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(2).hex()}"
        now_str = datetime.now().isoformat()

        # Log to SQLite WAL
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO peripheral_bus_transactions (
                    id, protocol, device_name, operation_type,
                    address_hex, register_hex, payload_hex,
                    data_length, duration_us, baud_or_clock_khz,
                    status, student_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                tx_id, "I2C", device_name, "READ" if is_read else "WRITE",
                slave_addr_7bit, reg_addr_hex, data_byte_hex,
                1, total_duration_us, clock_khz,
                "SUCCESS", student_id, now_str
            ))
            conn.commit()

        return {
            "status": "SUCCESS",
            "transaction_id": tx_id,
            "protocol": "I2C",
            "speed_mode": speed_mode,
            "clock_khz": clock_khz,
            "device_name": device_name,
            "slave_address": slave_addr_7bit,
            "register_address": reg_addr_hex,
            "is_read": is_read,
            "data_byte": data_byte_hex,
            "packet_steps": packet_steps,
            "total_duration_us": total_duration_us,
            "samples_count": len(waveform_samples),
            "waveform_samples": waveform_samples[:64],
            "created_at": now_str
        }

    def simulate_uart_transaction(
        self,
        baud_rate: int = 115200,
        tx_payload: str = "OK",
        parity: str = "NONE",
        stop_bits: int = 1,
        device_name: str = "ESP32 Wi-Fi Node",
        student_id: str = "2023MITEC042"
    ) -> Dict[str, Any]:
        """
        Simulates an asynchronous UART frame with Start Bit (0), 8 Data Bits (LSB first),
        Parity bit, and Stop bit (1) at the designated baud rate.
        """
        baud_rate = max(1200, min(baud_rate, 921600))
        t_bit_us = round(1000000.0 / baud_rate, 3)
        t_qtr_bit_us = round(t_bit_us / 4.0, 3)

        waveform_samples: List[Dict[str, Any]] = []
        cur_time_us = 0.0
        sample_idx = 0

        # Helper to push sample
        def push_sample(tx: int, rx: int, annot: str):
            nonlocal cur_time_us, sample_idx
            waveform_samples.append({
                "sample_index": sample_idx,
                "time_us": round(cur_time_us, 3),
                "line1_name": "TX", "line1_val": tx,
                "line2_name": "RX", "line2_val": rx,
                "line3_name": "UNUSED", "line3_val": 0,
                "line4_name": "UNUSED", "line4_val": 0,
                "packet_annotation": annot
            })
            sample_idx += 1
            cur_time_us += t_qtr_bit_us

        # Initial Idle State (TX HIGH, RX HIGH)
        for _ in range(4):
            push_sample(1, 1, "IDLE (HIGH)")

        packet_frames = []
        bytes_data = [ord(ch) for ch in tx_payload] if tx_payload else [0x41]

        for char_idx, char_code in enumerate(bytes_data):
            char_hex = f"0x{char_code:02X}"
            char_ascii = chr(char_code) if 32 <= char_code <= 126 else f"\\x{char_code:02X}"

            # Calculate parity
            ones_count = bin(char_code).count("1")
            parity_bit = 0
            if parity == "EVEN":
                parity_bit = 1 if (ones_count % 2 != 0) else 0
            elif parity == "ODD":
                parity_bit = 0 if (ones_count % 2 != 0) else 1

            packet_frames.append({
                "char_index": char_idx,
                "ascii": char_ascii,
                "hex": char_hex,
                "parity_bit": parity_bit if parity != "NONE" else None
            })

            # 1. Start Bit (Active LOW for 1 bit period)
            for _ in range(4):
                push_sample(0, 1, f"START_BIT (C{char_idx})")

            # 2. 8 Data bits (LSB First: Bit 0 to Bit 7)
            for bit_idx in range(8):
                bit_val = (char_code >> bit_idx) & 1
                for _ in range(4):
                    push_sample(bit_val, 1, f"C{char_idx}_D{bit_idx}={bit_val}")

            # 3. Optional Parity Bit
            if parity != "NONE":
                for _ in range(4):
                    push_sample(parity_bit, 1, f"PARITY={parity_bit}")

            # 4. Stop Bits (Active HIGH for 1 or 2 bit periods)
            for sb in range(stop_bits):
                for _ in range(4):
                    push_sample(1, 1, f"STOP_BIT_{sb + 1}")

        total_duration_us = round(cur_time_us, 3)
        tx_id = f"BUS_UART_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(2).hex()}"
        now_str = datetime.now().isoformat()

        # Log to SQLite WAL
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO peripheral_bus_transactions (
                    id, protocol, device_name, operation_type,
                    address_hex, register_hex, payload_hex,
                    data_length, duration_us, baud_or_clock_khz,
                    status, student_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                tx_id, "UART", device_name, f"ASYNC_{baud_rate}_{parity}",
                "N/A", "N/A", " ".join(f"{b:02X}" for b in bytes_data),
                len(bytes_data), total_duration_us, float(baud_rate),
                "SUCCESS", student_id, now_str
            ))
            conn.commit()

        return {
            "status": "SUCCESS",
            "transaction_id": tx_id,
            "protocol": "UART",
            "baud_rate": baud_rate,
            "bit_period_us": t_bit_us,
            "parity": parity,
            "stop_bits": stop_bits,
            "device_name": device_name,
            "payload_text": tx_payload,
            "packet_frames": packet_frames,
            "total_duration_us": total_duration_us,
            "samples_count": len(waveform_samples),
            "waveform_samples": waveform_samples[:64],
            "created_at": now_str
        }

    def get_transaction_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns recent bus transactions from SQLite WAL."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM peripheral_bus_transactions
                ORDER BY created_at DESC
                LIMIT ?;
            """, (limit,)).fetchall()
            return [dict(r) for r in rows]

    def export_transaction_csv(self, protocol: str = "SPI") -> str:
        """Exports simulated protocol transaction traces formatted as RFC-4180 CSV."""
        if protocol.upper() == "I2C":
            res = self.simulate_i2c_transaction()
        elif protocol.upper() == "UART":
            res = self.simulate_uart_transaction()
        else:
            res = self.simulate_spi_transaction()

        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        writer.writerow([
            "Sample_Index", "Time_us", "Line1_Name", "Line1_Val",
            "Line2_Name", "Line2_Val", "Line3_Name", "Line3_Val",
            "Line4_Name", "Line4_Val", "Packet_Annotation"
        ])

        for s in res["waveform_samples"]:
            writer.writerow([
                s["sample_index"],
                s["time_us"],
                s["line1_name"],
                s["line1_val"],
                s["line2_name"],
                s["line2_val"],
                s["line3_name"],
                s["line3_val"],
                s["line4_name"],
                s["line4_val"],
                s["packet_annotation"]
            ])

        return output.getvalue()


# Singleton Instance
peripheral_bus_engine = PeripheralBusEngine()

