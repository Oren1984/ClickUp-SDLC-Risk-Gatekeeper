# Governance and Validation

## Human oversight

The gatekeeper supports decisions. It does not make them. Every score, level, and gate it shows is a **recommendation** for a person to review.

The intended review loop:

1. The engine reviews each task and shows findings and recommendations in the dashboard.
2. A reviewer reads them in context. Is the gap real, or handled somewhere the tool can't see? Is the severity right for this task?
3. The reviewer decides: approve, send back for clarification, route to QA, security, or architecture review, hold for a dependency, or escalate.
4. The task owner updates the task, and the check runs again.

The app has no feature for recording step 3. Decisions are captured wherever the team tracks its work.

| Role | Responsibility |
|---|---|
| Rule engine | Flags gaps, explains them, recommends a next step |
| Project / delivery lead | Owns the sprint-readiness decision; drives clarification |
| QA lead | Reviews QA-routed tasks; confirms test plans and DoD |
| Tech lead / architect | Reviews architecture-routed tasks |
| Security / compliance reviewer | Signs off on security, AI-readiness, and compliance findings |
| Task owner | Fills in the missing information |

## Authority boundaries

What the tool **does not** do, according to the current code:

- It does not change task status, block work, or approve work in any system
- It does not write to ClickUp. Write-back methods raise `NotImplementedError`
- It does not run on a trigger or in the background. Reviews happen when the dashboard loads
- It does not use an LLM or send task content to any AI service

If write-back is added in future, it should only happen after a human approves, as an informational note (a comment or label) the team can reverse, never as an automatic hard block.

Findings are explainable by design. Each comes from a named rule with a fixed weight in `src/core/risk_rules.py`, and the score is just their sum. When the needed information is missing, the tool treats that as a risk and does not assume the task is fine. A false alarm costs a short review; a missed gap can cost much more.

## Security and privacy

- **No secrets in the repository.** `.env.example` holds placeholders only. `.env` is excluded by `.gitignore` and `.dockerignore`.
- **Token handling.** The ClickUp token comes only from the environment (or a constructor argument). It is sent only as the `Authorization` header and never appears in `repr`, `str`, error messages, or script output. Tests check this.
- **Read-only access.** The client and the connection script use only `GET` requests.
- **Mock data by default.** All demo tasks are fictional, and nothing leaves the machine unless you run the optional client or script.
- **Container.** The Docker image runs as a non-root user.
- **Dashboard hardening.** None: no authentication, HTTPS, or rate limiting. Run it locally or on a trusted network only.
- **If adapted for real data:** treat task content as internal or confidential, keep compliance-related notes in-boundary, and send only the fields needed if any external AI service is ever added.

## Testing

The suite has 64 pytest tests. They run offline, with no token or network access.

| File | Tests | Covers |
|---|---|---|
| `tests/test_clickup_adapter.py` | 8 | Data loading, required fields, unique IDs, task lookup, reference files |
| `tests/test_risk_reviewer.py` | 22 | Level thresholds, each rule firing and passing, gate decisions, score cap, AI readiness dimensions |
| `tests/test_compliance_checks.py` | 8 | Framework detection, evidence found or missing, multiple frameworks, `has_compliance_gaps()` |
| `tests/test_integrations.py` | 26 | Mock client and `TaskClient` protocol; unconfigured API client returns `[]`/`None`; write methods raise `NotImplementedError`; token never leaks; simulated HTTP responses (mapping, multiple lists, 404, errors); `_map_task()` edge cases |

Run them from the repository root:

```bash
pytest          # all tests
pytest -v       # verbose
```

Last run during this documentation update: **64 passed**.

Not covered by automated tests:

- The Streamlit UI (checked by running the app)
- Live ClickUp API calls (use the connection script manually with your own token)
- The Docker build (it currently fails because `requirements.txt` is missing; see [DEMO_AND_OPERATIONS.md](DEMO_AND_OPERATIONS.md#docker-startup))

## Limitations

**Rules and scoring**

- Rules check keywords and field completeness. They don't understand meaning, so well-formed but wrong acceptance criteria pass.
- Real risks can be missed when the wording avoids the keywords. For example, "file upload" or "payments" do not trigger the security rule.
- False alarms are possible when a keyword appears by coincidence.
- A Low score is approved even if a light rule fired. The finding is still shown.
- RULE-010 depends on today's date. Every demo due date is now past, so every demo task gets +20.
- Rules read task fields only, not code, attachments, or links.

**Compliance**

- Detection and evidence are both keyword-based. Finding the word "DPA" does not mean a DPA exists.
- Compliance checks use substring matching and their own keyword lists, so they can disagree with the rule engine (see TASK-010).
- This is not a substitute for legal, security, or compliance review, especially in regulated industries.

**Data and integration**

- All task data is mock JSON with no sync. The dashboard never uses live data.
- The reference JSON files (policies, DoD, architecture guidelines) do not drive the engine.
- The read-only client has no pagination, rate limiting, or retries, and its field mapping is not validated against live data. It also can't parse ClickUp's timestamp due dates.

**Application**

- Single-user, with no authentication, no persistent storage, and no way to record decisions.
- Results are cached per session and recomputed when the app restarts.

## Future improvements

These are ideas based on gaps in the current code, not commitments. Each would need explicit approval before any work starts.

| Idea | Why |
|---|---|
| Add `requirements.txt` back | Restores `pip install -r` and the Docker build |
| Make demo due dates relative, or allow a fixed review date | Keeps RULE-010 results stable over time |
| Validate the ClickUp field mapping against a real workspace, including due-date and dropdown conversion | Required before any live use |
| Add pagination and basic rate-limit handling to the read-only client | Lists with more than one page of tasks |
| Optional dashboard switch to the read-only client, with mock data as the default | Demonstrate live review without changing the default |
| Record reviewer decisions in the dashboard | Close the human-review loop inside the tool |
| Human-approved write-back (comment or label only) | The adapter's TODO list; must stay reversible and approval-gated |
| Align the compliance and rule keyword lists | Fewer cases where the two views disagree |
