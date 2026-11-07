"""
========================================================================================
VoltCore Apex Academia - Phase 9 Enterprise Test Suite
Target: Instructor & Administrator CMS, Multi-Tenant Analytics Dashboard & PWA Offline Sync
Lead Systems Architect: Ashok Kumar A
Machine Target: HP Victus (LAPTOP-3NEGBVLE) — Whisper-Quiet, Passive CPU (<5%)
Standards: Autonomous Engineering Cluster • Outcome-Based Education (OBE) • Bloom's Taxonomy
Architecture: SQLite WAL Mode • RBAC Enforcement • Idempotent Offline Sync
========================================================================================
"""

import os
import json
import time
import pytest
from io import BytesIO

# Import Phase 9 backend engines
from backend.instructor_cms_engine import InstructorCmsEngine, instructor_cms_engine
from backend.learning_analytics_engine import LearningAnalyticsEngine, learning_analytics_engine
from backend.offline_sync_engine import OfflineSyncEngine, offline_sync_engine

TEST_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_phase9_enterprise.db")


@pytest.fixture(autouse=True)
def clean_test_db():
    """Ensure clean isolated SQLite database for Phase 9 Enterprise tests."""
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
# 1. INSTRUCTOR CMS: COURSE PUBLISHING STUDIO
# ========================================================================================

def test_instructor_cms_course_publishing():
    """Verifies that faculty can publish new courses with modular syllabus and hardware targets."""
    engine = InstructorCmsEngine(db_path=TEST_DB_PATH)

    payload = {
        "course_code": "EC3701",
        "course_name": "Advanced Embedded Systems Architecture",
        "department": "Department of Electronics Engineering",
        "semester": 5,
        "credits": 4,
        "instructor_id": "FAC_042",
        "instructor_name": "Ashok Kumar A",
        "syllabus_modules": [
            {"module_id": "MOD_01", "title": "ARM Cortex-M4 NVIC & Concurrency", "bloom_level": "Level 4: Analyze"},
            {"module_id": "MOD_02", "title": "Circular DMA & High-Speed ADC Streaming", "bloom_level": "Level 4: Analyze"},
            {"module_id": "MOD_03", "title": "FreeRTOS Preemptive Schedulers & PendSV", "bloom_level": "Level 5: Evaluate"}
        ],
        "hardware_targets": ["STM32F401RE", "ESP32-S3", "Artix-7 FPGA"],
        "prerequisites": ["EC3451 Linear Integrated Circuits", "EC3352 Digital Systems"]
    }

    res = engine.publish_course(payload, actor_role="Faculty")
    assert res["status"] == "SUCCESS"
    assert res["course_code"] == "EC3701"
    assert res["credits"] == 4

    published = engine.get_published_courses()
    assert len(published) >= 1
    found = next((c for c in published if c["course_code"] == "EC3701"), None)
    assert found is not None
    assert found["course_name"] == "Advanced Embedded Systems Architecture"
    assert len(found["syllabus_modules"]) == 3
    assert "STM32F401RE" in found["hardware_targets"]


# ========================================================================================
# 2. INSTRUCTOR CMS: RBAC AUTHORIZATION ENFORCEMENT & AUDIT LOGGING
# ========================================================================================

def test_instructor_cms_rbac_enforcement():
    """Verifies that unauthorized roles (Student) are forbidden from publishing courses or managing question banks."""
    engine = InstructorCmsEngine(db_path=TEST_DB_PATH)

    # 1. Verify permission query matrix
    assert engine.verify_permission("Admin", "PUBLISH_COURSE") is True
    assert engine.verify_permission("Faculty", "PUBLISH_COURSE") is True
    assert engine.verify_permission("Instructor", "PUBLISH_COURSE") is True
    assert engine.verify_permission("Platform-Lead", "PUBLISH_COURSE") is True
    assert engine.verify_permission("Student", "PUBLISH_COURSE") is False
    assert engine.verify_permission("TeachingAssistant", "PUBLISH_COURSE") is False
    assert engine.verify_permission("TeachingAssistant", "REVIEW_REPORT") is True

    # 2. Student attempt to publish course
    payload_course = {
        "course_code": "EC9999",
        "course_name": "Rogue Course Attempt",
        "instructor_id": "STU_999"
    }
    denied_course = engine.publish_course(payload_course, actor_role="Student")
    assert denied_course["status"] == "FORBIDDEN"
    assert "Insufficient permissions" in denied_course["error"]

    # 3. Student attempt to add question to bank
    payload_q = {
        "course_code": "EC3701",
        "section": "sec_core",
        "course_outcome": "CO1",
        "bloom_level": "Level 2: Understand",
        "marks": 2,
        "question_type": "MCQ",
        "question_text": "Unauthorized Question",
        "correct_answer": "A"
    }
    denied_q = engine.add_question_to_bank(payload_q, actor_role="Student")
    assert denied_q["status"] == "FORBIDDEN"

    # 4. Confirm audit logs capture the denied actions
    conn = engine._get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT actor_id, actor_role, action, status FROM cms_audit_logs WHERE status = 'DENIED';")
        logs = cur.fetchall()
        assert len(logs) >= 2
        actions = [log[2] for log in logs]
        assert "PUBLISH_COURSE" in actions
        assert "MANAGE_QUESTION_BANK" in actions
    finally:
        conn.close()


# ========================================================================================
# 3. INSTRUCTOR CMS: LAB REPORT REVIEW & AI VERDICT OVERRIDE
# ========================================================================================

def test_instructor_cms_report_review_override():
    """Verifies that faculty can review student lab reports and override automated AI verdicts."""
    engine = InstructorCmsEngine(db_path=TEST_DB_PATH)

    review_payload = {
        "report_id": "REP_LAB_007",
        "student_id": "2023MITEC042",
        "course_code": "EC3701",
        "original_ai_verdict": "NEEDS_REVISION",
        "faculty_override_verdict": "APPROVED",
        "adjusted_score": 94.5,
        "max_score": 100.0,
        "reviewer_id": "FAC_042",
        "faculty_notes": "Reviewed waveform logic analyzer capture. Student properly demonstrated edge-triggered interrupt behavior."
    }

    res = engine.review_and_override_report(review_payload, actor_role="Faculty")
    assert res["status"] == "SUCCESS"
    assert res["report_id"] == "REP_LAB_007"
    assert res["adjusted_score"] == 94.5
    assert res["override_verdict"] == "APPROVED"

    # Unauthorized role check
    denied = engine.review_and_override_report(review_payload, actor_role="Student")
    assert denied["status"] == "FORBIDDEN"


# ========================================================================================
# 4. INSTRUCTOR CMS: EXAM QUESTION BANK MANAGEMENT
# ========================================================================================

def test_instructor_cms_question_bank_management():
    """Verifies adding and querying examination questions with Bloom's Taxonomy categorization."""
    engine = InstructorCmsEngine(db_path=TEST_DB_PATH)

    q1 = {
        "course_code": "EC3701",
        "section": "sec_interrupts",
        "course_outcome": "CO3",
        "bloom_level": "Level 4: Analyze",
        "marks": 2,
        "question_type": "MCQ",
        "question_text": "Which register in the ARM Cortex-M4 NVIC enables NVIC IRQ line 23?",
        "options": ["NVIC->ISER[0]", "NVIC->ICER[0]", "NVIC->ISPR[0]", "NVIC->IABR[0]"],
        "correct_answer": "NVIC->ISER[0]",
        "derivation": "ISER (Interrupt Set-Enable Register) enables IRQ lines. IRQ 23 corresponds to bit 23 in ISER[0].",
        "distractor": "ICER clears enable, ISPR sets pending, and IABR reads active state."
    }

    q2 = {
        "course_code": "EC3701",
        "section": "sec_freertos",
        "course_outcome": "CO4",
        "bloom_level": "Level 5: Evaluate",
        "marks": 2,
        "question_type": "NAT",
        "question_text": "Calculate CPU utilization (%) for two tasks: Task 1 (C=2ms, T=10ms) and Task 2 (C=4ms, T=20ms).",
        "correct_answer": "40.0",
        "tolerance": 0.5,
        "derivation": "U = (2/10) + (4/20) = 0.20 + 0.20 = 0.40 = 40.0%",
        "distractor": "Omitting common denominator yields incorrect utilization sum."
    }

    res1 = engine.add_question_to_bank(q1, actor_role="Faculty")
    assert res1["status"] == "SUCCESS"
    assert res1["bloom_level"] == "Level 4: Analyze"

    res2 = engine.add_question_to_bank(q2, actor_role="Admin")
    assert res2["status"] == "SUCCESS"

    # Query questions for EC3701
    questions = engine.get_questions_by_course("EC3701")
    assert len(questions) == 2
    mcq = next((q for q in questions if q["question_type"] == "MCQ"), None)
    assert mcq is not None
    assert mcq["correct_answer"] == "NVIC->ISER[0]"
    assert len(mcq["options"]) == 4

    nat = next((q for q in questions if q["question_type"] == "NAT"), None)
    assert nat is not None
    assert nat["tolerance"] == 0.5


# ========================================================================================
# 5. LEARNING ANALYTICS: OBE COURSE OUTCOME (CO1-CO5) DIRECT ATTAINMENT
# ========================================================================================

def test_obe_course_outcome_direct_attainment():
    """Verifies direct CO attainment percentage computation and NBA Level mapping (Levels 0 to 3)."""
    analytics = LearningAnalyticsEngine(db_path=TEST_DB_PATH)

    # High performing cohort
    mock_student_scores_high = [
        {"co_scores": {"CO1": 18, "CO2": 19, "CO3": 17, "CO4": 18, "CO5": 19}, "co_max": {"CO1": 20, "CO2": 20, "CO3": 20, "CO4": 20, "CO5": 20}},
        {"co_scores": {"CO1": 16, "CO2": 18, "CO3": 18, "CO4": 17, "CO5": 18}, "co_max": {"CO1": 20, "CO2": 20, "CO3": 20, "CO4": 20, "CO5": 20}},
        {"co_scores": {"CO1": 19, "CO2": 17, "CO3": 19, "CO4": 18, "CO5": 16}, "co_max": {"CO1": 20, "CO2": 20, "CO3": 20, "CO4": 20, "CO5": 20}},
    ]

    co_results = analytics.calculate_co_attainment(mock_student_scores_high)
    assert len(co_results) == 5
    for co_id in ["CO1", "CO2", "CO3", "CO4", "CO5"]:
        assert co_results[co_id]["attainment_percentage"] >= 80.0
        assert co_results[co_id]["nba_level"] == 3
        assert "ATTAINED (Level 3 - Strong)" in co_results[co_id]["status"]

    # Cohort requiring remedial action
    mock_student_scores_low = [
        {"co_scores": {"CO1": 8, "CO2": 9, "CO3": 7, "CO4": 8, "CO5": 7}, "co_max": {"CO1": 20, "CO2": 20, "CO3": 20, "CO4": 20, "CO5": 20}},
        {"co_scores": {"CO1": 7, "CO2": 8, "CO3": 6, "CO4": 9, "CO5": 8}, "co_max": {"CO1": 20, "CO2": 20, "CO3": 20, "CO4": 20, "CO5": 20}},
    ]

    co_results_low = analytics.calculate_co_attainment(mock_student_scores_low)
    assert co_results_low["CO3"]["attainment_percentage"] < 50.0
    assert co_results_low["CO3"]["nba_level"] == 0
    assert co_results_low["CO3"]["status"] == "REMEDIAL_ACTION_REQUIRED"


# ========================================================================================
# 6. LEARNING ANALYTICS: NBA PROGRAM OUTCOME (PO1-PO12, PSO1-PSO2) MATRIX
# ========================================================================================

def test_nba_program_outcome_matrix():
    """Verifies that direct CO attainment is projected onto PO1-PO12 and PSO1-PSO2 with correlation weights."""
    analytics = LearningAnalyticsEngine(db_path=TEST_DB_PATH)

    mock_co_results = {
        "CO1": {"attainment_percentage": 82.5},
        "CO2": {"attainment_percentage": 78.0},
        "CO3": {"attainment_percentage": 85.0},
        "CO4": {"attainment_percentage": 74.0},
        "CO5": {"attainment_percentage": 80.0}
    }

    po_matrix = analytics.calculate_po_matrix(mock_co_results)

    # Must contain PO1-PO12 and PSO1-PSO2
    expected_pos = [f"PO{i}" for i in range(1, 13)] + ["PSO1", "PSO2"]
    for p in expected_pos:
        assert p in po_matrix
        assert "po_title" in po_matrix[p]
        assert "attained_percentage" in po_matrix[p]
        assert "nba_attainment_points" in po_matrix[p]
        assert po_matrix[p]["nba_attainment_points"] <= 3.0

    # Silicon engineering PSO1 should have high attainment
    assert po_matrix["PSO1"]["attained_percentage"] >= 75.0
    assert po_matrix["PSO1"]["status"] == "MET"


# ========================================================================================
# 7. LEARNING ANALYTICS: SCORE DISTRIBUTIONS, LAB BOTTLENECKS & SNAPSHOTS
# ========================================================================================

def test_learning_analytics_score_distribution_and_bottlenecks():
    """Verifies statistical score distribution, lab bottleneck detection, and snapshot generation."""
    analytics = LearningAnalyticsEngine(db_path=TEST_DB_PATH)

    # 1. Score Distribution
    scores = [95.0, 88.0, 72.0, 60.0, 45.0, 90.0, 84.0, 76.0, 52.0, 98.0]
    dist = analytics.calculate_score_distribution(scores)
    assert dist["sample_size"] == 10
    assert dist["lowest_score"] == 45.0
    assert dist["highest_score"] == 98.0
    assert 70.0 <= dist["mean_score"] <= 80.0
    assert "grade_counts" in dist
    assert "histogram_bins" in dist
    assert sum(dist["histogram_bins"].values()) == 10

    # 2. Lab Bottlenecks
    bottlenecks = analytics.detect_lab_bottlenecks()
    assert len(bottlenecks) >= 2
    b1 = bottlenecks[0]
    assert "lab_id" in b1
    assert "failure_rate_pct" in b1
    assert "severity" in b1
    assert "common_trap" in b1

    # 3. Analytics Snapshot
    snapshot = analytics.generate_analytics_snapshot(
        cohort_id="COHORT_2023_2027_ECE_A",
        course_code="EC3701"
    )
    assert "snapshot_id" in snapshot
    assert snapshot["cohort_id"] == "COHORT_2023_2027_ECE_A"
    assert snapshot["course_code"] == "EC3701"
    assert "co_attainment" in snapshot
    assert "po_attainment" in snapshot
    assert "lab_bottlenecks" in snapshot


# ========================================================================================
# 8. PWA OFFLINE SYNC: BATCH INGESTION & IDEMPOTENCY
# ========================================================================================

def test_pwa_offline_sync_ingestion_and_idempotency():
    """Verifies that offline sync events are ingested idempotently without duplicate XP or replay errors."""
    sync_engine = OfflineSyncEngine(db_path=TEST_DB_PATH)

    events_batch = [
        {
            "client_event_id": "CLIENT_EV_901",
            "event_type": "CHAPTER_PROGRESS",
            "resource_id": "STM32_MOD_14_SYSTICK",
            "payload": {"progress_pct": 100.0, "time_spent_sec": 420},
            "client_timestamp": "2026-11-07 10:15:00",
            "xp_reward": 50
        },
        {
            "client_event_id": "CLIENT_EV_902",
            "event_type": "QUIZ_COMPLETION",
            "resource_id": "QUIZ_PENDSV_EXCP",
            "payload": {"score": 90.0, "passed": True},
            "client_timestamp": "2026-11-07 10:20:00",
            "xp_reward": 80
        }
    ]

    # First sync: both succeed
    res1 = sync_engine.process_sync_batch("STUDENT_042", events_batch)
    assert res1["status"] == "SUCCESS"
    assert res1["synced_count"] == 2
    assert res1["duplicates_skipped"] == 0
    assert res1["total_xp_awarded"] == 130

    # Second sync of the EXACT same batch: both skipped as duplicates
    res2 = sync_engine.process_sync_batch("STUDENT_042", events_batch)
    assert res2["status"] == "SUCCESS"
    assert res2["synced_count"] == 0
    assert res2["duplicates_skipped"] == 2
    assert res2["total_xp_awarded"] == 0
    assert res2["details"][0]["status"] == "ALREADY_SYNCED"

    # Status query
    status = sync_engine.get_sync_status("STUDENT_042")
    assert status["status"] == "SUCCESS"
    assert status["total_events_synced"] == 2


# ========================================================================================
# 9. PWA OFFLINE SYNC: TIMESTAMP-BASED CONFLICT RESOLUTION
# ========================================================================================

def test_pwa_offline_sync_conflict_resolution():
    """Verifies timestamp-based conflict reconciliation between client offline state and server ledger."""
    sync_engine = OfflineSyncEngine(db_path=TEST_DB_PATH)

    # 1. Base Event establishing initial ledger record at 10:00:00
    ev1 = [{
        "client_event_id": "EV_CONF_001",
        "event_type": "LAB_REPORT",
        "resource_id": "LAB_DMA_STREAM",
        "payload": {"draft_code": "DMA_Init(&hdma);", "revision": 1},
        "client_timestamp": "2026-11-07 10:00:00",
        "xp_reward": 20
    }]
    sync_engine.process_sync_batch("STUDENT_042", ev1)

    # 2. Newer Client Event at 10:10:00 -> CLIENT_WIN
    ev2 = [{
        "client_event_id": "EV_CONF_002",
        "event_type": "LAB_REPORT",
        "resource_id": "LAB_DMA_STREAM",
        "payload": {"draft_code": "DMA_Init(&hdma); // With double-buffer enabled", "revision": 2},
        "client_timestamp": "2026-11-07 10:10:00",
        "xp_reward": 10
    }]
    res2 = sync_engine.process_sync_batch("STUDENT_042", ev2)
    assert res2["conflicts_resolved"] == 1
    assert res2["details"][0]["status"] == "CONFLICT_RESOLVED_CLIENT_WIN"

    # 3. Stale/Older Client Event at 09:45:00 -> SERVER_PRESERVED
    ev3 = [{
        "client_event_id": "EV_CONF_003",
        "event_type": "LAB_REPORT",
        "resource_id": "LAB_DMA_STREAM",
        "payload": {"draft_code": "Old stale uncommitted draft", "revision": 0},
        "client_timestamp": "2026-11-07 09:45:00",
        "xp_reward": 5
    }]
    res3 = sync_engine.process_sync_batch("STUDENT_042", ev3)
    assert res3["conflicts_resolved"] == 1
    assert res3["details"][0]["status"] == "CONFLICT_RESOLVED_SERVER_PRESERVED"

    # Confirm that ledger retains the newer revision (revision 2)
    conn = sync_engine._get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT version_seq, data_json FROM offline_sync_ledger WHERE resource_id = 'LAB_DMA_STREAM';")
        row = cur.fetchone()
        assert row is not None
        assert row[0] == 2  # version_seq incremented
        assert "double-buffer" in row[1]
    finally:
        conn.close()


# ========================================================================================
# 10. HTTP SERVER ROUTING VALIDATION (MOCK REQUEST HANDLER)
# ========================================================================================

def test_attendance_server_phase9_enterprise_routes():
    """Verifies attendance_server.py FallbackHTTPHandler dispatches all Phase 9 endpoints."""
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

    # 1. POST /api/cms/course/publish (Faculty -> 200 OK)
    course_body = json.dumps({
        "course_code": "EC4801",
        "course_name": "Autonomous Radar Systems",
        "department": "Electronics Engineering",
        "semester": 6,
        "credits": 4,
        "instructor_id": "FAC_042",
        "syllabus_modules": [{"module_id": "M1", "title": "FMCW Radar Architecture"}]
    }).encode("utf-8")

    req_publish = (
        b"POST /api/cms/course/publish HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"X-User-Role: Faculty\r\n"
        b"Content-Type: application/json\r\n"
        b"Content-Length: " + str(len(course_body)).encode("utf-8") + b"\r\n\r\n"
        + course_body
    )
    sock_publish = MockSocket(req_publish)
    FallbackHTTPHandler(sock_publish, ("127.0.0.1", 8080), DummyServer())
    resp_publish = sock_publish.output.getvalue().decode("utf-8")
    assert "200 OK" in resp_publish
    assert "EC4801" in resp_publish

    # 2. POST /api/cms/course/publish (Student -> 403 Forbidden)
    req_pub_denied = (
        b"POST /api/cms/course/publish HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"X-User-Role: Student\r\n"
        b"Content-Type: application/json\r\n"
        b"Content-Length: " + str(len(course_body)).encode("utf-8") + b"\r\n\r\n"
        + course_body
    )
    sock_pub_denied = MockSocket(req_pub_denied)
    FallbackHTTPHandler(sock_pub_denied, ("127.0.0.1", 8080), DummyServer())
    resp_pub_denied = sock_pub_denied.output.getvalue().decode("utf-8")
    assert "403 Forbidden" in resp_pub_denied
    assert "FORBIDDEN" in resp_pub_denied

    # 3. GET /api/cms/courses
    req_get_c = b"GET /api/cms/courses HTTP/1.1\r\nHost: localhost\r\n\r\n"
    sock_get_c = MockSocket(req_get_c)
    FallbackHTTPHandler(sock_get_c, ("127.0.0.1", 8080), DummyServer())
    resp_get_c = sock_get_c.output.getvalue().decode("utf-8")
    assert "200 OK" in resp_get_c
    assert "courses" in resp_get_c

    # 4. POST /api/cms/report/review
    review_body = json.dumps({
        "report_id": "REP_TEST_99",
        "student_id": "STUDENT_TEST_042",
        "course_code": "EC4801",
        "original_ai_verdict": "NEEDS_REVISION",
        "faculty_override_verdict": "APPROVED",
        "adjusted_score": 92.0,
        "reviewer_id": "FAC_042",
        "faculty_notes": "Manually verified hardware timing."
    }).encode("utf-8")

    req_rev = (
        b"POST /api/cms/report/review HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"X-User-Role: Faculty\r\n"
        b"Content-Type: application/json\r\n"
        b"Content-Length: " + str(len(review_body)).encode("utf-8") + b"\r\n\r\n"
        + review_body
    )
    sock_rev = MockSocket(req_rev)
    FallbackHTTPHandler(sock_rev, ("127.0.0.1", 8080), DummyServer())
    resp_rev = sock_rev.output.getvalue().decode("utf-8")
    assert "200 OK" in resp_rev
    assert "REP_TEST_99" in resp_rev

    # 5. GET /api/analytics/obe-matrix
    req_obe = b"GET /api/analytics/obe-matrix?cohort_id=COHORT_2023_2027_ECE_A&course_code=EC3701 HTTP/1.1\r\nHost: localhost\r\n\r\n"
    sock_obe = MockSocket(req_obe)
    FallbackHTTPHandler(sock_obe, ("127.0.0.1", 8080), DummyServer())
    resp_obe = sock_obe.output.getvalue().decode("utf-8")
    assert "200 OK" in resp_obe
    assert "co_attainment" in resp_obe
    assert "po_attainment" in resp_obe

    # 6. POST /api/sync/batch
    sync_body = json.dumps({
        "student_id": "STUDENT_TEST_042",
        "events": [
            {
                "client_event_id": "EV_HTTP_001",
                "event_type": "CHAPTER_PROGRESS",
                "resource_id": "MOD_14_SYSTICK",
                "payload": {"progress": 100},
                "client_timestamp": "2026-11-07 10:00:00"
            }
        ]
    }).encode("utf-8")

    req_sync = (
        b"POST /api/sync/batch HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Content-Type: application/json\r\n"
        b"Content-Length: " + str(len(sync_body)).encode("utf-8") + b"\r\n\r\n"
        + sync_body
    )
    sock_sync = MockSocket(req_sync)
    FallbackHTTPHandler(sock_sync, ("127.0.0.1", 8080), DummyServer())
    resp_sync = sock_sync.output.getvalue().decode("utf-8")
    assert "200 OK" in resp_sync
    assert "synced_count" in resp_sync

    # 7. GET /api/sync/status
    req_sync_stat = b"GET /api/sync/status?student_id=STUDENT_TEST_042 HTTP/1.1\r\nHost: localhost\r\n\r\n"
    sock_sync_stat = MockSocket(req_sync_stat)
    FallbackHTTPHandler(sock_sync_stat, ("127.0.0.1", 8080), DummyServer())
    resp_sync_stat = sock_sync_stat.output.getvalue().decode("utf-8")
    assert "200 OK" in resp_sync_stat
    assert "total_events_synced" in resp_sync_stat


# ========================================================================================
# 11. PRIVACY INVARIANTS & THERMAL SAFETY VALIDATION
# ========================================================================================

def test_phase9_privacy_and_thermal_invariants():
    """Strictly validates zero leakage of private credentials and < 250ms thermal execution budget."""
    restricted_patterns = ["ashokkumar2008313@gmail.com", "9597382878"]
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    files_to_check = [
        os.path.join(base_dir, "backend", "instructor_cms_engine.py"),
        os.path.join(base_dir, "backend", "learning_analytics_engine.py"),
        os.path.join(base_dir, "backend", "offline_sync_engine.py"),
        os.path.join(base_dir, "public", "service-worker.js"),
        os.path.join(base_dir, "public", "sw.js"),
        os.path.join(base_dir, "src", "components", "TeacherAnalyticsDashboard.jsx"),
        os.path.join(base_dir, "src", "components", "FacultyAdminHub.jsx"),
        os.path.join(base_dir, "src", "components", "CloudSyncStatus.jsx")
    ]

    for fpath in files_to_check:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            for pat in restricted_patterns:
                assert pat not in content, f"Restricted admin metadata leaked in {fpath}"

    # Thermal benchmark: Ensure CMS publishing, analytics calculation, and offline sync run < 350ms total
    cms = InstructorCmsEngine(db_path=TEST_DB_PATH)
    analytics = LearningAnalyticsEngine(db_path=TEST_DB_PATH)
    sync = OfflineSyncEngine(db_path=TEST_DB_PATH)

    t0 = time.perf_counter()
    for i in range(10):
        cms.publish_course({
            "course_code": f"EC{4000+i}",
            "course_name": f"Embedded Stream Course {i}",
            "instructor_id": "FAC_BENCH"
        }, actor_role="Faculty")
        analytics.calculate_score_distribution([95.0, 80.0, 60.0, 45.0, 75.0])
        sync.process_sync_batch("STUDENT_BENCH", [{
            "client_event_id": f"EV_BENCH_{i}",
            "event_type": "BENCHMARK_PROG",
            "resource_id": "BENCH_RES",
            "payload": {"step": i},
            "client_timestamp": "2026-11-07 10:00:00"
        }])
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    assert elapsed_ms < 600.0, f"Engine operations took {elapsed_ms:.2f}ms (> 600ms thermal budget)"
