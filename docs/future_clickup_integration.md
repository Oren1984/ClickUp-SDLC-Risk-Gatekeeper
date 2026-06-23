# ClickUp API Integration

## Phase 1 — Read-Only Integration (Implemented)

The read-only ClickUp API integration is complete. The project defaults to mock/demo
data and activates live API fetching when `CLICKUP_API_TOKEN` is present in the
environment.

### Active endpoints (GET only)

```
GET /api/v2/team/{team_id}/space          ← list spaces in workspace
GET /api/v2/space/{space_id}/folder       ← list folders in space
GET /api/v2/folder/{folder_id}/list       ← list lists in folder
GET /api/v2/list/{list_id}/task           ← fetch tasks from a list
GET /api/v2/task/{task_id}                ← fetch a single task
```

### Authentication

```python
# In .env (never commit this file)
CLICKUP_API_TOKEN=your_personal_api_token

# In src/integrations/clickup_api_client.py
headers = {"Authorization": os.environ["CLICKUP_API_TOKEN"]}
# Token is never printed, never included in logs or error messages
```

### Environment variables

```
CLICKUP_API_TOKEN=REPLACE_WITH_CLICKUP_PERSONAL_API_TOKEN
CLICKUP_TEAM_ID=REPLACE_WITH_CLICKUP_WORKSPACE_TEAM_ID
CLICKUP_SPACE_ID=REPLACE_WITH_CLICKUP_SPACE_ID
CLICKUP_FOLDER_ID=REPLACE_WITH_CLICKUP_FOLDER_ID
CLICKUP_LIST_BACKLOG_REQUIREMENTS_ID=REPLACE_WITH_BACKLOG_REQUIREMENTS_LIST_ID
CLICKUP_LIST_SDLC_RISK_REVIEW_ID=REPLACE_WITH_SDLC_RISK_REVIEW_LIST_ID
CLICKUP_LIST_QA_DOD_VALIDATION_ID=REPLACE_WITH_QA_DOD_VALIDATION_LIST_ID
CLICKUP_LIST_GOVERNANCE_HITL_ID=REPLACE_WITH_GOVERNANCE_HITL_LIST_ID
CLICKUP_LIST_DEMO_DASHBOARD_ID=REPLACE_WITH_DEMO_DASHBOARD_LIST_ID
CLICKUP_INTEGRATION_MODE=readonly
CLICKUP_USE_MOCK_FALLBACK=true
```

### Task schema mapping

ClickUp API v2 responses are mapped to the standard internal task schema:

```python
def _map_task(raw: dict) -> dict:
    custom = {cf["name"]: cf.get("value") for cf in raw.get("custom_fields") or []}
    return {
        "task_id": raw.get("id", ""),
        "title": raw.get("name", ""),
        "description": raw.get("description", ""),
        "status": raw["status"]["status"],
        "priority": raw["priority"]["priority"] if raw.get("priority") else "none",
        "assignee": raw["assignees"][0]["username"] if raw.get("assignees") else "Unassigned",
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
```

### ClickUp Custom Fields required

To use with real ClickUp tasks, create these custom fields in your workspace:

| Field Name | Type | Purpose |
|---|---|---|
| Acceptance Criteria | Long Text | Task completion definition |
| QA Notes | Long Text | Test plan and cases |
| Security Notes | Long Text | Security review notes |
| Architecture Notes | Long Text | Architecture review notes |
| DoD Status | Dropdown | complete / incomplete / missing |
| Sprint | Text or Relationship | Sprint name or ID |

### Connection check script

```bash
python scripts/check_clickup_connection.py
```

Validates env vars, fetches workspace/space/folder/list/task metadata,
and prints safe output. Never prints the token. No write operations.

---

## Phase 2 — HITL Write-Back (Future Only)

Write-back is intentionally not implemented in Phase 1.
All write methods raise `NotImplementedError`.

When a human approves an AI risk finding, Phase 2 will enable:

### Post risk review as a comment

```python
def post_review_comment(task_id: str, comment: str) -> None:
    requests.post(
        f"{BASE_URL}/task/{task_id}/comment",
        headers=headers,
        json={"comment_text": comment},
    )
```

### Apply risk label tag

```python
def set_risk_label(task_id: str, risk_level: str) -> None:
    requests.post(
        f"{BASE_URL}/task/{task_id}/tag/risk-{risk_level.lower()}",
        headers=headers,
    )
```

### Update task status

```python
def update_task_status(task_id: str, new_status: str) -> None:
    requests.put(
        f"{BASE_URL}/task/{task_id}",
        headers=headers,
        json={"status": new_status},
    )
```

### Phase 2 architecture (future)

```
ClickUp Webhook (task created / moved to sprint)
      │
      ▼
Risk Gate API endpoint (FastAPI or Lambda)
      │
      ▼
ClickUpApiClient.fetch_tasks() — live API call
      │
      ▼
RiskReviewer.review(task)
      │
      ├── [human approves] → post_review_comment(task_id, findings_text)
      ├── [human approves] → set_risk_label(task_id, risk_level)
      └── [human approves] → update_task_status(task_id, "Needs Risk Review")
```

### Estimated Phase 2 effort

| Task | Estimate |
|---|---|
| HITL approval UI | 4–8 hours |
| Comment posting | 1 hour |
| Label/status update | 1 hour |
| Webhook endpoint | 2–4 hours |
| **Total** | **~1–2 days** |
