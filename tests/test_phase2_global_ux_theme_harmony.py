"""
========================================================================================
VoltCore Apex Academia - Phase 2 Global UX Polish & 18-Theme Visual Harmony Test Suite
Anna University / MIT Campus Standards (Department of Electronics Engineering)
Platform Lead & Principal Systems Architect: Ashok Kumar A (2023MITEC042)
Target Hardware: HP Victus (LAPTOP-3NEGBVLE) — Passive CPU (<5%), Zero GPU Load
Standards: WCAG 2.1 AAA Accessibility • 18 Vibrant Non-Black Themes • Responsive Layout
========================================================================================
"""

import os
import re
import math
from pathlib import Path
import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_THEME_VARS = [
    "--theme-primary",
    "--theme-accent",
    "--theme-bg",
    "--theme-bg-gradient",
    "--theme-surface",
    "--theme-card",
    "--theme-border",
    "--theme-text",
    "--theme-text-muted",
    "--theme-glow"
]

EXPECTED_THEME_IDS = [
    "cyber-emerald", "electric-violet", "sunset-crimson", "oceanic-azure",
    "golden-mustard", "tokyo-neon", "nordic-frost", "forest-sage",
    "solar-flare", "cherry-blossom", "pastel-academic", "oxford-navy",
    "synthwave-80s", "matrix-terminal", "lavender-dream", "autumn-copper",
    "clean-canvas", "cosmic-nebula"
]


def hex_to_rgb(hex_str: str):
    clean = hex_str.strip().lstrip('#')
    if len(clean) == 3:
        clean = ''.join([c * 2 for c in clean])
    return [int(clean[i:i+2], 16) for i in (0, 2, 4)]


def relative_luminance(rgb):
    srgb = [c / 255.0 for c in rgb]
    lum = []
    for c in srgb:
        if c <= 0.03928:
            lum.append(c / 12.92)
        else:
            lum.append(((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * lum[0] + 0.7152 * lum[1] + 0.0722 * lum[2]


def contrast_ratio(rgb1, rgb2):
    l1 = relative_luminance(rgb1)
    l2 = relative_luminance(rgb2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


class TestEighteenThemeHarmony:
    """Verifies that all 18 themes contain complete CSS variables and satisfy WCAG AAA standards."""

    @pytest.fixture(autouse=True)
    def load_global_css(self):
        css_path = WORKSPACE_ROOT / "src" / "styles" / "global.css"
        assert css_path.exists(), "global.css must exist"
        self.css_content = css_path.read_text(encoding="utf-8")

    def test_all_18_themes_registered_in_css(self):
        for theme_id in EXPECTED_THEME_IDS:
            assert f'[data-theme="{theme_id}"]' in self.css_content, f"Theme '{theme_id}' missing in global.css"

    def test_each_theme_defines_all_10_variables(self):
        blocks = re.findall(r'\[data-theme=["\']([a-zA-Z0-9_-]+)["\']\][^{]*\{([^}]+)\}', self.css_content)
        theme_map = {tid: content for tid, content in blocks}

        for theme_id in EXPECTED_THEME_IDS:
            assert theme_id in theme_map, f"Theme '{theme_id}' not parsed properly"
            content = theme_map[theme_id]
            for var in REQUIRED_THEME_VARS:
                assert var in content, f"Variable '{var}' missing in theme '{theme_id}'"

    def test_wcag_aaa_contrast_ratios_across_all_themes(self):
        blocks = re.findall(r'\[data-theme=["\']([a-zA-Z0-9_-]+)["\']\][^{]*\{([^}]+)\}', self.css_content)
        for theme_id, content in blocks:
            text_match = re.search(r'--theme-text:\s*(#[0-9a-fA-F]{3,6})', content)
            muted_match = re.search(r'--theme-text-muted:\s*(#[0-9a-fA-F]{3,6})', content)
            bg_match = re.search(r'--theme-bg:\s*(#[0-9a-fA-F]{3,6})', content)

            assert text_match and bg_match, f"Theme '{theme_id}' missing text or bg hex code"
            primary_contrast = contrast_ratio(hex_to_rgb(text_match.group(1)), hex_to_rgb(bg_match.group(1)))
            assert primary_contrast >= 7.0, f"Theme '{theme_id}' primary text contrast ({primary_contrast:.2f}:1) fails WCAG AAA (>= 7.0:1)"

            if muted_match:
                muted_contrast = contrast_ratio(hex_to_rgb(muted_match.group(1)), hex_to_rgb(bg_match.group(1)))
                assert muted_contrast >= 4.5, f"Theme '{theme_id}' muted text contrast ({muted_contrast:.2f}:1) fails WCAG AA (>= 4.5:1)"


class TestFrontendAccessibilityAndPolish:
    """Verifies ARIA roles, focus indicators, and semantic HTML across core micro-islands."""

    def test_multi_role_auth_modal_accessibility(self):
        file_path = WORKSPACE_ROOT / "src" / "components" / "MultiRoleAuthModal.jsx"
        assert file_path.exists()
        content = file_path.read_text(encoding="utf-8")

        assert 'role="tablist"' in content
        assert 'aria-selected' in content
        assert 'htmlFor="auth-user-id"' in content
        assert 'id="auth-user-id"' in content
        assert 'htmlFor="auth-password"' in content
        assert 'id="auth-password"' in content
        assert 'focus:ring-2' in content

    def test_theme_selector_keyboard_navigation_and_aria(self):
        file_path = WORKSPACE_ROOT / "src" / "components" / "ThemeSelector.jsx"
        assert file_path.exists()
        content = file_path.read_text(encoding="utf-8")

        assert 'aria-haspopup="dialog"' in content
        assert 'aria-expanded' in content
        assert 'role="dialog"' in content
        assert 'aria-modal="true"' in content
        assert 'handleKeyDown' in content or 'Escape' in content
        assert 'aria-pressed' in content

    def test_subject_emblem_theme_adaptability(self):
        file_path = WORKSPACE_ROOT / "src" / "components" / "SubjectEmblem.jsx"
        assert file_path.exists()
        content = file_path.read_text(encoding="utf-8")

        assert 'var(--theme-text' in content
        assert 'var(--theme-text-muted' in content
        assert 'aria-label' in content
        assert 'role="img"' in content

    def test_main_layout_dynamic_theme_ambient_glow(self):
        file_path = WORKSPACE_ROOT / "src" / "layouts" / "MainLayout.astro"
        assert file_path.exists()
        content = file_path.read_text(encoding="utf-8")

        assert 'var(--theme-primary' in content
        assert 'var(--theme-bg' in content
        assert 'overflow-x-hidden' in content
        assert '.glass-card' in content
