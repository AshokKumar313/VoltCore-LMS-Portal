#!/usr/bin/env python3
"""
========================================================================================
VoltCore Apex Academia - Deterministic Hardware Schematic Generator
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/schematic_generator.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Deterministically compiles publication-grade, IEEE 315 / IEC 60617 compliant vector
  SVG circuit schematics at build time using Schemdraw, eliminating reliance on
  generative AI image hallucination.
========================================================================================
"""

import os
import sys
import argparse
from typing import Dict, Optional

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import schemdraw
    import schemdraw.elements as elm
    HAS_SCHEMDRAW = True
except ImportError:
    HAS_SCHEMDRAW = False


DEFAULT_OUTPUT_DIR = os.path.join("public", "visuals", "schematics")


def _ensure_dir(path: str) -> None:
    """Ensures parent and target directories exist."""
    os.makedirs(path, exist_ok=True)


def _inject_svg_metadata(svg_data: str, circuit_name: str) -> str:
    """Injects academic attribution metadata and responsive CSS into the SVG."""
    metadata_comment = (
        f"<!--\n"
        f"  VoltCore Apex Academia - Deterministic Circuit Schematic\n"
        f"  Circuit: {circuit_name}\n"
        f"  Institution: Madras Institute of Technology (MIT) Campus, Anna University\n"
        f"  Department: Department of Electronics Engineering (Regulation 2023)\n"
        f"  Platform Lead: Ashok Kumar A (ashokkumar3132008@gmail.com)\n"
        f"  Generator: Schemdraw Deterministic Vector Compiler (Zero AI Hallucination)\n"
        f"-->\n"
    )
    if "<svg" in svg_data:
        svg_data = svg_data.replace("<svg", metadata_comment + "<svg", 1)
    return svg_data


def generate_bjt_ce_amplifier(output_file: Optional[str] = None) -> str:
    """
    Generates a BJT Common-Emitter (CE) Voltage-Divider Biased Amplifier schematic with
    emitter bypass capacitor CE and input/output coupling capacitors C1, C2.
    """
    if not HAS_SCHEMDRAW:
        raise RuntimeError("schemdraw library is required to compile schematics.")

    with schemdraw.Drawing(show=False) as d:
        d.config(fontsize=11, font='sans-serif', inches_per_unit=0.55)

        # Transistor Core
        Q1 = d.add(elm.BjtNpn(label='Q1\n2N2222\n(β=150)'))

        # Base Node & Voltage Divider
        d.add(elm.Dot().at(Q1.base))

        # Upper Bias Resistor R1 -> VCC
        d.add(elm.Resistor().up().at(Q1.base).label('R1\n47 kΩ'))
        d.add(elm.Vdd().label('+12V (Vcc)'))

        # Lower Bias Resistor R2 -> GND
        d.add(elm.Resistor().down().at(Q1.base).label('R2\n10 kΩ'))
        d.add(elm.Ground())

        # AC Signal Input Network (Vin -> C1 -> Base)
        d.add(elm.Capacitor().left().at(Q1.base).label('C1\n10 μF', loc='bottom'))
        d.add(elm.SourceSin().down().label('Vin\n10 mV pk\n1 kHz'))
        d.add(elm.Ground())

        # Collector Branch (Q1.collector -> Rc -> VCC)
        d.add(elm.Dot().at(Q1.collector))
        d.add(elm.Resistor().up().at(Q1.collector).label('Rc\n2.2 kΩ'))
        d.add(elm.Vdd().label('+12V (Vcc)'))

        # Output Coupling Network (Q1.collector -> C2 -> Vout)
        d.add(elm.Capacitor().right().at(Q1.collector).label('C2\n10 μF', loc='bottom'))
        d.add(elm.Line().right().length(1.2).label('Vout\n(180° Inverted)', loc='right'))

        # Emitter Branch with Parallel Emitter Degeneration & Bypass (Re || Ce)
        d.add(elm.Dot().at(Q1.emitter))
        d.add(elm.Resistor().down().at(Q1.emitter).label('Re\n470 Ω'))
        GND_E = d.add(elm.Ground())

        # Emitter Bypass Capacitor Ce parallel to Re
        d.add(elm.Line().right().at(Q1.emitter).length(1.8))
        d.add(elm.Capacitor().down().label('Ce\n100 μF', loc='bottom'))
        d.add(elm.Line().left().tox(GND_E.start))

    svg_data = d.get_imagedata('svg').decode('utf-8')
    svg_data = _inject_svg_metadata(svg_data, "BJT Common-Emitter Amplifier with Voltage Divider Bias")

    if output_file:
        _ensure_dir(os.path.dirname(os.path.abspath(output_file)))
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(svg_data)

    return svg_data


def generate_opamp_inverting(output_file: Optional[str] = None) -> str:
    """
    Generates an Operational Amplifier (Op-Amp) Inverting Amplifier schematic:
    Av = -Rf / Rin, Virtual Ground at inverting input.
    """
    if not HAS_SCHEMDRAW:
        raise RuntimeError("schemdraw library is required to compile schematics.")

    with schemdraw.Drawing(show=False) as d:
        d.config(fontsize=11, font='sans-serif', inches_per_unit=0.55)

        op = d.add(elm.Opamp(leads=True).label('LM741\n(Op-Amp)', loc='center'))

        # Non-inverting input grounded (Virtual Ground at inverting pin)
        d.add(elm.Ground().at(op.in2))

        # Inverting Input Node
        d.add(elm.Dot().at(op.in1))

        # Input Resistor Rin and Signal Source Vin
        d.add(elm.Resistor().left().at(op.in1).label('Rin\n10 kΩ'))
        d.add(elm.SourceSin().down().label('Vin\n1 Vpk'))
        d.add(elm.Ground())

        # Feedback Resistor Rf loop from Output to in1
        d.add(elm.Line().up().at(op.in1).length(1.5))
        d.add(elm.Resistor().right().tox(op.out).label('Rf\n100 kΩ'))
        d.add(elm.Line().down().toy(op.out))
        d.add(elm.Dot().at(op.out))

        # Output terminal
        d.add(elm.Line().right().at(op.out).length(1.2).label('Vout\n(Av = -10)', loc='right'))

    svg_data = d.get_imagedata('svg').decode('utf-8')
    svg_data = _inject_svg_metadata(svg_data, "Operational Amplifier Inverting Configuration (Av = -Rf/Rin)")

    if output_file:
        _ensure_dir(os.path.dirname(os.path.abspath(output_file)))
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(svg_data)

    return svg_data


def generate_rc_lowpass(output_file: Optional[str] = None) -> str:
    """
    Generates a 1st-Order Passive RC Low-Pass Filter schematic:
    Cutoff frequency fc = 1 / (2 * pi * R * C).
    """
    if not HAS_SCHEMDRAW:
        raise RuntimeError("schemdraw library is required to compile schematics.")

    with schemdraw.Drawing(show=False) as d:
        d.config(fontsize=11, font='sans-serif', inches_per_unit=0.55)

        # Input Source
        d.add(elm.SourceSin().up().label('Vin\nAC Sweep'))
        d.add(elm.Dot())

        # Series Resistor R
        d.add(elm.Resistor().right().label('R\n1 kΩ'))
        d.add(elm.Dot())

        # Shunt Capacitor C to Ground
        d.add(elm.Capacitor().down().label('C\n100 nF', loc='bottom'))
        d.add(elm.Ground())

        # Output Port
        d.add(elm.Line().right().at(d.elements[2].end).length(1.5).label('Vout\n(fc = 1.59 kHz)', loc='right'))

    svg_data = d.get_imagedata('svg').decode('utf-8')
    svg_data = _inject_svg_metadata(svg_data, "1st-Order Passive RC Low-Pass Filter (fc = 1 / (2*pi*R*C))")

    if output_file:
        _ensure_dir(os.path.dirname(os.path.abspath(output_file)))
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(svg_data)

    return svg_data


def generate_esp32_i2c_bus(output_file: Optional[str] = None) -> str:
    """
    Generates an ESP32 I2C Hardware Bus Topology with 4.7 kΩ pull-ups to 3.3V,
    SDA (GPIO 21), SCL (GPIO 22), and multi-drop sensor interconnect.
    """
    if not HAS_SCHEMDRAW:
        raise RuntimeError("schemdraw library is required to compile schematics.")

    with schemdraw.Drawing(show=False) as d:
        d.config(fontsize=11, font='sans-serif', inches_per_unit=0.55)

        # 3.3V Rail
        VCC = d.add(elm.Vdd().label('+3.3V (VDD_MCU)'))
        d.add(elm.Line().right().length(3.0))
        d.add(elm.Dot())

        # Pull-Up R1 (SCL) and Pull-Up R2 (SDA)
        d.add(elm.Resistor().down().label('Rp1\n4.7 kΩ (SCL)'))
        SCL_NODE = d.add(elm.Dot())

        d.add(elm.Line().right().at(d.elements[2].end).length(2.0))
        d.add(elm.Resistor().down().label('Rp2\n4.7 kΩ (SDA)'))
        SDA_NODE = d.add(elm.Dot())

        # Lines to MCU Pins
        d.add(elm.Line().left().at(SCL_NODE.center).length(2.5).label('ESP32 GPIO 22\n(SCL Master Clock)', loc='left'))
        d.add(elm.Line().right().at(SCL_NODE.center).length(2.5).label('ADXL345 SCL\n(0x53 Slave)', loc='right'))

        d.add(elm.Line().left().at(SDA_NODE.center).length(4.5).label('ESP32 GPIO 21\n(SDA Open-Drain Data)', loc='left'))
        d.add(elm.Line().right().at(SDA_NODE.center).length(2.5).label('ADXL345 SDA\n(Bi-Directional)', loc='right'))

    svg_data = d.get_imagedata('svg').decode('utf-8')
    svg_data = _inject_svg_metadata(svg_data, "ESP32 Open-Drain I2C Bus Topology with 4.7kΩ Pull-Ups")

    if output_file:
        _ensure_dir(os.path.dirname(os.path.abspath(output_file)))
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(svg_data)

    return svg_data


def generate_all_schematics(output_dir: str = DEFAULT_OUTPUT_DIR) -> Dict[str, str]:
    """
    Compiles all standard curriculum schematics into the specified target directory.
    Returns a dictionary of circuit IDs mapped to their output file paths.
    """
    _ensure_dir(output_dir)

    generators = {
        "bjt_ce_amplifier": ("bjt_ce_amplifier.svg", generate_bjt_ce_amplifier),
        "opamp_inverting": ("opamp_inverting_amplifier.svg", generate_opamp_inverting),
        "rc_lowpass_filter": ("rc_lowpass_filter.svg", generate_rc_lowpass),
        "esp32_i2c_bus": ("esp32_i2c_bus_topology.svg", generate_esp32_i2c_bus)
    }

    generated_map = {}
    for cid, (filename, fn) in generators.items():
        out_path = os.path.join(output_dir, filename)
        fn(output_file=out_path)
        generated_map[cid] = out_path

    return generated_map


def main():
    parser = argparse.ArgumentParser(
        description="VoltCore Apex Academia - Deterministic Circuit Schematic Generator"
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save generated SVGs (default: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--circuit",
        choices=["all", "bjt_ce", "opamp", "rc", "i2c"],
        default="all",
        help="Specific circuit schematic to generate"
    )

    args = parser.parse_args()

    # Determine Project Root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    target_dir = os.path.abspath(args.output_dir if os.path.isabs(args.output_dir) else os.path.join(project_root, args.output_dir))

    print(f"\n[VOLTCORE APEX ACADEMIA - SCHEMDRAW VECTOR COMPILER]")
    print(f"Target Output Directory: {target_dir}")

    if args.circuit == "all":
        results = generate_all_schematics(output_dir=target_dir)
        for cid, fpath in results.items():
            fsize = os.path.getsize(fpath)
            print(f"  ✓ Compiled [{cid:<18}] -> {os.path.basename(fpath)} ({fsize:,} bytes)")
    elif args.circuit == "bjt_ce":
        p = os.path.join(target_dir, "bjt_ce_amplifier.svg")
        generate_bjt_ce_amplifier(output_file=p)
        print(f"  ✓ Compiled [bjt_ce_amplifier] -> {p}")
    elif args.circuit == "opamp":
        p = os.path.join(target_dir, "opamp_inverting_amplifier.svg")
        generate_opamp_inverting(output_file=p)
        print(f"  ✓ Compiled [opamp_inverting] -> {p}")
    elif args.circuit == "rc":
        p = os.path.join(target_dir, "rc_lowpass_filter.svg")
        generate_rc_lowpass(output_file=p)
        print(f"  ✓ Compiled [rc_lowpass_filter] -> {p}")
    elif args.circuit == "i2c":
        p = os.path.join(target_dir, "esp32_i2c_bus_topology.svg")
        generate_esp32_i2c_bus(output_file=p)
        print(f"  ✓ Compiled [esp32_i2c_bus] -> {p}")

    print("[SUCCESS] All deterministic circuit schematics generated with zero generative AI hallucination.\n")


if __name__ == "__main__":
    main()

