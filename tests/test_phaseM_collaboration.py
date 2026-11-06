"""
========================================================================================
VoltCore Apex Academia - Unit Tests for Phase M: Collaboration & Community (Features 331–340)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
========================================================================================
"""

import os
import pytest
import tempfile
from backend.collaboration_community_engine import (
    CollaborationCommunityEngine,
    AU_REG2023_SUBJECTS,
    FACULTY_DIRECTORY,
    DEFAULT_ANNOUNCEMENTS
)

@pytest.fixture
def temp_engine():
    """Create an isolated temporary SQLite database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = CollaborationCommunityEngine(db_path=path)
    yield engine
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def test_forum_posts_and_replies(temp_engine):
    """Feature 331: Student Discussion Forums (post, reply, upvote, solution)."""
    # 1. Post a forum thread
    res = temp_engine.post_forum_message(
        post_id="post_001",
        title="Setup vs Hold time violation fix on TSMC 28nm",
        category="VLSI",
        author_name="Ashok Kumar A",
        author_roll="2023MITEC042",
        content="How do delay cells inserted in the data path prevent hold time violations without degrading clock frequency?",
        tags=["VLSI", "STA", "HoldTime"]
    )
    assert res["status"] == "success"
    assert res["post_id"] == "post_001"

    # 2. Reply to thread
    reply_res = temp_engine.reply_forum_post(
        reply_id="rep_001",
        post_id="post_001",
        author_name="Kavitha R",
        author_roll="2023MITEC055",
        content="Hold time check is independent of clock period. Adding buffer delay in the data path increases t_cq + t_comb to satisfy t_hold."
    )
    assert reply_res["status"] == "success"

    # 3. Upvote post
    up_res = temp_engine.upvote_forum_post("post_001")
    assert up_res["status"] == "success"
    assert up_res["upvotes"] == 1

    # 4. Mark reply as solution
    sol_res = temp_engine.mark_forum_solution("post_001", "rep_001")
    assert sol_res["status"] == "success"
    assert sol_res["solution_id"] == "rep_001"

    posts = temp_engine.get_forum_posts(category="VLSI")
    assert len(posts) == 1
    assert posts[0]["solution_id"] == "rep_001"
    assert posts[0]["reply_count"] == 1


def test_subject_wise_questions(temp_engine):
    """Feature 332: Subject-Wise Question Community (Anna Univ Reg 2023)."""
    # 1. Post question for valid subject EC3351
    q_res = temp_engine.post_subject_question(
        q_id="q_ec3351_01",
        subject_code="EC3351",
        title="Bode plot gain margin calculation with non-minimum phase zero",
        question_text="How does an RHP zero shift the phase angle curve and impact gain margin stability?",
        author_roll="2023MITEC042"
    )
    assert q_res["status"] == "success"
    assert q_res["subject_name"] == "Control Systems"

    # 2. Reject invalid subject code
    invalid_res = temp_engine.post_subject_question(
        q_id="q_invalid",
        subject_code="CS9999",
        title="Invalid course",
        question_text="Test invalid",
        author_roll="2023MITEC042"
    )
    assert invalid_res["status"] == "error"

    # 3. Submit verified answer
    ans_res = temp_engine.answer_subject_question(
        ans_id="ans_001",
        question_id="q_ec3351_01",
        author_roll="2023MITEC088",
        author_name="Ramesh K",
        answer_text="An RHP zero introduces +20dB/dec magnitude slope but -90 deg phase lag, dramatically eroding phase margin.",
        is_verified=True
    )
    assert ans_res["status"] == "success"

    q_list = temp_engine.get_subject_questions(subject_code="EC3351")
    assert len(q_list) == 1
    assert q_list[0]["answers_count"] == 1


def test_study_group_lifecycle(temp_engine):
    """Feature 333: Study Group Creator (Create, join, capacity enforcement, leave)."""
    # 1. Create study group with max 2 members
    grp_res = temp_engine.create_study_group(
        group_id="grp_vlsi_01",
        name="VLSI Physical Synthesis Cohort",
        subject_code="EC3552",
        topic="Cadence Innovus Floorplanning & CTS",
        max_members=2,
        schedule_time="Tues & Thurs 18:00 IST",
        virtual_room_url="https://meet.jit.si/voltcore-vlsi-01",
        created_by_roll="2023MITEC042",
        creator_name="Ashok Kumar A"
    )
    assert grp_res["status"] == "success"
    assert grp_res["members_count"] == 1

    # 2. Join group (2nd member - succeeds)
    j1 = temp_engine.join_study_group("grp_vlsi_01", "2023MITEC010", "Dinesh S")
    assert j1["status"] == "success"

    # 3. Join group (3rd member - rejected due to capacity limit)
    j2 = temp_engine.join_study_group("grp_vlsi_01", "2023MITEC011", "Swetha M")
    assert j2["status"] == "error"
    assert "capacity" in j2["message"].lower()

    # 4. Leave group and re-join
    temp_engine.leave_study_group("grp_vlsi_01", "2023MITEC010")
    j3 = temp_engine.join_study_group("grp_vlsi_01", "2023MITEC011", "Swetha M")
    assert j3["status"] == "success"

    groups = temp_engine.list_study_groups()
    assert len(groups) == 1
    assert groups[0]["member_count"] == 2


def test_collaborative_notes(temp_engine):
    """Feature 334: Collaborative Notes Workspace (Markdown, revision tracking)."""
    # 1. Create version 1 note
    n1 = temp_engine.create_or_update_note(
        note_id="note_dsp_01",
        title="FFT Radix-2 Cooley-Tukey Butterflies",
        subject_code="EC3351",
        content_markdown="# Radix-2 DIT FFT\nTwiddle factor W_N^k = e^{-j 2\\pi k / N}.",
        authors=["Ashok Kumar A"],
        tags=["DSP", "FFT", "Algorithms"]
    )
    assert n1["version"] == 1

    # 2. Revise note to version 2
    n2 = temp_engine.create_or_update_note(
        note_id="note_dsp_01",
        title="FFT Radix-2 Cooley-Tukey Butterflies (Updated)",
        subject_code="EC3351",
        content_markdown="# Radix-2 DIT FFT\nTwiddle factor W_N^k = e^{-j 2\\pi k / N}.\nComputational complexity O(N log2 N).",
        authors=["Ashok Kumar A", "Priya B"],
        tags=["DSP", "FFT", "Complexity"]
    )
    assert n2["version"] == 2

    note = temp_engine.get_note("note_dsp_01")
    assert note["version"] == 2
    assert "Priya B" in note["authors"]

    all_notes = temp_engine.list_notes(subject_code="EC3351")
    assert len(all_notes) == 1


def test_peer_assignment_review(temp_engine):
    """Feature 335: Peer Assignment Review (Rubric weighted evaluation)."""
    # circuit=9.0, sim=8.0, doc=10.0 => 0.40*9.0 + 0.35*8.0 + 0.25*10.0 = 3.6 + 2.8 + 2.5 = 8.90
    rev = temp_engine.submit_peer_review(
        review_id="rev_001",
        assignment_title="Lab 4: Op-Amp Second-Order Sallen-Key Low Pass Filter",
        subject_code="EC3451",
        student_roll="2023MITEC042",
        reviewer_roll="2023MITEC015",
        circuit_score=9.0,
        sim_score=8.0,
        doc_score=10.0,
        comments="Clean SPICE schematic and Monte Carlo component tolerance analysis. Excellent passband flatness."
    )
    assert rev["status"] == "success"
    assert rev["overall_score"] == 8.90

    # Test clamping of out-of-range values (>10.0 capped to 10.0)
    rev2 = temp_engine.submit_peer_review(
        review_id="rev_002",
        assignment_title="Lab 5: Verilog UART Transmitter",
        subject_code="EC3352",
        student_roll="2023MITEC042",
        reviewer_roll="2023MITEC018",
        circuit_score=15.0, # should clamp to 10.0
        sim_score=10.0,
        doc_score=10.0,
        comments="Flawless baud rate generator."
    )
    assert rev2["overall_score"] == 10.0

    student_revs = temp_engine.get_assignment_reviews("2023MITEC042")
    assert len(student_revs) == 2


def test_project_team_board(temp_engine):
    """Feature 336: Project Team Discussion Board (Sprint tasks & status)."""
    temp_engine.create_project_board(
        board_id="board_smart_inhaler",
        project_title="Smart IoT Nebulizer with Edge TinyML",
        sprint_goal="Complete I2C pressure sensor reading & FreeRTOS task scheduling",
        created_by="Ashok Kumar A"
    )

    t1 = temp_engine.add_project_task("task_01", "board_smart_inhaler", "Configure BMP280 over I2C1", "Ashok Kumar A", "TODO")
    t2 = temp_engine.add_project_task("task_02", "board_smart_inhaler", "Create FreeRTOS sampling task (100Hz)", "Kavitha R", "TODO")
    assert t1["status"] == "TODO"

    temp_engine.update_task_status("task_01", "DONE")
    temp_engine.update_task_status("task_02", "IN_PROGRESS")

    board = temp_engine.get_project_board("board_smart_inhaler")
    assert board["project_title"] == "Smart IoT Nebulizer with Edge TinyML"
    assert len(board["tasks"]) == 2
    t1_found = next(t for t in board["tasks"] if t["id"] == "task_01")
    assert t1_found["status"] == "DONE"


def test_faculty_doubt_clearing(temp_engine):
    """Feature 337: Faculty Doubt-Clearing Portal (Direct queries, office hours)."""
    # 1. Student submits doubt to Dr. P. Nirmal
    doubt = temp_engine.submit_faculty_doubt(
        doubt_id="dbt_001",
        student_roll="2023MITEC042",
        faculty_id="fac_01",
        subject_code="EC3552",
        query_text="Sir, when setting up multi-corner multi-mode (MCMM) STA, how do we treat OCV derates for hold vs setup?",
        priority="HIGH"
    )
    assert doubt["status"] == "success"
    assert doubt["faculty_name"] == "Dr. P. Nirmal"
    assert doubt["status_code"] == "PENDING"

    # 2. Faculty responds
    res = temp_engine.respond_faculty_doubt(
        doubt_id="dbt_001",
        faculty_response="For hold analysis, use late derate on launch clock/data and early derate on capture clock path."
    )
    assert res["status_code"] == "RESOLVED"

    doubts = temp_engine.get_faculty_doubts(student_roll="2023MITEC042")
    assert len(doubts) == 1
    assert doubts[0]["status"] == "RESOLVED"
    assert "Tues/Thurs" in doubts[0]["office_hours"]


def test_shared_resource_library(temp_engine):
    """Feature 338: Shared Resource Library (Netlists, testbenches, downloads)."""
    up = temp_engine.upload_shared_resource(
        resource_id="res_001",
        title="LTspice Subcircuit: TSMC 65nm CMOS Inverter VTC",
        category="SPICE_NETLIST",
        subject_code="EC3552",
        uploader_name="Ashok Kumar A",
        uploader_roll="2023MITEC042",
        file_url="https://voltcore.annauniv.edu/resources/cmos_65nm.cir"
    )
    assert up["status"] == "success"

    temp_engine.upvote_resource("res_001")
    temp_engine.upvote_resource("res_001")
    down = temp_engine.download_resource("res_001")
    assert down["downloads"] == 1

    resources = temp_engine.list_shared_resources(category="SPICE_NETLIST")
    assert len(resources) == 1
    assert resources[0]["upvotes"] == 2


def test_student_karma_and_badges(temp_engine):
    """Feature 339: Student Knowledge Contribution Points & Badge awards."""
    # 1. Award points in VLSI
    temp_engine.award_karma_points("2023MITEC042", "Ashok Kumar A", 55, domain="VLSI")
    karma = temp_engine.get_student_karma("2023MITEC042")
    assert karma["points"] == 55
    assert "silicon_scholar" in karma["badges"]

    # 2. Award additional points to cross 100 threshold
    temp_engine.award_karma_points("2023MITEC042", "Ashok Kumar A", 50, domain="Embedded")
    karma2 = temp_engine.get_student_karma("2023MITEC042")
    assert karma2["points"] == 105
    assert "rtos_champion" in karma2["badges"]
    assert "apex_fellow" in karma2["badges"]

    # 3. Verify leaderboard
    temp_engine.award_karma_points("2023MITEC099", "Student B", 20, domain="Signals")
    lb = temp_engine.get_karma_leaderboard(limit=5)
    assert len(lb) == 2
    assert lb[0]["student_roll"] == "2023MITEC042"
    assert lb[0]["rank"] == 1


def test_academic_announcements(temp_engine):
    """Feature 340: Academic Announcement Feed (Anna Univ & MIT circulars)."""
    ann = temp_engine.get_announcements()
    assert len(ann) >= 4

    urgent = temp_engine.get_announcements(priority="URGENT")
    assert len(urgent) >= 1
    assert any("End-Semester Practical" in a["title"] for a in urgent)

    hackathons = temp_engine.get_announcements(category="HACKATHON")
    assert len(hackathons) >= 1
    assert "VoltCore Hackathon" in hackathons[0]["title"]
