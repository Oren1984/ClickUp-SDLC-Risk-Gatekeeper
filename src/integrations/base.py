"""Base protocol for task data clients.

Any adapter that fetches tasks for the risk engine must satisfy this protocol.
Both MockTaskClient and ClickUpApiClient implement it.
"""
from __future__ import annotations
from typing import Protocol, runtime_checkable


@runtime_checkable
class TaskClient(Protocol):
    """Protocol that all task data adapters must satisfy."""

    def fetch_tasks(self) -> list[dict]:
        """Return a list of task dicts in the standard schema."""
        ...

    def fetch_task_by_id(self, task_id: str) -> dict | None:
        """Return a single task by ID, or None if not found."""
        ...
