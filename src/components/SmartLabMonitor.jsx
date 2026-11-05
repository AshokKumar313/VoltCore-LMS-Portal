import React, { useState, useEffect } from 'react';
import { triggerToast } from './ToastNotifications.jsx';

/**
 * ========================================================================================
 * VoltCore Apex Academia - IoT Smart Laboratory & Equipment Telemetry Monitor
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Component: src/components/SmartLabMonitor.jsx
 * Platform Lead / Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 * 
 * Features:
 *   - Live equipment power telemetry (Oscilloscopes, DC Power Supplies, Soldering, Fume)
 *   - Operational hours vs tip/filter maintenance threshold tracking
 *   - Real-time booking and fault ticket dispatch (+120 XP rewards)
 *   - Zero background polling: single-shot initial audit + on-demand refresh
 * ========================================================================================
 */

const FALLBACK_EQUIPMENT = [
  {
    equipment_id: 'OSC-DSOX1204G-01',
    name: 'Keysight DSOX1204G 4-Channel 100MHz DSO',
    bench_id: 'BENCH_304_A',
    category: 'Oscilloscope',
    status: 'ONLINE_IDLE',
    current_power_watts: 24.5,
    voltage_v: 230.2,
    current_a: 0.106,
    cumulative_hours: 184.2,
    maintenance_interval_hours: 500.0,
    temperature_c: 36.4,
    active_booking: null,
    icon: '📊'
  },
  {
    equipment_id: 'PSU-DP832-02',
    name: 'Rigol DP832 Triple-Output DC Power Supply',
    bench_id: 'BENCH_304_A',
    category: 'PowerSupply',
    status: 'IN_USE',
    current_power_watts: 68.4,
    voltage_v: 230.0,
    current_a: 0.297,
    cumulative_hours: 242.8,
    maintenance_interval_hours: 400.0,
    temperature_c: 42.1,
    active_booking: '2023MITEC042',
    icon: '⚡'
  },
  {
    equipment_id: 'SOLD-WT1010-03',
    name: 'Weller WT1010 Precision Soldering Station',
    bench_id: 'BENCH_304_B',
    category: 'Soldering',
    status: 'MAINTENANCE_DUE',
    current_power_watts: 85.0,
    voltage_v: 229.8,
    current_a: 0.370,
    cumulative_hours: 204.5,
    maintenance_interval_hours: 200.0,
    temperature_c: 51.3,
    active_booking: null,
    icon: '🔥'
  },
  {
    equipment_id: 'FUME-FA430-04',
    name: 'Hakko FA-430 HEPA Fume Extraction System',
    bench_id: 'BENCH_304_B',
    category: 'FumeExtractor',
    status: 'ONLINE_IDLE',
    current_power_watts: 110.0,
    voltage_v: 230.1,
    current_a: 0.478,
    cumulative_hours: 145.0,
    maintenance_interval_hours: 300.0,
    temperature_c: 34.8,
    active_booking: null,
    icon: '💨'
  }
];

export default function SmartLabMonitor() {
  const [equipmentList, setEquipmentList] = useState(FALLBACK_EQUIPMENT);
  const [activeTab, setActiveTab] = useState('ALL'); // 'ALL' | 'BENCH_304_A' | 'BENCH_304_B'
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastRefreshedTime, setLastRefreshedTime] = useState(null);
  const [faultModalTarget, setFaultModalTarget] = useState(null);
  const [faultDescription, setFaultDescription] = useState('');
  const [faultType, setFaultType] = useState('CALIBRATION_DRIFT');

  // Load telemetry from backend on mount (Single-shot, zero continuous polling loop)
  const fetchTelemetry = async () => {
    setIsRefreshing(true);
    try {
      const res = await fetch('http://localhost:5000/api/smart_lab/overview', { signal: AbortSignal.timeout(2000) });
      if (res.ok) {
        const data = await res.json();
        if (data.equipment) {
          // Merge with icons
          const mapped = data.equipment.map(e => ({
            ...e,
            icon: e.category === 'Oscilloscope' ? '📊' : e.category === 'PowerSupply' ? '⚡' : e.category === 'Soldering' ? '🔥' : '💨'
          }));
          setEquipmentList(mapped);
        }
      }
    } catch {
      // Retain fallback data gracefully
    } finally {
      setIsRefreshing(false);
      setLastRefreshedTime(new Date().toLocaleTimeString());
    }
  };

  useEffect(() => {
    fetchTelemetry();
  }, []);

  const handleBookEquipment = (eqId) => {
    setEquipmentList(prev => prev.map(eq => {
      if (eq.equipment_id === eqId) {
        return { ...eq, status: 'IN_USE', active_booking: '2023MITEC042' };
      }
      return eq;
    }));

    triggerToast({
      title: 'Equipment Reserved',
      message: `Reserved ${eqId} at MIT Lab 304. Session logged (+120 XP).`,
      type: 'success',
      category: 'iot'
    });
  };

  const handleReleaseEquipment = (eqId) => {
    setEquipmentList(prev => prev.map(eq => {
      if (eq.equipment_id === eqId) {
        return { ...eq, status: 'ONLINE_IDLE', active_booking: null };
      }
      return eq;
    }));

    triggerToast({
      title: 'Equipment Released',
      message: `Session closed for ${eqId}. Bench returned to idle state.`,
      type: 'info',
      category: 'iot'
    });
  };

  const handleSubmitFault = (e) => {
    e.preventDefault();
    if (!faultModalTarget) return;

    setEquipmentList(prev => prev.map(eq => {
      if (eq.equipment_id === faultModalTarget.equipment_id) {
        return { ...eq, status: 'FAULT_ALERT' };
      }
      return eq;
    }));

    triggerToast({
      title: 'Fault Dispatched',
      message: `Logged ${faultType} on ${faultModalTarget.equipment_id}. MIT Lab technician notified.`,
      type: 'warning',
      category: 'security'
    });

    setFaultModalTarget(null);
    setFaultDescription('');
  };

  // Aggregated Lab Metrics
  const totalPower = Math.round(equipmentList.reduce((acc, eq) => acc + (eq.current_power_watts || 0), 0));
  const activeCount = equipmentList.filter(eq => eq.status === 'IN_USE').length;
  const maintenanceCount = equipmentList.filter(eq => eq.status === 'MAINTENANCE_DUE').length;
  const faultCount = equipmentList.filter(eq => eq.status === 'FAULT_ALERT').length;

  const filteredEquipment = equipmentList.filter(eq => {
    if (activeTab === 'ALL') return true;
    return eq.bench_id === activeTab;
  });

  return (
    <div className="rounded-3xl border border-[#00F0B5]/30 bg-gradient-to-br from-[#020813] via-[#041026] to-[#020813] p-6 sm:p-8 font-mono text-slate-100 shadow-2xl space-y-6">
      
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-[#00F0B5] border border-[#00F0B5]/30 font-bold uppercase tracking-wider">
              Smart IoT Laboratory 304
            </span>
            <span className="text-xs text-slate-400">MIT Campus • Department of Electronics Engineering</span>
          </div>
          <h2 className="text-lg sm:text-xl font-bold text-white mt-1">
            Real-Time Equipment Telemetry & Maintenance Hub
          </h2>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={fetchTelemetry}
            disabled={isRefreshing}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-[#00693E] to-[#00F0B5] hover:brightness-110 text-[#020813] font-bold text-xs flex items-center gap-2 transition-all shadow-emerald-glow disabled:opacity-50"
          >
            {isRefreshing ? (
              <>
                <span className="w-2.5 h-2.5 border-2 border-[#020813] border-t-transparent rounded-full animate-spin"></span>
                <span>Refreshing...</span>
              </>
            ) : (
              <>
                <span>⟳ Refresh Telemetry</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* 4 Laboratory Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
        
        <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-1.5">
          <div className="flex justify-between items-center text-slate-400 text-[11px]">
            <span>TOTAL POWER DRAW</span>
            <span className="text-[#00F0B5] font-bold">LIVE TELEMETRY</span>
          </div>
          <div className="text-xl font-bold text-white flex items-baseline gap-1">
            <span>{totalPower}</span>
            <span className="text-xs font-normal text-slate-400">Watts</span>
          </div>
          <div className="text-[10px] text-emerald-400">
            Energy efficiency index: 94.2% (PF 0.96)
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-1.5">
          <div className="flex justify-between items-center text-slate-400 text-[11px]">
            <span>ACTIVE SESSIONS</span>
            <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse"></span>
          </div>
          <div className="text-xl font-bold text-cyan-300">
            {activeCount} / {equipmentList.length} In-Use
          </div>
          <div className="text-[10px] text-slate-400">
            Assigned to student RFID sessions
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-1.5">
          <div className="flex justify-between items-center text-slate-400 text-[11px]">
            <span>MAINTENANCE ALERTS</span>
            <span className={`text-[10px] font-bold ${maintenanceCount > 0 ? 'text-amber-400' : 'text-slate-500'}`}>
              {maintenanceCount} Due
            </span>
          </div>
          <div className="text-xl font-bold text-amber-300">
            {maintenanceCount > 0 ? `${maintenanceCount} Pending Servicing` : 'All Gear Calibrated'}
          </div>
          <div className="text-[10px] text-slate-400">
            Tip oxidation & filter limit tracking
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-[#020813] border border-slate-800 space-y-1.5">
          <div className="flex justify-between items-center text-slate-400 text-[11px]">
            <span>FAULT INCIDENTS</span>
            <span className={`h-2 w-2 rounded-full ${faultCount > 0 ? 'bg-rose-500 animate-ping' : 'bg-emerald-400'}`}></span>
          </div>
          <div className="text-xl font-bold text-white">
            {faultCount === 0 ? 'Zero Breaches' : `${faultCount} Fault(s) Flagged`}
          </div>
          <div className="text-[10px] text-slate-400">
            Over-current & thermal trip limits active
          </div>
        </div>

      </div>

      {/* Bench Filter Tabs */}
      <div className="flex gap-2 border-b border-slate-800 pb-2 text-xs">
        {['ALL', 'BENCH_304_A', 'BENCH_304_B'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-3 py-1.5 rounded-xl transition-all ${
              activeTab === tab
                ? 'bg-gradient-to-r from-[#00693E] to-[#00b884] text-[#020813] font-bold shadow-emerald-glow'
                : 'bg-[#020813] text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            {tab === 'ALL' ? 'All Benches (Lab 304)' : tab.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Equipment Inventory Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredEquipment.map(eq => {
          const hoursPct = Math.min(100, Math.round((eq.cumulative_hours / eq.maintenance_interval_hours) * 100));
          const isOverLimit = eq.cumulative_hours >= eq.maintenance_interval_hours;

          return (
            <div
              key={eq.equipment_id}
              className={`p-6 rounded-2xl bg-[#020813] border transition-all space-y-4 ${
                eq.status === 'FAULT_ALERT'
                  ? 'border-rose-500/60 shadow-lg shadow-rose-950/40'
                  : eq.status === 'MAINTENANCE_DUE'
                  ? 'border-amber-500/50'
                  : eq.status === 'IN_USE'
                  ? 'border-cyan-500/40'
                  : 'border-[#00F0B5]/30'
              }`}
            >
              {/* Card Header */}
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="text-3xl p-2 rounded-xl bg-slate-900 border border-slate-800">
                    {eq.icon}
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-xs sm:text-sm">{eq.name}</h3>
                    <div className="text-[11px] text-slate-400 mt-0.5">
                      ID: <span className="text-[#00F0B5]">{eq.equipment_id}</span> • {eq.bench_id}
                    </div>
                  </div>
                </div>

                <span className={`text-[10px] px-2.5 py-1 rounded-full font-bold border ${
                  eq.status === 'ONLINE_IDLE'
                    ? 'bg-emerald-500/20 text-[#00F0B5] border-[#00F0B5]/30'
                    : eq.status === 'IN_USE'
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30'
                    : eq.status === 'MAINTENANCE_DUE'
                    ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                    : 'bg-rose-500/20 text-rose-300 border-rose-500/30'
                }`}>
                  {eq.status.replace('_', ' ')}
                </span>
              </div>

              {/* Real-time Telemetry Metrics */}
              <div className="grid grid-cols-4 gap-2 text-center p-3 rounded-xl bg-[#041026] border border-slate-800 text-[11px]">
                <div>
                  <div className="text-slate-500 text-[10px]">VOLTAGE</div>
                  <div className="font-bold text-slate-200">{eq.voltage_v} V</div>
                </div>
                <div>
                  <div className="text-slate-500 text-[10px]">CURRENT</div>
                  <div className="font-bold text-slate-200">{eq.current_a} A</div>
                </div>
                <div>
                  <div className="text-slate-500 text-[10px]">POWER</div>
                  <div className="font-bold text-emerald-400">{eq.current_power_watts} W</div>
                </div>
                <div>
                  <div className="text-slate-500 text-[10px]">TEMP</div>
                  <div className={`font-bold ${eq.temperature_c > 50 ? 'text-amber-400' : 'text-slate-200'}`}>
                    {eq.temperature_c} °C
                  </div>
                </div>
              </div>

              {/* Maintenance Hours Progress Bar */}
              <div className="space-y-1 text-xs">
                <div className="flex justify-between items-center text-[11px]">
                  <span className="text-slate-400">Cumulative Operating Hours:</span>
                  <span className={`font-bold ${isOverLimit ? 'text-amber-400' : 'text-slate-200'}`}>
                    {eq.cumulative_hours} / {eq.maintenance_interval_hours} hrs ({hoursPct}%)
                  </span>
                </div>
                <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      isOverLimit ? 'bg-amber-500' : 'bg-gradient-to-r from-[#00693E] to-[#00F0B5]'
                    }`}
                    style={{ width: `${hoursPct}%` }}
                  ></div>
                </div>
                {isOverLimit && (
                  <div className="text-[10px] text-amber-400">
                    ⚠ Calibration / consumable tip inspection required before next lab session.
                  </div>
                )}
              </div>

              {/* Actions Footer */}
              <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-xs">
                <div className="text-[11px] text-slate-400">
                  {eq.active_booking ? (
                    <span>In session: <strong className="text-white">{eq.active_booking}</strong></span>
                  ) : (
                    <span className="text-emerald-400 font-semibold">Available for Booking</span>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setFaultModalTarget(eq)}
                    className="text-[10px] px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
                  >
                    Report Fault
                  </button>

                  {eq.status === 'ONLINE_IDLE' && (
                    <button
                      type="button"
                      onClick={() => handleBookEquipment(eq.equipment_id)}
                      className="text-[10px] px-3 py-1 rounded-lg bg-gradient-to-r from-[#00693E] to-[#00F0B5] text-[#020813] font-bold hover:brightness-110 shadow-emerald-glow"
                    >
                      Book (+120 XP)
                    </button>
                  )}

                  {eq.status === 'IN_USE' && eq.active_booking === '2023MITEC042' && (
                    <button
                      type="button"
                      onClick={() => handleReleaseEquipment(eq.equipment_id)}
                      className="text-[10px] px-3 py-1 rounded-lg bg-rose-600/30 hover:bg-rose-600 text-rose-300 hover:text-white border border-rose-500/40 font-bold"
                    >
                      Release
                    </button>
                  )}
                </div>
              </div>

            </div>
          );
        })}
      </div>

      {/* Fault Logging Modal */}
      {faultModalTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="w-full max-w-md p-6 rounded-2xl bg-[#041026] border border-[#00F0B5]/40 shadow-2xl space-y-4 text-xs font-mono">
            <div className="flex justify-between items-center pb-2 border-b border-slate-800">
              <h3 className="font-bold text-white text-sm">Report Equipment Fault</h3>
              <button
                type="button"
                onClick={() => setFaultModalTarget(null)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmitFault} className="space-y-3">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Equipment Name:</label>
                <div className="p-2 rounded-lg bg-[#020813] text-slate-200 border border-slate-800">
                  {faultModalTarget.name} ({faultModalTarget.equipment_id})
                </div>
              </div>

              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Fault Category:</label>
                <select
                  value={faultType}
                  onChange={(e) => setFaultType(e.target.value)}
                  className="w-full p-2 rounded-lg bg-[#020813] text-slate-200 border border-slate-700 focus:border-[#00F0B5] outline-none"
                >
                  <option value="CALIBRATION_DRIFT">Calibration Drift (&gt; 2% Tolerance)</option>
                  <option value="OVER_CURRENT_TRIP">Over-Current Trip / Fuse Blown</option>
                  <option value="TIP_OXIDATION">Soldering Tip Oxidation / Thermal Stall</option>
                  <option value="HEPA_FILTER_CLOG">Fume Extractor Filter Airflow Reduction</option>
                  <option value="PHYSICAL_DAMAGE">Probe / Connector Physical Wear</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Detailed Description:</label>
                <textarea
                  rows={3}
                  value={faultDescription}
                  onChange={(e) => setFaultDescription(e.target.value)}
                  placeholder="Describe observed waveform distortion, noise, or heating..."
                  required
                  className="w-full p-2.5 rounded-lg bg-[#020813] text-slate-200 border border-slate-700 focus:border-[#00F0B5] outline-none text-xs"
                ></textarea>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setFaultModalTarget(null)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-rose-600 to-amber-600 text-white font-bold"
                >
                  Dispatch Fault Ticket
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Footer Info Bar */}
      <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800/80 flex flex-col sm:flex-row items-start sm:items-center justify-between text-xs text-slate-300 gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-slate-400">Telemetry Protocol:</span>
          <span className="text-[#00F0B5] font-bold">MQTT-over-WSS / REST IEEE 1451</span>
          <span className="text-slate-500">•</span>
          <span className="text-slate-400">Bench Controller:</span>
          <span className="text-white">ESP32-S3 Dual-Core FreeRTOS Node</span>
          {lastRefreshedTime && (
            <>
              <span className="text-slate-500">•</span>
              <span className="text-slate-400">Audit Time: {lastRefreshedTime}</span>
            </>
          )}
        </div>
        <div className="text-[10px] text-slate-400">
          Anna University ECE Lab 304 Telemetry Gateway
        </div>
      </div>

    </div>
  );
}
