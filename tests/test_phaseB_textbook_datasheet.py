"""
========================================================================================
VoltCore Apex Academia - Phase B Test Suite: ECE Textbooks & Datasheets
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU usage.
========================================================================================
"""

import os
import pytest
import sqlite3
from backend.textbook_datasheet_engine import (
    TextbookDatasheetEngine,
    TEXTBOOK_CATALOG,
    DATASHEET_CATALOG,
    DIAGRAM_CATALOG
)


@pytest.fixture
def engine(tmp_path):
    """Instantiate TextbookDatasheetEngine with an isolated temporary SQLite WAL database."""
    db_file = str(tmp_path / "test_textbooks.db")
    return TextbookDatasheetEngine(db_path=db_file)


def test_textbook_engine_wal_mode(engine):
    """Verify that SQLite tables for bookmarks and annotations are initialized in WAL mode."""
    conn = sqlite3.connect(engine.db_path)
    try:
        cur = conn.execute("PRAGMA journal_mode;")
        mode = cur.fetchone()[0]
        assert mode.lower() == "wal", f"Expected WAL mode, got {mode}"

        cur = conn.execute("""
            SELECT name FROM sqlite_master WHERE type='table'
            AND name IN ('textbook_bookmarks', 'textbook_annotations');
        """)
        tables = {row[0] for row in cur.fetchall()}
        assert "textbook_bookmarks" in tables
        assert "textbook_annotations" in tables
    finally:
        conn.close()


def test_get_textbooks_and_chapters(engine):
    """Verify retrieval of curated Anna University ECE textbooks (Feature 211)."""
    books = engine.get_textbooks()
    assert len(books) >= 3

    book_ids = {b["id"] for b in books}
    assert "cortex_m_guide" in book_ids
    assert "sedra_smith_circuits" in book_ids
    assert "tinyml_warden" in book_ids

    cortex = engine.get_textbook_by_id("cortex_m_guide")
    assert cortex is not None
    assert cortex["author"] == "Joseph Yiu"
    assert len(cortex["chapters"]) >= 3

    for ch in cortex["chapters"]:
        assert "id" in ch
        assert "title" in ch
        assert "content_markdown" in ch
        assert len(ch["key_equations"]) > 0


def test_bookmark_management(engine):
    """Verify saving and fetching chapter bookmarks (Feature 212)."""
    # Verify seeded bookmark
    initial_bookmarks = engine.get_bookmarks("2023MITEC042")
    assert len(initial_bookmarks) >= 1

    # Save new bookmark
    res = engine.save_bookmark(
        student_id="2023MITEC042",
        book_id="sedra_smith_circuits",
        chapter_id="ch1_opamp",
        section_title="Miller Compensation Frequency Response",
        page_offset=72
    )
    assert res["status"] == "success"
    assert res["section_title"] == "Miller Compensation Frequency Response"

    updated_bookmarks = engine.get_bookmarks("2023MITEC042")
    assert len(updated_bookmarks) == len(initial_bookmarks) + 1
    titles = [b["section_title"] for b in updated_bookmarks]
    assert "Miller Compensation Frequency Response" in titles


def test_annotation_management(engine):
    """Verify adding inline annotations and color tags (Feature 213)."""
    # Verify seeded annotation
    initial_ann = engine.get_annotations("2023MITEC042")
    assert len(initial_ann) >= 1

    # Save new annotation
    res = engine.save_annotation(
        student_id="2023MITEC042",
        book_id="tinyml_warden",
        chapter_id="ch1_quant",
        selected_quote="Real Value = Scale * (Quantized_Int8 - ZeroPoint)",
        student_note="Important for ESP32-S3 INT8 inference latency derivation.",
        color_tag="Emerald"
    )
    assert res["status"] == "success"
    assert res["color_tag"] == "Emerald"

    ann_list = engine.get_annotations("2023MITEC042", book_id="tinyml_warden")
    assert len(ann_list) == 1
    assert "ESP32-S3" in ann_list[0]["student_note"]

    # Empty quote or note raises ValueError
    with pytest.raises(ValueError):
        engine.save_annotation("2023MITEC042", "tinyml_warden", "ch1_quant", "", "Note", "Yellow")
    with pytest.raises(ValueError):
        engine.save_annotation("2023MITEC042", "tinyml_warden", "ch1_quant", "Quote", "", "Yellow")


def test_datasheet_comparison(engine):
    """Verify microcontroller specification matrix comparisons (Feature 214)."""
    all_datasheets = engine.compare_datasheets([])
    assert len(all_datasheets) == 4

    # Compare specific silicon: ESP32 vs STM32F401
    subset = engine.compare_datasheets(["esp32_wroom_32", "stm32f401re"])
    assert len(subset) == 2
    names = {s["name"] for s in subset}
    assert "Espressif ESP32-WROOM-32" in names
    assert "STMicroelectronics STM32F401RE" in names

    esp32 = next(s for s in subset if s["id"] == "esp32_wroom_32")
    assert esp32["clock_mhz"] == 240
    assert esp32["sram_kb"] == 520
    assert esp32["deep_sleep_ua"] == 5.0


def test_diagram_library_retrieval(engine):
    """Verify technical block & circuit diagram catalog (Feature 215)."""
    diagrams = engine.get_diagram_library()
    assert len(diagrams) >= 4

    diag_ids = {d["id"] for d in diagrams}
    assert "diag_cortex_m4_bus" in diag_ids
    assert "diag_esp32_dual_core" in diag_ids
    assert "diag_opamp_miller" in diag_ids
    assert "diag_tinyml_arena" in diag_ids

    for d in diagrams:
        assert "title" in d
        assert "category" in d
        assert len(d["layers"]) > 0
