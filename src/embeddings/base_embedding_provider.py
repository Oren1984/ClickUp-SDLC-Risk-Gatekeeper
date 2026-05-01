from __future__ import annotations

from typing import List

from src.core.contracts import EmbeddingProvider

# Re-export so downstream code can import from either location.
__all__ = ["BaseEmbeddingProvider", "EmbeddingProvider"]


class BaseEmbeddingProvider(EmbeddingProvider):
    """
    Abstract base that adds shared convenience on top of EmbeddingProvider.

    Concrete providers (Mock, HuggingFace, OpenAI, Gemini) inherit from here.
    Do not instantiate BaseEmbeddingProvider directly — it does not implement
    embed(), provider_name, or dimension.
    """

    def embed_one(self, text: str) -> List[float]:
        """Embed a single text string. Convenience wrapper around embed()."""
        return self.embed([text])[0]
