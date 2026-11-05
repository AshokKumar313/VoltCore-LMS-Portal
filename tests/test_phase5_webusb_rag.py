"""
========================================================================================
VoltCore Apex Academia - Phase 5 Automated Test Suite
WebUSB Flashing, Dense Vector RAG Semantic Engine & Cloud Staging Blueprint Verification
----------------------------------------------------------------------------------------
Module: tests/test_phase5_webusb_rag.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import sys
import json
import math
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.faiss_index_manager import VectorIndexManager
from backend.vector_rag_engine import (
    VectorRagEngine,
    compute_deterministic_embedding,
    vector_rag_engine,
    EMBEDDING_DIM
)
from backend.security_auth import (
    PUBLIC_CONTACT_METADATA,
    SECURE_ADMIN_EMAIL,
    SECURE_ADMIN_PHONE
)


class TestVectorIndexManager(unittest.TestCase):
    """Verifies vector indexing, normalization, and nearest-neighbor search accuracy."""

    def setUp(self):
        self.manager = VectorIndexManager(dimension=16)

    def test_vector_normalization_and_addition(self):
        v1 = [1.0] * 16
        meta = {"title": "Test Vector 1", "module": "EC8701"}
        idx = self.manager.add_item(v1, meta)
        self.assertEqual(idx, 0)
        self.assertEqual(self.manager.count(), 1)

    def test_cosine_similarity_ordering(self):
        # Create distinct test vectors
        v_base = [1.0, 0.0] + [0.0] * 14
        v_similar = [0.9, 0.1] + [0.0] * 14
        v_orthogonal = [0.0, 1.0] + [0.0] * 14

        self.manager.add_items(
            [v_base, v_similar, v_orthogonal],
            [{"name": "Base"}, {"name": "Similar"}, {"name": "Orthogonal"}]
        )

        results = self.manager.search(v_base, top_k=3)
        self.assertEqual(len(results), 3)

        # First result must be Base itself (cosine similarity ~1.0)
        self.assertEqual(results[0][0]["name"], "Base")
        self.assertAlmostEqual(results[0][1], 1.0, places=3)

        # Second result must be Similar
        self.assertEqual(results[1][0]["name"], "Similar")
        self.assertGreater(results[1][1], 0.8)

        # Third result must be Orthogonal (cosine similarity ~0.0)
        self.assertEqual(results[2][0]["name"], "Orthogonal")
        self.assertAlmostEqual(results[2][1], 0.0, places=3)

    def test_save_and_load_vector_index(self):
        tmp_dir = os.path.join(PROJECT_ROOT, "backend", "cache")
        v = [0.5] * 16
        self.manager.add_item(v, {"name": "Persisted Document"})

        save_paths = self.manager.save_index(tmp_dir, filename_prefix="test_idx")
        self.assertTrue(os.path.exists(save_paths["meta_file"]))

        new_manager = VectorIndexManager(dimension=16)
        loaded = new_manager.load_index(tmp_dir, filename_prefix="test_idx")
        self.assertTrue(loaded)
        self.assertEqual(new_manager.count(), 1)
        self.assertEqual(new_manager.metadata[0]["name"], "Persisted Document")

        # Cleanup test files
        for p in save_paths.values():
            if os.path.exists(p):
                os.remove(p)


class TestVectorRagEngine(unittest.TestCase):
    """Verifies dense vector curriculum indexing and semantic retrieval."""

    def test_deterministic_embedding_dimension_and_norm(self):
        vec = compute_deterministic_embedding("ARM Cortex-M DMA zero-copy circular buffer", dim=EMBEDDING_DIM)
        self.assertEqual(len(vec), EMBEDDING_DIM)

        norm = math.sqrt(sum(x * x for x in vec))
        self.assertAlmostEqual(norm, 1.0, places=4)

    def test_semantic_cluster_similarity(self):
        vec_dma1 = compute_deterministic_embedding("STM32 Cortex-M DMA memory barrier")
        vec_dma2 = compute_deterministic_embedding("Direct Memory Access circular buffer")
        vec_riscv = compute_deterministic_embedding("5-stage pipelined RV32I hazard forwarding")

        # Cosine similarity between dma1 and dma2
        sim_dma = sum(a * b for a, b in zip(vec_dma1, vec_dma2))
        sim_cross = sum(a * b for a, b in zip(vec_dma1, vec_riscv))

        # DMA concepts must be more similar to each other than to RISC-V pipeline
        self.assertGreater(sim_dma, sim_cross)

    def test_curriculum_indexing_and_search(self):
        engine = VectorRagEngine(dimension=EMBEDDING_DIM)
        count = engine.index_curriculum_documents()
        self.assertGreater(count, 10, "Curriculum documents and NPTEL mapper must be indexed")

        # Test search for DMA
        results = engine.semantic_search("ARM Cortex-M DMA circular ping-pong buffer", top_k=3)
        self.assertGreater(len(results), 0)
        top = results[0]
        self.assertIn("module_code", top)
        self.assertGreater(top["similarity_score"], 0.2)

        # Test query_curriculum_tutor interface
        resp = engine.query_curriculum_tutor("RISC-V hazard forwarding and stall units")
        self.assertEqual(resp["status"], "success")
        self.assertIn("answer", resp)
        self.assertIn("citations", resp)


class TestWebUsbFlashingPanelAndPage(unittest.TestCase):
    """Verifies WebUSB / WebSerial flashing component and hosting page."""

    def test_webusb_component_exists_and_features(self):
        comp_path = os.path.join(PROJECT_ROOT, "src", "components", "WebUsbFlashingPanel.jsx")
        self.assertTrue(os.path.exists(comp_path), "WebUsbFlashingPanel.jsx must exist")

        with open(comp_path, "r", encoding="utf-8") as f:
            code = f.read()

        # WebSerial API references
        self.assertIn("navigator.serial", code)
        self.assertIn("requestPort", code)
        self.assertIn("setSignals", code)

        # DTR / RTS bootloader pulsing
        self.assertIn("dataTerminalReady", code)
        self.assertIn("requestToSend", code)
        self.assertIn("pulseEsp32Bootloader", code)

        # Hardware Boards and offsets
        self.assertIn("esp32_wroom", code)
        self.assertIn("stm32_cortex_m4", code)
        self.assertIn("0x1000", code)
        self.assertIn("0x10000", code)

        # Serial monitor
        self.assertIn("serialLogs", code)
        self.assertIn("handleSendSerialCommand", code)

    def test_flash_firmware_page_exists(self):
        page_path = os.path.join(PROJECT_ROOT, "src", "pages", "flash-firmware.astro")
        self.assertTrue(os.path.exists(page_path), "flash-firmware.astro must exist")

        with open(page_path, "r", encoding="utf-8") as f:
            code = f.read()

        self.assertIn("WebUsbFlashingPanel", code)
        self.assertIn("client:load", code)


class TestCloudDeploymentBlueprint(unittest.TestCase):
    """Verifies cloud staging blueprints and environment variables schemas."""

    def test_render_yaml_validity(self):
        render_path = os.path.join(PROJECT_ROOT, "deploy", "render.yaml")
        self.assertTrue(os.path.exists(render_path), "deploy/render.yaml must exist")

        with open(render_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("type: web", content)
        self.assertIn("name: voltcore-apex-api", content)
        self.assertIn("healthCheckPath: /api/health", content)
        self.assertIn("singapore", content)
        self.assertIn("LMS_DB_PATH", content)
        self.assertIn("SECURE_ADMIN_EMAIL", content)
        self.assertIn("SECURE_ADMIN_PHONE", content)

    def test_cloud_deployment_config_json_schema(self):
        config_path = os.path.join(PROJECT_ROOT, "cloud_deployment_config.json")
        self.assertTrue(os.path.exists(config_path), "cloud_deployment_config.json must exist")

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("project", data)
        self.assertEqual(data["project"]["lead_architect"], "Ashok Kumar A")
        self.assertIn("cloud_targets", data)
        self.assertIn("render", data["cloud_targets"])
        self.assertIn("railway", data["cloud_targets"])
        self.assertIn("fly_io", data["cloud_targets"])
        self.assertIn("local_docker_desktop", data["cloud_targets"])
        self.assertIn("privacy_and_security_policy", data)
        self.assertEqual(data["privacy_and_security_policy"]["public_contact"]["email"], PUBLIC_CONTACT_METADATA["public_email"])


if __name__ == "__main__":
    unittest.main()

