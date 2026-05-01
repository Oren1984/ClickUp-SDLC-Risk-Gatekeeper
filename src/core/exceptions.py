from __future__ import annotations


class RAGLabError(Exception):
    """Base exception for all RAG Retrieval Evaluation Lab errors."""


class ConfigurationError(RAGLabError):
    """Raised when configuration is missing, invalid, or incompatible."""


class ValidationError(RAGLabError):
    """Raised when user input fails validation (files, queries, parameters)."""


class IngestionError(RAGLabError):
    """Raised when document loading or parsing fails."""


class ChunkingError(RAGLabError):
    """Raised when text chunking fails."""


class EmbeddingError(RAGLabError):
    """Raised when embedding generation fails (e.g. API error, model load failure)."""


class VectorStoreError(RAGLabError):
    """Raised when a vector store operation fails (add, search, persist, load)."""


class RetrievalError(RAGLabError):
    """Raised when the retrieval pipeline fails."""


class EvaluationError(RAGLabError):
    """Raised when evaluation fails (e.g. malformed ground truth, metric error)."""
