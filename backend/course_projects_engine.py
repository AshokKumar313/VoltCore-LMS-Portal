"""
========================================================================================
VoltCore Apex Academia - Projects, Practicals & Progress Tracking Engine (Phase 9)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead & Systems Architect: Ashok Kumar A
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313

Capabilities:
  - Mini-projects and major capstone catalog for priority courses:
      * EC23S01: Numerical and Signal Processing Practice Through Python
      * EC23C03: Electronic Devices
      * EC23E04: Optics and Lasers
      * EC8702:  Embedded Systems
  - Continuous Internal Evaluation (CIE) milestone weightage auditing (sums to 100%)
  - Practical experiment rubric validation (sums to 30 marks)
  - Course completion percentage, XP, and academic rank calculation
  - Lab report generation conforming to Anna University Regulation 2023 format
  - SQLite WAL persistence for student milestones and deliverables
Hardware Safe: Zero background polling loops, passive CPU footprint (<8%), thread-safe.
========================================================================================
"""

import os
import json
import sqlite3
import datetime
from typing import Dict, Any, List, Optional, Tuple, Set

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")

# -----------------------------------------------------------------------------
# PROJECTS & PRACTICALS CATALOG SPECIFICATION
# -----------------------------------------------------------------------------

COURSE_PROJECTS_CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "EC23S01": [
        {
            "id": "EC23S01_PRJ1",
            "course_code": "EC23S01",
            "title": "Real-Time Acoustic Heart Sound (PCG) Noise Cancellation",
            "type": "mini",
            "estimated_hours": 25,
            "milestones": [
                {"id": "M1", "title": "Dataset Acquisition", "weightage_pct": 25},
                {"id": "M2", "title": "LMS Weight Convergence", "weightage_pct": 25},
                {"id": "M3", "title": "SNR Evaluation", "weightage_pct": 25},
                {"id": "M4", "title": "Technical Report", "weightage_pct": 25}
            ]
        },
        {
            "id": "EC23S01_PRJ2",
            "course_code": "EC23S01",
            "title": "Edge-AI Speech Keyword Spotting & Spectrogram Feature Extractor",
            "type": "major",
            "estimated_hours": 50,
            "milestones": [
                {"id": "M1", "title": "Audio Preprocessing & STFT", "weightage_pct": 20},
                {"id": "M2", "title": "TinyML Classifier Training", "weightage_pct": 30},
                {"id": "M3", "title": "Hardware Deployment", "weightage_pct": 25},
                {"id": "M4", "title": "Latency & Energy Profiling", "weightage_pct": 25}
            ]
        }
    ],
    "EC23C03": [
        {
            "id": "EC23C03_PRJ1",
            "course_code": "EC23C03",
            "title": "Temperature-Compensated CMOS Bandgap Voltage Reference (BGR)",
            "type": "mini",
            "estimated_hours": 25,
            "milestones": [
                {"id": "M1", "title": "Bipolar Core & VT Derivation", "weightage_pct": 25},
                {"id": "M2", "title": "Resistor Ratio Tuning", "weightage_pct": 25},
                {"id": "M3", "title": "Temp Sweep Simulation", "weightage_pct": 25},
                {"id": "M4", "title": "PSRR Analysis & Dossier", "weightage_pct": 25}
            ]
        },
        {
            "id": "EC23C03_PRJ2",
            "course_code": "EC23C03",
            "title": "Sub-Threshold Low-Power Biosensor Front-End with Integrated Photodiode",
            "type": "major",
            "estimated_hours": 50,
            "milestones": [
                {"id": "M1", "title": "Sub-Threshold Modeling", "weightage_pct": 20},
                {"id": "M2", "title": "TIA Circuit Synthesis", "weightage_pct": 30},
                {"id": "M3", "title": "Breadboard Prototype & PPG", "weightage_pct": 25},
                {"id": "M4", "title": "Noise Floor & Linearity", "weightage_pct": 25}
            ]
        }
    ],
    "EC23E04": [
        {
            "id": "EC23E04_PRJ1",
            "course_code": "EC23E04",
            "title": "Optical Fiber Fabry-Perot Interferometer for Micro-Strain & Thermal Sensing",
            "type": "mini",
            "estimated_hours": 25,
            "milestones": [
                {"id": "M1", "title": "Air Cavity Interference Theory", "weightage_pct": 25},
                {"id": "M2", "title": "Micro-Cavity Alignment", "weightage_pct": 25},
                {"id": "M3", "title": "Thermal Calibration", "weightage_pct": 25},
                {"id": "M4", "title": "Phase Unwrapping Algorithm", "weightage_pct": 25}
            ]
        },
        {
            "id": "EC23E04_PRJ2",
            "course_code": "EC23E04",
            "title": "Free-Space Optical (FSO) Laser Transceiver with Adaptive Beam Collimation",
            "type": "major",
            "estimated_hours": 50,
            "milestones": [
                {"id": "M1", "title": "Gaussian Beam Divergence", "weightage_pct": 20},
                {"id": "M2", "title": "Modulation & Driver Circuitry", "weightage_pct": 30},
                {"id": "M3", "title": "Free-Space Link Test", "weightage_pct": 25},
                {"id": "M4", "title": "Active Alignment & Dossier", "weightage_pct": 25}
            ]
        }
    ],
    "EC8702": [
        {
            "id": "EC8702_PRJ1",
            "course_code": "EC8702",
            "title": "Hard Real-Time Motor Position Controller with FreeRTOS & Quadrature Encoder",
            "type": "mini",
            "estimated_hours": 25,
            "milestones": [
                {"id": "M1", "title": "Timer Encoder Mode & DMA", "weightage_pct": 25},
                {"id": "M2", "title": "Preemptive Task Hierarchy", "weightage_pct": 25},
                {"id": "M3", "title": "CMSIS-DSP PID Tuning", "weightage_pct": 25},
                {"id": "M4", "title": "Interrupt Jitter & Deadline Audit", "weightage_pct": 25}
            ]
        },
        {
            "id": "EC8702_PRJ2",
            "course_code": "EC8702",
            "title": "Autonomous TinyML Drone Flight Controller with Fault-Tolerant RTOS",
            "type": "major",
            "estimated_hours": 50,
            "milestones": [
                {"id": "M1", "title": "Sensor Read & EKF Fusion", "weightage_pct": 20},
                {"id": "M2", "title": "Watchdog & Priority Ceiling", "weightage_pct": 30},
                {"id": "M3", "title": "TinyML Motor Vibration Anomaly", "weightage_pct": 25},
                {"id": "M4", "title": "HIL Flight Test & Final Dossier", "weightage_pct": 25}
            ]
        }
    ]
}

COURSE_PRACTICALS_CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "EC23S01": [
        {
            "id": "EC23S01_EXP1",
            "course_code": "EC23S01",
            "lab_number": 1,
            "title": "Discrete Linear & Circular Convolution via NumPy and SciPy",
            "aim": "To compute linear and circular convolution of two sequences x[n] and h[n].",
            "formula": "L = N1 + N2 - 1",
            "rubric_marks": {"preparation": 5, "execution": 10, "analysis": 10, "viva": 5}
        },
        {
            "id": "EC23S01_EXP2",
            "course_code": "EC23S01",
            "lab_number": 2,
            "title": "Design of Butterworth IIR Low-Pass Filter Using Bilinear Transformation",
            "aim": "To design a digital Butterworth low-pass filter using bilinear pre-warping.",
            "formula": "Omega = (2/T)*tan(omega/2)",
            "rubric_marks": {"preparation": 5, "execution": 10, "analysis": 10, "viva": 5}
        }
    ],
    "EC23C03": [
        {
            "id": "EC23C03_EXP1",
            "course_code": "EC23C03",
            "lab_number": 1,
            "title": "PN Junction Diode Forward and Reverse Characteristics",
            "aim": "To plot forward and reverse bias V-I characteristics of 1N4148.",
            "formula": "rd = eta*VT / ID",
            "rubric_marks": {"preparation": 5, "execution": 10, "analysis": 10, "viva": 5}
        },
        {
            "id": "EC23C03_EXP2",
            "course_code": "EC23C03",
            "lab_number": 2,
            "title": "Enhancement MOSFET Drain & Transfer Characteristics (2N7000)",
            "aim": "To determine threshold voltage Vth and transconductance gm.",
            "formula": "ID,sat = 0.5*kn*(VGS - Vth)^2",
            "rubric_marks": {"preparation": 5, "execution": 10, "analysis": 10, "viva": 5}
        }
    ],
    "EC23E04": [
        {
            "id": "EC23E04_EXP1",
            "course_code": "EC23E04",
            "lab_number": 1,
            "title": "Laser Resonator Stability Verification & Cavity g-Parameter Mapping",
            "aim": "To verify optical resonator stability for continuous-wave oscillation.",
            "formula": "0 <= g1*g2 <= 1",
            "rubric_marks": {"preparation": 5, "execution": 10, "analysis": 10, "viva": 5}
        }
    ],
    "EC8702": [
        {
            "id": "EC8702_EXP1",
            "course_code": "EC8702",
            "lab_number": 1,
            "title": "FreeRTOS Preemptive Priority Scheduling & Schedulability Verification",
            "aim": "To verify Rate Monotonic Scheduling (RMS) utilization bounds.",
            "formula": "U = sum(Ci/Ti) <= n*(2^(1/n) - 1)",
            "rubric_marks": {"preparation": 5, "execution": 10, "analysis": 10, "viva": 5}
        }
    ]
}


# -----------------------------------------------------------------------------
# BACKEND PROJECTS & PROGRESS ENGINE
# -----------------------------------------------------------------------------

class CourseProjectsEngine:
    """
    Evaluates student course projects, practical rubrics, and Continuous Internal Evaluation (CIE) progress.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self._ensure_database_schema()

    def _ensure_database_schema(self) -> None:
        """Create project milestone tracking table in SQLite WAL mode."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            try:
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS course_project_milestone_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        submission_id TEXT UNIQUE NOT NULL,
                        course_code TEXT NOT NULL,
                        project_id TEXT NOT NULL,
                        milestone_id TEXT NOT NULL,
                        student_id TEXT NOT NULL,
                        deliverable_url TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)
                conn.commit()
            finally:
                conn.close()
        except Exception:
            pass

    def validate_catalog(self) -> Dict[str, Any]:
        """
        Verify that all project milestones sum to 100% and practical rubrics sum to 30 marks.
        """
        errors = []
        total_projects = 0
        total_practicals = 0

        # 1. Project milestone verification
        for code, projs in COURSE_PROJECTS_CATALOG.items():
            for p in projs:
                total_projects += 1
                p_id = p["id"]
                milestones = p.get("milestones", [])
                if len(milestones) < 3:
                    errors.append(f"{p_id}: Project must have at least 3 milestones")
                total_weight = sum(m.get("weightage_pct", 0) for m in milestones)
                if total_weight != 100:
                    errors.append(f"{p_id}: Milestone weightages must sum to 100%, found {total_weight}%")

        # 2. Practical rubric verification
        for code, practicals in COURSE_PRACTICALS_CATALOG.items():
            for prac in practicals:
                total_practicals += 1
                prac_id = prac["id"]
                rubric = prac.get("rubric_marks", {})
                rubric_sum = sum(rubric.values())
                if rubric_sum != 30:
                    errors.append(f"{prac_id}: CIE practical rubric marks must sum to 30, found {rubric_sum}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "total_courses": len(COURSE_PROJECTS_CATALOG),
            "total_projects": total_projects,
            "total_practicals": total_practicals
        }

    def calculate_course_progress(
        self,
        course_code: str,
        completed_milestone_keys: List[str],
        verified_practical_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Calculates weighted course completion percentage, XP, and academic rank.
        """
        projs = COURSE_PROJECTS_CATALOG.get(course_code, [])
        practicals = COURSE_PRACTICALS_CATALOG.get(course_code, [])

        # Count total milestones
        total_milestones = sum(len(p.get("milestones", [])) for p in projs)
        finished_milestones = 0
        for p in projs:
            for m in p.get("milestones", []):
                key = f"{p['id']}_{m['id']}"
                if key in completed_milestone_keys:
                    finished_milestones += 1

        # Count practicals
        total_practicals = len(practicals)
        finished_practicals = sum(1 for prac in practicals if prac["id"] in verified_practical_ids)

        weight_milestones = (finished_milestones / total_milestones * 60.0) if total_milestones > 0 else 60.0
        weight_practicals = (finished_practicals / total_practicals * 40.0) if total_practicals > 0 else 40.0
        overall_percentage = round(weight_milestones + weight_practicals, 1)

        # XP calculation: 250 XP per milestone + 500 XP per practical
        earned_xp = (finished_milestones * 250) + (finished_practicals * 500)

        # Academic Rank Title
        if overall_percentage >= 90.0:
            academic_rank = "Apex Systems Architect"
        elif overall_percentage >= 65.0:
            academic_rank = "Hardware Adept"
        elif overall_percentage >= 35.0:
            academic_rank = "Laboratory Practitioner"
        elif overall_percentage > 0.0:
            academic_rank = "Junior Apprentice"
        else:
            academic_rank = "Novice Explorer"

        return {
            "course_code": course_code,
            "total_milestones": total_milestones,
            "finished_milestones": finished_milestones,
            "total_practicals": total_practicals,
            "finished_practicals": finished_practicals,
            "overall_percentage": overall_percentage,
            "earned_xp": earned_xp,
            "academic_rank": academic_rank
        }

    def generate_lab_report(
        self,
        course_code: str,
        practical_id: str,
        student_name: str = "ECE Undergraduate",
        roll_number: str = "2023MITEC042"
    ) -> Dict[str, Any]:
        """
        Synthesizes formatted laboratory record text adhering to Anna University Regulation 2023.
        """
        practicals = COURSE_PRACTICALS_CATALOG.get(course_code, [])
        prac = next((p for p in practicals if p["id"] == practical_id), None)
        if not prac:
            return {"error": f"Practical {practical_id} not found in course {course_code}"}

        report_md = f"""# LABORATORY RECORD OF EXPERIMENTS
**Madras Institute of Technology (MIT Campus), Anna University**  
**Department of Electronics Engineering — Regulation 2023**

---

### Course Information
- **Course Code:** {course_code}
- **Experiment No:** {prac.get('lab_number', 1)}
- **Title:** {prac.get('title')}
- **Student Name:** {student_name}
- **Roll Number:** {roll_number}
- **Date:** {datetime.date.today().isoformat()}

## 1. Aim
{prac.get('aim')}

## 2. Theoretical Principles & Governing Formulas
$${prac.get('formula')}$$

## 3. Continuous Internal Evaluation (CIE) Rubric (Max: 30 Marks)
| Evaluation Criteria | Maximum Marks |
| :--- | :--- |
| Pre-Lab Preparation & Circuit Schematic | 05 |
| Laboratory Execution & Circuit Assembly | 10 |
| Data Analysis & Waveform Synthesis | 10 |
| Technical Viva-Voce Examination | 05 |
| **Total Marks** | **30 Marks** |
"""
        return {
            "course_code": course_code,
            "practical_id": practical_id,
            "student_name": student_name,
            "roll_number": roll_number,
            "report_markdown": report_md
        }

    def log_milestone_submission(
        self,
        course_code: str,
        project_id: str,
        milestone_id: str,
        student_id: str,
        deliverable_url: str = "local://repository/artifacts"
    ) -> Dict[str, Any]:
        """Persists milestone deliverable record into SQLite WAL database."""
        sub_id = f"MS-{project_id}-{milestone_id}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}"
        now = datetime.datetime.now().isoformat()

        try:
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            try:
                conn.execute("""
                    INSERT INTO course_project_milestone_logs
                    (submission_id, course_code, project_id, milestone_id, student_id, deliverable_url, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sub_id,
                    course_code,
                    project_id,
                    milestone_id,
                    student_id,
                    deliverable_url,
                    now
                ))
                conn.commit()
            finally:
                conn.close()
            return {"status": "success", "submission_id": sub_id, "logged_at": now}
        except Exception as e:
            return {"status": "error", "error": str(e)}
