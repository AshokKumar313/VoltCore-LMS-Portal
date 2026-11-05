import React, { useState, useEffect } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Analog & Communication Engineering Center
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * Course Codes: EC3451 - Linear Integrated Circuits | EC3491 - Communication Systems
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 * ========================================================================================
 */

const DEFAULT_STUDENT_ID = "2023MITEC042";

const CURRICULUM_PRESETS = [
  {
    preset_id: "PRESET_SALLEN_KEY_1KHZ",
    title: "2nd-Order Sallen-Key Butterworth LPF",
    subject_code: "EC3451",
    category: "FILTER",
    description: "Unity-gain Sallen-Key low-pass filter designed for 1 kHz cutoff with Q=0.707 (maximally flat).",
    tab: "filter",
    params: { filter_type: "SALLEN_KEY_LPF", R: 15900, C: 1.414e-8, R2: 15900, C2: 7.07e-9, gain: 1.0 }
  },
  {
    preset_id: "PRESET_BJT_VOLTAGE_DIVIDER",
    title: "BJT Voltage Divider Bias (Active Region)",
    subject_code: "EC3451",
    category: "TRANSISTOR",
    description: "Standard 12V NPN transistor amplifier stage operating in the linear active region (Lab 304 spec).",
    tab: "transistor",
    params: { transistor_type: "BJT_NPN", Vcc: 12.0, R1: 39000, R2: 10000, Rc: 2200, Re: 1000, beta: 150, Vbe: 0.7 }
  },
  {
    preset_id: "PRESET_MOSFET_SELF_BIAS",
    title: "MOSFET Voltage Divider Bias (Saturation)",
    subject_code: "EC3451",
    category: "TRANSISTOR",
    description: "N-channel enhancement MOSFET biased in saturation for analog linear amplification.",
    tab: "transistor",
    params: { transistor_type: "MOSFET_NMOS", Vcc: 15.0, R1: 1000000, R2: 500000, Rc: 3300, Re: 1500, Vth: 2.0, kn: 1.5e-3 }
  },
  {
    preset_id: "PRESET_OPAMP_INVERTING_LM741",
    title: "LM741 Inverting Amplifier (Av = -10)",
    subject_code: "EC3451",
    category: "OPAMP",
    description: "Inverting operational amplifier stage with 10k input, 100k feedback, and GBW=1MHz.",
    tab: "opamp",
    params: { config: "INVERTING", Rin: 10000, Rf: 100000, GBW: 1000000, SR: 500000, Vpeak: 5.0, Vio: 0.002 }
  },
  {
    preset_id: "PRESET_TXLINE_COAX_50OHM",
    title: "50Ω Coaxial Feedline with Mismatched Load",
    subject_code: "EC3491",
    category: "RF_COMM",
    description: "50-ohm RF feedline terminated in a complex 75 + j25 ohm load.",
    tab: "rf_comm",
    params: { Z0: 50.0, ZL_real: 75.0, ZL_imag: 25.0 }
  },
  {
    preset_id: "PRESET_FM_BROADCAST_CARSON",
    title: "Commercial FM Broadcast Carson's Bandwidth",
    subject_code: "EC3491",
    category: "RF_COMM",
    description: "Standard 75 kHz peak frequency deviation commercial FM broadcast signal at fm=15 kHz.",
    tab: "rf_comm",
    params: { modulation_type: "FM", delta_f: 75000, mod_freq: 15000, carrier_freq: 100e6, Pc: 1000, snr_db: 25, channel_bandwidth: 200000 }
  }
];

export default function AnalogCommHub() {
  const [activeTab, setActiveTab] = useState('filter'); // 'filter' | 'transistor' | 'opamp' | 'rf_comm' | 'presets'
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  // =========================================================================
  // TAB 1: ANALOG FILTER STATE
  // =========================================================================
  const [filterType, setFilterType] = useState('RC_LPF');
  const [filterR, setFilterR] = useState(10000);
  const [filterC, setFilterC] = useState(1.0e-8);
  const [filterL, setFilterL] = useState(1.0e-3);
  const [filterR2, setFilterR2] = useState(10000);
  const [filterC2, setFilterC2] = useState(1.0e-8);
  const [filterGain, setFilterGain] = useState(1.0);
  const [filterResult, setFilterResult] = useState(null);

  useEffect(() => {
    handleComputeFilter();
  }, [filterType, filterR, filterC, filterL, filterR2, filterC2, filterGain]);

  const handleComputeFilter = () => {
    fetch('/api/analog_comm/filter_calc', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filter_type: filterType,
        R: filterR,
        C: filterC,
        L: filterL,
        R2: filterR2,
        C2: filterC2,
        gain: filterGain
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'SUCCESS') setFilterResult(data);
      })
      .catch(() => {});
  };

  // =========================================================================
  // TAB 2: TRANSISTOR BIASING STATE
  // =========================================================================
  const [transistorType, setTransistorType] = useState('BJT_NPN');
  const [transVcc, setTransVcc] = useState(12.0);
  const [transR1, setTransR1] = useState(39000);
  const [transR2, setTransR2] = useState(10000);
  const [transRc, setTransRc] = useState(2200);
  const [transRe, setTransRe] = useState(1000);
  const [transBeta, setTransBeta] = useState(150);
  const [transVbe, setTransVbe] = useState(0.7);
  const [transVth, setTransVth] = useState(2.0);
  const [transKn, setTransKn] = useState(1.5e-3);
  const [transResult, setTransResult] = useState(null);

  useEffect(() => {
    handleComputeTransistor();
  }, [transistorType, transVcc, transR1, transR2, transRc, transRe, transBeta, transVbe, transVth, transKn]);

  const handleComputeTransistor = () => {
    fetch('/api/analog_comm/transistor_bias', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        transistor_type: transistorType,
        Vcc: transVcc,
        R1: transR1,
        R2: transR2,
        Rc: transRc,
        Re: transRe,
        beta: transBeta,
        Vbe: transVbe,
        Vth: transVth,
        kn: transKn
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'SUCCESS') setTransResult(data);
      })
      .catch(() => {});
  };

  // =========================================================================
  // TAB 3: OP-AMP & LINEAR IC STATE
  // =========================================================================
  const [opConfig, setOpConfig] = useState('INVERTING');
  const [opRin, setOpRin] = useState(10000);
  const [opRf, setOpRf] = useState(100000);
  const [opGbw, setOpGbw] = useState(1000000);
  const [opSr, setOpSr] = useState(500000); // 0.5 V/us = 500,000 V/s
  const [opVpeak, setOpVpeak] = useState(5.0);
  const [opVio, setOpVio] = useState(0.002);
  const [opResult, setOpResult] = useState(null);

  useEffect(() => {
    handleComputeOpamp();
  }, [opConfig, opRin, opRf, opGbw, opSr, opVpeak, opVio]);

  const handleComputeOpamp = () => {
    fetch('/api/analog_comm/opamp_calc', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        config: opConfig,
        Rin: opRin,
        Rf: opRf,
        GBW: opGbw,
        SR: opSr,
        Vpeak: opVpeak,
        Vio: opVio
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'SUCCESS') setOpResult(data);
      })
      .catch(() => {});
  };

  // =========================================================================
  // TAB 4: TRANSMISSION LINE & MODULATION STATE
  // =========================================================================
  const [rfZ0, setRfZ0] = useState(50.0);
  const [rfZlReal, setRfZlReal] = useState(75.0);
  const [rfZlImag, setRfZlImag] = useState(25.0);
  const [rfTxResult, setRfTxResult] = useState(null);

  const [modType, setModType] = useState('FM');
  const [modFm, setModFm] = useState(15000);
  const [modDeltaF, setModDeltaF] = useState(75000);
  const [modIndex, setModIndex] = useState(0.8);
  const [modPc, setModPc] = useState(1000);
  const [modSnr, setModSnr] = useState(20.0);
  const [modBw, setModBw] = useState(200000);
  const [modResult, setModResult] = useState(null);

  useEffect(() => {
    // Compute TX Line
    fetch('/api/analog_comm/txline_calc', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ Z0: rfZ0, ZL_real: rfZlReal, ZL_imag: rfZlImag })
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'SUCCESS') setRfTxResult(data);
      })
      .catch(() => {});

    // Compute Modulation
    fetch('/api/analog_comm/modulation_calc', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        modulation_type: modType,
        mod_freq: modFm,
        delta_f: modDeltaF,
        mod_index: modIndex,
        Pc: modPc,
        snr_db: modSnr,
        channel_bandwidth: modBw
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'SUCCESS') setModResult(data);
      })
      .catch(() => {});
  }, [rfZ0, rfZlReal, rfZlImag, modType, modFm, modDeltaF, modIndex, modPc, modSnr, modBw]);

  const handleLoadPreset = (preset) => {
    if (preset.tab === 'filter') {
      setFilterType(preset.params.filter_type || 'RC_LPF');
      setFilterR(preset.params.R || 10000);
      setFilterC(preset.params.C || 1e-8);
      if (preset.params.R2) setFilterR2(preset.params.R2);
      if (preset.params.C2) setFilterC2(preset.params.C2);
      if (preset.params.gain) setFilterGain(preset.params.gain);
      setActiveTab('filter');
    } else if (preset.tab === 'transistor') {
      setTransistorType(preset.params.transistor_type || 'BJT_NPN');
      setTransVcc(preset.params.Vcc || 12.0);
      setTransR1(preset.params.R1 || 39000);
      setTransR2(preset.params.R2 || 10000);
      setTransRc(preset.params.Rc || 2200);
      setTransRe(preset.params.Re || 1000);
      if (preset.params.beta) setTransBeta(preset.params.beta);
      if (preset.params.Vth) setTransVth(preset.params.Vth);
      if (preset.params.kn) setTransKn(preset.params.kn);
      setActiveTab('transistor');
    } else if (preset.tab === 'opamp') {
      setOpConfig(preset.params.config || 'INVERTING');
      setOpRin(preset.params.Rin || 10000);
      setOpRf(preset.params.Rf || 100000);
      if (preset.params.GBW) setOpGbw(preset.params.GBW);
      if (preset.params.SR) setOpSr(preset.params.SR);
      if (preset.params.Vio) setOpVio(preset.params.Vio);
      setActiveTab('opamp');
    } else if (preset.tab === 'rf_comm') {
      if (preset.params.Z0) setRfZ0(preset.params.Z0);
      if (preset.params.ZL_real) setRfZlReal(preset.params.ZL_real);
      if (preset.params.ZL_imag !== undefined) setRfZlImag(preset.params.ZL_imag);
      if (preset.params.modulation_type) setModType(preset.params.modulation_type);
      if (preset.params.delta_f) setModDeltaF(preset.params.delta_f);
      if (preset.params.fm) setModFm(preset.params.fm);
      setActiveTab('rf_comm');
    }
    showToast(`Loaded ${preset.title}!`);
  };

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    showToast(`Copied ${label} to clipboard!`);
  };

  return (
    <div className="w-full min-h-screen bg-slate-900/60 p-4 md:p-8 text-slate-100">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-emerald-600/95 text-white px-5 py-3 rounded-xl shadow-2xl border border-emerald-400/40 backdrop-blur-md flex items-center gap-3 animate-fade-in">
          <svg className="w-5 h-5 text-emerald-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
          </svg>
          <span className="text-sm font-medium">{toastMessage}</span>
        </div>
      )}

      {/* Header Container */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                MIT Campus • EC3451 LIC &amp; EC3491 Comm Systems
              </span>
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                Lead: Ashok Kumar A ({DEFAULT_STUDENT_ID})
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
              Analog &amp; Communication Engineering Center
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Interactive Sallen-Key active filters, BJT/MOSFET Q-point load lines, Op-Amp slew rate models, and RF modulation systems.
            </p>
          </div>

          {/* Quick Metrics Ribbon */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-3 text-center">
              <div className="text-xs text-emerald-400 font-medium">⚡ Active Solvers</div>
              <div className="text-lg font-bold text-white mt-1">5 Core Models</div>
            </div>
            <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-3 text-center">
              <div className="text-xs text-cyan-400 font-medium">🔬 Transistor Bias</div>
              <div className="text-lg font-bold text-white mt-1">BJT &amp; MOSFET</div>
            </div>
            <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-3 text-center">
              <div className="text-xs text-amber-400 font-medium">📻 RF Modulation</div>
              <div className="text-lg font-bold text-white mt-1">AM, FM &amp; Shannon</div>
            </div>
            <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-3 text-center">
              <div className="text-xs text-purple-400 font-medium">📚 Lab Bench</div>
              <div className="text-lg font-bold text-purple-300 mt-1">6 Presets</div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap items-center gap-2 mt-6">
          <button
            onClick={() => setActiveTab('filter')}
            className={`px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 transition-all ${
              activeTab === 'filter'
                ? 'bg-emerald-500 text-slate-950 font-semibold shadow-lg shadow-emerald-500/20'
                : 'bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-white'
            }`}
          >
            <span>〰️</span> Analog Filter Designer
          </button>

          <button
            onClick={() => setActiveTab('transistor')}
            className={`px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 transition-all ${
              activeTab === 'transistor'
                ? 'bg-emerald-500 text-slate-950 font-semibold shadow-lg shadow-emerald-500/20'
                : 'bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-white'
            }`}
          >
            <span>⚡</span> BJT &amp; MOSFET Q-Point Solver
          </button>

          <button
            onClick={() => setActiveTab('opamp')}
            className={`px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 transition-all ${
              activeTab === 'opamp'
                ? 'bg-emerald-500 text-slate-950 font-semibold shadow-lg shadow-emerald-500/20'
                : 'bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-white'
            }`}
          >
            <span>🎛️</span> Op-Amp &amp; Slew Rate Models
          </button>

          <button
            onClick={() => setActiveTab('rf_comm')}
            className={`px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 transition-all ${
              activeTab === 'rf_comm'
                ? 'bg-emerald-500 text-slate-950 font-semibold shadow-lg shadow-emerald-500/20'
                : 'bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-white'
            }`}
          >
            <span>📡</span> RF Transmission &amp; Modulation
          </button>

          <button
            onClick={() => setActiveTab('presets')}
            className={`px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 transition-all ${
              activeTab === 'presets'
                ? 'bg-emerald-500 text-slate-950 font-semibold shadow-lg shadow-emerald-500/20'
                : 'bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-white'
            }`}
          >
            <span>📚</span> EC3451/91 Benchmark Labs
          </button>
        </div>
      </div>

      {/* Main Workspace Panels */}
      <div className="max-w-7xl mx-auto">
        {/* ========================================================================= */}
        {/* TAB 1: ANALOG FILTER DESIGNER */}
        {/* ========================================================================= */}
        {activeTab === 'filter' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Input Controls (5 cols) */}
            <div className="lg:col-span-5 space-y-6">
              <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
                <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                  <span>⚙️</span> Filter Topology &amp; Values
                </h3>

                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Filter Topology</label>
                    <select
                      value={filterType}
                      onChange={(e) => setFilterType(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500"
                    >
                      <option value="RC_LPF">1st-Order Passive RC Low-Pass</option>
                      <option value="RC_HPF">1st-Order Passive RC High-Pass</option>
                      <option value="SALLEN_KEY_LPF">2nd-Order Sallen-Key Active LPF</option>
                      <option value="SALLEN_KEY_HPF">2nd-Order Sallen-Key Active HPF</option>
                      <option value="LC_RESONANT">2nd-Order LC Resonant Tank</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Resistance R1 (Ω)</label>
                      <input
                        type="number"
                        value={filterR}
                        onChange={(e) => setFilterR(parseFloat(e.target.value) || 1)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Capacitance C1 (F)</label>
                      <input
                        type="number"
                        step="1e-10"
                        value={filterC}
                        onChange={(e) => setFilterC(parseFloat(e.target.value) || 1e-12)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                      />
                    </div>
                  </div>

                  {filterType.startsWith('SALLEN_KEY') && (
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-medium text-slate-400 mb-1">Resistance R2 (Ω)</label>
                        <input
                          type="number"
                          value={filterR2}
                          onChange={(e) => setFilterR2(parseFloat(e.target.value) || 1)}
                          className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-slate-400 mb-1">Capacitance C2 (F)</label>
                        <input
                          type="number"
                          step="1e-10"
                          value={filterC2}
                          onChange={(e) => setFilterC2(parseFloat(e.target.value) || 1e-12)}
                          className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                        />
                      </div>
                    </div>
                  )}

                  {filterType === 'LC_RESONANT' && (
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Inductance L (H)</label>
                      <input
                        type="number"
                        step="1e-4"
                        value={filterL}
                        onChange={(e) => setFilterL(parseFloat(e.target.value) || 1e-6)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Results & Bode Response (7 cols) */}
            <div className="lg:col-span-7 space-y-6">
              {filterResult && (
                <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-base font-bold text-white flex items-center gap-2">
                      <span>📊</span> Filter Response Characteristics
                    </h3>
                    <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                      Order {filterResult.order}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
                    <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                      <div className="text-xs text-slate-400">Cutoff Frequency (fc)</div>
                      <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
                        {filterResult.cutoff_frequency_hz >= 1000
                          ? `${(filterResult.cutoff_frequency_hz / 1000).toFixed(2)} kHz`
                          : `${filterResult.cutoff_frequency_hz} Hz`}
                      </div>
                    </div>

                    <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                      <div className="text-xs text-slate-400">Quality Factor (Q)</div>
                      <div className="text-xl font-bold font-mono text-cyan-400 mt-1">
                        {filterResult.q_factor}
                      </div>
                    </div>

                    <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                      <div className="text-xs text-slate-400">Time Constant (τ)</div>
                      <div className="text-xl font-bold font-mono text-amber-400 mt-1">
                        {filterResult.time_constant_seconds} s
                      </div>
                    </div>
                  </div>

                  {/* Bode Magnitude Sample Table */}
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Simulated Bode Magnitude Points</h4>
                  <div className="overflow-x-auto border border-slate-800 rounded-xl">
                    <table className="w-full text-center text-xs font-mono">
                      <thead className="bg-slate-900 text-slate-400">
                        <tr>
                          <th className="py-2 px-3">Test Frequency (Hz)</th>
                          <th className="py-2 px-3">Relative Point</th>
                          <th className="py-2 px-3 text-emerald-400">Gain Magnitude (dB)</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {filterResult.bode_response.map((pt, idx) => (
                          <tr key={idx} className="hover:bg-slate-800/40">
                            <td className="py-2 px-3 text-slate-300">{pt.frequency_hz} Hz</td>
                            <td className="py-2 px-3 text-slate-500">{['0.1 fc', '0.5 fc', '1.0 fc (-3dB)', '2.0 fc', '10.0 fc'][idx]}</td>
                            <td className="py-2 px-3 font-bold text-emerald-400">{pt.magnitude_db} dB</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="mt-4 text-xs text-slate-400 font-mono bg-slate-950 p-3 rounded-xl border border-slate-800">
                    Formula: {filterResult.formula}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 2: TRANSISTOR Q-POINT SOLVER */}
        {/* ========================================================================= */}
        {activeTab === 'transistor' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            <div className="lg:col-span-5 space-y-6">
              <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
                <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                  <span>⚡</span> Biasing Circuit Parameters
                </h3>

                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Transistor Family</label>
                    <select
                      value={transistorType}
                      onChange={(e) => setTransistorType(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500"
                    >
                      <option value="BJT_NPN">BJT NPN (Voltage Divider Bias)</option>
                      <option value="MOSFET_NMOS">MOSFET N-Channel (Enhancement Mode)</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Supply Vcc/Vdd (V)</label>
                      <input
                        type="number"
                        value={transVcc}
                        onChange={(e) => setTransVcc(parseFloat(e.target.value) || 1)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Divider R1 (Ω)</label>
                      <input
                        type="number"
                        value={transR1}
                        onChange={(e) => setTransR1(parseFloat(e.target.value) || 1)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Divider R2 (Ω)</label>
                      <input
                        type="number"
                        value={transR2}
                        onChange={(e) => setTransR2(parseFloat(e.target.value) || 1)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Collector/Drain Rc/Rd (Ω)</label>
                      <input
                        type="number"
                        value={transRc}
                        onChange={(e) => setTransRc(parseFloat(e.target.value) || 1)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Emitter/Source Re/Rs (Ω)</label>
                      <input
                        type="number"
                        value={transRe}
                        onChange={(e) => setTransRe(parseFloat(e.target.value) || 1)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                      />
                    </div>
                    {transistorType === 'BJT_NPN' ? (
                      <div>
                        <label className="block text-xs font-medium text-slate-400 mb-1">Current Gain (β)</label>
                        <input
                          type="number"
                          value={transBeta}
                          onChange={(e) => setTransBeta(parseFloat(e.target.value) || 1)}
                          className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                        />
                      </div>
                    ) : (
                      <div>
                        <label className="block text-xs font-medium text-slate-400 mb-1">Threshold Vth (V)</label>
                        <input
                          type="number"
                          value={transVth}
                          onChange={(e) => setTransVth(parseFloat(e.target.value) || 0)}
                          className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                        />
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Results (7 cols) */}
            <div className="lg:col-span-7 space-y-6">
              {transResult && (
                <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-base font-bold text-white flex items-center gap-2">
                      <span>🎯</span> DC Q-Point Operating State
                    </h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-bold border ${
                      transResult.operating_region === 'ACTIVE' || transResult.operating_region === 'SATURATION'
                        ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                        : 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                    }`}>
                      {transResult.operating_region} REGION
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
                    {transistorType === 'BJT_NPN' ? (
                      <>
                        <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                          <div className="text-xs text-slate-400">Collector Current (IC)</div>
                          <div className="text-xl font-bold font-mono text-cyan-400 mt-1">{transResult.IC_milliamps} mA</div>
                        </div>
                        <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                          <div className="text-xs text-slate-400">Collector-Emitter (VCE)</div>
                          <div className="text-xl font-bold font-mono text-emerald-400 mt-1">{transResult.VCE_volts} V</div>
                        </div>
                        <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                          <div className="text-xs text-slate-400">Base Current (IB)</div>
                          <div className="text-xl font-bold font-mono text-amber-400 mt-1">{transResult.IB_microamps} μA</div>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                          <div className="text-xs text-slate-400">Drain Current (ID)</div>
                          <div className="text-xl font-bold font-mono text-cyan-400 mt-1">{transResult.ID_milliamps} mA</div>
                        </div>
                        <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                          <div className="text-xs text-slate-400">Drain-Source (VDS)</div>
                          <div className="text-xl font-bold font-mono text-emerald-400 mt-1">{transResult.VDS_volts} V</div>
                        </div>
                        <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                          <div className="text-xs text-slate-400">Gate-Source (VGS)</div>
                          <div className="text-xl font-bold font-mono text-amber-400 mt-1">{transResult.VGS_volts} V</div>
                        </div>
                      </>
                    )}
                  </div>

                  <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 text-xs text-slate-300 leading-relaxed">
                    <span className="font-bold text-white block mb-1">Analysis Verdict:</span>
                    {transResult.analysis}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 3: OP-AMP & SLEW RATE MODELS */}
        {/* ========================================================================= */}
        {activeTab === 'opamp' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            <div className="lg:col-span-5 space-y-6">
              <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
                <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                  <span>🎛️</span> Op-Amp Circuit Configuration
                </h3>

                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Topology</label>
                    <div className="grid grid-cols-2 gap-2">
                      <button
                        onClick={() => setOpConfig('INVERTING')}
                        className={`py-2 rounded-xl text-xs font-bold transition-all ${
                          opConfig === 'INVERTING'
                            ? 'bg-emerald-500 text-slate-950'
                            : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-700'
                        }`}
                      >
                        Inverting (Av = -Rf/Rin)
                      </button>
                      <button
                        onClick={() => setOpConfig('NON_INVERTING')}
                        className={`py-2 rounded-xl text-xs font-bold transition-all ${
                          opConfig === 'NON_INVERTING'
                            ? 'bg-emerald-500 text-slate-950'
                            : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-700'
                        }`}
                      >
                        Non-Inverting (Av = 1+Rf/R1)
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Input Resistor Rin (Ω)</label>
                      <input
                        type="number"
                        value={opRin}
                        onChange={(e) => setOpRin(parseFloat(e.target.value) || 1)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Feedback Resistor Rf (Ω)</label>
                      <input
                        type="number"
                        value={opRf}
                        onChange={(e) => setOpRf(parseFloat(e.target.value) || 1)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Gain-Bandwidth GBW (Hz)</label>
                      <input
                        type="number"
                        value={opGbw}
                        onChange={(e) => setOpGbw(parseFloat(e.target.value) || 1000)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Slew Rate (V/μs)</label>
                      <input
                        type="number"
                        step="0.1"
                        value={opSr / 1e6}
                        onChange={(e) => setOpSr((parseFloat(e.target.value) || 0.1) * 1e6)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Results (7 cols) */}
            <div className="lg:col-span-7 space-y-6">
              {opResult && (
                <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
                  <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                    <span>📐</span> Performance Metrics
                  </h3>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
                    <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                      <div className="text-xs text-slate-400">Voltage Gain (Av)</div>
                      <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
                        {opResult.voltage_gain} ({opResult.voltage_gain_db} dB)
                      </div>
                    </div>

                    <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                      <div className="text-xs text-slate-400">Bandwidth (f_3dB)</div>
                      <div className="text-xl font-bold font-mono text-cyan-400 mt-1">
                        {opResult.closed_loop_bandwidth_hz >= 1000
                          ? `${(opResult.closed_loop_bandwidth_hz / 1000).toFixed(1)} kHz`
                          : `${opResult.closed_loop_bandwidth_hz} Hz`}
                      </div>
                    </div>

                    <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                      <div className="text-xs text-slate-400">Full-Power BW (Slew)</div>
                      <div className="text-xl font-bold font-mono text-amber-400 mt-1">
                        {opResult.full_power_bandwidth_hz >= 1000
                          ? `${(opResult.full_power_bandwidth_hz / 1000).toFixed(1)} kHz`
                          : `${opResult.full_power_bandwidth_hz} Hz`}
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 text-xs text-slate-400 font-mono space-y-1">
                    <div>Formula: {opResult.formula}</div>
                    <div>Slew Rate: {opResult.slew_rate_v_per_us} V/μs</div>
                    <div>Worst-case Output Offset: {opResult.output_offset_mv} mV</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 4: RF TRANSMISSION & MODULATION */}
        {/* ========================================================================= */}
        {activeTab === 'rf_comm' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
            {/* Panel A: Transmission Line */}
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6 space-y-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>📡</span> RF Transmission Line Matching
              </h3>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Z0 (Ω)</label>
                  <input
                    type="number"
                    value={rfZ0}
                    onChange={(e) => setRfZ0(parseFloat(e.target.value) || 1)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Re(ZL) (Ω)</label>
                  <input
                    type="number"
                    value={rfZlReal}
                    onChange={(e) => setRfZlReal(parseFloat(e.target.value) || 0)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Im(ZL) (Ω)</label>
                  <input
                    type="number"
                    value={rfZlImag}
                    onChange={(e) => setRfZlImag(parseFloat(e.target.value) || 0)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                  />
                </div>
              </div>

              {rfTxResult && (
                <div className="grid grid-cols-2 gap-3 pt-2">
                  <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                    <div className="text-xs text-slate-400">Reflection Coeff |Γ|</div>
                    <div className="text-lg font-bold font-mono text-cyan-400 mt-1">
                      {rfTxResult.reflection_coefficient_mag} ∠ {rfTxResult.reflection_coefficient_phase_deg}°
                    </div>
                  </div>

                  <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                    <div className="text-xs text-slate-400">VSWR (Voltage SWR)</div>
                    <div className={`text-lg font-bold font-mono mt-1 ${rfTxResult.is_well_matched ? 'text-emerald-400' : 'text-amber-400'}`}>
                      {rfTxResult.vswr} : 1
                    </div>
                  </div>

                  <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                    <div className="text-xs text-slate-400">Return Loss</div>
                    <div className="text-lg font-bold font-mono text-emerald-400 mt-1">{rfTxResult.return_loss_db} dB</div>
                  </div>

                  <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                    <div className="text-xs text-slate-400">Power Delivered</div>
                    <div className="text-lg font-bold font-mono text-purple-400 mt-1">{rfTxResult.power_delivered_pct}%</div>
                  </div>
                </div>
              )}
            </div>

            {/* Panel B: Modulation & Information Theory */}
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6 space-y-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>📻</span> Modulation &amp; Information Limits
              </h3>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Modulation Type</label>
                  <select
                    value={modType}
                    onChange={(e) => setModType(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white"
                  >
                    <option value="FM">Frequency Modulation (FM)</option>
                    <option value="AM">Amplitude Modulation (AM)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Message Freq fm (Hz)</label>
                  <input
                    type="number"
                    value={modFm}
                    onChange={(e) => setModFm(parseFloat(e.target.value) || 1)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                  />
                </div>
              </div>

              {modResult && (
                <div className="grid grid-cols-2 gap-3 pt-2">
                  <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                    <div className="text-xs text-slate-400">Transmission BW</div>
                    <div className="text-lg font-bold font-mono text-emerald-400 mt-1">
                      {modResult.modulation_type === 'FM'
                        ? `${(modResult.carson_bandwidth_hz / 1000).toFixed(1)} kHz`
                        : `${(modResult.transmission_bandwidth_hz / 1000).toFixed(1)} kHz`}
                    </div>
                  </div>

                  <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                    <div className="text-xs text-slate-400">Nyquist Min Rate</div>
                    <div className="text-lg font-bold font-mono text-cyan-400 mt-1">
                      {(modResult.nyquist_rate_hz / 1000).toFixed(1)} kS/s
                    </div>
                  </div>

                  <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800 col-span-2">
                    <div className="text-xs text-slate-400">Shannon Channel Capacity (C = B log2(1+SNR))</div>
                    <div className="text-lg font-bold font-mono text-purple-300 mt-1">
                      {modResult.shannon_capacity_kbps} kbps
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 5: EC3451 & EC3491 PRESETS */}
        {/* ========================================================================= */}
        {activeTab === 'presets' && (
          <div className="space-y-6">
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6">
              <h3 className="text-base font-bold text-white mb-2">Anna University Regulation 2023 Lab Presets</h3>
              <p className="text-xs text-slate-400 mb-6">
                Curriculum exercises covering active filters, small-signal transistor bias, Op-Amp frequency response, and Carson's rule FM broadcasting.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {CURRICULUM_PRESETS.map((p) => (
                  <div
                    key={p.preset_id}
                    className="bg-slate-900/80 border border-slate-800 hover:border-slate-700 rounded-xl p-5 transition-all flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between gap-2">
                        <span className="px-2 py-0.5 rounded text-xs font-bold bg-slate-800 text-emerald-400 border border-emerald-500/20">
                          {p.subject_code} • {p.category}
                        </span>
                      </div>

                      <h4 className="text-base font-bold text-white mt-2">{p.title}</h4>
                      <p className="text-xs text-slate-400 mt-1">{p.description}</p>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-end">
                      <button
                        onClick={() => handleLoadPreset(p)}
                        className="px-4 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs font-bold transition-colors"
                      >
                        Load Into Solver →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
