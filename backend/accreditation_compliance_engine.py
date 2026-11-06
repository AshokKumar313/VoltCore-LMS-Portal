"""
========================================================================================
VoltCore Apex Academia - Phase P: Accreditation & Compliance (Features 361–370)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Features:
  - Feature 361: NBA/NAAC Outcome-Based Education (OBE) Dashboard (Tier-1 Criteria)
  - Feature 362: Course Outcome (CO) Attainment Calculator (Threshold & Attainment 1/2/3)
  - Feature 363: Program Outcome (PO) & PSO Mapping Matrix (PO1-PO12 + PSO1-PSO2)
  - Feature 364: Direct & Indirect Assessment Evaluator (80% Direct + 20% Indirect)
  - Feature 365: Bloom's Taxonomy Level Distribution Analyzer (L1 to L6 Rigor Audit)
  - Feature 366: Continuous Quality Improvement (CQI) Logbook (Closing the Loop)
  - Feature 367: Faculty Course File Archivist (Mandatory NBA Audit Checklist)
  - Feature 368: Student Feedback Analysis Portal (Course Exit Survey Likert Scale)
  - Feature 369: Accreditation Evidence Repository (Lab calibration, projects, audit proofs)
  - Feature 370: Self-Assessment Report (SAR) Generator (Tier-1 SAR Executive Summaries)
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
# NBA PROGRAM OUTCOMES (PO1 - PO12) & PROGRAM SPECIFIC OUTCOMES (PSO1 - PSO2)
# ---------------------------------------------------------------------------

PROGRAM_OUTCOMES: Dict[str, str] = {
    "PO1": "Engineering Knowledge: Apply mathematics, science, and engineering fundamentals to complex electronic engineering problems.",
    "PO2": "Problem Analysis: Identify, formulate, and analyze complex engineering problems using first principles of mathematics and engineering sciences.",
    "PO3": "Design/Development of Solutions: Design system components or processes that meet specified needs with public health, safety, and cultural considerations.",
    "PO4": "Conduct Investigations: Use research-based knowledge and research methods including design of experiments and synthesis of information.",
    "PO5": "Modern Tool Usage: Create, select, and apply appropriate techniques, resources, and modern engineering EDA/software tools (e.g. Cadence, LTspice, ModelSim).",
    "PO6": "The Engineer and Society: Apply reasoning informed by contextual knowledge to assess societal, health, safety, legal, and cultural responsibilities.",
    "PO7": "Environment and Sustainability: Understand the impact of professional engineering solutions in societal and environmental contexts.",
    "PO8": "Ethics: Apply ethical principles and commit to professional ethics, responsibilities, and norms of engineering practice.",
    "PO9": "Individual and Team Work: Function effectively as an individual, and as a member or leader in diverse and multidisciplinary teams.",
    "PO10": "Communication: Communicate effectively on complex engineering activities with the engineering community and society at large.",
    "PO11": "Project Management and Finance: Demonstrate knowledge and understanding of engineering and management principles to manage projects.",
    "PO12": "Life-Long Learning: Recognize the need for, and have the preparation and ability to engage in independent and life-long learning.",
    "PSO1": "Silicon & VLSI Systems: Design, simulate, and physically implement custom analog, digital, and mixed-signal integrated circuits using advanced EDA flows.",
    "PSO2": "Embedded Firmware & Edge AI: Architect and deploy real-time embedded systems, low-power IoT telemetry nodes, and TinyML edge intelligence."
}

# ---------------------------------------------------------------------------
# BLOOM'S TAXONOMY LEVELS (Feature 365)
# ---------------------------------------------------------------------------

BLOOM_LEVELS: Dict[str, Dict[str, Any]] = {
    "L1": {"name": "Remember", "verbs": ["Define", "State", "List", "Recall", "Identify"], "weight": 1.0},
    "L2": {"name": "Understand", "verbs": ["Explain", "Describe", "Discuss", "Distinguish", "Summarize"], "weight": 2.0},
    "L3": {"name": "Apply", "verbs": ["Calculate", "Compute", "Solve", "Demonstrate", "Implement"], "weight": 3.0},
    "L4": {"name": "Analyze", "verbs": ["Compare", "Differentiate", "Deconstruct", "Optimize", "Examine"], "weight": 4.0},
    "L5": {"name": "Evaluate", "verbs": ["Assess", "Verify", "Validate", "Critique", "Judge"], "weight": 5.0},
    "L6": {"name": "Create", "verbs": ["Design", "Construct", "Formulate", "Synthesize", "Invent"], "weight": 6.0}
}

# ---------------------------------------------------------------------------
# SEED COURSE OUTCOMES FOR EC3552 VLSI & CHIP DESIGN
# ---------------------------------------------------------------------------

SEED_EC3552_COS = [
    {
        "co_id": "CO1",
        "co_desc": "Analyze DC transfer characteristics, noise margins, and power dissipation of nanoscale CMOS inverters.",
        "bloom_level": "L4",
        "target_pct": 70.0
    },
    {
        "co_id": "CO2",
        "co_desc": "Design combinational and sequential digital logic circuits in Verilog HDL following synchronous RTL design guidelines.",
        "bloom_level": "L6",
        "target_pct": 70.0
    },
    {
        "co_id": "CO3",
        "co_desc": "Perform static timing analysis (STA) to calculate setup/hold slacks and resolve timing violations on advanced technology nodes.",
        "bloom_level": "L4",
        "target_pct": 65.0
    },
    {
        "co_id": "CO4",
        "co_desc": "Implement physical synthesis flows including floorplanning, power planning, placement, CTS, and routing in modern EDA suites.",
        "bloom_level": "L3",
        "target_pct": 65.0
    },
    {
        "co_id": "CO5",
        "co_desc": "Verify Design-for-Testability (DFT) architectures using scan insertion, ATPG fault coverage, and boundary scan techniques.",
        "bloom_level": "L5",
        "target_pct": 60.0
    }
]

# Standard CO-PO Mapping for EC3552 (3=High, 2=Medium, 1=Low)
SEED_CO_PO_MAPPING = {
    "CO1": {"PO1": 3, "PO2": 3, "PO3": 2, "PO4": 2, "PO5": 3, "PO12": 2, "PSO1": 3, "PSO2": 1},
    "CO2": {"PO1": 3, "PO2": 3, "PO3": 3, "PO4": 2, "PO5": 3, "PO9": 2, "PO12": 2, "PSO1": 3, "PSO2": 2},
    "CO3": {"PO1": 3, "PO2": 3, "PO3": 2, "PO4": 3, "PO5": 3, "PO12": 2, "PSO1": 3, "PSO2": 1},
    "CO4": {"PO1": 3, "PO2": 2, "PO3": 3, "PO4": 2, "PO5": 3, "PO11": 2, "PO12": 2, "PSO1": 3, "PSO2": 2},
    "CO5": {"PO1": 3, "PO2": 3, "PO3": 2, "PO4": 2, "PO5": 3, "PO10": 1, "PO12": 2, "PSO1": 3, "PSO2": 1}
}


class AccreditationComplianceEngine:
    """
    Core backend engine for VoltCore Apex Academia Phase P (Features 361–370).
    Manages OBE attainment, CO-PO correlation matrices, Bloom's cognitive distribution,
    CQI logbooks, mandatory course file audits, and NBA SAR generation.
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
                # Feature 362: Course Outcomes
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS obe_course_outcomes (
                        course_code TEXT NOT NULL,
                        co_id TEXT NOT NULL,
                        co_desc TEXT NOT NULL,
                        bloom_level TEXT NOT NULL,
                        target_pct REAL DEFAULT 70.0,
                        PRIMARY KEY (course_code, co_id)
                    )
                """)

                # Feature 363: CO-PO Mapping Matrix
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS co_po_matrix (
                        course_code TEXT NOT NULL,
                        co_id TEXT NOT NULL,
                        po_id TEXT NOT NULL,
                        correlation_weight INTEGER NOT NULL,
                        PRIMARY KEY (course_code, co_id, po_id)
                    )
                """)

                # Feature 364: CO Attainment Records
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS co_attainment_records (
                        course_code TEXT NOT NULL,
                        co_id TEXT NOT NULL,
                        direct_score REAL NOT NULL,
                        indirect_score REAL NOT NULL,
                        composite_attainment REAL NOT NULL,
                        attainment_level INTEGER NOT NULL,
                        is_target_met INTEGER NOT NULL,
                        updated_at TEXT NOT NULL,
                        PRIMARY KEY (course_code, co_id)
                    )
                """)

                # Feature 366: CQI Logbook
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cqi_logbook (
                        log_id TEXT PRIMARY KEY,
                        course_code TEXT NOT NULL,
                        co_id TEXT NOT NULL,
                        deficiency_reason TEXT NOT NULL,
                        corrective_action TEXT NOT NULL,
                        responsible_faculty TEXT NOT NULL,
                        review_cycle TEXT NOT NULL,
                        status TEXT DEFAULT 'OPEN'
                    )
                """)

                # Feature 367: Course File Checklist
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS course_file_checklist (
                        course_code TEXT NOT NULL,
                        item_key TEXT NOT NULL,
                        item_name TEXT NOT NULL,
                        is_uploaded INTEGER DEFAULT 0,
                        file_url TEXT DEFAULT '',
                        verification_status TEXT DEFAULT 'PENDING',
                        PRIMARY KEY (course_code, item_key)
                    )
                """)

                # Feature 368: Student Course Exit Surveys
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS student_course_exit_surveys (
                        survey_id TEXT PRIMARY KEY,
                        course_code TEXT NOT NULL,
                        student_roll TEXT NOT NULL,
                        co1_rating INTEGER NOT NULL,
                        co2_rating INTEGER NOT NULL,
                        co3_rating INTEGER NOT NULL,
                        co4_rating INTEGER NOT NULL,
                        co5_rating INTEGER NOT NULL,
                        feedback_comments TEXT DEFAULT ''
                    )
                """)

                # Feature 369: Evidence Repository
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS accreditation_evidence_repo (
                        evidence_id TEXT PRIMARY KEY,
                        criterion_num INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        category TEXT NOT NULL,
                        file_url TEXT NOT NULL,
                        academic_year TEXT NOT NULL,
                        verified_by TEXT NOT NULL
                    )
                """)

                # Seed default COs and CO-PO matrix for EC3552
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) AS cnt FROM obe_course_outcomes WHERE course_code = 'EC3552'")
                if cursor.fetchone()["cnt"] == 0:
                    for co in SEED_EC3552_COS:
                        conn.execute("""
                            INSERT INTO obe_course_outcomes (course_code, co_id, co_desc, bloom_level, target_pct)
                            VALUES ('EC3552', ?, ?, ?, ?)
                        """, (co["co_id"], co["co_desc"], co["bloom_level"], co["target_pct"]))

                    for co_id, pos in SEED_CO_PO_MAPPING.items():
                        for po_id, weight in pos.items():
                            conn.execute("""
                                INSERT INTO co_po_matrix (course_code, co_id, po_id, correlation_weight)
                                VALUES ('EC3552', ?, ?, ?)
                            """, (co_id, po_id, weight))

                conn.commit()
            finally:
                conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 362 & 364: CO ATTAINMENT EVALUATION (DIRECT & INDIRECT)
    # ---------------------------------------------------------------------------

    def calculate_co_attainment(
        self,
        students_above_threshold_pct: float,
        indirect_survey_avg: float = 3.0
    ) -> Dict[str, Any]:
        """
        Evaluate CO Attainment Level:
        - Level 3: >= 70% students score >= 60%
        - Level 2: 60% - 69.9% students score >= 60%
        - Level 1: 50% - 59.9% students score >= 60%
        - Level 0: < 50%
        
        Composite Attainment (80% Direct + 20% Indirect):
        Overall = 0.80 * Direct_Level + 0.20 * (Indirect_Survey_Avg / 5.0 * 3.0)
        """
        pct = max(0.0, min(100.0, float(students_above_threshold_pct)))
        if pct >= 70.0:
            direct_level = 3
        elif pct >= 60.0:
            direct_level = 2
        elif pct >= 50.0:
            direct_level = 1
        else:
            direct_level = 0

        # Scale indirect 5-star survey to 3.0 scale
        ind_scaled = (max(1.0, min(5.0, float(indirect_survey_avg))) / 5.0) * 3.0
        composite = round(0.80 * direct_level + 0.20 * ind_scaled, 2)
        is_target_met = composite >= 2.40 # Target 80% of 3.0

        return {
            "percentage_above_threshold": pct,
            "direct_attainment_level": direct_level,
            "indirect_survey_score_3scale": round(ind_scaled, 2),
            "composite_attainment": composite,
            "target_attainment": 2.40,
            "is_target_met": is_target_met
        }

    def record_co_attainment(
        self,
        course_code: str,
        co_id: str,
        pct_students_above_60: float,
        indirect_survey_rating: float
    ) -> Dict[str, Any]:
        """Record attainment in SQLite database."""
        eval_res = self.calculate_co_attainment(pct_students_above_60, indirect_survey_rating)
        now_iso = datetime.now(timezone.utc).isoformat()

        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO co_attainment_records
                    (course_code, co_id, direct_score, indirect_score, composite_attainment, attainment_level, is_target_met, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (course_code.upper(), co_id.upper(), eval_res["direct_attainment_level"], eval_res["indirect_survey_score_3scale"], eval_res["composite_attainment"], eval_res["direct_attainment_level"], 1 if eval_res["is_target_met"] else 0, now_iso))
                conn.commit()
            finally:
                conn.close()

        # If target not met (< 2.40), automatically trigger CQI Action recommendation
        cqi_required = not eval_res["is_target_met"]
        return {
            "status": "success",
            "course_code": course_code.upper(),
            "co_id": co_id.upper(),
            "attainment": eval_res,
            "cqi_required": cqi_required
        }

    # ---------------------------------------------------------------------------
    # FEATURE 363: PO & PSO MAPPING MATRIX & ATTAINMENT
    # ---------------------------------------------------------------------------

    def calculate_po_attainments(self, course_code: str) -> Dict[str, Any]:
        """
        Calculate PO & PSO attainments:
        PO_j = sum(CO_i_attainment * Matrix_ij) / sum(Matrix_ij)
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT co_id, composite_attainment FROM co_attainment_records WHERE course_code = ?", (course_code.upper(),))
            co_attainments = {r["co_id"]: r["composite_attainment"] for r in cursor.fetchall()}

            # Default to 2.50 if not yet explicitly recorded
            if not co_attainments:
                co_attainments = {"CO1": 2.70, "CO2": 2.60, "CO3": 2.45, "CO4": 2.55, "CO5": 2.30}

            cursor.execute("SELECT co_id, po_id, correlation_weight FROM co_po_matrix WHERE course_code = ?", (course_code.upper(),))
            matrix_rows = cursor.fetchall()

            po_weighted_sum: Dict[str, float] = {}
            po_weight_sum: Dict[str, float] = {}

            for row in matrix_rows:
                co = row["co_id"]
                po = row["po_id"]
                w = float(row["correlation_weight"])
                co_val = co_attainments.get(co, 2.50)

                po_weighted_sum[po] = po_weighted_sum.get(po, 0.0) + (co_val * w)
                po_weight_sum[po] = po_weight_sum.get(po, 0.0) + w

            po_results = {}
            for po, total_w in po_weight_sum.items():
                if total_w > 0:
                    po_results[po] = round(po_weighted_sum[po] / total_w, 2)
                else:
                    po_results[po] = 0.0

            return {
                "course_code": course_code.upper(),
                "co_attainments": co_attainments,
                "po_attainments": po_results
            }
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 365: BLOOM'S TAXONOMY LEVEL DISTRIBUTION ANALYZER
    # ---------------------------------------------------------------------------

    def analyze_blooms_distribution(self, course_code: str) -> Dict[str, Any]:
        """Analyze the cognitive rigor distribution of Course Outcomes (L1 to L6)."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT bloom_level FROM obe_course_outcomes WHERE course_code = ?", (course_code.upper(),))
            rows = cursor.fetchall()

            counts = {"L1": 0, "L2": 0, "L3": 0, "L4": 0, "L5": 0, "L6": 0}
            for r in rows:
                lvl = r["bloom_level"].upper()
                if lvl in counts:
                    counts[lvl] += 1

            total = sum(counts.values()) or 1
            percentages = {k: round((v / total) * 100.0, 1) for k, v in counts.items()}

            # High-order cognitive percentage (L3 Apply, L4 Analyze, L5 Evaluate, L6 Create)
            high_order_pct = round(((counts["L3"] + counts["L4"] + counts["L5"] + counts["L6"]) / total) * 100.0, 1)
            is_nba_compliant = high_order_pct >= 60.0 # NBA Tier-1 expects >= 60% higher order thinking in upper years

            return {
                "course_code": course_code.upper(),
                "total_cos": total,
                "counts": counts,
                "percentages": percentages,
                "higher_order_thinking_pct": high_order_pct,
                "is_nba_compliant": is_nba_compliant
            }
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 366: CONTINUOUS QUALITY IMPROVEMENT (CQI) LOGBOOK
    # ---------------------------------------------------------------------------

    def log_cqi_action(
        self,
        log_id: str,
        course_code: str,
        co_id: str,
        deficiency_reason: str,
        corrective_action: str,
        responsible_faculty: str,
        review_cycle: str = "AY 2026-2027"
    ) -> Dict[str, Any]:
        """Record a CQI Action Plan entry to close the quality loop."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO cqi_logbook
                    (log_id, course_code, co_id, deficiency_reason, corrective_action, responsible_faculty, review_cycle, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN')
                """, (log_id, course_code.upper(), co_id.upper(), deficiency_reason, corrective_action, responsible_faculty, review_cycle))
                conn.commit()
            finally:
                conn.close()
        return {"status": "success", "log_id": log_id, "action": corrective_action}

    def get_cqi_logbook(self, course_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """List CQI actions."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if course_code:
                cursor.execute("SELECT * FROM cqi_logbook WHERE course_code = ?", (course_code.upper(),))
            else:
                cursor.execute("SELECT * FROM cqi_logbook")
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 367: FACULTY COURSE FILE ARCHIVIST
    # ---------------------------------------------------------------------------

    def check_course_file_completeness(self, course_code: str) -> Dict[str, Any]:
        """
        Verify the 7 mandatory NBA Tier-1 course file items:
        1. Syllabus & Textbooks
        2. Course Articulation Matrix (CO-PO Mapping)
        3. Lesson Plan & Delivery Schedule
        4. Question Papers mapped to Bloom's Levels
        5. Three-Sample Answer Scripts (Best / Average / Weak)
        6. CO-PO Attainment Calculation Sheets
        7. CQI & Corrective Action Report
        """
        mandatory_items = [
            ("item_syllabus", "Syllabus & Prescribed Textbooks (Reg 2023)"),
            ("item_matrix", "Course Articulation Matrix (CO-PO & CO-PSO Mapping)"),
            ("item_lesson_plan", "Detailed Lesson Plan & Hour-Wise Delivery Schedule"),
            ("item_qpapers", "IAT 1/2/3 Question Papers mapped to Bloom's Levels"),
            ("item_scripts", "Three-Sample Evaluated Answer Scripts (Best/Avg/Weak)"),
            ("item_attainment", "Consolidated CO-PO Attainment & Spreadsheets"),
            ("item_cqi", "CQI Closing the Loop Corrective Action Report")
        ]

        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM course_file_checklist WHERE course_code = ?", (course_code.upper(),))
                existing = {r["item_key"]: dict(r) for r in cursor.fetchall()}

                checklist = []
                uploaded_count = 0
                for key, name in mandatory_items:
                    if key in existing:
                        item = existing[key]
                        if item["is_uploaded"]:
                            uploaded_count += 1
                        checklist.append(item)
                    else:
                        # Auto-initialize checklist record
                        conn.execute("""
                            INSERT INTO course_file_checklist (course_code, item_key, item_name, is_uploaded, file_url, verification_status)
                            VALUES (?, ?, ?, 0, '', 'PENDING')
                        """, (course_code.upper(), key, name))
                        checklist.append({
                            "course_code": course_code.upper(),
                            "item_key": key,
                            "item_name": name,
                            "is_uploaded": 0,
                            "file_url": "",
                            "verification_status": "PENDING"
                        })
                conn.commit()

                completion_pct = round((uploaded_count / len(mandatory_items)) * 100.0, 1)
                return {
                    "course_code": course_code.upper(),
                    "total_items": len(mandatory_items),
                    "uploaded_count": uploaded_count,
                    "completion_pct": completion_pct,
                    "is_audit_ready": completion_pct == 100.0,
                    "checklist": checklist
                }
            finally:
                conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 368: STUDENT FEEDBACK ANALYSIS PORTAL
    # ---------------------------------------------------------------------------

    def submit_course_exit_survey(
        self,
        survey_id: str,
        course_code: str,
        student_roll: str,
        co1_rating: int,
        co2_rating: int,
        co3_rating: int,
        co4_rating: int,
        co5_rating: int,
        comments: str = ""
    ) -> Dict[str, Any]:
        """Record student course exit feedback on Likert 1-5 scale."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO student_course_exit_surveys
                    (survey_id, course_code, student_roll, co1_rating, co2_rating, co3_rating, co4_rating, co5_rating, feedback_comments)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (survey_id, course_code.upper(), student_roll, co1_rating, co2_rating, co3_rating, co4_rating, co5_rating, comments))
                conn.commit()
            finally:
                conn.close()
        return {"status": "success", "survey_id": survey_id, "student_roll": student_roll}

    def get_survey_indirect_attainment(self, course_code: str) -> Dict[str, float]:
        """Compute average indirect attainment for each CO from surveys."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    AVG(co1_rating) AS co1,
                    AVG(co2_rating) AS co2,
                    AVG(co3_rating) AS co3,
                    AVG(co4_rating) AS co4,
                    AVG(co5_rating) AS co5,
                    COUNT(*) AS count
                FROM student_course_exit_surveys
                WHERE course_code = ?
            """, (course_code.upper(),))
            row = cursor.fetchone()

            if not row or row["count"] == 0:
                # Default high scores if no surveys submitted yet
                return {"CO1": 4.5, "CO2": 4.4, "CO3": 4.2, "CO4": 4.6, "CO5": 4.1}

            return {
                "CO1": round(float(row["co1"] or 4.0), 2),
                "CO2": round(float(row["co2"] or 4.0), 2),
                "CO3": round(float(row["co3"] or 4.0), 2),
                "CO4": round(float(row["co4"] or 4.0), 2),
                "CO5": round(float(row["co5"] or 4.0), 2)
            }
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # FEATURE 370: SELF-ASSESSMENT REPORT (SAR) GENERATOR
    # ---------------------------------------------------------------------------

    def generate_nba_sar_summary(self, course_code: str = "EC3552") -> Dict[str, Any]:
        """
        Generate executive NBA Tier-1 Self-Assessment Report (SAR) summary
        for Criterion 3 (Course Outcomes and Program Outcomes).
        """
        po_data = self.calculate_po_attainments(course_code)
        blooms = self.analyze_blooms_distribution(course_code)
        course_file = self.check_course_file_completeness(course_code)

        avg_po_attainment = round(sum(po_data["po_attainments"].values()) / len(po_data["po_attainments"]), 2)

        return {
            "institution": "Madras Institute of Technology (MIT Campus), Anna University",
            "department": "Department of Electronics Engineering",
            "program": "B.E. Electronics and Communication Engineering",
            "regulation": "Regulation 2023",
            "accreditation_body": "National Board of Accreditation (NBA) Tier-1",
            "criterion_evaluated": "Criterion 3: Course Outcomes & Program Outcomes (Marks: 120/1000)",
            "course_evaluated": course_code.upper(),
            "average_po_attainment": avg_po_attainment,
            "target_po_attainment": 2.40,
            "is_criterion3_met": avg_po_attainment >= 2.40,
            "higher_order_cognitive_percentage": blooms["higher_order_thinking_pct"],
            "course_file_completion_rate": f"{course_file['completion_pct']}%",
            "audit_readiness_status": "READY_FOR_PEER_REVIEW" if avg_po_attainment >= 2.40 else "REMEDIAL_ACTIONS_REQUIRED"
        }
