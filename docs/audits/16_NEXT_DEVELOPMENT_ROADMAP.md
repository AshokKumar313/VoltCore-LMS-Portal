# VoltCore Apex Academia — Complete LMS Current Status Audit
# 16. Next Development Roadmap

**Audit Date**: November 7, 2026  
**Auditor**: Principal Software Architect & ECE Educational Platform Director  
**Audit Location**: `docs/audits/16_NEXT_DEVELOPMENT_ROADMAP.md`

---

## 1. Roadmap Strategic Objectives

This development roadmap is derived strictly from the evidence established in the audit. It organizes future work into six sequential, risk-prioritized stages. For every proposed feature, the roadmap states whether the capability **Already Exists**, **Needs Improvement**, or is **Completely New**, explicitly preventing redundant development.

---

## 2. Six-Stage Development Roadmap

### Stage A — Critical Corrections (Security, Data Integrity & Test Health)
*Target: Immediate execution prior to any new feature development.*

| Proposed Work Item | Classification | Rationale & Scope |
| :--- | :--- | :--- |
| **A1. Replace Python `eval()` with Safe AST Visitor** | **Needs Improvement** (Security Critical) | Replace `eval()` in `vlsi_physical_design_engine.py` (L256) and `digital_electronics_engine.py` (L327) with an `ast.NodeVisitor` that allows only boolean/bitwise operators, completely eliminating the object-traversal RCE vulnerability. |
| **A2. Fix 13 Legacy Test Assertions** | **Needs Improvement** | Update the 13 failing test assertions in legacy phase tests to match sanitized institutional branding (`"Autonomous Engineering Cluster"`), restoring full 100% CI pass rate across all 977 tests. |
| **A3. Enforce Mandatory Production JWT Secret** | **Needs Improvement** | Modify `security_auth.py` to raise a runtime exception if `VOLTCORE_JWT_SECRET` is unset or matches the default development key when running in production mode. |
| **A4. Add Direct Route Alias for `/stm32-academy`** | **Needs Improvement** | Add an Astro redirect in `astro.config.mjs` routing `/stm32-academy` directly to `/embedded-systems/stm32-academy/` to prevent 404 errors. |

---

### Stage B — LMS Completion (Authentication, Student Sessions & Core Workflows)
*Target: Transitioning the platform from open prototype to true multi-tenant LMS.*

| Proposed Work Item | Classification | Rationale & Scope |
| :--- | :--- | :--- |
| **B1. Implement Frontend Auth Context & Route Guard** | **Completely New** (Frontend) | The backend already has PBKDF2 hashing and JWT verification. Build a React/Astro client-side `<AuthProvider>` and route guard intercepting unauthenticated navigation to `/faculty-admin`, `/enterprise-admin`, and student dashboards. |
| **B2. Unify Dual SQLite Databases** | **Needs Improvement** | Consolidate `voltcore_telemetry.db` into `voltcore_lms.db` or create an explicit centralized connection router in `sqlite_wal_optimizer.py` to eliminate table duplication (`student_portfolios`, `study_groups`). |
| **B3. Student Lab Report PDF Upload Pipeline** | **Completely New** | Build a secure multipart file-upload endpoint and PDF viewer for student laboratory writeups, pairing physical observations with simulation logs. |
| **B4. Offline IndexedDB Quiz Submission Spooling** | **Completely New** | Connect the Service Worker background sync to an IndexedDB spool, allowing students in rural/disconnected environments to complete quizzes offline and automatically submit them upon reconnection. |

---

### Stage C — Engineering Education Expansion (Curriculum Verticals)
*Target: Expanding textbook lessons across the broader 8-semester ECE curriculum.*

| Proposed Work Item | Classification | Rationale & Scope |
| :--- | :--- | :--- |
| **C1. Expand STM32 Academy Chapters 18–21** | **Needs Improvement** | Augment Chapters 18–21 (Low Power, Watchdogs, Bootloader, TinyML) with additional hardware oscilloscope captures and standalone Makefile build templates. |
| **C2. Author Core ECE 5-Unit Lesson Chapters** | **Completely New** | Create high-density MDX textbook modules for remaining core ECE subjects (Electromagnetic Fields, Analog CMOS Design, Control Systems) matching the depth of the 4 priority courses. |
| **C3. Add RV32M Hardware Multiplication Extension** | **Completely New** | Extend `riscv_processor_engine.py` to support hardware integer multiplication and division (`MUL`, `MULH`, `DIV`, `REM`) with multi-cycle execution modeling. |

---

### Stage D — Simulation and Research (Solver Extensions & Virtual Labs)
*Target: Deepening numerical accuracy and experimental laboratory fidelity.*

| Proposed Work Item | Classification | Rationale & Scope |
| :--- | :--- | :--- |
| **D1. Frequency-Domain AC Small-Signal MNA Solver** | **Needs Improvement** | Add dedicated small-signal linear AC matrix formulation to `analog_mna_engine.py` for automated Bode plot generation directly from SPICE netlists. |
| **D2. Double-Stub Tuner Matching Calculator** | **Completely New** | Extend `rf_smith_chart_engine.py` to compute double-stub tuner spacings and susceptances for fixed-position RF matching networks. |
| **D3. WebAudio Real-Time FFT Microphone Ingest** | **Completely New** | Connect `VirtualOscilloscope.jsx` to the browser WebAudio API to enable live microphone audio waveform capture and real-time spectrum analysis. |
| **D4. WebAssembly QEMU Embedded Simulator Fallback** | **Completely New** | Package an in-browser WebAssembly QEMU ARM emulator to provide completely offline, zero-network firmware simulation without Wokwi web dependency. |

---

### Stage E — Professional Engineering Platform (Portfolio & Industry Bridge)
*Target: Career preparation, portfolio export, and accreditation compliance.*

| Proposed Work Item | Classification | Rationale & Scope |
| :--- | :--- | :--- |
| **E1. Automated GitHub Pages Student Portfolio Publisher** | **Completely New** | Add an automated OAuth GitHub integration allowing students to deploy their ATS-verified engineering portfolios directly to GitHub Pages with one click. |
| **E2. IEEE Paper LaTeX / PDF Export Generator** | **Completely New** | Build a server-side ReportLab / LaTeX compiler that formats student research hypotheses and capstone projects into publication-ready two-column IEEE manuscripts. |
| **E3. Automated OBE Attainment & NAAC Audit Reporter** | **Needs Improvement** | Connect `accreditation_compliance_engine.py` directly to quiz and lab submission grades to generate one-click NBA/NAAC Course Outcome attainment spreadsheets. |

---

### Stage F — Optimization and Production Hardening
*Target: Scale, maintainability, and enterprise deployment.*

| Proposed Work Item | Classification | Rationale & Scope |
| :--- | :--- | :--- |
| **F1. Refactor Monolithic Server into Flask Blueprints** | **Needs Improvement** | Split the 9,739-line `attendance_server.py` into modular route files (`routes/mna.py`, `routes/riscv.py`, `routes/vlsi.py`, `routes/academic.py`), improving maintainability and startup speed. |
| **F2. Lazy-Load Off-Screen React Islands** | **Needs Improvement** | Convert off-screen React components from `client:load` to `client:visible`, accelerating mobile page rendering and cutting hydration latency. |
| **F3. Automated SQLite Backup Daemon** | **Completely New** | Deploy a lightweight container or background task executing daily `sqlite3 ".backup"` snapshots to ensure disaster recovery. |
| **F4. Configurable `PUBLIC_API_URL` for Production** | **Needs Improvement** | Parameterize frontend API fetch calls to support cross-domain production hosting on cloud platforms (Render, Railway, AWS). |

---

## 3. What to Avoid Developing (Already Fully Implemented)

To maintain focused engineering efficiency, **DO NOT reinvent the following features**:
- ❌ **Do not write another MNA Circuit Solver**: `backend/analog_mna_engine.py` already implements Newton-Raphson DC OP, transient integration, and non-linear diode/BJT/MOSFET models.
- ❌ **Do not write another RISC-V 5-Stage Pipeline Simulator**: `backend/riscv_processor_engine.py` already handles RV32I parsing, data forwarding, load-use stalls, and branch flushes.
- ❌ **Do not write another SVA Formal Assertion Engine**: `backend/vlsi_physical_design_engine.py` already supports temporal implications, delay ranges, and sampled value functions.
- ❌ **Do not write another Smith Chart Calculator**: `backend/rf_smith_chart_engine.py` already solves complex reflection, admittance, and single-stub matching.
- ❌ **Do not rewrite STM32 Chapters 1–17**: The existing 17 chapters are exhaustive, register-accurate, and pedagogically sound.
