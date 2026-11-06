"""
========================================================================================
VoltCore Apex Academia - Phase 35: FPGA Synthesis & Logic Analyzer Simulator Engine
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Hardware Safe: Zero background polling loops, SQLite WAL mode, cool thermal footprint.
========================================================================================
"""

import os
import sqlite3
import json
import csv
import io
import math
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Database path in workspace root
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "voltcore_telemetry.db")

# Target FPGA architectures
FPGA_TARGETS: Dict[str, Dict[str, Any]] = {
    "XILINX_ARTIX7_XC7A35T": {
        "key": "XILINX_ARTIX7_XC7A35T",
        "name": "AMD Xilinx Artix-7 (XC7A35T-1CPG236C)",
        "family": "Artix-7",
        "vendor": "AMD Xilinx",
        "technology": "28nm TSMC High Performance Low Power (HPL)",
        "luts_total": 20800,
        "ffs_total": 41600,
        "bram_36k_total": 50,
        "dsp_slices_total": 90,
        "io_pins_total": 106,
        "max_pll_freq_mhz": 450.0,
        "typical_core_v": 1.00,
        "t_co_typical_ns": 0.42,
        "t_su_typical_ns": 0.18,
        "t_route_factor": 1.05
    },
    "INTEL_CYCLONE_IV_EP4CE6": {
        "key": "INTEL_CYCLONE_IV_EP4CE6",
        "name": "Intel Altera Cyclone IV E (EP4CE6E22C8N)",
        "family": "Cyclone IV E",
        "vendor": "Intel PSG (Altera)",
        "technology": "60nm Low Power",
        "luts_total": 6272,
        "ffs_total": 6272,
        "bram_36k_total": 30,
        "dsp_slices_total": 15,
        "io_pins_total": 91,
        "max_pll_freq_mhz": 250.0,
        "typical_core_v": 1.20,
        "t_co_typical_ns": 0.65,
        "t_su_typical_ns": 0.32,
        "t_route_factor": 1.25
    },
    "LATTICE_ICE40_HX1K": {
        "key": "LATTICE_ICE40_HX1K",
        "name": "Lattice iCE40-HX1K (iCE40HX1K-TQ144)",
        "family": "iCE40 UltraPlus / HX",
        "vendor": "Lattice Semiconductor",
        "technology": "40nm NVCM Low Power",
        "luts_total": 1280,
        "ffs_total": 1280,
        "bram_36k_total": 16,
        "dsp_slices_total": 0,
        "io_pins_total": 96,
        "max_pll_freq_mhz": 133.0,
        "typical_core_v": 1.20,
        "t_co_typical_ns": 0.95,
        "t_su_typical_ns": 0.45,
        "t_route_factor": 1.40
    }
}

# Synthesizable HDL Module Models
HDL_MODULES: Dict[str, Dict[str, Any]] = {
    "CLOCK_DIVIDER_COUNTER": {
        "key": "CLOCK_DIVIDER_COUNTER",
        "title": "4-Bit Synchronous Counter & Clock Divider Cascade",
        "category": "Sequential Logic",
        "verilog_source": """// VoltCore Apex Academia - 4-Bit Synchronous Counter & Clock Divider
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
endmodule""",
        "vhdl_source": """-- VoltCore Apex Academia - 4-Bit Synchronous Counter & Clock Divider
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
end Behavioral;""",
        "base_luts": 14,
        "base_ffs": 18,
        "base_bram": 0,
        "base_dsp": 0,
        "t_logic_ns": 0.75
    },
    "UART_TX_FSM": {
        "key": "UART_TX_FSM",
        "title": "4-State UART Serial Transmitter Finite State Machine",
        "category": "Finite State Machine (FSM)",
        "verilog_source": """// VoltCore Apex Academia - 4-State UART Serial Transmitter FSM
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
                    tx_line   <= 1'b0; // Start bit is active LOW
                    fsm_state <= DATA;
                    bit_idx   <= 3'd0;
                end
                DATA: begin
                    tx_line <= shift_reg[bit_idx];
                    if (bit_idx == 3'd7) begin
                        fsm_state <= STOP;
                    end else begin
                        bit_idx <= bit_idx + 1'b1;
                    end
                end
                STOP: begin
                    tx_line   <= 1'b1; // Stop bit is HIGH
                    fsm_state <= IDLE;
                    tx_busy   <= 1'b0;
                end
            endcase
        end
    end
endmodule""",
        "vhdl_source": """-- VoltCore Apex Academia - 4-State UART Serial Transmitter FSM
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
    signal current_state, next_state : state_type := ST_IDLE;
    signal shift_reg : std_logic_vector(7 downto 0) := (others => '0');
    signal bit_idx   : integer range 0 to 7 := 0;
begin
    -- Sequential process
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            current_state <= ST_IDLE;
            tx_line <= '1';
            tx_busy <= '0';
            shift_reg <= (others => '0');
            bit_idx <= 0;
        elsif rising_edge(clk) then
            case current_state is
                when ST_IDLE =>
                    tx_line <= '1';
                    tx_busy <= '0';
                    if tx_start = '1' then
                        shift_reg <= tx_data;
                        current_state <= ST_START;
                        tx_busy <= '1';
                    end if;
                when ST_START =>
                    tx_line <= '0';
                    bit_idx <= 0;
                    current_state <= ST_DATA;
                when ST_DATA =>
                    tx_line <= shift_reg(bit_idx);
                    if bit_idx = 7 then
                        current_state <= ST_STOP;
                    else
                        bit_idx <= bit_idx + 1;
                    end if;
                when ST_STOP =>
                    tx_line <= '1';
                    current_state <= ST_IDLE;
                    tx_busy <= '0';
            endcase;
        end if;
    end process;

    fsm_state <= "00" when current_state = ST_IDLE else
                 "01" when current_state = ST_START else
                 "10" when current_state = ST_DATA else "11";
end Behavioral;""",
        "base_luts": 32,
        "base_ffs": 28,
        "base_bram": 0,
        "base_dsp": 0,
        "t_logic_ns": 1.15
    },
    "PIPELINED_ALU_8BIT": {
        "key": "PIPELINED_ALU_8BIT",
        "title": "8-Bit Pipelined Multi-Function Arithmetic Logic Unit (ALU)",
        "category": "Combinatorial & Pipelined Logic",
        "verilog_source": """// VoltCore Apex Academia - 8-Bit Registered Multi-Function ALU
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
            3'b000:  raw_result = operand_a + operand_b;              // ADD
            3'b001:  raw_result = operand_a - operand_b;              // SUB
            3'b010:  raw_result = {1'b0, operand_a & operand_b};       // AND
            3'b011:  raw_result = {1'b0, operand_a | operand_b};       // OR
            3'b100:  raw_result = {1'b0, operand_a ^ operand_b};       // XOR
            3'b101:  raw_result = {operand_a[7], operand_a[6:0], 1'b0}; // SHL
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
endmodule""",
        "vhdl_source": """-- VoltCore Apex Academia - 8-Bit Registered Multi-Function ALU
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
        variable op_a_ext, op_b_ext : unsigned(8 downto 0);
        variable res_ext : unsigned(8 downto 0);
    begin
        if rst_n = '0' then
            alu_result <= (others => '0');
            carry_out  <= '0';
            zero_flag  <= '0';
        elsif rising_edge(clk) then
            op_a_ext := resize(unsigned(operand_a), 9);
            op_b_ext := resize(unsigned(operand_b), 9);
            case alu_op is
                when "000" => res_ext := op_a_ext + op_b_ext;
                when "001" => res_ext := op_a_ext - op_b_ext;
                when "010" => res_ext := resize(unsigned(operand_a and operand_b), 9);
                when "011" => res_ext := resize(unsigned(operand_a or operand_b), 9);
                when "100" => res_ext := resize(unsigned(operand_a xor operand_b), 9);
                when "101" => res_ext := shift_left(op_a_ext, 1);
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
end Behavioral;""",
        "base_luts": 64,
        "base_ffs": 48,
        "base_bram": 0,
        "base_dsp": 1,
        "t_logic_ns": 1.72
    },
    "FIFO_BUFFER_8X8": {
        "key": "FIFO_BUFFER_8X8",
        "title": "8-Word Circular First-In First-Out (FIFO) Dual-Port Buffer",
        "category": "Memory & Queues",
        "verilog_source": """// VoltCore Apex Academia - 8x8 Circular FIFO Buffer
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
            // Write operation
            if (wr_en && !full) begin
                mem[wr_ptr] <= din;
                wr_ptr      <= wr_ptr + 1'b1;
            end
            // Read operation
            if (rd_en && !empty) begin
                dout   <= mem[rd_ptr];
                rd_ptr <= rd_ptr + 1'b1;
            end
            // Counter management
            case ({wr_en && !full, rd_en && !empty})
                2'b10: fifo_count <= fifo_count + 1'b1;
                2'b01: fifo_count <= fifo_count - 1'b1;
                default: fifo_count <= fifo_count;
            endcase
        end
    end
endmodule""",
        "vhdl_source": """-- VoltCore Apex Academia - 8x8 Circular FIFO Buffer
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
end Behavioral;""",
        "base_luts": 45,
        "base_ffs": 36,
        "base_bram": 1,
        "base_dsp": 0,
        "t_logic_ns": 1.40
    }
}


class FpgaSynthesisEngine:
    """
    Lightweight, high-precision FPGA synthesis estimation and logic analyzer trace engine.
    Computes LUT/FF utilization, timing metrics (WNS, TNS, Fmax), generates multi-channel
    timing traces, and saves results in SQLite WAL tables without polling loops.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_sqlite_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns SQLite connection configured with WAL journaling."""
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite_tables(self) -> None:
        """Initializes tables for FPGA synthesis runs and logic analyzer traces."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fpga_synthesis_runs (
                    id TEXT PRIMARY KEY,
                    target_fpga TEXT NOT NULL,
                    module_key TEXT NOT NULL,
                    hdl_type TEXT NOT NULL,
                    luts_used INTEGER NOT NULL,
                    luts_total INTEGER NOT NULL,
                    ffs_used INTEGER NOT NULL,
                    ffs_total INTEGER NOT NULL,
                    bram_used INTEGER NOT NULL,
                    bram_total INTEGER NOT NULL,
                    dsp_used INTEGER NOT NULL,
                    dsp_total INTEGER NOT NULL,
                    fmax_mhz REAL NOT NULL,
                    min_period_ns REAL NOT NULL,
                    setup_slack_ns REAL NOT NULL,
                    hold_slack_ns REAL NOT NULL,
                    student_id TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS logic_analyzer_traces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    synthesis_id TEXT NOT NULL,
                    cycle_index INTEGER NOT NULL,
                    time_ns REAL NOT NULL,
                    clk INTEGER NOT NULL,
                    reset INTEGER NOT NULL,
                    enable INTEGER NOT NULL,
                    data_in_hex TEXT NOT NULL,
                    data_out_hex TEXT NOT NULL,
                    fsm_state TEXT NOT NULL,
                    flags TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(synthesis_id) REFERENCES fpga_synthesis_runs(id)
                );
            """)
            conn.commit()

    def get_available_targets(self) -> List[Dict[str, Any]]:
        """Returns catalog of supported FPGA hardware targets."""
        return list(FPGA_TARGETS.values())

    def get_available_modules(self) -> List[Dict[str, Any]]:
        """Returns catalog of synthesizable HDL module templates."""
        modules = []
        for mod in HDL_MODULES.values():
            modules.append({
                "key": mod["key"],
                "title": mod["title"],
                "category": mod["category"],
                "base_luts": mod["base_luts"],
                "base_ffs": mod["base_ffs"],
                "base_bram": mod["base_bram"],
                "base_dsp": mod["base_dsp"]
            })
        return modules

    def get_module_source(self, module_key: str, hdl_type: str = "VERILOG") -> Dict[str, Any]:
        """Returns HDL source code and module metadata."""
        mod = HDL_MODULES.get(module_key, HDL_MODULES["CLOCK_DIVIDER_COUNTER"])
        hdl = hdl_type.upper()
        source = mod["verilog_source"] if hdl == "VERILOG" else mod["vhdl_source"]
        return {
            "module_key": mod["key"],
            "title": mod["title"],
            "category": mod["category"],
            "hdl_type": hdl,
            "source_code": source
        }

    def synthesize_module(
        self,
        target_fpga: str = "XILINX_ARTIX7_XC7A35T",
        module_key: str = "CLOCK_DIVIDER_COUNTER",
        hdl_type: str = "VERILOG",
        target_clock_mhz: float = 100.0,
        student_id: str = "2023MITEC042"
    ) -> Dict[str, Any]:
        """
        Executes deterministic synthesis estimation and static timing analysis (STA).
        Calculates LUT/FF utilization, minimum clock period, setup slack (WNS), and Fmax.
        Persists report into SQLite WAL without background polling.
        """
        target = FPGA_TARGETS.get(target_fpga, FPGA_TARGETS["XILINX_ARTIX7_XC7A35T"])
        mod = HDL_MODULES.get(module_key, HDL_MODULES["CLOCK_DIVIDER_COUNTER"])

        # Target-scaled synthesis utilization
        scale = 1.0 if "ARTIX7" in target["key"] else (1.15 if "CYCLONE" in target["key"] else 1.30)
        luts_used = int(math.ceil(mod["base_luts"] * scale))
        ffs_used = int(math.ceil(mod["base_ffs"] * scale))
        bram_used = mod["base_bram"]
        dsp_used = mod["base_dsp"]

        luts_pct = round((luts_used / target["luts_total"]) * 100.0, 3)
        ffs_pct = round((ffs_used / target["ffs_total"]) * 100.0, 3)
        bram_pct = round((bram_used / target["bram_36k_total"]) * 100.0, 3) if target["bram_36k_total"] > 0 else 0.0
        dsp_pct = round((dsp_used / target["dsp_slices_total"]) * 100.0, 3) if target["dsp_slices_total"] > 0 else 0.0

        # Static Timing Analysis (STA)
        # T_crit = T_co + T_logic + (T_route_factor * 0.45) + T_su
        t_co = target["t_co_typical_ns"]
        t_su = target["t_su_typical_ns"]
        t_logic = mod["t_logic_ns"]
        t_route = target["t_route_factor"] * 0.45
        t_crit_ns = round(t_co + t_logic + t_route + t_su, 3)

        # Maximum Operating Frequency
        fmax_mhz = min(target["max_pll_freq_mhz"], round(1000.0 / t_crit_ns, 2))

        # Setup slack with respect to user's target clock
        target_period_ns = round(1000.0 / target_clock_mhz, 3)
        setup_slack_ns = round(target_period_ns - t_crit_ns, 3)
        hold_slack_ns = round(t_co - target["t_su_typical_ns"] + 0.12, 3)
        timing_met = setup_slack_ns >= 0.0 and hold_slack_ns >= 0.0

        run_id = f"SYNTH_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(2).hex()}"
        timestamp = datetime.now().isoformat()

        # Persist to SQLite WAL
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO fpga_synthesis_runs (
                    id, target_fpga, module_key, hdl_type,
                    luts_used, luts_total, ffs_used, ffs_total,
                    bram_used, bram_total, dsp_used, dsp_total,
                    fmax_mhz, min_period_ns, setup_slack_ns, hold_slack_ns,
                    student_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                run_id, target["key"], mod["key"], hdl_type.upper(),
                luts_used, target["luts_total"], ffs_used, target["ffs_total"],
                bram_used, target["bram_36k_total"], dsp_used, target["dsp_slices_total"],
                fmax_mhz, t_crit_ns, setup_slack_ns, hold_slack_ns,
                student_id, timestamp
            ))
            conn.commit()

        return {
            "status": "SUCCESS",
            "synthesis_id": run_id,
            "target_fpga": target,
            "module": {
                "key": mod["key"],
                "title": mod["title"],
                "category": mod["category"]
            },
            "hdl_type": hdl_type.upper(),
            "target_clock_mhz": target_clock_mhz,
            "target_period_ns": target_period_ns,
            "utilization": {
                "luts_used": luts_used,
                "luts_total": target["luts_total"],
                "luts_pct": luts_pct,
                "ffs_used": ffs_used,
                "ffs_total": target["ffs_total"],
                "ffs_pct": ffs_pct,
                "bram_used": bram_used,
                "bram_total": target["bram_36k_total"],
                "bram_pct": bram_pct,
                "dsp_used": dsp_used,
                "dsp_total": target["dsp_slices_total"],
                "dsp_pct": dsp_pct
            },
            "timing_metrics": {
                "fmax_mhz": fmax_mhz,
                "min_period_ns": t_crit_ns,
                "setup_slack_ns": setup_slack_ns,
                "hold_slack_ns": hold_slack_ns,
                "timing_met": timing_met,
                "t_co_ns": t_co,
                "t_logic_ns": t_logic,
                "t_route_ns": round(t_route, 3),
                "t_su_ns": t_su
            },
            "platform_lead": "Ashok Kumar A (2023MITEC042)",
            "institution": "MIT Campus, Anna University",
            "timestamp": timestamp
        }

    def generate_logic_analyzer_traces(
        self,
        module_key: str = "CLOCK_DIVIDER_COUNTER",
        cycles: int = 32,
        clk_period_ns: float = 10.0,
        synthesis_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates simulated multi-channel logic analyzer waveform cycles for the specified HDL module.
        Channels modeled: CLK, RESET, ENABLE, DATA_IN[7:0], DATA_OUT[7:0], FSM_STATE, and Flags.
        Saves traces to SQLite WAL and returns JSON data.
        """
        mod = HDL_MODULES.get(module_key, HDL_MODULES["CLOCK_DIVIDER_COUNTER"])
        cycles = max(8, min(cycles, 64))
        traces: List[Dict[str, Any]] = []

        now_str = datetime.now().isoformat()
        synth_id = synthesis_id or f"SYNTH_AUTO_{os.urandom(3).hex()}"

        # State tracking variables
        counter_val = 0
        uart_state = 0  # 0: IDLE, 1: START, 2: DATA, 3: STOP
        uart_bit_idx = 0
        uart_shift_data = 0xA5
        uart_tx_line = 1

        alu_acc = 0x00
        fifo_buffer: List[int] = []
        fifo_head = 0

        for c in range(cycles):
            time_ns = round(c * clk_period_ns, 2)
            # Reset active for first 2 cycles
            rst = 1 if c < 2 else 0
            # Enable active on and off to simulate control gating
            en = 1 if (c >= 2 and (c % 10 != 8)) else 0

            din_val = 0x00
            dout_val = 0x00
            fsm_str = "IDLE (00)"
            flags_str = "NONE"

            if mod["key"] == "CLOCK_DIVIDER_COUNTER":
                din_val = (c * 3) & 0xFF
                if rst == 1:
                    counter_val = 0
                elif en == 1:
                    counter_val = (counter_val + 1) & 0x0F
                dout_val = counter_val
                tc = 1 if (counter_val == 0x0F and en == 1) else 0
                div2 = counter_val & 0x01
                div4 = (counter_val >> 1) & 0x01
                div8 = (counter_val >> 2) & 0x01
                div16 = (counter_val >> 3) & 0x01
                fsm_str = f"Q={counter_val:X}h"
                flags_str = f"TC={'1' if tc else '0'}|D2={div2}|D4={div4}|D8={div8}|D16={div16}"

            elif mod["key"] == "UART_TX_FSM":
                din_val = 0x4D if (c % 16 < 8) else 0x54  # Ascii 'M' and 'T'
                if rst == 1:
                    uart_state = 0
                    uart_tx_line = 1
                    uart_bit_idx = 0
                else:
                    if uart_state == 0:  # IDLE
                        uart_tx_line = 1
                        fsm_str = "IDLE (00)"
                        if c >= 3 and (c % 12 == 3):
                            uart_state = 1
                            uart_shift_data = din_val
                    elif uart_state == 1:  # START
                        uart_tx_line = 0
                        fsm_str = "START (01)"
                        uart_state = 2
                        uart_bit_idx = 0
                    elif uart_state == 2:  # DATA
                        uart_tx_line = (uart_shift_data >> uart_bit_idx) & 0x01
                        fsm_str = f"DATA_BIT[{uart_bit_idx}] (10)"
                        uart_bit_idx += 1
                        if uart_bit_idx >= 8:
                            uart_state = 3
                    elif uart_state == 3:  # STOP
                        uart_tx_line = 1
                        fsm_str = "STOP (11)"
                        uart_state = 0

                dout_val = 0x01 if uart_tx_line else 0x00
                flags_str = f"TX={'HIGH' if uart_tx_line else 'LOW'}|BUSY={'1' if uart_state != 0 else '0'}"

            elif mod["key"] == "PIPELINED_ALU_8BIT":
                din_val = (c * 7 + 0x11) & 0xFF
                operand_b = 0x05
                op_code = (c // 5) % 6
                op_names = ["ADD", "SUB", "AND", "OR", "XOR", "SHL"]
                cur_op = op_names[op_code]

                if rst == 1:
                    alu_acc = 0x00
                    carry = 0
                    zero = 1
                else:
                    if cur_op == "ADD":
                        full_res = din_val + operand_b
                    elif cur_op == "SUB":
                        full_res = din_val - operand_b if din_val >= operand_b else (256 + din_val - operand_b)
                    elif cur_op == "AND":
                        full_res = din_val & operand_b
                    elif cur_op == "OR":
                        full_res = din_val | operand_b
                    elif cur_op == "XOR":
                        full_res = din_val ^ operand_b
                    elif cur_op == "SHL":
                        full_res = (din_val << 1) & 0x1FF
                    else:
                        full_res = 0

                    alu_acc = full_res & 0xFF
                    carry = 1 if full_res > 255 else 0
                    zero = 1 if alu_acc == 0 else 0

                dout_val = alu_acc
                fsm_str = f"OP={cur_op}"
                flags_str = f"ZERO={zero}|CARRY={carry}"

            elif mod["key"] == "FIFO_BUFFER_8X8":
                din_val = (0x30 + c) & 0xFF
                wr_pulse = 1 if (c in [2, 3, 4, 5, 8, 9, 12, 13]) else 0
                rd_pulse = 1 if (c in [6, 7, 10, 11, 14, 15, 16]) else 0

                if rst == 1:
                    fifo_buffer = []
                    dout_val = 0x00
                else:
                    if wr_pulse and len(fifo_buffer) < 8:
                        fifo_buffer.append(din_val)
                    if rd_pulse and len(fifo_buffer) > 0:
                        dout_val = fifo_buffer.pop(0)

                is_full = 1 if len(fifo_buffer) >= 8 else 0
                is_empty = 1 if len(fifo_buffer) == 0 else 0
                fsm_str = f"DEPTH={len(fifo_buffer)}/8"
                flags_str = f"FULL={is_full}|EMPTY={is_empty}|WR={wr_pulse}|RD={rd_pulse}"

            trace_entry = {
                "cycle": c,
                "time_ns": time_ns,
                "clk": 1 if (c % 2 == 0) else 0,
                "reset": rst,
                "enable": en,
                "data_in_hex": f"0x{din_val:02X}",
                "data_in_dec": din_val,
                "data_out_hex": f"0x{dout_val:02X}",
                "data_out_dec": dout_val,
                "fsm_state": fsm_str,
                "flags": flags_str
            }
            traces.append(trace_entry)

        # Bulk write traces to SQLite WAL
        with self._get_connection() as conn:
            conn.executemany("""
                INSERT INTO logic_analyzer_traces (
                    synthesis_id, cycle_index, time_ns, clk, reset, enable,
                    data_in_hex, data_out_hex, fsm_state, flags, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, [
                (
                    synth_id, t["cycle"], t["time_ns"], t["clk"], t["reset"], t["enable"],
                    t["data_in_hex"], t["data_out_hex"], t["fsm_state"], t["flags"], now_str
                ) for t in traces
            ])
            conn.commit()

        return {
            "status": "SUCCESS",
            "synthesis_id": synth_id,
            "module_key": mod["key"],
            "title": mod["title"],
            "cycles_count": len(traces),
            "clock_period_ns": clk_period_ns,
            "traces": traces,
            "generated_at": now_str
        }

    def get_synthesis_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns recent FPGA synthesis runs from SQLite WAL."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM fpga_synthesis_runs
                ORDER BY created_at DESC
                LIMIT ?;
            """, (limit,)).fetchall()
            return [dict(r) for r in rows]

    def export_traces_csv(
        self,
        module_key: str = "CLOCK_DIVIDER_COUNTER",
        cycles: int = 32,
        clk_period_ns: float = 10.0
    ) -> str:
        """Exports logic analyzer waveform traces formatted as RFC-4180 CSV."""
        trace_data = self.generate_logic_analyzer_traces(module_key, cycles, clk_period_ns)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        # CSV Header
        writer.writerow([
            "Cycle", "Time_ns", "CLK", "RESET", "ENABLE",
            "DATA_IN_HEX", "DATA_IN_DEC", "DATA_OUT_HEX", "DATA_OUT_DEC",
            "FSM_STATE", "FLAGS"
        ])

        for t in trace_data["traces"]:
            writer.writerow([
                t["cycle"],
                t["time_ns"],
                t["clk"],
                t["reset"],
                t["enable"],
                t["data_in_hex"],
                t["data_in_dec"],
                t["data_out_hex"],
                t["data_out_dec"],
                t["fsm_state"],
                t["flags"]
            ])

        return output.getvalue()


# Singleton Instance
fpga_synthesis_engine = FpgaSynthesisEngine()
