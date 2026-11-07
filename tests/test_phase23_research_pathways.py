"""
========================================================================================
VoltCore Apex Academia - Phase 23 Verification Suite
Cross-Disciplinary Research Hub, Experiment Notebooks & Unified Learning Pathways
----------------------------------------------------------------------------------------
Module: tests/test_phase23_research_pathways.py
Platform Lead & System Architect: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import math
import tempfile
import pytest
from pathlib import Path

from backend.cross_disciplinary_research_engine import (
    ExperimentNotebookEngine,
    CROSS_DISCIPLINARY_PROJECTS,
    get_cross_disciplinary_project,
    list_all_cross_disciplinary_projects
)
from backend.learning_pathway_engine import (
    LearningPathwayEngine,
    ACADEMIC_PATHWAYS,
    CONCEPT_DEPENDENCY_GRAPH,
    learning_pathway_engine
)

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


class TestCrossDisciplinaryExperimentNotebooks:
    """Verifies version-controlled Markdown notebooks, MNA state capture, SPICE export, and oscilloscope tools."""

    @pytest.fixture
    def test_engine(self):
        """Creates an isolated test engine backed by a temporary SQLite database."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_experiment_notebooks.db")
        return ExperimentNotebookEngine(db_path=db_path)

    def test_notebook_creation_and_initial_commit(self, test_engine):
        """Notebook creation must generate valid SHA-256 commit hash and store initial state."""
        nb = test_engine.create_notebook(
            notebook_id="NB-TEST-001",
            project_id="PRJ-IOT-EDGE-01",
            title="High-Speed Bus Termination Protocol",
            author="Ashok Kumar A (2023MITEC042)",
            initial_markdown="# Experiment Setup\nTesting 100MHz FMC bus reflections.",
            mna_state={"nodes": 3, "voltages": [3.3, 1.65, 0.0]},
            spice_netlist="V1 1 0 3.3\nR1 1 2 50\n.end",
            waveform_data={"vpp": 3.3, "freq": 100.0}
        )

        assert nb["notebook_id"] == "NB-TEST-001"
        assert len(nb["commit_hash"]) == 64
        assert nb["total_commits"] == 1

        retrieved = test_engine.get_notebook("NB-TEST-001")
        assert retrieved is not None
        assert retrieved["title"] == "High-Speed Bus Termination Protocol"
        assert retrieved["latest_commit"]["commit_hash"] == nb["commit_hash"]
        assert retrieved["latest_commit"]["mna_state"]["voltages"] == [3.3, 1.65, 0.0]

    def test_notebook_commit_revision_chain(self, test_engine):
        """Committing revisions must build an immutable cryptographic parent-child chain."""
        init_res = test_engine.create_notebook(
            notebook_id="NB-CHAIN-001",
            project_id="PRJ-POWER-DRIVE-03",
            title="GaN Switching Analysis",
            author="Ashok Kumar A (2023MITEC042)",
            initial_markdown="Initial draft."
        )
        h1 = init_res["commit_hash"]

        rev_res = test_engine.commit_revision(
            notebook_id="NB-CHAIN-001",
            author="Ashok Kumar A (2023MITEC042)",
            commit_message="Updated dead-time tuning to 45ns",
            markdown_content="Second revision with 45ns dead-time parameter."
        )
        h2 = rev_res["commit_hash"]

        assert rev_res["parent_hash"] == h1
        assert rev_res["total_commits"] == 2

        history = test_engine.get_commit_history("NB-CHAIN-001")
        assert len(history) == 2
        assert history[0]["commit_hash"] == h1
        assert history[1]["commit_hash"] == h2
        assert history[1]["parent_hash"] == h1

    def test_mna_state_capture_validation(self):
        """MNA state capture must validate dimensions and record matrix parameters."""
        matrix = [[0.05, -0.02], [-0.02, 0.05]]
        currents = [0.1, 0.0]
        voltages = [3.3, 1.65]

        state = ExperimentNotebookEngine.capture_mna_state(
            circuit_name="Resistive_Divider",
            nodes_count=2,
            conductance_matrix=matrix,
            rhs_current_vector=currents,
            solved_voltages=voltages
        )

        assert state["circuit_name"] == "Resistive_Divider"
        assert state["nodes_count"] == 2
        assert state["solved_voltages"] == [3.3, 1.65]

        # Dimension mismatch test
        with pytest.raises(ValueError, match="Matrix dimension mismatch"):
            ExperimentNotebookEngine.capture_mna_state(
                circuit_name="Invalid",
                nodes_count=3,  # Mismatched count
                conductance_matrix=matrix,
                rhs_current_vector=currents,
                solved_voltages=voltages
            )

    def test_spice_netlist_generation(self):
        """SPICE netlist export must format valid syntax with element instances and directives."""
        elements = [
            {"name": "V1", "n1": 1, "n2": 0, "val": "DC 5.0"},
            {"name": "R1", "n1": 1, "n2": 2, "val": "10k"},
            {"name": "C1", "n1": 2, "n2": 0, "val": "100n"},
            {"name": "Q1", "n1": 3, "n2": 2, "n3": 0, "model": "2N2222"}
        ]
        models = [".model 2N2222 NPN(IS=1E-14 BF=200)"]

        deck = ExperimentNotebookEngine.generate_spice_netlist(
            circuit_title="Low-Noise BJT Stage",
            elements=elements,
            analysis_directive=".tran 1u 10m",
            model_cards=models
        )

        assert "* VoltCore Apex Academia - Verified SPICE Netlist Export" in deck
        assert "Circuit Title: Low-Noise BJT Stage" in deck
        assert ".model 2N2222 NPN(IS=1E-14 BF=200)" in deck
        assert "V1 1 0 DC 5.0" in deck
        assert "R1 1 2 10k" in deck
        assert "C1 2 0 100n" in deck
        assert "Q1 3 2 0 2N2222" in deck
        assert ".tran 1u 10m" in deck
        assert ".end" in deck

    def test_oscilloscope_snapshot_metrics(self):
        """Oscilloscope processing must accurately evaluate Vpp, Vrms, and estimated frequency."""
        # Generate 1000 samples of 10 kHz sine wave at 1 MHz sample rate
        fs = 1000000.0  # 1 MHz sample rate (100 samples per cycle)
        f_sig = 10000.0  # 10 kHz
        num_samples = 1000
        time_samples = [i / fs for i in range(num_samples)]
        voltage_samples = [1.65 + 1.65 * math.sin(2 * math.pi * f_sig * t) for t in time_samples]

        metrics = ExperimentNotebookEngine.process_oscilloscope_snapshot(
            channel_name="CH1_CLK",
            sample_rate_hz=fs,
            time_samples=time_samples,
            voltage_samples=voltage_samples
        )

        assert metrics["channel_name"] == "CH1_CLK"
        assert metrics["sample_count"] == 1000
        assert math.isclose(metrics["v_pp"], 3.3, abs_tol=0.05)
        assert math.isclose(metrics["v_avg"], 1.65, abs_tol=0.05)
        # Expected Vrms = sqrt(1.65^2 + (1.65/sqrt(2))^2) ≈ 2.02V
        assert math.isclose(metrics["v_rms"], 2.02, abs_tol=0.05)
        # Frequency should be approximately 10000 Hz
        assert math.isclose(metrics["estimated_frequency_hz"], 10000.0, abs_tol=500.0)

    def test_cross_disciplinary_project_emblem_integration(self):
        """Cross-disciplinary projects must resolve and inherit central subject emblems."""
        projects = list_all_cross_disciplinary_projects()
        assert len(projects) == 5

        prj_ids = {p["project_id"] for p in projects}
        assert prj_ids == {
            "PRJ-IOT-EDGE-01", "PRJ-BIOSIG-DSP-02", "PRJ-POWER-DRIVE-03",
            "PRJ-NEUROMORPH-04", "PRJ-PHASED-RF-05"
        }

        # Inspect Bio-Signal project
        bio = get_cross_disciplinary_project("PRJ-BIOSIG-DSP-02")
        assert bio is not None
        assert bio["short_title"] == "Bio-Signal DSP Processor"
        assert len(bio["disciplines_metadata"]) == 3

        # Check inherited emblem metadata
        disc_names = [d["discipline_name"] for d in bio["disciplines_metadata"]]
        assert "Digital Signal Processing & Algorithms" in disc_names
        assert "Analog Integrated Circuit Design" in disc_names
        assert "Signals & Linear Systems Theory" in disc_names


class TestUnifiedLearningPathwaySynthesis:
    """Verifies 5 academic pathways DAG topological sort, mastery tracking, and remedial dispatching."""

    def test_all_five_pathways_registered(self):
        """All 5 academic pathways must be registered with complete metadata."""
        engine = learning_pathway_engine
        pathways = engine.list_all_pathways()
        assert len(pathways) == 5

        expected_ids = {
            "pathway_semiconductor", "pathway_embedded", "pathway_dsp_telecom",
            "pathway_vlsi", "pathway_ai_hardware"
        }
        assert {p["id"] for p in pathways} == expected_ids

    def test_topological_sort_all_pathways(self):
        """Every pathway DAG must sort topologically without circular dependencies."""
        engine = learning_pathway_engine
        for pid in ACADEMIC_PATHWAYS.keys():
            sorted_nodes = engine.topological_sort_pathway(pid)
            pathway = ACADEMIC_PATHWAYS[pid]
            assert len(sorted_nodes) == len(pathway["nodes"])

            # Verify prerequisite order constraint
            positions = {code: i for i, code in enumerate(sorted_nodes)}
            for n in pathway["nodes"]:
                code = n["code"]
                for p in n.get("prerequisites", []):
                    assert positions[p] < positions[code], (
                        f"In {pid}: prerequisite {p} appears after {code} in sorted order!"
                    )

    def test_student_pathway_mastery_evaluation(self):
        """Student progress evaluation must calculate unlocked nodes and completion percentages."""
        engine = learning_pathway_engine

        # Student has completed only EC23C01 and EC23C02 in semiconductor pathway
        completed = {"EC23C01", "EC23C02"}
        eval_res = engine.evaluate_student_progress("pathway_semiconductor", completed)

        assert eval_res["pathway_id"] == "pathway_semiconductor"
        # 2 out of 4 nodes = 50.0%
        assert eval_res["progress_percentage"] == 50.0
        assert eval_res["attained_credits"] == 7  # 4 + 3 credits
        # EC23C03 requires EC23C02 which is completed -> unlocked
        assert "EC23C03" in eval_res["unlocked_next_nodes"]
        # EC23C05 requires EC23C03 -> locked
        assert "EC23C05" in eval_res["locked_nodes"]

    def test_remedial_micro_lesson_generator(self):
        """Failing scores (<70%) must trigger remedial micro-lessons with root prerequisites."""
        # Test failing score on Elmore Delay in VLSI
        remedial = LearningPathwayEngine.generate_remedial_micro_lesson(
            target_concept="Elmore_Delay",
            telemetry_score=56.4
        )

        assert remedial["status"] == "REMEDIAL_DISPATCHED"
        assert remedial["requires_remediation"] is True
        assert remedial["root_prerequisite"] == "RC_Time_Constants"
        assert remedial["discipline_origin"] == "EC23C01"
        assert remedial["discipline_name"] == "Circuit Analysis & Network Synthesis"
        assert "RC Modeling" in remedial["remedial_title"]
        assert remedial["diagnostic_task"]["question"] is not None

        # Test passing score on same concept
        passing = LearningPathwayEngine.generate_remedial_micro_lesson(
            target_concept="Elmore_Delay",
            telemetry_score=88.5
        )
        assert passing["status"] == "MASTERY_SATISFIED"
        assert passing["requires_remediation"] is False


class TestFrontendResearchAndPathwayIntegration:
    """Verifies that research page and experiment studio components are correctly structured."""

    def test_research_page_structure(self):
        """Research page must include VoltCoreBrandHeader, role badge, breadcrumbs, and studio."""
        page_path = WORKSPACE_ROOT / "src" / "pages" / "research.astro"
        assert page_path.exists()
        content = page_path.read_text(encoding="utf-8")

        assert "VoltCoreBrandHeader" in content
        assert "ROLE: RESEARCH FELLOW / SCHOLAR" in content
        assert "Cross-Disciplinary Research Hub" in content
        assert "ExperimentNotebookStudio" in content
        assert "ResearchDiscoveryHub" in content
        assert "aria-label=\"Breadcrumb\"" in content

    def test_experiment_studio_component_structure(self):
        """ExperimentNotebookStudio must define MNA state, SPICE netlist, and waveform attachments."""
        studio_path = WORKSPACE_ROOT / "src" / "components" / "ExperimentNotebookStudio.jsx"
        assert studio_path.exists()
        content = studio_path.read_text(encoding="utf-8")

        assert "SubjectEmblem" in content
        assert "getSubjectMetadata" in content
        assert "PRJ-IOT-EDGE-01" in content
        assert "PRJ-BIOSIG-DSP-02" in content
        assert "PRJ-POWER-DRIVE-03" in content
        assert "Modified Nodal Analysis (MNA)" in content
        assert "Berkeley SPICE" in content
        assert "Digital Storage Oscilloscope" in content
