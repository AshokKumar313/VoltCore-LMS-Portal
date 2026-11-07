# VoltCore Apex Academia — Complete LMS Current Status Audit
# 04. Academic Curriculum Audit

**Audit Date**: November 7, 2026  
**Auditor**: ECE Curriculum Specialist & Academic Systems Reviewer  
**Audit Location**: `docs/audits/04_ACADEMIC_CURRICULUM_AUDIT.md`

---

## 1. Academic Infrastructure Architecture

VoltCore Apex Academia models higher engineering education under the **Anna University Regulation 2023** framework, specifically calibrated for the Department of Electronics Engineering at Madras Institute of Technology (MIT) Campus.

The academic structure incorporates:
- **Choice-Based Credit System (CBCS)**: Modular course classifications (PCC, PEC, OEC, EEC, BSC, ESC).
- **Outcome-Based Education (OBE)**: Explicit Course Outcomes ($CO_1$ through $CO_5$) mapped to Program Outcomes ($PO_1$ to $PO_{12}$) and Program Specific Outcomes ($PSO_1, PSO_2$) with Bloom's Taxonomy attainment thresholds ($L_1$ to $L_6$).
- **Prerequisite Directed Acyclic Graph (DAG)**: Strict topological dependencies governed by [`backend/course_config_engine.py`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/backend/course_config_engine.py).

---

## 2. Course Catalogue & Priority Courses

The course configuration schema ([`src/data/course_config_schema.ts`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/src/data/course_config_schema.ts)) establishes deep curriculum data for four priority cornerstone subjects:

| Subject Code | Official Course Title | Semester | Category | Credits | Hours (L-T-P) | Content Depth |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EC23C03** | Electronic Devices and Circuits | 3 | PCC | 4 | 3-0-2 | Complete (5 Units, COs, Labs) |
| **EC23S01** | Python Digital Signal Processing | 4 | EEC | 2 | 0-0-4 | Complete (5 Units, COs, Labs) |
| **EC23E04** | Optics, Lasers and Fiber Optics | 5 | PEC | 3 | 3-0-0 | Complete (5 Units, COs, Labs) |
| **EC8702** | Advanced Embedded Systems Architecture | 7 | PCC | 3 | 3-0-0 | Complete (5 Units, COs, Labs) |

Each of these priority courses defines:
1. Complete 5-unit syllabus descriptions with lecture hour breakdowns.
2. 5 discrete Course Outcomes with Bloom's levels and PO/PSO mapping.
3. Module-to-lab experiment relationships specifying physical apparatus and simulation components.
4. Hard and soft prerequisite DAG links.
5. Primary textbooks (e.g., Sedra & Smith, Oppenheim & Schafer, Keiser, Sloss) and reference literature.

---

## 3. Tier-3 Specialization Tracks (10 Modules)

Beyond the standard undergraduate curriculum, the platform provides 10 industrial-grade specialization tracks located in `src/content/modules/`:

| Module Code | Specialization Track Title | Difficulty | Hardware / Workbench Target |
| :--- | :--- | :--- | :--- |
| **IOT8701** | IoT Edge Node Foundations & Bare-Metal GPIO | Fundamental | ESP32 DevKit v4, PIR, LDR |
| **AUTO8702** | Automotive Radar & Ultrasonic Edge Sensing | Intermediate | HC-SR04, MCP2515 CAN Bus, DS18B20 |
| **UAV8703** | Defense UAV Telemetry & FHSS Modulation | Advanced | LoRa SX1276, Doppler Shift Solver |
| **RAIL8704** | High-Speed Railway Edge AI & Track Defect Classification | Advanced | OpenMV / Edge Camera, TensorFlow Lite |
| **RISCV8705** | 5-Stage Pipelined RV32I RISC-V Soft-Core Design | Advanced | RV32I Pipeline Simulator, Verilog RTL |
| **RTOS8706** | Real-Time Operating Systems (FreeRTOS) Scheduling | Intermediate | FreeRTOS Preemptive Kernel Simulator |
| **ANLG8707** | Advanced Analog Small-Signal & High-Frequency SI | Advanced | Non-Linear MNA Solver, S-Parameters |
| **DMA8708** | Advanced ARM Cortex-M DMA & Zero-Copy IPC | Advanced | Ping-Pong Buffer Bench, STM32F401 |
| **TML8709** | TinyML Edge AI Neural Networks & Vibration FFT | Advanced | CMSIS-NN Quantizer, Anomaly Detector |
| **INST8710** | Advanced ECE Instrumentation & Bode Plot Dynamics | Intermediate | Complex Plane Solver, K-Map Minimizer |

---

## 4. Genuinely Developed Content vs. Placeholder Shells

A critical finding of this audit is the distinction between actual high-density educational content and curricular skeletons:

### Genuinely Developed Content (High Engineering Quality)
- **STM32 Academy**: 21 chapters in `src/content/stm32-academy/` (over 250 KB of original technical markdown). Features exact register offsets, bitmask truth tables, assembly startup routines, vector tables, and linker script derivations.
- **Tier-3 Specialization Modules**: 10 modules in `src/content/modules/` containing thorough mathematical formulations, timing diagrams, and lab instructions.
- **Priority Course Metadata**: Full CBCS parameters, Bloom's level mappings, and textbook citations in `course_config_schema.ts`.
- **GATE ECE Question Bank**: Interactive numerical solvers for GATE questions in `src/components/GateEceQuestionBank.jsx` and `GateEceInteractiveSolvers.jsx`.

### Skeletons & Placeholders (Requires Expansion)
- **Broad 8-Semester Curriculum**: In [`backend/academic_management_engine.py`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/backend/academic_management_engine.py), approximately 40 standard engineering courses (e.g., *Electromagnetic Fields*, *Transmission Lines*, *Environmental Science*) exist as syllabus records in SQLite tables (`academic_syllabus_subjects`), but **do not possess dedicated 5-unit MDX lesson chapters or slide decks**.
- **Lecture Presentations & Slide Decks**: The platform does not currently store or render PowerPoint (`.pptx`) or PDF slide presentations; all educational content is presented as interactive web reading chapters and interactive simulation islands.
- **Viva Voce Oral Examination**: The viva simulator uses keyword heuristics against pre-defined question templates rather than open-ended dialogue evaluation.

---

## 5. Learning Analytics & Student Assessment

1. **Course Quizzes ([`src/data/course_quiz_data.ts`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/src/data/course_quiz_data.ts))**:
   - Multiple-choice questions with formula explanations, common trap warnings, and Bloom's cognitive taxonomy tags.
   - Immediate feedback with score tallying.
2. **Laboratory Workbenches ([`src/data/course_lab_data.ts`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/src/data/course_lab_data.ts))**:
   - Structured experimental protocols: Objective, Apparatus, Formulae, Procedure, Observation Table, and Post-Lab Viva Questions.
3. **Capstone Projects ([`src/data/course_projects_data.ts`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/src/data/course_projects_data.ts))**:
   - Project specifications including Bill of Materials (BOM), calculation worksheets, and rubric marks (Literature Review, Hardware Design, Firmware Quality, Demonstration, Viva).
4. **Learning Analytics Engine ([`backend/learning_analytics_engine.py`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/backend/learning_analytics_engine.py))**:
   - Calculates student engagement indices, quiz velocity, OBE attainment percentages, and mastery token eligibility.

---

## 6. Curricular Inconsistencies & Recommendations

1. **Inconsistent Institutional Labeling**:
   - Several files still refer to `"Madras Institute of Technology (MIT) Campus, Anna University"`, while sanitized production pages display `"Autonomous Engineering Cluster"` or `"VoltCore Apex Academia"`. This inconsistency caused 13 test assertion failures.
2. **Missing Downstream Prerequisites**:
   - Advanced courses like `RISCV8705` list `EC8702` as a prerequisite, but the DAG engine allows students who bypass the sidebar navigation to open the simulator directly via `/simulation` or `/workspace`.
3. **Curricular Depth Recommendation**:
   - Preserve the depth of STM32 Academy and Tier-3 tracks as the platform's benchmark standard. For general ECE subjects, integrate curated open-access references (NPTEL, MIT OCW) rather than drafting hundreds of static textbook chapters from scratch.
