from __future__ import annotations

import hashlib
import math
from typing import List

from src.embeddings.base_embedding_provider import BaseEmbeddingProvider

_DIMENSION = 384

# numpy is used when available (it is in requirements.txt) for higher-quality
# random normal vectors.  A pure-stdlib fallback is provided so that the mock
# provider can operate in any environment where numpy may be unavailable.
try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic mock embedding provider.

    Requires no API key, no internet, and no model download.
    Produces L2-normalised unit vectors of fixed dimension 384.
    The same input text always returns the same vector — guaranteed stable
    within a single Python process and across runs.

    Use this as the default provider for tests, CI, and Docker smoke checks.
    """

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [_text_to_vector(t) for t in texts]

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def dimension(self) -> int:
        return _DIMENSION


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _text_to_vector(text: str) -> List[float]:
    """
    Produce a deterministic unit-norm vector for *text*.

    Uses numpy when available (seeded PRNG → standard-normal draw → L2 norm).
    Falls back to a pure-stdlib approach when numpy is not installed.
    Within a single session the same implementation is always chosen, so
    vectors produced during index-build and query are always compatible.
    """
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    seed = int.from_bytes(digest[:4], byteorder="big")

    if _HAS_NUMPY:
        return _numpy_vector(seed)
    return _stdlib_vector(digest)


def _numpy_vector(seed: int) -> List[float]:
    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(_DIMENSION)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def _stdlib_vector(digest: bytes) -> List[float]:
    """
    Pure-stdlib deterministic vector using SHAKE-128 XOF.
    Each 4-byte window of the expanded output is interpreted as a signed
    32-bit integer and mapped to the range [-1, 1].
    """
    raw = hashlib.shake_128(digest).digest(4 * _DIMENSION)
    values: List[float] = []
    for i in range(0, 4 * _DIMENSION, 4):
        n = int.from_bytes(raw[i: i + 4], byteorder="big", signed=True)
        values.append(n / 2_147_483_648.0)

    norm = math.sqrt(sum(x * x for x in values))
    return [x / norm for x in values] if norm > 0 else values
