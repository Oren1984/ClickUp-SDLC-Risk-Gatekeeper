from __future__ import annotations

from typing import List, Optional

from src.core.exceptions import EmbeddingError
from src.embeddings.base_embedding_provider import BaseEmbeddingProvider

_DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Known output dimensions for supported models.
# Used to answer dimension queries before the model is loaded.
_KNOWN_DIMENSIONS: dict[str, int] = {
    "sentence-transformers/all-MiniLM-L6-v2": 384,
    "BAAI/bge-base-en-v1.5": 768,
    "intfloat/e5-base": 768,
}


class HuggingFaceEmbeddingProvider(BaseEmbeddingProvider):
    """
    Local embedding provider backed by sentence-transformers.

    The model is lazy-loaded on first embed() call — no download happens at
    construction time.  Requires sentence-transformers to be installed and
    internet access for the initial model download.

    Supported models (recommended):
    - sentence-transformers/all-MiniLM-L6-v2  (384 dims, fast, default)
    - BAAI/bge-base-en-v1.5                   (768 dims, higher quality)
    - intfloat/e5-base                         (768 dims, strong retrieval)
    """

    def __init__(
        self,
        model_name: str = _DEFAULT_MODEL,
        device: Optional[str] = None,
    ) -> None:
        self._model_name = model_name
        self._device = device  # None lets sentence-transformers auto-detect
        self._model = None
        self._dimension: int = _KNOWN_DIMENSIONS.get(model_name, 0)

    # ------------------------------------------------------------------

    def embed(self, texts: List[str]) -> List[List[float]]:
        self._ensure_loaded()
        try:
            embeddings = self._model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            return [e.tolist() for e in embeddings]
        except Exception as exc:
            raise EmbeddingError(
                f"HuggingFace embedding failed for model '{self._model_name}': {exc}"
            ) from exc

    @property
    def provider_name(self) -> str:
        return "huggingface"

    @property
    def dimension(self) -> int:
        return self._dimension

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise EmbeddingError(
                "sentence-transformers is required for HuggingFaceEmbeddingProvider. "
                "Install it with: pip install sentence-transformers"
            ) from exc

        try:
            kwargs = {"model_name_or_path": self._model_name}
            if self._device:
                kwargs["device"] = self._device
            self._model = SentenceTransformer(**kwargs)
            self._dimension = self._model.get_sentence_embedding_dimension()
        except Exception as exc:
            raise EmbeddingError(
                f"Failed to load model '{self._model_name}': {exc}. "
                "Ensure the model name is valid and internet access is available "
                "for the initial download."
            ) from exc
