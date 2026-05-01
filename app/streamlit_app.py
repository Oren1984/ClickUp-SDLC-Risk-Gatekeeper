"""RAG Retrieval Evaluation Lab — Streamlit UI"""
from __future__ import annotations

import os
import sys

# Ensure project root is on the path regardless of CWD
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st

# Must be the first Streamlit call
st.set_page_config(
    page_title="RAG Retrieval Evaluation Lab",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🧪",
)

from src.core.config import settings
from src.core.exceptions import (
    ConfigurationError,
    EvaluationError,
    RAGLabError,
    ValidationError,
)
from src.observability.health import check_health
from src.observability.metrics import METRICS
from src.security.file_validation import validate_file
from src.security.prompt_safety import check_prompt_safety

# Create runtime directories on startup
for _d in [
    settings.data_dir,
    os.path.join(settings.data_dir, "raw"),
    os.path.join(settings.data_dir, "ground_truth"),
    settings.vector_db_dir,
    settings.results_dir,
]:
    os.makedirs(_d, exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════
# Session state
# ══════════════════════════════════════════════════════════════════════════

_SS_DEFAULTS: dict = {
    "pipeline": None,
    "index_built": False,
    "last_build_summary": None,
    "last_retrieval_results": [],
    "last_evaluation_summary": None,
    "last_evaluation_results": [],
    "built_with_config": {},
}
for _k, _v in _SS_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ══════════════════════════════════════════════════════════════════════════
# Factory helpers
# ══════════════════════════════════════════════════════════════════════════

def create_embedding_provider(provider_name: str, model_name: str):
    if provider_name == "mock":
        from src.embeddings.mock_embedding_provider import MockEmbeddingProvider
        return MockEmbeddingProvider()
    if provider_name == "huggingface":
        from src.embeddings.huggingface_provider import HuggingFaceEmbeddingProvider
        return HuggingFaceEmbeddingProvider(model_name=model_name)
    if provider_name == "openai":
        from src.embeddings.openai_provider import OpenAIEmbeddingProvider
        return OpenAIEmbeddingProvider(api_key=settings.openai_api_key, model_name=model_name)
    if provider_name == "gemini":
        from src.embeddings.gemini_provider import GeminiEmbeddingProvider
        return GeminiEmbeddingProvider(api_key=settings.gemini_api_key, model_name=model_name)
    raise ConfigurationError(f"Unknown embedding provider: {provider_name!r}")


def create_vector_store(store_name: str):
    if store_name == "chroma":
        from src.vectorstores.chroma_store import ChromaVectorStore
        return ChromaVectorStore(
            persist_directory=os.path.join(settings.vector_db_dir, "chroma"),
        )
    if store_name == "faiss":
        from src.vectorstores.faiss_store import FaissVectorStore
        return FaissVectorStore(
            persist_directory=os.path.join(settings.vector_db_dir, "faiss"),
        )
    raise ConfigurationError(f"Unknown vector store: {store_name!r}")


def create_chunker(strategy: str, chunk_size: int, chunk_overlap: int):
    if strategy == "recursive":
        from src.chunking.recursive_chunker import RecursiveChunker
        return RecursiveChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    if strategy == "fixed":
        from src.chunking.fixed_chunker import FixedChunker
        return FixedChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    raise ConfigurationError(f"Unknown chunking strategy: {strategy!r}")


def create_reranker(_use_reranker: bool):
    # v1: PassThroughReranker only. CrossEncoderReranker support in a future version.
    from src.retrieval.reranker import PassThroughReranker
    return PassThroughReranker()


# ══════════════════════════════════════════════════════════════════════════
# UI helpers
# ══════════════════════════════════════════════════════════════════════════

def _save_upload(uploaded_file) -> str:
    """Validate and persist an uploaded Streamlit file under data/raw/."""
    raw_dir = os.path.join(settings.data_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    content = uploaded_file.getvalue()
    safe_name = validate_file(
        uploaded_file.name, len(content), max_upload_mb=settings.max_upload_mb,
    )
    save_path = os.path.join(raw_dir, safe_name)
    with open(save_path, "wb") as f:
        f.write(content)
    return save_path


def _cfg_snapshot(provider, model, store, strategy, csize, coverlap) -> dict:
    return {
        "provider": provider, "model": model, "store": store,
        "strategy": strategy, "chunk_size": int(csize), "chunk_overlap": int(coverlap),
    }


def _cfg_changed(cfg: dict) -> bool:
    return (
        bool(st.session_state.index_built)
        and st.session_state.built_with_config != cfg
    )


def _fmt_size(n_bytes: int) -> str:
    if n_bytes < 1_048_576:
        return f"{n_bytes / 1024:.1f} KB"
    return f"{n_bytes / 1_048_576:.2f} MB"


# ══════════════════════════════════════════════════════════════════════════
# Page header
# ══════════════════════════════════════════════════════════════════════════

st.markdown(
    """
    <div style="
        padding: 0.75rem 0 0.5rem;
        border-bottom: 2px solid #e0e6ed;
        margin-bottom: 0.75rem;
    ">
        <h1 style="margin:0; font-size:1.9rem; line-height:1.25;">
            🧪 RAG Retrieval Evaluation Lab
        </h1>
        <p style="margin:0.3rem 0 0; font-size:1.0rem; color:#333;">
            <strong>Oren Salami</strong> | 🧠 AI Systems Engineer
        </p>
        <p style="margin:0.1rem 0 0; color:#888; font-size:0.85rem;">
            Intelligent Systems &bull; AI Agents &bull; Data &amp; Automation
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.header("⚙️ Configuration")

    mock_mode = st.toggle(
        "Mock Mode",
        value=True,
        key="sw_mock_mode",
        help="Deterministic mock embeddings — no API key required.",
    )

    # ── Embedding ──────────────────────────────────────────────────────────
    st.subheader("Embedding")
    provider_name: str = st.selectbox(
        "Provider",
        ["mock", "huggingface", "openai", "gemini"],
        index=0,
        key="sw_provider",
    )

    if mock_mode and provider_name != "mock":
        st.caption("ℹ️ Mock Mode is ON — consider switching to the 'mock' provider.")

    _model_map = {
        "mock":        ["mock-384"],
        "huggingface": [
            "sentence-transformers/all-MiniLM-L6-v2",
            "BAAI/bge-base-en-v1.5",
            "intfloat/e5-base",
        ],
        "openai":  ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
        "gemini":  ["models/embedding-001", "models/text-embedding-004"],
    }
    model_name: str = st.selectbox(
        "Model", _model_map.get(provider_name, ["mock-384"]), key="sw_model",
    )

    # API key guard for paid providers
    if provider_name == "openai" and not settings.openai_api_key:
        st.error("OPENAI_API_KEY not set. Add it to .env or use mock mode.")
    if provider_name == "gemini" and not settings.gemini_api_key:
        st.error("GEMINI_API_KEY not set. Add it to .env or use mock mode.")

    # ── Vector store ───────────────────────────────────────────────────────
    st.subheader("Vector Store")
    store_name: str = st.selectbox("Store", ["chroma", "faiss"], key="sw_store")

    # ── Chunking ───────────────────────────────────────────────────────────
    st.subheader("Chunking")
    chunk_strategy: str = st.selectbox(
        "Strategy", ["recursive", "fixed"], key="sw_strategy",
    )
    chunk_size: int = int(
        st.number_input("Chunk Size", min_value=200, max_value=1500, value=500,
                        step=50, key="sw_chunk_size")
    )
    chunk_overlap: int = int(
        st.number_input("Chunk Overlap", min_value=0, max_value=300, value=100,
                        step=10, key="sw_chunk_overlap")
    )
    _overlap_invalid = chunk_overlap >= chunk_size
    if _overlap_invalid:
        st.error("Chunk overlap must be less than chunk size.")

    # ── Retrieval ──────────────────────────────────────────────────────────
    st.subheader("Retrieval")
    top_k: int = int(
        st.number_input("Top-K", min_value=1, max_value=20, value=5, key="sw_top_k")
    )

    # ── Options ────────────────────────────────────────────────────────────
    st.subheader("Options")
    use_reranker: bool = st.toggle(
        "Use Reranker", value=False, key="sw_use_reranker",
        help="v1: PassThroughReranker (no-op). Full cross-encoder in a future version.",
    )
    redact_pii: bool = st.toggle("PII Redaction", value=False, key="sw_redact_pii")

    # ── Config change warning ──────────────────────────────────────────────
    _cfg = _cfg_snapshot(
        provider_name, model_name, store_name, chunk_strategy, chunk_size, chunk_overlap,
    )
    if _cfg_changed(_cfg):
        st.warning("⚠️ Config changed since last build — rebuild the index.")

    # ── Index status ───────────────────────────────────────────────────────
    if st.session_state.index_built and st.session_state.last_build_summary:
        _bs = st.session_state.last_build_summary
        st.success(
            f"✅ Index ready  \n"
            f"{_bs.get('chunks_created','?')} chunks · "
            f"{_bs.get('embedding_provider','?')} / {_bs.get('vector_store','?')}"
        )

    st.divider()
    st.subheader("Actions")

    build_clicked: bool = st.button(
        "🔨 Build Index",
        type="primary",
        key="btn_build",
        use_container_width=True,
        disabled=_overlap_invalid,
    )
    clear_clicked: bool = st.button(
        "🗑️ Clear / Reset",
        key="btn_clear",
        use_container_width=True,
    )

    # Handle clear immediately (before tabs render)
    if clear_clicked:
        if st.session_state.pipeline is not None:
            try:
                st.session_state.pipeline.clear()
            except Exception:
                pass
        for _k, _v in _SS_DEFAULTS.items():
            st.session_state[_k] = _v
        st.toast("Pipeline cleared.", icon="🗑️")

# ══════════════════════════════════════════════════════════════════════════
# Tabs
# ══════════════════════════════════════════════════════════════════════════

tab_ingest, tab_retrieval, tab_eval, tab_status = st.tabs(
    ["📥 Ingestion", "🔍 Retrieval Demo", "📊 Evaluation", "🩺 System Status"]
)

# ─────────────────────────────────────────────────────────────────────────
# Tab 1 — Ingestion
# ─────────────────────────────────────────────────────────────────────────

with tab_ingest:
    st.subheader("Document Ingestion")
    st.caption(
        "Upload a document, adjust the pipeline configuration in the sidebar, "
        "then click **🔨 Build Index**."
    )

    uploaded_file = st.file_uploader(
        "Upload document",
        type=["pdf", "txt", "md", "html", "htm"],
        key="file_uploader",
        help="Supported formats: PDF, TXT, Markdown, HTML, HTM",
    )

    if uploaded_file is not None:
        _content = uploaded_file.getvalue()
        _c1, _c2, _c3 = st.columns(3)
        _c1.metric("Filename", uploaded_file.name)
        _c2.metric("Size", _fmt_size(len(_content)))
        _c3.metric("Type", os.path.splitext(uploaded_file.name)[1].lower() or "—")

    # ── Build Index handler ────────────────────────────────────────────────
    if build_clicked:
        if uploaded_file is None:
            st.error("Please upload a document before building the index.")
            st.toast("No file uploaded.", icon="⚠️")
        elif _overlap_invalid:
            st.error("Fix chunk overlap (must be less than chunk size) before building.")
        else:
            with st.spinner("Building index — please wait…"):
                try:
                    # Clear previous pipeline/store for a clean rebuild
                    if st.session_state.pipeline is not None:
                        try:
                            st.session_state.pipeline.clear()
                        except Exception:
                            pass

                    saved_path = _save_upload(uploaded_file)
                    _provider = create_embedding_provider(provider_name, model_name)
                    _store = create_vector_store(store_name)
                    _chunker = create_chunker(chunk_strategy, chunk_size, chunk_overlap)
                    _reranker = create_reranker(use_reranker)

                    from src.pipeline.rag_pipeline import RAGPipeline
                    _pipeline = RAGPipeline(_provider, _store, _chunker, _reranker)
                    _summary = _pipeline.build_index(saved_path, redact_pii=redact_pii)

                    st.session_state.pipeline = _pipeline
                    st.session_state.index_built = True
                    st.session_state.last_build_summary = _summary
                    st.session_state.built_with_config = _cfg
                    st.toast(
                        f"Index built! {_summary['chunks_created']} chunks.", icon="✅"
                    )

                except ValidationError as exc:
                    st.error(f"Validation error: {exc}")
                    METRICS.record_error(str(exc))
                    st.toast("Validation error — see Ingestion tab.", icon="❌")
                except RAGLabError as exc:
                    st.error(f"Pipeline error: {exc}")
                    st.toast("Build failed — see Ingestion tab.", icon="❌")
                except Exception as exc:
                    st.error(f"Unexpected error ({type(exc).__name__}): {exc}")
                    METRICS.record_error(str(exc))
                    st.toast("Build failed — see Ingestion tab.", icon="❌")

    # ── Build summary ──────────────────────────────────────────────────────
    if st.session_state.last_build_summary:
        _s = st.session_state.last_build_summary
        st.success("✅ Index is ready for querying.")
        st.subheader("Last Build Summary")
        _sc1, _sc2, _sc3 = st.columns(3)
        _sc1.metric("Doc ID", _s.get("doc_id", "—"))
        _sc2.metric("Chunks Created", _s.get("chunks_created", 0))
        _sc3.metric(
            "Provider / Store",
            f"{_s.get('embedding_provider','?')} / {_s.get('vector_store','?')}",
        )
        with st.expander("Source path"):
            st.code(_s.get("source", ""), language=None)
    elif not build_clicked:
        st.info(
            "Upload a document and click **🔨 Build Index** in the sidebar "
            "to start the ingestion pipeline."
        )

# ─────────────────────────────────────────────────────────────────────────
# Tab 2 — Retrieval Demo
# ─────────────────────────────────────────────────────────────────────────

with tab_retrieval:
    st.subheader("Retrieval Demo")
    st.caption(
        "Retrieve the most relevant document chunks for a natural-language query. "
        "No LLM generation — this project returns retrieved chunks only."
    )

    _query_input = st.text_area(
        "Query",
        placeholder="e.g. What chunking strategies are available?",
        height=90,
        key="query_input",
    )
    _run_retrieval = st.button("🔍 Run Retrieval", type="primary", key="btn_run_retrieval")

    if _run_retrieval:
        if not st.session_state.index_built or st.session_state.pipeline is None:
            st.warning("Build an index first (go to the **📥 Ingestion** tab).")
        elif not _query_input or not _query_input.strip():
            st.warning("Enter a non-empty query.")
        else:
            _safety = check_prompt_safety(_query_input)
            if _safety.is_suspicious:
                st.warning(
                    f"⚠️ {_safety.warning}  \n"
                    f"Matched: {', '.join(_safety.matched_patterns)}"
                )
            with st.spinner("Retrieving…"):
                try:
                    _chunks = st.session_state.pipeline.query(
                        _query_input.strip(), top_k
                    )
                    st.session_state.last_retrieval_results = _chunks
                except ValidationError as exc:
                    st.error(f"Validation error: {exc}")
                except RAGLabError as exc:
                    st.error(f"Retrieval error: {exc}")
                except Exception as exc:
                    st.error(f"Unexpected error: {exc}")
                    METRICS.record_error(str(exc))

    _ret_results = st.session_state.last_retrieval_results
    if _ret_results:
        st.success(f"Retrieved **{len(_ret_results)}** chunk(s).")
        for _chunk in _ret_results:
            _rank = _chunk.rank or "—"
            _score_str = f"{_chunk.score:.4f}" if _chunk.score is not None else "—"
            _src = _chunk.metadata.get("file_name") or _chunk.metadata.get("source", "")
            _hdr = f"Rank {_rank}  |  Score: {_score_str}  |  Doc: {_chunk.doc_id}"
            if _src:
                _hdr += f"  |  {os.path.basename(str(_src))}"
            with st.expander(_hdr, expanded=(_chunk.rank == 1)):
                st.caption(f"Chunk ID: `{_chunk.chunk_id}`")
                st.write(_chunk.text)
    elif _run_retrieval and st.session_state.index_built:
        st.info("No results returned for this query.")
    elif not st.session_state.index_built:
        st.info("Build an index first, then enter a query here.")

# ─────────────────────────────────────────────────────────────────────────
# Tab 3 — Evaluation
# ─────────────────────────────────────────────────────────────────────────

with tab_eval:
    st.subheader("Retrieval Evaluation")
    st.caption(
        "Score retrieval quality against the ground-truth question set using "
        "Recall@K, Precision@K, MRR, and nDCG@K."
    )

    _gt_path = os.path.join(settings.data_dir, "ground_truth", "questions.json")
    _ground_truth = None

    try:
        from src.evaluation.ground_truth_loader import load_ground_truth
        _ground_truth = load_ground_truth(_gt_path)
        st.info(
            f"📋 Loaded **{len(_ground_truth)}** ground-truth questions "
            f"from `{_gt_path}`."
        )
    except EvaluationError as exc:
        st.error(f"Could not load ground truth: {exc}")
    except Exception as exc:
        st.error(f"Unexpected error loading ground truth: {exc}")

    _run_eval = st.button("📊 Run Evaluation", type="primary", key="btn_run_eval")

    if _run_eval:
        if not st.session_state.index_built or st.session_state.pipeline is None:
            st.warning("Build an index first (go to the **📥 Ingestion** tab).")
        elif _ground_truth is None:
            st.error("Ground truth could not be loaded — cannot evaluate.")
        else:
            with st.spinner("Running evaluation…"):
                try:
                    from src.evaluation.evaluator import RetrievalEvaluator
                    _evaluator = RetrievalEvaluator(st.session_state.pipeline)
                    _eval_results, _eval_summary = _evaluator.evaluate(
                        _ground_truth, top_k=top_k
                    )
                    _csv_path = os.path.join(
                        settings.results_dir, "evaluation_results.csv"
                    )
                    _evaluator.save_results_csv(_eval_results, path=_csv_path)
                    st.session_state.last_evaluation_results = _eval_results
                    st.session_state.last_evaluation_summary = _eval_summary
                    st.toast("Evaluation complete.", icon="📊")
                except EvaluationError as exc:
                    st.error(f"Evaluation error: {exc}")
                except RAGLabError as exc:
                    st.error(f"Pipeline error: {exc}")
                except Exception as exc:
                    st.error(f"Unexpected error: {exc}")
                    METRICS.record_error(str(exc))

    _eval_summary = st.session_state.last_evaluation_summary
    _eval_results = st.session_state.last_evaluation_results

    if _eval_summary:
        st.success("Evaluation complete.")
        st.subheader("Summary Metrics")
        _em1, _em2, _em3, _em4 = st.columns(4)
        _em1.metric("Recall@K", f"{_eval_summary.get('avg_recall_at_k', 0):.4f}")
        _em2.metric("Precision@K", f"{_eval_summary.get('avg_precision_at_k', 0):.4f}")
        _em3.metric("MRR", f"{_eval_summary.get('avg_mrr', 0):.4f}")
        _em4.metric("nDCG@K", f"{_eval_summary.get('avg_ndcg_at_k', 0):.4f}")
        _eqa, _eqb = st.columns(2)
        _eqa.metric("Questions", _eval_summary.get("total_questions", 0))
        _eqb.metric("Errors", _eval_summary.get("error_count", 0))

    if _eval_results:
        st.subheader("Per-Question Results")
        try:
            import pandas as pd
            _df = pd.DataFrame([
                {
                    "Question": r["question"][:65] + ("…" if len(r["question"]) > 65 else ""),
                    "Recall@K":    round(r["recall_at_k"], 4),
                    "Precision@K": round(r["precision_at_k"], 4),
                    "MRR":         round(r["mrr"], 4),
                    "nDCG@K":      round(r["ndcg_at_k"], 4),
                    "Error":       r.get("error") or "",
                }
                for r in _eval_results
            ])
            st.dataframe(_df, use_container_width=True)
        except ImportError:
            for _r in _eval_results:
                st.write(
                    f"- {_r['question'][:65]}: "
                    f"recall={_r['recall_at_k']:.4f}, mrr={_r['mrr']:.4f}"
                )

        _csv_path = os.path.join(settings.results_dir, "evaluation_results.csv")
        if os.path.exists(_csv_path):
            with open(_csv_path, "rb") as _f:
                st.download_button(
                    label="⬇️ Download Results CSV",
                    data=_f,
                    file_name="evaluation_results.csv",
                    mime="text/csv",
                    key="btn_dl_csv",
                )

    elif not _run_eval:
        st.info(
            "Click **📊 Run Evaluation** to score retrieval quality against "
            "the ground-truth questions."
        )

# ─────────────────────────────────────────────────────────────────────────
# Tab 4 — System Status
# ─────────────────────────────────────────────────────────────────────────

with tab_status:
    st.subheader("System Status")

    _sc1, _sc2 = st.columns(2)

    with _sc1:
        st.subheader("Active Configuration")
        st.metric("Embedding Provider", provider_name)
        _model_display = model_name if len(model_name) <= 38 else model_name[:35] + "…"
        st.metric("Embedding Model", _model_display)
        st.metric("Vector Store", store_name)
        st.metric("Chunking Strategy", chunk_strategy)
        st.metric("Chunk Size", chunk_size)
        st.metric("Chunk Overlap", chunk_overlap)
        st.metric("Top-K", top_k)
        st.metric("Mock Mode", "ON" if mock_mode else "OFF")
        st.metric("Reranker", "ON (PassThrough)" if use_reranker else "OFF")
        st.metric("PII Redaction", "ON" if redact_pii else "OFF")

    with _sc2:
        st.subheader("Pipeline State")
        _idx_label = "✅ READY" if st.session_state.index_built else "⏳ NOT BUILT"
        st.metric("Index Status", _idx_label)
        if st.session_state.last_build_summary:
            _bs2 = st.session_state.last_build_summary
            st.metric("Last Doc ID", _bs2.get("doc_id", "—"))
            st.metric("Last Chunks", _bs2.get("chunks_created", 0))

        st.subheader("Observability Metrics")
        _m = METRICS.to_dict()
        st.metric("Documents Loaded", _m["documents_loaded_total"])
        st.metric("Chunks Created",   _m["chunks_created_total"])
        st.metric("Queries Run",      _m["query_count_total"])
        st.metric("Errors",           _m["error_count_total"])
        st.metric("Embed Latency (s)",    f"{_m['embedding_latency_seconds']:.4f}")
        st.metric("Retrieval Latency (s)", f"{_m['retrieval_latency_seconds']:.4f}")
        st.metric("Rerank Latency (s)",    f"{_m['rerank_latency_seconds']:.4f}")
        if _m["last_error"]:
            st.error(f"Last Error: {_m['last_error'][:120]}")
        else:
            st.caption("No errors recorded.")

    st.divider()
    st.subheader("Health Check")
    _health = check_health(settings)
    _overall_icon = "✅" if _health.healthy else "⚠️"
    st.write(f"**Overall**: {_overall_icon} {'Healthy' if _health.healthy else 'Degraded'}")

    _hcheck_keys = [k for k in _health.checks]
    _hcols = st.columns(min(len(_hcheck_keys), 4))
    for _hi, _hk in enumerate(_hcheck_keys):
        _icon = "✅" if _health.checks[_hk] else "❌"
        _hcols[_hi % len(_hcols)].metric(
            f"{_icon} {_hk}",
            _health.details.get(_hk, "—"),
        )
