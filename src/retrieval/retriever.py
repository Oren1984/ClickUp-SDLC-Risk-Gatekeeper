from __future__ import annotations

from typing import List, Optional

from src.core.contracts import Chunk, EmbeddingProvider, Reranker, VectorStore
from src.core.exceptions import RetrievalError
from src.security.query_validation import validate_query, validate_top_k


class Retriever:
    """
    Dense retrieval component.

    Receives a pre-built EmbeddingProvider and VectorStore and uses them to
    answer queries. The same EmbeddingProvider instance that was used to build
    the index must be passed here to guarantee embedding compatibility.

    An optional Reranker is applied after vector search when provided.
    This class never loads documents, never chunks text, and never creates
    embeddings for stored chunks — those responsibilities belong to the pipeline.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        reranker: Optional[Reranker] = None,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._reranker = reranker

    # ------------------------------------------------------------------

    def query(self, query_text: str, top_k: int) -> List[Chunk]:
        """
        Embed query_text and return the top_k most similar chunks.

        Raises ValidationError if query_text or top_k are invalid.
        Raises RetrievalError if vector search or reranking fails.
        """
        query_text = validate_query(query_text)
        top_k = validate_top_k(top_k)

        try:
            query_embedding = self._embedding_provider.embed([query_text])[0]
        except Exception as exc:
            raise RetrievalError(
                f"Failed to embed query: {exc}"
            ) from exc

        try:
            chunks = self._vector_store.search(query_embedding, top_k)
        except Exception as exc:
            raise RetrievalError(
                f"Vector store search failed: {exc}"
            ) from exc

        if self._reranker and chunks:
            try:
                chunks = self._reranker.rerank(query_text, chunks)
            except Exception as exc:
                raise RetrievalError(
                    f"Reranking failed: {exc}"
                ) from exc

        return chunks
