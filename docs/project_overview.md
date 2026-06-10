# Project Overview: SDLC Risk & Compliance Gatekeeper

**Oren Salami | Technology Project Management + AI Tools**

## What is this project?

This is an AI-assisted SDLC quality gate that automatically reviews technical tasks
before they enter development, and identifies gaps in quality, security, architecture,
and compliance.

It is designed to slot into an Agile/Scrum workflow between **Sprint Planning** and
**Development Start**, providing a fast, automated risk assessment of every task.

## Why does it matter?

Engineering teams frequently move tasks from backlog to sprint with incomplete information.
The cost of catching a missing security review or undefined acceptance criteria in
**planning** is near zero. The cost of catching it in **production** is very high.

This tool moves risk detection as far left as possible in the SDLC.

## Who is this for?

This demo is relevant to:

- **Engineering Managers** — early visibility into sprint risk before development starts
- **QA Engineers** — automatic flagging of tasks without test plans
- **Security Engineers** — surface security and compliance gaps at the task level
- **DevOps Engineers** — detect architecture-impacting changes before code is written
- **Product Managers** — understand which tasks need clarification before sprint commit
- **AI Engineers** — review AI/LLM tasks for missing guardrails and safety controls

## What does the demo show?

The Streamlit dashboard shows:

1. **Project Risk Overview** — summary metrics across all tasks in the project
2. **Task Risk Dashboard** — every task with its risk score, level, and gate decision
3. **Task Detail View** — drill-down into any task with full findings and recommendations
4. **Compliance Gap View** — tasks flagged against GDPR, PCI-DSS, HIPAA, SOX

## What is mock vs. what is real?

| Component | Status |
|-----------|--------|
| Risk rules engine | Real — deterministic Python |
| Compliance checks | Real — GDPR, PCI, HIPAA, SOX pattern matching |
| Task data | Mock — 20 realistic ClickUp-style JSON tasks |
| Integration adapter | Not connected to live API — clear TODOs in `clickup_adapter.py` |
| Risk scoring | Real — weighted rule-based scoring |
| Gate decisions | Real — logic-driven based on detected rules |

## Integration positioning

The demo uses a **ClickUp-style workflow** as the first integration example.
The adapter-based architecture (`src/core/clickup_adapter.py`) is designed so the same
risk engine can later connect to real ClickUp, or be extended to support Jira, Monday,
Linear, Azure DevOps, Notion, or any other task-management platform with a task API.

## SDLC positioning

```
Backlog → Sprint Planning → [RISK GATE] → Development → Code Review → QA → Staging → Production
                                ↑
                         This project
```

The gatekeeper runs at the point where tasks are committed to a sprint, before any
development work begins.
