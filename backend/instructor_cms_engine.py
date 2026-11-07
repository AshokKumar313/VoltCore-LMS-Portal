"""
========================================================================================
VoltCore Apex Academia - Enterprise Instructor & CMS Management Engine
Module: backend/instructor_cms_engine.py
Platform Lead: Ashok Kumar A
Standards: Autonomous Engineering Cluster • Outcome-Based Education (OBE) • Bloom's Taxonomy
Architecture: SQLite WAL Mode • RBAC Authorization • Passive CPU Footprint
========================================================================================
"""

import os
import json
import sqlite3
import datetime
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")

# Permitted RBAC Roles
ROLES_PRIVILEGED = {"Admin", "Faculty", "Instructor", "Platform-Lead"}
ROLES_EVALUATOR = {"Admin", "Faculty", "Instructor", "Platform-Lead", "TeachingAssistant"}
ROLES_STUDENT = {"Student"}


class InstructorCmsEngine:
    """
    Enterprise Instructor Content Management System:
      - Role-Based Access Control (RBAC) verification for administrative actions
      - Course publishing studio with modular syllabus, OBE mapping & hardware targets
      - Student lab report evaluation and AI code reviewer verdict overrides
      - Examination question bank manager with Bloom's Taxonomy tagging
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self):
        conn = self._get_connection()
        try:
            # 1. Published Courses Catalog
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cms_published_courses (
                    course_code TEXT PRIMARY KEY,
                    course_name TEXT NOT NULL,
                    department TEXT NOT NULL,
                    semester INTEGER NOT NULL,
                    credits INTEGER NOT NULL,
                    instructor_id TEXT NOT NULL,
                    instructor_name TEXT NOT NULL,
                    syllabus_modules_json TEXT NOT NULL,
                    hardware_targets_json TEXT NOT NULL,
                    prerequisites_json TEXT,
                    status TEXT DEFAULT 'PUBLISHED',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 2. Lab Report Evaluations & AI Overrides
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cms_report_reviews (
                    review_id TEXT PRIMARY KEY,
                    report_id TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    course_code TEXT NOT NULL,
                    original_ai_verdict TEXT NOT NULL,
                    faculty_override_verdict TEXT NOT NULL,
                    adjusted_score REAL NOT NULL,
                    max_score REAL DEFAULT 100.0,
                    reviewer_id TEXT NOT NULL,
                    reviewer_role TEXT NOT NULL,
                    faculty_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 3. Examination Question Bank
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cms_exam_question_bank (
                    question_id TEXT PRIMARY KEY,
                    course_code TEXT NOT NULL,
                    section TEXT NOT NULL,
                    course_outcome TEXT NOT NULL,
                    bloom_level TEXT NOT NULL,
                    marks INTEGER NOT NULL,
                    question_type TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    options_json TEXT,
                    correct_answer TEXT NOT NULL,
                    tolerance REAL DEFAULT 0.0,
                    derivation TEXT,
                    distractor TEXT,
                    created_by TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 4. Security & Audit Trail
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cms_audit_logs (
                    log_id TEXT PRIMARY KEY,
                    actor_id TEXT NOT NULL,
                    actor_role TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # RBAC AUTHORIZATION CHECK
    # ---------------------------------------------------------------------------

    def verify_permission(self, actor_role: str, action: str) -> bool:
        """
        Verifies whether actor_role is authorized to execute action.
        """
        role_clean = (actor_role or "Student").strip()
        if action in ("PUBLISH_COURSE", "OVERRIDE_VERDICT", "MANAGE_QUESTION_BANK"):
            return role_clean in ROLES_PRIVILEGED
        if action in ("REVIEW_REPORT", "VIEW_PENDING_REPORTS"):
            return role_clean in ROLES_EVALUATOR
        return False

    def _log_audit_event(
        self,
        actor_id: str,
        actor_role: str,
        action: str,
        resource_id: str,
        status: str,
        details: str = ""
    ):
        conn = self._get_connection()
        try:
            log_id = f"AUDIT_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}_{os.urandom(2).hex()}"
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("""
                INSERT INTO cms_audit_logs
                (log_id, actor_id, actor_role, action, resource_id, status, details, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (log_id, actor_id, actor_role, action, resource_id, status, details, now_str))
            conn.commit()
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # COURSE PUBLISHING STUDIO
    # ---------------------------------------------------------------------------

    def publish_course(self, payload: Dict[str, Any], actor_role: str = "Faculty") -> Dict[str, Any]:
        """
        Publishes a new engineering course to the curriculum repository.
        Requires Faculty or Admin privileges.
        """
        instructor_id = payload.get("instructor_id", "FAC_042")
        if not self.verify_permission(actor_role, "PUBLISH_COURSE"):
            self._log_audit_event(
                instructor_id, actor_role, "PUBLISH_COURSE",
                payload.get("course_code", "UNKNOWN"), "DENIED",
                "Unauthorized course publishing attempt by unprivileged role."
            )
            return {
                "status": "FORBIDDEN",
                "error": "Insufficient permissions. Course publishing requires Faculty or Admin credentials."
            }

        course_code = payload.get("course_code", "EC3701").strip().upper()
        course_name = payload.get("course_name", "Advanced Embedded Systems Architecture")
        dept = payload.get("department", "Department of Electronics Engineering")
        sem = int(payload.get("semester", 5))
        credits_val = int(payload.get("credits", 4))
        instructor_name = payload.get("instructor_name", "Ashok Kumar A")

        syllabus_modules = payload.get("syllabus_modules", [
            {"module_id": "MOD_01", "title": "ARM Cortex-M4 NVIC & Concurrency", "bloom_level": "Level 4: Analyze"},
            {"module_id": "MOD_02", "title": "Circular DMA & High-Speed ADC Streaming", "bloom_level": "Level 4: Analyze"},
            {"module_id": "MOD_03", "title": "FreeRTOS Preemptive Schedulers & PendSV", "bloom_level": "Level 5: Evaluate"}
        ])

        hardware_targets = payload.get("hardware_targets", ["STM32F401RE", "ESP32", "Artix-7 FPGA"])
        prerequisites = payload.get("prerequisites", ["EC3451 Linear Integrated Circuits", "EC3352 Digital Systems"])

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = self._get_connection()
        try:
            conn.execute("""
                INSERT OR REPLACE INTO cms_published_courses
                (course_code, course_name, department, semester, credits, instructor_id, instructor_name,
                 syllabus_modules_json, hardware_targets_json, prerequisites_json, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PUBLISHED', ?, ?);
            """, (
                course_code, course_name, dept, sem, credits_val, instructor_id, instructor_name,
                json.dumps(syllabus_modules), json.dumps(hardware_targets), json.dumps(prerequisites),
                now_str, now_str
            ))
            conn.commit()
        finally:
            conn.close()

        self._log_audit_event(
            instructor_id, actor_role, "PUBLISH_COURSE", course_code, "SUCCESS",
            f"Course {course_code} successfully published."
        )

        return {
            "status": "SUCCESS",
            "course_code": course_code,
            "course_name": course_name,
            "credits": credits_val,
            "modules_count": len(syllabus_modules),
            "hardware_targets": hardware_targets,
            "published_at": now_str
        }

    def get_published_courses(self) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT course_code, course_name, department, semester, credits, instructor_name,
                       syllabus_modules_json, hardware_targets_json, status, updated_at
                FROM cms_published_courses
                ORDER BY course_code ASC;
            """)
            rows = cur.fetchall()
            return [{
                "course_code": r[0],
                "course_name": r[1],
                "department": r[2],
                "semester": r[3],
                "credits": r[4],
                "instructor_name": r[5],
                "syllabus_modules": json.loads(r[6]),
                "hardware_targets": json.loads(r[7]),
                "status": r[8],
                "updated_at": r[9]
            } for r in rows]
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # LAB REPORT REVIEW & AI VERDICT OVERRIDES
    # ---------------------------------------------------------------------------

    def review_and_override_report(
        self,
        payload: Dict[str, Any],
        actor_role: str = "Faculty"
    ) -> Dict[str, Any]:
        """
        Allows faculty to override automated AI code review verdicts on student lab submissions.
        """
        reviewer_id = payload.get("reviewer_id", "FAC_042")
        if not self.verify_permission(actor_role, "OVERRIDE_VERDICT"):
            self._log_audit_event(
                reviewer_id, actor_role, "OVERRIDE_VERDICT",
                payload.get("report_id", "UNKNOWN"), "DENIED",
                "Unauthorized override attempt by non-faculty role."
            )
            return {
                "status": "FORBIDDEN",
                "error": "Insufficient permissions. Verdict overrides require Faculty credentials."
            }

        report_id = payload.get("report_id", "REP_STM32_01")
        student_id = payload.get("student_id", "2023MITEC042")
        course_code = payload.get("course_code", "EC3701")
        ai_verdict = payload.get("original_ai_verdict", "NEEDS_REVISION")
        override_verdict = payload.get("faculty_override_verdict", "APPROVED")
        adj_score = float(payload.get("adjusted_score", 96.0))
        max_score = float(payload.get("max_score", 100.0))
        notes = payload.get("faculty_notes", "Faculty override: verified hardware oscilloscope captures show race condition avoided.")

        review_id = f"REV_{report_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}_{os.urandom(2).hex()}"
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = self._get_connection()
        try:
            conn.execute("""
                INSERT INTO cms_report_reviews
                (review_id, report_id, student_id, course_code, original_ai_verdict,
                 faculty_override_verdict, adjusted_score, max_score, reviewer_id, reviewer_role, faculty_notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                review_id, report_id, student_id, course_code, ai_verdict,
                override_verdict, adj_score, max_score, reviewer_id, actor_role, notes, now_str
            ))
            conn.commit()
        finally:
            conn.close()

        self._log_audit_event(
            reviewer_id, actor_role, "OVERRIDE_VERDICT", report_id, "SUCCESS",
            f"Overrode {ai_verdict} -> {override_verdict} (Score: {adj_score}/{max_score})"
        )

        return {
            "status": "SUCCESS",
            "review_id": review_id,
            "report_id": report_id,
            "student_id": student_id,
            "override_verdict": override_verdict,
            "adjusted_score": adj_score,
            "max_score": max_score,
            "reviewer_id": reviewer_id,
            "notes": notes,
            "reviewed_at": now_str
        }

    # ---------------------------------------------------------------------------
    # EXAMINATION QUESTION BANK MANAGEMENT
    # ---------------------------------------------------------------------------

    def add_question_to_bank(
        self,
        payload: Dict[str, Any],
        actor_role: str = "Faculty"
    ) -> Dict[str, Any]:
        """
        Adds a new verified technical question to the examination bank.
        """
        creator_id = payload.get("created_by", "FAC_042")
        if not self.verify_permission(actor_role, "MANAGE_QUESTION_BANK"):
            self._log_audit_event(
                creator_id, actor_role, "MANAGE_QUESTION_BANK",
                payload.get("question_id", "UNKNOWN"), "DENIED",
                "Unauthorized question creation attempt by unprivileged role."
            )
            return {
                "status": "FORBIDDEN",
                "error": "Insufficient permissions. Question bank management requires Faculty credentials."
            }

        qid = payload.get("question_id") or f"Q_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        course_code = payload.get("course_code", "EC3701").strip().upper()
        section = payload.get("section", "sec_embedded")
        co = payload.get("course_outcome", "CO4")
        bloom = payload.get("bloom_level", "Level 4: Analyze")
        marks = int(payload.get("marks", 2))
        qtype = payload.get("question_type", "MCQ")
        qtext = payload.get("question_text", "Explain Cortex-M DMA FIFO threshold configuration.")
        options = payload.get("options", [
            {"key": "A", "text": "Direct mode (single transfer per request)"},
            {"key": "B", "text": "1/4 FIFO full threshold"},
            {"key": "C", "text": "1/2 FIFO full threshold"},
            {"key": "D", "text": "Full FIFO threshold burst"}
        ])
        ans = str(payload.get("correct_answer", "C"))
        tol = float(payload.get("tolerance", 0.0))
        derivation = payload.get("derivation", "FIFO threshold configures DMA flow controller burst trigger.")
        distractor = payload.get("distractor", "Direct mode bypasses internal 16-byte FIFO.")
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = self._get_connection()
        try:
            conn.execute("""
                INSERT OR REPLACE INTO cms_exam_question_bank
                (question_id, course_code, section, course_outcome, bloom_level, marks, question_type,
                 question_text, options_json, correct_answer, tolerance, derivation, distractor, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                qid, course_code, section, co, bloom, marks, qtype,
                qtext, json.dumps(options), ans, tol, derivation, distractor, creator_id, now_str
            ))
            conn.commit()
        finally:
            conn.close()

        self._log_audit_event(
            creator_id, actor_role, "MANAGE_QUESTION_BANK", qid, "SUCCESS",
            f"Added {qtype} question ({co}, {marks} marks)"
        )

        return {
            "status": "SUCCESS",
            "question_id": qid,
            "course_code": course_code,
            "section": section,
            "course_outcome": co,
            "bloom_level": bloom,
            "marks": marks,
            "question_type": qtype,
            "created_at": now_str
        }

    def get_questions_by_course(self, course_code: str) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT question_id, course_code, section, course_outcome, bloom_level, marks,
                       question_type, question_text, options_json, correct_answer, tolerance, derivation, distractor
                FROM cms_exam_question_bank
                WHERE course_code = ?
                ORDER BY course_outcome ASC, question_id ASC;
            """, (course_code.strip().upper(),))
            rows = cur.fetchall()
            return [{
                "question_id": r[0],
                "course_code": r[1],
                "section": r[2],
                "course_outcome": r[3],
                "bloom_level": r[4],
                "marks": r[5],
                "question_type": r[6],
                "question_text": r[7],
                "options": json.loads(r[8]) if r[8] else [],
                "correct_answer": r[9],
                "tolerance": r[10],
                "derivation": r[11],
                "distractor": r[12]
            } for r in rows]
        finally:
            conn.close()


instructor_cms_engine = InstructorCmsEngine()
