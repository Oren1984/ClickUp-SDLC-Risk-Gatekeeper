from __future__ import annotations

import re

# Email addresses
_EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
)

# Phone-like sequences: optional +, a digit, 7-15 mixed digit/separator chars, a digit
_PHONE_RE = re.compile(
    r"\+?\d[\d\s\-().]{7,15}\d"
)

# Long digit runs that resemble IDs, SSNs, or account numbers (7+ consecutive digits)
_ID_RE = re.compile(r"\b\d{7,}\b")

_EMAIL_PLACEHOLDER = "[EMAIL]"
_PHONE_PLACEHOLDER = "[PHONE]"
_ID_PLACEHOLDER = "[ID]"


def redact_pii(text: str) -> str:
    """
    Replace recognisable PII patterns with safe placeholders.

    Apply during ingestion (before chunking and storage) when
    PII redaction is enabled via configuration. Optional in v1.
    """
    text = _EMAIL_RE.sub(_EMAIL_PLACEHOLDER, text)
    text = _PHONE_RE.sub(_PHONE_PLACEHOLDER, text)
    text = _ID_RE.sub(_ID_PLACEHOLDER, text)
    return text
