from __future__ import annotations

from typing import List

from src.chunking.base_chunker import BaseChunker
from src.core.contracts import Chunk, Document
from src.core.exceptions import ChunkingError

# Separators tried in order from coarsest to finest.
_SEPARATORS: List[str] = ["\n\n", "\n", ". ", "! ", "? ", " "]


class RecursiveChunker(BaseChunker):
    """
    Splits text by progressively finer natural boundaries (paragraph → line
    → sentence → word), then merges small pieces into chunks of ~chunk_size
    characters with chunk_overlap overlap.

    Preserves natural text structure better than FixedChunker at the cost of
    slightly variable chunk lengths.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100) -> None:
        if chunk_overlap >= chunk_size:
            raise ChunkingError(
                f"chunk_overlap ({chunk_overlap}) must be less than "
                f"chunk_size ({chunk_size})."
            )
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    # ------------------------------------------------------------------

    def chunk(self, document: Document) -> List[Chunk]:
        text = (document.text or "").strip()
        if not text:
            return []

        pieces = self._split_recursive(text, _SEPARATORS)
        merged = self._merge_pieces(pieces)

        return [
            self._build_chunk(
                doc_id=document.doc_id,
                text=chunk_text,
                index=i,
                base_metadata=dict(document.metadata),
            )
            for i, chunk_text in enumerate(merged)
            if chunk_text.strip()
        ]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _split_recursive(self, text: str, separators: List[str]) -> List[str]:
        """
        Recursively split text so every piece is <= chunk_size characters.
        Tries each separator in order; falls back to character-level cutting.
        """
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        if not separators:
            # Hard character-level cut as last resort
            step = max(1, self.chunk_size - self.chunk_overlap)
            return [
                text[i: i + self.chunk_size]
                for i in range(0, len(text), step)
                if text[i: i + self.chunk_size].strip()
            ]

        sep, rest = separators[0], separators[1:]
        parts = [p for p in text.split(sep) if p.strip()]

        if len(parts) <= 1:
            # This separator produced no useful split; try finer
            return self._split_recursive(text, rest)

        result: List[str] = []
        for part in parts:
            if len(part) <= self.chunk_size:
                result.append(part.strip())
            else:
                result.extend(self._split_recursive(part, rest))

        return [p for p in result if p]

    def _merge_pieces(self, pieces: List[str]) -> List[str]:
        """
        Greedily accumulate pieces into chunks of ~chunk_size characters.
        Carries over the tail of each chunk as overlap for the next one.
        """
        if not pieces:
            return []

        chunks: List[str] = []
        buf: List[str] = []
        buf_len: int = 0

        for piece in pieces:
            plen = len(piece)
            sep_cost = 1 if buf else 0

            if buf and buf_len + sep_cost + plen > self.chunk_size:
                # Flush current buffer as a chunk
                chunks.append(" ".join(buf))

                # Carry over tail pieces whose combined length <= chunk_overlap
                tail: List[str] = []
                tail_len: int = 0
                for p in reversed(buf):
                    addition = len(p) + (1 if tail else 0)
                    if tail_len + addition <= self.chunk_overlap:
                        tail.insert(0, p)
                        tail_len += addition
                    else:
                        break

                buf = tail
                buf_len = tail_len

            buf.append(piece)
            buf_len += plen + (1 if len(buf) > 1 else 0)

        if buf:
            chunks.append(" ".join(buf))

        return [c.strip() for c in chunks if c.strip()]
