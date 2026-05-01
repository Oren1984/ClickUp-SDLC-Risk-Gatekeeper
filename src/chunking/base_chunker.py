from __future__ import annotations

from src.core.contracts import Chunk, Chunker, Document

# Re-export so downstream code can import Chunker from either location.
__all__ = ["BaseChunker", "Chunker"]


class BaseChunker(Chunker):
    """
    Abstract base that adds shared utilities on top of the Chunker contract.

    Concrete implementations (RecursiveChunker, FixedChunker) inherit from
    here. Do not instantiate BaseChunker directly.
    """

    def _make_chunk_id(self, doc_id: str, index: int) -> str:
        """Return a deterministic chunk_id: '{doc_id}_chunk_{index:04d}'."""
        return f"{doc_id}_chunk_{index:04d}"

    def _build_chunk(
        self,
        doc_id: str,
        text: str,
        index: int,
        base_metadata: dict,
    ) -> Chunk:
        """Construct a Chunk with all required fields set to safe defaults."""
        return Chunk(
            chunk_id=self._make_chunk_id(doc_id, index),
            doc_id=doc_id,
            text=text,
            metadata={**base_metadata, "chunk_index": index},
            embedding=None,
            score=None,
            rank=None,
        )
