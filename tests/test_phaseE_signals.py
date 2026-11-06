"""
========================================================================================
VoltCore Apex Academia - Phase E Test Suite: Signals & Communication Systems
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU usage.
========================================================================================
"""

import os
import pytest
import sqlite3
from backend.signals_communication_engine import (
    SignalsCommunicationEngine,
    DIGITAL_MODULATION_SCHEMES
)


@pytest.fixture
def engine(tmp_path):
    """Instantiate SignalsCommunicationEngine with an isolated temporary SQLite WAL database."""
    db_file = str(tmp_path / "test_signals.db")
    return SignalsCommunicationEngine(db_path=db_file)


def test_signals_wal_mode(engine):
    """Verify that SQLite tables for signals and modulation are initialized in WAL mode."""
    conn = sqlite3.connect(engine.db_path)
    try:
        cur = conn.execute("PRAGMA journal_mode;")
        mode = cur.fetchone()[0]
        assert mode.lower() == "wal", f"Expected WAL mode, got {mode}"

        cur = conn.execute("""
            SELECT name FROM sqlite_master WHERE type='table'
            AND name IN ('signals_simulations', 'modulation_experiments');
        """)
        tables = {row[0] for row in cur.fetchall()}
        assert "signals_simulations" in tables
        assert "modulation_experiments" in tables
    finally:
        conn.close()


def test_generate_waveform(engine):
    """Verify waveform generation, energy, and RMS power metrics (Feature 251)."""
    sine = engine.generate_waveform("sine", amplitude=2.0, frequency_hz=10.0, duration_sec=1.0)
    assert sine["waveform_type"] == "sine"
    assert sine["total_samples"] == 200
    assert sine["rms_value"] > 0
    assert len(sine["points"]) > 50

    sq = engine.generate_waveform("square", amplitude=1.0, frequency_hz=5.0)
    assert sq["average_power_watts"] > 0

    tri = engine.generate_waveform("triangle", amplitude=1.0, frequency_hz=5.0)
    assert tri["total_samples"] == 200

    sinc = engine.generate_waveform("sinc", amplitude=1.0, frequency_hz=5.0)
    assert sinc["total_samples"] == 200

    with pytest.raises(ValueError):
        engine.generate_waveform("sine", frequency_hz=-5.0)

    with pytest.raises(ValueError):
        engine.generate_waveform("invalid_wave")


def test_combine_signals(engine):
    """Verify addition, multiplication, and beat frequency calculation (Feature 252)."""
    add_res = engine.combine_signals("add", f1_hz=10.0, f2_hz=12.0)
    assert add_res["beat_frequency_hz"] == 2.0
    assert add_res["envelope_period_sec"] == 0.5
    assert len(add_res["points"]) > 50

    mul_res = engine.combine_signals("multiply", f1_hz=10.0, f2_hz=10.0)
    assert mul_res["beat_frequency_hz"] == 0.0

    with pytest.raises(ValueError):
        engine.combine_signals("invalid_op")


def test_transform_signal(engine):
    """Verify time shift, scaling, and reversal transformations (Feature 253)."""
    # Delay and compression
    trans = engine.transform_signal(a_scale=2.0, t0_shift=0.5, reverse=False)
    assert "Compression" in trans["scale_effect"]
    assert "Delay" in trans["shift_effect"]
    assert trans["time_reversed"] is False

    # Expansion and advance with reversal
    rev = engine.transform_signal(a_scale=0.5, t0_shift=-0.2, reverse=True)
    assert "Expansion" in rev["scale_effect"]
    assert "Advance" in rev["shift_effect"]
    assert rev["time_reversed"] is True

    with pytest.raises(ValueError):
        engine.transform_signal(a_scale=0.0)


def test_check_discrete_periodicity(engine):
    """Verify discrete-time periodicity check and fundamental period calculation (Feature 254)."""
    # Periodic: f = 50 Hz, fs = 200 Hz -> f/fs = 1/4 -> N = 4
    per = engine.check_discrete_periodicity(analog_freq_hz=50.0, sampling_rate_fs=200.0)
    assert per["is_discrete_periodic"] is True
    assert per["fundamental_period_n"] == 4

    # Irrational/Aperiodic test
    with pytest.raises(ValueError):
        engine.check_discrete_periodicity(analog_freq_hz=50.0, sampling_rate_fs=-100.0)


def test_fourier_transform_pair(engine):
    """Verify analytical Fourier transform pairs (Feature 255)."""
    rect = engine.get_fourier_transform_pair("rect", param=2.0)
    assert "sinc" in rect["fourier_transform_expression"]
    assert len(rect["first_zero_crossings_rad_s"]) == 3

    exp = engine.get_fourier_transform_pair("exponential", param=3.0)
    assert "3.0" in exp["fourier_transform_expression"]

    delta = engine.get_fourier_transform_pair("delta")
    assert "1.0" in delta["fourier_transform_expression"]

    with pytest.raises(ValueError):
        engine.get_fourier_transform_pair("unknown_sig")


def test_synthesize_fourier_series(engine):
    """Verify Fourier series harmonic synthesis and Gibbs phenomenon (Feature 256)."""
    sq_syn = engine.synthesize_fourier_series("square", harmonics=7, fundamental_freq_hz=2.0)
    assert sq_syn["harmonics_count"] == 7
    assert sq_syn["gibbs_overshoot_pct"] == 8.95
    assert len(sq_syn["harmonic_coefficients"]) == 7
    assert len(sq_syn["points"]) == 101

    saw_syn = engine.synthesize_fourier_series("sawtooth", harmonics=5)
    assert saw_syn["gibbs_overshoot_pct"] == 0.0

    with pytest.raises(ValueError):
        engine.synthesize_fourier_series("square", harmonics=0)


def test_calculate_convolution(engine):
    """Verify discrete linear and circular convolution (Feature 257)."""
    x = [1.0, 2.0, 3.0]
    h = [1.0, 1.0]

    # Linear: output len = 3 + 2 - 1 = 4
    # y = [1*1, 1*1 + 2*1, 2*1 + 3*1, 3*1] = [1, 3, 5, 3]
    lin = engine.calculate_convolution(x, h, circular=False)
    assert lin["output_length"] == 4
    assert lin["output_sequence"] == [1.0, 3.0, 5.0, 3.0]

    # Circular: N = 4
    circ = engine.calculate_convolution(x, h, circular=True, n_points=4)
    assert circ["output_length"] == 4
    assert circ["aliasing_present"] is False
    assert circ["output_sequence"] == [1.0, 3.0, 5.0, 3.0]

    with pytest.raises(ValueError):
        engine.calculate_convolution([], [1.0])

    with pytest.raises(ValueError):
        engine.calculate_convolution([1, 2, 3], [1, 1], circular=True, n_points=2)


def test_analyze_sampling(engine):
    """Verify Nyquist theorem, oversampling, and aliased frequency calculation (Feature 258)."""
    # Oversampling: fs = 300, signal = 100 -> Nyquist rate = 200
    over = engine.analyze_sampling(signal_freq_hz=100.0, sampling_rate_fs=300.0)
    assert over["has_aliasing"] is False
    assert over["nyquist_rate_hz"] == 200.0

    # Undersampling: fs = 150, signal = 100 -> Alias frequency = |100 - 150| = 50 Hz
    under = engine.analyze_sampling(signal_freq_hz=100.0, sampling_rate_fs=150.0)
    assert under["has_aliasing"] is True
    assert under["apparent_alias_frequency_hz"] == 50.0

    with pytest.raises(ValueError):
        engine.analyze_sampling(signal_freq_hz=-10.0, sampling_rate_fs=100.0)


def test_calculate_analog_modulation(engine):
    """Verify AM modulation index, efficiency, and FM Carson's rule bandwidth (Feature 259)."""
    # Standard AM: Ac = 10V, Am = 8V -> m = 0.8
    am = engine.calculate_analog_modulation(mod_type="AM", fc_hz=10000.0, fm_hz=1000.0, ac_v=10.0, am_v=8.0)
    assert am["modulation_index_m"] == 0.8
    assert am["bandwidth_hz"] == 2000.0
    assert 20.0 < am["power_efficiency_pct"] < 30.0

    # Frequency Modulation (FM): kf = 500 Hz/V, Am = 4V -> Delta_f = 2000 Hz, fm = 1000 Hz -> beta = 2.0
    fm = engine.calculate_analog_modulation(mod_type="FM", fc_hz=100000.0, fm_hz=1000.0, ac_v=10.0, am_v=4.0, kf_hz_v=500.0)
    assert fm["frequency_deviation_hz"] == 2000.0
    assert fm["modulation_index_beta"] == 2.0
    assert fm["carsons_bandwidth_hz"] == 6000.0  # 2 * (2000 + 1000)

    with pytest.raises(ValueError):
        engine.calculate_analog_modulation(mod_type="UNKNOWN")


def test_compare_digital_modulations(engine):
    """Verify digital modulation constellation points and BER computation (Feature 260)."""
    comp = engine.compare_digital_modulations(snr_db=10.0)
    assert comp["snr_db"] == 10.0
    assert len(comp["schemes"]) == 4

    schemes = {s["scheme"]: s for s in comp["schemes"]}
    assert "BPSK" in schemes
    assert "QPSK" in schemes
    assert "16-QAM" in schemes
    assert "BFSK" in schemes

    assert schemes["BPSK"]["bits_per_symbol"] == 1
    assert schemes["QPSK"]["bits_per_symbol"] == 2
    assert schemes["16-QAM"]["bits_per_symbol"] == 4
    assert schemes["16-QAM"]["spectral_efficiency"] == 4.0
    assert schemes["BPSK"]["bit_error_rate"] < 1e-4


def test_persistence_methods(engine):
    """Verify SQLite WAL simulation logging and retrieval."""
    sim = engine.save_simulation(
        student_id="2023MITEC042",
        operation_type="SAMPLING_ANALYSIS",
        input_params={"f_sig": 100, "fs": 300},
        output_metrics={"alias": 0, "status": "Oversampling"}
    )
    assert sim["status"] == "success"
    assert sim["simulation_id"] > 0

    sims = engine.get_simulations("2023MITEC042")
    assert len(sims) >= 1
    assert sims[0]["operation_type"] == "SAMPLING_ANALYSIS"

    # Test modulation experiment persistence
    exp = engine.save_modulation_experiment(
        student_id="2023MITEC042",
        mod_type="FM_WBFM",
        carrier_freq_hz=100000.0,
        message_freq_hz=1000.0,
        bandwidth_hz=6000.0,
        modulation_index=2.0
    )
    assert exp["status"] == "success"
    assert exp["experiment_id"] > 0

    experiments = engine.get_modulation_experiments("2023MITEC042")
    assert len(experiments) >= 1
    assert experiments[0]["mod_type"] == "FM_WBFM"

