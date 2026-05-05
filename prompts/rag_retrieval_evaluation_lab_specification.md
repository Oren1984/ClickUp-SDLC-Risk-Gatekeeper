# RAG Engineering Lab — Technical Specification

## 1. Project Identity

**Repository name:** `rag-retrieval-evaluation-lab`  
**Project display name:** `RAG Engineering Lab`  
**Previous name:** RAG Retrieval Evaluation Lab  
**Project type:** RAG  
**Primary UI:** Streamlit  
**Execution style:** Local-first, modular, Dockerized, mock-friendly  
**Main goal:** Build a local RAG retrieval laboratory that compares chunking strategies, embedding providers, vector stores, retrieval quality, and optional re-ranking using measurable retrieval metrics.

---

## 2. Project Purpose

This project implements a local-first Retrieval-Augmented Generation retrieval pipeline focused on the technical retrieval layer:

```text
Ingest → Clean → Chunk → Embed → Store → Retrieve → Optional Re-rank → Evaluate → Display in Streamlit
```

The system is intended for academic submission, hands-on learning, and portfolio demonstration.

The project must demonstrate:

- document ingestion
- text cleaning
- configurable chunking
- multiple embedding providers
- ChromaDB and FAISS vector stores
- mock mode for offline/no-cost execution
- retrieval over indexed chunks
- optional re-ranking
- retrieval evaluation using metrics
- Streamlit UI
- Docker packaging
- basic security, validation, observability, and testing

---

## 3. Scope

### In Scope

The repository must include:

- Streamlit UI for document upload, configuration, retrieval, and evaluation
- PDF/TXT/MD/HTML document ingestion
- text cleaning and normalization
- configurable chunking strategies
- embedding provider abstraction
- vector store abstraction
- ChromaDB implementation
- FAISS implementation
- HuggingFace local embedding implementation
- OpenAI embedding provider interface
- Gemini embedding provider interface
- deterministic mock embedding provider
- retrieval pipeline
- optional re-ranking component
- ground-truth based evaluation
- metrics: Recall@k, MRR, nDCG, and optionally Precision@k
- Dockerfile and docker-compose.yml
- `.env.example`
- unit, integration, and E2E tests
- basic observability in the Streamlit UI
- basic security and validation controls
- concise documentation

### Out of Scope / Non-Goals

Do NOT implement or introduce:

- autonomous agents
- MCP orchestration
- CrewAI
- multi-agent workflow
- Kubernetes
- Terraform
- React frontend
- production SaaS authentication
- multi-user authorization system
- heavy local LLM serving
- Ollama as a required dependency
- paid API dependency as a default execution path
- unrelated portfolio/static site features

The project is a local modular RAG retrieval lab, not an agent platform.

---

## 4. Required Architecture Principles

The implementation must be modular, object-oriented, and provider-based.

Use common interfaces / base classes for replaceable components:

```text
EmbeddingProvider
├── MockEmbeddingProvider
├── HuggingFaceEmbeddingProvider
├── OpenAIEmbeddingProvider
└── GeminiEmbeddingProvider

VectorStore
├── ChromaVectorStore
└── FaissVectorStore

Chunker
├── RecursiveChunker
└── FixedChunker
```

The system must allow switching providers through configuration and/or the Streamlit UI without rewriting pipeline code.

---

## 5. Recommended Repository Structure

```text
rag-retrieval-evaluation-lab/
│
├── app/
│   └── streamlit_app.py
│
├── src/
│   ├── core/
│   │   ├── config.py
│   │   ├── logging_config.py
│   │   ├── exceptions.py
│   │   └── contracts.py
│   │
│   ├── ingestion/
│   │   ├── document_loader.py
│   │   ├── text_cleaner.py
│   │   └── metadata_extractor.py
│   │
│   ├── chunking/
│   │   ├── base_chunker.py
│   │   ├── recursive_chunker.py
│   │   └── fixed_chunker.py
│   │
│   ├── embeddings/
│   │   ├── base_embedding_provider.py
│   │   ├── mock_embedding_provider.py
│   │   ├── huggingface_provider.py
│   │   ├── openai_provider.py
│   │   └── gemini_provider.py
│   │
│   ├── vectorstores/
│   │   ├── base_vector_store.py
│   │   ├── chroma_store.py
│   │   └── faiss_store.py
│   │
│   ├── retrieval/
│   │   ├── retriever.py
│   │   ├── hybrid_retriever.py
│   │   └── reranker.py
│   │
│   ├── evaluation/
│   │   ├── metrics.py
│   │   ├── evaluator.py
│   │   └── ground_truth_loader.py
│   │
│   ├── observability/
│   │   ├── metrics.py
│   │   ├── tracing.py
│   │   └── health.py
│   │
│   └── security/
│       ├── file_validation.py
│       ├── query_validation.py
│       ├── prompt_safety.py
│       └── pii_redaction.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── ground_truth/
│       └── questions.json
│
├── vector_db/
│   ├── chroma/
│   └── faiss/
│
├── results/
│   └── evaluation_results.csv
│
├── notebooks/
│   └── rag_retrieval_experiments.ipynb
│
├── docs/
│   ├── specification.md
│   ├── architecture.md
│   ├── experiment_plan.md
│   ├── testing_strategy.md
│   ├── security_observability.md
│   ├── evaluation_report.md
│   └── known_limitations.md
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── README.md
└── .gitignore
```

Claude must scan the existing repository before changing anything. If the current repository already has some of these files or folders, update the plan accordingly instead of blindly recreating everything.

---

## 6. Functional Requirements

### 6.1 Document Ingestion

The system must support loading:

- `.pdf`
- `.txt`
- `.md`
- `.html`

Required behavior:

- validate file type
- validate file size
- safely store uploaded files under `data/raw/`
- extract text
- attach metadata:
  - file name
  - source path
  - file type
  - page number if available
  - chunk id after chunking

### 6.2 Text Cleaning

Implement a text cleaner that can:

- normalize whitespace
- remove excessive blank lines
- remove obvious boilerplate where reasonable
- skip empty or extremely short text sections
- preserve readable text boundaries

### 6.3 Chunking

Support at least:

- recursive chunking
- fixed-size chunking

Default configuration:

```text
chunk_size = 500
chunk_overlap = 100
```

UI-configurable parameters:

```text
chunk_size: 200–1500
chunk_overlap: 0–300
```

The system should support comparing multiple chunking setups during evaluation.

### 6.4 Embedding Providers

Implement a provider interface with these providers:

#### MockEmbeddingProvider

Required and default-safe provider.

- no API key
- no internet
- no paid dependency
- deterministic output
- fixed dimension, for example 384
- suitable for tests, CI, Docker smoke checks, and demo mode

#### HuggingFaceEmbeddingProvider

Local embedding provider.

Recommended models:

- `sentence-transformers/all-MiniLM-L6-v2`
- `BAAI/bge-base-en-v1.5`
- `intfloat/e5-base`

#### OpenAIEmbeddingProvider

Optional provider.

- uses `OPENAI_API_KEY`
- must fail gracefully if key is missing
- must not be default
- must not print secrets

#### GeminiEmbeddingProvider

Optional provider.

- uses `GEMINI_API_KEY`
- must fail gracefully if key is missing
- must not be default
- must not print secrets

### 6.5 Vector Stores

Implement a common vector store interface.

Required implementations:

#### ChromaVectorStore

- local persistence
- metadata support
- default recommended vector store

#### FaissVectorStore

- local vector index
- support metadata mapping separately if needed
- suitable for fast local experiments

The Streamlit UI should allow selecting:

```text
Vector Store:
- ChromaDB
- FAISS
```

### 6.6 Retrieval

The retrieval layer must:

- accept user query
- embed query using the same embedding provider used for documents
- retrieve top-k chunks
- return chunk text, score if available, metadata, and rank

UI-configurable parameter:

```text
top_k: 1–20
```

### 6.7 Optional Re-ranking

Add optional re-ranking behind a clear switch.

Recommended default:

```text
USE_RERANKER=false
```

If implemented, use a local cross-encoder such as:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

Rules:

- must be optional
- must not block base pipeline
- must be clearly documented as slower but more precise
- must support fallback if model loading fails

### 6.8 Evaluation

Implement evaluation against ground truth queries.

Required metrics:

- Recall@k
- MRR
- nDCG

Optional metric:

- Precision@k

Ground truth file example:

```json
[
  {
    "question": "What is the recommended overlap baseline?",
    "expected_answer": "10-20% overlap",
    "relevant_doc_id": "doc_001"
  }
]
```

Evaluation must support comparing:

- chunking strategy
- chunk size
- chunk overlap
- embedding provider
- embedding model
- vector store
- re-ranker on/off if available

Output:

- table in Streamlit
- CSV file under `results/evaluation_results.csv`

---

## 7. Streamlit UI Requirements

The Streamlit app must include:

### Sidebar Configuration

- document upload
- embedding provider selector
- embedding model selector where relevant
- vector store selector
- chunking strategy selector
- chunk size input
- overlap input
- top-k input
- re-ranker toggle
- mock mode toggle
- build index button

### Main Tabs / Sections

Recommended tabs:

1. **Ingestion**
   - upload file
   - show extracted text summary
   - show number of documents/chunks

2. **Retrieval Demo**
   - ask a question
   - show retrieved chunks
   - show rank, score, metadata, source

3. **Evaluation**
   - load ground truth
   - run benchmark
   - show metrics table
   - export CSV

4. **System Status**
   - selected provider
   - selected vector store
   - documents loaded
   - chunks created
   - last retrieval latency
   - errors count
   - readiness state

---

## 8. Security and Safety Requirements

This is not an enterprise security project, but it must include basic safeguards.

### File Upload Protection

- allow only PDF/TXT/MD/HTML
- limit upload size, for example 10MB
- prevent path traversal
- sanitize file names
- store only in controlled data folders

### Query Validation

- reject empty queries
- limit query length
- validate top-k range
- validate chunk size range
- validate overlap range
- ensure overlap is smaller than chunk size

### API Key Safety

- no keys in code
- use `.env`
- provide `.env.example`
- never log secrets
- if API key missing, switch to mock mode or show clear error

### Prompt / Query Safety

Add a lightweight warning mechanism for suspicious query patterns such as:

- "ignore previous instructions"
- "show system prompt"
- "delete files"
- "run command"
- "developer message"

Do not overbuild this. A warning is enough for v1.

### PII Redaction

Optional but recommended:

- redact emails
- redact phone numbers
- redact ID-like patterns

---

## 9. Observability Requirements

The project must include lightweight observability suitable for a Streamlit-based local system.

Track at least:

- number of loaded documents
- number of created chunks
- selected embedding provider
- selected vector store
- embedding latency
- retrieval latency
- re-ranking latency if enabled
- query count
- error count
- last error message if safe

Expose this in the Streamlit `System Status` tab.

Optional later improvement:

- Prometheus-style metrics
- FastAPI health endpoint

Do not add FastAPI unless explicitly approved later.

---

## 10. Testing Requirements

Testing must work in mock mode without external API keys.

### Unit Tests

Required:

- text cleaner
- chunkers
- embedding provider factory
- mock embedding provider
- vector store factory
- metrics: Recall@k, MRR, nDCG
- file validation
- query validation
- config loading

### Integration Tests

Required:

- Chroma pipeline with mock embeddings
- FAISS pipeline with mock embeddings
- retrieval flow
- evaluation flow using sample ground truth

### E2E Test

Required:

```text
Load sample document
→ clean
→ chunk
→ mock embed
→ store
→ retrieve
→ evaluate
```

The E2E test must not require OpenAI, Gemini, or real paid services.

---

## 11. Docker Requirements

The project must include:

- Dockerfile
- docker-compose.yml
- `.dockerignore`
- `.env.example`

Default Docker behavior:

- run Streamlit app on port `8501`
- mount or preserve:
  - `data/`
  - `vector_db/`
  - `results/`

Recommended compose service:

```yaml
services:
  rag-app:
    build: .
    ports:
      - "8501:8501"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./vector_db:/app/vector_db
      - ./results:/app/results
```

Docker must support mock mode as the default safe execution path.

---

## 12. Configuration Requirements

Required `.env.example` keys:

```env
APP_ENV=local
MOCK_MODE=true

EMBEDDING_PROVIDER=mock
EMBEDDING_MODEL=mock-384
VECTOR_STORE=chroma

CHUNK_STRATEGY=recursive
CHUNK_SIZE=500
CHUNK_OVERLAP=100
TOP_K=5
USE_RERANKER=false

OPENAI_API_KEY=
GEMINI_API_KEY=

DATA_DIR=data
VECTOR_DB_DIR=vector_db
RESULTS_DIR=results
MAX_UPLOAD_MB=10
LOG_LEVEL=INFO
```

---

## 13. Documentation Requirements

Required documentation:

- `README.md`
- `docs/specification.md`
- `docs/architecture.md`
- `docs/experiment_plan.md`
- `docs/testing_strategy.md`
- `docs/security_observability.md`
- `docs/evaluation_report.md`
- `docs/known_limitations.md`

README must include:

- project purpose
- what the project does
- what it does not do
- quickstart local
- Docker quickstart
- configuration table
- supported providers
- supported vector stores
- mock mode explanation
- evaluation explanation
- testing instructions

---

## 14. CI/CD Requirements

CI/CD is not required in the first implementation stage, but the repository should be ready for it.

Later CI should run:

```text
install dependencies
lint or static check if available
unit tests
integration tests in mock mode
Docker build
optional smoke check
```

Do not introduce complex deployment workflows unless explicitly approved.

---

## 15. Delivery Plan for Claude

Claude must follow the staged prompt pipeline and must not implement all phases at once.

Use the existing prompt workflow:

1. `00_pipeline_controller.md` + `01_scan_and_plan.md`
2. Wait for approval
3. `00_pipeline_controller.md` + `02_architecture_review.md`
4. Wait for approval
5. `00_pipeline_controller.md` + `03_execute_plan.md`
6. Execute one approved stage at a time
7. Wait for approval after each stage
8. `00_pipeline_controller.md` + `04_testing_audit.md`
9. `00_pipeline_controller.md` + `05_documentation_update.md`
10. `00_pipeline_controller.md` + `06_cicd_setup.md`

---

## 16. Success Criteria

The project is successful when:

- Streamlit app runs locally
- Docker Compose runs the app
- user can upload or load a sample document
- system chunks the text
- selected embedding provider creates embeddings
- selected vector store stores chunks
- user can query and retrieve top-k chunks
- mock mode works without external API keys
- Chroma and FAISS are both supported or clearly staged
- basic evaluation metrics run
- results are displayed in Streamlit
- tests pass in mock mode
- README explains usage and boundaries
- no agent/MCP/CrewAI scope is introduced

---

## 17. Key Engineering Boundaries

Claude must preserve these boundaries:

- Local-first
- RAG retrieval only
- Streamlit UI only
- Mock mode first
- Paid APIs optional only
- Dockerized
- Modular OOP provider design
- No agent orchestration
- No heavy platform expansion
- No cloud deployment in v1
- No unrelated portfolio features

---

## 18. Final Implementation Priority

Build in this order:

1. repository scan and plan
2. architecture review
3. minimal working pipeline with mock mode
4. Streamlit UI
5. ChromaDB support
6. FAISS support
7. HuggingFace support
8. optional OpenAI/Gemini provider stubs or working adapters
9. evaluation metrics
10. security validation
11. observability panel
12. Docker
13. tests
14. documentation
15. CI/CD planning
