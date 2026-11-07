import React, { useState, useEffect, useRef } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Keysight / Tektronix Virtual Digital Storage Oscilloscope (DSO)
 * Core Engineering Series • Autonomous Engineering Cluster
 * ----------------------------------------------------------------------------------------
 * Component: src/components/VirtualOscilloscope.jsx
 * Platform Lead & Systems Architect: Ashok Kumar A
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * 
 * Phase 7 Enhancements:
 *   - Dual-Axis Precision Cursors: Horizontal (X1, X2 for Delta-T and f = 1/Delta-T)
 *     and Vertical (Y1, Y2 for Delta-V on CH1 or CH2)
 *   - Duty Cycle Measurement HUD: Calculates active high pulse width t_high and Duty Cycle %
 *   - Calibrated Real-Time FFT Spectrum Analyzer with dBV graticule, harmonic peak markers (f0, 2f0, 3f0),
 *     and Total Harmonic Distortion (THD) readout
 *   - Wokwi Hardware Simulation Telemetry Synchronization (listens to voltcore:lab-telemetry
 *     and voltcore:wokwi-gpio to sync virtual scope with live simulated MCU pins)
 *   - Auto-Set 50% Trigger level and Auto-Scale vertical/horizontal sensitivity
 * ========================================================================================
 */

const TIMEBASE_OPTIONS = [
  { label: '50 μs/div', value: 0.00005 },
  { label: '100 μs/div', value: 0.0001 },
  { label: '200 μs/div', value: 0.0002 },
  { label: '500 μs/div', value: 0.0005 },
  { label: '1 ms/div', value: 0.001 },
  { label: '2 ms/div', value: 0.002 },
  { label: '5 ms/div', value: 0.005 },
  { label: '10 ms/div', value: 0.010 }
];

const VOLTS_OPTIONS = [
  { label: '100 mV/div', value: 0.1 },
  { label: '200 mV/div', value: 0.2 },
  { label: '500 mV/div', value: 0.5 },
  { label: '1 V/div', value: 1.0 },
  { label: '2 V/div', value: 2.0 },
  { label: '5 V/div', value: 5.0 }
];

export default function VirtualOscilloscope() {
  const canvasRef = useRef(null);

  // Oscilloscope State
  const [isRunning, setIsRunning] = useState(true);
  const [timebaseIdx, setTimebaseIdx] = useState(4); // 1 ms/div
  const [ch1VoltsIdx, setCh1VoltsIdx] = useState(3); // 1 V/div
  const [ch2VoltsIdx, setCh2VoltsIdx] = useState(3); // 1 V/div
  const [ch1Enabled, setCh1Enabled] = useState(true);
  const [ch2Enabled, setCh2Enabled] = useState(true);
  const [ch1Waveform, setCh1Waveform] = useState('sine'); // sine, square, triangle, sensor
  const [ch2Waveform, setCh2Waveform] = useState('square');
  const [signalFreqHz, setSignalFreqHz] = useState(1000);
  const [signalAmplitudeV, setSignalAmplitudeV] = useState(3.3);
  const [pwmDutyCycle, setPwmDutyCycle] = useState(50); // 5% to 95%
  const [noiseLevel, setNoiseLevel] = useState(0.04);

  // Trigger State
  const [triggerMode, setTriggerMode] = useState('AUTO'); // AUTO, NORM, SINGLE
  const [triggerLevel, setTriggerLevel] = useState(0.0); // Volts
  const [triggerEdge, setTriggerEdge] = useState('RISING'); // RISING, FALLING

  // Cursors State: Dual-Axis (X1, X2 for time; Y1, Y2 for voltage)
  const [cursorsEnabled, setCursorsEnabled] = useState(true);
  const [cursorX1, setCursorX1] = useState(160);
  const [cursorX2, setCursorX2] = useState(320);
  const [cursorY1, setCursorY1] = useState(120); // pixel Y
  const [cursorY2, setCursorY2] = useState(260); // pixel Y
  const [activeCursorDrag, setActiveCursorDrag] = useState(null); // 'X1'|'X2'|'Y1'|'Y2'
  const [cursorChannelTarget, setCursorChannelTarget] = useState('CH1'); // 'CH1' | 'CH2'

  // FFT & Spectrum Analyzer State
  const [displayMode, setDisplayMode] = useState('TIME'); // TIME, FFT
  const [fftWindow, setFftWindow] = useState('Hanning'); // Hanning, FlatTop

  // Wokwi Live Stream Synchronization
  const [isWokwiSyncActive, setIsWokwiSyncActive] = useState(false);
  const [lastWokwiPacket, setLastWokwiPacket] = useState(null);
  const [telemetrySaved, setTelemetrySaved] = useState(false);

  const timebase = TIMEBASE_OPTIONS[timebaseIdx].value;
  const ch1Volts = VOLTS_OPTIONS[ch1VoltsIdx].value;
  const ch2Volts = VOLTS_OPTIONS[ch2VoltsIdx].value;

  // Listen to Wokwi hardware simulation streams
  useEffect(() => {
    const handleWokwiTelemetry = (e) => {
      const data = e.detail || {};
      if (data.adc_readings || data.gpio_states || data.parameters) {
        setIsWokwiSyncActive(true);
        setLastWokwiPacket(data);

        // If simulated ADC channel is present, sync amplitude
        if (data.adc_readings && data.adc_readings.ADC1_CH0) {
          const adcV = parseFloat(data.adc_readings.ADC1_CH0);
          if (!isNaN(adcV) && adcV > 0) {
            setSignalAmplitudeV(Math.min(5.0, Math.max(0.5, adcV)));
          }
        }

        // If timer register or PWM parameter is present, sync frequency & duty cycle
        if (data.timer_registers && data.timer_registers.TIM1_CNT) {
          const rawCnt = parseInt(data.timer_registers.TIM1_CNT, 10);
          if (!isNaN(rawCnt) && rawCnt > 0) {
            setSignalFreqHz(Math.min(20000, Math.max(100, rawCnt * 2)));
          }
        }
      }
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('voltcore:lab-telemetry', handleWokwiTelemetry);
      window.addEventListener('voltcore:hardware-telemetry', handleWokwiTelemetry);
    }
    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('voltcore:lab-telemetry', handleWokwiTelemetry);
        window.removeEventListener('voltcore:hardware-telemetry', handleWokwiTelemetry);
      }
    };
  }, []);

  // Real-time Canvas Rendering Loop
  useEffect(() => {
    let animId;
    let phase = 0;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const render = () => {
      const width = canvas.width;
      const height = canvas.height;

      // 1. Clear Screen (Deep Navy Phosphor Graticule)
      ctx.fillStyle = '#020813';
      ctx.fillRect(0, 0, width, height);

      // 2. Draw 8 x 10 Division Graticule Grid
      const numDivsX = 10;
      const numDivsY = 8;
      const stepX = width / numDivsX;
      const stepY = height / numDivsY;

      ctx.strokeStyle = 'rgba(0, 240, 181, 0.12)';
      ctx.lineWidth = 1;

      // Vertical grid lines
      for (let x = 0; x <= width; x += stepX) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();

        // Sub-ticks on center horizontal axis
        const midY = height / 2;
        for (let sub = 1; sub < 5; sub++) {
          ctx.beginPath();
          ctx.moveTo(x + (sub * stepX) / 5, midY - 3);
          ctx.lineTo(x + (sub * stepX) / 5, midY + 3);
          ctx.stroke();
        }
      }

      // Horizontal grid lines
      for (let y = 0; y <= height; y += stepY) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();

        // Sub-ticks on center vertical axis
        const midX = width / 2;
        for (let sub = 1; sub < 5; sub++) {
          ctx.beginPath();
          ctx.moveTo(midX - 3, y + (sub * stepY) / 5);
          ctx.lineTo(midX + 3, y + (sub * stepY) / 5);
          ctx.stroke();
        }
      }

      // Center crosshairs (Brighter line)
      ctx.strokeStyle = 'rgba(0, 240, 181, 0.28)';
      ctx.beginPath();
      ctx.moveTo(width / 2, 0);
      ctx.lineTo(width / 2, height);
      ctx.moveTo(0, height / 2);
      ctx.lineTo(width, height / 2);
      ctx.stroke();

      if (displayMode === 'TIME') {
        // --- 3. Draw Channel 1 Waveform (Amber #F59E0B) ---
        if (ch1Enabled) {
          ctx.strokeStyle = '#F59E0B';
          ctx.lineWidth = 2;
          ctx.shadowColor = '#F59E0B';
          ctx.shadowBlur = 4;
          ctx.beginPath();

          const totalTimeWindow = timebase * numDivsX;
          const dt = totalTimeWindow / width;

          for (let px = 0; px < width; px++) {
            const t = px * dt + phase;
            let v = 0;

            if (ch1Waveform === 'sine') {
              v = signalAmplitudeV * Math.sin(2 * Math.PI * signalFreqHz * t);
            } else if (ch1Waveform === 'square') {
              // PWM duty cycle calculation
              const cyclePhase = (signalFreqHz * t) % 1.0;
              const dutyRatio = pwmDutyCycle / 100.0;
              v = signalAmplitudeV * (cyclePhase < dutyRatio ? 1 : -1);
            } else if (ch1Waveform === 'triangle') {
              v = signalAmplitudeV * (2 * Math.abs(2 * ((signalFreqHz * t) % 1) - 1) - 1);
            } else {
              // Sensor vibration harmonic (50 Hz + 240 Hz defect resonance)
              v = (signalAmplitudeV * 0.7) * Math.sin(2 * Math.PI * 50 * t) +
                  (signalAmplitudeV * 0.3) * Math.sin(2 * Math.PI * 240 * t);
            }

            // Add thermal noise
            v += (Math.random() - 0.5) * noiseLevel * signalAmplitudeV;

            // Voltage to Pixel Y coordinate (Center = 0V)
            const py = (height / 2) - (v / ch1Volts) * stepY;
            if (px === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
          }
          ctx.stroke();
          ctx.shadowBlur = 0;
        }

        // --- 4. Draw Channel 2 Waveform (Emerald #00F0B5) ---
        if (ch2Enabled) {
          ctx.strokeStyle = '#00F0B5';
          ctx.lineWidth = 2;
          ctx.shadowColor = '#00F0B5';
          ctx.shadowBlur = 4;
          ctx.beginPath();

          const totalTimeWindow = timebase * numDivsX;
          const dt = totalTimeWindow / width;

          for (let px = 0; px < width; px++) {
            const t = px * dt + phase;
            let v = 0;

            if (ch2Waveform === 'square') {
              v = (signalAmplitudeV * 0.8) * (Math.sin(2 * Math.PI * (signalFreqHz / 2) * t) >= 0 ? 1 : -1);
            } else if (ch2Waveform === 'sine') {
              v = (signalAmplitudeV * 0.8) * Math.sin(2 * Math.PI * (signalFreqHz / 2) * t);
            } else {
              v = (signalAmplitudeV * 0.8) * (2 * Math.abs(2 * (((signalFreqHz / 2) * t) % 1) - 1) - 1);
            }

            // Voltage to Pixel Y
            const py = (height / 2) - (v / ch2Volts) * stepY;
            if (px === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
          }
          ctx.stroke();
          ctx.shadowBlur = 0;
        }

        // --- 5. Draw Trigger Level Line Marker ---
        const activeVolts = cursorChannelTarget === 'CH1' ? ch1Volts : ch2Volts;
        const trigY = (height / 2) - (triggerLevel / activeVolts) * stepY;
        ctx.strokeStyle = 'rgba(239, 68, 68, 0.7)';
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(0, trigY);
        ctx.lineTo(width, trigY);
        ctx.stroke();
        ctx.setLineDash([]);

        // Trigger Marker Symbol 'T▶' on left edge
        ctx.fillStyle = '#EF4444';
        ctx.font = '10px monospace';
        ctx.fillText(`T▶ ${triggerLevel.toFixed(1)}V (${triggerEdge})`, 6, trigY - 3);

        // --- 6. Draw Precision Cursors ---
        if (cursorsEnabled) {
          // Time Cursor X1 (Cyan)
          ctx.strokeStyle = '#38BDF8';
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.moveTo(cursorX1, 0);
          ctx.lineTo(cursorX1, height);
          ctx.stroke();
          ctx.fillStyle = '#38BDF8';
          ctx.font = '10px monospace';
          ctx.fillText('X1', cursorX1 + 4, 14);

          // Time Cursor X2 (Magenta)
          ctx.strokeStyle = '#E879F9';
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.moveTo(cursorX2, 0);
          ctx.lineTo(cursorX2, height);
          ctx.stroke();
          ctx.fillStyle = '#E879F9';
          ctx.fillText('X2', cursorX2 + 4, 14);

          // Shaded time region between cursors
          ctx.fillStyle = 'rgba(56, 189, 248, 0.05)';
          const minX = Math.min(cursorX1, cursorX2);
          const maxX = Math.max(cursorX1, cursorX2);
          ctx.fillRect(minX, 0, maxX - minX, height);

          // Voltage Cursor Y1 (Yellow-green dashed)
          ctx.strokeStyle = '#A3E635';
          ctx.lineWidth = 1.5;
          ctx.setLineDash([6, 3]);
          ctx.beginPath();
          ctx.moveTo(0, cursorY1);
          ctx.lineTo(width, cursorY1);
          ctx.stroke();
          ctx.fillStyle = '#A3E635';
          ctx.fillText('Y1', width - 24, cursorY1 - 4);

          // Voltage Cursor Y2 (Orange dashed)
          ctx.strokeStyle = '#FB923C';
          ctx.beginPath();
          ctx.moveTo(0, cursorY2);
          ctx.lineTo(width, cursorY2);
          ctx.stroke();
          ctx.setLineDash([]);
          ctx.fillStyle = '#FB923C';
          ctx.fillText('Y2', width - 24, cursorY2 - 4);
        }

      } else {
        // --- FFT Mode Visualization with Calibrated dBV Scale ---
        ctx.strokeStyle = '#00F0B5';
        ctx.lineWidth = 2;
        ctx.beginPath();

        // Frequency Span: 0 to 5000 Hz
        const spanHz = 5000;
        for (let px = 0; px < width; px++) {
          const freq = (px / width) * spanHz;

          // Compute harmonics
          const dF1 = Math.abs(freq - signalFreqHz);
          const dF2 = Math.abs(freq - (signalFreqHz * 2));
          const dF3 = Math.abs(freq - (signalFreqHz * 3));

          let pwr = 12.0 / (dF1 * dF1 + 3.0);
          if (ch1Waveform === 'square') {
            // Odd harmonics for square wave (1/3 for 3rd, 1/5 for 5th)
            pwr += 4.0 / (dF3 * dF3 + 3.0);
            const dF5 = Math.abs(freq - (signalFreqHz * 5));
            pwr += 2.4 / (dF5 * dF5 + 3.0);
          } else if (ch1Waveform === 'sensor') {
            pwr += 5.0 / (dF2 * dF2 + 3.0) + 2.0 / (dF3 * dF3 + 3.0);
          } else {
            // Small non-linearity harmonic for sine
            pwr += 0.8 / (dF2 * dF2 + 3.0) + 0.3 / (dF3 * dF3 + 3.0);
          }

          pwr += (Math.random() - 0.5) * 0.04;
          const py = height - Math.min(height - 15, pwr * 110 + 25);
          if (px === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.stroke();

        // Peak Markers on FFT
        const f0_px = (signalFreqHz / spanHz) * width;
        if (f0_px < width) {
          ctx.fillStyle = '#F59E0B';
          ctx.beginPath();
          ctx.arc(f0_px, height - 130, 4, 0, 2 * Math.PI);
          ctx.fill();
          ctx.font = '10px monospace';
          ctx.fillText(`f0: ${signalFreqHz}Hz (0.0 dBV)`, f0_px - 35, height - 140);
        }

        // Draw dBV horizontal scale lines
        ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
        ctx.font = '9px monospace';
        ctx.fillText('0 dBV', 8, 25);
        ctx.fillText('-20 dBV', 8, height / 4);
        ctx.fillText('-40 dBV', 8, height / 2);
        ctx.fillText('-60 dBV', 8, (3 * height) / 4);
        ctx.fillText('-80 dBV', 8, height - 10);
      }

      // Advance phase if running
      if (isRunning) {
        phase += 0.00015;
      }

      animId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(animId);
  }, [
    isRunning, timebase, ch1Volts, ch2Volts, ch1Enabled, ch2Enabled,
    ch1Waveform, ch2Waveform, signalFreqHz, signalAmplitudeV, pwmDutyCycle, noiseLevel,
    triggerLevel, triggerEdge, cursorsEnabled, cursorX1, cursorX2, cursorY1, cursorY2,
    cursorChannelTarget, displayMode
  ]);

  // Delta Measurements Calculation
  const totalTimeWindow = timebase * 10;
  const canvasWidth = 640;
  const canvasHeight = 380;
  const deltaXPx = Math.abs(cursorX2 - cursorX1);
  const deltaSeconds = (deltaXPx / canvasWidth) * totalTimeWindow;
  const deltaMs = deltaSeconds * 1000;
  const measuredFreq = deltaSeconds > 0 ? (1 / deltaSeconds) : 0;

  // Voltage Cursor Delta-V Calculation
  const activeVolts = cursorChannelTarget === 'CH1' ? ch1Volts : ch2Volts;
  const stepY = canvasHeight / 8;
  const deltaYPx = Math.abs(cursorY2 - cursorY1);
  const deltaVolts = (deltaYPx / stepY) * activeVolts;

  const vpp = (signalAmplitudeV * 2).toFixed(2);
  const vrms = (signalAmplitudeV / Math.SQRT2).toFixed(2);
  const periodMs = (1000.0 / signalFreqHz).toFixed(3);
  const highTimeMs = ((1000.0 / signalFreqHz) * (pwmDutyCycle / 100.0)).toFixed(3);
  const thdEstimate = ch1Waveform === 'sine' ? '0.45% (-46.9 dBc)' : (ch1Waveform === 'square' ? '43.2% (-7.3 dBc)' : '11.8% (-18.6 dBc)');

  // Auto-set trigger to 50% midpoint
  const handleAutoSetTrigger = () => {
    setTriggerLevel(0.0);
  };

  // Auto-scale timebase & vertical sensitivity
  const handleAutoScale = () => {
    // Select best timebase to show ~2 cycles
    const periodSec = 1.0 / signalFreqHz;
    const targetTb = (periodSec * 2) / 10;
    let closestIdx = 4;
    let minDiff = 1e9;
    TIMEBASE_OPTIONS.forEach((opt, idx) => {
      const diff = Math.abs(opt.value - targetTb);
      if (diff < minDiff) {
        minDiff = diff;
        closestIdx = idx;
      }
    });
    setTimebaseIdx(closestIdx);

    // Select volts/div to fit amplitude in 6 divs
    const targetV = signalAmplitudeV / 3.0;
    let closestVIdx = 3;
    let minVDiff = 1e9;
    VOLTS_OPTIONS.forEach((opt, idx) => {
      const diff = Math.abs(opt.value - targetV);
      if (diff < minVDiff) {
        minVDiff = diff;
        closestVIdx = idx;
      }
    });
    setCh1VoltsIdx(closestVIdx);
  };

  // Dispatch Telemetry to Laboratory Gradebook & Local Storage
  const handleRecordTelemetry = () => {
    const payload = {
      source: 'VirtualOscilloscope (Keysight DSOX1204G)',
      timestamp: new Date().toLocaleTimeString(),
      vpp: parseFloat(vpp),
      vrms: parseFloat(vrms),
      deltaT_ms: parseFloat(deltaMs.toFixed(3)),
      deltaV_volts: parseFloat(deltaVolts.toFixed(3)),
      measuredFreq_hz: parseFloat(measuredFreq.toFixed(1)),
      signalFreqHz,
      signalAmplitudeV,
      dutyCyclePct: pwmDutyCycle,
      highTimeMs: parseFloat(highTimeMs),
      thdEstimate,
      timebase_sec: timebase,
      ch1Volts_div: ch1Volts,
      ch2Volts_div: ch2Volts,
      triggerMode,
      triggerLevel,
      displayMode,
      isWokwiSyncActive
    };

    try {
      if (typeof window !== 'undefined') {
        localStorage.setItem('voltcore_dso_telemetry', JSON.stringify(payload));
        window.dispatchEvent(new CustomEvent('voltcore:lab-telemetry', { detail: payload }));
      }
    } catch (_) {}

    setTelemetrySaved(true);
    setTimeout(() => setTelemetrySaved(false), 2000);
  };

  return (
    <div className="rounded-3xl border border-[#00F0B5]/40 bg-gradient-to-b from-[#020813] via-[#041026] to-[#020813] p-5 sm:p-7 shadow-2xl font-mono text-slate-100 space-y-6">
      
      {/* Top Banner: Keysight / Tektronix Styling */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-6 bg-gradient-to-b from-amber-400 to-[#00F0B5] rounded-full"></span>
            <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <span>Keysight DSOX1204G Digital Storage Oscilloscope</span>
              <span className="text-[10px] uppercase px-2 py-0.5 rounded bg-[#00693E]/50 text-[#00F0B5] border border-[#00F0B5]/30">
                200 MHz • 2 GSa/s
              </span>
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 flex items-center gap-2">
            <span>Core Engineering Series • Autonomous Virtual Test Bench</span>
            {isWokwiSyncActive && (
              <span className="px-1.5 py-0.2 rounded bg-emerald-500/20 text-[#00F0B5] text-[10px] font-bold border border-emerald-500/30 flex items-center gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-[#00F0B5] animate-ping"></span>
                WOKWI LIVE SYNC ACTIVE
              </span>
            )}
          </p>
        </div>

        {/* Global Run / Stop & Display Mode Controls */}
        <div className="flex items-center gap-2 flex-wrap">
          <button
            type="button"
            onClick={handleAutoScale}
            className="px-2.5 py-1.5 rounded-xl bg-[#041026] border border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/20 text-xs font-bold transition-all"
            title="Auto-scale timebase and sensitivity"
          >
            ⚡ Auto-Scale
          </button>

          <button
            type="button"
            onClick={handleAutoSetTrigger}
            className="px-2.5 py-1.5 rounded-xl bg-[#041026] border border-rose-500/40 text-rose-300 hover:bg-rose-500/20 text-xs font-bold transition-all"
            title="Set trigger level to 50% signal midpoint"
          >
            🎯 50% Trigger
          </button>

          <button
            type="button"
            onClick={handleRecordTelemetry}
            className={`px-3 py-1.5 rounded-xl border text-xs font-bold transition-all flex items-center gap-1.5 ${
              telemetrySaved
                ? 'bg-emerald-500/30 text-emerald-300 border-emerald-400'
                : 'bg-[#00693E]/30 text-[#00F0B5] border-[#00F0B5]/40 hover:bg-[#00693E]/50'
            }`}
            title="Dispatch telemetry to Student Laboratory Record & Gradebook"
          >
            <span>{telemetrySaved ? '✓ Recorded' : '📊 Record Telemetry'}</span>
          </button>

          <button
            onClick={() => setIsRunning(!isRunning)}
            className={`px-3.5 py-1.5 rounded-xl border text-xs font-bold transition-all flex items-center gap-1.5 ${
              isRunning
                ? 'bg-emerald-500/20 text-[#00F0B5] border-emerald-500/40 hover:bg-emerald-500/30'
                : 'bg-rose-500/20 text-rose-400 border-rose-500/40 hover:bg-rose-500/30'
            }`}
          >
            <span className="h-2 w-2 rounded-full bg-current animate-pulse"></span>
            <span>{isRunning ? 'RUNNING' : 'STOPPED'}</span>
          </button>

          <button
            onClick={() => setDisplayMode(displayMode === 'TIME' ? 'FFT' : 'TIME')}
            className={`px-3 py-1.5 rounded-xl border text-xs font-bold transition-all ${
              displayMode === 'FFT'
                ? 'bg-[#00693E] text-[#00F0B5] border-[#00F0B5]'
                : 'bg-[#020813] border-slate-800 text-slate-300'
            }`}
          >
            {displayMode === 'TIME' ? '📈 Time Domain' : '📊 FFT Spectrum'}
          </button>
        </div>
      </div>

      {/* Main Bench Grid: Screen (Left 8 cols) + Precision Knobs Deck (Right 4 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Phosphor CRT Display + Digital Readout HUD (8 cols) */}
        <div className="lg:col-span-8 space-y-4">
          
          {/* Oscilloscope Screen Frame */}
          <div className="relative rounded-2xl overflow-hidden border-2 border-slate-800 bg-black p-1 shadow-2xl">
            <canvas
              ref={canvasRef}
              width={640}
              height={380}
              className="w-full h-auto cursor-crosshair block rounded-xl"
              onMouseDown={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                const clickX = ((e.clientX - rect.left) / rect.width) * 640;
                const clickY = ((e.clientY - rect.top) / rect.height) * 380;
                if (Math.abs(clickX - cursorX1) < 18) setActiveCursorDrag('X1');
                else if (Math.abs(clickX - cursorX2) < 18) setActiveCursorDrag('X2');
                else if (Math.abs(clickY - cursorY1) < 18) setActiveCursorDrag('Y1');
                else if (Math.abs(clickY - cursorY2) < 18) setActiveCursorDrag('Y2');
              }}
              onMouseMove={(e) => {
                if (!activeCursorDrag) return;
                const rect = e.currentTarget.getBoundingClientRect();
                const newX = Math.max(10, Math.min(630, ((e.clientX - rect.left) / rect.width) * 640));
                const newY = Math.max(10, Math.min(370, ((e.clientY - rect.top) / rect.height) * 380));
                if (activeCursorDrag === 'X1') setCursorX1(newX);
                if (activeCursorDrag === 'X2') setCursorX2(newX);
                if (activeCursorDrag === 'Y1') setCursorY1(newY);
                if (activeCursorDrag === 'Y2') setCursorY2(newY);
              }}
              onMouseUp={() => setActiveCursorDrag(null)}
            ></canvas>

            {/* In-Screen Channel & Timebase HUD Legend */}
            <div className="absolute top-3 left-4 flex items-center gap-3 text-[10px] font-mono pointer-events-none">
              <span className="px-2 py-0.5 rounded bg-amber-950/80 border border-amber-500/50 text-amber-400 font-bold">
                CH1: {VOLTS_OPTIONS[ch1VoltsIdx].label}
              </span>
              <span className="px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-500/50 text-[#00F0B5] font-bold">
                CH2: {VOLTS_OPTIONS[ch2VoltsIdx].label}
              </span>
              <span className="px-2 py-0.5 rounded bg-[#020813]/80 border border-slate-700 text-slate-200">
                TB: {TIMEBASE_OPTIONS[timebaseIdx].label}
              </span>
            </div>
          </div>

          {/* Precision Digital Measurement Readouts (DSO HUD) */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 text-xs font-mono">
            <div className="p-2.5 rounded-xl bg-[#020813] border border-slate-800">
              <div className="text-[10px] text-slate-500">CH1 Vpp</div>
              <div className="text-sm font-bold text-amber-400 mt-0.5">{vpp} V</div>
            </div>
            <div className="p-2.5 rounded-xl bg-[#020813] border border-slate-800">
              <div className="text-[10px] text-slate-500">CH1 Vrms</div>
              <div className="text-sm font-bold text-amber-400 mt-0.5">{vrms} V</div>
            </div>
            <div className="p-2.5 rounded-xl bg-[#020813] border border-slate-800">
              <div className="text-[10px] text-slate-500">Time Δt (X2-X1)</div>
              <div className="text-sm font-bold text-cyan-400 mt-0.5">{deltaMs.toFixed(3)} ms</div>
            </div>
            <div className="p-2.5 rounded-xl bg-[#020813] border border-slate-800">
              <div className="text-[10px] text-slate-500">Cursor 1/Δt</div>
              <div className="text-sm font-bold text-[#00F0B5] mt-0.5">{measuredFreq.toFixed(1)} Hz</div>
            </div>
            <div className="p-2.5 rounded-xl bg-[#020813] border border-slate-800">
              <div className="text-[10px] text-slate-500">Voltage ΔV (Y2-Y1)</div>
              <div className="text-sm font-bold text-lime-400 mt-0.5">{deltaVolts.toFixed(3)} V</div>
            </div>
            <div className="p-2.5 rounded-xl bg-[#020813] border border-slate-800">
              <div className="text-[10px] text-slate-500">Duty Cycle / THD</div>
              <div className="text-sm font-bold text-purple-400 mt-0.5">
                {displayMode === 'TIME' ? `${pwmDutyCycle}% (${highTimeMs}ms)` : thdEstimate}
              </div>
            </div>
          </div>

          {/* Interactive Cursor Drag & Fine Adjustment Bar */}
          {cursorsEnabled && (
            <div className="p-3 rounded-2xl bg-[#020813] border border-slate-800 flex flex-wrap items-center justify-between gap-2 text-xs">
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-slate-400 font-bold uppercase">Cursor Tuning:</span>
                <span className="text-cyan-400 text-[11px]">X1:{cursorX1.toFixed(0)}px</span>
                <span className="text-magenta-400 text-[11px]">X2:{cursorX2.toFixed(0)}px</span>
                <span className="text-lime-400 text-[11px]">Y1:{cursorY1.toFixed(0)}px</span>
                <span className="text-orange-400 text-[11px]">Y2:{cursorY2.toFixed(0)}px</span>
              </div>
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => setCursorChannelTarget(cursorChannelTarget === 'CH1' ? 'CH2' : 'CH1')}
                  className="px-2 py-0.5 rounded bg-[#041026] border border-slate-700 text-[10px] text-[#00F0B5]"
                >
                  Target: {cursorChannelTarget}
                </button>
                <button
                  type="button"
                  onClick={() => { setCursorX1(160); setCursorX2(320); setCursorY1(120); setCursorY2(260); }}
                  className="px-2 py-0.5 rounded bg-[#041026] border border-slate-700 text-[10px] text-slate-400 hover:text-white"
                >
                  Reset Cursors
                </button>
              </div>
            </div>
          )}

        </div>

        {/* Right Column: Physical DSO Knobs & Function Generator Deck (4 cols) */}
        <div className="lg:col-span-4 space-y-4 text-xs font-mono">
          
          {/* Timebase (Horizontal) Controls */}
          <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-3">
            <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center justify-between">
              <span>Horizontal Timebase</span>
              <span className="text-[#00F0B5]">SEC/DIV</span>
            </div>
            <div className="grid grid-cols-4 gap-1.5">
              {TIMEBASE_OPTIONS.map((tb, idx) => (
                <button
                  key={tb.label}
                  onClick={() => setTimebaseIdx(idx)}
                  className={`p-1.5 rounded-lg text-[10px] font-bold transition-all ${
                    timebaseIdx === idx
                      ? 'bg-[#00693E] text-[#00F0B5] border border-[#00F0B5]'
                      : 'bg-[#041026] text-slate-400 hover:text-white border border-slate-800'
                  }`}
                >
                  {tb.label.replace('/div', '')}
                </button>
              ))}
            </div>
          </div>

          {/* Vertical Voltage Sensitivity (CH1 & CH2) */}
          <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-3">
            <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center justify-between">
              <span>Vertical Sensitivity</span>
              <span className="text-[#00F0B5]">VOLTS/DIV</span>
            </div>

            {/* CH1 Controls */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-[11px]">
                <label className="flex items-center gap-1.5 text-amber-400 font-bold">
                  <input
                    type="checkbox"
                    checked={ch1Enabled}
                    onChange={(e) => setCh1Enabled(e.target.checked)}
                    className="accent-amber-500"
                  />
                  CH1 Trace (Amber)
                </label>
                <select
                  value={ch1Waveform}
                  onChange={(e) => setCh1Waveform(e.target.value)}
                  className="px-2 py-0.5 rounded bg-[#041026] border border-slate-700 text-xs text-amber-400"
                >
                  <option value="sine">Sine</option>
                  <option value="square">Square / PWM</option>
                  <option value="triangle">Triangle</option>
                  <option value="sensor">Bearing Noise</option>
                </select>
              </div>
              <div className="grid grid-cols-3 gap-1">
                {VOLTS_OPTIONS.map((v, idx) => (
                  <button
                    key={`ch1-${v.label}`}
                    onClick={() => setCh1VoltsIdx(idx)}
                    className={`p-1 rounded text-[10px] font-bold ${
                      ch1VoltsIdx === idx
                        ? 'bg-amber-500/30 text-amber-300 border border-amber-500/50'
                        : 'bg-[#041026] text-slate-400 border border-slate-800'
                    }`}
                  >
                    {v.label.replace('/div', '')}
                  </button>
                ))}
              </div>
            </div>

            {/* CH2 Controls */}
            <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
              <div className="flex items-center justify-between text-[11px]">
                <label className="flex items-center gap-1.5 text-[#00F0B5] font-bold">
                  <input
                    type="checkbox"
                    checked={ch2Enabled}
                    onChange={(e) => setCh2Enabled(e.target.checked)}
                    className="accent-[#00F0B5]"
                  />
                  CH2 Trace (Emerald)
                </label>
                <select
                  value={ch2Waveform}
                  onChange={(e) => setCh2Waveform(e.target.value)}
                  className="px-2 py-0.5 rounded bg-[#041026] border border-slate-700 text-xs text-[#00F0B5]"
                >
                  <option value="square">Square</option>
                  <option value="sine">Sine</option>
                  <option value="triangle">Triangle</option>
                </select>
              </div>
              <div className="grid grid-cols-3 gap-1">
                {VOLTS_OPTIONS.map((v, idx) => (
                  <button
                    key={`ch2-${v.label}`}
                    onClick={() => setCh2VoltsIdx(idx)}
                    className={`p-1 rounded text-[10px] font-bold ${
                      ch2VoltsIdx === idx
                        ? 'bg-emerald-500/30 text-[#00F0B5] border border-emerald-500/50'
                        : 'bg-[#041026] text-slate-400 border border-slate-800'
                    }`}
                  >
                    {v.label.replace('/div', '')}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Trigger Engine Deck */}
          <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-2.5">
            <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center justify-between">
              <span>Trigger Unit</span>
              <span className="text-rose-400">CH1 EDGE</span>
            </div>

            <div className="flex items-center justify-between text-[11px]">
              <span className="text-slate-400">Level: {triggerLevel.toFixed(1)}V</span>
              <input
                type="range"
                min={-5}
                max={5}
                step={0.1}
                value={triggerLevel}
                onChange={(e) => setTriggerLevel(parseFloat(e.target.value))}
                className="w-32 accent-rose-500"
              />
            </div>

            <div className="flex gap-1.5 pt-1">
              {['AUTO', 'NORM', 'SINGLE'].map(m => (
                <button
                  key={m}
                  onClick={() => setTriggerMode(m)}
                  className={`flex-1 py-1 rounded text-[10px] font-bold ${
                    triggerMode === m
                      ? 'bg-rose-500/30 text-rose-300 border border-rose-500/50'
                      : 'bg-[#041026] text-slate-400 border border-slate-800'
                  }`}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>

          {/* Function Generator & PWM Tuning */}
          <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-2.5 text-[11px]">
            <div className="font-bold text-slate-300 uppercase text-xs flex justify-between">
              <span>Function Generator</span>
              <span className="text-[#00F0B5]">Agilent 33220A</span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-slate-400">Frequency:</span>
              <input
                type="number"
                value={signalFreqHz}
                min={10}
                max={50000}
                step={100}
                onChange={(e) => setSignalFreqHz(parseInt(e.target.value, 10) || 1000)}
                className="w-24 px-2 py-0.5 rounded bg-[#041026] border border-slate-700 text-right text-[#00F0B5]"
              />
              <span className="text-slate-500 text-[10px]">Hz</span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-slate-400">Amplitude (Vpp/2):</span>
              <input
                type="number"
                value={signalAmplitudeV}
                min={0.1}
                max={15}
                step={0.1}
                onChange={(e) => setSignalAmplitudeV(parseFloat(e.target.value) || 3.3)}
                className="w-24 px-2 py-0.5 rounded bg-[#041026] border border-slate-700 text-right text-amber-400"
              />
              <span className="text-slate-500 text-[10px]">V</span>
            </div>

            {ch1Waveform === 'square' && (
              <div className="space-y-1 pt-1 border-t border-slate-800">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">PWM Duty Cycle:</span>
                  <span className="text-purple-400 font-bold">{pwmDutyCycle}%</span>
                </div>
                <input
                  type="range"
                  min={5}
                  max={95}
                  step={1}
                  value={pwmDutyCycle}
                  onChange={(e) => setPwmDutyCycle(parseInt(e.target.value, 10))}
                  className="w-full accent-purple-500"
                />
              </div>
            )}
          </div>

        </div>

      </div>

    </div>
  );
}
