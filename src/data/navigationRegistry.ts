/**
 * ========================================================================================
 * VoltCore Apex Academia - Unified 14-Category Navigation & Route Registry
 * Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
 * Platform Lead: Ashok Kumar A (2023MITEC042)
 *
 * Comprehensive index of all 86 application routes grouped into 14 sovereign categories.
 * Provides instant lookups for Topbar navigation, Course Sidebar, Breadcrumbs, and ⌘K Search.
 * ========================================================================================
 */

export interface NavItem {
  path: string;
  title: string;
  shortTitle: string;
  categoryId: string;
  categoryName: string;
  categoryIcon: string;
  icon: string;
  badge?: string;
  badgeColor?: string;
  description: string;
  keywords: string[];
  roleRequired?: 'Admin_Owner' | 'Teacher' | 'Student';
  isExternal?: boolean;
}

export interface NavCategory {
  id: string;
  number: string;
  name: string;
  icon: string;
  description: string;
  items: NavItem[];
}

export const NAVIGATION_CATEGORIES: NavCategory[] = [
  {
    id: "my-learning",
    number: "01",
    name: "My Learning",
    icon: "📊",
    description: "Personalized student trajectory, pomodoro focus, and attendance logs.",
    items: [
      {
        path: "/learning-dashboard",
        title: "Student Learning Dashboard & Adaptive Path",
        shortTitle: "Dashboard",
        categoryId: "my-learning",
        categoryName: "My Learning",
        categoryIcon: "📊",
        icon: "🎓",
        badge: "Phase A",
        badgeColor: "#00F0B5",
        description: "5 ECE domain mastery meters, prerequisite DAG, and cognitive gap detection.",
        keywords: ["learning", "dashboard", "gpa", "cgpa", "mastery", "prerequisites", "dag", "cognitive"]
      },
      {
        path: "/learning-productivity",
        title: "Learning Productivity & Focus Studio",
        shortTitle: "Productivity",
        categoryId: "my-learning",
        categoryName: "My Learning",
        categoryIcon: "📊",
        icon: "⏱️",
        badge: "Focus",
        badgeColor: "#38BDF8",
        description: "Pomodoro timer, technical focus tracker, and spaced revision scheduler.",
        keywords: ["pomodoro", "timer", "focus", "productivity", "study plan", "habits"]
      },
      {
        path: "/flashcards",
        title: "SM-2 Spaced Repetition ECE Flashcards",
        shortTitle: "Flashcards",
        categoryId: "my-learning",
        categoryName: "My Learning",
        categoryIcon: "📊",
        icon: "🃏",
        badge: "SM-2",
        badgeColor: "#F59E0B",
        description: "ARM registers, RISC-V hazards, and Nyquist criteria active recall cards.",
        keywords: ["flashcards", "spaced repetition", "sm2", "recall", "registers", "opcodes"]
      },
      {
        path: "/attendance",
        title: "Hardware RFID Attendance Scan Log",
        shortTitle: "Attendance",
        categoryId: "my-learning",
        categoryName: "My Learning",
        categoryIcon: "📊",
        icon: "📡",
        badge: "RFID",
        badgeColor: "#10B981",
        description: "ESP32 Lab 304 real-time scan verification and attendance percentage tracker.",
        keywords: ["attendance", "rfid", "esp32", "lab 304", "scans", "75% rule"]
      }
    ]
  },
  {
    id: "course-library",
    number: "02",
    name: "Course Library",
    icon: "📚",
    description: "Curated curriculum catalog, Anna University formulas, and academic calendar.",
    items: [
      {
        path: "/course-hub",
        title: "Modular Course Shell Hub (4 Priority Courses)",
        shortTitle: "Course Hub",
        categoryId: "course-library",
        categoryName: "Course Library",
        categoryIcon: "📚",
        icon: "🏛️",
        badge: "Interactive Lab",
        badgeColor: "#00F0B5",
        description: "Python DSP, Semiconductor Devices, Optical Comm, and Embedded Systems.",
        keywords: ["course hub", "syllabus", "ec23s01", "ec23c03", "ec23e04", "ec8702", "units"]
      },
      {
        path: "/ece-knowledge",
        title: "ECE Formulas & Technical Encyclopedia",
        shortTitle: "Encyclopedia",
        categoryId: "course-library",
        categoryName: "Course Library",
        categoryIcon: "📚",
        icon: "📐",
        badge: "Reference",
        badgeColor: "#6366F1",
        description: "Derivations, circuit laws, semiconductor parameters, and communication formulas.",
        keywords: ["formulas", "encyclopedia", "equations", "katex", "semiconductors", "derivations"]
      },
      {
        path: "/academic-hub",
        title: "Academic Management & Calendar Hub",
        shortTitle: "Academic Hub",
        categoryId: "course-library",
        categoryName: "Course Library",
        categoryIcon: "📚",
        icon: "📅",
        badge: "Schedule",
        badgeColor: "#A855F7",
        description: "Internal assessment timelines, semester schedules, and syllabus status.",
        keywords: ["calendar", "timetable", "schedule", "academic", "deadlines", "internal exams"]
      }
    ]
  },
  {
    id: "semester-courses",
    number: "03",
    name: "Semester Courses",
    icon: "⚡",
    description: "Core curriculum subjects: Digital, Analog, Signals, Embedded, and IoT.",
    items: [
      {
        path: "/digital-logic",
        title: "Digital Logic & 4-Variable K-Map Studio",
        shortTitle: "Digital Logic",
        categoryId: "semester-courses",
        categoryName: "Semester Courses",
        categoryIcon: "⚡",
        icon: "🎛️",
        badge: "EC3352",
        badgeColor: "#06B6D4",
        description: "74HC logic gates, Quine-McCluskey minimization, and two's complement arithmetic.",
        keywords: ["digital logic", "k-map", "karnaugh", "quine mccluskey", "ec3352", "truth table"]
      },
      {
        path: "/digital-electronics",
        title: "Digital Systems Design & Circuit Solvers",
        shortTitle: "Digital Systems",
        categoryId: "semester-courses",
        categoryName: "Semester Courses",
        categoryIcon: "⚡",
        icon: "⚡",
        badge: "Solvers",
        badgeColor: "#00F0B5",
        description: "Number systems, adders, multiplexers, and safe boolean expression evaluation.",
        keywords: ["digital electronics", "adders", "multiplexers", "gray code", "excess-3", "conversions"]
      },
      {
        path: "/analog-electronics",
        title: "Analog Electronics & Semiconductor Physics",
        shortTitle: "Analog Electronics",
        categoryId: "semester-courses",
        categoryName: "Semester Courses",
        categoryIcon: "⚡",
        icon: "🔬",
        badge: "Circuits",
        badgeColor: "#F59E0B",
        description: "BJT small-signal models, MOSFET IV curves, and active op-amp topologies.",
        keywords: ["analog", "bjt", "mosfet", "opamp", "small signal", "diodes", "filters"]
      },
      {
        path: "/analog-communication",
        title: "Analog & Communication Systems",
        shortTitle: "Analog Comm",
        categoryId: "semester-courses",
        categoryName: "Semester Courses",
        categoryIcon: "⚡",
        icon: "📻",
        badge: "EC3451",
        badgeColor: "#84A950",
        description: "AM, FM, superheterodyne receivers, noise figure, and SNR derivations.",
        keywords: ["communication", "am", "fm", "modulation", "noise figure", "snr", "ec3451"]
      },
      {
        path: "/signals-communication",
        title: "Signals & Digital Communication Systems",
        shortTitle: "Signals & Systems",
        categoryId: "semester-courses",
        categoryName: "Semester Courses",
        categoryIcon: "⚡",
        icon: "📡",
        badge: "DSP",
        badgeColor: "#6366F1",
        description: "Continuous and discrete convolution, Fourier transform, and Nyquist sampling.",
        keywords: ["signals", "convolution", "fft", "dft", "nyquist", "aliasing", "fourier"]
      },
      {
        path: "/embedded-systems",
        title: "Embedded Systems & ARM Cortex-M Hub",
        shortTitle: "Embedded Systems",
        categoryId: "semester-courses",
        categoryName: "Semester Courses",
        categoryIcon: "⚡",
        icon: "💽",
        badge: "Embedded",
        badgeColor: "#00D8F6",
        description: "ARM Cortex-M4 registers, NVIC interrupt grouping, and peripheral memory mapping.",
        keywords: ["embedded", "arm", "cortex-m", "nvic", "registers", "dma", "ec8702"]
      },
      {
        path: "/embedded-systems/stm32-academy",
        title: "Bare-Metal STM32 Academy (21 Chapters)",
        shortTitle: "STM32 Academy",
        categoryId: "semester-courses",
        categoryName: "Semester Courses",
        categoryIcon: "⚡",
        icon: "🦾",
        badge: "21 Chapters",
        badgeColor: "#10B981",
        description: "From ARM startup and vector table to FreeRTOS, TinyML, and low-power modes.",
        keywords: ["stm32", "bare metal", "arm", "freertos", "tinyml", "registers", "cortex-m4"]
      },
      {
        path: "/stm32-academy",
        title: "STM32 Academy (Canonical Alias)",
        shortTitle: "STM32 Alias",
        categoryId: "semester-courses",
        categoryName: "Semester Courses",
        categoryIcon: "⚡",
        icon: "⏩",
        badge: "301 Redirect",
        badgeColor: "#00F0B5",
        description: "Fast redirect bridge to the 21-chapter bare-metal STM32 Academy syllabus.",
        keywords: ["stm32-academy", "alias", "redirect"]
      },
      {
        path: "/iot-connected-systems",
        title: "IoT & Connected Systems Hub",
        shortTitle: "IoT Systems",
        categoryId: "semester-courses",
        categoryName: "Semester Courses",
        categoryIcon: "⚡",
        icon: "🌐",
        badge: "IoT",
        badgeColor: "#14B8A6",
        description: "5-layer IoT architecture, MQTT 3.1.1 protocol, and edge gateway telemetry.",
        keywords: ["iot", "connected", "mqtt", "gateway", "sensors", "architecture"]
      }
    ]
  },
  {
    id: "unit-wise-notes",
    number: "04",
    name: "Unit-wise Notes",
    icon: "📝",
    description: "Curated lecture notes and derivations for Units I to V across all subjects.",
    items: [
      {
        path: "/textbook-library?tab=notes",
        title: "Unit-Wise Lecture Notes & Study Guides",
        shortTitle: "Lecture Notes",
        categoryId: "unit-wise-notes",
        categoryName: "Unit-wise Notes",
        categoryIcon: "📝",
        icon: "📑",
        badge: "Units I-V",
        badgeColor: "#F59E0B",
        description: "Comprehensive notes with KaTeX equations, circuit figures, and exam tips.",
        keywords: ["notes", "lecture notes", "units", "unit 1", "unit 2", "unit 3", "unit 4", "unit 5"]
      },
      {
        path: "/course-hub",
        title: "Unit-Wise Lesson Reader (Flagship Courses)",
        shortTitle: "Lesson Reader",
        categoryId: "unit-wise-notes",
        categoryName: "Unit-wise Notes",
        categoryIcon: "📝",
        icon: "📖",
        badge: "Interactive",
        badgeColor: "#00F0B5",
        description: "Structured 15-lesson reader for Digital Signal Processing and priority courses.",
        keywords: ["lesson reader", "ec23s01", "python dsp", "markdown notes", "formula cards"]
      }
    ]
  },
  {
    id: "video-lectures",
    number: "05",
    name: "Video Lectures",
    icon: "🎥",
    description: "NPTEL IIT video lectures synchronized with Anna University syllabus units.",
    items: [
      {
        path: "/nptel-player",
        title: "Smart NPTEL MOOC Lecture Player",
        shortTitle: "NPTEL Player",
        categoryId: "video-lectures",
        categoryName: "Video Lectures",
        categoryIcon: "🎥",
        icon: "▶️",
        badge: "15s Sync",
        badgeColor: "#F59E0B",
        description: "IIT video playback, speed control (0.5x–2.0x), key concepts, and markdown notes.",
        keywords: ["nptel", "player", "video", "iit", "youtube", "mooc", "timestamps", "lectures"]
      },
      {
        path: "/nptel",
        title: "NPTEL IIT Curriculum Video Mapper",
        shortTitle: "Video Mapper",
        categoryId: "video-lectures",
        categoryName: "Video Lectures",
        categoryIcon: "🎥",
        icon: "🗺️",
        badge: "9 Modules",
        badgeColor: "#00F0B5",
        description: "Unit-mapped playlists from IIT Kharagpur, IIT Madras, and IIT Bombay.",
        keywords: ["nptel mapper", "iit kharagpur", "iit madras", "mooc syllabus", "video links"]
      }
    ]
  },
  {
    id: "digital-library",
    number: "06",
    name: "Digital Library",
    icon: "🏛️",
    description: "Standard ECE textbooks, manufacturer datasheets, and scientific math studio.",
    items: [
      {
        path: "/textbook-library",
        title: "ECE Textbook Reader & Datasheet Library",
        shortTitle: "Textbooks",
        categoryId: "digital-library",
        categoryName: "Digital Library",
        categoryIcon: "🏛️",
        icon: "📕",
        badge: "Datasheets",
        badgeColor: "#F59E0B",
        description: "Sedra & Smith, Oppenheim, Yiu, STM32 datasheets, and silicon errata sheets.",
        keywords: ["textbooks", "library", "datasheets", "sedra smith", "oppenheim", "pdf reader"]
      },
      {
        path: "/math-studio",
        title: "Mathematical Formulation & SPICE Studio",
        shortTitle: "Math Studio",
        categoryId: "digital-library",
        categoryName: "Digital Library",
        categoryIcon: "🏛️",
        icon: "🧮",
        badge: "KaTeX",
        badgeColor: "#6366F1",
        description: "Interactive KaTeX formula editor, matrix algebra, and circuit transfer functions.",
        keywords: ["math", "latex", "katex", "matrix", "formulas", "spice math"]
      }
    ]
  },
  {
    id: "practice-assessment",
    number: "07",
    name: "Practice & Assessment",
    icon: "🎯",
    description: "GATE ECE exam preparation, autograders, and AI viva-voce simulators.",
    items: [
      {
        path: "/gate-ece",
        title: "2,000+ GATE ECE Question Bank & Solvers",
        shortTitle: "GATE Bank",
        categoryId: "practice-assessment",
        categoryName: "Practice & Assessment",
        categoryIcon: "🎯",
        icon: "🏆",
        badge: "2,000+ MCQs",
        badgeColor: "#F59E0B",
        description: "Topic-wise past papers, numerical answer type (NAT), and stepwise derivations.",
        keywords: ["gate", "gate ece", "mcqs", "nat", "question bank", "past papers", "exam prep"]
      },
      {
        path: "/exam-center",
        title: "GATE ECE Timed Examination Simulator",
        shortTitle: "Exam Simulator",
        categoryId: "practice-assessment",
        categoryName: "Practice & Assessment",
        categoryIcon: "🎯",
        icon: "⏳",
        badge: "Virtual Hall",
        badgeColor: "#EF4444",
        description: "Official GATE interface, countdown timer, negative marking, and virtual calculator.",
        keywords: ["exam", "test simulator", "timed hall", "negative marking", "mock test"]
      },
      {
        path: "/autograder",
        title: "Wokwi Firmware AutoGrader & AST Evaluator",
        shortTitle: "AutoGrader",
        categoryId: "practice-assessment",
        categoryName: "Practice & Assessment",
        categoryIcon: "🎯",
        icon: "🤖",
        badge: "AST Checks",
        badgeColor: "#00F0B5",
        description: "Automated firmware test benches, register verification, and timing checks.",
        keywords: ["autograder", "grading", "tests", "ast", "c++ testbench", "wokwi grader"]
      },
      {
        path: "/viva-voce",
        title: "AI Viva-Voce Simulator & Defense Hub",
        shortTitle: "Viva Simulator",
        categoryId: "practice-assessment",
        categoryName: "Practice & Assessment",
        categoryIcon: "🎯",
        icon: "🎙️",
        badge: "Oral Defense",
        badgeColor: "#38BDF8",
        description: "Interactive oral viva defense for Lab 304, mini-projects, and capstone reviews.",
        keywords: ["viva", "oral exam", "defense", "questions", "interview", "external examiner"]
      }
    ]
  },
  {
    id: "engineering-laboratories",
    number: "08",
    name: "Engineering Laboratories",
    icon: "🔬",
    description: "Virtual test benches, hardware bridges, SPICE, Wokwi, and oscilloscope tools.",
    items: [
      {
        path: "/simulation",
        title: "Hardware & SPICE Simulation Deck",
        shortTitle: "Simulation Lab",
        categoryId: "engineering-laboratories",
        categoryName: "Engineering Laboratories",
        categoryIcon: "🔬",
        icon: "🎛️",
        badge: "SPICE",
        badgeColor: "#00F0B5",
        description: "Zero-latency analog transient, AC analysis, and digital circuit simulation.",
        keywords: ["simulation", "spice", "ltspice", "circuits", "transient", "ac analysis"]
      },
      {
        path: "/virtual-bench",
        title: "Keysight DSOX1204G Virtual Oscilloscope",
        shortTitle: "Oscilloscope",
        categoryId: "engineering-laboratories",
        categoryName: "Engineering Laboratories",
        categoryIcon: "🔬",
        icon: "📈",
        badge: "DSO 4-Ch",
        badgeColor: "#06B6D4",
        description: "4-channel virtual digital storage oscilloscope with FFT spectral analysis.",
        keywords: ["oscilloscope", "dso", "virtual bench", "fft", "keysight", "waveform", "probes"]
      },
      {
        path: "/hardware-hil",
        title: "Hardware-in-the-Loop (HIL) Test Bench",
        shortTitle: "Hardware HIL",
        categoryId: "engineering-laboratories",
        categoryName: "Engineering Laboratories",
        categoryIcon: "🔬",
        icon: "🔌",
        badge: "HIL v2",
        badgeColor: "#A855F7",
        description: "Real-time stimulus generation and loopback validation for physical MCUs.",
        keywords: ["hil", "hardware in the loop", "real time", "stimulus", "test bench", "can bus"]
      },
      {
        path: "/physical-lab",
        title: "Physical Lab Automation & WebSerial Bridge",
        shortTitle: "Physical Lab",
        categoryId: "engineering-laboratories",
        categoryName: "Engineering Laboratories",
        categoryIcon: "🔬",
        icon: "🧪",
        badge: "WebSerial",
        badgeColor: "#10B981",
        description: "Direct browser-to-hardware COM port serial bridge and lab bench instrumentation.",
        keywords: ["physical lab", "serial", "webserial", "com port", "baud", "uart bridge"]
      },
      {
        path: "/iot-lab",
        title: "IoT Smart Lab 304 Station",
        shortTitle: "IoT Lab 304",
        categoryId: "engineering-laboratories",
        categoryName: "Engineering Laboratories",
        categoryIcon: "🔬",
        icon: "🏢",
        badge: "Station 304",
        badgeColor: "#00F0B5",
        description: "ESP32 physical station telemetry, environmental sensor hubs, and bench locks.",
        keywords: ["iot lab", "lab 304", "station", "esp32", "mit campus", "sensors"]
      },
      {
        path: "/smart-lab",
        title: "Smart Laboratory Telemetry Hub",
        shortTitle: "Smart Lab",
        categoryId: "engineering-laboratories",
        categoryName: "Engineering Laboratories",
        categoryIcon: "🔬",
        icon: "💡",
        badge: "Telemetry",
        badgeColor: "#14B8A6",
        description: "Real-time bench occupancy, power profiling, and environmental telemetry.",
        keywords: ["smart lab", "occupancy", "power profiling", "bench monitor"]
      },
      {
        path: "/voice-lab",
        title: "Voice Hands-Free Lab Assistant",
        shortTitle: "Voice Lab",
        categoryId: "engineering-laboratories",
        categoryName: "Engineering Laboratories",
        categoryIcon: "🔬",
        icon: "🗣️",
        badge: "Voice AI",
        badgeColor: "#F59E0B",
        description: "Hands-free voice commands for DSO adjustments, pinout lookups, and timer logs.",
        keywords: ["voice", "hands free", "speech", "lab assistant", "microphone"]
      },
      {
        path: "/flash-firmware",
        title: "WebUSB Microcontroller Firmware Flasher",
        shortTitle: "Firmware Flasher",
        categoryId: "engineering-laboratories",
        categoryName: "Engineering Laboratories",
        categoryIcon: "🔬",
        icon: "⚡",
        badge: "WebUSB",
        badgeColor: "#00F0B5",
        description: "Flash compiled .bin/.hex firmware directly to ESP32 and STM32 from browser.",
        keywords: ["flasher", "webusb", "firmware", "burn hex", "esp32 flash", "dfu"]
      },
      {
        path: "/component-inspector",
        title: "Smart Component & PCB Inspector",
        shortTitle: "PCB Inspector",
        categoryId: "engineering-laboratories",
        categoryName: "Engineering Laboratories",
        categoryIcon: "🔬",
        icon: "🔍",
        badge: "SMD/PCB",
        badgeColor: "#38BDF8",
        description: "SMD component packaging, resistor color bands, and IC pinout locator.",
        keywords: ["component", "pcb", "inspector", "resistor color", "smd", "pinout"]
      },
      {
        path: "/fleet",
        title: "IoT Edge Fleet Manager",
        shortTitle: "Fleet Manager",
        categoryId: "engineering-laboratories",
        categoryName: "Engineering Laboratories",
        categoryIcon: "🔬",
        icon: "🛰️",
        badge: "LittleFS",
        badgeColor: "#6366F1",
        description: "OTA firmware updates, LittleFS filesystem inspections, and device health.",
        keywords: ["fleet", "ota", "devices", "littlefs", "edge nodes", "firmware update"]
      }
    ]
  },
  {
    id: "ai-learning-assistant",
    number: "09",
    name: "AI Learning Assistant",
    icon: "🧠",
    description: "Gemini AI multimodal tutor, syllabus explainers, and digital twins.",
    items: [
      {
        path: "/ai-assisted-learning",
        title: "AI-Assisted Learning & Viva Mentor Hub",
        shortTitle: "AI Mentor",
        categoryId: "ai-learning-assistant",
        categoryName: "AI Learning Assistant",
        categoryIcon: "🧠",
        icon: "💡",
        badge: "Gemini 2.0",
        badgeColor: "#38BDF8",
        description: "Curriculum-aligned AI mentor, stepwise derivations, and code explanation.",
        keywords: ["ai", "mentor", "gemini", "tutor", "explainer", "rag", "viva assistant"]
      },
      {
        path: "/next-gen",
        title: "Next-Gen Innovations & Silicon Digital Twin",
        shortTitle: "Digital Twin",
        categoryId: "ai-learning-assistant",
        categoryName: "AI Learning Assistant",
        categoryIcon: "🧠",
        icon: "🧬",
        badge: "Digital Twin",
        badgeColor: "#D946EF",
        description: "Autonomous silicon twin modeling, neuromorphic compute, and edge generative AI.",
        keywords: ["next-gen", "digital twin", "neuromorphic", "ai twin", "future tech"]
      }
    ]
  },
  {
    id: "projects-portfolio",
    number: "10",
    name: "Projects & Portfolio",
    icon: "🛠️",
    description: "Anna University EC3711 mini-projects, capstone portfolios, and BOM costing.",
    items: [
      {
        path: "/student-projects",
        title: "Student Projects & Engineering Portfolios",
        shortTitle: "Student Projects",
        categoryId: "projects-portfolio",
        categoryName: "Projects & Portfolio",
        categoryIcon: "🛠️",
        icon: "💼",
        badge: "EC3711",
        badgeColor: "#00F0B5",
        description: "Milestone reviews, project idea generator, proposal templates, and BOM calculator.",
        keywords: ["projects", "ec3711", "mini project", "capstone", "portfolio", "bom", "proposals"]
      },
      {
        path: "/project-innovation",
        title: "Project Innovation & Patent Incubator",
        shortTitle: "Project Incubator",
        categoryId: "projects-portfolio",
        categoryName: "Projects & Portfolio",
        categoryIcon: "🛠️",
        icon: "🚀",
        badge: "Incubator",
        badgeColor: "#F59E0B",
        description: "Hardware prototyping pipelines, patent checklists, and institutional competitions.",
        keywords: ["innovation", "patents", "incubator", "prototyping", "hackathons"]
      },
      {
        path: "/collaboration",
        title: "Student Portfolio Showcase & Team Hub",
        shortTitle: "Portfolio Hub",
        categoryId: "projects-portfolio",
        categoryName: "Projects & Portfolio",
        categoryIcon: "🛠️",
        icon: "👥",
        badge: "Showcase",
        badgeColor: "#06B6D4",
        description: "Peer project showcases, verified credentials, and team collaboration decks.",
        keywords: ["collaboration", "showcase", "peer review", "teams", "credentials"]
      }
    ]
  },
  {
    id: "research-resources",
    number: "11",
    name: "Research Resources",
    icon: "💡",
    description: "IEEE Xplore discovery, BibTeX reference manager, and Q1 journal pipelines.",
    items: [
      {
        path: "/research-innovation",
        title: "Research Discovery & IEEE Capstones",
        shortTitle: "Research Discovery",
        categoryId: "research-resources",
        categoryName: "Research Resources",
        categoryIcon: "💡",
        icon: "🔬",
        badge: "IEEE Xplore",
        badgeColor: "#10B981",
        description: "6G, terahertz electronics, neuromorphic circuits, and literature review tool.",
        keywords: ["research", "ieee", "xplore", "citations", "bibtex", "literature review", "6g"]
      },
      {
        path: "/research",
        title: "IEEE Transactions Journal Workspace",
        shortTitle: "IEEE Workspace",
        categoryId: "research-resources",
        categoryName: "Research Resources",
        categoryIcon: "💡",
        icon: "📜",
        badge: "Q1 Pipeline",
        badgeColor: "#38BDF8",
        description: "Standard IEEE two-column paper template, DOI metadata, and peer review guidelines.",
        keywords: ["ieee template", "journal", "q1", "paper writing", "transactions", "doi"]
      }
    ]
  },
  {
    id: "google-drive-resources",
    number: "12",
    name: "Google Drive Resources",
    icon: "📁",
    description: "Institutional cloud repositories, verified datasheet vaults, and lab manuals.",
    items: [
      {
        path: "/course-hub#drive-vault",
        title: "Institutional ECE Datasheet & Lab Manual Vault",
        shortTitle: "Datasheet Vault",
        categoryId: "google-drive-resources",
        categoryName: "Google Drive Resources",
        categoryIcon: "📁",
        icon: "☁️",
        badge: "Drive Mount",
        badgeColor: "#00F0B5",
        description: "Official Anna University laboratory manuals, schematic diagrams, and components.",
        keywords: ["google drive", "drive", "cloud", "lab manuals", "datasheet vault", "pdf"]
      },
      {
        path: "/textbook-library#institutional-drive",
        title: "Anna University MIT Campus Cloud Course Archives",
        shortTitle: "Course Archives",
        categoryId: "google-drive-resources",
        categoryName: "Google Drive Resources",
        categoryIcon: "📁",
        icon: "📂",
        badge: "Verified AU",
        badgeColor: "#F59E0B",
        description: "Regulation 2023 syllabus archives, question papers, and past solutions.",
        keywords: ["archives", "drive links", "past question papers", "mit campus drive", "au reg 2023"]
      }
    ]
  },
  {
    id: "my-notes-bookmarks",
    number: "13",
    name: "My Notes & Bookmarks",
    icon: "🔖",
    description: "Persistent student bookmarks, KaTeX annotations, and personal study notes.",
    items: [
      {
        path: "/course-hub#bookmarks",
        title: "Bookmarked Lessons & Saved Derivations",
        shortTitle: "Bookmarks",
        categoryId: "my-notes-bookmarks",
        categoryName: "My Notes & Bookmarks",
        categoryIcon: "🔖",
        icon: "⭐",
        badge: "Local Sync",
        badgeColor: "#F59E0B",
        description: "Saved lesson topics, starred KaTeX formulas, and pinned simulator presets.",
        keywords: ["bookmarks", "saved", "favorites", "starred", "pinned formulas"]
      },
      {
        path: "/textbook-library#my-notes",
        title: "Student Textbook Margin Notes & Highlights",
        shortTitle: "Margin Notes",
        categoryId: "my-notes-bookmarks",
        categoryName: "My Notes & Bookmarks",
        categoryIcon: "🔖",
        icon: "✍️",
        badge: "Annotations",
        badgeColor: "#00F0B5",
        description: "In-line marginal notes, technical memos, and personal study annotations.",
        keywords: ["notes", "my notes", "annotations", "margin notes", "highlights"]
      }
    ]
  },
  {
    id: "profile-settings",
    number: "14",
    name: "Profile & Settings",
    icon: "⚙️",
    description: "Account profiles, studio frame configuration, governance, and administration.",
    items: [
      {
        path: "/profile",
        title: "Academic Transcript & Scholar Identity",
        shortTitle: "Profile",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "👤",
        badge: "2023MITEC042",
        badgeColor: "#00F0B5",
        description: "RFID token E2 80 6F 3B, academic credits, earned XP, and skill badges.",
        keywords: ["profile", "transcript", "ashok kumar", "roll no", "rfid", "xp", "badges"]
      },
      {
        path: "/settings",
        title: "System Settings & Theme Configuration",
        shortTitle: "Settings",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "⚙️",
        badge: "18 Themes",
        badgeColor: "#38BDF8",
        description: "18-color theme manager, hardware baud rates, and cache options.",
        keywords: ["settings", "themes", "config", "baud rate", "telemetry settings", "sync"]
      },
      {
        path: "/workspace",
        title: "Resizable Studio & 18 Vibrant Themes Workspace",
        shortTitle: "Studio Workspace",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "🖥️",
        badge: "Studio",
        badgeColor: "#00F0B5",
        description: "4-frame modular engineering workspace: Video, Simulator, Editor, and Notes.",
        keywords: ["workspace", "studio", "multi-frame", "resizable", "18 themes", "palette"]
      },
      {
        path: "/login",
        title: "Multi-Role Institutional IAM Authentication",
        shortTitle: "Sign In / Switch Role",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "🔐",
        badge: "IAM SSO",
        badgeColor: "#10B981",
        description: "Role presets for Student (2023MITEC042), Faculty, Lab Instructor, and Dean.",
        keywords: ["login", "auth", "sso", "roles", "switch user", "student", "faculty", "dean"]
      },
      {
        path: "/careers",
        title: "ECE Career Pathways & Regulation 2023 Tracks",
        shortTitle: "Career Pathways",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "🧭",
        badge: "Tracks",
        badgeColor: "#00F0B5",
        description: "Embedded Software, VLSI Design, RF Systems, and Robotics career roadmaps.",
        keywords: ["careers", "pathways", "embedded engineer", "vlsi engineer", "r2023"]
      },
      {
        path: "/career-professional",
        title: "Career & Professional Development Center",
        shortTitle: "Professional Dev",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "💼",
        badge: "Interviews",
        badgeColor: "#14B8A6",
        description: "Technical interview question banks, Day-0 placement prep, and resume rubrics.",
        keywords: ["placements", "interviews", "professional", "resume", "day-0"]
      },
      {
        path: "/collaboration-community",
        title: "Collaboration & Department Community",
        shortTitle: "Community",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "💬",
        badge: "Forums",
        badgeColor: "#06B6D4",
        description: "Student peer forums, study cohorts, and regulation 2023 academic discussions.",
        keywords: ["community", "discussion", "forums", "cohorts", "questions"]
      },
      {
        path: "/accessibility",
        title: "Accessibility & Inclusive Engineering Hub",
        shortTitle: "Accessibility",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "♿",
        badge: "தமிழ் / WCAG",
        badgeColor: "#00F0B5",
        description: "Tamil-English bilingual terms, high-contrast modes, and screen reader labels.",
        keywords: ["accessibility", "tamil", "wcag", "screen reader", "inclusive", "contrast"]
      },
      {
        path: "/accessibility-multilingual",
        title: "Multilingual ECE Lexicon & Accessible Tools",
        shortTitle: "Multilingual",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "🌐",
        badge: "Bilingual",
        badgeColor: "#10B981",
        description: "Standardized Tamil technical vocabulary for electronics engineering concepts.",
        keywords: ["multilingual", "tamil dictionary", "lexicon", "accessible math"]
      },
      {
        path: "/enterprise-admin",
        title: "Enterprise Administration & NBA/NAAC Hub",
        shortTitle: "Enterprise Admin",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "⚖️",
        badge: "Dean / Admin",
        badgeColor: "#A855F7",
        roleRequired: "Admin_Owner",
        description: "Accreditation attainments, PO1-PO12 aggregation, and cryptographic audit logs.",
        keywords: ["enterprise", "admin", "dean", "nba", "naac", "accreditation", "audit", "attainment"]
      },
      {
        path: "/faculty-workspace",
        title: "Faculty & Department Productivity Workspace",
        shortTitle: "Faculty Workspace",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "🏛️",
        badge: "Faculty",
        badgeColor: "#14B8A6",
        roleRequired: "Teacher",
        description: "Lecture planning (Units I-V), continuous assessments, and Council Minutes.",
        keywords: ["faculty", "professor", "curriculum", "lecture planner", "cat 1", "cat 2", "mom"]
      },
      {
        path: "/faculty-admin",
        title: "Faculty & Administrative Management Hub",
        shortTitle: "Faculty Admin",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "📋",
        badge: "Management",
        badgeColor: "#38BDF8",
        roleRequired: "Teacher",
        description: "Teaching loads, student grade dossiers, and master department schedule.",
        keywords: ["faculty admin", "teaching load", "grades", "master schedule", "students"]
      },
      {
        path: "/teacher",
        title: "Teacher Analytics & Outcome Assessment",
        shortTitle: "Teacher Analytics",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "📊",
        badge: "Analytics",
        badgeColor: "#06B6D4",
        roleRequired: "Teacher",
        description: "Real-time class grade distributions, at-risk alerts, and outcome compliance.",
        keywords: ["teacher", "analytics", "class performance", "outcomes", "at risk"]
      },
      {
        path: "/accreditation-compliance",
        title: "Accreditation & NBA/NAAC Statutory Hub",
        shortTitle: "Accreditation",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "🏅",
        badge: "NBA Tier-1",
        badgeColor: "#10B981",
        description: "Course outcome (CO1-CO5) and program outcome (PO1-PO12) mapping matrix.",
        keywords: ["nba", "naac", "co po mapping", "compliance", "sar", "cqi"]
      },
      {
        path: "/security-hub",
        title: "Security Hardening & SOC Management",
        shortTitle: "Security Hub",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "🛡️",
        badge: "SOC",
        badgeColor: "#EF4444",
        description: "MFA tokens, PBKDF2 iterations, access logs, and security diagnostics.",
        keywords: ["security", "mfa", "pbkdf2", "hash", "soc", "tokens"]
      },
      {
        path: "/security-integrity",
        title: "System Integrity, Cryptography & RBAC",
        shortTitle: "System Integrity",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "🔒",
        badge: "SHA-256",
        badgeColor: "#10B981",
        description: "Cryptographic WAL hashes, authorization matrices, and lead developer signature.",
        keywords: ["integrity", "cryptography", "sha256", "rbac", "authorizations"]
      },
      {
        path: "/performance-optimization",
        title: "Performance Optimization & APM Hub",
        shortTitle: "Performance",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "⚡",
        badge: "Sub-3ms",
        badgeColor: "#00F0B5",
        description: "Sub-3ms SQLite queries, asset bundle stats, and lazy hydration profiles.",
        keywords: ["performance", "caching", "apm", "latency", "sqlite speed", "bundle"]
      },
      {
        path: "/system-health",
        title: "Platform Health & SRE Telemetry Hub",
        shortTitle: "Platform Health",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "🩺",
        badge: "SRE",
        badgeColor: "#38BDF8",
        description: "Server uptime, database connection pool, and client latency telemetry.",
        keywords: ["health", "sre", "uptime", "telemetry", "status", "server"]
      },
      {
        path: "/system-health-integration",
        title: "System Health & CI/CD Integration Hub",
        shortTitle: "CI/CD Health",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "🛠️",
        badge: "CI/CD",
        badgeColor: "#6366F1",
        description: "Automated regression test metrics (1108 tests), git build status, and linting.",
        keywords: ["cicd", "tests", "pytest", "regression", "build health", "git"]
      },
      {
        path: "/data-intelligence",
        title: "Data Intelligence & Curriculum QA Hub",
        shortTitle: "Data QA",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "📈",
        badge: "AU QA",
        badgeColor: "#F59E0B",
        description: "Content QA validator reports, syllabus coverage metrics, and gap audits.",
        keywords: ["data intelligence", "qa", "validator", "content coverage", "audit"]
      },
      {
        path: "/telemetry",
        title: "Real-Time SSE Telemetry Stream",
        shortTitle: "Live Telemetry",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "📡",
        badge: "SSE Stream",
        badgeColor: "#00F0B5",
        description: "Server-Sent Events streaming live ESP32 voltage, temperature, and packet rates.",
        keywords: ["telemetry", "sse", "live stream", "packets", "esp32 stream", "voltage"]
      },
      {
        path: "/cloud-deploy",
        title: "Cloud Staging & Deployment Hub",
        shortTitle: "Cloud Staging",
        categoryId: "profile-settings",
        categoryName: "Profile & Settings",
        categoryIcon: "⚙️",
        icon: "☁️",
        badge: "Staging",
        badgeColor: "#38BDF8",
        description: "Static generation stats, preview servers, and sovereign deployment scripts.",
        keywords: ["cloud", "deploy", "staging", "docker", "hosting", "dist"]
      }
    ]
  }
];

// Flat list of all items for fast search and lookup
export const ALL_NAV_ITEMS: NavItem[] = NAVIGATION_CATEGORIES.flatMap((c) => c.items);

/**
 * Derives the active category and nav item for a given URL pathname.
 */
export function getBreadcrumbs(pathname: string): { category: NavCategory; item: NavItem } | null {
  if (!pathname || pathname === '/') return null;

  // Clean pathname trailing slash
  const cleanPath = pathname.endsWith('/') && pathname.length > 1 ? pathname.slice(0, -1) : pathname;

  // Exact match first
  for (const cat of NAVIGATION_CATEGORIES) {
    for (const it of cat.items) {
      if (it.path === cleanPath) {
        return { category: cat, item: it };
      }
    }
  }

  // Prefix match for nested routes (e.g., STM32 academy chapters)
  for (const cat of NAVIGATION_CATEGORIES) {
    for (const it of cat.items) {
      if (it.path !== '/' && cleanPath.startsWith(it.path)) {
        return { category: cat, item: it };
      }
    }
  }

  return null;
}

/**
 * Instant fuzzy / keyword search over all categories, routes, ECE codes, and tools.
 */
export function searchNavItems(query: string, maxResults: number = 8): NavItem[] {
  const q = (query || '').trim().toLowerCase();
  if (!q) {
    // Return curated flagship items by default
    return ALL_NAV_ITEMS.slice(0, maxResults);
  }

  const scored = ALL_NAV_ITEMS.map((item) => {
    let score = 0;
    const titleLower = item.title.toLowerCase();
    const shortLower = item.shortTitle.toLowerCase();
    const pathLower = item.path.toLowerCase();
    const descLower = item.description.toLowerCase();
    const catLower = item.categoryName.toLowerCase();

    if (titleLower === q || shortLower === q) score += 100;
    else if (titleLower.startsWith(q)) score += 50;
    else if (titleLower.includes(q)) score += 30;

    if (pathLower.includes(q)) score += 25;
    if (catLower.includes(q)) score += 20;
    if (descLower.includes(q)) score += 15;

    for (const kw of item.keywords) {
      if (kw === q) score += 40;
      else if (kw.includes(q)) score += 20;
    }

    return { item, score };
  });

  return scored
    .filter((s) => s.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, maxResults)
    .map((s) => s.item);
}
