"""
========================================================================================
VoltCore Apex Academia - Master Enterprise Documentation Generator
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: scripts/generate_master_documentation.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
Target Environment: HP Victus 15-fa2xxx (LAPTOP-3NEGBVLE / Intel Core 5 210H / 24GB RAM)

Outputs Generated:
  1. docs/VoltCore_Apex_Academia_Master_Guide.docx (Microsoft Word Enterprise Document)
  2. docs/VoltCore_Apex_Academia_Master_Guide.pdf  (High-Resolution ReportLab PDF)
  3. docs/MASTER_PROJECT_GUIDE.md                 (GitHub-Flavored Markdown Technical Guide)
========================================================================================
"""

import os
import sys
import time
import tracemalloc
from datetime import datetime, timezone

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

# Output target file paths
DOCX_PATH = os.path.join(DOCS_DIR, "VoltCore_Apex_Academia_Master_Guide.docx")
PDF_PATH = os.path.join(DOCS_DIR, "VoltCore_Apex_Academia_Master_Guide.pdf")
MD_PATH = os.path.join(DOCS_DIR, "MASTER_PROJECT_GUIDE.md")

# ========================================================================================
# Phase 1 to Phase 30 Encyclopedia Data
# ========================================================================================

PHASES_DATA = [
    {
        "num": 1,
        "name": "Smart Attendance & Secure RBAC Portal",
        "route": "/attendance",
        "engine": "attendance_server.py / lms_database.py",
        "logic": "PBKDF2-HMAC-SHA256 (600,000 iterations), RFID UID validation (E2 80 6F 3B), session tokens",
        "specialty": "Contactless ESP32 RFID laboratory attendance with zero-latency SQLite WAL check-ins."
    },
    {
        "num": 2,
        "name": "Curriculum Management & NPTEL Video Sync",
        "route": "/nptel & /nptel-player",
        "engine": "courseware_engine.py",
        "logic": "17 MIT ECE Regulation 2023 modules, timestamped video chapter offsets, Markdown notes export",
        "specialty": "IIT Madras MOOC alignment with speed scaling (0.5x–2.0x) and offline syllabus cache."
    },
    {
        "num": 3,
        "name": "Enterprise Admin & NBA/NAAC Attainment",
        "route": "/enterprise-admin",
        "engine": "enterprise_admin_engine.py",
        "logic": "CO-PO direct/indirect weighted attainment matrices, SHA-256 tamper-evident audit ledger",
        "specialty": "Automated accreditation compliance reporting reducing NBA audit preparation from weeks to seconds."
    },
    {
        "num": 4,
        "name": "TinyML Edge Inference & Offline DSP",
        "route": "/simulation",
        "engine": "WebAssembly / Canvas Signal Visualizer",
        "logic": "WebAssembly INT8 quantized neural network inference, Radix-2 1024-point FFT spectrum analysis",
        "specialty": "Browser-native offline signal processing without remote server roundtrips or GPU dependencies."
    },
    {
        "num": 5,
        "name": "WebUSB/WebSerial Flasher & Dense Vector RAG",
        "route": "/flash-firmware",
        "engine": "rag_tutor_engine.py / WebSerial API",
        "logic": "DTR/RTS hardware bootloader pulse sequencing, 384-dimensional cosine similarity embeddings",
        "specialty": "Direct browser-to-silicon ESP32/STM32 firmware flashing paired with curriculum-aware AI tutor."
    },
    {
        "num": 6,
        "name": "Wokwi Simulation Controller & AutoGrader",
        "route": "/autograder",
        "engine": "autograder_engine.py",
        "logic": "Python AST static analysis, register bitmask audits, non-blocking timing loop evaluation",
        "specialty": "Instant automated code grading preventing infinite loops and validating hardware pin assignments."
    },
    {
        "num": 7,
        "name": "Production Hardening & Zero-Leak SOC Audits",
        "route": "/settings",
        "engine": "deploy/production_readiness_audit.py",
        "logic": "Token-bucket rate limiting (60 req/min), recursive regex client-bundle privacy scanner",
        "specialty": "Zero client-side credential exposure guaranteeing strict confidentiality of MIT administrator keys."
    },
    {
        "num": 8,
        "name": "Concurrency, Offline Spool & Fleet Management",
        "route": "/fleet",
        "engine": "fleet_manager_engine.py",
        "logic": "LittleFS binary synchronization, offline FIFO transaction spooling, optimistic lock recovery",
        "specialty": "Multi-bench fleet firmware distribution resilient against intermittent campus network drops."
    },
    {
        "num": 9,
        "name": "Examination Center & GATE Simulator",
        "route": "/exam-center",
        "engine": "exam_simulator_engine.py",
        "logic": "Adaptive multi-section timing, GATE 1/3 negative marking penalties, CO1–CO5 topic mastery score",
        "specialty": "Full-screen distraction-free examination environment mirroring National Testing Agency (NTA) UI."
    },
    {
        "num": 10,
        "name": "IoT Smart Laboratory 304 Baseline Testbed",
        "route": "/smart-lab",
        "engine": "smart_lab_engine.py",
        "logic": "Keysight DSOX1204G & Rigol DP832 bench state tracking, instrument calibration maintenance schedules",
        "specialty": "Real-time workbench status hub with preventative maintenance alert escalation."
    },
    {
        "num": 11,
        "name": "Collaboration Workspace & Gamified Hub",
        "route": "/collaboration",
        "engine": "collaboration_engine.py",
        "logic": "XP multiplier scaling (1.0x–2.5x), peer code review threads, Silicon Grandmaster leaderboard",
        "specialty": "Gamified engineering study pods boosting student peer engagement and collaborative debugging."
    },
    {
        "num": 12,
        "name": "Research Discovery & IEEE Knowledge Hub",
        "route": "/research",
        "engine": "research_discovery_engine.py",
        "logic": "IEEE Xplore metadata parsing, automated BibTeX citation synthesis, hypothesis evaluation matrix",
        "specialty": "Undergraduate research accelerator mapping student projects to IEEE Transactions literature."
    },
    {
        "num": 13,
        "name": "Enterprise Faculty Workload Analytics",
        "route": "/teacher",
        "engine": "teacher_analytics_engine.py",
        "logic": "Faculty credit-hour distribution models, student attendance risk heatmaps, NBA SAR Criterion 5",
        "specialty": "Institutional administrative decision matrix balancing faculty teaching and research duties."
    },
    {
        "num": 14,
        "name": "Security Operations Center (SOC) & TOTP MFA",
        "route": "/security-hub",
        "engine": "security_hardening_engine.py",
        "logic": "RFC 6238 TOTP HMAC-SHA1/SHA256, chained SHA-256 tamper-evident security audit logs",
        "specialty": "Departmental security dashboard defending against brute-force and session tampering vectors."
    },
    {
        "num": 15,
        "name": "Next-Gen AI Innovations & Autonomous Agent Twin",
        "route": "/next-gen",
        "engine": "next_gen_agent_engine.py",
        "logic": "Multi-variable academic distress regression, heuristic study schedule optimizer, proactive intervention",
        "specialty": "Personalized digital academic twin advising students on prerequisite mastery and revision cycles."
    },
    {
        "num": 16,
        "name": "Cloud Deployment & Multi-Stage Container Staging",
        "route": "/cloud-deploy",
        "engine": "deploy/Dockerfile / docker-compose.yml",
        "logic": "Alpine multi-stage Docker builds, non-root user execution (`voltcore:1001`), resource caps",
        "specialty": "Lightweight container image (<150MB) deploying anywhere from local lab rigs to AWS/DigitalOcean."
    },
    {
        "num": 17,
        "name": "Physical Hardware-in-the-Loop (HIL) Lab Automation",
        "route": "/physical-lab",
        "engine": "physical_lab_engine.py",
        "logic": "WebSerial loopback latency test, ADC 12-bit linearity calibration, I2C bus clock-stretch timeout audit",
        "specialty": "Live hardware pin validation testing real physical boards before student project viva submission."
    },
    {
        "num": 18,
        "name": "Voice-Enabled Hands-Free Lab Assistant",
        "route": "/voice-lab",
        "engine": "Web Speech API / SpeechSynthesis",
        "logic": "Deterministic acoustic intent parsing, local browser TTS synthesizer, hands-free formula lookup",
        "specialty": "Zero-touch lab operation allowing students to query formulas while hands hold soldering irons/probes."
    },
    {
        "num": 19,
        "name": "Intelligent Academic Management Hub",
        "route": "/academic-hub",
        "engine": "academic_management_engine.py",
        "logic": "Directed Acyclic Graph (DAG) course prerequisite validator, IA-1/IA-2 syllabus milestone completion",
        "specialty": "Dynamic prerequisite tree traversal alerting students before enrolling in advanced electives."
    },
    {
        "num": 20,
        "name": "Advanced ECE Knowledge & Formula Encyclopedia",
        "route": "/ece-knowledge",
        "engine": "ece_knowledge_engine.py",
        "logic": "Curated LaTeX equations across 6 core ECE domains, Lab 304 component datasheets, acronym glossary",
        "specialty": "Instant 1-click LaTeX math clipboard copying with interactive component pinouts (ESP32-S3, LM741)."
    },
    {
        "num": 21,
        "name": "Smart Learning Productivity & Study Management",
        "route": "/learning-productivity",
        "engine": "learning_productivity_engine.py",
        "logic": "Web Audio API custom frequency synthesizer, Ebbinghaus forgetting curve intervals (1, 3, 7, 14, 30 days)",
        "specialty": "Deterministic Pomodoro timer with distraction-free HUD and offline spaced repetition queue."
    },
    {
        "num": 22,
        "name": "Advanced Digital Electronics Learning Center",
        "route": "/digital-electronics",
        "engine": "digital_electronics_engine.py",
        "logic": "7-format base converter, Quine-McCluskey 2–4 variable K-Map prime implicant table, SOP/POS generator",
        "specialty": "Algorithmic Boolean simplification solving manual circuit minimization assignments in real time."
    },
    {
        "num": 23,
        "name": "Analog & Communication Engineering Center",
        "route": "/analog-communication",
        "engine": "analog_comm_engine.py",
        "logic": "Sallen-Key Butterworth 20-point Bode plots, BJT Thevenin Q-point, Shannon-Hartley channel capacity",
        "specialty": "End-to-end analog circuit design matching EC3451 & EC3491 laboratory curricula."
    },
    {
        "num": 24,
        "name": "Engineering Project & Innovation Center",
        "route": "/project-innovation",
        "engine": "project_innovation_engine.py",
        "logic": "EC3711 proposal builder, BOM costing with 18% GST + 10% contingency, automated GPIO/LDO voltage auditor",
        "specialty": "Automated hardware compatibility checker catching 5V-to-3.3V logic level mismatches before burning chips."
    },
    {
        "num": 25,
        "name": "Faculty & Department Productivity Workspace",
        "route": "/faculty-workspace",
        "engine": "faculty_productivity_engine.py",
        "logic": "Unit I–V lecture planner mapped to Bloom's Taxonomy (K1–K5), weighted rubrics, Department MoM ledger",
        "specialty": "Comprehensive teaching administrative workspace standardizing lesson delivery across all ECE sections."
    },
    {
        "num": 26,
        "name": "Accessibility & Inclusive Learning Center",
        "route": "/accessibility",
        "engine": "accessibility_engine.py",
        "logic": "Bilingual English/Tamil ECE lexicon with phonetic transliteration, physical analogies, WCAG 2.1 AAA HUD",
        "specialty": "High-contrast, dyslexia-friendly, font-scalable interface with native Tamil voice explanations."
    },
    {
        "num": 27,
        "name": "Data Intelligence & Academic Quality Center",
        "route": "/data-intelligence",
        "engine": "data_intelligence_engine.py",
        "logic": "AU R2023 Clause 7.2 attendance compliance (>=75%, 65-75% condonation), Jaccard similarity duplicate check",
        "specialty": "Academic quality auditor identifying Bloom's cognitive gaps (<40% higher order) and syllabus deficits."
    },
    {
        "num": 28,
        "name": "Platform Intelligence & Reliability Center (SRE)",
        "route": "/system-health",
        "engine": "platform_reliability_engine.py",
        "logic": "APM p50/p95 latency metrics, SQLite WAL PRAGMA quick_check integrity scanner, 39-route reachability test",
        "specialty": "Live SRE health hub with 1-click WAL checkpointing maintaining sub-3ms system latency."
    },
    {
        "num": 29,
        "name": "IoT Smart Laboratory & Equipment Telemetry Hub",
        "route": "/iot-lab",
        "engine": "iot_telemetry_engine.py",
        "logic": "Lab 304 8 smart bench nodes, P = V * I calculation, automated trip relays (>25V, >3.0A, >65°C)",
        "specialty": "Automated safety trip interlock isolating dangerous high-voltage AC/DC workbench overloads in <5ms."
    },
    {
        "num": 30,
        "name": "Smart PCB, SMD & Component Inspector Lab",
        "route": "/component-inspector",
        "engine": "component_inspector_engine.py",
        "logic": "IEC 60062 4/5/6-band resistor color decoding, EIA-96 SMD lookups, IPC-2221 trace width, IC Theta-JA heat",
        "specialty": "Visual graphical resistor canvas, SMD keypad decoder, and silicon junction safety heat checker."
    }
]

# ========================================================================================
# Markdown Generator
# ========================================================================================

def generate_markdown_guide():
    """Generates docs/MASTER_PROJECT_GUIDE.md with complete architectural coverage."""
    lines = []
    lines.append("# VoltCore Apex Academia — Master Enterprise Technical & Architectural Guide")
    lines.append("")
    lines.append("**Institution:** Madras Institute of Technology (MIT) Campus, Anna University, Chromepet  ")
    lines.append("**Department:** Department of Electronics Engineering (Regulation 2023)  ")
    lines.append("**Platform Lead / Principal Systems Architect:** Ashok Kumar A (`2023MITEC042`)  ")
    lines.append("**Public Contact:** `ashokkumar3132008@gmail.com` | [GitHub Repository](https://github.com/AshokKumar313)  ")
    lines.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  ")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 1
    lines.append("## 1. Executive Summary & Project Vision")
    lines.append("")
    lines.append("VoltCore Apex Academia is an enterprise-grade academic learning management, physical laboratory automation, and hardware verification platform specifically engineered for the Department of Electronics Engineering at Madras Institute of Technology (MIT) Campus, Anna University, under ECE Regulation 2023.")
    lines.append("")
    lines.append("### Core Engineering Philosophy:")
    lines.append("1. **Zero-Bloat Execution:** The entire ecosystem operates without heavy background database daemons, cloud dependencies, or unconstrained machine learning containers. All mathematical solvers, circuit calculators, and search routines run deterministically in native Python and optimized client-side WebAssembly.")
    lines.append("2. **Sub-3ms Local Persistence:** Powered by SQLite in Write-Ahead Logging (`WAL`) mode, delivering concurrent non-blocking reads and high-throughput writes while maintaining an on-disk footprint under 50MB.")
    lines.append("3. **Offline-First PWA Resilience:** Featuring dual Service Workers (`public/service-worker.js` and `src/service-worker.js`), the platform pre-caches all 39 static routes, ensuring that student laboratory experiments, formula encyclopedia searches, and calculator solvers remain 100% operational during campus Wi-Fi outages.")
    lines.append("4. **Passive Thermal Profile & Hardware Safety:** Architected strictly for student and laboratory workstations (specifically tested and validated on HP Victus 15-fa2xxx with Intel Core 5 210H, 24GB DDR5, and RTX 4050). The platform maintains quiet fan profiles, sub-300MB process memory footprints, and sub-8s full test suite execution without thermal stress.")
    lines.append("5. **Rigorous Quality & Security Invariants:** Backed by 325 automated pytest unit tests across 32 suites, automated production readiness audits with zero credential leakage, and 100% verified static routes.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 2
    lines.append("## 2. System Architecture: From Scratch to Advanced Enterprise")
    lines.append("")
    lines.append("```")
    lines.append("┌────────────────────────────────────────────────────────────────────────┐")
    lines.append("│              VOLTCORE APEX ACADEMIA - FULL STACK TOPOLOGY              │")
    lines.append("├────────────────────────────────────────────────────────────────────────┤")
    lines.append("│  CLIENT LAYER: Astro 5 SSG + React 19 Interactive Islands + Tailwind   │")
    lines.append("│  • 39 Verified Static HTML Routes (dist/*.html)                        │")
    lines.append("│  • Dual PWA Service Workers (NetworkFirst / CacheFirst Pre-Caching)    │")
    lines.append("├────────────────────────────────────────────────────────────────────────┤")
    lines.append("│  GATEWAY LAYER: Dual-Mode Backend Gateway (attendance_server.py:5000)  │")
    lines.append("│  • Flask REST API with CORS headers                                    │")
    lines.append("│  • Zero-Dependency Fallback: Python stdlib http.server Handler         │")
    lines.append("├────────────────────────────────────────────────────────────────────────┤")
    lines.append("│  ENGINE LAYER: 20+ Specialized Python Modules (backend/*_engine.py)    │")
    lines.append("│  • Thread-Safe RLock Synchronization                                   │")
    lines.append("│  • Mathematical & Deterministic Algorithmic Solvers                    │")
    lines.append("├────────────────────────────────────────────────────────────────────────┤")
    lines.append("│  PERSISTENCE LAYER: SQLite 3 with Write-Ahead Logging (WAL Mode)       │")
    lines.append("│  • PRAGMA journal_mode = WAL; PRAGMA synchronous = NORMAL;             │")
    lines.append("│  • Over 30 Specialized Tables (voltcore_lms.db)                        │")
    lines.append("└────────────────────────────────────────────────────────────────────────┘")
    lines.append("```")
    lines.append("")
    lines.append("### Architectural Deep Dive:")
    lines.append("- **Frontend Architecture:** Built on Astro 5 Static Site Generation. Pages are statically compiled into blazing-fast HTML, injecting React 19 client components only where dynamic DOM state is strictly required (`client:load`). This hybrid architecture eliminates client-side hydration lag and guarantees sub-second first contentful paint.")
    lines.append("- **Dual-Mode Backend Resilience:** `attendance_server.py` implements intelligent environment probing. When Flask and Flask-CORS are present, it spins up a robust WSGI HTTP server. If run in stripped-down student or embedded environments where pip packages are prohibited, it smoothly falls back to an internal standard-library `http.server.BaseHTTPRequestHandler` supporting all REST API routes seamlessly.")
    lines.append("- **Database & Storage Architecture:** `voltcore_lms.db` enforces SQLite WAL mode. WAL separates reader threads from writer threads, preventing lock contention during simultaneous RFID attendance scans, IoT telemetry ingestion, and examination submissions.")
    lines.append("- **Security & Access Control (RBAC):** Passwords are encrypted using 600,000 iterations of PBKDF2-HMAC-SHA256 with cryptographically random 16-byte salts. Roles (`Student`, `Faculty`, `LabTechnician`, `Admin`, `HOD_ECE`) are verified at engine level. All private administrative keys are stored behind environment variables and verified by automated audit scripts.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 3
    lines.append("## 3. What Is Inside & Specialty of Each Module (Phase 1 to 30 Encyclopedia)")
    lines.append("")
    lines.append("| Phase | Module Name | Route URL | Primary Engine | Core Mathematical / Technical Logic | Unique Laboratory Specialty |")
    lines.append("|:---|:---|:---|:---|:---|:---|")
    for p in PHASES_DATA:
        lines.append(f"| **Phase {p['num']}** | {p['name']} | `{p['route']}` | `{p['engine']}` | {p['logic']} | {p['specialty']} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 4
    lines.append("## 4. How to Use the Platform (User, Faculty & Technician Manual)")
    lines.append("")
    lines.append("### 4.1 Student Guide:")
    lines.append("1. **Global Navigation:** Use the topbar or press `Ctrl+K` (or `⌘K` on macOS) to invoke the Instant Command Palette. Type any course code (`EC3352`, `EC3451`), instrument, or module name to jump directly.")
    lines.append("2. **Component & PCB Inspection:** Navigate to `/component-inspector` to decode 4/5/6-band axial resistors with live color-band graphics, look up SMD chip markings, size PCB trace widths using IPC-2221 formulas, and verify IC heatsink requirements.")
    lines.append("3. **Formula & Knowledge Lookup:** Visit `/ece-knowledge` to access curated LaTeX formulas, datasheets for lab ICs (ESP32-S3, LM741, STM32F4), and copy LaTeX code with a single click.")
    lines.append("4. **Digital & Analog Circuit Solvers:** Use `/digital-electronics` for multi-base conversions and K-Map simplifications, and `/analog-communication` for Sallen-Key active filter Bode plots and BJT/MOSFET bias calculations.")
    lines.append("5. **Focus & Productivity:** Launch `/learning-productivity` for distraction-free Pomodoro study intervals with synthesized audio chimes and Ebbinghaus spaced repetition flashcards.")
    lines.append("6. **Inclusive & Bilingual Learning:** Toggle Tamil/English terminology and intuitive physical analogies on `/accessibility` with text-to-speech audio guidance.")
    lines.append("")
    lines.append("### 4.2 Faculty Guide:")
    lines.append("1. **Curriculum & Lecture Planning:** Access `/faculty-workspace` to map syllabus units across Bloom's Taxonomy cognitive levels (K1 to K5), evaluate student submissions using weighted rubrics, and maintain Minutes of Meetings (MoM).")
    lines.append("2. **Academic Compliance & Attainment:** Review `/data-intelligence` to verify Anna University Clause 7.2 student attendance requirements (>=75%), audit syllabus coverage heatmaps, and generate CO-PO attainment matrices on `/enterprise-admin`.")
    lines.append("3. **Project & Innovation Mentorship:** Use `/project-innovation` to review EC3711 Mini-Project proposals, audit student BOM budgets, and run automated logic-level compatibility audits.")
    lines.append("")
    lines.append("### 4.3 Lab Technician & SRE Guide:")
    lines.append("1. **Lab 304 Telemetry Monitoring:** Open `/iot-lab` to observe real-time voltage, current, power ($P = V \times I$), and temperature across 8 dedicated workbench nodes.")
    lines.append("2. **Emergency Bench Relay Isolation:** Remotely toggle AC/DC power relays (`CLOSED` vs `OPEN`) or acknowledge automated safety trips (>25V, >3.0A, >65°C).")
    lines.append("3. **Platform Reliability & Database Checkpointing:** Visit `/system-health` to run APM latency tests, verify 39-route reachability, and execute 1-click SQLite WAL checkpoints (`PRAGMA wal_checkpoint(TRUNCATE);`).")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 5
    lines.append("## 5. Developer Setup, Build & Verification Guide")
    lines.append("")
    lines.append("### Prerequisites:")
    lines.append("- Node.js v20.x or higher with npm")
    lines.append("- Python 3.10 to 3.14 with standard libraries")
    lines.append("")
    lines.append("### Step-by-Step Commands:")
    lines.append("```powershell")
    lines.append("# 1. Clone & Enter Project Repository")
    lines.append("cd 'C:\\Users\\Ashok kumar A\\OneDrive\\Documents\\VoltCore-LMS-Portal'")
    lines.append("")
    lines.append("# 2. Install Node Dependencies")
    lines.append("npm install")
    lines.append("")
    lines.append("# 3. Launch Backend Attendance & Telemetry Gateway")
    lines.append("python attendance_server.py")
    lines.append("")
    lines.append("# 4. Execute Full Static Production Build (Builds all 39 static routes)")
    lines.append("npm.cmd run build")
    lines.append("")
    lines.append("# 5. Execute Complete Test Suite (325 tests in ~7 seconds)")
    lines.append("python -m pytest tests/")
    lines.append("")
    lines.append("# 6. Execute Production Readiness & Privacy Audit")
    lines.append("python deploy/production_readiness_audit.py")
    lines.append("")
    lines.append("# 7. Execute Courseware Content QA Validator")
    lines.append("python scripts/content_qa_validator.py")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 6
    lines.append("## 6. Master API & SQLite WAL Database Schema Reference")
    lines.append("")
    lines.append("### 6.1 Complete REST API Endpoints:")
    lines.append("| HTTP Method | Endpoint Path | Primary Engine | Description |")
    lines.append("|:---|:---|:---|:---|")
    lines.append("| `POST` | `/api/attendance` | `attendance_server.py` | Logs RFID student scan and returns profile |")
    lines.append("| `GET` | `/api/academic/overview` | `academic_management_engine.py` | Retrieves calendar events, tests, and syllabus |")
    lines.append("| `POST` | `/api/academic/check-prerequisite` | `academic_management_engine.py` | Evaluates DAG course prerequisite eligibility |")
    lines.append("| `GET` | `/api/knowledge/categories` | `ece_knowledge_engine.py` | Returns ECE formula topics and datasheets |")
    lines.append("| `GET` | `/api/productivity/streak` | `learning_productivity_engine.py` | Retrieves daily Pomodoro streak and retention |")
    lines.append("| `POST` | `/api/productivity/pomodoro/log` | `learning_productivity_engine.py` | Records completed deep work focus session |")
    lines.append("| `POST` | `/api/digital/convert-base` | `digital_electronics_engine.py` | Converts number across 7 digital formats |")
    lines.append("| `POST` | `/api/digital/solve-kmap` | `digital_electronics_engine.py` | Quine-McCluskey 2–4 variable SOP/POS solver |")
    lines.append("| `POST` | `/api/analog/sallen-key` | `analog_comm_engine.py` | Sallen-Key active filter cutoff and Bode data |")
    lines.append("| `POST` | `/api/analog/bjt-bias` | `analog_comm_engine.py` | Solves BJT voltage divider Q-point stability |")
    lines.append("| `POST` | `/api/project/verify-compatibility`| `project_innovation_engine.py` | Audits pin voltage, LDO power, and I2C buses |")
    lines.append("| `GET` | `/api/faculty/dashboard` | `faculty_productivity_engine.py` | Returns syllabus planner, rubrics, and MoM |")
    lines.append("| `GET` | `/api/accessibility/glossary` | `accessibility_engine.py` | Returns English/Tamil ECE lexicon |")
    lines.append("| `GET` | `/api/data-intelligence/audit` | `data_intelligence_engine.py` | Audits Clause 7.2 attendance and Bloom gaps |")
    lines.append("| `GET` | `/api/reliability/overview` | `platform_reliability_engine.py` | Live APM p50/p95 latency and SQLite WAL status |")
    lines.append("| `GET` | `/api/iot/overview` | `iot_telemetry_engine.py` | Lab 304 8-bench aggregate power and health |")
    lines.append("| `POST` | `/api/iot/bench/relay` | `iot_telemetry_engine.py` | Toggles AC/DC bench relay isolation state |")
    lines.append("| `POST` | `/api/inspector/axial-decode` | `component_inspector_engine.py` | Decodes 4/5/6-band axial resistor colors |")
    lines.append("| `POST` | `/api/inspector/smd-decode` | `component_inspector_engine.py` | Decodes 3/4-digit and EIA-96 SMD chips |")
    lines.append("| `POST` | `/api/inspector/pcb-trace` | `component_inspector_engine.py` | IPC-2221 PCB trace width and Joule loss |")
    lines.append("| `POST` | `/api/inspector/ic-thermal` | `component_inspector_engine.py` | IC package silicon junction temperature check |")
    lines.append("")
    lines.append("### 6.2 Master SQLite WAL Database Tables:")
    lines.append("| Table Name | Engine Owner | Primary Key | Key Storage Fields |")
    lines.append("|:---|:---|:---|:---|")
    lines.append("| `users` | `lms_database.py` | `id` | username, role, password_hash, rfid_uid, department |")
    lines.append("| `attendance_records` | `lms_database.py` | `id` | student_id, timestamp, node_id, status |")
    lines.append("| `academic_calendar_events` | `academic_management_engine.py` | `event_id` | event_title, event_type, start_date, co_mapped |")
    lines.append("| `ece_formula_catalog` | `ece_knowledge_engine.py` | `formula_id` | category, title, latex_code, explanation |")
    lines.append("| `pomodoro_sessions` | `learning_productivity_engine.py` | `session_id` | student_id, duration_minutes, completed_at |")
    lines.append("| `saved_kmap_solutions` | `digital_electronics_engine.py` | `calc_id` | variables_json, minterms_json, sop_expression |")
    lines.append("| `analog_circuit_calculations` | `analog_comm_engine.py` | `calc_id` | circuit_type, input_params_json, results_json |")
    lines.append("| `project_proposals` | `project_innovation_engine.py` | `proposal_id` | title, student_team_json, bom_cost, status |")
    lines.append("| `faculty_lecture_plans` | `faculty_productivity_engine.py` | `plan_id` | course_code, unit_number, blooms_level, notes |")
    lines.append("| `accessibility_lexicon` | `accessibility_engine.py` | `term_id` | term_en, term_ta, transliteration, analogy |")
    lines.append("| `data_quality_audit_logs` | `data_intelligence_engine.py` | `audit_id` | category, findings_json, severity, audited_at |")
    lines.append("| `reliability_apm_metrics` | `platform_reliability_engine.py` | `metric_id` | route, p50_ms, p95_ms, wal_bytes, recorded_at |")
    lines.append("| `iot_bench_nodes` | `iot_telemetry_engine.py` | `node_id` | bench_id, voltage_v, current_a, power_w, relay_state |")
    lines.append("| `component_inspection_history` | `component_inspector_engine.py` | `id` | inspection_type, component_class, results_json |")
    lines.append("| `saved_pcb_trace_calculations` | `component_inspector_engine.py` | `calc_id` | current_a, width_mils, width_mm, resistance_ohms |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("**VoltCore Apex Academia © 2026** • Madras Institute of Technology Campus, Anna University • All Systems Operational.")

    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[OK] Generated Markdown guide: {MD_PATH} ({len(lines)} lines)")


# ========================================================================================
# DOCX Generator
# ========================================================================================

def generate_docx_guide():
    """Generates docs/VoltCore_Apex_Academia_Master_Guide.docx using python-docx."""
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    doc = Document()

    # Configure Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Document Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("VOLTCORE APEX ACADEMIA\n")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0, 105, 62)  # Anna University Green

    r_sub = p_title.add_run("Master Enterprise Technical Architecture & Operations Guide\n")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(0, 160, 120)

    r_meta = p_title.add_run("Department of Electronics Engineering • Anna University / MIT Campus (Regulation 2023)\nPlatform Lead: Ashok Kumar A (2023MITEC042)")
    r_meta.font.name = "Arial"
    r_meta.font.size = Pt(10)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Section 1: Executive Summary
    h1 = doc.add_heading("1. Executive Summary & Project Vision", level=1)
    h1.paragraph_format.space_before = Pt(12)
    p = doc.add_paragraph(
        "VoltCore Apex Academia is an enterprise academic learning management, physical laboratory automation, and hardware verification suite designed specifically for the Madras Institute of Technology (MIT) Campus, Anna University, under ECE Regulation 2023. Built with an uncompromising zero-bloat philosophy, the platform guarantees sub-3ms SQLite Write-Ahead Logging (WAL) persistence, offline Progressive Web App (PWA) resilience across 39 verified static routes, and strict thermal compliance designed for student laptops and laboratory benches."
    )
    p.paragraph_format.line_spacing = 1.15

    # Core Principles Bullet Points
    doc.add_paragraph("• Zero-Bloat Execution: Pure native Python and deterministic WebAssembly solvers with zero background container overhead.", style='List Bullet')
    doc.add_paragraph("• Sub-3ms SQLite WAL Persistence: Concurrent, non-blocking read/write transactions backed by voltcore_lms.db in WAL mode.", style='List Bullet')
    doc.add_paragraph("• 39-Route Offline PWA Resilience: Dual service workers pre-cache static routes for zero downtime during campus network drops.", style='List Bullet')
    doc.add_paragraph("• HP Victus Passive Cooling Safety: Designed for passive thermal stability (<300MB memory, zero webcam loops, sub-8s test suite).", style='List Bullet')
    doc.add_paragraph("• Comprehensive Test Coverage: 325 passing automated unit tests across 32 pytest suites with 100% zero credential leakage.", style='List Bullet')

    # Section 2: System Architecture
    h2 = doc.add_heading("2. How It Is Made: System Architecture & Technologies", level=1)
    h2.paragraph_format.space_before = Pt(14)
    p2 = doc.add_paragraph(
        "The VoltCore Apex architecture is structured into four cohesive layers engineered for maximum performance, offline reliability, and absolute hardware safety:"
    )
    p2.paragraph_format.line_spacing = 1.15

    doc.add_paragraph("1. Frontend Layer: Astro 5 Static Site Generation (SSG) compiles all 39 enterprise routes to lightweight static HTML and CSS. Dynamic controls leverage React 19 interactive islands (client:load) and Tailwind CSS glassmorphism, achieving sub-second initial paint times.")
    doc.add_paragraph("2. Dual-Mode Backend Gateway (attendance_server.py): Features a primary Flask REST API with CORS headers. If deployed in minimal environments where external libraries are unavailable, it automatically transitions to Python's standard-library http.server with zero loss in endpoint availability.")
    doc.add_paragraph("3. Database Persistence Layer: Utilizes SQLite 3 configured with Write-Ahead Logging (PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;). This permits concurrent reads while writes commit instantly to WAL files without lock contention.")
    doc.add_paragraph("4. Security & QA Gates: Cryptographic security relies on PBKDF2-HMAC-SHA256 (600,000 iterations). Strict RBAC barriers protect administrative functions, while automated deployment audits verify that zero private credentials exist in client bundles.")

    # Section 3: Phase 1 to 30 Encyclopedia Table
    h3 = doc.add_heading("3. Module Encyclopedia: Complete Phases 1 through 30", level=1)
    h3.paragraph_format.space_before = Pt(14)
    doc.add_paragraph("Complete reference of all 30 engineered phases powering VoltCore Apex Academia:")

    table = doc.add_table(rows=1, cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    hdr_cells = table.rows[0].cells
    hdr_titles = ["Phase", "Module Name", "Route URL", "Primary Logic", "Unique Laboratory Specialty"]
    col_widths = [Inches(0.7), Inches(1.5), Inches(1.3), Inches(1.8), Inches(1.7)]

    for idx, title in enumerate(hdr_titles):
        hdr_cells[idx].text = title
        hdr_cells[idx].width = col_widths[idx]
        run = hdr_cells[idx].paragraphs[0].runs[0]
        run.font.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(255, 255, 255)
        # Background color
        shading = OxmlElement('w:shd')
        shading.set(qn('w:val'), 'clear')
        shading.set(qn('w:color'), 'auto')
        shading.set(qn('w:fill'), '00693E')
        hdr_cells[idx]._tc.get_or_add_tcPr().append(shading)

    for p in PHASES_DATA:
        row_cells = table.add_row().cells
        row_cells[0].text = f"P{p['num']}"
        row_cells[1].text = p['name']
        row_cells[2].text = p['route']
        row_cells[3].text = p['logic']
        row_cells[4].text = p['specialty']
        for i in range(5):
            row_cells[i].width = col_widths[i]
            for r in row_cells[i].paragraphs[0].runs:
                r.font.size = Pt(8)

    # Section 4: User Manual
    h4 = doc.add_heading("4. How to Use the Platform: User, Faculty & Technician Manual", level=1)
    h4.paragraph_format.space_before = Pt(14)
    doc.add_paragraph("• Students: Navigate using the global topbar or Ctrl+K / ⌘K command search palette. Access /component-inspector for live axial resistor color decoding, SMD EIA-96 chip marking lookups, and IPC-2221 PCB trace width calculations. Practice GATE exams on /exam-center and study with offline spaced repetition on /learning-productivity.")
    doc.add_paragraph("• Faculty: Design unit lesson plans mapped to Bloom's Taxonomy (K1–K5) on /faculty-workspace, review EC3711 student mini-project proposals on /project-innovation, and track Anna University Clause 7.2 student attendance compliance (>=75%) on /data-intelligence.")
    doc.add_paragraph("• Lab Technicians: Monitor Lab 304 8-bench real-time telemetry on /iot-lab, inspect automated overload safety trips (>25V, >3A, >65°C), remotely isolate bench power relays, and run APM latency checks on /system-health.")

    # Section 5: Developer Guide
    h5 = doc.add_heading("5. Developer Setup, Build & Verification Guide", level=1)
    h5.paragraph_format.space_before = Pt(14)
    doc.add_paragraph("Standard terminal workflow to build, run, and test VoltCore Apex Academia:")
    doc.add_paragraph("1. npm install                -> Install frontend dependencies\n2. python attendance_server.py -> Launch backend REST gateway on port 5000\n3. npm.cmd run build          -> Build static production bundle (39 static routes)\n4. python -m pytest tests/     -> Execute all 325 automated tests across 32 suites (~7s)\n5. python deploy/production_readiness_audit.py -> Verify routes & 0 credential leaks\n6. python scripts/content_qa_validator.py      -> Verify 17/17 courseware modules")

    # Section 6: API and Database Reference
    h6 = doc.add_heading("6. Master API & SQLite WAL Database Reference", level=1)
    h6.paragraph_format.space_before = Pt(14)
    doc.add_paragraph("• Key REST APIs: /api/attendance (RFID scans), /api/academic/overview (Calendar & DAG), /api/productivity/streak (Pomodoro), /api/digital/solve-kmap (Quine-McCluskey), /api/analog/sallen-key (Bode plots), /api/project/verify-compatibility (BOM & logic audit), /api/data-intelligence/audit (Compliance), /api/iot/bench/relay (Safety interlock), /api/inspector/axial-decode (Resistor decoding), /api/inspector/pcb-trace (IPC-2221 trace sizing).")
    doc.add_paragraph("• Core SQLite WAL Tables: users, attendance_records, academic_calendar_events, ece_formula_catalog, pomodoro_sessions, saved_kmap_solutions, analog_circuit_calculations, project_proposals, faculty_lecture_plans, accessibility_lexicon, data_quality_audit_logs, reliability_apm_metrics, iot_bench_nodes, component_inspection_history, saved_pcb_trace_calculations.")

    doc.save(DOCX_PATH)
    print(f"[OK] Generated DOCX guide: {DOCX_PATH}")


# ========================================================================================
# PDF Generator
# ========================================================================================

def generate_pdf_guide():
    """Generates docs/VoltCore_Apex_Academia_Master_Guide.pdf using ReportLab."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfgen import canvas

    class NumberedCanvas(canvas.Canvas):
        """Two-pass canvas to dynamically compute and print total page numbers."""
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_page_decorations(num_pages)
                super().showPage()
            super().save()

        def draw_page_decorations(self, total_pages):
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            
            # Header (pages > 1)
            if self._pageNumber > 1:
                self.drawString(54, 755, "VoltCore Apex Academia — Master Enterprise Technical Architecture Guide")
                self.drawRightString(558, 755, "Anna University / MIT Campus (ECE R2023)")
                self.setStrokeColor(colors.HexColor("#CBD5E1"))
                self.setLineWidth(0.5)
                self.line(54, 750, 558, 750)

            # Footer
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 45, 558, 45)
            self.drawString(54, 32, "Platform Architect: Ashok Kumar A (2023MITEC042) • Lab 304 Hardware Prototyping")
            self.drawRightString(558, 32, f"Page {self._pageNumber} of {total_pages}")
            self.restoreState()

    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#00693E'),
        alignment=1,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#00A078'),
        alignment=1,
        spaceAfter=4
    )
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#64748B'),
        alignment=1,
        spaceAfter=14
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#00693E'),
        spaceBefore=12,
        spaceAfter=6
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=6
    )
    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F1F5F9'),
        spaceBefore=4,
        spaceAfter=6
    )
    table_text = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#1E293B')
    )
    table_hdr = ParagraphStyle(
        'TableHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.white
    )

    story = []

    # Title Banner
    story.append(Paragraph("VOLTCORE APEX ACADEMIA", title_style))
    story.append(Paragraph("Master Enterprise Technical Architecture & Operations Guide", subtitle_style))
    story.append(Paragraph("Madras Institute of Technology (MIT) Campus • Anna University, Chromepet<br/>Department of Electronics Engineering (Regulation 2023)<br/>Platform Lead / Systems Architect: Ashok Kumar A (2023MITEC042)", meta_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#00693E"), spaceAfter=12))

    # Section 1
    story.append(Paragraph("1. Executive Summary & Project Vision", h1_style))
    story.append(Paragraph(
        "VoltCore Apex Academia is an enterprise-grade academic learning management, physical laboratory automation, and hardware verification suite designed for the Department of Electronics Engineering at MIT Campus, Anna University, under ECE Regulation 2023. Engineered with an uncompromising zero-bloat philosophy, the platform guarantees sub-3ms SQLite Write-Ahead Logging (WAL) persistence, offline Progressive Web App (PWA) resilience across 39 verified static routes, and quiet passive-cooling operation tested on HP Victus developer workstations.",
        body_style
    ))
    story.append(Paragraph("<b>• Zero-Bloat Execution:</b> Pure native Python and deterministic WebAssembly solvers with zero background container overhead.", body_style))
    story.append(Paragraph("<b>• Sub-3ms SQLite WAL Persistence:</b> Concurrent, non-blocking read/write transactions backed by voltcore_lms.db in WAL mode.", body_style))
    story.append(Paragraph("<b>• 39-Route Offline PWA Resilience:</b> Dual service workers pre-cache static routes for zero downtime during campus network drops.", body_style))
    story.append(Paragraph("<b>• HP Victus Passive Cooling Safety:</b> Designed for passive thermal stability (<300MB memory, zero webcam loops, sub-8s test suite).", body_style))
    story.append(Paragraph("<b>• Comprehensive Test Coverage:</b> 325 passing automated unit tests across 32 pytest suites with 100% zero credential leakage.", body_style))

    # Section 2
    story.append(Paragraph("2. How It Is Made: System Architecture from Scratch to Advanced", h1_style))
    story.append(Paragraph(
        "The architecture is segmented into four cohesive tiers designed for extreme resilience and minimal hardware overhead:",
        body_style
    ))
    story.append(Paragraph("<b>1. Frontend Layer:</b> Astro 5 Static Site Generation (SSG) compiles 39 verified routes to pure static HTML/CSS. Dynamic modules utilize React 19 interactive islands (<code>client:load</code>) and Tailwind CSS glassmorphism, achieving sub-second initial paint times.", body_style))
    story.append(Paragraph("<b>2. Dual-Mode Backend Gateway (attendance_server.py):</b> Operates a primary Flask REST API with CORS headers. When deployed in restricted lab environments without pip packages, it automatically switches to Python's standard-library <code>http.server</code> handler with zero endpoint failure.", body_style))
    story.append(Paragraph("<b>3. Persistence Layer:</b> SQLite 3 configured in Write-Ahead Logging (<code>PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;</code>). WAL decouples read operations from write commits, eliminating database lock contention during high-concurrency lab sessions.", body_style))
    story.append(Paragraph("<b>4. Security & QA Gates:</b> Cryptographic authentication relies on PBKDF2-HMAC-SHA256 (600,000 iterations). Strict RBAC barriers protect administrative functions, while automated deployment audits verify that zero private credentials exist in client bundles.", body_style))

    story.append(PageBreak())

    # Section 3
    story.append(Paragraph("3. Module Encyclopedia: Complete Phases 1 through 30", h1_style))
    story.append(Paragraph(
        "Complete technical encyclopedia of all 30 engineered phases powering VoltCore Apex Academia:",
        body_style
    ))

    # Table of Phases
    table_data = [
        [
            Paragraph("Phase", table_hdr),
            Paragraph("Module Name", table_hdr),
            Paragraph("Route URL", table_hdr),
            Paragraph("Primary Logic & Formulations", table_hdr),
            Paragraph("Unique Laboratory Specialty", table_hdr)
        ]
    ]

    for p in PHASES_DATA:
        table_data.append([
            Paragraph(f"<b>P{p['num']}</b>", table_text),
            Paragraph(p['name'], table_text),
            Paragraph(f"<code>{p['route']}</code>", table_text),
            Paragraph(p['logic'], table_text),
            Paragraph(p['specialty'], table_text)
        ])

    pdf_table = Table(table_data, colWidths=[32, 110, 95, 135, 132])
    pdf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00693E')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(pdf_table)

    story.append(PageBreak())

    # Section 4
    story.append(Paragraph("4. How to Use the Platform (User, Faculty & Technician Manual)", h1_style))
    story.append(Paragraph("<b>Student Workflows:</b>", h2_style))
    story.append(Paragraph(
        "Students access all features via the Global Topbar or by pressing <code>Ctrl+K</code> (or <code>⌘K</code>) to launch the Instant Command Palette. Access <code>/component-inspector</code> to decode 4/5/6-band axial resistors with real-time graphical bands, look up SMD EIA-96 markings, size PCB trace widths using IPC-2221 formulas, and verify IC heatsink thermal requirements. Use <code>/exam-center</code> for timed GATE practice, and <code>/learning-productivity</code> for Pomodoro deep-work sessions with spaced repetition recall.",
        body_style
    ))

    story.append(Paragraph("<b>Faculty Workflows:</b>", h2_style))
    story.append(Paragraph(
        "Faculty members use <code>/faculty-workspace</code> to create Unit I–V lesson plans mapped to Bloom's Taxonomy cognitive levels (K1 to K5), grade lab exercises with weighted rubrics, and record Department Minutes of Meetings (MoM). On <code>/data-intelligence</code>, faculty audit Anna University Clause 7.2 student attendance compliance (>=75%) and review syllabus coverage heatmaps.",
        body_style
    ))

    story.append(Paragraph("<b>Lab Technician Workflows:</b>", h2_style))
    story.append(Paragraph(
        "Lab technicians open <code>/iot-lab</code> to monitor real-time telemetry across 8 dedicated workbench nodes (voltage, current, power P = V * I, temperature). The system automatically trips safety relays (>25V over-voltage, >3.0A over-current, >65°C over-temp). Technicians can remotely toggle relays or acknowledge alerts, and monitor database health on <code>/system-health</code>.",
        body_style
    ))

    # Section 5
    story.append(Paragraph("5. Developer Setup, Build & Verification Guide", h1_style))
    story.append(Paragraph("Standard execution steps to install, launch, build, and audit the application:", body_style))
    cmd_text = (
        "npm install                                  # Install frontend Node dependencies<br/>"
        "python attendance_server.py                  # Launch backend gateway on port 5000<br/>"
        "npm.cmd run build                            # Compile all 39 static routes (dist/*.html)<br/>"
        "python -m pytest tests/                      # Run 325 unit tests across 32 suites (~7s)<br/>"
        "python deploy/production_readiness_audit.py  # Audit 39 static routes and 0 privacy leaks<br/>"
        "python scripts/content_qa_validator.py       # Validate 17/17 courseware modules"
    )
    story.append(Paragraph(cmd_text, code_style))

    # Section 6
    story.append(Paragraph("6. Master API & SQLite WAL Database Schema Reference", h1_style))
    story.append(Paragraph(
        "<b>Key REST API Endpoints:</b><br/>"
        "• <code>POST /api/attendance</code>: Contactless RFID card scan check-in<br/>"
        "• <code>GET /api/academic/overview</code>: Academic calendar milestones, syllabus progress, DAG prerequisite check<br/>"
        "• <code>POST /api/productivity/pomodoro/log</code>: Log completed deep work focus session<br/>"
        "• <code>POST /api/digital/solve-kmap</code>: Quine-McCluskey 2–4 variable Boolean minimization<br/>"
        "• <code>POST /api/analog/sallen-key</code>: Sallen-Key active filter 20-point Bode plot calculator<br/>"
        "• <code>POST /api/project/verify-compatibility</code>: Automated 5V-to-3.3V GPIO, LDO, and I2C hardware conflict check<br/>"
        "• <code>GET /api/iot/overview</code>: Lab 304 8-bench live power consumption and safety status<br/>"
        "• <code>POST /api/iot/bench/relay</code>: High-voltage AC/DC workbench relay isolation control<br/>"
        "• <code>POST /api/inspector/axial-decode</code>: IEC 60062 4/5/6-band resistor color decoding with TCR<br/>"
        "• <code>POST /api/inspector/smd-decode</code>: SMD 3/4-digit and EIA-96 1% metal film decoder<br/>"
        "• <code>POST /api/inspector/pcb-trace</code>: IPC-2221 PCB trace width and Joule loss calculator<br/>"
        "• <code>POST /api/inspector/ic-thermal</code>: IC package silicon junction temperature safety assessment",
        body_style
    ))
    story.append(Paragraph(
        "<b>Core Database Tables in voltcore_lms.db:</b><br/>"
        "<code>users</code>, <code>attendance_records</code>, <code>academic_calendar_events</code>, <code>ece_formula_catalog</code>, <code>pomodoro_sessions</code>, <code>saved_kmap_solutions</code>, <code>analog_circuit_calculations</code>, <code>project_proposals</code>, <code>faculty_lecture_plans</code>, <code>accessibility_lexicon</code>, <code>data_quality_audit_logs</code>, <code>reliability_apm_metrics</code>, <code>iot_bench_nodes</code>, <code>component_inspection_history</code>, <code>saved_pcb_trace_calculations</code>.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Generated PDF guide: {PDF_PATH}")


# ========================================================================================
# Main Script Execution
# ========================================================================================

def main():
    start_time = time.time()
    tracemalloc.start()

    print("=" * 80)
    print("VOLTCORE APEX ACADEMIA — MASTER DOCUMENTATION GENERATION")
    print("Madras Institute of Technology (MIT) Campus, Anna University")
    print(f"Platform Lead: Ashok Kumar A (2023MITEC042) • Target: {DOCS_DIR}")
    print("=" * 80)

    # 1. Generate Markdown Guide
    generate_markdown_guide()

    # 2. Generate DOCX Guide
    generate_docx_guide()

    # 3. Generate PDF Guide
    generate_pdf_guide()

    elapsed = time.time() - start_time
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_mb = peak_mem / (1024 * 1024)

    print("-" * 80)
    print(f"Execution Completed in: {elapsed:.2f} seconds (Target: < 3.0s)")
    print(f"Peak Memory Footprint:  {peak_mb:.2f} MB (Target: < 200MB)")
    print("Generated Artifacts:")
    print(f"  1. {DOCX_PATH} ({os.path.getsize(DOCX_PATH)} bytes)")
    print(f"  2. {PDF_PATH} ({os.path.getsize(PDF_PATH)} bytes)")
    print(f"  3. {MD_PATH} ({os.path.getsize(MD_PATH)} bytes)")
    print("=" * 80)


if __name__ == "__main__":
    main()
