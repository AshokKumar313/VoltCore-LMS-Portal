"""
========================================================================================
VoltCore Apex Academia - Phase O: Faculty & Administrative Management (Features 351–360)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Features:
  - Feature 351: Faculty Dashboard (Teaching Load, Student Strength, Quick Stats)
  - Feature 352: Student Performance Analytics (GPA distribution, Internals, At-Risk Alert)
  - Feature 353: Assignment Grading Suite (Rubric-based evaluation, Grade release)
  - Feature 354: Attendance Management Portal (Session attendance, 75% cutoff rule)
  - Feature 355: Course Material Upload Manager (Notes, Lab manuals, Question banks)
  - Feature 356: Announcement Broadcast System (Audience targeting, Urgent broadcasts)
  - Feature 357: Student Progress Report Generator (AU Reg 2023 Dossier, Grades O to U)
  - Feature 358: Department Notice Board (Accreditation NBA/NAAC, Faculty circulars)
  - Feature 359: Timetable & Schedule Manager (7-period slots, Lab rooms, Faculty in-charge)
  - Feature 360: Faculty Office Hours Scheduler (In-person & Virtual booking slots)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
========================================================================================
"""

import os
import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")

# ---------------------------------------------------------------------------
# DEFAULT ECE COURSES (Feature 351)
# ---------------------------------------------------------------------------

DEFAULT_FACULTY_COURSES = [
    {
        "course_id": "c_ec3552",
        "course_code": "EC3552",
        "course_name": "VLSI and Chip Design",
        "faculty_id": "fac_01",
        "faculty_name": "Dr. P. Nirmal",
        "semester": 5,
        "academic_year": "2026-2027",
        "enrolled_count": 64
    },
    {
        "course_id": "c_ec3451",
        "course_code": "EC3451",
        "course_name": "Linear Integrated Circuits",
        "faculty_id": "fac_02",
        "faculty_name": "Dr. S. Malarvizhi",
        "semester": 4,
        "academic_year": "2026-2027",
        "enrolled_count": 68
    },
    {
        "course_id": "c_ec3501",
        "course_code": "EC3501",
        "course_name": "Wireless Communication",
        "faculty_id": "fac_03",
        "faculty_name": "Dr. V. Sathiesh Kumar",
        "semester": 5,
        "academic_year": "2026-2027",
        "enrolled_count": 64
    },
    {
        "course_id": "c_ec3711",
        "course_code": "EC3711",
        "course_name": "Embedded Systems Laboratory",
        "faculty_id": "fac_02",
        "faculty_name": "Dr. S. Malarvizhi",
        "semester": 5,
        "academic_year": "2026-2027",
        "enrolled_count": 64
    }
]

# ---------------------------------------------------------------------------
# DEFAULT TIMETABLE SLOTS (Feature 359)
# ---------------------------------------------------------------------------

DEFAULT_TIMETABLE = [
    {"slot_id": "tt_m1", "day": "MON", "period": 1, "time": "08:30 - 09:20", "course_code": "EC3552", "room": "ECE-LH1", "faculty": "Dr. P. Nirmal"},
    {"slot_id": "tt_m2", "day": "MON", "period": 2, "time": "09:20 - 10:10", "course_code": "EC3501", "room": "ECE-LH1", "faculty": "Dr. V. Sathiesh Kumar"},
    {"slot_id": "tt_m3", "day": "MON", "period": 3, "time": "10:30 - 11:20", "course_code": "EC3451", "room": "ECE-LH2", "faculty": "Dr. S. Malarvizhi"},
    {"slot_id": "tt_m4", "day": "MON", "period": 4, "time": "11:20 - 12:10", "course_code": "EC3351", "room": "ECE-LH2", "faculty": "Dr. T. S. Pradeep Kumar"},
    {"slot_id": "tt_m5", "day": "MON", "period": 5, "time": "13:30 - 16:30", "course_code": "EC3711", "room": "Embedded/HIL Lab 304", "faculty": "Dr. S. Malarvizhi"},
    {"slot_id": "tt_t1", "day": "TUE", "period": 1, "time": "08:30 - 09:20", "course_code": "EC3501", "room": "ECE-LH1", "faculty": "Dr. V. Sathiesh Kumar"},
    {"slot_id": "tt_t2", "day": "TUE", "period": 2, "time": "09:20 - 10:10", "course_code": "EC3552", "room": "ECE-LH1", "faculty": "Dr. P. Nirmal"},
    {"slot_id": "tt_t3", "day": "TUE", "period": 3, "time": "10:30 - 11:20", "course_code": "EC3551", "room": "Microwave Lab", "faculty": "Dr. V. Sathiesh Kumar"},
    {"slot_id": "tt_w1", "day": "WED", "period": 1, "time": "08:30 - 11:30", "course_code": "EC3552", "room": "VLSI CAD Lab", "faculty": "Dr. P. Nirmal"}
]

# ---------------------------------------------------------------------------
# DEFAULT NOTICE BOARD (Feature 358)
# ---------------------------------------------------------------------------

DEFAULT_NOTICES = [
    {
        "id": "not_01",
        "title": "NBA Accreditation Tier-1 Evaluation Visit (Criterion 4 & 5 Audit)",
        "category": "ACCREDITATION",
        "priority": "URGENT",
        "author": "HOD / Department of Electronics Engineering",
        "date": "2026-11-05",
        "content": "All faculty handling Regulation 2023 courses are requested to submit course files, attainment sheets (CO-PO mapping), and student portfolio samples to the department IQAC room by Nov 12."
    },
    {
        "id": "not_02",
        "title": "Call for Proposals: DST-SERB Semiconductor R&D Initiative 2026",
        "category": "RESEARCH_GRANT",
        "priority": "NORMAL",
        "author": "Dean of Research, MIT Campus",
        "date": "2026-11-03",
        "content": "Faculty members working in GaN power devices, RF-MEMS, and RISC-V edge processors are invited to submit inter-departmental research proposals under the India Semiconductor Mission."
    },
    {
        "id": "not_03",
        "title": "Faculty Development Program (FDP) on Cadence Genus & Innovus EDA",
        "category": "FDP",
        "priority": "NORMAL",
        "author": "VLSI Centre of Excellence, MIT Campus",
        "date": "2026-11-01",
        "content": "One-week hands-on FDP on 7nm synthesis and physical placement workflows in collaboration with Cadence Design Systems."
    }
]


class FacultyAdminEngine:
    """
    Core backend engine for VoltCore Apex Academia Phase O (Features 351–360).
    Manages faculty dashboards, grade calculations, student progress reports,
    attendance policies, timetables, course resources, and office hours.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_sqlite()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _init_sqlite(self) -> None:
        with self._lock:
            conn = self._get_connection()
            try:
                # Feature 351: Faculty courses
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS faculty_courses (
                        course_id TEXT PRIMARY KEY,
                        course_code TEXT NOT NULL,
                        course_name TEXT NOT NULL,
                        faculty_id TEXT NOT NULL,
                        faculty_name TEXT NOT NULL,
                        semester INTEGER NOT NULL,
                        academic_year TEXT NOT NULL,
                        enrolled_count INTEGER DEFAULT 0
                    )
                """)

                # Feature 352: Student enrollments & analytics
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS student_enrollments (
                        student_roll TEXT NOT NULL,
                        student_name TEXT NOT NULL,
                        course_code TEXT NOT NULL,
                        internal_1 REAL DEFAULT 0.0,
                        internal_2 REAL DEFAULT 0.0,
                        internal_3 REAL DEFAULT 0.0,
                        assignment_score REAL DEFAULT 0.0,
                        attendance_pct REAL DEFAULT 100.0,
                        cgpa REAL DEFAULT 8.0,
                        PRIMARY KEY (student_roll, course_code)
                    )
                """)

                # Feature 353: Assignment grading
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS assignment_submissions (
                        submission_id TEXT PRIMARY KEY,
                        student_roll TEXT NOT NULL,
                        student_name TEXT NOT NULL,
                        assignment_title TEXT NOT NULL,
                        course_code TEXT NOT NULL,
                        circuit_score REAL DEFAULT 0.0,
                        sim_score REAL DEFAULT 0.0,
                        viva_score REAL DEFAULT 0.0,
                        report_score REAL DEFAULT 0.0,
                        total_score REAL DEFAULT 0.0,
                        max_score REAL DEFAULT 100.0,
                        feedback TEXT DEFAULT '',
                        is_graded INTEGER DEFAULT 0,
                        graded_at TEXT
                    )
                """)

                # Feature 355: Course materials
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS course_materials (
                        material_id TEXT PRIMARY KEY,
                        course_code TEXT NOT NULL,
                        title TEXT NOT NULL,
                        category TEXT NOT NULL,
                        file_url TEXT NOT NULL,
                        uploaded_by TEXT NOT NULL,
                        uploaded_at TEXT NOT NULL
                    )
                """)

                # Feature 356 & 358: Announcements & Department Notice Board
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS department_announcements (
                        announcement_id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        target_audience TEXT NOT NULL,
                        category TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        author_name TEXT NOT NULL,
                        date TEXT NOT NULL,
                        content TEXT NOT NULL
                    )
                """)

                # Feature 359: Timetable slots
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS timetable_slots (
                        slot_id TEXT PRIMARY KEY,
                        day TEXT NOT NULL,
                        period INTEGER NOT NULL,
                        time TEXT NOT NULL,
                        course_code TEXT NOT NULL,
                        room TEXT NOT NULL,
                        faculty TEXT NOT NULL
                    )
                """)

                # Feature 360: Faculty office hours
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS faculty_office_slots (
                        slot_id TEXT PRIMARY KEY,
                        faculty_id TEXT NOT NULL,
                        faculty_name TEXT NOT NULL,
                        day TEXT NOT NULL,
                        time TEXT NOT NULL,
                        mode TEXT NOT NULL,
                        room_or_url TEXT NOT NULL,
                        is_booked INTEGER DEFAULT 0,
                        booked_by_roll TEXT DEFAULT NULL,
                        booked_by_name TEXT DEFAULT NULL
                    )
                """)

                # Seed initial records if empty
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) AS cnt FROM faculty_courses")
                if cursor.fetchone()["cnt"] == 0:
                    for fc in DEFAULT_FACULTY_COURSES:
                        conn.execute("""
                            INSERT INTO faculty_courses
                            (course_id, course_code, course_name, faculty_id, faculty_name, semester, academic_year, enrolled_count)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (fc["course_id"], fc["course_code"], fc["course_name"], fc["faculty_id"], fc["faculty_name"], fc["semester"], fc["academic_year"], fc["enrolled_count"]))

                cursor.execute("SELECT COUNT(*) AS cnt FROM department_announcements")
                if cursor.fetchone()["cnt"] == 0:
                    for n in DEFAULT_NOTICES:
                        conn.execute("""
                            INSERT INTO department_announcements
                            (announcement_id, title, target_audience, category, priority, author_name, date, content)
                            VALUES (?, ?, 'FACULTY_AND_STUDENTS', ?, ?, ?, ?, ?)
                        """, (n["id"], n["title"], n["category"], n["priority"], n["author"], n["date"], n["content"]))

                cursor.execute("SELECT COUNT(*) AS cnt FROM timetable_slots")
                if cursor.fetchone()["cnt"] == 0:
                    for t in DEFAULT_TIMETABLE:
                        conn.execute("""
                            INSERT INTO timetable_slots
                            (slot_id, day, period, time, course_code, room, faculty)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (t["slot_id"], t["day"], t["period"], t["time"], t["course_code"], t["room"], t["faculty"]))

                conn.commit()
            finally:
                conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 351: FACULTY DASHBOARD OVERVIEW
    # ---------------------------------------------------------------------------

    def get_faculty_dashboard(self, faculty_id: str = "fac_01") -> Dict[str, Any]:
        """Fetch summary of courses taught, total student strength, and pending tasks."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM faculty_courses WHERE faculty_id = ?", (faculty_id,))
            courses = [dict(r) for r in cursor.fetchall()]

            total_students = sum(c["enrolled_count"] for c in courses)

            # Count ungraded submissions
            cursor.execute("SELECT COUNT(*) AS cnt FROM assignment_submissions WHERE is_graded = 0")
            pending_grading = cursor.fetchone()["cnt"]

            return {
                "faculty_id": faculty_id,
                "assigned_courses": courses,
                "total_courses": len(courses),
                "total_students": total_students,
                "pending_grading_count": pending_grading
            }
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 352: STUDENT PERFORMANCE ANALYTICS & AT-RISK RADAR
    # ---------------------------------------------------------------------------

    def enroll_student(
        self,
        student_roll: str,
        student_name: str,
        course_code: str,
        internal_1: float,
        internal_2: float,
        internal_3: float,
        assignment_score: float,
        attendance_pct: float,
        cgpa: float
    ) -> Dict[str, Any]:
        """Enroll or update student course records with academic marks."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO student_enrollments
                    (student_roll, student_name, course_code, internal_1, internal_2, internal_3, assignment_score, attendance_pct, cgpa)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (student_roll, student_name, course_code.upper(), internal_1, internal_2, internal_3, assignment_score, attendance_pct, cgpa))
                conn.commit()
            finally:
                conn.close()
        return {"status": "success", "student_roll": student_roll, "course_code": course_code.upper()}

    def get_course_analytics(self, course_code: str) -> Dict[str, Any]:
        """
        Calculate class performance metrics:
        - Average internals, pass percentage (internal score >= 50%)
        - List of at-risk students (CGPA < 6.5 or Attendance < 75%)
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM student_enrollments WHERE course_code = ?", (course_code.upper(),))
            rows = [dict(r) for r in cursor.fetchall()]

            if not rows:
                return {
                    "course_code": course_code.upper(),
                    "enrolled_count": 0,
                    "avg_internal": 0.0,
                    "avg_attendance": 0.0,
                    "pass_percentage": 0.0,
                    "at_risk_students": []
                }

            total_internals = 0.0
            total_attendance = 0.0
            passed_count = 0
            at_risk = []

            for s in rows:
                avg_i = (s["internal_1"] + s["internal_2"] + s["internal_3"]) / 3.0
                composite_internal = 0.40 * avg_i + 0.20 * s["assignment_score"]
                total_internals += composite_internal
                total_attendance += s["attendance_pct"]

                if composite_internal >= 25.0: # 50% of 50-mark internal scale
                    passed_count += 1

                # At-risk criteria: CGPA < 6.5 OR Attendance < 75.0%
                is_risk = False
                reasons = []
                if s["cgpa"] < 6.5:
                    is_risk = True
                    reasons.append(f"Low CGPA ({s['cgpa']:.2f})")
                if s["attendance_pct"] < 75.0:
                    is_risk = True
                    reasons.append(f"Attendance Shortage ({s['attendance_pct']:.1f}%)")

                if is_risk:
                    at_risk.append({
                        "student_roll": s["student_roll"],
                        "student_name": s["student_name"],
                        "cgpa": s["cgpa"],
                        "attendance_pct": s["attendance_pct"],
                        "reasons": reasons
                    })

            n = len(rows)
            return {
                "course_code": course_code.upper(),
                "enrolled_count": n,
                "avg_internal": round(total_internals / n, 2),
                "avg_attendance": round(total_attendance / n, 2),
                "pass_percentage": round((passed_count / n) * 100.0, 1),
                "at_risk_count": len(at_risk),
                "at_risk_students": at_risk
            }
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 353: ASSIGNMENT GRADING SUITE
    # ---------------------------------------------------------------------------

    def submit_assignment(
        self,
        submission_id: str,
        student_roll: str,
        student_name: str,
        assignment_title: str,
        course_code: str,
        max_score: float = 100.0
    ) -> Dict[str, Any]:
        """Record an assignment submission awaiting grading."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO assignment_submissions
                    (submission_id, student_roll, student_name, assignment_title, course_code, circuit_score, sim_score, viva_score, report_score, total_score, max_score, feedback, is_graded, graded_at)
                    VALUES (?, ?, ?, ?, ?, 0.0, 0.0, 0.0, 0.0, 0.0, ?, '', 0, NULL)
                """, (submission_id, student_roll, student_name, assignment_title, course_code.upper(), max_score))
                conn.commit()
            finally:
                conn.close()
        return {"status": "success", "submission_id": submission_id}

    def grade_assignment(
        self,
        submission_id: str,
        circuit_score: float,
        sim_score: float,
        viva_score: float,
        report_score: float,
        feedback: str
    ) -> Dict[str, Any]:
        """
        Grade an assignment submission using the ECE 4-pillar rubric:
        Total = Circuit (30) + Simulation (30) + Viva (20) + Report (20) = 100 max.
        """
        c = max(0.0, min(30.0, float(circuit_score)))
        s = max(0.0, min(30.0, float(sim_score)))
        v = max(0.0, min(20.0, float(viva_score)))
        r = max(0.0, min(20.0, float(report_score)))
        total = round(c + s + v + r, 2)
        now_iso = datetime.now(timezone.utc).isoformat()

        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    UPDATE assignment_submissions
                    SET circuit_score = ?, sim_score = ?, viva_score = ?, report_score = ?, total_score = ?, feedback = ?, is_graded = 1, graded_at = ?
                    WHERE submission_id = ?
                """, (c, s, v, r, total, feedback, now_iso, submission_id))
                conn.commit()
            finally:
                conn.close()

        return {
            "status": "success",
            "submission_id": submission_id,
            "total_score": total,
            "rubric": {"circuit": c, "simulation": s, "viva": v, "report": r}
        }

    def get_assignment_submissions(self, course_code: str) -> List[Dict[str, Any]]:
        """List all submissions for a course."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM assignment_submissions WHERE course_code = ? ORDER BY is_graded ASC", (course_code.upper(),))
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 354: ATTENDANCE MANAGEMENT (ANNA UNIVERSITY 75% CUTOFF)
    # ---------------------------------------------------------------------------

    def evaluate_attendance_status(self, attendance_pct: float) -> Dict[str, Any]:
        """
        Evaluate attendance according to Anna University Regulation 2023:
        - >= 80%: Satisfactory / Normal Exam Eligibility
        - 75% to 79.9%: Condonation Required on Medical Grounds (HOD Approval)
        - < 75%: Shortage / Debarred from End-Semester Examinations
        """
        pct = max(0.0, min(100.0, float(attendance_pct)))
        if pct >= 80.0:
            return {"status": "ELIGIBLE", "badge": "SATISFACTORY", "code": "GREEN", "message": "Normal end-semester examination hall ticket issued."}
        elif pct >= 75.0:
            return {"status": "CONDONATION_REQUIRED", "badge": "CONDONATION", "code": "AMBER", "message": "Medical/OD certificate and condonation fee approval required."}
        else:
            return {"status": "DEBARRED", "badge": "ATTENDANCE_SHORTAGE", "code": "RED", "message": "Attendance below 75%. Student must repeat the course semester."}

    # ---------------------------------------------------------------------------
    # FEATURE 355: COURSE MATERIAL UPLOAD MANAGER
    # ---------------------------------------------------------------------------

    def upload_course_material(
        self,
        material_id: str,
        course_code: str,
        title: str,
        category: str,
        file_url: str,
        uploaded_by: str
    ) -> Dict[str, Any]:
        """Register course resource (syllabus, lab manual, notes, templates)."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO course_materials
                    (material_id, course_code, title, category, file_url, uploaded_by, uploaded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (material_id, course_code.upper(), title, category.upper(), file_url, uploaded_by, now_iso))
                conn.commit()
            finally:
                conn.close()
        return {"status": "success", "material_id": material_id, "title": title}

    def list_course_materials(self, course_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """List materials optionally filtered by course."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if course_code:
                cursor.execute("SELECT * FROM course_materials WHERE course_code = ? ORDER BY uploaded_at DESC", (course_code.upper(),))
            else:
                cursor.execute("SELECT * FROM course_materials ORDER BY uploaded_at DESC")
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 356 & 358: ANNOUNCEMENT BROADCAST & DEPARTMENT NOTICE BOARD
    # ---------------------------------------------------------------------------

    def broadcast_announcement(
        self,
        announcement_id: str,
        title: str,
        target_audience: str,
        category: str,
        priority: str,
        author_name: str,
        content: str
    ) -> Dict[str, Any]:
        """Broadcast an administrative notice to selected cohort."""
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO department_announcements
                    (announcement_id, title, target_audience, category, priority, author_name, date, content)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (announcement_id, title, target_audience.upper(), category.upper(), priority.upper(), author_name, now_iso, content))
                conn.commit()
            finally:
                conn.close()
        return {"status": "success", "announcement_id": announcement_id, "title": title}

    def get_department_notices(self) -> List[Dict[str, Any]]:
        """List all notices from the department notice board."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM department_announcements ORDER BY date DESC")
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 357: STUDENT PROGRESS REPORT GENERATOR (ANNA UNIV REG 2023)
    # ---------------------------------------------------------------------------

    def generate_student_progress_dossier(self, student_roll: str) -> Optional[Dict[str, Any]]:
        """
        Generate complete academic progress report card according to Anna University
        Regulation 2023 grading scheme (O, A+, A, B+, B, C, U).
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM student_enrollments WHERE student_roll = ?", (student_roll,))
            records = [dict(r) for r in cursor.fetchall()]

            if not records:
                return None

            student_name = records[0]["student_name"]
            cgpa = records[0]["cgpa"]

            course_grades = []
            total_weighted_points = 0.0

            for rec in records:
                avg_i = (rec["internal_1"] + rec["internal_2"] + rec["internal_3"]) / 3.0
                scaled_internal = (avg_i * 2.0) if avg_i <= 50.0 else avg_i
                total_marks = round(scaled_internal * 0.70 + rec["assignment_score"] * 0.30, 1)

                # Anna Univ Regulation 2023 Grade Mapping
                if total_marks >= 91.0:
                    grade, gp = "O", 10.0
                elif total_marks >= 81.0:
                    grade, gp = "A+", 9.0
                elif total_marks >= 71.0:
                    grade, gp = "A", 8.0
                elif total_marks >= 61.0:
                    grade, gp = "B+", 7.0
                elif total_marks >= 50.0:
                    grade, gp = "B", 6.0
                else:
                    grade, gp = "U", 0.0

                att_status = self.evaluate_attendance_status(rec["attendance_pct"])
                course_grades.append({
                    "course_code": rec["course_code"],
                    "total_marks": total_marks,
                    "letter_grade": grade,
                    "grade_point": gp,
                    "attendance_pct": rec["attendance_pct"],
                    "attendance_status": att_status["badge"]
                })
                total_weighted_points += gp

            gpa = round(total_weighted_points / len(course_grades), 2) if course_grades else 0.0

            return {
                "student_roll": student_roll,
                "student_name": student_name,
                "overall_cgpa": cgpa,
                "semester_gpa": gpa,
                "institution": "Madras Institute of Technology (MIT Campus), Anna University",
                "regulation": "Regulation 2023",
                "department": "Department of Electronics Engineering",
                "courses": course_grades
            }
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 359: TIMETABLE & SCHEDULE MANAGER
    # ---------------------------------------------------------------------------

    def get_timetable(self, day: Optional[str] = None) -> List[Dict[str, Any]]:
        """List lecture timetable slots."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if day:
                cursor.execute("SELECT * FROM timetable_slots WHERE day = ? ORDER BY period ASC", (day.upper(),))
            else:
                cursor.execute("SELECT * FROM timetable_slots ORDER BY day, period ASC")
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 360: FACULTY OFFICE HOURS SCHEDULER
    # ---------------------------------------------------------------------------

    def add_office_slot(
        self,
        slot_id: str,
        faculty_id: str,
        faculty_name: str,
        day: str,
        time: str,
        mode: str,
        room_or_url: str
    ) -> Dict[str, Any]:
        """Add an open office hours counseling slot."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO faculty_office_slots
                    (slot_id, faculty_id, faculty_name, day, time, mode, room_or_url, is_booked, booked_by_roll, booked_by_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0, NULL, NULL)
                """, (slot_id, faculty_id, faculty_name, day.upper(), time, mode.upper(), room_or_url))
                conn.commit()
            finally:
                conn.close()
        return {"status": "success", "slot_id": slot_id}

    def book_office_slot(self, slot_id: str, student_roll: str, student_name: str) -> Dict[str, Any]:
        """Book a faculty office slot."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT is_booked FROM faculty_office_slots WHERE slot_id = ?", (slot_id,))
                slot = cursor.fetchone()
                if not slot:
                    return {"status": "error", "message": "Office slot not found"}
                if slot["is_booked"]:
                    return {"status": "error", "message": "Slot already booked"}

                conn.execute("""
                    UPDATE faculty_office_slots
                    SET is_booked = 1, booked_by_roll = ?, booked_by_name = ?
                    WHERE slot_id = ?
                """, (student_roll, student_name, slot_id))
                conn.commit()
            finally:
                conn.close()
        return {"status": "success", "slot_id": slot_id, "student_roll": student_roll}

    def get_office_slots(self, faculty_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List open or booked office slots."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if faculty_id:
                cursor.execute("SELECT * FROM faculty_office_slots WHERE faculty_id = ? ORDER BY day, time ASC", (faculty_id,))
            else:
                cursor.execute("SELECT * FROM faculty_office_slots ORDER BY day, time ASC")
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()
