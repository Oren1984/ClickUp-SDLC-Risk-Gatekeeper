# Future Improvements

## Project Status

This project is currently **closed, stable, and intentionally lean**. It meets its purpose as a portfolio-grade AI-assisted SDLC risk gatekeeper demo and should not be expanded beyond that purpose.

This document is a **future review list only**. Listing an item here does not authorize its implementation. Nothing in this file may be acted on without explicit human approval, obtained separately for each item.

---

## Approved Future Review Items

### 1. Correct the Streamlit About-tab description of the ClickUp API client

- **Current issue:** `app/streamlit_app.py`'s About tab states that `clickup_api_client.py` is a placeholder that raises `NotImplementedError`. This is inaccurate — Phase 1 read-only fetch (`fetch_tasks()`, `fetch_task_by_id()`) is implemented and tested; only the write-back methods raise `NotImplementedError`.
- **Preferred future action:** Update the About tab and sidebar caption text to accurately describe Phase 1 (read, implemented) vs. Phase 2 (write, not implemented).
- **Priority:** High
- **Effort:** Low
- **Files involved:** `app/streamlit_app.py`
- **Implementation condition:** Only after explicit human approval of the exact wording change.

### 2. Correct the README explanation of what `CLICKUP_API_TOKEN` currently activates

- **Current issue:** `README.md` states that supplying `CLICKUP_API_TOKEN` "activates live data fetching." In the current app, `app/streamlit_app.py` always loads mock data via `src/core/clickup_adapter.py` and never calls `ClickUpApiClient`. The token only affects `scripts/check_clickup_connection.py` today.
- **Preferred future action:** Reword the README section to state precisely what the token currently does (enables the connection-check script) versus what it does not yet do (feed the Streamlit dashboard).
- **Priority:** High
- **Effort:** Low
- **Files involved:** `README.md`
- **Implementation condition:** Only after explicit human approval of the exact wording change.

### 3. Clarify that policy/DoD/architecture-guideline JSON files are reference data only

- **Current issue:** `data/clickup_demo/policies.json`, `definition_of_done.json`, and `architecture_guidelines.json` are loaded by `clickup_adapter.py` and covered by tests, but are not consumed by `risk_rules.py`, `risk_reviewer.py`, or the Streamlit app. Rule thresholds are separately hardcoded in `risk_rules.py` and currently happen to match the JSON values, with no mechanism keeping them in sync.
- **Preferred future action:** Add a short note (e.g., in `docs/architecture.md`) stating these files are reference/aspirational data not currently wired into rule logic. Wiring them in as a single source of truth is a separate, lower-priority option only worth pursuing if thresholds need to become configurable.
- **Priority:** Medium
- **Effort:** Low (documentation note) / Medium (if wiring is later chosen)
- **Files involved:** `data/clickup_demo/policies.json`, `src/core/risk_rules.py`, `docs/architecture.md`
- **Implementation condition:** Only after explicit human approval; default preference is the documentation-only option unless the owner requests wiring.

### 4. Rotate or remove the local ClickUp token before the repository is copied, exported, zipped, or shared

- **Current issue:** The local `.env` file contains what appears to be a real ClickUp personal API token. It is correctly excluded by `.gitignore` and `.dockerignore` and was confirmed never committed to git history, but it still exists in plaintext on disk.
- **Preferred future action:** Rotate or blank the token in `.env` before the project folder is ever copied, zipped, or shared outside this machine. Reconfirm no packaging or export step includes `.env`.
- **Priority:** Medium
- **Effort:** Low
- **Files involved:** `.env` (untracked, local only)
- **Implementation condition:** This is an operational action for the project owner, not a code change — no AI implementation plan is needed, only owner action.

---

## Explicitly Rejected Scope Expansion

The following are **not to be added** at the current project stage:

- Kubernetes
- Microservices
- Additional databases or queues
- Enterprise IAM
- Large monitoring or observability stacks
- LLM-based risk analysis
- Autonomous write-back
- Automatic decision execution
- Additional agents
- Production integrations
- Unnecessary cloud infrastructure

---

## Reopening Conditions

The project should only be reopened for further work if one of the following occurs:

- A documentation contradiction affects portfolio credibility.
- A security issue is discovered.
- A core business rule is incorrect.
- The project scope changes due to a real business requirement.
- A selected improvement is explicitly approved by the project owner.

---

## Human Approval Rule

- No item in this file may be implemented automatically.
- Claude or any other AI coding tool must first prepare a proposed implementation plan before touching any file.
- The plan must identify exact files, expected changes, risks, and tests.
- Implementation may begin only after explicit human approval of that plan.
- After each approved step, the AI must stop, report the result, and wait for approval before proceeding to the next step.
