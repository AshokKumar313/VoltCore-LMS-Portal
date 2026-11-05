"""
========================================================================================
VoltCore Apex Academia - Faculty & Department Productivity Workspace (Phase 25)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/faculty_productivity_engine.py
Course Scope: EC3451 (LIC), EC3491 (CS), EC3352 (DSD), EC3601 (Embedded), EC3711 (Mini-Proj)
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Lightweight backend manager handling:
    1. Syllabus Unit-Wise Lecture Planning Workspaces (Units I - V, CO Mapping, Bloom's Taxonomy).
    2. Faculty Lesson Template Library (Lecture, Lab Practical, Flipped Classroom).
    3. Digital Assignment Distribution with Weighted Continuous Assessment Rubrics.
    4. Student Submission Feedback Center with Qualitative & Metric Scoring.
    5. Department of Electronics Engineering Meeting Minutes (MoM) & Action Item Tracker.
    6. SQLite WAL-backed persistence with sub-3ms query latency & passive thermal profile.
========================================================================================
"""

import os
import time
import json
import sqlite3
import threading
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")

# Default demo identifiers
DEFAULT_FACULTY_ID = "FAC_MIT_ECE_001"
DEFAULT_FACULTY_NAME = "Dr. P. Nirmal Kumar (Professor & Head, Dept of Electronics)"
DEFAULT_STUDENT_ID = "2023MITEC042"

# Curated Faculty Lesson Templates (Anna University Regulation 2023 Aligned)
FACULTY_TEMPLATES_CATALOG = [
    {
        "template_id": "TPL_THEORY_ACTIVE_FILTERS",
        "course_code": "EC3451",
        "title": "Active Filter Synthesis & Sallen-Key Topologies",
        "category": "THEORY_UNIT",
        "description": "Comprehensive 3-lecture sequence on second-order active low-pass and high-pass Butterworth filters with frequency scaling and damping factor tuning.",
        "suggested_duration_hours": 3.0,
        "co_mappings": ["CO2", "CO3"],
        "pedagogical_aids": ["Interactive PPT", "LTspice Live Waveform Projection", "Chalk & Talk Derivations"],
        "sample_topics": [
            "Butterworth filter polynomial approximations and transfer functions",
            "Sallen-Key low-pass filter synthesis with unity gain and equal component design",
            "Quality factor (Q) tuning, cutoff frequency determination, and component tolerance sensitivity"
        ]
    },
    {
        "template_id": "TPL_LAB_OPAMP_CHARACTERIZATION",
        "course_code": "EC3451",
        "title": "Op-Amp Non-Ideal Dynamics & Slew Rate Measurement",
        "category": "LAB_PRACTICAL",
        "description": "Laboratory practical on characterizing LM741 / TL082 input offset voltage, slew rate distortion limits, and gain-bandwidth product trade-offs.",
        "suggested_duration_hours": 2.0,
        "co_mappings": ["CO1", "CO4"],
        "pedagogical_aids": ["Digital Storage Oscilloscope (DSO)", "Function Generator", "Hardware Breadboard Kit"],
        "sample_topics": [
            "Input offset voltage measurement and nulling potentiometer circuit",
            "Large-signal square wave response and slew rate calculation (V/us)",
            "Frequency response measurement and closed-loop -3dB bandwidth determination"
        ]
    },
    {
        "template_id": "TPL_FLIPPED_MODULATION_CARSON",
        "course_code": "EC3491",
        "title": "FM Carson's Rule & Spectral Power Distribution",
        "category": "FLIPPED_CLASSROOM",
        "description": "Pre-lecture simulation activity followed by group problem solving on Carson's bandwidth rule and Bessel function power distribution in FM broadcasting.",
        "suggested_duration_hours": 2.0,
        "co_mappings": ["CO2", "CO4"],
        "pedagogical_aids": ["Pre-Recorded Video", "VoltCore Spectrum Visualizer", "Group Problem Worksheet"],
        "sample_topics": [
            "Narrowband FM vs Wideband FM spectral comparison",
            "Carson's Rule derivation and transmission bandwidth calculations",
            "Power efficiency comparison between standard AM and angle modulation systems"
        ]
    },
    {
        "template_id": "TPL_EMBEDDED_RTOS_TASKS",
        "course_code": "EC3601",
        "title": "Deterministic Preemptive Task Scheduling in FreeRTOS",
        "category": "THEORY_UNIT",
        "description": "Lecture framework covering Rate Monotonic Scheduling (RMS), priority inversion, mutex priority inheritance, and context switching overhead.",
        "suggested_duration_hours": 3.0,
        "co_mappings": ["CO3", "CO5"],
        "pedagogical_aids": ["Wokwi ESP32 Live Emulation", "Logic Analyzer Trace Viewer", "Interactive PPT"],
        "sample_topics": [
            "FreeRTOS task control blocks (TCB) and state transitions",
            "Rate Monotonic priority assignment and CPU utilization bounds",
            "Priority inversion mitigation using binary semaphores vs priority-inheriting mutexes"
        ]
    }
]


class FacultyProductivityEngine:
    """
    High-performance, lightweight Faculty & Department Productivity Workspace engine.
    Supports unit-wise lecture planning, lesson templates, digital assignments,
    rubric-based evaluation feedback, and departmental meeting minutes.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def init_db(self):
        """Initializes tables for lesson plans, templates, assignments, feedback, and meeting minutes."""
        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    # 1. Faculty Lesson Plans Table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS faculty_lesson_plans (
                            plan_id TEXT PRIMARY KEY,
                            course_code TEXT NOT NULL,
                            course_title TEXT NOT NULL,
                            faculty_id TEXT NOT NULL,
                            faculty_name TEXT NOT NULL,
                            unit_number INTEGER NOT NULL,
                            unit_title TEXT NOT NULL,
                            topic_title TEXT NOT NULL,
                            planned_hours REAL DEFAULT 1.0,
                            actual_hours REAL DEFAULT 1.0,
                            pedagogy_mode TEXT DEFAULT 'Chalk & Talk',
                            course_outcome TEXT DEFAULT 'CO1',
                            bloom_level TEXT DEFAULT 'K2-Understand',
                            status TEXT DEFAULT 'PLANNED',
                            completed_date TEXT,
                            notes TEXT,
                            created_at REAL,
                            updated_at REAL
                        );
                    """)

                    # 2. Faculty Lesson Templates Table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS faculty_lesson_templates (
                            template_id TEXT PRIMARY KEY,
                            course_code TEXT NOT NULL,
                            title TEXT NOT NULL,
                            category TEXT NOT NULL,
                            description TEXT,
                            suggested_duration_hours REAL,
                            co_mappings_json TEXT,
                            pedagogical_aids_json TEXT,
                            sample_topics_json TEXT
                        );
                    """)

                    # 3. Faculty Assignments Table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS faculty_assignments (
                            assignment_id TEXT PRIMARY KEY,
                            course_code TEXT NOT NULL,
                            faculty_id TEXT NOT NULL,
                            faculty_name TEXT NOT NULL,
                            title TEXT NOT NULL,
                            unit_number INTEGER DEFAULT 1,
                            instructions TEXT,
                            questions_json TEXT,
                            due_date TEXT NOT NULL,
                            total_marks REAL DEFAULT 100.0,
                            rubric_json TEXT,
                            status TEXT DEFAULT 'PUBLISHED',
                            created_at REAL
                        );
                    """)

                    # 4. Student Submissions & Feedback Table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS assignment_submissions_feedback (
                            feedback_id TEXT PRIMARY KEY,
                            assignment_id TEXT NOT NULL,
                            student_id TEXT NOT NULL,
                            student_name TEXT NOT NULL,
                            submission_url TEXT,
                            marks_obtained REAL,
                            total_marks REAL DEFAULT 100.0,
                            evaluation_rubric_scores_json TEXT,
                            qualitative_feedback TEXT,
                            evaluated_by TEXT,
                            evaluated_at REAL,
                            status TEXT DEFAULT 'GRADED',
                            FOREIGN KEY (assignment_id) REFERENCES faculty_assignments(assignment_id)
                        );
                    """)

                    # 5. Department Meeting Minutes Table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS department_meeting_minutes (
                            meeting_id TEXT PRIMARY KEY,
                            meeting_title TEXT NOT NULL,
                            meeting_date TEXT NOT NULL,
                            chairperson TEXT NOT NULL,
                            attendees_json TEXT,
                            agenda_items_json TEXT,
                            key_decisions_json TEXT,
                            action_items_json TEXT,
                            created_at REAL
                        );
                    """)

                    # Fast indices
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_lesson_plans_course ON faculty_lesson_plans(course_code, unit_number);")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_assignments_course ON faculty_assignments(course_code);")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_student ON assignment_submissions_feedback(student_id);")

                    self._seed_default_data(conn)
            finally:
                conn.close()

    def _seed_default_data(self, conn: sqlite3.Connection):
        """Seeds lesson templates, sample lesson plans, assignments, feedback, and meeting minutes."""
        now = time.time()

        # 1. Seed Faculty Templates
        for tpl in FACULTY_TEMPLATES_CATALOG:
            conn.execute("""
                INSERT OR IGNORE INTO faculty_lesson_templates (
                    template_id, course_code, title, category,
                    description, suggested_duration_hours,
                    co_mappings_json, pedagogical_aids_json, sample_topics_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                tpl["template_id"],
                tpl["course_code"],
                tpl["title"],
                tpl["category"],
                tpl["description"],
                tpl["suggested_duration_hours"],
                json.dumps(tpl["co_mappings"]),
                json.dumps(tpl["pedagogical_aids"]),
                json.dumps(tpl["sample_topics"])
            ))

        # 2. Seed Sample Lesson Plans for EC3451 & EC3491
        sample_plans = [
            ("LP_EC3451_01", "EC3451", "Linear Integrated Circuits", DEFAULT_FACULTY_ID, DEFAULT_FACULTY_NAME, 1, "Unit I: Operational Amplifier Fundamentals", "Differential Amplifier configurations, CMRR, and current mirror bias circuits", 2.0, 2.0, "Chalk & Talk", "CO1", "K2-Understand", "COMPLETED", "2026-10-10", "Derivations completed on board; students solved 2 practice numericals.", now, now),
            ("LP_EC3451_02", "EC3451", "Linear Integrated Circuits", DEFAULT_FACULTY_ID, DEFAULT_FACULTY_NAME, 1, "Unit I: Operational Amplifier Fundamentals", "Op-Amp non-ideal DC/AC characteristics: input offset voltage, slew rate, frequency response", 2.0, 2.0, "Interactive PPT", "CO1", "K3-Apply", "COMPLETED", "2026-10-14", "DSO demonstration of slew-rate triangular distortion conducted.", now, now),
            ("LP_EC3451_03", "EC3451", "Linear Integrated Circuits", DEFAULT_FACULTY_ID, DEFAULT_FACULTY_NAME, 2, "Unit II: Active Filters & Signal Conditioning", "First and second-order low-pass Butterworth filters using Sallen-Key topology", 2.0, 2.0, "Wokwi Simulation", "CO2", "K3-Apply", "COMPLETED", "2026-10-22", "Simulated cutoff response in LTspice and compared with KaTeX formulas.", now, now),
            ("LP_EC3451_04", "EC3451", "Linear Integrated Circuits", DEFAULT_FACULTY_ID, DEFAULT_FACULTY_NAME, 2, "Unit II: Active Filters & Signal Conditioning", "Higher-order filter synthesis, Chebyshev passband ripple, and bandpass state-variable filters", 2.0, 1.5, "Interactive PPT", "CO2", "K4-Analyze", "IN_PROGRESS", None, "Students preparing group presentations on bandpass architectures.", now, now),
            ("LP_EC3451_05", "EC3451", "Linear Integrated Circuits", DEFAULT_FACULTY_ID, DEFAULT_FACULTY_NAME, 3, "Unit III: Waveform Generators & 555 Timers", "Schmitt Trigger, Astable and Monostable multivibrators using IC 555", 2.0, 0.0, "Hardware Lab Bench", "CO3", "K3-Apply", "PLANNED", None, "Scheduled for next lab cycle in Lab 304.", now, now),
            ("LP_EC3491_01", "EC3491", "Communication Systems", DEFAULT_FACULTY_ID, DEFAULT_FACULTY_NAME, 1, "Unit I: Amplitude Modulation Systems", "Double Sideband Full Carrier (DSB-FC) and Suppressed Carrier (DSB-SC) modulation equations", 2.0, 2.0, "Chalk & Talk", "CO1", "K2-Understand", "COMPLETED", "2026-10-12", "Power efficiency calculations derived for modulation index mu=1.0.", now, now),
            ("LP_EC3491_02", "EC3491", "Communication Systems", DEFAULT_FACULTY_ID, DEFAULT_FACULTY_NAME, 2, "Unit II: Angle Modulation & Carson Rule", "FM frequency deviation, modulation index, and Carson's rule transmission bandwidth", 2.0, 2.0, "Wokwi Simulation", "CO2", "K3-Apply", "COMPLETED", "2026-10-28", "Audio spectrum demonstration shown using software spectrogram tool.", now, now),
            ("LP_EC3491_03", "EC3491", "Communication Systems", DEFAULT_FACULTY_ID, DEFAULT_FACULTY_NAME, 3, "Unit III: Pulse Modulation & Sampling", "Nyquist sampling theorem, aliasing mitigation, and Pulse Code Modulation (PCM) quantization", 2.0, 0.0, "Flipped Classroom", "CO3", "K4-Analyze", "PLANNED", None, "Pre-lecture quiz uploaded to portal.", now, now)
        ]
        for plan in sample_plans:
            conn.execute("""
                INSERT OR IGNORE INTO faculty_lesson_plans (
                    plan_id, course_code, course_title, faculty_id, faculty_name,
                    unit_number, unit_title, topic_title, planned_hours, actual_hours,
                    pedagogy_mode, course_outcome, bloom_level, status, completed_date,
                    notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, plan)

        # 3. Seed Sample Assignments
        sample_assignments = [
            (
                "ASGN_EC3451_01",
                "EC3451",
                DEFAULT_FACULTY_ID,
                DEFAULT_FACULTY_NAME,
                "Assignment 1: Sallen-Key Active Filter Synthesis & LTspice Verification",
                2,
                "Design a 2nd-order Butterworth low-pass filter with cutoff fc = 1.0 kHz and unity gain. Calculate exact R1, R2, C1, and C2 values. Run AC sweep in LTspice and verify -3dB cutoff and -40dB/decade roll-off.",
                json.dumps([
                    "Derive the transfer function H(s) of a Sallen-Key low-pass filter topology.",
                    "Select standard component values assuming C1 = 14.14 nF and C2 = 7.07 nF. Determine required R1 and R2.",
                    "Plot the Bode magnitude and phase response from 10 Hz to 100 kHz in LTspice or Python.",
                    "Explain the impact of op-amp gain-bandwidth product (GBWP) on filter cutoff degradation at high frequencies."
                ]),
                "2026-11-20",
                100.0,
                json.dumps({
                    "mathematical_derivation": 25,
                    "component_selection": 25,
                    "simulation_accuracy": 30,
                    "interpretation_and_report": 20
                }),
                "PUBLISHED",
                now
            ),
            (
                "ASGN_EC3491_01",
                "EC3491",
                DEFAULT_FACULTY_ID,
                DEFAULT_FACULTY_NAME,
                "Assignment 1: Angle Modulation & Carson's Bandwidth Analysis",
                2,
                "Analyze a commercial FM broadcast transmission with carrier fc = 100 MHz, message frequency fm = 15 kHz, and peak frequency deviation delta_f = 75 kHz. Calculate modulation index and total transmission bandwidth.",
                json.dumps([
                    "Calculate the FM modulation index beta.",
                    "Apply Carson's Rule to determine total 98% power bandwidth in kHz.",
                    "Compare with the 1% Bessel function sideband bandwidth.",
                    "Compute the total transmitted power if carrier amplitude Ac = 10V into 50 Ohm antenna."
                ]),
                "2026-11-25",
                100.0,
                json.dumps({
                    "modulation_index_calc": 30,
                    "carsons_rule_bandwidth": 35,
                    "power_calculations": 20,
                    "technical_presentation": 15
                }),
                "PUBLISHED",
                now
            )
        ]
        for asgn in sample_assignments:
            conn.execute("""
                INSERT OR IGNORE INTO faculty_assignments (
                    assignment_id, course_code, faculty_id, faculty_name,
                    title, unit_number, instructions, questions_json,
                    due_date, total_marks, rubric_json, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, asgn)

        # 4. Seed Sample Assignment Evaluation / Feedback for Ashok Kumar A
        sample_feedback_id = "FB_ASGN_EC3451_01_2023MITEC042"
        cursor = conn.execute("SELECT feedback_id FROM assignment_submissions_feedback WHERE feedback_id = ?", (sample_feedback_id,))
        if not cursor.fetchone():
            conn.execute("""
                INSERT INTO assignment_submissions_feedback (
                    feedback_id, assignment_id, student_id, student_name,
                    submission_url, marks_obtained, total_marks,
                    evaluation_rubric_scores_json, qualitative_feedback,
                    evaluated_by, evaluated_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                sample_feedback_id,
                "ASGN_EC3451_01",
                DEFAULT_STUDENT_ID,
                "Ashok Kumar A",
                "https://github.com/AshokKumar313/VoltCore-LMS-Portal/raw/main/reports/ec3451_assignment1_filter_synthesis.pdf",
                96.0,
                100.0,
                json.dumps({
                    "mathematical_derivation": 25.0,
                    "component_selection": 24.0,
                    "simulation_accuracy": 29.0,
                    "interpretation_and_report": 18.0
                }),
                "Exemplary submission. Mathematical derivation for Sallen-Key second-order transfer function was rigorous. LTspice AC analysis matches theoretical cutoff within 0.4% error. Excellent analysis of high-frequency op-amp GBWP limitations.",
                DEFAULT_FACULTY_NAME,
                now,
                "GRADED"
            ))

        # 5. Seed Department Meeting Minutes (MoM)
        sample_meeting_id = "MOM_MIT_ECE_2026_10_25"
        cursor = conn.execute("SELECT meeting_id FROM department_meeting_minutes WHERE meeting_id = ?", (sample_meeting_id,))
        if not cursor.fetchone():
            conn.execute("""
                INSERT INTO department_meeting_minutes (
                    meeting_id, meeting_title, meeting_date, chairperson,
                    attendees_json, agenda_items_json, key_decisions_json,
                    action_items_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                sample_meeting_id,
                "Department Faculty Review: Internal Assessment 1 & Lab Attainment",
                "2026-10-25",
                DEFAULT_FACULTY_NAME,
                json.dumps([
                    "Dr. P. Nirmal Kumar (HOD / Chair)",
                    "Dr. M. Kannan (Professor, ECE)",
                    "Dr. S. Piramasubramanian (Assoc. Prof, ECE)",
                    "Dr. G. Balamurugan (Asst. Prof, ECE)",
                    "Ashok Kumar A (Student Platform Lead, Invitee)"
                ]),
                json.dumps([
                    "Analysis of Internal Assessment 1 (IA-1) pass percentages and CO attainment across EC3451 & EC3491.",
                    "Review of Lab 304 hardware equipment calibration (DSOs, Signal Generators, FPGA trainers).",
                    "Implementation of continuous digital rubric grading in VoltCore Apex Academia portal.",
                    "Mini-project (EC3711) milestone tracking and faculty supervisor assignments."
                ]),
                json.dumps([
                    "Remedial problem-solving tutorials approved for students scoring below 60% in IA-1.",
                    "VoltCore automated rubric grading officially recognized for 20% continuous evaluation marks.",
                    "Laboratory hours extended to 6:30 PM on Thursdays for hardware project prototyping."
                ]),
                json.dumps([
                    {"task": "Publish remedial tutorial schedule for EC3451 Unit II", "assignee": "Dr. G. Balamurugan", "deadline": "2026-11-05", "status": "COMPLETED"},
                    {"task": "Verify calibration certificates for DSO benches in Lab 304", "assignee": "Lab Superintendent", "deadline": "2026-11-12", "status": "IN_PROGRESS"},
                    {"task": "Collect mid-term mini-project proposal submissions via portal", "assignee": "Dr. M. Kannan", "deadline": "2026-11-18", "status": "PENDING"}
                ]),
                now
            ))

    # ====================================================================================
    # 1. Overview & Faculty Analytics
    # ====================================================================================

    def get_overview(self, faculty_id: str = DEFAULT_FACULTY_ID) -> Dict[str, Any]:
        """Provides an aggregated overview of faculty lecture plans, assignments, and minutes."""
        conn = self._get_connection()
        try:
            # Lesson plans summary
            cur = conn.execute("""
                SELECT COUNT(*) AS total_plans,
                       SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed_plans,
                       SUM(CASE WHEN status = 'IN_PROGRESS' THEN 1 ELSE 0 END) AS in_progress_plans,
                       COALESCE(SUM(planned_hours), 0.0) AS total_planned_hours,
                       COALESCE(SUM(actual_hours), 0.0) AS total_actual_hours
                FROM faculty_lesson_plans;
            """)
            lp_row = cur.fetchone()
            total_lp = lp_row["total_plans"] or 0
            comp_lp = lp_row["completed_plans"] or 0
            in_prog_lp = lp_row["in_progress_plans"] or 0
            planned_hrs = lp_row["total_planned_hours"] or 0.0
            actual_hrs = lp_row["total_actual_hours"] or 0.0
            syllabus_coverage_pct = round((comp_lp / total_lp * 100), 1) if total_lp > 0 else 0.0

            # Assignments summary
            cur = conn.execute("SELECT COUNT(*) AS total_assignments FROM faculty_assignments;")
            total_asgns = cur.fetchone()["total_assignments"]

            # Submissions & Graded feedback summary
            cur = conn.execute("""
                SELECT COUNT(*) AS total_feedbacks,
                       AVG(marks_obtained) AS avg_score
                FROM assignment_submissions_feedback;
            """)
            fb_row = cur.fetchone()
            total_fb = fb_row["total_feedbacks"] or 0
            avg_score = round(fb_row["avg_score"] or 0.0, 1)

            # Meeting minutes count
            cur = conn.execute("SELECT COUNT(*) AS total_meetings FROM department_meeting_minutes;")
            total_meetings = cur.fetchone()["total_meetings"]

            # Templates count
            cur = conn.execute("SELECT COUNT(*) AS total_templates FROM faculty_lesson_templates;")
            total_templates = cur.fetchone()["total_templates"]

            return {
                "status": "SUCCESS",
                "faculty_id": faculty_id,
                "faculty_name": DEFAULT_FACULTY_NAME,
                "institution": "Madras Institute of Technology (MIT) Campus, Anna University",
                "department": "Department of Electronics Engineering",
                "metrics": {
                    "total_lesson_plans": total_lp,
                    "completed_lesson_plans": comp_lp,
                    "in_progress_lesson_plans": in_prog_lp,
                    "syllabus_coverage_percent": syllabus_coverage_pct,
                    "total_planned_hours": round(planned_hrs, 1),
                    "total_actual_hours": round(actual_hrs, 1),
                    "total_assignments": total_asgns,
                    "total_graded_feedbacks": total_fb,
                    "average_assignment_score": avg_score,
                    "total_meeting_minutes": total_meetings,
                    "total_templates_available": total_templates
                }
            }
        finally:
            conn.close()

    # ====================================================================================
    # 2. Syllabus Unit-Wise Lecture Planning
    # ====================================================================================

    def get_lesson_plans(
        self,
        course_code: Optional[str] = None,
        unit_number: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves lecture plans with optional course and unit filters."""
        conn = self._get_connection()
        try:
            query = "SELECT * FROM faculty_lesson_plans WHERE 1=1"
            params = []
            if course_code:
                query += " AND course_code = ?"
                params.append(course_code)
            if unit_number is not None:
                query += " AND unit_number = ?"
                params.append(unit_number)

            query += " ORDER BY course_code ASC, unit_number ASC, plan_id ASC;"
            cur = conn.execute(query, tuple(params))
            plans = []
            for row in cur.fetchall():
                plans.append({
                    "plan_id": row["plan_id"],
                    "course_code": row["course_code"],
                    "course_title": row["course_title"],
                    "faculty_id": row["faculty_id"],
                    "faculty_name": row["faculty_name"],
                    "unit_number": row["unit_number"],
                    "unit_title": row["unit_title"],
                    "topic_title": row["topic_title"],
                    "planned_hours": row["planned_hours"],
                    "actual_hours": row["actual_hours"],
                    "pedagogy_mode": row["pedagogy_mode"],
                    "course_outcome": row["course_outcome"],
                    "bloom_level": row["bloom_level"],
                    "status": row["status"],
                    "completed_date": row["completed_date"],
                    "notes": row["notes"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                })
            return plans
        finally:
            conn.close()

    def create_lesson_plan(self, data: Dict[str, Any], actor_role: str = "Faculty") -> Dict[str, Any]:
        """Creates a new syllabus lesson plan with RBAC faculty enforcement."""
        if actor_role not in ["Faculty", "Teacher", "Admin"]:
            return {"status": "FORBIDDEN", "message": "Only faculty members or administrators can create lesson plans."}

        course_code = (data.get("course_code") or "").strip().upper()
        topic = (data.get("topic_title") or "").strip()
        if not course_code or not topic:
            return {"status": "ERROR", "message": "Course code and topic title are required."}

        plan_id = data.get("plan_id") or f"LP_{course_code}_{int(time.time()*1000)}"
        course_title = data.get("course_title", "ECE Core Specialization")
        faculty_id = data.get("faculty_id", DEFAULT_FACULTY_ID)
        faculty_name = data.get("faculty_name", DEFAULT_FACULTY_NAME)
        unit_num = max(1, min(5, int(data.get("unit_number", 1))))
        unit_title = data.get("unit_title", f"Unit {unit_num} Core Syllabus")
        planned_hrs = max(0.5, float(data.get("planned_hours", 1.0)))
        actual_hrs = max(0.0, float(data.get("actual_hours", 1.0)))
        pedagogy = data.get("pedagogy_mode", "Chalk & Talk")
        co = data.get("course_outcome", f"CO{unit_num}")
        bloom = data.get("bloom_level", "K2-Understand")
        status = data.get("status", "PLANNED")
        notes = data.get("notes", "")
        now = time.time()

        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    conn.execute("""
                        INSERT INTO faculty_lesson_plans (
                            plan_id, course_code, course_title, faculty_id, faculty_name,
                            unit_number, unit_title, topic_title, planned_hours, actual_hours,
                            pedagogy_mode, course_outcome, bloom_level, status, completed_date,
                            notes, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        plan_id, course_code, course_title, faculty_id, faculty_name,
                        unit_num, unit_title, topic, planned_hrs, actual_hrs,
                        pedagogy, co, bloom, status,
                        time.strftime("%Y-%m-%d") if status == "COMPLETED" else None,
                        notes, now, now
                    ))
                return {
                    "status": "SUCCESS",
                    "plan_id": plan_id,
                    "message": f"Lesson plan '{topic}' registered for {course_code} Unit {unit_num}."
                }
            except sqlite3.IntegrityError:
                return {"status": "ERROR", "message": f"Lesson plan with ID '{plan_id}' already exists."}
            finally:
                conn.close()

    def update_lesson_plan_status(
        self,
        plan_id: str,
        new_status: str,
        actual_hours: Optional[float] = None,
        notes: Optional[str] = None,
        actor_role: str = "Faculty"
    ) -> Dict[str, Any]:
        """Toggles lesson plan status (PLANNED, IN_PROGRESS, COMPLETED) with RBAC enforcement."""
        if actor_role not in ["Faculty", "Teacher", "Admin"]:
            return {"status": "FORBIDDEN", "message": "Only faculty members or administrators can update lesson plan status."}

        valid_statuses = ["PLANNED", "IN_PROGRESS", "COMPLETED"]
        if new_status not in valid_statuses:
            return {"status": "ERROR", "message": f"Invalid status '{new_status}'."}

        completed_date = time.strftime("%Y-%m-%d") if new_status == "COMPLETED" else None
        now = time.time()

        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    if actual_hours is not None:
                        cur = conn.execute("""
                            UPDATE faculty_lesson_plans
                            SET status = ?, completed_date = ?, actual_hours = ?, notes = COALESCE(?, notes), updated_at = ?
                            WHERE plan_id = ?;
                        """, (new_status, completed_date, actual_hours, notes, now, plan_id))
                    else:
                        cur = conn.execute("""
                            UPDATE faculty_lesson_plans
                            SET status = ?, completed_date = ?, notes = COALESCE(?, notes), updated_at = ?
                            WHERE plan_id = ?;
                        """, (new_status, completed_date, notes, now, plan_id))

                    if cur.rowcount == 0:
                        return {"status": "ERROR", "message": f"Lesson plan '{plan_id}' not found."}

                return {
                    "status": "SUCCESS",
                    "plan_id": plan_id,
                    "new_status": new_status,
                    "completed_date": completed_date
                }
            finally:
                conn.close()

    # ====================================================================================
    # 3. Faculty Lesson Template Library
    # ====================================================================================

    def get_templates(self, course_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns standard lesson plan templates."""
        conn = self._get_connection()
        try:
            query = "SELECT * FROM faculty_lesson_templates WHERE 1=1"
            params = []
            if course_code:
                query += " AND course_code = ?"
                params.append(course_code)

            query += " ORDER BY template_id ASC;"
            cur = conn.execute(query, tuple(params))
            templates = []
            for row in cur.fetchall():
                templates.append({
                    "template_id": row["template_id"],
                    "course_code": row["course_code"],
                    "title": row["title"],
                    "category": row["category"],
                    "description": row["description"],
                    "suggested_duration_hours": row["suggested_duration_hours"],
                    "co_mappings": json.loads(row["co_mappings_json"] or "[]"),
                    "pedagogical_aids": json.loads(row["pedagogical_aids_json"] or "[]"),
                    "sample_topics": json.loads(row["sample_topics_json"] or "[]")
                })
            return templates
        finally:
            conn.close()

    # ====================================================================================
    # 4. Digital Assignment Distribution
    # ====================================================================================

    def get_assignments(self, course_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns active and published continuous assessment assignments."""
        conn = self._get_connection()
        try:
            query = "SELECT * FROM faculty_assignments WHERE 1=1"
            params = []
            if course_code:
                query += " AND course_code = ?"
                params.append(course_code)

            query += " ORDER BY created_at DESC;"
            cur = conn.execute(query, tuple(params))
            assignments = []
            for row in cur.fetchall():
                # Count submissions
                cur_sub = conn.execute("""
                    SELECT COUNT(*) AS total_subs,
                           AVG(marks_obtained) AS avg_mark
                    FROM assignment_submissions_feedback
                    WHERE assignment_id = ?;
                """, (row["assignment_id"],))
                sub_row = cur_sub.fetchone()

                assignments.append({
                    "assignment_id": row["assignment_id"],
                    "course_code": row["course_code"],
                    "faculty_id": row["faculty_id"],
                    "faculty_name": row["faculty_name"],
                    "title": row["title"],
                    "unit_number": row["unit_number"],
                    "instructions": row["instructions"],
                    "questions": json.loads(row["questions_json"] or "[]"),
                    "due_date": row["due_date"],
                    "total_marks": row["total_marks"],
                    "rubric": json.loads(row["rubric_json"] or "{}"),
                    "status": row["status"],
                    "submissions_count": sub_row["total_subs"] or 0,
                    "average_score": round(sub_row["avg_mark"] or 0.0, 1),
                    "created_at": row["created_at"]
                })
            return assignments
        finally:
            conn.close()

    def create_assignment(self, data: Dict[str, Any], actor_role: str = "Faculty") -> Dict[str, Any]:
        """Publishes a new continuous assessment assignment with RBAC enforcement."""
        if actor_role not in ["Faculty", "Teacher", "Admin"]:
            return {"status": "FORBIDDEN", "message": "Only faculty members or administrators can create and publish assignments."}

        course_code = (data.get("course_code") or "").strip().upper()
        title = (data.get("title") or "").strip()
        due_date = (data.get("due_date") or "").strip()
        if not course_code or not title or not due_date:
            return {"status": "ERROR", "message": "Course code, title, and due date are required."}

        asgn_id = data.get("assignment_id") or f"ASGN_{course_code}_{int(time.time()*1000)}"
        faculty_id = data.get("faculty_id", DEFAULT_FACULTY_ID)
        faculty_name = data.get("faculty_name", DEFAULT_FACULTY_NAME)
        unit_num = int(data.get("unit_number", 1))
        instructions = data.get("instructions", "")
        questions = data.get("questions", [])
        total_marks = float(data.get("total_marks", 100.0))
        rubric = data.get("rubric", {
            "understanding": 25,
            "analysis_and_simulation": 35,
            "calculations": 25,
            "report_presentation": 15
        })
        status = data.get("status", "PUBLISHED")
        now = time.time()

        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    conn.execute("""
                        INSERT INTO faculty_assignments (
                            assignment_id, course_code, faculty_id, faculty_name,
                            title, unit_number, instructions, questions_json,
                            due_date, total_marks, rubric_json, status, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        asgn_id, course_code, faculty_id, faculty_name,
                        title, unit_num, instructions, json.dumps(questions),
                        due_date, total_marks, json.dumps(rubric), status, now
                    ))
                return {
                    "status": "SUCCESS",
                    "assignment_id": asgn_id,
                    "message": f"Assignment '{title}' published for {course_code}."
                }
            except sqlite3.IntegrityError:
                return {"status": "ERROR", "message": f"Assignment '{asgn_id}' already exists."}
            finally:
                conn.close()

    # ====================================================================================
    # 5. Assignment Submission Feedback Center
    # ====================================================================================

    def get_assignment_feedback(
        self,
        assignment_id: Optional[str] = None,
        student_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves graded submissions and faculty qualitative evaluation reports."""
        conn = self._get_connection()
        try:
            query = "SELECT * FROM assignment_submissions_feedback WHERE 1=1"
            params = []
            if assignment_id:
                query += " AND assignment_id = ?"
                params.append(assignment_id)
            if student_id:
                query += " AND student_id = ?"
                params.append(student_id)

            query += " ORDER BY evaluated_at DESC;"
            cur = conn.execute(query, tuple(params))
            feedbacks = []
            for row in cur.fetchall():
                feedbacks.append({
                    "feedback_id": row["feedback_id"],
                    "assignment_id": row["assignment_id"],
                    "student_id": row["student_id"],
                    "student_name": row["student_name"],
                    "submission_url": row["submission_url"],
                    "marks_obtained": row["marks_obtained"],
                    "total_marks": row["total_marks"],
                    "rubric_scores": json.loads(row["evaluation_rubric_scores_json"] or "{}"),
                    "qualitative_feedback": row["qualitative_feedback"],
                    "evaluated_by": row["evaluated_by"],
                    "evaluated_at": row["evaluated_at"],
                    "status": row["status"]
                })
            return feedbacks
        finally:
            conn.close()

    def record_feedback(self, data: Dict[str, Any], actor_role: str = "Faculty") -> Dict[str, Any]:
        """Records student grade and qualitative rubric feedback with RBAC enforcement."""
        if actor_role not in ["Faculty", "Teacher", "Admin"]:
            return {"status": "FORBIDDEN", "message": "Only faculty members or administrators can evaluate submissions."}

        assignment_id = (data.get("assignment_id") or "").strip()
        student_id = (data.get("student_id") or "").strip()
        if not assignment_id or not student_id:
            return {"status": "ERROR", "message": "Assignment ID and Student ID are required."}

        marks = float(data.get("marks_obtained", 0.0))
        total_marks = float(data.get("total_marks", 100.0))
        if marks < 0.0 or marks > total_marks:
            return {"status": "ERROR", "message": f"Marks ({marks}) must be between 0.0 and {total_marks}."}

        feedback_id = data.get("feedback_id") or f"FB_{assignment_id}_{student_id}"
        student_name = data.get("student_name", "Student")
        sub_url = data.get("submission_url", "")
        rubric_scores = data.get("evaluation_rubric_scores", {})
        qual_fb = data.get("qualitative_feedback", "Evaluated against continuous assessment rubrics.")
        eval_by = data.get("evaluated_by", DEFAULT_FACULTY_NAME)
        status = data.get("status", "GRADED")
        now = time.time()

        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO assignment_submissions_feedback (
                            feedback_id, assignment_id, student_id, student_name,
                            submission_url, marks_obtained, total_marks,
                            evaluation_rubric_scores_json, qualitative_feedback,
                            evaluated_by, evaluated_at, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        feedback_id, assignment_id, student_id, student_name,
                        sub_url, marks, total_marks,
                        json.dumps(rubric_scores), qual_fb,
                        eval_by, now, status
                    ))
                return {
                    "status": "SUCCESS",
                    "feedback_id": feedback_id,
                    "marks_obtained": marks,
                    "message": f"Feedback and grade for student {student_id} recorded successfully."
                }
            finally:
                conn.close()

    # ====================================================================================
    # 6. Department Meeting Minutes & Action Tracker
    # ====================================================================================

    def get_meeting_minutes(self) -> List[Dict[str, Any]]:
        """Retrieves official departmental meeting minutes with action items."""
        conn = self._get_connection()
        try:
            cur = conn.execute("SELECT * FROM department_meeting_minutes ORDER BY meeting_date DESC;")
            meetings = []
            for row in cur.fetchall():
                meetings.append({
                    "meeting_id": row["meeting_id"],
                    "meeting_title": row["meeting_title"],
                    "meeting_date": row["meeting_date"],
                    "chairperson": row["chairperson"],
                    "attendees": json.loads(row["attendees_json"] or "[]"),
                    "agenda_items": json.loads(row["agenda_items_json"] or "[]"),
                    "key_decisions": json.loads(row["key_decisions_json"] or "[]"),
                    "action_items": json.loads(row["action_items_json"] or "[]"),
                    "created_at": row["created_at"]
                })
            return meetings
        finally:
            conn.close()

    def record_meeting_minutes(self, data: Dict[str, Any], actor_role: str = "Faculty") -> Dict[str, Any]:
        """Records departmental meeting minutes with action item assignments."""
        if actor_role not in ["Faculty", "Teacher", "Admin"]:
            return {"status": "FORBIDDEN", "message": "Only faculty members or administrators can record meeting minutes."}

        title = (data.get("meeting_title") or "").strip()
        m_date = (data.get("meeting_date") or time.strftime("%Y-%m-%d")).strip()
        if not title:
            return {"status": "ERROR", "message": "Meeting title is required."}

        meeting_id = data.get("meeting_id") or f"MOM_MIT_ECE_{int(time.time()*1000)}"
        chair = data.get("chairperson", DEFAULT_FACULTY_NAME)
        attendees = data.get("attendees", [DEFAULT_FACULTY_NAME])
        agenda = data.get("agenda_items", [])
        decisions = data.get("key_decisions", [])
        actions = data.get("action_items", [])
        now = time.time()

        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    conn.execute("""
                        INSERT INTO department_meeting_minutes (
                            meeting_id, meeting_title, meeting_date, chairperson,
                            attendees_json, agenda_items_json, key_decisions_json,
                            action_items_json, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        meeting_id, title, m_date, chair,
                        json.dumps(attendees), json.dumps(agenda),
                        json.dumps(decisions), json.dumps(actions),
                        now
                    ))
                return {
                    "status": "SUCCESS",
                    "meeting_id": meeting_id,
                    "message": f"Minutes for '{title}' recorded successfully."
                }
            except sqlite3.IntegrityError:
                return {"status": "ERROR", "message": f"Meeting with ID '{meeting_id}' already exists."}
            finally:
                conn.close()


# Singleton instance for system-wide dispatch
faculty_productivity_engine = FacultyProductivityEngine()
