import React, { useState, useMemo, useEffect } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Phase F: Embedded Systems & Microcontrollers (Features 261–270)
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 *
 * Features:
 *   - Feature 261: Microcontroller Pinout Explorer (STM32F401, ATmega328P, ESP32, RP2040)
 *   - Feature 262: GPIO Configuration Learning Tool (MODER, OTYPER, OSPEEDR, PUPDR, AFR)
 *   - Feature 263: UART Communication Visualizer (BRR Mantissa/Fraction, Frame Timing, Bit Duration)
 *   - Feature 264: SPI Communication Diagram Explorer (Modes 0-3, CPOL/CPHA, SCK Prescaler, Bitrate)
 *   - Feature 265: I2C Address and Transaction Explorer (7-bit/8-bit R/W, ACK/NACK, Pull-up Resistor Math)
 *   - Feature 266: Interrupt Handling Learning Simulator (NVIC Priority Grouping, Preempt/Subpriority, Latency)
 *   - Feature 267: Timer and Counter Configuration Calculator (PSC, ARR, Overflow Frequency, Auto-Solver)
 *   - Feature 268: PWM Duty Cycle Visualizer (CCR, ARR, Edge vs Center-Aligned, Average Voltage)
 *   - Feature 269: Memory Map Explorer (Flash, SRAM, Peripherals, Bit-Band Alias Address Calculator)
 *   - Feature 270: Embedded C Code Snippet Library (Bare-Metal Templates, Bilingual English/Tamil Notes)
 * Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
 * ========================================================================================
 */

// Microcontroller Profiles & Pinout DB (Feature 261)
const MCUS = {
  STM32F401CCU6: {
    name: "STM32F401CCU6 Black Pill",
    arch: "ARM Cortex-M4F (32-bit)",
    fpu: "Single-Precision FPU (FPv4-SP)",
    clockMhz: 84,
    voltage: "3.3V",
    flashKb: 256,
    sramKb: 64,
    gpioCount: 36,
    adc: "12-bit (16 channels)",
    dac: "None",
    fiveVTolerant: true,
    timers: ["TIM1 (Advanced)", "TIM2, TIM5 (32-bit)", "TIM3, TIM4 (16-bit)", "TIM9..11"],
    peripherals: "3x USART, 3x SPI, 3x I2C, USB OTG FS",
    pins: [
      { num: 1, name: "VBAT", type: "POWER", desc: "Backup Battery Power", ft: false },
      { num: 2, name: "PC13", type: "GPIO", desc: "User LED (Active Low) / RTC_AF1", ft: false },
      { num: 3, name: "PC14", type: "OSC", desc: "OSC32_IN (32.768 kHz RTC)", ft: false },
      { num: 4, name: "PC15", type: "OSC", desc: "OSC32_OUT", ft: false },
      { num: 5, name: "PA0", type: "ANALOG_TIM", desc: "ADC1_IN0 / TIM2_CH1 / TIM5_CH1 / WKUP", ft: false },
      { num: 6, name: "PA1", type: "ANALOG_TIM", desc: "ADC1_IN1 / TIM2_CH2 / TIM5_CH2", ft: false },
      { num: 7, name: "PA2", type: "USART_ADC", desc: "USART2_TX / ADC1_IN2 / TIM2_CH3", ft: false },
      { num: 8, name: "PA3", type: "USART_ADC", desc: "USART2_RX / ADC1_IN3 / TIM2_CH4", ft: false },
      { num: 9, name: "PA4", type: "SPI_ADC", desc: "SPI1_NSS / ADC1_IN4 / USART2_CK", ft: false },
      { num: 10, name: "PA5", type: "SPI_ADC", desc: "SPI1_SCK / ADC1_IN5 / TIM2_CH1", ft: false },
      { num: 11, name: "PA6", type: "SPI_ADC", desc: "SPI1_MISO / ADC1_IN6 / TIM3_CH1", ft: false },
      { num: 12, name: "PA7", type: "SPI_ADC", desc: "SPI1_MOSI / ADC1_IN7 / TIM3_CH2", ft: false },
      { num: 13, name: "PB0", type: "ANALOG_TIM", desc: "ADC1_IN8 / TIM3_CH3 / TIM1_CH2N", ft: false },
      { num: 14, name: "PB1", type: "ANALOG_TIM", desc: "ADC1_IN9 / TIM3_CH4 / TIM1_CH3N", ft: false },
      { num: 15, name: "PB2", type: "BOOT", desc: "BOOT1 / PB2 (5V Tolerant)", ft: true },
      { num: 16, name: "PB10", type: "I2C_SPI", desc: "I2C2_SCL / SPI2_SCK / TIM2_CH3", ft: true },
      { num: 17, name: "3V3", type: "POWER", desc: "+3.3V System Power Rail", ft: false },
      { num: 18, name: "GND", type: "POWER", desc: "System Ground", ft: false },
      { num: 19, name: "5V", type: "POWER", desc: "+5V USB Power Rail (LDO In)", ft: false },
      { num: 20, name: "PB6", type: "I2C_TIM", desc: "I2C1_SCL / TIM4_CH1 / USART1_TX", ft: true },
      { num: 21, name: "PB7", type: "I2C_TIM", desc: "I2C1_SDA / TIM4_CH2 / USART1_RX", ft: true },
      { num: 22, name: "PB8", type: "I2C_TIM", desc: "I2C1_SCL / TIM4_CH3 / TIM10_CH1", ft: true },
      { num: 23, name: "PB9", type: "I2C_TIM", desc: "I2C1_SDA / TIM4_CH4 / TIM11_CH1", ft: true },
      { num: 24, name: "PA9", type: "USART", desc: "USART1_TX / TIM1_CH2 (5V Tolerant)", ft: true },
      { num: 25, name: "PA10", type: "USART", desc: "USART1_RX / TIM1_CH3 (5V Tolerant)", ft: true },
      { num: 26, name: "PA11", type: "USB", desc: "USB_DM (Data-) / TIM1_CH4 / CAN_RX", ft: true },
      { num: 27, name: "PA12", type: "USB", desc: "USB_DP (Data+) / TIM1_ETR / CAN_TX", ft: true }
    ]
  },
  ATMEGA328P: {
    name: "ATmega328P-PU",
    arch: "AVR 8-bit RISC",
    fpu: "None (Software Emulated)",
    clockMhz: 16,
    voltage: "5.0V",
    flashKb: 32,
    sramKb: 2,
    gpioCount: 23,
    adc: "10-bit (6 channels)",
    dac: "None",
    fiveVTolerant: true,
    timers: ["Timer0 (8-bit)", "Timer1 (16-bit)", "Timer2 (8-bit)"],
    peripherals: "1x USART, 1x SPI, 1x I2C",
    pins: [
      { num: 1, name: "PC6/RESET", type: "RESET", desc: "Active Low Reset Pin", ft: true },
      { num: 2, name: "PD0/RXD", type: "USART", desc: "USART Receive Data (Digital 0)", ft: true },
      { num: 3, name: "PD1/TXD", type: "USART", desc: "USART Transmit Data (Digital 1)", ft: true },
      { num: 4, name: "PD2/INT0", type: "INT", desc: "External Interrupt 0 (Digital 2)", ft: true },
      { num: 5, name: "PD3/INT1/OC2B", type: "PWM", desc: "Ext Interrupt 1 / Timer2 PWM (Digital 3)", ft: true },
      { num: 7, name: "VCC", type: "POWER", desc: "+5V Supply Power", ft: true },
      { num: 8, name: "GND", type: "POWER", desc: "System Ground", ft: true },
      { num: 9, name: "PB6/XTAL1", type: "OSC", desc: "16 MHz Crystal Oscillator In", ft: true },
      { num: 10, name: "PB7/XTAL2", type: "OSC", desc: "16 MHz Crystal Oscillator Out", ft: true },
      { num: 11, name: "PD5/OC0B/T1", type: "PWM", desc: "Timer0 PWM / Timer1 Counter In (Digital 5)", ft: true },
      { num: 12, name: "PD6/OC0A", type: "PWM", desc: "Timer0 PWM (Digital 6)", ft: true },
      { num: 15, name: "PB1/OC1A", type: "PWM", desc: "Timer1 16-bit PWM (Digital 9)", ft: true },
      { num: 16, name: "PB2/OC1B/SS", type: "SPI", desc: "SPI Slave Select (Digital 10)", ft: true },
      { num: 17, name: "PB3/MOSI", type: "SPI", desc: "SPI Master Out Slave In (Digital 11)", ft: true },
      { num: 18, name: "PB4/MISO", type: "SPI", desc: "SPI Master In Slave Out (Digital 12)", ft: true },
      { num: 19, name: "PB5/SCK", type: "SPI", desc: "SPI Serial Clock / Built-in LED (Digital 13)", ft: true },
      { num: 23, name: "PC0/ADC0", type: "ADC", desc: "10-bit ADC Channel 0 (Analog 0)", ft: true },
      { num: 27, name: "PC4/SDA", type: "I2C", desc: "I2C Serial Data (Analog 4)", ft: true },
      { num: 28, name: "PC5/SCL", type: "I2C", desc: "I2C Serial Clock (Analog 5)", ft: true }
    ]
  },
  ESP32_WROOM: {
    name: "ESP32-WROOM-32",
    arch: "Xtensa Dual-Core 32-bit LX6",
    fpu: "Single-Precision Hardware FPU",
    clockMhz: 240,
    voltage: "3.3V",
    flashKb: 4096,
    sramKb: 520,
    gpioCount: 34,
    adc: "12-bit (18 channels)",
    dac: "8-bit (2 channels)",
    fiveVTolerant: false,
    timers: ["4 x 64-bit General Purpose Timers"],
    peripherals: "3x UART, 3x SPI, 2x I2C, 2x I2S, CAN 2.0, Wi-Fi 802.11 b/g/n, BLE 4.2",
    pins: [
      { num: 1, name: "3V3", type: "POWER", desc: "+3.3V Regulated Power", ft: false },
      { num: 2, name: "EN", type: "RESET", desc: "Chip Enable / Reset", ft: false },
      { num: 3, name: "GPIO36/VP", type: "ADC", desc: "ADC1_CH0 / Sensor VP (Input Only)", ft: false },
      { num: 4, name: "GPIO39/VN", type: "ADC", desc: "ADC1_CH3 / Sensor VN (Input Only)", ft: false },
      { num: 5, name: "GPIO34", type: "ADC", desc: "ADC1_CH6 (Input Only, No internal pullup)", ft: false },
      { num: 6, name: "GPIO35", type: "ADC", desc: "ADC1_CH7 (Input Only)", ft: false },
      { num: 7, name: "GPIO32", type: "TOUCH_ADC", desc: "Touch9 / ADC1_CH4 / 32K_XP", ft: false },
      { num: 8, name: "GPIO33", type: "TOUCH_ADC", desc: "Touch8 / ADC1_CH5 / 32K_XN", ft: false },
      { num: 9, name: "GPIO25/DAC1", type: "DAC", desc: "8-bit DAC1 / ADC2_CH8", ft: false },
      { num: 10, name: "GPIO26/DAC2", type: "DAC", desc: "8-bit DAC2 / ADC2_CH9", ft: false },
      { num: 11, name: "GPIO27", type: "TOUCH", desc: "Touch7 / ADC2_CH7", ft: false },
      { num: 12, name: "GPIO14", type: "SPI", desc: "HSPI_CLK / Touch6 / ADC2_CH6", ft: false },
      { num: 13, name: "GPIO12", type: "SPI", desc: "HSPI_MISO / Touch5 (Strapping Pin)", ft: false },
      { num: 14, name: "GND", type: "POWER", desc: "System Ground", ft: false },
      { num: 15, name: "GPIO13", type: "SPI", desc: "HSPI_MOSI / Touch4 / ADC2_CH4", ft: false },
      { num: 21, name: "GPIO21/SDA", type: "I2C", desc: "Default Wire I2C SDA", ft: false },
      { num: 22, name: "GPIO22/SCL", type: "I2C", desc: "Default Wire I2C SCL", ft: false },
      { num: 23, name: "GPIO1/TX0", type: "UART", desc: "UART0 Transmit (USB Debug)", ft: false },
      { num: 24, name: "GPIO3/RX0", type: "UART", desc: "UART0 Receive (USB Debug)", ft: false }
    ]
  },
  RP2040: {
    name: "Raspberry Pi RP2040",
    arch: "Dual ARM Cortex-M0+ (32-bit)",
    fpu: "None (Fast ROM Software Floating Point)",
    clockMhz: 133,
    voltage: "3.3V",
    flashKb: 2048,
    sramKb: 264,
    gpioCount: 30,
    adc: "12-bit (4 channels)",
    dac: "None",
    fiveVTolerant: false,
    timers: ["64-bit Microsecond Timer + 8 PWM Dual-Channel Slices"],
    peripherals: "2x UART, 2x SPI, 2x I2C, 2x PIO (8 State Machines)",
    pins: [
      { num: 1, name: "GP0", type: "UART_SPI", desc: "UART0 TX / I2C0 SDA / SPI0 RX", ft: false },
      { num: 2, name: "GP1", type: "UART_SPI", desc: "UART0 RX / I2C0 SCL / SPI0 CSn", ft: false },
      { num: 3, name: "GND", type: "POWER", desc: "Ground", ft: false },
      { num: 4, name: "GP2", type: "SPI_I2C", desc: "SPI0 SCK / I2C1 SDA", ft: false },
      { num: 5, name: "GP3", type: "SPI_I2C", desc: "SPI0 TX / I2C1 SCL", ft: false },
      { num: 6, name: "GP4", type: "UART_I2C", desc: "UART1 TX / I2C0 SDA", ft: false },
      { num: 7, name: "GP5", type: "UART_I2C", desc: "UART1 RX / I2C0 SCL", ft: false },
      { num: 8, name: "GND", type: "POWER", desc: "Ground", ft: false },
      { num: 9, name: "GP6", type: "PWM", desc: "PWM3 A / I2C1 SDA", ft: false },
      { num: 10, name: "GP7", type: "PWM", desc: "PWM3 B / I2C1 SCL", ft: false },
      { num: 31, name: "GP26/ADC0", type: "ADC", desc: "12-bit ADC Channel 0", ft: false },
      { num: 32, name: "GP27/ADC1", type: "ADC", desc: "12-bit ADC Channel 1", ft: false },
      { num: 34, name: "GP28/ADC2", type: "ADC", desc: "12-bit ADC Channel 2", ft: false },
      { num: 36, name: "3V3", type: "POWER", desc: "+3.3V Output Power", ft: false },
      { num: 40, name: "VBUS", type: "POWER", desc: "+5V USB Power Rail", ft: false }
    ]
  }
};

// Bare-Metal C Templates (Feature 270)
const CODE_SNIPPETS = {
  GPIO_TOGGLE: {
    title: "GPIO Pin Toggle (Cortex-M CMSIS Bare-Metal)",
    mcu: "STM32F401 (GPIOC Pin 13 User LED)",
    tamilTitle: "GPIO பின் நிலை மாற்றி (LED Toggle)",
    tamilDesc: "GPIOC பின் 13 இல் இணைக்கப்பட்ட LED-ஐ BSRR ரிஜிஸ்டர் கொண்டு ஆட்டாமிக் முறையில் கட்டுப்படுத்தும் நிரல்.",
    code: `/* STM32F401CCU6 Bare-Metal GPIO Toggle (PC13 User LED) */
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

    /* 2. Configure PC13 as Output (MODER13 = 01b) */
    GPIOC->MODER &= ~(3U << (13 * 2));
    GPIOC->MODER |=  (1U << (13 * 2));

    /* 3. Output Type: Push-Pull (OTYPER13 = 0) */
    GPIOC->OTYPER &= ~(1U << 13);

    /* 4. Speed: Low 2MHz (OSPEEDR13 = 00b) */
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
}`
  },
  UART_TX: {
    title: "Polled Non-Blocking UART Transmit (USART1)",
    mcu: "STM32F401 (PA9 TX @ 115200 Baud)",
    tamilTitle: "USART தொடர் தொடர்பு பரிமாற்றம்",
    tamilDesc: "USART1 டிரான்ஸ்மிட்டரை துவக்கி 115200 Baud வேகத்தில் தகவலை பிசி டெர்மினலுக்கு அனுப்பும் நிரல்.",
    code: `/* STM32F401 USART1 115200 Baud Transmit */
#include "stm32f4xx.h"

void uart1_init(void) {
    /* 1. Enable GPIOA and USART1 Peripheral Clocks */
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_USART1EN;

    /* 2. Configure PA9 as Alternate Function AF7 (USART1_TX) */
    GPIOA->MODER &= ~(3U << (9 * 2));
    GPIOA->MODER |=  (2U << (9 * 2));
    GPIOA->AFR[1] |= (7U << ((9 - 8) * 4));

    /* 3. Set Baud Rate for 84 MHz APB2 Clock:
     * USART_DIV = 84000000 / (16 * 115200) = 45.5729
     * Mantissa = 45 (0x2D), Fraction = round(0.5729 * 16) = 9 (0x9) -> BRR = 0x02D9 */
    USART1->BRR = 0x02D9;

    /* 4. Enable Transmitter and USART */
    USART1->CR1 = USART_CR1_TE | USART_CR1_UE;
}

void uart1_write_char(char c) {
    while (!(USART1->SR & USART_SR_TXE));
    USART1->DR = (uint16_t)c;
}

void uart1_write_string(const char *str) {
    while (*str) uart1_write_char(*str++);
}`
  },
  SYSTICK_DELAY: {
    title: "SysTick Millisecond Delay Generator",
    mcu: "ARM Cortex-M Core Peripheral",
    tamilTitle: "சிஸ்டிக் (SysTick) நேர தாமதம்",
    tamilDesc: "Cortex-M இன் உட்புற சிஸ்டிக் கவுண்டர் கொண்டு மிகத்துல்லிய மில்லி-நொடி தாமதம் உருவாக்கும் முறை.",
    code: `/* ARM Cortex-M Hardware SysTick Precise Delay */
#include "stm32f4xx.h"

static volatile uint32_t s_ms_ticks = 0;

void SysTick_Handler(void) {
    s_ms_ticks++;
}

void systick_init(uint32_t system_clock_hz) {
    /* Reload for 1ms interrupt: LOAD = (Clock / 1000) - 1 */
    SysTick->LOAD = (system_clock_hz / 1000) - 1;
    SysTick->VAL = 0;
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk |
                    SysTick_CTRL_TICKINT_Msk   |
                    SysTick_CTRL_ENABLE_Msk;
}

void delay_ms(uint32_t ms) {
    uint32_t start = s_ms_ticks;
    while ((s_ms_ticks - start) < ms) {
        __WFI(); /* Wait for interrupt: conserves HP Victus energy */
    }
}`
  },
  TIMER_PWM: {
    title: "Hardware Timer PWM Initialization (TIM2_CH1)",
    mcu: "STM32F401 (PA0 / TIM2_CH1 @ 20 kHz)",
    tamilTitle: "டைமர் PWM சிக்னல் உருவாக்கம்",
    tamilDesc: "TIM2 டைமரைப் பயன்படுத்தி மோட்டார் அல்லது LED பிரகாசத்தைக் கட்டுப்படுத்த PWM அலைவரிசை அமைக்கும் நிரல்.",
    code: `/* STM32F401 Timer 2 Channel 1 PWM (20 kHz, 84 MHz Timer Clock) */
#include "stm32f4xx.h"

void tim2_pwm_init(void) {
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;

    /* PA0 to AF1 (TIM2_CH1) */
    GPIOA->MODER &= ~(3U << (0 * 2));
    GPIOA->MODER |=  (2U << (0 * 2));
    GPIOA->AFR[0] |= (1U << (0 * 4));

    /* Frequency = 84 MHz / 20 kHz = 4200 counts */
    TIM2->PSC = 0;
    TIM2->ARR = 4199;

    /* PWM Mode 1 (OC1M = 110b) + Preload */
    TIM2->CCMR1 |= (6U << TIM_CCMR1_OC1M_Pos) | TIM_CCMR1_OC1PE;
    TIM2->CCR1 = 2100; /* Initial 50% Duty */

    TIM2->CCER |= TIM_CCER_CC1E;
    TIM2->CR1  |= TIM_CR1_ARPE | TIM_CR1_CEN;
}

void set_duty(uint32_t percent) {
    if (percent > 100) percent = 100;
    TIM2->CCR1 = (TIM2->ARR + 1) * percent / 100;
}`
  },
  ADC_CONVERSION: {
    title: "12-bit ADC Single Polled Conversion",
    mcu: "STM32F401 (PA1 / ADC_IN1)",
    tamilTitle: "அனலாக் முதல் டிஜிட்டல் மாற்றம் (ADC)",
    tamilDesc: "PA1 பினில் உள்ள அனலாக் சென்சார் மின்னழுத்தத்தை 12-பிட் டிஜிட்டல் எண்ணாக மாற்றும் நிரல்.",
    code: `/* STM32F401 12-bit ADC1 Conversion on PA1 */
#include "stm32f4xx.h"

void adc1_init(void) {
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_ADC1EN;

    /* PA1 Analog Mode */
    GPIOA->MODER |= (3U << (1 * 2));

    ADC->CCR |= (1U << ADC_CCR_ADCPRE_Pos); /* Clock / 4 = 21MHz */
    ADC1->SQR1 = 0; /* 1 conversion */
    ADC1->SQR3 = 1; /* Channel 1 */
    ADC1->SMPR2 |= (4U << (1 * 3)); /* 84 cycles sample */
    ADC1->CR2 |= ADC_CR2_ADON;
}

uint16_t adc1_read(void) {
    ADC1->CR2 |= ADC_CR2_SWSTART;
    while (!(ADC1->SR & ADC_SR_EOC));
    return (uint16_t)ADC1->DR;
}

float read_voltage(void) {
    return ((float)adc1_read() * 3.3f) / 4095.0f;
}`
  }
};

export default function EmbeddedSystemsHub() {
  const [activeTab, setActiveTab] = useState("mcu_pinout"); // mcu_pinout, gpio_tool, serial_buses, nvic_timers, pwm_code
  const [bilingual, setBilingual] = useState(false);
  const [copiedKey, setCopiedKey] = useState(null);

  // VoltCore STM32 Academy Progress State (Phase 1 Expansion)
  const [stm32CompletedCount, setStm32CompletedCount] = useState(0);

  useEffect(() => {
    try {
      const raw = localStorage.getItem('voltcore_stm32_completed');
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
          setStm32CompletedCount(parsed.length);
        }
      }
    } catch (e) {}
  }, []);

  // Tab 1: MCU Pinout State
  const [selectedMcu, setSelectedMcu] = useState("STM32F401CCU6");
  const [pinFilter, setPinFilter] = useState("ALL");
  const [selectedPin, setSelectedPin] = useState(MCUS["STM32F401CCU6"].pins[4]);

  // Tab 1: Bit-band Explorer State
  const [bitbandRegion, setBitbandRegion] = useState("SRAM");
  const [bitbandAddressHex, setBitbandAddressHex] = useState("20000004");
  const [bitbandBit, setBitbandBit] = useState(2);

  // Tab 2: GPIO Tool State
  const [gpioPin, setGpioPin] = useState(13);
  const [gpioMode, setGpioMode] = useState("OUTPUT"); // INPUT, OUTPUT, AF, ANALOG
  const [gpioOtype, setGpioOtype] = useState("PUSH_PULL"); // PUSH_PULL, OPEN_DRAIN
  const [gpioSpeed, setGpioSpeed] = useState("LOW"); // LOW, MEDIUM, HIGH, VERY_HIGH
  const [gpioPupd, setGpioPupd] = useState("NO_PULL"); // NO_PULL, PULL_UP, PULL_DOWN
  const [gpioAf, setGpioAf] = useState(0);

  // Tab 3: Serial Protocols State
  const [serialSubtab, setSerialSubtab] = useState("UART"); // UART, SPI, I2C
  // UART
  const [uartClockMhz, setUartClockMhz] = useState(84);
  const [uartBaud, setUartBaud] = useState(115200);
  const [uartOver8, setUartOver8] = useState(0);
  const [uartChar, setUartChar] = useState("A");
  // SPI
  const [spiClockMhz, setSpiClockMhz] = useState(84);
  const [spiPrescaler, setSpiPrescaler] = useState(4);
  const [spiCpol, setSpiCpol] = useState(0);
  const [spiCpha, setSpiCpha] = useState(0);
  // I2C
  const [i2cAddrHex, setI2cAddrHex] = useState("68");
  const [i2cSpeed, setI2cSpeed] = useState("STANDARD"); // STANDARD, FAST, FAST_PLUS
  const [i2cCapPf, setI2cCapPf] = useState(150);
  const [i2cVdd, setI2cVdd] = useState(3.3);

  // Tab 4: Interrupts & Timers State
  const [nvicPrigroup, setNvicPrigroup] = useState(3);
  const [irqAPreempt, setIrqAPreempt] = useState(1);
  const [irqASub, setIrqASub] = useState(2);
  const [irqBPreempt, setIrqBPreempt] = useState(0);
  const [irqBSub, setIrqBSub] = useState(1);
  // Timer Solver
  const [timClockMhz, setTimClockMhz] = useState(84);
  const [timTargetFreq, setTimTargetFreq] = useState(1000);

  // Tab 5: PWM & Code State
  const [pwmArr, setPwmArr] = useState(999);
  const [pwmCcr, setPwmCcr] = useState(500);
  const [pwmVdd, setPwmVdd] = useState(3.3);
  const [pwmPsc, setPwmPsc] = useState(83);
  const [pwmMode, setPwmMode] = useState("EDGE_ALIGNED");
  const [selectedSnippetKey, setSelectedSnippetKey] = useState("GPIO_TOGGLE");

  // Copy helper
  const handleCopy = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  // Calculations: Bit-band
  const bitbandResult = useMemo(() => {
    try {
      const addr = parseInt(bitbandAddressHex, 16);
      if (isNaN(addr)) return null;
      const base = bitbandRegion === "SRAM" ? 0x20000000 : 0x40000000;
      const aliasBase = bitbandRegion === "SRAM" ? 0x22000000 : 0x42000000;
      const offset = addr - base;
      const aliasAddr = aliasBase + (offset * 32) + (bitbandBit * 4);
      return {
        byteOffset: offset,
        aliasHex: `0x${(aliasAddr >>> 0).toString(16).toUpperCase().padStart(8, '0')}`,
        cMacro: `*(volatile uint32_t *)0x${(aliasAddr >>> 0).toString(16).toUpperCase().padStart(8, '0')} = 1;`
      };
    } catch {
      return null;
    }
  }, [bitbandRegion, bitbandAddressHex, bitbandBit]);

  // Calculations: GPIO Registers
  const gpioResult = useMemo(() => {
    const modeMap = { INPUT: 0, OUTPUT: 1, AF: 2, ANALOG: 3 };
    const otypeMap = { PUSH_PULL: 0, OPEN_DRAIN: 1 };
    const speedMap = { LOW: 0, MEDIUM: 1, HIGH: 2, VERY_HIGH: 3 };
    const pupdMap = { NO_PULL: 0, PULL_UP: 1, PULL_DOWN: 2 };

    const mVal = modeMap[gpioMode];
    const oVal = otypeMap[gpioOtype];
    const sVal = speedMap[gpioSpeed];
    const pVal = pupdMap[gpioPupd];

    const moderMask = mVal << (gpioPin * 2);
    const otyperMask = oVal << gpioPin;
    const ospeedrMask = sVal << (gpioPin * 2);
    const pupdrMask = pVal << (gpioPin * 2);

    const afrIdx = gpioPin < 8 ? 0 : 1;
    const afrShift = (gpioPin % 8) * 4;
    const afrMask = gpioAf << afrShift;

    return {
      moderHex: `0x${(moderMask >>> 0).toString(16).toUpperCase().padStart(8, '0')}`,
      otyperHex: `0x${(otyperMask >>> 0).toString(16).toUpperCase().padStart(4, '0')}`,
      ospeedrHex: `0x${(ospeedrMask >>> 0).toString(16).toUpperCase().padStart(8, '0')}`,
      pupdrHex: `0x${(pupdrMask >>> 0).toString(16).toUpperCase().padStart(8, '0')}`,
      afrIdx,
      afrHex: `0x${(afrMask >>> 0).toString(16).toUpperCase().padStart(8, '0')}`
    };
  }, [gpioPin, gpioMode, gpioOtype, gpioSpeed, gpioPupd, gpioAf]);

  // Calculations: UART
  const uartResult = useMemo(() => {
    const fClk = uartClockMhz * 1e6;
    const over = uartOver8 === 1 ? 8 : 16;
    const div = fClk / (over * uartBaud);
    let mantissa = Math.floor(div);
    let fraction = Math.round((div - mantissa) * over);
    if (fraction >= over) {
      mantissa += 1;
      fraction = 0;
    }
    const divActual = mantissa + (fraction / over);
    const actualBaud = fClk / (over * divActual);
    const err = Math.abs(actualBaud - uartBaud) / uartBaud * 100;
    const brr = (mantissa << 4) | (fraction & (uartOver8 === 1 ? 0x07 : 0x0F));
    const bitUs = (1.0 / uartBaud) * 1e6;
    const charCode = uartChar.charCodeAt(0) || 65;
    const bits = [];
    for (let i = 0; i < 8; i++) {
      bits.push((charCode >> i) & 1);
    }
    return {
      mantissa,
      fraction,
      brrHex: `0x${brr.toString(16).toUpperCase().padStart(4, '0')}`,
      actualBaud: actualBaud.toFixed(1),
      errorPct: err.toFixed(3),
      bitUs: bitUs.toFixed(2),
      frameUs: (bitUs * 10).toFixed(2),
      dataBits: bits,
      hexChar: `0x${charCode.toString(16).toUpperCase().padStart(2, '0')}`
    };
  }, [uartClockMhz, uartBaud, uartOver8, uartChar]);

  // Calculations: SPI
  const spiResult = useMemo(() => {
    const fClk = spiClockMhz * 1e6;
    const sckFreq = fClk / spiPrescaler;
    const sckPeriodUs = (1.0 / sckFreq) * 1e6;
    const byteUs = 8.0 * sckPeriodUs;
    const mode = (spiCpol * 2) + spiCpha;
    return {
      mode,
      sckFreqMhz: (sckFreq / 1e6).toFixed(3),
      sckPeriodUs: sckPeriodUs.toFixed(3),
      byteUs: byteUs.toFixed(3),
      throughputKbps: ((sckFreq / 8.0) / 1024.0).toFixed(1)
    };
  }, [spiClockMhz, spiPrescaler, spiCpol, spiCpha]);

  // Calculations: I2C
  const i2cResult = useMemo(() => {
    const addr = parseInt(i2cAddrHex, 16) || 0x68;
    const writeByte = (addr << 1) | 0;
    const readByte = (addr << 1) | 1;

    const specs = {
      STANDARD: { f: 100000, trMax: 1000, iol: 0.003, vol: 0.4 },
      FAST: { f: 400000, trMax: 300, iol: 0.003, vol: 0.4 },
      FAST_PLUS: { f: 1000000, trMax: 120, iol: 0.020, vol: 0.4 }
    };
    const s = specs[i2cSpeed];
    const rpMin = (i2cVdd - s.vol) / s.iol;
    const cb = i2cCapPf * 1e-12;
    const rpMax = (s.trMax * 1e-9) / (0.8473 * cb);
    const rpRec = Math.sqrt(rpMin * rpMax);

    return {
      writeHex: `0x${writeByte.toString(16).toUpperCase().padStart(2, '0')}`,
      readHex: `0x${readByte.toString(16).toUpperCase().padStart(2, '0')}`,
      rpMin: Math.round(rpMin),
      rpMax: Math.round(rpMax),
      rpRec: Math.round(rpRec),
      isValid: rpMin < rpMax
    };
  }, [i2cAddrHex, i2cSpeed, i2cCapPf, i2cVdd]);

  // Calculations: NVIC
  const nvicResult = useMemo(() => {
    const preemptBits = Math.max(0, 4 - nvicPrigroup);
    const subBits = 4 - preemptBits;
    const maxPreempt = (1 << preemptBits) - 1;
    const maxSub = (1 << subBits) - 1;

    let preemptOccurred = false;
    let verdict = "";
    if (irqAPreempt < irqBPreempt) {
      preemptOccurred = true;
      verdict = `IRQ A (Preempt ${irqAPreempt}) PREEMPTS IRQ B (Preempt ${irqBPreempt})`;
    } else if (irqBPreempt < irqAPreempt) {
      preemptOccurred = true;
      verdict = `IRQ B (Preempt ${irqBPreempt}) PREEMPTS IRQ A (Preempt ${irqAPreempt})`;
    } else {
      preemptOccurred = false;
      if (irqASub < irqBSub) {
        verdict = `No preemption. If concurrent, IRQ A runs first (Subpriority ${irqASub} < ${irqBSub})`;
      } else if (irqBSub < irqASub) {
        verdict = `No preemption. If concurrent, IRQ B runs first (Subpriority ${irqBSub} < ${irqASub})`;
      } else {
        verdict = `Identical priority levels. Hardware vector index arbitrates.`;
      }
    }
    return {
      preemptBits,
      subBits,
      maxPreempt,
      maxSub,
      preemptOccurred,
      verdict
    };
  }, [nvicPrigroup, irqAPreempt, irqASub, irqBPreempt, irqBSub]);

  // Calculations: Timer Configuration Solver
  const timResult = useMemo(() => {
    const fTim = timClockMhz * 1e6;
    const totalDiv = Math.round(fTim / timTargetFreq);
    let bestPsc = 0;
    let bestArr = 0;
    let bestErr = Infinity;

    // Fast check for common integer divisors
    const sqrt = Math.floor(Math.sqrt(totalDiv));
    for (let psc = Math.max(0, sqrt - 200); psc <= Math.min(65535, sqrt + 200); psc++) {
      const arr = Math.floor(totalDiv / (psc + 1)) - 1;
      if (arr >= 0 && arr <= 65535) {
        const actualF = fTim / ((psc + 1) * (arr + 1));
        const err = Math.abs(actualF - timTargetFreq) / timTargetFreq * 100;
        if (err < bestErr) {
          bestErr = err;
          bestPsc = psc;
          bestArr = arr;
          if (err === 0) break;
        }
      }
    }

    if (bestErr > 0) {
      for (const psc of [0, 7, 15, 31, 79, 83, 99, 167, 839, 999, 8399]) {
        if (psc > 65535) continue;
        const arr = Math.round(fTim / (timTargetFreq * (psc + 1))) - 1;
        if (arr >= 0 && arr <= 65535) {
          const actualF = fTim / ((psc + 1) * (arr + 1));
          const err = Math.abs(actualF - timTargetFreq) / timTargetFreq * 100;
          if (err < bestErr) {
            bestErr = err;
            bestPsc = psc;
            bestArr = arr;
          }
        }
      }
    }

    const actualF = fTim / ((bestPsc + 1) * (bestArr + 1));
    const tickUs = ((bestPsc + 1) / fTim) * 1e6;
    const periodMs = (1.0 / actualF) * 1000;

    return {
      psc: bestPsc,
      arr: bestArr,
      actualF: actualF.toFixed(3),
      errorPct: bestErr.toFixed(5),
      tickUs: tickUs.toFixed(3),
      periodMs: periodMs.toFixed(3)
    };
  }, [timClockMhz, timTargetFreq]);

  // Calculations: PWM
  const pwmResult = useMemo(() => {
    const dutyPct = Math.min(100, Math.max(0, (pwmCcr / (pwmArr + 1)) * 100));
    const fTim = 84000000;
    const isCenter = pwmMode === "CENTER_ALIGNED";
    const freqHz = isCenter
      ? (pwmArr > 0 ? fTim / (2.0 * (pwmPsc + 1) * pwmArr) : 0)
      : (fTim / ((pwmPsc + 1) * (pwmArr + 1)));
    const periodUs = freqHz > 0 ? (1.0 / freqHz) * 1e6 : 0;
    const tHighUs = (dutyPct / 100.0) * periodUs;
    const tLowUs = periodUs - tHighUs;
    const vAvg = pwmVdd * (dutyPct / 100.0);

    return {
      dutyPct: dutyPct.toFixed(1),
      freqHz: Math.round(freqHz),
      periodUs: periodUs.toFixed(1),
      tHighUs: tHighUs.toFixed(1),
      tLowUs: tLowUs.toFixed(1),
      vAvg: vAvg.toFixed(2)
    };
  }, [pwmArr, pwmCcr, pwmVdd, pwmPsc, pwmMode]);

  const activeMcuData = MCUS[selectedMcu];
  const filteredPins = useMemo(() => {
    if (pinFilter === "ALL") return activeMcuData.pins;
    return activeMcuData.pins.filter(p => p.type.includes(pinFilter));
  }, [selectedMcu, pinFilter, activeMcuData]);

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6 text-slate-100">
      {/* Top Banner / Hero */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-indigo-950/80 to-slate-900 border border-indigo-500/30 p-6 shadow-2xl backdrop-blur-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <span className="px-2.5 py-1 text-xs font-mono font-semibold tracking-wider uppercase rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">
                Phase F • Features 261–270
              </span>
              <span className="text-xs text-slate-400 font-mono">
                Core Series • Autonomous Engineering Cluster
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white mt-2 tracking-tight">
              Embedded Systems & Microcontroller Architecture Hub
            </h1>
            <p className="text-sm text-slate-300 max-w-2xl mt-1">
              Interactive Cortex-M, AVR & ESP32 register configurations, hardware serial bus timing visualizers, NVIC interrupt latency models, and bare-metal embedded C generation.
            </p>
          </div>

          <div className="flex items-center gap-3 self-start md:self-auto">
            <button
              onClick={() => setBilingual(!bilingual)}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-all ${
                bilingual
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                  : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'
              }`}
            >
              {bilingual ? 'Tamil Notes: ON (தமிழ்)' : 'Tamil Notes: OFF'}
            </button>
            <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-mono flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              SQLite WAL Active
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 mt-6 pt-4 border-t border-slate-800">
          {[
            { id: "mcu_pinout", label: "1. MCU Pinout & Memory", icon: "칩" },
            { id: "gpio_tool", label: "2. GPIO & Registers", icon: "핀" },
            { id: "serial_buses", label: "3. UART / SPI / I²C", icon: "வரிசை" },
            { id: "nvic_timers", label: "4. Interrupts & Timers", icon: "நேரம்" },
            { id: "pwm_code", label: "5. PWM & Bare-Metal C", icon: "நிரல்" }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold tracking-wide transition-all ${
                activeTab === tab.id
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30 border border-indigo-400/30'
                  : 'bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-700/60 border border-slate-700/60'
              }`}
            >
              <span className="mr-1.5 opacity-70">[{tab.icon}]</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* VoltCore STM32 Academy Expansion Card (Hardware Accelerated Theme Tokens) */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-cyan-950/40 to-slate-900 border border-cyan-500/30 p-5 sm:p-6 shadow-xl backdrop-blur-xl">
        <div className="absolute right-0 top-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2.5 max-w-3xl">
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 text-xs font-bold font-mono border border-cyan-500/40 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                NEW EXPANSION: STM32 ACADEMY
              </span>
              <span className="text-xs text-slate-400 font-mono">
                21 Curriculum Modules • 5 Architectural Tiers
              </span>
            </div>

            <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight flex items-center gap-2">
              <span>⚡</span> VoltCore STM32 Bare-Metal Academy
            </h2>

            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              Dive deep into register-level firmware development on ARM Cortex-M3 (STM32F103 Blue Pill) and Cortex-M4F (Nucleo-F401RE). Master reset sequences, vector tables, PLL clock math, atomic bit manipulation (BSRR), DMA streams, and FreeRTOS without vendor abstraction bloat.
            </p>

            <div className="flex flex-wrap items-center gap-2 pt-1">
              <span className="px-2.5 py-1 rounded-lg bg-slate-950/80 border border-slate-800 text-[11px] font-mono text-cyan-300">
                Nucleo-F401RE (84MHz FPU)
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-slate-950/80 border border-slate-800 text-[11px] font-mono text-blue-300">
                Blue Pill STM32F103 (72MHz)
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-slate-950/80 border border-slate-800 text-[11px] font-mono text-emerald-300">
                Pure C99 & CMSIS Registers
              </span>
            </div>
          </div>

          {/* Interactive Mini Progress Ring & CTA */}
          <div className="flex items-center gap-4 bg-slate-950/70 p-4 rounded-xl border border-cyan-500/20 flex-shrink-0 self-start md:self-auto">
            <div className="relative w-16 h-16 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="32"
                  cy="32"
                  r="26"
                  stroke="currentColor"
                  strokeWidth="5"
                  className="text-slate-800"
                  fill="transparent"
                />
                <circle
                  cx="32"
                  cy="32"
                  r="26"
                  stroke="currentColor"
                  strokeWidth="5"
                  strokeDasharray={2 * Math.PI * 26}
                  strokeDashoffset={(2 * Math.PI * 26) - (Math.round((stm32CompletedCount / 21) * 100) / 100) * (2 * Math.PI * 26)}
                  strokeLinecap="round"
                  className="text-cyan-400 transition-all duration-500"
                  fill="transparent"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                <span className="text-xs font-black text-white font-mono">{Math.round((stm32CompletedCount / 21) * 100)}%</span>
              </div>
            </div>

            <div className="space-y-1.5 font-mono">
              <div className="text-[11px] text-slate-400">{stm32CompletedCount} / 21 Modules</div>
              <a
                href="/embedded-systems/stm32-academy"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-cyan-600/20 border border-cyan-400/40 transition-all"
              >
                <span>Launch Academy</span>
                <span>→</span>
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: MCU Pinout & Memory Map Explorer (Features 261 & 269)              */}
      {/* ========================================================================= */}
      {activeTab === "mcu_pinout" && (
        <div className="space-y-6">
          {/* MCU Specs Top Card */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
            <div className="lg:col-span-1 p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-indigo-400">
                Select Microcontroller
              </h3>
              <div className="space-y-2">
                {Object.keys(MCUS).map(key => (
                  <button
                    key={key}
                    onClick={() => {
                      setSelectedMcu(key);
                      setSelectedPin(MCUS[key].pins[0]);
                    }}
                    className={`w-full text-left px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
                      selectedMcu === key
                        ? 'bg-indigo-600/30 text-indigo-200 border border-indigo-500/50'
                        : 'bg-slate-800/50 text-slate-400 hover:bg-slate-800 border border-slate-700/40'
                    }`}
                  >
                    <div className="font-semibold text-white">{MCUS[key].name}</div>
                    <div className="text-[10px] text-slate-400 font-mono mt-0.5">{MCUS[key].arch}</div>
                  </button>
                ))}
              </div>

              <div className="pt-3 border-t border-slate-800">
                <span className="text-xs text-slate-400">Pin Filter:</span>
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {["ALL", "GPIO", "ADC", "SPI", "I2C", "USART", "PWM", "POWER"].map(f => (
                    <button
                      key={f}
                      onClick={() => setPinFilter(f)}
                      className={`px-2 py-1 text-[10px] font-mono rounded-md border ${
                        pinFilter === f
                          ? 'bg-indigo-500 text-white border-indigo-400'
                          : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'
                      }`}
                    >
                      {f}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Architecture Metrics Dashboard */}
            <div className="lg:col-span-3 p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                <div>
                  <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    {activeMcuData.name}
                    {activeMcuData.fiveVTolerant && (
                      <span className="px-2 py-0.5 text-[10px] font-mono font-semibold rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                        5V Tolerant FT Pins
                      </span>
                    )}
                  </h2>
                  <div className="text-xs text-slate-400 font-mono mt-0.5">
                    Architecture: {activeMcuData.arch} | Core Clock: {activeMcuData.clockMhz} MHz | FPU: {activeMcuData.fpu}
                  </div>
                </div>
                <div className="text-xs text-slate-400 font-mono">
                  Voltage: <span className="text-indigo-300 font-bold">{activeMcuData.voltage}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/50">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Flash ROM</div>
                  <div className="text-base font-extrabold text-white mt-1">{activeMcuData.flashKb} KB</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Code storage</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/50">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">SRAM</div>
                  <div className="text-base font-extrabold text-emerald-400 mt-1">{activeMcuData.sramKb} KB</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Volatile memory</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/50">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">ADC Converter</div>
                  <div className="text-base font-extrabold text-cyan-400 mt-1">{activeMcuData.adc}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Analog sampling</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/50">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">GPIO Count</div>
                  <div className="text-base font-extrabold text-amber-400 mt-1">{activeMcuData.gpioCount} Pins</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Configurable I/O</div>
                </div>
              </div>

              {bilingual && (
                <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 leading-relaxed">
                  <strong>தமிழ் குறிப்பு:</strong> {activeMcuData.name} என்பது அண்ணா பல்கலைக்கழக ECE செய்முறைக்கு உகந்த மைக்ரோகண்ட்ரோலர். 84MHz வேகத்தில் இயங்கும் இதில் ARM Cortex-M4F கோர் மற்றும் ஹார்டுவேர் கணிப்பொறி (FPU) உள்ளது.
                </div>
              )}

              {/* Pin Selection Grid */}
              <div className="space-y-2">
                <div className="text-xs font-mono text-slate-400">
                  Click a pin to view Alternate Functions & Electrical Limits:
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-2 max-h-56 overflow-y-auto p-1">
                  {filteredPins.map(p => (
                    <button
                      key={p.num}
                      onClick={() => setSelectedPin(p)}
                      className={`p-2 rounded-lg text-left border transition-all ${
                        selectedPin?.num === p.num
                          ? 'bg-indigo-600 text-white border-indigo-400 ring-2 ring-indigo-400/30'
                          : 'bg-slate-800/60 text-slate-300 border-slate-700/60 hover:bg-slate-700/60'
                      }`}
                    >
                      <div className="flex items-center justify-between text-[11px] font-bold">
                        <span>P{p.num}</span>
                        {p.ft && <span className="text-[9px] text-emerald-400">FT</span>}
                      </div>
                      <div className="text-xs font-mono truncate text-indigo-300 font-semibold">{p.name}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Selected Pin Details Inspector */}
              {selectedPin && (
                <div className="p-4 rounded-xl bg-slate-950/70 border border-indigo-500/30 flex flex-col md:flex-row md:items-center justify-between gap-3">
                  <div>
                    <div className="text-xs font-mono text-indigo-400 uppercase">
                      Pin {selectedPin.num} Inspector: {selectedPin.name}
                    </div>
                    <div className="text-sm font-semibold text-white mt-0.5">{selectedPin.desc}</div>
                    <div className="text-xs text-slate-400 mt-1">
                      Type: <span className="text-slate-200 font-mono">{selectedPin.type}</span> | 5V Tolerant:{" "}
                      <span className={selectedPin.ft ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                        {selectedPin.ft ? "YES (5.5V Safe)" : "NO (3.3V Max)"}
                      </span>
                    </div>
                  </div>
                  <div className="text-xs font-mono text-slate-400 bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                    Max Current: ±25 mA | Pull-up: 40 kΩ
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Feature 269: Memory Map & Bit-Band Calculator */}
          <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  Feature 269: ARM Cortex-M Memory Map & Atomic Bit-Band Engine
                </h3>
                <p className="text-xs text-slate-400">
                  Maps 1-bit operations to full 32-bit word addresses to enable single-cycle atomic read-modify-write without disabling interrupts.
                </p>
              </div>
              <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 px-3 py-1 rounded-full border border-cyan-800">
                Formula: Alias = Base + (Offset × 32) + (Bit × 4)
              </span>
            </div>

            {/* Visual Memory Blocks */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3">
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/60">
                <div className="text-[10px] font-mono text-indigo-400">0x0800 0000 - 0x0807 FFFF</div>
                <div className="text-xs font-bold text-white mt-1">Flash Memory</div>
                <div className="text-[11px] text-slate-400">512 KB Code Space</div>
              </div>
              <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-800/40">
                <div className="text-[10px] font-mono text-emerald-400">0x2000 0000 - 0x2001 BFFF</div>
                <div className="text-xs font-bold text-emerald-200 mt-1">SRAM1 / SRAM2</div>
                <div className="text-[11px] text-slate-400">Bit-band Region 1MB</div>
              </div>
              <div className="p-3 rounded-xl bg-cyan-950/30 border border-cyan-800/40">
                <div className="text-[10px] font-mono text-cyan-400">0x2200 0000 - 0x23FF FFFF</div>
                <div className="text-xs font-bold text-cyan-200 mt-1">SRAM Bit-Band Alias</div>
                <div className="text-[11px] text-slate-400">32MB Alias Space</div>
              </div>
              <div className="p-3 rounded-xl bg-amber-950/30 border border-amber-800/40">
                <div className="text-[10px] font-mono text-amber-400">0x4000 0000 - 0x5000 0000</div>
                <div className="text-xs font-bold text-amber-200 mt-1">Peripherals (APB/AHB)</div>
                <div className="text-[11px] text-slate-400">GPIO, Timers, SPI, I2C</div>
              </div>
              <div className="p-3 rounded-xl bg-violet-950/30 border border-violet-800/40">
                <div className="text-[10px] font-mono text-violet-400">0xE000 E000 - 0xE00F FFFF</div>
                <div className="text-xs font-bold text-violet-200 mt-1">System Control (PPB)</div>
                <div className="text-[11px] text-slate-400">NVIC, SysTick, SCB</div>
              </div>
            </div>

            {/* Interactive Calculator */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
              <div className="space-y-2">
                <label className="text-xs font-mono text-slate-300">Target Memory Region:</label>
                <select
                  value={bitbandRegion}
                  onChange={e => {
                    setBitbandRegion(e.target.value);
                    setBitbandAddressHex(e.target.value === "SRAM" ? "20000004" : "40020014");
                  }}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                >
                  <option value="SRAM">SRAM (Base: 0x20000000 | Alias: 0x22000000)</option>
                  <option value="PERIPHERAL">Peripherals (Base: 0x40000000 | Alias: 0x42000000)</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-mono text-slate-300">Byte Address (Hex):</label>
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-mono text-slate-500">0x</span>
                  <input
                    type="text"
                    value={bitbandAddressHex}
                    onChange={e => setBitbandAddressHex(e.target.value.replace(/[^0-9a-fA-F]/g, ''))}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono uppercase"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-mono text-slate-300">Target Bit Index (0 to 7): {bitbandBit}</label>
                <input
                  type="range"
                  min="0"
                  max="7"
                  value={bitbandBit}
                  onChange={e => setBitbandBit(parseInt(e.target.value))}
                  className="w-full accent-indigo-500"
                />
              </div>
            </div>

            {/* Bit-band Output */}
            {bitbandResult && (
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div className="space-y-1">
                  <div className="text-[11px] font-mono text-slate-400">
                    Calculated Alias Word Address:
                  </div>
                  <div className="text-lg font-mono font-extrabold text-cyan-300">
                    {bitbandResult.aliasHex}
                  </div>
                  <div className="text-xs text-slate-400 font-mono">
                    Byte Offset: {bitbandResult.byteOffset} bytes | Bit: {bitbandBit}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <code className="text-xs font-mono bg-slate-900 px-3 py-2 rounded-lg border border-slate-700 text-emerald-400">
                    {bitbandResult.cMacro}
                  </code>
                  <button
                    onClick={() => handleCopy(bitbandResult.cMacro, 'bitband')}
                    className="px-3 py-2 text-xs font-mono rounded-lg bg-indigo-600/30 text-indigo-300 border border-indigo-500/50 hover:bg-indigo-600 hover:text-white transition-all"
                  >
                    {copiedKey === 'bitband' ? 'Copied!' : 'Copy'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: GPIO Configuration & Register Tool (Feature 262)                   */}
      {/* ========================================================================= */}
      {activeTab === "gpio_tool" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Control Form */}
            <div className="lg:col-span-1 p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-indigo-400">
                GPIO Pin Configuration
              </h3>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">Target Pin: PA{gpioPin}</label>
                <input
                  type="range"
                  min="0"
                  max="15"
                  value={gpioPin}
                  onChange={e => setGpioPin(parseInt(e.target.value))}
                  className="w-full accent-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">Pin Mode (MODER):</label>
                <select
                  value={gpioMode}
                  onChange={e => setGpioMode(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                >
                  <option value="INPUT">Input Mode (00b)</option>
                  <option value="OUTPUT">General Purpose Output (01b)</option>
                  <option value="AF">Alternate Function (10b)</option>
                  <option value="ANALOG">Analog Mode (11b)</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">Output Type (OTYPER):</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => setGpioOtype("PUSH_PULL")}
                    className={`py-1.5 text-xs font-medium rounded-lg border transition-all ${
                      gpioOtype === "PUSH_PULL"
                        ? 'bg-indigo-600 text-white border-indigo-400'
                        : 'bg-slate-800 text-slate-400 border-slate-700'
                    }`}
                  >
                    Push-Pull (0)
                  </button>
                  <button
                    onClick={() => setGpioOtype("OPEN_DRAIN")}
                    className={`py-1.5 text-xs font-medium rounded-lg border transition-all ${
                      gpioOtype === "OPEN_DRAIN"
                        ? 'bg-indigo-600 text-white border-indigo-400'
                        : 'bg-slate-800 text-slate-400 border-slate-700'
                    }`}
                  >
                    Open-Drain (1)
                  </button>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">Output Speed (OSPEEDR):</label>
                <select
                  value={gpioSpeed}
                  onChange={e => setGpioSpeed(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                >
                  <option value="LOW">Low Speed - 2 MHz (00b)</option>
                  <option value="MEDIUM">Medium Speed - 25 MHz (01b)</option>
                  <option value="HIGH">Fast / High Speed - 50 MHz (10b)</option>
                  <option value="VERY_HIGH">High Speed - 100 MHz (11b)</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">Pull-up/Pull-down (PUPDR):</label>
                <select
                  value={gpioPupd}
                  onChange={e => setGpioPupd(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                >
                  <option value="NO_PULL">Floating / No Pull (00b)</option>
                  <option value="PULL_UP">Internal Pull-Up (01b)</option>
                  <option value="PULL_DOWN">Internal Pull-Down (10b)</option>
                </select>
              </div>

              {gpioMode === "AF" && (
                <div className="space-y-1.5">
                  <label className="text-xs font-mono text-amber-300">Alternate Function AF0..AF15: {gpioAf}</label>
                  <input
                    type="range"
                    min="0"
                    max="15"
                    value={gpioAf}
                    onChange={e => setGpioAf(parseInt(e.target.value))}
                    className="w-full accent-amber-500"
                  />
                  <div className="text-[10px] text-slate-400 font-mono">
                    e.g. AF7 = USART1/2, AF5 = SPI1/2, AF4 = I2C1..3
                  </div>
                </div>
              )}
            </div>

            {/* Register Hex Output & CMSIS Code */}
            <div className="lg:col-span-2 p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-5">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white">
                  Cortex-M GPIO Register Hexadecimal Bitmasks
                </h3>
                <span className="text-xs font-mono text-indigo-400">Port A Pin {gpioPin}</span>
              </div>

              {/* 4 Register Metric Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">MODER Mask</div>
                  <div className="text-sm font-mono font-bold text-cyan-300 mt-1">{gpioResult.moderHex}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Bits [{gpioPin * 2 + 1}:{gpioPin * 2}]</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">OTYPER Mask</div>
                  <div className="text-sm font-mono font-bold text-emerald-300 mt-1">{gpioResult.otyperHex}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Bit [{gpioPin}]</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">OSPEEDR Mask</div>
                  <div className="text-sm font-mono font-bold text-amber-300 mt-1">{gpioResult.ospeedrHex}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Bits [{gpioPin * 2 + 1}:{gpioPin * 2}]</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">PUPDR Mask</div>
                  <div className="text-sm font-mono font-bold text-purple-300 mt-1">{gpioResult.pupdrHex}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Bits [{gpioPin * 2 + 1}:{gpioPin * 2}]</div>
                </div>
              </div>

              {/* Circuit Driver SVG: Push-pull vs Open-drain */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-slate-300">
                    Output Stage Schematic: {gpioOtype === "PUSH_PULL" ? "Push-Pull Totem-Pole Driver" : "Open-Drain Low-Side Driver"}
                  </span>
                  <span className="text-[11px] text-slate-400">
                    {gpioOtype === "PUSH_PULL" ? "Drives HIGH & LOW actively" : "Requires External Pull-up for HIGH"}
                  </span>
                </div>
                <svg viewBox="0 0 600 120" className="w-full h-28 bg-slate-900 rounded-lg">
                  {gpioOtype === "PUSH_PULL" ? (
                    <g>
                      {/* VDD rail */}
                      <line x1="50" y1="20" x2="250" y2="20" stroke="#6366f1" strokeWidth="2" />
                      <text x="50" y="15" fill="#a5b4fc" fontSize="10" fontFamily="monospace">+3.3V (VDD)</text>
                      {/* PMOS Transistor */}
                      <rect x="180" y="25" width="40" height="25" fill="#312e81" stroke="#818cf8" strokeWidth="1.5" rx="3" />
                      <text x="185" y="41" fill="#e0e7ff" fontSize="9" fontFamily="monospace">P-MOS</text>
                      <line x1="200" y1="20" x2="200" y2="25" stroke="#818cf8" strokeWidth="2" />
                      <line x1="200" y1="50" x2="200" y2="65" stroke="#818cf8" strokeWidth="2" />
                      {/* Output Node */}
                      <circle cx="200" cy="65" r="4" fill="#38bdf8" />
                      <line x1="200" y1="65" x2="450" y2="65" stroke="#38bdf8" strokeWidth="2.5" />
                      <text x="460" y="69" fill="#38bdf8" fontSize="11" fontFamily="monospace" fontWeight="bold">Pin PA{gpioPin}</text>
                      {/* NMOS Transistor */}
                      <line x1="200" y1="65" x2="200" y2="80" stroke="#818cf8" strokeWidth="2" />
                      <rect x="180" y="80" width="40" height="25" fill="#1e1b4b" stroke="#818cf8" strokeWidth="1.5" rx="3" />
                      <text x="185" y="96" fill="#e0e7ff" fontSize="9" fontFamily="monospace">N-MOS</text>
                      {/* GND rail */}
                      <line x1="200" y1="105" x2="200" y2="115" stroke="#818cf8" strokeWidth="2" />
                      <line x1="180" y1="115" x2="220" y2="115" stroke="#64748b" strokeWidth="2" />
                      <text x="225" y="117" fill="#94a3b8" fontSize="9" fontFamily="monospace">GND</text>
                    </g>
                  ) : (
                    <g>
                      {/* Open-drain with Pullup */}
                      <line x1="50" y1="20" x2="250" y2="20" stroke="#f59e0b" strokeWidth="2" />
                      <text x="50" y="15" fill="#fcd34d" fontSize="10" fontFamily="monospace">+3.3V (VDD)</text>
                      {/* Pullup Resistor */}
                      <rect x="188" y="25" width="24" height="30" fill="#78350f" stroke="#f59e0b" strokeWidth="1.5" />
                      <text x="192" y="43" fill="#fde68a" fontSize="8" fontFamily="monospace">R_pu</text>
                      <line x1="200" y1="20" x2="200" y2="25" stroke="#f59e0b" strokeWidth="2" />
                      <line x1="200" y1="55" x2="200" y2="65" stroke="#f59e0b" strokeWidth="2" />
                      {/* Output Node */}
                      <circle cx="200" cy="65" r="4" fill="#38bdf8" />
                      <line x1="200" y1="65" x2="450" y2="65" stroke="#38bdf8" strokeWidth="2.5" />
                      <text x="460" y="69" fill="#38bdf8" fontSize="11" fontFamily="monospace" fontWeight="bold">Pin PA{gpioPin} (I2C/Bus)</text>
                      {/* Low side NMOS */}
                      <line x1="200" y1="65" x2="200" y2="80" stroke="#818cf8" strokeWidth="2" />
                      <rect x="180" y="80" width="40" height="25" fill="#1e1b4b" stroke="#818cf8" strokeWidth="1.5" rx="3" />
                      <text x="185" y="96" fill="#e0e7ff" fontSize="9" fontFamily="monospace">N-MOS</text>
                      <line x1="200" y1="105" x2="200" y2="115" stroke="#818cf8" strokeWidth="2" />
                      <line x1="180" y1="115" x2="220" y2="115" stroke="#64748b" strokeWidth="2" />
                      <text x="225" y="117" fill="#94a3b8" fontSize="9" fontFamily="monospace">GND</text>
                    </g>
                  )}
                </svg>
              </div>

              {/* Generated C Code */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-300">CMSIS Register Configuration:</span>
                  <button
                    onClick={() => {
                      const code = `/* Configure Pin PA${gpioPin} */\nGPIOA->MODER   &= ~(3U << (${gpioPin} * 2));\nGPIOA->MODER   |=  (${gpioMode === 'INPUT' ? 0 : gpioMode === 'OUTPUT' ? 1 : gpioMode === 'AF' ? 2 : 3}U << (${gpioPin} * 2));\nGPIOA->OTYPER  &= ~(1U << ${gpioPin});\nGPIOA->OTYPER  |=  (${gpioOtype === 'PUSH_PULL' ? 0 : 1}U << ${gpioPin});\nGPIOA->OSPEEDR &= ~(3U << (${gpioPin} * 2));\nGPIOA->OSPEEDR |=  (${gpioSpeed === 'LOW' ? 0 : gpioSpeed === 'MEDIUM' ? 1 : gpioSpeed === 'HIGH' ? 2 : 3}U << (${gpioPin} * 2));\nGPIOA->PUPDR   &= ~(3U << (${gpioPin} * 2));\nGPIOA->PUPDR   |=  (${gpioPupd === 'NO_PULL' ? 0 : gpioPupd === 'PULL_UP' ? 1 : 2}U << (${gpioPin} * 2));`;
                      handleCopy(code, 'gpio_code');
                    }}
                    className="px-2.5 py-1 text-xs font-mono rounded bg-slate-800 text-indigo-300 hover:text-white border border-slate-700"
                  >
                    {copiedKey === 'gpio_code' ? 'Copied!' : 'Copy Code'}
                  </button>
                </div>
                <pre className="p-3 rounded-xl bg-slate-950 font-mono text-xs text-emerald-400 overflow-x-auto border border-slate-800">
{`/* Configure Pin PA${gpioPin} */
GPIOA->MODER   &= ~(3U << (${gpioPin} * 2));
GPIOA->MODER   |=  (${gpioMode === 'INPUT' ? 0 : gpioMode === 'OUTPUT' ? 1 : gpioMode === 'AF' ? 2 : 3}U << (${gpioPin} * 2));
GPIOA->OTYPER  &= ~(1U << ${gpioPin});
GPIOA->OTYPER  |=  (${gpioOtype === 'PUSH_PULL' ? 0 : 1}U << ${gpioPin});
GPIOA->OSPEEDR &= ~(3U << (${gpioPin} * 2));
GPIOA->OSPEEDR |=  (${gpioSpeed === 'LOW' ? 0 : gpioSpeed === 'MEDIUM' ? 1 : gpioSpeed === 'HIGH' ? 2 : 3}U << (${gpioPin} * 2));
GPIOA->PUPDR   &= ~(3U << (${gpioPin} * 2));
GPIOA->PUPDR   |=  (${gpioPupd === 'NO_PULL' ? 0 : gpioPupd === 'PULL_UP' ? 1 : 2}U << (${gpioPin} * 2));`}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: Serial Communication Protocols (Features 263, 264, 265)             */}
      {/* ========================================================================= */}
      {activeTab === "serial_buses" && (
        <div className="space-y-6">
          {/* Subtabs for UART / SPI / I2C */}
          <div className="flex gap-2">
            {[
              { id: "UART", label: "Feature 263: UART Visualizer" },
              { id: "SPI", label: "Feature 264: SPI Diagram Explorer" },
              { id: "I2C", label: "Feature 265: I²C Transaction & Resistors" }
            ].map(st => (
              <button
                key={st.id}
                onClick={() => setSerialSubtab(st.id)}
                className={`px-4 py-2 rounded-xl text-xs font-semibold tracking-wide transition-all ${
                  serialSubtab === st.id
                    ? 'bg-indigo-600 text-white shadow-md border border-indigo-400/40'
                    : 'bg-slate-800 text-slate-400 hover:text-white border border-slate-700'
                }`}
              >
                {st.label}
              </button>
            ))}
          </div>

          {/* UART Visualizer */}
          {serialSubtab === "UART" && (
            <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-mono text-slate-300">Clock f_CK (MHz): {uartClockMhz} MHz</label>
                  <select
                    value={uartClockMhz}
                    onChange={e => setUartClockMhz(parseFloat(e.target.value))}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                  >
                    <option value={16}>16 MHz (AVR / APB1 standard)</option>
                    <option value={42}>42 MHz (STM32 APB1 max)</option>
                    <option value={84}>84 MHz (STM32 APB2 max)</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-mono text-slate-300">Baud Rate:</label>
                  <select
                    value={uartBaud}
                    onChange={e => setUartBaud(parseInt(e.target.value))}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                  >
                    <option value={9600}>9600 Baud</option>
                    <option value={19200}>19200 Baud</option>
                    <option value={38400}>38400 Baud</option>
                    <option value={57600}>57600 Baud</option>
                    <option value={115200}>115200 Baud (Standard)</option>
                    <option value={230400}>230400 Baud</option>
                    <option value={921600}>921600 Baud</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-mono text-slate-300">Oversampling (OVER8):</label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => setUartOver8(0)}
                      className={`py-1.5 text-xs font-medium rounded-lg border ${
                        uartOver8 === 0 ? 'bg-indigo-600 text-white border-indigo-400' : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}
                    >
                      16x (Standard)
                    </button>
                    <button
                      onClick={() => setUartOver8(1)}
                      className={`py-1.5 text-xs font-medium rounded-lg border ${
                        uartOver8 === 1 ? 'bg-indigo-600 text-white border-indigo-400' : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}
                    >
                      8x (High Speed)
                    </button>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-mono text-slate-300">Transmit ASCII Char:</label>
                  <input
                    type="text"
                    maxLength={1}
                    value={uartChar}
                    onChange={e => setUartChar(e.target.value || "A")}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono text-center font-bold"
                  />
                </div>
              </div>

              {/* UART Results Metrics */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">USART_BRR Hex</div>
                  <div className="text-base font-extrabold text-cyan-300 mt-1">{uartResult.brrHex}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">M={uartResult.mantissa}, F={uartResult.fraction}</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Actual Baud</div>
                  <div className="text-base font-extrabold text-white mt-1">{uartResult.actualBaud}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Achieved rate</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Baud Error %</div>
                  <div className={`text-base font-extrabold mt-1 ${parseFloat(uartResult.errorPct) < 2.0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {uartResult.errorPct}%
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Tolerance &lt; 2.5%</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Bit Duration</div>
                  <div className="text-base font-extrabold text-purple-300 mt-1">{uartResult.bitUs} µs</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">1 bit time</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">8N1 Frame Time</div>
                  <div className="text-base font-extrabold text-amber-300 mt-1">{uartResult.frameUs} µs</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">10 bits total</div>
                </div>
              </div>

              {/* UART 8N1 Waveform SVG */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                  <span>8N1 Frame Waveform for '{uartChar}' ({uartResult.hexChar})</span>
                  <span>LSB First (D0 → D7)</span>
                </div>
                <svg viewBox="0 0 660 110" className="w-full h-24 bg-slate-900 rounded-lg">
                  {/* Grid lines for 10 bits */}
                  {[...Array(11)].map((_, i) => (
                    <line key={i} x1={30 + i * 55} y1="10" x2={30 + i * 55} y2="90" stroke="#334155" strokeDasharray="2,2" strokeWidth="1" />
                  ))}

                  {/* Waveform line */}
                  <path
                    d={`
                      M 10 30 L 30 30 
                      L 30 80 L 85 80
                      ${uartResult.dataBits.map((b, idx) => {
                        const xStart = 85 + idx * 55;
                        const xEnd = xStart + 55;
                        const y = b === 1 ? 30 : 80;
                        return `L ${xStart} ${y} L ${xEnd} ${y}`;
                      }).join(' ')}
                      L 525 30 L 580 30 L 640 30
                    `}
                    fill="none"
                    stroke="#10b981"
                    strokeWidth="2.5"
                  />

                  {/* Labels */}
                  <text x="45" y="100" fill="#94a3b8" fontSize="10" fontFamily="monospace">START</text>
                  {uartResult.dataBits.map((b, i) => (
                    <text key={i} x={105 + i * 55} y="100" fill="#cbd5e1" fontSize="10" fontFamily="monospace">
                      D{i}:{b}
                    </text>
                  ))}
                  <text x="540" y="100" fill="#94a3b8" fontSize="10" fontFamily="monospace">STOP</text>
                  <text x="12" y="34" fill="#64748b" fontSize="9" fontFamily="monospace">1 (HIGH)</text>
                  <text x="12" y="84" fill="#64748b" fontSize="9" fontFamily="monospace">0 (LOW)</text>
                </svg>
              </div>
            </div>
          )}

          {/* SPI Diagram Explorer */}
          {serialSubtab === "SPI" && (
            <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-mono text-slate-300">PCLK Clock: {spiClockMhz} MHz</label>
                  <select
                    value={spiClockMhz}
                    onChange={e => setSpiClockMhz(parseFloat(e.target.value))}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                  >
                    <option value={42}>42 MHz (APB1 Clock)</option>
                    <option value={84}>84 MHz (APB2 Clock)</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-mono text-slate-300">Clock Prescaler:</label>
                  <select
                    value={spiPrescaler}
                    onChange={e => setSpiPrescaler(parseInt(e.target.value))}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                  >
                    {[2, 4, 8, 16, 32, 64, 128, 256].map(p => (
                      <option key={p} value={p}>Div by {p} ({((spiClockMhz / p)).toFixed(2)} MHz)</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-mono text-slate-300">Clock Polarity (CPOL):</label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => setSpiCpol(0)}
                      className={`py-1.5 text-xs font-medium rounded-lg border ${
                        spiCpol === 0 ? 'bg-indigo-600 text-white border-indigo-400' : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}
                    >
                      CPOL=0 (Idle Low)
                    </button>
                    <button
                      onClick={() => setSpiCpol(1)}
                      className={`py-1.5 text-xs font-medium rounded-lg border ${
                        spiCpol === 1 ? 'bg-indigo-600 text-white border-indigo-400' : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}
                    >
                      CPOL=1 (Idle High)
                    </button>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-mono text-slate-300">Clock Phase (CPHA):</label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => setSpiCpha(0)}
                      className={`py-1.5 text-xs font-medium rounded-lg border ${
                        spiCpha === 0 ? 'bg-indigo-600 text-white border-indigo-400' : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}
                    >
                      CPHA=0 (1st Edge)
                    </button>
                    <button
                      onClick={() => setSpiCpha(1)}
                      className={`py-1.5 text-xs font-medium rounded-lg border ${
                        spiCpha === 1 ? 'bg-indigo-600 text-white border-indigo-400' : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}
                    >
                      CPHA=1 (2nd Edge)
                    </button>
                  </div>
                </div>
              </div>

              {/* SPI Mode Metrics */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Selected Mode</div>
                  <div className="text-base font-extrabold text-cyan-300 mt-1">SPI Mode {spiResult.mode}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">CPOL={spiCpol}, CPHA={spiCpha}</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">SCK Clock Freq</div>
                  <div className="text-base font-extrabold text-emerald-400 mt-1">{spiResult.sckFreqMhz} MHz</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Period = {spiResult.sckPeriodUs} µs</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Byte Transfer Time</div>
                  <div className="text-base font-extrabold text-purple-300 mt-1">{spiResult.byteUs} µs</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">8 clock pulses</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Max Throughput</div>
                  <div className="text-base font-extrabold text-amber-400 mt-1">{spiResult.throughputKbps} KB/s</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Theoretical limit</div>
                </div>
              </div>

              {/* SPI 4-Wire Timing Diagram SVG */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                  <span>SPI 4-Wire Bus Protocol (Mode {spiResult.mode})</span>
                  <span>Active Low CS</span>
                </div>
                <svg viewBox="0 0 650 140" className="w-full h-32 bg-slate-900 rounded-lg">
                  {/* CS Line */}
                  <text x="15" y="25" fill="#f43f5e" fontSize="10" fontFamily="monospace">/CS</text>
                  <path d="M 50 15 L 90 15 L 95 30 L 580 30 L 585 15 L 630 15" fill="none" stroke="#f43f5e" strokeWidth="2" />

                  {/* SCK Line */}
                  <text x="15" y="60" fill="#38bdf8" fontSize="10" fontFamily="monospace">SCK</text>
                  <path
                    d={`
                      M 50 ${spiCpol === 0 ? 65 : 45} 
                      L 100 ${spiCpol === 0 ? 65 : 45}
                      ${[...Array(8)].map((_, i) => {
                        const x = 110 + i * 55;
                        return spiCpol === 0
                          ? `L ${x} 45 L ${x + 25} 45 L ${x + 25} 65 L ${x + 50} 65`
                          : `L ${x} 65 L ${x + 25} 65 L ${x + 25} 45 L ${x + 50} 45`;
                      }).join(' ')}
                      L 580 ${spiCpol === 0 ? 65 : 45} L 630 ${spiCpol === 0 ? 65 : 45}
                    `}
                    fill="none"
                    stroke="#38bdf8"
                    strokeWidth="2"
                  />

                  {/* MOSI Line */}
                  <text x="15" y="95" fill="#10b981" fontSize="10" fontFamily="monospace">MOSI</text>
                  <path
                    d="M 50 90 L 100 90 L 110 80 L 160 80 L 165 100 L 220 100 L 225 80 L 275 80 L 280 100 L 330 100 L 335 80 L 550 80 L 630 90"
                    fill="none"
                    stroke="#10b981"
                    strokeWidth="2"
                  />
                  <text x="130" y="93" fill="#a7f3d0" fontSize="8" fontFamily="monospace">Bit 7</text>
                  <text x="185" y="93" fill="#a7f3d0" fontSize="8" fontFamily="monospace">Bit 6</text>
                  <text x="240" y="93" fill="#a7f3d0" fontSize="8" fontFamily="monospace">Bit 5</text>

                  {/* MISO Line */}
                  <text x="15" y="125" fill="#a855f7" fontSize="10" fontFamily="monospace">MISO</text>
                  <path
                    d="M 50 120 L 100 120 L 110 130 L 160 130 L 165 110 L 220 110 L 225 130 L 550 130 L 630 120"
                    fill="none"
                    stroke="#a855f7"
                    strokeWidth="2"
                  />
                </svg>
              </div>
            </div>
          )}

          {/* I2C Transaction & Pull-up Math */}
          {serialSubtab === "I2C" && (
            <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-mono text-slate-300">7-bit Slave Address (Hex):</label>
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-mono text-slate-500">0x</span>
                    <input
                      type="text"
                      maxLength={2}
                      value={i2cAddrHex}
                      onChange={e => setI2cAddrHex(e.target.value.replace(/[^0-9a-fA-F]/g, ''))}
                      className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono uppercase"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-mono text-slate-300">Bus Speed Mode:</label>
                  <select
                    value={i2cSpeed}
                    onChange={e => setI2cSpeed(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                  >
                    <option value="STANDARD">Standard Mode (100 kHz)</option>
                    <option value="FAST">Fast Mode (400 kHz)</option>
                    <option value="FAST_PLUS">Fast Mode Plus (1.0 MHz)</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-mono text-slate-300">Bus Capacitance (Cb): {i2cCapPf} pF</label>
                  <input
                    type="range"
                    min="20"
                    max="400"
                    step="10"
                    value={i2cCapPf}
                    onChange={e => setI2cCapPf(parseInt(e.target.value))}
                    className="w-full accent-indigo-500"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-mono text-slate-300">Bus Voltage (VDD):</label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => setI2cVdd(3.3)}
                      className={`py-1.5 text-xs font-medium rounded-lg border ${
                        i2cVdd === 3.3 ? 'bg-indigo-600 text-white border-indigo-400' : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}
                    >
                      3.3V System
                    </button>
                    <button
                      onClick={() => setI2cVdd(5.0)}
                      className={`py-1.5 text-xs font-medium rounded-lg border ${
                        i2cVdd === 5.0 ? 'bg-indigo-600 text-white border-indigo-400' : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}
                    >
                      5.0V System
                    </button>
                  </div>
                </div>
              </div>

              {/* I2C Address Breakdown & Pull-up Math Results */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Write Address (R/W=0)</div>
                  <div className="text-base font-extrabold text-cyan-300 mt-1">{i2cResult.writeHex}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">(Addr &lt;&lt; 1) | 0</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Read Address (R/W=1)</div>
                  <div className="text-base font-extrabold text-purple-300 mt-1">{i2cResult.readHex}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">(Addr &lt;&lt; 1) | 1</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Pull-up Window (Rp)</div>
                  <div className="text-base font-extrabold text-amber-300 mt-1">
                    {i2cResult.rpMin}Ω – {i2cResult.rpMax}Ω
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Min (VOL) to Max (Rise Time)</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Recommended Rp</div>
                  <div className="text-base font-extrabold text-emerald-400 mt-1">
                    ~{(i2cResult.rpRec / 1000).toFixed(1)} kΩ
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Geometric mean sizing</div>
                </div>
              </div>

              {/* I2C Protocol Frame SVG (START -> 7-bit -> R/W -> ACK -> DATA -> STOP) */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <div className="text-xs font-mono text-slate-400">
                  I²C Bus Transaction Frame (START → Address → ACK → STOP)
                </div>
                <svg viewBox="0 0 650 90" className="w-full h-20 bg-slate-900 rounded-lg">
                  {/* SCL Clock line */}
                  <text x="15" y="30" fill="#38bdf8" fontSize="10" fontFamily="monospace">SCL</text>
                  <path
                    d="M 50 35 L 80 35 L 85 20 L 105 20 L 110 35 L 130 35 L 135 20 L 155 20 L 160 35 L 560 35 L 565 20 L 590 20 L 595 35 L 630 35"
                    fill="none"
                    stroke="#38bdf8"
                    strokeWidth="2"
                  />
                  {/* SDA Data line with START and STOP conditions */}
                  <text x="15" y="65" fill="#10b981" fontSize="10" fontFamily="monospace">SDA</text>
                  <path
                    d="M 50 55 L 75 55 L 75 75 L 120 75 L 125 55 L 200 55 L 205 75 L 550 75 L 575 75 L 575 55 L 630 55"
                    fill="none"
                    stroke="#10b981"
                    strokeWidth="2"
                  />
                  {/* Annotation labels */}
                  <text x="65" y="85" fill="#f59e0b" fontSize="9" fontFamily="monospace">START</text>
                  <text x="140" y="85" fill="#cbd5e1" fontSize="9" fontFamily="monospace">7-bit ADDR</text>
                  <text x="250" y="85" fill="#38bdf8" fontSize="9" fontFamily="monospace">R/W</text>
                  <text x="310" y="85" fill="#a7f3d0" fontSize="9" fontFamily="monospace">ACK (0)</text>
                  <text x="400" y="85" fill="#cbd5e1" fontSize="9" fontFamily="monospace">8-bit DATA</text>
                  <text x="565" y="85" fill="#f43f5e" fontSize="9" fontFamily="monospace">STOP</text>
                </svg>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: Interrupts & Hardware Timers (Features 266 & 267)                   */}
      {/* ========================================================================= */}
      {activeTab === "nvic_timers" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Feature 266: NVIC Simulator */}
            <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white">
                  Feature 266: ARM Cortex-M NVIC Interrupt Priority & Latency
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  AIRCR PRIGROUP splits 4-bit priority into Preemption Priority and Subpriority.
                </p>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">
                  Priority Grouping (PRIGROUP): Group {nvicPrigroup}
                </label>
                <select
                  value={nvicPrigroup}
                  onChange={e => setNvicPrigroup(parseInt(e.target.value))}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                >
                  <option value={0}>Group 0: 4-bit Preempt (16 levels), 0-bit Sub (0 levels)</option>
                  <option value={1}>Group 1: 3-bit Preempt (8 levels), 1-bit Sub (2 levels)</option>
                  <option value={2}>Group 2: 2-bit Preempt (4 levels), 2-bit Sub (4 levels)</option>
                  <option value={3}>Group 3: 1-bit Preempt (2 levels), 3-bit Sub (8 levels)</option>
                  <option value={4}>Group 4: 0-bit Preempt (None), 4-bit Sub (16 levels)</option>
                </select>
              </div>

              {/* 2 IRQ comparison slots */}
              <div className="grid grid-cols-2 gap-3 pt-1">
                {/* IRQ A */}
                <div className="p-3 rounded-xl bg-slate-800/50 border border-indigo-500/30 space-y-2">
                  <div className="text-xs font-bold text-indigo-300">IRQ A: EXTI0_IRQn</div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-mono text-slate-400">Preempt Priority: {irqAPreempt}</label>
                    <input
                      type="range"
                      min="0"
                      max={nvicResult.maxPreempt}
                      value={irqAPreempt}
                      onChange={e => setIrqAPreempt(parseInt(e.target.value))}
                      className="w-full accent-indigo-500"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-mono text-slate-400">Subpriority: {irqASub}</label>
                    <input
                      type="range"
                      min="0"
                      max={nvicResult.maxSub}
                      value={irqASub}
                      onChange={e => setIrqASub(parseInt(e.target.value))}
                      className="w-full accent-indigo-500"
                    />
                  </div>
                </div>

                {/* IRQ B */}
                <div className="p-3 rounded-xl bg-slate-800/50 border border-purple-500/30 space-y-2">
                  <div className="text-xs font-bold text-purple-300">IRQ B: USART1_IRQn</div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-mono text-slate-400">Preempt Priority: {irqBPreempt}</label>
                    <input
                      type="range"
                      min="0"
                      max={nvicResult.maxPreempt}
                      value={irqBPreempt}
                      onChange={e => setIrqBPreempt(parseInt(e.target.value))}
                      className="w-full accent-purple-500"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-mono text-slate-400">Subpriority: {irqBSub}</label>
                    <input
                      type="range"
                      min="0"
                      max={nvicResult.maxSub}
                      value={irqBSub}
                      onChange={e => setIrqBSub(parseInt(e.target.value))}
                      className="w-full accent-purple-500"
                    />
                  </div>
                </div>
              </div>

              {/* Verdict outcome box */}
              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                <div className="text-[10px] font-mono uppercase text-slate-400">Arbitration Outcome:</div>
                <div className={`text-xs font-mono font-bold ${nvicResult.preemptOccurred ? 'text-emerald-400' : 'text-amber-300'}`}>
                  {nvicResult.verdict}
                </div>
              </div>

              {/* Cortex-M Latency Metrics */}
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="p-2 rounded-lg bg-slate-800/40 border border-slate-700/60">
                  <div className="text-[10px] text-slate-400 font-mono">Stacking</div>
                  <div className="text-sm font-bold text-white">12 Cycles</div>
                </div>
                <div className="p-2 rounded-lg bg-slate-800/40 border border-slate-700/60">
                  <div className="text-[10px] text-slate-400 font-mono">Tail-Chaining</div>
                  <div className="text-sm font-bold text-emerald-400">6 Cycles</div>
                </div>
                <div className="p-2 rounded-lg bg-slate-800/40 border border-slate-700/60">
                  <div className="text-[10px] text-slate-400 font-mono">Late-Arriving</div>
                  <div className="text-sm font-bold text-cyan-400">0 Cycles</div>
                </div>
              </div>
            </div>

            {/* Feature 267: Timer Configuration Calculator */}
            <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white">
                  Feature 267: Timer PSC / ARR Auto-Configuration Solver
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Solves for 16-bit Prescaler and Auto-Reload values to achieve desired output frequency with 0% error.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-xs font-mono text-slate-300">Timer Clock (f_TIM):</label>
                  <select
                    value={timClockMhz}
                    onChange={e => setTimClockMhz(parseFloat(e.target.value))}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                  >
                    <option value={16}>16 MHz (AVR / ATmega)</option>
                    <option value={42}>42 MHz (STM32 APB1)</option>
                    <option value={84}>84 MHz (STM32 Black Pill)</option>
                    <option value={168}>168 MHz (STM32F407 High Speed)</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-mono text-slate-300">Target Output Freq (Hz):</label>
                  <input
                    type="number"
                    min="1"
                    max="1000000"
                    value={timTargetFreq}
                    onChange={e => setTimTargetFreq(Math.max(1, parseFloat(e.target.value) || 1))}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                  />
                </div>
              </div>

              {/* Quick Preset Buttons */}
              <div className="space-y-1">
                <span className="text-[10px] font-mono text-slate-400">ECE Standard Lab Presets:</span>
                <div className="flex flex-wrap gap-1.5">
                  {[
                    { label: "1 Hz (Blink)", freq: 1 },
                    { label: "100 Hz", freq: 100 },
                    { label: "1 kHz (SysTick)", freq: 1000 },
                    { label: "20 kHz (Motor)", freq: 20000 }
                  ].map(pr => (
                    <button
                      key={pr.label}
                      onClick={() => setTimTargetFreq(pr.freq)}
                      className="px-2.5 py-1 text-[10px] font-mono rounded bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-slate-700"
                    >
                      {pr.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Calculated Results */}
              <div className="grid grid-cols-2 gap-3 pt-2">
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Prescaler (PSC)</div>
                  <div className="text-base font-extrabold text-cyan-300 mt-1">{timResult.psc}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Divides by {timResult.psc + 1}</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Auto-Reload (ARR)</div>
                  <div className="text-base font-extrabold text-purple-300 mt-1">{timResult.arr}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Top counter value</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Actual Frequency</div>
                  <div className="text-base font-extrabold text-emerald-400 mt-1">{timResult.actualF} Hz</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Error: {timResult.errorPct}%</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Tick Resolution</div>
                  <div className="text-base font-extrabold text-amber-300 mt-1">{timResult.tickUs} µs</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Period: {timResult.periodMs} ms</div>
                </div>
              </div>

              {/* C initialization snippet */}
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-300">
                <span className="text-slate-500">/* Register Initialization */</span><br />
                TIMx-&gt;PSC = <span className="text-cyan-300">{timResult.psc}</span>;<br />
                TIMx-&gt;ARR = <span className="text-purple-300">{timResult.arr}</span>;
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 5: PWM Duty Cycle & Bare-Metal C Library (Features 268 & 270)         */}
      {/* ========================================================================= */}
      {activeTab === "pwm_code" && (
        <div className="space-y-6">
          {/* Feature 268: PWM Duty Cycle Visualizer */}
          <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white">
                  Feature 268: Hardware PWM Duty Cycle & Average Voltage Visualizer
                </h3>
                <p className="text-xs text-slate-400">
                  Interactive pulse-width modulation generator with live average voltage $V_{`avg`} = V_{`DD`} \times \text{Duty}$ calculation.
                </p>
              </div>
              <span className="text-xs font-mono text-indigo-400 bg-indigo-950/60 px-3 py-1 rounded-full border border-indigo-800">
                Formula: Duty % = (CCR / (ARR + 1)) × 100%
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">Auto-Reload Register (ARR): {pwmArr}</label>
                <input
                  type="number"
                  min="10"
                  max="65535"
                  value={pwmArr}
                  onChange={e => setPwmArr(Math.max(1, parseInt(e.target.value) || 999))}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">
                  Capture/Compare (CCR): {pwmCcr} ({pwmResult.dutyPct}%)
                </label>
                <input
                  type="range"
                  min="0"
                  max={pwmArr + 1}
                  value={pwmCcr}
                  onChange={e => setPwmCcr(parseInt(e.target.value))}
                  className="w-full accent-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">Supply Voltage (VDD): {pwmVdd}V</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => setPwmVdd(3.3)}
                    className={`py-1.5 text-xs font-medium rounded-lg border ${
                      pwmVdd === 3.3 ? 'bg-indigo-600 text-white border-indigo-400' : 'bg-slate-800 text-slate-400 border-slate-700'
                    }`}
                  >
                    3.3V
                  </button>
                  <button
                    onClick={() => setPwmVdd(5.0)}
                    className={`py-1.5 text-xs font-medium rounded-lg border ${
                      pwmVdd === 5.0 ? 'bg-indigo-600 text-white border-indigo-400' : 'bg-slate-800 text-slate-400 border-slate-700'
                    }`}
                  >
                    5.0V
                  </button>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">Alignment Mode:</label>
                <select
                  value={pwmMode}
                  onChange={e => setPwmMode(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                >
                  <option value="EDGE_ALIGNED">Edge-Aligned (Mode 1)</option>
                  <option value="CENTER_ALIGNED">Center-Aligned (Up-Down)</option>
                </select>
              </div>
            </div>

            {/* PWM Metrics */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                <div className="text-[10px] font-mono text-slate-400 uppercase">Duty Cycle</div>
                <div className="text-base font-extrabold text-cyan-300 mt-1">{pwmResult.dutyPct}%</div>
                <div className="text-[10px] text-slate-500 mt-0.5">High time ratio</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                <div className="text-[10px] font-mono text-slate-400 uppercase">Average DC Voltage</div>
                <div className="text-base font-extrabold text-emerald-400 mt-1">{pwmResult.vAvg} V</div>
                <div className="text-[10px] text-slate-500 mt-0.5">V_avg = VDD × Duty</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                <div className="text-[10px] font-mono text-slate-400 uppercase">PWM Frequency</div>
                <div className="text-base font-extrabold text-purple-300 mt-1">{pwmResult.freqHz} Hz</div>
                <div className="text-[10px] text-slate-500 mt-0.5">Period: {pwmResult.periodUs} µs</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                <div className="text-[10px] font-mono text-slate-400 uppercase">Pulse High (t_on)</div>
                <div className="text-base font-extrabold text-amber-300 mt-1">{pwmResult.tHighUs} µs</div>
                <div className="text-[10px] text-slate-500 mt-0.5">t_low = {pwmResult.tLowUs} µs</div>
              </div>
            </div>

            {/* Dynamic PWM Waveform SVG */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <span>PWM Pulse Waveform ({pwmResult.dutyPct}% Duty Cycle)</span>
                <span className="text-emerald-400 font-bold">V_avg = {pwmResult.vAvg} V</span>
              </div>
              <svg viewBox="0 0 650 110" className="w-full h-28 bg-slate-900 rounded-lg">
                {/* 2 Complete PWM Cycles */}
                {(() => {
                  const duty = parseFloat(pwmResult.dutyPct) / 100.0;
                  const cycleW = 270;
                  const onW = cycleW * duty;
                  const offW = cycleW * (1.0 - duty);
                  const yHigh = 25;
                  const yLow = 85;
                  const vAvgY = yLow - (yLow - yHigh) * duty;

                  return (
                    <g>
                      {/* V_avg dashed line */}
                      <line x1="30" y1={vAvgY} x2="620" y2={vAvgY} stroke="#10b981" strokeWidth="1.5" strokeDasharray="4,4" />
                      <text x="540" y={vAvgY - 5} fill="#a7f3d0" fontSize="9" fontFamily="monospace">
                        V_avg: {pwmResult.vAvg}V
                      </text>

                      {/* PWM Waveform Pulse 1 & 2 */}
                      <path
                        d={`
                          M 40 ${yLow}
                          L 40 ${yHigh} L ${40 + onW} ${yHigh} L ${40 + onW} ${yLow} L ${40 + cycleW} ${yLow}
                          L ${40 + cycleW} ${yHigh} L ${40 + cycleW + onW} ${yHigh} L ${40 + cycleW + onW} ${yLow} L ${40 + 2 * cycleW} ${yLow}
                        `}
                        fill="none"
                        stroke="#38bdf8"
                        strokeWidth="2.5"
                      />

                      {/* Period marker */}
                      <line x1="40" y1="98" x2={40 + cycleW} y2="98" stroke="#94a3b8" strokeWidth="1" />
                      <text x={40 + cycleW / 2 - 20} y="106" fill="#94a3b8" fontSize="9" fontFamily="monospace">
                        Period T ({pwmResult.periodUs} µs)
                      </text>
                    </g>
                  );
                })()}
              </svg>
            </div>
          </div>

          {/* Feature 270: Bare-Metal Embedded C Snippet Library */}
          <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white">
                  Feature 270: Production Bare-Metal Embedded C Code Library
                </h3>
                <p className="text-xs text-slate-400">
                  Ready-to-flash CMSIS register-level embedded C drivers with dual-language English & Tamil documentation.
                </p>
              </div>
              <button
                onClick={() => handleCopy(CODE_SNIPPETS[selectedSnippetKey].code, selectedSnippetKey)}
                className="px-3.5 py-1.5 text-xs font-mono font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-500 shadow-md transition-all self-start sm:self-auto"
              >
                {copiedKey === selectedSnippetKey ? 'Copied to Clipboard!' : 'Copy Code Snippet'}
              </button>
            </div>

            {/* Template Selector Pills */}
            <div className="flex flex-wrap gap-2">
              {Object.keys(CODE_SNIPPETS).map(key => (
                <button
                  key={key}
                  onClick={() => setSelectedSnippetKey(key)}
                  className={`px-3.5 py-2 rounded-xl text-xs font-medium transition-all ${
                    selectedSnippetKey === key
                      ? 'bg-indigo-600 text-white shadow-md border border-indigo-400'
                      : 'bg-slate-800/80 text-slate-400 hover:text-white border border-slate-700'
                  }`}
                >
                  {CODE_SNIPPETS[key].title}
                </button>
              ))}
            </div>

            {/* Snippet Header & Bilingual Commentary */}
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <span className="text-sm font-bold text-white">{CODE_SNIPPETS[selectedSnippetKey].title}</span>
                <span className="text-xs font-mono text-indigo-300">{CODE_SNIPPETS[selectedSnippetKey].mcu}</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                {CODE_SNIPPETS[selectedSnippetKey].tamilDesc}
              </p>
              {bilingual && (
                <div className="text-xs text-amber-300 font-sans pt-1 border-t border-slate-800">
                  <strong>தமிழ் விளக்கம்:</strong> {CODE_SNIPPETS[selectedSnippetKey].tamilDesc}
                </div>
              )}
            </div>

            {/* Code Block with Syntax Highlighting Look */}
            <pre className="p-4 rounded-xl bg-slate-950 font-mono text-xs text-emerald-400 overflow-x-auto border border-slate-800 max-h-96">
              {CODE_SNIPPETS[selectedSnippetKey].code}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
