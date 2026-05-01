from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List

from src.core.exceptions import EvaluationError

_DEFAULT_PATH = os.path.join("data", "ground_truth", "questions.json")


@dataclass
class GroundTruthEntry:
    """
    A single ground-truth evaluation entry with support for multiple relevant
    document IDs.

    Extends the EvaluationQuestion DTO pattern from src/core/contracts.py to
    support both single-ID ("relevant_doc_id") and multi-ID ("relevant_doc_ids")
    JSON formats. Internally always represented as a list.
    """

    question: str
    expected_answer: str
    relevant_doc_ids: List[str] = field(default_factory=list)


def load_ground_truth(path: str = _DEFAULT_PATH) -> List[GroundTruthEntry]:
    """
    Load evaluation questions from a JSON file.

    Supports two relevant-ID formats per entry:
      - "relevant_doc_id":  "doc_001"          (string — normalised to a one-item list)
      - "relevant_doc_ids": ["doc_001", "doc_002"]  (list — used as-is)

    Raises EvaluationError for missing file, invalid JSON, or malformed entries.
    """
    if not os.path.exists(path):
        raise EvaluationError(
            f"Ground truth file not found: '{path}'. "
            "Create it at data/ground_truth/questions.json or pass an explicit path."
        )

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise EvaluationError(
            f"Invalid JSON in ground truth file '{path}': {exc}"
        ) from exc
    except OSError as exc:
        raise EvaluationError(
            f"Could not read ground truth file '{path}': {exc}"
        ) from exc

    if not isinstance(data, list):
        raise EvaluationError(
            f"Ground truth file must contain a JSON array at the top level, "
            f"got {type(data).__name__}."
        )

    entries: List[GroundTruthEntry] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise EvaluationError(
                f"Entry {i} in '{path}' is not a JSON object."
            )

        question = item.get("question")
        expected_answer = item.get("expected_answer")

        if not question or not str(question).strip():
            raise EvaluationError(
                f"Entry {i} in '{path}' is missing a non-empty 'question'."
            )
        if not expected_answer or not str(expected_answer).strip():
            raise EvaluationError(
                f"Entry {i} in '{path}' is missing a non-empty 'expected_answer'."
            )

        # Normalise relevant IDs to a list
        if "relevant_doc_ids" in item:
            relevant_doc_ids = item["relevant_doc_ids"]
            if not isinstance(relevant_doc_ids, list):
                raise EvaluationError(
                    f"Entry {i} in '{path}': 'relevant_doc_ids' must be a JSON array, "
                    f"got {type(relevant_doc_ids).__name__}."
                )
            if not relevant_doc_ids:
                raise EvaluationError(
                    f"Entry {i} in '{path}': 'relevant_doc_ids' must not be empty."
                )
        elif "relevant_doc_id" in item:
            single = item["relevant_doc_id"]
            if not isinstance(single, str) or not single.strip():
                raise EvaluationError(
                    f"Entry {i} in '{path}': 'relevant_doc_id' must be a non-empty string."
                )
            relevant_doc_ids = [single]
        else:
            raise EvaluationError(
                f"Entry {i} in '{path}' must contain either 'relevant_doc_id' "
                "(string) or 'relevant_doc_ids' (array)."
            )

        entries.append(
            GroundTruthEntry(
                question=str(question).strip(),
                expected_answer=str(expected_answer).strip(),
                relevant_doc_ids=relevant_doc_ids,
            )
        )

    return entries
