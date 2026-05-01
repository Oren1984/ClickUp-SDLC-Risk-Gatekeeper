from __future__ import annotations

import os
import re
from pathlib import Path

from src.core.exceptions import ValidationError

ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".pdf", ".txt", ".md", ".html", ".htm"})
_MAX_FILENAME_LENGTH = 200
_SAFE_CHARS = re.compile(r"[^\w\s\-.]")
_MULTI_SEPARATORS = re.compile(r"[\s_]+")


def validate_file(filename: str, file_size_bytes: int, max_upload_mb: int = 10) -> str:
    """
    Validate an uploaded file by name and size.

    Returns the sanitized filename on success.
    Raises ValidationError on any violation.
    """
    if not filename or not filename.strip():
        raise ValidationError("Filename must not be empty.")

    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValidationError(
            f"File type '{suffix}' is not allowed. Allowed types: {allowed}"
        )

    max_bytes = max_upload_mb * 1024 * 1024
    if file_size_bytes > max_bytes:
        size_mb = file_size_bytes / (1024 * 1024)
        raise ValidationError(
            f"File size {size_mb:.1f} MB exceeds the {max_upload_mb} MB upload limit."
        )

    return _sanitize_filename(filename)


def _sanitize_filename(filename: str) -> str:
    """
    Remove directory traversal, null bytes, and unsafe characters.
    Returns a safe filename suitable for storage under data/raw/.
    """
    # Strip any directory component — prevent path traversal
    name = os.path.basename(filename)

    # Remove null bytes
    name = name.replace("\x00", "")

    stem = Path(name).stem
    suffix = Path(name).suffix.lower()

    # Replace unsafe characters with underscores
    stem = _SAFE_CHARS.sub("_", stem)

    # Collapse repeated whitespace/underscores
    stem = _MULTI_SEPARATORS.sub("_", stem).strip("_")

    if not stem:
        raise ValidationError("Filename is empty after sanitization.")

    # Enforce max total length while preserving extension
    max_stem = _MAX_FILENAME_LENGTH - len(suffix)
    if len(stem) > max_stem:
        stem = stem[:max_stem]

    return stem + suffix
