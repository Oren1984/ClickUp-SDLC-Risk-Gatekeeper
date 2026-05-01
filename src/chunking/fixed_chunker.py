from __future__ import annotations

from typing import List

from src.chunking.base_chunker import BaseChunker
from src.core.contracts import Chunk, Document
from src.core.exceptions import ChunkingError


class FixedChunker(BaseChunker):
    """
    Splits text into fixed-size character windows with a configurable overlap.

    Does not attempt to respect natural text boundaries. Useful as a baseline
    comparison strategy against RecursiveChunker in evaluation runs.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100) -> None:
        if chunk_overlap >= chunk_size:
            raise ChunkingError(
                f"chunk_overlap ({chunk_overlap}) must be less than "
                f"chunk_size ({chunk_size})."
            )
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, document: Document) -> List[Chunk]:
        text = (document.text or "").strip()
        if not text:
            return []

        step = self.chunk_size - self.chunk_overlap
        chunks: List[Chunk] = []
        index = 0

        for start in range(0, len(text), step):
            chunk_text = text[start: start + self.chunk_size].strip()
            if not chunk_text:
                continue
            chunks.append(
                self._build_chunk(
                    doc_id=document.doc_id,
                    text=chunk_text,
                    index=index,
                    base_metadata=dict(document.metadata),
                )
            )
            index += 1

        return chunks
