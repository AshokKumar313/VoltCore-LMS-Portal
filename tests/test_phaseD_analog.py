"""
========================================================================================
VoltCore Apex Academia - Phase D Test Suite: Analog Electronics & Semiconductors
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU usage.
========================================================================================
"""

import os
import pytest
import sqlite3
from backend.analog_electronics_engine import (
    AnalogElectronicsEngine,
    SEMICONDUCTOR_MATERIALS,
    BJT_CONFIGURATIONS
)


@pytest.fixture
def engine(tmp_path):
    """Instantiate AnalogElectronicsEngine with an isolated temporary SQLite WAL database."""
    db_file = str(tmp_path / "test_analog.db")
    return AnalogElectronicsEngine(db_path=db_file)


def test_analog_engine_wal_mode(engine):
    """Verify that SQLite tables for analog simulations and studies are initialized in WAL mode."""
    conn = sqlite3.connect(engine.db_path)
    try:
        cur = conn.execute("PRAGMA journal_mode;")
        mode = cur.fetchone()[0]
        assert mode.lower() == "wal", f"Expected WAL mode, got {mode}"

        cur = conn.execute("""
            SELECT name FROM sqlite_master WHERE type='table'
            AND name IN ('analog_circuit_simulations', 'semiconductor_studies');
        """)
        tables = {row[0] for row in cur.fetchall()}
        assert "analog_circuit_simulations" in tables
        assert "semiconductor_studies" in tables
    finally:
        conn.close()


def test_calculate_pn_junction(engine):
    """Verify PN junction built-in potential, depletion width, and E-field (Feature 241)."""
    # Silicon standard junction
    si_res = engine.calculate_pn_junction(material="Silicon", na_cm3=1e16, nd_cm3=1e16)
    assert 0.65 <= si_res["built_in_potential_v"] <= 0.75
    assert si_res["depletion_width_um"] > 0
    assert si_res["peak_electric_field_kv_cm"] > 0
    assert si_res["junction_capacitance_pf"] > 0

    # Germanium junction (lower Vbi due to smaller bandgap)
    ge_res = engine.calculate_pn_junction(material="Germanium", na_cm3=1e16, nd_cm3=1e16)
    assert ge_res["built_in_potential_v"] < si_res["built_in_potential_v"]

    # Reverse bias increases depletion width
    rev_res = engine.calculate_pn_junction(material="Silicon", na_cm3=1e16, nd_cm3=1e16, applied_voltage_v=-5.0)
    assert rev_res["depletion_width_um"] > si_res["depletion_width_um"]

    # Invalid material or non-positive doping
    with pytest.raises(ValueError):
        engine.calculate_pn_junction(material="Kryptonite")

    with pytest.raises(ValueError):
        engine.calculate_pn_junction(material="Silicon", na_cm3=-1e16)


def test_calculate_diode_iv(engine):
    """Verify Shockley diode equation and dynamic resistance (Feature 242)."""
    # Forward biased silicon diode at 0.7V
    fwd = engine.calculate_diode_iv(is_sat_a=1e-12, voltage_v=0.7)
    assert fwd["current_ma"] > 0
    assert fwd["dynamic_resistance_ohm"] > 0
    assert len(fwd["curve_points"]) > 10

    # Reverse biased diode
    rev = engine.calculate_diode_iv(is_sat_a=1e-12, voltage_v=-2.0)
    assert rev["current_ma"] <= 0


def test_design_zener_regulator(engine):
    """Verify Zener diode voltage regulator series resistor sizing and regulation (Feature 243)."""
    zener = engine.design_zener_regulator(
        vin_min_v=15.0,
        vin_max_v=18.0,
        vz_v=10.0,
        il_min_ma=5.0,
        il_max_ma=50.0,
        iz_min_ma=5.0,
        pz_max_w=1.5,
        rz_ohm=8.0
    )
    assert zener["valid_design"] is True
    assert zener["rs_min_ohm"] < zener["rs_max_ohm"]
    assert zener["recommended_rs_ohm"] > 0
    assert zener["line_regulation"] > 0
    assert zener["load_regulation_mv_per_ma"] < 0

    # Invalid: Vin_min <= Vz
    with pytest.raises(ValueError):
        engine.design_zener_regulator(vin_min_v=10.0, vz_v=12.0)


def test_compare_bjt_configurations(engine):
    """Verify BJT configuration matrix and current gain relationships (Feature 244)."""
    bjt = engine.compare_bjt_configurations(beta=100.0)
    assert bjt["beta"] == 100.0
    assert 0.99 <= bjt["alpha"] < 1.0
    assert bjt["gamma"] == 101.0
    assert "CE" in bjt["configurations"]
    assert "CB" in bjt["configurations"]
    assert "CC" in bjt["configurations"]
    assert bjt["configurations"]["CE"]["phase_shift_deg"] == 180
    assert bjt["configurations"]["CB"]["phase_shift_deg"] == 0

    with pytest.raises(ValueError):
        engine.compare_bjt_configurations(beta=-10)


def test_calculate_mosfet_iv(engine):
    """Verify MOSFET operating regions: Cutoff, Triode, and Saturation (Feature 245)."""
    # Cutoff: Vgs <= Vth
    cutoff = engine.calculate_mosfet_iv(vgs_v=0.5, vds_v=2.0, vth_v=1.0)
    assert cutoff["operating_region"] == "Cutoff"
    assert cutoff["drain_current_ma"] == 0.0

    # Triode: Vgs > Vth and Vds < Vov
    triode = engine.calculate_mosfet_iv(vgs_v=3.0, vds_v=0.5, vth_v=1.0)
    assert triode["operating_region"] == "Triode (Linear)"
    assert triode["drain_current_ma"] > 0.0

    # Saturation: Vgs > Vth and Vds >= Vov
    sat = engine.calculate_mosfet_iv(vgs_v=3.0, vds_v=3.0, vth_v=1.0)
    assert sat["operating_region"] == "Saturation (Active)"
    assert sat["drain_current_ma"] > 0.0
    assert sat["transconductance_gm_ms"] > 0.0
    assert len(sat["vds_sweep"]) == 51


def test_calculate_ce_amplifier(engine):
    """Verify BJT Common Emitter small-signal AC gain and input/output impedances (Feature 246)."""
    bypassed = engine.calculate_ce_amplifier(ic_ma=2.0, beta=100.0, bypassed_emitter=True)
    assert bypassed["voltage_gain_av"] < -10.0  # Inverting high gain
    assert bypassed["transconductance_gm_ms"] > 0
    assert bypassed["input_impedance_rin_kohm"] > 0
    assert bypassed["lower_cutoff_fl_hz"] > 0

    unbypassed = engine.calculate_ce_amplifier(ic_ma=2.0, beta=100.0, bypassed_emitter=False)
    # Unbypassed emitter degeneration increases Rin and reduces magnitude of Av
    assert abs(unbypassed["voltage_gain_av"]) < abs(bypassed["voltage_gain_av"])
    assert unbypassed["input_impedance_rin_kohm"] > bypassed["input_impedance_rin_kohm"]


def test_calculate_opamp_circuit(engine):
    """Verify Inverting, Non-Inverting, Follower, Differential op-amp circuits and Slew Rate (Feature 247)."""
    # Inverting amplifier: Av = -Rf / Rin
    inv = engine.calculate_opamp_circuit(topology="inverting", rf_kohm=100.0, rin_kohm=10.0, vin_v=1.0)
    assert inv["ideal_gain"] == -10.0
    assert inv["vout_actual_v"] == -10.0
    assert inv["is_saturated"] is False

    # Saturation when input exceeds rail limit
    inv_sat = engine.calculate_opamp_circuit(topology="inverting", rf_kohm=100.0, rin_kohm=10.0, vin_v=5.0, v_supply_v=15.0)
    assert inv_sat["is_saturated"] is True
    assert inv_sat["vout_actual_v"] == -13.5  # 15V - 1.5V rail drop

    # Non-inverting amplifier: Av = 1 + Rf / Rin
    non_inv = engine.calculate_opamp_circuit(topology="non_inverting", rf_kohm=90.0, rin_kohm=10.0, vin_v=1.0)
    assert non_inv["ideal_gain"] == 10.0
    assert non_inv["vout_actual_v"] == 10.0

    # Voltage Follower: Av = 1
    follower = engine.calculate_opamp_circuit(topology="voltage_follower", vin_v=3.3)
    assert follower["ideal_gain"] == 1.0
    assert follower["vout_actual_v"] == 3.3

    # Differential amplifier
    diff = engine.calculate_opamp_circuit(topology="differential", rf_kohm=20.0, rin_kohm=10.0, vin_v=1.0, vin2_v=3.0)
    assert diff["ideal_gain"] == 2.0
    assert diff["vout_actual_v"] == 4.0  # 2 * (3.0 - 1.0)

    with pytest.raises(ValueError):
        engine.calculate_opamp_circuit(topology="unsupported_opamp")


def test_calculate_transient_response(engine):
    """Verify RC and RL circuit transient step responses and time constants (Feature 248)."""
    # RC circuit: tau = R * C = 10k * 1uF = 10ms
    rc = engine.calculate_transient_response(circuit_type="RC", r_kohm=10.0, c_uf=1.0, v_step_v=5.0)
    assert rc["time_constant_tau_ms"] == 10.0
    assert rc["settling_time_5tau_ms"] == 50.0
    assert len(rc["curve_points"]) == 21
    # At 5 tau, charging voltage should be > 99% of V_step
    assert rc["curve_points"][-1]["v_charge_v"] > 4.95

    # RL circuit: tau = L / R = 100mH / 1k = 0.1ms
    rl = engine.calculate_transient_response(circuit_type="RL", r_kohm=1.0, l_mh=100.0, v_step_v=5.0)
    assert rl["time_constant_tau_ms"] == 0.1

    with pytest.raises(ValueError):
        engine.calculate_transient_response(circuit_type="UNKNOWN")


def test_calculate_rlc_resonance(engine):
    """Verify Series and Parallel RLC resonance frequency, Q-factor, and damping (Feature 249)."""
    # Series RLC: R = 10 ohm, L = 100 uH, C = 10 nF
    # f0 = 1 / (2 * pi * sqrt(100e-6 * 10e-9)) = ~159.155 kHz
    res = engine.calculate_rlc_resonance(r_ohm=10.0, l_uh=100.0, c_nf=10.0, topology="series")
    assert 158.0 < res["resonant_freq_f0_khz"] < 161.0
    assert res["quality_factor_q"] > 0
    assert res["bandwidth_bw_khz"] > 0
    assert res["lower_cutoff_f1_khz"] < res["resonant_freq_f0_khz"] < res["upper_cutoff_f2_khz"]

    # Parallel RLC
    res_par = engine.calculate_rlc_resonance(r_ohm=1000.0, l_uh=100.0, c_nf=10.0, topology="parallel")
    assert res_par["quality_factor_q"] > 0

    with pytest.raises(ValueError):
        engine.calculate_rlc_resonance(r_ohm=0.0, l_uh=100.0, c_nf=10.0)


def test_compare_semiconductor_materials(engine):
    """Verify semiconductor material database and Baliga FOM calculations (Feature 250)."""
    comp = engine.compare_semiconductor_materials()
    assert comp["materials_count"] == 5
    mats = {m["symbol"]: m for m in comp["comparison"]}

    assert "Si" in mats
    assert "Ge" in mats
    assert "GaAs" in mats
    assert "GaN" in mats
    assert "4H-SiC" in mats

    # Bandgap assertions
    assert mats["Si"]["bandgap_ev"] == 1.12
    assert mats["Ge"]["bandgap_ev"] == 0.66
    assert mats["GaN"]["bandgap_ev"] == 3.4

    # Baliga FOM: GaN and SiC should vastly exceed Silicon (> 100x)
    assert mats["GaN"]["baliga_fom_normalized"] > 100.0
    assert mats["4H-SiC"]["baliga_fom_normalized"] > 100.0


def test_persistence_methods(engine):
    """Verify SQLite WAL simulation saving and retrieval."""
    sim = engine.save_simulation(
        student_id="2023MITEC042",
        circuit_type="BJT_CE_AMP",
        input_params={"ic_ma": 2.0, "beta": 100},
        computed_metrics={"gain_av": -125.4, "rin_kohm": 2.1}
    )
    assert sim["status"] == "success"
    assert sim["simulation_id"] > 0

    sims = engine.get_simulations("2023MITEC042")
    assert len(sims) >= 1
    assert sims[0]["circuit_type"] == "BJT_CE_AMP"
