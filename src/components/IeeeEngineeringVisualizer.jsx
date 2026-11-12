import React, { useState, useMemo } from 'react';

/**
 * ============================================================================
 * VOLTCORE APEX ACADEMIA — IEEE-STANDARD ENGINEERING VISUALIZER
 * ============================================================================
 * Department of Electronics Engineering • MIT Campus • Anna University
 * Regulation 2023 — Choice Based Credit System (CBCS)
 * 
 * 5 Modular Engineering Instrumentation Modes:
 * 1. BJT Voltage-Divider Bias & Q-Point Stability Calculator (EC23C03 / EC23C05 / EC23C01 / EC23C02)
 * 2. NMOS Voltage-Divider Bias & Loadline Explorer (EC23C03 / EC23C05 / VLSI7001)
 * 3. Digital Filter Magnitude & Z-Plane Pole-Zero Constellation (EC23S01 / EC23C07)
 * 4. Digital Sequential Logic & Setup/Hold Timing Slack Explorer (EC23C04 / EC23C06 / HDL6001)
 * 5. Communication Modulation & Shannon-Hartley Capacity Space (EC23C08 / EC23E04)
 * 
 * Features:
 * - 5-way segmented topology switcher
 * - 4-to-5 cell tabular numeral readout deck with dynamic safety warnings
 * - Live interactive SVG waveforms and constellation scatter plots
 * - Direct links and inline previews of IEEE vector schematic assets
 * - Full 18-theme CSS variable compatibility with high-contrast accessibility
 * ============================================================================
 */

export default function IeeeEngineeringVisualizer({
  initialMode = 'bjt',
  courseCode = 'EC23S01',
  themeColor = '#00F0B5'
}) {
  // Determine starting mode based on courseCode if default was requested
  const resolvedInitialMode = useMemo(() => {
    if (initialMode && ['bjt', 'nmos', 'dsp', 'digital', 'comm', 'kmap_bode'].includes(initialMode)) return initialMode;
    if (['EC23S01', 'EC23C07'].includes(courseCode)) return 'dsp';
    if (['EC23C04', 'EC23C06', 'HDL6001', 'VLSI7001'].includes(courseCode)) return 'digital';
    if (['EC23C08', 'EC23E04'].includes(courseCode)) return 'comm';
    if (['EC23C03', 'EC23C05', 'EC23C01', 'EC23C02'].includes(courseCode)) return 'bjt';
    return 'bjt';
  }, [initialMode, courseCode]);

  const [activeMode, setActiveMode] = useState(resolvedInitialMode);
  const [showDiagram, setShowDiagram] = useState(false);

  // --------------------------------------------------------------------------
  // MODE 1: BJT VOLTAGE-DIVIDER BIAS PARAMETERS
  // --------------------------------------------------------------------------
  const [bjtVcc, setBjtVcc] = useState(12.0);      // Volts
  const [bjtR1, setBjtR1] = useState(47.0);        // kOhm
  const [bjtR2, setBjtR2] = useState(10.0);        // kOhm
  const [bjtRc, setBjtRc] = useState(2.2);         // kOhm
  const [bjtRe, setBjtRe] = useState(1.0);         // kOhm
  const [bjtBeta, setBjtBeta] = useState(100);     // Unitless current gain

  // BJT Mathematical Derivations
  const bjtResults = useMemo(() => {
    const Vbe = 0.7; // Constant silicon diode forward drop
    const Vth = (bjtVcc * bjtR2) / (bjtR1 + bjtR2);
    const Rth = (bjtR1 * bjtR2) / (bjtR1 + bjtR2);

    let state = 'ACTIVE';
    let Ib = 0;
    let Ic = 0;
    let Vce = bjtVcc;
    const IcSat = (bjtVcc - 0.2) / (bjtRc + bjtRe);

    if (Vth <= Vbe) {
      state = 'CUTOFF';
      Ib = 0;
      Ic = 0;
      Vce = bjtVcc;
    } else {
      // Ib in mA (V in Volts, R in kOhms)
      Ib = (Vth - Vbe) / (Rth + (bjtBeta + 1) * bjtRe);
      const IcActive = bjtBeta * Ib;

      if (IcActive >= IcSat) {
        state = 'SATURATION';
        Ic = IcSat;
        Vce = 0.2;
      } else {
        state = 'ACTIVE';
        Ic = IcActive;
        Vce = bjtVcc - Ic * (bjtRc + bjtRe);
      }
    }

    // Stability Factor S(Ico) = (1 + beta) * (1 + Rth/Re) / (1 + beta + Rth/Re)
    const ratio = Rth / bjtRe;
    const S = (1 + bjtBeta) * (1 + ratio) / (1 + bjtBeta + ratio);

    // Transconductance gm = Ic / Vt (Vt approx 26mV at 300K)
    const gm = Ic > 0 ? (Ic / 0.026) : 0; // in mS

    // Power Dissipation Pd = Vce * Ic (mW)
    const Pd = Vce * Ic;

    // Midpoint Target Coordinates for undistorted maximum swing
    const idealVce = bjtVcc / 2;
    const idealIc = IcSat / 2;

    return { Vth, Rth, Ib, Ic, Vce, IcSat, S, gm, Pd, state, idealVce, idealIc };
  }, [bjtVcc, bjtR1, bjtR2, bjtRc, bjtRe, bjtBeta]);

  // --------------------------------------------------------------------------
  // MODE 2: NMOS VOLTAGE-DIVIDER BIAS PARAMETERS
  // --------------------------------------------------------------------------
  const [nmosVdd, setNmosVdd] = useState(15.0);    // Volts
  const [nmosR1, setNmosR1] = useState(1000.0);   // kOhm (1 MOhm)
  const [nmosR2, setNmosR2] = useState(470.0);    // kOhm
  const [nmosRd, setNmosRd] = useState(3.3);      // kOhm
  const [nmosRs, setNmosRs] = useState(1.2);      // kOhm
  const [nmosVth, setNmosVth] = useState(1.5);    // Volts threshold
  const [nmosKn, setNmosKn] = useState(1.0);      // mA/V^2 process conduction parameter

  // NMOS Mathematical Derivations
  const nmosResults = useMemo(() => {
    const Vg = (nmosVdd * nmosR2) / (nmosR1 + nmosR2);
    const deltaV = Vg - nmosVth;

    let state = 'SATURATION';
    let Id = 0;
    let Vgs = Vg;
    let Vds = nmosVdd;
    const IdSatMax = nmosVdd / (nmosRd + nmosRs);

    if (deltaV <= 0) {
      state = 'CUTOFF';
      Id = 0;
      Vgs = Vg;
      Vds = nmosVdd;
    } else {
      // Quadratic: a*Id^2 + b*Id + c = 0
      const a = nmosKn * Math.pow(nmosRs, 2);
      const b = -(2 * nmosKn * nmosRs * deltaV + 1);
      const c = nmosKn * Math.pow(deltaV, 2);
      const D = b * b - 4 * a * c;

      if (D >= 0 && a > 0) {
        // Physical branch with minus root
        const root1 = (-b - Math.sqrt(D)) / (2 * a);
        Id = root1;
        Vgs = Vg - Id * nmosRs;
        Vds = nmosVdd - Id * (nmosRd + nmosRs);
        const VdsSat = Vgs - nmosVth;

        if (Vds < VdsSat) {
          state = 'TRIODE';
        } else {
          state = 'SATURATION';
        }
      } else {
        Id = 0;
        Vds = nmosVdd;
      }
    }

    const gm = (state === 'SATURATION' && Id > 0) ? (2 * Math.sqrt(nmosKn * Id)) : 0;
    const Pd = Vds * Id;

    return { Vg, Id, Vgs, Vds, gm, Pd, state, IdSatMax };
  }, [nmosVdd, nmosR1, nmosR2, nmosRd, nmosRs, nmosVth, nmosKn]);

  // --------------------------------------------------------------------------
  // MODE 3: DIGITAL FILTER & FFT FREQUENCY RESPONSE PARAMETERS
  // --------------------------------------------------------------------------
  const [dspType, setDspType] = useState('lowpass'); // 'lowpass', 'highpass', 'bandpass'
  const [dspOrder, setDspOrder] = useState(3);       // Order N = 1 to 6
  const [dspWc, setDspWc] = useState(0.35);          // Normalized cutoff (fraction of pi)
  const [dspProbeW, setDspProbeW] = useState(0.35);  // Cursor frequency probe

  // DSP Calculations
  const dspResults = useMemo(() => {
    const N = dspOrder;
    const wc = dspWc * Math.PI; // Cutoff in rad/sample
    const Fs = 48000; // 48 kHz sample rate standard
    const fcHz = (dspWc * Fs) / 2; // Analog frequency equivalent
    const tanWc2 = Math.tan(wc / 2);

    const pointsCount = 64;
    const sweepData = [];
    for (let i = 0; i <= pointsCount; i++) {
      const wFrac = i / pointsCount;
      const wRad = wFrac * Math.PI;
      const tanW2 = Math.tan(wRad / 2);
      
      let magLin = 0;
      if (dspType === 'lowpass') {
        const ratio = tanW2 / (tanWc2 || 0.001);
        magLin = 1 / Math.sqrt(1 + Math.pow(ratio, 2 * N));
      } else if (dspType === 'highpass') {
        const ratio = (tanWc2 || 0.001) / (tanW2 || 0.0001);
        magLin = 1 / Math.sqrt(1 + Math.pow(ratio, 2 * N));
      } else {
        const center = tanWc2;
        const bw = 0.2 * center;
        const dist = Math.abs(tanW2 - center) / (bw || 0.001);
        magLin = 1 / Math.sqrt(1 + Math.pow(dist, 2 * N));
      }

      const magDb = Math.max(-60, 20 * Math.log10(Math.max(0.0001, magLin)));
      sweepData.push({ wFrac, wRad, magLin, magDb });
    }

    // Bilinear Transform Poles on Z-Plane
    const poles = [];
    for (let k = 1; k <= N; k++) {
      const theta = (Math.PI * (2 * k + N - 1)) / (2 * N);
      const sigma = tanWc2 * Math.cos(theta);
      const omega = tanWc2 * Math.sin(theta);

      const numR = 1 + sigma;
      const numI = omega;
      const denR = 1 - sigma;
      const denI = -omega;
      const denMagSq = denR * denR + denI * denI;

      const zR = (numR * denR + numI * denI) / denMagSq;
      const zI = (numI * denR - numR * denI) / denMagSq;
      const radius = Math.sqrt(zR * zR + zI * zI);
      poles.push({ zR, zI, radius });
    }

    const zeros = [];
    const zeroVal = dspType === 'lowpass' ? -1 : (dspType === 'highpass' ? 1 : 0);
    for (let k = 0; k < N; k++) {
      zeros.push({ zR: zeroVal, zI: 0 });
    }

    const stopbandRatio = Math.tan(1.5 * wc / 2) / (tanWc2 || 0.001);
    const stopbandDb = -10 * Math.log10(1 + Math.pow(stopbandRatio, 2 * N));
    const maxPoleRadius = Math.max(...poles.map(p => p.radius));
    const stabilityMargin = Math.max(0, 1 - maxPoleRadius);

    const probeTanW2 = Math.tan((dspProbeW * Math.PI) / 2);
    const probeRatio = probeTanW2 / (tanWc2 || 0.001);
    const probeMagLin = 1 / Math.sqrt(1 + Math.pow(probeRatio, 2 * N));
    const probeMagDb = Math.max(-60, 20 * Math.log10(probeMagLin));

    return {
      sweepData,
      poles,
      zeros,
      fcHz,
      stopbandDb,
      maxPoleRadius,
      stabilityMargin,
      probeMagDb
    };
  }, [dspType, dspOrder, dspWc, dspProbeW]);

  // --------------------------------------------------------------------------
  // MODE 4: DIGITAL LOGIC & FLIP-FLOP TIMING SLACK PARAMETERS (EC23C04 / HDL6001)
  // --------------------------------------------------------------------------
  const [digitalFclk, setDigitalFclk] = useState(100);   // Clock Frequency (MHz)
  const [digitalTcq, setDigitalTcq] = useState(1.2);     // Clock-to-Q delay (ns)
  const [digitalTcomb, setDigitalTcomb] = useState(5.2); // Combinational logic delay (ns)
  const [digitalTsetup, setDigitalTsetup] = useState(1.5);// Setup requirement (ns)
  const [digitalThold, setDigitalThold] = useState(0.8);  // Hold requirement (ns)

  const digitalResults = useMemo(() => {
    const Tclk = 1000 / digitalFclk; // Clock period in ns
    const dataArrival = digitalTcq + digitalTcomb;
    const dataRequired = Tclk - digitalTsetup;
    const setupSlack = dataRequired - dataArrival; // in ns
    const holdSlack = (digitalTcq + 0.3 * digitalTcomb) - digitalThold;
    const isTimingMet = setupSlack >= 0;
    const maxFreq = 1000 / (digitalTcq + digitalTcomb + digitalTsetup);

    return { Tclk, dataArrival, dataRequired, setupSlack, holdSlack, isTimingMet, maxFreq };
  }, [digitalFclk, digitalTcq, digitalTcomb, digitalTsetup, digitalThold]);

  // --------------------------------------------------------------------------
  // MODE 5: COMMUNICATION MODULATION & SHANNON-HARTLEY CAPACITY (EC23C08 / EC23E04)
  // --------------------------------------------------------------------------
  const [commBw, setCommBw] = useState(5.0);           // Bandwidth (MHz)
  const [commSnrDb, setCommSnrDb] = useState(18.0);    // SNR in dB
  const [commMod, setCommMod] = useState('16qam');     // 'bpsk', 'qpsk', '16qam'

  const commResults = useMemo(() => {
    const snrLin = Math.pow(10, commSnrDb / 10);
    // Shannon-Hartley Capacity: C = B * log2(1 + SNR) in Mbps
    const capacityMbps = commBw * Math.log2(1 + snrLin);
    const spectralEff = Math.log2(1 + snrLin); // bps/Hz
    const ebNoLin = snrLin / spectralEff;
    const ebNoDb = 10 * Math.log10(Math.max(0.001, ebNoLin));

    // Approximate bit error probability
    let ber = 0;
    if (commMod === 'bpsk' || commMod === 'qpsk') {
      // 0.5 * erfc(sqrt(Eb/N0))
      const x = Math.sqrt(ebNoLin);
      ber = Math.max(1e-9, 0.5 * Math.exp(-x * x) / (Math.sqrt(Math.PI) * (x + 0.001)));
    } else {
      // 16-QAM
      const x = Math.sqrt(0.4 * ebNoLin);
      ber = Math.max(1e-9, 0.375 * Math.exp(-x * x) / (Math.sqrt(Math.PI) * (x + 0.001)));
    }

    // Constellation points and noise scatter variance
    const noiseStd = Math.min(0.35, 1 / (Math.sqrt(2 * snrLin) + 0.001));

    return { snrLin, capacityMbps, spectralEff, ebNoDb, ber, noiseStd };
  }, [commBw, commSnrDb, commMod]);


  // --------------------------------------------------------------------------
  // MODE 6: BOOLEAN K-MAP SIMPLIFIER & BODE ASYMPTOTIC EXPLORER
  // --------------------------------------------------------------------------
  // 16-cell K-Map minterm array [m0 .. m15]
  // Row AB: 00 (0,1,3,2), 01 (4,5,7,6), 11 (12,13,15,14), 10 (8,9,11,10)
  // Col CD: 00, 01, 11, 10
  const [kmapCells, setKmapCells] = useState([
    0, 1, 0, 1, // m0, m1, m2, m3
    1, 0, 1, 0, // m4, m5, m6, m7
    0, 1, 0, 1, // m8, m9, m10, m11
    1, 0, 1, 0  // m12, m13, m14, m15
  ]);
  const [bodeFc, setBodeFc] = useState(1000); // Corner Frequency Hz
  const [bodeOrder, setBodeOrder] = useState(2); // 1, 2, or 3
  const [bodeZeta, setBodeZeta] = useState(0.707); // Damping ratio
  const [bodeType, setBodeType] = useState('lowpass'); // lowpass or highpass

  // Toggle K-Map minterm
  const toggleKmapCell = (idx) => {
    setKmapCells(prev => {
      const next = [...prev];
      next[idx] = next[idx] === 1 ? 0 : 1;
      return next;
    });
  };

  // K-Map Presets
  const setKmapPreset = (preset) => {
    if (preset === 'zero') {
      setKmapCells(new Array(16).fill(0));
    } else if (preset === 'one') {
      setKmapCells(new Array(16).fill(1));
    } else if (preset === 'fa_sum') {
      // Full Adder Sum: A ^ B ^ C (for 3 vars, replicated for D don't care: m1, m2, m4, m7, m9, m10, m12, m15)
      const cells = new Array(16).fill(0);
      [1, 2, 4, 7, 9, 10, 12, 15].forEach(i => cells[i] = 1);
      setKmapCells(cells);
    } else if (preset === 'fa_carry') {
      // Majority / Carry: m3, m5, m6, m7, m11, m13, m14, m15
      const cells = new Array(16).fill(0);
      [3, 5, 6, 7, 11, 13, 14, 15].forEach(i => cells[i] = 1);
      setKmapCells(cells);
    } else if (preset === 'parity') {
      // 4-bit odd parity: m1, m2, m4, m7, m8, m11, m13, m14
      const cells = new Array(16).fill(0);
      [1, 2, 4, 7, 8, 11, 13, 14].forEach(i => cells[i] = 1);
      setKmapCells(cells);
    } else if (preset === 'invert') {
      setKmapCells(prev => prev.map(v => (v === 1 ? 0 : 1)));
    }
  };

  // Derive Canonical SOP and simplified representation
  const kmapResults = useMemo(() => {
    const activeMinterms = [];
    kmapCells.forEach((val, idx) => {
      if (val === 1) activeMinterms.push(idx);
    });

    let sop = '';
    if (activeMinterms.length === 0) {
      sop = 'F = 0 (GND / Contradiction)';
    } else if (activeMinterms.length === 16) {
      sop = 'F = 1 (V_DD / Tautology)';
    } else {
      sop = `F(A,B,C,D) = Σ m(${activeMinterms.join(', ')})`;
    }

    return {
      activeCount: activeMinterms.length,
      activeMinterms,
      canonicalSop: sop
    };
  }, [kmapCells]);

  // Bode Plot Calculations
  const bodeResults = useMemo(() => {
    const rollOffSlope = -20 * bodeOrder; // dB/decade
    const qFactor = 1 / (2 * Math.max(0.05, bodeZeta));
    const resonanceFreq = bodeZeta < 0.707 ? bodeFc * Math.sqrt(1 - 2 * bodeZeta * bodeZeta) : null;
    const peakGainDb = bodeZeta < 0.707 ? 20 * Math.log10(1 / (2 * bodeZeta * Math.sqrt(1 - bodeZeta * bodeZeta))) : 0;
    const gainAtFc = -10 * Math.log10(Math.pow(2, bodeOrder)); // Approx -3.01 dB for 1st order
    const phaseAtFc = -45 * bodeOrder; // Degrees

    // Generate 4-decade frequency points from 0.01 * bodeFc to 100 * bodeFc
    const points = [];
    const numPoints = 80;
    const logMin = Math.log10(bodeFc / 100);
    const logMax = Math.log10(bodeFc * 100);

    for (let i = 0; i <= numPoints; i++) {
      const logF = logMin + (i / numPoints) * (logMax - logMin);
      const f = Math.pow(10, logF);
      const ratio = f / bodeFc;

      let magDb = 0;
      let phaseDeg = 0;

      if (bodeType === 'lowpass') {
        if (bodeOrder === 1) {
          magDb = -10 * Math.log10(1 + ratio * ratio);
          phaseDeg = -Math.atan(ratio) * (180 / Math.PI);
        } else if (bodeOrder === 2) {
          const denom = Math.pow(1 - ratio * ratio, 2) + Math.pow(2 * bodeZeta * ratio, 2);
          magDb = -10 * Math.log10(Math.max(1e-12, denom));
          phaseDeg = -Math.atan2(2 * bodeZeta * ratio, 1 - ratio * ratio) * (180 / Math.PI);
        } else {
          const denom1 = 1 + ratio * ratio;
          const denom2 = Math.pow(1 - ratio * ratio, 2) + Math.pow(2 * bodeZeta * ratio, 2);
          magDb = -10 * Math.log10(Math.max(1e-12, denom1 * denom2));
          phaseDeg = -(Math.atan(ratio) + Math.atan2(2 * bodeZeta * ratio, 1 - ratio * ratio)) * (180 / Math.PI);
        }
      } else {
        // Highpass
        if (bodeOrder === 1) {
          magDb = 10 * Math.log10(ratio * ratio / (1 + ratio * ratio));
          phaseDeg = 90 - Math.atan(ratio) * (180 / Math.PI);
        } else {
          const numer = Math.pow(ratio, 2 * bodeOrder);
          const denom = Math.pow(1 - ratio * ratio, 2) + Math.pow(2 * bodeZeta * ratio, 2);
          magDb = 10 * Math.log10(Math.max(1e-12, numer / Math.max(1e-12, denom)));
          phaseDeg = 180 - Math.atan2(2 * bodeZeta * ratio, 1 - ratio * ratio) * (180 / Math.PI);
        }
      }

      // Clamp for SVG graph boundaries (-80 dB to +20 dB)
      const clampedMag = Math.max(-80, Math.min(25, magDb));
      points.push({ f, ratio, magDb: clampedMag, phaseDeg });
    }

    return {
      rollOffSlope,
      qFactor,
      resonanceFreq,
      peakGainDb,
      gainAtFc,
      phaseAtFc,
      points
    };
  }, [bodeFc, bodeOrder, bodeZeta, bodeType]);

  return (
    <div className="rounded-3xl border border-[#00F0B5]/30 bg-[#020813] text-slate-100 shadow-2xl p-5 sm:p-7 space-y-6 font-mono">
      
      {/* HEADER & 5-WAY SEGMENTED CONTROLLER */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-6 bg-gradient-to-b from-[#00693E] to-[#00F0B5] rounded-full"></span>
            <h3 className="text-lg sm:text-xl font-bold text-white tracking-tight font-heading flex items-center gap-2">
              <span>IEEE Interactive Engineering Visualizer</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-[#00693E]/40 text-[#00F0B5] border border-[#00F0B5]/30 uppercase font-mono">
                AU-R2023 Direct Compute
              </span>
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-sans">
            Semiconductor loadline, digital timing closure &amp; communication channel capacity instrumentation.
          </p>
        </div>

        {/* Mode Switcher Buttons */}
        <div className="flex flex-wrap items-center gap-1.5 p-1 rounded-2xl bg-[#041026] border border-slate-800 text-xs">
          <button
            onClick={() => setActiveMode('bjt')}
            className={`px-3 py-1.5 rounded-xl font-bold transition-all ${
              activeMode === 'bjt'
                ? 'bg-[#00693E] text-[#00F0B5] border border-[#00F0B5]/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            BJT Loadline
          </button>
          <button
            onClick={() => setActiveMode('nmos')}
            className={`px-3 py-1.5 rounded-xl font-bold transition-all ${
              activeMode === 'nmos'
                ? 'bg-[#00693E] text-[#00F0B5] border border-[#00F0B5]/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            NMOS Bias
          </button>
          <button
            onClick={() => setActiveMode('dsp')}
            className={`px-3 py-1.5 rounded-xl font-bold transition-all ${
              activeMode === 'dsp'
                ? 'bg-[#00693E] text-[#00F0B5] border border-[#00F0B5]/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            DSP Filter &amp; Z-Plane
          </button>
          <button
            onClick={() => setActiveMode('digital')}
            className={`px-3 py-1.5 rounded-xl font-bold transition-all ${
              activeMode === 'digital'
                ? 'bg-[#00693E] text-[#00F0B5] border border-[#00F0B5]/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Digital Timing Slack
          </button>
          <button
            onClick={() => setActiveMode('comm')}
            className={`px-3 py-1.5 rounded-xl font-bold transition-all ${
              activeMode === 'comm'
                ? 'bg-[#00693E] text-[#00F0B5] border border-[#00F0B5]/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Comm &amp; Shannon
          </button>
          <button
            onClick={() => setActiveMode('kmap_bode')}
            className={`px-3 py-1.5 rounded-xl font-bold transition-all ${
              activeMode === 'kmap_bode'
                ? 'bg-[#00693E] text-[#00F0B5] border border-[#00F0B5]/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            K-Map &amp; Bode Plot
          </button>
        </div>
      </div>

      {/* =====================================================================
          MODE 1: BJT VOLTAGE-DIVIDER BIAS VISUALIZER
          ===================================================================== */}
      {activeMode === 'bjt' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Quiescent Current</span>
              <div className="text-xl font-bold text-[#00F0B5] font-mono tracking-tight">
                {bjtResults.Ic.toFixed(2)} <span className="text-xs font-normal text-slate-400">mA</span>
              </div>
              <span className="text-[10px] text-slate-500 font-sans block">I_CQ (Collector)</span>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Collector-Emitter</span>
              <div className="text-xl font-bold text-white font-mono tracking-tight">
                {bjtResults.Vce.toFixed(2)} <span className="text-xs font-normal text-slate-400">V</span>
              </div>
              <span className="text-[10px] text-slate-500 font-sans block">V_CEQ Quiescent</span>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Stability Factor S</span>
              <div className={`text-xl font-bold font-mono tracking-tight ${
                bjtResults.S < 15 ? 'text-emerald-400' : (bjtResults.S < 30 ? 'text-amber-400' : 'text-rose-400')
              }`}>
                {bjtResults.S.toFixed(2)}
              </div>
              <span className="text-[10px] text-slate-500 font-sans block">
                {bjtResults.S < 15 ? '✦ Excellent' : (bjtResults.S < 30 ? 'Moderate' : 'Poor Drift')}
              </span>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Transconductance</span>
              <div className="text-xl font-bold text-cyan-300 font-mono tracking-tight">
                {bjtResults.gm.toFixed(1)} <span className="text-xs font-normal text-slate-400">mS</span>
              </div>
              <span className="text-[10px] text-slate-500 font-sans block">g_m = I_C / V_T</span>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1 col-span-2 sm:col-span-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Dissipation &amp; Region</span>
              <div className="text-xl font-bold text-amber-300 font-mono tracking-tight">
                {bjtResults.Pd.toFixed(1)} <span className="text-xs font-normal text-slate-400">mW</span>
              </div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 block">
                {bjtResults.state}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            <div className="lg:col-span-7 rounded-2xl border border-slate-800 bg-[#010610] p-4 relative overflow-hidden shadow-inner">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800/80 text-xs">
                <span className="font-bold text-slate-300 flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-[#00F0B5]"></span>
                  <span>BJT DC Loadline &amp; Dynamic Q-Point Trajectory</span>
                </span>
                <span className="text-[10px] text-slate-500 font-sans">
                  Target: Midpoint for Max Undistorted Swing
                </span>
              </div>

              <div className="w-full aspect-[5/3.2] pt-2">
                <svg viewBox="0 0 500 320" className="w-full h-full select-none">
                  <defs>
                    <linearGradient id="satZoneGrad" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stopColor="#f43f5e" stopOpacity="0.15" />
                      <stop offset="100%" stopColor="#f43f5e" stopOpacity="0.02" />
                    </linearGradient>
                  </defs>
                  {[60, 110, 160, 210, 260].map((y) => (
                    <line key={y} x1="50" y1={y} x2="470" y2={y} stroke="#1e293b" strokeDasharray="3 3" strokeWidth="0.8" />
                  ))}
                  {[120, 190, 260, 330, 400].map((x) => (
                    <line key={x} x1={x} y1="20" x2={x} y2="280" stroke="#1e293b" strokeDasharray="3 3" strokeWidth="0.8" />
                  ))}
                  <rect x="50" y="20" width="30" height="260" fill="url(#satZoneGrad)" />
                  <line x1="50" y1="280" x2="475" y2="280" stroke="#64748b" strokeWidth="1.5" />
                  <line x1="50" y1="280" x2="50" y2="15" stroke="#64748b" strokeWidth="1.5" />
                  <text x="480" y="296" fill="#94a3b8" fontSize="11" textAnchor="end" fontFamily="monospace">V_CE (V)</text>
                  <text x="45" y="15" fill="#94a3b8" fontSize="11" textAnchor="end" fontFamily="monospace">I_C (mA)</text>

                  {(() => {
                    const maxV = bjtVcc;
                    const maxI = Math.max(0.1, bjtResults.IcSat * 1.15);
                    const toX = (v) => 50 + (v / maxV) * 410;
                    const toY = (i) => 280 - (i / maxI) * 250;
                    const pSatX = toX(0);
                    const pSatY = toY(bjtResults.IcSat);
                    const pCutoffX = toX(bjtVcc);
                    const pCutoffY = toY(0);
                    const qX = toX(Math.max(0, Math.min(bjtVcc, bjtResults.Vce)));
                    const qY = toY(Math.max(0, Math.min(maxI, bjtResults.Ic)));
                    const idealX = toX(bjtResults.idealVce);
                    const idealY = toY(bjtResults.idealIc);

                    return (
                      <>
                        <circle cx={idealX} cy={idealY} r="7" fill="none" stroke="#3b82f6" strokeWidth="1.5" strokeDasharray="2 2" />
                        <line x1={pSatX} y1={pSatY} x2={pCutoffX} y2={pCutoffY} stroke="#00F0B5" strokeWidth="2.5" />
                        <circle cx={pSatX} cy={pSatY} r="4" fill="#00F0B5" />
                        <circle cx={pCutoffX} cy={pCutoffY} r="4" fill="#00F0B5" />
                        <line x1={qX} y1={qY} x2={qX} y2="280" stroke="#f59e0b" strokeDasharray="3 3" strokeWidth="1" />
                        <line x1={qX} y1={qY} x2="50" y2={qY} stroke="#f59e0b" strokeDasharray="3 3" strokeWidth="1" />
                        <circle cx={qX} cy={qY} r="6" fill="#f59e0b" stroke="#ffffff" strokeWidth="2" />
                        <rect x={Math.min(320, qX + 12)} y={Math.max(30, qY - 26)} width="130" height="24" rx="6" fill="#041026" stroke="#f59e0b" strokeWidth="1" />
                        <text x={Math.min(320, qX + 12) + 8} y={Math.max(30, qY - 26) + 16} fill="#fef08a" fontSize="10" fontWeight="bold" fontFamily="monospace">
                          Q-POINT: ({bjtResults.Vce.toFixed(2)}V, {bjtResults.Ic.toFixed(2)}mA)
                        </text>
                      </>
                    );
                  })()}
                </svg>
              </div>

              <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800/80 text-[10px] text-slate-400 font-sans">
                <span className="flex items-center gap-1">
                  <span className="h-2 w-3 bg-[#00F0B5] rounded-sm"></span>
                  <span>DC Loadline Slope: -1 / (R_C + R_E)</span>
                </span>
                <button
                  type="button"
                  onClick={() => setShowDiagram(!showDiagram)}
                  className="text-[#00F0B5] hover:underline flex items-center gap-1"
                >
                  <span>{showDiagram ? 'Hide Schematic' : 'View IEEE Schematic'}</span>
                  <span>↗</span>
                </button>
              </div>
            </div>

            <div className="lg:col-span-5 p-4 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <span className="text-xs font-bold text-slate-200 uppercase tracking-wider">Parameters</span>
                <button
                  onClick={() => { setBjtVcc(12.0); setBjtR1(47.0); setBjtR2(10.0); setBjtRc(2.2); setBjtRe(1.0); setBjtBeta(100); }}
                  className="text-[10px] text-slate-400 hover:text-[#00F0B5]"
                >
                  Reset
                </button>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Supply V_CC:</span>
                  <span className="text-emerald-400 font-bold">{bjtVcc.toFixed(1)} V</span>
                </div>
                <input type="range" min="5" max="24" step="0.5" value={bjtVcc} onChange={(e) => setBjtVcc(parseFloat(e.target.value))} className="w-full h-1.5 bg-slate-800 rounded-lg accent-[#00F0B5]" />
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Collector R_C:</span>
                  <span className="text-emerald-400 font-bold">{bjtRc.toFixed(1)} kΩ</span>
                </div>
                <input type="range" min="0.5" max="10" step="0.1" value={bjtRc} onChange={(e) => setBjtRc(parseFloat(e.target.value))} className="w-full h-1.5 bg-slate-800 rounded-lg accent-[#00F0B5]" />
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Emitter R_E:</span>
                  <span className="text-emerald-400 font-bold">{bjtRe.toFixed(2)} kΩ</span>
                </div>
                <input type="range" min="0.2" max="5" step="0.1" value={bjtRe} onChange={(e) => setBjtRe(parseFloat(e.target.value))} className="w-full h-1.5 bg-slate-800 rounded-lg accent-[#00F0B5]" />
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Gain β:</span>
                  <span className="text-cyan-400 font-bold">{bjtBeta}</span>
                </div>
                <input type="range" min="30" max="300" step="5" value={bjtBeta} onChange={(e) => setBjtBeta(parseInt(e.target.value, 10))} className="w-full h-1.5 bg-slate-800 rounded-lg accent-cyan-400" />
              </div>
            </div>
          </div>

          {showDiagram && (
            <div className="p-4 rounded-2xl bg-[#010610] border border-[#00F0B5]/40 space-y-3">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="font-bold text-slate-200">IEEE Std 315-1975 Schematic: BJT Common-Emitter Amplifier</span>
                <a href="/assets/diagrams/bjt_voltage_divider_ieee.svg" target="_blank" rel="noopener noreferrer" className="text-[#00F0B5] hover:underline">Open Vector Source ↗</a>
              </div>
              <div className="w-full flex justify-center bg-[#020813] rounded-xl p-4 border border-slate-800">
                <img src="/assets/diagrams/bjt_voltage_divider_ieee.svg" alt="IEEE BJT Schematic" className="max-h-64 object-contain" />
              </div>
            </div>
          )}

          <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 text-xs text-slate-300 flex flex-wrap items-center justify-between gap-3">
            <span className="font-sans">
              <strong className="text-emerald-400 font-mono">Governing Equation:</strong> S(I_CO) = (1 + β) · (1 + R_TH/R_E) / (1 + β + R_TH/R_E)
            </span>
            <span className="text-[11px] text-slate-400 font-mono">MIT Campus ECE • Circuits &amp; Analog Devices</span>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODE 2: NMOS VOLTAGE-DIVIDER BIAS VISUALIZER
          ===================================================================== */}
      {activeMode === 'nmos' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Drain Current I_D</span>
              <div className="text-xl font-bold text-[#00F0B5] font-mono tracking-tight">{nmosResults.Id.toFixed(2)} mA</div>
              <span className="text-[10px] text-slate-500 font-sans block">Quiescent Drain Current</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Drain-Source V_DS</span>
              <div className="text-xl font-bold text-white font-mono tracking-tight">{nmosResults.Vds.toFixed(2)} V</div>
              <span className="text-[10px] text-slate-500 font-sans block">Pinch-off = {(nmosResults.Vgs - nmosVth).toFixed(2)}V</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Transconductance</span>
              <div className="text-xl font-bold text-cyan-300 font-mono tracking-tight">{nmosResults.gm.toFixed(2)} mS</div>
              <span className="text-[10px] text-slate-500 font-sans block">g_m = 2√(K_n · I_D)</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Operating Region</span>
              <div className="text-xl font-bold text-amber-300 font-mono tracking-tight">{nmosResults.state}</div>
              <span className="text-[10px] text-slate-500 font-sans block">P_D = {nmosResults.Pd.toFixed(1)} mW</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-2xl bg-[#041026] border border-slate-800">
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Supply V_DD:</span>
                <span className="text-emerald-400 font-bold">{nmosVdd.toFixed(1)} V</span>
              </div>
              <input type="range" min="5" max="25" step="0.5" value={nmosVdd} onChange={(e) => setNmosVdd(parseFloat(e.target.value))} className="w-full h-1.5 bg-slate-800 rounded-lg accent-[#00F0B5]" />
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Drain R_D:</span>
                <span className="text-emerald-400 font-bold">{nmosRd.toFixed(1)} kΩ</span>
              </div>
              <input type="range" min="0.5" max="10" step="0.1" value={nmosRd} onChange={(e) => setNmosRd(parseFloat(e.target.value))} className="w-full h-1.5 bg-slate-800 rounded-lg accent-[#00F0B5]" />
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Threshold V_TH:</span>
                <span className="text-cyan-400 font-bold">{nmosVth.toFixed(1)} V</span>
              </div>
              <input type="range" min="0.5" max="3.0" step="0.1" value={nmosVth} onChange={(e) => setNmosVth(parseFloat(e.target.value))} className="w-full h-1.5 bg-slate-800 rounded-lg accent-cyan-400" />
            </div>
          </div>

          <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 text-xs text-slate-300 flex flex-wrap items-center justify-between gap-3">
            <span className="font-sans">
              <strong className="text-emerald-400 font-mono">Governing Equation:</strong> I_D = K_n (V_GS - V_TH)² in Saturation [V_DS ≥ V_GS - V_TH]
            </span>
            <span className="text-[11px] text-slate-400 font-mono">MIT Campus ECE • Solid State Devices &amp; CMOS VLSI</span>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODE 3: DIGITAL FILTER & FFT FREQUENCY RESPONSE
          ===================================================================== */}
      {activeMode === 'dsp' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Cutoff Frequency</span>
              <div className="text-xl font-bold text-[#00F0B5] font-mono tracking-tight">{dspResults.fcHz.toFixed(1)} kHz</div>
              <span className="text-[10px] text-slate-500 font-sans block">ω_c = {dspWc.toFixed(2)}π</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Filter Order N</span>
              <div className="text-xl font-bold text-white font-mono tracking-tight">N = {dspOrder}</div>
              <span className="text-[10px] text-slate-500 font-sans block">Roll-off: -{dspOrder * 20} dB/dec</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Stopband Attenuation</span>
              <div className="text-xl font-bold text-amber-300 font-mono tracking-tight">{dspResults.stopbandDb.toFixed(1)} dB</div>
              <span className="text-[10px] text-slate-500 font-sans block">At 1.5 · ω_c</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Stability Margin</span>
              <div className="text-xl font-bold text-emerald-400 font-mono tracking-tight">{dspResults.stabilityMargin.toFixed(3)}</div>
              <span className="text-[10px] text-slate-500 font-sans block">Max |p_k| = {dspResults.maxPoleRadius.toFixed(3)} &lt; 1</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            <div className="lg:col-span-7 rounded-2xl border border-slate-800 bg-[#010610] p-4 relative overflow-hidden shadow-inner space-y-2">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800/80 text-xs">
                <span className="font-bold text-slate-300 flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-[#00F0B5]"></span>
                  <span>Magnitude Response |H(e^jω)| (dB)</span>
                </span>
                <span className="text-[10px] text-slate-400 font-mono">
                  Probe: <strong className="text-amber-400">{dspResults.probeMagDb.toFixed(1)} dB</strong>
                </span>
              </div>
              <div className="w-full aspect-[4.8/2.6] pt-1">
                <svg viewBox="0 0 480 260" className="w-full h-full select-none">
                  {[30, 63, 96, 130, 163, 196, 230].map((y, idx) => (
                    <g key={y}>
                      <line x1="45" y1={y} x2="465" y2={y} stroke="#1e293b" strokeDasharray="3 3" strokeWidth="0.8" />
                      <text x="40" y={y + 3} fill="#64748b" fontSize="8" textAnchor="end" fontFamily="monospace">{-idx * 10}dB</text>
                    </g>
                  ))}
                  {[0, 0.25, 0.5, 0.75, 1.0].map((f) => (
                    <g key={f}>
                      <line x1={45 + f * 420} y1="30" x2={45 + f * 420} y2="230" stroke="#1e293b" strokeDasharray="3 3" strokeWidth="0.8" />
                      <text x={45 + f * 420} y="244" fill="#64748b" fontSize="8" textAnchor="middle" fontFamily="monospace">{f === 0 ? '0' : (f === 1 ? 'π' : `${f}π`)}</text>
                    </g>
                  ))}
                  <line x1="45" y1="40" x2="465" y2="40" stroke="#f43f5e" strokeDasharray="4 2" strokeWidth="1" />
                  {(() => {
                    const cutoffX = 45 + dspWc * 420;
                    const pathD = dspResults.sweepData.reduce((acc, pt, idx) => {
                      const x = 45 + pt.wFrac * 420;
                      const y = 30 + (Math.abs(pt.magDb) / 60) * 200;
                      return idx === 0 ? `M ${x} ${y}` : `${acc} L ${x} ${y}`;
                    }, '');
                    const probeX = 45 + dspProbeW * 420;
                    const probeY = 30 + (Math.abs(dspResults.probeMagDb) / 60) * 200;
                    return (
                      <>
                        <line x1={cutoffX} y1="30" x2={cutoffX} y2="230" stroke="#00F0B5" strokeDasharray="3 3" strokeWidth="1" />
                        <path d={pathD} fill="none" stroke="#00F0B5" strokeWidth="2.5" />
                        <line x1={probeX} y1="30" x2={probeX} y2="230" stroke="#f59e0b" strokeWidth="1.2" strokeDasharray="2 2" />
                        <circle cx={probeX} cy={probeY} r="5" fill="#f59e0b" stroke="#ffffff" strokeWidth="1.5" />
                      </>
                    );
                  })()}
                </svg>
              </div>
              <div className="pt-2 flex items-center gap-3 text-xs border-t border-slate-800">
                <span className="text-slate-400 text-[11px] shrink-0 font-mono">Sweep Probe ω:</span>
                <input type="range" min="0" max="1" step="0.01" value={dspProbeW} onChange={(e) => setDspProbeW(parseFloat(e.target.value))} className="w-full h-1.5 bg-slate-800 rounded-lg accent-amber-400" />
                <span className="text-amber-400 font-mono text-[11px] font-bold shrink-0">{(dspProbeW * 24).toFixed(1)} kHz</span>
              </div>
            </div>

            <div className="lg:col-span-5 rounded-2xl border border-slate-800 bg-[#010610] p-4 relative overflow-hidden shadow-inner space-y-2">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800/80 text-xs">
                <span className="font-bold text-slate-300 flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-cyan-400"></span>
                  <span>Z-Plane Pole-Zero Constellation</span>
                </span>
                <span className="text-[10px] text-emerald-400 font-mono">|z| &lt; 1 Stable</span>
              </div>
              <div className="w-full aspect-[2.8/2.6] flex justify-center items-center">
                <svg viewBox="0 0 280 260" className="w-full h-full select-none">
                  <line x1="20" y1="130" x2="260" y2="130" stroke="#334155" strokeWidth="1.2" />
                  <line x1="140" y1="10" x2="140" y2="250" stroke="#334155" strokeWidth="1.2" />
                  <circle cx="140" cy="130" r="90" fill="none" stroke="#00F0B5" strokeWidth="1.5" strokeDasharray="4 3" opacity="0.7" />
                  {(() => {
                    const angle = dspProbeW * Math.PI;
                    const px = 140 + 90 * Math.cos(angle);
                    const py = 130 - 90 * Math.sin(angle);
                    return (
                      <g>
                        <line x1="140" y1="130" x2={px} y2={py} stroke="#f59e0b" strokeWidth="1" strokeDasharray="2 2" />
                        <circle cx={px} cy={py} r="4" fill="#f59e0b" />
                      </g>
                    );
                  })()}
                  {dspResults.poles.map((p, idx) => {
                    const cx = 140 + p.zR * 90;
                    const cy = 130 - p.zI * 90;
                    return (
                      <g key={idx}>
                        <line x1={cx - 4} y1={cy - 4} x2={cx + 4} y2={cy + 4} stroke="#38bdf8" strokeWidth="2.5" />
                        <line x1={cx - 4} y1={cy + 4} x2={cx + 4} y2={cy - 4} stroke="#38bdf8" strokeWidth="2.5" />
                      </g>
                    );
                  })}
                  {dspResults.zeros.map((z, idx) => (
                    <circle key={idx} cx={140 + z.zR * 90} cy={130 - z.zI * 90} r="4.5" fill="none" stroke="#f59e0b" strokeWidth="2" />
                  ))}
                </svg>
              </div>
              <div className="flex items-center justify-between text-[10px] text-slate-400 font-sans pt-1 border-t border-slate-800">
                <span className="text-cyan-400 font-mono">{dspResults.poles.length} System Poles</span>
                <button onClick={() => setShowDiagram(!showDiagram)} className="text-[#00F0B5] hover:underline">
                  {showDiagram ? 'Hide Butterfly' : 'View FFT Flow'} ↗
                </button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-2xl bg-[#041026] border border-slate-800">
            <div className="space-y-1">
              <span className="text-slate-400 text-xs font-mono">Architecture:</span>
              <div className="flex gap-2">
                {['lowpass', 'highpass', 'bandpass'].map((t) => (
                  <button key={t} onClick={() => setDspType(t)} className={`px-2.5 py-1 rounded-xl text-xs font-bold capitalize ${dspType === t ? 'bg-[#00693E] text-[#00F0B5] border border-[#00F0B5]/40' : 'bg-[#020813] text-slate-400 border border-slate-800'}`}>
                    {t}
                  </button>
                ))}
              </div>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Order N:</span>
                <span className="text-emerald-400 font-bold">{dspOrder}</span>
              </div>
              <input type="range" min="1" max="6" step="1" value={dspOrder} onChange={(e) => setDspOrder(parseInt(e.target.value, 10))} className="w-full h-1.5 bg-slate-800 rounded-lg accent-[#00F0B5]" />
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Cutoff ω_c:</span>
                <span className="text-cyan-400 font-bold">{dspWc.toFixed(2)}π</span>
              </div>
              <input type="range" min="0.08" max="0.85" step="0.01" value={dspWc} onChange={(e) => setDspWc(parseFloat(e.target.value))} className="w-full h-1.5 bg-slate-800 rounded-lg accent-cyan-400" />
            </div>
          </div>

          {showDiagram && (
            <div className="p-4 rounded-2xl bg-[#010610] border border-[#00F0B5]/40 space-y-3">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="font-bold text-slate-200">IEEE Radix-2 Decimation-In-Time (DIT-FFT) Butterfly Signal Flow Graph</span>
                <a href="/assets/diagrams/dsp_fft_butterfly_ieee.svg" target="_blank" rel="noopener noreferrer" className="text-[#00F0B5] hover:underline">Open Vector Source ↗</a>
              </div>
              <div className="w-full flex justify-center bg-[#020813] rounded-xl p-4 border border-slate-800">
                <img src="/assets/diagrams/dsp_fft_butterfly_ieee.svg" alt="IEEE DIT-FFT Butterfly" className="max-h-64 object-contain" />
              </div>
            </div>
          )}

          <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 text-xs text-slate-300 flex flex-wrap items-center justify-between gap-3">
            <span className="font-sans">
              <strong className="text-emerald-400 font-mono">Bilinear Transform:</strong> s = 2/T · (z - 1) / (z + 1) with tangent pre-warping Ω = 2/T · tan(ω/2)
            </span>
            <span className="text-[11px] text-slate-400 font-mono">MIT Campus ECE • Digital Signal Processing &amp; Linear Systems</span>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODE 4: DIGITAL LOGIC & FLIP-FLOP TIMING SLACK (EC23C04 / EC23C06 / HDL6001)
          ===================================================================== */}
      {activeMode === 'digital' && (
        <div className="space-y-6">
          {/* Readout Deck */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Max Frequency f_max</span>
              <div className="text-xl font-bold text-[#00F0B5] font-mono tracking-tight">
                {digitalResults.maxFreq.toFixed(1)} <span className="text-xs font-normal text-slate-400">MHz</span>
              </div>
              <span className="text-[10px] text-slate-500 font-sans block">1 / (t_cq + t_comb + t_setup)</span>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Setup Slack Δt</span>
              <div className={`text-xl font-bold font-mono tracking-tight ${
                digitalResults.isTimingMet ? 'text-emerald-400' : 'text-rose-400'
              }`}>
                {digitalResults.setupSlack > 0 ? `+${digitalResults.setupSlack.toFixed(2)}` : digitalResults.setupSlack.toFixed(2)} <span className="text-xs font-normal text-slate-400">ns</span>
              </div>
              <span className="text-[10px] text-slate-500 font-sans block">
                {digitalResults.isTimingMet ? '✦ Timing Closure Met' : '⚠ Setup Violation!'}
              </span>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Clock Period T_clk</span>
              <div className="text-xl font-bold text-white font-mono tracking-tight">
                {digitalResults.Tclk.toFixed(2)} <span className="text-xs font-normal text-slate-400">ns</span>
              </div>
              <span className="text-[10px] text-slate-500 font-sans block">At f_clk = {digitalFclk} MHz</span>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Hold Slack</span>
              <div className="text-xl font-bold text-amber-300 font-mono tracking-tight">
                +{digitalResults.holdSlack.toFixed(2)} <span className="text-xs font-normal text-slate-400">ns</span>
              </div>
              <span className="text-[10px] text-slate-500 font-sans block">t_cq - t_hold margin</span>
            </div>
          </div>

          {/* Graphical Waveform View */}
          <div className="rounded-2xl border border-slate-800 bg-[#010610] p-4 relative overflow-hidden shadow-inner space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800/80 text-xs">
              <span className="font-bold text-slate-300 flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${digitalResults.isTimingMet ? 'bg-emerald-400' : 'bg-rose-500 animate-pulse'}`}></span>
                <span>Flip-Flop Setup/Hold Timing Analyzer (Launch to Capture)</span>
              </span>
              <button
                type="button"
                onClick={() => setShowDiagram(!showDiagram)}
                className="text-[#00F0B5] hover:underline"
              >
                {showDiagram ? 'Hide Timing Spec' : 'View IEEE Timing Spec'} ↗
              </button>
            </div>

            {/* Dynamic SVG Waveform */}
            <div className="w-full aspect-[4.8/2.0]">
              <svg viewBox="0 0 600 240" className="w-full h-full select-none">
                {/* t=0 launch edge: x=100, t=Tclk capture edge: x=460 */}
                <line x1="100" y1="20" x2="100" y2="210" stroke="#00F0B5" strokeOpacity="0.3" strokeDasharray="3 3" />
                <line x1="460" y1="20" x2="460" y2="210" stroke="#00F0B5" strokeOpacity="0.4" strokeDasharray="3 3" />

                {/* Setup & Hold Shaded Windows */}
                {(() => {
                  const setupPx = Math.min(80, (digitalTsetup / digitalResults.Tclk) * 360);
                  const holdPx = Math.min(60, (digitalThold / digitalResults.Tclk) * 360);
                  const dataArrPx = 100 + ((digitalResults.dataArrival / digitalResults.Tclk) * 360);

                  return (
                    <>
                      {/* Setup Window (Red/Pink) */}
                      <rect x={460 - setupPx} y="20" width={setupPx} height="190" fill="#f43f5e" fillOpacity="0.18" />
                      {/* Hold Window (Amber) */}
                      <rect x="460" y="20" width={holdPx} height="190" fill="#f59e0b" fillOpacity="0.18" />

                      {/* CLK Waveform */}
                      <path d="M 40 60 L 100 60 L 100 30 L 280 30 L 280 60 L 460 60 L 460 30 L 580 30" stroke="#00F0B5" strokeWidth="2" fill="none" />
                      <text x="35" y="48" fill="#00F0B5" fontSize="10" textAnchor="end" fontFamily="monospace">CLK</text>

                      {/* Data Arrival Bus */}
                      <path d={`M 40 120 L 100 120 L 115 140 L ${Math.min(460, dataArrPx)} 140 L ${Math.min(475, dataArrPx + 15)} 120 L 580 120`} stroke="#38bdf8" strokeWidth="2" fill="none" />
                      <path d={`M 40 140 L 100 140 L 115 120 L ${Math.min(460, dataArrPx)} 120 L ${Math.min(475, dataArrPx + 15)} 140 L 580 140`} stroke="#38bdf8" strokeWidth="2" fill="none" strokeDasharray="2 2" />
                      <text x="35" y="132" fill="#38bdf8" fontSize="10" textAnchor="end" fontFamily="monospace">DATA</text>

                      {/* Data Settling Pointer */}
                      <line x1={dataArrPx} y1="110" x2={dataArrPx} y2="150" stroke={digitalResults.isTimingMet ? '#10b981' : '#f43f5e'} strokeWidth="2" />
                      <text x={dataArrPx} y="105" fill={digitalResults.isTimingMet ? '#10b981' : '#f43f5e'} fontSize="9" textAnchor="middle" fontFamily="monospace" fontWeight="bold">
                        Data Arrival: {digitalResults.dataArrival.toFixed(2)}ns
                      </text>

                      {/* Setup Slack annotation */}
                      {digitalResults.isTimingMet ? (
                        <rect x="360" y="165" width="90" height="20" rx="4" fill="#041026" stroke="#10b981" />
                      ) : (
                        <rect x="360" y="165" width="110" height="20" rx="4" fill="#881337" stroke="#f43f5e" />
                      )}
                      <text x="365" y="179" fill="#ffffff" fontSize="9" fontFamily="monospace">
                        Slack: {digitalResults.setupSlack.toFixed(2)}ns
                      </text>
                    </>
                  );
                })()}

                <text x="100" y="225" fill="#94a3b8" fontSize="9" textAnchor="middle" fontFamily="monospace">t = 0 (Launch)</text>
                <text x="460" y="225" fill="#94a3b8" fontSize="9" textAnchor="middle" fontFamily="monospace">t = T_clk (Capture)</text>
              </svg>
            </div>
          </div>

          {/* Sliders */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 rounded-2xl bg-[#041026] border border-slate-800">
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Clock f_clk:</span>
                <span className="text-emerald-400 font-bold">{digitalFclk} MHz</span>
              </div>
              <input type="range" min="20" max="250" step="5" value={digitalFclk} onChange={(e) => setDigitalFclk(parseInt(e.target.value, 10))} className="w-full h-1.5 bg-slate-800 rounded-lg accent-[#00F0B5]" />
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Combinational t_comb:</span>
                <span className="text-cyan-400 font-bold">{digitalTcomb.toFixed(1)} ns</span>
              </div>
              <input type="range" min="1.0" max="12.0" step="0.2" value={digitalTcomb} onChange={(e) => setDigitalTcomb(parseFloat(e.target.value))} className="w-full h-1.5 bg-slate-800 rounded-lg accent-cyan-400" />
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Setup Time t_setup:</span>
                <span className="text-amber-400 font-bold">{digitalTsetup.toFixed(1)} ns</span>
              </div>
              <input type="range" min="0.5" max="3.0" step="0.1" value={digitalTsetup} onChange={(e) => setDigitalTsetup(parseFloat(e.target.value))} className="w-full h-1.5 bg-slate-800 rounded-lg accent-amber-400" />
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Clock-to-Q t_cq:</span>
                <span className="text-purple-400 font-bold">{digitalTcq.toFixed(1)} ns</span>
              </div>
              <input type="range" min="0.4" max="3.0" step="0.1" value={digitalTcq} onChange={(e) => setDigitalTcq(parseFloat(e.target.value))} className="w-full h-1.5 bg-slate-800 rounded-lg accent-purple-400" />
            </div>
          </div>

          {showDiagram && (
            <div className="p-4 rounded-2xl bg-[#010610] border border-[#00F0B5]/40 space-y-3">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="font-bold text-slate-200">IEEE Std 1076 / Static Timing Analysis Setup &amp; Hold Specification</span>
                <a href="/assets/diagrams/digital_timing_slack_ieee.svg" target="_blank" rel="noopener noreferrer" className="text-[#00F0B5] hover:underline">Open Vector Source ↗</a>
              </div>
              <div className="w-full flex justify-center bg-[#020813] rounded-xl p-4 border border-slate-800">
                <img src="/assets/diagrams/digital_timing_slack_ieee.svg" alt="IEEE Digital Timing Slack" className="max-h-64 object-contain" />
              </div>
            </div>
          )}

          <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 text-xs text-slate-300 flex flex-wrap items-center justify-between gap-3">
            <span className="font-sans">
              <strong className="text-emerald-400 font-mono">Setup Closure Condition:</strong> T_clk ≥ t_cq + t_comb + t_setup &nbsp;|&nbsp; Slack = T_clk - (t_cq + t_comb + t_setup) ≥ 0
            </span>
            <span className="text-[11px] text-slate-400 font-mono">MIT Campus ECE • Digital Systems &amp; Hardware Description Languages</span>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODE 5: COMMUNICATION MODULATION & SHANNON CAPACITY
          ===================================================================== */}
      {activeMode === 'comm' && (
        <div className="space-y-6">
          {/* Readout Deck */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Shannon Capacity C</span>
              <div className="text-xl font-bold text-[#00F0B5] font-mono tracking-tight">
                {commResults.capacityMbps.toFixed(2)} <span className="text-xs font-normal text-slate-400">Mbps</span>
              </div>
              <span className="text-[10px] text-slate-500 font-sans block">B · log2(1 + SNR)</span>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Spectral Efficiency</span>
              <div className="text-xl font-bold text-white font-mono tracking-tight">
                {commResults.spectralEff.toFixed(2)} <span className="text-xs font-normal text-slate-400">bps/Hz</span>
              </div>
              <span className="text-[10px] text-slate-500 font-sans block">η = C / B</span>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Channel Eb / N0</span>
              <div className="text-xl font-bold text-cyan-300 font-mono tracking-tight">
                {commResults.ebNoDb.toFixed(2)} <span className="text-xs font-normal text-slate-400">dB</span>
              </div>
              <span className="text-[10px] text-slate-500 font-sans block">Limit: &gt; -1.59 dB</span>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Estimated Bit Error P_b</span>
              <div className="text-xl font-bold text-amber-300 font-mono tracking-tight">
                {commResults.ber < 1e-4 ? commResults.ber.toExponential(2) : commResults.ber.toFixed(4)}
              </div>
              <span className="text-[10px] text-slate-500 font-sans block">{commMod.toUpperCase()} Constellation</span>
            </div>
          </div>

          {/* Interactive Constellation Display */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            <div className="lg:col-span-7 rounded-2xl border border-slate-800 bg-[#010610] p-4 relative overflow-hidden shadow-inner space-y-2">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800/80 text-xs">
                <span className="font-bold text-slate-300 flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-[#00F0B5]"></span>
                  <span>In-Phase (I) vs Quadrature (Q) Signal Space Constellation</span>
                </span>
                <span className="text-[10px] text-slate-400 font-mono">
                  SNR: <strong className="text-[#00F0B5]">{commSnrDb.toFixed(1)} dB</strong>
                </span>
              </div>

              {/* SVG Constellation */}
              <div className="w-full aspect-[4.8/3.2] flex justify-center items-center">
                <svg viewBox="0 0 360 260" className="w-full h-full select-none">
                  <line x1="20" y1="130" x2="340" y2="130" stroke="#334155" strokeWidth="1.2" />
                  <line x1="180" y1="10" x2="180" y2="250" stroke="#334155" strokeWidth="1.2" />
                  <text x="335" y="125" fill="#64748b" fontSize="9" textAnchor="end" fontFamily="monospace">In-Phase (I)</text>
                  <text x="185" y="20" fill="#64748b" fontSize="9" fontFamily="monospace">Quad (Q)</text>
                  <circle cx="180" cy="130" r="85" fill="none" stroke="#1e293b" strokeDasharray="3 3" />

                  {/* Render Points based on Modulation Scheme with noise jitter */}
                  {(() => {
                    const scatterR = Math.min(22, Math.max(3, commResults.noiseStd * 70));
                    let coords = [];
                    if (commMod === 'bpsk') {
                      coords = [{ x: -60, y: 0, label: '0' }, { x: 60, y: 0, label: '1' }];
                    } else if (commMod === 'qpsk') {
                      coords = [
                        { x: -50, y: -50, label: '00' }, { x: 50, y: -50, label: '01' },
                        { x: -50, y: 50, label: '10' }, { x: 50, y: 50, label: '11' }
                      ];
                    } else {
                      // 16-QAM
                      const vals = [-75, -25, 25, 75];
                      vals.forEach(ix => {
                        vals.forEach(qy => {
                          coords.push({ x: ix, y: qy, label: '' });
                        });
                      });
                    }

                    return coords.map((pt, idx) => {
                      const cx = 180 + pt.x;
                      const cy = 130 - pt.y;
                      return (
                        <g key={idx}>
                          <circle cx={cx} cy={cy} r={scatterR} fill="#00F0B5" fillOpacity="0.18" />
                          <circle cx={cx} cy={cy} r="4.5" fill="#00F0B5" stroke="#ffffff" strokeWidth="1.5" />
                          {pt.label && (
                            <text x={cx} y={cy - 8} fill="#38bdf8" fontSize="8" textAnchor="middle" fontFamily="monospace">{pt.label}</text>
                          )}
                        </g>
                      );
                    });
                  })()}
                </svg>
              </div>

              <div className="flex items-center justify-between text-[10px] text-slate-400 font-sans pt-1 border-t border-slate-800">
                <span>Constellation Dispersion ∝ 1 / √(2 · SNR)</span>
                <button onClick={() => setShowDiagram(!showDiagram)} className="text-[#00F0B5] hover:underline">
                  {showDiagram ? 'Hide Constellation Diagram' : 'View IEEE 16-QAM Poster'} ↗
                </button>
              </div>
            </div>

            {/* Modulation Controls */}
            <div className="lg:col-span-5 p-4 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
              <div className="space-y-1">
                <span className="text-slate-400 text-xs font-mono">Modulation Scheme:</span>
                <div className="flex gap-2">
                  {['bpsk', 'qpsk', '16qam'].map((m) => (
                    <button
                      key={m}
                      onClick={() => setCommMod(m)}
                      className={`px-3 py-1.5 rounded-xl text-xs font-bold uppercase transition-all ${
                        commMod === m
                          ? 'bg-[#00693E] text-[#00F0B5] border border-[#00F0B5]/40 shadow-sm'
                          : 'bg-[#020813] text-slate-400 border border-slate-800 hover:text-white'
                      }`}
                    >
                      {m}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400 font-mono">Bandwidth B:</span>
                  <span className="text-emerald-400 font-bold font-mono">{commBw.toFixed(1)} MHz</span>
                </div>
                <input
                  type="range"
                  min="0.5"
                  max="25.0"
                  step="0.5"
                  value={commBw}
                  onChange={(e) => setCommBw(parseFloat(e.target.value))}
                  className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-[#00F0B5]"
                />
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400 font-mono">Signal-to-Noise Ratio:</span>
                  <span className="text-cyan-400 font-bold font-mono">{commSnrDb.toFixed(1)} dB</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="35"
                  step="0.5"
                  value={commSnrDb}
                  onChange={(e) => setCommSnrDb(parseFloat(e.target.value))}
                  className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                />
              </div>

              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800/80 text-[11px] text-slate-300 space-y-1">
                <div className="text-slate-400 font-bold text-[10px] uppercase">Channel Bound Metrics:</div>
                <div className="flex justify-between">
                  <span>Linear SNR:</span>
                  <span className="text-white font-mono">{commResults.snrLin.toFixed(1)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Theoretical Shannon Bound:</span>
                  <span className="text-white font-mono">{commResults.capacityMbps.toFixed(2)} Mbps</span>
                </div>
              </div>
            </div>
          </div>

          {showDiagram && (
            <div className="p-4 rounded-2xl bg-[#010610] border border-[#00F0B5]/40 space-y-3">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="font-bold text-slate-200">IEEE Standard 16-QAM Constellation &amp; Shannon Capacity Space</span>
                <a href="/assets/diagrams/comm_constellation_ieee.svg" target="_blank" rel="noopener noreferrer" className="text-[#00F0B5] hover:underline">Open Vector Source ↗</a>
              </div>
              <div className="w-full flex justify-center bg-[#020813] rounded-xl p-4 border border-slate-800">
                <img src="/assets/diagrams/comm_constellation_ieee.svg" alt="IEEE 16-QAM Constellation" className="max-h-64 object-contain" />
              </div>
            </div>
          )}

          <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 text-xs text-slate-300 flex flex-wrap items-center justify-between gap-3">
            <span className="font-sans">
              <strong className="text-emerald-400 font-mono">Shannon-Hartley Theorem:</strong> C = B · log2(1 + S/N) [Bits/sec] &nbsp;|&nbsp; Limit: Eb/N0 ≥ ln(2) ≈ -1.59 dB
            </span>
            <span className="text-[11px] text-slate-400 font-mono">MIT Campus ECE • Analog &amp; Digital Communication Systems</span>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODE 6: BOOLEAN K-MAP SIMPLIFIER & BODE ASYMPTOTIC EXPLORER
          ===================================================================== */}
      {activeMode === 'kmap_bode' && (
        <div className="space-y-6">
          {/* Readout Summary Deck */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-mono">Corner Freq (f_c)</div>
              <div className="text-xl font-extrabold text-[#00F0B5] font-mono mt-0.5">
                {bodeFc >= 1000 ? `${(bodeFc / 1000).toFixed(1)} kHz` : `${bodeFc} Hz`}
              </div>
              <div className="text-[10px] text-slate-500 mt-1">Cutoff Boundary</div>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-mono">Asymptotic Roll-off</div>
              <div className="text-xl font-extrabold text-cyan-400 font-mono mt-0.5">
                {bodeResults.rollOffSlope} dB/dec
              </div>
              <div className="text-[10px] text-slate-500 mt-1">Order n = {bodeOrder}</div>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-mono">Damping (ζ) &amp; Q</div>
              <div className="text-xl font-extrabold text-amber-400 font-mono mt-0.5">
                Q = {bodeResults.qFactor.toFixed(2)}
              </div>
              <div className="text-[10px] text-slate-500 mt-1">ζ = {bodeZeta.toFixed(3)}</div>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-mono">Phase at f_c</div>
              <div className="text-xl font-extrabold text-purple-400 font-mono mt-0.5">
                {bodeResults.phaseAtFc}°
              </div>
              <div className="text-[10px] text-slate-500 mt-1">Lag angle</div>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-mono">Active Minterms</div>
              <div className="text-xl font-extrabold text-emerald-400 font-mono mt-0.5">
                {kmapResults.activeCount} / 16
              </div>
              <div className="text-[10px] text-slate-500 mt-1">4-Variable K-Map</div>
            </div>
          </div>

          {/* Interactive Workbenches Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left 6 cols: 4-Variable Karnaugh Map (Gray Code 00, 01, 11, 10) */}
            <div className="lg:col-span-6 p-4 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <span className="text-sm">🔲</span>
                  <span className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
                    4-Variable Karnaugh Map [A, B, C, D]
                  </span>
                </div>
                <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/30">
                  Gray-Code Ordered
                </span>
              </div>

              {/* K-Map Quick Presets */}
              <div className="flex flex-wrap items-center gap-1.5 font-mono text-[10px]">
                <button
                  type="button"
                  onClick={() => setKmapPreset('fa_sum')}
                  className="px-2 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white"
                >
                  Adder Sum
                </button>
                <button
                  type="button"
                  onClick={() => setKmapPreset('fa_carry')}
                  className="px-2 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white"
                >
                  Carry / Majority
                </button>
                <button
                  type="button"
                  onClick={() => setKmapPreset('parity')}
                  className="px-2 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white"
                >
                  Parity
                </button>
                <button
                  type="button"
                  onClick={() => setKmapPreset('invert')}
                  className="px-2 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-amber-400"
                >
                  Invert
                </button>
                <button
                  type="button"
                  onClick={() => setKmapPreset('zero')}
                  className="px-2 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-rose-400"
                >
                  Clear (All 0)
                </button>
              </div>

              {/* 4x4 K-Map Grid */}
              <div className="overflow-x-auto">
                <table className="w-full text-center border-collapse font-mono text-xs">
                  <thead>
                    <tr>
                      <th className="p-1.5 text-slate-500 text-[10px] border border-slate-800 bg-[#020813]">AB \ CD</th>
                      {['00', '01', '11', '10'].map(cd => (
                        <th key={cd} className="p-1.5 text-cyan-400 font-bold border border-slate-800 bg-[#020813] text-[11px]">
                          {cd}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      { ab: '00', minterms: [0, 1, 3, 2] },
                      { ab: '01', minterms: [4, 5, 7, 6] },
                      { ab: '11', minterms: [12, 13, 15, 14] },
                      { ab: '10', minterms: [8, 9, 11, 10] }
                    ].map(row => (
                      <tr key={row.ab}>
                        <td className="p-1.5 font-bold text-emerald-400 border border-slate-800 bg-[#020813] text-[11px]">
                          {row.ab}
                        </td>
                        {row.minterms.map(mIdx => {
                          const val = kmapCells[mIdx];
                          return (
                            <td
                              key={mIdx}
                              onClick={() => toggleKmapCell(mIdx)}
                              className={`p-3 border border-slate-800 cursor-pointer transition-all ${
                                val === 1
                                  ? 'bg-emerald-500/25 text-emerald-300 font-extrabold border-emerald-500/50 shadow-inner'
                                  : 'bg-slate-950/60 text-slate-600 hover:bg-slate-900'
                              }`}
                            >
                              <div className="text-base font-bold">{val}</div>
                              <div className="text-[9px] text-slate-500 mt-0.5">m{mIdx}</div>
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Minimized / Canonical SOP Readout */}
              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800 space-y-1 font-mono text-xs">
                <div className="text-slate-400 text-[10px] uppercase font-bold">Canonical Sum-of-Products (SOP):</div>
                <div className="text-emerald-400 font-bold break-all">
                  {kmapResults.canonicalSop}
                </div>
              </div>
            </div>

            {/* Right 6 cols: Asymptotic & Live Bode Magnitude/Phase Plot */}
            <div className="lg:col-span-6 p-4 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <span className="text-sm">📈</span>
                  <span className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
                    Bode Asymptotic Magnitude &amp; Phase
                  </span>
                </div>
                <div className="flex items-center gap-2 font-mono text-[10px]">
                  <button
                    onClick={() => setBodeType(bodeType === 'lowpass' ? 'highpass' : 'lowpass')}
                    className="px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-500/40 uppercase font-bold"
                  >
                    {bodeType}
                  </button>
                </div>
              </div>

              {/* Interactive Sliders */}
              <div className="grid grid-cols-3 gap-3 font-mono text-xs">
                <div className="space-y-1">
                  <div className="flex justify-between text-[11px]">
                    <span className="text-slate-400">f_c:</span>
                    <span className="text-emerald-400 font-bold">
                      {bodeFc >= 1000 ? `${(bodeFc / 1000).toFixed(1)}k` : `${bodeFc}`}Hz
                    </span>
                  </div>
                  <input
                    type="range"
                    min="50"
                    max="50000"
                    step="50"
                    value={bodeFc}
                    onChange={(e) => setBodeFc(parseFloat(e.target.value))}
                    className="w-full h-1.5 bg-slate-800 rounded-lg accent-[#00F0B5]"
                  />
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between text-[11px]">
                    <span className="text-slate-400">Order:</span>
                    <span className="text-cyan-400 font-bold">n = {bodeOrder}</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="3"
                    step="1"
                    value={bodeOrder}
                    onChange={(e) => setBodeOrder(parseInt(e.target.value, 10))}
                    className="w-full h-1.5 bg-slate-800 rounded-lg accent-cyan-400"
                  />
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between text-[11px]">
                    <span className="text-slate-400">Damping ζ:</span>
                    <span className="text-amber-400 font-bold">{bodeZeta.toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min="0.1"
                    max="1.5"
                    step="0.05"
                    value={bodeZeta}
                    onChange={(e) => setBodeZeta(parseFloat(e.target.value))}
                    className="w-full h-1.5 bg-slate-800 rounded-lg accent-amber-400"
                  />
                </div>
              </div>

              {/* Live SVG Bode Magnitude Plot */}
              <div className="p-3 rounded-xl bg-[#020813] border border-slate-800/80">
                <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 mb-1">
                  <span>Magnitude Response |H(jω)| [dB]</span>
                  <span className="text-emerald-400">Slope: {bodeResults.rollOffSlope} dB/decade</span>
                </div>
                <svg viewBox="0 0 400 160" className="w-full h-40">
                  {/* Grid Lines */}
                  <line x1="40" y1="20" x2="380" y2="20" stroke="#1E293B" strokeDasharray="3 3" />
                  <line x1="40" y1="50" x2="380" y2="50" stroke="#334155" />
                  <line x1="40" y1="85" x2="380" y2="85" stroke="#1E293B" strokeDasharray="3 3" />
                  <line x1="40" y1="120" x2="380" y2="120" stroke="#1E293B" strokeDasharray="3 3" />
                  <line x1="40" y1="150" x2="380" y2="150" stroke="#1E293B" strokeDasharray="3 3" />

                  {/* Frequency Vertical Lines (4 decades) */}
                  <line x1="40" y1="10" x2="40" y2="150" stroke="#334155" />
                  <line x1="125" y1="10" x2="125" y2="150" stroke="#1E293B" strokeDasharray="2 2" />
                  <line x1="210" y1="10" x2="210" y2="150" stroke="#00F0B5" strokeWidth="1.5" />
                  <line x1="295" y1="10" x2="295" y2="150" stroke="#1E293B" strokeDasharray="2 2" />
                  <line x1="380" y1="10" x2="380" y2="150" stroke="#334155" />

                  {/* Axis Text */}
                  <text x="35" y="54" fill="#94A3B8" fontSize="9" textAnchor="end" fontFamily="monospace">0dB</text>
                  <text x="35" y="89" fill="#94A3B8" fontSize="9" textAnchor="end" fontFamily="monospace">-20</text>
                  <text x="35" y="124" fill="#94A3B8" fontSize="9" textAnchor="end" fontFamily="monospace">-40</text>
                  <text x="210" y="160" fill="#00F0B5" fontSize="9" textAnchor="middle" fontFamily="monospace">f_c</text>

                  {/* Asymptotic straight line guide */}
                  {bodeType === 'lowpass' ? (
                    <polyline
                      points={`40,50 210,50 380,${50 + (170 / 85) * (-bodeResults.rollOffSlope * 1.5)}`}
                      fill="none"
                      stroke="#F59E0B"
                      strokeWidth="1.5"
                      strokeDasharray="4 3"
                      opacity="0.6"
                    />
                  ) : (
                    <polyline
                      points={`40,${50 + (170 / 85) * (bodeResults.rollOffSlope * 1.5)} 210,50 380,50`}
                      fill="none"
                      stroke="#F59E0B"
                      strokeWidth="1.5"
                      strokeDasharray="4 3"
                      opacity="0.6"
                    />
                  )}

                  {/* Actual Curve */}
                  <polyline
                    points={bodeResults.points.map((pt, idx) => {
                      const x = 40 + (idx / (bodeResults.points.length - 1)) * 340;
                      // 0 dB is at y = 50. -80 dB is at y = 150. (+20 dB is at y = 20)
                      const y = 50 - (pt.magDb / 20) * 25;
                      return `${x.toFixed(1)},${y.toFixed(1)}`;
                    }).join(' ')}
                    fill="none"
                    stroke="#00F0B5"
                    strokeWidth="2.5"
                  />
                </svg>
              </div>
            </div>
          </div>

          {/* Footer Technical Attribution */}
          <div className="p-3.5 rounded-2xl bg-[#041026] border border-slate-800 text-xs text-slate-300 flex flex-wrap items-center justify-between gap-3">
            <span className="font-sans">
              <strong className="text-emerald-400 font-mono">Bode Stability Criterion:</strong> Gain Margin GM ≥ 6 dB &nbsp;|&nbsp; Phase Margin PM ≥ 45° for robust closed-loop stability.
            </span>
            <span className="text-[11px] text-slate-400 font-mono">MIT Campus ECE • Control Systems Engineering &amp; Linear Circuits</span>
          </div>
        </div>
      )}


    </div>
  );
}
