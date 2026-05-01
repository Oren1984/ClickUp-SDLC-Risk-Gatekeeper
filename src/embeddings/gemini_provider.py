from __future__ import annotations

import os
from typing import List, Optional

from src.core.exceptions import EmbeddingError
from src.embeddings.base_embedding_provider import BaseEmbeddingProvider

_DEFAULT_MODEL = "models/embedding-001"
_DEFAULT_TASK_TYPE = "RETRIEVAL_DOCUMENT"

# models/embedding-001 and models/text-embedding-004 both return 768 dims.
_KNOWN_DIMENSIONS: dict[str, int] = {
    "models/embedding-001": 768,
    "models/text-embedding-004": 768,
}


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """
    Optional embedding provider backed by the Google Gemini Embeddings API.

    Requires GEMINI_API_KEY to be set in the environment or passed explicitly.
    Raises EmbeddingError at construction time if the key is absent.

    Never logs or prints the API key.
    Not required for mock mode, tests, or CI.

    task_type controls the Gemini embedding optimization target:
    - "RETRIEVAL_DOCUMENT"  — for indexing document chunks (default)
    - "RETRIEVAL_QUERY"     — for embedding user queries
    - "SEMANTIC_SIMILARITY" — general similarity tasks
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = _DEFAULT_MODEL,
        task_type: str = _DEFAULT_TASK_TYPE,
    ) -> None:
        resolved = api_key or os.getenv("GEMINI_API_KEY") or ""
        if not resolved:
            raise EmbeddingError(
                "GEMINI_API_KEY is required for GeminiEmbeddingProvider. "
                "Set it in your .env file or pass it as api_key=. "
                "Switch EMBEDDING_PROVIDER=mock to run without an API key."
            )
        self._model_name = model_name
        self._task_type = task_type
        self._dimension = _KNOWN_DIMENSIONS.get(model_name, 768)
        self._genai = None
        self.__api_key = resolved

    # ------------------------------------------------------------------

    def embed(self, texts: List[str]) -> List[List[float]]:
        self._ensure_configured()
        results: List[List[float]] = []
        for text in texts:
            try:
                response = self._genai.embed_content(
                    model=self._model_name,
                    content=text,
                    task_type=self._task_type,
                )
                results.append(response["embedding"])
            except Exception as exc:
                raise EmbeddingError(
                    f"Gemini embedding request failed for model "
                    f"'{self._model_name}': {exc}"
                ) from exc
        return results

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def dimension(self) -> int:
        return self._dimension

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _ensure_configured(self) -> None:
        if self._genai is not None:
            return
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise EmbeddingError(
                "google-generativeai package is required for GeminiEmbeddingProvider. "
                "Install it with: pip install google-generativeai"
            ) from exc
        genai.configure(api_key=self.__api_key)
        self._genai = genai
