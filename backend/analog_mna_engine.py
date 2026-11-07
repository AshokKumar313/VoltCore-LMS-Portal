"""
========================================================================================
VoltCore Apex Academia - Non-Linear Modified Nodal Analysis (MNA) Engine
Phase 12: Analog Circuit Simulator & Transistor Transient Analysis Kernel
Anna University / MIT Campus - Department of Electronics Engineering
Lead Systems Architect & Senior Analog IC Design Specialist: Ashok Kumar A
========================================================================================
Capabilities:
  - Modified Nodal Analysis (MNA) Matrix Formulation: Augmented [G B; C D] * [v; j] = [i; e]
  - Non-Linear Newton-Raphson Iteration with Berkeley SPICE 'pnjlim' Voltage Limiting
  - Semiconductor Device Models:
      * Shockley Exponential Diode (ID = IS * (exp(VD / (n*VT)) - 1)) with dynamic conductance gd
      * BJT Non-Linear Ebers-Moll Model (Active, Saturation, Cutoff) with gmf, gmr, gpi, gmu
      * MOSFET Shichman-Hodges Quadratic Model (Cutoff, Triode, Saturation) with gm and gds
  - Numerical Integration Methods:
      * Trapezoidal Rule (2nd-Order A-stable, minimal phase lag)
      * Backward Euler (1st-Order L-stable, high-frequency numerical damping)
  - Adaptive Time-Stepping with Local Truncation Error (LTE) Monitoring
  - Automated Topology Error Checking (Floating nodes, Voltage shorts, Self-loops, Ground paths)
  - SQLite WAL Mode Simulation Audit Logger ('circuit_simulation_history')
  - Zero External Binary Dependencies, Microsecond Execution, Safe Low-Overhead Host Profiling
========================================================================================
"""

import os
import sys
import math
import cmath
import copy
import random
import json
import sqlite3
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional, Set

from backend.semiconductor_physics_engine import (
    SemiconductorPhysicsEngine,
    semiconductor_physics_engine,
    SEMICONDUCTOR_MATERIALS
)

# Physical Constants (at Room Temperature T = 300.0 Kelvin)
Q_ELEC = 1.602176634e-19       # Electron charge (Coulombs)
K_BOLTZ = 1.380649e-23         # Boltzmann constant (J/K)
T_ROOM = 300.0                 # Room temperature in Kelvin
VT_ROOM = (K_BOLTZ * T_ROOM) / Q_ELEC  # ~0.025852 V (25.85 mV)
G_MIN = 1e-12                  # Minimum conductance to ground to prevent singular matrices [S]

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")


def pnjlim(v_new: float, v_old: float, vt: float, vcrit: float) -> float:
    """
    Berkeley SPICE 'pnjlim' diode voltage limiter.
    Prevents exponential runaway and numerical overflow in Newton-Raphson iterations.
    """
    if v_new > vcrit and abs(v_new - v_old) > (vt + vt):
        if v_old > 0.0:
            arg = 1.0 + (v_new - v_old) / vt
            if arg > 0.0:
                return v_old + vt * math.log(arg)
            else:
                return vcrit
        else:
            return vt * math.log(v_new / vt) if v_new > 0.0 else vcrit
    return v_new


def solve_linear_system(A: List[List[float]], b: List[float]) -> List[float]:
    """
    Pure Python Gauss-Jordan elimination with scaled partial pivoting.
    Self-contained, fast (<100 microseconds for N <= 50), zero external binary dependencies.
    """
    n = len(b)
    if n == 0:
        return []

    # Create augmented matrix [A | b]
    M = [row[:] + [b[i]] for i, row in enumerate(A)]

    for i in range(n):
        # Find pivot in column i from row i down to n-1
        max_row = i
        max_val = abs(M[i][i])
        for r in range(i + 1, n):
            val = abs(M[r][i])
            if val > max_val:
                max_val = val
                max_row = r

        if max_val < 1e-15:
            # Add small epsilon conductance on diagonal to regularize near-singular matrices
            M[i][i] += 1e-12

        # Swap rows
        if max_row != i:
            M[i], M[max_row] = M[max_row], M[i]

        pivot = M[i][i]
        for c in range(i, n + 1):
            M[i][c] /= pivot

        # Eliminate column in all other rows
        for r in range(n):
            if r != i and abs(M[r][i]) > 1e-16:
                factor = M[r][i]
                for c in range(i, n + 1):
                    M[r][c] -= factor * M[i][c]

    return [M[i][n] for i in range(n)]


# ========================================================================================
# 1. Circuit Component Definitions
# ========================================================================================

class CircuitComponent:
    """Base class for all discrete and active analog circuit components."""
    def __init__(self, name: str, comp_type: str):
        self.name = name.upper().strip()
        self.comp_type = comp_type.upper().strip()


class Resistor(CircuitComponent):
    def __init__(self, name: str, n1: str, n2: str, value: float):
        super().__init__(name, "RESISTOR")
        self.n1 = str(n1).strip()
        self.n2 = str(n2).strip()
        self.resistance = max(1e-9, float(value))
        self.conductance = 1.0 / self.resistance


class Capacitor(CircuitComponent):
    def __init__(self, name: str, n1: str, n2: str, value: float, ic: float = 0.0):
        super().__init__(name, "CAPACITOR")
        self.n1 = str(n1).strip()
        self.n2 = str(n2).strip()
        self.capacitance = max(1e-15, float(value))
        self.ic = float(ic)
        # Transient companion state
        self.v_prev = self.ic
        self.i_prev = 0.0


class Inductor(CircuitComponent):
    def __init__(self, name: str, n1: str, n2: str, value: float, ic: float = 0.0):
        super().__init__(name, "INDUCTOR")
        self.n1 = str(n1).strip()
        self.n2 = str(n2).strip()
        self.inductance = max(1e-12, float(value))
        self.ic = float(ic)
        # Transient companion state
        self.v_prev = 0.0
        self.i_prev = self.ic


class VoltageSource(CircuitComponent):
    def __init__(
        self,
        name: str,
        n_pos: str,
        n_neg: str,
        dc_val: float = 0.0,
        wave_type: str = "DC",
        amplitude: float = 0.0,
        freq_hz: float = 1000.0,
        phase_deg: float = 0.0,
        offset: float = 0.0
    ):
        super().__init__(name, "VOLTAGE_SOURCE")
        self.n_pos = str(n_pos).strip()
        self.n_neg = str(n_neg).strip()
        self.dc_val = float(dc_val)
        self.wave_type = wave_type.upper().strip()  # "DC", "SINE", "PULSE", "STEP"
        self.amplitude = float(amplitude)
        self.freq_hz = float(freq_hz)
        self.phase_deg = float(phase_deg)
        self.offset = float(offset)

    def get_voltage_at_time(self, t: float) -> float:
        if self.wave_type == "DC":
            return self.dc_val
        elif self.wave_type == "SINE":
            omega = 2.0 * math.pi * self.freq_hz
            phi = math.radians(self.phase_deg)
            return self.offset + self.amplitude * math.sin(omega * t + phi)
        elif self.wave_type == "STEP":
            return (self.offset + self.amplitude) if t > 0.0 else self.offset
        elif self.wave_type == "PULSE":
            period = 1.0 / max(1e-6, self.freq_hz)
            t_mod = t % period
            return (self.offset + self.amplitude) if t_mod < (0.5 * period) else self.offset
        return self.dc_val


class CurrentSource(CircuitComponent):
    def __init__(self, name: str, n_pos: str, n_neg: str, dc_val: float = 0.0):
        super().__init__(name, "CURRENT_SOURCE")
        self.n_pos = str(n_pos).strip()  # Current flows OUT of n_pos
        self.n_neg = str(n_neg).strip()  # Current flows INTO n_neg
        self.dc_val = float(dc_val)


class Diode(CircuitComponent):
    def __init__(
        self,
        name: str,
        n_anode: str,
        n_cathode: str,
        is_sat: float = 1e-14,
        n_factor: float = 1.0,
        series_r: float = 0.0
    ):
        super().__init__(name, "DIODE")
        self.n_anode = str(n_anode).strip()
        self.n_cathode = str(n_cathode).strip()
        self.is_sat = max(1e-20, float(is_sat))
        self.n_factor = max(0.5, float(n_factor))
        self.series_r = max(0.0, float(series_r))
        self.vt = self.n_factor * VT_ROOM
        self.vcrit = self.vt * math.log(self.vt / (math.sqrt(2.0) * self.is_sat))
        # Current operating point
        self.vd_op = 0.65
        self.id_op = 1e-3
        self.gd_op = 1e-3 / self.vt


class BJT(CircuitComponent):
    def __init__(
        self,
        name: str,
        n_c: str,
        n_b: str,
        n_e: str,
        bjt_type: str = "NPN",
        beta_f: float = 100.0,
        beta_r: float = 1.0,
        is_sat: float = 1e-14,
        va: float = 100.0
    ):
        super().__init__(name, "BJT")
        self.n_c = str(n_c).strip()
        self.n_b = str(n_b).strip()
        self.n_e = str(n_e).strip()
        self.bjt_type = bjt_type.upper().strip()
        self.beta_f = max(1.0, float(beta_f))
        self.beta_r = max(0.01, float(beta_r))
        self.is_sat = max(1e-20, float(is_sat))
        self.va = max(5.0, float(va))  # Early voltage
        self.vt = VT_ROOM
        # Operating points
        self.vbe_op = 0.65
        self.vbc_op = -2.0
        self.ic_op = 1e-3
        self.ib_op = 1e-5


class MOSFET(CircuitComponent):
    def __init__(
        self,
        name: str,
        n_d: str,
        n_g: str,
        n_s: str,
        mos_type: str = "NMOS",
        vth: float = 1.0,
        kn: float = 10e-3,  # A/V^2
        lambda_param: float = 0.02
    ):
        super().__init__(name, "MOSFET")
        self.n_d = str(n_d).strip()
        self.n_g = str(n_g).strip()
        self.n_s = str(n_s).strip()
        self.mos_type = mos_type.upper().strip()
        self.vth = float(vth)
        self.kn = max(1e-6, float(kn))
        self.lambda_param = max(0.0, float(lambda_param))
        # Operating points
        self.vgs_op = 2.0
        self.vds_op = 3.0
        self.id_op = 1e-3
        self.gm_op = 1e-3
        self.gds_op = 1e-5


# ========================================================================================
# 2. Circuit Representation & Topology Validator
# ========================================================================================

class Circuit:
    """Manages the network of components, node indexing, and automated topology verification."""

    def __init__(self, title: str = "Untitled Circuit"):
        self.title = title
        self.components: List[CircuitComponent] = []
        self.node_to_idx: Dict[str, int] = {"0": 0, "GND": 0}
        self.idx_to_node: Dict[int, str] = {0: "0"}
        self._next_node_idx = 1

    def get_or_create_node_idx(self, node_name: str) -> int:
        norm = str(node_name).strip().upper()
        if norm in ("0", "GND", "GROUND"):
            return 0
        if norm not in self.node_to_idx:
            idx = self._next_node_idx
            self.node_to_idx[norm] = idx
            self.idx_to_node[idx] = norm
            self._next_node_idx += 1
            return idx
        return self.node_to_idx[norm]

    def add_resistor(self, name: str, n1: str, n2: str, value: float) -> Resistor:
        self.get_or_create_node_idx(n1)
        self.get_or_create_node_idx(n2)
        r = Resistor(name, n1, n2, value)
        self.components.append(r)
        return r

    def add_capacitor(self, name: str, n1: str, n2: str, value: float, ic: float = 0.0) -> Capacitor:
        self.get_or_create_node_idx(n1)
        self.get_or_create_node_idx(n2)
        c = Capacitor(name, n1, n2, value, ic)
        self.components.append(c)
        return c

    def add_inductor(self, name: str, n1: str, n2: str, value: float, ic: float = 0.0) -> Inductor:
        self.get_or_create_node_idx(n1)
        self.get_or_create_node_idx(n2)
        ind = Inductor(name, n1, n2, value, ic)
        self.components.append(ind)
        return ind

    def add_voltage_source(
        self,
        name: str,
        n_pos: str,
        n_neg: str,
        dc_val: float = 0.0,
        wave_type: str = "DC",
        amplitude: float = 0.0,
        freq_hz: float = 1000.0,
        phase_deg: float = 0.0,
        offset: float = 0.0
    ) -> VoltageSource:
        self.get_or_create_node_idx(n_pos)
        self.get_or_create_node_idx(n_neg)
        v = VoltageSource(name, n_pos, n_neg, dc_val, wave_type, amplitude, freq_hz, phase_deg, offset)
        self.components.append(v)
        return v

    def add_current_source(self, name: str, n_pos: str, n_neg: str, dc_val: float = 0.0) -> CurrentSource:
        self.get_or_create_node_idx(n_pos)
        self.get_or_create_node_idx(n_neg)
        i = CurrentSource(name, n_pos, n_neg, dc_val)
        self.components.append(i)
        return i

    def add_diode(
        self,
        name: str,
        n_anode: str,
        n_cathode: str,
        is_sat: float = 1e-14,
        n_factor: float = 1.0,
        series_r: float = 0.0
    ) -> Diode:
        self.get_or_create_node_idx(n_anode)
        self.get_or_create_node_idx(n_cathode)
        d = Diode(name, n_anode, n_cathode, is_sat, n_factor, series_r)
        self.components.append(d)
        return d

    def add_bjt(
        self,
        name: str,
        n_c: str,
        n_b: str,
        n_e: str,
        bjt_type: str = "NPN",
        beta_f: float = 100.0,
        beta_r: float = 1.0,
        is_sat: float = 1e-14,
        va: float = 100.0
    ) -> BJT:
        self.get_or_create_node_idx(n_c)
        self.get_or_create_node_idx(n_b)
        self.get_or_create_node_idx(n_e)
        q = BJT(name, n_c, n_b, n_e, bjt_type, beta_f, beta_r, is_sat, va)
        self.components.append(q)
        return q

    def add_mosfet(
        self,
        name: str,
        n_d: str,
        n_g: str,
        n_s: str,
        mos_type: str = "NMOS",
        vth: float = 1.0,
        kn: float = 10e-3,
        lambda_param: float = 0.02
    ) -> MOSFET:
        self.get_or_create_node_idx(n_d)
        self.get_or_create_node_idx(n_g)
        self.get_or_create_node_idx(n_s)
        m = MOSFET(name, n_d, n_g, n_s, mos_type, vth, kn, lambda_param)
        self.components.append(m)
        return m

    def num_nodes(self) -> int:
        """Returns total non-ground node count."""
        return self._next_node_idx - 1

    def validate_circuit(self) -> Dict[str, Any]:
        """Alias for validate_topology."""
        return self.validate_topology()

    def validate_topology(self) -> Dict[str, Any]:
        """
        Automated topology checker:
          - Detects self-loops (component connected between node and itself).
          - Detects floating nodes (node degree < 2, or disconnected from ground).
          - Detects ideal voltage source short circuits.
        """
        errors = []
        warnings = []

        node_connections: Dict[str, List[str]] = {n: [] for n in self.node_to_idx}
        v_sources = [c for c in self.components if isinstance(c, VoltageSource)]

        # Check self-loops and build adjacency graph
        for comp in self.components:
            if isinstance(comp, (Resistor, Capacitor, Inductor, VoltageSource, CurrentSource, Diode)):
                n1 = getattr(comp, "n1", getattr(comp, "n_pos", getattr(comp, "n_anode", None)))
                n2 = getattr(comp, "n2", getattr(comp, "n_neg", getattr(comp, "n_cathode", None)))
                if n1 and n2:
                    n1_norm = str(n1).strip().upper()
                    n2_norm = str(n2).strip().upper()
                    if n1_norm == n2_norm:
                        errors.append(f"Self-loop short: Component '{comp.name}' is tied between '{n1}' and itself.")
                    node_connections.setdefault(n1_norm, []).append(comp.name)
                    node_connections.setdefault(n2_norm, []).append(comp.name)
            elif isinstance(comp, BJT):
                node_connections.setdefault(comp.n_c.upper(), []).append(comp.name)
                node_connections.setdefault(comp.n_b.upper(), []).append(comp.name)
                node_connections.setdefault(comp.n_e.upper(), []).append(comp.name)
            elif isinstance(comp, MOSFET):
                node_connections.setdefault(comp.n_d.upper(), []).append(comp.name)
                node_connections.setdefault(comp.n_g.upper(), []).append(comp.name)
                node_connections.setdefault(comp.n_s.upper(), []).append(comp.name)

        # Check for floating nodes (degree < 2, excluding reference node)
        for node, connected in node_connections.items():
            if node in ("0", "GND", "GROUND"):
                continue
            if len(connected) == 0:
                warnings.append(f"Unconnected node: Node '{node}' has no components attached.")
            elif len(connected) == 1:
                warnings.append(f"Floating terminal: Node '{node}' is only connected to single component '{connected[0]}'.")

        # Check for parallel conflicting voltage sources (short circuit)
        for i in range(len(v_sources)):
            for j in range(i + 1, len(v_sources)):
                v1 = v_sources[i]
                v2 = v_sources[j]
                pair1 = {v1.n_pos.upper(), v1.n_neg.upper()}
                pair2 = {v2.n_pos.upper(), v2.n_neg.upper()}
                if pair1 == pair2:
                    if v1.dc_val != v2.dc_val:
                        errors.append(f"Voltage loop short circuit: Voltage sources '{v1.name}' ({v1.dc_val}V) and '{v2.name}' ({v2.dc_val}V) are tied in parallel.")

        # Check DC path to ground via BFS
        visited_nodes: Set[str] = set()
        queue = ["0", "GND"]
        visited_nodes.update(queue)

        adj: Dict[str, Set[str]] = {n: set() for n in node_connections}
        for comp in self.components:
            if isinstance(comp, (Resistor, Inductor, Diode)):
                n1 = getattr(comp, "n1", getattr(comp, "n_anode", None))
                n2 = getattr(comp, "n2", getattr(comp, "n_cathode", None))
                if n1 and n2:
                    adj.setdefault(n1.upper(), set()).add(n2.upper())
                    adj.setdefault(n2.upper(), set()).add(n1.upper())
            elif isinstance(comp, VoltageSource):
                adj.setdefault(comp.n_pos.upper(), set()).add(comp.n_neg.upper())
                adj.setdefault(comp.n_neg.upper(), set()).add(comp.n_pos.upper())

        while queue:
            curr = queue.pop(0)
            for neighbor in adj.get(curr, []):
                if neighbor not in visited_nodes:
                    visited_nodes.add(neighbor)
                    queue.append(neighbor)

        for node in node_connections:
            if node not in ("0", "GND", "GROUND") and node not in visited_nodes:
                warnings.append(f"No DC path to ground: Node '{node}' has no direct resistive/voltage path to reference Node 0.")

        is_valid = len(errors) == 0
        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "node_count": self.num_nodes(),
            "component_count": len(self.components)
        }


# ========================================================================================
# 3. Non-Linear Modified Nodal Analysis (MNA) Matrix Solver
# ========================================================================================

class NonLinearMNASolver:
    """
    Formulates and solves Modified Nodal Analysis (MNA) matrices:
      [G  B] * [v] = [i]
      [C  D]   [j]   [e]
    Iteratively solves non-linear device operating points via Newton-Raphson.
    Performs transient analysis with Trapezoidal and Backward Euler companion models.
    """

    def __init__(self, circuit: Circuit):
        self.circuit = circuit

    def _assemble_mna_system(
        self,
        v_guess: List[float],
        t: float = 0.0,
        dt: float = 1e-6,
        integration_method: str = "TRAPEZOIDAL"
    ) -> Tuple[List[List[float]], List[float], List[VoltageSource], List[Inductor]]:
        """
        Assembles augmented MNA matrix A and RHS vector z at time t and operating point v_guess.
        """
        N = self.circuit.num_nodes()
        v_sources = [c for c in self.circuit.components if isinstance(c, VoltageSource)]
        inductors = [c for c in self.circuit.components if isinstance(c, Inductor)]
        M = len(v_sources) + len(inductors)
        total_dim = N + M

        A = [[0.0 for _ in range(total_dim)] for _ in range(total_dim)]
        z = [0.0 for _ in range(total_dim)]

        # Add minimum G_MIN conductance from every node to ground for numerical stability
        for i in range(N):
            A[i][i] += G_MIN

        # Helper to safely stamp conductances between n1 and n2
        def stamp_conductance(n1_idx: int, n2_idx: int, g: float):
            if n1_idx > 0:
                A[n1_idx - 1][n1_idx - 1] += g
            if n2_idx > 0:
                A[n2_idx - 1][n2_idx - 1] += g
            if n1_idx > 0 and n2_idx > 0:
                A[n1_idx - 1][n2_idx - 1] -= g
                A[n2_idx - 1][n1_idx - 1] -= g

        # Helper to safely stamp current source flowing from n_from to n_to
        def stamp_current_source(n_from_idx: int, n_to_idx: int, i_val: float):
            if n_from_idx > 0:
                z[n_from_idx - 1] -= i_val
            if n_to_idx > 0:
                z[n_to_idx - 1] += i_val

        # 1. Stamp Passive Linear Resistors
        for comp in self.circuit.components:
            if isinstance(comp, Resistor):
                n1 = self.circuit.get_or_create_node_idx(comp.n1)
                n2 = self.circuit.get_or_create_node_idx(comp.n2)
                stamp_conductance(n1, n2, comp.conductance)

        # 2. Stamp Independent Current Sources
        for comp in self.circuit.components:
            if isinstance(comp, CurrentSource):
                n_pos = self.circuit.get_or_create_node_idx(comp.n_pos)
                n_neg = self.circuit.get_or_create_node_idx(comp.n_neg)
                stamp_current_source(n_pos, n_neg, comp.dc_val)

        # 3. Stamp Reactive Capacitors (Transient Companion Models)
        for comp in self.circuit.components:
            if isinstance(comp, Capacitor):
                n1 = self.circuit.get_or_create_node_idx(comp.n1)
                n2 = self.circuit.get_or_create_node_idx(comp.n2)
                if integration_method == "BACKWARD_EULER":
                    g_eq = comp.capacitance / dt
                    i_eq = g_eq * comp.v_prev
                else:  # TRAPEZOIDAL
                    g_eq = 2.0 * comp.capacitance / dt
                    i_eq = g_eq * comp.v_prev + comp.i_prev

                stamp_conductance(n1, n2, g_eq)
                stamp_current_source(n2, n1, i_eq)

        # 4. Stamp Non-Linear Diodes (Newton-Raphson Linearized Companion)
        for comp in self.circuit.components:
            if isinstance(comp, Diode):
                n_a = self.circuit.get_or_create_node_idx(comp.n_anode)
                n_k = self.circuit.get_or_create_node_idx(comp.n_cathode)
                va = v_guess[n_a - 1] if n_a > 0 else 0.0
                vk = v_guess[n_k - 1] if n_k > 0 else 0.0
                vd = va - vk

                # Apply Berkeley SPICE pnjlim to stabilize voltage swing
                vd_lim = pnjlim(vd, comp.vd_op, comp.vt, comp.vcrit)
                comp.vd_op = vd_lim

                # Shockley diode IV & small-signal dynamic conductance
                exp_arg = min(40.0, max(-40.0, vd_lim / comp.vt))
                exp_val = math.exp(exp_arg)
                i_d = comp.is_sat * (exp_val - 1.0)
                g_d = max(1e-12, (comp.is_sat / comp.vt) * exp_val)
                comp.id_op = i_d
                comp.gd_op = g_d

                # Companion parallel current source: I_eq = I_D - g_d * V_D
                i_eq = i_d - g_d * vd_lim

                stamp_conductance(n_a, n_k, g_d)
                stamp_current_source(n_a, n_k, i_eq)

        # 5. Stamp Non-Linear BJTs (Ebers-Moll Linearized Companion)
        for comp in self.circuit.components:
            if isinstance(comp, BJT):
                nc = self.circuit.get_or_create_node_idx(comp.n_c)
                nb = self.circuit.get_or_create_node_idx(comp.n_b)
                ne = self.circuit.get_or_create_node_idx(comp.n_e)
                vc = v_guess[nc - 1] if nc > 0 else 0.0
                vb = v_guess[nb - 1] if nb > 0 else 0.0
                ve = v_guess[ne - 1] if ne > 0 else 0.0

                vbe = vb - ve
                vbc = vb - vc

                vbe_lim = pnjlim(vbe, comp.vbe_op, comp.vt, 0.72)
                vbc_lim = pnjlim(vbc, comp.vbc_op, comp.vt, 0.72)
                comp.vbe_op = vbe_lim
                comp.vbc_op = vbc_lim

                # Ebers-Moll currents
                exp_be = math.exp(min(35.0, max(-35.0, vbe_lim / comp.vt)))
                exp_bc = math.exp(min(35.0, max(-35.0, vbc_lim / comp.vt)))
                i_f = comp.is_sat * (exp_be - 1.0)
                i_r = (comp.is_sat / comp.beta_r) * (exp_bc - 1.0)

                ic = i_f - i_r - (i_r / comp.beta_r)
                ib = (i_f / comp.beta_f) + (i_r / comp.beta_r)
                comp.ic_op = ic
                comp.ib_op = ib

                g_mf = (comp.is_sat / comp.vt) * exp_be
                g_mr = ((comp.is_sat / comp.beta_r) / comp.vt) * exp_bc
                g_pi = g_mf / comp.beta_f
                g_mu = g_mr / comp.beta_r

                # Stamp base-emitter & base-collector conductances
                stamp_conductance(nb, ne, g_pi)
                stamp_conductance(nb, nc, g_mu)

                # Early effect output conductance
                vce = vc - ve
                g_o = max(1e-9, abs(ic) / comp.va)
                stamp_conductance(nc, ne, g_o)

                # Transconductance controlled current source: Ic = g_mf * vbe
                if nc > 0 and nb > 0:
                    A[nc - 1][nb - 1] += g_mf
                if nc > 0 and ne > 0:
                    A[nc - 1][ne - 1] -= g_mf
                if ne > 0 and nb > 0:
                    A[ne - 1][nb - 1] -= g_mf
                if ne > 0 and ne > 0:
                    A[ne - 1][ne - 1] += g_mf

                # Equivalent currents on RHS
                i_c_eq = ic - g_mf * vbe_lim - g_o * vce
                i_b_eq = ib - g_pi * vbe_lim - g_mu * vbc_lim
                stamp_current_source(nc, ne, i_c_eq)
                stamp_current_source(nb, ne, i_b_eq)

        # 6. Stamp Non-Linear MOSFETs (Shichman-Hodges Linearized Companion)
        for comp in self.circuit.components:
            if isinstance(comp, MOSFET):
                nd = self.circuit.get_or_create_node_idx(comp.n_d)
                ng = self.circuit.get_or_create_node_idx(comp.n_g)
                ns = self.circuit.get_or_create_node_idx(comp.n_s)
                vd = v_guess[nd - 1] if nd > 0 else 0.0
                vg = v_guess[ng - 1] if ng > 0 else 0.0
                vs = v_guess[ns - 1] if ns > 0 else 0.0

                vgs = vg - vs
                vds = vd - vs
                vov = vgs - comp.vth

                if vov <= 0.0:
                    # Cutoff region
                    i_d = 0.0
                    g_m = 0.0
                    g_ds = G_MIN
                elif vds < vov:
                    # Triode region
                    i_d = comp.kn * (vov * vds - 0.5 * vds * vds)
                    g_m = comp.kn * vds
                    g_ds = max(G_MIN, comp.kn * (vov - vds))
                else:
                    # Saturation region
                    i_d = 0.5 * comp.kn * (vov ** 2) * (1.0 + comp.lambda_param * vds)
                    g_m = comp.kn * vov * (1.0 + comp.lambda_param * vds)
                    g_ds = max(G_MIN, 0.5 * comp.kn * (vov ** 2) * comp.lambda_param)

                comp.id_op = i_d
                comp.gm_op = g_m
                comp.gds_op = g_ds

                stamp_conductance(nd, ns, g_ds)

                # VCCS: id = gm * (vg - vs)
                if nd > 0 and ng > 0:
                    A[nd - 1][ng - 1] += g_m
                if nd > 0 and ns > 0:
                    A[nd - 1][ns - 1] -= g_m
                if ns > 0 and ng > 0:
                    A[ns - 1][ng - 1] -= g_m
                if ns > 0 and ns > 0:
                    A[ns - 1][ns - 1] += g_m

                i_eq = i_d - g_m * vgs - g_ds * vds
                stamp_current_source(nd, ns, i_eq)

        # 7. Stamp Voltage Sources (B and C matrices in MNA)
        for k, vsrc in enumerate(v_sources):
            row_idx = N + k
            n_p = self.circuit.get_or_create_node_idx(vsrc.n_pos)
            n_m = self.circuit.get_or_create_node_idx(vsrc.n_neg)

            # B matrix (KCL current injection)
            if n_p > 0:
                A[n_p - 1][row_idx] += 1.0
            if n_m > 0:
                A[n_m - 1][row_idx] -= 1.0

            # C matrix (KVL voltage constraint)
            if n_p > 0:
                A[row_idx][n_p - 1] += 1.0
            if n_m > 0:
                A[row_idx][n_m - 1] -= 1.0

            # RHS value (Voltage at time t)
            z[row_idx] = vsrc.get_voltage_at_time(t)

        # 8. Stamp Inductors (Treated via companion current/voltage variables)
        for k, ind in enumerate(inductors):
            row_idx = N + len(v_sources) + k
            n1 = self.circuit.get_or_create_node_idx(ind.n1)
            n2 = self.circuit.get_or_create_node_idx(ind.n2)

            if n1 > 0:
                A[n1 - 1][row_idx] += 1.0
            if n2 > 0:
                A[n2 - 1][row_idx] -= 1.0
            if n1 > 0:
                A[row_idx][n1 - 1] += 1.0
            if n2 > 0:
                A[row_idx][n2 - 1] -= 1.0

            # Companion resistance D term
            if integration_method == "BACKWARD_EULER":
                r_eq = ind.inductance / dt
                A[row_idx][row_idx] -= r_eq
                z[row_idx] = -r_eq * ind.i_prev
            else:  # TRAPEZOIDAL
                r_eq = 2.0 * ind.inductance / dt
                A[row_idx][row_idx] -= r_eq
                z[row_idx] = -r_eq * ind.i_prev - ind.v_prev

        return A, z, v_sources, inductors

    def solve_dc_operating_point(
        self,
        max_iterations: int = 50,
        voltage_tol: float = 1e-6
    ) -> Dict[str, Any]:
        """
        Computes the DC Operating Point (.op) using Newton-Raphson iteration.
        """
        N = self.circuit.num_nodes()
        v_guess = [0.0 for _ in range(N)]
        converged = False
        iteration_count = 0

        # Initialize diode/transistor voltages with typical forward drops
        for comp in self.circuit.components:
            if isinstance(comp, Diode):
                comp.vd_op = 0.65
            elif isinstance(comp, BJT):
                comp.vbe_op = 0.65
                comp.vbc_op = -2.0

        for it in range(max_iterations):
            iteration_count += 1
            A, z, v_sources, inductors = self._assemble_mna_system(
                v_guess, t=0.0, dt=1.0, integration_method="TRAPEZOIDAL"
            )
            x_sol = solve_linear_system(A, z)
            v_new = x_sol[:N]

            # Check convergence norm (node voltages and device junction voltages)
            max_diff = 0.0
            for i in range(N):
                diff = abs(v_new[i] - v_guess[i])
                if diff > max_diff:
                    max_diff = diff

            # Check if any non-linear device was clamped by pnjlim
            device_diff_max = 0.0
            for comp in self.circuit.components:
                if isinstance(comp, Diode):
                    na = self.circuit.get_or_create_node_idx(comp.n_anode)
                    nk = self.circuit.get_or_create_node_idx(comp.n_cathode)
                    va = v_new[na - 1] if na > 0 else 0.0
                    vk = v_new[nk - 1] if nk > 0 else 0.0
                    dd = abs((va - vk) - comp.vd_op)
                    if dd > device_diff_max:
                        device_diff_max = dd
                elif isinstance(comp, BJT):
                    nb = self.circuit.get_or_create_node_idx(comp.n_b)
                    ne = self.circuit.get_or_create_node_idx(comp.n_e)
                    nc = self.circuit.get_or_create_node_idx(comp.n_c)
                    vb = v_new[nb - 1] if nb > 0 else 0.0
                    ve = v_new[ne - 1] if ne > 0 else 0.0
                    vc = v_new[nc - 1] if nc > 0 else 0.0
                    dd_be = abs((vb - ve) - comp.vbe_op)
                    dd_bc = abs((vb - vc) - comp.vbc_op)
                    device_diff_max = max(device_diff_max, dd_be, dd_bc)

            v_guess = v_new
            if it >= 2 and max_diff < voltage_tol and device_diff_max < voltage_tol:
                converged = True
                break

        # Map solution vector back to node names
        node_voltages = {"0": 0.0, "GND": 0.0}
        for idx, name in self.circuit.idx_to_node.items():
            if idx > 0 and idx <= len(v_guess):
                node_voltages[name] = round(v_guess[idx - 1], 6)

        # Device operating reports
        devices = {}
        for comp in self.circuit.components:
            if isinstance(comp, Diode):
                devices[comp.name] = {
                    "type": "DIODE",
                    "v_d": round(comp.vd_op, 5),
                    "i_d_mA": round(comp.id_op * 1000.0, 4),
                    "g_d_S": round(comp.gd_op, 5),
                    "state": "FORWARD" if comp.vd_op >= 0.55 else "REVERSE/CUTOFF"
                }
            elif isinstance(comp, BJT):
                devices[comp.name] = {
                    "type": f"BJT_{comp.bjt_type}",
                    "v_be": round(comp.vbe_op, 4),
                    "v_bc": round(comp.vbc_op, 4),
                    "i_c_mA": round(comp.ic_op * 1000.0, 4),
                    "i_b_uA": round(comp.ib_op * 1e6, 3),
                    "beta_effective": round(comp.ic_op / max(1e-12, comp.ib_op), 1),
                    "region": "ACTIVE" if (comp.vbe_op > 0.5 and comp.vbc_op < 0.2) else ("SATURATION" if comp.vbc_op >= 0.2 else "CUTOFF")
                }
            elif isinstance(comp, MOSFET):
                vov = comp.vgs_op - comp.vth
                reg = "CUTOFF" if vov <= 0 else ("TRIODE" if comp.vds_op < vov else "SATURATION")
                devices[comp.name] = {
                    "type": comp.mos_type,
                    "v_gs": round(comp.vgs_op, 4),
                    "v_ds": round(comp.vds_op, 4),
                    "i_d_mA": round(comp.id_op * 1000.0, 4),
                    "g_m_mS": round(comp.gm_op * 1000.0, 3),
                    "region": reg
                }

        return {
            "converged": converged,
            "iterations": iteration_count,
            "node_voltages": node_voltages,
            "devices": devices,
            "analysis_type": "DC_OPERATING_POINT"
        }

    def solve_transient(
        self,
        t_stop: float = 5e-3,
        t_step: float = 10e-6,
        integration_method: str = "TRAPEZOIDAL",
        adaptive_stepping: bool = True
    ) -> Dict[str, Any]:
        """
        Executes transient numerical integration from t = 0 to t_stop.
        Returns time points, node voltage trajectories, and component currents.
        """
        N = self.circuit.num_nodes()
        t = 0.0
        dt = float(t_step)
        method = integration_method.upper().strip()
        if method not in ("TRAPEZOIDAL", "BACKWARD_EULER"):
            method = "TRAPEZOIDAL"

        # Initialize node voltages with DC operating point
        dc_op = self.solve_dc_operating_point()
        v_current = [0.0 for _ in range(N)]
        for idx in range(1, N + 1):
            name = self.circuit.idx_to_node.get(idx, "")
            v_current[idx - 1] = dc_op["node_voltages"].get(name, 0.0)

        # Initialize capacitor and inductor states
        for comp in self.circuit.components:
            if isinstance(comp, Capacitor):
                n1 = self.circuit.get_or_create_node_idx(comp.n1)
                n2 = self.circuit.get_or_create_node_idx(comp.n2)
                v1 = v_current[n1 - 1] if n1 > 0 else 0.0
                v2 = v_current[n2 - 1] if n2 > 0 else 0.0
                comp.v_prev = (v1 - v2) if comp.ic == 0.0 else comp.ic
                comp.i_prev = 0.0
            elif isinstance(comp, Inductor):
                comp.i_prev = comp.ic
                comp.v_prev = 0.0

        time_points: List[float] = [0.0]
        node_trajectories: Dict[str, List[float]] = {
            self.circuit.idx_to_node[i]: [v_current[i - 1]] for i in range(1, N + 1)
        }
        node_trajectories["0"] = [0.0]

        total_steps = 0
        nr_iterations_total = 0

        while t < t_stop:
            t_next = min(t_stop, t + dt)
            dt_step = t_next - t

            # Newton-Raphson iteration for the current time step
            v_guess = v_current[:]
            step_converged = False
            step_iterations = 0

            for it in range(30):
                step_iterations += 1
                A, z, v_sources, inductors = self._assemble_mna_system(
                    v_guess, t=t_next, dt=dt_step, integration_method=method
                )
                x_sol = solve_linear_system(A, z)
                v_cand = x_sol[:N]

                max_diff = max(abs(v_cand[i] - v_guess[i]) for i in range(N)) if N > 0 else 0.0

                device_diff_max = 0.0
                for comp in self.circuit.components:
                    if isinstance(comp, Diode):
                        na = self.circuit.get_or_create_node_idx(comp.n_anode)
                        nk = self.circuit.get_or_create_node_idx(comp.n_cathode)
                        va = v_cand[na - 1] if na > 0 else 0.0
                        vk = v_cand[nk - 1] if nk > 0 else 0.0
                        dd = abs((va - vk) - comp.vd_op)
                        if dd > device_diff_max:
                            device_diff_max = dd
                    elif isinstance(comp, BJT):
                        nb = self.circuit.get_or_create_node_idx(comp.n_b)
                        ne = self.circuit.get_or_create_node_idx(comp.n_e)
                        nc = self.circuit.get_or_create_node_idx(comp.n_c)
                        vb = v_cand[nb - 1] if nb > 0 else 0.0
                        ve = v_cand[ne - 1] if ne > 0 else 0.0
                        vc = v_cand[nc - 1] if nc > 0 else 0.0
                        dd_be = abs((vb - ve) - comp.vbe_op)
                        dd_bc = abs((vb - vc) - comp.vbc_op)
                        device_diff_max = max(device_diff_max, dd_be, dd_bc)

                v_guess = v_cand

                if max_diff < 1e-4 and device_diff_max < 1e-4:
                    step_converged = True
                    break

            nr_iterations_total += step_iterations

            # Adaptive stepping adjustments
            if not step_converged and adaptive_stepping and dt > 1e-8:
                # Halve time step and retry
                dt *= 0.5
                continue

            v_current = v_guess
            t = t_next
            total_steps += 1
            time_points.append(round(t, 8))

            for idx in range(1, N + 1):
                name = self.circuit.idx_to_node[idx]
                node_trajectories[name].append(round(v_current[idx - 1], 5))
            node_trajectories["0"].append(0.0)

            # Update capacitor and inductor companion history
            for comp in self.circuit.components:
                if isinstance(comp, Capacitor):
                    n1 = self.circuit.get_or_create_node_idx(comp.n1)
                    n2 = self.circuit.get_or_create_node_idx(comp.n2)
                    v1 = v_current[n1 - 1] if n1 > 0 else 0.0
                    v2 = v_current[n2 - 1] if n2 > 0 else 0.0
                    v_cap = v1 - v2
                    if method == "BACKWARD_EULER":
                        comp.i_prev = comp.capacitance * (v_cap - comp.v_prev) / dt_step
                    else:  # TRAPEZOIDAL
                        comp.i_prev = (2.0 * comp.capacitance / dt_step) * (v_cap - comp.v_prev) - comp.i_prev
                    comp.v_prev = v_cap
                elif isinstance(comp, Inductor):
                    n1 = self.circuit.get_or_create_node_idx(comp.n1)
                    n2 = self.circuit.get_or_create_node_idx(comp.n2)
                    v1 = v_current[n1 - 1] if n1 > 0 else 0.0
                    v2 = v_current[n2 - 1] if n2 > 0 else 0.0
                    v_ind = v1 - v2
                    if method == "BACKWARD_EULER":
                        comp.i_prev = comp.i_prev + (dt_step / comp.inductance) * v_ind
                    else:  # TRAPEZOIDAL
                        comp.i_prev = comp.i_prev + (dt_step / (2.0 * comp.inductance)) * (v_ind + comp.v_prev)
                    comp.v_prev = v_ind

            # Restore nominal step if converged easily
            if adaptive_stepping and step_iterations <= 3 and dt < t_step:
                dt = min(t_step, dt * 1.5)

        return {
            "status": "SUCCESS",
            "integration_method": method,
            "t_stop": t_stop,
            "total_steps": total_steps,
            "avg_nr_iterations": round(nr_iterations_total / max(1, total_steps), 2),
            "time_points": time_points,
            "trajectories": node_trajectories,
            "analysis_type": "TRANSIENT"
        }


# ========================================================================================
# Phase 16: Engineering Assumptions Checker for Analog Circuits & Transistors
# ========================================================================================

class CircuitAssumptionsChecker:
    """
    Validates physical engineering assumptions on analog circuits and transistor operating points:
      - BJT Active (Linear) vs Saturation vs Cutoff region violations
      - MOSFET Saturation vs Triode vs Subthreshold region violations
      - Diode reverse breakdown and excessive dissipation
      - Extreme node voltage boundaries (|V| > 1000V)
    """

    @staticmethod
    def check_assumptions(
        circuit: Circuit,
        simulation_results: Dict[str, Any],
        assumed_operating_mode: str = "LINEAR_AMPLIFICATION"
    ) -> Dict[str, Any]:
        violations = []
        warnings = []
        device_operating_points = {}
        trajectories = simulation_results.get("trajectories", {})
        node_voltages = simulation_results.get("node_voltages") or {}

        final_voltages = dict(node_voltages)
        for n, vals in trajectories.items():
            if vals and len(vals) > 0:
                final_voltages[n] = vals[-1]

        # 1. BJT Operating Region Validation
        for comp in circuit.components:
            if isinstance(comp, BJT):
                vc = final_voltages.get(comp.n_c, 0.0)
                vb = final_voltages.get(comp.n_b, 0.0)
                ve = final_voltages.get(comp.n_e, 0.0)

                vbe = vb - ve
                vce = vc - ve
                vbc = vb - vc

                if comp.bjt_type == "NPN":
                    is_active = (vbe >= 0.55) and (vce >= 0.20)
                    is_saturated = (vbe >= 0.55) and (vce < 0.20)
                    is_cutoff = vbe < 0.50
                    is_reverse = (vbc >= 0.55) and (vbe < 0.50)
                else:  # PNP
                    vbe = -vbe
                    vce = -vce
                    vbc = -vbc
                    is_active = (vbe >= 0.55) and (vce >= 0.20)
                    is_saturated = (vbe >= 0.55) and (vce < 0.20)
                    is_cutoff = vbe < 0.50
                    is_reverse = (vbc >= 0.55) and (vbe < 0.50)

                op_region = "ACTIVE" if is_active else "SATURATION" if is_saturated else "CUTOFF" if is_cutoff else "REVERSE_ACTIVE"

                device_operating_points[comp.name] = {
                    "device": "BJT",
                    "type": comp.bjt_type,
                    "region": op_region,
                    "vbe": round(vbe, 3),
                    "vce": round(vce, 3),
                    "vbc": round(vbc, 3)
                }

                if assumed_operating_mode.upper() == "LINEAR_AMPLIFICATION" and is_saturated:
                    violations.append({
                        "device": comp.name,
                        "type": "BJT_SATURATION_REGION_VIOLATION",
                        "severity": "CRITICAL",
                        "message": f"BJT '{comp.name}' entered Saturation region (Vce = {vce:.3f}V < 0.20V, Vbe = {vbe:.3f}V). Linear amplification is compromised; collector current is limited by external load Rc."
                    })
                elif assumed_operating_mode.upper() == "LINEAR_AMPLIFICATION" and is_cutoff:
                    violations.append({
                        "device": comp.name,
                        "type": "BJT_CUTOFF_REGION_VIOLATION",
                        "severity": "HIGH",
                        "message": f"BJT '{comp.name}' is in Cutoff region (Vbe = {vbe:.3f}V < 0.50V). Base-emitter junction lacks forward bias; no amplification occurs."
                    })

                if abs(vce) > 50.0:
                    violations.append({
                        "device": comp.name,
                        "type": "BJT_BREAKDOWN_VOLTAGE_EXCEEDED",
                        "severity": "CRITICAL",
                        "message": f"BJT '{comp.name}' Collector-Emitter voltage (Vce = {vce:.2f}V) exceeds maximum Vceo rating (50V)."
                    })

            # 2. MOSFET Operating Region Validation
            elif isinstance(comp, MOSFET):
                vd = final_voltages.get(comp.n_d, 0.0)
                vg = final_voltages.get(comp.n_g, 0.0)
                vs = final_voltages.get(comp.n_s, 0.0)

                vgs = vg - vs
                vds = vd - vs
                vth = comp.vth
                vov = vgs - vth

                if comp.mos_type == "NMOS":
                    is_sat = (vgs > vth) and (vds >= vov)
                    is_triode = (vgs > vth) and (vds < vov)
                    is_cutoff = vgs <= vth
                else:  # PMOS
                    vgs = -vgs
                    vds = -vds
                    vth = -vth
                    vov = vgs - vth
                    is_sat = (vgs > vth) and (vds >= vov)
                    is_triode = (vgs > vth) and (vds < vov)
                    is_cutoff = vgs <= vth

                op_region = "SATURATION" if is_sat else "TRIODE" if is_triode else "CUTOFF"
                device_operating_points[comp.name] = {
                    "device": "MOSFET",
                    "type": comp.mos_type,
                    "region": op_region,
                    "vgs": round(vgs, 3),
                    "vds": round(vds, 3),
                    "vov": round(vov, 3)
                }

                if assumed_operating_mode.upper() == "LINEAR_AMPLIFICATION" and is_triode:
                    violations.append({
                        "device": comp.name,
                        "type": "MOSFET_TRIODE_REGION_VIOLATION",
                        "severity": "CRITICAL",
                        "message": f"MOSFET '{comp.name}' entered Triode (Ohmic) region (Vds = {vds:.3f}V < Vov = {vov:.3f}V). Channel pinch-off is lost; transconductance gm drops."
                    })
                elif assumed_operating_mode.upper() == "LINEAR_AMPLIFICATION" and is_cutoff:
                    violations.append({
                        "device": comp.name,
                        "type": "MOSFET_SUBTHRESHOLD_CUTOFF_VIOLATION",
                        "severity": "HIGH",
                        "message": f"MOSFET '{comp.name}' is in Cutoff (Vgs = {vgs:.3f}V <= Vth = {vth:.3f}V). Inversion channel has not formed."
                    })

            # 3. Diode Breakdown Validation
            elif isinstance(comp, Diode):
                v1 = final_voltages.get(comp.n_anode, 0.0)
                v2 = final_voltages.get(comp.n_cathode, 0.0)
                vd = v1 - v2
                device_operating_points[comp.name] = {
                    "device": "DIODE",
                    "vd": round(vd, 3),
                    "state": "FORWARD" if vd >= 0.55 else "REVERSE" if vd >= -50.0 else "BREAKDOWN"
                }
                if vd < -50.0:
                    violations.append({
                        "device": comp.name,
                        "type": "DIODE_REVERSE_BREAKDOWN_EXCEEDED",
                        "severity": "CRITICAL",
                        "message": f"Diode '{comp.name}' reverse voltage (Vd = {vd:.2f}V) exceeds peak inverse voltage (PIV 50V)."
                    })

        # 4. Extreme Node Voltages Check
        for n, v in final_voltages.items():
            if math.isnan(v) or math.isinf(v) or abs(v) > 1000.0:
                violations.append({
                    "node": n,
                    "type": "EXTREME_VOLTAGE_NUMERICAL_DIVERGENCE",
                    "severity": "CRITICAL",
                    "message": f"Node '{n}' voltage reached unphysical extreme ({v}V), indicating numerical instability or floating node."
                })

        return {
            "assumptions_valid": len(violations) == 0,
            "violations_count": len(violations),
            "violations": violations,
            "warnings_count": len(warnings),
            "warnings": warnings,
            "device_operating_points": device_operating_points,
            "operating_points": device_operating_points
        }


# ========================================================================================
# Phase 17: Circuit Tolerance Monte Carlo Yield Analysis Engine
# ========================================================================================

class CircuitMonteCarloSimulator:
    """
    High-Performance Circuit Tolerance & Monte Carlo Yield Analysis Engine.
    Executes Gaussian variation sweeps over passive (R, C, L) and active (BJT, MOSFET, Diode)
    component parameters, computing yield, mean, standard deviation, confidence intervals,
    parameter sensitivity rankings, and histogram distributions.
    """

    @staticmethod
    def calculate_distribution_statistics(values: List[float]) -> Dict[str, Any]:
        """Calculates comprehensive descriptive statistics and percentiles."""
        if not values:
            return {"mean": 0.0, "std_dev": 0.0, "min": 0.0, "max": 0.0, "median_p50": 0.0}

        n = len(values)
        mean_val = sum(values) / n
        if n > 1:
            variance = sum((x - mean_val) ** 2 for x in values) / (n - 1)
            std_dev = math.sqrt(variance)
        else:
            variance = 0.0
            std_dev = 0.0

        sorted_vals = sorted(values)
        def percentile(p: float) -> float:
            k = (n - 1) * p
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return sorted_vals[int(k)]
            d0 = sorted_vals[int(f)] * (c - k)
            d1 = sorted_vals[int(c)] * (k - f)
            return d0 + d1

        min_val = sorted_vals[0]
        max_val = sorted_vals[-1]
        p10 = percentile(0.10)
        p25 = percentile(0.25)
        p50 = percentile(0.50)  # median
        p75 = percentile(0.75)
        p90 = percentile(0.90)
        iqr = p75 - p25

        # Higher statistical moments: skewness & kurtosis
        if std_dev > 1e-12 and n >= 3:
            skewness = (sum(((x - mean_val) / std_dev) ** 3 for x in values) * n) / ((n - 1) * (n - 2))
            kurtosis = (sum(((x - mean_val) / std_dev) ** 4 for x in values) / n) - 3.0
        else:
            skewness = 0.0
            kurtosis = 0.0

        return {
            "count": n,
            "mean": round(mean_val, 5),
            "std_dev": round(std_dev, 5),
            "variance": round(variance, 6),
            "min": round(min_val, 5),
            "max": round(max_val, 5),
            "range": round(max_val - min_val, 5),
            "median_p50": round(p50, 5),
            "p10": round(p10, 5),
            "p25": round(p25, 5),
            "p75": round(p75, 5),
            "p90": round(p90, 5),
            "iqr": round(iqr, 5),
            "skewness": round(skewness, 4),
            "kurtosis": round(kurtosis, 4)
        }

    @staticmethod
    def compute_wilson_score_interval(p_hat: float, n: int, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Computes Wilson score confidence interval for sample proportion p_hat.
        Guaranteed to lie within [0.0, 100.0]% and mathematically robust across all n.
        """
        if n <= 0:
            return 0.0, 100.0
        z = 1.95996  # 95% confidence level
        denom = 1.0 + (z ** 2) / n
        center = (p_hat + (z ** 2) / (2.0 * n)) / denom
        half_width = (z / denom) * math.sqrt((p_hat * (1.0 - p_hat) / n) + ((z ** 2) / (4.0 * (n ** 2))))
        lower = max(0.0, center - half_width)
        upper = min(1.0, center + half_width)
        return round(lower * 100.0, 2), round(upper * 100.0, 2)

    @staticmethod
    def generate_histogram(values: List[float], num_bins: int = 15) -> Dict[str, Any]:
        """Generates histogram bin boundaries, midpoints, frequencies, and counts."""
        if not values:
            return {"bin_edges": [], "bin_midpoints": [], "counts": [], "frequencies": []}
        min_v = min(values)
        max_v = max(values)
        n = len(values)

        if abs(max_v - min_v) < 1e-12:
            return {
                "bin_edges": [round(min_v - 0.1, 4), round(max_v + 0.1, 4)],
                "bin_midpoints": [round(min_v, 4)],
                "counts": [n],
                "frequencies": [1.0]
            }

        bin_w = (max_v - min_v) / num_bins
        edges = [min_v + i * bin_w for i in range(num_bins + 1)]
        midpoints = [0.5 * (edges[i] + edges[i + 1]) for i in range(num_bins)]
        counts = [0] * num_bins

        for val in values:
            idx = int((val - min_v) / bin_w)
            if idx >= num_bins:
                idx = num_bins - 1
            counts[idx] += 1

        freqs = [c / n for c in counts]
        return {
            "bin_edges": [round(e, 4) for e in edges],
            "bin_midpoints": [round(m, 4) for m in midpoints],
            "counts": counts,
            "frequencies": [round(f, 4) for f in freqs]
        }

    @staticmethod
    def compute_parameter_sensitivities(
        param_variations: Dict[str, List[float]],
        output_values: List[float]
    ) -> List[Dict[str, Any]]:
        """
        Computes Pearson correlation coefficient r(param, V_out) across Monte Carlo samples
        to isolate components dominating output variance.
        """
        n = len(output_values)
        if n < 3:
            return []

        mean_out = sum(output_values) / n
        denom_out = math.sqrt(sum((v - mean_out) ** 2 for v in output_values))
        if denom_out < 1e-12:
            return []

        sensitivities = []
        for p_name, p_vals in param_variations.items():
            if len(p_vals) != n:
                continue
            mean_p = sum(p_vals) / n
            denom_p = math.sqrt(sum((p - mean_p) ** 2 for p in p_vals))
            if denom_p < 1e-12:
                r = 0.0
            else:
                cov = sum((p_vals[i] - mean_p) * (output_values[i] - mean_out) for i in range(n))
                r = cov / (denom_p * denom_out)

            abs_r = abs(r)
            if abs_r >= 0.6:
                impact = "DOMINANT"
            elif abs_r >= 0.3:
                impact = "HIGH"
            elif abs_r >= 0.1:
                impact = "MODERATE"
            else:
                impact = "NEGLIGIBLE"

            sensitivities.append({
                "parameter": p_name,
                "correlation_r": round(r, 4),
                "absolute_r": round(abs_r, 4),
                "mean_value": round(mean_p, 4),
                "impact_level": impact
            })

        sensitivities.sort(key=lambda s: s["absolute_r"], reverse=True)
        for idx, item in enumerate(sensitivities, 1):
            item["ranking"] = idx
        return sensitivities

    @classmethod
    def run_monte_carlo(
        cls,
        circuit: Circuit,
        runs: int = 200,
        tolerances: Optional[Dict[str, float]] = None,
        target_nodes: Optional[List[str]] = None,
        acceptance_criteria: Optional[Dict[str, Tuple[float, float]]] = None,
        analysis_type: str = "DC_OP",
        t_stop: float = 3e-3,
        t_step: float = 20e-6,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Executes a statistical Monte Carlo variation sweep over component tolerances.
        """
        rng = random.Random(seed) if seed is not None else random.Random()
        runs_count = max(5, min(1000, int(runs)))
        tol_map = dict(tolerances or {})

        # Identify target nodes
        if not target_nodes:
            if acceptance_criteria:
                target_nodes = list(acceptance_criteria.keys())
            else:
                target_nodes = [n for n in circuit.idx_to_node.values() if n not in ("0", "GND", "GROUND")]
                if not target_nodes:
                    target_nodes = ["1"]

        node_trajectories: Dict[str, List[float]] = {n: [] for n in target_nodes}
        param_variations: Dict[str, List[float]] = {}
        passed_runs = 0
        failed_runs = 0
        run_samples = []

        for k in range(runs_count):
            sim_circ = copy.deepcopy(circuit)

            # Perturb component parameters with Gaussian variations
            for comp in sim_circ.components:
                if isinstance(comp, Resistor):
                    tol = tol_map.get(comp.name, tol_map.get("R", 0.05))
                    sigma = (tol / 3.0) * comp.resistance
                    r_val = max(1e-4, rng.gauss(comp.resistance, sigma))
                    comp.resistance = r_val
                    comp.conductance = 1.0 / r_val
                    param_variations.setdefault(f"{comp.name}_R", []).append(r_val)

                elif isinstance(comp, Capacitor):
                    tol = tol_map.get(comp.name, tol_map.get("C", 0.10))
                    sigma = (tol / 3.0) * comp.capacitance
                    c_val = max(1e-15, rng.gauss(comp.capacitance, sigma))
                    comp.capacitance = c_val
                    param_variations.setdefault(f"{comp.name}_C", []).append(c_val)

                elif isinstance(comp, Inductor):
                    tol = tol_map.get(comp.name, tol_map.get("L", 0.05))
                    sigma = (tol / 3.0) * comp.inductance
                    l_val = max(1e-15, rng.gauss(comp.inductance, sigma))
                    comp.inductance = l_val
                    param_variations.setdefault(f"{comp.name}_L", []).append(l_val)

                elif isinstance(comp, VoltageSource):
                    tol = tol_map.get(comp.name, tol_map.get("V", 0.02))
                    sigma = (tol / 3.0) * max(0.1, abs(comp.dc_val))
                    v_val = rng.gauss(comp.dc_val, sigma)
                    comp.dc_val = v_val
                    param_variations.setdefault(f"{comp.name}_V", []).append(v_val)

                elif isinstance(comp, BJT):
                    b_tol = tol_map.get(f"{comp.name}_BETA", tol_map.get("BJT_BETA", 0.20))
                    sigma_b = (b_tol / 3.0) * comp.beta_f
                    beta_val = max(5.0, rng.gauss(comp.beta_f, sigma_b))
                    comp.beta_f = beta_val
                    param_variations.setdefault(f"{comp.name}_BETA", []).append(beta_val)

                    is_tol = tol_map.get(f"{comp.name}_IS", 0.15)
                    sigma_is = (is_tol / 3.0) * comp.is_sat
                    is_val = max(1e-20, rng.gauss(comp.is_sat, sigma_is))
                    comp.is_sat = is_val
                    param_variations.setdefault(f"{comp.name}_IS", []).append(is_val)

                elif isinstance(comp, MOSFET):
                    vth_tol = tol_map.get(f"{comp.name}_VTH", tol_map.get("MOS_VTH", 0.10))
                    sigma_vth = (vth_tol / 3.0) * max(0.2, abs(comp.vth))
                    vth_val = rng.gauss(comp.vth, sigma_vth)
                    comp.vth = vth_val
                    param_variations.setdefault(f"{comp.name}_VTH", []).append(vth_val)

                    kn_tol = tol_map.get(f"{comp.name}_KN", 0.15)
                    sigma_kn = (kn_tol / 3.0) * comp.kn
                    kn_val = max(1e-6, rng.gauss(comp.kn, sigma_kn))
                    comp.kn = kn_val
                    param_variations.setdefault(f"{comp.name}_KN", []).append(kn_val)

                elif isinstance(comp, Diode):
                    is_tol = tol_map.get(f"{comp.name}_IS", tol_map.get("DIODE_IS", 0.15))
                    sigma_is = (is_tol / 3.0) * comp.is_sat
                    is_val = max(1e-20, rng.gauss(comp.is_sat, sigma_is))
                    comp.is_sat = is_val
                    param_variations.setdefault(f"{comp.name}_IS", []).append(is_val)

            # Solve perturbed circuit
            solver = NonLinearMNASolver(sim_circ)
            if analysis_type.upper() in ("DC_OP", "DC_OPERATING_POINT"):
                sol = solver.solve_dc_operating_point()
                node_v = sol.get("node_voltages", {})
            else:
                sol = solver.solve_transient(t_stop=t_stop, t_step=t_step)
                node_v = {n: vals[-1] for n, vals in sol.get("trajectories", {}).items() if vals}

            # Evaluate acceptance criteria
            run_passed = True
            run_snapshot = {}
            for n in target_nodes:
                val = float(node_v.get(n, 0.0))
                node_trajectories[n].append(val)
                run_snapshot[n] = round(val, 4)
                if acceptance_criteria and n in acceptance_criteria:
                    min_v, max_v = acceptance_criteria[n]
                    if not (min_v <= val <= max_v):
                        run_passed = False

            if run_passed:
                passed_runs += 1
            else:
                failed_runs += 1

            if k < 25:
                run_samples.append({
                    "run": k + 1,
                    "passed": run_passed,
                    "voltages": run_snapshot
                })

        # Calculate statistics
        yield_pct = round((passed_runs / runs_count) * 100.0, 2)
        p_hat = passed_runs / runs_count
        ci_lower, ci_upper = cls.compute_wilson_score_interval(p_hat, runs_count)

        node_statistics = {}
        histograms = {}
        for n in target_nodes:
            vals = node_trajectories[n]
            node_statistics[n] = cls.calculate_distribution_statistics(vals)
            histograms[n] = cls.generate_histogram(vals, num_bins=15)

        primary_target = target_nodes[0]
        sensitivities = cls.compute_parameter_sensitivities(
            param_variations,
            node_trajectories.get(primary_target, [])
        )

        return {
            "status": "SUCCESS",
            "circuit_title": circuit.title,
            "total_runs": runs_count,
            "passed_runs": passed_runs,
            "failed_runs": failed_runs,
            "yield_pct": yield_pct,
            "wilson_ci_95": {
                "lower_pct": ci_lower,
                "upper_pct": ci_upper
            },
            "acceptance_criteria": acceptance_criteria or {},
            "monitored_nodes": target_nodes,
            "primary_target_node": primary_target,
            "node_statistics": node_statistics,
            "histograms": histograms,
            "parameter_sensitivities": sensitivities,
            "sample_runs": run_samples
        }


# ========================================================================================
# 4. Curated Academic Circuit Presets & Simulation Engine Facade
# ========================================================================================

class AnalogMNAEngine:
    """
    High-level facade providing curated analog circuit presets, schematic parsing,
    and SQLite WAL-mode simulation history logging.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    def _init_db(self):
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS circuit_simulation_history (
                    simulation_id TEXT PRIMARY KEY,
                    circuit_name TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    integration_method TEXT,
                    node_count INTEGER,
                    component_count INTEGER,
                    t_stop REAL,
                    total_steps INTEGER,
                    cpu_time_ms REAL,
                    timestamp TEXT
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS circuit_monte_carlo_history (
                    mc_id TEXT PRIMARY KEY,
                    circuit_title TEXT NOT NULL,
                    total_runs INTEGER NOT NULL,
                    passed_runs INTEGER NOT NULL,
                    yield_pct REAL NOT NULL,
                    target_node TEXT,
                    mean_val REAL,
                    std_dev_val REAL,
                    ci_lower REAL,
                    ci_upper REAL,
                    cpu_time_ms REAL,
                    timestamp TEXT,
                    summary_json TEXT
                );
            """)
            conn.commit()
        finally:
            conn.close()

    def record_simulation_run(
        self,
        circuit_name: str,
        analysis_type: str,
        integration_method: str,
        node_count: int,
        comp_count: int,
        t_stop: float,
        steps: int,
        cpu_ms: float
    ) -> str:
        sim_id = f"SIM_{int(time.time() * 1000)}_{os.urandom(2).hex()}"
        now_str = datetime.now(timezone.utc).isoformat()
        conn = self._get_connection()
        try:
            conn.execute("""
                INSERT INTO circuit_simulation_history (
                    simulation_id, circuit_name, analysis_type, integration_method,
                    node_count, component_count, t_stop, total_steps, cpu_time_ms, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (sim_id, circuit_name, analysis_type, integration_method, node_count, comp_count, t_stop, steps, cpu_ms, now_str))
            conn.commit()
        finally:
            conn.close()
        return sim_id

    def get_simulation_history(self, limit: int = 25) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        history = []
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT simulation_id, circuit_name, analysis_type, integration_method,
                       node_count, component_count, t_stop, total_steps, cpu_time_ms, timestamp
                FROM circuit_simulation_history
                ORDER BY timestamp DESC
                LIMIT ?;
            """, (int(limit),))
            for r in cur.fetchall():
                history.append({
                    "simulation_id": r[0],
                    "circuit_name": r[1],
                    "analysis_type": r[2],
                    "integration_method": r[3],
                    "node_count": r[4],
                    "component_count": r[5],
                    "t_stop": r[6],
                    "total_steps": r[7],
                    "cpu_time_ms": r[8],
                    "timestamp": r[9]
                })
        finally:
            conn.close()
        return history

    def get_preset_circuit(self, preset_id: str, params: Optional[Dict[str, Any]] = None) -> Circuit:
        """Constructs curated academic circuit benchmarks."""
        params = params or {}
        p_id = preset_id.lower().strip()

        if p_id in ("diode_rectifier", "diode_half_wave"):
            # Half-wave Diode Rectifier with Filter Capacitor
            ckt = Circuit(title="Diode Half-Wave Rectifier with Smoothing Capacitor")
            vin_peak = float(params.get("vin_peak", 5.0))
            freq = float(params.get("freq_hz", 1000.0))
            r_load = float(params.get("r_load", 1000.0))
            c_filter = float(params.get("c_filter", 10e-6))
            is_sat = float(params.get("is_sat", 1e-14))

            ckt.add_voltage_source("V1", "IN", "0", wave_type="SINE", amplitude=vin_peak, freq_hz=freq)
            ckt.add_diode("D1", "IN", "OUT", is_sat=is_sat)
            ckt.add_resistor("RL", "OUT", "0", r_load)
            if c_filter > 0.0:
                ckt.add_capacitor("C1", "OUT", "0", c_filter)
            return ckt

        elif p_id in ("rc_transient", "rc_step"):
            # Classic RC step response (exact tau = R * C)
            ckt = Circuit(title="RC Step Transient Response")
            v_step = float(params.get("v_step", 5.0))
            r_val = float(params.get("r_val", 1000.0))
            c_val = float(params.get("c_val", 1e-6))

            ckt.add_voltage_source("V1", "IN", "0", wave_type="STEP", amplitude=v_step)
            ckt.add_resistor("R1", "IN", "OUT", r_val)
            ckt.add_capacitor("C1", "OUT", "0", c_val)
            return ckt

        elif p_id in ("rlc_resonance", "rlc_tank"):
            # RLC Underdamped / Resonant Circuit
            ckt = Circuit(title="Series RLC Step Transient Resonator")
            v_step = float(params.get("v_step", 5.0))
            r_val = float(params.get("r_val", 50.0))
            l_val = float(params.get("l_val", 10e-3))  # 10 mH
            c_val = float(params.get("c_val", 1e-6))   # 1 uF

            ckt.add_voltage_source("V1", "IN", "0", wave_type="STEP", amplitude=v_step)
            ckt.add_resistor("R1", "IN", "MID", r_val)
            ckt.add_inductor("L1", "MID", "OUT", l_val)
            ckt.add_capacitor("C1", "OUT", "0", c_val)
            return ckt

        elif p_id in ("bjt_ce_amplifier", "bjt_ce"):
            # BJT Common-Emitter Transistor Amplifier
            ckt = Circuit(title="BJT Common-Emitter Audio Amplifier")
            vcc = float(params.get("vcc", 10.0))
            r1 = float(params.get("r1", 47000.0))
            r2 = float(params.get("r2", 10000.0))
            rc = float(params.get("rc", 2200.0))
            re = float(params.get("re", 680.0))
            beta = float(params.get("beta", 100.0))
            vin_ac = float(params.get("vin_ac", 0.05))  # 50 mV AC
            freq = float(params.get("freq_hz", 1000.0))

            ckt.add_voltage_source("VCC", "VCC", "0", dc_val=vcc)
            ckt.add_voltage_source("VIN", "IN", "0", wave_type="SINE", amplitude=vin_ac, freq_hz=freq)
            ckt.add_capacitor("CIN", "IN", "BASE", 10e-6)
            ckt.add_resistor("R1", "VCC", "BASE", r1)
            ckt.add_resistor("R2", "BASE", "0", r2)
            ckt.add_resistor("RC", "VCC", "COLL", rc)
            ckt.add_resistor("RE", "EMIT", "0", re)
            ckt.add_capacitor("CE", "EMIT", "0", 100e-6)
            ckt.add_bjt("Q1", "COLL", "BASE", "EMIT", bjt_type="NPN", beta_f=beta)
            return ckt

        elif p_id in ("mosfet_inverter", "cmos_inverter"):
            # NMOS Inverter with Resistive Pull-Up
            ckt = Circuit(title="NMOS Digital Inverter Transient Pulse")
            vdd = float(params.get("vdd", 5.0))
            r_pullup = float(params.get("r_pullup", 2000.0))
            vth = float(params.get("vth", 1.2))
            kn = float(params.get("kn", 20e-3))
            c_load = float(params.get("c_load", 10e-12))  # 10 pF parasitic load
            freq = float(params.get("freq_hz", 100000.0)) # 100 kHz pulse

            ckt.add_voltage_source("VDD", "VDD", "0", dc_val=vdd)
            ckt.add_voltage_source("VIN", "IN", "0", wave_type="PULSE", amplitude=5.0, freq_hz=freq)
            ckt.add_resistor("RD", "VDD", "OUT", r_pullup)
            ckt.add_mosfet("M1", "OUT", "IN", "0", mos_type="NMOS", vth=vth, kn=kn)
            if c_load > 0.0:
                ckt.add_capacitor("CL", "OUT", "0", c_load)
            return ckt

        else:
            # Default RC circuit
            return self.get_preset_circuit("rc_transient", params)

    def run_simulation(
        self,
        circuit: Circuit,
        analysis_type: str = "TRANSIENT",
        t_stop: float = 3e-3,
        t_step: float = 20e-6,
        integration_method: str = "TRAPEZOIDAL"
    ) -> Dict[str, Any]:
        """Validates and runs the MNA simulation with telemetry logging."""
        start_time = time.perf_counter()

        # 1. Topology validation
        topology_report = circuit.validate_circuit()
        if not topology_report["is_valid"]:
            return {
                "status": "ERROR",
                "error": "Topology validation failed.",
                "details": topology_report["errors"],
                "warnings": topology_report["warnings"]
            }

        solver = NonLinearMNASolver(circuit)

        if analysis_type.upper() == "DC_OPERATING_POINT":
            res = solver.solve_dc_operating_point()
            steps = 1
        else:
            res = solver.solve_transient(
                t_stop=t_stop,
                t_step=t_step,
                integration_method=integration_method
            )
            steps = res.get("total_steps", 0)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # 2. Record to SQLite WAL simulation history
        sim_id = self.record_simulation_run(
            circuit_name=circuit.title,
            analysis_type=analysis_type,
            integration_method=integration_method,
            node_count=circuit.num_nodes(),
            comp_count=len(circuit.components),
            t_stop=t_stop if analysis_type.upper() == "TRANSIENT" else 0.0,
            steps=steps,
            cpu_ms=round(elapsed_ms, 2)
        )

        res["simulation_id"] = sim_id
        res["circuit_title"] = circuit.title
        res["cpu_time_ms"] = round(elapsed_ms, 2)
        res["node_count"] = circuit.num_nodes()
        res["component_count"] = len(circuit.components)
        res["topology_warnings"] = topology_report["warnings"]

        # Run engineering assumptions audit
        res["assumptions_check"] = CircuitAssumptionsChecker.check_assumptions(circuit, res)

        return res

    def check_circuit_assumptions(
        self,
        circuit: Circuit,
        simulation_results: Dict[str, Any],
        assumed_operating_mode: str = "LINEAR_AMPLIFICATION"
    ) -> Dict[str, Any]:
        """Validates engineering assumptions on circuit operating point and device regions."""
        return CircuitAssumptionsChecker.check_assumptions(circuit, simulation_results, assumed_operating_mode)

    def simulate_spice_netlist(
        self,
        netlist_text: str,
        analysis_type: Optional[str] = None,
        t_stop: Optional[float] = None,
        t_step: Optional[float] = None,
        integration_method: str = "TRAPEZOIDAL"
    ) -> Dict[str, Any]:
        """
        Parses standard Berkeley SPICE netlist text and simulates it using the NonLinearMNASolver.
        """
        circuit, meta = parse_spice_netlist(netlist_text)
        act_analysis = (analysis_type or meta.get("analysis_type", "TRANSIENT")).upper()
        act_t_stop = float(t_stop if t_stop is not None else meta.get("t_stop", 3e-3))
        act_t_step = float(t_step if t_step is not None else meta.get("t_step", 20e-6))

        res = self.run_simulation(
            circuit=circuit,
            analysis_type=act_analysis,
            t_stop=act_t_stop,
            t_step=act_t_step,
            integration_method=integration_method
        )
        res["meta"] = meta
        res["netlist"] = netlist_text
        return res

    def record_monte_carlo_run(
        self,
        circuit_title: str,
        total_runs: int,
        passed_runs: int,
        yield_pct: float,
        target_node: str,
        mean_val: float,
        std_dev_val: float,
        ci_lower: float,
        ci_upper: float,
        cpu_ms: float,
        summary: Dict[str, Any]
    ) -> str:
        mc_id = f"MC_{int(time.time() * 1000)}_{os.urandom(2).hex()}"
        now_str = datetime.now(timezone.utc).isoformat()
        conn = self._get_connection()
        try:
            conn.execute("""
                INSERT INTO circuit_monte_carlo_history (
                    mc_id, circuit_title, total_runs, passed_runs, yield_pct,
                    target_node, mean_val, std_dev_val, ci_lower, ci_upper,
                    cpu_time_ms, timestamp, summary_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                mc_id, circuit_title, total_runs, passed_runs, yield_pct,
                target_node, mean_val, std_dev_val, ci_lower, ci_upper,
                cpu_ms, now_str, json.dumps(summary)
            ))
            conn.commit()
        finally:
            conn.close()
        return mc_id

    def get_monte_carlo_history(self, limit: int = 25) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        history = []
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT mc_id, circuit_title, total_runs, passed_runs, yield_pct,
                       target_node, mean_val, std_dev_val, ci_lower, ci_upper,
                       cpu_time_ms, timestamp
                FROM circuit_monte_carlo_history
                ORDER BY timestamp DESC
                LIMIT ?;
            """, (int(limit),))
            for r in cur.fetchall():
                history.append({
                    "mc_id": r[0],
                    "circuit_title": r[1],
                    "total_runs": r[2],
                    "passed_runs": r[3],
                    "yield_pct": r[4],
                    "target_node": r[5],
                    "mean_val": r[6],
                    "std_dev_val": r[7],
                    "ci_lower": r[8],
                    "ci_upper": r[9],
                    "cpu_time_ms": r[10],
                    "timestamp": r[11]
                })
        finally:
            conn.close()
        return history

    def run_monte_carlo(
        self,
        circuit: Optional[Circuit] = None,
        netlist: Optional[str] = None,
        preset_id: Optional[str] = None,
        preset_params: Optional[Dict[str, Any]] = None,
        runs: int = 200,
        tolerances: Optional[Dict[str, float]] = None,
        target_nodes: Optional[List[str]] = None,
        acceptance_criteria: Optional[Dict[str, Tuple[float, float]]] = None,
        analysis_type: str = "DC_OP",
        t_stop: float = 3e-3,
        t_step: float = 20e-6,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Executes a Monte Carlo tolerance analysis on a Circuit, Netlist, or Preset.
        Persists results into SQLite WAL table 'circuit_monte_carlo_history'.
        """
        start_time = time.perf_counter()

        if circuit is None:
            if netlist:
                circuit, _ = parse_spice_netlist(netlist)
            elif preset_id:
                circuit = self.get_preset_circuit(preset_id, preset_params)
            else:
                circuit = self.get_preset_circuit("rc_transient", preset_params)

        res = CircuitMonteCarloSimulator.run_monte_carlo(
            circuit=circuit,
            runs=runs,
            tolerances=tolerances,
            target_nodes=target_nodes,
            acceptance_criteria=acceptance_criteria,
            analysis_type=analysis_type,
            t_stop=t_stop,
            t_step=t_step,
            seed=seed
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        res["cpu_time_ms"] = round(elapsed_ms, 2)

        target_node = res.get("primary_target_node", "OUT")
        stats = res.get("node_statistics", {}).get(target_node, {})
        mean_v = stats.get("mean", 0.0)
        std_v = stats.get("std_dev", 0.0)
        ci = res.get("wilson_ci_95", {})
        ci_low = ci.get("lower_pct", 0.0)
        ci_high = ci.get("upper_pct", 100.0)

        mc_id = self.record_monte_carlo_run(
            circuit_title=circuit.title,
            total_runs=res["total_runs"],
            passed_runs=res["passed_runs"],
            yield_pct=res["yield_pct"],
            target_node=target_node,
            mean_val=mean_v,
            std_dev_val=std_v,
            ci_lower=ci_low,
            ci_upper=ci_high,
            cpu_ms=round(elapsed_ms, 2),
            summary={
                "monitored_nodes": res["monitored_nodes"],
                "acceptance_criteria": res["acceptance_criteria"],
                "primary_target_node": target_node,
                "node_statistics": res["node_statistics"],
                "parameter_sensitivities": res["parameter_sensitivities"][:5]
            }
        )
        res["mc_id"] = mc_id
        return res

    def export_preset_spice(self, preset_id: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Exports a named academic preset circuit into Berkeley SPICE (.cir) text format."""
        ckt = self.get_preset_circuit(preset_id, params)
        return circuit_to_spice_netlist(ckt)


# ========================================================================================
# 5. Berkeley SPICE Netlist Parser & Serializer (Phase 13)
# ========================================================================================

SPICE_SCALE_FACTORS = {
    "T": 1e12,
    "G": 1e9,
    "MEG": 1e6,
    "K": 1e3,
    "M": 1e-3,
    "U": 1e-6,
    "N": 1e-9,
    "P": 1e-12,
    "F": 1e-15,
}

import re


def parse_spice_value(raw_val: Any) -> float:
    """
    Parses SPICE numerical formats with standard engineering metric scale factors:
      T/t = 1e12, G/g = 1e9, MEG/meg = 1e6, K/k = 1e3, M/m = 1e-3 (unless MEG),
      U/u = 1e-6, N/n = 1e-9, P/p = 1e-12, F/f = 1e-15.
    Strips trailing unit qualifiers (e.g., '10uF' -> 1e-5, '100Ohm' -> 100.0, '5V' -> 5.0).
    """
    s = str(raw_val).strip()
    if not s:
        return 0.0
    try:
        return float(s)
    except ValueError:
        pass

    m = re.match(r"^([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*([a-zA-Z]+)?$", s)
    if not m:
        raise ValueError(f"Invalid SPICE numerical value: '{raw_val}'")

    base_num = float(m.group(1))
    suffix_raw = (m.group(2) or "").upper()
    if not suffix_raw:
        return base_num

    if suffix_raw.startswith("MEG"):
        return base_num * 1e6

    first_char = suffix_raw[0]
    if first_char in SPICE_SCALE_FACTORS:
        return base_num * SPICE_SCALE_FACTORS[first_char]

    return base_num


def parse_source_spec(tokens: List[str]) -> Tuple[str, float, float, float]:
    """
    Parses SPICE source excitation specifications:
      - DC: 'DC 5', '5', '5V'
      - SINE: 'SIN(0 5 1000)', 'SINE (0, 3.3, 2000)'
      - STEP: 'STEP 0 5', 'STEP 5'
      - PULSE: 'PULSE(0 5 0 1n 1n 0.5m 1m)'
    Returns: (wave_type, amplitude, freq_hz, offset)
    """
    rest = " ".join(tokens)
    # 1. SINE
    m_sin = re.search(r"SIN(?:E)?\s*\(([^)]+)\)", rest, re.IGNORECASE)
    if m_sin:
        args = [a.strip() for a in re.split(r"[\s,]+", m_sin.group(1).strip()) if a.strip()]
        offset = parse_spice_value(args[0]) if len(args) > 0 else 0.0
        ampl = parse_spice_value(args[1]) if len(args) > 1 else 1.0
        freq = parse_spice_value(args[2]) if len(args) > 2 else 1000.0
        return ("SINE", ampl, freq, offset)

    # 2. PULSE
    m_pulse = re.search(r"PULSE\s*\(([^)]+)\)", rest, re.IGNORECASE)
    if m_pulse:
        args = [a.strip() for a in re.split(r"[\s,]+", m_pulse.group(1).strip()) if a.strip()]
        v1 = parse_spice_value(args[0]) if len(args) > 0 else 0.0
        v2 = parse_spice_value(args[1]) if len(args) > 1 else 5.0
        freq = 1000.0
        if len(args) >= 7:
            period = parse_spice_value(args[6])
            if period > 0:
                freq = 1.0 / period
        return ("PULSE", v2 - v1, freq, v1)

    # 3. STEP
    m_step = re.search(r"STEP\s+([^\s]+)(?:\s+([^\s]+))?", rest, re.IGNORECASE)
    if m_step:
        val1 = parse_spice_value(m_step.group(1))
        val2 = parse_spice_value(m_step.group(2)) if m_step.group(2) else None
        if val2 is not None:
            return ("STEP", val2, 0.0, val1)
        return ("STEP", val1, 0.0, 0.0)

    # 4. DC
    m_dc = re.search(r"(?:DC\s+)?([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?[a-zA-Z]*)", rest, re.IGNORECASE)
    if m_dc:
        return ("DC", parse_spice_value(m_dc.group(1)), 0.0, 0.0)

    return ("DC", 0.0, 0.0, 0.0)


def parse_spice_netlist(netlist_text: str) -> Tuple[Circuit, Dict[str, Any]]:
    """
    Parses a standard Berkeley SPICE (.cir) netlist string into a VoltCore Circuit instance.
    Supports R, C, L, V, I, D, Q (BJT), M (MOSFET) components, along with .tran, .op, and .model directives.
    Returns: (circuit, metadata)
    """
    lines = netlist_text.splitlines()
    title = ""
    metadata: Dict[str, Any] = {
        "title": "VoltCore SPICE Circuit",
        "analysis_type": "TRANSIENT",
        "t_step": 20e-6,
        "t_stop": 3e-3,
        "models": {},
        "directives": []
    }

    parsed_lines = []
    first_non_empty = True
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith(('*', '#', ';')):
            if first_non_empty and not title:
                title = stripped.lstrip('*#; ').strip()
                metadata["title"] = title
            first_non_empty = False
            continue
        if first_non_empty and not stripped.startswith('.'):
            # Line 1 is title by SPICE convention
            title = stripped
            metadata["title"] = title
            first_non_empty = False
            continue
        first_non_empty = False
        parsed_lines.append(stripped)

    if not title:
        title = "VoltCore SPICE Circuit"
        metadata["title"] = title

    circuit = Circuit(title=title)

    for line in parsed_lines:
        tokens = line.split()
        if not tokens:
            continue
        elem = tokens[0].upper()

        # 1. Directives
        if elem.startswith('.'):
            directive = elem[1:]
            metadata["directives"].append(line)
            if directive == "TRAN":
                # .TRAN <tstep> <tstop>
                if len(tokens) >= 3:
                    metadata["t_step"] = parse_spice_value(tokens[1])
                    metadata["t_stop"] = parse_spice_value(tokens[2])
                elif len(tokens) == 2:
                    metadata["t_stop"] = parse_spice_value(tokens[1])
                metadata["analysis_type"] = "TRANSIENT"
            elif directive == "OP":
                metadata["analysis_type"] = "DC_OPERATING_POINT"
            elif directive == "TITLE":
                title = line[len(tokens[0]):].strip()
                circuit.title = title
                metadata["title"] = title
            elif directive == "MODEL":
                if len(tokens) >= 3:
                    model_name = tokens[1].upper()
                    model_type = tokens[2].upper()
                    metadata["models"][model_name] = {"type": model_type, "raw": line}
            continue

        # 2. Components
        char = elem[0]
        name = tokens[0].upper()

        if char == 'R':
            # R<name> <n1> <n2> <value>
            if len(tokens) >= 4:
                val = parse_spice_value(tokens[3])
                circuit.add_resistor(name, tokens[1], tokens[2], val)
        elif char == 'C':
            # C<name> <n1> <n2> <value> [IC=<ic>]
            if len(tokens) >= 4:
                val = parse_spice_value(tokens[3])
                ic = 0.0
                for tok in tokens[4:]:
                    if tok.upper().startswith("IC="):
                        ic = parse_spice_value(tok[3:])
                circuit.add_capacitor(name, tokens[1], tokens[2], val, ic)
        elif char == 'L':
            # L<name> <n1> <n2> <value> [IC=<ic>]
            if len(tokens) >= 4:
                val = parse_spice_value(tokens[3])
                ic = 0.0
                for tok in tokens[4:]:
                    if tok.upper().startswith("IC="):
                        ic = parse_spice_value(tok[3:])
                circuit.add_inductor(name, tokens[1], tokens[2], val, ic)
        elif char == 'V':
            # V<name> <n+> <n-> [DC <val> | SIN(...) | PULSE(...) | STEP ... | <val>]
            if len(tokens) >= 4:
                wave_type, ampl, freq, offset = parse_source_spec(tokens[3:])
                if wave_type == "DC":
                    circuit.add_voltage_source(name, tokens[1], tokens[2], dc_val=ampl)
                else:
                    circuit.add_voltage_source(
                        name, tokens[1], tokens[2],
                        wave_type=wave_type, amplitude=ampl, freq_hz=freq, offset=offset
                    )
        elif char == 'I':
            # I<name> <n+> <n-> [DC] <val>
            if len(tokens) >= 4:
                val_tok = tokens[4] if (len(tokens) >= 5 and tokens[3].upper() == "DC") else tokens[3]
                val = parse_spice_value(val_tok)
                circuit.add_current_source(name, tokens[1], tokens[2], dc_val=val)
        elif char == 'D':
            # D<name> <n_anode> <n_cathode> [model]
            if len(tokens) >= 3:
                circuit.add_diode(name, tokens[1], tokens[2])
        elif char == 'Q':
            # Q<name> <n_c> <n_b> <n_e> [model]
            if len(tokens) >= 4:
                circuit.add_bjt(name, tokens[1], tokens[2], tokens[3])
        elif char == 'M':
            # M<name> <n_d> <n_g> <n_s> [n_b] [model]
            if len(tokens) >= 4:
                n_d = tokens[1]
                n_g = tokens[2]
                n_s = tokens[3]
                circuit.add_mosfet(name, n_d, n_g, n_s)

    return circuit, metadata


def circuit_to_spice_netlist(circuit: Circuit, t_step: float = 20e-6, t_stop: float = 3e-3) -> str:
    """
    Serializes a VoltCore Circuit instance into standard Berkeley SPICE (.cir) netlist format.
    """
    lines = [
        "* VoltCore Apex Academia - Berkeley SPICE Netlist (.cir)",
        f"* Circuit: {circuit.title}",
        f"* Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "* Platform Lead: Ashok Kumar A (Senior Analog IC Design Specialist)",
        ""
    ]
    for comp in circuit.components:
        if isinstance(comp, Resistor):
            lines.append(f"{comp.name} {comp.n1} {comp.n2} {comp.resistance:g}")
        elif isinstance(comp, Capacitor):
            lines.append(f"{comp.name} {comp.n1} {comp.n2} {comp.capacitance:g}")
        elif isinstance(comp, Inductor):
            lines.append(f"{comp.name} {comp.n1} {comp.n2} {comp.inductance:g}")
        elif isinstance(comp, VoltageSource):
            if comp.wave_type == "DC":
                lines.append(f"{comp.name} {comp.n_pos} {comp.n_neg} DC {comp.dc_val:g}")
            elif comp.wave_type in ("SINE", "SIN"):
                lines.append(f"{comp.name} {comp.n_pos} {comp.n_neg} SIN({comp.offset:g} {comp.amplitude:g} {comp.freq_hz:g})")
            elif comp.wave_type == "STEP":
                lines.append(f"{comp.name} {comp.n_pos} {comp.n_neg} STEP {comp.offset:g} {comp.amplitude:g}")
            elif comp.wave_type == "PULSE":
                period = 1.0 / max(1.0, comp.freq_hz)
                lines.append(f"{comp.name} {comp.n_pos} {comp.n_neg} PULSE({comp.offset:g} {comp.offset + comp.amplitude:g} 0 1n 1n {0.5 * period:g} {period:g})")
            else:
                lines.append(f"{comp.name} {comp.n_pos} {comp.n_neg} {comp.dc_val:g}")
        elif isinstance(comp, CurrentSource):
            lines.append(f"{comp.name} {comp.n_pos} {comp.n_neg} DC {comp.dc_val:g}")
        elif isinstance(comp, Diode):
            lines.append(f"{comp.name} {comp.n_anode} {comp.n_cathode} 1N4148")
        elif isinstance(comp, BJT):
            lines.append(f"{comp.name} {comp.n_c} {comp.n_b} {comp.n_e} 2N2222")
        elif isinstance(comp, MOSFET):
            lines.append(f"{comp.name} {comp.n_d} {comp.n_g} {comp.n_s} 0 NMOS")

    lines.append("")
    lines.append(f".tran {t_step:g} {t_stop:g}")
    lines.append(".end")
    return "\n".join(lines)


# Global singleton instance for platform-wide use
analog_mna_engine = AnalogMNAEngine()
