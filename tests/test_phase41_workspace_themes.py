"""
========================================================================================
VoltCore Apex Academia - Phase 41: Multi-Theme & Resizable Workspace Test Suite
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
========================================================================================
"""

import os
import pytest
import sqlite3
import json
from backend.workspace_themes_engine import (
    THEMES_CATALOG,
    COURSE_TRACKS,
    init_workspace_themes_db,
    save_theme_preference,
    get_latest_theme_preference,
    calculate_equal_frame_split,
    save_workspace_snapshot,
    get_latest_workspace_snapshot
)


@pytest.fixture
def temp_db(tmp_path):
    """Provide an isolated temporary SQLite database in WAL mode."""
    db_file = str(tmp_path / "test_workspace_themes.db")
    init_workspace_themes_db(db_file)
    return db_file


def test_eighteen_themes_catalog_completeness():
    """Verify that exactly 18 vibrant, colorful non-black themes exist with required properties."""
    assert len(THEMES_CATALOG) == 18, f"Expected 18 themes, found {len(THEMES_CATALOG)}"

    required_keys = {"id", "name", "category", "badge", "icon", "description", "colors"}
    required_colors = {"primary", "accent", "background", "surface", "card", "border", "text", "textMuted", "glow"}

    theme_ids = set()
    categories = set()

    for theme in THEMES_CATALOG:
        for key in required_keys:
            assert key in theme, f"Theme missing key '{key}': {theme}"

        assert theme["id"] not in theme_ids, f"Duplicate theme ID: {theme['id']}"
        theme_ids.add(theme["id"])
        categories.add(theme["category"])

        for c_key in required_colors:
            assert c_key in theme["colors"], f"Theme '{theme['id']}' missing color '{c_key}'"
            assert isinstance(theme["colors"][c_key], str) and len(theme["colors"][c_key]) > 0

    # Ensure diverse non-black focus categories are present
    assert "Vibrant Neon" in categories
    assert "Sunset Gradient" in categories
    assert "Rich Chromatic" in categories
    assert "Pastel Academy" in categories
    assert "Light Dynamic" in categories
    assert "Multi-Chromatic" in categories


def test_granular_course_tracks_and_sections():
    """Verify the 3 intuitive general tracks and their 7 granular sections."""
    assert len(COURSE_TRACKS) == 3, f"Expected 3 tracks, found {len(COURSE_TRACKS)}"

    track_ids = {t["track_id"] for t in COURSE_TRACKS}
    assert "embedded_systems" in track_ids
    assert "generative_ai" in track_ids
    assert "foundational_fundamentals" in track_ids

    expected_sections = {
        "intro",
        "course_material",
        "daily_quiz",
        "assessments",
        "assignments",
        "mini_projects",
        "major_projects"
    }

    for track in COURSE_TRACKS:
        assert "title" in track and len(track["title"]) > 0
        assert "regulation" in track
        assert len(track["sections"]) == 7, f"Track '{track['track_id']}' does not have 7 sections"

        actual_sections = {s["section_id"] for s in track["sections"]}
        assert actual_sections == expected_sections, f"Track '{track['track_id']}' missing sections"

        for sec in track["sections"]:
            assert "title" in sec and len(sec["title"]) > 0
            assert "summary" in sec and len(sec["summary"]) > 0
            assert "starter_code" in sec and len(sec["starter_code"]) > 0
            assert "circuit_sim" in sec and len(sec["circuit_sim"]) > 0


def test_equal_frame_split_calculation():
    """Verify deterministic dimensions and percentages for equal grid splitting."""
    # 4 Frames (2x2 Equal Grid)
    all_four = {"video": True, "circuit": True, "code": True, "notes": True}
    res4 = calculate_equal_frame_split(all_four)
    assert res4["active_count"] == 4
    assert res4["frame_percentage"] == 25.0
    assert len(res4["per_frame"]) == 4
    for k in all_four:
        assert res4["per_frame"][k] == 25.0

    # 3 Frames (Equal 3-Way Split)
    three_frames = {"video": True, "circuit": True, "code": True, "notes": False}
    res3 = calculate_equal_frame_split(three_frames)
    assert res3["active_count"] == 3
    assert res3["frame_percentage"] == 33.33
    assert "notes" not in res3["per_frame"]

    # 2 Frames (50/50 Equal Split)
    two_frames = {"video": False, "circuit": True, "code": True, "notes": False}
    res2 = calculate_equal_frame_split(two_frames)
    assert res2["active_count"] == 2
    assert res2["frame_percentage"] == 50.0
    assert res2["per_frame"]["circuit"] == 50.0
    assert res2["per_frame"]["code"] == 50.0

    # 1 Frame (100% Full View)
    one_frame = {"video": False, "circuit": False, "code": True, "notes": False}
    res1 = calculate_equal_frame_split(one_frame)
    assert res1["active_count"] == 1
    assert res1["frame_percentage"] == 100.0
    assert res1["per_frame"]["code"] == 100.0

    # 0 Frames
    zero_frame = {"video": False, "circuit": False, "code": False, "notes": False}
    res0 = calculate_equal_frame_split(zero_frame)
    assert res0["active_count"] == 0
    assert res0["frame_percentage"] == 0.0


def test_theme_preference_persistence(temp_db):
    """Verify SQLite WAL persistence and retrieval of theme preferences."""
    # Default fallback
    default_pref = get_latest_theme_preference("2023MITEC042", temp_db)
    assert default_pref["theme_id"] == "cyber-emerald"

    # Save a vibrant theme: Tokyo Neon
    save_res = save_theme_preference("tokyo-neon", "2023MITEC042", temp_db)
    assert save_res["status"] == "success"
    assert save_res["theme_id"] == "tokyo-neon"

    latest = get_latest_theme_preference("2023MITEC042", temp_db)
    assert latest["theme_id"] == "tokyo-neon"
    assert latest["theme_name"] == "Tokyo Cyberpunk Neon"

    # Save another theme: Clean Canvas
    save_res2 = save_theme_preference("clean-canvas", "2023MITEC042", temp_db)
    assert save_res2["status"] == "success"

    latest2 = get_latest_theme_preference("2023MITEC042", temp_db)
    assert latest2["theme_id"] == "clean-canvas"

    # Invalid theme raises ValueError
    with pytest.raises(ValueError):
        save_theme_preference("non_existent_theme", "2023MITEC042", temp_db)


def test_workspace_snapshot_persistence(temp_db):
    """Verify storing and retrieving snapshots of the resizable multi-frame workspace."""
    frames = {"video": True, "circuit": True, "code": True, "notes": True}
    ratios = {"top": 50.0, "bottom": 50.0}

    save_res = save_workspace_snapshot(
        layout_mode="grid",
        frames_visible=frames,
        split_ratio=ratios,
        active_track="embedded_systems",
        active_section="intro",
        student_id="2023MITEC042",
        db_path=temp_db
    )
    assert save_res["status"] == "success"
    assert save_res["layout_mode"] == "grid"

    snapshot = get_latest_workspace_snapshot("2023MITEC042", temp_db)
    assert snapshot is not None
    assert snapshot["layout_mode"] == "grid"
    assert snapshot["frames_visible"] == frames
    assert snapshot["active_track"] == "embedded_systems"
    assert snapshot["active_section"] == "intro"


def test_wal_mode_enabled(temp_db):
    """Verify SQLite database journal mode is WAL."""
    conn = sqlite3.connect(temp_db)
    try:
        cur = conn.execute("PRAGMA journal_mode;")
        mode = cur.fetchone()[0]
        assert mode.lower() == "wal", f"Expected WAL mode, got {mode}"
    finally:
        conn.close()
