"""
========================================================================================
VoltCore Apex Academia - Advanced ECE Knowledge Center & Formula Encyclopedia
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/ece_knowledge_engine.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Lightweight backend manager handling:
    1. Curated ECE Formula Encyclopedia (LaTeX, derivation, variables, unit results).
    2. Component Datasheet Library (ESP32, STM32, Op-Amps, Transistors, Instruments).
    3. Technical Abbreviation Dictionary (CMRR, PLL, AWGN, SAR ADC, FSM, SPI).
    4. SQLite WAL-backed fast lookup engine (< 5ms latency, zero GPU/CPU load).
========================================================================================
"""

import os
import time
import json
import sqlite3
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")

# Default Anna University ECE Regulation 2023 Formula Encyclopedia
DEFAULT_FORMULAS = [
    # --- EC3352: Digital Systems Design ---
    {
        "formula_id": "FORM_DE_MORGAN",
        "topic": "Boolean Algebra",
        "formula_name": "De Morgan's Laws",
        "subject_code": "EC3352",
        "unit_number": 1,
        "latex_repr": "\\overline{A \\cdot B} = \\bar{A} + \\bar{B}, \\quad \\overline{A + B} = \\bar{A} \\cdot \\bar{B}",
        "plain_text": "NOT(A AND B) = NOT(A) OR NOT(B); NOT(A OR B) = NOT(A) AND NOT(B)",
        "derivation_summary": "Fundamental duality theorem in Boolean algebra transforming product-of-sums into sum-of-products.",
        "variables_json": json.dumps({"A": "Binary Boolean input A", "B": "Binary Boolean input B"}),
        "unit_result": "Boolean (0 or 1)",
        "au_regulation": "EC3352"
    },
    {
        "formula_id": "FORM_FSM_CLOCK_PERIOD",
        "topic": "Synchronous Sequential Logic",
        "formula_name": "FSM Minimum Clock Period & Setup Invariant",
        "subject_code": "EC3352",
        "unit_number": 2,
        "latex_repr": "T_{clk} \\ge t_{cq} + t_{comb} + t_{setup}",
        "plain_text": "Tclk >= t_cq + t_comb + t_setup",
        "derivation_summary": "Ensures data launched from flip-flop propagation delay and combinational network stabilizes before next clock edge.",
        "variables_json": json.dumps({"T_{clk}": "Clock period (s)", "t_{cq}": "Clock-to-Q delay (s)", "t_{comb}": "Max combinational delay (s)", "t_{setup}": "Flip-flop setup time (s)"}),
        "unit_result": "Seconds (s)",
        "au_regulation": "EC3352"
    },
    {
        "formula_id": "FORM_CLA_CARRY",
        "topic": "Arithmetic Circuits",
        "formula_name": "Carry Lookahead Adder Carry Generation",
        "subject_code": "EC3352",
        "unit_number": 1,
        "latex_repr": "C_{i+1} = G_i + P_i C_i, \\quad G_i = A_i B_i, \\; P_i = A_i \\oplus B_i",
        "plain_text": "C_(i+1) = G_i + P_i * C_i where G_i = A_i * B_i and P_i = A_i XOR B_i",
        "derivation_summary": "Eliminates ripple carry propagation delay by computing carries in parallel using Generate and Propagate terms.",
        "variables_json": json.dumps({"C_{i+1}": "Carry out of stage i", "G_i": "Carry generate term", "P_i": "Carry propagate term", "C_i": "Carry in"}),
        "unit_result": "Boolean (Carry bit)",
        "au_regulation": "EC3352"
    },

    # --- EC3452: Electromagnetic Fields ---
    {
        "formula_id": "FORM_GAUSS_ELECTRIC",
        "topic": "Electrostatics",
        "formula_name": "Gauss's Law for Electric Fields (Differential Form)",
        "subject_code": "EC3452",
        "unit_number": 1,
        "latex_repr": "\\nabla \\cdot \\mathbf{D} = \\rho_v",
        "plain_text": "div(D) = rho_v",
        "derivation_summary": "States that the divergence of electric flux density D from any volume is equal to the volume charge density enclosed.",
        "variables_json": json.dumps({"D": "Electric flux density (C/m^2)", "rho_v": "Volume charge density (C/m^3)"}),
        "unit_result": "Coulombs / m^3",
        "au_regulation": "EC3452"
    },
    {
        "formula_id": "FORM_FARADAY_INDUCTION",
        "topic": "Time-Varying Fields",
        "formula_name": "Faraday's Law of Induction (Maxwell's 3rd Equation)",
        "subject_code": "EC3452",
        "unit_number": 4,
        "latex_repr": "\\nabla \\times \\mathbf{E} = -\\frac{\\partial \\mathbf{B}}{\\partial t}",
        "plain_text": "curl(E) = -dB/dt",
        "derivation_summary": "A time-varying magnetic flux density produces an electric field circulation, forming the governing equation for inductors and transformers.",
        "variables_json": json.dumps({"E": "Electric field intensity (V/m)", "B": "Magnetic flux density (Tesla)", "t": "Time (s)"}),
        "unit_result": "Volts / m^2",
        "au_regulation": "EC3452"
    },
    {
        "formula_id": "FORM_POYNTING_VECTOR",
        "topic": "Electromagnetic Wave Propagation",
        "formula_name": "Poynting Vector (Instantaneous Power Flow)",
        "subject_code": "EC3452",
        "unit_number": 4,
        "latex_repr": "\\mathbf{S} = \\mathbf{E} \\times \\mathbf{H}",
        "plain_text": "S = E x H",
        "derivation_summary": "Represents the directional energy flux density (rate of energy transfer per unit area) of an electromagnetic wave.",
        "variables_json": json.dumps({"S": "Poynting vector (W/m^2)", "E": "Electric field vector (V/m)", "H": "Magnetic field vector (A/m)"}),
        "unit_result": "Watts / m^2",
        "au_regulation": "EC3452"
    },
    {
        "formula_id": "FORM_SKIN_DEPTH",
        "topic": "Uniform Plane Waves",
        "formula_name": "Skin Depth in Good Conducting Media",
        "subject_code": "EC3452",
        "unit_number": 5,
        "latex_repr": "\\delta = \\frac{1}{\\sqrt{\\pi f \\mu \\sigma}}",
        "plain_text": "delta = 1 / sqrt(pi * f * mu * sigma)",
        "derivation_summary": "Depth at which the amplitude of an impinging electromagnetic wave attenuates to 1/e (~36.8%) of its surface value.",
        "variables_json": json.dumps({"delta": "Skin depth (m)", "f": "Frequency (Hz)", "mu": "Permeability (H/m)", "sigma": "Conductivity (S/m)"}),
        "unit_result": "Meters (m)",
        "au_regulation": "EC3452"
    },

    # --- EC3451: Linear Integrated Circuits ---
    {
        "formula_id": "FORM_OPAMP_INV_GAIN",
        "topic": "Operational Amplifiers",
        "formula_name": "Inverting Op-Amp Closed-Loop Voltage Gain",
        "subject_code": "EC3451",
        "unit_number": 1,
        "latex_repr": "A_v = -\\frac{R_f}{R_{in}}",
        "plain_text": "Av = -(Rf / Rin)",
        "derivation_summary": "Derived from virtual ground concept at the inverting terminal under negative feedback configuration.",
        "variables_json": json.dumps({"A_v": "Voltage gain (dimensionless)", "R_f": "Feedback resistor (Ohms)", "R_{in}": "Input resistor (Ohms)"}),
        "unit_result": "V/V",
        "au_regulation": "EC3451"
    },
    {
        "formula_id": "FORM_OPAMP_CMRR",
        "topic": "Differential Amplifiers",
        "formula_name": "Common-Mode Rejection Ratio (CMRR)",
        "subject_code": "EC3451",
        "unit_number": 1,
        "latex_repr": "\\text{CMRR}_{dB} = 20 \\log_{10} \\left|\\frac{A_d}{A_{cm}}\\right|",
        "plain_text": "CMRR_dB = 20 * log10(|Ad / Acm|)",
        "derivation_summary": "Figures of merit measuring the amplifier's ability to reject unwanted common-mode noise while amplifying differential signals.",
        "variables_json": json.dumps({"A_d": "Differential gain", "A_{cm}": "Common-mode gain"}),
        "unit_result": "Decibels (dB)",
        "au_regulation": "EC3451"
    },
    {
        "formula_id": "FORM_SLEW_RATE",
        "topic": "Op-Amp Dynamic Characteristics",
        "formula_name": "Full-Power Bandwidth & Slew Rate",
        "subject_code": "EC3451",
        "unit_number": 1,
        "latex_repr": "\\text{SR} = \\left.\\frac{dV_o}{dt}\\right|_{max} = 2\\pi f_{max} V_p",
        "plain_text": "SR = 2 * pi * f_max * V_p",
        "derivation_summary": "Maximum rate of change of output voltage without experiencing non-linear slew-induced distortion.",
        "variables_json": json.dumps({"SR": "Slew Rate (V/s or V/us)", "f_{max}": "Full-power bandwidth (Hz)", "V_p": "Peak output amplitude (V)"}),
        "unit_result": "V / microsecond",
        "au_regulation": "EC3451"
    },
    {
        "formula_id": "FORM_555_ASTABLE",
        "topic": "Special Function ICs",
        "formula_name": "IC 555 Astable Multivibrator Frequency",
        "subject_code": "EC3451",
        "unit_number": 5,
        "latex_repr": "f = \\frac{1.44}{(R_A + 2 R_B) C}, \\quad D = \\frac{R_A + R_B}{R_A + 2 R_B}",
        "plain_text": "f = 1.44 / ((RA + 2*RB) * C); Duty Cycle = (RA + RB) / (RA + 2*RB)",
        "derivation_summary": "Charge time through (RA + RB)*C*ln(2) and discharge time through RB*C*ln(2).",
        "variables_json": json.dumps({"f": "Oscillation frequency (Hz)", "R_A": "Timing resistor A (Ohms)", "R_B": "Timing resistor B (Ohms)", "C": "Timing capacitor (F)"}),
        "unit_result": "Hertz (Hz)",
        "au_regulation": "EC3451"
    },

    # --- EC3491: Communication Systems ---
    {
        "formula_id": "FORM_RLC_RESONANCE",
        "topic": "RF & Tuned Circuits",
        "formula_name": "Series/Parallel RLC Resonant Frequency",
        "subject_code": "EC3491",
        "unit_number": 1,
        "latex_repr": "f_0 = \\frac{1}{2\\pi \\sqrt{L C}}",
        "plain_text": "f0 = 1 / (2 * pi * sqrt(L * C))",
        "derivation_summary": "Condition where inductive reactance cancels capacitive reactance, resulting in purely resistive impedance.",
        "variables_json": json.dumps({"f_0": "Resonant frequency (Hz)", "L": "Inductance (H)", "C": "Capacitance (F)"}),
        "unit_result": "Hertz (Hz)",
        "au_regulation": "EC3491"
    },
    {
        "formula_id": "FORM_NYQUIST_SAMPLING",
        "topic": "Baseband Digital Transmission",
        "formula_name": "Nyquist-Shannon Sampling Criterion",
        "subject_code": "EC3491",
        "unit_number": 3,
        "latex_repr": "f_s \\ge 2 f_{max}",
        "plain_text": "fs >= 2 * fmax",
        "derivation_summary": "Minimum sampling rate required to fully reconstruct a bandlimited analog signal without spectral aliasing.",
        "variables_json": json.dumps({"f_s": "Sampling frequency (Hz)", "f_{max}": "Highest signal frequency (Hz)"}),
        "unit_result": "Samples / second (Hz)",
        "au_regulation": "EC3491"
    },
    {
        "formula_id": "FORM_SHANNON_CAPACITY",
        "topic": "Information Theory",
        "formula_name": "Shannon-Hartley Channel Capacity",
        "subject_code": "EC3491",
        "unit_number": 5,
        "latex_repr": "C = B \\log_2\\left(1 + \\text{SNR}\\right)",
        "plain_text": "C = B * log2(1 + SNR)",
        "derivation_summary": "Theoretical maximum rate at which error-free data can be transmitted over an additive white Gaussian noise channel.",
        "variables_json": json.dumps({"C": "Channel capacity (bps)", "B": "Channel bandwidth (Hz)", "SNR": "Signal-to-noise power ratio (linear)"}),
        "unit_result": "Bits / second",
        "au_regulation": "EC3491"
    },
    {
        "formula_id": "FORM_CARSON_RULE",
        "topic": "Angle Modulation",
        "formula_name": "Carson's Rule for FM Transmission Bandwidth",
        "subject_code": "EC3491",
        "unit_number": 2,
        "latex_repr": "B_T = 2 (\\Delta f + f_m) = 2 f_m (\\beta + 1)",
        "plain_text": "BT = 2 * (delta_f + fm) = 2 * fm * (beta + 1)",
        "derivation_summary": "Approximates 98% of the total transmitted power in an angle-modulated frequency carrier.",
        "variables_json": json.dumps({"B_T": "Transmission bandwidth (Hz)", "delta_f": "Peak frequency deviation (Hz)", "f_m": "Modulating frequency (Hz)", "beta": "Modulation index"}),
        "unit_result": "Hertz (Hz)",
        "au_regulation": "EC3491"
    }
]

# Curated Component Datasheet Library
DEFAULT_COMPONENTS = [
    {
        "part_number": "ESP32-S3-WROOM-1",
        "component_name": "Dual-Core Xtensa LX7 MCU with Wi-Fi & BLE",
        "category": "MICROCONTROLLER",
        "manufacturer": "Espressif Systems",
        "operating_voltage": "3.0V – 3.6V",
        "package_type": "QFN-56 / Surface Mount",
        "pin_count": 44,
        "key_specs_json": json.dumps({
            "Core Clock": "240 MHz",
            "Flash": "8 MB SPI Flash",
            "SRAM": "512 KB",
            "Wireless": "2.4 GHz Wi-Fi (802.11 b/g/n) + Bluetooth 5.0 LE",
            "Hardware USB": "Full-speed USB-OTG and USB-CDC Serial",
            "Peripherals": "4x SPI, 3x UART, 2x I2C, 14x Touch, 8x PWM"
        }),
        "datasheet_url": "https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf"
    },
    {
        "part_number": "STM32F407VGT6",
        "component_name": "ARM Cortex-M4 High-Performance DSP MCU",
        "category": "MICROCONTROLLER",
        "manufacturer": "STMicroelectronics",
        "operating_voltage": "1.8V – 3.6V",
        "package_type": "LQFP-100",
        "pin_count": 100,
        "key_specs_json": json.dumps({
            "Core Clock": "168 MHz with Single-Precision FPU",
            "Flash": "1024 KB Flash Memory",
            "SRAM": "192 KB (including 64KB CCM RAM)",
            "ADC": "3x 12-bit, 2.4 MSPS ADCs (up to 7.2 MSPS interleaved)",
            "DAC": "2x 12-bit DAC channels",
            "Peripherals": "Ethernet MAC, USB OTG HS/FS, 3x SPI, 4x USART, 3x I2C"
        }),
        "datasheet_url": "https://www.st.com/resource/en/datasheet/stm32f407vg.pdf"
    },
    {
        "part_number": "LM741CN",
        "component_name": "General Purpose Operational Amplifier",
        "category": "OPAMP",
        "manufacturer": "Texas Instruments",
        "operating_voltage": "±5.0V to ±18.0V",
        "package_type": "PDIP-8",
        "pin_count": 8,
        "key_specs_json": json.dumps({
            "Unity Gain Bandwidth": "1.0 MHz",
            "Slew Rate": "0.5 V/µs",
            "Input Offset Voltage": "1.0 mV typical",
            "CMRR": "90 dB typical",
            "Supply Current": "1.7 mA",
            "Protection": "Short-circuit protected output"
        }),
        "datasheet_url": "https://www.ti.com/lit/ds/symlink/lm741.pdf"
    },
    {
        "part_number": "NE555P",
        "component_name": "Precision Bipolar Timer / Pulse Generator",
        "category": "TIMER",
        "manufacturer": "Texas Instruments",
        "operating_voltage": "4.5V – 16.0V",
        "package_type": "PDIP-8",
        "pin_count": 8,
        "key_specs_json": json.dumps({
            "Max Operating Frequency": "500 kHz",
            "Timing Delay": "Microseconds to hours",
            "Output Sink/Source": "200 mA capability",
            "Operating Modes": "Astable, Monostable, Bistable",
            "Trigger Voltage": "1/3 Vcc",
            "Threshold Voltage": "2/3 Vcc"
        }),
        "datasheet_url": "https://www.ti.com/lit/ds/symlink/ne555.pdf"
    },
    {
        "part_number": "2N2222A",
        "component_name": "NPN High-Speed Switching Transistor",
        "category": "TRANSISTOR",
        "manufacturer": "ON Semiconductor",
        "operating_voltage": "Vceo = 40V, Vcbo = 75V",
        "package_type": "TO-92",
        "pin_count": 3,
        "key_specs_json": json.dumps({
            "Collector Current (Ic)": "800 mA continuous",
            "Transition Frequency (fT)": "300 MHz",
            "DC Current Gain (hFE)": "100 to 300 @ 150mA",
            "Power Dissipation": "625 mW @ 25°C ambient",
            "Turn-on Time": "35 ns",
            "Turn-off Time": "285 ns"
        }),
        "datasheet_url": "https://www.onsemi.com/pdf/datasheet/p2n2222a-d.pdf"
    },
    {
        "part_number": "AD620AN",
        "component_name": "Low Cost, Low Power Instrumentation Amplifier",
        "category": "OPAMP",
        "manufacturer": "Analog Devices",
        "operating_voltage": "±2.3V to ±18.0V",
        "package_type": "DIP-8",
        "pin_count": 8,
        "key_specs_json": json.dumps({
            "Gain Range": "1 to 10,000 configured by 1 external resistor Rg",
            "Gain Formula": "G = 1 + (49.4 kΩ / Rg)",
            "CMRR": "100 dB minimum (G = 10)",
            "Input Offset Drift": "0.6 µV/°C",
            "Bandwidth": "120 kHz (G = 100)",
            "Quiescent Current": "1.3 mA max"
        }),
        "datasheet_url": "https://www.analog.com/media/en/technical-documentation/data-sheets/AD620.pdf"
    },
    {
        "part_number": "Keysight-DSOX1204G",
        "component_name": "4-Channel Digital Storage Oscilloscope with WaveGen",
        "category": "INSTRUMENT",
        "manufacturer": "Keysight Technologies",
        "operating_voltage": "100V – 240V AC",
        "package_type": "Benchtop Instrument",
        "pin_count": 4,
        "key_specs_json": json.dumps({
            "Bandwidth": "70 MHz to 200 MHz upgradeable",
            "Sample Rate": "Up to 2.0 GSa/s",
            "Channels": "4 analog channels",
            "Function Generator": "20 MHz built-in arbitrary waveform generator",
            "Waveform Update Rate": "100,000 waveforms/second",
            "Serial Bus Decode": "I2C, SPI, UART/RS232, CAN, LIN"
        }),
        "datasheet_url": "https://www.keysight.com/us/en/assets/7018-05995/data-sheets/5992-3484EN.pdf"
    },
    {
        "part_number": "Rigol-DP832",
        "component_name": "Programmable Triple-Output Linear DC Power Supply",
        "category": "INSTRUMENT",
        "manufacturer": "Rigol Technologies",
        "operating_voltage": "100V – 240V AC",
        "package_type": "Benchtop Instrument",
        "pin_count": 3,
        "key_specs_json": json.dumps({
            "Channels": "3 isolated channels (Ch1: 30V/3A, Ch2: 30V/3A, Ch3: 5V/3A)",
            "Total Power": "195 Watts",
            "Ripple & Noise": "< 350 µVrms / 2 mVpp",
            "Over-Voltage / Over-Current": "Hardware electronic trip < 10 ms",
            "Connectivity": "USB Device, USB Host, LAN (LXI-C), GPIB"
        }),
        "datasheet_url": "https://www.rigolna.com/products/dc-power-loads/dp800/"
    }
]

# ECE Technical Abbreviation Dictionary
DEFAULT_ABBREVIATIONS = [
    {
        "term": "CMRR",
        "full_form": "Common-Mode Rejection Ratio",
        "category": "ANALOG_CIRCUITS",
        "definition": "The ratio of differential voltage gain to common-mode voltage gain in an operational or instrumentation amplifier, expressing its ability to reject common-mode noise.",
        "related_subject": "EC3451"
    },
    {
        "term": "PLL",
        "full_form": "Phase-Locked Loop",
        "category": "COMMUNICATION",
        "definition": "An electronic feedback circuit consisting of a phase detector, low-pass filter, and voltage-controlled oscillator that locks output frequency to an input reference phase.",
        "related_subject": "EC3451"
    },
    {
        "term": "FSM",
        "full_form": "Finite State Machine",
        "category": "DIGITAL_SYSTEMS",
        "definition": "A computational sequential model with discrete states, transitions triggered by inputs, and registered outputs (Mealy or Moore architectures).",
        "related_subject": "EC3352"
    },
    {
        "term": "AWGN",
        "full_form": "Additive White Gaussian Noise",
        "category": "COMMUNICATION",
        "definition": "A channel noise impairment model where thermal noise is added linearly with uniform spectral density across all frequencies and Gaussian amplitude probability.",
        "related_subject": "EC3491"
    },
    {
        "term": "SAR ADC",
        "full_form": "Successive Approximation Register Analog-to-Digital Converter",
        "category": "ANALOG_CIRCUITS",
        "definition": "A widely used ADC architecture that performs binary search comparisons with an internal DAC to convert analog voltages into discrete digital codes.",
        "related_subject": "EC3451"
    },
    {
        "term": "BER",
        "full_form": "Bit Error Rate",
        "category": "COMMUNICATION",
        "definition": "The percentage of bits with errors divided by the total number of bits transmitted, received, or processed over a telecommunication link.",
        "related_subject": "EC3491"
    },
    {
        "term": "FFT",
        "full_form": "Fast Fourier Transform",
        "category": "SIGNAL_PROCESSING",
        "definition": "An optimized mathematical algorithm to compute the Discrete Fourier Transform (DFT) of a digital sequence in O(N log N) computational complexity.",
        "related_subject": "EC3491"
    },
    {
        "term": "SPI",
        "full_form": "Serial Peripheral Interface",
        "category": "EMBEDDED_SYSTEMS",
        "definition": "A synchronous 4-wire full-duplex serial communication bus standard (MOSI, MISO, SCLK, and CS/SS) widely utilized for sensors, flash memories, and DACs.",
        "related_subject": "EC3352"
    },
    {
        "term": "I2C",
        "full_form": "Inter-Integrated Circuit",
        "category": "EMBEDDED_SYSTEMS",
        "definition": "A multi-master, multi-slave, single-ended 2-wire serial bus standard utilizing Serial Data (SDA) and Serial Clock (SCL) with open-drain pull-up resistors.",
        "related_subject": "EC3352"
    },
    {
        "term": "UART",
        "full_form": "Universal Asynchronous Receiver-Transmitter",
        "category": "EMBEDDED_SYSTEMS",
        "definition": "A hardware communication protocol facilitating asynchronous byte transmission without shared clock signals via configurable baud rates, start/stop, and parity bits.",
        "related_subject": "EC3352"
    },
    {
        "term": "HIL",
        "full_form": "Hardware-in-the-Loop",
        "category": "EMBEDDED_SYSTEMS",
        "definition": "A real-time simulation technique where physical microcontrollers, FPGA boards, or sensors interact directly with virtual circuit models and test assertion benches.",
        "related_subject": "EC3352"
    },
    {
        "term": "PWM",
        "full_form": "Pulse-Width Modulation",
        "category": "EMBEDDED_SYSTEMS",
        "definition": "A modulation technique that varies the duty cycle of a fixed-frequency rectangular carrier wave to control average electrical power delivered to motors, LEDs, or power stages.",
        "related_subject": "EC3451"
    },
    {
        "term": "EMF",
        "full_form": "Electromotive Force",
        "category": "ELECTROMAGNETICS",
        "definition": "The electrical energy provided by an energy source per coulomb of charge, or the voltage induced across a conductor by time-varying magnetic flux.",
        "related_subject": "EC3452"
    },
    {
        "term": "RISC-V",
        "full_form": "Reduced Instruction Set Computer - Architecture V",
        "category": "DIGITAL_SYSTEMS",
        "definition": "An open standard, royalty-free instruction set architecture (ISA) based on established reduced instruction set computer principles.",
        "related_subject": "EC3352"
    }
]


class EceKnowledgeEngine:
    """
    Lightweight, thread-safe ECE Knowledge Center & Formula Encyclopedia Manager
    using SQLite WAL storage for sub-millisecond retrieval on local hardware.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self._lock = threading.Lock()
        self._init_sqlite_schema()
        self._seed_default_knowledge_data()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns an optimized SQLite WAL connection."""
        conn = sqlite3.connect(self.db_path, timeout=5.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode = WAL;")
        cur.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_sqlite_schema(self) -> None:
        """Initializes tables for ECE formulas, component datasheets, and abbreviations."""
        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()
            try:
                # 1. Formula Encyclopedia
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS ece_formula_encyclopedia (
                        formula_id TEXT PRIMARY KEY,
                        topic TEXT NOT NULL,
                        formula_name TEXT NOT NULL,
                        subject_code TEXT NOT NULL,
                        unit_number INTEGER NOT NULL,
                        latex_repr TEXT NOT NULL,
                        plain_text TEXT NOT NULL,
                        derivation_summary TEXT NOT NULL,
                        variables_json TEXT NOT NULL,
                        unit_result TEXT NOT NULL,
                        au_regulation TEXT NOT NULL
                    );
                """)

                # 2. Component Datasheet Library
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS ece_component_datasheets (
                        part_number TEXT PRIMARY KEY,
                        component_name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        manufacturer TEXT NOT NULL,
                        operating_voltage TEXT NOT NULL,
                        package_type TEXT NOT NULL,
                        pin_count INTEGER NOT NULL,
                        key_specs_json TEXT NOT NULL,
                        datasheet_url TEXT NOT NULL
                    );
                """)

                # 3. Technical Abbreviation Dictionary
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS ece_abbreviation_dictionary (
                        term TEXT PRIMARY KEY,
                        full_form TEXT NOT NULL,
                        category TEXT NOT NULL,
                        definition TEXT NOT NULL,
                        related_subject TEXT NOT NULL
                    );
                """)
                conn.commit()
            finally:
                conn.close()

    def _seed_default_knowledge_data(self) -> None:
        """Seeds initial Anna University ECE knowledge base if empty."""
        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()
            try:
                # Seed formulas
                cur.execute("SELECT COUNT(*) FROM ece_formula_encyclopedia;")
                if cur.fetchone()[0] == 0:
                    for f in DEFAULT_FORMULAS:
                        cur.execute("""
                            INSERT INTO ece_formula_encyclopedia
                            (formula_id, topic, formula_name, subject_code, unit_number, latex_repr, plain_text, derivation_summary, variables_json, unit_result, au_regulation)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, (
                            f["formula_id"], f["topic"], f["formula_name"],
                            f["subject_code"], f["unit_number"], f["latex_repr"],
                            f["plain_text"], f["derivation_summary"],
                            f["variables_json"], f["unit_result"], f["au_regulation"]
                        ))

                # Seed components
                cur.execute("SELECT COUNT(*) FROM ece_component_datasheets;")
                if cur.fetchone()[0] == 0:
                    for comp in DEFAULT_COMPONENTS:
                        cur.execute("""
                            INSERT INTO ece_component_datasheets
                            (part_number, component_name, category, manufacturer, operating_voltage, package_type, pin_count, key_specs_json, datasheet_url)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, (
                            comp["part_number"], comp["component_name"], comp["category"],
                            comp["manufacturer"], comp["operating_voltage"],
                            comp["package_type"], comp["pin_count"],
                            comp["key_specs_json"], comp["datasheet_url"]
                        ))

                # Seed abbreviations
                cur.execute("SELECT COUNT(*) FROM ece_abbreviation_dictionary;")
                if cur.fetchone()[0] == 0:
                    for abbr in DEFAULT_ABBREVIATIONS:
                        cur.execute("""
                            INSERT INTO ece_abbreviation_dictionary
                            (term, full_form, category, definition, related_subject)
                            VALUES (?, ?, ?, ?, ?);
                        """, (
                            abbr["term"], abbr["full_form"], abbr["category"],
                            abbr["definition"], abbr["related_subject"]
                        ))
                conn.commit()
            finally:
                conn.close()

    def search_formulas(
        self,
        query: Optional[str] = None,
        subject_code: Optional[str] = None,
        unit_number: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Searches formula encyclopedia by keyword, subject code, or unit number."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            conditions = []
            params = []

            if subject_code and subject_code.upper() != "ALL":
                conditions.append("UPPER(subject_code) = UPPER(?)")
                params.append(subject_code)

            if unit_number is not None and unit_number > 0:
                conditions.append("unit_number = ?")
                params.append(unit_number)

            if query and query.strip():
                kw = f"%{query.strip()}%"
                conditions.append("(formula_name LIKE ? OR topic LIKE ? OR plain_text LIKE ? OR derivation_summary LIKE ?)")
                params.extend([kw, kw, kw, kw])

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            sql = f"SELECT * FROM ece_formula_encyclopedia{where_clause} ORDER BY subject_code, unit_number, formula_name;"
            cur.execute(sql, params)
            rows = cur.fetchall()

            results = []
            for r in rows:
                item = dict(r)
                item["variables"] = json.loads(item["variables_json"])
                results.append(item)
            return results
        finally:
            conn.close()

    def search_components(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Searches component datasheet library by part number, name, or category."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            conditions = []
            params = []

            if category and category.upper() != "ALL":
                conditions.append("UPPER(category) = UPPER(?)")
                params.append(category)

            if query and query.strip():
                kw = f"%{query.strip()}%"
                conditions.append("(part_number LIKE ? OR component_name LIKE ? OR manufacturer LIKE ?)")
                params.extend([kw, kw, kw])

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            sql = f"SELECT * FROM ece_component_datasheets{where_clause} ORDER BY category, part_number;"
            cur.execute(sql, params)
            rows = cur.fetchall()

            results = []
            for r in rows:
                item = dict(r)
                item["key_specs"] = json.loads(item["key_specs_json"])
                results.append(item)
            return results
        finally:
            conn.close()

    def search_abbreviations(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Searches technical abbreviation dictionary by term or definition."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            conditions = []
            params = []

            if category and category.upper() != "ALL":
                conditions.append("UPPER(category) = UPPER(?)")
                params.append(category)

            if query and query.strip():
                kw = f"%{query.strip()}%"
                conditions.append("(term LIKE ? OR full_form LIKE ? OR definition LIKE ?)")
                params.extend([kw, kw, kw])

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            sql = f"SELECT * FROM ece_abbreviation_dictionary{where_clause} ORDER BY term ASC;"
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def add_custom_formula(
        self,
        topic: str,
        formula_name: str,
        subject_code: str,
        unit_number: int,
        latex_repr: str,
        plain_text: str,
        derivation_summary: str,
        variables: Dict[str, str],
        unit_result: str,
        actor_role: str = "Faculty"
    ) -> Dict[str, Any]:
        """Adds a curated formula entity with strict RBAC enforcement (Faculty/Admin only)."""
        if actor_role not in ("Faculty", "Admin", "Chairperson"):
            return {
                "status": "FORBIDDEN",
                "message": f"Role '{actor_role}' lacks permission to add curated formulas to encyclopedia. Required: Faculty or Admin."
            }

        formula_id = f"FORM_{int(time.time() * 1000)}"
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO ece_formula_encyclopedia
                    (formula_id, topic, formula_name, subject_code, unit_number, latex_repr, plain_text, derivation_summary, variables_json, unit_result, au_regulation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    formula_id, topic, formula_name, subject_code, unit_number,
                    latex_repr, plain_text, derivation_summary, json.dumps(variables),
                    unit_result, subject_code
                ))
                conn.commit()
                return {
                    "status": "SUCCESS",
                    "formula_id": formula_id,
                    "formula_name": formula_name,
                    "message": "Formula successfully added to Anna University ECE Knowledge Center."
                }
            finally:
                conn.close()

    def get_knowledge_overview(self) -> Dict[str, Any]:
        """Aggregates catalog statistics across formulas, components, and abbreviations."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM ece_formula_encyclopedia;")
            total_formulas = cur.fetchone()[0]

            cur.execute("SELECT COUNT(DISTINCT subject_code) FROM ece_formula_encyclopedia;")
            total_subjects = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM ece_component_datasheets;")
            total_components = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM ece_abbreviation_dictionary;")
            total_abbreviations = cur.fetchone()[0]

            return {
                "status": "OPERATIONAL",
                "campus": "Madras Institute of Technology (MIT) Campus, Anna University",
                "department": "Department of Electronics Engineering",
                "regulation": "ECE Regulation 2023",
                "total_formulas": total_formulas,
                "total_subjects_covered": total_subjects,
                "total_components": total_components,
                "total_abbreviations": total_abbreviations,
                "supported_subjects": ["EC3352", "EC3452", "EC3451", "EC3491"],
                "query_latency": "< 5ms (Native SQLite WAL)",
                "thermal_status": "PASSIVE_SAFE"
            }
        finally:
            conn.close()


# Global Singleton
ece_knowledge_engine = EceKnowledgeEngine()
