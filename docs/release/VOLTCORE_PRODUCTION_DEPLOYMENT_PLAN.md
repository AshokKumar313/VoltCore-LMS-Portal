# VoltCore Apex Academia — Production Deployment Plan & Infrastructure Runbook

**Institutional Header**: Department of Electronics Engineering, Madras Institute of Technology (MIT) Campus, Anna University  
**Platform Lead & Systems Architect**: Ashok Kumar A (`2023MITEC042`)  
**Deployment Target**: Multi-Stage Containerized Cloud / On-Premise Campus Server  
**Architecture**: Astro 5 Static Presentation + Python 3.12 Flask API + SQLite WAL Mode  

---

## 1. Deployment Architecture Overview

```
                                  +-----------------------+
                                  |   Internet / Campus   |
                                  +-----------+-----------+
                                              |
                                              v
                              +---------------+---------------+
                              |    Nginx Reverse Proxy /      |
                              |    GitHub Pages CDN Edge      |
                              +---------------+---------------+
                                              |
                   +--------------------------+--------------------------+
                   | (Static Requests)                                   | (API / Telemetry)
                   v                                                     v
      +----------------------------+                       +----------------------------+
      |  Astro 5 SSG Production    |                       |   Python 3.12 Flask API    |
      |  Static Distribution       |                       |   Container Runner         |
      |  * 85 HTML Static Pages    |                       |   * Port: 5000             |
      |  * Hydrated React Islands  |                       |   * Resource Quota: 0.75 CPU|
      |  * Compiled Tailwind CSS   |                       |   * Memory Limit: 256MB    |
      +----------------------------+                       +--------------+-------------+
                                                                          |
                                                                          v
                                                           +----------------------------+
                                                           |   SQLite 3.45 (WAL Mode)   |
                                                           |   Zero-Downtime Data Layer |
                                                           |   * PRAGMA journal_mode=WAL|
                                                           |   * PRAGMA synchronous=NORM|
                                                           |   * Persistent Volume Mount|
                                                           +----------------------------+
```

---

## 2. Multi-Stage Docker Container Specification

The platform utilizes a hardened multi-stage Docker build (`Dockerfile`) to produce lightweight, secure, and reproducible deployment images:

### Stage 1: Frontend Asset Compilation (`node:20-alpine`)
- Builds all 85 Astro static routes and React micro-islands into `/app/dist`.
- Employs frozen npm lockfile installation (`npm ci`).
- Executes with zero node runtime in the final production container.

### Stage 2: Production Microservice Runner (`python:3.12-slim`)
- Copies static build artifacts from Stage 1.
- Installs minimal runtime dependencies (curl, sqlite3).
- Configures persistent storage volumes (`/app/data`) for SQLite database files (`voltcore_lms.db`, `voltcore_telemetry.db`).
- Executes under strict resource limits via `docker-compose.yml`:
  ```yaml
  resources:
    limits:
      cpus: '0.75'
      memory: 256M
    reservations:
      cpus: '0.15'
      memory: 64M
  ```

---

## 3. Continuous Integration & Deployment (CI/CD) Workflow

The GitHub Actions workflow (`.github/workflows/deploy.yml`) enforces multi-stage automated verification before any production deployment:

1. **Verification & Pytest Suite**:
   - Python 3.12 clean environment setup.
   - Comprehensive syntax verification (`python -m py_compile`).
   - Execution of the complete automated test suite (`pytest tests/ -v`).
   - AST sandbox security scan and credential leakage assertion (`grep` checks for private admin contact tokens).

2. **Static Route SSG Compilation**:
   - Compiles Astro static build (`npm run build`).
   - Verifies the existence of all production HTML static routes.

3. **Production Deployment**:
   - Deploys static frontend distribution to GitHub Pages or cloud hosting edge.
   - Dispatches container registry images for the backend REST gateway.

---

## 4. SQLite WAL Mode & Zero-Downtime Backup Runbook

To ensure complete data integrity without write stalls, VoltCore Apex Academia operates SQLite in Write-Ahead Logging (WAL) mode:

### Connection Pragma Invariants:
```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA busy_timeout = 5000;
PRAGMA foreign_keys = ON;
PRAGMA cache_size = -2000;
```

### Zero-Downtime Online Backup Procedure:
1. Backups utilize the SQLite Online Backup API (`sqlite3_backup_step()`), enabling concurrent reads and writes during the snapshot.
2. The administrative endpoint `/api/admin/backup-db` verifies `ADMIN` role authentication before triggering the backup.
3. Checkpointing is executed non-blockingly:
   ```python
   def execute_wal_checkpoint(db_path: str) -> Dict[str, Any]:
       with sqlite3.connect(db_path) as conn:
           cursor = conn.cursor()
           cursor.execute("PRAGMA wal_checkpoint(TRUNCATE);")
           res = cursor.fetchone()
           return {"checkpoint_status": "SUCCESS", "busy": res[0], "log": res[1], "checkpointed": res[2]}
   ```
4. Automated retention policy keeps the 10 most recent timestamped backups and purges older archives to conserve disk space.

---

## 5. Observability, Structured Logging & Health Probes

### 1. Healthcheck Endpoints:
- `/api/system/health` & `/api/health`: Return JSON health status including database integrity, WAL size, thread pool utilization, and thermal guard profile:
  ```json
  {
    "status": "HEALTHY",
    "platform": "VoltCore Apex Academia",
    "version": "5.0.0-Production",
    "sqlite_wal": {
      "status": "HEALTHY",
      "journal_mode": "WAL",
      "integrity_check": "ok",
      "is_healthy": true
    },
    "thermal_guard": {
      "thermal_status": "NOMINAL",
      "cpu_load_target": "<5%",
      "fan_profile": "Whisper-Quiet"
    }
  }
  ```

### 2. Structured JSON Logging:
- Managed via `backend/structured_logger.py`.
- Formats every event with ISO-8601 UTC timestamps, service name, correlation IDs (`req_xxxxxxxxxxxx`), and execution latency (`duration_ms`).
- Automatically redacts sensitive fields (`password`, `token`, `secret`, `jwt`).

---

## 6. Rollback & Disaster Recovery Procedures

1. **Frontend Rollback**:
   - Instant rollback via GitHub Pages / CDN deployment history or redeployment of previous git tag.
2. **Backend Container Rollback**:
   - `docker-compose down && docker-compose up -d --build <previous-tag>`
3. **Database Restoration**:
   - In the event of catastrophic data corruption, restore from the latest verified WAL backup:
     ```bash
     cp voltcore_lms_backup_YYYYMMDD_HHMMSS.db voltcore_lms.db
     python -c "from backend.sqlite_wal_optimizer import check_database_health; print(check_database_health())"
     ```

**Approval**: Verified and ready for deployment execution.
