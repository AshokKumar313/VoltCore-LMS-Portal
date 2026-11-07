"""
========================================================================================
VoltCore Apex Academia - RISC-V 5-Stage Pipelined Processor Architect
Phase 20: RV32I Core, Hazard Detection, Data Forwarding, Stalls, & Cycle-Accurate Simulator
Lead Processor Microarchitect & Digital Design Specialist: Ashok Kumar A
========================================================================================
Features:
  1. Complete RV32I 5-Stage Instruction Pipeline:
     - IF (Instruction Fetch): Program Counter (PC), Instruction Memory fetch, PC+4.
     - ID (Instruction Decode & RegRead): Opcode decoding, 32-register bank read, immediate gen.
     - EX (Execute / ALU): Arithmetic/logical operations, branch condition evaluation.
     - MEM (Data Memory Access): Synchronous word memory load (LW) and store (SW).
     - WB (Register Write-Back): Destination register commit with x0 hardwired to zero.
  2. Data Forwarding Unit:
     - EX -> EX Forwarding: Direct bypassing from EX/MEM to EX stage for rs1 and rs2.
     - MEM -> EX Forwarding: Direct bypassing from MEM/WB to EX stage for rs1 and rs2.
     - Priority arbitration: EX/MEM forwarding takes precedence over MEM/WB forwarding.
  3. Hazard Detection & Control Unit:
     - Load-Use Hazard Detection: Injects 1-cycle bubble into ID/EX, freezes PC & IF/ID.
     - Branch / Jump Control Hazard: Pipeline flush on taken BEQ, BNE, or JAL instructions.
  4. Telemetry & Analytics:
     - Cycles, retired instructions, CPI (Cycles Per Instruction), IPC (Instructions Per Cycle).
     - Dynamic stall count, forwarding events count, branch flushes, register snapshots.
     - Cycle-by-cycle stage occupancy trace: IF, ID, EX, MEM, WB status.
  5. SQLite WAL Mode Persistence:
     - Logged in table 'riscv_processor_history' in voltcore_telemetry.db.
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU usage (<5%).
========================================================================================
"""

import os
import re
import copy
import json
import time
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Union

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")

# Register Name to Index Mapping (ABI + Numerical)
ABI_REGISTER_MAP: Dict[str, int] = {
    "zero": 0, "x0": 0,
    "ra": 1,   "x1": 1,
    "sp": 2,   "x2": 2,
    "gp": 3,   "x3": 3,
    "tp": 4,   "x4": 4,
    "t0": 5,   "x5": 5,
    "t1": 6,   "x6": 6,
    "t2": 7,   "x7": 7,
    "s0": 8,   "fp": 8, "x8": 8,
    "s1": 9,   "x9": 9,
    "a0": 10,  "x10": 10,
    "a1": 11,  "x11": 11,
    "a2": 12,  "x12": 12,
    "a3": 13,  "x13": 13,
    "a4": 14,  "x14": 14,
    "a5": 15,  "x15": 15,
    "a6": 16,  "x16": 16,
    "a7": 17,  "x17": 17,
    "s2": 18,  "x18": 18,
    "s3": 19,  "x19": 19,
    "s4": 20,  "x20": 20,
    "s5": 21,  "x21": 21,
    "s6": 22,  "x22": 22,
    "s7": 23,  "x23": 23,
    "s8": 24,  "x24": 24,
    "s9": 25,  "x25": 25,
    "s10": 26, "x26": 26,
    "s11": 27, "x27": 27,
    "t3": 28,  "x28": 28,
    "t4": 29,  "x29": 29,
    "t5": 30,  "x30": 30,
    "t6": 31,  "x31": 31,
}

REGISTER_NAMES = [f"x{i}" for i in range(32)]


def to_signed_32(val: int) -> int:
    """Converts an integer to a 32-bit signed integer."""
    val = val & 0xFFFFFFFF
    if val & 0x80000000:
        return val - 0x100000000
    return val


def to_uint_32(val: int) -> int:
    """Converts an integer to a 32-bit unsigned representation."""
    return val & 0xFFFFFFFF


class RiscVInstruction:
    """Represents a decoded RV32I instruction."""

    def __init__(
        self,
        raw_str: str,
        opcode: str,
        rd: int = 0,
        rs1: int = 0,
        rs2: int = 0,
        imm: int = 0,
        label: Optional[str] = None,
        pc: int = 0,
    ) -> None:
        self.raw_str = raw_str
        self.opcode = opcode.upper()
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm
        self.label = label
        self.pc = pc

        # Control Signals
        self.is_alu_reg = self.opcode in ("ADD", "SUB", "AND", "OR", "XOR", "SLT")
        self.is_alu_imm = self.opcode in ("ADDI",)
        self.is_load = self.opcode in ("LW",)
        self.is_store = self.opcode in ("SW",)
        self.is_branch = self.opcode in ("BEQ", "BNE")
        self.is_jal = self.opcode in ("JAL",)
        self.is_nop = self.opcode in ("NOP",)

        self.reg_write = (self.is_alu_reg or self.is_alu_imm or self.is_load or self.is_jal) and (self.rd != 0)
        self.mem_read = self.is_load
        self.mem_write = self.is_store

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pc": self.pc,
            "raw": self.raw_str,
            "opcode": self.opcode,
            "rd": self.rd,
            "rs1": self.rs1,
            "rs2": self.rs2,
            "imm": self.imm,
            "reg_write": self.reg_write,
            "mem_read": self.mem_read,
            "mem_write": self.mem_write,
            "is_branch": self.is_branch,
            "is_jal": self.is_jal,
        }


class RiscVAssembler:
    """Assembles RV32I text assembly into executable instruction objects."""

    @staticmethod
    def parse_register(reg_token: str) -> int:
        clean = reg_token.strip().lower().replace(",", "")
        if clean in ABI_REGISTER_MAP:
            return ABI_REGISTER_MAP[clean]
        if clean.startswith("x") and clean[1:].isdigit():
            idx = int(clean[1:])
            if 0 <= idx < 32:
                return idx
        raise ValueError(f"Unknown RISC-V register identifier: '{reg_token}'")

    @staticmethod
    def parse_immediate(imm_token: str) -> int:
        clean = imm_token.strip().replace(",", "")
        if clean.startswith("0x") or clean.startswith("0X"):
            return int(clean, 16)
        if clean.startswith("-0x") or clean.startswith("-0X"):
            return -int(clean[1:], 16)
        return int(clean)

    @classmethod
    def assemble(cls, assembly_code: str) -> List[RiscVInstruction]:
        lines = assembly_code.strip().split("\n")
        instructions: List[RiscVInstruction] = []
        labels: Dict[str, int] = {}
        cleaned_lines: List[Tuple[int, str]] = []

        pc = 0
        # Pass 1: Record labels and strip comments
        for raw_line in lines:
            line = raw_line.split("#")[0].split("//")[0].strip()
            if not line:
                continue

            # Check for label definition
            if ":" in line:
                label_part, rest = line.split(":", 1)
                label_name = label_part.strip()
                labels[label_name] = pc
                line = rest.strip()
                if not line:
                    continue

            cleaned_lines.append((pc, line))
            pc += 4

        # Pass 2: Parse instructions
        for instr_pc, line in cleaned_lines:
            tokens = re.split(r"[,\s]+", line)
            tokens = [t.strip() for t in tokens if t.strip()]
            if not tokens:
                continue

            opcode = tokens[0].upper()

            if opcode == "NOP":
                instructions.append(RiscVInstruction(line, "NOP", rd=0, rs1=0, rs2=0, imm=0, pc=instr_pc))
            elif opcode in ("ADD", "SUB", "AND", "OR", "XOR", "SLT"):
                # Format: ADD rd, rs1, rs2
                rd = cls.parse_register(tokens[1])
                rs1 = cls.parse_register(tokens[2])
                rs2 = cls.parse_register(tokens[3])
                instructions.append(RiscVInstruction(line, opcode, rd=rd, rs1=rs1, rs2=rs2, pc=instr_pc))
            elif opcode == "ADDI":
                # Format: ADDI rd, rs1, imm
                rd = cls.parse_register(tokens[1])
                rs1 = cls.parse_register(tokens[2])
                imm = cls.parse_immediate(tokens[3])
                instructions.append(RiscVInstruction(line, opcode, rd=rd, rs1=rs1, imm=imm, pc=instr_pc))
            elif opcode == "LW":
                # Format: LW rd, offset(rs1) OR LW rd, rs1, offset
                rd = cls.parse_register(tokens[1])
                load_match = re.match(r"(-?\d+|0x[0-9a-fA-F]+)\s*\(\s*([a-zA-Z0-9_]+)\s*\)", tokens[2])
                if load_match:
                    imm = cls.parse_immediate(load_match.group(1))
                    rs1 = cls.parse_register(load_match.group(2))
                elif len(tokens) >= 4:
                    rs1 = cls.parse_register(tokens[2])
                    imm = cls.parse_immediate(tokens[3])
                else:
                    raise ValueError(f"Malformed LW instruction: {line}")
                instructions.append(RiscVInstruction(line, opcode, rd=rd, rs1=rs1, imm=imm, pc=instr_pc))
            elif opcode == "SW":
                # Format: SW rs2, offset(rs1) OR SW rs2, rs1, offset
                rs2 = cls.parse_register(tokens[1])
                store_match = re.match(r"(-?\d+|0x[0-9a-fA-F]+)\s*\(\s*([a-zA-Z0-9_]+)\s*\)", tokens[2])
                if store_match:
                    imm = cls.parse_immediate(store_match.group(1))
                    rs1 = cls.parse_register(store_match.group(2))
                elif len(tokens) >= 4:
                    rs1 = cls.parse_register(tokens[2])
                    imm = cls.parse_immediate(tokens[3])
                else:
                    raise ValueError(f"Malformed SW instruction: {line}")
                instructions.append(RiscVInstruction(line, opcode, rd=0, rs1=rs1, rs2=rs2, imm=imm, pc=instr_pc))
            elif opcode in ("BEQ", "BNE"):
                # Format: BEQ rs1, rs2, label/offset
                rs1 = cls.parse_register(tokens[1])
                rs2 = cls.parse_register(tokens[2])
                target = tokens[3]
                if target in labels:
                    target_pc = labels[target]
                    imm = target_pc - instr_pc
                else:
                    imm = cls.parse_immediate(target)
                instructions.append(RiscVInstruction(line, opcode, rd=0, rs1=rs1, rs2=rs2, imm=imm, pc=instr_pc))
            elif opcode in ("JAL", "J"):
                # Format: JAL rd, label/offset OR JAL label (defaults rd=ra=1) OR J label (defaults rd=x0=0)
                if opcode == "J":
                    rd = 0
                    target = tokens[1]
                elif len(tokens) == 2:
                    rd = 1  # default ra
                    target = tokens[1]
                else:
                    rd = cls.parse_register(tokens[1])
                    target = tokens[2]

                if target in labels:
                    target_pc = labels[target]
                    imm = target_pc - instr_pc
                else:
                    imm = cls.parse_immediate(target)
                instructions.append(RiscVInstruction(line, "JAL", rd=rd, imm=imm, pc=instr_pc))
            else:
                raise ValueError(f"Unsupported RISC-V opcode: '{opcode}'")

        return instructions


class RiscV5StagePipeline:
    """
    Simulates a cycle-accurate 5-stage RISC-V RV32I Processor.
    Stages: IF -> ID -> EX -> MEM -> WB.
    Includes Forwarding Unit and Load-Use Hazard Stall Detection.
    """

    def __init__(self, initial_memory: Optional[Dict[int, int]] = None) -> None:
        # Architectural State
        self.registers: List[int] = [0] * 32
        self.memory: Dict[int, int] = copy.deepcopy(initial_memory) if initial_memory else {}
        self.pc: int = 0

        # Program Memory (PC -> RiscVInstruction)
        self.instruction_memory: Dict[int, RiscVInstruction] = {}
        self.program_length: int = 0

        # Pipeline Registers
        self.IF_ID: Optional[Dict[str, Any]] = None
        self.ID_EX: Optional[Dict[str, Any]] = None
        self.EX_MEM: Optional[Dict[str, Any]] = None
        self.MEM_WB: Optional[Dict[str, Any]] = None

        # Telemetry & Metrics
        self.cycle_count: int = 0
        self.instructions_retired: int = 0
        self.stalls_count: int = 0
        self.forwarding_events: int = 0
        self.branch_flushes: int = 0
        self.cycle_trace: List[Dict[str, Any]] = []

    def load_program(self, program: Union[str, List[RiscVInstruction]]) -> None:
        """Loads and resets program into instruction memory."""
        if isinstance(program, str):
            instr_list = RiscVAssembler.assemble(program)
        else:
            instr_list = program

        self.instruction_memory.clear()
        for instr in instr_list:
            self.instruction_memory[instr.pc] = instr
        self.program_length = len(instr_list) * 4

        self.reset()

    def reset(self) -> None:
        """Resets processor state."""
        self.registers = [0] * 32
        self.pc = 0
        self.IF_ID = None
        self.ID_EX = None
        self.EX_MEM = None
        self.MEM_WB = None
        self.cycle_count = 0
        self.instructions_retired = 0
        self.stalls_count = 0
        self.forwarding_events = 0
        self.branch_flushes = 0
        self.cycle_trace.clear()

    def is_pipeline_empty(self) -> bool:
        """Checks if all pipeline stages are empty and PC is beyond instruction memory."""
        all_empty = (
            self.IF_ID is None
            and self.ID_EX is None
            and self.EX_MEM is None
            and self.MEM_WB is None
        )
        return all_empty and (self.pc >= self.program_length or self.pc not in self.instruction_memory)

    def step(self) -> Dict[str, Any]:
        """
        Advances the 5-stage pipeline by exactly one clock cycle.
        Executes stages in reverse (WB -> MEM -> EX -> ID -> IF)
        to cleanly reflect intra-cycle latching.
        """
        self.cycle_count += 1
        trace_entry: Dict[str, Any] = {
            "cycle": self.cycle_count,
            "pc": self.pc,
            "IF": "-",
            "ID": "-",
            "EX": "-",
            "MEM": "-",
            "WB": "-",
            "stall": False,
            "flushed": False,
            "forward_a": "NONE",
            "forward_b": "NONE",
        }

        # -------------------------------------------------------------
        # 1. WB Stage (Write-Back)
        # -------------------------------------------------------------
        if self.MEM_WB is not None:
            wb_instr = self.MEM_WB["instr"]
            wb_rd = self.MEM_WB["rd"]
            wb_val = self.MEM_WB["write_data"]
            trace_entry["WB"] = wb_instr.raw_str

            if self.MEM_WB["reg_write"] and wb_rd != 0:
                self.registers[wb_rd] = to_signed_32(wb_val)

            # Invariant: Register x0 is always hardwired to 0
            self.registers[0] = 0
            self.instructions_retired += 1

        # -------------------------------------------------------------
        # 2. MEM Stage (Memory Access)
        # -------------------------------------------------------------
        next_MEM_WB = None
        if self.EX_MEM is not None:
            mem_instr = self.EX_MEM["instr"]
            alu_res = self.EX_MEM["alu_result"]
            store_val = self.EX_MEM["store_data"]
            trace_entry["MEM"] = mem_instr.raw_str

            write_data = alu_res
            if self.EX_MEM["mem_read"]:
                # Load Word from data memory
                write_data = self.memory.get(alu_res, 0)
            elif self.EX_MEM["mem_write"]:
                # Store Word into data memory
                self.memory[alu_res] = to_signed_32(store_val)

            next_MEM_WB = {
                "instr": mem_instr,
                "rd": self.EX_MEM["rd"],
                "write_data": write_data,
                "reg_write": self.EX_MEM["reg_write"],
            }

        # -------------------------------------------------------------
        # 3. EX Stage (Execute & Forwarding)
        # -------------------------------------------------------------
        next_EX_MEM = None
        branch_taken = False
        branch_target = self.pc

        if self.ID_EX is not None:
            ex_instr = self.ID_EX["instr"]
            trace_entry["EX"] = ex_instr.raw_str

            # Operand Resolution via Forwarding Unit
            op_a = self.ID_EX["rdata1"]
            op_b = self.ID_EX["rdata2"]
            store_data = self.ID_EX["rdata2"]

            # Forwarding for Operand A (rs1)
            # EX/MEM Forwarding has higher priority than MEM/WB
            if (
                self.EX_MEM is not None
                and self.EX_MEM["reg_write"]
                and self.EX_MEM["rd"] != 0
                and self.EX_MEM["rd"] == self.ID_EX["rs1"]
            ):
                op_a = self.EX_MEM["alu_result"]
                trace_entry["forward_a"] = f"EX/MEM(x{self.EX_MEM['rd']})"
                self.forwarding_events += 1
            elif (
                self.MEM_WB is not None
                and self.MEM_WB["reg_write"]
                and self.MEM_WB["rd"] != 0
                and self.MEM_WB["rd"] == self.ID_EX["rs1"]
            ):
                op_a = self.MEM_WB["write_data"]
                trace_entry["forward_a"] = f"MEM/WB(x{self.MEM_WB['rd']})"
                self.forwarding_events += 1

            # Forwarding for Operand B (rs2)
            if (
                self.EX_MEM is not None
                and self.EX_MEM["reg_write"]
                and self.EX_MEM["rd"] != 0
                and self.EX_MEM["rd"] == self.ID_EX["rs2"]
            ):
                store_data = self.EX_MEM["alu_result"]
                if not (ex_instr.is_alu_imm or ex_instr.is_load):
                    op_b = self.EX_MEM["alu_result"]
                trace_entry["forward_b"] = f"EX/MEM(x{self.EX_MEM['rd']})"
                self.forwarding_events += 1
            elif (
                self.MEM_WB is not None
                and self.MEM_WB["reg_write"]
                and self.MEM_WB["rd"] != 0
                and self.MEM_WB["rd"] == self.ID_EX["rs2"]
            ):
                store_data = self.MEM_WB["write_data"]
                if not (ex_instr.is_alu_imm or ex_instr.is_load):
                    op_b = self.MEM_WB["write_data"]
                trace_entry["forward_b"] = f"MEM/WB(x{self.MEM_WB['rd']})"
                self.forwarding_events += 1

            # Select ALU Input B: immediate for I-type/Load/Store, register for R-type/Branch
            alu_in_b = self.ID_EX["imm"] if (ex_instr.is_alu_imm or ex_instr.is_load or ex_instr.is_store) else op_b

            # ALU Computation
            alu_res = 0
            if ex_instr.opcode in ("ADD", "ADDI"):
                alu_res = to_signed_32(op_a + alu_in_b)
            elif ex_instr.opcode == "SUB":
                alu_res = to_signed_32(op_a - alu_in_b)
            elif ex_instr.opcode == "AND":
                alu_res = to_signed_32(op_a & alu_in_b)
            elif ex_instr.opcode == "OR":
                alu_res = to_signed_32(op_a | alu_in_b)
            elif ex_instr.opcode == "XOR":
                alu_res = to_signed_32(op_a ^ alu_in_b)
            elif ex_instr.opcode == "SLT":
                alu_res = 1 if (op_a < alu_in_b) else 0
            elif ex_instr.is_load or ex_instr.is_store:
                alu_res = to_signed_32(op_a + self.ID_EX["imm"])
            elif ex_instr.is_jal:
                alu_res = self.ID_EX["pc"] + 4  # Return address
                branch_taken = True
                branch_target = self.ID_EX["pc"] + self.ID_EX["imm"]

            # Branch Evaluation
            if ex_instr.is_branch:
                if ex_instr.opcode == "BEQ" and (op_a == op_b):
                    branch_taken = True
                elif ex_instr.opcode == "BNE" and (op_a != op_b):
                    branch_taken = True

                if branch_taken:
                    branch_target = self.ID_EX["pc"] + self.ID_EX["imm"]

            next_EX_MEM = {
                "instr": ex_instr,
                "rd": self.ID_EX["rd"],
                "alu_result": alu_res,
                "store_data": store_data,
                "reg_write": self.ID_EX["reg_write"],
                "mem_read": self.ID_EX["mem_read"],
                "mem_write": self.ID_EX["mem_write"],
            }

        # -------------------------------------------------------------
        # 4. ID Stage (Decode & Load-Use Hazard Detection)
        # -------------------------------------------------------------
        next_ID_EX = None
        stall_pipeline = False

        if self.IF_ID is not None:
            id_instr = self.IF_ID["instr"]
            trace_entry["ID"] = id_instr.raw_str

            # Load-Use Hazard Detection:
            # If instruction in EX is LW, and its destination matches rs1 or rs2 of instruction in ID
            if self.ID_EX is not None and self.ID_EX["mem_read"] and self.ID_EX["rd"] != 0:
                load_rd = self.ID_EX["rd"]
                needs_rs1 = id_instr.is_alu_reg or id_instr.is_alu_imm or id_instr.is_load or id_instr.is_store or id_instr.is_branch
                needs_rs2 = id_instr.is_alu_reg or id_instr.is_branch or id_instr.is_store

                if (needs_rs1 and id_instr.rs1 == load_rd) or (needs_rs2 and id_instr.rs2 == load_rd and not id_instr.is_store):
                    stall_pipeline = True
                    self.stalls_count += 1
                    trace_entry["stall"] = True

            if not stall_pipeline:
                next_ID_EX = {
                    "instr": id_instr,
                    "pc": self.IF_ID["pc"],
                    "rd": id_instr.rd,
                    "rs1": id_instr.rs1,
                    "rs2": id_instr.rs2,
                    "rdata1": self.registers[id_instr.rs1],
                    "rdata2": self.registers[id_instr.rs2],
                    "imm": id_instr.imm,
                    "reg_write": id_instr.reg_write,
                    "mem_read": id_instr.mem_read,
                    "mem_write": id_instr.mem_write,
                }

        # -------------------------------------------------------------
        # 5. IF Stage (Instruction Fetch)
        # -------------------------------------------------------------
        next_IF_ID = None
        if not stall_pipeline:
            if self.pc in self.instruction_memory:
                fetched_instr = self.instruction_memory[self.pc]
                trace_entry["IF"] = fetched_instr.raw_str
                next_IF_ID = {
                    "instr": fetched_instr,
                    "pc": self.pc,
                }
                self.pc += 4
        else:
            # On stall: preserve current IF_ID and don't advance PC
            next_IF_ID = self.IF_ID
            if self.IF_ID is not None:
                trace_entry["IF"] = f"STALL({self.IF_ID['instr'].raw_str})"

        # -------------------------------------------------------------
        # Branch Flush Arbitration
        # -------------------------------------------------------------
        if branch_taken:
            # Control hazard: flush IF/ID and ID/EX registers
            self.branch_flushes += 1
            trace_entry["flushed"] = True
            self.pc = branch_target
            next_IF_ID = None
            next_ID_EX = None

        # -------------------------------------------------------------
        # Pipeline Register Latching
        # -------------------------------------------------------------
        self.MEM_WB = next_MEM_WB
        self.EX_MEM = next_EX_MEM
        self.ID_EX = next_ID_EX
        self.IF_ID = next_IF_ID

        self.cycle_trace.append(trace_entry)
        return trace_entry

    def run_simulation(self, max_cycles: int = 500) -> Dict[str, Any]:
        """Runs the pipeline until complete drain or max_cycles."""
        while self.cycle_count < max_cycles:
            if self.is_pipeline_empty() and self.cycle_count > 0:
                break
            self.step()

        cpi = round(self.cycle_count / max(1, self.instructions_retired), 3)
        ipc = round(self.instructions_retired / max(1, self.cycle_count), 3)

        reg_dict = {f"x{i}": self.registers[i] for i in range(32)}
        # Add ABI aliases (ra, sp, gp, tp, t0-t6, s0-s11, a0-a7, zero)
        for abi_name, reg_idx in ABI_REGISTER_MAP.items():
            reg_dict[abi_name] = self.registers[reg_idx]

        return {
            "total_cycles": self.cycle_count,
            "instructions_retired": self.instructions_retired,
            "cpi": cpi,
            "ipc": ipc,
            "stalls_count": self.stalls_count,
            "forwarding_events": self.forwarding_events,
            "branch_flushes": self.branch_flushes,
            "final_registers": reg_dict,
            "data_memory": {str(k): v for k, v in self.memory.items()},
            "cycle_trace": self.cycle_trace,
        }


# ========================================================================================
# 3. Processor Engine Singleton with SQLite WAL Persistence
# ========================================================================================
class RiscVProcessorEngine:
    """Wrapper engine for executing and logging RISC-V 5-stage pipeline simulations."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_db(self) -> None:
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS riscv_processor_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        experiment_id TEXT NOT NULL UNIQUE,
                        program_name TEXT NOT NULL,
                        total_cycles INTEGER NOT NULL,
                        instructions_retired INTEGER NOT NULL,
                        cpi REAL NOT NULL,
                        stalls_count INTEGER NOT NULL,
                        forwarding_events INTEGER NOT NULL,
                        branch_flushes INTEGER NOT NULL,
                        metrics_json TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)
                conn.commit()
            finally:
                conn.close()

    def simulate_assembly(
        self,
        assembly_code: str,
        program_name: str = "rv32i_benchmark",
        max_cycles: int = 500,
        initial_memory: Optional[Dict[int, int]] = None,
    ) -> Dict[str, Any]:
        """Runs cycle-accurate RV32I simulation and persists run telemetry."""
        pipeline = RiscV5StagePipeline(initial_memory=initial_memory)
        pipeline.load_program(assembly_code)
        result = pipeline.run_simulation(max_cycles=max_cycles)

        exp_id = f"RV32_{int(time.time() * 1000)}"
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute(
                    """
                    INSERT INTO riscv_processor_history (
                        experiment_id, program_name, total_cycles, instructions_retired,
                        cpi, stalls_count, forwarding_events, branch_flushes, metrics_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        exp_id,
                        program_name,
                        result["total_cycles"],
                        result["instructions_retired"],
                        result["cpi"],
                        result["stalls_count"],
                        result["forwarding_events"],
                        result["branch_flushes"],
                        json.dumps({
                            "cpi": result["cpi"],
                            "ipc": result["ipc"],
                            "final_registers": result["final_registers"],
                            "memory_size": len(result["data_memory"]),
                        }),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.commit()
            except Exception:
                pass
            finally:
                conn.close()

        result["experiment_id"] = exp_id
        result["program_name"] = program_name
        return result

    def get_history(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Retrieves recent RISC-V processor simulation runs from SQLite WAL database."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT id, experiment_id, program_name, total_cycles, instructions_retired,
                           cpi, stalls_count, forwarding_events, branch_flushes, metrics_json, created_at
                    FROM riscv_processor_history
                    ORDER BY id DESC LIMIT ?
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
                results = []
                for r in rows:
                    results.append({
                        "id": r["id"],
                        "experiment_id": r["experiment_id"],
                        "program_name": r["program_name"],
                        "total_cycles": r["total_cycles"],
                        "instructions_retired": r["instructions_retired"],
                        "cpi": r["cpi"],
                        "stalls_count": r["stalls_count"],
                        "forwarding_events": r["forwarding_events"],
                        "branch_flushes": r["branch_flushes"],
                        "metrics": json.loads(r["metrics_json"]) if r["metrics_json"] else {},
                        "created_at": r["created_at"],
                    })
                return results
            except Exception:
                return []
            finally:
                conn.close()


# Singleton Instance
riscv_processor_engine = RiscVProcessorEngine()
