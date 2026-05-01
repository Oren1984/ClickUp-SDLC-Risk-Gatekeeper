from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

# Lightweight pattern list for v1. Not a comprehensive injection defense —
# a warning mechanism only. Expand in future versions if needed.
_SUSPICIOUS_PATTERNS: List[str] = [
    "ignore previous instructions",
    "ignore all previous",
    "disregard previous",
    "show system prompt",
    "reveal system prompt",
    "print system prompt",
    "developer message",
    "system message",
    "forget your instructions",
    "delete files",
    "run command",
    "execute code",
    "drop table",
    "rm -rf",
]


@dataclass
class SafetyCheckResult:
    is_suspicious: bool
    matched_patterns: List[str] = field(default_factory=list)
    warning: str = ""


def check_prompt_safety(query: str) -> SafetyCheckResult:
    """
    Lightweight scan for suspicious query patterns.

    Returns a SafetyCheckResult. Does not block — the caller (Streamlit UI)
    decides whether to warn the user or proceed.
    """
    lower = query.lower()
    matched = [p for p in _SUSPICIOUS_PATTERNS if p in lower]

    if matched:
        return SafetyCheckResult(
            is_suspicious=True,
            matched_patterns=matched,
            warning=(
                "Query may contain a prompt-injection attempt. "
                "Proceeding with caution."
            ),
        )

    return SafetyCheckResult(is_suspicious=False)
