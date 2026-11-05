"""
========================================================================================
VoltCore Apex Academia - FAISS / NumPy Vector Index Manager
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/faiss_index_manager.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Manages semantic embedding vectors, persistence, and nearest-neighbor search.
  Uses native FAISS (IndexFlatIP) when present, with a vector-accelerated NumPy
  normalized dot-product engine as a zero-dependency fallback.
========================================================================================
"""

import os
import sys
import json
import math
from typing import List, Dict, Any, Tuple, Optional

# Attempt FAISS import, fallback to NumPy
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class VectorIndexManager:
    """
    High-performance vector index manager supporting FAISS and NumPy.
    Provides L2-normalized inner-product search for exact cosine similarity.
    """

    def __init__(self, dimension: int = 384, index_type: str = "FlatIP"):
        self.dimension = dimension
        self.index_type = index_type
        self.metadata: List[Dict[str, Any]] = []
        self.faiss_index = None
        self.numpy_matrix: Optional[Any] = None
        self.is_faiss = HAS_FAISS

        if self.is_faiss:
            # Inner Product index on normalized vectors equals Cosine Similarity
            self.faiss_index = faiss.IndexFlatIP(self.dimension)
        elif HAS_NUMPY:
            self.numpy_matrix = np.empty((0, self.dimension), dtype=np.float32)

    def _normalize_vector(self, vec: Any) -> Any:
        """Normalizes vector to unit length for cosine similarity."""
        if HAS_NUMPY:
            arr = np.asarray(vec, dtype=np.float32)
            norm = np.linalg.norm(arr)
            return arr / (norm + 1e-10) if norm > 0 else arr
        else:
            norm = math.sqrt(sum(x * x for x in vec))
            return [x / (norm + 1e-10) for x in vec] if norm > 0 else vec

    def add_item(self, vector: List[float], meta: Dict[str, Any]) -> int:
        """Adds a single vector and associated curriculum metadata."""
        return self.add_items([vector], [meta])[0]

    def add_items(self, vectors: List[List[float]], meta_list: List[Dict[str, Any]]) -> List[int]:
        """Adds a batch of vectors and metadata to the index."""
        if not vectors or len(vectors) != len(meta_list):
            raise ValueError("Vectors and metadata lists must be non-empty and equal in length.")

        assigned_ids = []
        start_idx = len(self.metadata)

        if HAS_NUMPY:
            norm_vecs = np.array([self._normalize_vector(v) for v in vectors], dtype=np.float32)

            if self.is_faiss and self.faiss_index is not None:
                self.faiss_index.add(norm_vecs)
            else:
                if self.numpy_matrix is None or self.numpy_matrix.shape[0] == 0:
                    self.numpy_matrix = norm_vecs
                else:
                    self.numpy_matrix = np.vstack([self.numpy_matrix, norm_vecs])
        else:
            # Pure Python fallback for environments without numpy
            if not hasattr(self, "_py_vectors"):
                self._py_vectors = []
            for v in vectors:
                self._py_vectors.append(self._normalize_vector(v))

        for idx, m in enumerate(meta_list):
            item_id = start_idx + idx
            entry = dict(m)
            entry["vector_id"] = item_id
            self.metadata.append(entry)
            assigned_ids.append(item_id)

        return assigned_ids

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        Executes nearest neighbor search using cosine similarity.
        Returns list of (metadata, similarity_score) tuples ordered descending.
        """
        if len(self.metadata) == 0:
            return []

        norm_query = self._normalize_vector(query_vector)
        k = min(top_k, len(self.metadata))

        if self.is_faiss and self.faiss_index is not None:
            q_arr = np.array([norm_query], dtype=np.float32)
            distances, indices = self.faiss_index.search(q_arr, k)
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if 0 <= idx < len(self.metadata):
                    results.append((self.metadata[idx], float(dist)))
            return results

        elif HAS_NUMPY and self.numpy_matrix is not None and self.numpy_matrix.shape[0] > 0:
            # Matrix dot-product across all indexed vectors: (N, D) @ (D,) -> (N,)
            scores = np.dot(self.numpy_matrix, norm_query)
            top_indices = np.argsort(scores)[::-1][:k]
            return [(self.metadata[i], float(scores[i])) for i in top_indices]

        else:
            # Pure Python dot product fallback
            scores = []
            for i, v in enumerate(getattr(self, "_py_vectors", [])):
                score = sum(a * b for a, b in zip(v, norm_query))
                scores.append((self.metadata[i], float(score)))
            scores.sort(key=lambda x: x[1], reverse=True)
            return scores[:k]

    def count(self) -> int:
        """Returns total number of indexed vectors."""
        return len(self.metadata)

    def save_index(self, directory_path: str, filename_prefix: str = "voltcore_vector_index") -> Dict[str, str]:
        """Persists vector embeddings and metadata to disk."""
        os.makedirs(directory_path, exist_ok=True)
        meta_file = os.path.join(directory_path, f"{filename_prefix}_meta.json")
        matrix_file = os.path.join(directory_path, f"{filename_prefix}_matrix.npy")

        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump({
                "dimension": self.dimension,
                "count": len(self.metadata),
                "is_faiss": self.is_faiss,
                "metadata": self.metadata
            }, f, indent=2)

        if HAS_NUMPY and self.numpy_matrix is not None:
            np.save(matrix_file, self.numpy_matrix)

        return {"meta_file": meta_file, "matrix_file": matrix_file}

    def load_index(self, directory_path: str, filename_prefix: str = "voltcore_vector_index") -> bool:
        """Loads vector embeddings and metadata from disk."""
        meta_file = os.path.join(directory_path, f"{filename_prefix}_meta.json")
        matrix_file = os.path.join(directory_path, f"{filename_prefix}_matrix.npy")

        if not os.path.exists(meta_file):
            return False

        with open(meta_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.dimension = data.get("dimension", self.dimension)
        self.metadata = data.get("metadata", [])

        if HAS_NUMPY and os.path.exists(matrix_file):
            self.numpy_matrix = np.load(matrix_file)
            if self.is_faiss:
                self.faiss_index = faiss.IndexFlatIP(self.dimension)
                self.faiss_index.add(self.numpy_matrix)
        return True

