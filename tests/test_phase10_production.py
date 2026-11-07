"""
========================================================================================
VoltCore Apex Academia - Phase 10 Production Test Suite
Target: Cloud Containerization, Automated CI/CD, SQLite WAL Optimizer & Health Suite
Lead Systems Architect: Ashok Kumar A
Machine Target: HP Victus (LAPTOP-3NEGBVLE) — Whisper-Quiet, Passive CPU (<5%)
Standards: Autonomous Engineering Cluster • Low-Overhead Production • Zero Data Loss WAL
========================================================================================
"""

import os
import json
import time
import pytest
import sqlite3
import threading
from io import BytesIO

# Import Phase 10 backend components
from backend.sqlite_wal_optimizer import (
    SQLiteConnectionPool,
    sqlite_pool,
    execute_wal_checkpoint,
    get_wal_statistics,
    check_database_health,
    get_system_health_status
)

TEST_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_phase10_production.db")


@pytest.fixture(autouse=True)
def clean_test_db():
    """Ensure clean isolated SQLite database for Phase 10 Production tests."""
    for path in [TEST_DB_PATH, f"{TEST_DB_PATH}-wal", f"{TEST_DB_PATH}-shm"]:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass
    yield
    for path in [TEST_DB_PATH, f"{TEST_DB_PATH}-wal", f"{TEST_DB_PATH}-shm"]:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass


# ========================================================================================
# 1. DOCKER MULTI-STAGE BUILD CONFIGURATION & SYNTAX
# ========================================================================================

def test_docker_multistage_dockerfile_syntax():
    """Verifies that the root Dockerfile implements a production-grade multi-stage build."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dockerfile_path = os.path.join(base_dir, "Dockerfile")

    assert os.path.isfile(dockerfile_path), "Root Dockerfile must exist for cloud containerization."

    with open(dockerfile_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Stage 1: Frontend build stage
    assert "FROM node:20-alpine AS frontend-builder" in content
    assert "npm run build" in content

    # Stage 2: Python production runtime stage
    assert "FROM python:3.12-slim AS production-runner" in content or "FROM python:" in content
    assert "COPY --from=frontend-builder /app/dist /app/dist" in content

    # Persistent WAL storage & port exposure
    assert 'VOLUME ["/app/data"]' in content or "VOLUME" in content
    assert "EXPOSE 5000" in content
    assert "HEALTHCHECK" in content
    assert "attendance_server.py" in content


# ========================================================================================
# 2. DOCKER COMPOSE CONFIGURATION & PERSISTENT STORAGE
# ========================================================================================

def test_docker_compose_production_structure():
    """Verifies docker-compose.yml defines services, healthcheck, and persistent volume mappings."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    compose_path = os.path.join(base_dir, "docker-compose.yml")

    assert os.path.isfile(compose_path), "docker-compose.yml must exist."

    with open(compose_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify services
    assert "api:" in content
    assert "web:" in content
    assert "cache:" in content

    # Verify multi-stage build target
    assert "dockerfile: Dockerfile" in content

    # Verify persistent volume mappings for SQLite WAL logs
    assert "voltcore_db_data:/app/data" in content
    assert "voltcore_db_data:" in content

    # Verify healthcheck configured
    assert "healthcheck:" in content
    assert "/api/system/health" in content


# ========================================================================================
# 3. SQLITE WAL CHECKPOINTING MODES & DIAGNOSTICS
# ========================================================================================

def test_sqlite_wal_checkpoint_modes():
    """Verifies all SQLite WAL checkpoint routines (PASSIVE, FULL, RESTART, TRUNCATE)."""
    # Initialize test DB in WAL mode
    conn = sqlite3.connect(TEST_DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("CREATE TABLE test_telemetry (id INTEGER PRIMARY KEY, msg TEXT);")
    for i in range(25):
        conn.execute("INSERT INTO test_telemetry (msg) VALUES (?);", (f"Frame {i}",))
    conn.commit()
    conn.close()

    # 1. Test PASSIVE mode checkpoint
    res_passive = execute_wal_checkpoint(TEST_DB_PATH, mode="PASSIVE")
    assert res_passive["status"] in ("SUCCESS", "BUSY")
    assert res_passive["mode"] == "PASSIVE"
    assert "log_frames" in res_passive
    assert "checkpointed_frames" in res_passive

    # 2. Test FULL mode checkpoint
    res_full = execute_wal_checkpoint(TEST_DB_PATH, mode="FULL")
    assert res_full["status"] == "SUCCESS"
    assert res_full["mode"] == "FULL"

    # 3. Test RESTART mode checkpoint
    res_restart = execute_wal_checkpoint(TEST_DB_PATH, mode="RESTART")
    assert res_restart["status"] == "SUCCESS"
    assert res_restart["mode"] == "RESTART"

    # 4. Test TRUNCATE mode checkpoint
    res_trunc = execute_wal_checkpoint(TEST_DB_PATH, mode="TRUNCATE")
    assert res_trunc["status"] == "SUCCESS"
    assert res_trunc["mode"] == "TRUNCATE"

    # 5. Verify WAL statistics
    stats = get_wal_statistics(TEST_DB_PATH)
    assert stats["db_path"] == TEST_DB_PATH
    assert stats["db_size_kb"] > 0


# ========================================================================================
# 4. AUTOMATED DATABASE HEALTH MONITOR
# ========================================================================================

def test_sqlite_wal_health_monitor():
    """Verifies that check_database_health() verifies WAL mode, integrity, and busy timeout."""
    # Pre-seed DB
    conn = sqlite3.connect(TEST_DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("CREATE TABLE health_check_tab (k TEXT PRIMARY KEY, v TEXT);")
    conn.execute("INSERT INTO health_check_tab VALUES ('status', 'optimal');")
    conn.commit()
    conn.close()

    health = check_database_health(TEST_DB_PATH)
    assert health["status"] == "HEALTHY"
    assert health["journal_mode"] == "WAL"
    assert health["is_wal_mode"] is True
    assert health["integrity_check"] == "ok"
    assert health["quick_check"] == "ok"
    assert health["page_count"] > 0
    assert health["page_size_bytes"] > 0
    assert health["is_healthy"] is True


# ========================================================================================
# 5. THREAD-SAFE CONNECTION POOL & CONCURRENCY
# ========================================================================================

def test_sqlite_connection_pool_concurrency():
    """Verifies thread-safe connection acquisition without lock contention across threads."""
    pool = SQLiteConnectionPool(db_path=TEST_DB_PATH, max_connections=4, timeout_seconds=5.0)

    # Initialize schema
    with pool.get_connection() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS counter (id INTEGER PRIMARY KEY, val INTEGER);")
        conn.execute("INSERT OR REPLACE INTO counter (id, val) VALUES (1, 0);")
        conn.commit()

    errors = []

    def worker_increment(worker_id: int):
        try:
            for _ in range(5):
                with pool.get_connection() as c:
                    cur = c.cursor()
                    cur.execute("UPDATE counter SET val = val + 1 WHERE id = 1;")
                    c.commit()
        except Exception as e:
            errors.append((worker_id, str(e)))

    threads = [threading.Thread(target=worker_increment, args=(i,)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Thread pool concurrent errors encountered: {errors}"

    # Verify final counter value is 20 (4 threads * 5 increments)
    with pool.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT val FROM counter WHERE id = 1;")
        total = cur.fetchone()[0]
        assert total == 20

    pool.close_all()


# ========================================================================================
# 6. SYSTEM HEALTH STATUS & THERMAL PROFILE AGGREGATION
# ========================================================================================

def test_system_health_status_aggregation():
    """Verifies comprehensive production health report covering database, threads, and thermal status."""
    report = get_system_health_status(TEST_DB_PATH)

    assert report["status"] == "HEALTHY"
    assert report["platform"] == "VoltCore Apex Academia"
    assert "sqlite_wal" in report
    assert report["sqlite_wal"]["is_wal_mode"] is True

    # Verify thread pool metrics
    assert "thread_pool" in report
    assert report["thread_pool"]["pool_healthy"] is True
    assert report["thread_pool"]["active_threads"] >= 1

    # Verify thermal guard metrics
    assert "thermal_guard" in report
    thermal = report["thermal_guard"]
    assert thermal["thermal_status"] == "NOMINAL"
    assert thermal["cpu_load_target"] == "<5%"
    assert thermal["fan_profile"] == "Whisper-Quiet"
    assert thermal["hardware_target"] == "HP Victus (LAPTOP-3NEGBVLE)"


# ========================================================================================
# 7. HTTP SERVER HEALTH ENDPOINT ROUTING (MOCK REQUEST HANDLER)
# ========================================================================================

def test_attendance_server_system_health_endpoint():
    """Verifies attendance_server.py dispatches /api/system/health and /api/health."""
    from attendance_server import FallbackHTTPHandler

    class DummyServer:
        pass

    class MockSocket:
        def __init__(self, data):
            self.data = data
            self.output = BytesIO()

        def makefile(self, mode, *args, **kwargs):
            if 'r' in mode:
                return BytesIO(self.data)
            return self.output

        def sendall(self, b):
            self.output.write(b)

    # 1. Test GET /api/system/health
    req_sys_health = b"GET /api/system/health HTTP/1.1\r\nHost: localhost\r\n\r\n"
    sock_sys_health = MockSocket(req_sys_health)
    FallbackHTTPHandler(sock_sys_health, ("127.0.0.1", 5000), DummyServer())
    resp_sys_health = sock_sys_health.output.getvalue().decode("utf-8")
    assert "200 OK" in resp_sys_health
    assert "VoltCore Apex Academia" in resp_sys_health
    assert "sqlite_wal" in resp_sys_health
    assert "thermal_guard" in resp_sys_health

    # 2. Test GET /api/health (Backward compatibility)
    req_health = b"GET /api/health HTTP/1.1\r\nHost: localhost\r\n\r\n"
    sock_health = MockSocket(req_health)
    FallbackHTTPHandler(sock_health, ("127.0.0.1", 5000), DummyServer())
    resp_health = sock_health.output.getvalue().decode("utf-8")
    assert "200 OK" in resp_health
    assert "ONLINE" in resp_health or "HEALTHY" in resp_health


# ========================================================================================
# 8. CI/CD WORKFLOW PIPELINE VERIFICATION
# ========================================================================================

def test_cicd_workflow_syntax_and_jobs():
    """Verifies .github/workflows/deploy.yml configures automated testing and build verification."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    workflow_path = os.path.join(base_dir, ".github", "workflows", "deploy.yml")

    assert os.path.isfile(workflow_path), "deploy.yml workflow file must exist."

    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow_content = f.read()

    assert "push:" in workflow_content
    assert "pull_request:" in workflow_content
    assert "verification-and-tests:" in workflow_content
    assert "build-static-routes:" in workflow_content
    assert "pytest tests/test_phase5_telemetry.py" in workflow_content
    assert "test_phase10_production.py" in workflow_content
    assert "npm run build" in workflow_content


# ========================================================================================
# 9. ZERO-LEAKAGE PRIVACY & THERMAL SAFETY INVARIANTS
# ========================================================================================

def test_phase10_privacy_and_thermal_safety():
    """Strictly validates zero leakage of private credentials and < 250ms thermal execution budget."""
    restricted_patterns = ["ashokkumar2008313@gmail.com", "9597382878"]
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    files_to_check = [
        os.path.join(base_dir, "Dockerfile"),
        os.path.join(base_dir, "docker-compose.yml"),
        os.path.join(base_dir, ".dockerignore"),
        os.path.join(base_dir, "backend", "sqlite_wal_optimizer.py"),
        os.path.join(base_dir, ".github", "workflows", "deploy.yml")
    ]

    for fpath in files_to_check:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            for pat in restricted_patterns:
                assert pat not in content, f"Restricted admin metadata leaked in {fpath}"

    # Thermal benchmark: Ensure health checks and WAL checkpoints run < 250ms total
    t0 = time.perf_counter()
    for _ in range(10):
        check_database_health(TEST_DB_PATH)
        get_system_health_status(TEST_DB_PATH)
        execute_wal_checkpoint(TEST_DB_PATH, mode="PASSIVE")
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    assert elapsed_ms < 250.0, f"Health check operations took {elapsed_ms:.2f}ms (> 250ms thermal budget)"
