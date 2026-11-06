"""
========================================================================================
VoltCore Apex Academia - Unit Tests for Phase H: Practical Laboratory Learning
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
========================================================================================
"""

import os
import pytest
import tempfile
from backend.practical_laboratory_engine import PracticalLaboratoryEngine, COMPONENT_PINOUT_CATALOG, ANNA_UNIV_ECE_LABS


@pytest.fixture
def engine():
    """Provides a fresh isolated instance of PracticalLaboratoryEngine with temporary SQLite DB."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_lab_telemetry.db")
    eng = PracticalLaboratoryEngine(db_path=db_path)
    yield eng


# =========================================================================
# Feature 281: Virtual Breadboard Connection Analyzer
# =========================================================================
def test_breadboard_connection_rules(engine):
    # Same column in top bank (A12 and C12) -> Connected
    conn1 = engine.validate_breadboard_connection("A12", "C12")
    assert conn1["is_connected"] is True

    # Same column straddling central trough (C12 and G12) -> Isolated by trough
    conn2 = engine.validate_breadboard_connection("C12", "G12")
    assert conn2["is_connected"] is False
    assert "central IC trough" in conn2["description"]

    # Different columns (A12 and A13) -> Isolated
    conn3 = engine.validate_breadboard_connection("A12", "A13")
    assert conn3["is_connected"] is False

    # Power rail continuity
    conn_pwr = engine.validate_breadboard_connection("TOP_RED", "TOP_RED")
    assert conn_pwr["is_connected"] is True


# =========================================================================
# Feature 282: Component Identification & Pinout
# =========================================================================
def test_component_identification(engine):
    bc547 = engine.get_component_pinout("BC547")
    assert bc547["package"] == "TO-92"
    assert "Collector (C)" in bc547["pins"][1]
    assert "Base (B)" in bc547["pins"][2]
    assert "Emitter (E)" in bc547["pins"][3]

    # Quiz verification
    guess_res = engine.verify_pin_identification("BC547", 1, "Collector")
    assert guess_res["is_correct"] is True

    with pytest.raises(ValueError):
        engine.get_component_pinout("UNKNOWN_PART")


# =========================================================================
# Feature 283: Resistor Colour Code Calculator (4, 5, 6-Band)
# =========================================================================
def test_resistor_color_code_4band(engine):
    # Brown (1), Black (0), Red (10^2), Gold (5%) -> 10 * 100 = 1000 ohms = 1k
    res = engine.calculate_resistor_value(["BROWN", "BLACK", "RED", "GOLD"])
    assert res["nominal_resistance_ohms"] == 1000.0
    assert "1 kΩ" in res["formatted_resistance"] or "1.00 kΩ" in res["formatted_resistance"]
    assert res["tolerance_percent"] == 5.0
    assert res["min_resistance_ohms"] == 950.0
    assert res["max_resistance_ohms"] == 1050.0


def test_resistor_color_code_5_and_6band(engine):
    # 5-Band: Yellow (4), Violet (7), Black (0), Brown (10^1), Brown (1%) -> 470 * 10 = 4700 ohms = 4.7k
    res5 = engine.calculate_resistor_value(["YELLOW", "VIOLET", "BLACK", "BROWN", "BROWN"])
    assert res5["nominal_resistance_ohms"] == 4700.0
    assert res5["tolerance_percent"] == 1.0

    # 6-Band with Temp Coeff: Brown (1), Black (0), Black (0), Orange (10^3), Blue (0.25%), Red (50 ppm)
    # 100 * 1000 = 100k
    res6 = engine.calculate_resistor_value(["BROWN", "BLACK", "BLACK", "ORANGE", "BLUE", "RED"])
    assert res6["nominal_resistance_ohms"] == 100000.0
    assert res6["temp_coeff_ppm_k"] == 50

    with pytest.raises(ValueError):
        engine.calculate_resistor_value(["BROWN", "BLACK"])  # Less than 4 bands


# =========================================================================
# Feature 284: Component Selection Guide & Derating
# =========================================================================
def test_component_rating_selection(engine):
    # Operating at 12V, 0.05A (50mA) -> P = 0.6W. Derating 2.0x -> 1.2W required -> selects 2.0W standard
    sel = engine.select_component_rating(
        component_type="Resistor",
        operating_voltage_v=12.0,
        operating_current_a=0.05,
        safety_derating_factor=2.0
    )
    assert sel["power_dissipated_w"] == pytest.approx(0.6, abs=0.01)
    assert sel["recommended_resistor_wattage_w"] == 2.0
    assert sel["recommended_capacitor_voltage_v"] >= 18  # 12 * 1.5


# =========================================================================
# Feature 285: Circuit Troubleshooting Decision Tree
# =========================================================================
def test_circuit_troubleshooting(engine):
    diag = engine.diagnose_circuit_fault(["IC is burning hot to touch"])
    assert diag["priority"] == "HIGH"
    assert any("Reverse Polarity" in c or "inverted" in c for c in diag["diagnosed_root_causes"])

    diag_clip = engine.diagnose_circuit_fault(["Output waveform is clipping on bottom"])
    assert any("Q-point" in c for c in diag_clip["diagnosed_root_causes"])


# =========================================================================
# Feature 286: Laboratory Safety Protocols
# =========================================================================
def test_safety_checklist_evaluation(engine):
    safe_answers = {
        "power_off_while_wiring": True,
        "polarity_verified": True,
        "esd_strap_worn": True,
        "current_limit_set": True,
        "eyewear_worn": True
    }
    eval_safe = engine.evaluate_safety_checklist(safe_answers)
    assert eval_safe["is_safe_to_energize"] is True
    assert eval_safe["passed_percentage"] == 100.0

    unsafe_answers = {"power_off_while_wiring": False, "polarity_verified": True}
    eval_unsafe = engine.evaluate_safety_checklist(unsafe_answers)
    assert eval_unsafe["is_safe_to_energize"] is False


# =========================================================================
# Feature 287: Practical Experiment Preparation Guide
# =========================================================================
def test_experiment_guides(engine):
    guide = engine.get_experiment_guide("EC3361")
    assert "Electronic Devices & Circuits" in guide["title"]
    assert len(guide["experiments"]) >= 5

    with pytest.raises(ValueError):
        engine.get_experiment_guide("NON_EXISTENT_LAB")


# =========================================================================
# Feature 288: Experiment Observation Error Calculator
# =========================================================================
def test_observation_error_calculator(engine):
    # Measured 4.8V vs Theory 5.0V -> Error = (0.2 / 5.0) * 100 = 4.0%
    err = engine.calculate_observation_error(measured_val=4.8, theoretical_val=5.0)
    assert err["error_percent"] == 4.0
    assert err["is_acceptable"] is True

    # High error reading
    err_high = engine.calculate_observation_error(measured_val=2.0, theoretical_val=5.0)
    assert err_high["error_percent"] == 60.0
    assert err_high["is_acceptable"] is False


# =========================================================================
# Feature 289: Virtual Instrument Reading Practice
# =========================================================================
def test_virtual_oscilloscope_reading(engine):
    # Vertical: 4.0 divisions @ 0.5 V/div, 1X probe -> V_pp = 2.0V
    # Horizontal: 5.0 divisions @ 0.2 ms/div -> Period = 1.0 ms -> Freq = 1000 Hz
    scope = engine.calculate_scope_measurements(
        div_y=4.0,
        volts_per_div=0.5,
        div_x=5.0,
        time_per_div_ms=0.2,
        probe_attenuation=1
    )
    assert scope["v_pp_volts"] == 2.0
    assert scope["v_amplitude_volts"] == 1.0
    assert scope["period_ms"] == 1.0
    assert scope["frequency_hz"] == 1000.0

    with pytest.raises(ValueError):
        engine.calculate_scope_measurements(div_y=4.0, volts_per_div=-1.0, div_x=5.0, time_per_div_ms=0.2)


# =========================================================================
# Feature 290: Lab Report Generator
# =========================================================================
def test_lab_report_generation(engine):
    report_md = engine.generate_laboratory_report(
        student_id="2023MITEC042",
        student_name="Ashok Kumar A",
        roll_no="2023MITEC042",
        exp_code="EC3361-EXP02",
        exp_title="BJT Common Emitter Characteristics",
        aim="To plot the input and output characteristics of a Common Emitter BJT amplifier.",
        apparatus=["BC547 Transistor", "Dual RPS (0-30V)", "Multimeters", "Decade Resistance Box"],
        formulae_md="h_fe = delta(I_C) / delta(I_B) at constant V_CE",
        results_summary="Input resistance h_ie = 1.5 kΩ, Current gain h_fe = 185."
    )
    assert "ANNA UNIVERSITY" in report_md
    assert "Ashok Kumar A" in report_md
    assert "BC547 Transistor" in report_md


# =========================================================================
# Persistence: SQLite WAL Integration
# =========================================================================
def test_lab_persistence(engine):
    obs_id = engine.save_observation(
        student_id="2023MITEC042",
        exp_code="EC3361-EXP01",
        exp_title="Zener Regulator Test",
        input_params={"Vin": 12.0, "Rz": 220},
        measured={"Vout": 5.12},
        theoretical={"Vout": 5.10},
        error_percent=0.39
    )
    assert obs_id > 0

    obs_list = engine.get_observations("2023MITEC042")
    assert len(obs_list) >= 1
    assert any(o["exp_code"] == "EC3361-EXP01" for o in obs_list)

    rep_id = engine.save_report(
        student_id="2023MITEC042",
        exp_code="EC3361-EXP01",
        report_markdown="# Sample Report Content",
        status="SUBMITTED"
    )
    assert rep_id > 0
