"""Tests for the integration adapter layer (base protocol, mock client, API placeholder)."""
import pytest
from src.integrations.base import TaskClient
from src.integrations.mock_client import MockTaskClient
from src.integrations.clickup_api_client import ClickUpApiClient


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


class TestClickUpApiClient:
    def test_fetch_tasks_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            ClickUpApiClient().fetch_tasks()

    def test_fetch_task_by_id_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            ClickUpApiClient().fetch_task_by_id("TASK-001")

    def test_post_review_comment_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            ClickUpApiClient().post_review_comment("TASK-001", "Risk: high")

    def test_set_risk_label_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            ClickUpApiClient().set_risk_label("TASK-001", "high")

    def test_update_task_status_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            ClickUpApiClient().update_task_status("TASK-001", "needs-review")
