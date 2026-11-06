"""
========================================================================================
VoltCore Apex Academia - Phase L: Career & Professional Development (Features 321–330)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Features:
  - Feature 321: ECE Career Roadmap (Firmware, VLSI, Analog, RF, Automotive EV)
  - Feature 322: Embedded Systems Skill Tracker (C/C++, RTOS, Buses, Hardware Debug)
  - Feature 323: Semiconductor Industry Learning Track (IC Fab, EUV, Foundries)
  - Feature 324: VLSI Learning Roadmap (RTL to GDSII, Synthesis, STA, DFT, Tapeout)
  - Feature 325: IoT Career Preparation Track (MQTT, LoRaWAN, BLE, TinyML, Security)
  - Feature 326: Technical Interview Question Bank (Qualcomm, TI, Intel, NXP, Bosch)
  - Feature 327: Resume Builder (ATS-Compliant ECE Resume for Campus Recruitment)
  - Feature 328: Technical Skills Assessment (Diagnostic interactive quiz & scoring)
  - Feature 329: Internship Application Tracker (Company, Role, Tier, Status, Stipend)
  - Feature 330: Placement Preparation Dashboard (Campus Day-0/1 countdown, CGPA, Target)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
========================================================================================
"""

import os
import re
import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")

# ---------------------------------------------------------------------------
# ECE CAREER ROADMAP CATALOG (Feature 321)
# ---------------------------------------------------------------------------

CAREER_ROADMAPS: Dict[str, Dict[str, Any]] = {
    "embedded_firmware": {
        "title": "Embedded Systems & Firmware Engineer",
        "domain": "Embedded Systems & IoT",
        "avg_ctc_lpa": "8.5 – 24.0 LPA",
        "top_recruiters": ["Qualcomm", "Texas Instruments", "Bosch", "NXP Semiconductors", "Schneider Electric", "Honeywell"],
        "core_prerequisites": [
            "Bare-metal C and Embedded C++ (volatile, bit manipulation, pointers)",
            "ARM Cortex-M (M0+/M3/M4/M7) & RISC-V register architecture",
            "Bus protocols: I2C, SPI, UART, CAN 2.0B / CAN-FD, Ethernet",
            "Real-Time Operating Systems (FreeRTOS tasks, queues, semaphores, mutexes)",
            "Hardware test equipment: Digital Oscilloscope, Logic Analyzer, JTAG/SWD debuggers"
        ],
        "anna_univ_courses": ["EC3711 Embedded Systems Lab", "EC3451 Linear Integrated Circuits", "EC3561 Comm Systems"]
    },
    "digital_vlsi": {
        "title": "Digital VLSI & ASIC Design Engineer",
        "domain": "Semiconductor & Microelectronics",
        "avg_ctc_lpa": "12.0 – 32.0 LPA",
        "top_recruiters": ["Intel", "NVIDIA", "Qualcomm", "AMD", "MediaTek", "Synopsys", "Cadence"],
        "core_prerequisites": [
            "Hardware Description Languages: Verilog HDL & SystemVerilog",
            "Digital design: Synchronous FSMs, pipelining, clock-domain crossing (CDC)",
            "Static Timing Analysis (STA): Setup time, hold time, slack, clock jitter",
            "Design for Testability (DFT): Scan insertion, boundary scan IEEE 1149.1, ATPG",
            "EDA Workflows: Synopsys Design Compiler, Cadence Genus, Innovus P&R"
        ],
        "anna_univ_courses": ["EC3452 Digital Systems Design", "EC3611 VLSI Design Lab", "Low-Power VLSI Elective"]
    },
    "analog_rf": {
        "title": "Analog Mixed-Signal & RF IC Designer",
        "domain": "Analog & Radio Frequency Systems",
        "avg_ctc_lpa": "14.0 – 36.0 LPA",
        "top_recruiters": ["Texas Instruments", "Analog Devices (ADI)", "Skyworks", "Qorvo", "Broadcom", "Infineon"],
        "core_prerequisites": [
            "CMOS analog building blocks: Current mirrors, differential pairs, bandgap references",
            "Operational Transconductance Amplifiers (OTA) & frequency compensation",
            "RF Front-Ends: Low-Noise Amplifiers (LNA), mixers, LC VCOs, Phase-Locked Loops (PLL)",
            "S-parameters, impedance matching on Smith Charts, 50-ohm transmission lines",
            "Simulation: Cadence Virtuoso Spectre, Keysight ADS, S-parameter VNA measurement"
        ],
        "anna_univ_courses": ["EC3351 Electronic Devices", "EC3451 Linear Integrated Circuits", "RF & Microwave Elective"]
    },
    "automotive_ev": {
        "title": "Automotive Electronics & EV Systems Architect",
        "domain": "Automotive Systems",
        "avg_ctc_lpa": "9.0 – 22.0 LPA",
        "top_recruiters": ["Bosch", "Continental", "Tata Motors / Tata Elxsi", "Aptiv", "Valeo", "Ola Electric"],
        "core_prerequisites": [
            "Automotive networking: CAN-FD, LIN, FlexRay, Automotive Ethernet",
            "AUTOSAR (Automotive Open System Architecture) Classic and Adaptive platform",
            "ISO 26262 Road Vehicles Functional Safety (ASIL A to ASIL D)",
            "Battery Management Systems (BMS): Cell balancing, SOC/SOH Coulomb counting",
            "Model-Based Development: MATLAB/Simulink and Embedded Coder auto-generation"
        ],
        "anna_univ_courses": ["Automotive ECE Elective", "EC3711 Embedded Lab", "Power Electronics"]
    }
}

# ---------------------------------------------------------------------------
# INTERVIEW QUESTION BANK (Feature 326)
# ---------------------------------------------------------------------------

INTERVIEW_QUESTION_BANK: List[Dict[str, Any]] = [
    {
        "q_id": "INT-01",
        "company": "Qualcomm / Texas Instruments",
        "domain": "Embedded C",
        "question": "Explain the difference between 'const int *p', 'int * const p', and 'const int * const p'. Where is each typically utilized?",
        "model_solution": (
            "1. 'const int *p': Pointer to a constant integer. The integer value cannot be modified through p (*p = 10 is illegal), but p itself can point to another address. Used for read-only buffers in drivers.\n"
            "2. 'int * const p': Constant pointer to an integer. The pointer cannot point to another address, but the integer data can be modified (*p = 10 is valid). Used for memory-mapped hardware peripheral registers.\n"
            "3. 'const int * const p': Constant pointer to a constant integer. Neither the address nor the target value can be changed. Used for ROM tables and immutable calibration vectors."
        ),
        "difficulty": "Medium"
    },
    {
        "q_id": "INT-02",
        "company": "Intel / NVIDIA",
        "domain": "Digital VLSI",
        "question": "What is the difference between Setup Time and Hold Time? Which violation is catastrophic in silicon and cannot be fixed by lowering clock frequency?",
        "model_solution": (
            "Setup Time (t_setup) is the minimum duration the data input must remain stable before the active clock edge. Violation condition: T_clk < t_cq + t_comb + t_setup. Setup violations CAN be resolved by reducing clock frequency.\n"
            "Hold Time (t_hold) is the minimum duration data must remain stable AFTER the active clock edge. Violation condition: t_cq + t_comb < t_hold. HOLD TIME VIOLATIONS ARE FATAL IN SILICON! Lowering the clock frequency does not help because both terms are frequency-independent. It must be resolved during physical design by inserting delay buffer cells."
        ),
        "difficulty": "Hard"
    },
    {
        "q_id": "INT-03",
        "company": "Broadcom / MediaTek",
        "domain": "Verilog HDL",
        "question": "Why should non-blocking assignments (<=) always be used for sequential logic and blocking assignments (=) for combinational logic?",
        "model_solution": (
            "Non-blocking assignments evaluate all right-hand sides in the Active simulation region and update left-hand sides in the NBA (Non-Blocking Assignment) region. This guarantees race-free execution when cascading flip-flops (e.g. shift registers). Using blocking assignments inside sequential always @(posedge clk) blocks introduces simulator execution order dependencies, leading to synthesis-simulation mismatches and hardware bugs."
        ),
        "difficulty": "Medium"
    },
    {
        "q_id": "INT-04",
        "company": "NXP / Bosch",
        "domain": "Microcontrollers & RTOS",
        "question": "What is Priority Inversion in a Real-Time Operating System, and how do Priority Inheritance and Priority Ceiling protocols prevent it?",
        "model_solution": (
            "Priority Inversion occurs when a high-priority task is blocked waiting for a shared mutex held by a low-priority task, and an intermediate-priority task preempts the low-priority task, indirectly starving the high-priority task.\n"
            "Priority Inheritance temporarily elevates the priority of the low-priority lock holder to the priority of the highest-priority blocked task until the lock is released.\n"
            "Priority Ceiling pre-assigns each mutex a ceiling priority equal to the highest priority task that may acquire it, preventing deadlocks and bounding priority inversion to at most one lock acquisition."
        ),
        "difficulty": "Hard"
    }
]

# ---------------------------------------------------------------------------
# DATABASE INITIALIZATION (SQLite WAL Mode)
# ---------------------------------------------------------------------------

_db_lock = threading.Lock()

def init_career_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initialize SQLite tables for Phase L Career & Professional Development."""
    with _db_lock:
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            cursor = conn.cursor()

            # 1. Career Skill Progress
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS career_skill_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    skill_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    proficiency_percentage REAL NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 2. Internship Applications Tracker
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS internship_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_id TEXT UNIQUE NOT NULL,
                    student_id TEXT NOT NULL,
                    company TEXT NOT NULL,
                    role TEXT NOT NULL,
                    tier TEXT NOT NULL,
                    stipend_inr REAL DEFAULT 35000.0,
                    status TEXT NOT NULL,
                    deadline_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 3. Placement Readiness
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS placement_readiness (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT UNIQUE NOT NULL,
                    cgpa REAL NOT NULL,
                    aptitude_score REAL DEFAULT 85.0,
                    core_ece_score REAL DEFAULT 90.0,
                    coding_score REAL DEFAULT 80.0,
                    overall_readiness_percentage REAL NOT NULL,
                    target_companies_json TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 4. Student Resumes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS student_resumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resume_id TEXT UNIQUE NOT NULL,
                    student_id TEXT NOT NULL,
                    resume_title TEXT NOT NULL,
                    resume_markdown TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            conn.commit()
        finally:
            conn.close()

# ---------------------------------------------------------------------------
# FEATURE 321: ECE CAREER ROADMAP
# ---------------------------------------------------------------------------

def get_career_roadmap(track_key: str = "embedded_firmware") -> Dict[str, Any]:
    """
    Feature 321: Returns structured career trajectories, salary ranges,
    top recruiters, and prerequisites.
    """
    clean_key = track_key.lower().strip()
    roadmap = CAREER_ROADMAPS.get(clean_key, CAREER_ROADMAPS["embedded_firmware"])
    return {
        "status": "success",
        "track_key": clean_key,
        **roadmap
    }

# ---------------------------------------------------------------------------
# FEATURE 322: EMBEDDED SYSTEMS SKILL TRACKER
# ---------------------------------------------------------------------------

def update_skill_progress(
    student_id: str,
    skill_name: str,
    category: str,
    proficiency_percentage: float,
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """
    Feature 322: Logs student proficiency scores in core ECE skills.
    """
    init_career_db(db_path)
    pct = max(0.0, min(100.0, float(proficiency_percentage)))

    with _db_lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO career_skill_progress (student_id, skill_name, category, proficiency_percentage)
            VALUES (?, ?, ?, ?)
        """, (student_id, skill_name, category, pct))
        conn.commit()
        conn.close()

    return {
        "status": "success",
        "student_id": student_id,
        "skill_name": skill_name,
        "category": category,
        "proficiency_percentage": pct
    }

# ---------------------------------------------------------------------------
# FEATURE 326: TECHNICAL INTERVIEW QUESTION BANK
# ---------------------------------------------------------------------------

def query_interview_questions(domain: str = "all", company: str = "all") -> List[Dict[str, Any]]:
    """
    Feature 326: Queries curated technical interview questions with model answers.
    """
    results = []
    dom_clean = domain.lower().strip()
    comp_clean = company.lower().strip()

    for q in INTERVIEW_QUESTION_BANK:
        if dom_clean != "all" and dom_clean not in q["domain"].lower():
            continue
        if comp_clean != "all" and comp_clean not in q["company"].lower():
            continue
        results.append(q)

    return results or INTERVIEW_QUESTION_BANK

# ---------------------------------------------------------------------------
# FEATURE 327: RESUME BUILDER (ECE ATS-COMPLIANT FORMAT)
# ---------------------------------------------------------------------------

def generate_ece_resume(
    student_name: str = "Ashok Kumar A",
    roll_no: str = "2023MITEC042",
    email: str = "ashokkumar3132008@gmail.com",
    cgpa: float = 8.85,
    flagship_project: str = "VoltCore Apex Academia: Full-Stack ECE LMS & Hardware-in-the-Loop Platform",
    top_skills: Optional[List[str]] = None,
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """
    Feature 327: Synthesizes a standardized, ATS-compliant ECE engineering resume.
    """
    skills = top_skills or [
        "Verilog HDL", "ARM Cortex-M Bare-Metal", "FreeRTOS",
        "C/C++", "Python SciPy", "KiCad PCB Layout", "TinyML"
    ]
    resume_id = f"RES-{roll_no}"

    resume_md = f"""# {student_name}
**Roll No:** {roll_no} | **Email:** {email} | **GitHub:** https://github.com/AshokKumar313
**Institution:** Madras Institute of Technology (MIT) Campus, Anna University, Chennai

---

## EDUCATION
**B.E. Electronics and Communication Engineering** (Regulation 2023)  
*Madras Institute of Technology (MIT) Campus, Anna University*  
- **Cumulative GPA:** {cgpa} / 10.0  
- **Relevant Coursework:** Electronic Devices, Digital Systems Design, Linear Integrated Circuits, Signals & Systems, Communication Systems, Embedded Systems Lab.

## TECHNICAL COMPETENCIES
- **Hardware & Languages:** {', '.join(skills)}
- **EDA & Simulation Tools:** Cadence Virtuoso, Vivado Design Suite, LTspice, ModelSim, KiCad
- **Protocols & Busses:** I2C, SPI, UART, CAN 2.0B, LoRaWAN, MQTT, TCP/IP
- **Laboratory Equipment:** Mixed Signal Oscilloscopes, Spectrum Analyzers, Logic Analyzers, Bench RPS

## FLAGSHIP PROJECTS
### {flagship_project}
- Architected modular educational LMS with 50+ interactive engineering islands covering Digital Logic, Analog Semis, Signals, Embedded Systems, and Laboratory breadboards.
- Implemented client-safe SQLite WAL telemetry engines with zero CPU background throttling.
- Designed automated Bill of Materials (BOM) generator with GST tax and component deratings.

## CERTIFICATIONS & HONORS
- Top Performer: Anna University Department of Electronics Engineering
- NPTEL / SWAYAM Elite Gold: Microprocessors and Microcontrollers
- IEEE Student Member • Lead Architect at VoltCore Systems
"""

    init_career_db(db_path)
    with _db_lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO student_resumes (resume_id, student_id, resume_title, resume_markdown)
            VALUES (?, ?, ?, ?)
        """, (resume_id, roll_no, f"ECE Resume - {student_name}", resume_md))
        conn.commit()
        conn.close()

    return {
        "status": "success",
        "resume_id": resume_id,
        "student_name": student_name,
        "roll_no": roll_no,
        "resume_markdown": resume_md
    }

# ---------------------------------------------------------------------------
# FEATURE 328: TECHNICAL SKILLS ASSESSMENT
# ---------------------------------------------------------------------------

def evaluate_technical_skills_assessment(answers: Dict[str, int]) -> Dict[str, Any]:
    """
    Feature 328: Diagnostic interactive quiz evaluating core ECE skills.
    Answers map question ID (Q1..Q4) to selected option index (0..3).
    """
    answer_key = {
        "Q1": {"correct": 1, "topic": "C Pointers", "weight": 25.0},
        "Q2": {"correct": 2, "topic": "VLSI Timing", "weight": 25.0},
        "Q3": {"correct": 0, "topic": "Verilog Assignments", "weight": 25.0},
        "Q4": {"correct": 3, "topic": "RTOS Scheduling", "weight": 25.0}
    }

    score = 0.0
    detailed_feedback = []

    for q_id, meta in answer_key.items():
        user_choice = answers.get(q_id, -1)
        is_correct = (user_choice == meta["correct"])
        if is_correct:
            score += meta["weight"]
        detailed_feedback.append({
            "question_id": q_id,
            "topic": meta["topic"],
            "is_correct": is_correct,
            "points_earned": meta["weight"] if is_correct else 0.0
        })

    readiness_level = "Tier-1 Day-0 Ready" if score >= 75.0 else "Intermediate Review Needed"

    return {
        "status": "success",
        "total_score": round(score, 1),
        "max_score": 100.0,
        "readiness_level": readiness_level,
        "feedback": detailed_feedback
    }

# ---------------------------------------------------------------------------
# FEATURE 329: INTERNSHIP APPLICATION TRACKER
# ---------------------------------------------------------------------------

def track_internship_application(
    company: str,
    role: str,
    tier: str = "Tier 1",
    stipend_inr: float = 45000.0,
    status: str = "APPLIED",
    deadline_date: Optional[str] = None,
    student_id: str = "2023MITEC042",
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """
    Feature 329: Tracks student internship recruitment pipelines.
    """
    app_id = f"INT-APP-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    init_career_db(db_path)

    with _db_lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO internship_applications 
            (app_id, student_id, company, role, tier, stipend_inr, status, deadline_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (app_id, student_id, company, role, tier, float(stipend_inr), status.upper(), deadline_date))
        conn.commit()
        conn.close()

    return {
        "status": "success",
        "app_id": app_id,
        "student_id": student_id,
        "company": company,
        "role": role,
        "tier": tier,
        "stipend_inr": stipend_inr,
        "app_status": status.upper(),
        "deadline_date": deadline_date
    }

# ---------------------------------------------------------------------------
# FEATURE 330: PLACEMENT PREPARATION DASHBOARD
# ---------------------------------------------------------------------------

def calculate_placement_readiness(
    student_id: str = "2023MITEC042",
    cgpa: float = 8.85,
    aptitude_score: float = 88.0,
    core_ece_score: float = 92.0,
    coding_score: float = 85.0,
    target_companies: Optional[List[str]] = None,
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """
    Feature 330: Computes composite campus placement readiness index.
    Formula: Readiness = 0.35 * CoreECE + 0.25 * Aptitude + 0.25 * Coding + 0.15 * (CGPA * 10)
    """
    targets = target_companies or ["Qualcomm", "Texas Instruments", "Intel", "NXP", "Bosch"]
    cgpa_norm = (cgpa / 10.0) * 100.0
    composite_index = (0.35 * core_ece_score) + (0.25 * aptitude_score) + (0.25 * coding_score) + (0.15 * cgpa_norm)
    composite_index = round(min(100.0, max(0.0, composite_index)), 1)

    init_career_db(db_path)
    with _db_lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO placement_readiness 
            (student_id, cgpa, aptitude_score, core_ece_score, coding_score, overall_readiness_percentage, target_companies_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (student_id, cgpa, aptitude_score, core_ece_score, coding_score, composite_index, json.dumps(targets)))
        conn.commit()
        conn.close()

    return {
        "status": "success",
        "student_id": student_id,
        "cgpa": cgpa,
        "readiness_percentage": composite_index,
        "is_day_zero_eligible": cgpa >= 8.0 and composite_index >= 80.0,
        "target_companies": targets
    }
