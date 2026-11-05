"""
========================================================================================
VoltCore Apex Academia - Embedded Firmware Automated Grading Engine
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/autograder_engine.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Static AST-like analysis, memory safety audit, and rubric evaluation for student-
  submitted C, C++, and FreeRTOS embedded firmware across multi-architecture MCU targets.
========================================================================================
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from backend.security_auth import OWNER_METADATA


class FirmwareAutograderEngine:
    """
    Automated grading engine enforcing Anna University ECE Regulation 2023 laboratory standards.
    Performs memory leak checks, stack overflow detection, pin conflict checks, and RTOS audits.
    """

    INPUT_ONLY_PINS = {"34", "35", "36", "39"}
    ADC2_WIFI_CONFLICT_PINS = {"0", "2", "4", "12", "13", "14", "15", "25", "26", "27"}

    def grade_firmware_submission(
        self,
        source_code: str,
        module_code: str = "EC8701",
        target_mcu: str = "esp32"
    ) -> Dict[str, Any]:
        """
        Executes comprehensive static analysis on firmware code.
        Returns detailed scoring matrix, deductions, and pedagogical remediation.
        """
        lines = source_code.split("\n")
        deductions: List[Dict[str, Any]] = []
        positive_credits: List[str] = []

        # Category scores (out of 25 each -> total 100)
        scores = {
            "memory_safety": 25,
            "concurrency_rtos": 25,
            "hardware_pins": 25,
            "code_quality": 25
        }

        # 1. Memory Leak & Allocation Audit
        malloc_count = len(re.findall(r"\b(malloc|calloc|pvPortMalloc)\s*\(", source_code))
        free_count = len(re.findall(r"\b(free|vPortFree)\s*\(", source_code))

        if malloc_count > free_count:
            diff = malloc_count - free_count
            deduction = min(20, diff * 10)
            scores["memory_safety"] -= deduction
            deductions.append({
                "category": "memory_safety",
                "severity": "CRITICAL",
                "issue": f"Potential Heap Memory Leak: {malloc_count} dynamic allocation(s) found but only {free_count} deallocation(s).",
                "penalty": deduction,
                "remedy": "Ensure every malloc/pvPortMalloc has a corresponding free/vPortFree in all execution paths."
            })
        elif malloc_count > 0 and malloc_count == free_count:
            positive_credits.append("Clean Heap Memory Balance: All dynamic allocations properly paired with free/vPortFree.")

        # 2. Stack Overflow Hazards (Large buffers allocated locally inside functions)
        large_buffer_pattern = re.compile(r"\b(uint8_t|char|int|float)\s+([a-zA-Z0-9_]+)\[\s*(\d{4,})\s*\];")
        for idx, line in enumerate(lines, 1):
            match = large_buffer_pattern.search(line)
            if match:
                buf_type, buf_name, size = match.groups()
                if int(size) >= 2048:
                    scores["memory_safety"] = max(0, scores["memory_safety"] - 10)
                    deductions.append({
                        "category": "memory_safety",
                        "severity": "HIGH",
                        "line": idx,
                        "issue": f"Stack Overflow Hazard: Local array '{buf_name}' allocated on task stack with size {size} bytes.",
                        "penalty": 10,
                        "remedy": "Allocate large buffers in static/global BSS memory or pass via pointer to prevent stack overflow."
                    })

        # 3. Blocking Delay Anti-Pattern inside FreeRTOS tasks
        has_freertos = "xTaskCreate" in source_code or "vTaskDelay" in source_code or "FreeRTOS.h" in source_code
        has_blocking_delay = bool(re.search(r"\bdelay\s*\(\s*\d+\s*\);", source_code))

        if has_freertos and has_blocking_delay:
            scores["concurrency_rtos"] -= 15
            deductions.append({
                "category": "concurrency_rtos",
                "severity": "HIGH",
                "issue": "FreeRTOS CPU Starvation: Found blocking delay() inside multi-tasking FreeRTOS firmware.",
                "penalty": 15,
                "remedy": "Replace busy-wait delay() with non-blocking vTaskDelay(pdMS_TO_TICKS(ms)) to yield execution to lower-priority tasks."
            })
        elif has_freertos and not has_blocking_delay:
            positive_credits.append("Deterministic Multi-Tasking: Compliant use of non-blocking FreeRTOS delay primitives.")

        # 4. DMA Memory Barrier Verification for Advanced DMA Modules
        if module_code in ("EC8708", "EC8706") and "DMA" in source_code:
            has_dmb = "__DMB" in source_code or "__DSB" in source_code
            if not has_dmb:
                scores["concurrency_rtos"] -= 10
                deductions.append({
                    "category": "concurrency_rtos",
                    "severity": "MEDIUM",
                    "issue": "Missing Memory Barrier: Out-of-order DMA buffer write without __DMB() or __DSB().",
                    "penalty": 10,
                    "remedy": "Invoke __DMB() after writing buffer pointers to commit changes into SRAM before enabling DMA stream."
                })
            else:
                positive_credits.append("Memory Coherency: ARM Data Memory Barrier (__DMB) properly placed before DMA trigger.")

        # 5. Hardware Pin Mismatches (Input-Only Pin Assignment as Output)
        pin_mode_pattern = re.compile(r"\bpinMode\s*\(\s*(\d+)\s*,\s*OUTPUT\s*\)", re.IGNORECASE)
        for idx, line in enumerate(lines, 1):
            match = pin_mode_pattern.search(line)
            if match:
                pin = match.group(1)
                if pin in self.INPUT_ONLY_PINS:
                    scores["hardware_pins"] -= 15
                    deductions.append({
                        "category": "hardware_pins",
                        "severity": "CRITICAL",
                        "line": idx,
                        "issue": f"Hardware Invalid Pin Mode: GPIO {pin} is an input-only pin on ESP32 and cannot be set as OUTPUT.",
                        "penalty": 15,
                        "remedy": f"Select an output-capable GPIO (e.g. GPIO 18, 19, 21, 22, 23) instead of input-only GPIO {pin}."
                    })

        # 6. ADC2 Wi-Fi Contention Trap
        has_wifi = bool(re.search(r"\b(WiFi\.begin|esp_wifi_start)\b", source_code))
        analog_read_pattern = re.compile(r"\banalogRead\s*\(\s*(\d+)\s*\)", re.IGNORECASE)
        if has_wifi:
            for idx, line in enumerate(lines, 1):
                match = analog_read_pattern.search(line)
                if match:
                    pin = match.group(1)
                    if pin in self.ADC2_WIFI_CONFLICT_PINS:
                        scores["hardware_pins"] -= 10
                        deductions.append({
                            "category": "hardware_pins",
                            "severity": "HIGH",
                            "line": idx,
                            "issue": f"ADC2 / Wi-Fi Contention: Analog read on GPIO {pin} (ADC2) fails when Wi-Fi driver is active.",
                            "penalty": 10,
                            "remedy": "Use ADC1 channels (GPIO 32, 33, 34, 35, 36, 39) which operate independently from Wi-Fi."
                        })
                        break

        # Calculate Total Composite Score
        total_score = sum(max(0, s) for s in scores.values())
        grade = "O" if total_score >= 90 else "A+" if total_score >= 80 else "A" if total_score >= 70 else "B+" if total_score >= 60 else "RA"

        return {
            "status": "success",
            "module_code": module_code,
            "target_mcu": target_mcu,
            "total_score": total_score,
            "grade": grade,
            "category_scores": scores,
            "deductions": deductions,
            "positive_credits": positive_credits,
            "evaluated_by": "VoltCore AST Autograder v6.0 (MIT Campus ECE)",
            "passed": total_score >= 60,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Global Autograder Instance
firmware_autograder = FirmwareAutograderEngine()

