# VoltCore Apex Academia — Custom Artwork & Canva Asset Drop-In Guide
**Department of Electronics Engineering | Madras Institute of Technology (MIT) Campus, Anna University**  
*Regulation 2023 — Electronics and Communication Engineering (ECE)*

---

## 1. Overview & Architectural Role
VoltCore Apex Academia features a bespoke, vector-first visual system designed to render beautifully across all **18 institutional CSS themes** (including Dark MIT Oceanic, Slate Midnight, Nordic Frost, Crimson Research, and High-Contrast Accessibility).

This directory and its sibling asset directories are pre-wired to accept custom graphics designed in **Canva**, Figma, Adobe Illustrator, or Inkscape:
- `public/assets/covers/` — Course domain headers and unit strip headers.
- `public/assets/branding/` — Institutional seals, crests, and emblems.
- `public/assets/diagrams/` — Circuit schematics, block diagrams, and timing wave charts.
- `public/assets/posters/` — High-resolution formula posters and curriculum roadmap infographics.
- `public/assets/presentations/` — 16:9 lecture presentation slide deck templates.

---

## 2. Dimensional & Technical Specifications

| Asset Type | Target Directory | Canvas Dimensions | Aspect Ratio | Formats | Max File Size | Safe Margin |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Course & Unit Covers** | `public/assets/covers/` | `1200 × 400 px` | 3:1 | SVG (preferred), WebP | `< 15 KB` (SVG) / `< 60 KB` (WebP) | 48px on all edges |
| **Formula & Tech Posters** | `public/assets/posters/` | `1200 × 900 px` or `1200 × 1600 px` | 4:3 or 3:4 | SVG (preferred), WebP | `< 15 KB` (SVG) / `< 75 KB` (WebP) | 40px all margins |
| **Lecture Slide Decks** | `public/assets/presentations/` | `1200 × 675 px` or `1920 × 1080 px` | 16:9 | SVG (preferred), WebP | `< 15 KB` (SVG) / `< 80 KB` (WebP) | 48px horizontal |
| **Subject Emblems** | `public/assets/branding/` | `512 × 512 px` | 1:1 | SVG (transparent) | `< 10 KB` | 32px circular zone |
| **IEEE Schematic Diagrams** | `public/assets/diagrams/` | `800 × 500 px` | 16:10 | SVG (IEEE Std 315) | `< 20 KB` | 24px around text |

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

## 4. Pre-Wired Asset Drop-In Map

### A. Course Covers (`public/assets/covers/`)
- `cover_signals_dsp.svg`
- `cover_analog_devices.svg`
- `cover_digital_vlsi.svg`
- `cover_comm_rf.svg`
- `cover_embedded_iot.svg`
- `cover_control_em.svg`

### B. Posters & Roadmap Infographics (`public/assets/posters/`)
- `ece_formula_master_poster.svg` — Master formula sheet across all core ECE disciplines.
- `stm32_architecture_roadmap.svg` — 21-chapter embedded systems & RTOS roadmap.

### C. Lecture Presentations (`public/assets/presentations/`)
- `ece_dsp_spectral_lecture_deck.svg` — 16:9 OBE lecture slide deck presentation.

---

## 5. How to Export from Canva

1. Create a custom design in Canva:
   - For Covers: `1200` wide by `400` tall (px).
   - For Posters: `1200` wide by `900` tall (px).
   - For Slides: `1200` wide by `675` tall (px).
   - For Emblems: `512` wide by `512` tall (px).
2. Choose **Share** $\to$ **Download**.
3. Select **SVG** as file type (with *Transparent Background* for emblems).
4. Save the file into the corresponding folder listed above.
5. Verify in browser or run `npm run build` to ensure instant visual updates.
