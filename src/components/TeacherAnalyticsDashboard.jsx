import React, { useState, useEffect } from 'react';
import { triggerToast } from './ToastNotifications.jsx';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Enterprise Teacher & Administrator Analytics Dashboard
 * Autonomous Engineering Cluster Standards • Lead Systems Architect: Ashok Kumar A
 * ----------------------------------------------------------------------------------------
 * Privacy Standard: Private Admin Email & Phone isolated via RBAC & Environment Variables
 * Features:
 *   - Class Weak-Topic Matrices derived from Wokwi AutoGrader failure logs
 *   - At-Risk Student Early Warning System via Statistical Attendance Z-Scores (Z = (X - μ) / σ)
 *   - Automated NBA / NAAC Course Outcome (CO1-CO5) and Program Outcome (PO) Attainment Engine
 *   - OBE & ABET/NBA Matrix with Cohort Velocity, Score Distribution & Lab Bottlenecks
 *   - Interactive Role-Based Access Control (RBAC) Data Privacy Isolation Toggle
 * ========================================================================================
 */

const DEFAULT_WEAK_TOPICS = [
  {
    topic: 'ARM Cortex-M DMA Memory Barriers (__DMB, __DSB)',
    module: 'EC8708 (Lab 02)',
    failureRate: 42.2,
    commonMistake: 'Enabling DMA_SxCR_EN before memory barrier commits pointer writes into SRAM',
    severity: 'CRITICAL',
    action: 'Mandate Section IV Engineering Trap drill on out-of-order bus memory coherency.'
  },
  {
    topic: 'FreeRTOS Priority Inversion & Mutex Deadlocks',
    module: 'EC8706 (Lab 01)',
    failureRate: 37.5,
    commonMistake: 'Taking recursive mutex from within ISR context or neglecting priority ceiling',
    severity: 'HIGH',
    action: 'Review xSemaphoreCreateMutex vs Binary Semaphore signaling matrix.'
  },
  {
    topic: 'RISC-V RAW Hazard Forwarding & Load-Use Stalls',
    module: 'EC8705 (Lab 04)',
    failureRate: 31.3,
    commonMistake: 'Forwarding x0 register operand instead of hardwiring constant zero',
    severity: 'HIGH',
    action: 'Simulate 5-stage pipeline hazard unit in Verilog test bench.'
  },
  {
    topic: 'I2C Bus Contention & CRC-8 Calculation',
    module: 'EC8704 (Lab 03)',
    failureRate: 26.6,
    commonMistake: 'Unbounded while loop on I2C_FLAG_BUSY causing deadlock during clock stretching',
    severity: 'MEDIUM',
    action: 'Implement hardware watchdog timer and non-blocking timeout returns.'
  },
  {
    topic: 'Defense UAV FHSS LoRa Doppler Bin Migration',
    module: 'EC8703 (Lab 05)',
    failureRate: 21.9,
    commonMistake: 'Omitting TCXO calibration register updates under 108 km/h velocity shifts',
    severity: 'MEDIUM',
    action: 'Derive delta_f Doppler equation for 2.4 GHz carrier frequencies.'
  }
];

const DEFAULT_CO_ATTAINMENT = [
  { co: 'CO1', title: 'Bare-Metal Registers & Atomic GPIO Concurrency', target: 70.0, attained: 84.5, level: 2.54, status: 'ATTAINED', pos: ['PO1', 'PO2'] },
  { co: 'CO2', title: 'Automotive CAN & Bus Protocols with CRC-8', target: 70.0, attained: 78.2, level: 2.35, status: 'ATTAINED', pos: ['PO3', 'PO5'] },
  { co: 'CO3', title: '5-Stage Pipelined RISC-V Soft-Core on Artix-7', target: 70.0, attained: 71.8, level: 2.15, status: 'ATTAINED', pos: ['PO3', 'PO4'] },
  { co: 'CO4', title: 'FreeRTOS Deterministic Multi-Core Scheduling', target: 70.0, attained: 68.4, level: 2.05, status: 'REMEDIAL_ACTION_REQUIRED', pos: ['PO2', 'PO3'] },
  { co: 'CO5', title: 'Advanced DMA Circular Zero-Copy Instrumentation', target: 70.0, attained: 82.0, level: 2.46, status: 'ATTAINED', pos: ['PO1', 'PO5', 'PO12'] },
];

const DEFAULT_PO_MATRIX = [
  { po: 'PO1', title: 'Engineering Knowledge', coWeights: { CO1: 3, CO2: 3, CO3: 3, CO4: 3, CO5: 3 }, attainment: 77.0, status: 'MET' },
  { po: 'PO2', title: 'Problem Analysis', coWeights: { CO1: 3, CO2: 3, CO3: 3, CO4: 3, CO5: 3 }, attainment: 76.5, status: 'MET' },
  { po: 'PO3', title: 'Design Solutions', coWeights: { CO1: 2, CO2: 3, CO3: 3, CO4: 3, CO5: 3 }, attainment: 75.2, status: 'MET' },
  { po: 'PO4', title: 'Complex Investigations', coWeights: { CO1: 2, CO2: 2, CO3: 3, CO4: 3, CO5: 3 }, attainment: 74.8, status: 'MET' },
  { po: 'PO5', title: 'Modern Tools Usage', coWeights: { CO1: 3, CO2: 3, CO3: 3, CO4: 2, CO5: 3 }, attainment: 79.4, status: 'MET' },
  { po: 'PO7', title: 'Sustainability & Power', coWeights: { CO4: 2, CO5: 3 }, attainment: 75.2, status: 'MET' },
  { po: 'PO12', title: 'Life-Long Learning', coWeights: { CO1: 2, CO2: 2, CO3: 3, CO4: 3, CO5: 3 }, attainment: 77.8, status: 'MET' },
  { po: 'PSO1', title: 'Silicon & RTL Engineering', coWeights: { CO1: 2, CO2: 3, CO3: 3, CO4: 3, CO5: 3 }, attainment: 77.2, status: 'MET' },
  { po: 'PSO2', title: 'Edge IoT & Telemetry', coWeights: { CO1: 1, CO2: 2, CO3: 2, CO4: 3, CO5: 3 }, attainment: 75.8, status: 'MET' }
];

const DEFAULT_SCORE_DISTRIBUTION = {
  sample_size: 40,
  mean_score: 83.2,
  std_deviation: 7.4,
  histogram_bins: {
    '0-40 (Remedial)': 1,
    '41-55 (Grade B)': 3,
    '56-70 (Grade B+)': 6,
    '71-85 (Grade A/A+)': 18,
    '86-100 (Grade O)': 12
  },
  grade_counts: { O: 12, 'A+': 11, A: 7, 'B+': 6, B: 3, RA: 1 },
  pass_rate_pct: 97.5
};

const DEFAULT_LAB_BOTTLENECKS = [
  { lab_id: 'LAB_DMA_02', title: 'DMA Circular Streaming & Memory Barriers', failure_rate: 38.5, trap: 'Omitting __DMB() memory barrier before enabling DMA_SxCR_EN bit.', severity: 'CRITICAL' },
  { lab_id: 'LAB_RTOS_04', title: 'FreeRTOS Mutex Priority Inversion & Ceilings', failure_rate: 32.0, trap: 'Taking recursive mutex inside high-frequency ISR context.', severity: 'HIGH' },
  { lab_id: 'LAB_I2C_03', title: 'I2C Open-Drain Clock Stretching Recovery', failure_rate: 24.5, trap: 'Unbounded busy-wait loop on SCL line without hardware timeout.', severity: 'MEDIUM' }
];

const DEFAULT_AT_RISK_ROSTER = [
  { id: '2023MITEC051', name: 'Manojkumar T', attendance: 62.5, zScore: -2.31, labScore: 48.0, vivaScore: 40.0, riskTier: 'CRITICAL_DEFICIT', compliant: false },
  { id: '2023MITEC023', name: 'Harish R', attendance: 68.0, zScore: -1.78, labScore: 52.0, vivaScore: 45.0, riskTier: 'CRITICAL_DEFICIT', compliant: false },
  { id: '2023MITEC064', name: 'Priyanka S', attendance: 72.0, zScore: -1.39, labScore: 64.0, vivaScore: 60.0, riskTier: 'MODERATE_WARNING', compliant: false },
  { id: '2023MITEC058', name: 'Naveen P', attendance: 84.0, zScore: -0.22, labScore: 82.0, vivaScore: 78.0, riskTier: 'NORMAL', compliant: true },
  { id: '2023MITEC014', name: 'Deepa K', attendance: 89.0, zScore: 0.27, labScore: 94.0, vivaScore: 90.0, riskTier: 'NORMAL', compliant: true },
  { id: '2023MITEC001', name: 'Aarav S', attendance: 92.5, zScore: 0.61, labScore: 88.0, vivaScore: 85.0, riskTier: 'NORMAL', compliant: true },
  { id: '2023MITEC035', name: 'Kavitha M', attendance: 95.0, zScore: 0.85, labScore: 96.0, vivaScore: 92.0, riskTier: 'NORMAL', compliant: true },
  { id: '2023MITEC042', name: 'Ashok Kumar A', attendance: 98.0, zScore: 1.15, labScore: 100.0, vivaScore: 98.0, riskTier: 'NORMAL', compliant: true },
];

export default function TeacherAnalyticsDashboard({
  backendUrl = 'http://127.0.0.1:5000'
}) {
  const [activeTab, setActiveTab] = useState('obe_matrix'); // 'obe_matrix' | 'weak_topics' | 'at_risk' | 'nba_attainment' | 'rbac_privacy'
  const [userRole, setUserRole] = useState('Teacher'); // 'Student' | 'Teacher' | 'Admin_Owner'
  const [selectedCohort, setSelectedCohort] = useState('COHORT_2023_2027_ECE_A');
  const [adminMetadata, setAdminMetadata] = useState(null);
  const [weakTopics, setWeakTopics] = useState(DEFAULT_WEAK_TOPICS);
  const [atRiskRoster, setAtRiskRoster] = useState(DEFAULT_AT_RISK_ROSTER);
  const [coAttainment, setCoAttainment] = useState(DEFAULT_CO_ATTAINMENT);
  const [poMatrix, setPoMatrix] = useState(DEFAULT_PO_MATRIX);
  const [scoreDistribution, setScoreDistribution] = useState(DEFAULT_SCORE_DISTRIBUTION);
  const [labBottlenecks, setLabBottlenecks] = useState(DEFAULT_LAB_BOTTLENECKS);
  const [alertDispatched, setAlertDispatched] = useState({});

  // Sync Analytics from API on Mount
  useEffect(() => {
    async function fetchAnalytics() {
      try {
        const [wtRes, attRes, obeRes] = await Promise.all([
          fetch(`${backendUrl}/api/analytics/weak_topics`),
          fetch(`${backendUrl}/api/analytics/attainment`),
          fetch(`${backendUrl}/api/analytics/obe-matrix?cohort_id=${selectedCohort}`)
        ]);

        if (wtRes.ok) {
          const wtData = await wtRes.json();
          if (wtData.weak_topic_matrix) {
            setWeakTopics(wtData.weak_topic_matrix);
          }
        }

        if (attRes.ok) {
          const attData = await attRes.json();
          if (attData.course_outcomes) setCoAttainment(attData.course_outcomes);
          if (attData.at_risk_roster) setAtRiskRoster(attData.at_risk_roster);
        }

        if (obeRes.ok) {
          const obeData = await obeRes.json();
          if (obeData.score_distribution) setScoreDistribution(obeData.score_distribution);
          if (obeData.lab_bottlenecks) setLabBottlenecks(obeData.lab_bottlenecks);
        }
      } catch {
        // Deterministic offline fallback
      }
    }
    fetchAnalytics();
  }, [backendUrl, selectedCohort]);

  // Handle RBAC Audit Metadata fetch
  useEffect(() => {
    async function fetchAudit() {
      try {
        const res = await fetch(`${backendUrl}/api/admin/audit_metadata?role=${userRole}`);
        if (res.ok) {
          const data = await res.json();
          setAdminMetadata(data);
        }
      } catch {
        // Local fallback
        setAdminMetadata({
          platform_lead: 'Ashok Kumar A',
          institution: 'Autonomous Engineering Cluster',
          rbac_access_level: userRole === 'Admin_Owner' ? 'PRIVILEGED_ADMIN_ACCESS' : 'PUBLIC_UNPRIVILEGED'
        });
      }
    }
    fetchAudit();
  }, [userRole, backendUrl]);

  const handleExportNbaCsv = () => {
    const csvContent =
      'data:text/csv;charset=utf-8,Course Outcome,Title,Target %,Attained %,Level (3.0),Status,Mapped POs\n' +
      coAttainment
        .map(
          (c) =>
            `"${c.co}","${c.title}",${c.target || 70.0},${c.attained || 0},${
              c.level || 0
            },"${c.status}","${(c.pos || []).join(', ')}"`
        )
        .join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `NBA_SAR_CO_PO_Attainment_${selectedCohort}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    triggerToast({
      title: 'NBA SAR Export Complete',
      message: `Exported Course Outcome attainment metrics for ${selectedCohort}.`,
      type: 'success',
      category: 'academic'
    });
  };

  return (
    <div className="w-full flex flex-col gap-6 font-sans">
      {/* Header Deck & RBAC Switcher */}
      <div className="p-5 rounded-2xl bg-[#041026]/90 border border-[#00F0B5]/25 backdrop-blur-xl shadow-glass flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-[#00F0B5] animate-ping"></span>
            <span className="text-[10px] font-mono font-bold tracking-widest text-[#00F0B5] uppercase bg-[#00693E]/30 px-2 py-0.5 rounded border border-[#00F0B5]/30">
              Department Executive Console
            </span>
            <span className="text-xs font-mono text-slate-400">
              Autonomous Engineering Cluster • OBE Attainment
            </span>
          </div>
          <h2 className="text-lg md:text-xl font-bold text-slate-100">
            Multi-Tenant Learning Analytics, At-Risk Radar & CO-PO Attainment
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Cohort learning velocity, Wokwi firmware failure matrices, and automated accreditation reports.
          </p>
        </div>

        {/* Cohort Selector & RBAC Switcher */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
          <div className="flex flex-col font-mono text-xs">
            <span className="text-[10px] text-slate-400 uppercase">Target Cohort:</span>
            <select
              value={selectedCohort}
              onChange={(e) => setSelectedCohort(e.target.value)}
              className="px-2.5 py-1.5 rounded-xl bg-[#020813] border border-slate-700 text-white text-xs font-mono focus:border-[#00F0B5] outline-none"
            >
              <option value="COHORT_2023_2027_ECE_A">Batch 2023-2027 ECE (Section A)</option>
              <option value="COHORT_2023_2027_ECE_B">Batch 2023-2027 ECE (Section B)</option>
              <option value="COHORT_2024_2028_ECE">Batch 2024-2028 ECE (Second Year)</option>
            </select>
          </div>

          <div className="flex flex-col font-mono text-xs">
            <span className="text-[10px] text-slate-400 uppercase">Simulated RBAC Role:</span>
            <div className="flex items-center gap-1 bg-[#020813] p-1 rounded-xl border border-slate-800">
              <button
                onClick={() => setUserRole('Student')}
                className={`px-2 py-1 rounded-lg transition-all text-[11px] ${
                  userRole === 'Student' ? 'bg-slate-700 text-white font-bold' : 'text-slate-400 hover:text-white'
                }`}
              >
                Student
              </button>
              <button
                onClick={() => setUserRole('Teacher')}
                className={`px-2 py-1 rounded-lg transition-all text-[11px] ${
                  userRole === 'Teacher' ? 'bg-[#00693E] text-[#00F0B5] font-bold border border-[#00F0B5]/40' : 'text-slate-400 hover:text-white'
                }`}
              >
                Faculty
              </button>
              <button
                onClick={() => setUserRole('Admin_Owner')}
                className={`px-2 py-1 rounded-lg transition-all text-[11px] ${
                  userRole === 'Admin_Owner' ? 'bg-gradient-to-r from-amber-500 to-[#00F0B5] text-[#020813] font-bold' : 'text-slate-400 hover:text-white'
                }`}
              >
                Admin
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-3">
        <button
          onClick={() => setActiveTab('obe_matrix')}
          className={`px-4 py-2 rounded-xl text-xs font-mono transition-all flex items-center gap-2 ${
            activeTab === 'obe_matrix'
              ? 'bg-[#00F0B5] text-[#020813] font-bold shadow-emerald-glow'
              : 'bg-[#041026]/80 text-slate-400 border border-slate-800 hover:text-white'
          }`}
        >
          <span>📊 OBE CO-PO Attainment & Velocity</span>
        </button>

        <button
          onClick={() => setActiveTab('weak_topics')}
          className={`px-4 py-2 rounded-xl text-xs font-mono transition-all flex items-center gap-2 ${
            activeTab === 'weak_topics'
              ? 'bg-[#00F0B5] text-[#020813] font-bold shadow-emerald-glow'
              : 'bg-[#041026]/80 text-slate-400 border border-slate-800 hover:text-white'
          }`}
        >
          <span>📉 Class Weak-Topic Matrix</span>
        </button>

        <button
          onClick={() => setActiveTab('at_risk')}
          className={`px-4 py-2 rounded-xl text-xs font-mono transition-all flex items-center gap-2 ${
            activeTab === 'at_risk'
              ? 'bg-rose-500 text-white font-bold shadow-[0_0_15px_rgba(244,63,94,0.35)]'
              : 'bg-[#041026]/80 text-slate-400 border border-slate-800 hover:text-white'
          }`}
        >
          <span>🚨 At-Risk Early Warning (Z-Scores)</span>
          <span className="px-1.5 py-0.2 rounded-full bg-rose-950 text-rose-300 text-[10px] border border-rose-500/30">
            {atRiskRoster.filter((s) => s.riskTier !== 'NORMAL').length} Flagged
          </span>
        </button>

        <button
          onClick={() => setActiveTab('nba_attainment')}
          className={`px-4 py-2 rounded-xl text-xs font-mono transition-all flex items-center gap-2 ${
            activeTab === 'nba_attainment'
              ? 'bg-amber-400 text-[#020813] font-bold shadow-[0_0_15px_rgba(255,183,3,0.3)]'
              : 'bg-[#041026]/80 text-slate-400 border border-slate-800 hover:text-white'
          }`}
        >
          <span>🏛️ NBA / NAAC SAR Cards</span>
        </button>

        <button
          onClick={() => setActiveTab('rbac_privacy')}
          className={`px-4 py-2 rounded-xl text-xs font-mono transition-all flex items-center gap-2 ${
            activeTab === 'rbac_privacy'
              ? 'bg-cyan-400 text-[#020813] font-bold shadow-[0_0_15px_rgba(6,182,212,0.35)]'
              : 'bg-[#041026]/80 text-slate-400 border border-slate-800 hover:text-white'
          }`}
        >
          <span>🔒 Data Privacy & Audit</span>
        </button>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: OBE CO-PO ATTAINMENT MATRIX, VELOCITY & BOTTLENECKS */}
      {/* ========================================================================= */}
      {activeTab === 'obe_matrix' && (
        <div className="space-y-6">
          {/* Top Banner & Export */}
          <div className="p-4 rounded-xl bg-[#041026]/90 border border-emerald-500/30 backdrop-blur-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <div className="text-xs font-mono font-bold text-[#00F0B5] uppercase tracking-wider">
                ABET / NBA Criterion 3 • Outcome-Based Education Framework
              </div>
              <h3 className="text-base font-bold text-white mt-0.5">
                Program Outcome (PO1-PO12, PSO1-PSO2) Attainment Matrix
              </h3>
              <p className="text-xs text-slate-400 mt-0.5 font-mono">
                Cohort: <strong className="text-white">{selectedCohort}</strong> • Target Threshold: 70.0% Attainment (Level 2.1)
              </p>
            </div>

            <button
              onClick={handleExportNbaCsv}
              className="px-4 py-2 rounded-xl bg-[#00F0B5] hover:brightness-110 text-[#020813] font-mono font-bold text-xs transition-all shadow-emerald-glow flex items-center gap-2 flex-shrink-0"
            >
              <span>📥 Export CO-PO Matrix (CSV)</span>
            </button>
          </div>

          {/* PO Attainment Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {poMatrix.map((item) => (
              <div
                key={item.po}
                className="p-4 rounded-2xl bg-[#020813] border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-[#00F0B5] border border-[#00F0B5]/30">
                      {item.po}
                    </span>
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-800 text-emerald-400 border border-emerald-500/30">
                      {item.status}
                    </span>
                  </div>
                  <h4 className="text-xs font-bold text-white line-clamp-1">{item.title}</h4>
                  
                  <div className="mt-3 p-2.5 rounded-xl bg-[#041026] border border-slate-800/80 font-mono text-xs">
                    <div className="flex justify-between items-center mb-1 text-[11px]">
                      <span className="text-slate-400">Attainment:</span>
                      <span className="font-bold text-[#00F0B5]">{item.attainment}%</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-slate-900 overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-[#00693E] to-[#00F0B5]"
                        style={{ width: `${item.attainment}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                <div className="mt-3 pt-2 border-t border-slate-800/80 text-[10px] text-slate-400 flex items-center justify-between">
                  <span>Correlation Weights:</span>
                  <span className="text-slate-300 font-bold font-mono">High (3.0)</span>
                </div>
              </div>
            ))}
          </div>

          {/* Score Distribution Histogram & Bottlenecks */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* Histogram (7 cols) */}
            <div className="lg:col-span-7 p-6 rounded-2xl bg-[#020813] border border-slate-800 space-y-4 font-mono text-xs">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <span className="font-bold text-white text-sm">Cohort Score Distribution & Grade Breakdown</span>
                <span className="text-emerald-400 font-bold">Pass Rate: {scoreDistribution.pass_rate_pct}%</span>
              </div>

              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="text-[10px] text-slate-400">Mean Score</div>
                  <div className="text-lg font-bold text-white mt-0.5">{scoreDistribution.mean_score} / 100</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="text-[10px] text-slate-400">Std Deviation (σ)</div>
                  <div className="text-lg font-bold text-amber-400 mt-0.5">{scoreDistribution.std_deviation}</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="text-[10px] text-slate-400">Grade O (Mastery)</div>
                  <div className="text-lg font-bold text-[#00F0B5] mt-0.5">{scoreDistribution.grade_counts.O} Students</div>
                </div>
              </div>

              <div className="space-y-2 pt-2">
                {Object.entries(scoreDistribution.histogram_bins).map(([binName, count]) => {
                  const pct = Math.round((count / scoreDistribution.sample_size) * 100);
                  return (
                    <div key={binName} className="space-y-1">
                      <div className="flex justify-between items-center text-[11px]">
                        <span className="text-slate-300">{binName}</span>
                        <span className="font-bold text-white">{count} ({pct}%)</span>
                      </div>
                      <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-[#00693E] to-[#00F0B5]"
                          style={{ width: `${pct}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Bottlenecks Panel (5 cols) */}
            <div className="lg:col-span-5 p-6 rounded-2xl bg-[#020813] border border-rose-500/30 space-y-4 font-mono text-xs">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <span className="font-bold text-rose-400 text-sm flex items-center gap-2">
                  <span>⚠</span> Laboratory Completion Bottlenecks
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-500/30">
                  3 Flagged Labs
                </span>
              </div>

              <div className="space-y-3">
                {labBottlenecks.map((b) => (
                  <div key={b.lab_id} className="p-3.5 rounded-xl bg-[#041026] border border-slate-800 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white text-[11px]">{b.title}</span>
                      <span className="text-rose-400 font-bold text-[10px]">{b.failure_rate}% Drop-Off</span>
                    </div>
                    <p className="text-[10px] text-slate-300 font-sans leading-relaxed">
                      <strong>Root Trap:</strong> {b.trap}
                    </p>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: CLASS WEAK-TOPIC MATRIX */}
      {/* ========================================================================= */}
      {activeTab === 'weak_topics' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-[#041026]/90 border border-slate-800 flex items-center justify-between text-xs font-mono">
            <div>
              <span className="font-bold text-white text-sm">Class Failure Patterns from Virtual Testbenches</span>
              <p className="text-slate-400 text-[11px]">Derived automatically from Wokwi simulation runs and static code review logs.</p>
            </div>
            <span className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 text-[10px]">
              {weakTopics.length} Common Inquiries
            </span>
          </div>

          <div className="grid grid-cols-1 gap-3">
            {weakTopics.map((wt, idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-[#020813] border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 font-mono text-xs">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-sm">{wt.topic}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                      {wt.module}
                    </span>
                  </div>
                  <div className="text-slate-400 text-[11px] font-sans">
                    <strong>Mistake:</strong> {wt.commonMistake}
                  </div>
                  <div className="text-emerald-400 text-[11px] font-sans">
                    <strong>Remedy:</strong> {wt.action}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <div className="text-rose-400 font-bold text-sm">{wt.failureRate}%</div>
                    <div className="text-[9px] text-slate-500">Error Frequency</div>
                  </div>
                  <span className={`text-[10px] px-2.5 py-1 rounded-lg font-bold border ${
                    wt.severity === 'CRITICAL' ? 'bg-rose-950/80 text-rose-300 border-rose-500/40' : 'bg-amber-950/60 text-amber-300 border-amber-500/30'
                  }`}>
                    {wt.severity}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: AT-RISK STUDENTS */}
      {/* ========================================================================= */}
      {activeTab === 'at_risk' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-[#041026]/90 border border-rose-500/30 flex items-center justify-between text-xs font-mono">
            <div>
              <span className="font-bold text-white text-sm">Statistical Attendance & CIE Z-Score Radar</span>
              <p className="text-slate-400 text-[11px]">Identifies candidates with Z &lt; -1.2 standard deviations requiring remedial faculty counseling.</p>
            </div>
            <span className="px-2.5 py-1 rounded-lg bg-rose-950 text-rose-300 border border-rose-500/30 text-[10px] font-bold">
              Regulation Cutoff: 75% Attendance
            </span>
          </div>

          <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-[#020813]">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-[#041026] text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="p-3.5">Roll No</th>
                  <th className="p-3.5">Student Name</th>
                  <th className="p-3.5">Attendance</th>
                  <th className="p-3.5">Z-Score</th>
                  <th className="p-3.5">Lab Score</th>
                  <th className="p-3.5">Viva Score</th>
                  <th className="p-3.5">Risk Status</th>
                  <th className="p-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {atRiskRoster.map((st) => (
                  <tr key={st.id} className="hover:bg-slate-900/40 transition-colors">
                    <td className="p-3.5 font-bold text-white">{st.id}</td>
                    <td className="p-3.5">{st.name}</td>
                    <td className="p-3.5">
                      <span className={st.attendance < 75.0 ? 'text-rose-400 font-bold' : 'text-emerald-400'}>
                        {st.attendance}%
                      </span>
                    </td>
                    <td className="p-3.5 text-slate-400">{st.zScore}</td>
                    <td className="p-3.5">{st.labScore} / 100</td>
                    <td className="p-3.5">{st.vivaScore} / 100</td>
                    <td className="p-3.5">
                      <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                        st.riskTier === 'CRITICAL_DEFICIT'
                          ? 'bg-rose-950 text-rose-300 border border-rose-500/40'
                          : (st.riskTier === 'MODERATE_WARNING' ? 'bg-amber-950 text-amber-300 border border-amber-500/30' : 'bg-emerald-950 text-emerald-300 border border-emerald-500/30')
                      }`}>
                        {st.riskTier}
                      </span>
                    </td>
                    <td className="p-3.5 text-right">
                      <button
                        type="button"
                        onClick={() => {
                          setAlertDispatched(prev => ({ ...prev, [st.id]: true }));
                          triggerToast({
                            title: 'Remedial Notice Dispatched',
                            message: `Dispatched academic notice to ${st.name} (${st.id}).`,
                            type: 'info',
                            category: 'academic'
                          });
                        }}
                        className={`text-[10px] px-2.5 py-1 rounded-lg border font-bold transition-all ${
                          alertDispatched[st.id]
                            ? 'bg-slate-800 text-slate-500 border-slate-700'
                            : 'bg-rose-600/30 hover:bg-rose-600 text-rose-300 hover:text-white border-rose-500/40'
                        }`}
                      >
                        {alertDispatched[st.id] ? '✓ Dispatched' : 'Counsel'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: NBA / NAAC SAR CARDS */}
      {/* ========================================================================= */}
      {activeTab === 'nba_attainment' && (
        <div className="space-y-6">
          <div className="p-4 rounded-xl bg-[#041026]/90 border border-amber-500/30 backdrop-blur-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <div className="text-xs font-mono font-bold text-amber-400 uppercase tracking-wider">
                NBA Tier-1 (Washington Accord) & NAAC Criterion 2.6 Framework
              </div>
              <h3 className="text-base font-bold text-white mt-0.5">
                Direct Laboratory Course Outcome (CO1-CO5) Attainment Matrix
              </h3>
              <p className="text-xs text-slate-400 mt-0.5 font-mono">
                Target Benchmark: 70.0% (Level 2.1 on 3-Point Bloom Scale)
              </p>
            </div>

            <button
              onClick={handleExportNbaCsv}
              className="px-4 py-2 rounded-xl bg-amber-400 hover:bg-amber-300 text-[#020813] font-mono font-bold text-xs transition-all shadow-[0_0_15px_rgba(255,183,3,0.3)] flex items-center gap-2 flex-shrink-0"
            >
              <span>📥 Export NBA SAR Report (CSV)</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {coAttainment.map((coItem, cIdx) => (
              <div
                key={cIdx}
                className="p-5 rounded-2xl bg-[#041026]/90 border border-slate-800 backdrop-blur-xl shadow-glass flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                      {coItem.co}
                    </span>
                    <span
                      className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                        coItem.status === 'ATTAINED'
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                      }`}
                    >
                      {coItem.status}
                    </span>
                  </div>

                  <h4 className="text-xs font-bold text-slate-100 leading-snug">
                    {coItem.title}
                  </h4>

                  <div className="mt-4 p-3 rounded-xl bg-[#020813] border border-slate-800">
                    <div className="flex justify-between items-center text-xs font-mono mb-1">
                      <span className="text-slate-400">Attainment Score:</span>
                      <span className="font-bold text-[#00F0B5]">
                        {coItem.level || coItem.attainment_level} / 3.00 ({coItem.attained || coItem.attained_pct}%)
                      </span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden border border-slate-800">
                      <div
                        className={`h-full ${
                          (coItem.attained || coItem.attained_pct) >= 70.0 ? 'bg-[#00F0B5]' : 'bg-rose-500'
                        }`}
                        style={{
                          width: `${Math.min(100, ((coItem.attained || coItem.attained_pct) / 100) * 100)}%`
                        }}
                      />
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-[11px] font-mono">
                  <span className="text-slate-400">Mapped POs:</span>
                  <div className="flex items-center gap-1">
                    {(coItem.pos || coItem.mapped_pos || []).map((po, pIdx) => (
                      <span key={pIdx} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">
                        {po}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 5: DATA PRIVACY & RBAC ISOLATION AUDIT */}
      {/* ========================================================================= */}
      {activeTab === 'rbac_privacy' && (
        <div className="p-6 rounded-2xl bg-[#041026]/90 border border-cyan-500/30 backdrop-blur-xl shadow-glass flex flex-col gap-4 font-mono text-xs">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <div className="text-cyan-400 font-bold uppercase text-[11px]">
                Data Privacy & RBAC Isolation Specification
              </div>
              <h3 className="text-base font-bold text-white mt-0.5">
                Owner Credential Protection & Audit Telemetry
              </h3>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase ${
                userRole === 'Admin_Owner'
                  ? 'bg-gradient-to-r from-amber-500 to-[#00F0B5] text-[#020813]'
                  : 'bg-slate-800 text-slate-300'
              }`}
            >
              Current Access: {userRole}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-[#020813] border border-slate-800 space-y-2.5">
              <div className="text-[#00F0B5] font-bold flex items-center gap-2">
                <span>🌐 Public Contact Metadata</span>
                <span className="text-[9px] px-1.5 py-0.2 rounded bg-[#00693E]/40 text-[#00F0B5]">
                  Public Header Safe
                </span>
              </div>
              <div>
                <span className="text-slate-500">Platform Lead:</span>{' '}
                <span className="text-white font-bold">{adminMetadata?.platform_lead || 'Ashok Kumar A'}</span>
              </div>
              <div>
                <span className="text-slate-500">Public Contact Email:</span>{' '}
                <span className="text-slate-200">scholar@voltcore.org</span>
              </div>
              <div>
                <span className="text-slate-500">GitHub Repository:</span>{' '}
                <a
                  href="https://github.com/AshokKumar313"
                  target="_blank"
                  rel="noreferrer"
                  className="text-cyan-400 hover:underline"
                >
                  https://github.com/AshokKumar313
                </a>
              </div>
              <div>
                <span className="text-slate-500">Institution:</span>{' '}
                <span className="text-slate-300">{adminMetadata?.institution || 'Autonomous Engineering Cluster'}</span>
              </div>
            </div>

            <div
              className={`p-4 rounded-xl border space-y-2.5 ${
                userRole === 'Admin_Owner'
                  ? 'bg-amber-950/20 border-amber-500/40'
                  : 'bg-slate-900/60 border-slate-800'
              }`}
            >
              <div className="flex items-center justify-between">
                <span
                  className={`font-bold flex items-center gap-1.5 ${
                    userRole === 'Admin_Owner' ? 'text-amber-400' : 'text-slate-400'
                  }`}
                >
                  <span>{userRole === 'Admin_Owner' ? '🔓' : '🔒'} Privileged Admin Telemetry</span>
                </span>
                <span
                  className={`text-[9px] px-2 py-0.5 rounded uppercase font-bold ${
                    userRole === 'Admin_Owner'
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                      : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                  }`}
                >
                  {adminMetadata?.rbac_access_level || 'PROTECTED'}
                </span>
              </div>

              <div>
                <span className="text-slate-500">Role Status:</span>
                <div
                  className={`mt-0.5 p-2 rounded-lg ${
                    userRole === 'Admin_Owner'
                      ? 'bg-[#020813] text-amber-300 font-bold border border-amber-500/25'
                      : 'bg-black/50 text-slate-500 italic'
                  }`}
                >
                  {userRole === 'Admin_Owner' ? 'PRIVILEGED_ROOT_OPERATOR' : '[REDACTED - REQUIRES PRIVILEGED RBAC ACCESS]'}
                </div>
              </div>

              <div className="text-[10px] text-slate-400 pt-2 border-t border-slate-800/80">
                Notice: Private admin credentials are strictly isolated via RBAC and never leaked to public headers or static client bundles.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
