# VoltCore Apex Academia — Custom Artwork & Canva Asset Drop-In Guide
**Department of Electronics Engineering | Madras Institute of Technology (MIT) Campus, Anna University**  
*Regulation 2023 — Electronics and Communication Engineering (ECE)*

---

## 1. Overview & Architectural Role
VoltCore Apex Academia features a bespoke, vector-first visual system designed to render beautifully across all **18 institutional CSS themes** (including Dark MIT Oceanic, Slate Midnight, Nordic Frost, Crimson Research, and High-Contrast Accessibility).

This directory (`public/assets/covers/`) and its sibling asset directories are pre-wired to accept custom graphics designed in **Canva**, Figma, Adobe Illustrator, or Inkscape.

---

## 2. Dimensional & Technical Specifications

| Asset Type | Target Path | Dimensions | Aspect Ratio | Formats | Max File Size | Safe Margin |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Course & Unit Covers** | `public/assets/covers/` | `1200 × 400 px` | 3:1 | SVG (preferred), WebP | `< 15 KB` (SVG) / `< 60 KB` (WebP) | 48px on all edges |
| **Subject Emblems** | `public/assets/branding/` | `512 × 512 px` | 1:1 | SVG (transparent) | `< 10 KB` | 32px circular safe zone |
| **IEEE Schematic Diagrams** | `public/assets/diagrams/` | `800 × 500 px` | 16:10 | SVG (IEEE Std 315 / 1076) | `< 20 KB` | 24px around text labels |

---

## 3. Mandatory Design Invariants

1. **ZERO VISIBLE COURSE CODES:**
   - **Never include alphanumeric course codes** (such as `EC23C01`–`EC23S01`, `EC8702`, `IOT8701`, etc.) in the artwork, titles, labels, or exported file names.
   - Use clean, professional discipline names:
     - `Signals, DSP & Wavelet Analysis`
     - `Semiconductor Devices & Integrated Circuits`
     - `Digital Systems & Computer Architecture`
     - `Electromagnetic Waves, Antennas & RF`
     - `Embedded Real-Time Systems & IoT`
     - `Linear Control Theory & Instrumentation`

2. **THEME-ADAPTIVE CONTRAST & ACCESSIBILITY:**
   - Backgrounds should use deep dark-slate tones (`#070d1e`, `#0a1128`, `#0f172a`) with subtle linear gradients.
   - Use glowing cyber/technical accents:
     - **Cyan Primary:** `#38bdf8` / `#06b6d4`
     - **Emerald Secondary:** `#10b981` / `#34d399`
     - **Indigo / Violet Accent:** `#818cf8` / `#a855f7`
     - **Amber / Warning:** `#f59e0b` / `#fbbf24`
   - Ensure contrast ratio $> 7:1$ when text is overlaid on cover images.

3. **VECTOR SVG OPTIMIZATION:**
   - When exporting from Canva or Illustrator:
     - Choose **SVG** format.
     - Enable **Outline / Convert text to paths** if custom fonts are used.
     - Minify SVG with tools like SVGO or remove unused `metadata` tags.
     - Keep gradient definitions within `<defs>` tags.

---

## 4. Pre-Wired Asset Map

Drop custom-designed replacement SVGs directly into `public/assets/covers/` with the exact filenames below:

| Target Filename | Subject Domain / Category | Featured Technical Motifs |
| :--- | :--- | :--- |
| `cover_signals_dsp.svg` | Digital Signal Processing, Filter Design, Wavelets | Radix-2 FFT butterflies, Dirac delta combs, KaTeX formulas |
| `cover_analog_devices.svg` | Analog Electronics, Op-Amps, BJTs, MOSFETs | Hybrid-$\pi$ models, differential pairs, Bode curves |
| `cover_digital_vlsi.svg` | Digital Logic, VLSI Design, Verilog, RISC-V | 5-stage pipeline buses, clock trees, cell layout grids |
| `cover_comm_rf.svg` | Wireless Comm, Antennas, RF Systems | QAM constellations, Smith charts, radiation patterns |
| `cover_embedded_iot.svg` | Microcontrollers, ARM Cortex-M, STM32, RTOS | NVIC interrupt trees, DMA circular buffers, AHB matrix |
| `cover_control_em.svg` | Control Systems, State-Space, EM Fields | Root locus plots, Nyquist contours, Maxwell wave fronts |

---

## 5. How to Export from Canva

1. Create a custom design in Canva:
   - For Covers: `1200` wide by `400` tall (px).
   - For Emblems: `512` wide by `512` tall (px).
2. Choose **Share** $\to$ **Download**.
3. Select **SVG** as file type (with *Transparent Background* for emblems).
4. Save the file into the corresponding folder listed above.
5. Verify in browser or run `npm run build` to ensure instant visual updates.
