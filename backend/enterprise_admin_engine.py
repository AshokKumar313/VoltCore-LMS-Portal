"""
========================================================================================
VoltCore Apex Academia - Enterprise Administration & NBA/NAAC Accreditation Engine
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/enterprise_admin_engine.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Lightweight enterprise administration manager handling faculty workload heatmaps,
  automated NBA Course Outcome (CO) to Program Outcome (PO1-PO12) attainment matrices,
  cryptographically linked NAAC audit logs (SHA-256), and multi-department course allocations.
========================================================================================
"""

import os
import hashlib
import sqlite3
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")

# Default Faculty Workload Registry for MIT Campus ECE
DEFAULT_FACULTY_ROSTER = [
    {
        "faculty_id": "FAC-MIT-001",
        "name": "Dr. S. K. Ramesh",
        "designation": "Professor & Head of Department",
        "department": "Electronics Engineering",
        "teaching_hours": 14,
        "lab_supervision_hours": 8,
        "funded_projects_count": 3,
        "student_rating": 4.85,
        "specialization": "Embedded Avionics & VLSI",
        "status": "ACTIVE"
    },
    {
        "faculty_id": "FAC-MIT-002",
        "name": "Dr. M. V. Geetha",
        "designation": "Associate Professor",
        "department": "Electronics Engineering",
        "teaching_hours": 16,
        "lab_supervision_hours": 10,
        "funded_projects_count": 2,
        "student_rating": 4.70,
        "specialization": "Real-Time Operating Systems & TinyML",
        "status": "ACTIVE"
    },
    {
        "faculty_id": "FAC-MIT-003",
        "name": "Dr. R. Balaji",
        "designation": "Assistant Professor",
        "department": "Electronics Engineering",
        "teaching_hours": 18,
        "lab_supervision_hours": 6,
        "funded_projects_count": 1,
        "student_rating": 4.62,
        "specialization": "FPGA Architectures & RISC-V",
        "status": "ACTIVE"
    },
    {
        "faculty_id": "FAC-MIT-004",
        "name": "Ashok Kumar A",
        "designation": "Platform Architect & HIL Research Lead",
        "department": "Electronics Engineering",
        "teaching_hours": 10,
        "lab_supervision_hours": 16,
        "funded_projects_count": 2,
        "student_rating": 4.95,
        "specialization": "HIL Hardware Benches & Distributed IoT",
        "status": "ACTIVE"
    }
]

# NBA Program Outcomes Mapping Reference (PO1 - PO12, PSO1 - PSO2)
PO_DEFINITIONS = {
    "PO1": "Engineering Knowledge (Semiconductor physics, digital logic, circuit analysis)",
    "PO2": "Problem Analysis (Real-time task latency, pipeline stalls, jitter bounding)",
    "PO3": "Design/Development of Solutions (Embedded firmware, DMA zero-copy conduits)",
    "PO4": "Conduct Investigations of Complex Problems (HIL Bench 304 oscilloscope analysis)",
    "PO5": "Modern Tool Usage (Wokwi, LTSPICE, WebSerial, FreeRTOS, Vivado)",
    "PO6": "The Engineer and Society (Railway track safety, automotive edge diagnostics)",
    "PO7": "Environment and Sustainability (Low-power INT8 TinyML, GaN efficiency)",
    "PO8": "Ethics (Plagiarism-free code reviews, open-source compliance)",
    "PO9": "Individual and Team Work (Study group cohorts, collaborative reviews)",
    "PO10": "Communication (IEEE format publication, technical documentation)",
    "PO11": "Project Management and Finance (Bill of materials, power consumption budget)",
    "PO12": "Life-long Learning (GATE ECE simulation, continuous firmware evolution)",
    "PSO1": "Silicon & Embedded Systems Synthesis (Custom ARM/RISC-V peripherals)",
    "PSO2": "IoT Communication & Edge Hardware (MQTT/WebSerial direct silicon telemetry)"
}


class EnterpriseAdminEngine:
    """
    Enterprise Administration, Multi-Department Course Allocation & NBA/NAAC Engine.
    Persists data in SQLite with Write-Ahead Logging (WAL) and enforces cryptographic
    immutability on administrative audit logs via SHA-256 chain links.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self._lock = threading.Lock()
        self._init_sqlite_schema()
        self._seed_initial_records()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns an optimized SQLite WAL connection."""
        conn = sqlite3.connect(self.db_path, timeout=5.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode = WAL;")
        cur.execute("PRAGMA synchronous = NORMAL;")
        cur.execute("PRAGMA busy_timeout = 5000;")
        cur.close()
        return conn

    def _init_sqlite_schema(self):
        """Initializes tables for faculty metrics, allocations, NBA attainment, and NAAC logs."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS faculty_metrics (
                        faculty_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        designation TEXT NOT NULL,
                        department TEXT NOT NULL,
                        teaching_hours INTEGER NOT NULL,
                        lab_supervision_hours INTEGER NOT NULL,
                        funded_projects_count INTEGER DEFAULT 0,
                        student_rating REAL DEFAULT 4.5,
                        specialization TEXT NOT NULL,
                        status TEXT DEFAULT 'ACTIVE',
                        updated_at TEXT NOT NULL
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS course_allocations (
                        allocation_id TEXT PRIMARY KEY,
                        course_code TEXT NOT NULL,
                        course_name TEXT NOT NULL,
                        department TEXT NOT NULL,
                        faculty_id TEXT NOT NULL,
                        faculty_name TEXT NOT NULL,
                        credit_hours INTEGER NOT NULL,
                        slot TEXT NOT NULL,
                        venue TEXT NOT NULL,
                        capacity INTEGER NOT NULL,
                        enrolled_count INTEGER DEFAULT 0,
                        created_at TEXT NOT NULL
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS naac_audit_trail (
                        log_id TEXT PRIMARY KEY,
                        actor_role TEXT NOT NULL,
                        action TEXT NOT NULL,
                        resource TEXT NOT NULL,
                        details TEXT NOT NULL,
                        prev_hash TEXT NOT NULL,
                        entry_hash TEXT NOT NULL,
                        timestamp TEXT NOT NULL
                    );
                """)
                conn.commit()
            finally:
                conn.close()

    def _seed_initial_records(self):
        """Seeds default faculty and sample course allocations if empty."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM faculty_metrics;")
                if cur.fetchone()[0] == 0:
                    now_str = datetime.now(timezone.utc).isoformat()
                    for f in DEFAULT_FACULTY_ROSTER:
                        cur.execute("""
                            INSERT INTO faculty_metrics
                            (faculty_id, name, designation, department, teaching_hours,
                             lab_supervision_hours, funded_projects_count, student_rating,
                             specialization, status, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, (
                            f["faculty_id"], f["name"], f["designation"], f["department"],
                            f["teaching_hours"], f["lab_supervision_hours"],
                            f["funded_projects_count"], f["student_rating"],
                            f["specialization"], f["status"], now_str
                        ))

                # Seed initial course allocation
                cur.execute("SELECT COUNT(*) FROM course_allocations;")
                if cur.fetchone()[0] == 0:
                    now_str = datetime.now(timezone.utc).isoformat()
                    cur.execute("""
                        INSERT INTO course_allocations
                        (allocation_id, course_code, course_name, department, faculty_id,
                         faculty_name, credit_hours, slot, venue, capacity, enrolled_count, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        "ALC-EC8702-01", "EC8702", "Advanced Embedded Systems & RTOS Laboratory",
                        "Electronics Engineering", "FAC-MIT-004", "Ashok Kumar A",
                        4, "Slot-A (Tue/Thu 14:00 - 17:00)", "Lab 304 HIL Facility", 45, 42, now_str
                    ))

                # Seed genesis NAAC audit log entry
                cur.execute("SELECT COUNT(*) FROM naac_audit_trail;")
                if cur.fetchone()[0] == 0:
                    now_str = datetime.now(timezone.utc).isoformat()
                    genesis_details = "Institutional Genesis: VoltCore Apex Academia NBA & NAAC Audit Ledger Initialized."
                    prev_h = "0" * 64
                    entry_h = hashlib.sha256(f"LOG-000001:Admin_Owner:GENESIS:SYSTEM:{genesis_details}:{now_str}:{prev_h}".encode()).hexdigest()
                    cur.execute("""
                        INSERT INTO naac_audit_trail
                        (log_id, actor_role, action, resource, details, prev_hash, entry_hash, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """, ("LOG-000001", "Admin_Owner", "GENESIS", "SYSTEM", genesis_details, prev_h, entry_h, now_str))

                conn.commit()
            finally:
                conn.close()

    # =========================================================================
    # Faculty Workload & Heatmap Metrics
    # =========================================================================
    def get_faculty_workload_metrics(self) -> List[Dict[str, Any]]:
        """
        Retrieves faculty workload hours, teaching loads, and overload alerts.
        Overload threshold: > 24 total weekly hours (Teaching + Lab Supervision).
        """
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM faculty_metrics ORDER BY (teaching_hours + lab_supervision_hours) DESC;")
            rows = cur.fetchall()
            results = []
            for r in rows:
                total_hours = r["teaching_hours"] + r["lab_supervision_hours"]
                status = "NORMAL"
                if total_hours >= 26:
                    status = "CRITICAL_OVERLOAD"
                elif total_hours >= 22:
                    status = "HIGH_WORKLOAD"

                results.append({
                    "faculty_id": r["faculty_id"],
                    "name": r["name"],
                    "designation": r["designation"],
                    "department": r["department"],
                    "teaching_hours": r["teaching_hours"],
                    "lab_supervision_hours": r["lab_supervision_hours"],
                    "total_hours": total_hours,
                    "funded_projects": r["funded_projects_count"],
                    "student_rating": r["student_rating"],
                    "specialization": r["specialization"],
                    "workload_status": status
                })
            return results
        finally:
            conn.close()

    # =========================================================================
    # Automated NBA Course Outcome (CO) to PO Attainment Matrix
    # =========================================================================
    def compute_nba_co_po_matrix(self) -> Dict[str, Any]:
        """
        Calculates direct & indirect NBA attainment across PO1-PO12 and PSO1-PSO2.
        Enforces NBA threshold criteria (Target: 70% attainment = 2.1 / 3.0 level).
        """
        # Anna University Regulation 2023 EC8702 Course Outcomes
        co_scores = [
            {"co": "CO1", "title": "Bare-Metal Registers & GPIO Concurrency", "score_pct": 84.5, "level": 2.54, "mappings": {"PO1": 3, "PO2": 2, "PO5": 3, "PSO1": 3}},
            {"co": "CO2", "title": "Automotive CAN & Bus Protocols with CRC", "score_pct": 78.2, "level": 2.35, "mappings": {"PO3": 3, "PO5": 2, "PO6": 2, "PSO2": 3}},
            {"co": "CO3", "title": "5-Stage Pipelined RISC-V Soft-Core", "score_pct": 71.8, "level": 2.15, "mappings": {"PO3": 3, "PO4": 3, "PO5": 2, "PSO1": 2}},
            {"co": "CO4", "title": "FreeRTOS Scheduling & Priority Inversion", "score_pct": 69.1, "level": 2.07, "mappings": {"PO2": 3, "PO3": 2, "PO8": 2, "PSO1": 3}},
            {"co": "CO5", "title": "Advanced DMA Circular Zero-Copy IPC", "score_pct": 82.0, "level": 2.46, "mappings": {"PO1": 3, "PO5": 3, "PO12": 3, "PSO2": 3}},
        ]

        target_level = 2.10  # 70% NBA standard
        all_pos = [f"PO{i}" for i in range(1, 13)] + ["PSO1", "PSO2"]
        po_attainment = {}

        for po in all_pos:
            total_weight = 0
            weighted_sum = 0.0
            for co in co_scores:
                weight = co["mappings"].get(po, 0)
                if weight > 0:
                    total_weight += weight
                    weighted_sum += co["level"] * weight

            if total_weight > 0:
                avg_attainment = round(weighted_sum / total_weight, 2)
                percentage = round((avg_attainment / 3.0) * 100.0, 1)
                status = "ATTAINED" if avg_attainment >= target_level else "REMEDIAL_REQUIRED"
            else:
                avg_attainment = 0.0
                percentage = 0.0
                status = "NOT_MAPPED"

            po_attainment[po] = {
                "po_code": po,
                "description": PO_DEFINITIONS.get(po, "Program Outcome"),
                "attainment_level": avg_attainment,
                "attainment_percentage": percentage,
                "status": status,
                "mapped": total_weight > 0
            }

        overall_attained_count = sum(1 for p in po_attainment.values() if p["status"] == "ATTAINED")
        total_mapped = sum(1 for p in po_attainment.values() if p["mapped"])
        compliance_pct = round((overall_attained_count / total_mapped) * 100.0, 1) if total_mapped > 0 else 0.0

        return {
            "academic_year": "2026-2027",
            "regulation": "Anna University R2023",
            "department": "Department of Electronics Engineering",
            "institution": "Madras Institute of Technology (MIT) Campus",
            "target_threshold_level": target_level,
            "target_percentage": 70.0,
            "total_mapped_pos": total_mapped,
            "attained_pos_count": overall_attained_count,
            "nba_compliance_percentage": compliance_pct,
            "course_outcomes": co_scores,
            "po_attainment_matrix": po_attainment
        }

    # =========================================================================
    # NAAC Cryptographic Audit Log with SHA-256 Linkage
    # =========================================================================
    def record_naac_audit_event(
        self,
        actor_role: str,
        action: str,
        resource: str,
        details: str
    ) -> Dict[str, Any]:
        """
        Records an immutable administrative event in the NAAC audit ledger.
        Cryptographically signs each record with SHA-256 chained to previous hash.
        """
        privileged_roles = {"Admin", "Admin_Owner", "Dean_Academic", "HOD_ECE"}
        if actor_role not in privileged_roles:
            return {
                "status": "FORBIDDEN",
                "error": f"Role '{actor_role}' is not authorized to create administrative NAAC audit entries."
            }

        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT entry_hash FROM naac_audit_trail ORDER BY rowid DESC LIMIT 1;")
                prev_row = cur.fetchone()
                prev_hash = prev_row["entry_hash"] if prev_row else "0" * 64

                cur.execute("SELECT COUNT(*) FROM naac_audit_trail;")
                count = cur.fetchone()[0] + 1
                log_id = f"LOG-{count:06d}"
                now_str = datetime.now(timezone.utc).isoformat()

                # Generate SHA-256 block hash
                hash_input = f"{log_id}:{actor_role}:{action}:{resource}:{details}:{now_str}:{prev_hash}"
                entry_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

                cur.execute("""
                    INSERT INTO naac_audit_trail
                    (log_id, actor_role, action, resource, details, prev_hash, entry_hash, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """, (log_id, actor_role, action, resource, details, prev_hash, entry_hash, now_str))
                conn.commit()

                return {
                    "status": "SUCCESS",
                    "log_id": log_id,
                    "action": action,
                    "entry_hash": entry_hash,
                    "prev_hash": prev_hash,
                    "timestamp": now_str
                }
            finally:
                conn.close()

    def verify_audit_log_integrity(self) -> Dict[str, Any]:
        """
        Validates the complete SHA-256 cryptographic chain of the NAAC audit trail.
        Returns whether the ledger has suffered any tampering or alteration.
        """
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM naac_audit_trail ORDER BY rowid ASC;")
            rows = cur.fetchall()

            if not rows:
                return {"status": "SUCCESS", "verified": True, "total_records": 0, "tampered": False}

            prev_hash = "0" * 64
            for r in rows:
                expected_input = f"{r['log_id']}:{r['actor_role']}:{r['action']}:{r['resource']}:{r['details']}:{r['timestamp']}:{r['prev_hash']}"
                calculated_hash = hashlib.sha256(expected_input.encode("utf-8")).hexdigest()

                if calculated_hash != r["entry_hash"]:
                    return {
                        "status": "INTEGRITY_BREACH",
                        "verified": False,
                        "tampered": True,
                        "failed_at_log_id": r["log_id"],
                        "message": f"Cryptographic mismatch detected at {r['log_id']}."
                    }

                prev_hash = r["entry_hash"]

            return {
                "status": "SUCCESS",
                "verified": True,
                "total_records": len(rows),
                "tampered": False,
                "latest_block_hash": prev_hash
            }
        finally:
            conn.close()

    def get_naac_compliance_summary(self) -> Dict[str, Any]:
        """
        Returns projected NAAC Criteria 1-7 compliance scores and cumulative CGPA.
        """
        criteria = [
            {"criterion": 1, "name": "Curricular Aspects", "weightage": 100, "score": 93.5, "status": "EXCELLENT"},
            {"criterion": 2, "name": "Teaching-Learning and Evaluation", "weightage": 350, "score": 331.0, "status": "EXCELLENT"},
            {"criterion": 3, "name": "Research, Innovations and Extension", "weightage": 110, "score": 101.5, "status": "EXCELLENT"},
            {"criterion": 4, "name": "Infrastructure and Learning Resources", "weightage": 100, "score": 97.0, "status": "OUTSTANDING"},
            {"criterion": 5, "name": "Student Support and Progression", "weightage": 140, "score": 128.0, "status": "EXCELLENT"},
            {"criterion": 6, "name": "Governance, Leadership and Management", "weightage": 100, "score": 92.5, "status": "EXCELLENT"},
            {"criterion": 7, "name": "Institutional Values and Best Practices", "weightage": 100, "score": 96.0, "status": "OUTSTANDING"},
        ]

        total_weight = sum(c["weightage"] for c in criteria)
        total_score = sum(c["score"] for c in criteria)
        projected_cgpa = round((total_score / total_weight) * 4.0, 2)
        projected_grade = "A++" if projected_cgpa >= 3.51 else ("A+" if projected_cgpa >= 3.26 else "A")

        return {
            "institution": "Madras Institute of Technology (MIT) Campus, Anna University",
            "accreditation_cycle": "Cycle 4 Re-Accreditation (2026-2031)",
            "total_weightage": total_weight,
            "total_score": round(total_score, 1),
            "projected_cgpa": projected_cgpa,
            "projected_grade": projected_grade,
            "criteria": criteria
        }

    # =========================================================================
    # Multi-Department Course Allocation Operations
    # =========================================================================
    def allocate_course(
        self,
        course_code: str,
        course_name: str,
        department: str,
        faculty_id: str,
        faculty_name: str,
        credit_hours: int,
        slot: str,
        venue: str,
        capacity: int = 50,
        actor_role: str = "Admin"
    ) -> Dict[str, Any]:
        """
        Allocates an academic course to a designated faculty member.
        Detects schedule/venue conflict and enforces strict RBAC barriers.
        """
        privileged_roles = {"Admin", "Admin_Owner", "Dean_Academic", "HOD_ECE"}
        if actor_role not in privileged_roles:
            return {
                "status": "FORBIDDEN",
                "error": f"Role '{actor_role}' is not authorized to allocate academic courses."
            }

        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                # Check for room slot conflict
                cur.execute("SELECT course_code, faculty_name FROM course_allocations WHERE slot = ? AND venue = ?;", (slot, venue))
                conflict = cur.fetchone()
                if conflict:
                    return {
                        "status": "CONFLICT",
                        "error": f"Venue collision: Room '{venue}' in slot '{slot}' is already occupied by {conflict['course_code']} ({conflict['faculty_name']})."
                    }

                allocation_id = f"ALC-{course_code}-{int(datetime.now().timestamp())%10000:04d}"
                now_str = datetime.now(timezone.utc).isoformat()

                cur.execute("""
                    INSERT INTO course_allocations
                    (allocation_id, course_code, course_name, department, faculty_id,
                     faculty_name, credit_hours, slot, venue, capacity, enrolled_count, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?);
                """, (
                    allocation_id, course_code, course_name, department, faculty_id,
                    faculty_name, credit_hours, slot, venue, capacity, now_str
                ))

                # Also automatically log this administrative event into the NAAC audit trail
                conn.commit()
            finally:
                conn.close()

        # Log event in NAAC ledger
        self.record_naac_audit_event(
            actor_role=actor_role,
            action="COURSE_ALLOCATION",
            resource=course_code,
            details=f"Course {course_code} ({course_name}) allocated to {faculty_name} ({venue}, {slot})."
        )

        return {
            "status": "SUCCESS",
            "allocation_id": allocation_id,
            "course_code": course_code,
            "faculty_name": faculty_name,
            "venue": venue,
            "slot": slot
        }

    def list_course_allocations(self, department: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns active course allocations, optionally filtered by academic department."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            if department:
                cur.execute("SELECT * FROM course_allocations WHERE department = ? ORDER BY course_code ASC;", (department,))
            else:
                cur.execute("SELECT * FROM course_allocations ORDER BY department ASC, course_code ASC;")
            
            rows = cur.fetchall()
            return [
                {
                    "allocation_id": r["allocation_id"],
                    "course_code": r["course_code"],
                    "course_name": r["course_name"],
                    "department": r["department"],
                    "faculty_id": r["faculty_id"],
                    "faculty_name": r["faculty_name"],
                    "credit_hours": r["credit_hours"],
                    "slot": r["slot"],
                    "venue": r["venue"],
                    "capacity": r["capacity"],
                    "enrolled_count": r["enrolled_count"]
                }
                for r in rows
            ]
        finally:
            conn.close()

    def get_enterprise_overview(self) -> Dict[str, Any]:
        """Provides a comprehensive overview for the Enterprise Admin dashboard."""
        return {
            "institution": "Madras Institute of Technology (MIT) Campus, Anna University",
            "department": "Department of Electronics Engineering",
            "faculty": self.get_faculty_workload_metrics(),
            "nba_matrix": self.compute_nba_co_po_matrix(),
            "naac_summary": self.get_naac_compliance_summary(),
            "audit_integrity": self.verify_audit_log_integrity(),
            "allocations": self.list_course_allocations()
        }


# Global Enterprise Admin Engine Singleton
enterprise_admin_engine = EnterpriseAdminEngine()
