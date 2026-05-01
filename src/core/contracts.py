from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Shared Data Transfer Objects
# ---------------------------------------------------------------------------


@dataclass
class Document:
    """Represents a loaded source document before chunking."""

    doc_id: str
    text: str
    source: str
    file_type: str
    page_number: Optional[int] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class Chunk:
    """
    Represents a single text chunk derived from a Document.

    Serves as the unit of storage, retrieval, and evaluation throughout
    the pipeline. Fields score and rank are populated by the retrieval layer.
    """

    chunk_id: str
    doc_id: str
    text: str
    metadata: dict = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    score: Optional[float] = None
    rank: Optional[int] = None


@dataclass
class EvaluationQuestion:
    """A single ground-truth entry used during evaluation."""

    question: str
    expected_answer: str
    relevant_doc_id: str


# ---------------------------------------------------------------------------
# Abstract Provider Interfaces
# ---------------------------------------------------------------------------


class EmbeddingProvider(ABC):
    """Common interface for all embedding providers."""

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts and return one vector per text."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier (e.g. 'mock', 'huggingface')."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Dimensionality of the embedding vectors produced by this provider."""


class VectorStore(ABC):
    """
    Common interface for vector store implementations.

    All methods operate on Chunk objects so that text and metadata are
    preserved alongside embeddings regardless of the underlying store.
    FAISS implementations must maintain an internal metadata sidecar.
    """

    @abstractmethod
    def add(self, chunks: List[Chunk]) -> None:
        """Add chunks (with embeddings already set) to the store."""

    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int) -> List[Chunk]:
        """Return the top_k most similar chunks for the given query embedding."""

    @abstractmethod
    def persist(self) -> None:
        """Persist the index and metadata to disk."""

    @abstractmethod
    def load(self) -> None:
        """Load a previously persisted index and metadata from disk."""

    @abstractmethod
    def clear(self) -> None:
        """Remove all stored vectors and metadata."""

    @property
    @abstractmethod
    def store_name(self) -> str:
        """Human-readable store identifier (e.g. 'chroma', 'faiss')."""


class Chunker(ABC):
    """Common interface for text chunking strategies."""

    @abstractmethod
    def chunk(self, document: Document) -> List[Chunk]:
        """Split a Document into a list of Chunks."""


class Reranker(ABC):
    """Optional interface for cross-encoder re-ranking."""

    @abstractmethod
    def rerank(self, query: str, chunks: List[Chunk]) -> List[Chunk]:
        """
        Re-rank retrieved chunks by relevance to the query.
        Returns chunks in descending relevance order with updated rank fields.
        """
