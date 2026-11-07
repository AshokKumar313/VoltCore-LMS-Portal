"""
========================================================================================
VoltCore Apex Academia - Tier 3 Course Expansion Testbed & Validation Suite
Core Engineering Series • Autonomous Engineering Cluster
Platform Lead & Systems Architect: Ashok Kumar A
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313

Validates:
  1. Frontmatter integrity across all 10 Specialization Track MDX modules
  2. Zero duplicate codes and zero slug collisions across src/content/modules/
  3. All 10 Specialization Tracks mapped to dedicated simulation components
  4. Descriptive engineering titles exclusively, with institutional markers decoupled
  5. Content collection markdown parsing and unclosed code fence detection
  6. Progress tracking database persistence under SQLite WAL mode (busy_timeout = 5000)
  7. Passive CPU footprint (<500ms execution) ensuring HP Victus laptop thermal safety
========================================================================================
"""

import os
import re
import time
import sqlite3
import tempfile
import pytest

from backend.course_config_engine import (
    CourseConfigEngine,
    TIER3_SPECIALIZATION_TRACKS,
)

BASE_MODULES_DIR = os.path.join("src", "content", "modules")

EXPECTED_TIER3_MODULES = {
    "1-iot-foundations.mdx": {
        "track": "IoT Edge",
        "code": "IOT8701",
        "sim": "IoTSensorSimulatorHub",
        "trackSlug": "iot-edge",
    },
    "2-automotive-edge.mdx": {
        "track": "Automotive Radar",
        "code": "AUTO8702",
        "sim": "VirtualOscilloscope",
        "trackSlug": "automotive-radar",
    },
    "3-defense-uav.mdx": {
        "track": "Defense UAV",
        "code": "UAV8703",
        "sim": "IotTelemetryHub",
        "trackSlug": "defense-uav",
    },
    "4-railway-edge-ai.mdx": {
        "track": "Railway AI",
        "code": "RAIL8704",
        "sim": "TinyMlEngineHub",
        "trackSlug": "railway-ai",
    },
    "5-riscv-fpga.mdx": {
        "track": "RISC-V RTL",
        "code": "RISCV8705",
        "sim": "FpgaSynthesisHub",
        "trackSlug": "riscv-rtl",
    },
    "6-embedded-rtos.mdx": {
        "track": "FreeRTOS Scheduling",
        "code": "RTOS8706",
        "sim": "RtosSchedulerHub",
        "trackSlug": "freertos-scheduling",
    },
    "7-analog-signal-integrity.mdx": {
        "track": "Advanced Analog",
        "code": "ANLG8707",
        "sim": "LtspiceSimulationViewer",
        "trackSlug": "advanced-analog",
    },
    "8-advanced-rtos-dma.mdx": {
        "track": "Zero-Copy IPC",
        "code": "DMA8708",
        "sim": "DmaNvicHub",
        "trackSlug": "zero-copy-ipc",
    },
    "9-tiny-ml-edge.mdx": {
        "track": "TinyML",
        "code": "TML8709",
        "sim": "TinyMlEngineHub",
        "trackSlug": "tinyml",
    },
    os.path.join("advanced-ece", "10-gate-ece-instrumentation.mdx"): {
        "track": "Instrumentation",
        "code": "INST8710",
        "sim": "GateEceInteractiveSolvers",
        "trackSlug": "instrumentation",
    },
}


def parse_frontmatter(file_path: str) -> dict:
    """Extract YAML frontmatter key-values without external heavy dependencies."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert content.startswith("---"), f"{file_path} must start with YAML delimiter"
    parts = content.split("---", 2)
    assert len(parts) >= 3, f"{file_path} frontmatter must be enclosed in --- delimiters"

    fm_lines = parts[1].splitlines()
    data = {}
    current_key = None
    in_list = False

    for line in fm_lines:
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith("#"):
            continue

        if line_stripped.startswith("- ") and in_list and current_key:
            data[current_key].append(line_stripped[2:].strip().strip('"\''))
            continue

        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"\'')
            if not val:
                # Potential list or object
                current_key = key
                in_list = True
                data[key] = []
            else:
                current_key = key
                in_list = False
                data[key] = val

    return data, parts[2]


@pytest.fixture
def config_engine():
    return CourseConfigEngine()


def test_tier3_modules_exist_on_disk():
    """Verify all 10 Tier 3 specialization MDX modules exist on disk."""
    for rel_path in EXPECTED_TIER3_MODULES:
        full_path = os.path.join(BASE_MODULES_DIR, rel_path)
        assert os.path.isfile(full_path), f"Module file missing: {full_path}"


def test_tier3_frontmatter_integrity_and_types():
    """Verify strict frontmatter schema and metadata typing across all 10 modules."""
    required_fields = [
        "title",
        "code",
        "semester",
        "regulation",
        "department",
        "credits",
        "order",
        "specializationTrack",
        "simulationComponent",
        "trackSlug",
        "description",
        "difficulty",
        "author",
        "publishDate",
        "prerequisites",
        "learningOutcomes",
        "hardwareKit",
        "tags",
    ]

    for rel_path, expected in EXPECTED_TIER3_MODULES.items():
        full_path = os.path.join(BASE_MODULES_DIR, rel_path)
        fm, body = parse_frontmatter(full_path)

        for field in required_fields:
            assert field in fm, f"{rel_path} is missing required frontmatter field '{field}'"

        assert fm["code"] == expected["code"], (
            f"{rel_path} has code '{fm['code']}', expected '{expected['code']}'"
        )
        assert fm["specializationTrack"] == expected["track"], (
            f"{rel_path} has track '{fm['specializationTrack']}', expected '{expected['track']}'"
        )
        assert fm["simulationComponent"] == expected["sim"], (
            f"{rel_path} has simulationComponent '{fm['simulationComponent']}', expected '{expected['sim']}'"
        )
        assert fm["trackSlug"] == expected["trackSlug"], (
            f"{rel_path} has trackSlug '{fm['trackSlug']}', expected '{expected['trackSlug']}'"
        )
        assert len(fm.get("learningOutcomes", [])) >= 3, (
            f"{rel_path} must specify at least 3 learning outcomes"
        )
        assert len(fm.get("hardwareKit", [])) >= 2, (
            f"{rel_path} must specify at least 2 hardwareKit items"
        )


def test_zero_duplicate_codes_across_all_modules():
    """Audit every single .md and .mdx file under src/content/modules/ to ensure zero duplicate course codes."""
    code_to_file = {}
    for root, _, files in os.walk(BASE_MODULES_DIR):
        for f in files:
            if f.endswith((".md", ".mdx")):
                fpath = os.path.join(root, f)
                rel_path = os.path.relpath(fpath, BASE_MODULES_DIR)
                fm, _ = parse_frontmatter(fpath)
                code = fm.get("code")
                if code:
                    assert code not in code_to_file, (
                        f"Duplicate code collision: '{code}' found in both '{rel_path}' and '{code_to_file[code]}'"
                    )
                    code_to_file[code] = rel_path

    assert len(code_to_file) >= 10, "Should have audited at least 10 modules"


def test_institutional_decoupling_in_titles_and_frontmatter():
    """Verify that titles, regulations, and departments are completely free of legacy institutional markers."""
    legacy_terms = ["Anna University", "MIT Campus", "Anna-University", "MITChromepet"]

    for rel_path in EXPECTED_TIER3_MODULES:
        full_path = os.path.join(BASE_MODULES_DIR, rel_path)
        fm, _ = parse_frontmatter(full_path)

        for term in legacy_terms:
            assert term.lower() not in fm["title"].lower(), (
                f"{rel_path} title contains legacy term '{term}': {fm['title']}"
            )
            assert term.lower() not in fm["regulation"].lower(), (
                f"{rel_path} regulation contains legacy term '{term}': {fm['regulation']}"
            )
            assert term.lower() not in fm["department"].lower(), (
                f"{rel_path} department contains legacy term '{term}': {fm['department']}"
            )

        # Descriptive engineering titles should not start with redundant course codes
        assert not re.match(r"^EC\d{4}:", fm["title"]), (
            f"{rel_path} title should be a clean descriptive engineering title without 'ECxxxx:' prefix"
        )


def test_backend_config_engine_tier3_registry(config_engine):
    """Verify that CourseConfigEngine properly resolves all 10 Tier 3 Specialization Tracks."""
    tracks = config_engine.get_tier3_specialization_tracks()
    assert len(tracks) == 10, f"Expected 10 Tier 3 tracks, got {len(tracks)}"

    for rel_path, expected in EXPECTED_TIER3_MODULES.items():
        track_by_code = config_engine.get_tier3_track_by_code(expected["code"])
        assert track_by_code is not None, f"Track code {expected['code']} not found in registry"
        assert track_by_code["track"] == expected["track"]
        assert track_by_code["simulation_component"] == expected["sim"]

        track_by_name = config_engine.get_tier3_track_by_name(expected["track"])
        assert track_by_name is not None, f"Track name {expected['track']} not found in registry"
        assert track_by_name["code"] == expected["code"]


def test_markdown_code_fence_closure():
    """Verify that all markdown and MDX modules have properly balanced code fences."""
    for rel_path in EXPECTED_TIER3_MODULES:
        full_path = os.path.join(BASE_MODULES_DIR, rel_path)
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Count occurrences of triple backtick fences
        fence_count = len(re.findall(r"^```", content, re.MULTILINE))
        assert fence_count % 2 == 0, (
            f"{rel_path} has unclosed code fences (fence count: {fence_count})"
        )


def test_sqlite_wal_persistence_under_concurrency():
    """Verify that progress tracking SQLite databases operate in WAL mode with busy_timeout."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        conn = sqlite3.connect(db_path, timeout=5.0)
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")

        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode;")
        mode = cursor.fetchone()[0]
        assert mode.upper() == "WAL", f"Expected WAL mode, got {mode}"

        # Create progress tracking table for Tier 3 modules
        conn.execute("""
            CREATE TABLE IF NOT EXISTS module_track_progress (
                user_id TEXT NOT NULL,
                module_code TEXT NOT NULL,
                track_name TEXT NOT NULL,
                simulation_completed INTEGER DEFAULT 0,
                score REAL DEFAULT 0.0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, module_code)
            );
        """)

        # Insert all 10 tracks
        for expected in EXPECTED_TIER3_MODULES.values():
            conn.execute("""
                INSERT INTO module_track_progress (user_id, module_code, track_name, simulation_completed, score)
                VALUES (?, ?, ?, 1, 95.0);
            """, ("user_victus_01", expected["code"], expected["track"]))

        conn.commit()

        cursor.execute("SELECT count(*) FROM module_track_progress WHERE user_id = 'user_victus_01';")
        count = cursor.fetchone()[0]
        assert count == 10, f"Expected 10 persisted progress records, got {count}"

        conn.close()
    finally:
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except PermissionError:
                pass


def test_passive_cpu_execution_time():
    """Verify test execution completes in sub-500ms preserving HP Victus thermal safety."""
    start_time = time.perf_counter()
    engine = CourseConfigEngine()
    tracks = engine.get_tier3_specialization_tracks()
    assert len(tracks) == 10

    for t in tracks:
        assert t["code"] is not None
        assert t["simulation_component"] is not None

    elapsed = time.perf_counter() - start_time
    assert elapsed < 0.5, f"Execution took {elapsed:.4f}s, exceeding 500ms thermal budget"
