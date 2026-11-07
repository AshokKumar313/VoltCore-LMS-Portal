"""
========================================================================================
VoltCore Apex Academia - SQLite WAL Performance & Schema Integrity Enforcer
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: scripts/db_wal_integrity_enforcer.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  1. Creates verified transactional online backups using sqlite3.Connection.backup().
  2. Enforces standard SQLite WAL performance PRAGMAs across all databases:
       - PRAGMA journal_mode = WAL
       - PRAGMA synchronous = NORMAL
       - PRAGMA busy_timeout = 5000
       - PRAGMA foreign_keys = ON
  3. Executes TRUNCATE WAL checkpoints and query optimizer statistics (PRAGMA optimize).
  4. Runs deep integrity checks (integrity_check, quick_check, foreign_key_check).
  5. Evaluates schema catalog synchronization and produces formal audit metrics.
========================================================================================
"""

import os
import sys
import time
import sqlite3
import datetime
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKUP_DIR = os.path.join(BASE_DIR, "backend", "cache", "backups")
LMS_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")
TELEMETRY_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")


def create_verified_backup(src_db_path: str, backup_dir: str = BACKUP_DIR) -> Dict[str, Any]:
    """
    Creates an online, non-blocking transactional backup using SQLite native backup API.
    Verifies destination file size and page integrity.
    """
    if not os.path.isfile(src_db_path):
        return {"status": "SKIPPED", "message": f"Source database not found: {src_db_path}"}

    os.makedirs(backup_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(src_db_path))[0]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{base_name}_backup_{timestamp}.db"
    dest_path = os.path.join(backup_dir, backup_filename)

    src_conn = sqlite3.connect(src_db_path, timeout=10.0)
    dest_conn = sqlite3.connect(dest_path)

    t0 = time.perf_counter()
    with dest_conn:
        src_conn.backup(dest_conn, pages=250)
    dest_conn.close()
    src_conn.close()
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    # Verify backup integrity
    verify_conn = sqlite3.connect(dest_path)
    cur = verify_conn.cursor()
    cur.execute("PRAGMA integrity_check;")
    integrity = cur.fetchone()[0]
    cur.execute("PRAGMA page_count;")
    page_count = cur.fetchone()[0]
    verify_conn.close()

    dest_size = os.path.getsize(dest_path)

    return {
        "status": "SUCCESS" if integrity.lower() == "ok" else "FAILED",
        "source_db": src_db_path,
        "backup_path": dest_path,
        "backup_size_bytes": dest_size,
        "page_count": page_count,
        "integrity": integrity,
        "backup_duration_ms": round(elapsed_ms, 2)
    }


def enforce_wal_and_integrity(db_path: str) -> Dict[str, Any]:
    """
    Applies standard WAL pragmas, runs TRUNCATE checkpoint, and performs integrity audits.
    """
    if not os.path.isfile(db_path):
        return {"status": "SKIPPED", "message": f"Database file not found: {db_path}"}

    conn = sqlite3.connect(db_path, timeout=10.0)
    cur = conn.cursor()

    # 1. Enforce standard production PRAGMAs
    cur.execute("PRAGMA journal_mode = WAL;")
    journal_mode = str(cur.fetchone()[0]).upper()

    cur.execute("PRAGMA synchronous = NORMAL;")
    cur.execute("PRAGMA busy_timeout = 5000;")
    cur.execute("PRAGMA foreign_keys = ON;")

    # Verify pragmas
    cur.execute("PRAGMA synchronous;")
    sync_mode = cur.fetchone()[0]  # 1 = NORMAL, 2 = FULL

    cur.execute("PRAGMA busy_timeout;")
    busy_to = cur.fetchone()[0]

    cur.execute("PRAGMA foreign_keys;")
    fk_enabled = cur.fetchone()[0]

    # 2. Checkpoint WAL and optimize
    cur.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    checkpoint_res = cur.fetchone()

    cur.execute("PRAGMA optimize;")

    # 3. Deep integrity checks
    cur.execute("PRAGMA integrity_check;")
    integrity = str(cur.fetchone()[0])

    cur.execute("PRAGMA quick_check;")
    quick = str(cur.fetchone()[0])

    cur.execute("PRAGMA foreign_key_check;")
    fk_violations = cur.fetchall()

    # 4. Schema catalog inspection
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [r[0] for r in cur.fetchall()]

    table_metrics = {}
    for t in tables:
        try:
            cur.execute(f'SELECT COUNT(*) FROM "{t}";')
            table_metrics[t] = cur.fetchone()[0]
        except Exception as e:
            table_metrics[t] = f"ERROR: {str(e)}"

    cur.close()
    conn.close()

    db_size = os.path.getsize(db_path)
    wal_path = f"{db_path}-wal"
    wal_size = os.path.getsize(wal_path) if os.path.isfile(wal_path) else 0

    return {
        "status": "SUCCESS" if (integrity.lower() == "ok" and len(fk_violations) == 0) else "DEGRADED",
        "db_path": db_path,
        "db_size_bytes": db_size,
        "wal_size_bytes": wal_size,
        "journal_mode": journal_mode,
        "synchronous_mode": "NORMAL" if sync_mode == 1 else str(sync_mode),
        "busy_timeout_ms": busy_to,
        "foreign_keys_enabled": fk_enabled == 1,
        "checkpoint_result": {
            "busy": checkpoint_res[0] if checkpoint_res else 0,
            "log_frames": checkpoint_res[1] if checkpoint_res else 0,
            "checkpointed_frames": checkpoint_res[2] if checkpoint_res else 0
        },
        "integrity_check": integrity,
        "quick_check": quick,
        "foreign_key_violations_count": len(fk_violations),
        "table_count": len(tables),
        "table_metrics": table_metrics
    }


def execute_full_database_hardening() -> Dict[str, Any]:
    """Executes backup, WAL optimization, and integrity enforcement across all project databases."""
    databases = [LMS_DB_PATH, TELEMETRY_DB_PATH]
    
    # Also check test databases if present
    test_dbs = [
        os.path.join(BASE_DIR, "tests", "test_fpga_synthesis.db"),
        os.path.join(BASE_DIR, "tests", "test_peripheral_bus.db")
    ]
    for tdb in test_dbs:
        if os.path.isfile(tdb):
            databases.append(tdb)

    results = {
        "timestamp": datetime.datetime.now().isoformat(),
        "backups": [],
        "enforcements": []
    }

    for db in databases:
        if db in (LMS_DB_PATH, TELEMETRY_DB_PATH):
            bkp = create_verified_backup(db)
            results["backups"].append(bkp)
        enf = enforce_wal_and_integrity(db)
        results["enforcements"].append(enf)

    return results


if __name__ == "__main__":
    report = execute_full_database_hardening()
    print("=" * 80)
    print("VOLTCORE APEX ACADEMIA - DATABASE HARDENING & INTEGRITY REPORT")
    print("=" * 80)
    for b in report["backups"]:
        print(f"BACKUP: {b['source_db']} -> {b['backup_path']} ({b['backup_size_bytes']} bytes, {b['backup_duration_ms']} ms, Integrity: {b['integrity']})")
    print("-" * 80)
    for e in report["enforcements"]:
        print(f"ENFORCED: {e['db_path']}")
        print(f"  Mode: {e['journal_mode']} | Sync: {e['synchronous_mode']} | BusyTimeout: {e['busy_timeout_ms']}ms | ForeignKeys: {e['foreign_keys_enabled']}")
        print(f"  Integrity: {e['integrity_check']} | FK Violations: {e['foreign_key_violations_count']} | Tables: {e['table_count']}")
    print("=" * 80)
