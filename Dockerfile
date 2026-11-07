# ========================================================================================
# VoltCore Apex Academia - Production Multi-Stage Container Dockerfile
# Platform Lead: Ashok Kumar A
# Architecture:
#   Stage 1 (frontend-builder) : Node 20 Alpine compiles Astro 5 static production bundle (dist/)
#   Stage 2 (production-runner): Python 3.12 Slim serves Python REST API + SQLite WAL Mode
# Standards: Autonomous Engineering Cluster • Low Thermal Load • Zero Data Loss WAL
# ========================================================================================

# ----------------------------------------------------------------------------------------
# STAGE 1: FRONTEND ASSET COMPILATION (Astro 5 + React 19 + TypeScript)
# ----------------------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache libc6-compat

# Copy package configurations
COPY package.json package-lock.json* ./

# Install npm dependencies (frozen lockfile when available)
RUN npm ci || npm install

# Copy application source code for static compilation
COPY astro.config.mjs tailwind.config.mjs tsconfig.json ./
COPY public/ ./public/
COPY src/ ./src/

# Compile production static distribution (output to /app/dist)
ENV NODE_ENV=production
RUN npm run build

# ----------------------------------------------------------------------------------------
# STAGE 2: PRODUCTION RUNTIME (Python 3.12 Flask / SQLite WAL Backend)
# ----------------------------------------------------------------------------------------
FROM python:3.12-slim AS production-runner

# Optimize Python execution for low-overhead, unbuffered microservice execution
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000 \
    VOLTCORE_ENV=production \
    LMS_DB_PATH=/app/data/voltcore_lms.db \
    TELEMETRY_DB_PATH=/app/data/voltcore_telemetry.db

WORKDIR /app

# Install system dependencies (curl for healthchecks, sqlite3 for diagnostic inspection)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Persistent volume directory for SQLite WAL & SHM storage (Zero Data Loss)
RUN mkdir -p /app/data && chmod 777 /app/data
VOLUME ["/app/data"]

# Install Python backend dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt || true

# Copy backend Python code and application server
COPY lms_database.py attendance_server.py /app/
COPY backend/ /app/backend/
COPY src/content/modules/ /app/src/content/modules/

# Copy compiled static frontend bundle from Stage 1 builder
COPY --from=frontend-builder /app/dist /app/dist

# Expose Telemetry and API Gateway port
EXPOSE 5000

# Continuous Healthcheck Probe (Testing /api/system/health)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/api/system/health || curl -f http://localhost:5000/api/health || exit 1

# Launch Server (Passive CPU footprint)
CMD ["python", "attendance_server.py"]
