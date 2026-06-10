# Workflow: How the Risk Gate Fits the SDLC

## SDLC Integration Point

```
Product Backlog
      │
Sprint Planning
      │
      ▼
┌─────────────────────────────────┐
│   SDLC Risk & Compliance Gate   │  ← This project
│                                 │
│  1. Load task from ClickUp      │
│  2. Run 10 risk rules           │
│  3. Check compliance frameworks │
│  4. Produce risk score + level  │
│  5. Issue gate decision         │
│  6. Return findings + recs      │
└─────────────────────────────────┘
      │                  │
      ▼                  ▼
Approved for         Blocked / Needs Review
Development               │
      │               PM/Lead reviews
      ▼               resolves gaps
  Development          re-submits
      │
  Code Review
      │
  QA / Testing
      │
  Staging Deploy
      │
  Production
```

## Gate Decision Flow

```
Run all rules
      │
      ├── Any rule triggers "blocked" status?  → Gate: Blocked
      │
      ├── Risk Level = Critical?
      │     ├── Compliance gap (RULE-009)?      → Gate: Requires Security Review
      │     ├── AI guardrails missing (RULE-005)?→ Gate: Requires Security Review
      │     └── Arch gap (RULE-006)?            → Gate: Requires Architecture Review
      │
      ├── Risk Level = High?
      │     ├── Security gap (RULE-004)?        → Gate: Requires Security Review
      │     ├── Arch gap (RULE-006)?            → Gate: Requires Architecture Review
      │     ├── QA gap (RULE-002)?              → Gate: Requires QA Review
      │     └── Other?                          → Gate: Needs Clarification
      │
      ├── Risk Level = Medium?
      │     ├── QA gap (RULE-002)?              → Gate: Requires QA Review
      │     └── Other?                          → Gate: Needs Clarification
      │
      └── Risk Level = Low?                     → Gate: Approved for Development
```

## Agile/Scrum Fit

| Ceremony | How this tool fits |
|----------|-------------------|
| Backlog Refinement | Review tasks before they are sprint-ready. Flag gaps early. |
| Sprint Planning | Gate check before committing a task to a sprint. |
| Daily Standup | Blocked tasks surfaced clearly with root cause. |
| Sprint Review | Risk reports available as part of sprint summary. |
| Retrospective | Recurring risk patterns identified across sprints. |

## Example: Task Lifecycle With the Gate

1. PM creates "Implement payment processing" task in ClickUp
2. Task is assigned to Sprint 4 during planning
3. Risk Gate runs automatically and detects:
   - Missing acceptance criteria (RULE-001)
   - No QA notes (RULE-002)
   - PCI compliance task with no evidence (RULE-009)
   - Security task with no security notes (RULE-004)
4. Gate decision: **Requires Security Review** (score: 95/100 — Critical)
5. PM and lead review findings and recommendations
6. PM updates task with acceptance criteria, QA plan, and compliance evidence
7. Gate re-runs: score drops to 10/100 — **Approved for Development**
8. Task enters development sprint

## Risk Resolution Loop

```
Task flagged → Review findings → Update task → Re-run gate → Gate clears → Develop
```
