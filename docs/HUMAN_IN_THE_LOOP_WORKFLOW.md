# Human-in-the-Loop Workflow

**ClickUp SDLC Risk Gatekeeper**

---

## Overview

This document describes the practical Human-in-the-Loop (HITL) review workflow used by the ClickUp SDLC Risk Gatekeeper. The AI system generates a structured risk assessment for each task. A human reviewer — PM, QA lead, or Tech Lead — evaluates that assessment and makes the final gate decision.

The AI does not make binding decisions. The human does.

---

## Review Workflow

### Step 1 — Task or Story Enters Review

A task or user story is submitted for SDLC risk review. This can happen:
- During backlog refinement (proactive gate before sprint planning)
- At sprint planning (final check before sprint commitment)
- On-demand (when a task is escalated or flagged as high-priority)

In demo mode, all 20 tasks are reviewed at startup. In a live integration, this would be triggered by a webhook when a task moves to "Ready for Review" status in ClickUp.

---

### Step 2 — AI Checks for Gaps and Risks

The risk engine evaluates each task against 10 SDLC rules:

| Check | What the AI looks for |
|---|---|
| Acceptance criteria quality | Is it present? Is it specific enough? |
| QA notes and test plan | Is a test approach defined? |
| Definition of Done | Is the DoD confirmed as complete? |
| Security sensitivity | If security-tagged, are security notes present? |
| AI/LLM task readiness | If AI-tagged, is at least one readiness signal documented — evaluation criteria, groundedness/source quality, AI/API cost awareness, fallback/degraded-mode behavior, tool/data permission sensitivity, or guardrails? |
| Architecture impact | If architecture-tagged, are design review notes present? |
| Scope clarity | Is a critical task sufficiently defined? |
| Dependency blockers | Is the task blocked by an unresolved dependency? |
| Compliance evidence | If compliance-tagged, is evidence documented? |
| Timeline risk | Is the due date overdue or at immediate risk? |

Each triggered rule adds to the risk score and contributes a specific finding and recommendation.

---

### Step 3 — AI Generates Risk Summary and Recommended Actions

The system outputs:
- **Risk score** (0–100) — weighted sum of triggered rules
- **Risk level** — Low (0–25), Medium (26–50), High (51–75), Critical (76–100)
- **Gate decision** — one of six recommended outcomes (see below)
- **Findings** — one line per rule triggered, explaining the gap
- **Recommendations** — one actionable next step per finding

This output is visible in the Streamlit dashboard under the Task Risk Dashboard and Task Detail tabs.

---

### Step 4 — Human Reviewer Evaluates the Recommendation

The PM, QA lead, or Tech Lead reviews the AI output in context. They consider:
- Does this finding reflect a real gap, or is there out-of-band information that addresses it?
- Is the severity appropriate for this specific task?
- Does the team have the capacity to resolve the gaps before sprint start?
- Are there dependencies or organisational constraints the system cannot see?

The reviewer is not required to accept the AI recommendation. They may agree, override, or escalate based on their judgment.

---

### Step 5 — Human Makes the Final Gate Decision

The reviewer selects one of the six gate outcomes:

| Outcome | Meaning | What happens next |
|---|---|---|
| ✅ Ready for Development | Task passes all checks — the reviewer is satisfied | Task enters the sprint |
| 💬 Needs Clarification | Minor gaps must be resolved | PM updates the task and re-submits |
| 🧪 QA Risk Detected | QA notes or DoD gaps require QA lead review | QA lead reviews and updates the task |
| 🔒 Security / Compliance Concern | Security, AI safety, or compliance gap detected | Security team or compliance reviewer signs off |
| 🚫 Blocked by Dependency | An unresolved dependency prevents progress | Dependency is resolved first; task re-enters review |
| 📢 Escalate to Tech Lead / PM | Risk is too complex or uncertain for the current reviewer | Escalated for senior review before decision |

---

### Step 6 — Resolution and Re-entry

After the human decision:
- If resolved: the task enters development or the sprint backlog
- If gaps remain: the task owner updates the required fields and the review runs again
- If escalated: the senior reviewer makes the final call and documents the decision

In a live ClickUp integration, the reviewer's decision can be annotated back to the task as a comment. The AI system never writes to ClickUp autonomously.

---

## Example Review Outcomes

### Outcome: Ready for Development

**Task:** "Fix broken pagination on order history page"
**AI findings:** None — acceptance criteria are clear, DoD is confirmed, QA notes are present
**AI recommendation:** Approved for Development
**Human decision:** Approved — task enters sprint

---

### Outcome: Needs Clarification

**Task:** "Update search feature"
**AI findings:** Acceptance criteria are vague (less than 30 characters); DoD not confirmed
**AI recommendation:** Needs Clarification
**Human decision:** PM adds acceptance criteria and confirms DoD; task re-submits and clears

---

### Outcome: QA Risk Detected

**Task:** "Add admin user role"
**AI findings:** No QA notes defined; no test plan for RBAC permission logic
**AI recommendation:** Requires QA Review
**Human decision:** QA lead adds test cases for role assignment, permission boundaries, and edge cases; task re-submits and clears

---

### Outcome: Security / Compliance Concern

**Task:** "Integrate Stripe payment flow"
**AI findings:** PCI-DSS compliance task with no evidence; no security notes; no QA plan
**AI recommendation:** Requires Security Review
**Human decision:** Security lead adds threat model notes and PCI evidence reference; QA adds test plan; task re-submits

---

### Outcome: Blocked by Dependency

**Task:** "Refactor GraphQL API to use new schema"
**AI findings:** Task status is 'blocked'; depends on TASK-003 (schema migration) which is not complete
**AI recommendation:** Blocked
**Human decision:** Task is removed from sprint until TASK-003 is resolved; PM updates sprint plan

---

### Outcome: Escalate to Tech Lead / PM

**Task:** "Migrate production database to PostgreSQL 16"
**AI findings:** No architecture notes; no QA plan; critical priority with vague scope; architecture-impacting change
**AI recommendation:** Requires Architecture Review (Critical — 75/100)
**Human decision:** PM escalates to Tech Lead; Tech Lead adds architecture review notes and rollback plan; task re-submits

---

## Who Owns What

| Role | Responsibility in HITL Workflow |
|---|---|
| AI System | Generates risk assessment, findings, and recommended actions |
| PM | Reviews findings, drives clarification, owns sprint readiness decision |
| QA Lead | Validates QA readiness, reviews QA-flagged tasks, confirms test plan |
| Tech Lead / Architect | Reviews architecture-flagged tasks, confirms design decisions |
| Security / Compliance | Signs off on security, AI safety, and compliance-flagged tasks |
| Task Owner / Developer | Updates task fields to resolve findings after review |

The AI system has no role in final decisions. It is a reviewer's assistant.
