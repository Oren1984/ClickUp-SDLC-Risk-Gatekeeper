# ClickUp SDLC Risk Gatekeeper

**AI-assisted SDLC Risk & Compliance Gatekeeper for ClickUp-style software delivery workflows.**

Oren Salami | Technology Project Management + AI Tools

---

## Business Problem

In Agile and Scrum teams, tasks regularly enter development sprints missing critical information:

- Vague or missing acceptance criteria
- No QA test plan or Definition of Done confirmation
- Security-sensitive changes without a threat model
- AI/LLM features without safety guardrails or fallback behavior
- Architecture-impacting changes without design review
- Compliance tasks (GDPR, PCI-DSS, HIPAA) without documented evidence

Catching these gaps in planning costs nothing. Catching them in production is expensive.

---

## What the System Does

The **ClickUp SDLC Risk Gatekeeper** is a governance and risk-review assistant for tasks, user stories, QA readiness, security and compliance gaps, missing acceptance criteria, and Definition of Done alignment.

It is **not** a generic chatbot and **not** a ClickUp clone. It is a structured risk gate that sits between backlog refinement and development start.

For each task, the system:

1. Loads the task from a ClickUp-compatible data source (mock JSON in this demo)
2. Runs 10 deterministic SDLC risk rules across quality, QA, security, architecture, compliance, and dependency dimensions
3. Produces a **risk score (0–100)**, **risk level** (Low / Medium / High / Critical), **gate decision**, **findings**, and **recommendations**
4. Presents results in a Streamlit dashboard for human review and final decision

| Gate Decision | Meaning |
|---|---|
| ✅ Approved for Development | Task passes all quality gates — ready to enter sprint |
| 💬 Needs Clarification | Minor gaps must be resolved before development starts |
| 🧪 Requires QA Review | QA lead must review and approve before dev starts |
| 🔒 Requires Security Review | Security or compliance team must sign off |
| 🏗️ Requires Architecture Review | Tech lead or architect must review system impact |
| 🚫 Blocked | Cannot proceed — blocking dependency or critical gap unresolved |

---

## Why ClickUp-Style Workflows

ClickUp is a widely used project management platform in software delivery teams. Its task structure — titles, descriptions, acceptance criteria, assignees, priorities, tags, custom fields, due dates — maps naturally to SDLC governance requirements.

This project uses a **ClickUp-compatible JSON schema** for all mock data, making the path to a real ClickUp workspace practical and well-defined. The same risk logic can also apply to Jira, Linear, Notion, Azure DevOps, or any tool with a task API — the adapter layer is designed to be swapped without touching the core engine.

---

## Demo Mode

This project runs entirely on **local mock data**. No ClickUp credentials, no API keys, and no cloud setup are required.

All 20 demo tasks are realistic but fictional, stored in `data/clickup_demo/tasks.json`. Each task was designed to trigger a specific combination of risk rules for demonstration purposes.

The `src/core/clickup_adapter.py` module is the active data source. It loads local JSON. When real ClickUp API integration is needed in the future, only this adapter needs to change — the risk engine remains untouched.

---

## AI Governance & Human-in-the-Loop

The risk gatekeeper is designed as a **decision-support tool**, not an autonomous decision-maker.

**Core principles:**
- AI recommendations are **advisory**. Final gate decisions are owned by the PM, QA lead, or Tech Lead.
- Every finding is **explainable**: each rule states exactly what is missing and why it matters.
- The system **flags uncertainty** rather than guessing — if data is missing, it reports the gap.
- **No task is automatically approved or rejected** without a human reviewing the output.
- The PM / QA / Tech Lead remains responsible for all decisions.

See [docs/AI_GOVERNANCE_AND_RISK_PRINCIPLES.md](docs/AI_GOVERNANCE_AND_RISK_PRINCIPLES.md) and [docs/HUMAN_IN_THE_LOOP_WORKFLOW.md](docs/HUMAN_IN_THE_LOOP_WORKFLOW.md) for the full governance framework.

---

## Optional ClickUp Read-Only API Integration

**Phase 1 (read-only) is implemented.** The project runs in mock/demo mode by default with no credentials required. Supplying a ClickUp API token activates live data fetching.

### How it works

- `src/integrations/clickup_api_client.py` — read-only ClickUp v2 API client
- When `CLICKUP_API_TOKEN` is set: fetches live tasks from configured lists
- When unconfigured: `fetch_tasks()` returns `[]` and the app continues with mock data
- Write operations (`post_review_comment`, `set_risk_label`, `update_task_status`) raise `NotImplementedError` — Phase 2 (HITL write-back) only

### Setup (optional)

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Fill in the real values in `.env` (never commit this file):
   ```
   CLICKUP_API_TOKEN=your_personal_api_token
   CLICKUP_TEAM_ID=your_workspace_team_id
   CLICKUP_SPACE_ID=your_space_id
   CLICKUP_FOLDER_ID=your_folder_id
   CLICKUP_LIST_BACKLOG_REQUIREMENTS_ID=...
   CLICKUP_LIST_SDLC_RISK_REVIEW_ID=...
   CLICKUP_LIST_QA_DOD_VALIDATION_ID=...
   CLICKUP_LIST_GOVERNANCE_HITL_ID=...
   CLICKUP_LIST_DEMO_DASHBOARD_ID=...
   ```
3. Verify the connection (safe read-only check, token is never printed):
   ```bash
   python scripts/check_clickup_connection.py
   ```

### Security boundaries

- Token is read from environment only — never hardcoded, never logged, never printed
- All endpoints used are `GET` (read-only)
- No write-back of any kind in Phase 1
- If env vars are missing the app silently uses mock data

See [docs/future_clickup_integration.md](docs/future_clickup_integration.md) for the Phase 2 write-back plan.

---

## Architecture

```
data/clickup_demo/tasks.json          ← 20 mock ClickUp-style tasks
         │
         ▼
src/core/clickup_adapter.py           ← active mock adapter (JSON loader)
src/integrations/                     ← future-ready integration layer
  base.py                             ←   adapter protocol / interface
  mock_client.py                      ←   mock implementation
  clickup_api_client.py               ←   future placeholder (NotImplementedError)
         │
         ▼
src/core/risk_rules.py                ← 10 SDLC risk rules (deterministic)
src/core/risk_reviewer.py             ← scoring + gate decision logic
src/core/compliance_checks.py         ← GDPR / PCI-DSS / HIPAA / SOX
         │
         ▼
src/core/report_generator.py          ← per-task + project summary report
         │
         ▼
app/streamlit_app.py                  ← Streamlit SDLC risk dashboard
```

All components are pure Python. No external services, no cloud, no database required.

---

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Open: http://localhost:8501

**Static portfolio site:**
```bash
cd static-site
python -m http.server 8000
```

Open: http://localhost:8000

---

## Run with Docker

```bash
docker compose up --build
```

Open: http://localhost:8501

---

## Testing

```bash
pytest
```

Tests cover the adapter, risk reviewer, compliance checks, and integration skeleton. All tests use mock data — no external dependencies required.

---

## Documentation

| Document | Purpose |
|---|---|
| [docs/AI_GOVERNANCE_AND_RISK_PRINCIPLES.md](docs/AI_GOVERNANCE_AND_RISK_PRINCIPLES.md) | AI governance framework and responsible use principles |
| [docs/HUMAN_IN_THE_LOOP_WORKFLOW.md](docs/HUMAN_IN_THE_LOOP_WORKFLOW.md) | Human-in-the-loop review process and decision outcomes |
| [docs/EVALUATION_SCENARIOS.md](docs/EVALUATION_SCENARIOS.md) | 10 demo scenarios with inputs, outputs, and rationale |
| [docs/FUTURE_CLICKUP_API_READINESS.md](docs/FUTURE_CLICKUP_API_READINESS.md) | ClickUp API integration roadmap and boundary design |
| [docs/architecture.md](docs/architecture.md) | Component architecture and data flow |
| [docs/workflow.md](docs/workflow.md) | SDLC gate flow and Agile/Scrum fit |
| [docs/demo_scenarios.md](docs/demo_scenarios.md) | All 20 mock tasks and what each one demonstrates |
| [docs/future_clickup_integration.md](docs/future_clickup_integration.md) | Step-by-step ClickUp API integration guide |
| [docs/limitations.md](docs/limitations.md) | Known limitations and scope boundaries |
| [docs/testing_strategy.md](docs/testing_strategy.md) | Testing approach and coverage |

---

## Portfolio & Career Positioning

**Category:** Technology Project Management + AI Tools

This project demonstrates:

| Skill Area | What is Demonstrated |
|---|---|
| Technology Project Management | SDLC gate design, sprint quality control, task readiness validation |
| QA Thinking | Automated QA readiness checking, DoD enforcement, test plan visibility |
| Risk & Compliance | Pre-development risk scoring, GDPR/PCI/HIPAA gap detection |
| AI Governance | Human-in-the-Loop design, explainable AI outputs, advisory-only AI |
| AI Engineering | Adapter-based integration pattern, mock-first architecture |
| Software Delivery | Agile/Scrum fit, dependency management, sprint risk visibility |

This is a **practical AI-assisted process improvement tool** for technical project management — not a pure ML engineering project. It shows how SDLC governance, QA, security review, architecture review, compliance checking, and risk management can be embedded into task-management workflows using lightweight, deterministic Python. No LLM inference required. Runs entirely on local data.

---

## License

MIT License. See [LICENSE](LICENSE).
