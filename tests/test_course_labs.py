"""
========================================================================================
VoltCore Apex Academia - Unit Tests for Laboratory Simulators & Interactive Benchmarks
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead & Systems Architect: Ashok Kumar A
========================================================================================
"""

import pytest
import tempfile
import os
from backend.course_lab_engine import CourseLabEngine, COURSE_LAB_CATALOG_DATA


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


@pytest.fixture
def lab_engine(temp_db):
    return CourseLabEngine(db_path=temp_db)


def test_lab_catalog_validation(lab_engine):
    """Verify that all 4 priority courses have valid lab exercises with parameters and apparatus."""
    audit = lab_engine.validate_catalog()
    assert audit["valid"] is True, f"Validation errors: {audit.get('errors')}"
    assert audit["total_courses"] == 4
    assert audit["total_labs"] >= 5


def test_simulate_dsp_butterworth(lab_engine):
    """Verify Butterworth filter frequency response, cutoff attenuation, and Nyquist checking."""
    # 4th order lowpass at fc = 1000 Hz, fs = 16000 Hz
    sim = lab_engine.simulate_dsp_butterworth(fc=1000, fs=16000, order=4, gain=1.0)
    assert sim["is_nyquist_valid"] is True
    assert sim["nyquist_freq"] == 8000.0
    assert sim["roll_off_db_per_decade"] == -80  # -20 * 4 dB/decade
    
    # At cutoff, magnitude gain must be approx 1 / sqrt(2) = 0.7071 (-3.01 dB)
    assert abs(sim["mag_at_cutoff"] - 0.7071) < 0.005
    assert abs(sim["db_at_cutoff"] - (-3.01)) < 0.05


def test_simulate_device_iv(lab_engine):
    """Verify Shockley diode IV and MOSFET saturation characteristics."""
    # At room temperature 300K, VT approx 25.86 mV
    sim = lab_engine.simulate_device_iv(vf=0.65, temp_k=300, eta=1.0, vgs=3.3, vth=1.2, kn=20.0)
    assert 25.8 <= sim["vt_mv"] <= 25.9
    assert sim["diode_current_ma"] > 0
    assert sim["dynamic_rd_ohms"] > 0
    assert sim["is_conduction_active"] is True
    
    # MOSFET Vov = 3.3 - 1.2 = 2.1V, ID,sat = 0.5 * 20 * 2.1^2 = 44.1 mA
    assert sim["vov"] == 2.1
    assert abs(sim["mosfet_sat_id_ma"] - 44.1) < 0.1
    assert abs(sim["transconductance_gm_ma_v"] - 42.0) < 0.1


def test_simulate_laser_cavity(lab_engine):
    """Verify optical cavity stability g-parameters and longitudinal mode spacing."""
    # Confocal cavity: L = 0.5m, R1 = 0.5m, R2 = 0.5m -> g1 = 0, g2 = 0, g1*g2 = 0 (STABLE)
    confocal = lab_engine.simulate_laser_cavity(cavity_length=0.5, r1=0.5, r2=0.5)
    assert confocal["g1"] == 0.0
    assert confocal["g2"] == 0.0
    assert confocal["g_prod"] == 0.0
    assert confocal["is_stable"] is True
    
    # Delta_nu = c / (2 * 0.5) = 2.9979e8 / 1.0 = 299.79 MHz
    assert abs(confocal["mode_spacing_mhz"] - 299.79) < 0.1

    # Unstable cavity: L = 1.5m, R1 = 0.8m, R2 = 0.6m -> g1 = 1 - 1.875 = -0.875, g2 = 1 - 2.5 = -1.5
    # g1*g2 = 1.3125 > 1 (UNSTABLE)
    unstable = lab_engine.simulate_laser_cavity(cavity_length=1.5, r1=0.8, r2=0.6)
    assert unstable["is_stable"] is False
    assert unstable["g_prod"] > 1.0


def test_simulate_rtos_schedulability(lab_engine):
    """Verify Rate Monotonic Scheduling (RMS) utilization and ARM NVIC tail-chaining."""
    tasks = [
        {"c": 5, "t": 30},   # U1 = 16.67%
        {"c": 12, "t": 60},  # U2 = 20.00%
        {"c": 15, "t": 120}  # U3 = 12.50%
    ]
    sim = lab_engine.simulate_rtos_schedulability(tasks, core_clock_mhz=84.0)
    assert sim["task_count"] == 3
    # Total U = 16.67 + 20.00 + 12.50 = 49.17%
    assert abs(sim["total_utilization_pct"] - 49.17) < 0.1
    # Bound for n=3 is 77.98%
    assert abs(sim["liu_layland_bound_pct"] - 77.98) < 0.1
    assert sim["is_schedulable"] is True
    
    # ARM Cortex-M4 tail-chaining savings: 6 cycles vs 24 cycles = 75% savings
    assert sim["latency_savings_pct"] == 75.0


def test_log_observation(lab_engine):
    """Verify SQLite WAL observation trial logging."""
    payload = {
        "fc": 1000,
        "fs": 16000,
        "order": 4,
        "mag_at_cutoff": 0.7071
    }
    res = lab_engine.log_observation(
        course_code="EC23S01",
        lab_id="EC23S01_LAB1",
        student_id="2023MITEC042",
        telemetry=payload
    )
    assert res["status"] == "success"
    assert "observation_id" in res


def test_error_handling(lab_engine):
    """Verify robust exception handling on out-of-bound inputs."""
    with pytest.raises(ValueError):
        lab_engine.simulate_dsp_butterworth(fc=-100, fs=16000, order=2)

    with pytest.raises(ValueError):
        lab_engine.simulate_device_iv(vf=0.5, temp_k=-10)

    with pytest.raises(ValueError):
        lab_engine.simulate_laser_cavity(cavity_length=-1.0, r1=1.0, r2=1.0)

    with pytest.raises(ValueError):
        lab_engine.simulate_rtos_schedulability([])
