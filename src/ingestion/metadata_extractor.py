from __future__ import annotations

from pathlib import Path
from typing import Optional


def generate_doc_id(file_path: str) -> str:
    """
    Derive a deterministic, human-readable doc_id from a file path.

    Uses the filename stem (no extension), lowercased, spaces replaced
    with underscores. Example: 'My Document.pdf' → 'my_document'.
    """
    return Path(file_path).stem.lower().replace(" ", "_")


def build_document_metadata(
    file_path: str,
    doc_id: str,
    page_number: Optional[int] = None,
    extra: Optional[dict] = None,
) -> dict:
    """
    Build the standard metadata dict for a Document DTO.

    Chunk-specific fields (chunk_index, chunk_id) are added later by the
    chunker and should not be set here.
    """
    path = Path(file_path)
    meta: dict = {
        "file_name": path.name,
        "source": str(path.resolve()),
        "file_type": path.suffix.lower(),
        "doc_id": doc_id,
    }
    if page_number is not None:
        meta["page_number"] = page_number
    if extra:
        meta.update(extra)
    return meta
