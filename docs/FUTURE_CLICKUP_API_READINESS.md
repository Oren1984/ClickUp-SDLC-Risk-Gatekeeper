# Future ClickUp API Readiness

**ClickUp SDLC Risk Gatekeeper**

---

## Current State

The project runs entirely on local mock data. The `src/core/clickup_adapter.py` module loads tasks from `data/clickup_demo/tasks.json`. No ClickUp credentials, no API calls, and no external services are required.

This is intentional. The project is demo-first. The integration boundary is designed and documented, but the real API connection is not active.

---

## Why Real Integration Is Out of Scope for This Version

1. **Portfolio clarity** — A demo that requires a live ClickUp workspace cannot be reviewed by a recruiter or interviewer without setup. Mock-first means it runs everywhere.
2. **Architecture separation** — The risk engine should be proven correct on controlled data before connecting to live task data.
3. **No secrets in the repo** — Activating real API calls requires credential management that is out of scope for a portfolio project.
4. **Stability** — A live API dependency makes the demo brittle. A ClickUp workspace change can break the demo.

The integration will be activated when these conditions are met: a real workspace is available, credentials are managed securely, and the mapping from ClickUp custom fields to the task schema is validated.

---

## Integration Boundary Design

The system is adapter-based. The core risk engine (`src/core/risk_reviewer.py`, `src/core/risk_rules.py`, `src/core/compliance_checks.py`) does not know where task data comes from. It only receives a task dict in the standard schema.

The integration layer sits between the data source and the risk engine:

```
ClickUp API  (or any PM tool)
      │
      ▼
src/integrations/clickup_api_client.py   ← future-ready placeholder
      │
      ▼  (maps to standard task schema)
src/core/risk_reviewer.py               ← unchanged
      │
      ▼
Dashboard output
```

To activate real ClickUp data, only the adapter changes. The risk logic stays intact.

---

## What Real Integration Could Pull from ClickUp

A future real integration would use the ClickUp v2 API to fetch:

| Field | ClickUp API field |
|---|---|
| Task ID | `task.id` |
| Title | `task.name` |
| Description | `task.description` |
| Status | `task.status.status` |
| Priority | `task.priority.priority` |
| Assignees | `task.assignees[].username` |
| Tags | `task.tags[].name` |
| Due date | `task.due_date` |
| Dependencies | `task.dependencies[].task_id` |
| Acceptance Criteria | Custom field: `Acceptance Criteria` |
| QA Notes | Custom field: `QA Notes` |
| Security Notes | Custom field: `Security Notes` |
| Architecture Notes | Custom field: `Architecture Notes` |
| DoD Status | Custom field: `DoD Status` |
| Sprint | Custom field or Relationship: `Sprint` |

ClickUp custom fields are returned as a `custom_fields` array. The adapter maps field names to the standard task schema.

---

## What Real Integration Could Write Back to ClickUp

After a human reviewer approves the AI risk output, the system could optionally write back to ClickUp:

| Action | ClickUp API endpoint |
|---|---|
| Post risk review summary as comment | `POST /api/v2/task/{task_id}/comment` |
| Apply risk level tag | `POST /api/v2/task/{task_id}/tag/risk-{level}` |
| Update task status to reflect gate outcome | `PUT /api/v2/task/{task_id}` |

These write-back actions must only happen after human approval. The system must not write to ClickUp autonomously.

---

## Authentication Requirements

When real integration is activated:

- The ClickUp API token must be stored in an environment variable: `CLICKUP_API_TOKEN`
- The token must never be committed to any file in the repository
- The `.env.example` file documents the required variables — the `.env` file is gitignored
- Token rotation must not break the integration (use env vars, not hardcoded values)
- API calls must respect ClickUp rate limits (100 req/min for most endpoints)

---

## Integration Skeleton

The `src/integrations/` directory contains the future-ready skeleton:

```
src/integrations/
  __init__.py             ← package marker
  base.py                 ← TaskClient protocol (interface definition)
  mock_client.py          ← active mock implementation (reads local JSON)
  clickup_api_client.py   ← future placeholder (raises NotImplementedError)
```

`clickup_api_client.py` documents the required methods and their signatures. All methods raise `NotImplementedError` with a clear message explaining how to activate them.

To activate real integration:
1. Implement `fetch_tasks()` in `clickup_api_client.py` using `requests` and the ClickUp v2 API
2. Implement `fetch_task_by_id()` similarly
3. Add field mapping from ClickUp's raw task format to the standard schema
4. Set `CLICKUP_API_TOKEN` in the environment
5. Update `app/streamlit_app.py` to use `ClickUpApiClient` instead of the adapter's `load_tasks()`

---

## Adapter-Based Architecture Benefit

Because the risk engine is decoupled from the data source, the same integration pattern applies to any project management tool:

| Tool | What to implement |
|---|---|
| ClickUp | `src/integrations/clickup_api_client.py` |
| Jira | `src/integrations/jira_client.py` |
| Linear | `src/integrations/linear_client.py` |
| Notion | `src/integrations/notion_client.py` |
| Azure DevOps | `src/integrations/ado_client.py` |
| Monday.com | `src/integrations/monday_client.py` |

Each client implements the `TaskClient` protocol from `src/integrations/base.py`. The risk engine and dashboard require no changes.

---

## Estimated Effort to Activate ClickUp Integration

| Task | Estimate |
|---|---|
| Implement `fetch_tasks()` with API call and field mapping | 2–4 hours |
| Implement `fetch_task_by_id()` | 1 hour |
| Set up ClickUp workspace with required custom fields | 1–2 hours |
| Add write-back methods (comment, label, status) | 2 hours |
| Add webhook endpoint to trigger review on task update | 2–4 hours |
| End-to-end testing with a real ClickUp workspace | 2–4 hours |
| **Total** | **~1–2 days** |
