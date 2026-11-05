"""
========================================================================================
VoltCore Apex Academia - Test Suite: Phase 12 Research Discovery & Knowledge Engine
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_phase12_research_discovery.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import tempfile
import unittest
from backend.research_discovery_engine import ResearchDiscoveryEngine


class TestPhase12ResearchDiscovery(unittest.TestCase):
    """
    Validation suite for Phase 12:
      - IEEE citation parsing and BibTeX generation
      - Semantic & keyword paper retrieval
      - Multi-paper literature review synthesis
      - Novel research hypothesis formulation
      - RBAC permission barriers on institutional paper indexing
      - Astro page, React island component & data privacy invariants
    """

    def setUp(self):
        # Create an isolated temporary SQLite database for each test
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.engine = ResearchDiscoveryEngine(db_path=self.temp_db_path)
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except Exception:
                pass

    def test_citation_parsing_and_bibtex_export(self):
        """Validates BibTeX input parsing and formatted citation export."""
        raw_bibtex = """
        @article{Kumar2023,
          author  = {Kumar A. and Swaminathan P.},
          title   = {Deterministic FreeRTOS Task Scheduling on STM32H7 Dual-Core},
          journal = {IEEE Transactions on Embedded Systems},
          year    = {2023},
          doi     = {10.1109/TES.2023.1234567}
        }
        """
        parsed = self.engine.parse_bibtex(raw_bibtex)
        self.assertEqual(parsed["status"], "SUCCESS")
        self.assertEqual(parsed["title"], "Deterministic FreeRTOS Task Scheduling on STM32H7 Dual-Core")
        self.assertIn("Kumar A.", parsed["authors"])
        self.assertEqual(parsed["year"], 2023)

        # Test BibTeX export for seeded paper
        exported_bibtex = self.engine.generate_bibtex("IEEE-TCAD-2023-01")
        self.assertIn("@article", exported_bibtex)
        self.assertIn("10.1109/TCAD.2023.8821940", exported_bibtex)
        self.assertIn("Deterministic Real-Time Scheduling", exported_bibtex)

    def test_semantic_and_keyword_search(self):
        """Validates zero-bloat semantic and keyword retrieval with ranking."""
        # 1. Search for RTOS and DMA
        rtos_results = self.engine.search_papers(query="FreeRTOS DMA STM32H7")
        self.assertGreaterEqual(len(rtos_results), 1)
        self.assertEqual(rtos_results[0]["paper_id"], "IEEE-TCAD-2023-01")
        self.assertGreater(rtos_results[0]["relevance_score"], 0)

        # 2. Domain filter
        ai_papers = self.engine.search_papers(domain="IoT & TinyML")
        self.assertTrue(all(p["domain"] == "IoT & TinyML" for p in ai_papers))
        self.assertTrue(any("ESP32-S3" in p["title"] or "TinyML" in p["keywords"] for p in ai_papers))

        # 3. Keyword filter
        gan_papers = self.engine.search_papers(keyword="GaN")
        self.assertTrue(all("GaN" in p["keywords"] for p in gan_papers))

    def test_automated_literature_synthesis(self):
        """Validates automated cross-paper synthesis and gap identification."""
        target_ids = ["IEEE-TCAD-2023-01", "IEEE-JIOT-2024-02"]
        synthesis = self.engine.generate_literature_synthesis(target_ids)

        self.assertEqual(synthesis["status"], "SUCCESS")
        self.assertEqual(synthesis["papers_analyzed"], 2)
        self.assertIn("methodological_consensus", synthesis)
        self.assertIn("research_gap", synthesis)
        self.assertIn("recommended_methodology", synthesis)
        self.assertIn("curriculum_outcomes", synthesis)
        self.assertTrue(any("CO4" in o for o in synthesis["curriculum_outcomes"]))

    def test_research_hypothesis_generation(self):
        """Validates AI hypothesis formulation and empirical Lab 304 protocol derivation."""
        hyp = self.engine.generate_research_hypothesis(
            domain="Automotive EV Inverters",
            primary_tech="GaN Power Devices with Adaptive Dead-Time Control",
            target_metric="Switching Energy Dissipation",
            created_by="2023MITEC042"
        )
        self.assertEqual(hyp["status"], "SUCCESS")
        self.assertIn("HYP-", hyp["hypothesis_id"])
        self.assertIn("Adaptive Dead-Time", hyp["title"])
        self.assertIn("Switching Energy Dissipation", hyp["novel_hypothesis"])
        self.assertIn("Lab 304", hyp["verification_protocol"])

    def test_institutional_paper_indexing_rbac_barrier(self):
        """Validates that only privileged roles (Admin, Teacher, Research_Lead) can index papers."""
        new_paper = {
            "title": "Sub-Nanosecond Jitter Clock Multiplier for High-Speed SerDes",
            "authors": ["Kumar A.", "Balasubramanian D."],
            "journal": "IEEE Journal of Solid-State Circuits",
            "year": 2024,
            "domain": "Analog & RF IC Design"
        }

        # Student attempt must be forbidden
        unauth_res = self.engine.index_institutional_paper(
            paper_data=new_paper,
            actor_role="Student"
        )
        self.assertEqual(unauth_res["status"], "FORBIDDEN")

        # Privileged Research_Lead attempt must succeed
        auth_res = self.engine.index_institutional_paper(
            paper_data=new_paper,
            actor_role="Research_Lead"
        )
        self.assertEqual(auth_res["status"], "SUCCESS")
        self.assertIn("IEEE-MIT-", auth_res["paper_id"])

    def test_research_page_and_component_exist(self):
        """Ensures Astro hosting page and React island component are in place."""
        page_path = os.path.join(self.base_dir, "src", "pages", "research.astro")
        component_path = os.path.join(self.base_dir, "src", "components", "ResearchDiscoveryHub.jsx")

        self.assertTrue(os.path.isfile(page_path), "src/pages/research.astro must exist")
        self.assertTrue(os.path.isfile(component_path), "src/components/ResearchDiscoveryHub.jsx must exist")

        with open(page_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("ResearchDiscoveryHub", content)
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
            os.path.join(self.base_dir, "src", "pages", "research.astro"),
            os.path.join(self.base_dir, "src", "components", "ResearchDiscoveryHub.jsx"),
            os.path.join(self.base_dir, "backend", "research_discovery_engine.py")
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

