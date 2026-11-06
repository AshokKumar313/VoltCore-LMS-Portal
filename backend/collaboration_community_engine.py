"""
========================================================================================
VoltCore Apex Academia - Phase M: Collaboration & Community (Features 331–340)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Features:
  - Feature 331: Student Discussion Forums (ECE Topics, Threads, Upvoting, Solution Marking)
  - Feature 332: Subject-Wise Question Community (Anna Univ Reg 2023 Core Codes)
  - Feature 333: Study Group Creator (Virtual rooms, schedules, peer join/leave)
  - Feature 334: Collaborative Notes Workspace (Markdown notes, revision tags, export)
  - Feature 335: Peer Assignment Review (Rubric-based evaluation, weighted scoring)
  - Feature 336: Project Team Discussion Board (Channels, sprint tasks, status boards)
  - Feature 337: Faculty Doubt-Clearing Portal (Direct query to professors, priority queues)
  - Feature 338: Shared Resource Library (SPICE netlists, Verilog TB, MATLAB, notes)
  - Feature 339: Student Knowledge Contribution Points (Karma, badges, leaderboard)
  - Feature 340: Academic Announcement Feed (Anna University & MIT Campus circulars)
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
# ANNA UNIVERSITY REGULATION 2023 ECE SUBJECT CODES (Feature 332)
# ---------------------------------------------------------------------------

AU_REG2023_SUBJECTS: Dict[str, Dict[str, Any]] = {
    "EC3351": {
        "code": "EC3351",
        "name": "Control Systems",
        "semester": 3,
        "credits": 4,
        "topics": ["Transfer Functions", "Block Diagram Reduction", "Routh-Hurwitz", "Bode & Nyquist Plots", "State-Space Analysis"]
    },
    "EC3352": {
        "code": "EC3352",
        "name": "Digital Systems Design",
        "semester": 3,
        "credits": 4,
        "topics": ["K-Maps & Quine-McCluskey", "Synchronous Sequential Circuits", "Verilog HDL", "FSM Synthesis", "Hazards & Glitches"]
    },
    "EC3451": {
        "code": "EC3451",
        "name": "Linear Integrated Circuits",
        "semester": 4,
        "credits": 3,
        "topics": ["Op-Amp Fundamentals", "Active Filters", "555 Timer Astable/Monostable", "Phase-Locked Loops (PLL)", "ADC/DAC Converters"]
    },
    "EC3452": {
        "code": "EC3452",
        "name": "Electromagnetic Fields",
        "semester": 4,
        "credits": 4,
        "topics": ["Maxwell's Equations", "Poynting Vector", "Wave Propagation in Dielectrics", "Transmission Line Equations", "Smith Chart"]
    },
    "EC3501": {
        "code": "EC3501",
        "name": "Wireless Communication",
        "semester": 5,
        "credits": 3,
        "topics": ["Cellular Architecture", "Rayleigh & Rician Fading", "CDMA / OFDM Principles", "MIMO Antenna Systems", "5G NR Standards"]
    },
    "EC3551": {
        "code": "EC3551",
        "name": "Transmission Lines and RF Systems",
        "semester": 5,
        "credits": 3,
        "topics": ["S-Parameters", "Impedance Matching Stubs", "Microstrip Lines", "RF Power Amplifiers", "Waveguides & Cavities"]
    },
    "EC3552": {
        "code": "EC3552",
        "name": "VLSI and Chip Design",
        "semester": 5,
        "credits": 4,
        "topics": ["CMOS Inverter DC Transfer", "Static & Dynamic Power", "RTL-to-GDSII Synthesis", "Static Timing Analysis (STA)", "DFT & Scan Chains"]
    },
    "EC3601": {
        "code": "EC3601",
        "name": "Medical Electronics",
        "semester": 6,
        "credits": 3,
        "topics": ["Biopotential Electrodes", "ECG/EEG/EMG Lead Systems", "Patient Safety & Isolation", "Defibrillators & Pacemakers", "Bio-Telemetry"]
    }
}

# ---------------------------------------------------------------------------
# MIT CAMPUS ECE FACULTY DIRECTORY (Feature 337)
# ---------------------------------------------------------------------------

FACULTY_DIRECTORY: List[Dict[str, Any]] = [
    {
        "id": "fac_01",
        "name": "Dr. P. Nirmal",
        "designation": "Professor & Head",
        "department": "Electronics Engineering, MIT Campus",
        "specialization": "VLSI Design, Low Power Architectures",
        "office_hours": "Tues/Thurs 14:00 - 16:00 IST",
        "verified": True
    },
    {
        "id": "fac_02",
        "name": "Dr. S. Malarvizhi",
        "designation": "Associate Professor",
        "department": "Electronics Engineering, MIT Campus",
        "specialization": "Embedded Systems, RTOS, ARM Architecture",
        "office_hours": "Mon/Wed 10:00 - 12:00 IST",
        "verified": True
    },
    {
        "id": "fac_03",
        "name": "Dr. V. Sathiesh Kumar",
        "designation": "Assistant Professor (Sr. Gr.)",
        "department": "Electronics Engineering, MIT Campus",
        "specialization": "Wireless Comm, RF Circuits & Antennas",
        "office_hours": "Fri 11:00 - 13:00 IST",
        "verified": True
    },
    {
        "id": "fac_04",
        "name": "Dr. T. S. Pradeep Kumar",
        "designation": "Associate Professor",
        "department": "Electronics Engineering, MIT Campus",
        "specialization": "IoT Architectures, TinyML, Sensor Networks",
        "office_hours": "Wed/Fri 14:30 - 16:30 IST",
        "verified": True
    }
]

# ---------------------------------------------------------------------------
# ACADEMIC ANNOUNCEMENTS SEED CATALOG (Feature 340)
# ---------------------------------------------------------------------------

DEFAULT_ANNOUNCEMENTS: List[Dict[str, Any]] = [
    {
        "id": "ann_2026_01",
        "title": "Anna University End-Semester Practical Exam Schedule (Nov/Dec 2026)",
        "category": "EXAM_TIMETABLE",
        "priority": "URGENT",
        "department": "Office of the Controller of Examinations, Anna University",
        "date": "2026-11-05",
        "summary": "Practical and Viva-Voce examinations for B.E. ECE (Reg 2023) Semesters III and V commence on November 18, 2026. Hall tickets available on ACOE portal.",
        "action_link": "https://acoe.annauniv.edu"
    },
    {
        "id": "ann_2026_02",
        "title": "Texas Instruments Day-0 Placement & Core Internship Drive 2026",
        "category": "ANNA_UNIV_CIRCULAR",
        "priority": "IMPORTANT",
        "department": "CUIC / Placement Cell, MIT Campus",
        "date": "2026-11-04",
        "summary": "TI Analog & Embedded Firmware drive scheduled for pre-final and final year students. Shortlisting requires CGPA >= 8.25 and verified hardware project portfolio.",
        "action_link": "https://cuic.annauniv.edu"
    },
    {
        "id": "ann_2026_03",
        "title": "IEEE MIT Student Branch: Hands-on Workshop on RISC-V Custom Instructions",
        "category": "IEEE_STUDENT_BRANCH",
        "priority": "INFO",
        "department": "IEEE Student Branch, Madras Institute of Technology",
        "date": "2026-11-03",
        "summary": "Two-day workshop covering Chisel HDL, RISC-V GNU toolchain, and FPGA implementation of custom vector extensions. Certificates awarded.",
        "action_link": "https://mitindia.edu/ieee"
    },
    {
        "id": "ann_2026_04",
        "title": "VoltCore Hackathon 2026: Low-Power Edge IoT for Sustainable Agriculture",
        "category": "HACKATHON",
        "priority": "IMPORTANT",
        "department": "Department of Electronics Engineering, MIT Campus",
        "date": "2026-11-01",
        "summary": "Inter-college hardware hackathon on energy-harvesting IoT nodes using STM32L4 and LoRaWAN. Cash prizes up to Rs. 75,000 sponsored by Apex Core Labs.",
        "action_link": "https://voltcore.annauniv.edu/hackathon"
    }
]

# ---------------------------------------------------------------------------
# BADGE DEFINITIONS (Feature 339)
# ---------------------------------------------------------------------------

BADGE_CRITERIA = [
    {"badge_id": "silicon_scholar", "name": "Silicon Scholar", "min_points": 50, "category": "VLSI", "icon": "microchip"},
    {"badge_id": "rtos_champion", "name": "RTOS Champion", "min_points": 50, "category": "Embedded", "icon": "cpu"},
    {"badge_id": "dsp_master", "name": "DSP Master", "min_points": 50, "category": "Signals", "icon": "activity"},
    {"badge_id": "apex_fellow", "name": "VoltCore Apex Fellow", "min_points": 100, "category": "All", "icon": "award"}
]


class CollaborationCommunityEngine:
    """
    Core backend engine for VoltCore Apex Academia Phase M (Features 331–340).
    Manages discussion forums, study groups, peer reviews, faculty doubts,
    shared resource libraries, and community karma rankings.
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
                # Feature 331: Forum posts & replies
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS forum_posts (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        category TEXT NOT NULL,
                        author_name TEXT NOT NULL,
                        author_roll TEXT NOT NULL,
                        content TEXT NOT NULL,
                        tags TEXT NOT NULL,
                        upvotes INTEGER DEFAULT 0,
                        reply_count INTEGER DEFAULT 0,
                        solution_id TEXT DEFAULT NULL,
                        created_at TEXT NOT NULL
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS forum_replies (
                        id TEXT PRIMARY KEY,
                        post_id TEXT NOT NULL,
                        author_name TEXT NOT NULL,
                        author_roll TEXT NOT NULL,
                        content TEXT NOT NULL,
                        upvotes INTEGER DEFAULT 0,
                        is_solution INTEGER DEFAULT 0,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (post_id) REFERENCES forum_posts(id)
                    )
                """)

                # Feature 332: Subject-wise questions
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS subject_questions (
                        id TEXT PRIMARY KEY,
                        subject_code TEXT NOT NULL,
                        title TEXT NOT NULL,
                        question_text TEXT NOT NULL,
                        author_roll TEXT NOT NULL,
                        answers_count INTEGER DEFAULT 0,
                        created_at TEXT NOT NULL
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS subject_answers (
                        id TEXT PRIMARY KEY,
                        question_id TEXT NOT NULL,
                        author_roll TEXT NOT NULL,
                        author_name TEXT NOT NULL,
                        answer_text TEXT NOT NULL,
                        is_verified INTEGER DEFAULT 0,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (question_id) REFERENCES subject_questions(id)
                    )
                """)

                # Feature 333: Study groups
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS study_groups (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        subject_code TEXT NOT NULL,
                        topic TEXT NOT NULL,
                        max_members INTEGER DEFAULT 6,
                        schedule_time TEXT NOT NULL,
                        virtual_room_url TEXT NOT NULL,
                        created_by TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS study_group_members (
                        group_id TEXT NOT NULL,
                        student_roll TEXT NOT NULL,
                        student_name TEXT NOT NULL,
                        joined_at TEXT NOT NULL,
                        PRIMARY KEY (group_id, student_roll)
                    )
                """)

                # Feature 334: Collaborative notes
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS collaborative_notes (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        subject_code TEXT NOT NULL,
                        content_markdown TEXT NOT NULL,
                        authors TEXT NOT NULL,
                        version INTEGER DEFAULT 1,
                        tags TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)

                # Feature 335: Peer assignment reviews
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS peer_assignment_reviews (
                        id TEXT PRIMARY KEY,
                        assignment_title TEXT NOT NULL,
                        subject_code TEXT NOT NULL,
                        student_roll TEXT NOT NULL,
                        reviewer_roll TEXT NOT NULL,
                        circuit_score REAL NOT NULL,
                        sim_score REAL NOT NULL,
                        doc_score REAL NOT NULL,
                        overall_score REAL NOT NULL,
                        comments TEXT NOT NULL,
                        submitted_at TEXT NOT NULL
                    )
                """)

                # Feature 336: Project team boards
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS project_boards (
                        id TEXT PRIMARY KEY,
                        project_title TEXT NOT NULL,
                        sprint_goal TEXT NOT NULL,
                        created_by TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS project_tasks (
                        id TEXT PRIMARY KEY,
                        board_id TEXT NOT NULL,
                        description TEXT NOT NULL,
                        assignee TEXT NOT NULL,
                        status TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        FOREIGN KEY (board_id) REFERENCES project_boards(id)
                    )
                """)

                # Feature 337: Faculty doubts
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS faculty_doubts (
                        id TEXT PRIMARY KEY,
                        student_roll TEXT NOT NULL,
                        faculty_id TEXT NOT NULL,
                        subject_code TEXT NOT NULL,
                        query_text TEXT NOT NULL,
                        priority TEXT DEFAULT 'MEDIUM',
                        status TEXT DEFAULT 'PENDING',
                        faculty_response TEXT DEFAULT NULL,
                        submitted_at TEXT NOT NULL
                    )
                """)

                # Feature 338: Shared resource library
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS shared_resources (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        category TEXT NOT NULL,
                        subject_code TEXT NOT NULL,
                        uploader_name TEXT NOT NULL,
                        uploader_roll TEXT NOT NULL,
                        file_url TEXT NOT NULL,
                        upvotes INTEGER DEFAULT 0,
                        downloads INTEGER DEFAULT 0,
                        created_at TEXT NOT NULL
                    )
                """)

                # Feature 339: Student karma points
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS student_karma_points (
                        student_roll TEXT PRIMARY KEY,
                        student_name TEXT NOT NULL,
                        points INTEGER DEFAULT 0,
                        vlsi_points INTEGER DEFAULT 0,
                        embedded_points INTEGER DEFAULT 0,
                        dsp_points INTEGER DEFAULT 0,
                        badges TEXT DEFAULT '[]',
                        last_awarded TEXT NOT NULL
                    )
                """)

                # Feature 340: Academic announcements
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS academic_announcements (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        category TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        department TEXT NOT NULL,
                        date TEXT NOT NULL,
                        summary TEXT NOT NULL,
                        action_link TEXT NOT NULL
                    )
                """)

                # Seed default announcements if table empty
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) AS cnt FROM academic_announcements")
                if cursor.fetchone()["cnt"] == 0:
                    for ann in DEFAULT_ANNOUNCEMENTS:
                        conn.execute("""
                            INSERT INTO academic_announcements 
                            (id, title, category, priority, department, date, summary, action_link)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            ann["id"], ann["title"], ann["category"], ann["priority"],
                            ann["department"], ann["date"], ann["summary"], ann["action_link"]
                        ))

                conn.commit()
            finally:
                conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 331: STUDENT DISCUSSION FORUMS
    # ---------------------------------------------------------------------------

    def post_forum_message(
        self,
        post_id: str,
        title: str,
        category: str,
        author_name: str,
        author_roll: str,
        content: str,
        tags: List[str]
    ) -> Dict[str, Any]:
        """Post a new discussion thread in the ECE forum."""
        now_iso = datetime.now(timezone.utc).isoformat()
        tags_json = json.dumps(tags)
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO forum_posts
                    (id, title, category, author_name, author_roll, content, tags, upvotes, reply_count, solution_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, NULL, ?)
                """, (post_id, title, category, author_name, author_roll, content, tags_json, now_iso))
                conn.commit()
            finally:
                conn.close()

        # Award +2 karma points for thread creation
        self.award_karma_points(author_roll, author_name, 2, category)

        return {
            "status": "success",
            "post_id": post_id,
            "title": title,
            "category": category,
            "created_at": now_iso
        }

    def reply_forum_post(
        self,
        reply_id: str,
        post_id: str,
        author_name: str,
        author_roll: str,
        content: str
    ) -> Dict[str, Any]:
        """Post a reply to an existing forum thread."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO forum_replies
                    (id, post_id, author_name, author_roll, content, upvotes, is_solution, created_at)
                    VALUES (?, ?, ?, ?, ?, 0, 0, ?)
                """, (reply_id, post_id, author_name, author_roll, content, now_iso))
                conn.execute("""
                    UPDATE forum_posts SET reply_count = reply_count + 1 WHERE id = ?
                """, (post_id,))
                conn.commit()
            finally:
                conn.close()

        self.award_karma_points(author_roll, author_name, 3, "All")
        return {"status": "success", "reply_id": reply_id, "post_id": post_id}

    def upvote_forum_post(self, post_id: str) -> Dict[str, Any]:
        """Upvote a forum post."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("UPDATE forum_posts SET upvotes = upvotes + 1 WHERE id = ?", (post_id,))
                cursor = conn.cursor()
                cursor.execute("SELECT author_roll, author_name, upvotes FROM forum_posts WHERE id = ?", (post_id,))
                row = cursor.fetchone()
                conn.commit()
            finally:
                conn.close()

        if row:
            self.award_karma_points(row["author_roll"], row["author_name"], 2, "All")
            return {"status": "success", "post_id": post_id, "upvotes": row["upvotes"]}
        return {"status": "error", "message": "Post not found"}

    def mark_forum_solution(self, post_id: str, reply_id: str) -> Dict[str, Any]:
        """Mark a specific reply as the accepted solution for a thread."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("UPDATE forum_posts SET solution_id = ? WHERE id = ?", (reply_id, post_id))
                conn.execute("UPDATE forum_replies SET is_solution = 1 WHERE id = ?", (reply_id,))
                cursor = conn.cursor()
                cursor.execute("SELECT author_roll, author_name FROM forum_replies WHERE id = ?", (reply_id,))
                reply_author = cursor.fetchone()
                conn.commit()
            finally:
                conn.close()

        if reply_author:
            # High karma bonus for accepted solution (+15)
            self.award_karma_points(reply_author["author_roll"], reply_author["author_name"], 15, "All")

        return {"status": "success", "post_id": post_id, "solution_id": reply_id}

    def get_forum_posts(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve forum posts, optionally filtered by category."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if category and category != "ALL":
                cursor.execute("SELECT * FROM forum_posts WHERE category = ? ORDER BY created_at DESC", (category,))
            else:
                cursor.execute("SELECT * FROM forum_posts ORDER BY created_at DESC")
            rows = cursor.fetchall()
            posts = []
            for r in rows:
                p = dict(r)
                p["tags"] = json.loads(p["tags"]) if p["tags"] else []
                posts.append(p)
            return posts
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 332: SUBJECT-WISE QUESTION COMMUNITY
    # ---------------------------------------------------------------------------

    def post_subject_question(
        self,
        q_id: str,
        subject_code: str,
        title: str,
        question_text: str,
        author_roll: str
    ) -> Dict[str, Any]:
        """Post a question tied to an Anna University Reg 2023 subject code."""
        subj_info = AU_REG2023_SUBJECTS.get(subject_code.upper())
        if not subj_info:
            return {"status": "error", "message": f"Invalid subject code {subject_code}. Must be Reg 2023 ECE."}

        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO subject_questions
                    (id, subject_code, title, question_text, author_roll, answers_count, created_at)
                    VALUES (?, ?, ?, ?, ?, 0, ?)
                """, (q_id, subject_code.upper(), title, question_text, author_roll, now_iso))
                conn.commit()
            finally:
                conn.close()

        return {
            "status": "success",
            "question_id": q_id,
            "subject_code": subject_code.upper(),
            "subject_name": subj_info["name"]
        }

    def answer_subject_question(
        self,
        ans_id: str,
        question_id: str,
        author_roll: str,
        author_name: str,
        answer_text: str,
        is_verified: bool = False
    ) -> Dict[str, Any]:
        """Provide an answer to a subject-specific question."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO subject_answers
                    (id, question_id, author_roll, author_name, answer_text, is_verified, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (ans_id, question_id, author_roll, author_name, answer_text, 1 if is_verified else 0, now_iso))
                conn.execute("""
                    UPDATE subject_questions SET answers_count = answers_count + 1 WHERE id = ?
                """, (question_id,))
                conn.commit()
            finally:
                conn.close()

        pts = 15 if is_verified else 5
        self.award_karma_points(author_roll, author_name, pts, "All")
        return {"status": "success", "answer_id": ans_id, "question_id": question_id}

    def get_subject_questions(self, subject_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """List subject questions, optionally filtered by code."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if subject_code:
                cursor.execute("SELECT * FROM subject_questions WHERE subject_code = ? ORDER BY created_at DESC", (subject_code.upper(),))
            else:
                cursor.execute("SELECT * FROM subject_questions ORDER BY created_at DESC")
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 333: STUDY GROUP CREATOR
    # ---------------------------------------------------------------------------

    def create_study_group(
        self,
        group_id: str,
        name: str,
        subject_code: str,
        topic: str,
        max_members: int,
        schedule_time: str,
        virtual_room_url: str,
        created_by_roll: str,
        creator_name: str
    ) -> Dict[str, Any]:
        """Create a new peer study group for an ECE course."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO study_groups
                    (id, name, subject_code, topic, max_members, schedule_time, virtual_room_url, created_by, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (group_id, name, subject_code.upper(), topic, max_members, schedule_time, virtual_room_url, created_by_roll, now_iso))
                conn.execute("""
                    INSERT OR REPLACE INTO study_group_members
                    (group_id, student_roll, student_name, joined_at)
                    VALUES (?, ?, ?, ?)
                """, (group_id, created_by_roll, creator_name, now_iso))
                conn.commit()
            finally:
                conn.close()

        self.award_karma_points(created_by_roll, creator_name, 5, "All")
        return {
            "status": "success",
            "group_id": group_id,
            "name": name,
            "members_count": 1
        }

    def join_study_group(self, group_id: str, student_roll: str, student_name: str) -> Dict[str, Any]:
        """Join an existing study group if under member capacity."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT max_members FROM study_groups WHERE id = ?", (group_id,))
                grp = cursor.fetchone()
                if not grp:
                    return {"status": "error", "message": "Study group not found"}

                cursor.execute("SELECT COUNT(*) AS count FROM study_group_members WHERE group_id = ?", (group_id,))
                current_cnt = cursor.fetchone()["count"]

                if current_cnt >= grp["max_members"]:
                    return {"status": "error", "message": "Study group is at maximum capacity"}

                conn.execute("""
                    INSERT OR REPLACE INTO study_group_members
                    (group_id, student_roll, student_name, joined_at)
                    VALUES (?, ?, ?, ?)
                """, (group_id, student_roll, student_name, now_iso))
                conn.commit()
            finally:
                conn.close()

        return {"status": "success", "group_id": group_id, "student_roll": student_roll}

    def leave_study_group(self, group_id: str, student_roll: str) -> Dict[str, Any]:
        """Leave a study group."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("DELETE FROM study_group_members WHERE group_id = ? AND student_roll = ?", (group_id, student_roll))
                conn.commit()
            finally:
                conn.close()
        return {"status": "success", "group_id": group_id, "student_roll": student_roll}

    def list_study_groups(self) -> List[Dict[str, Any]]:
        """List active study groups with member counts."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT g.*, COUNT(m.student_roll) AS member_count
                FROM study_groups g
                LEFT JOIN study_group_members m ON g.id = m.group_id
                GROUP BY g.id
                ORDER BY g.created_at DESC
            """)
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 334: COLLABORATIVE NOTES WORKSPACE
    # ---------------------------------------------------------------------------

    def create_or_update_note(
        self,
        note_id: str,
        title: str,
        subject_code: str,
        content_markdown: str,
        authors: List[str],
        tags: List[str]
    ) -> Dict[str, Any]:
        """Save or revise a collaborative study note."""
        now_iso = datetime.now(timezone.utc).isoformat()
        authors_json = json.dumps(authors)
        tags_json = json.dumps(tags)

        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT version FROM collaborative_notes WHERE id = ?", (note_id,))
                existing = cursor.fetchone()
                version = (existing["version"] + 1) if existing else 1

                conn.execute("""
                    INSERT OR REPLACE INTO collaborative_notes
                    (id, title, subject_code, content_markdown, authors, version, tags, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (note_id, title, subject_code.upper(), content_markdown, authors_json, version, tags_json, now_iso))
                conn.commit()
            finally:
                conn.close()

        return {
            "status": "success",
            "note_id": note_id,
            "version": version,
            "title": title,
            "updated_at": now_iso
        }

    def get_note(self, note_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a note by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM collaborative_notes WHERE id = ?", (note_id,))
            row = cursor.fetchone()
            if not row:
                return None
            d = dict(row)
            d["authors"] = json.loads(d["authors"]) if d["authors"] else []
            d["tags"] = json.loads(d["tags"]) if d["tags"] else []
            return d
        finally:
            conn.close()

    def list_notes(self, subject_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """List notes optionally filtered by subject code."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if subject_code:
                cursor.execute("SELECT * FROM collaborative_notes WHERE subject_code = ? ORDER BY updated_at DESC", (subject_code.upper(),))
            else:
                cursor.execute("SELECT * FROM collaborative_notes ORDER BY updated_at DESC")
            notes = []
            for r in cursor.fetchall():
                d = dict(r)
                d["authors"] = json.loads(d["authors"]) if d["authors"] else []
                d["tags"] = json.loads(d["tags"]) if d["tags"] else []
                notes.append(d)
            return notes
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 335: PEER ASSIGNMENT REVIEW
    # ---------------------------------------------------------------------------

    def submit_peer_review(
        self,
        review_id: str,
        assignment_title: str,
        subject_code: str,
        student_roll: str,
        reviewer_roll: str,
        circuit_score: float,
        sim_score: float,
        doc_score: float,
        comments: str
    ) -> Dict[str, Any]:
        """
        Submit a rubric-based peer review.
        Weighted overall score = 0.40 * circuit + 0.35 * sim + 0.25 * doc (scale 10.0).
        """
        # Clamp scores between 0 and 10
        c_score = max(0.0, min(10.0, float(circuit_score)))
        s_score = max(0.0, min(10.0, float(sim_score)))
        d_score = max(0.0, min(10.0, float(doc_score)))
        overall = round(0.40 * c_score + 0.35 * s_score + 0.25 * d_score, 2)

        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO peer_assignment_reviews
                    (id, assignment_title, subject_code, student_roll, reviewer_roll, circuit_score, sim_score, doc_score, overall_score, comments, submitted_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (review_id, assignment_title, subject_code.upper(), student_roll, reviewer_roll, c_score, s_score, d_score, overall, comments, now_iso))
                conn.commit()
            finally:
                conn.close()

        # Award reviewer 10 karma points for peer feedback
        self.award_karma_points(reviewer_roll, f"Peer Reviewer ({reviewer_roll})", 10, "All")

        return {
            "status": "success",
            "review_id": review_id,
            "overall_score": overall,
            "rubric_breakdown": {
                "circuit_design": c_score,
                "simulation_accuracy": s_score,
                "documentation": d_score
            }
        }

    def get_assignment_reviews(self, student_roll: str) -> List[Dict[str, Any]]:
        """Get all peer reviews for a student's assignments."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM peer_assignment_reviews WHERE student_roll = ? ORDER BY submitted_at DESC", (student_roll,))
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 336: PROJECT TEAM DISCUSSION BOARD
    # ---------------------------------------------------------------------------

    def create_project_board(self, board_id: str, project_title: str, sprint_goal: str, created_by: str) -> Dict[str, Any]:
        """Create a project team sprint board."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO project_boards
                    (id, project_title, sprint_goal, created_by, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (board_id, project_title, sprint_goal, created_by, now_iso))
                conn.commit()
            finally:
                conn.close()
        return {"status": "success", "board_id": board_id, "project_title": project_title}

    def add_project_task(self, task_id: str, board_id: str, description: str, assignee: str, status: str = "TODO") -> Dict[str, Any]:
        """Add a task to a project board."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO project_tasks
                    (id, board_id, description, assignee, status, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (task_id, board_id, description, assignee, status.upper(), now_iso))
                conn.commit()
            finally:
                conn.close()
        return {"status": "success", "task_id": task_id, "board_id": board_id, "status": status.upper()}

    def update_task_status(self, task_id: str, status: str) -> Dict[str, Any]:
        """Update task status (TODO, IN_PROGRESS, DONE)."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("UPDATE project_tasks SET status = ?, updated_at = ? WHERE id = ?", (status.upper(), now_iso, task_id))
                conn.commit()
            finally:
                conn.close()
        return {"status": "success", "task_id": task_id, "new_status": status.upper()}

    def get_project_board(self, board_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve project board with all associated tasks."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM project_boards WHERE id = ?", (board_id,))
            board = cursor.fetchone()
            if not board:
                return None
            res = dict(board)
            cursor.execute("SELECT * FROM project_tasks WHERE board_id = ? ORDER BY updated_at DESC", (board_id,))
            res["tasks"] = [dict(t) for t in cursor.fetchall()]
            return res
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 337: FACULTY DOUBT-CLEARING PORTAL
    # ---------------------------------------------------------------------------

    def submit_faculty_doubt(
        self,
        doubt_id: str,
        student_roll: str,
        faculty_id: str,
        subject_code: str,
        query_text: str,
        priority: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """Submit a doubt directly to faculty members with office hours tracking."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO faculty_doubts
                    (id, student_roll, faculty_id, subject_code, query_text, priority, status, faculty_response, submitted_at)
                    VALUES (?, ?, ?, ?, ?, ?, 'PENDING', NULL, ?)
                """, (doubt_id, student_roll, faculty_id, subject_code.upper(), query_text, priority.upper(), now_iso))
                conn.commit()
            finally:
                conn.close()

        faculty = next((f for f in FACULTY_DIRECTORY if f["id"] == faculty_id), None)
        faculty_name = faculty["name"] if faculty else "Faculty Member"

        return {
            "status": "success",
            "doubt_id": doubt_id,
            "faculty_name": faculty_name,
            "status_code": "PENDING"
        }

    def respond_faculty_doubt(self, doubt_id: str, faculty_response: str) -> Dict[str, Any]:
        """Faculty responds and resolves a student doubt."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    UPDATE faculty_doubts
                    SET status = 'RESOLVED', faculty_response = ?
                    WHERE id = ?
                """, (faculty_response, doubt_id))
                conn.commit()
            finally:
                conn.close()
        return {"status": "success", "doubt_id": doubt_id, "status_code": "RESOLVED"}

    def get_faculty_doubts(self, student_roll: Optional[str] = None) -> List[Dict[str, Any]]:
        """List faculty doubts, optionally filtered by student roll."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if student_roll:
                cursor.execute("SELECT * FROM faculty_doubts WHERE student_roll = ? ORDER BY submitted_at DESC", (student_roll,))
            else:
                cursor.execute("SELECT * FROM faculty_doubts ORDER BY submitted_at DESC")
            doubts = [dict(r) for r in cursor.fetchall()]
            for d in doubts:
                fac = next((f for f in FACULTY_DIRECTORY if f["id"] == d["faculty_id"]), None)
                d["faculty_name"] = fac["name"] if fac else "Faculty Member"
                d["office_hours"] = fac["office_hours"] if fac else "N/A"
            return doubts
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 338: SHARED RESOURCE LIBRARY
    # ---------------------------------------------------------------------------

    def upload_shared_resource(
        self,
        resource_id: str,
        title: str,
        category: str,
        subject_code: str,
        uploader_name: str,
        uploader_roll: str,
        file_url: str
    ) -> Dict[str, Any]:
        """Register a shared academic resource in the community repository."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO shared_resources
                    (id, title, category, subject_code, uploader_name, uploader_roll, file_url, upvotes, downloads, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, ?)
                """, (resource_id, title, category.upper(), subject_code.upper(), uploader_name, uploader_roll, file_url, now_iso))
                conn.commit()
            finally:
                conn.close()

        # Award 5 points for uploading a learning resource
        self.award_karma_points(uploader_roll, uploader_name, 5, "All")
        return {"status": "success", "resource_id": resource_id, "title": title}

    def upvote_resource(self, resource_id: str) -> Dict[str, Any]:
        """Upvote a shared learning resource."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("UPDATE shared_resources SET upvotes = upvotes + 1 WHERE id = ?", (resource_id,))
                cursor = conn.cursor()
                cursor.execute("SELECT upvotes FROM shared_resources WHERE id = ?", (resource_id,))
                row = cursor.fetchone()
                conn.commit()
            finally:
                conn.close()
        return {"status": "success", "resource_id": resource_id, "upvotes": row["upvotes"] if row else 0}

    def download_resource(self, resource_id: str) -> Dict[str, Any]:
        """Increment download counter."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("UPDATE shared_resources SET downloads = downloads + 1 WHERE id = ?", (resource_id,))
                cursor = conn.cursor()
                cursor.execute("SELECT downloads, file_url FROM shared_resources WHERE id = ?", (resource_id,))
                row = cursor.fetchone()
                conn.commit()
            finally:
                conn.close()
        return {"status": "success", "resource_id": resource_id, "downloads": row["downloads"] if row else 0, "file_url": row["file_url"] if row else ""}

    def list_shared_resources(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List shared learning resources."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if category and category != "ALL":
                cursor.execute("SELECT * FROM shared_resources WHERE category = ? ORDER BY upvotes DESC", (category.upper(),))
            else:
                cursor.execute("SELECT * FROM shared_resources ORDER BY upvotes DESC")
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 339: STUDENT KNOWLEDGE CONTRIBUTION POINTS (KARMA)
    # ---------------------------------------------------------------------------

    def award_karma_points(
        self,
        student_roll: str,
        student_name: str,
        points: int,
        domain: str = "All"
    ) -> Dict[str, Any]:
        """Award knowledge points and evaluate badge achievements."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM student_karma_points WHERE student_roll = ?", (student_roll,))
                existing = cursor.fetchone()

                if existing:
                    cur_pts = existing["points"] + points
                    vlsi = existing["vlsi_points"] + (points if domain in ["VLSI", "Semiconductor"] else 0)
                    emb = existing["embedded_points"] + (points if domain in ["Embedded", "IoT"] else 0)
                    dsp = existing["dsp_points"] + (points if domain in ["Signals", "DSP"] else 0)
                    badges = json.loads(existing["badges"]) if existing["badges"] else []
                else:
                    cur_pts = points
                    vlsi = points if domain in ["VLSI", "Semiconductor"] else 0
                    emb = points if domain in ["Embedded", "IoT"] else 0
                    dsp = points if domain in ["Signals", "DSP"] else 0
                    badges = []

                # Evaluate badges
                if vlsi >= 50 and "silicon_scholar" not in badges:
                    badges.append("silicon_scholar")
                if emb >= 50 and "rtos_champion" not in badges:
                    badges.append("rtos_champion")
                if dsp >= 50 and "dsp_master" not in badges:
                    badges.append("dsp_master")
                if cur_pts >= 100 and "apex_fellow" not in badges:
                    badges.append("apex_fellow")

                badges_json = json.dumps(badges)
                conn.execute("""
                    INSERT OR REPLACE INTO student_karma_points
                    (student_roll, student_name, points, vlsi_points, embedded_points, dsp_points, badges, last_awarded)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (student_roll, student_name, cur_pts, vlsi, emb, dsp, badges_json, now_iso))
                conn.commit()
            finally:
                conn.close()

        return {
            "status": "success",
            "student_roll": student_roll,
            "total_points": cur_pts,
            "badges": badges
        }

    def get_student_karma(self, student_roll: str) -> Optional[Dict[str, Any]]:
        """Retrieve karma profile for a specific student."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM student_karma_points WHERE student_roll = ?", (student_roll,))
            row = cursor.fetchone()
            if not row:
                return None
            res = dict(row)
            res["badges"] = json.loads(res["badges"]) if res["badges"] else []
            return res
        finally:
            conn.close()

    def get_karma_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top contributors on the community leaderboard."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM student_karma_points ORDER BY points DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            leaderboard = []
            for idx, r in enumerate(rows, 1):
                item = dict(r)
                item["rank"] = idx
                item["badges"] = json.loads(item["badges"]) if item["badges"] else []
                leaderboard.append(item)
            return leaderboard
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 340: ACADEMIC ANNOUNCEMENT FEED
    # ---------------------------------------------------------------------------

    def get_announcements(
        self,
        category: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve academic notices and circulars."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM academic_announcements WHERE 1=1"
            params: List[Any] = []
            if category and category != "ALL":
                query += " AND category = ?"
                params.append(category)
            if priority and priority != "ALL":
                query += " AND priority = ?"
                params.append(priority)
            query += " ORDER BY date DESC"

            cursor.execute(query, tuple(params))
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()
