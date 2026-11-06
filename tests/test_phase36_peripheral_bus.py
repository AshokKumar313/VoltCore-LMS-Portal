"""
========================================================================================
VoltCore Apex Academia - Phase 36 Test Suite
Module: Peripheral Bus Protocols Analyzer Tests (SPI, I2C, UART)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
========================================================================================
"""

import os
import sqlite3
import pytest
from backend.peripheral_bus_engine import (
    PeripheralBusEngine,
    BUS_PROTOCOLS,
    peripheral_bus_engine
)


def test_engine_initialization_and_wal(tmp_path):
    """Verifies SQLite tables and WAL mode are initialized correctly."""
    db_file = str(tmp_path / "test_bus_init.db")
    engine = PeripheralBusEngine(db_path=db_file)
    conn = engine._get_connection()
    cursor = conn.cursor()

    # Verify journal mode is WAL
    journal_mode = cursor.execute("PRAGMA journal_mode;").fetchone()[0]
    assert journal_mode.upper() == "WAL"

    # Verify tables exist
    tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    assert "peripheral_bus_transactions" in tables
    assert "peripheral_bus_waveforms" in tables
    conn.close()


def test_get_protocol_presets(tmp_path):
    """Verifies protocol catalogs for SPI, I2C, and UART."""
    db_file = str(tmp_path / "test_bus_presets.db")
    engine = PeripheralBusEngine(db_path=db_file)
    presets = engine.get_protocol_presets()

    assert "SPI" in presets
    assert "I2C" in presets
    assert "UART" in presets

    # Verify SPI modes
    spi_modes = presets["SPI"]["modes"]
    assert "MODE_0" in spi_modes
    assert "MODE_1" in spi_modes
    assert "MODE_2" in spi_modes
    assert "MODE_3" in spi_modes
    assert spi_modes["MODE_0"]["cpol"] == 0
    assert spi_modes["MODE_0"]["cpha"] == 0
    assert spi_modes["MODE_3"]["cpol"] == 1
    assert spi_modes["MODE_3"]["cpha"] == 1

    # Verify I2C devices
    i2c_devs = [d["key"] for d in presets["I2C"]["devices"]]
    assert "I2C_MPU6050" in i2c_devs
    assert "I2C_BMP280" in i2c_devs

    # Verify UART baud rates
    assert 9600 in presets["UART"]["baud_rates"]
    assert 115200 in presets["UART"]["baud_rates"]


def test_simulate_spi_transaction(tmp_path):
    """Verifies SPI transaction simulation, CS assertion, MOSI/MISO bits, and timing."""
    db_file = str(tmp_path / "test_bus_spi.db")
    engine = PeripheralBusEngine(db_path=db_file)
    res = engine.simulate_spi_transaction(
        mode_key="MODE_0",
        clock_khz=1000.0,
        tx_bytes=[0x9F, 0x00],
        rx_bytes=[0x00, 0xEF],
        device_name="Winbond W25Q64 Flash",
        student_id="2023MITEC042"
    )

    assert res["status"] == "SUCCESS"
    assert res["protocol"] == "SPI"
    assert res["mode"] == "MODE_0"
    assert res["cpol"] == 0
    assert res["cpha"] == 0
    assert res["total_duration_us"] > 0
    assert len(res["waveform_samples"]) > 10

    # First sample is IDLE (CS=1)
    assert res["waveform_samples"][0]["line1_val"] == 1  # CS
    # Second sample is CS_ASSERT (CS=0)
    assert res["waveform_samples"][1]["line1_val"] == 0  # CS


def test_simulate_i2c_transaction(tmp_path):
    """Verifies I2C read transaction, START condition, ACK, Repeated START, read byte, and STOP."""
    db_file = str(tmp_path / "test_bus_i2c.db")
    engine = PeripheralBusEngine(db_path=db_file)
    res = engine.simulate_i2c_transaction(
        slave_addr_7bit="0x68",
        reg_addr_hex="0x75",
        is_read=True,
        data_byte_hex="0x68",
        speed_mode="STANDARD",
        device_name="InvenSense MPU-6050",
        student_id="2023MITEC042"
    )

    assert res["status"] == "SUCCESS"
    assert res["protocol"] == "I2C"
    assert res["slave_address"] == "0x68"
    assert res["is_read"] is True
    assert len(res["packet_steps"]) >= 6

    stages = [step["stage"] for step in res["packet_steps"]]
    assert "START" in stages
    assert "SLAVE_ADDR_W" in stages
    assert "ACK_1" in stages
    assert "REG_PTR" in stages
    assert "RESTART" in stages
    assert "DATA_READ" in stages
    assert "STOP" in stages


def test_simulate_uart_transaction(tmp_path):
    """Verifies UART asynchronous framing, Start bit, 8 data bits, parity, and Stop bit."""
    db_file = str(tmp_path / "test_bus_uart.db")
    engine = PeripheralBusEngine(db_path=db_file)
    res = engine.simulate_uart_transaction(
        baud_rate=115200,
        tx_payload="OK",
        parity="EVEN",
        stop_bits=1,
        device_name="ESP32 Wi-Fi Node",
        student_id="2023MITEC042"
    )

    assert res["status"] == "SUCCESS"
    assert res["protocol"] == "UART"
    assert res["baud_rate"] == 115200
    assert res["bit_period_us"] < 10.0  # ~8.68 us at 115200 baud
    assert len(res["packet_frames"]) == 2  # 'O' and 'K'
    assert res["packet_frames"][0]["ascii"] == "O"
    assert res["packet_frames"][1]["ascii"] == "K"
    assert res["packet_frames"][0]["parity_bit"] in (0, 1)


def test_transaction_history_persistence(tmp_path):
    """Verifies persistence of simulated transactions in SQLite WAL."""
    db_file = str(tmp_path / "test_bus_history.db")
    engine = PeripheralBusEngine(db_path=db_file)
    engine.simulate_spi_transaction(device_name="Test SPI Dev")
    engine.simulate_i2c_transaction(device_name="Test I2C Dev")
    engine.simulate_uart_transaction(device_name="Test UART Dev")

    history = engine.get_transaction_history(limit=10)
    assert len(history) == 3
    protocols = [h["protocol"] for h in history]
    assert "SPI" in protocols
    assert "I2C" in protocols
    assert "UART" in protocols


def test_export_transaction_csv(tmp_path):
    """Verifies RFC-4180 CSV export of transaction waveforms."""
    db_file = str(tmp_path / "test_bus_csv.db")
    engine = PeripheralBusEngine(db_path=db_file)
    csv_str = engine.export_transaction_csv(protocol="I2C")

    assert "Sample_Index,Time_us,Line1_Name,Line1_Val" in csv_str
    lines = [line.strip() for line in csv_str.strip().split("\n") if line.strip()]
    assert len(lines) > 10
    assert "SCL" in csv_str
    assert "SDA" in csv_str


def test_privacy_invariants_and_attribution():
    """Strictly verifies zero leakage of private credentials and confirms public author attribution."""
    with open("backend/peripheral_bus_engine.py", "r", encoding="utf-8") as f:
        code_str = f.read()

    # Zero leakage
    assert "9597382878" not in code_str
    assert "ashokkumar2008313@gmail.com" not in code_str

    # Public attribution
    assert "Ashok Kumar A" in code_str
    assert "2023MITEC042" in code_str
    assert "Anna University" in code_str
