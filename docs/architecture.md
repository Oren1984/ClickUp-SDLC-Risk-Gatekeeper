# Architecture — ClickUp SDLC Risk Gatekeeper

**Oren Salami | Technology Project Management + AI Tools**

## System Design

The project follows a simple, flat architecture with minimal abstraction. There are no
unnecessary layers, no ORMs, no message queues, and no microservices. The goal is a
readable, demonstrable system.

```
app/streamlit_app.py
        │
        ├── src/core/clickup_adapter.py   ← data loading (mock only)
        │           │
        │           └── data/clickup_demo/tasks.json
        │
        ├── src/core/risk_reviewer.py     ← orchestrates all rules
        │           │
        │           └── src/core/risk_rules.py  ← 10 rule functions
        │
        ├── src/core/compliance_checks.py ← GDPR/PCI/HIPAA/SOX
        │
        └── src/core/report_generator.py  ← summary + task reports
```

## Component Responsibilities

### `clickup_adapter.py`
- Loads tasks, policies, DoD, and guidelines from local JSON files
- Provides `load_tasks()`, `get_task_by_id()`, and data access functions
- Contains stub functions with TODO comments for future ClickUp API integration
- Mock-first: no network calls, no credentials required
- The separate `src/integrations/clickup_api_client.py` implements real read-only
  ClickUp API calls (Phase 1), but is not called by this adapter or by
  `app/streamlit_app.py` — see `docs/future_clickup_integration.md`

### `risk_rules.py`
- Contains keyword lists (SECURITY_KEYWORDS, AI_KEYWORDS, ARCHITECTURE_KEYWORDS, etc.)
- Contains one function per rule, each returning a `RuleFinding` or `None`
- Rules are stateless, pure functions — easy to test and extend
- Uses word-boundary regex matching to avoid false positives on substrings

### `risk_reviewer.py`
- `RiskReviewer.review(task)` applies all rules and returns `RiskReviewResult`
- Score = sum of triggered rule weights, capped at 100
- Level thresholds: Low (0–25), Medium (26–50), High (51–75), Critical (76–100)
- Gate decision logic: prioritizes Blocked > Security > Architecture > QA > Clarification > Approved

### `compliance_checks.py`
- Framework profiles define keyword triggers and required evidence keywords
- `check_compliance(task)` returns a list of `ComplianceResult` objects
- Supports: GDPR, PCI-DSS, HIPAA, SOX, General Security
- Independently callable from the reviewer for the compliance tab

### `report_generator.py`
- `generate_task_report()` flattens a task + review result into a display dict
- `generate_summary_report()` aggregates across all task reports
- Used by the Streamlit app for summary metrics

### `streamlit_app.py`
- Single-file Streamlit dashboard
- Loads and reviews all tasks at startup (cached with `@st.cache_data`)
- Four tabs: Dashboard, Task Detail, Compliance View, About
- Sidebar filters: Sprint, Status, Risk Level, Gate Decision

## Data Flow

```
JSON file → load_tasks() → [task dict] → RiskReviewer.review()
                                             ↓
                                     RiskReviewResult
                                             ↓
                                  generate_task_report()
                                             ↓
                                   Streamlit display
```

## Reference Data Files

`data/clickup_demo/policies.json`, `definition_of_done.json`, and
`architecture_guidelines.json` are loaded by `clickup_adapter.py`
(`load_policies()`, `load_definition_of_done()`, `load_architecture_guidelines()`)
and covered by tests, but they are reference/demonstration data only. The active
risk thresholds and gate logic live in `risk_rules.py` and `risk_reviewer.py` as
Python constants — the values in `policies.json` currently match them by
convention, but nothing synchronizes the two. Changing `policies.json` has no
effect on the running risk engine.

## Design Decisions

**Why deterministic rules instead of an LLM?**
Deterministic rules are transparent, fast, testable, and run offline. The focus
of this demo is the workflow and SDLC gate logic, not LLM inference. An LLM layer
could be added on top for free-text analysis, but the rule engine provides the
predictable baseline.

**Why flat JSON data?**
The demo data needs to be readable, editable, and version-controlled. JSON is
sufficient for 20 tasks and eliminates any database dependency.

**Why a single `src/core/` module?**
The project is small enough that a flat core module is more readable than
over-engineered sub-packages.
