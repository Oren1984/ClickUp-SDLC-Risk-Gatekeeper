# AGENTS.md — Contributor and AI Agent Guidelines

## Project Purpose

**ClickUp SDLC Risk Gatekeeper** is an AI-assisted SDLC risk and governance tool for ClickUp-style software delivery workflows. It is a portfolio project demonstrating Technology Project Management, QA thinking, SDLC governance, AI risk detection, and practical AI engineering.

This document defines how AI coding agents and human contributors should work in this repository.

---

## What Agents Are Allowed to Modify

- `src/core/` — risk rules, reviewer, compliance checks, adapter, report generator
- `src/integrations/` — integration adapters (mock and future placeholder only)
- `app/streamlit_app.py` — Streamlit dashboard UI and visible text
- `tests/` — pytest tests for all modules
- `docs/` — documentation improvements and additions
- `data/clickup_demo/` — mock task data, policies, DoD, architecture guidelines
- `static-site/` — static HTML/CSS portfolio site
- `requirements.txt` — dependency additions (keep minimal)
- `README.md`, `AGENTS.md` — project-level documentation

---

## What Agents Must Not Do

### ClickUp API

- Do **not** make real ClickUp API calls in any code path that runs by default
- Do **not** activate `clickup_api_client.py` — it must remain a placeholder that raises `NotImplementedError`
- Do **not** add `CLICKUP_API_TOKEN` or any real token to committed files
- Do **not** require real ClickUp credentials to run the app or tests

### Secrets and credentials

- Do **not** hardcode tokens, API keys, passwords, or credentials in any file
- Do **not** commit `.env` files containing real secrets
- Use environment variables only, documented in `.env.example`

### Architecture

- Do **not** add databases, message queues, microservices, or external cloud services
- Do **not** introduce FastAPI, Flask, or additional web servers unless explicitly requested
- Do **not** add new infrastructure dependencies (Redis, Celery, Docker registries, etc.)
- Keep the architecture flat, readable, and explainable to a non-engineer

### Mock/demo mode

- Do **not** change the default app behavior away from mock/demo data
- The Streamlit app must continue to run with `streamlit run app/streamlit_app.py` with no credentials
- `src/core/clickup_adapter.py` must remain the active default data source

### Tests

- Do **not** delete or weaken existing test assertions
- Do **not** introduce test mocks that hide real integration failures
- If you add new modules, add corresponding tests in `tests/`

### Over-engineering

- Do **not** add abstract factory patterns, DI containers, or design patterns beyond what the task requires
- Do **not** add logging frameworks, monitoring stacks, or observability infrastructure
- Do **not** create new Python packages without a clear, stated reason
- Three similar lines is better than a premature abstraction
- Prefer small, readable, focused changes

---

## Default Behavior Rules

1. **Mock data is the default.** All demo runs must work without credentials.
2. **Future-ready means placeholder only.** `clickup_api_client.py` raises `NotImplementedError`. Do not implement real API calls.
3. **Tests must pass.** Run `pytest` before submitting any change.
4. **Portfolio clarity is a requirement.** Code should be readable by a reviewer without deep Python expertise.
5. **No unnecessary comments.** Only add a comment when the WHY is non-obvious — a hidden constraint, a workaround, a subtle invariant.

---

## How to Add a New Integration Adapter

If you need to support a new project management tool (Jira, Linear, Notion, etc.):

1. Add a new file in `src/integrations/` (e.g., `jira_client.py`)
2. Implement the `TaskClient` protocol defined in `src/integrations/base.py`
3. Methods that require real API credentials must raise `NotImplementedError` until integration is explicitly activated
4. Add tests in `tests/test_integrations.py`
5. Document the integration boundary in `docs/FUTURE_CLICKUP_API_READINESS.md`
6. Do **not** change the default data source in `app/streamlit_app.py`

---

## Commit Style

- Keep commits focused and small
- Write commit messages that explain WHY, not just WHAT
- Do not amend published commits
- Do not force-push to `main`
- Do not skip pre-commit hooks
