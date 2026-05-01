from __future__ import annotations

from typing import Dict, List, Optional

from src.core.contracts import Chunk, Chunker, EmbeddingProvider, Reranker, VectorStore
from src.core.exceptions import RetrievalError
from src.ingestion.document_loader import load_document
from src.ingestion.text_cleaner import clean_text
from src.observability.metrics import METRICS
from src.observability.tracing import timer
from src.retrieval.retriever import Retriever


class RAGPipeline:
    """
    Thin orchestrator that wires ingestion, chunking, embedding, storage, and
    retrieval into a single coherent pipeline.

    All provider/store/chunker instances are owned by the pipeline. The same
    EmbeddingProvider instance is used for both build_index() and query(),
    guaranteeing embedding-space consistency.

    This class does not implement evaluation, Streamlit UI, or document
    management beyond the single build_index/query/clear lifecycle.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        chunker: Chunker,
        reranker: Optional[Reranker] = None,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._chunker = chunker
        self._retriever = Retriever(embedding_provider, vector_store, reranker)
        self._index_built: bool = False

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def build_index(self, file_path: str, redact_pii: bool = False) -> Dict:
        """
        Ingest a single document, chunk it, embed the chunks, and add them to
        the vector store.

        Returns a summary dict:
            doc_id, source, chunks_created, embedding_provider, vector_store

        Raises IngestionError, ChunkingError, EmbeddingError, or VectorStoreError
        on failure. Errors are recorded in METRICS before re-raising.
        """
        try:
            document = load_document(file_path)

            cleaned = clean_text(document.text, redact_pii=redact_pii)
            document.text = cleaned

            chunks = self._chunker.chunk(document)

            if chunks:
                texts = [c.text for c in chunks]
                with timer() as t_embed:
                    embeddings = self._embedding_provider.embed(texts)
                for chunk, embedding in zip(chunks, embeddings):
                    chunk.embedding = embedding

                self._vector_store.add(chunks)
                METRICS.embedding_latency_seconds = t_embed["elapsed"]

            METRICS.documents_loaded_total += 1
            METRICS.chunks_created_total += len(chunks)
            METRICS.selected_embedding_provider = self._embedding_provider.provider_name
            METRICS.selected_vector_store = self._vector_store.store_name
            self._index_built = True

            return {
                "doc_id": document.doc_id,
                "source": document.source,
                "chunks_created": len(chunks),
                "embedding_provider": self._embedding_provider.provider_name,
                "vector_store": self._vector_store.store_name,
            }

        except Exception as exc:
            METRICS.record_error(str(exc))
            raise

    def query(self, query_text: str, top_k: int) -> List[Chunk]:
        """
        Retrieve the top_k most relevant chunks for query_text.

        Raises RetrievalError if build_index() has not been called yet.
        Raises ValidationError if query_text or top_k are invalid.
        """
        if not self._index_built:
            raise RetrievalError(
                "No index has been built. Call build_index() before querying. "
                "To use a pre-existing vector store, call mark_ready() first."
            )
        try:
            with timer() as t_retrieval:
                chunks = self._retriever.query(query_text, top_k)
            METRICS.query_count_total += 1
            METRICS.retrieval_latency_seconds = t_retrieval["elapsed"]
            return chunks
        except RetrievalError:
            raise
        except Exception as exc:
            METRICS.record_error(str(exc))
            raise RetrievalError(f"Query failed: {exc}") from exc

    def clear(self) -> None:
        """Remove all stored vectors and reset pipeline state."""
        self._vector_store.clear()
        self._index_built = False

    def mark_ready(self) -> None:
        """
        Mark the pipeline as ready to query without calling build_index().

        Use this when the vector store was pre-loaded from disk (e.g. via
        vector_store.load()) before the pipeline was constructed.
        """
        self._index_built = True
