from __future__ import annotations

from typing import List

from src.core.contracts import Chunk, VectorStore
from src.core.exceptions import VectorStoreError


class BaseVectorStore(VectorStore):
    """
    Thin base class for VectorStore implementations.

    Provides shared validation helpers. All abstract methods from VectorStore
    must still be implemented by concrete subclasses.
    """

    def _require_embeddings(self, chunks: List[Chunk]) -> None:
        """Raise VectorStoreError if any chunk is missing its embedding."""
        missing = [c.chunk_id for c in chunks if c.embedding is None]
        if not missing:
            return
        preview = missing[:5]
        suffix = " (and more)" if len(missing) > 5 else ""
        raise VectorStoreError(
            f"All chunks must have embeddings before being added to the store. "
            f"Missing embeddings for: {preview}{suffix}"
        )
