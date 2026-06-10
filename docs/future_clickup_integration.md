# Future ClickUp API Integration

## Current State

The project runs entirely on local mock data. The `src/core/clickup_adapter.py`
module loads tasks from `data/clickup_demo/tasks.json`.

## Integration Path

### Step 1 — Authentication

```python
# Add to .env
CLICKUP_API_TOKEN=pk_xxxxxxxxxxxxxxxx

# In clickup_adapter.py
import os, requests
HEADERS = {"Authorization": os.environ["CLICKUP_API_TOKEN"]}
BASE_URL = "https://api.clickup.com/api/v2"
```

### Step 2 — Pull Tasks from a List

```python
def load_tasks(list_id: str) -> list[dict]:
    resp = requests.get(f"{BASE_URL}/list/{list_id}/task", headers=HEADERS)
    resp.raise_for_status()
    raw = resp.json()["tasks"]
    return [_map_clickup_task(t) for t in raw]
```

### Step 3 — Map ClickUp Custom Fields

ClickUp tasks use a `custom_fields` array. You need to map field names to the
schema used by the risk reviewer:

```python
def _map_clickup_task(raw: dict) -> dict:
    custom = {cf["name"]: cf.get("value") for cf in raw.get("custom_fields", [])}
    return {
        "task_id": raw["id"],
        "title": raw["name"],
        "description": raw.get("description", ""),
        "status": raw["status"]["status"],
        "priority": raw["priority"]["priority"] if raw.get("priority") else "none",
        "assignee": raw["assignees"][0]["username"] if raw.get("assignees") else "Unassigned",
        "sprint": custom.get("Sprint", ""),
        "tags": [t["name"] for t in raw.get("tags", [])],
        "acceptance_criteria": custom.get("Acceptance Criteria"),
        "definition_of_done_status": custom.get("DoD Status"),
        "security_notes": custom.get("Security Notes"),
        "architecture_notes": custom.get("Architecture Notes"),
        "qa_notes": custom.get("QA Notes"),
        "dependencies": [d["task_id"] for d in raw.get("dependencies", [])],
        "due_date": raw.get("due_date"),
    }
```

### Step 4 — Post Risk Review as a Comment

```python
def post_review_comment(task_id: str, comment: str) -> None:
    requests.post(
        f"{BASE_URL}/task/{task_id}/comment",
        headers=HEADERS,
        json={"comment_text": comment},
    )
```

### Step 5 — Apply Risk Label Tag

```python
def set_risk_label(task_id: str, risk_level: str) -> None:
    requests.post(
        f"{BASE_URL}/task/{task_id}/tag/risk-{risk_level.lower()}",
        headers=HEADERS,
    )
```

### Step 6 — Update Task Status

```python
def update_task_status(task_id: str, new_status: str) -> None:
    requests.put(
        f"{BASE_URL}/task/{task_id}",
        headers=HEADERS,
        json={"status": new_status},
    )
```

## Integration Architecture

```
ClickUp Webhook (task created / moved to sprint)
      │
      ▼
Risk Gate API endpoint (FastAPI or Lambda)
      │
      ▼
clickup_adapter.load_tasks() — live API call
      │
      ▼
RiskReviewer.review(task)
      │
      ├── post_review_comment(task_id, findings_text)
      ├── set_risk_label(task_id, risk_level)
      └── update_task_status(task_id, "Needs Risk Review") if blocked
```

## ClickUp Custom Fields Required

To use this system with real ClickUp tasks, create these custom fields in your workspace:

| Field Name | Type | Purpose |
|-----------|------|---------|
| Acceptance Criteria | Long Text | Task completion definition |
| QA Notes | Long Text | Test plan and cases |
| Security Notes | Long Text | Security review notes |
| Architecture Notes | Long Text | Architecture review notes |
| DoD Status | Dropdown | complete / incomplete / missing |
| Sprint | Text or Relationship | Sprint name or ID |

## Estimated Integration Effort

| Task | Estimate |
|------|---------|
| API authentication setup | 1 hour |
| Task mapping function | 2–4 hours |
| Comment posting | 1 hour |
| Label/status update | 1 hour |
| Webhook endpoint | 2–4 hours |
| Custom field setup in ClickUp | 1–2 hours |
| **Total** | **~1–2 days** |
