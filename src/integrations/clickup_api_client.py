"""
ClickUp API v2 read-only client.

Fetches tasks from configured ClickUp lists when CLICKUP_API_TOKEN is set.
Returns [] / None gracefully when credentials are absent — the app continues
in mock/demo mode without crashing.

Write operations (post_review_comment, set_risk_label, update_task_status)
are intentionally not implemented. Phase 2 (HITL write-back) only.
See docs/future_clickup_integration.md for the write-back plan.
"""
from __future__ import annotations
import os

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _requests = None  # type: ignore[assignment]
    _HAS_REQUESTS = False

_BASE_URL = "https://api.clickup.com/api/v2"

_LIST_ENV_KEYS = [
    "CLICKUP_LIST_BACKLOG_REQUIREMENTS_ID",
    "CLICKUP_LIST_SDLC_RISK_REVIEW_ID",
    "CLICKUP_LIST_QA_DOD_VALIDATION_ID",
    "CLICKUP_LIST_GOVERNANCE_HITL_ID",
    "CLICKUP_LIST_DEMO_DASHBOARD_ID",
]


class ClickUpApiClient:
    """Read-only ClickUp API v2 client.

    When CLICKUP_API_TOKEN is set: fetches live tasks from ClickUp.
    When unconfigured: fetch_tasks() returns [] and fetch_task_by_id() returns None.

    Write operations raise NotImplementedError — Phase 2 (HITL) only.
    The token is never printed, logged, or included in error messages.
    """

    def __init__(
        self,
        api_token: str | None = None,
        list_id: str | None = None,
        list_ids: list[str] | None = None,
    ):
        # Kept as internal attribute; never surfaces in repr/str
        self._token = api_token or os.environ.get("CLICKUP_API_TOKEN") or ""
        # list_id (singular) kept for backward compat; list_ids takes precedence
        if list_ids is not None:
            self._list_ids = list_ids
        elif list_id is not None:
            self._list_ids = [list_id]
        else:
            self._list_ids = _configured_list_ids()

    def _is_configured(self) -> bool:
        return bool(self._token) and bool(self._list_ids) and _HAS_REQUESTS

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": self._token}

    # ── Read-only operations ────────────────────────────────────────────────

    def fetch_tasks(self) -> list[dict]:
        """Fetch all tasks from configured ClickUp lists.

        Returns [] when CLICKUP_API_TOKEN is not set, no list IDs are configured,
        or the 'requests' package is not installed.
        Raises RuntimeError (token-safe message) on API errors.
        """
        if not self._is_configured():
            return []
        tasks: list[dict] = []
        for list_id in self._list_ids:
            tasks.extend(self._fetch_list_tasks(list_id))
        return tasks

    def _fetch_list_tasks(self, list_id: str) -> list[dict]:
        resp = _requests.get(  # type: ignore[union-attr]
            f"{_BASE_URL}/list/{list_id}/task",
            headers=self._headers,
            timeout=10,
        )
        if not resp.ok:
            raise RuntimeError(
                f"ClickUp API error fetching list {list_id}: HTTP {resp.status_code}"
            )
        return [_map_task(t) for t in resp.json().get("tasks", [])]

    def fetch_task_by_id(self, task_id: str) -> dict | None:
        """Fetch a single task by ClickUp task ID.

        Returns None when unconfigured or when the task is not found (HTTP 404).
        Raises RuntimeError (token-safe message) on other API errors.
        """
        if not self._is_configured():
            return None
        resp = _requests.get(  # type: ignore[union-attr]
            f"{_BASE_URL}/task/{task_id}",
            headers=self._headers,
            timeout=10,
        )
        if resp.status_code == 404:
            return None
        if not resp.ok:
            raise RuntimeError(
                f"ClickUp API error fetching task {task_id}: HTTP {resp.status_code}"
            )
        return _map_task(resp.json())

    # ── Write operations — Phase 2 (HITL) only ─────────────────────────────

    def post_review_comment(self, task_id: str, comment: str) -> None:
        """Post a risk review comment to a ClickUp task.
        Not implemented — Phase 2 (HITL write-back) only.
        """
        raise NotImplementedError(
            "Write-back not implemented in Phase 1. "
            "See docs/future_clickup_integration.md for the HITL plan."
        )

    def set_risk_label(self, task_id: str, risk_level: str) -> None:
        """Apply a risk-level tag to a ClickUp task.
        Not implemented — Phase 2 (HITL write-back) only.
        """
        raise NotImplementedError(
            "Write-back not implemented in Phase 1."
        )

    def update_task_status(self, task_id: str, new_status: str) -> None:
        """Update a ClickUp task's status.
        Not implemented — Phase 2 (HITL write-back) only.
        """
        raise NotImplementedError(
            "Write-back not implemented in Phase 1."
        )


# ── Module-level helpers ────────────────────────────────────────────────────

def _configured_list_ids() -> list[str]:
    """Return all non-empty ClickUp list IDs found in environment variables."""
    return [os.environ[k] for k in _LIST_ENV_KEYS if os.environ.get(k)]


def _map_task(raw: dict) -> dict:
    """Map a ClickUp API v2 task response to the standard internal task schema."""
    custom = {cf["name"]: cf.get("value") for cf in raw.get("custom_fields") or []}
    priority_raw = raw.get("priority")
    priority = priority_raw["priority"] if isinstance(priority_raw, dict) else "none"
    assignees = raw.get("assignees") or []
    assignee = assignees[0].get("username", "Unassigned") if assignees else "Unassigned"
    status_raw = raw.get("status") or {}
    status = status_raw.get("status", "unknown") if isinstance(status_raw, dict) else str(status_raw)
    return {
        "task_id": raw.get("id", ""),
        "title": raw.get("name", ""),
        "description": raw.get("description", ""),
        "status": status,
        "priority": priority,
        "assignee": assignee,
        "sprint": custom.get("Sprint", ""),
        "tags": [t["name"] for t in raw.get("tags") or []],
        "acceptance_criteria": custom.get("Acceptance Criteria"),
        "definition_of_done_status": custom.get("DoD Status"),
        "security_notes": custom.get("Security Notes"),
        "architecture_notes": custom.get("Architecture Notes"),
        "qa_notes": custom.get("QA Notes"),
        "dependencies": [d.get("task_id", "") for d in raw.get("dependencies") or []],
        "due_date": raw.get("due_date"),
    }
