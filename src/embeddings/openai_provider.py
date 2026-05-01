from __future__ import annotations

import os
from typing import List, Optional

from src.core.exceptions import EmbeddingError
from src.embeddings.base_embedding_provider import BaseEmbeddingProvider

_DEFAULT_MODEL = "text-embedding-3-small"

_KNOWN_DIMENSIONS: dict[str, int] = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """
    Optional embedding provider backed by the OpenAI Embeddings API.

    Requires OPENAI_API_KEY to be set in the environment or passed explicitly.
    Raises EmbeddingError at construction time if the key is absent.

    Never logs or prints the API key.
    Not required for mock mode, tests, or CI.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = _DEFAULT_MODEL,
    ) -> None:
        resolved = api_key or os.getenv("OPENAI_API_KEY") or ""
        if not resolved:
            raise EmbeddingError(
                "OPENAI_API_KEY is required for OpenAIEmbeddingProvider. "
                "Set it in your .env file or pass it as api_key=. "
                "Switch EMBEDDING_PROVIDER=mock to run without an API key."
            )
        self._model_name = model_name
        self._dimension = _KNOWN_DIMENSIONS.get(model_name, 1536)
        self._client = None
        # Store key only for lazy client construction; never expose it.
        self.__api_key = resolved

    # ------------------------------------------------------------------

    def embed(self, texts: List[str]) -> List[List[float]]:
        self._ensure_client()
        try:
            response = self._client.embeddings.create(
                input=texts,
                model=self._model_name,
            )
            return [item.embedding for item in response.data]
        except Exception as exc:
            raise EmbeddingError(f"OpenAI embedding request failed: {exc}") from exc

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def dimension(self) -> int:
        return self._dimension

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _ensure_client(self) -> None:
        if self._client is not None:
            return
        try:
            import openai
        except ImportError as exc:
            raise EmbeddingError(
                "openai package is required for OpenAIEmbeddingProvider. "
                "Install it with: pip install openai"
            ) from exc
        self._client = openai.OpenAI(api_key=self.__api_key)
