"""
========================================================================================
VoltCore Apex Academia - Smart Learning Productivity & Study Management Center
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/learning_productivity_engine.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Lightweight backend productivity manager handling:
    1. Pomodoro Study Sessions (25m, 50m, custom, focus scoring, distraction-free mode).
    2. Learning Streak Tracker (daily streaks, total minutes, sessions, historical heatmap).
    3. Smart Bookmark Manager (subject categorization, tags, resource references).
    4. Spaced Revision Priority Queue (decay interval calculator, urgency scoring).
    5. SQLite WAL-backed fast lookup engine (< 5ms latency, minimal CPU/memory footprint).
========================================================================================
"""

import os
import time
import json
import sqlite3
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")

# Default demo student
DEFAULT_STUDENT_ID = "2023MITEC042"

# Spaced Repetition Spacing Steps (in days)
SPACING_LADDER = [1, 3, 7, 14, 30]


class LearningProductivityEngine:
    """
    High-performance, low-overhead learning productivity and study session manager.
    Optimized for zero-bloat execution and passive thermal profiles.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
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
        """Initializes tables and indexes for learning productivity tracking."""
        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()

            # 1. Study Sessions Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS productivity_study_sessions (
                    session_id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    subject_code TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    session_type TEXT NOT NULL,
                    focus_score INTEGER NOT NULL,
                    notes TEXT,
                    distraction_free_mode INTEGER DEFAULT 0,
                    completed_at TEXT NOT NULL
                );
            """)

            # 2. Learning Streaks Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS productivity_learning_streaks (
                    student_id TEXT PRIMARY KEY,
                    current_streak_days INTEGER DEFAULT 0,
                    longest_streak_days INTEGER DEFAULT 0,
                    total_study_minutes INTEGER DEFAULT 0,
                    total_sessions_completed INTEGER DEFAULT 0,
                    last_active_date TEXT,
                    streak_history_json TEXT DEFAULT '[]',
                    updated_at TEXT
                );
            """)

            # 3. Smart Bookmarks Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS productivity_bookmarks (
                    bookmark_id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    subject_code TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    resource_url TEXT NOT NULL,
                    tags_json TEXT DEFAULT '[]',
                    notes TEXT,
                    priority TEXT DEFAULT 'MEDIUM',
                    created_at TEXT NOT NULL
                );
            """)

            # 4. Spaced Revision Priority Queue Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS productivity_revision_queue (
                    queue_id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    subject_code TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    confidence_level INTEGER DEFAULT 3,
                    last_reviewed_at TEXT NOT NULL,
                    next_review_due TEXT NOT NULL,
                    decay_interval_days INTEGER DEFAULT 3,
                    urgency_score REAL DEFAULT 1.0,
                    status TEXT DEFAULT 'PENDING'
                );
            """)

            # Performance indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_prod_sess_student ON productivity_study_sessions(student_id, completed_at);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_prod_sess_sub ON productivity_study_sessions(subject_code);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_prod_book_student ON productivity_bookmarks(student_id, subject_code);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_prod_rev_student ON productivity_revision_queue(student_id, status);")

            conn.commit()
            self._seed_default_data(conn)
            conn.close()

    def _seed_default_data(self, conn: sqlite3.Connection) -> None:
        """Seeds initial study data and demonstration records if empty."""
        cur = conn.cursor()

        # Seed Streak for 2023MITEC042
        cur.execute("SELECT COUNT(*) FROM productivity_learning_streaks WHERE student_id = ?", (DEFAULT_STUDENT_ID,))
        if cur.fetchone()[0] == 0:
            today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            # Create synthetic history for the past 7 days
            history = [(datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
            cur.execute("""
                INSERT INTO productivity_learning_streaks
                (student_id, current_streak_days, longest_streak_days, total_study_minutes, total_sessions_completed, last_active_date, streak_history_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                DEFAULT_STUDENT_ID,
                7,
                14,
                1420,
                38,
                today_str,
                json.dumps(history),
                datetime.now(timezone.utc).isoformat()
            ))

        # Seed Sample Study Sessions
        cur.execute("SELECT COUNT(*) FROM productivity_study_sessions WHERE student_id = ?", (DEFAULT_STUDENT_ID,))
        if cur.fetchone()[0] == 0:
            sample_sessions = [
                ("SESS_SEED_01", DEFAULT_STUDENT_ID, "EC3352", "FSM State Minimization & Flow Tables", 25, "POMODORO_25", 5, "Completed Mealy to Moore conversion exercises.", 1, (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()),
                ("SESS_SEED_02", DEFAULT_STUDENT_ID, "EC3452", "Poynting Vector & Wave Power Density", 50, "DEEP_WORK_50", 4, "Derived instantaneous and time-average Poynting vector.", 1, (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat()),
                ("SESS_SEED_03", DEFAULT_STUDENT_ID, "EC3451", "Active Butterworth Filter Sallen-Key Topologies", 25, "POMODORO_25", 5, "Calculated cut-off frequencies and Q-factor damping.", 0, (datetime.now(timezone.utc) - timedelta(days=1, hours=2)).isoformat()),
                ("SESS_SEED_04", DEFAULT_STUDENT_ID, "EC3491", "Superheterodyne Receiver IF Image Frequency Rejection", 50, "DEEP_WORK_50", 5, "Plotted tracking curves and calculated IF image response.", 1, (datetime.now(timezone.utc) - timedelta(days=1, hours=6)).isoformat()),
            ]
            cur.executemany("""
                INSERT INTO productivity_study_sessions
                (session_id, student_id, subject_code, topic, duration_minutes, session_type, focus_score, notes, distraction_free_mode, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_sessions)

        # Seed Smart Bookmarks
        cur.execute("SELECT COUNT(*) FROM productivity_bookmarks WHERE student_id = ?", (DEFAULT_STUDENT_ID,))
        if cur.fetchone()[0] == 0:
            sample_bookmarks = [
                ("BOOK_SEED_01", DEFAULT_STUDENT_ID, "EC3352", "Synchronous Sequential Logic Synthesis", "/modules", json.dumps(["digital", "fsm", "verilog"]), "Crucial for Continuous Assessment Test 1 and End-Sem Theory.", "HIGH", datetime.now(timezone.utc).isoformat()),
                ("BOOK_SEED_02", DEFAULT_STUDENT_ID, "EC3452", "Maxwell's Equations Differential & Integral Forms", "/ece-knowledge", json.dumps(["em-fields", "maxwell", "boundary-conditions"]), "Includes vector calculus identities and normal/tangential field transitions.", "HIGH", datetime.now(timezone.utc).isoformat()),
                ("BOOK_SEED_03", DEFAULT_STUDENT_ID, "EC3451", "Op-Amp Inverting/Non-Inverting Active Filters", "/simulation", json.dumps(["analog", "op-amp", "spice"]), "Interactive SPICE simulations for Bode magnitude and phase response.", "MEDIUM", datetime.now(timezone.utc).isoformat()),
                ("BOOK_SEED_04", DEFAULT_STUDENT_ID, "EC3491", "FM Modulation Index & Carson's Bandwidth Rule", "/ece-knowledge", json.dumps(["communication", "fm", "bessel"]), "Bessel function power distribution cheat sheet and calculation examples.", "MEDIUM", datetime.now(timezone.utc).isoformat()),
            ]
            cur.executemany("""
                INSERT INTO productivity_bookmarks
                (bookmark_id, student_id, subject_code, topic, resource_url, tags_json, notes, priority, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_bookmarks)

        # Seed Spaced Revision Queue Items
        cur.execute("SELECT COUNT(*) FROM productivity_revision_queue WHERE student_id = ?", (DEFAULT_STUDENT_ID,))
        if cur.fetchone()[0] == 0:
            sample_queue = [
                ("REV_SEED_01", DEFAULT_STUDENT_ID, "EC3452", "Boundary Conditions for Dielectric-Dielectric Interfaces", 2, (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(), (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(), 3, 2.67, "DUE"),
                ("REV_SEED_02", DEFAULT_STUDENT_ID, "EC3352", "Algorithmic State Machines (ASM) Charts", 4, (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(), (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(), 7, 0.57, "PENDING"),
                ("REV_SEED_03", DEFAULT_STUDENT_ID, "EC3451", "Instrumentation Amplifier 3-Op-Amp CMRR Derivation", 3, (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(), datetime.now(timezone.utc).isoformat(), 3, 3.0, "DUE"),
                ("REV_SEED_04", DEFAULT_STUDENT_ID, "EC3491", "Nyquist Criterion for Zero ISI and Raised Cosine Filter", 5, (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(), (datetime.now(timezone.utc) + timedelta(days=13)).isoformat(), 14, 0.07, "PENDING"),
            ]
            cur.executemany("""
                INSERT INTO productivity_revision_queue
                (queue_id, student_id, subject_code, topic, confidence_level, last_reviewed_at, next_review_due, decay_interval_days, urgency_score, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_queue)

        conn.commit()

    # ====================================================================================
    # 1. STUDY SESSIONS & POMODORO LOGGING
    # ====================================================================================

    def log_study_session(
        self,
        student_id: str,
        subject_code: str,
        topic: str,
        duration_minutes: int,
        session_type: str = "POMODORO_25",
        focus_score: int = 5,
        notes: str = "",
        distraction_free_mode: bool = False,
        completed_at: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Logs a completed study session and atomically recalculates learning streaks.
        """
        student_id = (student_id or DEFAULT_STUDENT_ID).strip()
        subject_code = (subject_code or "ECE_GENERAL").strip().upper()
        topic = (topic or "Untitled Session").strip()
        duration_minutes = max(1, int(duration_minutes))
        focus_score = max(1, min(5, int(focus_score)))
        now_dt = datetime.now(timezone.utc)
        completed_at_iso = completed_at or now_dt.isoformat()
        today_str = completed_at_iso[:10]

        session_id = f"SESS_{int(time.time() * 1000)}"

        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()

            # Insert Session
            cur.execute("""
                INSERT INTO productivity_study_sessions
                (session_id, student_id, subject_code, topic, duration_minutes, session_type, focus_score, notes, distraction_free_mode, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                student_id,
                subject_code,
                topic,
                duration_minutes,
                session_type,
                focus_score,
                notes,
                1 if distraction_free_mode else 0,
                completed_at_iso
            ))

            # Update or Create Streak
            cur.execute("""
                SELECT current_streak_days, longest_streak_days, total_study_minutes, total_sessions_completed, last_active_date, streak_history_json
                FROM productivity_learning_streaks
                WHERE student_id = ?
            """, (student_id,))
            streak_row = cur.fetchone()

            if streak_row:
                current_streak = streak_row["current_streak_days"]
                longest_streak = streak_row["longest_streak_days"]
                total_minutes = streak_row["total_study_minutes"] + duration_minutes
                total_sessions = streak_row["total_sessions_completed"] + 1
                last_active = streak_row["last_active_date"]
                try:
                    history = json.loads(streak_row["streak_history_json"] or "[]")
                except Exception:
                    history = []

                if last_active == today_str:
                    # Already active today: keep streak count unchanged
                    pass
                elif last_active:
                    try:
                        last_date = datetime.strptime(last_active, "%Y-%m-%d").date()
                        curr_date = datetime.strptime(today_str, "%Y-%m-%d").date()
                        diff_days = (curr_date - last_date).days
                        if diff_days == 1:
                            current_streak += 1
                        elif diff_days > 1:
                            current_streak = 1
                    except Exception:
                        current_streak = 1
                else:
                    current_streak = 1

                if current_streak > longest_streak:
                    longest_streak = current_streak

                if today_str not in history:
                    history.append(today_str)
                    if len(history) > 60:
                        history = history[-60:]

                cur.execute("""
                    UPDATE productivity_learning_streaks
                    SET current_streak_days = ?,
                        longest_streak_days = ?,
                        total_study_minutes = ?,
                        total_sessions_completed = ?,
                        last_active_date = ?,
                        streak_history_json = ?,
                        updated_at = ?
                    WHERE student_id = ?
                """, (
                    current_streak,
                    longest_streak,
                    total_minutes,
                    total_sessions,
                    today_str,
                    json.dumps(history),
                    now_dt.isoformat(),
                    student_id
                ))
            else:
                current_streak = 1
                longest_streak = 1
                total_minutes = duration_minutes
                total_sessions = 1
                history = [today_str]
                cur.execute("""
                    INSERT INTO productivity_learning_streaks
                    (student_id, current_streak_days, longest_streak_days, total_study_minutes, total_sessions_completed, last_active_date, streak_history_json, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    student_id,
                    current_streak,
                    longest_streak,
                    total_minutes,
                    total_sessions,
                    today_str,
                    json.dumps(history),
                    now_dt.isoformat()
                ))

            conn.commit()
            conn.close()

        return {
            "status": "SUCCESS",
            "session_id": session_id,
            "student_id": student_id,
            "subject_code": subject_code,
            "duration_minutes": duration_minutes,
            "current_streak_days": current_streak,
            "longest_streak_days": longest_streak,
            "total_study_minutes": total_minutes,
            "total_sessions_completed": total_sessions
        }

    def get_study_sessions(self, student_id: str = DEFAULT_STUDENT_ID, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns recent completed study sessions for a student."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT session_id, student_id, subject_code, topic, duration_minutes,
                   session_type, focus_score, notes, distraction_free_mode, completed_at
            FROM productivity_study_sessions
            WHERE student_id = ?
            ORDER BY completed_at DESC
            LIMIT ?
        """, (student_id, limit))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    # ====================================================================================
    # 2. LEARNING STREAKS & METRICS
    # ====================================================================================

    def get_streak_metrics(self, student_id: str = DEFAULT_STUDENT_ID) -> Dict[str, Any]:
        """Returns student streak metrics, study totals, and recent activity heatmap."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT student_id, current_streak_days, longest_streak_days,
                   total_study_minutes, total_sessions_completed, last_active_date,
                   streak_history_json, updated_at
            FROM productivity_learning_streaks
            WHERE student_id = ?
        """, (student_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return {
                "student_id": student_id,
                "current_streak_days": 0,
                "longest_streak_days": 0,
                "total_study_minutes": 0,
                "total_study_hours": 0.0,
                "total_sessions_completed": 0,
                "last_active_date": None,
                "streak_history": [],
                "is_active_today": False
            }

        res = dict(row)
        try:
            res["streak_history"] = json.loads(res.pop("streak_history_json") or "[]")
        except Exception:
            res["streak_history"] = []

        res["total_study_hours"] = round(res["total_study_minutes"] / 60.0, 1)
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        res["is_active_today"] = (res.get("last_active_date") == today_str)

        return res

    # ====================================================================================
    # 3. SMART BOOKMARKS
    # ====================================================================================

    def get_bookmarks(self, student_id: str = DEFAULT_STUDENT_ID, subject_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns smart bookmarks for a student, optionally filtered by subject code."""
        conn = self._get_connection()
        cur = conn.cursor()
        if subject_code:
            cur.execute("""
                SELECT bookmark_id, student_id, subject_code, topic, resource_url, tags_json, notes, priority, created_at
                FROM productivity_bookmarks
                WHERE student_id = ? AND subject_code = ?
                ORDER BY created_at DESC
            """, (student_id, subject_code))
        else:
            cur.execute("""
                SELECT bookmark_id, student_id, subject_code, topic, resource_url, tags_json, notes, priority, created_at
                FROM productivity_bookmarks
                WHERE student_id = ?
                ORDER BY created_at DESC
            """, (student_id,))

        raw_rows = cur.fetchall()
        conn.close()

        bookmarks = []
        for r in raw_rows:
            item = dict(r)
            try:
                item["tags"] = json.loads(item.pop("tags_json") or "[]")
            except Exception:
                item["tags"] = []
            bookmarks.append(item)

        return bookmarks

    def add_bookmark(
        self,
        student_id: str,
        subject_code: str,
        topic: str,
        resource_url: str,
        tags: Optional[List[str]] = None,
        notes: str = "",
        priority: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """Adds a smart bookmark for quick revision access."""
        bookmark_id = f"BOOK_{int(time.time() * 1000)}"
        tags_json = json.dumps(tags or [])
        created_at = datetime.now(timezone.utc).isoformat()

        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO productivity_bookmarks
                (bookmark_id, student_id, subject_code, topic, resource_url, tags_json, notes, priority, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bookmark_id,
                student_id or DEFAULT_STUDENT_ID,
                subject_code.upper(),
                topic,
                resource_url,
                tags_json,
                notes,
                priority.upper(),
                created_at
            ))
            conn.commit()
            conn.close()

        return {
            "status": "SUCCESS",
            "bookmark_id": bookmark_id,
            "topic": topic,
            "subject_code": subject_code
        }

    def delete_bookmark(self, bookmark_id: str, student_id: str = DEFAULT_STUDENT_ID) -> bool:
        """Deletes a smart bookmark."""
        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("""
                DELETE FROM productivity_bookmarks
                WHERE bookmark_id = ? AND student_id = ?
            """, (bookmark_id, student_id))
            affected = cur.rowcount
            conn.commit()
            conn.close()
        return affected > 0

    # ====================================================================================
    # 4. SPACED REVISION PRIORITY QUEUE
    # ====================================================================================

    def _calculate_urgency(self, last_reviewed_iso: str, decay_interval_days: int, confidence_level: int) -> tuple[float, str]:
        """Calculates urgency score and status based on spaced repetition decay."""
        now_dt = datetime.now(timezone.utc)
        try:
            last_dt = datetime.fromisoformat(last_reviewed_iso.replace("Z", "+00:00"))
        except Exception:
            last_dt = now_dt - timedelta(days=decay_interval_days)

        days_elapsed = max(0, (now_dt - last_dt).total_seconds() / 86400.0)
        interval = max(1, decay_interval_days)
        decay_factor = days_elapsed / float(interval)
        # Urgency is proportional to elapsed ratio and inverted confidence
        urgency = round(decay_factor * (6.0 - max(1, min(5, confidence_level))), 2)

        status = "DUE" if days_elapsed >= interval else "PENDING"
        return urgency, status

    def get_revision_queue(self, student_id: str = DEFAULT_STUDENT_ID) -> List[Dict[str, Any]]:
        """Returns the dynamic revision queue sorted by urgency score descending."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT queue_id, student_id, subject_code, topic, confidence_level,
                   last_reviewed_at, next_review_due, decay_interval_days, urgency_score, status
            FROM productivity_revision_queue
            WHERE student_id = ?
        """, (student_id,))
        raw_rows = [dict(r) for r in cur.fetchall()]
        conn.close()

        queue = []
        for item in raw_rows:
            # Recalculate dynamic urgency score in real-time
            urgency, status = self._calculate_urgency(
                item["last_reviewed_at"],
                item["decay_interval_days"],
                item["confidence_level"]
            )
            item["urgency_score"] = urgency
            item["status"] = status
            queue.append(item)

        # Sort by urgency score descending
        queue.sort(key=lambda x: x["urgency_score"], reverse=True)
        return queue

    def add_revision_item(
        self,
        student_id: str,
        subject_code: str,
        topic: str,
        confidence_level: int = 3,
        initial_interval_days: int = 3
    ) -> Dict[str, Any]:
        """Adds a new topic to the student's spaced revision queue."""
        queue_id = f"REV_{int(time.time() * 1000)}"
        now_dt = datetime.now(timezone.utc)
        last_reviewed_at = now_dt.isoformat()
        next_review_due = (now_dt + timedelta(days=initial_interval_days)).isoformat()
        urgency, status = self._calculate_urgency(last_reviewed_at, initial_interval_days, confidence_level)

        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO productivity_revision_queue
                (queue_id, student_id, subject_code, topic, confidence_level, last_reviewed_at, next_review_due, decay_interval_days, urgency_score, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                queue_id,
                student_id or DEFAULT_STUDENT_ID,
                subject_code.upper(),
                topic,
                confidence_level,
                last_reviewed_at,
                next_review_due,
                initial_interval_days,
                urgency,
                status
            ))
            conn.commit()
            conn.close()

        return {
            "status": "SUCCESS",
            "queue_id": queue_id,
            "topic": topic,
            "next_review_due": next_review_due
        }

    def update_revision_item(
        self,
        queue_id: str,
        student_id: str,
        confidence_level: int
    ) -> Dict[str, Any]:
        """
        Marks a revision item as reviewed, updates confidence level, and steps through the spacing ladder.
        """
        confidence_level = max(1, min(5, int(confidence_level)))
        now_dt = datetime.now(timezone.utc)

        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT decay_interval_days FROM productivity_revision_queue
                WHERE queue_id = ? AND student_id = ?
            """, (queue_id, student_id))
            row = cur.fetchone()

            if not row:
                conn.close()
                return {"status": "ERROR", "message": "Revision item not found"}

            curr_interval = row["decay_interval_days"]

            # Advance or reset ladder based on confidence
            if confidence_level >= 4:
                # Advance ladder
                next_interval = 30
                for step in SPACING_LADDER:
                    if step > curr_interval:
                        next_interval = step
                        break
            elif confidence_level == 3:
                # Maintain or step up slightly
                next_interval = max(curr_interval, 3)
            else:
                # Reset to 1 day for low confidence
                next_interval = 1

            last_reviewed_at = now_dt.isoformat()
            next_review_due = (now_dt + timedelta(days=next_interval)).isoformat()
            urgency, status = self._calculate_urgency(last_reviewed_at, next_interval, confidence_level)

            cur.execute("""
                UPDATE productivity_revision_queue
                SET confidence_level = ?,
                    last_reviewed_at = ?,
                    next_review_due = ?,
                    decay_interval_days = ?,
                    urgency_score = ?,
                    status = ?
                WHERE queue_id = ? AND student_id = ?
            """, (
                confidence_level,
                last_reviewed_at,
                next_review_due,
                next_interval,
                urgency,
                status,
                queue_id,
                student_id
            ))
            conn.commit()
            conn.close()

        return {
            "status": "SUCCESS",
            "queue_id": queue_id,
            "new_interval_days": next_interval,
            "confidence_level": confidence_level,
            "next_review_due": next_review_due
        }

    # ====================================================================================
    # 5. PRODUCTIVITY OVERVIEW AGGREGATOR
    # ====================================================================================

    def get_productivity_overview(self, student_id: str = DEFAULT_STUDENT_ID) -> Dict[str, Any]:
        """Aggregates high-level metrics for dashboard cards (< 5ms response time)."""
        streak_data = self.get_streak_metrics(student_id)
        sessions = self.get_study_sessions(student_id, limit=100)
        bookmarks = self.get_bookmarks(student_id)
        revision_items = self.get_revision_queue(student_id)

        # Compute subject time distribution
        subject_dist: Dict[str, int] = {}
        for s in sessions:
            sub = s["subject_code"]
            subject_dist[sub] = subject_dist.get(sub, 0) + s["duration_minutes"]

        # Due revision count
        due_count = sum(1 for item in revision_items if item["status"] == "DUE")

        return {
            "student_id": student_id,
            "streak": streak_data,
            "total_study_minutes": streak_data.get("total_study_minutes", 0),
            "total_study_hours": streak_data.get("total_study_hours", 0.0),
            "total_sessions": streak_data.get("total_sessions_completed", 0),
            "due_revisions_count": due_count,
            "total_bookmarks_count": len(bookmarks),
            "subject_distribution_minutes": subject_dist,
            "recent_sessions": sessions[:5],
            "top_revision_items": revision_items[:4]
        }

    def reset_student_streak_admin(self, student_id: str, actor_role: str) -> Dict[str, Any]:
        """Admin-only reset mechanism for streaks."""
        if actor_role not in ["Admin", "Faculty"]:
            return {"status": "FORBIDDEN", "message": "Only Administrators or Faculty may reset student streak ledgers."}

        with self._lock:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE productivity_learning_streaks
                SET current_streak_days = 0,
                    last_active_date = NULL,
                    updated_at = ?
                WHERE student_id = ?
            """, (datetime.now(timezone.utc).isoformat(), student_id))
            conn.commit()
            conn.close()

        return {"status": "SUCCESS", "message": f"Streak reset for student {student_id}"}


# Singleton instance for system-wide low-overhead dispatch
learning_productivity_engine = LearningProductivityEngine()

