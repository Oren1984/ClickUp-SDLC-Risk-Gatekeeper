# ClickUp — Automated SDLC Risk & Compliance Gatekeeper

**Oren Salami | AI Systems Engineer**
SDLC · Agile / Scrum · Risk Management · QA Readiness · Compliance · AI-Assisted Decision Support

---

## Project Overview

The **ClickUp SDLC Risk & Compliance Gatekeeper** is an automated risk review system that analyzes technical tasks before they enter development, and flags gaps in quality, security, architecture, and compliance.

It simulates the role of an AI-assisted gate that sits between **task planning** and **development start** in an Agile/Scrum workflow — catching problems early, before they become expensive bugs, security incidents, or compliance violations.

> **Demo mode:** All data is local mock JSON. No real ClickUp API calls are made.
> The adapter layer is designed for future ClickUp API integration.

---

## What problem does this solve?

In real engineering teams, tasks frequently enter development with:

- Missing or vague acceptance criteria
- No QA or test plan
- Security-sensitive changes without a threat model
- AI/LLM features without safety guardrails
- Architecture-impacting changes without a design review
- Compliance requirements (GDPR, PCI, HIPAA) missing evidence

This tool provides an **automated first-pass review** that catches these gaps at task-planning time, reducing rework and risk downstream.

---

## Core Risk Rules

| Rule | Category | What it detects |
|------|----------|----------------|
| RULE-001 | Quality | Missing or insufficient acceptance criteria |
| RULE-002 | QA | No QA notes or test plan |
| RULE-003 | Process | Definition of Done not confirmed |
| RULE-004 | Security | Security task without security notes |
| RULE-005 | AI Safety | AI/LLM task without guardrails or fallback |
| RULE-006 | Architecture | Arch-impacting task without architecture review |
| RULE-007 | Scope | Critical priority with vague scope |
| RULE-008 | Dependency | Blocked by unresolved dependency |
| RULE-009 | Compliance | Compliance task without evidence |
| RULE-010 | Timeline | Due date overdue or at immediate risk |

---

## Gate Decisions

Each task receives one of six gate decisions:

| Decision | Meaning |
|----------|---------|
| ✅ Approved for Development | Task passes all quality gates |
| 💬 Needs Clarification | Minor gaps must be resolved first |
| 🧪 Requires QA Review | QA lead must review before dev starts |
| 🔒 Requires Security Review | Security team must sign off |
| 🏗️ Requires Architecture Review | Tech lead or architect must review |
| 🚫 Blocked | Cannot proceed — blocking dependency or critical gap |

---

## Repository Structure

```
clickup-sdlc-risk-gatekeeper/
├── app/
│   └── streamlit_app.py          # Streamlit dashboard
├── src/
│   └── core/
│       ├── risk_rules.py         # 10 SDLC risk rules
│       ├── risk_reviewer.py      # Risk scoring and gate logic
│       ├── compliance_checks.py  # GDPR, PCI, HIPAA, SOX checks
│       ├── clickup_adapter.py    # Data loader (mock + future API)
│       └── report_generator.py  # Summary and task report builder
├── data/
│   └── clickup_demo/
│       ├── tasks.json                  # 20 mock ClickUp tasks
│       ├── policies.json               # Risk thresholds and gate definitions
│       ├── definition_of_done.json     # DoD checklist
│       └── architecture_guidelines.json
├── docs/
│   ├── project_overview.md
│   ├── architecture.md
│   ├── workflow.md
│   ├── demo_scenarios.md
│   ├── future_clickup_integration.md
│   ├── testing_strategy.md
│   └── limitations.md
├── tests/
│   ├── test_risk_reviewer.py
│   ├── test_compliance_checks.py
│   └── test_clickup_adapter.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## How to Run

**Clone and set up:**

```bash
git clone https://github.com/Oren1984/clickup-sdlc-risk-gatekeeper.git
cd clickup-sdlc-risk-gatekeeper
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

**Run the Streamlit app:**

```bash
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

## Run Tests

```bash
pytest
pytest -v          # verbose output
pytest --cov=src   # with coverage
```

All 36 tests should pass. No API keys or external services required.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| Risk Engine | Python (deterministic rules) |
| Data | JSON mock data |
| Compliance | Custom GDPR/PCI/HIPAA/SOX checks |
| Tests | pytest |
| Packaging | Docker, Docker Compose |

---

## Demo Scenarios

20 tasks covering:
- AI/LLM feature without guardrails (Critical)
- Payment integration without PCI evidence (Critical)
- GDPR endpoint without compliance docs (Critical)
- OAuth2 task without security notes (High)
- Database migration without architecture review (High)
- CI/CD setup without architecture notes (High)
- Blocked dependency task (Blocked)
- Vague critical-priority task (High)
- Clean tasks approved for development (Low)

See [docs/demo_scenarios.md](docs/demo_scenarios.md) for full walkthrough.

---

## Future ClickUp API Integration

See [docs/future_clickup_integration.md](docs/future_clickup_integration.md) and
the TODO comments in `src/core/clickup_adapter.py`.

The adapter is mock-first by design. Switching to live data requires setting
`CLICKUP_API_TOKEN` and uncommenting API call implementations.

---

## License

MIT License. See the LICENSE file for details.
