"""Tests for the integration adapter layer (base protocol, mock client, read-only API client)."""
from __future__ import annotations
import pytest
from unittest.mock import patch, MagicMock

from src.integrations.base import TaskClient
from src.integrations.mock_client import MockTaskClient
from src.integrations.clickup_api_client import ClickUpApiClient, _map_task


# ── Mock client tests ───────────────────────────────────────────────────────

class TestMockTaskClient:
    def test_implements_task_client_protocol(self):
        assert isinstance(MockTaskClient(), TaskClient)

    def test_fetch_tasks_returns_list(self):
        tasks = MockTaskClient().fetch_tasks()
        assert isinstance(tasks, list)
        assert len(tasks) >= 1

    def test_fetch_tasks_have_required_fields(self):
        for task in MockTaskClient().fetch_tasks():
            assert "task_id" in task
            assert "title" in task

    def test_fetch_task_by_id_found(self):
        task = MockTaskClient().fetch_task_by_id("TASK-001")
        assert task is not None
        assert task["task_id"] == "TASK-001"

    def test_fetch_task_by_id_not_found(self):
        assert MockTaskClient().fetch_task_by_id("TASK-NONEXISTENT") is None


# ── Real API client tests ───────────────────────────────────────────────────

class TestClickUpApiClientUnconfigured:
    """Tests that verify safe behavior when credentials are absent."""

    def test_fetch_tasks_returns_empty_without_token(self):
        client = ClickUpApiClient(api_token="", list_ids=["list-123"])
        assert client.fetch_tasks() == []

    def test_fetch_tasks_returns_empty_without_list_ids(self):
        client = ClickUpApiClient(api_token="fake-token", list_ids=[])
        assert client.fetch_tasks() == []

    def test_fetch_tasks_returns_empty_with_no_args_and_no_env(self, monkeypatch):
        monkeypatch.delenv("CLICKUP_API_TOKEN", raising=False)
        monkeypatch.delenv("CLICKUP_LIST_BACKLOG_REQUIREMENTS_ID", raising=False)
        client = ClickUpApiClient()
        assert client.fetch_tasks() == []

    def test_fetch_task_by_id_returns_none_without_token(self):
        client = ClickUpApiClient(api_token="", list_ids=["list-123"])
        assert client.fetch_task_by_id("some-task-id") is None

    def test_missing_token_does_not_crash(self):
        client = ClickUpApiClient(api_token=None)
        result = client.fetch_tasks()
        assert result == []


class TestClickUpApiClientWriteOpsBlocked:
    """Write operations must raise NotImplementedError — Phase 2 only."""

    def test_post_review_comment_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            ClickUpApiClient().post_review_comment("TASK-001", "Risk: high")

    def test_set_risk_label_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            ClickUpApiClient().set_risk_label("TASK-001", "high")

    def test_update_task_status_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            ClickUpApiClient().update_task_status("TASK-001", "needs-review")


class TestClickUpApiClientTokenSafety:
    """Token must never appear in repr, str, or error messages."""

    def test_token_not_in_repr(self):
        secret = "secret-token-must-not-leak"
        client = ClickUpApiClient(api_token=secret)
        assert secret not in repr(client)

    def test_token_not_in_str(self):
        secret = "secret-token-must-not-leak"
        client = ClickUpApiClient(api_token=secret)
        assert secret not in str(client)

    def test_api_error_message_does_not_contain_token(self):
        secret = "very-secret-token-xyz"
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 401

        with patch("src.integrations.clickup_api_client._requests.get", return_value=mock_resp):
            client = ClickUpApiClient(api_token=secret, list_ids=["list-123"])
            try:
                client.fetch_tasks()
            except RuntimeError as exc:
                assert secret not in str(exc)


class TestClickUpApiClientMockResponse:
    """Tests using mocked HTTP responses to verify mapping and error handling."""

    def _make_raw_task(self, **overrides) -> dict:
        base = {
            "id": "cu-task-abc",
            "name": "Implement OAuth2 login",
            "description": "Add Google SSO support",
            "status": {"status": "in progress"},
            "priority": {"priority": "high"},
            "assignees": [{"username": "alice"}],
            "tags": [{"name": "security"}, {"name": "auth"}],
            "custom_fields": [
                {"name": "Sprint", "value": "Sprint 4"},
                {"name": "Acceptance Criteria", "value": "User can log in with Google"},
                {"name": "QA Notes", "value": "Test OAuth flow end-to-end"},
                {"name": "Security Notes", "value": "Use PKCE; validate redirect URIs"},
                {"name": "Architecture Notes", "value": None},
                {"name": "DoD Status", "value": "incomplete"},
            ],
            "dependencies": [],
            "due_date": "1735689600000",
        }
        base.update(overrides)
        return base

    def test_fetch_tasks_returns_mapped_tasks(self):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"tasks": [self._make_raw_task()]}

        with patch("src.integrations.clickup_api_client._requests.get", return_value=mock_resp):
            client = ClickUpApiClient(api_token="test-token", list_ids=["list-123"])
            tasks = client.fetch_tasks()

        assert len(tasks) == 1
        task = tasks[0]
        assert task["task_id"] == "cu-task-abc"
        assert task["title"] == "Implement OAuth2 login"
        assert task["status"] == "in progress"
        assert task["priority"] == "high"
        assert task["assignee"] == "alice"
        assert task["sprint"] == "Sprint 4"
        assert "security" in task["tags"]
        assert task["acceptance_criteria"] == "User can log in with Google"
        assert task["qa_notes"] == "Test OAuth flow end-to-end"
        assert task["security_notes"] == "Use PKCE; validate redirect URIs"
        assert task["architecture_notes"] is None

    def test_fetch_task_by_id_returns_mapped_task(self):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_resp.json.return_value = self._make_raw_task()

        with patch("src.integrations.clickup_api_client._requests.get", return_value=mock_resp):
            client = ClickUpApiClient(api_token="test-token", list_ids=["list-123"])
            task = client.fetch_task_by_id("cu-task-abc")

        assert task is not None
        assert task["task_id"] == "cu-task-abc"

    def test_fetch_task_by_id_returns_none_on_404(self):
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 404

        with patch("src.integrations.clickup_api_client._requests.get", return_value=mock_resp):
            client = ClickUpApiClient(api_token="test-token", list_ids=["list-123"])
            result = client.fetch_task_by_id("nonexistent-task")

        assert result is None

    def test_fetch_tasks_api_error_raises_runtime_error(self):
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 503

        with patch("src.integrations.clickup_api_client._requests.get", return_value=mock_resp):
            client = ClickUpApiClient(api_token="test-token", list_ids=["list-123"])
            with pytest.raises(RuntimeError, match="HTTP 503"):
                client.fetch_tasks()

    def test_fetch_tasks_empty_list_response(self):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"tasks": []}

        with patch("src.integrations.clickup_api_client._requests.get", return_value=mock_resp):
            client = ClickUpApiClient(api_token="test-token", list_ids=["list-123"])
            assert client.fetch_tasks() == []

    def test_fetch_tasks_aggregates_multiple_lists(self):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"tasks": [self._make_raw_task()]}

        with patch("src.integrations.clickup_api_client._requests.get", return_value=mock_resp):
            client = ClickUpApiClient(api_token="test-token", list_ids=["list-1", "list-2"])
            tasks = client.fetch_tasks()

        assert len(tasks) == 2  # one task from each list


# ── _map_task unit tests ────────────────────────────────────────────────────

class TestMapTask:
    def test_maps_basic_fields(self):
        raw = {
            "id": "t1",
            "name": "Task One",
            "description": "A description",
            "status": {"status": "open"},
            "priority": {"priority": "medium"},
            "assignees": [{"username": "bob"}],
            "tags": [],
            "custom_fields": [],
            "dependencies": [],
        }
        result = _map_task(raw)
        assert result["task_id"] == "t1"
        assert result["title"] == "Task One"
        assert result["status"] == "open"
        assert result["priority"] == "medium"
        assert result["assignee"] == "bob"

    def test_handles_missing_priority(self):
        raw = {"id": "t2", "name": "T2", "priority": None, "assignees": [], "tags": [],
               "custom_fields": [], "dependencies": []}
        result = _map_task(raw)
        assert result["priority"] == "none"

    def test_handles_missing_assignees(self):
        raw = {"id": "t3", "name": "T3", "assignees": [], "tags": [],
               "custom_fields": [], "dependencies": []}
        result = _map_task(raw)
        assert result["assignee"] == "Unassigned"

    def test_handles_none_fields(self):
        raw = {"id": "t4", "name": "T4", "tags": None, "assignees": None,
               "custom_fields": None, "dependencies": None}
        result = _map_task(raw)
        assert result["tags"] == []
        assert result["assignee"] == "Unassigned"
        assert result["dependencies"] == []
