"""
========================================================================================
VoltCore Apex Academia - Intelligent Academic Management Engine (Phase 19)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/academic_management_engine.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Lightweight backend manager handling:
    1. Smart Academic Calendar (university schedules, IA-1/IA-2 tests, lab practicals).
    2. Syllabus Completion Tracker at subject, unit, and topic levels (Regulation 2023).
    3. Prerequisite validation engine preventing out-of-order course progression.
    4. SQLite WAL-backed performance and attainment ledgers with RBAC protection.
========================================================================================
"""

import os
import time
import json
import sqlite3
import threading
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, date

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")

# Default Anna University MIT Campus ECE Regulation 2023 Curricular Roster
DEFAULT_SUBJECTS = [
    {
        "subject_code": "EC3352",
        "subject_name": "Digital Systems Design",
        "semester": 3,
        "credits": 3,
        "total_hours": 45,
        "faculty_in_charge": "Dr. M. Kannan",
        "department": "Electronics Engineering"
    },
    {
        "subject_code": "EC3452",
        "subject_name": "Electromagnetic Fields",
        "semester": 4,
        "credits": 4,
        "total_hours": 60,
        "faculty_in_charge": "Dr. P. Nirmal Kumar",
        "department": "Electronics Engineering"
    },
    {
        "subject_code": "EC3451",
        "subject_name": "Linear Integrated Circuits",
        "semester": 4,
        "credits": 3,
        "total_hours": 45,
        "faculty_in_charge": "Dr. V. Sathiesh Kumar",
        "department": "Electronics Engineering"
    },
    {
        "subject_code": "EC3491",
        "subject_name": "Communication Systems",
        "semester": 4,
        "credits": 3,
        "total_hours": 45,
        "faculty_in_charge": "Dr. S. Dhanasekaran",
        "department": "Electronics Engineering"
    }
]

# Structured Syllabus Units & Topics
DEFAULT_SYLLABUS_HIERARCHY = [
    # --- EC3352: Digital Systems Design ---
    {
        "subject_code": "EC3352",
        "unit_id": "EC3352_U1",
        "unit_number": 1,
        "unit_title": "Combinational Logic Circuit Synthesis",
        "target_hours": 9,
        "topics": [
            {"topic_id": "EC3352_T1_1", "topic_name": "Karnaugh Maps & Quine-McCluskey Optimization", "prereq": None, "status": "COMPLETED", "hours": 3.0},
            {"topic_id": "EC3352_T1_2", "topic_name": "Carry-Lookahead Adders & Fast ALU Topologies", "prereq": "EC3352_T1_1", "status": "COMPLETED", "hours": 3.0},
            {"topic_id": "EC3352_T1_3", "topic_name": "Magnitude Comparators and Decoders", "prereq": "EC3352_T1_2", "status": "COMPLETED", "hours": 3.0}
        ]
    },
    {
        "subject_code": "EC3352",
        "unit_id": "EC3352_U2",
        "unit_number": 2,
        "unit_title": "Synchronous Sequential Logic & FSM",
        "target_hours": 9,
        "topics": [
            {"topic_id": "EC3352_T2_1", "topic_name": "Flip-Flop Metatables & Setup/Hold Time Invariants", "prereq": "EC3352_T1_2", "status": "COMPLETED", "hours": 3.0},
            {"topic_id": "EC3352_T2_2", "topic_name": "Mealy & Moore State Machine Reduction", "prereq": "EC3352_T2_1", "status": "COMPLETED", "hours": 3.0},
            {"topic_id": "EC3352_T2_3", "topic_name": "Asynchronous & Synchronous Counter Verification", "prereq": "EC3352_T2_2", "status": "IN_PROGRESS", "hours": 2.0}
        ]
    },
    {
        "subject_code": "EC3352",
        "unit_id": "EC3352_U3",
        "unit_number": 3,
        "unit_title": "Asynchronous Sequential Networks & Hazards",
        "target_hours": 9,
        "topics": [
            {"topic_id": "EC3352_T3_1", "topic_name": "Primitive Flow Tables & State Assignment", "prereq": "EC3352_T2_2", "status": "PENDING", "hours": 0.0},
            {"topic_id": "EC3352_T3_2", "topic_name": "Critical & Non-Critical Race Elimination", "prereq": "EC3352_T3_1", "status": "PENDING", "hours": 0.0},
            {"topic_id": "EC3352_T3_3", "topic_name": "Static and Dynamic Hazards in Combinational Paths", "prereq": "EC3352_T3_2", "status": "PENDING", "hours": 0.0}
        ]
    },

    # --- EC3452: Electromagnetic Fields ---
    {
        "subject_code": "EC3452",
        "unit_id": "EC3452_U1",
        "unit_number": 1,
        "unit_title": "Static Electric Fields & Gauss Law",
        "target_hours": 12,
        "topics": [
            {"topic_id": "EC3452_T1_1", "topic_name": "Coulomb's Law, Divergence Theorem & Electric Flux", "prereq": None, "status": "COMPLETED", "hours": 4.0},
            {"topic_id": "EC3452_T1_2", "topic_name": "Poisson and Laplace Differential Equations", "prereq": "EC3452_T1_1", "status": "COMPLETED", "hours": 4.0},
            {"topic_id": "EC3452_T1_3", "topic_name": "Capacitance Calculation for Parallel Plates and Coaxial Cables", "prereq": "EC3452_T1_2", "status": "COMPLETED", "hours": 4.0}
        ]
    },
    {
        "subject_code": "EC3452",
        "unit_id": "EC3452_U2",
        "unit_number": 2,
        "unit_title": "Static Magnetic Fields & Vector Potential",
        "target_hours": 12,
        "topics": [
            {"topic_id": "EC3452_T2_1", "topic_name": "Biot-Savart Law and Ampere's Circuital Law", "prereq": "EC3452_T1_1", "status": "COMPLETED", "hours": 4.0},
            {"topic_id": "EC3452_T2_2", "topic_name": "Magnetic Vector Potential & Curl of H", "prereq": "EC3452_T2_1", "status": "IN_PROGRESS", "hours": 3.0},
            {"topic_id": "EC3452_T2_3", "topic_name": "Self and Mutual Inductance in Solenoids and Toroids", "prereq": "EC3452_T2_2", "status": "PENDING", "hours": 0.0}
        ]
    },
    {
        "subject_code": "EC3452",
        "unit_id": "EC3452_U4",
        "unit_number": 4,
        "unit_title": "Time-Varying Fields & Maxwell's Equations",
        "target_hours": 12,
        "topics": [
            {"topic_id": "EC3452_T4_1", "topic_name": "Faraday's Law of Induction & Transformer EMF", "prereq": "EC3452_T2_2", "status": "PENDING", "hours": 0.0},
            {"topic_id": "EC3452_T4_2", "topic_name": "Maxwell's Equations in Differential & Integral Forms", "prereq": "EC3452_T4_1", "status": "PENDING", "hours": 0.0},
            {"topic_id": "EC3452_T4_3", "topic_name": "Poynting Vector & Electromagnetic Power Flow", "prereq": "EC3452_T4_2", "status": "PENDING", "hours": 0.0}
        ]
    },

    # --- EC3451: Linear Integrated Circuits ---
    {
        "subject_code": "EC3451",
        "unit_id": "EC3451_U1",
        "unit_number": 1,
        "unit_title": "Op-Amp Internal Architectures & DC Characteristics",
        "target_hours": 9,
        "topics": [
            {"topic_id": "EC3451_T1_1", "topic_name": "Differential Pair Stage, CMRR, & Active Current Mirror", "prereq": None, "status": "COMPLETED", "hours": 3.0},
            {"topic_id": "EC3451_T1_2", "topic_name": "Input Offset Voltage, Slew Rate, and Frequency Compensation", "prereq": "EC3451_T1_1", "status": "COMPLETED", "hours": 3.0},
            {"topic_id": "EC3451_T1_3", "topic_name": "Inverting and Non-Inverting Closed-Loop Analysis", "prereq": "EC3451_T1_2", "status": "COMPLETED", "hours": 3.0}
        ]
    },
    {
        "subject_code": "EC3451",
        "unit_id": "EC3451_U2",
        "unit_number": 2,
        "unit_title": "Active Filters & Non-Linear Signal Processing",
        "target_hours": 9,
        "topics": [
            {"topic_id": "EC3451_T2_1", "topic_name": "Sallen-Key Active Low-Pass & High-Pass Filter Design", "prereq": "EC3451_T1_3", "status": "COMPLETED", "hours": 3.0},
            {"topic_id": "EC3451_T2_2", "topic_name": "Precision Rectifiers, Peak Detectors & Schmitt Triggers", "prereq": "EC3451_T2_1", "status": "IN_PROGRESS", "hours": 2.5},
            {"topic_id": "EC3451_T2_3", "topic_name": "IC 555 Astable and Monostable Multivibrators", "prereq": "EC3451_T2_2", "status": "PENDING", "hours": 0.0}
        ]
    },

    # --- EC3491: Communication Systems ---
    {
        "subject_code": "EC3491",
        "unit_id": "EC3491_U1",
        "unit_number": 1,
        "unit_title": "Continuous Wave Modulation (AM & FM)",
        "target_hours": 9,
        "topics": [
            {"topic_id": "EC3491_T1_1", "topic_name": "DSB-FC, DSB-SC, and SSB-SC Spectral Efficiency", "prereq": None, "status": "COMPLETED", "hours": 3.0},
            {"topic_id": "EC3491_T1_2", "topic_name": "Wideband Frequency Modulation & Carson's Rule", "prereq": "EC3491_T1_1", "status": "COMPLETED", "hours": 3.0},
            {"topic_id": "EC3491_T1_3", "topic_name": "Superheterodyne Receiver Intermediate Frequency Selection", "prereq": "EC3491_T1_2", "status": "COMPLETED", "hours": 3.0}
        ]
    },
    {
        "subject_code": "EC3491",
        "unit_id": "EC3491_U3",
        "unit_number": 3,
        "unit_title": "Baseband Digital Transmission & ISI",
        "target_hours": 9,
        "topics": [
            {"topic_id": "EC3491_T3_1", "topic_name": "Sampling Theorem & Pulse Code Modulation (PCM)", "prereq": "EC3491_T1_3", "status": "COMPLETED", "hours": 3.0},
            {"topic_id": "EC3491_T3_2", "topic_name": "Nyquist Criterion for Zero Inter-Symbol Interference", "prereq": "EC3491_T3_1", "status": "IN_PROGRESS", "hours": 2.0},
            {"topic_id": "EC3491_T3_3", "topic_name": "Matched Filter Receiver & Probability of Error", "prereq": "EC3491_T3_2", "status": "PENDING", "hours": 0.0}
        ]
    }
]

# Smart Academic Calendar Events
DEFAULT_CALENDAR_EVENTS = [
    {
        "event_id": "EVT_IA1_2026",
        "title": "Continuous Assessment Test 1 (IA-1)",
        "event_type": "EXAM",
        "start_date": "2026-11-12",
        "end_date": "2026-11-16",
        "venue": "MIT Campus Examination Hall 2",
        "target_regulation": "ECE Regulation 2023 (Semester 4)",
        "description": "Continuous Assessment covering Units 1 & 2 for all core electronics engineering subjects."
    },
    {
        "event_id": "EVT_LAB_HIL_304",
        "title": "Hardware HIL & Microcontroller Lab Practical Bench",
        "event_type": "LAB",
        "start_date": "2026-11-18",
        "end_date": "2026-11-18",
        "venue": "Lab 304 Embedded Systems Lab",
        "target_regulation": "ECE Regulation 2023 (Semester 4)",
        "description": "Hands-on bench assessment for ESP32-S3 and STM32 DMA communication with DSO."
    },
    {
        "event_id": "EVT_NPTEL_EXAM",
        "title": "NPTEL Proctored Certification Exam (TinyML & RTOS)",
        "event_type": "MILESTONE",
        "start_date": "2026-12-05",
        "end_date": "2026-12-05",
        "venue": "IIT Madras Online Testing Node",
        "target_regulation": "ECE Open Elective",
        "description": "Nationwide MOOC credit transfer exam for Embedded RTOS and TinyML Edge AI."
    },
    {
        "event_id": "EVT_IA2_2026",
        "title": "Continuous Assessment Test 2 (IA-2)",
        "event_type": "EXAM",
        "start_date": "2026-12-10",
        "end_date": "2026-12-14",
        "venue": "MIT Campus Examination Hall 2",
        "target_regulation": "ECE Regulation 2023 (Semester 4)",
        "description": "Continuous Assessment covering Units 3 & 4 with NBA CO-PO mapping analytics."
    },
    {
        "event_id": "EVT_MODEL_PRAC_2026",
        "title": "Model Practical Examination (Analog & Digital VLSI Lab)",
        "event_type": "LAB",
        "start_date": "2026-12-20",
        "end_date": "2026-12-22",
        "venue": "Electronics Dept Labs 301-304",
        "target_regulation": "ECE Regulation 2023 (Semester 4)",
        "description": "Full-day mock university practical exam with physical oscilloscope rubrics."
    },
    {
        "event_id": "EVT_MINI_PROJECT_REV",
        "title": "Capstone Mini-Project Phase 1 Evaluation Review",
        "event_type": "MILESTONE",
        "start_date": "2026-12-28",
        "end_date": "2026-12-28",
        "venue": "Department Seminar Hall, MIT Campus",
        "target_regulation": "ECE Regulation 2023 (Semester 4)",
        "description": "Faculty jury evaluation of hardware prototype, Git repository, and bill of materials."
    },
    {
        "event_id": "EVT_AU_THEORY_SEM4",
        "title": "Anna University End-Semester Theory Examinations",
        "event_type": "EXAM",
        "start_date": "2027-01-08",
        "end_date": "2027-01-24",
        "venue": "Centrally Designated Exam Centers",
        "target_regulation": "ECE Regulation 2023 (Semester 4)",
        "description": "Final university degree examinations under Controller of Examinations, Anna University."
    }
]


class AcademicManagementEngine:
    """
    Lightweight, thread-safe academic management engine handling university schedules,
    syllabus completion tracking, and prerequisite verification with SQLite WAL storage.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self._lock = threading.Lock()
        self._init_sqlite_schema()
        self._seed_default_academic_data()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns an optimized SQLite WAL connection."""
        conn = sqlite3.connect(self.db_path, timeout=5.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode = WAL;")
        cur.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_sqlite_schema(self) -> None:
        """Initializes tables for academic calendar, subjects, units, topics, and student progress."""
        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()
            try:
                # 1. Academic Calendar Events
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS academic_calendar_events (
                        event_id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        start_date TEXT NOT NULL,
                        end_date TEXT NOT NULL,
                        venue TEXT NOT NULL,
                        target_regulation TEXT NOT NULL,
                        description TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)

                # 2. Syllabus Subjects
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS academic_syllabus_subjects (
                        subject_code TEXT PRIMARY KEY,
                        subject_name TEXT NOT NULL,
                        semester INTEGER NOT NULL,
                        credits INTEGER NOT NULL,
                        total_hours INTEGER NOT NULL,
                        faculty_in_charge TEXT NOT NULL,
                        department TEXT NOT NULL
                    );
                """)

                # 3. Syllabus Units
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS academic_syllabus_units (
                        unit_id TEXT PRIMARY KEY,
                        subject_code TEXT NOT NULL,
                        unit_number INTEGER NOT NULL,
                        unit_title TEXT NOT NULL,
                        target_hours INTEGER NOT NULL,
                        FOREIGN KEY (subject_code) REFERENCES academic_syllabus_subjects(subject_code)
                    );
                """)

                # 4. Syllabus Topics with Prerequisite Links
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS academic_syllabus_topics (
                        topic_id TEXT PRIMARY KEY,
                        unit_id TEXT NOT NULL,
                        subject_code TEXT NOT NULL,
                        topic_name TEXT NOT NULL,
                        prerequisite_topic_id TEXT,
                        status TEXT NOT NULL,
                        hours_spent REAL NOT NULL,
                        completed_at TEXT,
                        FOREIGN KEY (unit_id) REFERENCES academic_syllabus_units(unit_id)
                    );
                """)

                # 5. Student Subject Progress & Attainment Cache
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS academic_student_progress (
                        progress_id TEXT PRIMARY KEY,
                        student_id TEXT NOT NULL,
                        subject_code TEXT NOT NULL,
                        completion_percentage REAL NOT NULL,
                        co_attainment_score REAL NOT NULL,
                        last_updated TEXT NOT NULL,
                        UNIQUE(student_id, subject_code)
                    );
                """)
                conn.commit()
            finally:
                conn.close()

    def _seed_default_academic_data(self) -> None:
        """Seeds initial Anna University ECE curriculum and academic calendar events if empty."""
        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()
            try:
                # Seed calendar events
                cur.execute("SELECT COUNT(*) FROM academic_calendar_events;")
                if cur.fetchone()[0] == 0:
                    for ev in DEFAULT_CALENDAR_EVENTS:
                        cur.execute("""
                            INSERT INTO academic_calendar_events
                            (event_id, title, event_type, start_date, end_date, venue, target_regulation, description, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, (
                            ev["event_id"], ev["title"], ev["event_type"],
                            ev["start_date"], ev["end_date"], ev["venue"],
                            ev["target_regulation"], ev["description"],
                            datetime.now(timezone.utc).isoformat()
                        ))

                # Seed subjects
                cur.execute("SELECT COUNT(*) FROM academic_syllabus_subjects;")
                if cur.fetchone()[0] == 0:
                    for sub in DEFAULT_SUBJECTS:
                        cur.execute("""
                            INSERT INTO academic_syllabus_subjects
                            (subject_code, subject_name, semester, credits, total_hours, faculty_in_charge, department)
                            VALUES (?, ?, ?, ?, ?, ?, ?);
                        """, (
                            sub["subject_code"], sub["subject_name"], sub["semester"],
                            sub["credits"], sub["total_hours"], sub["faculty_in_charge"],
                            sub["department"]
                        ))

                # Seed units and topics
                cur.execute("SELECT COUNT(*) FROM academic_syllabus_units;")
                if cur.fetchone()[0] == 0:
                    for unit in DEFAULT_SYLLABUS_HIERARCHY:
                        cur.execute("""
                            INSERT INTO academic_syllabus_units
                            (unit_id, subject_code, unit_number, unit_title, target_hours)
                            VALUES (?, ?, ?, ?, ?);
                        """, (
                            unit["unit_id"], unit["subject_code"], unit["unit_number"],
                            unit["unit_title"], unit["target_hours"]
                        ))

                        for top in unit["topics"]:
                            cur.execute("""
                                INSERT INTO academic_syllabus_topics
                                (topic_id, unit_id, subject_code, topic_name, prerequisite_topic_id, status, hours_spent, completed_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                            """, (
                                top["topic_id"], unit["unit_id"], unit["subject_code"],
                                top["topic_name"], top["prereq"], top["status"],
                                top["hours"], datetime.now(timezone.utc).isoformat() if top["status"] == "COMPLETED" else None
                            ))
                conn.commit()
            finally:
                conn.close()

    def get_calendar_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieves academic calendar events with optional filtering and countdown calculation."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            if event_type and event_type.upper() != "ALL":
                cur.execute("""
                    SELECT * FROM academic_calendar_events
                    WHERE UPPER(event_type) = UPPER(?)
                    ORDER BY start_date ASC LIMIT ?;
                """, (event_type, limit))
            else:
                cur.execute("""
                    SELECT * FROM academic_calendar_events
                    ORDER BY start_date ASC LIMIT ?;
                """, (limit,))

            rows = cur.fetchall()
            today_str = date.today().isoformat()
            results = []
            for r in rows:
                item = dict(r)
                # Compute days remaining
                try:
                    ev_date = datetime.strptime(item["start_date"], "%Y-%m-%d").date()
                    delta = (ev_date - date.today()).days
                    item["days_remaining"] = delta
                    item["is_past"] = delta < 0
                    item["is_today"] = delta == 0
                except Exception:
                    item["days_remaining"] = 0
                    item["is_past"] = False
                    item["is_today"] = False
                results.append(item)
            return results
        finally:
            conn.close()

    def add_calendar_event(
        self,
        title: str,
        event_type: str,
        start_date: str,
        end_date: str,
        venue: str,
        description: str,
        target_regulation: str = "ECE Regulation 2023",
        actor_role: str = "Faculty"
    ) -> Dict[str, Any]:
        """Adds a calendar event with strict RBAC enforcement (Faculty/Admin only)."""
        if actor_role not in ("Faculty", "Admin", "Chairperson"):
            return {
                "status": "FORBIDDEN",
                "message": f"Role '{actor_role}' lacks permission to add academic calendar events. Required: Faculty or Admin."
            }

        event_id = f"EVT_{int(time.time() * 1000)}"
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO academic_calendar_events
                    (event_id, title, event_type, start_date, end_date, venue, target_regulation, description, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    event_id, title, event_type.upper(), start_date, end_date,
                    venue, target_regulation, description, datetime.now(timezone.utc).isoformat()
                ))
                conn.commit()
                return {
                    "status": "SUCCESS",
                    "event_id": event_id,
                    "title": title,
                    "message": "Academic calendar milestone successfully scheduled."
                }
            finally:
                conn.close()

    def get_syllabus_overview(self, student_id: str = "2023MITEC042") -> Dict[str, Any]:
        """Provides an aggregated overview of semester syllabus progression and subject health."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM academic_syllabus_subjects ORDER BY semester, subject_code;")
            subjects = [dict(r) for r in cur.fetchall()]

            total_topics_all = 0
            completed_topics_all = 0
            total_credits = 0
            subject_progress_list = []

            for sub in subjects:
                code = sub["subject_code"]
                total_credits += sub["credits"]

                cur.execute("""
                    SELECT COUNT(*),
                           SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END),
                           SUM(CASE WHEN status = 'IN_PROGRESS' THEN 1 ELSE 0 END),
                           SUM(hours_spent)
                    FROM academic_syllabus_topics
                    WHERE subject_code = ?;
                """, (code,))
                t_count, c_count, ip_count, hrs = cur.fetchone()
                t_count = t_count or 0
                c_count = c_count or 0
                ip_count = ip_count or 0
                hrs = round(hrs or 0.0, 1)

                total_topics_all += t_count
                completed_topics_all += c_count

                pct = round((c_count / t_count * 100.0), 1) if t_count > 0 else 0.0
                co_score = round(min(3.0, (pct / 100.0) * 3.0), 2)

                subject_progress_list.append({
                    "subject_code": code,
                    "subject_name": sub["subject_name"],
                    "faculty": sub["faculty_in_charge"],
                    "credits": sub["credits"],
                    "total_topics": t_count,
                    "completed_topics": c_count,
                    "in_progress_topics": ip_count,
                    "hours_logged": hrs,
                    "target_hours": sub["total_hours"],
                    "completion_percentage": pct,
                    "co_attainment_score": co_score
                })

            overall_pct = round((completed_topics_all / total_topics_all * 100.0), 1) if total_topics_all > 0 else 0.0

            # Count upcoming exams and deadlines
            cur.execute("""
                SELECT COUNT(*) FROM academic_calendar_events
                WHERE event_type IN ('EXAM', 'LAB', 'MILESTONE')
                  AND start_date >= date('now');
            """)
            upcoming_deadlines = cur.fetchone()[0]

            return {
                "status": "OPERATIONAL",
                "campus": "Madras Institute of Technology (MIT) Campus, Anna University",
                "department": "Department of Electronics Engineering",
                "regulation": "ECE Regulation 2023",
                "student_id": student_id,
                "overall_completion_percentage": overall_pct,
                "total_credits_tracked": total_credits,
                "total_subjects": len(subjects),
                "total_topics": total_topics_all,
                "completed_topics": completed_topics_all,
                "upcoming_deadlines_count": upcoming_deadlines,
                "subject_progress": subject_progress_list
            }
        finally:
            conn.close()

    def get_subject_details(self, subject_code: str) -> Optional[Dict[str, Any]]:
        """Returns subject hierarchy including nested units and topics with prerequisite metadata."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM academic_syllabus_subjects WHERE subject_code = ?;", (subject_code,))
            sub_row = cur.fetchone()
            if not sub_row:
                return None

            subject_info = dict(sub_row)

            cur.execute("""
                SELECT * FROM academic_syllabus_units
                WHERE subject_code = ?
                ORDER BY unit_number ASC;
            """, (subject_code,))
            units = [dict(u) for u in cur.fetchall()]

            for u in units:
                cur.execute("""
                    SELECT * FROM academic_syllabus_topics
                    WHERE unit_id = ?
                    ORDER BY topic_id ASC;
                """, (u["unit_id"],))
                topics = [dict(t) for t in cur.fetchall()]

                # Calculate unit completion
                completed_count = sum(1 for t in topics if t["status"] == "COMPLETED")
                u["topics"] = topics
                u["total_topics"] = len(topics)
                u["completed_topics"] = completed_count
                u["unit_completion_pct"] = round((completed_count / len(topics) * 100.0), 1) if topics else 0.0

            subject_info["units"] = units
            return subject_info
        finally:
            conn.close()

    def check_prerequisites(self, topic_id: str) -> Dict[str, Any]:
        """
        Validates if topic prerequisite constraints are satisfied:
        Returns status 'SATISFIED', 'BLOCKED', or 'NONE'.
        """
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM academic_syllabus_topics WHERE topic_id = ?;", (topic_id,))
            row = cur.fetchone()
            if not row:
                return {"status": "ERROR", "message": "Topic not found"}

            topic = dict(row)
            prereq_id = topic.get("prerequisite_topic_id")

            if not prereq_id:
                return {
                    "topic_id": topic_id,
                    "topic_name": topic["topic_name"],
                    "status": "NONE",
                    "satisfied": True,
                    "prerequisite": None,
                    "message": "No prerequisites required. Ready for study."
                }

            cur.execute("SELECT * FROM academic_syllabus_topics WHERE topic_id = ?;", (prereq_id,))
            prereq_row = cur.fetchone()
            if not prereq_row:
                return {
                    "topic_id": topic_id,
                    "topic_name": topic["topic_name"],
                    "status": "NONE",
                    "satisfied": True,
                    "prerequisite": None
                }

            prereq = dict(prereq_row)
            is_satisfied = prereq["status"] == "COMPLETED"

            return {
                "topic_id": topic_id,
                "topic_name": topic["topic_name"],
                "status": "SATISFIED" if is_satisfied else "BLOCKED",
                "satisfied": is_satisfied,
                "prerequisite": {
                    "topic_id": prereq["topic_id"],
                    "topic_name": prereq["topic_name"],
                    "status": prereq["status"]
                },
                "message": "Prerequisite satisfied." if is_satisfied else f"Blocked by prerequisite: '{prereq['topic_name']}' must be COMPLETED first."
            }
        finally:
            conn.close()

    def update_topic_status(
        self,
        topic_id: str,
        new_status: str,
        hours_spent: Optional[float] = None,
        student_id: str = "2023MITEC042",
        actor_role: str = "Student"
    ) -> Dict[str, Any]:
        """
        Updates topic study/completion status with prerequisite enforcement:
        - Validates that prerequisites are completed before allowing status = 'COMPLETED'.
        - Updates hours logged and timestamp.
        - Refreshes student subject progress in SQLite WAL.
        """
        valid_statuses = ("COMPLETED", "IN_PROGRESS", "PENDING")
        new_status = new_status.upper()
        if new_status not in valid_statuses:
            return {"status": "ERROR", "message": f"Invalid status. Must be one of: {valid_statuses}"}

        # Check prerequisite rule if marking complete
        if new_status == "COMPLETED":
            prereq_check = self.check_prerequisites(topic_id)
            if not prereq_check.get("satisfied", True):
                return {
                    "status": "PREREQUISITE_BLOCKED",
                    "message": prereq_check["message"],
                    "prerequisite": prereq_check.get("prerequisite")
                }

        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM academic_syllabus_topics WHERE topic_id = ?;", (topic_id,))
                topic_row = cur.fetchone()
                if not topic_row:
                    return {"status": "ERROR", "message": f"Topic '{topic_id}' not found."}

                topic = dict(topic_row)
                sub_code = topic["subject_code"]
                current_hours = topic["hours_spent"]
                updated_hours = hours_spent if hours_spent is not None else current_hours

                comp_date = datetime.now(timezone.utc).isoformat() if new_status == "COMPLETED" else None

                cur.execute("""
                    UPDATE academic_syllabus_topics
                    SET status = ?, hours_spent = ?, completed_at = ?
                    WHERE topic_id = ?;
                """, (new_status, updated_hours, comp_date, topic_id))

                # Recalculate subject progress for student
                cur.execute("""
                    SELECT COUNT(*),
                           SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END)
                    FROM academic_syllabus_topics
                    WHERE subject_code = ?;
                """, (sub_code,))
                total_t, comp_t = cur.fetchone()
                pct = round((comp_t / total_t * 100.0), 1) if total_t > 0 else 0.0
                co_score = round(min(3.0, (pct / 100.0) * 3.0), 2)

                prog_id = f"PROG_{student_id}_{sub_code}"
                cur.execute("""
                    INSERT INTO academic_student_progress
                    (progress_id, student_id, subject_code, completion_percentage, co_attainment_score, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(student_id, subject_code) DO UPDATE SET
                        completion_percentage = excluded.completion_percentage,
                        co_attainment_score = excluded.co_attainment_score,
                        last_updated = excluded.last_updated;
                """, (prog_id, student_id, sub_code, pct, co_score, datetime.now(timezone.utc).isoformat()))

                conn.commit()

                return {
                    "status": "SUCCESS",
                    "topic_id": topic_id,
                    "new_status": new_status,
                    "hours_spent": updated_hours,
                    "subject_code": sub_code,
                    "subject_completion_percentage": pct,
                    "co_attainment_score": co_score,
                    "message": f"Topic '{topic['topic_name']}' updated to {new_status}."
                }
            finally:
                conn.close()


# Global Singleton
academic_management_engine = AcademicManagementEngine()
