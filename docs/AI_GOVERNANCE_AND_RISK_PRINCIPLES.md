# AI Governance & Risk Principles

**ClickUp SDLC Risk Gatekeeper**

---

## Purpose

This document defines the AI governance framework for the ClickUp SDLC Risk Gatekeeper. It establishes how the system generates risk recommendations, what decisions remain with humans, what the system's limitations are, and how it should be used responsibly in software delivery environments.

This framework applies whether the system is used as a portfolio demo or adapted for real SDLC workflows.

---

## Human-in-the-Loop Principle

**The SDLC Risk Gatekeeper is a decision-support tool, not a decision-making authority.**

Every risk recommendation the system produces is an input to a human review process — not an automatic outcome. A task marked "Requires Security Review" does not block the task automatically. A human reviewer must read the findings, evaluate the context, and make a final call.

This is not a technical limitation of the current demo. It is the intended and correct design for AI-assisted governance in software delivery. Fully automated SDLC gates create false confidence and remove human accountability from decisions that carry real consequences.

---

## AI Recommendations Are Advisory, Not Final

The system produces:
- A risk score (0–100)
- A risk level (Low / Medium / High / Critical)
- A gate decision recommendation
- A list of specific findings
- Practical recommendations for each finding

All of these are **suggestions for the human reviewer to evaluate**, not mandatory outcomes. The PM, QA lead, or Tech Lead:
- May agree with the recommendation and act on it
- May override it with documented justification
- May add context the system cannot see (verbal agreements, out-of-band reviews, known exceptions)

The system cannot account for everything. Human judgment remains the final authority.

---

## Risk Scoring Is Explainable

Every risk score is the direct sum of triggered rule weights. No black-box model is involved. When the system assigns a Critical risk level, it states exactly which rules triggered, with what weight, and why.

This explainability is intentional. In SDLC governance, a reviewer who does not understand why a task was flagged cannot make an informed decision about whether to accept or resolve the risk.

The system does not produce probabilistic outputs or confidence scores. Each rule fires deterministically on the task data. This makes the system auditable and predictable.

---

## The System Should Flag Uncertainty

When the data required to evaluate a rule is absent, the system treats that absence as a risk signal. A task with no security notes is flagged as potentially missing a required review — not assumed to be compliant.

This conservative default is intentional. The cost of a false positive (reviewing a task that was actually fine) is low. The cost of a false negative (missing a real security or compliance gap) can be high.

Reviewers who know that a flag is not applicable for a specific task should document that decision in the task itself, not disable the rule.

---

## No Automatic Approval or Rejection of Tasks

The system does not write back to ClickUp, block tasks in the project management tool, or change any task status without a human action. In the current demo, all output is read-only.

When real ClickUp API integration is added in the future, any write-back actions (posting a comment, applying a risk label, updating a status) must be:
1. Triggered only after a human reviews the AI output
2. Applied as informational annotations, not hard blocks
3. Reversible by the task owner or PM

The system is not permitted to autonomously move tasks to a "blocked" state or prevent development from starting. Gate enforcement remains with the team, not the tool.

---

## PM / QA / Tech Lead Remains Responsible

Using the SDLC Risk Gatekeeper does not transfer responsibility for delivery quality from the project team to the AI system. The PM, QA lead, and Tech Lead remain accountable for:
- Sprint readiness decisions
- Security review sign-off
- Architecture change approvals
- Compliance evidence validation
- Definition of Done confirmation

The tool surfaces gaps and generates recommendations. The team owns the outcomes.

---

## Data Privacy Assumptions

In demo mode, all data is local mock JSON. No real task data, personal information, business logic, or credentials are processed.

If this system is adapted for real use:
- Task data processed by the risk engine should be treated as internal/confidential
- No task content should be sent to external AI APIs or third-party services without explicit consent
- If LLM-based analysis is added in the future, data minimisation principles apply — only the fields required for risk analysis should be included in any external call
- Compliance task data (GDPR references, PII annotations, PCI evidence notes) is particularly sensitive and must remain in-boundary

---

## Limitations of AI Review

The current system uses deterministic rule-based analysis, not large language model inference. Its limitations include:

**What the system cannot detect:**
- Incorrect acceptance criteria that look well-formed but are logically wrong
- Security vulnerabilities in the code itself (it reviews task metadata, not code)
- Organizational context, stakeholder agreements, or verbal approvals
- Intent — it can only evaluate what is written in the task fields

**What the system can detect:**
- Missing or insufficient task data
- High-risk patterns based on tags, title keywords, and field completeness
- Compliance framework gaps based on task annotations
- Known risk combinations (e.g., security + missing DoD + no QA notes)

Reviewers should treat the system as a **checklist assistant** that catches common gaps, not as a comprehensive security or compliance audit.

---

## Responsible Use in SDLC Environments

This system is appropriate for:
- Pre-sprint readiness gates to catch obvious gaps before development
- Risk visibility dashboards for PMs and Tech Leads
- QA and compliance checklists embedded in task review workflows
- Portfolio demonstrations of AI-assisted governance thinking

This system is **not** appropriate as the sole compliance mechanism for regulated industries (healthcare, finance, government). It is a supporting tool. Formal compliance review processes, qualified reviewers, and documented sign-off chains remain mandatory in regulated environments.

---

## Why This Matters for Project Management and Software Delivery

The gap between "task created" and "task ready for development" is one of the most common sources of rework, sprint failure, and production incidents in software teams.

AI-assisted SDLC governance addresses this by:
- Making the review process systematic and repeatable
- Surfacing gaps that are easy to overlook under sprint pressure
- Creating a shared language for risk between PMs, QA, security, and engineering
- Reducing the cognitive load on reviewers without removing their judgment

Done well, this kind of tooling makes human reviewers faster and more consistent — without replacing them.
