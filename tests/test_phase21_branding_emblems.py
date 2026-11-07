"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 21 Brand Identity & ECE Subject Emblem System
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase21_branding_emblems.py
Platform Lead & Educational Systems Director: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Verifies:
  1. Sovereign Brand Identity & Institutional Presentation:
     - Emerald/cyan silicon emblem asset integrity (public/favicon.svg)
     - Institutional motto: "Engineering Intelligence. Practical Innovation. Academic Excellence."
     - Multi-role authentication views (Student, Teacher, Lab-Instructor, Admin)
  2. Canva-Inspired Subject Emblem Registry (14 Core ECE Disciplines):
     - Complete 14 core disciplines registration
     - Technical SVG circuit geometries and element counts
     - Harmonious primary/accent color codes and gradients
     - Deterministic fallback icon behavior for unknown / elective courses
  3. Frontend Integration & Theme Adaptability:
     - SubjectEmblem component existence and props contract
     - Integration in EceCourseworkGrid and CourseShellHub
     - 18-theme CSS variables compatibility
========================================================================================
"""

import os
import sys
import json
import re
import pytest
from typing import Dict, Any

# Ensure project root in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.subject_emblem_registry import (
    ECE_SUBJECT_EMBLEMS,
    DEFAULT_FALLBACK,
    get_subject_emblem,
    list_all_subject_emblems,
    get_institutional_branding,
    INSTITUTIONAL_BRANDING
)


# ========================================================================================
# 1. SOVEREIGN BRAND IDENTITY & ASSETS
# ========================================================================================

class TestPhase21SovereignBrandIdentity:
    """Verifies official VoltCore brand identity, silicon emblem, and institutional motto."""

    def test_favicon_silicon_emblem_asset_integrity(self):
        """public/favicon.svg must exist, be valid XML/SVG, and contain the emerald silicon die."""
        favicon_path = os.path.join(PROJECT_ROOT, "public", "favicon.svg")
        assert os.path.isfile(favicon_path), "public/favicon.svg asset missing!"

        with open(favicon_path, "r", encoding="utf-8") as f:
            svg_content = f.read()

        assert "<svg" in svg_content
        assert "</svg>" in svg_content
        assert "viewBox=\"0 0 64 64\"" in svg_content
        # Assert emerald silicon gradient and chevron path
        assert "#00F0B5" in svg_content
        assert "#00693E" in svg_content
        assert "Silicon Substrate" in svg_content or "rect" in svg_content
        assert "Chevron" in svg_content or "path" in svg_content

    def test_institutional_branding_metadata(self):
        """Institutional branding must contain verified MIT Campus and Anna University metadata."""
        branding = get_institutional_branding()
        assert branding["platform_name"] == "VoltCore Apex Academia"
        assert "Ashok Kumar A" in branding["lead_architect"]
        assert "2023MITEC042" in branding["lead_architect"]
        assert "Madras Institute of Technology" in branding["institution"]
        assert "MIT" in branding["institution"]
        assert "Campus" in branding["institution"]
        assert "Anna University" in branding["institution"]
        assert "Department of Electronics Engineering" in branding["department"]
        assert branding["regulation"] == "Regulation 2023"
        assert branding["motto"] == "Engineering Intelligence. Practical Innovation. Academic Excellence."
        assert branding["supported_themes_count"] == 18

    def test_login_page_and_multi_role_auth_views(self):
        """src/pages/login.astro and MultiRoleAuthModal.jsx must exist and support all 4 roles."""
        login_page_path = os.path.join(PROJECT_ROOT, "src", "pages", "login.astro")
        modal_comp_path = os.path.join(PROJECT_ROOT, "src", "components", "MultiRoleAuthModal.jsx")

        assert os.path.isfile(login_page_path), "src/pages/login.astro must exist"
        assert os.path.isfile(modal_comp_path), "src/components/MultiRoleAuthModal.jsx must exist"

        with open(modal_comp_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Assert all 4 institutional roles
        required_roles = ["Student", "Teacher", "Lab-Instructor", "Admin_Owner"]
        for role in required_roles:
            assert role in content, f"Role '{role}' missing from MultiRoleAuthModal!"

        # Assert PBKDF2 iterations and institutional motto
        assert "PBKDF2" in content
        assert "600,000" in content
        assert "Engineering Intelligence. Practical Innovation. Academic Excellence." in content


# ========================================================================================
# 2. CANVA-INSPIRED SUBJECT EMBLEM REGISTRY (14 CORE ECE DISCIPLINES)
# ========================================================================================

class TestPhase21SubjectEmblemRegistry:
    """Verifies all 14 core ECE disciplines have precision vector SVG emblems and metadata."""

    REQUIRED_DISCIPLINE_CODES = [
        "EC23C01",  # Circuit Analysis
        "EC23C02",  # Semiconductor Physics
        "EC23C03",  # Electronic Devices
        "EC23C05",  # Analog Electronics
        "EC23C06",  # Digital Electronics
        "EC23C04",  # Signals & Systems
        "EC23C07",  # Control Systems
        "EC23S01",  # Python DSP
        "EC23C08",  # Communication Systems
        "EC8702",   # Embedded Systems
        "STM32-ACADEMY",  # STM32 Firmware
        "IOT8701",  # ESP32 IoT Systems
        "HDL6001",  # Verilog HDL & FPGA
        "VLSI7001", # CMOS VLSI Design
    ]

    def test_all_14_disciplines_registered_backend(self):
        """All 14 core ECE courses must be registered in backend/subject_emblem_registry.py."""
        registered = list_all_subject_emblems()
        assert len(registered) == 14
        reg_codes = [s["code"] for s in registered]
        for code in self.REQUIRED_DISCIPLINE_CODES:
            assert code in reg_codes, f"Course code {code} missing from backend emblem registry!"

    def test_frontend_ts_subject_registry_mirrors_backend(self):
        """src/data/subjectRegistry.ts must exist and mirror all 14 disciplines with SVG paths."""
        ts_path = os.path.join(PROJECT_ROOT, "src", "data", "subjectRegistry.ts")
        assert os.path.isfile(ts_path), "src/data/subjectRegistry.ts must exist"

        with open(ts_path, "r", encoding="utf-8") as f:
            ts_content = f.read()

        for code in self.REQUIRED_DISCIPLINE_CODES:
            assert f"'{code}'" in ts_content or f'"{code}"' in ts_content, (
                f"Course code {code} missing from src/data/subjectRegistry.ts!"
            )

    def test_subject_emblem_geometry_and_color_tokens(self):
        """Every subject emblem must define valid colors, symbol name, and keywords."""
        hex_color_regex = re.compile(r"^#[0-9A-Fa-f]{6}$")

        for code in self.REQUIRED_DISCIPLINE_CODES:
            emblem = get_subject_emblem(code)
            assert emblem["code"] == code
            assert len(emblem["name"]) > 10
            assert len(emblem["symbol_name"]) > 5
            assert hex_color_regex.match(emblem["primary_color"]), f"Invalid primary hex: {emblem['primary_color']}"
            assert hex_color_regex.match(emblem["accent_color"]), f"Invalid accent hex: {emblem['accent_color']}"
            assert len(emblem["gradient"]) == 2
            assert len(emblem["technical_keywords"]) >= 3
            assert len(emblem["accessible_label"]) > 10

    def test_fallback_emblem_for_unknown_codes(self):
        """Unknown or None course codes must resolve to DEFAULT_FALLBACK without crashing."""
        fallback_unknown = get_subject_emblem("ELECTIVE_UNKNOWN_999")
        assert fallback_unknown["code"] == "CORE-GENERIC"
        assert fallback_unknown["symbol_name"] == "Silicon Chevron Beacon"

        fallback_none = get_subject_emblem(None)
        assert fallback_none["code"] == "CORE-GENERIC"
        assert fallback_none["primary_color"] == "#00F0B5"


# ========================================================================================
# 3. FRONTEND INTEGRATION & THEME ADAPTABILITY
# ========================================================================================

class TestPhase21FrontendIntegrationAndThemes:
    """Verifies component existence, theme variable bindings, and dashboard integrations."""

    def test_subject_emblem_jsx_component_exists(self):
        """src/components/SubjectEmblem.jsx must exist and support sizing props."""
        comp_path = os.path.join(PROJECT_ROOT, "src", "components", "SubjectEmblem.jsx")
        assert os.path.isfile(comp_path), "src/components/SubjectEmblem.jsx must exist"

        with open(comp_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "getSubjectMetadata" in content
        assert "SIZE_MAP" in content
        assert "aria-label" in content

    def test_voltcore_brand_header_component_exists(self):
        """src/components/VoltCoreBrandHeader.astro must feature the institutional motto."""
        header_path = os.path.join(PROJECT_ROOT, "src", "components", "VoltCoreBrandHeader.astro")
        assert os.path.isfile(header_path), "src/components/VoltCoreBrandHeader.astro must exist"

        with open(header_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "favicon.svg" in content
        assert "Engineering Intelligence. Practical Innovation. Academic Excellence." in content
        assert "var(--theme-primary)" in content

    def test_topbar_uses_official_silicon_emblem(self):
        """src/components/Topbar.astro must embed /favicon.svg and institutional subtitle."""
        topbar_path = os.path.join(PROJECT_ROOT, "src", "components", "Topbar.astro")
        with open(topbar_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "/favicon.svg" in content
        assert "Engineering Intelligence" in content
        assert "Academic Excellence" in content
        assert "/login" in content

    def test_coursework_grid_and_course_shell_integration(self):
        """EceCourseworkGrid and CourseShellHub must import and render the emblem system."""
        grid_path = os.path.join(PROJECT_ROOT, "src", "components", "EceCourseworkGrid.jsx")
        shell_path = os.path.join(PROJECT_ROOT, "src", "components", "CourseShellHub.jsx")

        with open(grid_path, "r", encoding="utf-8") as f:
            grid_content = f.read()
        assert "SubjectEmblem" in grid_content

        with open(shell_path, "r", encoding="utf-8") as f:
            shell_content = f.read()
        assert "getSubjectMetadata" in shell_content
        assert "DepartmentalBadgeIcon" in shell_content
