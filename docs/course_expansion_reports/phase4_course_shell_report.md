# VoltCore Apex Academia — Modular Course Shell & Branding Architecture
**Madras Institute of Technology (MIT) Campus, Anna University • Department of Electronics Engineering**  
*Regulation 2023 Curriculum Expansion | Lead Systems Architect: Ashok Kumar A*

---

## 1. Executive Summary

This phase advances the individual course shell experience with specialized departmental branding tokens, responsive vector iconography, dynamic breadcrumb routing, and state-preserving unit-wise navigation across **Units I through V**.

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 VOLTCORE COURSE BRANDING ARCHITECTURE                                 │
├───────────────┬───────────────────┬──────────────────────┬──────────────────────┬─────────────────────┤
│ Course Code   │ Subject Title     │ Color Family Token   │ Glowing Accent Box   │ Vector Domain Badge │
├───────────────┼───────────────────┼──────────────────────┼──────────────────────┼─────────────────────┤
│ EC23S01       │ Numerical & DSP   │ Emerald (#00F0B5)    │ 0 0 25px Emerald     │ Discrete Sample DSP │
│ EC23C03       │ Electronic Device │ Amber (#F59E0B)      │ 0 0 25px Amber       │ Bandgap Recombine   │
│ EC23E04       │ Optics & Lasers   │ Cyan (#06B6D4)       │ 0 0 25px Cyan        │ Resonator Mirrors   │
│ EC8702        │ Embedded Systems  │ Indigo (#6366F1)     │ 0 0 25px Indigo      │ ARM Cortex-M Die    │
└───────────────┴───────────────────┴──────────────────────┴──────────────────────┴─────────────────────┘
```

---

## 2. Key Architectural Upgrades

### 1. Course Branding Tokens & Hardware-Accelerated Glow Effects
- **Tailwind Configuration (`tailwind.config.mjs`)**:
  - Registered per-course color families: `course-emerald`, `course-amber`, `course-cyan`, and `course-indigo`.
  - Added hardware-accelerated glowing drop-shadows:
    - `'course-emerald-glow': '0 0 25px rgba(0, 240, 181, 0.35)'`
    - `'course-amber-glow': '0 0 25px rgba(245, 158, 11, 0.35)'`
    - `'course-cyan-glow': '0 0 25px rgba(6, 182, 212, 0.35)'`
    - `'course-indigo-glow': '0 0 25px rgba(99, 102, 241, 0.35)'`
    - Plus inner ambient glow definitions (`inset 0 0 15px ...`).
- **Global CSS Utility Classes (`src/styles/global.css`)**:
  - Implemented `.course-card-*`, `.course-glow-*`, and `.course-badge-*` utilities using `transform: translateZ(0); will-change: box-shadow, border-color;` to leverage GPU compositing and protect the HP Victus CPU from software rendering overhead.

### 2. Departmental Badge Icon Suite
Custom SVG vector integration in [`src/components/CourseShellHub.jsx`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/src/components/CourseShellHub.jsx) adhering to ECE domain specifications:
- **`EC23S01` (DspWaveformSvg)**: Discrete impulse train $x[n]$ with stem markers, continuous carrier wave, and FFT spectral power frequency bins.
- **`EC23C03` (SemiconductorBandgapSvg)**: Conduction Band ($E_c$), Valence Band ($E_v$), dashed Fermi level ($E_F$), electron-hole recombination, and photon transition arrow across forbidden gap $E_g$.
- **`EC23E04` (LaserResonatorSvg)**: Confocal mirrors ($M_1, M_2$), gain medium active crystal, internal standing optical wave, and coherent collimated laser wavefronts.
- **`EC8702` (ArmCortexMicrocontrollerSvg)**: QFP chip package leads, central silicon CPU die, internal bus topology (AHB/APB), and interrupt control labels ("ARM M4").

### 3. Unit-Wise Navigation Tabs & Dynamic Breadcrumbs
- **Dynamic Breadcrumbs**: Reactive hierarchical navigation trail:
  `Home / Course Hub / EC23S01 / Unit III: IIR Digital Filter Synthesis`
  Enables one-click jumps between global catalog and specific unit levels.
- **Roman Numeral Strip (Units I to V)**:
  Direct unit switcher preserving syllabus hours, deliverable topics, and laboratory linkages.
- **Unit Sub-View Selectors**:
  - `[ 📋 Syllabus Topics ]`: Course syllabus breakdown and curriculum deliverable hours.
  - `[ 📐 KaTeX Formulations ]`: Formally rendered LaTeX expressions with parameter definitions.
  - `[ 🧪 Lab Exercises & Simulator ]`: Laboratory experiment alignment with direct `"Launch Simulator Workbench ➔"` routing.

---

## 3. Verification & Compliance Matrix

| Target Verification | Tool / Method | Metric / Result | Status |
| :--- | :--- | :--- | :--- |
| **TypeScript Static Check** | `npx tsc --noEmit` | 0 Errors | PASS |
| **Course Engine Pytest** | `python -m pytest tests/test_course_config.py` | 8/8 passed in 0.07s | PASS |
| **Full Regression Suite** | `python -m pytest tests/` | 619/619 passed in 13.84s | PASS |
| **Astro Production Build** | `npm run build` | 60 static pages in 7.62s | PASS |
| **Git Synchronization** | `git push origin main` | Synced to `a897c6d` | PASS |
| **Thermal Budget** | Passive CPU measurement | Zero polling daemons, <8% CPU | PASS |
| **Attribution Policy** | Code audit | Peer-neutral departmental views | PASS |
