"""
VoltCore Apex Academia - STM32 Academy Expansion (Phase 1 Test Suite)
Validates content collection structure, frontmatter metadata typing, register decoupling, and routing integrity.
"""

import os
import re
import pytest

STM32_CONTENT_DIR = os.path.join("src", "content", "stm32-academy")
ROUTING_DIR = os.path.join("src", "pages", "embedded-systems", "stm32-academy")


def test_stm32_academy_21_modules_exist():
    """Verify that all 21 curriculum modules exist in src/content/stm32-academy/"""
    assert os.path.isdir(STM32_CONTENT_DIR), f"Directory {STM32_CONTENT_DIR} must exist"
    files = [f for f in os.listdir(STM32_CONTENT_DIR) if f.endswith(".mdx")]
    assert len(files) == 21, f"Expected 21 MDX modules, found {len(files)}"


def test_stm32_academy_frontmatter_metadata_typing():
    """Verify strict metadata schema across all 21 module frontmatters"""
    files = sorted([f for f in os.listdir(STM32_CONTENT_DIR) if f.endswith(".mdx")])
    found_numbers = set()

    required_fields = [
        "moduleNumber:",
        "title:",
        "shortTitle:",
        "tier:",
        "difficulty:",
        "boardTargets:",
        "prerequisites:",
        "estimatedDuration:",
        "cortexArchitecture:",
        "registerFocus:",
        "description:",
        "keyFormulas:",
        "hardwareApparatus:",
        "order:",
        "xpReward:"
    ]

    for fname in files:
        fpath = os.path.join(STM32_CONTENT_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        assert content.startswith("---"), f"{fname} must start with YAML frontmatter delimiter"
        parts = content.split("---", 2)
        assert len(parts) >= 3, f"{fname} frontmatter must be closed with ---"
        frontmatter = parts[1]

        # Verify all required fields
        for field in required_fields:
            assert field in frontmatter, f"{fname} missing frontmatter field {field}"

        # Check module number
        match = re.search(r"moduleNumber:\s*(\d+)", frontmatter)
        assert match, f"{fname} must have valid integer moduleNumber"
        mod_num = int(match.group(1))
        assert 1 <= mod_num <= 21, f"{fname} moduleNumber {mod_num} out of range [1, 21]"
        found_numbers.add(mod_num)

        # Check board targets
        assert "Nucleo-F401RE" in frontmatter or "Blue Pill" in frontmatter, f"{fname} must target Nucleo or Blue Pill"

    assert len(found_numbers) == 21, f"Expected module numbers 1..21, found {sorted(found_numbers)}"


def test_stm32_academy_landing_and_reader_routes_exist():
    """Verify routing files for STM32 Academy landing and chapter dynamic reader"""
    index_route = os.path.join(ROUTING_DIR, "index.astro")
    reader_route = os.path.join(ROUTING_DIR, "[...slug].astro")
    hub_component = os.path.join("src", "components", "Stm32AcademyHub.jsx")

    assert os.path.isfile(index_route), f"Landing route {index_route} must exist"
    assert os.path.isfile(reader_route), f"Reader route {reader_route} must exist"
    assert os.path.isfile(hub_component), f"React Island {hub_component} must exist"

    # Verify getCollection('stm32-academy') is invoked
    with open(index_route, "r", encoding="utf-8") as f:
        idx_content = f.read()
    assert "stm32-academy" in idx_content, "index.astro must query 'stm32-academy' collection"

    with open(reader_route, "r", encoding="utf-8") as f:
        reader_content = f.read()
    assert "getStaticPaths" in reader_content, "[...slug].astro must define getStaticPaths"
    assert "stm32-academy" in reader_content, "[...slug].astro must query 'stm32-academy' collection"


def test_embedded_systems_hub_integration():
    """Verify STM32 Academy card with progress ring is integrated into EmbeddedSystemsHub.jsx"""
    hub_path = os.path.join("src", "components", "EmbeddedSystemsHub.jsx")
    with open(hub_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "VoltCore STM32 Bare-Metal Academy" in content or "STM32 ACADEMY" in content
    assert "stm32CompletedCount" in content
    assert "/embedded-systems/stm32-academy" in content


def test_course_config_schema_universal_embedded_spec():
    """Verify Cortex-M & STM32 register map decoupling in src/data/course_config_schema.ts"""
    schema_path = os.path.join("src", "data", "course_config_schema.ts")
    with open(schema_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "CortexMArchitectureSpec" in content
    assert "Stm32RegisterMap" in content
    assert "Stm32DeviceProfile" in content
    assert "ARM_CORTEX_SPECS" in content
    assert "STM32_DEVICE_PROFILES" in content
    assert "compareStm32Registers" in content


def test_phase2_module_01_silicon_taxonomy_and_docs():
    """Verify Phase 2 deep-dive technical content for Module 01"""
    fpath = os.path.join(STM32_CONTENT_DIR, "01-arm-cortex-m-architecture.mdx")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "STM32F401RET6" in content, "Module 01 must decode STM32F401RET6"
    assert "STM32F103C8T6" in content, "Module 01 must reference Blue Pill STM32F103C8T6"
    assert "Datasheet" in content and "Reference Manual" in content
    assert "Programming Manual" in content and "Errata Sheet" in content
    assert "Microprocessor" in content and "Microcontroller" in content


def test_phase2_module_02_advanced_embedded_c_volatile():
    """Verify Phase 2 deep-dive technical content for Module 02"""
    fpath = os.path.join(STM32_CONTENT_DIR, "02-gnu-arm-toolchain-makefiles-linker.mdx")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "volatile" in content, "Module 02 must explain the volatile qualifier"
    assert "led_init_register_level" in content
    assert "GPIOA_BSRR" in content and "GPIOA_ODR" in content
    assert "Read-Modify-Write" in content or "RMW" in content
    assert "GPIO_TypeDef" in content, "Module 02 must cover CMSIS struct-based modeling"


def test_phase2_module_03_cortex_m_registers_and_hardfault():
    """Verify Phase 2 deep-dive technical content for Module 03"""
    fpath = os.path.join(STM32_CONTENT_DIR, "03-reset-sequence-vector-table-crt0.mdx")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "MSP" in content and "PSP" in content, "Module 03 must cover dual stack architecture"
    assert "EXC_RETURN" in content, "Module 03 must detail EXC_RETURN tokens"
    assert "HardFault_Handler" in content
    assert "SCB_CFSR" in content or "CFSR" in content
    assert "Thumb" in content, "Module 03 must explain Thumb bit and instruction alignment"


def test_phase2_module_04_memory_map_and_linker_anatomy():
    """Verify Phase 2 deep-dive technical content for Module 04"""
    fpath = os.path.join(STM32_CONTENT_DIR, "04-clock-tree-rcc-pll-pwr.mdx")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "0x08000000" in content, "Module 04 must specify Flash base address"
    assert "0x20000000" in content, "Module 04 must specify SRAM base address"
    assert "AHB1" in content and "APB1" in content and "APB2" in content
    assert ".text" in content and ".data" in content and ".bss" in content
    assert "_sidata" in content and "_sdata" in content and "_sbss" in content
    assert "_estack" in content, "Module 04 must calculate top of stack"


def test_stm32_prerequisite_slug_integrity():
    """Verify that all prerequisite module slugs across all 21 MDX files resolve to existing files"""
    files = sorted([f for f in os.listdir(STM32_CONTENT_DIR) if f.endswith(".mdx")])
    slugs = {os.path.splitext(f)[0] for f in files}

    for fname in files:
        fpath = os.path.join(STM32_CONTENT_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        match = re.search(r"prerequisites:\s*\n((?:\s+-\s*['\"][^'\"]+['\"]\s*\n?)+)", content)
        if match:
            raw = match.group(1)
            items = re.findall(r"-\s*['\"]([^'\"]+)['\"]", raw)
            for item in items:
                if re.match(r"^\d{2}-", item):
                    assert item in slugs, f"Broken prerequisite slug '{item}' referenced in {fname}"


def test_phase3_module_05_gpio_architecture_f1_vs_f4():
    """Verify Phase 3 deep-dive technical content for Module 05 (GPIO & Atomic BSRR)"""
    fpath = os.path.join(STM32_CONTENT_DIR, "05-bare-metal-gpio-atomic-bit-ops.mdx")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "MODER" in content and "OTYPER" in content and "OSPEEDR" in content and "PUPDR" in content
    assert "CRL" in content and "CRH" in content, "Module 05 must contrast STM32F1 CRL/CRH"
    assert "BSRR" in content, "Module 05 must explain atomic Bit Set/Reset Register"
    assert "0x42000000" in content or "0x22000000" in content, "Module 05 must detail bit-banding memory alias"


def test_phase3_module_06_rcc_clock_tree_and_flash_wait_states():
    """Verify Phase 3 deep-dive technical content for Module 06 (RCC, PLL & Flash Latency)"""
    fpath = os.path.join(STM32_CONTENT_DIR, "06-rcc-clock-tree-pll-flash-latency.mdx")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "HSI" in content and "HSE" in content and "LSI" in content and "LSE" in content
    assert "FLASH_ACR" in content or "wait states" in content
    assert "84 MHz" in content or "84000000" in content
    assert "rcc_clock_init_84mhz_hse" in content
    assert "PWR_CR" in content or "VOS" in content


def test_phase3_module_07_nvic_priority_grouping_and_exti():
    """Verify Phase 3 deep-dive technical content for Module 07 (NVIC & EXTI)"""
    fpath = os.path.join(STM32_CONTENT_DIR, "07-nvic-interrupts-exti.mdx")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "AIRCR" in content and "PRIGROUP" in content, "Module 07 must explain priority grouping"
    assert "tail-chaining" in content or "Tail-Chaining" in content
    assert "SYSCFG" in content or "EXTICR" in content
    assert "EXTI_PR" in content and "rc_w1" in content or "write 1" in content
    assert "EXTI15_10_IRQHandler" in content


def test_phase3_module_08_timers_pwm_and_encoder_interface():
    """Verify Phase 3 deep-dive technical content for Module 08 (Timers, PWM & Encoders)"""
    fpath = os.path.join(STM32_CONTENT_DIR, "08-timers-pwm-generation.mdx")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "TIMx_PSC" in content and "TIMx_ARR" in content and "TIMx_CNT" in content
    assert "Center-Aligned" in content or "center-aligned" in content
    assert "ARPE" in content and "OC1PE" in content, "Module 08 must detail preload shadow mechanism"
    assert "Quadrature" in content or "Encoder" in content
    assert "tim2_pwm_center_aligned_init" in content


def test_phase3_module_09_sar_adc_calibration_and_dma_streaming():
    """Verify Phase 3 deep-dive technical content for Module 09 (ADC, DMA & Serial Protocols)"""
    fpath = os.path.join(STM32_CONTENT_DIR, "09-adc-sensor-calibration.mdx")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "SAR" in content or "Successive Approximation" in content
    assert "0x1FFF7A2A" in content, "Module 09 must provide VREFINT factory eFuse calibration address"
    assert "0x1FFF7A2C" in content and "0x1FFF7A2E" in content, "Module 09 must detail temperature sensor calibration constants"
    assert "DMA2" in content and "CIRC" in content, "Module 09 must cover DMA circular mode"
    assert "Ping-Pong" in content or "HTIF" in content or "TCIF" in content
    assert "USART_BRR" in content or "Baud" in content
    assert "CPOL" in content and "CPHA" in content
    assert "adc1_dma_circular_init" in content


def test_phase4_module_10_i2c_bus_and_recovery():
    """Verify Phase 4 deep-dive technical content for Module 10 (I2C Bus & Recovery)"""
    fpath = os.path.join(STM32_CONTENT_DIR, "10-i2c-bus-sensor-interfacing.mdx")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Open-Drain" in content or "open-drain" in content
    assert "Wired-AND" in content or "wired-AND" in content
    assert "R_{p(min)}" in content or "R_{pullup_min}" in content or "Rp" in content
    assert "Clock Stretching" in content or "clock stretching" in content
    assert "i2c1_bus_recovery_sequence" in content, "Module 10 must implement 9-clock bus recovery sequence"
    assert "i2c1_init_fast_mode" in content
    assert "ADDR" in content and "I2C_SR2" in content, "Module 10 must detail ADDR flag clearing"


def test_phase4_module_11_spi_full_duplex_and_flash():
    """Verify Phase 4 deep-dive technical content for Module 11 (SPI Full-Duplex & Flash)"""
    fpath = os.path.join(STM32_CONTENT_DIR, "11-spi-full-duplex-display-flash.mdx")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "CPOL" in content and "CPHA" in content
    assert "Mode 0" in content and "Mode 3" in content
    assert "SSM" in content and "SSI" in content, "Module 11 must cover Software Slave Management"
    assert "OVR" in content, "Module 11 must explain Overrun flag and clearing sequence"
    assert "W25Q64" in content, "Module 11 must cover W25Q64 NOR Flash"
    assert "0x9F" in content, "Module 11 must specify JEDEC Read ID opcode"
    assert "spi1_master_init" in content and "spi1_transfer_byte" in content
    assert "ST7789" in content and "D/CX" in content


def test_phase4_module_12_dma_controller_and_m2m():
    """Verify Phase 4 deep-dive technical content for Module 12 (DMA Streams & M2M)"""
    fpath = os.path.join(STM32_CONTENT_DIR, "12-dma-zero-copy-peripherals.mdx")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Channels" in content and "Streams" in content, "Module 12 must contrast F1 channels with F4 streams"
    assert "CHSEL" in content or "Crossbar" in content
    assert "FIFO" in content and "FTH" in content, "Module 12 must detail FIFO thresholds"
    assert "Memory-to-Memory" in content or "M2M" in content
    assert "DMA2" in content, "Module 12 must note M2M restriction to DMA2"
    assert "dma2_m2m_burst_copy" in content
    assert "DMA_SxCR" in content and "DMA_SxNDTR" in content


def test_phase4_module_13_can_bus_and_bxcan_engine():
    """Verify Phase 4 deep-dive technical content for Module 13 (CAN Bus & bxCAN)"""
    fpath = os.path.join(STM32_CONTENT_DIR, "13-can-bus-bxcan-automotive.mdx")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "CAN_H" in content and "CAN_L" in content, "Module 13 must detail differential lines"
    assert "Dominant" in content and "Recessive" in content
    assert "Arbitration" in content or "arbitration" in content
    assert "Time Quantum" in content or "T_q" in content
    assert "Sample Point" in content or "Sample point" in content
    assert "Mailbox" in content or "FIFO0" in content
    assert "CAN_BTR" in content and "INAK" in content
    assert "can1_init_500kbps" in content and "can1_transmit_frame" in content


def test_phase5_module_14_systick_and_cooperative_scheduler():
    """Verify Phase 5 deep-dive technical content for Module 14 (SysTick & Cooperative Scheduling)"""
    fpath = os.path.join(STM32_CONTENT_DIR, "14-systick-software-schedulers.mdx")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "STK_CTRL" in content and "STK_LOAD" in content and "STK_VAL" in content
    assert "24-bit" in content, "Module 14 must detail 24-bit down counter"
    assert "SysTick_Handler" in content
    assert "systick_init" in content and "systick_get_uptime_ms" in content
    assert "cooperative" in content or "Cooperative" in content
    assert "scheduler_run" in content


def test_phase5_module_15_freertos_pendsv_and_dual_stacks():
    """Verify Phase 5 deep-dive technical content for Module 15 (PendSV & Dual Stacks)"""
    fpath = os.path.join(STM32_CONTENT_DIR, "15-freertos-kernel-porting-pendsv.mdx")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "PendSV" in content or "PENDSVSET" in content
    assert "MSP" in content and "PSP" in content, "Module 15 must contrast MSP and PSP"
    assert "Handler Mode" in content and "Thread Mode" in content
    assert "PendSV_Handler" in content
    assert "pxPortInitialiseStack" in content
    assert "0x01000000" in content, "Module 15 must initialize Thumb bit in xPSR"
    assert "Tickless" in content or "TICKLESS" in content


def test_phase5_module_16_rtos_queues_and_priority_inheritance():
    """Verify Phase 5 deep-dive technical content for Module 16 (Queues & Priority Inheritance)"""
    fpath = os.path.join(STM32_CONTENT_DIR, "16-rtos-queues-mutexes-priority-inversion.mdx")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Priority Inversion" in content or "priority inversion" in content
    assert "Pathfinder" in content, "Module 16 must reference Mars Pathfinder case study"
    assert "Priority Inheritance" in content or "priority inheritance" in content
    assert "QueueHandle_t" in content and "xQueueCreate" in content
    assert "xSemaphoreCreateMutex" in content
    assert "Copy-by-Value" in content or "copy-by-value" in content


def test_phase5_module_17_real_time_schedulability_and_hardware_fpu():
    """Verify Phase 5 deep-dive technical content for Module 17 (RMS, EDF & Hardware FPU)"""
    fpath = os.path.join(STM32_CONTENT_DIR, "17-hardware-fpu-cmsis-dsp.mdx")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Rate Monotonic" in content or "RMS" in content
    assert "Liu & Layland" in content or "Liu and Layland" in content
    assert "69.3%" in content or "ln(2)" in content, "Module 17 must reference asymptotic 69.3% bound"
    assert "Response Time Analysis" in content or "RTA" in content
    assert "Earliest Deadline First" in content or "EDF" in content
    assert "SCB_CPACR" in content or "CPACR" in content
    assert "Lazy Stacking" in content or "LSPEN" in content
    assert "fpu_hardware_init" in content and "rms_is_schedulable_guaranteed" in content




