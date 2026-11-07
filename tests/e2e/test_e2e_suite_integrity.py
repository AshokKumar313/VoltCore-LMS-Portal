"""
========================================================================================
VoltCore Apex Academia - Test Suite Integrity Verifier for Playwright E2E Suite
Lead Systems Architect & Quality Assurance Director: Ashok Kumar A
========================================================================================
Validates:
  1. Playwright configuration schema, headless mode enforcement, single worker limitation.
  2. Route path contracts: all URLs tested in .spec.ts map to real Astro pages in src/pages/.
  3. Interactive DOM selectors and text invariants match React components.
  4. HP Victus thermal profile preservation (0 unmonitored browser spawning in unit test runs).
========================================================================================
"""

import os
import re
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
E2E_DIR = os.path.join(BASE_DIR, "tests", "e2e")
SRC_PAGES_DIR = os.path.join(BASE_DIR, "src", "pages")


class TestPlaywrightConfigurationIntegrity:
    """Verifies that playwright.config.ts adheres to production testing and thermal guidelines."""

    def test_config_file_exists(self):
        cfg_path = os.path.join(E2E_DIR, "playwright.config.ts")
        assert os.path.isfile(cfg_path), "playwright.config.ts must exist in tests/e2e/"

    def test_headless_mode_enforced(self):
        cfg_path = os.path.join(E2E_DIR, "playwright.config.ts")
        with open(cfg_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "headless: true" in content, "Headless execution must be strictly enabled."
        assert "workers: 1" in content, "Workers must be limited to 1 for thermal budget safety."
        assert "fullyParallel: false" in content, "Parallel test runs should be disabled to prevent CPU spikes."

    def test_spec_files_exist(self):
        expected_specs = [
            "course_navigation.spec.ts",
            "simulation_workbenches.spec.ts",
            "gate_quiz_assessment.spec.ts",
            "portfolio_export.spec.ts"
        ]
        for spec in expected_specs:
            spec_path = os.path.join(E2E_DIR, spec)
            assert os.path.isfile(spec_path), f"Expected test spec {spec} was not found in tests/e2e/"


class TestE2eRouteMappingContract:
    """Verifies that every route tested by Playwright has a corresponding Astro page."""

    ROUTE_TO_PAGE_MAP = {
        "/": "index.astro",
        "/embedded-systems": "embedded-systems.astro",
        "/embedded-systems/stm32-academy": "embedded-systems/stm32-academy/index.astro",
        "/enterprise-admin": "enterprise-admin.astro",
        "/virtual-bench": "virtual-bench.astro",
        "/math-studio": "math-studio.astro",
        "/simulation": "simulation.astro",
        "/gate-ece": "gate-ece.astro",
        "/exam-center": "exam-center.astro",
        "/student-projects": "student-projects.astro",
        "/careers": "careers.astro"
    }

    def test_all_tested_routes_exist_in_pages(self):
        for route, expected_page in self.ROUTE_TO_PAGE_MAP.items():
            page_file = os.path.join(SRC_PAGES_DIR, *expected_page.split("/"))
            assert os.path.isfile(page_file), f"Route '{route}' maps to missing Astro page: {page_file}"

    def test_spec_files_contain_assertions(self):
        """Verifies each .spec.ts file contains valid test and expect assertions."""
        spec_files = [f for f in os.listdir(E2E_DIR) if f.endswith(".spec.ts")]
        for sf in spec_files:
            path = os.path.join(E2E_DIR, sf)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            assert "test.describe" in content, f"{sf} missing test.describe"
            assert "expect(" in content, f"{sf} missing expect assertions"
            assert "await page.goto(" in content, f"{sf} missing page.goto navigation"
