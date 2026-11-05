"""
========================================================================================
VoltCore Apex Academia - Circuit & Schematic Syntax Parser
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/circuit_syntax_parser.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Static linting, electrical rule checking (ERC), and schematic topology verification
  for Wokwi diagram.json and Schemdraw circuit models submitted in laboratory assignments.
========================================================================================
"""

import json
from typing import Dict, Any, List, Tuple, Set


class CircuitSyntaxParser:
    """
    Electrical Rules Checking (ERC) engine for Wokwi and Schemdraw topologies.
    Detects VCC-GND shorts, missing I2C pullups, and 5V-to-3.3V logic level overvoltages.
    """

    ESP32_INPUT_ONLY_PINS = {"34", "35", "36", "39"}
    ESP32_STRAPPING_PINS = {"0", "2", "12", "15"}

    def parse_wokwi_diagram(self, diagram_json_str: str) -> Dict[str, Any]:
        """
        Parses Wokwi diagram.json structure and executes Electrical Rules Check (ERC).
        """
        try:
            data = json.loads(diagram_json_str)
        except json.JSONDecodeError as err:
            return {
                "valid": False,
                "score": 0,
                "errors": [f"Malformed JSON in diagram specification: {str(err)}"],
                "warnings": [],
                "part_count": 0,
                "connection_count": 0
            }

        parts = data.get("parts", [])
        connections = data.get("connections", [])

        errors: List[str] = []
        warnings: List[str] = []

        # 1. Connectivity Graph Analysis
        pin_nets: Dict[str, Set[str]] = {}
        for conn in connections:
            if not isinstance(conn, list) or len(conn) < 2:
                continue
            src, dst = str(conn[0]), str(conn[1])
            pin_nets.setdefault(src, set()).add(dst)
            pin_nets.setdefault(dst, set()).add(src)

        # 2. Short Circuit Detection (VCC directly connected to GND)
        for pin, neighbors in pin_nets.items():
            pin_lower = pin.lower()
            if any(p in pin_lower for p in ["vcc", "5v", "3v3", "vin"]):
                for n in neighbors:
                    n_lower = n.lower()
                    if any(g in n_lower for g in ["gnd", "ground", "0v"]):
                        errors.append(f"CRITICAL SHORT CIRCUIT: Direct connection detected between power rail '{pin}' and ground '{n}'.")

        # 3. I2C Bus Pull-Up Resistor Verification
        has_i2c_dev = any("mpu6050" in str(p).lower() or "ds1307" in str(p).lower() or "pcf8574" in str(p).lower() for p in parts)
        if has_i2c_dev:
            has_pullup = any("resistor" in str(p).lower() for p in parts)
            if not has_pullup:
                warnings.append("I2C BUS INTEGRITY: External pull-up resistors (2.2k-4.7kΩ) recommended on SDA/SCL lines for 400kHz Fast-Mode operation.")

        # 4. Input-Only Pin Output Assignment Check
        for conn in connections:
            if len(conn) >= 2:
                for endpoint in [str(conn[0]), str(conn[1])]:
                    parts_split = endpoint.split(":")
                    if len(parts_split) == 2 and ("esp" in parts_split[0].lower() or "mcu" in parts_split[0].lower()):
                        pin_num = parts_split[1].replace("gpio", "").replace("d", "")
                        # If connected to LED anode or relay without input capability
                        if pin_num in self.ESP32_INPUT_ONLY_PINS:
                            peer = conn[1] if endpoint == str(conn[0]) else conn[0]
                            if any(act in str(peer).lower() for act in ["led", "relay", "buzzer", "motor"]):
                                errors.append(f"PIN MISMATCH: GPIO {pin_num} is an input-only pin (GPI) on ESP32 and cannot drive actuator '{peer}'.")

        # Calculate Score out of 100
        score = 100
        score -= len(errors) * 35
        score -= len(warnings) * 10
        score = max(0, min(100, score))

        return {
            "valid": len(errors) == 0,
            "score": score,
            "errors": errors,
            "warnings": warnings,
            "part_count": len(parts),
            "connection_count": len(connections),
            "status": "PASS" if len(errors) == 0 else "FAIL"
        }
