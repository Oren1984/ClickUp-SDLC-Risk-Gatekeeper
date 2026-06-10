"""Tests for the ClickUp adapter (mock data loading)."""
import pytest
from src.core.clickup_adapter import (
    load_tasks,
    load_policies,
    load_definition_of_done,
    load_architecture_guidelines,
    get_task_by_id,
)

REQUIRED_TASK_FIELDS = [
    "task_id", "title", "description", "status", "priority",
    "assignee", "sprint", "tags",
]


def test_load_tasks_returns_list():
    tasks = load_tasks()
    assert isinstance(tasks, list)
    assert len(tasks) >= 12


def test_tasks_have_required_fields():
    tasks = load_tasks()
    for task in tasks:
        for field in REQUIRED_TASK_FIELDS:
            assert field in task, f"Task {task.get('task_id')} missing field: {field}"


def test_task_ids_are_unique():
    tasks = load_tasks()
    ids = [t["task_id"] for t in tasks]
    assert len(ids) == len(set(ids)), "Duplicate task IDs found"


def test_get_task_by_id_found():
    task = get_task_by_id("TASK-001")
    assert task is not None
    assert task["task_id"] == "TASK-001"


def test_get_task_by_id_not_found():
    task = get_task_by_id("TASK-NONEXISTENT")
    assert task is None


def test_load_policies():
    policies = load_policies()
    assert "risk_thresholds" in policies
    assert "gate_decisions" in policies
    assert "Low" in policies["risk_thresholds"]
    assert "Critical" in policies["risk_thresholds"]


def test_load_definition_of_done():
    dod = load_definition_of_done()
    assert "checklist" in dod
    assert len(dod["checklist"]) > 0
    for item in dod["checklist"]:
        assert "id" in item
        assert "item" in item


def test_load_architecture_guidelines():
    guidelines = load_architecture_guidelines()
    assert "review_triggers" in guidelines
    assert len(guidelines["review_triggers"]) > 0
