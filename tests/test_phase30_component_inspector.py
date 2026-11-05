"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 30 (Smart PCB, SMD & Component Inspector Lab)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase30_component_inspector.py
Target Facility: Lab 304 (Hardware Prototyping & Inspection Suite, MIT Campus, Chromepet)
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import pytest
from backend.component_inspector_engine import (
    ComponentInspectorEngine,
    DEFAULT_SMD_CATALOG,
    DEFAULT_IC_THERMAL_CATALOG
)


@pytest.fixture
def test_engine(tmp_path):
    """Provides an isolated ComponentInspectorEngine backed by a temporary SQLite WAL DB."""
    db_file = str(tmp_path / "test_component_inspector.db")
    engine = ComponentInspectorEngine(db_path=db_file)
    return engine


def test_engine_initialization_and_wal(test_engine):
    """Verifies that SQLite tables are created with WAL mode and catalogs are seeded."""
    conn = test_engine._get_connection()
    try:
        cur = conn.execute("PRAGMA journal_mode;")
        journal_mode = cur.fetchone()[0].upper()
        assert journal_mode == "WAL", f"Expected WAL mode, got {journal_mode}"

        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        assert "component_inspection_history" in tables
        assert "saved_pcb_trace_calculations" in tables
        assert "smd_marking_catalog" in tables
        assert "ic_package_thermal_catalog" in tables

        # Verify seeded catalog counts
        cur = conn.execute("SELECT COUNT(*) FROM smd_marking_catalog;")
        assert cur.fetchone()[0] == len(DEFAULT_SMD_CATALOG)

        cur = conn.execute("SELECT COUNT(*) FROM ic_package_thermal_catalog;")
        assert cur.fetchone()[0] == len(DEFAULT_IC_THERMAL_CATALOG)
    finally:
        conn.close()


def test_axial_resistor_4band_decoding(test_engine):
    """Validates 4-band axial resistor decoding for standard resistance values and tolerances."""
    # 1. Yellow Violet Red Gold = 47 * 10^2 = 4700 Ohm (4.70 kOhm) +/- 5%
    r1 = test_engine.decode_axial_resistor(["yellow", "violet", "red", "gold"])
    assert r1["status"] == "SUCCESS"
    assert r1["band_count"] == 4
    assert r1["resistance_ohms"] == 4700.0
    assert "4.7" in r1["formatted"]
    assert r1["tolerance_pct"] == 5.0
    assert r1["min_resistance_ohms"] == 4465.0
    assert r1["max_resistance_ohms"] == 4935.0
    assert r1["tcr_ppm_k"] is None

    # 2. Brown Black Red Gold = 10 * 10^2 = 1000 Ohm (1.00 kOhm) +/- 5%
    r2 = test_engine.decode_axial_resistor(["brown", "black", "red", "gold"])
    assert r2["status"] == "SUCCESS"
    assert r2["resistance_ohms"] == 1000.0
    assert "1" in r2["formatted"]
    assert r2["tolerance_pct"] == 5.0

    # 3. Invalid color inputs
    r_err = test_engine.decode_axial_resistor(["gold", "silver", "red", "gold"])
    assert r_err["status"] == "ERROR"


def test_axial_resistor_5band_decoding(test_engine):
    """Validates 5-band axial resistor decoding with 3 significant digits."""
    # Brown Black Black Red Brown = 100 * 10^2 = 10,000 Ohm (10 kOhm) +/- 1%
    r = test_engine.decode_axial_resistor(["brown", "black", "black", "red", "brown"])
    assert r["status"] == "SUCCESS"
    assert r["band_count"] == 5
    assert r["digits_value"] == 100
    assert r["multiplier"] == 100.0
    assert r["resistance_ohms"] == 10000.0
    assert "10" in r["formatted"]
    assert r["tolerance_pct"] == 1.0
    assert r["min_resistance_ohms"] == 9900.0
    assert r["max_resistance_ohms"] == 10100.0

    # Red Red Black Brown Brown = 220 * 10^1 = 2200 Ohm (2.20 kOhm) +/- 1%
    r2 = test_engine.decode_axial_resistor(["red", "red", "black", "brown", "brown"])
    assert r2["status"] == "SUCCESS"
    assert r2["resistance_ohms"] == 2200.0
    assert r2["tolerance_pct"] == 1.0


def test_axial_resistor_6band_decoding_with_tcr(test_engine):
    """Validates 6-band axial resistor decoding with TCR (ppm/K) temperature coefficients."""
    # Orange Orange Black Brown Brown Red = 330 * 10^1 = 3300 Ohm (3.30 kOhm) +/- 1%, TCR = 50 ppm/K (Red)
    r = test_engine.decode_axial_resistor(["orange", "orange", "black", "brown", "brown", "red"])
    assert r["status"] == "SUCCESS"
    assert r["band_count"] == 6
    assert r["resistance_ohms"] == 3300.0
    assert r["tolerance_pct"] == 1.0
    assert r["tcr_ppm_k"] == 50

    # Blue Grey Black Black Brown Brown = 680 * 1 = 680 Ohm +/- 1%, TCR = 100 ppm/K (Brown)
    r2 = test_engine.decode_axial_resistor(["blue", "grey", "black", "black", "brown", "brown"])
    assert r2["status"] == "SUCCESS"
    assert r2["resistance_ohms"] == 680.0
    assert r2["tcr_ppm_k"] == 100


def test_smd_resistor_3digit_and_4digit_decoding(test_engine):
    """Validates SMD 3-digit and 4-digit resistor markings including zero-ohm jumpers and 'R' notations."""
    # Standard 3-digit: 472 -> 4700 Ohm
    s1 = test_engine.decode_smd_marking("472", "RESISTOR")
    assert s1["status"] == "SUCCESS"
    assert s1["nominal_value"] == 4700.0
    assert "4.7" in s1["value_formatted"]
    assert s1["tolerance_pct"] == 5.0

    # Standard 3-digit: 103 -> 10000 Ohm
    s2 = test_engine.decode_smd_marking("103", "RESISTOR")
    assert s2["nominal_value"] == 10000.0

    # Zero-ohm jumper: 000
    s_jump = test_engine.decode_smd_marking("000", "RESISTOR")
    assert s_jump["nominal_value"] == 0.0
    assert "Jumper" in s_jump["value_formatted"] or "0" in s_jump["value_formatted"]

    # Decimal R-notation: 4R7 -> 4.7 Ohm
    s_r1 = test_engine.decode_smd_marking("4R7", "RESISTOR")
    assert s_r1["nominal_value"] == 4.7

    # Precision 4-digit: 1001 -> 100 * 10^1 = 1000 Ohm (1.00 kOhm) +/- 1%
    s_4d = test_engine.decode_smd_marking("1001", "RESISTOR")
    assert s_4d["nominal_value"] == 1000.0
    assert s_4d["tolerance_pct"] == 1.0

    # Precision 4-digit: 4702 -> 470 * 10^2 = 47000 Ohm (47.0 kOhm)
    s_4d2 = test_engine.decode_smd_marking("4702", "RESISTOR")
    assert s_4d2["nominal_value"] == 47000.0
    assert s_4d2["tolerance_pct"] == 1.0


def test_smd_eia96_and_capacitor_decoding(test_engine):
    """Validates EIA-96 1% precision codes and 3-digit ceramic capacitor markings."""
    # EIA-96: 01A -> 100 * 1 = 100 Ohm
    e1 = test_engine.decode_smd_marking("01A", "RESISTOR")
    assert e1["status"] == "SUCCESS"
    assert e1["standard"] == "EIA-96"
    assert e1["nominal_value"] == 100.0

    # EIA-96: 01C -> 100 * 100 = 10000 Ohm (10 kOhm)
    e2 = test_engine.decode_smd_marking("01C", "RESISTOR")
    assert e2["nominal_value"] == 10000.0

    # EIA-96: 68X -> 499 * 0.1 = 49.9 Ohm (High-speed Ethernet/USB)
    e3 = test_engine.decode_smd_marking("68X", "RESISTOR")
    assert e3["nominal_value"] == 49.9

    # SMD MLCC Capacitor: 104 -> 10 * 10^4 pF = 100,000 pF = 100 nF (0.1 uF)
    c1 = test_engine.decode_smd_marking("104", "CAPACITOR")
    assert c1["status"] == "SUCCESS"
    assert c1["nominal_value"] == 100000.0
    assert "100" in c1["value_formatted"] and "nF" in c1["value_formatted"]

    # SMD MLCC Capacitor: 223 -> 22 * 10^3 pF = 22 nF
    c2 = test_engine.decode_smd_marking("223", "CAPACITOR")
    assert c2["nominal_value"] == 22000.0
    assert "22 nF" in c2["value_formatted"]


def test_ipc2221_pcb_trace_width_calculation(test_engine):
    """Validates IPC-2221 trace width sizing, layer difference (external vs internal), and resistance."""
    # Continuous current 2.5A, 10 deg C temp rise, 1.0 oz copper
    ext_trace = test_engine.calculate_pcb_trace_width(
        current_a=2.5,
        temp_rise_c=10.0,
        copper_oz=1.0,
        trace_type="external",
        trace_length_cm=10.0
    )
    assert ext_trace["status"] == "SUCCESS"
    assert ext_trace["trace_width_mils"] > 0
    assert ext_trace["trace_width_mm"] > 0
    assert ext_trace["resistance_ohms"] > 0
    assert ext_trace["voltage_drop_v"] > 0
    assert ext_trace["power_loss_w"] > 0
    # ~41.85 mils
    assert 35.0 < ext_trace["trace_width_mils"] < 50.0

    # Internal layer has lower heat dissipation (k=0.024 vs 0.048), so requires wider trace
    int_trace = test_engine.calculate_pcb_trace_width(
        current_a=2.5,
        temp_rise_c=10.0,
        copper_oz=1.0,
        trace_type="internal",
        trace_length_cm=10.0
    )
    assert int_trace["trace_width_mils"] > ext_trace["trace_width_mils"]


def test_ic_package_thermal_dissipation_safety(test_engine):
    """Validates IC silicon junction temperature TJ = TA + (PD * Theta_JA) and status thresholds."""
    # 1. DIP-8 (Theta_JA = 100 deg C/W), 0.5W, 25 deg C ambient -> TJ = 25 + 50 = 75 deg C (OPTIMAL)
    th1 = test_engine.evaluate_ic_thermal_dissipation("DIP-8", power_watts=0.5, ambient_temp_c=25.0)
    assert th1["status"] == "SUCCESS"
    assert th1["junction_temp_c"] == 75.0
    assert th1["thermal_status"] == "OPTIMAL"
    assert th1["heatsink_required"] is False

    # 2. TO-220 (Theta_JA = 62.5 deg C/W), 2.0W, 25 deg C ambient -> TJ = 25 + 125 = 150 deg C (WARNING/CRITICAL)
    th2 = test_engine.evaluate_ic_thermal_dissipation("TO-220", power_watts=2.0, ambient_temp_c=25.0)
    assert th2["status"] == "SUCCESS"
    assert th2["junction_temp_c"] == 150.0
    assert th2["thermal_status"] in ("WARNING", "CRITICAL_HAZARD")
    assert th2["heatsink_required"] is True
    assert th2["recommended_heatsink_theta_sa"] is not None

    # 3. SOT-23 (Theta_JA = 250 deg C/W), 0.5W, 25 deg C ambient -> TJ = 25 + 125 = 150 deg C (CRITICAL_HAZARD, max 125)
    th3 = test_engine.evaluate_ic_thermal_dissipation("SOT-23", power_watts=0.5, ambient_temp_c=25.0)
    assert th3["junction_temp_c"] == 150.0
    assert th3["thermal_status"] == "CRITICAL_HAZARD"


def test_component_history_persistence_and_catalogs(test_engine):
    """Verifies that inspection history logs to SQLite WAL and catalogs can be queried."""
    # Log an axial decoding
    test_engine.decode_axial_resistor(["brown", "black", "orange", "gold"])
    # Log an SMD decoding
    test_engine.decode_smd_marking("103", "RESISTOR")
    # Log a PCB trace
    test_engine.calculate_pcb_trace_width(current_a=1.5, temp_rise_c=10.0)

    history = test_engine.get_inspection_history(limit=10)
    assert history["status"] == "SUCCESS"
    assert history["count"] >= 3

    catalogs = test_engine.get_catalogs()
    assert catalogs["status"] == "SUCCESS"
    assert len(catalogs["smd_markings"]) >= 10
    assert len(catalogs["ic_packages"]) >= 7
    assert "black" in catalogs["color_digits"]


def test_privacy_invariants_no_credential_leakage():
    """
    Scans Phase 30 codebase files to guarantee zero hardcoded private admin credentials.
    Strictly adheres to HP Victus Data Privacy Policy (Anna University / MIT Campus).
    """
    forbidden_tokens = [
        "ashokkumar2008313" + "@gmail.com",
        "9597382878"
    ]
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    phase30_files = [
        os.path.join(repo_root, "backend", "component_inspector_engine.py"),
        os.path.join(repo_root, "src", "components", "ComponentInspectorHub.jsx"),
        os.path.join(repo_root, "src", "pages", "component-inspector.astro"),
        os.path.join(repo_root, "attendance_server.py")
    ]

    for fpath in phase30_files:
        if os.path.isfile(fpath):
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                for token in forbidden_tokens:
                    assert token not in content, f"Privacy violation: {token} leaked in {fpath}"
