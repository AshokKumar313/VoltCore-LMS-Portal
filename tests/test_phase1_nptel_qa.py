"""
========================================================================================
VoltCore Apex Academia - Phase 1 Automated Test Suite
NPTEL Mapper JSON, Content QA Anti-Hallucination Validator & Schemdraw Vector Compiler
----------------------------------------------------------------------------------------
Module: tests/test_phase1_nptel_qa.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Academic Institution: Madras Institute of Technology (MIT) Campus, Anna University
Department: Department of Electronics Engineering (Regulation 2023)
========================================================================================
"""

import os
import sys
import json
import tempfile
import unittest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.content_qa_validator import (
    strip_code_and_frontmatter,
    verify_katex_math_balance,
    verify_link_integrity,
    verify_citations_and_sources,
    validate_single_file,
    validate_directory
)
from backend.schematic_generator import (
    generate_bjt_ce_amplifier,
    generate_opamp_inverting,
    generate_rc_lowpass,
    generate_esp32_i2c_bus,
    generate_all_schematics
)


class TestNPTELMapperSchema(unittest.TestCase):
    """Verifies the integrity, structure, and academic mappings of src/data/nptel_mapper.json."""

    @classmethod
    def setUpClass(cls):
        cls.mapper_path = os.path.join(PROJECT_ROOT, "src", "data", "nptel_mapper.json")
        with open(cls.mapper_path, "r", encoding="utf-8") as f:
            cls.data = json.load(f)

    def test_mapper_file_existence_and_metadata(self):
        self.assertTrue(os.path.exists(self.mapper_path), "src/data/nptel_mapper.json must exist")
        self.assertEqual(self.data.get("schema_version"), "1.0.0")
        self.assertIn("Madras Institute of Technology", self.data.get("academic_institution", ""))
        self.assertIn("Anna University", self.data.get("academic_institution", ""))
        self.assertIn("Regulation 2023", self.data.get("regulation", ""))
        self.assertEqual(self.data.get("platform_lead"), "Ashok Kumar A")
        self.assertEqual(self.data.get("public_contact"), "ashokkumar3132008@gmail.com")

    def test_curriculum_modules_coverage(self):
        modules = self.data.get("modules", [])
        self.assertGreaterEqual(len(modules), 9, "Must map all 9 core curriculum modules")

        expected_codes = {
            "EC8701", "EC8702", "EC8703", "EC8704", "EC8705",
            "EC8706", "EC8707", "EC8708", "EC8709"
        }
        actual_codes = {m["module_code"] for m in modules}
        self.assertTrue(expected_codes.issubset(actual_codes), f"Missing module codes: {expected_codes - actual_codes}")

    def test_nptel_lecture_timestamps_and_cos(self):
        for mod in self.data.get("modules", []):
            code = mod["module_code"]
            self.assertIn("module_title", mod, f"Module {code} missing title")
            self.assertGreaterEqual(len(mod.get("mapped_cos", [])), 1, f"Module {code} must have mapped COs")
            self.assertGreaterEqual(len(mod.get("mapped_pos", [])), 1, f"Module {code} must have mapped POs")
            self.assertGreaterEqual(len(mod.get("prerequisites", [])), 1, f"Module {code} must have prerequisites")

            nptel = mod.get("nptel_course", {})
            self.assertTrue(nptel.get("course_id"), f"Module {code} missing NPTEL course_id")
            self.assertTrue(nptel.get("instructor"), f"Module {code} missing NPTEL instructor")
            self.assertTrue(nptel.get("playlist_id"), f"Module {code} missing NPTEL playlist_id")

            lectures = nptel.get("lectures", [])
            self.assertGreaterEqual(len(lectures), 1, f"Module {code} must map at least 1 lecture")

            for lec in lectures:
                t_start = lec.get("timestamp_start_sec", -1)
                t_end = lec.get("timestamp_end_sec", -1)
                self.assertGreaterEqual(t_start, 0, f"Invalid start timestamp in {code}")
                self.assertGreater(t_end, t_start, f"End timestamp must exceed start timestamp in {code}")
                self.assertTrue(lec.get("youtube_video_id"), f"Missing video ID in {code}")
                self.assertTrue(lec.get("youtube_url", "").startswith("https://www.youtube.com/watch?v="))
                self.assertIn(lec.get("unit_mapped"), [1, 2, 3, 4, 5], f"Unit out of bounds in {code}")
                self.assertGreaterEqual(len(lec.get("key_concepts", [])), 2, f"Insufficient key concepts in {code}")


class TestContentQAValidator(unittest.TestCase):
    """Verifies the parsing, bracket matching, link verification, and citation checks in content_qa_validator.py."""

    def test_katex_display_math_balance(self):
        # Balanced display math
        good_content = "Here is an equation:\n$$E = m \\cdot c^2$$\nwhich is famous."
        issues = verify_katex_math_balance(good_content)
        self.assertEqual(len(issues), 0)

        # Unbalanced display math
        bad_content = "Here is broken math:\n$$E = m \\cdot c^2\nwith no closing delimiter."
        issues = verify_katex_math_balance(bad_content)
        self.assertGreaterEqual(len(issues), 1)
        self.assertTrue(any("display math" in err.lower() for err in issues))

    def test_katex_curly_brace_and_left_right_balance(self):
        # Mismatched curly brace
        broken_brace = "The formula is $\\frac{a}{b$ which misses closing brace."
        issues = verify_katex_math_balance(broken_brace)
        self.assertTrue(any("unclosed opening brace" in err.lower() or "brace" in err.lower() for err in issues))

        # Mismatched \left / \right
        broken_left = "Formula: $$\\left( \\frac{a}{b} $$ without right paren."
        issues = verify_katex_math_balance(broken_left)
        self.assertTrue(any("left" in err.lower() and "right" in err.lower() for err in issues))

    def test_link_integrity_verification(self):
        # Valid internal route
        valid_link = "Check our [Attendance Log](/attendance) or [Live Telemetry](/telemetry)."
        issues = verify_link_integrity(valid_link, PROJECT_ROOT)
        self.assertEqual(len(issues), 0)

        # Invalid internal route
        invalid_link = "Check this [Phantom Page](/nonexistent_phantom_route_12345)."
        issues = verify_link_integrity(invalid_link, PROJECT_ROOT)
        self.assertGreaterEqual(len(issues), 1)
        self.assertTrue(any("unrecognized internal route" in err.lower() for err in issues))

        # Empty anchor or target
        empty_anchor = "Broken [ ](/attendance) link."
        issues_empty = verify_link_integrity(empty_anchor, PROJECT_ROOT)
        self.assertTrue(any("empty link anchor" in err.lower() for err in issues_empty))

    def test_citations_and_sources_enforcement(self):
        # Content with IEEE reference frontmatter
        good_frontmatter = "ieeeReference: 'IEEE Transactions on Vehicular Technology, Vol. 72'"
        good_body = "This paper analyzes CAN bus priority arbitration."
        issues, count = verify_citations_and_sources(good_body, good_frontmatter)
        self.assertEqual(len(issues), 0)
        self.assertGreaterEqual(count, 1)

        # Content with no citations or references
        blank_body = "Some generic unverifiable statement without citations or standard names."
        issues_fail, count_zero = verify_citations_and_sources(blank_body, None)
        self.assertGreaterEqual(len(issues_fail), 1)
        self.assertEqual(count_zero, 0)
        self.assertTrue(any("mandatory citation" in err.lower() for err in issues_fail))

    def test_full_curriculum_directory_qa_audit(self):
        modules_dir = os.path.join(PROJECT_ROOT, "src", "content", "modules")
        report = validate_directory(modules_dir)
        self.assertGreaterEqual(report["total_files"], 10, "Should scan at least 10 curriculum module files")
        self.assertEqual(report["failed_files"], 0, f"Expected 0 QA failures, found errors in: {[r['filename'] for r in report['results'] if not r['passed']]}")
        self.assertTrue(report["all_passed"], "All modules must pass content QA audit")


class TestSchematicGenerator(unittest.TestCase):
    """Verifies deterministic Schemdraw circuit compilation, SVG formatting, and component tags."""

    def test_generate_bjt_ce_amplifier_svg(self):
        svg_content = generate_bjt_ce_amplifier()
        self.assertIsInstance(svg_content, str)
        self.assertIn("<svg", svg_content)
        self.assertIn("</svg>", svg_content)
        self.assertIn("2N2222", svg_content)
        self.assertIn("R1", svg_content)
        self.assertIn("Rc", svg_content)
        self.assertIn("Vcc", svg_content)
        self.assertIn("VoltCore Apex Academia", svg_content)

    def test_generate_opamp_inverting_svg(self):
        svg_content = generate_opamp_inverting()
        self.assertIn("<svg", svg_content)
        self.assertIn("LM741", svg_content)
        self.assertIn("Rin", svg_content)
        self.assertIn("Rf", svg_content)
        self.assertIn("Vout", svg_content)

    def test_generate_rc_lowpass_svg(self):
        svg_content = generate_rc_lowpass()
        self.assertIn("<svg", svg_content)
        self.assertIn("1 kΩ", svg_content)
        self.assertIn("100 nF", svg_content)
        self.assertIn("fc = 1.59 kHz", svg_content)

    def test_generate_esp32_i2c_bus_svg(self):
        svg_content = generate_esp32_i2c_bus()
        self.assertIn("<svg", svg_content)
        self.assertIn("GPIO 21", svg_content)
        self.assertIn("GPIO 22", svg_content)
        self.assertIn("4.7 kΩ", svg_content)
        self.assertIn("ADXL345", svg_content)

    def test_generate_all_schematics_writes_to_disk(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            generated = generate_all_schematics(output_dir=tmp_dir)
            self.assertEqual(len(generated), 4)

            expected_files = [
                "bjt_ce_amplifier.svg",
                "opamp_inverting_amplifier.svg",
                "rc_lowpass_filter.svg",
                "esp32_i2c_bus_topology.svg"
            ]

            for fname in expected_files:
                fpath = os.path.join(tmp_dir, fname)
                self.assertTrue(os.path.exists(fpath), f"File {fname} was not created on disk")
                self.assertGreater(os.path.getsize(fpath), 1000, f"File {fname} is unexpectedly small")


if __name__ == "__main__":
    unittest.main()
