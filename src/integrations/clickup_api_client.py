"""
ClickUp API client — future placeholder only.

Real integration is intentionally not active in this version.
All methods raise NotImplementedError until real integration is explicitly enabled.

To activate:
  1. Set CLICKUP_API_TOKEN in environment variables (never commit it)
  2. Implement fetch_tasks() using GET https://api.clickup.com/api/v2/list/{list_id}/task
  3. Implement fetch_task_by_id() using GET https://api.clickup.com/api/v2/task/{task_id}
  4. Map ClickUp custom fields to the standard task schema
  5. See docs/FUTURE_CLICKUP_API_READINESS.md for the full integration plan

Default app behavior continues to use MockTaskClient via src/core/clickup_adapter.py.
"""
from __future__ import annotations


class ClickUpApiClient:
    """Future-ready ClickUp API adapter. Not active — all methods raise NotImplementedError."""

    def __init__(self, api_token: str | None = None, list_id: str | None = None):
        self.api_token = api_token
        self.list_id = list_id

    def fetch_tasks(self) -> list[dict]:
        """Fetch tasks from a real ClickUp list via the v2 API."""
        raise NotImplementedError(
            "ClickUp API integration is not yet active. "
            "Set CLICKUP_API_TOKEN and implement this method. "
            "See docs/FUTURE_CLICKUP_API_READINESS.md for the integration plan."
        )

    def fetch_task_by_id(self, task_id: str) -> dict | None:
        """Fetch a single ClickUp task by ID via the v2 API."""
        raise NotImplementedError(
            "ClickUp API integration is not yet active. "
            "See docs/FUTURE_CLICKUP_API_READINESS.md for the integration plan."
        )

    def post_review_comment(self, task_id: str, comment: str) -> None:
        """Post an AI risk review summary as a ClickUp task comment.

        Only call this after a human has reviewed and approved the AI output.
        Maps to: POST /api/v2/task/{task_id}/comment
        """
        raise NotImplementedError("ClickUp API integration not yet active.")

    def set_risk_label(self, task_id: str, risk_level: str) -> None:
        """Apply a risk-level tag (e.g., 'risk-high') to a ClickUp task.

        Maps to: POST /api/v2/task/{task_id}/tag/risk-{level}
        """
        raise NotImplementedError("ClickUp API integration not yet active.")

    def update_task_status(self, task_id: str, new_status: str) -> None:
        """Update a ClickUp task status (e.g., to reflect gate outcome).

        Maps to: PUT /api/v2/task/{task_id}
        """
        raise NotImplementedError("ClickUp API integration not yet active.")
