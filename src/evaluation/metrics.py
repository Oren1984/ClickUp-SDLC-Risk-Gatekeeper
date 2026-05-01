from __future__ import annotations

import math
from typing import List


def recall_at_k(
    relevant_ids: List[str],
    retrieved_ids: List[str],
    k: int,
) -> float:
    """
    Fraction of relevant IDs that appear in the top-k retrieved IDs.

    Returns 0.0 when relevant_ids or retrieved_ids is empty, or when k <= 0.
    For a single-relevant-document setup this is equivalent to binary hit@k.
    """
    if not relevant_ids or not retrieved_ids or k <= 0:
        return 0.0
    top_k_set = set(retrieved_ids[:k])
    hits = sum(1 for rid in relevant_ids if rid in top_k_set)
    return hits / len(relevant_ids)


def precision_at_k(
    relevant_ids: List[str],
    retrieved_ids: List[str],
    k: int,
) -> float:
    """
    Fraction of the top-k retrieved IDs that are relevant.

    Returns 0.0 when retrieved_ids is empty, relevant_ids is empty, or k <= 0.
    Denominator is always k (not the number of retrieved results).
    """
    if not relevant_ids or not retrieved_ids or k <= 0:
        return 0.0
    relevant_set = set(relevant_ids)
    top_k = retrieved_ids[:k]
    hits = sum(1 for rid in top_k if rid in relevant_set)
    return hits / k


def mrr(
    relevant_ids: List[str],
    retrieved_ids: List[str],
) -> float:
    """
    Reciprocal Rank of the first relevant result in retrieved_ids.

    Returns 1/rank_of_first_relevant, or 0.0 if no relevant result is found.
    """
    if not relevant_ids or not retrieved_ids:
        return 0.0
    relevant_set = set(relevant_ids)
    for rank, rid in enumerate(retrieved_ids, start=1):
        if rid in relevant_set:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(
    relevant_ids: List[str],
    retrieved_ids: List[str],
    k: int,
) -> float:
    """
    Normalised Discounted Cumulative Gain at k with binary relevance.

    DCG  = sum(rel_i / log2(i+1)) for i in 1..k  (rel_i in {0, 1})
    IDCG = DCG for the ideal ordering (all relevant docs ranked first).
    nDCG = DCG / IDCG

    Returns 0.0 when relevant_ids or retrieved_ids is empty, or k <= 0.
    """
    if not relevant_ids or not retrieved_ids or k <= 0:
        return 0.0
    relevant_set = set(relevant_ids)
    top_k = retrieved_ids[:k]

    dcg = sum(
        1.0 / math.log2(i + 1)
        for i, rid in enumerate(top_k, start=1)
        if rid in relevant_set
    )

    # Ideal: all min(|relevant|, k) relevant docs ranked first
    ideal_hits = min(len(relevant_ids), k)
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, ideal_hits + 1))

    return dcg / idcg if idcg > 0.0 else 0.0
