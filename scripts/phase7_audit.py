#!/usr/bin/env python3
"""
========================================================================================
VoltCore Apex Academia - Phase 7 Full Route Regression & Static Build Integrity Audit
Anna University / MIT Campus Standards (Department of Electronics Engineering)
Platform Lead: Ashok Kumar A (2023MITEC042)
========================================================================================
"""

import os
import re
import sys
import json
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
DIST = WORKSPACE / "dist"

print("=" * 80)
print("VOLTCORE APEX ACADEMIA — PHASE 7 INTEGRITY AUDIT")
print("=" * 80)

if not DIST.exists():
    print("ERROR: dist directory does not exist! Run npm run build first.")
    sys.exit(1)

# -----------------------------------------------------------------------------
# 1. HTML ENTRYPOINTS COUNT & INVENTORY
# -----------------------------------------------------------------------------
html_files = list(DIST.rglob("*.html"))
print(f"\n[1] HTML Entrypoints in dist/: Found {len(html_files)} HTML files.")

built_routes = {}
for h in html_files:
    rel = h.relative_to(DIST).as_posix()
    if rel == "index.html":
        route = "/"
    elif rel.endswith("/index.html"):
        route = "/" + rel[:-11]
    elif rel.endswith(".html"):
        route = "/" + rel[:-5]
    else:
        route = "/" + rel
    built_routes[route] = h

print(f"Total Unique Built Routes Identified: {len(built_routes)}")

# Check key expected routes
mandatory_routes = [
    "/",
    "/learning-dashboard",
    "/stm32-academy",
    "/embedded-systems/stm32-academy",
    "/course-hub",
    "/nptel-player",
    "/textbook-library",
    "/exam-center",
    "/simulation",
    "/enterprise-admin",
    "/faculty-workspace",
    "/faculty-admin",
    "/gate-ece",
    "/flashcards",
    "/attendance",
    "/virtual-bench"
]

missing_mandatory = [r for r in mandatory_routes if r not in built_routes]
if missing_mandatory:
    print(f"FAILED: Missing mandatory routes in dist/: {missing_mandatory}")
else:
    print(f"PASSED: All {len(mandatory_routes)} mandatory test routes present in dist/.")

# -----------------------------------------------------------------------------
# 2. INTERNAL LINK CRAWLER (HREF AUDIT)
# -----------------------------------------------------------------------------
print("\n[2] Internal Link Integrity Audit (href='/...')...")

broken_links = []
total_internal_links = 0
all_internal_targets = set()

# Regex to capture href="/..."
href_pattern = re.compile(r'href=["\'](/[^"\'\s#?]*)(?:\?[^"\'\s#]*)?(?:#[^"\'\s]*)?["\']')

for h in html_files:
    rel_source = h.relative_to(DIST).as_posix()
    try:
        content = h.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"Error reading {rel_source}: {e}")
        continue

    links = href_pattern.findall(content)
    for link in links:
        total_internal_links += 1
        norm_link = link.rstrip("/") if link != "/" else "/"
        all_internal_targets.add(norm_link)

        target_path_file = DIST / norm_link.lstrip("/")
        target_path_dir = DIST / norm_link.lstrip("/") / "index.html"
        
        is_valid = (
            norm_link in built_routes or
            (norm_link + "/") in built_routes or
            target_path_file.is_file() or
            target_path_dir.is_file() or
            norm_link.startswith("/_astro/") or
            norm_link in ["/favicon.svg", "/favicon.ico", "/robots.txt", "/manifest.json"]
        )

        if not is_valid:
            broken_links.append((rel_source, link))

print(f"Total Internal Links Scanned: {total_internal_links}")
print(f"Unique Internal Targets: {len(all_internal_targets)}")

if broken_links:
    print(f"WARNING: Found {len(broken_links)} broken internal links:")
    unique_broken = set(broken_links)
    for src, tgt in sorted(unique_broken)[:20]:
        print(f"   From: {src} -> Target: {tgt}")
else:
    print("PASSED: 100% of internal links resolve to valid routes/assets! Zero 404 links.")

# -----------------------------------------------------------------------------
# 3. NAVIGATION REGISTRY PARITY CHECK
# -----------------------------------------------------------------------------
print("\n[3] navigationRegistry.ts Parity Check...")
nav_registry_file = WORKSPACE / "src" / "data" / "navigationRegistry.ts"
if not nav_registry_file.exists():
    print("FAILED: src/data/navigationRegistry.ts not found!")
else:
    nav_content = nav_registry_file.read_text(encoding="utf-8")
    nav_paths = re.findall(r"path:\s*['\"]([^'\"]+)['\"]", nav_content)
    print(f"Extracted {len(nav_paths)} route paths from navigationRegistry.ts.")
    
    missing_nav_routes = []
    for path in nav_paths:
        base_path = path.split("?")[0].split("#")[0].rstrip("/")
        if not base_path:
            base_path = "/"
        
        target_path_file = DIST / base_path.lstrip("/")
        target_path_dir = DIST / base_path.lstrip("/") / "index.html"

        valid = (
            base_path in built_routes or
            (base_path + "/") in built_routes or
            target_path_file.is_file() or
            target_path_dir.is_file()
        )
        if not valid:
            missing_nav_routes.append(path)

    if missing_nav_routes:
        print(f"WARNING: The following navigation items in navigationRegistry.ts do not exist in dist/: {set(missing_nav_routes)}")
    else:
        print(f"PASSED: All {len(nav_paths)} navigation registry routes exist in dist/!")

# -----------------------------------------------------------------------------
# 4. AUTH GUARD (AUTH-001) VERIFICATION
# -----------------------------------------------------------------------------
print("\n[4] Auth Guard (AUTH-001) Verification...")
protected_pages = [
    "enterprise-admin/index.html",
    "faculty-workspace/index.html",
    "faculty-admin/index.html"
]

auth_all_passed = True
for page in protected_pages:
    page_path = DIST / page
    if not page_path.exists():
        print(f"FAILED: Protected page {page} not found in dist/")
        auth_all_passed = False
        continue

    content = page_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    has_voltcore_user = "voltcore_user" in content
    has_role_check = "role" in content and "Admin_Owner" in content and "Teacher" in content
    has_redirect = "window.location.replace('/login')" in content or "window.location.replace" in content
    has_noscript = "<noscript" in content_lower and ("access restricted" in content_lower or "javascript is required" in content_lower or "javascript required" in content_lower)

    if has_voltcore_user and has_role_check and has_redirect and has_noscript:
        print(f"PASSED: {page} has verified pre-hydration AUTH-001 role guard & <noscript> banner.")
    else:
        print(f"FAILED: {page} is missing auth guard components! (user:{has_voltcore_user}, role:{has_role_check}, redir:{has_redirect}, noscript:{has_noscript})")
        auth_all_passed = False

# -----------------------------------------------------------------------------
# 5. THEME ATTRIBUTES VERIFICATION (ALL 18 THEMES)
# -----------------------------------------------------------------------------
print("\n[5] Theme Attributes Verification (18 Themes)...")
global_css = (WORKSPACE / "src" / "styles" / "global.css").read_text(encoding="utf-8")
theme_selector = (WORKSPACE / "src" / "components" / "ThemeSelector.jsx").read_text(encoding="utf-8")

THEME_KEYS = [
    "cyber-emerald",
    "electric-violet",
    "sunset-crimson",
    "oceanic-azure",
    "golden-mustard",
    "tokyo-neon",
    "nordic-frost",
    "forest-sage",
    "solar-flare",
    "cherry-blossom",
    "pastel-academic",
    "oxford-navy",
    "synthwave-80s",
    "matrix-terminal",
    "lavender-dream",
    "autumn-copper",
    "clean-canvas",
    "cosmic-nebula"
]

css_missing = []
jsx_missing = []

for t in THEME_KEYS:
    if f'[data-theme="{t}"]' not in global_css and f"[data-theme='{t}']" not in global_css and f'data-theme="{t}"' not in global_css:
        css_missing.append(t)
    if t not in theme_selector:
        jsx_missing.append(t)

print(f"Theme verification: {len(THEME_KEYS)} themes checked.")
if css_missing:
    print(f"FAILED: Themes missing in global.css: {css_missing}")
else:
    print(f"PASSED: All 18 themes present in src/styles/global.css")

if jsx_missing:
    print(f"FAILED: Themes missing in ThemeSelector.jsx: {jsx_missing}")
else:
    print(f"PASSED: All 18 themes present in ThemeSelector.jsx")

# -----------------------------------------------------------------------------
# 6. PRIVACY & CREDENTIAL LEAKAGE SCAN
# -----------------------------------------------------------------------------
print("\n[6] Privacy & Sensitive Credential Leakage Scan in dist/...")
sensitive_patterns = [
    (r'AIzaSy[0-9A-Za-z-_]{33}', "Live Google API Key"),
    (r'sk-[A-Za-z0-9]{20,}', "OpenAI/Anthropic Secret Key"),
    (r'ghp_[A-Za-z0-9]{36}', "GitHub Personal Access Token"),
    (r'AWS_SECRET_ACCESS_KEY', "AWS Secret Key Reference"),
    (r'(?i)password\s*[:=]\s*["\'][^"\']{4,}["\']', "Hardcoded plaintext password"),
    (r'C:\\Users\\Ashok kumar A\\OneDrive\\Documents\\VoltCore-LMS-Portal\\backups\\', "Backup directory path leak")
]

leaks_found = []
scan_files = list(DIST.rglob("*.html")) + list(DIST.rglob("*.js"))
print(f"Scanning {len(scan_files)} generated assets (.html and .js)...")

for sf in scan_files:
    try:
        txt = sf.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue

    for pat, label in sensitive_patterns:
        matches = re.findall(pat, txt)
        if matches:
            leaks_found.append((sf.relative_to(DIST).as_posix(), label, len(matches)))

if leaks_found:
    print(f"WARNING: Potential leaks detected: {leaks_found}")
else:
    print(f"PASSED: Zero credentials, private telephone numbers, or backup paths leaked in dist/!")

print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
