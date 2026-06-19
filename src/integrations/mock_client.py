"""Mock task client — returns local demo data.

Used by default in all demo and test runs. No credentials required.
Delegates to the existing clickup_adapter JSON loader.
"""
from __future__ import annotations
from src.core.clickup_adapter import load_tasks, get_task_by_id


class MockTaskClient:
    """Implements TaskClient using local ClickUp-style JSON demo data."""

    def fetch_tasks(self) -> list[dict]:
        """Return all mock tasks from data/clickup_demo/tasks.json."""
        return load_tasks()

    def fetch_task_by_id(self, task_id: str) -> dict | None:
        """Return a single mock task by ID, or None if not found."""
        return get_task_by_id(task_id)
