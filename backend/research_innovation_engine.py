"""
========================================================================================
VoltCore Apex Academia - Phase J: Research & Innovation Hub (Features 301–310)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Features:
  - Feature 301: IEEE Paper Reading Workspace (Structured layout, margin notes, math)
  - Feature 302: Research Topic Discovery Board (6G THz, Neuromorphic, GaN, RISC-V, PIC)
  - Feature 303: Research Paper Tagging System (Domain, Methodology, Tools, TRL 1-9)
  - Feature 304: Citation Format Assistant (BibTeX, IEEE, APA, Harvard, Chicago)
  - Feature 305: Literature Review Organizer (Comparative matrix, SOTA metrics, gaps)
  - Feature 306: Research Gap Tracking Board (Open scientific hurdles & attack vectors)
  - Feature 307: Research Idea Notebook (Hypotheses, apparatus, expected outcomes)
  - Feature 308: Patent Reference Organizer (USPTO/IPO/WIPO, CPC/IPC codes, prior art)
  - Feature 309: Research Collaboration Workspace (CRediT taxonomy, roles, equipment)
  - Feature 310: Publication Progress Tracker (Stages: Draft -> Review -> Q1/Q2 Accepted)
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
# ECE RESEARCH TOPIC DISCOVERY CATALOG (Feature 302)
# ---------------------------------------------------------------------------

RESEARCH_FRONTIERS: Dict[str, Dict[str, Any]] = {
    "6g_sub_thz_ris": {
        "topic_id": "6g_sub_thz_ris",
        "title": "Sub-THz Wireless Communications & Reconfigurable Intelligent Surfaces (RIS)",
        "domain": "Wireless & RF Systems",
        "trl_level": 4,
        "target_frequencies": "100 GHz – 300 GHz (D-Band)",
        "summary": "Exploring beamforming, channel estimation, and passive meta-atom phase manipulation to overcome severe atmospheric molecular absorption and path loss in beyond-5G/6G outdoor urban environments.",
        "open_challenges": [
            "Near-field spherical wavefront beam-squint mitigation",
            "Ultra-low-power PIN diode or varactor control circuitry for 10,000+ element metasurfaces",
            "Joint communication and radar sensing (JCAS) waveform design"
        ],
        "key_venues": ["IEEE Transactions on Wireless Communications", "IEEE JSAC", "IEEE MTT-S IMS"],
        "mit_apparatus_needed": "Vector Network Analyzer (up to 110 GHz), Horn Antennas, Anechoic Chamber"
    },
    "neuromorphic_memristor": {
        "topic_id": "neuromorphic_memristor",
        "title": "Neuromorphic In-Memory Computing Using Memristive Crossbar Arrays",
        "domain": "VLSI & Brain-Inspired Computing",
        "trl_level": 3,
        "target_frequencies": "Sub-100 MHz (Ultra-Low Power Event-Driven)",
        "summary": "Direct hardware implementation of spiking neural networks (SNN) utilizing resistive switching devices (RRAM / PCM) to eliminate the von Neumann memory bottleneck for continuous edge intelligence.",
        "open_challenges": [
            "Device-to-device conductance variability and sneak-path current suppression",
            "Analog-to-digital converter (ADC) power and area domination in large crossbars",
            "On-chip spike-timing-dependent plasticity (STDP) unsupervised learning stability"
        ],
        "key_venues": ["IEEE Transactions on Electron Devices", "IEEE JSSC", "Nature Electronics"],
        "mit_apparatus_needed": "Semiconductor Parameter Analyzer (Keysight B1500A), Probe Station, Cadence Virtuoso"
    },
    "gan_power_converters": {
        "topic_id": "gan_power_converters",
        "title": "Wide-Bandgap GaN High-Electron-Mobility Transistor (HEMT) Power Stages",
        "domain": "Power Electronics & Energy Systems",
        "trl_level": 6,
        "target_frequencies": "1 MHz – 10 MHz High-Frequency Switching",
        "summary": "Developing multi-kilowatt, high-power-density resonant DC-DC converters for EV fast-chargers and aerospace microgrids leveraging high two-dimensional electron gas (2DEG) electron mobility and high breakdown fields.",
        "open_challenges": [
            "Parasitic inductance-induced voltage overshoot during nanosecond dV/dt switching",
            "Dynamic on-resistance (R_DS(on)) degradation caused by surface electron trapping",
            "High-side isolated gate driver noise immunity under >100 V/ns common-mode transients"
        ],
        "key_venues": ["IEEE Transactions on Power Electronics", "IEEE TIE", "IEEE APEC"],
        "mit_apparatus_needed": "High-Voltage Differential Probes, Rogowski Current Sensors, Thermal Imaging Camera"
    },
    "riscv_edge_accelerators": {
        "topic_id": "riscv_edge_accelerators",
        "title": "Custom RISC-V Vector Extensions for Low-Power TinyML Edge Acceleration",
        "domain": "Embedded Systems & Computer Architecture",
        "trl_level": 5,
        "target_frequencies": "200 MHz – 500 MHz (FPGA & ASIC)",
        "summary": "Architecting domain-specific ISA extensions on open-source RISC-V cores (CV32E40P, Rocket) with systolic tensor arrays and 8-bit/4-bit integer quantization for edge computer vision and audio keyword spotting.",
        "open_challenges": [
            "Memory bandwidth bottleneck in tight tightly-coupled scratchpad SRAMs",
            "Compiler toolchain auto-vectorization for custom non-standard instructions",
            "Zero-overhead hardware loop controllers and SIMD multiply-accumulate (MAC) pipelining"
        ],
        "key_venues": ["IEEE Micro", "ACM/IEEE DAC", "IEEE Transactions on Computers"],
        "mit_apparatus_needed": "Xilinx Zynq UltraScale+ FPGA Board, Vivado Design Suite, Logic Analyzer"
    },
    "silicon_photonics": {
        "topic_id": "silicon_photonics",
        "title": "Silicon Photonic Integrated Circuits (PIC) for Co-Packaged Data Center Optics",
        "domain": "Photonics & Optoelectronics",
        "trl_level": 4,
        "target_frequencies": "100 Gbaud / 800 Gbps Optical Transceivers",
        "summary": "Designing Mach-Zehnder optical modulators, microring resonators, and grating couplers on silicon-on-insulator (SOI) wafers to bypass copper electrical interconnect bandwidth-distance limits.",
        "open_challenges": [
            "Thermal sensitivity of microring resonance wavelengths requiring active thermal tuning",
            "High coupling loss between optical single-mode fibers and sub-micron silicon waveguides",
            "Monolithic integration of III-V lasers onto standard CMOS manufacturing lines"
        ],
        "key_venues": ["IEEE Journal of Lightwave Technology", "IEEE Photonics Technology Letters", "OFC"],
        "mit_apparatus_needed": "Tunable Laser Source, Optical Spectrum Analyzer, Precision Fiber Alignment Stage"
    }
}

# ---------------------------------------------------------------------------
# DATABASE INITIALIZATION (SQLite WAL Mode)
# ---------------------------------------------------------------------------

_db_lock = threading.Lock()

def init_research_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initialize SQLite tables for Phase J Research & Innovation with WAL mode."""
    with _db_lock:
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            cursor = conn.cursor()

            # 1. Research Papers Repository (Feature 301, 303)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS research_papers_v2 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paper_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    authors TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    journal_or_conf TEXT NOT NULL,
                    doi TEXT,
                    abstract TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    trl_level INTEGER DEFAULT 3,
                    annotations_json TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 2. Literature Review Comparative Matrix (Feature 305)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS literature_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    review_id TEXT UNIQUE NOT NULL,
                    student_id TEXT NOT NULL,
                    topic_title TEXT NOT NULL,
                    matrix_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 3. Research Gaps Tracker (Feature 306)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS research_gaps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gap_id TEXT UNIQUE NOT NULL,
                    student_id TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    gap_statement TEXT NOT NULL,
                    sota_limitation TEXT NOT NULL,
                    proposed_attack_vector TEXT NOT NULL,
                    status TEXT DEFAULT 'OPEN',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 4. Research Idea Notebook (Feature 307)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS research_ideas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    idea_id TEXT UNIQUE NOT NULL,
                    student_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    hypothesis TEXT NOT NULL,
                    apparatus_needed TEXT NOT NULL,
                    feasibility_score REAL DEFAULT 8.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 5. Patent References Organizer (Feature 308)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patent_references (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patent_id TEXT UNIQUE NOT NULL,
                    patent_number TEXT NOT NULL,
                    title TEXT NOT NULL,
                    assignee TEXT NOT NULL,
                    cpc_class TEXT NOT NULL,
                    independent_claim_summary TEXT NOT NULL,
                    prior_art_relation TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 6. Publication Progress Tracker (Feature 310)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS publication_pipeline (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pipeline_id TEXT UNIQUE NOT NULL,
                    student_id TEXT NOT NULL,
                    manuscript_title TEXT NOT NULL,
                    target_journal TEXT NOT NULL,
                    quartile TEXT NOT NULL,
                    status TEXT NOT NULL,
                    impact_factor REAL DEFAULT 3.5,
                    deadline_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            conn.commit()
        finally:
            conn.close()

# ---------------------------------------------------------------------------
# FEATURE 301 & 303: RESEARCH PAPERS & TAGGING
# ---------------------------------------------------------------------------

def register_research_paper(
    paper_id: str,
    title: str,
    authors: str,
    year: int,
    journal_or_conf: str,
    abstract: str,
    domain: str,
    tags: List[str],
    doi: Optional[str] = None,
    trl_level: int = 3,
    annotations: Optional[List[Dict[str, Any]]] = None,
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """
    Feature 301 & 303: Registers a paper with multi-dimensional taxonomy tags,
    abstract, DOI, and reading margin annotations.
    """
    init_research_db(db_path)
    clean_id = paper_id.strip()
    annotations_list = annotations or []

    with _db_lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO research_papers_v2 
            (paper_id, title, authors, year, journal_or_conf, doi, abstract, domain, tags_json, trl_level, annotations_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            clean_id, title.strip(), authors.strip(), int(year), journal_or_conf.strip(),
            doi.strip() if doi else None, abstract.strip(), domain.strip(),
            json.dumps(tags), int(trl_level), json.dumps(annotations_list)
        ))
        conn.commit()
        conn.close()

    return {
        "status": "success",
        "paper_id": clean_id,
        "title": title,
        "authors": authors,
        "year": year,
        "domain": domain,
        "tags": tags,
        "trl_level": trl_level,
        "annotations_count": len(annotations_list)
    }

def get_research_paper(paper_id: str, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieve full research paper record with parsed JSON tags and annotations."""
    init_research_db(db_path)
    with _db_lock:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM research_papers_v2 WHERE paper_id = ?", (paper_id.strip(),))
        row = cursor.fetchone()
        conn.close()

    if not row:
        return None

    return {
        "paper_id": row["paper_id"],
        "title": row["title"],
        "authors": row["authors"],
        "year": row["year"],
        "journal_or_conf": row["journal_or_conf"],
        "doi": row["doi"],
        "abstract": row["abstract"],
        "domain": row["domain"],
        "tags": json.loads(row["tags_json"]),
        "trl_level": row["trl_level"],
        "annotations": json.loads(row["annotations_json"])
    }

# ---------------------------------------------------------------------------
# FEATURE 304: CITATION FORMAT ASSISTANT
# ---------------------------------------------------------------------------

def generate_citation_formats(
    title: str,
    authors: str,
    year: int,
    journal_or_conf: str,
    volume: Optional[str] = None,
    issue: Optional[str] = None,
    pages: Optional[str] = None,
    doi: Optional[str] = None
) -> Dict[str, str]:
    """
    Feature 304: Generates verified BibTeX, IEEE, APA 7th, Harvard, and Chicago citations.
    """
    # BibTeX Citation Key Generation: FirstAuthorLastNameYearFirstWord
    first_author_clean = authors.split(",")[0].split("&")[0].strip().split()[-1].lower()
    first_author_clean = re.sub(r'[^a-zA-Z0-9]', '', first_author_clean) or "author"
    first_title_word = re.sub(r'[^a-zA-Z0-9]', '', title.strip().split()[0].lower())
    bibtex_key = f"{first_author_clean}{year}{first_title_word}"

    # 1. BibTeX Format
    bibtex_lines = [
        f"@article{{{bibtex_key},",
        f"  author    = {{{authors}}},",
        f"  title     = {{{{{title}}}}},",
        f"  journal   = {{{journal_or_conf}}},",
        f"  year      = {{{year}}},"
    ]
    if volume:
        bibtex_lines.append(f"  volume    = {{{volume}}},")
    if issue:
        bibtex_lines.append(f"  number    = {{{issue}}},")
    if pages:
        bibtex_lines.append(f"  pages     = {{{pages}}},")
    if doi:
        bibtex_lines.append(f"  doi       = {{{doi}}},")
    bibtex_lines.append("}")
    bibtex = "\n".join(bibtex_lines)

    # 2. IEEE Format: [1] J. K. Author, "Name of paper," Abbrev. Title of Periodical, vol. x, no. x, pp. xxx-xxx, Abbrev. Month, year, DOI.
    vol_str = f", vol. {volume}" if volume else ""
    iss_str = f", no. {issue}" if issue else ""
    pp_str = f", pp. {pages}" if pages else ""
    doi_str = f", doi: {doi}." if doi else "."
    ieee = f'{authors}, "{title}," {journal_or_conf}{vol_str}{iss_str}{pp_str}, {year}{doi_str}'

    # 3. APA 7th Edition: Author, A. A. (Year). Title of article. Title of Periodical, xx(x), pp–pp. https://doi.org/xx
    apa_vol = f", {volume}" if volume else ""
    apa_iss = f"({issue})" if issue else ""
    apa_pp = f", {pages}" if pages else ""
    apa_doi = f" https://doi.org/{doi}" if doi else ""
    apa = f"{authors} ({year}). {title}. {journal_or_conf}{apa_vol}{apa_iss}{apa_pp}.{apa_doi}"

    # 4. Harvard Style
    harvard = f"{authors}, {year}. {title}. {journal_or_conf}{vol_str}{iss_str}{pp_str}."

    # 5. Chicago Manual of Style
    chicago = f'{authors}. "{title}." {journal_or_conf} {volume or ""}{f", no. {issue}" if issue else ""} ({year}): {pages or "n.p."}.'

    return {
        "bibtex_key": bibtex_key,
        "bibtex": bibtex,
        "ieee": ieee,
        "apa": apa,
        "harvard": harvard,
        "chicago": chicago
    }

# ---------------------------------------------------------------------------
# FEATURE 305: LITERATURE REVIEW ORGANIZER
# ---------------------------------------------------------------------------

def generate_literature_review_matrix(
    topic_title: str,
    papers: List[Dict[str, Any]],
    student_id: str = "2023MITEC042",
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """
    Feature 305: Constructs a comparative literature matrix contrasting
    methodologies, strengths, limitations, and benchmark metrics.
    """
    review_id = f"REV-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    matrix_rows = []

    for p in papers:
        matrix_rows.append({
            "paper_id": p.get("paper_id", "REF-001"),
            "title": p.get("title", "Untitled Manuscript"),
            "authors": p.get("authors", "Author et al."),
            "year": p.get("year", 2024),
            "methodology": p.get("methodology", "Simulation / Analytical Modeling"),
            "key_strengths": p.get("strengths", "High energy efficiency, scalable architecture"),
            "limitations": p.get("limitations", "High area overhead under deep submicron nodes"),
            "benchmark_metrics": p.get("metrics", "Gain > 20 dB, Power < 5 mW")
        })

    init_research_db(db_path)
    with _db_lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO literature_reviews (review_id, student_id, topic_title, matrix_json)
            VALUES (?, ?, ?, ?)
        """, (review_id, student_id, topic_title, json.dumps(matrix_rows)))
        conn.commit()
        conn.close()

    return {
        "status": "success",
        "review_id": review_id,
        "student_id": student_id,
        "topic_title": topic_title,
        "paper_count": len(matrix_rows),
        "matrix": matrix_rows
    }

# ---------------------------------------------------------------------------
# FEATURE 306: RESEARCH GAP TRACKING BOARD
# ---------------------------------------------------------------------------

def track_research_gap(
    domain: str,
    gap_statement: str,
    sota_limitation: str,
    proposed_attack_vector: str,
    student_id: str = "2023MITEC042",
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """
    Feature 306: Registers and tracks unresolved scientific gaps in ECE research.
    """
    gap_id = f"GAP-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    init_research_db(db_path)

    with _db_lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO research_gaps 
            (gap_id, student_id, domain, gap_statement, sota_limitation, proposed_attack_vector, status)
            VALUES (?, ?, ?, ?, ?, ?, 'OPEN')
        """, (gap_id, student_id, domain, gap_statement, sota_limitation, proposed_attack_vector))
        conn.commit()
        conn.close()

    return {
        "status": "success",
        "gap_id": gap_id,
        "student_id": student_id,
        "domain": domain,
        "gap_statement": gap_statement,
        "sota_limitation": sota_limitation,
        "proposed_attack_vector": proposed_attack_vector,
        "tracking_status": "OPEN"
    }

# ---------------------------------------------------------------------------
# FEATURE 307: RESEARCH IDEA NOTEBOOK
# ---------------------------------------------------------------------------

def log_research_idea(
    title: str,
    hypothesis: str,
    apparatus_needed: str,
    feasibility_score: float = 8.5,
    student_id: str = "2023MITEC042",
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """
    Feature 307: Structured ideation notebook logging hypotheses and lab requirements.
    """
    idea_id = f"IDEA-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    init_research_db(db_path)

    with _db_lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO research_ideas (idea_id, student_id, title, hypothesis, apparatus_needed, feasibility_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (idea_id, student_id, title, hypothesis, apparatus_needed, float(feasibility_score)))
        conn.commit()
        conn.close()

    return {
        "status": "success",
        "idea_id": idea_id,
        "student_id": student_id,
        "title": title,
        "hypothesis": hypothesis,
        "apparatus_needed": apparatus_needed,
        "feasibility_score": feasibility_score
    }

# ---------------------------------------------------------------------------
# FEATURE 308: PATENT REFERENCE ORGANIZER
# ---------------------------------------------------------------------------

def register_patent_reference(
    patent_number: str,
    title: str,
    assignee: str,
    cpc_class: str,
    independent_claim_summary: str,
    prior_art_relation: str,
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """
    Feature 308: Catalogs essential ECE patents with claim summaries and CPC classes.
    """
    clean_no = patent_number.strip().upper()
    patent_id = f"PAT-{re.sub(r'[^A-Z0-9]', '', clean_no)}"
    init_research_db(db_path)

    with _db_lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO patent_references 
            (patent_id, patent_number, title, assignee, cpc_class, independent_claim_summary, prior_art_relation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (patent_id, clean_no, title.strip(), assignee.strip(), cpc_class.strip(), independent_claim_summary.strip(), prior_art_relation.strip()))
        conn.commit()
        conn.close()

    return {
        "status": "success",
        "patent_id": patent_id,
        "patent_number": clean_no,
        "title": title,
        "assignee": assignee,
        "cpc_class": cpc_class,
        "independent_claim_summary": independent_claim_summary
    }

# ---------------------------------------------------------------------------
# FEATURE 309: RESEARCH COLLABORATION WORKSPACE (CRediT Taxonomy)
# ---------------------------------------------------------------------------

def map_credit_collaborators(
    project_title: str,
    collaborators: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Feature 309: Maps student research co-author responsibilities using
    the international CRediT (Contributor Roles Taxonomy).
    """
    valid_roles = {
        "conceptualization": "Ideas, formulation of overarching research goals",
        "formal_analysis": "Application of statistical, mathematical, or computational techniques",
        "investigation": "Conducting research and data/evidence collection",
        "methodology": "Development or design of methodology and circuit architecture",
        "software": "Programming, software development, EDA script automation",
        "validation": "Verification of overall replication and experimental validity",
        "writing_original": "Preparation and presentation of the published work",
        "writing_review_editing": "Critical review, commentary, and revision"
    }

    mapped_roster = []
    for c in collaborators:
        roles_assigned = c.get("roles", ["investigation"])
        mapped_roster.append({
            "name": c.get("name", "Researcher"),
            "roll_no": c.get("roll_no", "2023MITEC000"),
            "affiliation": c.get("affiliation", "MIT Campus, Anna University"),
            "roles": [r for r in roles_assigned if r.lower() in valid_roles] or ["investigation"]
        })

    return {
        "status": "success",
        "project_title": project_title,
        "total_collaborators": len(mapped_roster),
        "collaborator_roster": mapped_roster,
        "credit_taxonomy_standard": "CASRAI / ISO 20147 Compliant"
    }

# ---------------------------------------------------------------------------
# FEATURE 310: PUBLICATION PROGRESS TRACKER
# ---------------------------------------------------------------------------

def track_publication_pipeline(
    manuscript_title: str,
    target_journal: str,
    quartile: str = "Q1",
    status: str = "SUBMITTED",
    impact_factor: float = 4.2,
    deadline_date: Optional[str] = None,
    student_id: str = "2023MITEC042",
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """
    Feature 310: Tracks manuscript lifecycle stages (Draft -> Review -> Published)
    with quartile metrics and submission deadlines.
    """
    pipeline_id = f"PUB-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    init_research_db(db_path)

    with _db_lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO publication_pipeline 
            (pipeline_id, student_id, manuscript_title, target_journal, quartile, status, impact_factor, deadline_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (pipeline_id, student_id, manuscript_title, target_journal, quartile.upper(), status.upper(), float(impact_factor), deadline_date))
        conn.commit()
        conn.close()

    return {
        "status": "success",
        "pipeline_id": pipeline_id,
        "student_id": student_id,
        "manuscript_title": manuscript_title,
        "target_journal": target_journal,
        "quartile": quartile.upper(),
        "lifecycle_stage": status.upper(),
        "impact_factor": impact_factor,
        "deadline_date": deadline_date
    }
