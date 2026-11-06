# Phase 8 Engineering Report: Laboratory Simulators & Interactive Benchmarks Expansion

**VoltCore Apex Academia — Department of Electronics Engineering**  
**Institution:** Madras Institute of Technology (MIT Campus), Anna University, Chennai  
**Regulation:** Anna University Regulation 2023 (CBCS & NBA Tier-1 Aligned)  
**Lead Systems Architect & Principal ECE Educator:** Ashok Kumar A  
**Hardware Baseline:** HP Victus (`LAPTOP-3NEGBVLE`) | OS: Windows 11  
**Thermal Standard:** Zero Background Polling Daemons • Passive CPU Footprint (<8%) • Lightweight SQLite WAL Mode

---

## 1. Executive Summary

Phase 8 expands the individual course experience for **VoltCore Apex Academia** by deploying dedicated, interactive, client-side laboratory workbenches. This module provides:
1. **Interactive Real-Time Simulation Workbenches** for all 4 priority courses (`EC23S01`, `EC23C03`, `EC23E04`, `EC8702`).
2. **SVG Waveform & Characteristic Curve Visualizers**:
   - `EC23S01`: Butterworth IIR Filter Frequency Response $|H(f)|$ (Bode plot) with -3dB cutoff threshold and roll-off rate ($-20 \times N\text{ dB/decade}$).
   - `EC23C03`: Semiconductor Diode Shockley exponential IV curve and MOSFET saturation output characteristic curve family.
   - `EC23E04`: Optical laser cavity universal $(g_1 - g_2)$ stability diagram with hyperbola boundaries ($g_1 g_2 = 1$) and longitudinal mode spacing $\Delta \nu$.
   - `EC8702`: FreeRTOS Rate Monotonic Scheduling (RMS) utilization stacked bar chart and ARM Cortex-M4 NVIC tail-chaining benchmark (6 cycles vs 24 cycles).
3. **Observation Data Logger with CSV Export**: Students can record trial points locally using browser `localStorage` (zero background polling daemons).
4. **Viva-Voce & Laboratory Rubric**: Anna University Regulation 2023 safety protocols and conceptual viva-voce questions.

---

## 2. Laboratory Exercise Matrix & Physics Formulations

The laboratory catalog ([`src/data/course_lab_data.ts`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/src/data/course_lab_data.ts)) contains structured configurations across the 4 priority courses:

| Course Code | Laboratory Title | Platform & Apparatus | Governing Physical Formulations |
| :--- | :--- | :--- | :--- |
| **`EC23S01`** | Butterworth DSP Filter Response & FFT Spectrum | Python SciPy, Digital Oscilloscope, Workstation | $$|H(j\Omega)|^2 = \frac{1}{1 + (\Omega / \Omega_c)^{2N}}, \quad \text{Roll-off} = -20 \times N\text{ dB/dec}, \quad f_{\text{Nyquist}} = \frac{f_s}{2}$$ |
| **`EC23C03`** | Semiconductor Diode & MOSFET IV Curve Tracer | Variable DC Supply, Keithley DMM, 2N7000 MOSFET, 1N4148 Diode | $$I_D = I_S \left( e^{\frac{V_D}{\eta V_T}} - 1 \right), \quad r_d = \frac{\eta V_T}{I_D}, \quad I_{D,\text{sat}} = \frac{1}{2} k_n (V_{GS} - V_{th})^2$$ |
| **`EC23E04`** | Laser Resonator Stability & Cavity Mode Simulator | He-Ne Laser (632.8 nm), Optical Rail, Dielectric Mirrors ($R_1, R_2$) | $$g_1 = 1 - \frac{L}{R_1}, \quad g_2 = 1 - \frac{L}{R_2}, \quad 0 \le g_1 g_2 \le 1, \quad \Delta \nu = \frac{c}{2L}$$ |
| **`EC8702`** | FreeRTOS Task Scheduler & Interrupt Latency Benchmarks | STM32F401RE Nucleo-64 (ARM Cortex-M4 84MHz), Saleae Logic Analyzer | $$U = \sum_{i=1}^n \frac{C_i}{T_i} \le n(2^{1/n} - 1), \quad T_{\text{tail-chain}} = 6\text{ cycles (75\% latency savings)}$$ |

---

## 3. UI Component Architecture: [`CourseLabSimulator.jsx`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/src/components/CourseLabSimulator.jsx)

The simulation engine is embedded directly into [`CourseShellHub.jsx`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/src/components/CourseShellHub.jsx) under the dedicated `simulator` tab.

```mermaid
flowchart TD
    A["CourseShellHub Navigation ('simulator' Tab)"] --> B["CourseLabSimulator Component"]
    B --> C["Lab Exercise Switcher (Unit I / II / IV)"]
    C --> D["Parameter Controls & Benchmark Presets"]
    D --> E["100% Client-Side Physics Calculation Engine"]
    E --> F["Real-Time SVG Waveform / Diagram Canvas"]
    F --> G["Analytical Metrics Cards (Gain, rd, g-Product, Total U%)"]
    F --> H["Record Observation Button"]
    H --> I["Observation Data Table (localStorage & CSV Export)"]
    B --> J["Viva-Voce & Reg 2023 Safety Protocol"]
```

---

## 4. Backend Engine: [`backend/course_lab_engine.py`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/backend/course_lab_engine.py)

- **Analytical Physics Simulation**: Python backend models replicating client-side physics calculations for automated assessment grading.
- **Catalog Verification**: Complete integrity checks ensuring parameters, apparatus, and viva-voce entries are present.
- **SQLite WAL Observation Telemetry**: High-concurrency logging using Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) with clean connection handling to avoid Windows file lock collisions.

---

## 5. Verification & Testing Metrics

### Pytest Verification
- **Targeted Lab Tests:** [`tests/test_course_labs.py`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/tests/test_course_labs.py) — **7/7 passed in 0.19s**.
- **Full Pytest Regression Suite:** **640/640 passed in 14.24s** across all phases without regressions.

### Static & Production Builds
- **TypeScript:** `npx tsc --noEmit` — 0 errors.
- **Astro Static Production Build:** `npm run build` — **60 pages built in 7.85s**.
- **Git Remote Synchronization:** Committed (`eeac6db`) and pushed to `https://github.com/AshokKumar313/VoltCore-LMS-Portal.git` on branch `main`.

---

## 6. Hardware & Thermal Protection Profile (HP Victus)

- **Polling Loop Overhead:** 0% (Reactive SVG rendering on parameter change).
- **Background Daemons:** 0.
- **CPU Footprint:** < 6% throughout the testing and compilation lifecycle.
