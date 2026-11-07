"""
========================================================================================
VoltCore Apex Academia - Phase 13 Test Suite: Multi-Instrument DSO Synchronization,
Interactive Berkeley SPICE Netlist Editor & Anna University ECE Regulation 2023 Integration
========================================================================================
Platform Lead & Senior Systems Architect: Ashok Kumar A
Senior Analog IC Design Specialist • Department of Electronics Engineering
Host Profile: HP Victus 15-fa2xxx (LAPTOP-3NEGBVLE) • Passive CPU Target (<5%)
========================================================================================
"""

import os
import re
import json
import sqlite3
import pytest
from backend.analog_mna_engine import (
    Circuit,
    Resistor,
    Capacitor,
    Inductor,
    VoltageSource,
    CurrentSource,
    Diode,
    BJT,
    MOSFET,
    NonLinearMNASolver,
    AnalogMNAEngine,
    analog_mna_engine,
    parse_spice_value,
    parse_source_spec,
    parse_spice_netlist,
    circuit_to_spice_netlist,
    SPICE_SCALE_FACTORS
)


class TestPhase13SpiceNetlistParser:
    """Verifies Berkeley SPICE (.cir) metric scale factors and token parsing."""

    def test_spice_value_metric_suffixes(self):
        """Validates standard SPICE engineering suffixes (T, G, MEG, K, M, U, N, P, F)."""
        assert parse_spice_value("1k") == pytest.approx(1000.0)
        assert parse_spice_value("1.5k") == pytest.approx(1500.0)
        assert parse_spice_value("47kOhm") == pytest.approx(47000.0)
        assert parse_spice_value("10u") == pytest.approx(1e-5)
        assert parse_spice_value("10uF") == pytest.approx(1e-5)
        assert parse_spice_value("100n") == pytest.approx(1e-7)
        assert parse_spice_value("22p") == pytest.approx(22e-12)
        assert parse_spice_value("5V") == pytest.approx(5.0)
        assert parse_spice_value("1000") == pytest.approx(1000.0)
        assert parse_spice_value("1e-6") == pytest.approx(1e-6)
        assert parse_spice_value("0.025") == pytest.approx(0.025)

    def test_spice_meg_vs_milli_distinction(self):
        """Validates critical Berkeley SPICE convention: M is milli (1e-3), MEG is mega (1e6)."""
        assert parse_spice_value("10m") == pytest.approx(0.01)
        assert parse_spice_value("10mH") == pytest.approx(0.01)
        assert parse_spice_value("10MEG") == pytest.approx(10e6)
        assert parse_spice_value("2.2meg") == pytest.approx(2.2e6)

    def test_parse_source_spec_variations(self):
        """Verifies parsing of DC, SINE, STEP, and PULSE voltage specifications."""
        # SINE
        wtype, ampl, freq, offset = parse_source_spec(["SIN(0", "5", "1000)"])
        assert wtype == "SINE"
        assert ampl == pytest.approx(5.0)
        assert freq == pytest.approx(1000.0)
        assert offset == pytest.approx(0.0)

        # STEP
        wtype, ampl, freq, offset = parse_source_spec(["STEP", "0", "5"])
        assert wtype == "STEP"
        assert ampl == pytest.approx(5.0)

        # DC
        wtype, ampl, freq, offset = parse_source_spec(["DC", "10.0"])
        assert wtype == "DC"
        assert ampl == pytest.approx(10.0)

        # Bare number DC
        wtype, ampl, freq, offset = parse_source_spec(["3.3"])
        assert wtype == "DC"
        assert ampl == pytest.approx(3.3)

    def test_parse_complete_spice_deck(self):
        """Verifies parsing a multi-component Berkeley SPICE netlist deck."""
        netlist = """* VoltCore Academic Low-Pass Filter
V1 IN 0 STEP 0 5
R1 IN OUT 1k
C1 OUT 0 1u
.tran 20u 3m
.end
"""
        ckt, meta = parse_spice_netlist(netlist)
        assert ckt.title == "VoltCore Academic Low-Pass Filter"
        assert len(ckt.components) == 3
        assert ckt.num_nodes() == 2
        assert meta["analysis_type"] == "TRANSIENT"
        assert meta["t_step"] == pytest.approx(20e-6)
        assert meta["t_stop"] == pytest.approx(3e-3)


class TestPhase13SpiceSimulationEngine:
    """Verifies executing MNA simulations from raw Berkeley SPICE netlists."""

    def test_simulate_spice_netlist_rc_step(self):
        """Verifies transient MNA simulation directly from SPICE text."""
        netlist = """* RC Charging Step Circuit
V1 IN 0 STEP 0 5
R1 IN OUT 1k
C1 OUT 0 1u
.tran 20u 3m
.end
"""
        res = analog_mna_engine.simulate_spice_netlist(netlist)
        assert res["status"] == "SUCCESS"
        assert res["total_steps"] > 100
        assert "OUT" in res["trajectories"]
        assert "IN" in res["trajectories"]

        # Final voltage after 3tau (3 ms / 1 ms = 3tau) should be ~4.75 V
        final_vout = res["trajectories"]["OUT"][-1]
        assert 4.70 <= final_vout <= 4.80

    def test_simulate_spice_netlist_diode_rectifier(self):
        """Verifies non-linear Newton-Raphson MNA simulation on SPICE diode rectifier."""
        netlist = """* Diode Half-Wave Rectifier
V1 IN 0 SIN(0 5 1000)
D1 IN OUT 1N4148
RL OUT 0 1k
C1 OUT 0 10u
.tran 20u 3m
.end
"""
        res = analog_mna_engine.simulate_spice_netlist(netlist)
        assert res["status"] == "SUCCESS"
        assert "OUT" in res["trajectories"]
        max_vout = max(res["trajectories"]["OUT"])
        # Forward drop across diode reduces 5V peak to ~4.2 - 4.4V
        assert 4.0 <= max_vout <= 4.6

    def test_circuit_to_spice_serialization_roundtrip(self):
        """Verifies serialization of a Circuit instance to SPICE syntax and re-parsing."""
        ckt = Circuit("Audio BJT Preamplifier")
        ckt.add_voltage_source("VCC", "VCC", "0", dc_val=10.0)
        ckt.add_resistor("R1", "VCC", "BASE", 47000.0)
        ckt.add_resistor("R2", "BASE", "0", 10000.0)
        ckt.add_resistor("RC", "VCC", "COLL", 2200.0)
        ckt.add_resistor("RE", "EMIT", "0", 680.0)
        ckt.add_bjt("Q1", "COLL", "BASE", "EMIT")

        spice_text = circuit_to_spice_netlist(ckt, t_step=10e-6, t_stop=3e-3)
        assert "Q1 COLL BASE EMIT" in spice_text
        assert "R1 VCC BASE 47000" in spice_text
        assert ".tran" in spice_text
        assert ".end" in spice_text

        # Re-parse serialized text
        re_ckt, meta = parse_spice_netlist(spice_text)
        assert len(re_ckt.components) == len(ckt.components)
        assert re_ckt.num_nodes() == ckt.num_nodes()


class TestPhase13CourseLabDataMapping:
    """Verifies Anna University Regulation 2023 EC23C03 laboratory curriculum integration."""

    def test_ec23c03_catalog_expansion(self):
        """Verifies EC23C03 includes all four pre-configured Anna University lab exercises."""
        lab_data_path = os.path.join(
            os.path.dirname(__file__), "..", "src", "data", "course_lab_data.ts"
        )
        with open(lab_data_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check all 4 lab IDs are present in EC23C03
        assert "EC23C03_LAB1" in content
        assert "EC23C03_LAB2" in content
        assert "EC23C03_LAB3" in content
        assert "EC23C03_LAB4" in content

        # Check titles
        assert "BJT Common-Emitter Transistor Small-Signal Voltage Gain & Bias Stability" in content
        assert "NMOS/CMOS Digital Inverter Switching Transient & Propagation Delay" in content
        assert "2nd-Order Series & Parallel RLC Transient Step Resonator & Damping Factor" in content

    def test_mna_config_bindings_in_lab_catalog(self):
        """Verifies mnaConfig bindings exist for the EC23C03 laboratory modules."""
        lab_data_path = os.path.join(
            os.path.dirname(__file__), "..", "src", "data", "course_lab_data.ts"
        )
        with open(lab_data_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "bjt_ce_amplifier" in content
        assert "mosfet_inverter" in content
        assert "rlc_resonance" in content
        assert "diode_rectifier" in content
        assert "mnaConfig:" in content
        assert "spiceNetlistTemplate:" in content


class TestPhase13MultiInstrumentTelemetry:
    """Verifies cross-instrument telemetry and SQLite WAL history persistence."""

    def test_mna_waveform_telemetry_schema(self):
        """Verifies payload structure consumed by VirtualOscilloscope.jsx."""
        netlist = """* Oscilloscope Sync Test
V1 IN 0 STEP 0 5
R1 IN OUT 1k
C1 OUT 0 1u
.tran 20u 3m
.end
"""
        res = analog_mna_engine.simulate_spice_netlist(netlist)
        t_pts = res["time_points"]
        vin = res["trajectories"]["IN"]
        vout = res["trajectories"]["OUT"]

        # Mock payload matching voltcore:mna-waveform custom event
        payload = {
            "tool": "Non-Linear MNA Analog Workbench",
            "presetName": "RC Filter",
            "timePoints": t_pts,
            "vinCurve": vin,
            "voutCurve": vout
        }

        assert len(payload["timePoints"]) == len(payload["vinCurve"])
        assert len(payload["vinCurve"]) == len(payload["voutCurve"])
        assert payload["vinCurve"][-1] == pytest.approx(5.0)
        assert 4.70 <= payload["voutCurve"][-1] <= 4.80

    def test_sqlite_wal_simulation_history_durability(self):
        """Verifies simulation run audit records are saved to SQLite WAL table."""
        history = analog_mna_engine.get_simulation_history(limit=5)
        assert isinstance(history, list)
        if len(history) > 0:
            rec = history[0]
            assert "simulation_id" in rec
            assert "circuit_name" in rec
            assert "analysis_type" in rec
            assert "cpu_time_ms" in rec
            assert rec["simulation_id"].startswith("SIM_")
