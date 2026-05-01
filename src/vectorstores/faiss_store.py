from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import numpy as np

from src.core.contracts import Chunk
from src.core.exceptions import VectorStoreError
from src.vectorstores.base_vector_store import BaseVectorStore

_DEFAULT_PERSIST_DIR = os.path.join("vector_db", "faiss")
_INDEX_FILENAME = "index.faiss"
_META_FILENAME = "metadata.json"


class FaissVectorStore(BaseVectorStore):
    """
    Vector store backed by FAISS (faiss-cpu) with an in-memory metadata sidecar.

    Uses IndexFlatIP (inner product), which equals cosine similarity for
    L2-normalised vectors. Search results are sorted by decreasing inner product
    (highest score = most similar). Scores are in the range [-1.0, 1.0] for
    unit-norm vectors.

    The metadata sidecar is a list indexed by FAISS internal integer position.
    It preserves chunk_id, doc_id, text, and metadata for every stored chunk.
    Both the FAISS index and the sidecar can be persisted to disk via persist().
    """

    def __init__(self, persist_directory: str = _DEFAULT_PERSIST_DIR) -> None:
        self._persist_directory = persist_directory
        self._index = None  # faiss.IndexFlatIP — created lazily on first add
        self._dimension: Optional[int] = None
        self._sidecar: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # VectorStore interface
    # ------------------------------------------------------------------

    def add(self, chunks: List[Chunk]) -> None:
        if not chunks:
            return
        self._require_embeddings(chunks)
        dim = len(chunks[0].embedding)
        self._ensure_index(dim)
        if dim != self._dimension:
            raise VectorStoreError(
                f"Embedding dimension mismatch: index expects {self._dimension} dims, "
                f"chunks have {dim} dims."
            )
        try:
            vectors = np.array([c.embedding for c in chunks], dtype=np.float32)
            self._index.add(vectors)
        except Exception as exc:
            raise VectorStoreError(f"FAISS add failed: {exc}") from exc
        for chunk in chunks:
            self._sidecar.append({
                "chunk_id": chunk.chunk_id,
                "doc_id": chunk.doc_id,
                "text": chunk.text,
                "metadata": chunk.metadata,
            })

    def search(self, query_embedding: List[float], top_k: int) -> List[Chunk]:
        if self._index is None or self._index.ntotal == 0:
            return []
        n = min(top_k, self._index.ntotal)
        try:
            query = np.array([query_embedding], dtype=np.float32)
            distances, indices = self._index.search(query, n)
        except Exception as exc:
            raise VectorStoreError(f"FAISS search failed: {exc}") from exc

        chunks: List[Chunk] = []
        for rank, (dist, idx) in enumerate(
            zip(distances[0].tolist(), indices[0].tolist()), start=1
        ):
            if idx == -1:  # FAISS sentinel for missing results
                continue
            entry = self._sidecar[idx]
            chunks.append(
                Chunk(
                    chunk_id=entry["chunk_id"],
                    doc_id=entry["doc_id"],
                    text=entry["text"],
                    metadata=dict(entry["metadata"]),
                    score=float(dist),
                    rank=rank,
                )
            )
        return chunks

    def persist(self) -> None:
        if self._index is None:
            return
        faiss = self._import_faiss()
        os.makedirs(self._persist_directory, exist_ok=True)
        index_path = os.path.join(self._persist_directory, _INDEX_FILENAME)
        meta_path = os.path.join(self._persist_directory, _META_FILENAME)
        try:
            faiss.write_index(self._index, index_path)
        except Exception as exc:
            raise VectorStoreError(f"Failed to write FAISS index to '{index_path}': {exc}") from exc
        try:
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(self._sidecar, f, ensure_ascii=False)
        except Exception as exc:
            raise VectorStoreError(
                f"Failed to write FAISS metadata sidecar to '{meta_path}': {exc}"
            ) from exc

    def load(self) -> None:
        faiss = self._import_faiss()
        index_path = os.path.join(self._persist_directory, _INDEX_FILENAME)
        meta_path = os.path.join(self._persist_directory, _META_FILENAME)
        if not os.path.exists(index_path):
            return  # Nothing persisted yet; remain empty
        try:
            self._index = faiss.read_index(index_path)
            self._dimension = self._index.d
        except Exception as exc:
            raise VectorStoreError(
                f"Failed to read FAISS index from '{index_path}': {exc}"
            ) from exc
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    self._sidecar = json.load(f)
            except Exception as exc:
                raise VectorStoreError(
                    f"Failed to read FAISS metadata sidecar from '{meta_path}': {exc}"
                ) from exc

    def clear(self) -> None:
        if self._index is not None:
            self._index.reset()
        self._sidecar = []

    @property
    def store_name(self) -> str:
        return "faiss"

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    @staticmethod
    def _import_faiss():
        try:
            import faiss
            return faiss
        except ImportError as exc:
            raise VectorStoreError(
                "faiss-cpu package is required for FaissVectorStore. "
                "Install it with: pip install faiss-cpu"
            ) from exc

    def _ensure_index(self, dim: int) -> None:
        if self._index is not None:
            return
        faiss = self._import_faiss()
        self._dimension = dim
        self._index = faiss.IndexFlatIP(dim)
