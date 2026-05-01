from __future__ import annotations

import os
from typing import Any, Dict, List

from src.core.contracts import Chunk
from src.core.exceptions import VectorStoreError
from src.vectorstores.base_vector_store import BaseVectorStore

_DEFAULT_COLLECTION = "rag_chunks"
_DEFAULT_PERSIST_DIR = os.path.join("vector_db", "chroma")


class ChromaVectorStore(BaseVectorStore):
    """
    Vector store backed by ChromaDB with local persistence.

    Embeddings must be pre-computed and attached to Chunk objects before
    calling add(). This class never invokes any embedding provider.

    The collection uses cosine distance, which is compatible with the
    L2-normalised vectors produced by all embedding providers in this project.
    """

    def __init__(
        self,
        persist_directory: str = _DEFAULT_PERSIST_DIR,
        collection_name: str = _DEFAULT_COLLECTION,
    ) -> None:
        self._persist_directory = persist_directory
        self._collection_name = collection_name
        self._client = None
        self._collection = None

    # ------------------------------------------------------------------
    # VectorStore interface
    # ------------------------------------------------------------------

    def add(self, chunks: List[Chunk]) -> None:
        if not chunks:
            return
        self._require_embeddings(chunks)
        collection = self._get_collection()
        ids = [c.chunk_id for c in chunks]
        embeddings = [c.embedding for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [self._build_chroma_metadata(c) for c in chunks]
        try:
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
        except Exception as exc:
            raise VectorStoreError(f"ChromaDB add failed: {exc}") from exc

    def search(self, query_embedding: List[float], top_k: int) -> List[Chunk]:
        collection = self._get_collection()
        try:
            count = collection.count()
        except Exception as exc:
            raise VectorStoreError(f"ChromaDB count failed: {exc}") from exc
        if count == 0:
            return []
        n = min(top_k, count)
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            raise VectorStoreError(f"ChromaDB search failed: {exc}") from exc
        return self._parse_results(results)

    def persist(self) -> None:
        # PersistentClient writes to disk automatically; this fulfils the interface.
        pass

    def load(self) -> None:
        # Lazily opens the collection if not already open.
        self._get_collection()

    def clear(self) -> None:
        client = self._ensure_client()
        try:
            client.delete_collection(self._collection_name)
        except Exception:
            pass  # Collection may not exist yet; that's fine
        self._collection = None

    @property
    def store_name(self) -> str:
        return "chroma"

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _ensure_client(self):
        if self._client is not None:
            return self._client
        try:
            import chromadb
        except ImportError as exc:
            raise VectorStoreError(
                "chromadb package is required for ChromaVectorStore. "
                "Install it with: pip install chromadb"
            ) from exc
        os.makedirs(self._persist_directory, exist_ok=True)
        try:
            self._client = chromadb.PersistentClient(path=self._persist_directory)
        except Exception as exc:
            raise VectorStoreError(
                f"Failed to create ChromaDB client at '{self._persist_directory}': {exc}"
            ) from exc
        return self._client

    def _get_collection(self):
        if self._collection is not None:
            return self._collection
        client = self._ensure_client()
        try:
            self._collection = client.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as exc:
            raise VectorStoreError(
                f"Failed to get/create ChromaDB collection '{self._collection_name}': {exc}"
            ) from exc
        return self._collection

    @staticmethod
    def _build_chroma_metadata(chunk: Chunk) -> Dict[str, Any]:
        """
        Build a flat metadata dict for ChromaDB storage.

        ChromaDB requires flat dicts with str/int/float/bool values and
        no None entries. doc_id is always included for round-trip reconstruction.
        """
        meta: Dict[str, Any] = {"doc_id": chunk.doc_id}
        for k, v in chunk.metadata.items():
            if isinstance(v, (str, int, float, bool)):
                meta[k] = v
            elif v is not None:
                meta[k] = str(v)
            # None values are silently dropped; Chroma does not accept them
        return meta

    @staticmethod
    def _parse_results(results: dict) -> List[Chunk]:
        ids_list = results.get("ids", [[]])[0]
        docs_list = results.get("documents", [[]])[0]
        metas_list = results.get("metadatas", [[]])[0]
        dists_list = results.get("distances", [[]])[0]

        chunks: List[Chunk] = []
        for rank, (cid, text, raw_meta, dist) in enumerate(
            zip(ids_list, docs_list, metas_list, dists_list), start=1
        ):
            meta = dict(raw_meta)  # defensive copy before mutation
            doc_id = meta.pop("doc_id", "")
            chunks.append(
                Chunk(
                    chunk_id=cid,
                    doc_id=doc_id,
                    text=text,
                    metadata=meta,
                    score=1.0 - dist,  # cosine distance -> cosine similarity
                    rank=rank,
                )
            )
        return chunks
