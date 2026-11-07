"""
========================================================================================
VoltCore Apex Academia - Technical Viva Voce & Oral Assessment Simulator
Module: backend/viva_simulator_engine.py
Platform Lead: Ashok Kumar A
Standards: Outcome-Based Education (OBE) • Bloom's Taxonomy • Autonomous Engineering Cluster
Architecture: SQLite WAL Mode • Deterministic Semantic Evaluation • Passive CPU
========================================================================================
"""

import os
import re
import json
import sqlite3
import datetime
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")

# Standard Technical Viva Voce Question Catalog
VIVA_QUESTIONS = [
    {
        "id": "VIVA_01_NVIC_LATENCY",
        "topic": "ARM Cortex-M Interrupt Architecture & NVIC",
        "question": "Explain the architectural mechanisms contributing to ARM Cortex-M interrupt entry latency and how NVIC priority grouping differentiates preemption priority from subpriority.",
        "bloom_level": "Level 4: Analyze",
        "max_marks": 10.0,
        "key_concepts": [
            "stacking", "12 cycles", "tail-chaining", "late-arrival",
            "preemption priority", "subpriority", "aircr prigroup", "nested"
        ],
        "rubric": {
            "core_depth": 5.0,
            "keyword_precision": 3.0,
            "clarity_and_insight": 2.0
        },
        "model_answer": "ARM Cortex-M4 features a deterministic 12-cycle interrupt latency achieved through automatic hardware stack framing of 8 registers (R0-R3, R12, LR, PC, xPSR) onto the current stack. Features like tail-chaining reduce latency to just 6 cycles between consecutive interrupts without redundant unstacking. The AIRCR PRIGROUP register divides the 8-bit priority field into preemption priority (which allows an incoming interrupt to immediately preempt an active ISR) and subpriority (which resolves simultaneous pending requests without preemption)."
    },
    {
        "id": "VIVA_02_I2C_STRETCHING",
        "topic": "I2C Physical Layer & Bus Recovery",
        "question": "Why does the I2C physical layer require open-drain output drivers with pull-up resistors, and what causes an I2C slave to perform clock stretching?",
        "bloom_level": "Level 3: Apply",
        "max_marks": 10.0,
        "key_concepts": [
            "open-drain", "pull-up", "wired-and", "bus contention",
            "clock stretching", "scl low", "slow peripheral"
        ],
        "rubric": {
            "core_depth": 5.0,
            "keyword_precision": 3.0,
            "clarity_and_insight": 2.0
        },
        "model_answer": "I2C uses open-drain NMOS transistors paired with external pull-up resistors to create a wired-AND physical bus. This ensures electrical safety: if two masters drive simultaneously, zero short-circuit currents occur during multi-master arbitration. Clock stretching occurs when a slower slave device holds the SCL line LOW after an ACK bit to pause transmission while completing an internal operation, such as an ADC conversion or Flash write buffer flush. The master pauses until SCL is released."
    },
    {
        "id": "VIVA_03_STA_METASTABILITY",
        "topic": "Static Timing Analysis (STA) & FPGA Timing Closure",
        "question": "Define Setup Time and Hold Time in synchronous flip-flops. Why cannot a hold-time violation be resolved by simply reducing the system clock frequency, and how must silicon designers fix it?",
        "bloom_level": "Level 4: Analyze",
        "max_marks": 10.0,
        "key_concepts": [
            "setup time", "hold time", "metastability", "clock skew",
            "insert delay buffers", "independent of clock period", "t_co + t_logic >= t_hold"
        ],
        "rubric": {
            "core_depth": 5.0,
            "keyword_precision": 3.0,
            "clarity_and_insight": 2.0
        },
        "model_answer": "Setup time (T_su) is the minimum time data must remain stable before the active clock edge; hold time (T_h) is the minimum duration data must remain stable after the clock edge to prevent internal flip-flop metastability. Setup slack depends on clock period (T_clk - T_crit), so reducing clock frequency fixes setup violations. However, hold time is evaluated on the exact same clock edge (T_co + T_logic >= T_h + T_skew) and is completely independent of clock frequency. A hold violation means data changed too quickly and can only be resolved by inserting delay buffers or routing delay into the short data path."
    },
    {
        "id": "VIVA_04_FREERTOS_PENDSV",
        "topic": "SysTick & PendSV Real-Time Context Switching",
        "question": "In FreeRTOS on Cortex-M, why does the kernel defer task context switching to the PendSV exception rather than performing it directly inside the SysTick interrupt service routine?",
        "bloom_level": "Level 5: Evaluate",
        "max_marks": 10.0,
        "key_concepts": [
            "pendsv lowest priority", "systick", "context switch", "interrupt preemption",
            "prevent nesting", "msp to psp", "tail-chaining"
        ],
        "rubric": {
            "core_depth": 5.0,
            "keyword_precision": 3.0,
            "clarity_and_insight": 2.0
        },
        "model_answer": "If a context switch were performed directly inside the SysTick ISR while a higher-priority hardware ISR (such as a motor control PWM or UART DMA handler) was preempted, the task context switch would corrupt or delay time-critical ISR execution. FreeRTOS solves this by setting PendSV to the absolute lowest priority (0xFF). SysTick sets the PendSV bit; ARM hardware waits until all higher-priority ISRs finish executing, and only then executes PendSV to safely swap Process Stack Pointers (PSP) and Task Control Blocks (TCB) without delaying hardware interrupts."
    },
    {
        "id": "VIVA_05_ADC_DMA_STREAMING",
        "topic": "SAR ADC Calibration, Sampling Time & DMA Overrun",
        "question": "How does source signal impedance affect the required SAR ADC sampling time, and how does circular double-buffering with Half-Transfer interrupts prevent telemetry buffer overrun?",
        "bloom_level": "Level 4: Analyze",
        "max_marks": 10.0,
        "key_concepts": [
            "sampling capacitor", "input impedance", "rc charging time",
            "circular buffer", "half-transfer interrupt", "transfer-complete", "overrun"
        ],
        "rubric": {
            "core_depth": 5.0,
            "keyword_precision": 3.0,
            "clarity_and_insight": 2.0
        },
        "model_answer": "The internal sample-and-hold circuit consists of an analog switch resistance and sampling capacitor (typically 4-10 pF). High external source impedance (R_AIN) increases the RC time constant, requiring a longer sampling time (more ADC clock cycles in SMPR) to charge the internal capacitor to within 0.5 LSB of the true voltage. Circular DMA double-buffering uses a contiguous SRAM buffer where the DMA controller emits a Half-Transfer (HT) interrupt at 50% filling, allowing the CPU to process Buffer A while the DMA hardware continues streaming into Buffer B. When Transfer-Complete (TC) fires, the CPU processes Buffer B while DMA wraps around to Buffer A, completely eliminating buffer overrun."
    }
]


class VivaVoceSimulatorEngine:
    """
    Lightweight, AI-aligned Technical Viva Voce simulation engine.
    Scores student audio/text responses against rubric parameters, semantic
    keywords, and Bloom's Taxonomy cognitive benchmarks with SQLite WAL persistence.
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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS technical_viva_evaluations (
                    id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    student_answer TEXT NOT NULL,
                    total_score REAL NOT NULL,
                    max_marks REAL DEFAULT 10.0,
                    bloom_attainment TEXT,
                    rubric_scores_json TEXT NOT NULL,
                    missing_concepts_json TEXT,
                    feedback TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
        finally:
            conn.close()

    def get_questions(self) -> List[Dict[str, Any]]:
        return VIVA_QUESTIONS

    def evaluate_response(
        self,
        question_id: str,
        student_answer: str,
        student_id: str = "2023MITEC042"
    ) -> Dict[str, Any]:
        """
        Evaluates student verbal/written response against question key concepts.
        """
        question = next((q for q in VIVA_QUESTIONS if q["id"] == question_id), VIVA_QUESTIONS[0])
        text_clean = student_answer.lower()

        # Concept matching
        key_concepts = question["key_concepts"]
        matched_concepts = []
        missing_concepts = []

        for concept in key_concepts:
            pattern = re.escape(concept.lower())
            if re.search(r'\b' + pattern + r'\b', text_clean) or concept.lower() in text_clean:
                matched_concepts.append(concept)
            else:
                missing_concepts.append(concept)

        coverage_ratio = len(matched_concepts) / max(1, len(key_concepts))

        # Rubric scoring
        # Core depth (0 - 5.0)
        depth_score = round(min(5.0, coverage_ratio * 5.0 + (0.5 if len(text_clean.split()) > 30 else 0.0)), 1)
        # Keyword precision (0 - 3.0)
        precision_score = round(min(3.0, (len(matched_concepts) / max(1, len(key_concepts))) * 3.0), 1)
        # Clarity & Insight (0 - 2.0)
        clarity_score = 2.0 if len(text_clean.split()) >= 25 else (1.5 if len(text_clean.split()) >= 10 else 1.0)

        total_score = round(depth_score + precision_score + clarity_score, 1)
        total_score = min(question["max_marks"], total_score)

        # Bloom's Taxonomy Attainment
        target_bloom = question["bloom_level"]
        if total_score >= 8.0:
            attainment_status = f"MASTERED ({target_bloom})"
            verdict = "EXEMPLARY TECHNICAL RIGOR"
        elif total_score >= 6.0:
            attainment_status = f"ATTAINED ({target_bloom})"
            verdict = "COMPETENT ENGINEERING GRASP"
        else:
            attainment_status = "PARTIAL ATTAINMENT"
            verdict = "REVISION RECOMMENDED"

        # Constructive Feedback
        feedback_lines = []
        if matched_concepts:
            feedback_lines.append(f"Strong grasp demonstrated on concepts: {', '.join(matched_concepts)}.")
        if missing_concepts:
            feedback_lines.append(f"To reach full master level, incorporate: {', '.join(missing_concepts)}.")
        feedback_lines.append(f"Consult benchmark model answer for full microarchitectural derivation.")

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        eval_id = f"VIVA_{student_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}_{os.urandom(3).hex()}"

        rubric_breakdown = {
            "core_depth": depth_score,
            "keyword_precision": precision_score,
            "clarity_and_insight": clarity_score
        }

        # Persist to SQLite WAL
        conn = self._get_connection()
        try:
            conn.execute("""
                INSERT INTO technical_viva_evaluations
                (id, student_id, question_id, student_answer, total_score, max_marks, bloom_attainment, rubric_scores_json, missing_concepts_json, feedback, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                eval_id, student_id, question["id"], student_answer,
                total_score, question["max_marks"], attainment_status,
                json.dumps(rubric_breakdown), json.dumps(missing_concepts),
                " ".join(feedback_lines), now_str
            ))
            conn.commit()
        finally:
            conn.close()

        return {
            "evaluation_id": eval_id,
            "question_id": question["id"],
            "topic": question["topic"],
            "total_score": total_score,
            "max_marks": question["max_marks"],
            "percentage": round((total_score / question["max_marks"]) * 100.0, 1),
            "verdict": verdict,
            "bloom_level": target_bloom,
            "bloom_attainment": attainment_status,
            "rubric_breakdown": rubric_breakdown,
            "matched_concepts": matched_concepts,
            "missing_concepts": missing_concepts,
            "feedback": " ".join(feedback_lines),
            "model_answer": question["model_answer"],
            "created_at": now_str
        }

    def get_history(self, student_id: str, limit: int = 15) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, question_id, total_score, max_marks, bloom_attainment, feedback, created_at
                FROM technical_viva_evaluations
                WHERE student_id = ?
                ORDER BY created_at DESC LIMIT ?;
            """, (student_id, limit))
            rows = cur.fetchall()
            return [{
                "id": r[0],
                "question_id": r[1],
                "total_score": r[2],
                "max_marks": r[3],
                "bloom_attainment": r[4],
                "feedback": r[5],
                "created_at": r[6]
            } for r in rows]
        finally:
            conn.close()


viva_simulator_engine = VivaVoceSimulatorEngine()
