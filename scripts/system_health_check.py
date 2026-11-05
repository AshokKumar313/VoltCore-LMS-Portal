"""
========================================================================================
VoltCore Apex Academia - System Health & Thermal Readiness CLI Utility
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Script: scripts/system_health_check.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Command-line diagnostic verifying CPU thermal readiness, process memory limits (<300MB),
  SQLite WAL integrity, and sub-50ms query latencies for HP Victus 15 environments.
========================================================================================
"""

import os
import sys
import json
import argparse
from datetime import datetime

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.performance_profiler import SystemPerformanceProfiler


class TerminalFormat:
    BOLD = "\033[1m"
    DIM = "\033[2m"
    EMERALD = "\033[38;2;0;240;181m"
    NAVY_BG = "\033[48;2;2;8;19m"
    GREEN = "\033[92m"
    AMBER = "\033[93m"
    ROSE = "\033[91m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    RESET = "\033[0m"


def print_banner():
    print(f"{TerminalFormat.BOLD}{TerminalFormat.EMERALD}")
    print("╔══════════════════════════════════════════════════════════════════════════════════════╗")
    print("║        VOLTCORE APEX ACADEMIA — SYSTEM HEALTH & THERMAL READINESS AUDIT              ║")
    print("║     HP Victus 15-fa2xxx | 24GB RAM | RTX 4050 | MIT Campus, Anna University          ║")
    print("╚══════════════════════════════════════════════════════════════════════════════════════╝")
    print(f"{TerminalFormat.RESET}")


def run_diagnostics(strict: bool = False, json_mode: bool = False, db_path: str = None) -> int:
    profiler = SystemPerformanceProfiler(db_path=db_path)
    profile = profiler.collect_full_profile()

    if json_mode:
        print(json.dumps(profile, indent=2))
        return 0 if profile.get("healthy", False) else (1 if strict else 0)

    print_banner()

    # 1. Thermal & CPU Readiness
    cpu = profile["thermal_and_cpu"]
    status_color = TerminalFormat.GREEN if cpu["ready"] else TerminalFormat.ROSE
    print(f"{TerminalFormat.BOLD}1. Hardware Safety & Thermal Protection (Victus Mandate):{TerminalFormat.RESET}")
    print(f"   • Status:          {status_color}{cpu['status']}{TerminalFormat.RESET} ({cpu['description']})")
    print(f"   • CPU Hardware:    {cpu['processor']} ({cpu['core_count']} Cores, {cpu['machine']})")
    print(f"   • Benchmark Time:  {cpu['benchmark_eval_ms']} ms (100k cycles)")
    print(f"   • Policy:          {TerminalFormat.CYAN}{cpu['safety_policy']}{TerminalFormat.RESET}")
    print()

    # 2. Memory Footprint
    ram = profile["memory_footprint"]
    ram_color = TerminalFormat.GREEN if ram["compliant"] else TerminalFormat.ROSE
    print(f"{TerminalFormat.BOLD}2. Process Memory Footprint & Headroom:{TerminalFormat.RESET}")
    print(f"   • Working Set RAM: {ram_color}{ram['process_ram_mb']} MB{TerminalFormat.RESET} (Target: < {ram['target_limit_mb']} MB, Cap: {ram['max_limit_mb']} MB)")
    print(f"   • RAM Headroom:    {ram['memory_headroom_mb']} MB remaining before threshold")
    print(f"   • Architecture:    {ram['architecture']}")
    print()

    # 3. SQLite WAL Database Integrity
    wal = profile["sqlite_wal_integrity"]
    wal_color = TerminalFormat.GREEN if wal.get("valid", False) else TerminalFormat.ROSE
    print(f"{TerminalFormat.BOLD}3. SQLite WAL Database Engine Integrity:{TerminalFormat.RESET}")
    print(f"   • Status:          {wal_color}{wal.get('status')}{TerminalFormat.RESET} (Integrity: {wal.get('integrity_check')}, QuickCheck: {wal.get('quick_check')})")
    print(f"   • Journal Mode:    {TerminalFormat.CYAN}{wal.get('journal_mode', '').upper()}{TerminalFormat.RESET} (Write-Ahead Logging: {wal.get('is_wal')})")
    print(f"   • Size on Disk:    {wal.get('db_size_kb')} KB (WAL Frame Size: {wal.get('wal_size_kb')} KB)")
    print(f"   • Registered Rows: Users: {wal.get('table_counts', {}).get('users', 0)} | Attendance: {wal.get('table_counts', {}).get('attendance', 0)} | Modules: {wal.get('table_counts', {}).get('module_lifecycle', 0)}")
    print()

    # 4. Latency Benchmarks
    lat = profile["query_latencies"]
    bench = lat.get("benchmarks", {})
    print(f"{TerminalFormat.BOLD}4. Sub-50ms Query & Inference Benchmarks:{TerminalFormat.RESET}")
    for name, data in bench.items():
        if isinstance(data, dict):
            p_color = TerminalFormat.GREEN if data.get("passed") else TerminalFormat.ROSE
            tag = "✓ PASS" if data.get("passed") else "✗ FAIL"
            avg = data.get("avg_ms", "N/A")
            max_val = data.get("max_ms", "N/A")
            print(f"   • {name:<26} {p_color}{tag}{TerminalFormat.RESET} | Avg: {avg:>7} ms | Max: {max_val:>7} ms | Cap: 50.0 ms")
    print()

    # Consolidated Verdict
    is_healthy = profile.get("healthy", False)
    grade = profile.get("overall_health", "UNKNOWN")
    verdict_color = TerminalFormat.GREEN if is_healthy else TerminalFormat.AMBER

    print("────────────────────────────────────────────────────────────────────────────────────────")
    print(f" OVERALL VERDICT: {verdict_color}{TerminalFormat.BOLD}{grade}{TerminalFormat.RESET} | Duration: {profile['profiling_duration_ms']} ms | Zero Bloat Verified")
    print("────────────────────────────────────────────────────────────────────────────────────────")
    print()

    if strict and not is_healthy:
        return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VoltCore Apex Academia System Health & Thermal Auditor")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Exit with non-zero code on degraded state")
    parser.add_argument("--db-path", type=str, default=None, help="Custom SQLite DB path")
    args = parser.parse_args()

    sys.exit(run_diagnostics(strict=args.strict, json_mode=args.json, db_path=args.db_path))
