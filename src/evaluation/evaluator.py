from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

from src.core.exceptions import EvaluationError
from src.evaluation.ground_truth_loader import GroundTruthEntry
from src.evaluation.metrics import mrr, ndcg_at_k, precision_at_k, recall_at_k

_DEFAULT_RESULTS_PATH = os.path.join("results", "evaluation_results.csv")


class RetrievalEvaluator:
    """
    Evaluates retrieval quality against a set of ground-truth questions.

    Accepts any object that exposes query(query_text: str, top_k: int) -> List[Chunk].
    This is satisfied by RAGPipeline and Retriever alike.

    Scoring is doc_id-based: each retrieved chunk's doc_id is compared against
    the relevant_doc_ids for the question. This is v1 behaviour — chunk_id-level
    matching can be added later without changing the metric functions.
    """

    def __init__(self, pipeline: Any) -> None:
        if not callable(getattr(pipeline, "query", None)):
            raise EvaluationError(
                "The pipeline object must expose a query(query_text, top_k) method."
            )
        self._pipeline = pipeline

    # ------------------------------------------------------------------
    # Main evaluation entry point
    # ------------------------------------------------------------------

    def evaluate(
        self,
        ground_truth: List[GroundTruthEntry],
        top_k: int = 5,
    ) -> Tuple[List[Dict], Dict]:
        """
        Run retrieval for every ground-truth entry and compute metrics.

        Returns:
            results  -- list of per-question result dicts
            summary  -- dict of averaged metrics across all questions
        """
        if not ground_truth:
            raise EvaluationError("Ground truth list is empty.")

        results: List[Dict] = []
        for entry in ground_truth:
            row = self._evaluate_one(entry, top_k)
            results.append(row)

        summary = self._summarise(results)
        return results, summary

    # ------------------------------------------------------------------
    # Optional output helpers
    # ------------------------------------------------------------------

    def to_dataframe(self, results: List[Dict]):
        """
        Convert results to a pandas DataFrame.

        Raises ImportError if pandas is not installed (it is in requirements.txt).
        """
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError(
                "pandas is required for to_dataframe(). "
                "Install it with: pip install pandas"
            ) from exc
        return pd.DataFrame(results)

    def save_results_csv(
        self,
        results: List[Dict],
        path: str = _DEFAULT_RESULTS_PATH,
    ) -> None:
        """
        Save evaluation results to a CSV file, creating parent directories as needed.

        List-valued columns (relevant_doc_ids, retrieved_doc_ids, retrieved_chunk_ids)
        are serialised as pipe-separated strings for readability.
        """
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        # Flatten list fields for CSV compatibility
        flat_results = [_flatten_row(r) for r in results]

        try:
            import pandas as pd
            pd.DataFrame(flat_results).to_csv(path, index=False, encoding="utf-8")
        except ImportError:
            import csv
            with open(path, "w", newline="", encoding="utf-8") as f:
                if not flat_results:
                    return
                writer = csv.DictWriter(f, fieldnames=flat_results[0].keys())
                writer.writeheader()
                writer.writerows(flat_results)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _evaluate_one(self, entry: GroundTruthEntry, top_k: int) -> Dict:
        try:
            chunks = self._pipeline.query(entry.question, top_k)

            # Doc-id-level matching: use chunk.doc_id for scoring.
            # chunk.metadata may also carry "doc_id" as a fallback.
            retrieved_doc_ids = [
                c.doc_id or c.metadata.get("doc_id", "")
                for c in chunks
            ]
            retrieved_chunk_ids = [c.chunk_id for c in chunks]

            # Deduplicate doc_ids by first occurrence before computing metrics.
            # nDCG (and the other rank-based metrics) assume each item appears
            # at most once in the ranked list. Without deduplication, multiple
            # chunks from the same document would inflate DCG above IDCG.
            scored_doc_ids = _deduplicate_ordered(retrieved_doc_ids)

            return {
                "question": entry.question,
                "expected_answer": entry.expected_answer,
                "relevant_doc_ids": entry.relevant_doc_ids,
                "retrieved_doc_ids": retrieved_doc_ids,
                "retrieved_chunk_ids": retrieved_chunk_ids,
                "recall_at_k": recall_at_k(entry.relevant_doc_ids, scored_doc_ids, top_k),
                "precision_at_k": precision_at_k(entry.relevant_doc_ids, scored_doc_ids, top_k),
                "mrr": mrr(entry.relevant_doc_ids, scored_doc_ids),
                "ndcg_at_k": ndcg_at_k(entry.relevant_doc_ids, scored_doc_ids, top_k),
                "top_k": top_k,
                "error": None,
            }

        except Exception as exc:
            return {
                "question": entry.question,
                "expected_answer": entry.expected_answer,
                "relevant_doc_ids": entry.relevant_doc_ids,
                "retrieved_doc_ids": [],
                "retrieved_chunk_ids": [],
                "recall_at_k": 0.0,
                "precision_at_k": 0.0,
                "mrr": 0.0,
                "ndcg_at_k": 0.0,
                "top_k": top_k,
                "error": str(exc),
            }

    @staticmethod
    def _summarise(results: List[Dict]) -> Dict:
        n = len(results)
        if n == 0:
            return {
                "total_questions": 0,
                "avg_recall_at_k": 0.0,
                "avg_precision_at_k": 0.0,
                "avg_mrr": 0.0,
                "avg_ndcg_at_k": 0.0,
                "error_count": 0,
            }
        return {
            "total_questions": n,
            "avg_recall_at_k": round(
                sum(r["recall_at_k"] for r in results) / n, 4
            ),
            "avg_precision_at_k": round(
                sum(r["precision_at_k"] for r in results) / n, 4
            ),
            "avg_mrr": round(
                sum(r["mrr"] for r in results) / n, 4
            ),
            "avg_ndcg_at_k": round(
                sum(r["ndcg_at_k"] for r in results) / n, 4
            ),
            "error_count": sum(1 for r in results if r["error"] is not None),
        }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _deduplicate_ordered(ids: List[str]) -> List[str]:
    """Return ids with duplicates removed, preserving first-occurrence order."""
    seen: set = set()
    result: List[str] = []
    for item in ids:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _flatten_row(row: Dict) -> Dict:
    """Convert list-valued fields to pipe-separated strings for CSV output."""
    out = dict(row)
    for key in ("relevant_doc_ids", "retrieved_doc_ids", "retrieved_chunk_ids"):
        if isinstance(out.get(key), list):
            out[key] = "|".join(str(x) for x in out[key])
    return out
