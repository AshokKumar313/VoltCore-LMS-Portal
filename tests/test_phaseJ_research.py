"""
========================================================================================
VoltCore Apex Academia - Phase J Unit Test Suite (Features 301–310)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
========================================================================================
"""

import os
import sqlite3
import pytest
from backend.research_innovation_engine import (
    RESEARCH_FRONTIERS,
    register_research_paper,
    get_research_paper,
    generate_citation_formats,
    generate_literature_review_matrix,
    track_research_gap,
    log_research_idea,
    register_patent_reference,
    map_credit_collaborators,
    track_publication_pipeline,
    init_research_db
)

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_research_innovation.db")

@pytest.fixture(autouse=True)
def clean_test_db():
    """Ensure clean isolated SQLite test database."""
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
    init_research_db(TEST_DB_PATH)
    yield
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass

# Feature 302: Research Frontiers Catalog
def test_research_frontiers_catalog():
    assert "6g_sub_thz_ris" in RESEARCH_FRONTIERS
    assert "neuromorphic_memristor" in RESEARCH_FRONTIERS
    assert "gan_power_converters" in RESEARCH_FRONTIERS
    assert "riscv_edge_accelerators" in RESEARCH_FRONTIERS
    assert "silicon_photonics" in RESEARCH_FRONTIERS

    ris = RESEARCH_FRONTIERS["6g_sub_thz_ris"]
    assert "100 GHz" in ris["target_frequencies"]
    assert len(ris["open_challenges"]) >= 2
    assert "Vector Network Analyzer" in ris["mit_apparatus_needed"]

# Feature 301 & 303: Research Paper Repository & Tagging
def test_register_and_get_research_paper():
    paper_id = "IEEE-2024-RISC"
    title = "Energy-Efficient Neuromorphic SNN Accelerator on 28nm FD-SOI"
    authors = "Kumar, A., Ramanathan, S., & Sridhar, V."
    year = 2024
    journal = "IEEE Journal of Solid-State Circuits"
    abstract = "A sub-milliwatt event-driven spiking neural network processor with 1024 memristive crossbar neurons."
    domain = "VLSI"
    tags = ["Memristor", "SNN", "28nm", "In-Memory Computing", "FD-SOI"]
    annotations = [
        {"section": "Architecture", "note": "Uses 1T1R crossbar cell to suppress sneak path leakage.", "highlight": "1T1R"}
    ]

    reg_res = register_research_paper(
        paper_id=paper_id,
        title=title,
        authors=authors,
        year=year,
        journal_or_conf=journal,
        abstract=abstract,
        domain=domain,
        tags=tags,
        doi="10.1109/JSSC.2024.1234567",
        trl_level=4,
        annotations=annotations,
        db_path=TEST_DB_PATH
    )
    assert reg_res["status"] == "success"
    assert reg_res["paper_id"] == paper_id

    # Retrieve paper
    paper = get_research_paper(paper_id, db_path=TEST_DB_PATH)
    assert paper is not None
    assert paper["title"] == title
    assert paper["year"] == 2024
    assert len(paper["tags"]) == 5
    assert len(paper["annotations"]) == 1
    assert "1T1R" in paper["annotations"][0]["note"]

# Feature 304: Citation Format Assistant
def test_generate_citation_formats():
    cites = generate_citation_formats(
        title="Sub-Terahertz Reconfigurable Intelligent Surfaces for 6G Wireless Backhaul",
        authors="Ashok Kumar, A. and Ramanathan, S.",
        year=2024,
        journal_or_conf="IEEE Transactions on Wireless Communications",
        volume="23",
        issue="4",
        pages="2150-2165",
        doi="10.1109/TWC.2024.9876543"
    )
    # Check BibTeX
    assert "@article{" in cites["bibtex"]
    assert "journal   = {IEEE Transactions on Wireless Communications}" in cites["bibtex"]
    assert "doi       = {10.1109/TWC.2024.9876543}" in cites["bibtex"]

    # Check IEEE style
    assert 'Ashok Kumar, A. and Ramanathan, S., "Sub-Terahertz Reconfigurable Intelligent Surfaces' in cites["ieee"]
    assert "vol. 23, no. 4, pp. 2150-2165, 2024" in cites["ieee"]

    # Check APA style
    assert "Ashok Kumar, A. and Ramanathan, S. (2024)." in cites["apa"]
    assert "https://doi.org/10.1109/TWC.2024.9876543" in cites["apa"]

    # Check Harvard & Chicago
    assert "Harvard" in cites or len(cites["harvard"]) > 10
    assert "Chicago" in cites or len(cites["chicago"]) > 10

# Feature 305: Literature Review Organizer
def test_generate_literature_review_matrix():
    papers = [
        {
            "paper_id": "PAP-01",
            "title": "GaN Resonant Converter at 5 MHz",
            "authors": "Zhang et al.",
            "year": 2023,
            "methodology": "Zero-Voltage Switching (ZVS) Half-Bridge",
            "strengths": "97.8% peak efficiency, 45 W/in3 power density",
            "limitations": "Gate driver ringing under high dV/dt",
            "metrics": "Efficiency 97.8%, Freq 5 MHz"
        },
        {
            "paper_id": "PAP-02",
            "title": "SiC Multi-level Inverter for Traction",
            "authors": "Schmidt & Muller",
            "year": 2024,
            "methodology": "3-Level Neutral Point Clamped",
            "strengths": "1200V blocking voltage, low THD",
            "limitations": "High thermal heatsink requirement",
            "metrics": "THD < 1.5%, Power 50 kW"
        }
    ]
    res = generate_literature_review_matrix(
        topic_title="Wide-Bandgap Semiconductor Power Systems",
        papers=papers,
        student_id="2023MITEC042",
        db_path=TEST_DB_PATH
    )
    assert res["status"] == "success"
    assert res["paper_count"] == 2
    assert "REV-" in res["review_id"]
    assert res["matrix"][0]["paper_id"] == "PAP-01"

# Feature 306: Research Gap Tracking
def test_track_research_gap():
    res = track_research_gap(
        domain="Edge AI & TinyML",
        gap_statement="Unsupervised continuous learning on battery-less microcontrollers without catastrophic forgetting.",
        sota_limitation="Current TinyML algorithms require full offline backpropagation and multi-megabyte weight storage.",
        proposed_attack_vector="Sparse episodic memory replay combined with quantized low-rank adaptation (QLoRA) on RISC-V scratchpad SRAM.",
        student_id="2023MITEC042",
        db_path=TEST_DB_PATH
    )
    assert res["status"] == "success"
    assert "GAP-" in res["gap_id"]
    assert res["tracking_status"] == "OPEN"
    assert "TinyML" in res["domain"]

# Feature 307: Research Idea Notebook
def test_log_research_idea():
    res = log_research_idea(
        title="Adaptive Sub-Threshold Body-Biased Low-Noise Amplifier for Wearable ECG",
        hypothesis="Dynamic substrate forward-biasing will lower noise figure to <1.8 dB while consuming <50 uW from 0.5V rail.",
        apparatus_needed="Cadence Virtuoso IC618, TSMC 65nm PDK, Agilent Noise Figure Meter",
        feasibility_score=9.0,
        student_id="2023MITEC042",
        db_path=TEST_DB_PATH
    )
    assert res["status"] == "success"
    assert "IDEA-" in res["idea_id"]
    assert res["feasibility_score"] == 9.0
    assert "Cadence Virtuoso" in res["apparatus_needed"]

# Feature 308: Patent Reference Organizer
def test_register_patent_reference():
    res = register_patent_reference(
        patent_number="US11234567B2",
        title="Apparatus and Method for Beam-Squint Compensation in Wideband Phased Arrays",
        assignee="Qualcomm Incorporated",
        cpc_class="H01Q 3/26, H04B 7/06",
        independent_claim_summary="True-time-delay (TTD) active phase shifting matrix combined with baseband frequency-domain pre-equalization.",
        prior_art_relation="Differentiates over narrow-band phase shifters by eliminating beam deflection across wide multi-gigahertz channels.",
        db_path=TEST_DB_PATH
    )
    assert res["status"] == "success"
    assert res["patent_number"] == "US11234567B2"
    assert "Qualcomm" in res["assignee"]
    assert "H01Q" in res["cpc_class"]

# Feature 309: Collaboration Workspace (CRediT Taxonomy)
def test_map_credit_collaborators():
    collaborators = [
        {
            "name": "Ashok Kumar A",
            "roll_no": "2023MITEC042",
            "affiliation": "MIT Campus, Anna University",
            "roles": ["conceptualization", "methodology", "writing_original"]
        },
        {
            "name": "Dr. Ramanathan",
            "roll_no": "FACULTY-ECE",
            "affiliation": "MIT Campus, Anna University",
            "roles": ["formal_analysis", "validation", "writing_review_editing"]
        }
    ]
    res = map_credit_collaborators("6G Sub-THz Metasurface System", collaborators)
    assert res["status"] == "success"
    assert res["total_collaborators"] == 2
    assert "conceptualization" in res["collaborator_roster"][0]["roles"]
    assert "CASRAI" in res["credit_taxonomy_standard"]

# Feature 310: Publication Progress Tracker
def test_track_publication_pipeline():
    res = track_publication_pipeline(
        manuscript_title="Energy-Efficient Neuromorphic In-Memory Accelerator for Ultra-Low Power Edge Vision",
        target_journal="IEEE Transactions on Very Large Scale Integration (VLSI) Systems",
        quartile="Q1",
        status="UNDER_PEER_REVIEW",
        impact_factor=2.8,
        deadline_date="2026-12-15",
        student_id="2023MITEC042",
        db_path=TEST_DB_PATH
    )
    assert res["status"] == "success"
    assert "PUB-" in res["pipeline_id"]
    assert res["quartile"] == "Q1"
    assert res["lifecycle_stage"] == "UNDER_PEER_REVIEW"
    assert res["impact_factor"] == 2.8

# SQLite WAL Mode Persistence Test
def test_research_sqlite_wal_persistence():
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    assert "research_papers_v2" in tables
    assert "literature_reviews" in tables
    assert "research_gaps" in tables
    assert "research_ideas" in tables
    assert "patent_references" in tables
    assert "publication_pipeline" in tables
    conn.close()
