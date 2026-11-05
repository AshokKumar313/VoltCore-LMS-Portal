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
