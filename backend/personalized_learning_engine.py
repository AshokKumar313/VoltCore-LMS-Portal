"""
========================================================================================
VoltCore Apex Academia - Phase A: Intelligent Learning Experience (Features 201–202)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Features:
  - Feature 201: Personalized Learning Dashboard (Domain mastery, cognitive gap detection)
  - Feature 202: Adaptive Learning Path Generator (Prerequisite DAG, target career goals)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU usage.
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

# Anna University R2023 ECE Core Domains
ECE_DOMAINS = [
    {
        "id": "embedded_rtos",
        "name": "Embedded Systems & FreeRTOS",
        "code": "EC8702",
        "credits": 4,
        "topics": [
            "ARM Cortex-M Architecture & NVIC",
            "FreeRTOS Preemption & Priority Inversion",
            "DMA Zero-Copy Peripheral Transfers",
            "Hardware Interrupt Latency (ISR)"
        ]
    },
    {
        "id": "digital_vlsi",
        "name": "Digital VLSI & FPGA Synthesis",
        "code": "EC3451",
        "credits": 4,
        "topics": [
            "Quine-McCluskey K-Map Minimization",
            "Verilog HDL Finite State Machines",
            "FPGA LUT-6 & Timing Constraints",
            "Clock Domain Crossing (CDC) Metastability"
        ]
    },
    {
        "id": "analog_rf",
        "name": "Analog Integrated Circuits & Signals",
        "code": "EC3452",
        "credits": 4,
        "topics": [
            "Op-Amp 741 Miller Compensation & Pole Splitting",
            "Differential Pair CMRR & Tail Resistance",
            "Sallen-Key Active Filter Bode Analysis",
            "BJT Small-Signal Hybrid-Pi Modeling"
        ]
    },
    {
        "id": "tinyml_edge",
        "name": "TinyML & Edge AI Intelligence",
        "code": "EC3712",
        "credits": 3,
        "topics": [
            "INT8 Symmetric Quantization & Zero-Point",
            "Depthwise Separable Convolutions & MACs",
            "Microcontroller Tensor Arena Allocation",
            "Acoustic & Vibration Anomaly Detection"
        ]
    },
    {
        "id": "iot_bus",
        "name": "IoT Telemetry & Peripheral Protocols",
        "code": "EC3552",
        "credits": 3,
        "topics": [
            "SPI Mode 0-3 Bus Waveform Timing",
            "I2C 7-Bit Address Framing & ACK/NACK",
            "MQTT Pub/Sub Telemetry Streaming",
            "WebSerial Hardware-in-the-Loop Bridge"
        ]
    }
]

# Adaptive Career Tracks and Required Milestone DAGs
CAREER_TRACKS = {
    "embedded_firmware_architect": {
        "title": "Tier-1 Embedded Firmware Architect",
        "target_companies": "Qualcomm, Texas Instruments, Intel, Apple",
        "milestones": [
            {"id": "m1", "title": "ARM Cortex-M4 Fundamentals & Memory Map", "domain": "embedded_rtos", "difficulty": "Intermediate", "min_score": 75},
            {"id": "m2", "title": "FreeRTOS Priority Inversion & Mutex Protocol", "domain": "embedded_rtos", "difficulty": "Advanced", "min_score": 80},
            {"id": "m3", "title": "Scatter-Gather DMA & Zero-Copy Circular Buffers", "domain": "embedded_rtos", "difficulty": "Hardcore", "min_score": 85},
            {"id": "m4", "title": "SPI/I2C/UART Peripheral Bus Driver Synthesis", "domain": "iot_bus", "difficulty": "Advanced", "min_score": 80}
        ]
    },
    "gate_ece_top_ranker": {
        "title": "GATE ECE Top 100 Ranker",
        "target_companies": "IISc Bangalore, IIT Madras, BARC, ISRO",
        "milestones": [
            {"id": "g1", "title": "Network Theorems & RLC Transients", "domain": "analog_rf", "difficulty": "Intermediate", "min_score": 70},
            {"id": "g2", "title": "Small-Signal BJT & Op-Amp Frequency Response", "domain": "analog_rf", "difficulty": "Advanced", "min_score": 80},
            {"id": "g3", "title": "Sequential Logic FSM & Setup/Hold Times", "domain": "digital_vlsi", "difficulty": "Advanced", "min_score": 80},
            {"id": "g4", "title": "Nyquist Stability & Control System State Space", "domain": "analog_rf", "difficulty": "Hardcore", "min_score": 85}
        ]
    },
    "edge_ai_silicon_engineer": {
        "title": "Edge AI & Silicon Systems Engineer",
        "target_companies": "NVIDIA, Edge Impulse, Bosch, STMicroelectronics",
        "milestones": [
            {"id": "a1", "title": "INT8 Quantization & MAC Operations", "domain": "tinyml_edge", "difficulty": "Intermediate", "min_score": 75},
            {"id": "a2", "title": "Microcontroller Tensor Arena SRAM Budgeting", "domain": "tinyml_edge", "difficulty": "Advanced", "min_score": 80},
            {"id": "a3", "title": "ESP32-S3 Keyword Spotting Firmware", "domain": "tinyml_edge", "difficulty": "Hardcore", "min_score": 85},
            {"id": "a4", "title": "WebSerial HIL Telemetry & Anomaly Sentinel", "domain": "iot_bus", "difficulty": "Advanced", "min_score": 80}
        ]
    }
}


class PersonalizedLearningEngine:
    """
    Backend engine for Feature 201 (Personalized Dashboard) & Feature 202 (Adaptive Learning Path).
    Strictly follows hardware safety: SQLite WAL, passive CPU, zero continuous background polling.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_db(self) -> None:
        with self._lock:
            conn = self._get_connection()
            try:
                # Student Profiles & Target Career Goals
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS student_learning_profiles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT UNIQUE NOT NULL,
                        student_name TEXT NOT NULL,
                        department TEXT NOT NULL,
                        target_career TEXT NOT NULL,
                        weekly_goal_hours REAL NOT NULL,
                        study_streak_days INTEGER DEFAULT 0,
                        total_xp INTEGER DEFAULT 0,
                        updated_at TEXT NOT NULL
                    );
                """)

                # Adaptive Diagnostic Quiz Attempts
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS adaptive_quiz_attempts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        domain_id TEXT NOT NULL,
                        quiz_title TEXT NOT NULL,
                        score REAL NOT NULL,
                        max_score REAL NOT NULL,
                        percentage REAL NOT NULL,
                        weak_topics_json TEXT NOT NULL,
                        attempted_at TEXT NOT NULL
                    );
                """)

                # Adaptive Recommendations
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS adaptive_learning_recommendations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        milestone_id TEXT NOT NULL,
                        recommended_action TEXT NOT NULL,
                        priority_level TEXT NOT NULL,
                        reason TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)

                # Seed default student if not present
                cur = conn.execute("SELECT id FROM student_learning_profiles WHERE student_id = ?", ("2023MITEC042",))
                if not cur.fetchone():
                    now = datetime.now(timezone.utc).isoformat()
                    conn.execute("""
                        INSERT INTO student_learning_profiles (
                            student_id, student_name, department, target_career,
                            weekly_goal_hours, study_streak_days, total_xp, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "2023MITEC042",
                        "Ashok Kumar A",
                        "Department of Electronics Engineering",
                        "embedded_firmware_architect",
                        12.5,
                        14,
                        4950,
                        now
                    ))

                conn.commit()
            finally:
                conn.close()

    def get_student_profile(self, student_id: str = "2023MITEC042") -> Dict[str, Any]:
        """Retrieve student profile with career target and study streak."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.execute("""
                    SELECT student_id, student_name, department, target_career,
                           weekly_goal_hours, study_streak_days, total_xp, updated_at
                    FROM student_learning_profiles WHERE student_id = ?
                """, (student_id,))
                row = cur.fetchone()
                if row:
                    return dict(row)
                return {
                    "student_id": student_id,
                    "student_name": "Ashok Kumar A",
                    "department": "Department of Electronics Engineering",
                    "target_career": "embedded_firmware_architect",
                    "weekly_goal_hours": 12.5,
                    "study_streak_days": 14,
                    "total_xp": 4950,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            finally:
                conn.close()

    def update_target_career(self, student_id: str, career_key: str) -> Dict[str, Any]:
        """Update student's career objective (Feature 202)."""
        if career_key not in CAREER_TRACKS:
            raise ValueError(f"Invalid career track '{career_key}'. Available: {list(CAREER_TRACKS.keys())}")

        with self._lock:
            conn = self._get_connection()
            try:
                now = datetime.now(timezone.utc).isoformat()
                conn.execute("""
                    UPDATE student_learning_profiles
                    SET target_career = ?, updated_at = ?
                    WHERE student_id = ?
                """, (career_key, now, student_id))
                conn.commit()
                return {
                    "status": "success",
                    "student_id": student_id,
                    "target_career": career_key,
                    "career_info": CAREER_TRACKS[career_key]
                }
            finally:
                conn.close()

    def log_quiz_attempt(
        self,
        student_id: str,
        domain_id: str,
        quiz_title: str,
        score: float,
        max_score: float,
        weak_topics: List[str]
    ) -> Dict[str, Any]:
        """Record diagnostic quiz results and update domain mastery telemetry."""
        if max_score <= 0:
            raise ValueError("max_score must be greater than zero.")
        percentage = round((score / max_score) * 100.0, 1)

        with self._lock:
            conn = self._get_connection()
            try:
                now = datetime.now(timezone.utc).isoformat()
                conn.execute("""
                    INSERT INTO adaptive_quiz_attempts (
                        student_id, domain_id, quiz_title, score, max_score, percentage,
                        weak_topics_json, attempted_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    student_id,
                    domain_id,
                    quiz_title,
                    score,
                    max_score,
                    percentage,
                    json.dumps(weak_topics),
                    now
                ))
                conn.commit()
                return {
                    "status": "logged",
                    "student_id": student_id,
                    "domain_id": domain_id,
                    "percentage": percentage,
                    "weak_topics": weak_topics,
                    "attempted_at": now
                }
            finally:
                conn.close()

    def calculate_domain_mastery(self, student_id: str = "2023MITEC042") -> List[Dict[str, Any]]:
        """
        Calculate mastery percentage across 5 core ECE domains based on quiz history
        and course milestones.
        """
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.execute("""
                    SELECT domain_id, AVG(percentage) as avg_score, COUNT(*) as attempts
                    FROM adaptive_quiz_attempts
                    WHERE student_id = ?
                    GROUP BY domain_id
                """, (student_id,))
                scores_by_domain = {row["domain_id"]: (row["avg_score"], row["attempts"]) for row in cur.fetchall()}

                # Base baseline mastery levels (pre-populated for student profile)
                default_baselines = {
                    "embedded_rtos": 88.0,
                    "digital_vlsi": 76.5,
                    "analog_rf": 71.0,
                    "tinyml_edge": 82.5,
                    "iot_bus": 91.0
                }

                mastery_list = []
                for domain in ECE_DOMAINS:
                    d_id = domain["id"]
                    if d_id in scores_by_domain:
                        avg_score, attempts = scores_by_domain[d_id]
                        # Blend baseline with recent quiz attempts
                        mastery = round((default_baselines.get(d_id, 75.0) * 0.4) + (avg_score * 0.6), 1)
                    else:
                        mastery = default_baselines.get(d_id, 75.0)
                        attempts = 1

                    mastery_list.append({
                        "domain_id": d_id,
                        "name": domain["name"],
                        "code": domain["code"],
                        "credits": domain["credits"],
                        "mastery_percentage": min(100.0, max(0.0, mastery)),
                        "status": "Advanced" if mastery >= 85 else "Proficient" if mastery >= 75 else "Needs Review",
                        "attempts_count": attempts,
                        "topics": domain["topics"]
                    })

                return mastery_list
            finally:
                conn.close()

    def detect_cognitive_gaps(self, student_id: str = "2023MITEC042") -> List[Dict[str, Any]]:
        """
        Identify high-priority academic weaknesses from quiz errors and prerequisite dependencies.
        (Feature 201).
        """
        mastery = self.calculate_domain_mastery(student_id)
        gaps = []

        # Find domains with mastery < 80%
        for d in mastery:
            if d["mastery_percentage"] < 80.0:
                gaps.append({
                    "domain_id": d["domain_id"],
                    "domain_name": d["name"],
                    "mastery": d["mastery_percentage"],
                    "urgency": "High" if d["mastery_percentage"] < 75.0 else "Medium",
                    "focus_topic": d["topics"][0],
                    "recommendation": f"Complete diagnostic drill on '{d['topics'][0]}' to exceed 80% competency threshold."
                })

        # Add simulated syllabus trap gap if none detected
        if not gaps:
            gaps.append({
                "domain_id": "analog_rf",
                "domain_name": "Analog Integrated Circuits & Signals",
                "mastery": 74.0,
                "urgency": "High",
                "focus_topic": "Op-Amp 741 Miller Compensation & Pole Splitting",
                "recommendation": "Review second-stage dominant pole shift and phase margin derivation in LIC."
            })

        return gaps

    def generate_adaptive_learning_path(self, student_id: str = "2023MITEC042") -> Dict[str, Any]:
        """
        Dynamically synthesize next recommended learning path based on student's target career
        and current domain mastery (Feature 202).
        """
        profile = self.get_student_profile(student_id)
        career_key = profile.get("target_career", "embedded_firmware_architect")
        career_info = CAREER_TRACKS.get(career_key, CAREER_TRACKS["embedded_firmware_architect"])

        mastery_map = {d["domain_id"]: d["mastery_percentage"] for d in self.calculate_domain_mastery(student_id)}

        evaluated_milestones = []
        next_recommended = None

        for idx, m in enumerate(career_info["milestones"]):
            current_mastery = mastery_map.get(m["domain"], 70.0)
            is_completed = current_mastery >= m["min_score"]

            status = "Completed" if is_completed else "In Progress"
            if not is_completed and next_recommended is None:
                status = "Recommended Next"
                next_recommended = {
                    "milestone_id": m["id"],
                    "title": m["title"],
                    "domain": m["domain"],
                    "difficulty": m["difficulty"],
                    "current_mastery": current_mastery,
                    "target_score": m["min_score"],
                    "estimated_hours": 3.5,
                    "reason": f"Required prerequisite for {career_info['title']}. Current mastery ({current_mastery}%) below {m['min_score']}% threshold."
                }
            elif not is_completed:
                status = "Locked (Prerequisite Required)"

            evaluated_milestones.append({
                "step": idx + 1,
                "milestone_id": m["id"],
                "title": m["title"],
                "domain": m["domain"],
                "difficulty": m["difficulty"],
                "status": status,
                "current_mastery": current_mastery,
                "required_score": m["min_score"]
            })

        # Fallback if all completed
        if next_recommended is None:
            next_recommended = {
                "milestone_id": "capstone_adv",
                "title": "IEEE Capstone Journal Synthesis & Hardware Verification",
                "domain": "embedded_rtos",
                "difficulty": "Hardcore",
                "current_mastery": 95.0,
                "target_score": 90,
                "estimated_hours": 6.0,
                "reason": "All core career prerequisites fulfilled! Ready for peer-reviewed IEEE publication."
            }

        return {
            "student_id": student_id,
            "target_career": career_key,
            "career_title": career_info["title"],
            "target_companies": career_info["target_companies"],
            "next_recommended_action": next_recommended,
            "milestone_path": evaluated_milestones
        }
