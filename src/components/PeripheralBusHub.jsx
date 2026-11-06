import React, { useState, useEffect, useMemo } from 'react';

// Preset Device Catalogs
const PROTOCOL_CONFIGS = {
  SPI: {
    modes: [
      { key: 'MODE_0', label: 'Mode 0 (CPOL=0, CPHA=0)', cpol: 0, cpha: 0, desc: 'Clock Idle LOW, Sample on Rising Edge' },
      { key: 'MODE_1', label: 'Mode 1 (CPOL=0, CPHA=1)', cpol: 0, cpha: 1, desc: 'Clock Idle LOW, Sample on Falling Edge' },
      { key: 'MODE_2', label: 'Mode 2 (CPOL=1, CPHA=0)', cpol: 1, cpha: 0, desc: 'Clock Idle HIGH, Sample on Falling Edge' },
      { key: 'MODE_3', label: 'Mode 3 (CPOL=1, CPHA=1)', cpol: 1, cpha: 1, desc: 'Clock Idle HIGH, Sample on Rising Edge' }
    ],
    devices: [
      {
        key: 'SPI_W25Q64_FLASH',
        name: 'Winbond W25Q64 (64Mb SPI Flash)',
        cmd: '0x9F (JEDEC ID)',
        tx_bytes: [0x9F, 0x00, 0x00, 0x00],
        rx_bytes: [0x00, 0xEF, 0x40, 0x17],
        default_mode: 'MODE_0',
        default_clk_khz: 1000.0
      },
      {
        key: 'SPI_MAX7219_LED',
        name: 'Maxim MAX7219 (LED Matrix)',
        cmd: '0x09 (Decode Mode)',
        tx_bytes: [0x09, 0xFF],
        rx_bytes: [0x00, 0x00],
        default_mode: 'MODE_0',
        default_clk_khz: 500.0
      },
      {
        key: 'SPI_MCP3008_ADC',
        name: 'Microchip MCP3008 (10-Bit ADC)',
        cmd: '0x01 (Start Bit Ch0)',
        tx_bytes: [0x01, 0x80, 0x00],
        rx_bytes: [0x00, 0x02, 0x8A],
        default_mode: 'MODE_0',
        default_clk_khz: 1000.0
      }
    ]
  },
  I2C: {
    speeds: [
      { key: 'STANDARD', label: 'Standard Mode (100 kHz)', freq_khz: 100.0, period_us: 10.0 },
      { key: 'FAST', label: 'Fast Mode (400 kHz)', freq_khz: 400.0, period_us: 2.5 },
      { key: 'FAST_PLUS', label: 'Fast Mode Plus (1.0 MHz)', freq_khz: 1000.0, period_us: 1.0 }
    ],
    devices: [
      {
        key: 'I2C_MPU6050',
        name: 'InvenSense MPU-6050 (6-Axis IMU)',
        addr_7bit: '0x68',
        reg_hex: '0x75',
        reg_name: 'WHO_AM_I',
        resp_hex: '0x68',
        is_read: true
      },
      {
        key: 'I2C_BMP280',
        name: 'Bosch BMP280 (Barometer)',
        addr_7bit: '0x76',
        reg_hex: '0xD0',
        reg_name: 'CHIP_ID',
        resp_hex: '0x58',
        is_read: true
      },
      {
        key: 'I2C_SSD1306_OLED',
        name: 'SSD1306 (128x64 OLED)',
        addr_7bit: '0x3C',
        reg_hex: '0x00',
        reg_name: 'COMMAND',
        resp_hex: '0xAF',
        is_read: false
      }
    ]
  },
  UART: {
    baud_rates: [9600, 19200, 38400, 57600, 115200],
    parities: ['NONE', 'EVEN', 'ODD'],
    devices: [
      {
        key: 'UART_GPS_NMEA',
        name: 'u-blox NEO-6M (GPS Receiver)',
        baud: 9600,
        parity: 'NONE',
        payload: '$GPGGA'
      },
      {
        key: 'UART_ESP32_AT',
        name: 'ESP32 Wi-Fi Node (AT Commands)',
        baud: 115200,
        parity: 'NONE',
        payload: 'AT+GMR'
      },
      {
        key: 'UART_HC05_BT',
        name: 'HC-05 Bluetooth Serial',
        baud: 38400,
        parity: 'NONE',
        payload: 'AT+NAME?'
      }
    ]
  }
};

// Bilingual Guidance Dictionary
const DICTIONARY = {
  en: {
    badge: 'PHASE 36 ENTERPRISE',
    title: 'Peripheral Bus Protocols Analyzer',
    subtitle: 'Interactive SPI (Modes 0-3), I2C (7-Bit/ACK), and UART Baud Framing Timing Analyzer',
    author: 'Platform Lead: Ashok Kumar A (2023MITEC042) • MIT Campus, Anna University',
    spiTab: 'SPI (Full-Duplex)',
    i2cTab: 'I2C (2-Wire Bus)',
    uartTab: 'UART (Async Serial)',
    configHeader: 'Protocol Configuration & Peripheral Preset',
    targetDevice: 'Target Peripheral Device',
    spiMode: 'SPI Mode (CPOL / CPHA)',
    clockSpeed: 'Clock / Baud Frequency',
    packetInspectHeader: 'Transaction Protocol Frame Breakdown',
    waveformHeader: 'Digital Waveform & Timing Diagram',
    exportCsv: 'Export Bus CSV',
    cpolDesc: 'CPOL (Clock Polarity): Determines if SCLK idles LOW (0) or HIGH (1).',
    cphaDesc: 'CPHA (Clock Phase): Determines if data is sampled on the first or second clock transition.',
    i2cOpenDrain: 'Open-Drain & Pull-Up: SCL and SDA lines require external pull-up resistors (typically 4.7kΩ) for bidirectional bus floating.',
    uartFraming: 'UART Framing: Start bit (LOW) synchronizes the local clock; 8 data bits follow LSB first with optional parity.'
  },
  ta: {
    badge: 'கட்டம் 36 நிறுவனம்',
    title: 'புற சாதன பேருந்து நெறிமுறை ஆய்வாளர்',
    subtitle: 'SPI (முறைகள் 0-3), I2C (7-பிட் முகவரி/ACK), மற்றும் UART தொடர் நேர பகுப்பாய்வி',
    author: 'தள ஒருங்கிணைப்பாளர்: அசோக் குமார் A (2023MITEC042) • MIT வளாகம், அண்ணா பல்கலைக்கழகம்',
    spiTab: 'SPI (முழு டூப்ளக்ஸ்)',
    i2cTab: 'I2C (இரு-கம்பி பேருந்து)',
    uartTab: 'UART (ஒத்திசைவற்ற தொடர்)',
    configHeader: 'நெறிமுறை கட்டமைப்பு மற்றும் சாதன அமைவு',
    targetDevice: 'இலக்கு புற சாதனம்',
    spiMode: 'SPI பயன்முறை (CPOL / CPHA)',
    clockSpeed: 'கடிகாரம் / போட் அதிர்வெண்',
    packetInspectHeader: 'பரிவர்த்தனை நெறிமுறை அடுக்கு விவரங்கள்',
    waveformHeader: 'டிஜிட்டல் அலைவடிவம் மற்றும் நேர வரைபடம்',
    exportCsv: 'CSV கோப்பாக பதிவிறக்கு',
    cpolDesc: 'CPOL: கடிகாரம் அமைதியில் இருக்கும் போது LOW (0) அல்லது HIGH (1) ஆக இருப்பதை தீர்மானிக்கிறது.',
    cphaDesc: 'CPHA: தரவு முதல் அல்லது இரண்டாவது கடிகார விளிம்பில் மாதிரி எடுக்கப்படுகிறதா என்பதை தீர்மானிக்கிறது.',
    i2cOpenDrain: 'திறந்த வடிகால்: SCL மற்றும் SDA கோடுகளுக்கு 4.7kΩ இழுக்கும் மின்தடைகள் (Pull-Up) தேவைப்படுகின்றன.',
    uartFraming: 'UART கட்டமைப்பு: தொடக்க பிட் (0) உள்ளூர் கடிகாரத்தை ஒத்திசைக்கிறது; 8 தரவு பிட்கள் LSB முதலில் அனுப்பப்படும்.'
  }
};

export default function PeripheralBusHub() {
  const [lang, setLang] = useState('en');
  const t = DICTIONARY[lang];

  // Active Protocol Tab
  const [activeTab, setActiveTab] = useState('SPI'); // 'SPI', 'I2C', 'UART'

  // SPI State
  const [spiMode, setSpiMode] = useState('MODE_0');
  const [spiDeviceKey, setSpiDeviceKey] = useState('SPI_W25Q64_FLASH');
  const [spiClockKhz, setSpiClockKhz] = useState(1000.0);

  // I2C State
  const [i2cDeviceKey, setI2cDeviceKey] = useState('I2C_MPU6050');
  const [i2cSpeedMode, setI2cSpeedMode] = useState('STANDARD');
  const [i2cIsRead, setI2cIsRead] = useState(true);

  // UART State
  const [uartDeviceKey, setUartDeviceKey] = useState('UART_ESP32_AT');
  const [uartBaud, setUartBaud] = useState(115200);
  const [uartParity, setUartParity] = useState('NONE');
  const [uartPayload, setUartPayload] = useState('AT+GMR');

  // Simulation Results
  const [simulationResult, setSimulationResult] = useState(null);
  const [hoverSample, setHoverSample] = useState(null);

  // Active Device Lookups
  const activeSpiDev = PROTOCOL_CONFIGS.SPI.devices.find(d => d.key === spiDeviceKey);
  const activeI2cDev = PROTOCOL_CONFIGS.I2C.devices.find(d => d.key === i2cDeviceKey);
  const activeUartDev = PROTOCOL_CONFIGS.UART.devices.find(d => d.key === uartDeviceKey);

  // Client-Side Deterministic Fallback Math Engine
  const computeClientSimulation = () => {
    if (activeTab === 'SPI') {
      const modeObj = PROTOCOL_CONFIGS.SPI.modes.find(m => m.key === spiMode);
      const cpol = modeObj.cpol;
      const cpha = modeObj.cpha;
      const tHalfUs = Number(((1000.0 / spiClockKhz) / 2.0).toFixed(3));
      const samples = [];
      let curTime = 0.0;
      let sIdx = 0;

      // IDLE
      samples.push({
        sample_index: sIdx++, time_us: curTime,
        line1_name: 'CS', line1_val: 1,
        line2_name: 'SCLK', line2_val: cpol,
        line3_name: 'MOSI', line3_val: 0,
        line4_name: 'MISO', line4_val: 0,
        packet_annotation: 'IDLE'
      });
      curTime += tHalfUs;

      // CS ASSERT
      samples.push({
        sample_index: sIdx++, time_us: curTime,
        line1_name: 'CS', line1_val: 0,
        line2_name: 'SCLK', line2_val: cpol,
        line3_name: 'MOSI', line3_val: 0,
        line4_name: 'MISO', line4_val: 0,
        packet_annotation: 'CS_ASSERT'
      });
      curTime += tHalfUs;

      const txBytes = activeSpiDev ? activeSpiDev.tx_bytes : [0x9F, 0x00];
      const rxBytes = activeSpiDev ? activeSpiDev.rx_bytes : [0x00, 0xEF];

      txBytes.forEach((tb, bIdx) => {
        const rb = rxBytes[bIdx] || 0x00;
        for (let bit = 7; bit >= 0; bit--) {
          const mosi = (tb >> bit) & 1;
          const miso = (rb >> bit) & 1;
          const clk1 = cpha === 0 ? 1 - cpol : cpol;
          const clk2 = cpha === 0 ? cpol : 1 - cpol;

          samples.push({
            sample_index: sIdx++, time_us: Number(curTime.toFixed(3)),
            line1_name: 'CS', line1_val: 0,
            line2_name: 'SCLK', line2_val: clk1,
            line3_name: 'MOSI', line3_val: mosi,
            line4_name: 'MISO', line4_val: miso,
            packet_annotation: `B${bIdx}[${bit}]`
          });
          curTime += tHalfUs;

          samples.push({
            sample_index: sIdx++, time_us: Number(curTime.toFixed(3)),
            line1_name: 'CS', line1_val: 0,
            line2_name: 'SCLK', line2_val: clk2,
            line3_name: 'MOSI', line3_val: mosi,
            line4_name: 'MISO', line4_val: miso,
            packet_annotation: `B${bIdx}[${bit}]`
          });
          curTime += tHalfUs;
        }
      });

      // CS DEASSERT
      samples.push({
        sample_index: sIdx++, time_us: Number(curTime.toFixed(3)),
        line1_name: 'CS', line1_val: 1,
        line2_name: 'SCLK', line2_val: cpol,
        line3_name: 'MOSI', line3_val: 0,
        line4_name: 'MISO', line4_val: 0,
        packet_annotation: 'CS_DEASSERT'
      });

      return {
        protocol: 'SPI',
        mode: spiMode,
        device_name: activeSpiDev ? activeSpiDev.name : 'SPI Flash',
        clock_khz: spiClockKhz,
        packet_steps: [
          { stage: 'CS_ASSERT', label: 'CS Active LOW', color: 'bg-rose-950/80 text-rose-300 border-rose-500/40' },
          { stage: 'MOSI_CMD', label: `MOSI: 0x${txBytes[0].toString(16).toUpperCase()}`, color: 'bg-cyan-950/80 text-cyan-300 border-cyan-500/40' },
          { stage: 'MISO_RESP', label: `MISO: ${rxBytes.map(b => '0x' + b.toString(16).toUpperCase()).join(' ')}`, color: 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40' },
          { stage: 'CS_DEASSERT', label: 'CS Idle HIGH', color: 'bg-slate-800 text-slate-300 border-slate-700' }
        ],
        total_duration_us: Number(curTime.toFixed(2)),
        samples: samples.slice(0, 48)
      };
    } else if (activeTab === 'I2C') {
      const speedObj = PROTOCOL_CONFIGS.I2C.speeds.find(s => s.key === i2cSpeedMode);
      const tClkUs = speedObj ? speedObj.period_us : 10.0;
      const tQtr = Number((tClkUs / 4.0).toFixed(3));
      const samples = [];
      let curTime = 0.0;
      let sIdx = 0;

      const push = (scl, sda, annot) => {
        samples.push({
          sample_index: sIdx++, time_us: Number(curTime.toFixed(3)),
          line1_name: 'SCL', line1_val: scl,
          line2_name: 'SDA', line2_val: sda,
          packet_annotation: annot
        });
        curTime += tQtr;
      };

      // IDLE
      push(1, 1, 'IDLE');
      // START
      push(1, 0, 'START');
      push(0, 0, 'START_HOLD');

      const addr = activeI2cDev ? parseInt(activeI2cDev.addr_7bit, 16) : 0x68;
      const addrByte = (addr << 1) | 0;

      // 7-Bit Address + Write Bit
      for (let bit = 7; bit >= 0; bit--) {
        const v = (addrByte >> bit) & 1;
        push(0, v, `ADDR[${bit}]`);
        push(1, v, `ADDR[${bit}]`);
        push(1, v, `ADDR[${bit}]`);
        push(0, v, `ADDR[${bit}]`);
      }
      // ACK 1
      push(0, 0, 'ACK_1');
      push(1, 0, 'ACK_1');
      push(0, 0, 'ACK_1');

      // Register Byte
      const reg = activeI2cDev ? parseInt(activeI2cDev.reg_hex, 16) : 0x75;
      for (let bit = 7; bit >= 0; bit--) {
        const v = (reg >> bit) & 1;
        push(0, v, `REG[${bit}]`);
        push(1, v, `REG[${bit}]`);
        push(1, v, `REG[${bit}]`);
        push(0, v, `REG[${bit}]`);
      }
      // ACK 2
      push(0, 0, 'ACK_2');
      push(1, 0, 'ACK_2');
      push(0, 0, 'ACK_2');

      // STOP
      push(0, 0, 'PREP_STOP');
      push(1, 0, 'SCL_STOP');
      push(1, 1, 'STOP');

      return {
        protocol: 'I2C',
        speed_mode: i2cSpeedMode,
        device_name: activeI2cDev ? activeI2cDev.name : 'MPU6050',
        clock_khz: speedObj.freq_khz,
        packet_steps: [
          { stage: 'START', label: 'START', color: 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40' },
          { stage: 'ADDR', label: `ADDR: ${activeI2cDev ? activeI2cDev.addr_7bit : '0x68'} [W]`, color: 'bg-purple-950/80 text-purple-300 border-purple-500/40' },
          { stage: 'ACK1', label: 'ACK (0)', color: 'bg-emerald-950/80 text-emerald-400 border-emerald-500/40' },
          { stage: 'REG', label: `REG: ${activeI2cDev ? activeI2cDev.reg_hex : '0x75'}`, color: 'bg-amber-950/80 text-amber-300 border-amber-500/40' },
          { stage: 'ACK2', label: 'ACK (0)', color: 'bg-emerald-950/80 text-emerald-400 border-emerald-500/40' },
          { stage: 'STOP', label: 'STOP', color: 'bg-slate-800 text-slate-300 border-slate-700' }
        ],
        total_duration_us: Number(curTime.toFixed(2)),
        samples: samples.slice(0, 48)
      };
    } else {
      // UART
      const tBitUs = Number((1000000.0 / uartBaud).toFixed(3));
      const tQtr = Number((tBitUs / 4.0).toFixed(3));
      const samples = [];
      let curTime = 0.0;
      let sIdx = 0;

      const push = (tx, annot) => {
        samples.push({
          sample_index: sIdx++, time_us: Number(curTime.toFixed(3)),
          line1_name: 'TX', line1_val: tx,
          line2_name: 'RX', line2_val: 1,
          packet_annotation: annot
        });
        curTime += tQtr;
      };

      // IDLE
      for (let i = 0; i < 4; i++) push(1, 'IDLE');

      const chars = uartPayload ? uartPayload.split('') : ['O', 'K'];
      chars.slice(0, 3).forEach((ch, cIdx) => {
        const code = ch.charCodeAt(0);
        // START BIT (0)
        for (let i = 0; i < 4; i++) push(0, `START (${ch})`);
        // 8 Data Bits (LSB first)
        for (let bit = 0; bit < 8; bit++) {
          const v = (code >> bit) & 1;
          for (let i = 0; i < 4; i++) push(v, `${ch}[${bit}]=${v}`);
        }
        // STOP BIT (1)
        for (let i = 0; i < 4; i++) push(1, 'STOP');
      });

      return {
        protocol: 'UART',
        baud_rate: uartBaud,
        device_name: activeUartDev ? activeUartDev.name : 'ESP32 Wi-Fi',
        packet_steps: chars.map((ch, idx) => ({
          stage: `CHAR_${idx}`,
          label: `'${ch}' (0x${ch.charCodeAt(0).toString(16).toUpperCase()})`,
          color: 'bg-cyan-950/80 text-cyan-300 border-cyan-500/40'
        })),
        total_duration_us: Number(curTime.toFixed(2)),
        samples: samples.slice(0, 48)
      };
    }
  };

  // Run simulation upon parameter updates
  useEffect(() => {
    handleRunSimulation();
  }, [activeTab, spiMode, spiDeviceKey, spiClockKhz, i2cDeviceKey, i2cSpeedMode, i2cIsRead, uartDeviceKey, uartBaud, uartParity, uartPayload]);

  const handleRunSimulation = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1200);

      const resp = await fetch('/api/peripheral-bus/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({
          protocol: activeTab,
          mode_key: spiMode,
          clock_khz: spiClockKhz,
          device_name: activeTab === 'SPI' ? activeSpiDev.name : (activeTab === 'I2C' ? activeI2cDev.name : activeUartDev.name),
          slave_addr_7bit: activeI2cDev ? activeI2cDev.addr_7bit : '0x68',
          reg_addr_hex: activeI2cDev ? activeI2cDev.reg_hex : '0x75',
          is_read: i2cIsRead,
          data_byte_hex: activeI2cDev ? activeI2cDev.resp_hex : '0x68',
          speed_mode: i2cSpeedMode,
          baud_rate: uartBaud,
          tx_payload: uartPayload,
          parity: uartParity,
          stop_bits: 1,
          student_id: '2023MITEC042'
        })
      });
      clearTimeout(timeoutId);

      if (resp.ok) {
        const data = await resp.json();
        setSimulationResult({
          ...data,
          samples: data.waveform_samples || []
        });
      } else {
        setSimulationResult(computeClientSimulation());
      }
    } catch {
      setSimulationResult(computeClientSimulation());
    }
  };

  // Export CSV Action
  const handleExportCsv = () => {
    if (!simulationResult || !simulationResult.samples) return;
    let csvContent = 'Sample,Time_us,Line1_Name,Line1_Val,Line2_Name,Line2_Val,Packet_Annotation\n';
    simulationResult.samples.forEach(s => {
      csvContent += `${s.sample_index},${s.time_us},${s.line1_name},${s.line1_val},${s.line2_name},${s.line2_val},"${s.packet_annotation}"\n`;
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `voltcore_bus_${activeTab.toLowerCase()}_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 font-mono text-slate-200">
      
      {/* Top Banner Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-[#020813]/90 border border-emerald-500/30 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-emerald-700 flex items-center justify-center text-xl shadow-lg">
            🔌
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                {t.badge}
              </span>
              <h2 className="text-lg font-bold text-white tracking-wide font-sans">{t.title}</h2>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">{t.subtitle}</p>
          </div>
        </div>

        {/* Language & Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setLang(l => l === 'en' ? 'ta' : 'en')}
            className="px-3 py-1.5 text-xs font-bold rounded-xl bg-slate-800 hover:bg-slate-700 text-amber-400 border border-amber-500/30 transition-all"
            title="Toggle Tamil / English"
          >
            🌐 {lang === 'en' ? 'தமிழ்' : 'English'}
          </button>
          <button
            onClick={handleExportCsv}
            className="px-3 py-1.5 text-xs font-bold rounded-xl bg-emerald-950/60 hover:bg-emerald-900/80 text-emerald-300 border border-emerald-500/40 transition-all flex items-center gap-1.5"
          >
            <span>📥</span>
            <span>{t.exportCsv}</span>
          </button>
        </div>
      </div>

      {/* Protocol Selection Tabs */}
      <div className="flex rounded-2xl bg-slate-900/80 p-1.5 border border-slate-800 gap-2">
        <button
          onClick={() => setActiveTab('SPI')}
          className={`flex-1 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            activeTab === 'SPI'
              ? 'bg-gradient-to-r from-emerald-600 to-teal-700 text-white shadow-lg'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          <span>⚡</span>
          <span>{t.spiTab}</span>
        </button>

        <button
          onClick={() => setActiveTab('I2C')}
          className={`flex-1 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            activeTab === 'I2C'
              ? 'bg-gradient-to-r from-cyan-600 to-blue-700 text-white shadow-lg'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          <span>🔄</span>
          <span>{t.i2cTab}</span>
        </button>

        <button
          onClick={() => setActiveTab('UART')}
          className={`flex-1 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            activeTab === 'UART'
              ? 'bg-gradient-to-r from-amber-600 to-orange-700 text-white shadow-lg'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          <span>📶</span>
          <span>{t.uartTab}</span>
        </button>
      </div>

      {/* Protocol Specific Configuration */}
      <div className="p-6 rounded-2xl bg-[#020813]/85 border border-slate-800 shadow-lg space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-sm font-bold text-emerald-400 flex items-center gap-2">
            <span>⚙️</span>
            <span>{t.configHeader}</span>
          </h3>
          <span className="text-[11px] text-slate-400">{t.author}</span>
        </div>

        {/* SPI Controls */}
        {activeTab === 'SPI' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300">{t.targetDevice}</label>
              <select
                value={spiDeviceKey}
                onChange={(e) => setSpiDeviceKey(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-emerald-500"
              >
                {PROTOCOL_CONFIGS.SPI.devices.map(dev => (
                  <option key={dev.key} value={dev.key}>
                    {dev.name}
                  </option>
                ))}
              </select>
              <span className="text-[10px] text-slate-400 block">
                Command: {activeSpiDev ? activeSpiDev.cmd : 'JEDEC ID'}
              </span>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300">{t.spiMode}</label>
              <select
                value={spiMode}
                onChange={(e) => setSpiMode(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-emerald-500"
              >
                {PROTOCOL_CONFIGS.SPI.modes.map(m => (
                  <option key={m.key} value={m.key}>
                    {m.label}
                  </option>
                ))}
              </select>
              <span className="text-[10px] text-emerald-400 block">
                {PROTOCOL_CONFIGS.SPI.modes.find(m => m.key === spiMode)?.desc}
              </span>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-xs">
                <label className="font-bold text-slate-300">{t.clockSpeed}</label>
                <span className="text-emerald-400 font-bold">{spiClockKhz} kHz</span>
              </div>
              <input
                type="range"
                min="100"
                max="5000"
                step="100"
                value={spiClockKhz}
                onChange={(e) => setSpiClockKhz(parseFloat(e.target.value))}
                className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
              />
              <div className="flex justify-between text-[10px] text-slate-500">
                <span>100 kHz</span>
                <span>1 MHz</span>
                <span>5 MHz</span>
              </div>
            </div>
          </div>
        )}

        {/* I2C Controls */}
        {activeTab === 'I2C' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300">{t.targetDevice}</label>
              <select
                value={i2cDeviceKey}
                onChange={(e) => setI2cDeviceKey(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-cyan-500"
              >
                {PROTOCOL_CONFIGS.I2C.devices.map(dev => (
                  <option key={dev.key} value={dev.key}>
                    {dev.name} ({dev.addr_7bit})
                  </option>
                ))}
              </select>
              <span className="text-[10px] text-slate-400 block">
                Register: {activeI2cDev ? `${activeI2cDev.reg_name} (${activeI2cDev.reg_hex})` : 'WHO_AM_I'}
              </span>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300">I2C Speed Mode</label>
              <select
                value={i2cSpeedMode}
                onChange={(e) => setI2cSpeedMode(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-cyan-500"
              >
                {PROTOCOL_CONFIGS.I2C.speeds.map(s => (
                  <option key={s.key} value={s.key}>
                    {s.label}
                  </option>
                ))}
              </select>
              <span className="text-[10px] text-cyan-400 block">
                Pull-Up Bus Margin: 4.7 kΩ Nominal
              </span>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300">Transaction Mode</label>
              <div className="flex rounded-xl bg-slate-900 p-1 border border-slate-700">
                <button
                  onClick={() => setI2cIsRead(true)}
                  className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-all ${
                    i2cIsRead ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Read (R/W = 1)
                </button>
                <button
                  onClick={() => setI2cIsRead(false)}
                  className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-all ${
                    !i2cIsRead ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Write (R/W = 0)
                </button>
              </div>
              <span className="text-[10px] text-slate-400 block">
                Payload Response: {activeI2cDev ? activeI2cDev.resp_hex : '0x68'}
              </span>
            </div>
          </div>
        )}

        {/* UART Controls */}
        {activeTab === 'UART' && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300">{t.targetDevice}</label>
              <select
                value={uartDeviceKey}
                onChange={(e) => {
                  setUartDeviceKey(e.target.value);
                  const dev = PROTOCOL_CONFIGS.UART.devices.find(d => d.key === e.target.value);
                  if (dev) {
                    setUartBaud(dev.baud);
                    setUartPayload(dev.payload);
                  }
                }}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-amber-500"
              >
                {PROTOCOL_CONFIGS.UART.devices.map(dev => (
                  <option key={dev.key} value={dev.key}>
                    {dev.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300">Baud Rate (bps)</label>
              <select
                value={uartBaud}
                onChange={(e) => setUartBaud(parseInt(e.target.value))}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-amber-500"
              >
                {PROTOCOL_CONFIGS.UART.baud_rates.map(b => (
                  <option key={b} value={b}>
                    {b} bps ({(1000000 / b).toFixed(2)} µs/bit)
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300">Parity</label>
              <select
                value={uartParity}
                onChange={(e) => setUartParity(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-amber-500"
              >
                {PROTOCOL_CONFIGS.UART.parities.map(p => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300">Payload String</label>
              <input
                type="text"
                value={uartPayload}
                onChange={(e) => setUartPayload(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-amber-500 font-mono"
                placeholder="AT..."
              />
            </div>
          </div>
        )}

      </div>

      {/* Packet Inspection Protocol Frames Breakdown */}
      {simulationResult && simulationResult.packet_steps && (
        <div className="p-5 rounded-2xl bg-[#020813]/90 border border-slate-800 shadow-xl space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <h4 className="text-xs font-bold text-slate-300 flex items-center gap-2">
              <span>🔍</span>
              <span>{t.packetInspectHeader} ({simulationResult.device_name})</span>
            </h4>
            <span className="text-[11px] text-emerald-400 font-bold">
              Total Duration: {simulationResult.total_duration_us} µs
            </span>
          </div>

          <div className="flex items-center gap-2 overflow-x-auto py-2">
            {simulationResult.packet_steps.map((step, idx) => (
              <div
                key={idx}
                className={`px-3 py-1.5 rounded-xl border text-xs font-bold whitespace-nowrap flex items-center gap-1.5 shadow-sm ${
                  step.color || 'bg-slate-800 text-slate-200 border-slate-700'
                }`}
              >
                <span>{step.label || step.stage}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Digital Waveform Timing Canvas */}
      <div className="p-6 rounded-2xl bg-[#020813]/90 border border-slate-800 shadow-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h4 className="text-xs font-bold text-emerald-400 flex items-center gap-2">
            <span>📈</span>
            <span>{t.waveformHeader}</span>
          </h4>
          {hoverSample && (
            <div className="text-xs font-bold text-amber-400 flex items-center gap-3">
              <span>Time: {hoverSample.time_us} µs</span>
              <span>Annot: {hoverSample.packet_annotation}</span>
            </div>
          )}
        </div>

        {/* SVG Waveform Rendering */}
        {simulationResult && simulationResult.samples && (
          <div className="overflow-x-auto border border-slate-800 rounded-xl bg-[#010611] p-4 select-none">
            {(() => {
              const sampleWidth = 24;
              const totalSvgWidth = Math.max(760, simulationResult.samples.length * sampleWidth + 100);
              const labelWidth = 90;

              // Identify active channels based on protocol
              const channels = activeTab === 'SPI'
                ? [
                    { name: 'CS', color: '#f43f5e', key: 'line1_val' },
                    { name: 'SCLK', color: '#10b981', key: 'line2_val' },
                    { name: 'MOSI', color: '#38bdf8', key: 'line3_val' },
                    { name: 'MISO', color: '#a855f7', key: 'line4_val' }
                  ]
                : activeTab === 'I2C'
                ? [
                    { name: 'SCL', color: '#10b981', key: 'line1_val' },
                    { name: 'SDA', color: '#38bdf8', key: 'line2_val' }
                  ]
                : [
                    { name: 'TX', color: '#f59e0b', key: 'line1_val' },
                    { name: 'RX', color: '#10b981', key: 'line2_val' }
                  ];

              const rowHeight = 44;
              const totalHeight = channels.length * rowHeight + 35;

              return (
                <svg
                  width={totalSvgWidth}
                  height={totalHeight}
                  className="font-mono text-[10px]"
                  style={{ minWidth: '100%' }}
                >
                  {/* Grid Lines */}
                  {simulationResult.samples.map((s, i) => {
                    const x = labelWidth + i * sampleWidth;
                    return (
                      <g key={i}>
                        <line
                          x1={x}
                          y1={20}
                          x2={x}
                          y2={totalHeight - 10}
                          stroke="#1e293b"
                          strokeWidth="1"
                          strokeDasharray="2,4"
                        />
                        {i % 4 === 0 && (
                          <text x={x} y={14} fill="#64748b" textAnchor="middle" fontSize="9">
                            {s.time_us}µs
                          </text>
                        )}
                      </g>
                    );
                  })}

                  {/* Render Channels */}
                  {channels.map((ch, chIdx) => {
                    const rowY = 24 + chIdx * rowHeight;
                    const highY = rowY + 6;
                    const lowY = rowY + rowHeight - 12;

                    return (
                      <g key={ch.name}>
                        {/* Channel Label */}
                        <rect
                          x={0}
                          y={rowY}
                          width={labelWidth - 8}
                          height={rowHeight - 6}
                          fill="#0f172a"
                          rx={4}
                        />
                        <text
                          x={8}
                          y={rowY + (rowHeight / 2)}
                          fill={ch.color}
                          fontSize="11"
                          fontWeight="bold"
                        >
                          {ch.name}
                        </text>

                        {/* Waveform Step Path */}
                        <path
                          d={(() => {
                            let pathStr = '';
                            simulationResult.samples.forEach((s, i) => {
                              const xStart = labelWidth + i * sampleWidth;
                              const xEnd = xStart + sampleWidth;
                              const val = s[ch.key] !== undefined ? s[ch.key] : 0;
                              const targetY = val === 1 ? highY : lowY;

                              if (i === 0) {
                                pathStr += `M ${xStart} ${targetY}`;
                              } else {
                                const prevVal = simulationResult.samples[i - 1][ch.key];
                                if (prevVal !== val) {
                                  pathStr += ` L ${xStart} ${targetY}`;
                                }
                              }
                              pathStr += ` L ${xEnd} ${targetY}`;
                            });
                            return pathStr;
                          })()}
                          fill="none"
                          stroke={ch.color}
                          strokeWidth="2"
                        />
                      </g>
                    );
                  })}
                </svg>
              );
            })()}
          </div>
        )}
      </div>

      {/* Bilingual Protocol Concepts & Thermal Policy Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        <div className="p-4 rounded-xl bg-[#020813]/80 border border-slate-800">
          <div className="font-bold text-emerald-400 mb-1 flex items-center gap-1.5">
            <span>📚</span>
            <span>SPI CPOL & CPHA</span>
          </div>
          <p className="text-slate-400 leading-relaxed">{t.cpolDesc} {t.cphaDesc}</p>
        </div>

        <div className="p-4 rounded-xl bg-[#020813]/80 border border-slate-800">
          <div className="font-bold text-cyan-400 mb-1 flex items-center gap-1.5">
            <span>🔄</span>
            <span>I2C Open-Drain Bus</span>
          </div>
          <p className="text-slate-400 leading-relaxed">{t.i2cOpenDrain}</p>
        </div>

        <div className="p-4 rounded-xl bg-[#020813]/80 border border-emerald-500/30">
          <div className="font-bold text-emerald-400 mb-1 flex items-center gap-1.5">
            <span>🛡️</span>
            <span>HP Victus Thermal Safety</span>
          </div>
          <p className="text-slate-400 leading-relaxed">
            Deterministic bitwise protocol framing with zero continuous polling loops keeps memory footprint sub-300MB and fans whisper-quiet.
          </p>
        </div>
      </div>

    </div>
  );
}
