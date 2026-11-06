"""
========================================================================================
VoltCore Apex Academia - Phase 2 Expansion Automated Test Suite
Content Status Lifecycle, Career Tracks, Virtual Bench, Smart NPTEL & tsconfig Compliance
----------------------------------------------------------------------------------------
Module: tests/test_phase2_expansion.py
Platform Lead / System Architect: Ashok Kumar A
Academic Institution: Madras Institute of Technology (MIT) Campus, Anna University
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
========================================================================================
"""

import os
import sys
import json
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import lms_database
from backend.content_status_api import (
    get_content_status_report,
    update_content_status_entry,
    get_changelog_history,
    VALID_STATUSES
)
import scripts.content_qa_validator as validator


class TestTsconfigDeprecations(unittest.TestCase):
    """Verifies tsconfig.json has the requested ignoreDeprecations flag and strict compiler options."""

    def test_tsconfig_has_ignore_deprecations(self):
        tsconfig_path = os.path.join(PROJECT_ROOT, "tsconfig.json")
        self.assertTrue(os.path.exists(tsconfig_path), "tsconfig.json must exist in project root")

        with open(tsconfig_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        compiler_options = data.get("compilerOptions", {})
        self.assertIn("ignoreDeprecations", compiler_options)
        self.assertIn(compiler_options["ignoreDeprecations"], ["5.0", "6.0"])
        self.assertEqual(compiler_options.get("baseUrl"), ".")
        self.assertTrue(compiler_options.get("strictNullChecks"))


class TestContentStatusLifecycle(unittest.TestCase):
    """Verifies SQLite WAL lifecycle state machine and audit changelog for curriculum modules."""

    def setUp(self):
        lms_database.init_db()

    def test_valid_statuses_defined(self):
        expected = ["Draft", "AI-Generated", "Human-Reviewed", "Faculty-Approved", "Published"]
        self.assertEqual(VALID_STATUSES, expected)

    def test_get_content_status_report(self):
        report = get_content_status_report()
        self.assertEqual(report["status"], "success")
        self.assertIn("total_modules", report)
        self.assertIn("stage_distribution", report)
        self.assertIn("modules", report)
        self.assertGreaterEqual(len(report["modules"]), 5)

        first = report["modules"][0]
        self.assertIn("module_code", first)
        self.assertIn("status", first)
        self.assertIn(first["status"], VALID_STATUSES)

    def test_update_status_and_changelog_audit(self):
        test_mod = "EC8701"
        # Transition to Human-Reviewed
        res, code = update_content_status_entry(
            module_code=test_mod,
            new_status="Human-Reviewed",
            author="Dr. S. K. Ramanathan (Professor, MIT ECE)",
            comment="Audit completed for ESP32 FreeRTOS timing specs"
        )
        self.assertEqual(code, 200)
        self.assertTrue(res["success"])
        self.assertEqual(res["new_status"], "Human-Reviewed")

        # Verify audit changelog
        history_resp = get_changelog_history(test_mod)
        self.assertEqual(history_resp["status"], "success")
        history = history_resp["changelog"]
        self.assertGreaterEqual(len(history), 1)
        latest = history[0]
        self.assertEqual(latest["module_code"], test_mod)
        self.assertEqual(latest["new_status"], "Human-Reviewed")
        self.assertIn("Dr. S. K. Ramanathan", latest["author"])
        self.assertIn("FreeRTOS", latest["comment"])

    def test_invalid_status_rejected(self):
        res, code = update_content_status_entry(
            module_code="EC8701",
            new_status="Invalid-Stage-Name",
            author="Ashok Kumar A",
            comment="Testing invalid input"
        )
        self.assertEqual(code, 400)
        self.assertFalse(res["success"])
        self.assertIn("error", res)


class TestCareerTracksCurriculum(unittest.TestCase):
    """Verifies the 5 ECE career tracks in src/content/modules/career-tracks/ with full schema."""

    TRACKS = [
        "embedded-firmware.mdx",
        "vlsi-rtl-design.mdx",
        "iot-cloud-systems.mdx",
        "automotive-systems.mdx",
        "hardware-test-validation.mdx"
    ]

    def test_all_career_track_files_exist(self):
        tracks_dir = os.path.join(PROJECT_ROOT, "src", "content", "modules", "career-tracks")
        self.assertTrue(os.path.isdir(tracks_dir), "career-tracks directory must exist")

        for track_file in self.TRACKS:
            path = os.path.join(tracks_dir, track_file)
            self.assertTrue(os.path.exists(path), f"Career track {track_file} must exist")

    def test_career_tracks_frontmatter_schema(self):
        tracks_dir = os.path.join(PROJECT_ROOT, "src", "content", "modules", "career-tracks")
        required_keys = [
            "title", "code", "semester", "credits", "order",
            "difficulty", "prerequisites", "learningOutcomes",
            "hardwareKit", "tags", "ieeeReference"
        ]

        for track_file in self.TRACKS:
            path = os.path.join(tracks_dir, track_file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertTrue(content.startswith("---"), f"{track_file} must have frontmatter header")
            parts = content.split("---", 2)
            self.assertGreaterEqual(len(parts), 3, f"{track_file} must have complete frontmatter block")
            frontmatter = parts[1]

            for key in required_keys:
                self.assertIn(f"{key}:", frontmatter, f"{track_file} missing required key '{key}'")

            # Check that Anna University or ECE regulation is referenced
            self.assertTrue(
                "Anna University" in content or "MIT Campus" in content or "R2023" in content,
                f"{track_file} should link to Anna University MIT ECE standards"
            )


class TestPhase2ComponentsAndPages(unittest.TestCase):
    """Verifies React components and Astro pages created in Phase 2."""

    def test_smart_nptel_player_component_and_page(self):
        comp = os.path.join(PROJECT_ROOT, "src", "components", "SmartNptelPlayer.jsx")
        page = os.path.join(PROJECT_ROOT, "src", "pages", "nptel-player.astro")
        self.assertTrue(os.path.exists(comp), "SmartNptelPlayer.jsx must exist")
        self.assertTrue(os.path.exists(page), "nptel-player.astro must exist")

        with open(comp, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn("SmartNptelPlayer", code)
        self.assertIn("playbackSpeed", code)
        self.assertIn("exportNotesMarkdown", code)

        with open(page, "r", encoding="utf-8") as f:
            pcode = f.read()
        self.assertIn("SmartNptelPlayer", pcode)

    def test_content_status_board_component(self):
        comp = os.path.join(PROJECT_ROOT, "src", "components", "ContentStatusBoard.jsx")
        self.assertTrue(os.path.exists(comp), "ContentStatusBoard.jsx must exist")

        with open(comp, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn("ContentStatusBoard", code)
        self.assertIn("handleStatusSubmit", code)
        self.assertIn("/api/content/status", code)

    def test_virtual_oscilloscope_component_and_page(self):
        comp = os.path.join(PROJECT_ROOT, "src", "components", "VirtualOscilloscope.jsx")
        page = os.path.join(PROJECT_ROOT, "src", "pages", "virtual-bench.astro")
        self.assertTrue(os.path.exists(comp), "VirtualOscilloscope.jsx must exist")
        self.assertTrue(os.path.exists(page), "virtual-bench.astro must exist")

        with open(comp, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn("VirtualOscilloscope", code)
        self.assertIn("Keysight", code)
        self.assertIn("canvasRef", code)
        self.assertIn("deltaSeconds", code)

        with open(page, "r", encoding="utf-8") as f:
            pcode = f.read()
        self.assertIn("VirtualOscilloscope", pcode)

    def test_careers_page_exists(self):
        page = os.path.join(PROJECT_ROOT, "src", "pages", "careers.astro")
        self.assertTrue(os.path.exists(page), "careers.astro must exist")
        with open(page, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn("careerTracks", code)
        self.assertIn("TRACK-EMB", code)


class TestNavigationAndPwaRouteSync(unittest.TestCase):
    """Verifies navigation links, service worker precaching, and QA validator routes are in sync."""

    def test_qa_validator_contains_phase2_routes(self):
        self.assertIn("/careers", validator.VALID_INTERNAL_ROUTES)
        self.assertIn("/virtual-bench", validator.VALID_INTERNAL_ROUTES)
        self.assertIn("/nptel-player", validator.VALID_INTERNAL_ROUTES)

    def test_service_worker_precaches_phase2_routes(self):
        for sw_file in ["public/service-worker.js", "src/service-worker.js"]:
            path = os.path.join(PROJECT_ROOT, sw_file)
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
            self.assertIn("'/careers'", code)
            self.assertIn("'/virtual-bench'", code)
            self.assertIn("'/nptel-player'", code)

    def test_topbar_links_to_phase2_routes(self):
        topbar_path = os.path.join(PROJECT_ROOT, "src", "components", "Topbar.astro")
        with open(topbar_path, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn('href="/careers"', code)
        self.assertIn('href="/virtual-bench"', code)
        self.assertIn('href="/nptel-player"', code)


if __name__ == "__main__":
    unittest.main()
