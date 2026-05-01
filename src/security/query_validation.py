from __future__ import annotations

from src.core.exceptions import ValidationError

_MAX_QUERY_LENGTH = 2000


def validate_query(query: str) -> str:
    """Validate and strip a user query. Raises ValidationError if invalid."""
    if not query or not query.strip():
        raise ValidationError("Query must not be empty.")

    query = query.strip()

    if len(query) > _MAX_QUERY_LENGTH:
        raise ValidationError(
            f"Query length {len(query)} exceeds the maximum of {_MAX_QUERY_LENGTH} characters."
        )

    return query


def validate_top_k(top_k: int) -> int:
    """Validate top_k is within the allowed range [1, 20]."""
    if not isinstance(top_k, int) or not (1 <= top_k <= 20):
        raise ValidationError("top_k must be an integer between 1 and 20.")
    return top_k


def validate_chunk_size(chunk_size: int) -> int:
    """Validate chunk_size is within the allowed range [200, 1500]."""
    if not isinstance(chunk_size, int) or not (200 <= chunk_size <= 1500):
        raise ValidationError("chunk_size must be an integer between 200 and 1500.")
    return chunk_size


def validate_chunk_overlap(chunk_overlap: int, chunk_size: int) -> int:
    """Validate chunk_overlap is within range and strictly less than chunk_size."""
    if not isinstance(chunk_overlap, int) or not (0 <= chunk_overlap <= 300):
        raise ValidationError("chunk_overlap must be an integer between 0 and 300.")
    if chunk_overlap >= chunk_size:
        raise ValidationError(
            f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})."
        )
    return chunk_overlap


def validate_retrieval_params(
    query: str,
    top_k: int,
    chunk_size: int,
    chunk_overlap: int,
) -> tuple[str, int, int, int]:
    """
    Validate all retrieval parameters together.
    Returns the validated (query, top_k, chunk_size, chunk_overlap) tuple.
    """
    query = validate_query(query)
    top_k = validate_top_k(top_k)
    chunk_size = validate_chunk_size(chunk_size)
    chunk_overlap = validate_chunk_overlap(chunk_overlap, chunk_size)
    return query, top_k, chunk_size, chunk_overlap
