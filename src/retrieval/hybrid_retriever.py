from __future__ import annotations

from typing import List

from src.core.contracts import Chunk
from src.core.exceptions import RetrievalError


class HybridRetriever:
    """
    Planned hybrid dense + sparse retriever (v1 stub — not yet implemented).

    A future version will combine dense vector search with BM25 keyword search
    and merge the ranked result lists (e.g. Reciprocal Rank Fusion).

    This stub exists to establish the module boundary and raise a clear error
    if called prematurely. No external dependencies (rank-bm25, etc.) are added.

    To perform retrieval now, use Retriever with a ChromaVectorStore or
    FaissVectorStore.
    """

    def query(self, query_text: str, top_k: int) -> List[Chunk]:
        raise RetrievalError(
            "Hybrid retrieval is planned for a future version. "
            "Use Retriever with a vector store for dense retrieval."
        )
