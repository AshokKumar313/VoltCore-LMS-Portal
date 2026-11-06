import React, { useState, useMemo } from 'react';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Phase G: IoT & Connected Systems Hub (Features 271–280)
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 *
 * Features:
 *   - Feature 271: IoT Architecture Diagram Builder (Perception, Edge, Network, Cloud, App)
 *   - Feature 272: MQTT Message Structure Explorer (Fixed/Variable Headers, QoS 0/1/2 Handshakes)
 *   - Feature 273: Sensor Data Dashboard with Anomaly Detection (Z-Score & Thresholds)
 *   - Feature 274: IoT Device Registry (ESP32, STM32-LoRa, RP2040, nRF52 Inventory)
 *   - Feature 275: Virtual Sensor Calibration Tool (2-Point Linear, Temp Compensation)
 *   - Feature 276: MQTT Topic Structure Designer (Hierarchical Paths & Wildcard Matcher)
 *   - Feature 277: IoT Packet History Ledger (CONNECT, PUBLISH, SUBSCRIBE, RSSI, SNR)
 *   - Feature 278: Device Status Timeline Generator (Boot, Wi-Fi, MQTT Handshake, Sleep)
 *   - Feature 279: Smart Home / Industrial Automation Rule Engine (IF-THEN Trigger Engine)
 *   - Feature 280: IoT Network Topology Visualizer & Link Budget (Star, Mesh, Path Loss)
 * Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
 * ========================================================================================
 */

// 5-Tier Architecture Model (Feature 271)
const TIERS = [
  {
    id: 1,
    name: "Perception Layer",
    taName: "உணர்வி அடுக்கு",
    desc: "Physical signal acquisition via analog/digital transducers & local actuation.",
    taDesc: "சென்சார்கள் மற்றும் ஆக்சுவேட்டர்கள் மூலம் இயற்பியல் தகவல்களைப் பெறுதல்.",
    protocols: ["I2C", "SPI", "UART", "1-Wire", "ADC"],
    hardware: ["BME280 (Temp/Hum/Press)", "MPU6050 (IMU)", "MQ-135 (Air Quality)", "Relay"],
    color: "emerald"
  },
  {
    id: 2,
    name: "Edge / Gateway Layer",
    taName: "எட்ஜ் / கேட்வே அடுக்கு",
    desc: "Local telemetry aggregation, edge filtering, security encryption & protocol translation.",
    taDesc: "உள்ளூர் அளவில் தரவு சேகரிப்பு, பில்டரிங் மற்றும் நெறிமுறை மாற்றம்.",
    protocols: ["ESP-NOW", "Modbus-RTU", "BLE Mesh", "CAN Bus"],
    hardware: ["ESP32-S3 Edge Gateway", "Raspberry Pi 4 CM4", "STM32F4 Gateway"],
    color: "cyan"
  },
  {
    id: 3,
    name: "Network & Transport Layer",
    taName: "நெட்வொர்க் பரிமாற்ற அடுக்கு",
    desc: "Local and long-range wireless backhaul routing telemetry to internet gateways.",
    taDesc: "நீண்ட தூர வயர்லெஸ் முறையில் தகவல்களை இணையத்திற்கு அனுப்புதல்.",
    protocols: ["Wi-Fi (802.11 b/g/n)", "LoRaWAN (IN865)", "NB-IoT", "ZigBee (802.15.4)"],
    hardware: ["SX1276 LoRa Transceiver", "SIM7080G Cellular", "CC2530 ZigBee"],
    color: "indigo"
  },
  {
    id: 4,
    name: "Middleware & Cloud Broker",
    taName: "கிளவுட் தரவுத்தரகர் அடுக்கு",
    desc: "Scalable pub/sub message brokering, time-series storage & analytics engines.",
    taDesc: "MQTT மெசேஜ் புரோக்கர், தரவுத்தளம் மற்றும் நிகழ்நேர பகுப்பாய்வு.",
    protocols: ["MQTT 3.1.1/5.0", "CoAP", "HTTP/2 REST", "WebSockets"],
    hardware: ["Mosquitto MQTT Broker", "SQLite WAL Telemetry Store", "EMQX Cluster"],
    color: "purple"
  },
  {
    id: 5,
    name: "Application & Business Layer",
    taName: "பயன்பாட்டு அடுக்கு",
    desc: "Real-time supervisory dashboards, IF-THEN automation rules & predictive alerts.",
    taDesc: "பயனர் டேஷ்போர்டு, தானியங்கி விதிகள் மற்றும் பாதுகாப்பு எச்சரிக்கைகள்.",
    protocols: ["HTTPS", "WSS", "WebPush", "SMTP", "SMS Webhook"],
    hardware: ["VoltCore Apex Dashboard", "Grafana Panels", "Automated Relays"],
    color: "amber"
  }
];

// Sample Device Inventory (Feature 274)
const INITIAL_DEVICES = [
  {
    nodeId: "NODE-MIT-LAB304-01",
    name: "Ambient Environmental Node",
    platform: "ESP32-WROOM-32",
    mac: "24:6F:28:1A:BC:01",
    ip: "192.168.1.101",
    firmware: "v2.4.1",
    status: "ONLINE",
    battery: 98,
    sensors: ["BME280", "MQ-135"],
    rssi: -62
  },
  {
    nodeId: "NODE-MIT-LAB304-02",
    name: "Precision Vibration Sensor",
    platform: "STM32F4-LORA",
    mac: "00:80:E1:15:2B:02",
    ip: "192.168.1.102",
    firmware: "v1.9.0",
    status: "ONLINE",
    battery: 85,
    sensors: ["MPU6050", "ADXL345"],
    rssi: -55
  },
  {
    nodeId: "NODE-MIT-ROOF-03",
    name: "Solar Micro-Weather Station",
    platform: "RP2040-WIFI",
    mac: "D8:3A:DD:C4:4E:03",
    ip: "192.168.1.103",
    firmware: "v2.1.0",
    status: "SLEEPING",
    battery: 72,
    sensors: ["Anemometer", "Pyranometer"],
    rssi: -78
  },
  {
    nodeId: "NODE-MIT-SMART-04",
    name: "Industrial Relay Controller",
    platform: "ESP32-S3",
    mac: "30:AE:A4:07:9F:04",
    ip: "192.168.1.104",
    firmware: "v3.0.2",
    status: "ONLINE",
    battery: 100,
    sensors: ["CT Sensor", "4-Ch Relay"],
    rssi: -48
  }
];

// Sample Telemetry Series (Feature 273)
const SENSOR_STREAMS = {
  Temperature: {
    unit: "°C",
    upper: 40,
    lower: 15,
    data: [26.2, 26.5, 26.4, 26.8, 27.1, 26.9, 27.4, 27.8, 28.2, 42.5, 28.1, 28.4, 28.0, 27.9, 28.3]
  },
  Humidity: {
    unit: "%",
    upper: 80,
    lower: 30,
    data: [54.2, 55.0, 54.8, 56.1, 56.4, 55.9, 57.2, 58.0, 58.5, 59.1, 58.8, 59.4, 60.1, 59.8, 59.5]
  },
  Pressure: {
    unit: "hPa",
    upper: 1030,
    lower: 980,
    data: [1013.2, 1013.1, 1013.3, 1013.0, 1012.9, 1013.1, 1012.8, 1012.7, 1012.8, 1012.6, 1012.5, 1012.7, 1012.6, 1012.8, 1012.9]
  },
  AirQuality: {
    unit: "AQI",
    upper: 150,
    lower: 0,
    data: [42, 45, 44, 48, 50, 49, 52, 55, 60, 185, 58, 54, 52, 50, 48]
  }
};

export default function IoTConnectedSystemsHub() {
  const [activeTab, setActiveTab] = useState("architecture"); // architecture, mqtt_explorer, telemetry_cal, registry_timeline, rules_packets
  const [bilingual, setBilingual] = useState(false);

  // Tab 1: Architecture & Topology
  const [selectedTier, setSelectedTier] = useState(TIERS[0]);
  const [networkTopology, setNetworkTopology] = useState("STAR"); // STAR, MESH, HYBRID
  const [linkDistMeters, setLinkDistMeters] = useState(50);
  const [linkFreqMhz, setLinkFreqMhz] = useState(2400); // 2400 (Wi-Fi) or 868 (LoRa)
  const [linkTxPower, setLinkTxPower] = useState(14); // dBm

  // Tab 2: MQTT Explorer & Topic Designer
  const [mqttType, setMqttType] = useState("PUBLISH");
  const [mqttQoS, setMqttQoS] = useState(1);
  const [mqttRetain, setMqttRetain] = useState(0);
  const [mqttTopic, setMqttTopic] = useState("voltcore/mit/ece/lab304/node01/temperature");
  const [mqttPayloadText, setMqttPayloadText] = useState('{"temp": 28.4, "unit": "C"}');
  const [topicFilter, setTopicFilter] = useState("voltcore/mit/+/lab304/#");

  // Tab 3: Telemetry & Calibration
  const [selectedMetric, setSelectedMetric] = useState("Temperature");
  const [p1Raw, setP1Raw] = useState(0.0);
  const [p1Ref, setP1Ref] = useState(0.0);
  const [p2Raw, setP2Raw] = useState(3.3);
  const [p2Ref, setP2Ref] = useState(100.0);
  const [calRawVal, setCalRawVal] = useState(1.65);
  const [ambientTemp, setAmbientTemp] = useState(30.0);

  // Tab 4: Registry & Timeline
  const [devices] = useState(INITIAL_DEVICES);
  const [selectedDevice, setSelectedDevice] = useState(INITIAL_DEVICES[0]);

  // Tab 5: Rules & Packets
  const [ruleMetric, setRuleMetric] = useState("temperature");
  const [ruleOp, setRuleOp] = useState(">");
  const [ruleThreshold, setRuleThreshold] = useState(32.0);
  const [ruleAction, setRuleAction] = useState("RELAY_FAN_ON");
  const [ruleTarget, setRuleTarget] = useState("NODE-MIT-SMART-04");
  const [simTestVal, setSimTestVal] = useState(35.5);

  // Calculations: RF Link Budget
  const linkBudget = useMemo(() => {
    // FSPL (dB) = 20*log10(d) + 20*log10(f_MHz) - 27.55
    const fspl = 20.0 * Math.log10(linkDistMeters) + 20.0 * Math.log10(linkFreqMhz) - 27.55;
    const txGain = 2.0;
    const rxGain = 2.0;
    const rxSens = linkFreqMhz === 2400 ? -95.0 : -130.0; // LoRa has much higher sensitivity
    const rssi = linkTxPower + txGain + rxGain - fspl;
    const margin = rssi - rxSens;
    return {
      fspl: fspl.toFixed(1),
      rssi: rssi.toFixed(1),
      rxSens: rxSens.toFixed(1),
      margin: margin.toFixed(1),
      isViable: margin >= 0
    };
  }, [linkDistMeters, linkFreqMhz, linkTxPower]);

  // Calculations: MQTT Packet Hex Breakdown
  const mqttResult = useMemo(() => {
    const typeCodes = { CONNECT: 1, CONNACK: 2, PUBLISH: 3, PUBACK: 4, SUBSCRIBE: 8, PINGREQ: 12 };
    const code = typeCodes[mqttType] || 3;
    const b1 = (code << 4) | (mqttQoS << 1) | mqttRetain;
    const topicLen = mqttTopic.length;
    const payloadLen = mqttPayloadText.length;
    const varHeaderLen = mqttType === "PUBLISH" ? (2 + topicLen + (mqttQoS > 0 ? 2 : 0)) : 2;
    const totalRem = varHeaderLen + payloadLen;

    const handshake = [
      { step: 1, from: "Edge Node", to: "Broker", msg: `PUBLISH (QoS ${mqttQoS}, ${mqttRetain ? 'Retained' : 'Normal'})` }
    ];
    if (mqttQoS === 1) {
      handshake.push({ step: 2, from: "Broker", to: "Edge Node", msg: "PUBACK (Packet Identifier Confirmed)" });
    } else if (mqttQoS === 2) {
      handshake.push({ step: 2, from: "Broker", to: "Edge Node", msg: "PUBREC (Publish Received)" });
      handshake.push({ step: 3, from: "Edge Node", to: "Broker", msg: "PUBREL (Publish Release)" });
      handshake.push({ step: 4, from: "Broker", to: "Edge Node", msg: "PUBCOMP (Publish Complete)" });
    }

    return {
      b1Hex: `0x${b1.toString(16).toUpperCase().padStart(2, '0')}`,
      totalBytes: 1 + 1 + totalRem,
      remLen: totalRem,
      handshake
    };
  }, [mqttType, mqttQoS, mqttRetain, mqttTopic, mqttPayloadText]);

  // Calculations: Topic Wildcard Matching
  const topicMatchResult = useMemo(() => {
    const fParts = topicFilter.strip ? topicFilter.strip("/").split("/") : topicFilter.split("/").filter(Boolean);
    const tParts = mqttTopic.split("/").filter(Boolean);
    let matched = true;
    let i = 0;
    while (i < fParts.length) {
      const f = fParts[i];
      if (f === "#") {
        matched = true;
        break;
      }
      if (i >= tParts.length) {
        matched = false;
        break;
      }
      if (f !== "+" && f !== tParts[i]) {
        matched = false;
        break;
      }
      i++;
    }
    if (matched && fParts[fParts.length - 1] !== "#" && fParts.length !== tParts.length) {
      matched = false;
    }
    return matched;
  }, [topicFilter, mqttTopic]);

  // Calculations: Sensor Telemetry Anomaly Detection
  const telemetryStats = useMemo(() => {
    const stream = SENSOR_STREAMS[selectedMetric];
    const data = stream.data;
    const n = data.length;
    const mean = data.reduce((a, b) => a + b, 0) / n;
    const variance = data.reduce((a, b) => a + (b - mean) ** 2, 0) / (n - 1);
    const stdDev = Math.sqrt(variance);

    const anomalies = [];
    const zScores = data.map((val, idx) => {
      const z = stdDev > 0 ? (val - mean) / stdDev : 0;
      if (Math.abs(z) > 2.0 || val > stream.upper || val < stream.lower) {
        anomalies.push({ idx, val, z: z.toFixed(2) });
      }
      return z;
    });

    return {
      mean: mean.toFixed(2),
      stdDev: stdDev.toFixed(2),
      min: Math.min(...data).toFixed(1),
      max: Math.max(...data).toFixed(1),
      data,
      unit: stream.unit,
      anomalies,
      zScores
    };
  }, [selectedMetric]);

  // Calculations: Sensor Calibration
  const calResult = useMemo(() => {
    if (p2Raw === p1Raw) return null;
    const m = (p2Ref - p1Ref) / (p2Raw - p1Raw);
    const c = p1Ref - (m * p1Raw);
    const yLin = (m * calRawVal) + c;
    const tempDelta = ambientTemp - 25.0;
    const tempCoeff = 0.002;
    const compFactor = 1.0 - (tempCoeff * tempDelta);
    const yFinal = yLin * compFactor;
    return {
      slope: m.toFixed(4),
      offset: c.toFixed(4),
      linearVal: yLin.toFixed(2),
      compFactor: compFactor.toFixed(4),
      finalVal: yFinal.toFixed(2),
      err: (calRawVal - yFinal).toFixed(2)
    };
  }, [p1Raw, p1Ref, p2Raw, p2Ref, calRawVal, ambientTemp]);

  // Calculations: Automation Rule Evaluation
  const ruleEvaluation = useMemo(() => {
    let triggered = false;
    if (ruleOp === ">") triggered = simTestVal > ruleThreshold;
    else if (ruleOp === "<") triggered = simTestVal < ruleThreshold;
    else if (ruleOp === ">=") triggered = simTestVal >= ruleThreshold;
    else if (ruleOp === "<=") triggered = simTestVal <= ruleThreshold;
    else if (ruleOp === "==") triggered = simTestVal === ruleThreshold;
    return {
      triggered,
      actionPayload: triggered ? { action: ruleAction, target: ruleTarget, state: "DISPATCHED", timestamp: "JUST NOW" } : null
    };
  }, [ruleOp, simTestVal, ruleThreshold, ruleAction, ruleTarget]);

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6 text-slate-100">
      {/* Top Banner / Hero */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-cyan-950/80 to-slate-900 border border-cyan-500/30 p-6 shadow-2xl backdrop-blur-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <span className="px-2.5 py-1 text-xs font-mono font-semibold tracking-wider uppercase rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                Phase G • Features 271–280
              </span>
              <span className="text-xs text-slate-400 font-mono">
                Regulation 2023 | MIT Campus, Anna University
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white mt-2 tracking-tight">
              IoT & Connected Systems Engineering Hub
            </h1>
            <p className="text-sm text-slate-300 max-w-2xl mt-1">
              Interactive 5-tier IoT architecture modeling, MQTT 3.1.1 protocol inspection, multi-metric sensor telemetry, Z-score anomaly detection, and automated smart logic engines.
            </p>
          </div>

          <div className="flex items-center gap-3 self-start md:self-auto">
            <button
              onClick={() => setBilingual(!bilingual)}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-all ${
                bilingual
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                  : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'
              }`}
            >
              {bilingual ? 'Tamil Notes: ON (தமிழ்)' : 'Tamil Notes: OFF'}
            </button>
            <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-mono flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              SQLite WAL Active
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 mt-6 pt-4 border-t border-slate-800">
          {[
            { id: "architecture", label: "1. Architecture & Topology", icon: "🏛️" },
            { id: "mqtt_explorer", label: "2. MQTT & Topic Designer", icon: "📡" },
            { id: "telemetry_cal", label: "3. Telemetry & Calibration", icon: "📊" },
            { id: "registry_timeline", label: "4. Device Registry & Timeline", icon: "📱" },
            { id: "rules_packets", label: "5. Rules & Packet History", icon: "⚡" }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold tracking-wide transition-all ${
                activeTab === tab.id
                  ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-600/30 border border-cyan-400/30'
                  : 'bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-700/60 border border-slate-700/60'
              }`}
            >
              <span className="mr-1.5 opacity-80">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: Architecture & Topology (Features 271 & 280)                        */}
      {/* ========================================================================= */}
      {activeTab === "architecture" && (
        <div className="space-y-6">
          {/* Feature 271: 5-Tier Architecture Model */}
          <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  Feature 271: 5-Tier Industrial IoT Layered Architecture
                </h3>
                <p className="text-xs text-slate-400">
                  Standard architectural taxonomy for mission-critical edge-to-cloud telemetry systems.
                </p>
              </div>
              <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 px-3 py-1 rounded-full border border-cyan-800">
                Click any tier to inspect protocols & hardware
              </span>
            </div>

            {/* 5 Layer Horizontal Cards */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
              {TIERS.map(tier => (
                <button
                  key={tier.id}
                  onClick={() => setSelectedTier(tier)}
                  className={`p-4 rounded-xl text-left border transition-all ${
                    selectedTier.id === tier.id
                      ? 'bg-cyan-950/60 border-cyan-400 ring-2 ring-cyan-500/30 shadow-lg'
                      : 'bg-slate-800/40 border-slate-700/60 hover:bg-slate-800'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono font-bold text-cyan-400">TIER {tier.id}</span>
                    <span className="h-2 w-2 rounded-full bg-cyan-400"></span>
                  </div>
                  <div className="text-xs font-bold text-white mt-1">{tier.name}</div>
                  <div className="text-[10px] text-slate-400 font-sans mt-0.5">{tier.taName}</div>
                </button>
              ))}
            </div>

            {/* Selected Tier Inspector */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-2">
                <span className="text-sm font-bold text-cyan-300">
                  Tier {selectedTier.id}: {selectedTier.name} ({selectedTier.taName})
                </span>
                <span className="text-xs font-mono text-slate-400">Role: {selectedTier.role}</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                {bilingual ? selectedTier.taDesc : selectedTier.desc}
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Supported Protocols:</div>
                  <div className="flex flex-wrap gap-1.5 mt-1.5">
                    {selectedTier.protocols.map(pr => (
                      <span key={pr} className="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-mono text-cyan-300 border border-slate-700">
                        {pr}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Hardware Implementations:</div>
                  <div className="flex flex-wrap gap-1.5 mt-1.5">
                    {selectedTier.hardware.map(hw => (
                      <span key={hw} className="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-mono text-emerald-300 border border-slate-700">
                        {hw}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Feature 280: Network Topology & RF Link Budget */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-cyan-400">
                RF Link Budget Parameters
              </h3>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">Network Topology:</label>
                <div className="grid grid-cols-3 gap-1.5">
                  {["STAR", "MESH", "HYBRID"].map(t => (
                    <button
                      key={t}
                      onClick={() => setNetworkTopology(t)}
                      className={`py-1.5 text-xs font-medium rounded-lg border transition-all ${
                        networkTopology === t
                          ? 'bg-cyan-600 text-white border-cyan-400'
                          : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">Carrier Frequency:</label>
                <select
                  value={linkFreqMhz}
                  onChange={e => setLinkFreqMhz(parseFloat(e.target.value))}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                >
                  <option value={2400}>2.4 GHz (Wi-Fi / BLE / ZigBee)</option>
                  <option value={868}>868 MHz (LoRaWAN IN865 Band)</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">Distance (Meters): {linkDistMeters}m</label>
                <input
                  type="range"
                  min="5"
                  max="500"
                  step="5"
                  value={linkDistMeters}
                  onChange={e => setLinkDistMeters(parseInt(e.target.value))}
                  className="w-full accent-cyan-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">Tx Transmit Power: {linkTxPower} dBm</label>
                <input
                  type="range"
                  min="0"
                  max="20"
                  value={linkTxPower}
                  onChange={e => setLinkTxPower(parseInt(e.target.value))}
                  className="w-full accent-cyan-500"
                />
              </div>
            </div>

            {/* Topology SVG Visualizer & Budget Metrics */}
            <div className="lg:col-span-2 p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white">
                  Network Topology: {networkTopology} Architecture
                </h3>
                <span className={`text-xs font-mono font-bold px-2.5 py-0.5 rounded-full border ${
                  linkBudget.isViable
                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                    : 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                }`}>
                  Link Margin: {linkBudget.margin} dB ({linkBudget.isViable ? 'VIABLE' : 'UNREACHABLE'})
                </span>
              </div>

              {/* 4 Link Budget Metric Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Path Loss (FSPL)</div>
                  <div className="text-base font-extrabold text-cyan-300 mt-1">{linkBudget.fspl} dB</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Free-space attenuation</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Expected RSSI</div>
                  <div className="text-base font-extrabold text-purple-300 mt-1">{linkBudget.rssi} dBm</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Received signal strength</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Rx Sensitivity</div>
                  <div className="text-base font-extrabold text-amber-300 mt-1">{linkBudget.rxSens} dBm</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Receiver noise floor</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Link Margin</div>
                  <div className={`text-base font-extrabold mt-1 ${linkBudget.isViable ? 'text-emerald-400' : 'text-rose-400'}`}>
                    +{linkBudget.margin} dB
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Fade margin headroom</div>
                </div>
              </div>

              {/* Network Graph SVG */}
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <svg viewBox="0 0 550 160" className="w-full h-36 bg-slate-900 rounded-lg">
                  {/* Central Gateway Node */}
                  <circle cx="275" cy="80" r="16" fill="#0891b2" stroke="#38bdf8" strokeWidth="2.5" />
                  <text x="275" y="84" fill="#ffffff" fontSize="9" fontFamily="monospace" textAnchor="middle" fontWeight="bold">GW</text>

                  {/* Peripheral Nodes & Link Lines */}
                  {[
                    { x: 90, y: 40, label: "Node 1" },
                    { x: 90, y: 120, label: "Node 2" },
                    { x: 460, y: 40, label: "Node 3" },
                    { x: 460, y: 120, label: "Node 4" }
                  ].map((node, i) => (
                    <g key={i}>
                      {/* Connection Line */}
                      <line
                        x1="275"
                        y1="80"
                        x2={node.x}
                        y2={node.y}
                        stroke={linkBudget.isViable ? "#06b6d4" : "#f43f5e"}
                        strokeDasharray={networkTopology === "MESH" ? "4,4" : "none"}
                        strokeWidth="1.5"
                      />
                      {/* Node Circle */}
                      <circle cx={node.x} cy={node.y} r="12" fill="#1e293b" stroke="#06b6d4" strokeWidth="2" />
                      <text x={node.x} y={node.y + 4} fill="#e2e8f0" fontSize="8" fontFamily="monospace" textAnchor="middle">
                        N{i + 1}
                      </text>
                      <text x={node.x} y={node.y + 22} fill="#94a3b8" fontSize="8" fontFamily="monospace" textAnchor="middle">
                        {node.label}
                      </text>
                    </g>
                  ))}

                  {/* Mesh Cross-links if MESH selected */}
                  {networkTopology === "MESH" && (
                    <g stroke="#a855f7" strokeDasharray="2,2" strokeWidth="1">
                      <line x1="90" y1="40" x2="90" y2="120" />
                      <line x1="460" y1="40" x2="460" y2="120" />
                      <line x1="90" y1="40" x2="460" y2="40" />
                    </g>
                  )}
                </svg>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: MQTT Explorer & Topic Designer (Features 272 & 276)                 */}
      {/* ========================================================================= */}
      {activeTab === "mqtt_explorer" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Control Panel */}
            <div className="lg:col-span-1 p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-cyan-400">
                MQTT Packet Configuration
              </h3>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">Packet Control Type:</label>
                <select
                  value={mqttType}
                  onChange={e => setMqttType(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                >
                  <option value="PUBLISH">PUBLISH (Application Data)</option>
                  <option value="CONNECT">CONNECT (Client Handshake)</option>
                  <option value="SUBSCRIBE">SUBSCRIBE (Topic Registration)</option>
                  <option value="PUBACK">PUBACK (QoS 1 Acknowledgment)</option>
                  <option value="PINGREQ">PINGREQ (Keep-Alive Heartbeat)</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">Quality of Service (QoS):</label>
                <div className="grid grid-cols-3 gap-1.5">
                  {[0, 1, 2].map(q => (
                    <button
                      key={q}
                      onClick={() => setMqttQoS(q)}
                      className={`py-1.5 text-xs font-mono font-bold rounded-lg border transition-all ${
                        mqttQoS === q
                          ? 'bg-cyan-600 text-white border-cyan-400'
                          : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}
                    >
                      QoS {q}
                    </button>
                  ))}
                </div>
                <div className="text-[10px] text-slate-400 font-mono">
                  {mqttQoS === 0 && "At most once (Fire & Forget, 0 ACK)"}
                  {mqttQoS === 1 && "At least once (Requires PUBACK)"}
                  {mqttQoS === 2 && "Exactly once (4-way Handshake)"}
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">Retain Flag (RETAIN):</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => setMqttRetain(0)}
                    className={`py-1.5 text-xs font-medium rounded-lg border ${
                      mqttRetain === 0 ? 'bg-cyan-600 text-white border-cyan-400' : 'bg-slate-800 text-slate-400 border-slate-700'
                    }`}
                  >
                    Normal (0)
                  </button>
                  <button
                    onClick={() => setMqttRetain(1)}
                    className={`py-1.5 text-xs font-medium rounded-lg border ${
                      mqttRetain === 1 ? 'bg-cyan-600 text-white border-cyan-400' : 'bg-slate-800 text-slate-400 border-slate-700'
                    }`}
                  >
                    Retain (1)
                  </button>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">Topic Path:</label>
                <input
                  type="text"
                  value={mqttTopic}
                  onChange={e => setMqttTopic(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300">JSON Payload:</label>
                <textarea
                  rows={3}
                  value={mqttPayloadText}
                  onChange={e => setMqttPayloadText(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2 text-xs font-mono"
                />
              </div>
            </div>

            {/* Binary Inspector & QoS Handshake */}
            <div className="lg:col-span-2 p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-5">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white">
                  Feature 272: MQTT 3.1.1 Packet Header Binary Breakdown
                </h3>
                <span className="text-xs font-mono text-cyan-400">Fixed Header: {mqttResult.b1Hex}</span>
              </div>

              {/* Bit Breakdown of Byte 1 */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <div className="text-xs font-mono text-slate-400">Fixed Header Byte 1 Bitfields [7:0]:</div>
                <div className="grid grid-cols-4 gap-2 text-center font-mono">
                  <div className="p-2 rounded bg-cyan-950/40 border border-cyan-800">
                    <div className="text-[10px] text-cyan-400">Bits [7:4]</div>
                    <div className="text-xs font-bold text-white mt-0.5">Type: {mqttType}</div>
                  </div>
                  <div className="p-2 rounded bg-slate-800 border border-slate-700">
                    <div className="text-[10px] text-slate-400">Bit [3]</div>
                    <div className="text-xs font-bold text-white mt-0.5">DUP: 0</div>
                  </div>
                  <div className="p-2 rounded bg-purple-950/40 border border-purple-800">
                    <div className="text-[10px] text-purple-400">Bits [2:1]</div>
                    <div className="text-xs font-bold text-purple-200 mt-0.5">QoS: {mqttQoS}</div>
                  </div>
                  <div className="p-2 rounded bg-amber-950/40 border border-amber-800">
                    <div className="text-[10px] text-amber-400">Bit [0]</div>
                    <div className="text-xs font-bold text-amber-200 mt-0.5">RETAIN: {mqttRetain}</div>
                  </div>
                </div>
              </div>

              {/* QoS Handshake Step Sequence */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                <div className="text-xs font-mono text-slate-300 font-bold">
                  QoS {mqttQoS} Handshake Flow Timeline:
                </div>
                <div className="space-y-2">
                  {mqttResult.handshake.map(step => (
                    <div key={step.step} className="flex items-center gap-3 p-2 rounded-lg bg-slate-900 border border-slate-800 font-mono text-xs">
                      <span className="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold text-[10px]">
                        {step.step}
                      </span>
                      <span className="text-slate-400">{step.from} → {step.to}:</span>
                      <span className="text-emerald-400 font-semibold">{step.msg}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Feature 276: Topic Hierarchy & Wildcard Matcher */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">Feature 276: Wildcard Matcher ('+' single, '#' multi)</span>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                    topicMatchResult
                      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                      : 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                  }`}>
                    {topicMatchResult ? 'MATCH SUCCESS' : 'NO MATCH'}
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="text-[10px] font-mono text-slate-400">Subscription Pattern:</label>
                    <input
                      type="text"
                      value={topicFilter}
                      onChange={e => setTopicFilter(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 text-cyan-300 rounded p-1.5 text-xs font-mono mt-1"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] font-mono text-slate-400">Actual Publish Topic:</label>
                    <div className="text-xs font-mono text-slate-300 p-1.5 rounded bg-slate-900 border border-slate-800 truncate mt-1">
                      {mqttTopic}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: Telemetry & Calibration (Features 273 & 275)                        */}
      {/* ========================================================================= */}
      {activeTab === "telemetry_cal" && (
        <div className="space-y-6">
          {/* Feature 273: Sensor Data Dashboard with Z-score Anomaly Detection */}
          <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  Feature 273: Real-Time Telemetry Stream & Z-Score Anomaly Detector
                </h3>
                <p className="text-xs text-slate-400">
                  Statistical outlier detection flags readings deviating $|Z| &gt; 2.0$ from historical baseline.
                </p>
              </div>
              <div className="flex gap-1.5">
                {Object.keys(SENSOR_STREAMS).map(m => (
                  <button
                    key={m}
                    onClick={() => setSelectedMetric(m)}
                    className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-all ${
                      selectedMetric === m
                        ? 'bg-cyan-600 text-white border-cyan-400'
                        : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'
                    }`}
                  >
                    {m}
                  </button>
                ))}
              </div>
            </div>

            {/* Metric Statistics */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                <div className="text-[10px] font-mono text-slate-400 uppercase">Stream Mean (μ)</div>
                <div className="text-base font-extrabold text-cyan-300 mt-1">{telemetryStats.mean} {telemetryStats.unit}</div>
                <div className="text-[10px] text-slate-500 mt-0.5">Moving average</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                <div className="text-[10px] font-mono text-slate-400 uppercase">Std Deviation (σ)</div>
                <div className="text-base font-extrabold text-purple-300 mt-1">{telemetryStats.stdDev}</div>
                <div className="text-[10px] text-slate-500 mt-0.5">Sample dispersion</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                <div className="text-[10px] font-mono text-slate-400 uppercase">Min / Max Range</div>
                <div className="text-base font-extrabold text-emerald-400 mt-1">{telemetryStats.min} – {telemetryStats.max}</div>
                <div className="text-[10px] text-slate-500 mt-0.5">Peak excursions</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                <div className="text-[10px] font-mono text-slate-400 uppercase">Anomalies Detected</div>
                <div className={`text-base font-extrabold mt-1 ${telemetryStats.anomalies.length > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {telemetryStats.anomalies.length} Outliers
                </div>
                <div className="text-[10px] text-slate-500 mt-0.5">|Z| &gt; 2.0 or threshold</div>
              </div>
            </div>

            {/* Time-Series SVG with Outlier Highlight */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <span>Telemetry Waveform for {selectedMetric} ({telemetryStats.data.length} sample points)</span>
                <span className="text-rose-400 font-bold">Red Markers = Anomaly Detected</span>
              </div>
              <svg viewBox="0 0 650 120" className="w-full h-32 bg-slate-900 rounded-lg">
                {(() => {
                  const min = parseFloat(telemetryStats.min);
                  const max = parseFloat(telemetryStats.max);
                  const range = max - min || 1;
                  const pts = telemetryStats.data.map((val, idx) => {
                    const x = 30 + idx * 42;
                    const y = 100 - ((val - min) / range) * 80;
                    return { x, y, val, idx };
                  });
                  const pathD = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');

                  return (
                    <g>
                      {/* Grid Lines */}
                      <line x1="30" y1="20" x2="620" y2="20" stroke="#334155" strokeDasharray="2,2" strokeWidth="1" />
                      <line x1="30" y1="100" x2="620" y2="100" stroke="#334155" strokeDasharray="2,2" strokeWidth="1" />

                      {/* Continuous Trend Line */}
                      <path d={pathD} fill="none" stroke="#06b6d4" strokeWidth="2.5" />

                      {/* Data Point Circles */}
                      {pts.map(p => {
                        const isAnomaly = telemetryStats.anomalies.some(a => a.idx === p.idx);
                        return (
                          <g key={p.idx}>
                            <circle
                              cx={p.x}
                              cy={p.y}
                              r={isAnomaly ? 6 : 3}
                              fill={isAnomaly ? "#f43f5e" : "#38bdf8"}
                              stroke={isAnomaly ? "#ffffff" : "none"}
                              strokeWidth={isAnomaly ? 1.5 : 0}
                            />
                            {isAnomaly && (
                              <text x={p.x} y={p.y - 10} fill="#f43f5e" fontSize="9" fontFamily="monospace" textAnchor="middle" fontWeight="bold">
                                {p.val}
                              </text>
                            )}
                          </g>
                        );
                      })}
                    </g>
                  );
                })()}
              </svg>
            </div>
          </div>

          {/* Feature 275: Virtual Sensor Calibration Tool */}
          <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
            <div className="border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white">
                Feature 275: Virtual Sensor Calibration & Temperature Compensation Tool
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Solves gain and offset ($y = m \cdot x + c$) with real-time temperature coefficient drift correction ($y_{`comp`} = y [1 - \alpha (T - 25)]$).
              </p>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="space-y-1">
                <label className="text-xs font-mono text-slate-300">Point 1 Raw Input (V):</label>
                <input
                  type="number"
                  step="0.1"
                  value={p1Raw}
                  onChange={e => setP1Raw(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded p-1.5 text-xs font-mono"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-mono text-slate-300">Point 1 Ref Value:</label>
                <input
                  type="number"
                  step="1"
                  value={p1Ref}
                  onChange={e => setP1Ref(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded p-1.5 text-xs font-mono"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-mono text-slate-300">Point 2 Raw Input (V):</label>
                <input
                  type="number"
                  step="0.1"
                  value={p2Raw}
                  onChange={e => setP2Raw(parseFloat(e.target.value) || 3.3)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded p-1.5 text-xs font-mono"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-mono text-slate-300">Point 2 Ref Value:</label>
                <input
                  type="number"
                  step="1"
                  value={p2Ref}
                  onChange={e => setP2Ref(parseFloat(e.target.value) || 100)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded p-1.5 text-xs font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
              <div className="space-y-1">
                <label className="text-xs font-mono text-slate-300">Current Raw Sensor Input (V): {calRawVal} V</label>
                <input
                  type="range"
                  min="0"
                  max="3.3"
                  step="0.05"
                  value={calRawVal}
                  onChange={e => setCalRawVal(parseFloat(e.target.value))}
                  className="w-full accent-cyan-500"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-mono text-slate-300">Ambient Operating Temp: {ambientTemp} °C</label>
                <input
                  type="range"
                  min="10"
                  max="50"
                  step="1"
                  value={ambientTemp}
                  onChange={e => setAmbientTemp(parseFloat(e.target.value))}
                  className="w-full accent-cyan-500"
                />
              </div>
            </div>

            {calResult && (
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div className="space-y-1">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Calibrated Physical Output:</div>
                  <div className="text-xl font-bold font-mono text-emerald-400">
                    {calResult.finalVal} (Linear: {calResult.linearVal})
                  </div>
                  <div className="text-xs text-slate-400 font-mono">
                    Slope m = {calResult.slope} | Offset c = {calResult.offset}
                  </div>
                </div>
                <div className="text-xs font-mono text-slate-400 bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                  Temp Factor: {calResult.compFactor} (Offset Error: {calResult.err})
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: Device Registry & Timeline (Features 274 & 278)                    */}
      {/* ========================================================================= */}
      {activeTab === "registry_timeline" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Device Registry Grid */}
            <div className="lg:col-span-2 p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white">
                  Feature 274: IoT Hardware Device Registry (4 Nodes Active)
                </h3>
                <span className="text-xs font-mono text-cyan-400">Provisioned via SQLite WAL</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {devices.map(dev => (
                  <button
                    key={dev.nodeId}
                    onClick={() => setSelectedDevice(dev)}
                    className={`p-4 rounded-xl text-left border transition-all ${
                      selectedDevice.nodeId === dev.nodeId
                        ? 'bg-cyan-950/50 border-cyan-400 shadow-md ring-2 ring-cyan-500/20'
                        : 'bg-slate-800/40 border-slate-700/60 hover:bg-slate-800'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-white">{dev.nodeId}</span>
                      <span className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded ${
                        dev.status === "ONLINE"
                          ? 'bg-emerald-500/20 text-emerald-300'
                          : 'bg-amber-500/20 text-amber-300'
                      }`}>
                        {dev.status}
                      </span>
                    </div>
                    <div className="text-xs font-semibold text-cyan-300 mt-1">{dev.name}</div>
                    <div className="text-[10px] text-slate-400 font-mono mt-1">
                      Platform: {dev.platform} | IP: {dev.ip}
                    </div>
                    <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono mt-2 pt-2 border-t border-slate-700/50">
                      <span>Battery: {dev.battery}%</span>
                      <span>RSSI: {dev.rssi} dBm</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Selected Device Deep Inspector */}
            <div className="lg:col-span-1 p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-cyan-400">
                Node Specification Inspector
              </h3>
              <div className="space-y-2 text-xs font-mono">
                <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                  <span className="text-slate-400">Node ID:</span>
                  <div className="text-white font-bold mt-0.5">{selectedDevice.nodeId}</div>
                </div>
                <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                  <span className="text-slate-400">Hardware MAC:</span>
                  <div className="text-cyan-300 mt-0.5">{selectedDevice.mac}</div>
                </div>
                <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                  <span className="text-slate-400">Firmware Version:</span>
                  <div className="text-emerald-300 mt-0.5">{selectedDevice.firmware}</div>
                </div>
                <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                  <span className="text-slate-400">Attached Transducers:</span>
                  <div className="text-slate-200 mt-0.5">{selectedDevice.sensors.join(", ")}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Feature 278: Device Status Timeline Generator */}
          <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
            <div className="border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white">
                Feature 278: Lifecycle State Transition Waterfall ({selectedDevice.nodeId})
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Microsecond boot, association, broker handshake, and sleep entry sequence.
              </p>
            </div>

            <div className="space-y-2">
              {[
                { t: "+0.00s", state: "POWER_ON", desc: "Cold boot via POR (Power-on Reset)", status: "INFO" },
                { t: "+0.45s", state: "WIFI_CONNECTING", desc: "Associating with AP SSID 'MIT_ECE_IoT_LAB'", status: "PROGRESS" },
                { t: "+1.82s", state: "WIFI_CONNECTED", desc: `DHCP IP Acquired: ${selectedDevice.ip} (RSSI ${selectedDevice.rssi} dBm)`, status: "SUCCESS" },
                { t: "+2.10s", state: "MQTT_CONNECTING", desc: "Initiating TLS handshake to mqtt.voltcore.local:1883", status: "PROGRESS" },
                { t: "+2.38s", state: "MQTT_CONNECTED", desc: "CONNACK received (Return Code 0: Connection Accepted)", status: "SUCCESS" },
                { t: "+2.50s", state: "TELEMETRY_PUB", desc: "Published BME280 telemetry frame (QoS 1, PacketID=1042)", status: "SUCCESS" },
                { t: "+2.58s", state: "PUBACK_RECV", desc: "PUBACK acknowledged by broker in 80ms", status: "SUCCESS" },
                { t: "+3.00s", state: "DEEP_SLEEP_ENTER", desc: "Entering RTC Deep Sleep mode (Wake timer: 60s)", status: "SLEEP" }
              ].map((ev, i) => (
                <div key={i} className="flex items-center gap-3 p-2.5 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs">
                  <span className="text-slate-500 w-16">{ev.t}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-cyan-300 font-bold w-36 text-center">
                    {ev.state}
                  </span>
                  <span className="text-slate-300 flex-1">{ev.desc}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 5: Rules & Packet History (Features 277 & 279)                         */}
      {/* ========================================================================= */}
      {activeTab === "rules_packets" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Feature 279: Smart Automation Rule Engine */}
            <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white">
                  Feature 279: Conditional IF-THEN Automation Rule Engine
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Automated rule evaluation triggers physical actuators when metrics exceed thresholds.
                </p>
              </div>

              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                <div className="text-xs font-mono font-bold text-cyan-400">Rule Logic Formulation:</div>
                <div className="grid grid-cols-3 gap-2">
                  <div className="space-y-1">
                    <label className="text-[10px] font-mono text-slate-400">Metric:</label>
                    <select
                      value={ruleMetric}
                      onChange={e => setRuleMetric(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 text-white rounded p-1.5 text-xs font-mono"
                    >
                      <option value="temperature">Temperature (°C)</option>
                      <option value="humidity">Humidity (%)</option>
                      <option value="aqi">Air Quality (AQI)</option>
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-mono text-slate-400">Condition:</label>
                    <select
                      value={ruleOp}
                      onChange={e => setRuleOp(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 text-white rounded p-1.5 text-xs font-mono"
                    >
                      <option value=">">&gt; (Greater than)</option>
                      <option value="<">&lt; (Less than)</option>
                      <option value=">=">&gt;= (Greater or equal)</option>
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-mono text-slate-400">Threshold:</label>
                    <input
                      type="number"
                      step="0.5"
                      value={ruleThreshold}
                      onChange={e => setRuleThreshold(parseFloat(e.target.value) || 0)}
                      className="w-full bg-slate-800 border border-slate-700 text-white rounded p-1.5 text-xs font-mono"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-1">
                  <div className="space-y-1">
                    <label className="text-[10px] font-mono text-slate-400">Action Dispatched:</label>
                    <select
                      value={ruleAction}
                      onChange={e => setRuleAction(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 text-white rounded p-1.5 text-xs font-mono"
                    >
                      <option value="RELAY_FAN_ON">Activate Cooling Fan (Relay 1)</option>
                      <option value="VENT_EXHAUST">Open Exhaust Flap (Relay 2)</option>
                      <option value="ALARM_BUZZER">Trigger Safety Alarm (Buzzer)</option>
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-mono text-slate-400">Target Actuator Node:</label>
                    <input
                      type="text"
                      value={ruleTarget}
                      onChange={e => setRuleTarget(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 text-white rounded p-1.5 text-xs font-mono"
                    />
                  </div>
                </div>
              </div>

              {/* Live Rule Tester */}
              <div className="space-y-2">
                <label className="text-xs font-mono text-slate-300">
                  Simulate Live Telemetry Input ({ruleMetric}): {simTestVal}
                </label>
                <input
                  type="range"
                  min="15"
                  max="60"
                  step="0.5"
                  value={simTestVal}
                  onChange={e => setSimTestVal(parseFloat(e.target.value))}
                  className="w-full accent-cyan-500"
                />
              </div>

              {/* Evaluation Result */}
              <div className={`p-4 rounded-xl border flex items-center justify-between ${
                ruleEvaluation.triggered
                  ? 'bg-rose-950/40 border-rose-500/40 text-rose-200'
                  : 'bg-emerald-950/40 border-emerald-500/40 text-emerald-200'
              }`}>
                <div>
                  <div className="text-xs font-bold font-mono">
                    {ruleEvaluation.triggered ? 'RULE FIRED (ACTUATOR TRIGGERED)' : 'NORMAL STATE (NO ACTION)'}
                  </div>
                  <div className="text-[10px] font-mono mt-0.5">
                    {simTestVal} {ruleOp} {ruleThreshold} is {ruleEvaluation.triggered ? 'TRUE' : 'FALSE'}
                  </div>
                </div>
                {ruleEvaluation.triggered && (
                  <span className="px-2 py-1 rounded bg-rose-500/20 text-rose-300 font-mono text-xs font-bold border border-rose-500/40">
                    {ruleAction}
                  </span>
                )}
              </div>
            </div>

            {/* Feature 277: IoT Packet History Ledger */}
            <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white">
                  Feature 277: Real-Time IoT Telemetry Packet History Ledger
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Inspectable audit ledger of recent inbound and outbound MQTT telemetry packets.
                </p>
              </div>

              <div className="space-y-2 max-h-80 overflow-y-auto">
                {[
                  { id: 1045, node: "NODE-MIT-LAB304-01", topic: "voltcore/mit/lab304/ambient", qos: 1, rssi: -62, time: "19:42:01", data: "temp: 26.4°C, hum: 58%" },
                  { id: 1044, node: "NODE-MIT-LAB304-02", topic: "voltcore/mit/lab304/vibration", qos: 2, rssi: -55, time: "19:41:48", data: "accel: 0.04g, 120Hz" },
                  { id: 1043, node: "NODE-MIT-ROOF-03", topic: "voltcore/mit/roof/weather", qos: 0, rssi: -78, time: "19:41:20", data: "lux: 85k, wind: 4.2m/s" },
                  { id: 1042, node: "NODE-MIT-SMART-04", topic: "voltcore/mit/relay/status", qos: 1, rssi: -48, time: "19:40:55", data: "relay1: OFF, relay2: ON" },
                  { id: 1041, node: "NODE-MIT-LAB304-01", topic: "voltcore/mit/lab304/ambient", qos: 1, rssi: -63, time: "19:40:01", data: "temp: 26.3°C, hum: 58%" }
                ].map(pkt => (
                  <div key={pkt.id} className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs space-y-1">
                    <div className="flex items-center justify-between text-slate-400 text-[10px]">
                      <span>Packet #{pkt.id} • {pkt.node}</span>
                      <span>{pkt.time}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-cyan-300 font-semibold">{pkt.topic}</span>
                      <span className="text-slate-400 text-[10px]">QoS {pkt.qos} | {pkt.rssi} dBm</span>
                    </div>
                    <div className="text-emerald-400 text-[11px] truncate">
                      Payload: {pkt.data}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
