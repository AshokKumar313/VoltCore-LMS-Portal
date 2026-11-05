"""
========================================================================================
VoltCore Apex Academia - Student Experience, Portfolio & Collaboration Hub
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/collaboration_hub.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Lightweight backend manager for student engineering portfolios, peer code reviews,
  study group matching, and academic leaderboard XP tracking backed by SQLite WAL tables.
========================================================================================
"""

import os
import time
import sqlite3
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")

# MIT Campus ECE Regulation 2023 Default Students
DEFAULT_LEADERBOARD_DATA = [
    {
        "student_id": "2023MITEC042",
        "name": "Ashok Kumar A",
        "roll_no": "2023MITEC042",
        "xp": 4850,
        "streak_days": 14,
        "department": "Electronics Engineering",
        "institution": "MIT Campus, Anna University",
        "tier": "Silicon Grandmaster",
        "badges": ["HIL Test Lead", "TinyML Deployer", "RTOS Kernel Master", "Silicon Architect"]
    },
    {
        "student_id": "2023MITEC018",
        "name": "Priya Swaminathan",
        "roll_no": "2023MITEC018",
        "xp": 3920,
        "streak_days": 11,
        "department": "Electronics Engineering",
        "institution": "MIT Campus, Anna University",
        "tier": "Firmware Architect",
        "badges": ["Edge AI Specialist", "DMA Optimization"]
    },
    {
        "student_id": "2023MITEC055",
        "name": "Karthik Ramanathan",
        "roll_no": "2023MITEC055",
        "xp": 3410,
        "streak_days": 8,
        "department": "Electronics Engineering",
        "institution": "MIT Campus, Anna University",
        "tier": "Embedded Specialist",
        "badges": ["RISC-V Verilog", "Wokwi Speedrunner"]
    },
    {
        "student_id": "2023MITEC012",
        "name": "Deepa Balasubramanian",
        "roll_no": "2023MITEC012",
        "xp": 2890,
        "streak_days": 9,
        "department": "Electronics Engineering",
        "institution": "MIT Campus, Anna University",
        "tier": "Embedded Specialist",
        "badges": ["Analog Signal Integrity", "SPICE Solver"]
    },
    {
        "student_id": "2023MITEC061",
        "name": "Vigneshwaran K",
        "roll_no": "2023MITEC061",
        "xp": 2450,
        "streak_days": 5,
        "department": "Electronics Engineering",
        "institution": "MIT Campus, Anna University",
        "tier": "Circuit Novice",
        "badges": ["I2C Bus Analyzer"]
    }
]

# Initial Portfolio Projects
DEFAULT_PORTFOLIO_PROJECTS = [
    {
        "project_id": "PRJ-MIT-001",
        "student_id": "2023MITEC042",
        "student_name": "Ashok Kumar A",
        "title": "Dual-Core FreeRTOS Drone Flight Controller",
        "description": "High-rate PID stabilization on STM32H7 with hardware DMA SPI telemetry to ground station. Verified via HIL Test Bench 304.",
        "domain": "Embedded Firmware",
        "tech_stack": ["STM32H7", "FreeRTOS", "DMA", "SPI", "MPU6050"],
        "repo_url": "https://github.com/AshokKumar313/VoltCore-LMS-Portal",
        "wokwi_url": "https://wokwi.com/projects/voltcore-flight-controller",
        "hardware_hil_verified": True,
        "status": "FEATURED",
        "likes_count": 38,
        "xp_reward": 200,
        "created_at": "2026-11-01T10:00:00Z"
    },
    {
        "project_id": "PRJ-MIT-002",
        "student_id": "2023MITEC018",
        "student_name": "Priya Swaminathan",
        "title": "Edge AI Railway Track Micro-Crack Detector",
        "description": "Quantized INT8 CNN model running on ESP32-S3 LittleFS partition with auto-upload to MQTT cloud.",
        "domain": "IoT & TinyML",
        "tech_stack": ["ESP32-S3", "TensorFlow Lite", "LittleFS", "MQTT"],
        "repo_url": "https://github.com/AshokKumar313/railway-edge-detector",
        "wokwi_url": "https://wokwi.com/projects/railway-crack-detector",
        "hardware_hil_verified": True,
        "status": "VERIFIED",
        "likes_count": 27,
        "xp_reward": 180,
        "created_at": "2026-11-02T14:30:00Z"
    },
    {
        "project_id": "PRJ-MIT-003",
        "student_id": "2023MITEC055",
        "student_name": "Karthik Ramanathan",
        "title": "RV32I 5-Stage Pipelined RISC-V Core with Hazard Unit",
        "description": "Synthesizable Verilog HDL implementing Harvard architecture with ALU data forwarding and branch hazard stalls.",
        "domain": "VLSI & FPGA",
        "tech_stack": ["Verilog", "RISC-V", "Xilinx Vivado", "ModelSim"],
        "repo_url": "https://github.com/AshokKumar313/rv32i-pipelined-core",
        "wokwi_url": "",
        "hardware_hil_verified": False,
        "status": "VERIFIED",
        "likes_count": 21,
        "xp_reward": 180,
        "created_at": "2026-11-03T11:15:00Z"
    }
]

# Initial Study Groups
DEFAULT_STUDY_GROUPS = [
    {
        "group_id": "GRP-EC8702-01",
        "group_name": "EC8702 Embedded RTOS Core Fellowship",
        "subject_code": "EC8702",
        "topic": "Priority Inversion, Semaphore Mutexes & FreeRTOS Heap_4 Analysis",
        "leader_id": "2023MITEC042",
        "leader_name": "Ashok Kumar A",
        "schedule_slot": "Tue & Thu 17:30 - 19:00 IST",
        "meeting_link": "https://meet.mitindia.edu/voltcore-rtos-sprint",
        "max_members": 6,
        "members": ["2023MITEC042", "2023MITEC018", "2023MITEC055"]
    },
    {
        "group_id": "GRP-GATE-02",
        "group_name": "GATE ECE 2024 Analog & Semiconductor Cohort",
        "subject_code": "GATE-ECE",
        "topic": "Small-Signal Hybrid-Pi BJT/MOSFET & Nyquist Stability Derivations",
        "leader_id": "2023MITEC018",
        "leader_name": "Priya Swaminathan",
        "schedule_slot": "Sat & Sun 10:00 - 12:00 IST",
        "meeting_link": "https://meet.mitindia.edu/gate-ece-analog-deepdive",
        "max_members": 8,
        "members": ["2023MITEC018", "2023MITEC012", "2023MITEC061"]
    }
]


class CollaborationHub:
    """
    Thread-safe student collaboration manager and academic leaderboard engine.
    Persists data in SQLite with Write-Ahead Logging (WAL) for high concurrency.
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
        """Initializes tables for portfolios, reviews, study groups, and leaderboards."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS student_portfolios (
                        project_id TEXT PRIMARY KEY,
                        student_id TEXT NOT NULL,
                        student_name TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        domain TEXT NOT NULL,
                        tech_stack TEXT NOT NULL,
                        repo_url TEXT,
                        wokwi_url TEXT,
                        hardware_hil_verified INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'SUBMITTED',
                        likes_count INTEGER DEFAULT 0,
                        xp_reward INTEGER DEFAULT 200,
                        created_at TEXT NOT NULL
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS peer_reviews (
                        review_id TEXT PRIMARY KEY,
                        project_id TEXT NOT NULL,
                        reviewer_id TEXT NOT NULL,
                        reviewer_name TEXT NOT NULL,
                        code_quality REAL NOT NULL,
                        timing_safety REAL NOT NULL,
                        memory_efficiency REAL NOT NULL,
                        test_coverage REAL NOT NULL,
                        overall_score REAL NOT NULL,
                        comments TEXT NOT NULL,
                        status TEXT NOT NULL,
                        xp_awarded INTEGER DEFAULT 150,
                        created_at TEXT NOT NULL
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS study_groups (
                        group_id TEXT PRIMARY KEY,
                        group_name TEXT NOT NULL,
                        subject_code TEXT NOT NULL,
                        topic TEXT NOT NULL,
                        leader_id TEXT NOT NULL,
                        leader_name TEXT NOT NULL,
                        schedule_slot TEXT NOT NULL,
                        meeting_link TEXT NOT NULL,
                        max_members INTEGER NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS study_group_members (
                        group_id TEXT NOT NULL,
                        student_id TEXT NOT NULL,
                        student_name TEXT NOT NULL,
                        joined_at TEXT NOT NULL,
                        PRIMARY KEY (group_id, student_id)
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS leaderboard_xp (
                        student_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        roll_no TEXT NOT NULL,
                        xp INTEGER NOT NULL,
                        streak_days INTEGER DEFAULT 1,
                        department TEXT NOT NULL,
                        institution TEXT NOT NULL,
                        tier TEXT NOT NULL,
                        badges TEXT NOT NULL
                    );
                """)
                conn.commit()
            finally:
                conn.close()

    def _seed_initial_records(self):
        """Seeds default portfolios, groups, and leaderboard rankings if empty."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                # 1. Leaderboard seeding
                cur.execute("SELECT COUNT(*) FROM leaderboard_xp;")
                if cur.fetchone()[0] == 0:
                    for s in DEFAULT_LEADERBOARD_DATA:
                        cur.execute("""
                            INSERT INTO leaderboard_xp 
                            (student_id, name, roll_no, xp, streak_days, department, institution, tier, badges)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, (
                            s["student_id"], s["name"], s["roll_no"], s["xp"],
                            s["streak_days"], s["department"], s["institution"],
                            s["tier"], ",".join(s["badges"])
                        ))

                # 2. Portfolio seeding
                cur.execute("SELECT COUNT(*) FROM student_portfolios;")
                if cur.fetchone()[0] == 0:
                    for p in DEFAULT_PORTFOLIO_PROJECTS:
                        cur.execute("""
                            INSERT INTO student_portfolios
                            (project_id, student_id, student_name, title, description, domain,
                             tech_stack, repo_url, wokwi_url, hardware_hil_verified, status,
                             likes_count, xp_reward, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, (
                            p["project_id"], p["student_id"], p["student_name"], p["title"],
                            p["description"], p["domain"], ",".join(p["tech_stack"]),
                            p["repo_url"], p["wokwi_url"], 1 if p["hardware_hil_verified"] else 0,
                            p["status"], p["likes_count"], p["xp_reward"], p["created_at"]
                        ))

                # 3. Study groups seeding
                cur.execute("SELECT COUNT(*) FROM study_groups;")
                if cur.fetchone()[0] == 0:
                    for g in DEFAULT_STUDY_GROUPS:
                        now_str = datetime.now(timezone.utc).isoformat()
                        cur.execute("""
                            INSERT INTO study_groups
                            (group_id, group_name, subject_code, topic, leader_id, leader_name,
                             schedule_slot, meeting_link, max_members, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, (
                            g["group_id"], g["group_name"], g["subject_code"], g["topic"],
                            g["leader_id"], g["leader_name"], g["schedule_slot"],
                            g["meeting_link"], g["max_members"], now_str
                        ))
                        for member_id in g["members"]:
                            cur.execute("""
                                INSERT OR IGNORE INTO study_group_members (group_id, student_id, student_name, joined_at)
                                VALUES (?, ?, ?, ?);
                            """, (g["group_id"], member_id, "Student Member", now_str))

                conn.commit()
            finally:
                conn.close()

    @staticmethod
    def _calculate_tier(xp: int) -> str:
        """Derives ECE rank tier based on cumulative XP points."""
        if xp >= 4000:
            return "Silicon Grandmaster"
        elif xp >= 3000:
            return "Firmware Architect"
        elif xp >= 2000:
            return "Embedded Specialist"
        else:
            return "Circuit Novice"

    # =========================================================================
    # Portfolio Operations
    # =========================================================================
    def submit_portfolio_project(
        self,
        student_id: str,
        student_name: str,
        title: str,
        description: str,
        domain: str,
        tech_stack: List[str],
        repo_url: str = "",
        wokwi_url: str = "",
        hardware_hil_verified: bool = False
    ) -> Dict[str, Any]:
        """Submits a student engineering project and awards +200 XP."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                project_id = f"PRJ-{int(time.time()*1000)%1000000:06d}"
                created_at = datetime.now(timezone.utc).isoformat()
                xp_reward = 200

                cur.execute("""
                    INSERT INTO student_portfolios
                    (project_id, student_id, student_name, title, description, domain,
                     tech_stack, repo_url, wokwi_url, hardware_hil_verified, status,
                     likes_count, xp_reward, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SUBMITTED', 0, ?, ?);
                """, (
                    project_id, student_id, student_name, title, description, domain,
                    ",".join(tech_stack), repo_url, wokwi_url,
                    1 if hardware_hil_verified else 0, xp_reward, created_at
                ))

                # Increment student XP
                self._record_xp_delta_locked(conn, student_id, xp_reward)
                conn.commit()

                return {
                    "status": "SUCCESS",
                    "project_id": project_id,
                    "title": title,
                    "xp_awarded": xp_reward,
                    "message": f"Project '{title}' submitted successfully (+{xp_reward} XP awarded)!"
                }
            finally:
                conn.close()

    def list_portfolio_projects(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns all submitted portfolios, optionally filtered by domain."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            if domain:
                cur.execute("SELECT * FROM student_portfolios WHERE domain = ? ORDER BY likes_count DESC, created_at DESC;", (domain,))
            else:
                cur.execute("SELECT * FROM student_portfolios ORDER BY likes_count DESC, created_at DESC;")
            
            rows = cur.fetchall()
            results = []
            for r in rows:
                results.append({
                    "project_id": r["project_id"],
                    "student_id": r["student_id"],
                    "student_name": r["student_name"],
                    "title": r["title"],
                    "description": r["description"],
                    "domain": r["domain"],
                    "tech_stack": [t.strip() for t in r["tech_stack"].split(",") if t.strip()],
                    "repo_url": r["repo_url"],
                    "wokwi_url": r["wokwi_url"],
                    "hardware_hil_verified": bool(r["hardware_hil_verified"]),
                    "status": r["status"],
                    "likes_count": r["likes_count"],
                    "xp_reward": r["xp_reward"],
                    "created_at": r["created_at"]
                })
            return results
        finally:
            conn.close()

    def like_project(self, project_id: str) -> Dict[str, Any]:
        """Increments project thumbs-up count."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("UPDATE student_portfolios SET likes_count = likes_count + 1 WHERE project_id = ?;", (project_id,))
                cur.execute("SELECT likes_count FROM student_portfolios WHERE project_id = ?;", (project_id,))
                row = cur.fetchone()
                if not row:
                    return {"status": "ERROR", "error": "Project not found"}
                conn.commit()
                return {"status": "SUCCESS", "project_id": project_id, "likes_count": row["likes_count"]}
            finally:
                conn.close()

    def endorse_portfolio_project(
        self,
        project_id: str,
        actor_role: str = "Student",
        new_status: str = "FEATURED"
    ) -> Dict[str, Any]:
        """
        RBAC Guard: Only 'Admin', 'Teacher', or 'Admin_Owner' can endorse or feature a project.
        """
        privileged_roles = {"Admin", "Teacher", "Admin_Owner", "Lab-Instructor"}
        if actor_role not in privileged_roles:
            return {
                "status": "FORBIDDEN",
                "error": f"Role '{actor_role}' is not authorized to endorse or feature projects."
            }

        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("UPDATE student_portfolios SET status = ? WHERE project_id = ?;", (new_status, project_id))
                if cur.rowcount == 0:
                    return {"status": "ERROR", "error": "Project not found"}
                conn.commit()
                return {"status": "SUCCESS", "project_id": project_id, "new_status": new_status}
            finally:
                conn.close()

    # =========================================================================
    # Peer Review Operations
    # =========================================================================
    def submit_peer_review(
        self,
        project_id: str,
        reviewer_id: str,
        reviewer_name: str,
        rubric_scores: Dict[str, float],
        comments: str
    ) -> Dict[str, Any]:
        """
        Submits a peer code review with a 4-criterion rubric (1.0 to 10.0):
        code_quality, timing_safety, memory_efficiency, test_coverage.
        Average >= 7.0 triggers status 'APPROVED', else 'CHANGES_REQUESTED'.
        Awards +150 XP to the reviewer.
        """
        scores = [
            rubric_scores.get("code_quality", 5.0),
            rubric_scores.get("timing_safety", 5.0),
            rubric_scores.get("memory_efficiency", 5.0),
            rubric_scores.get("test_coverage", 5.0)
        ]
        overall = round(sum(scores) / len(scores), 2)
        decision_status = "APPROVED" if overall >= 7.0 else "CHANGES_REQUESTED"
        review_id = f"REV-{int(time.time()*1000)%1000000:06d}"
        created_at = datetime.now(timezone.utc).isoformat()
        xp_awarded = 150

        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO peer_reviews
                    (review_id, project_id, reviewer_id, reviewer_name,
                     code_quality, timing_safety, memory_efficiency, test_coverage,
                     overall_score, comments, status, xp_awarded, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    review_id, project_id, reviewer_id, reviewer_name,
                    rubric_scores.get("code_quality", 5.0),
                    rubric_scores.get("timing_safety", 5.0),
                    rubric_scores.get("memory_efficiency", 5.0),
                    rubric_scores.get("test_coverage", 5.0),
                    overall, comments, decision_status, xp_awarded, created_at
                ))

                # Update portfolio status to VERIFIED if approved
                if decision_status == "APPROVED":
                    cur.execute("UPDATE student_portfolios SET status = 'VERIFIED' WHERE project_id = ? AND status = 'SUBMITTED';", (project_id,))

                # Award reviewer XP
                self._record_xp_delta_locked(conn, reviewer_id, xp_awarded)
                conn.commit()

                return {
                    "status": "SUCCESS",
                    "review_id": review_id,
                    "project_id": project_id,
                    "overall_score": overall,
                    "decision": decision_status,
                    "xp_awarded": xp_awarded
                }
            finally:
                conn.close()

    def list_peer_reviews(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves peer reviews, optionally for a specific project."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            if project_id:
                cur.execute("SELECT * FROM peer_reviews WHERE project_id = ? ORDER BY created_at DESC;", (project_id,))
            else:
                cur.execute("SELECT * FROM peer_reviews ORDER BY created_at DESC;")
            
            rows = cur.fetchall()
            return [
                {
                    "review_id": r["review_id"],
                    "project_id": r["project_id"],
                    "reviewer_id": r["reviewer_id"],
                    "reviewer_name": r["reviewer_name"],
                    "rubric_scores": {
                        "code_quality": r["code_quality"],
                        "timing_safety": r["timing_safety"],
                        "memory_efficiency": r["memory_efficiency"],
                        "test_coverage": r["test_coverage"]
                    },
                    "overall_score": r["overall_score"],
                    "comments": r["comments"],
                    "status": r["status"],
                    "xp_awarded": r["xp_awarded"],
                    "created_at": r["created_at"]
                }
                for r in rows
            ]
        finally:
            conn.close()

    # =========================================================================
    # Study Group Operations
    # =========================================================================
    def create_study_group(
        self,
        group_name: str,
        subject_code: str,
        topic: str,
        leader_id: str,
        leader_name: str,
        schedule_slot: str,
        meeting_link: str,
        max_members: int = 6
    ) -> Dict[str, Any]:
        """Creates a new student study group and auto-enrolls the creator."""
        group_id = f"GRP-{subject_code}-{int(time.time())%100000:05d}"
        created_at = datetime.now(timezone.utc).isoformat()

        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO study_groups
                    (group_id, group_name, subject_code, topic, leader_id, leader_name,
                     schedule_slot, meeting_link, max_members, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    group_id, group_name, subject_code, topic, leader_id, leader_name,
                    schedule_slot, meeting_link, max_members, created_at
                ))
                # Add leader as initial member
                cur.execute("""
                    INSERT INTO study_group_members (group_id, student_id, student_name, joined_at)
                    VALUES (?, ?, ?, ?);
                """, (group_id, leader_id, leader_name, created_at))

                # Award leader +100 XP for initiating a collaboration pod
                self._record_xp_delta_locked(conn, leader_id, 100)
                conn.commit()

                return {
                    "status": "SUCCESS",
                    "group_id": group_id,
                    "group_name": group_name,
                    "xp_awarded": 100
                }
            finally:
                conn.close()

    def join_study_group(
        self,
        group_id: str,
        student_id: str,
        student_name: str
    ) -> Dict[str, Any]:
        """Enrolls a student into an open study group if capacity allows."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT max_members FROM study_groups WHERE group_id = ?;", (group_id,))
                g = cur.fetchone()
                if not g:
                    return {"status": "ERROR", "error": "Study group not found"}

                max_members = g["max_members"]
                cur.execute("SELECT COUNT(*) FROM study_group_members WHERE group_id = ?;", (group_id,))
                cur_count = cur.fetchone()[0]

                if cur_count >= max_members:
                    return {"status": "FULL", "error": f"Study group has reached capacity ({max_members} members)"}

                now_str = datetime.now(timezone.utc).isoformat()
                cur.execute("""
                    INSERT OR IGNORE INTO study_group_members (group_id, student_id, student_name, joined_at)
                    VALUES (?, ?, ?, ?);
                """, (group_id, student_id, student_name, now_str))

                if cur.rowcount == 0:
                    return {"status": "ALREADY_MEMBER", "message": "Student is already in this study group"}

                # Award +50 XP for joining a study cohort
                self._record_xp_delta_locked(conn, student_id, 50)
                conn.commit()

                return {
                    "status": "SUCCESS",
                    "group_id": group_id,
                    "member_count": cur_count + 1,
                    "xp_awarded": 50
                }
            finally:
                conn.close()

    def list_study_groups(self, subject_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists active study groups with member rosters."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            if subject_code:
                cur.execute("SELECT * FROM study_groups WHERE subject_code = ? ORDER BY created_at DESC;", (subject_code,))
            else:
                cur.execute("SELECT * FROM study_groups ORDER BY created_at DESC;")
            
            groups = cur.fetchall()
            results = []
            for g in groups:
                cur.execute("SELECT student_id, student_name FROM study_group_members WHERE group_id = ?;", (g["group_id"],))
                members = [{"student_id": m["student_id"], "student_name": m["student_name"]} for m in cur.fetchall()]
                results.append({
                    "group_id": g["group_id"],
                    "group_name": g["group_name"],
                    "subject_code": g["subject_code"],
                    "topic": g["topic"],
                    "leader_id": g["leader_id"],
                    "leader_name": g["leader_name"],
                    "schedule_slot": g["schedule_slot"],
                    "meeting_link": g["meeting_link"],
                    "max_members": g["max_members"],
                    "members": members,
                    "member_count": len(members),
                    "is_full": len(members) >= g["max_members"]
                })
            return results
        finally:
            conn.close()

    # =========================================================================
    # Academic Leaderboard Operations
    # =========================================================================
    def _record_xp_delta_locked(self, conn: sqlite3.Connection, student_id: str, xp_delta: int):
        """Internal helper to increment XP and recalculate rank tier."""
        cur = conn.cursor()
        cur.execute("SELECT xp FROM leaderboard_xp WHERE student_id = ?;", (student_id,))
        row = cur.fetchone()
        if row:
            new_xp = row["xp"] + xp_delta
            new_tier = self._calculate_tier(new_xp)
            cur.execute("""
                UPDATE leaderboard_xp 
                SET xp = ?, tier = ? 
                WHERE student_id = ?;
            """, (new_xp, new_tier, student_id))
        else:
            new_tier = self._calculate_tier(xp_delta)
            cur.execute("""
                INSERT INTO leaderboard_xp 
                (student_id, name, roll_no, xp, streak_days, department, institution, tier, badges)
                VALUES (?, ?, ?, ?, 1, 'Electronics Engineering', 'MIT Campus, Anna University', ?, 'Newcomer');
            """, (student_id, f"Student {student_id}", student_id, xp_delta, new_tier))

    def record_xp_activity(self, student_id: str, xp_delta: int, reason: str = "") -> Dict[str, Any]:
        """Public method to record gamified XP activities."""
        with self._lock:
            conn = self._get_connection()
            try:
                self._record_xp_delta_locked(conn, student_id, xp_delta)
                conn.commit()
                cur = conn.cursor()
                cur.execute("SELECT xp, tier FROM leaderboard_xp WHERE student_id = ?;", (student_id,))
                row = cur.fetchone()
                return {
                    "status": "SUCCESS",
                    "student_id": student_id,
                    "xp_delta": xp_delta,
                    "new_total_xp": row["xp"] if row else xp_delta,
                    "tier": row["tier"] if row else "Circuit Novice",
                    "reason": reason
                }
            finally:
                conn.close()

    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Returns leaderboard rankings ordered by XP descending."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM leaderboard_xp ORDER BY xp DESC LIMIT ?;", (limit,))
            rows = cur.fetchall()
            results = []
            for idx, r in enumerate(rows, start=1):
                results.append({
                    "rank": idx,
                    "student_id": r["student_id"],
                    "name": r["name"],
                    "roll_no": r["roll_no"],
                    "xp": r["xp"],
                    "streak_days": r["streak_days"],
                    "department": r["department"],
                    "institution": r["institution"],
                    "tier": r["tier"],
                    "badges": [b.strip() for b in r["badges"].split(",") if b.strip()]
                })
            return results
        finally:
            conn.close()

    def get_collaboration_overview(self) -> Dict[str, Any]:
        """Provides an aggregated summary for the student collaboration dashboard."""
        return {
            "institution": "Madras Institute of Technology (MIT) Campus, Anna University",
            "department": "Department of Electronics Engineering",
            "portfolios": self.list_portfolio_projects()[:6],
            "study_groups": self.list_study_groups()[:6],
            "leaderboard": self.get_leaderboard(limit=5),
            "recent_reviews": self.list_peer_reviews()[:4]
        }


# Global Collaboration Hub Singleton
collaboration_hub = CollaborationHub()

