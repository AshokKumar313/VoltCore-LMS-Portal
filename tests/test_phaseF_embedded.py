"""
========================================================================================
VoltCore Apex Academia - Unit Tests for Phase F: Embedded Systems (Features 261–270)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
========================================================================================
"""

import os
import pytest
import tempfile
from backend.embedded_systems_engine import EmbeddedSystemsEngine, MICROCONTROLLER_CATALOG, BARE_METAL_CODE_LIBRARY


@pytest.fixture
def engine():
    """Provides a fresh isolated instance of EmbeddedSystemsEngine with a temporary SQLite DB."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_embedded_telemetry.db")
    eng = EmbeddedSystemsEngine(db_path=db_path)
    yield eng


# =========================================================================
# Feature 261: Microcontroller Pinout & Specs
# =========================================================================
def test_microcontroller_specs(engine):
    stm32 = engine.get_microcontroller_specs("STM32F401CCU6")
    assert stm32["architecture"] == "ARM Cortex-M4F (32-bit)"
    assert stm32["clock_freq_mhz"] == 84
    assert stm32["five_volt_tolerant"] is True

    esp32 = engine.get_microcontroller_specs("ESP32_WROOM")
    assert esp32["architecture"] == "Xtensa Dual-Core 32-bit LX6"
    assert esp32["clock_freq_mhz"] == 240

    all_mcus = engine.list_microcontrollers()
    assert len(all_mcus) >= 4

    with pytest.raises(ValueError):
        engine.get_microcontroller_specs("NON_EXISTENT_CHIP")


# =========================================================================
# Feature 262: GPIO Register Calculation
# =========================================================================
def test_gpio_register_calculation(engine):
    # PC13 as Output Push-Pull, Low speed
    res = engine.calculate_gpio_registers(pin=13, mode="OUTPUT", otype="PUSH_PULL", speed="LOW", pupd="NO_PULL")
    assert res["pin"] == 13
    assert res["mode"] == "OUTPUT"
    # MODER13 = 01b -> shift 26 bits: 1 << 26 = 0x04000000
    assert res["moder_mask_hex"] == "0x04000000"
    assert res["otyper_mask_hex"] == "0x0000"
    assert "GPIOC" in res["c_snippet"] or "GPIOx" in res["c_snippet"]

    # PA9 as AF (AF7 for USART1 TX)
    af_res = engine.calculate_gpio_registers(pin=9, mode="AF", af_num=7)
    assert af_res["afr_index"] == 1  # Pins 8-15 use AFR[1]
    # AFR[1] pin 9 shift = (9-8)*4 = 4 bits -> 7 << 4 = 0x00000070
    assert af_res["afr_mask_hex"] == "0x00000070"

    with pytest.raises(ValueError):
        engine.calculate_gpio_registers(pin=16)  # Only 0..15 supported


# =========================================================================
# Feature 263: UART Baud Rate Generator
# =========================================================================
def test_uart_baud_rate_generator(engine):
    # 84 MHz clock, 115200 Baud, 16x oversampling (over8 = 0)
    # Expected: 84,000,000 / (16 * 115200) = 45.5729
    # Mantissa = 45 (0x2D), Fraction = round(0.5729 * 16) = 9 (0x09) -> BRR = 0x02D9
    res = engine.calculate_uart_baud(f_pclk_hz=84000000.0, desired_baud=115200, over8=0)
    assert res["mantissa"] == 45
    assert res["fraction"] == 9
    assert res["brr_hex"] == "0x02D9"
    assert res["is_tolerable"] is True
    assert res["error_percent"] < 1.0
    assert res["bit_duration_us"] == pytest.approx(8.68, abs=0.1)

    with pytest.raises(ValueError):
        engine.calculate_uart_baud(f_pclk_hz=0, desired_baud=115200)


# =========================================================================
# Feature 264: SPI Communication Modes
# =========================================================================
def test_spi_parameters(engine):
    # Mode 0 (CPOL=0, CPHA=0), 84 MHz PCLK, Prescaler 4 -> 21 MHz SCK
    spi0 = engine.calculate_spi_parameters(f_pclk_hz=84000000.0, prescaler=4, cpol=0, cpha=0)
    assert spi0["spi_mode"] == 0
    assert spi0["sck_freq_hz"] == 21000000.0
    assert "Mode 0" in spi0["mode_description"]

    # Mode 3 (CPOL=1, CPHA=1), 84 MHz PCLK, Prescaler 16 -> 5.25 MHz SCK
    spi3 = engine.calculate_spi_parameters(f_pclk_hz=84000000.0, prescaler=16, cpol=1, cpha=1)
    assert spi3["spi_mode"] == 3
    assert spi3["sck_freq_hz"] == 5250000.0

    with pytest.raises(ValueError):
        engine.calculate_spi_parameters(f_pclk_hz=84000000.0, prescaler=5)  # Invalid prescaler


# =========================================================================
# Feature 265: I2C Address & Pull-Up Resistor
# =========================================================================
def test_i2c_bus_parameters(engine):
    # MPU-6050 address 0x68
    # Write byte = (0x68 << 1) | 0 = 0xD0
    # Read byte = (0x68 << 1) | 1 = 0xD1
    res = engine.calculate_i2c_bus_parameters(slave_address_7bit=0x68, bus_speed_mode="STANDARD", vdd_v=3.3, bus_capacitance_pf=150.0)
    assert res["slave_address_7bit_hex"] == "0x68"
    assert res["write_byte_hex"] == "0xD0"
    assert res["read_byte_hex"] == "0xD1"
    assert res["is_valid_pullup_window"] is True
    assert res["rp_min_ohms"] < res["rp_max_ohms"]
    assert 900.0 < res["rp_min_ohms"] < 1000.0  # (3.3 - 0.4) / 3mA = 966.7 ohms

    with pytest.raises(ValueError):
        engine.calculate_i2c_bus_parameters(slave_address_7bit=0xFF)  # Must be 7-bit (<= 127)


# =========================================================================
# Feature 266: Interrupt Handling & NVIC Preemption
# =========================================================================
def test_nvic_preemption_simulation(engine):
    # PRIGROUP = 3: 4 preemption levels (bits [7:7]), 8 subpriorities
    irq_high_urgency = {"name": "EXTI0", "preempt": 0, "sub": 1}
    irq_low_urgency = {"name": "USART1", "preempt": 2, "sub": 0}

    sim = engine.simulate_nvic_priority(prigroup=3, irq_a=irq_high_urgency, irq_b=irq_low_urgency)
    assert sim["preempt_occurred"] is True
    assert "EXTI0 preempts USART1" in sim["execution_outcome"]
    assert sim["latency_metrics"]["tail_chaining_cycles"] == 6

    # Equal preemption, subpriority arbitration
    irq_c = {"name": "TIM2", "preempt": 1, "sub": 0}
    irq_d = {"name": "TIM3", "preempt": 1, "sub": 2}
    sim_sub = engine.simulate_nvic_priority(prigroup=3, irq_a=irq_c, irq_b=irq_d)
    assert sim_sub["preempt_occurred"] is False
    assert "TIM2 runs first" in sim_sub["execution_outcome"]


# =========================================================================
# Feature 267: Timer PSC / ARR Auto-Solver
# =========================================================================
def test_timer_auto_solver(engine):
    # 84 MHz clock, target 1000 Hz (1 kHz)
    # Expected: (PSC + 1) * (ARR + 1) = 84,000
    res = engine.solve_timer_configuration(f_tim_hz=84000000.0, target_freq_hz=1000.0)
    assert res["error_percent"] == pytest.approx(0.0, abs=1e-3)
    assert res["actual_freq_hz"] == pytest.approx(1000.0, abs=0.1)
    assert res["period_ms"] == pytest.approx(1.0, abs=0.01)

    # 16 MHz AVR clock, target 1 Hz
    avr_res = engine.solve_timer_configuration(f_tim_hz=16000000.0, target_freq_hz=1.0)
    assert avr_res["actual_freq_hz"] == pytest.approx(1.0, abs=0.01)

    with pytest.raises(ValueError):
        engine.solve_timer_configuration(f_tim_hz=-100, target_freq_hz=1000)


# =========================================================================
# Feature 268: PWM Duty Cycle & Average Voltage
# =========================================================================
def test_pwm_duty_cycle(engine):
    # ARR = 999, CCR = 500 -> 50% duty cycle
    res = engine.calculate_pwm_parameters(arr=999, ccr=500, vdd_v=3.3, f_tim_hz=84000000.0, psc=83)
    assert res["duty_cycle_percent"] == 50.0
    assert res["v_avg_volts"] == pytest.approx(1.65, abs=0.02)
    assert res["frequency_hz"] == pytest.approx(1000.0, abs=1.0)

    # Center-aligned mode check
    res_center = engine.calculate_pwm_parameters(arr=1000, ccr=250, mode="CENTER_ALIGNED")
    assert res_center["mode"] == "Center-Aligned"

    with pytest.raises(ValueError):
        engine.calculate_pwm_parameters(arr=-1, ccr=10)


# =========================================================================
# Feature 269: Bit-Band Alias Address Calculator
# =========================================================================
def test_bitband_alias_address(engine):
    # SRAM Address 0x20000000, Bit 0
    # Expected Alias: 0x22000000 + (0 * 32) + (0 * 4) = 0x22000000
    sram_alias = engine.calculate_bitband_alias(byte_address=0x20000000, bit_index=0)
    assert sram_alias["alias_address_hex"] == "0x22000000"

    # SRAM Address 0x20000004, Bit 2
    # Alias = 0x22000000 + (4 * 32) + (2 * 4) = 0x22000000 + 128 + 8 = 0x22000088
    sram_alias2 = engine.calculate_bitband_alias(byte_address=0x20000004, bit_index=2)
    assert sram_alias2["alias_address_hex"] == "0x22000088"

    # Peripheral Address 0x40020014 (GPIOA ODR in STM32F4), Bit 5
    # Byte offset = 0x00020014 = 131092
    # Alias = 0x42000000 + (131092 * 32) + (5 * 4) = 0x42000000 + 4194944 + 20 = 0x42400294
    periph_alias = engine.calculate_bitband_alias(byte_address=0x40020014, bit_index=5)
    assert periph_alias["region"] == "Peripherals (1MB Bit-Band Region)"
    assert periph_alias["alias_address_hex"] == "0x42400294"

    with pytest.raises(ValueError):
        engine.calculate_bitband_alias(byte_address=0x08000000, bit_index=0)  # Flash has no bit-band


# =========================================================================
# Feature 270: Bare-Metal Code Snippets
# =========================================================================
def test_bare_metal_snippets(engine):
    snippet = engine.get_code_snippet("GPIO_TOGGLE")
    assert "GPIOC" in snippet["code"]
    assert "தமிழ்" in snippet["tamil_desc"] or "ரிஜிஸ்டர்" in snippet["tamil_desc"]

    all_snippets = engine.list_code_snippets()
    assert len(all_snippets) >= 5

    with pytest.raises(ValueError):
        engine.get_code_snippet("INVALID_SNIPPET_NAME")


# =========================================================================
# Persistence: SQLite WAL Integration
# =========================================================================
def test_embedded_simulations_persistence(engine):
    sim_id = engine.save_simulation(
        student_id="2023MITEC042",
        feature_id=263,
        feature_name="UART_BAUD_CALCULATION",
        input_payload={"clock_hz": 84000000, "baud": 115200},
        computed_metrics={"brr": "0x02D9", "error": 0.16}
    )
    assert sim_id > 0

    history = engine.get_simulations("2023MITEC042")
    assert len(history) >= 1
    assert any(h["feature_name"] == "UART_BAUD_CALCULATION" for h in history)


def test_timer_configuration_persistence(engine):
    cfg_id = engine.save_timer_config(
        student_id="2023MITEC042",
        mcu_family="STM32F401",
        tim_clock_hz=84000000.0,
        target_freq_hz=50.0,
        prescaler=83,
        auto_reload=19999,
        actual_freq_hz=50.0,
        error_percent=0.0
    )
    assert cfg_id > 0

    configs = engine.get_timer_configs("2023MITEC042")
    assert len(configs) >= 1
    assert any(c["target_freq_hz"] == 50.0 for c in configs)
