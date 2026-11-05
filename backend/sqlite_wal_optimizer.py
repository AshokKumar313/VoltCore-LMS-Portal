"""
========================================================================================
VoltCore Apex Academia - SQLite WAL Optimizer & Thread-Safe Connection Pool
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/sqlite_wal_optimizer.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  High-concurrency SQLite optimization engine for Flask and multi-threaded workers.
  Enforces Write-Ahead Logging (WAL), memory-mapped I/O (MMAP), 5-second busy timeout,
  and connection pooling to eliminate database locks under multi-user concurrent loads.
========================================================================================
"""

import os
import time
import queue
import sqlite3
import threading
from contextlib import contextmanager
from typing import Dict, Any, Optional, Tuple, List

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")


class SQLiteConnectionPool:
    """
    Thread-safe connection pool for SQLite in Write-Ahead Logging (WAL) mode.
    Pre-allocates connections with optimized PRAGMA directives for zero lock contention.
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        max_connections: int = 10,
        timeout_seconds: float = 5.0
    ):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.max_connections = max_connections
        self.timeout_seconds = timeout_seconds
        self._pool: queue.Queue = queue.Queue(maxsize=max_connections)
        self._lock = threading.Lock()
        self._created_count = 0

        # Pre-seed half the pool for fast startup
        initial_seed = max(2, max_connections // 2)
        for _ in range(initial_seed):
            conn = self._create_optimized_connection()
            self._pool.put(conn)
            self._created_count += 1

    def _create_optimized_connection(self) -> sqlite3.Connection:
        """
        Creates a single SQLite connection tuned for high concurrent throughput.
        """
        conn = sqlite3.connect(
            self.db_path,
            timeout=self.timeout_seconds,
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row

        cur = conn.cursor()
        # 1. Write-Ahead Logging: enables concurrent readers alongside 1 writer
        cur.execute("PRAGMA journal_mode = WAL;")
        # 2. Synchronous Normal: safe in WAL mode, eliminates disk sync bottlenecks
        cur.execute("PRAGMA synchronous = NORMAL;")
        # 3. Busy timeout: wait up to 5,000ms if a write transaction is committing
        cur.execute("PRAGMA busy_timeout = 5000;")
        # 4. Cache size: 8MB in-memory page cache (negative = KB)
        cur.execute("PRAGMA cache_size = -8000;")
        # 5. Memory-mapped I/O: 32MB zero-copy reads
        cur.execute("PRAGMA mmap_size = 33554432;")
        # 6. Store temp tables and indexes in memory
        cur.execute("PRAGMA temp_store = MEMORY;")
        cur.close()

        return conn

    @contextmanager
    def get_connection(self):
        """
        Context manager to acquire and return a connection safely.
        Usage:
            with pool.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT ...")
        """
        conn = None
        try:
            # Try to fetch from pool, or create on demand up to max_connections
            try:
                conn = self._pool.get(block=True, timeout=self.timeout_seconds)
            except queue.Empty:
                with self._lock:
                    if self._created_count < self.max_connections:
                        conn = self._create_optimized_connection()
                        self._created_count += 1
                    else:
                        raise sqlite3.OperationalError(
                            "SQLiteConnectionPool exhausted: all connections currently active"
                        )
            yield conn
        finally:
            if conn is not None:
                try:
                    # Roll back any dangling open transaction before returning to pool
                    if conn.in_transaction:
                        conn.rollback()
                except Exception:
                    pass
                self._pool.put(conn)

    def close_all(self):
        """Closes all pooled connections."""
        with self._lock:
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    conn.close()
                except Exception:
                    pass
            self._created_count = 0


def execute_wal_checkpoint(
    db_path: Optional[str] = None,
    mode: str = "PASSIVE"
) -> Dict[str, Any]:
    """
    Executes a WAL checkpoint operation.
    Modes:
      - PASSIVE: Checkpoints as many frames as possible without waiting for readers.
      - FULL: Waits for readers to complete and checkpoints all frames.
      - RESTART: Checkpoints all frames and restarts the WAL file from frame 1.
      - TRUNCATE: Like RESTART, but truncates the WAL file to zero bytes.
    """
    target_db = db_path or DEFAULT_DB_PATH
    valid_modes = {"PASSIVE", "FULL", "RESTART", "TRUNCATE"}
    selected_mode = mode.upper() if mode.upper() in valid_modes else "PASSIVE"

    try:
        conn = sqlite3.connect(target_db, timeout=5.0)
        cur = conn.cursor()
        cur.execute(f"PRAGMA wal_checkpoint({selected_mode});")
        res = cur.fetchone()  # (busy, log_frames, checkpointed_frames)
        conn.close()

        busy, log_frames, checkpointed_frames = res if res else (0, 0, 0)
        success = busy == 0

        return {
            "status": "SUCCESS" if success else "BUSY",
            "mode": selected_mode,
            "busy": busy,
            "log_frames": log_frames,
            "checkpointed_frames": checkpointed_frames,
            "all_checkpointed": log_frames == checkpointed_frames
        }
    except Exception as exc:
        return {
            "status": "ERROR",
            "mode": selected_mode,
            "error": str(exc),
            "all_checkpointed": False
        }


def get_wal_statistics(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Returns database size, WAL file presence, and frame stats."""
    target_db = db_path or DEFAULT_DB_PATH
    wal_file = f"{target_db}-wal"
    shm_file = f"{target_db}-shm"

    db_size = os.path.getsize(target_db) if os.path.isfile(target_db) else 0
    wal_size = os.path.getsize(wal_file) if os.path.isfile(wal_file) else 0
    shm_size = os.path.getsize(shm_file) if os.path.isfile(shm_file) else 0

    return {
        "db_path": target_db,
        "db_size_kb": round(db_size / 1024.0, 2),
        "wal_exists": os.path.isfile(wal_file),
        "wal_size_kb": round(wal_size / 1024.0, 2),
        "shm_exists": os.path.isfile(shm_file),
        "shm_size_kb": round(shm_size / 1024.0, 2)
    }


# Global singleton pool for application-wide use
sqlite_pool = SQLiteConnectionPool()

