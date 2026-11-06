"""
========================================================================================
VoltCore Apex Academia - Unit Tests for Phase O: Faculty & Administrative Management
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
========================================================================================
"""

import os
import pytest
import tempfile
from backend.faculty_admin_engine import (
    FacultyAdminEngine,
    DEFAULT_FACULTY_COURSES,
    DEFAULT_TIMETABLE,
    DEFAULT_NOTICES
)

@pytest.fixture
def temp_engine():
    """Create an isolated temporary SQLite database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = FacultyAdminEngine(db_path=path)
    yield engine
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def test_faculty_dashboard_overview(temp_engine):
    """Feature 351: Faculty Dashboard metrics."""
    dash = temp_engine.get_faculty_dashboard(faculty_id="fac_01")
    assert dash["faculty_id"] == "fac_01"
    assert dash["total_courses"] >= 1
    assert dash["total_students"] >= 64
    assert "assigned_courses" in dash


def test_student_enrollment_and_analytics(temp_engine):
    """Feature 352: Student Performance Analytics & At-Risk radar."""
    # 1. Enroll high-performing student
    temp_engine.enroll_student(
        student_roll="2023MITEC042",
        student_name="Ashok Kumar A",
        course_code="EC3552",
        internal_1=48.0,
        internal_2=49.0,
        internal_3=50.0,
        assignment_score=98.0,
        attendance_pct=96.0,
        cgpa=9.42
    )

    # 2. Enroll at-risk student (attendance shortage and low CGPA)
    temp_engine.enroll_student(
        student_roll="2023MITEC099",
        student_name="Arun V",
        course_code="EC3552",
        internal_1=20.0,
        internal_2=18.0,
        internal_3=22.0,
        assignment_score=40.0,
        attendance_pct=68.0, # < 75%
        cgpa=5.80            # < 6.5
    )

    analytics = temp_engine.get_course_analytics("EC3552")
    assert analytics["enrolled_count"] == 2
    assert analytics["pass_percentage"] >= 50.0
    assert analytics["at_risk_count"] == 1
    assert analytics["at_risk_students"][0]["student_roll"] == "2023MITEC099"
    assert "Attendance Shortage" in analytics["at_risk_students"][0]["reasons"][1]


def test_assignment_grading_rubric(temp_engine):
    """Feature 353: Assignment Grading Suite with 4-pillar ECE rubric."""
    sub = temp_engine.submit_assignment(
        submission_id="sub_vlsi_01",
        student_roll="2023MITEC042",
        student_name="Ashok Kumar A",
        assignment_title="Lab 3: CMOS Inverter Layout and DRC/LVS Sign-Off",
        course_code="EC3552"
    )
    assert sub["status"] == "success"

    # Grade with rubric: circuit=28, sim=29, viva=19, report=19 => 95.0 total
    graded = temp_engine.grade_assignment(
        submission_id="sub_vlsi_01",
        circuit_score=28.0,
        sim_score=29.0,
        viva_score=19.0,
        report_score=19.0,
        feedback="Clean DRC/LVS run without latchup violations. Excellent transient rise/fall symmetry."
    )
    assert graded["status"] == "success"
    assert graded["total_score"] == 95.0

    submissions = temp_engine.get_assignment_submissions("EC3552")
    assert len(submissions) == 1
    assert submissions[0]["is_graded"] == 1
    assert submissions[0]["total_score"] == 95.0


def test_attendance_evaluation_cutoff(temp_engine):
    """Feature 354: Anna University Regulation 2023 75% Cutoff evaluation."""
    # Satisfactory
    s1 = temp_engine.evaluate_attendance_status(92.5)
    assert s1["badge"] == "SATISFACTORY"
    assert s1["status"] == "ELIGIBLE"

    # Condonation range (75% to 79.9%)
    s2 = temp_engine.evaluate_attendance_status(77.0)
    assert s2["badge"] == "CONDONATION"
    assert s2["status"] == "CONDONATION_REQUIRED"

    # Debarred (< 75%)
    s3 = temp_engine.evaluate_attendance_status(71.4)
    assert s3["badge"] == "ATTENDANCE_SHORTAGE"
    assert s3["status"] == "DEBARRED"


def test_course_material_upload(temp_engine):
    """Feature 355: Course Material Upload Manager."""
    res = temp_engine.upload_course_material(
        material_id="mat_ec3552_01",
        course_code="EC3552",
        title="Cadence Innovus Floorplanning & Power Mesh Guidelines",
        category="LAB_MANUAL",
        file_url="https://voltcore.annauniv.edu/courses/ec3552_lab_manual.pdf",
        uploaded_by="Dr. P. Nirmal"
    )
    assert res["status"] == "success"

    materials = temp_engine.list_course_materials("EC3552")
    assert len(materials) == 1
    assert materials[0]["category"] == "LAB_MANUAL"


def test_announcement_broadcast(temp_engine):
    """Feature 356 & 358: Announcement Broadcast & Department Notice Board."""
    res = temp_engine.broadcast_announcement(
        announcement_id="ann_eval_01",
        title="Lab Internal Assessment Test II Timetable",
        target_audience="SEM_5",
        category="EXAM",
        priority="URGENT",
        author_name="Dr. P. Nirmal",
        content="Lab internal practicals commence on November 20. Netlists and viva portfolios must be finalized."
    )
    assert res["status"] == "success"

    notices = temp_engine.get_department_notices()
    assert len(notices) >= 4
    assert any("Lab Internal Assessment" in n["title"] for n in notices)


def test_student_progress_dossier_generation(temp_engine):
    """Feature 357: Student Progress Report Card (Anna Univ Reg 2023 O-to-U grades)."""
    temp_engine.enroll_student(
        student_roll="2023MITEC042",
        student_name="Ashok Kumar A",
        course_code="EC3552",
        internal_1=48.0, internal_2=49.0, internal_3=50.0,
        assignment_score=95.0, attendance_pct=98.0, cgpa=9.45
    )
    temp_engine.enroll_student(
        student_roll="2023MITEC042",
        student_name="Ashok Kumar A",
        course_code="EC3711",
        internal_1=46.0, internal_2=48.0, internal_3=48.0,
        assignment_score=92.0, attendance_pct=95.0, cgpa=9.45
    )

    dossier = temp_engine.generate_student_progress_dossier("2023MITEC042")
    assert dossier is not None
    assert dossier["student_name"] == "Ashok Kumar A"
    assert len(dossier["courses"]) == 2
    assert dossier["courses"][0]["letter_grade"] in ["O", "A+"]
    assert dossier["semester_gpa"] >= 9.0


def test_timetable_retrieval(temp_engine):
    """Feature 359: Timetable & Schedule Manager."""
    mon_schedule = temp_engine.get_timetable(day="MON")
    assert len(mon_schedule) >= 3
    assert mon_schedule[0]["course_code"] == "EC3552"
    assert "ECE-LH1" in mon_schedule[0]["room"]


def test_faculty_office_hours_booking(temp_engine):
    """Feature 360: Faculty Office Hours Scheduler."""
    temp_engine.add_office_slot(
        slot_id="slot_fac01_tue",
        faculty_id="fac_01",
        faculty_name="Dr. P. Nirmal",
        day="TUE",
        time="14:00 - 15:00",
        mode="IN_PERSON",
        room_or_url="Room ECE-302"
    )

    # 1. Book available slot
    book_res = temp_engine.book_office_slot(
        slot_id="slot_fac01_tue",
        student_roll="2023MITEC042",
        student_name="Ashok Kumar A"
    )
    assert book_res["status"] == "success"

    # 2. Reject second booking on same slot
    double_book = temp_engine.book_office_slot(
        slot_id="slot_fac01_tue",
        student_roll="2023MITEC055",
        student_name="Kavitha R"
    )
    assert double_book["status"] == "error"
    assert "already booked" in double_book["message"].lower()

    slots = temp_engine.get_office_slots(faculty_id="fac_01")
    assert len(slots) == 1
    assert slots[0]["is_booked"] == 1
    assert slots[0]["booked_by_roll"] == "2023MITEC042"
