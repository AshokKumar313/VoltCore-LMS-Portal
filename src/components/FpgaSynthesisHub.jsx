import React, { useState, useEffect, useMemo, useRef } from 'react';

// Target FPGA Architectures Presets
const FPGA_PRESETS = {
  XILINX_ARTIX7_XC7A35T: {
    key: 'XILINX_ARTIX7_XC7A35T',
    name: 'AMD Xilinx Artix-7 (XC7A35T)',
    family: 'Artix-7 28nm',
    vendor: 'AMD Xilinx',
    luts_total: 20800,
    ffs_total: 41600,
    bram_total: 50,
    dsp_total: 90,
    max_pll_mhz: 450.0,
    t_co_ns: 0.42,
    t_su_ns: 0.18,
    route_factor: 1.05
  },
  INTEL_CYCLONE_IV_EP4CE6: {
    key: 'INTEL_CYCLONE_IV_EP4CE6',
    name: 'Intel Cyclone IV E (EP4CE6)',
    family: 'Cyclone IV 60nm',
    vendor: 'Intel PSG (Altera)',
    luts_total: 6272,
    ffs_total: 6272,
    bram_total: 30,
    dsp_total: 15,
    max_pll_mhz: 250.0,
    t_co_ns: 0.65,
    t_su_ns: 0.32,
    route_factor: 1.25
  },
  LATTICE_ICE40_HX1K: {
    key: 'LATTICE_ICE40_HX1K',
    name: 'Lattice iCE40-HX1K',
    family: 'iCE40 UltraPlus 40nm',
    vendor: 'Lattice Semiconductor',
    luts_total: 1280,
    ffs_total: 1280,
    bram_total: 16,
    dsp_total: 0,
    max_pll_mhz: 133.0,
    t_co_ns: 0.95,
    t_su_ns: 0.45,
    route_factor: 1.40
  }
};

// Preset HDL Modules with Verilog & VHDL Source Code
const MODULE_PRESETS = {
  CLOCK_DIVIDER_COUNTER: {
    key: 'CLOCK_DIVIDER_COUNTER',
    title: '4-Bit Synchronous Counter & Clock Divider',
    category: 'Sequential Logic',
    base_luts: 14,
    base_ffs: 18,
    base_bram: 0,
    base_dsp: 0,
    t_logic_ns: 0.75,
    verilog: `// VoltCore Apex Academia - 4-Bit Synchronous Counter & Clock Divider
// Platform Lead: Ashok Kumar A (2023MITEC042) - MIT Campus, Anna University
module clock_divider_counter (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       en,
    output reg  [3:0] q_out,
    output wire       div2,
    output wire       div4,
    output wire       div8,
    output wire       div16,
    output wire       tc
);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            q_out <= 4'b0000;
        end else if (en) begin
            q_out <= q_out + 1'b1;
        end
    end

    assign div2  = q_out[0];
    assign div4  = q_out[1];
    assign div8  = q_out[2];
    assign div16 = q_out[3];
    assign tc    = (q_out == 4'hF) & en;
endmodule`,
    vhdl: `-- VoltCore Apex Academia - 4-Bit Synchronous Counter & Clock Divider
-- Platform Lead: Ashok Kumar A (2023MITEC042) - MIT Campus, Anna University
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity clock_divider_counter is
    Port (
        clk   : in  STD_LOGIC;
        rst_n : in  STD_LOGIC;
        en    : in  STD_LOGIC;
        q_out : out STD_LOGIC_VECTOR (3 downto 0);
        div2  : out STD_LOGIC;
        div4  : out STD_LOGIC;
        div8  : out STD_LOGIC;
        div16 : out STD_LOGIC;
        tc    : out STD_LOGIC
    );
end clock_divider_counter;

architecture Behavioral of clock_divider_counter is
    signal count_reg : unsigned(3 downto 0) := (others => '0');
begin
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            count_reg <= (others => '0');
        elsif rising_edge(clk) then
            if en = '1' then
                count_reg <= count_reg + 1;
            end if;
        end if;
    end process;

    q_out <= std_logic_vector(count_reg);
    div2  <= count_reg(0);
    div4  <= count_reg(1);
    div8  <= count_reg(2);
    div16 <= count_reg(3);
    tc    <= '1' when (count_reg = "1111" and en = '1') else '0';
end Behavioral;`
  },
  UART_TX_FSM: {
    key: 'UART_TX_FSM',
    title: '4-State UART Serial Transmitter FSM',
    category: 'Finite State Machine (FSM)',
    base_luts: 32,
    base_ffs: 28,
    base_bram: 0,
    base_dsp: 0,
    t_logic_ns: 1.15,
    verilog: `// VoltCore Apex Academia - 4-State UART Serial Transmitter FSM
// Platform Lead: Ashok Kumar A (2023MITEC042) - MIT Campus, Anna University
module uart_tx_fsm (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       tx_start,
    input  wire [7:0] tx_data,
    output reg        tx_line,
    output reg        tx_busy,
    output reg  [1:0] fsm_state
);
    localparam IDLE  = 2'b00;
    localparam START = 2'b01;
    localparam DATA  = 2'b10;
    localparam STOP  = 2'b11;

    reg [2:0] bit_idx;
    reg [7:0] shift_reg;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            fsm_state <= IDLE;
            tx_line   <= 1'b1;
            tx_busy   <= 1'b0;
            bit_idx   <= 3'd0;
            shift_reg <= 8'h00;
        end else begin
            case (fsm_state)
                IDLE: begin
                    tx_line <= 1'b1;
                    tx_busy <= 1'b0;
                    if (tx_start) begin
                        shift_reg <= tx_data;
                        fsm_state <= START;
                        tx_busy   <= 1'b1;
                    end
                end
                START: begin
                    tx_line   <= 1'b0; // Active low start bit
                    fsm_state <= DATA;
                    bit_idx   <= 3'd0;
                end
                DATA: begin
                    tx_line <= shift_reg[bit_idx];
                    if (bit_idx == 3'd7)
                        fsm_state <= STOP;
                    else
                        bit_idx <= bit_idx + 1'b1;
                end
                STOP: begin
                    tx_line   <= 1'b1; // Stop bit is HIGH
                    fsm_state <= IDLE;
                    tx_busy   <= 1'b0;
                end
            endcase
        end
    end
endmodule`,
    vhdl: `-- VoltCore Apex Academia - 4-State UART Serial Transmitter FSM
-- Platform Lead: Ashok Kumar A (2023MITEC042) - MIT Campus, Anna University
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity uart_tx_fsm is
    Port (
        clk       : in  STD_LOGIC;
        rst_n     : in  STD_LOGIC;
        tx_start  : in  STD_LOGIC;
        tx_data   : in  STD_LOGIC_VECTOR (7 downto 0);
        tx_line   : out STD_LOGIC;
        tx_busy   : out STD_LOGIC;
        fsm_state : out STD_LOGIC_VECTOR (1 downto 0)
    );
end uart_tx_fsm;

architecture Behavioral of uart_tx_fsm is
    type state_type is (ST_IDLE, ST_START, ST_DATA, ST_STOP);
    signal current_state : state_type := ST_IDLE;
    signal shift_reg     : std_logic_vector(7 downto 0) := (others => '0');
    signal bit_idx       : integer range 0 to 7 := 0;
begin
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            current_state <= ST_IDLE;
            tx_line       <= '1';
            tx_busy       <= '0';
        elsif rising_edge(clk) then
            case current_state is
                when ST_IDLE =>
                    tx_line <= '1';
                    tx_busy <= '0';
                    if tx_start = '1' then
                        shift_reg     <= tx_data;
                        current_state <= ST_START;
                        tx_busy       <= '1';
                    end if;
                when ST_START =>
                    tx_line       <= '0';
                    bit_idx       <= 0;
                    current_state <= ST_DATA;
                when ST_DATA =>
                    tx_line <= shift_reg(bit_idx);
                    if bit_idx = 7 then
                        current_state <= ST_STOP;
                    else
                        bit_idx <= bit_idx + 1;
                    end if;
                when ST_STOP =>
                    tx_line       <= '1';
                    current_state <= ST_IDLE;
                    tx_busy       <= '0';
            endcase;
        end if;
    end process;
    fsm_state <= "00" when current_state = ST_IDLE else
                 "01" when current_state = ST_START else
                 "10" when current_state = ST_DATA else "11";
end Behavioral;`
  },
  PIPELINED_ALU_8BIT: {
    key: 'PIPELINED_ALU_8BIT',
    title: '8-Bit Pipelined Multi-Function ALU',
    category: 'Combinatorial & Pipelined Logic',
    base_luts: 64,
    base_ffs: 48,
    base_bram: 0,
    base_dsp: 1,
    t_logic_ns: 1.72,
    verilog: `// VoltCore Apex Academia - 8-Bit Registered Multi-Function ALU
// Platform Lead: Ashok Kumar A (2023MITEC042) - MIT Campus, Anna University
module pipelined_alu_8bit (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [2:0]  alu_op,    // 000: ADD, 001: SUB, 010: AND, 011: OR, 100: XOR, 101: SHL
    input  wire [7:0]  operand_a,
    input  wire [7:0]  operand_b,
    output reg  [7:0]  alu_result,
    output reg         carry_out,
    output reg         zero_flag
);
    reg [8:0] raw_result;

    always @(*) begin
        case (alu_op)
            3'b000:  raw_result = operand_a + operand_b;
            3'b001:  raw_result = operand_a - operand_b;
            3'b010:  raw_result = {1'b0, operand_a & operand_b};
            3'b011:  raw_result = {1'b0, operand_a | operand_b};
            3'b100:  raw_result = {1'b0, operand_a ^ operand_b};
            3'b101:  raw_result = {operand_a[7], operand_a[6:0], 1'b0};
            default: raw_result = 9'h000;
        endcase
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            alu_result <= 8'h00;
            carry_out  <= 1'b0;
            zero_flag  <= 1'b0;
        end else begin
            alu_result <= raw_result[7:0];
            carry_out  <= raw_result[8];
            zero_flag  <= (raw_result[7:0] == 8'h00);
        end
    end
endmodule`,
    vhdl: `-- VoltCore Apex Academia - 8-Bit Registered Multi-Function ALU
-- Platform Lead: Ashok Kumar A (2023MITEC042) - MIT Campus, Anna University
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity pipelined_alu_8bit is
    Port (
        clk        : in  STD_LOGIC;
        rst_n      : in  STD_LOGIC;
        alu_op     : in  STD_LOGIC_VECTOR (2 downto 0);
        operand_a  : in  STD_LOGIC_VECTOR (7 downto 0);
        operand_b  : in  STD_LOGIC_VECTOR (7 downto 0);
        alu_result : out STD_LOGIC_VECTOR (7 downto 0);
        carry_out  : out STD_LOGIC;
        zero_flag  : out STD_LOGIC
    );
end pipelined_alu_8bit;

architecture Behavioral of pipelined_alu_8bit is
begin
    process(clk, rst_n)
        variable res_ext : unsigned(8 downto 0);
    begin
        if rst_n = '0' then
            alu_result <= (others => '0');
            carry_out  <= '0';
            zero_flag  <= '0';
        elsif rising_edge(clk) then
            case alu_op is
                when "000" => res_ext := resize(unsigned(operand_a), 9) + resize(unsigned(operand_b), 9);
                when "001" => res_ext := resize(unsigned(operand_a), 9) - resize(unsigned(operand_b), 9);
                when "010" => res_ext := resize(unsigned(operand_a and operand_b), 9);
                when "011" => res_ext := resize(unsigned(operand_a or operand_b), 9);
                when "100" => res_ext := resize(unsigned(operand_a xor operand_b), 9);
                when others => res_ext := (others => '0');
            end case;
            alu_result <= std_logic_vector(res_ext(7 downto 0));
            carry_out  <= res_ext(8);
            if res_ext(7 downto 0) = "00000000" then
                zero_flag <= '1';
            else
                zero_flag <= '0';
            end if;
        end if;
    end process;
end Behavioral;`
  },
  FIFO_BUFFER_8X8: {
    key: 'FIFO_BUFFER_8X8',
    title: '8-Word Circular FIFO Dual-Port Buffer',
    category: 'Memory & Queues',
    base_luts: 45,
    base_ffs: 36,
    base_bram: 1,
    base_dsp: 0,
    t_logic_ns: 1.40,
    verilog: `// VoltCore Apex Academia - 8x8 Circular FIFO Buffer
// Platform Lead: Ashok Kumar A (2023MITEC042) - MIT Campus, Anna University
module fifo_buffer_8x8 (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       wr_en,
    input  wire       rd_en,
    input  wire [7:0] din,
    output reg  [7:0] dout,
    output wire       full,
    output wire       empty,
    output reg  [3:0] fifo_count
);
    reg [7:0] mem [0:7];
    reg [2:0] wr_ptr;
    reg [2:0] rd_ptr;

    assign empty = (fifo_count == 4'd0);
    assign full  = (fifo_count == 4'd8);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr     <= 3'd0;
            rd_ptr     <= 3'd0;
            fifo_count <= 4'd0;
            dout       <= 8'h00;
        end else begin
            if (wr_en && !full) begin
                mem[wr_ptr] <= din;
                wr_ptr      <= wr_ptr + 1'b1;
            end
            if (rd_en && !empty) begin
                dout   <= mem[rd_ptr];
                rd_ptr <= rd_ptr + 1'b1;
            end
            case ({wr_en && !full, rd_en && !empty})
                2'b10: fifo_count <= fifo_count + 1'b1;
                2'b01: fifo_count <= fifo_count - 1'b1;
                default: fifo_count <= fifo_count;
            endcase
        end
    end
endmodule`,
    vhdl: `-- VoltCore Apex Academia - 8x8 Circular FIFO Buffer
-- Platform Lead: Ashok Kumar A (2023MITEC042) - MIT Campus, Anna University
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity fifo_buffer_8x8 is
    Port (
        clk        : in  STD_LOGIC;
        rst_n      : in  STD_LOGIC;
        wr_en      : in  STD_LOGIC;
        rd_en      : in  STD_LOGIC;
        din        : in  STD_LOGIC_VECTOR (7 downto 0);
        dout       : out STD_LOGIC_VECTOR (7 downto 0);
        full       : out STD_LOGIC;
        empty      : out STD_LOGIC;
        fifo_count : out STD_LOGIC_VECTOR (3 downto 0)
    );
end fifo_buffer_8x8;

architecture Behavioral of fifo_buffer_8x8 is
    type ram_type is array (0 to 7) of std_logic_vector(7 downto 0);
    signal mem : ram_type := (others => (others => '0'));
    signal wr_ptr, rd_ptr : integer range 0 to 7 := 0;
    signal count : integer range 0 to 8 := 0;
begin
    empty <= '1' when count = 0 else '0';
    full  <= '1' when count = 8 else '0';
    fifo_count <= std_logic_vector(to_unsigned(count, 4));

    process(clk, rst_n)
    begin
        if rst_n = '0' then
            wr_ptr <= 0;
            rd_ptr <= 0;
            count  <= 0;
            dout   <= (others => '0');
        elsif rising_edge(clk) then
            if wr_en = '1' and count < 8 then
                mem(wr_ptr) <= din;
                wr_ptr <= (wr_ptr + 1) mod 8;
            end if;
            if rd_en = '1' and count > 0 then
                dout <= mem(rd_ptr);
                rd_ptr <= (rd_ptr + 1) mod 8;
            end if;
            if (wr_en = '1' and count < 8) and not (rd_en = '1' and count > 0) then
                count <= count + 1;
            elsif (rd_en = '1' and count > 0) and not (wr_en = '1' and count < 8) then
                count <= count - 1;
            end if;
        end if;
    end process;
end Behavioral;`
  }
};

// Bilingual Technical Guidance
const DICTIONARY = {
  en: {
    badge: 'PHASE 35 ENTERPRISE',
    title: 'FPGA Synthesis & Logic Analyzer Simulator',
    subtitle: 'VHDL/Verilog Synthesis Estimator • Static Timing Analyzer • Multi-Channel Digital Logic Analyzer',
    author: 'Platform Lead: Ashok Kumar A (2023MITEC042) • MIT Campus, Anna University',
    controlsHeader: 'Synthesis Target & Hardware Configuration',
    targetFpga: 'Target FPGA Architecture',
    hdlModule: 'Synthesizable HDL Module',
    hdlLanguage: 'HDL Language',
    clockFreq: 'Target Clock Frequency (F_clk)',
    runSynthesis: 'Run Synthesis & STA',
    viewSource: 'View Synthesizable HDL',
    utilizationHeader: 'Resource Utilization & Static Timing Analysis (STA)',
    luts: 'Lookup Tables (LUTs)',
    ffs: 'Flip-Flops (Registers)',
    brams: 'Block RAM (36Kb Tiles)',
    dsps: 'DSP Multiplier Slices',
    fmax: 'Max Operating Freq (F_max)',
    minPeriod: 'Critical Path Period (T_crit)',
    setupSlack: 'Setup Slack (WNS)',
    holdSlack: 'Hold Slack (THS)',
    timingMet: 'Timing Constraints Met',
    timingViolated: 'Timing Violation Detected',
    logicAnalyzerHeader: 'Multi-Channel Digital Logic Analyzer & Cursor Timing HUD',
    cursorA: 'Cursor A (T1)',
    cursorB: 'Cursor B (T2)',
    deltaT: 'Delta (ΔT)',
    equivFreq: 'Equivalent Frequency',
    cycles: 'Display Cycles',
    zoom: 'Waveform Zoom',
    stepFwd: 'Step Clock (+1)',
    resetClock: 'Reset Traces',
    exportCsv: 'Export Logic Analyzer CSV',
    lutDesc: 'Lookup Table (LUT): Reconfigurable SRAM truth table implementing combinational boolean functions.',
    ffDesc: 'Flip-Flop (FF): Edge-triggered storage register for sequential state elements.',
    slackDesc: 'Setup Slack (WNS): Positive margin ensuring signal arrives before clock edge.'
  },
  ta: {
    badge: 'கட்டம் 35 நிறுவனம்',
    title: 'FPGA தொகுப்பு & லாஜிக் அனலைசர் சிமுலேட்டர்',
    subtitle: 'VHDL/Verilog தொகுப்பு மதிப்பீடு • நிலையான நேரப் பகுப்பாய்வி • பல சேனல் டிஜிட்டல் அலைவடிவங்கள்',
    author: 'தள ஒருங்கிணைப்பாளர்: அசோக் குமார் A (2023MITEC042) • MIT வளாகம், அண்ணா பல்கலைக்கழகம்',
    controlsHeader: 'தொகுப்பு இலக்கு & வன்பொருள் கட்டமைப்பு',
    targetFpga: 'இலக்கு FPGA கட்டமைப்பு',
    hdlModule: 'தொகுக்கக்கூடிய HDL தொகுதி',
    hdlLanguage: 'HDL மொழி',
    clockFreq: 'இலக்கு கடிகார அதிர்வெண் (F_clk)',
    runSynthesis: 'தொகுப்பு மற்றும் நேர ஆய்வு',
    viewSource: 'HDL மூல நிரல் காண்க',
    utilizationHeader: 'வளப் பயன்பாடு & நிலையான நேரப் பகுப்பாய்வு (STA)',
    luts: 'தேடல் அட்டவணைகள் (LUTs)',
    ffs: 'ஃபிளிப்-ஃப்ளாப்கள் (பதிவேடுகள்)',
    brams: 'பிளாக் ரேம் (36Kb அடுக்குகள்)',
    dsps: 'DSP பெருக்கல் துண்டுகள்',
    fmax: 'அதிகபட்ச அதிர்வெண் (F_max)',
    minPeriod: 'முக்கிய பாதை நேரம் (T_crit)',
    setupSlack: 'அமைவு இடைவெளி (WNS)',
    holdSlack: 'பிடிப்பு இடைவெளி (THS)',
    timingMet: 'நேரக் கட்டுப்பாடுகள் பூர்த்தி செய்யப்பட்டன',
    timingViolated: 'நேர விதிமீறல் கண்டறியப்பட்டது',
    logicAnalyzerHeader: 'பல-சேனல் டிஜிட்டல் லாஜிக் அனலைசர் & கர்சர் அளவீட்டு கருவி',
    cursorA: 'கர்சர் A (T1)',
    cursorB: 'கர்சர் B (T2)',
    deltaT: 'வேறுபாடு (ΔT)',
    equivFreq: 'சமமான அதிர்வெண்',
    cycles: 'சுழற்சிகள்',
    zoom: 'அலை உருப்பெருக்கம்',
    stepFwd: 'ஒரு படி நகர்த்து (+1)',
    resetClock: 'மீட்டமை',
    exportCsv: 'CSV கோப்பாக பதிவிறக்கு',
    lutDesc: 'தேடல் அட்டவணை: பூலியன் தர்க்க செயல்பாடுகளை செயல்படுத்தும் சிறிய மறுசீரமைக்கக்கூடிய நினைவகம்.',
    ffDesc: 'ஃபிளிப்-ஃப்ளாப்: கடிகார விளிம்பில் 1-பிட் நிலையை சேமிக்கும் தொடர் மின்னணு உறுப்பு.',
    slackDesc: 'அமைவு இடைவெளி (WNS): கடிகார விளிம்பிற்கு முன் சமிக்ஞை வந்து சேர்வதை உறுதி செய்யும் கூடுதல் நேரம்.'
  }
};

export default function FpgaSynthesisHub() {
  const [lang, setLang] = useState('en');
  const t = DICTIONARY[lang];

  // Selected Target FPGA & HDL Module
  const [selectedTargetKey, setSelectedTargetKey] = useState('XILINX_ARTIX7_XC7A35T');
  const [selectedModuleKey, setSelectedModuleKey] = useState('CLOCK_DIVIDER_COUNTER');
  const [hdlLanguage, setHdlLanguage] = useState('VERILOG'); // 'VERILOG' or 'VHDL'
  const [targetClockMhz, setTargetClockMhz] = useState(100.0);

  // Logic Analyzer Controls
  const [displayCycles, setDisplayCycles] = useState(32);
  const [zoomLevel, setZoomLevel] = useState(1); // 1x, 2x, 4x
  const [cursorA, setCursorA] = useState(4); // cycle index
  const [cursorB, setCursorB] = useState(12); // cycle index
  const [showSourceModal, setShowSourceModal] = useState(false);
  const [isCopied, setIsCopied] = useState(false);

  // Synthesis Output State
  const [synthesisResult, setSynthesisResult] = useState(null);
  const [waveformTraces, setWaveformTraces] = useState([]);
  const [isSynthesizing, setIsSynthesizing] = useState(false);

  const activeTarget = FPGA_PRESETS[selectedTargetKey];
  const activeModule = MODULE_PRESETS[selectedModuleKey];

  // Deterministic Local Synthesis Engine (Client Fallback & Instant Calculation)
  const computeClientSynthesis = (target, mod, clkMhz) => {
    const scale = target.key.includes('ARTIX7') ? 1.0 : (target.key.includes('CYCLONE') ? 1.15 : 1.30);
    const lutsUsed = Math.ceil(mod.base_luts * scale);
    const ffsUsed = Math.ceil(mod.base_ffs * scale);
    const bramUsed = mod.base_bram;
    const dspUsed = mod.base_dsp;

    const t_co = target.t_co_ns;
    const t_su = target.t_su_ns;
    const t_logic = mod.t_logic_ns;
    const t_route = Number((target.route_factor * 0.45).toFixed(3));
    const t_crit = Number((t_co + t_logic + t_route + t_su).toFixed(3));

    const fmax = Math.min(target.max_pll_mhz, Number((1000.0 / t_crit).toFixed(2)));
    const targetPeriod = Number((1000.0 / clkMhz).toFixed(3));
    const setupSlack = Number((targetPeriod - t_crit).toFixed(3));
    const holdSlack = Number((t_co - t_su + 0.12).toFixed(3));

    return {
      synthesis_id: `SYNTH_LOCAL_${Date.now().toString(16).toUpperCase()}`,
      utilization: {
        luts_used: lutsUsed,
        luts_total: target.luts_total,
        luts_pct: Number(((lutsUsed / target.luts_total) * 100).toFixed(3)),
        ffs_used: ffsUsed,
        ffs_total: target.ffs_total,
        ffs_pct: Number(((ffsUsed / target.ffs_total) * 100).toFixed(3)),
        bram_used: bramUsed,
        bram_total: target.bram_total,
        bram_pct: target.bram_total > 0 ? Number(((bramUsed / target.bram_total) * 100).toFixed(3)) : 0.0,
        dsp_used: dspUsed,
        dsp_total: target.dsp_total,
        dsp_pct: target.dsp_total > 0 ? Number(((dspUsed / target.dsp_total) * 100).toFixed(3)) : 0.0
      },
      timing_metrics: {
        fmax_mhz: fmax,
        min_period_ns: t_crit,
        setup_slack_ns: setupSlack,
        hold_slack_ns: holdSlack,
        timing_met: setupSlack >= 0 && holdSlack >= 0,
        t_co_ns: t_co,
        t_logic_ns: t_logic,
        t_route_ns: t_route,
        t_su_ns: t_su
      }
    };
  };

  // Deterministic Waveform Generator
  const generateTraces = (modKey, totalCycles, clkMhz) => {
    const clkPeriodNs = Number((1000.0 / clkMhz).toFixed(2));
    const traces = [];

    let countVal = 0;
    let uartState = 0;
    let uartBitIdx = 0;
    let uartShift = 0x4D;
    let uartTx = 1;
    let aluAcc = 0;
    let fifoBuf = [];

    for (let c = 0; c < totalCycles; c++) {
      const timeNs = Number((c * clkPeriodNs).toFixed(2));
      const rst = c < 2 ? 1 : 0;
      const en = (c >= 2 && (c % 10 !== 8)) ? 1 : 0;

      let din = 0x00;
      let dout = 0x00;
      let fsmStr = 'IDLE';
      let flags = 'NONE';

      if (modKey === 'CLOCK_DIVIDER_COUNTER') {
        din = (c * 3) & 0xFF;
        if (rst === 1) {
          countVal = 0;
        } else if (en === 1) {
          countVal = (countVal + 1) & 0x0F;
        }
        dout = countVal;
        const tc = (countVal === 0x0F && en === 1) ? 1 : 0;
        fsmStr = `Q=0x${countVal.toString(16).toUpperCase()}`;
        flags = `TC=${tc} | D2=${countVal & 1} | D4=${(countVal >> 1) & 1}`;
      } else if (modKey === 'UART_TX_FSM') {
        din = (c % 16 < 8) ? 0x4D : 0x54;
        if (rst === 1) {
          uartState = 0;
          uartTx = 1;
          uartBitIdx = 0;
        } else {
          if (uartState === 0) {
            uartTx = 1;
            fsmStr = 'IDLE (00)';
            if (c >= 3 && (c % 12 === 3)) {
              uartState = 1;
              uartShift = din;
            }
          } else if (uartState === 1) {
            uartTx = 0;
            fsmStr = 'START (01)';
            uartState = 2;
            uartBitIdx = 0;
          } else if (uartState === 2) {
            uartTx = (uartShift >> uartBitIdx) & 1;
            fsmStr = `DATA[${uartBitIdx}] (10)`;
            uartBitIdx++;
            if (uartBitIdx >= 8) uartState = 3;
          } else if (uartState === 3) {
            uartTx = 1;
            fsmStr = 'STOP (11)';
            uartState = 0;
          }
        }
        dout = uartTx ? 0x01 : 0x00;
        flags = `TX=${uartTx ? 'HIGH' : 'LOW'} | BUSY=${uartState !== 0 ? '1' : '0'}`;
      } else if (modKey === 'PIPELINED_ALU_8BIT') {
        din = (c * 7 + 0x11) & 0xFF;
        const operandB = 0x05;
        const opNames = ['ADD', 'SUB', 'AND', 'OR', 'XOR', 'SHL'];
        const opCode = Math.floor(c / 5) % 6;
        const curOp = opNames[opCode];

        if (rst === 1) {
          aluAcc = 0;
        } else {
          let res = 0;
          if (curOp === 'ADD') res = din + operandB;
          else if (curOp === 'SUB') res = din >= operandB ? din - operandB : (256 + din - operandB);
          else if (curOp === 'AND') res = din & operandB;
          else if (curOp === 'OR') res = din | operandB;
          else if (curOp === 'XOR') res = din ^ operandB;
          else if (curOp === 'SHL') res = (din << 1) & 0x1FF;
          aluAcc = res & 0xFF;
        }
        dout = aluAcc;
        fsmStr = `OP=${curOp}`;
        flags = `CARRY=${aluAcc > 255 ? '1' : '0'} | ZERO=${aluAcc === 0 ? '1' : '0'}`;
      } else if (modKey === 'FIFO_BUFFER_8X8') {
        din = (0x30 + c) & 0xFF;
        const wr = [2, 3, 4, 5, 8, 9, 12, 13].includes(c) ? 1 : 0;
        const rd = [6, 7, 10, 11, 14, 15, 16].includes(c) ? 1 : 0;

        if (rst === 1) {
          fifoBuf = [];
          dout = 0x00;
        } else {
          if (wr && fifoBuf.length < 8) fifoBuf.push(din);
          if (rd && fifoBuf.length > 0) dout = fifoBuf.shift();
        }
        fsmStr = `DEPTH=${fifoBuf.length}/8`;
        flags = `FULL=${fifoBuf.length >= 8 ? '1' : '0'} | EMPTY=${fifoBuf.length === 0 ? '1' : '0'}`;
      }

      traces.push({
        cycle: c,
        time_ns: timeNs,
        clk: c % 2 === 0 ? 1 : 0,
        reset: rst,
        enable: en,
        data_in_hex: `0x${din.toString(16).padStart(2, '0').toUpperCase()}`,
        data_out_hex: `0x${dout.toString(16).padStart(2, '0').toUpperCase()}`,
        fsm_state: fsmStr,
        flags: flags
      });
    }

    return traces;
  };

  // Run initial synthesis & trace generation on load or parameter changes
  useEffect(() => {
    handleRunSynthesis();
  }, [selectedTargetKey, selectedModuleKey, targetClockMhz, displayCycles]);

  const handleRunSynthesis = async () => {
    setIsSynthesizing(true);
    try {
      // Attempt backend synthesis endpoint with quick timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1200);

      const resp = await fetch('/api/fpga/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({
          target_fpga: selectedTargetKey,
          module_key: selectedModuleKey,
          hdl_type: hdlLanguage,
          target_clock_mhz: targetClockMhz,
          student_id: '2023MITEC042'
        })
      });
      clearTimeout(timeoutId);

      if (resp.ok) {
        const data = await resp.json();
        setSynthesisResult(data);
      } else {
        setSynthesisResult(computeClientSynthesis(activeTarget, activeModule, targetClockMhz));
      }
    } catch {
      // Deterministic fallback
      setSynthesisResult(computeClientSynthesis(activeTarget, activeModule, targetClockMhz));
    }

    // Generate Waveform Traces
    const traces = generateTraces(selectedModuleKey, displayCycles, targetClockMhz);
    setWaveformTraces(traces);
    setIsSynthesizing(false);
  };

  // Cursor Time and Channel Calculations
  const clkPeriodNs = useMemo(() => Number((1000.0 / targetClockMhz).toFixed(2)), [targetClockMhz]);
  const timeA = useMemo(() => Number((cursorA * clkPeriodNs).toFixed(2)), [cursorA, clkPeriodNs]);
  const timeB = useMemo(() => Number((cursorB * clkPeriodNs).toFixed(2)), [cursorB, clkPeriodNs]);
  const deltaCycles = useMemo(() => Math.abs(cursorB - cursorA), [cursorA, cursorB]);
  const deltaT = useMemo(() => Number(Math.abs(timeB - timeA).toFixed(2)), [timeA, timeB]);
  const equivFreqMhz = useMemo(() => {
    if (deltaT <= 0) return 0;
    return Number(((1000.0 / deltaT)).toFixed(2));
  }, [deltaT]);

  const traceA = waveformTraces[cursorA] || null;
  const traceB = waveformTraces[cursorB] || null;

  // CSV Export Action
  const handleExportCsv = () => {
    let csvContent = 'Cycle,Time_ns,CLK,RESET,ENABLE,DATA_IN_HEX,DATA_OUT_HEX,FSM_STATE,FLAGS\n';
    waveformTraces.forEach(t => {
      csvContent += `${t.cycle},${t.time_ns},${t.clk},${t.reset},${t.enable},${t.data_in_hex},${t.data_out_hex},"${t.fsm_state}","${t.flags}"\n`;
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `voltcore_logic_analyzer_${selectedModuleKey}_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const copySourceToClipboard = () => {
    const code = hdlLanguage === 'VERILOG' ? activeModule.verilog : activeModule.vhdl;
    navigator.clipboard.writeText(code);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  return (
    <div className="space-y-6 font-mono text-slate-200">
      
      {/* Top Banner & Language Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-[#020813]/90 border border-emerald-500/30 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-xl shadow-lg">
            ⚡
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

        {/* Language & Reset Trigger */}
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

      {/* Synthesis Configuration Grid */}
      <div className="p-6 rounded-2xl bg-[#020813]/85 border border-slate-800 shadow-lg space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-sm font-bold text-emerald-400 flex items-center gap-2">
            <span>⚙️</span>
            <span>{t.controlsHeader}</span>
          </h3>
          <span className="text-[11px] text-slate-400">{t.author}</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
          {/* Target FPGA Dropdown */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-300">{t.targetFpga}</label>
            <select
              value={selectedTargetKey}
              onChange={(e) => setSelectedTargetKey(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              {Object.values(FPGA_PRESETS).map(fpga => (
                <option key={fpga.key} value={fpga.key}>
                  {fpga.name}
                </option>
              ))}
            </select>
            <span className="text-[10px] text-slate-500 block">
              {activeTarget.family} • {activeTarget.vendor}
            </span>
          </div>

          {/* HDL Module Dropdown */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-300">{t.hdlModule}</label>
            <select
              value={selectedModuleKey}
              onChange={(e) => setSelectedModuleKey(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              {Object.values(MODULE_PRESETS).map(mod => (
                <option key={mod.key} value={mod.key}>
                  {mod.title}
                </option>
              ))}
            </select>
            <span className="text-[10px] text-emerald-500/80 block">
              Category: {activeModule.category}
            </span>
          </div>

          {/* HDL Language Toggle */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-300">{t.hdlLanguage}</label>
            <div className="flex rounded-xl bg-slate-900 p-1 border border-slate-700">
              <button
                onClick={() => setHdlLanguage('VERILOG')}
                className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-all ${
                  hdlLanguage === 'VERILOG'
                    ? 'bg-emerald-600 text-white shadow'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Verilog (2001)
              </button>
              <button
                onClick={() => setHdlLanguage('VHDL')}
                className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-all ${
                  hdlLanguage === 'VHDL'
                    ? 'bg-emerald-600 text-white shadow'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                VHDL (1993)
              </button>
            </div>
            <button
              onClick={() => setShowSourceModal(true)}
              className="text-[10px] text-cyan-400 hover:underline flex items-center gap-1 mt-1"
            >
              <span>📄</span>
              <span>{t.viewSource}</span>
            </button>
          </div>

          {/* Clock Frequency Slider */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs">
              <label className="font-bold text-slate-300">{t.clockFreq}</label>
              <span className="text-emerald-400 font-bold">{targetClockMhz} MHz (T = {clkPeriodNs} ns)</span>
            </div>
            <input
              type="range"
              min="10"
              max="250"
              step="5"
              value={targetClockMhz}
              onChange={(e) => setTargetClockMhz(parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>10 MHz</span>
              <span>100 MHz</span>
              <span>250 MHz</span>
            </div>
          </div>
        </div>
      </div>

      {/* Synthesis Utilization & STA Timing Cards */}
      {synthesisResult && (
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-4">
          
          {/* LUTs Card */}
          <div className="p-4 rounded-xl bg-[#020813]/90 border border-slate-800 flex flex-col justify-between">
            <div className="text-[11px] text-slate-400 font-bold">{t.luts}</div>
            <div className="my-2">
              <span className="text-xl font-black text-emerald-400">
                {synthesisResult.utilization.luts_used}
              </span>
              <span className="text-xs text-slate-500 ml-1">/ {synthesisResult.utilization.luts_total}</span>
            </div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.max(2, Math.min(100, synthesisResult.utilization.luts_pct * 10))}%` }}
              ></div>
            </div>
            <span className="text-[10px] text-slate-500 mt-1">{synthesisResult.utilization.luts_pct}% used</span>
          </div>

          {/* Flip-Flops Card */}
          <div className="p-4 rounded-xl bg-[#020813]/90 border border-slate-800 flex flex-col justify-between">
            <div className="text-[11px] text-slate-400 font-bold">{t.ffs}</div>
            <div className="my-2">
              <span className="text-xl font-black text-cyan-400">
                {synthesisResult.utilization.ffs_used}
              </span>
              <span className="text-xs text-slate-500 ml-1">/ {synthesisResult.utilization.ffs_total}</span>
            </div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-cyan-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.max(2, Math.min(100, synthesisResult.utilization.ffs_pct * 10))}%` }}
              ></div>
            </div>
            <span className="text-[10px] text-slate-500 mt-1">{synthesisResult.utilization.ffs_pct}% used</span>
          </div>

          {/* Block RAM Card */}
          <div className="p-4 rounded-xl bg-[#020813]/90 border border-slate-800 flex flex-col justify-between">
            <div className="text-[11px] text-slate-400 font-bold">{t.brams}</div>
            <div className="my-2">
              <span className="text-xl font-black text-amber-400">
                {synthesisResult.utilization.bram_used}
              </span>
              <span className="text-xs text-slate-500 ml-1">/ {synthesisResult.utilization.bram_total}</span>
            </div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-amber-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.max(2, Math.min(100, synthesisResult.utilization.bram_pct))}%` }}
              ></div>
            </div>
            <span className="text-[10px] text-slate-500 mt-1">{synthesisResult.utilization.bram_pct}% used</span>
          </div>

          {/* DSP Slices Card */}
          <div className="p-4 rounded-xl bg-[#020813]/90 border border-slate-800 flex flex-col justify-between">
            <div className="text-[11px] text-slate-400 font-bold">{t.dsps}</div>
            <div className="my-2">
              <span className="text-xl font-black text-purple-400">
                {synthesisResult.utilization.dsp_used}
              </span>
              <span className="text-xs text-slate-500 ml-1">/ {synthesisResult.utilization.dsp_total}</span>
            </div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-purple-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.max(2, Math.min(100, synthesisResult.utilization.dsp_pct))}%` }}
              ></div>
            </div>
            <span className="text-[10px] text-slate-500 mt-1">{synthesisResult.utilization.dsp_pct}% used</span>
          </div>

          {/* Fmax Badge */}
          <div className="p-4 rounded-xl bg-[#020813]/90 border border-slate-800 flex flex-col justify-between">
            <div className="text-[11px] text-slate-400 font-bold">{t.fmax}</div>
            <div className="my-2">
              <span className="text-xl font-black text-emerald-300">
                {synthesisResult.timing_metrics.fmax_mhz}
              </span>
              <span className="text-xs text-slate-500 ml-1">MHz</span>
            </div>
            <div className="text-[10px] text-slate-400">
              T_crit = {synthesisResult.timing_metrics.min_period_ns} ns
            </div>
            <span className="text-[10px] text-emerald-500">STA Max Limit</span>
          </div>

          {/* Setup Slack (WNS) */}
          <div className={`p-4 rounded-xl bg-[#020813]/90 border flex flex-col justify-between ${
            synthesisResult.timing_metrics.timing_met ? 'border-emerald-500/40' : 'border-rose-500/40'
          }`}>
            <div className="text-[11px] text-slate-400 font-bold">{t.setupSlack}</div>
            <div className="my-2">
              <span className={`text-xl font-black ${
                synthesisResult.timing_metrics.timing_met ? 'text-emerald-400' : 'text-rose-400'
              }`}>
                {synthesisResult.timing_metrics.setup_slack_ns >= 0 ? '+' : ''}
                {synthesisResult.timing_metrics.setup_slack_ns}
              </span>
              <span className="text-xs text-slate-500 ml-1">ns</span>
            </div>
            <div className="text-[10px] text-slate-400">
              Hold Slack: +{synthesisResult.timing_metrics.hold_slack_ns} ns
            </div>
            <span className={`text-[10px] font-bold ${
              synthesisResult.timing_metrics.timing_met ? 'text-emerald-400' : 'text-rose-400'
            }`}>
              {synthesisResult.timing_metrics.timing_met ? `✓ ${t.timingMet}` : `✗ ${t.timingViolated}`}
            </span>
          </div>

        </div>
      )}

      {/* Logic Analyzer & Cursor Timing HUD */}
      <div className="p-6 rounded-2xl bg-[#020813]/90 border border-slate-800 shadow-2xl space-y-5">
        
        {/* HUD Top Bar: Measurement Readout */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/90 border border-slate-700/80">
          <div className="flex items-center gap-4 flex-wrap">
            {/* Cursor A Badge */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-950/60 border border-cyan-500/40 text-xs">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
              <span className="text-cyan-300 font-bold">{t.cursorA}:</span>
              <span className="text-white font-mono">{timeA} ns (C{cursorA})</span>
            </div>

            {/* Cursor B Badge */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-950/60 border border-amber-500/40 text-xs">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
              <span className="text-amber-300 font-bold">{t.cursorB}:</span>
              <span className="text-white font-mono">{timeB} ns (C{cursorB})</span>
            </div>

            {/* Delta Timing Badge */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/60 border border-emerald-500/40 text-xs">
              <span className="text-emerald-400 font-bold">{t.deltaT}:</span>
              <span className="text-emerald-300 font-mono font-bold">{deltaT} ns ({deltaCycles} cycles)</span>
            </div>

            {/* Equivalent Frequency */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-purple-950/60 border border-purple-500/40 text-xs">
              <span className="text-purple-300 font-bold">{t.equivFreq}:</span>
              <span className="text-white font-mono font-bold">{equivFreqMhz} MHz</span>
            </div>
          </div>

          {/* Display & Zoom Controls */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-xs text-slate-400">
              <span>{t.cycles}:</span>
              {[16, 32, 64].map(num => (
                <button
                  key={num}
                  onClick={() => setDisplayCycles(num)}
                  className={`px-2 py-1 rounded text-xs font-bold ${
                    displayCycles === num
                      ? 'bg-emerald-600 text-white'
                      : 'bg-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  {num}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-1 text-xs">
              <button
                onClick={() => setZoomLevel(z => Math.max(1, z - 1))}
                className="w-7 h-7 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 flex items-center justify-center font-bold"
                title="Zoom Out"
              >
                -
              </button>
              <span className="text-xs px-1.5 text-slate-400">{zoomLevel}x</span>
              <button
                onClick={() => setZoomLevel(z => Math.min(3, z + 1))}
                className="w-7 h-7 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 flex items-center justify-center font-bold"
                title="Zoom In"
              >
                +
              </button>
            </div>
          </div>
        </div>

        {/* Cursor Position Sliders */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs bg-slate-950/50 p-3 rounded-xl border border-slate-800">
          <div className="flex items-center gap-3">
            <span className="text-cyan-400 font-bold min-w-[70px]">Cursor A:</span>
            <input
              type="range"
              min="0"
              max={displayCycles - 1}
              value={cursorA}
              onChange={(e) => setCursorA(parseInt(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
            />
            <span className="font-mono text-cyan-300 min-w-[40px]">C{cursorA}</span>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-amber-400 font-bold min-w-[70px]">Cursor B:</span>
            <input
              type="range"
              min="0"
              max={displayCycles - 1}
              value={cursorB}
              onChange={(e) => setCursorB(parseInt(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-400"
            />
            <span className="font-mono text-amber-300 min-w-[40px]">C{cursorB}</span>
          </div>
        </div>

        {/* Waveform Canvas / SVG Container */}
        <div className="overflow-x-auto border border-slate-800 rounded-xl bg-[#010611] p-4 relative select-none">
          
          {/* Signal Trace Rows */}
          {(() => {
            const cycleWidth = 32 * zoomLevel;
            const totalSvgWidth = Math.max(800, displayCycles * cycleWidth + 120);
            const labelColWidth = 110;
            const plotWidth = displayCycles * cycleWidth;

            // Channels list
            const channels = [
              { name: 'CLK', type: 'digital', height: 36 },
              { name: 'RESET', type: 'digital', height: 36 },
              { name: 'ENABLE', type: 'digital', height: 36 },
              { name: 'DATA_IN[7:0]', type: 'bus', height: 42 },
              { name: 'DATA_OUT[7:0]', type: 'bus', height: 42 },
              { name: 'FSM_STATE', type: 'bus', height: 42 }
            ];

            const totalHeight = channels.reduce((acc, c) => acc + c.height, 0) + 40;

            // Cursor X coordinates
            const cursorAX = labelColWidth + cursorA * cycleWidth + (cycleWidth / 2);
            const cursorBX = labelColWidth + cursorB * cycleWidth + (cycleWidth / 2);

            return (
              <svg
                width={totalSvgWidth}
                height={totalHeight}
                className="font-mono text-[11px]"
                style={{ minWidth: '100%' }}
              >
                {/* Background Grid Lines for each clock cycle */}
                {Array.from({ length: displayCycles }).map((_, i) => {
                  const x = labelColWidth + i * cycleWidth;
                  return (
                    <g key={i}>
                      <line
                        x1={x}
                        y1={24}
                        x2={x}
                        y2={totalHeight - 10}
                        stroke="#1e293b"
                        strokeWidth="1"
                        strokeDasharray="2,4"
                      />
                      <text
                        x={x + cycleWidth / 2}
                        y={16}
                        fill="#64748b"
                        textAnchor="middle"
                        fontSize="9"
                      >
                        {i}
                      </text>
                    </g>
                  );
                })}

                {/* Render Each Channel */}
                {(() => {
                  let currentY = 28;

                  return channels.map((ch, chIdx) => {
                    const rowY = currentY;
                    currentY += ch.height;
                    const baselineY = rowY + ch.height - 8;
                    const highY = rowY + 8;

                    return (
                      <g key={ch.name}>
                        {/* Channel Label */}
                        <rect
                          x={0}
                          y={rowY}
                          width={labelColWidth - 8}
                          height={ch.height - 4}
                          fill="#0f172a"
                          rx={4}
                        />
                        <text
                          x={8}
                          y={rowY + (ch.height / 2) + 2}
                          fill="#38bdf8"
                          fontSize="10"
                          fontWeight="bold"
                        >
                          {ch.name}
                        </text>

                        {/* Channel Waveform Paths */}
                        {ch.type === 'digital' ? (
                          // Square Wave Digital Paths
                          <path
                            d={(() => {
                              let pathStr = '';
                              waveformTraces.forEach((t, i) => {
                                const xStart = labelColWidth + i * cycleWidth;
                                const xMid = xStart + (cycleWidth / 2);
                                const xEnd = xStart + cycleWidth;

                                if (ch.name === 'CLK') {
                                  // Alternating clock inside cycle
                                  if (i === 0) pathStr += `M ${xStart} ${baselineY}`;
                                  pathStr += ` L ${xStart} ${highY} L ${xMid} ${highY} L ${xMid} ${baselineY} L ${xEnd} ${baselineY}`;
                                } else {
                                  const val = ch.name === 'RESET' ? t.reset : t.enable;
                                  const targetY = val === 1 ? highY : baselineY;
                                  if (i === 0) {
                                    pathStr += `M ${xStart} ${targetY}`;
                                  } else {
                                    const prevVal = ch.name === 'RESET' ? waveformTraces[i - 1].reset : waveformTraces[i - 1].enable;
                                    if (prevVal !== val) {
                                      pathStr += ` L ${xStart} ${targetY}`;
                                    }
                                  }
                                  pathStr += ` L ${xEnd} ${targetY}`;
                                }
                              });
                              return pathStr;
                            })()}
                            fill="none"
                            stroke={ch.name === 'CLK' ? '#10b981' : (ch.name === 'RESET' ? '#f43f5e' : '#38bdf8')}
                            strokeWidth="2"
                          />
                        ) : (
                          // Multi-bit Bus Hexagonal Crossover Shapes
                          waveformTraces.map((t, i) => {
                            const xStart = labelColWidth + i * cycleWidth;
                            const xEnd = xStart + cycleWidth;
                            const hexVal = ch.name === 'DATA_IN[7:0]' ? t.data_in_hex : (ch.name === 'DATA_OUT[7:0]' ? t.data_out_hex : t.fsm_state);
                            const slant = 4;

                            return (
                              <g key={i}>
                                <polygon
                                  points={`
                                    ${xStart + slant},${highY}
                                    ${xEnd - slant},${highY}
                                    ${xEnd},${rowY + (ch.height / 2)}
                                    ${xEnd - slant},${baselineY}
                                    ${xStart + slant},${baselineY}
                                    ${xStart},${rowY + (ch.height / 2)}
                                  `}
                                  fill="#1e293b"
                                  stroke={ch.name === 'DATA_OUT[7:0]' ? '#a855f7' : (ch.name === 'DATA_IN[7:0]' ? '#06b6d4' : '#eab308')}
                                  strokeWidth="1.5"
                                />
                                <text
                                  x={xStart + (cycleWidth / 2)}
                                  y={rowY + (ch.height / 2) + 3}
                                  fill="#f8fafc"
                                  fontSize="9"
                                  textAnchor="middle"
                                  fontWeight="bold"
                                >
                                  {zoomLevel === 1 && hexVal.length > 6 ? hexVal.slice(0, 5) : hexVal}
                                </text>
                              </g>
                            );
                          })
                        )}
                      </g>
                    );
                  });
                })()}

                {/* Vertical Cursor A Guideline */}
                <line
                  x1={cursorAX}
                  y1={20}
                  x2={cursorAX}
                  y2={totalHeight}
                  stroke="#22d3ee"
                  strokeWidth="2"
                  strokeDasharray="4,2"
                />
                <circle cx={cursorAX} cy={20} r={4} fill="#22d3ee" />
                <text x={cursorAX + 4} y={16} fill="#22d3ee" fontSize="9" fontWeight="bold">
                  A
                </text>

                {/* Vertical Cursor B Guideline */}
                <line
                  x1={cursorBX}
                  y1={20}
                  x2={cursorBX}
                  y2={totalHeight}
                  stroke="#fbbf24"
                  strokeWidth="2"
                  strokeDasharray="4,2"
                />
                <circle cx={cursorBX} cy={20} r={4} fill="#fbbf24" />
                <text x={cursorBX + 4} y={16} fill="#fbbf24" fontSize="9" fontWeight="bold">
                  B
                </text>
              </svg>
            );
          })()}
        </div>

        {/* State Probe Table Under Cursors */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          {/* Probe A */}
          <div className="p-3 rounded-xl bg-cyan-950/30 border border-cyan-500/30">
            <div className="flex items-center justify-between font-bold text-cyan-400 mb-2 border-b border-cyan-500/20 pb-1">
              <span>Probe Cursor A (Cycle {cursorA} • {timeA} ns)</span>
              <span className="text-[10px] text-cyan-200">State Values</span>
            </div>
            {traceA && (
              <div className="grid grid-cols-3 gap-2 font-mono text-[11px]">
                <div>CLK: <span className="text-white font-bold">{traceA.clk}</span></div>
                <div>RESET: <span className="text-white font-bold">{traceA.reset}</span></div>
                <div>ENABLE: <span className="text-white font-bold">{traceA.enable}</span></div>
                <div className="col-span-3">DIN: <span className="text-cyan-300 font-bold">{traceA.data_in_hex}</span></div>
                <div className="col-span-3">DOUT: <span className="text-purple-300 font-bold">{traceA.data_out_hex}</span></div>
                <div className="col-span-3 text-slate-300">State: <span className="text-amber-300 font-bold">{traceA.fsm_state}</span></div>
              </div>
            )}
          </div>

          {/* Probe B */}
          <div className="p-3 rounded-xl bg-amber-950/30 border border-amber-500/30">
            <div className="flex items-center justify-between font-bold text-amber-400 mb-2 border-b border-amber-500/20 pb-1">
              <span>Probe Cursor B (Cycle {cursorB} • {timeB} ns)</span>
              <span className="text-[10px] text-amber-200">State Values</span>
            </div>
            {traceB && (
              <div className="grid grid-cols-3 gap-2 font-mono text-[11px]">
                <div>CLK: <span className="text-white font-bold">{traceB.clk}</span></div>
                <div>RESET: <span className="text-white font-bold">{traceB.reset}</span></div>
                <div>ENABLE: <span className="text-white font-bold">{traceB.enable}</span></div>
                <div className="col-span-3">DIN: <span className="text-cyan-300 font-bold">{traceB.data_in_hex}</span></div>
                <div className="col-span-3">DOUT: <span className="text-purple-300 font-bold">{traceB.data_out_hex}</span></div>
                <div className="col-span-3 text-slate-300">State: <span className="text-amber-300 font-bold">{traceB.fsm_state}</span></div>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Bilingual FPGA Concepts & Thermal Guidance Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        <div className="p-4 rounded-xl bg-[#020813]/80 border border-slate-800">
          <div className="font-bold text-emerald-400 mb-1 flex items-center gap-1.5">
            <span>📚</span>
            <span>{t.luts}</span>
          </div>
          <p className="text-slate-400 leading-relaxed">{t.lutDesc}</p>
        </div>

        <div className="p-4 rounded-xl bg-[#020813]/80 border border-slate-800">
          <div className="font-bold text-cyan-400 mb-1 flex items-center gap-1.5">
            <span>⏱️</span>
            <span>{t.setupSlack}</span>
          </div>
          <p className="text-slate-400 leading-relaxed">{t.slackDesc}</p>
        </div>

        <div className="p-4 rounded-xl bg-[#020813]/80 border border-emerald-500/30">
          <div className="font-bold text-emerald-400 mb-1 flex items-center gap-1.5">
            <span>🛡️</span>
            <span>HP Victus Thermal Safety</span>
          </div>
          <p className="text-slate-400 leading-relaxed">
            Deterministic static timing calculation with zero continuous polling loops preserves whisper-quiet fans and cool sub-50°C operation on LAPTOP-3NEGBVLE.
          </p>
        </div>
      </div>

      {/* Modal: View Synthesizable HDL Code */}
      {showSourceModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="w-full max-w-3xl rounded-2xl bg-[#020813] border border-emerald-500/40 p-6 space-y-4 shadow-2xl max-h-[85vh] flex flex-col">
            
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <span className="text-lg">📄</span>
                <h3 className="text-sm font-bold text-white">
                  {activeModule.title} — Synthesizable {hdlLanguage}
                </h3>
              </div>
              <button
                onClick={() => setShowSourceModal(false)}
                className="w-7 h-7 rounded-lg bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center font-bold"
              >
                ✕
              </button>
            </div>

            <div className="flex-1 overflow-auto bg-slate-950 p-4 rounded-xl border border-slate-800">
              <pre className="text-xs text-emerald-300 font-mono leading-relaxed whitespace-pre">
                {hdlLanguage === 'VERILOG' ? activeModule.verilog : activeModule.vhdl}
              </pre>
            </div>

            <div className="flex items-center justify-between pt-2">
              <span className="text-[11px] text-slate-500">
                Anna University ECE Regulation 2023 • Synthesizable RTL
              </span>
              <div className="flex gap-2">
                <button
                  onClick={copySourceToClipboard}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-bold text-white border border-slate-700 flex items-center gap-1"
                >
                  <span>📋</span>
                  <span>{isCopied ? 'Copied!' : 'Copy Code'}</span>
                </button>
                <button
                  onClick={() => setShowSourceModal(false)}
                  className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-bold text-white"
                >
                  Close
                </button>
              </div>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
