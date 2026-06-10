"""
ClickUp adapter — currently loads local mock data.
Designed so the same interface can later connect to the real ClickUp API.
"""
from __future__ import annotations
import json
import os
from typing import Any

# TODO (ClickUp API integration):
#   1. Add CLICKUP_API_TOKEN to environment variables
#   2. Replace _load_json() calls with requests to https://api.clickup.com/api/v2/
#   3. Map ClickUp custom fields to the task schema used here
#   4. Support pulling tasks from a specific List, Folder, or Space
#   5. Implement post_review_comment(task_id, comment) to write findings back
#   6. Implement set_risk_label(task_id, label) to tag tasks with risk level
#   7. Implement update_task_status(task_id, status) to gate tasks at review
#   8. Cache API responses locally to avoid rate-limit issues during demos

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "clickup_demo")


def _load_json(filename: str) -> Any:
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_tasks() -> list[dict]:
    """Load mock ClickUp tasks from local JSON. Replace with API call in production."""
    return _load_json("tasks.json")


def load_policies() -> dict:
    """Load risk policies and thresholds."""
    return _load_json("policies.json")


def load_definition_of_done() -> dict:
    """Load the project Definition of Done checklist."""
    return _load_json("definition_of_done.json")


def load_architecture_guidelines() -> dict:
    """Load architecture review guidelines."""
    return _load_json("architecture_guidelines.json")


def get_task_by_id(task_id: str) -> dict | None:
    """Return a single task by ID, or None if not found."""
    tasks = load_tasks()
    for task in tasks:
        if task.get("task_id") == task_id:
            return task
    return None


# TODO: implement these when connecting to real ClickUp API
def post_review_comment(task_id: str, comment: str) -> None:
    """Post a risk review summary as a ClickUp task comment."""
    # TODO: POST /api/v2/task/{task_id}/comment
    raise NotImplementedError("ClickUp API integration not yet enabled. Set CLICKUP_API_TOKEN.")


def set_risk_label(task_id: str, risk_level: str) -> None:
    """Apply a risk label tag to a ClickUp task."""
    # TODO: PUT /api/v2/task/{task_id} with tag: risk-{level}
    raise NotImplementedError("ClickUp API integration not yet enabled.")


def update_task_status(task_id: str, new_status: str) -> None:
    """Update a ClickUp task status (e.g., block it at the risk gate)."""
    # TODO: PUT /api/v2/task/{task_id} with status field
    raise NotImplementedError("ClickUp API integration not yet enabled.")
