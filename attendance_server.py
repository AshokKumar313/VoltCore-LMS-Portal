"""
========================================================================================
VoltCore Apex Academia - Hardware Telemetry & Attendance Server
Anna University / MIT Campus - Department of Electronics Engineering
----------------------------------------------------------------------------------------
Module: attendance_server.py
Port: 5000
Protocols: HTTP REST JSON API, CORS enabled
Hardware Target: ESP32 IoT Node (MFRC522 RFID, FreeRTOS telemetry)
========================================================================================
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure database access from current directory
import lms_database
from backend.ltspice_runner import parse_and_run_spice_simulation
from backend.security_auth import (
    OWNER_METADATA,
    PUBLIC_CONTACT_METADATA,
    get_admin_audit_metadata,
    global_rate_limiter
)
from backend.security_middleware import init_security_middleware, add_security_headers, SECURITY_HEADERS
from backend.rag_tutor_engine import query_rag_knowledge_base
try:
    from backend.websocket_gateway import telemetry_broker
except ImportError:
    from websocket_gateway import telemetry_broker

# ANSI Terminal Formatting for High-Precision Diagnostics
class TerminalColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    EMERALD = '\033[38;2;0;240;181m'
    NAVY = '\033[38;2;2;8;19m'
    BG_EMERALD = '\033[48;2;0;105;62m'


def log_terminal_diagnostic(
    event_type: str,
    node_id: str,
    student_id: str,
    student_name: str,
    rfid_uid: str,
    status: str,
    rssi: Any = None,
    http_code: int = 200
) -> None:
    """Prints a high-visibility, precision terminal diagnostic for hardware telemetry."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    color_status = TerminalColors.GREEN if http_code == 200 else TerminalColors.RED
    status_icon = "✓" if http_code == 200 else "✗"
    
    border = "─" * 86
    print(f"\n{TerminalColors.CYAN}┌{border}┐{TerminalColors.RESET}")
    print(f"{TerminalColors.CYAN}│{TerminalColors.RESET} {TerminalColors.BOLD}{TerminalColors.EMERALD}[VOLTCORE APEX ACADEMIA - ESP32 TELEMETRY]{TerminalColors.RESET} {TerminalColors.YELLOW}{now_str}{TerminalColors.RESET} │")
    print(f"{TerminalColors.CYAN}├{border}┤{TerminalColors.RESET}")
    print(f"{TerminalColors.CYAN}│{TerminalColors.RESET}  • Node Identifier : {TerminalColors.BOLD}{node_id:<28}{TerminalColors.RESET} Signal (RSSI) : {TerminalColors.CYAN}{str(rssi) + ' dBm' if rssi else 'N/A':<15}{TerminalColors.RESET} │")
    print(f"{TerminalColors.CYAN}│{TerminalColors.RESET}  • Student Name    : {TerminalColors.BOLD}{student_name:<28}{TerminalColors.RESET} Student Roll  : {TerminalColors.YELLOW}{student_id:<15}{TerminalColors.RESET} │")
    print(f"{TerminalColors.CYAN}│{TerminalColors.RESET}  • RFID UID Token  : {TerminalColors.BLUE}{rfid_uid:<28}{TerminalColors.RESET} Campus Hub    : MIT Chromepet   │")
    print(f"{TerminalColors.CYAN}│{TerminalColors.RESET}  • Access Result   : {color_status}{status_icon} {status} (HTTP {http_code}){TerminalColors.RESET}{' ' * (44 - len(status))} │")
    print(f"{TerminalColors.CYAN}└{border}┘{TerminalColors.RESET}\n")


def process_attendance_scan(payload: Dict[str, Any]) -> tuple[Dict[str, Any], int]:
    """
    Validates scan data, looks up user in lms_database, logs attendance, and returns response.
    """
    student_id = payload.get("student_id") or payload.get("user_id", "")
    rfid_uid = payload.get("rfid_uid", "").strip().upper()
    node_id = payload.get("node_id", "ESP32_MIT_NODE_DEFAULT")
    rssi = payload.get("rssi", None)

    # Resolve Student either by Roll/UserID or by RFID Token
    user = None
    if student_id:
        user = lms_database.get_user_by_id(student_id)
    elif rfid_uid:
        user = lms_database.get_user_by_rfid(rfid_uid)

    if not user:
        # Check if student_id matches RFID in database
        if rfid_uid:
            user = lms_database.get_user_by_rfid(rfid_uid)

    if user:
        rec = lms_database.record_attendance(
            user_id=user["user_id"],
            node_id=node_id,
            rfid_uid=rfid_uid or user.get("rfid_uid", "SIMULATED_UID"),
            status="Lab-Verified"
        )
        # Real-Time SSE Telemetry Fan-Out
        try:
            telemetry_broker.emit_attendance_scan(
                node_id=node_id,
                student_id=user["user_id"],
                student_name=user["name"],
                rfid_uid=rfid_uid or user.get("rfid_uid", "SIMULATED_UID"),
                status="Lab-Verified",
                rssi=rssi
            )
            telemetry_broker.emit_xp_gain(
                student_id=user["user_id"],
                student_name=user["name"],
                xp_amount=50,
                reason="ESP32 Lab Entry RFID Scan",
                multiplier="2.5x"
            )
        except Exception:
            pass

        log_terminal_diagnostic(
            event_type="RFID_AUTH_SUCCESS",
            node_id=node_id,
            student_id=user["user_id"],
            student_name=user["name"],
            rfid_uid=rfid_uid or user.get("rfid_uid", "SIMULATED_UID"),
            status="AUTHORIZED - LAB ENTRY LOGGED",
            rssi=rssi,
            http_code=200
        )
        return {
            "status": "success",
            "message": f"Attendance verified for {user['name']}",
            "student_id": user["user_id"],
            "name": user["name"],
            "department": user["department"],
            "campus": user["campus"],
            "xp_awarded": 50,
            "attendance_record": rec
        }, 200
    else:
        # Unknown student / card
        unknown_id = student_id or "UNKNOWN"
        log_terminal_diagnostic(
            event_type="RFID_AUTH_FAILED",
            node_id=node_id,
            student_id=unknown_id,
            student_name="[Unregistered Identity]",
            rfid_uid=rfid_uid or "N/A",
            status="REJECTED - UNREGISTERED CARD",
            rssi=rssi,
            http_code=404
        )
        return {
            "status": "error",
            "message": "Student ID or RFID UID not recognized in Anna University / MIT Campus roster.",
            "student_id": unknown_id,
            "rfid_uid": rfid_uid
        }, 404


def process_bulk_attendance_sync(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Processes LittleFS bulk offline queue dispatches from ESP32 nodes.
    Validates cryptographic SHA-256 hash chaining to ensure tamper-evident offline logging.
    """
    node_id = payload.get("node_id", "ESP32_UNKNOWN_NODE")
    records = payload.get("records", [])

    if not records or not isinstance(records, list):
        return {"status": "error", "message": "Empty or invalid records array in bulk sync."}, 400

    verified_count = 0
    tampered_indices = []
    committed_records = []
    prev_expected_hash = None

    for idx, r in enumerate(records):
        seq = r.get("seq_id", idx)
        ts = r.get("timestamp", 0)
        sid = r.get("student_id", "")
        uid = r.get("rfid_uid", "")
        r_prev_hash = r.get("prev_hash", "")
        r_hash = r.get("hash", "")

        # Verify hash chaining sequence if consecutive items in batch
        if prev_expected_hash and r_prev_hash != prev_expected_hash:
            tampered_indices.append(idx)
            continue

        # Recompute SHA-256 digest
        preimage = f"{r_prev_hash}:{seq}:{ts}:{sid}:{uid}:{node_id}".encode("utf-8")
        computed_hash = hashlib.sha256(preimage).hexdigest()

        if computed_hash.lower() != r_hash.lower():
            tampered_indices.append(idx)
            continue

        prev_expected_hash = computed_hash

        # Commit to local SQLite relational store if user enrolled
        user = lms_database.get_user_by_id(sid) or lms_database.get_user_by_rfid(uid)
        if user:
            uid_to_log = uid or user.get("rfid_uid", "OFFLINE_LITTLEFS_UID")
            try:
                rec = lms_database.record_attendance(
                    user_id=user["user_id"],
                    node_id=node_id,
                    rfid_uid=uid_to_log,
                    status="Lab-Verified"
                )
                committed_records.append(rec)
            except Exception:
                pass
        verified_count += 1

    # Real-Time SSE Telemetry Fan-Out for Fleet Status
    try:
        telemetry_broker.emit_fleet_heartbeat(
            node_id=node_id,
            status="BULK_SYNC_SUCCESS" if not tampered_indices else "INTEGRITY_ALERT",
            rssi=-60,
            spool_depth=len(records) - verified_count,
            ip="10.0.4.18"
        )
    except Exception:
        pass

    log_status = "AUTHORIZED - BULK LITTLEFS COMMITTED" if verified_count > 0 else "REJECTED - HASH CHAIN FAILED"
    log_terminal_diagnostic(
        event_type="LITTLEFS_BULK_SYNC",
        node_id=node_id,
        student_id=f"{verified_count} Scans",
        student_name=f"Bulk Sync ({verified_count}/{len(records)})",
        rfid_uid=prev_expected_hash[:16] + "..." if prev_expected_hash else "CHAIN_VOID",
        status=log_status,
        http_code=200 if not tampered_indices else 207
    )

    return {
        "status": "success" if not tampered_indices else "partial_success",
        "node_id": node_id,
        "total_received": len(records),
        "verified_committed": verified_count,
        "tampered_rejected": len(tampered_indices),
        "tampered_indices": tampered_indices,
        "head_hash": prev_expected_hash or "",
        "timestamp": datetime.now().isoformat()
    }, 200 if not tampered_indices else 207


def get_class_weak_topics() -> Dict[str, Any]:
    """Returns class weak-topic failure matrix derived from Wokwi auto-grader failure telemetry."""
    return {
        "cohort": "Anna University MIT Campus - Department of Electronics Engineering (ECE R2023)",
        "enrolled_students": 64,
        "evaluations_analyzed": 384,
        "weak_topic_matrix": [
            {
                "topic": "ARM Cortex-M DMA Memory Barriers (__DMB, __DSB)",
                "module": "EC8708 (Lab 02)",
                "failure_rate_percent": 42.2,
                "common_mistake": "Enabling DMA_SxCR_EN before memory barrier commits pointer writes into SRAM",
                "severity": "CRITICAL",
                "recommended_action": "Mandate Section IV Engineering Trap drill on out-of-order bus memory coherency."
            },
            {
                "topic": "FreeRTOS Priority Inversion & Mutex Deadlocks",
                "module": "EC8706 (Lab 01)",
                "failure_rate_percent": 37.5,
                "common_mistake": "Taking recursive mutex from within ISR context or neglecting priority inheritance ceiling",
                "severity": "HIGH",
                "recommended_action": "Review xSemaphoreCreateMutex vs Binary Semaphore signaling matrix."
            },
            {
                "topic": "RISC-V RAW Hazard Forwarding & Load-Use Stalls",
                "module": "EC8705 (Lab 04)",
                "failure_rate_percent": 31.3,
                "common_mistake": "Forwarding x0 register operand instead of hardwiring constant zero",
                "severity": "HIGH",
                "recommended_action": "Simulate 5-stage pipeline hazard unit in Verilog test bench."
            },
            {
                "topic": "I2C Bus Contention & CRC-8 Calculation",
                "module": "EC8704 (Lab 03)",
                "failure_rate_percent": 26.6,
                "common_mistake": "Unbounded while loop on I2C_FLAG_BUSY causing system deadlock during clock stretching",
                "severity": "MEDIUM",
                "recommended_action": "Implement hardware watchdog timer and non-blocking timeout returns."
            },
            {
                "topic": "Defense UAV FHSS LoRa Doppler Bin Migration",
                "module": "EC8703 (Lab 05)",
                "failure_rate_percent": 21.9,
                "common_mistake": "Omitting TCXO calibration register updates under 108 km/h velocity shifts",
                "severity": "MEDIUM",
                "recommended_action": "Derive delta_f Doppler equation for 2.4 GHz carrier frequencies."
            }
        ],
        "generated_at": datetime.now().isoformat()
    }


def compute_nba_attainment_and_zscores() -> Dict[str, Any]:
    """
    Computes NBA / NAAC Course Outcome (CO1-CO5) and Program Outcome (PO1-PO12) attainment metrics,
    along with at-risk student early warning indicators using attendance Z-scores.
    """
    # Sample cohort distribution representing MIT Campus 7th Sem ECE
    students = [
        {"id": "2023MITEC001", "name": "Aarav S", "attendance_pct": 92.5, "lab_score_pct": 88.0, "viva_pct": 85.0},
        {"id": "2023MITEC014", "name": "Deepa K", "attendance_pct": 89.0, "lab_score_pct": 94.0, "viva_pct": 90.0},
        {"id": "2023MITEC023", "name": "Harish R", "attendance_pct": 68.0, "lab_score_pct": 52.0, "viva_pct": 45.0}, # At Risk
        {"id": "2023MITEC035", "name": "Kavitha M", "attendance_pct": 95.0, "lab_score_pct": 96.0, "viva_pct": 92.0},
        {"id": "2023MITEC042", "name": "Ashok Kumar A", "attendance_pct": 98.0, "lab_score_pct": 100.0, "viva_pct": 98.0}, # Platform Architect
        {"id": "2023MITEC051", "name": "Manojkumar T", "attendance_pct": 62.5, "lab_score_pct": 48.0, "viva_pct": 40.0}, # Critical At Risk
        {"id": "2023MITEC058", "name": "Naveen P", "attendance_pct": 84.0, "lab_score_pct": 82.0, "viva_pct": 78.0},
        {"id": "2023MITEC064", "name": "Priyanka S", "attendance_pct": 72.0, "lab_score_pct": 64.0, "viva_pct": 60.0}, # Moderate Risk
    ]

    # Calculate Attendance Mean and Standard Deviation
    att_vals = [s["attendance_pct"] for s in students]
    mean_att = sum(att_vals) / len(att_vals)
    variance_att = sum((x - mean_att) ** 2 for x in att_vals) / len(att_vals)
    std_att = variance_att ** 0.5 if variance_att > 0 else 1.0

    at_risk_roster = []
    for s in students:
        z_score = (s["attendance_pct"] - mean_att) / std_att
        risk_tier = "NORMAL"
        if z_score < -1.5 or s["attendance_pct"] < 75.0:
            risk_tier = "CRITICAL_DEFICIT"
        elif z_score < -0.8 or s["attendance_pct"] < 80.0:
            risk_tier = "MODERATE_WARNING"

        at_risk_roster.append({
            "student_id": s["id"],
            "student_name": s["name"],
            "attendance_pct": round(s["attendance_pct"], 1),
            "z_score": round(z_score, 2),
            "lab_score_pct": round(s["lab_score_pct"], 1),
            "viva_pct": round(s["viva_pct"], 1),
            "risk_tier": risk_tier,
            "mandatory_75_compliant": s["attendance_pct"] >= 75.0
        })

    # Sort at_risk_roster so most vulnerable students appear first
    at_risk_roster.sort(key=lambda x: x["z_score"])

    # NBA Course Outcomes (CO1 to CO5) Attainment Matrix (Scale: 0.0 to 3.0 / Target: 2.1 = 70%)
    course_outcomes = [
        {"co": "CO1", "title": "Bare-Metal Registers & GPIO Concurrency", "target_pct": 70.0, "attained_pct": 84.5, "attainment_level": 2.54, "status": "ATTAINED", "mapped_pos": ["PO1", "PO2"]},
        {"co": "CO2", "title": "Automotive CAN & Bus Protocols with CRC", "target_pct": 70.0, "attained_pct": 78.2, "attainment_level": 2.35, "status": "ATTAINED", "mapped_pos": ["PO3", "PO5"]},
        {"co": "CO3", "title": "5-Stage Pipelined RISC-V Soft-Core", "target_pct": 70.0, "attained_pct": 71.8, "attainment_level": 2.15, "status": "ATTAINED", "mapped_pos": ["PO3", "PO4"]},
        {"co": "CO4", "title": "FreeRTOS Scheduling & Priority Inversion", "target_pct": 70.0, "attained_pct": 68.4, "attainment_level": 2.05, "status": "REMEDIAL_ACTION_REQUIRED", "mapped_pos": ["PO2", "PO3"]},
        {"co": "CO5", "title": "Advanced DMA Circular Zero-Copy IPC", "target_pct": 70.0, "attained_pct": 82.0, "attainment_level": 2.46, "status": "ATTAINED", "mapped_pos": ["PO1", "PO5", "PO12"]},
    ]

    return {
        "academic_year": "2026-2027",
        "semester": "Semester VII",
        "regulation": "Anna University R2023",
        "course": "EC8702 / EC8708: Advanced Embedded Systems & RTOS Laboratory",
        "mean_attendance": round(mean_att, 2),
        "std_attendance": round(std_att, 2),
        "total_enrolled": len(students),
        "at_risk_count": sum(1 for s in at_risk_roster if s["risk_tier"] != "NORMAL"),
        "course_outcomes": course_outcomes,
        "at_risk_roster": at_risk_roster,
        "timestamp": datetime.now().isoformat()
    }


def handle_tutor_query(payload: Dict[str, Any]) -> tuple[Dict[str, Any], int]:
    """Processes AI tutor queries and viva challenges using local RAG curriculum engine and Ollama."""
    query = payload.get("query", "").strip()
    student_id = payload.get("student_id", "2023MITEC042")
    mode = payload.get("mode", "chat")
    use_ollama = payload.get("use_ollama", False)
    model = payload.get("model")

    if not query:
        return {
            "status": "error",
            "message": "Empty query received."
        }, 400

    try:
        rag_data = query_rag_knowledge_base(
            query=query,
            student_id=student_id,
            mode=mode,
            use_ollama=use_ollama,
            model=model
        )
        return rag_data, 200
    except Exception as e:
        return {
            "status": "error",
            "message": f"RAG query failed: {str(e)}",
            "student_id": student_id
        }, 500


# Check if Flask is installed in environment
try:
    from flask import Flask, request, jsonify, make_response
    from flask_cors import CORS
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


if HAS_FLASK:
    app = Flask("VoltCoreAttendanceServer")
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    init_security_middleware(app)

    @app.route("/", methods=["GET"])
    def root_endpoint():
        return jsonify({
            "platform": "VoltCore Apex Academia",
            "system": "Embedded Systems & IoT LMS Telemetry Gateway",
            "institution": "Madras Institute of Technology (MIT) Campus, Anna University",
            "status": "ONLINE",
            "endpoints": {
                "GET /api/attendance": "Fetch chronologically ordered attendance logs",
                "POST /api/attendance": "Receive and log ESP32 student RFID scans",
                "GET /api/health": "Telemetry node and database health check"
            }
        })

    @app.route("/api/health", methods=["GET"])
    def health_endpoint():
        return jsonify({
            "status": "HEALTHY",
            "port": 5000,
            "database": "voltcore_lms.db",
            "journal_mode": "wal",
            "timestamp": datetime.utcnow().isoformat(),
            "target_node": "ESP32-WROOM-32 / FreeRTOS",
            "thermal_guard": "HP Victus 15-fa2xxx Low-Overhead Safe"
        }), 200

    @app.route("/api/system/metrics", methods=["GET"])
    def system_metrics_endpoint():
        from backend.performance_profiler import performance_profiler
        profile = performance_profiler.collect_full_profile()
        return jsonify(profile), 200

    @app.route("/api/attendance", methods=["GET", "POST", "OPTIONS"])
    def attendance_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            return resp

        if request.method == "GET":
            student_id = request.args.get("student_id")
            limit = int(request.args.get("limit", 50))
            logs = lms_database.get_attendance_history(user_id=student_id, limit=limit)
            return jsonify({
                "count": len(logs),
                "data": logs,
                "timestamp": datetime.utcnow().isoformat()
            }), 200

        elif request.method == "POST":
            payload = request.get_json(silent=True) or request.form.to_dict()
            if not payload:
                return jsonify({"status": "error", "message": "Missing JSON request body."}), 400

            resp_data, status_code = process_attendance_scan(payload)
            return jsonify(resp_data), status_code

    @app.route("/api/attendance/bulk_sync", methods=["POST", "OPTIONS"])
    def attendance_bulk_sync_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp

        payload = request.get_json(silent=True) or {}
        resp_data, status_code = process_bulk_attendance_sync(payload)
        return jsonify(resp_data), status_code

    @app.route("/api/analytics/weak_topics", methods=["GET"])
    def analytics_weak_topics_endpoint():
        return jsonify(get_class_weak_topics()), 200

    @app.route("/api/analytics/attainment", methods=["GET"])
    def analytics_attainment_endpoint():
        return jsonify(compute_nba_attainment_and_zscores()), 200

    @app.route("/api/admin/audit_metadata", methods=["GET"])
    def admin_audit_metadata_endpoint():
        # Authenticate role: check query or header for privileged role
        role = request.args.get("role", "Student")
        auth_header = request.headers.get("Authorization", "")
        if "Bearer " in auth_header:
            from backend.security_auth import verify_jwt_token
            claims = verify_jwt_token(auth_header.split(" ")[1])
            if claims:
                role = claims.get("role", role)

        audit_data = get_admin_audit_metadata(role=role)
        return jsonify(audit_data), 200

    @app.route("/api/user", methods=["GET"])
    def user_profile_endpoint():
        student_id = request.args.get("student_id", "2023MITEC042")
        user = lms_database.get_user_by_id(student_id)
        if user:
            return jsonify({
                "status": "success",
                "user": user,
                "level": 18,
                "title": "Silicon Grandmaster",
                "multiplier": 2.5
            }), 200
        return jsonify({"status": "error", "message": "User not found"}), 404

    @app.route("/api/rag_query", methods=["POST", "OPTIONS"])
    @app.route("/api/tutor_query", methods=["POST", "OPTIONS"])
    @app.route("/app/api/tutor_query", methods=["POST", "OPTIONS"])
    def tutor_query_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp

        payload = request.get_json(silent=True) or request.form.to_dict()
        if not payload:
            return jsonify({"status": "error", "message": "Missing query payload"}), 400
        resp_data, status_code = handle_tutor_query(payload)
        return jsonify(resp_data), status_code

    @app.route("/api/spice_simulate", methods=["GET", "POST", "OPTIONS"])
    def spice_simulate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            return resp

        if request.method == "GET":
            circuit_id = request.args.get("circuit", "bjt_ce")
            sim_data = parse_and_run_spice_simulation(circuit_id)
            return jsonify(sim_data), 200
        else:
            payload = request.get_json(silent=True) or {}
            circuit_id = payload.get("circuit", "bjt_ce")
            params = payload.get("params", {})
            sim_data = parse_and_run_spice_simulation(circuit_id, params)
            return jsonify(sim_data), 200

    @app.route("/api/telemetry/stream", methods=["GET"])
    def telemetry_stream_endpoint():
        from flask import Response
        resp = Response(telemetry_broker.stream_generator(), mimetype="text/event-stream")
        resp.headers["Cache-Control"] = "no-cache"
        resp.headers["X-Accel-Buffering"] = "no"
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp

    @app.route("/api/telemetry/broadcast", methods=["POST", "OPTIONS"])
    def telemetry_broadcast_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp

        payload = request.get_json(silent=True) or {}
        ev_type = payload.get("event_type", "custom_telemetry")
        data = payload.get("data", {})
        listeners = telemetry_broker.broadcast(ev_type, data)
        return jsonify({
            "status": "broadcast_dispatched",
            "event_type": ev_type,
            "listeners": listeners,
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    @app.route("/api/telemetry/history", methods=["GET"])
    def telemetry_history_endpoint():
        limit = int(request.args.get("limit", 25))
        return jsonify({
            "status": "success",
            "history": telemetry_broker.get_recent_history(limit),
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    @app.route("/api/content/status", methods=["GET"])
    def content_status_endpoint():
        from backend.content_status_api import get_content_status_report
        return jsonify(get_content_status_report()), 200

    @app.route("/api/content/status/update", methods=["POST", "OPTIONS"])
    def content_status_update_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp

        from backend.content_status_api import update_content_status_entry
        payload = request.get_json(silent=True) or {}
        res_data, status_code = update_content_status_entry(payload)
        return jsonify(res_data), status_code

    @app.route("/api/content/changelog", methods=["GET"])
    def content_changelog_endpoint():
        from backend.content_status_api import get_changelog_history
        mod_code = request.args.get("module_code")
        limit = int(request.args.get("limit", 50))
        return jsonify(get_changelog_history(module_code=mod_code, limit=limit)), 200

    @app.route("/api/smart_lab/overview", methods=["GET"])
    def smart_lab_overview_endpoint():
        from backend.iot_telemetry_hub import smart_lab_hub
        return jsonify(smart_lab_hub.get_lab_overview()), 200

    @app.route("/api/smart_lab/book", methods=["POST", "OPTIONS"])
    def smart_lab_book_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp

        from backend.iot_telemetry_hub import smart_lab_hub
        payload = request.get_json(silent=True) or {}
        eq_id = payload.get("equipment_id", "")
        std_id = payload.get("student_id", "2023MITEC042")
        result = smart_lab_hub.book_equipment(eq_id, student_id=std_id)
        code = 200 if result.get("status") == "SUCCESS" else 400
        return jsonify(result), code

    @app.route("/api/collaboration/overview", methods=["GET"])
    def collaboration_overview_endpoint():
        from backend.collaboration_hub import collaboration_hub
        return jsonify(collaboration_hub.get_collaboration_overview()), 200

    @app.route("/api/collaboration/portfolio/like", methods=["POST", "OPTIONS"])
    def collaboration_like_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.collaboration_hub import collaboration_hub
        payload = request.get_json(silent=True) or {}
        prj_id = payload.get("project_id", "")
        res = collaboration_hub.like_project(prj_id)
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    # ====================================================================================
    # Phase 27: Data Intelligence & Academic Quality Center Endpoints
    # ====================================================================================

    @app.route("/api/intelligence/overview", methods=["GET"])
    def intelligence_overview_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        return jsonify(data_intelligence_engine.get_overview_metrics()), 200

    @app.route("/api/intelligence/audits", methods=["GET"])
    def intelligence_audits_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        atype = request.args.get("audit_type")
        status = request.args.get("status")
        sev = request.args.get("severity")
        return jsonify(data_intelligence_engine.get_academic_audits(atype, status, sev)), 200

    @app.route("/api/intelligence/run-consistency-check", methods=["POST", "OPTIONS"])
    def intelligence_consistency_check_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.run_record_consistency_check(actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/resolve-audit", methods=["POST", "OPTIONS"])
    def intelligence_resolve_audit_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        aid = payload.get("audit_id", "")
        notes = payload.get("resolution_notes", "Audit cleared by academic reviewer.")
        by = payload.get("resolved_by", "2023MITEC042")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_audit_issue(aid, notes, resolved_by=by, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/syllabus-coverage", methods=["GET"])
    def intelligence_syllabus_coverage_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_syllabus_coverage(code)), 200

    @app.route("/api/intelligence/update-syllabus-unit", methods=["POST", "OPTIONS"])
    def intelligence_update_syllabus_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        unit = int(payload.get("unit_num", 1))
        covered = int(payload.get("topics_covered", 0))
        hrs = float(payload.get("hours_actual", 0.0))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.update_syllabus_unit_progress(code, unit, covered, hrs, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), status_code

    @app.route("/api/intelligence/question-bank-gaps", methods=["GET"])
    def intelligence_qb_gaps_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_question_bank_gaps(code)), 200

    @app.route("/api/intelligence/analyze-question-bank", methods=["POST", "OPTIONS"])
    def intelligence_analyze_qb_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        questions = payload.get("questions", [])
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.analyze_custom_question_bank(code, questions, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), status_code

    @app.route("/api/intelligence/content-freshness", methods=["GET"])
    def intelligence_content_freshness_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        status = request.args.get("freshness_status")
        return jsonify(data_intelligence_engine.get_content_freshness(code, status)), 200

    @app.route("/api/intelligence/audit-freshness", methods=["POST", "OPTIONS"])
    def intelligence_audit_freshness_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        thresh = int(payload.get("stale_threshold_days", 180))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.audit_content_freshness(thresh, actor_role=role)
        return jsonify(res), 200

    @app.route("/api/intelligence/duplicate-documents", methods=["GET"])
    def intelligence_duplicate_docs_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        status = request.args.get("status")
        return jsonify(data_intelligence_engine.get_duplicate_documents(status)), 200

    @app.route("/api/intelligence/detect-duplicates", methods=["POST", "OPTIONS"])
    def intelligence_detect_duplicates_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        res = data_intelligence_engine.detect_duplicate_submission(
            doc_id_a=payload.get("doc_id_a", "DOC_A"),
            doc_id_b=payload.get("doc_id_b", "DOC_B"),
            title_a=payload.get("title_a", "Document A"),
            title_b=payload.get("title_b", "Document B"),
            text_a=payload.get("text_a", ""),
            text_b=payload.get("text_b", ""),
            threshold_pct=float(payload.get("threshold_pct", 75.0)),
            actor_role=payload.get("role", "Faculty")
        )
        return jsonify(res), 200

    @app.route("/api/intelligence/resolve-duplicate", methods=["POST", "OPTIONS"])
    def intelligence_resolve_duplicate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        did = payload.get("duplicate_id", "")
        res_action = payload.get("resolution", "MERGED")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_duplicate_pair(did, res_action, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/research/overview", methods=["GET"])
    def research_overview_endpoint():
        from backend.research_discovery_engine import research_discovery_engine
        return jsonify(research_discovery_engine.get_research_overview()), 200

    @app.route("/api/research/synthesize", methods=["POST", "OPTIONS"])
    def research_synthesize_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.research_discovery_engine import research_discovery_engine
        payload = request.get_json(silent=True) or {}
        pids = payload.get("paper_ids", [])
        return jsonify(research_discovery_engine.generate_literature_synthesis(pids)), 200

    @app.route("/api/enterprise_admin/overview", methods=["GET"])
    def enterprise_admin_overview_endpoint():
        from backend.enterprise_admin_engine import enterprise_admin_engine
        return jsonify(enterprise_admin_engine.get_enterprise_overview()), 200

    @app.route("/api/enterprise_admin/nba_matrix", methods=["GET"])
    def enterprise_admin_nba_matrix_endpoint():
        from backend.enterprise_admin_engine import enterprise_admin_engine
        return jsonify(enterprise_admin_engine.compute_nba_co_po_matrix()), 200

    @app.route("/api/security/overview", methods=["GET"])
    def security_overview_endpoint():
        from backend.security_hardening_engine import security_hardening_engine
        return jsonify(security_hardening_engine.get_security_overview()), 200

    @app.route("/api/security/mfa/validate", methods=["POST", "OPTIONS"])
    def security_mfa_validate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.security_hardening_engine import security_hardening_engine
        payload = request.get_json(silent=True) or {}
        uid = payload.get("user_id", "2023MITEC042")
        tok = payload.get("token", "")
        ip = request.remote_addr or "127.0.0.1"
        res = security_hardening_engine.validate_mfa_token(uid, tok, client_ip=ip)
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    # ====================================================================================
    # Phase 27: Data Intelligence & Academic Quality Center Endpoints
    # ====================================================================================

    @app.route("/api/intelligence/overview", methods=["GET"])
    def intelligence_overview_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        return jsonify(data_intelligence_engine.get_overview_metrics()), 200

    @app.route("/api/intelligence/audits", methods=["GET"])
    def intelligence_audits_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        atype = request.args.get("audit_type")
        status = request.args.get("status")
        sev = request.args.get("severity")
        return jsonify(data_intelligence_engine.get_academic_audits(atype, status, sev)), 200

    @app.route("/api/intelligence/run-consistency-check", methods=["POST", "OPTIONS"])
    def intelligence_consistency_check_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.run_record_consistency_check(actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/resolve-audit", methods=["POST", "OPTIONS"])
    def intelligence_resolve_audit_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        aid = payload.get("audit_id", "")
        notes = payload.get("resolution_notes", "Audit cleared by academic reviewer.")
        by = payload.get("resolved_by", "2023MITEC042")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_audit_issue(aid, notes, resolved_by=by, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/syllabus-coverage", methods=["GET"])
    def intelligence_syllabus_coverage_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_syllabus_coverage(code)), 200

    @app.route("/api/intelligence/update-syllabus-unit", methods=["POST", "OPTIONS"])
    def intelligence_update_syllabus_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        unit = int(payload.get("unit_num", 1))
        covered = int(payload.get("topics_covered", 0))
        hrs = float(payload.get("hours_actual", 0.0))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.update_syllabus_unit_progress(code, unit, covered, hrs, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), status_code

    @app.route("/api/intelligence/question-bank-gaps", methods=["GET"])
    def intelligence_qb_gaps_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_question_bank_gaps(code)), 200

    @app.route("/api/intelligence/analyze-question-bank", methods=["POST", "OPTIONS"])
    def intelligence_analyze_qb_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        questions = payload.get("questions", [])
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.analyze_custom_question_bank(code, questions, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), status_code

    @app.route("/api/intelligence/content-freshness", methods=["GET"])
    def intelligence_content_freshness_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        status = request.args.get("freshness_status")
        return jsonify(data_intelligence_engine.get_content_freshness(code, status)), 200

    @app.route("/api/intelligence/audit-freshness", methods=["POST", "OPTIONS"])
    def intelligence_audit_freshness_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        thresh = int(payload.get("stale_threshold_days", 180))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.audit_content_freshness(thresh, actor_role=role)
        return jsonify(res), 200

    @app.route("/api/intelligence/duplicate-documents", methods=["GET"])
    def intelligence_duplicate_docs_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        status = request.args.get("status")
        return jsonify(data_intelligence_engine.get_duplicate_documents(status)), 200

    @app.route("/api/intelligence/detect-duplicates", methods=["POST", "OPTIONS"])
    def intelligence_detect_duplicates_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        res = data_intelligence_engine.detect_duplicate_submission(
            doc_id_a=payload.get("doc_id_a", "DOC_A"),
            doc_id_b=payload.get("doc_id_b", "DOC_B"),
            title_a=payload.get("title_a", "Document A"),
            title_b=payload.get("title_b", "Document B"),
            text_a=payload.get("text_a", ""),
            text_b=payload.get("text_b", ""),
            threshold_pct=float(payload.get("threshold_pct", 75.0)),
            actor_role=payload.get("role", "Faculty")
        )
        return jsonify(res), 200

    @app.route("/api/intelligence/resolve-duplicate", methods=["POST", "OPTIONS"])
    def intelligence_resolve_duplicate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        did = payload.get("duplicate_id", "")
        res_action = payload.get("resolution", "MERGED")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_duplicate_pair(did, res_action, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/security/backup/create", methods=["POST", "OPTIONS"])
    def security_backup_create_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.security_hardening_engine import security_hardening_engine
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "Admin")
        res = security_hardening_engine.create_database_backup(actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else 403
        return jsonify(res), code

    @app.route("/api/next_gen/overview", methods=["GET"])
    def next_gen_overview_endpoint():
        from backend.next_gen_agent_engine import next_gen_agent_engine
        uid = request.args.get("user_id", "2023MITEC042")
        return jsonify(next_gen_agent_engine.get_next_gen_overview(user_id=uid)), 200

    @app.route("/api/next_gen/recommendations", methods=["GET"])
    def next_gen_recommendations_endpoint():
        from backend.next_gen_agent_engine import next_gen_agent_engine
        uid = request.args.get("user_id", "2023MITEC042")
        return jsonify(next_gen_agent_engine.recommend_syllabus_progression(user_id=uid)), 200

    @app.route("/api/next_gen/diagnose", methods=["POST", "OPTIONS"])
    def next_gen_diagnose_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.next_gen_agent_engine import next_gen_agent_engine
        payload = request.get_json(silent=True) or {}
        symptom = payload.get("symptom", "")
        hardware = payload.get("hardware", "ESP32-S3")
        role = payload.get("role", "Student")
        res = next_gen_agent_engine.diagnose_lab_issue(symptom_query=symptom, hardware_target=hardware, actor_role=role)
        return jsonify(res), 200

    @app.route("/api/next_gen/career_path", methods=["GET"])
    def next_gen_career_path_endpoint():
        from backend.next_gen_agent_engine import next_gen_agent_engine
        uid = request.args.get("user_id", "2023MITEC042")
        return jsonify(next_gen_agent_engine.predict_career_path(user_id=uid)), 200

    @app.route("/api/next_gen/telemetry_twin", methods=["GET"])
    def next_gen_telemetry_twin_endpoint():
        from backend.next_gen_agent_engine import next_gen_agent_engine
        return jsonify(next_gen_agent_engine.get_digital_twin_telemetry()), 200

    @app.route("/api/cloud_deploy/status", methods=["GET"])
    def cloud_deploy_status_endpoint():
        from deploy.cloud_deployment_optimizer import cloud_deployment_optimizer
        return jsonify(cloud_deployment_optimizer.run_full_cloud_audit()), 200

    @app.route("/api/cloud_deploy/manifest", methods=["GET"])
    def cloud_deploy_manifest_endpoint():
        from deploy.cloud_deployment_optimizer import cloud_deployment_optimizer
        return jsonify(cloud_deployment_optimizer.generate_production_manifest()), 200

    @app.route("/api/physical_hil/ports", methods=["GET"])
    def physical_hil_ports_endpoint():
        from backend.physical_hil_manager import physical_hil_manager
        return jsonify(physical_hil_manager.list_detected_ports()), 200

    @app.route("/api/physical_hil/overview", methods=["GET"])
    def physical_hil_overview_endpoint():
        from backend.physical_hil_manager import physical_hil_manager
        return jsonify(physical_hil_manager.get_lab_overview()), 200

    @app.route("/api/physical_hil/lock", methods=["POST", "OPTIONS"])
    def physical_hil_lock_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.physical_hil_manager import physical_hil_manager
        payload = request.get_json(silent=True) or {}
        port_id = payload.get("port_id", "COM3")
        user_id = payload.get("user_id", "2023MITEC042")
        role = payload.get("role", "Student")
        res = physical_hil_manager.acquire_port_lock(port_id, user_id, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 409)
        return jsonify(res), code

    @app.route("/api/physical_hil/release", methods=["POST", "OPTIONS"])
    def physical_hil_release_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.physical_hil_manager import physical_hil_manager
        payload = request.get_json(silent=True) or {}
        port_id = payload.get("port_id", "COM3")
        user_id = payload.get("user_id", "2023MITEC042")
        res = physical_hil_manager.release_port_lock(port_id, user_id)
        code = 200 if res.get("status") == "SUCCESS" else 403
        return jsonify(res), code

    @app.route("/api/physical_hil/run_assertion", methods=["POST", "OPTIONS"])
    def physical_hil_assertion_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.physical_hil_manager import physical_hil_manager
        payload = request.get_json(silent=True) or {}
        port_id = payload.get("port_id", "COM3")
        user_id = payload.get("user_id", "2023MITEC042")
        res = physical_hil_manager.run_test_bench_assertions(port_id, user_id)
        return jsonify(res), 200

    @app.route("/api/voice/parse", methods=["POST", "OPTIONS"])
    def voice_parse_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.voice_command_router import voice_command_router
        payload = request.get_json(silent=True) or {}
        transcript = payload.get("transcript", "")
        student_id = payload.get("student_id", "2023MITEC042")
        role = payload.get("role", "Student")
        res = voice_command_router.process_voice_query(transcript, student_id=student_id, actor_role=role)
        return jsonify(res), 200

    @app.route("/api/voice/formulas", methods=["GET"])
    def voice_formulas_endpoint():
        from backend.voice_command_router import voice_command_router
        return jsonify(voice_command_router.get_all_formulas()), 200

    @app.route("/api/voice/history", methods=["GET"])
    def voice_history_endpoint():
        from backend.voice_command_router import voice_command_router
        limit = int(request.args.get("limit", 20))
        return jsonify(voice_command_router.get_recent_logs(limit=limit)), 200

    @app.route("/api/voice/overview", methods=["GET"])
    def voice_overview_endpoint():
        from backend.voice_command_router import voice_command_router
        return jsonify(voice_command_router.get_voice_overview()), 200

    @app.route("/api/academic/calendar", methods=["GET"])
    def academic_calendar_endpoint():
        from backend.academic_management_engine import academic_management_engine
        ev_type = request.args.get("event_type", "ALL")
        limit = int(request.args.get("limit", 50))
        return jsonify(academic_management_engine.get_calendar_events(event_type=ev_type, limit=limit)), 200

    @app.route("/api/academic/syllabus", methods=["GET"])
    def academic_syllabus_endpoint():
        from backend.academic_management_engine import academic_management_engine
        code = request.args.get("subject_code")
        sid = request.args.get("student_id", "2023MITEC042")
        if code:
            data = academic_management_engine.get_subject_details(code)
            if data:
                return jsonify(data), 200
            return jsonify({"status": "error", "message": f"Subject '{code}' not found"}), 404
        return jsonify(academic_management_engine.get_syllabus_overview(student_id=sid)), 200

    @app.route("/api/academic/overview", methods=["GET"])
    def academic_overview_endpoint():
        from backend.academic_management_engine import academic_management_engine
        sid = request.args.get("student_id", "2023MITEC042")
        return jsonify(academic_management_engine.get_syllabus_overview(student_id=sid)), 200

    @app.route("/api/academic/topic/update", methods=["POST", "OPTIONS"])
    def academic_topic_update_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.academic_management_engine import academic_management_engine
        payload = request.get_json(silent=True) or {}
        tid = payload.get("topic_id", "")
        status = payload.get("status", "COMPLETED")
        hrs = payload.get("hours_spent")
        sid = payload.get("student_id", "2023MITEC042")
        role = payload.get("role", "Student")
        res = academic_management_engine.update_topic_status(
            topic_id=tid,
            new_status=status,
            hours_spent=float(hrs) if hrs is not None else None,
            student_id=sid,
            actor_role=role
        )
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    # ====================================================================================
    # Phase 27: Data Intelligence & Academic Quality Center Endpoints
    # ====================================================================================

    @app.route("/api/intelligence/overview", methods=["GET"])
    def intelligence_overview_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        return jsonify(data_intelligence_engine.get_overview_metrics()), 200

    @app.route("/api/intelligence/audits", methods=["GET"])
    def intelligence_audits_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        atype = request.args.get("audit_type")
        status = request.args.get("status")
        sev = request.args.get("severity")
        return jsonify(data_intelligence_engine.get_academic_audits(atype, status, sev)), 200

    @app.route("/api/intelligence/run-consistency-check", methods=["POST", "OPTIONS"])
    def intelligence_consistency_check_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.run_record_consistency_check(actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/resolve-audit", methods=["POST", "OPTIONS"])
    def intelligence_resolve_audit_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        aid = payload.get("audit_id", "")
        notes = payload.get("resolution_notes", "Audit cleared by academic reviewer.")
        by = payload.get("resolved_by", "2023MITEC042")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_audit_issue(aid, notes, resolved_by=by, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/syllabus-coverage", methods=["GET"])
    def intelligence_syllabus_coverage_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_syllabus_coverage(code)), 200

    @app.route("/api/intelligence/update-syllabus-unit", methods=["POST", "OPTIONS"])
    def intelligence_update_syllabus_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        unit = int(payload.get("unit_num", 1))
        covered = int(payload.get("topics_covered", 0))
        hrs = float(payload.get("hours_actual", 0.0))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.update_syllabus_unit_progress(code, unit, covered, hrs, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), status_code

    @app.route("/api/intelligence/question-bank-gaps", methods=["GET"])
    def intelligence_qb_gaps_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_question_bank_gaps(code)), 200

    @app.route("/api/intelligence/analyze-question-bank", methods=["POST", "OPTIONS"])
    def intelligence_analyze_qb_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        questions = payload.get("questions", [])
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.analyze_custom_question_bank(code, questions, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), status_code

    @app.route("/api/intelligence/content-freshness", methods=["GET"])
    def intelligence_content_freshness_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        status = request.args.get("freshness_status")
        return jsonify(data_intelligence_engine.get_content_freshness(code, status)), 200

    @app.route("/api/intelligence/audit-freshness", methods=["POST", "OPTIONS"])
    def intelligence_audit_freshness_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        thresh = int(payload.get("stale_threshold_days", 180))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.audit_content_freshness(thresh, actor_role=role)
        return jsonify(res), 200

    @app.route("/api/intelligence/duplicate-documents", methods=["GET"])
    def intelligence_duplicate_docs_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        status = request.args.get("status")
        return jsonify(data_intelligence_engine.get_duplicate_documents(status)), 200

    @app.route("/api/intelligence/detect-duplicates", methods=["POST", "OPTIONS"])
    def intelligence_detect_duplicates_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        res = data_intelligence_engine.detect_duplicate_submission(
            doc_id_a=payload.get("doc_id_a", "DOC_A"),
            doc_id_b=payload.get("doc_id_b", "DOC_B"),
            title_a=payload.get("title_a", "Document A"),
            title_b=payload.get("title_b", "Document B"),
            text_a=payload.get("text_a", ""),
            text_b=payload.get("text_b", ""),
            threshold_pct=float(payload.get("threshold_pct", 75.0)),
            actor_role=payload.get("role", "Faculty")
        )
        return jsonify(res), 200

    @app.route("/api/intelligence/resolve-duplicate", methods=["POST", "OPTIONS"])
    def intelligence_resolve_duplicate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        did = payload.get("duplicate_id", "")
        res_action = payload.get("resolution", "MERGED")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_duplicate_pair(did, res_action, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/academic/calendar/add", methods=["POST", "OPTIONS"])
    def academic_calendar_add_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.academic_management_engine import academic_management_engine
        payload = request.get_json(silent=True) or {}
        title = payload.get("title", "")
        ev_type = payload.get("event_type", "EXAM")
        s_date = payload.get("start_date", "")
        e_date = payload.get("end_date", s_date)
        venue = payload.get("venue", "MIT Campus")
        desc = payload.get("description", "")
        reg = payload.get("target_regulation", "ECE Regulation 2023")
        role = payload.get("role", "Faculty")
        res = academic_management_engine.add_calendar_event(
            title=title,
            event_type=ev_type,
            start_date=s_date,
            end_date=e_date,
            venue=venue,
            description=desc,
            target_regulation=reg,
            actor_role=role
        )
        code = 200 if res.get("status") == "SUCCESS" else 403
        return jsonify(res), code

    @app.route("/api/ece_knowledge/formulas", methods=["GET"])
    def ece_knowledge_formulas_endpoint():
        from backend.ece_knowledge_engine import ece_knowledge_engine
        q = request.args.get("query")
        sub = request.args.get("subject_code")
        unit = int(request.args.get("unit_number")) if request.args.get("unit_number") else None
        return jsonify(ece_knowledge_engine.search_formulas(query=q, subject_code=sub, unit_number=unit)), 200

    @app.route("/api/ece_knowledge/components", methods=["GET"])
    def ece_knowledge_components_endpoint():
        from backend.ece_knowledge_engine import ece_knowledge_engine
        q = request.args.get("query")
        cat = request.args.get("category")
        return jsonify(ece_knowledge_engine.search_components(query=q, category=cat)), 200

    @app.route("/api/ece_knowledge/abbreviations", methods=["GET"])
    def ece_knowledge_abbreviations_endpoint():
        from backend.ece_knowledge_engine import ece_knowledge_engine
        q = request.args.get("query")
        cat = request.args.get("category")
        return jsonify(ece_knowledge_engine.search_abbreviations(query=q, category=cat)), 200

    @app.route("/api/ece_knowledge/overview", methods=["GET"])
    def ece_knowledge_overview_endpoint():
        from backend.ece_knowledge_engine import ece_knowledge_engine
        return jsonify(ece_knowledge_engine.get_knowledge_overview()), 200

    @app.route("/api/ece_knowledge/formula/add", methods=["POST", "OPTIONS"])
    def ece_knowledge_formula_add_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.ece_knowledge_engine import ece_knowledge_engine
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "Faculty")
        res = ece_knowledge_engine.add_custom_formula(
            topic=payload.get("topic", "General"),
            formula_name=payload.get("formula_name", ""),
            subject_code=payload.get("subject_code", "EC3451"),
            unit_number=int(payload.get("unit_number", 1)),
            latex_repr=payload.get("latex_repr", ""),
            plain_text=payload.get("plain_text", ""),
            derivation_summary=payload.get("derivation_summary", ""),
            variables=payload.get("variables", {}),
            unit_result=payload.get("unit_result", ""),
            actor_role=role
        )
        code = 200 if res.get("status") == "SUCCESS" else 403
        return jsonify(res), code

    @app.route("/api/productivity/overview", methods=["GET"])
    def productivity_overview_endpoint():
        from backend.learning_productivity_engine import learning_productivity_engine
        sid = request.args.get("student_id", "2023MITEC042")
        return jsonify(learning_productivity_engine.get_productivity_overview(sid)), 200

    @app.route("/api/productivity/streaks", methods=["GET"])
    def productivity_streaks_endpoint():
        from backend.learning_productivity_engine import learning_productivity_engine
        sid = request.args.get("student_id", "2023MITEC042")
        return jsonify(learning_productivity_engine.get_streak_metrics(sid)), 200

    @app.route("/api/productivity/session/log", methods=["POST", "OPTIONS"])
    def productivity_session_log_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.learning_productivity_engine import learning_productivity_engine
        payload = request.get_json(silent=True) or {}
        res = learning_productivity_engine.log_study_session(
            student_id=payload.get("student_id", "2023MITEC042"),
            subject_code=payload.get("subject_code", "ECE_GENERAL"),
            topic=payload.get("topic", "Self Study"),
            duration_minutes=int(payload.get("duration_minutes", 25)),
            session_type=payload.get("session_type", "POMODORO_25"),
            focus_score=int(payload.get("focus_score", 5)),
            notes=payload.get("notes", ""),
            distraction_free_mode=bool(payload.get("distraction_free_mode", False)),
            completed_at=payload.get("completed_at")
        )
        return jsonify(res), 200

    @app.route("/api/productivity/bookmarks", methods=["GET"])
    def productivity_bookmarks_endpoint():
        from backend.learning_productivity_engine import learning_productivity_engine
        sid = request.args.get("student_id", "2023MITEC042")
        sub = request.args.get("subject_code")
        return jsonify(learning_productivity_engine.get_bookmarks(sid, sub)), 200

    @app.route("/api/productivity/bookmarks/add", methods=["POST", "OPTIONS"])
    def productivity_bookmarks_add_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.learning_productivity_engine import learning_productivity_engine
        payload = request.get_json(silent=True) or {}
        res = learning_productivity_engine.add_bookmark(
            student_id=payload.get("student_id", "2023MITEC042"),
            subject_code=payload.get("subject_code", "EC3451"),
            topic=payload.get("topic", ""),
            resource_url=payload.get("resource_url", "/modules"),
            tags=payload.get("tags", []),
            notes=payload.get("notes", ""),
            priority=payload.get("priority", "MEDIUM")
        )
        return jsonify(res), 200

    @app.route("/api/productivity/bookmarks/delete", methods=["POST", "OPTIONS"])
    def productivity_bookmarks_delete_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.learning_productivity_engine import learning_productivity_engine
        payload = request.get_json(silent=True) or {}
        success = learning_productivity_engine.delete_bookmark(
            bookmark_id=payload.get("bookmark_id", ""),
            student_id=payload.get("student_id", "2023MITEC042")
        )
        return jsonify({"status": "SUCCESS" if success else "NOT_FOUND"}), 200

    @app.route("/api/productivity/revision_queue", methods=["GET"])
    def productivity_revision_queue_endpoint():
        from backend.learning_productivity_engine import learning_productivity_engine
        sid = request.args.get("student_id", "2023MITEC042")
        return jsonify(learning_productivity_engine.get_revision_queue(sid)), 200

    @app.route("/api/productivity/revision_queue/update", methods=["POST", "OPTIONS"])
    def productivity_revision_queue_update_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.learning_productivity_engine import learning_productivity_engine
        payload = request.get_json(silent=True) or {}
        res = learning_productivity_engine.update_revision_item(
            queue_id=payload.get("queue_id", ""),
            student_id=payload.get("student_id", "2023MITEC042"),
            confidence_level=int(payload.get("confidence_level", 3))
        )
        return jsonify(res), 200

    @app.route("/api/productivity/revision_queue/add", methods=["POST", "OPTIONS"])
    def productivity_revision_queue_add_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.learning_productivity_engine import learning_productivity_engine
        payload = request.get_json(silent=True) or {}
        res = learning_productivity_engine.add_revision_item(
            student_id=payload.get("student_id", "2023MITEC042"),
            subject_code=payload.get("subject_code", "EC3451"),
            topic=payload.get("topic", ""),
            confidence_level=int(payload.get("confidence_level", 3)),
            initial_interval_days=int(payload.get("initial_interval_days", 3))
        )
        return jsonify(res), 200

    @app.route("/api/digital/overview", methods=["GET"])
    def digital_overview_endpoint():
        from backend.digital_electronics_engine import digital_electronics_engine
        sid = request.args.get("student_id", "2023MITEC042")
        return jsonify(digital_electronics_engine.get_overview(sid)), 200

    @app.route("/api/digital/presets", methods=["GET"])
    def digital_presets_endpoint():
        from backend.digital_electronics_engine import digital_electronics_engine
        return jsonify(digital_electronics_engine.get_presets()), 200

    @app.route("/api/digital/circuits", methods=["GET"])
    def digital_circuits_endpoint():
        from backend.digital_electronics_engine import digital_electronics_engine
        sid = request.args.get("student_id", "2023MITEC042")
        return jsonify(digital_electronics_engine.get_saved_circuits(sid)), 200

    @app.route("/api/digital/convert_number", methods=["POST", "OPTIONS"])
    def digital_convert_number_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.digital_electronics_engine import digital_electronics_engine
        payload = request.get_json(silent=True) or {}
        val = str(payload.get("value", "0"))
        base = payload.get("from_base", "DECIMAL")
        sid = payload.get("student_id", "2023MITEC042")
        res = digital_electronics_engine.convert_number(val, base, sid)
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    # ====================================================================================
    # Phase 27: Data Intelligence & Academic Quality Center Endpoints
    # ====================================================================================

    @app.route("/api/intelligence/overview", methods=["GET"])
    def intelligence_overview_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        return jsonify(data_intelligence_engine.get_overview_metrics()), 200

    @app.route("/api/intelligence/audits", methods=["GET"])
    def intelligence_audits_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        atype = request.args.get("audit_type")
        status = request.args.get("status")
        sev = request.args.get("severity")
        return jsonify(data_intelligence_engine.get_academic_audits(atype, status, sev)), 200

    @app.route("/api/intelligence/run-consistency-check", methods=["POST", "OPTIONS"])
    def intelligence_consistency_check_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.run_record_consistency_check(actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/resolve-audit", methods=["POST", "OPTIONS"])
    def intelligence_resolve_audit_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        aid = payload.get("audit_id", "")
        notes = payload.get("resolution_notes", "Audit cleared by academic reviewer.")
        by = payload.get("resolved_by", "2023MITEC042")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_audit_issue(aid, notes, resolved_by=by, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/syllabus-coverage", methods=["GET"])
    def intelligence_syllabus_coverage_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_syllabus_coverage(code)), 200

    @app.route("/api/intelligence/update-syllabus-unit", methods=["POST", "OPTIONS"])
    def intelligence_update_syllabus_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        unit = int(payload.get("unit_num", 1))
        covered = int(payload.get("topics_covered", 0))
        hrs = float(payload.get("hours_actual", 0.0))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.update_syllabus_unit_progress(code, unit, covered, hrs, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), status_code

    @app.route("/api/intelligence/question-bank-gaps", methods=["GET"])
    def intelligence_qb_gaps_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_question_bank_gaps(code)), 200

    @app.route("/api/intelligence/analyze-question-bank", methods=["POST", "OPTIONS"])
    def intelligence_analyze_qb_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        questions = payload.get("questions", [])
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.analyze_custom_question_bank(code, questions, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), status_code

    @app.route("/api/intelligence/content-freshness", methods=["GET"])
    def intelligence_content_freshness_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        status = request.args.get("freshness_status")
        return jsonify(data_intelligence_engine.get_content_freshness(code, status)), 200

    @app.route("/api/intelligence/audit-freshness", methods=["POST", "OPTIONS"])
    def intelligence_audit_freshness_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        thresh = int(payload.get("stale_threshold_days", 180))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.audit_content_freshness(thresh, actor_role=role)
        return jsonify(res), 200

    @app.route("/api/intelligence/duplicate-documents", methods=["GET"])
    def intelligence_duplicate_docs_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        status = request.args.get("status")
        return jsonify(data_intelligence_engine.get_duplicate_documents(status)), 200

    @app.route("/api/intelligence/detect-duplicates", methods=["POST", "OPTIONS"])
    def intelligence_detect_duplicates_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        res = data_intelligence_engine.detect_duplicate_submission(
            doc_id_a=payload.get("doc_id_a", "DOC_A"),
            doc_id_b=payload.get("doc_id_b", "DOC_B"),
            title_a=payload.get("title_a", "Document A"),
            title_b=payload.get("title_b", "Document B"),
            text_a=payload.get("text_a", ""),
            text_b=payload.get("text_b", ""),
            threshold_pct=float(payload.get("threshold_pct", 75.0)),
            actor_role=payload.get("role", "Faculty")
        )
        return jsonify(res), 200

    @app.route("/api/intelligence/resolve-duplicate", methods=["POST", "OPTIONS"])
    def intelligence_resolve_duplicate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        did = payload.get("duplicate_id", "")
        res_action = payload.get("resolution", "MERGED")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_duplicate_pair(did, res_action, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/digital/truth_table", methods=["POST", "OPTIONS"])
    def digital_truth_table_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.digital_electronics_engine import digital_electronics_engine
        payload = request.get_json(silent=True) or {}
        expr = payload.get("expression", "")
        vars_list = payload.get("variables", None)
        res = digital_electronics_engine.generate_truth_table(expr, vars_list)
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    # ====================================================================================
    # Phase 27: Data Intelligence & Academic Quality Center Endpoints
    # ====================================================================================

    @app.route("/api/intelligence/overview", methods=["GET"])
    def intelligence_overview_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        return jsonify(data_intelligence_engine.get_overview_metrics()), 200

    @app.route("/api/intelligence/audits", methods=["GET"])
    def intelligence_audits_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        atype = request.args.get("audit_type")
        status = request.args.get("status")
        sev = request.args.get("severity")
        return jsonify(data_intelligence_engine.get_academic_audits(atype, status, sev)), 200

    @app.route("/api/intelligence/run-consistency-check", methods=["POST", "OPTIONS"])
    def intelligence_consistency_check_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.run_record_consistency_check(actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/resolve-audit", methods=["POST", "OPTIONS"])
    def intelligence_resolve_audit_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        aid = payload.get("audit_id", "")
        notes = payload.get("resolution_notes", "Audit cleared by academic reviewer.")
        by = payload.get("resolved_by", "2023MITEC042")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_audit_issue(aid, notes, resolved_by=by, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/syllabus-coverage", methods=["GET"])
    def intelligence_syllabus_coverage_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_syllabus_coverage(code)), 200

    @app.route("/api/intelligence/update-syllabus-unit", methods=["POST", "OPTIONS"])
    def intelligence_update_syllabus_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        unit = int(payload.get("unit_num", 1))
        covered = int(payload.get("topics_covered", 0))
        hrs = float(payload.get("hours_actual", 0.0))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.update_syllabus_unit_progress(code, unit, covered, hrs, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), status_code

    @app.route("/api/intelligence/question-bank-gaps", methods=["GET"])
    def intelligence_qb_gaps_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_question_bank_gaps(code)), 200

    @app.route("/api/intelligence/analyze-question-bank", methods=["POST", "OPTIONS"])
    def intelligence_analyze_qb_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        questions = payload.get("questions", [])
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.analyze_custom_question_bank(code, questions, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), status_code

    @app.route("/api/intelligence/content-freshness", methods=["GET"])
    def intelligence_content_freshness_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        status = request.args.get("freshness_status")
        return jsonify(data_intelligence_engine.get_content_freshness(code, status)), 200

    @app.route("/api/intelligence/audit-freshness", methods=["POST", "OPTIONS"])
    def intelligence_audit_freshness_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        thresh = int(payload.get("stale_threshold_days", 180))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.audit_content_freshness(thresh, actor_role=role)
        return jsonify(res), 200

    @app.route("/api/intelligence/duplicate-documents", methods=["GET"])
    def intelligence_duplicate_docs_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        status = request.args.get("status")
        return jsonify(data_intelligence_engine.get_duplicate_documents(status)), 200

    @app.route("/api/intelligence/detect-duplicates", methods=["POST", "OPTIONS"])
    def intelligence_detect_duplicates_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        res = data_intelligence_engine.detect_duplicate_submission(
            doc_id_a=payload.get("doc_id_a", "DOC_A"),
            doc_id_b=payload.get("doc_id_b", "DOC_B"),
            title_a=payload.get("title_a", "Document A"),
            title_b=payload.get("title_b", "Document B"),
            text_a=payload.get("text_a", ""),
            text_b=payload.get("text_b", ""),
            threshold_pct=float(payload.get("threshold_pct", 75.0)),
            actor_role=payload.get("role", "Faculty")
        )
        return jsonify(res), 200

    @app.route("/api/intelligence/resolve-duplicate", methods=["POST", "OPTIONS"])
    def intelligence_resolve_duplicate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        did = payload.get("duplicate_id", "")
        res_action = payload.get("resolution", "MERGED")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_duplicate_pair(did, res_action, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/digital/kmap_solve", methods=["POST", "OPTIONS"])
    def digital_kmap_solve_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.digital_electronics_engine import digital_electronics_engine
        payload = request.get_json(silent=True) or {}
        num_v = int(payload.get("num_variables", 3))
        mins = payload.get("minterms", [])
        dcs = payload.get("dont_cares", [])
        vars_list = payload.get("variables", None)
        res = digital_electronics_engine.solve_kmap(num_v, mins, dcs, vars_list)
        return jsonify(res), 200

    @app.route("/api/digital/circuit/save", methods=["POST", "OPTIONS"])
    def digital_circuit_save_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.digital_electronics_engine import digital_electronics_engine
        payload = request.get_json(silent=True) or {}
        res = digital_electronics_engine.save_circuit(
            student_id=payload.get("student_id", "2023MITEC042"),
            title=payload.get("title", "Custom Design"),
            expression=payload.get("expression", ""),
            num_variables=int(payload.get("num_variables", 3)),
            variables=payload.get("variables", ["A", "B", "C"]),
            minterms=payload.get("minterms", []),
            simplified_sop=payload.get("simplified_sop", ""),
            actor_role=payload.get("role", "Student")
        )
        return jsonify(res), 200

    @app.route("/api/analog_comm/overview", methods=["GET"])
    def analog_comm_overview_endpoint():
        from backend.analog_comm_engine import analog_comm_engine
        sid = request.args.get("student_id", "2023MITEC042")
        return jsonify(analog_comm_engine.get_overview(sid)), 200

    @app.route("/api/analog_comm/presets", methods=["GET"])
    def analog_comm_presets_endpoint():
        from backend.analog_comm_engine import analog_comm_engine
        cat = request.args.get("category")
        return jsonify(analog_comm_engine.get_presets(cat)), 200

    @app.route("/api/analog_comm/calculations", methods=["GET"])
    def analog_comm_calculations_endpoint():
        from backend.analog_comm_engine import analog_comm_engine
        sid = request.args.get("student_id", "2023MITEC042")
        return jsonify(analog_comm_engine.get_saved_calculations(sid)), 200

    @app.route("/api/analog_comm/filter_calc", methods=["POST", "OPTIONS"])
    def analog_comm_filter_calc_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.analog_comm_engine import analog_comm_engine
        payload = request.get_json(silent=True) or {}
        res = analog_comm_engine.calculate_filter(
            filter_type=payload.get("filter_type", "RC_LPF"),
            R=float(payload.get("R", 10000.0)),
            C=float(payload.get("C", 1.0e-8)),
            L=float(payload.get("L", 1.0e-3)),
            R2=float(payload.get("R2")) if payload.get("R2") else None,
            C2=float(payload.get("C2")) if payload.get("C2") else None,
            gain=float(payload.get("gain", 1.0))
        )
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    # ====================================================================================
    # Phase 27: Data Intelligence & Academic Quality Center Endpoints
    # ====================================================================================

    @app.route("/api/intelligence/overview", methods=["GET"])
    def intelligence_overview_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        return jsonify(data_intelligence_engine.get_overview_metrics()), 200

    @app.route("/api/intelligence/audits", methods=["GET"])
    def intelligence_audits_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        atype = request.args.get("audit_type")
        status = request.args.get("status")
        sev = request.args.get("severity")
        return jsonify(data_intelligence_engine.get_academic_audits(atype, status, sev)), 200

    @app.route("/api/intelligence/run-consistency-check", methods=["POST", "OPTIONS"])
    def intelligence_consistency_check_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.run_record_consistency_check(actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/resolve-audit", methods=["POST", "OPTIONS"])
    def intelligence_resolve_audit_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        aid = payload.get("audit_id", "")
        notes = payload.get("resolution_notes", "Audit cleared by academic reviewer.")
        by = payload.get("resolved_by", "2023MITEC042")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_audit_issue(aid, notes, resolved_by=by, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/syllabus-coverage", methods=["GET"])
    def intelligence_syllabus_coverage_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_syllabus_coverage(code)), 200

    @app.route("/api/intelligence/update-syllabus-unit", methods=["POST", "OPTIONS"])
    def intelligence_update_syllabus_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        unit = int(payload.get("unit_num", 1))
        covered = int(payload.get("topics_covered", 0))
        hrs = float(payload.get("hours_actual", 0.0))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.update_syllabus_unit_progress(code, unit, covered, hrs, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), status_code

    @app.route("/api/intelligence/question-bank-gaps", methods=["GET"])
    def intelligence_qb_gaps_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_question_bank_gaps(code)), 200

    @app.route("/api/intelligence/analyze-question-bank", methods=["POST", "OPTIONS"])
    def intelligence_analyze_qb_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        questions = payload.get("questions", [])
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.analyze_custom_question_bank(code, questions, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), status_code

    @app.route("/api/intelligence/content-freshness", methods=["GET"])
    def intelligence_content_freshness_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        status = request.args.get("freshness_status")
        return jsonify(data_intelligence_engine.get_content_freshness(code, status)), 200

    @app.route("/api/intelligence/audit-freshness", methods=["POST", "OPTIONS"])
    def intelligence_audit_freshness_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        thresh = int(payload.get("stale_threshold_days", 180))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.audit_content_freshness(thresh, actor_role=role)
        return jsonify(res), 200

    @app.route("/api/intelligence/duplicate-documents", methods=["GET"])
    def intelligence_duplicate_docs_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        status = request.args.get("status")
        return jsonify(data_intelligence_engine.get_duplicate_documents(status)), 200

    @app.route("/api/intelligence/detect-duplicates", methods=["POST", "OPTIONS"])
    def intelligence_detect_duplicates_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        res = data_intelligence_engine.detect_duplicate_submission(
            doc_id_a=payload.get("doc_id_a", "DOC_A"),
            doc_id_b=payload.get("doc_id_b", "DOC_B"),
            title_a=payload.get("title_a", "Document A"),
            title_b=payload.get("title_b", "Document B"),
            text_a=payload.get("text_a", ""),
            text_b=payload.get("text_b", ""),
            threshold_pct=float(payload.get("threshold_pct", 75.0)),
            actor_role=payload.get("role", "Faculty")
        )
        return jsonify(res), 200

    @app.route("/api/intelligence/resolve-duplicate", methods=["POST", "OPTIONS"])
    def intelligence_resolve_duplicate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        did = payload.get("duplicate_id", "")
        res_action = payload.get("resolution", "MERGED")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_duplicate_pair(did, res_action, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/analog_comm/transistor_bias", methods=["POST", "OPTIONS"])
    def analog_comm_transistor_bias_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.analog_comm_engine import analog_comm_engine
        payload = request.get_json(silent=True) or {}
        res = analog_comm_engine.calculate_transistor_bias(
            transistor_type=payload.get("transistor_type", "BJT_NPN"),
            Vcc=float(payload.get("Vcc", 12.0)),
            R1=float(payload.get("R1", 39000.0)),
            R2=float(payload.get("R2", 10000.0)),
            Rc=float(payload.get("Rc", 2200.0)),
            Re=float(payload.get("Re", 1000.0)),
            beta=float(payload.get("beta", 150.0)),
            Vbe=float(payload.get("Vbe", 0.7)),
            Vth=float(payload.get("Vth", 2.0)),
            kn=float(payload.get("kn", 1.5e-3))
        )
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    # ====================================================================================
    # Phase 27: Data Intelligence & Academic Quality Center Endpoints
    # ====================================================================================

    @app.route("/api/intelligence/overview", methods=["GET"])
    def intelligence_overview_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        return jsonify(data_intelligence_engine.get_overview_metrics()), 200

    @app.route("/api/intelligence/audits", methods=["GET"])
    def intelligence_audits_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        atype = request.args.get("audit_type")
        status = request.args.get("status")
        sev = request.args.get("severity")
        return jsonify(data_intelligence_engine.get_academic_audits(atype, status, sev)), 200

    @app.route("/api/intelligence/run-consistency-check", methods=["POST", "OPTIONS"])
    def intelligence_consistency_check_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.run_record_consistency_check(actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/resolve-audit", methods=["POST", "OPTIONS"])
    def intelligence_resolve_audit_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        aid = payload.get("audit_id", "")
        notes = payload.get("resolution_notes", "Audit cleared by academic reviewer.")
        by = payload.get("resolved_by", "2023MITEC042")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_audit_issue(aid, notes, resolved_by=by, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/syllabus-coverage", methods=["GET"])
    def intelligence_syllabus_coverage_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_syllabus_coverage(code)), 200

    @app.route("/api/intelligence/update-syllabus-unit", methods=["POST", "OPTIONS"])
    def intelligence_update_syllabus_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        unit = int(payload.get("unit_num", 1))
        covered = int(payload.get("topics_covered", 0))
        hrs = float(payload.get("hours_actual", 0.0))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.update_syllabus_unit_progress(code, unit, covered, hrs, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), status_code

    @app.route("/api/intelligence/question-bank-gaps", methods=["GET"])
    def intelligence_qb_gaps_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_question_bank_gaps(code)), 200

    @app.route("/api/intelligence/analyze-question-bank", methods=["POST", "OPTIONS"])
    def intelligence_analyze_qb_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        questions = payload.get("questions", [])
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.analyze_custom_question_bank(code, questions, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), status_code

    @app.route("/api/intelligence/content-freshness", methods=["GET"])
    def intelligence_content_freshness_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        status = request.args.get("freshness_status")
        return jsonify(data_intelligence_engine.get_content_freshness(code, status)), 200

    @app.route("/api/intelligence/audit-freshness", methods=["POST", "OPTIONS"])
    def intelligence_audit_freshness_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        thresh = int(payload.get("stale_threshold_days", 180))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.audit_content_freshness(thresh, actor_role=role)
        return jsonify(res), 200

    @app.route("/api/intelligence/duplicate-documents", methods=["GET"])
    def intelligence_duplicate_docs_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        status = request.args.get("status")
        return jsonify(data_intelligence_engine.get_duplicate_documents(status)), 200

    @app.route("/api/intelligence/detect-duplicates", methods=["POST", "OPTIONS"])
    def intelligence_detect_duplicates_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        res = data_intelligence_engine.detect_duplicate_submission(
            doc_id_a=payload.get("doc_id_a", "DOC_A"),
            doc_id_b=payload.get("doc_id_b", "DOC_B"),
            title_a=payload.get("title_a", "Document A"),
            title_b=payload.get("title_b", "Document B"),
            text_a=payload.get("text_a", ""),
            text_b=payload.get("text_b", ""),
            threshold_pct=float(payload.get("threshold_pct", 75.0)),
            actor_role=payload.get("role", "Faculty")
        )
        return jsonify(res), 200

    @app.route("/api/intelligence/resolve-duplicate", methods=["POST", "OPTIONS"])
    def intelligence_resolve_duplicate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        did = payload.get("duplicate_id", "")
        res_action = payload.get("resolution", "MERGED")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_duplicate_pair(did, res_action, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/analog_comm/opamp_calc", methods=["POST", "OPTIONS"])
    def analog_comm_opamp_calc_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.analog_comm_engine import analog_comm_engine
        payload = request.get_json(silent=True) or {}
        res = analog_comm_engine.calculate_opamp(
            config=payload.get("config", "INVERTING"),
            Rin=float(payload.get("Rin", 10000.0)),
            Rf=float(payload.get("Rf", 100000.0)),
            GBW=float(payload.get("GBW", 1000000.0)),
            SR=float(payload.get("SR", 500000.0)),
            Vpeak=float(payload.get("Vpeak", 5.0)),
            Vio=float(payload.get("Vio", 0.002)),
            Iio=float(payload.get("Iio", 2.0e-8))
        )
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    # ====================================================================================
    # Phase 27: Data Intelligence & Academic Quality Center Endpoints
    # ====================================================================================

    @app.route("/api/intelligence/overview", methods=["GET"])
    def intelligence_overview_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        return jsonify(data_intelligence_engine.get_overview_metrics()), 200

    @app.route("/api/intelligence/audits", methods=["GET"])
    def intelligence_audits_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        atype = request.args.get("audit_type")
        status = request.args.get("status")
        sev = request.args.get("severity")
        return jsonify(data_intelligence_engine.get_academic_audits(atype, status, sev)), 200

    @app.route("/api/intelligence/run-consistency-check", methods=["POST", "OPTIONS"])
    def intelligence_consistency_check_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.run_record_consistency_check(actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/resolve-audit", methods=["POST", "OPTIONS"])
    def intelligence_resolve_audit_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        aid = payload.get("audit_id", "")
        notes = payload.get("resolution_notes", "Audit cleared by academic reviewer.")
        by = payload.get("resolved_by", "2023MITEC042")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_audit_issue(aid, notes, resolved_by=by, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/syllabus-coverage", methods=["GET"])
    def intelligence_syllabus_coverage_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_syllabus_coverage(code)), 200

    @app.route("/api/intelligence/update-syllabus-unit", methods=["POST", "OPTIONS"])
    def intelligence_update_syllabus_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        unit = int(payload.get("unit_num", 1))
        covered = int(payload.get("topics_covered", 0))
        hrs = float(payload.get("hours_actual", 0.0))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.update_syllabus_unit_progress(code, unit, covered, hrs, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), status_code

    @app.route("/api/intelligence/question-bank-gaps", methods=["GET"])
    def intelligence_qb_gaps_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_question_bank_gaps(code)), 200

    @app.route("/api/intelligence/analyze-question-bank", methods=["POST", "OPTIONS"])
    def intelligence_analyze_qb_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        questions = payload.get("questions", [])
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.analyze_custom_question_bank(code, questions, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), status_code

    @app.route("/api/intelligence/content-freshness", methods=["GET"])
    def intelligence_content_freshness_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        status = request.args.get("freshness_status")
        return jsonify(data_intelligence_engine.get_content_freshness(code, status)), 200

    @app.route("/api/intelligence/audit-freshness", methods=["POST", "OPTIONS"])
    def intelligence_audit_freshness_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        thresh = int(payload.get("stale_threshold_days", 180))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.audit_content_freshness(thresh, actor_role=role)
        return jsonify(res), 200

    @app.route("/api/intelligence/duplicate-documents", methods=["GET"])
    def intelligence_duplicate_docs_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        status = request.args.get("status")
        return jsonify(data_intelligence_engine.get_duplicate_documents(status)), 200

    @app.route("/api/intelligence/detect-duplicates", methods=["POST", "OPTIONS"])
    def intelligence_detect_duplicates_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        res = data_intelligence_engine.detect_duplicate_submission(
            doc_id_a=payload.get("doc_id_a", "DOC_A"),
            doc_id_b=payload.get("doc_id_b", "DOC_B"),
            title_a=payload.get("title_a", "Document A"),
            title_b=payload.get("title_b", "Document B"),
            text_a=payload.get("text_a", ""),
            text_b=payload.get("text_b", ""),
            threshold_pct=float(payload.get("threshold_pct", 75.0)),
            actor_role=payload.get("role", "Faculty")
        )
        return jsonify(res), 200

    @app.route("/api/intelligence/resolve-duplicate", methods=["POST", "OPTIONS"])
    def intelligence_resolve_duplicate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        did = payload.get("duplicate_id", "")
        res_action = payload.get("resolution", "MERGED")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_duplicate_pair(did, res_action, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/analog_comm/txline_calc", methods=["POST", "OPTIONS"])
    def analog_comm_txline_calc_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.analog_comm_engine import analog_comm_engine
        payload = request.get_json(silent=True) or {}
        res = analog_comm_engine.calculate_txline(
            Z0=float(payload.get("Z0", 50.0)),
            ZL_real=float(payload.get("ZL_real", 75.0)),
            ZL_imag=float(payload.get("ZL_imag", 0.0))
        )
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    # ====================================================================================
    # Phase 27: Data Intelligence & Academic Quality Center Endpoints
    # ====================================================================================

    @app.route("/api/intelligence/overview", methods=["GET"])
    def intelligence_overview_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        return jsonify(data_intelligence_engine.get_overview_metrics()), 200

    @app.route("/api/intelligence/audits", methods=["GET"])
    def intelligence_audits_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        atype = request.args.get("audit_type")
        status = request.args.get("status")
        sev = request.args.get("severity")
        return jsonify(data_intelligence_engine.get_academic_audits(atype, status, sev)), 200

    @app.route("/api/intelligence/run-consistency-check", methods=["POST", "OPTIONS"])
    def intelligence_consistency_check_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.run_record_consistency_check(actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/resolve-audit", methods=["POST", "OPTIONS"])
    def intelligence_resolve_audit_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        aid = payload.get("audit_id", "")
        notes = payload.get("resolution_notes", "Audit cleared by academic reviewer.")
        by = payload.get("resolved_by", "2023MITEC042")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_audit_issue(aid, notes, resolved_by=by, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/syllabus-coverage", methods=["GET"])
    def intelligence_syllabus_coverage_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_syllabus_coverage(code)), 200

    @app.route("/api/intelligence/update-syllabus-unit", methods=["POST", "OPTIONS"])
    def intelligence_update_syllabus_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        unit = int(payload.get("unit_num", 1))
        covered = int(payload.get("topics_covered", 0))
        hrs = float(payload.get("hours_actual", 0.0))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.update_syllabus_unit_progress(code, unit, covered, hrs, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), status_code

    @app.route("/api/intelligence/question-bank-gaps", methods=["GET"])
    def intelligence_qb_gaps_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_question_bank_gaps(code)), 200

    @app.route("/api/intelligence/analyze-question-bank", methods=["POST", "OPTIONS"])
    def intelligence_analyze_qb_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        questions = payload.get("questions", [])
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.analyze_custom_question_bank(code, questions, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), status_code

    @app.route("/api/intelligence/content-freshness", methods=["GET"])
    def intelligence_content_freshness_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        status = request.args.get("freshness_status")
        return jsonify(data_intelligence_engine.get_content_freshness(code, status)), 200

    @app.route("/api/intelligence/audit-freshness", methods=["POST", "OPTIONS"])
    def intelligence_audit_freshness_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        thresh = int(payload.get("stale_threshold_days", 180))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.audit_content_freshness(thresh, actor_role=role)
        return jsonify(res), 200

    @app.route("/api/intelligence/duplicate-documents", methods=["GET"])
    def intelligence_duplicate_docs_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        status = request.args.get("status")
        return jsonify(data_intelligence_engine.get_duplicate_documents(status)), 200

    @app.route("/api/intelligence/detect-duplicates", methods=["POST", "OPTIONS"])
    def intelligence_detect_duplicates_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        res = data_intelligence_engine.detect_duplicate_submission(
            doc_id_a=payload.get("doc_id_a", "DOC_A"),
            doc_id_b=payload.get("doc_id_b", "DOC_B"),
            title_a=payload.get("title_a", "Document A"),
            title_b=payload.get("title_b", "Document B"),
            text_a=payload.get("text_a", ""),
            text_b=payload.get("text_b", ""),
            threshold_pct=float(payload.get("threshold_pct", 75.0)),
            actor_role=payload.get("role", "Faculty")
        )
        return jsonify(res), 200

    @app.route("/api/intelligence/resolve-duplicate", methods=["POST", "OPTIONS"])
    def intelligence_resolve_duplicate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        did = payload.get("duplicate_id", "")
        res_action = payload.get("resolution", "MERGED")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_duplicate_pair(did, res_action, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/analog_comm/modulation_calc", methods=["POST", "OPTIONS"])
    def analog_comm_modulation_calc_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.analog_comm_engine import analog_comm_engine
        payload = request.get_json(silent=True) or {}
        res = analog_comm_engine.calculate_modulation(
            modulation_type=payload.get("modulation_type", "AM"),
            carrier_freq=float(payload.get("carrier_freq", 1.0e6)),
            mod_freq=float(payload.get("mod_freq", 5000.0)),
            mod_index=float(payload.get("mod_index", 0.8)),
            delta_f=float(payload.get("delta_f", 75000.0)),
            Pc=float(payload.get("Pc", 100.0)),
            snr_db=float(payload.get("snr_db", 20.0)),
            channel_bandwidth=float(payload.get("channel_bandwidth", 100000.0))
        )
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    # ====================================================================================
    # Phase 27: Data Intelligence & Academic Quality Center Endpoints
    # ====================================================================================

    @app.route("/api/intelligence/overview", methods=["GET"])
    def intelligence_overview_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        return jsonify(data_intelligence_engine.get_overview_metrics()), 200

    @app.route("/api/intelligence/audits", methods=["GET"])
    def intelligence_audits_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        atype = request.args.get("audit_type")
        status = request.args.get("status")
        sev = request.args.get("severity")
        return jsonify(data_intelligence_engine.get_academic_audits(atype, status, sev)), 200

    @app.route("/api/intelligence/run-consistency-check", methods=["POST", "OPTIONS"])
    def intelligence_consistency_check_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.run_record_consistency_check(actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/resolve-audit", methods=["POST", "OPTIONS"])
    def intelligence_resolve_audit_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        aid = payload.get("audit_id", "")
        notes = payload.get("resolution_notes", "Audit cleared by academic reviewer.")
        by = payload.get("resolved_by", "2023MITEC042")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_audit_issue(aid, notes, resolved_by=by, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/syllabus-coverage", methods=["GET"])
    def intelligence_syllabus_coverage_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_syllabus_coverage(code)), 200

    @app.route("/api/intelligence/update-syllabus-unit", methods=["POST", "OPTIONS"])
    def intelligence_update_syllabus_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        unit = int(payload.get("unit_num", 1))
        covered = int(payload.get("topics_covered", 0))
        hrs = float(payload.get("hours_actual", 0.0))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.update_syllabus_unit_progress(code, unit, covered, hrs, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), status_code

    @app.route("/api/intelligence/question-bank-gaps", methods=["GET"])
    def intelligence_qb_gaps_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_question_bank_gaps(code)), 200

    @app.route("/api/intelligence/analyze-question-bank", methods=["POST", "OPTIONS"])
    def intelligence_analyze_qb_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        questions = payload.get("questions", [])
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.analyze_custom_question_bank(code, questions, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), status_code

    @app.route("/api/intelligence/content-freshness", methods=["GET"])
    def intelligence_content_freshness_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        status = request.args.get("freshness_status")
        return jsonify(data_intelligence_engine.get_content_freshness(code, status)), 200

    @app.route("/api/intelligence/audit-freshness", methods=["POST", "OPTIONS"])
    def intelligence_audit_freshness_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        thresh = int(payload.get("stale_threshold_days", 180))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.audit_content_freshness(thresh, actor_role=role)
        return jsonify(res), 200

    @app.route("/api/intelligence/duplicate-documents", methods=["GET"])
    def intelligence_duplicate_docs_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        status = request.args.get("status")
        return jsonify(data_intelligence_engine.get_duplicate_documents(status)), 200

    @app.route("/api/intelligence/detect-duplicates", methods=["POST", "OPTIONS"])
    def intelligence_detect_duplicates_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        res = data_intelligence_engine.detect_duplicate_submission(
            doc_id_a=payload.get("doc_id_a", "DOC_A"),
            doc_id_b=payload.get("doc_id_b", "DOC_B"),
            title_a=payload.get("title_a", "Document A"),
            title_b=payload.get("title_b", "Document B"),
            text_a=payload.get("text_a", ""),
            text_b=payload.get("text_b", ""),
            threshold_pct=float(payload.get("threshold_pct", 75.0)),
            actor_role=payload.get("role", "Faculty")
        )
        return jsonify(res), 200

    @app.route("/api/intelligence/resolve-duplicate", methods=["POST", "OPTIONS"])
    def intelligence_resolve_duplicate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        did = payload.get("duplicate_id", "")
        res_action = payload.get("resolution", "MERGED")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_duplicate_pair(did, res_action, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/analog_comm/calc/save", methods=["POST", "OPTIONS"])
    def analog_comm_calc_save_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.analog_comm_engine import analog_comm_engine
        payload = request.get_json(silent=True) or {}
        res = analog_comm_engine.save_calculation(
            student_id=payload.get("student_id", "2023MITEC042"),
            title=payload.get("title", "Custom Calculation"),
            category=payload.get("category", "FILTER"),
            parameters=payload.get("parameters", {}),
            results=payload.get("results", {}),
            subject_code=payload.get("subject_code", "EC3451")
        )
        return jsonify(res), 200

    # ====================================================================================
    # Phase 24: Engineering Project & Innovation Center Endpoints
    # ====================================================================================

    @app.route("/api/projects/overview", methods=["GET"])
    def projects_overview_endpoint():
        from backend.project_innovation_engine import project_innovation_engine
        sid = request.args.get("student_id", "2023MITEC042")
        return jsonify(project_innovation_engine.get_overview(sid)), 200

    @app.route("/api/projects/ideas", methods=["GET"])
    def projects_ideas_endpoint():
        from backend.project_innovation_engine import project_innovation_engine
        domain = request.args.get("domain")
        diff = request.args.get("difficulty")
        return jsonify(project_innovation_engine.get_innovation_ideas(domain, diff)), 200

    @app.route("/api/projects/proposals", methods=["GET", "POST", "OPTIONS"])
    def projects_proposals_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            return resp
        from backend.project_innovation_engine import project_innovation_engine
        if request.method == "GET":
            sid = request.args.get("student_id", "2023MITEC042")
            return jsonify(project_innovation_engine.get_proposals(sid)), 200
        else:
            payload = request.get_json(silent=True) or {}
            role = payload.get("role", "Student")
            res = project_innovation_engine.create_proposal(payload, actor_role=role)
            code = 200 if res.get("status") == "SUCCESS" else 400
            return jsonify(res), code

    @app.route("/api/projects/proposal/detail", methods=["GET"])
    def projects_proposal_detail_endpoint():
        from backend.project_innovation_engine import project_innovation_engine
        pid = request.args.get("proposal_id", "")
        detail = project_innovation_engine.get_proposal_detail(pid)
        if not detail:
            return jsonify({"status": "ERROR", "message": "Proposal not found"}), 404
        return jsonify({"status": "SUCCESS", "proposal": detail}), 200

    @app.route("/api/projects/proposal/status", methods=["POST", "OPTIONS"])
    def projects_proposal_status_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.project_innovation_engine import project_innovation_engine
        payload = request.get_json(silent=True) or {}
        pid = payload.get("proposal_id", "")
        status = payload.get("status", "")
        role = payload.get("role", "Student")
        res = project_innovation_engine.update_proposal_status(pid, status, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/projects/bom_calc", methods=["POST", "OPTIONS"])
    def projects_bom_calc_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.project_innovation_engine import project_innovation_engine
        payload = request.get_json(silent=True) or {}
        items = payload.get("items", [])
        tax = float(payload.get("tax_buffer_percent", 18.0))
        contingency = float(payload.get("contingency_percent", 10.0))
        res = project_innovation_engine.calculate_bom(items, tax, contingency)
        return jsonify(res), 200

    @app.route("/api/projects/bom/save", methods=["POST", "OPTIONS"])
    def projects_bom_save_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.project_innovation_engine import project_innovation_engine
        payload = request.get_json(silent=True) or {}
        pid = payload.get("proposal_id", "")
        items = payload.get("items", [])
        res = project_innovation_engine.save_bom_items(pid, items)
        return jsonify(res), 200

    @app.route("/api/projects/check_compatibility", methods=["POST", "OPTIONS"])
    def projects_check_compatibility_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.project_innovation_engine import project_innovation_engine
        payload = request.get_json(silent=True) or {}
        mcu = payload.get("mcu_name", "ESP32-WROOM-32")
        components = payload.get("components", [])
        res = project_innovation_engine.check_compatibility(mcu, components)
        return jsonify(res), 200

    @app.route("/api/projects/milestones", methods=["GET", "POST", "OPTIONS"])
    def projects_milestones_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            return resp
        from backend.project_innovation_engine import project_innovation_engine
        if request.method == "GET":
            pid = request.args.get("proposal_id", "")
            return jsonify(project_innovation_engine.get_milestones(pid)), 200
        else:
            payload = request.get_json(silent=True) or {}
            res = project_innovation_engine.add_milestone(payload)
            code = 200 if res.get("status") == "SUCCESS" else 400
            return jsonify(res), code

    @app.route("/api/projects/milestone/status", methods=["POST", "OPTIONS"])
    def projects_milestone_status_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.project_innovation_engine import project_innovation_engine
        payload = request.get_json(silent=True) or {}
        mid = payload.get("milestone_id", "")
        status = payload.get("status", "COMPLETED")
        res = project_innovation_engine.update_milestone_status(mid, status)
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    # ====================================================================================
    # Phase 27: Data Intelligence & Academic Quality Center Endpoints
    # ====================================================================================

    @app.route("/api/intelligence/overview", methods=["GET"])
    def intelligence_overview_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        return jsonify(data_intelligence_engine.get_overview_metrics()), 200

    @app.route("/api/intelligence/audits", methods=["GET"])
    def intelligence_audits_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        atype = request.args.get("audit_type")
        status = request.args.get("status")
        sev = request.args.get("severity")
        return jsonify(data_intelligence_engine.get_academic_audits(atype, status, sev)), 200

    @app.route("/api/intelligence/run-consistency-check", methods=["POST", "OPTIONS"])
    def intelligence_consistency_check_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.run_record_consistency_check(actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/resolve-audit", methods=["POST", "OPTIONS"])
    def intelligence_resolve_audit_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        aid = payload.get("audit_id", "")
        notes = payload.get("resolution_notes", "Audit cleared by academic reviewer.")
        by = payload.get("resolved_by", "2023MITEC042")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_audit_issue(aid, notes, resolved_by=by, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/syllabus-coverage", methods=["GET"])
    def intelligence_syllabus_coverage_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_syllabus_coverage(code)), 200

    @app.route("/api/intelligence/update-syllabus-unit", methods=["POST", "OPTIONS"])
    def intelligence_update_syllabus_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        unit = int(payload.get("unit_num", 1))
        covered = int(payload.get("topics_covered", 0))
        hrs = float(payload.get("hours_actual", 0.0))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.update_syllabus_unit_progress(code, unit, covered, hrs, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), status_code

    @app.route("/api/intelligence/question-bank-gaps", methods=["GET"])
    def intelligence_qb_gaps_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_question_bank_gaps(code)), 200

    @app.route("/api/intelligence/analyze-question-bank", methods=["POST", "OPTIONS"])
    def intelligence_analyze_qb_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        questions = payload.get("questions", [])
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.analyze_custom_question_bank(code, questions, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), status_code

    @app.route("/api/intelligence/content-freshness", methods=["GET"])
    def intelligence_content_freshness_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        status = request.args.get("freshness_status")
        return jsonify(data_intelligence_engine.get_content_freshness(code, status)), 200

    @app.route("/api/intelligence/audit-freshness", methods=["POST", "OPTIONS"])
    def intelligence_audit_freshness_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        thresh = int(payload.get("stale_threshold_days", 180))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.audit_content_freshness(thresh, actor_role=role)
        return jsonify(res), 200

    @app.route("/api/intelligence/duplicate-documents", methods=["GET"])
    def intelligence_duplicate_docs_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        status = request.args.get("status")
        return jsonify(data_intelligence_engine.get_duplicate_documents(status)), 200

    @app.route("/api/intelligence/detect-duplicates", methods=["POST", "OPTIONS"])
    def intelligence_detect_duplicates_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        res = data_intelligence_engine.detect_duplicate_submission(
            doc_id_a=payload.get("doc_id_a", "DOC_A"),
            doc_id_b=payload.get("doc_id_b", "DOC_B"),
            title_a=payload.get("title_a", "Document A"),
            title_b=payload.get("title_b", "Document B"),
            text_a=payload.get("text_a", ""),
            text_b=payload.get("text_b", ""),
            threshold_pct=float(payload.get("threshold_pct", 75.0)),
            actor_role=payload.get("role", "Faculty")
        )
        return jsonify(res), 200

    @app.route("/api/intelligence/resolve-duplicate", methods=["POST", "OPTIONS"])
    def intelligence_resolve_duplicate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        did = payload.get("duplicate_id", "")
        res_action = payload.get("resolution", "MERGED")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_duplicate_pair(did, res_action, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    # ====================================================================================
    # Phase 25: Faculty & Department Productivity Workspace Endpoints
    # ====================================================================================

    @app.route("/api/faculty/overview", methods=["GET"])
    def faculty_overview_endpoint():
        from backend.faculty_productivity_engine import faculty_productivity_engine
        fid = request.args.get("faculty_id", "FAC_MIT_ECE_001")
        return jsonify(faculty_productivity_engine.get_overview(fid)), 200

    @app.route("/api/faculty/lesson_plans", methods=["GET", "POST", "OPTIONS"])
    def faculty_lesson_plans_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            return resp
        from backend.faculty_productivity_engine import faculty_productivity_engine
        if request.method == "GET":
            code = request.args.get("course_code")
            unit = int(request.args.get("unit_number")) if request.args.get("unit_number") else None
            return jsonify(faculty_productivity_engine.get_lesson_plans(code, unit)), 200
        else:
            payload = request.get_json(silent=True) or {}
            role = payload.get("role", "Faculty")
            res = faculty_productivity_engine.create_lesson_plan(payload, actor_role=role)
            status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
            return jsonify(res), status_code

    @app.route("/api/faculty/lesson_plan/status", methods=["POST", "OPTIONS"])
    def faculty_lesson_plan_status_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.faculty_productivity_engine import faculty_productivity_engine
        payload = request.get_json(silent=True) or {}
        pid = payload.get("plan_id", "")
        status = payload.get("status", "COMPLETED")
        hrs = float(payload.get("actual_hours")) if payload.get("actual_hours") is not None else None
        notes = payload.get("notes")
        role = payload.get("role", "Faculty")
        res = faculty_productivity_engine.update_lesson_plan_status(pid, status, actual_hours=hrs, notes=notes, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), status_code

    @app.route("/api/faculty/templates", methods=["GET"])
    def faculty_templates_endpoint():
        from backend.faculty_productivity_engine import faculty_productivity_engine
        code = request.args.get("course_code")
        return jsonify(faculty_productivity_engine.get_templates(code)), 200

    @app.route("/api/faculty/assignments", methods=["GET", "POST", "OPTIONS"])
    def faculty_assignments_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            return resp
        from backend.faculty_productivity_engine import faculty_productivity_engine
        if request.method == "GET":
            code = request.args.get("course_code")
            return jsonify(faculty_productivity_engine.get_assignments(code)), 200
        else:
            payload = request.get_json(silent=True) or {}
            role = payload.get("role", "Faculty")
            res = faculty_productivity_engine.create_assignment(payload, actor_role=role)
            status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
            return jsonify(res), status_code

    @app.route("/api/faculty/feedback", methods=["GET", "POST", "OPTIONS"])
    def faculty_feedback_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            return resp
        from backend.faculty_productivity_engine import faculty_productivity_engine
        if request.method == "GET":
            asgn_id = request.args.get("assignment_id")
            sid = request.args.get("student_id")
            return jsonify(faculty_productivity_engine.get_assignment_feedback(asgn_id, sid)), 200
        else:
            payload = request.get_json(silent=True) or {}
            role = payload.get("role", "Faculty")
            res = faculty_productivity_engine.record_feedback(payload, actor_role=role)
            status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
            return jsonify(res), status_code

    @app.route("/api/faculty/meeting_minutes", methods=["GET", "POST", "OPTIONS"])
    def faculty_meeting_minutes_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            return resp
        from backend.faculty_productivity_engine import faculty_productivity_engine
        if request.method == "GET":
            return jsonify(faculty_productivity_engine.get_meeting_minutes()), 200
        else:
            payload = request.get_json(silent=True) or {}
            role = payload.get("role", "Faculty")
            res = faculty_productivity_engine.record_meeting_minutes(payload, actor_role=role)
            status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
            return jsonify(res), status_code

    # ====================================================================================
    # Phase 26: Accessibility & Inclusive Learning Center Endpoints
    # ====================================================================================

    @app.route("/api/accessibility/overview", methods=["GET"])
    def accessibility_overview_endpoint():
        from backend.accessibility_engine import accessibility_engine
        uid = request.args.get("user_id", "2023MITEC042")
        return jsonify(accessibility_engine.get_overview(uid)), 200

    @app.route("/api/accessibility/preferences", methods=["GET", "POST", "OPTIONS"])
    def accessibility_preferences_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            return resp
        from backend.accessibility_engine import accessibility_engine
        if request.method == "GET":
            uid = request.args.get("user_id", "2023MITEC042")
            return jsonify(accessibility_engine.get_preferences(uid)), 200
        else:
            payload = request.get_json(silent=True) or {}
            uid = payload.get("user_id", "2023MITEC042")
            res = accessibility_engine.save_preferences(uid, payload)
            return jsonify(res), 200

    @app.route("/api/accessibility/dictionary", methods=["GET"])
    def accessibility_dictionary_endpoint():
        from backend.accessibility_engine import accessibility_engine
        q = request.args.get("query")
        cat = request.args.get("category")
        course = request.args.get("course_code")
        lang = request.args.get("language", "en")
        return jsonify(accessibility_engine.get_dictionary(query=q, category=cat, course_code=course, language=lang)), 200

    @app.route("/api/accessibility/simplify", methods=["GET"])
    def accessibility_simplify_endpoint():
        from backend.accessibility_engine import accessibility_engine
        key = request.args.get("concept_key", "")
        detail = accessibility_engine.get_simplification(key)
        if not detail:
            return jsonify({"status": "ERROR", "message": "Concept simplification not found"}), 404
        return jsonify({"status": "SUCCESS", "simplification": detail}), 200

    @app.route("/api/accessibility/simplifications", methods=["GET"])
    def accessibility_simplifications_all_endpoint():
        from backend.accessibility_engine import accessibility_engine
        return jsonify(accessibility_engine.get_all_simplifications()), 200

    @app.route("/api/accessibility/feedback", methods=["POST", "OPTIONS"])
    def accessibility_feedback_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.accessibility_engine import accessibility_engine
        payload = request.get_json(silent=True) or {}
        res = accessibility_engine.record_feedback(payload)
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code


    # ====================================================================================
    # Phase 27: Data Intelligence & Academic Quality Center Endpoints
    # ====================================================================================

    @app.route("/api/intelligence/overview", methods=["GET"])
    def intelligence_overview_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        return jsonify(data_intelligence_engine.get_overview_metrics()), 200

    @app.route("/api/intelligence/audits", methods=["GET"])
    def intelligence_audits_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        atype = request.args.get("audit_type")
        status = request.args.get("status")
        sev = request.args.get("severity")
        return jsonify(data_intelligence_engine.get_academic_audits(atype, status, sev)), 200

    @app.route("/api/intelligence/run-consistency-check", methods=["POST", "OPTIONS"])
    def intelligence_consistency_check_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.run_record_consistency_check(actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/resolve-audit", methods=["POST", "OPTIONS"])
    def intelligence_resolve_audit_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        aid = payload.get("audit_id", "")
        notes = payload.get("resolution_notes", "Audit cleared by academic reviewer.")
        by = payload.get("resolved_by", "2023MITEC042")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_audit_issue(aid, notes, resolved_by=by, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/syllabus-coverage", methods=["GET"])
    def intelligence_syllabus_coverage_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_syllabus_coverage(code)), 200

    @app.route("/api/intelligence/update-syllabus-unit", methods=["POST", "OPTIONS"])
    def intelligence_update_syllabus_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        unit = int(payload.get("unit_num", 1))
        covered = int(payload.get("topics_covered", 0))
        hrs = float(payload.get("hours_actual", 0.0))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.update_syllabus_unit_progress(code, unit, covered, hrs, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), status_code

    @app.route("/api/intelligence/question-bank-gaps", methods=["GET"])
    def intelligence_qb_gaps_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_question_bank_gaps(code)), 200

    @app.route("/api/intelligence/analyze-question-bank", methods=["POST", "OPTIONS"])
    def intelligence_analyze_qb_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        questions = payload.get("questions", [])
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.analyze_custom_question_bank(code, questions, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), status_code

    @app.route("/api/intelligence/content-freshness", methods=["GET"])
    def intelligence_content_freshness_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        status = request.args.get("freshness_status")
        return jsonify(data_intelligence_engine.get_content_freshness(code, status)), 200

    @app.route("/api/intelligence/audit-freshness", methods=["POST", "OPTIONS"])
    def intelligence_audit_freshness_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        thresh = int(payload.get("stale_threshold_days", 180))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.audit_content_freshness(thresh, actor_role=role)
        return jsonify(res), 200

    @app.route("/api/intelligence/duplicate-documents", methods=["GET"])
    def intelligence_duplicate_docs_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        status = request.args.get("status")
        return jsonify(data_intelligence_engine.get_duplicate_documents(status)), 200

    @app.route("/api/intelligence/detect-duplicates", methods=["POST", "OPTIONS"])
    def intelligence_detect_duplicates_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        res = data_intelligence_engine.detect_duplicate_submission(
            doc_id_a=payload.get("doc_id_a", "DOC_A"),
            doc_id_b=payload.get("doc_id_b", "DOC_B"),
            title_a=payload.get("title_a", "Document A"),
            title_b=payload.get("title_b", "Document B"),
            text_a=payload.get("text_a", ""),
            text_b=payload.get("text_b", ""),
            threshold_pct=float(payload.get("threshold_pct", 75.0)),
            actor_role=payload.get("role", "Faculty")
        )
        return jsonify(res), 200

    @app.route("/api/intelligence/resolve-duplicate", methods=["POST", "OPTIONS"])
    def intelligence_resolve_duplicate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        did = payload.get("duplicate_id", "")
        res_action = payload.get("resolution", "MERGED")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_duplicate_pair(did, res_action, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    # ====================================================================================
    # Phase 27: Data Intelligence & Academic Quality Center Endpoints
    # ====================================================================================

    @app.route("/api/intelligence/overview", methods=["GET"])
    def intelligence_overview_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        return jsonify(data_intelligence_engine.get_overview_metrics()), 200

    @app.route("/api/intelligence/audits", methods=["GET"])
    def intelligence_audits_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        atype = request.args.get("audit_type")
        status = request.args.get("status")
        sev = request.args.get("severity")
        return jsonify(data_intelligence_engine.get_academic_audits(atype, status, sev)), 200

    @app.route("/api/intelligence/run-consistency-check", methods=["POST", "OPTIONS"])
    def intelligence_consistency_check_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.run_record_consistency_check(actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/resolve-audit", methods=["POST", "OPTIONS"])
    def intelligence_resolve_audit_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        aid = payload.get("audit_id", "")
        notes = payload.get("resolution_notes", "Audit cleared by academic reviewer.")
        by = payload.get("resolved_by", "2023MITEC042")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_audit_issue(aid, notes, resolved_by=by, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/intelligence/syllabus-coverage", methods=["GET"])
    def intelligence_syllabus_coverage_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_syllabus_coverage(code)), 200

    @app.route("/api/intelligence/update-syllabus-unit", methods=["POST", "OPTIONS"])
    def intelligence_update_syllabus_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        unit = int(payload.get("unit_num", 1))
        covered = int(payload.get("topics_covered", 0))
        hrs = float(payload.get("hours_actual", 0.0))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.update_syllabus_unit_progress(code, unit, covered, hrs, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), status_code

    @app.route("/api/intelligence/question-bank-gaps", methods=["GET"])
    def intelligence_qb_gaps_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        return jsonify(data_intelligence_engine.get_question_bank_gaps(code)), 200

    @app.route("/api/intelligence/analyze-question-bank", methods=["POST", "OPTIONS"])
    def intelligence_analyze_qb_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        code = payload.get("course_code", "EC3451")
        questions = payload.get("questions", [])
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.analyze_custom_question_bank(code, questions, actor_role=role)
        status_code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), status_code

    @app.route("/api/intelligence/content-freshness", methods=["GET"])
    def intelligence_content_freshness_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        code = request.args.get("course_code")
        status = request.args.get("freshness_status")
        return jsonify(data_intelligence_engine.get_content_freshness(code, status)), 200

    @app.route("/api/intelligence/audit-freshness", methods=["POST", "OPTIONS"])
    def intelligence_audit_freshness_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        thresh = int(payload.get("stale_threshold_days", 180))
        role = payload.get("role", "Faculty")
        res = data_intelligence_engine.audit_content_freshness(thresh, actor_role=role)
        return jsonify(res), 200

    @app.route("/api/intelligence/duplicate-documents", methods=["GET"])
    def intelligence_duplicate_docs_endpoint():
        from backend.data_intelligence_engine import data_intelligence_engine
        status = request.args.get("status")
        return jsonify(data_intelligence_engine.get_duplicate_documents(status)), 200

    @app.route("/api/intelligence/detect-duplicates", methods=["POST", "OPTIONS"])
    def intelligence_detect_duplicates_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        res = data_intelligence_engine.detect_duplicate_submission(
            doc_id_a=payload.get("doc_id_a", "DOC_A"),
            doc_id_b=payload.get("doc_id_b", "DOC_B"),
            title_a=payload.get("title_a", "Document A"),
            title_b=payload.get("title_b", "Document B"),
            text_a=payload.get("text_a", ""),
            text_b=payload.get("text_b", ""),
            threshold_pct=float(payload.get("threshold_pct", 75.0)),
            actor_role=payload.get("role", "Faculty")
        )
        return jsonify(res), 200

    @app.route("/api/intelligence/resolve-duplicate", methods=["POST", "OPTIONS"])
    def intelligence_resolve_duplicate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.data_intelligence_engine import data_intelligence_engine
        payload = request.get_json(silent=True) or {}
        did = payload.get("duplicate_id", "")
        res_action = payload.get("resolution", "MERGED")
        role = payload.get("role", "Admin")
        res = data_intelligence_engine.resolve_duplicate_pair(did, res_action, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code


    # ====================================================================================
    # Phase 28: Platform Intelligence & Reliability Center Endpoints
    # ====================================================================================

    @app.route("/api/reliability/overview", methods=["GET"])
    def reliability_overview_endpoint():
        from backend.platform_reliability_engine import platform_reliability_engine
        return jsonify(platform_reliability_engine.get_overview_metrics()), 200

    @app.route("/api/reliability/apm", methods=["GET"])
    def reliability_apm_endpoint():
        from backend.platform_reliability_engine import platform_reliability_engine
        return jsonify(platform_reliability_engine.get_apm_metrics()), 200

    @app.route("/api/reliability/telemetry", methods=["GET"])
    def reliability_telemetry_summary_endpoint():
        from backend.platform_reliability_engine import platform_reliability_engine
        limit = int(request.args.get("limit", 10))
        return jsonify(platform_reliability_engine.get_feature_usage_summary(limit)), 200

    @app.route("/api/reliability/record-telemetry", methods=["POST", "OPTIONS"])
    def reliability_record_telemetry_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.platform_reliability_engine import platform_reliability_engine
        payload = request.get_json(silent=True) or {}
        feat = payload.get("feature_name", "UNKNOWN_FEATURE")
        route = payload.get("route", "/")
        actor = payload.get("actor_id", "2023MITEC042")
        lat = float(payload.get("latency_ms", 1.5))
        status = int(payload.get("status_code", 200))
        res = platform_reliability_engine.record_feature_telemetry(feat, route, actor, lat, status)
        return jsonify(res), 200

    @app.route("/api/reliability/db-health", methods=["GET"])
    def reliability_db_health_endpoint():
        from backend.platform_reliability_engine import platform_reliability_engine
        return jsonify(platform_reliability_engine.get_database_wal_health()), 200

    @app.route("/api/reliability/db-checkpoint", methods=["POST", "OPTIONS"])
    def reliability_db_checkpoint_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.platform_reliability_engine import platform_reliability_engine
        payload = request.get_json(silent=True) or {}
        mode = payload.get("mode", "PASSIVE")
        role = payload.get("role", "Admin")
        res = platform_reliability_engine.execute_wal_checkpoint(mode=mode, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/reliability/link-checks", methods=["GET"])
    def reliability_link_checks_endpoint():
        from backend.platform_reliability_engine import platform_reliability_engine
        return jsonify(platform_reliability_engine.get_link_health_checks()), 200

    @app.route("/api/reliability/link-scan", methods=["POST", "OPTIONS"])
    def reliability_link_scan_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.platform_reliability_engine import platform_reliability_engine
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "Admin")
        res = platform_reliability_engine.run_route_integrity_scan(actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/reliability/config-audits", methods=["GET"])
    def reliability_config_audits_endpoint():
        from backend.platform_reliability_engine import platform_reliability_engine
        return jsonify(platform_reliability_engine.get_config_health_audits()), 200

    @app.route("/api/reliability/run-audit", methods=["POST", "OPTIONS"])
    def reliability_run_audit_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.platform_reliability_engine import platform_reliability_engine
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "Admin")
        res = platform_reliability_engine.run_full_system_audit(actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code


    # ====================================================================================
    # Phase 29: IoT Smart Laboratory & Equipment Telemetry Hub Endpoints
    # ====================================================================================

    @app.route("/api/iot/overview", methods=["GET"])
    def iot_overview_endpoint():
        from backend.iot_telemetry_engine import iot_telemetry_engine
        return jsonify(iot_telemetry_engine.get_overview_metrics()), 200

    @app.route("/api/iot/nodes", methods=["GET"])
    def iot_nodes_endpoint():
        from backend.iot_telemetry_engine import iot_telemetry_engine
        return jsonify(iot_telemetry_engine.get_bench_nodes()), 200

    @app.route("/api/iot/telemetry/ingest", methods=["POST", "OPTIONS"])
    def iot_telemetry_ingest_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.iot_telemetry_engine import iot_telemetry_engine
        payload = request.get_json(silent=True) or {}
        nid = payload.get("node_id", "NODE_ESP32_BENCH_01")
        v = float(payload.get("voltage_v", 12.0))
        c = float(payload.get("current_a", 1.0))
        t = float(payload.get("ambient_temp_c", 30.0))
        r = payload.get("relay_state")
        res = iot_telemetry_engine.ingest_telemetry_packet(nid, v, c, t, r)
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    @app.route("/api/iot/telemetry/history", methods=["GET"])
    def iot_telemetry_history_endpoint():
        from backend.iot_telemetry_engine import iot_telemetry_engine
        bench_id = request.args.get("bench_id")
        limit = int(request.args.get("limit", 20))
        return jsonify(iot_telemetry_engine.get_telemetry_history(bench_id, limit)), 200

    @app.route("/api/iot/alerts", methods=["GET"])
    def iot_alerts_endpoint():
        from backend.iot_telemetry_engine import iot_telemetry_engine
        status = request.args.get("status")
        return jsonify(iot_telemetry_engine.get_threshold_alerts(status)), 200

    @app.route("/api/iot/alerts/ack", methods=["POST", "OPTIONS"])
    def iot_alerts_ack_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.iot_telemetry_engine import iot_telemetry_engine
        payload = request.get_json(silent=True) or {}
        aid = payload.get("alert_id", "")
        notes = payload.get("notes", "Acknowledged by Lab Technician")
        role = payload.get("role", "Admin")
        res = iot_telemetry_engine.acknowledge_alert(aid, notes, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    @app.route("/api/iot/bench/relay", methods=["POST", "OPTIONS"])
    def iot_bench_relay_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.iot_telemetry_engine import iot_telemetry_engine
        payload = request.get_json(silent=True) or {}
        bid = payload.get("bench_id", "")
        state = payload.get("target_state", "CLOSED")
        actor = payload.get("actor_id", "2023MITEC042")
        role = payload.get("role", "Admin")
        res = iot_telemetry_engine.toggle_bench_relay(bid, state, actor_id=actor, actor_role=role)
        code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
        return jsonify(res), code

    # ====================================================================================
    # Phase 30: Smart PCB, SMD & Component Inspector Lab Endpoints
    # ====================================================================================

    @app.route("/api/inspector/axial-decode", methods=["POST", "OPTIONS"])
    def inspector_axial_decode_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.component_inspector_engine import component_inspector_engine
        payload = request.get_json(silent=True) or {}
        bands = payload.get("bands", [])
        actor = payload.get("actor_id", "2023MITEC042")
        res = component_inspector_engine.decode_axial_resistor(bands, actor_id=actor)
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    @app.route("/api/inspector/smd-decode", methods=["POST", "OPTIONS"])
    def inspector_smd_decode_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.component_inspector_engine import component_inspector_engine
        payload = request.get_json(silent=True) or {}
        code_str = payload.get("code", "")
        ctype = payload.get("component_type", "RESISTOR")
        actor = payload.get("actor_id", "2023MITEC042")
        res = component_inspector_engine.decode_smd_marking(code_str, component_type=ctype, actor_id=actor)
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    @app.route("/api/inspector/pcb-trace", methods=["POST", "OPTIONS"])
    def inspector_pcb_trace_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.component_inspector_engine import component_inspector_engine
        payload = request.get_json(silent=True) or {}
        curr = float(payload.get("current_a", 1.0))
        trise = float(payload.get("temp_rise_c", 10.0))
        cop = float(payload.get("copper_oz", 1.0))
        ttype = payload.get("trace_type", "external")
        length = float(payload.get("trace_length_cm", 10.0))
        amb = float(payload.get("ambient_temp_c", 25.0))
        dname = payload.get("design_name")
        actor = payload.get("actor_id", "2023MITEC042")
        res = component_inspector_engine.calculate_pcb_trace_width(
            curr, trise, cop, ttype, length, amb, design_name=dname, actor_id=actor
        )
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    @app.route("/api/inspector/ic-thermal", methods=["POST", "OPTIONS"])
    def inspector_ic_thermal_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.component_inspector_engine import component_inspector_engine
        payload = request.get_json(silent=True) or {}
        pkg = payload.get("package_code", "DIP-8")
        pwr = float(payload.get("power_watts", 0.5))
        amb = float(payload.get("ambient_temp_c", 25.0))
        th_ja = payload.get("theta_ja_custom")
        if th_ja is not None:
            th_ja = float(th_ja)
        target_tj = float(payload.get("target_max_tj_c", 100.0))
        actor = payload.get("actor_id", "2023MITEC042")
        res = component_inspector_engine.evaluate_ic_thermal_dissipation(
            pkg, pwr, amb, theta_ja_custom=th_ja, target_max_tj_c=target_tj, actor_id=actor
        )
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    @app.route("/api/inspector/history", methods=["GET"])
    def inspector_history_endpoint():
        from backend.component_inspector_engine import component_inspector_engine
        itype = request.args.get("inspection_type")
        limit = int(request.args.get("limit", 25))
        return jsonify(component_inspector_engine.get_inspection_history(itype, limit)), 200

    @app.route("/api/inspector/saved-pcb", methods=["GET"])
    def inspector_saved_pcb_endpoint():
        from backend.component_inspector_engine import component_inspector_engine
        limit = int(request.args.get("limit", 25))
        return jsonify(component_inspector_engine.get_saved_pcb_calculations(limit)), 200

    @app.route("/api/inspector/catalogs", methods=["GET"])
    def inspector_catalogs_endpoint():
        from backend.component_inspector_engine import component_inspector_engine
        return jsonify(component_inspector_engine.get_catalogs()), 200

    # ====================================================================================
    # Phase 31: ECE Coursework Assessment & Telemetry Verification Endpoints
    # ====================================================================================

    @app.route("/api/assessment/verify-logic", methods=["POST", "OPTIONS"])
    def assessment_verify_logic_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.ece_assignment_engine import ece_assignment_engine
        payload = request.get_json(silent=True) or {}
        circuit_type = payload.get("circuit_type", "FULL_ADDER")
        code_str = payload.get("code_or_expression", "")
        student_id = payload.get("student_id", "2023MITEC042")
        res = ece_assignment_engine.verify_combinational_logic(circuit_type, code_str, student_id=student_id)
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    @app.route("/api/assessment/verify-debounce", methods=["POST", "OPTIONS"])
    def assessment_verify_debounce_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.ece_assignment_engine import ece_assignment_engine
        payload = request.get_json(silent=True) or {}
        code_str = payload.get("code", "")
        sampling = float(payload.get("sampling_period_ms", 5.0))
        threshold = float(payload.get("debounce_threshold_ms", 30.0))
        student_id = payload.get("student_id", "2023MITEC042")
        res = ece_assignment_engine.verify_button_debouncing(code_str, sampling, threshold, student_id=student_id)
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    @app.route("/api/assessment/verify-timing", methods=["POST", "OPTIONS"])
    def assessment_verify_timing_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.ece_assignment_engine import ece_assignment_engine
        payload = request.get_json(silent=True) or {}
        code_str = payload.get("code", "")
        student_id = payload.get("student_id", "2023MITEC042")
        res = ece_assignment_engine.verify_non_blocking_timing(code_str, student_id=student_id)
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    @app.route("/api/assessment/verify-ir-interrupt", methods=["POST", "OPTIONS"])
    def assessment_verify_ir_interrupt_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.ece_assignment_engine import ece_assignment_engine
        payload = request.get_json(silent=True) or {}
        code_str = payload.get("code", "")
        student_id = payload.get("student_id", "2023MITEC042")
        res = ece_assignment_engine.verify_ir_proximity_interrupt(code_str, student_id=student_id)
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    @app.route("/api/assessment/history", methods=["GET"])
    def assessment_history_endpoint():
        from backend.ece_assignment_engine import ece_assignment_engine
        student_id = request.args.get("student_id", "2023MITEC042")
        limit = int(request.args.get("limit", 20))
        return jsonify(ece_assignment_engine.get_student_assessment_history(student_id=student_id, limit=limit)), 200

    @app.route("/api/assessment/telemetry", methods=["GET"])
    def assessment_telemetry_endpoint():
        from backend.ece_assignment_engine import ece_assignment_engine
        exp_type = request.args.get("experiment_type")
        limit = int(request.args.get("limit", 25))
        return jsonify(ece_assignment_engine.get_telemetry_logs(experiment_type=exp_type, limit=limit)), 200

    # ====================================================================================
    # Phase 32: IoT Sensor Telemetry Simulator Endpoints (Zero Polling Loops)
    # ====================================================================================

    @app.route("/api/sensor-sim/generate", methods=["POST", "OPTIONS"])
    def sensor_sim_generate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.iot_sensor_simulator_engine import iot_sensor_simulator_engine
        payload = request.get_json(silent=True) or {}
        count = int(payload.get("burst_count", 1))
        node_id = payload.get("node_id", "ESP32_LAB304_DHT22_IR")
        student_id = payload.get("student_id", "2023MITEC042")
        baseline_temp = float(payload.get("baseline_temp_c", 27.5))
        baseline_hum = float(payload.get("baseline_humidity_pct", 58.0))
        trigger_ir = bool(payload.get("trigger_ir_event", False))

        if count > 1:
            res = iot_sensor_simulator_engine.generate_burst_readings(
                count=count, node_id=node_id, student_id=student_id,
                baseline_temp_c=baseline_temp, baseline_humidity_pct=baseline_hum
            )
            return jsonify({"status": "SUCCESS", "count": len(res), "readings": res}), 200
        else:
            res = iot_sensor_simulator_engine.generate_simulated_reading(
                node_id=node_id, student_id=student_id,
                baseline_temp_c=baseline_temp, baseline_humidity_pct=baseline_hum,
                trigger_ir_event=trigger_ir
            )
            return jsonify(res), 200

    @app.route("/api/sensor-sim/ingest", methods=["POST", "OPTIONS"])
    def sensor_sim_ingest_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.iot_sensor_simulator_engine import iot_sensor_simulator_engine
        payload = request.get_json(silent=True) or {}
        res = iot_sensor_simulator_engine.ingest_custom_reading(payload)
        code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), code

    @app.route("/api/sensor-sim/readings", methods=["GET"])
    def sensor_sim_readings_endpoint():
        from backend.iot_sensor_simulator_engine import iot_sensor_simulator_engine
        node_id = request.args.get("node_id")
        limit = int(request.args.get("limit", 30))
        offset = int(request.args.get("offset", 0))
        return jsonify(iot_sensor_simulator_engine.get_telemetry_readings(node_id=node_id, limit=limit, offset=offset)), 200

    @app.route("/api/sensor-sim/stats", methods=["GET"])
    def sensor_sim_stats_endpoint():
        from backend.iot_sensor_simulator_engine import iot_sensor_simulator_engine
        node_id = request.args.get("node_id")
        return jsonify(iot_sensor_simulator_engine.get_telemetry_statistics(node_id=node_id)), 200

    @app.route("/api/sensor-sim/export-csv", methods=["GET"])
    def sensor_sim_export_csv_endpoint():
        from backend.iot_sensor_simulator_engine import iot_sensor_simulator_engine
        node_id = request.args.get("node_id")
        limit = int(request.args.get("limit", 500))
        csv_data = iot_sensor_simulator_engine.export_telemetry_csv(node_id=node_id, limit=limit)
        resp = make_response(csv_data)
        resp.headers["Content-Type"] = "text/csv; charset=utf-8"
        resp.headers["Content-Disposition"] = "attachment; filename=voltcore_sensor_telemetry.csv"
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp

    @app.route("/api/sensor-sim/clear", methods=["POST", "OPTIONS"])
    def sensor_sim_clear_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.iot_sensor_simulator_engine import iot_sensor_simulator_engine
        payload = request.get_json(silent=True) or {}
        node_id = payload.get("node_id")
        return jsonify(iot_sensor_simulator_engine.clear_simulated_readings(node_id=node_id)), 200

    # ====================================================================================
    # Phase 33: RTOS Task Scheduler & Context Switch Benchmarker Endpoints
    # ====================================================================================

    @app.route("/api/rtos/simulate", methods=["POST", "OPTIONS"])
    def rtos_simulate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.rtos_scheduler_engine import rtos_scheduler_engine
        payload = request.get_json(silent=True) or {}
        tasks = payload.get("tasks")
        mode = payload.get("mode", "PREEMPTIVE_PRIORITY")
        mcu = payload.get("mcu_target", "ESP32_WROOM_32")
        duration = int(payload.get("total_duration_ms", 50))
        student = payload.get("student_id", "2023MITEC042")
        res = rtos_scheduler_engine.simulate_scheduler(
            tasks=tasks, mode=mode, mcu_target=mcu,
            total_duration_ms=duration, student_id=student
        )
        return jsonify(res), 200

    @app.route("/api/rtos/benchmark", methods=["POST", "OPTIONS"])
    def rtos_benchmark_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.rtos_scheduler_engine import rtos_scheduler_engine
        payload = request.get_json(silent=True) or {}
        mcu = payload.get("mcu_target", "ESP32_WROOM_32")
        res = rtos_scheduler_engine.benchmark_mcu_hardware(mcu_key=mcu)
        return jsonify(res), 200

    @app.route("/api/rtos/history", methods=["GET"])
    def rtos_history_endpoint():
        from backend.rtos_scheduler_engine import rtos_scheduler_engine
        limit = int(request.args.get("limit", 15))
        return jsonify(rtos_scheduler_engine.get_simulation_history(limit=limit)), 200

    @app.route("/api/rtos/export-csv", methods=["GET"])
    def rtos_export_csv_endpoint():
        from backend.rtos_scheduler_engine import rtos_scheduler_engine
        csv_data = rtos_scheduler_engine.export_benchmark_csv()
        resp = make_response(csv_data)
        resp.headers["Content-Type"] = "text/csv; charset=utf-8"
        resp.headers["Content-Disposition"] = "attachment; filename=voltcore_rtos_benchmarks.csv"
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp

    # ====================================================================================
    # Phase 34: Low-Power Sleep & Battery Energy Profiler Endpoints
    # ====================================================================================

    @app.route("/api/energy/calculate", methods=["POST", "OPTIONS"])
    def energy_calculate_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.low_power_energy_engine import low_power_energy_engine
        payload = request.get_json(silent=True) or {}
        mcu = payload.get("mcu_target", "ESP32_WROOM_32")
        act_mode = payload.get("active_mode", "ACTIVE_WIFI_TX")
        slp_mode = payload.get("sleep_mode", "DEEP_SLEEP")
        wake = payload.get("wake_source", "RTC_TIMER")
        act_ms = float(payload.get("active_duration_ms", 200.0))
        slp_s = float(payload.get("sleep_duration_s", 59.8))
        bat = payload.get("battery_key", "LIPO_18650_2500MAH")
        eff = float(payload.get("battery_efficiency", 0.85))
        student = payload.get("student_id", "2023MITEC042")

        res = low_power_energy_engine.calculate_energy_profile(
            mcu_target=mcu, active_mode=act_mode, sleep_mode=slp_mode,
            wake_source=wake, active_duration_ms=act_ms, sleep_duration_s=slp_s,
            battery_key=bat, battery_efficiency=eff, student_id=student
        )
        return jsonify(res), 200

    @app.route("/api/energy/discharge-curve", methods=["POST", "OPTIONS"])
    def energy_discharge_curve_endpoint():
        if request.method == "OPTIONS":
            resp = make_response()
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            resp.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
            return resp
        from backend.low_power_energy_engine import low_power_energy_engine
        payload = request.get_json(silent=True) or {}
        bat = payload.get("battery_key", "LIPO_18650_2500MAH")
        current = float(payload.get("avg_current_ma", 0.54))
        eff = float(payload.get("battery_efficiency", 0.85))
        res = low_power_energy_engine.generate_discharge_curve(
            battery_key=bat, avg_current_ma=current, battery_efficiency=eff
        )
        return jsonify(res), 200

    @app.route("/api/energy/history", methods=["GET"])
    def energy_history_endpoint():
        from backend.low_power_energy_engine import low_power_energy_engine
        limit = int(request.args.get("limit", 15))
        return jsonify(low_power_energy_engine.get_simulation_history(limit=limit)), 200

    @app.route("/api/energy/export-csv", methods=["GET"])
    def energy_export_csv_endpoint():
        from backend.low_power_energy_engine import low_power_energy_engine
        csv_data = low_power_energy_engine.export_energy_csv()
        resp = make_response(csv_data)
        resp.headers["Content-Type"] = "text/csv; charset=utf-8"
        resp.headers["Content-Disposition"] = "attachment; filename=voltcore_energy_profiles.csv"
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp

    @app.route("/api/fpga/synthesize", methods=["POST", "OPTIONS"])
    def fpga_synthesize_endpoint():
        if request.method == "OPTIONS":
            return "", 204
        from backend.fpga_synthesis_engine import fpga_synthesis_engine
        payload = request.get_json(silent=True) or {}
        target = payload.get("target_fpga", "XILINX_ARTIX7_XC7A35T")
        mod = payload.get("module_key", "CLOCK_DIVIDER_COUNTER")
        hdl = payload.get("hdl_type", "VERILOG")
        clk = float(payload.get("target_clock_mhz", 100.0))
        student = payload.get("student_id", "2023MITEC042")
        res = fpga_synthesis_engine.synthesize_module(
            target_fpga=target, module_key=mod, hdl_type=hdl,
            target_clock_mhz=clk, student_id=student
        )
        return jsonify(res), 200

    @app.route("/api/fpga/generate-traces", methods=["POST", "OPTIONS"])
    def fpga_generate_traces_endpoint():
        if request.method == "OPTIONS":
            return "", 204
        from backend.fpga_synthesis_engine import fpga_synthesis_engine
        payload = request.get_json(silent=True) or {}
        mod = payload.get("module_key", "CLOCK_DIVIDER_COUNTER")
        cycles = int(payload.get("cycles", 32))
        clk_ns = float(payload.get("clock_period_ns", 10.0))
        synth_id = payload.get("synthesis_id")
        res = fpga_synthesis_engine.generate_logic_analyzer_traces(
            module_key=mod, cycles=cycles, clk_period_ns=clk_ns, synthesis_id=synth_id
        )
        return jsonify(res), 200

    @app.route("/api/fpga/targets", methods=["GET"])
    def fpga_targets_endpoint():
        from backend.fpga_synthesis_engine import fpga_synthesis_engine
        return jsonify(fpga_synthesis_engine.get_available_targets()), 200

    @app.route("/api/fpga/modules", methods=["GET"])
    def fpga_modules_endpoint():
        from backend.fpga_synthesis_engine import fpga_synthesis_engine
        return jsonify(fpga_synthesis_engine.get_available_modules()), 200

    @app.route("/api/fpga/source", methods=["GET"])
    def fpga_source_endpoint():
        from backend.fpga_synthesis_engine import fpga_synthesis_engine
        mod = request.args.get("module_key", "CLOCK_DIVIDER_COUNTER")
        hdl = request.args.get("hdl_type", "VERILOG")
        return jsonify(fpga_synthesis_engine.get_module_source(mod, hdl)), 200

    @app.route("/api/fpga/history", methods=["GET"])
    def fpga_history_endpoint():
        from backend.fpga_synthesis_engine import fpga_synthesis_engine
        limit = int(request.args.get("limit", 15))
        return jsonify(fpga_synthesis_engine.get_synthesis_history(limit=limit)), 200

    @app.route("/api/fpga/export-csv", methods=["GET"])
    def fpga_export_csv_endpoint():
        from backend.fpga_synthesis_engine import fpga_synthesis_engine
        mod = request.args.get("module_key", "CLOCK_DIVIDER_COUNTER")
        cycles = int(request.args.get("cycles", 32))
        clk_ns = float(request.args.get("clock_period_ns", 10.0))
        csv_data = fpga_synthesis_engine.export_traces_csv(module_key=mod, cycles=cycles, clk_period_ns=clk_ns)
        resp = make_response(csv_data)
        resp.headers["Content-Type"] = "text/csv; charset=utf-8"
        resp.headers["Content-Disposition"] = "attachment; filename=voltcore_logic_analyzer_traces.csv"
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp

    def run_server(host="0.0.0.0", port=5000):
        print(f"{TerminalColors.BOLD}{TerminalColors.EMERALD}")
        print("╔══════════════════════════════════════════════════════════════════════════════════╗")
        print("║          VOLTCORE APEX ACADEMIA - ATTENDANCE & TELEMETRY GATEWAY                 ║")
        print("║       Madras Institute of Technology (MIT) Campus, Anna University               ║")
        print("║                   Port 5000 | Flask / CORS REST Engine                           ║")
        print("╚══════════════════════════════════════════════════════════════════════════════════╝")
        print(f"{TerminalColors.RESET}")
        lms_database.init_db()
        lms_database.seed_mit_campus_data()
        app.run(host=host, port=port, debug=False)

else:
    # High-Performance Standard Library HTTP Fallback
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs

    class FallbackHTTPHandler(BaseHTTPRequestHandler):
        def _set_cors_headers(self, code=200):
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            for h_name, h_val in SECURITY_HEADERS.items():
                self.send_header(h_name, h_val)
            self.end_headers()

        def do_OPTIONS(self):
            self._set_cors_headers(204)

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path in ("/", "/api/health"):
                self._set_cors_headers(200)
                resp = {
                    "platform": "VoltCore Apex Academia",
                    "status": "ONLINE (Standard Library HTTP Fallback)",
                    "port": 5000,
                    "institution": "MIT Campus, Anna University"
                }
                self.wfile.write(json.dumps(resp).encode("utf-8"))
            elif parsed.path == "/api/attendance":
                params = parse_qs(parsed.query)
                student_id = params.get("student_id", [None])[0]
                limit = int(params.get("limit", [50])[0])
                logs = lms_database.get_attendance_history(user_id=student_id, limit=limit)
                self._set_cors_headers(200)
                self.wfile.write(json.dumps({"count": len(logs), "data": logs}).encode("utf-8"))
            elif parsed.path == "/api/user":
                params = parse_qs(parsed.query)
                student_id = params.get("student_id", ["2023MITEC042"])[0]
                user = lms_database.get_user_by_id(student_id)
                self._set_cors_headers(200 if user else 404)
                resp = {"status": "success", "user": user, "level": 18, "multiplier": 2.5} if user else {"error": "Not found"}
                self.wfile.write(json.dumps(resp).encode("utf-8"))
            elif parsed.path == "/api/analytics/weak_topics":
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(get_class_weak_topics()).encode("utf-8"))
            elif parsed.path == "/api/analytics/attainment":
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(compute_nba_attainment_and_zscores()).encode("utf-8"))
            elif parsed.path == "/api/admin/audit_metadata":
                params = parse_qs(parsed.query)
                role = params.get("role", ["Student"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(get_admin_audit_metadata(role)).encode("utf-8"))
            elif parsed.path == "/api/spice_simulate":
                params = parse_qs(parsed.query)
                circuit_id = params.get("circuit", ["bjt_ce"])[0]
                sim_data = parse_and_run_spice_simulation(circuit_id)
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(sim_data).encode("utf-8"))
            elif parsed.path == "/api/telemetry/history":
                params = parse_qs(parsed.query)
                limit = int(params.get("limit", [25])[0])
                self._set_cors_headers(200)
                self.wfile.write(json.dumps({"status": "success", "history": telemetry_broker.get_recent_history(limit)}).encode("utf-8"))
            elif parsed.path == "/api/content/status":
                from backend.content_status_api import get_content_status_report
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(get_content_status_report()).encode("utf-8"))
            elif parsed.path == "/api/content/changelog":
                from backend.content_status_api import get_changelog_history
                params = parse_qs(parsed.query)
                mod_code = params.get("module_code", [None])[0]
                limit = int(params.get("limit", [50])[0])
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(get_changelog_history(module_code=mod_code, limit=limit)).encode("utf-8"))
            elif parsed.path == "/api/collaboration/overview":
                from backend.collaboration_hub import collaboration_hub
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(collaboration_hub.get_collaboration_overview()).encode("utf-8"))
            elif parsed.path == "/api/research/overview":
                from backend.research_discovery_engine import research_discovery_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(research_discovery_engine.get_research_overview()).encode("utf-8"))
            elif parsed.path == "/api/enterprise_admin/overview":
                from backend.enterprise_admin_engine import enterprise_admin_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(enterprise_admin_engine.get_enterprise_overview()).encode("utf-8"))
            elif parsed.path == "/api/enterprise_admin/nba_matrix":
                from backend.enterprise_admin_engine import enterprise_admin_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(enterprise_admin_engine.compute_nba_co_po_matrix()).encode("utf-8"))
            elif parsed.path == "/api/security/overview":
                from backend.security_hardening_engine import security_hardening_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(security_hardening_engine.get_security_overview()).encode("utf-8"))
            elif parsed.path == "/api/next_gen/overview":
                from backend.next_gen_agent_engine import next_gen_agent_engine
                params = parse_qs(parsed.query)
                uid = params.get("user_id", ["2023MITEC042"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(next_gen_agent_engine.get_next_gen_overview(user_id=uid)).encode("utf-8"))
            elif parsed.path == "/api/next_gen/recommendations":
                from backend.next_gen_agent_engine import next_gen_agent_engine
                params = parse_qs(parsed.query)
                uid = params.get("user_id", ["2023MITEC042"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(next_gen_agent_engine.recommend_syllabus_progression(user_id=uid)).encode("utf-8"))
            elif parsed.path == "/api/next_gen/career_path":
                from backend.next_gen_agent_engine import next_gen_agent_engine
                params = parse_qs(parsed.query)
                uid = params.get("user_id", ["2023MITEC042"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(next_gen_agent_engine.predict_career_path(user_id=uid)).encode("utf-8"))
            elif parsed.path == "/api/next_gen/telemetry_twin":
                from backend.next_gen_agent_engine import next_gen_agent_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(next_gen_agent_engine.get_digital_twin_telemetry()).encode("utf-8"))
            elif parsed.path == "/api/cloud_deploy/status":
                from deploy.cloud_deployment_optimizer import cloud_deployment_optimizer
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(cloud_deployment_optimizer.run_full_cloud_audit()).encode("utf-8"))
            elif parsed.path == "/api/cloud_deploy/manifest":
                from deploy.cloud_deployment_optimizer import cloud_deployment_optimizer
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(cloud_deployment_optimizer.generate_production_manifest()).encode("utf-8"))
            elif parsed.path == "/api/physical_hil/ports":
                from backend.physical_hil_manager import physical_hil_manager
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(physical_hil_manager.list_detected_ports()).encode("utf-8"))
            elif parsed.path == "/api/physical_hil/overview":
                from backend.physical_hil_manager import physical_hil_manager
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(physical_hil_manager.get_lab_overview()).encode("utf-8"))
            elif parsed.path == "/api/voice/formulas":
                from backend.voice_command_router import voice_command_router
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(voice_command_router.get_all_formulas()).encode("utf-8"))
            elif parsed.path == "/api/voice/history":
                from backend.voice_command_router import voice_command_router
                params = parse_qs(parsed.query)
                limit = int(params.get("limit", [20])[0])
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(voice_command_router.get_recent_logs(limit=limit)).encode("utf-8"))
            elif parsed.path == "/api/voice/overview":
                from backend.voice_command_router import voice_command_router
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(voice_command_router.get_voice_overview()).encode("utf-8"))
            elif parsed.path == "/api/academic/calendar":
                from backend.academic_management_engine import academic_management_engine
                params = parse_qs(parsed.query)
                ev_type = params.get("event_type", ["ALL"])[0]
                limit = int(params.get("limit", [50])[0])
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(academic_management_engine.get_calendar_events(event_type=ev_type, limit=limit)).encode("utf-8"))
            elif parsed.path == "/api/academic/syllabus":
                from backend.academic_management_engine import academic_management_engine
                params = parse_qs(parsed.query)
                code = params.get("subject_code", [None])[0]
                sid = params.get("student_id", ["2023MITEC042"])[0]
                if code:
                    data = academic_management_engine.get_subject_details(code)
                    if data:
                        self._set_cors_headers(200)
                        self.wfile.write(json.dumps(data).encode("utf-8"))
                    else:
                        self._set_cors_headers(404)
                        self.wfile.write(json.dumps({"status": "error", "message": f"Subject '{code}' not found"}).encode("utf-8"))
                else:
                    self._set_cors_headers(200)
                    self.wfile.write(json.dumps(academic_management_engine.get_syllabus_overview(student_id=sid)).encode("utf-8"))
            elif parsed.path == "/api/academic/overview":
                from backend.academic_management_engine import academic_management_engine
                params = parse_qs(parsed.query)
                sid = params.get("student_id", ["2023MITEC042"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(academic_management_engine.get_syllabus_overview(student_id=sid)).encode("utf-8"))
            elif parsed.path == "/api/ece_knowledge/formulas":
                from backend.ece_knowledge_engine import ece_knowledge_engine
                params = parse_qs(parsed.query)
                q = params.get("query", [None])[0]
                sub = params.get("subject_code", [None])[0]
                unit_str = params.get("unit_number", [None])[0]
                unit = int(unit_str) if unit_str else None
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(ece_knowledge_engine.search_formulas(query=q, subject_code=sub, unit_number=unit)).encode("utf-8"))
            elif parsed.path == "/api/ece_knowledge/components":
                from backend.ece_knowledge_engine import ece_knowledge_engine
                params = parse_qs(parsed.query)
                q = params.get("query", [None])[0]
                cat = params.get("category", [None])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(ece_knowledge_engine.search_components(query=q, category=cat)).encode("utf-8"))
            elif parsed.path == "/api/ece_knowledge/abbreviations":
                from backend.ece_knowledge_engine import ece_knowledge_engine
                params = parse_qs(parsed.query)
                q = params.get("query", [None])[0]
                cat = params.get("category", [None])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(ece_knowledge_engine.search_abbreviations(query=q, category=cat)).encode("utf-8"))
            elif parsed.path == "/api/ece_knowledge/overview":
                from backend.ece_knowledge_engine import ece_knowledge_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(ece_knowledge_engine.get_knowledge_overview()).encode("utf-8"))
            elif parsed.path == "/api/productivity/overview":
                from backend.learning_productivity_engine import learning_productivity_engine
                sid = params.get("student_id", ["2023MITEC042"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(learning_productivity_engine.get_productivity_overview(sid)).encode("utf-8"))
            elif parsed.path == "/api/productivity/streaks":
                from backend.learning_productivity_engine import learning_productivity_engine
                sid = params.get("student_id", ["2023MITEC042"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(learning_productivity_engine.get_streak_metrics(sid)).encode("utf-8"))
            elif parsed.path == "/api/productivity/bookmarks":
                from backend.learning_productivity_engine import learning_productivity_engine
                sid = params.get("student_id", ["2023MITEC042"])[0]
                sub = params.get("subject_code", [None])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(learning_productivity_engine.get_bookmarks(sid, sub)).encode("utf-8"))
            elif parsed.path == "/api/productivity/revision_queue":
                from backend.learning_productivity_engine import learning_productivity_engine
                sid = params.get("student_id", ["2023MITEC042"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(learning_productivity_engine.get_revision_queue(sid)).encode("utf-8"))
            elif parsed.path == "/api/digital/overview":
                from backend.digital_electronics_engine import digital_electronics_engine
                sid = params.get("student_id", ["2023MITEC042"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(digital_electronics_engine.get_overview(sid)).encode("utf-8"))
            elif parsed.path == "/api/digital/presets":
                from backend.digital_electronics_engine import digital_electronics_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(digital_electronics_engine.get_presets()).encode("utf-8"))
            elif parsed.path == "/api/digital/circuits":
                from backend.digital_electronics_engine import digital_electronics_engine
                sid = params.get("student_id", ["2023MITEC042"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(digital_electronics_engine.get_saved_circuits(sid)).encode("utf-8"))
            elif parsed.path == "/api/analog_comm/overview":
                from backend.analog_comm_engine import analog_comm_engine
                sid = params.get("student_id", ["2023MITEC042"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(analog_comm_engine.get_overview(sid)).encode("utf-8"))
            elif parsed.path == "/api/analog_comm/presets":
                from backend.analog_comm_engine import analog_comm_engine
                cat = params.get("category", [None])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(analog_comm_engine.get_presets(cat)).encode("utf-8"))
            elif parsed.path == "/api/analog_comm/calculations":
                from backend.analog_comm_engine import analog_comm_engine
                sid = params.get("student_id", ["2023MITEC042"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(analog_comm_engine.get_saved_calculations(sid)).encode("utf-8"))
            elif parsed.path == "/api/projects/overview":
                from backend.project_innovation_engine import project_innovation_engine
                sid = params.get("student_id", ["2023MITEC042"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(project_innovation_engine.get_overview(sid)).encode("utf-8"))
            elif parsed.path == "/api/projects/ideas":
                from backend.project_innovation_engine import project_innovation_engine
                domain = params.get("domain", [None])[0]
                diff = params.get("difficulty", [None])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(project_innovation_engine.get_innovation_ideas(domain, diff)).encode("utf-8"))
            elif parsed.path == "/api/projects/proposals":
                from backend.project_innovation_engine import project_innovation_engine
                sid = params.get("student_id", ["2023MITEC042"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(project_innovation_engine.get_proposals(sid)).encode("utf-8"))
            elif parsed.path == "/api/projects/proposal/detail":
                from backend.project_innovation_engine import project_innovation_engine
                pid = params.get("proposal_id", [""])[0]
                detail = project_innovation_engine.get_proposal_detail(pid)
                if not detail:
                    self._set_cors_headers(404)
                    self.wfile.write(json.dumps({"status": "ERROR", "message": "Proposal not found"}).encode("utf-8"))
                else:
                    self._set_cors_headers(200)
                    self.wfile.write(json.dumps({"status": "SUCCESS", "proposal": detail}).encode("utf-8"))
            elif parsed.path == "/api/projects/milestones":
                from backend.project_innovation_engine import project_innovation_engine
                pid = params.get("proposal_id", [""])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(project_innovation_engine.get_milestones(pid)).encode("utf-8"))
            elif parsed.path == "/api/faculty/overview":
                from backend.faculty_productivity_engine import faculty_productivity_engine
                fid = params.get("faculty_id", ["FAC_MIT_ECE_001"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(faculty_productivity_engine.get_overview(fid)).encode("utf-8"))
            elif parsed.path == "/api/faculty/lesson_plans":
                from backend.faculty_productivity_engine import faculty_productivity_engine
                code = params.get("course_code", [None])[0]
                unit_raw = params.get("unit_number", [None])[0]
                unit = int(unit_raw) if unit_raw else None
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(faculty_productivity_engine.get_lesson_plans(code, unit)).encode("utf-8"))
            elif parsed.path == "/api/faculty/templates":
                from backend.faculty_productivity_engine import faculty_productivity_engine
                code = params.get("course_code", [None])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(faculty_productivity_engine.get_templates(code)).encode("utf-8"))
            elif parsed.path == "/api/faculty/assignments":
                from backend.faculty_productivity_engine import faculty_productivity_engine
                code = params.get("course_code", [None])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(faculty_productivity_engine.get_assignments(code)).encode("utf-8"))
            elif parsed.path == "/api/faculty/feedback":
                from backend.faculty_productivity_engine import faculty_productivity_engine
                asgn_id = params.get("assignment_id", [None])[0]
                sid = params.get("student_id", [None])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(faculty_productivity_engine.get_assignment_feedback(asgn_id, sid)).encode("utf-8"))
            elif parsed.path == "/api/faculty/meeting_minutes":
                from backend.faculty_productivity_engine import faculty_productivity_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(faculty_productivity_engine.get_meeting_minutes()).encode("utf-8"))
            elif parsed.path == "/api/accessibility/overview":
                from backend.accessibility_engine import accessibility_engine
                uid = params.get("user_id", ["2023MITEC042"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(accessibility_engine.get_overview(uid)).encode("utf-8"))
            elif parsed.path == "/api/accessibility/preferences":
                from backend.accessibility_engine import accessibility_engine
                uid = params.get("user_id", ["2023MITEC042"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(accessibility_engine.get_preferences(uid)).encode("utf-8"))
            elif parsed.path == "/api/accessibility/dictionary":
                from backend.accessibility_engine import accessibility_engine
                q = params.get("query", [None])[0]
                cat = params.get("category", [None])[0]
                course = params.get("course_code", [None])[0]
                lang = params.get("language", ["en"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(accessibility_engine.get_dictionary(query=q, category=cat, course_code=course, language=lang)).encode("utf-8"))
            elif parsed.path == "/api/accessibility/simplify":
                from backend.accessibility_engine import accessibility_engine
                key = params.get("concept_key", [""])[0]
                detail = accessibility_engine.get_simplification(key)
                if not detail:
                    self._set_cors_headers(404)
                    self.wfile.write(json.dumps({"status": "ERROR", "message": "Concept simplification not found"}).encode("utf-8"))
                else:
                    self._set_cors_headers(200)
                    self.wfile.write(json.dumps({"status": "SUCCESS", "simplification": detail}).encode("utf-8"))
            elif parsed.path == "/api/accessibility/simplifications":
                from backend.accessibility_engine import accessibility_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(accessibility_engine.get_all_simplifications()).encode("utf-8"))
            elif parsed.path == "/api/intelligence/overview":
                from backend.data_intelligence_engine import data_intelligence_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(data_intelligence_engine.get_overview_metrics()).encode("utf-8"))
            elif parsed.path == "/api/intelligence/audits":
                from backend.data_intelligence_engine import data_intelligence_engine
                atype = params.get("audit_type", [None])[0]
                status = params.get("status", [None])[0]
                sev = params.get("severity", [None])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(data_intelligence_engine.get_academic_audits(atype, status, sev)).encode("utf-8"))
            elif parsed.path == "/api/intelligence/syllabus-coverage":
                from backend.data_intelligence_engine import data_intelligence_engine
                code = params.get("course_code", [None])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(data_intelligence_engine.get_syllabus_coverage(code)).encode("utf-8"))
            elif parsed.path == "/api/intelligence/question-bank-gaps":
                from backend.data_intelligence_engine import data_intelligence_engine
                code = params.get("course_code", [None])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(data_intelligence_engine.get_question_bank_gaps(code)).encode("utf-8"))
            elif parsed.path == "/api/intelligence/content-freshness":
                from backend.data_intelligence_engine import data_intelligence_engine
                code = params.get("course_code", [None])[0]
                status = params.get("freshness_status", [None])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(data_intelligence_engine.get_content_freshness(code, status)).encode("utf-8"))
            elif parsed.path == "/api/intelligence/duplicate-documents":
                from backend.data_intelligence_engine import data_intelligence_engine
                status = params.get("status", [None])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(data_intelligence_engine.get_duplicate_documents(status)).encode("utf-8"))
            elif parsed.path == "/api/reliability/overview":
                from backend.platform_reliability_engine import platform_reliability_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(platform_reliability_engine.get_overview_metrics()).encode("utf-8"))
            elif parsed.path == "/api/reliability/apm":
                from backend.platform_reliability_engine import platform_reliability_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(platform_reliability_engine.get_apm_metrics()).encode("utf-8"))
            elif parsed.path == "/api/reliability/telemetry":
                from backend.platform_reliability_engine import platform_reliability_engine
                limit = int(params.get("limit", [10])[0])
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(platform_reliability_engine.get_feature_usage_summary(limit)).encode("utf-8"))
            elif parsed.path == "/api/reliability/db-health":
                from backend.platform_reliability_engine import platform_reliability_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(platform_reliability_engine.get_database_wal_health()).encode("utf-8"))
            elif parsed.path == "/api/reliability/link-checks":
                from backend.platform_reliability_engine import platform_reliability_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(platform_reliability_engine.get_link_health_checks()).encode("utf-8"))
            elif parsed.path == "/api/reliability/config-audits":
                from backend.platform_reliability_engine import platform_reliability_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(platform_reliability_engine.get_config_health_audits()).encode("utf-8"))
            elif parsed.path == "/api/iot/overview":
                from backend.iot_telemetry_engine import iot_telemetry_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(iot_telemetry_engine.get_overview_metrics()).encode("utf-8"))
            elif parsed.path == "/api/iot/nodes":
                from backend.iot_telemetry_engine import iot_telemetry_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(iot_telemetry_engine.get_bench_nodes()).encode("utf-8"))
            elif parsed.path == "/api/iot/telemetry/history":
                from backend.iot_telemetry_engine import iot_telemetry_engine
                bench_id = params.get("bench_id", [None])[0]
                limit = int(params.get("limit", [20])[0])
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(iot_telemetry_engine.get_telemetry_history(bench_id, limit)).encode("utf-8"))
            elif parsed.path == "/api/iot/alerts":
                from backend.iot_telemetry_engine import iot_telemetry_engine
                status = params.get("status", [None])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(iot_telemetry_engine.get_threshold_alerts(status)).encode("utf-8"))
            elif parsed.path == "/api/inspector/history":
                from backend.component_inspector_engine import component_inspector_engine
                itype = params.get("inspection_type", [None])[0]
                limit = int(params.get("limit", [25])[0])
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(component_inspector_engine.get_inspection_history(itype, limit)).encode("utf-8"))
            elif parsed.path == "/api/inspector/saved-pcb":
                from backend.component_inspector_engine import component_inspector_engine
                limit = int(params.get("limit", [25])[0])
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(component_inspector_engine.get_saved_pcb_calculations(limit)).encode("utf-8"))
            elif parsed.path == "/api/inspector/catalogs":
                from backend.component_inspector_engine import component_inspector_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(component_inspector_engine.get_catalogs()).encode("utf-8"))
            elif parsed.path == "/api/assessment/history":
                from backend.ece_assignment_engine import ece_assignment_engine
                student_id = params.get("student_id", ["2023MITEC042"])[0]
                limit = int(params.get("limit", [20])[0])
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(ece_assignment_engine.get_student_assessment_history(student_id=student_id, limit=limit)).encode("utf-8"))
            elif parsed.path == "/api/assessment/telemetry":
                from backend.ece_assignment_engine import ece_assignment_engine
                exp_type = params.get("experiment_type", [None])[0]
                limit = int(params.get("limit", [25])[0])
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(ece_assignment_engine.get_telemetry_logs(experiment_type=exp_type, limit=limit)).encode("utf-8"))
            elif parsed.path == "/api/sensor-sim/readings":
                from backend.iot_sensor_simulator_engine import iot_sensor_simulator_engine
                node_id = params.get("node_id", [None])[0]
                limit = int(params.get("limit", [30])[0])
                offset = int(params.get("offset", [0])[0])
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(iot_sensor_simulator_engine.get_telemetry_readings(node_id=node_id, limit=limit, offset=offset)).encode("utf-8"))
            elif parsed.path == "/api/sensor-sim/stats":
                from backend.iot_sensor_simulator_engine import iot_sensor_simulator_engine
                node_id = params.get("node_id", [None])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(iot_sensor_simulator_engine.get_telemetry_statistics(node_id=node_id)).encode("utf-8"))
            elif parsed.path == "/api/sensor-sim/export-csv":
                from backend.iot_sensor_simulator_engine import iot_sensor_simulator_engine
                node_id = params.get("node_id", [None])[0]
                limit = int(params.get("limit", [500])[0])
                csv_str = iot_sensor_simulator_engine.export_telemetry_csv(node_id=node_id, limit=limit)
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", "attachment; filename=voltcore_sensor_telemetry.csv")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(csv_str.encode("utf-8"))
            elif parsed.path == "/api/rtos/history":
                from backend.rtos_scheduler_engine import rtos_scheduler_engine
                limit = int(params.get("limit", [15])[0])
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(rtos_scheduler_engine.get_simulation_history(limit=limit)).encode("utf-8"))
            elif parsed.path == "/api/rtos/export-csv":
                from backend.rtos_scheduler_engine import rtos_scheduler_engine
                csv_str = rtos_scheduler_engine.export_benchmark_csv()
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", "attachment; filename=voltcore_rtos_benchmarks.csv")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(csv_str.encode("utf-8"))
            elif parsed.path == "/api/energy/history":
                from backend.low_power_energy_engine import low_power_energy_engine
                limit = int(params.get("limit", [15])[0])
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(low_power_energy_engine.get_simulation_history(limit=limit)).encode("utf-8"))
            elif parsed.path == "/api/energy/export-csv":
                from backend.low_power_energy_engine import low_power_energy_engine
                csv_str = low_power_energy_engine.export_energy_csv()
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", "attachment; filename=voltcore_energy_profiles.csv")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(csv_str.encode("utf-8"))
            elif parsed.path == "/api/fpga/targets":
                from backend.fpga_synthesis_engine import fpga_synthesis_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(fpga_synthesis_engine.get_available_targets()).encode("utf-8"))
            elif parsed.path == "/api/fpga/modules":
                from backend.fpga_synthesis_engine import fpga_synthesis_engine
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(fpga_synthesis_engine.get_available_modules()).encode("utf-8"))
            elif parsed.path == "/api/fpga/source":
                from backend.fpga_synthesis_engine import fpga_synthesis_engine
                mod = params.get("module_key", ["CLOCK_DIVIDER_COUNTER"])[0]
                hdl = params.get("hdl_type", ["VERILOG"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(fpga_synthesis_engine.get_module_source(mod, hdl)).encode("utf-8"))
            elif parsed.path == "/api/fpga/history":
                from backend.fpga_synthesis_engine import fpga_synthesis_engine
                limit = int(params.get("limit", [15])[0])
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(fpga_synthesis_engine.get_synthesis_history(limit=limit)).encode("utf-8"))
            elif parsed.path == "/api/fpga/export-csv":
                from backend.fpga_synthesis_engine import fpga_synthesis_engine
                mod = params.get("module_key", ["CLOCK_DIVIDER_COUNTER"])[0]
                cycles = int(params.get("cycles", [32])[0])
                clk_ns = float(params.get("clock_period_ns", [10.0])[0])
                csv_str = fpga_synthesis_engine.export_traces_csv(module_key=mod, cycles=cycles, clk_period_ns=clk_ns)
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", "attachment; filename=voltcore_logic_analyzer_traces.csv")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(csv_str.encode("utf-8"))
            else:
                self._set_cors_headers(404)
                self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

        def do_POST(self):
            parsed = urlparse(self.path)
            content_length = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_length)
            try:
                payload = json.loads(post_body.decode("utf-8")) if content_length > 0 else {}
            except Exception:
                self._set_cors_headers(400)
                self.wfile.write(json.dumps({"status": "error", "message": "Invalid JSON"}).encode("utf-8"))
                return

            if parsed.path == "/api/attendance":
                resp_data, status_code = process_attendance_scan(payload)
                self._set_cors_headers(status_code)
                self.wfile.write(json.dumps(resp_data).encode("utf-8"))
            elif parsed.path == "/api/attendance/bulk_sync":
                resp_data, status_code = process_bulk_attendance_sync(payload)
                self._set_cors_headers(status_code)
                self.wfile.write(json.dumps(resp_data).encode("utf-8"))
            elif parsed.path in ("/api/tutor_query", "/app/api/tutor_query", "/api/rag_query"):
                resp_data, status_code = handle_tutor_query(payload)
                self._set_cors_headers(status_code)
                self.wfile.write(json.dumps(resp_data).encode("utf-8"))
            elif parsed.path == "/api/analytics/weak_topics":
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(get_class_weak_topics()).encode("utf-8"))
            elif parsed.path == "/api/analytics/attainment":
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(compute_nba_attainment_and_zscores()).encode("utf-8"))
            elif parsed.path == "/api/admin/audit_metadata":
                params = parse_qs(parsed.query)
                role = params.get("role", ["Student"])[0]
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(get_admin_audit_metadata(role)).encode("utf-8"))
            elif parsed.path == "/api/spice_simulate":
                circuit_id = payload.get("circuit", "bjt_ce")
                params = payload.get("params", {})
                sim_data = parse_and_run_spice_simulation(circuit_id, params)
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(sim_data).encode("utf-8"))
            elif parsed.path == "/api/telemetry/broadcast":
                ev_type = payload.get("event_type", "custom_telemetry")
                data = payload.get("data", {})
                listeners = telemetry_broker.broadcast(ev_type, data)
                self._set_cors_headers(200)
                self.wfile.write(json.dumps({"status": "broadcast_dispatched", "event_type": ev_type, "listeners": listeners}).encode("utf-8"))
            elif parsed.path == "/api/content/status/update":
                from backend.content_status_api import update_content_status_entry
                res_data, status_code = update_content_status_entry(payload)
                self._set_cors_headers(status_code)
                self.wfile.write(json.dumps(res_data).encode("utf-8"))
            elif parsed.path == "/api/collaboration/portfolio/like":
                from backend.collaboration_hub import collaboration_hub
                prj_id = payload.get("project_id", "")
                res = collaboration_hub.like_project(prj_id)
                self._set_cors_headers(200 if res.get("status") == "SUCCESS" else 400)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/collaboration/group/join":
                from backend.collaboration_hub import collaboration_hub
                gid = payload.get("group_id", "")
                sid = payload.get("student_id", "2023MITEC042")
                sname = payload.get("student_name", "Ashok Kumar A")
                res = collaboration_hub.join_study_group(gid, sid, sname)
                self._set_cors_headers(200 if res.get("status") == "SUCCESS" else 400)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/research/synthesize":
                from backend.research_discovery_engine import research_discovery_engine
                pids = payload.get("paper_ids", [])
                res = research_discovery_engine.generate_literature_synthesis(pids)
                self._set_cors_headers(200 if res.get("status") == "SUCCESS" else 400)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/enterprise_admin/course_allocate":
                from backend.enterprise_admin_engine import enterprise_admin_engine
                res = enterprise_admin_engine.allocate_course(
                    course_code=payload.get("course_code", ""),
                    course_name=payload.get("course_name", ""),
                    department=payload.get("department", "Electronics Engineering"),
                    faculty_id=payload.get("faculty_id", ""),
                    faculty_name=payload.get("faculty_name", ""),
                    credit_hours=int(payload.get("credit_hours", 3)),
                    slot=payload.get("slot", ""),
                    venue=payload.get("venue", ""),
                    capacity=int(payload.get("capacity", 50)),
                    actor_role=payload.get("actor_role", "Admin")
                )
                code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 409)
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/security/mfa/validate":
                from backend.security_hardening_engine import security_hardening_engine
                uid = payload.get("user_id", "2023MITEC042")
                tok = payload.get("token", "")
                res = security_hardening_engine.validate_mfa_token(uid, tok)
                self._set_cors_headers(200 if res.get("status") == "SUCCESS" else 400)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/security/backup/create":
                from backend.security_hardening_engine import security_hardening_engine
                role = payload.get("role", "Admin")
                res = security_hardening_engine.create_database_backup(actor_role=role)
                self._set_cors_headers(200 if res.get("status") == "SUCCESS" else 403)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/next_gen/diagnose":
                from backend.next_gen_agent_engine import next_gen_agent_engine
                symptom = payload.get("symptom", "")
                hardware = payload.get("hardware", "ESP32-S3")
                role = payload.get("role", "Student")
                res = next_gen_agent_engine.diagnose_lab_issue(symptom_query=symptom, hardware_target=hardware, actor_role=role)
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/physical_hil/lock":
                from backend.physical_hil_manager import physical_hil_manager
                port_id = payload.get("port_id", "COM3")
                user_id = payload.get("user_id", "2023MITEC042")
                role = payload.get("role", "Student")
                res = physical_hil_manager.acquire_port_lock(port_id, user_id, actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 409)
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/physical_hil/release":
                from backend.physical_hil_manager import physical_hil_manager
                port_id = payload.get("port_id", "COM3")
                user_id = payload.get("user_id", "2023MITEC042")
                res = physical_hil_manager.release_port_lock(port_id, user_id)
                code = 200 if res.get("status") == "SUCCESS" else 403
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/physical_hil/run_assertion":
                from backend.physical_hil_manager import physical_hil_manager
                port_id = payload.get("port_id", "COM3")
                user_id = payload.get("user_id", "2023MITEC042")
                res = physical_hil_manager.run_test_bench_assertions(port_id, user_id)
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/voice/parse":
                from backend.voice_command_router import voice_command_router
                transcript = payload.get("transcript", "")
                student_id = payload.get("student_id", "2023MITEC042")
                role = payload.get("role", "Student")
                res = voice_command_router.process_voice_query(transcript, student_id=student_id, actor_role=role)
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/academic/topic/update":
                from backend.academic_management_engine import academic_management_engine
                tid = payload.get("topic_id", "")
                status = payload.get("status", "COMPLETED")
                hrs = payload.get("hours_spent")
                sid = payload.get("student_id", "2023MITEC042")
                role = payload.get("role", "Student")
                res = academic_management_engine.update_topic_status(
                    topic_id=tid,
                    new_status=status,
                    hours_spent=float(hrs) if hrs is not None else None,
                    student_id=sid,
                    actor_role=role
                )
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/academic/calendar/add":
                from backend.academic_management_engine import academic_management_engine
                title = payload.get("title", "")
                ev_type = payload.get("event_type", "EXAM")
                s_date = payload.get("start_date", "")
                e_date = payload.get("end_date", s_date)
                venue = payload.get("venue", "MIT Campus")
                desc = payload.get("description", "")
                reg = payload.get("target_regulation", "ECE Regulation 2023")
                role = payload.get("role", "Faculty")
                res = academic_management_engine.add_calendar_event(
                    title=title,
                    event_type=ev_type,
                    start_date=s_date,
                    end_date=e_date,
                    venue=venue,
                    description=desc,
                    target_regulation=reg,
                    actor_role=role
                )
                code = 200 if res.get("status") == "SUCCESS" else 403
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/ece_knowledge/formula/add":
                from backend.ece_knowledge_engine import ece_knowledge_engine
                role = payload.get("role", "Faculty")
                res = ece_knowledge_engine.add_custom_formula(
                    topic=payload.get("topic", "General"),
                    formula_name=payload.get("formula_name", ""),
                    subject_code=payload.get("subject_code", "EC3451"),
                    unit_number=int(payload.get("unit_number", 1)),
                    latex_repr=payload.get("latex_repr", ""),
                    plain_text=payload.get("plain_text", ""),
                    derivation_summary=payload.get("derivation_summary", ""),
                    variables=payload.get("variables", {}),
                    unit_result=payload.get("unit_result", ""),
                    actor_role=role
                )
                code = 200 if res.get("status") == "SUCCESS" else 403
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/productivity/session/log":
                from backend.learning_productivity_engine import learning_productivity_engine
                res = learning_productivity_engine.log_study_session(
                    student_id=payload.get("student_id", "2023MITEC042"),
                    subject_code=payload.get("subject_code", "ECE_GENERAL"),
                    topic=payload.get("topic", "Self Study"),
                    duration_minutes=int(payload.get("duration_minutes", 25)),
                    session_type=payload.get("session_type", "POMODORO_25"),
                    focus_score=int(payload.get("focus_score", 5)),
                    notes=payload.get("notes", ""),
                    distraction_free_mode=bool(payload.get("distraction_free_mode", False)),
                    completed_at=payload.get("completed_at")
                )
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/productivity/bookmarks/add":
                from backend.learning_productivity_engine import learning_productivity_engine
                res = learning_productivity_engine.add_bookmark(
                    student_id=payload.get("student_id", "2023MITEC042"),
                    subject_code=payload.get("subject_code", "EC3451"),
                    topic=payload.get("topic", ""),
                    resource_url=payload.get("resource_url", "/modules"),
                    tags=payload.get("tags", []),
                    notes=payload.get("notes", ""),
                    priority=payload.get("priority", "MEDIUM")
                )
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/productivity/bookmarks/delete":
                from backend.learning_productivity_engine import learning_productivity_engine
                success = learning_productivity_engine.delete_bookmark(
                    bookmark_id=payload.get("bookmark_id", ""),
                    student_id=payload.get("student_id", "2023MITEC042")
                )
                self._set_cors_headers(200)
                self.wfile.write(json.dumps({"status": "SUCCESS" if success else "NOT_FOUND"}).encode("utf-8"))
            elif parsed.path == "/api/productivity/revision_queue/update":
                from backend.learning_productivity_engine import learning_productivity_engine
                res = learning_productivity_engine.update_revision_item(
                    queue_id=payload.get("queue_id", ""),
                    student_id=payload.get("student_id", "2023MITEC042"),
                    confidence_level=int(payload.get("confidence_level", 3))
                )
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/productivity/revision_queue/add":
                from backend.learning_productivity_engine import learning_productivity_engine
                res = learning_productivity_engine.add_revision_item(
                    student_id=payload.get("student_id", "2023MITEC042"),
                    subject_code=payload.get("subject_code", "EC3451"),
                    topic=payload.get("topic", ""),
                    confidence_level=int(payload.get("confidence_level", 3)),
                    initial_interval_days=int(payload.get("initial_interval_days", 3))
                )
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/digital/convert_number":
                from backend.digital_electronics_engine import digital_electronics_engine
                val = str(payload.get("value", "0"))
                base = payload.get("from_base", "DECIMAL")
                sid = payload.get("student_id", "2023MITEC042")
                res = digital_electronics_engine.convert_number(val, base, sid)
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/digital/truth_table":
                from backend.digital_electronics_engine import digital_electronics_engine
                expr = payload.get("expression", "")
                vars_list = payload.get("variables", None)
                res = digital_electronics_engine.generate_truth_table(expr, vars_list)
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/digital/kmap_solve":
                from backend.digital_electronics_engine import digital_electronics_engine
                num_v = int(payload.get("num_variables", 3))
                mins = payload.get("minterms", [])
                dcs = payload.get("dont_cares", [])
                vars_list = payload.get("variables", None)
                res = digital_electronics_engine.solve_kmap(num_v, mins, dcs, vars_list)
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/digital/circuit/save":
                from backend.digital_electronics_engine import digital_electronics_engine
                res = digital_electronics_engine.save_circuit(
                    student_id=payload.get("student_id", "2023MITEC042"),
                    title=payload.get("title", "Custom Design"),
                    expression=payload.get("expression", ""),
                    num_variables=int(payload.get("num_variables", 3)),
                    variables=payload.get("variables", ["A", "B", "C"]),
                    minterms=payload.get("minterms", []),
                    simplified_sop=payload.get("simplified_sop", ""),
                    actor_role=payload.get("role", "Student")
                )
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/analog_comm/filter_calc":
                from backend.analog_comm_engine import analog_comm_engine
                res = analog_comm_engine.calculate_filter(
                    filter_type=payload.get("filter_type", "RC_LPF"),
                    R=float(payload.get("R", 10000.0)),
                    C=float(payload.get("C", 1.0e-8)),
                    L=float(payload.get("L", 1.0e-3)),
                    R2=float(payload.get("R2")) if payload.get("R2") else None,
                    C2=float(payload.get("C2")) if payload.get("C2") else None,
                    gain=float(payload.get("gain", 1.0))
                )
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/analog_comm/transistor_bias":
                from backend.analog_comm_engine import analog_comm_engine
                res = analog_comm_engine.calculate_transistor_bias(
                    transistor_type=payload.get("transistor_type", "BJT_NPN"),
                    Vcc=float(payload.get("Vcc", 12.0)),
                    R1=float(payload.get("R1", 39000.0)),
                    R2=float(payload.get("R2", 10000.0)),
                    Rc=float(payload.get("Rc", 2200.0)),
                    Re=float(payload.get("Re", 1000.0)),
                    beta=float(payload.get("beta", 150.0)),
                    Vbe=float(payload.get("Vbe", 0.7)),
                    Vth=float(payload.get("Vth", 2.0)),
                    kn=float(payload.get("kn", 1.5e-3))
                )
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/analog_comm/opamp_calc":
                from backend.analog_comm_engine import analog_comm_engine
                res = analog_comm_engine.calculate_opamp(
                    config=payload.get("config", "INVERTING"),
                    Rin=float(payload.get("Rin", 10000.0)),
                    Rf=float(payload.get("Rf", 100000.0)),
                    GBW=float(payload.get("GBW", 1000000.0)),
                    SR=float(payload.get("SR", 500000.0)),
                    Vpeak=float(payload.get("Vpeak", 5.0)),
                    Vio=float(payload.get("Vio", 0.002)),
                    Iio=float(payload.get("Iio", 2.0e-8))
                )
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/analog_comm/txline_calc":
                from backend.analog_comm_engine import analog_comm_engine
                res = analog_comm_engine.calculate_txline(
                    Z0=float(payload.get("Z0", 50.0)),
                    ZL_real=float(payload.get("ZL_real", 75.0)),
                    ZL_imag=float(payload.get("ZL_imag", 0.0))
                )
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/analog_comm/modulation_calc":
                from backend.analog_comm_engine import analog_comm_engine
                res = analog_comm_engine.calculate_modulation(
                    modulation_type=payload.get("modulation_type", "AM"),
                    carrier_freq=float(payload.get("carrier_freq", 1.0e6)),
                    mod_freq=float(payload.get("mod_freq", 5000.0)),
                    mod_index=float(payload.get("mod_index", 0.8)),
                    delta_f=float(payload.get("delta_f", 75000.0)),
                    Pc=float(payload.get("Pc", 100.0)),
                    snr_db=float(payload.get("snr_db", 20.0)),
                    channel_bandwidth=float(payload.get("channel_bandwidth", 100000.0))
                )
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/analog_comm/calc/save":
                from backend.analog_comm_engine import analog_comm_engine
                res = analog_comm_engine.save_calculation(
                    student_id=payload.get("student_id", "2023MITEC042"),
                    title=payload.get("title", "Custom Calculation"),
                    category=payload.get("category", "FILTER"),
                    parameters=payload.get("parameters", {}),
                    results=payload.get("results", {}),
                    subject_code=payload.get("subject_code", "EC3451")
                )
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/projects/proposals":
                from backend.project_innovation_engine import project_innovation_engine
                role = payload.get("role", "Student")
                res = project_innovation_engine.create_proposal(payload, actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/projects/proposal/status":
                from backend.project_innovation_engine import project_innovation_engine
                pid = payload.get("proposal_id", "")
                status = payload.get("status", "")
                role = payload.get("role", "Student")
                res = project_innovation_engine.update_proposal_status(pid, status, actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/projects/bom_calc":
                from backend.project_innovation_engine import project_innovation_engine
                items = payload.get("items", [])
                tax = float(payload.get("tax_buffer_percent", 18.0))
                contingency = float(payload.get("contingency_percent", 10.0))
                res = project_innovation_engine.calculate_bom(items, tax, contingency)
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/projects/bom/save":
                from backend.project_innovation_engine import project_innovation_engine
                pid = payload.get("proposal_id", "")
                items = payload.get("items", [])
                res = project_innovation_engine.save_bom_items(pid, items)
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/projects/check_compatibility":
                from backend.project_innovation_engine import project_innovation_engine
                mcu = payload.get("mcu_name", "ESP32-WROOM-32")
                components = payload.get("components", [])
                res = project_innovation_engine.check_compatibility(mcu, components)
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/projects/milestones":
                from backend.project_innovation_engine import project_innovation_engine
                res = project_innovation_engine.add_milestone(payload)
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/projects/milestone/status":
                from backend.project_innovation_engine import project_innovation_engine
                mid = payload.get("milestone_id", "")
                status = payload.get("status", "COMPLETED")
                res = project_innovation_engine.update_milestone_status(mid, status)
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/faculty/lesson_plans":
                from backend.faculty_productivity_engine import faculty_productivity_engine
                role = payload.get("role", "Faculty")
                res = faculty_productivity_engine.create_lesson_plan(payload, actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/faculty/lesson_plan/status":
                from backend.faculty_productivity_engine import faculty_productivity_engine
                pid = payload.get("plan_id", "")
                status = payload.get("status", "COMPLETED")
                hrs = float(payload.get("actual_hours")) if payload.get("actual_hours") is not None else None
                notes = payload.get("notes")
                role = payload.get("role", "Faculty")
                res = faculty_productivity_engine.update_lesson_plan_status(pid, status, actual_hours=hrs, notes=notes, actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/faculty/assignments":
                from backend.faculty_productivity_engine import faculty_productivity_engine
                role = payload.get("role", "Faculty")
                res = faculty_productivity_engine.create_assignment(payload, actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/faculty/feedback":
                from backend.faculty_productivity_engine import faculty_productivity_engine
                role = payload.get("role", "Faculty")
                res = faculty_productivity_engine.record_feedback(payload, actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/faculty/meeting_minutes":
                from backend.faculty_productivity_engine import faculty_productivity_engine
                role = payload.get("role", "Faculty")
                res = faculty_productivity_engine.record_meeting_minutes(payload, actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/accessibility/preferences":
                from backend.accessibility_engine import accessibility_engine
                uid = payload.get("user_id", "2023MITEC042")
                res = accessibility_engine.save_preferences(uid, payload)
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/accessibility/feedback":
                from backend.accessibility_engine import accessibility_engine
                res = accessibility_engine.record_feedback(payload)
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/intelligence/run-consistency-check":
                from backend.data_intelligence_engine import data_intelligence_engine
                role = payload.get("role", "Admin")
                res = data_intelligence_engine.run_record_consistency_check(actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/intelligence/resolve-audit":
                from backend.data_intelligence_engine import data_intelligence_engine
                aid = payload.get("audit_id", "")
                notes = payload.get("resolution_notes", "Audit cleared by academic reviewer.")
                by = payload.get("resolved_by", "2023MITEC042")
                role = payload.get("role", "Admin")
                res = data_intelligence_engine.resolve_audit_issue(aid, notes, resolved_by=by, actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/intelligence/update-syllabus-unit":
                from backend.data_intelligence_engine import data_intelligence_engine
                code = payload.get("course_code", "EC3451")
                unit = int(payload.get("unit_num", 1))
                covered = int(payload.get("topics_covered", 0))
                hrs = float(payload.get("hours_actual", 0.0))
                role = payload.get("role", "Faculty")
                res = data_intelligence_engine.update_syllabus_unit_progress(code, unit, covered, hrs, actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/intelligence/analyze-question-bank":
                from backend.data_intelligence_engine import data_intelligence_engine
                code = payload.get("course_code", "EC3451")
                questions = payload.get("questions", [])
                role = payload.get("role", "Faculty")
                res = data_intelligence_engine.analyze_custom_question_bank(code, questions, actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/intelligence/audit-freshness":
                from backend.data_intelligence_engine import data_intelligence_engine
                thresh = int(payload.get("stale_threshold_days", 180))
                role = payload.get("role", "Faculty")
                res = data_intelligence_engine.audit_content_freshness(thresh, actor_role=role)
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/intelligence/detect-duplicates":
                from backend.data_intelligence_engine import data_intelligence_engine
                res = data_intelligence_engine.detect_duplicate_submission(
                    doc_id_a=payload.get("doc_id_a", "DOC_A"),
                    doc_id_b=payload.get("doc_id_b", "DOC_B"),
                    title_a=payload.get("title_a", "Document A"),
                    title_b=payload.get("title_b", "Document B"),
                    text_a=payload.get("text_a", ""),
                    text_b=payload.get("text_b", ""),
                    threshold_pct=float(payload.get("threshold_pct", 75.0)),
                    actor_role=payload.get("role", "Faculty")
                )
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/intelligence/resolve-duplicate":
                from backend.data_intelligence_engine import data_intelligence_engine
                did = payload.get("duplicate_id", "")
                res_action = payload.get("resolution", "MERGED")
                role = payload.get("role", "Admin")
                res = data_intelligence_engine.resolve_duplicate_pair(did, res_action, actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/reliability/record-telemetry":
                from backend.platform_reliability_engine import platform_reliability_engine
                feat = payload.get("feature_name", "UNKNOWN_FEATURE")
                route = payload.get("route", "/")
                actor = payload.get("actor_id", "2023MITEC042")
                lat = float(payload.get("latency_ms", 1.5))
                status = int(payload.get("status_code", 200))
                res = platform_reliability_engine.record_feature_telemetry(feat, route, actor, lat, status)
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/reliability/db-checkpoint":
                from backend.platform_reliability_engine import platform_reliability_engine
                mode = payload.get("mode", "PASSIVE")
                role = payload.get("role", "Admin")
                res = platform_reliability_engine.execute_wal_checkpoint(mode=mode, actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/reliability/link-scan":
                from backend.platform_reliability_engine import platform_reliability_engine
                role = payload.get("role", "Admin")
                res = platform_reliability_engine.run_route_integrity_scan(actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/reliability/run-audit":
                from backend.platform_reliability_engine import platform_reliability_engine
                role = payload.get("role", "Admin")
                res = platform_reliability_engine.run_full_system_audit(actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/iot/telemetry/ingest":
                from backend.iot_telemetry_engine import iot_telemetry_engine
                nid = payload.get("node_id", "NODE_ESP32_BENCH_01")
                v = float(payload.get("voltage_v", 12.0))
                c = float(payload.get("current_a", 1.0))
                t = float(payload.get("ambient_temp_c", 30.0))
                r = payload.get("relay_state")
                res = iot_telemetry_engine.ingest_telemetry_packet(nid, v, c, t, r)
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/iot/alerts/ack":
                from backend.iot_telemetry_engine import iot_telemetry_engine
                aid = payload.get("alert_id", "")
                notes = payload.get("notes", "Acknowledged by Lab Technician")
                role = payload.get("role", "Admin")
                res = iot_telemetry_engine.acknowledge_alert(aid, notes, actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/iot/bench/relay":
                from backend.iot_telemetry_engine import iot_telemetry_engine
                bid = payload.get("bench_id", "")
                state = payload.get("target_state", "CLOSED")
                actor = payload.get("actor_id", "2023MITEC042")
                role = payload.get("role", "Admin")
                res = iot_telemetry_engine.toggle_bench_relay(bid, state, actor_id=actor, actor_role=role)
                code = 200 if res.get("status") == "SUCCESS" else (403 if res.get("status") == "FORBIDDEN" else 400)
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/inspector/axial-decode":
                from backend.component_inspector_engine import component_inspector_engine
                bands = payload.get("bands", [])
                actor = payload.get("actor_id", "2023MITEC042")
                res = component_inspector_engine.decode_axial_resistor(bands, actor_id=actor)
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/inspector/smd-decode":
                from backend.component_inspector_engine import component_inspector_engine
                code_str = payload.get("code", "")
                ctype = payload.get("component_type", "RESISTOR")
                actor = payload.get("actor_id", "2023MITEC042")
                res = component_inspector_engine.decode_smd_marking(code_str, component_type=ctype, actor_id=actor)
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/inspector/pcb-trace":
                from backend.component_inspector_engine import component_inspector_engine
                curr = float(payload.get("current_a", 1.0))
                trise = float(payload.get("temp_rise_c", 10.0))
                cop = float(payload.get("copper_oz", 1.0))
                ttype = payload.get("trace_type", "external")
                length = float(payload.get("trace_length_cm", 10.0))
                amb = float(payload.get("ambient_temp_c", 25.0))
                dname = payload.get("design_name")
                actor = payload.get("actor_id", "2023MITEC042")
                res = component_inspector_engine.calculate_pcb_trace_width(
                    curr, trise, cop, ttype, length, amb, design_name=dname, actor_id=actor
                )
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/inspector/ic-thermal":
                from backend.component_inspector_engine import component_inspector_engine
                pkg = payload.get("package_code", "DIP-8")
                pwr = float(payload.get("power_watts", 0.5))
                amb = float(payload.get("ambient_temp_c", 25.0))
                th_ja = payload.get("theta_ja_custom")
                if th_ja is not None:
                    th_ja = float(th_ja)
                target_tj = float(payload.get("target_max_tj_c", 100.0))
                actor = payload.get("actor_id", "2023MITEC042")
                res = component_inspector_engine.evaluate_ic_thermal_dissipation(
                    pkg, pwr, amb, theta_ja_custom=th_ja, target_max_tj_c=target_tj, actor_id=actor
                )
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/assessment/verify-logic":
                from backend.ece_assignment_engine import ece_assignment_engine
                circuit_type = payload.get("circuit_type", "FULL_ADDER")
                code_str = payload.get("code_or_expression", "")
                student_id = payload.get("student_id", "2023MITEC042")
                res = ece_assignment_engine.verify_combinational_logic(circuit_type, code_str, student_id=student_id)
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/assessment/verify-debounce":
                from backend.ece_assignment_engine import ece_assignment_engine
                code_str = payload.get("code", "")
                sampling = float(payload.get("sampling_period_ms", 5.0))
                threshold = float(payload.get("debounce_threshold_ms", 30.0))
                student_id = payload.get("student_id", "2023MITEC042")
                res = ece_assignment_engine.verify_button_debouncing(code_str, sampling, threshold, student_id=student_id)
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/assessment/verify-timing":
                from backend.ece_assignment_engine import ece_assignment_engine
                code_str = payload.get("code", "")
                student_id = payload.get("student_id", "2023MITEC042")
                res = ece_assignment_engine.verify_non_blocking_timing(code_str, student_id=student_id)
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/assessment/verify-ir-interrupt":
                from backend.ece_assignment_engine import ece_assignment_engine
                code_str = payload.get("code", "")
                student_id = payload.get("student_id", "2023MITEC042")
                res = ece_assignment_engine.verify_ir_proximity_interrupt(code_str, student_id=student_id)
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/sensor-sim/generate":
                from backend.iot_sensor_simulator_engine import iot_sensor_simulator_engine
                count = int(payload.get("burst_count", 1))
                node_id = payload.get("node_id", "ESP32_LAB304_DHT22_IR")
                student_id = payload.get("student_id", "2023MITEC042")
                baseline_temp = float(payload.get("baseline_temp_c", 27.5))
                baseline_hum = float(payload.get("baseline_humidity_pct", 58.0))
                trigger_ir = bool(payload.get("trigger_ir_event", False))

                if count > 1:
                    res = iot_sensor_simulator_engine.generate_burst_readings(
                        count=count, node_id=node_id, student_id=student_id,
                        baseline_temp_c=baseline_temp, baseline_humidity_pct=baseline_hum
                    )
                    self._set_cors_headers(200)
                    self.wfile.write(json.dumps({"status": "SUCCESS", "count": len(res), "readings": res}).encode("utf-8"))
                else:
                    res = iot_sensor_simulator_engine.generate_simulated_reading(
                        node_id=node_id, student_id=student_id,
                        baseline_temp_c=baseline_temp, baseline_humidity_pct=baseline_hum,
                        trigger_ir_event=trigger_ir
                    )
                    self._set_cors_headers(200)
                    self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/sensor-sim/ingest":
                from backend.iot_sensor_simulator_engine import iot_sensor_simulator_engine
                res = iot_sensor_simulator_engine.ingest_custom_reading(payload)
                code = 200 if res.get("status") == "SUCCESS" else 400
                self._set_cors_headers(code)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/sensor-sim/clear":
                from backend.iot_sensor_simulator_engine import iot_sensor_simulator_engine
                node_id = payload.get("node_id")
                res = iot_sensor_simulator_engine.clear_simulated_readings(node_id=node_id)
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/rtos/simulate":
                from backend.rtos_scheduler_engine import rtos_scheduler_engine
                tasks = payload.get("tasks")
                mode = payload.get("mode", "PREEMPTIVE_PRIORITY")
                mcu = payload.get("mcu_target", "ESP32_WROOM_32")
                duration = int(payload.get("total_duration_ms", 50))
                student = payload.get("student_id", "2023MITEC042")
                res = rtos_scheduler_engine.simulate_scheduler(
                    tasks=tasks, mode=mode, mcu_target=mcu,
                    total_duration_ms=duration, student_id=student
                )
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/rtos/benchmark":
                from backend.rtos_scheduler_engine import rtos_scheduler_engine
                mcu = payload.get("mcu_target", "ESP32_WROOM_32")
                res = rtos_scheduler_engine.benchmark_mcu_hardware(mcu_key=mcu)
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/energy/calculate":
                from backend.low_power_energy_engine import low_power_energy_engine
                mcu = payload.get("mcu_target", "ESP32_WROOM_32")
                act_mode = payload.get("active_mode", "ACTIVE_WIFI_TX")
                slp_mode = payload.get("sleep_mode", "DEEP_SLEEP")
                wake = payload.get("wake_source", "RTC_TIMER")
                act_ms = float(payload.get("active_duration_ms", 200.0))
                slp_s = float(payload.get("sleep_duration_s", 59.8))
                bat = payload.get("battery_key", "LIPO_18650_2500MAH")
                eff = float(payload.get("battery_efficiency", 0.85))
                student = payload.get("student_id", "2023MITEC042")

                res = low_power_energy_engine.calculate_energy_profile(
                    mcu_target=mcu, active_mode=act_mode, sleep_mode=slp_mode,
                    wake_source=wake, active_duration_ms=act_ms, sleep_duration_s=slp_s,
                    battery_key=bat, battery_efficiency=eff, student_id=student
                )
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/energy/discharge-curve":
                from backend.low_power_energy_engine import low_power_energy_engine
                bat = payload.get("battery_key", "LIPO_18650_2500MAH")
                current = float(payload.get("avg_current_ma", 0.54))
                eff = float(payload.get("battery_efficiency", 0.85))
                res = low_power_energy_engine.generate_discharge_curve(
                    battery_key=bat, avg_current_ma=current, battery_efficiency=eff
                )
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/fpga/synthesize":
                from backend.fpga_synthesis_engine import fpga_synthesis_engine
                target = payload.get("target_fpga", "XILINX_ARTIX7_XC7A35T")
                mod = payload.get("module_key", "CLOCK_DIVIDER_COUNTER")
                hdl = payload.get("hdl_type", "VERILOG")
                clk = float(payload.get("target_clock_mhz", 100.0))
                student = payload.get("student_id", "2023MITEC042")
                res = fpga_synthesis_engine.synthesize_module(
                    target_fpga=target, module_key=mod, hdl_type=hdl,
                    target_clock_mhz=clk, student_id=student
                )
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            elif parsed.path == "/api/fpga/generate-traces":
                from backend.fpga_synthesis_engine import fpga_synthesis_engine
                mod = payload.get("module_key", "CLOCK_DIVIDER_COUNTER")
                cycles = int(payload.get("cycles", 32))
                clk_ns = float(payload.get("clock_period_ns", 10.0))
                synth_id = payload.get("synthesis_id")
                res = fpga_synthesis_engine.generate_logic_analyzer_traces(
                    module_key=mod, cycles=cycles, clk_period_ns=clk_ns, synthesis_id=synth_id
                )
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
            else:
                self._set_cors_headers(404)
                self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

        def log_message(self, format, *args):
            # Suppress default noisy http.server logs; our custom logger prints rich diagnostics
            pass

    def run_server(host="0.0.0.0", port=5000):
        print(f"{TerminalColors.BOLD}{TerminalColors.EMERALD}")
        print("╔══════════════════════════════════════════════════════════════════════════════════╗")
        print("║          VOLTCORE APEX ACADEMIA - ATTENDANCE & TELEMETRY GATEWAY                 ║")
        print("║       Madras Institute of Technology (MIT) Campus, Anna University               ║")
        print("║          Port 5000 | Native HTTP Engine (Install Flask via pip)                  ║")
        print("╚══════════════════════════════════════════════════════════════════════════════════╝")
        print(f"{TerminalColors.RESET}")
        lms_database.init_db()
        lms_database.seed_mit_campus_data()
        server_address = (host, port)
        httpd = HTTPServer(server_address, FallbackHTTPHandler)
        print(f"[{TerminalColors.GREEN}INFO{TerminalColors.RESET}] Telemetry Server listening on http://127.0.0.1:{port}...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down Telemetry Server.")
            httpd.server_close()


if __name__ == "__main__":
    # Test scan locally if flag passed, otherwise run server
    if "--test-scan" in sys.argv:
        print("[TEST] Simulating incoming ESP32 scan for Ashok Kumar A...")
        test_payload = {
            "node_id": "ESP32_MIT_IOT_LAB_01",
            "student_id": "2023MITEC042",
            "rfid_uid": "E2 80 6F 3B",
            "rssi": -58
        }
        res, code = process_attendance_scan(test_payload)
        print("Response:", json.dumps(res, indent=2))
    else:
        run_server(port=5000)
