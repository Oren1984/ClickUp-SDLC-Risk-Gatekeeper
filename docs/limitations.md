# Limitations

## Scope Limitations

**This is a demo, not a production system.** The following limitations are intentional
design choices for a focused portfolio demonstration.

---

## Data

- All 20 tasks are mock data. No real ClickUp workspace is connected.
- Task data is static JSON — no real-time sync or incremental update.
- The risk rules run on each page load (cached by Streamlit for the session).

## Risk Engine

- Rules are deterministic and keyword-based. They do not understand natural language beyond pattern matching.
- A task can pass all rules and still have real quality gaps that require human review.
- A task can trigger rules and still be well-understood by the team — the gate is a signal, not a final verdict.
- False positives are possible for edge-case text that contains rule keywords coincidentally.
- The word-boundary regex matching reduces but does not eliminate false positives.

## Compliance Checks

- Compliance detection is based on keyword presence in task text fields.
- Evidence detection is based on keyword presence in notes fields — it does not validate that the evidence is complete or correct.
- The system does not parse attached documents or external links.
- This is not a substitute for a proper legal or compliance review.

## Integration

- The demo integration adapter (currently ClickUp-style) is not connected to a live API.
- There is no webhook, automation trigger, or real-time event integration.
- There is no write-back to any project-management tool (no comment posting, label setting, or status update).
- See `docs/future_clickup_integration.md` for the ClickUp integration path.
- The adapter architecture supports future extension to Jira, Monday, Linear, Azure DevOps, Notion, and others.

## Infrastructure

- Single-user Streamlit app — no multi-user sessions or auth.
- No persistent storage — reviews are re-computed on each session load.
- No production deployment hardening (no HTTPS, no auth, no rate limiting on the app itself).

## AI / LLM

- No LLM is used in this project. The risk engine is purely rule-based.
- The AI task readiness check (RULE-005) looks for keyword evidence of six readiness dimensions (evaluation criteria, groundedness/source quality, cost awareness, fallback readiness, tool/data permission sensitivity, guardrails). It only checks that at least one dimension is mentioned in the task notes — it does not verify the documented plan is actually correct or complete, and it does not enforce anything at runtime (no token limits, no permission checks, no automatic failover).
- Adding an LLM layer for free-text analysis would improve detection quality but is outside the scope of this demo.

---

## What This Project Is Good For

- Demonstrating understanding of SDLC, Agile, and risk management concepts
- Portfolio presentation for engineering, QA, security, DevOps, and PM roles
- Exploring how a risk gate fits into a sprint workflow
- Starting point for a real integration with ClickUp, Jira, Monday, Linear, or other task-management tools
- Educational demonstration of compliance framework awareness
