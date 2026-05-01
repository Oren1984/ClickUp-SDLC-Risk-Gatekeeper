# Testing Strategy

## Overview

The RAG Retrieval Evaluation Lab uses a **layered testing approach**:

1. **Stage smoke tests** — fast, standalone scripts run at the end of each build stage
2. **Unit tests** — pure function and component tests in `tests/unit/`
3. **Integration tests** — multi-component tests in `tests/integration/`
4. **End-to-end tests** — full pipeline tests in `tests/e2e/`

**All tests run in mock mode by default.** No API keys, no model downloads, and
no network access are required to run the test suite.

---

## Running Tests

```bash
# Run the full test suite
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run a specific layer
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run a stage smoke test directly
python _stage8_smoke_test.py
```

---

## Test Layers

### Stage Smoke Tests (`_stageN_smoke_test.py`)

Each build stage has a standalone smoke test at the repository root. These are
plain Python scripts (no pytest required) that validate all functionality added
in that stage before the next stage begins.

| File | Stage | Tests |
|------|-------|-------|
| `_stage5_smoke_test.py` | Embeddings | Mock, HuggingFace stub, OpenAI stub, Gemini stub |
| `_stage6_smoke_test.py` | Vector stores | ChromaDB add/search/persist, FAISS add/search |
| `_stage7_smoke_test.py` | Retrieval | Retriever, PassThroughReranker, RAGPipeline |
| `_stage8_smoke_test.py` | Evaluation | Metrics, GroundTruthLoader, RetrievalEvaluator |

All stage smoke tests:
- Use `MockEmbeddingProvider` exclusively
- Use `tempfile.TemporaryDirectory(ignore_cleanup_errors=True)` for isolation
- Call `METRICS.reset()` in teardown to prevent state leakage
- Assert exact expected values using manual arithmetic (no floating-point surprises)

---

### Unit Tests (`tests/unit/`)

Unit tests cover individual modules in isolation.

**What to test:**

- `src/evaluation/metrics.py` — each metric function against hand-calculated values:
  - Empty inputs return 0.0
  - k=0 returns 0.0
  - k > len(retrieved) handles gracefully
  - Multi-relevant document sets
  - nDCG deduplication (same doc_id across chunks)

- `src/chunking/` — each chunker with:
  - Empty document text
  - Text shorter than chunk_size (produces one chunk)
  - chunk_overlap >= chunk_size raises `ChunkingError`
  - Whitespace-only text produces no chunks

- `src/ingestion/text_cleaner.py` — whitespace normalisation, PII redaction

- `src/security/query_validation.py` — empty query, query over max length,
  valid query passes

- `src/embeddings/mock_embedding_provider.py` — dimension, L2 norm, determinism

**What does NOT require API keys:**

All unit tests. Mock provider produces valid vectors without any network calls.

---

### Integration Tests (`tests/integration/`)

Integration tests verify that two or more layers work together correctly.

**Key scenarios:**

- `Chunker` + `EmbeddingProvider` — chunks from a real document get valid embeddings
- `EmbeddingProvider` + `VectorStore` — embedded chunks are stored and retrieved
- `RAGPipeline.build_index()` — full ingestion path with a real temporary file
- `RAGPipeline.query()` — returns `List[Chunk]` with `score` and `rank` populated
- `RetrievalEvaluator` + `RAGPipeline` — evaluation completes with no errors

**Vector store tests:**

ChromaDB integration tests use `tempfile.TemporaryDirectory(ignore_cleanup_errors=True)`
to handle the Windows file-lock behaviour of ChromaDB's persistent client.

FAISS integration tests check:
- `ntotal == 0` before add; graceful empty-index search
- Sentinel index `-1` returned by FAISS on insufficient results handled correctly

---

### End-to-End Tests (`tests/e2e/`)

E2E tests run the full pipeline from a raw document file to a CSV evaluation result.

**Reference scenario (mirrors Stage 8 smoke test):**

1. Write `doc_001.txt` to a temp directory
2. Build an index with `MockEmbeddingProvider` + `ChromaVectorStore`
3. Load `data/ground_truth/questions.json`
4. Run `RetrievalEvaluator.evaluate(ground_truth, top_k=5)`
5. Assert:
   - `error_count == 0`
   - All metric scores in `[0.0, 1.0]`
   - `recall@5 == 1.0` (all five questions find `doc_001`)
6. Assert `save_results_csv()` writes a 6-line file (header + 5 rows)

**All E2E tests must pass without API keys.**

---

## What Should Never Require API Keys

| Component | Reason |
|-----------|--------|
| All unit tests | Use `MockEmbeddingProvider` |
| All integration tests | Use `MockEmbeddingProvider` |
| All E2E tests | Use `MockEmbeddingProvider` |
| Stage smoke tests | Use `MockEmbeddingProvider` |
| Docker smoke check | `MOCK_MODE=true` in default `.env` |
| Streamlit UI startup | Mock mode is the default |
| Notebook execution | Both notebooks use mock mode |

Real providers (`huggingface`, `openai`, `gemini`) are tested only in manual or
optional CI runs that have the necessary credentials.

---

## Docker Smoke Check

After building the Docker image, verify the container starts and the Streamlit UI
is reachable:

```bash
docker compose up --build -d
# Wait for container to start
curl -s -o /dev/null -w "%{http_code}" http://localhost:8501
# Expected: 200
docker compose down
```

The container runs with the default `.env` settings (`MOCK_MODE=true`), so no
API keys are required.

---

## Streamlit Smoke Check

A quick manual smoke check of the Streamlit UI:

1. `streamlit run app/streamlit_app.py`
2. Open [http://localhost:8501](http://localhost:8501)
3. Upload a `.txt` file → click "Build Index" → verify success message
4. Switch to Retrieval Demo → enter a query → verify ranked results appear
5. Switch to Evaluation → click "Run Evaluation" → verify metric scores appear
6. Switch to System Status → verify METRICS counters are non-zero

All steps should complete without entering any API key.

---

## Test Coverage Goals

| Layer | Target coverage |
|-------|----------------|
| `src/evaluation/metrics.py` | 100% |
| `src/evaluation/ground_truth_loader.py` | 100% |
| `src/evaluation/evaluator.py` | > 90% |
| `src/chunking/` | > 90% |
| `src/embeddings/mock_embedding_provider.py` | 100% |
| `src/security/` | > 85% |
| `src/pipeline/rag_pipeline.py` | > 85% |
| `src/vectorstores/` | > 80% |

---

## Test Isolation Rules

1. **Never share state between tests.** Each test creates its own temp directory
   and calls `METRICS.reset()` in teardown.
2. **Never write to `data/` or `vector_db/` in tests.** Use `tempfile.mkdtemp()`
   or `tempfile.TemporaryDirectory()`.
3. **Never commit `.env` with real API keys.** Tests must pass with the defaults
   in `.env.example`.
4. **Never skip cleanup on Windows.** Use `ignore_cleanup_errors=True` on
   `TemporaryDirectory` for ChromaDB tests.
