from __future__ import annotations

from typing import List

from src.core.contracts import Chunk, Reranker
from src.core.exceptions import RetrievalError


class PassThroughReranker(Reranker):
    """
    Default v1 reranker — returns chunks unchanged.

    Use this when no cross-encoder model is needed (mock mode, CI, testing).
    Preserves the scores and ranks set by the vector store.
    """

    def rerank(self, query: str, chunks: List[Chunk]) -> List[Chunk]:
        return chunks


class CrossEncoderReranker(Reranker):
    """
    Optional cross-encoder reranker backed by sentence-transformers.

    The model is lazy-loaded on the first rerank() call — no download happens
    at construction time. Requires sentence-transformers to be installed.

    Default model: cross-encoder/ms-marco-MiniLM-L-6-v2 (small, fast).
    Scores are raw logits from the cross-encoder; higher = more relevant.
    Chunks are returned in descending score order with updated rank fields.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ) -> None:
        self._model_name = model_name
        self._model = None

    def rerank(self, query: str, chunks: List[Chunk]) -> List[Chunk]:
        if not chunks:
            return chunks
        self._ensure_loaded()
        try:
            pairs = [[query, c.text] for c in chunks]
            scores = self._model.predict(pairs)
        except Exception as exc:
            raise RetrievalError(
                f"Cross-encoder reranking failed for model '{self._model_name}': {exc}"
            ) from exc

        ranked = sorted(
            zip(scores, chunks),
            key=lambda x: float(x[0]),
            reverse=True,
        )
        result: List[Chunk] = []
        for rank, (score, chunk) in enumerate(ranked, start=1):
            chunk.score = float(score)
            chunk.rank = rank
            result.append(chunk)
        return result

    # ------------------------------------------------------------------

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        try:
            from sentence_transformers import CrossEncoder
        except ImportError as exc:
            raise RetrievalError(
                "sentence-transformers is required for CrossEncoderReranker. "
                "Install it with: pip install sentence-transformers"
            ) from exc
        try:
            self._model = CrossEncoder(self._model_name)
        except Exception as exc:
            raise RetrievalError(
                f"Failed to load cross-encoder model '{self._model_name}': {exc}. "
                "Ensure the model name is valid and internet access is available "
                "for the initial download."
            ) from exc
