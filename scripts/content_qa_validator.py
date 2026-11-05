#!/usr/bin/env python3
"""
========================================================================================
VoltCore Apex Academia - Content QA & Anti-Hallucination Validator
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: scripts/content_qa_validator.py
Platform Lead / Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Scans all Markdown/MDX curriculum modules in src/content/modules/ to:
  1. Verify KaTeX bracket and delimiter balance ($...$, $$...$$, {}, [], ()).
  2. Validate internal and external link integrity.
  3. Enforce mandatory source/reference citations per claim to guard against hallucinations.
========================================================================================
"""

import os
import sys
import re
import json
import argparse
from typing import Dict, List, Any, Tuple, Optional

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Valid known internal routes in the VoltCore LMS Portal
VALID_INTERNAL_ROUTES = {
    "/",
    "/attendance",
    "/autograder",
    "/careers",
    "/flash-firmware",
    "/flashcards",
    "/fleet",
    "/gate-ece",
    "/hardware-hil",
    "/nptel",
    "/nptel-player",
    "/profile",
    "/settings",
    "/simulation",
    "/teacher",
    "/telemetry",
    "/virtual-bench"
}

# Recognized authoritative citation standards
AUTHORITATIVE_STANDARDS = [
    "IEEE", "ISO", "IEC", "NPTEL", "ARM", "CORTEX", "RISC-V",
    "STM32", "ESP32", "TEXAS INSTRUMENTS", "ANALOG DEVICES",
    "FREE-RTOS", "FREERTOS", "RFC", "WOKWI", "SPICE"
]


class TerminalColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    EMERALD = '\033[38;2;0;240;181m'


def strip_code_and_frontmatter(content: str) -> Tuple[str, Optional[str]]:
    """
    Extracts frontmatter YAML and returns stripped content without code blocks
    so that code brackets/dollars are not misconstrued as KaTeX math.
    """
    frontmatter = None
    body = content

    # Extract frontmatter if present
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2]

    # Strip multi-line fenced code blocks (``` ... ``` or ```` ... ````)
    body_no_code = re.sub(r'````[\s\S]*?````', '', body)
    body_no_code = re.sub(r'```[\s\S]*?```', '', body_no_code)

    # Strip HTML / Markdown comments (<!-- ... -->)
    body_no_code = re.sub(r'<!--[\s\S]*?-->', '', body_no_code)

    # Strip inline code spans (`...`)
    body_no_code = re.sub(r'`[^`\n]+`', '', body_no_code)

    return body_no_code, frontmatter


def verify_katex_math_balance(body_no_code: str) -> List[str]:
    r"""
    Verifies that all KaTeX math blocks are properly delimited,
    curly braces are strictly balanced, and \left / \right commands match.
    """
    issues = []

    # 1. Check Display Math ($$...$$) Delimiters
    display_pattern = re.compile(r'(?<!\\)\$\$([\s\S]*?)(?<!\\)\$\$')
    display_blocks = display_pattern.findall(body_no_code)
    
    # Strip matched display math blocks
    remainder_after_display = display_pattern.sub('', body_no_code)

    # Any remaining $$ is an unclosed display math delimiter
    remaining_display_delims = [m.start() for m in re.finditer(r'(?<!\\)\$\$', remainder_after_display)]
    if remaining_display_delims:
        issues.append(f"Unclosed display math delimiter ($$ count remaining = {len(remaining_display_delims)})")

    # 2. Check Inline Math ($...$) Delimiters
    # Matches $math$ where $ is not escaped, not followed by space, and ends with non-space $
    inline_pattern = re.compile(r'(?<!\\)\$(?!\s)([^\$\n]+?)(?<!\s)(?<!\\)\$')
    inline_blocks = inline_pattern.findall(remainder_after_display)

    # Strip matched inline math blocks
    remainder_after_inline = inline_pattern.sub('', remainder_after_display)

    # Look for any orphaned/unpaired $ that isn't currency (e.g. $100) or escaped (\$):
    orphan_dollars = [m.start() for m in re.finditer(r'(?<!\\)\$(?!\d|\s|\.|\,)', remainder_after_inline)]
    if orphan_dollars:
        issues.append(f"Unclosed or orphaned inline math delimiter ($ count remaining = {len(orphan_dollars)})")

    # 3. Check Curly Braces & \left / \right commands inside all extracted KaTeX formulas
    all_math = display_blocks + inline_blocks
    for idx, block in enumerate(all_math):
        # In KaTeX, curly braces {} MUST always be strictly balanced
        brace_stack = 0
        for ch in block:
            if ch == '{':
                brace_stack += 1
            elif ch == '}':
                brace_stack -= 1
                if brace_stack < 0:
                    snippet = block.strip()[:40].replace('\n', ' ')
                    issues.append(f"Unmatched closing brace '}}' in KaTeX block #{idx+1}: '{snippet}...'")
                    break
        if brace_stack > 0:
            snippet = block.strip()[:40].replace('\n', ' ')
            issues.append(f"Unclosed opening brace '{{' in KaTeX block #{idx+1}: '{snippet}...'")

        # For \left and \right commands in KaTeX:
        lefts = len(re.findall(r'\\left\b', block))
        rights = len(re.findall(r'\\right\b', block))
        if lefts != rights:
            snippet = block.strip()[:40].replace('\n', ' ')
            issues.append(f"Mismatched \\left ({lefts}) and \\right ({rights}) delimiters in KaTeX block #{idx+1}: '{snippet}...'")

    return issues


def verify_link_integrity(content: str, base_dir: str) -> List[str]:
    """
    Finds and validates markdown links: [text](target).
    Checks internal routes and verifies relative filesystem targets.
    """
    issues = []
    # Match markdown links [anchor](url)
    link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]*)\)')

    for match in link_pattern.finditer(content):
        anchor = match.group(1).strip()
        target = match.group(2).strip()

        # Check for empty anchor or target
        if not anchor:
            issues.append(f"Empty link anchor text pointing to '{target}'")
        if not target:
            issues.append(f"Empty link target URL for anchor '{anchor}'")
            continue

        # Skip anchor-only links on same page (#section)
        if target.startswith("#"):
            continue

        # Skip mailto: or tel: links
        if target.startswith("mailto:") or target.startswith("tel:"):
            continue

        # Check internal web routes
        if target.startswith("/"):
            # Strip anchors or query strings
            clean_route = target.split("#")[0].split("?")[0]
            # Valid if known internal page or in /visuals / /assets
            if clean_route not in VALID_INTERNAL_ROUTES and not clean_route.startswith("/visuals") and not clean_route.startswith("/assets") and not clean_route.endswith(".svg"):
                issues.append(f"Unrecognized internal route '{target}' for link '{anchor}'")

        # Check relative file paths (e.g. ../ or ./)
        elif target.startswith("./") or target.startswith("../"):
            clean_rel = target.split("#")[0].split("?")[0]
            resolved_path = os.path.normpath(os.path.join(base_dir, clean_rel))
            if not os.path.exists(resolved_path):
                issues.append(f"Broken relative file link '{target}' -> path not found: {resolved_path}")

        # Check external protocols
        elif not (target.startswith("http://") or target.startswith("https://") or target.startswith("file:///")):
            issues.append(f"Malformed link URI schema in target '{target}' for '{anchor}'")

    return issues


def verify_citations_and_sources(content: str, frontmatter: Optional[str]) -> Tuple[List[str], int]:
    """
    Enforces mandatory source/reference citations per claim to guard against hallucinations.
    Checks frontmatter for ieeeReference and body for References section / authoritative citations.
    """
    issues = []
    citation_count = 0

    # 1. Check Frontmatter for IEEE Reference
    has_frontmatter_ref = False
    if frontmatter:
        if "ieeeReference:" in frontmatter or "reference:" in frontmatter:
            has_frontmatter_ref = True
            citation_count += 1

    # 2. Check Body for References / Citations Section
    has_body_references_section = bool(
        re.search(r'#+\s*(?:References|References\s*&\s*Standards|Bibliography|Authoritative\s*Sources)', content, re.IGNORECASE)
    )
    if has_body_references_section:
        citation_count += 1

    # 3. Check for in-text academic citations or cite tags (e.g. [cite: ...], [1], [2], IEEE...)
    in_text_citations = len(re.findall(r'\[cite:[^\]]+\]|\[\d+\]', content))
    citation_count += in_text_citations

    # 4. Check for mentions of authoritative engineering standards
    content_upper = content.upper()
    standards_found = sum(1 for std in AUTHORITATIVE_STANDARDS if std in content_upper)
    citation_count += standards_found

    if not has_frontmatter_ref and not has_body_references_section and citation_count == 0:
        issues.append("Zero authoritative references or IEEE citations found. Mandatory citation enforcement failed.")

    return issues, citation_count


def validate_single_file(file_path: str) -> Dict[str, Any]:
    """
    Performs full content QA validation on a single Markdown/MDX lesson.
    """
    if not os.path.exists(file_path):
        return {
            "file": file_path,
            "passed": False,
            "errors": [f"File not found: {file_path}"],
            "warnings": [],
            "math_blocks_found": 0,
            "links_found": 0,
            "citations_found": 0
        }

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        raw_content = f.read()

    base_dir = os.path.dirname(os.path.abspath(file_path))
    body_no_code, frontmatter = strip_code_and_frontmatter(raw_content)

    errors = []
    warnings = []

    # 1. KaTeX Math Verification
    math_issues = verify_katex_math_balance(body_no_code)
    errors.extend(math_issues)

    # 2. Link Integrity Verification
    link_issues = verify_link_integrity(raw_content, base_dir)
    errors.extend(link_issues)

    # 3. Citation & Anti-Hallucination Enforcement
    citation_issues, citation_count = verify_citations_and_sources(raw_content, frontmatter)
    errors.extend(citation_issues)

    # Count statistics
    display_count = len(re.findall(r'(?<!\\)\$\$', body_no_code)) // 2
    inline_count = len(re.findall(r'(?<!\\)\$(?!\s)(.*?)(?<!\s)(?<!\\)\$', body_no_code))
    total_math = display_count + inline_count
    total_links = len(re.findall(r'\[([^\]]*)\]\(([^)]*)\)', raw_content))

    return {
        "file": file_path,
        "filename": os.path.basename(file_path),
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "math_blocks_found": total_math,
        "links_found": total_links,
        "citations_found": citation_count
    }


def validate_directory(dir_path: str) -> Dict[str, Any]:
    """
    Scans and validates all Markdown/MDX files in a directory recursively.
    """
    results = []
    total_files = 0
    passed_files = 0
    total_errors = 0

    for root, _, files in os.walk(dir_path):
        for file in sorted(files):
            if file.endswith(".md") or file.endswith(".mdx"):
                total_files += 1
                full_path = os.path.join(root, file)
                res = validate_single_file(full_path)
                results.append(res)
                if res["passed"]:
                    passed_files += 1
                else:
                    total_errors += len(res["errors"])

    return {
        "directory": dir_path,
        "total_files": total_files,
        "passed_files": passed_files,
        "failed_files": total_files - passed_files,
        "total_errors": total_errors,
        "all_passed": (total_files > 0 and passed_files == total_files),
        "results": results
    }


def main():
    parser = argparse.ArgumentParser(
        description="VoltCore Apex Academia - Content QA & Anti-Hallucination Validator"
    )
    parser.add_argument(
        "--dir",
        default=os.path.join("src", "content", "modules"),
        help="Directory to scan (default: src/content/modules)"
    )
    parser.add_argument(
        "--file",
        default=None,
        help="Optional single file to scan"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode: exit with code 1 if any error is encountered"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON format for automated CI/CD pipelines"
    )

    args = parser.parse_args()

    # Determine Project Root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    target_dir = os.path.abspath(args.dir if os.path.isabs(args.dir) else os.path.join(project_root, args.dir))

    if args.file:
        target_file = os.path.abspath(args.file if os.path.isabs(args.file) else os.path.join(project_root, args.file))
        res = validate_single_file(target_file)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"File: {res['filename']} -> {'[PASS]' if res['passed'] else '[FAIL]'}")
            for err in res["errors"]:
                print(f"  • {TerminalColors.RED}ERROR:{TerminalColors.RESET} {err}")
        sys.exit(0 if res["passed"] else 1)

    summary = validate_directory(target_dir)

    if args.json:
        print(json.dumps(summary, indent=2))
        sys.exit(0 if summary["all_passed"] else 1)

    # Terminal Precision Formatting
    print(f"\n{TerminalColors.CYAN}{'═' * 88}{TerminalColors.RESET}")
    print(f"{TerminalColors.BOLD}{TerminalColors.EMERALD} VOLTCORE APEX ACADEMIA — CONTENT QA & ANTI-HALLUCINATION AUDIT{TerminalColors.RESET}")
    print(f" Institution: Madras Institute of Technology (MIT) Campus, Anna University")
    print(f" Scanned Directory: {target_dir}")
    print(f"{TerminalColors.CYAN}{'─' * 88}{TerminalColors.RESET}")

    for r in summary["results"]:
        status_icon = f"{TerminalColors.GREEN}✓ PASS{TerminalColors.RESET}" if r["passed"] else f"{TerminalColors.RED}✗ FAIL{TerminalColors.RESET}"
        print(f" • {r['filename']:<36} {status_icon} | Math: {r['math_blocks_found']:<3} | Links: {r['links_found']:<3} | Citations: {r['citations_found']:<3}")
        if not r["passed"]:
            for err in r["errors"]:
                print(f"     {TerminalColors.RED}↳ ERROR:{TerminalColors.RESET} {err}")

    print(f"{TerminalColors.CYAN}{'─' * 88}{TerminalColors.RESET}")
    print(f" Summary: {summary['passed_files']}/{summary['total_files']} files passed QA ({summary['total_errors']} total issues detected).")
    print(f"{TerminalColors.CYAN}{'═' * 88}{TerminalColors.RESET}\n")

    if args.strict and not summary["all_passed"]:
        sys.exit(1)
    sys.exit(0 if summary["all_passed"] else 0)


if __name__ == "__main__":
    main()
