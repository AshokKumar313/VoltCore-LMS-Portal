"""
========================================================================================
VoltCore Apex Academia - Phase F: Embedded Systems & Microcontrollers (Features 261–270)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Features:
  - Feature 261: Microcontroller Pinout Explorer (STM32F401, ATmega328P, ESP32, RP2040)
  - Feature 262: GPIO Configuration Learning Tool (MODER, OTYPER, OSPEEDR, PUPDR, AFR)
  - Feature 263: UART Communication Visualizer (BRR Mantissa/Fraction, Frame Timing, Bit Duration)
  - Feature 264: SPI Communication Diagram Explorer (Modes 0-3, CPOL/CPHA, SCK Prescaler, Bitrate)
  - Feature 265: I2C Address and Transaction Explorer (7-bit/8-bit R/W, ACK/NACK, Pull-up Resistor Math)
  - Feature 266: Interrupt Handling Learning Simulator (NVIC Priority Grouping, Preempt/Subpriority, Latency)
  - Feature 267: Timer and Counter Configuration Calculator (PSC, ARR, Overflow Frequency, Auto-Solver)
  - Feature 268: PWM Duty Cycle Visualizer (CCR, ARR, Edge vs Center-Aligned, Average Voltage)
  - Feature 269: Memory Map Explorer (Flash, SRAM, Peripherals, Bit-Band Alias Address Calculator)
  - Feature 270: Embedded C Code Snippet Library (Bare-Metal Templates, Bilingual English/Tamil Notes)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
========================================================================================
"""

import os
import math
import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")

# Microcontroller Profiles (Feature 261)
MICROCONTROLLER_CATALOG: Dict[str, Dict[str, Any]] = {
    "STM32F401CCU6": {
        "name": "STM32F401CCU6 Black Pill",
        "architecture": "ARM Cortex-M4F (32-bit)",
        "fpu": "Hardware Single-Precision FPU (FPv4-SP)",
        "clock_freq_mhz": 84,
        "operating_voltage_v": 3.3,
        "flash_kb": 256,
        "sram_kb": 64,
        "gpio_count": 36,
        "adc_channels": 16,
        "adc_resolution_bits": 12,
        "dac_channels": 0,
        "timers": ["TIM1 (Advanced)", "TIM2 (32-bit)", "TIM3 (16-bit)", "TIM4 (16-bit)", "TIM5 (32-bit)", "TIM9", "TIM10", "TIM11"],
        "interfaces": {"USART": 3, "SPI": 3, "I2C": 3, "USB": "USB 2.0 OTG FS"},
        "package": "UFQFPN48 / Black Pill 40-pin header",
        "five_volt_tolerant": True,
        "max_gpio_current_ma": 25
    },
    "ATMEGA328P": {
        "name": "ATmega328P-PU",
        "architecture": "AVR (8-bit RISC)",
        "fpu": "None (Software Emulated)",
        "clock_freq_mhz": 16,
        "operating_voltage_v": 5.0,
        "flash_kb": 32,
        "sram_kb": 2,
        "gpio_count": 23,
        "adc_channels": 6,
        "adc_resolution_bits": 10,
        "dac_channels": 0,
        "timers": ["Timer0 (8-bit)", "Timer1 (16-bit)", "Timer2 (8-bit)"],
        "interfaces": {"USART": 1, "SPI": 1, "I2C": 1},
        "package": "DIP-28 / TQFP-32",
        "five_volt_tolerant": True,
        "max_gpio_current_ma": 40
    },
    "ESP32_WROOM": {
        "name": "ESP32-WROOM-32",
        "architecture": "Xtensa Dual-Core 32-bit LX6",
        "fpu": "Hardware Single-Precision FPU",
        "clock_freq_mhz": 240,
        "operating_voltage_v": 3.3,
        "flash_kb": 4096,
        "sram_kb": 520,
        "gpio_count": 34,
        "adc_channels": 18,
        "adc_resolution_bits": 12,
        "dac_channels": 2,
        "timers": ["4 x 64-bit General Purpose Timers"],
        "interfaces": {"UART": 3, "SPI": 3, "I2C": 2, "I2S": 2, "CAN": 1, "Wi-Fi": "802.11 b/g/n", "Bluetooth": "v4.2 BR/EDR & BLE"},
        "package": "DevKit 38-pin module",
        "five_volt_tolerant": False,
        "max_gpio_current_ma": 12
    },
    "RP2040": {
        "name": "Raspberry Pi RP2040",
        "architecture": "Dual ARM Cortex-M0+ (32-bit)",
        "fpu": "None (Optimized ROM Software Floating Point)",
        "clock_freq_mhz": 133,
        "operating_voltage_v": 3.3,
        "flash_kb": 2048,
        "sram_kb": 264,
        "gpio_count": 30,
        "adc_channels": 4,
        "adc_resolution_bits": 12,
        "dac_channels": 0,
        "timers": ["64-bit Microsecond Counter + 8 PWM slices"],
        "interfaces": {"UART": 2, "SPI": 2, "I2C": 2, "PIO": "2 x PIO blocks with 4 state machines each"},
        "package": "QFN-56 / Pico 40-pin header",
        "five_volt_tolerant": False,
        "max_gpio_current_ma": 12
    }
}

# Embedded C Bare-Metal Templates (Feature 270)
BARE_METAL_CODE_LIBRARY: Dict[str, Dict[str, Any]] = {
    "GPIO_TOGGLE": {
        "title": "GPIO Pin Toggle (Cortex-M CMSIS Bare-Metal)",
        "mcu": "STM32F401 (GPIOC Pin 13 User LED)",
        "tamil_desc": "GPIOC பின் 13 இல் இணைக்கப்பட்ட LED விளக்கை BSRR ரிஜிஸ்டர் மூலம் ஒளிரச்செய்து அணைக்கும் அடிப்படை நிரல்.",
        "description": "Configures PC13 as Output Push-Pull and toggles it using the atomic Bit Set/Reset Register (BSRR) without modifying neighboring bits.",
        "code": """/* STM32F401CCU6 Bare-Metal GPIO Toggle (PC13 User LED) */
#include "stm32f4xx.h"

void delay_ms(volatile uint32_t ms) {
    while (ms--) {
        for (volatile uint32_t i = 0; i < 8400; i++) {
            __NOP();
        }
    }
}

int main(void) {
    /* 1. Enable AHB1 peripheral clock for GPIOC */
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOCEN;

    /* 2. Configure PC13 as General Purpose Output (MODER13 = 01b) */
    GPIOC->MODER &= ~(3U << (13 * 2));
    GPIOC->MODER |=  (1U << (13 * 2));

    /* 3. Output Type: Push-Pull (OTYPER13 = 0) */
    GPIOC->OTYPER &= ~(1U << 13);

    /* 4. Speed: Low Speed 2MHz (OSPEEDR13 = 00b) */
    GPIOC->OSPEEDR &= ~(3U << (13 * 2));

    /* 5. Pull-up/Pull-down: No Pull (PUPDR13 = 00b) */
    GPIOC->PUPDR &= ~(3U << (13 * 2));

    while (1) {
        /* Turn LED ON (Active Low on Black Pill: Reset bit 13) */
        GPIOC->BSRR = (1U << (13 + 16));
        delay_ms(500);

        /* Turn LED OFF (Set bit 13) */
        GPIOC->BSRR = (1U << 13);
        delay_ms(500);
    }
}"""
    },
    "UART_TX_STRING": {
        "title": "Non-Blocking Polled UART Transmit (USART1)",
        "mcu": "STM32F401 (PA9 TX, PA10 RX @ 115200 Baud)",
        "tamil_desc": "USART1 மூலம் 115200 Baud வேகத்தில் சரங்களை (strings) கணினிக்கு அனுப்பி வைக்கும் நிரல்.",
        "description": "Configures PA9 as USART1 Alternate Function (AF7), sets Baud Rate Register (BRR) for 84MHz APB2 clock, and transmits characters.",
        "code": """/* STM32F401 USART1 115200 Baud Transmit */
#include "stm32f4xx.h"

void uart1_init(void) {
    /* 1. Enable GPIOA and USART1 Clocks */
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_USART1EN;

    /* 2. Configure PA9 as Alternate Function AF7 (USART1_TX) */
    GPIOA->MODER &= ~(3U << (9 * 2));
    GPIOA->MODER |=  (2U << (9 * 2));
    GPIOA->AFR[1] |= (7U << ((9 - 8) * 4));

    /* 3. Set Baud Rate for 84 MHz APB2 Clock (Baud = 115200)
     * USART_DIV = 84000000 / (16 * 115200) = 45.5729
     * Mantissa = 45 = 0x2D, Fraction = round(0.5729 * 16) = 9 = 0x9
     * BRR = 0x02D9 */
    USART1->BRR = 0x02D9;

    /* 4. Enable Transmitter and USART1 */
    USART1->CR1 = USART_CR1_TE | USART_CR1_UE;
}

void uart1_write_char(char c) {
    /* Wait until Transmit Data Register Empty (TXE flag) */
    while (!(USART1->SR & USART_SR_TXE));
    USART1->DR = (uint16_t)c;
}

void uart1_write_string(const char *str) {
    while (*str) {
        uart1_write_char(*str++);
    }
}

int main(void) {
    uart1_init();
    uart1_write_string("VoltCore Apex Academia: Embedded Systems Ready!\\r\\n");
    while (1);
}"""
    },
    "SYSTICK_TIMER_DELAY": {
        "title": "Hardware SysTick Millisecond Delay Generator",
        "mcu": "ARM Cortex-M Core Peripheral",
        "tamil_desc": "Cortex-M கோர் SysTick டைமர் பயன்படுத்தி துல்லியமான மில்லி-செகண்ட் தாமதம் உருவாக்கும் நுட்பம்.",
        "description": "Configures ARM Cortex-M SysTick internal hardware counter for precise non-blocking tick tracking.",
        "code": """/* ARM Cortex-M SysTick Precise Millisecond Delay */
#include "stm32f4xx.h"

static volatile uint32_t s_ticks = 0;

void SysTick_Handler(void) {
    s_ticks++;
}

void systick_init(uint32_t system_clock_hz) {
    /* Reload value for 1ms interrupt: LOAD = (Clock / 1000) - 1 */
    SysTick->LOAD = (system_clock_hz / 1000) - 1;
    SysTick->VAL = 0;
    /* Enable SysTick with Processor Clock and Interrupt */
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk |
                    SysTick_CTRL_TICKINT_Msk   |
                    SysTick_CTRL_ENABLE_Msk;
}

void delay_ms_systick(uint32_t delay) {
    uint32_t start = s_ticks;
    while ((s_ticks - start) < delay) {
        __WFI(); /* Sleep to conserve HP Victus / Core thermal energy */
    }
}"""
    },
    "TIMER_PWM_INIT": {
        "title": "Hardware Timer PWM Output Generation (TIM2_CH1)",
        "mcu": "STM32F401 (PA0 / TIM2_CH1 @ 20 kHz)",
        "tamil_desc": "TIM2 டைமரின் PWM சிக்னல் மூலம் DC மோட்டார் அல்லது LED பிரகாசத்தைக் கட்டுப்படுத்தும் நிரல்.",
        "description": "Sets up TIM2 in PWM Mode 1 (active when counter < CCR1) on PA0 (AF1) for variable duty cycle control.",
        "code": """/* STM32F401 Timer 2 Channel 1 PWM Generation (20 kHz, 84 MHz Timer Clock) */
#include "stm32f4xx.h"

void tim2_pwm_init(void) {
    /* 1. Clock Gating: GPIOA and TIM2 */
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;

    /* 2. Configure PA0 as AF1 (TIM2_CH1) */
    GPIOA->MODER &= ~(3U << (0 * 2));
    GPIOA->MODER |=  (2U << (0 * 2));
    GPIOA->AFR[0] |= (1U << (0 * 4));

    /* 3. Timer Prescaler and Auto-Reload for 20 kHz PWM:
     * Clock = 84 MHz. Target Freq = 20 kHz.
     * Total counts = 84 MHz / 20 kHz = 4200.
     * PSC = 0 (Prescaler = 1), ARR = 4199 */
    TIM2->PSC = 0;
    TIM2->ARR = 4199;

    /* 4. Configure PWM Mode 1 (OC1M = 110b) and Preload Enable */
    TIM2->CCMR1 &= ~TIM_CCMR1_OC1M;
    TIM2->CCMR1 |=  (6U << TIM_CCMR1_OC1M_Pos) | TIM_CCMR1_OC1PE;

    /* 5. Set Initial 50% Duty Cycle: CCR1 = 4200 / 2 = 2100 */
    TIM2->CCR1 = 2100;

    /* 6. Enable Output and Main Timer Counter */
    TIM2->CCER |= TIM_CCER_CC1E;
    TIM2->CR1  |= TIM_CR1_ARPE | TIM_CR1_CEN;
}

void set_pwm_duty(uint32_t duty_percent) {
    if (duty_percent > 100) duty_percent = 100;
    TIM2->CCR1 = (TIM2->ARR + 1) * duty_percent / 100;
}"""
    },
    "ADC_SINGLE_CONVERSION": {
        "title": "ADC1 Single Channel Polled Conversion (PA1 / ADC_IN1)",
        "mcu": "STM32F401 (12-bit Analog Conversion)",
        "tamil_desc": "PA1 பினில் உள்ள அனலாக் சென்சார் மின்னழுத்தத்தை 12-பிட் டிஜிட்டல் மதிப்பாக மாற்றும் நிரல்.",
        "description": "Configures ADC1 for single-conversion mode with 12-bit resolution ($V_{analog} = \frac{\text{RAW} \times 3.3}{4095}$).",
        "code": """/* STM32F401 12-bit ADC1 Conversion on PA1 (Channel 1) */
#include "stm32f4xx.h"

void adc1_init(void) {
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_ADC1EN;

    /* Configure PA1 as Analog Mode (MODER1 = 11b) */
    GPIOA->MODER |= (3U << (1 * 2));

    /* ADC Common Prescaler: APB2 / 4 = 84MHz / 4 = 21MHz (max 36MHz) */
    ADC->CCR &= ~ADC_CCR_ADCPRE;
    ADC->CCR |=  (1U << ADC_CCR_ADCPRE_Pos);

    /* 1 conversion in regular sequence, Channel 1 first */
    ADC1->SQR1 &= ~ADC_SQR1_L;
    ADC1->SQR3 = 1;

    /* Sample Time: 84 cycles for Channel 1 */
    ADC1->SMPR2 |= (4U << (1 * 3));

    /* Enable ADC1 */
    ADC1->CR2 |= ADC_CR2_ADON;
}

uint16_t adc1_read_raw(void) {
    /* Start conversion */
    ADC1->CR2 |= ADC_CR2_SWSTART;
    /* Wait for End of Conversion (EOC) flag */
    while (!(ADC1->SR & ADC_SR_EOC));
    return (uint16_t)ADC1->DR;
}

float adc1_read_voltage(void) {
    uint16_t raw = adc1_read_raw();
    return ((float)raw * 3.3f) / 4095.0f;
}"""
    }
}


class EmbeddedSystemsEngine:
    """
    Backend computational & simulation engine for Phase F (Features 261–270):
    - Microcontroller hardware profiles & pin capability explorer
    - GPIO register calculations (MODER, OTYPER, OSPEEDR, PUPDR, AFR)
    - UART Baud Rate Generator & bit-timing analysis
    - SPI modes (CPOL/CPHA) & throughput calculations
    - I2C address decoding, timing & pull-up resistor sizing
    - NVIC priority grouping, preemption rules & ISR latency
    - Timer PSC/ARR auto-configuration solver
    - PWM frequency, duty cycle & average voltage visualizer
    - Memory map navigation & bit-band alias address calculator
    - Bare-metal embedded C snippet retrieval
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
                # Embedded simulations ledger
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS embedded_simulations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        feature_id INTEGER NOT NULL,
                        feature_name TEXT NOT NULL,
                        input_payload TEXT NOT NULL,
                        computed_metrics TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)

                # Timer configurations ledger
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS timer_configurations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        mcu_family TEXT NOT NULL,
                        tim_clock_hz REAL NOT NULL,
                        target_freq_hz REAL NOT NULL,
                        prescaler INTEGER NOT NULL,
                        auto_reload INTEGER NOT NULL,
                        actual_freq_hz REAL NOT NULL,
                        error_percent REAL NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)

                # Seed demo record if empty
                cur = conn.execute("SELECT id FROM timer_configurations WHERE student_id = ?", ("2023MITEC042",))
                if not cur.fetchone():
                    now = datetime.now(timezone.utc).isoformat()
                    conn.execute("""
                        INSERT INTO timer_configurations (
                            student_id, mcu_family, tim_clock_hz, target_freq_hz,
                            prescaler, auto_reload, actual_freq_hz, error_percent, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, ("2023MITEC042", "STM32F401", 84000000.0, 1000.0, 83, 999, 1000.0, 0.0, now))

                    demo_payload = json.dumps({"pin": 13, "mode": "OUTPUT", "speed": "LOW"})
                    demo_metrics = json.dumps({"moder": "0x04000000", "otyper": "0x00000000"})
                    conn.execute("""
                        INSERT INTO embedded_simulations (
                            student_id, feature_id, feature_name, input_payload, computed_metrics, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, ("2023MITEC042", 262, "GPIO_CONFIGURATION", demo_payload, demo_metrics, now))
                conn.commit()
            finally:
                conn.close()

    # =========================================================================
    # Feature 261: Microcontroller Pinout & Specification Explorer
    # =========================================================================
    def get_microcontroller_specs(self, mcu_id: str) -> Dict[str, Any]:
        """Returns hardware architecture specifications for a supported microcontroller."""
        mcu_key = mcu_id.upper()
        if mcu_key not in MICROCONTROLLER_CATALOG:
            valid_keys = list(MICROCONTROLLER_CATALOG.keys())
            raise ValueError(f"Unknown MCU '{mcu_id}'. Available MCUs: {valid_keys}")
        return MICROCONTROLLER_CATALOG[mcu_key]

    def list_microcontrollers(self) -> List[Dict[str, Any]]:
        """Lists all supported microcontrollers."""
        return [{"mcu_id": k, **v} for k, v in MICROCONTROLLER_CATALOG.items()]

    # =========================================================================
    # Feature 262: GPIO Configuration Learning Tool
    # =========================================================================
    def calculate_gpio_registers(
        self,
        pin: int,
        mode: str = "OUTPUT",
        otype: str = "PUSH_PULL",
        speed: str = "LOW",
        pupd: str = "NO_PULL",
        af_num: int = 0
    ) -> Dict[str, Any]:
        """
        Calculates Cortex-M (STM32 style) GPIO register values and bitwise hex masks.
        pin: 0 to 15
        mode: 'INPUT' (00), 'OUTPUT' (01), 'AF' (10), 'ANALOG' (11)
        otype: 'PUSH_PULL' (0), 'OPEN_DRAIN' (1)
        speed: 'LOW' (00), 'MEDIUM' (01), 'HIGH' (10), 'VERY_HIGH' (11)
        pupd: 'NO_PULL' (00), 'PULL_UP' (01), 'PULL_DOWN' (10)
        af_num: 0 to 15 (Alternate function mapping)
        """
        if not (0 <= pin <= 15):
            raise ValueError("GPIO pin must be between 0 and 15 inclusive.")

        mode_map = {"INPUT": 0, "OUTPUT": 1, "AF": 2, "ANALOG": 3}
        otype_map = {"PUSH_PULL": 0, "OPEN_DRAIN": 1}
        speed_map = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "VERY_HIGH": 3}
        pupd_map = {"NO_PULL": 0, "PULL_UP": 1, "PULL_DOWN": 2}

        mode_val = mode_map.get(mode.upper(), 1)
        otype_val = otype_map.get(otype.upper(), 0)
        speed_val = speed_map.get(speed.upper(), 0)
        pupd_val = pupd_map.get(pupd.upper(), 0)
        af_val = max(0, min(15, int(af_num)))

        moder_mask = mode_val << (pin * 2)
        otyper_mask = otype_val << pin
        ospeedr_mask = speed_val << (pin * 2)
        pupdr_mask = pupd_val << (pin * 2)

        # Alternate Function Register (AFR[0] for pins 0-7, AFR[1] for pins 8-15)
        afr_index = 0 if pin < 8 else 1
        afr_shift = (pin % 8) * 4
        afr_mask = af_val << afr_shift

        c_snippet = (
            f"/* Configure Pin P[X]{pin} */\n"
            f"GPIOx->MODER   &= ~(3U << ({pin} * 2));\n"
            f"GPIOx->MODER   |=  ({mode_val}U << ({pin} * 2));\n"
            f"GPIOx->OTYPER  &= ~(1U << {pin});\n"
            f"GPIOx->OTYPER  |=  ({otype_val}U << {pin});\n"
            f"GPIOx->OSPEEDR &= ~(3U << ({pin} * 2));\n"
            f"GPIOx->OSPEEDR |=  ({speed_val}U << ({pin} * 2));\n"
            f"GPIOx->PUPDR   &= ~(3U << ({pin} * 2));\n"
            f"GPIOx->PUPDR   |=  ({pupd_val}U << ({pin} * 2));"
        )
        if mode.upper() == "AF":
            c_snippet += f"\nGPIOx->AFR[{afr_index}] |= ({af_val}U << {afr_shift});"

        return {
            "pin": pin,
            "mode": mode.upper(),
            "otype": otype.upper(),
            "speed": speed.upper(),
            "pupd": pupd.upper(),
            "af_num": af_val,
            "moder_mask_hex": f"0x{moder_mask:08X}",
            "otyper_mask_hex": f"0x{otyper_mask:04X}",
            "ospeedr_mask_hex": f"0x{ospeedr_mask:08X}",
            "pupdr_mask_hex": f"0x{pupdr_mask:08X}",
            "afr_index": afr_index,
            "afr_mask_hex": f"0x{afr_mask:08X}",
            "c_snippet": c_snippet
        }

    # =========================================================================
    # Feature 263: UART Communication Visualizer & Baud Rate Generator
    # =========================================================================
    def calculate_uart_baud(
        self,
        f_pclk_hz: float,
        desired_baud: int = 115200,
        over8: int = 0
    ) -> Dict[str, Any]:
        """
        Calculates STM32 / Cortex-M USART_BRR register value, mantissa, fraction,
        actual baud rate, percentage error, and bit timing duration.
        Formula: USART_DIV = f_pclk / (8 * (2 - over8) * desired_baud)
        """
        if f_pclk_hz <= 0 or desired_baud <= 0:
            raise ValueError("Clock frequency and Baud rate must be positive.")

        oversampling = 8 if over8 == 1 else 16
        divider = f_pclk_hz / (oversampling * desired_baud)
        mantissa = int(divider)
        fraction_raw = (divider - mantissa) * oversampling
        fraction = round(fraction_raw)

        # Carry-over handling if rounded fraction equals oversampling
        if fraction >= oversampling:
            mantissa += 1
            fraction = 0

        # Calculate actual baud rate achievable
        div_actual = mantissa + (fraction / oversampling)
        if div_actual > 0:
            actual_baud = f_pclk_hz / (oversampling * div_actual)
            error_percent = abs(actual_baud - desired_baud) / desired_baud * 100.0
        else:
            actual_baud = 0.0
            error_percent = 100.0

        # Register BRR formatting
        if over8 == 0:
            brr_reg = (mantissa << 4) | (fraction & 0x0F)
        else:
            brr_reg = (mantissa << 4) | (fraction & 0x07)

        bit_duration_us = (1.0 / desired_baud) * 1e6
        # Standard 8N1 frame = 1 start + 8 data + 0 parity + 1 stop = 10 bits
        frame_time_us = 10.0 * bit_duration_us
        max_bytes_per_sec = desired_baud / 10.0

        return {
            "f_pclk_hz": f_pclk_hz,
            "desired_baud": desired_baud,
            "over8": over8,
            "oversampling_factor": oversampling,
            "mantissa": mantissa,
            "fraction": fraction,
            "brr_hex": f"0x{brr_reg:04X}",
            "actual_baud": round(actual_baud, 2),
            "error_percent": round(error_percent, 4),
            "is_tolerable": error_percent <= 2.5,  # Standard UART tolerance limit
            "bit_duration_us": round(bit_duration_us, 3),
            "frame_time_8n1_us": round(frame_time_us, 3),
            "max_throughput_bytes_per_sec": round(max_bytes_per_sec, 1)
        }

    # =========================================================================
    # Feature 264: SPI Communication Diagram Explorer
    # =========================================================================
    def calculate_spi_parameters(
        self,
        f_pclk_hz: float,
        prescaler: int = 4,
        cpol: int = 0,
        cpha: int = 0
    ) -> Dict[str, Any]:
        """
        Calculates SPI bus parameters for Motorola SPI Modes 0, 1, 2, 3.
        cpol: 0 (Clock idle Low), 1 (Clock idle High)
        cpha: 0 (Sample on 1st leading edge), 1 (Sample on 2nd trailing edge)
        prescaler: 2, 4, 8, 16, 32, 64, 128, 256
        """
        valid_prescalers = [2, 4, 8, 16, 32, 64, 128, 256]
        if prescaler not in valid_prescalers:
            raise ValueError(f"Invalid SPI prescaler {prescaler}. Must be one of {valid_prescalers}")

        cpol_val = 1 if cpol else 0
        cpha_val = 1 if cpha else 0
        spi_mode = (cpol_val * 2) + cpha_val

        sck_freq_hz = f_pclk_hz / prescaler
        sck_period_us = (1.0 / sck_freq_hz) * 1e6
        byte_transfer_time_us = 8.0 * sck_period_us
        max_throughput_kb_per_sec = (sck_freq_hz / 8.0) / 1024.0

        edge_descriptions = {
            0: "Mode 0 (CPOL=0, CPHA=0): SCK idle Low. Sample on Leading/Rising edge, Shift on Trailing/Falling edge.",
            1: "Mode 1 (CPOL=0, CPHA=1): SCK idle Low. Shift on Leading/Rising edge, Sample on Trailing/Falling edge.",
            2: "Mode 2 (CPOL=1, CPHA=0): SCK idle High. Sample on Leading/Falling edge, Shift on Trailing/Rising edge.",
            3: "Mode 3 (CPOL=1, CPHA=1): SCK idle High. Shift on Leading/Falling edge, Sample on Trailing/Rising edge."
        }

        return {
            "spi_mode": spi_mode,
            "cpol": cpol_val,
            "cpha": cpha_val,
            "prescaler": prescaler,
            "sck_freq_hz": round(sck_freq_hz, 2),
            "sck_period_us": round(sck_period_us, 4),
            "byte_transfer_time_us": round(byte_transfer_time_us, 3),
            "max_throughput_kb_per_sec": round(max_throughput_kb_per_sec, 2),
            "mode_description": edge_descriptions[spi_mode]
        }

    # =========================================================================
    # Feature 265: I2C Address and Transaction Explorer
    # =========================================================================
    def calculate_i2c_bus_parameters(
        self,
        slave_address_7bit: int,
        bus_speed_mode: str = "STANDARD",
        vdd_v: float = 3.3,
        bus_capacitance_pf: float = 150.0
    ) -> Dict[str, Any]:
        """
        Calculates I2C 8-bit Read/Write addresses, bus timing constraints,
        and pull-up resistor sizing limits (Rp_min and Rp_max).
        bus_speed_mode: 'STANDARD' (100kHz), 'FAST' (400kHz), 'FAST_PLUS' (1000kHz)
        """
        if not (0 <= slave_address_7bit <= 127):
            raise ValueError("7-bit I2C address must be between 0x00 and 0x7F.")

        write_byte = (slave_address_7bit << 1) | 0
        read_byte = (slave_address_7bit << 1) | 1

        speed_specs = {
            "STANDARD": {"freq_hz": 100000, "t_r_max_ns": 1000.0, "i_ol_ma": 3.0, "v_ol_v": 0.4},
            "FAST": {"freq_hz": 400000, "t_r_max_ns": 300.0, "i_ol_ma": 3.0, "v_ol_v": 0.4},
            "FAST_PLUS": {"freq_hz": 1000000, "t_r_max_ns": 120.0, "i_ol_ma": 20.0, "v_ol_v": 0.4}
        }
        spec = speed_specs.get(bus_speed_mode.upper(), speed_specs["STANDARD"])

        # Pull-up Resistor sizing (I2C Specification Rev 7.0)
        # Rp_min = (Vdd - Vol) / Iol
        rp_min_ohms = ((vdd_v - spec["v_ol_v"]) / (spec["i_ol_ma"] * 1e-3))

        # Rp_max = tr / (0.8473 * Cb)
        cb_farads = bus_capacitance_pf * 1e-12
        rp_max_ohms = (spec["t_r_max_ns"] * 1e-9) / (0.8473 * cb_farads)

        # Standard recommended resistor (nearest common E24 value between min and max)
        recommended_rp_ohms = math.sqrt(rp_min_ohms * rp_max_ohms)

        return {
            "slave_address_7bit_hex": f"0x{slave_address_7bit:02X}",
            "write_byte_hex": f"0x{write_byte:02X}",
            "read_byte_hex": f"0x{read_byte:02X}",
            "bus_speed_mode": bus_speed_mode.upper(),
            "clock_freq_hz": spec["freq_hz"],
            "bus_capacitance_pf": bus_capacitance_pf,
            "rp_min_ohms": round(rp_min_ohms, 1),
            "rp_max_ohms": round(rp_max_ohms, 1),
            "recommended_rp_ohms": round(recommended_rp_ohms, 1),
            "is_valid_pullup_window": rp_min_ohms < rp_max_ohms
        }

    # =========================================================================
    # Feature 266: Interrupt Handling Learning Simulator
    # =========================================================================
    def simulate_nvic_priority(
        self,
        prigroup: int = 3,
        irq_a: Optional[Dict[str, Any]] = None,
        irq_b: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simulates ARM Cortex-M NVIC Priority Grouping and Preemption logic.
        AIRCR PRIGROUP values 0 to 4 (assuming 4 bits of priority implemented in STM32F4).
        """
        prigroup_safe = max(0, min(4, int(prigroup)))
        # PRIGROUP = 3: 4 preemption levels (bits [7:7]), 8 subpriority levels (bits [6:4]) in 4-bit config
        # Standard Cortex-M 4-bit priority mapping (STM32 implements bits 7..4)
        preempt_bits = max(0, 4 - prigroup_safe)
        sub_bits = 4 - preempt_bits

        max_preempt = (1 << preempt_bits) - 1
        max_sub = (1 << sub_bits) - 1

        a = irq_a or {"name": "USART1_IRQn", "preempt": 1, "sub": 2}
        b = irq_b or {"name": "EXTI0_IRQn", "preempt": 0, "sub": 1}

        # Preemption check: Lower numerical priority value = higher urgency
        preempt_a = int(a.get("preempt", 0))
        preempt_b = int(b.get("preempt", 0))
        sub_a = int(a.get("sub", 0))
        sub_b = int(b.get("sub", 0))

        if preempt_a < preempt_b:
            execution_order = f"{a['name']} preempts {b['name']} (Preempt {preempt_a} < {preempt_b})"
            preempt_occurred = True
        elif preempt_b < preempt_a:
            execution_order = f"{b['name']} preempts {a['name']} (Preempt {preempt_b} < {preempt_a})"
            preempt_occurred = True
        else:
            # Same preemption level: whoever is currently running finishes; if simultaneous, subpriority decides
            preempt_occurred = False
            if sub_a < sub_b:
                execution_order = f"No preemption. If pending simultaneously, {a['name']} runs first (Subpriority {sub_a} < {sub_b})"
            elif sub_b < sub_a:
                execution_order = f"No preemption. If pending simultaneously, {b['name']} runs first (Subpriority {sub_b} < {sub_a})"
            else:
                execution_order = f"Identical priorities. Hardware IRQ number decides dispatch order."

        return {
            "prigroup": prigroup_safe,
            "preempt_bits": preempt_bits,
            "subpriority_bits": sub_bits,
            "num_preempt_levels": 1 << preempt_bits,
            "num_sub_levels": 1 << sub_bits,
            "preempt_occurred": preempt_occurred,
            "execution_outcome": execution_order,
            "latency_metrics": {
                "stacking_cycles": 12,
                "unstacking_cycles": 12,
                "tail_chaining_cycles": 6,
                "late_arriving_cycles": 0
            }
        }

    # =========================================================================
    # Feature 267: Timer and Counter Configuration Calculator
    # =========================================================================
    def solve_timer_configuration(
        self,
        f_tim_hz: float,
        target_freq_hz: float
    ) -> Dict[str, Any]:
        """
        Solves for optimal 16-bit Prescaler (PSC) and Auto-Reload Register (ARR)
        to synthesize target_freq_hz from timer clock f_tim_hz with zero or minimal error.
        f_out = f_tim / ((PSC + 1) * (ARR + 1))
        """
        if f_tim_hz <= 0 or target_freq_hz <= 0:
            raise ValueError("Timer clock and target frequency must be strictly positive.")

        total_divider = round(f_tim_hz / target_freq_hz)
        if total_divider < 1:
            total_divider = 1

        best_psc = 0
        best_arr = 0
        best_error = float("inf")

        # Preferred clean round PSC choices (e.g. 1us or 1ms tick: PSC = f_tim/1MHz - 1)
        # Search feasible PSC values between 0 and 65535
        # Start by testing natural factor pairs
        sqrt_div = int(math.isqrt(total_divider))
        for psc_candidate in range(max(0, sqrt_div - 200), min(65536, sqrt_div + 200)):
            if psc_candidate + 1 <= 0:
                continue
            arr_candidate = (total_divider // (psc_candidate + 1)) - 1
            if 0 <= arr_candidate <= 65535:
                actual_div = (psc_candidate + 1) * (arr_candidate + 1)
                actual_f = f_tim_hz / actual_div
                err = abs(actual_f - target_freq_hz) / target_freq_hz * 100.0
                if err < best_error:
                    best_error = err
                    best_psc = psc_candidate
                    best_arr = arr_candidate
                    if best_error == 0.0:
                        break

        # If best_error is still not zero, fall back to optimal ratio search
        if best_error > 0.0:
            for psc in [0, 1, 3, 7, 9, 15, 31, 63, 79, 83, 99, 167, 999, 8399]:
                if psc > 65535:
                    continue
                arr = round(f_tim_hz / (target_freq_hz * (psc + 1))) - 1
                if 0 <= arr <= 65535:
                    actual_f = f_tim_hz / ((psc + 1) * (arr + 1))
                    err = abs(actual_f - target_freq_hz) / target_freq_hz * 100.0
                    if err < best_error:
                        best_error = err
                        best_psc = psc
                        best_arr = arr

        actual_freq = f_tim_hz / ((best_psc + 1) * (best_arr + 1))
        tick_resolution_us = ((best_psc + 1) / f_tim_hz) * 1e6
        period_ms = (1.0 / actual_freq) * 1000.0

        return {
            "f_tim_hz": f_tim_hz,
            "target_freq_hz": target_freq_hz,
            "prescaler_psc": best_psc,
            "auto_reload_arr": best_arr,
            "actual_freq_hz": round(actual_freq, 4),
            "error_percent": round(best_error, 5),
            "tick_resolution_us": round(tick_resolution_us, 4),
            "period_ms": round(period_ms, 4)
        }

    # =========================================================================
    # Feature 268: PWM Duty Cycle Visualizer
    # =========================================================================
    def calculate_pwm_parameters(
        self,
        arr: int,
        ccr: int,
        vdd_v: float = 3.3,
        f_tim_hz: float = 84000000.0,
        psc: int = 83,
        mode: str = "EDGE_ALIGNED"
    ) -> Dict[str, Any]:
        """
        Calculates PWM duty cycle percentage, pulse widths, and average DC voltage.
        Duty Cycle % = (CCR / (ARR + 1)) * 100 (for Edge-Aligned Mode 1)
        """
        if arr < 0 or ccr < 0:
            raise ValueError("ARR and CCR register values must be non-negative.")

        # Clamp CCR to ARR + 1
        ccr_clamped = min(ccr, arr + 1)
        duty_cycle_percent = (ccr_clamped / (arr + 1)) * 100.0 if (arr + 1) > 0 else 0.0

        is_center_aligned = mode.upper() == "CENTER_ALIGNED"
        if is_center_aligned:
            # Center-aligned frequency is halved because counter counts UP then DOWN
            freq_hz = f_tim_hz / (2.0 * (psc + 1) * arr) if arr > 0 else 0.0
        else:
            freq_hz = f_tim_hz / ((psc + 1) * (arr + 1))

        period_us = (1.0 / freq_hz) * 1e6 if freq_hz > 0 else 0.0
        t_high_us = (duty_cycle_percent / 100.0) * period_us
        t_low_us = period_us - t_high_us
        v_avg = vdd_v * (duty_cycle_percent / 100.0)

        return {
            "arr": arr,
            "ccr": ccr_clamped,
            "mode": "Center-Aligned" if is_center_aligned else "Edge-Aligned",
            "duty_cycle_percent": round(duty_cycle_percent, 2),
            "frequency_hz": round(freq_hz, 2),
            "period_us": round(period_us, 3),
            "t_high_us": round(t_high_us, 3),
            "t_low_us": round(t_low_us, 3),
            "v_avg_volts": round(v_avg, 3)
        }

    # =========================================================================
    # Feature 269: Memory Map Explorer & Bit-Band Alias Calculator
    # =========================================================================
    def calculate_bitband_alias(
        self,
        byte_address: int,
        bit_index: int
    ) -> Dict[str, Any]:
        """
        Calculates the ARM Cortex-M bit-band alias address for atomic bit manipulation.
        Formula: Alias = Alias_Base + (Byte_Offset * 32) + (Bit_Index * 4)
        Supported bit-band regions:
          - SRAM: 0x20000000 to 0x200FFFFF -> Alias: 0x22000000
          - Peripherals: 0x40000000 to 0x400FFFFF -> Alias: 0x42000000
        """
        if not (0 <= bit_index <= 7):
            raise ValueError("Bit index must be between 0 and 7.")

        if 0x20000000 <= byte_address <= 0x200FFFFF:
            region = "SRAM (1MB Bit-Band Region)"
            base = 0x20000000
            alias_base = 0x22000000
        elif 0x40000000 <= byte_address <= 0x400FFFFF:
            region = "Peripherals (1MB Bit-Band Region)"
            base = 0x40000000
            alias_base = 0x42000000
        else:
            raise ValueError(f"Address 0x{byte_address:08X} is outside standard Cortex-M bit-band regions.")

        byte_offset = byte_address - base
        alias_address = alias_base + (byte_offset * 32) + (bit_index * 4)

        c_macro = f"#define BITBAND_ADDR(addr, bit) ((void *)({alias_base:#x} + (((uint32_t)(addr) - {base:#x}) * 32) + ((bit) * 4)))"

        return {
            "region": region,
            "byte_address_hex": f"0x{byte_address:08X}",
            "bit_index": bit_index,
            "alias_address_hex": f"0x{alias_address:08X}",
            "c_macro": c_macro,
            "atomic_benefit": "Guarantees single-cycle atomic read-modify-write without disabling interrupts."
        }

    # =========================================================================
    # Feature 270: Embedded C Code Snippet Library
    # =========================================================================
    def get_code_snippet(self, snippet_id: str) -> Dict[str, Any]:
        """Retrieves bare-metal embedded C template with dual-language commentary."""
        key = snippet_id.upper()
        if key not in BARE_METAL_CODE_LIBRARY:
            valid_keys = list(BARE_METAL_CODE_LIBRARY.keys())
            raise ValueError(f"Unknown snippet '{snippet_id}'. Available snippets: {valid_keys}")
        return BARE_METAL_CODE_LIBRARY[key]

    def list_code_snippets(self) -> List[Dict[str, Any]]:
        """Lists all bare-metal code snippet summaries."""
        return [{"snippet_id": k, **v} for k, v in BARE_METAL_CODE_LIBRARY.items()]

    # =========================================================================
    # Persistence Methods (SQLite WAL)
    # =========================================================================
    def save_simulation(
        self,
        student_id: str,
        feature_id: int,
        feature_name: str,
        input_payload: Dict[str, Any],
        computed_metrics: Dict[str, Any]
    ) -> int:
        """Saves an embedded simulation event to the SQLite WAL database."""
        with self._lock:
            conn = self._get_connection()
            try:
                now = datetime.now(timezone.utc).isoformat()
                cur = conn.execute("""
                    INSERT INTO embedded_simulations (
                        student_id, feature_id, feature_name, input_payload, computed_metrics, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    student_id,
                    feature_id,
                    feature_name,
                    json.dumps(input_payload),
                    json.dumps(computed_metrics),
                    now
                ))
                conn.commit()
                return cur.lastrowid
            finally:
                conn.close()

    def get_simulations(self, student_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves simulation history for a student."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.execute("""
                    SELECT id, student_id, feature_id, feature_name, input_payload, computed_metrics, created_at
                    FROM embedded_simulations
                    WHERE student_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                """, (student_id, limit))
                rows = cur.fetchall()
                results = []
                for r in rows:
                    results.append({
                        "id": r["id"],
                        "student_id": r["student_id"],
                        "feature_id": r["feature_id"],
                        "feature_name": r["feature_name"],
                        "input_payload": json.loads(r["input_payload"]),
                        "computed_metrics": json.loads(r["computed_metrics"]),
                        "created_at": r["created_at"]
                    })
                return results
            finally:
                conn.close()

    def save_timer_config(
        self,
        student_id: str,
        mcu_family: str,
        tim_clock_hz: float,
        target_freq_hz: float,
        prescaler: int,
        auto_reload: int,
        actual_freq_hz: float,
        error_percent: float
    ) -> int:
        """Saves a timer configuration to SQLite WAL."""
        with self._lock:
            conn = self._get_connection()
            try:
                now = datetime.now(timezone.utc).isoformat()
                cur = conn.execute("""
                    INSERT INTO timer_configurations (
                        student_id, mcu_family, tim_clock_hz, target_freq_hz,
                        prescaler, auto_reload, actual_freq_hz, error_percent, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    student_id, mcu_family, tim_clock_hz, target_freq_hz,
                    prescaler, auto_reload, actual_freq_hz, error_percent, now
                ))
                conn.commit()
                return cur.lastrowid
            finally:
                conn.close()

    def get_timer_configs(self, student_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves saved timer configurations."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.execute("""
                    SELECT id, student_id, mcu_family, tim_clock_hz, target_freq_hz,
                           prescaler, auto_reload, actual_freq_hz, error_percent, created_at
                    FROM timer_configurations
                    WHERE student_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                """, (student_id, limit))
                rows = cur.fetchall()
                return [dict(r) for r in rows]
            finally:
                conn.close()
