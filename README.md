# SDLC Risk & Compliance Gatekeeper

**Oren Salami | Technology Project Management + AI Tools**

A ClickUp-style workflow demo for technical project management, designed to identify QA gaps,
security risks, missing requirements, Definition of Done violations, compliance gaps, and
architecture review needs before tasks enter development.

This project demonstrates how AI-assisted review logic can support small teams, solo builders,
and technical project managers by adding an early SDLC risk gate to task-management workflows.

> **Demo mode:** This project uses local ClickUp-style mock data. No API keys or external
> services required. The adapter-based architecture can later connect to real ClickUp, Jira,
> Monday, Linear, Azure DevOps, Notion, or any other task-management platform.

---

## Project Overview

The **SDLC Risk & Compliance Gatekeeper** is an automated risk review system that analyzes
technical tasks before they enter development and flags gaps in quality, security, architecture,
and compliance.

It sits between **Sprint Planning** and **Development Start** in an Agile/Scrum workflow —
catching problems early, before they become expensive bugs, security incidents, or compliance
violations.

**The gatekeeper reviews:**
- User stories and task descriptions for missing acceptance criteria
- QA notes and DoD status for test readiness
- Security-sensitive tasks for missing threat models and security notes
- AI/LLM tasks for missing guardrails and fallback behavior
- Architecture-impacting tasks for missing design review
- Compliance tasks (GDPR, PCI, HIPAA, SOX) for missing evidence
- Critical-priority tasks for vague scope
- Tasks with dependencies for blocked status
- Due dates for overdue or at-risk timelines

---

## Core Review Flows

| Flow | Input | Output |
|------|-------|--------|
| Task Readiness Review | User story, description, acceptance criteria | Missing requirements, clarification needs |
| QA Readiness Check | QA notes, test expectations, DoD status | QA gaps, test readiness, DoD violations |
| Security Risk Review | Tags, description, security notes | Security review requirement, validation gaps |
| Architecture Review Gate | System, database, integration notes | Architecture review recommendation |
| Compliance Gate | Policy and evidence fields, tags | Compliance framework gaps, evidence requirements |
| SDLC Decision Support | Full task context — all fields | Gate decision, risk score, findings, next actions |

---

## Risk Rules

| Rule | Category | What it detects | Weight |
|------|----------|----------------|--------|
| RULE-001 | Quality | Missing or insufficient acceptance criteria | 20 |
| RULE-002 | QA | No QA notes or test plan | 15 |
| RULE-003 | Process | Definition of Done not confirmed | 15 |
| RULE-004 | Security | Security task without security notes | 30 |
| RULE-005 | AI Safety | AI/LLM task without guardrails or fallback | 35 |
| RULE-006 | Architecture | Architecture-impacting task without design review | 25 |
| RULE-007 | Scope | Critical priority task with vague scope | 20 |
| RULE-008 | Dependency | Blocked by unresolved dependency | 25 |
| RULE-009 | Compliance | Compliance task without evidence or sign-off | 35 |
| RULE-010 | Timeline | Due date overdue or at immediate risk | 10–20 |

Risk score = sum of triggered rule weights, capped at 100.
Levels: Low (0–25) · Medium (26–50) · High (51–75) · Critical (76–100)

---

## Gate Decisions

| Decision | Meaning |
|----------|---------|
| ✅ Approved for Development | Task passes all quality gates |
| 💬 Needs Clarification | Minor gaps must be resolved first |
| 🧪 Requires QA Review | QA lead must review before dev starts |
| 🔒 Requires Security Review | Security or compliance team must sign off |
| 🏗️ Requires Architecture Review | Tech lead or architect must review |
| 🚫 Blocked | Cannot proceed — blocking dependency or critical gap |

---

## Architecture

```
── Demo Data Layer ────────────────────────────────────────────────────────

data/clickup_demo/tasks.json              ← 20 mock ClickUp-style tasks
data/clickup_demo/policies.json           ← risk thresholds + gate definitions
data/clickup_demo/definition_of_done.json ← DoD checklist
             │
             ▼
── Integration Adapter ────────────────────────────────────────────────────

src/core/clickup_adapter.py               ← active mock adapter
                                             TODO: replace with ClickUp / Jira /
                                             Monday / Linear / Azure DevOps API
             │
             ▼
── Risk Engine ────────────────────────────────────────────────────────────

src/core/risk_rules.py                    ← 10 SDLC risk rules (deterministic)
src/core/risk_reviewer.py                 ← scoring + gate decision logic
src/core/compliance_checks.py             ← GDPR / PCI-DSS / HIPAA / SOX
             │
             ▼
── Report + Dashboard ─────────────────────────────────────────────────────

src/core/report_generator.py              ← per-task + project summary
app/streamlit_app.py                      ← Streamlit SDLC risk dashboard
```

---

## How to Run

**Install and start:**

```bash
git clone https://github.com/Oren1984/sdlc-risk-gatekeeper.git
cd sdlc-risk-gatekeeper
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Open: http://localhost:8501

---

## Docker

```bash
docker compose up --build
```

Open: http://localhost:8501

---

## Static Portfolio Site

A standalone portfolio page is included in `static-site/`.
It explains the project, architecture, demo scenarios, and future integration path
in a recruiter-ready format — no Streamlit or Python required.

```bash
cd static-site
python -m http.server 8000
```

Open: http://localhost:8000

Or open `static-site/index.html` directly in any browser.

---

## Dashboard Capabilities

The Streamlit dashboard has four tabs:

- **Task Risk Dashboard** — full task list with risk scores, gate decisions, and expandable findings
- **Task Detail View** — drill-down into any task: description, notes, findings, recommendations
- **Compliance Gap Analysis** — GDPR, PCI-DSS, HIPAA, SOX gaps with evidence status
- **About** — project context, rule table, integration guide

Sidebar filters: Sprint · Status · Risk Level · Gate Decision

Summary metrics: Total tasks · Approved · Blocked · High/Critical · QA needed · Security needed · Architecture needed

---

## Demo Data

20 realistic mock tasks in `data/clickup_demo/tasks.json`. All fictional, all local.

| Scenario | Task | Risk |
|----------|------|------|
| PCI compliance task with no evidence | Stripe payment integration | Critical 100/100 |
| AI task without guardrails | AI recommendation engine | Critical |
| LLM moderation without safety controls | Content moderation | Critical 85/100 |
| Security + compliance + architecture gaps combined | Encrypt PII at rest | Critical 100/100 |
| Auth task without security notes | OAuth2 implementation | High 80/100 |
| Migration without architecture review | Database schema migration | Medium |
| Critical priority, description: "Deploy." | Production deployment | Critical 95/100 |
| Blocked by unresolved dependency | GraphQL API refactor | Blocked |
| GDPR endpoint without compliance docs | Data deletion endpoint | Medium |
| Simple bug fix, complete DoD | Fix typo on About page | Low — Approved ✅ |
| Security task with full notes and CISO sign-off | bcrypt password update | Low — Approved ✅ |

See [docs/demo_scenarios.md](docs/demo_scenarios.md) for the full walkthrough.

---

## Run Tests

```bash
pytest               # 36 tests
pytest -v            # verbose
pytest --cov=src     # with coverage
```

All 36 tests pass. No API keys or external services required.

---

## Documentation

| Document | Contents |
|----------|----------|
| [docs/project_overview.md](docs/project_overview.md) | What the project is, who it's for, mock vs. real |
| [docs/architecture.md](docs/architecture.md) | System design and component responsibilities |
| [docs/workflow.md](docs/workflow.md) | SDLC gate flow and Agile/Scrum fit |
| [docs/demo_scenarios.md](docs/demo_scenarios.md) | Full walkthrough of all 20 demo tasks |
| [docs/future_clickup_integration.md](docs/future_clickup_integration.md) | Step-by-step ClickUp API integration guide |
| [docs/testing_strategy.md](docs/testing_strategy.md) | Test coverage and philosophy |
| [docs/limitations.md](docs/limitations.md) | Known limitations and scope boundaries |

---

## Integration & Extension

The demo uses a **ClickUp-style adapter** as the first supported workflow integration.
The architecture is designed so the same risk engine can later connect to:

**ClickUp** · Jira · Monday · Linear · Azure DevOps · Notion · GitHub Issues

See `src/core/clickup_adapter.py` TODO comments and `docs/future_clickup_integration.md`
for the ClickUp integration guide. Estimated effort for a live connection: **1–2 days**.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| Risk Engine | Python — deterministic rule-based |
| Compliance | GDPR / PCI-DSS / HIPAA / SOX pattern matching |
| Data | JSON mock data (ClickUp-style schema) |
| Tests | pytest — 36 tests |
| Packaging | Docker, Docker Compose |
| Static Site | HTML + CSS — no framework, no build step |

---

## Project Category

**Technology Project Management + AI Tools**

This project demonstrates practical AI-assisted process improvement for technical project
management. It shows how SDLC, QA readiness, security review, architecture review,
compliance thinking, and risk management can be embedded into task-management workflows
using lightweight, deterministic Python. No LLM inference required. No cloud dependency.

Relevant to: Engineering Managers · QA Engineers · Security Engineers ·
DevOps / Platform Engineers · AI Engineers · Technical Project Managers

---

## License

MIT License. See the LICENSE file for details.
