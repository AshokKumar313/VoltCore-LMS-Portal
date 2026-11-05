"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 11 Student Experience & Collaboration Hub
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase11_collaboration.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import tempfile
import unittest
from backend.collaboration_hub import CollaborationHub


class TestPhase11Collaboration(unittest.TestCase):
    """
    Validation suite for Phase 11:
      - Student project portfolio submissions & domain queries
      - Peer code review rubric evaluation & status transitions
      - Study cohort group creation, member limits & enrollment
      - Academic leaderboard XP tracking & Silicon Grandmaster tiers
      - RBAC permission barriers on endorsements
      - Astro page, React island component & data privacy invariants
    """

    def setUp(self):
        # Create an isolated temporary SQLite database for each test
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.hub = CollaborationHub(db_path=self.temp_db_path)
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except Exception:
                pass

    def test_portfolio_submission_and_listing(self):
        """Validates student engineering portfolio submission and domain filtering."""
        res = self.hub.submit_portfolio_project(
            student_id="2023MITEC099",
            student_name="Test Candidate",
            title="STM32 FreeRTOS CAN-Bus Node",
            description="CAN 2.0B bus analyzer with hardware frame filtering and LittleFS spooling.",
            domain="Embedded Firmware",
            tech_stack=["STM32", "CAN", "FreeRTOS"],
            repo_url="https://github.com/AshokKumar313/can-bus-node",
            wokwi_url="",
            hardware_hil_verified=True
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["xp_awarded"], 200)

        # Query all portfolios
        all_projects = self.hub.list_portfolio_projects()
        self.assertGreaterEqual(len(all_projects), 4)

        # Domain filter test
        firmware_projects = self.hub.list_portfolio_projects(domain="Embedded Firmware")
        self.assertTrue(all(p["domain"] == "Embedded Firmware" for p in firmware_projects))
        self.assertTrue(any(p["title"] == "STM32 FreeRTOS CAN-Bus Node" for p in firmware_projects))

    def test_portfolio_upvote_likes(self):
        """Validates thumbs-up peer endorsements on portfolio items."""
        projects = self.hub.list_portfolio_projects()
        first_proj_id = projects[0]["project_id"]
        initial_likes = projects[0]["likes_count"]

        res = self.hub.like_project(first_proj_id)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["likes_count"], initial_likes + 1)

    def test_portfolio_endorsement_rbac_barrier(self):
        """Validates that only privileged roles (Admin/Teacher) can feature or endorse projects."""
        projects = self.hub.list_portfolio_projects()
        target_id = projects[0]["project_id"]

        # Student attempt must be forbidden
        unauth_res = self.hub.endorse_portfolio_project(
            project_id=target_id,
            actor_role="Student",
            new_status="FEATURED"
        )
        self.assertEqual(unauth_res["status"], "FORBIDDEN")

        # Admin / Teacher attempt must succeed
        auth_res = self.hub.endorse_portfolio_project(
            project_id=target_id,
            actor_role="Admin",
            new_status="FEATURED"
        )
        self.assertEqual(auth_res["status"], "SUCCESS")
        self.assertEqual(auth_res["new_status"], "FEATURED")

    def test_peer_review_rubric_scoring_and_status_transitions(self):
        """Validates rubric-based peer code reviews, scoring threshold, and +150 XP rewards."""
        # 1. High-scoring review (overall >= 7.0) -> APPROVED
        approved_res = self.hub.submit_peer_review(
            project_id="PRJ-MIT-002",
            reviewer_id="2023MITEC042",
            reviewer_name="Ashok Kumar A",
            rubric_scores={
                "code_quality": 9.0,
                "timing_safety": 8.5,
                "memory_efficiency": 9.0,
                "test_coverage": 8.5
            },
            comments="Flawless DMA circular ring buffer implementation."
        )
        self.assertEqual(approved_res["status"], "SUCCESS")
        self.assertEqual(approved_res["decision"], "APPROVED")
        self.assertEqual(approved_res["xp_awarded"], 150)
        self.assertGreaterEqual(approved_res["overall_score"], 7.0)

        # 2. Low-scoring review (overall < 7.0) -> CHANGES_REQUESTED
        rejection_res = self.hub.submit_peer_review(
            project_id="PRJ-MIT-003",
            reviewer_id="2023MITEC018",
            reviewer_name="Priya Swaminathan",
            rubric_scores={
                "code_quality": 5.0,
                "timing_safety": 4.5,
                "memory_efficiency": 6.0,
                "test_coverage": 5.0
            },
            comments="Missing timeout guards on while loops; potential CPU hang detected."
        )
        self.assertEqual(rejection_res["status"], "SUCCESS")
        self.assertEqual(rejection_res["decision"], "CHANGES_REQUESTED")
        self.assertLess(rejection_res["overall_score"], 7.0)

    def test_study_group_creation_and_member_enrollment(self):
        """Validates creating study cohorts, member capacity constraints, and joining rewards."""
        # 1. Create a study group
        create_res = self.hub.create_study_group(
            group_name="VLSI Timing Closure Sprint",
            subject_code="EC8702",
            topic="Setup & Hold Time Violations in Synchronous RTL Pipelines",
            leader_id="2023MITEC042",
            leader_name="Ashok Kumar A",
            schedule_slot="Friday 17:00 IST",
            meeting_link="https://meet.mitindia.edu/vlsi-sprint",
            max_members=2  # small capacity to test boundary
        )
        self.assertEqual(create_res["status"], "SUCCESS")
        self.assertEqual(create_res["xp_awarded"], 100)
        gid = create_res["group_id"]

        # 2. Join group (fills capacity to 2/2)
        join_res = self.hub.join_study_group(
            group_id=gid,
            student_id="2023MITEC018",
            student_name="Priya Swaminathan"
        )
        self.assertEqual(join_res["status"], "SUCCESS")
        self.assertEqual(join_res["xp_awarded"], 50)

        # 3. Third member attempt must return FULL
        full_res = self.hub.join_study_group(
            group_id=gid,
            student_id="2023MITEC055",
            student_name="Karthik Ramanathan"
        )
        self.assertEqual(full_res["status"], "FULL")

    def test_leaderboard_xp_calculation_and_tier_sorting(self):
        """Validates leaderboard XP ranking, tier derivations, and streak tracking."""
        leaderboard = self.hub.get_leaderboard(limit=5)
        self.assertEqual(len(leaderboard), 5)

        # Top ranked student must be Ashok Kumar A
        top_student = leaderboard[0]
        self.assertEqual(top_student["rank"], 1)
        self.assertEqual(top_student["roll_no"], "2023MITEC042")
        self.assertEqual(top_student["tier"], "Silicon Grandmaster")
        self.assertGreaterEqual(top_student["xp"], 4850)

        # Verify descending XP order
        xps = [s["xp"] for s in leaderboard]
        self.assertEqual(xps, sorted(xps, reverse=True))

        # Test dynamic tier derivation
        self.assertEqual(CollaborationHub._calculate_tier(4500), "Silicon Grandmaster")
        self.assertEqual(CollaborationHub._calculate_tier(3500), "Firmware Architect")
        self.assertEqual(CollaborationHub._calculate_tier(2500), "Embedded Specialist")
        self.assertEqual(CollaborationHub._calculate_tier(1200), "Circuit Novice")

    def test_collaboration_page_and_component_exist(self):
        """Ensures Astro hosting page and React island component are in place."""
        page_path = os.path.join(self.base_dir, "src", "pages", "collaboration.astro")
        component_path = os.path.join(self.base_dir, "src", "components", "StudentPortfolioHub.jsx")

        self.assertTrue(os.path.isfile(page_path), "src/pages/collaboration.astro must exist")
        self.assertTrue(os.path.isfile(component_path), "src/components/StudentPortfolioHub.jsx must exist")

        with open(page_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("StudentPortfolioHub", content)
            self.assertIn("Madras Institute of Technology", content)
            self.assertIn("Ashok Kumar A", content)

    def test_data_privacy_invariants_no_leakage(self):
        """Strictly ensures private admin contact credentials are never present in client files."""
        restricted_patterns = [
            "ashokkumar2008313@gmail.com",
            "+91 9597382878",
            "9597382878"
        ]
        files_to_check = [
            os.path.join(self.base_dir, "src", "pages", "collaboration.astro"),
            os.path.join(self.base_dir, "src", "components", "StudentPortfolioHub.jsx"),
            os.path.join(self.base_dir, "backend", "collaboration_hub.py")
        ]

        for filepath in files_to_check:
            if not os.path.isfile(filepath):
                continue
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                for pattern in restricted_patterns:
                    self.assertNotIn(
                        pattern,
                        content,
                        f"Data privacy breach: Restricted credential '{pattern}' found in '{filepath}'!"
                    )


if __name__ == "__main__":
    unittest.main()
