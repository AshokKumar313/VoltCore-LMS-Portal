"""
========================================================================================
VoltCore Apex Academia - Phase 22 Verification Suite
Professional Subject Naming, Discipline Alignment & Role Workspace Dashboards
----------------------------------------------------------------------------------------
Module: tests/test_phase22_professional_naming.py
Platform Lead & Educational Systems Director: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import re
import pytest
from pathlib import Path

from backend.subject_emblem_registry import (
    ECE_SUBJECT_EMBLEMS,
    DEFAULT_FALLBACK,
    get_subject_emblem,
    get_discipline_name,
    get_professional_title,
    list_all_subject_emblems,
    list_discipline_catalog,
    get_institutional_branding,
)

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


class TestProfessionalSubjectNaming:
    """Verifies that all 14 core ECE subjects feature clean, professional engineering names."""

    def test_backend_all_fourteen_disciplines_populated(self):
        """Backend registry must contain exactly 14 official ECE disciplines."""
        assert len(ECE_SUBJECT_EMBLEMS) == 14
        expected_codes = {
            "EC23C01", "EC23C02", "EC23C03", "EC23C05", "EC23C06",
            "EC23C04", "EC23C07", "EC23S01", "EC23C08", "EC8702",
            "STM32-ACADEMY", "IOT8701", "HDL6001", "VLSI7001"
        }
        assert set(ECE_SUBJECT_EMBLEMS.keys()) == expected_codes

    def test_backend_professional_naming_attributes(self):
        """Every discipline must have discipline_name, professional_title, industry_domain, and subfield."""
        for code, meta in ECE_SUBJECT_EMBLEMS.items():
            assert "discipline_name" in meta, f"Missing discipline_name for {code}"
            assert "professional_title" in meta, f"Missing professional_title for {code}"
            assert "industry_domain" in meta, f"Missing industry_domain for {code}"
            assert "subfield" in meta, f"Missing subfield for {code}"

            # Discipline names must be clean, human-readable strings (> 5 chars)
            assert len(meta["discipline_name"]) >= 5
            assert len(meta["professional_title"]) >= 5

            # Discipline names must NOT contain the raw course code
            assert code not in meta["discipline_name"], (
                f"Raw code {code} found in discipline_name: '{meta['discipline_name']}'"
            )

    def test_backend_discipline_lookup_helpers(self):
        """Lookup helpers must return valid professional names and handle invalid/None queries."""
        # Known codes
        assert get_discipline_name("EC23C02") == "Semiconductor Device Physics"
        assert get_discipline_name("VLSI7001") == "Digital VLSI Design & Silicon Layout"
        assert get_discipline_name("EC23C07") == "Control Systems Engineering"
        assert get_discipline_name("EC8702") == "Embedded Real-Time Systems"

        # Case insensitivity & whitespace trimming
        assert get_discipline_name("  ec23c01  ") == "Circuit Analysis & Network Synthesis"

        # Professional title lookup
        assert "Feedback Dynamics" in get_professional_title("EC23C07")
        assert "Sub-Micron CMOS" in get_professional_title("VLSI7001")

        # Fallback handling
        assert get_discipline_name(None) == DEFAULT_FALLBACK["discipline_name"]
        assert get_discipline_name("UNKNOWN-COURSE-999") == DEFAULT_FALLBACK["discipline_name"]
        assert get_professional_title(None) == DEFAULT_FALLBACK["professional_title"]

    def test_backend_discipline_catalog(self):
        """list_discipline_catalog must return 14 structured items with clean metadata."""
        catalog = list_discipline_catalog()
        assert len(catalog) == 14
        for item in catalog:
            assert "discipline_name" in item
            assert "professional_title" in item
            assert "industry_domain" in item
            assert "subfield" in item
            assert "code" in item
            assert "primary_color" in item

    def test_typescript_registry_contains_professional_fields(self):
        """TypeScript registry must declare and define disciplineName, professionalTitle, industryDomain, subfield."""
        ts_path = WORKSPACE_ROOT / "src" / "data" / "subjectRegistry.ts"
        assert ts_path.exists(), "src/data/subjectRegistry.ts must exist"
        content = ts_path.read_text(encoding="utf-8")

        # Interface definitions
        assert "disciplineName: string;" in content
        assert "professionalTitle: string;" in content
        assert "industryDomain: string;" in content
        assert "subfield: string;" in content

        # Helper functions
        assert "export function getDisciplineName" in content
        assert "export function getProfessionalTitle" in content

        # Check key discipline names in registry
        assert "'Semiconductor Device Physics'" in content
        assert "'Digital VLSI Design & Silicon Layout'" in content
        assert "'Control Systems Engineering'" in content
        assert "'Embedded Real-Time Systems'" in content


class TestRoleBasedDashboardWorkspaces:
    """Verifies that all three role workspaces are equipped with sovereign branding, role badges, and breadcrumbs."""

    def test_student_learning_dashboard(self):
        """Student Learning Dashboard must contain VoltCoreBrandHeader, SCHOLAR/STUDENT role badge, and breadcrumbs."""
        page_path = WORKSPACE_ROOT / "src" / "pages" / "learning-dashboard.astro"
        assert page_path.exists()
        content = page_path.read_text(encoding="utf-8")

        assert "VoltCoreBrandHeader" in content
        assert "ROLE: SCHOLAR / STUDENT" in content
        assert "Student Learning Dashboard" in content
        assert "aria-label=\"Breadcrumb\"" in content
        assert "14 Core ECE" in content

    def test_faculty_productivity_workspace(self):
        """Faculty Workspace must contain VoltCoreBrandHeader, PROFESSOR role badge, and breadcrumbs."""
        page_path = WORKSPACE_ROOT / "src" / "pages" / "faculty-workspace.astro"
        assert page_path.exists()
        content = page_path.read_text(encoding="utf-8")

        assert "VoltCoreBrandHeader" in content
        assert "ROLE: PROFESSOR / CURRICULUM DIRECTOR" in content
        assert "Faculty & Department Productivity Workspace" in content
        assert "aria-label=\"Breadcrumb\"" in content
        assert "Units I - V" in content

    def test_enterprise_admin_control_panel(self):
        """Enterprise Admin must contain VoltCoreBrandHeader, DEAN role badge, and breadcrumbs."""
        page_path = WORKSPACE_ROOT / "src" / "pages" / "enterprise-admin.astro"
        assert page_path.exists()
        content = page_path.read_text(encoding="utf-8")

        assert "VoltCoreBrandHeader" in content
        assert "ROLE: DEAN / ACCREDITATION CONTROLLER" in content
        assert "Enterprise Administration" in content
        assert "aria-label=\"Breadcrumb\"" in content
        assert "NBA" in content or "CO-PO" in content


class TestComponentPresentationIntegrity:
    """Verifies component presentation layers display clean engineering terms without exposing raw codes."""

    def test_subject_emblem_tooltip_cleanliness(self):
        """SubjectEmblem tooltip must present clean engineering discipline name and symbol without raw code parens."""
        emblem_path = WORKSPACE_ROOT / "src" / "components" / "SubjectEmblem.jsx"
        assert emblem_path.exists()
        content = emblem_path.read_text(encoding="utf-8")

        # The title attribute must use displayName — symbolName
        assert "${displayName} — ${meta.symbolName}" in content
        # Must not contain the old format: meta.name (meta.code) - meta.symbolName
        assert "${meta.name} (${meta.code})" not in content
        # Must support showLabel
        assert "showLabel = false" in content

    def test_coursework_grid_secondary_code_placement(self):
        """EceCourseworkGrid must emphasize discipline name and demote code to secondary metadata."""
        grid_path = WORKSPACE_ROOT / "src" / "components" / "EceCourseworkGrid.jsx"
        assert grid_path.exists()
        content = grid_path.read_text(encoding="utf-8")

        assert "course.disciplineName || course.title" in content
        assert "Technical Course Code:" in content

    def test_course_shell_hub_professional_titles(self):
        """CourseShellHub must display shortTitle/name prominently with code in brackets."""
        shell_path = WORKSPACE_ROOT / "src" / "components" / "CourseShellHub.jsx"
        assert shell_path.exists()
        content = shell_path.read_text(encoding="utf-8")

        assert "c.shortTitle || c.name" in content
        assert "[{c.code}]" in content
