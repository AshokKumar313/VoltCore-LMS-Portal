"""
========================================================================================
VoltCore Apex Academia - IoT Smart Laboratory & Equipment Telemetry Hub
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/iot_telemetry_hub.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Lightweight telemetry manager for smart laboratory instruments (oscilloscopes,
  DC power supplies, soldering stations, and fume extractors) in MIT Campus Lab 304.
  Tracks real-time power, operational hours, automated fault alerts, and bookings.
========================================================================================
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import threading

# Standard MIT Campus Lab 304 Equipment Registry
DEFAULT_LAB_EQUIPMENT = [
    {
        "equipment_id": "OSC-DSOX1204G-01",
        "name": "Keysight DSOX1204G 4-Channel 100MHz Digital Storage Oscilloscope",
        "bench_id": "BENCH_304_A",
        "category": "Oscilloscope",
        "status": "ONLINE_IDLE",
        "current_power_watts": 24.5,
        "voltage_v": 230.2,
        "current_a": 0.106,
        "cumulative_hours": 184.2,
        "maintenance_interval_hours": 500.0,
        "temperature_c": 36.4,
        "active_booking": None,
        "max_current_a": 1.0,
        "max_temperature_c": 60.0
    },
    {
        "equipment_id": "PSU-DP832-02",
        "name": "Rigol DP832 Programmable Triple-Output Precision DC Power Supply",
        "bench_id": "BENCH_304_A",
        "category": "PowerSupply",
        "status": "IN_USE",
        "current_power_watts": 68.4,
        "voltage_v": 230.0,
        "current_a": 0.297,
        "cumulative_hours": 242.8,
        "maintenance_interval_hours": 400.0,
        "temperature_c": 42.1,
        "active_booking": "2023MITEC042",
        "max_current_a": 3.2,
        "max_temperature_c": 65.0
    },
    {
        "equipment_id": "SOLD-WT1010-03",
        "name": "Weller WT1010 High-Precision ESD-Safe Soldering Station",
        "bench_id": "BENCH_304_B",
        "category": "Soldering",
        "status": "MAINTENANCE_DUE",
        "current_power_watts": 85.0,
        "voltage_v": 229.8,
        "current_a": 0.370,
        "cumulative_hours": 204.5,
        "maintenance_interval_hours": 200.0,  # 200h tip oxidation limit
        "temperature_c": 51.3,
        "active_booking": None,
        "max_current_a": 0.8,
        "max_temperature_c": 75.0
    },
    {
        "equipment_id": "FUME-FA430-04",
        "name": "Hakko FA-430 High-Efficiency HEPA Fume Extraction System",
        "bench_id": "BENCH_304_B",
        "category": "FumeExtractor",
        "status": "ONLINE_IDLE",
        "current_power_watts": 110.0,
        "voltage_v": 230.1,
        "current_a": 0.478,
        "cumulative_hours": 145.0,
        "maintenance_interval_hours": 300.0,  # 300h filter lifespan
        "temperature_c": 34.8,
        "active_booking": None,
        "max_current_a": 1.5,
        "max_temperature_c": 55.0
    }
]


class SmartLabTelemetryHub:
    """
    Real-time telemetry and equipment asset manager for MIT Campus Smart ECE Laboratory.
    Maintains zero polling overhead and enforces RBAC permission controls on fault dispatch.
    """

    def __init__(self, initial_equipment: Optional[List[Dict[str, Any]]] = None):
        self._equipment = {
            item["equipment_id"]: dict(item)
            for item in (initial_equipment or DEFAULT_LAB_EQUIPMENT)
        }
        self._alerts: List[Dict[str, Any]] = []
        self._fault_tickets: List[Dict[str, Any]] = []
        self._booking_history: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

        # Seed initial alert for pre-expired maintenance gear
        for eq in self._equipment.values():
            if eq["cumulative_hours"] >= eq["maintenance_interval_hours"]:
                self._alerts.append({
                    "alert_id": f"ALT_{eq['equipment_id']}_MAINT",
                    "equipment_id": eq["equipment_id"],
                    "severity": "WARNING",
                    "type": "MAINTENANCE_DUE",
                    "message": f"Maintenance due on {eq['name']} (Operating hours: {eq['cumulative_hours']} >= {eq['maintenance_interval_hours']} limit)",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

    def ingest_telemetry(
        self,
        equipment_id: str,
        voltage_v: float,
        current_a: float,
        temperature_c: float,
        power_watts: Optional[float] = None,
        hours_increment: float = 0.0
    ) -> Dict[str, Any]:
        """
        Ingests real-time power & environmental telemetry from an equipment sensor node.
        Calculates power, evaluates safety limits, and generates maintenance alarms.
        """
        with self._lock:
            if equipment_id not in self._equipment:
                return {
                    "status": "ERROR",
                    "error": f"Equipment '{equipment_id}' not found in registry"
                }

            eq = self._equipment[equipment_id]
            calc_power = power_watts if power_watts is not None else round(voltage_v * current_a, 2)

            eq["voltage_v"] = round(voltage_v, 2)
            eq["current_a"] = round(current_a, 3)
            eq["current_power_watts"] = round(calc_power, 2)
            eq["temperature_c"] = round(temperature_c, 1)
            eq["cumulative_hours"] = round(eq["cumulative_hours"] + hours_increment, 2)

            new_alerts: List[Dict[str, Any]] = []

            # 1. Over-current trip check
            if current_a > eq["max_current_a"]:
                alert = {
                    "alert_id": f"ALT_{equipment_id}_{int(time.time())}",
                    "equipment_id": equipment_id,
                    "severity": "CRITICAL",
                    "type": "OVER_CURRENT_TRIP",
                    "message": f"Over-current fault on {eq['name']}: {current_a}A exceeds maximum safe threshold {eq['max_current_a']}A",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                new_alerts.append(alert)
                eq["status"] = "FAULT_ALERT"
                self._alerts.append(alert)

            # 2. Thermal overload check
            elif temperature_c > eq["max_temperature_c"]:
                alert = {
                    "alert_id": f"ALT_{equipment_id}_TEMP_{int(time.time())}",
                    "equipment_id": equipment_id,
                    "severity": "HIGH",
                    "type": "TEMPERATURE_OVERLOAD",
                    "message": f"Thermal limit exceeded on {eq['name']}: {temperature_c}°C exceeds limit {eq['max_temperature_c']}°C",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                new_alerts.append(alert)
                eq["status"] = "FAULT_ALERT"
                self._alerts.append(alert)

            # 3. Scheduled Maintenance Check
            elif eq["cumulative_hours"] >= eq["maintenance_interval_hours"]:
                eq["status"] = "MAINTENANCE_DUE"

            return {
                "status": "SUCCESS",
                "equipment_id": equipment_id,
                "current_power_watts": eq["current_power_watts"],
                "cumulative_hours": eq["cumulative_hours"],
                "equipment_status": eq["status"],
                "new_alerts": new_alerts
            }

    def book_equipment(
        self,
        equipment_id: str,
        student_id: str = "2023MITEC042",
        bench_slot: str = "SLOT_MORNING"
    ) -> Dict[str, Any]:
        """
        Books smart laboratory equipment for an authenticated student session.
        """
        with self._lock:
            if equipment_id not in self._equipment:
                return {"status": "ERROR", "error": f"Equipment {equipment_id} not found"}

            eq = self._equipment[equipment_id]
            if eq["status"] in ("FAULT_ALERT", "MAINTENANCE_DUE"):
                return {
                    "status": "REJECTED",
                    "error": f"Cannot book {eq['name']}: equipment is currently in {eq['status']} state"
                }

            if eq["active_booking"] is not None and eq["active_booking"] != student_id:
                return {
                    "status": "REJECTED",
                    "error": f"Equipment {eq['name']} is currently in use by student {eq['active_booking']}"
                }

            eq["status"] = "IN_USE"
            eq["active_booking"] = student_id

            booking_record = {
                "booking_id": f"BKG_{equipment_id}_{int(time.time())}",
                "equipment_id": equipment_id,
                "equipment_name": eq["name"],
                "student_id": student_id,
                "bench_slot": bench_slot,
                "start_time": datetime.now(timezone.utc).isoformat()
            }
            self._booking_history.append(booking_record)

            return {
                "status": "SUCCESS",
                "booking": booking_record,
                "xp_reward": 120
            }

    def release_equipment(self, equipment_id: str) -> Dict[str, Any]:
        """
        Releases an active equipment session back to ONLINE_IDLE status.
        """
        with self._lock:
            if equipment_id not in self._equipment:
                return {"status": "ERROR", "error": "Equipment not found"}

            eq = self._equipment[equipment_id]
            prev_student = eq["active_booking"]
            eq["active_booking"] = None
            if eq["status"] == "IN_USE":
                eq["status"] = "ONLINE_IDLE"

            return {
                "status": "SUCCESS",
                "equipment_id": equipment_id,
                "released_from": prev_student,
                "new_status": eq["status"]
            }

    def log_fault_ticket(
        self,
        equipment_id: str,
        fault_type: str,
        description: str,
        reported_by: str = "2023MITEC042"
    ) -> Dict[str, Any]:
        """
        Logs an equipment breakdown or calibration drift ticket.
        """
        with self._lock:
            if equipment_id not in self._equipment:
                return {"status": "ERROR", "error": "Equipment not found"}

            eq = self._equipment[equipment_id]
            eq["status"] = "FAULT_ALERT"

            ticket = {
                "ticket_id": f"TCK_{equipment_id}_{int(time.time())}",
                "equipment_id": equipment_id,
                "equipment_name": eq["name"],
                "fault_type": fault_type,
                "description": description,
                "reported_by": reported_by,
                "resolved": False,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            self._fault_tickets.append(ticket)

            return {
                "status": "SUCCESS",
                "ticket": ticket,
                "equipment_status": eq["status"]
            }

    def resolve_fault(
        self,
        equipment_id: str,
        resolution_notes: str,
        resolved_by_role: str = "Student"
    ) -> Dict[str, Any]:
        """
        Resolves equipment fault and resets maintenance counter.
        RBAC Enforcement: Only 'Admin', 'Teacher', or 'Lab-Instructor' roles can resolve.
        """
        privileged_roles = {"Admin", "Teacher", "Lab-Instructor", "Admin_Owner"}
        if resolved_by_role not in privileged_roles:
            return {
                "status": "FORBIDDEN",
                "error": f"Role '{resolved_by_role}' is not authorized to resolve equipment faults. Privileged role required."
            }

        with self._lock:
            if equipment_id not in self._equipment:
                return {"status": "ERROR", "error": "Equipment not found"}

            eq = self._equipment[equipment_id]
            eq["status"] = "ONLINE_IDLE"
            eq["cumulative_hours"] = 0.0  # Reset after servicing

            for t in self._fault_tickets:
                if t["equipment_id"] == equipment_id and not t["resolved"]:
                    t["resolved"] = True
                    t["resolution_notes"] = resolution_notes

            # Prune associated alerts
            self._alerts = [a for a in self._alerts if a["equipment_id"] != equipment_id]

            return {
                "status": "SUCCESS",
                "equipment_id": equipment_id,
                "new_status": eq["status"],
                "resolution_notes": resolution_notes
            }

    def get_lab_overview(self) -> Dict[str, Any]:
        """
        Aggregates real-time laboratory metrics across MIT Campus Lab 304.
        """
        with self._lock:
            equipment_list = list(self._equipment.values())
            total_equipment = len(equipment_list)
            online_count = sum(1 for e in equipment_list if e["status"] in ("ONLINE_IDLE", "IN_USE"))
            in_use_count = sum(1 for e in equipment_list if e["status"] == "IN_USE")
            maintenance_count = sum(1 for e in equipment_list if e["status"] == "MAINTENANCE_DUE")
            fault_count = sum(1 for e in equipment_list if e["status"] == "FAULT_ALERT")

            total_power_watts = round(sum(e["current_power_watts"] for e in equipment_list), 2)
            total_kwh_estimate = round(sum((e["current_power_watts"] * e["cumulative_hours"]) / 1000.0 for e in equipment_list), 2)

            return {
                "laboratory": "MIT Campus Embedded & IoT Systems Laboratory (Lab 304)",
                "institution": "Madras Institute of Technology, Anna University, Chromepet",
                "total_equipment": total_equipment,
                "online_count": online_count,
                "in_use_count": in_use_count,
                "maintenance_count": maintenance_count,
                "fault_count": fault_count,
                "total_power_watts": total_power_watts,
                "total_kwh_estimate": total_kwh_estimate,
                "equipment": equipment_list,
                "active_alerts_count": len(self._alerts),
                "active_alerts": self._alerts[-5:],
                "open_tickets_count": sum(1 for t in self._fault_tickets if not t["resolved"])
            }


# Global Smart Lab Hub singleton
smart_lab_hub = SmartLabTelemetryHub()
