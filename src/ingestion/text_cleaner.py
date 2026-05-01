from __future__ import annotations

import re

_MULTI_SPACES = re.compile(r"[ \t]+")
_MULTI_NEWLINES = re.compile(r"\n{3,}")

_MIN_CONTENT_LENGTH = 3


def clean_text(text: str, redact_pii: bool = False) -> str:
    """
    Normalize text for downstream chunking.

    - Collapses multiple spaces and tabs to a single space.
    - Reduces 3+ consecutive newlines to 2 (preserves paragraph structure).
    - Strips leading/trailing whitespace.
    - Returns empty string for content shorter than _MIN_CONTENT_LENGTH.
    - Optionally applies PII redaction when redact_pii=True.
    """
    if not text or not text.strip():
        return ""

    text = _MULTI_SPACES.sub(" ", text)
    # Strip per-line leading/trailing spaces (spaces adjacent to newlines)
    text = "\n".join(line.strip() for line in text.split("\n"))
    text = _MULTI_NEWLINES.sub("\n\n", text)
    text = text.strip()

    if len(text) < _MIN_CONTENT_LENGTH:
        return ""

    if redact_pii:
        from src.security.pii_redaction import redact_pii as _do_redact
        text = _do_redact(text)

    return text
