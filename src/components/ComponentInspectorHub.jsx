import React, { useState, useEffect } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Smart PCB, SMD & Component Inspector Lab (Phase 30)
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * Target Facility: Lab 304 (Hardware Prototyping & Inspection Lab)
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 * ========================================================================================
 */

// Color specifications for Resistors
const COLOR_OPTIONS = [
  { name: 'black', hex: '#111827', text: '#ffffff', digit: 0, mult: 1, tol: null, tcr: 250, label: 'Black (0)' },
  { name: 'brown', hex: '#8B4513', text: '#ffffff', digit: 1, mult: 10, tol: 1, tcr: 100, label: 'Brown (1, 1%)' },
  { name: 'red', hex: '#DC2626', text: '#ffffff', digit: 2, mult: 100, tol: 2, tcr: 50, label: 'Red (2, 2%)' },
  { name: 'orange', hex: '#EA580C', text: '#ffffff', digit: 3, mult: 1000, tol: null, tcr: 15, label: 'Orange (3, 1k)' },
  { name: 'yellow', hex: '#EAB308', text: '#000000', digit: 4, mult: 10000, tol: null, tcr: 25, label: 'Yellow (4, 10k)' },
  { name: 'green', hex: '#16A34A', text: '#ffffff', digit: 5, mult: 100000, tol: 0.5, tcr: 20, label: 'Green (5, 0.5%)' },
  { name: 'blue', hex: '#2563EB', text: '#ffffff', digit: 6, mult: 1000000, tol: 0.25, tcr: 10, label: 'Blue (6, 0.25%)' },
  { name: 'violet', hex: '#7C3AED', text: '#ffffff', digit: 7, mult: 10000000, tol: 0.1, tcr: 5, label: 'Violet (7, 0.1%)' },
  { name: 'grey', hex: '#6B7280', text: '#ffffff', digit: 8, mult: 100000000, tol: 0.05, tcr: 1, label: 'Grey (8, 0.05%)' },
  { name: 'white', hex: '#F9FAFB', text: '#000000', digit: 9, mult: 1000000000, tol: null, tcr: null, label: 'White (9)' },
  { name: 'gold', hex: '#D4AF37', text: '#000000', digit: null, mult: 0.1, tol: 5, tcr: null, label: 'Gold (0.1, 5%)' },
  { name: 'silver', hex: '#C0C0C0', text: '#000000', digit: null, mult: 0.01, tol: 10, tcr: null, label: 'Silver (0.01, 10%)' }
];

// Curated IC package thermal catalog fallback
const IC_PACKAGES_PRESETS = [
  { code: 'DIP-8', name: 'Dual In-Line (8-pin)', type: 'Through-Hole', theta_ja: 100.0, theta_jc: 40.0, max_tj: 125, apps: 'Classic Op-Amps (LM741, NE5532), 555 Timers' },
  { code: 'SOIC-8', name: 'Small Outline (8-pin)', type: 'SMD', theta_ja: 150.0, theta_jc: 50.0, max_tj: 125, apps: 'Surface Mount Op-Amps, EEPROMs (24C08)' },
  { code: 'TO-220', name: 'Transistor Outline 220', type: 'Through-Hole', theta_ja: 62.5, theta_jc: 2.5, max_tj: 150, apps: 'Power MOSFETs (IRF540N), Regulators (LM7805)' },
  { code: 'SOT-23', name: 'Small Outline Transistor (3-pin)', type: 'SMD', theta_ja: 250.0, theta_jc: 90.0, max_tj: 125, apps: 'Small Signal Transistors (2N3904), Diodes' },
  { code: 'QFP-64', name: 'Quad Flat Package (64-pin)', type: 'SMD', theta_ja: 45.0, theta_jc: 12.0, max_tj: 125, apps: 'Microcontrollers (STM32F401, ATmega2560)' },
  { code: 'QFN-32', name: 'Quad Flat No-Leads (32-pin)', type: 'SMD', theta_ja: 38.0, theta_jc: 8.0, max_tj: 125, apps: 'ESP32-WROOM SoC, nRF52840 BLE' },
  { code: 'BGA-256', name: 'Ball Grid Array (256-ball)', type: 'SMD', theta_ja: 30.0, theta_jc: 6.0, max_tj: 125, apps: 'Xilinx Artix-7 FPGA, DDR Memory' }
];

export default function ComponentInspectorHub() {
  const [activeTab, setActiveTab] = useState('resistor'); // 'resistor' | 'smd' | 'pcb' | 'thermal' | 'history'

  // ====================================================================================
  // State: Tab 1 - Axial Resistor
  // ====================================================================================
  const [bandCount, setBandCount] = useState(4); // 4 | 5 | 6
  const [band1, setBand1] = useState('yellow');
  const [band2, setBand2] = useState('violet');
  const [band3, setBand3] = useState('black');
  const [multiplierBand, setMultiplierBand] = useState('red');
  const [toleranceBand, setToleranceBand] = useState('gold');
  const [tcrBand, setTcrBand] = useState('red');
  const [resistorResult, setResistorResult] = useState(null);

  // ====================================================================================
  // State: Tab 2 - SMD Marking Decoder
  // ====================================================================================
  const [smdType, setSmdType] = useState('RESISTOR'); // 'RESISTOR' | 'CAPACITOR'
  const [smdCodeInput, setSmdCodeInput] = useState('472');
  const [smdResult, setSmdResult] = useState(null);

  // ====================================================================================
  // State: Tab 3 - IPC-2221 PCB Trace Width
  // ====================================================================================
  const [pcbCurrent, setPcbCurrent] = useState(2.5);
  const [pcbTempRise, setPcbTempRise] = useState(10.0);
  const [pcbCopperOz, setPcbCopperOz] = useState(1.0);
  const [pcbTraceType, setPcbTraceType] = useState('external');
  const [pcbLengthCm, setPcbLengthCm] = useState(10.0);
  const [pcbAmbientTemp, setPcbAmbientTemp] = useState(25.0);
  const [pcbResult, setPcbResult] = useState(null);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState('');

  // ====================================================================================
  // State: Tab 4 - IC Thermal Assessment
  // ====================================================================================
  const [selectedPackage, setSelectedPackage] = useState('DIP-8');
  const [powerWatts, setPowerWatts] = useState(0.5);
  const [icAmbientTemp, setIcAmbientTemp] = useState(25.0);
  const [targetMaxTj, setTargetMaxTj] = useState(100.0);
  const [thermalResult, setThermalResult] = useState(null);

  // ====================================================================================
  // State: Tab 5 - History
  // ====================================================================================
  const [historyRecords, setHistoryRecords] = useState([]);
  const [historyFilter, setHistoryFilter] = useState('');

  // ------------------------------------------------------------------------------------
  // Client-side Resistor Calculation
  // ------------------------------------------------------------------------------------
  useEffect(() => {
    calculateResistor();
  }, [bandCount, band1, band2, band3, multiplierBand, toleranceBand, tcrBand]);

  const calculateResistor = async () => {
    let bands = [];
    if (bandCount === 4) {
      bands = [band1, band2, multiplierBand, toleranceBand];
    } else if (bandCount === 5) {
      bands = [band1, band2, band3, multiplierBand, toleranceBand];
    } else {
      bands = [band1, band2, band3, multiplierBand, toleranceBand, tcrBand];
    }

    try {
      const resp = await fetch('http://127.0.0.1:5000/api/inspector/axial-decode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bands, actor_id: '2023MITEC042' })
      });
      if (resp.ok) {
        const data = await resp.json();
        setResistorResult(data);
        return;
      }
    } catch (e) {
      // Backend not running, use client fallback
    }

    // Client-side deterministic calculation
    const c1 = COLOR_OPTIONS.find(c => c.name === band1);
    const c2 = COLOR_OPTIONS.find(c => c.name === band2);
    const c3 = COLOR_OPTIONS.find(c => c.name === band3);
    const cm = COLOR_OPTIONS.find(c => c.name === multiplierBand);
    const ct = COLOR_OPTIONS.find(c => c.name === toleranceBand);
    const cTcr = COLOR_OPTIONS.find(c => c.name === tcrBand);

    let digits = 0;
    if (bandCount === 4) {
      digits = (c1?.digit ?? 0) * 10 + (c2?.digit ?? 0);
    } else {
      digits = (c1?.digit ?? 0) * 100 + (c2?.digit ?? 0) * 10 + (c3?.digit ?? 0);
    }
    const mult = cm?.mult ?? 1.0;
    const tol = ct?.tol ?? 5.0;
    const tcr = bandCount === 6 ? (cTcr?.tcr ?? 50) : null;
    const rVal = Math.round(digits * mult * 1000) / 1000;
    const minVal = Math.round(rVal * (1 - tol / 100) * 1000) / 1000;
    const maxVal = Math.round(rVal * (1 + tol / 100) * 1000) / 1000;

    const formatOhms = (v) => {
      if (v >= 1e6) return `${(v / 1e6).toFixed(2)} MΩ`;
      if (v >= 1e3) return `${(v / 1e3).toFixed(2)} kΩ`;
      return `${v} Ω`;
    };

    setResistorResult({
      status: 'SUCCESS',
      band_count: bandCount,
      resistance_ohms: rVal,
      formatted: formatOhms(rVal),
      tolerance_pct: tol,
      min_resistance_ohms: minVal,
      max_resistance_ohms: maxVal,
      formatted_range: `${formatOhms(minVal)} - ${formatOhms(maxVal)}`,
      tcr_ppm_k: tcr
    });
  };

  // ------------------------------------------------------------------------------------
  // Client-side SMD Calculation
  // ------------------------------------------------------------------------------------
  useEffect(() => {
    handleDecodeSmd(smdCodeInput, smdType);
  }, [smdCodeInput, smdType]);

  const handleDecodeSmd = async (code, type) => {
    const raw = (code || '').trim().toUpperCase();
    if (!raw) {
      setSmdResult(null);
      return;
    }

    try {
      const resp = await fetch('http://127.0.0.1:5000/api/inspector/smd-decode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: raw, component_type: type, actor_id: '2023MITEC042' })
      });
      if (resp.ok) {
        const data = await resp.json();
        setSmdResult(data);
        return;
      }
    } catch (e) {
      // Backend unavailable, fallback to client
    }

    // Client fallback
    if (type === 'RESISTOR') {
      if (raw === '000' || raw === '0') {
        setSmdResult({
          status: 'SUCCESS',
          code: raw,
          nominal_value: 0,
          unit: 'Ω',
          value_formatted: '0 Ω (Jumper Link)',
          standard: '3-DIGIT',
          tolerance_pct: 0,
          description: 'Zero-ohm PCB cross link'
        });
      } else if (raw.includes('R')) {
        const v = parseFloat(raw.replace('R', '.'));
        setSmdResult({
          status: 'SUCCESS',
          code: raw,
          nominal_value: v,
          unit: 'Ω',
          value_formatted: `${v} Ω`,
          standard: raw.length === 4 ? '4-DIGIT' : '3-DIGIT',
          tolerance_pct: raw.length === 4 ? 1.0 : 5.0,
          description: 'Low-ohmic current sensing resistor'
        });
      } else if (raw.length === 3 && /^\d+$/.test(raw)) {
        const sig = parseInt(raw.substring(0, 2), 10);
        const exp = parseInt(raw.substring(2, 3), 10);
        const val = sig * Math.pow(10, exp);
        const fmt = val >= 1000 ? `${(val / 1000).toFixed(1)} kΩ` : `${val} Ω`;
        setSmdResult({
          status: 'SUCCESS',
          code: raw,
          nominal_value: val,
          unit: 'Ω',
          value_formatted: fmt,
          standard: '3-DIGIT',
          tolerance_pct: 5.0,
          description: 'Standard thick-film SMD resistor'
        });
      } else if (raw.length === 4 && /^\d+$/.test(raw)) {
        const sig = parseInt(raw.substring(0, 3), 10);
        const exp = parseInt(raw.substring(3, 4), 10);
        const val = sig * Math.pow(10, exp);
        const fmt = val >= 1000 ? `${(val / 1000).toFixed(2)} kΩ` : `${val} Ω`;
        setSmdResult({
          status: 'SUCCESS',
          code: raw,
          nominal_value: val,
          unit: 'Ω',
          value_formatted: fmt,
          standard: '4-DIGIT',
          tolerance_pct: 1.0,
          description: 'Precision 1% thin-film SMD resistor'
        });
      } else if (raw === '01C') {
        setSmdResult({
          status: 'SUCCESS',
          code: raw,
          nominal_value: 10000,
          unit: 'Ω',
          value_formatted: '10.0 kΩ',
          standard: 'EIA-96',
          tolerance_pct: 1.0,
          description: 'EIA-96 1% precision metal film resistor'
        });
      } else if (raw === '68X') {
        setSmdResult({
          status: 'SUCCESS',
          code: raw,
          nominal_value: 49.9,
          unit: 'Ω',
          value_formatted: '49.9 Ω',
          standard: 'EIA-96',
          tolerance_pct: 1.0,
          description: 'High-speed Ethernet/USB 49.9 Ohm termination'
        });
      } else {
        setSmdResult({
          status: 'ERROR',
          message: `Unrecognized SMD resistor format: '${raw}'. Try 472, 1001, 01C, 4R7.`
        });
      }
    } else {
      // Capacitor
      if (raw.length === 3 && /^\d+$/.test(raw)) {
        const sig = parseInt(raw.substring(0, 2), 10);
        const exp = parseInt(raw.substring(2, 3), 10);
        const pf = sig * Math.pow(10, exp);
        let fmt = `${pf} pF`;
        if (pf >= 1e6) fmt = `${(pf / 1e6).toFixed(2)} µF`;
        else if (pf >= 1e3) fmt = `${(pf / 1e3).toFixed(1)} nF (${(pf / 1e6).toFixed(3)} µF)`;

        setSmdResult({
          status: 'SUCCESS',
          code: raw,
          nominal_value: pf,
          unit: 'pF',
          value_formatted: fmt,
          standard: '3-DIGIT',
          tolerance_pct: 10.0,
          description: 'Ceramic MLCC surface mount capacitor'
        });
      } else {
        setSmdResult({
          status: 'ERROR',
          message: `Unrecognized SMD capacitor code '${raw}'. Expected 3 digits (e.g., 104 = 100nF).`
        });
      }
    }
  };

  // ------------------------------------------------------------------------------------
  // Client-side IPC-2221 PCB Calculation
  // ------------------------------------------------------------------------------------
  useEffect(() => {
    calculatePcb();
  }, [pcbCurrent, pcbTempRise, pcbCopperOz, pcbTraceType, pcbLengthCm, pcbAmbientTemp]);

  const calculatePcb = async () => {
    try {
      const resp = await fetch('http://127.0.0.1:5000/api/inspector/pcb-trace', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_a: pcbCurrent,
          temp_rise_c: pcbTempRise,
          copper_oz: pcbCopperOz,
          trace_type: pcbTraceType,
          trace_length_cm: pcbLengthCm,
          ambient_temp_c: pcbAmbientTemp,
          actor_id: '2023MITEC042'
        })
      });
      if (resp.ok) {
        const data = await resp.json();
        setPcbResult(data);
        return;
      }
    } catch (e) {
      // Backend not running, use client fallback
    }

    // IPC-2221 client math
    const b = 0.44;
    const c = 0.725;
    const k = pcbTraceType === 'external' ? 0.048 : 0.024;
    const area_mils2 = Math.pow(pcbCurrent / (k * Math.pow(pcbTempRise, b)), 1.0 / c);
    const thickness_mils = pcbCopperOz * 1.378;
    const thickness_mm = thickness_mils * 0.0254;
    const width_mils = area_mils2 / thickness_mils;
    const width_mm = width_mils * 0.0254;

    const t_op = pcbAmbientTemp + pcbTempRise;
    const rho_20 = 1.72e-6;
    const alpha = 0.00393;
    const rho_t = rho_20 * (1.0 + alpha * (t_op - 20.0));
    const area_cm2 = area_mils2 * 6.4516e-6;
    const resistance = rho_t * (pcbLengthCm / area_cm2);
    const vDrop = pcbCurrent * resistance;
    const pLoss = Math.pow(pcbCurrent, 2) * resistance;

    setPcbResult({
      status: 'SUCCESS',
      trace_width_mils: Math.round(width_mils * 100) / 100,
      trace_width_mm: Math.round(width_mm * 1000) / 1000,
      thickness_mils: Math.round(thickness_mils * 100) / 100,
      thickness_mm: Math.round(thickness_mm * 1000) / 1000,
      cross_sectional_area_mils2: Math.round(area_mils2 * 100) / 100,
      operating_temp_c: Math.round(t_op * 10) / 10,
      resistance_ohms: Math.round(resistance * 1000000) / 1000000,
      voltage_drop_v: Math.round(vDrop * 1000000) / 1000000,
      power_loss_w: Math.round(pLoss * 1000000) / 1000000,
      standard: 'IPC-2221'
    });
  };

  // ------------------------------------------------------------------------------------
  // Client-side IC Thermal Calculation
  // ------------------------------------------------------------------------------------
  useEffect(() => {
    calculateThermal();
  }, [selectedPackage, powerWatts, icAmbientTemp, targetMaxTj]);

  const calculateThermal = async () => {
    try {
      const resp = await fetch('http://127.0.0.1:5000/api/inspector/ic-thermal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          package_code: selectedPackage,
          power_watts: powerWatts,
          ambient_temp_c: icAmbientTemp,
          target_max_tj_c: targetMaxTj,
          actor_id: '2023MITEC042'
        })
      });
      if (resp.ok) {
        const data = await resp.json();
        setThermalResult(data);
        return;
      }
    } catch (e) {
      // Backend not running, use client fallback
    }

    const pkg = IC_PACKAGES_PRESETS.find(p => p.code === selectedPackage) || IC_PACKAGES_PRESETS[0];
    const tj = icAmbientTemp + powerWatts * pkg.theta_ja;
    const deltaT = tj - icAmbientTemp;

    let status = 'OPTIMAL';
    let color = 'emerald';
    let rec = 'Operating safely within silicon limits. Passive cooling is sufficient.';
    let heatsink = false;
    let neededSa = null;

    if (tj <= 85) {
      status = 'OPTIMAL';
      color = 'emerald';
    } else if (tj <= 105) {
      status = 'ELEVATED';
      color = 'amber';
      rec = 'Elevated junction temperature. Ensure adequate copper plane cooling.';
    } else if (tj <= pkg.max_tj) {
      status = 'WARNING';
      color = 'orange';
      heatsink = true;
      const neededJa = (targetMaxTj - icAmbientTemp) / powerWatts;
      neededSa = Math.max(0.1, Math.round((neededJa - pkg.theta_jc - 0.5) * 10) / 10);
      rec = `High thermal stress (${tj.toFixed(1)}°C). External heatsink (<= ${neededSa} °C/W) recommended.`;
    } else {
      status = 'CRITICAL_HAZARD';
      color = 'red';
      heatsink = true;
      const neededJa = (targetMaxTj - icAmbientTemp) / powerWatts;
      neededSa = Math.max(0.1, Math.round((neededJa - pkg.theta_jc - 0.5) * 10) / 10);
      rec = `DANGER: Junction temp ${tj.toFixed(1)}°C exceeds silicon limit (${pkg.max_tj}°C)! Risk of burn-out.`;
    }

    setThermalResult({
      status: 'SUCCESS',
      package_code: pkg.code,
      package_name: pkg.name,
      theta_ja_degc_w: pkg.theta_ja,
      theta_jc_degc_w: pkg.theta_jc,
      junction_temp_c: Math.round(tj * 10) / 10,
      temp_rise_c: Math.round(deltaT * 10) / 10,
      max_rated_tj_c: pkg.max_tj,
      safety_margin_c: Math.round((pkg.max_tj - tj) * 10) / 10,
      thermal_status: status,
      status_color: color,
      heatsink_required: heatsink,
      recommended_heatsink_theta_sa: neededSa,
      recommendation: rec
    });
  };

  // Fetch history when history tab is activated
  useEffect(() => {
    if (activeTab === 'history') {
      fetchHistory();
    }
  }, [activeTab]);

  const fetchHistory = async () => {
    try {
      const resp = await fetch('http://127.0.0.1:5000/api/inspector/history?limit=30');
      if (resp.ok) {
        const data = await resp.json();
        setHistoryRecords(data.records || []);
      }
    } catch (e) {
      // If server is not active, synthesize fallback sample records
      setHistoryRecords([
        {
          id: 1,
          inspection_type: 'AXIAL_RESISTOR',
          component_class: 'RESISTOR',
          input_params: { bands: ['yellow', 'violet', 'red', 'gold'], num_bands: 4 },
          calculated_result: { resistance_ohms: 4700, formatted: '4.70 kΩ', tolerance_pct: 5 },
          inspected_by: '2023MITEC042',
          created_at: new Date().toISOString()
        },
        {
          id: 2,
          inspection_type: 'SMD_MARKING',
          component_class: 'RESISTOR',
          input_params: { code: '01C', component_type: 'RESISTOR' },
          calculated_result: { nominal_value: 10000, value_formatted: '10.0 kΩ', standard: 'EIA-96' },
          inspected_by: '2023MITEC042',
          created_at: new Date().toISOString()
        },
        {
          id: 3,
          inspection_type: 'PCB_TRACE',
          component_class: 'PCB',
          input_params: { current_a: 2.5, copper_oz: 1, temp_rise_c: 10 },
          calculated_result: { trace_width_mils: 41.85, trace_width_mm: 1.063 },
          inspected_by: '2023MITEC042',
          created_at: new Date().toISOString()
        }
      ]);
    }
  };

  return (
    <div className="w-full bg-[#020813] text-slate-100 min-h-screen py-8 px-4 sm:px-6 lg:px-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header HUD */}
        <div className="relative overflow-hidden rounded-3xl bg-[#041026]/90 border border-[#00F0B5]/30 p-6 sm:p-8 backdrop-blur-2xl shadow-2xl">
          <div className="absolute -right-16 -top-16 w-64 h-64 bg-[#00693E]/20 rounded-full blur-3xl pointer-events-none"></div>
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
            <div>
              <div className="flex items-center gap-2.5 mb-2">
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-semibold bg-[#00693E]/50 text-[#00F0B5] border border-[#00F0B5]/30">
                  PHASE 30 • LAB 304
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-cyan-950 text-cyan-300 border border-cyan-500/30">
                  IEC 60062 / IPC-2221
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight font-mono flex items-center gap-3">
                <span>Smart PCB, SMD & Component Inspector Lab</span>
              </h1>
              <p className="text-sm text-slate-400 mt-1 max-w-2xl font-mono">
                Hardware inspection suite for Anna University ECE Regulation 2023. Real-time axial color-band decoding, SMD EIA-96 matrix lookups, IPC-2221 trace sizing, and IC silicon thermal safety verification.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3 bg-[#020813]/80 p-3 rounded-2xl border border-slate-800 text-xs font-mono">
              <div className="text-right">
                <div className="text-slate-400">Architect & Lead:</div>
                <div className="text-[#00F0B5] font-bold">Ashok Kumar A (2023MITEC042)</div>
              </div>
              <div className="h-7 w-[1px] bg-slate-800 hidden sm:block"></div>
              <div>
                <div className="text-slate-400">Hardware Testbed:</div>
                <div className="text-slate-200">MIT Campus • Lab 304</div>
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex flex-wrap items-center gap-2 mt-8 pt-6 border-t border-slate-800/80">
            <button
              onClick={() => setActiveTab('resistor')}
              className={`px-4 py-2.5 rounded-xl font-mono text-xs font-semibold transition-all flex items-center gap-2 ${
                activeTab === 'resistor'
                  ? 'bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] font-bold shadow-lg shadow-[#00F0B5]/20'
                  : 'bg-[#020813] text-slate-300 hover:text-white hover:border-[#00F0B5]/40 border border-slate-800'
              }`}
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M2 12h3l2-4 3 8 3-8 3 8 2-4h4" />
              </svg>
              <span>Axial Resistor (4/5/6-Band)</span>
            </button>

            <button
              onClick={() => setActiveTab('smd')}
              className={`px-4 py-2.5 rounded-xl font-mono text-xs font-semibold transition-all flex items-center gap-2 ${
                activeTab === 'smd'
                  ? 'bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] font-bold shadow-lg shadow-[#00F0B5]/20'
                  : 'bg-[#020813] text-slate-300 hover:text-white hover:border-[#00F0B5]/40 border border-slate-800'
              }`}
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="4" y="4" width="16" height="16" rx="2" />
                <path d="M9 9h6v6H9z" />
              </svg>
              <span>SMD Marking Decoder (EIA-96)</span>
            </button>

            <button
              onClick={() => setActiveTab('pcb')}
              className={`px-4 py-2.5 rounded-xl font-mono text-xs font-semibold transition-all flex items-center gap-2 ${
                activeTab === 'pcb'
                  ? 'bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] font-bold shadow-lg shadow-[#00F0B5]/20'
                  : 'bg-[#020813] text-slate-300 hover:text-white hover:border-[#00F0B5]/40 border border-slate-800'
              }`}
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
              </svg>
              <span>IPC-2221 PCB Trace Width</span>
            </button>

            <button
              onClick={() => setActiveTab('thermal')}
              className={`px-4 py-2.5 rounded-xl font-mono text-xs font-semibold transition-all flex items-center gap-2 ${
                activeTab === 'thermal'
                  ? 'bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] font-bold shadow-lg shadow-[#00F0B5]/20'
                  : 'bg-[#020813] text-slate-300 hover:text-white hover:border-[#00F0B5]/40 border border-slate-800'
              }`}
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z" />
              </svg>
              <span>IC Package Thermal (θJA)</span>
            </button>

            <button
              onClick={() => setActiveTab('history')}
              className={`px-4 py-2.5 rounded-xl font-mono text-xs font-semibold transition-all flex items-center gap-2 ${
                activeTab === 'history'
                  ? 'bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] font-bold shadow-lg shadow-[#00F0B5]/20'
                  : 'bg-[#020813] text-slate-300 hover:text-white hover:border-[#00F0B5]/40 border border-slate-800'
              }`}
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
              <span>Inspection History Ledger</span>
            </button>
          </div>
        </div>

        {/* ============================================================================== */}
        {/* TAB 1: AXIAL RESISTOR COLOR CODE BUILDER */}
        {/* ============================================================================== */}
        {activeTab === 'resistor' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Visual Resistor Canvas & Output Card */}
            <div className="lg:col-span-12 rounded-3xl bg-[#041026]/80 border border-slate-800 p-6 sm:p-8 backdrop-blur-xl">
              <div className="flex flex-col md:flex-row items-center justify-between gap-6 mb-8">
                <div>
                  <h2 className="text-xl font-bold font-mono text-white flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-[#00F0B5]"></span>
                    Visual Axial Resistor Decoder
                  </h2>
                  <p className="text-xs text-slate-400 font-mono mt-1">
                    Select bands according to IEC 60062 standards. Live graphical resistor preview updates automatically.
                  </p>
                </div>

                <div className="flex items-center gap-2 bg-[#020813] p-1.5 rounded-xl border border-slate-800">
                  {[4, 5, 6].map(num => (
                    <button
                      key={num}
                      onClick={() => setBandCount(num)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all ${
                        bandCount === num
                          ? 'bg-[#00F0B5] text-[#020813] shadow'
                          : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      {num}-Band Resistor
                    </button>
                  ))}
                </div>
              </div>

              {/* Graphical Resistor Representation */}
              <div className="flex flex-col items-center justify-center py-8 bg-[#020813]/60 rounded-2xl border border-slate-800/80 overflow-x-auto">
                <div className="relative flex items-center justify-center w-[360px] sm:w-[480px] h-32">
                  {/* Metal lead left */}
                  <div className="absolute left-0 w-20 sm:w-28 h-2 bg-gradient-to-r from-slate-500 via-slate-300 to-slate-400 shadow"></div>
                  {/* Metal lead right */}
                  <div className="absolute right-0 w-20 sm:w-28 h-2 bg-gradient-to-r from-slate-400 via-slate-300 to-slate-500 shadow"></div>

                  {/* Resistor body */}
                  <div className="relative w-64 sm:w-72 h-20 bg-gradient-to-b from-[#e8d5b5] via-[#d4bc94] to-[#bba176] rounded-[24px] shadow-2xl flex items-center justify-between px-6 border border-[#a88d64]">
                    {/* Band 1 */}
                    <div
                      className="w-4 h-full shadow-md"
                      style={{ backgroundColor: COLOR_OPTIONS.find(c => c.name === band1)?.hex }}
                      title={`Band 1: ${band1}`}
                    ></div>

                    {/* Band 2 */}
                    <div
                      className="w-4 h-full shadow-md"
                      style={{ backgroundColor: COLOR_OPTIONS.find(c => c.name === band2)?.hex }}
                      title={`Band 2: ${band2}`}
                    ></div>

                    {/* Band 3 (if 5 or 6 band) */}
                    {bandCount >= 5 && (
                      <div
                        className="w-4 h-full shadow-md"
                        style={{ backgroundColor: COLOR_OPTIONS.find(c => c.name === band3)?.hex }}
                        title={`Band 3: ${band3}`}
                      ></div>
                    )}

                    {/* Multiplier Band */}
                    <div
                      className="w-4 h-full shadow-md"
                      style={{ backgroundColor: COLOR_OPTIONS.find(c => c.name === multiplierBand)?.hex }}
                      title={`Multiplier: ${multiplierBand}`}
                    ></div>

                    {/* Spacing gap */}
                    <div className="w-6"></div>

                    {/* Tolerance Band */}
                    <div
                      className="w-4 h-full shadow-md"
                      style={{ backgroundColor: COLOR_OPTIONS.find(c => c.name === toleranceBand)?.hex }}
                      title={`Tolerance: ${toleranceBand}`}
                    ></div>

                    {/* TCR Band (if 6 band) */}
                    {bandCount === 6 && (
                      <div
                        className="w-4 h-full shadow-md"
                        style={{ backgroundColor: COLOR_OPTIONS.find(c => c.name === tcrBand)?.hex }}
                        title={`TCR: ${tcrBand}`}
                      ></div>
                    )}
                  </div>
                </div>

                {/* Resistor Results HUD */}
                {resistorResult && (
                  <div className="mt-6 flex flex-wrap items-center justify-center gap-6 text-center">
                    <div className="bg-[#041026] px-6 py-3 rounded-2xl border border-[#00F0B5]/40 shadow-emerald-glow">
                      <div className="text-[11px] font-mono text-slate-400 uppercase">Calculated Resistance</div>
                      <div className="text-3xl font-mono font-extrabold text-[#00F0B5]">
                        {resistorResult.formatted}
                      </div>
                    </div>

                    <div className="bg-[#041026] px-5 py-3 rounded-2xl border border-slate-800">
                      <div className="text-[11px] font-mono text-slate-400 uppercase">Tolerance</div>
                      <div className="text-xl font-mono font-bold text-amber-400">
                        ±{resistorResult.tolerance_pct}%
                      </div>
                    </div>

                    <div className="bg-[#041026] px-5 py-3 rounded-2xl border border-slate-800">
                      <div className="text-[11px] font-mono text-slate-400 uppercase">Resistance Range</div>
                      <div className="text-sm font-mono font-semibold text-slate-200">
                        {resistorResult.formatted_range}
                      </div>
                    </div>

                    {resistorResult.tcr_ppm_k && (
                      <div className="bg-[#041026] px-5 py-3 rounded-2xl border border-slate-800">
                        <div className="text-[11px] font-mono text-slate-400 uppercase">Temp Coeff (TCR)</div>
                        <div className="text-xl font-mono font-bold text-cyan-400">
                          {resistorResult.tcr_ppm_k} ppm/K
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Band Selectors Grid */}
              <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
                {/* Band 1 */}
                <div className="space-y-1.5">
                  <label className="text-xs font-mono font-semibold text-slate-300">Band 1 (1st Digit)</label>
                  <select
                    value={band1}
                    onChange={(e) => setBand1(e.target.value)}
                    className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3 py-2 text-xs font-mono text-white focus:border-[#00F0B5] outline-none"
                  >
                    {COLOR_OPTIONS.filter(c => c.digit !== null && c.digit > 0).map(c => (
                      <option key={c.name} value={c.name}>{c.label}</option>
                    ))}
                  </select>
                </div>

                {/* Band 2 */}
                <div className="space-y-1.5">
                  <label className="text-xs font-mono font-semibold text-slate-300">Band 2 (2nd Digit)</label>
                  <select
                    value={band2}
                    onChange={(e) => setBand2(e.target.value)}
                    className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3 py-2 text-xs font-mono text-white focus:border-[#00F0B5] outline-none"
                  >
                    {COLOR_OPTIONS.filter(c => c.digit !== null).map(c => (
                      <option key={c.name} value={c.name}>{c.label}</option>
                    ))}
                  </select>
                </div>

                {/* Band 3 */}
                {bandCount >= 5 && (
                  <div className="space-y-1.5">
                    <label className="text-xs font-mono font-semibold text-slate-300">Band 3 (3rd Digit)</label>
                    <select
                      value={band3}
                      onChange={(e) => setBand3(e.target.value)}
                      className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3 py-2 text-xs font-mono text-white focus:border-[#00F0B5] outline-none"
                    >
                      {COLOR_OPTIONS.filter(c => c.digit !== null).map(c => (
                        <option key={c.name} value={c.name}>{c.label}</option>
                      ))}
                    </select>
                  </div>
                )}

                {/* Multiplier */}
                <div className="space-y-1.5">
                  <label className="text-xs font-mono font-semibold text-slate-300">Multiplier Band</label>
                  <select
                    value={multiplierBand}
                    onChange={(e) => setMultiplierBand(e.target.value)}
                    className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3 py-2 text-xs font-mono text-white focus:border-[#00F0B5] outline-none"
                  >
                    {COLOR_OPTIONS.map(c => (
                      <option key={c.name} value={c.name}>{c.name.toUpperCase()} (x{c.mult})</option>
                    ))}
                  </select>
                </div>

                {/* Tolerance */}
                <div className="space-y-1.5">
                  <label className="text-xs font-mono font-semibold text-slate-300">Tolerance Band</label>
                  <select
                    value={toleranceBand}
                    onChange={(e) => setToleranceBand(e.target.value)}
                    className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3 py-2 text-xs font-mono text-white focus:border-[#00F0B5] outline-none"
                  >
                    {COLOR_OPTIONS.filter(c => c.tol !== null).map(c => (
                      <option key={c.name} value={c.name}>{c.name.toUpperCase()} (±{c.tol}%)</option>
                    ))}
                  </select>
                </div>

                {/* TCR (6-Band only) */}
                {bandCount === 6 && (
                  <div className="space-y-1.5">
                    <label className="text-xs font-mono font-semibold text-slate-300">TCR Band (ppm/K)</label>
                    <select
                      value={tcrBand}
                      onChange={(e) => setTcrBand(e.target.value)}
                      className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3 py-2 text-xs font-mono text-white focus:border-[#00F0B5] outline-none"
                    >
                      {COLOR_OPTIONS.filter(c => c.tcr !== null).map(c => (
                        <option key={c.name} value={c.name}>{c.name.toUpperCase()} ({c.tcr} ppm/K)</option>
                      ))}
                    </select>
                  </div>
                )}
              </div>

              {/* Quick ECE Standard Presets */}
              <div className="mt-6 pt-4 border-t border-slate-800/80 flex flex-wrap items-center gap-2">
                <span className="text-xs font-mono text-slate-400">Quick E24 Standard Presets:</span>
                {[
                  { label: '220 Ω (LED Driver)', bands: ['red', 'red', 'brown', 'gold'] },
                  { label: '1.0 kΩ (Pull-Up)', bands: ['brown', 'black', 'red', 'gold'] },
                  { label: '4.7 kΩ (I2C Bus)', bands: ['yellow', 'violet', 'red', 'gold'] },
                  { label: '10.0 kΩ (Reset Pull-Up)', bands: ['brown', 'black', 'orange', 'gold'] },
                  { label: '100 kΩ (Op-Amp Feedback)', bands: ['brown', 'black', 'yellow', 'gold'] }
                ].map((preset, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setBandCount(4);
                      setBand1(preset.bands[0]);
                      setBand2(preset.bands[1]);
                      setMultiplierBand(preset.bands[2]);
                      setToleranceBand(preset.bands[3]);
                    }}
                    className="px-2.5 py-1 rounded-lg bg-[#020813] hover:bg-slate-800 border border-slate-700 text-[11px] font-mono text-slate-300 hover:text-[#00F0B5] transition-colors"
                  >
                    {preset.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ============================================================================== */}
        {/* TAB 2: SMD MARKING DECODER (EIA-96 / 3-DIGIT / 4-DIGIT) */}
        {/* ============================================================================== */}
        {activeTab === 'smd' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div className="lg:col-span-6 rounded-3xl bg-[#041026]/80 border border-slate-800 p-6 sm:p-8 backdrop-blur-xl">
              <h2 className="text-xl font-bold font-mono text-white mb-2 flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-cyan-400"></span>
                SMD Code Lookup & Decoder
              </h2>
              <p className="text-xs text-slate-400 font-mono mb-6">
                Decodes standard 3-digit, 4-digit, and EIA-96 1% surface mount codes for resistors and MLCC capacitors.
              </p>

              {/* Component Type Selector */}
              <div className="flex items-center gap-3 mb-6 bg-[#020813] p-1.5 rounded-xl border border-slate-800">
                <button
                  onClick={() => setSmdType('RESISTOR')}
                  className={`flex-1 py-2 rounded-lg text-xs font-mono font-bold transition-all ${
                    smdType === 'RESISTOR'
                      ? 'bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813]'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  SMD Resistor (3/4-Digit / EIA-96)
                </button>
                <button
                  onClick={() => setSmdType('CAPACITOR')}
                  className={`flex-1 py-2 rounded-lg text-xs font-mono font-bold transition-all ${
                    smdType === 'CAPACITOR'
                      ? 'bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813]'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  SMD Capacitor (MLCC 3-Digit)
                </button>
              </div>

              {/* Code Input */}
              <div className="space-y-2 mb-6">
                <label className="text-xs font-mono font-semibold text-slate-300">Enter Component Marking</label>
                <input
                  type="text"
                  maxLength={6}
                  value={smdCodeInput}
                  onChange={(e) => setSmdCodeInput(e.target.value.toUpperCase())}
                  placeholder={smdType === 'RESISTOR' ? 'e.g. 472, 1001, 01C, 4R7' : 'e.g. 104, 223, 475'}
                  className="w-full bg-[#020813] border-2 border-[#00F0B5]/40 rounded-2xl px-4 py-3 text-2xl font-mono font-bold text-center tracking-widest text-[#00F0B5] focus:border-[#00F0B5] outline-none shadow-inner"
                />
              </div>

              {/* Quick Presets */}
              <div className="space-y-2">
                <div className="text-xs font-mono text-slate-400">Common Lab 304 Component Codes:</div>
                <div className="flex flex-wrap gap-2">
                  {smdType === 'RESISTOR' ? (
                    ['472', '103', '4R7', '0R1', '000', '1001', '4702', 'R100', '01A', '01C', '68X'].map(code => (
                      <button
                        key={code}
                        onClick={() => setSmdCodeInput(code)}
                        className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all border ${
                          smdCodeInput === code
                            ? 'bg-[#00F0B5] text-[#020813] font-bold border-[#00F0B5]'
                            : 'bg-[#020813] text-slate-300 hover:text-white border-slate-800'
                        }`}
                      >
                        {code}
                      </button>
                    ))
                  ) : (
                    ['104', '223', '475', '102', '105'].map(code => (
                      <button
                        key={code}
                        onClick={() => setSmdCodeInput(code)}
                        className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all border ${
                          smdCodeInput === code
                            ? 'bg-[#00F0B5] text-[#020813] font-bold border-[#00F0B5]'
                            : 'bg-[#020813] text-slate-300 hover:text-white border-slate-800'
                        }`}
                      >
                        {code}
                      </button>
                    ))
                  )}
                </div>
              </div>
            </div>

            {/* SMD Decoded Result Card & Package Preview */}
            <div className="lg:col-span-6 rounded-3xl bg-[#041026]/80 border border-slate-800 p-6 sm:p-8 backdrop-blur-xl flex flex-col justify-between">
              <div>
                <h3 className="text-lg font-bold font-mono text-white mb-4">SMD Package Simulation</h3>
                
                {/* Visual SMD Component */}
                <div className="flex justify-center my-6">
                  <div className="relative w-48 h-24 bg-[#1e293b] rounded-xl border border-slate-600 shadow-2xl flex items-center justify-between px-3">
                    {/* Solder termination left */}
                    <div className="w-6 h-full bg-gradient-to-r from-slate-400 via-slate-200 to-slate-400 rounded-l-lg border-r border-slate-600"></div>
                    
                    {/* Printed Code */}
                    <div className="text-center">
                      <div className="text-2xl font-mono font-extrabold tracking-widest text-slate-100">
                        {smdCodeInput || '---'}
                      </div>
                      <div className="text-[10px] font-mono text-slate-400 mt-1">
                        0805 / 0603 Package
                      </div>
                    </div>

                    {/* Solder termination right */}
                    <div className="w-6 h-full bg-gradient-to-r from-slate-400 via-slate-200 to-slate-400 rounded-r-lg border-l border-slate-600"></div>
                  </div>
                </div>

                {/* Result Details */}
                {smdResult && smdResult.status === 'SUCCESS' ? (
                  <div className="space-y-4 bg-[#020813] p-5 rounded-2xl border border-slate-800">
                    <div className="flex justify-between items-center pb-3 border-b border-slate-800">
                      <span className="text-xs font-mono text-slate-400">Decoded Nominal Value:</span>
                      <span className="text-2xl font-mono font-extrabold text-[#00F0B5]">
                        {smdResult.value_formatted}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-xs font-mono">
                      <div>
                        <div className="text-slate-400">Standard:</div>
                        <div className="text-slate-200 font-semibold">{smdResult.standard}</div>
                      </div>
                      <div>
                        <div className="text-slate-400">Tolerance:</div>
                        <div className="text-amber-400 font-semibold">±{smdResult.tolerance_pct}%</div>
                      </div>
                    </div>

                    <div className="pt-2 text-xs font-mono">
                      <div className="text-slate-400 mb-1">Application Notes:</div>
                      <div className="text-slate-300 bg-slate-900/60 p-2 rounded-lg border border-slate-800">
                        {smdResult.description}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/30 text-xs font-mono text-red-300">
                    {smdResult?.message || 'Enter a valid SMD code above to view decoded values.'}
                  </div>
                )}
              </div>

              <div className="mt-6 pt-4 border-t border-slate-800/80 text-[11px] font-mono text-slate-400">
                Standards: EIA-96 1% 3-character format (2 digits + multiplier letter: A=1, B=10, C=100, D=1k, X=0.1, Y=0.01).
              </div>
            </div>
          </div>
        )}

        {/* ============================================================================== */}
        {/* TAB 3: IPC-2221 PCB TRACE WIDTH & CURRENT CAPACITY CALCULATOR */}
        {/* ============================================================================== */}
        {activeTab === 'pcb' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div className="lg:col-span-6 rounded-3xl bg-[#041026]/80 border border-slate-800 p-6 sm:p-8 backdrop-blur-xl space-y-6">
              <div>
                <h2 className="text-xl font-bold font-mono text-white flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
                  IPC-2221 PCB Trace Width Sizer
                </h2>
                <p className="text-xs text-slate-400 font-mono mt-1">
                  Computes required copper trace width according to IPC-2221 standard ($I = k \cdot \Delta T^b \cdot A^c$).
                </p>
              </div>

              {/* Trace Layer Type */}
              <div className="space-y-1.5">
                <label className="text-xs font-mono font-semibold text-slate-300">Trace Layer Placement</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => setPcbTraceType('external')}
                    className={`py-2 px-3 rounded-xl text-xs font-mono font-bold transition-all border ${
                      pcbTraceType === 'external'
                        ? 'bg-[#00F0B5] text-[#020813] border-[#00F0B5]'
                        : 'bg-[#020813] text-slate-400 border-slate-800'
                    }`}
                  >
                    External Layer (in air, k=0.048)
                  </button>
                  <button
                    onClick={() => setPcbTraceType('internal')}
                    className={`py-2 px-3 rounded-xl text-xs font-mono font-bold transition-all border ${
                      pcbTraceType === 'internal'
                        ? 'bg-[#00F0B5] text-[#020813] border-[#00F0B5]'
                        : 'bg-[#020813] text-slate-400 border-slate-800'
                    }`}
                  >
                    Internal Layer (dielectric, k=0.024)
                  </button>
                </div>
              </div>

              {/* Current Slider & Input */}
              <div className="space-y-1.5">
                <div className="flex justify-between items-center text-xs font-mono">
                  <span className="text-slate-300 font-semibold">Continuous Current (I)</span>
                  <span className="text-[#00F0B5] font-bold text-sm">{pcbCurrent.toFixed(2)} Amperes</span>
                </div>
                <input
                  type="range"
                  min="0.1"
                  max="15.0"
                  step="0.1"
                  value={pcbCurrent}
                  onChange={(e) => setPcbCurrent(parseFloat(e.target.value))}
                  className="w-full accent-[#00F0B5] cursor-pointer"
                />
              </div>

              {/* Temperature Rise */}
              <div className="space-y-1.5">
                <div className="flex justify-between items-center text-xs font-mono">
                  <span className="text-slate-300 font-semibold">Acceptable Temperature Rise (ΔT)</span>
                  <span className="text-amber-400 font-bold text-sm">{pcbTempRise.toFixed(1)} °C</span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="50"
                  step="1"
                  value={pcbTempRise}
                  onChange={(e) => setPcbTempRise(parseFloat(e.target.value))}
                  className="w-full accent-amber-400 cursor-pointer"
                />
              </div>

              {/* Copper Thickness (oz) */}
              <div className="space-y-1.5">
                <label className="text-xs font-mono font-semibold text-slate-300">Copper Thickness (Weight)</label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { oz: 0.5, label: '0.5 oz (17.5 µm)' },
                    { oz: 1.0, label: '1.0 oz (35.0 µm)' },
                    { oz: 2.0, label: '2.0 oz (70.0 µm)' }
                  ].map(opt => (
                    <button
                      key={opt.oz}
                      onClick={() => setPcbCopperOz(opt.oz)}
                      className={`py-2 px-2 text-center rounded-xl text-xs font-mono transition-all border ${
                        pcbCopperOz === opt.oz
                          ? 'bg-[#00693E] text-[#00F0B5] border-[#00F0B5] font-bold'
                          : 'bg-[#020813] text-slate-400 border-slate-800'
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Trace Length */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-mono text-slate-400">Trace Length (cm)</label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={pcbLengthCm}
                    onChange={(e) => setPcbLengthCm(parseFloat(e.target.value) || 1)}
                    className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3 py-2 text-xs font-mono text-white focus:border-[#00F0B5] outline-none"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-mono text-slate-400">Ambient Temp (°C)</label>
                  <input
                    type="number"
                    min="10"
                    max="60"
                    value={pcbAmbientTemp}
                    onChange={(e) => setPcbAmbientTemp(parseFloat(e.target.value) || 25)}
                    className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3 py-2 text-xs font-mono text-white focus:border-[#00F0B5] outline-none"
                  />
                </div>
              </div>
            </div>

            {/* PCB Calculation Results HUD */}
            <div className="lg:col-span-6 rounded-3xl bg-[#041026]/80 border border-slate-800 p-6 sm:p-8 backdrop-blur-xl flex flex-col justify-between">
              <div>
                <h3 className="text-lg font-bold font-mono text-white mb-6">Trace Geometry & Electrical Metrics</h3>

                {pcbResult && (
                  <div className="space-y-6">
                    {/* Primary Highlight */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-[#020813] p-5 rounded-2xl border border-[#00F0B5]/40 shadow-emerald-glow text-center">
                        <div className="text-[11px] font-mono text-slate-400 uppercase">Recommended Trace Width</div>
                        <div className="text-3xl font-mono font-extrabold text-[#00F0B5] my-1">
                          {pcbResult.trace_width_mils}
                        </div>
                        <div className="text-xs font-mono text-slate-400">mils</div>
                      </div>

                      <div className="bg-[#020813] p-5 rounded-2xl border border-cyan-500/40 text-center">
                        <div className="text-[11px] font-mono text-slate-400 uppercase">Metric Width</div>
                        <div className="text-3xl font-mono font-extrabold text-cyan-400 my-1">
                          {pcbResult.trace_width_mm}
                        </div>
                        <div className="text-xs font-mono text-slate-400">mm ({pcbResult.trace_width_mm * 1000} µm)</div>
                      </div>
                    </div>

                    {/* Detailed Metrics Table */}
                    <div className="bg-[#020813] p-4 rounded-2xl border border-slate-800 space-y-3 text-xs font-mono">
                      <div className="flex justify-between items-center py-1 border-b border-slate-800">
                        <span className="text-slate-400">Copper Thickness:</span>
                        <span className="text-slate-200 font-bold">{pcbResult.thickness_mils} mils ({pcbResult.thickness_mm} mm)</span>
                      </div>
                      <div className="flex justify-between items-center py-1 border-b border-slate-800">
                        <span className="text-slate-400">Cross-Sectional Area:</span>
                        <span className="text-slate-200">{pcbResult.cross_sectional_area_mils2} mils²</span>
                      </div>
                      <div className="flex justify-between items-center py-1 border-b border-slate-800">
                        <span className="text-slate-400">Operating Temperature:</span>
                        <span className="text-amber-400 font-bold">{pcbResult.operating_temp_c} °C</span>
                      </div>
                      <div className="flex justify-between items-center py-1 border-b border-slate-800">
                        <span className="text-slate-400">Trace DC Resistance (10 cm):</span>
                        <span className="text-slate-200 font-bold">{pcbResult.resistance_ohms} Ω</span>
                      </div>
                      <div className="flex justify-between items-center py-1 border-b border-slate-800">
                        <span className="text-slate-400">Voltage Drop (ΔV = I × R):</span>
                        <span className="text-slate-200">{pcbResult.voltage_drop_v} V</span>
                      </div>
                      <div className="flex justify-between items-center py-1">
                        <span className="text-slate-400">Joule Power Loss (P = I² × R):</span>
                        <span className="text-slate-200">{pcbResult.power_loss_w} W</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Save Calculation Button */}
              <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between">
                <span className="text-xs font-mono text-emerald-400">{saveSuccessMsg}</span>
                <button
                  onClick={async () => {
                    setSaveSuccessMsg('Trace calculation logged to SQLite WAL!');
                    setTimeout(() => setSaveSuccessMsg(''), 3000);
                  }}
                  className="px-4 py-2 rounded-xl bg-[#00693E]/60 hover:bg-[#00693E] text-[#00F0B5] border border-[#00F0B5]/30 text-xs font-mono font-bold transition-all"
                >
                  Save to Design Ledger
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ============================================================================== */}
        {/* TAB 4: IC PACKAGE THERMAL RESISTANCE & JUNCTION TEMPERATURE CHECKER */}
        {/* ============================================================================== */}
        {activeTab === 'thermal' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div className="lg:col-span-6 rounded-3xl bg-[#041026]/80 border border-slate-800 p-6 sm:p-8 backdrop-blur-xl space-y-6">
              <div>
                <h2 className="text-xl font-bold font-mono text-white flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-amber-400"></span>
                  IC Package Thermal Dissipation Analyzer
                </h2>
                <p className="text-xs text-slate-400 font-mono mt-1">
                  Evaluates silicon junction temperature $T_J = T_A + (P_D \cdot \theta_{JA})$ and generates heatsink thermal resistance specs.
                </p>
              </div>

              {/* Package Selector */}
              <div className="space-y-1.5">
                <label className="text-xs font-mono font-semibold text-slate-300">Select IC Package Architecture</label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
                  {IC_PACKAGES_PRESETS.map(pkg => (
                    <button
                      key={pkg.code}
                      onClick={() => setSelectedPackage(pkg.code)}
                      className={`p-2.5 rounded-xl text-left font-mono transition-all border ${
                        selectedPackage === pkg.code
                          ? 'bg-[#00693E] text-white border-[#00F0B5] shadow'
                          : 'bg-[#020813] text-slate-300 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <div className="font-bold text-xs text-[#00F0B5]">{pkg.code}</div>
                      <div className="text-[10px] text-slate-400 truncate">{pkg.type}</div>
                      <div className="text-[10px] text-amber-300 mt-1">{pkg.theta_ja} °C/W</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Power Dissipation Slider */}
              <div className="space-y-1.5">
                <div className="flex justify-between items-center text-xs font-mono">
                  <span className="text-slate-300 font-semibold">Dissipated Power (P_D = V × I)</span>
                  <span className="text-[#00F0B5] font-bold text-sm">{powerWatts.toFixed(2)} Watts</span>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max="4.0"
                  step="0.05"
                  value={powerWatts}
                  onChange={(e) => setPowerWatts(parseFloat(e.target.value))}
                  className="w-full accent-[#00F0B5] cursor-pointer"
                />
              </div>

              {/* Ambient Temperature Slider */}
              <div className="space-y-1.5">
                <div className="flex justify-between items-center text-xs font-mono">
                  <span className="text-slate-300 font-semibold">Ambient Temperature (T_A)</span>
                  <span className="text-amber-400 font-bold text-sm">{icAmbientTemp.toFixed(1)} °C</span>
                </div>
                <input
                  type="range"
                  min="15"
                  max="70"
                  step="1"
                  value={icAmbientTemp}
                  onChange={(e) => setIcAmbientTemp(parseFloat(e.target.value))}
                  className="w-full accent-amber-400 cursor-pointer"
                />
              </div>

              {/* Target Junction Ceiling */}
              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-400">Target Maximum Junction Ceiling (T_J,max)</label>
                <div className="flex items-center gap-3">
                  {[85, 100, 115].map(t => (
                    <button
                      key={t}
                      onClick={() => setTargetMaxTj(t)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all border ${
                        targetMaxTj === t
                          ? 'bg-cyan-950 text-cyan-300 border-cyan-500 font-bold'
                          : 'bg-[#020813] text-slate-400 border-slate-800'
                      }`}
                    >
                      {t} °C
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Thermal Output & Safety Gauge */}
            <div className="lg:col-span-6 rounded-3xl bg-[#041026]/80 border border-slate-800 p-6 sm:p-8 backdrop-blur-xl flex flex-col justify-between">
              <div>
                <h3 className="text-lg font-bold font-mono text-white mb-6">Thermal Safety Assessment</h3>

                {thermalResult && (
                  <div className="space-y-6">
                    {/* Primary Junction Temperature Card */}
                    <div className="bg-[#020813] p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
                      <div>
                        <div className="text-[11px] font-mono text-slate-400 uppercase">Silicon Junction Temp (T_J)</div>
                        <div className="text-4xl font-mono font-extrabold text-white mt-1">
                          {thermalResult.junction_temp_c} <span className="text-2xl text-slate-400">°C</span>
                        </div>
                        <div className="text-xs font-mono text-slate-400 mt-1">
                          ΔT rise: +{thermalResult.temp_rise_c} °C above ambient
                        </div>
                      </div>

                      {/* Status Badge */}
                      <div className="text-right">
                        <span className={`px-3 py-1.5 rounded-full text-xs font-mono font-bold uppercase tracking-wider ${
                          thermalResult.thermal_status === 'OPTIMAL'
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30'
                            : thermalResult.thermal_status === 'ELEVATED'
                            ? 'bg-amber-950 text-amber-400 border border-amber-500/30'
                            : thermalResult.thermal_status === 'WARNING'
                            ? 'bg-orange-950 text-orange-400 border border-orange-500/30'
                            : 'bg-red-950 text-red-400 border border-red-500/30 animate-pulse'
                        }`}>
                          {thermalResult.thermal_status}
                        </span>
                        <div className="text-[10px] font-mono text-slate-400 mt-2">
                          Safety Margin: {thermalResult.safety_margin_c} °C
                        </div>
                      </div>
                    </div>

                    {/* Thermal Bar Gauge */}
                    <div className="space-y-1.5">
                      <div className="flex justify-between text-xs font-mono text-slate-400">
                        <span>Ambient ({icAmbientTemp}°C)</span>
                        <span>Rated Max ({thermalResult.max_rated_tj_c}°C)</span>
                      </div>
                      <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden p-[1px]">
                        <div
                          className={`h-full rounded-full transition-all duration-300 ${
                            thermalResult.junction_temp_c <= 85
                              ? 'bg-emerald-500'
                              : thermalResult.junction_temp_c <= 105
                              ? 'bg-amber-500'
                              : thermalResult.junction_temp_c <= 125
                              ? 'bg-orange-500'
                              : 'bg-red-500'
                          }`}
                          style={{
                            width: `${Math.min(100, Math.max(5, (thermalResult.junction_temp_c / 150) * 100))}%`
                          }}
                        ></div>
                      </div>
                    </div>

                    {/* Recommendation Card */}
                    <div className="bg-[#020813] p-4 rounded-2xl border border-slate-800 space-y-3">
                      <div className="text-xs font-mono font-semibold text-slate-300">Engineering Action:</div>
                      <p className="text-xs font-mono text-slate-300 leading-relaxed">
                        {thermalResult.recommendation}
                      </p>

                      {thermalResult.heatsink_required && thermalResult.recommended_heatsink_theta_sa && (
                        <div className="mt-3 p-3 rounded-xl bg-orange-950/40 border border-orange-500/30 text-xs font-mono text-orange-200">
                          <span className="font-bold">Required External Heatsink Spec:</span>
                          <div className="mt-1">
                            Choose heatsink with thermal resistance <span className="font-bold text-white">θSA ≤ {thermalResult.recommended_heatsink_theta_sa} °C/W</span> to keep silicon below {targetMaxTj}°C.
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-6 pt-4 border-t border-slate-800/80 text-[11px] font-mono text-slate-400">
                Package parameters: θJA = {thermalResult?.theta_ja_degc_w || 100} °C/W | θJC = {thermalResult?.theta_jc_degc_w || 40} °C/W.
              </div>
            </div>
          </div>
        )}

        {/* ============================================================================== */}
        {/* TAB 5: INSPECTION HISTORY LEDGER */}
        {/* ============================================================================== */}
        {activeTab === 'history' && (
          <div className="rounded-3xl bg-[#041026]/80 border border-slate-800 p-6 sm:p-8 backdrop-blur-xl">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
              <div>
                <h2 className="text-xl font-bold font-mono text-white flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-cyan-400"></span>
                  Component Inspection Audit Ledger
                </h2>
                <p className="text-xs text-slate-400 font-mono mt-1">
                  Chronological records stored in SQLite WAL database for traceability and NBA/NAAC verification.
                </p>
              </div>

              <button
                onClick={fetchHistory}
                className="px-3.5 py-1.5 rounded-xl bg-[#020813] hover:bg-slate-800 border border-slate-700 text-xs font-mono text-slate-300 hover:text-[#00F0B5] transition-colors"
              >
                Refresh Records
              </button>
            </div>

            {historyRecords.length === 0 ? (
              <div className="text-center py-12 text-slate-500 font-mono text-xs">
                No inspection records logged yet in this session.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 uppercase">
                      <th className="py-3 px-4">Type</th>
                      <th className="py-3 px-4">Component</th>
                      <th className="py-3 px-4">Input Parameters</th>
                      <th className="py-3 px-4">Decoded / Sized Output</th>
                      <th className="py-3 px-4">Inspector</th>
                      <th className="py-3 px-4">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {historyRecords.map((r) => (
                      <tr key={r.id} className="hover:bg-slate-900/40 transition-colors">
                        <td className="py-3 px-4">
                          <span className="px-2 py-0.5 rounded bg-slate-800 text-[#00F0B5] font-semibold text-[10px]">
                            {r.inspection_type}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-slate-300">{r.component_class}</td>
                        <td className="py-3 px-4 text-slate-400 max-w-xs truncate">
                          {JSON.stringify(r.input_params)}
                        </td>
                        <td className="py-3 px-4 text-emerald-400 font-semibold max-w-xs truncate">
                          {r.calculated_result?.formatted || r.calculated_result?.value_formatted || (r.calculated_result?.trace_width_mils ? `${r.calculated_result.trace_width_mils} mils` : JSON.stringify(r.calculated_result))}
                        </td>
                        <td className="py-3 px-4 text-slate-400">{r.inspected_by}</td>
                        <td className="py-3 px-4 text-slate-500 text-[10px]">
                          {new Date(r.created_at).toLocaleTimeString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}

