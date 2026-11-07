"""
========================================================================================
VoltCore Apex Academia - PWA Offline Learning Synchronization Engine
Module: backend/offline_sync_engine.py
Platform Lead: Ashok Kumar A
Standards: Autonomous Engineering Cluster • Offline-First PWA • Idempotent Replay
Architecture: SQLite WAL Mode • Conflict Resolution • Passive CPU Footprint
========================================================================================
"""

import os
import json
import sqlite3
import datetime
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")


class OfflineSyncEngine:
    """
    PWA Offline Learning Synchronization Engine:
      - Ingests spooled offline quiz submissions, lab reports, and reading progress
      - Implements idempotent deduplication via client_event_id
      - Resolves state conflicts using client vs server timestamp reconciliation
      - Commits atomic transactions into SQLite WAL mode
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self):
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS offline_sync_events (
                    event_id TEXT PRIMARY KEY,
                    client_event_id TEXT UNIQUE NOT NULL,
                    student_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    resource_id TEXT,
                    payload_json TEXT NOT NULL,
                    client_timestamp TEXT NOT NULL,
                    server_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sync_status TEXT NOT NULL,
                    conflict_notes TEXT,
                    xp_awarded INTEGER DEFAULT 0
                );
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS offline_sync_ledger (
                    resource_id TEXT PRIMARY KEY,
                    resource_type TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    version_seq INTEGER DEFAULT 1,
                    data_json TEXT NOT NULL,
                    last_client_timestamp TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
        finally:
            conn.close()

    # ---------------------------------------------------------------------------
    # BATCH SYNC INGESTION & IDEMPOTENT RESOLUTION
    # ---------------------------------------------------------------------------

    def process_sync_batch(
        self,
        student_id: str,
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Processes a batch of spooled offline events atomically.
        Guarantees idempotency and conflict resolution.
        """
        if not events:
            return {
                "status": "SUCCESS",
                "synced_count": 0,
                "duplicates_skipped": 0,
                "conflicts_resolved": 0,
                "total_xp_awarded": 0,
                "details": []
            }

        conn = self._get_connection()
        synced_count = 0
        duplicates_skipped = 0
        conflicts_resolved = 0
        total_xp = 0
        details = []

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            for ev in events:
                client_ev_id = ev.get("client_event_id") or f"CLIENT_EV_{os.urandom(6).hex()}"
                ev_type = ev.get("event_type", "CHAPTER_PROGRESS").upper()
                res_id = ev.get("resource_id", "GENERIC_RES")
                payload = ev.get("payload", {})
                client_ts = ev.get("client_timestamp", now_str)

                # 1. Idempotency Check: Was this client_event_id already synced?
                cur = conn.cursor()
                cur.execute(
                    "SELECT event_id, sync_status FROM offline_sync_events WHERE client_event_id = ?;",
                    (client_ev_id,)
                )
                existing = cur.fetchone()
                if existing:
                    duplicates_skipped += 1
                    details.append({
                        "client_event_id": client_ev_id,
                        "status": "ALREADY_SYNCED",
                        "server_event_id": existing[0]
                    })
                    continue

                # 2. Conflict Detection against offline_sync_ledger
                cur.execute(
                    "SELECT version_seq, data_json, last_client_timestamp FROM offline_sync_ledger WHERE resource_id = ?;",
                    (res_id,)
                )
                ledger_row = cur.fetchone()

                sync_status = "SYNCED"
                conflict_notes = "Clean synchronization."
                xp = int(ev.get("xp_reward", 25))

                if ledger_row:
                    v_seq, prev_data, prev_ts = ledger_row
                    # If incoming client timestamp is older than existing ledger timestamp
                    if client_ts < prev_ts:
                        sync_status = "CONFLICT_RESOLVED_SERVER_PRESERVED"
                        conflict_notes = f"Incoming offline change ({client_ts}) was older than server version ({prev_ts}). Merged metadata."
                        conflicts_resolved += 1
                    else:
                        sync_status = "CONFLICT_RESOLVED_CLIENT_WIN"
                        conflict_notes = f"Incoming offline change ({client_ts}) was newer than server version ({prev_ts}). Overwrote ledger."
                        conflicts_resolved += 1
                        conn.execute("""
                            UPDATE offline_sync_ledger
                            SET version_seq = version_seq + 1, data_json = ?, last_client_timestamp = ?, updated_at = ?
                            WHERE resource_id = ?;
                        """, (json.dumps(payload), client_ts, now_str, res_id))
                else:
                    # New record in ledger
                    conn.execute("""
                        INSERT INTO offline_sync_ledger
                        (resource_id, resource_type, student_id, version_seq, data_json, last_client_timestamp, updated_at)
                        VALUES (?, ?, ?, 1, ?, ?, ?);
                    """, (res_id, ev_type, student_id, json.dumps(payload), client_ts, now_str))

                # Insert into events log
                server_ev_id = f"SYNC_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}_{os.urandom(2).hex()}"
                conn.execute("""
                    INSERT INTO offline_sync_events
                    (event_id, client_event_id, student_id, event_type, resource_id,
                     payload_json, client_timestamp, server_timestamp, sync_status, conflict_notes, xp_awarded)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    server_ev_id, client_ev_id, student_id, ev_type, res_id,
                    json.dumps(payload), client_ts, now_str, sync_status, conflict_notes, xp
                ))

                synced_count += 1
                total_xp += xp
                details.append({
                    "client_event_id": client_ev_id,
                    "server_event_id": server_ev_id,
                    "status": sync_status,
                    "xp_awarded": xp,
                    "conflict_notes": conflict_notes
                })

            conn.commit()
        finally:
            conn.close()

        return {
            "status": "SUCCESS",
            "student_id": student_id,
            "synced_count": synced_count,
            "duplicates_skipped": duplicates_skipped,
            "conflicts_resolved": conflicts_resolved,
            "total_xp_awarded": total_xp,
            "processed_at": now_str,
            "details": details
        }

    # ---------------------------------------------------------------------------
    # SYNC STATUS & HISTORY QUERY
    # ---------------------------------------------------------------------------

    def get_sync_status(self, student_id: str) -> Dict[str, Any]:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT COUNT(*),
                       SUM(CASE WHEN sync_status = 'SYNCED' THEN 1 ELSE 0 END),
                       SUM(CASE WHEN sync_status LIKE 'CONFLICT_%' THEN 1 ELSE 0 END),
                       SUM(xp_awarded),
                       MAX(server_timestamp)
                FROM offline_sync_events
                WHERE student_id = ?;
            """, (student_id,))
            row = cur.fetchone()

            total_events = row[0] or 0
            clean_synced = row[1] or 0
            conflicts = row[2] or 0
            total_xp = row[3] or 0
            last_sync = row[4] or "No previous synchronization"

            # Query recent 10 sync events
            cur.execute("""
                SELECT event_id, event_type, resource_id, sync_status, xp_awarded, server_timestamp
                FROM offline_sync_events
                WHERE student_id = ?
                ORDER BY server_timestamp DESC LIMIT 10;
            """, (student_id,))
            recent_rows = cur.fetchall()
            recent_events = [{
                "event_id": r[0],
                "event_type": r[1],
                "resource_id": r[2],
                "sync_status": r[3],
                "xp_awarded": r[4],
                "timestamp": r[5]
            } for r in recent_rows]

            return {
                "status": "SUCCESS",
                "student_id": student_id,
                "total_events_synced": total_events,
                "clean_synced": clean_synced,
                "conflicts_resolved": conflicts,
                "total_xp_accumulated": total_xp,
                "last_sync_timestamp": last_sync,
                "recent_events": recent_events
            }
        finally:
            conn.close()


offline_sync_engine = OfflineSyncEngine()
