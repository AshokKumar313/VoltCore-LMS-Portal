import React, { useState, useEffect } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Engineering Project & Innovation Center (Phase 24)
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * Course Code: EC3711 - Mini Project / Comprehensive Practical (Regulation 2023)
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A (2023MITEC042)
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 * ========================================================================================
 */

// Default curated ideas fallback
const FALLBACK_IDEAS = [
  {
    idea_id: "IDEA_LORA_AGRI_NODE",
    title: "LoRaWAN Agricultural Soil & Microclimate Node",
    domain: "IoT & Smart Systems",
    difficulty: "Intermediate",
    curriculum_mapping: "EC3501 Wireless Communication & Networks",
    description: "Ultra-low-power edge sensory node measuring volumetric soil moisture, temperature, and atmospheric pressure with deep-sleep telemetry over 5km LoRa links.",
    suggested_mcu: "ESP32-WROOM-32",
    hardware_stack: ["ESP32-WROOM-32", "SX1278 LoRa Module", "BME280 Sensor", "Capacitive Soil Moisture Sensor", "TP4056 Solar Charger"],
    software_stack: ["FreeRTOS", "RadioHead / LMIC Library", "InfluxDB", "Grafana"],
    estimated_budget_inr: 2450.0,
    tags: ["IoT", "LoRaWAN", "Agriculture", "LowPower", "SmartSensing"]
  },
  {
    idea_id: "IDEA_QUADCOPTER_RTOS",
    title: "Deterministic Quadcopter Flight Controller on FreeRTOS",
    domain: "Embedded RTOS & Robotics",
    difficulty: "Advanced",
    curriculum_mapping: "EC3601 Embedded Systems & RTOS",
    description: "Sub-millisecond cascaded PID attitude control loop running as high-priority real-time tasks with Kalman filtering for fused IMU/Barometer telemetry.",
    suggested_mcu: "STM32F401CCU6 (BlackPill)",
    hardware_stack: ["STM32F401CCU6", "MPU6050 6-DOF IMU", "BMP280 Barometer", "4x 20A ESC", "2204 Brushless Motors"],
    software_stack: ["FreeRTOS Kernel", "CMSIS-DSP", "DMA SPI/I2C Drivers", "PID Tuning GUI"],
    estimated_budget_inr: 6200.0,
    tags: ["RTOS", "FlightControl", "Robotics", "KalmanFilter", "STM32"]
  },
  {
    idea_id: "IDEA_TINYML_VIBRATION",
    title: "TinyML Vibration Anomaly Detector for Industrial Motors",
    domain: "Edge AI & Signal Processing",
    difficulty: "Intermediate",
    curriculum_mapping: "EC3701 TinyML & Intelligent Edge Systems",
    description: "On-device accelerometer FFT spectral feature extraction and quantized neural network (INT8) inferencing to predict bearing wear and rotor imbalances.",
    suggested_mcu: "Raspberry Pi Pico (RP2040)",
    hardware_stack: ["Raspberry Pi Pico", "ADXL345 Accelerometer", "SSD1306 OLED Display", "Active Buzzer"],
    software_stack: ["TensorFlow Lite for Microcontrollers", "Edge Impulse C++ SDK", "Python SciPy"],
    estimated_budget_inr: 1850.0,
    tags: ["TinyML", "EdgeAI", "PredictiveMaintenance", "Vibration", "SignalProcessing"]
  },
  {
    idea_id: "IDEA_RISCV_PIPELINED_CORE",
    title: "FPGA Pipelined 32-bit RISC-V (RV32I) Soft-Core Processor",
    domain: "VLSI & Digital Systems",
    difficulty: "Advanced",
    curriculum_mapping: "EC3352 Digital Systems Design & Computer Architecture",
    description: "5-stage classical pipelined RISC-V RV32I core with hazard resolution, forwarding units, Harvard cache architecture, and custom peripheral memory mapping.",
    suggested_mcu: "Xilinx Spartan-7 / Artix-7 FPGA",
    hardware_stack: ["Xilinx Spartan-7 FPGA Board", "UART-to-USB Bridge", "7-Segment Displays", "Tactile Switches"],
    software_stack: ["Verilog HDL", "Xilinx Vivado", "GNU RISC-V Toolchain", "GTKWave"],
    estimated_budget_inr: 7500.0,
    tags: ["VLSI", "RISC-V", "Verilog", "FPGA", "ComputerArchitecture"]
  },
  {
    idea_id: "IDEA_PPG_HEALTH_MONITOR",
    title: "Non-Invasive Wearable PPG Heart Rate & SpO2 Monitor",
    domain: "Biomedical Electronics",
    difficulty: "Beginner",
    curriculum_mapping: "EC3451 Linear Integrated Circuits & Biomedical Instrumentation",
    description: "Optical sensor photoplethysmography circuit with active bandpass analog front-end (0.5 - 4 Hz) and digital peak-detection algorithm for cardiac rhythm tracking.",
    suggested_mcu: "Arduino Nano 33 BLE",
    hardware_stack: ["Arduino Nano 33 BLE", "MAX30102 Pulse Oximeter", "0.96 inch I2C OLED", "LiPo 3.7V Battery"],
    software_stack: ["Arduino C++", "BLE HID Service", "Butterworth Filter Lib"],
    estimated_budget_inr: 2100.0,
    tags: ["Biomedical", "PPG", "Wearables", "SpO2", "Healthcare"]
  },
  {
    idea_id: "IDEA_AUTONOMOUS_ROVER_SLAM",
    title: "Autonomous Ground Rover with Ultrasonic LiDAR SLAM",
    domain: "Robotics & Automation",
    difficulty: "Intermediate",
    curriculum_mapping: "EC3601 Embedded Systems & Microcontrollers",
    description: "Differential-drive autonomous robotic platform combining Time-of-Flight (ToF) laser ranging with ultrasonic collision avoidance and obstacle mapping.",
    suggested_mcu: "ESP32-WROOM-32",
    hardware_stack: ["ESP32-WROOM-32", "VL53L0X ToF Laser Sensor", "2x HC-SR04 Ultrasonic", "L298N Motor Driver", "2x TT Gear Motors"],
    software_stack: ["ESP-IDF / Arduino", "Micro-ROS", "Occupancy Grid Mapping"],
    estimated_budget_inr: 3400.0,
    tags: ["Robotics", "SLAM", "Autonomous", "ObstacleAvoidance", "Sensors"]
  }
];

// Fallback MCU Database
const MCU_OPTIONS = [
  { name: "ESP32-WROOM-32", voltage: 3.3, max_ma: 600.0, tol5v: false, ports: "2x I2C, 3x SPI, 3x UART" },
  { name: "STM32F401CCU6 (BlackPill)", voltage: 3.3, max_ma: 400.0, tol5v: true, ports: "3x I2C, 4x SPI, 3x UART" },
  { name: "Arduino Uno R3 (ATmega328P)", voltage: 5.0, max_ma: 800.0, tol5v: true, ports: "1x I2C, 1x SPI, 1x UART" },
  { name: "Raspberry Pi Pico (RP2040)", voltage: 3.3, max_ma: 300.0, tol5v: false, ports: "2x I2C, 2x SPI, 2x UART" },
  { name: "Arduino Nano 33 BLE (nRF52840)", voltage: 3.3, max_ma: 200.0, tol5v: false, ports: "1x I2C, 1x SPI, 1x UART" }
];

// Fallback Quick Component Catalog
const PRESET_COMPONENTS = [
  { name: "BME280 Barometric/Humidity/Temp Sensor", voltage: 3.3, current_ma: 3.6, iface: "I2C", addr: "0x76", price: 380, cat: "SENSOR" },
  { name: "MPU6050 6-DOF IMU Accelerometer", voltage: 3.3, current_ma: 3.9, iface: "I2C", addr: "0x68", price: 190, cat: "SENSOR" },
  { name: "HC-SR04 Ultrasonic Distance Sensor", voltage: 5.0, current_ma: 15.0, iface: "GPIO_PULSE", price: 120, cat: "SENSOR" },
  { name: "SX1278 433MHz LoRa Transceiver", voltage: 3.3, current_ma: 120.0, iface: "SPI", price: 550, cat: "COMMUNICATION" },
  { name: "SIM800L Cellular GSM/GPRS Module", voltage: 4.0, current_ma: 2000.0, iface: "UART", price: 650, cat: "COMMUNICATION" },
  { name: "SSD1306 0.96 inch 128x64 OLED Display", voltage: 3.3, current_ma: 22.0, iface: "I2C", addr: "0x3C", price: 280, cat: "DISPLAY" },
  { name: "SG90 9g Micro Servo Motor", voltage: 5.0, current_ma: 500.0, iface: "PWM", price: 140, cat: "ACTUATOR" },
  { name: "MAX30102 Pulse Oximeter & Heart Rate", voltage: 3.3, current_ma: 2.5, iface: "I2C", addr: "0x57", price: 320, cat: "SENSOR" },
  { name: "VL53L0X Time-of-Flight Laser Sensor", voltage: 3.3, current_ma: 19.0, iface: "I2C", addr: "0x29", price: 450, cat: "SENSOR" },
  { name: "ADXL345 3-Axis Digital Accelerometer", voltage: 3.3, current_ma: 0.14, iface: "I2C", addr: "0x53", price: 210, cat: "SENSOR" }
];

export default function ProjectInnovationHub() {
  const [activeTab, setActiveTab] = useState('proposals'); // 'proposals', 'bom', 'compatibility', 'milestones', 'ideas'
  const [studentId, setStudentId] = useState('2023MITEC042');
  const [overview, setOverview] = useState(null);
  const [ideas, setIdeas] = useState(FALLBACK_IDEAS);
  const [selectedDomain, setSelectedDomain] = useState('ALL');
  const [proposals, setProposals] = useState([]);
  const [selectedProposalId, setSelectedProposalId] = useState('PROP_2023MITEC042_01');
  const [notification, setNotification] = useState(null);

  // Proposal Form State
  const [proposalForm, setProposalForm] = useState({
    title: '',
    domain: 'IoT & Smart Systems',
    abstract: '',
    objectives: ['Establish low-power baseline current < 50 uA in deep sleep.', 'Validate sensory packet CRC transmission over 3 km radius.'],
    hardware_stack: ['ESP32-WROOM-32', 'SX1278 LoRa Module', 'BME280 Sensor'],
    software_stack: ['FreeRTOS Kernel', 'RadioHead Driver', 'InfluxDB'],
    mentor_name: 'Dr. P. Nirmal Kumar (Professor & Head, Dept of Electronics)'
  });

  // BOM Estimator State
  const [bomItems, setBomItems] = useState([
    { id: '1', component_name: 'ESP32-WROOM-32 DevKit', category: 'MCU', quantity: 1, unit_price_inr: 350.0, vendor: 'Robu.in' },
    { id: '2', component_name: 'SX1278 433MHz LoRa Module', category: 'COMMUNICATION', quantity: 1, unit_price_inr: 550.0, vendor: 'Robocraze' },
    { id: '3', component_name: 'BME280 Pressure/Temp Sensor', category: 'SENSOR', quantity: 1, unit_price_inr: 380.0, vendor: 'ElectronicsComp' },
    { id: '4', component_name: 'Capacitive Soil Moisture Sensor', category: 'SENSOR', quantity: 2, unit_price_inr: 85.0, vendor: 'Robu.in' },
    { id: '5', component_name: 'TP4056 1A Li-Ion Solar Charger', category: 'POWER', quantity: 1, unit_price_inr: 45.0, vendor: 'Robu.in' },
    { id: '6', component_name: '3.7V 2500mAh 18650 Li-ion Cell', category: 'POWER', quantity: 1, unit_price_inr: 240.0, vendor: 'Bakoma Batteries' }
  ]);
  const [taxRate, setTaxRate] = useState(18.0);
  const [contingencyRate, setContingencyRate] = useState(10.0);
  const [newItemName, setNewItemName] = useState('');
  const [newItemCat, setNewItemCat] = useState('SENSOR');
  const [newItemQty, setNewItemQty] = useState(1);
  const [newItemPrice, setNewItemPrice] = useState(150);
  const [newItemVendor, setNewItemVendor] = useState('Robu.in');

  // Compatibility Checker State
  const [selectedMcu, setSelectedMcu] = useState('ESP32-WROOM-32');
  const [activeComponents, setActiveComponents] = useState([
    PRESET_COMPONENTS[0], // BME280
    PRESET_COMPONENTS[1], // MPU6050
    PRESET_COMPONENTS[3]  // SX1278
  ]);
  const [compatResult, setCompatResult] = useState(null);

  // Milestones State
  const [milestones, setMilestones] = useState([
    { milestone_id: 'MS_01', title: 'Literature Survey & Architecture Design', weightage_percent: 20, due_date: '2026-11-15', status: 'COMPLETED', deliverables: ['Survey report', 'System block diagram'] },
    { milestone_id: 'MS_02', title: 'Hardware Prototyping & Sensor Validation', weightage_percent: 25, due_date: '2026-11-30', status: 'COMPLETED', deliverables: ['Oscilloscope probe captures', 'I2C signal decode'] },
    { milestone_id: 'MS_03', title: 'Firmware Development & LoRa Integration', weightage_percent: 30, due_date: '2026-12-15', status: 'IN_PROGRESS', deliverables: ['FreeRTOS tasks firmware', 'LoRa packet verification'] },
    { milestone_id: 'MS_04', title: 'Field Deployment & Final Viva Voce', weightage_percent: 25, due_date: '2027-01-10', status: 'PENDING', deliverables: ['Thesis report PDF', 'Live MIT demonstration'] }
  ]);
  const [newMsTitle, setNewMsTitle] = useState('');
  const [newMsWeight, setNewMsWeight] = useState(20);
  const [newMsDate, setNewMsDate] = useState('2026-12-31');

  const showToast = (msg, type = 'info') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  };

  // Fetch initial overview and proposals
  useEffect(() => {
    fetchOverview();
    fetchProposals();
    fetchIdeas();
  }, [studentId]);

  // Recalculate compatibility whenever MCU or components change
  useEffect(() => {
    evaluateCompatibility();
  }, [selectedMcu, activeComponents]);

  const fetchOverview = async () => {
    try {
      const res = await fetch(`/api/projects/overview?student_id=${studentId}`);
      if (res.ok) {
        const data = await res.json();
        setOverview(data);
      }
    } catch {
      // Local fallback metrics
      setOverview({
        metrics: {
          total_proposals: 1,
          approved_proposals: 1,
          total_milestones: milestones.length,
          completed_milestones: milestones.filter(m => m.status === 'COMPLETED').length,
          in_progress_milestones: milestones.filter(m => m.status === 'IN_PROGRESS').length,
          overall_progress_percent: 50.0,
          total_bom_expenditure_inr: 1735.0,
          curated_ideas_count: 6
        }
      });
    }
  };

  const fetchProposals = async () => {
    try {
      const res = await fetch(`/api/projects/proposals?student_id=${studentId}`);
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          setProposals(data);
          setSelectedProposalId(data[0].proposal_id);
        }
      }
    } catch {
      // fallback
      setProposals([
        {
          proposal_id: 'PROP_2023MITEC042_01',
          title: 'Autonomous IoT Edge Microclimate & Crop Disease Monitoring Node',
          domain: 'IoT & Smart Systems',
          mentor_name: 'Dr. P. Nirmal Kumar (MIT Campus)',
          status: 'APPROVED',
          progress_percent: 50.0,
          bom_items_count: 6,
          bom_subtotal_inr: 1735.0,
          created_at: Date.now() / 1000
        }
      ]);
    }
  };

  const fetchIdeas = async () => {
    try {
      const res = await fetch('/api/projects/ideas');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          setIdeas(data);
        }
      }
    } catch {
      setIdeas(FALLBACK_IDEAS);
    }
  };

  // Evaluate Hardware Compatibility
  const evaluateCompatibility = async () => {
    try {
      const res = await fetch('/api/projects/check_compatibility', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mcu_name: selectedMcu,
          components: activeComponents.map(c => ({
            name: c.name,
            logic_voltage: c.voltage,
            current_ma: c.current_ma,
            interface: c.iface,
            i2c_address: c.addr
          }))
        })
      });
      if (res.ok) {
        const data = await res.json();
        setCompatResult(data);
        return;
      }
    } catch {
      // Offline local evaluation fallback
    }

    // Local evaluation
    const mcu = MCU_OPTIONS.find(m => m.name === selectedMcu) || MCU_OPTIONS[0];
    const totalCurrent = activeComponents.reduce((acc, c) => acc + (c.current_ma || 0), 0);
    const headroom = Math.round((mcu.max_ma - totalCurrent) * 100) / 100;
    const headroomPct = Math.max(0, Math.round((headroom / mcu.max_ma) * 100));

    const errors = [];
    const caveats = [];
    const passed = [];

    activeComponents.forEach(c => {
      if (mcu.voltage === 3.3 && c.voltage > 3.6) {
        if (mcu.tol5v) {
          caveats.push(`5V-Tolerant Caveat: '${c.name}' operates at ${c.voltage}V. MCU supports 5V pins, but level shifter is recommended for noise immunity.`);
        } else {
          errors.push(`CRITICAL VOLTAGE HAZARD: '${c.name}' (${c.voltage}V) connects to 3.3V non-tolerant ${mcu.name}. Level shifter required!`);
        }
      } else if (mcu.voltage === 5.0 && c.voltage < 4.0) {
        errors.push(`CRITICAL VOLTAGE HAZARD: ${mcu.name} drives 5.0V into strict ${c.voltage}V '${c.name}'. Component will be damaged!`);
      } else {
        passed.push(`Logic Voltage: '${c.name}' (${c.voltage}V) matches ${mcu.name} (${mcu.voltage}V).`);
      }
    });

    if (totalCurrent > mcu.max_ma) {
      errors.push(`POWER OVERLOAD: Total current (${totalCurrent} mA) exceeds on-board regulator (${mcu.max_ma} mA). Add external supply!`);
    } else if (headroomPct < 15) {
      caveats.push(`Tight Headroom: Total draw (${totalCurrent} mA) consumes ${100 - headroomPct}% of regulator capacity.`);
    } else {
      passed.push(`Power Budget Healthy: Total load ${totalCurrent} mA has ${headroomPct}% safety headroom.`);
    }

    const verdict = errors.length > 0 ? 'INCOMPATIBLE' : (caveats.length > 0 ? 'COMPATIBLE_WITH_CAVEATS' : 'COMPATIBLE');

    setCompatResult({
      verdict,
      power_budget: {
        total_current_ma: Math.round(totalCurrent * 10) / 10,
        regulator_max_ma: mcu.max_ma,
        headroom_ma: headroom,
        headroom_percent: headroomPct
      },
      critical_errors: errors,
      caveats,
      passed_checks: passed
    });
  };

  // Add Component to Compatibility Test Bench
  const addComponentToBench = (comp) => {
    if (activeComponents.some(c => c.name === comp.name)) {
      showToast(`'${comp.name}' is already on the bench.`, 'warning');
      return;
    }
    setActiveComponents([...activeComponents, comp]);
    showToast(`Added '${comp.name}' to compatibility test bench.`, 'success');
  };

  const removeComponentFromBench = (name) => {
    setActiveComponents(activeComponents.filter(c => c.name !== name));
  };

  // BOM Management
  const addBomItem = () => {
    if (!newItemName.trim()) {
      showToast('Please enter a component name.', 'error');
      return;
    }
    const item = {
      id: Date.now().toString(),
      component_name: newItemName.trim(),
      category: newItemCat,
      quantity: Math.max(1, parseInt(newItemQty) || 1),
      unit_price_inr: Math.max(0, parseFloat(newItemPrice) || 0),
      vendor: newItemVendor.trim() || 'Local Distributor'
    };
    setBomItems([...bomItems, item]);
    setNewItemName('');
    showToast(`Added '${item.component_name}' to BOM.`, 'success');
  };

  const removeBomItem = (id) => {
    setBomItems(bomItems.filter(b => b.id !== id));
  };

  // BOM Calculations
  const bomSubtotal = bomItems.reduce((acc, it) => acc + (it.quantity * it.unit_price_inr), 0);
  const bomGst = Math.round(bomSubtotal * (taxRate / 100.0) * 100) / 100;
  const bomContingency = Math.round(bomSubtotal * (contingencyRate / 100.0) * 100) / 100;
  const bomGrandTotal = Math.round((bomSubtotal + bomGst + bomContingency) * 100) / 100;

  // Use Idea as Template
  const loadIdeaIntoForm = (idea) => {
    setProposalForm({
      title: idea.title,
      domain: idea.domain,
      abstract: idea.description,
      objectives: [
        `Implement core sensing & telemetry according to ${idea.curriculum_mapping}.`,
        `Prototype schematic on breadboard using ${idea.suggested_mcu}.`,
        'Verify power consumption within regulation budget.',
        'Document performance milestones and present viva demonstration.'
      ],
      hardware_stack: [...idea.hardware_stack],
      software_stack: [...idea.software_stack],
      mentor_name: 'Dr. P. Nirmal Kumar (Professor & Head, Dept of Electronics)'
    });
    setActiveTab('proposals');
    showToast(`Loaded template '${idea.title}' into Proposal Builder!`, 'success');
  };

  // Submit Proposal
  const handleProposalSubmit = async (e) => {
    e.preventDefault();
    if (!proposalForm.title.trim()) {
      showToast('Please specify a project title.', 'error');
      return;
    }

    try {
      const res = await fetch('/api/projects/proposals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId,
          title: proposalForm.title,
          domain: proposalForm.domain,
          abstract: proposalForm.abstract,
          objectives: proposalForm.objectives,
          hardware_stack: proposalForm.hardware_stack,
          software_stack: proposalForm.software_stack,
          mentor_name: proposalForm.mentor_name,
          role: 'Student'
        })
      });

      if (res.ok) {
        showToast('Mini-project proposal submitted successfully for faculty review!', 'success');
        fetchProposals();
        fetchOverview();
        return;
      }
    } catch {
      // Local fallback
    }

    const newProp = {
      proposal_id: `PROP_${Date.now()}`,
      title: proposalForm.title,
      domain: proposalForm.domain,
      mentor_name: proposalForm.mentor_name,
      status: 'SUBMITTED',
      progress_percent: 0.0,
      bom_items_count: bomItems.length,
      bom_subtotal_inr: bomSubtotal,
      created_at: Date.now() / 1000
    };
    setProposals([newProp, ...proposals]);
    showToast('Mini-project proposal recorded locally and queued for review.', 'success');
  };

  // Toggle Milestone Status
  const toggleMilestone = async (id, currentStatus) => {
    const nextStatus = currentStatus === 'PENDING' ? 'IN_PROGRESS' : (currentStatus === 'IN_PROGRESS' ? 'COMPLETED' : 'PENDING');
    try {
      await fetch('/api/projects/milestone/status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ milestone_id: id, status: nextStatus })
      });
    } catch {
      // ignore offline
    }

    setMilestones(milestones.map(m => m.milestone_id === id ? { ...m, status: nextStatus } : m));
    showToast(`Milestone status updated to ${nextStatus}.`, 'info');
  };

  // Add Milestone
  const handleAddMilestone = async (e) => {
    e.preventDefault();
    if (!newMsTitle.trim()) return;

    const newMs = {
      milestone_id: `MS_${Date.now()}`,
      title: newMsTitle.trim(),
      weightage_percent: parseFloat(newMsWeight) || 20,
      due_date: newMsDate,
      status: 'PENDING',
      deliverables: ['Working prototype artifact', 'Technical report commit']
    };

    try {
      await fetch('/api/projects/milestones', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          proposal_id: selectedProposalId,
          ...newMs
        })
      });
    } catch {
      // fallback
    }

    setMilestones([...milestones, newMs]);
    setNewMsTitle('');
    showToast('New project milestone successfully added.', 'success');
  };

  // Filter Ideas
  const filteredIdeas = selectedDomain === 'ALL'
    ? ideas
    : ideas.filter(i => i.domain.toLowerCase().includes(selectedDomain.toLowerCase()));

  // Milestone Progress
  const completedWeight = milestones.filter(m => m.status === 'COMPLETED').reduce((acc, m) => acc + m.weightage_percent, 0);
  const totalWeight = milestones.reduce((acc, m) => acc + m.weightage_percent, 0) || 100;
  const attainmentPercent = Math.min(100, Math.round((completedWeight / totalWeight) * 100));

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {notification && (
        <div className={`p-3.5 rounded-xl border text-sm flex items-center justify-between transition-all ${
          notification.type === 'error'
            ? 'bg-rose-950/80 border-rose-500/50 text-rose-200'
            : notification.type === 'warning'
            ? 'bg-amber-950/80 border-amber-500/50 text-amber-200'
            : 'bg-[#041026]/90 border-[#00F0B5]/40 text-[#00F0B5]'
        }`}>
          <span>{notification.msg}</span>
          <button onClick={() => setNotification(null)} className="text-xs opacity-70 hover:opacity-100 ml-4">✕</button>
        </div>
      )}

      {/* Top Banner / Metrics Strip */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Total Proposals</span>
          <div className="text-2xl font-bold text-slate-100 mt-1">
            {overview?.metrics?.total_proposals || proposals.length}
          </div>
          <span className="text-[10px] text-emerald-400 mt-1">Anna Univ Reg 2023</span>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Approved Projects</span>
          <div className="text-2xl font-bold text-[#00F0B5] mt-1">
            {overview?.metrics?.approved_proposals || 1}
          </div>
          <span className="text-[10px] text-slate-400 mt-1">Faculty Mentored</span>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Project Attainment</span>
          <div className="text-2xl font-bold text-cyan-300 mt-1">
            {attainmentPercent}%
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
            <div className="bg-gradient-to-r from-emerald-500 to-cyan-400 h-full rounded-full transition-all duration-500" style={{ width: `${attainmentPercent}%` }} />
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Est. BOM Expenditure</span>
          <div className="text-2xl font-bold text-amber-300 mt-1">
            ₹{bomGrandTotal.toLocaleString('en-IN')}
          </div>
          <span className="text-[10px] text-slate-400 mt-1">Incl. 18% GST + Buffer</span>
        </div>

        <div className="p-4 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between col-span-2 md:col-span-1">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Innovation Catalog</span>
          <div className="text-2xl font-bold text-purple-300 mt-1">
            {ideas.length} Ideas
          </div>
          <span className="text-[10px] text-slate-400 mt-1">Curated ECE Blueprints</span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-slate-800 overflow-x-auto gap-2 pb-2">
        {[
          { id: 'proposals', label: '1. Proposal Studio', desc: 'Mini-Project Builder' },
          { id: 'bom', label: '2. BOM Cost Estimator', desc: 'Hardware Budget & GST' },
          { id: 'compatibility', label: '3. Compatibility Lab', desc: 'Voltage & Current Check' },
          { id: 'milestones', label: '4. Milestone Tracker', desc: 'Deliverables & Viva' },
          { id: 'ideas', label: '5. Innovation Library', desc: 'Curriculum Blueprints' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2.5 rounded-xl text-left whitespace-nowrap transition-all ${
              activeTab === tab.id
                ? 'bg-[#00F0B5]/15 border border-[#00F0B5]/40 text-[#00F0B5]'
                : 'text-slate-400 hover:text-slate-200 hover:bg-[#020813] border border-transparent'
            }`}
          >
            <div className="text-xs font-semibold">{tab.label}</div>
            <div className="text-[10px] opacity-70">{tab.desc}</div>
          </button>
        ))}
      </div>

      {/* TAB 1: Proposal Studio */}
      {activeTab === 'proposals' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Proposal Generation Form */}
          <div className="lg:col-span-2 p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
              <div>
                <h3 className="text-lg font-semibold text-slate-100">Mini-Project Proposal Builder</h3>
                <p className="text-xs text-slate-400">Anna University Regulation 2023 • EC3711 Mini Project Submission</p>
              </div>
              <span className="text-xs px-2.5 py-1 rounded-md bg-[#00693E]/40 text-[#00F0B5] border border-[#00F0B5]/30 font-mono">
                EC3711 Form
              </span>
            </div>

            <form onSubmit={handleProposalSubmit} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">Project Title</label>
                <input
                  type="text"
                  required
                  value={proposalForm.title}
                  onChange={(e) => setProposalForm({ ...proposalForm, title: e.target.value })}
                  placeholder="e.g., Ultra-Low-Power Edge IoT Microclimate Node with LoRa Telemetry"
                  className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-[#00F0B5]"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">ECE Specialization Domain</label>
                  <select
                    value={proposalForm.domain}
                    onChange={(e) => setProposalForm({ ...proposalForm, domain: e.target.value })}
                    className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-[#00F0B5]"
                  >
                    <option value="IoT & Smart Systems">IoT & Smart Systems</option>
                    <option value="Embedded RTOS & Robotics">Embedded RTOS & Robotics</option>
                    <option value="Edge AI & Signal Processing">Edge AI & Signal Processing</option>
                    <option value="VLSI & Digital Systems">VLSI & Digital Systems</option>
                    <option value="Biomedical Electronics">Biomedical Electronics</option>
                    <option value="Wireless & RF Communications">Wireless & RF Communications</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs text-slate-300 mb-1">Faculty Mentor / Supervisor</label>
                  <input
                    type="text"
                    value={proposalForm.mentor_name}
                    onChange={(e) => setProposalForm({ ...proposalForm, mentor_name: e.target.value })}
                    className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-[#00F0B5]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Technical Abstract & Problem Statement</label>
                <textarea
                  rows={3}
                  value={proposalForm.abstract}
                  onChange={(e) => setProposalForm({ ...proposalForm, abstract: e.target.value })}
                  placeholder="Summarize the core technical challenges, proposed circuit architecture, and expected experimental deliverables..."
                  className="w-full bg-[#020813] border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-slate-200 focus:outline-none focus:border-[#00F0B5]"
                />
              </div>

              {/* Objectives */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-xs text-slate-300">Key Technical Objectives</label>
                  <button
                    type="button"
                    onClick={() => setProposalForm({
                      ...proposalForm,
                      objectives: [...proposalForm.objectives, `New objective #${proposalForm.objectives.length + 1}`]
                    })}
                    className="text-[11px] text-[#00F0B5] hover:underline"
                  >
                    + Add Objective
                  </button>
                </div>
                <div className="space-y-1.5">
                  {proposalForm.objectives.map((obj, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <span className="text-xs font-mono text-slate-500 w-4">{idx + 1}.</span>
                      <input
                        type="text"
                        value={obj}
                        onChange={(e) => {
                          const updated = [...proposalForm.objectives];
                          updated[idx] = e.target.value;
                          setProposalForm({ ...proposalForm, objectives: updated });
                        }}
                        className="flex-1 bg-[#020813] border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                      />
                      <button
                        type="button"
                        onClick={() => {
                          const updated = proposalForm.objectives.filter((_, i) => i !== idx);
                          setProposalForm({ ...proposalForm, objectives: updated });
                        }}
                        className="text-xs text-slate-500 hover:text-rose-400 px-1"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Hardware & Software Stacks */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Hardware Stack (Key Chips & Modules)</label>
                  <div className="flex flex-wrap gap-1.5 p-2 bg-[#020813] border border-slate-800 rounded-xl min-h-[42px]">
                    {proposalForm.hardware_stack.map((hw, idx) => (
                      <span key={idx} className="text-[11px] px-2 py-0.5 rounded-md bg-[#041026] text-slate-200 border border-slate-700 flex items-center gap-1">
                        {hw}
                        <button
                          type="button"
                          onClick={() => setProposalForm({
                            ...proposalForm,
                            hardware_stack: proposalForm.hardware_stack.filter((_, i) => i !== idx)
                          })}
                          className="hover:text-rose-400"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-xs text-slate-300 mb-1">Firmware & Software Stack</label>
                  <div className="flex flex-wrap gap-1.5 p-2 bg-[#020813] border border-slate-800 rounded-xl min-h-[42px]">
                    {proposalForm.software_stack.map((sw, idx) => (
                      <span key={idx} className="text-[11px] px-2 py-0.5 rounded-md bg-[#041026] text-slate-200 border border-slate-700 flex items-center gap-1">
                        {sw}
                        <button
                          type="button"
                          onClick={() => setProposalForm({
                            ...proposalForm,
                            software_stack: proposalForm.software_stack.filter((_, i) => i !== idx)
                          })}
                          className="hover:text-rose-400"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="pt-2 flex justify-end gap-3">
                <button
                  type="submit"
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-[#00F0B5] text-slate-950 font-semibold text-xs hover:opacity-95 shadow-lg shadow-[#00F0B5]/20"
                >
                  Submit Proposal for Review
                </button>
              </div>
            </form>
          </div>

          {/* Registered Proposals List */}
          <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
            <h3 className="text-md font-semibold text-slate-100">Registered Project Proposals</h3>
            <p className="text-xs text-slate-400">Proposals linked to Student ID: <span className="font-mono text-[#00F0B5]">{studentId}</span></p>

            <div className="space-y-3">
              {proposals.map((prop) => (
                <div
                  key={prop.proposal_id}
                  onClick={() => setSelectedProposalId(prop.proposal_id)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    selectedProposalId === prop.proposal_id
                      ? 'bg-[#020813] border-[#00F0B5]'
                      : 'bg-[#020813]/60 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-mono text-slate-400">{prop.proposal_id}</span>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                      prop.status === 'APPROVED'
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30'
                        : prop.status === 'SUBMITTED'
                        ? 'bg-amber-950 text-amber-400 border border-amber-500/30'
                        : 'bg-slate-800 text-slate-300'
                    }`}>
                      {prop.status}
                    </span>
                  </div>

                  <h4 className="text-xs font-semibold text-slate-200 line-clamp-2">{prop.title}</h4>
                  <div className="text-[11px] text-slate-400 mt-1">{prop.domain}</div>

                  <div className="mt-3 pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-400">
                    <span>BOM: ₹{(prop.bom_subtotal_inr || 1735).toLocaleString('en-IN')}</span>
                    <span>Progress: {prop.progress_percent || 50}%</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="p-3 rounded-xl bg-[#020813] border border-slate-800/80 text-[11px] text-slate-400">
              <span className="font-semibold text-slate-200">Regulation 2023 Notice:</span> All proposals must obtain mentor approval prior to component procurement. Final Viva Voce accounts for 40% of EC3711 grading.
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: BOM Cost Estimator */}
      {activeTab === 'bom' && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
              <div>
                <h3 className="text-lg font-semibold text-slate-100">Engineering Bill of Materials (BOM) Calculator</h3>
                <p className="text-xs text-slate-400">Hardware Component Cost Estimation with GST and Engineering Contingency</p>
              </div>

              {/* Sliders for GST and Contingency */}
              <div className="flex items-center gap-4 text-xs text-slate-300">
                <div className="flex items-center gap-2">
                  <span>GST Buffer:</span>
                  <input
                    type="number"
                    min="0"
                    max="30"
                    value={taxRate}
                    onChange={(e) => setTaxRate(parseFloat(e.target.value) || 0)}
                    className="w-14 bg-[#020813] border border-slate-700 rounded-lg px-2 py-1 text-center font-mono text-emerald-400"
                  />
                  <span>%</span>
                </div>
                <div className="flex items-center gap-2">
                  <span>Contingency:</span>
                  <input
                    type="number"
                    min="0"
                    max="30"
                    value={contingencyRate}
                    onChange={(e) => setContingencyRate(parseFloat(e.target.value) || 0)}
                    className="w-14 bg-[#020813] border border-slate-700 rounded-lg px-2 py-1 text-center font-mono text-amber-400"
                  />
                  <span>%</span>
                </div>
              </div>
            </div>

            {/* Live BOM Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-mono">
                    <th className="py-2.5 px-3">Component Name</th>
                    <th className="py-2.5 px-3">Category</th>
                    <th className="py-2.5 px-3">Vendor</th>
                    <th className="py-2.5 px-3 text-right">Unit Price (₹)</th>
                    <th className="py-2.5 px-3 text-center">Qty</th>
                    <th className="py-2.5 px-3 text-right">Subtotal (₹)</th>
                    <th className="py-2.5 px-3 text-center">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-200">
                  {bomItems.map((item) => (
                    <tr key={item.id} className="hover:bg-[#020813]/60">
                      <td className="py-2 px-3 font-semibold text-slate-100">{item.component_name}</td>
                      <td className="py-2 px-3">
                        <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 font-mono text-slate-300">
                          {item.category}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-slate-400">{item.vendor}</td>
                      <td className="py-2 px-3 text-right font-mono">₹{item.unit_price_inr.toFixed(2)}</td>
                      <td className="py-2 px-3 text-center font-mono">{item.quantity}</td>
                      <td className="py-2 px-3 text-right font-mono font-semibold text-slate-100">
                        ₹{(item.quantity * item.unit_price_inr).toFixed(2)}
                      </td>
                      <td className="py-2 px-3 text-center">
                        <button
                          onClick={() => removeBomItem(item.id)}
                          className="text-slate-500 hover:text-rose-400 text-sm"
                        >
                          ✕
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Quick Component Adder Form */}
            <div className="p-4 rounded-xl bg-[#020813] border border-slate-800 grid grid-cols-1 md:grid-cols-6 gap-3 items-end">
              <div className="md:col-span-2">
                <label className="block text-[11px] text-slate-400 mb-1">Add Component</label>
                <input
                  type="text"
                  placeholder="e.g. BMP280 Barometer"
                  value={newItemName}
                  onChange={(e) => setNewItemName(e.target.value)}
                  className="w-full bg-[#041026] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                />
              </div>

              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Category</label>
                <select
                  value={newItemCat}
                  onChange={(e) => setNewItemCat(e.target.value)}
                  className="w-full bg-[#041026] border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-slate-200"
                >
                  <option value="MCU">MCU</option>
                  <option value="SENSOR">SENSOR</option>
                  <option value="COMMUNICATION">COMM</option>
                  <option value="ACTUATOR">ACTUATOR</option>
                  <option value="POWER">POWER</option>
                  <option value="DISPLAY">DISPLAY</option>
                  <option value="PASSIVE">PASSIVE</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Qty</label>
                <input
                  type="number"
                  min="1"
                  value={newItemQty}
                  onChange={(e) => setNewItemQty(e.target.value)}
                  className="w-full bg-[#041026] border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-slate-200"
                />
              </div>

              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Unit Price (₹)</label>
                <input
                  type="number"
                  min="0"
                  value={newItemPrice}
                  onChange={(e) => setNewItemPrice(e.target.value)}
                  className="w-full bg-[#041026] border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-slate-200"
                />
              </div>

              <div>
                <button
                  type="button"
                  onClick={addBomItem}
                  className="w-full py-2 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 border border-emerald-500/30 rounded-lg text-xs font-semibold"
                >
                  + Add to BOM
                </button>
              </div>
            </div>

            {/* Financial Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2">
              <div className="p-3.5 rounded-xl bg-[#020813] border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-mono">BOM Subtotal</span>
                <div className="text-lg font-bold text-slate-100 font-mono mt-0.5">
                  ₹{bomSubtotal.toFixed(2)}
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-[#020813] border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-mono">GST Buffer ({taxRate}%)</span>
                <div className="text-lg font-bold text-emerald-400 font-mono mt-0.5">
                  ₹{bomGst.toFixed(2)}
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-[#020813] border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-mono">Contingency ({contingencyRate}%)</span>
                <div className="text-lg font-bold text-amber-400 font-mono mt-0.5">
                  ₹{bomContingency.toFixed(2)}
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-[#00693E]/20 border border-[#00F0B5]/30">
                <span className="text-[10px] text-[#00F0B5] uppercase font-mono">Grand Total Budget</span>
                <div className="text-xl font-bold text-[#00F0B5] font-mono mt-0.5">
                  ₹{bomGrandTotal.toFixed(2)}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Hardware Compatibility Lab */}
      {activeTab === 'compatibility' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Microcontroller & Component Bench */}
          <div className="lg:col-span-2 space-y-4">
            <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
              <div className="border-b border-slate-800/80 pb-3 flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-slate-100">Component Interoperability & Power Rail Analyzer</h3>
                  <p className="text-xs text-slate-400">Verifies logic voltage level matching, regulator current budget, and bus constraints</p>
                </div>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                  Lab Rule Checker
                </span>
              </div>

              {/* MCU Selection */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-2">1. Select Target Microcontroller Platform</label>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5">
                  {MCU_OPTIONS.map(mcu => (
                    <div
                      key={mcu.name}
                      onClick={() => setSelectedMcu(mcu.name)}
                      className={`p-3 rounded-xl border cursor-pointer transition-all ${
                        selectedMcu === mcu.name
                          ? 'bg-[#00F0B5]/10 border-[#00F0B5] text-slate-100'
                          : 'bg-[#020813] border-slate-800 text-slate-400 hover:border-slate-700'
                      }`}
                    >
                      <div className="text-xs font-bold">{mcu.name}</div>
                      <div className="text-[10px] font-mono mt-1 text-[#00F0B5]">
                        Logic: {mcu.voltage}V • LDO Max: {mcu.max_ma}mA
                      </div>
                      <div className="text-[9px] text-slate-500 mt-0.5">{mcu.ports}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Active Components on Bench */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-xs font-semibold text-slate-300">2. Active Attached Modules & Sensors</label>
                  <span className="text-[11px] text-slate-400 font-mono">{activeComponents.length} Connected</span>
                </div>

                <div className="space-y-2">
                  {activeComponents.map((comp) => (
                    <div key={comp.name} className="p-3 rounded-xl bg-[#020813] border border-slate-800 flex items-center justify-between">
                      <div>
                        <div className="text-xs font-semibold text-slate-200">{comp.name}</div>
                        <div className="text-[10px] font-mono text-slate-400 flex gap-3 mt-0.5">
                          <span>Voltage: <b className="text-slate-300">{comp.voltage}V</b></span>
                          <span>Current: <b className="text-slate-300">{comp.current_ma} mA</b></span>
                          <span>Interface: <b className="text-cyan-400">{comp.iface}</b></span>
                        </div>
                      </div>
                      <button
                        onClick={() => removeComponentFromBench(comp.name)}
                        className="text-xs text-slate-500 hover:text-rose-400 px-2 py-1 rounded bg-slate-900 border border-slate-800"
                      >
                        Disconnect
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick Add Preset Modules */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-2">3. Add Modules from ECE Component Catalog</label>
                <div className="flex flex-wrap gap-2">
                  {PRESET_COMPONENTS.map(comp => (
                    <button
                      key={comp.name}
                      onClick={() => addComponentToBench(comp)}
                      className="px-2.5 py-1.5 rounded-lg bg-[#020813] hover:bg-[#00F0B5]/10 border border-slate-800 hover:border-[#00F0B5]/40 text-slate-300 hover:text-[#00F0B5] text-[11px] font-mono transition-all"
                    >
                      + {comp.name.split(' ')[0]} ({comp.voltage}V, {comp.current_ma}mA)
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Compatibility Verdict & Diagnostics */}
          <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
            <h3 className="text-md font-semibold text-slate-100">Engineering Compatibility Verdict</h3>

            {compatResult && (
              <>
                {/* Big Verdict Badge */}
                <div className={`p-4 rounded-xl border text-center ${
                  compatResult.verdict === 'COMPATIBLE'
                    ? 'bg-emerald-950/60 border-emerald-500/50 text-emerald-300'
                    : compatResult.verdict === 'COMPATIBLE_WITH_CAVEATS'
                    ? 'bg-amber-950/60 border-amber-500/50 text-amber-300'
                    : 'bg-rose-950/60 border-rose-500/50 text-rose-300'
                }`}>
                  <div className="text-sm font-mono uppercase tracking-wider font-bold">
                    {compatResult.verdict.replace(/_/g, ' ')}
                  </div>
                  <div className="text-xs opacity-80 mt-1">
                    {compatResult.verdict === 'COMPATIBLE'
                      ? 'All electrical, power, and interface constraints satisfied.'
                      : compatResult.verdict === 'COMPATIBLE_WITH_CAVEATS'
                      ? 'Functional with protective circuitry / level translators.'
                      : 'Severe electrical mismatch detected. Hardware damage risk.'}
                  </div>
                </div>

                {/* Power Budget Gauge */}
                <div className="p-4 rounded-xl bg-[#020813] border border-slate-800 space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-400">Total Current Draw:</span>
                    <span className="font-mono text-slate-200">
                      {compatResult.power_budget.total_current_ma} mA / {compatResult.power_budget.regulator_max_ma} mA
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-300 ${
                        compatResult.power_budget.total_current_ma > compatResult.power_budget.regulator_max_ma
                          ? 'bg-rose-500'
                          : compatResult.power_budget.headroom_percent < 20
                          ? 'bg-amber-500'
                          : 'bg-emerald-400'
                      }`}
                      style={{
                        width: `${Math.min(100, (compatResult.power_budget.total_current_ma / compatResult.power_budget.regulator_max_ma) * 100)}%`
                      }}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                    <span>Headroom: {compatResult.power_budget.headroom_ma} mA</span>
                    <span>Safety Margin: {compatResult.power_budget.headroom_percent}%</span>
                  </div>
                </div>

                {/* Critical Issues Feed */}
                {compatResult.critical_errors.length > 0 && (
                  <div className="space-y-1.5">
                    <span className="text-[11px] font-semibold text-rose-400 uppercase tracking-wider">Critical Blockers:</span>
                    {compatResult.critical_errors.map((err, idx) => (
                      <div key={idx} className="p-2.5 rounded-lg bg-rose-950/40 border border-rose-500/30 text-[11px] text-rose-200">
                        ⚠️ {err}
                      </div>
                    ))}
                  </div>
                )}

                {/* Engineering Caveats */}
                {compatResult.caveats.length > 0 && (
                  <div className="space-y-1.5">
                    <span className="text-[11px] font-semibold text-amber-400 uppercase tracking-wider">Engineering Advice:</span>
                    {compatResult.caveats.map((cav, idx) => (
                      <div key={idx} className="p-2.5 rounded-lg bg-amber-950/40 border border-amber-500/30 text-[11px] text-amber-200">
                        ⚡ {cav}
                      </div>
                    ))}
                  </div>
                )}

                {/* Passed Checks */}
                {compatResult.passed_checks.length > 0 && (
                  <div className="space-y-1.5">
                    <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider">Verified Compatible:</span>
                    {compatResult.passed_checks.map((chk, idx) => (
                      <div key={idx} className="p-2 rounded-lg bg-emerald-950/20 border border-emerald-500/20 text-[10px] text-emerald-300">
                        ✓ {chk}
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* TAB 4: Milestone Tracker */}
      {activeTab === 'milestones' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div>
                  <h3 className="text-lg font-semibold text-slate-100">Project Milestones & Deliverables</h3>
                  <p className="text-xs text-slate-400">Anna University EC3711 Continuous Evaluation Review Tracker</p>
                </div>
                <div className="text-right">
                  <div className="text-xs font-mono text-emerald-400 font-bold">{attainmentPercent}% Completed</div>
                  <div className="text-[10px] text-slate-400">Total Weight: {totalWeight}%</div>
                </div>
              </div>

              {/* Milestone Cards */}
              <div className="space-y-3">
                {milestones.map((ms, idx) => (
                  <div key={ms.milestone_id} className="p-4 rounded-xl bg-[#020813] border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 text-xs flex items-center justify-center font-mono">
                          {idx + 1}
                        </span>
                        <h4 className="text-xs font-bold text-slate-200">{ms.title}</h4>
                      </div>

                      <button
                        onClick={() => toggleMilestone(ms.milestone_id, ms.status)}
                        className={`text-[10px] px-2.5 py-1 rounded-md font-mono font-bold transition-all ${
                          ms.status === 'COMPLETED'
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/40 hover:bg-emerald-900/60'
                            : ms.status === 'IN_PROGRESS'
                            ? 'bg-cyan-950 text-cyan-400 border border-cyan-500/40 hover:bg-cyan-900/60'
                            : 'bg-slate-800 text-slate-400 border border-slate-700 hover:bg-slate-700'
                        }`}
                      >
                        {ms.status} ↻
                      </button>
                    </div>

                    <p className="text-xs text-slate-400 pl-7">{ms.description || 'Milestone deliverables verification.'}</p>

                    <div className="pl-7 flex items-center gap-4 text-[10px] text-slate-500 font-mono">
                      <span>Weightage: <b className="text-slate-300">{ms.weightage_percent}%</b></span>
                      <span>Target Date: <b className="text-slate-300">{ms.due_date}</b></span>
                    </div>

                    {ms.deliverables && ms.deliverables.length > 0 && (
                      <div className="pl-7 pt-1 flex flex-wrap gap-1.5">
                        {ms.deliverables.map((deliv, dIdx) => (
                          <span key={dIdx} className="text-[9px] px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                            📋 {deliv}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Add Milestone Form */}
          <div className="p-6 rounded-2xl bg-[#041026] border border-slate-800 space-y-4">
            <h3 className="text-md font-semibold text-slate-100">Add Project Milestone</h3>
            <p className="text-xs text-slate-400">Append an evaluation milestone for continuous assessment.</p>

            <form onSubmit={handleAddMilestone} className="space-y-3">
              <div>
                <label className="block text-xs text-slate-300 mb-1">Milestone Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. PCB Layout & Fabrication"
                  value={newMsTitle}
                  onChange={(e) => setNewMsTitle(e.target.value)}
                  className="w-full bg-[#020813] border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Weightage %</label>
                  <input
                    type="number"
                    min="5"
                    max="50"
                    value={newMsWeight}
                    onChange={(e) => setNewMsWeight(e.target.value)}
                    className="w-full bg-[#020813] border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Due Date</label>
                  <input
                    type="date"
                    value={newMsDate}
                    onChange={(e) => setNewMsDate(e.target.value)}
                    className="w-full bg-[#020813] border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded-xl bg-[#00F0B5]/20 hover:bg-[#00F0B5]/30 text-[#00F0B5] border border-[#00F0B5]/40 text-xs font-semibold"
              >
                + Register Milestone
              </button>
            </form>

            <div className="p-3.5 rounded-xl bg-[#020813] border border-slate-800 text-[11px] text-slate-400 space-y-1">
              <div className="font-semibold text-slate-200">MIT Evaluation Rubric:</div>
              <div>• Review 1 (20%): Abstract, Problem & Component Spec</div>
              <div>• Review 2 (30%): Circuit Simulation & Breadboard Prototype</div>
              <div>• Review 3 (30%): Final Packaging & Telemetry Tests</div>
              <div>• Viva Voce (20%): External Examiner Technical Defense</div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: Innovation Idea Library */}
      {activeTab === 'ideas' && (
        <div className="space-y-4">
          {/* Domain Filter Pills */}
          <div className="flex gap-2 overflow-x-auto pb-1">
            {['ALL', 'IoT', 'Embedded RTOS', 'Edge AI', 'VLSI', 'Biomedical', 'Robotics'].map(dom => (
              <button
                key={dom}
                onClick={() => setSelectedDomain(dom)}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${
                  selectedDomain === dom
                    ? 'bg-[#00F0B5] text-slate-950 font-bold'
                    : 'bg-[#041026] text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                {dom}
              </button>
            ))}
          </div>

          {/* Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredIdeas.map((idea) => (
              <div key={idea.idea_id} className="p-5 rounded-2xl bg-[#041026] border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition-all">
                <div className="space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] px-2 py-0.5 rounded font-mono bg-[#00693E]/40 text-[#00F0B5] border border-[#00F0B5]/20">
                      {idea.domain}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">{idea.difficulty}</span>
                  </div>

                  <h4 className="text-sm font-bold text-slate-100">{idea.title}</h4>
                  <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed">{idea.description}</p>

                  <div className="p-2 rounded-lg bg-[#020813] text-[10px] font-mono text-slate-300">
                    <div className="text-slate-500">Curriculum Link:</div>
                    <div className="text-emerald-400 truncate">{idea.curriculum_mapping}</div>
                  </div>

                  <div className="space-y-1">
                    <div className="text-[10px] text-slate-500">Hardware Stack:</div>
                    <div className="flex flex-wrap gap-1">
                      {idea.hardware_stack.map((hw, idx) => (
                        <span key={idx} className="text-[9px] px-1.5 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">
                          {hw}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
                  <span className="text-xs font-mono font-semibold text-amber-300">
                    Est. ₹{idea.estimated_budget_inr.toLocaleString('en-IN')}
                  </span>
                  <button
                    onClick={() => loadIdeaIntoForm(idea)}
                    className="px-3 py-1.5 rounded-lg bg-[#00F0B5]/15 hover:bg-[#00F0B5]/25 text-[#00F0B5] border border-[#00F0B5]/30 text-xs font-semibold transition-all"
                  >
                    Use Template →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

